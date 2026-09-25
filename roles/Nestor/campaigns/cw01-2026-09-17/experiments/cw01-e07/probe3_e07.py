"""Probe G: which single search-regime feature, if any, makes state use evolvable?

Probe F showed diagonal recurrence changes nothing: the fitness trajectory's swings are
theta-draw noise (the zero-output floor moves with |theta|), and state dependence of the
best organisms stays ~0.005 at 40 generations and ~0.06 at 120 under both recurrences.
The search is simply too slow to climb from a 0.1-scale random genome to the accumulator
ridge, which needs coordinated moves of a_i up and B down.

Three single-feature candidates, production recurrence (full) kept, everything else
unchanged, 40 generations (the pilot budget), two lineages each:
  G1  mut_sigma        0.05 -> 0.20
  G2  init_sigma       0.10 -> 0.50
  G3  lifetimes/eval   2    -> 8
Plus the baseline for reference. This is measurement to CHOOSE the one correction; no
gate is run here and no threshold is touched.
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
sys.path.insert(0, str(HERE))
import world_e07 as W          # noqa: E402
from probe2_e07 import variant_run   # noqa: E402


def main():
    t0 = time.time()
    base = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    aid = base["attempt_id"]
    Q = W.attempt_Q(base, aid, "gate")
    variants = {
        "G0_baseline": {},
        "G1_mut_sigma_0.20": {"mut_sigma": 0.20},
        "G2_init_sigma_0.50": {"init_sigma": 0.50},
        "G3_lifetimes_8": {"lifetimes_per_eval": 8},
    }
    rep = {}
    for name, over in variants.items():
        cfg = copy.deepcopy(base)
        cfg["evolution"].update(over)
        print("\n-- %s --" % name)
        rep[name] = [variant_run(cfg, aid, Q, 40, j, "%s-%d" % (name, j)) for j in range(2)]
    summary = {}
    for name, runs in rep.items():
        summary[name] = {"I_top16_mean": [round(float(np.mean(r["top16_I"])), 3) for r in runs],
                         "dep_top16_mean": [round(float(np.mean(r["top16_dep"])), 3) for r in runs],
                         "AURC_k3_min": [round(float(np.nanmin(r["AURC_k3"])), 3) for r in runs],
                         "P4_k3": [(r["P4_k3"]["outcome"], round(r["P4_k3"]["ratio"], 2)
                                    if np.isfinite(r["P4_k3"]["ratio"]) else None) for r in runs]}
    print("\n== summary ==")
    for k, v in summary.items():
        print("   %-20s %s" % (k, v))
    (HERE / "PROBE3_E07.json").write_text(json.dumps({"runs": rep, "summary": summary,
                                                      "_elapsed_s": round(time.time() - t0, 1)},
                                                     indent=1, ensure_ascii=True, default=str),
                                          encoding="utf-8")
    print("PROBE3_E07.json written (%.1f s)" % (time.time() - t0))


if __name__ == "__main__":
    main()
