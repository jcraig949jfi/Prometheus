"""TFS-1 known-answer tests. Run from roles/Aphrodite/beta04:   python -m tfs1.tests.run_tests [--quick]

Writes tfs1/TFS1_TEST_RESULTS.json (numbers for every test) and exits non-zero on any FAIL.
"""
import hashlib
import json
import os
import random
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")

from tfs1 import core as C                                  # noqa: E402
from tfs1 import compress as K                              # noqa: E402
from tfs1 import membrane as M                              # noqa: E402
from tfs1.enum import Enumerator, canon_comm, make_verifier  # noqa: E402
from tfs1.library import Library                            # noqa: E402
from tfs1.mutate import Mutator, mutation_search, rng_for   # noqa: E402

QUICK = "--quick" in sys.argv
HERE = Path(__file__).resolve().parent.parent
RESULTS = {}


def P(s):
    return C.parse(s)


TESTS = []


def test(fn):
    """Register only (importing this module must never run tests: subprocess fixtures import it)."""
    TESTS.append(fn)
    return fn


def _run(fn):
    name = fn.__name__
    t0 = time.perf_counter()
    try:
        info = fn() or {}
        status = "PASS"
    except Exception as e:                    # noqa: BLE001
        info = {"error": repr(e), "trace": traceback.format_exc()[-1500:]}
        status = "FAIL"
    info["status"] = status
    info["seconds"] = round(time.perf_counter() - t0, 2)
    RESULTS[name] = info
    print("%-40s %s  %s" % (name, status, {k: v for k, v in info.items() if k not in ("trace",)}))
    return fn


def check(cond, msg="check failed"):
    if not cond:
        raise AssertionError(msg)


# ================================================================ interpreter guards
GUARDS = [
    # (program, input, expected)   FAIL = C.FAIL
    ("(div 7 2)", [], 3), ("(div (neg 7) 2)", [], -4), ("(div 7 0)", [], C.FAIL), ("(div 0 0)", [], C.FAIL),
    ("(mod 7 3)", [], 1), ("(mod (neg 7) 3)", [], 2), ("(mod 7 (neg 3))", [], -2), ("(mod 7 0)", [], C.FAIL),
    ("(gcd (neg 12) 18)", [], 6), ("(gcd 0 0)", [], 0), ("(gcd 0 (neg 5))", [], 5),
    ("(pow 2 3)", [], 8), ("(pow 2 (neg 1))", [], 0), ("(pow 2 33)", [], 0), ("(pow 2 32)", [], 2 ** 32),
    ("(pow 0 0)", [], 1), ("(pow (neg 2) 3)", [], -8),
    ("(pow 10 18)", [], 10 ** 18), ("(pow 10 19)", [], C.FAIL), ("(neg (pow 10 18))", [], -10 ** 18),
    ("(add (pow 10 18) 1)", [], C.FAIL), ("(sub (neg (pow 10 18)) 1)", [], C.FAIL),
    ("(mul (pow 10 9) (pow 10 9))", [], 10 ** 18), ("(mul (pow 10 9) (mul (pow 10 9) 2))", [], C.FAIL),
    ("(pow 3 32)", [], 3 ** 32), ("(pow 4 32)", [], C.FAIL),
    ("(lt 1 2)", [], True), ("(eq 2 2)", [], True), ("(gt 1 2)", [], False),
    ("(and (lt 1 2) (gt 1 2))", [], False), ("(or (lt 1 2) (gt 1 2))", [], True), ("(not (lt 1 2))", [], False),
    ("(if (lt 1 2) 3 0)", [], 3), ("(if (gt 1 2) 3 0)", [], 0),
    ("(if (lt 1 2) 3 (div 1 0))", [], C.FAIL),                       # strict: untaken branch FAILs
    ("(and (gt 1 2) (eq (div 1 0) 1))", [], C.FAIL),                 # strict and
    ("(len xs)", [], 0), ("(len xs)", [4, 5], 2),
    ("(head xs)", [], C.FAIL), ("(last xs)", [], C.FAIL), ("(max xs)", [], C.FAIL), ("(min xs)", [], C.FAIL),
    ("(sum xs)", [], 0), ("(head xs)", [4, 5], 4), ("(last xs)", [4, 5], 5), ("(max xs)", [4, 9, 5], 9),
    ("(min xs)", [4, 9, -5], -5), ("(sum xs)", [4, 9, -5], 8),
    ("(rev xs)", [1, 2, 3], [3, 2, 1]), ("(rev xs)", [], []),
    ("(take 2 xs)", [1, 2, 3], [1, 2]), ("(take (neg 1) xs)", [1, 2, 3], []), ("(take 9 xs)", [1, 2, 3], [1, 2, 3]),
    ("(drop 2 xs)", [1, 2, 3], [3]), ("(drop (neg 1) xs)", [1, 2, 3], [1, 2, 3]), ("(drop 9 xs)", [1, 2, 3], []),
    ("(map (lam x (mul x 2)) xs)", [1, 2], [2, 4]), ("(map (lam x (div 1 x)) xs)", [1, 0], C.FAIL),
    ("(map (lam x (div 1 x)) xs)", [], []),
    ("(filter (lam x (gt x 1)) xs)", [1, 2, 3], [2, 3]),
    ("(foldl (lam a (lam b (sub a b))) 0 xs)", [1, 2, 3], -6),         # ((0-1)-2)-3: a = acc, b = element
    ("(foldl (lam a (lam b (add (mul a 10) b))) 0 xs)", [1, 2, 3], 123),
    ("(scanl (lam a (lam b (add a b))) 0 xs)", [1, 2, 3], [0, 1, 3, 6]),
    ("(scanl (lam a (lam b (add a b))) 5 xs)", [], [5]),
    ("(zipw (lam a (lam b (sub a b))) xs (rev xs))", [1, 2, 5], [-4, 0, 4]),
    ("(zipw (lam a (lam b (add a b))) xs (drop 1 xs))", [1, 2, 5], [3, 7]),   # truncating
    ("(app (lam x (add x 1)) 4)", [], 5), ("(app (lam a (lam b (sub a b))) 4 1)", [], 3),
    ("(sum (map (lam x (pow 10 17)) xs))", [1] * 11, C.FAIL),          # sum output over the ceiling
    ("(map (lam x (sum (map (lam y (mul x y)) xs))) xs)", [1, 2], [3, 6]),   # nested scopes
    ("(map (lam x (head (map (lam y (sub y x)) xs))) xs)", [1, 5], [0, -4]),   # inner y, outer x
    ("(map (lam x (head (map (lam x (add x 1)) xs))) xs)", [1, 5], [2, 2]),   # shadowing: inner x
]


@test
def test_interpreter_guards():
    bad = []
    for src, inp, want in GUARDS:
        t = P(src)
        C.type_of(t)
        got = C.evaluate(t, inp)[0]
        if not (got == want and (got == C.FAIL or type(got) is type(want))):
            bad.append((src, inp, want, got))
    check(not bad, "guard mismatches: %r" % bad)
    return {"cases": len(GUARDS), "mismatches": 0}


@test
def test_units_known_answers():
    cases = [("(sum (map (lam x (mul x x)) xs))", [1, 2, 3], 5, 5),
             ("(if (lt (head xs) 2) 1 (div 3 0))", [1, 2, 3], 3, 3),        # FAIL after 3 units (left-to-right)
             ("(foldl (lam a (lam b (add a b))) 0 xs)", [1, 2, 3, 4], 5, 5),
             ("(len xs)", [], 1, 1), ("3", [], 0, 0), ("xs", [1], 0, 0)]
    for src, inp, ue, up in cases:
        v, e, p = C.evaluate(P(src), inp)
        check((e, p) == (ue, up), "units %s: got %s" % (src, (e, p)))
    # promoted ledger: caller lambdas and argument expressions are caller code
    lib = Library()
    m, _ = lib.promote_body(P("(sum (map h0 h1))"))
    v, e, p = C.evaluate(P("(%s (lam x (mul x x)) (rev xs))" % m.id), [1, 2, 3], lib)
    check((v, e, p) == (14, 6, 5), "M(f,l): %r" % ((v, e, p),))   # exp: sum+map+rev+3 mul; prom: call+rev+3 mul
    a, _ = lib.promote_lambda(P("(lam x (add (mul x x) 1))"))
    v, e, p = C.evaluate(P("(%s (%s (head xs)))" % (a.id, a.id)), [2], lib)
    # inner call arg (head xs) is forced twice by the inner body and the inner call itself is forced twice by the
    # outer body (call-by-name == expansion): expanded = 2*(head) ... counted exactly as the expansion
    e2 = C.evaluate(lib.expand(P("(%s (%s (head xs)))" % (a.id, a.id))), [2])
    check((v, e) == (e2[0], e2[1]), "nested CBN units %r vs %r" % ((v, e), e2))
    check(p == 1 + 2 * (1 + 2), "promoted units %d" % p)   # outer call 1; inner call evaluated twice, each 1 + 2 heads
    return {"cases": len(cases) + 2}


@test
def test_parse_print_roundtrip_and_types():
    E = Enumerator()
    rng = random.Random(7)
    n = 0
    for T in C.VALUE_TYPES:
        for sz in range(1, 7):
            lst = E.terms(T, (), sz)
            for _ in range(min(len(lst), 400)):
                t, s = lst[rng.randrange(len(lst))]
                check(C.to_str(t) == s, "table text mismatch")
                check(P(s) == t, "roundtrip %s" % s)
                check(C.type_of(t) == T, "type %s" % s)
                n += 1
    bad = ["(add xs 1)", "(map (lam x (lt x 1)) xs)", "(filter (lam x (add x 1)) xs)", "(foldl (lam x (add x 1)) 0 xs)",
           "(if 1 2 3)", "(head 3)", "(map xs xs)", "(add (lam x x) 1)", "(sum xs xs)",
           "(zipw (lam a (lam b (lt a b))) xs xs)", "(app (lam x x) xs)", "(foo 1)"]
    rej = 0
    for s in bad:
        try:
            C.type_of(P(s))
        except (C.TypeErr, ValueError, KeyError):
            rej += 1
    check(rej == len(bad), "ill-typed accepted: %d/%d rejected" % (rej, len(bad)))
    check(P("(lam a b (add a b))") == P("(lam a (lam b (add a b)))"), "binary lambda sugar")
    return {"roundtrips": n, "ill_typed_rejected": rej}


# ================================================================ promotion semantics
def _random_library(seed=0):
    lib = Library()
    rng = random.Random(seed)
    a, _ = lib.promote_lambda(P("(lam x (add (mul x x) 1))"), {"kat": "A"})
    b, _ = lib.promote_lambda(P("(lam a (lam b (sub (mul a 2) b)))"), {"kat": "B"})
    c, _ = lib.promote_body(P("(sum (map h0 h1))"), None, {"kat": "C fn-param"})
    d, _ = lib.promote_body(P("(%s (lam x (%s x)) (filter (lam x (gt x h0)) xs))" % (c.id, a.id)), None,
                            {"kat": "D depth2 uses C, A, param under lambda"})
    e, _ = lib.promote_body(P("(div (head h0) (len h0))"), None, {"kat": "E partial"})
    f, _ = lib.promote_body(P("(%s (%s h0 3) (%s (map (lam x (%s x h0)) xs)))" % (b.id, b.id, e.id, b.id)), None,
                            {"kat": "F depth2, param used twice"})
    g, _ = lib.promote_lambda(P("(lam a (lam b (mul a 3)))"), {"kat": "G unused param"})
    h, _ = lib.promote_term(P("(foldl (lam a (lam b (%s a b))) (%s 0) xs)" % (g.id, a.id)), {"kat": "H arity0 xs"})
    i, _ = lib.promote_body(P("(%s (%s (scanl (lam a (lam b (add a b))) 0 h0)) (%s (len h0)))" % (b.id, e.id, f.id)),
                            None, {"kat": "I depth3"})
    j, _ = lib.promote_body(P("(if (lt h0 0) (%s h0) (%s (take h0 xs)))" % (a.id, e.id)), None,
                            {"kat": "J strict if over entries"})
    return lib


@test
def test_promotion_semantics_random():
    lib = _random_library()
    check(lib.max_depth() == 3, "library depth %d" % lib.max_depth())
    E = Enumerator(lib)
    mut = Mutator(E, max_fill=4, max_size=14)
    rng = random.Random(12345)
    n_cases = 3000 if QUICK else 12000
    mism, fails, with_calls, cases = [], 0, 0, 0
    progs = []
    while len(progs) < (n_cases // 4):
        T = rng.choice(C.VALUE_TYPES)
        t = mut.random_term(T, (), rng, max_n=5)
        if t is None:
            continue
        for _ in range(rng.randrange(3)):
            t2 = mut.mutate(t, T, rng)
            t = t2 or t
        if not C.has_call(t) and rng.random() < 0.8:
            continue
        progs.append((t, T))
    for t, T in progs:
        check(C.type_of(t, 0, None, lib) == T, "ill-typed random program")
        exp = lib.expand(t)
        check(not C.has_call(exp), "expansion still has calls")
        C.type_of(exp)
        fd = C.compile_term(t, lib, None, swap=True)
        fe = C.compile_term(exp, None, None, swap=False)
        with_calls += C.has_call(t)
        for _ in range(4):
            L = rng.randrange(0, 7)
            pool = [rng.randint(-6, 9) for _ in range(L)]
            if rng.random() < 0.1 and L:
                pool[rng.randrange(L)] = rng.choice([10 ** 17, -10 ** 17, 10 ** 9])
            C.U[0] = C.U[1] = 0
            vd = C.run(fd, list(pool))
            ud = C.U[0]
            C.U[0] = C.U[1] = 0
            ve = C.run(fe, list(pool))
            ue, up = C.U[0], C.U[1]
            cases += 1
            fails += vd == C.FAIL
            if not (C.same_value(vd, ve) and ud == ue and ue == up):
                mism.append((C.to_str(t), pool, vd, ve, ud, ue))
    check(not mism, "%d mismatches, first %r" % (len(mism), mism[:2]))
    return {"cases": cases, "programs": len(progs), "programs_with_calls": with_calls, "fail_cases": fails,
            "mismatches_value_or_FAIL": 0, "mismatches_expanded_units": 0, "library_entries": len(lib),
            "library_max_depth": lib.max_depth()}


# ================================================================ serialization / transplant
@test
def test_serialization_roundtrip_and_tamper():
    lib = _random_library()
    s = lib.dumps()
    lib2 = Library.loads(s)
    check(lib2.dumps() == s, "roundtrip not byte-identical")
    # a different insertion order gives the same bytes
    obj = json.loads(s)
    obj2 = dict(obj, entries=list(reversed(obj["entries"])))
    check(Library.from_json(obj2).dumps() == s, "order-dependent serialization")
    tampered = 0
    # (1) edit a body without fixing the hash
    o = json.loads(s)
    o["entries"][0]["body"] = "(add h0 1)" if o["entries"][0]["body"] != "(add h0 1)" else "(add h0 2)"
    try:
        Library.from_json(o)
    except ValueError:
        tampered += 1
    # (2) edit the depth AND recompute the hash -> must fail re-derivation
    o = json.loads(s)
    r = o["entries"][-1]
    r["depth"] = 1
    r["hash"] = M.sha({k: r[k] for k in r if k != "hash"})
    try:
        Library.from_json(o)
    except ValueError:
        tampered += 1
    # (3) missing dependency
    o = json.loads(s)
    o["entries"] = [e for e in o["entries"] if e["depth"] > 1]
    try:
        Library.from_json(o)
    except KeyError:
        tampered += 1
    check(tampered == 3, "tamper detection %d/3" % tampered)
    # fresh-process determinism of the serialized bytes
    code = ("import sys; sys.path.insert(0, %r); from tfs1.tests.run_tests import _random_library;"
            "import hashlib; print(hashlib.sha256(_random_library().dumps().encode()).hexdigest())") % str(HERE.parent)
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, timeout=120)
    check(out.stdout.strip() == lib.sha256(), "fresh-process library sha differs: %r" % out.stderr[-500:])
    return {"entries": len(lib), "library_sha256": lib.sha256(), "tamper_cases_detected": tampered,
            "fresh_process_sha_equal": True}


def _toy_tasks():
    rng = random.Random(99)

    def mk(fid, fn, T="Int"):
        def ins(k):
            return [[rng.randint(-4, 9) for _ in range(rng.randint(1, 6))] for _ in range(k)]
        return {"family_id": fid, "output_type": T, "dev": [[i, fn(i)] for i in ins(8)],
                "test": [[i, fn(i)] for i in ins(32)]}
    return [mk("sumsq1", lambda l: sum(v * v + 1 for v in l)), mk("len", lambda l: len(l)),
            mk("maxp1", lambda l: max(l) + 1), mk("rev", lambda l: l[::-1], "List")]


@test
def test_transplant_no_donor_state():
    lib = _random_library()
    tasks = _toy_tasks()
    supply = {"budget": 3000, "max_size": 6, "seed": 5, "tasks": tasks}
    with tempfile.TemporaryDirectory() as td:
        res = M.transplant(lib, supply, td, tag="kat")
    v = res["verification"]
    check(v["NO_DONOR_STATE"], "receipt verification: %r" % v)
    local = M.run_tasks(Library.loads(lib.dumps()), supply)
    check(local == res["receipt"]["results"], "recipient results differ from in-process results")
    return {"verification": v, "library_sha256": res["library_sha256"], "tasks_sha256": res["tasks_sha256"],
            "recipient_pid": res["receipt"]["pid"], "results": [(r["family_id"], r["hit"], r["hit_charge"])
                                                               for r in res["receipt"]["results"]]}


# ================================================================ alias collapse / depth
@test
def test_alias_collapse_and_depth():
    lib = Library()
    a, st = lib.promote_lambda(P("(lam x (add (mul x x) 1))"))
    check(a.depth == 1 and st == "new", "A depth")
    out = {}
    # O1 defect case: P_x({H}) must map to P_x at depth 1 (no new id)
    x, st = lib.promote_body(P("(%s h0)" % a.id))
    check(x.id == a.id and st == "collapsed" and x.depth == 1, "eta alias not collapsed")
    out["eta_alias"] = st
    # re-spelling in base of an existing entry
    x, st = lib.promote_body(P("(add (mul h0 h0) 1)"))
    check(x.id == a.id and st == "collapsed", "re-spelling not collapsed")
    out["respelling"] = st
    # commuted spelling is a different term (no semantic equivalence check: documented limitation)
    x, st = lib.promote_body(P("(add 1 (mul h0 h0))"))
    out["commuted_respelling_status"] = st
    # genuine composition
    b, st = lib.promote_body(P("(sum (map (lam x (%s (%s x))) h0))" % (a.id, a.id)))
    check(b.depth == 2 and b.deps == [a.id] and b.lineage == [a.id], "composition depth")
    # A2 re-expression: entry applied to atoms only -> keeps callee depth
    c, st = lib.promote_body(P("(%s xs)" % b.id))
    check(st == "new" and c.alias_of == b.id and c.depth == 2, "A2 depth %d" % c.depth)
    c2, st2 = lib.promote_body(P("(%s 3)" % a.id))
    check(c2.alias_of == a.id and c2.depth == 1, "A2 constant arg")
    # composition of two entries IS a new level
    d, st = lib.promote_body(P("(%s (%s h0))" % (a.id, a.id)))
    check(d.depth == 2 and d.alias_of is None, "entry-over-entry composition depth")
    # depth-3 chain and lineage
    e, st = lib.promote_body(P("(add (%s h0) 1)" % d.id))
    check(e.depth == 3 and e.lineage == sorted({a.id, d.id}), "depth 3 lineage")
    # trivial bodies rejected
    rej = 0
    for s in ("h0", "3", "xs"):
        try:
            lib.promote_body(P(s))
        except ValueError:
            rej += 1
    check(rej == 3, "trivial bodies")
    # ids are content-addressed: provenance does not change the id, a fresh library gives the same id
    lib2 = Library()
    a2, _ = lib2.promote_lambda(P("(lam x (add (mul x x) 1))"), {"arm": "other"})
    check(a2.id == a.id and a2.hash != a.hash, "content addressing")
    out.update({"composition_depth": b.depth, "A2_depth": c.depth, "chain_depth": e.depth, "trivial_rejected": rej})
    return out


# ================================================================ enumerator
@test
def test_count_equals_materialised():
    E = Enumerator(_random_library())
    n = 0
    for T in C.VALUE_TYPES:
        for ctx in ((), ("x",), ("a", "b"), ("x", "a", "b")):
            for sz in range(1, 6 if QUICK else 7):
                check(E.count(T, ctx, sz) == len(E.terms(T, ctx, sz)), "count %s %s %d" % (T, ctx, sz))
                n += 1
    E0 = Enumerator()
    return {"classes_checked": n, "base_Int_class_sizes": [E0.count("Int", (), k) for k in range(1, 10)],
            "base_List_class_sizes": [E0.count("List", (), k) for k in range(1, 10)]}


@test
def test_chunked_keyed_order_equals_full_sort():
    E = Enumerator()
    full = E.keyed_class("Int", 6, 3, "s")
    chunked = list(E.keyed_iter("Int", 6, 3, "s", chunk=7000))
    check([t for _k, t in full] == [t for _k, t in chunked], "chunked order differs")
    lim = list(E.keyed_iter("Int", 6, 3, "s", limit=20000, chunk=7000))
    check([t for _k, t in lim] == [t for _k, t in full[:20000]], "limited chunked order differs")
    keys = [k for k, _t in full]
    check(keys == sorted(keys), "not ascending")
    return {"class_size": len(full)}


def _trace(lib, seed, slot, budget, max_size=5, T="Int"):
    E = Enumerator(lib)
    tr = []
    ex = [([1, 2, 3], -999999)]                      # unreachable target: walk the full budget
    E.search(ex, T, seed, slot, budget, max_size, trace=tr)
    return [s for _c, s in tr]


@test
def test_enumerator_determinism_and_crn():
    lib = _random_library()
    budget = E_budget = 8000
    t1 = _trace(lib, 1, "fam", budget)
    t2 = _trace(Library.loads(lib.dumps()), 1, "fam", budget)
    check(t1 == t2, "same seed/slot/library -> different sequence")
    # entry insertion order permutation
    obj = json.loads(lib.dumps())
    obj["entries"] = list(reversed(obj["entries"]))
    t3 = _trace(Library.from_json(obj), 1, "fam", budget)
    check(t1 == t3, "entry permutation changed the walk")
    t4 = _trace(lib, 2, "fam", budget)
    check(t1 != t4, "different seed gave the same walk")
    # fresh process
    code = ("import sys; sys.path.insert(0, %r); from tfs1.tests.run_tests import _trace, _random_library;"
            "import hashlib; print(hashlib.sha256('\\n'.join(_trace(_random_library(), 1, 'fam', %d)).encode())"
            ".hexdigest())") % (str(HERE.parent), budget)
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, timeout=300)
    h1 = hashlib.sha256("\n".join(t1).encode()).hexdigest()
    check(out.stdout.strip() == h1, "fresh process walk differs %r" % out.stderr[-300:])
    # shared terms keep relative order: walk complete classes 1..5 with and without the library
    E0, E1 = Enumerator(), Enumerator(lib)
    b0, b1 = E0.cumulative("Int", 5), E1.cumulative("Int", 5)
    w0 = _trace(None, 1, "fam", b0)
    w1 = _trace(lib, 1, "fam", b1)
    base_in_w1 = [s for s in w1 if "L_" not in s]
    check(base_in_w1 == w0, "shared base terms changed relative order")
    return {"walk_sha256": h1, "budget": budget, "fresh_process_equal": True, "permutation_invariant": True,
            "base_walk_len": len(w0), "library_walk_len": len(w1), "shared_order_preserved": True}


@test
def test_cost_ledger_exact():
    lib = _random_library()
    E = Enumerator(lib)
    rng = random.Random(3)
    ins = [[rng.randint(-3, 8) for _ in range(rng.randint(1, 5))] for _ in range(8)]
    a_id = [e.id for e in lib.entries.values() if e.provenance.get("kat") == "A"][0]
    a = lib.entries[a_id]
    want = lambda l: sum(v * v + 1 for v in l)           # noqa: E731
    dev = [(i, want(i)) for i in ins]
    tr = []
    r = E.search(dev, "Int", 11, "ledger", 200000, 7, trace=tr)
    check(r["hit"], "no hit")
    check(r["charges"] == len(tr) == r["hit_charge"], "charges != evaluated candidates")
    rank = E.rank_of(P(r["program"]), "Int", 11, "ledger")
    check(rank == r["hit_charge"], "static rank %s != hitting charge %s" % (rank, r["hit_charge"]))
    # independent recomputation of both unit ledgers over the trace (early exit, same order)
    ue = up = 0
    for _c, s in tr:
        t = P(s)
        fn = C.compile_term(t, lib, None, swap=True)
        C.U[0] = C.U[1] = 0
        C.check_dev(fn, [(list(i), o) for i, o in dev])
        ue += C.U[0]
        up += C.U[1]
    check((ue, up) == (r["units_expanded"], r["units_promoted"]), "unit ledgers %r vs %r" %
          ((ue, up), (r["units_expanded"], r["units_promoted"])))
    # exhaustive miss: charges == cumulative class sizes exactly
    r2 = E.search([([1], 10 ** 9 + 7)], "Int", 11, "ledger", 10 ** 7, 4)
    check(r2["charges"] == E.cumulative("Int", 4) and r2["complete_through_size"] == 4, "exhaustive count")
    return {"hit_program": r["program"], "hit_charge": r["hit_charge"], "static_rank": rank,
            "units_expanded": ue, "units_promoted": up, "exhaustive_through_4_charges": r2["charges"],
            "uses_entry": a_id in r["program"]}


# ================================================================ mutator
@test
def test_mutator_typed_and_deterministic():
    lib = _random_library()
    E = Enumerator(lib)
    mut = Mutator(E, max_fill=3, max_size=14)
    rng = random.Random(5)
    n = bad = 0
    ops_seen = set()
    for _ in range(600 if QUICK else 3000):
        T = rng.choice(C.VALUE_TYPES)
        t = mut.random_term(T, (), rng, 5)
        c = mut.mutate(t, T, rng)
        if c is None:
            continue
        n += 1
        try:
            if C.type_of(c, 0, None, lib) != T:
                bad += 1
        except C.TypeErr:
            bad += 1
        check(C.size(c) <= 14, "oversize child")
    check(bad == 0, "%d ill-typed children" % bad)

    def seq(seed):
        r = rng_for(seed, "slot")
        t = P("(sum xs)")
        out = []
        for _ in range(300):
            c = mut.mutate(t, "Int", r)
            out.append(C.to_str(c))
            t = c
        return out
    check(seq(4) == seq(4) and seq(4) != seq(5), "mutation determinism")
    tasks = _toy_tasks()
    r1 = mutation_search(tasks[0]["dev"], "Int", ["(sum xs)"], 3000, 4, "sumsq1", E, policy="random",
                         full_outputs=True)
    r2 = mutation_search(tasks[0]["dev"], "Int", ["(sum xs)"], 3000, 4, "sumsq1", Enumerator(Library.loads(lib.dumps())),
                         policy="random", full_outputs=True)
    check(r1 == r2, "mutation_search not deterministic")
    return {"children_checked": n, "ill_typed": bad, "walk_hit": r1["hit"], "walk_charges": r1["charges"],
            "walk_program": r1["program"]}


# ================================================================ compressor
@test
def test_compressor_planted_kat():
    # planted corpus: 4 expanded programs S_b(S_a(x_i)) with S_a(v) = v*v + 1 and S_b(u) = sum(map(lam x (mul 3 u)) ..)
    lib = Library()
    sa, _ = lib.promote_lambda(P("(lam x (add (mul x x) 1))"), {"kat": "S_a"})
    corpus = ["(sum (map (lam x (mul 3 (add (mul x x) 1))) xs))",
              "(sum (map (lam x (mul 3 (add (mul x x) 1))) (rev xs)))",
              "(sum (map (lam x (mul 3 (add (mul x x) 1))) (drop 1 xs)))",
              "(sum (map (lam x (mul 3 (add (mul x x) 1))) (take 3 xs)))"]
    c1 = K.propose(corpus, lib)
    c1b = K.propose(list(reversed(corpus)), lib)          # before the library changes below
    top = c1[0]
    e, st = lib.promote_body(top["body_t"], top["params"], {"kat": "compressed"})
    check(sa.id in top["body"] and e.depth == 2 and e.deps == [sa.id], "with library: %r depth %d" %
          (top["body"], e.depth))
    c0 = K.propose(corpus, Library())
    lib0 = Library()
    e0, _ = lib0.promote_body(c0[0]["body_t"], c0[0]["params"])
    check(e0.depth == 1, "without library depth %d" % e0.depth)
    check(lib.expand(e.body_t) == lib0.expand(e0.body_t), "same mechanism at depth 2 vs depth 1")
    # planted alias corpus: programs that are bare re-expressions of S_a must not produce an alias candidate
    alias_corpus = ["(%s (head xs))" % sa.id, "(%s (last xs))" % sa.id, "(%s (len xs))" % sa.id]
    ca = K.propose(alias_corpus, lib)
    check(all(not (c["body_t"][0] == sa.id and all(a[0] in ("hole", "int", "xs") for a in c["body_t"][1:]))
              for c in ca), "alias candidate proposed")
    # determinism under corpus permutation
    check([c["body"] for c in c1] == [c["body"] for c in c1b], "corpus order changed candidates")
    return {"top_with_library": top["body"], "gain": top["gain"], "uses": top["uses"], "depth_with_library": e.depth,
            "top_without_library": c0[0]["body"], "depth_without_library": e0.depth,
            "alias_candidates": len([c for c in ca if c["body_t"][0] == sa.id])}


@test
def test_compressor_function_hole():
    corpus = ["(sum (map (lam x (add x 1)) (filter (lam x (gt x 0)) xs)))",
              "(sum (map (lam x (mul x x)) (filter (lam x (gt x 0)) xs)))",
              "(sum (map (lam x (sub 0 x)) (filter (lam x (gt x 0)) xs)))"]
    c = K.propose(corpus, Library())
    fn_hole = [x for x in c if "Int->Int" in x["params"]]
    check(fn_hole, "no function-typed hole candidate: %r" % [x["body"] for x in c])
    lib = Library()
    e, _ = lib.promote_body(fn_hole[0]["body_t"], fn_hole[0]["params"])
    prog = P("(%s (lam x (mul x 3)))" % e.id) if e.params == ["Int->Int"] else None
    check(prog is not None, "params %r" % e.params)
    v1 = C.evaluate(prog, [1, -2, 4], lib)
    v2 = C.evaluate(lib.expand(prog), [1, -2, 4])
    check(v1[0] == 15 and v1[:2] == v2[:2], "fn-hole entry semantics %r %r" % (v1, v2))
    return {"candidate": fn_hole[0]["body"], "params": fn_hole[0]["params"], "gain": fn_hole[0]["gain"]}


# ================================================================ statistics
@test
def test_flip_test_known_values():
    r = M.flip_test([1] * 10)
    check(abs(r["p_one_sided"] - 1 / 1024) < 1e-6 and r["attainable_min_p"] == round(1 / 1024, 8), "all-positive")
    r = M.flip_test([3, -1, 2, 0])
    check(r["p_one_sided"] == 0.25 and r["p_two_sided"] == 0.5 and r["nonzero"] == 3, "small exact %r" % r)
    lib = _random_library()
    tasks = _toy_tasks()
    a = M.hitting_costs(None, tasks, 4000, 0, 6)
    b = M.hitting_costs(lib, tasks, 4000, 0, 6)
    res = M.paired_crn(a, b)
    return {"flip_all_pos_p": 1 / 1024, "paired_example": {k: res[k] for k in ("diffs", "p_one_sided",
                                                                               "hits_control", "hits_treatment")}}


if __name__ == "__main__":
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    for fn in TESTS:
        if not only or fn.__name__ in only:
            _run(fn)
    out = HERE / ("TFS1_TEST_RESULTS%s.json" % ("_PARTIAL" if only else ("_QUICK" if QUICK else "")))
    summary = {"pass": sum(r["status"] == "PASS" for r in RESULTS.values()),
               "fail": sum(r["status"] == "FAIL" for r in RESULTS.values()),
               "python": sys.version.split()[0], "quick": QUICK,
               "code_sha256": M.code_hashes()}
    out.write_text(json.dumps({"summary": summary, "tests": RESULTS}, indent=1, sort_keys=True, default=str))
    print(summary["pass"], "PASS", summary["fail"], "FAIL ->", out)
    sys.exit(1 if summary["fail"] else 0)
