"""Declared journey contracts: coverage is evidence, never an automatic release."""
import hashlib
import json
import re

LEVELS = ('unit', 'integration', 'e2e', 'simulated')
INTERFACES = ('browser', 'api', 'cli')


def texts(values, require, label, nonempty=False):
    require(isinstance(values, list) and all(isinstance(v, str) and v.strip() for v in values), label)
    require(len(values) == len(set(values)) and (not nonempty or bool(values)), label)


def validate_journeys(state, require):
    journeys = state.get('journeys', [])
    require(isinstance(journeys, list) and all(isinstance(j, dict) for j in journeys), 'journeys: object list required')
    seen = set()
    for j in journeys:
        for key in ('id', 'profile'):
            require(isinstance(j.get(key), str) and j[key].strip(), 'journey text required')
        require(j['id'] not in seen, 'duplicate journey')
        seen.add(j['id'])
        texts(j.get('modules'), require, 'journey modules', True)
        require(all(m in state['modules'] for m in j['modules']), 'unknown journey module')
        require(type(j.get('critical')) is bool and j.get('interface') in INTERFACES, 'journey critical/interface invalid')
        texts(j.get('boundaries'), require, 'journey boundaries', True)
        scenarios = j.get('scenarios')
        require(isinstance(scenarios, list) and scenarios and all(isinstance(s, dict) for s in scenarios), 'journey scenarios required')
        ids = []
        for s in scenarios:
            require(isinstance(s.get('id'), str) and s['id'].strip(), 'scenario id required')
            ids.append(s['id'])
            texts(s.get('criteria'), require, 'scenario criteria', True)
        require(len(ids) == len(set(ids)), 'duplicate scenario')


def validate_evidence(item, state, require):
    v = item.get('verification')
    if v is None:
        return
    require(isinstance(v, dict) and v.get('level') in LEVELS, 'verification level invalid')
    for key in ('scenario', 'profile'):
        require(isinstance(v.get(key), str) and v[key].strip(), 'verification identity required')
    require(v.get('interface') in INTERFACES, 'verification interface invalid')
    require(v.get('source_state') in ('clean', 'dirty'), 'verification source_state invalid')
    require(isinstance(v.get('commit'), str) and re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', v['commit']) is not None, 'verification commit required')
    for key in ('criteria', 'boundaries', 'simulated_boundaries'):
        texts(v.get(key), require, 'verification ' + key)
    if v.get('journey') is not None or v['level'] == 'e2e':
        journeys = {j['id']: j for j in state.get('journeys', [])}
        require(isinstance(v.get('journey'), str) and v['journey'] in journeys, 'unknown evidence journey')
        j = journeys[v['journey']]
        require(item['module'] in j['modules'], 'evidence module outside journey')
        require(v['scenario'] in {s['id'] for s in j['scenarios']}, 'unknown evidence scenario')
        criteria = next(s['criteria'] for s in j['scenarios'] if s['id'] == v['scenario'])
        require(set(v['criteria']) <= set(criteria), 'unknown evidence criterion')


def evidence_key(item):
    v = item.get('verification') or {}
    return (item['module'], item['kind'], v.get('level', 'unclassified'), v.get('journey'),
            v.get('scenario'), v.get('profile'), item.get('environment') if v else None)


def evidence_fingerprint(state, prints, item):
    v = item.get('verification') or {}
    if not v.get('journey'):
        return prints[item['module']]
    j = next(j for j in state['journeys'] if j['id'] == v['journey'])
    data = {'journey': j, 'modules': {m: prints[m] for m in sorted(j['modules'])}}
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def journey_coverage(state, reports, module=None):
    journeys = [j for j in state.get('journeys', []) if j['critical'] and (module is None or module in j['modules'])]
    results = []
    for j in journeys:
        candidates = [e for e in reports if (e.get('verification') or {}).get('journey') == j['id']]
        environments = sorted({e['environment'] for e in candidates if isinstance(e.get('environment'), str) and e['environment'].strip()})
        assessments = []
        for environment in environments:
            missing = []
            for scenario in j['scenarios']:
                covered = set()
                for e in candidates:
                    v = e.get('verification') or {}
                    if (e.get('environment') == environment and e.get('status') == 'current' and e.get('result') == 'passed' and
                        v.get('level') == 'e2e' and v.get('scenario') == scenario['id'] and
                        v.get('profile') == j['profile'] and v.get('interface') == j['interface'] and
                        not v.get('simulated_boundaries') and set(j['boundaries']) <= set(v.get('boundaries', []))):
                        covered.update(v.get('criteria', []))
                missing.extend(scenario['id'] + ':' + c for c in scenario['criteria'] if c not in covered)
            assessments.append({'environment': environment, 'profile': j['profile'], 'eligible': not missing, 'missing': missing})
        best = min(assessments, key=lambda a: len(a['missing'])) if assessments else {
            'environment': None, 'profile': j['profile'], 'eligible': False,
            'missing': [s['id'] + ':' + c for s in j['scenarios'] for c in s['criteria']]}
        results.append({'id': j['id'], 'eligible': best['eligible'], 'missing': best['missing'],
                        'environment': best['environment'], 'profile': j['profile'], 'environments': assessments})
    eligible = bool(results) and all(r['eligible'] for r in results)
    return {'eligible': eligible, 'journeys': results,
            'reason': 'requires explicit operational review' if eligible else 'critical E2E coverage pending; no automatic exception'}
