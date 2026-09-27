import json, collections, random
W=r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs=[json.loads(l) for l in open(W+r"\runs.jsonl",encoding="utf-8")]




sp=[r for r in runs if r["triggers"].get("spontaneous_replication")]
random.seed(2); samp=random.sample(sp,min(600,len(sp)))
agg=collections.defaultdict(list); zeroish=collections.Counter(); mat=collections.Counter(); interv=0
for r in samp:
    s=json.load(open(r["dir"]+r"\summary.json")); ph=r["vec"]["reproduction"]
    eb=s["endogenous_births"] or 1
    agg[ph].append(s["captures"]/eb)
    if not s["top"]:
        zeroish[(ph,"EXTINCT at end")]+=1; continue
    t=s["top"][0]; tape=bytes.fromhex(t["tape"])
    zeroish[(ph, "top tape >=75% zero bytes" if tape.count(0)>=0.75*len(tape) else "not")]+=1
    if r["kind"]=="intervention": interv+=1
    ev=[json.loads(l) for l in open(r["dir"]+r"\events.jsonl") if '"copy"' in l]
    for e in ev:
        if e.get("kind")=="copy": mat[(ph,e["material"])]+=1
print("spontaneous_replication sample",len(samp),"; of which intervention runs (init_tapes transplanted):",interv)
for ph,v in agg.items(): print(" %-20s n=%d median captures/endogenous_births = %.2f ; >0.5 in %d runs"%(ph,len(v),sorted(v)[len(v)//2],sum(x>0.5 for x in v)))
print(" top-tape zero-dominance:",dict(zeroish))
print(" copy events (first 400/run) by material:",dict(mat))
