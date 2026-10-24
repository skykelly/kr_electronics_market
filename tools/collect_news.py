#!/usr/bin/env python3
"""네이버 뉴스 검색 API 수집기. 질문별 검색어로 날짜순 기사를 모아 후보 파일을 만든다.

출력: state/candidates/<KST 날짜>.json   (오늘 처음 본 후보만)
      state/candidates/seen.json          (본 기사 주소 색인, 60일 보관)
역할: 후보 발굴만 한다. 사건 여부 판정, 원문 확인, 질문 배정 확정, 기록 작성은 일간 배치가 한다.
토큰을 쓰지 않는다(외부 접속은 GitHub Actions 에서 실행).

사용
  NAVER_CLIENT_ID=.. NAVER_CLIENT_SECRET=.. python3 tools/collect_news.py
  python3 tools/collect_news.py --fixture tests/fixtures/naver_sample.json --questions C1,O1 --out /tmp/x   (시험)
  옵션: --questions S1,C1  --lookback 14  --out <폴더>  --dry (파일을 쓰지 않고 요약만)
"""
import argparse, datetime as dt, email.utils, html, json, os, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KST = dt.timezone(dt.timedelta(hours=9))
API = "https://openapi.naver.com/v1/search/news.json"
SEEN_DAYS = 60


def today():
    return dt.datetime.now(KST).date()


def clean(s):
    return html.unescape(re.sub(r"</?b>", "", s or "")).strip()


def norm_url(u):
    p = urllib.parse.urlsplit(u.strip())
    return urllib.parse.urlunsplit((p.scheme, p.netloc.lower().removeprefix("www."), p.path.rstrip("/"), p.query if "n.news.naver" in p.netloc else "", ""))


def norm_title(t):
    t = re.sub(r"\[[^\]]*\]|\([^)]*\)|[^0-9A-Za-z가-힣]", "", t)
    return t[:24]


def parse_date(s):
    try:
        return email.utils.parsedate_to_datetime(s).astimezone(KST)
    except Exception:
        return None


def fetch(query, start, display, cid, sec, fixture=None):
    if fixture is not None:
        # 시험용: 같은 응답을 첫 페이지에서만 돌려준다
        return fixture if start == 1 else {"items": []}
    url = f"{API}?{urllib.parse.urlencode({'query': query, 'display': display, 'start': start, 'sort': 'date'})}"
    req = urllib.request.Request(url, headers={"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": sec})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(1.5 * (attempt + 1))


def known_urls():
    """이미 기록에 출처로 들어간 주소."""
    out = set()
    for f in ROOT.glob("*/*/records.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except Exception:
                continue
            for s in r.get("sources", []) or []:
                if s.get("url"):
                    out.add(norm_url(s["url"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions")
    ap.add_argument("--lookback", type=int)
    ap.add_argument("--out")
    ap.add_argument("--fixture")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    qj = json.loads((ROOT / "tools/queries.json").read_text(encoding="utf-8"))
    cfg = json.loads((ROOT / "tools/news_keywords.json").read_text(encoding="utf-8"))
    lookback = a.lookback or qj.get("lookback_days", 14)
    qs = [x.strip() for x in a.questions.split(",")] if a.questions else list(qj["questions"])
    cid, sec = os.environ.get("NAVER_CLIENT_ID"), os.environ.get("NAVER_CLIENT_SECRET")
    fixture = json.loads(Path(a.fixture).read_text(encoding="utf-8")) if a.fixture else None
    if fixture is None and not (cid and sec):
        sys.exit("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수가 없습니다.")

    now = dt.datetime.now(KST)
    cutoff = now - dt.timedelta(days=lookback)
    outdir = Path(a.out) if a.out else ROOT / "state/candidates"
    seen_path = outdir / "seen.json"
    seen = json.loads(seen_path.read_text(encoding="utf-8")) if seen_path.exists() else {}
    seen = {u: d for u, d in seen.items() if (today() - dt.date.fromisoformat(d)).days <= SEEN_DAYS}
    in_records = known_urls() if not a.fixture else set()

    found = {}   # norm_url -> item
    log = {}     # 질문 -> 통계
    for q in qs:
        must = cfg["must_any"].get(q, [])
        st = {"queries": 0, "api_items": 0, "in_window": 0, "kept": 0, "errors": 0}
        for query in qj["questions"][q]["queries"]:
            st["queries"] += 1
            for page in range(cfg["max_pages"]):
                start = 1 + page * cfg["display"]
                try:
                    res = fetch(query, start, cfg["display"], cid, sec, fixture)
                except Exception as e:
                    st["errors"] += 1
                    print(f"[{q}] '{query}' 오류: {e}", file=sys.stderr)
                    break
                items = res.get("items", [])
                st["api_items"] += len(items)
                in_win = 0
                for it in items:
                    d = parse_date(it.get("pubDate", ""))
                    if not d or d < cutoff:
                        continue
                    in_win += 1
                    title, desc = clean(it.get("title")), clean(it.get("description"))
                    if must and not any(m.lower() in (title + " " + desc).lower() for m in must):
                        continue
                    link = it.get("originallink") or it.get("link")
                    key = norm_url(link)
                    if key in in_records:
                        continue
                    st["in_window"] += 1
                    if key in found:
                        found[key]["questions"].add(q)
                        found[key]["queries"].add(query)
                    else:
                        found[key] = {"url": link, "naver_url": it.get("link"), "title": title, "desc": desc,
                                      "published": d.isoformat(timespec="minutes"), "host": urllib.parse.urlsplit(link).netloc,
                                      "questions": {q}, "queries": {query}}
                # 이 페이지가 전부 기간 안이면 다음 페이지도 본다
                if len(items) < cfg["display"] or in_win < len(items):
                    break
                time.sleep(0.1)
            time.sleep(0.1)
        log[q] = st

    # 같은 제목 묶기(다른 매체 전재)
    clusters = {}
    for key, it in sorted(found.items(), key=lambda kv: kv[1]["published"]):
        ck = norm_title(it["title"])
        if ck in clusters:
            clusters[ck]["also"].append({"url": it["url"], "host": it["host"], "published": it["published"]})
            clusters[ck]["questions"] |= it["questions"]
            clusters[ck]["queries"] |= it["queries"]
        else:
            it["also"] = []
            clusters[ck] = it

    new = []
    for it in clusters.values():
        k = norm_url(it["url"])
        if k in seen:
            continue
        it["questions"] = sorted(it["questions"])
        it["queries"] = sorted(it["queries"])
        new.append(it)
    # 질문별 상한(최신순)
    per, kept = {}, []
    for it in sorted(new, key=lambda x: x["published"], reverse=True):
        q0 = it["questions"][0]
        per[q0] = per.get(q0, 0) + 1
        if per[q0] <= cfg["max_per_question"]:
            kept.append(it)
    for it in kept:
        log[it["questions"][0]]["kept"] += 1

    out = {"date": today().isoformat(), "collected_at": now.isoformat(timespec="minutes"), "lookback_days": lookback,
           "count": len(kept), "stats": log, "items": kept}
    print(f"후보 {len(kept)}건 (제목 묶음 전 {len(found)}건) · 질의 {sum(s['queries'] for s in log.values())}건 · 오류 {sum(s['errors'] for s in log.values())}건")
    for q, s in log.items():
        print(f"  {q}: 질의 {s['queries']} · 응답 {s['api_items']} · 기간·필터 통과 {s['in_window']} · 후보 {s['kept']} · 오류 {s['errors']}")
    if a.dry:
        return
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{today().isoformat()}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for it in kept:
        seen[norm_url(it["url"])] = today().isoformat()
        for al in it["also"]:
            seen[norm_url(al["url"])] = today().isoformat()
    seen_path.write_text(json.dumps(seen, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
