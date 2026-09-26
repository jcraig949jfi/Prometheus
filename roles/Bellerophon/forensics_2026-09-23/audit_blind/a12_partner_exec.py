"""In solved runs behind REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL, how much of the final population's solving is done
by code the organism does not own (PC runs off its own tape into the partner window)?"""
import json, os, sys, collections, random
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import vm
from prometheus.z80atlas.tasks import Task, score
W = r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs = [json.loads(l) for l in open(os.path.join(W, "runs.jsonl"), encoding="utf-8")]
byf = collections.defaultdict(list)
for r in runs: byf[r["family"]].append(r)
flags = [f for f in json.load(open(os.path.join(W, "flags.json"))) if f["flag"] == "REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL"]
rng = random.Random(0)
def acc(tape, partner, L, task, vec, rep=48):
    ok = 0; pcs = 0
    for _ in range(rep):
        inp = task.inputs(rng); mem = bytearray(256); mem[:L] = tape[:L]
        if partner is not None: mem[L:2 * L] = partner[:L]
        for i, v in enumerate(inp): mem[vm.IN_BASE + i] = v
        tr = vm.execute(mem, L, 0, 256, inp, allow_copyall=vec["representation"] == "VM_COPY")
        sc = score(task, tr.outputs, task.expected(inp), vec["scoring"], vec["read_gate"], tr.first_out_step, tr.first_in_step)
        ok += sc >= 0.999 if vec["scoring"] == "ATOMIC" else sc; pcs += tr.pc_max >= L
    return ok / rep, pcs / rep
c = collections.Counter(); nruns = 0
for f in flags:
    solved = [r for r in byf[f["family"]] if (r["summary"].get("solvers_tail") or 0) >= 1 and r["kind"] != "intervention"]
    if not solved: continue
    r = solved[0]; v = r["vec"]
    if v["layout"] != "SHARED" or v["env_dynamics"] != "FIXED" or v["spatial"] == "RESERVOIR": continue
    L = 32 if v["representation"] == "BYTECODE32" else 64
    snaps = [json.loads(l) for l in open(os.path.join(r["dir"], "snapshots.jsonl"))]
    fin = snaps[-1]; tk = fin["env"][0]; task = Task(tk["kind"], k=tk["k"])
    tapes = [(bytes.fromhex(h), n) for h, n in fin["tapes"]]
    if len(tapes) < 2: continue
    nruns += 1
    for t, n in tapes:
        a_iso, _ = acc(t, None, L, task, v)
        partners = [p for p, _ in tapes if p != t][:3]
        a_p = max(acc(t, p, L, task, v)[0] for p in partners)
        a_self, pc = acc(t, t, L, task, v)
        cls = "solves alone" if a_iso >= 0.85 else ("solves ONLY with a partner in the window" if max(a_p, a_self) >= 0.85 else "not a solver")
        c[cls] += n
        if cls != "not a solver": c["  of solver copies: PC left own tape (pc_max>=L) in %s" % ("most" if pc > 0.5 else "few") + " runs"] += n
print("runs examined:", nruns)
for k, v in c.items(): print(" ", k, v)
