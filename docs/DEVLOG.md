# 개발 로그

최신 기록이 위에 옵니다. 새 기록은 "로그" 맨 위에 날짜, 커밋, 한 일, 결과 순서로 추가합니다.
프로젝트 개요는 [CONCEPT.md](CONCEPT.md)를 봅니다.

## 현재 상태 (2026-10-14)

| 항목 | 상태 |
|---|---|
| 배포 주소 | https://webgl3ddata.vercel.app/ |
| 배포본 내용 | upstream `keni2r/webgl3ddata`의 `67deeef`와 일치 (Babylon.js 라벨 버전) |
| 작업 저장소 | origin `Kenistark/webgl3ddata` main `8c44627` + 이번 정리 작업(미커밋) |
| 메인 뷰어 | Three.js 0.160.0 |
| 등록 모델 | JadeToad.glb, Breather / SCBA (scene.gltf) |

**배포 반영 경로 확인 필요.** 배포본은 upstream의 최신 커밋과 파일 위치까지 일치합니다.
origin에만 있는 10월 14일 커밋들은 아직 배포되지 않았습니다. Vercel 프로젝트가 어느 저장소에 연결돼 있는지는 Vercel 대시보드에서 확인해야 합니다.

## 알려진 문제

| 상태 | 문제 | 근거 | 해결 방향 |
|---|---|---|---|
| 해결 (미커밋) | JadeToad.glb를 `source/model/`로 옮긴 뒤에도 코드가 `./JadeToad.glb`를 불러와 404. 기본 화면이 빈 채로 뜸 | 로컬 서버에서 재현 | 모델 경로를 `MODEL_URLS` 한곳에서 관리 |
| 미해결 | 모델을 빠르게 연속 전환하면 이전 요청의 모델이 뒤늦게 추가되어 두 개가 겹쳐 보임 | 로컬 서버에서 재현 | 요청마다 번호를 매기고 오래된 요청의 결과는 버림 |
| 미해결 | "모두 함께 보기"에서 하나가 실패해도 나머지는 뒤늦게 추가되고, 카메라는 초기화되지 않음 | 경로 수정 전 재현 | `Promise.allSettled`로 결과를 모은 뒤 배치 |
| 미해결 | 실패 시 항상 "로컬 웹 서버에서 실행하라"고 안내함. 서버에서 404가 난 경우에도 같은 문구 | 로컬 서버에서 확인 | 실패한 파일 경로와 상태 코드를 표시 |
| 미해결 | 모델을 바꿀 때 geometry, material, texture를 해제하지 않음. 전환을 반복하면 GPU 메모리가 늘 수 있음 | 코드 확인, 측정은 안 함 | 제거 시 `dispose()` 호출 |
| 미해결 | 모바일 폭(375px)에서 290px 고정 컨트롤 패널이 화면 대부분을 가림 | 모바일 에뮬레이션에서 확인 | 패널 접기 버튼 또는 하단 시트 |
| 미해결 | 글꼴로 Pretendard를 지정했지만 불러오는 코드가 없어 시스템 글꼴로 대체됨 | 코드 확인 | 웹폰트 링크 추가 또는 지정 제거 |
| 확인 필요 | Breather 모델은 SKETCHFAB Standard 라이선스. 공개 저장소와 공개 배포에 원본 파일을 둬도 되는지 불명확 | 모델 메타데이터 | 약관 확인. 안 되면 비공개 처리 또는 교체 |
| 참고 | Breather는 cm 단위로 제작되어 glTF 기준 높이가 약 112m. 뷰어가 크기를 정규화해서 화면에는 문제없음 | `tools/inspect_model.py` | 다른 엔진에서 열 때 스케일 주의 |

## 로그

### 2026-10-14 · 미커밋 · 프로젝트 분석과 구조 정리

- 전체 커밋 히스토리, 현재 뷰어 코드, 두 모델 파일 내부 구조를 분석했다.
- 로컬 서버와 배포 사이트에서 실제 동작을 확인했다. 위 "알려진 문제" 표가 그 결과다.
- `scene.gltf`, `scene.bin`을 `source/model/breather/`로 옮겼다. 모든 모델을 `source/model/` 아래로 모으고, 여러 파일로 된 glTF는 모델별 폴더로 묶는 규칙을 정했다.
- `index.html`의 모델 경로를 `MODEL_URLS` 한곳에서 관리하도록 바꿨다. JadeToad 404가 해결되어 세 가지 보기 모드가 모두 로드된다.
- 선택 메뉴의 "scene.gltf (기본 씬)"을 실제 내용에 맞게 "Breather / SCBA (scene.gltf)"로 바꿨다.
- 앞으로 쓸 폴더를 만들었다: `source/texture/`, `source/hdri/`, `experiments/`, `js/`, `css/`, `docs/screenshots/`.
- 모델 요약 스크립트 `tools/inspect_model.py`를 추가했다.
- `docs/CONCEPT.md`, `docs/DEVLOG.md`, 루트 `README.md`를 작성했다.

### 2026-10-14 · `8c44627` · Three.js 뷰어로 전면 교체

- Babylon.js 라벨 페이지를 Three.js 0.160.0 기반 뷰어로 바꿨다.
- 기능: 모델 선택(단일, 둘 다), OrbitControls 자동 회전과 속도, 주 조명과 환경광 밝기, 조명 각도, 그림자와 그리드 토글, 배경색 선택, 로딩 화면.
- 모델 크기를 자동으로 맞추고 바닥 위에 올리는 배치 로직, 카메라 상하 각도 제한을 넣었다.
- 결과: 직전 커밋에서 JadeToad.glb를 옮겼는데 코드는 `./JadeToad.glb`를 불러서 기본 모델이 404로 뜨지 않았다.
- 이전 Babylon.js 라벨 테스트 코드가 이 커밋에서 덮어써졌다. 아래 명령으로 다시 꺼낼 수 있다.
  ```bash
  git show 0187055:index.html
  ```

### 2026-10-14 · `b02d8df` · JadeToad.glb를 source/model/로 이동

- 모델 파일을 `source/model/` 아래로 모으기 시작했다.

### 2026-06-17 · `67deeef` · scene.gltf, scene.bin을 루트로 이동

- `source/model/`에 있던 Breather 모델 파일을 루트로 옮겼다.
- 이 커밋이 upstream `keni2r/webgl3ddata`의 최신 커밋이고, 현재 Vercel 배포본과 일치한다.

### 2026-06-17 · `0187055` · 모델 경로 "./"를 "/"로 변경

- 주석상 목적은 Vercel 라우팅 오류 방지였다. 로드 실패 시 콘솔 오류와 알림창을 띄우도록 했다.
- `index.html`이 루트에 있으면 `./`와 `/`는 같은 주소를 가리킨다. 당시 오류의 실제 원인은 경로 표기가 아니었을 가능성이 크다.

### 2026-05-22 · `5b0c036` · JadeToad.glb 추가, Babylon.js 라벨 테스트

- 루트에 JadeToad.glb를 추가했다.
- Babylon.js GUI로 머리, 가슴, 배 위치에 이름표와 점선 지시선을 붙였다.
- 모델을 위아래로 움직여 지시선이 모델을 따라가는지 확인하는 애니메이션을 넣었다.

### 2026-05-20 · `9d912b0` · 모델 경로 수정

- 존재하지 않던 `./model.glb` 대신 `./source/model/scene.gltf`를 불러오도록 고쳤다.

### 2026-05-20 · `35e42fc` · 프로젝트 시작

- Babylon.js 기본 뷰어 `index.html`을 만들었다.
- Sketchfab의 Breather / SCBA 모델(`scene.gltf`, `scene.bin`)을 `source/model/`에 추가했다.
