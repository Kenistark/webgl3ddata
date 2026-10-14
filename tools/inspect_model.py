#!/usr/bin/env python3
"""glTF / GLB 모델 요약 도구 (표준 라이브러리만 사용).

새 모델을 source/model/ 에 넣은 뒤 실행해서 크기, 폴리곤 수, 재질, 텍스처,
확장 기능, 출처 정보를 확인하고 docs/CONCEPT.md 의 모델 목록에 옮겨 적는다.

사용법:
    python tools/inspect_model.py source/model/JadeToad.glb
    python tools/inspect_model.py source/model          # 폴더 안의 .glb/.gltf 전부
"""
import json
import math
import struct
import sys
from pathlib import Path

COMPONENTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def load_gltf(path):
    data = path.read_bytes()
    if path.suffix.lower() == ".glb":
        magic, _version, _length = struct.unpack_from("<4sII", data, 0)
        if magic != b"glTF":
            raise ValueError("GLB 매직 넘버(glTF)가 아닙니다")
        chunk_len, chunk_type = struct.unpack_from("<I4s", data, 12)
        if chunk_type != b"JSON":
            raise ValueError("GLB 첫 청크가 JSON이 아닙니다")
        return json.loads(data[20:20 + chunk_len].decode("utf-8"))
    return json.loads(data.decode("utf-8"))


def mat_mul(a, b):
    # 4x4 column-major 행렬 곱 (glTF 규약)
    out = [0.0] * 16
    for col in range(4):
        for row in range(4):
            out[col * 4 + row] = sum(a[k * 4 + row] * b[col * 4 + k] for k in range(4))
    return out


def node_matrix(node):
    if "matrix" in node:
        return list(node["matrix"])
    tx, ty, tz = node.get("translation", [0, 0, 0])
    qx, qy, qz, qw = node.get("rotation", [0, 0, 0, 1])
    sx, sy, sz = node.get("scale", [1, 1, 1])
    return [
        (1 - 2 * (qy * qy + qz * qz)) * sx, (2 * (qx * qy + qz * qw)) * sx, (2 * (qx * qz - qy * qw)) * sx, 0,
        (2 * (qx * qy - qz * qw)) * sy, (1 - 2 * (qx * qx + qz * qz)) * sy, (2 * (qy * qz + qx * qw)) * sy, 0,
        (2 * (qx * qz + qy * qw)) * sz, (2 * (qy * qz - qx * qw)) * sz, (1 - 2 * (qx * qx + qy * qy)) * sz, 0,
        tx, ty, tz, 1,
    ]


def transform_point(m, p):
    x, y, z = p
    return [m[0] * x + m[4] * y + m[8] * z + m[12],
            m[1] * x + m[5] * y + m[9] * z + m[13],
            m[2] * x + m[6] * y + m[10] * z + m[14]]


def world_bounds(g):
    """씬 노드 변환을 적용한 월드 바운딩 박스 (accessor min/max 기준 근사치)."""
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    nodes = g.get("nodes", [])
    scenes = g.get("scenes", [])
    roots = scenes[g.get("scene", 0)]["nodes"] if scenes else range(len(nodes))
    identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    stack = [(i, identity) for i in roots]
    while stack:
        idx, parent = stack.pop()
        node = nodes[idx]
        m = mat_mul(parent, node_matrix(node))
        if "mesh" in node:
            for prim in g["meshes"][node["mesh"]]["primitives"]:
                acc = g["accessors"][prim["attributes"]["POSITION"]]
                if "min" not in acc:
                    continue
                a, b = acc["min"], acc["max"]
                for corner in [(x, y, z) for x in (a[0], b[0]) for y in (a[1], b[1]) for z in (a[2], b[2])]:
                    w = transform_point(m, corner)
                    lo = [min(lo[i], w[i]) for i in range(3)]
                    hi = [max(hi[i], w[i]) for i in range(3)]
        stack.extend((c, m) for c in node.get("children", []))
    if lo[0] == math.inf:
        return None
    return lo, hi


def file_size(path, g):
    size = path.stat().st_size
    if path.suffix.lower() == ".gltf":
        for item in g.get("buffers", []) + g.get("images", []):
            uri = item.get("uri")
            if uri and not uri.startswith("data:"):
                ext = path.parent / uri
                if ext.exists():
                    size += ext.stat().st_size
    return size


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.2f} {unit}"
        n /= 1024


def summarize(path):
    g = load_gltf(path)
    accessors = g.get("accessors", [])
    tris = verts = 0
    other_modes = set()
    for mesh in g.get("meshes", []):
        for prim in mesh["primitives"]:
            mode = prim.get("mode", 4)
            n_pos = accessors[prim["attributes"]["POSITION"]]["count"]
            verts += n_pos
            if mode != 4:
                other_modes.add(mode)
                continue
            n_idx = accessors[prim["indices"]]["count"] if "indices" in prim else n_pos
            tris += n_idx // 3

    images = g.get("images", [])
    img_bytes = 0
    for im in images:
        if "bufferView" in im:
            img_bytes += g["bufferViews"][im["bufferView"]]["byteLength"]
        elif im.get("uri") and not im["uri"].startswith("data:"):
            p = path.parent / im["uri"]
            img_bytes += p.stat().st_size if p.exists() else 0

    asset = g.get("asset", {})
    extras = asset.get("extras", {})
    lines = [
        f"== {path.as_posix()}",
        f"  형식        : {'GLB (단일 바이너리)' if path.suffix.lower() == '.glb' else 'glTF (JSON + 외부 파일)'}",
        f"  전체 용량   : {human(file_size(path, g))}",
        f"  생성 도구   : {asset.get('generator', '-')}",
        f"  메시/노드   : {len(g.get('meshes', []))} / {len(g.get('nodes', []))}",
        f"  삼각형      : {tris:,}" + (f"  (삼각형 외 primitive mode: {sorted(other_modes)})" if other_modes else ""),
        f"  정점        : {verts:,}",
        f"  재질        : {len(g.get('materials', []))}  "
        + ", ".join(m.get("name", "?") + ("[BLEND]" if m.get("alphaMode") == "BLEND" else "")
                    for m in g.get("materials", [])),
        f"  텍스처 이미지: {len(images)}  ({human(img_bytes)}, "
        + ", ".join(sorted({im.get('mimeType', Path(im.get('uri', '')).suffix or '?') for im in images})) + ")"
        if images else "  텍스처 이미지: 0",
        f"  애니메이션  : {len(g.get('animations', []))},  스킨: {len(g.get('skins', []))}",
        f"  확장 사용   : {', '.join(g.get('extensionsUsed', [])) or '-'}",
        f"  확장 필수   : {', '.join(g.get('extensionsRequired', [])) or '-'}",
    ]
    bounds = world_bounds(g)
    if bounds:
        size = [bounds[1][i] - bounds[0][i] for i in range(3)]
        lines.append("  월드 크기   : " + " x ".join(f"{s:.3f}" for s in size) + "  (X x Y x Z, glTF 단위=미터)")
    if extras:
        for key in ("title", "author", "license", "source"):
            if key in extras:
                lines.append(f"  {key:<11} : {extras[key]}")
    return "\n".join(lines)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    targets = []
    for arg in argv[1:]:
        p = Path(arg)
        if p.is_dir():
            targets += sorted(x for x in p.rglob("*") if x.suffix.lower() in (".glb", ".gltf"))
        else:
            targets.append(p)
    for t in targets:
        try:
            print(summarize(t))
        except Exception as exc:  # 깨진 파일도 목록 전체 검사는 계속 진행
            print(f"== {t.as_posix()}\n  [오류] {exc}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
