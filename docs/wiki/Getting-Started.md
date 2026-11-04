# Getting Started

[Home](https://github.com/vicircle22/OSS/wiki) · [Development Guide](https://github.com/vicircle22/OSS/wiki/Development-Guide) · [Troubleshooting](https://github.com/vicircle22/OSS/wiki/Troubleshooting)

## 목표와 현재 상태

AI SUMMIT은 AI 관련 자료 저장·구조화 요약·Action Item 관리를 목표로 하는 학기 프로젝트입니다.
현재 실행할 수 있는 것은 **브라우저 와이어프레임**, **DORA 수집·예시 보고서**, **PR 품질 검사**입니다.
Spring Boot·PostgreSQL·실제 LLM·로그인·공개 배포는 아직 기획입니다. 아래 시작 절차에 Java·DB·AI 키는 필요하지 않습니다.

## 준비물

- Git과 최신 브라우저
- Python **3.12 이상**. `python3`가 없으면 설치 상태를 확인하고 Windows에서는 `py -3` 또는 `python`을 사용합니다.
- 코드 읽기·로컬 테스트는 공개 저장소 접근만 있으면 됩니다. push·Wiki 수정은 저장소 쓰기 권한이 필요합니다.

```bash
git --version
python3 --version
git clone https://github.com/vicircle22/OSS.git
cd OSS
```

이미 내려받았다면 새로 clone하지 말고 작업 파일을 확인한 뒤 `git fetch origin`으로 원격 상태를 확인합니다.
작성 중인 파일이 있으면 보존한 후 브랜치를 바꿉니다. 자세한 과정은 [Development Guide](https://github.com/vicircle22/OSS/wiki/Development-Guide)를 따릅니다.

## 1. 테스트로 환경 확인

저장소 최상위, 즉 `README.md`, `scripts`, `tests`가 있는 폴더에서 실행합니다.

```bash
python3 -m unittest discover -s tests -v
```

기존 DORA 9개와 커밋 검사 7개가 기준선입니다. 이번 과제로 추가된 비동기 보고서 테스트가 있으면 함께 실행됩니다.
실제 테스트 수·실패 메시지는 현재 실행 결과를 기준으로 기록합니다. Python 외부 패키지 설치는 필요 없습니다.

## 2. 와이어프레임 열기

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory docs
```

브라우저에서 **http://127.0.0.1:8765/wireframes/** 를 엽니다. 종료는 실행 터미널에서 `Ctrl+C`입니다.

확인할 흐름:

1. 목록에서 자료 열기 → 요약·원문·행동 탭 전환
2. 저장 화면에서 URL 또는 본문 등록 → 데모 분석 상태 확인
3. 행동 완료·취소 → 상세와 전체 행동의 진행 수 확인
4. Desktop/Mobile·오류 상태 예시 확인

이 화면은 **메모리 기반 데모**입니다. 새로고침하면 초기화되고 실제 URL 수집·LLM 호출·DB 저장은 하지 않습니다.
입력 자료 대신 예시 텍스트로 검토하세요. 링크 수집 실패나 입력 조건은 [Troubleshooting](https://github.com/vicircle22/OSS/wiki/Troubleshooting)을 참고합니다.

## 3. 네트워크 없이 DORA 예시 생성

별도 터미널을 열고 저장소 최상위에서 실행합니다. 기존 추적 파일에 덮어쓰지 않고 임시 출력 폴더를 사용합니다.

```bash
python3 scripts/dora/collect.py --fixture scripts/dora/example.json --out /tmp/oss-dora-preview
python3 -m http.server 8766 --bind 127.0.0.1 --directory /tmp/oss-dora-preview
```

브라우저: **http://127.0.0.1:8766/**. `metrics.json`, `report.md`, `dashboard.svg`, `index.html`이 생성됩니다.
Windows에서는 `/tmp/oss-dora-preview` 대신 `%TEMP%` 또는 실제 임시 폴더 경로를 사용합니다.
**예시 데이터이며 실제 성과가 아닙니다.** 실측·대리지표의 정의와 권한은 [DORA 안내](https://github.com/vicircle22/OSS/blob/main/docs/dora/README.md)에 있습니다.

## 다음 문서

- 코드를 수정하려면 [Development Guide](https://github.com/vicircle22/OSS/wiki/Development-Guide)
- 오류가 나면 [Troubleshooting](https://github.com/vicircle22/OSS/wiki/Troubleshooting)
- 요구사항은 [PRD](https://github.com/vicircle22/OSS/blob/main/docs/AI-SUMMIT-PRD.md)

검토 기준일: 2026-11-04. 코드가 바뀌면 실행 명령과 문서도 같은 PR에서 갱신합니다.
