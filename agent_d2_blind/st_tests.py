"""Substrate tests ST1 (homoiconicity), ST2 (determinism/totality), ST3
(expressiveness floor), plus the validity-filter diagnostic.

ST1-ST3 were declared in MANIFEST section 5 before any census ran.
"""
import json
import random

from d2 import g1, g2, g3, g3b, probes, census
from d2.core import ser

HOLE = "\x00HOLE"

# The canonical useful transformation this experiment would have needed:
#   M(core) = (if (null x) nil (cons core[x := (head x)] (self (tail x))))
# i.e. lift a seed core into a structural recursion over a list. Two interacting
# structural edits (variable re-binding + control scaffolding) whose decomposition
# is never given to any learner.
TARGET_WRAP = ("if", ("null", "x"), "nil", ("cons", HOLE, ("self", ("tail", "x"))))
CORES = ["x", ("cons", "x", "nil"), ("if", ("eq", "x", ("q", "a")), ("q", "c"), "x")]


def g1_build(v):
    """G1 expression evaluating to the constant term v, with HOLE -> the input."""
    if v == HOLE:
        return "x"
    if type(v) is str:
        return ("q", v)
    out = "nil"
    for u in reversed(v):
        out = ("cons", g1_build(u), out)
    return out


def g2_build(v):
    if v == HOLE:
        return "here"
    if type(v) is str:
        return ("qq", v)
    k = len(v)
    if k == 0:
        return "nilc"
    if k > 4:
        raise ValueError("arity")
    return ("L%d" % k,) + tuple(g2_build(u) for u in v)


def g3_build(v):
    if v == HOLE:
        return "v0"
    if type(v) is str:
        return ("qq", v)
    k = len(v)
    if k == 0:
        return "nilc"
    if k > 4:
        raise ValueError("arity")
    return ("L%d" % k,) + tuple(g3_build(u) for u in v)


# ------------------------------------------------------------------ ST1

def st1(basis, t1, t2):
    """apply(t2, t1) must yield a DIFFERENT valid transform of the same basis
    that still executes. Transform-of-transform must be native, not bolted on."""
    if basis is g1:
        r = g1.run(t2, t1)
    else:
        # raw meta application without the object-language validity check
        try:
            if basis is g2:
                r = ("ok", g2._exec(t2, t1, [0], 2000))
            else:
                rules = g3._rules(t2)
                if basis is g3b:
                    r = ("ok", g3b._pass(t1, rules, [0], 2000))
                else:
                    cur, ctr = t1, [0]
                    for _ in range(64):
                        cur, hit = g3._step(cur, rules, ctr, 2000)
                        if not hit:
                            break
                    r = ("ok", cur)
        except Exception as e:
            return {"pass": False, "why": "meta application raised %s" % type(e).__name__}
    if r[0] != "ok":
        return {"pass": False, "why": "meta application errored: %s" % (r[1],)}
    t1p = r[1]
    if not basis.valid_transform(t1p):
        return {"pass": False, "why": "result is not a valid transform of the basis",
                "result": ser(t1p) if type(t1p) in (str, tuple) else str(t1p)}
    if t1p == t1:
        return {"pass": False, "why": "no change"}
    a = basis.apply_transform(t1, probes.A[6])
    b = basis.apply_transform(t1p, probes.A[6])
    return {"pass": True, "t1": ser(t1), "t1_prime": ser(t1p),
            "t1_on_probe": str(a), "t1prime_on_probe": str(b),
            "behaviour_changed": a != b}


# ------------------------------------------------------------------ ST2

def st2(basis, enum, n, sample=4000, seed=0):
    rnd = random.Random(seed)
    pool = []
    for _, t in enum.stream(n):
        pool.append(t)
        if len(pool) > 200000:
            break
    ts = rnd.sample(pool, min(sample, len(pool)))
    bad = 0
    nondet = 0
    for t in ts:
        for p in probes.A:
            try:
                r1 = basis.apply_transform(t, p, census.LIMIT, census.DMAX)
                r2 = basis.apply_transform(t, p, census.LIMIT, census.DMAX)
            except Exception:
                bad += 1
                continue
            if r1 != r2:
                nondet += 1
            if r1[0] not in ("ok", "err", "invalid"):
                bad += 1
    return {"pass": bad == 0 and nondet == 0, "sampled": len(ts),
            "escaped_exceptions": bad, "nondeterministic": nondet}


# ------------------------------------------------------------------ ST3

def st3():
    out = {}

    # --- G1
    sub_g1 = ("if", ("eq", "x", ("q", "x")),
              ("cons", ("q", "head"), ("cons", ("q", "x"), "nil")),
              ("if", ("atom", "x"), "x",
               ("if", ("null", "x"), "nil",
                ("cons", ("self", ("head", "x")), ("self", ("tail", "x"))))))
    wrap_g1 = g1_build(TARGET_WRAP)
    out["G1"] = _check(g1, sub_g1, wrap_g1)

    # --- G2: no conditional, so the substitution edit is inexpressible
    wrap_g2 = ("at", "root", ("put", g2_build(TARGET_WRAP)))
    out["G2"] = _check(g2, None, wrap_g2,
                       sub_note="inexpressible: G2 has no conditional, so a node "
                                "cannot be rewritten only when it is the variable")

    # --- G3 / G3B
    sub_g3 = ("r1", ("rule", ("qp", "x"), ("L2", ("qq", "head"), ("qq", "x"))))
    wrap_g3 = ("r1", ("rule", "pv0", g3_build(TARGET_WRAP)))
    out["G3"] = _check(g3, sub_g3, wrap_g3)
    out["G3B"] = _check(g3b, sub_g3, wrap_g3)
    return out


def _check(basis, sub, wrap, sub_note=None):
    rec = {"sub_size": basis.size(sub) if sub is not None else None,
           "wrap_size": basis.size(wrap),
           "sub": ser(sub) if sub is not None else sub_note,
           "wrap": ser(wrap)}
    results = []
    ok_all = True
    for core in CORES:
        if sub is None:
            ok_all = False
            results.append({"core": ser(core), "status": "SUB inexpressible"})
            continue
        r1 = basis.apply_transform(sub, core, 4000, 24)
        if r1[0] != "ok":
            ok_all = False
            results.append({"core": ser(core), "status": "SUB failed: %s" % (r1[1],)})
            continue
        r2 = basis.apply_transform(wrap, r1[1], 4000, 24)
        if r2[0] != "ok":
            ok_all = False
            results.append({"core": ser(core), "status": "WRAP failed: %s" % (r2[1],)})
            continue
        m = r2[1]
        # does M(core) actually map core over a list?
        inp = ("a", "b", "c")
        got = g1.run(m, inp, 4000, 24)
        want = []
        okw = True
        for e in inp:
            rr = g1.run(core, e, 4000, 24)
            if rr[0] != "ok":
                okw = False
                break
            want.append(rr[1])
        expected = tuple(want) if okw else None
        good = got[0] == "ok" and expected is not None and got[1] == expected
        ok_all = ok_all and good
        results.append({"core": ser(core), "M": ser(m), "M_on_abc": str(got),
                        "expected": str(expected), "correct": good})
    rec["results"] = results
    rec["pass"] = ok_all
    return rec


# --------------------------------------------------- validity-filter diagnostic

def reach(basis, enum, n):
    C = census.Census(basis, probes.A, probes.I12, probes.I24)
    r = C.scan(enum, n)
    return {"programs": r["n_total"], "live_fraction": r["n_live"] / r["n_total"],
            "distinct_valid_artifacts_reached": len(C.term_id),
            "distinct_struct_classes": r["n_struct_classes"]}


if __name__ == "__main__":
    res = {}
    res["ST3_expressiveness_floor"] = st3()

    cfg = [("G1", g1, g1.Enum(), 6), ("G2", g2, g2.Enum(), 6),
           ("G3", g3, g3.Enum(), 7), ("G3B", g3b, g3.Enum(), 7)]

    t1s = {
        "G1": ("cons", ("head", "x"), ("tail", "x")),
        "G2": ("at", "root", ("put", ("L2", ("qq", "head"), "here"))),
        "G3": ("r1", ("rule", ("qp", "a"), ("qq", "b"))),
        "G3B": ("r1", ("rule", ("qp", "a"), ("qq", "b"))),
    }
    t2s = {
        "G1": ("cons", ("q", "tail"), ("cons", "x", "nil")),
        "G2": ("at", ("d1", "root"), ("put", ("L2", ("qq", "d0"), ("qq", "nil")))),
        "G3": ("r1", ("rule", ("qp", "a"), ("qq", "c"))),
        "G3B": ("r1", ("rule", ("qp", "a"), ("qq", "c"))),
    }

    res["ST1_homoiconicity"] = {}
    res["ST2_determinism_totality"] = {}
    res["validity_filter"] = {}
    for name, basis, enum, n in cfg:
        res["ST1_homoiconicity"][name] = st1(basis, t1s[name], t2s[name])
        res["ST2_determinism_totality"][name] = st2(basis, enum, n)
        print(name, "ST1", res["ST1_homoiconicity"][name]["pass"],
              "ST2", res["ST2_determinism_totality"][name]["pass"])
    for name, basis, enum, n in cfg:
        res["validity_filter"][name] = reach(basis, basis.Enum() if name != "G3B" else g3.Enum(), n)
        print(name, res["validity_filter"][name])

    json.dump(res, open("ledgers/substrate_tests.json", "w"), indent=1, default=str)
    print(json.dumps(res["ST3_expressiveness_floor"], indent=1, default=str)[:3000])
