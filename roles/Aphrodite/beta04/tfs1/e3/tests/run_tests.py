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
