"""Read-only issue response report. Bot acknowledgements never satisfy the SLA."""
import argparse
from datetime import timedelta
import html
import json
import os
from pathlib import Path

from scripts.dora.collect import GitHub, UTC, iso, time
from datetime import datetime


def summarize(issues, comments, now, sla_hours=24):
    if sla_hours <= 0:
        raise ValueError('SLA hours must be positive')
    start = now - timedelta(days=7)
    issues = [i for i in issues if 'pull_request' not in i]
    inside = lambda stamp: stamp and start <= time(stamp) < now
    rows = []
    for issue in issues:
        created = time(issue['created_at'])
        if issue['state'] != 'open' or created > now:
            continue
        replies = []
        for comment in comments.get(str(issue['number']), []):
            user = comment.get('user') or {}
            login = user.get('login', '')
            stamp = time(comment['created_at'])
            if (login and login != issue['user']['login'] and user.get('type') != 'Bot'
                    and not login.endswith('[bot]') and created <= stamp <= now):
                replies.append(stamp)
        first = min(replies) if replies else None
        age = (now - created).total_seconds() / 3600
        rows.append({'number': issue['number'], 'title': issue['title'],
                     'url': issue['html_url'], 'age_hours': age,
                     'response_hours': (first - created).total_seconds() / 3600 if first else None,
                     'overdue': first is None and age >= sla_hours})
    return {'generated_at': iso(now), 'sla_hours': sla_hours,
            'opened_week': sum(bool(inside(i['created_at'])) for i in issues),
            'closed_week': sum(bool(inside(i.get('closed_at'))) for i in issues),
            'open_count': len(rows), 'pending_count': sum(r['response_hours'] is None for r in rows),
            'overdue_count': sum(r['overdue'] for r in rows), 'rows': rows}


def render(data, example=False):
    lines = ['# AI SUMMIT 비동기 협업 주간 요약', '',
             '**예시 데이터 · 운영 측정 아님**' if example else '**GitHub 일반 Issue 기록 기반 · 읽기 전용**',
             f"수집: {data['generated_at']}", '',
             f"최근 7일 생성 {data['opened_week']}건 / 종료 {data['closed_week']}건 / 현재 열림 {data['open_count']}건",
             f"첫 사람 응답 대기 {data['pending_count']}건 / {data['sla_hours']}시간 이상 대기 {data['overdue_count']}건", '',
             '| Issue | 경과 시간 | 첫 사람 응답 | 상태 |', '|---|---|---|---|']
    for row in data['rows']:
        title = html.escape(row['title']).replace('\n', ' ').replace('\r', ' ')
        title = title.replace('|', '\\|').replace('[', '\\[').replace(']', '\\]')
        response = '대기' if row['response_hours'] is None else f"{row['response_hours']:.1f} h"
        lines.append(f"| [#{row['number']} {title}]({row['url']}) | {row['age_hours']:.1f} h | {response} | {'응답 목표 초과' if row['overdue'] else '확인'} |")
    lines += ['', 'SLA는 팀 합의 전 24시간 경과 시간 제안입니다. UTC 기준이며 주말도 포함합니다.',
              '작성자 본인·Bot·[bot] 계정의 댓글은 사람의 첫 응답으로 세지 않습니다.',
              '일반 Issue 댓글만 측정하며 PR 리뷰·Discussions·DM·실제 해결 시간은 측정하지 않습니다.',
              '기간은 [수집-7일, 수집)이며 현재 열린 오래된 Issue도 응답 대기에 포함합니다.',
              '이 보고서는 댓글·라벨·담당자를 변경하거나 자동 독촉하지 않습니다.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default=os.getenv('GITHUB_REPOSITORY', 'vicircle22/OSS'))
    parser.add_argument('--fixture', type=Path, help='Offline synthetic data, explicitly marked as example')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.fixture:
        fixture = json.loads(args.fixture.read_text(encoding='utf-8'))
        issues, comments, now = fixture['issues'], fixture['comments'], time(fixture['now'])
    else:
        api = GitHub(args.repo, os.getenv('GITHUB_TOKEN'))
        now = datetime.now(UTC)
        issues = api.pages('/issues', {'state': 'all'})
        comments = {str(i['number']): api.pages(f"/issues/{i['number']}/comments")
                    for i in issues if 'pull_request' not in i and i['state'] == 'open'}
    data = summarize(issues, comments, now)
    data['data_mode'] = 'example' if args.fixture else 'live'
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'report.md').write_text(render(data, bool(args.fixture)), encoding='utf-8')
    (args.out / 'summary.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
