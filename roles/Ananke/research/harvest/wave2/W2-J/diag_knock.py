"""Diagnostic knock-outs: which physics dial kills a plant at a row? Sets one dial to its benign value at a
time (DIAGNOSTIC physics, not C1 rows). 16 DEV worlds. usage: python diag_knock.py cell8 fam 'opts-json'"""
import sys, time
from wj_common import *
import plants_wj as pw
from screen2 import build
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics
t0 = time.process_time()
c8, fam, opts = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
r = [x for x in xor_evolve() if x["cell_id"].startswith(c8)][0]
ph0 = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
seeds = assays.world_seeds(WJ_DEV, 16)
knocks = {"none": {}, "jitter0": dict(lat_jitter=0), "dup0": dict(dup=0.0), "mut0": dict(mut_site=0.0),
          "cap0": dict(cap=0), "noise0": dict(noise=0), "loss0": dict(loss=0.0), "eco0": dict(e_income=0, c_emit=0, c_op=0, c_mem=0),
          "sync": dict(update_mode="sync", update_period=1), "decay0": dict(decay_shift=0)}
only = sys.argv[4].split(",") if len(sys.argv) > 4 else list(knocks)
out = {}
for name in only:
    ph1 = ph0.replace(**knocks[name])
    lines, ev, f2 = build(ph1, env, fam, opts)
    ph, ov = pw.fit(ph1, lines, ev, f2, strict=False)
    e = hc.evaluate(ph, pw.genome(ph, lines), env, seeds)
    out[name] = round(e["acc"], 3)
    print(c8, name, out[name], flush=True)
out["cpu_s"] = time.process_time() - t0
save(f"diag_knock_{c8}_{fam}.json", out)
print(out["cpu_s"])
