"""E3 runner tests. Run from roles/Aphrodite/beta04:   python -m tfs1.e3.tests.run_tests
Uses the EXPOSED pilot_v2 worlds (development data). Writes tfs1/e3/E3_TEST_RESULTS.json."""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")

from tfs1 import core as C                                   # noqa: E402
from tfs1.library import Library, references_xs              # noqa: E402
from tfs1.membrane import code_hashes                        # noqa: E402
from tfs1.e3 import worlds as WD                             # noqa: E402
from tfs1.e3 import organism as O                            # noqa: E402
from tfs1.e3 import final_eval as FE                         # noqa: E402
from tfs1.e3 import dependency as DP                         # noqa: E402
from tfs1.e3 import e3_known_positive as KP                  # noqa: E402

BETA04 = Path(__file__).resolve().parents[3]
ROOT = BETA04 / "foundry" / "pilot_v2"
WORLD = "W1d5301d0"
HERE = Path(__file__).resolve().parent.parent
TESTS, RESULTS = [], {}


def test(fn):
    TESTS.append(fn)
    return fn


def check(c, msg="check failed"):
    if not c:
        raise AssertionError(msg)


def strip(rec):
    r = copy.deepcopy(rec)
    r.pop("cpu_s", None)
    for f in r["families"]:
        f.pop("cpu_s", None)
    for k in list(r["ledger"]):
        if k.endswith("cpu_s"):
            r["ledger"].pop(k)
    return r


def short(arm, n=10, B=1200, seed=0, **kw):
    return O.run_lifetime(str(ROOT), WORLD, arm, seed, n_families=n, B=B, **kw)


@test
def test_determinism_in_process_and_fresh_process():
    a = short("P1A1", 14, 1500)
    b = short("P1A1", 14, 1500)
    check(strip(a) == strip(b), "in-process lifetimes differ")
    code = ("import sys; sys.path.insert(0, %r); from tfs1.e3 import organism as O;"
            "print(O.run_lifetime(%r, %r, 'P1A1', 0, n_families=14, B=1500)['decision_sha256'])") % (
        str(BETA04), str(ROOT), WORLD)
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, timeout=600)
    check(out.stdout.strip() == a["decision_sha256"], "fresh process differs: %r" % out.stderr[-400:])
    c = short("P1A1", 14, 1500, seed=1)
    check(c["decision_sha256"] != a["decision_sha256"], "seed has no effect")
    return {"decision_sha256": a["decision_sha256"], "solved": a["solved"], "fresh_process_equal": True}


@test
def test_arm_view_only_access_log():
    po = WD.presentation_order(str(ROOT), WORLD, "CURRICULUM")          # coordinator side, BEFORE the lifetime
    log = WD.AccessLog()
    with log.active():
        W = WD.ArmWorld(str(ROOT), po["arm_world"])
        rec = O.Organism(W, po["order"][:12], "P1A1", 0, B=800).lifetime()
    view_dir = ROOT / "arm_view"
    outside = log.outside(view_dir)
    check(len(log.paths) >= 13, "access log recorded too little (%d)" % len(log.paths))
    check(not outside, "lifetime opened files outside the arm view: %r" % outside[:5])
    check(not any("evaluator" in p or "WORLD_" in p for p in log.paths), "evaluator-side file opened")
    # positive control: the log does catch an evaluator read
    log2 = WD.AccessLog()
    with log2.active():
        WD.Evaluator(str(ROOT), WORLD).task(po["order"][0])
    check(any("evaluator" in p for p in log2.paths), "access log missed an evaluator read")
    return {"paths_logged": len(log.paths), "outside_arm_view": 0, "arm_view_reads": rec["arm_view_reads"],
            "positive_control_detected": True}


@test
def test_budget_matching_and_crn():
    B, n = 1000, 8
    recs = {arm: short(arm, n, B) for arm in O.ARMS}
    for arm, r in recs.items():
        for f in r["families"]:
            check(f["charges"] <= B, "%s charges %d > B" % (arm, f["charges"]))
            check(f["solved"] or f["charges"] == B, "%s unsolved family charged %d != B" % (arm, f["charges"]))
            check(f["budget"] == B, "budget differs")
    # CRN: the first family has no history in any CURRICULUM arm -> identical search in all of them
    firsts = {arm: (r["families"][0]["slot"], r["families"][0]["hit_charge"], r["families"][0]["program"],
                    r["families"][0]["charges"]) for arm, r in recs.items() if r["order_name"] == "CURRICULUM"}
    check(len(set(firsts.values())) == 1, "first family differs across arms: %r" % firsts)
    # with promotion and archive OFF, arm decisions depend only on the family (P0A0 == itself on a re-run)
    return {"arms": len(recs), "B": B, "families": n, "first_family_identical_across_curriculum_arms": True,
            "solved_by_arm": {a: r["solved"] for a, r in recs.items()},
            "order_by_arm": {a: r["order_name"] for a, r in recs.items()}}


@test
def test_no_target_leakage_perturbed_evaluator():
    """Perturb test outputs, tribunal outputs and the witness of every family -> the lifetime (decisions, library,
    archive) is unchanged; final evaluation does change (the perturbation is effective)."""
    base = short("P1A1", 16, 1500)
    with tempfile.TemporaryDirectory() as td:
        pdir = Path(td) / "evaluator" / WORLD
        pdir.mkdir(parents=True)
        for f in (ROOT / "evaluator" / WORLD).glob("*.json"):
            d = json.loads(f.read_text())
            pert = lambda o: (o + 1) if isinstance(o, int) and not isinstance(o, bool) else (  # noqa: E731
                [v + 1 for v in o] if isinstance(o, list) else ("FAIL" if o != "FAIL" else 0))
            d["test"] = [[i, pert(o)] for i, o in d["test"]]
            d["tribunal"] = [[i, pert(o)] for i, o in d.get("tribunal", [])]
            d["witness"] = "(len xs)" if d.get("output_type") != "List" else "xs"
            (pdir / f.name).write_text(json.dumps(d))
        orig_init = WD.Evaluator.__init__

        def patched(self, root, world_id, override_dir=None):
            orig_init(self, root, world_id, override_dir=str(pdir))
        WD.Evaluator.__init__ = patched
        try:
            pert_rec = short("P1A1", 16, 1500)
            fe_pert = FE.evaluate_lifetime(pert_rec, str(ROOT), WORLD)
        finally:
            WD.Evaluator.__init__ = orig_init
    fe = FE.evaluate_lifetime(base, str(ROOT), WORLD)
    check(strip(base) == strip(pert_rec), "lifetime changed under evaluator perturbation")
    check(base["final_library_sha256"] == pert_rec["final_library_sha256"], "library changed")
    check(base["archive_final"] == pert_rec["archive_final"], "archive changed")
    q, qp = fe["endpoint"]["total_qualified"], fe_pert["endpoint"]["total_qualified"]
    check(base["solved"] == 0 or q != qp, "perturbation was not effective (%d vs %d)" % (q, qp))
    return {"decision_sha256": base["decision_sha256"], "qualified": q, "qualified_under_perturbation": qp,
            "solved": base["solved"]}


def synthetic_root(td, programs, aw="ASYNTH", n_dev=10, seed=7):
    """A PLANTED arm-view world (instrument test only): one family per program, dev from the program."""
    import hashlib as H
    import random as R
    rng = R.Random(seed)
    root = Path(td)
    vd = root / "arm_view" / aw
    vd.mkdir(parents=True)
    files, order = {}, []
    for k, src in enumerate(programs):
        t = C.parse(src)
        dev = []
        while len(dev) < n_dev:
            i = [rng.randint(-9, 9) for _ in range(rng.randint(1, 6))]
            v = C.evaluate(t, i)[0]
            if v != C.FAIL:
                dev.append([i, v])
        oid = "%016x" % k
        b = json.dumps({"id": oid, "dev": dev}).encode()
        (vd / ("%s.json" % oid)).write_bytes(b)
        files["arm_view/%s/%s.json" % (aw, oid)] = H.sha256(b).hexdigest()
        order.append(oid)
    (root / "arm_view" / "ARM_VIEW_MANIFEST.json").write_text(json.dumps({"worlds": {aw: {"files": files}}}))
    return root, aw, order


PLANTED = ["(map (lam x (neg x)) xs)", "(sum (map (lam x (neg x)) xs))", "(map (lam x (mul x x)) xs)",
           "(filter (lam x (gt x 0)) xs)", "(sum (map (lam x (mul x x)) xs))", "(map (lam x (neg (mul x x))) xs)"]


@test
def test_lifetime_library_semantics_and_v01_1():
    with tempfile.TemporaryDirectory() as td:
        root, aw, order = synthetic_root(td, PLANTED)
        W = WD.ArmWorld(str(root), aw)
        rec = O.Organism(W, order, "P1A0", 0, B=5000).lifetime()
        n_check = 0
        for sha_, js in rec["library_snapshots"].items():
            lib = Library.from_json(js)
            check(lib.sha256() == sha_, "snapshot hash")
            check(not any(references_xs(e.body_t) for e in lib.entries.values()), "v0.1-1 violated")
        for f in rec["families"]:
            if f["solved"] and f["library_sha256"]:
                lib = FE.library_of(rec, f)
                t = C.parse(f["program"])
                for i, _o in W.family(f["opaque"])["dev"]:
                    check(C.same_value(C.evaluate(t, i, lib)[0], C.evaluate(lib.expand(t), i)[0]), "prom != exp")
                    n_check += 1
        check(len(rec["library_snapshots"]) >= 1 and n_check > 0, "no promotion happened; test not exercised")
    return {"label": "PLANTED synthetic arm-view world (instrument test)", "snapshots": len(rec["library_snapshots"]),
            "solved": rec["solved"], "programs": [f["program"] for f in rec["families"]],
            "final_library": [(e["body"], e["depth"]) for e in rec["final_library"]["entries"]],
            "eval_checks": n_check, "families_using_library": sum(f["uses_library"] for f in rec["families"])}


@test
def test_checkpoint_resume_identical():
    from tfs1.e3.resumable import ResumableOrganism
    out = {}
    with tempfile.TemporaryDirectory() as td:
        root, aw, order = synthetic_root(Path(td) / "w", PLANTED + ["(sum (map (lam x (neg (mul x x))) xs))"])
        for arm in ("P1A1", "RANDOM-LIBRARY", "RANDOM-ARCHIVE"):
            W = WD.ArmWorld(str(root), aw)
            full = O.Organism(W, order, arm, 0, B=3000).lifetime()
            ck = Path(td) / ("ck_%s.json" % arm)
            n_calls = 0
            while True:
                n_calls += 1
                r = ResumableOrganism(WD.ArmWorld(str(root), aw), order, arm, 0, B=3000).run_until(ck, 0.0)
                if r.get("done"):
                    break
            check(r["decision_sha256"] == full["decision_sha256"], "%s resumed decisions differ" % arm)
            check(r["final_library_sha256"] == full["final_library_sha256"], "%s library differs" % arm)
            check(r["archive_final"] == full["archive_final"], "%s archive differs" % arm)
            out[arm] = {"calls": n_calls, "solved": full["solved"], "library": len(full["final_library"]["entries"])}
    return out


@test
def test_developmental_known_answer_depth2():
    d = O.Developmental("on", 8, 0)
    d.update(C.parse("(map (lam x (pow x 3)) xs)"))
    d.update(C.parse("(sum (map (lam x (pow x 3)) (rev xs)))"))
    d.update(C.parse("(filter (lam x (gt x 4)) xs)"))
    d.update(C.parse("(map (lam x (if (gt x 4) (pow x 3) x)) xs)"))
    lib = d.rebuild()
    bodies = {e.body: e.depth for e in lib.entries.values()}
    check(bodies.get("(pow h0 3)") == 1 and bodies.get("(gt h0 4)") == 1, "level-1 entries: %r" % bodies)
    d2 = [e for e in lib.entries.values() if e.depth == 2]
    check(d2 and any("if" in e.body for e in d2), "no depth-2 composition: %r" % bodies)
    # random library: same count, result types and body sizes
    r = O.Developmental("random", 8, 0)
    for p in ("(map (lam x (pow x 3)) xs)", "(sum (map (lam x (pow x 3)) (rev xs)))", "(filter (lam x (gt x 4)) xs)",
              "(map (lam x (if (gt x 4) (pow x 3) x)) xs)"):
        r.update(C.parse(p))
    rl = r.rebuild()
    sel = d.selection()
    check(len(rl) == len(sel), "random library size %d vs selection %d" % (len(rl), len(sel)))
    check(sorted(e.ret for e in rl.entries.values()) == sorted(c["ret"] if c["ret"] in (C.INT, C.BOOL) else C.INT
                                                                 for c in sel), "ret types differ")
    check(all(e.depth == 1 for e in rl.entries.values()), "random entries must not compose")
    return {"library": sorted(bodies.items()), "random_library": sorted(e.body for e in rl.entries.values())}


@test
def test_random_archive_matched():
    a = short("P0A1", 20, 1500)
    r = short("RANDOM-ARCHIVE", 20, 1500)
    ca = [(x["T"], x["size"], x["family"]) for x in a["archive_final"]]
    cr = [(x["T"], x["size"], x["family"]) for x in r["archive_final"]]
    check(len(ca) > 0 and all(x["kind"] == "random" for x in r["archive_final"]), "random archive kinds")
    # matched by construction per family on its OWN run: count per family = solved + top-k partial of that run
    per = {}
    for f in r["families"]:
        per[f["slot"]] = sum(1 for x in r["archive_final"] if x["family"] == f["slot"])
    check(all(v <= 1 + r["config"]["k_partial"] for v in per.values()), "count rule")
    return {"archive_P0A1": len(ca), "archive_RANDOM": len(cr),
            "sizes_P0A1": sorted(x[1] for x in ca)[:20], "sizes_RANDOM": sorted(x[1] for x in cr)[:20]}


@test
def test_dependency_machinery():
    lib = Library(closed_args=True)
    a, _ = lib.promote_lambda(C.parse("(lam x (pow x 3))"))
    b, _ = lib.promote_body(C.parse("(if (gt h0 4) (%s h0) h0)" % a.id))
    c, _ = lib.promote_lambda(C.parse("(lam x (add x 1))"))
    red = DP.reduced_library(lib, a.id)
    check(set(red.ids()) == {c.id}, "dependents not removed: %r" % red.ids())
    sh = DP.sham_library(red, a, 0)
    e = sh["library"].entries[sh["sham_id"]]
    check(e.params == a.params and e.ret == a.ret and e.depth == 1, "sham signature")
    return {"reduced": red.ids(), "sham_body": sh["sham_body"], "target_body": a.body}


@test
def test_known_positive_extraction_and_judge():
    cases = {("(div (add 1 (last xs)) 3)", "f"): "(lam x (div (add 1 x) 3))",
             ("(len (filter (lam x (lt x (add 2 3))) xs))", "p"): "(lam x (lt x (add 2 3)))",
             ("(foldl (lam a (lam b (sub b (div a 3)))) 1 xs)", "s"): "(lam a (lam b (sub b (div a 3))))",
             ("(sum xs)", "f"): None}
    for (p, k), want in cases.items():
        ex = KP.extract_mechanism(p, k)
        got = C.to_str(ex[0]) if ex else None
        check(got == want, "%s/%s -> %s" % (p, k, got))
    task = {"test": [[[1, 2], 3]], "tribunal": [[[], "FAIL"], [[4], 4]]}
    check(WD.judge("(sum xs)", task)["qualified"] is False, "sum([]) = 0 must not match FAIL")
    check(WD.judge("(add (head xs) (sum (drop 1 xs)))", task)["qualified"] is True, "FAIL agreement")
    # fallback OFF: the readout form gives no mechanism, a closed lambda still does
    check(KP.extract_mechanism("(div (add 1 (last xs)) 3)", "f", fallback=False) is None, "fallback off ignored")
    ex = KP.extract_mechanism("(len (filter (lam x (lt x (add 2 3))) xs))", "p", fallback=False)
    check(ex is not None and ex[1] == "closed_lambda", "closed lambda lost with fallback off")
    return {"cases": len(cases) + 4}


# ================================================================ E3-KP amendment A1: OE pruning, rows, links, verdict
from tfs1.enum import Enumerator, oe_probe_assignments     # noqa: E402

# Frozen BEFORE the OE change (enum.py blob e1c2993cb5dc20ea021306fc19bfc5d0c7846ca9 at f4a46d777): the keyed walk's
# full evaluated-candidate trace (charge, text), charges, units and class counts. oe=False must reproduce them exactly.
OE_OFF_REFERENCE = [
    {"fid": "W1d5301d0-F006-R1", "lib": [], "budget": 60000, "seed": 0, "charges": 49862, "hit_charge": 49862,
     "program": "(div (add 1 (last xs)) 3)", "units": [171043, 171043],
     "trace_sha256": "f7c1ac862c9ef24c7a6c01e42bb13a8bc5f5adc03a58e3f382a2dba483769b13",
     "counts": [4, 10, 110, 658, 6723, 55995, 563912]},
    {"fid": "W1d5301d0-F071-R4", "lib": ["(lam x (lt x (add 2 3)))", "(lam x (div (add 1 x) 3))"], "budget": 70000,
     "seed": 0, "charges": 64561, "hit_charge": 64561,
     "program": "(filter (lam x (L_91245740aedc x)) (map (lam x (L_a7616ca2cd22 x)) xs))", "units": [620942, 537660],
     "trace_sha256": "17362243ccc6b4b1ff5542c2b9dd6e2fdad32192f6176b1874fb16246d092313",
     "counts": [1, 1, 14, 106, 1072, 10640, 113144]},
    {"fid": "W1d5301d0-F027-R3", "lib": [], "budget": 25000, "seed": 1, "charges": 25000, "hit_charge": None,
     "program": None, "units": [76865, 76865],
     "trace_sha256": "198b3fc60bc1a340c5749b3f6baf9d811cca2044f5fa01812f840e39675eea9c",
     "counts": [4, 10, 110, 658, 6723, 55995, 563912]},
]


def _pilot_task(fid, world=WORLD):
    ev = WD.Evaluator(str(ROOT), world)
    by = {m["family_id"]: o for o, m in ev.id_map.items()}
    return ev.task(by[fid])


def _lib_of(lams):
    if not lams:
        return None
    lib = Library(closed_args=True)
    for s in lams:
        lib.promote_lambda(C.parse(s), {"t": "ref"})
    return lib


def _trace_sha(tr):
    import hashlib
    return hashlib.sha256("\n".join("%d %s" % x for x in tr).encode()).hexdigest()


@test
def test_oe_off_byte_identical_to_pre_oe_enumerator():
    for ref in OE_OFF_REFERENCE:
        task = _pilot_task(ref["fid"])
        for kw in ({}, {"oe": False}):
            E = Enumerator(_lib_of(ref["lib"]), **kw)
            tr = []
            r = E.search(task["dev"], task["output_type"], ref["seed"], ref["fid"], ref["budget"], 12, trace=tr)
            got = {"charges": r["charges"], "hit_charge": r["hit_charge"], "program": r["program"],
                   "units": [r["units_expanded"], r["units_promoted"]], "trace_sha256": _trace_sha(tr),
                   "counts": [E.count(task["output_type"], (), n) for n in range(1, 8)]}
            for k, v in got.items():
                check(v == ref[k], "%s %s: %r != frozen %r" % (ref["fid"], k, v, ref[k]))
            check("oe" not in r and "oe_stats" not in r, "oe=False result carries OE fields")
    return {"cases": len(OE_OFF_REFERENCE), "frozen_at": "f4a46d777 enum.py e1c2993c", "identical": True}


def _fresh_sig(t, ctx_len, inputs, lib=None):
    """Independent re-evaluation of an OE signature (fresh compile, no shared cache)."""
    fn = C.compile_term(t, lib, None, swap=lib is not None)
    out = []
    for inp, assigns in zip(inputs, oe_probe_assignments(inputs, ctx_len)):
        for env in assigns:
            C.XS[0] = list(inp)
            C.D[0] = 0
            try:
                v = fn(env)
            except C.Fail:
                v = C.FAIL
            out.append(tuple(v) if isinstance(v, list) else v)
    C.D[0] = 0
    return tuple(out)


@test
def test_oe_pruned_terms_observationally_equal_on_dev():
    """oe=True: every pruned subterm equals its kept representative on the OE probe set (dev inputs x binder probes);
    for closed terms (ctx = ()) this is value-or-FAIL equality on every dev input, and substituting representatives
    into every root program of a non-OE class leaves the dev vector unchanged (exactness of closed-context OE)."""
    task = _pilot_task("W1d5301d0-F006-R1")
    inputs = [i for i, _o in task["dev"]]
    E = Enumerator(None, oe=True, oe_inputs=inputs)
    E.oe_pruned_log = []
    gen7 = E.count(C.INT, (), 7)                     # builds every pruned table up to size 6, all contexts used
    log = E.oe_pruned_log
    check(len(log) > 1000, "too little pruning to test (%d)" % len(log))
    kept_text = {}
    for (T, ctx, n), lst in E._tab.items():
        for t, s in lst:
            kept_text[(T, ctx, s)] = t
    by_ctx, checked = {}, 0
    for i, (T, ctx, n, s, rep) in enumerate(log):
        by_ctx[len(ctx)] = by_ctx.get(len(ctx), 0) + 1
        if i % max(1, len(log) // 4000):
            continue
        tp, tr = C.parse(s, ctx), kept_text[(T, ctx, rep)]
        check(C.size(tr) <= C.size(tp), "representative larger than the pruned term")
        check((C.size(tr), C.to_str(tr, ctx)) < (C.size(tp), s), "representative is not earlier")
        check(_fresh_sig(tp, len(ctx), inputs) == _fresh_sig(tr, len(ctx), inputs),
              "pruned %s not equal to representative %s on the probe set" % (s, rep))
        if not ctx:
            for inp in inputs:
                a, _u, _v = C.evaluate(tp, inp)
                b, _u, _v = C.evaluate(tr, inp)
                check(C.same_value(a, b), "closed pruned term differs on a dev input")
        checked += 1
    # exactness of closed-context OE: substitute representatives for closed subterms of every non-OE root of size <= 6
    rep_of = {(T, s): kept_text[(T, ctx, rep)] for (T, ctx, n, s, rep) in log if not ctx}

    def subst(t):
        if t[0] in ("int", "var", "xs", "hole", "lam"):
            return t
        new = (t[0],) + tuple(subst(a) for a in t[1:])
        try:
            T = C.type_of(new)
        except C.TypeErr:
            return new
        return rep_of.get((T, C.to_str(new)), new)
    base = Enumerator(None)
    n_roots = n_changed = 0
    for T in (C.INT, C.LIST, C.BOOL):
        for n in range(1, 7):
            for t, s in base.terms(T, (), n):
                t2 = subst(t)
                n_roots += 1
                if t2 == t:
                    continue
                n_changed += 1
                for inp in inputs:
                    a = C.evaluate(t, inp)[0]
                    b = C.evaluate(t2, inp)[0]
                    check(C.same_value(a, b), "substitution changed the dev value of %s" % s)
    check(n_changed > 1000, "substitution check exercised too little (%d)" % n_changed)
    return {"pruned_logged": len(log), "pruned_checked": checked, "pruned_by_ctx_arity": by_ctx,
            "oe_stats": E.oe_stats, "generated_Int7_oe": gen7, "Int7_base": Enumerator(None).count(C.INT, (), 7),
            "roots_substituted": n_changed, "roots_scanned": n_roots}


@test
def test_oe_charges_exact_and_deterministic():
    """oe=True: exactly 1 charge per evaluated root candidate; completed size classes are walked in full (count() =
    the generated class); no root candidate is evaluated twice; deterministic; pruning does not lose the pilot stone
    (same program as the base walk, fewer charges)."""
    fid = "W1d5301d0-F006-R1"
    task = _pilot_task(fid)
    runs = []
    for _ in range(2):
        E = Enumerator(None, oe=True)
        tr = []
        r = E.search(task["dev"], task["output_type"], 0, fid, 60000, 12, trace=tr)
        runs.append((r, tr, E))
    (r, tr, E), (r2, tr2, _E2) = runs
    check(_trace_sha(tr) == _trace_sha(tr2) and r["program"] == r2["program"], "OE walk not deterministic")
    check(len(tr) == r["charges"] and [c for c, _s in tr] == list(range(1, r["charges"] + 1)), "charge != eval")
    check(len({s for _c, s in tr}) == len(tr), "a root candidate was evaluated twice")
    sizes = {}
    for _c, s in tr:
        n = C.size(C.parse(s))
        sizes[n] = sizes.get(n, 0) + 1
    for n in range(1, r["complete_through_size"] + 1):
        check(sizes.get(n, 0) == E.count(task["output_type"], (), n), "size %d not walked in full" % n)
    check(r["hit"] and r["program"] == OE_OFF_REFERENCE[0]["program"], "OE lost the stone")
    check(r["charges"] < OE_OFF_REFERENCE[0]["charges"], "OE did not reduce charges")
    check(r["oe_stats"]["signature_evals"] > 0 and r["oe_stats"]["pruned"] > 0, "no OE infra ledger")
    return {"charges_oe": r["charges"], "charges_base": OE_OFF_REFERENCE[0]["charges"], "program": r["program"],
            "oe_stats": r["oe_stats"], "walked_by_size": sizes}


def _fam(link=None, q=False, sf=True, world="W", rung="R3", detail=None, complete=True, sk="k"):
    return {"world": world, "family_id": "F", "rung": rung, "skeleton": sk, "chain_qualified": q,
            "scratch_fails": sf, "complete": complete, "first_failing_link": link, "link_detail": detail}


@test
def test_kp_pooled_verdict_and_oe_trigger_rules():
    V = KP.pooled_verdict
    # 12 / 15 chain-qualified and 12 / 15 scratch failing -> YES (exactly 80%)
    fams = [_fam(q=True) for _ in range(12)] + [_fam("HORIZON_R1", detail="IN_CLASS") for _ in range(3)]
    for i in range(3):
        fams[i]["scratch_fails"] = False
    v = V(fams, primary=True)
    check(v["TFS1_INSTRUMENT_QUALIFIED"] == "YES" and v["TFS1_REACHABILITY_INSTRUMENT"] is None, "12/15 must pass")
    check(v["scratch_fails_all_descriptive"] is False, "scratch-all descriptive")
    # 11 / 15 chain -> NO
    fams2 = [_fam(q=True) for _ in range(11)] + [_fam("HORIZON_R1", detail="IN_CLASS") for _ in range(4)]
    v2 = V(fams2, primary=True)
    check(v2["TFS1_INSTRUMENT_QUALIFIED"] == "NO" and v2["TFS1_REACHABILITY_INSTRUMENT"] == "FAIL", "11/15")
    check(v2["oe_repair_trigger"]["triggered"], "4/4 horizon must trigger the OE repair")
    # scratch fails only 11 / 15 -> NO even with 15 / 15 chain
    fams3 = [_fam(q=True) for _ in range(15)]
    for i in range(4):
        fams3[i]["scratch_fails"] = False
    v3 = V(fams3, primary=True)
    check(v3["TFS1_INSTRUMENT_QUALIFIED"] == "NO" and not v3["oe_repair_trigger"]["triggered"], "scratch rule")
    # horizon exactly half of the failing families -> NOT triggered (strict majority); plurality reading reported
    fams4 = [_fam(q=True) for _ in range(7)] + [_fam("HORIZON_R1", detail="IN_CLASS") for _ in range(4)] + \
        [_fam("UNDERDETERMINED_STONE") for _ in range(3)] + [_fam("R1_ACQUISITION")]
    v4 = V(fams4, primary=True)
    check(not v4["oe_repair_trigger"]["triggered"] and v4["oe_repair_trigger"]["plurality_reading"], "4/8")
    check(v4["first_failing_link_counts"]["HORIZON_R1"] == 4 and v4["dominant_link_plurality"] == "HORIZON_R1", "")
    # incomplete -> INCOMPLETE; secondary rows carry no trigger
    v5 = V([_fam(q=True, complete=False)], primary=False)
    check(v5["TFS1_INSTRUMENT_QUALIFIED"] == "INCOMPLETE" and "oe_repair_trigger" not in v5, "incomplete")
    # n = 7 generalisation: 6/7 >= 80% passes, 5/7 does not
    check(V([_fam(q=True)] * 6 + [_fam("HORIZON_R1")], False)["TFS1_INSTRUMENT_QUALIFIED"] == "YES", "6/7")
    check(V([_fam(q=True)] * 5 + [_fam("HORIZON_R1")] * 2, False)["TFS1_INSTRUMENT_QUALIFIED"] == "NO", "5/7")
    return {"cases": 8}


@test
def test_kp_first_failing_link_rules():
    kp = KP.KP(str(ROOT), WORLD)
    fid = "W1d5301d0-F027-R3"                                # constituents f1, s0
    cons = kp.constituents(fid)
    acq = {m: {"status": "ACQUIRED", "agrees_with_sealed_on_probe": 1.0} for m in cons}

    def miss(link, detail):
        return {"status": "NOT_ACQUIRED", "link": link, "link_detail": detail}
    st = {"size_promoted_form": 7, "hitting_cost_bracket": [131402, 1427485]}
    cases = [
        ({cons[0]: miss("HORIZON_R1", "IN_CLASS"), cons[1]: miss("UNDERDETERMINED_STONE", "x")}, None,
         "HORIZON_R1"),                                                     # first missing unit in mechanisms_used order
        ({cons[0]: acq[cons[0]], cons[1]: miss("R1_ACQUISITION", "NO_EXTRACTABLE_MECHANISM")}, None, "R1_ACQUISITION"),
        (acq, {"status": "SOLVED"}, None),
        ({cons[0]: dict(acq[cons[0]], agrees_with_sealed_on_probe=0.9), cons[1]: acq[cons[1]]},
         {"status": "SOLVED"}, None),                                       # flagged, not failed
        ({cons[0]: dict(acq[cons[0]], agrees_with_sealed_on_probe=0.9), cons[1]: acq[cons[1]]},
         {"status": "NOT_FOUND_AT_BUDGET", "complete_through_size": 6, "static": st}, "UNDERDETERMINED_STONE"),
        (acq, {"status": "FIRST_DEV_CONSISTENT_FAILS_TEST"}, "COMPOSITION_UNDERDETERMINED"),
        (acq, {"status": "NOT_FOUND_AT_BUDGET", "complete_through_size": 6, "static": st}, "COMPOSITION_HORIZON"),
        (acq, {"status": "NOT_FOUND_AT_BUDGET", "complete_through_size": 7, "static": st}, "UNDERDETERMINED_STONE"),
    ]
    for units, chain, want in cases:
        got = kp.family_link(fid, units, chain)["link"]
        check(got == want, "link %r != %r for %r / %r" % (got, want, units, chain))
    check(kp.family_link(fid, acq, {"status": "NOT_FOUND_AT_BUDGET", "complete_through_size": 6,
                                    "static": st})["detail"] == "IN_CLASS", "IN_CLASS detail")
    check(kp.family_link(fid, acq, {"status": "NOT_FOUND_AT_BUDGET", "complete_through_size": 5,
                                    "static": st})["detail"] == "CLASS_NOT_ENTERED", "NOT_ENTERED detail")
    check(KP._horizon(7, 8) == "IN_CLASS" and KP._horizon(5, 8) == "CLASS_NOT_ENTERED" and KP._horizon(8, 8) is None,
          "horizon helper")
    return {"cases": len(cases) + 3}


@test
def test_kp_rows_separate_cache_keys_and_reuse():
    """Every secondary row writes its own row key; identical searches are shared (fallback-off re-uses the primary's
    R1 searches, every library-free row re-uses scratch); the foundry row runs no R1 search and cross-checks
    FINAL.jsonl; extra seeds re-key every search. Small budget (development)."""
    B = 20000
    rows = {"primary": KP.Config(budget=B), "fallback_off": KP.Config(fallback=False, budget=B),
            "foundry": KP.Config(source="foundry", budget=B), "seed1": KP.Config(seed=1, budget=B),
            "all": KP.Config(scope="all", budget=B), "oe": KP.Config(oe=True, budget=B)}
    check(len({c.key() for c in rows.values()}) == len(rows), "row keys collide")
    with tempfile.TemporaryDirectory() as td:
        n_search = {}
        for name in ("primary", "fallback_off", "foundry", "seed1"):
            d = KP.run_stages(str(ROOT), WORLD, rows[name], "all", td, log=lambda s: None)
            n_search[name] = len(d["searches"])
        check(set(d["rows"]) == {rows[n].key() for n in ("primary", "fallback_off", "foundry", "seed1")}, "rows")
        prim, fbo = d["rows"][rows["primary"].key()], d["rows"][rows["fallback_off"].key()]
        fnd = d["rows"][rows["foundry"].key()]
        check(all(u["source"] == "foundry" and not u["attempts"] for u in fnd["units"].values()), "foundry ran R1")
        check(all(u.get("final_jsonl_crosscheck") is True for u in fnd["units"].values()
                  if u["status"] == "ACQUIRED"), "FINAL.jsonl cross-check")
        # at B = 2e4 no R1 stone of this world is found, so fallback-off needs no new search (all shared with the
        # primary); the foundry row adds exactly one chain search per admitted family (scratch shared); seed 1 re-keys
        adm = KP.KP(str(ROOT), WORLD).admitted()
        check(n_search["fallback_off"] == n_search["primary"], "fallback-off re-ran shared searches")
        check(n_search["foundry"] == n_search["fallback_off"] + len(adm), "foundry row: one chain search per family")
        new_seed1 = [k for k in d["searches"] if "|seed=1|" in k]
        check(len(new_seed1) == n_search["seed1"] - n_search["foundry"] > 0, "seed-1 searches not re-keyed")
        check(set(prim["scratch"]) == set(fbo["scratch"]) == set(fnd["scratch"]), "scratch rows")
        desc = KP.KP(str(ROOT), WORLD).describe(d, rows["primary"])
        check(desc["descriptive_only"] and all(f["complete"] for f in desc["families"]), "describe")
        pooled = KP.pooled(str(ROOT), [WORLD], rows["primary"], td)
        check(pooled["verdict"]["n_admitted_R3_R4"] == 4, "pooled family count")
    return {"search_cache_sizes": n_search, "row_keys": [c.key() for c in rows.values()]}


# ================================================================ E3-ID (windows/E3ID_PREREG.md)
from tfs1.e3 import e3_identifiability as IDM          # noqa: E402


@test
def test_id_behaviour_classes_and_identifiability_labels():
    """Classes on probe INPUTS (FAIL is a value), first-appearance ranks, NO_STONE programs counted, post-hoc
    sealed-equivalent rank and R1 verdict, AMBIGUOUS / UNIQUE / NO_STONE labels."""
    xs_dev = [[1, 5, 4, 9], [4, 6, 2], [0, 7, 3, 5]]
    task = {"test": [[i, [v for v in i if v > 4]] for i in xs_dev],
            "tribunal": [[[5, 4, 10], [5, 10]]]}
    hits = [[10, "(filter (lam x (lt 3 x)) xs)"],          # x > 3            class 1
            [20, "(rev (rev xs))"],                         # no stone
            [30, "(filter (lam x (gt x 3)) xs)"],           # x > 3 again      class 1
            [40, "(filter (lam x (gt x (add 2 2))) xs)"],   # x > 4 (sealed)   class 2
            [50, "(filter (lam x (lt 4 x)) xs)"]]           # x > 4 again      class 2
    r = IDM.classify(hits, "p", "(lam x (gt x (add 2 2)))", task)
    check(r["n_classes"] == 2 and r["n_no_stone_programs"] == 1 and r["n_dev_consistent_programs"] == 5, "counts")
    check(r["slot_order"][1] == IDM.NO_STONE and len(r["slot_order"]) == 3, "slot order")
    check(r["classes"][0]["n_programs"] == 2 and r["classes"][1]["n_programs"] == 2, "class sizes")
    check(r["ID_IDENTIFIABILITY"] == "AMBIGUOUS" and not r["first_class_sealed_equivalent"], "AMBIGUOUS")
    check(r["sealed_equivalent_class_rank"] == 2 and r["sealed_equivalent_first_charge"] == 40
          and r["sealed_equivalent_first_ordinal"] == 4, "sealed rank")
    check(r["sealed_equivalent_first_program_r1_qualified"] is True and r["classes"][0]["r1_qualified"] is False,
          "post-hoc R1 verdicts")
    r2 = IDM.classify(hits[3:], "p", "(lam x (gt x (add 2 2)))", task)
    check(r2["ID_IDENTIFIABILITY"] == "UNIQUE" and r2["n_classes"] == 1, "UNIQUE")
    r3 = IDM.classify(hits[2:], "p", "(lam x (gt x (add 2 2)))", task)
    check(r3["ID_IDENTIFIABILITY"] == "AMBIGUOUS", "first class wrong, 2 classes")
    check(IDM.classify([[5, "(rev xs)"]], "p", "(lam x (gt x 4))", task)["ID_IDENTIFIABILITY"] == "NO_STONE", "")
    # FAIL is a value: (div x x) and the constant 1 differ only at 0 (FAIL vs 1)
    b1, b2 = IDM.behaviour(C.parse("(lam x (div x x))")), IDM.behaviour(C.parse("(lam x (div 3 3))"))
    check(b1 != b2 and sum(u != v for u, v in zip(b1, b2)) == 1 and C.FAIL in b1, "FAIL as a value")
    # binary stones on the [-12, 12]^2 grid
    bs = IDM.behaviour(C.parse("(lam a (lam b (sub b (div a 3))))"))
    check(len(bs) == 625, "pair grid")
    return {"classes": r["n_classes"], "labels": [r["ID_IDENTIFIABILITY"], r2["ID_IDENTIFIABILITY"]]}


def _id_case(td, world, B):
    KP.run_stages(str(ROOT), world, KP.Config(budget=B), "chain", td, log=lambda s: None)
    return IDM.run_stages(str(ROOT), world, td, td, "all", B, ks=(1, 2), cert=True, log=lambda s: None)


@test
def test_id_retain1_reproduces_e3kp_primary():
    """RETAIN-1 (designated, uncertified) reproduces the E3-KP primary chain outcome EXACTLY (byte-identical library
    sha, status, program, charge, charges) on every family whose constituents the primary acquired; RETAIN-1-CERT
    reproduces it on EVERY family (CHAIN_C_FAIL included). Also: ID-1's first hit equals the primary attempt's.
    Development budgets on EXPOSED pilot_v2: W1d5301d0 at 3e5 (all units acquired; one chain solved) and W0467897d
    at 6e4 (no unit acquired; p0's first dev-consistent stone rejected by the R1 certifier)."""
    out = {}
    with tempfile.TemporaryDirectory() as td:
        for world, B in (("W1d5301d0", 300000), ("W0467897d", 60000)):
            d = _id_case(td, world, B)
            I = IDM.ID(str(ROOT), world, td, B)
            n_cmp = 0
            for fid in I.kp.admitted():
                acq = all(I.prim["units"][m]["status"] == "ACQUIRED" for m in I.kp.constituents(fid))
                r1, rc = d["retain"]["RETAIN-1"][fid], d["retain"]["RETAIN-1-CERT"][fid]
                check(rc["reproduces_primary"], "RETAIN-1-CERT differs from the primary on %s" % fid)
                if acq:
                    check(r1["reproduces_primary"], "RETAIN-1 differs from the primary on %s: %r vs %r" % (
                        fid, (r1["status"], r1.get("found"), r1.get("charge")), r1["primary_chain"]))
                    n_cmp += 1
                else:
                    check(r1["reproduces_primary"] or r1["retain1_differs_by_design"], "unflagged difference")
            check(all(rec["primary_first_hit_matches"] for rec in d["id1"].values()), "ID-1 first hit")
            out[world] = {"B": B, "families_exact": n_cmp,
                          "statuses": {f: r["status"] for f, r in d["retain"]["RETAIN-1"].items()},
                          "id1": {k: (v["n_classes"], v["ID_IDENTIFIABILITY"]) for k, v in d["id1"].items()}}
        check(out["W1d5301d0"]["families_exact"] == 4, "exact comparison not exercised on all-acquired families")
        check("W0467897d" in out and any(v[0] >= 1 for v in out["W0467897d"]["id1"].values()), "non-acquired path")
    return out


@test
def test_id_pooled_outcome_rules():
    def U(lab, und=True, used=True):
        return {"world": "W", "mechanism": "m%d" % id(lab), "ID_IDENTIFIABILITY": lab, "underdetermined_stone_unit": und,
                "used_by_failed_family": used}

    def Fm(q4, link="UNDERDETERMINED_STONE"):
        r = {"qualified": q4, "link": None if q4 else link, "reproduces_primary": True,
             "retain1_differs_by_design": False}
        return {"family_id": "F", "RETAIN-1": r, "RETAIN-2": r, "RETAIN-4": r}
    f12 = [Fm(True) for _ in range(12)] + [Fm(False) for _ in range(3)]
    f11 = [Fm(True) for _ in range(11)] + [Fm(False, "COMPOSITION_HORIZON") for _ in range(4)]
    amb = [U("AMBIGUOUS") for _ in range(5)] + [U("UNIQUE") for _ in range(2)]
    o = IDM.outcomes(amb, f12)
    check(o["ID_RETENTION_REPAIR"] == "YES" and o["interpretation"] == "DEVELOPMENTAL_MACHINERY", "map 1")
    check(o["ID_IDENTIFIABILITY"]["fraction_ambiguous"] == round(5 / 7, 4), "fraction")
    o = IDM.outcomes(amb, f11)
    check(o["ID_RETENTION_REPAIR"] == "NO" and o["interpretation"] == "WORLD_RULER_IDENTIFIABILITY", "map 2")
    check(o["retain_rows"]["RETAIN-4"]["first_failing_link_counts"] == {"COMPOSITION_HORIZON": 4}, "link counts")
    o = IDM.outcomes([U("UNIQUE") for _ in range(4)] + [U("AMBIGUOUS")], f12)
    check(o["interpretation"] == "INSTRUMENT", "map 3")
    o = IDM.outcomes([U("UNIQUE"), U("AMBIGUOUS"), U("NO_STONE")], f12)
    check(o["interpretation"] == "MIXED" and o["ID_IDENTIFIABILITY"]["labelled"] == 2, "tie -> MIXED, NO_STONE excl.")
    check(IDM.outcomes([U("AMBIGUOUS", und=False)], f12)["interpretation"] == "NOT_APPLICABLE", "no UND units")
    inc = [dict(f) for f in f12]
    inc[0] = {"family_id": "F"}
    check(IDM.outcomes(amb, inc)["ID_RETENTION_REPAIR"] == "INCOMPLETE", "incomplete")
    return {"cases": 7}


# ================================================================ E3-R (windows/E3R_PREREG.md): X-ABS + 2x2 REPAIR_CLASS
FROZEN_KP_BLOB = "2b9845fedec302737ac5b3da3ef94616d625d68a"     # FREEZE_E3KP git blob of e3_known_positive.py
KP_PRODUCTION = BETA04 / "runs" / "kp_production"
REVIEWER_CASES = [   # (world, mechanism, sealed mechanism as stated in reviews/INDEPENDENT_REVIEW_RESULTS_v1.md F2)
    ("W483b8c31", "f0", "(lam x (add 2 (mul x x)))"),
    ("W6eb945cc", "f0", "(lam x (sub 1 (mul x x)))"),
    ("Wb49b6a5f", "f1", "(lam x (mul (mul x x) 3))")]


def _frozen_kp_module():
    import importlib.util
    src = subprocess.run(["git", "cat-file", "-p", FROZEN_KP_BLOB], capture_output=True, text=True, cwd=str(BETA04),
                         check=True).stdout
    spec = importlib.util.spec_from_loader("kp_frozen_blob", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__dict__["__file__"] = KP.__file__          # the frozen module locates HERE = tfs1/e3 from its own path
    exec(compile(src, "kp_frozen_blob", "exec"), mod.__dict__)
    return mod


def _probe_beh(lam_text):
    t = C.parse(lam_text)
    return [C.evaluate(("app", t, ("int", v)), [])[0] for v in range(-40, 41)]


@test
def test_e3r_frozen_extraction_and_keys_byte_identical():
    """The frozen E3-KP rule is unchanged: extract_mechanism (default and fallback off) equals the FROZEN blob's on
    every dev-consistent pilot R1 program (E3-ID enumerations) and every stored production R1 / chain program; frozen
    Config keys and row JSON are unchanged; the pilot primary units re-derive identically from the cached searches."""
    F = _frozen_kp_module()
    progs = set()
    for p in (HERE / "runs").glob("ID_W*.json"):
        for e in json.loads(p.read_text())["enumerations"].values():
            progs |= {h[1] for h in e["hits"]}
    for p in KP_PRODUCTION.glob("KPA1_W*.json"):
        for r in json.loads(p.read_text())["searches"].values():
            if r.get("program"):
                progs.add(r["program"])
    n = 0
    for prog in sorted(progs):
        for kind in ("f", "p", "s"):
            for fb in (True, False):
                a, b = KP.extract_mechanism(prog, kind, fallback=fb), F.extract_mechanism(prog, kind, fallback=fb)
                check((a is None and b is None) or (a is not None and b is not None and a == b),
                      "extraction differs from the frozen blob on %s/%s" % (prog, kind))
                n += 1
    for kw in ({}, {"fallback": False}, {"source": "foundry"}, {"scope": "all"}, {"seed": 2}, {"oe": True},
               {"budget": 20000}):
        check(KP.Config(**kw).key() == F.Config(**kw).key(), "frozen key changed %r" % kw)
        check(KP.Config(**kw).to_json() == F.Config(**kw).to_json(), "frozen to_json changed %r" % kw)
    check(KP.Config(extract="xabs").key() == KP.PRIMARY.key() + ".x-xabs", "xabs key")
    # the pilot primary units re-derive identically (all searches cached: no search runs)
    d = json.loads((HERE / "runs" / "KPA1_W1d5301d0.json").read_text())
    kp = KP.KP(str(ROOT), WORLD)
    n_s = len(d["searches"])
    for m, u in d["rows"][KP.PRIMARY.key()]["units"].items():
        check(kp.run_unit(d, m, KP.PRIMARY) == u, "unit %s re-derives differently" % m)
    check(len(d["searches"]) == n_s, "a search was run")
    return {"programs": len(progs), "comparisons": n, "frozen_blob": FROZEN_KP_BLOB}


@test
def test_e3r_xabs_reviewer_cases_from_stored_production_programs():
    """X-ABS on the 3 reviewer mis-cut units: the R1 programs are LOADED from runs/kp_production (no search on
    production; the R1 dev INPUTS are read for the validity check); X-ABS gives a stone equal to the sealed mechanism
    on [-40, 40], while the frozen rule still gives the mis-cut map body."""
    out = {}
    for world, m, sealed in REVIEWER_CASES:
        d = json.loads((KP_PRODUCTION / ("KPA1_%s.json" % world)).read_text())
        u = d["rows"][KP.PRIMARY.key()]["units"][m]
        prog, fid = u["attempts"][-1]["found"], u["from"]
        ev = WD.Evaluator(str(BETA04 / "foundry" / "production"), world)
        by = {mm["family_id"]: o for o, mm in ev.id_map.items()}
        dev = [i for i, _o in ev.task(by[fid])["dev"]]
        fr = KP.extract_mechanism(prog, "f")
        xa = KP.extract_mechanism(prog, "f", mode="xabs", dev_inputs=dev)
        check(C.to_str(fr[0]) == u["lambda"], "frozen rule changed on %s" % world)
        check(_probe_beh(C.to_str(fr[0])) != _probe_beh(sealed), "frozen stone unexpectedly sealed-equivalent")
        check(xa[1] == "xabs_absorbed" and _probe_beh(C.to_str(xa[0])) == _probe_beh(sealed),
              "X-ABS stone %s not sealed-equivalent on %s" % (C.to_str(xa[0]), world))
        out[world + "/" + m] = {"program": prog, "frozen": C.to_str(fr[0]), "xabs": C.to_str(xa[0])}
    # kinds p / s: X-ABS = the frozen rule
    for prog, kind in (("(len (filter (lam x (gt (sub x 2) 3)) xs))", "p"),
                       ("(foldl (lam a (lam b (sub b (div a 3)))) 0 xs)", "s")):
        check(KP.extract_mechanism(prog, kind, mode="xabs", dev_inputs=[[1, 2]]) == KP.extract_mechanism(prog, kind),
              "p/s must use the frozen rule")
    return out


@test
def test_e3r_xabs_validity_rejects_non_equivalent_absorption():
    """A non-monotone context ((mod [] 3) around max) is a type-valid, closed, xs-free candidate but NOT equivalent:
    it agrees on the dev inputs and is rejected by the 200 seeded probe lists, so X-ABS falls back to the frozen rule.
    A monotone-decreasing context is accepted only through the dual reducer; head contexts always absorb."""
    prog = "(mod (max (map (lam x (add x 1)) xs)) 3)"
    dev = [[2], [3, 7]]
    t = C.parse(prog)
    cands = KP.xabs_candidates(t)
    check(len(cands) == 1 and C.to_str(cands[0]["stone"]) == "(lam x (mod (add x 1) 3))", "candidate")
    p2 = ("max", ("map", cands[0]["stone"], ("xs",)))
    check(KP._agree_all(t, p2, dev), "construction: the absorption must agree on dev")
    check(not KP._agree_all(t, p2, dev + KP.xabs_probe_lists(dev)), "probes must expose it")
    check(KP.xabs_extract(prog, "f", dev) is None, "non-equivalent absorption accepted")
    ex = KP.extract_mechanism(prog, "f", mode="xabs", dev_inputs=dev)
    check(ex == KP.extract_mechanism(prog, "f") and C.to_str(ex[0]) == "(lam x (add x 1))", "fallback to frozen")
    dec = KP.xabs_extract("(neg (max (map (lam x (add x 1)) xs)))", "f", [[1, 5, -2], [0, 3]])
    check(dec is not None and dec["reducer_used"] == "min", "decreasing context via the dual reducer")
    hd = KP.xabs_extract("(mod (head (map (lam x (add x 1)) xs)) 3)", "f", [[1, 5, -2], [0, 3]])
    check(hd is not None and C.to_str(hd["stone"]) == "(lam x (mod (add x 1) 3))", "head absorbs any context")
    nest = KP.xabs_extract("(add 1 (mul 2 (max (map (lam x (pow x 2)) xs))))", "f", [[1, 5, -2], [0, 3]])
    check(nest is not None and nest["absorbed"] == 4 and C.to_str(nest["stone"]) ==
          "(lam x (add 1 (mul 2 (pow x 2))))", "maximal absorption")
    xs_ctx = KP.xabs_candidates(C.parse("(add (len xs) (max (map (lam x (pow x 2)) xs)))"))
    check(not xs_ctx, "a context that reads xs is not absorbable")
    return {"rejected": prog, "probes": KP.XABS_N_PROBES}


@test
def test_e3r_bounds_labels_stability_and_readings():
    """A1 bounds (LO: CENSORED / NOT_RUN not failed; HI: failed), COUNTS_CONDITIONAL, TRIVIALISED, conditional label
    text with the unconditional (LO) label; the prereg label table; stability; fixed reading texts (A4, A5); claim
    limits (A12)."""
    from tfs1.e3 import e3r as R3

    def fams(q, n=15, fail=15, cen=0, nr=0, links=None):
        st = ["FAILED"] * fail + ["CENSORED"] * cen + ["NOT_RUN"] * nr
        st += ["SOLVED"] * (n - len(st))
        out = []
        for i in range(n):
            ok = i < q
            out.append({"world": "W", "family_id": "F%02d" % i, "qualified": ok, "complete": True,
                        "link": None if ok else "COMPOSITION_HORIZON", "detail": None if ok else "IN_CLASS",
                        "scratch": st[i], "scratch_secondary_non_oe": "FAILED"})
        return out
    cs = R3.cell_summary(fams(13, fail=10, cen=3), {})
    check(cs["scratch_fails_LO"] == 10 and cs["scratch_fails_HI"] == 13 and cs["COUNTS_CONDITIONAL"]
          and cs["counts_HI"] and not cs["counts_LO"] and cs["trivialised_LO"] and cs["n_censored"] == 3, "bounds")
    full = R3.cell_summary(fams(13), {})
    no = R3.cell_summary(fams(7), {})
    nine = R3.cell_summary(fams(9), {})

    def lab(**cells):
        base = {"off_frozen": no, "on_frozen": no, "off_xabs": nine, "on_xabs": no}
        base.update(cells)
        return R3.seed_label(base)
    check(lab(on_frozen=full)["reported"] == "SEARCH", "SEARCH")
    check(lab(on_xabs=full)["reported"] == "BOTH_REQUIRED", "BOTH_REQUIRED")
    check(lab()["reported"] == "NONE", "NONE")
    check(lab(off_xabs=full, on_frozen=full)["reported"] == "EITHER", "EITHER")
    check(lab(off_xabs=full)["reported"] == "DEVELOPMENTAL", "DEVELOPMENTAL")
    c = lab(on_frozen=cs)
    check(not c["determined"] and c["unconditional"] == "NONE" and c["label_HI"] == "SEARCH"
          and c["reported"].startswith("SEARCH (CONDITIONAL: 3 OE scratches censored at 3,600 CPU-s"), "CONDITIONAL")
    inc = dict(no, complete=False)
    check(lab(on_xabs=inc)["reported"] == "INCOMPLETE", "INCOMPLETE")
    check(R3.stability(["SEARCH"] * 3)["stability"] == "STABLE", "STABLE")
    m = R3.stability(["NONE", "SEARCH", "SEARCH"])
    check(m["stability"] == "MAJORITY" and m["label"] == "SEARCH", "MAJORITY")
    u = R3.stability(["NONE", "SEARCH", "BOTH_REQUIRED"])
    check(u["stability"] == "SEED_UNSTABLE" and u["label"] == "NONE", "SEED_UNSTABLE")
    # dominant link of the reading cell (strict majority; UD split)
    f = fams(10)
    for i in range(10, 13):
        f[i].update(link="UNDERDETERMINED_STONE", ud={"ud": "UD-R1"})
    check(R3.dominant(f)["dominant"] == "UD-R1", "UD-R1 dominant (3 of 5)")
    f[12]["ud"] = {"ud": "UD-EXTRACT"}
    d = R3.dominant(f)
    check(d["dominant"] == "MIXED" and d["residual_links"]["UNDERDETERMINED_STONE/UD-R1"] == 2, "MIXED")
    check(R3.dominant(fams(10))["dominant"] == "HORIZON", "HORIZON")
    check("NOT a CHANGE_SEARCH finding" in R3.INTERPRETATION["NONE/HORIZON"]
          and "OE + post-hoc patch" in R3.INTERPRETATION["BOTH_REQUIRED"]
          and "WORLD" in R3.INTERPRETATION["NONE/UD-R1"]
          and "DEVELOPMENTAL coverage" in R3.INTERPRETATION["NONE/UD-EXTRACT"]
          and "does NOT discriminate CHANGE vs MIGRATE" in R3.SCOPE and R3.READING_CELL == "on_xabs", "texts")
    check(any("lifetime gate" in x for x in R3.CLAIM_LIMITS["may_not_claim"])
          and any("A1-A.5" in x for x in R3.CLAIM_LIMITS["may_not_claim"]), "claim limits")
    return {"cases": 22}


@test
def test_e3r_attribution_effects_masking_ud_split():
    from tfs1.e3 import e3r as R3

    def F(fid, q, link="COMPOSITION_HORIZON"):
        return {"world": "W", "family_id": fid, "qualified": q, "link": None if q else link, "detail": "IN_CLASS"}
    cells = {"off_frozen": [F("a", True), F("b", False), F("c", False), F("d", False), F("e", False), F("f", False)],
             "on_frozen": [F("a", True), F("b", True), F("c", False), F("d", True), F("e", False), F("f", True)],
             "off_xabs": [F("a", True), F("b", False), F("c", True), F("d", True), F("e", False), F("f", False)],
             "on_xabs": [F("a", True), F("b", True), F("c", True), F("d", True), F("e", False), F("f", False)]}
    at = R3.attribution(cells)
    cat = {r["family_id"]: r["category"] for r in at["families"]}
    check(cat == {"b": "OE-only", "c": "X-ABS-only", "d": "either", "e": "neither", "f": "OE-only"}, cat)
    check([r for r in at["families"] if r["family_id"] == "f"][0].get("note"), "interaction note")
    check([r for r in at["families"] if r["family_id"] == "e"][0]["residual_link"] == "COMPOSITION_HORIZON", "")
    cells["on_xabs"][4] = F("e", True)
    check({r["family_id"]: r["category"] for r in R3.attribution(cells)["families"]}["e"] == "both-only", "both-only")
    cs = {c: {"chain_qualified": sum(f["qualified"] for f in v)} for c, v in cells.items()}
    e = R3.effects(cs)
    check(e["interaction"] == 5 - 4 - 3 + 1 and e["OE_main_effect"] == (4 + 5 - 1 - 3) / 2, "effects")
    mk = R3.masking({"W/f0": {"lambda": "(lam x (pow x 2))", "status": "ACQUIRED"}},
                    {"W/f0": {"lambda": "(lam x (add 2 (pow x 2)))", "status": "ACQUIRED",
                              "extraction": "xabs_absorbed"}})
    check(mk["xabs_changed_any_stone_in_OE_cells"] and mk["units_changed"] == ["W/f0"], "masking")
    # UD split and the post-hoc global-equivalence check (the reviewer's F2 method)
    g = R3.global_equivalence("(add 2 (max (map (lam x (pow x 2)) xs)))", "(max (map (lam x (add 2 (mul x x))) xs))")
    check(g["globally_equivalent"] and g["n_lists"] == 1 + 401 + 20000, "globally equivalent")
    g2 = R3.global_equivalence("(len (filter (lam x (gt (sub x 2) 3)) xs))", "(len (filter (lam x (gt x 4)) xs))")
    check(not g2["globally_equivalent"] and g2["n_differ"] > 0, "x > 5 vs x > 4")
    kp = KP.KP(str(ROOT), WORLD)
    check(R3.ud_split(kp, {}, {"detail": "R1_FIRST_DEV_CONSISTENT_FAILS_TEST", "unit": "p0"})["ud"] == "UD-R1", "")
    fid = kp.r1_families("f1")[0]
    units = {"f1": {"from": fid, "lambda": "(lam x x)", "attempts": [{"family_id": fid,
                                                                      "found": kp.fams[fid]["witness"]}]}}
    us = R3.ud_split(kp, units, {"detail": "STONE_DISAGREES_SEALED_PROBES", "units": ["f1"]})
    check(us["ud"] == "UD-EXTRACT" and us["units"]["f1"]["global_equivalence_vs_sealed_r1_witness"]
          ["globally_equivalent"], "UD-EXTRACT with global equivalence")
    return {"tally": at["tally"], "effects": e}


@test
def test_e3r_xabs_singleton_probes_and_arm_view_assert():
    lists = KP.xabs_probe_lists([[3, -2], [5]])
    check(len(lists) == KP.XABS_N_PROBES + 8 and lists[-8:] == [[v] for v in range(-2, 6)], "singletons")
    check(all(0 <= len(x) <= 2 and all(-2 <= v <= 5 for v in x) for x in lists[:KP.XABS_N_PROBES]), "random part")
    kp = KP.KP(str(ROOT), WORLD)
    fid = kp.r1_families("f1")[0]
    check(kp.dev_inputs_checked(fid) == [i for i, _o in kp.task(fid)["dev"]], "arm view equal")
    kp.task(fid)["dev"][0] = [[999], kp.task(fid)["dev"][0][1]]          # tamper the (cached) evaluator dev
    try:
        kp.dev_inputs_checked(fid)
        raise AssertionError("tampered evaluator dev not detected")
    except AssertionError as e:
        check("differ from the arm view" in str(e), "assert message")
    return {"probe_lists": len(lists)}


@test
def test_e3r_capped_scratch_censored_cached_and_extension():
    """A1: an OE scratch above its cap is CENSORED (third state), cached per search key and re-used at the same cap;
    a larger cap (the one extension) re-runs it. Tiny caps on EXPOSED pilot_v2 (the child is this test's own process)."""
    from tfs1.e3 import e3r as R3
    kp = KP.KP(str(ROOT), WORLD)
    fid = kp.admitted()[0]
    cfg = KP.Config(oe=True)
    d = {"searches": {}, "rows": {}}
    r = KP.run_scratch_capped(kp, d, fid, cfg, 0.3)
    check(r["status"] == "CENSORED" and r["cap_s"] == 0.3, "censored")
    check(R3.scratch_state(d, fid, True, KP.BUDGET)["state"] == "CENSORED", "third state")
    r2 = KP.run_scratch_capped(kp, d, fid, cfg, 0.3)
    check(r2.get("reused_censored_search"), "censoring re-used")
    r3 = KP.run_scratch_capped(kp, d, fid, cfg, 0.6)
    check(r3["status"] == "CENSORED" and r3["cap_s"] == 0.6 and not r3.get("reused_censored_search"), "extension")
    return {"family": fid, "cpu_s": [r["cpu_s"], r3["cpu_s"]]}


@test
def test_e3r_lazy_scratch_order_and_stop_rule():
    """A1.4 / A1.5: OE scratch is run only while NEEDED and not DETERMINED, in the fixed order (Int-output families
    first, then family_id), skipping searches already decided or censored at >= this cap; the OE-scratch envelope
    blocks a start."""
    from tfs1.e3 import e3r_run as DR
    import types
    with tempfile.TemporaryDirectory() as td:
        a = types.SimpleNamespace(root=str(ROOT), kp_frozen=td, out=td, worlds="W1d5301d0,W0467897d", workers=1,
                                  budget=1000, deadline="2099-01-01T00:00Z", not_before="2000-01-01T00:00Z",
                                  envelope_core_h=14.0, debit_core_h=0.0, oe_scratch_envelope_core_h=16.0,
                                  min_free_gb=0.0, expect_off_frozen=None, expect_off_xabs=None,
                                  with_fallback_off=False)
        dr = DR.Driver(a)
        order = dr.scratch_order()
        types_ = [KP.KP(str(ROOT), w).task(f)["output_type"] for f, w in order]
        check(types_ == sorted(types_, key=lambda t: t != "Int"), "Int-output first")
        check([f for f, _w in order if KP.KP(str(ROOT), _w).task(f)["output_type"] == "Int"] ==
              sorted(f for f, _w in order if KP.KP(str(ROOT), _w).task(f)["output_type"] == "Int"), "family order")
        ran = []
        dr.run_jobs = lambda jobs, gate=None: ran.extend(j["name"] for j in jobs)
        state = {"n": 0}

        def nd():
            state["n"] += 1
            return True, state["n"] > 3, None
        dr.need_and_determined = nd
        dr.lazy_scratch(3600.0)
        check(len(ran) == 3 and ran[0].endswith("%s/%s/cap3600" % (order[0][1], order[0][0])), ran)
        ran.clear()
        dr.need_and_determined = lambda: (False, False, None)
        dr.lazy_scratch(3600.0)
        check(not ran, "not needed -> nothing runs")
        dr.need_and_determined = lambda: (True, False, None)
        dr.state["ledger_s"]["oe_scratch"] = 16 * 3600.0 - 100
        dr.lazy_scratch(3600.0)
        check(not ran and any("envelope" in n for n in dr.state.get("notes", [])), "envelope blocks")
    return {"order": order}


@test
def test_e3r_driver_end_to_end_resumable_hard_stop_and_custody():
    """The A9 driver on EXPOSED pilot_v2, one world, B = 2e4, 1 worker: hard stop in the past -> nothing runs and the
    label is INCOMPLETE; a full run completes (reproduction checks pass: off_frozen == the frozen pooled file and the
    asserted count); re-invoking runs NO new search (resumable); UTC start / end in the result and world files; the
    claim-limits block is present."""
    from tfs1.e3 import e3r_run as DR
    import types
    B, W = 20000, "W1d5301d0"
    with tempfile.TemporaryDirectory() as td:
        fz, out = Path(td) / "frozen", Path(td) / "run"
        KP.run_stages(str(ROOT), W, KP.Config(budget=B), "all", str(fz), log=lambda s: None)
        (fz / ("KPA1_POOLED_%s.json" % KP.Config(budget=B).key())).write_text(json.dumps(
            KP.pooled(str(ROOT), [W], KP.Config(budget=B), str(fz))))
        q0 = KP.pooled(str(ROOT), [W], KP.Config(budget=B), str(fz))["verdict"]["chain_qualified"]

        def args(deadline):
            return types.SimpleNamespace(root=str(ROOT), kp_frozen=str(fz), out=str(out), worlds=W, workers=1,
                                         budget=B, deadline=deadline, not_before="2000-01-01T00:00Z",
                                         envelope_core_h=14.0, debit_core_h=0.0, oe_scratch_envelope_core_h=16.0,
                                         min_free_gb=0.0, expect_off_frozen=q0, expect_off_xabs=None,
                                         with_fallback_off=True)
        r0 = DR.Driver(args("2000-01-01T00:00Z")).go()
        check(r0["driver_status"] == "HARD_STOP" and r0["REPAIR_CLASS"] == "INCOMPLETE", "hard stop")
        r1 = DR.Driver(args("2099-01-01T00:00Z")).go()
        check(r1["driver_status"] == "COMPLETE", r1["driver_status"])
        chk = r1["reproduction_checks"]
        check(chk["off_frozen_equals_frozen_pooled"] and chk["off_frozen_assert"]["pass"], chk)
        check(all(r1["per_seed"][s]["cells"][c]["complete"] for s in (0, 1, 2) for c in R3_CELLS()), "complete")
        check(r1["fallback_off_on_xabs"] is not None, "priority-2 row")
        led = json.loads((out / "E3R_STATE.json").read_text())["ledger_s"]
        fzk = set(json.loads((fz / ("KPA1_%s.json" % W)).read_text())["searches"])
        new_cpu = sum(v.get("cpu_s", 0) for k, v in KP._load(str(out), W)["searches"].items() if k not in fzk)
        check(abs(sum(led.values()) - new_cpu) < 1.0, "ledger %r != new-search CPU %.1f" % (led, new_cpu))
        n_search = len(KP._load(str(out), W)["searches"])
        r2 = DR.Driver(args("2099-01-01T00:00Z")).go()
        check(len(KP._load(str(out), W)["searches"]) == n_search and r2["REPAIR_CLASS"] == r1["REPAIR_CLASS"],
              "resume ran new searches")
        check(json.loads((out / "E3R_STATE.json").read_text())["ledger_s"] == led, "resume debited CPU")
        wf = KP._load(str(out), W)
        check(r1["utc_start"] and r1["utc_end"] and wf.get("utc_last_write") and all(
            v.get("utc_start") for k, v in wf["searches"].items() if k not in json.loads(
                (fz / ("KPA1_%s.json" % W)).read_text())["searches"]), "UTC custody")
        check(r1["claim_limits"]["may_not_claim"] and r1["scope"], "claim limits")
    return {"label": r1["REPAIR_CLASS"], "stability": r1["stability"], "ledger_s": led}


def R3_CELLS():
    from tfs1.e3 import e3r as R3
    return R3.CELLS


def _run(fn):
    t0 = time.perf_counter()
    try:
        info = fn() or {}
        st = "PASS"
    except Exception as e:                    # noqa: BLE001
        info = {"error": repr(e), "trace": traceback.format_exc()[-1500:]}
        st = "FAIL"
    info["status"] = st
    info["seconds"] = round(time.perf_counter() - t0, 1)
    RESULTS[fn.__name__] = info
    print("%-45s %s %s" % (fn.__name__, st, {k: v for k, v in info.items() if k != "trace"}), flush=True)


if __name__ == "__main__":
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    for fn in TESTS:
        if not only or fn.__name__ in only:
            _run(fn)
    s = {"pass": sum(r["status"] == "PASS" for r in RESULTS.values()),
         "fail": sum(r["status"] == "FAIL" for r in RESULTS.values()), "code_sha256": code_hashes(),
         "data": "EXPOSED pilot_v2 (development only)"}
    out = HERE / ("E3_TEST_RESULTS%s.json" % ("_PARTIAL" if only else ""))
    out.write_text(json.dumps({"summary": s, "tests": RESULTS}, indent=1, sort_keys=True, default=str))
    print(s["pass"], "PASS", s["fail"], "FAIL ->", out)
    sys.exit(1 if s["fail"] else 0)
