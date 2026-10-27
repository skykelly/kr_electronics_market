#!/usr/bin/env python3
"""후보 기사 원문에서 핵심 문장 몇 개를 발췌해 후보 파일에 붙인다(GitHub Actions 수집 단계, 토큰 0).

대상: tier A 후보 전부와 tier B 중 제목에 브랜드가 있고 단서어가 있는 후보(최대 --max 건, 기본 120).
추가: 항목마다
  excerpt   브랜드·주제어, 날짜·수치가 든 문장 최대 6개(합계 700자 이내). 기사 전문은 저장하지 않는다
  og_date   기사 메타의 게시 시각(있을 때)
  fetch     ok | 실패 사유(http 코드, timeout, 본문 없음)
역할: 일간 배치가 승인 없이도 원문의 핵심 수치를 확인할 수 있게 한다. 최종 확인은 발췌가 기사 요지와 맞는지 보는 정도로 하고,
      발췌로 부족하거나 fetch 가 실패한 후보만 WebFetch 로 직접 연다.
사용: python3 tools/fetch_excerpts.py [state/candidates/2026-10-27.json] [--max 120] [--test]
"""
import argparse, html, json, re, sys, time, urllib.request, urllib.error
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (compatible; KRApplianceSignalsBot/1.0; +https://github.com/skykelly/kr_electronics_market)"
NUM = re.compile(r"\d[\d,\.]*\s*(%|원|만|억|조|개|곳|일|월|대|종|점|명|건|인치|형|kg|L|리터|배)|\d{1,2}월\s*\d{1,2}일|\d{4}년")
SKIP_TAGS = {"script", "style", "noscript", "header", "footer", "nav", "aside", "form", "figure", "figcaption"}


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.paras, self._buf, self._skip, self._in_p = {}, [], [], 0, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            k = a.get("property") or a.get("name")
            if k and a.get("content"):
                self.meta.setdefault(k, a["content"])
        if tag in SKIP_TAGS:
            self._skip += 1
        if tag in ("p", "div", "br") and self._buf:
            self._flush()

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self._skip:
            self._skip -= 1
        if tag in ("p", "div"):
            self._flush()

    def handle_data(self, data):
        if not self._skip:
            self._buf.append(data)

    def _flush(self):
        t = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        self._buf = []
        if len(t) >= 25:
            self.paras.append(t)


def decode(raw, ctype):
    m = re.search(r"charset=([\w-]+)", ctype or "", re.I) or re.search(rb"charset=[\"']?([\w-]+)", raw[:2000], re.I)
    enc = (m.group(1).decode() if m and isinstance(m.group(1), bytes) else (m.group(1) if m else "utf-8"))
    for e in (enc, "utf-8", "euc-kr", "cp949"):
        try:
            return raw.decode(e)
        except Exception:
            continue
    return raw.decode("utf-8", "replace")


def sentences(paras):
    out = []
    for p in paras:
        for s in re.split(r"(?<=[다요음임함됨])[\.]\s+|(?<=\.)\s+(?=[가-힣A-Z\"'“‘])", p):
            s = s.strip()
            if 20 <= len(s) <= 260:
                out.append(s)
    return out


def excerpt(htmltext, terms, limit=700, n=6):
    p = P()
    p.feed(htmltext)
    sents = sentences(p.paras)
    seen, scored = set(), []
    for i, s in enumerate(sents):
        key = s[:30]
        if key in seen:
            continue
        seen.add(key)
        score = sum(2 for t in terms if t and t.lower() in s.lower()) + (1 if NUM.search(s) else 0)
        if "무단전재" in s or "저작권" in s or "기자" in s[-12:] and "@" in s:
            continue
        if score:
            scored.append((-score, i, s))
    pick = sorted(sorted(scored)[:n], key=lambda x: x[1])
    out, total = [], 0
    for _, _, s in pick:
        if total + len(s) > limit:
            break
        out.append(s)
        total += len(s)
    og = p.meta.get("article:published_time") or p.meta.get("og:regDate") or p.meta.get("pubdate") or ""
    return out, og, p.meta.get("og:description", "")[:200]


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return decode(r.read(1_500_000), r.headers.get("Content-Type"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--max", type=int, default=120)
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.test:
        sample = ("<html><head><meta property='article:published_time' content='2026-10-26T09:00:00+09:00'></head><body><nav>메뉴 메뉴 메뉴 메뉴 메뉴 메뉴 메뉴</nav>"
                  "<div class='art'><p>네이버는 26일 하반기 쇼핑 행사 넾다세일을 11월 8일까지 2주간 연다고 밝혔다. 참여 스토어는 약 1만3000개로 전년보다 30% 늘었다.</p>"
                  "<p>첫날에는 삼성전자와 LG전자의 가전 상품을 선보인다. 일별 쿠폰은 최대 7만원까지 할인받을 수 있다.</p><p>무단전재 및 재배포 금지 무단전재 및 재배포 금지</p></div>"
                  "<script>var x=1;</script></body></html>")
        ex, og, _ = excerpt(sample, ["삼성", "넾다세일"])
        assert len(ex) >= 3 and og.startswith("2026-10-26") and all("메뉴" not in s and "무단" not in s for s in ex), (ex, og)
        print("OK", ex)
        return
    p = Path(a.path) if a.path else sorted((ROOT / "state/candidates").glob("2*.json"))[-1]
    d = json.loads(p.read_text(encoding="utf-8"))
    must = json.loads((ROOT / "tools/news_keywords.json").read_text(encoding="utf-8"))["must_any"]
    todo = [it for it in d["items"] if it.get("tier") == "A" and "excerpt" not in it]
    todo += [it for it in d["items"] if it.get("tier") == "B" and it.get("q_title") and it.get("cues") and "excerpt" not in it]
    todo = todo[:a.max]
    stat = {"대상": len(todo), "ok": 0, "실패": 0}
    for it in todo:
        terms = sorted({t for q in (it.get("q_title") or it["questions"][:1]) for t in must.get(q, [])} | {"삼성", "LG"})
        try:
            ex, og, desc = excerpt(fetch(it["url"]), terms)
            it["fetch"] = "ok" if ex else "본문 없음"
            if ex:
                it["excerpt"] = ex
                stat["ok"] += 1
            else:
                stat["실패"] += 1
            if og:
                it["og_date"] = og
        except urllib.error.HTTPError as e:
            it["fetch"] = f"http {e.code}"; stat["실패"] += 1
        except Exception as e:
            it["fetch"] = type(e).__name__; stat["실패"] += 1
        time.sleep(0.4)
    d["stats_excerpt"] = stat
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"발췌: 대상 {stat['대상']}건 · 성공 {stat['ok']} · 실패 {stat['실패']}")


if __name__ == "__main__":
    main()
