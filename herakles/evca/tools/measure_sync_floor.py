"""Floor and range of `cellwise_synchronisation_match` (C-3 row, 2026-09-16).

Geometry is MAJ_STRUCTURAL_ZERO.md s3's, so the two per-cell criteria are
measured on the same footing: N = 149, 100 ICs (seed 20260910, unbiased
ensemble), 298 steps, 20 random tables (seeds 1000..1019). Also the two
constants, the blinker, the six recovered genomes and the eleven catalogue
organisms where genomes.py holds them, so the row can say what every held
organism scores. Writes one JSON beside CRITERIA.md; every number in the
CRITERIA row is read from that file.

    python -m herakles.evca.tools.measure_sync_floor

Refuses the canonical checkout (herakles/workspace.py).
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",
                                    ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from herakles import workspace                       # noqa: E402
from herakles import evca                            # noqa: E402
from herakles.evca import genomes as G               # noqa: E402

OUT = os.path.join(REPO, "herakles", "evca", "sync_floor_2026-09-16.json")
N, N_ICS, STEPS, SEED = 149, 100, 298, 20260910
RANDOM_SEEDS = list(range(1000, 1020))


def main() -> int:
    workspace.assert_not_canonical()
    ics = evca.make_ics(N_ICS, N, SEED)
    rows = []

    def row(label, table, kind):
        r = evca.cellwise_synchronisation_match(table, ics, STEPS)
        s = evca.synchronisation_score(table, ics, STEPS)
        rec = {"label": label, "kind": kind,
               "mean_sync_match": r["mean_sync_match"],
               "sd_across_ics": r["sd_across_ics"],
               "mean_flip_fraction": r["mean_flip_fraction"],
               "mean_phase_match": r["mean_phase_match"],
               "fraction_all_cells_sync": r["fraction_all_cells_sync"],
               "synchronisation_score": s["score"],
               "identity_holds": r["fraction_all_cells_sync"] == s["score"]}
        rows.append(rec)
        print("%-22s %-9s mean %.4f sd %.4f flip %.4f phase %.4f all %.3f"
              % (label, kind, rec["mean_sync_match"], rec["sd_across_ics"],
                 rec["mean_flip_fraction"], rec["mean_phase_match"],
                 rec["fraction_all_cells_sync"]))
        return rec

    for s in RANDOM_SEEDS:
        row("random_%d" % s, evca.random_table(s), "random")
    row("const_0", np.zeros(evca.TABLE_BITS, np.uint8), "constant")
    row("const_1", np.ones(evca.TABLE_BITS, np.uint8), "constant")
    row("blinker", evca.blinker_rule_table(), "control")
    for name in G.NAMES:
        row(name, evca.decode_table(G.rule_hex(name)), "genome")

    rand = [r["mean_sync_match"] for r in rows if r["kind"] == "random"]
    flips = [r["mean_flip_fraction"] for r in rows if r["kind"] == "random"]
    phase = [r["mean_phase_match"] for r in rows if r["kind"] == "random"]
    # the expected majority share of a Binomial(N, 1/2) draw, exact
    share = sum(math.comb(N, k) * max(k, N - k) / N for k in range(N + 1)) \
        / 2 ** N
    summary = {
        "geometry": {"n_cells": N, "n_ics": N_ICS, "steps": STEPS,
                     "ic_seed": SEED, "random_table_seeds": RANDOM_SEEDS},
        "random_tables": {
            "n": len(rand),
            "mean_of_means": float(np.mean(rand)),
            "min": float(min(rand)), "max": float(max(rand)),
            "sd_of_means": float(np.std(rand, ddof=1)),
            "mean_flip_fraction": float(np.mean(flips)),
            "mean_phase_match": float(np.mean(phase)),
        },
        "analytic": {
            "expected_majority_share_N149": share,
            "expected_if_flip_and_phase_independent_at_flip_half":
                0.5 * share,
            "stated_before_measurement": "about 0.27; not 0 and not 0.5",
        },
        "rows": rows,
    }
    with open(OUT, "w", encoding="ascii") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("random tables: mean %.4f  [%.4f, %.4f]  sd of means %.4f"
          % (summary["random_tables"]["mean_of_means"],
             summary["random_tables"]["min"], summary["random_tables"]["max"],
             summary["random_tables"]["sd_of_means"]))
    print("analytic majority share %.4f; 0.5 x share %.4f"
          % (share, 0.5 * share))
    print("wrote", os.path.relpath(OUT, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
