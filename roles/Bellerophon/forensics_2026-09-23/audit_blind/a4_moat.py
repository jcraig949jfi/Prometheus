import json, collections, random, sys
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import vm
from prometheus.z80atlas.tasks import Task, score
W=r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs=[json.loads(l) for l in open(W+r"\runs.jsonl",encoding="utf-8")]
mc=[r for r in runs if r["triggers"].get("moat_crossing")]
print("moat_crossing runs",len(mc),"of",len(runs))
random.seed(1); samp=random.sample(mc,min(1500,len(mc)))
c=collections.Counter(); exact=collections.Counter(); bytask=collections.Counter()
def acc(tape,kind,k,rg):
    T=Task(kind,k=k); ok=0
    for x in range(0,256,1):
        inp=[x] if kind!="SUM2" else [x,(x*37+11)&255]
        mem=bytearray(256); mem[:64]=tape[:64]
        for i,v in enumerate(inp): mem[vm.IN_BASE+i]=v
        tr=vm.execute(mem,len(tape),0,256,inp)
        ok+= score(T,tr.outputs,T.expected(inp),"ATOMIC",rg,tr.first_out_step,tr.first_in_step)>=0.999
    return ok/256
for r in samp:
    s=json.load(open(r["dir"]+r"\summary.json")); fc=s["first_crossing"]; v=r["vec"]
    same = fc["task"]["kind"]==v["task"]
    c[(v["spatial"]=="RESERVOIR", v["env_dynamics"] in ("SHIFT","PER_NICHE"), "crossed_on_configured_task" if same else "crossed_on_"+fc["task"]["kind"])]+=1
    if same and v["task"] in ("COND_ONE","COND_MULTI","SUM2") and v["representation"]!="BYTECODE32":
        a=acc(bytes.fromhex(fc["tape"]),v["task"],fc["task"]["k"],v["read_gate"])
        exact["isolated_atomic_acc>=0.99" if a>=0.99 else ("0.4-0.99" if a>=0.4 else "<0.4")]+=1
        bytask[(v["task"],v["scoring"],"acc>=0.99" if a>=0.99 else "partial")]+=1
for k,v in sorted(c.items(),key=lambda kv:-kv[1]): print(" reservoir=%s shift/per_niche=%s %s: %d"%(k[0],k[1],k[2],v))
print("crossing tapes on configured hard task, isolated exact accuracy over 256 inputs:",dict(exact))
for k,v in sorted(bytask.items()): print("  ",k,v)
