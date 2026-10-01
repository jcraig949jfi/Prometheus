"""DEV (16 worlds) plant vs NOR-cheat on the UNDECIDED rows' best variants. usage: python dev_cheat.py 'json list' tag"""
import sys, time
from wj_common import *
import plants_wj as pw
from screen2 import build
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics
t0 = time.process_time()
todo = json.loads(sys.argv[1]); tag = sys.argv[2]
seeds = assays.world_seeds(WJ_DEV, 16)
rows = {r["cell_id"][:8]: r for r in xor_evolve()}
out = []
for c8, fam, o in todo:
    r = rows[c8]; ph0 = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    rec = {"cell": r["cell_id"], "fam": fam, "opts": o}
    for ro in ("xor", "nor"):
        lines, ev, f2 = build(ph0, env, fam, o, readout=ro)
        ph, ov = pw.fit(ph0, lines, ev, f2, strict=False)
        e = hc.evaluate(ph, pw.genome(ph, lines), env, seeds)
        rec[ro] = {"acc": e["acc"], "lo99": e["lo99"]}
    out.append(rec)
    print(c8, fam, o, "xor %.3f nor %.3f" % (rec["xor"]["acc"], rec["nor"]["acc"]), flush=True)
save(f"dev_cheat_{tag}.json", {"rows": out, "cpu_s": time.process_time() - t0})
print("cpu_s", time.process_time() - t0)
