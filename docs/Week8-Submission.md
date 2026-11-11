# 8주차 · 워크플로우 실행 최적화

작성일: 2026-11-11 (Asia/Seoul).

## 제출 링크

- [최적화된 CI/CD](https://github.com/vicircle22/OSS/blob/main/.github/workflows/python-ci-cd.yml)
- [Reusable Workflow](https://github.com/vicircle22/OSS/blob/main/.github/workflows/reusable-python-checks.yml)
- [Composite Action](https://github.com/vicircle22/OSS/blob/main/.github/actions/python-environment/action.yml)
- [실측 비교 Workflow](https://github.com/vicircle22/OSS/actions/workflows/cache-benchmark.yml)
- [최적화 전 7주차 성공 실행](https://github.com/vicircle22/OSS/actions/runs/42771295275)

비교 보고서는 Cache Benchmark 실행의 Summary와 `cache-benchmark-report` 아티팩트에서 생성합니다.
[실측 전후 비교 보고서](Week8-Performance.md)에 같은 보고서와 원측정값을 보존했습니다. 준비 시간과 Job 전체 시간을 구분합니다.

## 구현

| 요구 | 적용 |
|---|---|
| Matrix 확장 | 7주차 3 OS × 2 Python(6개) → 3 OS × 3 Python(9개), Python 3.14 추가 |
| Reusable Workflow | 주 CI의 Matrix와 캐시 비교의 baseline/cold/warm이 같은 Lint·Test·아티팩트 검증 로직 호출 |
| Composite Action | Python 선택·정확한 키의 venv 복원·설치 생략·준비 시간 측정 재사용 |
| 캐싱 | OS·아키텍처·실제 Python 패치 버전·requirements 해시·namespace로 분리. 다른 환경의 캐시를 혼합하지 않음 |
| 실측 개선율 | 같은 조건의 캐시 미사용/첫 저장/적중 비교. 준비 시간·전체 Job 시간 구분 |
| 조건부 실행 | PR/main branch 조건 + Git diff 변경 파일 분류로 CI/배포 선택 |

## 선택적 배포 규칙

- PR은 변경 파일에 따라 Build/Test를 수행하지만 항상 Deploy는 건너뜁니다.
- main push에서 코드·테스트·실행용 UI·CI 설정·의존성이 바뀌면 검증 후 Release를 배포합니다.
- README·CONTRIBUTING·일반 Markdown 설명만 바뀌면 Build/Test/Deploy를 건너뜁니다.
- `docs/wireframes/`, `docs/dora/example/`은 실행 자원이므로 문서 폴더에 있어도 검증·배포 대상으로 봅니다.
- 알 수 없는 파일 형식·비교 실패는 보수적으로 검증·배포 대상으로 처리합니다.
- rename은 삭제·추가 경로 모두 비교하므로 코드 삭제/문서 이동을 놓치지 않습니다.
- 수동 실행은 변경 파일과 무관하게 검증을 강제합니다. Deploy는 여전히 main에서만 가능합니다.
- 문서 전용 변경은 다음 코드 배포 패키지에 포함되며 그때마다 새 Release를 만들지는 않습니다.
- 기존 PR Quality의 간단한 검사는 별도 Workflow로 유지합니다. 여기서 생략하는 것은 무거운 Build/9개 Matrix/Deploy입니다.

실제 결정은 `Detect changed files` Job Summary의 ci_required/deploy_required·변경 목록으로 확인합니다.
선택기 자체와 캐시 보고서의 조건 불일치·음수 개선율 처리도 테스트합니다.

## 캐시 측정의 해석

1. baseline: 캐시 없이 새 venv에 고정 Ruff를 설치합니다.
2. cold: 실행마다 고유한 새 namespace로 시작해 cache miss 후 같은 의존성을 설치·저장합니다.
3. warm: cold가 끝나 캐시를 저장한 뒤 새 Job에서 정확한 키를 복원하고 설치를 생략합니다.
4. `(baseline 준비 시간 − warm 준비 시간) ÷ baseline 준비 시간 × 100`을 개선율로 보고합니다.

Python 선택 후의 복원·설치 시간을 측정하며, 캐시 post-save는 준비 시간에서 제외하고 Job 전체 시간에는 포함합니다.
조건당 1회 관측이므로 러너·네트워크 변동이 있습니다. 전체 6개/9개 Matrix의 시간은 조건이 달라 직접 개선율로 비교하지 않습니다.
실제 warm 적중이 없거나 SHA·OS·Python·의존성이 다르면 비교를 실패로 처리합니다.

## 보안·기존 기능

- 캐시는 Python 도구 환경만 포함합니다. 배포 토큰은 Composite/Test에 전달하거나 캐시에 쓰지 않습니다.
- 기본 read 권한과 main Deploy의 제한적 write 권한을 유지합니다. 캐시 Job에 별도 개인 토큰을 추가하지 않습니다.
- Build 아티팩트를 Test/Deploy에서 내려받아 SHA-256·소스 SHA·경로를 확인하는 7주차 동작을 유지합니다.
- 기존 7주차 문서와 실행은 당시 6개 조합의 이력입니다. 최신 정의와 혼동하지 않습니다.

공식 근거: [Reusable Workflow](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows),
[Composite Action](https://docs.github.com/en/actions/tutorials/create-actions/create-a-composite-action),
[캐시](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching).
