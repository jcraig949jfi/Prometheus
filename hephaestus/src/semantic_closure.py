"""Semantic-only closure test for MINT-0001 (operator ruling on Q1/Q7, 2026-09-01).

Strip parsing away. Inputs are typed semantic state:
    q : quantifier in {universal, negative_universal, existential}
    d : domain size (int >= 0)
    s : satisfier count (int, 0 <= s <= d)
Target: the nine-row truth table the operator specified (plus concrete instances of "n>0").

Three arms, same table, same budget accounting (number of distinct expressions evaluated):
  A0  frozen Prometheus primitives (agents/hephaestus/src/forge_primitives.py), bottom-up
      enumeration, ONE expression over (d, s) must fit all quantifiers.  (No routing.)
  A1  same primitives, but with per-quantifier routing: one expression per quantifier
      (this is exactly what Apollo's guarded composition provides).
  B   generic small expression language: ==, <, <=, >, >=, not, and, or, +, -, constants 0/1,
      if-then-else is NOT needed because routing is per quantifier as in A1.
  C   the v3 kernel from the Master Smith session.
Output coercion in A0/A1: Python truthiness ONLY. No `== const` is granted to arm A; equality
must come from a primitive (information_sufficiency returns strings, which are all truthy, so it
cannot be used as a test; pigeonhole_check returns a real bool).

Interpretation rule, fixed in advance (operator, Q7): if A1 synthesises the table, MINT-0001's
kernel is a Level-1 COMPOSITION and the wall was a routing/search problem, not a missing operator.
If A cannot but B immediately can, an operator family is genuinely missing from the frozen set.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))
import forge_primitives as fp  # noqa: E402

QS = ["universal", "negative_universal", "existential"]
# The operator's table, with n>0 instantiated at several sizes so that "s<n" has several witnesses.
ROWS: list[tuple[str, int, int, bool]] = []
for q in QS:
    ROWS.append((q, 0, 0, q != "existential"))
for n in (1, 2, 3, 5):
    for s in range(0, n + 1):
        ROWS.append(("universal", n, s, s == n))
        ROWS.append(("negative_universal", n, s, s == 0))
        ROWS.append(("existential", n, s, s >= 1))
POINTS = sorted({(d, s) for _, d, s, _ in ROWS})


def target(q: str) -> tuple[bool, ...]:
    return tuple(t for qq, d, s, t in ROWS if qq == q)


def truth_vector(fn) -> tuple[bool, ...] | None:
    out = []
    for d, s in POINTS:
        try:
            v = fn(d, s)
            out.append(bool(v))
        except Exception:  # noqa: BLE001
            return None
    return tuple(out)


# ── Arm A: frozen primitives, bottom-up, observational equivalence on POINTS ────────────────
# Integer-typed primitives only (the others need lists/strings/graphs that nothing here builds).
A_OPS = {
    "all_but_n": (2, lambda a, b: fp.all_but_n(a, b)),
    "pigeonhole_check": (2, lambda a, b: fp.pigeonhole_check(a, b)),
    "fencepost_count_T": (1, lambda a: fp.fencepost_count(a, True)),
    "fencepost_count_F": (1, lambda a: fp.fencepost_count(a, False)),
    "modular_arithmetic": (3, lambda a, b, m: fp.modular_arithmetic(a, b, m) if m else None),
    "coin_flip_independence": (2, lambda n, k: fp.coin_flip_independence(n, k) if 0 <= k <= n else None),
    "information_sufficiency": (2, lambda a, b: fp.information_sufficiency(a, b)),   # strings: always truthy
    "parity_check_pair": (2, lambda a, b: fp.parity_check([a, b])),                    # strings: always truthy
}
B_OPS = {
    "eq": (2, lambda a, b: a == b), "lt": (2, lambda a, b: a < b), "le": (2, lambda a, b: a <= b),
    "gt": (2, lambda a, b: a > b), "ge": (2, lambda a, b: a >= b),
    "not": (1, lambda a: not a), "and": (2, lambda a, b: bool(a) and bool(b)), "or": (2, lambda a, b: bool(a) or bool(b)),
    "add": (2, lambda a, b: a + b), "sub": (2, lambda a, b: a - b),
}
TERMINALS = {"d": lambda d, s: d, "s": lambda d, s: s, "0": lambda d, s: 0, "1": lambda d, s: 1}


def enumerate_arm(ops: dict, max_depth: int, targets: dict[str, tuple[bool, ...]], budget: int):
    """Bottom-up enumeration with observational-equivalence pruning on the raw VALUE vector
    (so `d-s` and `s-d` are distinct programs); truthiness is applied only when checking targets."""
    t0 = time.time()
    seen: dict[tuple, str] = {}
    layers: list[list[tuple[str, object]]] = []
    evaluated = 0
    found: dict[str, tuple[str, int]] = {}
    cur = []
    for name, f in TERMINALS.items():
        vec = tuple(f(d, s) for d, s in POINTS)
        seen[vec] = name; cur.append((name, f)); evaluated += 1
    layers.append(cur)

    def check(name, f):
        tv = truth_vector(f)
        if tv is None:
            return
        for q, tgt in targets.items():
            if q not in found and tv == tgt:
                found[q] = (name, len(layers))

    for name, f in layers[0]:
        check(name, f)
    for depth in range(1, max_depth + 1):
        nxt = []
        pool = [e for L in layers for e in L]
        for opname, (ar, op) in ops.items():
            for args in itertools.product(pool, repeat=ar):
                if evaluated >= budget:
                    break
                if not any(a in layers[-1] for a in args):
                    continue  # at least one arg from the newest layer, else already enumerated
                fs = [a[1] for a in args]
                def f(d, s, op=op, fs=fs):
                    return op(*[g(d, s) for g in fs])
                try:
                    vec = tuple(f(d, s) for d, s in POINTS)
                except Exception:  # noqa: BLE001
                    evaluated += 1; continue
                evaluated += 1
                if vec in seen:
                    continue
                expr = f"{opname}({', '.join(a[0] for a in args)})"
                seen[vec] = expr; nxt.append((expr, f)); check(expr, f)
            if evaluated >= budget:
                break
        layers.append(nxt)
        if len(found) == len(targets) or evaluated >= budget:
            break
    return {"found": found, "evaluated": evaluated, "distinct_programs": len(seen), "depth_reached": len(layers) - 1,
            "seconds": round(time.time() - t0, 2), "budget": budget}


def arm_A0(budget: int, max_depth: int = 3):
    """One expression over (d, s) must reproduce ALL quantifiers' columns at once: impossible unless
    the columns coincide, which they do not. Reported to make the routing dependency explicit."""
    tgt_all = {"all_quantifiers_jointly": tuple(t for _, _, _, t in ROWS)}  # length 3*len(POINTS)
    # A single (d,s)->bool function yields len(POINTS) values, not 3x; so joint fit is impossible by
    # arity. We record that as the result rather than pretending to search.
    return {"found": {}, "note": "a single f(d,s) produces one column; the three quantifier columns differ "
                                 "on POINTS (e.g. d=0,s=0 -> T,T,F), so no routing-free expression can fit. "
                                 "Routing on the quantifier is REQUIRED; it is supplied by Apollo's guards.",
            "evaluated": 0, "budget": budget}


def arm_C():
    spec = importlib.util.spec_from_file_location(
        "v3", ROOT / "hephaestus/deep_mint_sessions/20260901T073136Z/candidates/v3_quantified_truth.py")
    v3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v3)
    qmap = {"universal": "universal", "negative_universal": "neg_universal", "existential": "existential"}
    ok = 0
    for q, d, s, t in ROWS:
        ok += int(v3.quantified_truth(qmap[q], d, s) == t)
    return {"rows": len(ROWS), "correct": ok, "kernel_lines": 10}


def main(budget: int = 200_000):
    targets = {q: target(q) for q in QS}
    res = {"table_rows": len(ROWS), "points": POINTS, "budget_per_arm": budget}
    res["A0_frozen_primitives_no_routing"] = arm_A0(budget)
    res["A1_frozen_primitives_with_routing"] = enumerate_arm(A_OPS, 3, targets, budget)
    res["B_generic_expression_language"] = enumerate_arm(B_OPS, 3, targets, budget)
    res["C_v3_kernel"] = arm_C()
    a1 = res["A1_frozen_primitives_with_routing"]["found"]; b = res["B_generic_expression_language"]["found"]
    if len(a1) == len(QS):
        verdict = ("A1 SYNTHESISES THE TABLE: the kernel is a Level-1 COMPOSITION of frozen primitives "
                   "(pigeonhole_check / all_but_n / constants) under per-quantifier routing. MINT-0001 was a "
                   "routing/search/representation problem, NOT a missing operator. Reclassify.")
    elif len(b) == len(QS):
        verdict = ("A cannot express the table under truthiness; B does immediately. An operator family "
                   "(boolean/comparison over counts) is genuinely missing from the frozen set: Level-2 candidate.")
    else:
        verdict = "Neither arm synthesised the table within budget/depth; inconclusive at this depth."
    res["verdict"] = verdict
    out = ROOT / "hephaestus/mint_queue/MINT-0001/semantic_closure_result.json"
    out.write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k not in ("points",)}, indent=1, default=str))
    return res


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 200_000)
