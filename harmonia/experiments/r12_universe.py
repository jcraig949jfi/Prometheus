"""R12 finite-universe generator + grammar/hypothesis-class (EXPERIMENTAL).

Part of the reasoning-ladder R12 "conjecture generation under falsification"
grader. Design spec: harmonia/memory/architecture/
reasoning_ladder_frontier_synthesis_2026-05-29.md  §4(R12), §5.

This module is PURE and deterministic (no LLM, no network). It builds:

  1. A finite phase space U of N objects, each a frozen dict of computable
     INTEGER features. Two universes are provided:
       - "bits"  : 5 boolean-feature vectors  -> 32 objects, feature dict of 0/1.
       - "tuples": integer 2-tuples on a small grid -> up to ~200 objects.
     The default and the one used for grading is "bits" (clean version-space
     enumeration; small enough that the full hypothesis class H is tractable).

  2. A GRAMMAR Gamma of restricted boolean predicates over the features
     (literals, AND/OR of <= k literals, plus comparisons on integer features).
     `enumerate_hypothesis_class` materialises EVERY predicate in Gamma up to a
     size bound -> the finite hypothesis class H used for version-space scoring.

  3. A randomized HIDDEN TARGET rule per trial: we pick a random member of H as
     ground truth, then reveal a labelled random subset and hold out the rest.
     Randomizing the target + the revealed subset per trial is the anti-memo
     control (§4: "Randomize the target per trial").

  4. NAIVE BASELINE predicates (constant-true/false, single most-correlated
     literal, majority-on-revealed) used by the conjecture grader to PENALIZE
     conjectures that merely mimic a trivial rule (§4, Gemini: "penalized by
     similarity to naive baselines").

Each predicate in H is represented as a small immutable AST-like tuple tree so
it is hashable, enumerable, printable, and evaluable WITHOUT any code execution.
The SAFE evaluator for *model-emitted* Python lives in r12_grader.py; this
module's own predicates never touch eval/exec.
"""
from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple

# An "object" is a mapping feature-name -> int. We keep them as plain dicts but
# always treat them read-only.
Obj = Dict[str, int]

# A predicate tree node is one of:
#   ("const", 0|1)
#   ("lit",   feat, want)         # feat == want   (want in {0,1} for bits)
#   ("cmp",   feat, op, k)        # feat <op> k     op in {"<","<=",">",">=","==","!="}
#   ("not",   node)
#   ("and",   (node, ...))
#   ("or",    (node, ...))
Pred = tuple


# --------------------------------------------------------------------------- #
# Universe builders
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Universe:
    name: str
    features: Tuple[str, ...]          # ordered feature names
    objects: Tuple[Obj, ...]           # the finite phase space
    feat_domain: Dict[str, Tuple[int, ...]]  # name -> sorted distinct values seen

    def __len__(self) -> int:
        return len(self.objects)


def build_bits_universe(n_bits: int = 5) -> Universe:
    """Boolean-feature vectors: 2**n_bits objects, features f0..f{n-1} in {0,1}.

    Also exposes a derived integer feature `popcount` (number of 1s) so the
    grammar can pose genuine integer comparisons, not only literals. popcount is
    a legitimate computable feature of the object, available to the model too.
    """
    feats = tuple(f"f{i}" for i in range(n_bits)) + ("popcount",)
    objs: List[Obj] = []
    for bits in itertools.product((0, 1), repeat=n_bits):
        o: Obj = {f"f{i}": b for i, b in enumerate(bits)}
        o["popcount"] = sum(bits)
        objs.append(o)
    domain = {f"f{i}": (0, 1) for i in range(n_bits)}
    domain["popcount"] = tuple(range(0, n_bits + 1))
    return Universe("bits", feats, tuple(objs), domain)


def build_tuples_universe(lo: int = 0, hi: int = 7) -> Universe:
    """Integer 2-tuples (x, y) on [lo, hi]^2 with derived features.

    Features: x, y, s=x+y, d=|x-y|, mx=max(x,y). ~ (hi-lo+1)**2 objects.
    """
    feats = ("x", "y", "s", "d", "mx")
    objs: List[Obj] = []
    rng_vals = range(lo, hi + 1)
    for x in rng_vals:
        for y in rng_vals:
            objs.append({"x": x, "y": y, "s": x + y, "d": abs(x - y),
                         "mx": max(x, y)})
    domain: Dict[str, Tuple[int, ...]] = {}
    for f in feats:
        domain[f] = tuple(sorted({o[f] for o in objs}))
    return Universe("tuples", feats, tuple(objs), domain)


# --------------------------------------------------------------------------- #
# Predicate evaluation (for OUR OWN trees only — never model code)
# --------------------------------------------------------------------------- #
def eval_pred(node: Pred, obj: Obj) -> bool:
    """Evaluate one of our internal predicate trees against an object. Pure."""
    tag = node[0]
    if tag == "const":
        return bool(node[1])
    if tag == "lit":
        _, feat, want = node
        return obj[feat] == want
    if tag == "cmp":
        _, feat, op, k = node
        v = obj[feat]
        if op == "<":
            return v < k
        if op == "<=":
            return v <= k
        if op == ">":
            return v > k
        if op == ">=":
            return v >= k
        if op == "==":
            return v == k
        if op == "!=":
            return v != k
        raise ValueError(f"bad op {op}")
    if tag == "not":
        return not eval_pred(node[1], obj)
    if tag == "and":
        return all(eval_pred(c, obj) for c in node[1])
    if tag == "or":
        return any(eval_pred(c, obj) for c in node[1])
    raise ValueError(f"bad node {node!r}")


def pred_to_str(node: Pred) -> str:
    """Human-readable rendering of an internal predicate tree."""
    tag = node[0]
    if tag == "const":
        return "True" if node[1] else "False"
    if tag == "lit":
        _, feat, want = node
        return f"{feat}=={want}"
    if tag == "cmp":
        _, feat, op, k = node
        return f"{feat}{op}{k}"
    if tag == "not":
        return f"not({pred_to_str(node[1])})"
    if tag == "and":
        return "(" + " and ".join(pred_to_str(c) for c in node[1]) + ")"
    if tag == "or":
        return "(" + " or ".join(pred_to_str(c) for c in node[1]) + ")"
    return repr(node)


def pred_to_python(node: Pred, param: str = "obj") -> str:
    """Render an internal predicate tree as a Python boolean expression that
    accesses features via `obj['feat']` -- i.e. exactly the form the SAFE
    evaluator accepts. Used for demos, the gold conjecture in tests, and to show
    the model the required feature-access convention.
    """
    tag = node[0]
    if tag == "const":
        return "True" if node[1] else "False"
    if tag == "lit":
        _, feat, want = node
        return f"{param}['{feat}'] == {want}"
    if tag == "cmp":
        _, feat, op, k = node
        return f"{param}['{feat}'] {op} {k}"
    if tag == "not":
        return f"(not ({pred_to_python(node[1], param)}))"
    if tag == "and":
        return "(" + " and ".join(pred_to_python(c, param) for c in node[1]) + ")"
    if tag == "or":
        return "(" + " or ".join(pred_to_python(c, param) for c in node[1]) + ")"
    return repr(node)


def pred_signature(node: Pred, universe: Universe) -> FrozenSet[int]:
    """The EXTENSION of a predicate: the frozenset of object indices it accepts.

    Two syntactically different predicates with the same extension are the same
    HYPOTHESIS for version-space purposes; we dedupe H by signature.
    """
    return frozenset(i for i, o in enumerate(universe.objects) if eval_pred(node, o))


# --------------------------------------------------------------------------- #
# Grammar Gamma -> enumerate the finite hypothesis class H
# --------------------------------------------------------------------------- #
def _atoms(universe: Universe) -> List[Pred]:
    """Atomic predicates: literals on each feature value + comparisons.

    For binary features we emit f==0 / f==1. For integer features we emit
    f<=k and f>=k threshold comparisons across the observed domain (interior
    cut points only — endpoints would duplicate const-true/false).
    """
    atoms: List[Pred] = []
    for feat in universe.features:
        dom = universe.feat_domain[feat]
        if set(dom) <= {0, 1}:
            atoms.append(("lit", feat, 0))
            atoms.append(("lit", feat, 1))
        else:
            vals = list(dom)
            # interior thresholds so each comparison is non-trivial
            for k in vals[1:]:
                atoms.append(("cmp", feat, ">=", k))
            for k in vals[:-1]:
                atoms.append(("cmp", feat, "<=", k))
            # a couple of equality cuts (e.g. popcount==2) add expressivity
            for k in vals:
                atoms.append(("cmp", feat, "==", k))
    return atoms


def enumerate_hypothesis_class(
    universe: Universe,
    max_terms: int = 2,
    include_or: bool = True,
    max_size: Optional[int] = None,
) -> List[Tuple[Pred, FrozenSet[int]]]:
    """Materialise H = every predicate in Gamma up to `max_terms` atoms, deduped
    by extension over `universe`.

    Gamma (size bound k = max_terms):
        const True/False
        single atom
        AND of up to k DISTINCT atoms
        OR  of up to k DISTINCT atoms   (if include_or)
    Returns a list of (canonical_pred, signature) with UNIQUE signatures. The
    canonical pred is the smallest tree found for that extension (for printing).

    This is the FINITE hypothesis class the test-quality grader scores against.
    """
    atoms = _atoms(universe)
    if max_size is not None:
        atoms = atoms[:max_size]

    by_sig: Dict[FrozenSet[int], Pred] = {}

    def offer(node: Pred) -> None:
        sig = pred_signature(node, universe)
        prev = by_sig.get(sig)
        if prev is None or _tree_size(node) < _tree_size(prev):
            by_sig[sig] = node

    offer(("const", 1))
    offer(("const", 0))
    for a in atoms:
        offer(a)
    # AND / OR of 2..max_terms distinct atoms
    for r in range(2, max_terms + 1):
        for combo in itertools.combinations(atoms, r):
            offer(("and", tuple(combo)))
            if include_or:
                offer(("or", tuple(combo)))

    return [(node, sig) for sig, node in by_sig.items()]


def _tree_size(node: Pred) -> int:
    tag = node[0]
    if tag in ("const", "lit", "cmp"):
        return 1
    if tag == "not":
        return 1 + _tree_size(node[1])
    if tag in ("and", "or"):
        return 1 + sum(_tree_size(c) for c in node[1])
    return 1


# --------------------------------------------------------------------------- #
# Trial: hidden target + revealed/held-out split  (anti-memo randomization)
# --------------------------------------------------------------------------- #
@dataclass
class Trial:
    universe: Universe
    target: Pred                       # hidden ground-truth predicate (in H)
    target_sig: FrozenSet[int]         # its extension over the universe
    revealed_idx: Tuple[int, ...]      # indices shown to the model (labelled)
    holdout_idx: Tuple[int, ...]       # indices held out
    labels: Dict[int, bool]            # idx -> ground-truth label (ALL objects)
    seed: int = 0
    H: List[Tuple[Pred, FrozenSet[int]]] = field(default_factory=list, repr=False)

    # convenience views -----------------------------------------------------
    def revealed_objects(self) -> List[Tuple[Obj, bool]]:
        return [(self.universe.objects[i], self.labels[i]) for i in self.revealed_idx]

    def all_labels_vec(self) -> List[bool]:
        return [self.labels[i] for i in range(len(self.universe))]


def _jaccard_idx(a: FrozenSet[int], b: FrozenSet[int]) -> float:
    if not a and not b:
        return 1.0
    u = len(a | b)
    return len(a & b) / u if u else 1.0


def make_trial(
    seed: int,
    universe: Optional[Universe] = None,
    max_terms: int = 2,
    n_reveal: int = 8,
    H: Optional[List[Tuple[Pred, FrozenSet[int]]]] = None,
    min_target_terms: int = 1,
    require_nontrivial: bool = True,
    balance_band: Tuple[float, float] = (0.25, 0.75),
    max_literal_sim: float = 0.85,
) -> Trial:
    """Construct one randomized trial.

    - Hidden target = a random member of H, drawn from the NON-DEGENERATE pool:
      not constant, extension size inside `balance_band` * |U| (so the rule is
      genuinely discriminating, not "accept ~everything"), AND not within
      `max_literal_sim` Jaccard of any single atom (so the rule is not just a
      relabelled single feature -- otherwise the baseline penalty would
      legitimately but uninterestingly zero every conjecture). This makes the
      conjecture-quality score meaningful: a good conjecture earns real credit.
    - Revealed subset = `n_reveal` random object indices, balanced so the model
      sees BOTH positives and negatives when possible. Default 8 keeps the
      version space > 1 so test-quality has signal.
    """
    rng = random.Random(seed)
    if universe is None:
        universe = build_bits_universe(5)
    if H is None:
        H = enumerate_hypothesis_class(universe, max_terms=max_terms)

    n = len(universe)
    n_reveal = min(n_reveal, n)

    # pick a non-degenerate, non-single-literal, balanced target
    candidates = H
    if require_nontrivial:
        lo, hi = balance_band
        lo_n, hi_n = lo * n, hi * n
        atom_sigs = [pred_signature(a, universe) for a in _atoms(universe)]
        pool = []
        for (p, s) in H:
            if not (lo_n <= len(s) <= hi_n):
                continue
            if max(_jaccard_idx(s, a) for a in atom_sigs) > max_literal_sim:
                continue
            pool.append((p, s))
        if pool:
            candidates = pool
        else:
            candidates = [(p, s) for (p, s) in H if 0 < len(s) < n] or H
    target, target_sig = rng.choice(candidates)

    labels = {i: (i in target_sig) for i in range(n)}

    # balanced reveal: sample positives and negatives separately when possible
    pos = [i for i in range(n) if labels[i]]
    neg = [i for i in range(n) if not labels[i]]
    rng.shuffle(pos)
    rng.shuffle(neg)
    half = n_reveal // 2
    take_pos = min(half, len(pos))
    take_neg = min(n_reveal - take_pos, len(neg))
    take_pos = min(n_reveal - take_neg, len(pos))  # rebalance if neg was short
    revealed = pos[:take_pos] + neg[:take_neg]
    rng.shuffle(revealed)
    revealed = tuple(sorted(revealed))
    holdout = tuple(i for i in range(n) if i not in set(revealed))

    return Trial(universe=universe, target=target, target_sig=target_sig,
                 revealed_idx=revealed, holdout_idx=holdout, labels=labels,
                 seed=seed, H=H)


# --------------------------------------------------------------------------- #
# Naive baselines (the conjecture grader penalizes similarity to these)
# --------------------------------------------------------------------------- #
def naive_baselines(trial: Trial) -> Dict[str, FrozenSet[int]]:
    """Return {name -> extension} for the naive predicates a lazy/overfit model
    might emit. Each extension is over the FULL universe (object indices).

      const_true   : accept everything
      const_false  : accept nothing
      majority      : the constant matching the majority label on the REVEALED set
      best_literal : the single atom from Gamma with highest agreement on the
                     REVEALED set (the "mimic-a-naive single feature" baseline)
      memorize_pos : accept EXACTLY the revealed positives, reject all else
                     (the "overfit-to-revealed" baseline — Gemini's overfit case)
    """
    uni = trial.universe
    n = len(uni)
    out: Dict[str, FrozenSet[int]] = {}
    out["const_true"] = frozenset(range(n))
    out["const_false"] = frozenset()

    rev = trial.revealed_idx
    pos_rev = sum(1 for i in rev if trial.labels[i])
    maj_true = pos_rev * 2 >= len(rev)
    out["majority"] = frozenset(range(n)) if maj_true else frozenset()

    # best single atom by agreement on revealed labels
    best_sig: Optional[FrozenSet[int]] = None
    best_agree = -1.0
    for atom in _atoms(uni):
        sig = pred_signature(atom, uni)
        agree = sum(1 for i in rev if (i in sig) == trial.labels[i])
        if agree > best_agree:
            best_agree = agree
            best_sig = sig
    out["best_literal"] = best_sig if best_sig is not None else frozenset()

    # overfit: exactly the revealed positives
    out["memorize_pos"] = frozenset(i for i in rev if trial.labels[i])
    return out


# --------------------------------------------------------------------------- #
# self-test when run directly
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    u = build_bits_universe(5)
    H = enumerate_hypothesis_class(u, max_terms=2)
    print(f"universe={u.name}  |U|={len(u)}  features={u.features}")
    print(f"|H| (distinct extensions, max_terms=2) = {len(H)}")
    t = make_trial(seed=1, universe=u, H=H, n_reveal=16)
    print(f"target = {pred_to_str(t.target)}  |ext|={len(t.target_sig)}")
    print(f"revealed={len(t.revealed_idx)}  holdout={len(t.holdout_idx)}")
    bl = naive_baselines(t)
    print("baselines:", {k: len(v) for k, v in bl.items()})
    ut = build_tuples_universe()
    print(f"tuples universe |U|={len(ut)} features={ut.features} "
          f"|H|={len(enumerate_hypothesis_class(ut, max_terms=2))}")
