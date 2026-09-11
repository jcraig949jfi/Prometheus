import json, random, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
REPO=Path("D:/Prometheus-worktrees/nemesis-adopt")
sys.path[:0]=[str(REPO), str(REPO/"agents/eos/src"), str(REPO/"roles/Nemesis/science")]
from archaeon.workspace import assert_not_canonical, receipt
import intake
from intake import Item, Claim, classify, PENDING, NOT_EXAMINED
from cheatlib import token_from_file, filler, absent_marker, shrink
assert_not_canonical()
rng=random.Random(20260911)
paths=[p for p in subprocess.run(["git","ls-files"],cwd=str(REPO),capture_output=True,text=True).stdout.splitlines()
       if p and not p.startswith(("agents/eos/","roles/Eos/")) and (REPO/p).is_file() and (REPO/p).stat().st_size>200]
def item(i):
    return Item(id="nemesis-refraud-%05d-%d"%(i,rng.randrange(10**8)),
        title="A Study of %s in %s Systems"%(filler(9,rng).strip(),filler(7,rng).strip()),
        source="nemesis-constructed", url="https://nemesis.invalid/refraud/%d"%i,
        abstract=filler(120,rng), fetched_at=datetime.now(timezone.utc).isoformat(),
        provenance="constructed by cheatlib")
RAT=("This item bears on the referenced location in the repository and the "
     "falsifier below states the result that would show otherwise.")
def popA(n):
    out=[];tries=0
    while len(out)<n and tries<n*20:
        tries+=1; rel=rng.choice(paths); tok=token_from_file(REPO/rel,rng,1)
        if tok is None: continue
        out.append((item(len(out)),Claim(sought="ANCHOR",rationale=RAT,
            referent="%s#%s"%(rel,tok),falsifier=filler(20,rng).replace(" ","x"),
            proposed_by="nemesis-cheatlib")))
    return out
def popB(n):
    return [(item(i),Claim(sought="ACQUIRE",rationale=RAT,capability_markers=[absent_marker(rng)],
        destination=rng.choice(paths),consumer=rng.choice(paths),proposed_by="nemesis-cheatlib")) for i in range(n)]
def popC_old(n):
    out=[]
    for i in range(n):
        w=datetime.now(timezone.utc)-timedelta(days=rng.randrange(0,25))
        out.append((item(i),Claim(sought="RESOURCE",rationale=RAT,observation={
            "endpoint":"https://nemesis-never-called.invalid/v1","observed_at":w.isoformat(),
            "status":200,"observed_by":intake.OBSERVER},proposed_by="nemesis-cheatlib")))
    return out
def run(tag,pop):
    st={}; crossed=0
    for it,c in pop:
        v=classify(it,c); st[v.state]=st.get(v.state,0)+1
        if v.state in (PENDING,"RESOURCE"): crossed+=1
    n=len(pop)
    print("%-10s n=%-4d crossed=%-4d rate=%.3f  %s"%(tag,n,crossed,crossed/n,st))
    return {"n":n,"crossed":crossed,"rate":crossed/n,"states":st}
res={"attack":"NEMESIS-01c re-attack on the REPAIRED gate","run_at":datetime.now(timezone.utc).isoformat(),
     "workspace":receipt(),"built_from":subprocess.run(["git","rev-parse","HEAD"],cwd=str(REPO),capture_output=True,text=True).stdout.strip(),
     "eligible_referent_files":len(paths),"populations":{}}
res["populations"]["A_anchor"]=run("POP-A",popA(200))
res["populations"]["B_acquire"]=run("POP-B",popB(8))
res["populations"]["C_resource_old_forgery"]=run("POP-C_old",popC_old(30))
# the 22-char fixpoint, replayed verbatim
def crosses(t):
    rel,tok,fals,rat=t
    return classify(item(1),Claim(sought="ANCHOR",rationale=rat,referent="%s#%s"%(rel,tok),
        falsifier=fals,proposed_by="nemesis-cheatlib")).state==PENDING
fx=(".gitignore","o",filler(20,rng).replace(" ","x"),"T")
res["twentytwo_char_fixpoint_still_crosses"]=crosses(fx)
print("22-char fixpoint still crosses:",res["twentytwo_char_fixpoint_still_crosses"])
out=REPO/"roles/Nemesis/attacks/2026-09-11_eos_gate_repaired/results_repaired.json"
out.write_text(json.dumps(res,indent=2),encoding="utf-8")
print("wrote",out)
