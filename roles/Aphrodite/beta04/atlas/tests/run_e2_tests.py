"""E2 driver / analyzer tests (EXPOSED foundry/pilot_v2 data and toys only; nothing runs on production families).
Writes atlas/E2_TEST_RESULTS.json.

Run from roles/Aphrodite/beta04:  OMP_NUM_THREADS=1 python -m atlas.tests.run_e2_tests
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from itertools import product
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
from tfs1 import core as C                         # noqa: E402
from tfs1.enum import Enumerator, canon_comm        # noqa: E402
from tfs1.mutate import rng_for                     # noqa: E402
from tfs1.e3 import worlds as WD                    # noqa: E402

from atlas import arms as A                         # noqa: E402
from atlas import common as K                       # noqa: E402
from atlas import e2_analyze as AN                  # noqa: E402
from atlas import e2_driver as D                    # noqa: E402
from atlas import e2_project as P                   # noqa: E402
from atlas import toys                              # noqa: E402

HERE = Path(__file__).resolve().parent.parent
BETA04 = HERE.parent
PILOT = BETA04 / "foundry" / "pilot_v2"
PROD = BETA04 / "foundry" / "production"
RESULTS = []
R = D.E2Root(PILOT)
F_HIT = "W0467897d-F085-R3"          # exposed guard_p family (D-BEH QUALIFIED on pilot_v2)
F_B = "W0467897d-F061-R3"


def test(fn):
    def run():
        t0 = time.process_time()
        try:
            info = fn()
            RESULTS.append({"test": fn.__name__, "pass": True, "info": info,
                            "cpu_s": round(time.process_time() - t0, 1)})
            print("PASS", fn.__name__, flush=True)
        except Exception:                                   # noqa: BLE001
            RESULTS.append({"test": fn.__name__, "pass": False, "error": traceback.format_exc(),
                            "cpu_s": round(time.process_time() - t0, 1)})
            print("FAIL", fn.__name__, traceback.format_exc(), flush=True)
    run.__name__ = fn.__name__
    return run


def _lt(fid):
    return R.learner_task(fid)


@test
def fast_restore_bit_identical():
    """E2 performance repair: the incremental weighted cell choice reproduces random.choices exactly."""
    cases = []
    T, lib = toys.all_toys()["GRADED"]
    tv = K.LearnerView(T)
    fs = D.FamilySetup(R, F_B)
    pv = K.LearnerView(_lt(F_B))
    for (view, lib_), (arm, desc), sd in product([(tv, lib), (pv, fs.lib)],
                                                 [("D1-X3", "D-BEH"), ("D1-X3G", "RAND:700"), ("D1-X2", "D-BEH"),
                                                  ("B2-DESCSEL", "D-BEH"), ("C2-RAND", "RAND:90")], (0, 1)):
        hs = []
        for ref in (True, False):
            s = A.Search(view, None, Enumerator(lib_), arm, sd, 3000, 10, desc, stop_on_hit=False, max_size=28)
            s.reference_restore = ref
            s.run()
            hs.append((s.loghash.hexdigest(), s.realised_cells(), s.restores))
        assert hs[0] == hs[1], (arm, sd, hs)
        cases.append(arm)
    return {"cases_identical": len(cases)}


@test
def arm_table_at_code_level():
    m = {a: (v["code"], v["credit"], v["library"]) for a, v in D.ARMS.items()}
    assert m == {"credit_blind": ("D1-chain_neutral", "none", True), "chain_strict": ("D1-chain_strict", "exact", True),
                 "chain_neutral": ("D1-chain_neutral", "exact", True), "D1-X3": ("D1-X3", "exact", True),
                 "X3G": ("D1-X3G", "exact", True), "desert_ref": ("D1-chain_neutral", "none", False)}, m
    assert D.ARMS["D1-X3"]["descriptor"] == "D-BEH" and D.ARMS["X3G"]["descriptor"] == "RAND:K"
    assert D.CONFIG["budget"] == 200_000 and D.CONFIG["seeds"] == list(range(8)) and D.CONFIG["max_size"] >= 28
    fs = D.FamilySetup(R, F_B)
    lt = _lt(F_B)
    # credit_blind: every non-all-FAIL child is accepted (key 0); chain_strict: only strict improvements
    for arm in ("credit_blind", "desert_ref", "chain_strict", "chain_neutral"):
        spec = D.ARMS[arm]
        lib = fs.lib if spec["library"] else None
        s = A.Search(K.LearnerView(lt), None, Enumerator(lib), spec["code"], 0, 600, 1, None, stop_on_hit=False,
                     max_size=D.CONFIG["max_size"], credit=spec["credit"])
        last = {}
        orig = s._evaluate

        def ev(t, _o=orig, _l=last):
            r = _o(t)
            _l["t"], _l["r"] = t, r
            return r
        s._evaluate = ev
        while not s.done:
            before = s.cur
            last.clear()
            s.step()
            if "r" not in last or before is None:          # before is None: the chain's single restore step
                continue
            r = last["r"]
            moved = s.cur[0] is last["t"]
            if arm in ("credit_blind", "desert_ref"):
                assert r["key"] == 0 and moved == (not r["allfail"]), arm
            elif arm == "chain_strict":
                assert moved == ((not r["allfail"]) and r["key"] > before[1])
            else:
                assert moved == ((not r["allfail"]) and r["key"] >= before[1])
        assert s.mut.max_size == D.CONFIG["max_size"]
        if arm == "desert_ref":
            assert s.lib is None
    # matched restore frequency X3 vs X3G (L = 1: one restore per charged child); chains restore once; CRN
    res = {}
    for arm, desc in (("D1-X3", "D-BEH"), ("D1-X3G", "RAND:500"), ("D1-chain_neutral", None)):
        s = A.Search(K.LearnerView(lt), None, Enumerator(fs.lib), arm, 3, 1500, 1, desc, stop_on_hit=False,
                     max_size=28)
        st0 = s.rng.getstate()
        s.run()
        res[arm] = (s.restores, s.charges - len(s.starts))
        assert st0 == rng_for(3, lt["family_id"]).getstate()
    assert res["D1-X3"] == res["D1-X3G"] and res["D1-X3"][0] == res["D1-X3"][1], res
    assert res["D1-chain_neutral"][0] == 1
    return {"restores": res}


@test
def search_sees_arm_view_only():
    log = WD.AccessLog()
    with log.active():
        lt = R.learner_task(F_B)
    assert not log.outside(PILOT / "arm_view"), log.paths
    assert set(lt) == {"family_id", "output_type", "dev", "arm_view_file_sha256"}
    m = R.meta[F_B]
    man = json.loads((PILOT / "arm_view" / "ARM_VIEW_MANIFEST.json").read_text())
    rel = "arm_view/%s/%s.json" % (m["arm_world"], m["opaque"])
    assert man["worlds"][m["arm_world"]]["files"][rel] == lt["arm_view_file_sha256"]
    assert lt["family_id"] == m["slot"] and F_B not in json.dumps(lt)          # opaque slot, never the family id
    view = K.LearnerView(lt)
    assert not hasattr(view, "test") and lt["dev"] == R.eval_task(F_B)["dev"]
    return {"files_read": len(log.paths), "slot": lt["family_id"]}


@test
def library_is_foundry_acquired_constituents():
    rows = []
    differs = 0
    for f in R.admitted(("R3", "R4")):
        fs = D.FamilySetup(R, f)
        info = fs.info
        W = info["world"]
        sealed = {x["name"]: x["term"] for x in R.sealed(W)["mechanisms"]}
        acq = R.acquired(W)["acquired"]
        sf = R.sealed_family(f)
        assert info["constituents"] == sf["mechanisms_used"]
        assert sorted(fs.lib_ids) == sorted(info["constituents"]) and len(fs.lib) == len(set(fs.lib_ids.values()))
        for mname, eid in fs.lib_ids.items():
            e = fs.lib.entries[eid]
            want = C.to_str(canon_comm(fs.lib.expand((eid,) + tuple(("hole", j) for j in range(len(e.params))))))
            lam = C.parse(acq[mname]["term"])
            from tfs1.library import lambda_to_body
            body, _k = lambda_to_body(lam)
            assert C.to_str(canon_comm(body)) == want, (f, mname)
            differs += acq[mname]["term"] != sealed[mname]
        assert fs.lib_witness is not None and fs.certify(fs.lib_witness, fs.lib)["qualified"]
        rows.append((f, fs.lib_witness_source))
    assert differs > 0                       # the acquired (learner-found) terms are not the sealed spellings
    return {"families": len(rows), "acquired_term_differs_from_sealed": differs}


@test
def certifier_task_tribunal_value_or_fail():
    """Regression for the pre-launch finding: an expected FAIL in the task's own tribunal must be matched."""
    t = K.load_task({"family_id": "T-FAIL", "output_type": "Int", "dev": [[[1, 2], 1], [[5, 3], 3]],
                     "test": [[[4, 9], 4], [[7, 1], 1]], "tribunal": [[[], "FAIL"], [[2, 8], 2]]})
    assert K.Certifier(t, None, "(min xs)").verify(C.parse("(min xs)"))
    assert not K.Certifier(t, None, "(min xs)").verify(C.parse("(head (rev (rev xs)))"))   # agrees on test, not []
    return "ok"


@test
def endpoint_primary_secondary_and_rederivation():
    fid = spur = None
    for f in R.admitted(("R3", "R4")):          # an Int family whose sum-keyed dev lookup is dev-consistent
        fs = D.FamilySetup(R, f)
        for pr in D.control_programs(fs.task):
            t = C.parse(pr["program"])
            if pr["kind"].startswith("lookup") and K.exact_credit(K.outs_of(t, [i for i, _ in fs.task["dev"]]),
                                                                  [o for _, o in fs.task["dev"]]) == len(fs.task["dev"]):
                fid, spur = f, pr["program"]
                break
        if fid:
            break
    assert fid is not None
    fs = D.FamilySetup(R, fid)
    lt = _lt(fid)
    out = {"family": fid}
    for name, starts, want in (("direct", [fs.lib_witness], (True, True, False, True)),
                               ("after_spurious", [spur, fs.lib_witness], (False, True, True, True))):
        r = D.run_search(lt, fs.task, fs.lib, "chain_neutral", 0, 50, fs.witness, starts=starts)
        r.pop("_search")
        got = (r["primary_hit"], r["secondary_hit"], r["certifier_assisted"], r["start_hit"])
        assert got == want, (name, got)
        shard = dict(r, family_id=fid, arm="chain_neutral", shard="t/%s" % name)
        rd = AN.Rederiver(PILOT).check(shard)
        assert (rd["primary_hit"], rd["secondary_hit"], rd["certifier_assisted"], rd["start_hit"]) == want
        bad = json.loads(json.dumps(shard, default=str))
        bad["primary_hit"] = not bad["primary_hit"]
        try:
            AN.Rederiver(PILOT).check(bad)
            raise AssertionError("tampered runner field accepted")
        except AN.Mismatch:
            pass
        out[name] = got
    return out


def _mini_screen(tmp: Path, families, seeds, budget, workers=2):
    plan = D.make_plan(R, tmp, n_seeds=seeds, budget=budget, families=families)
    for ph in ("qual", "kcal", "run"):
        D.run_shards(D.shards_for(plan, tmp, ph), workers, log=lambda *_: None)
    return plan


@test
def screen_resumable_deterministic_and_analyzer_rederives():
    tmp = Path(tempfile.mkdtemp(prefix="e2t_"))
    try:
        plan = _mini_screen(tmp, [F_HIT], 2, 12_000)
        st = D.status(plan, tmp)
        assert st["run"]["done"] == st["run"]["total"] == 12 and not st["run"]["errors"], st
        # analyzer runs (atlas / prelaunch absent -> REACHABILITY_ATLAS_COMPLETE = NO), re-derivation clean
        rep = AN.analyze(tmp)
        assert rep["rederivation"]["mismatches"] == 0 and rep["REACHABILITY_ATLAS_COMPLETE"] == "NO"
        fam = rep["per_family"][F_HIT]
        # resumability + determinism: delete two results, re-run with ONE worker, identical science fields
        sids = sorted(plan["run_shards"])[:2]
        before = {s: D._read_json(D.shard_path(tmp, s)) for s in sids}
        for s in sids:
            D.shard_path(tmp, s).unlink()
        n = D.run_shards(D.shards_for(plan, tmp, "run"), 1, log=lambda *_: None)
        assert len(n) == 2
        strip = lambda d: {k: v for k, v in d.items() if k not in ("pid", "cpu_s", "shard_cpu_s")}   # noqa: E731
        for s in sids:
            assert strip(before[s]) == strip(D._read_json(D.shard_path(tmp, s))), s
        assert D.run_shards(D.shards_for(plan, tmp, "run"), 2, log=lambda *_: None) == []
        # tamper: a runner field -> exit 3; a stored component -> exit 3; a missing shard -> exit 2
        codes = {}
        victim = D.shard_path(tmp, sids[0])
        good = victim.read_text()
        for what in ("runner_field", "component"):
            d = json.loads(good)
            if what == "runner_field":
                d["primary_hit"] = not d["primary_hit"]
            else:
                cs = d["components"]["consultations_stored"]
                if cs:
                    cs[0]["test_ok"] = not cs[0]["test_ok"]
                else:
                    d["components"]["hit"] = {"program": "(len xs)", "charge": 5}
            victim.write_text(json.dumps(d))
            r = subprocess.run([sys.executable, "-m", "atlas.e2_analyze", "--out", str(tmp)], cwd=str(BETA04),
                               capture_output=True, text=True)
            codes[what] = r.returncode
        victim.unlink()
        r = subprocess.run([sys.executable, "-m", "atlas.e2_analyze", "--out", str(tmp)], cwd=str(BETA04),
                           capture_output=True, text=True)
        codes["incomplete"] = r.returncode
        assert codes == {"runner_field": 3, "component": 3, "incomplete": 2}, codes
        return {"arms": {a: v.get("primary_hits") for a, v in fam["arms"].items()}, "label": fam["label"],
                "exit_codes": codes}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test
def labels_known_answers():
    L = AN.label_family
    assert L({"credit_blind": 0, "chain_strict": 0, "chain_neutral": 0, "D1-X3": 0, "X3G": 0,
              "desert_ref": 0})["label"] == "DESERT_OR_HORIZON"
    r = L({"credit_blind": 0, "chain_strict": 1, "chain_neutral": 4, "D1-X3": None, "X3G": None, "desert_ref": 0})
    assert r["label"] == "REACHED" and r["flags"] == ["REACHED", "CREDIT_GRADIENT"], r
    assert L({"credit_blind": 0, "chain_strict": 3, "chain_neutral": 0, "D1-X3": 0, "X3G": 0,
              "desert_ref": 0})["label"] == "CREDIT_GRADIENT"
    r = L({"credit_blind": 5, "chain_strict": 1, "chain_neutral": 2, "D1-X3": 0, "X3G": 0, "desert_ref": 0})
    assert r["flags"] == ["REACHED", "CREDIT_MISLEADING"], r
    assert L({"credit_blind": 4, "chain_strict": 2, "chain_neutral": 0, "D1-X3": 0, "X3G": 0,
              "desert_ref": 1})["label"] == "UNRESOLVED"
    # truncation (chain_strict dropped): rules use the credit chain(s) actually run
    assert L({"credit_blind": 3, "chain_strict": None, "chain_neutral": 0, "D1-X3": None, "X3G": None,
              "desert_ref": 0})["label"] == "CREDIT_MISLEADING"
    return "ok"


@test
def frontier_known_answers():
    assert AN.flip_p([1, 1, 1, 1, 1])["p_one_sided"] == 1 / 32
    assert AN.flip_p([1, 1, 1, 1, -1])["p_one_sided"] >= 2 / 32
    assert AN.flip_p([1, 1, 1, 1, 0])["p_one_sided"] >= 2 / 32
    assert abs(AN.flip_p([2, 0.5, 1, 1.5, 1])["p_one_sided"] - 1 / 32) < 1e-12

    def fam(x3, ne, g, other=0):
        mk = lambda h: {"status": "RUN", "primary_hits": h}                     # noqa: E731
        return {"arms": {"D1-X3": mk(x3), "chain_neutral": mk(ne), "X3G": mk(g), "credit_blind": mk(other),
                         "desert_ref": mk(0)}}
    clusters = {"f%d" % i: "u%d" % (i % 5) for i in range(10)}
    yes = {f: fam(3, 0, 1) for f in clusters}
    assert AN.frontier(yes, clusters)["FRONTIER_ARCHIVE_EFFECT"] == "YES_SCREEN"
    zero = {f: fam(0, 0, 0) for f in clusters}
    z = AN.frontier(zero, clusters)
    assert z["FRONTIER_ARCHIVE_EFFECT"] == "INCONCLUSIVE_CENSORED" and z["informative_units"] == 0  # never NO
    four = dict(yes)
    for f in ("f4", "f9"):
        four[f] = fam(0, 0, 0)
    assert AN.frontier(four, clusters)["FRONTIER_ARCHIVE_EFFECT"] == "INCONCLUSIVE_CENSORED"
    no = {f: fam(0, 2, 0) for f in clusters}
    assert AN.frontier(no, clusters)["FRONTIER_ARCHIVE_EFFECT"] == "NO"
    mixed = dict(yes)
    mixed["f0"] = fam(0, 5, 0)
    mixed["f5"] = fam(0, 5, 0)
    assert AN.frontier(mixed, clusters)["FRONTIER_ARCHIVE_EFFECT"] == "INCONCLUSIVE"
    un = dict(yes)
    un["f1"] = {"arms": {"D1-X3": {"status": "INSTRUMENT_UNVALIDATED"}, "chain_neutral": {"status": "RUN",
                                                                                         "primary_hits": 0}}}
    fr = AN.frontier(un, clusters)
    assert "f1" in fr["instrument_unvalidated_or_not_run"] and "f1" not in fr["population"]
    return "ok"


@test
def cluster_units_from_witness_skeletons():
    labels = ["R3:fp:map_of_filter"] * 4 + ["R4:fp:map_of_filter"] * 2 + ["R3:fp:guard_p", "R4:fp:guard_p",
              "R4:fp:guard_p"] + ["R3:fp:filter_of_map", "R4:fp:filter_of_map"] + ["R4:fs:post_fold",
              "R3:fs:post_fold"] + ["R4:fs:scan_of_map", "R3:fs:scan_of_map"]
    from collections import Counter
    c = Counter(D.cluster_of(x) for x in labels)
    assert sorted(c.values()) == [2, 2, 2, 3, 6] and len(c) == 5, c
    assert D.cluster_of("R3:fs:fold_of_map") == D.cluster_of("R4:fs:step_of_f") == "fs:scan_of_map"
    assert D.cluster_of("R3:fp:map_of_filter+red") == "fp:map_of_filter"
    assert D.cluster_of("R3:ff:compose") == D.cluster_of("R3:ff:two_maps")
    # production: structure only (sealed skeleton labels of the admitted R3/R4 set; no arm or search is run)
    RP = D.E2Root(PROD)
    pc = Counter(RP.info(f)["cluster"] for f in RP.admitted(("R3", "R4")))
    assert len(RP.admitted(("R3", "R4"))) == 15 and len(pc) == 5, pc
    return {"production_clusters": dict(pc)}


@test
def plan_truncation_and_production_guards():
    tmp = Path(tempfile.mkdtemp(prefix="e2p_"))
    try:
        RP = D.E2Root(PROD)
        p = D.make_plan(RP, tmp)
        assert len(p["screen_families"]) == 15 and len(p["atlas_families"]) == 53
        assert len(p["run_shards"]) == 15 * 6 * 8 and p["budget"] == 200_000
        dd = [f for f in RP.admitted(("R3", "R4")) if (RP.final_rows(RP.meta[f]["world"])[f].get("base1e6") or {})
              .get("solved") is False]
        p2 = D.make_plan(RP, tmp, n_seeds=6, drop=["chain_strict"], drop_desert_ref_for=dd)
        assert len(p2["run_shards"]) == 15 * 6 * 4 + (15 - len(dd)) * 6
        for bad in ({"budget": 1000}, {"families": RP.admitted(("R3",))[:1]}):
            try:
                D.make_plan(RP, tmp, **bad)
                raise AssertionError("override accepted on production")
            except SystemExit:
                pass
        try:
            D.timing(RP, tmp, [], 1000, 10)
            raise AssertionError("timing accepted production")
        except SystemExit:
            pass
        return {"desert_ref_droppable": len(dd)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test
def projection_and_power():
    # exact P(X > Y and X > Z) vs brute force
    from math import comb
    n, p1, p0 = 4, 0.3, 0.1
    pm = lambda k, p: comb(n, k) * p ** k * (1 - p) ** (n - k)                 # noqa: E731
    bf = sum(pm(x, p1) * pm(y, p0) * pm(z, p0) for x in range(n + 1) for y in range(n + 1) for z in range(n + 1)
             if x > y and x > z)
    assert abs(bf - P.p_beats_both(n, p1, p0)) < 1e-12
    assert P.power([2, 2, 2, 2], 8, 0.9, 0.0) == 0.0          # < 5 clusters: YES impossible
    assert P.power(P.CLUSTER_SIZES_ALL, 8, 0.5, 0.0) > P.power(P.CLUSTER_SIZES_ALL, 8, 0.2, 0.0)
    timing = {"families": {"x": {"arms": {a: {"cpu_s_per_2e5": c} for a, c in
                                           (("credit_blind", 50), ("chain_strict", 85), ("chain_neutral", 80),
                                            ("D1-X3", 200), ("X3G", 145), ("desert_ref", 45))},
                                 "qual_cpu_s": 7, "atlas_cpu_s": 55,
                                 "kcal_probe": {"x3_cpu_s": 200, "x3g_cpu_s": 130}}}}
    pr = P.project(timing)
    d = pr["decision"]
    assert d["truncation_steps"] == ["1: drop chain_strict"] and d["within_cap"], d
    assert pr["screen_projection_by_qualified_count"]["0"]["truncation_steps"] == []
    return {"upper_bound_core_h": d["history"]}


@test
def prelaunch_checks_on_exposed_pilot():
    rep = D.prelaunch(R, Path(tempfile.gettempdir()), log=lambda *_: None)
    assert rep["pass"], rep["summary"]
    c = rep["checks"]
    assert all(r["counts_as_discovery"] is False and r["search_steps_charged"] == 0
               for r in c["start_at_target"]["rows"])
    assert all(c["target_blindness"]["certifier_channel_exercised_by_arm"].values())
    return rep["summary"]


def main():
    t0 = time.time()
    tests = [fast_restore_bit_identical, arm_table_at_code_level, search_sees_arm_view_only,
             library_is_foundry_acquired_constituents, certifier_task_tribunal_value_or_fail,
             endpoint_primary_secondary_and_rederivation, screen_resumable_deterministic_and_analyzer_rederives,
             labels_known_answers, frontier_known_answers, cluster_units_from_witness_skeletons,
             plan_truncation_and_production_guards, projection_and_power, prelaunch_checks_on_exposed_pilot]
    only = sys.argv[1:]
    for t in tests:
        if not only or t.__name__ in only:
            t()
    code = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))}
    res = {"suite": "atlas E2 driver tests", "pass": sum(r["pass"] for r in RESULTS),
           "fail": sum(not r["pass"] for r in RESULTS), "wall_s": round(time.time() - t0, 1),
           "code_sha256": code, "results": RESULTS}
    if not only:
        (HERE / "E2_TEST_RESULTS.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str))
    print("PASS %d / FAIL %d" % (res["pass"], res["fail"]))
    sys.exit(0 if res["fail"] == 0 else 1)


if __name__ == "__main__":
    main()
