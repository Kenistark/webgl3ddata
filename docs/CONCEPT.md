# WebGL 3D Data — 기본 컨셉

브라우저(WebGL)에서 3D 파일이 제대로 열리고 보이는지 빠르게 확인하는 테스트 프로젝트입니다.
결과는 Vercel 정적 호스팅에 올려 PC와 모바일 어디서나 같은 화면으로 확인합니다.

- 배포 주소: https://webgl3ddata.vercel.app/
- 개발 기록: [DEVLOG.md](DEVLOG.md)

## 1. 목표

- 새로 받거나 만든 3D 파일을 폴더에 넣으면 바로 웹에서 열어 본다.
- 로딩, 크기와 중심, 재질과 텍스처, 투명 재질, 그림자, 조명 반응, 모바일 조작을 같은 조건에서 비교한다.
- 엔진별 차이(Three.js, Babylon.js)와 압축 방식별 용량·성능 차이를 기록으로 남긴다.

## 2. 원칙

- **빌드 없는 정적 사이트로 유지한다.** HTML과 CDN 모듈만 쓰고, 저장소 루트가 그대로 Vercel에 배포된다.
- **경로는 `index.html` 기준 상대 경로로 쓴다.** 예: `./source/model/JadeToad.glb`. 로컬 서버와 Vercel에서 똑같이 동작한다.
- **파일명 대소문자를 정확히 맞춘다.** Windows 로컬에서는 대소문자가 틀려도 열리지만 Vercel(Linux)에서는 404가 난다.
- **파일명에는 영문, 숫자, `-`, `_`만 쓴다.** 공백과 한글은 URL 인코딩 문제를 만든다.
- **모델 편집 기능은 목표가 아니다.** 보고, 비교하고, 기록하는 데 집중한다.

## 3. 기술 구성

| 항목 | 내용 |
|---|---|
| 렌더링 | Three.js 0.160.0 (unpkg CDN, import map) |
| 로더 | GLTFLoader (`.glb`, `.gltf`) |
| 카메라 | OrbitControls, 자동 회전, 상하 각도 15°~88°, 거리 1.2~20 |
| 조명 | HemisphereLight + DirectionalLight(그림자 2048px) + 보조 림라이트 |
| 렌더 설정 | sRGB 출력, ACES Filmic 톤매핑, PCF Soft 그림자 |
| 모델 배치 | 가장 긴 변을 2.2로 맞추고 바닥(y = -1) 위에 올림. "모두 함께 보기"는 x = ±1.4 |
| 배포 | Vercel 정적 호스팅, 빌드 단계 없음 |

## 4. 폴더 구조

```
webgl3ddata/
├── index.html              메인 뷰어 (Three.js). Vercel 루트 페이지
├── source/                 테스트 대상 에셋. 배포 시 그대로 공개된다
│   ├── model/              3D 모델
│   │   ├── JadeToad.glb    단일 파일 GLB는 바로 둔다
│   │   └── breather/       여러 파일로 된 glTF는 모델별 폴더로 묶는다
│   │       ├── scene.gltf
│   │       └── scene.bin
│   ├── texture/            (예정) 단독 텍스처, 재질 테스트용 이미지
│   └── hdri/               (예정) 환경맵 .hdr / .exr. 환경광과 반사 테스트
├── experiments/            (예정) 기능별 단독 테스트 페이지. 폴더 하나에 페이지 하나
├── js/                     (예정) index.html에서 분리할 JS 모듈
├── css/                    (예정) index.html에서 분리할 스타일
├── tools/                  로컬 보조 스크립트
│   └── inspect_model.py    모델 요약 (용량, 폴리곤, 재질, 텍스처, 출처)
└── docs/
    ├── CONCEPT.md          기본 컨셉 (이 문서)
    ├── DEVLOG.md           개발 로그
    └── screenshots/        (예정) 테스트 결과 캡처
```

빈 폴더는 Git이 추적하지 않으므로 `.gitkeep` 파일을 넣어 두었습니다. 폴더에 실제 파일이 생기면 지워도 됩니다.

**experiments 규칙.** `experiments/<이름>/index.html`로 만들면 `https://webgl3ddata.vercel.app/experiments/<이름>/`에서 열립니다.
모델은 복사하지 않고 `../../source/model/...` 상대 경로로 공유합니다.

## 5. 모델 추가 순서

1. 파일을 `source/model/`에 넣는다. `.gltf`처럼 `.bin`과 텍스처가 따로 있는 모델은 폴더째 넣는다.
2. 모델 정보를 확인한다.
   ```bash
   python tools/inspect_model.py source/model
   ```
3. `index.html`의 `MODEL_URLS`와 `#model-select` 옵션에 함께 등록한다.
4. 로컬 서버로 열어 아래 체크리스트를 확인한다.
   ```bash
   python -m http.server 8765
   ```
5. 아래 모델 목록 표와 [DEVLOG.md](DEVLOG.md)를 갱신한다.
6. 커밋하고 배포 저장소에 반영한 뒤 Vercel 주소에서 다시 확인한다.

GitHub는 50MB 이상 파일에 경고하고 100MB 이상 파일은 거부합니다. 큰 모델은 압축하거나 Git LFS를 검토합니다.

## 6. 모델별 테스트 체크리스트

- [ ] 로드 성공 (로컬 서버, Vercel 둘 다)
- [ ] 크기, 중심, 바닥 위치가 정상
- [ ] 재질 색상과 텍스처가 원본과 비슷함 (sRGB)
- [ ] 투명(BLEND) 재질의 앞뒤 정렬이 깨지지 않음
- [ ] 그림자를 만들고 받음
- [ ] 조명 밝기와 각도를 바꿨을 때 자연스럽게 반응
- [ ] 모바일에서 터치 회전과 확대가 동작
- [ ] 파일 용량과 로딩 시간이 허용 범위

## 7. 모델 목록

`tools/inspect_model.py`로 측정한 값입니다. (2026-10-14 기준)

| 항목 | JadeToad | Breather / SCBA |
|---|---|---|
| 경로 | `source/model/JadeToad.glb` | `source/model/breather/scene.gltf` + `scene.bin` |
| 형식 | GLB 단일 파일 | glTF + 외부 바이너리 |
| 용량 | 2.08 MB | 1.90 MB |
| 삼각형 | 6,456 | 44,040 |
| 정점 | 3,389 | 44,930 |
| 재질 | 1개 (Toad) | 14개, 그중 GlassShader는 투명 BLEND |
| 텍스처 | PNG 3장, 1.85 MB | 없음. 색상값만 사용 |
| 텍스처 종류 | baseColor, metallicRoughness + occlusion, normal | - |
| glTF 확장 | 없음 | KHR_materials_specular |
| 실제 크기 (m) | 0.35 × 0.41 × 0.41 | 67 × 112 × 113 (cm 단위로 제작된 것으로 보임) |
| 생성 도구 | Adobe Substance 3D Painter 12.0.3 | Sketchfab 16.14.0 |
| 출처 | 기록 없음. 확인 후 기입 | Studio Lab (Sketchfab) |
| 라이선스 | 기록 없음. 확인 후 기입 | SKETCHFAB Standard |

**JadeToad.** 용량의 약 89%가 텍스처입니다. 텍스처 압축(KTX2, WebP) 효과를 비교하기 좋은 샘플입니다.

**Breather.** 텍스처 없이 폴리곤과 재질 수가 많은 모델입니다. 지오메트리 압축(Draco, Meshopt)과 투명 재질 정렬을 테스트하기 좋은 샘플입니다.
Sketchfab Standard 라이선스는 원본 파일 재배포에 제한이 있을 수 있으므로, 공개 저장소와 공개 배포에 두어도 되는지 약관을 확인해야 합니다.

## 8. 앞으로 테스트할 것

| 순서 | 항목 | 사용할 폴더 |
|---|---|---|
| 1 | 뷰어 버그 수정: 모델 전환 중복, 리소스 해제, 오류 안내 | `index.html` |
| 2 | 모바일 레이아웃: 컨트롤 패널 접기 | `index.html` 또는 `css/` |
| 3 | 성능 표시: FPS, draw call, 삼각형 수 | `index.html` |
| 4 | 드래그 앤 드롭으로 로컬 파일 바로 열기 | `index.html` |
| 5 | HDRI 환경맵 조명과 반사 | `source/hdri/` |
| 6 | 압축 비교: Draco, Meshopt, KTX2 | `source/model/`, `experiments/` |
| 7 | Babylon.js 라벨(지시선) 테스트 복원, 엔진 비교 | `experiments/` |
| 8 | 모델 목록을 JSON으로 관리해 선택 메뉴 자동 생성 | `source/model/` |
| 9 | index.html의 스크립트와 스타일 분리 | `js/`, `css/` |
