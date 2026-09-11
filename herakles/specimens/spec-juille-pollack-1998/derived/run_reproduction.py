"""Juille and Pollack 1998, Table 1 reproduction. Implements PROTOCOL.md Q3-Q5.

Conventions are C1-e's (assumption A1 of the protocol): ring, synchronous,
steps = 2N, ICs iid Bernoulli(0.5), at_T, n_ics 10000 / 4000 / 2000.
Decision rule: REPRODUCED iff |measured - published| <= z * SE, z = 2.935
(Bonferroni, 15 cells, family-wise 0.05). Seeds derive from 20260911.

    python herakles/specimens/spec-juille-pollack-1998/derived/run_reproduction.py
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
from herakles.workspace import assert_not_canonical      # noqa: E402
from herakles import evca                                # noqa: E402
from herakles.evca import genomes as G                    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = os.path.join(HERE, "juille_pollack_1998_rule_tables.json")
OUT = os.path.join(HERE, "reproduction_results.json")

LATTICES = [(149, 10000), (599, 4000), (999, 2000)]
BASE_SEED = 20260911
RULES = ("coev1", "coev2", "das", "abk", "gkl")
N_CELLS_COMPARED = 15
Z = 2.935


def cell_seed(li, ri):
    return BASE_SEED + 1000 * li + ri


def run_cell(name, hexs, published, n_cells, n_ics, steps, seed):
    table = evca.decode_table(hexs)
    ics = evca.make_ics(n_ics, n_cells, seed)
    r = evca.classify(table, ics, steps, witness_limit=evca.WITNESS_LIMIT)
    p = r["accuracy"]
    se = math.sqrt(p * (1 - p) / n_ics)
    diff = p - published
    band = Z * se
    return {"rule": name, "n_cells": n_cells, "n_ics": n_ics, "steps": steps,
            "seed": seed, "published": published, "measured": p,
            "n_correct": r["n_correct"], "diff": diff, "se": se,
            "band_half_width": band,
            "abs_diff_in_se": (abs(diff) / se) if se > 0 else None,
            "decision": "REPRODUCED" if abs(diff) <= band else "DISCREPANT",
            "uniform_fixed_points": r["uniform_fixed_points"],
            "correct_mask_digest": r["correct_mask_digest"]}


def main():
    ws = assert_not_canonical("run the Juille-Pollack reproduction")
    t0 = time.time()
    tab = json.load(open(TABLES, encoding="utf-8"))
    assert tab["q1_gkl_calibration"] is True
    out = {"protocol": "herakles/specimens/spec-juille-pollack-1998/PROTOCOL.md",
           "workspace": ws, "z": Z, "cells_compared": N_CELLS_COMPARED,
           "primary": [], "cheat": None, "q5": None}
    print("%-6s %5s %6s %9s %9s %8s %7s %6s  %s" % (
        "rule", "N", "n_ics", "published", "measured", "diff", "band",
        "se_x", "decision"))
    for li, (n_cells, n_ics) in enumerate(LATTICES):
        for ri, name in enumerate(RULES):
            t = tab["tables"][name]
            row = run_cell(name, t["hex"], float(t["published_P"][str(n_cells)]),
                           n_cells, n_ics, 2 * n_cells, cell_seed(li, ri))
            out["primary"].append(row)
            print("%-6s %5d %6d %9.3f %9.4f %+8.4f %7.4f %6.2f  %s" % (
                name, n_cells, n_ics, row["published"], row["measured"],
                row["diff"], row["band_half_width"], row["abs_diff_in_se"],
                row["decision"]), flush=True)
            # write after every cell so a crash leaves rows, not nothing
            with open(OUT, "w", encoding="utf-8", newline="\n") as f:
                json.dump(out, f, indent=1)
    # CHEAT: mis-paired table, row 1 of coev1 + row 2 of coev2, N = 149.
    bits = tab["tables"]["coev1"]["bits"][:64] + tab["tables"]["coev2"]["bits"][64:]
    hexs = "%032x" % int(bits, 2)
    ics = evca.make_ics(4000, 149, BASE_SEED + 777)
    r = evca.classify(evca.decode_table(hexs), ics, 298)
    out["cheat"] = {"construction": "coev1 bits 0-63 + coev2 bits 64-127",
                    "hex": hexs, "n_cells": 149, "n_ics": 4000, "steps": 298,
                    "measured": r["accuracy"],
                    "q4_below_0_5": r["accuracy"] < 0.5}
    print("CHEAT mis-paired table at N=149:", r["accuracy"])
    # Q5: coev1/coev2 measured at N=149 vs the best held published P (GKL 0.816)
    best_held = max(float(G.GENOMES[n]["published_P"][149]) for n in G.NAMES)
    m = {row["rule"]: row["measured"] for row in out["primary"]
         if row["n_cells"] == 149}
    out["q5"] = {"best_held_published_P_149": best_held,
                 "coev1_measured_149": m["coev1"], "coev2_measured_149": m["coev2"],
                 "holds": m["coev1"] > best_held and m["coev2"] > best_held}
    n_rep = sum(1 for r in out["primary"] if r["decision"] == "REPRODUCED")
    out["q3"] = {"reproduced": n_rep, "of": len(out["primary"]),
                 "holds": n_rep >= 12}
    out["elapsed_s"] = round(time.time() - t0, 1)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    print("Q3 REPRODUCED %d of %d; Q4 %s; Q5 %s; %.0fs" % (
        n_rep, len(out["primary"]), out["cheat"]["q4_below_0_5"],
        out["q5"]["holds"], out["elapsed_s"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
