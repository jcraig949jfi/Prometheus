"""Step 1: reproduce Artemis's CVT-R per-side scores for all side-1-certified genomes and a side-0 comparison
set, through Artemis's adapter unchanged. Also: hash check of worktree code vs ADAPTER_CHECK, and identity of
the traced VM with the dense VM on the base lineages."""
import json, hashlib, time, random
from _env import A, ART, NES, ROWS, traced_dense, FRESH
import p11

out = {}
chk = json.loads((ART / "results" / "ADAPTER_CHECK.json").read_text())["files"]
hok = {}
for k, v in chk.items():
    p = (ART / k.replace("foreign/", "../../../../", 1)).resolve() if k.startswith("foreign") else ART / k
    hok[k] = hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == v
out["hash_match_LF"] = hok

side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
s0 = [r for r in ROWS if r["P11"]["certified_sides"] == [0]]
s0_fail = [r for r in s0 if not r["CVTR_accept"]]
s0_pass = [r for r in s0 if r["CVTR_accept"] and r["vm"] == "DENSE"][:8]
sel = side1 + s0_fail + s0_pass
t0 = time.time()
rep = []
for r in sel:
    G = bytes.fromhex(r["hex"])
    cv = A.cvt_genome(r["vm"], r["cell"], G, r["hex"])
    same = all(cv[s] == r["CVT"][str(s)] for s in (0, 1))
    rep.append({"key": r["key"], "cell": r["cell"], "vm": r["vm"], "p11_sides": r["P11"]["certified_sides"],
                "p11_s0": r["P11"]["rate_side0"], "p11_s1": r["P11"]["rate_side1"],
                "identical_to_record": same,
                "cvt": {s: [cv[s][c]["n"] for c in ("CVT1", "CVT2", "CVTR")] for s in (0, 1)}})
out["reproduce"] = rep
out["all_identical"] = all(x["identical_to_record"] for x in rep)

# traced VM == dense VM on the side-1 base step
T = traced_dense()
dz = A.vm_module("DENSE")
mism = 0; tot = 0
for r in side1:
    G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); n = P["n"]
    for k in range(3):
        from common import shabytes
        vb = shabytes("VICTIM", r["hex"], 1, k, n=n)
        a = p11.interact(dz, n=n, tape_len=P["tape_len"], ga=vb, gb=G, st_a=FRESH, st_b=FRESH, budget=P["budget"],
                         ops_mask=P["mask"], cmr=0.0, rng=random.Random(0))
        T._TR = []; T._LD = []
        b = p11.interact(T, n=n, tape_len=P["tape_len"], ga=vb, gb=G, st_a=FRESH, st_b=FRESH, budget=P["budget"],
                         ops_mask=P["mask"], cmr=0.0, rng=random.Random(0))
        T._TR = None; T._LD = None
        tot += 1; mism += (a[0] != b[0] or a[1] != b[1])
out["traced_vm_identity"] = {"interactions": tot, "mismatches": mism}
out["seconds"] = round(time.time() - t0, 1)
(pathlib := __import__("pathlib")).Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
print(out["all_identical"], all(hok.values()), out["traced_vm_identity"], out["seconds"])
for x in rep: print(x)
