"""C2-SFE-07 -- PRODUCER-CONSUMER: MATURITY GATING AND WALL-CLOCK ACCOUNTING (parent SFE-10).

    python -m archaeon.campaign2.c2_sfe07 [--seeds 1..6] [--N 200 --G 60 --E 16] [--producer-cap 30] [--dry-run]

SFE-10 (campaign 1) charged all production against the consumer's generations and found a
capable negative; the only paying exchange came from the one producer that had SOLVED its
own cell. Two principled changes to the economics, both preserving explicit communication
(ceil(bytes/4096) generations) and storage (0.5 generation per artifact held) costs:

  mono                the consumer spends the whole envelope (G) on the target W2_K2 4-bit
  gated_serial        a producer searches W0 4-bit until it SOLVES (stop rule; cap
                      producer_cap generations) and publishes only then (the gate is the
                      maturity block's `solved`); the consumer pays producer generations +
                      comm + storage out of the same envelope and starts from the fetched
                      top-4 elites substituted into its own generation 0 (common_fill). A
                      producer that never solves publishes nothing and still costs its cap.
  gated_serial_noex   the same reduced consumer budget, no import (budget loss alone)
  parallel            the producer runs on ITS OWN clock; the consumer runs the whole
                      envelope minus storage and, at consumer generation t_solve + comm,
                      the fetched elites are INJECTED into the running population (they
                      compete from that generation on); no producer -> identical to mono

Observables per arm x seed: held-out competence, first foothold generation (>= 0.5: the
half-credit shelf of a K=2 cell, C2-SFE-03), first FULL solve generation (>= 0.9), producer
solve time, costs charged, arrival generation, import lineage share at the end. The
break-even per seed is read off the rows: producer solve time + comm + storage against
mono's own exit generation.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from typing import Dict, List, Optional

from archaeon.wse import digest as D
from archaeon.wse import telemetry as T
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, common_fill, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2, Experiment
from archaeon.campaign2.runner import CAMPAIGN_SEED

TARGET = WorldSpec("W2_K2", K=2, value_bits=4)
SOURCE = WorldSpec("W0", value_bits=4)
ARMS = ["mono", "gated_serial", "gated_serial_noex", "parallel"]
COMM_BYTES_PER_GEN = 4096
STORAGE_GEN_PER_ARTIFACT = 0.5
TOP_K = 4
CHANCE = 1.0 / 16
FULL = 0.9


def run_producer(job: dict) -> dict:
    seed, N, E, cap = job["seed"], job["N"], job["E"], job["cap"]
    ev = Evolution(SOURCE, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c2-sfe07-producer", foundry=FOUNDRY_C2)
    for g in range(cap):
        last = g == cap - 1 or ev.first_solved_gen is not None
        ev.evaluate_generation(last=last)
        if ev.first_solved_gen is not None or last:
            break
        ev.reproduce()
    res = ev.result()
    mat = T.maturity(SOURCE.name, res["elite_eval"]["reward"], [z["reward"] for z in res["final_population"]], chance=CHANCE,
                     budget={"N": N, "G": res["generations"], "E": E, "cap": cap}, generation=res["generations"] - 1,
                     lineage={"elite_lineage_id": res["elite"]["lineage_id"], "ancestry_depth": len(res["ancestry"])})
    return {"seed": seed, "generations": res["generations"], "first_solved_gen": res["first_solved_gen"], "solved": mat["solved"], "maturity": mat,
            "elites": [e["manifest"] for e in res["final_elites"][:TOP_K]], "trace_best": [t["best_reward"] for t in res["trace"]], "_res": res}


def inject(ev: Evolution, manifests: List[dict], tag: str) -> int:
    """Imported organisms enter the CURRENT scored generation in place of its worst members and
    compete from this generation on (elitism and tournament see them)."""
    from proteus.foundry import generate as G
    eps = ev.episodes()
    from proteus.foundry.prng import seed_from
    rs = seed_from("wse.eval", ev.campaign_seed, ev.g, ev.cell_seed)
    new = []
    for m in manifests:
        org = G.organism_record(dict(m), None, ev.g); org["origins"] = [tag]
        e = evaluate(m, eps, rng_seed=rs)
        new.append((ev.regime.fitness(e["reward"], e["meter"], ev.E, multiplier=ev.multiplier()), org, e))
    scored = sorted(ev.scored, key=lambda z: -z[0])
    scored = scored[: max(0, len(scored) - len(new))] + new
    scored.sort(key=lambda z: -z[0])
    ev.scored = scored
    ev.pop = [z[1] for z in scored]
    return len(new)


def run_consumer(job: dict) -> dict:
    arm, seed, N, E, G_total = job["arm"], job["seed"], job["N"], job["E"], job["G"]
    imports: Optional[List[dict]] = job.get("imports")
    nbytes = job.get("bytes", 0)
    comm = int(math.ceil(nbytes / COMM_BYTES_PER_GEN)) if imports else 0
    storage = STORAGE_GEN_PER_ARTIFACT if imports else 0.0
    producer_gens = job.get("producer_gens", 0)
    t0 = time.time()
    init, prov, arrival = None, None, None
    if arm == "mono":
        G_ = G_total
    elif arm in ("gated_serial", "gated_serial_noex"):
        G_ = int(G_total - producer_gens - comm - storage)
        if arm == "gated_serial" and imports:
            init, prov = common_fill(CAMPAIGN_SEED, seed, N, imports, tag="import", foundry=FOUNDRY_C2)
    else:                                                                  # parallel
        G_ = int(G_total - storage)
        arrival = (job["t_solve"] + comm) if imports else None
    G_ = max(1, G_)
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c2-sfe07-" + arm, foundry=FOUNDRY_C2, init_pop=init, gen0_provenance=prov)
    injected_at = None
    for g in range(G_):
        ev.evaluate_generation(last=(g == G_ - 1))
        if arrival is not None and g >= arrival and injected_at is None:
            inject(ev, imports, "import"); injected_at = g
        if g < G_ - 1:
            ev.reproduce()
    res = ev.result()
    ho = evaluate(res["elite"]["manifest"], episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48), rng_seed=7)
    tb = [t["best_reward"] for t in res["trace"]]
    full = next((i for i, b in enumerate(tb) if b >= FULL), None)
    return {"arm": arm, "seed": seed, "consumer_G": G_, "producer_gens": producer_gens, "comm_gens": comm, "storage_gens": storage, "bytes": nbytes,
            "arrival_gen": injected_at, "imported": bool(imports), "competence_heldout": ho["reward"], "train_last": res["elite_eval"]["reward"],
            "first_solved_gen": res["first_solved_gen"], "reached": 1 if res["first_solved_gen"] is not None else 0, "full_solve_gen": full, "full": 1 if full is not None else 0,
            "charged_gen_at_foothold": (None if res["first_solved_gen"] is None else res["first_solved_gen"] + (producer_gens + comm + storage if arm.startswith("gated") else storage)),
            "import_share_final": res["trace"][-1]["origin_shares"].get("import", 0.0), "elite_origins": res["elite_origins"], "persist": ho["persist"],
            "elite_summary": res["elite_summary"], "trace_best": tb, "gen0_provenance": res["gen0_provenance"], "warnings": res["warnings"],
            "wall_s": round(time.time() - t0, 1), "_res": res}


class ProducerConsumer(Experiment):
    ID = "C2-SFE-07"
    TITLE = "producer-consumer: maturity gating and wall-clock accounting"
    PARENTS = ["SFE-10"]
    METRICS = ("competence_heldout", "first_solved_gen", "charged_gen_at_foothold", "full_solve_gen")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--producer-cap", type=int, default=30)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = ProducerConsumer(dry_run=a.dry_run, procs=a.procs)
    reach = X.reachability_for([(TARGET, a.N, a.G, a.E, "E0"), (SOURCE, a.N, a.producer_cap, a.E, "E0")])
    X.seal({
        "question": "Under a %d-generation envelope with explicit communication (ceil(bytes/4096) gens) and storage (0.5 gen/artifact) costs, does a producer on "
                    "W0 4-bit that publishes ONLY once it has solved its cell (maturity gate) pay for itself when charged serially, and does it pay when it "
                    "runs on its own clock and its elites are injected mid-run (wall-clock accounting)?" % a.G,
        "parent_evidence": "SFE-10: mono 3/3 vs pc_0.4 1/3, pc_0.2 0/3 (CAPABLE_NEGATIVE); the one paying exchange came from a producer that solved W0 (1.0 at G12). "
                           "C2-SFE-03/04: solved-W0 material lands on the K=2 half-credit shelf directly. Table: W2_K2 4-bit N200 G60 7/17; W0 4-bit COMMON by ~G35.",
        "assay_capability_requirement": "mono reaches a foothold in >= 1 of %d seeds (TARGET_UNREACHABLE otherwise); >= 1 producer solves within the cap "
                                        "(else no gated exchange happens and the rows record the cost of closed gates)" % len(a.seeds),
        "positive_control": "mono on W2_K2 4-bit (own generation 0): expected 0.41 per seed",
        "reachability_estimate": reach,
        "arms": ARMS,
        "crn_policy": "default; the same producer run per seed feeds both exchange arms; consumers share generation 0 (gated_serial substitutes the fetched "
                      "top-%d into it; parallel injects them at arrival)" % TOP_K,
        "budget": {"N": a.N, "G": a.G, "E": a.E, "producer_cap": a.producer_cap, "seeds": a.seeds, "comm_bytes_per_gen": COMM_BYTES_PER_GEN,
                   "storage_gen_per_artifact": STORAGE_GEN_PER_ARTIFACT, "top_k": TOP_K, "heldout_episodes": 48, "full_solve": FULL},
        "primary_observable": "competence_heldout per arm x seed (parallel vs mono; gated_serial vs mono secondary); first_solved_gen, charged generation at "
                              "foothold and full_solve_gen as the economics",
        "claim_ceiling": "weak at best (n=%d, one source/target pair); the break-even generation (producer solve time + comm + storage vs mono's exit) is the product" % len(a.seeds),
        "falsification_condition": "parallel - mono < 0.10 held-out => wall-clock division of labour does not pay at this envelope; gated_serial - mono < 0.10 => "
                                   "serial gating does not pay",
        "typed_failure_conditions": ["TARGET_UNREACHABLE (mono 0/%d)" % len(a.seeds), "IMMATURE_ARTIFACT cannot occur by construction (gate); a closed gate is a row "
                                     "with imported=false", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["producer solve time and maturity", "costs charged per row", "arrival generation", "import lineage share at the end",
                                       "first foothold and first full solve generations", "reachability rows (mono baseline)"],
        "machine_changes_exercised": ["E (gate = maturity.solved; publish requires it)", "G (mid-run injection through the step API)", "C (common_fill substitution)",
                                      "D", "F (costs from canonical bytes)", "H (origin shares)", "I"],
        "decl": {"target": {"baseline_arm": "mono", "reach_metric": "reached", "reach_min": 1, "reachability_class": reach["W2_K2"]["at_budget"]["class"]},
                 "n_min": len(a.seeds),
                 "primary": {"treatment": "parallel", "control": "mono", "metric": "competence_heldout", "min_effect": 0.10}},
    })
    X.decision("D2-015: the maturity gate is the artifact's `solved` flag; an unsolved producer publishes nothing and the consumer still pays its cap (the cost of a closed gate is a measurement, not a failure)")
    X.open("cmp2-sfe07", "C2-SFE-07 producer-consumer")
    w_p = X.world("producer", "FULLY_SHARED")
    w_c = X.world("consumer", "EXPLICIT_IMPORT_ONLY")
    X.publish_prereg(w_c)

    prods = X.pool_map(run_producer, [{"seed": s, "N": a.N, "E": a.E, "cap": a.producer_cap} for s in a.seeds], "producers_s")
    P = {p["seed"]: p for p in prods}
    for p in prods:
        res = p.pop("_res")
        X.reach_row(SOURCE, res, N=a.N, G=p["generations"], E=a.E, regime="E0", seed=p["seed"], arm="producer", kind="treated")
    X.receipt["producers"] = {s: {"generations": p["generations"], "first_solved_gen": p["first_solved_gen"], "solved": p["solved"],
                                  "elite": p["maturity"]["source_elite_reward"]} for s, p in P.items()}
    t0 = time.time()
    fetched: Dict[int, dict] = {}
    for s, p in P.items():
        if not p["solved"]:
            continue                                                       # the gate: nothing published
        art = X.publish(w_p, "elites_s%d" % s, "cmp2.pop.producer_elites.v1", {"seed": s, "manifests": p["elites"]}, {"info_kind": "success", "seed": s}, maturity=p["maturity"])
        obj = X.import_fetch("elites_s%d" % s, w_c, w_p, art)
        fetched[s] = {"manifests": (obj["manifests"] if obj else p["elites"]), "bytes": art.get("bytes") or len(D.canonical_bytes({"seed": s, "manifests": p["elites"]}))}
    X.att.timing("exchange_s", t0)

    jobs = []
    for s in a.seeds:
        p = P[s]; f = fetched.get(s)
        jobs.append({"arm": "mono", "seed": s, "N": a.N, "G": a.G, "E": a.E})
        jobs.append({"arm": "gated_serial", "seed": s, "N": a.N, "G": a.G, "E": a.E, "producer_gens": p["generations"], "imports": f["manifests"] if f else None,
                     "bytes": f["bytes"] if f else 0})
        jobs.append({"arm": "gated_serial_noex", "seed": s, "N": a.N, "G": a.G, "E": a.E, "producer_gens": p["generations"],
                     "imports": None, "bytes": f["bytes"] if f else 0})
        jobs.append({"arm": "parallel", "seed": s, "N": a.N, "G": a.G, "E": a.E, "imports": f["manifests"] if f else None, "bytes": f["bytes"] if f else 0,
                     "t_solve": p["first_solved_gen"] if p["solved"] else None})
    # noex arms must pay comm+storage of the artifact they did NOT fetch only if the design says so: they pay producer generations only (budget loss alone)
    for j in jobs:
        if j["arm"] == "gated_serial_noex":
            j["bytes"] = 0
    rows = X.pool_map(run_consumer, jobs, "consumers_s")
    for r in rows:
        res = r.pop("_res")
        X.reach_row(TARGET, res, N=a.N, G=r["consumer_G"], E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["competence_heldout"],
                    kind=None if r["arm"] in ("mono", "gated_serial_noex") else "treated")
    t0 = time.time()
    for r in rows:
        X.record(w_c, r, {"experiment": X.ID, "arm": r["arm"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E, "costs": {"comm": r["comm_gens"], "storage": r["storage_gens"],
                          "producer_gens": r["producer_gens"]}, "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("trace_best", "elite_summary", "gen0_provenance")},
                 "SURVIVED" if r["competence_heldout"] >= 0.5 else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    summ = {}
    for arm in ARMS:
        rs = sorted([r for r in rows if r["arm"] == arm], key=lambda r: r["seed"])
        summ[arm] = {"heldout": [round(r["competence_heldout"], 3) for r in rs], "footholds": sum(r["reached"] for r in rs), "first": [r["first_solved_gen"] for r in rs],
                     "charged_at_foothold": [r["charged_gen_at_foothold"] for r in rs], "full": sum(r["full"] for r in rs), "consumer_G": [r["consumer_G"] for r in rs],
                     "imported": [r["imported"] for r in rs], "import_share_final": [round(r["import_share_final"], 2) for r in rs]}
    X.receipt["summary"] = summ
    X.receipt["break_even"] = {s: {"producer_solve": P[s]["first_solved_gen"], "producer_gens": P[s]["generations"],
                                   "mono_exit": next((r["first_solved_gen"] for r in rows if r["arm"] == "mono" and r["seed"] == s), None)} for s in a.seeds}
    out = X.close(rows)
    print(json.dumps({"summary": summ, "producers": X.receipt["producers"], "break_even": X.receipt["break_even"], **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
