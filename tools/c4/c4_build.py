"""C4 샤오미(브랜드별 질문) 기록 생성.

1단계(재배치): 이전 기능별 기록(Z1~Z5)에서 샤오미이 주어인 사실 기록만 골라 중복을 합쳐 옮긴다.
  - 출처는 원 기록들의 합집합, moved_from에 원 ID를 남긴다. 문장을 고치면 why에 이유를 적는다.
  - 해석은 옮기지 않는다(새 질문 기준으로 새로 쓴다). 샤오미 단독 전망은 추적을 잇기 위해 옮긴다.
2단계(보강): 독립 조사 대조로 찾은 빈칸을 원문 확인 후 ADD로 더한다.
실행: python3 tools/c1/c1_build.py  → china-brands/c4/records_base.jsonl, c4_amap.json(키→ID 고정)
"""
import json, glob
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "china-brands/c4"
Z = {}
for f in glob.glob(str(ROOT / "china-legacy/z*/records.jsonl")):
    for l in open(f, encoding="utf-8"):
        r = json.loads(l); Z[r["id"]] = r
AMAP_P = Path(__file__).with_name("c4_amap.json")
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
mv("org_launch25", "사건", ["Z1-E-018"], "조직")
mv("org_press25", "사건", ["Z1-E-019"], "조직", statement="샤오미코리아는 2025년 1월 15일 서울 포시즌스호텔에서 설립 후 첫 기자간담회를 열었다. 조니 우 사장은 현지 기업으로 자리잡겠다고 밝혔고, 키코 송 동아시아 마케팅 총괄이 신제품을 발표했다.", check_flags=[], why="채널·AS·보증 서술은 각 축 기록으로 분리")
# ===================== 제품 =====================
mv("p_jan25", "사건", ["Z2-E-013"], "제품")
for k, i, ind in [("m_n16", "Z2-M-005", "C4-T2"), ("m_n22", "Z2-M-006", "C4-T2"), ("m_px14t", "Z2-M-018", "C4-T8"), ("m_px_tv65", "Z2-M-019", "C4-T8"), ("m_px_tv75", "Z2-M-020", "C4-T8"), ("m_px_tv100", "Z2-M-021", "C4-T8")]:
    mv(k, "지표", [i], "제품", indicator=ind)
mv("p_sep25", "사건", ["Z2-E-024"], "제품")
mv("p_big25", "사건", ["Z2-E-026"], "제품")
mv("p_wuhan25", "사건", ["Z2-E-028"], "제품")
# ===================== 채널 =====================
mv("ch_agent21", "사건", ["Z1-E-004"], "채널", event_type="채널·매장")
mv("ch_online25", "사건", ["Z3-E-021"], "채널", event_type="채널·매장")
mv("m_ch3", "지표", ["Z3-M-010"], "채널", indicator="C4-T3")
mv("ch_ifc25", "사건", ["Z3-E-030", "Z3-E-031", "Z1-E-029", "Z2-E-023"], "채널", event_type="채널·매장", statement="샤오미는 2025년 6월 28일 첫 국내 공식 매장 샤오미 스토어 IFC몰 여의도점(L2층, 약 60평)을 열었다. 스마트폰, 태블릿, TV, 진공청소기, 로봇청소기, 헤어드라이기 등 100여 개 제품을 전시하고 판매와 AS를 한곳에서 한다. 온라인과 오프라인의 가격·모델은 같고 한국 전역에 매장을 낼 계획이라고 밝혔다. 배송은 도심 48시간, 도서산간 72시간이다.", check_flags=["개점일은 예고 기사 기준이며 개점 후 기사로 직접 확인하지 못함", "매장 면적이 60평(약 197㎡)으로 환산 표기됨"], why="같은 매장 기록 4건을 합침. 보증·AS 인력은 AS 기록으로 분리")
mv("m_store1", "지표", ["Z3-M-003", "Z1-M-012"], "채널", indicator="C4-T3")
mv("m_visit1", "지표", ["Z3-M-024"], "채널", indicator="C4-T9")
mv("m_visit7", "지표", ["Z3-M-025"], "채널", indicator="C4-T9")
mv("ch_store3", "사건", ["Z3-E-036", "Z1-E-033"], "채널", event_type="채널·매장", statement="샤오미코리아는 2025년 9월 25일 하반기 기자간담회에서 2호점 구의 NC이스트폴점과 3호점 마곡 원그로브점을 9월 27일 연다고 밝혔다. 1호점 개점일 방문객은 7,400명, 7월 일평균은 약 3,000명이라고 밝혔다. 1호점 판매 비중은 스마트폰 플래그십 40%, 패드7 31%, TV S 미니 60%다.", why="같은 간담회 기록 2건을 합침. 서비스센터·협력 서술은 별도 기록")
mv("m_store3", "지표", ["Z3-M-004", "Z1-M-013"], "채널", indicator="C4-T3")
mv("ch_partner25", "사건", ["Z3-E-035"], "채널", event_type="제휴·협업")
mv("ch_store45", "사건", ["Z1-E-036", "Z3-E-038"], "채널", event_type="채널·매장", why="같은 보도 2건을 합침")
mv("ch_store8", "사건", ["Z1-E-039", "Z2-E-033", "Z3-E-043"], "채널", event_type="채널·매장", why="같은 딜사이트 보도 3건을 합침")
mv("m_store8", "지표", ["Z3-M-005", "Z1-M-014"], "채널", indicator="C4-T3")
# ===================== AS·신뢰 =====================
mv("as_war25", "사건", ["Z4-E-012"], "AS·신뢰", event_type="구독·케어·AS")
mv("m_war3", "지표", ["Z4-M-016"], "AS·신뢰", indicator="C4-T4")
mv("as_ifc25", "사건", ["Z4-E-025"], "AS·신뢰", event_type="구독·케어·AS")
mv("m_war_vac", "지표", ["Z4-M-017"], "AS·신뢰", indicator="C4-T4")
mv("m_war_tv", "지표", ["Z4-M-018"], "AS·신뢰", indicator="C4-T4")
mv("as_out25", "사건", ["Z4-E-026", "Z1-E-030"], "AS·신뢰", event_type="구독·케어·AS", statement="비즈한국은 2025년 6월 26일 샤오미가 국내 직영 AS센터 없이 SK네트웍스서비스에 외주해 전국 14개 지점에서 AS를 제공한다고 전했다. 소비자주권시민회의 조사에서 레드미 14C 액정 수리비가 구로 7만 8천 원, 광명 5만 3천 원으로 센터별로 달랐다. 샤오미는 개선책으로 오프라인 통합형 매장, 독자 AS센터, 현지 파트너 협력을 제시했고 센터 규모와 시기는 밝히지 않았다.", why="같은 보도 2건을 합침")
mv("m_out14", "지표", ["Z4-M-010", "Z1-M-016"], "AS·신뢰", indicator="C4-T4")
mv("as_ex25", "사건", ["Z4-E-031", "Z1-E-035"], "AS·신뢰", event_type="구독·케어·AS", why="같은 개소 보도 2건을 합침")
mv("m_ex1", "지표", ["Z4-M-011", "Z1-M-015"], "AS·신뢰", indicator="C4-T4")
mv("tr_pipc25", "사건", ["Z4-E-018"], "AS·신뢰", event_type="인증·규제", statement="개인정보보호위원회는 2025년 3월 4일 삼성전자, LG전자, 샤오미, 에코백스, 로보락의 로봇청소기를 대상으로 개인정보 수집·관리 실태를 사전 점검한다고 발표했다. 샤오미가 점검 대상에 포함됐다.", why="샤오미가 대상에 포함된 사실을 주어로 다시 씀")
mv("tr_pipc26", "사건", ["Z4-E-039"], "AS·신뢰", event_type="인증·규제", statement="개인정보보호위원회는 2026년 9월 14일 로보락, 삼성전자, LG전자, 에코백스, 샤오미 로봇청소기 점검 결과 특별한 침해 위험은 없었다고 밝혔다. 일부 국외 이전 고지가 미흡하고 국내대리인을 지정하지 않은 사례가 있어 시정 권고를 의결했다. 업체명은 공개하지 않아 샤오미에 해당하는지는 알 수 없다.", why="샤오미가 대상에 포함된 사실과 귀속 불가를 명시")
mv("m_pipc", "지표", ["Z4-M-027"], "AS·신뢰", indicator="C4-T7")
# ===================== 판촉·마케팅 =====================
mv("mk_stk25", "사건", ["Z5-E-023"], "판촉·마케팅")
mv("mk_open25", "사건", ["Z5-E-024"], "판촉·마케팅")
mv("mk_chu25", "사건", ["Z5-E-027"], "판촉·마케팅")
mv("mk_live25", "사건", ["Z5-E-028"], "판촉·마케팅", event_type="판촉", why="신제품 출시 서술은 제품 기록에 있어 판촉 기록으로 다시 분류")
mv("mk_bf25", "사건", ["Z5-E-030"], "판촉·마케팅")
mv("mk_fan26", "사건", ["Z5-E-038"], "판촉·마케팅")
# ===================== 성과 =====================
mv("pf_stat23", "사건", ["Z1-E-012"], "성과", actor="샤오미", statement="헤럴드경제는 2023년 11월 8일 통계업체 스태티스타를 인용해 국내 로봇청소기 판매 1~3위가 로보락, 샤오미, 에코백스 순이라고 전했다. 브랜드별 점유율 수치와 기준 연도는 기사에 없다.", why="샤오미(2위) 순위를 주어로 다시 씀")
# ===================== 전망(샤오미 단독, 추적 유지) =====================
FC = {"f_store1": ["Z1-F-001"], "f_ex": ["Z1-F-002"], "f_svc": ["Z1-F-003", "Z4-F-003"], "f_big26": ["Z2-F-001"], "f_s45": ["Z3-F-001"],
      "f_ex27": ["Z1-F-006", "Z4-F-007"], "f_big27": ["Z2-F-007"], "f_store12": ["Z3-F-005"], "f_fan27": ["Z5-F-007"]}
for k, ids in FC.items():
    r0 = {x: y for x, y in Z[ids[0]].items() if x not in ("id", "question", "added_on", "first_seen", "origin", "intake")}
    r0.update(moved_from=ids, axis="전망", type="전망")
    R.append((k, r0))

# ===================== 보강(독립 조사 대조 후) =====================
exec(open(Path(__file__).with_name("c4_add.py"), encoding="utf-8").read()) if Path(__file__).with_name("c4_add.py").exists() else None

# ===================== 해석·분석 전망(새 질문 기준으로 새로 작성) =====================
exec(open(Path(__file__).with_name("c4_interp.py"), encoding="utf-8").read()) if Path(__file__).with_name("c4_interp.py").exists() else None

# ---------- ID 부여(키 고정) ----------
L = {"사건": "E", "지표": "M", "해석": "I", "전망": "F"}
used = set(AMAP.values())
cnt = {}
for k, r in R:
    if k not in AMAP:
        t = L[r["type"]]
        n = max([int(v.split("-")[2]) for v in AMAP.values() if v.split("-")[1] == t] + [0]) + 1
        AMAP[k] = f"C4-{t}-{n:03d}"
zmap = {}
for k, r in R:
    for z in r.get("moved_from", []):
        zmap.setdefault(z, AMAP[k])
ZFIX = {}
def fix(x): return ZFIX.get(x) or AMAP.get(x, zmap.get(x, x))
out = []
for k, r in R:
    r = dict(r)
    r.update(id=AMAP[k], question="C4", question_version="v2.0", first_seen="R1", added_on=ON, status=r.get("status", "유효"), replaces=None)
    if r.get("basis"):
        b = []
        for x in r["basis"]:
            y = fix(x)
            if y not in b: b.append(y)
        r["basis"] = b
    r.setdefault("importance", 2); r.setdefault("check_flags", []); r.setdefault("sources", [])
    if "why" in r: r["moved_why"] = r.pop("why")
    out.append(r)
AMAP_P.write_text(json.dumps(AMAP, ensure_ascii=False, indent=0), encoding="utf-8")
(Path(__file__).with_name("c4_zmap.json")).write_text(json.dumps(zmap, ensure_ascii=False, indent=0), encoding="utf-8")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_base.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sorted(out, key=lambda r: r["id"])), encoding="utf-8")
if not (OUT / "patches.jsonl").exists(): (OUT / "patches.jsonl").write_text("", encoding="utf-8")
from collections import Counter
print("기록", len(out), Counter(r["type"] for r in out), "축", Counter(r.get("axis") for r in out))
