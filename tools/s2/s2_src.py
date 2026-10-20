# S2 출처 사전. 이번 세션에서 직접 연 페이지만 넣는다(S1에서 연 것은 s1_src에서 가져온다).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s1"))
from s1_src import SRC as S1
NR = "삼성전자 뉴스룸"
E = {
 "st_cb_launch":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/44296","2024-02-23"),
 "newsis_cb":("B","뉴시스","https://www.newsis.com/view/NISX20240223_0002637075","2024-02-23"),
 "st_cb_gray":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/53897","2024-07-01"),
 "aju_cb100k":("B","아주경제","https://www.ajunews.com/view/20250429081024177","2025-04-29"),
 "st_line2025":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/76592","2025-03-30"),
 "herald_cb26":("B","헤럴드경제","https://www.heraldk.com/article/2026032518000039082","2026-03-25"),
 "etnews_cb26":("B","전자신문","https://m.etnews.com/20260326000280","2026-03-26"),
 "newsis_share":("B","뉴시스","https://www.newsis.com/view/NISX20250522_0003186593","2025-05-22"),
 "dd_share":("B","디지털데일리","https://www.ddaily.co.kr/page/view/2025052212155760312","2025-05-22"),
 "dailian_ga2020":("B","데일리안","https://www.dailian.co.kr/news/view/864513/","2020-01-29"),
 "nr_ga10k":("A",NR,"https://news.samsung.com/kr/%ec%82%bc%ec%84%b1-%ea%b7%b8%eb%9e%91%eb%8d%b0-ai-%ea%b1%b4%ec%a1%b0%ea%b8%b0-%ec%b5%9c%eb%8b%a8-%ea%b8%b0%ea%b0%84-1%eb%a7%8c%eb%8c%80-%eb%8f%8c%ed%8c%8c","2020-03-01"),
 "etoday_mp1000":("B","이투데이","https://www.etoday.co.kr/news/view/2340906","2024-03-17"),
 "dailian_mp2021":("B","데일리안","https://www.dailian.co.kr/news/view/958147/","2021-01-24"),
 "st_mp2025a":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/72078","2025-02-09"),
 "st_mp2025b":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/74391","2025-03-06"),
 "tf_mp1300":("B","더팩트","https://news.tf.co.kr/read/economy/2289779.htm","2026-02-05"),
 "mt_mp2026":("B","머니투데이","https://www.mt.co.kr/industry/2026/02/05/2026020509021315845","2026-02-05"),
 "etoday_steam26":("B","이투데이","https://www.etoday.co.kr/news/view/2555491","2026-02-11"),
 "herald_steam20k":("B","헤럴드경제","https://www.heraldk.com/article/2026060115464269697","2026-06-01"),
 "nr_steam20k":("A",NR,"https://news.samsung.com/kr/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90-%EB%B9%84%EC%8A%A4%ED%8F%AC%ED%81%AC-ai-%EC%8A%A4%ED%8C%80-%EB%A1%9C%EB%B4%87%EC%B2%AD%EC%86%8C%EA%B8%B0-%EC%9B%94-%ED%8C%90%EB%A7%A4-2%EB%A7%8C-%EB%8C%80","2026-06-02"),
 "dailian_steam_basic":("B","데일리안","https://www.dailian.co.kr/news/view/1654746/%ED%95%B5%EC%8B%AC-%EA%B8%B0%EB%8A%A5-%EA%B7%B8%EB%8C%80%EB%A1%9C-%EA%B0%80%EA%B2%A9-%EB%82%AE%EA%B2%8C%EC%82%BC%EC%84%B1-%EB%A1%9C%EB%B4%87-2026","2026-06-11"),
 "dd_steam_basic":("B","디지털데일리","https://www.ddaily.co.kr/page/view/2026061109212554282","2026-06-11"),
 "st_steam2024":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/47223","2024-04-04"),
 "etoday_jet2021":("B","이투데이","https://www.etoday.co.kr/news/view/1991386","2021-02-03"),
 "dailian_jetbot":("B","데일리안","https://www.dailian.co.kr/news/view/985755/","2021-04-27"),
 "mtn_robot":("B","MTN 머니투데이방송","https://news.mtn.co.kr/news-detail/2026063016073873248","2026-06-30"),
 "ceoscore_robot":("B","CEO스코어데일리","https://www.ceoscoredaily.com/page/view/2024081217021627588","2024-08-12"),
 "inews_ad2018":("B","아이뉴스24","https://www.inews24.com/view/1122702","2018-09-04"),
 "dailian_ad2021":("B","데일리안","https://www.dailian.co.kr/news/view/960970/","2021-02-02"),
 "nr_ad2026":("A",NR,"https://news.samsung.com/kr/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90-2026%EB%85%84%ED%98%95-%EC%97%90%EC%96%B4%EB%93%9C%EB%A0%88%EC%84%9C-%EC%8B%A0%EC%A0%9C%ED%92%88-%EA%B3%B5%EA%B0%9C","2025-12-18"),
 "etoday_ad2026":("B","이투데이","https://www.etoday.co.kr/news/view/2537256","2025-12-18"),
 "genews_ad2026":("B","글로벌이코노믹","https://www.g-enews.com/article/Industry/2026/03/2026030210272299156ed0c62d49_1","2026-03-02"),
 "st_fh2024":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/50438","2024-05-17"),
 "newsis_fr2024":("B","뉴시스","https://mobile.newsis.com/view/NISX20240314_0002660224","2024-03-14"),
 "nr_kitchenfit":("A",NR,"https://news.samsung.com/kr/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90-%EB%B9%84%EC%8A%A4%ED%8F%AC%ED%81%AC-%ED%82%A4%EC%B9%9C%ED%95%8F-%EB%A7%A5%EC%8A%A4-%EB%83%89%EC%9E%A5%EA%B3%A0-%EC%8B%A0%EC%A0%9C%ED%92%88-%EC%B6%9C%EC%8B%9C","2025-02-28"),
 "st_kimchi2024":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/60007","2024-09-19"),
 "asiae_kimchi":("B","아시아경제","https://core.asiae.co.kr/article/2024111208231785524","2024-11-12"),
 "nr_kimchi2020":("A",NR,"https://news.samsung.com/kr/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90-%EB%B9%84%EC%8A%A4%ED%8F%AC%ED%81%AC-%EA%B9%80%EC%B9%98%ED%94%8C%EB%9F%AC%EC%8A%A4-%EC%8B%A0%EC%A0%9C%ED%92%88-%EC%B6%9C%EC%8B%9C","2020-08-31"),
 "etoday_fr2021":("B","이투데이","https://www.etoday.co.kr/news/view/2002163","2021-03-09"),
 "khan_home2021":("B","스포츠경향","https://sports.khan.co.kr/article/202103091146003","2021-03-09"),
 "newdaily_mp2022":("B","뉴데일리","https://biz.newdaily.co.kr/site/data/html/2022/03/24/2022032400015.amp.html","2022-03-24"),
 "dailian_mp2023":("B","데일리안","https://www.dailian.co.kr/news/view/1195814/","2023-01-26"),
 "dailian_kit2020":("B","데일리안","https://www.dailian.co.kr/news/view/938975/","2020-11-22"),
}
# 이번 세션에서 열지 못한 URL(예: 뉴스룸 비스포크 냉장고 2024 신제품)은 넣지 않는다.
SRC = dict(S1); SRC.update(E)
