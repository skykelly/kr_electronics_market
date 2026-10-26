#!/usr/bin/env python3
"""후보 파일(state/candidates/<날짜>.json)을 일간 배치가 읽기 쉬운 형태로 보여 주고, 처리 여부를 기록한다.

  python3 tools/candidates.py status                 # 수집 상태(정상/실패)와 처리 안 된 날짜
  python3 tools/candidates.py show [날짜] [--tier A,B] [--q C1,O1] [--full]   # 처리 안 된 모든 날짜(또는 지정 날짜)의 후보를 압축 표시
  python3 tools/candidates.py mark <날짜> --opened N --added N [--skipped '..'] [--leads '..']   # 처리 기록
처리 기록은 state/candidates/processed.json 에 쌓는다. 후보는 14일 겹쳐 수집되므로 하루 실패해도 다음 날 메운다.
"""
import argparse, json, re, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "state/candidates"
KST = dt.timezone(dt.timedelta(hours=9))


def files():
    return sorted(p for p in D.glob("2*.json") if len(p.stem) == 10)


def processed():
    p = D / "processed.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


STOP = set("그리고 하지만 대한 위한 통해 이번 올해 지난 오늘 최근 관련 국내 한국 신제품 출시 공개 발표".split())


def toks(t):
    return {w.lower() for w in re.findall(r"[0-9A-Za-z가-힣]{2,}", t) if w not in STOP}


def health(d):
    errs = sum(s["errors"] for s in d["stats"].values())
    qs = sum(s["queries"] for s in d["stats"].values())
    return ("정상" if qs and errs / qs < 0.2 else "실패"), errs, qs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["status", "show", "mark"])
    ap.add_argument("date", nargs="?")
    ap.add_argument("--tier", default="A")
    ap.add_argument("--q")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--opened", type=int, default=0)
    ap.add_argument("--added", type=int, default=0)
    ap.add_argument("--skipped", default="")
    ap.add_argument("--leads", default="")
    a = ap.parse_args()
    done = processed()
    today = dt.datetime.now(KST).date().isoformat()

    if a.cmd == "status":
        have = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in files()}
        if today not in have:
            print(f"{today}: 후보 파일 없음 → 수집 실패")
        for k, d in have.items():
            h, e, q = health(d)
            print(f"{k}: {h} · 후보 {d['count']}건 · 질의 {q}건 중 오류 {e}건 · 처리 {'완료' if k in done else '대기'}")
        return

    if a.cmd == "mark":
        done[a.date] = {"opened": a.opened, "added": a.added, "skipped": a.skipped, "leads": a.leads, "at": dt.datetime.now(KST).isoformat(timespec="minutes")}
        (D / "processed.json").write_text(json.dumps(done, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
        print("기록:", a.date, done[a.date])
        return

    # show
    tiers = set(a.tier.split(","))
    qs = set(a.q.split(",")) if a.q else None
    targets = [p for p in files() if (p.stem == a.date if a.date else p.stem not in done)]
    if not targets:
        print("처리할 후보 파일 없음")
        return
    seen = set()
    for p in targets:
        d = json.loads(p.read_text(encoding="utf-8"))
        h, e, q = health(d)
        print(f"## {p.stem} · {h} · 후보 {d['count']}건 · 정리 {d.get('stats_triage')}")
        clusters = []   # 같은 사건으로 보이는 기사 묶음(제목 단어가 절반 이상 겹침)
        for i, it in enumerate(d["items"]):
            if it.get("tier", "B") not in tiers or (qs and not (set(it["questions"]) & qs)):
                continue
            if it["url"] in seen:
                continue
            seen.add(it["url"])
            tk = toks(it["title"])
            for c in clusters:
                if len(tk & c["tk"]) >= 0.5 * min(len(tk), len(c["tk"])) and len(tk & c["tk"]) >= 3:
                    c["members"].append((i, it))
                    break
            else:
                clusters.append({"tk": tk, "members": [(i, it)]})
        for c in clusters:
            i, it = c["members"][0]
            n = len(c["members"])
            sim = ",".join(f"{x['id']}({x['score']})" for x in it.get("similar", []))
            hosts = ",".join(m[1]["host"].replace("www.", "") for m in c["members"][1:4])
            line = f"[{p.stem[5:]}#{i}] {it.get('tier','B')} {'/'.join(it.get('q_title') or ['('+x+')' for x in it['questions'][:2]])} {it['published'][5:10]} {it['host'].replace('www.','')} | {it['title'][:70]}"
            if n > 1:
                line += f" | 동일 사건 {n}건({hosts}…)"
            if sim:
                line += f" | 유사:{sim}"
            print(line)
            if a.full:
                print("    ", it["url"], "|", it["desc"][:140])

if __name__ == "__main__":
    main()
