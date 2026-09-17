"""File the B7b receipt from committed rows. Run only after the rows commit is pushed; pass that SHA.

usage: python -m primordial.soup.b7.receipt_b7b --git <pushed sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROWS = ROOT / "ledger" / "rows" / "B" / "B7b-reachable-eligibility.jsonl"
POSTHOC = ROOT / "ledger" / "rows" / "B" / "B7b-identifiability-posthoc.jsonl"
CLAIM = ("B7b: exact-fit eligibility on REACHABLE states (B7 demanded single-source over all states). One tick in regime "
         "g is s' = A s + b; for every transition after the first, target register r is exactly y = a*x_q + c iff "
         "A[r] A == a A[q] (mod 2^16). Predicted on C7d rows (C's old layout): (H1) all 28 full-fit targets are exact on "
         "reachable states with source among the old inputs; (H2) 0 of the 24 excluded targets are; (H3) gs 612 j2 is "
         "the charge column. Controls: every exact (a, c) reproduces the next register on 100% of in-regime transitions "
         "from tick 1; every NOT-exact fixed-layout target keeps C's fit_affine below support 1.0; B7's all-states rule "
         "must fail H1. Any H1/H2 counterexample -> KILL.")


def _jsonl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8")]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rows = _jsonl(ROWS)
    ph = _jsonl(POSTHOC)
    W = [x for x in rows if x["kind"] == "world"]
    ft = [x for x in rows if x["kind"] == "c7d_target"]
    ex = [x for x in rows if x["kind"] == "c7d_excluded"]
    full = [x for x in ft if x["c_full_fit"]]
    h1_n = sum(x["b7b_class"] == "exact_on_reachable" for x in full)
    h2_ce = [x for x in ex if x["b7b_class"] == "exact_on_reachable"]
    g612 = [x["b7b_class"] for x in ft if x["gen_seed"] == 612 and x["j"] == 2]
    pos = min(w["positive_control_min_match"] for w in W)
    neg = max(w["negative_control_max_support"] for w in W)
    neg_n = sum(w["negative_control_cases"] for w in W)
    cheat_n = sum(bool(x["b7_all_states_rule"]) for x in full)
    h1, h2, h3 = h1_n == len(full), not h2_ce, g612 == ["charge"]
    controls_ok = pos == 1.0 and neg < 1.0 and cheat_n < len(full)
    status = "INDETERMINATE" if not controls_ok else ("PASS" if (h1 and h2 and h3) else "KILL")
    ce = [x for x in ph if x["kind"] == "counterexample"]
    idf = [x for x in ph if x["kind"] == "fixed_target_identifiability"]
    exact_fixed = sum(t["exact_on_reachable"] for w in W for t in w["fixed_layout_targets"])
    rec = {
        "lane": "B", "exp_id": "B7b-reachable-state-exact-fit", "claim": CLAIM, "status": status,
        "engineering": {"worlds": len(W), "c7d_full_fit_targets": len(full), "c7d_excluded_targets": len(ex),
                        "negative_control_cases": neg_n},
        "science": {
            "hypothesis_scoring": {
                "h1_full_fit_exact_on_reachable": f"{'CONFIRMED' if h1 else 'WRONG'} ({h1_n}/{len(full)})",
                "h2_excluded_not_exact": (f"{'CONFIRMED' if h2 else 'WRONG'} ({len(h2_ce)}/{len(ex)} excluded targets "
                                          f"are exact on reachable states: "
                                          f"{[(x['gen_seed'], x['j'], x['c_null_surprises']) for x in h2_ce]})"),
                "h3_g612_j2_charge": f"{'CONFIRMED' if h3 else 'WRONG'} ({g612})",
            },
            "repairs_b7": f"B7's all-states rule held {cheat_n}/{len(full)} full-fit targets; the reachable-state rule holds {h1_n}/{len(full)}",
            "post_hoc_not_verdict": {
                "diagnosis": ("all 4 H2 counterexamples are a register carrying its own value (y = 1*x_r + 0) whose "
                              "reachable form has only EVEN coefficients, so every source difference is even and C's "
                              "fit_affine, which solves only from odd differences, can never recover a"),
                "evidence": [{"gen_seed": x["gen_seed"], "j": x["j"],
                              "exact_relation_rate": x["exact_relation_rate_on_null_trajectory"],
                              "source_min_2adic_valuation": x["source_row_min_2adic_valuation"],
                              "odd_difference_share": x["odd_difference_share_of_source"],
                              "c_fit_affine_support": round(x["c_fit_affine_best_support"], 4)} for x in ce],
                "consequence": "exact-on-reachable is necessary for C's learner but not sufficient; identifiability "
                               "(an odd coefficient in the source's reachable form) is the missing condition",
            },
            "deliverable_fixed_layout": {
                "exact_on_reachable": exact_fixed,
                "exact_and_identifiable": sum(x["identifiable_by_odd_differences"] for x in idf),
                "exact_identifiable_and_regime_changes_form": sum(x["identifiable_by_odd_differences"] and
                                                                  x["regime_changes_form"] for x in idf),
                "file": "primordial/soup/b7/c7_fixed_eligibility.json",
                "proposal_for_C_not_validated_by_B7b": ("eligible = exact_on_reachable AND identifiable_by_odd_differences "
                                                        "AND regime_changes_form, decided from the genome before any run; "
                                                        "C should pre-register its own rule"),
            },
        },
        "controls": {
            "cheat": f"B7's all-states rule scored on the same 28 full-fit targets: {cheat_n}/{len(full)} (fails H1)",
            "positive": f"every exact (a, c) reproduces the next register on in-regime transitions from tick 1: min match {pos}",
            "negative": f"C's fit_affine on NOT-exact fixed-layout targets: max support {neg:.4f} over {neg_n} cases (< 1.0)",
        },
        "rows": "primordial/ledger/rows/B/B7b-reachable-eligibility.jsonl + B7b-identifiability-posthoc.jsonl",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "science", "controls")}, indent=1))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
