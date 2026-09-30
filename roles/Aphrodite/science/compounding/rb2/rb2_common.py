"""RB-2 shared library (forensic, not a disposition).

Parameterised copy of spikes/k1_supply_census.witness_row (the tribunal's
STRUCTURAL preconditions as parameters), the task-grounded additive test,
the schema-family label, a cached exact Q2 (== a17.qualify for the fixed
family name Q2_NAME; validated against a17.qualify in rb2_census.py), the
K7-style extensional G1 test, and K2-style solvability cells.
Seeds: the forensic label APHRODITE/COMPOUNDING/RB2/v1 only.
"""
import math
import os
import random
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROLE = HERE.parents[2]
ENG = ROLE / "engine"
SPIKES = ROLE / "science" / "frontier" / "spikes"
for p in (str(ENG), str(ENG / "accel"), str(SPIKES)):
    if p not in sys.path:
        sys.path.insert(0, p)
os.environ["A17_FASTEVAL"] = "1"
import a17                  # noqa: E402
import basis_v4 as G        # noqa: E402
import engine as E          # noqa: E402
import fair as FR           # noqa: E402
import fasteval as FE       # noqa: E402
import identity as I        # noqa: E402
import tier3d as T3D        # noqa: E402
import tier3e as T3E        # noqa: E402
import tribunal_t4 as T4    # noqa: E402

SEED_LABEL = "APHRODITE/COMPOUNDING/RB2/v1"
STRATA = ["add", "sub", "mul", "fdiv", "mod", "gcd", "powr"]
H1 = ["0", "1"]
WIDE = ["0", "1", "(1 + 1)", "first", "last"]
WORKERS = 5
P_MOD = 2 ** 127 - 1          # V4: a prime below CEIL = 10**40

# the tribunal-precondition variants measured on the draws
VARIANTS = {
    "V0": dict(inv=True, prefix=False, stress=200, ce_ks=(2, 3, 80, 150), sem="exact", inits="H1"),
    "V1": dict(inv=False, prefix=False, stress=200, ce_ks=(2, 3, 80, 150), sem="exact", inits="H1"),
    "V2": dict(inv=False, prefix=True, stress=200, ce_ks=(2, 3, 80, 150), sem="exact", inits="H1"),
    "V3": dict(inv=True, prefix=False, stress=60, ce_ks=(2, 3, 40, 60), sem="exact", inits="H1"),
    "V4": dict(inv=True, prefix=False, stress=200, ce_ks=(2, 3, 80, 150), sem="modP", inits="H1"),
    "V5": dict(inv=True, prefix=False, stress=200, ce_ks=(2, 3, 80, 150), sem="exact", inits="WIDE"),
    "V6": dict(inv=False, prefix=False, stress=60, ce_ks=(2, 3, 40, 60), sem="exact", inits="WIDE"),
}
# T4-world variants use tribunal_t4.family_profile instead of a parameterised row
T4_VARIANTS = {"V7_T4_WIDE": "WIDE", "V8_T4_H1": "H1"}


def letter_name(prefix, obj):
    """A digit-free family name derived from a hash of obj."""
    return prefix + "".join(chr(97 + int(c, 16)) for c in I._sha(obj)[:12])


def mentions(src, n):
    return re.search(r"\b%s\b" % n, src) is not None


def worker_init():
    a17.worker_init()


# ---------------------------------------------------------------- draws
def sample(label=SEED_LABEL, n_per=1500):
    """Paired draws: each draw fixes (op, body, final) and one uniform u that
    picks the init in H1 and in the widened set, so V5-V7 differ from V0-V4 in
    the init only."""
    rng = random.Random(I._seed(label))
    finals = [f for f in G.FINAL_SPACE if mentions(f, "acc")]
    out = []
    for op in STRATA:
        pool = [b for b in G.BODY_SPACE if T3E._top_op(b) == op and mentions(b, "acc") and mentions(b, "v")]
        for k in range(n_per):
            b, f, u = rng.choice(pool), rng.choice(finals), rng.random()
            out.append({"op": op, "k": k, "body": b, "final": f,
                        "init_H1": H1[int(u * len(H1))], "init_WIDE": WIDE[int(u * len(WIDE))]})
    return out


# ---------------------------------------------------------------- evaluators
def _red(x):
    r = x % P_MOD
    return r - P_MOD if r > P_MOD // 2 else r


def run_mod(p, nums):
    """V4 semantics: every accumulator value and the output reduced to the
    symmetric residue mod P_MOD; no ceiling. Exceptions -> None."""
    vals, first, last = nums[:-1], nums[0], nums[-1]
    try:
        _, i, b, f = p
        bf = FE.fn(b)
        acc = _red(FE.fn(i)(0, 0, first, last))
        for v in vals:
            acc = bf(acc, v, first, last)
            if acc is None:
                return None
            acc = _red(acc)
        out = FE.fn(f)(acc, vals[-1] if vals else 0, first, last)
        return None if out is None else _red(out)
    except Exception:  # noqa: BLE001
        return None


def row(p, prm):
    """Parameterised K1 witness_row. With V0's parameters it consumes the rng
    exactly as k1_supply_census.witness_row does and returns the same flags."""
    rng = random.Random(repr(p))
    if prm["sem"] == "exact":
        run = lambda xs, m: FE.run_program(p, xs + [m], True)
    else:
        run = lambda xs, m: run_mod(p, xs + [m])
    wrap = [0]

    def chk(xs, m):
        o = run(xs, m)
        if prm["sem"] == "modP" and o != FE.run_program(p, xs + [m], True):
            wrap[0] += 1
        return o
    inv = True
    if prm["inv"]:
        for _ in range(25):
            xs = [rng.randint(2, 30) for _ in range(rng.randint(5, 30))]
            m = rng.randint(3, 97)
            perm = xs[1:]
            rng.shuffle(perm)
            a, b = chk(xs, m), chk([xs[0]] + perm, m)
            if a is None or b is None or a != b:
                inv = False
                break
    prefix_viol = 0
    if prm["prefix"]:
        # generator-side prefix-extension consistency: fold(xs+[y]) must equal
        # final(body(acc(xs), y)). For a fold witness this holds by construction.
        _, i0, b0, f0 = p
        for _ in range(25):
            xs = [rng.randint(2, 30) for _ in range(rng.randint(5, 30))]
            y, m = rng.randint(2, 30), rng.randint(3, 97)
            whole = FE.run_program(p, xs + [y] + [m], True)
            a = FE._fold_acc(FE.fn(i0), FE.fn(b0), xs, xs[0], m)
            if a is FE._FAIL:
                cont = None
            else:
                try:
                    a2 = FE.fn(b0)(a, y, xs[0], m)
                    cont = None if a2 is None or abs(a2) > G.CEIL else FE._final(FE.fn(f0), a2, y, xs[0], m)
                except Exception:  # noqa: BLE001
                    cont = None
            prefix_viol += whole != cont
    ext_none = sum(chk([rng.randint(2, 30) for _ in range(rng.randint(20, 60))], rng.randint(3, 97)) is None
                   for _ in range(20))
    st_none = sum(chk([rng.randint(2, 30) for _ in range(prm["stress"])], rng.randint(3, 97)) is None
                  for _ in range(10))
    ce_none = 0
    for i in range(12):
        k = rng.choice(list(prm["ce_ks"]))
        xs = [rng.randint(2, 30)] * k if i % 3 == 0 else [rng.randint(2, 30) for _ in range(k)]
        ce_none += chk(xs, rng.choice([1, 2, rng.randint(3, 97)])) is None
    outs, dep = set(), False
    for _ in range(60):
        xs = [rng.randint(2, 30) for _ in range(rng.randint(4, 9))]
        m = rng.randint(3, 97)
        o = run(xs, m)
        outs.add(o)
        ys = list(xs)
        ys[-1] = ys[-1] + 1 if ys[-1] < 30 else 2
        if run(ys, m) != o:
            dep = True
    nondeg = len(outs - {None}) >= 3 and dep and None not in outs
    struct_ok = inv and ext_none == 0 and st_none == 0 and ce_none == 0 and prefix_viol == 0
    return {"invariant": inv, "prefix_violations": prefix_viol, "ext_none": ext_none,
            "stress_none": st_none, "ce_none": ce_none, "nondegenerate": nondeg,
            "struct_ok": struct_ok, "admissible": struct_ok and nondeg, "wrap_probes": wrap[0]}


# ---------------------------------------------------------------- body semantics
ACC_GRID = (0, 1, 2, 3, 4, 5, 7, 10, 16, 31, 97, 1000)
VFL_GRID = [(v, f, l) for v in (2, 3, 5, 7, 12, 30) for f in (2, 5, 17) for l in (1, 3, 41, 97)]


def body_class(body):
    """Task-grounded test on non-negative accumulators.
    ADDITIVE : b(acc,v,f,l) - acc independent of acc for every (v,f,l)
    ACC_FREE : b independent of acc
    AFFINE_* : b = s*acc + c (s, c independent of acc), s != 1 somewhere
    NA_<op>  : otherwise; <op> = first non-additive operator on the shallowest
               root-to-acc path (the mechanism)."""
    f = FE.fn(body)
    add = free = aff = True
    slopes = set()
    slope_dep_v = False
    by_fl = {}
    for v, fi, la in VFL_GRID:
        ys = []
        for a in ACC_GRID:
            try:
                y = f(a, v, fi, la)
            except Exception:  # noqa: BLE001
                y = None
            ys.append(y)
        if any(y is None for y in ys):
            add = free = aff = False
            break
        d = [y - a for y, a in zip(ys, ACC_GRID)]
        add &= len(set(d)) == 1
        free &= len(set(ys)) == 1
        s = ys[1] - ys[0]
        aff &= all(y == s * a + ys[0] for y, a in zip(ys, ACC_GRID))
        slopes.add(s)
        by_fl.setdefault((fi, la), set()).add(s)
    if add and aff:
        return "ADDITIVE"
    if free:
        return "ACC_FREE"
    if aff:
        slope_dep_v = any(len(s) > 1 for s in by_fl.values())
        if slope_dep_v:
            return "AFFINE_SCALE_V"
        return "AFFINE_CONST_SLOPE" if len(slopes) == 1 else "AFFINE_SLOPE_FL"
    return "NA_" + _mech_op(I.parse(body)).upper()


def _mech_op(t):
    best = None

    def walk(t, path, depth):
        nonlocal best
        op, args = t
        if op == "var:acc":
            na = [o for o in path if o not in ("add", "sub")]
            if na and (best is None or depth < best[0]):
                best = (depth, na[0])
            return
        for a in args:
            walk(a, path + [op], depth + 1)
    walk(t, [], 0)
    return best[1] if best else "other"


def additive(body):
    return body_class(body) == "ADDITIVE"


# ---------------------------------------------------------------- cached exact Q2
# NAMES MUST BE DIGIT-FREE: prompts are parsed with re.findall(r"-?\d+"), so a
# digit in "Family <name> over:" becomes a list element (a17/K2 use letters only).
Q2_NAME = "rbtwoqfamily"
Q2_LABEL = "RB2"
_Q2 = {}


def _q2_pool():
    """Distinct PRISTINE-reachable output vectors on the Q2 probe pool of the
    fixed family name Q2_NAME, as an exact per-column integer code matrix."""
    if "mat" in _Q2:
        return _Q2
    import numpy as np
    prov = a17.Prov({Q2_NAME: ("(acc + v)", "acc", "0")})
    pool = prov.tasks(Q2_NAME, 240, E.dev_entropy(Q2_LABEL + "-pool-" + Q2_NAME, 0))
    probes = [prov.nums_of(t) for t in pool]
    pinfo = [(n[:-1], n[0], n[-1], (n[:-1][-1] if len(n) > 1 else 0)) for n in probes]
    accs, vecs = {}, {}
    for p in T3D.reachable_programs():
        _, i, b, fi = p
        al = accs.get((i, b))
        if al is None:
            al = accs[(i, b)] = [FE._fold_acc(FE.fn(i), FE.fn(b), vals, fst, lst) for vals, fst, lst, _ in pinfo]
        ffn = FE.fn(fi)
        v = tuple(None if a is FE._FAIL else FE._final(ffn, a, vl, fst, lst)
                  for a, (_v, fst, lst, vl) in zip(al, pinfo))
        vecs[v] = 1
    vecs = list(vecs)
    cols = [dict() for _ in range(240)]
    mat = np.empty((len(vecs), 240), dtype=np.int32)
    for r, v in enumerate(vecs):
        for c in range(240):
            x = v[c]
            if x is None:
                mat[r, c] = -2
            else:
                mat[r, c] = cols[c].setdefault(x, len(cols[c]))
    _Q2.update(mat=mat, cols=cols, probes=probes)
    return _Q2


def qualify_cached(init, body, final):
    """Exactly a17.qualify(Prov({Q2_NAME: (body, final, init)}), Q2_NAME, Q2_LABEL)."""
    import numpy as np
    q = _q2_pool()
    target = ("fold", init, body, final)
    tv = [FE.run_program(target, n, True) for n in q["probes"]]
    full = np.array([-2 if x is None else q["cols"][c].get(x, -3) for c, x in enumerate(tv)], dtype=np.int32)
    match = np.array([-1 if x is None else q["cols"][c].get(x, -3) for c, x in enumerate(tv)], dtype=np.int32)
    wrong = ~(q["mat"] == full).all(axis=1)
    eqm = (q["mat"][wrong] == match)
    rng = random.Random(E.dev_entropy(Q2_LABEL + "-draws-" + Q2_NAME, 0))
    for size in (4, 6, 8, 12, 16, 24):
        s = [int(eqm[:, rng.sample(range(240), size)].all(axis=1).sum()) for _ in range(200)]
        up = statistics.mean(s) + 1.96 * statistics.pstdev(s) / math.sqrt(len(s))
        if up < 0.05:
            return size
    return None


def qualify_reference(init, body, final):
    prov = a17.Prov({Q2_NAME: (body, final, init)})
    return a17.qualify(prov, Q2_NAME, Q2_LABEL)


# ---------------------------------------------------------------- K7-style extensional G1 test
_G1 = {}


def _g1_entry():
    if not _G1:
        e = [x for x in a17.L1_entries() if x["name"] == "derived_0"][0]
        inits = list(dict.fromkeys(list(e["inits"]) + WIDE))
        _G1.update(inits=inits, bodies=list(e["bodies"]), finals=list(e["finals"]))
    return _G1


def g1_equivalent(init, body, final, n=150):
    """Is the witness extensionally equal, on n task-domain inputs (values 2-30,
    lengths 2-60, query 1-97), to a program in G1's coverage (derived_0 bodies x
    finals, inits H1 plus the widened set -- conservative)?"""
    g = _g1_entry()
    rng = random.Random(body + final + init)
    ins = [[rng.randint(2, 30) for _ in range(rng.randint(2, 60))] + [rng.randint(1, 97)] for _ in range(n)]
    w = ("fold", init, body, final)
    tv = [FE.run_program(w, x, True) for x in ins]
    pinfo = [(x[:-1], x[0], x[-1]) for x in ins]
    ffns = [(fi, FE.fn(fi)) for fi in g["finals"]]
    for i in g["inits"]:
        ifn = FE.fn(i)
        for b in g["bodies"]:
            bfn = FE.fn(b)
            a0 = FE._fold_acc(ifn, bfn, *pinfo[0])
            cand = [(fi, ff) for fi, ff in ffns
                    if (None if a0 is FE._FAIL else FE._final(ff, a0, pinfo[0][0][-1], pinfo[0][1], pinfo[0][2])) == tv[0]]
            if not cand:
                continue
            accs = [a0] + [None] * (n - 1)
            for fi, ff in cand:
                ok = True
                for j in range(1, n):
                    if accs[j] is None:
                        a = FE._fold_acc(ifn, bfn, *pinfo[j])
                        accs[j] = a
                    a = accs[j]
                    got = None if a is FE._FAIL else FE._final(ff, a, pinfo[j][0][-1], pinfo[j][1], pinfo[j][2])
                    if got != tv[j]:
                        ok = False
                        break
                if ok:
                    return ["fold", i, b, fi]
    return None


# ---------------------------------------------------------------- K2-style solvability
def t4_qualifies(prov, name, prog):
    art = a17.M.artifact_for(name, prog, a17.EMITTER)
    T4.use_provider(prov)
    tr = T4.TribunalT4.after_freeze(art, name)
    return tr.qualified(tr.score(art))


def old_qualifies(prov, name, prog):
    a17.M.use_provider(prov)
    art = a17.M.artifact_for(name, prog, a17.EMITTER)
    tr = a17.M.MetaTribunal.after_freeze(art, name)
    return tr.qualified(tr.score(art))


def solve_cells(init, body, final, size, name, cells=4, label="RB2", tribunal=None):
    """K2 cells. 'solved' = a dev-consistent hit within escrow (K2's upper
    bound). With tribunal in {"T4", "OLD"}, also 'qualified' = the first of up
    to 5 hits whose emitted artifact the tribunal qualifies (a17.run_recipient
    pattern)."""
    prov = a17.Prov({name: (body, final, init)})
    a17.M.use_provider(prov)
    check = {"T4": t4_qualifies, "OLD": old_qualifies}.get(tribunal)
    out = {}
    for arm, ents in (("PRISTINE", FR.pristine().entries), ("L1", a17.L1_entries())):
        lib = FR.KLib(ents)
        solved, qual, charges, coords = 0, 0, [], {}
        for i in range(cells):
            c = FR.Cell(prov, name, i, size, label="%s-%s" % (label, arm))
            esc = E.Escrow(a17.ESCROW)
            hits = FR.search_collect(lib, c.parsed, esc, a17.ESCROW, c.seed,
                                     max_hits=5 if check else 1)
            if hits:
                solved += 1
                charges.append(hits[0][2])
                coords[hits[0][1]] = coords.get(hits[0][1], 0) + 1
                if check and any(check(prov, name, h[0]) for h in hits):
                    qual += 1
        out[arm] = {"solved": solved, "charges": charges, "coords": coords}
        if check:
            out[arm]["qualified"] = qual
    return out
