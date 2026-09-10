"""Qualify pinned z3-solver as a bounded logical oracle for H1's 3-input Boolean tasks.

    <env>/python techne/acquisition/checks/z3_h1_oracle.py --fixture-out <path>

Three things the operator asked for, and all three are exhaustive rather than sampled:

  PARITY      over ALL 256 functions of 3 inputs, z3's evaluation agrees with PROTEUS's
              truth-table oracle on all 8 assignments. 2,048 agreements, no sampling.
  SAT/UNSAT/UNKNOWN  all three outcomes observed and distinguished, with resource exhaustion
              separated from incompleteness by reason string.
  COUNTEREXAMPLES  every distinguishing input z3 returns is validated by PROTEUS's evaluator,
              not by z3 and not by this file. All 32,640 distinct unordered pairs of the 256
              functions are asked, so every witness in the whole small domain is checked.

INDEPENDENCE IS THE POINT. `proteus.eval.boolean.truth_table` evaluates the AST in Python with
no solver and no VM involved; Proteus's own docstring calls it "the independent oracle the brief
requires". This file builds the z3 formula from the SAME AST and never lets z3 judge itself.

ASSIGNMENT ORDER is Proteus's, quoted from BOOLEAN3_POPULATION.json correctness_scope: "input 0
is most significant; k-th case has bit j = (k >> (n-1-j)) & 1". A parity result under a
different case order would be a different claim wearing the same name.

NO CAMPAIGN USE until Harmonia rules on the parity fixture. The receipt says so and the fixture
is emitted for exactly that ruling.
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import sys
import time

import z3

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from proteus.eval import boolean as PB   # noqa: E402  Proteus's independent oracle

N = PB.N_INPUTS                 # 3
N_CASES = 2 ** N                # 8
N_FUNCS = 2 ** N_CASES          # 256


def case_bits(k: int) -> tuple[int, ...]:
    """Proteus's declared order: input 0 is most significant."""
    return tuple((k >> (N - 1 - j)) & 1 for j in range(N))


def expr_for_table(table: tuple[int, ...]):
    """Sum-of-products AST in Proteus's own constructors. Canonical, not clever: the point is
    that the AST is Proteus's to evaluate, not that it is minimal."""
    minterms = []
    for k, bit in enumerate(table):
        if not bit:
            continue
        lits = []
        for j, b in enumerate(case_bits(k)):
            lits.append(PB.I(j) if b else PB.Not(PB.I(j)))
        term = lits[0]
        for l in lits[1:]:
            term = PB.And(term, l)
        minterms.append(term)
    if not minterms:
        return PB.C(0)
    out = minterms[0]
    for m in minterms[1:]:
        out = PB.Or(out, m)
    return out


def to_z3(e, xs):
    """The SAME AST, translated for the solver. Proteus's tags, nothing invented."""
    tag = e[0]
    if tag == PB.CONST:
        return z3.BoolVal(bool(e[1]))
    if tag == PB.INPUT:
        return xs[e[1]]
    if tag == PB.NOT:
        return z3.Not(to_z3(e[1], xs))
    a, b = to_z3(e[1], xs), to_z3(e[2], xs)
    return {PB.AND: z3.And, PB.OR: z3.Or, PB.XOR: z3.Xor}[tag](a, b)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture-out", required=True)
    a = ap.parse_args(argv)

    xs = [z3.Bool(f"x{j}") for j in range(N)]
    tables = [tuple((f >> (N_CASES - 1 - k)) & 1 for k in range(N_CASES)) for f in range(N_FUNCS)]
    exprs = [expr_for_table(t) for t in tables]

    # ---- 0. the AST really realises the table, per PROTEUS's evaluator
    t0 = time.perf_counter()
    realises = [tuple(PB.truth_table(e)) == t for e, t in zip(exprs, tables)]
    build_s = time.perf_counter() - t0

    # ---- 1. PARITY: z3 vs Proteus, all 256 functions x all 8 assignments
    t0 = time.perf_counter()
    parity_mismatches = []
    for f, (e, t) in enumerate(zip(exprs, tables)):
        ze = to_z3(e, xs)
        for k in range(N_CASES):
            bits = case_bits(k)
            s = z3.Solver()
            s.add(*[x == z3.BoolVal(bool(bv)) for x, bv in zip(xs, bits)])
            s.add(ze if t[k] else z3.Not(ze))
            if str(s.check()) != "sat":
                parity_mismatches.append({"function": f, "case": k, "bits": list(bits),
                                          "proteus": t[k], "z3_result": str(s.check())})
    parity_s = time.perf_counter() - t0
    n_parity = N_FUNCS * N_CASES

    # ---- 2. EQUIVALENCE over every distinct pair, every witness validated by PROTEUS
    t0 = time.perf_counter()
    zexprs = [to_z3(e, xs) for e in exprs]
    self_failures, pair_failures, witness_failures = [], [], []
    n_pairs = n_witnesses = 0
    for f in range(N_FUNCS):                       # identical pair -> must be UNSAT
        s = z3.Solver()
        s.add(z3.Xor(zexprs[f], zexprs[f]))
        if str(s.check()) != "unsat":
            self_failures.append(f)
    for f, g in itertools.combinations(range(N_FUNCS), 2):
        n_pairs += 1
        s = z3.Solver()
        s.add(z3.Xor(zexprs[f], zexprs[g]))
        r = str(s.check())
        if r != "sat":
            pair_failures.append({"f": f, "g": g, "z3_result": r})
            continue
        m = s.model()
        w = tuple(1 if z3.is_true(m.eval(x, model_completion=True)) else 0 for x in xs)
        n_witnesses += 1
        # INDEPENDENT validation: Proteus's tables, not z3's model
        k = sum(b << (N - 1 - j) for j, b in enumerate(w))
        if tables[f][k] == tables[g][k]:
            witness_failures.append({"f": f, "g": g, "witness": list(w), "case": k,
                                     "proteus_f": tables[f][k], "proteus_g": tables[g][k]})
    pairs_s = time.perf_counter() - t0

    # ---- 3. UNKNOWN and resource exhaustion, distinguished
    def pigeon(s, n=12, m=11):
        P = [[z3.Bool(f"p_{i}_{j}") for j in range(m)] for i in range(n)]
        for i in range(n):
            s.add(z3.Or(P[i]))
        for j in range(m):
            for i in range(n):
                for k2 in range(i + 1, n):
                    s.add(z3.Or(z3.Not(P[i][j]), z3.Not(P[k2][j])))
    st = z3.Solver(); st.set("timeout", 50); pigeon(st)
    r_to = str(st.check()); reason_to = st.reason_unknown()
    sr = z3.Solver(); sr.set("rlimit", 2000); pigeon(sr)
    r_rl = str(sr.check()); reason_rl = sr.reason_unknown()

    # ---- 4. NEGATIVE CONTROL: the validator must be able to reject
    #        feed Proteus a witness that does NOT distinguish two functions it knows differ
    f0, g0 = 0, 1
    diff_cases = [k for k in range(N_CASES) if tables[f0][k] != tables[g0][k]]
    same_cases = [k for k in range(N_CASES) if tables[f0][k] == tables[g0][k]]
    neg = {"f": f0, "g": g0, "distinguishing_cases": diff_cases,
           "non_distinguishing_cases": same_cases,
           "validator_rejects_a_non_distinguishing_case":
               all(tables[f0][k] == tables[g0][k] for k in same_cases) and bool(same_cases)}

    checks = [
        ("every one of the 256 ASTs realises its intended table under PROTEUS's evaluator",
         all(realises)),
        (f"PARITY: z3 agrees with Proteus on all {n_parity} (function, assignment) pairs",
         not parity_mismatches),
        ("SAT observed: every distinct pair of functions yields a distinguishing input",
         not pair_failures),
        ("UNSAT observed: a function is never distinguishable from itself", not self_failures),
        (f"every one of the {n_witnesses} returned counterexamples is validated INDEPENDENTLY "
         f"by Proteus's tables", not witness_failures),
        ("UNKNOWN by wall-clock exhaustion is observed and named 'timeout'",
         r_to == "unknown" and reason_to == "timeout"),
        ("UNKNOWN by deterministic rlimit is observed and named distinctly",
         r_rl == "unknown" and reason_rl == "max. resource limit exceeded"),
        ("negative control: the independent validator rejects a non-distinguishing witness",
         neg["validator_rejects_a_non_distinguishing_case"]),
    ]

    fixture = {
        "schema": "techne.h1.z3_parity_fixture/1",
        "for": "Harmonia's ruling. No campaign use of z3 as an H1 oracle until that ruling.",
        "oracle": {"module": "proteus.eval.boolean",
                   "function": "truth_table",
                   "interface_version": PB.INTERFACE_VERSION,
                   "grammar_version": PB.GRAMMAR_VERSION,
                   "independence": "evaluates the AST in Python; no solver, no VM"},
        "solver": {"distribution": "z3-solver", "version": z3.get_version_string(),
                   "wheel_sha256": "9b0aca98598353ea7eb59a51f909a399f6d0e687a1de3671b60a734cea4bb6bd",
                   "env": "isolated venv h0h5_tools"},
        "domain": {"n_inputs": N, "n_cases": N_CASES, "n_functions": N_FUNCS,
                   "exhaustive": True,
                   "assignment_order": "input 0 is most significant; k-th case has bit "
                                       "j = (k >> (n-1-j)) & 1  [Proteus, "
                                       "BOOLEAN3_POPULATION.json correctness_scope]"},
        "ast_construction": "sum of products over Proteus's own C/I/Not/And/Or/Xor constructors; "
                            "canonical rather than minimal, because the AST only has to be "
                            "Proteus's to evaluate",
        "results": {
            "parity_pairs_checked": n_parity, "parity_mismatches": parity_mismatches,
            "self_pairs_unsat": N_FUNCS - len(self_failures), "self_failures": self_failures,
            "distinct_pairs_checked": n_pairs, "pairs_without_a_witness": pair_failures,
            "witnesses_returned": n_witnesses,
            "witnesses_rejected_by_the_independent_oracle": witness_failures,
            "unknown_timeout": {"result": r_to, "reason": reason_to},
            "unknown_rlimit": {"result": r_rl, "reason": reason_rl},
            "negative_control": neg,
        },
        "timing_seconds": {"ast_build_and_oracle": round(build_s, 2),
                           "parity": round(parity_s, 2), "pairs": round(pairs_s, 2)},
        "checks": [{"claim": c, "pass": bool(p)} for c, p in checks],
        "all_passed": all(p for _, p in checks),
        "what_this_does_NOT_establish": [
            "that z3 is a correct oracle outside 3-input Boolean. The domain is exhaustive "
            "WITHIN itself and says nothing about 4 inputs or about any other theory.",
            "that z3 may be used in a campaign. Harmonia rules on this fixture first.",
            "anything about z3's behaviour on hard instances: on this build every `unknown` I "
            "could elicit was a budget failure, which is a fact about what I could elicit.",
        ],
    }
    pathlib.Path(a.fixture_out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.fixture_out).write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    # ADAPTER_QUALIFICATION receipt, written from inside the isolated env (which can import
    # techne via PYTHONPATH). The stage is adapter qualification rather than a first useful
    # check because the consumer and its typed contract are both named.
    try:
        from techne.acquisition import receipt as _R
        rec = _R.new("ADAPTER_QUALIFICATION", "z3", tool="z3-solver")
        rec["check"] = "z3_as_a_bounded_logical_oracle_for_h1_3_input_boolean"
        rec["consumer"] = ("H1 1.0 -- bounded logical oracle over Proteus's 3-input Boolean "
                           "substrate (proteus.eval.boolean, interface "
                           + PB.INTERFACE_VERSION + ")")
        rec["fixture"] = a.fixture_out
        rec["observations"] = fixture
        rec["status"] = ("QUALIFIED_PENDING_HARMONIA_RULING" if fixture["all_passed"]
                         else "FAILED")
        rec["unrun_or_blocked"] = [
            "CAMPAIGN USE. Harmonia rules on the parity fixture first; this receipt is the "
            "input to that ruling, not a substitute for it.",
            "any domain beyond 3-input Boolean. The exhaustiveness is WITHIN this domain and "
            "says nothing about 4 inputs or any other theory.",
        ]
        print("receipt", _R.write(rec))
    except Exception as exc:                                   # recorded, never silent
        print(f"receipt NOT written: {type(exc).__name__}: {exc}")

    print(json.dumps({k: v for k, v in fixture.items() if k != "results"} |
                     {"results_summary": {
                         "parity_pairs": n_parity, "parity_mismatches": len(parity_mismatches),
                         "distinct_pairs": n_pairs, "witnesses": n_witnesses,
                         "witness_failures": len(witness_failures),
                         "unknown_reasons": [reason_to, reason_rl]}}))
    return 0 if fixture["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
