"""C2-SFE-04 -- FALSIFY SFE-07's FAILED-GENOTYPE SEEDING (parents SFE-07, SFE-08).

    python -m archaeon.campaign2.c2_sfe04 [--seeds 1..10] [--N 100 --G 40 --E 16] [--dry-run]

SFE-07 (campaign 1): 100 genotypes that FAILED World A (W1_d1 floor organisms of SFE-01's
source searches, manifests rebuilt) used as the whole generation 0 of a W3_K2 4-bit search
(N100 G40 E16) reached footholds 2/3 vs 100 random genotypes 0/3; SFE-08 found that
length-defined ORGANS of the same lineages carried nothing. What is the smallest description
of what a failed population transports? Sets (each replaces the WHOLE generation 0 through
common_fill; the random arm is the cell's own generation 0; ten seeds; same budget as the
parent so the parent's regime is kept):

  random               the cell's own generation 0                                   [primary control]
  failed_A             SFE-01's failed W1_d1 genotypes (fetched from campaign 1's engine
                       world), manifests rebuilt by SFE-07's recipe
  failed_shuffled      the same genomes, instruction order permuted                  [kill: composition suffices?]
  failed_opcodes       the same opcode words, operand words random                   [kill: opcodes suffice?]
  length_matched       random genomes with the failed set's instruction counts        [kill: length suffices?]
  evolved_unrelated    floor genotypes of a W7_K2 4-bit search (ASK2 combine)         [kill: any evolved floor?]
  evolved_solved       the final population of a W0 4-bit search run to solution     [probe: maturity / relatedness]

Assay capability: ANY arm reaches (the premise is that the baseline may not). Direct reuse
(best held-out of any member without evolution) is recorded per set. Every evolved set is
published with its source population's maturity block and fetched back before use.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List, Optional

from proteus.foundry import generate as G
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.wse import telemetry as T
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, common_fill, evaluate, run_cell
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2, REPO, Experiment
from archaeon.campaign2.runner import CAMPAIGN_SEED

WORLD_B = WorldSpec("W3_K2", K=2, ask_mode="one", value_bits=4)
SRC_UNRELATED = WorldSpec("W7_K2", K=2, ask_kind="ASK2", value_bits=4)
SRC_SOLVED = WorldSpec("W0", value_bits=4)
ARMS = ["random", "failed_A", "failed_shuffled", "failed_opcodes", "length_matched", "evolved_unrelated", "evolved_solved"]
KILL = ["failed_shuffled", "failed_opcodes", "length_matched", "evolved_unrelated"]
PROBES = ["evolved_solved"]
CHANCE = 1.0 / 16
MASK32 = 0xFFFFFFFF
MASK62 = (1 << 62) - 1
from proteus.foundry.vm import SCHEMA                          # noqa: E402


def manifest_from_genome(genome: List[int], seed: int) -> dict:
    """SFE-07's recipe: the genome is the only thing carried; every other field is a seeded draw."""
    from proteus.foundry.vm import validate_manifest
    rng = SplitMix64(seed_from("cmp1.sfe07.rebuild", seed, tuple(genome)))
    tape_choices = [t for t in (16, 32, 64, 128, 256) if t >= len(genome)] or [256]
    m = {"schema_version": SCHEMA, "n_regs": rng.randint(2, 16),
         "tape_words": tape_choices[rng.randbelow(len(tape_choices))], "genome": list(genome), "code_writable": bool(rng.randbelow(2)),
         "persist": ["none", "regs", "tape", "all"][rng.randbelow(4)], "tick_budget": [16, 64, 256][rng.randbelow(3)], "out_cap": [1, 4][rng.randbelow(2)]}
    try:
        validate_manifest(m)
    except Exception:                                            # noqa: BLE001
        base = G.generate(dict(FOUNDRY_C2, seed=seed & MASK62, n=1))[0]["manifest"]
        m["schema_version"] = base["schema_version"]
        validate_manifest(m)
    return m


def shuffle_genome(g: List[int], rng: SplitMix64) -> List[int]:
    ins = [g[i:i + 4] for i in range(0, len(g), 4)]
    for i in range(len(ins) - 1, 0, -1):
        j = rng.randbelow(i + 1); ins[i], ins[j] = ins[j], ins[i]
    return [w for ii in ins for w in ii]


def opcode_only(g: List[int], rng: SplitMix64) -> List[int]:
    return [w if i % 4 == 0 else (rng.next_u32() & MASK32) for i, w in enumerate(g)]


def random_same_length(g: List[int], rng: SplitMix64) -> List[int]:
    return [rng.next_u32() & MASK32 for _ in g]


def derive(genomes: List[List[int]], mode: str, seed: int) -> List[List[int]]:
    rng = SplitMix64(seed_from("c2.sfe04.derive", CAMPAIGN_SEED, seed, mode))
    f = {"failed_shuffled": shuffle_genome, "failed_opcodes": opcode_only, "length_matched": random_same_length}[mode]
    return [f(g, rng) for g in genomes]


def set_summary(genomes: List[List[int]]) -> dict:
    return T.population_summary([{"genome": g} for g in genomes])


# ------------------------------------------------------------------ sources
def run_source(job: dict) -> dict:
    spec, seed, N, G_, E, mode = job["spec"], job["seed"], job["N"], job["G"], job["E"], job["mode"]
    ev = Evolution(spec, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c2-sfe04-src-" + mode, foundry=FOUNDRY_C2)
    stop_at = None
    for g in range(G_):
        last = g == G_ - 1 or (stop_at is not None and g >= stop_at)
        ev.evaluate_generation(last=last)
        if mode == "solved" and ev.first_solved_gen is not None and stop_at is None:
            stop_at = g + 3
        if last:
            break
        ev.reproduce()
    res = ev.result()
    pop = res["final_population"]
    if mode == "unrelated":
        genomes = [z["manifest"]["genome"] for z in pop if z["reward"] == 0.0][:100]
    else:
        genomes = [z["manifest"]["genome"] for z in sorted(pop, key=lambda z: -z["reward"])][:100]
    mat = T.maturity(spec.name, res["elite_eval"]["reward"], [z["reward"] for z in pop], chance=CHANCE, budget={"N": N, "G": res["generations"], "E": E},
                     generation=res["generations"] - 1, lineage={"elite_lineage_id": res["elite"]["lineage_id"], "ancestry_depth": len(res["ancestry"])})
    return {"mode": mode, "seed": seed, "genomes": genomes, "maturity": mat, "first_solved_gen": res["first_solved_gen"], "generations": res["generations"],
            "n_floor": sum(1 for z in pop if z["reward"] == 0.0), "trace_best": [t["best_reward"] for t in res["trace"]], "_res": res}


# ------------------------------------------------------------------ target
def run_arm(job: dict) -> dict:
    arm, seed, N, G_, E = job["arm"], job["seed"], job["N"], job["G"], job["E"]
    t0 = time.time()
    eps = episodes_for(WORLD_B, CAMPAIGN_SEED, "heldout", seed, 48)
    direct_best = None
    if arm == "random":
        init, prov = None, None
    else:
        mans = [manifest_from_genome(g, seed) for g in job["genomes"][:N]]
        direct_best = 0.0
        for m in mans:
            try:
                direct_best = max(direct_best, evaluate(m, eps, rng_seed=7)["reward"])
            except Exception:                                        # noqa: BLE001
                pass
        init, prov = common_fill(CAMPAIGN_SEED, seed, N, mans, tag=arm, foundry=FOUNDRY_C2)
    res = run_cell(WORLD_B, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, G_=G_, E=E, init_pop=init, gen0_provenance=prov, branch="c2-sfe04-" + arm, foundry=FOUNDRY_C2)
    ho = evaluate(res["elite"]["manifest"], eps, rng_seed=7)
    return {"arm": arm, "seed": seed, "competence_heldout": ho["reward"], "train_last": res["elite_eval"]["reward"], "first_solved_gen": res["first_solved_gen"],
            "reached": 1 if res["first_solved_gen"] is not None else 0, "direct_best": direct_best, "n_members": len(job.get("genomes") or []),
            "persist": ho["persist"], "elite_summary": res["elite_summary"], "elite_origins": res["elite_origins"],
            "import_share_final": res["trace"][-1]["origin_shares"].get(arm, 0.0) if arm != "random" else None,
            "trace_best": [t["best_reward"] for t in res["trace"]], "gen0_provenance": res["gen0_provenance"], "warnings": res["warnings"],
            "wall_s": round(time.time() - t0, 1), "_res": res}


class Falsify07(Experiment):
    ID = "C2-SFE-04"
    TITLE = "falsify SFE-07's failed-genotype seeding (n=10, battery)"
    PARENTS = ["SFE-07", "SFE-08"]
    METRICS = ("competence_heldout", "train_last", "direct_best")


def fetch_failed_A(X: Falsify07) -> tuple:
    """SFE-01's failure artifacts, read from campaign 1's TERMINATED source world under campaign
    1's own principal (D-013); returns (genomes, provenance)."""
    r1 = json.loads((REPO / "archaeon" / "campaign1" / "SFE-01" / "RECEIPT.json").read_text(encoding="utf-8"))
    if X.dry_run:
        fm = dict(FOUNDRY_C2, seed=4040, n=100)
        return [o["manifest"]["genome"] for o in G.generate(fm)], {"dry_run": True, "note": "random genomes stand in for failed_A in a dry run"}
    rd = X.eng.read_campaign1()
    genomes, prov = [], {"world": r1["worlds"]["source"], "artifacts": {}, "dry_run": False}
    for s, ids in sorted(r1["artifacts"].items()):
        obj, info = X.att.step("fetch_failed_A", lambda s=s, ids=ids: X.eng.fetch(r1["worlds"]["source"], ids["failures"], expected=ids.get("failures_hash"), client=rd),
                               parts=(s,), kind="engine")
        prov["artifacts"][s] = dict(info, n=len(obj.get("failures", [])), n_floor=obj.get("n_floor"), n_pop=obj.get("n_pop"))
        genomes.extend(obj.get("failures", []))
    return genomes, prov


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=list(range(1, 11)))
    ap.add_argument("--N", type=int, default=100)
    ap.add_argument("--G", type=int, default=40)
    ap.add_argument("--G-source", type=int, default=60)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--margin", type=float, default=0.10)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = Falsify07(dry_run=a.dry_run, procs=a.procs)
    reach = X.reachability_for([(WORLD_B, a.N, a.G, a.E, "E0"), (SRC_UNRELATED, 200, a.G_source, a.E, "E0"), (SRC_SOLVED, 200, a.G_source, a.E, "E0")])
    battery = [{"name": k, "type": "kill", "rule": "failed_A - %s >= %.2f mean held-out" % (k, a.margin)} for k in KILL]
    X.seal({
        "question": "Do genotypes that FAILED W1_d1 (SFE-01's floor organisms), used as the whole generation 0, raise held-out competence on W3_K2 4-bit "
                    "over the cell's own generation 0 (SFE-07: 2/3 vs 0/3 at n=3), and if so what is the smallest description of the transported thing: "
                    "instruction order, opcode composition, genome length, 'any evolved floor', or a solved related population?",
        "parent_evidence": "SFE-07 attempt 2: failed_A 2/3 footholds vs random 0/3 (N100 G40 E16); SFE-08: length-defined organs of the same lineages at floor. "
                           "Campaign-1 fill for these sets was harness-seeded (L2-011). Table: W3_K2 4-bit N100 G40 E16 0/3 OBSERVED_UNREACHABLE_AT_BUDGET.",
        "assay_capability_requirement": "ANY arm reaches a foothold in >= 1 of %d seeds (the baseline may be unreachable by premise); every set has >= %d members" % (len(a.seeds), a.N),
        "positive_control": "none separate: the assay is capable iff some arm reaches (target baseline_arm '*'); the random arm measures the cell's own reach",
        "reachability_estimate": reach,
        "arms": ARMS,
        "crn_policy": "default; every set replaces the whole generation 0 through common_fill (tagged); the random arm is the untouched generation 0; "
                      "derived sets (shuffled / opcodes / length) are deterministic functions of failed_A keyed on the seed",
        "budget": {"N": a.N, "G": a.G, "E": a.E, "G_source": a.G_source, "seeds": a.seeds, "heldout_episodes": 48, "margin": a.margin},
        "primary_observable": "competence_heldout of the elite per arm x seed; primary comparison failed_A vs random; direct_best per set as telemetry",
        "claim_ceiling": "SUPPORTED_POSITIVE only if failed_A - random >= %.2f AND every kill attack survives by the same margin; otherwise WEAK_POSITIVE / CAPABLE_NEGATIVE" % a.margin,
        "falsification_condition": "failed_A - random < %.2f => the SFE-07 effect does not replicate; a kill arm within %.2f of failed_A => that description suffices" % (a.margin, a.margin),
        "typed_failure_conditions": ["TARGET_UNREACHABLE (no arm reaches)", "UNDERPOWERED", "IMMATURE_ARTIFACT recorded on failed_A (its source is immature by construction; telemetry, D2-011)",
                                     "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["direct_best per set", "set summaries (length, opcode categories)", "import_share_final (share of the final population descending from the set)",
                                       "source maturity per set", "first_solved_gen", "reachability rows (random arm baseline)"],
        "machine_changes_exercised": ["B (target '*' + battery)", "C (common_fill whole-population substitution)", "D (cross-campaign fetch as keyed steps)",
                                      "E (maturity on evolved sets)", "F (canonical digests on campaign-1 artifacts)", "G", "H (origin shares)", "I"],
        "decl": {"target": {"baseline_arm": "*", "reach_metric": "reached", "reach_min": 1, "reachability_class": reach["W3_K2"]["at_budget"]["class"]},
                 "n_min": len(a.seeds),
                 "primary": {"treatment": "failed_A", "control": "random", "metric": "competence_heldout", "min_effect": a.margin},
                 "battery": battery, "probes": PROBES},
    })
    X.decision("D2-012: assay capability = ANY arm reaches (target baseline_arm '*'); the premise of a transport-unlocks-an-unreachable-cell design is that the baseline may not reach")
    X.open("cmp2-sfe04", "C2-SFE-04 failed-genotype falsification")
    w_unr = X.world("source-unrelated", "FULLY_SHARED")
    w_sol = X.world("source-solved", "FULLY_SHARED")
    w_b = X.world("world-B", "EXPLICIT_IMPORT_ONLY")
    X.publish_prereg(w_b)

    t0 = time.time()
    failed, fprov = fetch_failed_A(X)
    X.receipt["failed_A_fetch"] = fprov | {"n_genomes": len(failed)}
    X.att.timing("fetch_s", t0)
    n_floor = sum(v.get("n_floor") or 0 for v in fprov.get("artifacts", {}).values()) or len(failed)
    n_pop = sum(v.get("n_pop") or 0 for v in fprov.get("artifacts", {}).values()) or 200 * 3
    failed_mat = T.maturity("W1_d1", 0.125, [0.0] * n_floor + [0.125] * max(0, n_pop - n_floor), chance=CHANCE,
                            budget={"N": 200, "G": 100, "E": 16, "campaign": "cmp1/SFE-01"}, lineage={"reconstructed": True, "note": "SFE-01 source elites 0.0625-0.125"})
    jobs = [{"spec": SRC_UNRELATED, "seed": s, "N": 200, "G": a.G_source, "E": a.E, "mode": "unrelated"} for s in a.seeds] + \
           [{"spec": SRC_SOLVED, "seed": s, "N": 200, "G": a.G_source, "E": a.E, "mode": "solved"} for s in a.seeds]
    srcs = X.pool_map(run_source, jobs, "sources_s")
    unr = {r["seed"]: r for r in srcs if r["mode"] == "unrelated"}
    sol = {r["seed"]: r for r in srcs if r["mode"] == "solved"}
    for r in srcs:
        res = r.pop("_res")
        X.reach_row(SRC_UNRELATED if r["mode"] == "unrelated" else SRC_SOLVED, res, N=200, G=r["generations"], E=a.E, regime="E0", seed=r["seed"],
                    arm="source-" + r["mode"], kind="baseline" if r["mode"] == "unrelated" else "treated")
    X.receipt["sources"] = {m: {s: {"elite": r["maturity"]["source_elite_reward"], "solved": r["maturity"]["solved"], "n": len(r["genomes"]), "n_floor": r["n_floor"],
                                    "first_solved_gen": r["first_solved_gen"], "generations": r["generations"]} for s, r in d.items()} for m, d in (("unrelated", unr), ("solved", sol))}

    # publish + fetch back every evolved set (maturity required by kind cmp2.pop.*)
    t0 = time.time()
    art = X.publish(w_b, "failed_A", "cmp2.pop.set.v1", {"set": "failed_A", "genomes": failed[:a.N], "provenance": fprov}, {"info_kind": "failure"}, maturity=failed_mat)
    if not X.dry_run:
        objf, info = X.att.step("fetch_native", lambda: X.eng.fetch(w_b, art["artifact_id"], expected=art["declared"]), parts=("failed_A",), kind="engine")
        X.receipt["imports"]["failed_A"] = info
        failed_used = objf["genomes"]
    else:
        failed_used = failed[:a.N]
    sets: Dict[int, Dict[str, List[List[int]]]] = {}
    for s in a.seeds:
        au = X.publish(w_unr, "unrelated_s%d" % s, "cmp2.pop.set.v1", {"set": "evolved_unrelated", "seed": s, "genomes": unr[s]["genomes"]},
                       {"info_kind": "failure", "seed": s}, maturity=unr[s]["maturity"])
        ou = X.import_fetch("unrelated_s%d" % s, w_b, w_unr, au)
        asol = X.publish(w_sol, "solved_s%d" % s, "cmp2.pop.set.v1", {"set": "evolved_solved", "seed": s, "genomes": sol[s]["genomes"]},
                         {"info_kind": "success", "seed": s}, maturity=sol[s]["maturity"])
        osol = X.import_fetch("solved_s%d" % s, w_b, w_sol, asol)
        sets[s] = {"random": None, "failed_A": failed_used, "failed_shuffled": derive(failed_used, "failed_shuffled", s),
                   "failed_opcodes": derive(failed_used, "failed_opcodes", s), "length_matched": derive(failed_used, "length_matched", s),
                   "evolved_unrelated": (ou["genomes"] if ou else unr[s]["genomes"]), "evolved_solved": (osol["genomes"] if osol else sol[s]["genomes"])}
    X.att.timing("exchange_s", t0)
    X.receipt["set_summaries"] = {arm: set_summary(sets[a.seeds[0]][arm]) for arm in ARMS if sets[a.seeds[0]][arm]}
    X.receipt["set_summaries"]["random_gen0"] = set_summary([o["manifest"]["genome"] for o in G.generate(dict(FOUNDRY_C2, seed=1, n=100))])
    X.att.save()

    jobs = [{"arm": arm, "seed": s, "N": a.N, "G": a.G, "E": a.E, "genomes": sets[s][arm]} for s in a.seeds for arm in ARMS
            if arm == "random" or (sets[s][arm] and len(sets[s][arm]) >= 10)]
    rows = X.pool_map(run_arm, jobs, "targets_s")
    for r in rows:
        res = r.pop("_res")
        X.reach_row(WORLD_B, res, N=a.N, G=a.G, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["competence_heldout"])
    t0 = time.time()
    for r in rows:
        X.record(w_b, r, {"experiment": X.ID, "arm": r["arm"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E, "world_B": WORLD_B.knobs(), "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("trace_best", "elite_summary", "gen0_provenance")},
                 "SURVIVED" if r["competence_heldout"] >= 0.5 else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    n_arm = {arm: sum(1 for r in rows if r["arm"] == arm) for arm in ARMS}
    means = {arm: (sum(r["competence_heldout"] for r in rows if r["arm"] == arm) / n_arm[arm]) if n_arm[arm] else None for arm in ARMS}
    foot = {arm: sum(r["reached"] for r in rows if r["arm"] == arm) for arm in ARMS}
    direct = {arm: (sum((r["direct_best"] or 0) for r in rows if r["arm"] == arm) / n_arm[arm]) if n_arm[arm] and arm != "random" else None for arm in ARMS}
    batt = [{"name": b["name"], "type": "kill", "passed": bool(means[b["name"]] is not None and means["failed_A"] is not None and means["failed_A"] - means[b["name"]] >= a.margin),
             "failed_A_minus": (round(means["failed_A"] - means[b["name"]], 4) if means[b["name"]] is not None and means["failed_A"] is not None else None)} for b in battery]
    X.receipt["effects"] = {"means": {k: (round(v, 4) if v is not None else None) for k, v in means.items()}, "footholds": foot, "n": n_arm,
                            "direct_best_mean": {k: (round(v, 4) if v is not None else None) for k, v in direct.items()},
                            "failed_A_minus_random": (round(means["failed_A"] - means["random"], 4) if means["failed_A"] is not None else None), "battery": batt,
                            "probes": {p: {"mean": means[p], "footholds": foot[p], "n": n_arm[p]} for p in PROBES}}
    out = X.close(rows, meas_extra={"battery": batt})
    print(json.dumps({"effects": X.receipt["effects"], "sources": {m: {"solved": [s for s, v in d.items() if v["solved"]]} for m, d in X.receipt["sources"].items()},
                      "failed_A": {k: v for k, v in X.receipt["failed_A_fetch"].items() if k != "artifacts"}, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
