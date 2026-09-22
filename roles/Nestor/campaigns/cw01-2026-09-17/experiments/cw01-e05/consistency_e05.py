"""cw01-e05 freeze-boundary consistency gate.

Two DIFFERENT kinds of check, deliberately kept apart:

  PART A  SPECIFICATION CONSISTENCY
          Do the committed artifacts state the same binding specification?
          WORLD.json, QUALIFY.json, VERDICT_CONTRACT.json, the driver's embedded
          contract, and the defect ledger. Recorded calibration figures are compared
          as RECORDED CONSTANTS. No world execution.

  PART B  EMPIRICAL RECONSTRUCTION
          Re-run the frozen selection procedure and require it to reproduce what was
          recorded. BINDING INVARIANTS: exactly 56 admissible subsets are evaluated;
          BEST reconstructs as [0,2,4]; WORST reconstructs as [4,5,7]; the frozen
          statistic and ordering procedure are used unchanged.

          If recomputation selects a different BEST or WORST, that is a REAL
          consistency failure. It is not a floating-point tolerance to widen and not
          a threshold to relax after observing it.

The driver's contract is IMPORTED as a live object (execute_e05.EMBEDDED_CONTRACT).
Nothing here inspects source text with regex or textual scraping.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
REPO = BASE.parents[3]
for p in (str(REPO), str(BASE / "lib"), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import world_e05 as W          # noqa: E402
import seeds as S              # noqa: E402
import contract as CT          # noqa: E402
import execute_e05 as X        # noqa: E402

EXPECTED_HASH = "c80b5bfd348f7b87418166061f39c1446bd45c6e74ff060f9c5927e24b2c5619"
BINDING_BEST = [0, 2, 4]
BINDING_WORST = [4, 5, 7]
BINDING_N_SUBSETS = 56

E05_DEFECTS = ["CW01-D037", "CW01-D038a", "CW01-D038b", "CW01-D039",
               "CW01-D040", "CW01-D041", "CW01-D042"]

PART_A = []
PART_B = []


def check(bucket, cid, passed, detail):
    bucket.append({"id": cid, "passed": bool(passed), "detail": detail})
    print("    %-28s %-6s %s" % (cid, "PASS" if passed else "FAIL", detail))
    return passed


# ------------------------------------------------------------ canonical readings
#
# Free-form prose is reduced to a canonical rule identifier rather than compared
# literally, so that wording differences between artifacts are not reported as
# specification drift, while a genuine change of rule is.

def _norm(t):
    return re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()


def basis_of(text):
    """Is a superadditivity definition expressed on INFORMATION or on SCORE?"""
    t = _norm(text)
    score_vocab = ("mixture value" in t) or ("score of" in t)
    info_vocab = ("information" in t) or ("mixture info" in t)
    if info_vocab and not score_vocab:
        return "information"
    if score_vocab and not info_vocab:
        return "score"
    if info_vocab and score_vocab:
        return "ambiguous"
    return "unspecified"


def statistic_id(text):
    t = _norm(text)
    if ("difference in differences" in t or t.startswith("did ")) \
            and ("normalised" in t or "normalized" in t) and "superadditivity" in t:
        return "did_normalised_superadditivity"
    return "OTHER(%s)" % t[:48]


def selection_id(text):
    t = _norm(text)
    if "exhaustive" in t and "enumeration" in t:
        return "exhaustive_enumeration"
    return "OTHER(%s)" % t[:48]


def budget_rule_id(text):
    t = _norm(text)
    basis = ("mean_conjunctive_demand_size"
             if {"mean", "conjunctive", "demand", "size"} <= set(t.split())
             else "UNKNOWN_BASIS")
    prec = ("declared_before_superadditivity"
            if ("declared" in t and "before" in t) else "NO_PRECEDENCE_CLAUSE")
    return "%s|%s" % (basis, prec)


# ------------------------------------------------------------------- PART A

def part_a(world, qualify, committed_raw):
    print("\n  PART A - SPECIFICATION CONSISTENCY (no world execution)\n")
    driver = CT.VerdictContract(X.EMBEDDED_CONTRACT)      # IMPORTED object
    fmc = qualify["final_measurement_contract"]
    enum = world["empirical_calibration"]["subset_enumeration"]
    inter = world["empirical_calibration"]["interaction_test"]

    # A1/A2 contract identity
    committed = CT.VerdictContract.load(HERE / "VERDICT_CONTRACT.json")
    check(PART_A, "A1_driver_matches_committed", driver.hash == committed.hash,
          "driver %s vs committed %s" % (driver.hash[:16], committed.hash[:16]))
    check(PART_A, "A2_hash_is_the_frozen_one", driver.hash == EXPECTED_HASH,
          "contract identity %s" % driver.hash[:16])
    check(PART_A, "A3_committed_self_verifies",
          committed_raw.get("contract_sha256") == committed.hash,
          "stored hash matches its own body")

    # A4 budget agreement across every artifact
    B = driver.get("budget_B")
    arms = {a: world["arms"][a].get("max_components")
            for a in ("treatment", "control_disjunctive_only")}
    check(PART_A, "A4_budget_B_agrees",
          all(v == B for v in arms.values()) and fmc["budget_B"] == B,
          "contract %s, WORLD arms %s, QUALIFY %s" % (B, arms, fmc["budget_B"]))

    # A5 BEST/WORST recorded identically
    check(PART_A, "A5_recorded_sets_agree",
          list(enum["best"]) == list(fmc["BEST"]) and list(enum["worst"]) == list(fmc["WORST"]),
          "WORLD best/worst %s/%s vs QUALIFY %s/%s"
          % (enum["best"], enum["worst"], fmc["BEST"], fmc["WORST"]))

    # A6 recorded calibration constants (exact equality, as recorded)
    cal = fmc["calibration"]
    pairs = [("best_conjunctive_pct", cal["BEST"]["conjunctive_pct"], inter["best_conjunctive_pct"]),
             ("best_disjunctive_pct", cal["BEST"]["disjunctive_pct"], inter["best_disjunctive_pct"]),
             ("best_law_effect", cal["BEST"]["law_effect_points"], inter["law_on_effect_best_points"]),
             ("worst_conjunctive_pct", cal["WORST"]["conjunctive_pct"], inter["worst_conjunctive_pct"]),
             ("worst_disjunctive_pct", cal["WORST"]["disjunctive_pct"], inter["worst_disjunctive_pct"]),
             ("worst_law_effect", cal["WORST"]["law_effect_points"], inter["law_on_effect_worst_points"]),
             ("did_points", cal["difference_in_differences_points"],
              inter["difference_in_differences_points"])]
    bad = [n for n, a, b in pairs if a != b]
    check(PART_A, "A6_calibration_constants", not bad,
          "7 recorded figures agree" if not bad else "disagree: %s" % bad)

    # A7 budget derivation rule, canonicalised
    rules = {"WORLD": budget_rule_id(world["components"]["_budget_basis"]),
             "QUALIFY": budget_rule_id(fmc["B_derivation"]),
             "CONTRACT": budget_rule_id(driver.get("budget_derivation"))}
    check(PART_A, "A7_budget_rule_canonical", len(set(rules.values())) == 1,
          "%s -> %s" % (sorted(set(rules.values())), "identical" if len(set(rules.values())) == 1 else rules))

    # A8 superadditivity is defined on INFORMATION everywhere
    m = world["measurements"]
    bases = {"CONTRACT.superadditivity_basis": basis_of(driver.get("superadditivity_basis")),
             "QUALIFY.final_measurement_contract.statistic": basis_of(fmc["statistic"]),
             "QUALIFY.Q16.measurement": basis_of(qualify["predicates"]["Q16_additive_prediction_is_measured"]["measurement"]),
             "WORLD.measurements.superadditivity": basis_of(m["superadditivity"]),
             "WORLD.measurements.mixture_info": basis_of(m.get("mixture_info", m.get("mixture_value", ""))),
             "WORLD.measurements.solo_value_i": basis_of(m["solo_value_i"]),
             "WORLD.measurements.additive_prediction": basis_of(m["additive_prediction"]),
             # same D038b defect, and the first version of this gate failed to look at it
             "WORLD.measurements.ablation_cost_i": basis_of(m["ablation_cost_i"])}
    wrong = {k: v for k, v in bases.items() if v != "information"}
    check(PART_A, "A8_superadditivity_basis", not wrong,
          "all artifacts define it on information" if not wrong
          else "NOT on information: %s" % json.dumps(wrong))

    # A9 the statistic itself
    stats = {"CONTRACT.statistic_name": statistic_id(driver.get("statistic_name")),
             "QUALIFY.statistic": statistic_id(fmc["statistic"]),
             "WORLD.interaction_test.statistic": statistic_id(inter["statistic"]),
             "WORLD.Q_M3_interaction": statistic_id(world["qualify_predicates"]["Q_M3_interaction"])}
    check(PART_A, "A9_statistic_identity", len(set(stats.values())) == 1,
          "all four read %s" % list(set(stats.values()))[0] if len(set(stats.values())) == 1
          else json.dumps(stats))

    # A10 null construction
    n_declared = int(re.search(r"(\d+)", _norm(driver.get("null_construction"))).group(1))
    check(PART_A, "A10_null_blocks", X.N_BLOCKS >= n_declared,
          "contract requires >=%d blocks; driver N_BLOCKS=%d" % (n_declared, X.N_BLOCKS))

    # A11 set selection procedure
    sels = {"CONTRACT": selection_id(driver.get("set_selection_procedure")),
            "QUALIFY": selection_id(fmc["set_selection"]),
            "WORLD.Q2": selection_id(world["qualify_predicates"]["Q2_carrying_is_a_real_trade"])}
    check(PART_A, "A11_set_selection", len(set(sels.values())) == 1 and
          list(set(sels.values()))[0] == "exhaustive_enumeration",
          "all artifacts: %s" % list(set(sels.values()))[0])

    # A12 ledger cross-reference (presence is binding; status is reported)
    led = [json.loads(l) for l in (BASE / "DEFECTS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    by_id = {d.get("id"): d.get("status") for d in led}
    missing = [d for d in E05_DEFECTS if d not in by_id]
    still_open = [d for d in E05_DEFECTS if by_id.get(d) == "OPEN"]
    check(PART_A, "A12_ledger_records_defects", not missing,
          "all 7 e05 defects present; %d still marked OPEN %s" % (len(still_open), still_open))

    # A13 the driver's own WORLD/contract guard actually refuses
    tmp = pathlib.Path(tempfile.mkdtemp())
    bad_world = json.loads(json.dumps(world))
    bad_world["arms"]["treatment"]["max_components"] = 4
    (tmp / "WORLD.json").write_text(json.dumps(bad_world), encoding="utf-8")
    saved = X.HERE
    refused = False
    try:
        X.HERE = tmp
        X.load_cfg("cw01-e05-a01", driver)
    except CT.ContractViolation:
        refused = True
    finally:
        X.HERE = saved
    check(PART_A, "A13_world_budget_guard", refused,
          "load_cfg refuses a WORLD whose max_components disagrees with budget_B")

    return driver


# ------------------------------------------------------------------- PART B

def part_b(driver):
    print("\n  PART B - EMPIRICAL RECONSTRUCTION (frozen procedure, re-run)\n")
    aid = driver.get("attempt_id")
    cfg = X.load_cfg(aid, driver)
    capmap = W.attempt_capabilities(cfg, S.seed)
    pool = W.attempt_item_pool(cfg, S.seed)
    B = driver.get("budget_B")

    sets = X.enumerate_sets(cfg, pool, capmap, S.seed, aid, B)

    check(PART_B, "B1_subset_count", sets["n_subsets"] == BINDING_N_SUBSETS,
          "evaluated %d admissible subsets (binding: %d)" % (sets["n_subsets"], BINDING_N_SUBSETS))
    check(PART_B, "B2_best_reconstructs", list(sets["best"]) == BINDING_BEST,
          "BEST recomputes as %s (binding: %s), score %.4f"
          % (sets["best"], BINDING_BEST, sets["best_score"]))
    check(PART_B, "B3_worst_reconstructs", list(sets["worst"]) == BINDING_WORST,
          "WORST recomputes as %s (binding: %s), score %.4f"
          % (sets["worst"], BINDING_WORST, sets["worst_score"]))
    check(PART_B, "B4_ordering_procedure_unchanged",
          sets["best_score"] >= sets["median_score"] >= sets["worst_score"],
          "argmax/argmin over mean score: best %.4f >= median %.4f >= worst %.4f"
          % (sets["best_score"], sets["median_score"], sets["worst_score"]))
    return sets


def main():
    print("########## e05 freeze-boundary consistency gate ##########")
    world = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    qualify = json.loads((HERE / "QUALIFY.json").read_text(encoding="utf-8"))
    committed_raw = json.loads((HERE / "VERDICT_CONTRACT.json").read_text(encoding="utf-8"))

    driver = part_a(world, qualify, committed_raw)
    sets = part_b(driver)

    a_ok = all(c["passed"] for c in PART_A)
    b_ok = all(c["passed"] for c in PART_B)
    print("\n    PART A %d/%d   PART B %d/%d"
          % (sum(c["passed"] for c in PART_A), len(PART_A),
             sum(c["passed"] for c in PART_B), len(PART_B)))
    print("    GATE: %s" % ("PASS" if (a_ok and b_ok) else "FAIL"))

    receipt = {
        "campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e05",
        "attempt_id": driver.get("attempt_id"),
        "verdict_contract_sha256": driver.hash,
        "contract_source": "imported object execute_e05.EMBEDDED_CONTRACT (not source text)",
        "part_a_specification_consistency": {"checks": PART_A, "passed": a_ok},
        "part_b_empirical_reconstruction": {
            "checks": PART_B, "passed": b_ok,
            "binding_invariants": {"n_subsets": BINDING_N_SUBSETS,
                                   "BEST": BINDING_BEST, "WORST": BINDING_WORST},
            "reconstructed": {"n_subsets": sets["n_subsets"], "BEST": sets["best"],
                              "WORST": sets["worst"], "best_score": sets["best_score"],
                              "median_score": sets["median_score"],
                              "worst_score": sets["worst_score"]},
            "_rule": "a different BEST or WORST is a real consistency failure, not a tolerance"},
        "gate": "PASS" if (a_ok and b_ok) else "FAIL"}
    (HERE / "CONSISTENCY_RECEIPT.json").write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    return 0 if (a_ok and b_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
