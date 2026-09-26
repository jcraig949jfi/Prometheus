import json, collections
W=r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs=[json.loads(l) for l in open(W+r"\runs.jsonl",encoding="utf-8")]
byf=collections.defaultdict(list)
for r in runs: byf[r["family"]].append(r)
flags=json.load(open(W+r"\flags.json"))
def solved(r): return (r["summary"].get("solvers_tail") or 0)>=1
for name in ("REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL","REACHED_INCREMENTAL_NOT_ATOMIC","RESERVOIR_CROSSED_MOAT"):
    fl=[f for f in flags if f["flag"]==name]
    nt=[len(byf[f["family"]]) for f in fl]; nc=[len(byf[f["control_family"]]) for f in fl]
    frac=[sum(map(solved,byf[f["family"]]))/len(byf[f["family"]]) for f in fl]
    kinds=collections.Counter(); inits=collections.Counter(); onlyone=0; tasks=collections.Counter(); scor=collections.Counter(); spat=collections.Counter();envd=collections.Counter()
    seeded_only=0; interv_only=0
    for f in fl:
        sr=[r for r in byf[f["family"]] if solved(r)]
        kinds.update(r["kind"] for r in sr)
        v=byf[f["family"]][0]["vec"]; inits[v["init"]]+=1; tasks[v["task"]]+=1; scor[v["scoring"]]+=1; spat[v["spatial"]]+=1; envd[v["env_dynamics"]]+=1
        if len(sr)==1: onlyone+=1
        if all(r["kind"]=="intervention" for r in sr): interv_only+=1
    print("==",name,len(fl))
    print(" treat runs: mean %.2f median %s ; control runs: mean %.2f median %s"%(sum(nt)/len(nt),sorted(nt)[len(nt)//2],sum(nc)/len(nc),sorted(nc)[len(nc)//2]))
    print(" treat runs > control runs: %d ; control has exactly 1 run: %d"%(sum(a>b for a,b in zip(nt,nc)), sum(b==1 for b in nc)))
    print(" solved-fraction in treatment: median %.2f ; flags where only 1 treatment run solved: %d ; only intervention runs solved: %d"%(sorted(frac)[len(frac)//2], onlyone, interv_only))
    print(" kinds of solved runs",dict(kinds)); print(" init",dict(inits)); print(" task",dict(tasks)); print(" scoring",dict(scor)); print(" spatial",dict(spat)); print(" env",dict(envd))
