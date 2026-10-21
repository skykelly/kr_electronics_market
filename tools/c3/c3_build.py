"""C3 에코백스(브랜드별 질문) 기록 생성.

1단계(재배치): 이전 기능별 기록(Z1~Z5)에서 에코백스이 주어인 사실 기록만 골라 중복을 합쳐 옮긴다.
  - 출처는 원 기록들의 합집합, moved_from에 원 ID를 남긴다. 문장을 고치면 why에 이유를 적는다.
  - 해석은 옮기지 않는다(새 질문 기준으로 새로 쓴다). 에코백스 단독 전망은 추적을 잇기 위해 옮긴다.
2단계(보강): 독립 조사 대조로 찾은 빈칸을 원문 확인 후 ADD로 더한다.
실행: python3 tools/c1/c1_build.py  → china-brands/c3/records_base.jsonl, c3_amap.json(키→ID 고정)
"""
import json, glob
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "china-brands/c3"
Z = {}
for f in glob.glob(str(ROOT / "china-legacy/z*/records.jsonl")):
    for l in open(f, encoding="utf-8"):
        r = json.loads(l); Z[r["id"]] = r
AMAP_P = Path(__file__).with_name("c3_amap.json")
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
mv("org_corp22", "사건", ["Z1-E-007"], "조직", statement="에코백스는 2022년 3월 22일 디봇 X1 패밀리 발표회에서 한국 법인을 올해 안에 설립할 계획이라고 밝혔다. 정철교 에코백스코리아 대표와 최용석 이사가 소개됐고, 지난해 국내 매출이 2019년 대비 약 3배 늘었다고 밝혔다. 자체 AS망은 별도 기록으로 분리했다.", event_type="전략·조직", why="자체 AS망 운영(5월 1일) 서술은 AS 기록으로 분리")
mv("org_apac24", "사건", ["Z1-E-014"], "조직", statement="에코백스 아시아태평양 총괄 매니저 웬촨 리우는 2024년 5월 7일 서울 성수동 발표회에서 한국을 매우 중요한 시장이라고 말했다.", event_type="전략·조직", why="전지현 모델 발표는 판촉 기록으로 분리")
mv("org_ceo25", "사건", ["Z1-E-022"], "조직")
# ===================== 제품 =====================
mv("p_x1", "사건", ["Z2-E-005"], "제품")
mv("p_24may", "사건", ["Z2-E-009"], "제품")
mv("p_24aug", "사건", ["Z2-E-010"], "제품")
mv("p_x8", "사건", ["Z2-E-016", "Z5-E-015"], "제품", why="같은 출시·가격 기록 2건을 합침")
mv("m_sku24", "지표", ["Z2-M-004"], "제품", indicator="C3-T2")
for k, i in [("m_px_x1o", "Z2-M-014"), ("m_px_x1t", "Z2-M-015"), ("m_px_x8", "Z2-M-016"), ("m_px_x8d", "Z2-M-017"), ("m_pa_x1", "Z2-M-035"), ("m_pa_x2", "Z2-M-036"), ("m_pa_x8", "Z2-M-037")]:
    mv(k, "지표", [i], "제품", indicator="C3-T8")
# ===================== 채널 =====================
mv("ch_gm22", "사건", ["Z3-E-009", "Z5-E-005"], "채널", event_type="채널·매장", why="같은 연말 판촉 기록 2건을 합침")
mv("m_ch22", "지표", ["Z3-M-009"], "채널", indicator="C3-T3")
mv("ch_cpg25", "사건", ["Z3-E-028", "Z2-E-022", "Z5-E-022"], "채널", event_type="채널·매장", why="같은 쿠팡 행사 기록 3건을 합침")
mv("m_cpg25", "지표", ["Z3-M-023"], "채널", indicator="C3-T9")
mv("ch_t50", "사건", ["Z5-E-025"], "채널", event_type="채널·매장", statement="쿠팡은 2025년 8월 10일 로봇청소기 셀렉트샵 행사를 열어 에코백스 디봇 T50 프로 옴니를 12.5% 할인해 8월 24일까지 사전예약을 받았다. 구매자 전원에게 전용 클리닝 용액을 주고 쿠팡안심케어를 쓰면 보증을 최대 5년까지 늘렸다.", why="쿠팡 행사 주체와 채널 축으로 다시 씀")
mv("ch_lhm26", "사건", ["Z3-E-040", "Z5-E-031"], "채널", event_type="채널·매장", why="같은 팝업 기록 2건을 합침")
# ===================== AS·신뢰 =====================
mv("as_own22", "사건", ["Z4-E-002"], "AS·신뢰", date="2022-03-22", event_type="구독·케어·AS")
mv("as_call23", "사건", ["Z4-E-005"], "AS·신뢰", event_type="구독·케어·AS")
mv("m_wty24", "지표", ["Z4-M-019"], "AS·신뢰", indicator="C3-T4")
mv("as_eng24", "사건", ["Z4-E-009"], "AS·신뢰", event_type="구독·케어·AS")
mv("as_63", "사건", ["Z4-E-013", "Z1-E-023"], "AS·신뢰", event_type="구독·케어·AS", check_flags=["센터 수 증가 전 값이 36곳(비즈니스워치 2025-02-05)과 27곳(전자신문 2025-05-27)으로 보도마다 다름"], why="같은 보도 2건을 합침")
mv("as_cpg25", "사건", ["Z3-E-029", "Z4-E-024"], "AS·신뢰", event_type="구독·케어·AS", check_flags=["센터 수 증가 전 값이 27곳(전자신문)과 36곳(비즈니스워치)으로 상충", "하이마트 AS 접수와 쿠팡 AS 시작 여부는 후속 원문을 찾지 못함"], why="같은 전자신문 기사의 2개 기록을 합침")
mv("as_gs25", "사건", ["Z4-E-023"], "AS·신뢰", event_type="구독·케어·AS")
mv("m_asc63", "지표", ["Z4-M-009", "Z1-M-008"], "AS·신뢰", indicator="C3-T4")
mv("m_eng1000", "지표", ["Z4-M-012"], "AS·신뢰", indicator="C3-T4")
mv("tr_hack24", "사건", ["Z4-E-014"], "AS·신뢰", event_type="인증·규제")
mv("tr_pipc25", "사건", ["Z4-E-018"], "AS·신뢰", event_type="인증·규제", statement="개인정보보호위원회는 2025년 3월 4일 삼성전자, LG전자, 샤오미, 에코백스, 로보락의 로봇청소기를 대상으로 개인정보 수집·관리 실태를 사전 점검한다고 발표했다. 에코백스가 점검 대상에 포함됐다.", why="에코백스가 대상에 포함된 사실을 주어로 다시 씀")
mv("tr_policy25", "사건", ["Z4-E-019"], "AS·신뢰", event_type="인증·규제", statement="전자신문은 2025년 3월 11일 브랜드별 개인정보 처리방침을 비교하며 에코백스가 알리바바클라우드와 바이두 등 중국 업체로의 전송과 싱가포르 저장을 처리방침에 적었다고 전했다.", why="드리미 서술은 C2 대상이라 제외")
mv("tr_kisa25", "사건", ["Z4-E-030"], "AS·신뢰", event_type="인증·규제", sources=[{"grade": "B", "publisher": "뉴데일리", "url": "https://biz.newdaily.co.kr/site/data/html/2025/09/02/2025090200368.html", "date": "2025-09-02"}] + [], statement="한국소비자원과 한국인터넷진흥원(KISA)이 2025년 9월 2일 로봇청소기 6종의 보안 40개 항목 점검 결과를 발표했다. 에코백스 디봇 X8 프로 옴니는 앱 사용자 인증 미비 3종 중 하나이고, 하드웨어 보안 수준이 상대적으로 낮은 2종(드리미·에코백스) 중 하나로 보도됐다. 에코백스는 한국 소비자 권익 보호에 협력하겠다며 보완 소프트웨어 업데이트를 모두 마쳤다고 밝혔다.", why="타 브랜드 결과는 해당 브랜드 질문으로 분리하고 뉴데일리 원문으로 에코백스 항목을 보강", check_flags=["지적된 사진 노출·카메라 강제 작동 취약점이 어느 제품에 해당하는지 기사에 구분이 없음"])
mv("tr_pipc26", "사건", ["Z4-E-039"], "AS·신뢰", event_type="인증·규제", statement="개인정보보호위원회는 2026년 9월 14일 로보락, 삼성전자, LG전자, 에코백스, 샤오미 로봇청소기 점검 결과 특별한 침해 위험은 없었다고 밝혔다. 일부 국외 이전 고지가 미흡하고 국내대리인을 지정하지 않은 사례가 있어 시정 권고를 의결했다. 업체명은 공개하지 않아 에코백스에 해당하는지는 알 수 없다.", why="에코백스가 대상에 포함된 사실과 귀속 불가를 명시")
mv("m_pipc", "지표", ["Z4-M-027"], "AS·신뢰", indicator="C3-T7")
# ===================== 판촉·마케팅 =====================
mv("mk_hyun22", "사건", ["Z5-E-004"], "판촉·마케팅")
mv("mk_jun24", "사건", ["Z5-E-012"], "판촉·마케팅")
mv("mk_trade26", "사건", ["Z5-E-037"], "판촉·마케팅")
mv("mk_cpg26", "사건", ["Z5-E-053"], "판촉·마케팅", statement="2026년 10월 12일 시작한 쿠팡 쿠가세(가전디지털 세일)에 에코백스가 참여 브랜드로 언급됐다(로보락, 드리미, TCL, 하이센스도 참여).", why="에코백스 참여 사실을 주어로 다시 씀")
# ===================== 성과 =====================
mv("pf_stat23", "사건", ["Z1-E-012"], "성과", actor="에코백스", statement="헤럴드경제는 2023년 11월 8일 통계업체 스태티스타를 인용해 국내 로봇청소기 판매 1~3위가 로보락, 샤오미, 에코백스 순이라고 전했다. 브랜드별 점유율 수치와 기준 연도는 기사에 없다.", why="에코백스(3위) 순위를 주어로 다시 씀")
mv("pf_share24", "사건", ["Z1-E-028"], "성과", statement="한국경제는 2025년 5월 19일 시장조사업체 자료로 에코백스의 2024년 한국 점유율이 4%로 전년보다 10%p 낮아졌다고 전했다. 조사기관 이름은 기사에 없다.", event_type="실적·시장", claim_type="해당 없음", external_check=None, why="서비스센터·택배 수리 서술은 AS 기록으로 분리", check_flags=["조사기관 미명시", "점유율 기준(금액·대수)과 전년 값 미상"])
# ===================== 전망(에코백스 단독, 추적 유지) =====================
FC = {"f_corp": ["Z1-F-005"], "f_cpg": ["Z3-F-004", "Z4-F-002"]}
for k, ids in FC.items():
    r0 = {x: y for x, y in Z[ids[0]].items() if x not in ("id", "question", "added_on", "first_seen", "origin", "intake")}
    r0.update(moved_from=ids, axis="전망", type="전망")
    R.append((k, r0))

# ===================== 보강(독립 조사 대조 후) =====================
exec(open(Path(__file__).with_name("c3_add.py"), encoding="utf-8").read()) if Path(__file__).with_name("c3_add.py").exists() else None

# ===================== 해석·분석 전망(새 질문 기준으로 새로 작성) =====================
exec(open(Path(__file__).with_name("c3_interp.py"), encoding="utf-8").read()) if Path(__file__).with_name("c3_interp.py").exists() else None

# ---------- ID 부여(키 고정) ----------
L = {"사건": "E", "지표": "M", "해석": "I", "전망": "F"}
used = set(AMAP.values())
cnt = {}
for k, r in R:
    if k not in AMAP:
        t = L[r["type"]]
        n = max([int(v.split("-")[2]) for v in AMAP.values() if v.split("-")[1] == t] + [0]) + 1
        AMAP[k] = f"C3-{t}-{n:03d}"
zmap = {}
for k, r in R:
    for z in r.get("moved_from", []):
        zmap.setdefault(z, AMAP[k])
ZFIX = {}
def fix(x): return ZFIX.get(x) or AMAP.get(x, zmap.get(x, x))
out = []
for k, r in R:
    r = dict(r)
    r.update(id=AMAP[k], question="C3", question_version="v2.0", first_seen="R1", added_on=ON, status=r.get("status", "유효"), replaces=None)
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
(Path(__file__).with_name("c3_zmap.json")).write_text(json.dumps(zmap, ensure_ascii=False, indent=0), encoding="utf-8")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_base.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sorted(out, key=lambda r: r["id"])), encoding="utf-8")
if not (OUT / "patches.jsonl").exists(): (OUT / "patches.jsonl").write_text("", encoding="utf-8")
from collections import Counter
print("기록", len(out), Counter(r["type"] for r in out), "축", Counter(r.get("axis") for r in out))
