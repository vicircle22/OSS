# DORA 메트릭 수집 자동화

2주차 과제의 네 지표를 GitHub Actions로 수집하고 대시보드 시안과 함께 제공한다.

## 제출할 화면

1. [워크플로우 코드](../../.github/workflows/metrics.yml): 주간 예약, 배포/장애 이벤트, 수동 실행, JSON 아티팩트 저장.
2. [Actions](https://github.com/vicircle22/OSS/actions/workflows/metrics.yml): 성공 실행의 Summary에서 네 지표와 주간 보고서 확인.
3. 실행 하단의 `dora-metrics-실행ID` 아티팩트: `metrics.json`, `report.md`, `dashboard.svg`, `index.html` 포함.
4. [대시보드 시안](example/dashboard.svg): **예시 데이터**로 화면 구성을 제시한다. 실측 값은 Actions 결과를 사용한다.

## 계산 기준

| 지표 | 자동 수집 원본 | 계산 |
|---|---|---|
| Lead Time | GitHub Deployments 성공 상태 + 이전 성공 배포 SHA 대비 새 커밋 | committer 시각부터 최초 성공 배포까지 초 단위, 중앙값 |
| Deployment Frequency | 대상 환경의 성공 배포 | 최근 28일 성공 배포 수 / 28일 |
| MTTR | `incident` 라벨 이슈 | 관찰 기간에 종료된 장애 이슈의 생성부터 종료까지 평균. 이슈 기록 기반 대리지표 |
| Change Failure Rate | 성공 배포 + `incident` 이슈의 `deployment_id` | 장애에 연결된 고유 배포 수 / 기간 내 성공 배포 수 × 100 |

관찰 기간은 UTC 기준 `[수집 시각-28일, 수집 시각)`이며 주별 값도 제공한다. 최초 배포는 이전 SHA 기준점이 없어 Lead Time에서 제외한다. 같은 커밋은 최초 배포 한 번만 집계하며, 이전 버전으로 롤백한 배포에서 새 Lead Time을 만들지 않는다. 배포 재시도 상태는 같은 deployment ID 안에서 중복 집계하지 않는다.

단순 push, PR 병합, CI 테스트 실패를 운영 배포나 운영 장애로 간주하지 않는다. GitHub의 deployment `failure`만으로 실제 서비스 장애를 판정하지 않으므로, 장애 이슈를 연결한다. 배포 실패 복구와 관련된 실제 사건을 기록해야 네 지표를 해석할 수 있다.

## 배포·장애 기록 연결

- Vercel/AWS 등 실제 배포 도구가 GitHub Deployments에 배포 SHA와 대상 환경, `success` 상태를 기록하도록 연동한다.
- 대상 환경의 기본값은 `production`. 다른 이름이면 저장소 Actions 변수 `DORA_ENVIRONMENT`를 지정한다.
- 실제 배포 관련 장애 발생 시 `incident` 라벨을 붙인 이슈 본문에 한 줄로 `deployment_id: 123456`을 기록한다. ID는 해당 운영 배포 ID여야 한다.
- 이슈 생성 시각을 장애 발견 시각, 종료 시각을 복구 시각의 대리지표로 사용한다. 실제 발견·복구와 이슈 기록 사이 지연은 MTTR의 한계다. 복구 완료 시 이슈를 닫는다.
- 과거 시각을 가짜로 넣거나 과제용 가짜 배포/장애 이슈를 실측 데이터에 섞지 않는다.

배포/장애 기록이 없는 경우 `null`과 **데이터 없음**을 출력한다. 성공 배포가 있고 장애 기록이 없으면 CFR은 기록상 0%지만, 이 값만으로 안정성을 증명할 수 없다. 아직 실제 서비스가 없는 현재 상태에서도 수집 실행, JSON 저장, 보고서 및 시안 생성은 검증할 수 있다.

## 실행 및 보고서

- 자동: 매주 월요일 09:00 KST, deployment status 변경, incident 이슈 변경.
- 수동: Actions → DORA Metrics → Run workflow.
- 워크플로우 변경 push 시 첫 수집 실행. 수집 전 계산 테스트를 수행한다.
- 토큰 권한은 contents/deployments/issues **read**. 저장소에 자동 commit/push하지 않는다.
- 보고서는 실행 Summary와 아티팩트에 자동 생성하며 90일 보존한다. 장기 보관 시 다운로드한다.
- API 오류 또는 페이지 한도 초과는 실행 실패로 표시하며 일부 데이터를 정상 수집처럼 출력하지 않는다.

```bash
python3 -m unittest discover -s tests -v
python3 scripts/dora/collect.py --repo vicircle22/OSS --out dora-output
python3 scripts/dora/collect.py --fixture scripts/dora/example.json --out docs/dora/example
python3 -m http.server 8765 --bind 127.0.0.1 --directory docs
```

브라우저: `http://127.0.0.1:8765/dora/example/`. 외부 라이브러리나 AI API 키는 필요 없다. 비공개 저장소는 환경변수 `GITHUB_TOKEN`에 읽기 토큰을 설정하며 토큰을 코드에 기록하지 않는다.

## 변경 전 백업 및 복원

- 원래 main: `ebdd019f9fd17620d0cdf9508ad07c1ca6a76fd0`
- [백업 브랜치](https://github.com/vicircle22/OSS/tree/backup/pre-dora-20261012-ebdd019): `backup/pre-dora-20261012-ebdd019`
- [백업 태그](https://github.com/vicircle22/OSS/releases/tag/backup-pre-dora-20261012-ebdd019): `backup-pre-dora-20261012-ebdd019`

Git 커밋이 파일의 스냅샷이며, 백업 브랜치와 태그는 그 커밋을 가리키는 복원 지점이다. 백업 ZIP은 태그 화면의 Code/Download ZIP 또는 아래 URL로 받을 수 있다.

`https://github.com/vicircle22/OSS/archive/refs/tags/backup-pre-dora-20261012-ebdd019.zip`

이 변경을 되돌릴 때는 추가된 DORA 기능 커밋을 `git revert <DORA-기능-커밋-SHA>`로 취소하고 push한다. 이후 다른 변경이 있다면 해당 커밋만 revert하고 충돌을 검토한다. 백업 태그로 새 작업 브랜치를 만들려면:

```bash
git fetch origin --tags
git switch -c restore/pre-dora backup-pre-dora-20261012-ebdd019
```

백업은 저장소 파일과 Git 이력을 보존한다. GitHub Issues·Milestones·계정 설정은 Git 스냅샷 대상이 아니다. 기존에 등록한 마일스톤은 이 작업에서 변경하지 않는다.

정의 참고: [DORA](https://dora.dev/guides/dora-metrics/), [GitHub Deployments](https://docs.github.com/en/rest/deployments/deployments). 과제에 명시된 전통적인 4개 지표 이름을 사용한다.
