#!/usr/bin/env python3
"""Read GitHub production deployments and incident issues; standard library only."""
import argparse
from datetime import datetime, timedelta, timezone
import html
import json
import os
from pathlib import Path
import re
import statistics
import urllib.parse
import urllib.request

UTC = timezone.utc


def time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(UTC)


def iso(value):
    return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')


class GitHub:
    def __init__(self, repo, token=None):
        if not re.fullmatch(r'[\w.-]+/[\w.-]+', repo):
            raise ValueError('Repository must be owner/name')
        self.base = f'https://api.github.com/repos/{repo}'
        self.token = token

    def get(self, path, params=None):
        url = self.base + path + ('?' + urllib.parse.urlencode(params) if params else '')
        headers = {'Accept': 'application/vnd.github+json',
                   'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'OSS-DORA'}
        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
            return json.load(response)

    def pages(self, path, params=None, key=None):
        result = []
        for page in range(1, 101):
            data = self.get(path, dict(params or {}, per_page=100, page=page))
            batch = data[key] if key else data
            if not isinstance(batch, list):
                raise ValueError('Unexpected API list response')
            result.extend(batch)
            if len(batch) < 100:
                return result
        raise RuntimeError('Pagination limit reached; refusing partial metrics')


def sources(api, environment):
    deployments, incidents, warnings = [], [], []
    for dep in api.pages('/deployments', {'environment': environment}):
        if dep.get('transient_environment'):
            continue
        statuses = api.pages(f"/deployments/{dep['id']}/statuses")
        successes = [s['created_at'] for s in statuses if s['state'] == 'success']
        if successes:
            deployments.append({'id': dep['id'], 'sha': dep['sha'],
                                'deployed_at': min(successes, key=time)})
    deployments.sort(key=lambda d: time(d['deployed_at']))
    for issue in api.pages('/issues', {'state': 'all', 'labels': 'incident'}):
        if 'pull_request' in issue:
            continue
        matches = re.findall(r'^\s*deployment_id:\s*(\d+)\s*$', issue.get('body') or '', re.M | re.I)
        if len(matches) != 1:
            warnings.append(f"incident #{issue['number']}: deployment_id 하나가 필요하여 제외")
            continue
        incidents.append({'number': issue['number'], 'deployment_id': int(matches[0]),
                          'opened_at': issue['created_at'], 'closed_at': issue.get('closed_at'),
                          'url': issue['html_url']})
    return deployments, incidents, warnings


def lead_samples(api, deployments):
    samples, warnings, seen = [], [], set()
    if not deployments:
        return samples, warnings
    seen.add(deployments[0]['sha'])
    warnings.append('최초 성공 배포는 이전 배포 기준점이 없어 Lead Time 표본에서 제외')
    for previous, current in zip(deployments, deployments[1:]):
        if previous['sha'] == current['sha']:
            continue
        path = f"/compare/{previous['sha']}...{current['sha']}"
        if api.get(path, {'per_page': 100, 'page': 1})['status'] == 'behind':
            # Baseline ancestors also existed in production before a rollback.
            reverse = f"/compare/{current['sha']}...{previous['sha']}"
            seen.update(c['sha'] for c in api.pages(reverse, key='commits'))
            continue
        for commit in api.pages(path, key='commits'):
            sha = commit['sha']
            if sha in seen:
                continue
            seen.add(sha)
            committed_at = commit['commit']['committer']['date']
            seconds = (time(current['deployed_at']) - time(committed_at)).total_seconds()
            if seconds < 0:
                warnings.append(f"배포 {current['id']}: 미래 커밋 시각 표본 제외")
                continue
            samples.append({'sha': sha, 'deployment_id': current['id'],
                            'deployed_at': current['deployed_at'], 'committed_at': committed_at,
                            'seconds': seconds})
    return samples, warnings


def calculate(deployments, incidents, samples, start, end):
    inside = lambda t: start <= time(t) < end
    selected = [d for d in deployments if inside(d['deployed_at'])]
    selected_ids = {d['id'] for d in selected}
    all_deps = {d['id']: d for d in deployments}
    linked = [i for i in incidents if i['deployment_id'] in all_deps
              and time(i['opened_at']) >= time(all_deps[i['deployment_id']]['deployed_at'])
              and time(i['opened_at']) < end]
    failed = {i['deployment_id'] for i in linked if i['deployment_id'] in selected_ids}
    recovered = [i for i in linked if i.get('closed_at') and inside(i['closed_at'])
                 and time(i['closed_at']) >= time(i['opened_at'])]
    durations = [(time(i['closed_at']) - time(i['opened_at'])).total_seconds() for i in recovered]
    leads = [s['seconds'] for s in samples if inside(s['deployed_at'])]
    days = (end - start).total_seconds() / 86400
    return {'lead_time_seconds': statistics.median(leads) if leads else None,
            'deployment_frequency_per_day': len(selected) / days if selected else None,
            'mttr_seconds': statistics.mean(durations) if durations else None,
            'change_failure_rate_percent': len(failed) / len(selected) * 100 if selected else None,
            'deployment_count': len(selected), 'lead_time_sample_count': len(leads),
            'failed_deployment_count': len(failed), 'resolved_incident_count': len(recovered),
            'open_incident_count': sum(not i.get('closed_at') or time(i['closed_at']) >= end for i in linked)}


DEFINITIONS = {
    'Lead Time': '이전 성공 배포 대비 새 커밋의 committer 시각 → 최초 성공 운영 배포 시각의 중앙값',
    'Deployment Frequency': '관찰 기간의 성공 운영 배포 수 / 관찰 일수',
    'MTTR': '기간 내 종료된 배포 관련 incident 생성 → 종료 시간 평균 (이슈 기반 대리지표)',
    'Change Failure Rate': '기간 내 성공 배포 중 incident에 연결된 고유 배포 수 / 성공 운영 배포 수 × 100',
}


def build(repo, environment, deployments, incidents, samples, warnings, now, mode='live'):
    start = now - timedelta(days=28)
    known = {d['id'] for d in deployments}
    for incident in incidents:
        if incident['deployment_id'] not in known:
            warnings.append(f"incident #{incident['number']}: 대상 환경의 성공 배포를 찾지 못해 제외")
        elif incident.get('closed_at') and time(incident['closed_at']) < time(incident['opened_at']):
            warnings.append(f"incident #{incident['number']}: 종료 시각 오류로 MTTR 표본 제외")
    weekly = []
    for offset in (28, 21, 14, 7):
        a, b = now - timedelta(days=offset), now - timedelta(days=offset - 7)
        weekly.append({'start': iso(a), 'end': iso(b), **calculate(deployments, incidents, samples, a, b)})
    return {'schema_version': 1, 'data_mode': mode, 'repository': repo, 'environment': environment,
            'generated_at': iso(now), 'window': {'start': iso(start), 'end': iso(now), 'days': 28},
            'metrics': calculate(deployments, incidents, samples, start, now), 'weekly': weekly,
            'warnings': warnings, 'definitions': DEFINITIONS,
            'coverage': 'GitHub에 기록된 대상 환경의 성공 배포와 incident 이슈만 측정합니다. 기록 누락 시 실제 운영 성과를 판단할 수 없습니다.',
            'sources': {'successful_deployments': deployments, 'incidents': incidents, 'lead_samples': samples}}


def display(metrics):
    hours = lambda v: '데이터 없음' if v is None else f'{v / 3600:.2f} h'
    return [hours(metrics['lead_time_seconds']),
            '데이터 없음' if metrics['deployment_frequency_per_day'] is None else f"{metrics['deployment_frequency_per_day']:.2f} /day",
            hours(metrics['mttr_seconds']),
            '데이터 없음' if metrics['change_failure_rate_percent'] is None else f"{metrics['change_failure_rate_percent']:.1f}%"]


def svg(data):
    mode = '예시 데이터 · 실제 운영 성과 아님' if data['data_mode'] == 'example' else 'GitHub 기록 기반 · 실측 수집'
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650" role="img" aria-labelledby="title desc">',
             '<title id="title">AI SUMMIT DORA Dashboard</title>',
             '<desc id="desc">DORA 4개 지표와 주간 성공 배포 수. 기록이 없으면 데이터 없음으로 표시.</desc>',
             '<rect width="1200" height="650" fill="#0b1220"/>',
             '<g font-family="Arial, Noto Sans KR, sans-serif" fill="#e9efff">',
             '<text x="42" y="56" font-size="28" font-weight="700">AI SUMMIT · DORA Dashboard</text>',
             f'<text x="42" y="88" font-size="14" fill="#93a9c4">{html.escape(mode)} | {html.escape(data["environment"])} | 28일 관찰</text>',
             f'<text x="42" y="115" font-size="13" fill="#93a9c4">{data["window"]["start"]} → {data["window"]["end"]} (UTC)</text>']
    subtitles = ['커밋 → 성공 배포 · 중앙값', '성공 운영 배포 / 일', '장애 이슈 생성 → 종료 · 평균', '장애 연결 배포 / 성공 배포']
    for i, (name, value, subtitle) in enumerate(zip(DEFINITIONS, display(data['metrics']), subtitles)):
        x = 42 + i * 282
        parts += [f'<rect x="{x}" y="143" width="268" height="147" rx="14" fill="#142238" stroke="#263b58"/>',
                  f'<text x="{x+17}" y="175" font-size="16">{name}</text>',
                  f'<text x="{x+17}" y="226" font-size="27" fill="#66e0cf" font-weight="700">{value}</text>',
                  f'<text x="{x+17}" y="264" font-size="12" fill="#a7b7cc">{subtitle}</text>']
    parts.append('<text x="42" y="331" font-size="19" font-weight="700">주간 성공 운영 배포 수</text>')
    maximum = max([w['deployment_count'] for w in data['weekly']] + [1])
    for i, week in enumerate(data['weekly']):
        y, count = 365 + i * 43, week['deployment_count']
        parts += [f'<text x="42" y="{y+18}" font-size="13" fill="#a7b7cc">{week["start"][:10]}</text>',
                  f'<rect x="165" y="{y}" width="880" height="25" rx="5" fill="#142238"/>',
                  f'<rect x="165" y="{y}" width="{count/maximum*770:.1f}" height="25" rx="5" fill="#36baa9"/>',
                  f'<text x="1070" y="{y+18}" font-size="14">{count}건</text>']
    parts += ['<text x="42" y="574" font-size="13" fill="#a7b7cc">기록이 없으면 수집 연결을 확인하세요. MTTR은 이슈 기록 기반이며, 장애가 없으면 값이 없습니다.</text>',
              '<text x="42" y="601" font-size="13" fill="#a7b7cc">측정 정의·표본 수·장애 연결·원본 근거는 보고서와 metrics.json에서 확인할 수 있습니다.</text>',
              f'<text x="42" y="628" font-size="12" fill="#7188a3">{html.escape(data["repository"])} · {data["generated_at"]}</text>',
              '</g></svg>']
    return '\n'.join(parts)


def report(data):
    m = data['metrics']
    lines = ['# AI SUMMIT — DORA 주간 보고서', '', f"- 수집 시각: {data['generated_at']} (UTC)",
             f"- 대상: `{data['repository']}` / `{data['environment']}`",
             f"- 관찰 기간: {data['window']['start']} ≤ 시각 < {data['window']['end']}",
             f"- 데이터: {'예시 데이터 (실제 운영 성과 아님)' if data['data_mode'] == 'example' else 'GitHub API 실측 수집'}", '',
             '| 지표 | 값 |', '|---|---|']
    lines += [f'| {n} | {v} |' for n, v in zip(DEFINITIONS, display(m))]
    lines += ['', f"성공 배포 {m['deployment_count']}건 · Lead Time 표본 {m['lead_time_sample_count']}개 · 장애 연결 배포 {m['failed_deployment_count']}건 · 종료 장애 {m['resolved_incident_count']}건 · 미해결 장애 {m['open_incident_count']}건", '',
              '## 주별 지표', '', '| 시작 (UTC) | Lead Time | Deployment Frequency | MTTR | Change Failure Rate |', '|---|---|---|---|---|']
    lines += [f"| {w['start'][:10]} | " + ' | '.join(display(w)) + ' |' for w in data['weekly']]
    lines += ['', '## 계산 정의와 해석', ''] + [f'- {k}: {v}' for k, v in DEFINITIONS.items()]
    lines += ['', data['coverage'], '', '장애 기록이 없으면 MTTR은 null입니다. 배포 기록이 없으면 비율도 null입니다. 장애 신고 누락 시 CFR 0%가 안정성을 증명하지 않습니다.', '', '## 수집 주의사항', '']
    lines += (['- ' + w for w in data['warnings']] or ['- 없음'])
    lines += ['', '## 원본 근거', '', '| 배포 ID | SHA | 성공 시각 |', '|---|---|---|']
    lines += [f"| {d['id']} | `{d['sha'][:12]}` | {d['deployed_at']} |" for d in data['sources']['successful_deployments']]
    lines += ['', '| 장애 이슈 | 연결 배포 | 생성 시각 | 종료 시각 |', '|---|---|---|---|']
    lines += [f"| [#{i['number']}]({i['url']}) | {i['deployment_id']} | {i['opened_at']} | {i.get('closed_at') or '미해결'} |" for i in data['sources']['incidents']]
    lines += ['', 'JSON·HTML·SVG 화면은 이 실행의 `dora-metrics-*` 아티팩트에서 다운로드할 수 있습니다.', '',
              '참고: https://dora.dev/guides/dora-metrics/ · https://docs.github.com/en/rest/deployments/deployments', '']
    return '\n'.join(lines)


def write(data, out):
    out.mkdir(parents=True, exist_ok=True)
    (out / 'metrics.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    graphic = svg(data)
    (out / 'dashboard.svg').write_text(graphic, encoding='utf-8')
    (out / 'report.md').write_text(report(data), encoding='utf-8')
    definitions = ''.join(f'<li><strong>{html.escape(k)}</strong>: {html.escape(v)}</li>' for k, v in DEFINITIONS.items())
    page = f'''<!doctype html>
<html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI SUMMIT DORA Dashboard</title>
<style>body{{margin:0;background:#0b1220;color:#e9efff;font:16px/1.7 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:20px}}svg{{width:100%;height:auto}}a{{color:#66e0cf}}section{{background:#142238;border:1px solid #263b58;border-radius:12px;padding:24px;margin:18px 0}}h2{{margin:0 0 12px}}</style>
<main>{graphic}<section><h2>측정 정의 및 근거</h2><ul>{definitions}</ul><p>{html.escape(data['coverage'])}</p><p><a href="metrics.json">JSON 원본</a> · <a href="report.md">주간 보고서</a></p></section></main></html>'''
    (out / 'index.html').write_text(page, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default=os.getenv('GITHUB_REPOSITORY', 'vicircle22/OSS'))
    parser.add_argument('--environment', default=os.getenv('DORA_ENVIRONMENT', 'production'))
    parser.add_argument('--out', type=Path, default=Path('docs/dora'))
    parser.add_argument('--fixture', type=Path, help='Synthetic example only; output marked example')
    args = parser.parse_args()
    if args.fixture:
        f = json.loads(args.fixture.read_text(encoding='utf-8'))
        data = build(args.repo, args.environment, f['deployments'], f['incidents'], f['lead_samples'], [], time(f['now']), mode='example')
    else:
        api = GitHub(args.repo, os.getenv('GITHUB_TOKEN'))
        deployments, incidents, warnings = sources(api, args.environment)
        samples, lead_warnings = lead_samples(api, deployments)
        data = build(args.repo, args.environment, deployments, incidents, samples, warnings + lead_warnings, datetime.now(UTC))
    write(data, args.out)
    print(json.dumps({'data_mode': data['data_mode'], 'metrics': data['metrics'], 'output': str(args.out)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
