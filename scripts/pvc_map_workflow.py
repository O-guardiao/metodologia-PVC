"""Local transaction workflow for textual catalogs; not a security sandbox."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile
import uuid

from pvc_catalog import (CatalogError, canonical, fingerprint, read_json, need, inventory,
                         validate_catalog, strings, relative, render, git, page, query, clip)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='temp-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            json.dump(data, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='temp-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def safe_control(control):
    need(not control.is_symlink(), 'Symlink control unsupported')
    if control.exists():
        for base, dirs, files in os.walk(control, followlinks=False):
            for name in dirs + files:
                need(not (Path(base) / name).is_symlink(), 'Symlink inside control directory unsupported')


@contextmanager
def locked(control):
    safe_control(control)
    need(control.exists() and not control.is_symlink(), 'Run init first; symlink control unsupported')
    lock = control / 'write.lock'
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise CatalogError('Writer lock exists. Inspect process before manual recovery; never blindly delete it.') from None
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def validate_plan(spec):
    need(isinstance(spec, dict), 'Plan must be object')
    for key in ('intent', 'next_step'):
        need(isinstance(spec.get(key), str) and spec[key].strip(), f'Plan {key} required')
    for key in ('scope', 'affected', 'preserve'):
        strings(spec.get(key), key, allow_empty=key == 'affected')
    for path in spec['scope']:
        relative(path)
    tests = spec.get('tests')
    need(isinstance(tests, list) and tests, 'Plan tests required')
    for argv in tests:
        need(isinstance(argv, list) and argv and all(isinstance(v, str) and v for v in argv), 'Test argv must be a nonempty string list')


class Workflow:
    def __init__(self, root):
        self.root = Path(root).resolve()
        need(self.root.is_dir(), 'Project root missing')
        self.control = self.root / '.pvc-map'
        need(not self.control.is_symlink(), 'Symlink control unsupported')

    def baseline(self):
        need(not (self.control / 'journal.json').exists(), 'Promotion incomplete: inspect status and recover')
        return self._baseline()

    def _baseline(self, relocating=False):
        safe_control(self.control)
        pointer = (self.control / 'CURRENT').read_text(encoding='utf-8').strip()
        need(len(pointer) == 32 and all(c in '0123456789abcdef' for c in pointer), 'Invalid CURRENT')
        folder = self.control / 'generations' / pointer
        manifest = read_json(folder / 'manifest.json')
        catalog = read_json(folder / 'catalog.json')
        need(isinstance(manifest, dict) and manifest.get('schema_version') == 1, 'Invalid manifest')
        if not relocating and manifest.get('root') != str(self.root):
            binding = read_json(self.control / 'relocation.json')
            need(binding == {'project_id': manifest.get('project_id'), 'generation': pointer,
                 'root': str(self.root), 'inventory': fingerprint(manifest.get('files'))},
                 'Catalog belongs to another project path; explicit relocation required')
        need(isinstance(manifest.get('project_id'), str) and manifest['project_id'], 'Project identity missing')
        need(isinstance(manifest.get('files'), dict), 'Invalid inventory')
        for path, item in manifest['files'].items():
            relative(path)
            need(isinstance(item, dict) and isinstance(item.get('bytes'), int), 'Invalid inventory item')
            sha = item.get('sha256')
            need(isinstance(sha, str) and len(sha) == 64 and all(c in '0123456789abcdef' for c in sha), 'Invalid inventory hash')
        validate_catalog(catalog, manifest['files'])
        need(manifest.get('catalog_hash') == fingerprint(catalog), 'Catalog altered outside generation')
        expected = render(catalog, manifest['files'])
        for name, content in expected.items():
            need((folder / name).read_text(encoding='utf-8') == content, f'Generated page altered: {name}')
        return pointer, manifest, catalog

    def init(self, catalog):
        need(not self.control.exists(), 'Catalog already exists; init never overwrites')
        files = inventory(self.root)
        validate_catalog(catalog, files)
        project = str(uuid.uuid4())
        self.control.mkdir()
        write_text(self.control / '.gitignore', 'change.json\njournal.json\nreceipt.json\nrelocation.json\nwrite.lock\nlogs/\ntemp-*\n')
        gen = self.generation(catalog, files, project)
        write_text(self.control / 'CURRENT', gen + '\n')
        return {'generation': gen, 'project_id': project, 'next': 'Inspect and commit catalog baseline before checkpoint'}

    def generation(self, catalog, files, project):
        gen = uuid.uuid4().hex
        folder = self.control / 'generations' / gen
        manifest = {'schema_version': 1, 'project_id': project, 'root': str(self.root),
                    'created_at': datetime.now(timezone.utc).isoformat(), 'files': files,
                    'catalog_hash': fingerprint(catalog), 'inventory_excludes': sorted(__import__('pvc_catalog').EXCLUDED)}
        write_json(folder / 'catalog.json', catalog)
        write_json(folder / 'manifest.json', manifest)
        for name, content in render(catalog, files).items():
            write_text(folder / name, content)
        return gen

    def relocate(self, expected_head):
        """Bind a verified copy locally; never rewrite identity or renew evidence."""
        need(not (self.control / 'journal.json').exists(), 'Recover promotion at original checkout first')
        gen, manifest, catalog = self._baseline(relocating=True)
        if (self.control / 'change.json').exists():
            need(self.load_change()['phase'] == 'promoted', 'Pending change cannot relocate')
        head = git(self.root, 'rev-parse', 'HEAD')
        need(isinstance(expected_head, str) and expected_head == head, 'Expected full HEAD mismatch')
        need(Path(git(self.root, 'rev-parse', '--show-toplevel')).resolve() == self.root, 'Project must be Git root')
        need(not git(self.root, 'status', '--porcelain'), 'Relocation requires clean Git')
        need(git(self.root, 'show', 'HEAD:.pvc-map/CURRENT') == gen, 'Committed pointer mismatch')
        names = ['manifest.json', 'catalog.json', *render(catalog, manifest['files'])]
        if (self.control / 'generations' / gen / 'audit.json').exists():
            names.append('audit.json')
        for name in names:
            path = f'.pvc-map/generations/{gen}/{name}'
            need(git(self.root, 'show', 'HEAD:' + path) == (self.root / path).read_text(encoding='utf-8').strip(), 'Committed generation differs')
        need(inventory(self.root) == manifest['files'], 'Copied inventory differs; relocation cannot refresh stale evidence')
        write_json(self.control / 'relocation.json', {'project_id': manifest['project_id'],
                   'generation': gen, 'root': str(self.root), 'inventory': fingerprint(manifest['files'])})
        return {'generation': gen, 'project_id': manifest['project_id'], 'bound_root': str(self.root),
                'evidence_renewed': False, 'next': 'Run entry; inspect environment and rerun relevant tests'}

    def load_change(self):
        safe_control(self.control)
        change = read_json(self.control / 'change.json')
        need(isinstance(change, dict) and change.get('schema_version') == 1, 'Invalid change state')
        need(change.get('phase') in ('planned', 'checkpoint', 'candidate', 'tested', 'reviewed', 'promoted'), 'Invalid phase')
        validate_plan(change.get('plan'))
        need(isinstance(change.get('generation'), str) and isinstance(change.get('project_id'), str), 'Invalid change identity')
        if change['phase'] != 'planned':
            need(isinstance(change.get('base_head'), str) and len(change['base_head']) in (40, 64), 'Missing Git checkpoint')
        if change['phase'] in ('candidate', 'tested', 'reviewed', 'promoted'):
            need(isinstance(change.get('candidate'), dict), 'Candidate missing')
            need(isinstance(change.get('candidate_files'), dict), 'Candidate inventory missing')
            for path, item in change['candidate_files'].items():
                relative(path)
                need(isinstance(item, dict) and type(item.get('bytes')) is int and item['bytes'] >= 0, 'Invalid candidate inventory')
                sha = item.get('sha256')
                need(isinstance(sha, str) and len(sha) == 64 and all(c in '0123456789abcdef' for c in sha), 'Invalid candidate hash')
            validate_catalog(change['candidate'], change['candidate_files'])
            need(change.get('candidate_digest') == fingerprint({'catalog': change['candidate'], 'files': change['candidate_files']}), 'Candidate altered')
        if change['phase'] in ('tested', 'reviewed', 'promoted'):
            test = change.get('test_run')
            need(isinstance(test, dict) and test.get('digest') == change['candidate_digest'], 'Test evidence stale')
            need(isinstance(test.get('results'), list) and len(test['results']) == len(change['plan']['tests']), 'Incomplete test evidence')
            for result, argv in zip(test['results'], change['plan']['tests']):
                need(isinstance(result, dict) and result.get('argv') == argv and type(result.get('returncode')) is int, 'Malformed test result')
                log = result.get('log')
                need(isinstance(log, str) and log.startswith('logs/') and '..' not in Path(log).parts, 'Invalid log path')
                need(result.get('sha256') == __import__('pvc_catalog').file_hash(self.control / log), 'Test log missing/changed')
        if change['phase'] in ('reviewed', 'promoted'):
            review = change.get('review')
            need(isinstance(review, dict) and all(isinstance(review.get(k), str) and review[k].strip() for k in ('reviewer', 'note', 'digest')), 'Invalid review')
            need(review['digest'] == change['candidate_digest'], 'Review stale')
        return change

    def checked(self, phases):
        gen, manifest, catalog = self.baseline()
        change = self.load_change()
        need(change['phase'] in phases, f'Expected phase {phases}; got {change["phase"]}')
        need(change['generation'] == gen and change['project_id'] == manifest['project_id'], 'Change baseline/identity mismatch')
        return change, manifest, catalog

    def save(self, change):
        write_json(self.control / 'change.json', change)

    def delta(self, baseline, current):
        return sorted(p for p in baseline.keys() | current.keys() if baseline.get(p) != current.get(p))

    def bounded_status(self, limit=10, offset=0):
        if (self.control / 'journal.json').exists():
            return {'blocked': 'promotion_incomplete', 'next': 'recover; do not repeat promotion'}
        gen, manifest, catalog = self.baseline()
        current = inventory(self.root)
        delta = self.delta(manifest['files'], current)
        covered = {s['path'] for s in catalog['symbols']}
        result = {'generation': gen, 'project_id': manifest['project_id'], 'index': f'.pvc-map/generations/{gen}/INDEX.md',
                  'fresh': not delta, 'delta': page(delta, limit, offset), 'files': len(current),
                  'symbols_declared': len(catalog['symbols']), 'unmapped_files': page(sorted(set(current) - covered), limit, offset),
                  'coverage': 'declared only; no automatic semantic completeness',
                  'catalogs': page([{'id': g['id'], 'title': clip(g['title']), 'purpose': clip(g['purpose'])} for g in catalog['catalogs']], limit, offset)}
        if (self.control / 'change.json').exists():
            change = self.load_change()
            result['change'] = {'phase': change['phase'], 'intent': clip(change['plan']['intent']), 'next_step': clip(change['plan']['next_step']), 'execution_status': change.get('execution_status', 'not running')}
            if change['phase'] == 'promoted':
                result['change']['plan_next_step'] = result['change']['next_step']
                result['change']['next_step'] = 'Inspect committed result and pending operational acceptance; do not repeat implementation'
                result['change']['commit'] = change['commit']
        return result

    def entry(self, limit=10, offset=0):
        result = self.bounded_status(limit, offset)
        need(not result.get('blocked'), 'Promotion incomplete; recover first')
        gen, manifest, _ = self.baseline()
        write_json(self.control / 'receipt.json', {'project_id': manifest['project_id'],
                   'generation': gen, 'inventory': fingerprint(manifest['files'])})
        result['receipt'] = 'entry emitted; this does not prove cognitive reading'
        return result

    def require_entry(self, gen, manifest):
        receipt = read_json(self.control / 'receipt.json')
        need(isinstance(receipt, dict) and receipt == {'project_id': manifest['project_id'],
             'generation': gen, 'inventory': fingerprint(manifest['files'])}, 'Run entry for current baseline first')

    def show(self, sid, limit=10, offset=0):
        gen, manifest, catalog = self.baseline()
        self.require_entry(gen, manifest)
        symbols = {s['id']: s for s in catalog['symbols']}
        need(sid in symbols, 'Unknown symbol ID')
        symbol = symbols[sid]
        result = {k: clip(symbol[k]) for k in ('id', 'name', 'path', 'kind', 'catalog', 'purpose', 'confidence')}
        for key in ('inputs', 'outputs', 'invariants', 'depends_on', 'aliases', 'tests', 'unknown_dependencies'):
            result[key] = page([clip(x) for x in symbol[key]], limit, offset)
        result['consumers'] = page(sorted(s['id'] for s in symbols.values() if sid in s['depends_on']), limit, offset)
        result['generation'] = gen
        result['detail'] = f'.pvc-map/generations/{gen}/catalogs/{symbol["catalog"]}.md'
        result['warning'] = 'Declared dependencies only. Inspect current source and status before changing.'
        return result

    def plan(self, spec):
        validate_plan(spec)
        gen, manifest, catalog = self.baseline()
        self.require_entry(gen, manifest)
        need(inventory(self.root) == manifest['files'], 'Baseline stale; reconcile actual changes before planning')
        if (self.control / 'change.json').exists():
            need(self.load_change()['phase'] == 'promoted', 'Active change already exists')
        need(all(s in {v['id'] for v in catalog['symbols']} for s in spec['affected']), 'Unknown affected symbol')
        change = {'schema_version': 1, 'phase': 'planned', 'generation': gen,
                  'project_id': manifest['project_id'], 'plan': spec}
        self.save(change)
        return change

    def checkpoint(self):
        change, manifest, _ = self.checked(('planned',))
        need(inventory(self.root) == manifest['files'], 'Files changed before checkpoint')
        need(Path(git(self.root, 'rev-parse', '--show-toplevel')).resolve() == self.root, 'Project must be Git root')
        need(not git(self.root, 'status', '--porcelain'), 'Checkpoint requires clean Git including untracked files')
        need(git(self.root, 'show', 'HEAD:.pvc-map/CURRENT') == change['generation'], 'Baseline is not committed')
        change.update(phase='checkpoint', base_head=git(self.root, 'rev-parse', 'HEAD'))
        self.save(change)
        return {'restore_point': change['base_head'], 'phase': change['phase']}

    def candidate(self, catalog):
        change, manifest, _ = self.checked(('checkpoint', 'candidate', 'tested', 'reviewed'))
        need(git(self.root, 'rev-parse', 'HEAD') == change['base_head'], 'Concurrent Git change; replan required')
        files = inventory(self.root)
        validate_catalog(catalog, files)
        delta = self.delta(manifest['files'], files)
        need(set(delta) <= set(change['plan']['scope']), f'Out-of-scope files: {set(delta) - set(change["plan"]["scope"])}')
        change.update(phase='candidate', candidate=catalog, candidate_files=files,
                      candidate_digest=fingerprint({'catalog': catalog, 'files': files}), delta=delta)
        change.pop('test_run', None)
        change.pop('review', None)
        self.save(change)
        return {'phase': 'candidate', 'delta': delta, 'baseline_unchanged': True}

    def current_candidate(self, change):
        need(inventory(self.root) == change['candidate_files'], 'Candidate stale: regenerate and retest')
        need(git(self.root, 'rev-parse', 'HEAD') == change['base_head'], 'HEAD changed after checkpoint')

    def test(self, reviewed=False, timeout=120, reconciled_effects=None):
        need(reviewed, 'Review test commands and environment, then supply --run-reviewed-tests')
        change, _, _ = self.checked(('candidate', 'tested', 'reviewed'))
        self.current_candidate(change)
        if change.get('execution_status'):
            need(isinstance(reconciled_effects, str) and reconciled_effects.strip(),
                 'Uncertain previous execution: inspect effects and supply --reconciled-effects reason before retry')
            change['reconciliation'] = {'reason': reconciled_effects, 'previous': change['execution_status']}
        # Invalidate reusable authorization BEFORE any command can run or interrupt.
        change.update(phase='candidate', execution_status='uncertain: execution started; inspect effects before retry')
        change.pop('test_run', None)
        change.pop('review', None)
        self.save(change)
        results = []
        self.control.joinpath('logs').mkdir(exist_ok=True)
        for argv in change['plan']['tests']:
            try:
                proc = subprocess.run(argv, cwd=self.root, capture_output=True, timeout=timeout, shell=False)
                content, code = proc.stdout + b'\n' + proc.stderr, proc.returncode
            except subprocess.TimeoutExpired as exc:
                content, code = (exc.stdout or b'') + b'\nTIMEOUT\n' + (exc.stderr or b''), 124
            except OSError as exc:
                content, code = str(exc).encode(), 127
            name = 'logs/' + uuid.uuid4().hex + '.txt'
            (self.control / name).write_bytes(content)
            results.append({'argv': argv, 'returncode': code, 'log': name, 'sha256': __import__('hashlib').sha256(content).hexdigest()})
        unchanged = inventory(self.root) == change['candidate_files']
        change.update(phase='tested' if unchanged else 'candidate', test_run={'digest': change['candidate_digest'], 'results': results})
        change.pop('review', None)
        if any(r['returncode'] == 124 for r in results):
            change['execution_status'] = 'uncertain: timed out; inspect effects before retry'
        else:
            change.pop('execution_status', None)
        self.save(change)
        return {'results': results, 'passed': unchanged and all(r['returncode'] == 0 for r in results),
                'candidate_unchanged': unchanged, 'baseline_unchanged': True}

    def review(self, reviewer, note):
        need(isinstance(reviewer, str) and reviewer.strip() and isinstance(note, str) and note.strip(), 'Review identity/note required')
        change, _, _ = self.checked(('tested',))
        self.current_candidate(change)
        need(all(r['returncode'] == 0 for r in change['test_run']['results']), 'Tests failed')
        change.update(phase='reviewed', review={'reviewer': reviewer, 'note': note, 'digest': change['candidate_digest']})
        self.save(change)
        return {'phase': 'reviewed', 'note': note, 'scope': change['plan']['scope']}

    def promote(self):
        change, manifest, _ = self.checked(('reviewed',))
        self.current_candidate(change)
        need(all(r['returncode'] == 0 for r in change['test_run']['results']), 'Tests failed')
        # Staged unrelated content must never be silently included in our commit.
        staged = git(self.root, 'diff', '--cached', '--name-only').splitlines()
        need(not staged, 'Unrelated/prestaged content present; inspect index first')
        gen = self.generation(change['candidate'], change['candidate_files'], manifest['project_id'])
        write_json(self.control / 'generations' / gen / 'audit.json',
                   {'plan': change['plan'], 'review': change['review'], 'test_run': change['test_run'],
                    'base_head': change['base_head'], 'candidate_digest': change['candidate_digest'],
                    'logs': 'local ignored files; hashes and commands recorded, rerun to reproduce'})
        journal = {'schema_version': 1, 'previous': change['generation'], 'candidate': gen,
                   'base_head': change['base_head'], 'digest': change['candidate_digest']}
        write_json(self.control / 'journal.json', journal)
        write_text(self.control / 'CURRENT', gen + '\n')
        paths = [p for p in change['plan']['scope'] if (self.root / p).exists() or p in manifest['files']]
        git(self.root, 'add', '-A', '--', *paths, '.pvc-map/CURRENT', f'.pvc-map/generations/{gen}')
        git(self.root, 'commit', '-m', 'PVC: ' + change['plan']['intent'][:120])
        return self.recover()

    def recover(self):
        """Finalize only proven commits; otherwise stop without reset or discard."""
        journal = read_json(self.control / 'journal.json')
        need(isinstance(journal, dict) and journal.get('schema_version') == 1, 'Invalid promotion journal')
        for key in ('previous', 'candidate'):
            need(isinstance(journal.get(key), str) and len(journal[key]) == 32 and all(c in '0123456789abcdef' for c in journal[key]), 'Invalid journal generation')
        change = self.load_change()
        need(change['phase'] in ('reviewed', 'promoted') and journal.get('previous') == change['generation'] and journal.get('digest') == change['candidate_digest'], 'Journal/change mismatch')
        head = git(self.root, 'rev-parse', 'HEAD')
        need(head != change['base_head'], 'Promotion not committed. Inspect staged diff; commit intended code/map together, then recover. No automatic reset.')
        need(git(self.root, 'show', 'HEAD:.pvc-map/CURRENT') == journal['candidate'], 'Committed map does not match candidate')
        need(git(self.root, 'rev-parse', 'HEAD^') == change['base_head'], 'Concurrent commit: inspect ancestry before recovery')
        gen, manifest, catalog = self._baseline()
        need(gen == journal['candidate'] and manifest['files'] == change['candidate_files'] and catalog == change['candidate'], 'Published candidate mismatched')
        for name in ('manifest.json', 'catalog.json', 'audit.json', *render(catalog, manifest['files'])):
            path = f'.pvc-map/generations/{gen}/{name}'
            need(git(self.root, 'show', 'HEAD:' + path) == (self.root / path).read_text(encoding='utf-8').strip(), 'Committed generation incomplete/different')
        need(inventory(self.root) == manifest['files'], 'Working files differ after promotion; inspect before recovery')
        tracked = git(self.root, 'diff', 'HEAD', '--name-only')
        need(not tracked, 'Uncommitted differences after promotion')
        change.update(phase='promoted', commit=head, promoted_generation=gen)
        self.save(change)
        (self.control / 'journal.json').unlink()
        return {'phase': 'promoted', 'commit': head, 'generation': gen, 'remote_publication': 'not attempted', 'operational_acceptance': False}
