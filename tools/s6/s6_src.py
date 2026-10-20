# S6 출처 사전: 이번 세션에서 직접 연 페이지만. S5 사전(S1~S4 포함)을 이어받는다.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s5"))
from s5_src import SRC as BASE
NR="삼성전자 뉴스룸"
E6={
 "aju_card19":("B","아주경제","https://www.ajunews.com/view/20191105092943276","2019-11-05"),
 "kg_sale21":("B","경기일보","https://kyeonggi.com/article/202012211149944","2020-12-21"),
 "dl_sale21":("B","데일리안","https://m.dailian.co.kr/news/view/948342","2020-12-21"),
 "aju_sale22":("B","아주경제","https://www.ajunews.com/view/20211226093400765","2021-12-26"),
 "inews_lotte22":("B","아이뉴스24","https://www.inews24.com/view/1461991","2022-03-21"),
 "nr_sale23":("A",NR,"https://news.samsung.com/kr/삼성전자-역대급-혜택의-삼성전자-세일-페스타-개최","2022-12-26"),
 "nr_wed23":("A",NR,"https://news.samsung.com/kr/삼성전자-혼수·이사-특별-기획전-실시","2023-02-13"),
 "deal_sale23":("B","딜사이트","https://dealsite.co.kr/articles/98881","2023-02-14"),
 "sbs_bf23":("B","SBS Biz","https://biz.sbs.co.kr/amp/article/20000144911","2023-11-20"),
 "st_sale24":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/40431","2023-12-26"),
 "nr_spring24":("A",NR,"https://news.samsung.com/kr/삼성전자-삼성-ai로-새봄-새단장-프로모션-진행","2024-03-31"),
 "st_aisale24":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/56461","2024-08-01"),
 "st_ksf24":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/63351","2024-11-01"),
 "st_sale25":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/69178","2025-01-06"),
 "st_aisub25":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/79661","2025-04-30"),
 "st_eff25":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/88570","2025-08"),
 "newsis_eff25":("B","뉴시스","https://mobile.newsis.com/view/NISX20250814_0003290416","2025-08-14"),
 "nr_ksf25":("A",NR,"https://news.samsung.com/kr/삼성전자-2025-코리아세일페스타-진행","2025-10-31"),
 "st_sale26":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/99405","2025-12-19"),
}
SRC=dict(BASE); SRC.update(E6)
