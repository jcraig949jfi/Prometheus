"""run_iq_port_1.py — IQ-PORT-1 measurement harness.

Runs every falsifier preregistered in PREREG_IQ_PORT_1_2026-08-25.md, in order, and emits
one terminal state. No number here is interpreted by a model: the terminal state is a
deterministic predicate over measured quantities.

    python aporia/iq/run_iq_port_1.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "apollo" / "src"
SCRIPTS = ROOT / "apollo" / "scripts"
for p in (str(SRC), str(SCRIPTS), str(ROOT / "agents" / "hephaestus" / "src"),
          str(Path(__file__).resolve().parent)):
    if p not in sys.path:
        sys.path.insert(0, p)

import blackboard_evolve as be            # noqa: E402  -- the frozen pool C
from blackboard import BlackboardState, run_pipeline  # noqa: E402
import forge_primitives as fp             # noqa: E402
import port_ops                            # noqa: E402

OUT = Path(__file__).resolve().parent
PREREG_HASH = "10fa10db9989eb3a79c2039d18b748a83e93f751578ec6d0a0e12717eb0fa5ae"

HASHED_FILES = [
    "apollo/src/blackboard.py", "apollo/src/blackboard_evolve.py",
    "apollo/src/blackboard_ops.py", "apollo/src/blackboard_ops_v2.py",
    "apollo/src/blackboard_ops_r2.py", "apollo/src/blackboard_ops_compare.py",
    "apollo/data/clean_canary_v01.json", "apollo/scripts/composition_gauntlet.py",
    "apollo/scripts/inference_canary.py", "apollo/scripts/cross_tier_canary.py",
    "agents/hephaestus/src/forge_primitives.py",
]

CEILING_BODY = ["parse_comparison", "parse_which_extreme", "parse_box_items",
                "op_aggregate_quantities", "parse_rules", "parse_ordinal", "forward_chain",
                "parse_names_and_relations", "relations_from_facts", "op_build_ordering"]
CEILING_TAIL = ["score_by_extreme_number__g", "score_by_aggregate__g",
                "score_by_derivability__g", "score_by_comparison__g", "select_nth__g"]

# The port must run BEFORE op_aggregate_quantities, which consumes `counts`.
PORTED_BODY = ["parse_comparison", "parse_which_extreme", "parse_box_items",
               "parse_all_but_n", "op_all_but_n",
               "op_aggregate_quantities", "parse_rules", "parse_ordinal", "forward_chain",
               "parse_names_and_relations", "relations_from_facts", "op_build_ordering"]


def evaluator_hash():
    h = hashlib.sha256()
    for f in HASHED_FILES:
        h.update(f.encode())
        h.update(hashlib.sha256((ROOT / f).read_bytes()).hexdigest().encode())
    return h.hexdigest()


def build_battery():
    canary = json.loads((ROOT / "apollo" / "data" / "clean_canary_v01.json")
                        .read_text(encoding="utf-8"))["tasks"]
    from composition_gauntlet import build_synthetic_canary
    from inference_canary import build_inference_canary
    from cross_tier_canary import build_cross_tier_canary
    subs = [("canary", canary), ("synth", build_synthetic_canary(n_each=15)),
            ("inference", build_inference_canary(n=20)),
            ("cross_tier", build_cross_tier_canary(n=20))]
    tasks, bounds, off = [], [], 0
    for name, ts in subs:
        for t in ts:
            t = dict(t)
            t["_subset"] = name
            tasks.append(t)
        bounds.append((name, off, off + len(ts)))
        off += len(ts)
    return tasks, bounds


TASKS, BOUNDS = build_battery()
ABN_IDX = [i for i, t in enumerate(TASKS)
           if t["_subset"] == "canary" and t.get("category") == "all_but_n"]


def resolve(name, pool):
    return pool[name]


def make_pool(extra=None):
    """C, or C u {p}. C itself is never mutated."""
    pool = {n: op for n, (op, _r) in be.REGISTRY.items()}
    if extra:
        pool.update(extra)
    return pool


def acc(pipeline_names, pool, seed_state=None):
    ops = [resolve(n, pool) for n in pipeline_names]
    hits, per_task = 0, []
    for t in TASKS:
        st = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        if seed_state is not None:
            seed_state(st, t)
        try:
            out = run_pipeline(ops, st)
            ans = out.selected_answer
        except Exception as e:
            ans = f"<EXC {type(e).__name__}>"
        ok = (ans == t["correct"])
        hits += ok
        per_task.append(ok)
    return hits / len(TASKS), per_task


def subset_acc(per_task):
    return {name: round(sum(per_task[a:b]) / (b - a), 4) for name, a, b in BOUNDS}


def cat_acc(per_task, subset, category):
    idx = [i for i, t in enumerate(TASKS)
           if t["_subset"] == subset and t.get("category") == category]
    return sum(per_task[i] for i in idx), len(idx)


def main():
    R = {"experiment": "IQ-PORT-1", "date": "2026-08-25", "agent": "Aporia (M1)",
         "prereg": "aporia/iq/PREREG_IQ_PORT_1_2026-08-25.md",
         "intervention_class": "PORT_EXISTING_CAPABILITY",
         "class_fixed_before_execution": True}

    # ── 0. evaluator-counterfeit gate ────────────────────────────────────────
    h = evaluator_hash()
    R["evaluator_hash"] = h
    R["evaluator_hash_matches_prereg"] = (h == PREREG_HASH)
    if h != PREREG_HASH:
        R["verdict"] = "INADMISSIBLE_EVALUATOR_DRIFT"
        json.dump(R, open(OUT / "RESULT_IQ_PORT_1.json", "w", encoding="utf-8"), indent=2)
        print("INADMISSIBLE: evaluator drifted from prereg hash")
        return

    # ── 1. baseline E(C) ─────────────────────────────────────────────────────
    C = make_pool()
    base_acc, base_pt = acc(CEILING_BODY + CEILING_TAIL, C)
    R["E_C"] = round(base_acc, 6)
    R["E_C_by_subset"] = subset_acc(base_pt)
    R["single_primitive_baseline"] = be._single_primitive_baseline(TASKS)
    # reordering control: the ported body with the new ops deleted must still be 0.8333,
    # otherwise any gain could be an artifact of moving op_aggregate_quantities.
    reorder = [n for n in PORTED_BODY if n not in port_ops.PORT_OPS] + CEILING_TAIL
    reorder_acc, _ = acc(reorder, C)
    R["reorder_control_acc"] = round(reorder_acc, 6)
    R["reorder_control_ok"] = abs(reorder_acc - base_acc) < 1e-12

    # ── 2. slot-producer audit: does anything in C write `quantities`? ───────
    producers = sorted(n for n, (op, _r) in be.REGISTRY.items() if "quantities" in op.writes)
    R["quantities_producers_in_C"] = producers

    # ── 3. footprint (P1) ────────────────────────────────────────────────────
    pair = [resolve(n, port_ops.PORT_OPS) for n in ("parse_all_but_n", "op_all_but_n")]
    footprint = []
    for i, t in enumerate(TASKS):
        st = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        before = (deepcopy(st.quantities), deepcopy(st.counts))
        out = run_pipeline(pair, st)
        if (out.quantities, out.counts) != before:
            footprint.append(i)
    R["footprint_indices"] = footprint
    R["footprint_size"] = len(footprint)
    R["footprint_equals_all_but_n"] = (footprint == ABN_IDX)
    R["all_but_n_indices"] = ABN_IDX

    # ── 4. exhibited pipeline, DeltaE_lower (P2-P5) ──────────────────────────
    CP = make_pool(port_ops.PORT_OPS)
    port_acc, port_pt = acc(PORTED_BODY + CEILING_TAIL, CP)
    R["E_C_union_p_exhibited"] = round(port_acc, 6)
    R["E_by_subset_ported"] = subset_acc(port_pt)
    delta_E = port_acc - base_acc          # unrounded; rounding is for the report only
    R["delta_E_lower"] = round(delta_E, 6)
    delta_E_upper = len(footprint) / len(TASKS)
    R["delta_E_upper_bound"] = round(delta_E_upper, 6)
    R["delta_E_is_exact"] = abs(delta_E - delta_E_upper) < 1e-12
    R["delta_E_upper_strength"] = "SUPPORTED (requires g-minus-new-ops valid over C; " \
                                  "checked for the exhibited pipeline only)"
    k, n = cat_acc(port_pt, "canary", "all_but_n")
    R["all_but_n_solved_after_port"] = f"{k}/{n}"
    R["single_primitive_baseline_after"] = be._single_primitive_baseline(TASKS)
    # no subset may regress
    R["no_regression"] = all(R["E_by_subset_ported"][s] >= R["E_C_by_subset"][s]
                             for s, _a, _b in BOUNDS)

    # ── 5. adapter-vs-rewrite: monkeypatch the forge kernel (P9) ─────────────
    real = fp.all_but_n
    try:
        fp.all_but_n = lambda total, n: 999999
        patched_acc, patched_pt = acc(PORTED_BODY + CEILING_TAIL, CP)
    finally:
        fp.all_but_n = real
    kp, kn = cat_acc(patched_pt, "canary", "all_but_n")
    R["delegation_probe"] = {"acc_with_kernel_broken": round(patched_acc, 6),
                             "all_but_n_solved": f"{kp}/{kn}"}
    R["adapter_verdict"] = "ADAPTER" if (kp == 0 and abs(patched_acc - base_acc) < 1e-12) \
        else "REWRITE"

    # ── 6. state injection: INJ-A / INJ-B (parse counterfeit) ────────────────
    def seed_quantities(st, t):
        if t["_subset"] == "canary" and t.get("category") == "all_but_n":
            s2 = BlackboardState(problem_text=t["prompt"], candidates=[])
            port_ops.parse_all_but_n(s2)
            st.quantities = dict(s2.quantities)

    def seed_counts(st, t):
        if t["_subset"] == "canary" and t.get("category") == "all_but_n":
            s2 = BlackboardState(problem_text=t["prompt"], candidates=[])
            port_ops.parse_all_but_n(s2)
            st.counts = {"remaining": {"count": s2.quantities["total"] - s2.quantities["removed"],
                                       "provenance": "INJECTED"}}

    inj_a_acc, inj_a_pt = acc(CEILING_BODY + CEILING_TAIL, C, seed_state=seed_quantities)
    inj_b_acc, inj_b_pt = acc(CEILING_BODY + CEILING_TAIL, C, seed_state=seed_counts)
    a_k, _ = cat_acc(inj_a_pt, "canary", "all_but_n")
    b_k, _ = cat_acc(inj_b_pt, "canary", "all_but_n")
    R["INJ_A_all_but_n_solved"] = a_k
    R["INJ_B_all_but_n_solved"] = b_k
    R["INJ_A_battery_acc"] = round(inj_a_acc, 6)
    R["INJ_B_battery_acc"] = round(inj_b_acc, 6)

    assert 0 <= a_k <= 5 and 0 <= b_k <= 5, "injection counts outside the enumerated range"
    if a_k == 5:
        branch = "B1_PARSE_ADAPTER"
    elif 1 <= a_k <= 4:
        branch = "B2_PARTIAL"
    elif a_k == 0 and b_k == 5:
        branch = "B3_PORT_WITH_PARSER_DEPENDENCY"
    else:
        branch = "B4_NEW_ROUTING_REQUIRED"
    R["injection_branch"] = branch
    # partition assert: every (a,b) in 0..5 x 0..5 maps to exactly one branch
    seen = set()
    for a in range(6):
        for b in range(6):
            got = ("B1_PARSE_ADAPTER" if a == 5 else
                   "B2_PARTIAL" if 1 <= a <= 4 else
                   "B3_PORT_WITH_PARSER_DEPENDENCY" if (a == 0 and b == 5) else
                   "B4_NEW_ROUTING_REQUIRED")
            seen.add((a, b, got))
    assert len(seen) == 36, "branch table does not partition the 36 cells"
    R["branch_table_partitions_36_cells"] = True

    # ── 7. mutation battery (answer counterfeit) ─────────────────────────────
    muts = {}
    for name, op in port_ops.MUTANTS.items():
        pool = make_pool({"parse_all_but_n": port_ops.parse_all_but_n, "op_all_but_n": op})
        m_acc, m_pt = acc(PORTED_BODY + CEILING_TAIL, pool)
        mk, _ = cat_acc(m_pt, "canary", "all_but_n")
        muts[name] = {"acc": round(m_acc, 6), "delta_E": round(m_acc - base_acc, 6),
                      "all_but_n_solved": mk}
    R["mutants"] = muts
    R["all_mutants_zero_delta"] = all(abs(v["delta_E"]) < 1e-12 for v in muts.values())

    # ── 8. leave-one-out knockout (composition counterfeit) ──────────────────
    ko_raw = {}
    full = PORTED_BODY + CEILING_TAIL
    for name in full:
        red = [n for n in full if n != name]
        k_acc, _ = acc(red, CP)
        ko_raw[name] = k_acc - port_acc          # unrounded
    ko = {k: round(v, 6) for k, v in ko_raw.items()}
    R["knockout_delta"] = ko
    R["knockout_port_load_bearing"] = (
        abs(ko_raw["op_all_but_n"] + delta_E) < 1e-12 and
        abs(ko_raw["parse_all_but_n"] + delta_E) < 1e-12)
    R["decorative_ops_in_exhibited_pipeline"] = sorted(n for n, d in ko_raw.items()
                                                       if abs(d) < 1e-12)

    # ── 9. terminal state: deterministic predicate, no interpretation ────────
    checks = {
        "P1_footprint_exactly_5_all_but_n": R["footprint_equals_all_but_n"],
        "P2_battery_0.8750": abs(port_acc - 0.875) < 1e-9,
        "P3_canary_0.7000": abs(R["E_by_subset_ported"]["canary"] - 0.70) < 1e-9,
        "P4_deltaE_5_over_120": abs(delta_E - 5 / 120) < 1e-12,
        "P5_single_primitive_baseline_zero": R["single_primitive_baseline_after"] == 0.0,
        "P6_knockout_op_all_but_n": abs(ko_raw["op_all_but_n"] + delta_E) < 1e-12,
        "P7_knockout_parse_all_but_n": abs(ko_raw["parse_all_but_n"] + delta_E) < 1e-12,
        "P8_all_mutants_zero": R["all_mutants_zero_delta"],
        "P9_delegation_breaks_on_patch": R["adapter_verdict"] == "ADAPTER",
        "reorder_control": R["reorder_control_ok"],
        "no_subset_regression": R["no_regression"],
        "branch_is_B3": branch == "B3_PORT_WITH_PARSER_DEPENDENCY",
    }
    R["checks"] = checks
    R["novelty_claim"] = "ZERO — class PORT_EXISTING_CAPABILITY establishes nothing about " \
                         "synthesis, discovery, abstraction learning, or library growth."
    if R["adapter_verdict"] == "REWRITE":
        R["verdict"] = "PARK_RECLASSIFIED_AS_MINT"
    elif branch != "B3_PORT_WITH_PARSER_DEPENDENCY":
        R["verdict"] = f"PARK_{branch}"
    elif all(checks.values()):
        R["verdict"] = "ADVANCE"
    else:
        R["verdict"] = "REDESIGN"
    R["failed_checks"] = sorted(k for k, v in checks.items() if not v)

    json.dump(R, open(OUT / "RESULT_IQ_PORT_1.json", "w", encoding="utf-8"), indent=2)
    for k, v in R.items():
        if k not in ("footprint_indices", "all_but_n_indices"):
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
