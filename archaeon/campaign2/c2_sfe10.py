"""C2-SFE-10 -- FUNCTION-BEARING ORGANS (parents SFE-08, SFE-07, SFE-01).

    python -m archaeon.campaign2.c2_sfe10 [--seeds 1..10] [--N 200 --G 60 --E 16] [--dry-run]

SFE-08 (campaign 1) defined an organ as a random 2-4-instruction WINDOW of a failed genotype
and found chimeras of such organs at the floor with their shuffled and random controls.
Here an organ is defined by FUNCTION: for each failed W1_d1 genotype (SFE-01's floor
organisms, fetched from campaign 1; manifests rebuilt by ONE fixed recipe so the recipe is
not a per-seed treatment, C2-SFE-04's confound), every instruction is knocked out (replaced
by NOP) and the organism's OUTPUT SEQUENCE on fixed probe episodes of its own cell is
compared with the intact organism's: an instruction is LOAD-BEARING if the knockout changes
any output. A functional organ is a maximal run of load-bearing instructions (2-8 long).
Sets on the target W2_K2 4-bit (each set = 100 organisms substituted into the cell's own
generation 0 of 200 through common_fill; ten seeds):

  random                the cell's own generation 0                                    [control]
  chimera_functional    functional organ from lineage X + functional organ from lineage Y (X != Y)
  chimera_length        SFE-08's definition: random 2-4-instruction windows, cross-lineage [primary control]
  shuffled_functional   chimera_functional with instruction order permuted within each organ [kill]
  whole_ancestors       whole failed genotypes (fixed recipe)                            [probe]

Load maps (share of load-bearing instructions per genome, organ counts and lengths) are the
telemetry. Direct reuse (best member on 48 held-out episodes) is recorded per set.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List

from proteus.foundry import generate as G
from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import SCHEMA, Player, validate_manifest

from archaeon.wse import telemetry as T
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import common_fill, evaluate, run_cell
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2, REPO, Experiment
from archaeon.campaign2.runner import CAMPAIGN_SEED

TARGET = WorldSpec("W2_K2", K=2, value_bits=4)
SOURCE = WorldSpec("W1_d1", delay=1, value_bits=4)
ARMS = ["random", "chimera_functional", "chimera_length", "shuffled_functional", "whole_ancestors"]
KILL = ["shuffled_functional"]
PROBES = ["whole_ancestors", "random"]
SET_N = 100
CHANCE = 1.0 / 16
MASK62 = (1 << 62) - 1
RECIPE_SEED = 0


def manifest_fixed(genome: List[int]) -> dict:
    """One fixed recipe for every genome (seeded on the genome only): the manifest is a function
    of the genome, never of the target seed."""
    rng = SplitMix64(seed_from("c2.sfe10.recipe", RECIPE_SEED, tuple(genome)))
    tape_choices = [t for t in (16, 32, 64, 128, 256) if t >= len(genome)] or [256]
    m = {"schema_version": SCHEMA, "n_regs": rng.randint(2, 16), "tape_words": tape_choices[rng.randbelow(len(tape_choices))], "genome": list(genome),
         "code_writable": bool(rng.randbelow(2)), "persist": ["none", "regs", "tape", "all"][rng.randbelow(4)], "tick_budget": [16, 64, 256][rng.randbelow(3)],
         "out_cap": [1, 4][rng.randbelow(2)]}
    validate_manifest(m)
    return m


def outputs(manifest: dict, episodes) -> List:
    """The organism's output word per tick (None when it emits nothing): its behaviour signature."""
    player = Player(manifest)
    sig = []
    for ei, ep in enumerate(episodes):
        st = player.fresh_state()
        rng = SplitMix64(seed_from("wse.vmrng", 3, ei))
        for words in ep.ticks:
            player.begin_tick(st)
            outs, _ = player.run_tick(st, [words], 1, rng)
            sig.append(outs[0][0] if outs and outs[0] else None)
    return sig


def load_map(genome: List[int], episodes) -> List[float]:
    m = manifest_fixed(genome)
    base = outputs(m, episodes)
    n = len(genome) // 4
    loads = []
    for i in range(n):
        g = list(genome); g[4 * i:4 * i + 4] = [0, 0, 0, 0]
        try:
            sig = outputs(dict(m, genome=g), episodes)
            loads.append(sum(1 for a, b in zip(sig, base) if a != b) / max(1, len(base)))
        except Exception:                                            # noqa: BLE001
            loads.append(0.0)
    return loads


def functional_organs(genome: List[int], loads: List[float], lo: int = 2, hi: int = 8) -> List[dict]:
    out = []; i = 0; n = len(loads)
    while i < n:
        if loads[i] > 0:
            j = i
            while j + 1 < n and loads[j + 1] > 0:
                j += 1
            run = list(range(i, j + 1))
            for s in range(0, len(run), hi):
                seg = run[s:s + hi]
                if len(seg) >= lo:
                    out.append({"words": genome[4 * seg[0]:4 * (seg[-1] + 1)], "offset": seg[0], "k": len(seg), "load_mean": round(sum(loads[x] for x in seg) / len(seg), 4)})
            i = j + 1
        else:
            i += 1
    return out


def length_organ(genome: List[int], rng: SplitMix64) -> dict:
    n = len(genome) // 4
    k = min(n, 2 + rng.randbelow(3)); off = rng.randbelow(max(1, n - k + 1))
    return {"words": genome[4 * off:4 * (off + k)], "offset": off, "k": k}


def shuffle_words(words: List[int], rng: SplitMix64) -> List[int]:
    ins = [words[i:i + 4] for i in range(0, len(words), 4)]
    for i in range(len(ins) - 1, 0, -1):
        j = rng.randbelow(i + 1); ins[i], ins[j] = ins[j], ins[i]
    return [w for ii in ins for w in ii]


def compose(lineages: Dict[str, List[dict]], mode: str, n: int, seed: int) -> List[dict]:
    """mode: functional | length | shuffled (functional organs with order permuted). Organs of
    two DIFFERENT lineages per chimera, with provenance."""
    names = sorted(lineages)
    rng = SplitMix64(seed_from("c2.sfe10.compose", CAMPAIGN_SEED, seed, mode))
    out = []
    for i in range(n):
        x = names[rng.randbelow(len(names))]
        y = names[(names.index(x) + 1 + rng.randbelow(len(names) - 1)) % len(names)]
        parts = []
        for ln in (x, y):
            if mode == "length":
                gi = rng.randbelow(len(lineages[ln])); o = length_organ(lineages[ln][gi]["genome"], rng); o["member"] = gi
            else:
                pool = [(gi, org) for gi, m in enumerate(lineages[ln]) for org in m["organs"]]
                if not pool:
                    gi = rng.randbelow(len(lineages[ln])); o = length_organ(lineages[ln][gi]["genome"], rng); o["member"] = gi; o["fallback"] = True
                else:
                    gi, o = pool[rng.randbelow(len(pool))]; o = dict(o, member=gi)
                if mode == "shuffled":
                    o = dict(o, words=shuffle_words(o["words"], rng))
            parts.append((ln, o))
        genome = list(parts[0][1]["words"]) + list(parts[1][1]["words"])
        out.append({"genome": genome, "provenance": {"mode": mode, "x": {"lineage": parts[0][0], **{k: v for k, v in parts[0][1].items() if k != "words"}},
                                                     "y": {"lineage": parts[1][0], **{k: v for k, v in parts[1][1].items() if k != "words"}}}})
    return out


def run_arm(job: dict) -> dict:
    arm, seed, N, G_, E = job["arm"], job["seed"], job["N"], job["G"], job["E"]
    t0 = time.time()
    eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48)
    direct_best = None
    if arm == "random":
        init, prov = None, None
    else:
        mans = [manifest_fixed(g) for g in job["genomes"][:SET_N]]
        direct_best = 0.0
        for m in mans:
            try:
                direct_best = max(direct_best, evaluate(m, eps, rng_seed=7)["reward"])
            except Exception:                                        # noqa: BLE001
                pass
        init, prov = common_fill(CAMPAIGN_SEED, seed, N, mans, tag=arm, foundry=FOUNDRY_C2)
    res = run_cell(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, G_=G_, E=E, init_pop=init, gen0_provenance=prov, branch="c2-sfe10-" + arm, foundry=FOUNDRY_C2)
    ho = evaluate(res["elite"]["manifest"], eps, rng_seed=7)
    return {"arm": arm, "seed": seed, "competence_heldout": ho["reward"], "train_last": res["elite_eval"]["reward"], "first_solved_gen": res["first_solved_gen"],
            "reached": 1 if res["first_solved_gen"] is not None else 0, "direct_best": direct_best, "n_members": len(job.get("genomes") or []),
            "functional_organs_used": job.get("n_functional"),
            "import_share_final": res["trace"][-1]["origin_shares"].get(arm, 0.0) if arm != "random" else None, "elite_origins": res["elite_origins"],
            "persist": ho["persist"], "elite_summary": res["elite_summary"], "trace_best": [t["best_reward"] for t in res["trace"]],
            "gen0_provenance": res["gen0_provenance"], "warnings": res["warnings"], "wall_s": round(time.time() - t0, 1), "_res": res}


class Organs(Experiment):
    ID = "C2-SFE-10"
    TITLE = "function-bearing organs"
    PARENTS = ["SFE-08", "SFE-07", "SFE-01"]
    METRICS = ("competence_heldout", "train_last", "direct_best", "import_share_final")


def fetch_failed(X: Organs) -> tuple:
    r1 = json.loads((REPO / "archaeon" / "campaign1" / "SFE-01" / "RECEIPT.json").read_text(encoding="utf-8"))
    if X.dry_run:
        out = {}
        for s in ("1", "2", "3"):
            out[s] = [o["manifest"]["genome"] for o in G.generate(dict(FOUNDRY_C2, seed=5050 + int(s), n=20))]
        return out, {"dry_run": True}
    rd = X.eng.read_campaign1()
    lineages, prov = {}, {"world": r1["worlds"]["source"], "artifacts": {}, "dry_run": False}
    for s, ids in sorted(r1["artifacts"].items()):
        obj, info = X.att.step("fetch_failed", lambda s=s, ids=ids: X.eng.fetch(r1["worlds"]["source"], ids["failures"], expected=ids.get("failures_hash"), client=rd),
                               parts=(s,), kind="engine")
        prov["artifacts"][s] = dict(info, n=len(obj.get("failures", [])))
        lineages[s] = obj.get("failures", [])
    return lineages, prov


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=list(range(1, 11)))
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--margin", type=float, default=0.10)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = Organs(dry_run=a.dry_run, procs=a.procs)
    reach = X.reachability_for([(TARGET, a.N, a.G, a.E, "E0")])
    battery = [{"name": k, "type": "kill", "rule": "chimera_functional - %s >= %.2f mean held-out" % (k, a.margin)} for k in KILL]
    X.seal({
        "question": "Do organs defined by KNOCKOUT LOAD (instructions whose removal changes the organism's outputs on its own cell) transfer where SFE-08's "
                    "length-defined organs did not: does a chimera of two functional organs from different failed lineages raise held-out competence on "
                    "W2_K2 4-bit over a chimera of two length-defined organs?",
        "parent_evidence": "SFE-08: chimera = shuffled = random at floor; whole ancestors 1/3 each. C2-SFE-04: failed genotypes carry nothing that survives shuffling; "
                           "the campaign-1 manifest rebuild was a per-seed treatment (fixed here). Table: W2_K2 4-bit N200 G60 E16 7/17 REACHABLE.",
        "assay_capability_requirement": "ANY arm reaches a foothold in >= 1 of %d seeds; >= 1 functional organ found per lineage (else the functional arm falls back "
                                        "to length organs and the row says so)" % len(a.seeds),
        "positive_control": "the random arm (own generation 0) on W2_K2 4-bit: expected 0.41 per seed; the whole_ancestors probe as the parent's reference",
        "reachability_estimate": reach,
        "arms": ARMS,
        "crn_policy": "default; every set substitutes %d organisms into the SAME generation 0 of %d (common_fill, tagged) so the import share is informative; "
                      "composition streams keyed on (seed, mode)" % (SET_N, a.N),
        "budget": {"N": a.N, "G": a.G, "E": a.E, "set_n": SET_N, "seeds": a.seeds, "heldout_episodes": 48, "margin": a.margin, "probe_episodes": 8, "recipe_seed": RECIPE_SEED},
        "primary_observable": "competence_heldout per arm x seed; chimera_functional vs chimera_length; direct_best and import_share_final as telemetry",
        "claim_ceiling": "SUPPORTED_POSITIVE only if the primary margin holds AND shuffled_functional falls below chimera_functional by the margin; else WEAK / CAPABLE_NEGATIVE",
        "falsification_condition": "chimera_functional - chimera_length < %.2f => function-defined organs transfer no better than length-defined ones" % a.margin,
        "typed_failure_conditions": ["TARGET_UNREACHABLE (no arm reaches)", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["load maps per genome (share load-bearing, organ count/length)", "direct_best per set", "import_share_final", "set summaries", "reachability rows"],
        "machine_changes_exercised": ["B (battery, target '*')", "C (partial substitution + origin share)", "D (cross-campaign fetch)", "E", "H (load maps)", "I"],
        "decl": {"target": {"baseline_arm": "*", "reach_metric": "reached", "reach_min": 1, "reachability_class": reach["W2_K2"]["at_budget"]["class"]}, "n_min": len(a.seeds),
                 "primary": {"treatment": "chimera_functional", "control": "chimera_length", "metric": "competence_heldout", "min_effect": a.margin},
                 "interventions": [{"arm": "chimera_functional", "counter": "functional_organs_used"}],
                 "battery": battery, "probes": PROBES},
    })
    X.decision("D2-018: an organ is FUNCTIONAL iff its instructions are load-bearing under single-instruction knockout on the SOURCE cell's probe episodes; the target is never consulted")
    X.open("cmp2-sfe10", "C2-SFE-10 functional organs")
    w_src = X.world("lineages", "FULLY_SHARED")
    w_tgt = X.world("target", "EXPLICIT_IMPORT_ONLY")
    X.publish_prereg(w_tgt)

    t0 = time.time()
    lineages_raw, fprov = fetch_failed(X)
    X.att.timing("fetch_s", t0)
    probe_eps = episodes_for(SOURCE, CAMPAIGN_SEED, "train", 777, 8)
    t0 = time.time()
    lineages: Dict[str, List[dict]] = {}
    load_stats = {}
    for ln, genomes in lineages_raw.items():
        members = []
        for g in genomes:
            loads = load_map(g, probe_eps)
            members.append({"genome": g, "loads": loads, "organs": functional_organs(g, loads)})
        lineages[ln] = members
        shares = [sum(1 for x in m["loads"] if x > 0) / max(1, len(m["loads"])) for m in members]
        load_stats[ln] = {"n_genomes": len(members), "load_share_mean": round(sum(shares) / max(1, len(shares)), 4),
                          "n_organs": sum(len(m["organs"]) for m in members), "organ_len_mean": round(sum(o["k"] for m in members for o in m["organs"]) / max(1, sum(len(m["organs"]) for m in members)), 3),
                          "genomes_with_organ": sum(1 for m in members if m["organs"])}
    X.att.timing("load_maps_s", t0)
    X.receipt["failed_fetch"] = fprov
    X.receipt["load_stats"] = load_stats
    X.att.save()
    mat = T.maturity("W1_d1", 0.125, [0.0] * 90 + [0.125] * 10, chance=CHANCE, budget={"campaign": "cmp1/SFE-01", "N": 200, "G": 100, "E": 16},
                     lineage={"reconstructed": True})
    X.publish(w_src, "load_maps", "cmp2.load_maps.v1", {ln: [{"genome": m["genome"], "loads": m["loads"], "organs": m["organs"]} for m in ms] for ln, ms in lineages.items()},
              {"info_kind": "observation"})
    t0 = time.time()
    sets_by_seed: Dict[int, Dict[str, List[List[int]]]] = {}
    whole = [m["genome"] for ms in lineages.values() for m in ms]
    for s in a.seeds:
        cf = compose(lineages, "functional", SET_N, s); cl = compose(lineages, "length", SET_N, s); cs_ = compose(lineages, "shuffled", SET_N, s)
        art = X.publish(w_src, "sets_s%d" % s, "cmp2.pop.organ_sets.v1", {"seed": s, "functional": cf, "length": cl, "shuffled": cs_},
                        {"info_kind": "artifact", "seed": s}, maturity=mat)
        obj = X.import_fetch("sets_s%d" % s, w_tgt, w_src, art)
        got = obj if obj else {"functional": cf, "length": cl, "shuffled": cs_}
        rng = SplitMix64(seed_from("c2.sfe10.whole", CAMPAIGN_SEED, s))
        wh = list(whole);
        for i in range(len(wh) - 1, 0, -1):
            j = rng.randbelow(i + 1); wh[i], wh[j] = wh[j], wh[i]
        sets_by_seed[s] = {"random": None, "chimera_functional": [c["genome"] for c in got["functional"]], "chimera_length": [c["genome"] for c in got["length"]],
                           "shuffled_functional": [c["genome"] for c in got["shuffled"]], "whole_ancestors": wh[:SET_N],
                           "_n_functional": sum(1 for c in got["functional"] if not (c["provenance"]["x"].get("fallback") or c["provenance"]["y"].get("fallback")))}
        if s == a.seeds[0]:
            X.receipt["fallback_share"] = {"functional": sum(1 for c in cf if c["provenance"]["x"].get("fallback") or c["provenance"]["y"].get("fallback")) / SET_N}
    X.att.timing("exchange_s", t0)
    X.receipt["set_summaries"] = {arm: T.population_summary([{"genome": g} for g in sets_by_seed[a.seeds[0]][arm]]) for arm in ARMS if sets_by_seed[a.seeds[0]][arm]}
    X.receipt["n_functional_by_seed"] = {s: sets_by_seed[s]["_n_functional"] for s in a.seeds}
    X.att.save()
    jobs = [{"arm": arm, "seed": s, "N": a.N, "G": a.G, "E": a.E, "genomes": sets_by_seed[s][arm],
             "n_functional": (sets_by_seed[s]["_n_functional"] if arm in ("chimera_functional", "shuffled_functional") else None)} for s in a.seeds for arm in ARMS]
    rows = X.pool_map(run_arm, jobs, "targets_s")
    for r in rows:
        res = r.pop("_res")
        X.reach_row(TARGET, res, N=a.N, G=a.G, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["competence_heldout"])
    t0 = time.time()
    for r in rows:
        X.record(w_tgt, r, {"experiment": X.ID, "arm": r["arm"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E, "target": TARGET.knobs(), "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("trace_best", "elite_summary", "gen0_provenance")},
                 "SURVIVED" if r["competence_heldout"] >= 0.5 else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    n_arm = {arm: sum(1 for r in rows if r["arm"] == arm) for arm in ARMS}
    means = {arm: (sum(r["competence_heldout"] for r in rows if r["arm"] == arm) / n_arm[arm]) if n_arm[arm] else None for arm in ARMS}
    foot = {arm: sum(r["reached"] for r in rows if r["arm"] == arm) for arm in ARMS}
    direct = {arm: (sum((r["direct_best"] or 0) for r in rows if r["arm"] == arm) / n_arm[arm]) if n_arm[arm] and arm != "random" else None for arm in ARMS}
    share = {arm: (sum((r["import_share_final"] or 0) for r in rows if r["arm"] == arm) / n_arm[arm]) if n_arm[arm] and arm != "random" else None for arm in ARMS}
    batt = [{"name": b["name"], "type": "kill", "passed": bool(means["chimera_functional"] - means[b["name"]] >= a.margin),
             "functional_minus": round(means["chimera_functional"] - means[b["name"]], 4)} for b in battery]
    X.receipt["effects"] = {"means": {k: (round(v, 4) if v is not None else None) for k, v in means.items()}, "footholds": foot, "n": n_arm,
                            "direct_best_mean": {k: (round(v, 4) if v is not None else None) for k, v in direct.items()},
                            "import_share_final_mean": {k: (round(v, 4) if v is not None else None) for k, v in share.items()},
                            "functional_minus_length": round(means["chimera_functional"] - means["chimera_length"], 4), "battery": batt}
    out = X.close(rows, meas_extra={"battery": batt})
    print(json.dumps({"effects": X.receipt["effects"], "load_stats": load_stats, "fallback_share": X.receipt.get("fallback_share"), **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
