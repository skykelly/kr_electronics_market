# KR Appliance Signals 작업 규칙

저장소 구조와 회차 흐름은 README.md, 포털 생성은 site/README.md를 본다. 이 파일은 사람이 매번 승인하던 판단 규칙과 수동 입력 절차를 적는다. 작업 전 항상 `git pull`(정기 실행과 수동 작업이 같은 저장소를 고친다).

## 공통 판단 규칙
- 원본은 질문별 `records_base.jsonl`(+ `patches.jsonl`, `daily.jsonl`). 변경 이력은 `changelog/<날짜>.json`(기준선 2026-10-21)이며 기록에서 다시 만들지 않는다. `records.jsonl`·아티클·변경 이력·포털은 언제든 다시 만드는 결과물이다.
- 출처 등급 A(1차·공식·공시) / B(주요 언론) / C(블로그·출처 불명). **C는 단독 근거로 쓰지 않는다.**
- **근거 없는 추측 금지, 근거 있는 정리는 적극:** 회사 의도·원인 추정, 가설, "~할 것이다" 식 예측은 기록하지 않는다(아래 분석 전망 규칙을 갖춘 경우만 예외). 해석은 지표·사건 2건 이상을 `basis`로 연결해 패턴·비교·전환점·구간별 특징·브랜드 간 차이를 쓴다(R0의 "증감만" 규칙은 폐기, `docs/retro_r0.md`).
- **전망은 두 종류:** `forecast_kind` = '회사 계획'(회사가 공식 발표한 목표·계획, `announced_by` 필수, 이행/미이행/만료로 추적) 또는 '분석 전망'(이 리포트의 판정 가능한 전망). 분석 전망은 작성일(`made_on`)로부터 6~18개월 안의 마감(`due`), `condition`, `method`(판정 방법), `reasoning`(예측 근거), `counter`(틀릴 수 있는 이유), 가능하면 `history`(과거 반복)를 적고, 사실 기록 2건 이상 + 해석 1건 이상을 `basis`로 연결한다. 판정은 맞음/틀림/판정 불가로 기록하고 틀린 전망도 지우지 않는다. 회사 의도 추정은 예측 근거로 쓰지 않는다.
- **질문 하나씩, 충분히:** 딥리서치는 한 번에 한 질문. 질문당 직접 연 원문 30건 이상·기록 30건 이상을 목표로 하고, 질문이 다루는 기간에 빈 구간을 남기지 않는다.
- **아티클 구조:** 한 줄 답 → 인사이트 요약(근거 번호) → 서술형 해석(문단마다 근거) → 원장 표 → 연표 → 지표 → 분석 전망 → 예측 근거 → 회사 공식 계획 → 미확인. 내용은 `meta.json`의 `insights`·`narrative`·`ledger`에 쓴다.
- **출처 유형:** `claim_type`을 자사 집계 / 외부 검증 / 공시로 단다. 자사 집계는 `external_check`에 외부 검증 출처 또는 '미확보'를 쓴다. 삼성 "자체 집계" 수치를 시장 사실처럼 쓰지 않는다.
- **글로벌 수치 혼용 금지:** 삼성 글로벌 TV 점유율, DX 실적 등은 한국 가전 성과로 쓰지 않는다. 한국 값이 없으면 기록하지 않고 `meta.json`의 `unknowns`에 적는다.
- 원문을 직접 열지 못한 값, 정의가 다른 값, 확신이 낮은 값은 단정하지 않는다. 문장에 차이를 병기하고 `check_flags`에 '확인 필요'를 남긴다.
- 기간이 있는 사건(판촉 등)은 `period_start`·`period_end`를 적고, 조건이 바뀌면 새 기록이 아니라 `patches.jsonl`의 revise(갱신)로 고친다.
- 아티클 본문에는 사실과 기준만 쓴다. "검증 결과에 따르면" 같은 과정 문구는 넣지 않는다.
- 문장을 바꾸면 이전 문장과 이유를 남긴다(revisions). 변경 종류는 `lib/records.py`의 KIND_ORDER만 쓴다.
- 반영 후: `lib/build_records.py` → `lib/render_article.py` → `python3 site/build_site.py`(깨진 링크 0) → PC·폰 폭 화면 점검 → 커밋 → 포털 게시.
- 보고 형식: 반영·건너뜀 건수, 신규 사건 목록, 갱신된 기록, '확인 필요' 목록, 한계.
- 경영진·외부 공유용 문장은 짧은 보고체, 줄표로 문장 잇지 않기, 비유·과장 없음, 약어는 처음에 풀어 쓰기.

## 일간 배치 절차 (매일 07:23 KST)
수집 구조: 06:30 KST에 GitHub Actions(`collect-news`)가 네이버 뉴스 API로 질문별 질의를 돌려 `state/candidates/<날짜>.json`을 커밋한다(조회 14일 겹침, 토큰 0). 일간 배치는 이 후보를 읽고 검증·반영한다. 하위 에이전트와 검색 도구 수집은 쓰지 않는다.
1. `git pull --rebase`. `python3 tools/candidates.py status`로 수집 상태를 본다. 오늘 후보 파일이 없거나 '실패'면 수집 실패로 보고하고, 이 배치는 3단계의 전망 판정과 단서 처리만 한다(검색으로 대체 수집하지 않는다. 다음 날 14일 겹침이 메운다).
2. **후보 읽기.** `python3 tools/candidates.py show`로 처리 안 된 날짜의 A등급 후보(사건 단서어 + 제목에 브랜드)를 같은 사건끼리 묶어 읽는다. 질문별로 좁히려면 `--q C1,O1`, B등급 제목을 훑으려면 `--tier A,B`, 주소와 요약까지 보려면 `--full`. B등급은 제목만 훑어 사건 같은 것만 올리고, C등급은 읽지 않는다. `유사:<ID>`가 붙은 후보는 그 기록과 대조해 같은 사건이면 제외하고, 기간·조건이 바뀐 경우만 `revise`로 갱신한다.
3. **검증·반영(본 실행, 직렬).** 수집 단계(Actions)가 A등급 후보의 핵심 문장을 `excerpt`로 붙여 둔다(`show --full`에 표시, 전문은 저장하지 않음). 발췌의 날짜·수치·주체가 사건 판정에 충분하면 발췌로 확인하고 기사 주소를 출처로 단다. 발췌가 없거나(`fetch` 실패) 부족하면 WebFetch로 원문을 직접 연다(무인 실행에서 열람 승인이 나지 않으면 단서로 남긴다). 후보마다 확인하고 규칙(출처 등급, 자사 집계, 글로벌 수치 제외, 추측 금지)으로 판정한 뒤 질문(catalog.json)에 배정한다. 기사에 보도자료·공시 링크가 있으면 그 1차 원문(A)을 출처로 단다. 하루 원문 열람은 40건을 상한으로 하고, 넘는 후보는 단서로 남긴다.
   - 중국 브랜드는 C1~C6(C1 로보락, C2 드리미, C3 에코백스, C4 샤오미, C5 TCL, C6 하이센스·마이디어·하이얼·모바)에 넣고 그 밖의 브랜드는 C6에 넣는다. Z1~Z5는 폐기됐다.
   - 한국 기타 경쟁사는 O1 코웨이, O2 쿠쿠, O3 SK매직, O4 다이슨(korea-competitors/oN)에 넣는다. 한국 값만 기록하고 해외·글로벌·해외 포함 연결 수치는 `unknowns`나 `check_flags`로 돌린다. 점유율은 조사기관이 없으면 '조사기관 없음' 플래그를 단다.
   - 신규: `python3 tools/daily.py add <질문 폴더> '<기록 JSON>'`
   - 기간·조건 변경: `python3 tools/daily.py revise <질문 폴더> <ID> 갱신 '<이유>' '<set JSON>'`
   - 마감이 지난 전망(회사 계획·분석 전망): `python3 tools/daily.py judge`. 틀린 전망도 지우지 않는다.
   - 판단이 애매하면 반영하지 않고 단서로 남긴다.
4. **처리 기록.** `python3 tools/candidates.py mark <후보 날짜> --opened <연 원문 수> --added <반영 수> --skipped '<제외 사유;...>' --leads '<단서;...>'`를 처리한 날짜마다 남긴다.
5. 바뀐 질문만 `lib/render_article.py` → `python3 site/build_site.py`(깨진 링크 0).
6. `python3 lib/diff_day.py --note "수집: 후보 N건(A등급 N) · 원문 N건 · 반영 N건 · 수집 상태 <정상|실패>"`(변화가 없어도 실행). 그다음 다시 `site/build_site.py`.
7. 커밋(`state/candidates/processed.json` 포함) → `git push`. 포털 재게시는 기록이 바뀐 날만 한다(아래 '포털 게시'). 변화 없는 날은 생략하고 그 날의 '변화 없음'은 changelog에만 남긴다.
8. 보고: 신규 N건 · 갱신 N건 · 판정 N건, 신규 사건 목록, '확인 필요'·단서 목록, 수집 요약(후보·A등급·원문·반영 수, 수집 상태). 변화가 없으면 "변화 없음"과 수집 요약. 수집 실패인 날은 "변화 없음" 대신 "수집 실패"로 쓴다.

## 재현율 점검 (주간 배치에서 함께)
지난 7일 기록 중 후보 파일에서 같은 사건이 보이지 않는 것(수동 입력·단서로 들어온 사건 포함)을 세어 보고에 적고, 놓친 유형이 있으면 `tools/queries.json` 검색어나 `tools/news_keywords.json` 필터를 보강한다. B·C등급 후보 중 사건이었던 것이 있으면 `tools/triage_candidates.py`의 단서어를 고친다.

## 주간 배치 절차 (월요일 08:52 KST)
1. `git pull` 후 30일 안에 마감되는 전망을 모아 판정 가능한 것을 판정한다(`tools/daily.py judge`).
2. 질문별 '확인 필요' 기록 중 3~5건을 골라 원문을 찾아 해소한다(`revise`, 종류는 누락정정·단정반증·상충 중).
3. 지난 7일 `changelog/*.json`을 요약해 `python3 lib/diff_day.py --note "주간 요약: ..."`로 오늘 Diff에 메모를 남긴다.
4. 렌더 → 포털 생성 → 커밋 → 재게시 → 보고(판정 N건, 해소 N건, 다음 주 마감 전망 목록).

## 회차 재조사(월간 딥리서치)
- 한국 기타 경쟁사(O1~O4)는 업체별로 (1) 기존 기록 없이 독립 조사, (2) 원문 대조, (3) 기록·해석·전망 작성, (4) 메타 판정 순서로 한다. 스크립트는 tools/oN/(oN_add.py, oN_interp.py, oN_meta.py)이고 `python3 tools/o_tmpl/mkobuild.py oN <업체>`로 oN_build.py를 만든다. 빌드 순서는 oN_build → build_records → oN_meta → render_article → build_site → diff_day --round ON → build_site.
- 중국 브랜드 질문 재편(2026-10-21~): 브랜드마다 (1) Z1~Z5에서 그 브랜드가 주어인 사실 기록만 합쳐 옮기고(moved_from에 원 ID), (2) 기존 기록을 보지 않는 독립 조사를 하위 에이전트로 돌려 대조하고, (3) 축×연도 빈칸을 원문으로 채운 뒤, (4) 해석·판정을 새로 쓴다. 생성 스크립트는 tools/c1/c1_build.py(재배치)·c1_add.py(보강)·c1_interp.py(해석·전망)·c1_meta.py를 본뜬다. 옮긴 Z 기록을 인용하던 X·S 기록은 tools/cN/cN_zmap.json으로 새 번호로 바꾼다. 판정은 meta.json의 judge(축 6개 × 진입·확장·정착·주도)로 쓴다. Z1~Z5는 C6까지 끝나면 정리한다.
- 요청 시 진행한다. 질문 build 스크립트로 `records_base.jsonl`을 다시 만든 뒤 `python3 lib/diff_day.py --round <질문>`으로 회차 1줄만 이력에 남긴다.

## 증분 회차 (질문별 리포트 재조사, 평일 10:14 KST 예약)
- 순서: `python3 tools/rotation.py due`로 오늘 질문(최대 3개)을 고른다. 등급별 간격은 1등급 7일, 2등급 15일, 3등급 30일(`tools/rotation.json`). 간격의 90% 이상 지난 질문을 많이 지난 순으로 고른다. 건너뛴 날은 다음 실행이 따라잡는다. `rotation.py status`로 전체 현황, `plan`으로 예상 배정을 본다.
- 한 질문 절차(직렬): (1) `git pull --rebase`. (2) 직전 회차 이후 일간 배치가 쌓은 기록과 단서(`python3 tools/intake.py leads <질문>`), 후보(`tools/candidates.py show --q <질문> --full`)를 읽는다. (3) 빈 구간만 원문(A/B)을 열어 `tools/daily.py add`로 추가한다(발췌로 충분하면 발췌, 아니면 WebFetch). (4) `cp meta.json meta_r<N>.json`으로 직전 회차를 보관하고 meta.json을 N+1로 올린다(round, date, round_label '<N+1>회차(증분)', one_line·rows·insights·narrative·ledger·unknowns 반영, 기존 문장은 근거가 바뀐 곳만 고친다). (5) 마감 전망은 `daily.py judge`. (6) `lib/build_records.py <질문>` → `lib/render_article.py <질문> --round N+1`. (7) `python3 lib/diff_report.py <질문> --old <질문>/meta_r<N>.json`(리포트 Diff, 종류 '회차 변경') → `python3 lib/diff_day.py`(기록 단위 Diff). (8) `python3 site/build_site.py`(깨진 링크 0), 폰·PC 폭 점검.
- 하루 끝: 커밋·푸시, 포털 게시는 하루 한 번만('포털 게시'), 보고(질문별 새 기록 수, 리포트 변경 항목 수, '확인 필요', 한계). 새 사실이 없으면 회차를 올리지 않고 `meta.json`의 date만 확인 날짜로 갱신하지 않는다(건너뜀으로 보고).
- 한 질문에서 새 원문이 30건에 못 미쳐도 증분 회차는 그대로 진행한다. 30건 기준은 월 1회 전체 재조사(수동 요청)에서 맞춘다.

## 포털 게시
- 아티팩트 https://claude.ai/artifact/XKKnhH2SFLjhcxBi5PBxpn. 진입 페이지는 1.4KB 셸(`site/dist/artifact_index.html`)이다. 본문은 `portal_body.html`, 스타일·스크립트는 `assets/portal.css`·`assets/portal.js`로 분리되어 있다(`site/split_entry.py`가 build_site 끝에서 만든다). 읽는 비용이 작으므로 게시 전 아티팩트를 read로 열어 최신 판을 기준으로 삼는다.
- 게시: `file_path`는 `site/dist/artifact_index.html`, `root`는 `site/dist`. `files`에는 `portal_body.html`과 바뀐 페이지(`manifest.json`의 `pages`)를 넣는다. `assets/*`는 바뀐 때만 넣는다. `index.html`은 files에 넣지 않는다(예약 경로).
- `capabilities`는 생략해 저장된 선언(sample, db, user)을 유지한다. `portal_body.html`에 doctype이 없다는 경고는 정상이다(셸이 가져다 끼우는 조각).
- "더 새 버전이 있다"며 거부되면 라이브 판을 read로 전부 읽은 뒤 같은 내용으로 다시 게시한다.
- 챗봇 이전 대화는 db의 `data/users/<id>/chats`에 본인 계정 전용으로 저장된다.

## 수동 지식 입력 (채팅으로 받은 자료)
기본 모드는 **검토 후 반영**. 사용자가 "바로 반영"이라고 할 때만 검토 카드를 건너뛴다.

1. 보관: `python3 tools/intake.py stage <파일> --title .. --slug <영문> [--author --date --url --grade]`
   - 원본은 `inbox/`(git 제외)에만 둔다. 저장소가 공개일 수 있어 남의 글 전문이나 사내 자료를 커밋하지 않는다.
   - 사내·비공개 자료는 받지 않는다(현재 방침). 받게 되면 이 규칙부터 바꾼다.
2. 추출·대조: 자료의 주장을 뽑아 질문(catalog.json)에 매핑하고, 기존 기록과 비교해 일치/갱신/상충/신규로 나눈다.
3. 원문 확인: 자료 자체가 C등급이거나 URL이 없으면 주장마다 원문(A/B)을 찾는다. 확인된 범위만 기록 문장으로 쓴다.
   - 사용자 메모·관찰은 사실 기록이 아니라 **단서(lead)**로 받는다. 원문을 찾으면 기록으로 올린다.
   - 사용자의 문장 지적("이 문장 틀렸어")은 근거를 확인한 뒤 누락정정·단정반증으로 반영한다.
4. 후보 작성: `intake/<ID>.proposal.json` (형식은 tools/intake.py 머리말). 원문 전문은 넣지 않는다.
5. 검토 카드: `python3 tools/intake.py preview <ID>` 결과를 채팅에 보여주고 승인을 받는다.
6. 반영: `python3 tools/intake.py apply <ID> [--only 1,2 | --skip 3]` → 질문별 `daily.jsonl`에 쓰고 build_records를 돌린다. 출력의 "meta.json에서 확인할 곳"을 보고 문장을 맞춘 뒤 위 '반영 후' 절차를 따른다.
7. 추적: `intake.py list`(접수 목록), `intake.py leads [질문]`(미확인 단서 — 다음 회차 요청서에 넣는다).
