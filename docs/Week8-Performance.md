# 8주차 캐싱 전후 실측 비교

- 실행 근거: https://github.com/vicircle22/OSS/actions/runs/42929447230
- 동일 소스 커밋: `b5577af8682ac584dc09579d5fcf5992811632c7`
- 환경: Linux / Python 3.12.16

| 구분 | Cache hit | 의존성 준비(초) | Job 전체(초) |
|---|---|---:|---:|
| baseline | false | 3.005 | 12 |
| cold | false | 4.351 | 13 |
| warm | true | 1.169 | 10 |

**의존성 준비 개선율: (3.005 − 1.169) / 3.005 × 100 = 61.09%**

Job 전체 시간의 관측 개선율: **16.67%**. 준비 시간 개선율과 혼동하지 않습니다.

## 측정 조건과 한계

- 같은 커밋·Python 패치 버전·OS·의존성 파일, 같은 Composite Action과 Reusable Workflow를 사용합니다.
- baseline은 캐시 기능을 끄고, cold는 이번 run만의 새 키로 저장, warm은 그 정확한 키 적중 후 설치를 생략합니다.
- 의존성 준비 시간은 Python 선택 이후부터 캐시 복원·venv 생성/설치·Ruff 확인까지 perf_counter로 측정합니다.
- Python 선택·checkout·Lint/Test·캐시 post-save는 준비 시간에서 제외됩니다. Job 전체에는 이 부가 비용도 포함됩니다.
- Job 전체는 GitHub started_at→completed_at이며, 다른 Job을 기다리는 시간은 별도입니다.
- 조건별 1회 관측이므로 러너·네트워크 변동과 캐시 저장 비용을 포함해 해석합니다. 통계적 보장이나 전체 9개 Matrix의 동일 개선율로 일반화하지 않습니다.
- 음수 개선율도 그대로 보고합니다. 관측값을 목표 수치에 맞춰 바꾸지 않습니다.
- 7주차 6개 조합과 8주차 9개 조합의 전체 시간은 조건이 달라 직접 개선율로 비교하지 않습니다.

## 구현·선택 실행의 실제 근거

- [최적화 전 7주차 main 실행](https://github.com/vicircle22/OSS/actions/runs/42771295275)
- [최적화 후 9개 Matrix PR 검증 성공](https://github.com/vicircle22/OSS/actions/runs/42929447114)
- [동일 조건 캐시 비교·원자료 아티팩트](https://github.com/vicircle22/OSS/actions/runs/42929447230)
- [재사용·캐시·분기 구현 PR #23](https://github.com/vicircle22/OSS/pull/23)
- [현재 CI/CD 실행](https://github.com/vicircle22/OSS/actions/workflows/python-ci-cd.yml)

이 보고서와 문서 링크만 추가하는 후속 PR/main push에서는 변경 파일 감지가 Build/Test/Deploy를 생략하는지 확인합니다.
기존 PR Quality의 간단한 커밋·테스트 검사는 독립적으로 유지합니다. 실제 생략 여부는 해당 실행의 Changed-file decision과 Job 상태를 확인합니다.

## 원측정값

```json
{
  "rows": [
    {
      "label": "warm",
      "revision": "b5577af8682ac584dc09579d5fcf5992811632c7",
      "run_id": "42929447230",
      "runner_os": "Linux",
      "python_version": "3.12.16",
      "requirements_sha256": "29100f9a45e4c8d96555d5d9b34f1a42e44fbb7ec48406b1b267bd45530b0512",
      "dependency_seconds": 1.169054,
      "cache_hit": "true"
    },
    {
      "label": "baseline",
      "revision": "b5577af8682ac584dc09579d5fcf5992811632c7",
      "run_id": "42929447230",
      "runner_os": "Linux",
      "python_version": "3.12.16",
      "requirements_sha256": "29100f9a45e4c8d96555d5d9b34f1a42e44fbb7ec48406b1b267bd45530b0512",
      "dependency_seconds": 3.004647,
      "cache_hit": "false"
    },
    {
      "label": "cold",
      "revision": "b5577af8682ac584dc09579d5fcf5992811632c7",
      "run_id": "42929447230",
      "runner_os": "Linux",
      "python_version": "3.12.16",
      "requirements_sha256": "29100f9a45e4c8d96555d5d9b34f1a42e44fbb7ec48406b1b267bd45530b0512",
      "dependency_seconds": 4.35116,
      "cache_hit": "false"
    }
  ],
  "durations": {
    "baseline": 12,
    "cold": 13,
    "warm": 10
  }
}
```
