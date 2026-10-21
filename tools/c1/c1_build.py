"""C1 로보락(브랜드별 질문) 기록 생성.

1단계(재배치): 이전 기능별 기록(Z1~Z5)에서 로보락이 주어인 사실 기록만 골라 중복을 합쳐 옮긴다.
  - 출처는 원 기록들의 합집합, moved_from에 원 ID를 남긴다. 문장을 고치면 why에 이유를 적는다.
  - 해석은 옮기지 않는다(새 질문 기준으로 새로 쓴다). 로보락 단독 전망은 추적을 잇기 위해 옮긴다.
2단계(보강): 독립 조사 대조로 찾은 빈칸을 원문 확인 후 ADD로 더한다.
실행: python3 tools/c1/c1_build.py  → china-brands/c1/records_base.jsonl, c1_amap.json(키→ID 고정)
"""
import json, glob
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "china-brands/c1"
Z = {}
for f in glob.glob(str(ROOT / "china-legacy/z*/records.jsonl")):
    for l in open(f, encoding="utf-8"):
        r = json.loads(l); Z[r["id"]] = r
AMAP_P = Path(__file__).with_name("c1_amap.json")
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
mv("org_corp", "사건", ["Z1-E-003"], "조직")
mv("org_mkt24", "사건", ["Z1-E-013"], "조직", statement="2024년 4월 S8 맥스V 울트라 론칭쇼에서 한국 마케팅 총괄(김서영)과 아시아태평양 마케팅 총괄(댄 챔)이 소개됐다. 한국 법인 대표 이름은 기사에 없다.", event_type="전략·조직", why="원 기록은 AS 접수와 조직을 함께 적어 조직 사실만 남김")
mv("org_glob26", "사건", ["Z1-E-046"], "성과", event_type="실적·시장", claim_type="자사 집계", external_check="미확보")
# ===================== 제품 =====================
mv("p_20", "사건", ["Z2-E-002", "Z3-E-004", "Z5-E-003"], "제품", statement="2020년 4월 13일 로봇청소기 S5 MAX와 무선청소기 H6의 국내 출시를 발표했고 한국 공식 웹사이트(kr.roborock.com)를 운영했다. 6월 2일에는 S5 MAX가 이베이코리아 빅스마일데이 G마켓 디지털·가전 판매 3위라고 밝혔다.", why="같은 출시·판매 사실을 담은 3개 기록을 합침")
mv("p_21", "사건", ["Z2-E-003", "Z1-E-005", "Z3-E-005"], "채널", statement="2021년 12월 1일 공식 네이버 스마트스토어를 열고 S7 Plus, S7, S6 MaxV, S5 Max, 다이애드, H7, 오토 엠프티 도크 7종을 입점시켰다. S7 Plus(2021년 9월 출시)는 자동 먼지 비움 도크를 묶은 구성이다.", event_type="채널·매장", why="같은 스마트스토어 개설 기록 3건을 합침")
mv("p_22", "사건", ["Z2-E-004"], "제품")
mv("p_24", "사건", ["Z2-E-008"], "제품")
mv("p_24w", "사건", ["Z2-E-011"], "제품")
mv("p_25", "사건", ["Z2-E-017"], "제품")
mv("p_25b", "사건", ["Z2-E-019"], "제품", statement="2025년 3월 무선 습건식 청소기 F25 에이스 콤보(3월 17일)와 세탁건조기 H1 라이트(3월 20일, 세탁 10kg·건조 6kg)를 추가로 냈다.", why="매장 수(370곳)는 채널 기록으로 분리")
mv("p_26", "사건", ["Z2-E-029"], "제품")
mv("p_26w", "사건", ["Z2-E-037"], "제품")
mv("p_26f", "사건", ["Z2-E-040", "Z3-E-054", "Z5-E-048"], "제품", statement="2026년 9월 3~13일 스타필드 수원 팝업에서 무선 습건식 청소기 F25 울트라 스팀 Gen 2를 처음 공개하고 국내 출시 예정이라고 했다. 출시일과 사양은 공개되지 않았다.", why="같은 공개 사실 3건을 합침")
mv("p_26s", "사건", ["Z5-E-052"], "판촉·마케팅")
mv("m_sku21", "지표", ["Z2-M-001"], "제품", indicator="C1-T2")
mv("m_sku24", "지표", ["Z2-M-002"], "제품", indicator="C1-T2")
mv("m_sku25", "지표", ["Z2-M-003"], "제품", indicator="C1-T2")
for k, i in [("m_px_s10", "Z2-M-009"), ("m_px_s10d", "Z2-M-010"), ("m_px_h1", "Z2-M-011"), ("m_px_m1", "Z2-M-012"), ("m_px_s8", "Z2-M-013"),
             ("m_pa_s7", "Z2-M-029"), ("m_pa_s8", "Z2-M-030"), ("m_pa_s9", "Z2-M-031"), ("m_pa_s10", "Z2-M-032"), ("m_kg_h1", "Z2-M-038"), ("m_kg_zx", "Z2-M-039")]:
    mv(k, "지표", [i], "제품", indicator="C1-T8")
# ===================== 채널 =====================
mv("ch_21", "사건", ["Z1-E-006"], "채널", event_type="채널·매장")
mv("ch_lhm22", "사건", ["Z3-E-007", "Z1-E-008"], "채널", statement="2022년 6월 롯데하이마트에 입점해 전국 49개 매장에서 판매했다고 테크42가 전했다.", event_type="채널·매장", date="2022-06", why="AS 협약(4월)은 AS 기록으로 분리")
mv("ch_cj23a", "사건", ["Z3-E-010", "Z5-E-006"], "채널", statement="2023년 6월 6일 CJ온스타일 '강주은의 굿라이프'에서 S8 Pro Ultra(170만 원대)를 방송해 2천 대를 4분 만에 팔고 주문액 30억 원을 기록했다. 같은 해 3월 S7 방송은 26분 동안 1,500개, 주문액 약 18억 원이었다.", why="같은 방송 기록 2건을 합침")
mv("ch_cj23b", "사건", ["Z3-E-011", "Z5-E-008"], "채널")
mv("ch_cj23c", "사건", ["Z3-E-013", "Z5-E-010"], "채널")
mv("ch_cj24", "사건", ["Z5-E-011"], "채널", event_type="채널·매장")
mv("ch_flag24", "사건", ["Z3-E-017", "Z1-E-016"], "채널", statement="2024년 7월 스타필드 하남에 첫 플래그십 스토어를 열었고 이후 스타필드 고양에 열었다.", event_type="채널·매장", why="매장 수(2025-03)는 별도 기록으로 분리")
mv("ch_370", "사건", ["Z3-E-024", "Z2-E-019", "Z1-E-016"], "채널", statement="2025년 3월 기준 백화점 37곳, 롯데하이마트와 아이나비 직영점 331곳, 플래그십 스토어 등 총 370개 매장을 운영한다고 밝혔다.", event_type="채널·매장", date="2025-03-31", why="매장 수 서술 3건을 합침")
mv("ch_pop25", "사건", ["Z3-E-025", "Z5-E-017"], "채널", event_type="채널·매장")
mv("ch_sub25", "사건", ["Z3-E-026", "Z4-E-021"], "채널")
mv("ch_pop26a", "사건", ["Z2-E-038", "Z3-E-050", "Z5-E-045"], "채널", statement="2026년 8월 3~16일 현대백화점 판교점 7층 팝업에서 세탁건조기 제오엑스를 S10 맥스V, H60 허브, F25 시리즈와 함께 전시하고 팝업 전용 특가로 팔았다.", event_type="채널·매장", why="같은 팝업 기록 3건을 합침")
mv("ch_pop26b", "사건", ["Z3-E-052", "Z5-E-047"], "채널", statement="2026년 8월 29일~9월 20일 롯데하이마트 잠실점에서 S10 맥스V 울트라 팝업을 열어 시연·상담을 하고 구매 고객 대상 100% 당첨 경품 추첨(1등 음식물처리기)을 했다.", event_type="채널·매장", why="같은 팝업 기록 2건을 합침")
mv("m_st22", "지표", ["Z3-M-001", "Z1-M-004"], "채널", indicator="C1-T3")
mv("m_st25", "지표", ["Z3-M-002"], "채널", indicator="C1-T3")
for k, i in [("m_cj23s7", "Z3-M-019"), ("m_cj23s8p", "Z3-M-020"), ("m_cj23s8", "Z3-M-021"), ("m_cj23ytd", "Z3-M-022")]:
    mv(k, "지표", [i], "채널", indicator="C1-T9")
# ===================== AS·신뢰 =====================
mv("as_sk22", "사건", ["Z4-E-004", "Z1-E-008"], "AS·신뢰", statement="2022년 4월 SK네트웍스서비스와 AS 업무협약을 맺었다.", event_type="구독·케어·AS", date="2022-04", why="하이마트 입점(6월)은 채널 기록으로 분리")
mv("as_344", "사건", ["Z4-E-007", "Z3-E-014", "Z1-E-013"], "AS·신뢰", statement="2024년 4월 16일 S8 맥스V 울트라 론칭쇼에서 전국 344개 롯데하이마트 지점에서 주말 포함 오전 10시~오후 8시에 AS를 접수한다고 밝혔다.", event_type="구독·케어·AS", why="같은 발표 3건을 합침")
mv("as_352", "사건", ["Z4-E-010", "Z1-E-017", "Z3-E-018"], "AS·신뢰", event_type="구독·케어·AS")
mv("as_25", "사건", ["Z4-E-015", "Z1-E-024"], "AS·신뢰")
mv("as_26", "사건", ["Z4-E-033", "Z1-E-037"], "AS·신뢰", statement="2026년 2월 26일 S10 맥스V 울트라 론칭에서 공식 AS센터 15곳(국내 총판 팅크웨어모바일 운영, 오전 8시~오후 6시)과 롯데하이마트 315개 매장 수리 접수를 밝히고, 3월부터 주요 로봇청소기 출장 AS를 시작한다고 했다.", event_type="구독·케어·AS", why="트러스트 센터는 별도 기록으로 분리")
mv("as_26b", "사건", ["Z4-E-037", "Z3-E-049"], "AS·신뢰", statement="2026년 7월 기준 공식 AS센터 15곳이 오전 8시~오후 6시, 롯데하이마트 315개 매장이 오전 10시~오후 8시 연중무휴로 수리를 접수하고, 직배수 스테이션 출장 AS가 2026년 2월 시작됐다고 뉴데일리가 전했다.", event_type="구독·케어·AS", why="같은 시점 운영 현황 2건을 합침")
mv("as_5y", "사건", ["Z4-E-034", "Z5-E-032"], "AS·신뢰", statement="S10 맥스V 울트라 론칭 프로모션(2026년 2월 27일~3월 8일) 구매 고객에게 기존 2년에 3년을 더한 총 5년 무상 AS를 줬다.", event_type="구독·케어·AS", why="같은 프로모션 2건을 합침")
mv("as_pet26", "사건", ["Z4-E-036", "Z1-E-043", "Z3-E-048", "Z5-E-042"], "AS·신뢰", statement="2026년 6월 25일 네이버 쇼핑라이브 구매자에게 반려동물 오물 사고 안심 보장(택배 접수 후 팅크웨어모바일 직영 서비스센터가 세척·재발송, 수령 후 6개월 이내 2회), 6월 28일 현대홈쇼핑 구매자에게 시니어 대상 설치·앱 설정·교육 서비스를 시범으로 제공했다.", event_type="구독·케어·AS", why="같은 시범 서비스 4건을 합침")
mv("as_kcsi", "사건", ["Z4-E-040"], "AS·신뢰")
for k, i in [("m_asc25", "Z4-M-001"), ("m_asc26", "Z4-M-003"), ("m_lhmr25", "Z4-M-002"), ("m_as344", "Z4-M-004"), ("m_as352", "Z3-M-016"), ("m_as315", "Z4-M-005"),
             ("m_wty1", "Z4-M-013"), ("m_wty2", "Z4-M-014"), ("m_wty5", "Z4-M-015")]:
    mv(k, "지표", [i], "AS·신뢰", indicator="C1-T4")
mv("tr_priv", "사건", ["Z4-E-017", "Z1-E-025"], "AS·신뢰", statement="2025년 2월 개인정보 처리방침 중 투야(Tuya) 등과 정보가 공유될 수 있다는 문구가 논란이 되자 입장문을 내 TÜV 라인란드 인증, TLS 암호화, 영상·오디오 서버 미저장을 설명했다. 2월 20일 론칭쇼에서는 문구를 검토 중이라고 밝혔다. 개인정보보호위원회는 사실관계를 파악 중이라고 했다.", event_type="인증·규제", why="같은 논란을 다룬 2건을 합침")
mv("tr_pipc25", "사건", ["Z4-E-018"], "AS·신뢰")
mv("tr_rev25", "사건", ["Z4-E-020"], "AS·신뢰")
mv("tr_kisa25", "사건", ["Z4-E-030"], "AS·신뢰")
mv("tr_trust26", "사건", ["Z4-E-032"], "AS·신뢰")
mv("tr_pipc26", "사건", ["Z4-E-039"], "AS·신뢰")
mv("m_pipc25", "지표", ["Z4-M-027"], "AS·신뢰", indicator="C1-T7")
mv("m_rev25", "지표", ["Z4-M-028"], "AS·신뢰", indicator="C1-T7")
# ===================== 판촉·마케팅 =====================
mv("mk_launch25", "사건", ["Z1-E-025"], "판촉·마케팅", statement="2025년 2월 20일 서울 파르나스 호텔에서 2025 론칭쇼를 열고 S9 맥스V 시리즈를 공개했다. 아시아태평양 마케팅 총괄 댄 챔이 발표했고 오프라인 매장을 늘릴 계획이라고 밝혔다.", event_type="마케팅", why="개인정보 문구 논란은 신뢰 기록으로 분리")
mv("mk_ad25", "사건", ["Z5-E-016"], "판촉·마케팅")
mv("mk_cgv25", "사건", ["Z5-E-018"], "판촉·마케팅")
mv("mk_award25", "사건", ["Z5-E-026"], "판촉·마케팅")
mv("mk_sale25", "사건", ["Z5-E-019"], "판촉·마케팅")
mv("mk_s10px", "사건", ["Z5-E-035"], "판촉·마케팅")
mv("mk_lhm26a", "사건", ["Z5-E-051"], "판촉·마케팅", statement="롯데하이마트가 2026년 10월 한 달간 전국 매장 이사·혼수 가전 행사와 청소기 할인전에서 로보락 S10 맥스V 울트라를 149만 원에 팔았다(같은 행사 드리미 아쿠아10 59만 9천 원, 다이슨 r2 112만 원). 제휴 카드 캐시백이 붙었다.", why="유통사 행사에서 로보락 가격을 주어로 다시 씀")
mv("mk_lhm26b", "사건", ["Z5-E-054"], "판촉·마케팅")
mv("mk_cpg26", "사건", ["Z5-E-053"], "판촉·마케팅", statement="2026년 10월 12일 시작한 쿠팡 쿠가세(가전디지털 세일)에 로보락이 참여 브랜드로 언급됐다(드리미, 에코백스, TCL, 하이센스도 참여).", why="로보락 참여 사실을 주어로 다시 씀")
# ===================== 전망(로보락 단독, 추적 유지) =====================
FC = {"f_asc": ["Z1-F-008", "Z4-F-006"], "f_f25": ["Z2-F-004"], "f_pa": ["Z2-F-005"], "f_lhm": ["Z3-F-006"], "f_visit": ["Z4-F-001"],
      "f_steam": ["Z5-F-001"], "f_kit": ["Z5-F-002"], "f_hub": ["Z5-F-003"], "f_cut": ["Z5-F-005"]}
for k, ids in FC.items():
    r0 = {x: y for x, y in Z[ids[0]].items() if x not in ("id", "question", "added_on", "first_seen", "origin", "intake")}
    r0.update(moved_from=ids, axis="전망", type="전망")
    R.append((k, r0))

# ===================== 보강(독립 조사 대조 후) =====================
exec(open(Path(__file__).with_name("c1_add.py"), encoding="utf-8").read()) if Path(__file__).with_name("c1_add.py").exists() else None

# ---------- ID 부여(키 고정) ----------
L = {"사건": "E", "지표": "M", "해석": "I", "전망": "F"}
used = set(AMAP.values())
cnt = {}
for k, r in R:
    if k not in AMAP:
        t = L[r["type"]]
        n = max([int(v.split("-")[2]) for v in AMAP.values() if v.split("-")[1] == t] + [0]) + 1
        AMAP[k] = f"C1-{t}-{n:03d}"
zmap = {}
for k, r in R:
    for z in r.get("moved_from", []):
        zmap.setdefault(z, AMAP[k])
def fix(x): return AMAP.get(x, zmap.get(x, x))
out = []
for k, r in R:
    r = dict(r)
    r.update(id=AMAP[k], question="C1", question_version="v2.0", first_seen="R1", added_on=ON, status=r.get("status", "유효"), replaces=None)
    if r.get("basis"): r["basis"] = [fix(x) for x in r["basis"]]
    r.setdefault("importance", 2); r.setdefault("check_flags", []); r.setdefault("sources", [])
    if "why" in r: r["moved_why"] = r.pop("why")
    out.append(r)
AMAP_P.write_text(json.dumps(AMAP, ensure_ascii=False, indent=0), encoding="utf-8")
(Path(__file__).with_name("c1_zmap.json")).write_text(json.dumps(zmap, ensure_ascii=False, indent=0), encoding="utf-8")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_base.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sorted(out, key=lambda r: r["id"])), encoding="utf-8")
if not (OUT / "patches.jsonl").exists(): (OUT / "patches.jsonl").write_text("", encoding="utf-8")
from collections import Counter
print("기록", len(out), Counter(r["type"] for r in out), "축", Counter(r.get("axis") for r in out))
