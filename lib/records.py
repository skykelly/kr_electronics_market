"""기록 공통 규칙과 수동 입력(patches.jsonl) 적용.

- 변경 종류(KIND_*)는 여기서만 정의한다. site/changes.py와 tools/intake.py가 가져다 쓴다.
- 각 질문의 build_records.py는 검증 직전에 apply_patches()를 불러
  같은 폴더의 patches.jsonl(수동 입력분)을 기록에 적용한다.

patches.jsonl 한 줄 형식
  {"op": "revise", "id": "I3-M-007", "kind": "갱신", "why": "...", "on": "2026-10-12", "intake": "<접수 ID>",
   "set": {"statement": "...", ...}, "add_sources": [{"url": ..., "publisher": ..., "date": ..., "grade": "A"}],
   "add_flags": ["..."], "add_basis": ["I3-M-010"]}
  {"op": "add", "on": "2026-10-12", "intake": "<접수 ID>", "record": {"id": "I3-E-009", "type": "사건", ...}}
"""
import json, re
from pathlib import Path

KIND_ORDER = ["판정", "누락정정", "단정반증", "전망 교체", "판정 기준 보완", "상충", "전망 점검", "회차 변경", "갱신", "신규", "삭제"]
KIND_CLS = {"누락정정": "k-fix", "단정반증": "k-fix", "전망 교체": "k-fix", "판정 기준 보완": "k-chg", "상충": "k-chg",
            "전망 점검": "k-chk", "회차 변경": "k-chg", "갱신": "k-chk", "신규": "k-new", "판정": "k-fix", "삭제": "k-chg"}
KIND_DEF = {"누락정정": "조사에서 빠졌거나 틀려서 고친 것", "단정반증": "단정한 표현이 새 근거와 맞지 않아 고친 것",
            "전망 교체": "전망의 기준이나 내용을 바꾼 것", "판정 기준 보완": "맞았는지 가릴 기준을 더 분명히 한 것",
            "상충": "출처마다 말이 달라 표시한 것", "전망 점검": "전망의 근거를 다시 살핀 것(결론 그대로)", "회차 변경": "회차 재조사로 리포트의 답·요약·서술·표가 바뀐 것",
            "갱신": "새 사실을 반영해 문장을 고친 것", "신규": "새로 더한 기록",
            "판정": "마감된 전망·계획의 결과(맞음·틀림·이행 등)를 적은 것", "삭제": "기록을 없앤 것(이유를 남김)"}
GRADES = ("A", "B", "C")


def _base_for(records):
    """질문 공통 필드(question, question_version 등)를 기존 기록에서 가져온다."""
    r0 = records[0]
    return {k: r0[k] for k in ("question", "question_version", "first_seen", "last_seen") if k in r0} | \
        {"status": "유효", "replaces": None, "check_flags": []}


def apply_patches(records, path):
    path = Path(path)
    if not path.exists():
        return 0
    by_id = {r["id"]: r for r in records}
    n = 0
    for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        p = json.loads(line)
        meta = {"origin": p.get("origin") or ("daily" if p.get("intake") == "daily" else "manual"), "intake": p.get("intake")}
        if p["op"] == "add":
            rec = dict(_base_for(records))
            rec.update(p["record"])
            rec["added_on"] = p["on"]
            rec.update(meta)
            if rec["id"] in by_id:
                raise ValueError(f"patches.jsonl {ln}행: 이미 있는 ID {rec['id']}")
            records.append(rec)
            by_id[rec["id"]] = rec
        elif p["op"] == "revise":
            r = by_id.get(p["id"])
            if r is None:
                raise ValueError(f"patches.jsonl {ln}행: 없는 기록 {p['id']}")
            if p["kind"] not in KIND_ORDER:
                raise ValueError(f"patches.jsonl {ln}행: 알 수 없는 변경 종류 {p['kind']}")
            ch = p.get("set", {})
            r.setdefault("revisions", []).append({"on": p["on"], "kind": p["kind"], "why": p["why"],
                                                  "before": r.get("statement") if "statement" in ch else None, **meta})
            r.update(ch)
            if p.get("add_sources"):
                r["sources"] = list(r.get("sources", [])) + p["add_sources"]
            if p.get("add_flags"):
                r["check_flags"] = list(r.get("check_flags", [])) + p["add_flags"]
            if p.get("add_basis"):
                r["basis"] = list(r.get("basis", [])) + [b for b in p["add_basis"] if b not in r.get("basis", [])]
        else:
            raise ValueError(f"patches.jsonl {ln}행: 알 수 없는 op {p['op']}")
        n += 1
    return n


ROOT = Path(__file__).resolve().parent.parent


def load_external(qno):
    """다른 질문의 기록(records.jsonl)을 읽어 {ID: (기록, 포털 경로)}로 돌려준다.

    통합 질문(X3 등)이 다른 질문의 사실 기록을 복사하지 않고 basis로 인용할 때 쓴다.
    포털 경로는 site/dist 기준 '<카테고리>/<질문>/r<최신 회차>.html'.
    """
    out = {}
    for f in sorted(ROOT.glob("*/*/records.jsonl")):
        qdir = f.parent
        rounds = sorted(int(m.group(1)) for m in (re.match(r"article_r(\d+)\.html$", x.name) for x in qdir.iterdir()) if m)
        if not rounds:
            continue
        path = f"{qdir.parent.name}/{qdir.name}/r{rounds[-1]}.html"
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("question") == qno:
                break
            if r.get("status") in (None, "유효", "미확인"):
                out[r["id"]] = (r, path)
    return out
