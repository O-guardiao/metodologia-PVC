"""Acceptance contracts: scenario coverage, not counts of isolated passing tests."""
import copy
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pvc_e2e as e2e
import pvc


def require(condition, message):
    if not condition:
        raise ValueError(message)


def state():
    return {'modules': {'frontend': {}, 'api': {}, 'unrelated': {}}, 'journeys': [
        {'id': 'purchase', 'modules': ['frontend', 'api'], 'critical': True,
         'interface': 'browser', 'boundaries': ['ui', 'http', 'database'],
         'profile': 'isolated-prod-like', 'scenarios': [
             {'id': 'happy', 'criteria': ['saved', 'visible-after-reload']},
             {'id': 'invalid', 'criteria': ['rejected', 'no-partial-write']}]}]}


def evidence(scenario='happy', criteria=None, **changes):
    criteria = criteria or (['saved', 'visible-after-reload'] if scenario == 'happy'
                            else ['rejected', 'no-partial-write'])
    verification = {'level': 'e2e', 'journey': 'purchase', 'scenario': scenario,
                    'profile': 'isolated-prod-like', 'interface': 'browser',
                    'commit': 'a' * 40, 'source_state': 'clean', 'criteria': criteria,
                    'boundaries': ['ui', 'http', 'database'], 'simulated_boundaries': []}
    verification.update(changes)
    return {'id': 'proof-' + scenario, 'module': 'frontend', 'kind': 'test',
            'environment': 'local isolated browser server database',
            'status': 'current', 'result': 'passed', 'verification': verification}


class JourneySchemaTests(unittest.TestCase):
    def test_legacy_state_and_evidence_remain_readable(self):
        e2e.validate_journeys({'modules': {}}, require)
        e2e.validate_evidence({'module': 'frontend'}, state(), require)
        report = evidence()
        report.pop('verification')
        self.assertFalse(e2e.journey_coverage(state(), [report])['eligible'])

    def test_valid_journey_and_classified_evidence(self):
        current = state()
        e2e.validate_journeys(current, require)
        e2e.validate_evidence(evidence(), current, require)

    def test_bad_journey_definitions_rejected(self):
        mutations = [
            lambda j: j.update(modules=['missing']),
            lambda j: j.update(critical='yes'),
            lambda j: j.update(interface='unit'),
            lambda j: j.update(boundaries=[]),
            lambda j: j.update(profile=''),
            lambda j: j.update(scenarios=[]),
            lambda j: j['scenarios'][0].update(criteria=[]),
            lambda j: j['scenarios'].append(copy.deepcopy(j['scenarios'][0])),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                current = state()
                mutation(current['journeys'][0])
                with self.assertRaises(ValueError):
                    e2e.validate_journeys(current, require)

    def test_duplicate_journey_ids_rejected(self):
        current = state()
        current['journeys'].append(copy.deepcopy(current['journeys'][0]))
        with self.assertRaises(ValueError):
            e2e.validate_journeys(current, require)

    def test_bad_verification_metadata_rejected(self):
        for changes in ({'commit': 'not-a-commit'}, {'source_state': 'maybe'},
                        {'level': 'magic'}, {'journey': 'missing'},
                        {'scenario': 'missing'}, {'criteria': 'saved'},
                        {'simulated_boundaries': 'none'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                e2e.validate_evidence(evidence(**changes), state(), require)

    def test_sha256_commit_supported(self):
        e2e.validate_evidence(evidence(commit='b' * 64), state(), require)

    def test_evidence_identity_separates_scenario_profile_environment_and_level(self):
        first = evidence()
        variants = [evidence('invalid'), evidence(profile='other'), evidence(level='unit')]
        other_env = copy.deepcopy(first)
        other_env['environment'] = 'another isolated environment'
        variants.append(other_env)
        for other in variants:
            self.assertNotEqual(e2e.evidence_key(first), e2e.evidence_key(other))
        repeat = copy.deepcopy(first)
        repeat['id'] = 'new-run'
        self.assertEqual(e2e.evidence_key(first), e2e.evidence_key(repeat))


class JourneyCoverageTests(unittest.TestCase):
    def coverage(self, reports, current=None, module=None):
        return e2e.journey_coverage(current or state(), reports, module=module)

    def test_all_critical_scenarios_and_criteria_required(self):
        partial = self.coverage([evidence()])
        self.assertFalse(partial['eligible'])
        self.assertIn('invalid:no-partial-write', partial['journeys'][0]['missing'])
        self.assertTrue(self.coverage([evidence(), evidence('invalid')])['eligible'])

    def test_criterion_missing_is_not_hidden_by_passing_scenario(self):
        report = self.coverage([evidence(criteria=['saved']), evidence('invalid')])
        self.assertFalse(report['eligible'])
        self.assertIn('happy:visible-after-reload', report['journeys'][0]['missing'])

    def test_many_unit_tests_cannot_replace_e2e(self):
        units = [evidence(level='unit') for _ in range(1000)]
        self.assertFalse(self.coverage(units + [evidence('invalid')])['eligible'])

    def test_integration_and_simulated_levels_do_not_complete_journey(self):
        for level in ('integration', 'simulated'):
            with self.subTest(level=level):
                self.assertFalse(self.coverage([evidence(level=level), evidence('invalid')])['eligible'])

    def test_api_only_evidence_does_not_prove_browser_flow(self):
        self.assertFalse(self.coverage([evidence(interface='api'), evidence('invalid')])['eligible'])

    def test_missing_or_simulated_boundary_blocks_completion(self):
        for changes in ({'boundaries': ['ui', 'http']}, {'simulated_boundaries': ['database']}):
            with self.subTest(changes=changes):
                self.assertFalse(self.coverage([evidence(**changes), evidence('invalid')])['eligible'])

    def test_other_environment_profile_cannot_satisfy_required_profile(self):
        self.assertFalse(self.coverage([evidence(profile='unit-memory'), evidence('invalid')])['eligible'])

    def test_stale_failed_superseded_or_blocked_are_not_proof(self):
        for key, value in [('status', 'stale'), ('status', 'invalid'), ('status', 'superseded'),
                           ('result', 'failed'), ('result', 'blocked')]:
            with self.subTest(key=key, value=value):
                item = evidence()
                item[key] = value
                self.assertFalse(self.coverage([item, evidence('invalid')])['eligible'])

    def test_legacy_operational_report_does_not_imply_e2e(self):
        item = evidence()
        item.pop('verification')
        item['kind'] = 'operational'
        self.assertFalse(self.coverage([item])['eligible'])

    def test_no_declared_critical_journey_means_pending_not_vacuous_success(self):
        current = state()
        current['journeys'] = []
        self.assertFalse(self.coverage([], current)['eligible'])

    def test_all_critical_journeys_required_not_only_first(self):
        current = state()
        second = copy.deepcopy(current['journeys'][0])
        second['id'] = 'refund'
        current['journeys'].append(second)
        self.assertFalse(self.coverage([evidence(), evidence('invalid')], current)['eligible'])

    def test_module_scope_includes_cross_component_journey(self):
        self.assertTrue(self.coverage([evidence(), evidence('invalid')], module='api')['eligible'])
        self.assertFalse(self.coverage([], module='api')['eligible'])


class EvidenceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        fixtures = Path(__file__).resolve().parent / 'fixtures'
        shutil.copytree(fixtures / 'project', self.root)
        (self.root / '.pvc').mkdir()
        self.state = json.loads((fixtures / 'state.json').read_text())
        journey = copy.deepcopy(state()['journeys'][0])
        journey['modules'] = ['save', 'independent']
        self.state['journeys'] = [journey]
        self.persist()

    def persist(self):
        (self.root / '.pvc/state.json').write_text(json.dumps(self.state))

    def record(self, scenario='happy', level='e2e', kind='test', environment=None):
        item = evidence(scenario, level=level)
        metadata = item['verification']
        snapshot = e2e.evidence_fingerprint(self.state, pvc.fingerprints(self.root, self.state),
                                            {'module': 'save', 'verification': metadata})
        result = pvc.capture(self.root, 'save', 'evidence.txt', kind, 'passed',
                             environment or item['environment'], 'Actual isolated fixture procedure',
                             self.state['version'], snapshot, metadata)
        self.state = pvc.read_json(self.root / '.pvc/state.json')
        return result

    def test_scenarios_remain_current_together_and_repeat_supersedes_only_itself(self):
        happy = self.record()
        invalid = self.record('invalid')
        report = pvc.inspect(self.root, self.state)
        self.assertTrue(report['journey_coverage']['eligible'])
        self.assertEqual({r['status'] for r in report['evidence']}, {'current'})
        newer = self.record()
        current = {r['id']: r['status'] for r in pvc.inspect(self.root, self.state)['evidence']}
        self.assertEqual(current[happy['id']], 'superseded')
        self.assertEqual(current[invalid['id']], 'current')
        self.assertEqual(current[newer['id']], 'current')

    def test_change_to_other_journey_module_invalidates_frontend_evidence(self):
        self.record()
        self.record('invalid')
        before = pvc.fingerprints(self.root, self.state)['save']
        (self.root / 'unrelated.md').write_text('Changed API behavior in declared journey module')
        self.assertEqual(before, pvc.fingerprints(self.root, self.state)['save'])
        report = pvc.inspect(self.root, self.state)
        self.assertEqual({r['status'] for r in report['evidence']}, {'stale'})
        self.assertFalse(report['journey_coverage']['eligible'])

    def test_changed_criteria_invalidate_old_journey_proof(self):
        self.record()
        self.state['journeys'][0]['scenarios'][0]['criteria'].append('new-observable-criterion')
        self.persist()
        report = pvc.inspect(self.root, self.state)
        self.assertEqual(report['evidence'][0]['status'], 'stale')
        self.assertFalse(report['journey_coverage']['eligible'])

    def test_snapshot_cli_returns_combined_journey_fingerprint(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/pvc.py'
        proc = subprocess.run([sys.executable, str(script), 'snapshot', '--project', str(self.root),
                               '--module', 'save', '--journey', 'purchase'], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        snapshot = json.loads(proc.stdout)
        expected = e2e.evidence_fingerprint(self.state, pvc.fingerprints(self.root, self.state),
                                            {'module': 'save', 'verification': {'journey': 'purchase'}})
        self.assertEqual(snapshot['fingerprint'], expected)

    def test_e2e_record_rejects_plain_module_snapshot_without_mutation(self):
        before = (self.root / '.pvc/state.json').read_bytes()
        with self.assertRaises(pvc.Invalid):
            pvc.capture(self.root, 'save', 'evidence.txt', 'test', 'passed', 'fixture',
                        'fixture procedure', self.state['version'],
                        pvc.fingerprints(self.root, self.state)['save'], evidence()['verification'])
        self.assertEqual(before, (self.root / '.pvc/state.json').read_bytes())

    def test_public_capture_cannot_mix_environments_for_gate(self):
        happy = self.record(kind='operational', environment='env-A-config-1')
        invalid = self.record('invalid', environment='env-B-config-2')
        decision = {'id': 'D-ENV', 'module': 'save', 'gate': 'G8', 'decision': 'GO',
                    'reason': 'Review', 'reviewer': 'fixture', 'version': self.state['version'],
                    'fingerprint': pvc.fingerprints(self.root, self.state)['save'],
                    'evidence_ids': [happy['id'], invalid['id']]}
        self.state['decisions'].append(decision)
        report = pvc.inspect(self.root, self.state)
        self.assertFalse(report['journey_coverage']['eligible'])
        self.assertFalse(report['structurally_valid'])
        self.assertEqual({e['environment'] for e in report['evidence']}, {'env-A-config-1', 'env-B-config-2'})
        self.state['decisions'] = []
        self.persist()
        invalid_a = self.record('invalid', environment='env-A-config-1')
        decision['evidence_ids'].append(invalid_a['id'])
        self.state['decisions'].append(decision)
        report = pvc.inspect(self.root, self.state)
        self.assertTrue(report['structurally_valid'], report['errors'])
        self.assertTrue(report['journey_coverage']['eligible'])
        self.assertEqual(report['journey_coverage']['journeys'][0]['environment'], 'env-A-config-1')

    def test_gate_needs_all_critical_scenarios_not_operational_label_alone(self):
        happy = self.record(kind='operational')
        decision = {'id': 'D-E2E', 'module': 'save', 'gate': 'G8', 'decision': 'GO',
                    'reason': 'Scenario review', 'reviewer': 'fixture reviewer',
                    'version': self.state['version'],
                    'fingerprint': pvc.fingerprints(self.root, self.state)['save'],
                    'evidence_ids': [happy['id']]}
        self.state['decisions'].append(decision)
        report = pvc.inspect(self.root, self.state)
        self.assertFalse(report['structurally_valid'])
        self.state['decisions'] = []
        self.persist()
        invalid = self.record('invalid')
        decision['evidence_ids'].append(invalid['id'])
        self.state['decisions'].append(decision)
        report = pvc.inspect(self.root, self.state)
        self.assertTrue(report['structurally_valid'], report['errors'])
        self.assertEqual(report['operational_approval'], 'requires_explicit_review')


if __name__ == '__main__':
    unittest.main()
