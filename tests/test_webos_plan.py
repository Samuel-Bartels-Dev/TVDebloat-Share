import copy
import json
from pathlib import Path
import tempfile
import unittest

from test_webos import FakeTV
from tvdebloat import webos, webos_profile, webos_plan


class MovingTV(FakeTV):
    move_verified = True

    def move_launch_point(self, point, position):
        self.order.remove(point)
        self.order.insert(position, point)


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tv = MovingTV()
        source = self.root / 'discovery.json'
        source.write_text(json.dumps(webos.discover(self.tv)), encoding='utf-8')
        self.profile = webos_profile.initialize(source, 'lg', 'SyntheticPanel', 'Test', self.root / 'profiles')

    def reorder(self):
        text = self.profile.read_text(encoding='utf-8')
        self.profile.write_text(text.replace('order = []', 'order = ["browser_bookmark", "netflix_default", "hdmi_one"]'), encoding='utf-8')
        return webos_plan.preview(self.tv, self.profile)

    def test_candidate_has_empty_actions_and_all_apps_review(self):
        profile = webos_profile.load(self.profile)
        self.assertEqual(profile['apps']['hide'], [])
        self.assertEqual(len(profile['apps']['review']), 3)
        self.assertEqual(profile['status'], 'candidate')
        with self.assertRaises(FileExistsError):
            webos_profile.initialize(self.root / 'discovery.json', 'lg', 'SyntheticPanel', 'Test', self.root / 'profiles')

    def test_exact_preview_describes_moves_and_inverse_without_writing(self):
        plan = self.reorder()
        self.assertEqual(self.tv.order, plan['before_order'])
        self.assertEqual(plan['actions'], [{'type': 'move_launch_point', 'id': 'browser_bookmark', 'position': 0}])
        self.assertTrue(plan['ready'])
        self.assertEqual(plan['after_order'][0], 'browser_bookmark')
        self.assertNotIn('PRIVATE', json.dumps(plan))

    def test_native_unverified_contract_blocks_apply_and_marks_preview(self):
        self.reorder()
        plan = webos_plan.preview(FakeTV(), self.profile)
        self.assertFalse(plan['ready'])
        self.assertTrue(plan['blocked'])
        with self.assertRaises(ValueError):
            webos_plan.apply(FakeTV(), self.profile, plan, plan['digest'], self.root / 'state', pilot=True)

    def test_apply_needs_exact_approval_and_pilot(self):
        plan = self.reorder()
        for digest, pilot in (('', True), ('wrong', True), (plan['digest'], False)):
            with self.assertRaises(ValueError):
                webos_plan.apply(self.tv, self.profile, plan, digest, self.root / 'state', pilot=pilot)
        self.assertEqual(self.tv.order, plan['before_order'])

    def test_apply_readback_and_explicit_restore_preview(self):
        plan = self.reorder()
        result = webos_plan.apply(self.tv, self.profile, plan, plan['digest'], self.root / 'state', pilot=True)
        journal = json.loads(Path(result['journal']).read_text(encoding='utf-8'))
        self.assertEqual(journal['status'], 'complete')
        self.assertEqual(self.tv.order, plan['after_order'])
        recovery = webos_plan.restore_preview(self.tv, result['journal'])
        self.assertEqual(recovery['after_order'], plan['before_order'])
        self.assertEqual(self.tv.order, plan['after_order'])
        restored = webos_plan.restore(self.tv, result['journal'], recovery['digest'], self.root / 'restore')
        self.assertEqual(self.tv.order, plan['before_order'])
        self.assertTrue(Path(restored['journal']).exists())

    def test_stale_layout_identity_and_profile_or_plan_tampering_refused(self):
        plan = self.reorder()
        bad = copy.deepcopy(plan)
        bad['actions'][0]['id'] = 'netflix_default'
        with self.assertRaises(ValueError):
            webos_plan.apply(self.tv, self.profile, bad, plan['digest'], self.root / 'state', pilot=True)
        self.tv.order.reverse()
        with self.assertRaises(ValueError):
            webos_plan.apply(self.tv, self.profile, plan, plan['digest'], self.root / 'state', pilot=True)
        self.tv.order = plan['before_order'][:]
        self.profile.write_text(self.profile.read_text(encoding='utf-8') + '\n# edited\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            webos_plan.apply(self.tv, self.profile, plan, plan['digest'], self.root / 'state', pilot=True)

    def test_pending_journal_survives_uncertain_failure_and_prevents_restore(self):
        plan = self.reorder()
        def fail(point, position):
            # The TV may have applied a write before the connection was lost.
            self.tv.order.remove(point)
            self.tv.order.insert(position, point)
            raise webos.WebOSError('connection lost')
        self.tv.move_launch_point = fail
        with self.assertRaisesRegex(ValueError, 'uncertain'):
            webos_plan.apply(self.tv, self.profile, plan, plan['digest'], self.root / 'state', pilot=True)
        journal = list((self.root / 'state').glob('*.json'))[0]
        data = json.loads(journal.read_text(encoding='utf-8'))
        self.assertEqual(data['status'], 'uncertain')
        self.assertEqual(data['pending'], plan['actions'][0])
        with self.assertRaises(ValueError):
            webos_plan.restore_preview(self.tv, journal)

    def test_journal_exists_before_each_write(self):
        plan = self.reorder()
        original = self.tv.move_launch_point
        def move(point, position):
            files = list((self.root / 'state').glob('*.json'))
            self.assertEqual(len(files), 1)
            journal = json.loads(files[0].read_text(encoding='utf-8'))
            self.assertEqual(journal['pending']['id'], point)
            original(point, position)
        self.tv.move_launch_point = move
        webos_plan.apply(self.tv, self.profile, plan, plan['digest'], self.root / 'state', pilot=True)

    def test_invalid_permutation_and_unsafe_ids_rejected(self):
        for order in ('["netflix_default"]', '["netflix_default", "netflix_default", "hdmi_one"]', '["x;reboot"]'):
            text = self.profile.read_text(encoding='utf-8')
            self.profile.write_text(text.replace('order = []', 'order = ' + order), encoding='utf-8')
            with self.assertRaises(ValueError):
                webos_plan.preview(self.tv, self.profile)
            self.profile.write_text(text, encoding='utf-8')

    def test_hide_and_disable_are_blocked_and_protected_apps_rejected(self):
        text = self.profile.read_text(encoding='utf-8')
        self.profile.write_text(text.replace('hide = []', 'hide = ["netflix"]'), encoding='utf-8')
        self.assertFalse(webos_plan.preview(self.tv, self.profile)['ready'])
        self.profile.write_text(text.replace('hide = []', 'hide = ["com.webos.app.hdmi1"]'), encoding='utf-8')
        with self.assertRaises(ValueError):
            webos_plan.preview(self.tv, self.profile)

    def test_wrong_identity_schema_and_platform_rejected(self):
        text = self.profile.read_text(encoding='utf-8')
        for old, new in [('platform = "webos"', 'platform = "android"'),
                         ('schema_version = 1', 'schema_version = 2'),
                         ('SyntheticPanel', 'OtherPanel')]:
            self.profile.write_text(text.replace(old, new), encoding='utf-8')
            with self.assertRaises(ValueError):
                webos_plan.preview(self.tv, self.profile)

    def test_device_replacement_and_concurrent_changes_prevent_recovery(self):
        plan = self.reorder()
        result = webos_plan.apply(self.tv, self.profile, plan, plan['digest'], self.root / 'state', pilot=True)
        self.tv.responses[webos.SYSTEM]['modelName'] = 'ReplacementPanel'
        with self.assertRaises(ValueError):
            webos_plan.restore_preview(self.tv, result['journal'])
        self.tv.responses[webos.SYSTEM]['modelName'] = 'SyntheticPanel'
        self.tv.order.reverse()
        with self.assertRaises(ValueError):
            webos_plan.restore_preview(self.tv, result['journal'])

    def test_success_without_matching_readback_is_uncertain(self):
        plan = self.reorder()
        self.tv.move_launch_point = lambda point, position: None
        with self.assertRaisesRegex(ValueError, 'uncertain'):
            webos_plan.apply(self.tv, self.profile, plan, plan['digest'], self.root / 'state', pilot=True)
        journal = json.loads(next((self.root / 'state').glob('*.json')).read_text(encoding='utf-8'))
        self.assertEqual(journal['status'], 'uncertain')

    def test_unknown_profile_fields_cannot_grant_capabilities(self):
        self.profile.write_text(self.profile.read_text(encoding='utf-8') + '\n[capabilities]\nmove_launch_point=true\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            webos_plan.preview(self.tv, self.profile)

    def test_verified_partial_prefix_can_be_previewed_and_restored(self):
        text = self.profile.read_text(encoding='utf-8')
        self.profile.write_text(text.replace('order = []', 'order = ["browser_bookmark", "hdmi_one", "netflix_default"]'), encoding='utf-8')
        plan = webos_plan.preview(self.tv, self.profile)
        result = webos_plan.apply(self.tv, self.profile, plan, plan['digest'], self.root / 'state', pilot=True)
        journal_path = Path(result['journal'])
        journal = json.loads(journal_path.read_text(encoding='utf-8'))
        self.assertEqual(len(journal['completed']), 2)
        journal['completed'] = journal['completed'][:1]
        journal['status'] = 'applying'
        partial = plan['before_order'][:]
        move = journal['completed'][0]
        partial.remove(move['id'])
        partial.insert(move['position'], move['id'])
        journal['current_order'] = partial
        journal_path.write_text(json.dumps(journal), encoding='utf-8')
        self.tv.order = partial[:]
        recovery = webos_plan.restore_preview(self.tv, journal_path)
        self.assertEqual(recovery['before_order'], partial)
        self.assertEqual(recovery['after_order'], plan['before_order'])
        webos_plan.restore(self.tv, journal_path, recovery['digest'], self.root / 'restore')
        self.assertEqual(self.tv.order, plan['before_order'])


if __name__ == '__main__':
    unittest.main()
