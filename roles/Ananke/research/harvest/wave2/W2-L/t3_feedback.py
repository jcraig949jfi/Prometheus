"""Addendum: W2-B's FLIP_FEEDBACK ruler (imported read-only from W2-B/rulers_c1.py) on given genomes at given rows.
usage: python t3_feedback.py <cell> <genome-name> [<genome-name> ...]   genome names: pflip, refresh, thin, relay"""
from w2l_common import *
sys.path.insert(0, str(HERE.parent / "W2-B"))
import rulers_c1                     # noqa  (read-only use)
import hp_variants as hv
cid = sys.argv[1]
r = hc.row(cid); ph, env = cell(r)
ck = Clock()
s = held_seeds(r)
out = {"cell": cid, "res": {}}
for name in sys.argv[2:]:
    if name == "relay":
        p2 = ph if ph.prog_len >= 12 else ph.replace(prog_len=12).validate()
        g = plants.plant("relay_flood", p2)
    else:
        v = {"pflip": "base"}.get(name, name)
        need = hv.NEED_L[v]
        p2 = ph if (ph.prog_len >= need and ph.state_dim >= 2) else ph.replace(prog_len=max(need, ph.prog_len), state_dim=max(2, ph.state_dim)).validate()
        g = hv.plant(v, p2)
    res = rulers_c1.m_flip_feedback()(p2, env, g, s)
    # also the ablated accuracy itself
    Pd = env.period()
    def abl(ep): ep.schedule.sense_val[Pd:, :, 1] = 0
    a = hc.evaluate(p2, g, env, s, sched_fn=abl)
    out["res"][name] = {"override_prog_len": None if p2 is ph else p2.prog_len, "ff_diff_lo99": res["value"],
                        "FLIP_FEEDBACK_pass": res["passed"], "acc_teachers_removed": a["acc"],
                        "acc_teachers_removed_ci": [a["lo99"], a["hi99"]]}
    print(cid, name, out["res"][name], flush=True)
out["compute"] = ck.done(); print(out["compute"])
save(f"t3_feedback_{cid[:8]}_{'_'.join(sys.argv[2:])}.json", out)
