"""Generate primordial/soup/b7/c7_fixed_eligibility.json for lane C's single C7 re-run, deterministically from B7b's rows.

Layout = C's FIXED trajectory() (d1f73fc3c): observation columns reordered so the non-charge columns keep their
permuted order and the charge channel is last; C's inputs are the D-1 register columns, and `fixed_column` below indexes
exactly those columns.

Per world: D, the permuted charge column, the fixed column order, and for every register column: register index,
exact_on_reachable (B7b), identifiable_by_odd_differences (B7b post hoc), regime_changes_form, and per regime the source
fixed column and (a, c) with y_next == a * x_source + c (mod 2^16) on every reachable in-regime transition.

This file is a lookup, not a verdict: B7b's own H2 died. C should pre-register its eligibility rule before using it.

usage: python -m primordial.soup.b7.make_eligibility_list
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROWS = ROOT / "ledger" / "rows" / "B" / "B7b-reachable-eligibility.jsonl"
POSTHOC = ROOT / "ledger" / "rows" / "B" / "B7b-identifiability-posthoc.jsonl"
OUT = pathlib.Path(__file__).resolve().with_name("c7_fixed_eligibility.json")


def main():
    rows = [json.loads(x) for x in open(ROWS, encoding="utf-8")]
    ph = [json.loads(x) for x in open(POSTHOC, encoding="utf-8")]
    ident = {(x["gen_seed"], x["fixed_column"]): x["identifiable_by_odd_differences"]
             for x in ph if x["kind"] == "fixed_target_identifiability"}
    worlds = {}
    for w in (x for x in rows if x["kind"] == "world"):
        cols = []
        for t in w["fixed_layout_targets"]:
            fits = {}
            for regime, hit in t["fit"].items():
                fits[regime] = None if hit is None else {"kind": hit["kind"],
                                                         "source_fixed_column": hit["source_fixed_column"],
                                                         "a": hit["a"], "c": hit["c"]}
            cols.append({"fixed_column": t["fixed_column"], "register": t["register"],
                         "exact_on_reachable": t["exact_on_reachable"],
                         "identifiable_by_odd_differences": ident.get((w["gen_seed"], t["fixed_column"]))
                         if t["exact_on_reachable"] else None,
                         "regime_changes_form": t["regime_changes_form"], "fit": fits})
        worlds[str(w["gen_seed"])] = {"D": w["D"], "charge_column_permuted": w["charge_column_permuted"],
                                     "fixed_order": w["fixed_order"], "corrupt_rate": w["corrupt_rate"],
                                     "regimes": w["regimes"], "register_columns": cols}
    doc = {"schema": "lane-B C7 fixed-layout exact-fit lookup v1",
           "source_rows": ["primordial/ledger/rows/B/B7b-reachable-eligibility.jsonl",
                           "primordial/ledger/rows/B/B7b-identifiability-posthoc.jsonl"],
           "caveat": "B7b's H2 died (4/24 excluded targets exact but unidentifiable by odd differences); a lookup, not a verdict",
           "field_semantics": {
               "regime_changes_form": ("compares the register's FULL composed form (A[r] A row + constant) between regimes, "
                                       "over all states. It can be true while the function a single-source learner sees on "
                                       "reachable states is identical in both regimes (lane C found 20 such columns, e.g. "
                                       "y = 1*x + 0 before and after the flip), so true does NOT guarantee a detectable flip."),
               "fit": ("(source_fixed_column, a, c) is the FIRST exact single-source representation found in input order. "
                       "Several equivalent representations can exist (e.g. a register predicting its own next value); "
                       "differing (a, c) across regimes for this representation does NOT mean the function changes. Compare "
                       "functions, not representations: lane C's C7e admitted 5 columns with regime_changes_form=false "
                       "because their listed (a, c) differed, and all 57 of their switches were missed."),
               "post_hoc_c7e": ("regime_changes_form=true AND a differing listed fit detected 73/73 switches in C7e (post hoc, "
                                "13 targets in 9 worlds; not a validated rule)"),
           },
           "count_note": "exact+identifiable+regime_changes_form = 33 (a B7b bus note mislabeled 43, which is exact+regime_changes_form)",
           "worlds": worlds}
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="ascii", newline="\n")
    n = sum(len(v["register_columns"]) for v in worlds.values())
    e = sum(c["exact_on_reachable"] for v in worlds.values() for c in v["register_columns"])
    i = sum(bool(c["identifiable_by_odd_differences"]) for v in worlds.values() for c in v["register_columns"])
    print(f"wrote {OUT.name}: {len(worlds)} worlds, {n} register columns, {e} exact, {i} exact+identifiable")


if __name__ == "__main__":
    main()
