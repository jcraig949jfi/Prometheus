"""Unit tests for the new legality-load generators (gen_abs_extra_clean,
gen_log_extra_3arg) added for the H1 predictive replication. Verifies ground
truth by DIRECT SUBSTITUTION — no LLM, no API, deterministic.

For abs_extra_clean: every probe must satisfy |x-a| = b-x at x=(a+b)/2 and
have a<=b (the filter precondition that makes "no solution" unambiguously wrong).

For log_extra_3arg: every probe must satisfy p(p-a)(p-b)=c at x=p (equivalent
to the log equation), have 0<a<b and p>b (strict domain), and have p as the
UNIQUE real root in x>b (otherwise the rejection sampler missed a case).

Run: python harmonia/experiments/test_legality_generators.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

_EXP = Path(__file__).resolve().parent
_REPO = _EXP.parents[1]
for _p in (str(_REPO), str(_EXP)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sympy as sp  # noqa: E402
from reasoning_phase0 import (  # noqa: E402
    gen_abs_extra_clean, gen_log_extra_3arg, _ans_correct,
)

_PASS = 0
_FAIL = 0

# Seeds the test must cover. 20260530 was the original authoring seed; the
# binding replication (legality_overrefusal_4arm_writeup_2026-05-30.md §3.2)
# pre-commits 20260601/02/03. A ground-truth guard that does not exercise the
# seeds the experiment actually runs is a guard that doesn't guard — so all
# four are checked here. (Audited 2026-06-05: a numpy + sympy scan over the
# three binding seeds and 3000 additional seeds found 0 poisoned probes, so
# the rejection-sampler fall-through in gen_log_extra_3arg never fires for
# these parameter ranges. These cases pin that result against regression.)
_SEEDS = (20260530, 20260601, 20260602, 20260603)


def check(name, cond, detail=""):
    global _PASS, _FAIL
    if cond:
        _PASS += 1
        print(f"  ok   {name}")
    else:
        _FAIL += 1
        print(f"  FAIL {name}  {detail}")


def test_abs_extra_clean_ground_truth():
    """Every probe: a<=b, gt=[(a+b)/2], and (a+b)/2 satisfies |x-a|=b-x.
    Checked on every binding seed (see _SEEDS)."""
    for seed in _SEEDS:
        rng = random.Random(seed)
        probes = gen_abs_extra_clean(rng)
        check(f"abs_clean[seed={seed}]: non-empty batch", len(probes) > 0)
        for i, p in enumerate(probes[:60]):   # check the first 60
            a, b = p.data["a"], p.data["b"]
            tag = f"abs_clean[s={seed},{i}]"
            check(f"{tag}: a<=b ({a}<={b})", a <= b)
            check(f"{tag}: gt has exactly 1 root", len(p.ground_truth) == 1)
            x = p.ground_truth[0]
            # Substitution: |x-a| should equal b-x
            lhs = abs(x - a)
            rhs = b - x
            check(f"{tag}: |x-{a}|=b-x at x={x} ({lhs}={rhs})", lhs == rhs)
            check(f"{tag}: kind tagged", p.kind == "abs_extra_clean")
            check(f"{tag}: tier tagged", p.tier == "AC")


def test_log_extra_3arg_ground_truth():
    """Every probe: 0<a<b, p>b, c=p(p-a)(p-b), and p is the UNIQUE real root in x>b.
    Checked on every binding seed (see _SEEDS) — this is the arm whose rejection
    sampler can fall through after 30 tries, so seed coverage is load-bearing."""
    for seed in _SEEDS:
        rng = random.Random(seed)
        probes = gen_log_extra_3arg(rng)
        check(f"log3[seed={seed}]: non-empty batch", len(probes) > 0)
        for i, p in enumerate(probes[:40]):
            a, b, c = p.data["a"], p.data["b"], p.data["c"]
            tag = f"log3[s={seed},{i}]"
            check(f"{tag}: 0<a<b ({a}<{b})", 0 < a < b)
            check(f"{tag}: gt has exactly 1 root", len(p.ground_truth) == 1)
            root = int(p.ground_truth[0])
            check(f"{tag}: p>b ({root}>{b})", root > b)
            # Direct substitution: x(x-a)(x-b) must equal c at x=root
            lhs = root * (root - a) * (root - b)
            check(f"{tag}: p(p-a)(p-b)=c at p={root} ({lhs}=={c})", lhs == c)
            check(f"{tag}: kind tagged", p.kind == "log_extra_3arg")
            check(f"{tag}: tier tagged", p.tier == "LE3")

            # The strong condition: p is the UNIQUE real root in x>b. Solve symbolically.
            x = sp.Symbol("x", real=True)
            cubic = x * (x - a) * (x - b) - c
            roots = [r for r in sp.solve(cubic, x) if r.is_real]
            in_domain = [r for r in roots if r > b]
            check(f"{tag}: unique real root in x>{b}", len(in_domain) == 1,
                  detail=f"in-domain roots: {in_domain}")
            check(f"{tag}: that root equals p={root}",
                  len(in_domain) == 1 and in_domain[0] == root)


def test_ans_correct_dispatches_new_kinds():
    """_ans_correct must accept the new kinds; verifies the kind-tuple was updated."""
    rng = random.Random(7)
    p_abs = gen_abs_extra_clean(rng)[0]
    p_log = gen_log_extra_3arg(rng)[0]
    check("ans_correct: abs_clean accepts gt", _ans_correct(p_abs, list(p_abs.ground_truth)))
    check("ans_correct: log3 accepts gt", _ans_correct(p_log, list(p_log.ground_truth)))
    # over-refusal (empty list) must score as WRONG on these clean-gt probes
    check("ans_correct: abs_clean rejects empty (over-refusal)", not _ans_correct(p_abs, []))
    check("ans_correct: log3 rejects empty (over-refusal)", not _ans_correct(p_log, []))
    # a wrong nonempty answer must also be WRONG
    check("ans_correct: abs_clean rejects wrong root", not _ans_correct(p_abs, [sp.Integer(999)]))
    check("ans_correct: log3 rejects wrong root", not _ans_correct(p_log, [sp.Integer(999)]))


def main():
    for fn in [test_abs_extra_clean_ground_truth,
               test_log_extra_3arg_ground_truth,
               test_ans_correct_dispatches_new_kinds]:
        print(f"\n# {fn.__name__}")
        fn()
    print(f"\n==== {_PASS} passed, {_FAIL} failed ====")
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()
