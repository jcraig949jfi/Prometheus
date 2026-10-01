"""Record-only demonstrations (no Runner): C-A3-INTERNALIZE event degeneracy (D10), X-A3-FAIR donor-profile truncation
(D11), W1 L2 screen multiplicity (D12), and the anticheat guards that cannot fire (D5)."""
from __future__ import annotations

import json
import math
import re

import _paths

# ---- D10: C-A3-INTERNALIZE event, as coded and under two stricter readings of the docstring's claim
CI = _paths.ARC3 / "c_a3_internalize" / "results"
rows = []
for p in sorted(CI.glob("*.json")):
    r = json.loads(p.read_text())
    d0n = bool(r["d0_free"]) and not any(r["d0_free"])
    last = next((c for c in reversed(r["checkpoints"]) if c["free"] > 0), None)
    if not d0n or last is None:
        continue
    fin = r["checkpoints"][-1]
    rows.append({"run": p.stem, "last_free_epoch": last["epoch"], "L_share_at_last_free": last["L_share"],
                 "free": last["free"], "free_in_L": last["free_in_L"], "final_epoch": fin["epoch"],
                 "final_free": fin["free"], "final_competent": fin["competent"], "final_L_share": fin["L_share"]})
ev = [x for x in rows if x["free_in_L"] >= 0.8 * x["free"] and x["L_share_at_last_free"] >= 0.5]
ev_final = [x for x in ev if x["final_free"] > 0 and x["final_L_share"] >= 0.5]
ev_major = [x for x in ev_final if x["final_free"] >= 0.5 * x["final_competent"]]
clause_redundant = all((x["free_in_L"] == x["free"]) == (x["L_share_at_last_free"] >= 0.5) for x in rows)
d10 = {"eligible_runs_D0_not_free_with_any_free": len(rows),
       "L_share_values_at_endpoint": sorted({x["L_share_at_last_free"] for x in rows}),
       "free_in_L_clause_equivalent_to_L_share_clause": clause_redundant,
       "events_as_coded": len(ev), "events_if_state_free_present_at_FINAL_checkpoint": len(ev_final),
       "events_if_state_free_is_majority_of_competent_at_final": len(ev_major),
       "event_rows": ev}

# ---- D11: X-A3-FAIR specialist share reads only the first 20 donor profiles (hex-sorted)
FAIR = _paths.ARC3 / "x_a3_fair" / "results"
trunc, flips = [], []
for w, ok_cls in (("ZERO", {"Z_ONLY"}), ("CONST5A", {"K_ONLY"})):
    for p in sorted(FAIR.glob("%s_*.json" % w)):
        r = json.loads(p.read_text())
        cp = next((c for c in r["checkpoints"] if c["donors"] > 0), None)
        if not cp or cp["donors"] <= 20:
            continue
        trunc.append(p.stem)
        rec = all(("Z" in v and "K" not in v) if w == "ZERO" else ("K" in v and "Z" not in v)
                  for v in cp["donor_profiles"].values())
        full = sum(n for k, n in cp["classes"].items() if k not in ok_cls) == 0
        if rec != full:
            flips.append({"run": p.stem, "recorded_specialist": rec, "full_set_specialist": full,
                          "classes": cp["classes"]})
d11 = {"first_donor_checkpoints_truncated": len(trunc), "specialist_flag_flipped_by_truncation": flips}

# ---- D12: probability a genome of per-seed pass rate p is labelled COMPETENT by run_dd.screen, per screening


def binom_ge(n, k, p):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


d12 = {"P_competent_per_screen": {str(p): round((1 - (1 - p) ** 4) * binom_ge(20, 10, p), 4)
                                  for p in (0.1, 0.2, 0.3, 0.4, 0.5)},
       "note": "stage 1 = any of 4 seeds (either side) passes; stage 2 = >= 10 of 20. Seeds are keyed on the genome's index "
               "in the sorted checkpoint list (run_dd.screen tag (..., j, 1)), so each checkpoint re-draws."}
borderline = 0
for p in sorted((_paths.W1 / "x_dd_dense_copy" / "results").glob("DENSE_COPY_*.json")):
    r = json.loads(p.read_text())
    rates = [g["rate"] for c in r["checkpoints"] for g in c["competent_genomes"]]
    if rates and max(rates) < 0.6:
        borderline += 1
d12["DENSE_COPY_L2_runs_whose_best_competent_rate_is_below_0.6"] = borderline

# ---- D5: anticheat counters that are declared but never written
src = (_paths.C9 / "world.py").read_text()
written = {k: bool(re.search(r'ct\["%s"\]\s*\+=' % k, src)) for k in
           ("validation_writes", "validation_world_ops", "nonheritable_state_inherited", "births_external")}
d5 = {"counter_ever_incremented_in_world.py": written,
      "IMMORTAL_cap": "max_age = epochs + 2; age is incremented once per step and there are `epochs` steps, so age <= epochs",
      "RUNNER_BIRTH": "births_external is incremented only in _external_births, which step() calls only when "
                      "reproduction == EXTERNAL; EXTERNAL is not in grammar.ENDOGENOUS, so `endogenous and births_external>0` "
                      "is unsatisfiable"}
_paths.dump("d6_records.json", {"D10_ci_event": d10, "D11_fair_truncation": d11, "D12_screen": d12, "D5_anticheat": d5})
