# 4주차 GitHub Flow · 코드리뷰 실습 기록

기록일: 2026-11-02 (Asia/Seoul). 저장소: [vicircle22/OSS](https://github.com/vicircle22/OSS).

**현재 상태: 작업 브랜치·Conventional Commits·PR 3개·AI 자체 리뷰·개선 반영 완료,
동료의 독립 리뷰와 병합은 대기 중.** 아래 자체 점검 3건을 동료 리뷰 3건 완료로 표시하지 않습니다.

## 요구사항과 증거

| 항목 | 상태 / 근거 |
|---|---|
| Feature 브랜치 전략 | 아래 세 브랜치를 기존 main에서 각각 생성. main 직접 수정 없음 |
| Conventional Commits | 모든 새 커밋과 PR 제목에 적용. 신규 커밋 범위 검사 CLI로 확인 |
| PR 생성 | #17, #18, #19 모두 main 대상 공개 PR |
| 최소 PR 3건 리뷰 | 서로 다른 3개 PR에 AI 보조 자체 COMMENT 등록. 동료 독립 리뷰는 별도 필요 |
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
세 PR 모두 vicircle22에게 리뷰 요청을 보냈으며, 아직 그 계정의 검토·승인을 기록하지 않았습니다.

## 검증 결과

- PR #17: DORA 기존 9개 + 신규 7개, 총 16개 unittest 통과.
- PR #17 최신 보완 커밋: [PR Quality 실행 #2 성공](https://github.com/vicircle22/OSS/actions/runs/41372485756).
- 새 코드가 없는 #18/#19는 Markdown 상대 링크·내용·whitespace를 확인하고 기존 테스트를 검증.
- 세 변경을 합친 **로컬 전용 통합 브랜치**에서 16개 테스트와 커밋 범위·제목 검사를 통과.
- 기존 기획·와이어프레임·DORA 구현 파일은 수정하지 않음. 이번 과제는 제품 기능 전체 구현·배포를 뜻하지 않음.

## 동료가 이어서 할 일

1. vicircle22가 각 PR의 Files changed와 검증 근거를 실제로 확인한다.
2. 발견한 문제·개선에 `[MUST]`·`[SHOULD]`를 붙여 Review를 제출한다.
   문제가 없으면 확인한 근거를 남기며, 존재하지 않는 결함을 만들지 않는다.
3. 지적이 있으면 작성자가 수정하고 리뷰어가 최신 커밋을 재검토한다.
4. 필요한 리뷰 수가 개인별인지 팀 합계인지 수업 기준으로 확인한다. 필요하면 서로 작성한 PR을 교차 검토한다.
5. 검증·필수 지적 해결·동료 리뷰 후 #17 → #18 → #19 순으로 병합하는 것을 권장한다.
   현재 세 PR은 독립 분기이므로 순서 자체가 기술적 의존성은 아니다.
6. 선택 보호 규칙과 템플릿·CODEOWNERS의 후속 PR 자동 적용을 소유자가 확인한다.

제출 URL은 이 기록 또는 PR 목록을 사용할 수 있으나, **동료 리뷰 대기 상태를 완료로 바꾸어 제출하지 않는다.**
병합 후 이 기록의 동료 리뷰·결과 링크와 상태를 실제 사실에 맞게 갱신한다.
