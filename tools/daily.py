"""일간·주간 배치용 기록 입력. 질문 폴더의 daily.jsonl에 추가하고 바로 검증한다(실패하면 되돌린다).

  python3 tools/daily.py add <질문 폴더> '<기록 JSON>'
      기록 JSON: type(사건|지표|전망|해석)과 필수 필드. id·added_on·question은 자동.
      출처는 "sources": [{"grade","publisher","url","date"}]. 사용자가 준 자료면 "origin": "manual".
  python3 tools/daily.py revise <질문 폴더> <기록 ID> <변경 종류> '<이유>' '<set JSON>'
  python3 tools/daily.py judge  <질문 폴더> <전망 ID> <판정> '<결과 문장>'
      판정: 맞음|틀림|판정 불가(분석 전망), 이행|미이행|변경|만료(회사 계획)
  python3 tools/daily.py next-id <질문 폴더> <사건|지표|전망|해석>

날짜는 KST 오늘. 반영 후 lib/diff_day.py가 그날 변경 이력을 만든다.
"""
import json, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")
L = {"사건": "E", "지표": "M", "전망": "F", "해석": "I"}


def ids(qdir):
    out = set()
    for f in ("records.jsonl",):
        p = qdir / f
        if p.exists():
            out |= {json.loads(l)["id"] for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}
    p = qdir / "daily.jsonl"
    if p.exists():
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.strip():
                d = json.loads(l)
                if d["op"] == "add":
                    out.add(d["record"]["id"])
    return out


def next_id(qdir, t):
    q = qdir.name.upper()
    n = max([int(i.split("-")[2]) for i in ids(qdir) if i.startswith(f"{q}-{L[t]}-")] or [0]) + 1
    return f"{q}-{L[t]}-{n:03d}"


def append(qdir, obj):
    p = qdir / "daily.jsonl"
    old = p.read_text(encoding="utf-8") if p.exists() else ""
    p.write_text(old + json.dumps(obj, ensure_ascii=False) + "\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "lib/build_records.py"), str(qdir)], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode:
        p.write_text(old, encoding="utf-8") if old else p.unlink()
        subprocess.run([sys.executable, str(ROOT / "lib/build_records.py"), str(qdir)], capture_output=True)
        raise SystemExit("검증 실패로 되돌림:\n" + r.stdout + r.stderr)


def main(a):
    if len(a) < 2:
        raise SystemExit(__doc__)
    cmd, qdir = a[0], (ROOT / a[1]).resolve()
    if cmd == "next-id":
        print(next_id(qdir, a[2])); return
    if cmd == "add":
        rec = json.loads(a[2])
        rec["id"] = rec.get("id") or next_id(qdir, rec["type"])
        rec.setdefault("added_on", TODAY); rec.setdefault("first_seen", "daily"); rec.setdefault("importance", 2)
        rec.setdefault("claim_type", "해당 없음")
        if rec["type"] == "전망":
            rec.setdefault("made_on", TODAY); rec.setdefault("forecast_status", "진행 중")
        append(qdir, {"op": "add", "on": TODAY, "intake": "daily", "record": rec})
        print("추가:", rec["id"])
    elif cmd == "revise":
        rid, kind, why, st = a[2], a[3], a[4], json.loads(a[5])
        append(qdir, {"op": "revise", "id": rid, "kind": kind, "why": why, "on": TODAY, "intake": "daily", "set": st})
        print("갱신:", rid)
    elif cmd == "judge":
        rid, stat, res = a[2], a[3], a[4]
        append(qdir, {"op": "revise", "id": rid, "kind": "판정", "why": f"마감 판정: {stat}", "on": TODAY, "intake": "daily",
                      "set": {"forecast_status": stat, "result": res}})
        print("판정:", rid, stat)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
