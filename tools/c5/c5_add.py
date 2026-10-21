# C5 보강: 독립 조사(2026-10-21, 기존 기록을 보지 않은 조사)와 대조하고 직접 원문을 열어 빈칸을 채운 기록. 원문을 직접 연 것만 싣는다.
def S(u, p, d, g="B"): return {"grade": g, "publisher": p, "url": u, "date": d}
def ev(k, date, axis, et, st, src, imp=2, actor="TCL", **o):
    add(k, "사건", axis, date=date, actor=actor, event_type=et, statement=st, sources=src, importance=imp, recurrence=o.pop("recurrence", "비정기"), **o)
def me(k, ind, val, unit, asof, axis, st, src, imp=2, **o):
    add(k, "지표", axis, indicator=ind, value=val, unit=unit, as_of=asof, region=o.pop("region", "한국"), statement=st, sources=src, importance=imp, **o)

TCLKR = S("https://www.tcl.com/kr/ko/about-tcl", "TCL 한국 공식 사이트(회사 소개)", "2026-10-21", "A")
DT23 = S("https://www.dt.co.kr/article/11545619", "디지털타임스", "2023-11-06")
AJ24 = S("https://www.ajunews.com/view/20240614150605022", "아주경제", "2024-06-14")
NS25 = S("https://www.newsis.com/view/NISX20250911_0003324892", "뉴시스", "2025-09-11")

ev("a_corp_official", "2023", "조직", "전략·조직", "TCL 한국 공식 사이트 회사 소개는 2023년 서울에 현지 법인 'TCL Electronics Korea Ltd.'를 설립했다고 적는다. 페이지에 법인 주소, 대표, 등기일은 없다.", [TCLKR], imp=2,
   check_flags=["연도만 표기됨. 2023-11-06 한국 법인 설립 발표 기사와 같은 시기로 보이나 등기일은 확인하지 못함"])
ev("ch_official26", "2026-10", "채널", "채널·매장", "TCL 한국 공식 사이트 회사 소개는 TV를 온라인에서 쿠팡, 네이버, 지마켓으로 팔고 오프라인에서 롯데하이마트, 코스트코, 홈플러스, 전자랜드로 판다고 적는다. 제품군은 TV, 에어컨, 냉장고, 모니터, 사운드바다. 페이지 확인일 기준이며 매장 수는 없다.", [TCLKR], imp=3,
   check_flags=["입점 시점과 매장 수는 페이지에 없음", "회사 소개 문구이며 개별 매장 입점은 직접 확인하지 못함"])
ev("as_official26", "2026-10", "AS·신뢰", "구독·케어·AS", "TCL 한국 공식 사이트 회사 소개는 전국에 여러 AS 센터, 고객 콜센터, 온라인 상담 서비스를 운영한다고 적는다. 센터 수와 위치, 보증 기간은 같은 사이트의 회사 소개·보증 정책 페이지에서 확인하지 못했다.", [TCLKR], imp=3,
   claim_type="자사 집계", external_check="미확보", check_flags=["센터 수·위치·위탁 여부는 페이지에 없음"])
ev("p_ac24", "2024-06-14", "제품", "제품 출시", "TCL은 2024년 6월 14일 인버터 에어컨 시리즈를 쿠팡에서 처음 출시했다. 벽걸이형 2종(TAC-08CSD, TAC-12CSD), 듀얼 인버터 창문형(TAC-07CWADBp_Upgraded), 스탠딩 냉난방기(TAC-24CHFA/C) 4종이다. 가격은 기사에 없다.", [AJ24], imp=2)
ev("as_ac24", "2024-06-14", "AS·신뢰", "구독·케어·AS", "TCL은 2024년 6월 쿠팡 출시 에어컨 구매 고객에게 2년 무상 보증과 설치 서비스를 제공한다고 밝혔다.", [AJ24], imp=2,
   check_flags=["AS 수행 주체와 센터는 기사에 없음"])
ev("mk_subway24", "2024", "판촉·마케팅", "마케팅", "뉴시스는 TCL이 2024년부터 서울 주요 지하철역 내 대형 광고판으로 TV를 홍보했다고 2025년 9월 11일 전했다.", [NS25], imp=2,
   check_flags=["연도만 표기됨. 광고 시작 시점과 기간, 규모는 기사에 없음"])
