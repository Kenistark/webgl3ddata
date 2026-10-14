# webgl3ddata

WebGL로 3D 파일(glTF, GLB)을 브라우저에서 열어 보고 테스트하는 프로젝트입니다.

- 배포: https://webgl3ddata.vercel.app/
- 기본 컨셉: [docs/CONCEPT.md](docs/CONCEPT.md)
- 개발 로그: [docs/DEVLOG.md](docs/DEVLOG.md)

## 로컬에서 실행

`index.html`을 파일로 직접 열면 브라우저가 모듈과 모델 로드를 막습니다. 로컬 서버로 엽니다.

```bash
python -m http.server 8765
```

브라우저에서 http://localhost:8765 를 엽니다.

## 모델 정보 확인

```bash
python tools/inspect_model.py source/model
```

## 폴더

| 폴더 | 용도 |
|---|---|
| `source/model/` | 테스트할 3D 모델 |
| `source/texture/`, `source/hdri/` | 텍스처, 환경맵 (예정) |
| `experiments/` | 기능별 단독 테스트 페이지 (예정) |
| `js/`, `css/` | index.html에서 분리할 코드 (예정) |
| `tools/` | 로컬 보조 스크립트 |
| `docs/` | 컨셉, 개발 로그, 스크린샷 |

자세한 규칙은 [docs/CONCEPT.md](docs/CONCEPT.md)에 있습니다.
