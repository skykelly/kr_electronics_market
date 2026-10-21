"""C5 TCL(브랜드별 질문) 기록 생성.

1단계(재배치): 이전 기능별 기록(Z1~Z5)에서 TCL이 주어인 사실 기록만 골라 중복을 합쳐 옮긴다.
  - 출처는 원 기록들의 합집합, moved_from에 원 ID를 남긴다. 문장을 고치면 why에 이유를 적는다.
  - 해석은 옮기지 않는다(새 질문 기준으로 새로 쓴다). TCL 단독 전망은 추적을 잇기 위해 옮긴다.
2단계(보강): 독립 조사 대조로 찾은 빈칸을 원문 확인 후 ADD로 더한다.
실행: python3 tools/c1/c1_build.py  → china-brands/c5/records_base.jsonl, c5_amap.json(키→ID 고정)
"""
import json as _j, re, glob as _g
_GZ = {}
_ZI = {'Z1-I-005': 'C5-I-003', 'Z2-I-003': 'C5-I-002'}
for _f in sorted(_g.glob(str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'c*' / 'c*_zmap.json'))):
    _GZ.update(_j.load(open(_f, encoding='utf-8')))
import json, glob
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "china-brands/c5"
Z = {}
for f in glob.glob(str(ROOT / "china-legacy/z*/records.jsonl")):
    for l in open(f, encoding="utf-8"):
        r = json.loads(l); Z[r["id"]] = r
AMAP_P = Path(__file__).with_name("c5_amap.json")
AMAP = json.loads(AMAP_P.read_text()) if AMAP_P.exists() else {}
ON = "2026-10-21"
R = []

def _src(ids):
    out, seen = [], set()
    for i in ids:
        for s in Z[i].get("sources", []):
            if s["url"] not in seen: seen.add(s["url"]); out.append(s)
    return out

def mv(k, t, ids, axis, **o):
    """t: 사건|지표|전망. ids: 원 기록(첫 번째가 기준)."""
    base = {x: y for x, y in Z[ids[0]].items() if x not in ("id", "question", "added_on", "first_seen", "revisions", "origin", "intake", "basis")}
    flags = []
    for i in ids:
        flags += [f for f in Z[i].get("check_flags", []) if f not in flags]
    base.update(check_flags=flags, sources=_src(ids), moved_from=ids, axis=axis,
                verified=all(Z[i].get("verified") for i in ids) if t != "전망" else None)
    base.update(o)
    base["type"] = t
    R.append((k, base))

def add(k, t, axis, **o):
    o.update(type=t, axis=axis); o.setdefault("check_flags", []); o.setdefault("claim_type", "해당 없음")
    o.setdefault("verified", True if t in ("사건", "지표") else None)
    R.append((k, o))

# ===================== 조직 =====================
mv("org_corp23", "사건", ["Z1-E-011"], "조직", event_type="전략·조직")
mv("org_iff25", "사건", ["Z1-E-026"], "조직", event_type="전략·조직")
mv("org_ceo26", "사건", ["Z1-E-041"], "조직", event_type="전략·조직")
# ===================== 제품 =====================
mv("p_2023", "사건", ["Z2-E-007"], "제품")
mv("p_iff25", "사건", ["Z2-E-021"], "제품", statement="TCL의 TV 자회사 아이팔콘(iFFALCON)이 2025년 5월 43형 풀HD(약 25만 원), 55형 4K 미니 LED(49만 원), 85형 4K(129만 원)를 출시했다. TCL의 2025년 TV는 50~98형, 30만 원대~600만 원대다.", why="판촉(상품권) 서술은 판촉 기록으로 분리")
mv("p_fr26", "사건", ["Z2-E-030", "Z3-E-041", "Z5-E-033"], "제품", why="같은 냉장고 출시 기록 3건을 합침")
mv("p_range26", "사건", ["Z2-E-035"], "제품")
mv("m_px98", "지표", ["Z2-M-026"], "제품", indicator="C5-T8")
mv("m_px75", "지표", ["Z2-M-025"], "제품", indicator="C5-T8")
mv("m_pxfr", "지표", ["Z2-M-027"], "제품", indicator="C5-T8")
mv("m_capfr", "지표", ["Z2-M-040"], "제품", indicator="C5-T8")
# ===================== 채널 =====================
mv("ch_hm15", "사건", ["Z3-E-003"], "채널", event_type="채널·매장")
mv("m_hm440", "지표", ["Z3-M-006"], "채널", indicator="C5-T3")
mv("ch_cpg22", "사건", ["Z3-E-006"], "채널", event_type="채널·매장")
mv("ch_naver23", "사건", ["Z3-E-012"], "채널", event_type="채널·매장", statement="TCL은 2023년 11월 6일 한국 법인 설립을 알리며 네이버 스마트스토어에서 TV 판매를 시작했다.", why="쿠폰 서술은 판촉 기록으로 분리")
mv("ch_online25", "사건", ["Z1-E-020", "Z2-E-014"], "채널", event_type="채널·매장", statement="2025년 1월 보도에 따르면 TCL 한국 법인은 2023년에 설립됐고 이후 온라인 판매에 집중했다. 네이버스토어와 쿠팡 기획전 중심으로 팔았고 방문 설치와 기존 TV 무상 수거를 제공한다. 75형 4K UHD TV는 네이버스토어에서 87만 9천 원에 팔렸다.", why="같은 기사 기록 2건을 합침")
mv("ch_store98", "사건", ["Z2-E-018", "Z3-E-023", "Z4-E-016"], "채널", event_type="채널·매장", why="같은 한국경제 기사 3건을 합침")
# ===================== AS·신뢰 =====================
mv("as_hm15", "사건", ["Z4-E-001"], "AS·신뢰", event_type="구독·케어·AS")
mv("m_war1", "지표", ["Z4-M-020"], "AS·신뢰", indicator="C5-T4")
mv("as_cpg22", "사건", ["Z4-E-003"], "AS·신뢰", event_type="구독·케어·AS")
mv("m_war2", "지표", ["Z4-M-021"], "AS·신뢰", indicator="C5-T4")
# ===================== 판촉·마케팅 =====================
mv("mk_naver23", "사건", ["Z5-E-009"], "판촉·마케팅")
mv("mk_naver25", "사건", ["Z3-E-020", "Z5-E-014"], "판촉·마케팅", why="같은 기사 2건을 합침")
mv("mk_iff25", "사건", ["Z5-E-020"], "판촉·마케팅")
mv("mk_fr26", "사건", ["Z5-E-033"], "판촉·마케팅")
# ===================== 전망(TCL 단독, 추적 유지) =====================
FC = {"f_off": ["Z1-F-009"], "f_ac": ["Z2-F-008"]}
for k, ids in FC.items():
    r0 = {x: y for x, y in Z[ids[0]].items() if x not in ("id", "question", "added_on", "first_seen", "origin", "intake")}
    r0.update(moved_from=ids, axis="전망", type="전망")
    R.append((k, r0))

# ===================== 보강(독립 조사 대조 후) =====================
exec(open(Path(__file__).with_name("c5_add.py"), encoding="utf-8").read()) if Path(__file__).with_name("c5_add.py").exists() else None

# ===================== 해석·분석 전망(새 질문 기준으로 새로 작성) =====================
exec(open(Path(__file__).with_name("c5_interp.py"), encoding="utf-8").read()) if Path(__file__).with_name("c5_interp.py").exists() else None

# ---------- ID 부여(키 고정) ----------
L = {"사건": "E", "지표": "M", "해석": "I", "전망": "F"}
used = set(AMAP.values())
cnt = {}
for k, r in R:
    if k not in AMAP:
        t = L[r["type"]]
        n = max([int(v.split("-")[2]) for v in AMAP.values() if v.split("-")[1] == t] + [0]) + 1
        AMAP[k] = f"C5-{t}-{n:03d}"
zmap = {}
for k, r in R:
    for z in r.get("moved_from", []):
        zmap.setdefault(z, AMAP[k])
ZFIX = {}
def fix(x): return ZFIX.get(x) or AMAP.get(x, zmap.get(x, x))
out = []
for k, r in R:
    r = dict(r)
    r.update(id=AMAP[k], question="C5", question_version="v2.0", first_seen="R1", added_on=ON, status=r.get("status", "유효"), replaces=None)
    if r.get("basis"):
        b = []
        for x in r["basis"]:
            y = fix(x)
            y = _ZI.get(y, y)  # Z 해석은 이 질문의 같은 주제 해석으로 바꾼다
            y = _GZ.get(y, y)  # 다른 브랜드로 옮겨진 Z 기록은 새 번호로
            if re.fullmatch(r'Z\d-[EMFI]-\d+', y): continue  # Z 구조 삭제(옮겨지지 않은 기록은 근거에서 뺀다)
            if y not in b: b.append(y)
        r["basis"] = b
    r.setdefault("importance", 2); r.setdefault("check_flags", []); r.setdefault("sources", [])
    if "why" in r: r["moved_why"] = r.pop("why")
    out.append(r)
AMAP_P.write_text(json.dumps(AMAP, ensure_ascii=False, indent=0), encoding="utf-8")
(Path(__file__).with_name("c5_zmap.json")).write_text(json.dumps(zmap, ensure_ascii=False, indent=0), encoding="utf-8")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_base.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sorted(out, key=lambda r: r["id"])), encoding="utf-8")
if not (OUT / "patches.jsonl").exists(): (OUT / "patches.jsonl").write_text("", encoding="utf-8")
from collections import Counter
print("기록", len(out), Counter(r["type"] for r in out), "축", Counter(r.get("axis") for r in out))
