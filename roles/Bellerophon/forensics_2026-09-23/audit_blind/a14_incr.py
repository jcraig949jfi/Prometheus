"""REACHED_INCREMENTAL_NOT_ATOMIC: are the INCREMENTAL 'solvers' exact solvers at all?"""
import json, os, sys, collections, random
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import vm
from prometheus.z80atlas.tasks import Task, score
W = r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs = [json.loads(l) for l in open(os.path.join(W, "runs.jsonl"), encoding="utf-8")]
byf = collections.defaultdict(list)
for r in runs: byf[r["family"]].append(r)
flags = [f for f in json.load(open(os.path.join(W, "flags.json"))) if f["flag"] == "REACHED_INCREMENTAL_NOT_ATOMIC"]
rng = random.Random(0)
def evals(tape, L, task, vec, rep=64):
    inc = ex = 0
    for _ in range(rep):
        inp = task.inputs(rng); mem = bytearray(256); mem[:L] = tape[:L]
        for i, v in enumerate(inp): mem[vm.IN_BASE + i] = v
        tr = vm.execute(mem, L, 0, 256, inp, allow_copyall=vec["representation"] == "VM_COPY")
        inc += score(task, tr.outputs, task.expected(inp), "INCREMENTAL", vec["read_gate"], tr.first_out_step, tr.first_in_step)
        ex += score(task, tr.outputs, task.expected(inp), "ATOMIC", vec["read_gate"], tr.first_out_step, tr.first_in_step)
    return inc / rep, ex / rep
c = collections.Counter(); nr = 0; per_run = collections.Counter()
for f in flags:
    rs = [r for r in byf[f["family"]] if (r["summary"].get("solvers_tail") or 0) >= 1 and r["kind"] != "intervention"]
    if not rs: continue
    r = rs[0]; v = r["vec"]
    if v["layout"] != "SHARED" or v["spatial"] == "RESERVOIR" or v["env_dynamics"] in ("SHIFT", "PER_NICHE", "ENV_REPRO"): continue
    L = 32 if v["representation"] == "BYTECODE32" else 64
    fin = [json.loads(l) for l in open(os.path.join(r["dir"], "snapshots.jsonl"))][-1]
    tk = fin["env"][0]; task = Task(tk["kind"], k=tk["k"]); nr += 1; best_exact = 0
    for h, n in fin["tapes"]:
        inc, ex = evals(bytes.fromhex(h), L, task, v)
        if inc >= 0.85:
            c["incremental solver, exact accuracy >= 0.99"] += n if ex >= 0.99 else 0
            c["incremental solver, exact accuracy < 0.99"] += n if ex < 0.99 else 0
            c["incremental solver, exact accuracy < 0.10"] += n if ex < 0.10 else 0
            best_exact = max(best_exact, ex)
    per_run["run's best incremental-solver exact acc >= 0.99" if best_exact >= 0.99 else "run has NO exact solver among its top tapes"] += 1
print("flagged runs examined:", nr)
for k, v in c.items(): print(" ", k, v)
for k, v in per_run.items(): print(" ", k, v)
