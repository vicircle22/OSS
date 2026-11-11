import unittest

from scripts.ci.cache_report import compare, job_durations
from scripts.ci.changed_paths import classify


class ChangeTests(unittest.TestCase):
    def test_documentation_only_skips_but_manual_forces(self):
        paths = ['README.md', 'docs/Week8-Performance.md', 'docs/wiki/Getting-Started.md']
        self.assertFalse(classify(paths)['deploy_required'])
        self.assertTrue(classify(paths, manual=True)['ci_required'])

    def test_runtime_workflow_and_unknown_files_run_conservatively(self):
        for path in ('scripts/dora/collect.py', 'docs/wireframes/index.html',
                     '.github/actions/python-environment/action.yml', 'new-code/app.xyz'):
            with self.subTest(path=path):
                self.assertTrue(classify(['README.md', path])['deploy_required'])


class MeasurementTests(unittest.TestCase):
    def rows(self):
        base = {'revision': 'a' * 40, 'runner_os': 'Linux', 'python_version': '3.12.12',
                'requirements_sha256': 'hash', 'run_id': '1'}
        return [dict(base, label=phase, dependency_seconds=seconds, cache_hit=hit)
                for phase, seconds, hit in [('baseline', 10, 'false'), ('cold', 12, 'false'), ('warm', 2, 'true')]]

    def test_measured_rate_and_slowdown_are_not_hidden(self):
        rows = self.rows()
        self.assertEqual(compare(rows)['improvement_percent'], 80)
        rows[2]['dependency_seconds'] = 15
        self.assertEqual(compare(rows)['improvement_percent'], -50)

    def test_mismatched_conditions_and_missing_cache_hit_are_rejected(self):
        rows = self.rows()
        rows[2]['revision'] = 'b' * 40
        with self.assertRaises(ValueError):
            compare(rows)
        rows = self.rows()
        rows[2]['cache_hit'] = 'false'
        with self.assertRaises(ValueError):
            compare(rows)

    def test_job_time_uses_actual_api_timestamps(self):
        jobs = [{'name': 'baseline / Check baseline', 'started_at': '2026-11-11T00:00:00Z',
                 'completed_at': '2026-11-11T00:00:30Z'}]
        self.assertEqual(job_durations(jobs), {'baseline': 30})
