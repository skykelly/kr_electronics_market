"""O 질문(한국 기타 경쟁사) 빌드 스크립트 생성기.
사용: python3 tools/o_tmpl/mkobuild.py o1 코웨이  → tools/o1/o1_build.py (보강·해석 스크립트 o1_add.py·o1_interp.py를 읽어 기록 생성)
"""
import sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
q, name = sys.argv[1], sys.argv[2]
Q = q.upper()
code = '''"""@Q@ @NAME@(한국 기타 경쟁사 질문) 기록 생성. 독립 조사 대조 후 원문을 직접 연 사실만 o_add로 더하고, 해석·전망은 o_interp로 쓴다.
실행: python3 tools/@q@/@q@_build.py  → korea-competitors/@q@/records_base.jsonl, @q@_amap.json(키→ID 고정)
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "korea-competitors/@q@"
AMAP_P = Path(__file__).with_name("@q@_amap.json")
AMAP = json.loads(AMAP_P.read_text()) if AMAP_P.exists() else {}
ON = "2026-10-21"
R = []

def add(k, t, axis, **o):
    o.update(type=t, axis=axis); o.setdefault("check_flags", []); o.setdefault("claim_type", "해당 없음")
    o.setdefault("verified", True if t in ("사건", "지표") else None)
    R.append((k, o))

exec(open(Path(__file__).with_name("@q@_add.py"), encoding="utf-8").read()) if Path(__file__).with_name("@q@_add.py").exists() else None
exec(open(Path(__file__).with_name("@q@_interp.py"), encoding="utf-8").read()) if Path(__file__).with_name("@q@_interp.py").exists() else None

L = {"사건": "E", "지표": "M", "해석": "I", "전망": "F"}
for k, r in R:
    if k not in AMAP:
        t = L[r["type"]]
        n = max([int(v.split("-")[2]) for v in AMAP.values() if v.split("-")[1] == t] + [0]) + 1
        AMAP[k] = f"@Q@-{t}-{n:03d}"
out = []
for k, r in R:
    r = dict(r)
    r.update(id=AMAP[k], question="@Q@", question_version="v2.0", first_seen="R1", added_on=ON, status=r.get("status", "유효"), replaces=None)
    if r.get("basis"):
        b = []
        for x in r["basis"]:
            y = AMAP.get(x, x)
            if y not in b: b.append(y)
        r["basis"] = b
    r.setdefault("importance", 2); r.setdefault("check_flags", []); r.setdefault("sources", [])
    out.append(r)
AMAP_P.write_text(json.dumps(AMAP, ensure_ascii=False, indent=0), encoding="utf-8")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_base.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\\n" for r in sorted(out, key=lambda r: r["id"])), encoding="utf-8")
if not (OUT / "patches.jsonl").exists(): (OUT / "patches.jsonl").write_text("", encoding="utf-8")
from collections import Counter
print("기록", len(out), Counter(r["type"] for r in out), "축", Counter(r.get("axis") for r in out))
'''
(R / f"tools/{q}").mkdir(exist_ok=True)
(R / f"tools/{q}/{q}_build.py").write_text(code.replace("@Q@", Q).replace("@q@", q).replace("@NAME@", name), encoding="utf-8")
print("ok", q)
