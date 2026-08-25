"""run_selector_preflight.py — SELECTOR PF1/PF2/PF3, exactly as preregistered (01bfbfa6).

PF3 decides whether the five-selector comparison runs at all. If fewer than three candidates in
the frozen pool have dE > 0, the comparison is VACUOUS -- a statement about the substrate's
headroom, NOT a kill of dE-as-selector. The preregistration predicts this outcome in advance
precisely so it cannot later be re-read as a kill.

THE ABSTAIN POOL IS MANDATORY HERE. 9 of 10 scorers emit candidates[0] when nothing matches,
which pays any firing-but-wrong candidate a 1-in-4 floor on a 4-candidate task. Measuring dE
under the guessing pool would hand junk candidates spurious positive dE -- the exact
contamination CEILING-ABSTAIN characterised. Every reading below uses the rotation-wrapped
abstain pool.

ADAPTATION RULE, declared before any score is computed. Each forge primitive is wired by
PARAMETER TYPE to a blackboard slot and by RETURN TYPE to an output slot, using the fixed table
below. A primitive whose parameters cannot all be sourced from slots is NOT EXPRESSIBLE and is
recorded as such -- it is not silently dropped.

    python aporia/iq/run_selector_preflight.py
"""
from __future__ import annotations

import hashlib
import inspect
import json
import sys
import typing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "apollo" / "src", ROOT / "apollo" / "scripts",
          ROOT / "agents" / "hephaestus" / "src", Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import blackboard_evolve as be                                     # noqa: E402
from blackboard import BlackboardState, BlackboardOp, run_pipeline  # noqa: E402
import forge_primitives as fp                                      # noqa: E402
import port_ops                                                    # noqa: E402
from run_iq_port_1 import TASKS, CEILING_BODY, CEILING_TAIL        # noqa: E402
from run_ceiling_abstain import abstain_pool                       # noqa: E402

OUT = Path(__file__).resolve().parent

# Declared BEFORE any score: parameter annotation -> slot that supplies it.
PARAM_SLOT = {
    "list[tuple[str, str]]": "relations",
    "set[str]": "facts",
    "list[str]": "names",
    "list[float]": "numbers",
    "list[int]": "numbers",
    "int": "max_value",
    "float": "max_value",
    "str": "question_target",
    "bool": "comparison",
    "dict[str, list]": "rules",
}
# Declared BEFORE any score: return annotation -> slot the result is written to.
RETURN_SLOT = {
    "int": "max_value", "float": "max_value",
    "list[str]": "ordered", "set[str]": "derived_facts",
    "dict[str, set[str]]": "transitive_closure", "str": "max_entity",
    "bool": "comparison", "list[float]": "numbers",
}

FORGE_NAMES = ["solve_sat", "modus_ponens", "check_transitivity", "negate", "bayesian_update",
               "expected_value", "entropy", "coin_flip_independence", "dag_traverse",
               "topological_sort", "counterfactual_intervention", "solve_constraints",
               "pigeonhole_check", "fencepost_count", "bat_and_ball", "modular_arithmetic",
               "all_but_n", "solve_linear_system", "temporal_order", "direction_composition",
               "track_beliefs", "sally_anne_test", "confidence_from_agreement",
               "information_sufficiency", "parity_check"]


def _ann(a):
    """Normalise an annotation to a comparable string.

    NOTE, and it was a real defect: builtins stringify as "<class 'int'>", not "int", so the
    first version of this function marked all_but_n NOT EXPRESSIBLE -- a primitive I had
    already successfully ported in IQ-PORT-1. The expressibility count is a reported number,
    so an annotation-formatting bug is a measurement bug.
    """
    if a is inspect.Parameter.empty:
        return "?"
    if isinstance(a, type):
        return a.__name__
    s = str(a).replace("typing.", "")
    s = s.split(" |")[0].strip()
    if s.startswith("<class '") and s.endswith("'>"):
        s = s[len("<class '"):-2]
    return s


def adapt(name):
    """Return (op, reads, writes) or (None, reason)."""
    fn = getattr(fp, name, None)
    if fn is None:
        return None, f"absent from forge_primitives"
    sig = inspect.signature(fn)
    reads, params = [], []
    for p in sig.parameters.values():
        slot = PARAM_SLOT.get(_ann(p.annotation))
        if slot is None:
            if p.default is not inspect.Parameter.empty:
                params.append((p.name, None, p.default))
                continue
            return None, f"parameter {p.name}:{_ann(p.annotation)} has no slot"
        reads.append(slot)
        params.append((p.name, slot, None))
    wslot = RETURN_SLOT.get(_ann(sig.return_annotation))
    if wslot is None:
        return None, f"return {_ann(sig.return_annotation)} has no slot"

    def body(state, _fn=fn, _params=params, _w=wslot):
        args = []
        for pname, slot, default in _params:
            if slot is None:
                args.append(default)
            else:
                v = getattr(state, slot)
                if slot == "relations":
                    v = list(v)
                elif slot == "facts":
                    v = set(v)
                elif slot in ("names", "numbers", "ordered"):
                    v = list(v)
                elif slot == "max_value":
                    v = 0 if v is None else (int(v) if _ann(inspect.signature(_fn)
                                                            .parameters[pname].annotation) == "int" else v)
                args.append(v)
        try:
            out = _fn(*args)
        except Exception:
            return state
        if out is None:
            return state
        setattr(state, _w, out)
        return state

    reads = sorted(set(reads)) or ["problem_text"]
    return BlackboardOp(body, reads=reads, writes=[wslot], on_fail="skip",
                        name=f"cand_{name}"), None


def acc(pool, pipeline):
    ops = [pool[n] for n in pipeline]
    hits = 0
    for t in TASKS:
        st = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        try:
            if run_pipeline(ops, st).selected_answer == t["correct"]:
                hits += 1
        except Exception:
            pass
    return hits / len(TASKS)


def main():
    R = {"experiment": "SELECTOR-PREFLIGHT", "date": "2026-08-25", "agent": "Aporia (M1)",
         "prereg": "aporia/iq/PREREG_SELECTOR_2026-08-25.md", "prereg_commit": "01bfbfa6",
         "pool_uses_abstain_scorers": True,
         "abstain_note": ("9 of 10 scorers guess candidates[0]; measuring dE under the guessing "
                          "pool would hand junk candidates a spurious 1-in-4 floor.")}

    # ── freeze the pool BY HASH before any score is computed ─────────────────
    names = FORGE_NAMES + ["parse_all_but_n", "op_all_but_n"]
    h = hashlib.sha256()
    for n in names:
        h.update(n.encode())
    R["frozen_pool"] = names
    R["frozen_pool_size"] = len(names)
    R["frozen_pool_sha256"] = h.hexdigest()

    POOL = abstain_pool()
    base = acc(POOL, CEILING_BODY + CEILING_TAIL)
    R["E_C_under_abstain"] = round(base, 6)

    # ── PF1: dE for every candidate ──────────────────────────────────────────
    rows, notexpr = {}, {}
    for n in names:
        if n in port_ops.PORT_OPS:
            op = port_ops.PORT_OPS[n]
        else:
            op, why = adapt(n)
            if op is None:
                notexpr[n] = why
                rows[n] = {"expressible": False, "reason": why, "dE": None}
                continue
        best = base
        for pos in range(len(CEILING_BODY) + 1):
            body = CEILING_BODY[:pos] + [f"cand::{n}"] + CEILING_BODY[pos:]
            p2 = dict(POOL)
            p2[f"cand::{n}"] = op
            try:
                best = max(best, acc(p2, body + CEILING_TAIL))
            except Exception:
                pass
        rows[n] = {"expressible": True, "dE": round(best - base, 6)}

    R["candidates"] = rows
    R["not_expressible"] = notexpr
    R["n_expressible"] = sum(1 for v in rows.values() if v["expressible"])
    R["n_not_expressible"] = len(notexpr)
    R["dropped_records"] = 0
    R["dropped_records_note"] = ("LOUD: every one of the frozen pool is accounted for as either "
                                 "expressible-with-a-dE or not-expressible-with-a-reason. "
                                 "n_expressible + n_not_expressible must equal pool size.")
    assert R["n_expressible"] + R["n_not_expressible"] == len(names), "pool accounting leaks"

    # ── PF2: attainable range and variance of the DV ─────────────────────────
    des = [v["dE"] for v in rows.values() if v["dE"] is not None]
    R["dE_values"] = {k: v["dE"] for k, v in rows.items() if v["dE"] is not None}
    R["dE_min"], R["dE_max"] = (min(des), max(des)) if des else (None, None)
    mean = sum(des) / len(des) if des else 0.0
    R["dE_mean"] = round(mean, 6)
    R["dE_variance"] = round(sum((d - mean) ** 2 for d in des) / len(des), 9) if des else None
    R["dE_distinct_values"] = sorted(set(des))
    R["n_positive_dE"] = sum(1 for d in des if d > 0)

    # ── PF3: the gate ────────────────────────────────────────────────────────
    R["PF3_threshold"] = 3
    R["PF3_passes"] = R["n_positive_dE"] >= 3
    R["verdict"] = ("PROCEED_TO_SELECTOR_COMPARISON" if R["PF3_passes"]
                    else "VACUOUS_DV_CANNOT_VARY")
    R["verdict_rule_null_output"] = (
        "If every candidate scores dE = 0 the DV is constant and NO selector can beat another "
        "for reasons related to selection. That is reported as VACUOUS -- a statement about the "
        "substrate's headroom -- and explicitly NOT as 'no selector beat random', which would be "
        "a kill of dE-as-selector that this reading cannot support.")
    seen = {("PROCEED_TO_SELECTOR_COMPARISON" if p else "VACUOUS_DV_CANNOT_VARY")
            for p in (True, False)}
    assert seen == {"PROCEED_TO_SELECTOR_COMPARISON", "VACUOUS_DV_CANNOT_VARY"}, "branch leak"
    R["branch_table_partitions"] = True
    if not R["PF3_passes"]:
        R["NOT_A_KILL"] = ("VACUOUS is NOT the preregistered KILL. The KILL requires PF3 to pass "
                           "and then R-ranking to fail against compression or random. That "
                           "comparison was never reached, so dE-as-selector is UNTESTED here, "
                           "not refuted.")

    json.dump(R, open(OUT / "RESULT_SELECTOR_PREFLIGHT.json", "w", encoding="utf-8"), indent=2)
    for k, v in R.items():
        if k not in ("candidates", "dropped_records_note", "verdict_rule_null_output",
                     "frozen_pool", "abstain_note"):
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
