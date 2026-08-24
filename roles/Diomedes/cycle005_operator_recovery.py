"""Diomedes cycle 005 — STEP 0: recover the operator semantics EXACTLY, from data, and
differential-test three independent sources against each other.

Charter S20: move from inference to discrete analysis, and put non-LLM controls at every
step. This script assumes NOTHING about what `log2_floor` or `sq_mod_100` mean. It
recovers each operator as an exact integer lookup table from the corpus's own records,
then checks the recovered tables against two other generator families that were produced
by different code paths.

Three independent sources of the same facts:
  S1  b4 / b3  ->  (operator, input_value) -> op_v          direct function samples
  S2  b2       ->  (f, g, v) -> fg_result, gf_result        composition results
  S3  b2       ->  (f, g, v) -> commutes                    the boolean the generator logged

Controls, all exact and all failing loudly:
  C1 CONSISTENCY  a given (operator, v) must never map to two different values anywhere
  C2 COMPOSITION  S1 composed by hand must reproduce S2's fg_result on every shared cell
  C3 BOOLEAN      (fg_result == gf_result) must equal S3's `commutes` on every shared cell
  C4 COVERAGE     report exactly which (operator, value) cells are missing; no interpolation

If C1-C3 hold on every shared cell, the operator semantics are established by execution,
not by my reading of the field names -- which is the point.

    python roles/Diomedes/cycle005_operator_recovery.py
"""
import collections
import glob
import gzip
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CORPUS = ROOT / "theseus/corpus"
OUT = pathlib.Path(__file__).resolve().parent / "cycle005_operator_tables.json"
MAX_LINES = 120_000


def main():
    files = sorted(glob.glob(str(CORPUS / "batch-*.jsonl.gz")))

    op_tab = collections.defaultdict(dict)        # S1: op -> {v: op(v)}
    conflicts = []                                 # C1 violations
    comp_rows = []                                 # S2/S3 rows for C2/C3

    def record(op, v, r):
        if op is None or v is None or r is None:
            return
        prev = op_tab[op].get(v)
        if prev is not None and prev != r:
            conflicts.append({"operator": op, "v": v, "seen": prev, "also": r})
        op_tab[op][v] = r

    for f in files:
        with gzip.open(f, "rt", encoding="utf-8", errors="replace") as fh:
            for j, line in enumerate(fh):
                if j >= MAX_LINES:
                    break
                if '"b2"' not in line and '"b3"' not in line and '"b4"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                g = d.get("generator_id")
                p = d.get("claim_payload") or {}
                if g == "b4":                       # {operator, input_value, op_v}
                    record(p.get("operator"), p.get("input_value"), p.get("op_v"))
                elif g == "b3":                     # {operator, input_value, op_v, op_op_v}
                    record(p.get("operator"), p.get("input_value"), p.get("op_v"))
                    record(p.get("operator"), p.get("op_v"), p.get("op_op_v"))
                elif g == "b2":
                    if all(k in p for k in ("operator_f", "operator_g", "input_value",
                                            "fg_result", "gf_result", "commutes")):
                        comp_rows.append((p["operator_f"], p["operator_g"], p["input_value"],
                                          p["fg_result"], p["gf_result"], p["commutes"]))

    # ---- C2 / C3 : differential tests against the composition records ----
    c2_ok = c2_tested = c3_ok = c3_tested = 0
    c2_fail, c3_fail = [], []
    for f_, g_, v, fg, gf, comm in comp_rows:
        gv = op_tab.get(g_, {}).get(v)
        if gv is not None:
            fgv = op_tab.get(f_, {}).get(gv)
            if fgv is not None:
                c2_tested += 1
                if fgv == fg:
                    c2_ok += 1
                elif len(c2_fail) < 12:
                    c2_fail.append({"f": f_, "g": g_, "v": v, "recovered": fgv, "logged": fg})
        c3_tested += 1
        if (fg == gf) == bool(comm):
            c3_ok += 1
        elif len(c3_fail) < 12:
            c3_fail.append({"f": f_, "g": g_, "v": v, "fg": fg, "gf": gf, "commutes": comm})

    ops = sorted(op_tab)
    vals = sorted({v for t in op_tab.values() for v in t})
    core = [v for v in vals if -50 <= v <= 50]
    coverage = {op: {"n_cells": len(op_tab[op]),
                     "core_-50..50_covered": sum(1 for v in core if v in op_tab[op]),
                     "core_missing": [v for v in core if v not in op_tab[op]][:10]}
               for op in ops}

    rep = {
        "sources": {"S1_b3_b4_function_samples": sum(len(t) for t in op_tab.values()),
                    "S2_S3_b2_composition_rows": len(comp_rows)},
        "operators_recovered": ops,
        "value_range_seen": [min(vals), max(vals)] if vals else None,
        "controls": {
            "C1_consistency_violations": len(conflicts),
            "C1_examples": conflicts[:10],
            "C2_composition_tested": c2_tested, "C2_composition_agree": c2_ok,
            "C2_agreement_rate": round(c2_ok / c2_tested, 6) if c2_tested else None,
            "C2_failures": c2_fail,
            "C3_boolean_tested": c3_tested, "C3_boolean_agree": c3_ok,
            "C3_agreement_rate": round(c3_ok / c3_tested, 6) if c3_tested else None,
            "C3_failures": c3_fail,
        },
        "C4_coverage": coverage,
        "operator_tables": {op: {str(k): v for k, v in sorted(op_tab[op].items())} for op in ops},
        "verdict": None,
    }
    exact = (len(conflicts) == 0 and c2_tested > 0 and c2_ok == c2_tested
             and c3_tested > 0 and c3_ok == c3_tested)
    rep["verdict"] = ("EXACT - operator semantics established by execution across three "
                      "independent sources; cycle 005 may enumerate"
                      if exact else
                      "DISAGREEMENT - sources conflict; enumeration is NOT admissible until resolved")
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")

    print("operators recovered:", ops)
    print("value range:", rep["value_range_seen"])
    print(f"S1 function samples: {rep['sources']['S1_b3_b4_function_samples']:,}   "
          f"S2/S3 composition rows: {len(comp_rows):,}")
    print(f"C1 consistency violations : {len(conflicts)}")
    print(f"C2 composition agreement  : {c2_ok:,}/{c2_tested:,}"
          + (f" = {c2_ok/c2_tested:.6f}" if c2_tested else ""))
    print(f"C3 boolean agreement      : {c3_ok:,}/{c3_tested:,}"
          + (f" = {c3_ok/c3_tested:.6f}" if c3_tested else ""))
    print("C4 coverage (core -50..50 of 101):")
    for op in ops:
        print(f"    {op:14s} {coverage[op]['core_-50..50_covered']:>4}/101")
    print("VERDICT:", rep["verdict"])
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
