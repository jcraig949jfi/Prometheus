"""Energy-economy check: at fded1681 / 070257d7 (e_income 4, e_max 100, c_emit 4 x fanout 8, c_op 1, c_mem 1)
INT_1 starves sensors of emission energy. Score the 3-line INT_LEAK (in genome space) on held + DICT."""
import w2m_common as c, w2m_plants as wp
from prometheus.ananke import envs
from prometheus.ananke.physics import Physics
R = {r["cell_id"][:8]: r for r in c.maj_rows()}
ck = c.Clock(); out = []
import sys
CIDS = sys.argv[1:] or ["fded1681", "070257d7"]
for cid in CIDS:
    r = R[cid]; ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"]); held = c.held_seeds(r)
    g = wp.int_leak(ph)
    e = c.hc.evaluate(ph, g, env, held); ed = c.hc.evaluate(ph, g, env, held, sched_fn=wp.dict_sched)
    out.append({"cell": r["cell_id"], "acc": e["acc"], "lo99": e["lo99"], "DICT": ed["acc"], "stats": e["stats"]})
    print(cid, "INT_LEAK %.3f lo %.3f DICT %.3f" % (e["acc"], e["lo99"], ed["acc"]), "emitters", e["stats"]["emitters"], flush=True)
c.save("econ_check_" + "_".join(CIDS) + ".json", {"rows": out, "compute": ck.done()}); print(ck.done())
