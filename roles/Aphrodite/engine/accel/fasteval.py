"""Accelerated, EXACT evaluator and search for Tier 3C (RunPod acceleration track).

Engineering/conformance only. Frozen canary: ACCEL_CANARY_RUNPOD_v1.md.
No existing engine file is modified; this module wraps the reference.

Why this is exact by construction
---------------------------------
Every value is still an arbitrary-precision Python int produced by the SAME
expression strings evaluated against the SAME globals (`basis_v4._G`: math,
abs, the guarded pow `_pw`, no builtins). Nothing is narrowed to int64, so there
is no overflow path to get wrong. The speed comes from ALGORITHMIC reuse, not
from changing arithmetic:

1. Compile-once closures. Each expression string becomes
   `lambda acc, v, first, last: <expr>` exactly once (the reference eval()s a
   code object against a fresh locals dict per step).

2. Loop-invariant hoisting across the candidate stream. Every Tier-3C stream is
   a nest `for init: for body: for final:` with FINAL innermost (both the library
   entries and the G4 fallback). A fold's accumulator after the loop depends on
   (init, body, instance) only, so it is computed once per (init, body) block
   instead of once per candidate -- ~|FINALS| = 180x fewer loop executions.

3. Final-expression memo. Within a search, instance 0 is fixed, so whether
   final f passes instance 0 depends only on the post-loop accumulator a0. The
   set of passing finals (as positions in that segment's shuffled order) is
   memoised per a0; only those few are checked on the remaining instances.

Charge semantics are reproduced arithmetically: candidate number n (1-based,
in stream order) is evaluated iff spent0 + n - 1 < min(limit, cap), a hit is
charged spent0 + n, the search stops at max_hits, and the escrow is left at
spent0 + (#candidates evaluated). The rng is consumed by exactly the same
shuffle calls, in the same order, as `Lib.candidates` / `scratch_candidates`.

An optional NumPy step (generator qualification's survivor counting) is a
boolean reduction over already-exact comparisons, so it is exact too.
"""
import math
import random
import statistics
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

import basis_v4 as G      # noqa: E402
import engine as E        # noqa: E402
import tier3c as T        # noqa: E402

CEIL = G.CEIL
_FAIL = object()           # sentinel: the fold returned None (failure / ceiling)
_UNSET = object()

# ---------------------------------------------------------------- closures
_FN = {}


def fn(expr: str):
    """expr -> f(acc, v, first, last), evaluated against basis_v4's globals."""
    f = _FN.get(expr)
    if f is None:
        f = eval("lambda acc, v, first, last: (%s)" % expr, G._G)   # noqa: S307
        if len(_FN) > 400_000:
            _FN.clear()
        _FN[expr] = f
    return f


def _fold_acc(ifn, bfn, vals, first, last):
    """Post-loop accumulator of a fold, or _FAIL exactly where run_program
    would return None before reaching the final expression."""
    try:
        acc = ifn(0, 0, first, last)
        for v in vals:
            acc = bfn(acc, v, first, last)
            if acc is None or abs(acc) > CEIL:
                return _FAIL
    except Exception:      # noqa: BLE001
        return _FAIL
    return acc


def _final(ffn, acc, v, first, last):
    try:
        out = ffn(acc, v, first, last)
    except Exception:      # noqa: BLE001
        return None
    if out is None or abs(out) > CEIL:
        return None
    return out


def run_program(prog, nums, trailing):
    """Drop-in for basis_v4.run_program (same value, same None)."""
    vals = nums[:-1] if trailing else nums
    first, last = nums[0], nums[-1]
    if prog[0] == "expr":
        return _final(fn(prog[1]), 0, 0, first, last)
    _, init, body, final = prog
    acc = _fold_acc(fn(init), fn(body), vals, first, last)
    if acc is _FAIL:
        return None
    return _final(fn(final), acc, vals[-1] if vals else 0, first, last)


# ---------------------------------------------------------------- search
def _segments(lib, rng):
    """The candidate stream of run_tier3c.Lib.candidates, as blocks, with the
    rng consumed by the same shuffles in the same order (lazily, as there)."""
    for e, bodies in zip(lib.entries, lib._expanded):
        inits, bl, finals = list(e["inits"]), list(bodies), list(e["finals"])
        if rng:
            for lst in (inits, bl, finals):
                rng.shuffle(lst)
        yield "fold", inits, bl, finals, e["name"]
    fs = list(G.FINAL_SPACE)
    inits, bodies = list(G.INIT_SPACE), list(G.BODY_SPACE)
    if rng:
        for lst in (fs, inits, bodies):
            rng.shuffle(lst)
    yield "expr", None, None, fs, "g4_fallback"
    yield "fold", inits, bodies, fs, "g4_fallback"


def _is_reference_lib(lib):
    import run_tier3c as R
    return type(lib) is R.Lib


def _generic_search(candidates, parsed, escrow, cap, max_hits):
    hits = []
    for prog, coord in candidates:
        if escrow.remaining() <= 0 or escrow.spent >= cap:
            break
        escrow.charge(1)
        ok = True
        for nums, gold in parsed:
            got = run_program(prog, nums, True)
            if got is None or str(got) != gold:
                ok = False
                break
        if ok:
            hits.append((prog, coord, escrow.spent))
            if len(hits) >= max_hits:
                break
    return hits


def search_collect(lib, examples, escrow, cap, rng, max_hits=5):
    """Drop-in for run_tier3c.search_collect: identical hits, identical spent."""
    parsed = [(T.nums_of(t), t["gold"]) for t in examples]
    if not parsed or not _is_reference_lib(lib):
        return _generic_search(lib.candidates(rng), parsed, escrow, cap, max_hits)

    ex = []
    for nums, gold in parsed:
        vals = nums[:-1]
        ex.append((vals, nums[0], nums[-1], vals[-1] if vals else 0, gold))
    n_ex = len(ex)
    v0, f0, l0, vl0, g0 = ex[0]
    spent0 = escrow.spent
    budget = max(0, min(escrow.limit, cap) - spent0)
    hits = []
    pos = 0                                  # candidates enumerated so far
    traj = {}                                # (init, body) -> [acc per instance]

    def finish(evaluated):
        escrow.charge(evaluated)
        return hits

    for kind, inits, bodies, finals, coord in _segments(lib, rng):
        if pos >= budget:
            return finish(budget)
        ffns = [fn(f) for f in finals]
        F = len(finals)
        if kind == "expr":
            for j in range(F):
                if pos >= budget:
                    return finish(budget)
                pos += 1
                ok = True
                for vals, first, last, _vl, gold in ex:
                    got = _final(ffns[j], 0, 0, first, last)
                    if got is None or str(got) != gold:
                        ok = False
                        break
                if ok:
                    hits.append((("expr", finals[j]), coord, spent0 + pos))
                    if len(hits) >= max_hits:
                        return finish(pos)
            continue

        pass0 = {}
        for i in inits:
            ifn = fn(i)
            for b in bodies:
                if pos >= budget:
                    return finish(budget)
                key = (i, b)
                tr = traj.get(key)
                if tr is None:
                    tr = [_UNSET] * n_ex
                    tr[0] = _fold_acc(ifn, fn(b), v0, f0, l0)
                    traj[key] = tr
                a0 = tr[0]
                if a0 is _FAIL:
                    pos += F
                    continue
                plist = pass0.get(a0)
                if plist is None:
                    plist = []
                    for j in range(F):
                        got = _final(ffns[j], a0, vl0, f0, l0)
                        if got is not None and str(got) == g0:
                            plist.append(j)
                    pass0[a0] = plist
                for j in plist:
                    n = pos + j + 1
                    if n > budget:
                        break
                    ok = True
                    for k in range(1, n_ex):
                        ak = tr[k]
                        if ak is _UNSET:
                            vals, first, last, _vl, _g = ex[k]
                            ak = tr[k] = _fold_acc(ifn, fn(b), vals, first, last)
                        if ak is _FAIL:
                            ok = False
                            break
                        vals, first, last, vl, gold = ex[k]
                        got = _final(ffns[j], ak, vl, first, last)
                        if got is None or str(got) != gold:
                            ok = False
                            break
                    if ok:
                        hits.append((("fold", i, b, finals[j]), coord, spent0 + n))
                        if len(hits) >= max_hits:
                            return finish(n)
                pos += F
    return finish(min(pos, budget))


# ---------------------------------------------------------------- generator qualification
def qualify_generator(family):
    """Drop-in for tier3c.qualify_generator (identical return value).

    Program values over the pool reuse the (init, body) accumulator per probe;
    survivor counting is an exact boolean reduction (NumPy when available)."""
    target = T.witness(family)
    pool = T.tasks(family, T.POOL_SIZE, E.dev_entropy("T3C-pool-" + family, 0))
    probes = [T.nums_of(t) for t in pool]
    tvals = tuple(G.run_program(target, nums, True) for nums in probes)
    pinfo = [(nums[:-1], nums[0], nums[-1], nums[-2] if len(nums) > 1 else 0)
             for nums in probes]

    accs = {}
    wrong = {}
    for p in T.reachable_programs():
        _, i, b, f = p
        key = (i, b)
        al = accs.get(key)
        if al is None:
            ifn, bfn = fn(i), fn(b)
            al = accs[key] = [_fold_acc(ifn, bfn, vals, first, last)
                              for vals, first, last, _vl in pinfo]
        ffn = fn(f)
        vals_t = tuple(None if a is _FAIL else _final(ffn, a, vl, first, last)
                       for a, (_v, first, last, vl) in zip(al, pinfo))
        if vals_t == tvals or vals_t in wrong:
            continue
        wrong[vals_t] = p
    wrong_vals = list(wrong)

    agree = [[vals[i] is not None and vals[i] == tvals[i] for i in range(T.POOL_SIZE)]
             for vals in wrong_vals]
    try:
        import numpy as np
        mat = np.array(agree, dtype=bool).reshape(len(agree), T.POOL_SIZE)

        def count(idx):
            return int(mat[:, idx].all(axis=1).sum()) if len(agree) else 0
    except ImportError:            # pragma: no cover
        def count(idx):
            return sum(1 for row in agree if all(row[i] for i in idx))

    rng = random.Random(E.dev_entropy("T3C-draws-" + family, 0))
    rows = []
    for size in T.DEV_SIZES:
        survivors = []
        for _d in range(T.CALIBRATION_DRAWS):
            idx = rng.sample(range(T.POOL_SIZE), size)
            survivors.append(count(idx))
        mean = statistics.mean(survivors)
        sd = statistics.pstdev(survivors)
        upper = mean + 1.96 * sd / math.sqrt(len(survivors))
        rows.append({"dev_size": size, "mean_surviving_wrong_classes": round(mean, 4),
                     "upper95": round(upper, 4), "draws": T.CALIBRATION_DRAWS,
                     "meets_threshold": bool(upper < T.DISCRIM_THRESHOLD)})
        if upper < T.DISCRIM_THRESHOLD:
            return {"family": family, "qualified_dev_size": size,
                    "distinct_wrong_classes_on_pool": len(wrong_vals),
                    "calibration": rows, "QUALIFIED": True}
    return {"family": family, "qualified_dev_size": None,
            "distinct_wrong_classes_on_pool": len(wrong_vals),
            "calibration": rows, "QUALIFIED": False}


def install():
    """Substitute the accelerated search + qualification into the reference
    pipeline modules (in-process only; no file is modified)."""
    import run_tier3c as R
    R.search_collect = search_collect
    T.qualify_generator = qualify_generator
