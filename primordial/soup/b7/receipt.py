"""File the B7 receipt from committed rows. Run AFTER rebase.

usage: python -m primordial.soup.b7.receipt --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B" / "B7-structural-eligibility.jsonl"
CLAIM = ("B7: structural (no-sampling) exact-fit eligibility for lane C's C7-style affine targets in B worlds "
         "(zero actions, stoch 0, obs_delay 0), cross-checked against C7c/C7d committed rows. Predicted: (H1) the "
         "charge bucket is NOT at the last permuted obs position in >= 50% of C7d's 36 worlds (C's harness assumes it "
         "is); (H2) every C7d target with null surprises <= 2 and full support is exact single-source-in-inputs, 0 "
         "exceptions; (H3) gs 612 j2 (C7d's only KILL target) is NOT exact-in-inputs; (H4) every C7d sensitive target "
         "excluded for null surprises > 2 is NOT exact-in-inputs. Controls: composed forms reproduce next registers "
         "exactly on NpEncounter zero-action trajectories 36/36; reverse-order cheat fails in >= 50% of worlds.")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rows = [json.loads(x) for x in open(ROWS, encoding="utf-8")]
    W = [r for r in rows if r["kind"] == "world"]
    ct = [r for r in rows if r["kind"] == "c_target" and r["source"] == "C7d"]
    cs = [r for r in rows if r["kind"] == "c_sensitive" and r["source"] == "C7d"]
    n = len(W)
    not_last = sum(not w["charge_is_last"] for w in W)
    val_ok = sum(w["validation"]["real"] == 1.0 and w["validation"]["null"] == 1.0 for w in W)
    g2 = [w for w in W if w["lin_ops"] >= 2]
    rev_fail = sum(w["validation_reverse_cheat"]["real"] < 1.0 or w["validation_reverse_cheat"]["null"] < 1.0 for w in g2)
    full = [r for r in ct if r["c_full_fit"]]
    exceptions = [r for r in full if r["b7_class_null"] != "exact_in_inputs"]
    g612 = next((r for r in ct if r["gen_seed"] == 612 and r["j"] == 2), None)
    excluded = [r for r in cs if not r["c_eligible"]]
    h4_counter = [r for r in excluded if r["b7_class_null"] == "exact_in_inputs"]
    h1 = not_last >= n / 2
    h2 = not exceptions
    h3 = g612 is not None and g612["b7_class_null"] != "exact_in_inputs"
    h4 = not h4_counter
    controls_ok = val_ok == n and rev_fail >= len(g2) / 2
    status = "INDETERMINATE" if not controls_ok else ("PASS" if (h1 and h2 and h3 and h4) else "KILL")
    exc_detail = [{"gen_seed": r["gen_seed"], "j": r["j"], "b7_class": r["b7_class_null"], "sources": r["b7_sources_null"],
                   "c_null_surprises": r["c_null_surprises"], "c_null_support": round(r["c_null_support"], 3),
                   "expected_support": round(r["expected_support"], 3)} for r in exceptions]
    one_surprise = sum(r["c_null_surprises"] == 1 for r in exceptions)
    charge_scored = [r for r in rows if r["kind"] == "c_target" and r["b7_class_null"] == "charge"]
    rec = {
        "lane": "B", "exp_id": "B7-structural-exact-fit-eligibility", "claim": CLAIM, "status": status,
        "refutes": ("C7d-chance-grounded-contrast CAUSE ATTRIBUTION only (not its verdict): C attributed the KILL to "
                    "'gs 612 target 2 ... a PARTIAL single-source fit'; that column is the charge bucket, mislabelled as a "
                    "register feature by the harness's charge-position assumption"),
        "engineering": {"worlds": n, "c7d_targets": len(ct), "c7d_sensitive_candidates": len(cs)},
        "science": {
            "hypothesis_scoring": {
                "h1_charge_not_last_ge_50pct": f"{'CONFIRMED' if h1 else 'WRONG'} ({not_last}/{n} worlds)",
                "h2_full_fit_targets_all_exact_in_inputs": (f"CONFIRMED ({len(full)}/{len(full)})" if h2 else
                                                            f"WRONG ({len(exceptions)}/{len(full)} full-fit targets are "
                                                            f"not exact-in-inputs under B7's all-states model)"),
                "h3_g612_j2_not_exact": (f"{'CONFIRMED' if h3 else 'WRONG'} (class: "
                                         f"{g612['b7_class_null'] if g612 else None})"),
                "h4_excluded_not_exact": f"{'CONFIRMED' if h4 else 'WRONG'} ({len(h4_counter)} counterexamples / "
                                         f"{len(excluded)} excluded; classes "
                                         f"{dict(Counter(r['b7_class_null'] for r in excluded))})",
            },
            "h2_exceptions": exc_detail,
            "c_harness_defect": {
                "fact": ("C7b/c/d take obs from B NpEncounter.observe_all, which places the charge bucket at vals[D-1] and "
                         "THEN permutes by obs_perm; the harness treats permuted column D-1 as charge (targets j in "
                         "range(D-1), inputs X = obs[..., :-1])"),
                "worlds_where_inputs_drop_a_register_and_include_charge": f"{not_last}/{n}",
                "charge_column_scored_as_a_target": [(r["source"], r["gen_seed"], r["j"],
                                                      f"{r['c_detected']}/{r['c_switches']} detected",
                                                      round(r["c_null_support"], 3)) for r in charge_scored],
                "fix": "q_star = list(m.obs_perm).index(D - 1); exclude q_star from targets and from X; keep the other "
                       "D-1 columns (all registers) as inputs",
            },
            "post_hoc_not_verdict": (f"{one_surprise}/{len(exceptions)} H2 exceptions have exactly 1 null surprise and "
                                     "support ~1 - 1/T (0.992 at T=128, 0.984 at T=64): consistent with a fit that "
                                     "fails only on the first transition, where registers are still independent "
                                     "initial values, and is exact after tick 1, when lin_ops have tied registers "
                                     "together. B7's all-states classification is too strict; a reachable-state "
                                     "test is proposed separately as B7b (new hypothesis, new bars)"),
        },
        "controls": {
            "cheat": (f"reverse-order lin_op composition fails trajectory validation in {rev_fail}/{len(g2)} worlds "
                      "with >= 2 lin_ops"),
            "validation": (f"composed in-order forms reproduce next registers exactly (every env, every tick, real "
                           f"and no_regime_flip) in {val_ok}/{n} worlds"),
        },
        "rows": "primordial/ledger/rows/B/B7-structural-eligibility.jsonl",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "refutes", "controls")}, indent=1))
    print(json.dumps(rec["science"]["hypothesis_scoring"], indent=1))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
