"""v4 s4.3 tracer agreement: Archaeon's tracer (bee_ref_tracer) vs the independent REFERENCE tracer
(ops/.../reftracer/ref_tracer_bee.py, written by an isolated worker from the prereg text alone).
Compared per locus: data label, addr_deps, ctrl_deps (at store), exec_deps (at store), performer entity, written.
CONSTANT labels are normalised: the reference treats CONSTANT as having no base labels (its CHOICE 3), and Archaeon's tracer keeps
("CONST", kind) bases, which are dropped here. Constant kinds are not compared.
Inputs: the 29 fixture images, N random interactions (random writer and occupant tapes, random input), and M mutated replicators.
    python -m archaeon.attribution.probes.tracer_agreement [--fuzz 300] [--replicators 200]
"""
import importlib.util
import os
import random
import sys
from collections import Counter

from archaeon.attribution import bee_ref_tracer as T
from archaeon.attribution import bee_fixtures as F

REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ops", "campaigns", "C-001", "ATTRIBUTION_ARC_2026-09-28",
                   "reftracer", "ref_tracer_bee.py")
L = 64


def load_ref():
    sp = importlib.util.spec_from_file_location("ref_tracer_bee", os.path.abspath(REF)); m = importlib.util.module_from_spec(sp)
    sys.modules["ref_tracer_bee"] = m; sp.loader.exec_module(m); return m


def norm_ref(lab):
    k = lab[0]
    if k == "ENTITY": return ("E", {"w": "W", "o": "P"}[lab[1]], lab[2])
    if k == "INPUT": return ("INPUT", lab[1])
    if k == "CONSTANT": return ("CONST",)
    if k == "COMPUTED": return ("COMPUTED", frozenset(norm_ref(b) for b in lab[1]))
    if k == "COMPUTED_FROM":
        inner = lab[1]
        bases = (frozenset(norm_ref(b) for b in inner[1]) if inner[0] == "COMPUTED" else frozenset([norm_ref(inner)]))
        return ("COMPUTED_FROM", bases)
    return (k,)


def norm_mine(lab):
    k = lab[0]
    if k == "CONST": return ("CONST",)
    if k in ("COMPUTED", "COMPUTED_FROM"): return (k, frozenset(b for b in lab[1] if b[0] != "CONST"))
    return lab


def nset_ref(s): return frozenset(norm_ref(b) for b in s)


def nset_mine(s): return frozenset(b for b in s if b[0] != "CONST")


def compare(R, m, inputs, occupied=True):
    V = T.vm16()
    _, mine, _ = T.trace(m, L, 256, inputs, occupied=occupied)
    res = R.trace_interaction(bytes(m), list(inputs), R.Cfg(), occupant=occupied)
    diffs = Counter(); ex = []
    for loc in res.loci:
        i = loc.locus; r = mine[i]
        checks = {"written": loc.written == r["written"], "data": norm_ref(loc.label) == norm_mine(r["data"])}
        if loc.written and r["written"]:
            checks["addr"] = nset_ref(loc.addr_deps) == nset_mine(r["addr"])
            checks["ctrl_at_store"] = nset_ref(loc.ctrl_deps_at_store or frozenset()) == nset_mine(r["ctrl"])
            checks["exec_at_store"] = nset_ref(loc.exec_deps_at_store or frozenset()) == nset_mine(r["exec"])
            pr = frozenset([{"w": "W", "o": "P"}[loc.performer[1]]]) if loc.performer and loc.performer[0] == "ENTITY" else frozenset()
            checks["performer"] = pr == frozenset(b[1] for b in r["performer"])
        for k, ok in checks.items():
            diffs[(k, ok)] += 1
            if not ok and len(ex) < 3: ex.append((i, k, loc.label, r["data"]))
    return diffs, ex


def main(a):
    R = load_ref(); rng = random.Random(11); V = T.vm16()
    fz = int(a[a.index("--fuzz") + 1]) if "--fuzz" in a else 300
    nr = int(a[a.index("--replicators") + 1]) if "--replicators" in a else 200
    total = Counter(); examples = {}
    for name, (m, x, _) in F.fixtures().items():
        d, ex = compare(R, m, x); total.update(d)
        if ex: examples[name] = ex
    for n in range(fz):
        m = bytearray(256); m[:2 * L] = bytes(rng.randrange(256) for _ in range(2 * L)); x = rng.randrange(256); m[V.IN_BASE] = x
        d, ex = compare(R, m, [x]); total.update(d)
        if ex and len(examples) < 12: examples["fuzz%d" % n] = ex
    for n in range(nr):
        base = V.replicator_copyall(L) if n % 2 else V.replicator(L)
        t = bytearray(base + bytes(rng.randrange(256) for _ in range(L - len(base))))
        for _ in range(rng.randrange(4)): t[rng.randrange(L)] = rng.randrange(256)
        m = bytearray(256); m[:L] = t; m[L:2 * L] = bytes(rng.randrange(256) for _ in range(L)); x = rng.randrange(256); m[V.IN_BASE] = x
        d, ex = compare(R, m, [x]); total.update(d)
        if ex and len(examples) < 16: examples["rep%d" % n] = ex
    fields = sorted({k for k, _ in total})
    print("field agreement (loci):")
    for f in fields:
        ok, bad = total[(f, True)], total[(f, False)]
        print("  %-14s %6d / %6d  = %.4f" % (f, ok, ok + bad, ok / (ok + bad)))
    print("examples of disagreement:")
    for k, v in list(examples.items())[:16]: print(" ", k, v)


if __name__ == "__main__":
    main(sys.argv[1:])
