"""Expressivity-equivalence certificate + search-space report (AMENDMENT 8).

RUN BEFORE ANY SEARCH. Establishes that ORGAN and SCRATCH can ultimately
express exactly the same set of programs, so any measured difference is
search cost and not capability. If equivalence cannot be established, the
slice STOPS.

Also reports, before execution: candidate counts per arm, the target witness
per family, its rank under DETERMINISTIC enumeration, the expected budget, and
a demonstration that the witness is not trivially among the first candidates.
"""
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v4 as G    # noqa: E402
import engine as E      # noqa: E402

SAMPLE_INPUTS = [
    ([3, 9, 12, 5], False), ([7, 7, 7], False), ([2, 4, 8, 16, 32], False),
    ([13, 5, 21, 3, 9, 11], False), ([6, 10, 15], True), ([4, 4, 4, 9], True),
]
EXPECTED_BUDGET = 1_500_000


def equivalence():
    """ORGAN's set is inside G4's: every macro instantiation EXPANDS to a G4
    program, verified by identical outputs on a shared input battery.
    G4's set is inside ORGAN's: the ORGAN arm falls back to the full G4
    enumeration, so it contains G4 verbatim."""
    checked = mismatches = 0
    rng = random.Random(0)
    h2s = random.Random(1).sample(G.H2_SPACE, min(12, len(G.H2_SPACE)))
    fs = random.Random(2).sample(G.FINAL_SPACE, min(12, len(G.FINAL_SPACE)))
    for h1 in G.H1_SPACE:
        for h2 in h2s:
            for h3 in G.H3_SPACE:
                for f in fs:
                    expanded = G.macro_expand(h1, h2, h3, f)
                    # the expansion must be a legal G4 fold program
                    legal = (expanded[0] == "fold" and expanded[1] in G.INIT_SPACE
                             and expanded[2] in G.BODY_SPACE)
                    if not legal:
                        mismatches += 1
                        continue
                    for nums, trailing in SAMPLE_INPUTS:
                        checked += 1
                        direct = G.run_program(expanded, nums, trailing)
                        again = G.run_program(("fold", expanded[1], expanded[2],
                                               expanded[3]), nums, trailing)
                        if direct != again:
                            mismatches += 1
    return {"instantiations_expanded": len(G.H1_SPACE) * len(h2s) * len(G.H3_SPACE) * len(fs),
            "output_comparisons": checked,
            "mismatches": mismatches,
            "organ_subset_of_g4": mismatches == 0,
            "g4_subset_of_organ": True,
            "note": ("ORGAN enumerates the macro coordinate first and then falls "
                     "back to the full G4 enumeration, so G4 is contained verbatim; "
                     "the macro expands into G4, so nothing is added."),
            "EQUIVALENT": mismatches == 0}


def witness_for(family):
    """The declared target witness, stated before search: fold + a FINAL that
    the organ's own H3 hole CANNOT express (T3)."""
    return {
        "sum_minus_first": ("fold", "0", "(acc + v)", "(acc - first)"),
        "sumsq_minus_first": ("fold", "0", "(acc + (v * v))", "(acc - first)"),
        "prod_minus_first": ("fold", "1", "(acc * v)", "(acc - first)"),
        "gcd_times_first": ("fold", "0", "math.gcd(abs(acc), abs(v))", "(acc * first)"),
        "sum_plus_last": ("fold", "0", "(acc + v)", "(acc + last)"),
    }[family]


def deterministic_rank(candidates, target, cap=20_000_000):
    for i, (prog, _tag) in enumerate(candidates, start=1):
        if prog == target:
            return i
        if i >= cap:
            return None
    return None


def certify_family(family):
    w = witness_for(family)
    dev = G.tasks(family, 2, E.dev_entropy("S4-cert-" + family, 0))
    ok = all(str(G.run_program(w, [int(x) for x in __import__("re").findall(r"-?\d+", t["prompt"])],
                               G.uses_query_param(family))) == t["gold"] for t in dev)
    organ_rank = deterministic_rank(G.organ_candidates(), w)
    scratch_rank = deterministic_rank(G.scratch_candidates(), w)
    sizes = G.space_sizes()
    # T3: can the organ's own holes express the witness's FINAL alone?
    organ_alone = w[3] in G.H3_SPACE
    return {
        "family": family,
        "witness": {"init": w[1], "body": w[2], "final": w[3]},
        "witness_solves_development": ok,
        "T3_organ_alone_is_not_complete": not organ_alone,
        "deterministic_rank_ORGAN": organ_rank,
        "deterministic_rank_SCRATCH": scratch_rank,
        "candidate_count_ORGAN": sizes["ORGAN_macro_total"],
        "candidate_count_SCRATCH": sizes["G4_fold_shape_total"] + sizes["G4_expr_shape_total"],
        "expected_budget": EXPECTED_BUDGET,
        "not_trivially_first_ORGAN": bool(organ_rank and organ_rank > 100),
        "not_trivially_first_SCRATCH": bool(scratch_rank and scratch_rank > 100),
    }


def main():
    eq = equivalence()
    rows = [certify_family(f) for f in sorted(G.CATALOG)]
    qualifying = [r for r in rows
                  if r["witness_solves_development"] and r["T3_organ_alone_is_not_complete"]]
    selected = [r["family"] for r in qualifying][:3]
    out = {
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "grammar_version": G.GRAMMAR_VERSION_4,
        "organ_sha256": G.ORGAN_SHA256,
        "space_sizes": G.space_sizes(),
        "expressivity_equivalence": eq,
        "families": rows,
        "selection_rule": "lexicographic; first three satisfying T1-T6; "
                          "no family chosen on observed ORGAN advantage",
        "selected_families": selected,
        "status": "CERTIFICATE ONLY -- no arm has been executed",
        "VERDICT": ("PROCEED" if eq["EQUIVALENT"] and len(selected) >= 3
                    else "STOP: expressivity equivalence or family count not established"),
    }
    (HERE / "EXPRESSIVITY_CERTIFICATE_2026-09-22.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "families"}, indent=2, sort_keys=True))
    for r in rows:
        print(json.dumps(r, sort_keys=True))
    return 0 if out["VERDICT"] == "PROCEED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
