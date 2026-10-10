"""Null ladder for list-program families (Beta-04 E1). Scored on held-out TEST examples; tribunal agreement is reported.

Every baseline is fitted on DEV only. Two verdicts are recorded:
  selected  : the model the baseline picks on dev alone (fixed preference order) solves test;
  hindsight : ANY dev-consistent model in the baseline's class solves test (N6-style; favours the null).
The admission gate uses HINDSIGHT (the stronger null) for the closed-form baselines. SMALL SEARCH follows the
contract protocol: the first dev-consistent program in enumeration order. `SOLVED` = correct on ALL test examples.

Ladder (in report order):
  constant   modal dev output
  lookup     exact dev-input match, else the modal dev output
  reactive   memoryless: Int output = g(one scalar feature in len/head/last/sum/max/min), with g a dev lookup
             table (+ affine or modal fallback) or an exact affine fit. List output = an elementwise transducer
             y_i = g(x_i) (map-like), or a keep(x_i) filter with a table + threshold/parity-rule fallback
             (filter-like). Scan-like outputs (one longer) use a constant y_0.
  history2   short fixed history: Int output = g(x[-2], x[-1]). List output = y_i = g(x[i-1], x[i]). g is a table
             with affine fallback, or an exact affine fit. Pad 0.
  library    about 45 fixed standard list programs (contract terms, plus sorted/dedupe in Python), raw or with an
             exact affine output correction (Int: c1*v + c0; List of equal length: elementwise)
  small      exhaustive typed enumeration (tenum, base grammar), first dev-consistent within B_small
"""
import json
from fractions import Fraction
from typing import Callable, Dict, List, Optional

import interp_a as A
import tenum

FEATURES = {
    "len": len, "head": lambda xs: xs[0] if xs else None, "last": lambda xs: xs[-1] if xs else None,
    "sum": sum, "max": lambda xs: max(xs) if xs else None, "min": lambda xs: min(xs) if xs else None,
}


def _j(v):
    return json.dumps(v)


def modal(vals):
    cnt, first = {}, {}
    for i, v in enumerate(vals):
        k = _j(v)
        cnt[k] = cnt.get(k, 0) + 1
        first.setdefault(k, i)
    best = max(cnt, key=lambda k: (cnt[k], -first[k]))
    return json.loads(best)


def solve_linear(rows):
    """rows: [(features tuple, y)] -> integer-valued exact affine coefficients (Fractions) or None."""
    if not rows:
        return None
    n = len(rows[0][0])
    M = [[Fraction(v) for v in f] + [Fraction(y)] for f, y in rows]
    piv_cols, r = [], 0
    for c in range(n):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [v / pv for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                fct = M[i][c]
                M[i] = [a - fct * b for a, b in zip(M[i], M[r])]
        piv_cols.append(c)
        r += 1
        if r == len(M):
            break
    for i in range(r, len(M)):
        if M[i][n] != 0:
            return None
    coef = [Fraction(0)] * n
    for i, c in enumerate(piv_cols):
        coef[c] = M[i][n]
    for f, y in rows:                                    # verify
        if sum(cf * v for cf, v in zip(coef, f)) != y:
            return None
    return coef


def affine_pred(coef, feats):
    if coef is None or any(v is None for v in feats):
        return None
    v = sum(c * f for c, f in zip(coef, feats))
    return int(v) if v.denominator == 1 else None


# ---------------------------------------------------------------- scoring helpers
def score(pred: Callable, examples):
    ok = 0
    for xs, y in examples:
        try:
            p = pred(xs)
        except Exception:                                # noqa: BLE001  (a baseline crash is a wrong answer)
            p = None
        if p is not None and p == y and type(p) is type(y):
            ok += 1
    return ok


def verdict(models: List[tuple], dev, test):
    """models: [(name, predictor)] in preference order. Returns dict with selected / hindsight verdicts."""
    nd, nt = len(dev), len(test)
    consistent = [(n, p) for n, p in models if score(p, dev) == nd]
    out = {"n_models": len(models), "n_dev_consistent": len(consistent)}
    best_test = 0
    best_name = None
    for n, p in models:
        s = score(p, test)
        if s > best_test:
            best_test, best_name = s, n
    out["best_test_acc"] = round(best_test / nt, 4)
    out["best_test_model"] = best_name
    out["best_consistent_test_acc"] = round(max([score(p, test) for _n, p in consistent] or [0]) / nt, 4)
    if consistent:
        sel_name, sel = consistent[0]
        out["selected_model"] = sel_name
        out["selected_solved"] = score(sel, test) == nt
        hs = [n for n, p in consistent if score(p, test) == nt]
        out["hindsight_solved"] = bool(hs)
        out["hindsight_model"] = hs[0] if hs else None
    else:
        out["selected_model"] = None
        out["selected_solved"] = False
        out["hindsight_solved"] = False
        out["hindsight_model"] = None
    out["solved"] = out["hindsight_solved"]
    return out


# ---------------------------------------------------------------- baselines
def b_constant(dev):
    c = modal([y for _x, y in dev])
    return [("const", lambda xs, c=c: c)]


def b_lookup(dev):
    tab = {}
    for x, y in dev:
        tab.setdefault(tuple(x), y)
    c = modal([y for _x, y in dev])
    return [("lookup", lambda xs, tab=tab, c=c: tab.get(tuple(xs), c))]


def _table(pairs):
    """key -> value table; None if conflicting."""
    tab = {}
    for k, v in pairs:
        if k in tab and tab[k] != v:
            return None
        tab[k] = v
    return tab


def _scalar_models(name, keyf, featf, dev, nfeat):
    """Models y = g(key) for Int outputs. keyf(xs) -> hashable key; featf(xs) -> tuple of numbers (affine)."""
    models = []
    ys = [y for _x, y in dev]
    if any(type(y) is not int for y in ys):
        return models
    feats = [featf(x) for x, _y in dev]
    if any(f is None or any(v is None for v in f) for f in feats):
        return models
    coef = solve_linear([(f + (1,), y) for f, y in zip(feats, ys)])
    if coef is not None:
        models.append(("%s:affine" % name, lambda xs, c=coef: affine_pred(c, (featf(xs) or (None,)) + (1,))))
    tab = _table([(keyf(x), y) for x, y in dev])
    if tab is not None:
        c = modal(ys)
        if coef is not None:
            models.append(("%s:table+affine" % name,
                           lambda xs, t=tab, cf=coef: t[keyf(xs)] if keyf(xs) in t
                           else affine_pred(cf, (featf(xs) or (None,)) + (1,))))
        models.append(("%s:table+const" % name, lambda xs, t=tab, c=c: t.get(keyf(xs), c)))
    return models


def _is_subseq(y, x):
    it = iter(x)
    return all(any(v == w for w in it) for v in y)


def _align_keep(x, y):
    """Greedy leftmost alignment of subsequence y in x -> keep flags."""
    flags, j = [], 0
    for v in x:
        if j < len(y) and v == y[j]:
            flags.append(True)
            j += 1
        else:
            flags.append(False)
    return flags if j == len(y) else None


KEEP_RULES = [("gt%d" % t, lambda v, t=t: v > t) for t in range(-20, 21)] + \
             [("lt%d" % t, lambda v, t=t: v < t) for t in range(-20, 21)] + \
             [("mod%d=%d" % (m, r), lambda v, m=m, r=r: v % m == r) for m in (2, 3, 4) for r in range(m)] + \
             [("mod%d!=%d" % (m, r), lambda v, m=m, r=r: v % m != r) for m in (2, 3, 4) for r in range(m)]


def _elementwise_models(name, ekey, efeat, dev, pad_first=False):
    """List outputs. Map-like: y_i = g(element context). Scan-like (len+1): y_0 constant then map-like."""
    models = []
    pairs, ok_len = [], True
    shift = None
    for x, y in dev:
        if type(y) is not list:
            return models
        if len(y) == len(x):
            s = 0
        elif len(y) == len(x) + 1:
            s = 1
        else:
            ok_len = False
            break
        if shift is None:
            shift = s
        elif shift != s:
            ok_len = False
            break
    if ok_len and shift is not None:
        y0 = modal([y[0] for _x, y in dev]) if shift else None
        if shift and any(y[0] != y0 for _x, y in dev):
            pass
        else:
            ctx = []
            for x, y in dev:
                for i in range(len(x)):
                    ctx.append((ekey(x, i), efeat(x, i), y[i + shift]))
            coef = solve_linear([(f + (1,), v) for _k, f, v in ctx])
            tab = _table([(k, v) for k, _f, v in ctx])
            cmod = modal([v for _k, _f, v in ctx]) if ctx else 0

            def mk(g):
                def pred(xs, g=g):
                    out = [g(xs, i) for i in range(len(xs))]
                    if any(v is None for v in out):
                        return None
                    return ([y0] if shift else []) + out
                return pred
            if coef is not None:
                models.append(("%s:elem_affine" % name, mk(lambda xs, i, c=coef: affine_pred(c, efeat(xs, i) + (1,)))))
            if tab is not None:
                if coef is not None:
                    models.append(("%s:elem_table+affine" % name,
                                   mk(lambda xs, i, t=tab, c=coef: t[ekey(xs, i)] if ekey(xs, i) in t
                                      else affine_pred(c, efeat(xs, i) + (1,)))))
                models.append(("%s:elem_table+const" % name,
                               mk(lambda xs, i, t=tab, c=cmod: t.get(ekey(xs, i), c))))
    # filter-like: every output is a subsequence of its input
    if all(type(y) is list and _is_subseq(y, x) for x, y in dev):
        kp = []
        for x, y in dev:
            fl = _align_keep(x, y)
            if fl is None:
                return models
            kp += [(ekey(x, i), f) for i, f in enumerate(fl)]
        tab = _table(kp)
        if tab is not None:
            for rn, rule in KEEP_RULES:
                if name == "reactive" and all(rule(k) == f for k, f in tab.items()):
                    models.append(("%s:keep_rule_%s" % (name, rn),
                                   lambda xs, r=rule: [v for v in xs if r(v)]))
            maj = sum(1 for f in tab.values() if f) * 2 >= len(tab)
            models.append(("%s:keep_table+maj" % name,
                           lambda xs, t=tab, m=maj: [v for i, v in enumerate(xs) if t.get(ekey(xs, i), m)]))
    return models


def b_reactive(dev):
    models = []
    for fn, f in FEATURES.items():
        models += _scalar_models("reactive_" + fn, lambda xs, f=f: f(xs), lambda xs, f=f: (f(xs),), dev, 1)
    models += _elementwise_models("reactive", lambda xs, i: xs[i], lambda xs, i: (xs[i],), dev)
    return models


def _h2(xs):
    if not xs:
        return None
    return (xs[-2] if len(xs) >= 2 else 0, xs[-1])


def b_history2(dev):
    models = _scalar_models("history2", _h2, _h2, dev, 2)
    models += _elementwise_models("history2", lambda xs, i: (xs[i - 1] if i else 0, xs[i]),
                                  lambda xs, i: (xs[i - 1] if i else 0, xs[i]), dev)
    return models


# ---------------------------------------------------------------- fixed-program library
LIB_SRC = [
    ("sum", "(sum xs)"), ("len", "(len xs)"), ("head", "(head xs)"), ("last", "(last xs)"),
    ("max", "(max xs)"), ("min", "(min xs)"),
    ("product", "(foldl (lam a (lam b (mul a b))) 1 xs)"),
    ("sum_sq", "(sum (map (lam x (mul x x)) xs))"),
    ("sum_abs", "(sum (map (lam x (gcd x 0)) xs))"),
    ("count_pos", "(len (filter (lam x (gt x 0)) xs))"),
    ("count_neg", "(len (filter (lam x (lt x 0)) xs))"),
    ("count_even", "(len (filter (lam x (eq (mod x 2) 0)) xs))"),
    ("count_zero", "(len (filter (lam x (eq x 0)) xs))"),
    ("sum_pos", "(sum (filter (lam x (gt x 0)) xs))"),
    ("sum_neg", "(sum (filter (lam x (lt x 0)) xs))"),
    ("sum_even", "(sum (filter (lam x (eq (mod x 2) 0)) xs))"),
    ("range", "(sub (max xs) (min xs))"),
    ("last_minus_head", "(sub (last xs) (head xs))"),
    ("alt_sum", "(foldl (lam a (lam b (sub b a))) 0 xs)"),
    ("mean_floor", "(div (sum xs) (len xs))"),
    ("sum_prefix_sums", "(sum (scanl (lam a (lam b (add a b))) 0 xs))"),
    ("max_abs", "(max (map (lam x (gcd x 0)) xs))"),
    ("gcd_all", "(foldl (lam a (lam b (gcd a b))) 0 xs)"),
    ("head_times_last", "(mul (head xs) (last xs))"),
    ("second", "(head (drop 1 xs))"),
    ("sum_parity", "(mod (sum xs) 2)"),
    ("max_prefix_sum", "(max (scanl (lam a (lam b (add a b))) 0 xs))"),
    ("min_prefix_sum", "(min (scanl (lam a (lam b (add a b))) 0 xs))"),
    ("id", "xs"), ("rev", "(rev xs)"), ("tail", "(drop 1 xs)"),
    ("init", "(take (sub (len xs) 1) xs)"),
    ("prefix_sums", "(scanl (lam a (lam b (add a b))) 0 xs)"),
    ("prefix_max", "(scanl (lam a (lam b (if (gt a b) a b))) (head xs) xs)"),
    ("prefix_min", "(scanl (lam a (lam b (if (lt a b) a b))) (head xs) xs)"),
    ("prefix_prod", "(scanl (lam a (lam b (mul a b))) 1 xs)"),
    ("map_abs", "(map (lam x (gcd x 0)) xs)"), ("map_sq", "(map (lam x (mul x x)) xs)"),
    ("map_sign", "(map (lam x (if (gt x 0) 1 (if (lt x 0) -1 0))) xs)"),
    ("map_mod2", "(map (lam x (mod x 2)) xs)"), ("map_mod3", "(map (lam x (mod x 3)) xs)"),
    ("filter_pos", "(filter (lam x (gt x 0)) xs)"), ("filter_neg", "(filter (lam x (lt x 0)) xs)"),
    ("filter_nonneg", "(filter (lam x (not (lt x 0))) xs)"),
    ("filter_even", "(filter (lam x (eq (mod x 2) 0)) xs)"),
    ("filter_odd", "(filter (lam x (eq (mod x 2) 1)) xs)"),
    ("filter_nonzero", "(filter (lam x (not (eq x 0))) xs)"),
    ("diffs", "(zipw (lam a (lam b (sub b a))) xs (drop 1 xs))"),
    ("pair_sums", "(zipw (lam a (lam b (add a b))) xs (drop 1 xs))"),
    ("pair_max", "(zipw (lam a (lam b (if (gt a b) a b))) xs (drop 1 xs))"),
]
LIB = [(n, A.parse(s)) for n, s in LIB_SRC]
LIB_PY = [("sorted", lambda xs: sorted(xs)), ("sorted_desc", lambda xs: sorted(xs, reverse=True)),
          ("dedupe", lambda xs: list(dict.fromkeys(xs))), ("count_distinct", lambda xs: len(set(xs)))]


def _lib_fn(t):
    def f(xs):
        v = A.run(t, xs)
        return None if v == A.FAIL else v
    return f


def b_library(dev):
    models = []
    progs = [(n, _lib_fn(t)) for n, t in LIB] + LIB_PY
    raw = [("lib:" + n, f) for n, f in progs]
    models += raw
    ys = [y for _x, y in dev]
    for n, f in progs:
        outs = [f(x) for x, _y in dev]
        if any(o is None for o in outs):
            continue
        if all(type(y) is int for y in ys) and all(type(o) is int for o in outs):
            coef = solve_linear([((o, 1), y) for o, y in zip(outs, ys)])
            if coef is not None:
                models.append(("lib:%s:affine" % n,
                               lambda xs, f=f, c=coef: (lambda o: None if type(o) is not int
                                                        else affine_pred(c, (o, 1)))(f(xs))))
        elif all(type(y) is list for y in ys) and all(type(o) is list and len(o) == len(y)
                                                      for o, y in zip(outs, ys)):
            rows = [((a, 1), b) for o, y in zip(outs, ys) for a, b in zip(o, y)]
            coef = solve_linear(rows)
            if coef is not None:
                def pred(xs, f=f, c=coef):
                    o = f(xs)
                    if type(o) is not list:
                        return None
                    r = [affine_pred(c, (a, 1)) for a in o]
                    return None if any(v is None for v in r) else r
                models.append(("lib:%s:elem_affine" % n, pred))
    return models


LADDER = [("constant", b_constant), ("lookup", b_lookup), ("reactive", b_reactive), ("history2", b_history2),
          ("library", b_library)]


def run_closed_form(dev, test, tribunal=None) -> Dict[str, dict]:
    res = {}
    for name, b in LADDER:
        models = b(dev)
        res[name] = verdict(models, dev, test) if models else {
            "n_models": 0, "n_dev_consistent": 0, "solved": False, "selected_solved": False,
            "hindsight_solved": False, "best_test_acc": 0.0, "best_consistent_test_acc": 0.0,
            "selected_model": None, "hindsight_model": None}
    return res


def run_small_search(grammar: tenum.Grammar, out_type, dev, test, budget, tribunal=None):
    T = "I" if out_type == "I" else ("L" if out_type == "L" else "B")
    r = tenum.search(grammar, T, dev, budget)
    out = {"budget": budget, "charge": r["charge"], "size_reached": r["size_reached"],
           "complete_size": r["complete_size"], "found": A.show(r["found"]) if r["found"] else None}
    if r["found"] is not None:
        prog = r["found"]
        ok = sum(1 for xs, y in test if A.run(prog, xs) == y)
        out["test_acc"] = round(ok / len(test), 4)
        out["solved"] = ok == len(test)
        out["found_esize"] = A.esize(prog)
        if tribunal:
            out["tribunal_agree"] = round(sum(1 for xs, y in tribunal if A.run(prog, xs) == y) / len(tribunal), 4)
    else:
        out["solved"] = False
        out["test_acc"] = 0.0
    return out
