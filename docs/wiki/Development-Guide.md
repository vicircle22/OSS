# Development Guide

[Home](https://github.com/vicircle22/OSS/wiki) · [Getting Started](https://github.com/vicircle22/OSS/wiki/Getting-Started) · [Troubleshooting](https://github.com/vicircle22/OSS/wiki/Troubleshooting)

## 저장소 구조와 구현 경계

| 경로 | 역할 |
|---|---|
| `docs/AI-SUMMIT-PRD.md` | 제품 범위·데이터 모델·API·분석 상태의 기획 |
| `docs/wireframes/index.html` | 설치 없는 브라우저 프로토타입 |
| `scripts/dora/`, `docs/dora/` | DORA 수집·보고서·예시와 측정 한계 |
| `scripts/collaboration/` | 커밋 헤더 검사와 비동기 보고서 도구 |
| `tests/` | 표준 라이브러리 기반 오프라인 회귀 테스트 |
| `.github/workflows/` | 실제로 등록된 GitHub Actions |
| `docs/wiki/` | 게시한 Wiki의 버전 관리 사본 |
| `docs/adr/` | 기술 결정의 배경·대안·결과 |
| `docs/automation/` | 아직 활성화하지 않은 비동기 자동화 초안 |

기획 문서가 존재한다고 Backend·DB·AI 연동이 구현된 것은 아닙니다. 범위는 [Getting Started](https://github.com/vicircle22/OSS/wiki/Getting-Started)와 실제 코드를 함께 확인합니다.

## GitHub Flow

작업 중인 파일이 없는지 확인한 뒤 시작합니다.

```bash
git status --short
git switch main
git pull --ff-only origin main
git switch -c feature/short-purpose
```

수정 → 테스트 → Conventional Commit → push → main 대상 PR 순서입니다.

```bash
python3 -m unittest discover -s tests -v
git diff --check
# 실제 수정한 경로로 바꿉니다.
git add -- '수정한-파일'
git commit -m "feat: 변경 목적"
git push -u origin feature/short-purpose
python3 scripts/collaboration/check_commits.py --base origin/main --head HEAD --title "feat: 변경 목적"
```

타입 예: `feat`, `fix`, `docs`, `refactor`, `test`, `ci`, `chore`. 선택 scope는 `fix(dora): ...` 형식이며 검사기는 영문·숫자·`._/-` 범위를 허용합니다.
검사기는 **커밋/PR 헤더**만 확인합니다. 동작·본문·footer·의미 버전의 타당성까지 보증하지 않습니다.
PR Quality는 제목 수정·새 커밋 등에서 검사합니다. 자동 검사 성공과 동료 승인은 구별합니다.

구체적인 협업 규칙은 [CONTRIBUTING](https://github.com/vicircle22/OSS/blob/main/CONTRIBUTING.md),
피드백은 [코드 리뷰 가이드](https://github.com/vicircle22/OSS/blob/main/docs/CODE_REVIEW.md)를 참고합니다.
이전 과제에서 사용자가 요청한 직접 병합 이력은 실제 기록대로 유지하며 동료 승인으로 바꾸어 쓰지 않습니다.

## 비동기 소통 규칙

- **Issue:** 재현할 버그, 담당·완료 기준이 있는 실행 작업. 논의 후 실제 작업을 Issue로 연결합니다.
- **PR:** 변경 파일·검증 결과·리뷰·피드백 반영.
- **Wiki:** 처음 시작·반복 실행·반복 질문의 답을 오래 보존.
- **ADR:** 오래 영향을 주는 기술 선택의 배경·대안·결정·결과.
- **Discussions:** 활성화 후 질문·아이디어·RFC 논의. 비활성 상태에서는 활성화·토론 완료라고 쓰지 않습니다.

메시지에는 **배경, 목적, 현재 상태, 기대/실제 결과, 시도한 방법, 필요한 결정, 응답 희망 시각(시간대)**을 포함합니다.
“이거 봐 주세요”만 반복하거나 즉답을 재촉하는 것은 충분한 맥락 제공이 아닙니다.
긴급 장애처럼 즉시 조율할 사안은 동기 소통을 쓰고, 결정과 후속 작업을 다시 기록합니다.

## SLA 제안과 주간 정리

초안 목표는 일반 Issue의 **작성자·봇을 제외한 첫 댓글까지 24시간(UTC 경과 시간, 주말 포함)**입니다.
팀 합의된 약속이 아니며, 업무시간 기준 SLA·PR 리뷰 응답은 별도 설계가 필요합니다.
봇 자동 응답은 사람의 응답으로 세지 않습니다. 초과 건은 문서·보고서에서 식별하며 누구에게도 자동 독촉하지 않습니다.

주간 요약에는 최근 7일 생성·종료 Issue, 답변 대기, SLA 초과, 진행 중 결정·다음 작업을 연결합니다.
[자동화 초안](https://github.com/vicircle22/OSS/tree/main/docs/automation)은 실행 중인 Workflow와 구별합니다.

## ADR와 문서 갱신

1. [ADR 템플릿](https://github.com/vicircle22/OSS/blob/main/docs/adr/0000-template.md)을 복사해 순번·짧은 이름으로 만듭니다.
2. 제안과 수락을 구분하고 검토 근거·대안·부작용·되돌릴 방법을 적습니다.
3. 실제 팀 합의가 생기면 날짜·논의 링크와 함께 상태를 바꿉니다. 합의를 만들어 쓰지 않습니다.
4. Wiki 수정 시 `docs/wiki/` 사본도 같은 내용으로 갱신합니다. 두 Git 저장소의 커밋을 기록합니다.

테스트가 실패하거나 인증·포트 문제가 생기면 [Troubleshooting](https://github.com/vicircle22/OSS/wiki/Troubleshooting)으로 이동합니다.
