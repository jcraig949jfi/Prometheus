"""S-M3: SETRULE configuration vs memory (plan 8e081dcb1)."""
import json
import pathlib
import sys
import time

import numpy as np
import torch

REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from prometheus.ananke import assays, c1b, c1b_run, lens  # noqa: E402

OUT = pathlib.Path(__file__).parent / "out"
DEV = "cuda"
SEEDS = assays.world_seeds(0x5E1, 64)
t0 = time.time()


def spike(cid):
    ph, env, g, _ = c1b_run.load(cid)
    Pd = env.period()
    tk = c1b.ticks(env)
    pre = [t0_ + max(1, env.delta // 2) for t0_ in tk["t0"]]      # mid-delta, before transport lands
    trials = range(env.trials)
    out = {"physics": {k: getattr(ph, k) for k in ("rules", "setrule", "wimm", "dest_mode",
                                                   "update_mode", "update_p", "lat_base")}}
    prev = {}

    def rcen(w, t):
        r = w.r
        p = lens.partner_index(w.B, w.dev)
        diff = (r != r[p]).float().mean().item()
        ch = 0.0 if "r" not in prev else (r != prev["r"]).float().mean().item()
        prev["r"] = r.clone()
        hist = torch.bincount(r.flatten(), minlength=ph.rules).tolist()
        return (diff, ch, hist)
    base = lens.run(ph, g, env, SEEDS, recorders={"r": rcen}, device=DEV)
    nrm = lens.trial_acc(base, trials)
    rc = base.rec["r"]
    out["normal"] = lens.ci(nrm)
    out["E1_partner_r_diff_frac"] = {"mean": float(np.mean([x[0] for x in rc])),
                                    "max": float(np.max([x[0] for x in rc])),
                                    "by_trial_mean": [float(np.mean([x[0] for x in rc[k * Pd:(k + 1) * Pd]]))
                                                      for k in range(env.trials)]}
    out["E1_r_change_frac"] = {"first_trial": float(np.mean([x[1] for x in rc[1:Pd]])),
                               "later": float(np.mean([x[1] for x in rc[Pd:]])),
                               "by_trial": [float(np.mean([x[1] for x in rc[k * Pd:(k + 1) * Pd]]))
                                            for k in range(env.trials)]}
    out["E1_rule_hist_first_last"] = [rc[0][2], rc[-1][2]]
    # E2 configure-then-freeze: freeze_rule from the start of trial 2
    def freeze(w):
        w.ctrl.freeze_rule = True
    r2 = lens.run(ph, g, env, SEEDS, hooks={2 * Pd - 1: freeze}, device=DEV)
    later = range(2, env.trials)
    out["E2_freeze_after_2_trials"] = {"normal_later": lens.ci(lens.trial_acc(base, later)),
                                       "frozen_later": lens.ci(lens.trial_acc(r2, later))}
    rf = lens.run(ph, g, env, SEEDS, ctrl=None, hooks={0: freeze}, device=DEV)
    out["E2b_freeze_from_tick1"] = lens.ci(lens.trial_acc(rf, trials))
    # E3 swap r at mid-delta; E4 reset r to r0 at mid-delta
    r3 = lens.run(ph, g, env, SEEDS, hooks={t: (lambda w: lens.swap(w, ["r"])) for t in pre}, device=DEV)
    p3 = lens.trial_acc(r3, trials)
    out["E3_swap_r_mid"] = {"acc": lens.ci(p3), "verdict": lens.swap_verdict(nrm, p3)}
    r4 = lens.run(ph, g, env, SEEDS, hooks={t: lens.reset_r for t in pre}, device=DEV)
    out["E4_reset_r_mid"] = lens.ci(lens.trial_acc(r4, trials))
    # carrier swaps for completeness (as M2)
    for an, fn in {"swap_inflight": lambda w: lens.swap(w, lens.FLIGHT_ARRAYS),
                   "swap_sitestate_no_r": lambda w: lens.swap(w, [a for a in lens.SITE_ARRAYS if a != "r"])}.items():
        rr = lens.run(ph, g, env, SEEDS, hooks={t: fn for t in pre}, device=DEV)
        pp = lens.trial_acc(rr, trials)
        out["swap_" + an] = {"acc": lens.ci(pp), "verdict": lens.swap_verdict(nrm, pp)}
    # E5 emissions under freeze_rule
    from prometheus.ananke.engine import Controls
    rz = lens.run(ph, g, env, SEEDS, ctrl=Controls(freeze_rule=True), device=DEV)
    out["E5_emitters_per_world"] = {"normal": float(base.stats["emitters"].mean()),
                                    "freeze_rule": float(rz.stats["emitters"].mean()),
                                    "attempted_normal": float(base.stats["attempted"].mean()),
                                    "attempted_freeze": float(rz.stats["attempted"].mean())}
    out["E5_freeze_rule_acc"] = lens.ci(lens.trial_acc(rz, trials))
    return out


if __name__ == "__main__":
    res = {cid[:8]: spike(cid) for cid in c1b.SPECIMENS["M3"]}
    res["_wall_s"] = time.time() - t0
    (OUT / "s_m3.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=lambda x: round(float(x), 3))[:6000])
