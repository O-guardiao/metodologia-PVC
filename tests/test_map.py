"""Executable contracts for the textual map and its local transaction workflow."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import pvc_catalog as cat
import pvc_map_workflow as flow


def catalog():
    return {'schema_version': 1, 'catalogs': [
        {'id': 'core', 'title': 'Core', 'purpose': 'Business rules', 'parent': None}],
        'symbols': [{'id': 'rule', 'name': 'rule', 'path': 'src/rule.py',
                     'kind': 'function', 'catalog': 'core', 'purpose': 'Return a value',
                     'confidence': 'declared', 'inputs': [], 'outputs': ['integer'],
                     'invariants': ['No external effects'], 'depends_on': [],
                     'aliases': ['botão comprar'], 'tests': ['checks.py'],
                     'unknown_dependencies': ['Dynamic callers not analyzed']}]}


class MapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'src').mkdir()
        (self.root / 'src/rule.py').write_text('VALUE = 1\n')
        (self.root / 'checks.py').write_text(
            "from pathlib import Path\nassert 'VALUE = 2' in Path('src/rule.py').read_text()\n")
        self.git('init', '-q')
        self.git('config', 'user.name', 'PVC Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('add', '.')
        self.git('commit', '-qm', 'source baseline')
        self.wf = flow.Workflow(self.root)
        self.catalog = catalog()

    def git(self, *args):
        return cat.git(self.root, *args)

    def init(self, commit=True):
        self.wf.init(self.catalog)
        if commit:
            self.git('add', '.pvc-map')
            self.git('commit', '-qm', 'map baseline')
        self.wf.entry()

    def spec(self, tests=None):
        return {'intent': 'Change rule value', 'next_step': 'Verify scoped behavior',
                'scope': ['src/rule.py'], 'affected': ['rule'],
                'preserve': ['No external effects'],
                'tests': tests or [[sys.executable, 'checks.py']]}

    def checkpoint(self, tests=None):
        self.init()
        self.wf.plan(self.spec(tests))
        self.wf.checkpoint()

    def candidate(self, value=2):
        (self.root / 'src/rule.py').write_text(f'VALUE = {value}\n')
        return self.wf.candidate(self.catalog)

    def reviewed(self):
        self.checkpoint()
        self.candidate()
        self.assertTrue(self.wf.test(True)['passed'])
        self.wf.review('reviewer', 'Checked behavior and scoped diff')

    def pointer(self):
        return (self.wf.control / 'CURRENT').read_bytes()

    def test_promoted_status_does_not_repeat_plan_next_step(self):
        self.reviewed()
        promoted = self.wf.promote()
        state = self.wf.bounded_status()['change']
        self.assertEqual(state['plan_next_step'], self.spec()['next_step'])
        self.assertIn('do not repeat implementation', state['next_step'])
        self.assertEqual(state['commit'], promoted['commit'])

    def test_explicit_relocation_preserves_identity_and_requires_exact_copy(self):
        self.init()
        with tempfile.TemporaryDirectory() as parent:
            clone = Path(parent) / 'copy'
            subprocess.run(['git', 'clone', '-q', str(self.root), str(clone)], check=True)
            moved = flow.Workflow(clone)
            with self.assertRaises(cat.CatalogError):
                moved.baseline()
            with self.assertRaises(cat.CatalogError):
                moved.relocate('wrong')
            before = (clone / '.pvc-map/CURRENT').read_bytes()
            result = moved.relocate(cat.git(clone, 'rev-parse', 'HEAD'))
            self.assertFalse(result['evidence_renewed'])
            self.assertEqual(before, (clone / '.pvc-map/CURRENT').read_bytes())
            self.assertEqual(moved.baseline()[1]['project_id'], self.wf.baseline()[1]['project_id'])
            self.assertTrue(moved.entry()['fresh'])
            self.assertEqual(cat.git(clone, 'status', '--porcelain'), '')
            (clone / 'src/rule.py').write_text('CHANGED = True')
            with self.assertRaises(cat.CatalogError):
                moved.relocate(cat.git(clone, 'rev-parse', 'HEAD'))

    def test_relocation_refuses_pending_change(self):
        self.init()
        self.wf.plan(self.spec())
        with self.assertRaises(cat.CatalogError):
            self.wf.relocate(self.git('rev-parse', 'HEAD'))

    def test_interrupted_retest_revokes_review_before_command(self):
        self.reviewed()
        original = flow.subprocess.run
        def interrupted(argv, *args, **kwargs):
            if 'checks.py' in argv:
                raise KeyboardInterrupt()
            return original(argv, *args, **kwargs)
        with patch.object(flow.subprocess, 'run', side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt):
                self.wf.test(True)
        change = self.wf.load_change()
        self.assertEqual(change['phase'], 'candidate')
        self.assertNotIn('review', change)
        self.assertNotIn('test_run', change)
        self.assertIn('uncertain', change['execution_status'])
        with self.assertRaises(cat.CatalogError):
            self.wf.promote()
        with self.assertRaises(cat.CatalogError):
            self.wf.test(True)
        self.assertTrue(self.wf.test(True, reconciled_effects='Fixture command never ran; checked source unchanged')['passed'])
        self.wf.review('reviewer', 'Retest inspected and rerun')
        self.assertEqual(self.wf.promote()['phase'], 'promoted')

    def test_root_diagram_derives_cross_catalog_dependencies(self):
        data = catalog()
        data['catalogs'].append({'id': 'ui', 'title': 'UI', 'purpose': 'Consumer', 'parent': 'core'})
        consumer = copy.deepcopy(data['symbols'][0])
        consumer.update(id='consumer', name='consume', catalog='ui', depends_on=['rule'])
        data['symbols'].append(consumer)
        cat.validate_catalog(data, cat.inventory(self.root))
        root = cat.render(data, cat.inventory(self.root))['INDEX.md']
        self.assertIn('g_ui -.->|depende: declarado| g_core', root)

    def test_init_is_fresh_and_never_overwrites(self):
        self.init()
        self.assertTrue(self.wf.bounded_status()['fresh'])
        self.assertEqual(self.wf.bounded_status()['unmapped_files']['items'], ['checks.py'])
        before = self.pointer()
        with self.assertRaises(cat.CatalogError):
            self.wf.init(self.catalog)
        self.assertEqual(before, self.pointer())

    def test_invalid_init_does_not_create_control(self):
        self.catalog['symbols'][0]['path'] = '../outside'
        with self.assertRaises(cat.CatalogError):
            self.wf.init(self.catalog)
        self.assertFalse(self.wf.control.exists())

    def test_entry_required_and_receipt_not_cognitive_guarantee(self):
        self.wf.init(self.catalog)
        with self.assertRaises(cat.CatalogError):
            self.wf.plan(self.spec())
        result = self.wf.entry()
        self.assertIn('does not prove', result['receipt'])
        self.wf.plan(self.spec())

    def test_checkpoint_requires_clean_committed_baseline(self):
        self.init(commit=False)
        self.wf.plan(self.spec())
        with self.assertRaises(cat.CatalogError):
            self.wf.checkpoint()
        self.git('add', '.pvc-map')
        self.git('commit', '-qm', 'map baseline')
        result = self.wf.checkpoint()
        self.assertEqual(result['restore_point'], self.git('rev-parse', 'HEAD'))

    def test_plan_stale_baseline_and_candidate_scope(self):
        self.init()
        (self.root / 'checks.py').write_text('print(1)\n')
        with self.assertRaises(cat.CatalogError):
            self.wf.plan(self.spec())
        self.assertFalse((self.wf.control / 'change.json').exists())
        self.assertFalse(self.wf.bounded_status()['fresh'])

    def test_out_of_scope_candidate_preserves_baseline_and_state(self):
        self.checkpoint()
        before = (self.wf.control / 'change.json').read_bytes()
        pointer = self.pointer()
        (self.root / 'checks.py').write_text('print(1)\n')
        with self.assertRaises(cat.CatalogError):
            self.wf.candidate(self.catalog)
        self.assertEqual(before, (self.wf.control / 'change.json').read_bytes())
        self.assertEqual(pointer, self.pointer())

    def test_failure_then_success_promotes_only_validated_candidate(self):
        self.checkpoint()
        original = self.pointer()
        self.candidate(3)
        with self.assertRaises(cat.CatalogError):
            self.wf.test()
        failed = self.wf.test(True)
        self.assertFalse(failed['passed'])
        self.assertEqual(original, self.pointer())
        with self.assertRaises(cat.CatalogError):
            self.wf.review('reviewer', 'Cannot approve failure')
        self.candidate(2)
        self.assertTrue(self.wf.test(True)['passed'])
        self.wf.review('reviewer', 'Inspected assertions and diff')
        result = self.wf.promote()
        self.assertEqual(result['phase'], 'promoted')
        self.assertFalse(result['operational_acceptance'])
        self.assertNotEqual(original, self.pointer())
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertEqual(self.git('show', 'HEAD:.pvc-map/CURRENT'), result['generation'])
        self.assertTrue(self.wf.bounded_status()['fresh'])
        with self.assertRaises(cat.CatalogError):
            self.wf.plan(self.spec())
        self.wf.entry()
        self.wf.plan(self.spec())

    def test_source_edit_invalidates_passed_tests(self):
        self.checkpoint()
        self.candidate()
        self.wf.test(True)
        (self.root / 'src/rule.py').write_text('VALUE = 99\n')
        with self.assertRaises(cat.CatalogError):
            self.wf.review('reviewer', 'Stale')

    def test_tampered_log_invalidates_test_evidence(self):
        self.checkpoint()
        self.candidate()
        result = self.wf.test(True)
        (self.wf.control / result['results'][0]['log']).write_text('forged')
        with self.assertRaises(cat.CatalogError):
            self.wf.review('reviewer', 'Invalid log')

    def test_malformed_json_and_state_rejected_before_mutation(self):
        self.checkpoint()
        path = self.wf.control / 'change.json'
        pointer = self.pointer()
        for payload in ('{broken', '[]', '{"schema_version": 1, "phase": "candidate"}'):
            with self.subTest(payload=payload):
                path.write_text(payload)
                with self.assertRaises(cat.CatalogError):
                    self.wf.candidate(self.catalog)
                self.assertEqual(path.read_text(), payload)
                self.assertEqual(pointer, self.pointer())

    def test_git_file_excluded_like_git_directory(self):
        self.assertNotIn('.git', cat.inventory(self.root))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / '.git').write_text('gitdir: /unavailable/worktree')
            (root / 'file.txt').write_text('text')
            self.assertEqual(set(cat.inventory(root)), {'file.txt'})

    def test_actual_git_worktree_supports_checkpoint(self):
        with tempfile.TemporaryDirectory() as folder:
            worktree = Path(folder) / 'tree'
            self.git('worktree', 'add', '--detach', str(worktree), 'HEAD')
            try:
                wf = flow.Workflow(worktree)
                self.assertTrue((worktree / '.git').is_file())
                wf.init(self.catalog)
                cat.git(worktree, 'add', '.pvc-map')
                cat.git(worktree, 'commit', '-qm', 'worktree baseline')
                wf.entry()
                wf.plan(self.spec())
                self.assertEqual(wf.checkpoint()['phase'], 'checkpoint')
            finally:
                self.git('worktree', 'remove', '--force', str(worktree))

    def test_symlink_file_and_directory_rejected(self):
        for directory in (False, True):
            with self.subTest(directory=directory):
                link = self.root / 'link'
                link.symlink_to(self.root / ('src' if directory else 'checks.py'), target_is_directory=directory)
                try:
                    with self.assertRaises(cat.CatalogError):
                        cat.inventory(self.root)
                finally:
                    link.unlink()

    def test_hierarchy_dependency_duplicate_and_reviewed_hash_validation(self):
        files = cat.inventory(self.root)
        mutations = [
            lambda c: c['catalogs'][0].update(parent='core'),
            lambda c: c['catalogs'][0].update(parent='missing'),
            lambda c: c['catalogs'][0].update(parent=[]),
            lambda c: c['symbols'][0].update(depends_on=['missing']),
            lambda c: c['symbols'].append(copy.deepcopy(c['symbols'][0])),
            lambda c: c['symbols'][0].update(confidence='reviewed'),
            lambda c: c['symbols'][0].update(aliases=['x', 'x']),
        ]
        for mutate in mutations:
            c = copy.deepcopy(self.catalog)
            mutate(c)
            with self.assertRaises(cat.CatalogError):
                cat.validate_catalog(c, files)
        self.catalog['symbols'][0].update(confidence='reviewed', reviewed_sha256=files['src/rule.py']['sha256'])
        cat.validate_catalog(self.catalog, files)

    def test_alias_query_paging_and_bounded_show(self):
        for n in range(4):
            s = copy.deepcopy(self.catalog['symbols'][0])
            s.update(id=f'caller{n}', depends_on=['rule'])
            self.catalog['symbols'].append(s)
        self.init()
        result = cat.query(self.catalog, 'BOTÃO comprar', limit=2)
        self.assertEqual(result['total'], 5)
        self.assertEqual(result['next_offset'], 2)
        self.assertEqual(len(cat.query(self.catalog, '', limit=2, offset=4)['items']), 1)
        self.assertEqual(self.wf.show('rule', limit=2)['consumers']['total'], 4)
        self.assertEqual(len(self.wf.show('rule', limit=2)['consumers']['items']), 2)
        for limit, offset in [(0, 0), (101, 0), (1, -1), (True, 0)]:
            with self.assertRaises(cat.CatalogError):
                cat.page([], limit, offset)

    def test_render_deterministic_from_reordered_records(self):
        for name in ('z', 'a'):
            self.catalog['catalogs'].append({'id': name, 'title': name, 'purpose': name, 'parent': 'core'})
        other = copy.deepcopy(self.catalog)
        other['catalogs'].reverse()
        files = cat.inventory(self.root)
        self.assertEqual(cat.render(self.catalog, files), cat.render(other, files))
        for text in cat.render(self.catalog, files).values():
            self.assertIn('```mermaid', text)
            self.assertTrue(all(line == line.rstrip() for line in text.splitlines()))

    def test_duplicate_arguments_preserved_and_not_shell_interpreted(self):
        argv = [sys.executable, '-c', 'import sys; assert sys.argv[1:] == ["same", "same", "; touch hacked"]', 'same', 'same', '; touch hacked']
        self.checkpoint([argv])
        self.candidate()
        self.assertTrue(self.wf.test(True)['passed'])
        self.assertFalse((self.root / 'hacked').exists())

    def test_test_mutation_requires_new_candidate(self):
        self.checkpoint([[sys.executable, '-c', "from pathlib import Path; Path('src/rule.py').write_text('changed')"]])
        self.candidate()
        result = self.wf.test(True)
        self.assertFalse(result['passed'])
        self.assertFalse(result['candidate_unchanged'])
        self.assertEqual(self.wf.load_change()['phase'], 'candidate')

    def test_interrupted_commit_requires_inspection_and_recover(self):
        self.reviewed()
        original_git = flow.git
        def fail_commit(root, *args):
            if args[0] == 'commit':
                raise cat.CatalogError('Simulated commit interruption')
            return original_git(root, *args)
        with patch.object(flow, 'git', side_effect=fail_commit):
            with self.assertRaises(cat.CatalogError):
                self.wf.promote()
        self.assertEqual(self.wf.bounded_status()['blocked'], 'promotion_incomplete')
        with self.assertRaises(cat.CatalogError):
            self.wf.recover()
        self.git('commit', '-qm', 'inspected intended staged recovery')
        self.assertEqual(self.wf.recover()['phase'], 'promoted')
        self.assertFalse((self.wf.control / 'journal.json').exists())
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_recovery_resumes_after_state_saved_before_journal_cleanup(self):
        self.reviewed()
        original_unlink = Path.unlink
        def interrupt_cleanup(path, *args, **kwargs):
            if path == self.wf.control / 'journal.json':
                raise OSError('Simulated interruption after promoted state persisted')
            return original_unlink(path, *args, **kwargs)
        with patch.object(Path, 'unlink', interrupt_cleanup):
            with self.assertRaises(OSError):
                self.wf.promote()
        self.assertEqual(self.wf.load_change()['phase'], 'promoted')
        self.assertEqual(self.wf.recover()['phase'], 'promoted')
        self.assertFalse((self.wf.control / 'journal.json').exists())

    def test_writer_lock_excludes_second_writer_and_releases_on_failure(self):
        self.init()
        with self.assertRaises(RuntimeError):
            with flow.locked(self.wf.control):
                with self.assertRaises(cat.CatalogError):
                    with flow.locked(self.wf.control):
                        self.fail('Second writer admitted')
                raise RuntimeError('first writer failed')
        self.assertFalse((self.wf.control / 'write.lock').exists())

    def test_dependency_change_exercises_real_consumer_and_catalog_edges(self):
        (self.root / 'src/rule.py').write_text('def rate():\n    return 2\n')
        (self.root / 'src/consumer.py').write_text(
            'from rule import rate\ndef total(quantity):\n    return quantity * rate()\n')
        (self.root / 'checks.py').write_text(
            "import sys\nsys.path.insert(0, 'src')\nfrom consumer import total\nassert total(4) == 12\n")
        self.catalog['symbols'][0].update(name='rate', purpose='Provide price per unit')
        consumer = copy.deepcopy(self.catalog['symbols'][0])
        consumer.update(id='total', name='total', path='src/consumer.py',
                        purpose='Compute total using rate', depends_on=['rule'],
                        inputs=['quantity'], outputs=['quantity multiplied by rate'], aliases=['cart total'])
        self.catalog['symbols'].append(consumer)
        self.git('add', '.')
        self.git('commit', '-qm', 'real dependency fixture')
        self.init()
        self.assertEqual(self.wf.show('rule')['consumers']['items'], ['total'])
        self.assertEqual(self.wf.show('total')['depends_on']['items'], ['rule'])
        before_consumer = (self.root / 'src/consumer.py').read_bytes()
        spec = self.spec()
        spec['affected'] = ['rule', 'total']
        self.wf.plan(spec)
        self.wf.checkpoint()
        (self.root / 'src/rule.py').write_text('def rate():\n    return 3\n')
        self.wf.candidate(self.catalog)
        self.assertTrue(self.wf.test(True)['passed'])
        self.wf.review('test reviewer', 'Real consumer assertion verifies changed supplier')
        result = self.wf.promote()
        self.assertEqual(result['phase'], 'promoted')
        self.assertEqual(before_consumer, (self.root / 'src/consumer.py').read_bytes())
        self.wf.entry()
        self.assertEqual(self.wf.show('rule')['consumers']['items'], ['total'])
        self.assertEqual(self.git('show', 'HEAD:src/rule.py'), 'def rate():\n    return 3')

    def test_invalid_nested_parent_is_rejected_before_hierarchy_walk(self):
        self.catalog['catalogs'][0]['parent'] = 'child'
        self.catalog['catalogs'].append({'id': 'child', 'title': 'Child',
                                         'purpose': 'Invalid ancestor', 'parent': []})
        with self.assertRaises(cat.CatalogError):
            self.wf.init(self.catalog)
        self.assertFalse(self.wf.control.exists())

    def test_control_character_path_rejected_before_initialization_mutates(self):
        bad = 'src/bad\nname.py'
        (self.root / bad).write_text('print(1)\n')
        self.catalog['symbols'][0]['path'] = bad
        with self.assertRaises(cat.CatalogError):
            self.wf.init(self.catalog)
        self.assertFalse(self.wf.control.exists())

    def test_cli_full_failed_then_successful_lifecycle(self):
        def cli(*args, expected=0):
            proc = subprocess.run([sys.executable, str(SCRIPTS / 'pvc_map.py'),
                                   '--project', str(self.root), *args], capture_output=True, text=True)
            self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr)
            return json.loads(proc.stdout if expected in (0, 2) else proc.stderr)
        with tempfile.TemporaryDirectory() as outside:
            cp, sp = Path(outside) / 'catalog.json', Path(outside) / 'plan.json'
            cp.write_text(json.dumps(self.catalog))
            sp.write_text(json.dumps(self.spec()))
            cli('init', '--catalog', str(cp))
            self.git('add', '.pvc-map')
            self.git('commit', '-qm', 'map baseline')
            cli('entry')
            cli('plan', '--spec', str(sp))
            cli('checkpoint')
            baseline = self.pointer()
            (self.root / 'src/rule.py').write_text('VALUE = 3\n')
            cli('candidate', '--catalog', str(cp))
            self.assertFalse(cli('test', '--run-reviewed-tests', expected=2)['passed'])
            self.assertEqual(baseline, self.pointer())
            cli('review', '--reviewer', 'test', '--note', 'Failing tests', expected=1)
            (self.root / 'src/rule.py').write_text('VALUE = 2\n')
            cli('candidate', '--catalog', str(cp))
            self.assertTrue(cli('test', '--run-reviewed-tests')['passed'])
            cli('review', '--reviewer', 'test', '--note', 'Inspected scoped correction')
            self.assertEqual(cli('promote')['phase'], 'promoted')
            self.assertTrue(cli('status')['fresh'])
            self.assertNotEqual(baseline, self.pointer())

    def test_rejects_tampered_generated_page(self):
        self.init()
        gen, _, _ = self.wf.baseline()
        (self.wf.control / 'generations' / gen / 'INDEX.md').write_text('forged map')
        with self.assertRaises(cat.CatalogError):
            self.wf.plan(self.spec())
        self.assertFalse((self.wf.control / 'change.json').exists())

    def test_prestaged_content_blocks_promotion(self):
        self.reviewed()
        self.git('add', 'src/rule.py')
        before = self.pointer()
        with self.assertRaises(cat.CatalogError):
            self.wf.promote()
        self.assertEqual(before, self.pointer())
        self.assertFalse((self.wf.control / 'journal.json').exists())

    def test_missing_executable_records_failure(self):
        self.checkpoint([[str(self.root / 'nonexistent-executable')]])
        self.candidate()
        result = self.wf.test(True)
        self.assertFalse(result['passed'])
        self.assertEqual(result['results'][0]['returncode'], 127)

    def test_timeout_records_failure(self):
        self.checkpoint([[sys.executable, '-c', 'import time; time.sleep(10)']])
        self.candidate()
        result = self.wf.test(True, timeout=0.02)
        self.assertFalse(result['passed'])
        self.assertEqual(result['results'][0]['returncode'], 124)

    def test_cli_entry_query_and_invalid_json_smoke(self):
        self.init()
        def cli(*args):
            return subprocess.run([sys.executable, str(SCRIPTS / 'pvc_map.py'), '--project', str(self.root), *args], capture_output=True, text=True)
        result = cli('entry', '--limit', '1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['fresh'])
        result = cli('query', 'comprar', '--limit', '1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['total'], 1)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as bad:
            bad.write('{invalid'); bad.flush()
            result = cli('plan', '--spec', bad.name)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stderr)['result'], 'not completed')
        self.assertFalse((self.wf.control / 'write.lock').exists())


if __name__ == '__main__':
    unittest.main()
