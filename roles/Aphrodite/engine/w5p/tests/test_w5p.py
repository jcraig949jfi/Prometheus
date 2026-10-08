"""W5P test suite. Run from roles/Aphrodite/engine:

    OMP_NUM_THREADS=1 python -m pytest w5p/tests/test_w5p.py -q            (fast tests)
    OMP_NUM_THREADS=1 W5P_SLOW=1 python -m pytest w5p/tests/test_w5p.py -q (+ donor-level NO-OP / smoke, ~20 min)
    OMP_NUM_THREADS=1 python -m w5p.tests.test_w5p [--slow]                (writes w5p/W5P_TEST_RESULTS.json)

Single process throughout (no pools).
"""
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENG = HERE.parent.parent
if str(ENG) not in sys.path:
    sys.path.insert(0, str(ENG))

from w5p import _paths  # noqa: E402,F401
from w5p import harness as _H  # noqa: E402,F401  (FIRST: b02 -> t51_natural sets A18_TAG=T51 before a18 loads)
import basis_v4 as G  # noqa: E402
REF_RUN = G.run_program                 # the reference interpreter, captured before any fast path is installed
import identity as I  # noqa: E402
import engine as E  # noqa: E402
from w5p import promote as W  # noqa: E402

SLOW = os.environ.get("W5P_SLOW") == "1"
OPS = sorted(E.PRIMITIVES)              # add fdiv gcd mod mul powr sub
RESULTS = {}


def _fe():
    import fasteval as FE
    return FE


# ================================================================ random W5P material
def rand_term(rng, d, ids, p_prob=0.35):
    if d == 0 or rng.random() < 0.2:
        return ("var:" + rng.choice(["acc", "v", "first", "last"]), []) if rng.random() < 0.7 else \
            ("const:%d" % rng.choice([0, 1]), [])
    if ids and rng.random() < p_prob:
        return ("prim:" + rng.choice(ids), [rand_term(rng, d - 1, ids, p_prob)])
    op = rng.choice(OPS)
    return (op, [rand_term(rng, d - 1, ids, p_prob), rand_term(rng, d - 1, ids, p_prob)])


def _paths_of(t, p=()):
    out = []
    for i, a in enumerate(t[1]):
        out.append(p + (i,))
        out += _paths_of(a, p + (i,))
    return out


def _put_hole(t, path):
    if not path:
        return ("hole", [])
    op, args = t
    args = list(args)
    args[path[0]] = _put_hole(args[path[0]], path[1:])
    return (op, args)


def rand_schema(rng, ids, d=3):
    while True:
        t = rand_term(rng, d, ids, 0.5 if ids else 0.0)
        ps = _paths_of(t)
        if not ps:
            continue
        if ids and not W.prims_in(t):
            continue
        s = _put_hole(t, rng.choice(ps))
        if ids and not W.prims_in(s):
            continue
        return W.to_src(s)


GUARD_SCHEMAS = ["(acc // {H})", "({H} % last)", "pow(acc, {H})", "pow({H}, v)", "math.gcd(abs({H}), abs(acc))",
                 "(acc * {H})", "(v - (acc + {H}))", "(acc - {H})"]


def build_registry(seed="W5P/TEST/REG/v1", n1=12, n2=8, n3=4):
    rng = random.Random(seed)
    reg = {}
    for s in GUARD_SCHEMAS:
        W.register(reg, W.Promoted.from_schema(s, reg, W.sha(s), "test"))
    for _ in range(n1):
        s = rand_schema(rng, [])
        W.register(reg, W.Promoted.from_schema(s, reg, W.sha(s), "test"))
    for depth_level, n in ((1, n2), (2, n3)):
        ids = [p for p in sorted(reg) if reg[p].depth == depth_level]
        for _ in range(n):
            s = rand_schema(rng, ids)
            W.register(reg, W.Promoted.from_schema(s, reg, W.sha(s), "test"))
    return reg


def rand_inputs(rng):
    k = rng.randint(1, 10)
    out = []
    for _ in range(k):
        u = rng.random()
        out.append(0 if u < 0.08 else (10 ** rng.randint(6, 12) * rng.choice([1, -1]) if u < 0.14 else
                                         rng.randint(-3, 30)))
    return out


def rand_program(rng, ids, reg=None):
    """A fold whose body contains >= 1 promoted node. Bodies whose expansion nests pow more than twice are redrawn
    (run_program checks the ceiling only between steps, so pow(pow(pow(x, 32), 32), 32) on a large x is a
    multi-megabyte integer -- a test-time hazard, not a semantic case)."""
    while True:
        body = W.to_src(rand_term(rng, rng.randint(1, 4), ids))
        if not W.has_promoted(body):
            body = "%s(%s)" % (rng.choice(ids), body)
        if reg is None or W.expand(body, reg).count("pow(") <= 2:
            return ("fold", rng.choice(G.INIT_SPACE), body, rng.choice(G.FINAL_SPACE))


# ================================================================ tests
def test_parse_normalise_continuity():
    """On base DSL, promote.parse / normalise / to_src == identity.parse / normalise / to_src (all G4 bodies + inits +
    finals). This is what lets the zero-promotion path be byte-identical to W5."""
    srcs = list(dict.fromkeys(list(G.BODY_SPACE) + list(G.INIT_SPACE) + list(G.FINAL_SPACE)))
    bad = 0
    for s in srcs:
        a, b = W.parse(s), I.parse(s)
        bad += a != b
        bad += W.normalise(a) != I.normalise(b)
        bad += W.to_src(a) != I.to_src(b)
        bad += W.expand(s, {}) != s
    RESULTS["PARSE_NORMALISE_CONTINUITY"] = {"sources": len(srcs), "mismatches": bad, "PASS": bad == 0}
    assert bad == 0


def test_promotion_semantics():
    """promoted (call-by-value direct evaluator) == expansion under the reference interpreter == expansion under
    fasteval, on >= 10,000 random (program, input) cases with depth-1/2/3 promoted primitives and the guards."""
    FE = _fe()
    reg = build_registry()
    ids = sorted(reg)
    rng = random.Random("W5P/TEST/SEM/v1")
    n = mism = fails = 0
    examples = []
    boundary = [list(x) for x in I.B1_BOUNDARY[::100] if len(x) >= 1]
    for k in range(1600):
        prog = rand_program(rng, ids, reg)
        exp = W.expand_program(prog, reg)
        if W.has_promoted(exp[2]):
            raise AssertionError("expansion left a promoted node")
        inputs = [rand_inputs(rng) for _ in range(6)] + [rng.choice(boundary) for _ in range(2)]
        for x in inputs:
            for trailing in ((True,) if k % 5 else (True, False)):
                a = W.run_program_direct(prog, x, trailing, reg)
                b = REF_RUN(exp, x, trailing)
                c = FE.run_program(exp, x, trailing)
                n += 1
                fails += b is None
                if not (a == b == c and type(a) is type(b) is type(c)):
                    mism += 1
                    if len(examples) < 5:
                        examples.append([list(prog), x, repr(a), repr(b), repr(c)])
    # targeted guard cases: each must FAIL / clamp identically on both paths
    P = {s: W.Promoted.make_id(s, []) for s in GUARD_SCHEMAS}
    guard_cases = [
        (("fold", "0", "%s(v)" % P["(acc // {H})"], "acc"), [3, 0, 4, 9], "fdiv_by_zero -> None"),
        (("fold", "1", "%s(0)" % P["({H} % last)"], "acc"), [3, 5, 0], "mod_by_zero(last=0) -> None"),
        (("fold", "1", "%s(33)" % P["pow(acc, {H})"], "acc"), [3, 5, 7], "pow guard b>32 -> 0"),
        (("fold", "1", "%s(v)" % P["pow(acc, {H})"], "acc"), [2, -1, 7], "pow guard b<0 -> 0"),
        (("fold", "1", "%s(v)" % P["(acc * {H})"], "acc"), [10 ** 15, 10 ** 15, 10 ** 15, 1], "ceiling 1e40 -> None"),
        (("fold", "1", "%s(32)" % P["pow({H}, v)"], "acc"), [3, 32, 1], "pow(32,32)=2^160 > 1e40 -> None"),
    ]
    gmm, grow = 0, []
    for prog, x, label in guard_cases:
        a = W.run_program_direct(prog, x, True, reg)
        b = REF_RUN(W.expand_program(prog, reg), x, True)
        gmm += a != b
        grow.append({"case": label, "direct": repr(a), "expansion": repr(b)})
    RESULTS["PROMOTION_SEMANTICS"] = {"registry": len(reg), "depths": sorted({p.depth for p in reg.values()}),
                                      "cases": n, "mismatches": mism, "reference_fail_fraction": round(fails / n, 4),
                                      "guard_cases": grow, "guard_mismatches": gmm, "examples": examples,
                                      "PASS": n >= 10_000 and mism == 0 and gmm == 0}
    assert n >= 10_000 and mism == 0 and gmm == 0, examples


def test_serialization_roundtrip():
    reg = build_registry()
    bad = 0
    reg2 = W.load_records([p.to_json() for p in reg.values()][::-1])           # reversed: dependency resolution
    for pid, p in reg.items():
        j = p.to_json()
        s = p.dumps()
        q = W.Promoted.from_json(json.loads(s), reg2)
        bad += q.dumps() != s or q.to_json()["hash"] != j["hash"] or q.id != pid
        bad += W.Promoted.make_id(p.schema, p.deps) != pid                  # content-addressed id
        bad += W.Promoted.from_schema(p.schema, reg, p.source_artifact_sha256, p.source_kind).dumps() != s
    tamper = json.loads(next(iter(reg.values())).dumps())
    tamper["expansion"] = "(acc + {H})"
    try:
        W.Promoted.from_json(tamper, reg2)
        tamper_rejected = False
    except ValueError:
        tamper_rejected = True
    tamper2 = json.loads(next(iter(reg.values())).dumps())
    tamper2["expansion"] = "(acc + {H})"
    tamper2["hash"] = W.sha({k: tamper2[k] for k in W.Promoted.FIELDS})   # re-hashed forgery: re-derivation catches it
    try:
        W.Promoted.from_json(tamper2, reg2)
        rehash_rejected = False
    except ValueError:
        rehash_rejected = True
    RESULTS["SERIALIZATION"] = {"records": len(reg), "mismatches": bad, "tamper_rejected": tamper_rejected,
                                "rehashed_forgery_rejected": rehash_rejected,
                                "PASS": bad == 0 and tamper_rejected and rehash_rejected}
    assert bad == 0 and tamper_rejected and rehash_rejected


_CHILD = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
from w5p import promote as W
import basis_v4 as G
d = json.load(open(sys.argv[2]))
reg = W.load_records(d["records"])
out = {"hashes": {k: p.to_json()["hash"] for k, p in reg.items()}, "vals": []}
for prog, x in d["cases"]:
    prog = tuple(prog)
    out["vals"].append([repr(W.run_program_direct(prog, x, True, reg)),
                        repr(G.run_program(W.expand_program(prog, reg), x, True)), W.expand_program(prog, reg)[2]])
print(json.dumps(out))
'''


def test_transplant_fresh_process():
    """Serialized promoted primitives loaded in a FRESH interpreter evaluate identically (direct and by expansion),
    with identical record hashes and identical expansions."""
    reg = build_registry()
    ids = sorted(reg)
    rng = random.Random("W5P/TEST/TRANSPLANT/v1")
    cases = [(list(rand_program(rng, ids, reg)), rand_inputs(rng)) for _ in range(400)]
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "lib.json"
        f.write_text(json.dumps({"records": W.lineage_records(reg, ids), "cases": cases}))
        cf = Path(td) / "child.py"
        cf.write_text(_CHILD)
        env = dict(os.environ, OMP_NUM_THREADS="1")
        out = json.loads(subprocess.run([sys.executable, str(cf), str(ENG), str(f)], capture_output=True, text=True,
                                        check=True, env=env).stdout)
    here = [[repr(W.run_program_direct(tuple(p), x, True, reg)), repr(REF_RUN(W.expand_program(tuple(p), reg), x, True)),
             W.expand_program(tuple(p), reg)[2]] for p, x in cases]
    hb = sum(out["hashes"][k] != reg[k].to_json()["hash"] for k in reg)
    vb = sum(a != b for a, b in zip(here, out["vals"]))
    RESULTS["TRANSPLANT"] = {"records": len(reg), "cases": len(cases), "hash_mismatches": hb, "value_mismatches": vb,
                             "PASS": hb == 0 and vb == 0}
    assert hb == 0 and vb == 0


def test_dependency_depth_bookkeeping():
    """Constructed toy (bookkeeping only, not a result): P1 := (acc - {H}); two certified classes whose bodies contain
    P1 in a context; the W5P derivation yields a schema containing P1; promoting it records depth 2, deps [P1],
    lineage [P1]; a further derivation over bodies containing P2 records depth 3. Expansions evaluate equal."""
    from w5p import donor as D
    reg = {}
    p1 = W.register(reg, W.Promoted.from_schema("(acc - {H})", reg, W.sha("toy"), "toy"))
    classes = [["(first * (acc - v))"], ["(first * (acc - (v * v)))"], ["(acc * v)"]]
    der = W.derive_schemas(classes, reg)
    with_p = [d["schema"] for d in der if W.has_promoted(d["schema"])]
    plain = [d["schema"] for d in der if not W.has_promoted(d["schema"])]
    assert with_p == ["(first * %s({H}))" % p1.id], der
    p2 = W.register(reg, W.Promoted.from_schema(with_p[0], reg, W.sha("toy2"), "toy"))
    # carried through a start library exactly as a next generation would receive it
    entry = {"name": "g2_new", "inits": ["0"], "bodies": [], "finals": ["acc"], "schema": with_p[0],
             "promoted": W.lineage_records(reg, [p1.id])}
    reg_next = D.promote_start([entry])
    classes2 = [["(v + (first * (acc - last)))"], ["(v + (first * (acc - 1)))"]]
    der2 = W.derive_schemas(classes2, reg_next)
    w2 = [d["schema"] for d in der2 if p2.id in d["schema"]]
    p3 = W.Promoted.from_schema(w2[0], reg_next, W.sha("toy3"), "toy")
    rng = random.Random(3)
    ev_bad = 0
    for _ in range(300):
        x = rand_inputs(rng)
        for pid in (p2.id, p3.id):
            prog = ("fold", "0", "%s(v)" % pid, "acc")
            r = reg_next if pid in reg_next else dict(reg_next, **{p3.id: p3})
            ev_bad += W.run_program_direct(prog, x, True, r) != REF_RUN(W.expand_program(prog, r), x, True)
    ok = (p1.depth == 1 and p2.depth == 2 and p2.deps == [p1.id] and p2.lineage == [p1.id]
          and reg_next[p2.id].depth == 2 and p3.depth == 3 and p3.lineage == sorted([p1.id, p2.id])
          and W.dag_depth(reg_next) == 2 and p2.expansion == "(first * (acc - {H}))" and ev_bad == 0)
    RESULTS["DEPENDENCY"] = {"P1": p1.id, "derived_plain": plain, "derived_with_P1": with_p, "P2": p2.id,
                             "P2_depth": p2.depth, "P2_deps": p2.deps, "P2_expansion": p2.expansion,
                             "next_gen_registry_depth": W.dag_depth(reg_next), "derived_with_P2": w2,
                             "P3_depth": p3.depth, "P3_lineage": p3.lineage, "eval_mismatches": ev_bad, "PASS": ok}
    assert ok


def test_fold_recognition_sound():
    """Every recognised promoted form expands to a body with the same normalised structure and the same values."""
    reg = build_registry()
    pats = W._patterns(reg)
    ids = sorted(reg)
    rng = random.Random("W5P/TEST/FOLD/v1")
    n = rec = bad = 0
    for _ in range(3000):
        b = W.to_src(W.expand_term(rand_term(rng, 3, ids), reg))
        f = W.forms(b, reg, pats)
        n += 1
        if len(f) == 2:
            rec += 1
            bad += W.normalise(W.parse(W.expand(f[1], reg))) != W.normalise(W.parse(b))
            for _k in range(3):
                x = rand_inputs(rng)
                p0, p1 = ("fold", "0", b, "acc"), ("fold", "0", f[1], "acc")
                bad += REF_RUN(p0, x, True) != W.run_program_direct(p1, x, True, reg)
    RESULTS["RECOGNITION"] = {"bodies": n, "recognised": rec, "mismatches": bad, "PASS": bad == 0 and rec > 0}
    assert bad == 0 and rec > 0


# ---------------------------------------------------------------- W5-world tests (need the G5 body space)
_W5 = {}


def _w5():
    if not _W5:
        os.environ.setdefault("A17_FASTEVAL", "1")
        import a18
        a18.use_world("W5")
        _W5["a18"] = a18
    return _W5["a18"]


def test_instantiate_and_derive_continuity():
    """Empty registry: promote.instantiate == tier3d.instantiate and promote.derive_schemas == tier3d.derive_schemas."""
    _w5()
    import tier3d as T3D
    import a18
    rng = random.Random("W5P/TEST/INST/v1")
    schemas = [a18.G1, "(v - (acc + {H}))", "(acc - {H})", "math.gcd(abs((acc // {H})), abs(first))"]
    while len(schemas) < 40:
        s = a18._random_schema(rng)
        if s:
            schemas.append(s)
    ib = sum(W.instantiate(s, {}) != T3D.instantiate(s) for s in schemas)
    db = 0
    for _ in range(25):
        cls = [sorted(rng.sample(list(G.BODY_SPACE[:10842]), rng.randint(1, 4))) for _ in range(rng.randint(2, 4))]
        db += W.derive_schemas(cls, {}) != T3D.derive_schemas(cls)
    RESULTS["INSTANTIATE_DERIVE_CONTINUITY"] = {"schemas": len(schemas), "instantiate_mismatches": ib,
                                                "derive_cases": 25, "derive_mismatches": db, "PASS": ib == 0 and db == 0}
    assert ib == 0 and db == 0


def _ref_cost(cell, lib, escrow):
    import fair as FR
    old = G.run_program
    G.run_program = REF_RUN
    try:
        esc = E.Escrow(escrow)
        hits = FR.search_collect(lib, cell.parsed, esc, escrow, cell.seed, max_hits=1)
    finally:
        G.run_program = old
    return (hits[0][2], hits[0][0]) if hits else (escrow, None)


def test_conformance_fast_paths():
    """Bodies containing promoted primitives (via expansion): fasteval == reference interpreter, and a18.fast_cost ==
    walk.first_hit == the reference Cell.cost walk on libraries holding W5P entries (expanded bodies beyond G5)."""
    a18 = _w5()
    import a17
    import fair as FR
    import walk
    from w5p import donor as D
    FE = _fe()
    reg = build_registry(n1=4, n2=4, n3=2)
    ids = sorted(reg)
    rng = random.Random("W5P/TEST/CONF/v1")
    # (a) evaluator conformance on expanded W5P programs, B1_BOUNDARY + random inputs
    inputs = [list(x) for x in I.B1_BOUNDARY[::250] if x]
    inputs += [rand_inputs(rng) for _ in range(30)]
    ev = evb = 0
    for _ in range(300):
        p = W.expand_program(rand_program(rng, ids, reg), reg)
        for x in inputs:
            ev += 1
            a, b = REF_RUN(p, x, True), FE.run_program(p, x, True)
            evb += a != b or type(a) is not type(b)
    # (b) walk conformance on W5P libraries
    schemas = []
    for pid in ids:
        for s in ("(first + %s({H}))" % pid, "(%s({H}) * v)" % pid, "%s((acc + {H}))" % pid):
            if W.instantiate(s, reg):
                schemas.append(s)
    libs = [FR.pristine().entries]
    for s in rng.sample(schemas, min(8, len(schemas))):
        libs.append([D.schema_entry("g2_new", s, reg)] + FR.pristine().entries)
    out_of_g5 = sum(1 for l in libs[1:] for b in l[0]["bodies"] if b not in FR._BODY_SET)
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    pairs = mm = hits = hits_outside = 0
    for k in range(48):
        lib_e = libs[1 + k % (len(libs) - 1)] if k % 4 else libs[0]
        # half the families are planted from the library's own promoted bodies, so hits inside W5P entries occur
        if k % 2 and lib_e[0].get("schema"):
            body = rng.choice(lib_e[0]["bodies"])
        else:
            body = rng.choice(G.BODY_SPACE)
        spec = {"conffam": (body, rng.choice(finals), rng.choice(G.H1_SPACE))}
        prov = a17.Prov(spec)
        cell = FR.Cell(prov, "conffam", k, rng.choice([4, 6]), label="W5P-CONF")
        lib = FR.KLib(lib_e)
        esc = 6000
        a = _ref_cost(cell, lib, esc)
        b = a18.fast_cost(lib, cell, esc)
        c = walk.first_hit(lib, cell, esc)
        pairs += 1
        same = (a[0] == b[0] == c[0] and (a[1] is None) == (b[1] is None) == (c[1] is None)
                and (a[1] is None or tuple(a[1]) == tuple(b[1]) == tuple(c[1])))
        mm += not same
        hits += a[1] is not None
        hits_outside += a[1] is not None and a[1][0] == "fold" and a[1][2] not in FR._BODY_SET
    RESULTS["CONFORMANCE"] = {"evaluator_pairs": ev, "evaluator_mismatches": evb, "walk_pairs": pairs,
                              "walk_mismatches": mm, "walk_hits": hits, "walk_hits_on_bodies_outside_G5": hits_outside, "libraries": len(libs), "bodies_outside_G5_in_libraries": out_of_g5,
                              "PASS": evb == 0 and mm == 0 and ev >= 10_000}
    assert evb == 0 and mm == 0


def test_meter_exact():
    """The arithmetic execution-unit ledger equals brute-force iteration over lib.candidates for random walks."""
    _w5()
    import fair as FR
    from w5p import donor as D
    reg = build_registry(n1=2, n2=2, n3=1)
    fm = {}
    e = D.schema_entry("g2_new", "(first + %s({H}))" % sorted(reg)[0], reg, fm)
    lib = FR.KLib([e] + FR.pristine().entries)
    m = D.Meter(fm, reg)
    rng = random.Random(5)
    bad = 0
    for _ in range(12):
        seed, n = rng.randint(0, 10 ** 6), rng.randint(1, 30_000)
        ue = up = 0
        for k, (prog, _c) in enumerate(lib.candidates(seed)):
            if k >= n:
                break
            if prog[0] == "expr":
                s = W.nodes(W.parse(prog[1]))
                ue += s
                up += s
            else:
                si, sf = W.nodes(W.parse(prog[1])), W.nodes(W.parse(prog[3]))
                ue += si + sf + W.nodes(W.parse(prog[2]))
                up += si + sf + W.nodes(W.parse(fm.get(prog[2], prog[2])))
        bad += m.walk_units(lib, seed, n) != (ue, up)
    RESULTS["METER_EXACT"] = {"walks": 12, "mismatches": bad, "PASS": bad == 0}
    assert bad == 0


# ---------------------------------------------------------------- donor level (slow)
def _t12():
    R = ENG.parent / "beta01" / "runs"
    roles = {p["seed"]: p for p in json.loads((R / "T12_REPL" / "T12_ROLES.json").read_text(encoding="utf-8"))}
    panel = json.loads((R / "T12_T51" / "T51_PLAN.json").read_text(encoding="utf-8"))["panel"]
    ref = {(x["seed"], "%s_%s" % (x["genome"], x["obs"])): x
           for x in map(json.loads, (R / "T12_REPL" / "T12_DONORS.jsonl").read_text(encoding="utf-8").splitlines())}
    return roles, panel, ref


KEYS = ("selected_schema", "selected_origin", "selected_entries", "n_observed", "n_derived", "classes")


def run_noop_continuity():
    """NO-OP CONTINUITY: the W5P donor (promotion ENABLED; a pristine start carries no schema, so the registry is
    empty) reproduces Beta-01 T12 seed 17 rows exactly, for g11@O10 and g0@O4."""
    from w5p import harness as H
    roles, panel, ref = _t12()
    out = {}
    for rule, wd in (("g11", "O10"), ("g0", "O4")):
        t0 = time.perf_counter()
        r = H.run(("noop", rule, wd, 17, roles[17][wd], panel, None))
        x = ref[(17, "%s_%s" % (rule, wd))]
        out["%s_%s" % (rule, wd)] = {"equal": {k: r[k] == x[k] for k in KEYS}, "selected_schema": r["selected_schema"],
                                     "registry_size": len(r["w5p"]["promoted_in_ids"]),
                                     "seconds_wall": round(time.perf_counter() - t0, 1), "ref_seconds": x["seconds"],
                                     "cost": r["w5p"]["cost"]["total"]}
    ok = all(all(v["equal"].values()) for v in out.values())
    RESULTS["NOOP_CONTINUITY_T12_SEED17"] = dict(out, PASS=ok)
    return ok


def run_transplant_smoke():
    """Smoke donor with an INHERITED abstraction (T12 seed-17 g11@O10 selected library, schema (acc - {H})) on the
    same seed-17 O10 roles (engineering smoke, not a result):
      A  gtc.donor_g (g10 genome, MEMORISE excluded = g11)           -- the W5 reference
      B  donor_w5p(promote=False, same rule)                          -- must equal A on every output key
      C  donor_w5p(promote=True,  same rule)                          -- the W5P donor; timed against A
    """
    from w5p import harness as H  # noqa: F401  (import order: b02 first)
    import b02
    import gtc
    from w5p import donor as D
    roles, panel, ref = _t12()
    start = ref[(17, "g11_O10")]["selected_entries"]
    fams = roles[17]["O10"]
    b02.T.init_worker()
    import a17
    import a18_c1
    a17.R_VAL = a18_c1.R_VAL_C1
    fl = [dict(f, qualified_dev_size=f["Q2_size"]) for f in fams]
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fl}
    args = ("LIN17", "P", 17, fl, specs, panel, True, start)
    t0 = time.perf_counter()
    b02._set_rule("g11")
    A = gtc.donor_g("g10", args)
    b02._set_rule("g0")
    ta = time.perf_counter() - t0
    t0 = time.perf_counter()
    B = D.donor_w5p("g10", args, exclude=("MEMORISE",), promote=False, meter=False)
    tb = time.perf_counter() - t0
    t0 = time.perf_counter()
    C = D.donor_w5p("g10", args, exclude=("MEMORISE",), promote=True)
    tc = time.perf_counter() - t0
    keys = ("selected", "selected_schema", "selected_entries", "selection_table", "meta_charges", "n_derived",
            "n_composed_candidates", "classes", "n_observed")
    eqAB = {k: A[k] == B[k] for k in keys}
    w = C["w5p"]
    RESULTS["TRANSPLANT_SMOKE_SEED17"] = {
        "B_promotion_off_equals_donor_g": eqAB,
        "A_donor_g": {"selected": A["selected"], "selected_schema": A["selected_schema"], "n_derived": A["n_derived"],
                      "meta_charges": A["meta_charges"], "seconds": round(ta, 1)},
        "B_w5p_promote_off_no_meter_seconds": round(tb, 1),
        "C_w5p": {"selected": C["selected"], "selected_schema": C["selected_schema"],
                  "selected_schema_expansion": w["selected_schema_expansion"], "n_derived": C["n_derived"],
                  "n_derived_with_promoted": w["n_derived_with_promoted"],
                  "derived_with_promoted": w["derived_with_promoted"][:10],
                  "promoted_in_ids": w["promoted_in_ids"],
                  "promoted_in_schemas": [p["schema"] for p in w["promoted_in"]],
                  "selected_promoted": [{k: p[k] for k in ("id", "schema", "expansion", "depth", "deps")}
                                        for p in w["selected_promoted"]],
                  "dag_depth": w["dag_depth"], "observed_equal_to_A": C["n_observed"] == A["n_observed"]
                  and C["classes"] == A["classes"],
                  "meta_charges": C["meta_charges"], "cost": w["cost"], "seconds": round(tc, 1),
                  "selection_table": C["selection_table"]},
        "PASS": all(eqAB.values())}
    return all(eqAB.values())


def test_slow_donor_level():
    if not SLOW:
        import pytest
        pytest.skip("set W5P_SLOW=1")
    assert run_noop_continuity()
    assert run_transplant_smoke()


FAST = [test_parse_normalise_continuity, test_promotion_semantics, test_serialization_roundtrip,
        test_transplant_fresh_process, test_dependency_depth_bookkeeping, test_fold_recognition_sound,
        test_instantiate_and_derive_continuity, test_conformance_fast_paths, test_meter_exact]


def main():
    slow = "--slow" in sys.argv
    status = {}
    for t in FAST:
        t0 = time.perf_counter()
        try:
            t()
            status[t.__name__] = "PASS"
        except Exception as e:      # noqa: BLE001
            status[t.__name__] = "FAIL: %r" % (e,)
        print(t.__name__, status[t.__name__], "%.1fs" % (time.perf_counter() - t0), flush=True)
    if slow:
        for fn in (run_noop_continuity, run_transplant_smoke):
            t0 = time.perf_counter()
            try:
                status[fn.__name__] = "PASS" if fn() else "FAIL"
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                status[fn.__name__] = "FAIL: %r" % (e,)
            print(fn.__name__, status[fn.__name__], "%.1fs" % (time.perf_counter() - t0), flush=True)
    out = HERE.parent / ("W5P_TEST_RESULTS%s.json" % ("" if slow else "_FAST"))
    out.write_text(json.dumps({"status": status, "results": RESULTS}, indent=1, default=str) + "\n", encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
