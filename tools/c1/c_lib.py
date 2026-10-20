import json
from pathlib import Path
from c_src import SRC
ROOT=Path(__file__).resolve().parents[2]
NOEXT="미확보(독립 기관 수치 확인 못 함)"
class B:
    def __init__(s,Q,outdir,here):
        s.Q=Q; s.out=ROOT/outdir; s.here=Path(here); s.R=[]
    def src(s,ks): return [{"grade":SRC[k][0],"publisher":SRC[k][1],"url":SRC[k][2],"date":SRC[k][3]} for k in ks]
    def ev(s,k,date,actor,et,stmt,ks,**kw):
        r=dict(k=k,type="사건",date=date,actor=actor,event_type=et,statement=stmt,sources=s.src(ks),recurrence=kw.pop("rec","비정기"),claim_type=kw.pop("claim","해당 없음"),importance=kw.pop("imp",2)); r.update(kw); s.R.append(r)
    def me(s,k,ind,unit,asof,val,stmt,ks,claim="해당 없음",**kw):
        r=dict(k=k,type="지표",indicator=ind,unit=unit,as_of=asof,region="한국",value=val,statement=stmt,sources=s.src(ks),claim_type=claim,importance=kw.pop("imp",2)); r.update(kw); s.R.append(r)
    def it(s,k,basis,dirn,target,stmt,imp=3): s.R.append(dict(k=k,type="해석",basis=basis,direction=dirn,target=target,statement=stmt,importance=imp,claim_type="해당 없음"))
    def af(s,k,due,stmt,cond,method,reasoning,counter,basis,history=None,imp=2):
        r=dict(k=k,type="전망",forecast_kind="분석 전망",made_on="2026-10-20",due=due,statement=stmt,condition=cond,method=method,reasoning=reasoning,counter=counter,basis=basis,forecast_status="진행 중",importance=imp,claim_type="해당 없음")
        if history: r["history"]=history
        s.R.append(r)
    def cp(s,k,due,stmt,method,by,basis=None,imp=2,flags=None):
        r=dict(k=k,type="전망",forecast_kind="회사 계획",due=due,statement=stmt,method=method,announced_by=by,forecast_status="진행 중",importance=imp,claim_type="해당 없음")
        if basis: r["basis"]=basis
        if flags: r["flags"]=flags
        s.R.append(r)
    def finish(s,patches):
        Q=s.Q; cnt={"사건":0,"지표":0,"해석":0,"전망":0}; L={"사건":"E","지표":"M","해석":"I","전망":"F"}; amap={}
        order=[r for r in s.R if r["type"]=="사건"]; order.sort(key=lambda r:r["date"])
        for t in ("지표","전망","해석"): order+=[r for r in s.R if r["type"]==t]
        for r in order:
            cnt[r["type"]]+=1; r["id"]=f"{Q}-{L[r['type']]}-{cnt[r['type']]:03d}"; amap[r["k"]]=r["id"]
        for r in order:
            if "basis" in r: r["basis"]=[amap[b] for b in r["basis"]]
            r.pop("k"); r["added_on"]="2026-10-20"; r["first_seen"]="R1"; r["question"]=Q
            if r["claim_type"]=="자사 집계" and not r.get("external_check"): r["external_check"]=NOEXT
            if "flags" in r: r["check_flags"]=r.pop("flags")
        json.dump(amap,open(s.here.with_name(Q.lower()+"_amap.json"),"w"),ensure_ascii=False,indent=0)
        (s.out/"records_base.jsonl").write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in sorted(order,key=lambda r:r["id"])),encoding="utf-8")
        pt=[]
        for p in patches:
            p=dict(p); p["id"]=amap[p["id"]]; p.setdefault("op","revise"); p.setdefault("on","2026-10-20"); p.setdefault("kind","갱신")
            if "add_basis" in p: p["add_basis"]=[amap[x] for x in p["add_basis"]]
            pt.append(p)
        (s.out/"patches.jsonl").write_text("".join(json.dumps(p,ensure_ascii=False)+"\n" for p in pt),encoding="utf-8")
        print(cnt,"sources:",len({x["url"] for r in order for x in r.get("sources",[])}))
