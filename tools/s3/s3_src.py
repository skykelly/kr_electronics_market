# S3 출처 사전: 이번 세션에서 직접 연 페이지만. S1·S2 사전을 이어받는다.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s2"))
from s2_src import SRC as BASE
NR="삼성전자 뉴스룸"
E3={
 "st_st2000":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/68527","2024-12-30"),
 "nr_st2000":("A",NR,"https://news.samsung.com/kr/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90-%EC%8A%A4%EB%A7%88%ED%8A%B8%EC%8B%B1%EC%8A%A4-%EA%B5%AD%EB%82%B4-%EC%9D%B4%EC%9A%A9-%EA%B3%A0%EA%B0%9D-2000%EB%A7%8C%EB%AA%85-%EB%84%98%EC%97%88%EB%8B%A4","2024-12-30"),
 "econ_conn":("B","이코노미스트","https://economist.co.kr/article/view/ecn202501060057","2025-01-13"),
 "st_ai150":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/57465","2024-08-15"),
 "hk_ac2025":("B","한국경제","https://www.hankyung.com/article/202506104226g","2025-06-10"),
 "fn_ai2025":("B","파이낸셜뉴스","https://www.fnnews.com/news/202506100902567180","2025-06-10"),
 "sat_3dae":("B","시사경제신문","https://sateconomy.co.kr/news/view/1065571615520439","2025-06-10"),
 "etoday_carbon":("B","이투데이","https://www.etoday.co.kr/news/view/2535680","2025-12-14"),
 "etoday_5yr":("B","이투데이","https://www.etoday.co.kr/news/view/2366652","2024-06-04"),
 "dailian_life2023":("B","데일리안","https://www.dailian.co.kr/news/view/1213742/","2023-03-21"),
 "mt_ces26":("B","머니투데이","https://www.mt.co.kr/industry/2026/01/05/2026010215102163482","2026-01-05"),
 "aju_ces26":("B","아주경제","https://www.ajunews.com/view/20260105015523364","2026-01-05"),
 "bizwatch_st10":("B","비즈니스워치","https://news.bizwatch.co.kr/article/industry/2024/09/13/0002","2024-09-15"),
 "st_ad2025":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/81985","2025-05-28"),
 "st_ad2024":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/47313","2024-04-05"),
 "ditoday_yuna":("B","디지털투데이","https://ditoday.com/?p=132851","2025-08-28"),
 "asiae_prada":("B","아시아경제","https://view.asiae.co.kr/article/2026050310570250065","2026-05-03"),
 "dailian_iot2018":("B","데일리안","https://www.dailian.co.kr/news/view/713818/","2018-05-17"),
 "fn_save2023":("B","파이낸셜뉴스","https://www.fnnews.com/news/202305101038263784","2023-05-10"),
 "nr_bixby2026":("A",NR,"https://news.samsung.com/kr/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90-ai-%EA%B0%80%EC%A0%84%EC%97%90-%EB%8D%94-%EB%98%91%EB%98%91%ED%95%B4%EC%A7%84-%EB%B9%85%EC%8A%A4%EB%B9%84-%EC%A0%81%EC%9A%A9","2026-03-31"),
 "nt_wce":("B","뉴스토마토","https://newstomato.com/ReadNews.aspx?no=1272869","2025-08-27"),
 "st_sub2024":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/68290","2024-12-26"),
 "nr_infog":("A",NR,"https://news.samsung.com/kr/%EC%9D%B8%ED%8F%AC%EA%B7%B8%EB%9E%98%ED%94%BD-1%EA%B0%80%EA%B5%AC-1%EC%8A%A4%EB%A7%88%ED%8A%B8%EC%8B%B1%EC%8A%A4-%EC%8B%9C%EB%8C%80-%EA%B5%AD%EB%82%B4-%EB%93%B1%EB%A1%9D","2026-03-10"),
 "segye_wtb":("B","세계일보","https://www.segye.com/view/20240403505652","2024-04-03"),
 "herald_aiwash":("B","헤럴드경제","https://www.heraldk.com/article/2025110617000038283","2025-11-06"),
 "hk_aiwash":("B","한국경제","https://www.hankyung.com/article/202511079523i","2025-11-07"),
 "sbs_aiwash":("B","SBS Biz","https://biz.sbs.co.kr/amp/article/20000270737","2025-11-07"),
 "open_ai2026":("B","오픈서베이","https://blog.opensurvey.co.kr/trendreport/ai-home-appliance-2026/","2026-04-01"),
 "hk_open":("B","한국경제","https://www.hankyung.com/article/202604012347g","2026-04-01"),
 "st_trio":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/79334","2025-04-27"),
 "hk_ambassador":("B","한국경제","https://www.hankyung.com/article/202507159420g","2025-07-16"),
 "aju_2021":("B","아주경제","https://www.ajunews.com/view/20211130143204594","2021-12-01"),
 "aju_ifa22":("B","아주경제","https://www.ajunews.com/view/20220902062903117","2022-09-02"),
 "newsis_ai2024b":("B","뉴시스","https://mobile.newsis.com/view/NISX20240524_0002747187","2024-05-25"),
 "deal_bh2022":("B","딜사이트","https://dealsite.co.kr/articles/83886","2022-02-17"),
 "dailian_ces2018b":("B","데일리안","https://www.dailian.co.kr/news/view/685428/","2018-01-09"),
 "mt_ces26_kr":("B","머니투데이","https://www.mt.co.kr/industry/2026/01/06/2026010607073170433","2026-01-06"),
}
SRC=dict(BASE); SRC.update(E3)
