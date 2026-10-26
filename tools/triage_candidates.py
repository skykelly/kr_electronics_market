#!/usr/bin/env python3
"""후보 파일에 사건 단서와 기존 기록 유사도를 덧붙인다(토큰을 쓰지 않는 규칙 기반 분류).

입력: state/candidates/<날짜>.json   (collect_news.py 결과)
추가: 항목마다
  cues        제목에 든 사건 단서어(출시, 발표, 개최, 할인 등)
  q_title     제목에 브랜드·주제어가 있는 질문(주 질문). 비면 요약에만 언급된 기사
  tier        A 사건 단서어 + 제목에 브랜드 / B 보통 / C 낮음(체험기·인터뷰·포토·광고성 연재)
  similar     같은 사건일 가능성이 있는 기존 기록 [{id, score}] (점수 0.35 이상, 최대 3개)
출력: 같은 파일을 덮어쓴다. stats_triage 에 건수 요약.
사건 여부 최종 판정, 원문 확인, 기록 작성은 일간 배치가 한다. 이 분류는 읽을 순서를 정하는 용도다.

사용: python3 tools/triage_candidates.py [state/candidates/2026-10-27.json]   (생략하면 가장 최근 파일)
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUES_A = ["출시", "공개", "발표", "개최", "오픈", "론칭", "선보", "돌입", "시작", "진행", "인수", "합병", "제휴", "협약", "업무협약",
          "할인", "프로모션", "이벤트", "사전예약", "팝업", "과징금", "시정", "제재", "리콜", "인증", "개편", "신설", "확대", "도입",
          "구독", "점유율", "순위", "실적", "영업이익", "매출", "판매금지", "가처분", "소송", "철수", "종료", "중단"]
LOW = ["체험기", "써보니", "인터뷰", "칼럼", "[포토]", "포토", "[사진]", "화보", "운세", "[위클리템]", "리뷰", "후기", "사설", "기고", "광고", "협찬", "[르포]", "부고", "인사"]
STOP = set("그리고 하지만 대한 위한 통해 이번 올해 지난 오늘 최근 관련 따른 대해 에서 으로 에게 이다 했다 한다 있다 밝혔다 전했다 위해 라고 것으로 가장 모두 이상 이하 기준 국내 한국 신제품 제품 기업 시장 가전 전자".split())


def toks(s):
    out = set()
    for w in re.findall(r"[0-9A-Za-z가-힣]{2,}", s):
        w = re.sub(r"(은|는|이|가|을|를|의|에|과|와|도|로|으로|에서)$", "", w) if re.search(r"[가-힣]", w) and len(w) > 3 else w
        if w not in STOP:
            out.add(w.lower())
    return out


def load_records():
    recs = []
    for f in ROOT.glob("*/*/records.jsonl"):
        q = f.parent.name.upper()
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("type") != "사건" or not r.get("statement"):
                continue
            recs.append({"id": r.get("id"), "q": q, "date": (r.get("date") or "")[:10], "t": toks(r["statement"])})
    return recs


def main():
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else sorted((ROOT / "state/candidates").glob("2*.json"))[-1]
    d = json.loads(p.read_text(encoding="utf-8"))
    must = json.loads((ROOT / "tools/news_keywords.json").read_text(encoding="utf-8"))["must_any"]
    recs = [r for r in load_records() if r["date"] >= "2026-09-01"]
    cnt = {"A": 0, "B": 0, "C": 0, "similar": 0}
    for it in d["items"]:
        title = it["title"]
        it["cues"] = [c for c in CUES_A if c in title]
        low = any(w in title for w in LOW)
        # 제목에 질문의 브랜드·주제어가 있는 질문만 '주 질문'으로 본다(요약에만 언급된 기사는 낮춘다)
        it["q_title"] = [q for q in it["questions"] if any(t.lower() in title.lower() for t in must.get(q, []))]
        it["tier"] = "C" if low else ("A" if (it["cues"] and it["q_title"]) else "B")
        tt = toks(title + " " + it.get("desc", ""))
        sims = []
        for r in recs:
            if r["q"] not in it["questions"] and not r["q"].startswith("X"):
                continue
            inter = len(tt & r["t"])
            if inter < 3:
                continue
            score = inter / max(1, min(len(tt), len(r["t"])))
            if score >= 0.35:
                sims.append({"id": r["id"], "score": round(score, 2)})
        it["similar"] = sorted(sims, key=lambda x: -x["score"])[:3]
        cnt[it["tier"]] += 1
        cnt["similar"] += bool(it["similar"])
    d["stats_triage"] = cnt
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(p.name, cnt)


if __name__ == "__main__":
    main()
