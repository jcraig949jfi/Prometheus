"""Economy-conditional bound (analytic). engine.py step 5: an emission needs E >= c_emit*copies; every awake
tick costs c_op per non-NOP line; E += e_income per tick, clamped to [0, e_max]; once E is pinned at 0 it can
never reach the emission cost if p_awake*k*c_op > e_income. With c_mem charges ignored (m=0: optimistic),
emission is impossible after t_dep = (e_max - c_emit*copies) / (p_awake*k*c_op - e_income), so only the
ceil(t_dep/Pd) first trials can carry information: acc <= .5 + .5 * f_lc2 * n/12.
k* = smallest number of non-NOP lines for which this bound is < .60."""
import math
from wj_common import *
from prometheus.ananke.physics import Physics
from prometheus.ananke import envs
R = {o["cell"]: o for o in json.load(open(OUT / "lc_robust.json"))["rows"]}
out = []
for r in xor_evolve():
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    if ph.c_op == 0 or R[r["cell_id"]]["lc2"] < 0.6:
        continue
    pa = 1.0 / ph.update_period if ph.update_mode == "sync" else ph.update_p
    cost = ph.c_emit * ph.copies()
    f = 2 * (R[r["cell_id"]]["lc2"] - 0.5)
    Pd = env.period()
    res = {}
    kstar = None
    for k in range(1, 40):
        drain = pa * k * ph.c_op - ph.e_income
        if drain <= 0 or ph.e_max < cost:
            n = env.trials if ph.e_max >= cost else 0
        else:
            tdep = (ph.e_max - cost) / drain
            n = min(env.trials, max(0, math.ceil(tdep / Pd)))
        ub = 0.5 + 0.5 * f * n / env.trials
        res[k] = round(ub, 3)
        if kstar is None and ub < 0.60:
            kstar = k
    out.append({"cell": r["cell_id"], "p_awake": pa, "emit_cost": cost, "e_max": ph.e_max, "income": ph.e_income,
                "lc2": R[r["cell_id"]]["lc2"], "k_star": kstar, "ub_k16": res[16], "ub_k8": res[8], "ub_k4": res[4]})
    print(r["cell_id"][:8], out[-1])
save("econ_bound.json", out)
