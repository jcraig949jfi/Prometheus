import json, collections, sys
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import vm
W=r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs=[json.loads(l) for l in open(W+r"\runs.jsonl",encoding="utf-8")]
sp=[r for r in runs if r["triggers"].get("spontaneous_replication") and r["kind"]!="intervention"]
def period(t):
    for d in (1,2,4,8,16,32):
        if all(t[i]==t[i%d] for i in range(len(t))): return d
    return None
c=collections.Counter(); c2=collections.Counter()
for r in sp:
    s=json.load(open(r["dir"]+r"\summary.json")); L=32 if r["vec"]["representation"]=="BYTECODE32" else 64
    fr=bytes.fromhex(s["first_replication"]["tape"])[:L]
    c[(r["vec"]["reproduction"], "period=%s"%period(fr))]+=1
    if s["top"]:
        c2[(r["vec"]["reproduction"], "period=%s"%period(bytes.fromhex(s["top"][0]["tape"])[:L]))]+=1
print("first replicator tape periodicity (proper period dividing L):")
for k,v in sorted(c.items()): print("  ",k,v)
print("top specimen periodicity:")
for k,v in sorted(c2.items()): print("  ",k,v)
