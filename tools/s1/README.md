S1 R1 기록 생성 스크립트. s1_src.py(출처) · s1_build.py(기록 → samsung/s1/records_base.jsonl) · s1_meta.py(한 줄 답·인사이트·서술·원장 → meta.json).
R1 이후 갱신은 records_base.jsonl 추가 또는 patches.jsonl로 하고, 이 스크립트를 다시 돌리지 않는다(덮어쓴다).
2026-10-20 사용자 요청으로 S1-E-021(2018 QLED 존 300여 개 보도)·S1-M-002(매장 300여 개 지표)를 records_base.jsonl에서 삭제했다. 스크립트를 다시 돌리면 둘이 되살아나고 번호가 밀리므로 재실행하지 않는다.
