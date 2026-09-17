"""Campaign 2 Phase A machine changes -- each group exercised minimally (directive: "exercise
each change minimally and preserve evidence that it works")."""
import json
from pathlib import Path

import pytest

from proteus.foundry import generate as G

from archaeon.wse import digest as D
from archaeon.wse import reachability as R
from archaeon.wse import states as S
from archaeon.wse import telemetry as T
from archaeon.wse.economics import REGIMES
from archaeon.wse.engine_descriptor import engine as engine_descriptor
from archaeon.wse.evolve import FOUNDRY, Evolution, common_fill, evaluate, gen0, run_cell
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2 import accounting as A
from archaeon.campaign2 import prereg as P
from archaeon.campaign2.runner import Attempt, Engine, step_key

HERE = Path(__file__).resolve().parent
F = dict(FOUNDRY, genome_instr_range=[1, 16], tape_words_choices=[16, 32, 64, 128, 256], tick_budget_choices=[16, 64, 256])
W0 = WorldSpec("W0", value_bits=4)


# ---------------------------------------------------------------- F: digest
def test_digest_one_canonical_form():
    h = "ab" * 32
    assert D.canon(h) == "sha256:" + h and D.canon("sha256:" + h) == "sha256:" + h
    assert D.same(h, "SHA256:" + h) and not D.same(h, None) and D.hexof("sha256:" + h) == h
    assert D.of_bytes(b"x").startswith("sha256:") and D.of_obj({"b": 1, "a": 2}) == D.of_obj({"a": 2, "b": 1})


def test_engine_descriptor_is_one_tracked_file():
    e = engine_descriptor()
    assert e["base_url"].startswith("https://") and e["engine_instance_id"].startswith("eng_") and e["cacert_exists"]


# ---------------------------------------------------------------- A: reachability
def test_reachability_classes_and_bands(tmp_path):
    assert R.classify(0, 0) == "UNESTABLISHED" and R.classify(2, 0) == "UNESTABLISHED"
    assert R.classify(3, 0) == "OBSERVED_UNREACHABLE_AT_BUDGET" and R.wilson(0, 3)[1] < 0.6
    assert R.classify(3, 1) == "REACHABLE" and R.classify(12, 1) == "RARE" and R.classify(12, 12) == "COMMON"
    tbl = tmp_path / "r.jsonl"
    rows = [R.row(W0, N=20, G=5, E=4, regime="E0", seed=s, source={"campaign": "t", "experiment": "x", "arm": "base"},
                  first_solved_gen=(2 if s == 1 else None), best_train_max=0.5, kind="baseline") for s in (1, 2, 3)]
    assert R.record(rows, tbl) == 3 and R.record(rows, tbl) == 0            # idempotent
    L = R.lookup("W0", value_bits=4, N=20, G=5, E=4, rows=R.load(tbl))
    assert L["n"] == 3 and L["k"] == 1 and L["class"] == "REACHABLE" and L["first_solved_gens"] == [2]
    assert R.candidates(0.2, 0.7, value_bits=4, rows=R.load(tbl))[0]["cell"] == "W0"
    assert R.lookup("W9", value_bits=4, rows=R.load(tbl))["class"] == "UNESTABLISHED"


def test_reachability_row_from_result_marks_kind():
    res = run_cell(W0, REGIMES["E0"], 1, 1, N=12, G_=3, E=4, foundry=F)
    r = R.row_from_result(W0, res, N=12, G=3, E=4, regime="E0", seed=1, source={"campaign": "t"})
    assert r["kind"] == "baseline" and r["eval_resolution"] == 0.25
    pop, prov = common_fill(1, 1, 12, [o["manifest"] for o in G.generate(dict(F, seed=5, n=2))], foundry=F)
    res2 = run_cell(W0, REGIMES["E0"], 1, 1, N=12, G_=3, E=4, init_pop=pop, gen0_provenance=prov, foundry=F)
    assert R.row_from_result(W0, res2, N=12, G=3, E=4, regime="E0", seed=1, source={})["kind"] == "treated"


# ---------------------------------------------------------------- C + G + H: loop
def test_crn_default_and_opt_out_and_snapshot():
    snap = json.loads((HERE / "data_evolve_snapshot_pre_c2.json").read_text(encoding="utf-8"))
    r = run_cell(W0, REGIMES["E0"], 20260917, 1, N=24, G_=6, E=4, branch="snap-branch", rng_label="snap-branch", foundry=F)
    assert [t["best_reward"] for t in r["trace"]] == snap["W0"]["trace_best"] and r["elite"]["organism_id"] == snap["W0"]["elite_id"]
    a = run_cell(W0, REGIMES["E0"], 20260917, 1, N=24, G_=5, E=4, branch="arm-A", foundry=F)
    b = run_cell(W0, REGIMES["E0"], 20260917, 1, N=24, G_=5, E=4, branch="arm-B", foundry=F)
    c = run_cell(W0, REGIMES["E0"], 20260917, 1, N=24, G_=5, E=4, branch="arm-B", rng_label="x", foundry=F)
    ids = lambda r: [o["manifest"] for o in r["final_population"]]           # noqa: E731
    assert ids(a) == ids(b) and ids(b) != ids(c)
    assert a["gen0_provenance"]["verified_common"] and a["warnings"] == [] and a["rng_label"] == "crn"


def test_common_fill_provenance_and_origin_share():
    subs = [o["manifest"] for o in G.generate(dict(F, seed=9, n=4))]
    pop, prov = common_fill(20260917, 1, 16, subs, tag="import", foundry=F)
    base = gen0(20260917, 1, 16, F)
    assert prov["n_substituted"] == 4 and prov["verified_common"]
    assert [o["organism_id"] for o in pop[4:]] == [o["organism_id"] for o in base[:12]]
    r = run_cell(W0, REGIMES["E0"], 20260917, 1, N=16, G_=3, E=4, init_pop=pop, gen0_provenance=prov, foundry=F)
    assert r["trace"][0]["origin_shares"]["import"] == 0.25 and "gen0_provenance" in r["trace"][0] and r["warnings"] == []
    r2 = run_cell(W0, REGIMES["E0"], 20260917, 1, N=16, G_=2, E=4, init_pop=pop, foundry=F)
    assert "GEN0_FILL_UNVERIFIED" in r2["warnings"]


def test_step_api_matches_run_and_allows_spec_change():
    ev = Evolution(W0, REGIMES["E0"], 20260917, 3, N=16, E=4, foundry=F)
    rows = [ev.step() for _ in range(3)]
    ev.spec = WorldSpec("W1_d1", delay=1, value_bits=4)                 # a curriculum changes the pressure between steps
    last = ev.evaluate_generation(last=True)
    res = ev.result()
    assert [r["gen"] for r in rows] == [0, 1, 2] and last["cell"] == "W1_d1" and res["generations"] == 4
    full = run_cell(W0, REGIMES["E0"], 20260917, 3, N=16, G_=3, E=4, foundry=F)
    ev2 = Evolution(W0, REGIMES["E0"], 20260917, 3, N=16, E=4, foundry=F)
    assert ev2.run(3)["final_population_ids"] == full["final_population_ids"]
    assert "first_solved_gen" in full and "elite_summary" in full


def test_interventions_applied_is_counted():
    m = G.generate(dict(F, seed=2, n=1))[0]["manifest"]
    eps = episodes_for(W0, 1, "train", 1, 5)
    assert evaluate(m, eps, intervention="ERASE_ALL", rng_seed=1)["interventions_applied"] == 5
    assert evaluate(m, eps, rng_seed=1)["interventions_applied"] == 0


# ---------------------------------------------------------------- E + H: telemetry
def test_maturity_and_summaries():
    m = T.maturity("W0", 0.125, [0.0, 0.0, 0.125], chance=1 / 16, budget={"N": 10, "G": 2, "E": 4})
    assert T.maturity_state(m) == "IMMATURE_ARTIFACT" and not m["solved"]
    assert T.maturity_state(T.maturity("W0", 0.0, [0.0, 0.0], chance=1 / 16, budget={})) == "RESIDUE_BELOW_FLOOR"
    assert T.maturity_state(T.maturity("W0", 1.0, [0.2, 1.0], chance=1 / 16, budget={})) is None
    s = T.genome_summary(G.generate(dict(F, seed=3, n=1))[0]["manifest"])
    assert s["instr"] >= 1 and abs(sum(s["category_shares"].values()) - 1.0) < 1e-6
    shelf = T.shelf_report([{"gen": 0, "r0": 1.0, "r4": 0.1}, {"gen": 5, "r0": 0.9, "r4": 0.5}, {"gen": 9, "r0": 0.2, "r4": 0.9}], ["r0", "r4"])
    assert shelf["r0"]["fell_at_gen"] == 9 and shelf["r4"]["fell_at_gen"] is None


# ---------------------------------------------------------------- B: typed states
def _rows(vals, arm="t", extra=None):
    return [dict({"arm": arm, "seed": i + 1, "competence_heldout": v, "first_solved_gen": (0 if v >= 0.5 else None)}, **(extra or {})) for i, v in enumerate(vals)]


def test_typed_states_fire_from_measurements():
    decl = {"positive_control": {"arm": "pc", "metric": "competence_heldout", "min": 0.5, "min_rows": 1},
            "interventions": [{"arm": "t", "counter": "tabu_hits"}],
            "artifacts": {"res": T.maturity("W0", 0.0, [0.0], chance=1 / 16, budget={}), "imm": T.maturity("W0", 0.2, [0.2], chance=1 / 16, budget={})},
            "stream": {"threshold": 0.5}, "readout_control": {"arm": "shift", "metric": "acc", "chance": 0.5, "min_above": 0.1},
            "target": {"baseline_arm": "base", "reach_metric": "competence_heldout", "reach_min": 0.5, "reachability_class": "RARE"}, "n_min": 3}
    rows = _rows([0.1, 0.1, 0.1], "t", {"tabu_hits": 0}) + _rows([0.1, 0.2, 0.1], "pc") + _rows([0.0, 0.0, 0.0], "base") + \
        [{"arm": "shift", "seed": 1, "acc": 0.52}]
    st = S.assay_states(decl, {"rows": rows, "stream_max_score": 0.3, "harness_errors": [], "engine_errors": []})
    names = {s["state"] for s in st}
    assert {"INTERVENTION_NOT_APPLIED", "RESIDUE_BELOW_FLOOR", "IMMATURE_ARTIFACT", "STREAM_BELOW_THRESHOLD", "TARGET_UNREACHABLE",
            "READOUT_CANNOT_EXPRESS", "POSITIVE_CONTROL_FAILED", "UNDERPOWERED"} <= names
    d = S.disposition_candidate(dict(decl, primary={"treatment": "t", "control": "base", "metric": "competence_heldout", "min_effect": 0.1}),
                                {"rows": rows, "engine_errors": [{"e": 1}]})
    assert d["disposition"] == "ENGINE_FAILURE"


def test_disposition_science_ladder():
    decl = {"positive_control": {"arm": "pc", "metric": "competence_heldout", "min": 0.5, "min_rows": 1},
            "primary": {"treatment": "t", "control": "c", "metric": "competence_heldout", "min_effect": 0.1}}
    pc = _rows([0.6], "pc")
    neg = S.disposition_candidate(decl, {"rows": _rows([0.1, 0.1, 0.1], "t") + _rows([0.1, 0.12, 0.1], "c") + pc})
    assert neg["disposition"] == "CAPABLE_NEGATIVE"
    weak = S.disposition_candidate(decl, {"rows": _rows([0.6, 0.5, 0.7], "t") + _rows([0.1, 0.1, 0.1], "c") + pc})
    assert weak["disposition"] == "WEAK_POSITIVE"
    big = _rows([0.6] * 10, "t") + _rows([0.1] * 10, "c") + pc
    assert S.disposition_candidate(decl, {"rows": big})["disposition"] == "WEAK_POSITIVE"            # n >= 10 alone never promotes
    d2 = dict(decl, battery=[{"name": "length", "passed": True}, {"name": "composition", "passed": True}])
    assert S.disposition_candidate(d2, {"rows": big})["disposition"] == "SUPPORTED_POSITIVE"
    d3 = dict(decl, battery=[{"name": "length", "passed": True}, {"name": "composition", "passed": False}])
    assert S.disposition_candidate(d3, {"rows": big})["disposition"] == "WEAK_POSITIVE"
    inc = S.disposition_candidate(decl, {"rows": _rows([0.1, 0.1], "t") + _rows([0.1, 0.1], "c") + _rows([0.1], "pc")})
    assert inc["disposition"] == "POSITIVE_CONTROL_FAILED"


# ---------------------------------------------------------------- D: attempts / resume
def test_attempts_are_numbered_persisted_and_resumable(tmp_path):
    calls = {"n": 0}

    def make():
        calls["n"] += 1
        return {"world_id": "wld_x", "alive": True}
    a1 = Attempt("C2-TEST", root=tmp_path, dry_run=True)
    assert a1.number == 1 and (a1.path / "RECEIPT.json").exists()
    w = a1.step("world", make, parts=("cell", 1), kind="world")
    with pytest.raises(RuntimeError):
        a1.step("boom", lambda: (_ for _ in ()).throw(RuntimeError("x")))
    assert a1.receipt["errors"][0]["step"] == "boom"
    a1.finalize(rows=[{"arm": "a"}], of_record=False)
    a2 = Attempt("C2-TEST", root=tmp_path, dry_run=True)
    assert a2.number == 2 and a2.receipt["resumed_from"] == 1
    w2 = a2.step("world", make, parts=("cell", 1), kind="world", verify=lambda r: r["alive"])
    assert w2 == w and calls["n"] == 1 and a2.receipt["replayed"] == ["world:cell/1"]
    a2.step("world", make, parts=("cell", 2), kind="world")                                    # a new key executes
    assert calls["n"] == 2
    a2.finalize(rows=[], of_record=False)
    a3 = Attempt("C2-TEST", root=tmp_path, dry_run=True)
    a3.step("world", make, parts=("cell", 1), kind="world", verify=lambda r: False)           # verifier says stale -> re-executed
    assert calls["n"] == 3
    idx = a3.finalize(rows=[{"arm": "b"}], of_record=True, disposition={"disposition": "INCONCLUSIVE"})
    assert idx["of_record"] == 3 and (tmp_path / "C2-TEST" / "RECEIPT.json").exists() and (tmp_path / "C2-TEST" / "rows.json").exists()
    assert set(idx["attempts"]) == {"1", "2", "3"} and idx["attempts"]["1"]["errors"] == 1
    assert step_key("a", 1) == step_key("a", 1) != step_key("a", 2)


def test_resume_never_replays_a_different_design(tmp_path):
    """C2-SFE-02 a05 replayed a04's records for a changed design; keys now carry the sealed prereg digest."""
    calls = {"n": 0}

    def post():
        calls["n"] += 1
        return {"obs": calls["n"]}
    a1 = Attempt("C2-TEST2", root=tmp_path, dry_run=True)
    a1.receipt["prereg_digest"] = "sha256:design-A"
    a1.step("record", post, parts=("arm", 1))
    a1.finalize(rows=[], of_record=False)
    a2 = Attempt("C2-TEST2", root=tmp_path, dry_run=True)
    a2.receipt["prereg_digest"] = "sha256:design-B"
    a2.step("record", post, parts=("arm", 1))
    assert calls["n"] == 2 and a2.receipt["replayed"] == []
    a2.finalize(rows=[], of_record=False)
    a3 = Attempt("C2-TEST2", root=tmp_path, dry_run=True)
    a3.receipt["prereg_digest"] = "sha256:design-B"
    assert a3.step("record", post, parts=("arm", 1)) == {"obs": 2} and calls["n"] == 2   # same design: replayed


def test_engine_wrapper_refuses_population_material_without_maturity():
    e = Engine(dry_run=True)
    with pytest.raises(ValueError):
        e.publish("w", "cmp2.pop.elites", {"x": 1})


# ---------------------------------------------------------------- I: prereg + accounting
def _prereg():
    return {"experiment": "C2-SFE-00", "title": "test", "parents": ["SFE-01"], "question": "q", "parent_evidence": "e",
            "assay_capability_requirement": "a", "positive_control": "p", "reachability_estimate": "r", "arms": ["t", "c"],
            "crn_policy": "default", "budget": {"N": 1}, "primary_observable": "competence_heldout", "claim_ceiling": "weak",
            "falsification_condition": "f", "typed_failure_conditions": ["TARGET_UNREACHABLE"], "expected_machine_telemetry": ["first_solved_gen"],
            "machine_changes_exercised": ["A"], "decl": {"primary": {"treatment": "t", "control": "c", "metric": "competence_heldout", "min_effect": 0.1}}}


def test_prereg_validate_seal_render(tmp_path):
    p = _prereg()
    assert P.validate(p) == [] and "question" in P.validate({k: v for k, v in p.items() if k != "question"})
    path = P.save(p, tmp_path)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert P.unchanged(p, saved["prereg_digest"]) and not P.unchanged(dict(p, question="changed"), saved["prereg_digest"])
    assert "QUESTION: q" in P.render(saved)


def test_record_and_ledger_generated_from_receipt(tmp_path):
    p = _prereg()
    rows = _rows([0.6, 0.5, 0.7], "t") + _rows([0.1, 0.1, 0.1], "c")
    receipt = {"attempt": 1, "engine_path": False, "worlds": {}, "artifacts": {}, "imports": {}, "records": {}, "errors": [{"step": "x", "error": "boom"}],
               "timings": {"total_s": 1.0}, "replayed": [], "teardown": {}}
    st = S.assay_states(p["decl"], {"rows": rows})
    disp = S.disposition_candidate(p["decl"], {"rows": rows}, st)
    idx = {"attempts": {"1": {"errors": 1, "replayed_steps": 0}, "2": {"errors": 0, "replayed_steps": 3}}, "of_record": 2}
    txt = A.render_record(p, receipt, rows, idx, states=st, disposition=disp, addendum={"science": "S", "disposition": "WEAK_POSITIVE"})
    assert "WEAK_POSITIVE" in txt and "0.600" in txt and "## B. EXECUTION" in txt and "DISPOSITION: WEAK_POSITIVE" in txt
    cands = A.ledger_candidates("C2-SFE-00", receipt, st, idx)
    assert {c["category"] for c in cands} >= {"BUG", "RECOVERY"}
    led = tmp_path / "L.jsonl"
    ids = A.append_ledger(cands, led)
    assert ids[0] == "L2-001" and A.next_ledger_id(led) == "L2-%03d" % (len(ids) + 1)
    A.recur(ids[0], "C2-SFE-01", led)
    assert json.loads(led.read_text().splitlines()[0])["recurrence"] == 1
    f = A.funnel_row("C2-SFE-00", p, receipt, st, disp, idx)
    assert f["assay_capable"] and f["scientific_disposition"] == "WEAK_POSITIVE" and f["attempts"] == 2 and f["resumed"]
