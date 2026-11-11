"""Compute an honest paired cache comparison from measured Actions artifacts."""
import argparse
from datetime import datetime
import json
from pathlib import Path


def compare(rows):
    phases = {r['label']: r for r in rows}
    if len(rows) != 3 or set(phases) != {'baseline', 'cold', 'warm'}:
        raise ValueError('Exactly baseline/cold/warm measurements are required')
    identity = ('revision', 'runner_os', 'python_version', 'requirements_sha256')
    if len({tuple(r[k] for k in identity) for r in rows}) != 1:
        raise ValueError('Comparison commit, OS, Python and dependencies must match')
    if phases['warm']['cache_hit'] != 'true' or phases['cold']['cache_hit'] != 'false':
        raise ValueError('Cold miss and warm exact cache hit must be demonstrated')
    baseline = phases['baseline']['dependency_seconds']
    if baseline <= 0:
        raise ValueError('Baseline duration must be positive')
    return {'phases': phases, 'improvement_percent':
            (baseline - phases['warm']['dependency_seconds']) / baseline * 100}


def job_durations(jobs):
    durations = {}
    for job in jobs:
        for phase in ('baseline', 'cold', 'warm'):
            if job['name'].endswith('Check ' + phase) and job.get('completed_at'):
                parse = lambda value: datetime.fromisoformat(value.replace('Z', '+00:00'))
                durations[phase] = (parse(job['completed_at']) - parse(job['started_at'])).total_seconds()
    return durations


def report(comparison, durations):
    phases = comparison['phases']
    lines = ['# 8주차 캐싱 전후 실측 비교', '',
             f"- 실행 근거: https://github.com/vicircle22/OSS/actions/runs/{phases['baseline']['run_id']}",
             f"- 동일 소스 커밋: `{phases['baseline']['revision']}`",
             f"- 환경: {phases['baseline']['runner_os']} / Python {phases['baseline']['python_version']}", '',
             '| 구분 | Cache hit | 의존성 준비(초) | Job 전체(초) |', '|---|---|---:|---:|']
    for phase in ('baseline', 'cold', 'warm'):
        row = phases[phase]
        lines.append(f"| {phase} | {row['cache_hit']} | {row['dependency_seconds']:.3f} | {durations.get(phase, '미수집')} |")
    b, w = phases['baseline']['dependency_seconds'], phases['warm']['dependency_seconds']
    lines += ['', f"**의존성 준비 개선율: ({b:.3f} − {w:.3f}) / {b:.3f} × 100 = {comparison['improvement_percent']:.2f}%**", '']
    if 'baseline' in durations and 'warm' in durations and durations['baseline'] > 0:
        rate = (durations['baseline'] - durations['warm']) / durations['baseline'] * 100
        lines.append(f'Job 전체 시간의 관측 개선율: **{rate:.2f}%**. 준비 시간 개선율과 혼동하지 않습니다.')
    lines += ['', '## 측정 조건과 한계', '',
              '- 같은 커밋·Python 패치 버전·OS·의존성 파일, 같은 Composite Action과 Reusable Workflow를 사용합니다.',
              '- baseline은 캐시 기능을 끄고, cold는 이번 run만의 새 키로 저장, warm은 그 정확한 키 적중 후 설치를 생략합니다.',
              '- 의존성 준비 시간은 Python 선택 이후부터 캐시 복원·venv 생성/설치·Ruff 확인까지 perf_counter로 측정합니다.',
              '- Python 선택·checkout·Lint/Test·캐시 post-save는 준비 시간에서 제외됩니다. Job 전체에는 이 부가 비용도 포함됩니다.',
              '- Job 전체는 GitHub started_at→completed_at이며, 다른 Job을 기다리는 시간은 별도입니다.',
              '- 조건별 1회 관측이므로 러너·네트워크 변동과 캐시 저장 비용을 포함해 해석합니다. 통계적 보장이나 전체 9개 Matrix의 동일 개선율로 일반화하지 않습니다.',
              '- 음수 개선율도 그대로 보고합니다. 관측값을 목표 수치에 맞춰 바꾸지 않습니다.',
              '- 7주차 6개 조합과 8주차 9개 조합의 전체 시간은 조건이 달라 직접 개선율로 비교하지 않습니다.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements', type=Path, required=True)
    parser.add_argument('--jobs', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    rows = [json.loads(p.read_text(encoding='utf-8')) for p in args.measurements.rglob('metrics.json')]
    result = compare(rows)
    durations = job_durations(json.loads(args.jobs.read_text(encoding='utf-8'))['jobs'])
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'report.md').write_text(report(result, durations), encoding='utf-8')
    (args.out / 'measurements.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    (args.out / 'job-durations.json').write_text(json.dumps(durations, indent=2) + '\n', encoding='utf-8')
    print('CACHE_BENCHMARK_JSON=' + json.dumps({'rows': rows, 'durations': durations}))


if __name__ == '__main__':
    main()
