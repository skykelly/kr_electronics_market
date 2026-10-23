"""수집 로그. 일간·요일 배치가 질문별로 얼마나 훑었는지 state/coverage/<날짜>.json에 남긴다.

  python3 tools/coverage.py log <질문> --queries N --opened N --candidates N --added N [--skipped '사유;사유'] [--leads '단서;단서']
  python3 tools/coverage.py report [날짜]     # 질문별 표와 미달 질문(질의 수 < tools/queries.json 의 80%)
  python3 tools/coverage.py missing           # 오늘 로그가 없는 질문
  python3 tools/coverage.py plan <질문>...     # 오늘 돌릴 질의(질문당 하루 한도 DAILY_CAP, 날짜로 순환). 검색 호출은 한 번의 실행에서 에이전트가 공유해 약 200회가 한도다.
날짜는 KST 오늘.
"""
import json, sys, os, datetime, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def today():
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
def path(d): return os.path.join(ROOT, "state", "coverage", d + ".json")
def load(d):
    p = path(d)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
DAILY_CAP = 8
def day_index():
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).toordinal()
def plan(qs, Q):
    out = {}
    for k in qs:
        L = Q[k]["queries"]
        if len(L) <= DAILY_CAP: out[k] = L; continue
        st = (day_index() * DAILY_CAP) % len(L)
        out[k] = [L[(st + i) % len(L)] for i in range(DAILY_CAP)]
    return out
def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return
    cmd = a[0]; Q = json.load(open(os.path.join(ROOT, "tools", "queries.json"), encoding="utf-8"))["questions"]
    if cmd == "log":
        ap = argparse.ArgumentParser(); ap.add_argument("q"); ap.add_argument("--queries", type=int, required=True)
        ap.add_argument("--opened", type=int, default=0); ap.add_argument("--candidates", type=int, default=0)
        ap.add_argument("--added", type=int, default=0); ap.add_argument("--skipped", default=""); ap.add_argument("--leads", default="")
        n = ap.parse_args(a[1:]); d = today(); data = load(d)
        if n.q not in Q: sys.exit("없는 질문: " + n.q)
        data[n.q] = {"queries_run": n.queries, "queries_planned": len(plan([n.q], Q)[n.q]), "opened": n.opened, "candidates": n.candidates,
                     "added": n.added, "skipped": [s for s in n.skipped.split(";") if s], "leads": [s for s in n.leads.split(";") if s]}
        os.makedirs(os.path.dirname(path(d)), exist_ok=True)
        json.dump(data, open(path(d), "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("기록", n.q)
    elif cmd == "report":
        d = a[1] if len(a) > 1 else today(); data = load(d); short = []
        print(d, "질문 | 질의 | 연 원문 | 후보 | 반영")
        for k in Q:
            r = data.get(k)
            if not r: print(k, "| 로그 없음"); short.append(k); continue
            print(k, "|", f"{r['queries_run']}/{r['queries_planned']}", "|", r["opened"], "|", r["candidates"], "|", r["added"])
            if r["queries_run"] < 0.8 * r["queries_planned"]: short.append(k)
        print("수집 미완료:", ", ".join(short) or "없음")
    elif cmd == "plan":
        for k, v in plan(a[1:] or list(Q), Q).items():
            print(k, len(v)); [print("  ", x) for x in v]
    elif cmd == "missing":
        data = load(today()); print(" ".join(k for k in Q if k not in data) or "없음")
main()
