import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts.dora.collect import GitHub, build, calculate, lead_samples, sources, time, write


class DoraTests(unittest.TestCase):
    def setUp(self):
        self.start = time('2026-10-05T00:00:00Z')
        self.end = time('2026-10-12T00:00:00Z')
        self.deployments = [
            {'id': 1, 'sha': 'a', 'deployed_at': '2026-10-04T00:00:00Z'},
            {'id': 2, 'sha': 'b', 'deployed_at': '2026-10-05T00:00:00Z'},
            {'id': 3, 'sha': 'c', 'deployed_at': '2026-10-10T00:00:00Z'},
            {'id': 4, 'sha': 'd', 'deployed_at': '2026-10-12T00:00:00Z'},
        ]

    def incident(self, number=1, dep=2, opened='2026-10-05T01:00:00Z', closed='2026-10-05T03:00:00Z'):
        return {'number': number, 'deployment_id': dep, 'opened_at': opened, 'closed_at': closed, 'url': 'https://github.com/vicircle22/OSS/issues/1'}

    def test_no_data_is_null_not_fake_zero(self):
        m = calculate([], [], [], self.start, self.end)
        for k in ('lead_time_seconds', 'deployment_frequency_per_day', 'mttr_seconds', 'change_failure_rate_percent'):
            self.assertIsNone(m[k])
        self.assertEqual(m['deployment_count'], 0)

    def test_four_metrics_and_distinct_failed_deployments(self):
        incidents = [self.incident(), self.incident(2), self.incident(3, dep=3, opened='2026-10-10T01:00:00Z', closed=None)]
        samples = [{'deployed_at': '2026-10-05T00:00:00Z', 'seconds': 3600}, {'deployed_at': '2026-10-10T00:00:00Z', 'seconds': 10800}]
        m = calculate(self.deployments, incidents, samples, self.start, self.end)
        self.assertEqual(m['lead_time_seconds'], 7200)
        self.assertAlmostEqual(m['deployment_frequency_per_day'], 2/7)
        self.assertEqual(m['change_failure_rate_percent'], 100)
        self.assertEqual(m['mttr_seconds'], 7200)
        self.assertEqual(m['open_incident_count'], 1)

    def test_no_incident_mttr_null_cfr_zero_when_deployments_exist(self):
        m = calculate(self.deployments, [], [], self.start, self.end)
        self.assertIsNone(m['mttr_seconds'])
        self.assertEqual(m['change_failure_rate_percent'], 0)

    def test_recovery_before_window_open_and_unknown_links(self):
        incidents = [self.incident(dep=1, opened='2026-10-04T12:00:00Z', closed='2026-10-05T12:00:00Z'), self.incident(2, dep=999)]
        m = calculate(self.deployments, incidents, [], self.start, self.end)
        self.assertEqual(m['mttr_seconds'], 86400)
        self.assertEqual(m['failed_deployment_count'], 0)

    def test_utc_boundaries_and_bad_timestamps(self):
        bad = self.incident(closed='2026-10-05T00:30:00Z')
        m = calculate(self.deployments, [bad], [], self.start, self.end)
        self.assertEqual(m['deployment_count'], 2) # start included, end excluded
        self.assertIsNone(m['mttr_seconds'])
        self.assertEqual(time('2026-10-05T09:00:00+09:00'), self.start)

    def test_paginated_api_and_exclusion_of_pull_requests(self):
        class Fake(GitHub):
            def get(self, path, params=None):
                if path == '/deployments':
                    return [{'id': 1, 'sha': 'a', 'transient_environment': False}, {'id': 2, 'sha': 'b', 'transient_environment': True}]
                if '/statuses' in path:
                    return [{'state': 'inactive', 'created_at': '2026-10-06T00:00:00Z'}, {'state': 'success', 'created_at': '2026-10-05T00:00:00Z'}]
                if path == '/issues':
                    return [{'number': 7, 'body': 'missing id'}, {'pull_request': {}, 'body': 'deployment_id: 1'}]
                return list(range(100)) if params['page'] == 1 else [100]
        api = Fake('vicircle22/OSS')
        self.assertEqual(len(api.pages('/test')), 101)
        deps, incidents, warnings = sources(api, 'production')
        self.assertEqual(len(deps), 1)
        self.assertEqual(deps[0]['deployed_at'], '2026-10-05T00:00:00Z')
        self.assertFalse(incidents)
        self.assertTrue(warnings)

    def test_compare_commit_first_delivery_and_rollback(self):
        class Fake:
            def get(self, path, params):
                return {'status': 'behind' if path.endswith('b...a') else 'ahead'}
            def pages(self, path, key=None):
                return [{'sha': 'new', 'commit': {'committer': {'date': '2026-10-04T23:00:00Z'}}}]
        deps = self.deployments[:2] + [{'id': 3, 'sha': 'a', 'deployed_at': '2026-10-06T00:00:00Z'}, {'id': 4, 'sha': 'b', 'deployed_at': '2026-10-07T00:00:00Z'}]
        samples, warnings = lead_samples(Fake(), deps)
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0]['seconds'], 3600)
        self.assertTrue(warnings)

    def test_outputs_are_valid_and_example_is_marked(self):
        data = build('vicircle22/OSS', 'production', [], [], [], [], self.end, mode='example')
        with tempfile.TemporaryDirectory() as directory:
            write(data, Path(directory))
            self.assertEqual(json.loads((Path(directory)/'metrics.json').read_text())['data_mode'], 'example')
            ET.fromstring((Path(directory)/'dashboard.svg').read_text())
            self.assertIn('예시 데이터', (Path(directory)/'index.html').read_text())
            self.assertIn('데이터 없음', (Path(directory)/'report.md').read_text())

    def test_rollback_to_before_initial_baseline_does_not_recount_ancestors(self):
        class Fake:
            def get(self, path, params):
                return {'status': 'behind' if path.endswith('baseline...old') else 'ahead'}
            def pages(self, path, key=None):
                return [{'sha': 'ancestor', 'commit': {'committer': {'date': '2026-10-01T00:00:00Z'}}},
                        {'sha': 'baseline', 'commit': {'committer': {'date': '2026-10-02T00:00:00Z'}}}]
        deps = [{'id': 1, 'sha': 'baseline', 'deployed_at': '2026-10-03T00:00:00Z'},
                {'id': 2, 'sha': 'old', 'deployed_at': '2026-10-04T00:00:00Z'},
                {'id': 3, 'sha': 'baseline', 'deployed_at': '2026-10-05T00:00:00Z'}]
        samples, _ = lead_samples(Fake(), deps)
        self.assertEqual(samples, [])


if __name__ == '__main__':
    unittest.main()
