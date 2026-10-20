"""records.jsonl + meta.json → 아티클 HTML(article_rN.html)과 포털 신호(signal_rN.json).

사용: python3 lib/render_article.py <질문 폴더> [--round N]   (기본 회차 = meta.json 의 round)

meta.json 형식
{
 "category": "Samsung Korea Appliances", "area": "전략 변화", "no": "S1",
 "round": 1, "date": "2026-10-20", "round_label": "R1 기준 회차",
 "title": "아티클 제목", "question": "고정 질문 문장",
 "one_line": "한 줄 답 (사실만)", "one_line_basis": ["S1-E-001"],
 "rows": [{"label": "구분", "text": "문장", "basis": ["S1-E-001"]}],
 "events_lead": "연표 앞 한 줄 설명",
 "indicators": {"S1-T1": "지표 이름"},
 "unknowns": [{"item": "공개되지 않은 값", "why": "왜 필요한가"}]
}
아티클 본문에는 사실과 기준만 쓴다. 회사 의도 추정이나 과정 문구는 넣지 않는다.
"""
import html, json, re, sys
from pathlib import Path

E = html.escape
ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / "lib" / "article.css").read_text(encoding="utf-8")


def main(qdir, rnd=None):
    qdir = Path(qdir)
    meta = json.loads((qdir / "meta.json").read_text(encoding="utf-8"))
    rnd = rnd or meta["round"]
    recs = [json.loads(l) for l in (qdir / "records.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    live = [r for r in recs if r.get("status") in (None, "유효", "미확인")]
    by = {r["id"]: r for r in recs}
    qno = meta["no"]

    def tags(ids):
        return "".join(f'<a class="rid" href="#{E(i)}" title="{E(by[i]["statement"])}">{E(i)}</a>' for i in ids if i in by)

    def src_links(r):
        return " · ".join(
            f'<a href="{E(s["url"])}" target="_blank" rel="noopener">{E(s["publisher"])}</a><span class="grade g{E(s["grade"])}">{E(s["grade"])}</span>'
            for s in r.get("sources", []))

    def claim_badge(r):
        ct = r.get("claim_type", "해당 없음")
        if ct == "해당 없음":
            return ""
        cls = {"자사 집계": "own-claim", "외부 검증": "ext-claim", "공시": "pub-claim"}[ct]
        return f'<span class="bdg {cls}">{E(ct)}</span>'

    # 1. 한 줄 답
    arows = "".join(f'<div class="arow"><dt>{E(x["label"])}</dt><dd>{E(x["text"])} {tags(x.get("basis", []))}</dd></div>' for x in meta.get("rows", []))

    # 2. 연표 (최신순, 연도 구분)
    events = sorted([r for r in live if r["type"] == "사건"], key=lambda r: (r["date"], r["id"]), reverse=True)
    erows, cur_year = "", None
    for r in events:
        y = r["date"][:4]
        if y != cur_year:
            cur_year = y
            erows += f'<li class="yearrow"><b>{E(y)}</b></li>'
        per = ""
        if r.get("period_start") or r.get("period_end"):
            per = f'<span class="bdg per">{E(r.get("period_start", "?"))} ~ {E(r.get("period_end", "?"))}</span>'
        rec = f'<span class="bdg rec-{"reg" if r.get("recurrence") == "정기" else "irr"}">{E(r["recurrence"])}</span>' if r.get("recurrence") in ("정기", "비정기") else ""
        tg = "".join(f'<span class="bdg tg">{E(t)}</span>' for t in r.get("tags", []))
        det = []
        for k, lab in (("product", "대상 제품"), ("channel", "채널"), ("benefit", "혜택"), ("message", "회사가 밝힌 메시지")):
            if r.get(k):
                det.append(f"<dt>{lab}</dt><dd>{E(r[k])}</dd>")
        ext = f'<div class="ext">외부 검증: {E(r["external_check"])}</div>' if r.get("external_check") else ""
        flags = f'<div class="ext warnline">{E("; ".join(r["check_flags"]))}</div>' if r.get("check_flags") else ""
        erows += (f'<li id="{E(r["id"])}"><time>{E(r["date"])}</time><div>'
                  f'<div class="bdgs"><span class="bdg et">{E(r["event_type"])}</span>{rec}{claim_badge(r)}{per}{tg}</div>'
                  f'<b>{E(r["actor"])}</b> {E(r["statement"])}'
                  f'{"<dl class=evd>" + "".join(det) + "</dl>" if det else ""}{ext}{flags}'
                  f'<div class="src">{src_links(r)} <code>{E(r["id"])}</code></div></div></li>')

    # 3. 핵심 지표
    names = meta.get("indicators", {})
    metrics = sorted([r for r in live if r["type"] == "지표"], key=lambda r: (r["indicator"], -r["importance"], r["id"]))
    filled = {r["indicator"] for r in metrics if r.get("verified")}

    def fmt_val(r):
        v, u = r.get("value"), r.get("unit", "")
        s = f"{v:g}" if isinstance(v, (int, float)) else str(v)
        return f"{s}{'' if u.startswith('%') else ' '}{u}"

    mrows = "".join(
        f'<tr id="{E(r["id"])}"><td class="ind">{E(r["indicator"])}<small>{E(names.get(r["indicator"], ""))}</small></td>'
        f'<td class="stmt">{E(r["statement"])} {claim_badge(r)}'
        f'{"<div class=ext>외부 검증: " + E(r["external_check"]) + "</div>" if r.get("external_check") else ""}'
        f'<div class="src">{src_links(r)}</div></td>'
        f'<td class="num">{E(fmt_val(r))}</td><td class="asof">{E(r["as_of"])}<small>{E(r["region"])}</small></td>'
        f'<td class="idc"><code>{E(r["id"])}</code></td></tr>' for r in metrics)

    # 4. 해석
    DIR = {"강화": "up", "약화": "down", "중립": "flat"}
    interps = [r for r in live if r["type"] == "해석"]
    irows = "".join(
        f'<tr id="{E(r["id"])}"><td><span class="dir {DIR[r["direction"]]}">{E(r["direction"])}</span></td><td class="tgt">{E(r["target"])}</td>'
        f'<td>{E(r["statement"])}</td><td>{tags(r["basis"])}</td><td class="idc"><code>{E(r["id"])}</code></td></tr>' for r in interps)

    # 5. 회사 공식 계획(전망)
    plans = sorted([r for r in live if r["type"] == "전망"], key=lambda r: (r["due"], r["id"]))
    prows = ""
    for r in plans:
        ab = r["announced_by"]
        abl = f'<a href="{E(ab["url"])}" target="_blank" rel="noopener">{E(ab.get("publisher", "발표"))}</a>' if isinstance(ab, dict) else E(str(ab))
        res = f'<small>결과: {E(r["result"])}</small>' if r.get("result") else ""
        prows += (f'<tr id="{E(r["id"])}"><td class="stmt">{E(r["statement"])}<small>확인 방법: {E(r["method"])}</small>{res}</td>'
                  f'<td class="asof">{E(r["due"])}</td><td>{abl}</td><td><span class="fstat">{E(r.get("forecast_status", "진행 중"))}</span></td>'
                  f'<td>{tags(r.get("basis", []))}</td></tr>')

    # 6. 미확인·경고
    unk = "".join(f'<tr><td>{E(u["item"])}</td><td class="muted">{E(u["why"])}</td></tr>' for u in meta.get("unknowns", []))
    warns = [r for r in live if (r["type"] in ("지표", "사건") and not r.get("verified")) or r.get("check_flags")]
    wrows = "".join(
        f'<tr><td><code>{E(r["id"])}</code></td><td><span class="wk">{"원문 미확인" if not r.get("verified") else "주의"}</span></td>'
        f'<td>{E(r["statement"])}</td><td class="muted">{E("; ".join(r.get("check_flags", [])))}</td></tr>' for r in warns)

    # 7. 인사이트 요약 · 서술형 해석 · 원장 (meta.json 의 insights / narrative / ledger)
    ins = meta.get("insights", [])
    insh = "".join(
        f'<li><b>{E(x["title"])}</b><p>{E(x["text"])} {tags(x.get("basis", []))}</p></li>' for x in ins)
    narr = ""
    for blk in meta.get("narrative", []):
        narr += f'<h3>{E(blk["heading"])}</h3>' if blk.get("heading") else ""
        for para in blk.get("paras", []):
            narr += f'<p>{E(para["text"])} {tags(para.get("basis", []))}</p>'
    led = meta.get("ledger")
    ledh = ""
    if led:
        th = "".join(f"<th>{E(c)}</th>" for c in led["columns"]) + "<th>근거</th>"
        tb = "".join("<tr>" + "".join(f'<td{" class=stmt" if i else " class=tgt"}>{E(c)}</td>' for i, c in enumerate(row["cells"]))
                     + f'<td>{tags(row.get("basis", []))}</td></tr>' for row in led["rows"])
        ledh = (f'<section><h2>{E(led.get("title", "원장"))} <small>{E(led.get("note", ""))}</small></h2>'
                f'<div class="tablewrap"><table class="ledger"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div></section>')

    counts = {t: sum(1 for r in recs if r["type"] == t) for t in ("지표", "사건", "해석", "전망")}
    n_ind = len(names)
    sec = []
    sec.append(f'<section class="answer-box"><h2>한 줄 답</h2><p class="answer narrow">{E(meta["one_line"])} {tags(meta.get("one_line_basis", []))}</p>'
               f'<dl class="arows">{arows}</dl></section>')
    if insh:
        sec.append(f'<section class="insights"><h2>인사이트 요약 <small>기록 2건 이상을 근거로 묶은 정리</small></h2><ol class="ins">{insh}</ol></section>')
    if narr:
        sec.append(f'<section class="narrative"><h2>해석 <small>시기별 서술 · 문단 끝 번호가 근거 기록</small></h2><div class="narrow prose">{narr}</div></section>')
    if ledh:
        sec.append(ledh)
    sec.append(f'<section><h2>연표 <small>최신순 · 사건 {len(events)}건</small></h2>'
               f'{"<p class=lead>" + E(meta["events_lead"]) + "</p>" if meta.get("events_lead") else ""}'
               f'<ul class="timeline evtl">{erows or "<li><p class=muted>기록된 사건이 없습니다.</p></li>"}</ul></section>')
    if metrics:
        sec.append(f'<section><h2>핵심 지표 <small>추적 지표 {len(filled)}/{n_ind}개 값 확보</small></h2>'
                   f'<div class="tablewrap"><table><thead><tr><th>추적 지표</th><th>내용 · 출처</th><th style="text-align:right">값</th><th>기준 시점</th><th>기록</th></tr></thead><tbody>{mrows}</tbody></table></div></section>')
    if interps:
        sec.append(f'<section><h2>해석 기록 <small>사실 기록 2건 이상을 근거로 연결한 것만</small></h2>'
                   f'<div class="tablewrap"><table><thead><tr><th>방향</th><th>대상</th><th>해석</th><th>근거</th><th>기록</th></tr></thead><tbody>{irows}</tbody></table></div></section>')
    if plans:
        sec.append(f'<section><h2>회사 공식 계획 <small>발표된 목표·계획만, 이행 여부를 추적</small></h2>'
                   f'<div class="tablewrap"><table><thead><tr><th>계획</th><th>확인 시점</th><th>발표 출처</th><th>상태</th><th>근거</th></tr></thead><tbody>{prows}</tbody></table></div></section>')
    if unk:
        sec.append(f'<section><h2>공개 자료로 확인되지 않은 것</h2><div class="tablewrap"><table><thead><tr><th>항목</th><th>왜 필요한가</th></tr></thead><tbody>{unk}</tbody></table></div></section>')
    if wrows:
        sec.append(f'<section><h2>미확인·경고 <small>본문 판단에서 빼거나 주의해서 쓴 기록</small></h2>'
                   f'<div class="tablewrap"><table><thead><tr><th>기록</th><th>구분</th><th>진술</th><th>사유</th></tr></thead><tbody>{wrows}</tbody></table></div></section>')

    page = f"""<title>{E(qno)} {E(meta["area"])} R{rnd}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans+KR:wght@400;500;600&family=Noto+Serif+KR:wght@600;800&display=swap">
<style>{CSS}</style>
<main>
  <header class="narrow">
    <div class="eyebrow"><span>{E(meta["category"])}</span><span>{E(qno)} · {E(meta["area"])}</span><span>R{rnd} {E(meta.get("round_label", ""))} · {E(meta["date"])}</span></div>
    <h1>{E(meta["title"])}</h1>
    <p class="question">고정 질문 v1.0 — {E(meta["question"])}</p>
  </header>
  {"".join(sec)}
  <footer>
    <span>이 글은 4유형 기록 {len(recs)}건(지표 {counts['지표']} · 사건 {counts['사건']} · 해석 {counts['해석']} · 전망 {counts['전망']})에서 생성했습니다. 문장 옆 번호를 누르면 해당 기록으로 이동합니다.</span>
    <span>출처 등급 A = 1차 조사·공식 발표, B = 주요 언론·2차 보도, C = 블로그·출처 불명(원문 확인 전까지 판단에 쓰지 않음). 출처 유형 '자사 집계'는 회사가 밝힌 수치로 외부 검증이 없을 수 있습니다.</span>
  </footer>
</main>
"""
    (qdir / f"article_r{rnd}.html").write_text(page, encoding="utf-8")
    anchors = set(re.findall(r'id="(%s-[A-Z]-\d{3})"' % qno, page))
    bad = sorted({i for i in re.findall(r'href="#(%s-[A-Z]-\d{3})"' % qno, page) if i not in anchors})
    last = events[0]["date"] if events else "—"
    signal = {"question": qno, "round": rnd, "kind": "text",
              "chip": f"최근 사건 {last}", "text": f"사건 {len(events)} · 지표 {len(metrics)} · 해석 {len(interps)} · 계획 {len(plans)}"}
    (qdir / f"signal_r{rnd}.json").write_text(json.dumps(signal, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{qdir}/article_r{rnd}.html 생성 ({len(page)} bytes); 앵커 없는 근거 링크: {bad or '없음'}")
    return 1 if bad else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    rn = int(a[a.index("--round") + 1]) if "--round" in a else None
    sys.exit(main(a[0], rn))
