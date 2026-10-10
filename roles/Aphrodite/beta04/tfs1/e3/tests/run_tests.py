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
    return {"cases": len(cases) + 2}


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
