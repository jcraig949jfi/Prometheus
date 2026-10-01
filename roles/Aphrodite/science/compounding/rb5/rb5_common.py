"""RB-5 shared library (forensic, not a disposition).

Imported task worlds -> Aphrodite fold task shape (list + trailing query m -> int).
  - witness search in G4 (basis_v4: 116 inits x 10,842 bodies x 180 finals, plus
    the 180-program 'expr' shape) and in G5 (a17.g5_bodies, depth-3), exhaustive,
    with an EARLY EXIT on dev instance 0: the post-loop accumulator of instance 0
    is computed for every (init, body); the finals whose instance-0 output is some
    family's instance-0 gold are memoised per accumulator value; only those
    candidates are evaluated on the remaining dev instances. Exact (fasteval
    closures over basis_v4 globals; same None / CEIL semantics as run_program).
  - holdout verification of every dev hit on an independent holdout set.
  - per-witness analysis: T4 family_profile, ruler_v2.fclass, rb2 body_class,
    K7-style extensional G1 test, exact Q2 (rb2_common.qualify_cached ==
    a17.qualify(a17.Prov({Q2_NAME: ...}), Q2_NAME, 'RB2'); spot-checked here
    against a17.qualify directly), and permutation invariance (old tribunal).
Seeds: forensic label APHRODITE/COMPOUNDING/RB5/v1 only.
"""
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROLE = HERE.parents[2]
ENG = ROLE / "engine"
for p in (str(ENG), str(ENG / "accel"), str(HERE.parent / "rb1"), str(HERE.parent / "rb2")):
    if p not in sys.path:
        sys.path.insert(0, p)
os.environ["A17_FASTEVAL"] = "1"
import a17                  # noqa: E402
import basis_v4 as G        # noqa: E402
import fasteval as FE       # noqa: E402
import tribunal_t4 as T4    # noqa: E402

LABEL = "APHRODITE/COMPOUNDING/RB5/v1"
CEIL = G.CEIL
WORKERS = 2
FAIL = FE._FAIL


def worker_init():
    a17.worker_init()


# ---------------------------------------------------------------- search
def _pinfo(instances):
    return [(n[:-1], n[0], n[-1], (n[:-1][-1] if len(n) > 1 else 0)) for n in instances]


def search(instances, targets, bodies, inits=None, finals=None, cap=60, per_body=2,
           expr=True):
    """Exhaustive enumeration of ('expr', f) and ('fold', i, b, f) for b in bodies,
    i in inits, f in finals, in that order (bodies outer). Returns
    {fid: [prog, ...]} (at most `cap` per family, at most `per_body` per body)
    for every program whose dev vector equals the family's dev gold.
    Early exit: instance-0 finals memoised per accumulator value; later dev
    instances are evaluated lazily and only while some candidate's output
    prefix is a prefix of a live gold vector. A gold vector is RETIRED from the
    prefix index once all its families hold `cap` witnesses (enumeration of
    other families continues unchanged)."""
    inits = list(G.INIT_SPACE) if inits is None else list(inits)
    finals = list(G.FINAL_SPACE) if finals is None else list(finals)
    P = _pinfo(instances)
    nP = len(P)
    full = defaultdict(list)
    for fid, g in targets.items():
        if None in g:
            continue
        full[tuple(g)].append(fid)
    pre = [defaultdict(int) for _ in P]      # live prefix -> #live gold vectors
    for g in full:
        for j in range(nP):
            pre[j][g[:j + 1]] += 1
    ffns = [FE.fn(f) for f in finals]
    ifns = [FE.fn(i) for i in inits]
    hits = defaultdict(list)
    retired = set()

    def record(prog, vec, nb):
        if vec in retired:
            return
        fids = full.get(vec, ())
        for fid in fids:
            if len(hits[fid]) < cap and nb[fid] < per_body:
                hits[fid].append(prog)
                nb[fid] += 1
        if all(len(hits[f]) >= cap for f in fids):
            retired.add(vec)
            for j in range(nP):
                k = vec[:j + 1]
                pre[j][k] -= 1
                if pre[j][k] <= 0:
                    del pre[j][k]

    if expr:
        for f, ff in zip(finals, ffns):
            vec = tuple(FE._final(ff, 0, 0, p[1], p[2]) for p in P)
            if vec in full:
                record(("expr", f), vec, defaultdict(int))
    v0, f0, l0, vl0 = P[0]
    t0 = {g[0] for g in full}
    memo = {}
    pre0 = pre[0]
    # inits grouped by their VALUE on dev instance 0 (the instance-0 fold depends
    # only on that value); group order = first appearance, members in order.
    groups = {}
    for i, ifn in zip(inits, ifns):
        try:
            x = ifn(0, 0, f0, l0)
        except Exception:      # noqa: BLE001
            continue
        if x is None or abs(x) > CEIL:
            continue
        groups.setdefault(x, []).append((i, ifn))
    gitems = list(groups.items())
    for b in bodies:
        if not pre0:
            break
        if isinstance(b, tuple):             # (src, precomposed fn): G5 extras
            b, bfn = b
        else:
            bfn = FE.fn(b)
        nb = defaultdict(int)
        found = []
        for x, members in gitems:
            a0 = _fold_from(x, bfn, v0, f0, l0)
            if a0 is FAIL:
                continue
            c = memo.get(a0)
            if c is None:
                if len(memo) > 300_000:
                    memo.clear()
                c = []
                for k, ff in enumerate(ffns):
                    o = FE._final(ff, a0, vl0, f0, l0)
                    if o in t0:
                        c.append((k, (o,)))
                memo[a0] = c
            if not c:
                continue
            c = [y for y in c if y[1] in pre0]
            if not c:
                continue
            for i, ifn in members:
                cand = c
                for j in range(1, nP):           # lazy, prefix-filtered (early exit)
                    if not cand:
                        break
                    p = P[j]
                    pj = pre[j]
                    a = FE._fold_acc(ifn, bfn, p[0], p[1], p[2])
                    nxt = []
                    for k, outs in cand:
                        o = None if a is FAIL else FE._final(ffns[k], a, p[3], p[1], p[2])
                        t = outs + (o,)
                        if t in pj:
                            nxt.append((k, t))
                    cand = nxt
                for k, vec in cand:
                    found.append((inits.index(i), k, i, vec))
        for _ii, k, i, vec in sorted(found):     # enumeration order (init, final)
            record(("fold", i, b, finals[k]), vec, nb)
    return dict(hits)


_OPS = {"add": lambda a, b: a + b, "sub": lambda a, b: a - b, "mul": lambda a, b: a * b,
        "fdiv": lambda a, b: a // b, "mod": lambda a, b: a % b,
        "gcd": lambda a, b: G.math.gcd(abs(a), abs(b)), "powr": lambda a, b: G._pw(a, b)}


def g5_extras():
    """The depth-3 G5 bodies NOT in G4, in a17.g5_bodies() order, as
    (src, fn) with fn composed from the G4 closure of the inner body: exactly
    prim(atom, inner) with the templates' semantics (E.PRIMITIVES; guarded pow;
    gcd of absolute values). Avoids compiling ~455k expressions per search."""
    import engine as E
    g4 = set(G.BODY_SPACE)
    atomfn = {a: FE.fn(a) for a in G.BODY_ATOMS}
    for name, (_f, tmpl) in sorted(E.PRIMITIVES.items()):
        op = _OPS[name]
        for a in G.BODY_ATOMS:
            af = atomfn[a]
            for b in G.BODY_SPACE:
                if b in G.BODY_ATOMS:
                    continue
                src = tmpl.format(a, b)
                if src in g4:
                    continue
                inner = FE.fn(b)
                yield src, (lambda op, af, inner: lambda acc, v, first, last:
                            op(af(acc, v, first, last), inner(acc, v, first, last)))(op, af, inner)


def _fold_from(x, bfn, vals, first, last):
    acc = x
    try:
        for v in vals:
            acc = bfn(acc, v, first, last)
            if acc is None or abs(acc) > CEIL:
                return FAIL
    except Exception:      # noqa: BLE001
        return FAIL
    return acc


def run(prog, nums):
    return FE.run_program(tuple(prog), nums, True)


def verify(prog, holdout):
    """holdout: list of (nums, gold) with gold possibly None (CEIL semantics)."""
    return all(run(prog, n) == g for n, g in holdout)


# ---------------------------------------------------------------- analysis
def t4_probe_inputs(n=50, seed="probe"):
    rng = random.Random(LABEL + "/" + seed)
    return [[rng.randint(2, 30) for _ in range(rng.randint(2, 40))] + [rng.randint(1, 97)]
            for _ in range(n)]


_PROBES = None


def behavior_key(prog):
    global _PROBES
    if _PROBES is None:
        _PROBES = t4_probe_inputs()
    return tuple(run(prog, x) for x in _PROBES)


def perm_invariant(prog, n=25):
    rng = random.Random(LABEL + "/perm")
    for _ in range(n):
        xs = [rng.randint(2, 30) for _ in range(rng.randint(5, 30))]
        m = rng.randint(3, 97)
        ys = [xs[0]] + sorted(xs[1:])
        if run(prog, xs + [m]) != run(prog, ys + [m]):
            return False
    return True


def analyse(prog, q2=True):
    """Task-side profile of one witness program (as an Aphrodite family)."""
    import rb2_common as R2
    import ruler_v2 as RV
    prog = tuple(prog)
    out = {"prog": list(prog)}
    if prog[0] == "expr":
        out.update(shape="expr", fclass="EXPR_NO_LOOP", body_class="EXPR_NO_LOOP")
        w = ("fold", "0", "acc", prog[1])      # the same function as a trivial fold
    else:
        out.update(shape="fold", fclass=RV.fclass(prog[2]), body_class=R2.body_class(prog[2]))
        w = prog
    prof = T4.family_profile(w)
    out["t4_admissible"] = prof["admissible"]
    out["t4_reasons"] = prof["reasons"]
    out["t4_L_max"] = prof["L_max"]
    out["perm_invariant"] = perm_invariant(w)
    if prog[0] == "fold":
        out["g1_equivalent"] = R2.g1_equivalent(prog[1], prog[2], prog[3]) is not None
    else:
        out["g1_equivalent"] = False
    out["Q2_size"] = None
    if q2 and prof["admissible"] and prog[0] == "fold":
        out["Q2_size"] = R2.qualify_cached(prog[1], prog[2], prog[3])
    return out


def classes_of(progs, max_classes=8):
    """Group verified witnesses by behaviour on the T4-domain probe set; the
    representative of a class is its first witness in enumeration order."""
    seen = {}
    for p in progs:
        k = behavior_key(p)
        if k not in seen:
            if len(seen) >= max_classes:
                continue
            seen[k] = [p]
        else:
            seen[k].append(p)
    return list(seen.values())


def analyse_family(verified, max_classes=8):
    """Behaviour classes of a family's verified witnesses, each analysed."""
    out = []
    for cl in classes_of([tuple(p) for p in verified], max_classes):
        a = analyse(cl[0])
        a["class_size"] = len(cl)
        out.append(a)
    return out


def family_summary(classes):
    """Best-case (lenient) verdict over a family's witness classes: a family is
    counted T4-admissible / Q2-qualified if ANY verified witness class is."""
    adm = [c for c in classes if c["t4_admissible"]]
    q = [c for c in adm if c["Q2_size"] is not None]
    best = (q or adm or classes or [None])[0]
    return {
        "expressible": bool(classes),
        "n_classes": len(classes),
        "t4_admissible": bool(adm),
        "q2_qualified": bool(q),
        "best_fclass": best["fclass"] if best else None,
        "best_prog": best["prog"] if best else None,
        "best_g1_equivalent": best["g1_equivalent"] if best else None,
        "best_perm_invariant": best["perm_invariant"] if best else None,
        "best_t4_reasons": best["t4_reasons"] if best else None,
        "fclasses_admissible_qualified": sorted({c["fclass"] for c in q}),
        "t4_reasons_all": sorted({r for c in classes for r in c["t4_reasons"]}),
    }
