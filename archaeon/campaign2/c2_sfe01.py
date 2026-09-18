"""C2-SFE-01 -- FAILURE-EPISODE TRANSPORT ON A REACHABLE TARGET (parent SFE-03).

    python -m archaeon.campaign2.c2_sfe01 [--seeds 1 2 3 4 5 6] [--N 200 --G 60 --E 16 --k 8] [--dry-run]

SFE-03's question, re-posed on a target the reachability table classes REACHABLE
(W2_K2 4-bit, N200 G60 E16: 4/9 baseline footholds): do transported FAILURE EPISODES
from a structurally RELEVANT source raise held-out competence above fresh search and
above random-compatible transport at matched evaluation budget?

Arms (six seeds; common random numbers; identical generation 0):
  fresh      the target's own training episodes only
  relevant   k transported episodes from W2_K2 8-bit (every structural knob equal to the
             target's; only the value width differs) -- episodes the source's final median
             organism FAILED, with the SOURCE's expected answers
  random     k transported episodes from W7_K2 4-bit (K=2, ASK2 combine: same grammar,
             different structure)
The k transported episodes REPLACE k of the E fresh training episodes every generation
(the step API takes the episode list; no monkeypatching); the count of generations in
which transport was applied is a row field (INTERVENTION_NOT_APPLIED fires on 0).
Packs are published by the source worlds (FAILURES_ONLY) with the source population's
maturity block, imported by the target world and fetched back: the target runs on the
bytes it fetched. Held-out: 48 episodes of the target's heldout family.
"""
from __future__ import annotations

import argparse
import sys
import time
from typing import Dict, List

from archaeon.wse import telemetry as T
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, evaluate, run_cell
from archaeon.wse.worlds import Episode, WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2, Experiment
from archaeon.campaign2.runner import CAMPAIGN_SEED

TARGET = WorldSpec("W2_K2", K=2, value_bits=4)
SOURCES = {"relevant": WorldSpec("W2_K2", K=2, value_bits=8),
           "random": WorldSpec("W7_K2", K=2, ask_kind="ASK2", value_bits=4)}
ARMS = ["fresh", "relevant", "random"]
CHANCE = 1.0 / 16


def relevance(src: WorldSpec, tgt: WorldSpec) -> dict:
    keys = ("K", "D", "ask_kind", "ask_mode", "op_mode", "topology", "delay")
    same = {k: getattr(src, k) == getattr(tgt, k) for k in keys}
    return {"rule": "all of K,D,ask_kind,ask_mode,op_mode,topology,delay equal (value_bits free)", "same": same, "relevant": all(same.values())}


def source_pack(job: dict) -> dict:
    """Run the source search; return k failure episodes of its LAST training family (the
    final population's median organism failed them) plus the source's maturity block."""
    spec, seed, N, G_, E, k = job["spec"], job["seed"], job["N"], job["G"], job["E"], job["k"]
    res = run_cell(spec, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, G_=G_, E=E, branch="c2-sfe01-src", foundry=FOUNDRY_C2)
    eps = episodes_for(spec, CAMPAIGN_SEED, "train", (G_ - 1) * 100003 + seed, E)
    pop = sorted(res["final_population"], key=lambda z: -z["reward"])
    probe = pop[len(pop) // 2]["manifest"]
    failed = []
    for ep in eps:
        if evaluate(probe, [ep], rng_seed=3)["reward"] < 1.0:
            failed.append({"ticks": ep.ticks, "expected": {str(kk): v for kk, v in ep.expected.items()},
                           "intervention_tick": ep.intervention_tick, "meta": {"cell": spec.name, "value_bits": spec.value_bits}})
    mat = T.maturity(spec.name, res["elite_eval"]["reward"], [z["reward"] for z in res["final_population"]], chance=CHANCE,
                     budget={"N": N, "G": G_, "E": E}, generation=res["generations"] - 1,
                     lineage={"elite_lineage_id": res["elite"]["lineage_id"], "ancestry_depth": len(res["ancestry"])})
    return {"source": job["name"], "seed": seed, "episodes": failed[:k], "n_failed_of": [len(failed), len(eps)], "maturity": mat,
            "first_solved_gen": res["first_solved_gen"], "trace_best": [t["best_reward"] for t in res["trace"]],
            "spec": {"N": N, "G": G_, "E": E}}


def run_arm(job: dict) -> dict:
    arm, seed, N, G_, E = job["arm"], job["seed"], job["N"], job["G"], job["E"]
    transported = [Episode(ticks=e["ticks"], expected={int(kk): v for kk, v in e["expected"].items()}, intervention_tick=e["intervention_tick"], meta=e["meta"])
                   for e in job["episodes"]]
    k = len(transported)
    t0 = time.time()
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c2-sfe01-" + arm, foundry=FOUNDRY_C2)
    applied = 0
    for g in range(G_):
        eps = None
        if k:
            eps = transported + ev.episodes()[: max(0, E - k)]
            applied += 1
        ev.evaluate_generation(episodes=eps, last=(g == G_ - 1))
        if g < G_ - 1:
            ev.reproduce()
    res = ev.result()
    ho = evaluate(res["elite"]["manifest"], episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48), rng_seed=7)
    return {"arm": arm, "seed": seed, "k": k, "transport_applied_gens": applied, "competence_heldout": ho["reward"],
            "train_last": res["elite_eval"]["reward"], "first_solved_gen": res["first_solved_gen"],
            "reached": 1 if res["first_solved_gen"] is not None else 0, "persist": ho["persist"], "ops_per_episode": ho["ops_per_episode"],
            "trace_best": [t["best_reward"] for t in res["trace"]], "elite_summary": res["elite_summary"],
            "gen0_provenance": res["gen0_provenance"], "warnings": res["warnings"], "wall_s": round(time.time() - t0, 1),
            "_res": res}


class Transport(Experiment):
    ID = "C2-SFE-01"
    TITLE = "failure-episode transport on a reachable target"
    PARENTS = ["SFE-03"]
    METRICS = ("competence_heldout", "train_last")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--G-source", type=int, default=60)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = Transport(dry_run=a.dry_run, procs=a.procs)
    reach = X.reachability_for([(TARGET, a.N, a.G, a.E, "E0")] + [(s, a.N, a.G_source, a.E, "E0") for s in SOURCES.values()])
    X.seal({
        "question": "Do k=%d transported FAILURE EPISODES from a structurally relevant source (W2_K2 8-bit) raise held-out competence on "
                    "W2_K2 4-bit above fresh search and above random-compatible transport (W7_K2) at matched evaluation budget?" % a.k,
        "parent_evidence": "SFE-03 (campaign 1): 0/9 rows reached W1_d4 at N200 G60; the question was never posed (INCONCLUSIVE). "
                           "Reachability table: W1_d4 4-bit RARE 1/6; W2_K2 4-bit N200 G60 E16 REACHABLE 4/9 (first solved 48-59).",
        "assay_capability_requirement": "the fresh arm reaches a foothold (training best >= 0.5) in >= 1 of %d seeds; otherwise TARGET_UNREACHABLE "
                                        "and the row of record is the reachability update, not a transport result" % len(a.seeds),
        "positive_control": "fresh arm on W2_K2 4-bit (own generation 0, no transport): expected 4/9 = 0.44 per seed; P(0 of %d) = %.3f" % (
            len(a.seeds), (1 - 4 / 9) ** len(a.seeds)),
        "reachability_estimate": reach,
        "arms": ARMS,
        "crn_policy": "default (rng_label=crn); identical generation 0 for the three arms per seed (gen0 with no substitution); "
                      "transported episodes replace the first k of E training episodes each generation",
        "budget": {"N": a.N, "G": a.G, "E": a.E, "k": a.k, "seeds": a.seeds, "G_source": a.G_source, "heldout_episodes": 48},
        "primary_observable": "competence_heldout (48 held-out episodes) of the elite, per arm x seed; footholds and first_solved_gen secondary",
        "claim_ceiling": "weak positive at best (n=%d, one target cell, one source per relevance class); a capable negative at this budget is evidence" % len(a.seeds),
        "falsification_condition": "relevant - fresh < 0.10 mean held-out with the fresh arm reaching >= 1 foothold => CAPABLE_NEGATIVE; "
                                   "relevant <= random => relevance is not the active ingredient",
        "typed_failure_conditions": ["TARGET_UNREACHABLE (fresh 0/%d)" % len(a.seeds), "INTERVENTION_NOT_APPLIED (transport_applied_gens == 0)",
                                     "UNDERPOWERED (< %d rows per arm)" % len(a.seeds), "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["first_solved_gen per row", "transport_applied_gens", "gen0_provenance", "source maturity per pack",
                                       "elite genome summary", "reachability rows appended (fresh arm baseline; others treated)"],
        "machine_changes_exercised": ["A reachability lookup in the prereg", "B typed states", "C CRN default + gen0 provenance", "D attempts/resume",
                                      "E maturity on packs", "F canonical digests + import hash checks", "G step API episode injection", "I generated record"],
        "decl": {"target": {"baseline_arm": "fresh", "reach_metric": "reached", "reach_min": 1, "reachability_class": reach["W2_K2"]["at_budget"]["class"]},
                 "positive_control": {"arm": "fresh", "metric": "reached", "min": 1, "min_rows": 1},
                 "interventions": [{"arm": "relevant", "counter": "transport_applied_gens"}, {"arm": "random", "counter": "transport_applied_gens"}],
                 "n_min": len(a.seeds),
                 "primary": {"treatment": "relevant", "control": "fresh", "metric": "competence_heldout", "min_effect": 0.10},
                 "artifact_policy": "packs carry maturity as telemetry; the transported material is EPISODES, not organisms, so maturity does not gate the assay (D2-006)"},
    })
    X.decision("D2-006: pack maturity is recorded, not gating (transported material is episodes; the source's own success is not required for its failures to be informative)")
    X.open("cmp2-sfe01", "C2-SFE-01 failure transport")
    src_w = {n: X.world("source-" + n, "FAILURES_ONLY") for n in SOURCES}
    tgt_w = X.world("target", "EXPLICIT_IMPORT_ONLY")
    X.publish_prereg(tgt_w)
    X.receipt["relevance"] = {n: relevance(s, TARGET) for n, s in SOURCES.items()}

    packs = X.pool_map(source_pack, [{"name": n, "spec": s, "seed": sd, "N": a.N, "G": a.G_source, "E": a.E, "k": a.k}
                                     for n, s in SOURCES.items() for sd in a.seeds], "sources_s")
    by = {(p["source"], p["seed"]): p for p in packs}
    X.receipt["packs"] = {"%s_s%d" % k: {kk: v for kk, v in p.items() if kk not in ("episodes", "trace_best")} | {"n_episodes": len(p["episodes"])} for k, p in by.items()}
    for (n, sd), p in by.items():
        X.reach_row(SOURCES[n], {"trace": [{"best_reward": b} for b in p["trace_best"]], "first_solved_gen": p["first_solved_gen"],
                                 "gen0_provenance": {"verified_common": True, "n_substituted": 0}, "solve_threshold": 0.5},
                    N=a.N, G=a.G_source, E=a.E, regime="E0", seed=sd, arm="source-" + n)
    t0 = time.time()
    for (n, sd), p in by.items():
        art = X.publish(src_w[n], "pack_%s_s%d" % (n, sd), "cmp2.failure_episodes.v1",
                        {"source": n, "seed": sd, "episodes": p["episodes"], "relevance": X.receipt["relevance"][n]},
                        {"info_kind": "failure", "seed": sd, "source": n}, maturity=p["maturity"])
        fetched = X.import_fetch("pack_%s_s%d" % (n, sd), tgt_w, src_w[n], art)
        if fetched is not None:
            by[(n, sd)]["episodes"] = fetched["episodes"]          # the target RUNS on what it fetched back
    X.att.timing("exchange_s", t0)

    jobs = []
    for sd in a.seeds:
        jobs.append({"arm": "fresh", "seed": sd, "episodes": [], "N": a.N, "G": a.G, "E": a.E})
        for n in SOURCES:
            jobs.append({"arm": n, "seed": sd, "episodes": by[(n, sd)]["episodes"], "N": a.N, "G": a.G, "E": a.E})
    rows = X.pool_map(run_arm, jobs, "targets_s")
    for r in rows:
        res = r.pop("_res")
        X.reach_row(TARGET, res, N=a.N, G=a.G, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["competence_heldout"],
                    kind=None if r["arm"] == "fresh" else "treated")     # episode injection is a treatment even with the common generation 0
    t0 = time.time()
    for r in rows:
        X.record(tgt_w, r, {"experiment": X.ID, "arm": r["arm"], "seed": r["seed"], "k": r["k"], "N": a.N, "G": a.G, "E": a.E, "target": TARGET.knobs(),
                            "relevance": X.receipt["relevance"].get(r["arm"]), "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("trace_best", "elite_summary", "gen0_provenance")},
                 "SURVIVED" if r["competence_heldout"] >= 0.5 else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    means = {arm: sum(r["competence_heldout"] for r in rows if r["arm"] == arm) / len(a.seeds) for arm in ARMS}
    X.receipt["effects"] = {"means": means, "relevant_minus_fresh": means["relevant"] - means["fresh"], "random_minus_fresh": means["random"] - means["fresh"],
                            "relevant_minus_random": means["relevant"] - means["random"],
                            "footholds": {arm: sum(r["reached"] for r in rows if r["arm"] == arm) for arm in ARMS}}
    out = X.close(rows, meas_extra={"pack_maturity": {k: v["maturity"] for k, v in X.receipt["packs"].items()}})
    print(__import__("json").dumps({"effects": X.receipt["effects"], "packs": {k: (v["maturity"]["source_elite_reward"], v["maturity"]["solved"], v["n_episodes"])
                                                                              for k, v in X.receipt["packs"].items()}, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
