"""C2-SFE-03 -- FALSIFY SFE-01's COMPONENT EFFECT (parent SFE-01).

    python -m archaeon.campaign2.c2_sfe03 [--seeds 1..12] [--N 200 --G 60 --E 16] [--G-source 100] [--dry-run]

SFE-01 (campaign 1): generation 0 of a W2_K2 search seeded with COMPONENT segments (aligned
2-4-instruction pieces of the above-floor organisms of a W1_d1 source search) reached
footholds 2/3 vs random-segment control 0/3 (n=3; the source never solved its own cell).
Here the claim is rerun at n=12 with a falsification battery whose job is to kill it if a
cheaper explanation suffices. Every arm applies the SAME insertion (one segment spliced into
every generation-0 organism at a seeded aligned position, common across arms) to the SAME
generation 0 (common_fill); only the material differs:

  baseline            nothing inserted
  components          SFE-01's recipe: segments of the top-8 above-floor organisms of the
                      W1_d1 source run with the target's seed (immature source)
  random_segments     segments cut from random genomes, same length distribution  [primary control]
  shuffled            the same components with instruction order permuted      [kill: composition suffices?]
  opcode_matched      the same components' opcode words, operands random         [kill: opcodes suffice?]
  self_segments       segments cut from the target's own generation-0 organisms [kill: any nonrandom
                                                                                  same-distribution material?]
  position_front      components inserted at position 0                          [probe: insertion position]
  other_lineage       components from the source run of ANOTHER seed             [probe: lineage identity]
  mature_source       components from W0 sources that SOLVED their cell           [probe: maturity]

A kill attack SURVIVES iff components beat the attack arm by the preregistered margin
(0.10 mean held-out); the machine promotes to SUPPORTED only if every kill attack survives.
Probes are reported, never scored. Material sets are published (components with the source
population's maturity block; kind cmp2.pop.* REQUIRES it) and fetched back by the target
world; the target runs on the fetched bytes.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List

from proteus.foundry import generate as G
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.wse import telemetry as T
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, common_fill, evaluate, gen0, run_cell
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2, Experiment
from archaeon.campaign2.runner import CAMPAIGN_SEED

TARGET = WorldSpec("W2_K2", K=2, value_bits=4)
SOURCE_IMMATURE = WorldSpec("W1_d1", delay=1, value_bits=4)
SOURCE_MATURE = WorldSpec("W0", value_bits=4)
ARMS = ["baseline", "components", "random_segments", "shuffled", "opcode_matched", "self_segments", "position_front", "other_lineage", "mature_source"]
KILL = ["random_segments", "shuffled", "opcode_matched", "self_segments"]
PROBES = ["position_front", "other_lineage", "mature_source"]
CHANCE = 1.0 / 16
MASK62 = (1 << 62) - 1
MASK32 = 0xFFFFFFFF


# ------------------------------------------------------------------ material
def segments_of(genomes: List[List[int]], max_per_genome: int = 999) -> List[dict]:
    out = []
    for gi, g in enumerate(genomes):
        n = len(g) // 4
        c = 0
        for k in (2, 3, 4):
            for i in range(0, max(1, n - k + 1)):
                seg = g[4 * i:4 * (i + k)]
                if len(seg) == 4 * k:
                    out.append({"words": seg, "k": k, "from": gi, "offset": i}); c += 1
                    if c >= max_per_genome:
                        break
    return out


def harvest(res: dict) -> List[dict]:
    """SFE-01's recipe: aligned 2-4-instruction segments of the top-8 ABOVE-FLOOR final organisms."""
    pop = [z for z in res["final_population"] if z["reward"] > 0.0][:8]
    segs = segments_of([z["manifest"]["genome"] for z in pop])
    for s in segs:
        s["source_reward"] = pop[s["from"]]["reward"]
    return segs


def shuffle_segments(segs: List[dict], seed: int) -> List[dict]:
    rng = SplitMix64(seed_from("c2.sfe03.shuffle", CAMPAIGN_SEED, seed))
    out = []
    for s in segs:
        ins = [s["words"][i:i + 4] for i in range(0, len(s["words"]), 4)]
        for i in range(len(ins) - 1, 0, -1):
            j = rng.randbelow(i + 1); ins[i], ins[j] = ins[j], ins[i]
        out.append(dict(s, words=[w for ii in ins for w in ii]))
    return out


def opcode_matched(segs: List[dict], seed: int) -> List[dict]:
    rng = SplitMix64(seed_from("c2.sfe03.opmatch", CAMPAIGN_SEED, seed))
    out = []
    for s in segs:
        w = list(s["words"])
        for i in range(len(w)):
            if i % 4 != 0:
                w[i] = rng.next_u32() & MASK32
        out.append(dict(s, words=w))
    return out


def random_segments(n_genomes: int, seed: int) -> List[dict]:
    fm = dict(FOUNDRY_C2); fm["seed"] = seed_from("c2.sfe03.random", CAMPAIGN_SEED, seed) & MASK62; fm["n"] = n_genomes
    return segments_of([o["manifest"]["genome"] for o in G.generate(fm)])


def material_summary(segs: List[dict]) -> dict:
    from proteus.foundry.affordances import CATEGORY, N_OPCODES
    ks = [s["k"] for s in segs]
    cats: Dict[str, int] = {}
    for s in segs:
        for w in s["words"][0::4]:
            c = CATEGORY[w % N_OPCODES]; cats[c] = cats.get(c, 0) + 1
    tot = max(1, sum(cats.values()))
    return {"n": len(segs), "k_mean": round(sum(ks) / max(1, len(ks)), 3), "k_hist": {k: ks.count(k) for k in (2, 3, 4)},
            "category_shares": {k: round(v / tot, 4) for k, v in sorted(cats.items())}}


# ------------------------------------------------------------------ jobs
def run_source(job: dict) -> dict:
    """Immature: SFE-01's W1_d1 run (G_source). Mature: W0 run by the step API until 3 generations past its first solver (cap G_source)."""
    spec, seed, N, G_, E, mode = job["spec"], job["seed"], job["N"], job["G"], job["E"], job["mode"]
    ev = Evolution(spec, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c2-sfe03-src-" + mode, foundry=FOUNDRY_C2)
    stop_at = None
    for g in range(G_):
        last = g == G_ - 1 or (stop_at is not None and g >= stop_at)
        ev.evaluate_generation(last=last)
        if mode == "mature" and ev.first_solved_gen is not None and stop_at is None:
            stop_at = g + 3
        if last:
            break
        ev.reproduce()
    res = ev.result()
    segs = harvest(res)
    mat = T.maturity(spec.name, res["elite_eval"]["reward"], [z["reward"] for z in res["final_population"]], chance=CHANCE,
                     budget={"N": N, "G": res["generations"], "E": E}, generation=res["generations"] - 1,
                     lineage={"elite_lineage_id": res["elite"]["lineage_id"], "ancestry_depth": len(res["ancestry"])})
    return {"mode": mode, "seed": seed, "segments": segs, "maturity": mat, "first_solved_gen": res["first_solved_gen"],
            "generations": res["generations"], "trace_best": [t["best_reward"] for t in res["trace"]], "summary": material_summary(segs),
            "_res": res}


def splice_all(pop: List[dict], segs: List[dict], seed: int, front: bool) -> List[dict]:
    """One segment into every organism at a seeded aligned position; the position/choice stream
    is keyed on the seed only, so every arm splices at the same places (common random numbers)."""
    rng = SplitMix64(seed_from("c2.sfe03.splice", CAMPAIGN_SEED, seed))
    out = []
    for org in pop:
        m = dict(org["manifest"]); g = list(m["genome"])
        seg = segs[rng.randbelow(len(segs))]["words"]
        n = len(g) // 4
        pos = 0 if front else rng.randint(0, n) * 4
        g = g[:pos] + list(seg) + g[pos:]
        cap = m["tape_words"]
        while len(g) > min(cap, 4096) or len(g) > 4 * 64:
            g = g[:-4]
        m["genome"] = g
        out.append(m)
    return out


def run_arm(job: dict) -> dict:
    arm, seed, N, G_, E = job["arm"], job["seed"], job["N"], job["G"], job["E"]
    base = gen0(CAMPAIGN_SEED, seed, N, FOUNDRY_C2)
    t0 = time.time()
    if arm == "baseline":
        init, prov = None, None
    else:
        segs = job["segments"]
        mans = splice_all(base, segs, seed, front=(arm == "position_front"))
        init, prov = common_fill(CAMPAIGN_SEED, seed, N, mans, tag=arm, foundry=FOUNDRY_C2)
    res = run_cell(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, G_=G_, E=E, init_pop=init, gen0_provenance=prov,
                   branch="c2-sfe03-" + arm, foundry=FOUNDRY_C2)
    ho = evaluate(res["elite"]["manifest"], episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48), rng_seed=7)
    return {"arm": arm, "seed": seed, "competence_heldout": ho["reward"], "train_last": res["elite_eval"]["reward"],
            "first_solved_gen": res["first_solved_gen"], "reached": 1 if res["first_solved_gen"] is not None else 0,
            "n_material": len(job.get("segments") or []), "persist": ho["persist"], "elite_summary": res["elite_summary"],
            "elite_origins": res["elite_origins"], "gen0_instr_mean": round(sum(len(o["manifest"]["genome"]) for o in (init or base)) / (4 * N), 2),
            "trace_best": [t["best_reward"] for t in res["trace"]], "gen0_provenance": res["gen0_provenance"], "warnings": res["warnings"],
            "wall_s": round(time.time() - t0, 1), "_res": res}


class Falsify01(Experiment):
    ID = "C2-SFE-03"
    TITLE = "falsify SFE-01's component effect (n=12, battery)"
    PARENTS = ["SFE-01"]
    METRICS = ("competence_heldout", "train_last")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=list(range(1, 13)))
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--G-source", type=int, default=100)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--margin", type=float, default=0.10)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = Falsify01(dry_run=a.dry_run, procs=a.procs)
    reach = X.reachability_for([(TARGET, a.N, a.G, a.E, "E0"), (SOURCE_IMMATURE, a.N, a.G_source, a.E, "E0"), (SOURCE_MATURE, a.N, a.G_source, a.E, "E0")])
    battery = [{"name": k, "type": "kill", "rule": "components - %s >= %.2f mean held-out" % (k, a.margin)} for k in KILL if k != "random_segments"]
    X.seal({
        "question": "Does seeding a W2_K2 4-bit search's generation 0 with component segments of an above-floor W1_d1 source population raise "
                    "held-out competence over random segments (SFE-01, 2/3 vs 0/3 at n=3), and does the effect survive cheaper explanations "
                    "(composition without order; opcodes without operands; any nonrandom same-distribution material)?",
        "parent_evidence": "SFE-01 attempt 2: components 2/3 footholds vs random-segment 0/3, neither 1/3, failure-tabu null; source elites 0.06-0.125 "
                           "(immature, L-010). Table: W2_K2 4-bit N200 G60 E16 7/17 REACHABLE.",
        "assay_capability_requirement": "baseline reaches >= 1 foothold in %d seeds (else TARGET_UNREACHABLE); every seeded arm's material set non-empty" % len(a.seeds),
        "positive_control": "baseline (own generation 0): expected 0.41 per seed; P(0 of %d) = %.4f" % (len(a.seeds), (1 - 7 / 17) ** len(a.seeds)),
        "reachability_estimate": reach,
        "arms": ARMS,
        "crn_policy": "default; identical generation 0 (gen0) for every arm; the splice position/choice stream keyed on the seed only, so arms differ in "
                      "material, not in where it goes (position_front excepted by design)",
        "budget": {"N": a.N, "G": a.G, "E": a.E, "G_source": a.G_source, "seeds": a.seeds, "heldout_episodes": 48, "margin": a.margin},
        "primary_observable": "competence_heldout of the elite (48 held-out episodes) per arm x seed; primary comparison components vs random_segments",
        "claim_ceiling": "SUPPORTED_POSITIVE only if components - random_segments >= %.2f AND every kill attack (shuffled, opcode_matched, self_segments) "
                         "survives by the same margin at n=%d; otherwise WEAK_POSITIVE or CAPABLE_NEGATIVE" % (a.margin, len(a.seeds)),
        "falsification_condition": "components - random_segments < %.2f => the SFE-01 effect does not replicate (CAPABLE_NEGATIVE); any kill arm within "
                                   "%.2f of components => that cheaper explanation suffices" % (a.margin, a.margin),
        "typed_failure_conditions": ["TARGET_UNREACHABLE (baseline 0/%d)" % len(a.seeds), "UNDERPOWERED", "IMMATURE_ARTIFACT recorded on immature sources "
                                     "(telemetry; the SFE-01 condition IS an immature source, so it does not gate)", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["material summaries (k histogram, opcode category shares) per set", "gen0 instruction-length mean per arm (length control)",
                                       "source maturity per set", "first_solved_gen per row", "elite origins", "reachability rows"],
        "machine_changes_exercised": ["B (battery in decl + meas)", "C (common_fill with N substitutions)", "E (maturity on every population artifact)",
                                      "G (mature sources run by the step API with a stop rule)", "H", "I"],
        "decl": {"target": {"baseline_arm": "baseline", "reach_metric": "reached", "reach_min": 1, "reachability_class": reach["W2_K2"]["at_budget"]["class"]},
                 "n_min": len(a.seeds),
                 "primary": {"treatment": "components", "control": "random_segments", "metric": "competence_heldout", "min_effect": a.margin},
                 "battery": battery, "probes": PROBES,
                 "artifact_policy": "maturity recorded on every material set; IMMATURE does not gate (the parent's condition is an immature source, D2-011)"},
    })
    X.decision("D2-011: IMMATURE_ARTIFACT is telemetry here, not a gate: the SFE-01 effect under test was produced by an immature source; the mature_source probe measures whether maturity changes it")
    X.open("cmp2-sfe03", "C2-SFE-03 component falsification")
    w_imm = X.world("source-immature", "FULLY_SHARED")
    w_mat = X.world("source-mature", "FULLY_SHARED")
    w_tgt = X.world("target", "EXPLICIT_IMPORT_ONLY")
    X.publish_prereg(w_tgt)

    # sources
    jobs = [{"spec": SOURCE_IMMATURE, "seed": s, "N": a.N, "G": a.G_source, "E": a.E, "mode": "immature"} for s in a.seeds] + \
           [{"spec": SOURCE_MATURE, "seed": s, "N": a.N, "G": a.G_source, "E": a.E, "mode": "mature"} for s in a.seeds]
    srcs = X.pool_map(run_source, jobs, "sources_s")
    imm = {r["seed"]: r for r in srcs if r["mode"] == "immature"}
    mat = {r["seed"]: r for r in srcs if r["mode"] == "mature"}
    for r in srcs:
        res = r.pop("_res")
        spec = SOURCE_IMMATURE if r["mode"] == "immature" else SOURCE_MATURE
        X.reach_row(spec, res, N=a.N, G=r["generations"], E=a.E, regime="E0", seed=r["seed"], arm="source-" + r["mode"],
                    kind="baseline" if r["mode"] == "immature" else "treated")           # the stop rule makes the mature run a schedule
    solved = [s for s, r in mat.items() if r["maturity"]["solved"]]
    mature_pool = [seg for s in solved for seg in mat[s]["segments"]]
    X.receipt["sources"] = {"immature": {s: {"elite": r["maturity"]["source_elite_reward"], "solved": r["maturity"]["solved"], "n_segments": len(r["segments"]),
                                             "first_solved_gen": r["first_solved_gen"], "summary": r["summary"]} for s, r in imm.items()},
                            "mature": {s: {"elite": r["maturity"]["source_elite_reward"], "solved": r["maturity"]["solved"], "n_segments": len(r["segments"]),
                                           "first_solved_gen": r["first_solved_gen"], "generations": r["generations"], "summary": r["summary"]} for s, r in mat.items()},
                            "mature_pool": {"solved_seeds": solved, "n_segments": len(mature_pool), "summary": material_summary(mature_pool) if mature_pool else None}}
    X.att.save()

    # publish + import + fetch: every material set the target uses comes back from the engine
    t0 = time.time()
    fetched: Dict[str, List[dict]] = {}
    for s in a.seeds:
        art = X.publish(w_imm, "components_s%d" % s, "cmp2.pop.components.v1", {"seed": s, "segments": imm[s]["segments"]},
                        {"info_kind": "success", "seed": s, "source": "W1_d1"}, maturity=imm[s]["maturity"])
        obj = X.import_fetch("components_s%d" % s, w_tgt, w_imm, art)
        fetched["components_s%d" % s] = obj["segments"] if obj else imm[s]["segments"]
        rs = random_segments(8, s)
        art = X.publish(w_imm, "random_s%d" % s, "cmp2.material.random_segments.v1", {"seed": s, "segments": rs}, {"info_kind": "artifact", "seed": s})
        obj = X.import_fetch("random_s%d" % s, w_tgt, w_imm, art)
        fetched["random_s%d" % s] = obj["segments"] if obj else rs
    if mature_pool:
        pool_mat = T.maturity("W0", max(mat[s]["maturity"]["source_elite_reward"] for s in solved), [mat[s]["maturity"]["source_elite_reward"] for s in solved],
                              chance=CHANCE, budget={"N": a.N, "G": a.G_source, "E": a.E, "pooled_seeds": solved})
        art = X.publish(w_mat, "mature_pool", "cmp2.pop.components.v1", {"solved_seeds": solved, "segments": mature_pool},
                        {"info_kind": "success", "source": "W0"}, maturity=pool_mat)
        obj = X.import_fetch("mature_pool", w_tgt, w_mat, art)
        fetched["mature_pool"] = obj["segments"] if obj else mature_pool
    X.att.timing("exchange_s", t0)

    # target arms
    jobs = []
    for s in a.seeds:
        comps = fetched["components_s%d" % s]
        other = fetched["components_s%d" % (a.seeds[(a.seeds.index(s) + 1) % len(a.seeds)])]
        selfsegs = segments_of([o["manifest"]["genome"] for o in gen0(CAMPAIGN_SEED, s, a.N, FOUNDRY_C2)[:8]])
        material = {"baseline": None, "components": comps, "random_segments": fetched["random_s%d" % s], "shuffled": shuffle_segments(comps, s),
                    "opcode_matched": opcode_matched(comps, s), "self_segments": selfsegs, "position_front": comps, "other_lineage": other,
                    "mature_source": fetched.get("mature_pool")}
        for arm in ARMS:
            if arm != "baseline" and not material[arm]:
                continue
            jobs.append({"arm": arm, "seed": s, "N": a.N, "G": a.G, "E": a.E, "segments": material[arm]})
    X.receipt["material_summaries"] = {arm: material_summary(m) for arm, m in
                                       {"components": fetched["components_s%d" % a.seeds[0]], "random_segments": fetched["random_s%d" % a.seeds[0]],
                                        "shuffled": shuffle_segments(fetched["components_s%d" % a.seeds[0]], a.seeds[0]),
                                        "opcode_matched": opcode_matched(fetched["components_s%d" % a.seeds[0]], a.seeds[0]),
                                        "self_segments": segments_of([o["manifest"]["genome"] for o in gen0(CAMPAIGN_SEED, a.seeds[0], a.N, FOUNDRY_C2)[:8]]),
                                        "mature_source": fetched.get("mature_pool") or []}.items()}
    rows = X.pool_map(run_arm, jobs, "targets_s")
    for r in rows:
        res = r.pop("_res")
        X.reach_row(TARGET, res, N=a.N, G=a.G, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["competence_heldout"])
    t0 = time.time()
    for r in rows:
        X.record(w_tgt, r, {"experiment": X.ID, "arm": r["arm"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E, "target": TARGET.knobs(),
                            "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("trace_best", "elite_summary", "gen0_provenance")},
                 "SURVIVED" if r["competence_heldout"] >= 0.5 else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    means = {arm: (sum(r["competence_heldout"] for r in rows if r["arm"] == arm) / max(1, sum(1 for r in rows if r["arm"] == arm))) for arm in ARMS}
    foot = {arm: sum(r["reached"] for r in rows if r["arm"] == arm) for arm in ARMS}
    n_arm = {arm: sum(1 for r in rows if r["arm"] == arm) for arm in ARMS}
    batt = [{"name": b["name"], "type": "kill", "passed": (n_arm[b["name"]] > 0 and (means["components"] - means[b["name"]] >= a.margin)),
             "components_minus": round(means["components"] - means[b["name"]], 4) if n_arm[b["name"]] else None} for b in battery]
    probes = {p: {"mean": round(means[p], 4), "components_minus": round(means["components"] - means[p], 4), "footholds": foot[p], "n": n_arm[p]} for p in PROBES}
    X.receipt["effects"] = {"means": {k: round(v, 4) for k, v in means.items()}, "footholds": foot, "n": n_arm,
                            "components_minus_random": round(means["components"] - means["random_segments"], 4), "battery": batt, "probes": probes}
    out = X.close(rows, meas_extra={"battery": batt, "artifacts": {}})
    print(json.dumps({"effects": X.receipt["effects"], "sources": {"immature_solved": sum(1 for r in imm.values() if r["maturity"]["solved"]),
                                                                    "mature_solved": solved}, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
