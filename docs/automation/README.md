# 비동기 협업 자동화 초안

`async-collaboration.draft.yml`은 **.github/workflows 밖의 초안**입니다. 현재 예약·자동 댓글·주간 보고서를 실행하지 않습니다.
추가한 보고서 도구는 오프라인 테스트와 읽기 전용 실제 수집을 지원합니다.

## 설계

| 기능 | 초안 동작 | 권한 / 한계 |
|---|---|---|
| 자동 접수 | 일반 Issue opened 시 안내 댓글 | issues:write. 변수 ASYNC_AUTOMATION_ENABLED=true인 경우에만. 사람 응답으로 세지 않음 |
| SLA 추적 | 열린 일반 Issue의 최초 타인 댓글과 24시간 이상 응답 대기 식별 | issues:read. 본인·Bot·[bot] 제외. PR 리뷰·Discussions·DM은 제외 |
| 주간 요약 | 최근 7일 생성·종료와 현재 응답 대기 보고서 | 월요일 UTC 00:00/KST 09:00, 수동 실행, Issue·댓글 이벤트 |
| 결과 | Step Summary + Markdown/JSON 아티팩트 | 자동 라벨·담당자·독촉 변경 없음 |

24시간은 **합의 전 제안**, UTC 경과 시간이며 주말도 포함합니다. 업무시간 달력·휴가·담당자 로테이션은 아직 구현하지 않았습니다.
첫 응답은 해결 완료가 아닙니다. 봇 안내를 반복 발행하지 않도록 opened만 대상으로 하며,
자체 댓글 이벤트는 보고서만 갱신하고 다시 접수 댓글을 쓰지 않습니다. Workflow 수동 재실행에 대한 중복 댓글 방지는 추가 검토 대상입니다.

## 실제 수집을 수동으로 실행할 때

저장소 최상위에서 읽기 권한의 GITHUB_TOKEN을 환경변수로 준비하고 실행합니다. 값은 문서·로그·커밋에 쓰지 않습니다.

```bash
python3 -m scripts.collaboration.async_report --repo vicircle22/OSS --out /tmp/oss-async-report
```

API 오류·페이지 한도 오류는 실패로 전파되며 일부 결과를 정상 보고서처럼 발행하지 않습니다.
실제 수집 결과에는 공개 Issue 제목·URL·응답 시간만 기록합니다. 댓글 본문은 보고서에 복사하지 않습니다.

## 활성화 전 검토

1. 팀이 응답 목표·공개 범위·실행 빈도를 합의하고 [RFC 초안](../rfc/0001-async-response-policy.md)에 근거를 남깁니다.
2. [ADR](../adr/README.md)에 수락/유예를 기록합니다.
3. 초안을 `.github/workflows/async-collaboration.yml`로 옮긴 PR을 검토합니다.
4. 먼저 읽기 전용 보고서를 검증합니다. 자동 댓글은 별도 변수 설정 전까지 꺼 둡니다.
5. 봇 재실행 중복·API 제한·아티팩트 공개 범위를 확인한 뒤 필요한 기능만 활성화합니다.

공식 참고: [이벤트](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows),
[GitHub CLI와 Actions](https://docs.github.com/en/actions/using-workflows/using-github-cli-in-workflows).
