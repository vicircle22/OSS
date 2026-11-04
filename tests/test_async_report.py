import unittest

from scripts.collaboration.async_report import render, summarize
from scripts.dora.collect import time


class AsyncReportTests(unittest.TestCase):
    def setUp(self):
        self.now = time('2026-11-04T00:00:00Z')
        self.issue = {'number': 1, 'title': 'Question', 'state': 'open',
                      'created_at': '2026-11-01T00:00:00Z', 'closed_at': None,
                      'user': {'login': 'author'}, 'html_url': 'https://github.com/vicircle22/OSS/issues/1'}

    def comment(self, login, stamp, kind='User'):
        return {'user': {'login': login, 'type': kind}, 'created_at': stamp}

    def test_author_and_bot_acknowledgements_do_not_stop_sla(self):
        comments = [self.comment('author', '2026-11-01T01:00:00Z'),
                    self.comment('helper[bot]', '2026-11-01T02:00:00Z'),
                    self.comment('automation', '2026-11-01T03:00:00Z', 'Bot')]
        data = summarize([self.issue], {'1': comments}, self.now)
        self.assertEqual(data['pending_count'], 1)
        self.assertEqual(data['overdue_count'], 1)

    def test_first_human_reply_is_chronological_and_utc_normalized(self):
        comments = [self.comment('reviewer', '2026-11-02T00:00:00Z'),
                    self.comment('other', '2026-11-01T12:00:00+09:00')]
        data = summarize([self.issue], {'1': comments}, self.now)
        self.assertEqual(data['rows'][0]['response_hours'], 3)
        self.assertEqual(data['overdue_count'], 0)

    def test_old_open_issue_is_not_lost_from_response_queue(self):
        self.issue['created_at'] = '2026-01-01T00:00:00Z'
        data = summarize([self.issue], {}, self.now)
        self.assertEqual(data['opened_week'], 0)
        self.assertEqual(data['overdue_count'], 1)

    def test_week_boundaries_closed_count_and_pr_exclusion(self):
        closed = dict(self.issue, number=2, state='closed', closed_at='2026-11-03T00:00:00Z')
        pr = dict(self.issue, number=3, pull_request={})
        end = dict(self.issue, number=4, created_at='2026-11-04T00:00:00Z')
        data = summarize([self.issue, closed, pr, end], {}, self.now)
        self.assertEqual(data['opened_week'], 2)
        self.assertEqual(data['closed_week'], 1)
        self.assertEqual(data['open_count'], 2)

    def test_example_marking_title_escaping_and_invalid_sla(self):
        self.issue['title'] = '<b>name</b> | [link]\nnext'
        data = summarize([self.issue], {}, self.now)
        text = render(data, example=True)
        self.assertIn('예시 데이터', text)
        self.assertIn('&lt;b&gt;', text)
        self.assertIn('\\|', text)
        with self.assertRaises(ValueError):
            summarize([], {}, self.now, sla_hours=0)
