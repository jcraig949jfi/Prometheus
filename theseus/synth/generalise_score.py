"""THESEUS-45 scoring (pre-registered rules): CMH/RD_MH over seed strata from TABLE.jsonl -> SUMMARY.json.

  PYTHONPATH=. python theseus/synth/generalise_score.py
"""
import json, numpy as np
from theseus.synth import pooled as P
rows=[json.loads(l) for l in open("theseus/runs/generalise_2026-10-09/TABLE.jsonl")]
def cmh(pred, grpA, grpB, key):
    tabs=[]
    for st in (1,2,3):
        A=[r for r in rows if r["stratum"]==st and grpA(r)]; B=[r for r in rows if r["stratum"]==st and grpB(r)]
        tabs.append((sum(pred(r) for r in A),len(A),sum(pred(r) for r in B),len(B)))
    z,p=P.cmh(tabs); rd,lo,hi=P.rd_mh(tabs)
    return {"key":key,"tables":tabs,"CMH_z":z,"p":p,"RD_MH":rd,"ci":[lo,hi]}
law=lambda r:r["arm"]=="law"; nol=lambda r:r["arm"]=="nolaw"
out={"H_DELAY":cmh(lambda r:r["J_delay"][4]>=.6,law,nol,"V4k20"),
     "H_ALPHA":cmh(lambda r:r["J_V8k8"]>=.6,law,nol,"V8k8"),
     "H_LAWESS":cmh(lambda r:r["J_delay"][4]>=.6,lambda r:law(r) and r["law_essential"],lambda r:law(r) and not r["law_essential"],"V4k20 within law-on")}
curves={a:[float(np.mean([r["J_delay"][j] for r in rows if r["arm"]==a])) for j in range(5)] for a in ("law","nolaw")}
v8={a:float(np.mean([r["J_V8k8"] for r in rows if r["arm"]==a])) for a in ("law","nolaw")}
def kmax(r):
    ks=[k for k,j in zip([4,8,12,16,20],r["J_delay"]) if j>=.6]; return max(ks) if ks else 0
km={a:{k:sum(kmax(r)==k for r in rows if r["arm"]==a) for k in (0,4,8,12,16,20)} for a in ("law","nolaw")}
le=[r for r in rows if r["arm"]=="law" and r["law_essential"]]
ar={"transfer_k20":[max(r["law_src_distinct"]) for r in le if r["J_delay"][4]>=.6],"fail_k20":[max(r["law_src_distinct"]) for r in le if r["J_delay"][4]<.6]}
ar={k:{"n":len(v),"mean":float(np.mean(v)) if v else None,"counts":{x:v.count(x) for x in sorted(set(v))}} for k,v in ar.items()}
res={"primaries":out,"mean_J_delay_curve_k4_8_12_16_20":curves,"mean_J_V8k8":v8,"largest_k_solved":km,"law_arity_essential":ar,"n":len(rows)}
json.dump(res,open("theseus/runs/generalise_2026-10-09/SUMMARY.json","w"),indent=1)
print(json.dumps(res,indent=1))
