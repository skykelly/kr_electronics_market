# S7 출처 사전: 이번 세션에서 직접 연 페이지만. S6 사전(S1~S5 포함)을 이어받는다.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s6"))
from s6_src import SRC as BASE
NR="삼성전자 뉴스룸"; SV="삼성전자서비스"
E7={
 "sat_cmp15":("B","시사경제신문","https://www.sateconomy.co.kr/news/view/179586836548097","2015-06-18"),
 "dl_dir18":("B","데일리안","https://www.dailian.co.kr/news/view/707482/","2018-04-17"),
 "bw_dir18":("B","비즈니스워치","https://news.bizwatch.co.kr/article/industry/2018/11/22/0026","2018-11-22"),
 "dl_ac19":("B","데일리안","https://m.dailian.co.kr/news/view/793175","2019-05-07"),
 "nr_ac19":("A",NR,"https://news.samsung.com/kr/%ec%82%bc%ec%84%b1%ec%a0%84%ec%9e%90%ec%84%9c%eb%b9%84%ec%8a%a4-%ec%97%90%ec%96%b4%ec%bb%a8-%ec%82%ac%ec%a0%84%ec%a0%90%ea%b2%80-%ec%84%9c%eb%b9%84%ec%8a%a4-%ea%b8%b0%ea%b0%84","2019-05-07"),
 "svc_ac20":("A",SV,"https://www.samsungsvc.co.kr/intro/news/3016457","2020-03-11"),
 "svc_ks20":("A",SV,"https://www.samsungsvc.co.kr/intro/news/3017747","2020-07-20"),
 "kg_life21":("B","경기일보","https://kyeonggi.com/article/202103091159486","2021-03-09"),
 "svc_ac21":("A",SV,"https://www.samsungsvc.co.kr/intro/news/3019766","2021-03-15"),
 "svc_ac22":("A",SV,"https://www.samsungsvc.co.kr/intro/news/3024147","2022-03-07"),
 "svc_ac23":("A",SV,"https://www.samsungsvc.co.kr/intro/news/3027071","2023-03-08"),
 "sg_ac23":("B","세계일보","https://www.segye.com/newsView/20230308503538","2023-03-08"),
 "dt_ac23":("B","디지털타임스","https://www.dt.co.kr/article/11498894","2023-03-08"),
 "svc_ks24":("A",SV,"https://www.samsungsvc.co.kr/intro/news/3031926","2024-07-02"),
 "st_ks24":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/54039","2024-07-02"),
 "bw_ai24":("B","비즈니스워치","https://news.bizwatch.co.kr/article/industry/2024/08/30/0019","2024-08-30"),
 "sbs_pre24":("B","SBS Biz","https://biz.sbs.co.kr/amp/article/20000202592","2024-11-20"),
 "nr_sub24":("A",NR,"https://news.samsung.com/kr/%ec%82%bc%ec%84%b1%ec%a0%84%ec%9e%90-ai-%ea%b5%ac%eb%8f%85%ed%81%b4%eb%9f%bd-%ec%8b%9c%ec%9e%91","2024-12-01"),
 "st_sub24a":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/65870","2024-12-01"),
 "dl_sub24":("B","데일리안","https://www.dailian.co.kr/news/view/1435546/%E6%9C%88-%EA%B5%AC%EB%8F%85%EB%A3%8C%EB%A1%9C-%EC%B5%9C%EC%8B%A0-%EC%A0%9C%ED%92%88-%EC%9D%B4%EC%9A%A9%ED%95%98%EC%84%B8%EC%9A%94-%EC%82%BC-2024","2024-12-01"),
 "st_tv25":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/74653","2025-03-09"),
 "st_pre25":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/78619","2025-04-21"),
 "nr_blue25":("A",NR,"https://news.samsung.com/kr/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90-%EA%B5%AC%EB%8F%85-%EA%B3%A0%EA%B0%9D-%EC%A0%84%EC%9A%A9-%EC%BC%80%EC%96%B4-%EB%B8%94%EB%A3%A8%ED%8C%A8%EC%8A%A4-%EC%84%9C%EB%B9%84%EC%8A%A4-%EC%A0%81","2025-09-01"),
 "st_blue25":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/89956","2025-09-01"),
 "hk_blue25":("B","한국경제","https://www.hankyung.com/article/2025090156401","2025-09-01"),
 "st_fes25b":("B","스마트투데이","https://www.smarttoday.co.kr/ko-kr/articles/92882","2025-10-01"),
 "et_fes25":("B","이투데이","https://www.etoday.co.kr/news/view/2512136","2025-10-01"),
 "sbs_th26":("B","SBS Biz","https://biz.sbs.co.kr/amp/article/20000319074","2026-06-26"),
 "hk_ks26":("B","한국경제","https://www.hankyung.com/article/2026070187261","2026-07-02"),
 "inews_sub26":("B","아이뉴스24","https://www.inews24.com/view/2009398","2026-09-28"),
 "dl_sub26":("B","데일리안","https://www.dailian.co.kr/news/view/1695036/","2026-09-28"),
 "nt_sub26":("B","뉴스토마토","https://newstomato.com/ReadNews.aspx?no=1314900","2026-09-28"),
 "asiae_sub26":("B","아시아경제","https://core.asiae.co.kr/article/2026092809572448156","2026-09-28"),
 "deal_sub26":("B","딜사이트","https://dealsite.co.kr/articles/169693","2026-09-28"),
 "sec_care26":("A","삼성닷컴","https://www.samsung.com/sec/careplus/applySubscribeView/","2026-10-20"),
 "svc_care26":("A",SV,"https://www.samsungsvc.co.kr/info/carePlus","2026-10-20"),
}
SRC=dict(BASE); SRC.update(E7)
