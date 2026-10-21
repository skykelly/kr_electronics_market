"""C6 하이센스·마이디어·하이얼·모바(브랜드별 질문) 기록 생성.

1단계(재배치): 이전 기능별 기록(Z1~Z5)에서 하이센스·마이디어·하이얼·모바이 주어인 사실 기록만 골라 중복을 합쳐 옮긴다.
  - 출처는 원 기록들의 합집합, moved_from에 원 ID를 남긴다. 문장을 고치면 why에 이유를 적는다.
  - 해석은 옮기지 않는다(새 질문 기준으로 새로 쓴다). 하이센스·마이디어·하이얼·모바 단독 전망은 추적을 잇기 위해 옮긴다.
2단계(보강): 독립 조사 대조로 찾은 빈칸을 원문 확인 후 ADD로 더한다.
실행: python3 tools/c1/c1_build.py  → china-brands/c6/records_base.jsonl, c6_amap.json(키→ID 고정)
"""
import json as _j, re, glob as _g
_GZ = {}
for _f in sorted(_g.glob(str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'c*' / 'c*_zmap.json'))):
    _GZ.update(_j.load(open(_f, encoding='utf-8')))
import json, glob
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "china-brands/c6"
Z = {}
for f in glob.glob(str(ROOT / "china-legacy/z*/records.jsonl")):
    for l in open(f, encoding="utf-8"):
        r = json.loads(l); Z[r["id"]] = r
AMAP_P = Path(__file__).with_name("c6_amap.json")
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
mv("org_h05", "사건", ["Z1-E-001"], "조직", event_type="전략·조직")
mv("org_h10", "사건", ["Z1-E-002"], "조직", event_type="전략·조직")
mv("org_m25", "사건", ["Z1-E-034"], "조직", event_type="전략·조직")
mv("org_m26", "사건", ["Z1-E-040"], "조직", event_type="전략·조직", statement="마이디어 코리아 김상우 대표는 2026년 4월 27일 스탠드형 에어컨 공개 자리에서 한국 에어컨 시장을 적극 공략하겠다고 밝혔다.", why="AS·판매처 서술은 각 축 기록으로 분리")
mv("org_mova25", "사건", ["Z3-E-032"], "조직", event_type="전략·조직", actor="모바(MOVA)", statement="드리미의 서브 브랜드였다가 2024년 말 분사한 모바가 2025년 8월 20일 한국 시장 진출을 공식 발표했다.", why="채널·AS 서술은 각 축 기록으로 분리")
# ===================== 제품 =====================
mv("p_h10", "사건", ["Z2-E-001", "Z3-E-002", "Z5-E-002"], "제품", why="같은 하이얼코리아 2010-05-28 발표 3건을 합침")
mv("m_h10px", "지표", ["Z2-M-028"], "제품", indicator="C6-T8")
mv("p_hs100", "사건", ["Z2-E-015"], "제품")
mv("p_m26ac", "사건", ["Z2-E-034", "Z5-E-039"], "제품", why="같은 마이디어 2026-04-27 공개 2건을 합침")
mv("m_m26ac", "지표", ["Z2-M-008"], "제품", indicator="C6-T2")
# ===================== 채널 =====================
mv("ch_h05", "사건", ["Z3-E-001", "Z5-E-001"], "채널", event_type="채널·매장", why="같은 우리홈쇼핑 2005-06-23 방송 2건을 합침")
mv("ch_hs24", "사건", ["Z3-E-015"], "채널", event_type="채널·매장")
mv("ch_hs25", "사건", ["Z1-E-021", "Z3-E-022"], "채널", event_type="채널·매장", why="같은 하이센스 2025-01-23 기사 2건을 합침")
mv("m_hs_ch1", "지표", ["Z3-M-013"], "채널", indicator="C6-T3")
mv("ch_hs26", "사건", ["Z1-E-042", "Z2-E-036", "Z3-E-046"], "채널", event_type="채널·매장", why="같은 뉴스1 2026-05-12 기사 3건을 합침")
mv("m_hs_ch2", "지표", ["Z3-M-014"], "채널", indicator="C6-T3")
mv("ch_m24", "사건", ["Z3-E-016"], "채널", event_type="채널·매장", actor="마이디어")
mv("ch_m25", "사건", ["Z1-E-032", "Z3-E-034"], "채널", event_type="채널·매장", why="같은 아이뉴스24 2025-09 기사 2건을 합침")
mv("ch_m26", "사건", ["Z3-E-045"], "채널", event_type="채널·매장")
mv("m_m_ch4", "지표", ["Z3-M-012"], "채널", indicator="C6-T3")
mv("m_m20", "지표", ["Z1-M-017"], "채널", indicator="C6-T3")
# ===================== AS·신뢰 =====================
mv("as_hs24", "사건", ["Z4-E-008"], "AS·신뢰", event_type="구독·케어·AS")
mv("as_mova25", "사건", ["Z4-E-028"], "AS·신뢰", event_type="구독·케어·AS", actor="모바(MOVA)")
mv("m_mova_war", "지표", ["Z4-M-022"], "AS·신뢰", indicator="C6-T4")
mv("as_m26", "사건", ["Z4-E-035"], "AS·신뢰", event_type="구독·케어·AS", statement="마이디어 코리아는 2026년 4월 27일 AS를 전국 캐리어 서비스센터와 연계해 제공한다고 밝혔다.", why="판매처 서술은 채널 기록으로 분리")
# ===================== 판촉·마케팅 =====================
mv("mk_m25kes", "사건", ["Z2-E-025", "Z3-E-037", "Z5-E-029"], "판촉·마케팅", event_type="마케팅", why="같은 KES 2025-10-21 참가 3건을 합침")
mv("mk_hs26", "사건", ["Z3-E-044", "Z5-E-040"], "판촉·마케팅", event_type="판촉", why="같은 하이센스 쿠가세 행사 2건을 합침")
# ===================== 전망(네 브랜드 단독, 추적 유지) =====================
FC = {"f_m20": ["Z1-F-004", "Z3-F-002"], "f_hm_hs": ["Z3-F-003"]}
for k, ids in FC.items():
    r0 = {x: y for x, y in Z[ids[0]].items() if x not in ("id", "question", "added_on", "first_seen", "origin", "intake")}
    r0.update(moved_from=ids, axis="전망", type="전망")
    R.append((k, r0))

# ===================== 보강(독립 조사 대조 후) =====================
exec(open(Path(__file__).with_name("c6_add.py"), encoding="utf-8").read()) if Path(__file__).with_name("c6_add.py").exists() else None

# ===================== 해석·분석 전망(새 질문 기준으로 새로 작성) =====================
exec(open(Path(__file__).with_name("c6_interp.py"), encoding="utf-8").read()) if Path(__file__).with_name("c6_interp.py").exists() else None

# ---------- ID 부여(키 고정) ----------
L = {"사건": "E", "지표": "M", "해석": "I", "전망": "F"}
used = set(AMAP.values())
cnt = {}
for k, r in R:
    if k not in AMAP:
        t = L[r["type"]]
        n = max([int(v.split("-")[2]) for v in AMAP.values() if v.split("-")[1] == t] + [0]) + 1
        AMAP[k] = f"C6-{t}-{n:03d}"
zmap = {}
for k, r in R:
    for z in r.get("moved_from", []):
        zmap.setdefault(z, AMAP[k])
ZFIX = {}
def fix(x): return ZFIX.get(x) or AMAP.get(x, zmap.get(x, x))
out = []
for k, r in R:
    r = dict(r)
    r.update(id=AMAP[k], question="C6", question_version="v2.0", first_seen="R1", added_on=ON, status=r.get("status", "유효"), replaces=None)
    if r.get("basis"):
        b = []
        for x in r["basis"]:
            y = fix(x)
            y = _GZ.get(y, y)  # 다른 브랜드로 옮겨진 Z 기록은 새 번호로
            if re.fullmatch(r'Z\d-[EMFI]-\d+', y): continue  # Z 구조 삭제(옮겨지지 않은 기록은 근거에서 뺀다)
            if y not in b: b.append(y)
        r["basis"] = b
    r.setdefault("importance", 2); r.setdefault("check_flags", []); r.setdefault("sources", [])
    if "why" in r: r["moved_why"] = r.pop("why")
    out.append(r)
AMAP_P.write_text(json.dumps(AMAP, ensure_ascii=False, indent=0), encoding="utf-8")
(Path(__file__).with_name("c6_zmap.json")).write_text(json.dumps(zmap, ensure_ascii=False, indent=0), encoding="utf-8")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_base.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sorted(out, key=lambda r: r["id"])), encoding="utf-8")
if not (OUT / "patches.jsonl").exists(): (OUT / "patches.jsonl").write_text("", encoding="utf-8")
from collections import Counter
print("기록", len(out), Counter(r["type"] for r in out), "축", Counter(r.get("axis") for r in out))
