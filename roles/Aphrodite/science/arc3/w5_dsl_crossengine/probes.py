"""ARC3 / W5 bounded probes of candidate DSL extensions (forensic, not a disposition).

  P1 grammar/search-space sizes per variant (and the PRISTINE-vs-escrow check).
  P2 degeneracy census: 600 NEW bodies per variant (mention acc and v; init H1; a G4
     final mentioning acc), each profiled with T4's family_profile logic (xdsl copy,
     equal to T4 on G4 witnesses), plus permutation invariance, extensional novelty
     against G4 (same init, final = acc), and for CONST the share that is an affine
     re-scaling/length-offset of a G4 family.
  P3 EC polynomial ladder expressibility, SYMBOLIC (exact for the {+,-,*,pow-by-constant}
     fragment; a lower bound otherwise), for the SUM (sum f(v)) and ORBIT
     (x' = f(x) + v) mappings, under left-atom depth 2/3 (G4/G5) and symmetric depth
     2/3 templates, with and without integer literals 2..9.
  P4 OEIS LINREC stratum (rb5 cache, 150 sequences, order <= 3): canonical witness
     under LAG registers + literals ("acc = v", final = recurrence over v, p, q...),
     verified on the listed terms, then profiled with T4 logic.
  P5 G1 = (acc + {H}) coverage inflation under each variant.
Single process, 1 core. Seeds: APHRODITE/ARC3/W5/v1/*.
"""
import itertools
import json
import random
import re
import sys
import time
from collections import Counter, defaultdict
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import xdsl as X            # noqa: E402
import basis_v4 as G        # noqa: E402

OUT = {}
T0 = time.time()


def log(m):
    print("[w5 %6.1fs] %s" % (time.time() - T0, m), flush=True)


def mentions(s, n):
    return re.search(r"\b%s\b" % n, s) is not None


# ---------------------------------------------------------------- P1
def p1():
    ESC = 250_000
    rows = {}
    for n in X.VARIANTS:
        g = X.grammar(n)
        prist = 2 * len(g["h2"]) * len(g["final"])
        rows[n] = {"bodies": len(g["body"]), "inits": len(g["init"]), "finals": len(g["final"]),
                   "level1": len(g["level1"]), "h2": len(g["h2"]),
                   "fallback_programs": len(g["init"]) * len(g["body"]) * len(g["final"]),
                   "pristine_entry": prist, "pristine_fits_escrow": prist <= ESC,
                   "g1_instances_in_space": None}
        # G1 coverage: (acc + {H}) with {H} in the variant's LEVEL1, body in the space
        bs = set(g["body"])
        rows[n]["g1_instances_in_space"] = sum(1 for f in g["level1"] if "(acc + %s)" % f in bs)
    # analytic: W5 (left-atom depth 3) and its mirror (symmetric depth-3 = both sides)
    b4 = 10842
    rows["W5_left_depth3"] = {"bodies": 465954, "note": "G4 + prim(atom, depth2) (a17.g5_bodies)"}
    rows["W5_plus_mirror"] = {"bodies": 465954 + 444528,
                              "note": "W5 + prim(depth2, atom); compound-compound pairs not counted"}
    OUT["P1_sizes"] = rows
    log("P1 done")


# ---------------------------------------------------------------- P2
def probe_set():
    rng = random.Random(X.LABEL + "/P2/probes")
    pr = []
    for L in range(2, 42, 2):                       # 20 lengths, a PAIR per length
        m = rng.randint(1, 97)
        a = [rng.randint(2, 30) for _ in range(L)]
        b = [a[0]] + [rng.randint(2, 30) for _ in range(L - 1)]   # same first, same m
        pr += [(a, m), (b, m)]
    return pr


def key_of(prog, P):
    return tuple(X.run(prog, xs, m)[0] for xs, m in P)


def pairdiff_norm(k):
    """Differences within same-length pairs, normalised by gcd and sign. Equal for
    two families that differ by c*F + g(length, first, m)."""
    if None in k:
        return None
    d = [k[2 * j] - k[2 * j + 1] for j in range(len(k) // 2)]
    g = 0
    for x in d:
        g = gcd(g, abs(x))
    if g == 0:
        return ("ZERO",)
    d = [x // g for x in d]
    s = next((1 if x > 0 else -1) for x in d if x != 0)
    return tuple(s * x for x in d)


def p2(n_sample=600):
    P = probe_set()
    g4 = X.grammar("G4")
    log("P2: indexing G4 (init H1 x 10,842 bodies, final acc)")
    g4keys, g4pd = set(), set()
    for init in G.H1_SPACE:
        for b in g4["body"]:
            k = key_of(("fold", init, b, "acc"), P)
            g4keys.add((init, k))
            pd = pairdiff_norm(k)
            if pd is not None:
                g4pd.add(pd)
    log("P2: G4 index %d keys, %d pair-diff classes" % (len(g4keys), len(g4pd)))
    g4set = set(g4["body"])
    finals = [f for f in G.FINAL_SPACE if mentions(f, "acc")]
    res = {}
    for n in X.VARIANTS:
        g = X.grammar(n)
        pool = [b for b in g["body"] if (n == "G4" or b not in g4set)
                and mentions(b, "acc") and mentions(b, "v")]
        rng = random.Random(X.LABEL + "/P2/" + n)
        samp = rng.sample(pool, min(n_sample, len(pool)))
        reasons, adm, adm_perm, adm_new, adm_aff, adm_g1form = Counter(), 0, 0, 0, 0, 0
        perm_all, new_all = 0, 0
        for b in samp:
            init = rng.choice(G.H1_SPACE)
            fin = rng.choice(finals)
            w = ("fold", init, b, fin)
            prof = X.family_profile(w)
            k = key_of(("fold", init, b, "acc"), P)
            is_new = (init, k) not in g4keys
            pi = X.perm_invariant(w)
            perm_all += pi
            new_all += is_new
            for r in prof["reasons"]:
                reasons[r] += 1
            if prof["admissible"]:
                adm += 1
                adm_perm += pi
                adm_new += is_new
                pd = pairdiff_norm(k)
                if is_new and pd is not None and pd in g4pd:
                    adm_aff += 1
                if re.fullmatch(r"\(acc [+] .*\)|\(.* [+] acc\)", b) and b.count("acc") == 1:
                    adm_g1form += 1
        N = len(samp)
        res[n] = {"pool": len(pool), "n": N,
                  "t4_admissible": adm, "t4_admissible_rate": round(adm / N, 3),
                  "reasons": dict(reasons.most_common()),
                  "perm_invariant_rate_all": round(perm_all / N, 3),
                  "perm_invariant_rate_admissible": round(adm_perm / adm, 3) if adm else None,
                  "ext_new_vs_G4_rate_all": round(new_all / N, 3),
                  "admissible_and_ext_new": adm_new,
                  "admissible_new_but_affine_or_length_offset_of_G4": adm_aff,
                  "admissible_and_ext_new_net_of_affine": adm_new - adm_aff,
                  "admissible_top_level_acc_plus_X": adm_g1form}
        log("P2 %s: %s" % (n, json.dumps({k: res[n][k] for k in
                                           ("t4_admissible_rate", "perm_invariant_rate_admissible",
                                            "admissible_and_ext_new",
                                            "admissible_new_but_affine_or_length_offset_of_G4")})))
    OUT["P2_degeneracy"] = res


# ---------------------------------------------------------------- P3 (symbolic polynomials)
MAXDEG, MAXCOEF = 4, 10 ** 5


def P_(d):
    return tuple(sorted((k, c) for k, c in d.items() if c != 0))


def padd(a, b, s=1):
    d = dict(a)
    for k, c in b:
        d[k] = d.get(k, 0) + s * c
    return P_(d)


def pmul(a, b):
    d = defaultdict(int)
    for (k1, c1) in a:
        for (k2, c2) in b:
            d[(k1[0] + k2[0], k1[1] + k2[1])] += c1 * c2
    return P_(d)


def pconst(p):
    if not p:
        return 0
    if len(p) == 1 and p[0][0] == (0, 0):
        return p[0][1]
    return None


def ok(p):
    return p is not None and all(k[0] <= MAXDEG and k[1] <= MAXDEG and abs(c) <= MAXCOEF
                                 for k, c in p)


def pops(a, b):
    out = [padd(a, b), padd(a, b, -1), pmul(a, b)]
    e = pconst(b)
    if e is not None and 0 <= e <= 32:
        r = ((((0, 0), 1),))
        for _ in range(e):
            r = pmul(r, a)
            if not ok(r):
                r = None
                break
        out.append(r)
    return [x for x in out if ok(x)]


ACC, V = ((((1, 0), 1),)), ((((0, 1), 1),))


def atoms(consts):
    out = [ACC, V, (), ((((0, 0), 1),))]
    if consts:
        out += [((((0, 0), c),)) for c in range(2, 10)]
    return list(dict.fromkeys(out))


def level(prev, atomset, sym, left_only_new=True):
    out = set(prev)
    comp = [x for x in prev if x not in atomset]
    for a in atomset:
        for b in comp:
            out.update(pops(a, b))
    if sym:
        for a in comp:
            for b in atomset:
                out.update(pops(a, b))
            for b in comp:
                out.update(pops(a, b))
    return out


def sets_for(consts, sym):
    A = atoms(consts)
    S1 = set(A)
    for a in A:
        for b in A:
            S1.update(pops(a, b))
    S2 = level(S1, set(A), sym)
    return A, S1, S2


def split(p, sup):
    hi = tuple((k, c) for k, c in p if k not in sup)
    lo = tuple((k, c) for k, c in p if k in sup)
    return hi, lo


def neg(p):
    return tuple((k, -c) for k, c in p)


def d3_hits(targets, A, S2, sym, sup):
    """All targets T (a set of polynomials) with T = x + y or x - y, x an atom
    (left-atom) or x in S2 (sym), y in S2; or T in S2. Exact over S2 x S2 by
    grouping on the monomials outside the target support (they must cancel)."""
    hits = {T for T in targets if T in S2}
    by_hi = defaultdict(set)
    for y in S2:
        hi, lo = split(y, sup)
        by_hi[hi].add(lo)
    tl = list(targets)
    import numpy as np
    supl = sorted(sup)
    OFF, BASE = 10 ** 6, 2 * 10 ** 6 + 1

    def code(lo):
        d = dict(lo)
        c = 0
        for k in supl:
            c = c * BASE + (d.get(k, 0) + OFF)
        return c

    def vec(lo):
        d = dict(lo)
        return [d.get(k, 0) for k in supl]

    def enc(M):
        c = np.zeros(len(M), dtype=object)
        for j in range(len(supl)):
            c = c * BASE + (M[:, j] + OFF)
        return c

    TV = np.array([vec(t) for t in tl], dtype=np.int64)
    zero_cls = by_hi.get((), set())
    zset = {tuple(vec(lo)) for lo in zero_cls}
    tindex = {tuple(r): j for j, r in enumerate(TV.tolist())}
    lefts = S2 if sym else A
    for x in lefts:
        hx, lx = split(x, sup)
        if hx == ():                      # both parts in the target support: vectorised
            xv = np.array(vec(lx), dtype=np.int64)
            for need in (TV - xv, xv - TV):
                for j, r in enumerate(map(tuple, need.tolist())):
                    if r in zset:
                        hits.add(tl[j])
            continue
        for cands, sgn in ((by_hi.get(neg(hx)), 1), (by_hi.get(hx), -1)):
            if not cands:
                continue
            for y_lo in cands:
                s = padd(lx, y_lo, sgn)
                if s in targets:
                    hits.add(s)
    return hits


def ec_targets(mapping):
    out = {}
    for a, b, c in itertools.product(range(10), repeat=3):
        if mapping == "SUM":        # body = acc + f(v)
            T = P_({(1, 0): 1, (0, 2): a, (0, 1): b, (0, 0): c})
        else:                       # ORBIT body = f(acc) + v
            T = P_({(2, 0): a, (1, 0): b, (0, 0): c, (0, 1): 1})
        out[(a, b, c)] = T
    return out


def tier(a, b, c):
    t = ["CONST" if a == 0 and b == 0 else ("LINEAR" if a == 0 else "QUAD")]
    if a > 0 and b > 0 and c > 0:
        t.append("QUAD_COMPLEX")
    if a > 1 and b > 1 and c > 1:
        t.append("QUAD_COEF_GT1")
    return t


def p3():
    res = {}
    SUP = {"SUM": {(1, 0), (0, 2), (0, 1), (0, 0)}, "ORBIT": {(2, 0), (1, 0), (0, 0), (0, 1)}}
    for consts in (False, True):
        for sym in (False, True):
            A, S1, S2 = sets_for(consts, sym)
            log("P3 consts=%s sym=%s |S1|=%d |S2|=%d" % (consts, sym, len(S1), len(S2)))
            scales = [1, 2] + (list(range(3, 10)) if consts else [])   # final acc, acc+acc, acc*k
            for mapping in ("SUM", "ORBIT"):
                want = defaultdict(list)          # polynomial -> [(a, b, c)]
                for (a, b, c), T in ec_targets(mapping).items():
                    for s in (scales if mapping == "SUM" else [1]):
                        if mapping == "SUM":
                            if a % s or b % s or c % s:
                                continue
                            want[P_({(1, 0): 1, (0, 2): a // s, (0, 1): b // s,
                                     (0, 0): c // s})].append((a, b, c))
                        else:
                            want[T].append((a, b, c))
                for depth in (2, 3):
                    name = "%s%s_d%d" % ("SYM" if sym else "LEFT", "+CONST" if consts else "", depth)
                    if depth == 2:
                        hitp = {T for T in want if T in S2}
                    else:
                        hitp = d3_hits(set(want), A, S2, sym, SUP[mapping])
                    got = {abc for T in hitp for abc in want[T]}
                    cnt = Counter()
                    for (a, b, c) in ec_targets(mapping):
                        for t in tier(a, b, c):
                            cnt[t + "_n"] += 1
                            cnt[t] += (a, b, c) in got
                    row = {t: "%d/%d" % (cnt[t], cnt[t + "_n"]) for t in
                           ("CONST", "LINEAR", "QUAD", "QUAD_COMPLEX", "QUAD_COEF_GT1")}
                    res.setdefault(name, {})[mapping] = row
                    log("P3 %s %s %s" % (name, mapping, json.dumps(row)))
    OUT["P3_EC_symbolic"] = res


# ---------------------------------------------------------------- P4 OEIS LINREC + lag
def p4():
    sel = json.load(open(HERE.parents[1] / "compounding" / "rb5" / "cache" / "oeis_selection_rb5.json"))
    L = [s for s in sel["sequences"] if "LINREC" in s["strata"]]
    rows, cnt = [], Counter()
    for s in L:
        d = s["recurrence"]["d"]
        coef = s["recurrence"]["coef"]           # c1..cd, c0
        cs, c0 = coef[:d], coef[d]
        # canonical lag witness: body 'v' (acc = last element); final uses v, p and,
        # for d = 3, one more lag (not available with a single p register -> needs 2).
        regs = ["v", "p", "PP"][:d]
        if d == 3:
            cnt["order3_needs_two_lag_registers"] += 1
            rows.append({"A": s["A"], "d": d, "witness": None})
            continue
        terms = " + ".join("(%d * %s)" % (c, r) for c, r in zip(cs, regs) if c) or "0"
        final = "(%s + %d)" % (terms, c0)
        w = ("fold", "0", "v", final)
        t = s["terms"]
        okk = all(X.run(w, t[:k], k)[0] == t[k] for k in range(max(d, 2), len(t)))
        prof = X.family_profile(w) if okk else None
        # depth of the final in the extension's own templates: literal * reg terms
        nterms = sum(1 for c in cs if c) + (c0 != 0)
        rows.append({"A": s["A"], "d": d, "verified_on_terms": okk, "final": final,
                     "final_terms": nterms,
                     "t4_admissible": prof["admissible"] if prof else None,
                     "t4_reasons": prof["reasons"] if prof else None})
        cnt["order%d" % d] += 1
        cnt["order%d_verified" % d] += okk
        if prof:
            cnt["order%d_admissible" % d] += prof["admissible"]
            for r in prof["reasons"]:
                cnt["reason_" + r] += 1
            cnt["order%d_final_depth1_expressible" % d] += nterms <= 1
    # an input-driven order-2 recurrence (not an OEIS task): does T4 admit it?
    driven = {"x' = x + q + v (LAGACC)": ("fold", "0", "(acc + (q + v))", "acc"),
              "x' = 2x - q + v (LAGACC, CONST)": ("fold", "0", "(v + ((2 * acc) - q))", "acc"),
              "sum (v - p) (LAGV telescoping)": ("fold", "0", "(acc + (v - p))", "acc"),
              "sum v*p (LAGV adjacent products)": ("fold", "0", "(acc + (v * p))", "acc"),
              "sum i*v (INDEX weighted)": ("fold", "0", "(acc + (i * v))", "acc"),
              "acc + i (INDEX length-only)": ("fold", "0", "(acc + i)", "(acc + last)"),
              "sum 3v (CONST, G1 instance)": ("fold", "0", "(acc + (3 * v))", "acc"),
              "Horner base 7 mod m (CONST)": ("fold", "0", "(v + (7 * acc))", "(acc % last)")}
    dv = {}
    for k, w in driven.items():
        pr = X.family_profile(w)
        dv[k] = {"prog": list(w), "t4_admissible": pr["admissible"], "reasons": pr["reasons"],
                 "perm_invariant": X.perm_invariant(w)}
    OUT["P4_OEIS_LINREC_lag"] = {"counts": dict(cnt), "rows": rows, "driven_examples": dv}
    log("P4 %s" % json.dumps(dict(cnt)))
    log("P4 driven %s" % json.dumps({k: (v["t4_admissible"], v["reasons"]) for k, v in dv.items()}))


if __name__ == "__main__":
    which = sys.argv[1:] or ["p1", "p3", "p4", "p2"]
    for w in which:
        globals()[w]()
        json.dump(OUT, open(HERE / ("W5_PROBES_%s.json" % "_".join(which)), "w"), indent=1)
    log("done")
