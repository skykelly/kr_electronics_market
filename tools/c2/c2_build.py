"""C2 드리미(브랜드별 질문) 기록 생성.

1단계(재배치): 이전 기능별 기록(Z1~Z5)에서 드리미이 주어인 사실 기록만 골라 중복을 합쳐 옮긴다.
  - 출처는 원 기록들의 합집합, moved_from에 원 ID를 남긴다. 문장을 고치면 why에 이유를 적는다.
  - 해석은 옮기지 않는다(새 질문 기준으로 새로 쓴다). 드리미 단독 전망은 추적을 잇기 위해 옮긴다.
2단계(보강): 독립 조사 대조로 찾은 빈칸을 원문 확인 후 ADD로 더한다.
실행: python3 tools/c1/c1_build.py  → china-brands/c2/records_base.jsonl, c2_amap.json(키→ID 고정)
"""
import json, glob
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "china-brands/c2"
Z = {}
for f in glob.glob(str(ROOT / "china-legacy/z*/records.jsonl")):
    for l in open(f, encoding="utf-8"):
        r = json.loads(l); Z[r["id"]] = r
AMAP_P = Path(__file__).with_name("c2_amap.json")
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
mv("org_kolon23", "사건", ["Z1-E-009", "Z4-E-006"], "조직", why="같은 파트너십 발표 2건을 합침")
mv("org_goal26", "사건", ["Z1-E-038"], "조직")
mv("org_inseoul26", "사건", ["Z1-E-044", "Z1-E-045"], "조직", date="2026-08-21", statement="2026년 8월 20~21일 한강 가빛섬에서 연 '드리미 인 서울'에서 한국을 핵심 전략시장으로 규정했다. 기사는 한국·일본·호주 지역 총괄 이사와 한국 법인 대표 등 경영진이 발표한다고 예고했다. 마케팅 총괄은 김명환, 홍보 총괄은 권기현이다. 법인 대표 이름은 기사에 없다.", event_type="전략·조직", why="행사 예고와 행사 결과 2건을 합치고 서비스센터 수치는 AS 기록으로 분리")
mv("org_dist26", "사건", ["Z1-E-047"], "조직", date="2026-09-09", statement="아시아경제는 2026년 9월 9일 드리미 테크놀로지의 국내 공식 총판이 오진양행이며 네이버 스마트스토어를 운영한다고 전했다.", event_type="전략·조직", why="같은 기사의 추석 판촉은 판촉 기록으로 분리", check_flags=["코오롱글로벌(공식 수입원, 2023·2025 기록)과 오진양행(총판)의 관계와 전환 시점 확인 필요"])
# ===================== 제품 =====================
mv("p_l20", "사건", ["Z2-E-006", "Z1-E-010", "Z5-E-007"], "제품", date="2023-08-21", statement="2023년 8월 21일 로봇청소기 L20 Ultra를 정식 출시했다. 코오롱글로벌 상사사업부문이 공식 수입하며 사전예약은 8월 10일부터 11일간 11% 이상 할인으로 받았다. 흡입력 7,000Pa, 모서리 2mm까지 닿는 물걸레 패드 확장, 패드 자동 탈부착, 물걸레 리프팅 10.5mm, 55개 물체 인식을 내세웠다. 판매가는 기사에 없다.", event_type="제품 출시", why="같은 출시·수입·사전예약 기록 3건을 합침")
mv("p_x50", "사건", ["Z2-E-012"], "제품")
mv("p_26plan", "사건", ["Z2-E-031"], "제품", statement="드리미테크놀로지코리아 문덕근 상무는 2026년 3월 25일 공기청정기·정수기·선풍기를 상반기에, TV와 세탁건조기를 하반기에 출시할 계획이라고 밝혔다.", event_type="제품 출시", why="잠실 팝업은 채널 기록으로 분리")
mv("p_26water", "사건", ["Z2-E-032"], "제품")
mv("p_26aqua", "사건", ["Z2-E-039", "Z5-E-046"], "제품", date="2026-08-21", statement="2026년 8월 21일 '드리미 인 서울'에서 아쿠아 20 울트라 롤러(아쿠아 스팀)를 출시했다. 최대 흡입력은 40,000Pa다. 드리미는 흡입력을 파스칼에서 와트로 바꾸거나 병기할 계획이 아직 없다고 밝혔다.", event_type="제품 출시", why="같은 행사 기록 2건을 합치고 X60 서비스 5년 프로그램은 AS 기록으로 분리")
mv("m_pa_l20", "지표", ["Z2-M-033"], "제품", indicator="C2-T8")
mv("m_pa_aqua", "지표", ["Z2-M-034"], "제품", indicator="C2-T8")
# ===================== 채널 =====================
mv("ch_flag25", "사건", ["Z1-E-027", "Z3-E-027", "Z5-E-021", "Z4-E-022", "Z2-E-020"], "채널", date="2025-05-11", statement="2025년 5월 서울 한남동 나인원한남에 한국 첫 플래그십 스토어를 열었다. 제품 체험, 구매 상담, AS 상담을 한곳에서 하고 X50s Pro Ultra, 음식물처리기, 공기청정기, 정수기, 헤어 스타일링 제품을 체험할 수 있다. 서비스 데스크는 평일 운영하고 택배 수리가 가능하며 품질보증 기간에는 무상이다. 일부 제품은 출시 예정으로 소개됐다.", event_type="채널·매장", why="같은 개점 기록 5건을 합침")
mv("ch_pop26", "사건", ["Z3-E-042", "Z5-E-034"], "채널", event_type="채널·매장", why="같은 팝업 기록 2건을 합침")
mv("m_ch_chu", "지표", ["Z3-M-011"], "채널", indicator="C2-T9")
# ===================== AS·신뢰 =====================
mv("as_nearby", "사건", ["Z1-E-031", "Z4-E-029", "Z3-E-039"], "AS·신뢰", event_type="구독·케어·AS", statement="드리미가 A/S 서비스 '니어바이(Nearby)'를 2025년 9월 시작했다. 공식 수입원 코오롱글로벌을 통해 정식 판매된 로봇청소기가 대상이다. 12월 15일 롯데하이마트, SK네트웍스서비스와 3사 협의로 범위를 넓혀 구매처나 제품 종류와 관계없이 전국 롯데하이마트 지점에서 수리를 접수한다(음식물처리기 제외).", why="같은 AS 체계 기록 3건을 합침")
mv("as_net26", "사건", ["Z4-E-038", "Z3-E-051"], "AS·신뢰", event_type="구독·케어·AS", date="2026-08-21", why="같은 발표 2건을 합침")
mv("as_dm26", "사건", ["Z5-E-041"], "AS·신뢰", event_type="구독·케어·AS")
mv("tr_policy25", "사건", ["Z4-E-019"], "AS·신뢰", date="2025-03-11", event_type="인증·규제", statement="전자신문은 2025년 3월 11일 브랜드별 개인정보 처리방침을 비교하며 드리미가 미국·독일·싱가포르 데이터센터를 쓰고 수집 항목이 불명확하다고 적었다고 전했다.", why="에코백스 서술은 C3 대상이라 제외")
mv("tr_kisa25", "사건", ["Z4-E-030"], "AS·신뢰", event_type="인증·규제", statement="한국소비자원과 한국인터넷진흥원(KISA)이 2025년 9월 2일 로봇청소기 6개 제품의 40개 항목 점검 결과를 발표했다(조사 2025년 3~7월). 보도는 드리미 X50 울트라에 카메라 강제 작동과 개인정보 노출 우려가 지적됐다고 전했다. 업체들은 즉시 조치했다고 전해졌다.", why="타 브랜드 결과는 해당 브랜드 질문으로 분리")
mv("m_cn_coop29", "지표", ["Z1-M-009", "Z4-M-006"], "AS·신뢰", indicator="C2-T4")
mv("m_cn_coop30", "지표", ["Z1-M-010", "Z4-M-007"], "AS·신뢰", indicator="C2-T4")
mv("m_cn_lhm310", "지표", ["Z1-M-011", "Z3-M-018", "Z4-M-008"], "AS·신뢰", indicator="C2-T4")
mv("m_x60_5y", "지표", ["Z4-M-023"], "AS·신뢰", indicator="C2-T4")
add("m_rc20", "지표", "AS·신뢰", indicator="C2-T4", value=20, unit="곳", as_of="2025-05", region="한국", importance=2, claim_type="해당 없음",
    statement="전자신문은 2025년 5월 27일 에코백스 수리센터가 63곳으로 늘어 로보락 22곳, 드리미 20곳의 3배 이상이라고 전했다. 직영과 협력 센터 구분은 기사에 없다.",
    sources=_src(["Z4-E-024"]), moved_from=["Z4-E-024"], moved_why="경쟁사 비교 기사에서 드리미 값만 지표로 분리", check_flags=["경쟁사 비교 기사 인용이며 드리미 직접 발표가 아님. 센터 운영 주체 확인 필요"])
# ===================== 판촉·마케팅 =====================
mv("mk_x50", "사건", ["Z5-E-013", "Z3-E-019"], "판촉·마케팅", why="같은 캠페인 기록 2건을 합침")
mv("mk_price26", "사건", ["Z5-E-036"], "판촉·마케팅")
mv("mk_amb26", "사건", ["Z5-E-044"], "판촉·마케팅")
mv("mk_chu26", "사건", ["Z5-E-049", "Z3-E-055", "Z2-E-041"], "판촉·마케팅", sources=_src(["Z5-E-049", "Z3-E-055", "Z2-E-041", "Z1-E-047"]), date="2026-09-09",
   statement="드리미가 2026년 9월 추석 판촉을 GS샵(9월 10일 22시 55분), 지마켓 G라이브(9월 17일), 11번가, 네이버, 쿠팡과 오진양행 스마트스토어에서 열었다. 아시아경제는 최대 53% 할인이라고 전했다. 로봇청소기 아쿠아 스팀과 X60, L시리즈, T16 프로 스팀 습건식 물걸레 청소기, 펫 공기청정기 AP10·FP10, 헤어가전 5종, 날개 없는 선풍기 MF10, 에어프라이어+전기그릴 AG10, 이중 조리가전 DZ30이 나왔다.", why="같은 판촉 기록 3건을 합치고 할인율은 총판 기사(Z1-E-047)에서 가져옴")
mv("mk_lhm26", "사건", ["Z5-E-051"], "판촉·마케팅", statement="롯데하이마트가 2026년 10월 한 달간 전국 매장 이사·혼수 가전 행사와 청소기 할인전을 열었고 드리미 아쿠아10을 59만 9천 원에 팔았다(같은 행사 로보락 S10 맥스V 울트라 149만 원, 다이슨 r2 112만 원). 제휴 카드 캐시백이 붙었다.", why="유통사 행사에서 드리미 가격을 주어로 다시 씀")
mv("mk_cpg26", "사건", ["Z5-E-053"], "판촉·마케팅", statement="2026년 10월 12일 시작한 쿠팡 쿠가세(가전디지털 세일)에 드리미가 참여 브랜드로 언급됐다(로보락, 에코백스, TCL, 하이센스도 참여).", why="드리미 참여 사실을 주어로 다시 씀")
# ===================== 성과 =====================
mv("pf_share25", "사건", ["Z3-E-033"], "성과")
mv("pf_prem26", "사건", ["Z5-E-050"], "성과", statement="스마트비즈는 2026년 10월 9일 롯데하이마트 10월 가전 할인전 기사에서 드리미의 130만 원 이상 프리미엄 로봇청소기 점유율이 올해 상반기 5%에서 12%로 올랐다고 적었다. 같은 기사는 중국 브랜드(로보락, 드리미, 에코백스)가 지난해 한국 시장의 약 60%를 차지한 것으로 추정된다고 전했다. 조사기관은 기사에 없다.", why="드리미 수치를 주어로 다시 씀")
# ===================== 전망(드리미 단독, 추적 유지) =====================
FC = {"f_direct": ["Z1-F-007"], "f_h1": ["Z2-F-002"], "f_h2": ["Z2-F-003"], "f_tv": ["Z2-F-009"], "f_store": ["Z3-F-007"], "f_ad": ["Z5-F-006"]}
for k, ids in FC.items():
    r0 = {x: y for x, y in Z[ids[0]].items() if x not in ("id", "question", "added_on", "first_seen", "origin", "intake")}
    r0.update(moved_from=ids, axis="전망", type="전망")
    R.append((k, r0))

# ===================== 보강(독립 조사 대조 후) =====================
exec(open(Path(__file__).with_name("c2_add.py"), encoding="utf-8").read()) if Path(__file__).with_name("c2_add.py").exists() else None

# ===================== 해석·분석 전망(새 질문 기준으로 새로 작성) =====================
exec(open(Path(__file__).with_name("c2_interp.py"), encoding="utf-8").read()) if Path(__file__).with_name("c2_interp.py").exists() else None

# ---------- ID 부여(키 고정) ----------
L = {"사건": "E", "지표": "M", "해석": "I", "전망": "F"}
used = set(AMAP.values())
cnt = {}
for k, r in R:
    if k not in AMAP:
        t = L[r["type"]]
        n = max([int(v.split("-")[2]) for v in AMAP.values() if v.split("-")[1] == t] + [0]) + 1
        AMAP[k] = f"C2-{t}-{n:03d}"
zmap = {}
for k, r in R:
    for z in r.get("moved_from", []):
        zmap.setdefault(z, AMAP[k])
ZFIX = {}
def fix(x): return ZFIX.get(x) or AMAP.get(x, zmap.get(x, x))
out = []
for k, r in R:
    r = dict(r)
    r.update(id=AMAP[k], question="C2", question_version="v2.0", first_seen="R1", added_on=ON, status=r.get("status", "유효"), replaces=None)
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
(Path(__file__).with_name("c2_zmap.json")).write_text(json.dumps(zmap, ensure_ascii=False, indent=0), encoding="utf-8")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_base.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sorted(out, key=lambda r: r["id"])), encoding="utf-8")
if not (OUT / "patches.jsonl").exists(): (OUT / "patches.jsonl").write_text("", encoding="utf-8")
from collections import Counter
print("기록", len(out), Counter(r["type"] for r in out), "축", Counter(r.get("axis") for r in out))
