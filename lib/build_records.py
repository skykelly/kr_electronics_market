"""질문 폴더의 records_base.jsonl + patches.jsonl → records.jsonl 생성과 규칙 검증.

사용: python3 lib/build_records.py <질문 폴더>   예) python3 lib/build_records.py samsung/s1
- records_base.jsonl : 조사 회차(딥리서치·일간 간단 조사)가 쌓는 기록 원본. 한 줄 = 한 기록.
- patches.jsonl      : 수동 입력분(tools/intake.py). lib/records.py 의 apply_patches 가 적용.
- records.jsonl      : 위 둘을 합쳐 검증한 결과물. 아티클·Diff·포털은 이 파일만 읽는다.

기록 형식은 README.md '기록 형식'을 본다. 규칙을 어기면 종료 코드 1로 끝난다.
"""
import json, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from records import apply_patches, GRADES

TYPE_OF = {"M": "지표", "E": "사건", "I": "해석", "F": "전망"}
CLAIMS = ("자사 집계", "외부 검증", "공시", "해당 없음")
EVENT_TYPES = ("전략·조직", "제품 출시", "AI·연결", "마케팅", "채널·매장", "판촉", "구독·케어·AS", "제휴·협업", "실적·시장", "인증·규제", "기타")
RECUR = ("정기", "비정기", "해당 없음")
DIRS = ("강화", "약화", "중립")
FSTAT = ("진행 중", "이행", "미이행", "변경", "만료")
DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def load(path):
    out = []
    p = Path(path)
    if not p.exists():
        return out
    for ln, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{p.name} {ln}행: JSON 오류 {e}")
    return out


def validate(recs, qno):
    errs, ids = [], {}
    id_re = re.compile(rf"^{qno}-([MEIF])-\d{{3}}$")
    for r in recs:
        rid = r.get("id", "?")
        m = id_re.match(rid)
        if not m:
            errs.append(f"{rid}: ID 형식이 {qno}-M/E/I/F-NNN 이 아님")
            continue
        if rid in ids:
            errs.append(f"{rid}: ID 중복")
        ids[rid] = r
        if TYPE_OF[m.group(1)] != r.get("type"):
            errs.append(f"{rid}: ID 글자와 type({r.get('type')}) 불일치")
        if not (r.get("statement") or "").strip():
            errs.append(f"{rid}: statement 없음")
        if r.get("importance") not in (1, 2, 3):
            errs.append(f"{rid}: importance는 1~3")
        if r.get("status") not in ("유효", "미확인", "대체됨", "반박됨"):
            errs.append(f"{rid}: status 값 오류")
        if r.get("claim_type") not in CLAIMS:
            errs.append(f"{rid}: claim_type은 {CLAIMS} 중 하나")
        if r.get("claim_type") == "자사 집계" and not r.get("external_check"):
            errs.append(f"{rid}: 자사 집계는 external_check(외부 검증 출처 또는 '미확보') 필요")
        srcs = r.get("sources") or []
        for s in srcs:
            if s.get("grade") not in GRADES or not s.get("url") or not s.get("publisher"):
                errs.append(f"{rid}: 출처 형식 오류 {s}")
        has_ab = any(s.get("grade") in ("A", "B") for s in srcs)
        t = r.get("type")
        if t in ("지표", "사건"):
            if not srcs:
                errs.append(f"{rid}: {t}은 출처 1개 이상 필요")
            if r.get("verified") and not has_ab:
                errs.append(f"{rid}: C등급만으로 verified 불가")
            if not has_ab and not r.get("check_flags"):
                errs.append(f"{rid}: A/B 출처가 없으면 check_flags에 '확인 필요' 사유 필요")
        if t == "사건":
            for k in ("date", "actor", "event_type"):
                if not r.get(k):
                    errs.append(f"{rid}: 사건에 {k} 없음")
            if r.get("date") and not DATE_RE.match(r["date"]):
                errs.append(f"{rid}: date는 YYYY 또는 YYYY-MM 또는 YYYY-MM-DD")
            if r.get("event_type") not in EVENT_TYPES:
                errs.append(f"{rid}: event_type은 {EVENT_TYPES} 중 하나")
            if r.get("recurrence", "해당 없음") not in RECUR:
                errs.append(f"{rid}: recurrence는 {RECUR}")
            for k in ("period_start", "period_end"):
                if r.get(k) and not DATE_RE.match(r[k]):
                    errs.append(f"{rid}: {k} 날짜 형식 오류")
        if t == "지표":
            for k in ("indicator", "unit", "as_of", "region"):
                if not r.get(k):
                    errs.append(f"{rid}: 지표에 {k} 없음")
            if r.get("value") is None:
                errs.append(f"{rid}: 지표에 value 없음 (값이 없으면 기록하지 않고 meta unknowns에 적는다)")
    for r in recs:
        rid = r.get("id", "?")
        t = r.get("type")
        if t == "해석":
            b = r.get("basis") or []
            if len(b) < 2:
                errs.append(f"{rid}: 해석은 사실 기록 2건 이상을 basis로 연결해야 함")
            for x in b:
                if x not in ids:
                    errs.append(f"{rid}: basis {x} 없음")
                elif ids[x].get("type") not in ("지표", "사건"):
                    errs.append(f"{rid}: basis {x}는 지표·사건이어야 함")
            if r.get("direction") not in DIRS or not r.get("target"):
                errs.append(f"{rid}: direction/target 오류")
        if t == "전망":
            for k in ("due", "method", "announced_by"):
                if not r.get(k):
                    errs.append(f"{rid}: 전망에 {k} 없음 (회사 공식 발표 계획만 기록)")
            if not DATE_RE.match(r.get("due") or ""):
                errs.append(f"{rid}: due 날짜 형식 오류")
            ab = r.get("announced_by")
            if isinstance(ab, dict) and not ab.get("url"):
                errs.append(f"{rid}: announced_by에 url 필요")
            for x in r.get("basis") or []:
                if x not in ids:
                    errs.append(f"{rid}: basis {x} 없음")
            if r.get("forecast_status", "진행 중") not in FSTAT:
                errs.append(f"{rid}: forecast_status는 {FSTAT}")
    return errs


def main(qdir):
    qdir = Path(qdir)
    qno = qdir.name.upper()
    recs = load(qdir / "records_base.jsonl")
    if not recs:
        raise SystemExit(f"{qdir}/records_base.jsonl 이 비어 있음")
    for r in recs:
        r.setdefault("question", qno)
        r.setdefault("question_version", "v1.0")
        r.setdefault("status", "유효")
        r.setdefault("replaces", None)
        r.setdefault("check_flags", [])
        r.setdefault("sources", [])
        r.setdefault("verified", any(s.get("grade") in ("A", "B") for s in r["sources"]) if r["type"] in ("지표", "사건") else None)
    n = apply_patches(recs, qdir / "patches.jsonl")
    errs = validate(recs, qno)
    if errs:
        print(f"{qdir}: 규칙 위반 {len(errs)}건")
        for e in errs[:60]:
            print(" -", e)
        sys.exit(1)
    with open(qdir / "records.jsonl", "w", encoding="utf-8") as f:
        for r in sorted(recs, key=lambda x: x["id"]):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    c = Counter(r["type"] for r in recs)
    print(f"{qdir}: 기록 {len(recs)}건 (지표 {c['지표']} · 사건 {c['사건']} · 해석 {c['해석']} · 전망 {c['전망']}), 수동 입력 {n}건 적용")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
