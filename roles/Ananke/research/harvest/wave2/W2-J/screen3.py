"""DEV screen of explicit (row, family, opts) variants. usage: python screen3.py 'json list of [cell8, fam, opts]' tag"""
import sys, time
from wj_common import *
import plants_wj as pw
from screen2 import build
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics
t0 = time.process_time()
todo = json.loads(sys.argv[1]); tag = sys.argv[2]
seeds = assays.world_seeds(WJ_DEV, 16)
res = []
rows = {r["cell_id"][:8]: r for r in xor_evolve()}
for c8, fam, o in todo:
    r = rows[c8]
    ph0 = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    lines, ev, f2 = build(ph0, env, fam, o)
    ph, ov = pw.fit(ph0, lines, ev, f2, strict=False)
    e = hc.evaluate(ph, pw.genome(ph, lines), env, seeds)
    st = e["stats"]
    res.append({"cell": r["cell_id"], "fam": fam, "opts": o, "len": len(lines), "override": ov, "acc": e["acc"], "stats": st})
    print(c8, fam, o, "len", len(lines), "acc %.3f" % e["acc"], "emit/aw %.3f coll %d" % (st["emitters"] / max(1, st["awake"]), st["collided"]), flush=True)
save(f"screen3_{tag}.json", {"rows": res, "cpu_s": time.process_time() - t0})
print("cpu_s", time.process_time() - t0)
