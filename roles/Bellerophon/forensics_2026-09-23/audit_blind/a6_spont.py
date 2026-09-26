import json, collections, sys
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import vm
W=r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs=[json.loads(l) for l in open(W+r"\runs.jsonl",encoding="utf-8")]
sp=[r for r in runs if r["triggers"].get("spontaneous_replication")]
iv=[r for r in sp if r["kind"]=="intervention"]
print("intervention spontaneous runs",len(iv),"seed_lineage_share values:",sorted(round(r["summary"]["seed_lineage_share"],2) for r in iv))
c=collections.Counter(); ex=[]
for r in sp:
    if r["kind"]=="intervention": continue
    s=json.load(open(r["dir"]+r"\summary.json")); fr=s["first_replication"]; ph=r["vec"]["reproduction"]
    L=32 if r["vec"]["representation"]=="BYTECODE32" else 64
    for label,tape in (("first_rep",bytes.fromhex(fr["tape"])),("top",bytes.fromhex(s["top"][0]["tape"]) if s["top"] else None)):
        if tape is None: continue
        mem=bytearray(256); mem[:L]=tape; tr=vm.execute(mem,L,0,256,[5],allow_copyall=r["vec"]["representation"]=="VM_COPY")
        nw=len(tr.writes); ldir=tr.opcodes.get(vm.LDIR,0)
        kind = "wrap-LDIR(>=200 addrs written)" if nw>=200 else ("writes window>=L" if sum(1 for a in tr.writes if L<=a<2*L)>=L else "other")
        c[(ph,label,kind, "io_corrupt" if tr.io_corrupt else "")]+=1
        if label=="top" and len(ex)<3 and ph=="ENDOGENOUS_COPY": ex.append((r["id"],vm.disassemble(tape,16)))
for k,v in sorted(c.items(), key=lambda kv:(kv[0][0],kv[0][1],-kv[1])): print(" ",k,v)
for e in ex: print(e)
