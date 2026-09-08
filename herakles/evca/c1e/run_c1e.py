"""WP-C1-e: the historical reproduction run. Implements PROTOCOL.md exactly.

Every constant here is copied from the protocol, which was committed before
this file existed. If a number here disagrees with the protocol, the protocol
wins and this file is wrong.

    python -m herakles.evca.c1e.run_c1e
"""
from __future__ import annotations

import io
import json
import math
import os
import time

from herakles import evca
from herakles.evca import genomes as G

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- protocol section 2 and 3, verbatim
LATTICES = [(149, 10000), (599, 4000), (999, 2000)]
BASE_SEED = 20260908
# protocol section 4: 18 cells, Bonferroni at family-wise 0.05
N_CELLS_COMPARED = 18
FAMILY_ALPHA = 0.05
PER_CELL_ALPHA = FAMILY_ALPHA / N_CELLS_COMPARED          # 0.002778
Z = 2.9912                                                # two-sided
# protocol section 5
SENSITIVITY_N = 149
SENSITIVITY_STEPS = [149, 298, 596, 1192]


def cell_seed(lattice_index: int, rule_index: int) -> int:
    return BASE_SEED + 1000 * lattice_index + rule_index


def run_cell(rule_name, n_cells, n_ics, steps, seed):
    table = evca.decode_table(G.rule_hex(rule_name))
    ics = evca.make_ics(n_ics, n_cells, seed)
    r = evca.classify(table, ics, steps, witness_limit=evca.WITNESS_LIMIT)
    p = r["accuracy"]
    se = math.sqrt(p * (1.0 - p) / n_ics)
    published = float(G.GENOMES[rule_name]["published_P"][n_cells])
    diff = p - published
    band = Z * se
    # protocol section 5: maj's published 0.000 gets the exact rule, because a
    # proportion test at p_hat = 0 has zero band width and would auto-fail.
    if published == 0.0:
        decision = "REPRODUCED" if r["n_correct"] == 0 else "EXACT_RULE_NONZERO"
        rule_applied = "exact (published is 0.000; zero-width band avoided)"
    else:
        decision = "REPRODUCED" if abs(diff) <= band else "DISCREPANT"
        rule_applied = "binomial, Bonferroni z = %.4f" % Z
    return {
        "rule": rule_name, "n_cells": n_cells, "n_ics": n_ics, "steps": steps,
        "seed": seed, "published": published, "measured": p,
        "n_correct": r["n_correct"], "n_incorrect": r["n_incorrect"],
        "diff": diff, "se": se, "band_half_width": band,
        "abs_diff_in_se": (abs(diff) / se) if se > 0 else None,
        "decision": decision, "decision_rule": rule_applied,
        "uniform_fixed_points": r["uniform_fixed_points"],
        "correct_mask_digest": r["correct_mask_digest"],
    }


def main():
    started = time.time()
    out = {"protocol": "herakles/evca/c1e/PROTOCOL.md",
           "z": Z, "per_cell_alpha": PER_CELL_ALPHA,
           "family_alpha": FAMILY_ALPHA, "cells_compared": N_CELLS_COMPARED,
           "primary": [], "sensitivity": []}

    print("PRIMARY RUN -- steps = 2N, per the protocol")
    print("%-10s %5s %6s %6s %9s %9s %8s %7s %6s  %s"
          % ("rule", "N", "n_ics", "steps", "published", "measured", "diff",
             "band", "se_x", "decision"))
    for li, (n_cells, n_ics) in enumerate(LATTICES):
        steps = 2 * n_cells
        for ri, name in enumerate(G.NAMES):
            row = run_cell(name, n_cells, n_ics, steps, cell_seed(li, ri))
            out["primary"].append(row)
            sx = ("%6.2f" % row["abs_diff_in_se"]) \
                if row["abs_diff_in_se"] is not None else "   n/a"
            print("%-10s %5d %6d %6d %9.3f %9.4f %+8.4f %7.4f %s  %s"
                  % (name, n_cells, n_ics, steps, row["published"],
                     row["measured"], row["diff"], row["band_half_width"],
                     sx, row["decision"]))

    print()
    print("SENSITIVITY -- N = %d, horizon sweep. CANNOT change any decision."
          % SENSITIVITY_N)
    print("%-10s %6s %9s %9s %+8s" % ("rule", "steps", "published",
                                      "measured", "diff"))
    for name in G.NAMES:
        for steps in SENSITIVITY_STEPS:
            table = evca.decode_table(G.rule_hex(name))
            ics = evca.make_ics(4000, SENSITIVITY_N, BASE_SEED + 777)
            r = evca.classify(table, ics, steps)
            pub = float(G.GENOMES[name]["published_P"][SENSITIVITY_N])
            row = {"rule": name, "n_cells": SENSITIVITY_N, "n_ics": 4000,
                   "steps": steps, "published": pub,
                   "measured": r["accuracy"], "diff": r["accuracy"] - pub}
            out["sensitivity"].append(row)
            print("%-10s %6d %9.3f %9.4f %+8.4f"
                  % (name, steps, pub, r["accuracy"], row["diff"]))

    out["elapsed_s"] = round(time.time() - started, 1)
    path = os.path.join(HERE, "c1e_results.json")
    io.open(path, "w", encoding="utf-8", newline="").write(
        json.dumps(out, indent=1, sort_keys=True) + "\n")
    print()
    print("wrote %s in %.1fs" % (path, out["elapsed_s"]))

    n_rep = sum(1 for r in out["primary"] if r["decision"] == "REPRODUCED")
    print("REPRODUCED %d of %d cells" % (n_rep, len(out["primary"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
