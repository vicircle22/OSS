# AI SUMMIT — DORA 주간 보고서

- 수집 시각: 2026-10-12T00:00:00Z (UTC)
- 대상: `vicircle22/OSS` / `production`
- 관찰 기간: 2026-09-14T00:00:00Z ≤ 시각 < 2026-10-12T00:00:00Z
- 데이터: 예시 데이터 (실제 운영 성과 아님)

| 지표 | 값 |
|---|---|
| Lead Time | 5.00 h |
| Deployment Frequency | 0.21 /day |
| MTTR | 2.00 h |
| Change Failure Rate | 16.7% |

성공 배포 6건 · Lead Time 표본 5개 · 장애 연결 배포 1건 · 종료 장애 1건 · 미해결 장애 0건

## 주별 지표

| 시작 (UTC) | Lead Time | Deployment Frequency | MTTR | Change Failure Rate |
|---|---|---|---|---|
| 2026-09-14 | 데이터 없음 | 0.14 /day | 데이터 없음 | 0.0% |
| 2026-09-21 | 7.00 h | 0.29 /day | 데이터 없음 | 0.0% |
| 2026-09-28 | 4.00 h | 0.14 /day | 데이터 없음 | 0.0% |
| 2026-10-05 | 4.00 h | 0.29 /day | 2.00 h | 50.0% |

## 계산 정의와 해석

- Lead Time: 이전 성공 배포 대비 새 커밋의 committer 시각 → 최초 성공 운영 배포 시각의 중앙값
- Deployment Frequency: 관찰 기간의 성공 운영 배포 수 / 관찰 일수
- MTTR: 기간 내 종료된 배포 관련 incident 생성 → 종료 시간 평균 (이슈 기반 대리지표)
- Change Failure Rate: 기간 내 성공 배포 중 incident에 연결된 고유 배포 수 / 성공 운영 배포 수 × 100

GitHub에 기록된 대상 환경의 성공 배포와 incident 이슈만 측정합니다. 기록 누락 시 실제 운영 성과를 판단할 수 없습니다.

장애 기록이 없으면 MTTR은 null입니다. 배포 기록이 없으면 비율도 null입니다. 장애 신고 누락 시 CFR 0%가 안정성을 증명하지 않습니다.

## 수집 주의사항

- 없음

## 원본 근거

| 배포 ID | SHA | 성공 시각 |
|---|---|---|
| 101 | `example-sha-` | 2026-09-18T12:00:00Z |
| 102 | `example-sha-` | 2026-09-22T12:00:00Z |
| 103 | `example-sha-` | 2026-09-27T12:00:00Z |
| 104 | `example-sha-` | 2026-10-01T12:00:00Z |
| 105 | `example-sha-` | 2026-10-07T12:00:00Z |
| 106 | `example-sha-` | 2026-10-10T12:00:00Z |

| 장애 이슈 | 연결 배포 | 생성 시각 | 종료 시각 |
|---|---|---|---|
| [#1](https://example.com/incident-1) | 105 | 2026-10-07T13:00:00Z | 2026-10-07T15:00:00Z |

JSON·HTML·SVG 화면은 이 실행의 `dora-metrics-*` 아티팩트에서 다운로드할 수 있습니다.

참고: https://dora.dev/guides/dora-metrics/ · https://docs.github.com/en/rest/deployments/deployments
