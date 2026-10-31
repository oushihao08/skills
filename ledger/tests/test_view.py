"""Isolated ledger behavior tests; no models, services, credentials or business writes."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('ledger', Path(__file__).resolve().parents[1] / 'scripts/view.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class LedgerTests(unittest.TestCase):
    def test_required_fields_and_times(self):
        self.item('a', {'work': 'planned'})
        original = copy.deepcopy(self.task)
        for field, bad in [('updated_at', None), ('updated_at', '2026-10-31T12:00:00'), ('updated_at', 'bad'), ('completion_criteria', '逐字错误'), ('completion_criteria', [' ']), ('goal_ref', None), ('scope', {}), ('next_actions', '错误'), ('items', None)]:
            with self.subTest(field=field, bad=bad):
                self.task = copy.deepcopy(original)
                self.task[field] = bad
                with self.assertRaises(ValueError):
                    self.write()
        self.task = original
        self.task['items'][0]['stages'][0]['observed_at'] = '2026-10-31'
        with self.assertRaisesRegex(ValueError, 'observed_at'):
            self.write()

    def test_empty_success_proofs_and_valid_alternatives(self):
        item = self.item('a', {'work': 'succeeded'})
        stage = item['stages'][0]
        for bad in [[''], [' '], [{}], [None]]:
            stage['evidence'] = bad
            with self.assertRaisesRegex(ValueError, '证据'):
                self.write()
        stage['evidence'] = []
        path = self.root / 'attempts/a_work.json'
        attempt = json.loads(path.read_text())
        for field, value, valid in [('artifacts', [{}], False), ('verification', [{}], False), ('verification', [{'kind': 'check', 'result': 'checked'}], False), ('artifacts', [{'ref': 'result.txt'}], True), ('verification', [{'kind': 'readback', 'result': 'matched', 'evidence': 'receipt'}], True)]:
            record = dict(attempt, **{field: value})
            self.put('attempts/a_work.json', record)
            if valid:
                self.write()
            else:
                with self.assertRaisesRegex(ValueError, '证据'):
                    self.write()

    def test_all_observation_states_in_history(self):
        self.item('a', {'work': 'planned'})
        for status in ['open', 'resolved', 'candidate', 'validated', 'rejected']:
            self.put('observations/' + status + '.json', {'id': status, 'kind': 'issue' if status in {'open', 'resolved'} else 'lesson', 'status': status, 'title': '记录-' + status})
        self.write()
        view = (self.root / '对账台.md').read_text()
        front, history = view.split('<details>', 1)
        self.assertIn('记录-open', front)
        for status in ['open', 'resolved', 'candidate', 'validated', 'rejected']:
            self.assertIn('observations/' + status + '.json', history)
            if status != 'open':
                self.assertNotIn('记录-' + status, front)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.task = {'schema_version': 1, 'id': 'demo', 'title': '批次对账', 'goal_ref': 'test', 'scope': 'isolated',
                     'completion_criteria': ['有凭证且验收通过'], 'next_actions': ['核对原回执'], 'updated_at': '2026-10-31T22:00:00+08:00', 'items': []}

    def item(self, key, states, accepted=False, group=''):
        item = {'id': key, 'title': key, 'group': group, 'stages': []}
        for sid, status in states.items():
            aid = key + '_' + sid
            stage = {'id': sid, 'title': sid, 'state': status, 'attempt_id': None, 'evidence': ['evidence/id'], 'observed_at': '2026-10-31T22:00:00+08:00'}
            if status in {'running', 'queued', 'succeeded', 'failed', 'unknown'}:
                stage['attempt_id'] = aid
                self.put('attempts/' + aid + '.json', {'id': aid, 'item_id': key, 'stage_id': sid, 'status': status, 'external_ids': {'request_id': 'external-' + aid}})
            item['stages'].append(stage)
        if accepted:
            item['acceptance'] = {'state': 'accepted', 'evidence': ['review/receipt']}
        self.task['items'].append(item)
        return item

    def put(self, name, value):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value, ensure_ascii=False))

    def write(self):
        self.put('task.json', self.task)
        return v.write_view(self.root)

    def test_twenty_pipeline_items_mutually_exclusive_counts(self):
        for i in range(20):
            status = ['succeeded', 'failed', 'running', 'unknown'][i % 4]
            self.item('q' + str(i), {'author': 'succeeded', 'answer': status}, accepted=status == 'succeeded')
        task, attempts, obs = self.write()
        counts = v.collections.Counter(v.state(i) for i in task['items'])
        self.assertEqual(dict(counts), {'done': 5, 'failed': 5, 'running': 5, 'unknown': 5})
        self.assertEqual(sum(counts.values()), 20)
        self.assertEqual(len(attempts), 40)
        self.assertIn('共 20 项', (self.root / '对账台.md').read_text())

    def test_success_requires_acceptance(self):
        i = self.item('a', {'work': 'succeeded'})
        self.write()
        self.assertEqual(v.state(i), 'review')

    def test_acceptance_without_evidence_rejected(self):
        i = self.item('a', {'work': 'succeeded'}, True)
        i['acceptance']['evidence'] = []
        with self.assertRaisesRegex(ValueError, '证据'):
            self.write()

    def test_acceptance_before_execution_rejected(self):
        self.item('a', {'work': 'running'}, True)
        with self.assertRaisesRegex(ValueError, '未执行成功'):
            self.write()

    def test_retry_preserves_failure_and_external_id(self):
        i = self.item('a', {'work': 'failed'})
        self.put('attempts/retry.json', {'id': 'retry', 'item_id': 'a', 'stage_id': 'work', 'previous_attempt_id': 'a_work', 'status': 'succeeded', 'external_ids': {'record_id': 'remote-record'}})
        i['stages'][0].update(state='succeeded', attempt_id='retry')
        self.write()
        task, attempts, _ = v.load(self.root)
        self.assertEqual(attempts['a_work']['status'], 'failed')
        self.assertEqual(attempts['retry']['previous_attempt_id'], 'a_work')
        self.assertIn('remote-record', (self.root / '对账台.md').read_text())

    def test_failed_validation_preserves_prior_view(self):
        self.item('a', {'work': 'planned'})
        self.write()
        before = (self.root / '对账台.md').read_bytes()
        self.task['items'][0]['stages'][0]['state'] = 'unknown'
        with self.assertRaises(ValueError):
            self.write()
        self.assertEqual(before, (self.root / '对账台.md').read_bytes())

    def test_unknown_cannot_have_finished_time(self):
        self.item('a', {'work': 'unknown'})
        p = self.root / 'attempts/a_work.json'
        a = json.loads(p.read_text())
        a['finished_at'] = '2026-10-31T22:00:00+08:00'
        self.put('attempts/a_work.json', a)
        with self.assertRaisesRegex(ValueError, '未知'):
            self.write()

    def test_heterogeneous_grouped_and_custom_fields(self):
        self.task['presentation'] = {'mode': 'grouped', 'columns': ['评分'], 'stage_order': ['ship']}
        a = self.item('a', {'draft': 'planned'}, group='写作')
        a['details'] = {'评分': 0}
        self.item('b', {'ship': 'blocked'}, group='交付')
        self.write()
        view = (self.root / '对账台.md').read_text()
        self.assertIn('### 写作', view)
        self.assertIn('### 交付', view)
        self.assertIn('| 0 |', view)
        self.assertIn('draft', view)
        self.assertIn('ship', view)

    def test_optional_skip_not_counted_done(self):
        a = self.item('a', {'work': 'skipped'})
        self.write()
        self.assertEqual(v.state(a), 'skipped')

    def test_cycle_and_cross_item_retries_rejected(self):
        self.item('a', {'work': 'failed'})
        self.item('b', {'work': 'failed'})
        a = json.loads((self.root / 'attempts/a_work.json').read_text())
        a['previous_attempt_id'] = 'b_work'
        self.put('attempts/a_work.json', a)
        with self.assertRaisesRegex(ValueError, '跨item'):
            self.write()

    def test_success_without_proof_rejected(self):
        i = self.item('a', {'work': 'succeeded'})
        i['stages'][0]['evidence'] = []
        with self.assertRaisesRegex(ValueError, '执行成功缺少证据'):
            self.write()

    def test_render_does_not_change_json(self):
        self.item('a', {'work': 'planned'})
        self.put('task.json', self.task)
        before = (self.root / 'task.json').read_bytes()
        v.write_view(self.root)
        self.assertEqual(before, (self.root / 'task.json').read_bytes())

    def test_escape_table_content_and_symlink_protection(self):
        i = self.item('a', {'work': 'planned'})
        i['title'] = '<script>|\n恶意'
        self.write()
        view = (self.root / '对账台.md').read_text()
        self.assertNotIn('<script>', view)
        self.assertIn('&#124;', view)
        dest = self.root / '对账台.md'
        dest.unlink()
        outside = self.root / 'preserve.txt'
        outside.write_text('keep')
        dest.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, '符号链接'):
            self.write()
        self.assertEqual(outside.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
