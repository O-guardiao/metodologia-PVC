#!/usr/bin/env python3
"""PVC 0.1.1: explicit project state, scoped evidence and selective context paths."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import sys
import tempfile
import uuid

PACKAGE = Path(__file__).resolve().parents[1]
PHASES = ('delimitar', 'executar', 'verificar')
KINDS = ('test', 'inspection', 'operational')
DECISIONS = ('GO', 'GO_WITH_RESTRICTIONS', 'NO_GO', 'KILL')


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except FileNotFoundError:
        raise Invalid(f'Arquivo ausente: {path}') from None
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Invalid(f'JSON invalido: {path}: {exc}') from None


def local_file(root, name):
    require(isinstance(name, str) and bool(name.strip()), 'Caminho vazio/invalido')
    require(not PureWindowsPath(name).drive and not Path(name).is_absolute(), f'Caminho deve ser relativo: {name}')
    require('\\' not in name and '..' not in Path(name).parts, f'Caminho inseguro: {name}')
    result = (root / name).resolve()
    require(result.is_relative_to(root.resolve()), f'Caminho fora do projeto: {name}')
    require(result.is_file(), f'Arquivo ausente: {name}')
    return result


def text_field(obj, key, location):
    require(isinstance(obj.get(key), str) and bool(obj[key].strip()), f'{location}.{key}: texto obrigatorio')


def text_list(obj, key, location, nonempty=False):
    value = obj.get(key)
    require(isinstance(value, list) and all(isinstance(v, str) and v.strip() for v in value), f'{location}.{key}: lista de textos esperada')
    require(not nonempty or bool(value), f'{location}.{key}: lista vazia')
    require(len(value) == len(set(value)), f'{location}.{key}: duplicatas')


def object_list(state, key):
    require(isinstance(state.get(key), list) and all(isinstance(x, dict) for x in state[key]), f'{key}: lista de objetos esperada')
    ids = [x.get('id') for x in state[key]]
    require(all(isinstance(x, str) and x.strip() for x in ids), f'{key}: IDs obrigatorios')
    require(len(ids) == len(set(ids)), f'{key}: IDs duplicados')


def validate_shape(state):
    require(isinstance(state, dict), 'Estado deve ser objeto')
    require(type(state.get('schema_version')) is int and state['schema_version'] == 1, 'schema_version deve ser 1')
    for key in ('project_id', 'goal', 'version', 'next_step'):
        text_field(state, key, 'state')
    text_list(state, 'blockers', 'state')
    text_list(state, 'links', 'state')
    modules = state.get('modules')
    require(isinstance(modules, dict), 'modules deve ser objeto')
    for name, module in modules.items():
        require(re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', name) is not None and isinstance(module, dict), 'Modulo invalido (nome: 1 a 64 caracteres)')
        for key in ('inputs', 'requirements', 'depends_on'):
            text_list(module, key, name, nonempty=key != 'depends_on')
        for dep in module['depends_on']:
            require(dep in modules, f'{name}: dependencia desconhecida {dep}')
        maturity = module.get('maturity')
        require(isinstance(maturity, dict), f'{name}: maturity obrigatoria')
        for key, options in [('trl', range(1, 10)), ('trl_target', range(1, 10)), ('lod', (100, 200, 300, 350, 400, 500)), ('lod_target', (100, 200, 300, 350, 400, 500))]:
            require(type(maturity.get(key)) is int and maturity[key] in options, f'{name}: {key} invalido')
    for key in ('evidence', 'decisions', 'pending_actions'):
        object_list(state, key)
    change = state.get('active_change')
    require(change is None or isinstance(change, dict), 'active_change deve ser objeto ou null')
    if change is not None:
        for key in ('id', 'intent', 'next_step'):
            text_field(change, key, 'active_change')
        text_list(change, 'modules', 'active_change', nonempty=True)
        text_list(change, 'preserve', 'active_change', nonempty=True)
        require(all(m in modules for m in change['modules']), 'active_change: modulo desconhecido')
        require(change.get('phase') in PHASES, 'active_change.phase invalida')
    for item in state['evidence']:
        for key in ('project_id', 'module', 'version', 'fingerprint', 'artifact', 'artifact_sha256', 'environment', 'procedure', 'recorded_at'):
            text_field(item, key, 'evidence')
        require(item.get('kind') in KINDS, 'evidence.kind invalido')
        require(item.get('result') in ('passed', 'failed'), 'evidence.result invalido')
        require(item['module'] in modules, 'evidence: modulo desconhecido')
        require(item['project_id'] == state['project_id'], 'Evidencia de outro projeto')
        for key in ('fingerprint', 'artifact_sha256'):
            require(re.fullmatch('[0-9a-f]{64}', item[key]) is not None, f'evidence.{key}: SHA-256 esperado')
    for item in state['decisions']:
        for key in ('module', 'reason', 'reviewer', 'version', 'fingerprint'):
            text_field(item, key, 'decision')
        require(item['module'] in modules, 'decision: modulo desconhecido')
        require(item.get('gate') in [f'G{i}' for i in range(10)], 'decision.gate invalido')
        require(item.get('decision') in DECISIONS, 'decision.decision invalida')
        text_list(item, 'evidence_ids', 'decision', nonempty=True)
    for item in state['pending_actions']:
        for key in ('action', 'target', 'verification', 'next_step'):
            text_field(item, key, 'pending_action')
        require(item.get('status') in ('pending', 'uncertain', 'confirmed', 'denied'), 'pending_action.status invalido')


def fingerprints(root, state):
    """Include declared file bytes and transitive contracts; detect cycles."""
    done, visiting = {}, set()

    def visit(name):
        if name in done:
            return done[name]
        require(name not in visiting, f'Ciclo de dependencias em {name}')
        visiting.add(name)
        module = state['modules'][name]
        files = {p: digest(local_file(root, p).read_bytes()) for p in sorted(module['inputs'])}
        dependencies = {dep: visit(dep) for dep in sorted(module['depends_on'])}
        # Maturity is an assessment, not an input to evidence about behavior.
        definition = {k: module[k] for k in ('inputs', 'requirements', 'depends_on')}
        done[name] = digest(canonical({'project_id': state['project_id'], 'version': state['version'], 'definition': definition, 'files': files, 'dependencies': dependencies}))
        visiting.remove(name)
        return done[name]

    for name in state['modules']:
        visit(name)
    return done


def inspect(root, state):
    validate_shape(state)
    for link in state['links']:
        local_file(root, link)
    prints = fingerprints(root, state)
    evidence, decisions, errors, warnings = [], [], [], []
    latest_evidence = {(x['module'], x['kind']): x['id'] for x in state['evidence']}
    latest_decision = {(x['module'], x['gate']): x['id'] for x in state['decisions']}
    for item in state['evidence']:
        reasons = []
        unavailable = False
        if item['version'] != state['version']:
            reasons.append('versao alterada')
        if item['fingerprint'] != prints[item['module']]:
            reasons.append('entradas ou dependencias alteradas')
        try:
            artifact = local_file(root, item['artifact'])
            if digest(artifact.read_bytes()) != item['artifact_sha256']:
                reasons.append('artefato alterado')
        except (Invalid, OSError) as exc:
            unavailable = True
            reasons.append(str(exc))
        status = 'invalid' if unavailable else ('stale' if reasons else 'current')
        if latest_evidence[(item['module'], item['kind'])] != item['id']:
            status = 'superseded'
        if unavailable:
            message = f"{item['id']}: artefato indisponivel: {item['artifact']}"
            (warnings if status == 'superseded' else errors).append(message)
        evidence.append({'id': item['id'], 'module': item['module'], 'kind': item['kind'], 'result': item['result'], 'artifact': item['artifact'], 'status': status, 'reasons': reasons})
    indexed = {x['id']: x for x in evidence}
    for item in state['decisions']:
        refs = item['evidence_ids']
        require(all(eid in indexed for eid in refs), f"{item['id']}: evidencia inexistente")
        require(all(indexed[eid]['module'] == item['module'] for eid in refs), f"{item['id']}: evidencia de outro modulo")
        stale = item['version'] != state['version'] or item['fingerprint'] != prints[item['module']] or any(indexed[eid]['status'] != 'current' for eid in refs)
        approving = item['decision'] in ('GO', 'GO_WITH_RESTRICTIONS')
        if approving:
            if any(indexed[eid]['result'] != 'passed' for eid in refs):
                errors.append(f"{item['id']}: aprovacao referencia falha")
            if item['gate'] in ('G8', 'G9') and not any(indexed[eid]['kind'] == 'operational' for eid in refs):
                errors.append(f"{item['id']}: G8/G9 exige evidencia operational")
        status = 'stale' if stale else 'current'
        if latest_decision[(item['module'], item['gate'])] != item['id']:
            status = 'superseded'
        decisions.append({**{key: item[key] for key in ('id', 'module', 'gate', 'decision', 'reason', 'reviewer', 'evidence_ids')}, 'status': status})
    unresolved = [x for x in state['pending_actions'] if x['status'] != 'confirmed']
    return {'project_id': state['project_id'], 'version': state['version'], 'fingerprints': prints, 'evidence': evidence, 'decisions': decisions, 'pending_actions': unresolved, 'errors': errors, 'history_warnings': warnings, 'degraded': bool(errors or warnings), 'structurally_valid': not errors, 'operational_approval': 'blocked_degraded_state' if errors or warnings else 'requires_explicit_review'}


def resume_report(state, report, modules=None, limit=10, offset=0):
    require(1 <= limit <= 100 and offset >= 0, 'Use limit de 1 a 100 e offset nao negativo')
    selection = set(modules or state['modules'])
    require(selection.issubset(state['modules']), 'Filtro contem modulo desconhecido')
    active_evidence = [x for x in report['evidence'] if x['status'] != 'superseded']
    active_decisions = [x for x in report['decisions'] if x['status'] != 'superseded']
    missing = [name for name in state['modules'] if not any(e['module'] == name and e['status'] == 'current' and e['result'] == 'passed' for e in active_evidence)]
    pagination = {}

    def page(key, items):
        next_offset = offset + limit if offset + limit < len(items) else None
        pagination[key] = {'total': len(items), 'offset': offset, 'limit': limit, 'next_offset': next_offset}
        return items[offset:offset + limit]

    result = {key: report[key] for key in ('project_id', 'version', 'structurally_valid', 'operational_approval', 'degraded')}
    result.update({'goal': state['goal'], 'active_change': state['active_change'], 'next_step': state['next_step'],
                   'selection': {'modules': sorted(selection) if modules else 'all'},
                   'state_pointer': '.pvc/state.json',
                   'global_index': {'modules': len(state['modules']), 'active_evidence': len(active_evidence),
                       'active_decisions': len(active_decisions), 'stale_evidence': sum(e['status'] == 'stale' for e in active_evidence),
                       'stale_decisions': sum(d['status'] == 'stale' for d in active_decisions),
                       'missing_evidence_modules': len(missing), 'blockers': len(state['blockers']),
                       'uncertain_actions': sum(a['status'] == 'uncertain' for a in report['pending_actions']),
                       'pending_or_denied_actions': sum(a['status'] in ('pending', 'denied') for a in report['pending_actions']),
                       'errors': len(report['errors']), 'history_warnings': len(report['history_warnings'])}})
    collections = {'evidence': [e for e in active_evidence if e['module'] in selection],
                   'decisions': [d for d in active_decisions if d['module'] in selection],
                   'pending_actions': report['pending_actions'], 'blockers': state['blockers'], 'links': state['links'],
                   'errors': report['errors'], 'history_warnings': report['history_warnings'],
                   'missing_evidence': [name for name in missing if name in selection]}
    for key, items in collections.items():
        result[key] = page(key, items)
    names = page('maturity', [name for name in state['modules'] if name in selection])
    result['maturity'] = {name: state['modules'][name]['maturity'] for name in names}
    result['pagination'] = pagination
    result['assessment_incomplete'] = report.get('assessment_incomplete', False)
    if result['assessment_incomplete']:
        result['global_index']['stale_evidence'] = None
        result['global_index']['stale_decisions'] = None
    result['instruction'] = 'Consulte o destino de acoes incertas antes de repetir. Contagens globais incluem itens fora do recorte/pagina. Leia paginas de blockers, acoes e erros antes de agir; use --offset N --limit L e opcional --module NOME. Validacao mecanica nao e aceite operacional.'
    # Bound long prose and nested lists too; expose every omission with its pointer.
    truncations = []

    def compact(value, pointer):
        if isinstance(value, str) and len(value) > 400:
            truncations.append({'pointer': pointer, 'omitted_characters': len(value) - 400})
            return value[:400] + ' [trecho; consulte state_pointer]'
        if isinstance(value, list):
            if len(value) > limit:
                truncations.append({'pointer': pointer, 'omitted_items': len(value) - limit})
            return [compact(item, f'{pointer}/{i}') for i, item in enumerate(value[:limit])]
        if isinstance(value, dict):
            return {key: compact(item, f'{pointer}/{key}') for key, item in value.items()}
        return value

    result = compact(result, '')
    result['truncations'] = truncations
    return result


def state_path(root):
    directory = root / '.pvc'
    require(not directory.is_symlink() and directory.resolve().is_relative_to(root.resolve()), '.pvc deve estar dentro do projeto')
    path = directory / 'state.json'
    require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), 'state.json deve estar dentro do projeto')
    return path


@contextmanager
def state_lock(root):
    path = state_path(root)
    path.parent.mkdir(exist_ok=True)
    lock = path.parent / 'write.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise Invalid('Estado em uso; verifique o processo escritor antes de remover .pvc/write.lock') from None
    try:
        os.close(fd)
        yield path
    finally:
        lock.unlink()


def save(path, state):
    validate_shape(state)
    fd, name = tempfile.mkstemp(prefix='state-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def initialize(root, goal, version):
    with state_lock(root) as path:
        require(not path.exists(), 'Estado existente preservado; use resume')
        state = {'schema_version': 1, 'project_id': str(uuid.uuid4()), 'goal': goal, 'version': version, 'next_step': 'Delimitar o primeiro fluxo e registrar modulos, criterios e entradas.', 'active_change': None, 'modules': {}, 'evidence': [], 'decisions': [], 'pending_actions': [], 'links': [], 'blockers': []}
        save(path, state)
    return state


def capture(root, module, artifact, kind, result, environment, procedure, observed_version, expected_fingerprint):
    with state_lock(root) as path:
        original = path.read_bytes()
        state = read_json(path)
        report = inspect(root, state)
        require(report['structurally_valid'], 'Corrija decisoes invalidas antes de registrar evidencia')
        require(module in state['modules'], f'Modulo desconhecido: {module}')
        require(observed_version == state['version'], 'Versao observada difere da versao atual')
        require(expected_fingerprint == report['fingerprints'][module], 'Snapshot anterior a execucao mudou; reexecute a verificacao')
        artifact_path = local_file(root, artifact)
        # Evidence must not fingerprint itself or it becomes stale as it is written.
        require(artifact not in {p for m in state['modules'].values() for p in m['inputs']}, 'Artefato de evidencia nao pode ser input')
        require(artifact != '.pvc/state.json', 'Estado nao e artefato de evidencia')
        item = {'id': str(uuid.uuid4()), 'project_id': state['project_id'], 'module': module, 'version': state['version'], 'fingerprint': report['fingerprints'][module], 'artifact': artifact, 'artifact_sha256': digest(artifact_path.read_bytes()), 'kind': kind, 'result': result, 'environment': environment, 'procedure': procedure, 'recorded_at': datetime.now(timezone.utc).isoformat()}
        require(fingerprints(root, state) == report['fingerprints'] and digest(artifact_path.read_bytes()) == item['artifact_sha256'], 'Arquivos mudaram durante registro; execute novamente a verificacao')
        require(path.read_bytes() == original, 'Estado mudou durante registro; releia antes de tentar novamente')
        state['evidence'].append(item)
        save(path, state)
    return item


def route(operation, topics):
    catalog = read_json(PACKAGE / 'catalog.json')
    require(operation in catalog['operations'], f'Operacao desconhecida: {operation}')
    chosen = catalog['operations'][operation]
    paths = [chosen['skill'], *chosen['references']]
    for topic in topics:
        require(topic in catalog['topics'], f'Tema desconhecido: {topic}')
        paths.append(catalog['topics'][topic])
    for path in paths:
        local_file(PACKAGE, path)
    return {'operation': operation, 'paths': list(dict.fromkeys(paths)), 'package_root': str(PACKAGE), 'loads_content': False}


def package_check():
    catalog = read_json(PACKAGE / 'catalog.json')
    for operation in catalog['operations']:
        route(operation, list(catalog['topics']))
    skills = [PACKAGE / 'skills/pvc/SKILL.md', *[PACKAGE / x['skill'] for x in catalog['operations'].values()]]
    for path in skills:
        content = path.read_text(encoding='utf-8')
        require(re.match(r'---\nname: .+\ndescription: .+\n---\n', content) is not None, f'Frontmatter invalido: {path}')
        require(len(content.split()) <= 500, f'Skill excede 500 palavras: {path}')
    checked = 0
    for path in PACKAGE.rglob('*.md'):
        if any(x in path.relative_to(PACKAGE).parts for x in ('.git', '.pvc', '.pvc-method', 'source')):
            continue
        for match in re.finditer(r'\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            target = match.group(1).split('#', 1)[0]
            if not target or re.match(r'[a-z]+://', target):
                continue
            resolved = (path.parent / target).resolve()
            require(resolved.is_relative_to(PACKAGE) and resolved.is_file(), f'Link local quebrado: {path.relative_to(PACKAGE)} -> {target}')
            checked += 1
    return {'valid': True, 'skills': len(skills), 'local_links_checked': checked, 'max_skill_words': max(len(p.read_text(encoding='utf-8').split()) for p in skills), 'llm_behavior_tested': False}


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest='command', required=True)
    for name in ('init', 'validate', 'resume', 'record', 'snapshot'):
        command = sub.add_parser(name)
        command.add_argument('--project', required=True, type=Path)
        if name == 'snapshot':
            command.add_argument('--module', required=True)
        if name == 'resume':
            command.add_argument('--module', action='append')
            command.add_argument('--limit', type=int, default=10)
            command.add_argument('--offset', type=int, default=0)
        if name == 'init':
            command.add_argument('--goal', required=True)
            command.add_argument('--version', required=True)
        if name == 'record':
            for arg in ('module', 'artifact', 'environment', 'procedure', 'observed-version', 'expected-fingerprint'):
                command.add_argument('--' + arg, required=True)
            command.add_argument('--kind', required=True, choices=KINDS)
            command.add_argument('--result', required=True, choices=('passed', 'failed'))
    routing = sub.add_parser('route')
    routing.add_argument('operation', choices=('retomar', *PHASES))
    routing.add_argument('--topic', action='append', default=[])
    sub.add_parser('check-package')
    return result


def run(args):
    if args.command == 'route':
        return route(args.operation, args.topic), 0
    if args.command == 'check-package':
        return package_check(), 0
    root = args.project.resolve()
    require(root.is_dir(), f'Projeto ausente: {root}')
    if args.command == 'init':
        state = initialize(root, args.goal, args.version)
        return {'initialized': True, 'project_id': state['project_id'], 'next_step': state['next_step']}, 0
    if args.command == 'record':
        return capture(root, args.module, args.artifact, args.kind, args.result, args.environment, args.procedure, args.observed_version, args.expected_fingerprint), 0
    state = read_json(state_path(root))
    try:
        report = inspect(root, state)
    except (Invalid, OSError) as exc:
        if args.command != 'resume':
            raise
        validate_shape(state)
        report = {'project_id': state['project_id'], 'version': state['version'], 'evidence': [], 'decisions': [],
                  'pending_actions': [a for a in state['pending_actions'] if a['status'] != 'confirmed'],
                  'errors': [str(exc)], 'history_warnings': [], 'degraded': True, 'structurally_valid': False,
                  'operational_approval': 'blocked_degraded_state', 'assessment_incomplete': True}
    if args.command == 'snapshot':
        require(args.module in state['modules'], f'Modulo desconhecido: {args.module}')
        return {'project_id': state['project_id'], 'module': args.module, 'version': state['version'], 'fingerprint': report['fingerprints'][args.module], 'instruction': 'Guarde antes de executar a verificacao; use no record apos a execucao.'}, 0
    stale = any(x['status'] == 'stale' for x in report['evidence'] + report['decisions'])
    code = 1 if report['degraded'] else (2 if stale else 0)
    if args.command == 'resume':
        report = resume_report(state, report, args.module, args.limit, args.offset)
    return report, code


def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    args = parser().parse_args(argv)
    try:
        result, code = run(args)
    except (Invalid, OSError) as exc:
        result, code = {'error': str(exc)}, 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    sys.exit(main())
