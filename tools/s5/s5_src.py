# S5 출처 사전: 이번 세션에서 직접 연 페이지만. S4 사전(S1~S3 포함)을 이어받는다.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s4"))
from s4_src import SRC as BASE
NR="삼성전자 뉴스룸"
E5={
 "etoday_2014":("B","이투데이","https://www.etoday.co.kr/news/view/971191","2014-08-21"),
 "nr_2014":("A",NR,"https://news.samsung.com/kr/삼성-디지털프라자-신개념-복합문화공간-선보여-2","2014-08-21"),
 "nr_gs2015":("A",NR,"https://news.samsung.com/kr/삼성전자-코리아-그랜드-세일-적극-동참","2015-08-19"),
 "aju_exp18":("B","아주경제","https://www.ajunews.com/view/20180819135635303","2018-08-19"),
 "dl_cp19":("B","데일리안","https://www.dailian.co.kr/news/view/847652/","2019-11-29"),
 "nr_cooker21":("A",NR,"https://news.samsung.com/kr/삼성전자-비스포크-큐커-위크-인기-행진","2021-08-17"),
 "inews_dp21":("B","아이뉴스24","https://www.inews24.com/view/1478514","2022-05-09"),
 "st_zone22":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/24250","2022-08-18"),
 "etoday_rn23":("B","이투데이","https://www.etoday.co.kr/news/view/2228047","2023-03-07"),
 "st_rn23":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/27686","2023-03-07"),
 "aju_rn23":("B","아주경제","https://www.ajunews.com/view/20230307083258439","2023-03-07"),
 "itw_rn23":("B","ITWorld","https://www.itworld.co.kr/article/3571449/%EC%82%BC%EC%84%B1-%EB%94%94%EC%A7%80%ED%84%B8%ED%94%84%EB%9D%BC%EC%9E%90-%EC%82%BC%EC%84%B1%EC%8A%A4%ED%86%A0%EC%96%B4-%EC%83%88%EC%B6%9C%EB%B0%9C%EC%B0%A8.html","2023-03-07"),
 "st_lg23":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/27834","2023-03-10"),
 "inews_gn23":("B","아이뉴스24","https://www.inews24.com/view/1593469","2023-05-11"),
 "st_gn23":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/31207","2023-06-20"),
 "tf_hub23":("B","더팩트","https://news.tf.co.kr/read/economy/2025627.htm","2023-06-22"),
 "aju_open24":("B","아주경제","https://www.ajunews.com/view/20240216082933226","2024-02-16"),
 "sat_hll24":("B","시사경제신문","https://sateconomy.co.kr/news/view/1065571702580899","2024-03-08"),
 "aju_ifa24":("B","아주경제","https://www.ajunews.com/view/20240910105720836","2024-09-10"),
 "st_pro25":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/74282","2025-03-05"),
 "newsis_dist25":("B","뉴시스","https://www.newsis.com/view/NISX20250306_0003089195","2025-03-07"),
 "st_combo25":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/78602","2025-04-20"),
 "fn_combo25":("B","파이낸셜뉴스","https://www.fnnews.com/news/202504200906003645","2025-04-20"),
 "ddaily_wed26":("B","디지털데일리","https://www.ddaily.co.kr/page/view/2026032613044745062","2026-03-26"),
 "inews_wed26":("B","아이뉴스24","https://www.inews24.com/view/1953648","2026-03-26"),
 "sbs_wed26":("B","SBS Biz","https://biz.sbs.co.kr/amp/article/20000299984","2026-03-26"),
 "ddaily_th26":("B","디지털데일리","https://www.ddaily.co.kr/m/page/view/2026060709504757669","2026-06-07"),
 "food_th26":("B","식품투데이","https://www.foodtoday.or.kr/mobile/article.html?no=205369","2026-06"),
 "st_th26":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/108152","2026-06"),
 "sisa_th26":("B","시사뉴스","https://sisa-news.com/mobile/article.html?no=270981","2026-06"),
 "etnews_on26":("B","전자신문","https://www.etnews.com/20260713000257","2026-07-13"),
 "mt_mod26":("B","머니투데이","https://www.mt.co.kr/article/2026062414354889301","2026-06-24"),
 "asiae_cd26":("B","아시아경제","https://core.asiae.co.kr/article/2026081612423170158","2026-08-16"),
 "nr_cd26":("A",NR,"https://news.samsung.com/kr/삼성전자-원스톱-혼수-특화-매장-삼성스토어-청담점","2026-08-25"),
 "nr_sub26":("A",NR,"https://news.samsung.com/kr/삼성전자-삼성-ai-구독-새단장-신혼·시니어·기업","2026-09-28"),
 "sbs_sub26":("B","SBS Biz","https://biz.sbs.co.kr/amp/article/20000336976","2026-09-28"),
 "nr_ksf16":("A",NR,"https://news.samsung.com/kr/삼성-디지털프라자-코리아-세일-페스타-적극-동","2016-10-06"),
 "nr_ksf17":("A",NR,"https://news.samsung.com/kr/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90-%EC%BD%94%EB%A6%AC%EC%95%84%EC%84%B8%EC%9D%BC%ED%8E%98%EC%8A%A4%ED%83%80-%EB%A7%9E%EC%95%84-%EC%9D%B8%EA%B8%B0-%EA%B0%80%EC%A0%84%E2%88%99it-%EC%A0%9C","2017-09-27"),
 "nr_ksf18":("A",NR,"https://news.samsung.com/kr/삼성전자-2018-코리아세일페스타-참가","2018-09-27"),
 "dl_ye19":("B","데일리안","https://www.dailian.co.kr/news/view/839711/","2019-11-03"),
}
SRC=dict(BASE); SRC.update(E5)
