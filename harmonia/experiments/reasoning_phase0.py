"""Reasoning Phase 0 (EXPERIMENTAL) — testable reasoning-ladder kill-space.

Ethos (James, 2026-05-27): fail early, fail often, drive signal from failure. So this harness plugs
deliberately CAPABILITY-CAPPED baseline reasoners into procedurally-generated R0-R3 + R6 probes (4
versions each: clean / isomorphic / adversarial / transfer) and emits a deterministic Reasoning Trace
Vector per attempt (the reasoning-side KillVector). A known-weak reasoner SHOULD fail in tier-predicted
ways — that is the calibration, and the failures are the product.

Reports:
  (1) reasoner x tier calibration (capability ceiling staircase — or not, which is itself evidence
      the tiers are orthogonal axes rather than ordered rungs);
  (2) dominant failure SHAPE per (reasoner, tier);
  (3) effective dimensionality of the trace-vector matrix + cross-tier distinguishability
      (the rung-reality test).

Offline, deterministic. Ground truth via sympy.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np
import sympy as sp

x, y = sp.symbols("x y")
SEED = 20260527
N_PER = 40  # probes per (tier, version)

# ---------------------------------------------------------------- probes
@dataclass
class Probe:
    tier: str
    version: str            # clean | iso | adversarial | transfer
    kind: str               # linear | quadratic | sqrt | rational | conjecture
    data: Dict[str, Any]
    ground_truth: Any
    legal: Dict[str, Any] = field(default_factory=dict)


def gen_R0(rng):  # pattern match -> survives isomorphism?
    out = []
    for _ in range(N_PER):
        a, b, c = rng.randint(2, 9), rng.randint(1, 9), rng.randint(10, 40)
        sol = sp.Rational(c - b, a)
        out.append(Probe("R0", "clean", "linear", {"expr": a * x + b - c}, sol))
        # isomorphic: nested/distributed rewrite of an equivalent equation
        p, q = rng.randint(2, 5), rng.randint(1, 6)
        rhs = rng.choice([v for v in range(2, 8) if v != p])  # ensure nonzero x-coefficient
        expr = (rng.randint(5, 20) - p * (q - x)) - (rhs * x + rng.randint(1, 6))
        sols = sp.solve(expr, x)
        out.append(Probe("R0", "iso", "linear", {"expr": expr}, sols[0]))
        # adversarial: renamed var + distractor term that cancels
        expr2 = a * y + b - c + 0 * (y ** 2 - y ** 2)
        out.append(Probe("R0", "adversarial", "linear", {"expr": expr2, "var": y},
                         sp.Rational(c - b, a)))
        # transfer: same structure, fractional coefficients
        expr3 = sp.Rational(a, 2) * x + sp.Rational(b, 3) - c
        out.append(Probe("R0", "transfer", "linear", {"expr": expr3}, sp.solve(expr3, x)[0]))
    return out


def gen_R1(rng):  # rule application; legality = domain (real roots exist?)
    out = []
    for _ in range(N_PER):
        r1, r2 = rng.randint(-6, 6), rng.randint(-6, 6)
        expr = sp.expand((x - r1) * (x - r2))            # factorable over reals
        out.append(Probe("R1", "clean", "quadratic", {"expr": expr},
                         sorted({sp.Rational(r1), sp.Rational(r2)}, key=float)))
        out.append(Probe("R1", "iso", "quadratic", {"expr": sp.expand(expr + 0)},
                         sorted({sp.Rational(r1), sp.Rational(r2)}, key=float)))
        # adversarial: no real roots (discriminant < 0) -> must NOT hallucinate real factors
        b = rng.randint(-3, 3)
        expr2 = x ** 2 + b * x + (b * b // 4 + rng.randint(1, 5))  # disc < 0
        out.append(Probe("R1", "adversarial", "quadratic", {"expr": expr2}, []))
        # transfer: leading coeff != 1
        k = rng.randint(2, 4)
        expr3 = sp.expand(k * (x - r1) * (x - r2))
        out.append(Probe("R1", "transfer", "quadratic", {"expr": expr3},
                         sorted({sp.Rational(r1), sp.Rational(r2)}, key=float)))
    return out


def gen_R2(rng):  # constraint tracking: sqrt(x+a) = x - b ; reject extraneous
    out = []
    for _ in range(N_PER):
        a, b = rng.randint(0, 6), rng.randint(0, 4)
        eq = sp.Eq(sp.sqrt(x + a), x - b)
        true_sols = [s for s in sp.solve(eq, x) if s.is_real]
        for v in ("clean", "iso", "adversarial", "transfer"):
            aa, bb = (a, b)
            if v == "iso":
                aa, bb = a + 1, b
            if v == "transfer":
                eq2 = sp.Eq(sp.sqrt(x + aa) + 0, (x - bb))
            else:
                eq2 = sp.Eq(sp.sqrt(x + aa), x - bb)
            ts = [s for s in sp.solve(eq2, x) if s.is_real]
            out.append(Probe("R2", v, "sqrt", {"a": aa, "b": bb, "eq": eq2}, ts,
                             legal={"domain": "x>=b and x+a>=0"}))
    return out


def gen_R3(rng):  # multi-step: rational eqn with an excluded value
    out = []
    for _ in range(N_PER):
        r = rng.randint(2, 9)
        # (x^2 - r^2)/(x - r) = x + r  -> identity for x != r ; the catch is x != r
        for v in ("clean", "iso", "adversarial", "transfer"):
            rr = r + (1 if v == "iso" else 0)
            out.append(Probe("R3", v, "rational",
                             {"num": x ** 2 - rr ** 2, "den": x - rr, "rhs": x + rr, "excluded": rr},
                             {"identity_except": rr}))
    return out


# conjectures: (statement_id, truth, counterexample, small_streak_clean)
CONJ = [
    ("ab_even_then_both_even", False, (2, 3), True),       # cex small
    ("n2_plus_n_even", True, None, False),                 # true
    ("n2_n_41_prime", False, 41, True),                    # cex DELAYED (n=41)
    ("all_primes_odd", False, 2, True),                    # cex small (2)
    ("sum_two_squares", True, None, False),                # true-ish placeholder
]

def gen_R6(rng):
    out = []
    for _ in range(N_PER):
        cid, truth, cex, streak = CONJ[rng.randint(0, len(CONJ) - 1)]
        for v in ("clean", "iso", "adversarial", "transfer"):
            out.append(Probe("R6", v, "conjecture",
                             {"cid": cid, "truth": truth, "cex": cex, "delayed": (cid == "n2_n_41_prime")},
                             truth))
    return out


def _board_balance(n, removed):
    cells = [(i, j) for i in range(n) for j in range(n) if (i, j) not in removed]
    blacks = sum(1 for (i, j) in cells if (i + j) % 2 == 0)
    return len(cells), blacks, len(cells) - blacks

def gen_R5(rng):  # invariant detection (parity) — parity-DECIDABLE instances only
    out = []
    for _ in range(N_PER):
        n = rng.choice([4, 6, 8])
        # clean: opposite corners removed -> both same color -> untileable (color parity)
        out.append(Probe("R5", "clean", "invariant",
                         {"n": n, "removed": {(0, 0), (n - 1, n - 1)}, "invariant": "color_parity"}, False))
        n2 = n + 2  # iso: bigger board, same construction
        out.append(Probe("R5", "iso", "invariant",
                         {"n": n2, "removed": {(0, 0), (n2 - 1, n2 - 1)}, "invariant": "color_parity"}, False))
        # adversarial: remove 1 cell -> ODD area -> untileable by AREA parity (not the textbook corner case)
        out.append(Probe("R5", "adversarial", "invariant",
                         {"n": n, "removed": {(0, 0)}, "invariant": "area_parity"}, False))
        # transfer: full even board, no removal -> tileable
        out.append(Probe("R5", "transfer", "invariant",
                         {"n": n, "removed": set(), "invariant": "none"}, True))
    return out

# Flawed/valid proofs as NUMBERED steps; ground_truth = 1-indexed first invalid
# step, or 0 if the proof is fully valid. Deterministic integer grading — no LLM.
_PROOFS = [
    {"name": "all_horses_same_color", "bad": 5, "steps": [
        "Base case: any single horse is the same color as itself.",
        "Inductive hypothesis: assume any group of n horses is all one color.",
        "Given n+1 horses, the first n are one color by the hypothesis.",
        "The last n are one color by the hypothesis.",
        "The first-n and last-n groups overlap, so all n+1 horses are one color.",
    ]},
    {"name": "two_equals_one", "bad": 5, "steps": [
        "Let a = b.",
        "Multiply both sides by a: a^2 = a*b.",
        "Subtract b^2 from both sides: a^2 - b^2 = a*b - b^2.",
        "Factor: (a-b)(a+b) = b(a-b).",
        "Divide both sides by (a-b): a + b = b.",
        "Since a=b: 2b = b, therefore 2 = 1.",
    ]},
    {"name": "sqrt_x2_equals_x", "bad": 2, "steps": [
        "For any real x, x^2 >= 0, so sqrt(x^2) is well defined.",
        "sqrt(x^2) = x because the square root undoes squaring.",
        "Hence sqrt(x^2) = x for all real x.",
    ]},
    {"name": "max_all_equal", "bad": 4, "steps": [
        "Base case: a set of one number has max = min, so its elements are all equal.",
        "Inductive hypothesis: any n numbers are all equal.",
        "For n+1 numbers, the first n are equal and the last n are equal by hypothesis.",
        "The two groups overlap, so all n+1 numbers are equal.",
    ]},
    {"name": "valid_sum_first_n", "bad": 0, "steps": [
        "Base case n=1: the sum is 1 and 1*(1+1)/2 = 1, so it holds.",
        "Inductive hypothesis: assume 1+2+...+k = k(k+1)/2.",
        "Then 1+...+k+(k+1) = k(k+1)/2 + (k+1) = (k+1)(k+2)/2.",
        "That is the formula at n=k+1, completing the induction.",
    ]},
]
def gen_R7(rng):  # proof repair — locate first invalid step (0 == fully valid)
    out = []
    for _ in range(N_PER):
        for v in ("clean", "iso", "adversarial", "transfer"):
            pr = _PROOFS[rng.randint(0, len(_PROOFS) - 1)]
            out.append(Probe("R7", v, "proof_repair",
                             {"proof": pr["name"], "steps": pr["steps"]}, pr["bad"]))
    return out


# R8 lemma selection: pick the lemma that unlocks the proof. lemmas[0] of each
# problem is the load-bearing one; 'over_general_false' is the CONTROL TRAP — a
# tempting, powerful-sounding but FALSE lemma (bait for the over-reach failure the
# Opus<Sonnet inversion exposed). Hand-verified.
_LEMMA_PROBLEMS = [
    {"goal": "For every integer n, n^2 + n is even.", "lemmas": [
        ("Of any two consecutive integers exactly one is even, so their product is even.", "load_bearing"),
        ("For every integer n, n is even.", "over_general_false"),
        ("The sum of two even integers is even.", "irrelevant_true"),
        ("For every integer n, n^2 = n.", "false_distractor"),
        ("For every integer n, n + 1 > n.", "trivial")]},
    {"goal": "For every integer n, n^3 - n is divisible by 6.", "lemmas": [
        ("n^3 - n = (n-1)*n*(n+1), and any product of three consecutive integers is divisible by 6.", "load_bearing"),
        ("Every cube n^3 is divisible by 6.", "over_general_false"),
        ("The product of two consecutive integers is divisible by 2.", "irrelevant_true"),
        ("n^3 - n >= 0 for every integer n.", "false_distractor"),
        ("6 = 2 * 3.", "trivial")]},
    {"goal": "The sum of the first n odd numbers equals n^2.", "lemmas": [
        ("The (k+1)-th odd number is 2k+1, and k^2 + (2k+1) = (k+1)^2 (the induction step).", "load_bearing"),
        ("Every sum of consecutive integers is a perfect square.", "over_general_false"),
        ("The sum of the first n integers is n(n+1)/2.", "irrelevant_true"),
        ("Every odd number is a perfect square.", "false_distractor"),
        ("1 is an odd number.", "trivial")]},
    {"goal": "sqrt(2) is irrational.", "lemmas": [
        ("If 2 divides a^2 then 2 divides a, forcing a common-factor contradiction.", "load_bearing"),
        ("The square root of every integer is irrational.", "over_general_false"),
        ("sqrt(4) = 2 is rational.", "irrelevant_true"),
        ("2 divides a^2 if and only if 2 divides a^2 + 1.", "false_distractor"),
        ("2 is a prime number.", "trivial")]},
]
def gen_R8(rng):  # lemma selection — pick the load-bearing lemma (trap = over_general_false)
    out = []
    for _ in range(N_PER):
        for v in ("clean", "iso", "adversarial", "transfer"):
            prob = _LEMMA_PROBLEMS[rng.randint(0, len(_LEMMA_PROBLEMS) - 1)]
            pairs = list(prob["lemmas"]); rng.shuffle(pairs)
            lemmas = [t for t, _ in pairs]; types = [ty for _, ty in pairs]
            correct = types.index("load_bearing") + 1   # 1-indexed
            out.append(Probe("R8", v, "lemma_select",
                             {"goal": prob["goal"], "lemmas": lemmas, "types": types}, correct))
    return out


def gen_sqrt_label(rng):  # C-FORMAT control: STRUCTURED legality check (label given candidates),
    out = []              # same execution skill as R2 but no free-gen solving — isolates format.
    for _ in range(N_PER):
        for v in ("clean", "iso", "adversarial", "transfer"):
            a, b = rng.randint(0, 6), rng.randint(0, 4)
            cands = [r for r in sp.solve(sp.Eq(x + a, (x - b) ** 2), x) if r.is_real]
            if not cands:
                continue
            mask = tuple(bool((c - b).is_nonnegative and (c + a).is_nonnegative) for c in cands)
            out.append(Probe("CF", v, "sqrt_label",
                             {"a": a, "b": b, "candidates": [sp.sstr(c) for c in cands]}, mask))
    return out


def gen_rational_extra(rng):  # C-MEMO: rational extraneous root — DIFFERENT operation, same legality skill.
    out = []                  # (x^2 - c^2)/(x - c) = k cancels to x = k - c, but x=c is EXCLUDED, so
    for _ in range(N_PER):    # k = 2c => only candidate is the excluded value => NO solution (the trap).
        for v in ("clean", "iso", "adversarial", "transfer"):
            c = rng.randint(1, 8)
            trap = (v == "adversarial") or (rng.random() < 0.4)
            k = 2 * c if trap else 2 * c + rng.choice([-3, -2, -1, 1, 2, 3])
            gt = [] if k == 2 * c else [sp.Integer(k - c)]
            out.append(Probe("RE", v, "rational_extra", {"c": c, "k": k}, gt))
    return out


def gen_abs_extra(rng):  # C-MEMO: absolute-value extraneous — |x-a| = b-x needs b-x >= 0
    out = []
    for _ in range(N_PER):
        for v in ("clean", "iso", "adversarial", "transfer"):
            a, b = rng.randint(0, 8), rng.randint(0, 8)
            if v == "adversarial" and a <= b:        # bias adversarial toward the no-solution trap
                a = b + rng.randint(1, 4)
            gt = [sp.Rational(a + b, 2)] if a <= b else []   # x=(a+b)/2 valid iff a<=b
            out.append(Probe("AE", v, "abs_extra", {"a": a, "b": b}, gt))
    return out


def gen_log_extra(rng):  # C-MEMO: log-domain extraneous — reject the non-positive candidate
    out = []
    for _ in range(N_PER):
        for v in ("clean", "iso", "adversarial", "transfer"):
            q = -rng.randint(1, 4)                   # negative root (extraneous: x>0 fails)
            p = -q + rng.randint(1, 5)               # positive root > a, valid
            a, b = p + q, -p * q                     # x^2-ax-b=0 has roots p(valid), q(rejected)
            out.append(Probe("LE", v, "log_extra", {"a": a, "b": b}, [sp.Integer(p)]))
    return out


def gen_abs_extra_clean(rng):  # H1 isolation: ONLY solvable cases (a<=b), so gt is always [(a+b)/2]
    """Filtered abs_extra for the over-pruning instrument: every probe has a
    valid root, so "no solution" is unambiguously wrong (=over-refusal). Removes
    the gt=[] confound that mixed correct-no-solution detection into the
    original gen_abs_extra error count."""
    out = []
    for _ in range(N_PER):
        for v in ("clean", "iso", "adversarial", "transfer"):
            a = rng.randint(0, 6)
            b = a + rng.randint(0, 8)                # always a<=b => x=(a+b)/2 valid
            out.append(Probe("AC", v, "abs_extra_clean",
                             {"a": a, "b": b}, [sp.Rational(a + b, 2)]))
    return out


def gen_log_extra_3arg(rng):  # H1 PREDICTION (dcl=3): three independent log-domain conditions
    """log(x)+log(x-a)+log(x-b)=log(c) with 0<a<b. Domain: x>0 AND x>a AND x>b,
    so x>b. Construct c from a chosen valid root p>b, then rejection-sample until
    p is the UNIQUE real root in the domain (so "[p]" is the only valid gt and
    any "no solution" answer is unambiguously over-refusal). This is the
    pre-registered predictive arm: if H1 (legality-load) holds, Opus's
    over-refusal here should EXCEED its over-refusal on log_extra (dcl=2)."""
    out = []
    for _ in range(N_PER):
        for v in ("clean", "iso", "adversarial", "transfer"):
            for _try in range(30):                   # rejection sample
                a = rng.randint(1, 4)
                b = a + rng.randint(1, 4)            # 0 < a < b
                p = b + rng.randint(1, 5)            # p > b (strict domain)
                # cubic x(x-a)(x-b) - c = (x-p)(x^2 + Ax + B); ensure quadratic
                # has NO real root in (b, inf) so p is the only in-domain real root
                A = p - a - b
                B = (p - a) * (p - b)
                disc = A * A - 4 * B
                if disc < 0:
                    break                            # quadratic has no real roots
                sqrt_d = disc ** 0.5
                r1 = (-A + sqrt_d) / 2.0
                r2 = (-A - sqrt_d) / 2.0
                if r1 <= b and r2 <= b:              # other reals exist but out of domain
                    break
            c = p * (p - a) * (p - b)
            out.append(Probe("LE3", v, "log_extra_3arg",
                             {"a": a, "b": b, "c": c}, [sp.Integer(p)]))
    return out


# ---------------------------------------------------------------- reasoners
# Each returns (answer, trace_dict). Capability caps are deliberate.
def _solve_real(expr):
    try:
        syms = list(expr.free_symbols)               # variable-agnostic (fixes R0 rename artifact)
        var = syms[0] if syms else x
        return sorted({s for s in sp.solve(expr, var) if s.is_real}, key=float)
    except Exception:
        return None

def reasoner_template(p):
    tr = {"operations_used": ["pattern_match"]}
    if p.kind == "linear" and p.version == "clean":
        return _solve_real(p.data["expr"]), tr
    if p.kind == "conjecture":
        return True, {"operations_used": ["guess_true"], "searched_counterexample": False}
    return None, tr  # template can't handle perturbed forms

def reasoner_procedural(p):
    tr = {"operations_used": []}
    if p.kind in ("linear", "quadratic"):
        tr["operations_used"] = ["formula"]
        return _solve_real(p.data["expr"]), tr
    if p.kind == "sqrt":
        # squares both sides, returns ALL roots, does NOT reject extraneous
        tr["operations_used"] = ["square_both_sides"]
        tr["invalid_operations_attempted"] = ["square_without_domain_check"]
        tr["domain_constraints_detected"] = []
        a, b = p.data["a"], p.data["b"]
        allroots = sp.solve(sp.Eq(x + a, (x - b) ** 2), x)
        return sorted({s for s in allroots if s.is_real}, key=float), tr
    if p.kind == "rational":
        # cancels naively -> "all x" (misses excluded value)
        tr["operations_used"] = ["cancel"]
        tr["invalid_operations_attempted"] = ["cancel_without_excluding_zero_denominator"]
        return "all_x", tr
    if p.kind == "conjecture":
        # tests small examples 0..6, affirms if all pass (over-generalizes)
        tr["operations_used"] = ["small_example_check"]; tr["counterexamples_tested"] = list(range(7))
        tr["searched_counterexample"] = True
        cid, cex = p.data["cid"], p.data["cex"]
        # if a small counterexample exists within 0..6, it catches it; delayed ones it misses
        caught = isinstance(cex, tuple) or (isinstance(cex, int) and cex <= 6)
        tr["overgeneralized"] = not caught
        return (False if caught else True), tr
    return None, tr

def reasoner_careful(p):
    ans, tr = reasoner_procedural(p)
    if p.kind == "sqrt":
        # tracks domain, rejects extraneous
        tr = {"operations_used": ["square_both_sides", "domain_check"],
              "domain_constraints_detected": ["x>=b", "x+a>=0"], "rejected_extraneous": True}
        return p.ground_truth, tr
    if p.kind == "rational":
        tr = {"operations_used": ["cancel", "exclude_zero_denominator"],
              "domain_constraints_detected": ["x!=excluded"]}
        return "all_x_except_excluded", tr
    return ans, tr

def reasoner_falsifier(p):
    ans, tr = reasoner_careful(p)
    if p.kind == "conjecture":
        # searches a wide structured range incl. structurally-suspicious values
        tr = {"operations_used": ["structured_counterexample_search"],
              "counterexamples_tested": list(range(0, 60)), "searched_counterexample": True}
        cid, cex, truth = p.data["cid"], p.data["cex"], p.data["truth"]
        caught = (cex is not None) and (isinstance(cex, tuple) or cex < 60)
        tr["found_counterexample"] = caught
        tr["overgeneralized"] = False
        return (False if caught else truth), tr
    return ans, tr

REASONERS = {"template": reasoner_template, "procedural": reasoner_procedural,
             "careful": reasoner_careful, "falsifier": reasoner_falsifier}

# ---------------------------------------------------------------- grading -> trace vector
TRACE_FIELDS = ["answer_correct", "survived_isomorphism", "domain_constraint_detected",
                "invalid_op_attempted", "rejected_extraneous", "searched_counterexample",
                "found_counterexample", "overgeneralized", "correct_decision",
                "reported_real_roots", "hallucinated_roots", "excluded_value_handled",
                "invariant_named", "failing_step_located",
                "lemma_selected", "picked_trap"]

def _ans_correct(p, ans):
    gt = p.ground_truth
    if p.kind in ("linear",):
        try: return ans is not None and len(ans) == 1 and sp.nsimplify(ans[0]) == sp.nsimplify(gt)
        except Exception: return False
    if p.kind in ("quadratic", "sqrt"):
        if ans is None: return False
        try: return sorted(map(float, ans)) == sorted(map(float, gt))
        except Exception: return False
    if p.kind == "rational":
        return ans == "all_x_except_excluded"
    if p.kind == "conjecture":
        return ans == p.data["truth"]
    if p.kind == "invariant":
        return ans == p.ground_truth          # bool tileable
    if p.kind == "proof_repair":
        return isinstance(ans, int) and ans == p.ground_truth   # first-invalid step index (0==valid)
    if p.kind == "lemma_select":
        return isinstance(ans, int) and ans == p.ground_truth   # 1-indexed load-bearing lemma
    if p.kind == "sqrt_label":
        return (isinstance(ans, (list, tuple)) and len(ans) == len(p.ground_truth)
                and tuple(bool(z) for z in ans) == p.ground_truth)
    if p.kind in ("rational_extra", "abs_extra", "abs_extra_clean",
                  "log_extra", "log_extra_3arg"):
        if ans is None:
            return False
        try:
            return sorted(map(float, ans)) == sorted(map(float, p.ground_truth))
        except Exception:
            return False
    return False

def grade(p, ans, tr):
    v = {f: np.nan for f in TRACE_FIELDS}
    correct = _ans_correct(p, ans)
    v["answer_correct"] = 1.0 if correct else 0.0
    if p.tier == "R0":
        v["survived_isomorphism"] = 1.0 if (p.version != "clean" and correct) else (0.0 if p.version != "clean" else np.nan)
    if p.tier == "R1":
        reported = ans if isinstance(ans, list) else []
        v["reported_real_roots"] = 1.0 if reported else 0.0
        if p.version == "adversarial":            # no real roots exist; reporting any == hallucination
            v["hallucinated_roots"] = 1.0 if reported else 0.0
    if p.tier == "R2":
        v["domain_constraint_detected"] = 1.0 if tr.get("domain_constraints_detected") else 0.0
        v["invalid_op_attempted"] = 1.0 if tr.get("invalid_operations_attempted") else 0.0
        v["rejected_extraneous"] = 1.0 if tr.get("rejected_extraneous") else 0.0
    if p.tier == "R3":
        v["domain_constraint_detected"] = 1.0 if tr.get("domain_constraints_detected") else 0.0
        v["invalid_op_attempted"] = 1.0 if tr.get("invalid_operations_attempted") else 0.0
        v["excluded_value_handled"] = 1.0 if ans == "all_x_except_excluded" else 0.0
    if p.tier == "R6":
        v["searched_counterexample"] = 1.0 if tr.get("searched_counterexample") else 0.0
        v["found_counterexample"] = 1.0 if tr.get("found_counterexample") else 0.0
        v["overgeneralized"] = 1.0 if tr.get("overgeneralized") else 0.0
        v["correct_decision"] = 1.0 if correct else 0.0
    if p.tier == "R5":
        v["invariant_named"] = 1.0 if tr.get("invariant_named") else 0.0
        v["correct_decision"] = 1.0 if correct else 0.0
    if p.tier == "R7":
        v["failing_step_located"] = 1.0 if correct else 0.0
    if p.tier == "R8":
        v["lemma_selected"] = 1.0 if correct else 0.0
        types = p.data.get("types", [])
        picked = ans if isinstance(ans, int) else None
        if (not correct) and picked is not None and 1 <= picked <= len(types):
            v["picked_trap"] = 1.0 if types[picked - 1] == "over_general_false" else 0.0
    # kill pattern (the failure SHAPE)
    kp = None
    if not correct:
        if p.tier == "R0": kp = "pattern_match_broke_under_isomorphism"
        elif p.tier == "R1": kp = "hallucinated_real_roots" if p.version == "adversarial" else "rule_misapplied"
        elif p.tier == "R2": kp = "extraneous_root_not_rejected"
        elif p.tier == "R3": kp = "excluded_value_missed"
        elif p.tier == "R6": kp = "overgeneralized_from_examples" if tr.get("overgeneralized") else "wrong_decision"
        elif p.tier == "R5": kp = "wrong_or_missing_invariant"
        elif p.tier == "R7": kp = "failing_step_not_located"
        elif p.tier == "R8":
            types = p.data.get("types", []); picked = ans if isinstance(ans, int) else None
            if picked is not None and 1 <= picked <= len(types):
                kp = ("grabbed_overgeneral_lemma" if types[picked - 1] == "over_general_false"
                      else f"picked_{types[picked - 1]}")
            else:
                kp = "no_lemma_selected"
        elif p.tier == "CF": kp = "mislabeled_validity"
        elif p.tier in ("RE", "AE", "LE"):
            al = ans if isinstance(ans, list) else ([] if ans is None else [ans])
            if not p.ground_truth and al: kp = "kept_excluded_root"   # gave x=c when none exists
            elif p.ground_truth and not al: kp = "over_refused"       # said none when one exists
            else: kp = "rational_wrong"
    v["_kill_pattern"] = kp
    return v, correct

# ---------------------------------------------------------------- runner
def eff_dim(M):
    cols = [j for j in range(M.shape[1]) if np.isfinite(M[:, j]).sum() > 2 and np.nanstd(M[:, j]) > 1e-9]
    if len(cols) < 2: return 1.0, len(cols)
    C = np.eye(len(cols))
    for a in range(len(cols)):
        for b in range(a + 1, len(cols)):
            xa, xb = M[:, cols[a]], M[:, cols[b]]
            ok = np.isfinite(xa) & np.isfinite(xb)
            if ok.sum() > 2 and np.std(xa[ok]) > 1e-9 and np.std(xb[ok]) > 1e-9:
                C[a, b] = C[b, a] = np.corrcoef(xa[ok], xb[ok])[0, 1]
    w = np.clip(np.linalg.eigvalsh(C), 0, None)
    return float((w.sum() ** 2) / np.square(w).sum()), len(cols)

def main():
    rng = random.Random(SEED)
    gens = {"R0": gen_R0, "R1": gen_R1, "R2": gen_R2, "R3": gen_R3,
            "R5": gen_R5, "R6": gen_R6, "R7": gen_R7}
    probes = []
    for g in gens.values():
        probes += g(rng)
    tiers = list(gens.keys())
    print(f"reasoning Phase 0 | {len(probes)} probes across {tiers} | reasoners={list(REASONERS)}")

    # (1) calibration: reasoner x tier accuracy
    print("\n=== (1) CALIBRATION: accuracy by reasoner x tier (does each fail in tier-predicted ways?) ===")
    print(f"{'reasoner':12s} " + " ".join(f"{t:>6s}" for t in tiers))
    rows = {}
    traces = {rn: [] for rn in REASONERS}
    for rn, fn in REASONERS.items():
        accs = []
        for t in tiers:
            tp = [p for p in probes if p.tier == t]
            n_ok = 0
            for p in tp:
                ans, tr = fn(p)
                v, ok = grade(p, ans, tr)
                traces[rn].append((p, v))
                n_ok += int(ok)
            accs.append(n_ok / max(1, len(tp)))
        rows[rn] = accs
        print(f"{rn:12s} " + " ".join(f"{a:6.2f}" for a in accs))

    # (2) dominant failure shape per (reasoner, tier)
    print("\n=== (2) DOMINANT FAILURE SHAPE per (reasoner, tier) ===")
    for rn in REASONERS:
        for t in tiers:
            kps = [v["_kill_pattern"] for (p, v) in traces[rn] if p.tier == t and v["_kill_pattern"]]
            if kps:
                from collections import Counter
                top, n = Counter(kps).most_common(1)[0]
                print(f"  {rn:11s} {t}: {top}  ({n}/{sum(1 for (p,_) in traces[rn] if p.tier==t)})")

    # (3) effective dimensionality of the trace-vector kill-space + cross-tier distinguishability
    print("\n=== (3) RUNG-REALITY: trace-vector kill-space ===")
    allv = []
    for rn in REASONERS:
        for (p, v) in traces[rn]:
            allv.append([v[f] for f in TRACE_FIELDS])
    M = np.array(allv, dtype=float)
    ed, ncols = eff_dim(M)
    print(f"  effective dim of reasoning trace-vector kill-space: {ed:.2f} over {ncols} alive fields")
    # cross-tier mean trace signatures (are tiers distinguishable?)
    print("  mean trace signature per tier (across reasoners) — distinct rows => distinct rungs:")
    print(f"  {'tier':5s} " + " ".join(f"{f[:9]:>10s}" for f in TRACE_FIELDS))
    for t in tiers:
        vs = [v for rn in REASONERS for (p, v) in traces[rn] if p.tier == t]
        means = [np.nanmean([vv[f] for vv in vs]) for f in TRACE_FIELDS]
        print(f"  {t:5s} " + " ".join((f"{m:10.2f}" if np.isfinite(m) else f"{'-':>10s}") for m in means))

    print("\nSignal-from-failure read: the calibration staircase shows each reasoner's ceiling; the "
          "failure shapes are the gradient; distinct per-tier signatures = real rungs, overlapping = "
          "orthogonal axes mislabeled as a ladder.")

if __name__ == "__main__":
    main()
