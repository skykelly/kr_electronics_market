#!/usr/bin/env python3
"""collect_news.py 시험. 네이버 응답 형식의 가짜 데이터로 필터·묶기·중복 제거를 확인한다(외부 접속 없음)."""
import datetime as dt, email.utils, json, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
now = dt.datetime.now(dt.timezone.utc)
def rfc(days): return email.utils.format_datetime(now - dt.timedelta(days=days))
fx = {"items": [
 {"title": "<b>로보락</b> 신제품 &quot;S10&quot; 출시", "originallink": "https://www.etnews.com/2026A", "link": "https://n.news.naver.com/1", "description": "<b>로보락</b>이 새 모델을 냈다", "pubDate": rfc(1)},
 {"title": "[단독] 로보락 신제품 S10 출시", "originallink": "https://www.mt.co.kr/2026B", "link": "https://n.news.naver.com/2", "description": "로보락 S10", "pubDate": rfc(1)},
 {"title": "로보락 3주 전 기사", "originallink": "https://www.hankyung.com/old", "link": "https://n.news.naver.com/3", "description": "로보락", "pubDate": rfc(30)},
 {"title": "삼성전자 갤럭시 출시", "originallink": "https://www.ajunews.com/x", "link": "https://n.news.naver.com/4", "description": "스마트폰", "pubDate": rfc(1)},
]}
with tempfile.TemporaryDirectory() as td:
    fxp = Path(td) / "fx.json"; fxp.write_text(json.dumps(fx), encoding="utf-8")
    out = Path(td) / "out"
    def run():
        r = subprocess.run([sys.executable, str(ROOT / "tools/collect_news.py"), "--fixture", str(fxp), "--questions", "C1", "--out", str(out)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        return r.stdout
    print(run())
    d = json.loads(next(out.glob("2*.json")).read_text(encoding="utf-8"))
    assert d["count"] == 1, d["count"]            # 기간 밖·필터 밖 제외, 같은 제목은 한 건으로 묶음
    it = d["items"][0]
    assert it["title"] == '로보락 신제품 "S10" 출시', it["title"]   # 태그·엔티티 정리
    assert len(it["also"]) == 1 and it["questions"] == ["C1"]
    run()                                          # 두 번째 실행: 이미 본 기사는 후보에서 빠진다
    seen_file = list(out.glob("2*.json"))
    d2 = json.loads(seen_file[0].read_text(encoding="utf-8"))
    assert d2["count"] == 0, d2["count"]
print("OK")
