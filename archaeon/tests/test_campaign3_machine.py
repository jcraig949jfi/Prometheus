"""Campaign 3 Phase A machine changes -- each exercised minimally with preserved evidence."""
from proteus.foundry import generate as G

from archaeon.wse import corridor as CT
from archaeon.wse import reachability as R
from archaeon.wse import telemetry as T
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import FOUNDRY, Evolution, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2 import prereg as P

F = dict(FOUNDRY, genome_instr_range=[1, 16], tape_words_choices=[16, 32, 64, 128, 256], tick_budget_choices=[16, 64, 256])
W2 = WorldSpec("W2_K2", K=2, value_bits=4)
W0 = WorldSpec("W0", value_bits=4)


# ---------------------------------------------------------------- A: three levels + candidates
def test_levels_need_heldout_for_summit():
    assert R.level_of(0.3) == "FLOOR" and R.level_of(0.5) == "SHELF" and R.level_of(0.95) == "SHELF"       # training-only summit = candidate
    assert R.level_of(0.95, 0.95) == "SUMMIT" and R.level_of(0.95, 0.53) == "SHELF"
    tb = [0.1, 0.5, 0.6, 0.95, 0.7]
    r = R.row(W2, N=10, G=5, E=4, regime="E0", seed=1, source={"campaign": "t"}, first_solved_gen=1, best_train_max=0.95, heldout=0.53, trace_best=tb)
    assert r["first_shelf_gen"] == 1 and r["summit_candidate_gen"] == 3 and r["first_summit_gen"] is None and r["summit_censored"] and r["level"] == "SHELF"
    r2 = R.row(W2, N=10, G=5, E=4, regime="E0", seed=2, source={"campaign": "t"}, first_solved_gen=1, best_train_max=0.95, heldout=0.92, trace_best=tb)
    assert r2["first_summit_gen"] == 3 and r2["level"] == "SUMMIT" and not r2["summit_censored"]


# ---------------------------------------------------------------- B: right-censoring / monotone lookup
def test_stopped_runs_inform_larger_budgets_monotonically(tmp_path):
    tbl = tmp_path / "r.jsonl"
    rows = [R.row(W0, N=20, G=12, E=4, regime="E0", seed=1, source={"campaign": "t", "experiment": "x", "arm": "a"}, first_solved_gen=10, best_train_max=1.0,
                  heldout=1.0, trace_best=[0.1] * 10 + [1.0, 1.0], stopped_on_solve=True, campaign_seed=1, rng_label="crn"),
            R.row(W0, N=20, G=60, E=4, regime="E0", seed=2, source={"campaign": "t", "experiment": "x", "arm": "a"}, first_solved_gen=None, best_train_max=0.2,
                  trace_best=[0.2] * 60, campaign_seed=1, rng_label="crn"),
            R.row(W0, N=20, G=60, E=4, regime="E0", seed=3, source={"campaign": "t", "experiment": "x", "arm": "a"}, first_solved_gen=40, best_train_max=1.0,
                  heldout=1.0, trace_best=[0.2] * 40 + [1.0] * 20, campaign_seed=1, rng_label="crn")]
    R.record(rows, tbl)
    L60 = R.lookup("W0", value_bits=4, N=20, G=60, E=4, rows=R.load(tbl))
    assert L60["n"] == 3 and L60["k"] == 2 and L60["n_censored_runs"] == 1 and L60["k_summit"] == 2 and L60["levels"]["SUMMIT"] == 2
    L30 = R.lookup("W0", value_bits=4, N=20, G=30, E=4, rows=R.load(tbl))
    assert L30["n"] == 3 and L30["k"] == 1                       # seed 3 reached at 40: NOT before 30; seed 1 (stopped at 12) informs 30
    L12 = R.lookup("W0", value_bits=4, N=20, G=12, E=4, rows=R.load(tbl), monotone=False)
    assert L12["n"] == 1


# ---------------------------------------------------------------- C: corridor table
def test_corridor_rows_and_edges(tmp_path):
    tbl = tmp_path / "c.jsonl"
    rows = [CT.row(source_cell="W0", target_cell="W2_K2", kind="direct", source={"campaign": "t", "experiment": "e", "arm": "a"}, direct_reuse={"best": 0.5, "n_sources": 4}),
            CT.row(source_cell="W0", target_cell="W2_K2", kind="init", source={"campaign": "t", "experiment": "e", "arm": "a"},
                   init={"dose": 4, "N": 200, "level": "SHELF", "first_shelf_gen": 3, "first_summit_gen": None, "seed": 1}),
            CT.row(source_cell="ladder:W0>W1_d1>W1_d2>W1_d4", target_cell="W1_d4", kind="ladder", source={"campaign": "t", "experiment": "e", "arm": "p0.1"},
                   init={"level": "SUMMIT", "first_summit_gen": 90, "seed": 2})]
    assert CT.record(rows, tbl) == 3 and CT.record(rows, tbl) == 0
    e = CT.edges(CT.load(tbl))
    assert e[("W0", "W2_K2")]["direct_best"] == 0.5 and e[("W0", "W2_K2")]["init_levels"]["SHELF"] == 1 and e[("W0", "W2_K2")]["first_shelf_gens"] == [3]
    assert e[("ladder:W0>W1_d1>W1_d2>W1_d4", "W1_d4")]["ladder_n"] == 1 and "W0" in CT.table_text(CT.load(tbl))


# ---------------------------------------------------------------- D: dense transition probes
def test_probe_plan_and_transition_events():
    plan = T.probe_plan(100, [25, 50, 75], dense=2, sparse=10)
    assert {23, 24, 25, 26, 27, 0, 99, 10, 20} <= set(plan) and 33 not in plan
    m = [{"gen": 0, "R0": 0.1}, {"gen": 5, "R0": 1.0}, {"gen": 10, "R0": 0.9}, {"gen": 15, "R0": 0.2}, {"gen": 20, "R0": 0.1}, {"gen": 30, "R0": 0.95}]
    ev = T.transition_events(m, "R0")
    assert ev["appeared"] == 5 and ev["collapsed"] == 15 and ev["recovered"] == 30


# ---------------------------------------------------------------- F: inject + offspring cap; per-stream credit
def test_per_ask_reward_inject_and_offspring_cap():
    m = G.generate(dict(F, seed=3, n=1))[0]["manifest"]
    e = evaluate(m, episodes_for(W2, 1, "train", 1, 4), rng_seed=1)
    assert len(e["per_ask_reward"]) == 2 and all(0.0 <= v <= 1.0 for v in e["per_ask_reward"])
    ev = Evolution(W2, REGIMES["E0"], 1, 1, N=40, E=4, foundry=F, offspring_cap=0.25)
    ev.evaluate_generation()
    n = ev.inject([o["manifest"] for o in G.generate(dict(F, seed=9, n=4))], "import")
    assert n == 4 and ev.trace[-1]["injected"]["origin_shares_after"]["import"] == 0.1
    ev.reproduce()
    kids = ev.pop[ev.elitism:]
    primary_import = sum(1 for o in kids if o.get("origins", [""])[0] == "import")
    assert primary_import <= int(0.25 * (40 - ev.elitism))
    assert "elite_per_ask" in ev.trace[-1] and "pop_max_per_ask" in ev.trace[-1]
    ev2 = Evolution(W2, REGIMES["E0"], 1, 1, N=40, E=4, foundry=F)                  # no cap: campaign-2 behaviour, run identical to before injection
    ev2.evaluate_generation(); ev2.reproduce()
    assert ev2.offspring_cap is None


# ---------------------------------------------------------------- campaign-3 prereg fields
def test_prereg_contract_has_campaign3_fields(tmp_path):
    from archaeon.campaign3.c3base import FIELDS_3
    assert {"why_this_slot", "kill_condition", "replacement_condition", "ancestry"} <= set(FIELDS_3) and "why_this_slot" not in P.FIELDS
    p = {f: "x" for f in FIELDS_3}; p["decl"] = {"n_min": 1}; p["parents"] = ["a"]; p["arms"] = ["a"]
    assert P.validate(p, FIELDS_3) == [] and P.validate({k: v for k, v in p.items() if k != "kill_condition"}, FIELDS_3) == ["kill_condition"]
    path = P.save(p, tmp_path, FIELDS_3)
    import json
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["sealed_fields"] == FIELDS_3 and P.unchanged(saved, saved["prereg_digest"])
    assert not P.unchanged(dict(saved, kill_condition="changed"), saved["prereg_digest"])       # the extra fields are in the seal
    assert "KILL CONDITION: x" in P.render(saved)
