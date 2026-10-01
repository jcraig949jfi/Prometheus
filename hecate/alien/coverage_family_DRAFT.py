"""DRAFT (design P) -- coverage-controlled alien family: induction vs coverage.

NOT FROZEN. No subject runs. Pure stdlib; imports nothing from the frozen pilot
(hecate/alien/{systems,generate,dataset,...}) and reads no pilot data.
Design: roles/Hecate/harvest_w2/DESIGN_P_coverage_controlled_family.md

System: ring of SITES=6 sites, values in Z_7, x_i' = T[x_i][x_{i+1 mod 6}] with
ONE shared 7x7 table T (49 entries). Each component has exactly one witness key
(x_i, x_{i+1}), and an observed transition reveals the VALUE of every key it
consults, so "covered" == "revealed" (fixes INV_E caveat 2).

A PAIR shares architecture, revealed key set R (|R| = m exactly), observed
source states and eval states:
  LAW   T = hidden compact law outside the textbook library (2R / 3R ridge sums)
        or, for the positive-control stratum, a library law (LIB_*)
  ARB   R-values = shuffle of LAW's R-values, U-values = shuffle of LAW's
        U-values, accepted only if default-agreement counts on U match LAW
        exactly and no library/generating class fits ARB's R-values
  SHADOW (scoring-only) LAW on R, ARB on U: the LAW run rescored; must be chance

    python -m hecate.alien.coverage_family_DRAFT          # self-test
"""

from __future__ import annotations

import itertools
import random
import sys
from fractions import Fraction
from math import comb

K = 7
SITES = 6
NKEYS = K * K
N_OBS = 40            # observed single-step transitions per member
MIN_SEEN = 2          # every revealed key appears at >= 2 observed sites
N_EVAL = 200          # held-out eval states per pair
MIN_EVAL_OCC = 5      # every unseen key occurs >= 5 times in the eval set
COVER_LEVELS = (25, 37)   # m: 25/49 = 0.510, 37/49 = 0.755
DIRS = [(0, 1)] + [(1, b) for b in range(K)]   # 8 projective directions of Z_7^2
AXES = frozenset([(1, 0), (0, 1)])
MAX_TRIES = 400


def kidx(a, b):
    return a * K + b


def step(T, s):
    return tuple(T[kidx(s[i], s[(i + 1) % SITES])] for i in range(SITES))


def keys_of(s):
    return [kidx(s[i], s[(i + 1) % SITES]) for i in range(SITES)]


# ---------------------------------------------------------------- lin. alg. mod 7

def fit_linear(feat, obs, targets):
    """Fit T(a,b) = feat(a,b) . x (mod 7) exactly on obs {key: val}.
    Returns None if inconsistent, else {u: prediction} for every u in targets
    that the fit DETERMINES (feat(u) in the row space of the observed rows)."""
    rows = [feat(k // K, k % K) + [v] for k, v in obs.items()]
    d = len(rows[0]) - 1
    piv, r = [], 0
    for c in range(d):
        pr = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if pr is None:
            continue
        rows[r], rows[pr] = rows[pr], rows[r]
        inv = pow(rows[r][c], -1, K)
        rows[r] = [(v * inv) % K for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                f = rows[i][c]
                rows[i] = [(x - f * y) % K for x, y in zip(rows[i], rows[r])]
        piv.append(c)
        r += 1
    if any(row[-1] for row in rows[r:]):
        return None
    x = [0] * d
    for i, c in enumerate(piv):
        x[c] = rows[i][-1]
    out = {}
    for u in targets:
        v = feat(u // K, u % K)
        w = v[:]
        for i, c in enumerate(piv):
            if w[c]:
                f = w[c]
                w = [(p - f * q) % K for p, q in zip(w, rows[i][:d])]
        if not any(w):
            out[u] = sum(p * q for p, q in zip(v, x)) % K
    return out


def onehot(i, n=K):
    v = [0] * n
    v[i] = 1
    return v


def ridge_feat(dirs):
    return lambda a, b: sum((onehot((al * a + be * b) % K) for al, be in dirs), [])


def mono_feat(deg):
    mons = [(i, j) for i in range(deg + 1) for j in range(deg + 1 - i)]
    return lambda a, b: [pow(a, i, K) * pow(b, j, K) % K for i, j in mons]


_PAIRS = [(a, b) for a in range(K) for b in range(a, K)]          # 28 unordered
_OFF = [(a, b) for a in range(K) for b in range(a + 1, K)]        # 21


def _sym(a, b):
    return onehot(_PAIRS.index((min(a, b), max(a, b))), len(_PAIRS))


def _antisym(a, b):
    v = [0] * len(_OFF)
    if a != b:
        v[_OFF.index((min(a, b), max(a, b)))] = 1 if a < b else K - 1
    return v


NAMED_OPS = {"max": max, "min": min, "absdiff": lambda a, b: abs(a - b),
             "fmean": lambda a, b: (a + b) // 2, "pow": lambda a, b: pow(a, b, K),
             "lt": lambda a, b: int(a < b)}

# Library of TEXTBOOK compact law classes, simplest first (declared, finite).
LIBRARY = ([("const", lambda a, b: [1]), ("affine", mono_feat(1)),
            ("poly2", mono_feat(2)), ("poly3", mono_feat(3))]
           + [("op:" + n, (lambda f: lambda a, b: [1, f(a, b) % K])(f))
              for n, f in NAMED_OPS.items()]
           + [("ridge%s" % (d,), ridge_feat([d])) for d in DIRS]
           + [("sep", ridge_feat([(1, 0), (0, 1)])), ("antisym", _antisym),
              ("sym", _sym)])


def latin_fit(obs, targets):
    """Latin-square completion by elimination (row/column permutations)."""
    cell = {k: {v} for k, v in obs.items()}
    for k in range(NKEYS):
        cell.setdefault(k, set(range(K)))
    lines = [[kidx(a, b) for b in range(K)] for a in range(K)] + \
            [[kidx(a, b) for a in range(K)] for b in range(K)]
    changed = True
    while changed:
        changed = False
        for ln in lines:
            fixed = [next(iter(cell[k])) for k in ln if len(cell[k]) == 1]
            if len(fixed) != len(set(fixed)):
                return None
            for k in ln:
                if len(cell[k]) > 1 and cell[k] & set(fixed):
                    cell[k] -= set(fixed)
                    changed = True
                if not cell[k]:
                    return None
            for v in range(K):
                where = [k for k in ln if v in cell[k]]
                if not where:
                    return None
                if len(where) == 1 and len(cell[where[0]]) > 1:
                    cell[where[0]] = {v}
                    changed = True
    return {u: next(iter(cell[u])) for u in targets if len(cell[u]) == 1}


def lawfit(obs, targets, extra=()):
    """Law-fitting baseline: first (simplest) consistent class that determines u
    predicts u; unpredicted u -> None. extra = additional (name, feat) classes."""
    pred, used = {}, {}
    for name, feat in list(LIBRARY) + list(extra):
        got = fit_linear(feat, obs, [u for u in targets if u not in pred])
        if got:
            pred.update(got)
            used.update({u: name for u in got})
    got = latin_fit(obs, [u for u in targets if u not in pred])
    if got:
        pred.update(got)
        used.update({u: "latin" for u in got})
    return pred, used


def class_combos(cls):
    n = {"2R": 2, "3R": 3, "2R_ALL": 2}[cls]
    return [c for c in itertools.combinations(DIRS, n)
            if cls == "2R_ALL" or not (n == 2 and set(c) == AXES)]


def class_fit(obs, targets, cls):
    """Generating-class oracle: union over all direction combos of the class.
    u is determined iff EVERY consistent combo determines it with one value."""
    fits = [fit_linear(ridge_feat(c), obs, targets) for c in class_combos(cls)]
    fits = [f for f in fits if f is not None]
    if not fits:
        return {}
    out = {}
    for u in targets:
        vals = {f.get(u) for f in fits}
        if len(vals) == 1 and None not in vals:
            out[u] = vals.pop()
    return out


# ---------------------------------------------------------------- generators

def draw_law(rng, cls):
    def nonconst():
        while True:
            f = [rng.randrange(K) for _ in range(K)]
            if len(set(f)) > 1:
                return f
    if cls in ("2R", "3R", "2R_AXES", "1R_DEGEN"):
        n = 3 if cls == "3R" else 2
        if cls == "2R_AXES":                       # = sep: MUST be rejected
            dirs = [(1, 0), (0, 1)]
        else:
            while True:
                dirs = rng.sample(DIRS, n)
                if not (n == 2 and set(dirs) == AXES):
                    break
        fs = [nonconst() for _ in dirs]
        if cls == "1R_DEGEN":                      # 2nd ridge constant: MUST be rejected
            fs[1] = [rng.randrange(K)] * K
        T = [sum(f[(al * a + be * b) % K] for f, (al, be) in zip(fs, dirs)) % K
             for a in range(K) for b in range(K)]
        return T, {"dirs": dirs, "f": fs}
    if cls == "LIB_affine":
        al, be, g = rng.randrange(1, K), rng.randrange(1, K), rng.randrange(K)
        return [(al * a + be * b + g) % K for a in range(K) for b in range(K)], {"abg": (al, be, g)}
    if cls == "LIB_poly2":
        while True:
            c = [rng.randrange(K) for _ in range(6)]
            if any(c[i] for i in (2, 4, 5)):       # a^2, ab, b^2 terms (mono order)
                break
        f = mono_feat(2)
        return [sum(p * q for p, q in zip(f(a, b), c)) % K for a in range(K) for b in range(K)], {"c": c}
    if cls == "LIB_op":
        n = rng.choice(sorted(NAMED_OPS))
        u, v = rng.randrange(1, K), rng.randrange(K)
        return [(u * NAMED_OPS[n](a, b) + v) % K for a in range(K) for b in range(K)], {"op": n, "uv": (u, v)}
    raise ValueError(cls)


def draw_sources(rng, R):
    """N_OBS distinct closed 6-walks in the digraph R; every R key seen >= MIN_SEEN times."""
    Rs = set(R)
    succ = {a: [b for b in range(K) if kidx(a, b) in Rs] for a in range(K)}

    def complete(x0, x1):
        def dfs(path):
            if len(path) == SITES:
                return path if kidx(path[-1], path[0]) in Rs else None
            nxt = succ[path[-1]][:]
            rng.shuffle(nxt)
            for y in nxt:
                got = dfs(path + [y])
                if got:
                    return got
            return None
        return dfs([x0, x1])

    seen = {k: 0 for k in R}
    srcs = []
    for _ in range(4 * N_OBS):
        need = [k for k in R if seen[k] < MIN_SEEN]
        if not need and len(srcs) >= N_OBS:
            break
        if len(srcs) >= N_OBS:
            return None
        k = rng.choice(need) if need else rng.choice(R)
        w = complete(k // K, k % K)
        if w is None:
            return None                               # arc on no closed 6-walk
        r = rng.randrange(SITES)
        s = tuple(w[r:] + w[:r])
        if s in srcs:
            continue
        srcs.append(s)
        for kk in keys_of(s):
            seen[kk] += 1
    if len(srcs) != N_OBS or min(seen.values()) < MIN_SEEN:
        return None
    return srcs


def default_counts(T, U):
    return (sum(T[u] == u // K for u in U), sum(T[u] == u % K for u in U),
            sum(T[u] == 0 for u in U))


def make_pair(seed, m, cls):
    rng = random.Random(seed)
    rej = {}

    def no(why):
        rej[why] = rej.get(why, 0) + 1

    alien = cls in ("2R", "3R", "2R_AXES", "1R_DEGEN")
    gen_cls = {"3R": "3R", "2R": "2R"}.get(cls, "2R_ALL")   # test classes: incl. axes
    for _ in range(MAX_TRIES):
        T, law = draw_law(rng, cls)
        R = sorted(rng.sample(range(NKEYS), m))
        U = [u for u in range(NKEYS) if u not in set(R)]
        obsR = {k: T[k] for k in R}
        srcs = draw_sources(rng, R)
        if srcs is None:
            no("R_not_walk_realizable")
            continue
        # identifiability certificate under the generating class
        cert = class_fit(obsR, U, gen_cls) if alien else lawfit(obsR, U)[0]
        if len(cert) != len(U) or any(cert[u] != T[u] for u in U):
            no("U_not_determined_by_class")
            continue
        lf, used = lawfit(obsR, U)
        lib_right = sum(lf.get(u) == T[u] for u in U)
        ocd_right = sum(T[u] == u // K for u in U)
        if alien and lib_right > ocd_right:
            no("NOT_ALIEN_library_solves:" + ",".join(sorted(set(used.values()))))
            continue
        # ARB: histogram-preserving shuffles, default-count matched, lawless on R
        dc = default_counts(T, U)
        A = None
        for _ in range(3000):
            rv = [T[k] for k in R]
            uv = [T[u] for u in U]
            rng.shuffle(rv)
            rng.shuffle(uv)
            cand = [0] * NKEYS
            for k, v in zip(R, rv):
                cand[k] = v
            for u, v in zip(U, uv):
                cand[u] = v
            if default_counts(cand, U) != dc:
                continue
            oA = {k: cand[k] for k in R}
            if lawfit(oA, U)[0] or class_fit(oA, U, "2R") or class_fit(oA, U, "3R"):
                continue
            A = cand
            break
        if A is None:
            no("ARB_unmatchable")
            continue
        shadow = [T[k] if k in obsR else A[k] for k in range(NKEYS)]
        ev, pool = [], set(srcs)
        while len(ev) < N_EVAL:
            s = tuple(rng.randrange(K) for _ in range(SITES))
            if s not in pool:
                pool.add(s)
                ev.append(s)
        occ = {u: 0 for u in U}
        for s in ev:
            for k in keys_of(s):
                if k in occ:
                    occ[k] += 1
        if min(occ.values()) < MIN_EVAL_OCC:
            no("eval_occurrence")
            continue
        return {"seed": seed, "m": m, "cls": cls, "law": law, "R": R, "U": U,
                "srcs": srcs, "eval": ev, "LAW": T, "ARB": A, "SHADOW": shadow,
                "rejections": rej}
    return {"seed": seed, "m": m, "cls": cls, "FAILED": True, "rejections": rej}


def verify_pair(P):
    """Fail-closed invariants; returns list of violated checks (empty = PASS)."""
    bad = []
    Rs, Us = set(P["R"]), set(P["U"])
    seen = {k for s in P["srcs"] for k in keys_of(s)}
    if seen != Rs:
        bad.append("coverage: seen keys != R")
    if len(Rs) != P["m"] or Rs & Us or len(Rs | Us) != NKEYS:
        bad.append("coverage: |R| != m or R,U not a partition")
    if len(set(P["srcs"])) != N_OBS or set(P["srcs"]) & set(P["eval"]):
        bad.append("sources not distinct / overlap eval")
    for name in ("LAW", "ARB"):
        if sorted(P[name][k] for k in P["R"]) != sorted(P["LAW"][k] for k in P["R"]):
            bad.append(name + ": R histogram differs")
        if sorted(P[name][u] for u in P["U"]) != sorted(P["LAW"][u] for u in P["U"]):
            bad.append(name + ": U histogram differs")
    if default_counts(P["LAW"], P["U"]) != default_counts(P["ARB"], P["U"]):
        bad.append("default-agreement counts differ")
    return bad


# ---------------------------------------------------------------- learners & scoring

def table_learner(fill):
    """fill(obs, U, pair) -> {u: value}; observed keys use observed values;
    anything unfilled -> own value (OCD 'nothing happens' default)."""
    def make(P, obs):
        got = fill(obs, P["U"], P)
        T = [obs.get(k, got.get(k, k // K)) for k in range(NKEYS)]
        return lambda s: step(T, s)
    return make


def _local(obs, U, P):
    out = {}
    for u in U:
        a, b = divmod(u, K)
        near = sorted((min((b - bb) % K, (bb - b) % K), bb) for bb in range(K) if kidx(a, bb) in obs)
        if near:
            out[u] = obs[kidx(a, near[0][1])]
    return out


def _mode(obs, U, P):
    vals = sorted(obs.values())
    md = max(range(K), key=lambda v: (vals.count(v), -v))
    return {u: md for u in U}


LEARNERS = {
    "ORACLE": None,                                          # truth (set per member)
    "OCD_a": table_learner(lambda o, U, P: {}),
    "OCD_b": table_learner(lambda o, U, P: {u: u % K for u in U}),
    "OCD_0": table_learner(lambda o, U, P: {u: 0 for u in U}),
    "MODE": table_learner(_mode),
    "LOCAL": table_learner(_local),
    "LAWFIT": table_learner(lambda o, U, P: lawfit(o, U)[0]),
    "INDUCER": table_learner(lambda o, U, P: {**lawfit(o, U)[0], **class_fit(o, U, "3R"),
                                              **class_fit(o, U, "2R")}),
}


def score(predict, truth, P):
    """Key-level (decision) + component-level (INV_E) uncovered accuracy.
    pred_key[u] = the subject's value for unseen key u if it is the same at every
    eval occurrence, else None (an inconsistent key never counts as right)."""
    Us = set(P["U"])
    key_ok = {u: True for u in P["U"]}
    pk = {}
    cu = cn = vu = vn = 0
    for s in P["eval"]:
        pr = predict(s)
        for i, k in enumerate(keys_of(s)):
            ok = pr[i] == truth[k]
            if k in Us:
                cn += 1
                cu += ok
                key_ok[k] = key_ok[k] and ok
                pk[k] = pr[i] if pk.get(k, pr[i]) == pr[i] else None
            else:
                vn += 1
                vu += ok
    return {"key_unc": sum(key_ok.values()), "U": len(Us), "comp_unc": (cu, cn),
            "comp_cov": (vu, vn), "pred_key": pk}


def leak_flag(pred_key, truth, U, seed, n_perm=2000, max_hits=2):
    """Permutation leak test: the ARB/SHADOW U-values are an exchangeable shuffle,
    so under no-leak the subject's matches are distributed as matches against
    random re-shuffles of the same U-values. Flag if <= max_hits of n_perm
    shuffles reach the observed match count (exact integers, p <= 3/2001)."""
    vals = [truth[u] for u in U]
    obs = sum(pred_key.get(u) == truth[u] for u in U)
    rng = random.Random(seed)
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(vals)
        hits += sum(pred_key.get(u) == v for u, v in zip(U, vals)) >= obs
    return hits <= max_hits


def run_member(P, learner, member):
    truth = P[member]
    obs = {k: truth[k] for k in P["R"]}
    if learner == "ORACLE":
        pred = lambda s: step(truth, s)
    else:
        pred = LEARNERS[learner](P, obs)
    out = score(pred, truth, P)
    if member == "LAW":                       # same run rescored against SHADOW truth
        out["shadow_key_unc"] = score(pred, P["SHADOW"], P)["key_unc"]
        out["leak"] = leak_flag(out["pred_key"], P["SHADOW"], P["U"], P["seed"])
    else:
        out["leak"] = leak_flag(out["pred_key"], truth, P["U"], P["seed"] + 1)
    return out


# ---------------------------------------------------------------- decision rules (exact)

def binom_tail_ge(n, k, num=1, den=2):
    """P(Bin(n, num/den) >= k) as a Fraction."""
    p = Fraction(num, den)
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def sign_crit(n, alpha=Fraction(1, 100)):
    """Least k with P(Bin(n,1/2) >= k) <= alpha (integer test: 100*sum C <= 2^n)."""
    for k in range(n + 1):
        if 100 * sum(comb(n, i) for i in range(k, n + 1)) <= 2 ** n:
            return k
    return n + 1


def decide(rows):
    """rows: per pair dicts with sL, sA, oL, oA (key counts), U, covL=(right,n), leakA/leakS,
    shadow, cls. Returns verdict label + the integers it used."""
    if any(r["oL"] != r["oA"] for r in rows):
        return "INVALID(ocd_unmatched)", {}
    leaks = sum(r["leakA"] or r["leakS"] for r in rows)
    if leaks >= 2:
        return "INVALID(leak_alarm=%d)" % leaks, {}
    cr = sum(r["covL"][0] for r in rows)
    cn = sum(r["covL"][1] for r in rows)
    if 20 * cr < 19 * cn:
        return "INDETERMINATE(no_engagement)", {"cov": (cr, cn)}
    d = [r["sL"] - r["sA"] for r in rows]
    npos, nneg = sum(x > 0 for x in d), sum(x < 0 for x in d)
    crit = sign_crit(npos + nneg)
    sd, su = sum(d), sum(r["U"] for r in rows)
    info = {"n": len(rows), "pos": npos, "neg": nneg, "crit": crit, "sum_d": sd, "sum_U": su}
    if npos >= crit and 4 * sd >= su:
        return "INDUCTION", info
    if npos < crit and 20 * sd <= su:
        return "NO_INDUCTION", info
    return "INDETERMINATE", info


# ---------------------------------------------------------------- self-test

def _selftest(n_alien=6):
    print("DRAFT coverage-controlled family self-test (K=7, 6-site ring, 49 keys)")
    pairs, fails = [], 0
    plan = []
    for m in COVER_LEVELS:
        plan += [(m, "2R")] * n_alien + [(m, "3R")] * (n_alien // 2)
        plan += [(m, "LIB_affine"), (m, "LIB_poly2"), (m, "LIB_op")] * 2
    rejtot = {}
    for i, (m, cls) in enumerate(plan):
        P = make_pair(20261001 * 100 + i, m, cls)
        for k, v in P["rejections"].items():
            rejtot[(m, cls, k)] = rejtot.get((m, cls, k), 0) + v
        if P.get("FAILED"):
            fails += 1
            print("  FAILED", m, cls, P["rejections"])
            continue
        bad = verify_pair(P)
        cov = Fraction(len({k for s in P["srcs"] for k in keys_of(s)}), NKEYS)
        print("  pair %2d m=%d %-10s coverage=%s (=%.3f) |U|=%d verify=%s dirs/law=%s"
              % (i, m, cls, cov, float(cov), len(P["U"]), "PASS" if not bad else bad,
                 P["law"].get("dirs", P["law"].get("op", P["law"].get("abg", "poly2")))))
        pairs.append(P)
    print("  generator failures:", fails)
    print("  rejection reasons (m, class, reason): count")
    for k in sorted(rejtot):
        print("    %s: %d" % (k, rejtot[k]))

    print("NOT-ALIEN detector (deliberately library-solvable 'aliens' must be rejected):")
    for cls in ("2R_AXES", "1R_DEGEN"):
        for m in COVER_LEVELS:
            P = make_pair(777 + m, m, cls)
            nrej = sum(v for k, v in P["rejections"].items() if k.startswith("NOT_ALIEN"))
            print("  %-8s m=%d accepted=%s NOT_ALIEN rejections=%d reasons=%s"
                  % (cls, m, not P.get("FAILED"), nrej, sorted(P["rejections"])))

    print("Learner scores (key-level uncovered correct, summed over pairs: LAW / ARB / SHADOW):")
    table = {}
    for name in ["ORACLE"] + [n for n in LEARNERS if n != "ORACLE"]:
        for strat in ("ALIEN", "LIB"):
            rows = []
            for P in pairs:
                if (strat == "LIB") != P["cls"].startswith("LIB"):
                    continue
                L, A = run_member(P, name, "LAW"), run_member(P, name, "ARB")
                oL, oA = run_member(P, "OCD_a", "LAW"), run_member(P, "OCD_a", "ARB")
                rows.append({"sL": L["key_unc"], "sA": A["key_unc"], "oL": oL["key_unc"],
                             "oA": oA["key_unc"], "U": L["U"], "covL": L["comp_cov"],
                             "shadow": L["shadow_key_unc"], "cls": P["cls"],
                             "leakA": A["leak"], "leakS": L["leak"],
                             "cuL": L["comp_unc"], "cuA": A["comp_unc"]})
            table[(name, strat)] = rows
            sL = sum(r["sL"] for r in rows)
            sA = sum(r["sA"] for r in rows)
            su = sum(r["U"] for r in rows)
            cuL = Fraction(sum(r["cuL"][0] for r in rows), sum(r["cuL"][1] for r in rows))
            cuA = Fraction(sum(r["cuA"][0] for r in rows), sum(r["cuA"][1] for r in rows))
            eq = all(r["sL"] == r["sA"] for r in rows)
            verdict, info = decide(rows)
            print("  %-8s %-5s LAW %3d/%3d ARB %3d SHADOW %3d | comp-unc LAW %.3f ARB %.3f"
                  " | L==A every pair: %-5s | %s %s"
                  % (name, strat, sL, su, sA, sum(r["shadow"] for r in rows), float(cuL),
                     float(cuA), eq, verdict, info))
    print("Construction checks:")
    for name in ("OCD_a", "OCD_b", "OCD_0", "MODE"):
        ok = all(r["sL"] == r["sA"] for s in ("ALIEN", "LIB") for r in table[(name, s)])
        print("  %-6s scores identical on LAW and ARB in every pair: %s" % (name, ok))
    ok = all(r["sL"] == r["oL"] for r in table[("LAWFIT", "ALIEN")])
    print("  LAWFIT == OCD_a on every accepted ALIEN LAW member (not-alien filter): %s" % ok)
    ok = all(r["sL"] == r["U"] for r in table[("LAWFIT", "LIB")])
    print("  LAWFIT solves every LIB LAW member: %s" % ok)
    ok = all(r["sL"] == r["U"] for r in table[("INDUCER", "ALIEN")])
    print("  INDUCER (class oracle) solves every ALIEN LAW member: %s" % ok)

    print("Leak control: a learner that reads the TRUE table of the member it is run on:")
    rows = []
    for P in pairs:
        if P["cls"].startswith("LIB"):
            continue
        L, A = run_member(P, "ORACLE", "LAW"), run_member(P, "ORACLE", "ARB")
        o = run_member(P, "OCD_a", "LAW")["key_unc"]
        rows.append({"sL": L["key_unc"], "sA": A["key_unc"], "oL": o, "oA": o, "U": L["U"],
                     "covL": L["comp_cov"], "shadow": L["shadow_key_unc"],
                     "leakA": A["leak"], "leakS": L["leak"]})
    print("  ", decide(rows))

    print("Power (exact; one-sided sign test alpha=0.01; p = P(d>0 | d!=0)):")
    for n in (12, 16, 24, 32, 48):
        c = sign_crit(n)
        pw = "  ".join("p=%.2f:%.3f" % (p, float(binom_tail_ge(n, c, int(p * 100), 100)))
                       for p in (0.70, 0.80, 0.90))
        print("  n_untied=%2d crit=%2d size=%.4f  %s" % (n, c, float(binom_tail_ge(n, c)), pw))


if __name__ == "__main__":
    _selftest(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
