"""ATLAS known-answer and instrument tests. Writes atlas/ATLAS_TEST_RESULTS.json.

Run from roles/Aphrodite/beta04:  OMP_NUM_THREADS=1 python -m atlas.tests.run_tests
"""
import copy
import hashlib
import inspect
import json
import math
import os
import random
import subprocess
import sys
import time
import traceback
from collections import Counter
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
from tfs1 import core as C                         # noqa: E402
from tfs1.enum import Enumerator, canon_comm        # noqa: E402
from tfs1.mutate import Mutator                     # noqa: E402

from atlas import arms as A                         # noqa: E402
from atlas import common as K                       # noqa: E402
from atlas import descriptors as D                  # noqa: E402
from atlas import measure as M                      # noqa: E402
from atlas import route as R                        # noqa: E402
from atlas import toys                              # noqa: E402
from atlas.sample import ranks_of, sample_uniform   # noqa: E402

HERE = Path(__file__).resolve().parent.parent
BEta04 = HERE.parent
RESULTS = []
TOYS = toys.all_toys()


def test(fn):
    def run():
        t0 = time.process_time()
        try:
            info = fn()
            ok = True
        except AssertionError as e:
            ok, info = False, {"assertion": str(e), "trace": traceback.format_exc()[-1500:]}
        except Exception as e:                       # noqa: BLE001
            ok, info = False, {"error": repr(e), "trace": traceback.format_exc()[-1500:]}
        RESULTS.append({"test": fn.__name__, "pass": ok, "cpu_s": round(time.process_time() - t0, 2), "info": info})
        print("%-44s %s  %.1fs" % (fn.__name__, "PASS" if ok else "FAIL", time.process_time() - t0), flush=True)
    run.__name__ = fn.__name__
    return run


# ---------------------------------------------------------------- sampler / ranks
@test
def sampler_uniform_over_class():
    out = {}
    for T, n, lib in (("Int", 4, None), ("List", 5, None), ("Int", 3, TOYS["TOY-D2"][1])):
        E = Enumerator(lib)
        members = {t for t, _s in E.terms(T, (), n)}
        r = random.Random(7)
        N = 40 * len(members)
        cnt = Counter(sample_uniform(E, T, (), n, r) for _ in range(N))
        assert set(cnt) <= members, "sample outside the class"
        exp = N / len(members)
        chi2 = sum((cnt.get(m, 0) - exp) ** 2 / exp for m in members)
        df = len(members) - 1
        z = (chi2 - df) / math.sqrt(2 * df)
        assert z < 4.0, "chi-square z = %.2f" % z
        out["%s/%d/lib%d" % (T, n, 0 if lib is None else len(lib))] = {"class": len(members), "draws": N,
                                                                       "coverage": len(cnt) / len(members),
                                                                       "chi2_z": round(z, 3)}
    return out


@test
def ranks_of_equals_rank_of():
    checked = 0
    for name in ("GRADED", "TOY-D2"):
        T, lib = TOYS[name]
        E = Enumerator(lib)
        r = random.Random(3)
        terms = [sample_uniform(E, T["output_type"], (), n, r) for n in (2, 3, 4, 5, 5, 6) for _ in range(3)]
        for sd in (0, 1):
            got = ranks_of(E, terms, T["output_type"], sd, T["family_id"])
            for t, g in zip(terms, got):
                assert g["rank"] == E.rank_of(t, T["output_type"], sd, T["family_id"]), C.to_str(t)
                checked += 1
    return {"terms_checked": checked}


# ---------------------------------------------------------------- route
@test
def route_edges_are_legal_mutations_and_step_prob_exact():
    T, lib = TOYS["GRADED"]
    E = Enumerator(lib)
    mut = Mutator(E)
    W = C.parse(T["witness"])
    lat = R.lattice(mut, W, "List")
    sp = R.StepProb(mut)
    zero = 0
    edges = 0
    for k, nd in lat["nodes"].items():
        for q, _mv in nd["prunes"]:
            edges += 1
            if sp.single(lat["nodes"][q]["term"], nd["term"], "List") <= 0:
                zero += 1
    assert zero == 0, "%d lattice edges are not single forward mutations" % zero
    route = R.canonical_route(mut, W, "List")
    # empirical frequencies vs exact p_eff on the route's steps
    r = random.Random(11)
    emp = []
    for a, b in zip(route, route[1:]):
        N = 60000
        hits = sum(1 for _ in range(N) if mut.mutate(a["term"], "List", r) == b["term"])
        ps = sp.single(a["term"], b["term"], "List")
        pn = sp.p_none(a["term"], "List", random.Random(5), 20000)
        pe = ps / (1 - pn)
        sd = math.sqrt(N * pe * (1 - pe))
        z = (hits - N * pe) / sd if sd > 0 else 0
        emp.append({"step": b["text"], "p_eff": pe, "empirical": hits / N, "z": round(z, 2)})
        assert abs(z) < 4.5, emp[-1]
    for i in range(1, len(route)):
        assert route[i]["size"] > route[i - 1]["size"]
    return {"lattice_nodes": len(lat["nodes"]), "edges": edges, "route": [x["text"] for x in route], "empirical": emp}


@test
def synonyms_are_semantically_identical():
    bad = n = 0
    for name, (T, lib) in TOYS.items():
        E = Enumerator(lib)
        mut = Mutator(E)
        view = K.LearnerView(T)
        cert = K.Certifier(T, lib)
        W = C.parse(T["witness"])
        r = random.Random(1)
        ins = view.dev_inputs + view.probes + cert.tribunal
        for t in [W] + [nd["term"] for nd in R.lattice(mut, W, T["output_type"])["nodes"].values()]:
            ref = K.outs_of(t, ins, lib)
            for q in R.synonyms(mut, t, T["output_type"], r, 6):
                n += 1
                bad += K.outs_of(q, ins, lib) != ref
    assert bad == 0, "%d of %d synonyms changed behaviour" % (bad, n)
    return {"synonyms_checked": n}


# ---------------------------------------------------------------- determinism / accounting
def _arm(name, arm, seed=0, budget=3000, desc=None, task=None, **kw):
    T, lib = TOYS[name]
    return A.run_arm(task or T, lib, arm, seed, budget, descriptor=desc, **kw)


@test
def determinism_in_process_and_fresh_process():
    a = _arm("GRADED", "B3-CELLADMIT", 2, 3000, "D-BEH", stop_on_hit=False)
    b = _arm("GRADED", "B3-CELLADMIT", 2, 3000, "D-BEH", stop_on_hit=False)
    c = _arm("GRADED", "B3-CELLADMIT", 3, 3000, "D-BEH", stop_on_hit=False)
    assert a["decision_log_sha256"] == b["decision_log_sha256"]
    assert a["decision_log_sha256"] != c["decision_log_sha256"]
    code = ("import os;os.environ['OMP_NUM_THREADS']='1';from atlas import toys,arms;T,l=toys.all_toys()['GRADED'];"
            "print(arms.run_arm(T,l,'B3-CELLADMIT',2,3000,descriptor='D-BEH',stop_on_hit=False)"
            "['decision_log_sha256'])")
    out = subprocess.run([sys.executable, "-c", code], cwd=str(BEta04), capture_output=True, text=True,
                         env={**os.environ, "PYTHONPATH": str(BEta04)}, timeout=300)
    fresh = out.stdout.strip().splitlines()[-1]
    assert fresh == a["decision_log_sha256"], (fresh, out.stderr[-500:])
    return {"sha": a["decision_log_sha256"][:16], "fresh_process_equal": True, "other_seed_differs": True}


@test
def matched_compute_accounting_exact():
    rows = {}
    T, lib = TOYS["TOY-D2"]
    view = K.LearnerView(T)
    E = Enumerator(lib)
    for arm, desc in (("A-FRESH", None), ("A-CHAIN", None), ("B1-RETAIN", None), ("B2-DESCSEL", "D-BEH"),
                      ("B3-CELLADMIT", "D-BEH"), ("C3-RAND", "RAND:50"), ("C2-RAND", "RAND:50")):
        s = A.Search(view, K.Certifier(T, lib), E, arm, 1, 2500, 10, desc, stop_on_hit=False, keep_log=True)
        r = s.run()
        nst = len(s.starts)
        assert r["ledger"]["search"]["charges"] == 2500, arm
        assert len(s.log) == 2500 - nst, arm
        expect_restores = 1 if arm == "A-CHAIN" else math.ceil((2500 - nst) / 10)
        assert s.restores == expect_restores, (arm, s.restores, expect_restores)
        # re-sum the expanded/promoted unit ledgers independently from the logged genotypes
        u = [0, 0]
        for t in [x["term"] for x in s.starts] + [C.parse(line.split("|")[1]) for line in s.log]:
            fn = K.compile_p(t, lib)
            C.U[0] = C.U[1] = 0
            for i in view.dev_inputs:
                C.run(fn, i)
            u[0] += C.U[0]
            u[1] += C.U[1]
        assert u == s.units_dev, (arm, u, s.units_dev)
        rows[arm] = {"charges": 2500, "restores": s.restores, "units_dev": s.units_dev,
                     "probe_runs": s.probe_runs, "rejected": s.rejected}
    return rows


# ---------------------------------------------------------------- target blindness
def _perturb(task):
    t = copy.deepcopy(task)

    def bump(o):
        if isinstance(o, bool):
            return not o
        if isinstance(o, int):
            return o + 1
        return o + [0]
    t["test"] = [[i, bump(o)] for i, o in t["test"]]
    t["witness"] = "(rev xs)" if t["output_type"] == "List" else "(len xs)"
    return t


@test
def archive_target_blindness_perturbation():
    out = {}
    for name, arm, desc in (("GRADED", "B1-RETAIN", None), ("GRADED", "B2-DESCSEL", "D-BEH"),
                            ("CREDIT", "B3-CELLADMIT", "D-BEH"), ("CREDIT", "C3-RAND", "RAND:300"),
                            ("TOY-D2", "B3-CELLADMIT", "D-RES")):
        T, lib = TOYS[name]
        P = _perturb(T)
        a = A.run_arm(T, lib, arm, 4, 4000, descriptor=desc, stop_on_hit=False, final_eval=False)
        b = A.run_arm(P, lib, arm, 4, 4000, descriptor=desc, stop_on_hit=False, final_eval=False)
        assert a["decision_log_sha256"] == b["decision_log_sha256"], (name, arm)
        assert a["archive"] == b["archive"], (name, arm)
        out["%s/%s" % (name, arm)] = {"same_decisions": True, "hits_original": len(a["mechanisms"]["qualified_skeletons"]),
                                      "hits_perturbed": len(b["mechanisms"]["qualified_skeletons"])}
    assert any(v["hits_original"] != v["hits_perturbed"] for v in out.values()), "perturbation never bit"
    v = K.LearnerView(TOYS["GRADED"][0])
    assert not any(k in vars(v) for k in ("test", "witness", "tribunal")), "LearnerView leaks target-side data"
    sig = inspect.signature(D.Descriptor.cell)
    assert list(sig.parameters) == ["self", "text", "dev_outs", "probe_outs", "view"]
    return out


# ---------------------------------------------------------------- restoration
@test
def genotype_and_state_restoration():
    T, lib = TOYS["GRADED"]
    view = K.LearnerView(T)
    E = Enumerator(lib)
    s = A.Search(view, K.Certifier(T, lib), E, "B3-CELLADMIT", 5, 4000, 10, "D-BEH", stop_on_hit=False,
                 store_rng=True)
    s.run()
    desc = D.get("D-BEH")
    for e in s.entries:
        t = C.parse(e["text"])
        assert t == e["term"]
        o = K.outs_of(t, view.dev_inputs, lib)
        p = K.outs_of(t, view.probes, lib)
        assert K.exact_credit(o, view.targets) == e["score"]
        assert desc.cell(e["text"], o, p, view) == e["cell"]
        assert hashlib.sha256(repr(e["rng_state"]).encode()).hexdigest()[:16] == e["rng_sha256"]
    # state restore: snapshot mid-run, finish; restore the snapshot into a NEW Search and finish -> identical
    s1 = A.Search(view, K.Certifier(T, lib), E, "B2-DESCSEL", 6, 4000, 10, "D-BEH", stop_on_hit=False)
    while s1.charges < 1700:
        s1.step()
    snap = s1.snapshot()
    r1 = s1.run()
    s2 = A.Search(view, K.Certifier(T, lib), E, "B2-DESCSEL", 6, 4000, 10, "D-BEH", stop_on_hit=False)
    s2.restore_state(snap)
    r2 = s2.run()
    s3 = A.Search(view, K.Certifier(T, lib), E, "B2-DESCSEL", 6, 4000, 10, "D-BEH", stop_on_hit=False)
    r3 = s3.run()
    assert r1["decision_log_sha256"] == r2["decision_log_sha256"] == r3["decision_log_sha256"]
    # genotype-only restore (copy the program, fresh RNG) does NOT reproduce the continuation
    s4 = A.Search(view, K.Certifier(T, lib), E, "B2-DESCSEL", 6, 4000, 10, "D-BEH", stop_on_hit=False)
    s4.restore_state(snap)
    s4.rng.seed(12345)
    r4 = s4.run()
    assert r4["decision_log_sha256"] != r1["decision_log_sha256"]
    return {"entries_checked": len(s.entries), "state_restore_identical": True,
            "genotype_only_restore_diverges": True}


# ---------------------------------------------------------------- random-control matching
@test
def random_control_matching():
    T, lib = TOYS["GRADED"]
    E = Enumerator(lib)
    cal = A.calibrate_random_k(T, lib, "B3-CELLADMIT", "D-BEH", 3000, seeds=(1000, 1001, 1002), E=E)
    assert cal["matched_within_5pct"], cal
    ev = []
    for sd in (0, 1, 2):
        b = A.run_arm(T, lib, "B3-CELLADMIT", sd, 3000, descriptor="D-BEH", stop_on_hit=False, E=E, final_eval=False)
        c = A.run_arm(T, lib, "C3-RAND", sd, 3000, descriptor="RAND:%d" % cal["K"], stop_on_hit=False, E=E,
                      final_eval=False)
        assert b["ledger"]["search"]["genotype_restores"] == c["ledger"]["search"]["genotype_restores"]
        ev.append((b["archive"]["realised_cells"], c["archive"]["realised_cells"]))
    rb = sum(x for x, _ in ev) / len(ev)
    rc = sum(y for _, y in ev) / len(ev)
    assert abs(rc - rb) <= 0.15 * rb, ev
    return {"calibration": cal, "eval_seeds_cells_B3_vs_C3": ev}


# ---------------------------------------------------------------- final evaluation / descriptor controls / x-check
@test
def final_evaluation_is_archive_free():
    params = list(inspect.signature(K.final_evaluation).parameters)
    assert not any("archive" in p or "search" in p for p in params), params
    T, lib = TOYS["DESERT"]
    good = K.final_evaluation(T["witness"], T, lib)
    bad = K.final_evaluation("(map (lam x (mul x x)) xs)", T, lib)
    assert good["autonomous_pass"] and not bad["autonomous_pass"]
    assert K.Certifier(T, lib, salt="FINAL").tribunal != K.Certifier(T, lib).tribunal
    return {"params": params, "witness": good["autonomous_pass"], "wrong": bad["autonomous_pass"]}


@test
def descriptor_qualification_controls_behave():
    out = {}
    for name in ("GRADED", "DESERT"):
        T, lib = TOYS[name]
        q = D.qualify(T, T["witness"], lib, per_size=400, walk_n=1500)
        assert q["controls_ok"], name
        assert q["synonym_semantic_mismatches"] == 0
        assert q["descriptors"]["C-FIT"]["R1_separation"] == 0.0
        assert q["descriptors"]["GENO"]["R2_invariance"] == 0.0
        out[name] = {k: q["descriptors"][k]["verdict"] for k in ("D-BEH", "D-CERT", "D-RES")}
    return out


@test
def crosscheck_tfs1_toy_hitting_cost():
    T, lib = TOYS["TOY-D2"]
    rows = M.hitting_cost(T, lib, (0,), 100_000, 8)
    assert rows[0]["hit_charge"] == 78783, rows[0]
    return {"seed0_hit_charge": rows[0]["hit_charge"], "substrate_lead_value": 78783}


@test
def planted_label_calibration():
    want = {"GRADED": "RARITY_LIMIT", "DESERT": "REACHABILITY_DESERT", "CREDIT": "CREDIT_LIMIT"}
    got = {}
    for name, lab in want.items():
        T, lib = TOYS[name]
        rec = M.atlas(T, lib, seeds=(0,), enum_budget=100_000, enum_max_size=7, density_max_n=4, robust_n=50)
        c = M.classify(rec, 5000)
        got[name] = c["local_search"]
        assert c["local_search"] == lab, (name, c)
    return got


@test
def empirical_flags_and_blind_control():
    B = 5000
    g = M.classify_empirical({"A-CHAIN": [100] * 8, "A-CHAIN[none]": [B] * 8, "A-CHAIN[partial]": [100] * 8}, B)
    assert g["FEEDBACK_USED"] and not g["ALT_CREDIT_HELPS"] and g["reading"] == "RARITY_LIMIT", g
    c = M.classify_empirical({"A-CHAIN": [B] * 8, "A-CHAIN[none]": [B] * 8, "A-CHAIN[partial]": [300] * 8}, B)
    assert c["reading"] == "CREDIT_LIMIT" and not c["DRIFT_CROSSES"], c
    d = M.classify_empirical({"A-CHAIN": [B] * 8, "A-CHAIN[none]": [B] * 8, "A-CHAIN[partial]": [B] * 8}, B)
    assert d["reading"] == "REACHABILITY_DESERT", d
    # the credit-blind chain (accepts every non-all-FAIL child) keeps exact accounting: one restore, budget charges
    T, lib = TOYS["GRADED"]
    view = K.LearnerView(T)
    E = Enumerator(lib)
    s = A.Search(view, None, E, "A-CHAIN", 0, 1500, 10, None, stop_on_hit=False, credit="none", keep_log=True)
    s.run()
    assert s.charges == 1500 and s.restores == 1
    return {"graded": g["reading"], "credit": c["reading"], "desert": d["reading"]}


def main():
    t0 = time.time()
    tests = [sampler_uniform_over_class, ranks_of_equals_rank_of, route_edges_are_legal_mutations_and_step_prob_exact,
             synonyms_are_semantically_identical, determinism_in_process_and_fresh_process,
             matched_compute_accounting_exact, archive_target_blindness_perturbation, genotype_and_state_restoration,
             random_control_matching, final_evaluation_is_archive_free, descriptor_qualification_controls_behave,
             crosscheck_tfs1_toy_hitting_cost, planted_label_calibration, empirical_flags_and_blind_control]
    for t in tests:
        t()
    code = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))}
    res = {"suite": "atlas-v0 tests", "pass": sum(r["pass"] for r in RESULTS), "fail": sum(not r["pass"] for r in RESULTS),
           "wall_s": round(time.time() - t0, 1), "code_sha256": code, "results": RESULTS}
    (HERE / "ATLAS_TEST_RESULTS.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str))
    print("PASS %d / FAIL %d" % (res["pass"], res["fail"]))


if __name__ == "__main__":
    main()
