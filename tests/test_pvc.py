import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pvc', ROOT / 'scripts/pvc.py')
pvc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pvc)
FIXTURE = ROOT / 'tests/fixtures'


class ProjectTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / 'tests/.tmp'
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.root = Path(self.temp.name) / 'project'
        shutil.copytree(FIXTURE / 'project', self.root)
        (self.root / '.pvc').mkdir()
        self.state = json.loads((FIXTURE / 'state.json').read_text(encoding='utf-8'))
        self.persist()

    def tearDown(self):
        self.assertTrue(Path(self.temp.name).resolve().is_relative_to((ROOT / 'tests/.tmp').resolve()))
        self.temp.cleanup()

    def persist(self):
        (self.root / '.pvc/state.json').write_text(json.dumps(self.state), encoding='utf-8')

    def refresh(self):
        self.state = pvc.read_json(self.root / '.pvc/state.json')

    def record(self, module='save', kind='test', result='passed'):
        item = pvc.capture(self.root, module, 'evidence.txt', kind, result, 'local fixture', 'Fixture procedure, not operational proof', self.state['version'], pvc.fingerprints(self.root, self.state)[module])
        self.refresh()
        return item

    def decision(self, evidence, gate='G8'):
        self.state['decisions'].append({
            'id': 'D-001', 'module': 'save', 'gate': gate,
            'decision': 'GO', 'reason': 'Fixture reviewed',
            'reviewer': 'fixture auditor', 'version': self.state['version'],
            'fingerprint': pvc.fingerprints(self.root, self.state)['save'],
            'evidence_ids': [evidence['id']]
        })

    def cli(self, *args):
        proc = subprocess.run([sys.executable, str(ROOT / 'scripts/pvc.py'), *args, '--project', str(self.root)], capture_output=True, text=True, encoding='utf-8')
        return proc.returncode, json.loads(proc.stdout)

    def test_missing_state_is_clear_and_does_not_initialize(self):
        (self.root / '.pvc/state.json').unlink()
        code, output = self.cli('resume')
        self.assertEqual(code, 1)
        self.assertIn('ausente', output['error'])
        self.assertFalse((self.root / '.pvc/state.json').exists())

    def test_init_preserves_existing_state(self):
        before = (self.root / '.pvc/state.json').read_bytes()
        with self.assertRaisesRegex(pvc.Invalid, 'existente preservado'):
            pvc.initialize(self.root, 'new', '2')
        self.assertEqual(before, (self.root / '.pvc/state.json').read_bytes())

    def test_new_projects_have_distinct_identity_and_no_approval(self):
        (self.root / '.pvc/state.json').unlink()
        a = pvc.initialize(self.root, 'Full product vision', '1')
        other = Path(self.temp.name) / 'other'
        other.mkdir()
        b = pvc.initialize(other, 'Full product vision', '1')
        self.assertNotEqual(a['project_id'], b['project_id'])
        self.assertEqual(a['evidence'], [])
        self.assertEqual(a['decisions'], [])

    def test_resume_recovers_goal_next_step_and_uncertain_action(self):
        code, output = self.cli('resume')
        self.assertEqual(code, 0)
        self.assertEqual(output['goal'], self.state['goal'])
        self.assertEqual(output['active_change']['next_step'], self.state['active_change']['next_step'])
        self.assertEqual(output['pending_actions'][0]['status'], 'uncertain')
        self.assertIn('antes de repetir', output['instruction'])
        self.assertEqual(output['missing_evidence'], ['contract', 'save', 'independent'])
        self.assertNotIn('fingerprints', output)
        self.assertNotIn('def save', json.dumps(output))

    def test_actual_fixture_behavior_and_failure(self):
        module_spec = importlib.util.spec_from_file_location('fixture_save', self.root / 'save.py')
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        self.assertEqual(module.save('task'), {'title': 'task'})
        with self.assertRaises(ValueError):
            module.save('')

    def test_cli_snapshot_record_validate_roundtrip(self):
        code, baseline = self.cli('snapshot', '--module', 'save')
        self.assertEqual(code, 0)
        code, evidence = self.cli('record', '--module', 'save', '--artifact', 'evidence.txt',
                                  '--kind', 'test', '--result', 'passed', '--environment', 'fixture local',
                                  '--procedure', 'fixture check', '--observed-version', baseline['version'],
                                  '--expected-fingerprint', baseline['fingerprint'])
        self.assertEqual(code, 0)
        code, report = self.cli('validate')
        self.assertEqual(code, 0)
        self.assertEqual(report['evidence'][0]['id'], evidence['id'])
        self.assertEqual(report['evidence'][0]['status'], 'current')

    def test_cli_init_then_resume_with_unicode_goal(self):
        (self.root / '.pvc/state.json').unlink()
        code, created = self.cli('init', '--goal', 'Operação com persistência', '--version', '1')
        self.assertEqual(code, 0)
        code, resumed = self.cli('resume')
        self.assertEqual(code, 0)
        self.assertEqual(resumed['project_id'], created['project_id'])
        self.assertEqual(resumed['goal'], 'Operação com persistência')

    def test_resume_preserves_module_and_restrictions_for_two_gate_decisions(self):
        first = self.record(kind='operational')
        second = self.record('independent', kind='operational')
        self.decision(first)
        self.state['decisions'][0]['decision'] = 'GO_WITH_RESTRICTIONS'
        self.state['decisions'][0]['reason'] = 'Uso local; backup ainda pendente'
        other = copy.deepcopy(self.state['decisions'][0])
        other.update(id='D-002', module='independent', reason='Ajuda revisada', reviewer='second reviewer',
                     evidence_ids=[second['id']], fingerprint=pvc.fingerprints(self.root, self.state)['independent'])
        self.state['decisions'].append(other)
        self.persist()
        code, result = self.cli('resume')
        self.assertEqual(code, 1)  # Legacy GO has no critical E2E evidence.
        decisions = {d['module']: d for d in result['decisions']}
        self.assertEqual(decisions['save']['reason'], 'Uso local; backup ainda pendente')
        self.assertEqual(decisions['save']['evidence_ids'], [first['id']])
        self.assertEqual(decisions['independent']['reviewer'], 'second reviewer')

    def test_missing_superseded_artifact_keeps_degraded_checkpoint(self):
        old = self.record()
        (self.root / 'new-evidence.txt').write_text('New observed result', encoding='utf-8')
        pvc.capture(self.root, 'save', 'new-evidence.txt', 'test', 'passed', 'local', 'new verification',
                    self.state['version'], pvc.fingerprints(self.root, self.state)['save'])
        (self.root / 'evidence.txt').unlink()
        code, result = self.cli('resume')
        self.assertEqual(code, 1)
        self.assertEqual(result['goal'], self.state['goal'])
        self.assertEqual(result['next_step'], self.state['next_step'])
        self.assertEqual(result['pending_actions'][0]['status'], 'uncertain')
        self.assertIn(old['id'], result['history_warnings'][0])
        self.assertTrue(result['degraded'])
        self.assertEqual(result['operational_approval'], 'blocked_degraded_state')

    def test_missing_current_artifact_is_invalid_not_approved(self):
        item = self.record(kind='operational')
        self.decision(item)
        self.persist()
        (self.root / 'evidence.txt').unlink()
        code, result = self.cli('resume')
        self.assertEqual(code, 1)
        self.assertEqual(result['evidence'][0]['status'], 'invalid')
        self.assertEqual(result['decisions'][0]['status'], 'stale')
        self.assertEqual(result['next_step'], self.state['next_step'])

    def test_missing_input_produces_explicit_incomplete_resume(self):
        (self.root / 'save.py').unlink()
        code, result = self.cli('resume')
        self.assertEqual(code, 1)
        self.assertTrue(result['assessment_incomplete'])
        self.assertIsNone(result['global_index']['stale_evidence'])
        self.assertEqual(result['goal'], self.state['goal'])
        self.assertEqual(result['pending_actions'][0]['status'], 'uncertain')

    def test_large_project_paginates_without_hiding_global_alert_counts(self):
        for i in range(80):
            self.state['modules'][f'module-{i}'] = copy.deepcopy(self.state['modules']['independent'])
        self.state['blockers'] = [f'Critical blocker {i}' for i in range(90)]
        for i in range(30):
            action = copy.deepcopy(self.state['pending_actions'][0])
            action['id'] = f'action-{i}'
            self.state['pending_actions'].append(action)
        self.persist()
        code, result = self.cli('resume', '--limit', '5')
        self.assertEqual(code, 0)
        self.assertEqual(len(result['maturity']), 5)
        self.assertEqual(len(result['blockers']), 5)
        self.assertEqual(len(result['pending_actions']), 5)
        self.assertEqual(result['global_index']['modules'], 83)
        self.assertEqual(result['global_index']['blockers'], 90)
        self.assertEqual(result['global_index']['uncertain_actions'], 31)
        self.assertEqual(result['pagination']['blockers']['next_offset'], 5)
        code, page = self.cli('resume', '--limit', '5', '--offset', '5')
        self.assertEqual(page['blockers'][0], 'Critical blocker 5')

    def test_module_selection_preserves_global_staleness_signal(self):
        self.record('save')
        self.record('independent')
        (self.root / 'contract.md').write_text('changed', encoding='utf-8')
        code, result = self.cli('resume', '--module', 'independent')
        self.assertEqual(code, 2)
        self.assertEqual(list(result['maturity']), ['independent'])
        self.assertEqual(result['evidence'][0]['status'], 'current')
        self.assertEqual(result['global_index']['stale_evidence'], 1)

    def test_long_prose_is_excerpted_with_explicit_pointer(self):
        self.state['goal'] = 'A' * 8000
        self.persist()
        code, result = self.cli('resume')
        self.assertEqual(code, 0)
        self.assertLess(len(result['goal']), 500)
        self.assertIn({'pointer': '/goal', 'omitted_characters': 7600}, result['truncations'])

    def test_invalid_resume_limit_is_rejected(self):
        code, result = self.cli('resume', '--limit', '0')
        self.assertEqual(code, 1)
        self.assertIn('limit', result['error'])

    def test_contract_change_invalidates_transitive_consumers_selectively(self):
        self.record('contract')
        self.record('save')
        self.record('independent')
        self.state['modules']['consumer'] = copy.deepcopy(self.state['modules']['independent'])
        self.state['modules']['consumer']['depends_on'] = ['save']
        self.persist()
        self.record('consumer')
        (self.root / 'contract.md').write_text('R-001 changed contract', encoding='utf-8')
        report = pvc.inspect(self.root, self.state)
        statuses = {e['module']: e['status'] for e in report['evidence']}
        self.assertEqual(statuses, {'contract': 'stale', 'save': 'stale', 'independent': 'current', 'consumer': 'stale'})

    def test_configuration_change_invalidates_module(self):
        self.record()
        (self.root / 'config.json').write_text('{"schema":2}', encoding='utf-8')
        self.assertEqual(pvc.inspect(self.root, self.state)['evidence'][0]['status'], 'stale')

    def test_version_change_requires_revalidation(self):
        self.record()
        self.state['version'] = '2.0'
        report = pvc.inspect(self.root, self.state)
        self.assertIn('versao alterada', report['evidence'][0]['reasons'])

    def test_record_rejects_input_change_after_test_started(self):
        before = pvc.fingerprints(self.root, self.state)['save']
        (self.root / 'config.json').write_text('{"schema":2}', encoding='utf-8')
        with self.assertRaisesRegex(pvc.Invalid, 'Snapshot anterior'):
            pvc.capture(self.root, 'save', 'evidence.txt', 'test', 'passed', 'local', 'test', '1.0', before)

    def test_record_rejects_wrong_observed_version(self):
        before = pvc.fingerprints(self.root, self.state)['save']
        with self.assertRaisesRegex(pvc.Invalid, 'Versao observada'):
            pvc.capture(self.root, 'save', 'evidence.txt', 'test', 'passed', 'local', 'test', 'old', before)

    def test_evidence_from_other_project_is_rejected(self):
        self.record()
        self.state['project_id'] = 'different-project'
        with self.assertRaisesRegex(pvc.Invalid, 'outro projeto'):
            pvc.inspect(self.root, self.state)

    def test_test_success_does_not_commission(self):
        item = self.record()
        self.assertEqual(pvc.inspect(self.root, self.state)['operational_approval'], 'requires_explicit_review')
        self.decision(item)
        report = pvc.inspect(self.root, self.state)
        self.assertFalse(report['structurally_valid'])
        self.assertIn('operational', report['errors'][0])

    def test_superseding_legacy_approval_with_no_go_allows_revalidation(self):
        item = self.record(kind='operational')
        self.decision(item)
        old = copy.deepcopy(self.state['decisions'][0])
        old.update(id='D-NOGO', decision='NO_GO', reason='Critical E2E still pending')
        self.state['decisions'].append(old)
        self.persist()
        self.assertTrue(pvc.inspect(self.root, self.state)['structurally_valid'])
        self.record()

    def test_legacy_operational_report_cannot_replace_critical_e2e(self):
        item = self.record(kind='operational')
        self.decision(item)
        report = pvc.inspect(self.root, self.state)
        self.assertFalse(report['structurally_valid'])
        self.assertIn('E2E', ' '.join(report['errors']))

    def test_failed_evidence_cannot_support_go(self):
        item = self.record(kind='operational', result='failed')
        self.decision(item)
        self.assertIn('falha', pvc.inspect(self.root, self.state)['errors'][0])

    def test_g9_requires_operational_evidence(self):
        item = self.record()
        self.decision(item, gate='G9')
        self.assertFalse(pvc.inspect(self.root, self.state)['structurally_valid'])

    def test_modified_artifact_is_stale(self):
        self.record()
        (self.root / 'evidence.txt').write_text('edited', encoding='utf-8')
        self.assertIn('artefato alterado', pvc.inspect(self.root, self.state)['evidence'][0]['reasons'])

    def test_rerun_supersedes_old_evidence_without_losing_history(self):
        old = self.record()
        (self.root / 'config.json').write_text('{"schema":2}', encoding='utf-8')
        new = self.record()
        report = pvc.inspect(self.root, self.state)
        self.assertEqual([e['status'] for e in report['evidence']], ['superseded', 'current'])
        self.assertNotEqual(old['id'], new['id'])
        code, output = self.cli('resume')
        self.assertEqual(code, 0)
        self.assertEqual(len(output['evidence']), 1)

    def test_old_decision_does_not_transfer_to_new_evidence(self):
        item = self.record(kind='operational')
        self.decision(item, gate='G7')
        self.persist()
        self.record(kind='operational')
        self.assertEqual(pvc.inspect(self.root, self.state)['decisions'][0]['status'], 'stale')

    def test_gate_approval_becomes_stale_after_contract_change(self):
        item = self.record(kind='operational')
        self.decision(item)
        (self.root / 'contract.md').write_text('new contract', encoding='utf-8')
        self.assertEqual(pvc.inspect(self.root, self.state)['decisions'][0]['status'], 'stale')

    def test_unrelated_module_change_preserves_evidence(self):
        self.record()
        (self.root / 'unrelated.md').write_text('new unrelated', encoding='utf-8')
        self.assertEqual(pvc.inspect(self.root, self.state)['evidence'][0]['status'], 'current')

    def test_missing_link_or_input_fails(self):
        for field in ('links', 'inputs'):
            with self.subTest(field=field):
                state = copy.deepcopy(self.state)
                if field == 'links':
                    state['links'].append('missing.md')
                else:
                    state['modules']['save']['inputs'].append('missing.py')
                with self.assertRaisesRegex(pvc.Invalid, 'ausente'):
                    pvc.inspect(self.root, state)

    def test_unknown_dependency_and_cycle_fail(self):
        self.state['modules']['contract']['depends_on'] = ['missing']
        with self.assertRaisesRegex(pvc.Invalid, 'desconhecida'):
            pvc.inspect(self.root, self.state)
        self.state['modules']['contract']['depends_on'] = ['save']
        with self.assertRaisesRegex(pvc.Invalid, 'Ciclo'):
            pvc.inspect(self.root, self.state)

    def test_rejects_absolute_and_traversal_paths(self):
        for path in ('../outside', 'C:/outside', '/outside', 'a\\b'):
            with self.subTest(path=path), self.assertRaises(pvc.Invalid):
                pvc.local_file(self.root, path)

    def test_rejects_external_symlink_path(self):
        target = Path(self.temp.name) / 'outside'
        target.write_text('outside', encoding='utf-8')
        try:
            (self.root / 'link').symlink_to(target)
        except OSError as error:
            self.skipTest(f'Symlink indisponivel no ambiente: {error.winerror if hasattr(error, "winerror") else error.errno}')
        with self.assertRaisesRegex(pvc.Invalid, 'fora do projeto'):
            pvc.local_file(self.root, 'link')

    def test_write_lock_prevents_conflicting_mutation(self):
        (self.root / '.pvc/write.lock').write_text('another writer', encoding='utf-8')
        with self.assertRaisesRegex(pvc.Invalid, 'Estado em uso'):
            self.record()
        self.assertEqual((self.root / '.pvc/write.lock').read_text(), 'another writer')

    def test_evidence_cannot_be_its_own_input(self):
        self.state['modules']['save']['inputs'].append('evidence.txt')
        self.persist()
        with self.assertRaisesRegex(pvc.Invalid, 'nao pode ser input'):
            self.record()

    def test_duplicate_ids_and_invalid_schema_fail_cleanly(self):
        self.record()
        self.state['evidence'].append(copy.deepcopy(self.state['evidence'][0]))
        with self.assertRaisesRegex(pvc.Invalid, 'duplicados'):
            pvc.inspect(self.root, self.state)
        self.state['schema_version'] = 2
        self.persist()
        code, output = self.cli('validate')
        self.assertEqual(code, 1)
        self.assertIn('schema_version', output['error'])

    def test_broken_evidence_reference_fails(self):
        item = self.record(kind='operational')
        self.decision(item)
        self.state['decisions'][0]['evidence_ids'] = ['missing']
        with self.assertRaisesRegex(pvc.Invalid, 'inexistente'):
            pvc.inspect(self.root, self.state)

    def test_evidence_for_wrong_module_cannot_approve(self):
        item = self.record('independent', kind='operational')
        self.decision(item)
        with self.assertRaisesRegex(pvc.Invalid, 'outro modulo'):
            pvc.inspect(self.root, self.state)

    def test_stale_cli_exit_is_distinct_from_invalid_state(self):
        self.record()
        (self.root / 'contract.md').write_text('changed', encoding='utf-8')
        code, output = self.cli('validate')
        self.assertEqual(code, 2)
        self.assertTrue(output['structurally_valid'])

    def test_malformed_json_is_actionable(self):
        (self.root / '.pvc/state.json').write_text('{', encoding='utf-8')
        code, output = self.cli('resume')
        self.assertEqual(code, 1)
        self.assertIn('JSON invalido', output['error'])


class RoutingTests(unittest.TestCase):
    def test_execution_loads_skill_and_trigger_index_only(self):
        result = pvc.route('executar', [])
        self.assertEqual(result['paths'], ['skills/pvc-executar/SKILL.md', 'references/fundamentos.md'])
        self.assertFalse(result['loads_content'])

    def test_only_requested_topics_are_added(self):
        result = pvc.route('executar', ['mocks', 'mocks'])
        self.assertEqual(result['paths'], ['skills/pvc-executar/SKILL.md', 'references/fundamentos.md', 'references/mocks.md'])
        self.assertNotIn('references/source/pvc-v1.0.md', result['paths'])

    def test_fundamentals_are_loaded_individually_when_selected(self):
        result = pvc.route('verificar', ['idempotencia'])
        self.assertIn('references/fundamentos/idempotencia.md', result['paths'])
        self.assertNotIn('references/fundamentos/concorrencia.md', result['paths'])
        self.assertNotIn('references/fundamentos/autorizacao.md', result['paths'])

    def test_unknown_topic_fails_without_fallback_to_all(self):
        with self.assertRaisesRegex(pvc.Invalid, 'desconhecido'):
            pvc.route('executar', ['invented'])

    def test_resume_does_not_load_all_reference_files(self):
        result = pvc.route('retomar', [])
        self.assertEqual(len(result['paths']), 2)
        self.assertNotIn('references/gates.md', result['paths'])

    def test_package_links_and_skill_budget(self):
        report = pvc.package_check()
        self.assertEqual(report['skills'], 5)
        self.assertLessEqual(report['max_skill_words'], 500)
        self.assertFalse(report['llm_behavior_tested'])


if __name__ == '__main__':
    unittest.main()
