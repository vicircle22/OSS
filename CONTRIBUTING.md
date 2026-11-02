# AI SUMMIT 기여 안내

이승원·이규호의 OSS기반SW프로그래밍 프로젝트입니다. main은 검토된 변경을 통합하는 브랜치로 유지합니다.
기획·와이어프레임과 실제 서비스 구현을 구분하고, 완료 여부는 실행·검증 근거로 판단합니다.

## 1. Feature 브랜치에서 시작

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/short-purpose
```

이번 4주차 실습은 `feature/` 브랜치를 사용합니다. 평소 작업 성격별 이름은
`feature/`(기능), `fix/`(오류), `docs/`(문서), `refactor/`(구조), `test/`(검증), `chore/`(기타)입니다.
한 브랜치·PR은 하나의 목적을 다룹니다. 다른 사람의 작업 브랜치를 덮어쓰지 않습니다.

## 2. Conventional Commits

형식: **`type(scope 선택)!선택: 변경 설명`**. 콜론 뒤 공백과 설명이 필요합니다.

| 타입 | 목적 | 예 |
|---|---|---|
| feat | 새 기능 | `feat(search): 태그 필터 추가` |
| fix | 오류 수정 | `fix: 빈 본문 입력 오류 수정` |
| docs | 문서 | `docs: 코드 리뷰 가이드 추가` |
| refactor | 동작을 유지하는 구조 개선 | `refactor(dora): 파싱 분리` |
| test | 테스트 | `test: 중복 URL 검증 추가` |
| ci / build | 자동화 / 빌드 | `ci: PR 검사 추가` |
| chore / style / perf / revert | 유지관리 / 형식 / 성능 / 되돌리기 | `chore: 설정 정리` |

호환성을 깨는 변경은 `feat(api)!: 응답 계약 변경`처럼 `!`를 쓰고 본문에 영향·대응을 적습니다.
허용 타입 목록은 팀 규칙이며 Conventional Commits 전체 명세가 이 목록만 허용한다는 뜻은 아닙니다.
PR 제목도 같은 형식으로 작성합니다. 자동 생성 merge commit은 일반 커밋 검사에서 제외합니다.

## 3. 검증하고 PR 만들기

Python 3.12 이상과 Git이 필요합니다. 현재 테스트는 표준 라이브러리만 사용합니다.

```bash
python3 -m unittest discover -s tests -v
git diff --check
git add <변경한-파일>
git commit -m "feat: 변경 목적"
git push -u origin feature/short-purpose
```

GitHub에서 main 대상 PR을 만들고 문제·변경·테스트 결과·한계·관련 Issue를 씁니다.
검토할 준비가 안 됐으면 Draft로 엽니다. 100~200줄은 작은 PR의 권장 가이드입니다.
새 검사기는 [PR #17](https://github.com/vicircle22/OSS/pull/17)에서 추가하며 병합 전에는 아래 파일이 main에 없습니다.

```bash
# PR #17 병합 후 사용. 커밋하기 전의 작업 파일은 이 검사에 포함되지 않습니다.
python3 scripts/collaboration/check_commits.py --base origin/main --head HEAD --title "feat: 변경 목적"
```

과거 main의 커밋을 다시 쓰지 않습니다. 이미 공유한 브랜치의 이력 수정이 필요하면 팀과 먼저 협의합니다.

## 4. 동료 리뷰와 병합

- 작성자 외 팀원에게 Review를 요청합니다. XAplus가 작성하면 vicircle22가, 반대면 XAplus가 검토합니다.
- `[MUST]` 필수 수정, `[SHOULD]` 권장 개선, `[NITS]` 사소한 지적으로 구분합니다.
- 작성자는 수정 커밋·테스트 결과로 답하고, 리뷰어는 최신 변경을 다시 확인합니다.
- 필수 지적 해결, 검사 결과, 동료 리뷰를 확인한 뒤 main으로 병합합니다.
- Squash를 사용하면 최종 커밋 제목도 Conventional Commits를 유지합니다.
- 자동 검사 성공은 동료 승인과 다릅니다. 작성자·AI 자체 점검을 다른 팀원 승인으로 기록하지 않습니다.

상세 리뷰 절차·예시는 [PR #18의 리뷰 가이드](https://github.com/vicircle22/OSS/pull/18/files)에 있습니다.
PR 템플릿과 CODEOWNERS는 main 병합 후 후속 PR에서 자동 적용 여부를 확인합니다.

## 5. 변경을 되돌릴 때

진행 중인 PR은 닫아 main을 유지할 수 있습니다. 병합된 변경은 되돌리기 PR로 검토합니다.
공유 main에 강제 push를 하지 않습니다. 되돌릴 대상·영향·검증 결과를 기록합니다.

## 6. 저장소 소유자가 설정할 수 있는 보호 규칙

현재 연결 계정 XAplus에는 저장소 관리 권한이 없어 보호 규칙을 적용하지 않았습니다.
소유자가 Settings의 Rules 또는 Branches에서 main을 대상으로 다음 설정을 검토합니다.

- PR을 통한 변경, 작성자 외 승인 최소 1명, 미해결 대화 해결 요구
- 새 커밋 후 이전 승인 무효화 여부 검토
- PR #17 병합 및 정상 실행 확인 후 실제 표시된 PR Quality 상태 검사를 필수로 선택
- 강제 push·브랜치 삭제 제한

이 목록은 **설정 제안**이며 실제 강제 적용 상태를 뜻하지 않습니다. CODEOWNERS만으로 병합이 차단되지는 않습니다.

공식 기준: [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow),
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
