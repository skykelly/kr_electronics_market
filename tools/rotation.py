#!/usr/bin/env python3
"""증분 회차 순환: 오늘 재조사할 질문을 고른다.

  python3 tools/rotation.py due [--date 2026-10-28] [--limit 3]   # 오늘 할 질문(간격의 90% 이상 지난 순)
  python3 tools/rotation.py status                                 # 전체 질문의 마지막 회차, 간격, 경과 비율
  python3 tools/rotation.py plan [--days 14]                        # 앞으로 며칠간 예상 배정(한도 적용)

간격: 1등급 7일, 2등급 15일, 3등급 30일. 건너뛴 날이 있어도 다음 실행이 밀린 질문부터 따라잡는다.
"""
import argparse, json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "tools/rotation.json").read_text(encoding="utf-8"))
KST = timezone(timedelta(hours=9))


def qdir(q):
    return ROOT / CFG["paths"][q[0]] / q.lower()


def rows(today):
    out = []
    for tier, qs in CFG["tiers"].items():
        for q in qs:
            m = json.loads((qdir(q) / "meta.json").read_text(encoding="utf-8"))
            last = date.fromisoformat(m["date"])
            iv = CFG["interval_days"][tier]
            out.append({"q": q, "tier": int(tier), "round": m.get("round"), "last": last, "interval": iv,
                        "ratio": (today - last).days / iv})
    return out


def pick(today, limit):
    return [r for r in sorted(rows(today), key=lambda r: -r["ratio"]) if r["ratio"] >= 0.9][:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["due", "status", "plan"])
    ap.add_argument("--date")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--days", type=int, default=14)
    a = ap.parse_args()
    today = date.fromisoformat(a.date) if a.date else datetime.now(KST).date()
    limit = a.limit or CFG["limit_per_day"]
    if a.cmd == "due":
        sel = pick(today, limit)
        if not sel:
            print("오늘 재조사할 질문 없음")
        for r in sel:
            print(f"{r['q']}  {r['tier']}등급  R{r['round']}→R{r['round']+1}  마지막 {r['last']}  경과 {(today-r['last']).days}일/{r['interval']}일")
    elif a.cmd == "status":
        for r in sorted(rows(today), key=lambda r: -r["ratio"]):
            print(f"{r['q']:3} {r['tier']}등급 R{r['round']} 마지막 {r['last']} 간격 {r['interval']:2}일 경과 {r['ratio']*100:4.0f}%")
    else:  # plan: 가상 실행(평일만, 실행하면 날짜가 갱신된다고 가정)
        sim = {r["q"]: r for r in rows(today)}
        d = today
        for _ in range(a.days):
            if d.weekday() < 5:
                for r in sim.values():
                    r["ratio"] = (d - r["last"]).days / r["interval"]
                sel = [r for r in sorted(sim.values(), key=lambda r: -r["ratio"]) if r["ratio"] >= 0.9][:limit]
                print(d, d.strftime("%a"), ",".join(r["q"] for r in sel) or "-")
                for r in sel:
                    r["last"] = d
            d += timedelta(days=1)


if __name__ == "__main__":
    main()
