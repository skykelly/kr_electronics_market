"""리포트 단위 Diff: 같은 질문의 이전 회차 meta(meta_rN.json)와 현재 meta.json을 비교해 changelog에 '회차 변경' 항목을 쌓는다.

사용:
  python3 lib/diff_report.py samsung/s6 --old samsung/s6/meta_r1.json [--date 2026-10-27] [--dry-run]

비교 대상: 한 줄 답(one_line), 답 표(rows, label 기준), 인사이트(insights, title 기준),
서술(narrative, heading 기준 문단), 원장 표(ledger.rows, 첫 칸 기준), 판정(judge), 미확인(unknowns, item 기준).
항목 id는 '<번호>-R<회차>:<영역>' 형식. 기록 단위 신규·갱신은 diff_day.py가 따로 쌓는다.
같은 날 다시 돌리면 같은 id 항목은 덮어쓴다.
"""
import argparse, json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "changelog"


def j(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def keyed(lst, key):
    return {key(x): x for x in lst or []}


def cmp_list(area, old, new, key, text, basis=lambda x: x.get("basis")):
    out = []
    o, n = keyed(old, key), keyed(new, key)
    for k in n:
        if k not in o:
            out.append((f"{area}:{k}", f"{area} 추가: {k}", None, text(n[k]), "새 항목을 더했다."))
        elif text(o[k]) != text(n[k]):
            out.append((f"{area}:{k}", f"{area} 수정: {k}", text(o[k]), text(n[k]), "문장이 바뀌었다."))
        elif basis(o[k]) != basis(n[k]):
            out.append((f"{area}:{k}", f"{area} 근거 변경: {k}", text(o[k]), text(n[k]), "문장은 같고 근거 기록이 바뀌었다."))
    for k in o:
        if k not in n:
            out.append((f"{area}:{k}", f"{area} 삭제: {k}", text(o[k]), None, "항목을 뺐다."))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("qdir")
    ap.add_argument("--old", required=True)
    ap.add_argument("--date")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    qd = ROOT / a.qdir if not Path(a.qdir).is_absolute() else Path(a.qdir)
    old = json.loads(Path(a.old).read_text(encoding="utf-8"))
    new = json.loads((qd / "meta.json").read_text(encoding="utf-8"))
    no, r = new["no"], new.get("round")
    day = a.date or datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")
    res = []  # (id, label, before, now, why)
    if old.get("one_line") != new.get("one_line"):
        res.append(("one_line", "한 줄 답", old.get("one_line"), new.get("one_line"), "한 줄 답이 바뀌었다."))
    elif old.get("one_line_basis") != new.get("one_line_basis"):
        res.append(("one_line", "한 줄 답 근거", j(old.get("one_line_basis")), j(new.get("one_line_basis")), "문장은 같고 근거 기록이 바뀌었다."))
    res += cmp_list("rows", old.get("rows"), new.get("rows"), lambda x: x["label"], lambda x: x["text"])
    res += cmp_list("insights", old.get("insights"), new.get("insights"), lambda x: x["title"], lambda x: x["text"])
    res += cmp_list("narrative", old.get("narrative"), new.get("narrative"), lambda x: x["heading"],
                    lambda x: " ".join(p["text"] if isinstance(p, dict) else str(p) for p in x["paras"]),
                    basis=lambda x: [p.get("basis") if isinstance(p, dict) else None for p in x["paras"]])
    ol, nl = old.get("ledger") or {}, new.get("ledger") or {}
    res += cmp_list("ledger", ol.get("rows"), nl.get("rows"), lambda x: str(x[0] if isinstance(x, list) else x.get("cells", [x])[0]),
                    lambda x: j(x), basis=lambda x: None)
    if old.get("judge") != new.get("judge"):
        res.append(("judge", "판정", j(old.get("judge")), j(new.get("judge")), "판정 표가 바뀌었다."))
    res += cmp_list("unknowns", old.get("unknowns"), new.get("unknowns"), lambda x: x["item"], lambda x: x.get("why", ""), basis=lambda x: None)
    items = [{"q": no, "id": f"{no}-R{r}:{i}", "kind": "회차 변경", "now": now, "before": before, "why": f"{label}. {why}", "origin": "round"}
             for i, label, before, now, why in res]
    items = [{k: v for k, v in it.items() if v is not None} for it in items]
    path = LOG / f"{day}.json"
    entry = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"date": day, "notes": [], "items": []}
    ids = {x["id"] for x in items}
    entry["items"] = [x for x in entry["items"] if x.get("id") not in ids] + items
    note = f"{no} 회차 {r} 리포트 변경 {len(items)}건 (이전 {old.get('round')}회차 대비)"
    entry["notes"] = [x for x in entry["notes"] if x != "변화 없음" and not x.startswith(f"{no} 회차 {r} 리포트 변경")] + [note]
    print(f"{day}: {note}")
    for it in items:
        print("  -", it["why"][:90])
    if not a.dry_run:
        LOG.mkdir(exist_ok=True)
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
