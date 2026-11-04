# 5주차 비동기 협업 체계 구축 · 제출 기록

실행일: 2026-11-04 (Asia/Seoul). 대상: [vicircle22/OSS](https://github.com/vicircle22/OSS).

## 제출 URL

**https://github.com/vicircle22/OSS/wiki**

| 필수 문서 | 실제 게시 URL | 주요 내용 |
|---|---|---|
| Getting Started | https://github.com/vicircle22/OSS/wiki/Getting-Started | 준비물·첫 테스트·프로토타입 실행·DORA 예시 |
| Development Guide | https://github.com/vicircle22/OSS/wiki/Development-Guide | 구조·GitHub Flow·비동기 기록·응답 목표·ADR |
| Troubleshooting | https://github.com/vicircle22/OSS/wiki/Troubleshooting | 환경·포트·입력·메트릭·인증·커밋 검사 문제 해결 |

세 문서 모두 나머지 두 문서를 링크합니다. Home·사이드바·푸터에서도 접근합니다.
실제 Wiki Git에 게시했으며 일반 저장소의 Markdown만으로 대체하지 않았습니다.

## 필수·선택 항목 상태

| 항목 | 결과 |
|---|---|
| Wiki 최소 3문서 | 3문서 + Home 게시 |
| 상호 링크 | 각 문서에서 나머지 두 문서와 Home 연결 |
| 선택 ADR | [템플릿·목록·이번 과제 적용 기록](adr/) 작성 |
| 선택 자동화 초안 | [자동접수·SLA·주간 요약 YAML와 안내](automation/) 작성. .github/workflows 밖에 보관해 비활성 |
| 응답 보고서 도구 | 일반 Issue의 첫 타인 댓글·대기·주간 생성/종료를 읽기 전용 수집 |
| 선택 Discussions | **사용자 선택으로 제외**. 활성화·카테고리 생성·토론 게시를 수행하지 않음 |
| RFC 정책 문서 | [설계 보조 초안](rfc/0001-async-response-policy.md)만 보존. 실제 토론·팀 합의로 표시하지 않음 |

## 게시·버전 관리 근거

- Wiki 게시 커밋: `20d12a8` (첫 Home 초기화 후 세 문서·사이드바·푸터 추가)
- Wiki 이력: 각 문서의 revision 링크 및 `https://github.com/vicircle22/OSS.wiki.git`
- 코드 저장소에는 [동일 문서 사본](wiki/)을 보존하고, 게시한 Wiki와 파일 내용을 대조함
- 기존 PRD·와이어프레임·DORA 구현은 유지함

## 실행 검증

- unittest **21개 통과**: 기존 16개 + 비동기 보고서 5개.
- 새 테스트: 작성자·봇 응답 제외, 첫 타인 응답의 시간순/UTC 변환, 오래된 열린 Issue 포함, 주간 경계·종료·PR 제외, 출력 이스케이프·예시 표시·잘못된 SLA.
- DORA fixture 실행: 임시 폴더에 JSON·Markdown·SVG·HTML 4개 생성. 기존 예시 파일에 덮어쓰지 않음.
- Wiki 안내의 로컬 HTTP 서버로 와이어프레임 경로를 확인함.
- 초안 YAML 파싱·자동응답 opt-in 조건·비활성 위치 확인.
- 문서 상대 링크·Wiki 상호 링크·사본 일치·whitespace 확인.

추가 읽기 전용 실행의 시점별 결과:

- 수집 시각: `2026-11-04T01:15:05.017576Z`
- 일반 열린 Issue 12개, 작성자·봇을 제외한 첫 타인 댓글 대기 12개.
- 제안한 24시간 경과 시간 기준 대기 초과 12개. 최근 7일 생성 0개·종료 0개.
- 이는 **Issue 기록의 응답 상태**이며 팀원의 태도·실제 업무·서비스 장애·DORA 성과를 평가하는 값이 아님.
- 수집은 댓글·라벨·담당자를 변경하지 않음. 과제에서 요구한 자동화는 초안이며 예약 실행·자동응답을 켜지 않음.

## 적용 범위

Spring Boot·DB·실제 LLM·공개 서비스 배포가 구현되었다는 뜻은 아닙니다.
24시간 응답 목표는 합의 전 제안이며 주말 포함 UTC 경과 시간입니다. 동료의 의견·승인·토론 기록을 만들지 않았습니다.
Canvas에는 위 Wiki URL을 제출할 수 있습니다. 이 작업에서 LMS의 과제 제출 버튼을 누르지는 않았습니다.
