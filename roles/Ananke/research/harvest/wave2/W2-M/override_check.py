"""Is prog_len the binding constraint at the ring64 r3 sample-fanout-8 prog_len-8 cells? INT_1 / INT_1A6 with a
prog_len override (flagged: OUTSIDE the cell genome space), on held worlds. Small (4 cells x 2 members)."""
import json
import w2m_common as c, w2m_plants as wp
from prometheus.ananke import envs
from prometheus.ananke.engine import Controls
from prometheus.ananke.physics import Physics
R = {r["cell_id"][:8]: r for r in c.maj_rows()}
ck = c.Clock(); out = []
for cid in ("fded1681", "626aa72f", "070257d7", "13a086e9"):
    r = R[cid]; ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); held = c.held_seeds(r)
    for name, kw in (("INT_1", dict(lanes=1)), ("INT_1A6", dict(lanes=1, reset="age", k=6))):
        ph2, g, ok, n = wp.member(ph, **kw)
        e = c.hc.evaluate(ph2, g, env, held)
        ed = c.hc.evaluate(ph2, g, env, held, sched_fn=wp.dict_sched)
        out.append({"cell": r["cell_id"], "member": name, "in_space": ok, "prog_len_used": ph2.prog_len,
                    "acc": e["acc"], "lo99": e["lo99"], "DICT": ed["acc"]})
        print(cid, name, ok, ph2.prog_len, "%.3f lo %.3f DICT %.3f" % (e["acc"], e["lo99"], ed["acc"]), flush=True)
c.save("override_check.json", {"rows": out, "compute": ck.done()}); print(ck.done())
