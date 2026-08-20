"""lattice_void_miner.py — Proposal B engine (Harmonia D, 2026-06-10).

Turn any operator/invariant/relation kill-lattice into either candidate
mathematics or a clean kill. Built for a3 (knot x EC functional identities),
generalizes to any generator whose claims have the shape

    f(inv_a(obj_a))  REL  g(inv_b(obj_b))

evaluated over the FULL cross-product of two object catalogs.

----------------------------------------------------------------------------
THE PRODUCT-MEASURE THEOREM (why this module is a decision procedure)
----------------------------------------------------------------------------
When obj_a and obj_b are paired by full cross-product (or sampled
independently, as a3's next() does), the joint distribution of
(inv_a(obj_a), inv_b(obj_b)) is the product of the two marginals. Therefore:

  (1) The "marginal-pairing null" (re-pair objects at random) is DEGENERATE:
      it produces *identically* the same hold-rate as the catalog statistic.
      No void can ever beat it, and no void can ever fail it. It carries
      zero discriminating power for this claim shape. (Demonstrated
      empirically by null_marginal_pairing below; do not use it as a gate.)

  (2) hold_rate == 1.0 exactly  <=>  REL holds on the SET PRODUCT
      range(f.inv_a) x range(g.inv_b). Every exact void is therefore
      certified by a set-level statement about the two transformed value
      sets A and B -- never by any knot<->EC correspondence. For the four
      a1/a3 relations the certificates are complete:

        equal         <=>  A == B == {c}            (both sides constant, equal)
        equal_mod_2   <=>  A, B parity-constant with the same parity
        divides       <=>  (0 in A => B == {0}) and every nonzero a | gcd(B)
        abs_diff_le_K <=>  max(A)-min(B) <= K and max(B)-min(A) <= K

      certificate() constructs the certificate and verify_certificate()
      re-checks that it logically entails the observed hold. A void with no
      certificate is a BUG in the sweep, not a discovery.

  (3) Consequently the only possible discovery content of a void is the
      single-catalog marginal facts the certificate cites (e.g. "every knot
      determinant is odd", "EC torsion is bounded") -- which are facts about
      ONE catalog each, plus a scalar compatibility between two summaries.
      Any "cross-domain identity" reading is a Pattern-30 red flag by
      construction.

Triviality classes assigned to each exact void (most-trivial first; the class
is the WEAKEST knowledge that fully explains the void, with population-true
explanations preferred over catalog-selection ones):
  T0 TAUTOLOGY       the two sides are the same generator computation compared
                     to itself (reflexive relation on an identical column, or
                     an injected spec.tautology_check) -- holds with no data at
                     all. Guards self-test generators like b1 (predicted==actual
                     from one flip table) from being mined as discoveries.
  T1 PIGEONHOLE      holds for arbitrary integers; property of (f,g,REL)
                     alone, independent of all catalog data.
  T1b THEOREM_PIGEONHOLE  fails for arbitrary integers, but holds for every
                     value inside a NAMED theorem's true domain (e.g. Mazur:
                     E(Q)_tors order in {1..10,12}). Population-true, not a
                     catalog artifact -- the cited theorem IS the (re)discovery.
                     Ranked above T2 because it survives catalog extension
                     whereas a constant side may be thin selection.
  T2 CONSTANT_SIDE   one transformed side is a single value; the void is an
                     absorbing-element fact (e.g. 1 divides everything). Often
                     a thin catalog fact, hence below T1b.
  T3 MARGINAL_FACT   both sides non-constant, no named theorem bounds them; the
                     certificate cites genuine value-set structure of each
                     catalog column. The cited facts are the candidate
                     (re)discoveries -- and the ones most likely to be
                     selection artifacts (closure-stress separates them).

Near-voids (hold_rate < 1 but above a band threshold) are NOT certified --
they get the statistical treatment: relation-laxity gradient + per-band
violation census + held-out split (which is only informative for near-voids;
for exact voids subset replication is logically vacuous).

Per feedback_track_d_replication_discipline, the relation semantics are
INJECTED (eval_relation), never reimplemented -- the a3 driver passes
theseus.generators.a1_catalog_cross_product._evaluate_relation verbatim.
Validator: harmonia/experiments/test_lattice_void_miner.py.
"""
from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


# ----------------------------------------------------------------------------
# Spec + evaluation
# ----------------------------------------------------------------------------
@dataclass
class LatticeSpec:
    """Everything the miner needs, with authoritative semantics injected."""
    side_a_name: str                      # e.g. "knot"
    side_b_name: str                      # e.g. "ec"
    side_a: Dict[str, List[int]]          # invariant -> raw defined values (multiplicity preserved)
    side_b: Dict[str, List[int]]
    operators: Dict[str, Callable[[int], int]]
    relations: Tuple[str, ...]
    eval_relation: Callable[[int, int, str], bool]   # injected, e.g. a1._evaluate_relation
    transform_errors: Tuple[type, ...] = (ValueError, OverflowError)  # a3's skip set
    # Optional: invariant_name -> (true-domain probe values, theorem_name). The
    # probe is a finite stand-in for the invariant's THEOREM-true range (NOT the
    # catalog sample). Only invariants with a non-trivial named bound need an
    # entry; unlisted invariants default to the unbounded _GENERIC_PROBE. Drives
    # the T1b theorem-pigeonhole tier. Empty (default) => T1b never fires =>
    # behaviour identical to the pre-T1b engine.
    domain_theorems: Dict[str, Tuple[Tuple[int, ...], str]] = field(default_factory=dict)
    # Optional: cell-dict -> reason string if this cell is a structural
    # tautology of the GENERATOR (the two sides are one computation compared to
    # itself), else None. Lets a self-test generator (b1) declare its sides
    # share a source. None (default) => only the built-in structural detector
    # (identical (op,invariant) on both sides + reflexive relation) can fire T0,
    # which is impossible for distinct-column cross-product specs like a3.
    tautology_check: Optional[Callable[[dict], Optional[str]]] = None


def _transformed_counters(side: Dict[str, List[int]],
                          operators: Dict[str, Callable[[int], int]],
                          errors: Tuple[type, ...]):
    """{(op_name, inv): (Counter(transformed value -> count), n_dropped)}."""
    out = {}
    for inv, vals in side.items():
        for op_name, op in operators.items():
            c: Counter = Counter()
            dropped = 0
            for v in vals:
                try:
                    c[op(v)] += 1
                except errors:
                    dropped += 1
            out[(op_name, inv)] = (c, dropped)
    return out


def evaluate_lattice(spec: LatticeSpec) -> List[dict]:
    """Exhaustive factored evaluation of every (f, g, inv_a, inv_b, rel) cell
    over the full object cross-product. Exact: hold_count is an integer count
    of holding (obj_a, obj_b) pairs, not an estimate.

    Factorization: REL is evaluated pointwise on the transformed value pair,
    so the cross-product sum collapses to a sum over unique transformed value
    pairs weighted by their multiplicities. This is exhaustive evaluation at
    histogram cost (resolves Proposal B §5 Q3 -- no subsampling, ever).
    """
    ta = _transformed_counters(spec.side_a, spec.operators, spec.transform_errors)
    tb = _transformed_counters(spec.side_b, spec.operators, spec.transform_errors)
    rel_cache: Dict[Tuple[int, int, str], bool] = {}
    ev = spec.eval_relation

    cells = []
    for (f, inv_a), (ca, drop_a) in ta.items():
        n_a = sum(ca.values())
        items_a = sorted(ca.items())
        for (g, inv_b), (cb, drop_b) in tb.items():
            n_b = sum(cb.values())
            items_b = sorted(cb.items())
            n_eval = n_a * n_b
            for rel in spec.relations:
                hold = 0
                for av, an in items_a:
                    for bv, bn in items_b:
                        key = (av, bv, rel)
                        h = rel_cache.get(key)
                        if h is None:
                            h = ev(av, bv, rel)
                            rel_cache[key] = h
                        if h:
                            hold += an * bn
                cells.append({
                    "f": f, "g": g, "inv_a": inv_a, "inv_b": inv_b, "rel": rel,
                    "n_a": n_a, "n_b": n_b, "n_eval": n_eval,
                    "n_dropped_a": drop_a, "n_dropped_b": drop_b,
                    "hold_count": hold,
                    "hold_rate": (hold / n_eval) if n_eval else 0.0,
                    "uniq_a": len(ca), "uniq_b": len(cb),
                    "is_exact_void": bool(n_eval) and hold == n_eval,
                })
    return cells


def cell_id(c: dict) -> str:
    return f"{c['f']}|{c['g']}|{c['inv_a']}|{c['inv_b']}|{c['rel']}"


# ----------------------------------------------------------------------------
# Certificates (exact voids only)
# ----------------------------------------------------------------------------
def _value_sets(spec: LatticeSpec, c: dict) -> Tuple[List[int], List[int]]:
    ta = _transformed_counters({c["inv_a"]: spec.side_a[c["inv_a"]]},
                               {c["f"]: spec.operators[c["f"]]},
                               spec.transform_errors)
    tb = _transformed_counters({c["inv_b"]: spec.side_b[c["inv_b"]]},
                               {c["g"]: spec.operators[c["g"]]},
                               spec.transform_errors)
    A = sorted(ta[(c["f"], c["inv_a"])][0])
    B = sorted(tb[(c["g"], c["inv_b"])][0])
    return A, B


def certificate(spec: LatticeSpec, c: dict) -> Optional[dict]:
    """Construct the set-level certificate for an exact void. Returns None if
    no certificate of the known forms exists (which, for the four a1/a3
    relations, means the cell is NOT an exact void or the sweep is buggy)."""
    A, B = _value_sets(spec, c)
    if not A or not B:
        return None
    rel = c["rel"]
    if rel == "equal":
        if len(set(A)) == 1 and set(A) == set(B):
            return {"form": "SINGLETON_EQUAL", "constant": A[0],
                    "statement": f"both sides constant == {A[0]}"}
        return None
    if rel == "equal_mod_2":
        pa, pb = {a % 2 for a in A}, {b % 2 for b in B}
        if len(pa) == 1 and pa == pb:
            p = next(iter(pa))
            return {"form": "PARITY_CONSTANT", "parity": p,
                    "statement": (f"A ⊂ {'odd' if p else 'even'} and "
                                  f"B ⊂ {'odd' if p else 'even'}")}
        return None
    if rel == "divides":
        sB = set(B)
        if 0 in A and sB != {0}:
            return None
        g = 0
        for b in B:
            g = math.gcd(g, b)
        nonzero_a = [a for a in set(A) if a != 0]
        # g == 0 <=> B == {0}: every nonzero a divides 0, and any 0 in A was
        # already gated on B == {0} above -- certificate holds unconditionally.
        if g == 0 or all(g % a == 0 for a in nonzero_a):
            return {"form": "DIVIDES_GCD", "gcd_b": g,
                    "statement": f"every a in A divides gcd(B) = {g}"
                                 + (" (B == {0}; 0 is divisible by all)" if g == 0 else "")}
        return None
    if rel.startswith("abs_diff_le_"):
        try:
            K = int(rel.split("_")[-1])
        except ValueError:
            return None
        if max(A) - min(B) <= K and max(B) - min(A) <= K:
            return {"form": "INTERVAL_WIDTH", "K": K,
                    "statement": (f"max(A)={max(A)}, min(A)={min(A)}, "
                                  f"max(B)={max(B)}, min(B)={min(B)}: "
                                  f"all pairwise |a-b| <= {K}")}
        return None
    return None


def verify_certificate(spec: LatticeSpec, c: dict, cert: dict) -> bool:
    """Verify the certificate's OWN algebraic content against freshly
    recomputed value sets, AND that the relation holds over the set product.

    v1 of this function ignored `cert` entirely and just re-evaluated all
    pairs — vacuous as a content check (garbage certificates shipped as
    "verified"). Caught by the 2026-06-10 adversarial panel (CODE lens,
    sabotage test). v2 checks the form-specific claim first; the direct
    all-pairs evaluation remains as the ground-truth leg."""
    if cert is None:
        return False
    A, B = _value_sets(spec, c)
    sA, sB = set(A), set(B)
    rel = c["rel"]
    form = cert.get("form")
    if form == "SINGLETON_EQUAL":
        content_ok = (rel == "equal" and sA == {cert["constant"]} == sB)
    elif form == "PARITY_CONSTANT":
        content_ok = (rel == "equal_mod_2"
                      and {a % 2 for a in sA} == {cert["parity"]}
                      == {b % 2 for b in sB})
    elif form == "DIVIDES_GCD":
        g = 0
        for b in sB:
            g = math.gcd(g, b)
        content_ok = (rel == "divides" and g == cert["gcd_b"]
                      and not (0 in sA and sB != {0})
                      and (g == 0 or all(g % a == 0 for a in sA if a != 0)))
    elif form == "INTERVAL_WIDTH":
        content_ok = (rel.startswith("abs_diff_le_")
                      and cert["K"] == int(rel.split("_")[-1])
                      and max(sA) - min(sB) <= cert["K"]
                      and max(sB) - min(sA) <= cert["K"])
    else:
        return False
    return content_ok and all(spec.eval_relation(a, b, rel)
                              for a in sA for b in sB)


# ----------------------------------------------------------------------------
# Nulls
# ----------------------------------------------------------------------------
# Deterministic generic-integer probe set: wide spread, primes, zeros,
# negatives, powers. Property tested: does (f, g, rel) hold on arbitrary
# integers, i.e. is the void independent of all catalog data (T1 PIGEONHOLE)?
_GENERIC_PROBE = sorted(set(
    list(range(-12, 13))
    + [17, -17, 31, 97, -97, 100, 101, 255, 256, 1000, -1000, 9973, -9973,
       4096, 99991, 2 ** 20, -(2 ** 20)]
))


def null_pigeonhole(spec: LatticeSpec, c: dict) -> dict:
    """T1: does the cell hold for arbitrary integers passed through (f, g)?
    If yes the void is a property of the operator/relation combination alone."""
    f, g = spec.operators[c["f"]], spec.operators[c["g"]]
    ok = True
    for x in _GENERIC_PROBE:
        for y in _GENERIC_PROBE:
            try:
                if not spec.eval_relation(f(x), g(y), c["rel"]):
                    ok = False
                    break
            except spec.transform_errors:
                continue
        if not ok:
            break
    return {"null": "pigeonhole", "killed": ok,
            "detail": "holds for arbitrary integers -> property of (f,g,rel) alone"
                      if ok else "fails on generic integers -> catalog-dependent"}


def null_tautology(spec: LatticeSpec, c: dict) -> dict:
    """T0: is the cell a self-comparison of one generator computation? Two
    routes: (a) the spec's injected tautology_check declares the two sides share
    a source (the b1 'predicted==actual from one flip table' case); (b) a
    built-in structural detector — identical (operator, invariant) on both sides
    under a reflexive relation, i.e. a column compared to an identical copy of
    itself. Either way the void carries zero discovery content: it would hold
    for ANY data, including data the generator never looked at.

    Checked BEFORE the certificate gate in mine(): a declared tautology is
    classified T0 even if the set-level certificate machinery does not recognise
    its shape (self-test generators need not emit one of the four a1 relations).
    For distinct-column cross-product specs with no tautology_check (a3), this
    null can never fire — backward-compatible by construction."""
    reason = None
    if spec.tautology_check is not None:
        try:
            reason = spec.tautology_check(c)
        except Exception:
            reason = None
    if reason is None and c["inv_a"] == c["inv_b"] and c["f"] == c["g"]:
        rel = c["rel"]
        try:
            reflexive = all(spec.eval_relation(v, v, rel) for v in _GENERIC_PROBE)
        except spec.transform_errors:
            reflexive = False
        if reflexive:
            reason = (f"structural: both sides {c['f']}∘{c['inv_a']} compared "
                      f"under reflexive relation {rel} (column vs identical copy)")
    return {"null": "tautology", "killed": reason is not None,
            "detail": reason or "sides are not a self-comparison of one computation"}


def null_theorem_pigeonhole(spec: LatticeSpec, c: dict) -> dict:
    """T1b: does the cell hold for every value inside a NAMED theorem's true
    domain (even though it fails for arbitrary integers, so plain pigeonhole
    missed it)? Sides without an injected domain theorem fall back to the
    unbounded _GENERIC_PROBE, so a kill here means the named theorem(s) are
    load-bearing and the void is population-true (survives catalog extension),
    not a thin selection fact. The cited theorem is the (re)discovery.

    Example (a3): mod_3(knot_inv) abs_diff_le_3 log2_floor(torsion). mod_3 caps
    side A to {0,1,2} for ANY integer; Mazur caps EC torsion order to {1..10,12}
    so log2_floor(torsion) <= 3; the interval holds for the whole population.
    Plain pigeonhole feeds 2**20 into the torsion slot (no curve over Q realises
    it) and wrongly concludes 'catalog-dependent'. This null injects the Mazur
    domain instead. Empty spec.domain_theorems => never fires (backward-compat)."""
    out = {"null": "theorem_pigeonhole", "killed": False, "theorems": [],
           "detail": "no domain theorems supplied"}
    if not spec.domain_theorems:
        return out
    dom_a = spec.domain_theorems.get(c["inv_a"])
    dom_b = spec.domain_theorems.get(c["inv_b"])
    if dom_a is None and dom_b is None:
        out["detail"] = "no named theorem bounds either side"
        return out
    probe_a = dom_a[0] if dom_a else _GENERIC_PROBE
    probe_b = dom_b[0] if dom_b else _GENERIC_PROBE
    f, g = spec.operators[c["f"]], spec.operators[c["g"]]
    cited = [t[1] for t in (dom_a, dom_b) if t]
    ok = True
    for x in probe_a:
        for y in probe_b:
            try:
                if not spec.eval_relation(f(x), g(y), c["rel"]):
                    ok = False
                    break
            except spec.transform_errors:
                continue
        if not ok:
            break
    out["killed"] = ok
    out["theorems"] = cited if ok else []
    out["detail"] = (f"holds for every value in theorem domain(s) {cited} -> "
                     "population-true restricted-domain pigeonhole"
                     if ok else
                     f"fails even within theorem domain(s) {cited} -> not "
                     "theorem-explained (genuine marginal structure)")
    return out


def null_constant_side(spec: LatticeSpec, c: dict) -> dict:
    """T2: is one transformed side a single value? If so, name the constant
    and whether the collapse came from the raw column or from the operator."""
    A, B = _value_sets(spec, c)
    out = {"null": "constant_side", "killed": False, "detail": ""}
    for side, vals, inv, op, raw in (
        ("A", A, c["inv_a"], c["f"], spec.side_a[c["inv_a"]]),
        ("B", B, c["inv_b"], c["g"], spec.side_b[c["inv_b"]]),
    ):
        if len(set(vals)) == 1:
            src = ("raw column is constant" if len(set(raw)) == 1
                   else f"operator {op} collapses {len(set(raw))} raw values")
            out["killed"] = True
            out["detail"] += (f"side {side} ({op}∘{inv}) constant == {vals[0]} "
                              f"[{src}; n={len(raw)} objects] ")
    if not out["killed"]:
        out["detail"] = "both transformed sides non-constant"
    return out


def null_relation_laxity(spec: LatticeSpec, c: dict, n_trials: int = 5,
                         seed: int = 20260610) -> dict:
    """Gradient leg: hold-rate of REL on random integer pairs drawn uniformly
    from the RAW value ranges of the two sides, passed through (f, g). How much
    of the cell's hold-rate does scale-matched noise already produce?"""
    rng = random.Random(seed)
    ra = spec.side_a[c["inv_a"]]
    rb = spec.side_b[c["inv_b"]]
    lo_a, hi_a, lo_b, hi_b = min(ra), max(ra), min(rb), max(rb)
    f, g = spec.operators[c["f"]], spec.operators[c["g"]]
    rates = []
    for _ in range(n_trials):
        hold = total = 0
        for _ in range(2000):
            x, y = rng.randint(lo_a, hi_a), rng.randint(lo_b, hi_b)
            try:
                h = spec.eval_relation(f(x), g(y), c["rel"])
            except spec.transform_errors:
                continue
            hold += h
            total += 1
        rates.append(hold / total if total else 0.0)
    mean = sum(rates) / len(rates)
    return {"null": "relation_laxity", "killed": mean >= 1.0,
            "generic_hold_rate": round(mean, 4),
            "detail": f"scale-matched random integers give hold_rate={mean:.4f}"}


def null_marginal_pairing(spec: LatticeSpec, c: dict, n_perms: int = 5,
                          seed: int = 20260610) -> dict:
    """DEGENERATE BY THEOREM under cross-product evaluation -- the statistic
    does not depend on object pairing at all. Implemented only to demonstrate
    the degeneracy empirically: random bijective re-pairings of equal-length
    samples reproduce the hold-rate up to binomial noise, always."""
    rng = random.Random(seed)
    f, g = spec.operators[c["f"]], spec.operators[c["g"]]

    # Domain-skip contract (HARMA-P14 defect): transform FIRST under the same
    # error policy _transformed_counters uses, dropping out-of-domain values —
    # a bare f(x) here crashed on every spec with domain-restricted operators,
    # which is exactly the spec class whose thin voids need this battery.
    def _dom(vals, op):
        out, dropped = [], 0
        for v in vals:
            try:
                out.append(op(v))
            except spec.transform_errors:
                dropped += 1
        return out, dropped

    ta, drop_a = _dom(spec.side_a[c["inv_a"]], f)
    tb, drop_b = _dom(spec.side_b[c["inv_b"]], g)
    if not ta or not tb:
        return {"null": "marginal_pairing", "killed": False, "degenerate": True,
                "perm_rates": [], "n_dropped": [drop_a, drop_b],
                "detail": "no in-domain values on one side; nothing to permute"}
    n = min(len(ta), len(tb), 1000)
    rates = []
    for _ in range(n_perms):
        sa = rng.sample(ta, n) if len(ta) >= n else [rng.choice(ta) for _ in range(n)]
        sb = rng.sample(tb, n) if len(tb) >= n else [rng.choice(tb) for _ in range(n)]
        rng.shuffle(sb)
        hold = sum(spec.eval_relation(x, y, c["rel"]) for x, y in zip(sa, sb))
        rates.append(hold / n)
    return {"null": "marginal_pairing", "killed": False, "degenerate": True,
            "perm_rates": [round(r, 4) for r in rates],
            "n_dropped": [drop_a, drop_b],
            "detail": ("DEGENERATE: pairing-permutation cannot move a "
                       "product-measure statistic; shown empirically, "
                       "never used as a gate")}


def null_object_domination(spec: LatticeSpec, c: dict) -> dict:
    """B2 guard: tiny support or one-object domination means 'unsampled-ish',
    not invariant. Reports support sizes; kills nothing by itself, annotates."""
    n_a, n_b = len(spec.side_a[c["inv_a"]]), len(spec.side_b[c["inv_b"]])
    return {"null": "object_domination", "killed": False,
            "n_objects_a": n_a, "n_objects_b": n_b,
            "thin": n_a < 10 or n_b < 10,
            "detail": f"support: {n_a} {spec.side_a_name} x {n_b} {spec.side_b_name}"
                      + (" -- THIN side, treat as weakly evidenced" if n_a < 10 or n_b < 10 else "")}


# ----------------------------------------------------------------------------
# Mining = sweep + certify + null cascade + classify
# ----------------------------------------------------------------------------
NEAR_VOID_BANDS = (0.999, 0.99, 0.95)


def mine(spec: LatticeSpec) -> dict:
    cells = evaluate_lattice(spec)
    voids = []
    for c in cells:
        if not c["is_exact_void"]:
            continue
        cert = certificate(spec, c)
        cert_ok = verify_certificate(spec, c, cert) if cert else False
        nulls = {
            "tautology": null_tautology(spec, c),
            "pigeonhole": null_pigeonhole(spec, c),
            "theorem_pigeonhole": null_theorem_pigeonhole(spec, c),
            "constant_side": null_constant_side(spec, c),
            "relation_laxity": null_relation_laxity(spec, c),
            "marginal_pairing": null_marginal_pairing(spec, c),
            "object_domination": null_object_domination(spec, c),
        }
        # Classify by the WEAKEST/most-population-true knowledge that explains
        # the void. T0 is checked before the certificate gate (a declared
        # self-comparison need not match a set-level certificate form). T1b
        # (named-theorem pigeonhole, population-true) outranks T2 (constant
        # side, often thin selection).
        if nulls["tautology"]["killed"]:
            tclass = "T0_TAUTOLOGY"
        elif cert is None or not cert_ok:
            tclass = "T4_NO_CERTIFICATE_BUG"      # impossible by theorem -> investigate
        elif nulls["pigeonhole"]["killed"]:
            tclass = "T1_PIGEONHOLE"
        elif nulls["theorem_pigeonhole"]["killed"]:
            tclass = "T1b_THEOREM_PIGEONHOLE"
        elif nulls["constant_side"]["killed"]:
            tclass = "T2_CONSTANT_SIDE"
        else:
            tclass = "T3_MARGINAL_FACT"
        voids.append({"cell": c, "cell_id": cell_id(c), "certificate": cert,
                      "certificate_verified": cert_ok, "nulls": nulls,
                      "triviality_class": tclass})

    near = {str(b): [c for c in cells
                     if not c["is_exact_void"] and c["hold_rate"] >= b
                     and (b == NEAR_VOID_BANDS[0] or c["hold_rate"] < _next_band(b))]
            for b in NEAR_VOID_BANDS}

    by_class = Counter(v["triviality_class"] for v in voids)
    return {
        "cells": cells,
        "voids": voids,
        "near_voids": near,
        "summary": {
            "n_cells": len(cells),
            "n_exact_voids": len(voids),
            "voids_by_class": dict(by_class),
            "n_near": {b: len(v) for b, v in near.items()},
        },
    }


def _next_band(b: float) -> float:
    bands = list(NEAR_VOID_BANDS)
    i = bands.index(b)
    return 1.0 if i == 0 else bands[i - 1]


# ----------------------------------------------------------------------------
# Same-object DIAGONAL lattice (the non-product-measure extension)
# ----------------------------------------------------------------------------
# Cells rel(f(inv_i(O)), g(inv_j(O))) evaluated per object O of ONE catalog.
# Pairing is the identity (each object with itself), NOT a cross-product, so
# the product-measure theorem deliberately FAILS here: a void can carry real
# within-object joint structure, and the re-pairing (column-shuffle) null is
# INFORMATIVE rather than degenerate. Classification per void:
#   D_MARGINAL  a set-product certificate exists on the two column ranges, but
#               only over the CATALOG-observed value sets -- the diagonal hold
#               is implied by marginals alone and may be thin selection
#               (a3-style triviality; same T1/T2/T3 taxonomy applies).
#   D_THEOREM   set-product certificate holds over the two NAMED-theorem true
#               domains (superset of the observed values) -- a population-true
#               marginal fact, not selection (the diagonal analogue of T1b). The
#               cited theorem explains it; not a within-object joint law.
#   D_JOINT     no set-product certificate, yet the diagonal holds on every
#               object -- candidate within-catalog inter-invariant LAW. The
#               permutation null quantifies how surprising the joint hold is.
#               (Theorem domains cannot rescue a D_JOINT: it already fails the
#               observed set-product, a subset of any theorem domain.)

def evaluate_diagonal_lattice(side: Dict[str, List[Optional[int]]],
                              operators: Dict[str, Callable[[int], int]],
                              relations: Tuple[str, ...],
                              eval_relation: Callable[[int, int, str], bool],
                              errors: Tuple[type, ...] = (ValueError, OverflowError),
                              n_perms: int = 200, seed: int = 20260610,
                              domain_theorems: Optional[Dict[str, Tuple[Tuple[int, ...], str]]] = None,
                              ) -> List[dict]:
    """side: invariant -> per-object aligned value lists (None = undefined;
    SAME index = same object — alignment is what carries the joint signal).

    domain_theorems (optional): invariant -> (true-domain probe, theorem_name),
    same contract as LatticeSpec.domain_theorems. When supplied, marginal voids
    that also hold over the named-theorem domain product are tagged D_THEOREM
    (population-true) and cite the theorem; absent or non-applicable, marginal
    voids stay D_MARGINAL exactly as before (backward-compatible)."""
    domain_theorems = domain_theorems or {}
    rng = random.Random(seed)
    invs = list(side)
    cells = []
    for inv_i in invs:
        for inv_j in invs:
            if inv_i == inv_j:
                continue
            pairs = [(a, b) for a, b in zip(side[inv_i], side[inv_j])
                     if a is not None and b is not None]
            if not pairs:
                continue
            col_a = [a for a, _ in pairs]
            col_b = [b for _, b in pairs]
            for f_name, f in operators.items():
                for g_name, g in operators.items():
                    try:
                        fa = [f(a) for a in col_a]
                        gb = [g(b) for b in col_b]
                    except errors:
                        continue
                    for rel in relations:
                        viol = sum(1 for x, y in zip(fa, gb)
                                   if not eval_relation(x, y, rel))
                        n = len(pairs)
                        cell = {"f": f_name, "g": g_name,
                                "inv_a": inv_i, "inv_b": inv_j, "rel": rel,
                                "n_eval": n, "hold_count": n - viol,
                                "hold_rate": (n - viol) / n,
                                "is_exact_void": viol == 0,
                                "diagonal": True}
                        if viol == 0:
                            # set-product certificate on the column ranges?
                            sA, sB = set(fa), set(gb)
                            marginal = all(eval_relation(a, b, rel)
                                           for a in sA for b in sB)
                            # permutation null: shuffle column b across objects
                            perm_void = 0
                            for _ in range(n_perms):
                                shuf = gb[:]
                                rng.shuffle(shuf)
                                if all(eval_relation(x, y, rel)
                                       for x, y in zip(fa, shuf)):
                                    perm_void += 1
                            if not marginal:
                                cell["joint_class"] = "D_JOINT"
                            else:
                                # population-true marginal? test over the named-
                                # theorem domains (observed set is a subset).
                                dom_i = domain_theorems.get(inv_i)
                                dom_j = domain_theorems.get(inv_j)
                                cited = [t[1] for t in (dom_i, dom_j) if t]
                                if cited:
                                    pa = [f(v) for v in dom_i[0]] if dom_i else sorted(sA)
                                    pb = [g(v) for v in dom_j[0]] if dom_j else sorted(sB)
                                    pop_true = all(eval_relation(a, b, rel)
                                                   for a in set(pa) for b in set(pb))
                                else:
                                    pop_true = False
                                if pop_true:
                                    cell["joint_class"] = "D_THEOREM"
                                    cell["theorems_cited"] = cited
                                else:
                                    cell["joint_class"] = "D_MARGINAL"
                            cell["perm_null_void_rate"] = perm_void / n_perms
                        cells.append(cell)
    return cells


# ----------------------------------------------------------------------------
# baseline_costume adapter (Proposal A integration -- B is A's first customer)
# ----------------------------------------------------------------------------
def void_jaccard_comparator(claim: dict, baseline_map: dict) -> tuple:
    """B's custom comparator for costume_check (the frozen contract expects B
    to pass one). Class imbalance makes raw per-key agreement useless (~99.9%
    of cells are NONVOID, so any baseline 'ties' trivially). Compare on the
    union of cells either side calls VOID: agreement = |both VOID| / |union|,
    actionable deltas = symmetric difference."""
    cv = {k for k, v in claim.items() if v == "VOID"}
    bv = {k for k, v in baseline_map.items() if v == "VOID"}
    union = cv | bv
    if not union:
        return 0.0, 0, 0
    inter = len(cv & bv)
    return inter / len(union), len(union) - inter, len(union)


def build_costume_baselines(spec: LatticeSpec, cells: List[dict]):
    """Three B-specific baselines, each a rows->{cell_id: label} callable
    recomputing void predictions from progressively stronger trivial knowledge:
      bl_pigeonhole          (f,g,rel) tautologies only — no catalog data
      bl_constant_absorber   + constant-transformed-side absorbing facts
      bl_marginal_certificate the full set-level certificate (by the theorem,
                              this must reproduce the claim EXACTLY; verdict
                              COSTUME_OF:bl_marginal_certificate is the
                              expected -- and correct -- outcome)
    Returned as a dict {name: rows->RecMap}; costume_gate injects them via
    baseline_costume.register() (see below).
    NOTE for Proposal A: the register() hook D requested is now SHIPPED by
    Harmonia B (commit cbcf8abb, 2026-06-15) — costume_gate uses it instead of
    the old CATALOG[name] monkey-patch. A's v0 generic catalog (marginal_majority
    / volume_weighted / pair_aware) still cannot express these baselines -- they
    need set-level arithmetic, not label counting (the custom-baseline path is
    load-bearing, as A's contract anticipated).
    """
    def _label_map(predicate) -> dict:
        return {cell_id(c): ("VOID" if predicate(c) else "NONVOID") for c in cells}

    def bl_pigeonhole(rows, **_kw):
        return _label_map(lambda c: null_pigeonhole(spec, c)["killed"])

    def bl_constant_absorber(rows, **_kw):
        def pred(c):
            if null_pigeonhole(spec, c)["killed"]:
                return True
            if not null_constant_side(spec, c)["killed"]:
                return False
            cert = certificate(spec, c)
            return cert is not None and verify_certificate(spec, c, cert)
        return _label_map(pred)

    def bl_marginal_certificate(rows, **_kw):
        def pred(c):
            cert = certificate(spec, c)
            return cert is not None and verify_certificate(spec, c, cert)
        return _label_map(pred)

    return {"bl_pigeonhole": bl_pigeonhole,
            "bl_constant_absorber": bl_constant_absorber,
            "bl_marginal_certificate": bl_marginal_certificate}


def costume_gate(spec: LatticeSpec, mined: dict):
    """Gate the void claim through Proposal A's shared primitive.

    DEGENERACY CAVEAT (2026-06-10 adversarial panel, C7 REFUTED; B's fix
    landed 2026-06-15): on a unique-key claim whose label_fn is derived from
    the claim itself, ANY within-key aggregating baseline (A's marginal_majority
    /pair_aware) is an identity copier and 'ties' at 1.0 — so a COSTUME_OF
    verdict from one would be NOT evidence by itself. The informative content is
    the baseline LADDER from progressively weaker trivial knowledge (pigeonhole
    < constant-absorber < full certificate). B's degeneracy guard now marks the
    aggregating-baseline tie `vacuous` when every key has one row, so the
    generic control no longer reports the spurious COSTUME_OF:marginal_majority
    (it now reads DISTINCT / INCONCLUSIVE_DEGENERATE). Returns (verdict,
    generic_control) — still interpret the ladder, not the tie.

    Injection uses baseline_costume.register() (B, commit cbcf8abb) — returns a
    fresh catalog without mutating the module-global CATALOG, so no cross-caller
    leak (the monkey-patch hazard this gate used to risk)."""
    from harmonia.primitives import baseline_costume as bc

    cells = mined["cells"]
    claim = {cell_id(c): ("VOID" if c["is_exact_void"] else "NONVOID")
             for c in cells}
    label_fn = lambda c: "VOID" if c["is_exact_void"] else "NONVOID"
    baselines = build_costume_baselines(spec, cells)
    cat = bc.CATALOG
    for name, fn in baselines.items():
        cat = bc.register(name, fn, catalog=cat)   # non-mutating injection
    verdict = bc.costume_check(
        claim, cells, tuple(baselines),
        key_fn=cell_id, label_fn=label_fn,
        comparator=void_jaccard_comparator, catalog=cat,
    )
    # Degeneracy control: A's generic catalog on the same wiring. Post-guard the
    # marginal_majority tie is suppressed as vacuous => DISTINCT, not the old
    # spurious COSTUME_OF:marginal_majority (B closed this loop).
    generic_control = bc.costume_check(
        claim, cells, ("marginal_majority", "volume_weighted"),
        key_fn=cell_id, label_fn=label_fn,
        comparator=void_jaccard_comparator,
    )
    return verdict, generic_control
