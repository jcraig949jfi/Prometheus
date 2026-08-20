"""R12 safe predicate evaluator + the two deterministic graders (EXPERIMENTAL).

Design spec: harmonia/memory/architecture/
reasoning_ladder_frontier_synthesis_2026-05-29.md  §4(R12), §5.

Three pieces, all PURE / deterministic / NO LLM-judge:

  1. SAFE EVALUATOR  -- `compile_safe_conjecture(src) -> SafePredicate`.
     Parse the model-emitted `def conjecture(obj): return <expr>` with the `ast`
     module, REJECT anything outside a tiny whitelist (bool ops, comparisons,
     arithmetic, `obj[...]` / `obj.get(...)` feature access, numeric / bool
     literals, the bound parameter name, and a short list of safe int helpers).
     Then evaluate the validated tree with our OWN tiny tree-walking interpreter
     -- we NEVER call Python's `eval`/`exec` on the source, NEVER `compile()` it.
     Imports, attribute access beyond the feature dict, arbitrary calls, loops,
     comprehensions, lambdas, f-strings, walrus, subscript-assignment, dunder
     access, etc. are all rejected at parse time.

  2. CONJECTURE-QUALITY grader -- held-out prediction accuracy over the full
     finite universe (Jaccard + exact-partition vs the hidden target), PENALIZED
     by similarity to the naive baselines from r12_universe.naive_baselines.

  3. TEST-QUALITY grader -- expected (and worst-case) version-space entropy
     reduction of the model's proposed next falsification test over the finite
     hypothesis class H. The version space V = {h in H consistent with revealed
     data}; a single-object probe partitions V into {h(obj)=True} / {h(obj)=False};
     score = H(V) - E[H(V')] (expected info gain in bits), plus the worst-case
     (guaranteed) reduction.

The two scores are returned SEPARATELY and never fused (Opus's directive).
"""
from __future__ import annotations

import ast
import math
from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, List, Optional, Sequence, Tuple

from r12_universe import (
    Obj,
    Trial,
    Universe,
    naive_baselines,
)

# ============================================================================ #
# 1. SAFE EVALUATOR
# ============================================================================ #
# Whitelisted free helper functions a conjecture may call. All pure, total, and
# returning ints/bools -- no I/O, no recursion-into-user-code, no unbounded work.
_SAFE_FUNCS: Dict[str, Any] = {
    "abs": abs,
    "min": min,
    "max": max,
    "len": len,
    "int": int,
    "bool": bool,
    # popcount-style helper (operates on already-extracted ints, not the obj)
    "sum": sum,
}

# AST node types we permit anywhere inside the returned expression.
_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp, ast.And, ast.Or,
    ast.UnaryOp, ast.Not, ast.UAdd, ast.USub,
    ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.Compare,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.Constant,
    ast.Name, ast.Load,
    ast.Subscript, ast.Index,            # obj['feat']  (Index for py<3.9 compat)
    ast.Call,                            # only to whitelisted funcs (checked)
    ast.Tuple, ast.List,                 # only as args to min/max/sum etc.
)


class UnsafeConjecture(Exception):
    """Raised when emitted code falls outside the safe whitelist."""


@dataclass
class SafePredicate:
    """A validated, sandboxed predicate. Calling it evaluates the vetted AST with
    our own interpreter against one object dict. Never runs raw source."""
    param: str
    expr: ast.AST
    src: str
    feature_keys: Tuple[str, ...]       # the obj[...] keys it actually reads

    def __call__(self, obj: Obj) -> bool:
        return bool(_interp(self.expr, {self.param: obj}))

    def extension(self, universe: Universe) -> FrozenSet[int]:
        """Indices of objects this predicate accepts. Robust to per-object
        evaluation errors (a KeyError on a feature the obj lacks counts as a
        rejection, not a crash)."""
        out = []
        for i, o in enumerate(universe.objects):
            try:
                if self(o):
                    out.append(i)
            except Exception:
                pass
        return frozenset(out)


def _check_node(node: ast.AST, param: str, keys: set) -> None:
    """Recursively validate one AST node against the whitelist."""
    if not isinstance(node, _ALLOWED_NODES):
        raise UnsafeConjecture(f"disallowed syntax: {type(node).__name__}")

    # Names: only the bound parameter and whitelisted function names.
    if isinstance(node, ast.Name):
        if node.id != param and node.id not in _SAFE_FUNCS:
            raise UnsafeConjecture(f"disallowed name: {node.id!r}")

    # Subscript: must be obj[<const-or-expr>], on the parameter only, Load ctx.
    if isinstance(node, ast.Subscript):
        if not isinstance(node.value, ast.Name) or node.value.id != param:
            raise UnsafeConjecture("subscript only allowed on the obj parameter")
        if not isinstance(node.ctx, ast.Load):
            raise UnsafeConjecture("subscript must be a read")
        # record string keys for reporting
        sl = node.slice
        if isinstance(sl, ast.Index):       # py<3.9
            sl = sl.value
        if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
            keys.add(sl.value)

    # Calls: only to whitelisted bare-name functions; no attribute calls, no
    # kwargs, no starargs.
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _SAFE_FUNCS:
            raise UnsafeConjecture("only whitelisted bare-name calls permitted")
        if getattr(node, "keywords", None):
            raise UnsafeConjecture("keyword args not permitted")
        for a in node.args:
            if isinstance(a, ast.Starred):
                raise UnsafeConjecture("starred args not permitted")

    # Constants: numbers, bools, and strings (strings only used as subscript keys
    # which we validated above; a bare string elsewhere is harmless but we keep
    # it simple by allowing str/int/float/bool/None constants).
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float, bool, str)) and node.value is not None:
            raise UnsafeConjecture(f"disallowed constant: {node.value!r}")

    # ANY attribute access is forbidden (blocks obj.__class__, .__globals__, etc.)
    if isinstance(node, ast.Attribute):
        raise UnsafeConjecture("attribute access is forbidden")

    # Pow with a constant exponent out of the safe band is rejected at PARSE
    # time (defence in depth -- the eval-time bound in _interp also guards the
    # dynamic case). Blocks resource exhaustion via 9999 ** 99 up front.
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        rhs = node.right
        if isinstance(rhs, ast.Constant) and isinstance(rhs.value, int):
            if rhs.value < 0 or rhs.value > 8:
                raise UnsafeConjecture("exponent out of safe range [0,8]")
        lhs = node.left
        if isinstance(lhs, ast.Constant) and isinstance(lhs.value, int):
            if abs(lhs.value) > 10_000:
                raise UnsafeConjecture("pow base out of safe range")

    # Mult with a sequence-typed operand is repetition, the Mult-shaped twin of
    # the Pow exhaustion vector (HARMA-P2, 2026-08-20). Parse-time layer; the
    # dynamic case (obj-features that are strings) is guarded in _interp.
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        for side in (node.left, node.right):
            if isinstance(side, (ast.List, ast.Tuple)) or (
                    isinstance(side, ast.Constant) and isinstance(side.value, str)):
                raise UnsafeConjecture("sequence repetition is forbidden")

    for child in ast.iter_child_nodes(node):
        _check_node(child, param, keys)


def compile_safe_conjecture(src: str) -> SafePredicate:
    """Parse + validate `def conjecture(obj): return <expr>` (or a bare
    `<expr>` in the parameter `obj`). Returns a SafePredicate or raises
    UnsafeConjecture. Does NOT execute the source.
    """
    if not isinstance(src, str) or not src.strip():
        raise UnsafeConjecture("empty source")
    if len(src) > 4000:
        raise UnsafeConjecture("source too long")

    try:
        mod = ast.parse(src, mode="exec")
    except SyntaxError as e:
        raise UnsafeConjecture(f"syntax error: {e}") from e

    # Accept either a single `def conjecture(obj): return EXPR` or a bare expr.
    expr_node: Optional[ast.AST] = None
    param = "obj"

    if (len(mod.body) == 1 and isinstance(mod.body[0], ast.FunctionDef)):
        fn = mod.body[0]
        args = fn.args
        if (args.posonlyargs or args.kwonlyargs or args.vararg or args.kwarg
                or len(args.args) != 1):
            raise UnsafeConjecture("conjecture must take exactly one positional arg")
        param = args.args[0].arg
        if any(d for d in fn.decorator_list):
            raise UnsafeConjecture("decorators not permitted")
        # body must be (optional docstring/exprs we ignore) + a single return EXPR
        ret = None
        for stmt in fn.body:
            if isinstance(stmt, ast.Return):
                ret = stmt
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue   # tolerate a docstring
            else:
                raise UnsafeConjecture(
                    f"only a single `return <expr>` allowed in body, got "
                    f"{type(stmt).__name__}")
        if ret is None or ret.value is None:
            raise UnsafeConjecture("conjecture must `return` a boolean expression")
        expr_node = ret.value
    elif len(mod.body) == 1 and isinstance(mod.body[0], ast.Expr):
        expr_node = mod.body[0].value
    else:
        raise UnsafeConjecture(
            "expected a single `def conjecture(obj): return EXPR` or a bare expr")

    keys: set = set()
    _check_node(ast.Expression(body=expr_node), param, keys)
    return SafePredicate(param=param,
                         expr=ast.Expression(body=expr_node),
                         src=src, feature_keys=tuple(sorted(keys)))


# --- our own tiny tree-walking interpreter (no eval/exec, ever) ------------- #
def _interp(node: ast.AST, env: Dict[str, Any]) -> Any:
    if isinstance(node, ast.Expression):
        return _interp(node.body, env)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in env:
            return env[node.id]
        if node.id in _SAFE_FUNCS:
            return _SAFE_FUNCS[node.id]
        raise UnsafeConjecture(f"unbound name {node.id!r}")
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            r = True
            for v in node.values:
                r = _interp(v, env)
                if not r:
                    return r
            return r
        else:  # Or
            r = False
            for v in node.values:
                r = _interp(v, env)
                if r:
                    return r
            return r
    if isinstance(node, ast.UnaryOp):
        v = _interp(node.operand, env)
        if isinstance(node.op, ast.Not):
            return not v
        if isinstance(node.op, ast.USub):
            return -v
        if isinstance(node.op, ast.UAdd):
            return +v
        raise UnsafeConjecture("bad unary op")
    if isinstance(node, ast.BinOp):
        a = _interp(node.left, env)
        b = _interp(node.right, env)
        op = node.op
        if isinstance(op, ast.Add):
            return a + b
        if isinstance(op, ast.Sub):
            return a - b
        if isinstance(op, ast.Mult):
            # Sequence repetition is the Mult-shaped twin of the Pow bound
            # (HARMA-P2 soak finding, 2026-08-20): 'a' * (10**8) projected to
            # ~100 MB per call while pow was rejected. Repetition has no
            # legitimate use in a boolean conjecture over obj features.
            if isinstance(a, (str, list, tuple)) or isinstance(b, (str, list, tuple)):
                raise UnsafeConjecture("sequence repetition is forbidden")
            return a * b
        if isinstance(op, ast.Mod):
            return a % b
        if isinstance(op, ast.FloorDiv):
            return a // b
        if isinstance(op, ast.Pow):
            # bound the exponent so a**b can't blow up time/memory
            if not isinstance(b, int) or b < 0 or b > 8:
                raise UnsafeConjecture("exponent out of safe range [0,8]")
            if not isinstance(a, int) or abs(a) > 10_000:
                raise UnsafeConjecture("base out of safe range")
            return a ** b
        raise UnsafeConjecture("bad binary op")
    if isinstance(node, ast.Compare):
        left = _interp(node.left, env)
        for op, comp in zip(node.ops, node.comparators):
            right = _interp(comp, env)
            if isinstance(op, ast.Eq):
                ok = left == right
            elif isinstance(op, ast.NotEq):
                ok = left != right
            elif isinstance(op, ast.Lt):
                ok = left < right
            elif isinstance(op, ast.LtE):
                ok = left <= right
            elif isinstance(op, ast.Gt):
                ok = left > right
            elif isinstance(op, ast.GtE):
                ok = left >= right
            else:
                raise UnsafeConjecture("bad comparison op")
            if not ok:
                return False
            left = right
        return True
    if isinstance(node, ast.Subscript):
        container = _interp(node.value, env)
        sl = node.slice
        if isinstance(sl, ast.Index):     # py<3.9
            sl = sl.value
        key = _interp(sl, env)
        return container[key]             # may KeyError -> caught by .extension
    if isinstance(node, ast.Call):
        fn = _interp(node.func, env)
        args = [_interp(a, env) for a in node.args]
        return fn(*args)
    if isinstance(node, (ast.Tuple, ast.List)):
        return [_interp(e, env) for e in node.elts]
    raise UnsafeConjecture(f"cannot interpret {type(node).__name__}")


# ============================================================================ #
# 2. CONJECTURE-QUALITY grader
# ============================================================================ #
def _jaccard(a: FrozenSet[int], b: FrozenSet[int]) -> float:
    if not a and not b:
        return 1.0
    u = len(a | b)
    return len(a & b) / u if u else 1.0


@dataclass
class ConjectureScore:
    quality: float                      # final, baseline-penalized [0,1]
    raw_holdout_acc: float              # held-out exact-match accuracy
    raw_jaccard_full: float             # Jaccard to target over full universe
    exact_partition: bool               # extension == target extension exactly
    baseline_jaccards: Dict[str, float]
    max_baseline_jaccard: float
    most_similar_baseline: str
    n_holdout: int
    detail: Dict[str, Any]


def grade_conjecture(trial: Trial, pred_ext: FrozenSet[int]) -> ConjectureScore:
    """Score a conjecture (given as its EXTENSION over the universe) vs the
    hidden target. SEPARATE from test quality.

    raw signal:
       - held-out accuracy: fraction of HELD-OUT objects labelled correctly
       - Jaccard(pred, target) over the full universe; exact_partition flag

    baseline penalty (Gemini): if the conjecture is ~as similar to a NAIVE
    baseline as it is to the target, it earns ~0. Concretely:
        quality = raw_jaccard_full * (1 - max_baseline_jaccard)
    so const-true / single-literal / memorize-revealed mimics collapse toward 0
    even if they happen to score some raw Jaccard. The held-out accuracy is
    reported alongside (un-penalized) for transparency.
    """
    target = trial.target_sig
    uni = trial.universe
    n = len(uni)

    # held-out accuracy
    hold = trial.holdout_idx
    if hold:
        correct = sum(1 for i in hold
                      if (i in pred_ext) == trial.labels[i])
        holdout_acc = correct / len(hold)
    else:
        holdout_acc = float("nan")

    jac = _jaccard(pred_ext, target)
    exact = (pred_ext == target)

    # baseline similarity
    bl = naive_baselines(trial)
    bl_jac = {name: _jaccard(pred_ext, ext) for name, ext in bl.items()}
    max_bl = max(bl_jac.values()) if bl_jac else 0.0
    worst_name = max(bl_jac, key=bl_jac.get) if bl_jac else ""

    quality = jac * (1.0 - max_bl)
    # if the conjecture IS exactly a baseline, force to 0 (mimicry, no credit)
    if any(pred_ext == ext for ext in bl.values()) and not exact:
        quality = 0.0
    quality = max(0.0, min(1.0, quality))

    return ConjectureScore(
        quality=quality,
        raw_holdout_acc=holdout_acc,
        raw_jaccard_full=jac,
        exact_partition=exact,
        baseline_jaccards=bl_jac,
        max_baseline_jaccard=max_bl,
        most_similar_baseline=worst_name,
        n_holdout=len(hold),
        detail={"pred_ext_size": len(pred_ext), "target_ext_size": len(target),
                "universe_size": n},
    )


# ============================================================================ #
# 3. TEST-QUALITY grader  (version-space entropy reduction)
# ============================================================================ #
def consistent_version_space(
    trial: Trial,
) -> List[Tuple[int, FrozenSet[int]]]:
    """V = hypotheses in H consistent with ALL revealed (object,label) pairs.

    Returns a list of (H-index, signature). Each signature is the extension of a
    surviving hypothesis over the universe. We treat all members as equally
    likely (uniform prior over the consistent set) for entropy purposes.
    """
    rev = trial.revealed_idx
    labels = trial.labels
    V: List[Tuple[int, FrozenSet[int]]] = []
    for hi, (_pred, sig) in enumerate(trial.H):
        if all((i in sig) == labels[i] for i in rev):
            V.append((hi, sig))
    return V


def _entropy_bits(parts: Sequence[int]) -> float:
    """Shannon entropy (bits) of a partition given by group sizes."""
    tot = sum(parts)
    if tot <= 0:
        return 0.0
    h = 0.0
    for c in parts:
        if c > 0:
            p = c / tot
            h -= p * math.log2(p)
    return h


@dataclass
class TestScore:
    info_gain_bits: float               # expected entropy reduction (the score)
    worst_case_gain_bits: float         # guaranteed (min over outcomes) reduction
    prior_entropy_bits: float           # H(V) before the test
    version_space_size: int
    splits_true: int                    # # hypotheses predicting True on the probe
    splits_false: int
    is_in_universe: bool                # was the probed object a real universe obj
    is_held_out: bool                   # (info) was it held out vs already revealed
    optimal_gain_bits: float            # best single-object info gain available
    efficiency: float                   # info_gain / optimal_gain in [0,1]
    detail: Dict[str, Any]


def _object_index(universe: Universe, probe_obj: Obj) -> Optional[int]:
    """Match a probe object to a universe index by exact feature equality on the
    canonical features (ignores extra keys the model may have added)."""
    feats = universe.features
    for i, o in enumerate(universe.objects):
        if all(probe_obj.get(f) == o.get(f) for f in feats):
            return i
    return None


def grade_test_object(
    trial: Trial,
    probe_obj: Obj,
    V: Optional[List[Tuple[int, FrozenSet[int]]]] = None,
) -> TestScore:
    """Score a proposed next test that probes a single object.

    Mechanics:
      V          = version space consistent with revealed data (uniform prior).
      For probed object o: split V into Vtrue = {h : o in h}, Vfalse = {h: o not}.
      The true label is unknown, so EXPECTED posterior entropy weights each
      branch by |branch|/|V|; expected info gain = H(V) - E[H(branch)].
      For binary outcomes this equals the binary entropy of the split fraction.
      worst_case_gain = H(V) - max(H(Vtrue), H(Vfalse))  (guaranteed reduction;
      an adversary picks the larger remaining branch). Both are reported.
    Also computes the OPTIMAL single-object info gain over the universe so we can
    report efficiency = gain / optimal in [0,1] (mechanical, no judge).
    """
    uni = trial.universe
    if V is None:
        V = consistent_version_space(trial)
    m = len(V)
    prior_h = math.log2(m) if m > 0 else 0.0

    idx = _object_index(uni, probe_obj)
    in_universe = idx is not None
    is_held_out = in_universe and (idx in set(trial.holdout_idx))

    def split_at(obj_idx: int) -> Tuple[int, int]:
        t = sum(1 for (_hi, sig) in V if obj_idx in sig)
        return t, m - t

    if in_universe:
        st, sf = split_at(idx)
    else:
        st = sf = 0   # off-universe probe distinguishes nothing

    # expected info gain for a binary, equal-prior partition = prior entropy of
    # the WHOLE space minus expected entropy of the conditional spaces. With a
    # uniform prior over V and a deterministic label per hypothesis, each branch
    # is itself uniform, so E[H] = (st/m)*log2(st) + (sf/m)*log2(sf).
    def exp_posterior(t: int, f: int) -> float:
        tot = t + f
        if tot == 0:
            return 0.0
        e = 0.0
        if t > 0:
            e += (t / tot) * math.log2(t)
        if f > 0:
            e += (f / tot) * math.log2(f)
        return e

    if m > 0 and (st + sf) > 0:
        exp_post = exp_posterior(st, sf)
        info_gain = prior_h - exp_post
        # worst case: adversary leaves the larger branch
        worst_post = math.log2(max(st, sf)) if max(st, sf) > 0 else 0.0
        worst_gain = prior_h - worst_post
    else:
        info_gain = 0.0
        worst_gain = 0.0

    # optimal single-object gain over the universe (the best test the model COULD
    # have proposed) -- used only for the efficiency ratio, never to grade by NL.
    optimal = 0.0
    if m > 0:
        for j in range(len(uni)):
            t = sum(1 for (_hi, sig) in V if j in sig)
            f = m - t
            g = prior_h - exp_posterior(t, f)
            if g > optimal:
                optimal = g
    efficiency = (info_gain / optimal) if optimal > 1e-12 else (
        1.0 if info_gain > -1e-12 and optimal <= 1e-12 else 0.0)
    efficiency = max(0.0, min(1.0, efficiency))

    return TestScore(
        info_gain_bits=info_gain,
        worst_case_gain_bits=worst_gain,
        prior_entropy_bits=prior_h,
        version_space_size=m,
        splits_true=st,
        splits_false=sf,
        is_in_universe=in_universe,
        is_held_out=is_held_out,
        optimal_gain_bits=optimal,
        efficiency=efficiency,
        detail={"probe_index": idx},
    )


# ============================================================================ #
# convenience: grade a full emitted (conjecture_src, test_obj) artifact
# ============================================================================ #
@dataclass
class R12Result:
    safe: bool
    unsafe_reason: Optional[str]
    conjecture: Optional[ConjectureScore]
    test: Optional[TestScore]
    feature_keys: Tuple[str, ...]
    pred_ext_size: Optional[int]


def grade_emission(
    trial: Trial,
    conjecture_src: str,
    test_obj: Optional[Obj],
) -> R12Result:
    """End-to-end: compile+sandbox the conjecture, grade conjecture quality and
    test quality SEPARATELY. Unsafe code -> safe=False, both scores None (the
    failure SHAPE: an unsafe emission is recorded, not silently zero-graded)."""
    try:
        pred = compile_safe_conjecture(conjecture_src)
    except UnsafeConjecture as e:
        return R12Result(False, str(e), None, None, (), None)

    ext = pred.extension(trial.universe)
    cq = grade_conjecture(trial, ext)
    V = consistent_version_space(trial)
    tq = grade_test_object(trial, test_obj, V=V) if test_obj is not None else None
    return R12Result(True, None, cq, tq, pred.feature_keys, len(ext))


if __name__ == "__main__":
    from r12_universe import (build_bits_universe, enumerate_hypothesis_class,
                              make_trial, pred_to_str, pred_to_python)
    u = build_bits_universe(5)
    H = enumerate_hypothesis_class(u, max_terms=2)
    t = make_trial(seed=3, universe=u, H=H, n_reveal=16)
    print("target:", pred_to_str(t.target))
    # a perfect conjecture written as python over features (obj['feat'] form)
    src = "def conjecture(obj):\n    return " + pred_to_python(t.target)
    res = grade_emission(t, src, dict(t.universe.objects[t.holdout_idx[0]]))
    print("safe:", res.safe, "feature_keys:", res.feature_keys)
    print("conjecture quality:", round(res.conjecture.quality, 3),
          "holdout_acc:", round(res.conjecture.raw_holdout_acc, 3),
          "exact:", res.conjecture.exact_partition)
    print("test info_gain bits:", round(res.test.info_gain_bits, 3),
          "of optimal", round(res.test.optimal_gain_bits, 3),
          "eff", round(res.test.efficiency, 3))
