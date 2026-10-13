# 3주차 — GitHub Projects 계획·추적 체계

기존 AI SUMMIT PRD와 와이어프레임, 16주 마일스톤을 사용한 개발 백로그다. 서비스 구현을 완료했다는 의미가 아니다.

## 제출용 링크

- [칸반 프로젝트](https://github.com/users/XAplus/projects/5)
- [백로그 이슈 목록](https://github.com/vicircle22/OSS/issues)
- [기존 주차 마일스톤](https://github.com/vicircle22/OSS/milestones?sort=title&direction=asc)
- [Bug report 템플릿](../.github/ISSUE_TEMPLATE/bug.yml)
- [Feature request 템플릿](../.github/ISSUE_TEMPLATE/feature.yml)
- [프로젝트 PRD](AI-SUMMIT-PRD.md)

프로젝트는 현재 작업 계정 XAplus 소유이며 OSS 저장소의 실제 이슈를 연결했다. 저장소 소유자 vicircle22와 달라 저장소의 Projects 목록 연결에는 소유자 제약이 있다. 위 프로젝트 URL을 직접 사용한다. 공개 여부는 프로젝트 Settings에서 확인한다.

## 칸반 운영 규칙

| 상태 | 진입 조건 | 다음 상태로 옮길 근거 |
|---|---|---|
| Backlog | PRD 근거·우선순위·마일스톤·인수 조건이 있는 작업 후보 | 선행 조건 확인 및 스프린트 선택 |
| To Do | 스프린트에 선택했고 착수할 수 있는 작업 | 담당자가 실제 작업을 시작함 |
| In Progress | 실제 수행 중인 작업, WIP 3개 이하 | PR·검증 결과를 제출함 |
| Review | 변경과 검증 근거를 검토 중 | 인수 조건 통과와 병합 또는 산출물 승인 |
| Done | 검토와 완료 기준을 충족한 작업 | 이슈를 닫고 근거를 보존함 |

보드에 모든 상태를 설정하되 아직 발생하지 않은 진행 상태나 완료를 만들지 않는다. 후속 구현은 Backlog에 둔다. 실제 작업 중인 보드 구성·템플릿 작업은 진행 또는 검토 단계에 표시하고, 완료 근거가 확보되면 닫는다.

## 라벨 체계

기존 `bug` / `enhancement` / `documentation` 라벨을 그대로 사용한다.

| 분류 | 라벨 | 용도 |
|---|---|---|
| 우선순위 | `priority: P0`, `priority: P1` | MVP 필수 / 핵심 흐름 검증 후 확장 |
| 영역 | `area: docs`, `area: backend`, `area: frontend`, `area: ai`, `area: qa` | 담당 기술 영역·문서·검증 |
| 스프린트 | `sprint: 01`, `sprint: 02` | 3주차 설계 / 4주차 Backend 기반 |

Bug 템플릿은 재현 절차·기대/실제 결과·환경·영향·회귀 검증을 요구하고 `bug`를 붙인다. Feature 템플릿은 사용자 가치·PRD 근거·완료 조건·의존성·추정·검증 계획을 기록하고 `enhancement`를 붙인다. 라벨의 priority/area/sprint와 기존 마일스톤은 등록 후 선택한다.

## 스프린트와 마일스톤

| 스프린트 | 기존 마일스톤 | 선택한 작업 | 초안 points |
|---|---|---|---:|
| Sprint 01 — 설계 | 03주차 · 시스템 설계, ERD 및 API 계약 | #2~#6: 운영 체계·템플릿·ERD·API·분석 계약 | 13 |
| Sprint 02 — 기반 | 04주차 · Spring Boot 구축 및 PostgreSQL 연결 | #7~#8: Spring Boot·DB migration | 6 |
| 후속 Backlog | 기존 05~14주차 마일스톤 | #9~#15: 콘텐츠·화면·AI·행동·검색·검증 | 33 |

기존 16개 마일스톤을 변경하지 않고 재사용했다. 실제 달력 시작일과 작업자 배분은 팀 합의 사항이므로 임의 날짜나 다른 구성원의 담당을 지정하지 않는다. 스프린트 종료 시 완료 기준을 충족한 이슈만 닫고, 미완료는 근거를 남긴 뒤 다음 계획으로 이동한다.

## 등록된 백로그

전체 14개, 상대 추정 52 points. 추정값은 팀 합의 전 초안이다.

| 이슈 | 작업 | 기존 주차 마일스톤 | points |
|---|---|---:|---:|
| [#2](https://github.com/vicircle22/OSS/issues/2) | 3주차 GitHub Projects 계획·추적 체계 구성 | 03주차 | 2 |
| [#3](https://github.com/vicircle22/OSS/issues/3) | Bug·Feature 이슈 템플릿과 백로그 운영 안내 추가 | 03주차 | 2 |
| [#4](https://github.com/vicircle22/OSS/issues/4) | PRD 데이터 모델 기반 ERD 확정 | 03주차 | 3 |
| [#5](https://github.com/vicircle22/OSS/issues/5) | REST API 요청·응답·오류 계약 확정 | 03주차 | 3 |
| [#6](https://github.com/vicircle22/OSS/issues/6) | 분석 상태 전이와 LLM 응답 JSON 계약 확정 | 03주차 | 3 |
| [#7](https://github.com/vicircle22/OSS/issues/7) | Spring Boot 프로젝트와 기본 health endpoint 구축 | 04주차 | 3 |
| [#8](https://github.com/vicircle22/OSS/issues/8) | PostgreSQL 연결과 DB migration 구축 | 04주차 | 3 |
| [#9](https://github.com/vicircle22/OSS/issues/9) | URL·텍스트 콘텐츠 CRUD 및 중복 검사 구현 | 05주차 | 5 |
| [#10](https://github.com/vicircle22/OSS/issues/10) | 기존 와이어프레임 기반 React 네 화면 구현 | 06주차 | 5 |
| [#11](https://github.com/vicircle22/OSS/issues/11) | LLM API 연결과 비동기 분석·재시도 구현 | 08주차 | 5 |
| [#12](https://github.com/vicircle22/OSS/issues/12) | 구조화 요약·태그 생성 및 결과 검증 구현 | 09주차 | 5 |
| [#13](https://github.com/vicircle22/OSS/issues/13) | Action Item 생성·완료·취소·편집·삭제 구현 | 11주차 | 5 |
| [#14](https://github.com/vicircle22/OSS/issues/14) | 검색·카테고리·태그·상태 필터와 페이지 탐색 구현 | 13주차 | 3 |
| [#15](https://github.com/vicircle22/OSS/issues/15) | 핵심 사용자 흐름·접근성·실패 복구 검증 | 14주차 | 5 |

## 선택 과제 — 기본 분석과 기준선

- Cycle Time: In Progress 최초 진입부터 Done까지의 시간. 중단·재개 정책은 팀 합의 후 기록한다. 아직 완료된 실제 구현 작업의 이력이 없어 대표 Cycle Time은 미측정이다.
- Velocity: 한 스프린트 내 완료 기준을 충족한 이슈의 Estimate 합계. 스프린트 기간 확정·종료 전에는 최종 Velocity로 보고하지 않는다.
- Burndown: 초기 스프린트 points에서 누적 완료 points를 뺀 남은 작업량. 범위 추가/제외는 별도 기록한다.

현재 계획 기준선은 Sprint 01=13, Sprint 02=6, 후속 Backlog=33 points다. 미구현 기능에 가짜 완료 이력을 넣지 않는다. 운영 체계·템플릿 산출물 완료가 확인되면 해당 4 points만 완료로 반영하고 Sprint 01 잔여 9 points를 추적한다. GitHub Insights와 보드의 상태별 Count/Estimate 합계로 진행 상황을 확인한다.

## 제출 화면

1. 프로젝트 전체 칸반: 5개 상태 컬럼과 실제 이슈 카드.
2. Backlog Register: 이슈·라벨·Estimate·기존 마일스톤 연결.
3. Sprint 01/Sprint 02 필터 또는 라벨로 구분한 스프린트 계획.
4. New issue에서 Bug report / Feature request 양식 선택 화면.

## 보존 및 복원

- 원래 main: `0b8afa314d2113aa2b3882d000d3632ed75bf6f9`.
- [백업 브랜치](https://github.com/vicircle22/OSS/tree/backup/pre-projects-20261013-0b8afa3): `backup/pre-projects-20261013-0b8afa3`.
- [백업 태그](https://github.com/vicircle22/OSS/tree/backup-pre-projects-20261013-0b8afa3): `backup-pre-projects-20261013-0b8afa3`.
- 저장소 변경은 새 `.github/ISSUE_TEMPLATE/*` 파일과 이 문서 추가로 한정한다. 기존 PRD·와이어프레임·DORA 코드와 README 내용은 보존한다.
- Git 스냅샷은 Projects·이슈·라벨을 저장하지 않는다. 이 작업 전 라벨·마일스톤·이슈 목록은 별도 기록하고, 기존 보드는 변경하지 않았다.
- 파일 변경을 취소하려면 이 작업 PR의 squash 커밋을 revert한다. 새 보드·이슈·라벨은 별도 관리 대상이며 임의 삭제하지 않는다.
