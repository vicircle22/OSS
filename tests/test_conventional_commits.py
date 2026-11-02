import contextlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.collaboration.check_commits import main, new_commits, valid_subject


class SubjectTests(unittest.TestCase):
    def test_valid_subjects(self):
        for subject in ('feat: 검색 추가', 'fix(api): reject empty input',
                        'feat(api)!: change response', 'docs: add review guide',
                        'ci: validate pull requests', 'refactor(dora): simplify parsing'):
            with self.subTest(subject=subject):
                self.assertTrue(valid_subject(subject))

    def test_invalid_subjects(self):
        for subject in ('Update README', 'feat:add search', 'feat: ',
                        'feat(): empty scope', 'unknown: add search',
                        'feat: first\nsecond', 'feat: \t', 'Feat: uppercase type'):
            with self.subTest(subject=subject):
                self.assertFalse(valid_subject(subject))


class RevisionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.previous = Path.cwd()
        os.chdir(self.directory.name)
        self.addCleanup(os.chdir, self.previous)
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('commit', '-q', '--allow-empty', '-m', 'Old history without convention')
        self.base = self.git('rev-parse', 'HEAD')

    def git(self, *args):
        return subprocess.run(['git', *args], check=True, capture_output=True,
                              text=True).stdout.strip()

    def check(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(['--base', self.base, *args])

    def test_old_history_is_excluded(self):
        self.git('commit', '-q', '--allow-empty', '-m', 'feat: add search')
        self.assertEqual(self.check('--title', 'feat: add search'), 0)
        self.assertEqual(len(new_commits(self.base, 'HEAD')), 1)

    def test_all_new_commits_are_checked(self):
        self.git('commit', '-q', '--allow-empty', '-m', 'Bad message')
        self.git('commit', '-q', '--allow-empty', '-m', 'fix: correct a bug')
        self.assertEqual(self.check(), 1)

    def test_invalid_pr_title_fails(self):
        self.git('commit', '-q', '--allow-empty', '-m', 'docs: add guide')
        self.assertEqual(self.check('--title', 'Update'), 1)

    def test_empty_range_and_missing_ref_fail(self):
        self.assertEqual(self.check(), 1)
        self.assertEqual(self.check('--head', 'missing-ref'), 2)

    def test_generated_merge_subject_is_excluded(self):
        self.git('switch', '-q', '-c', 'feature/test')
        self.git('commit', '-q', '--allow-empty', '-m', 'test: add coverage')
        self.git('switch', '-q', 'main')
        self.git('merge', '-q', '--no-ff', 'feature/test', '-m', 'Merge branch feature/test')
        self.assertEqual(self.check('--title', 'test: add coverage'), 0)
        self.assertEqual(len(new_commits(self.base, 'HEAD')), 1)


if __name__ == '__main__':
    unittest.main()
