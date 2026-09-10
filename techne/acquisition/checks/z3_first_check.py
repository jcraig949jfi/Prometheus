"""Z3 first useful check. Runs INSIDE the isolated env; imports nothing from techne.

    <tool_cache>/envs/h0h5_tools/Scripts/python techne/acquisition/checks/z3_first_check.py

Prints one JSON object on the last line of stdout.

What the design requires of this check:
    "Known SAT/UNSAT/UNKNOWN handling; independently validate a returned counterexample."
    "For Z3, handle unknown and resource exhaustion distinctly."

The named consumer is H1's Boolean oracle cross-check, so the check is shaped like that
consumer: two Boolean circuits, a solver asked for a DISTINGUISHING input, and a pure
Python truth-table evaluator -- which shares no code with z3 -- deciding whether the
witness really distinguishes them.

One case exists only to keep the validator honest: NEGATIVE_CONTROL feeds the validator a
deliberately wrong witness. A validator that cannot reject is not a validator, and a
check whose oracle always passes measures nothing.
"""
from __future__ import annotations

import itertools
import json
import sys
import time

import z3

N_VARS = 4


# ---------------------------------------------------------------- independent evaluator
def evaluate(circ, bits: tuple[int, ...]) -> int:
    """Pure Python. No z3. This is the independent oracle.

    Circuit grammar: int (variable index) | ('not', a) | ('and', a, b) | ('or', a, b)
    | ('xor', a, b) | 0/1 via ('const', v).
    """
    if isinstance(circ, int):
        return bits[circ]
    op = circ[0]
    if op == "const":
        return int(circ[1])
    if op == "not":
        return 1 - evaluate(circ[1], bits)
    a = evaluate(circ[1], bits)
    b = evaluate(circ[2], bits)
    if op == "and":
        return a & b
    if op == "or":
        return a | b
    if op == "xor":
        return a ^ b
    raise ValueError(f"unknown op {op!r}")


def truth_table(circ, n: int = N_VARS) -> list[int]:
    return [evaluate(circ, bits) for bits in itertools.product((0, 1), repeat=n)]


def differing_inputs(c1, c2, n: int = N_VARS) -> list[tuple[int, ...]]:
    return [bits for bits in itertools.product((0, 1), repeat=n)
            if evaluate(c1, bits) != evaluate(c2, bits)]


# ---------------------------------------------------------------- z3 translation
def to_z3(circ, xs):
    if isinstance(circ, int):
        return xs[circ]
    op = circ[0]
    if op == "const":
        return z3.BoolVal(bool(circ[1]))
    if op == "not":
        return z3.Not(to_z3(circ[1], xs))
    a, b = to_z3(circ[1], xs), to_z3(circ[2], xs)
    return {"and": z3.And, "or": z3.Or, "xor": z3.Xor}[op](a, b)


def ask_distinguishing(c1, c2, timeout_ms: int = 5000) -> dict:
    xs = [z3.Bool(f"x{i}") for i in range(N_VARS)]
    s = z3.Solver()
    s.set("timeout", timeout_ms)
    s.add(z3.Xor(to_z3(c1, xs), to_z3(c2, xs)))
    t0 = time.perf_counter()
    r = s.check()
    dt = time.perf_counter() - t0
    out = {"z3_result": str(r), "reason_unknown": s.reason_unknown() if str(r) == "unknown" else None,
           "seconds": round(dt, 4), "witness": None}
    if str(r) == "sat":
        m = s.model()
        out["witness"] = tuple(1 if z3.is_true(m.eval(x, model_completion=True)) else 0
                               for x in xs)
    return out


# ---------------------------------------------------------------- the cases
def case_sat_counterexample() -> dict:
    # Differ on exactly the inputs where x2=1 and x3=1: C1 has (x2 and x3), C2 has (x2 or x3).
    c1 = ("or", ("and", 0, 1), ("and", 2, 3))
    c2 = ("or", ("and", 0, 1), ("or", 2, 3))
    ask = ask_distinguishing(c1, c2)
    truth_diff = differing_inputs(c1, c2)
    w = ask["witness"]
    validated = w is not None and evaluate(c1, w) != evaluate(c2, w)
    return {
        "case": "SAT_WITH_INDEPENDENTLY_VALIDATED_COUNTEREXAMPLE",
        "expected_z3_result": "sat",
        "observed_z3_result": ask["z3_result"],
        "witness": list(w) if w else None,
        "independent_validator": {
            "c1_value_at_witness": evaluate(c1, w) if w else None,
            "c2_value_at_witness": evaluate(c2, w) if w else None,
            "witness_really_distinguishes": validated,
            "shares_code_with_z3": False,
        },
        "exhaustive_cross_check": {
            "n_inputs": 2 ** N_VARS,
            "n_differing_by_enumeration": len(truth_diff),
            "witness_in_enumerated_set": (tuple(w) in truth_diff) if w else None,
        },
        "pass": ask["z3_result"] == "sat" and validated and (tuple(w) in truth_diff),
        "seconds": ask["seconds"],
    }


def case_unsat_equivalence() -> dict:
    # De Morgan: not(a and b)  ==  (not a) or (not b). Syntactically different, same function.
    c1 = ("not", ("and", 0, 1))
    c2 = ("or", ("not", 0), ("not", 1))
    ask = ask_distinguishing(c1, c2)
    diff = differing_inputs(c1, c2)
    return {
        "case": "UNSAT_EQUIVALENCE",
        "expected_z3_result": "unsat",
        "observed_z3_result": ask["z3_result"],
        "exhaustive_cross_check": {
            "n_inputs": 2 ** N_VARS,
            "n_differing_by_enumeration": len(diff),
            "agrees_everywhere": len(diff) == 0,
        },
        "pass": ask["z3_result"] == "unsat" and len(diff) == 0,
        "seconds": ask["seconds"],
    }


def _pigeonhole(s, n: int = 12, m: int = 11) -> None:
    """n pigeons into m holes, n > m: unsatisfiable, and expensive for a CDCL solver.
    Used only to MAKE the solver run out of budget, never to test unsat."""
    P = [[z3.Bool(f"p_{i}_{j}") for j in range(m)] for i in range(n)]
    for i in range(n):
        s.add(z3.Or(P[i]))
    for j in range(m):
        for i in range(n):
            for k in range(i + 1, n):
                s.add(z3.Or(z3.Not(P[i][j]), z3.Not(P[k][j])))


def case_unknown_timeout() -> dict:
    s = z3.Solver()
    s.set("timeout", 50)
    _pigeonhole(s)
    t0 = time.perf_counter()
    r = s.check()
    reason = s.reason_unknown()
    return {
        "case": "UNKNOWN_BY_WALL_CLOCK_EXHAUSTION",
        "expected_z3_result": "unknown",
        "observed_z3_result": str(r),
        "reason_unknown": reason,
        "limit_set": {"timeout_ms": 50},
        "distinct_from_incompleteness": reason == "timeout",
        "pass": str(r) == "unknown" and reason == "timeout",
        "seconds": round(time.perf_counter() - t0, 4),
        "consumer_rule": "An adapter MUST surface this as a third outcome. Coercing it to "
                         "unsat would report 'no counterexample exists' when the truth is "
                         "'we stopped looking'.",
    }


def case_unknown_rlimit() -> dict:
    s = z3.Solver()
    s.set("rlimit", 2000)
    _pigeonhole(s)
    t0 = time.perf_counter()
    r = s.check()
    reason = s.reason_unknown()
    return {
        "case": "UNKNOWN_BY_DETERMINISTIC_RESOURCE_EXHAUSTION",
        "expected_z3_result": "unknown",
        "observed_z3_result": str(r),
        "reason_unknown": reason,
        "limit_set": {"rlimit": 2000},
        "distinct_from_timeout": reason != "timeout",
        "why_this_matters": "rlimit is deterministic where wall-clock timeout is not. A "
                           "repeatability check across hosts must use rlimit; a timeout "
                           "makes the same query answerable on a fast host and unknown on "
                           "a slow one.",
        "pass": str(r) == "unknown" and reason == "max. resource limit exceeded",
        "seconds": round(time.perf_counter() - t0, 4),
    }


def case_unknown_incompleteness() -> dict:
    """Try to produce an `unknown` that is NOT a budget failure. Retained whether or not
    it fires: a negative result here is information the consumer needs."""
    tried = []
    a, b, c = z3.Ints("a b c")
    x, y = z3.Reals("x y")
    f = z3.Function("f", z3.IntSort(), z3.IntSort())
    xi = z3.Int("xi")
    candidates = [
        ("nonlinear_int_satisfiable", lambda s: s.add(a > 1, b > 1, c > 1,
                                                     a * b * c == 105, a + b + c == 15), {}),
        ("nonlinear_int_nl_disabled", lambda s: s.add(a > 1, b > 1, c > 1,
                                                     a * b * c == 105, a + b + c == 15),
         {"smt.arith.nl": False}),
        ("nonlinear_real_quintic", lambda s: s.add(x * x * x * x * x - 3 * x + 1 == 0, x > 0), {}),
        ("quantified_uf_nonlinear", lambda s: s.add(
            z3.ForAll([xi], f(xi * xi) > f(xi) + 1), f(0) == 0), {}),
        ("quantified_mbqi_off", lambda s: s.add(
            z3.ForAll([xi], f(xi * xi) > f(xi) + 1), f(0) == 0), {"smt.mbqi": False}),
        ("forall_exists_square", lambda s: s.add(
            z3.ForAll([xi], z3.Exists([y], y * y == z3.ToReal(xi)))), {}),
    ]
    for name, build, opts in candidates:
        s = z3.Solver()
        s.set("timeout", 4000)
        for k, v in opts.items():
            s.set(k, v)
        build(s)
        t0 = time.perf_counter()
        r = s.check()
        tried.append({"candidate": name, "options": opts, "result": str(r),
                      "reason_unknown": s.reason_unknown() if str(r) == "unknown" else None,
                      "seconds": round(time.perf_counter() - t0, 4)})
    fired = [t for t in tried if t["result"] == "unknown" and t["reason_unknown"] not in
             ("timeout", "max. resource limit exceeded")]
    return {
        "case": "UNKNOWN_BY_INCOMPLETENESS",
        "candidates_tried": tried,
        "observed": bool(fired),
        "pass": None,
        "verdict": ("OBSERVED" if fired else "NOT_OBSERVED_ON_THIS_BUILD"),
        "retained_negative_result": (
            "On z3 " + z3.get_version_string() + " none of these six candidates produced an "
            "`unknown` whose reason was anything other than a budget being exhausted. This is "
            "NOT a claim that z3 is complete; it is a measured statement about what this seat "
            "could elicit in four seconds per query. The consumer-facing consequence: on this "
            "build an `unknown` seen in practice is most likely a budget failure, and the "
            "adapter must still report it as a third outcome rather than interpreting it."
        ) if not fired else None,
    }


def case_negative_control() -> dict:
    """The independent validator must be able to FAIL. Feed it a witness that does not
    distinguish the circuits and confirm it says so."""
    c1 = ("or", ("and", 0, 1), ("and", 2, 3))
    c2 = ("or", ("and", 0, 1), ("or", 2, 3))
    bogus = (0, 0, 0, 0)   # both circuits are 0 here: not a distinguishing input
    rejected = evaluate(c1, bogus) == evaluate(c2, bogus)
    also_bogus = (1, 1, 0, 0)  # both 1 here
    rejected2 = evaluate(c1, also_bogus) == evaluate(c2, also_bogus)
    return {
        "case": "NEGATIVE_CONTROL_VALIDATOR_CAN_REJECT",
        "bogus_witnesses": [list(bogus), list(also_bogus)],
        "validator_rejected_both": rejected and rejected2,
        "pass": rejected and rejected2,
        "why": "A validator that accepts everything makes the SAT case vacuous. This case "
               "fires the validator in the failing direction so the passing direction means "
               "something.",
    }


def main() -> int:
    cases = [case_negative_control(), case_sat_counterexample(), case_unsat_equivalence(),
             case_unknown_timeout(), case_unknown_rlimit(), case_unknown_incompleteness()]
    decided = [c for c in cases if c.get("pass") is not None]
    out = {
        "check": "z3_first_useful_check",
        "tool": "z3-solver",
        "z3_version": z3.get_version_string(),
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "n_vars": N_VARS,
        "distinct_outcomes_observed": sorted({c["observed_z3_result"] for c in cases
                                              if "observed_z3_result" in c}),
        "unknown_reasons_observed": sorted({c["reason_unknown"] for c in cases
                                            if c.get("reason_unknown")}),
        "cases": cases,
        "n_cases": len(cases),
        "n_decided": len(decided),
        "n_passed": sum(1 for c in decided if c["pass"]),
        "all_decided_passed": all(c["pass"] for c in decided),
    }
    print(json.dumps(out))
    return 0 if out["all_decided_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
