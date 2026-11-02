# 4주차 GitHub Flow · 코드리뷰 실습 기록

기록일: 2026-11-02 (Asia/Seoul). 저장소: [vicircle22/OSS](https://github.com/vicircle22/OSS).

**진행 방식: 사용자의 명시적 요청으로 동료 리뷰 요청을 취소하고 PR #17 → #18 → #19를 main에 직접 병합합니다.**
작업 브랜치·Conventional Commits·AI 자체 리뷰·개선 반영 기록은 보존합니다. 아래 자체 점검 3건은 동료 리뷰 3건 완료를 뜻하지 않습니다.

## 요구사항과 증거

| 항목 | 상태 / 근거 |
|---|---|
| Feature 브랜치 전략 | 아래 세 브랜치를 기존 main에서 각각 생성. main 직접 수정 없음 |
| Conventional Commits | 모든 새 커밋과 PR 제목에 적용. 신규 커밋 범위 검사 CLI로 확인 |
| PR 생성 | #17, #18, #19 모두 main 대상 공개 PR |
| 최소 PR 3건 리뷰 | 서로 다른 3개 PR에 AI 보조 자체 COMMENT 등록. 동료 독립 리뷰 기록은 없으며 사용자 요청으로 리뷰 요청 취소 |
| MUST/SHOULD 태그 | 아래 Review 링크에 필수 확인·권장 개선·검증 근거 기록 |
| 피드백 반영 | 범위 안내·검증 사례 항목·안전한 명령 예제 보완 커밋 연결 |
| 선택 PR 템플릿·리뷰 문서 | PR #18, CONTRIBUTING은 PR #19 |
| 선택 CODEOWNERS | PR #19. main 병합 후 후속 PR에서 자동 요청 확인 필요 |
| 선택 브랜치 보호 | 미적용. XAplus는 admin 권한이 없어 소유자 설정 안내만 작성 |

## PR · 리뷰 · 개선 반영

| PR / 브랜치 | 자체 리뷰 | 권장 개선 반영 |
|---|---|---|
| [#17 커밋·PR 검사](https://github.com/vicircle22/OSS/pull/17) · `feature/conventional-commit-check` | [MUST/SHOULD 리뷰](https://github.com/vicircle22/OSS/pull/17#pullrequestreview-5731225499) | [검사 범위를 헤더로 명시](https://github.com/vicircle22/OSS/commit/4f5949f98af55b147b01f082836e5a43dd99240a) |
| [#18 템플릿·리뷰 가이드](https://github.com/vicircle22/OSS/pull/18) · `feature/pr-review-template` | [MUST/SHOULD 리뷰](https://github.com/vicircle22/OSS/pull/18#pullrequestreview-5731225779) | [정상·경계·실패 사례 항목 추가](https://github.com/vicircle22/OSS/commit/91b1d98be520ff55c41e068eafb5504f85ea9723) |
| [#19 기여 안내·담당자](https://github.com/vicircle22/OSS/pull/19) · `feature/contributor-guide` | [MUST/SHOULD 리뷰](https://github.com/vicircle22/OSS/pull/19#pullrequestreview-5731226199) | [명령 예제의 파일명 인용](https://github.com/vicircle22/OSS/commit/96d953b29577796a815287cc80d107381fb2cd26) |

위 Review는 모두 작성자 XAplus 계정의 **AI 보조 자체 점검(Comment)**입니다.
세 PR 모두 vicircle22에게 보냈던 리뷰 요청을 사용자 지시에 따라 취소했습니다. 그 계정의 검토·승인은 기록하지 않았습니다.

## 검증 결과

- PR #17: DORA 기존 9개 + 신규 7개, 총 16개 unittest 통과.
- PR #17 최신 보완 커밋: [PR Quality 실행 #2 성공](https://github.com/vicircle22/OSS/actions/runs/41372485756).
- 새 코드가 없는 #18/#19는 Markdown 상대 링크·내용·whitespace를 확인하고 기존 테스트를 검증.
- 세 변경을 합친 **로컬 전용 통합 브랜치**에서 16개 테스트와 커밋 범위·제목 검사를 통과.
- 기존 기획·와이어프레임·DORA 구현 파일은 수정하지 않음. 이번 과제는 제품 기능 전체 구현·배포를 뜻하지 않음.

## 병합 방식과 후속 확인

- 이번 실행은 사용자 지시에 따라 동료 리뷰를 기다리지 않고 세 PR을 순서대로 병합합니다.
- #17과 #18은 병합되었으며, 이 기록은 #19와 함께 main에 반영됩니다. 각 PR 링크에서 실제 병합 시각·커밋을 확인할 수 있습니다.
- 일반 협업 가이드의 동료 리뷰 권장은 유지하되, 이번 직접 병합이 동료 승인을 받았다는 뜻은 아닙니다.
- 선택 보호 규칙은 미적용 상태이며 CODEOWNERS·템플릿의 후속 PR 자동 적용은 별도 확인 대상입니다.

병합 후 기록 URL: https://github.com/vicircle22/OSS/blob/main/docs/Week4-Submission.md
