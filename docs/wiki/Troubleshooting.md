# Troubleshooting

[Home](https://github.com/vicircle22/OSS/wiki) · [Getting Started](https://github.com/vicircle22/OSS/wiki/Getting-Started) · [Development Guide](https://github.com/vicircle22/OSS/wiki/Development-Guide)

문제를 남길 때 **증상 → 재현 → 기대/실제 → 환경 → 시도 → 결과**를 적습니다.
로그의 토큰·API 키·개인정보는 제거합니다. 저장소 파일을 덮어쓰거나 공유 이력을 강제로 바꾸기 전에 원인을 확인합니다.

## Python 명령을 찾지 못함

- 원인: Python 미설치 또는 명령 이름 차이.
- 해결: `python3 --version`으로 3.12 이상인지 확인합니다. Windows는 `py -3 --version` 또는 `python --version`을 확인하고 문서의 명령을 해당 이름으로 바꿉니다.
- 검증: 저장소 최상위에서 `python3 -m unittest discover -s tests -v` 실행.

## No module named scripts / 테스트가 0개임

- 원인: 저장소 최상위가 아닌 폴더에서 실행하거나 다른 Python 환경을 사용함.
- 해결: `README.md`, `scripts`, `tests`가 있는 `OSS` 폴더로 이동합니다. 테스트는 파일 하나 직접 실행 대신 discover 명령을 사용합니다.
- 검증: DORA·커밋 검사 등의 테스트 이름과 실행 수를 확인합니다. `Ran 0 tests`를 검증 완료로 기록하지 않습니다.

## Address already in use / 미리보기가 열리지 않음

- 원인: 8765 포트를 다른 프로그램이 사용하거나 로컬 서버가 종료됨.
- 해결: 자신이 띄운 서버라면 해당 터미널에서 `Ctrl+C`로 종료합니다. 다른 프로그램을 임의 종료하지 말고 8767 등 다른 포트를 사용합니다.

```bash
python3 -m http.server 8767 --bind 127.0.0.1 --directory docs
```

- 검증: **http://127.0.0.1:8767/wireframes/** 로 접속합니다. 포트를 바꿨다면 브라우저 주소도 함께 바꿉니다.
- 404라면 `--directory docs`가 있는지, 실행한 위치가 저장소 최상위인지 확인합니다.

## 새로고침 후 저장·행동 상태가 사라짐

- 원인: 현재 와이어프레임은 브라우저 메모리 기반 프로토타입입니다.
- 해결: 재현에 예시 데이터를 사용하고 결과 화면을 남깁니다. 이 단계에는 DB 저장·새로고침 영속성이 없습니다.
- 검증: 새로고침 전 데모 안에서 목록·상세·행동 화면의 진행 수가 일치하는지 확인합니다. 실제 서비스의 영속화 요구는 PRD와 구분합니다.

## URL 수집이 안 됨 / 본문 입력 오류

- 원인: 데모에는 외부 본문 수집이 없으며, 입력 조건과 중복 검사가 있습니다.
- 해결: 공개 http/https URL을 사용하고 텍스트는 공백 제거 후 **100~20,000자**, 제목 **120자**, 태그 **최대 5개·각 20자** 조건을 확인합니다.
- 검증: 짧은 본문 오류 시 입력이 유지되는지, 이미 저장한 URL의 안내에서 기존 자료로 이동하는지 확인합니다.
- 백엔드 URL 수집·SSRF 방어·실제 API 오류 처리는 향후 구현 검증 대상입니다.

## DORA가 데이터 없음 또는 null

- 원인: 대상 환경의 성공 배포·연결 장애 기록이 없거나 조회 권한·환경 이름이 다름.
- 해결: `production` 또는 `DORA_ENVIRONMENT`와 GitHub Deployments의 실제 이름을 대조합니다. 장애 연결은 실제 `incident` Issue의 `deployment_id`를 확인합니다.
- 검증: 실행 Summary의 표본 수·주의사항과 아티팩트의 `metrics.json`을 확인합니다. 기록이 없다고 가짜 배포·장애를 만들지 않습니다.
- 예시를 보려면 [Getting Started](https://github.com/vicircle22/OSS/wiki/Getting-Started)의 fixture 명령을 사용합니다. 예시를 실측으로 제출하지 않습니다.

## API 401/403/404/429

- 원인 후보: 로그인·저장소 접근 권한, 토큰 범위, API 제한, 없는 리소스.
- 해결: 로그인 계정과 저장소 권한을 확인하고 Actions의 읽기 권한을 확인합니다. 실패 로그의 상태 코드와 발생 시각을 남깁니다. 읽기 오류를 해결하려고 불필요한 쓰기·관리 권한을 부여하지 않습니다.
- 검증: 같은 명령을 필요한 권한으로 다시 실행하고 성공 여부를 확인합니다. 실제 토큰 값은 Issue·Wiki·화면 캡처에 포함하지 않습니다.

## PR Quality 실패 / cannot read the revision range

- 원인: `Update` 같은 제목·커밋, 허용하지 않은 타입·빈 설명, 또는 base/head 이력이 없는 얕은 clone.
- 해결: [Development Guide](https://github.com/vicircle22/OSS/wiki/Development-Guide)의 형식을 확인합니다. 얕은 clone이면 `git fetch --unshallow origin`, 일반 clone이면 `git fetch origin`으로 이력을 확보합니다.
- 검증: `python3 scripts/collaboration/check_commits.py --base origin/main --head HEAD --title "docs: 문서 개선"`와 테스트를 실행합니다. 이미 공유한 커밋의 이력 수정은 팀과 협의합니다.

## Wiki clone 실패 / repository not found

- 원인: Wiki 첫 페이지가 아직 생성되지 않았거나 주소·접근 권한이 잘못됨.
- 해결: GitHub의 Wiki 화면에서 첫 페이지가 있는지 확인합니다. Wiki는 일반 저장소와 별도로 `https://github.com/vicircle22/OSS.wiki.git`를 clone합니다.
- 검증: Wiki 저장소의 기본 브랜치에 push한 문서가 브라우저에서 보이는지 확인합니다. 일반 저장소에 Markdown을 넣는 것만으로 Wiki 게시가 되지는 않습니다.

## Discussions 탭이 없거나 설정 권한이 없음

- 원인: Discussions 미활성화 또는 현재 계정의 저장소 옵션 권한 부족.
- 해결: 권한이 있는 소유자에게 Settings → General → Features의 Discussions 설정을 요청합니다.
  그동안 RFC·카테고리 설계 초안은 저장소 문서에 보존합니다. 비활성화 상태를 운영 완료로 표시하지 않습니다.
- 검증: 실제 Discussions 탭·카테고리·토론 URL이 생겼는지 확인합니다.

반복 문제가 해결되면 이 문서를 갱신하고 [Home](https://github.com/vicircle22/OSS/wiki)과 관련 Issue/PR에 연결합니다.
