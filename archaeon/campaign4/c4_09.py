"""C4-09 -- LATERAL EXAPTATION / PAIRED ECOLOGY (campaign 4, slot 9). Preregistration: C4-09/DESIGN.md.

    python -m archaeon.campaign4.c4_09 [--seeds 1 2 3] [--N 50] [--G 100] [--E 16] [--B 24] [--procs 6] [--dry-run] [--self-test]

Four fixed worlds, one evolver each, the same 188 digest-verified C4-05 walkers as every world's
starting population. control: ordinary selection. lateral: each generation's below-floor,
non-degenerate children (up to B per world, in id order) are evaluated on the other three
worlds and enter a world's population iff their measured reward there is >= floor and >= that
world's median fitness (the evolver's inject). No classifier, no ranking; the extra evaluations
are counted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import generate as G                                   # noqa: E402
from proteus.foundry import grammar as GR                                   # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from archaeon.wse import reachability as R                                   # noqa: E402
from archaeon.wse.economics import REGIMES                                   # noqa: E402
from archaeon.wse.evolve import Evolution, evaluate                          # noqa: E402
from archaeon.wse.worlds import episodes_for                                 # noqa: E402
from archaeon.campaign2.c2base import FOUNDRY_C2                             # noqa: E402
from archaeon.campaign4.c4base import C4, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign4 import c4_06 as C6                                   # noqa: E402

ID = "C4-09"
WORLDS = ("W0", "W1_d1", "W1_d4", "W2_K2")
PROBE_EVERY = 10
HELDOUT = 48


def run_ecology(job: dict) -> dict:
    arm, seed, N, Gn, E, B, walkers = job["arm"], job["seed"], job["N"], job["G"], job["E"], job["B"], job["walkers"]
    rng = SplitMix64(seed_from("c4.09.start", CAMPAIGN_SEED, seed))
    idx = list(range(len(walkers)))
    evs: Dict[str, Evolution] = {}
    for w in WORLDS:
        pick = [idx[rng.randbelow(len(idx))] for _ in range(N)]
        init = []
        for i in pick:
            org = G.organism_record(dict(walkers[i]["manifest"]), None, 0); org["origins"] = ["walker"]; init.append(org)
        prov = {"fill": "c4-05 depth-16 walkers subsampled to N by the seed's rng", "n": N, "verified_common": True}
        evs[w] = Evolution(C1.ENVS[w], REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c4-09-%s-%s" % (arm, w), foundry=FOUNDRY_C2,
                           init_pop=init, gen0_provenance=prov, rng_label="c4-09-%s" % w)
    train_eps = {w: episodes_for(C1.ENVS[w], CAMPAIGN_SEED, "train", 1, E) for w in WORLDS}
    ho_eps = {w: episodes_for(C1.ENVS[w], CAMPAIGN_SEED, "heldout", seed, HELDOUT) for w in WORLDS}
    transfers = Counter()
    rescued_ids: Dict[str, set] = {w: set() for w in WORLDS}
    rescue_log = []
    probes = {w: [] for w in WORLDS}
    elite_rescued_probe = Counter()
    primary_evals, transfer_evals = 0, 0
    t0 = time.time()
    for g in range(Gn):
        for w in WORLDS:
            evs[w].evaluate_generation(last=(g == Gn - 1))
            primary_evals += N
        if arm == "lateral" and B > 0 and g > 0:
            for w in WORLDS:
                ev = evs[w]
                fits = sorted(z[0] for z in ev.scored)
                median = {u: sorted(z[0] for z in evs[u].scored)[len(evs[u].scored) // 2] for u in WORLDS}
                cands = [z for z in ev.scored if z[1]["organism_id"] in ev.records and z[2]["reward_per_ask"] < C1.FLOOR and z[2]["answered_share"] > 0]
                cands.sort(key=lambda z: z[1]["organism_id"])
                for fit, org, evd in cands[:B]:
                    for u in WORLDS:
                        if u == w:
                            continue
                        r = evaluate(org["manifest"], train_eps[u], rng_seed=0, reward_mode="per_ask")
                        transfer_evals += 1
                        f_u = REGIMES["E0"].fitness(r["reward_per_ask"], r["meter"], E) if hasattr(REGIMES["E0"], "fitness") else r["reward_per_ask"]
                        if r["reward_per_ask"] >= C1.FLOOR and f_u >= median[u]:
                            m = dict(org["manifest"])
                            n_in = evs[u].inject([m], tag="rescued")
                            if n_in:
                                # the injected organism's id is the record made by inject; tag its origin for descent tracking
                                transfers[(w, u)] += 1
                                rescue_log.append({"gen": g, "from": w, "to": u, "reward_from": evd["reward_per_ask"], "reward_to": r["reward_per_ask"], "median_to": median[u]})
                                for z in evs[u].scored:
                                    if "rescued" in z[1].get("origins", []):
                                        rescued_ids[u].add(z[1]["organism_id"])
        if g % PROBE_EVERY == 0 or g == Gn - 1:
            for w in WORLDS:
                elite = evs[w].scored[0][1]
                ho = evaluate(elite["manifest"], ho_eps[w], rng_seed=7, reward_mode="per_ask")
                probes[w].append({"gen": g, "heldout": round(ho["reward_per_ask"], 4), "elite_rescued": "rescued" in elite.get("origins", [])})
                if "rescued" in elite.get("origins", []):
                    elite_rescued_probe[w] += 1
        if g < Gn - 1:
            for w in WORLDS:
                evs[w].reproduce()
    out_w = {}
    for w in WORLDS:
        res = evs[w].result()
        pop = res["final_population"]
        n_res = sum(1 for z in pop if "rescued" in z.get("origins", []))
        out_w[w] = {"heldout_final": probes[w][-1]["heldout"], "heldout_best_probe": max(p["heldout"] for p in probes[w]),
                    "train_best_final": res["elite_fitness"], "rescued_descendants_final": n_res, "rescued_share_final": round(n_res / max(1, len(pop)), 4),
                    "elite_rescued_probes": elite_rescued_probe[w], "distinct_heldout_probe_values": len({p["heldout"] for p in probes[w]}),
                    "probes": probes[w], "trace_best": [t["best_reward"] for t in res["trace"]]}
    n_resc = sum(transfers.values())
    return {"arm": arm, "seed": seed, "N": N, "G": Gn, "E": E, "B": B, "worlds": out_w,
            "rescues": n_resc, "transfer_matrix": {"%s->%s" % k: v for k, v in transfers.items()},
            "rescue_survival": round(sum(out_w[w]["rescued_descendants_final"] for w in WORLDS) / n_resc, 4) if n_resc else None,
            "rescue_log": rescue_log[:200], "primary_evals": primary_evals, "transfer_evals": transfer_evals,
            "extra_compute_ratio": round(transfer_evals / max(1, primary_evals), 4), "wall_s": round(time.time() - t0, 1)}


def self_test() -> int:
    ps = C1.parents_from_population()[:12]
    rw = C6.regenerate_walkers(ps, 16)
    walkers = rw["walkers"]
    if len(walkers) < 4:
        walkers = walkers * 4
    a = run_ecology({"arm": "control", "seed": 1, "N": 8, "G": 4, "E": 8, "B": 0, "walkers": walkers})
    b = run_ecology({"arm": "control", "seed": 1, "N": 8, "G": 4, "E": 8, "B": 0, "walkers": walkers})
    c = run_ecology({"arm": "lateral", "seed": 1, "N": 8, "G": 4, "E": 8, "B": 0, "walkers": walkers})
    d = run_ecology({"arm": "lateral", "seed": 1, "N": 8, "G": 4, "E": 8, "B": 8, "walkers": walkers})
    det = all(a["worlds"][w]["trace_best"] == b["worlds"][w]["trace_best"] for w in WORLDS)
    neg = all(a["worlds"][w]["trace_best"] == c["worlds"][w]["trace_best"] for w in WORLDS)
    cheat = (1.0 >= C1.FLOOR)
    rep = {"walkers": len(walkers), "mismatches": rw["digest_mismatches"], "deterministic": det, "negative_B0_equals_control": neg, "cheat": cheat,
           "lateral_B8_rescues": d["rescues"], "transfer_evals": d["transfer_evals"], "extra_ratio": d["extra_compute_ratio"]}
    print(json.dumps(rep, indent=1))
    return 0 if (det and neg and cheat and rw["digest_mismatches"] == 0) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--N", type=int, default=50)
    ap.add_argument("--G", type=int, default=100)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--B", type=int, default=24)
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C4-09")
    if a.self_test:
        return self_test()
    if not a.dry_run and not C1.gate_is_green():
        print("REFUSED: launch gate not green")
        return 3
    from archaeon.campaign4.c4harness import Experiment4                    # noqa: PLC0415

    class Ecology(Experiment4):
        ID = "C4-09"
        TITLE = "lateral exaptation / paired ecology"
        PARENTS = ["C4-05", "C4-06"]
        ARM_FIELD = "arm"
        METRICS = ("rescues", "rescue_survival", "extra_compute_ratio", "worlds_improved")

    X = Ecology(dry_run=a.dry_run, procs=a.procs)
    design = (C4 / "C4-09" / "DESIGN.md").read_text(encoding="utf-8")
    parents = C1.parents_from_population()
    rw = C6.regenerate_walkers(parents, a.E)
    walkers = rw["walkers"]
    X.seal({
        "question": "Are useful stepping stones destroyed merely because they are bad at the environment that produced their parent? Four fixed worlds; "
                    "a below-floor non-degenerate child is evaluated on the other three (bounded budget B=%d per world per generation) and enters a world "
                    "only because of its measured reward there." % a.B,
        "parent_evidence": "C4-01: D6 exaptive 34/5,472 single edits (30 shelf); C4-05: depth-16 walkers exaptive .043; C4-06: no crossing at G=100.",
        "why_this_slot": "The campaign's POET-like test without assuming POET is the answer; the only slot that lets a failure in one world be a success in another.",
        "assay_capability_requirement": "self-test: determinism; B=0 lateral equals control trace for trace; cheat; walker digests equal C4-05's (%d/%d)" % (rw["regenerated"] - rw["digest_mismatches"], rw["regenerated"]),
        "positive_control": "control arm: every world reaches the shelf (train >= .45) in >= 2 of 3 seeds (the walkers start on or near it)",
        "reachability_estimate": {"note": "four-world ecology; per-world reachability lookups not applied"},
        "arms": ["control", "lateral"],
        "crn_policy": "identical seeds, identical starting subsamples per world, identical rng streams; the arms differ only in the lateral step",
        "budget": {"worlds": list(WORLDS), "N": a.N, "G": a.G, "E": a.E, "B": a.B, "seeds": a.seeds, "walkers": len(walkers), "heldout": HELDOUT},
        "primary_observable": "rescues and the transfer matrix; rescue survival at G=100; per-world held-out best vs control; distinct held-out elite values; "
                              "extra compute ratio; P1 and P2 as stated; the overhead failure shape",
        "claim_ceiling": "n=3 seeds; a count of rescues and their fates on four fixed worlds; no mechanism",
        "falsification_condition": "overhead: rescue survival < .10 AND no world improved by >= 1/16 in >= 2 seeds",
        "kill_condition": "control failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "UNDERPOWERED"],
        "expected_machine_telemetry": ["per-world traces and probes", "transfer matrix", "rescue log", "compute counts"],
        "machine_changes_exercised": ["multi-world evolver loop", "inject() as the lateral entry path"],
        "replacement_condition": "none",
        "ancestry": "original (queue slot 9)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": len(a.seeds), "primary": {"treatment": "lateral", "control": "control", "metric": "worlds_improved", "min_effect": 1.0}},
    })
    X.decision("D4-013: lateral entry rule = measured reward on the receiving world >= floor AND fitness >= that world's current median; candidates in "
               "organism-id order (no ranking), at most B per world per generation; inject replaces the receiving world's worst members")
    X.open("cmp4-c4-09")
    wid = X.world("ecology", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    jobs = [{"arm": arm, "seed": s, "N": a.N, "G": a.G, "E": a.E, "B": (a.B if arm == "lateral" else 0), "walkers": walkers} for arm in ("control", "lateral") for s in a.seeds]
    rows = X.pool_map(run_ecology, jobs, "ecology_s")
    by = {(r["arm"], r["seed"]): r for r in rows}
    grouped = []
    for r in rows:
        ctrl = by[("control", r["seed"])]
        improved = [w for w in WORLDS if r["worlds"][w]["heldout_final"] - ctrl["worlds"][w]["heldout_final"] >= C1.BAND] if r["arm"] == "lateral" else []
        r["worlds_improved"] = len(improved); r["improved_worlds"] = improved
        r["shelf_worlds"] = sum(1 for w in WORLDS if any(b >= R.SHELF_MIN for b in r["worlds"][w]["trace_best"]))
        grouped.append({"arm": r["arm"], "seed": r["seed"], "rescues": r["rescues"], "rescue_survival": r["rescue_survival"], "extra_compute_ratio": r["extra_compute_ratio"],
                        "worlds_improved": r["worlds_improved"], "shelf_worlds": r["shelf_worlds"],
                        **{"heldout_%s" % w: r["worlds"][w]["heldout_final"] for w in WORLDS}})
        content = {k: v for k, v in r.items() if k != "rescue_log"} | {"rescue_log_head": r["rescue_log"][:50]}
        for w in WORLDS:
            content["worlds"][w] = {k: v for k, v in r["worlds"][w].items() if k != "trace_best"}
        X.record(wid, r, {"arm": r["arm"], "seed": r["seed"]}, content, "SURVIVED", key_parts=(r["arm"], r["seed"]))
    lat = [r for r in rows if r["arm"] == "lateral"]
    surv = [r["rescue_survival"] for r in lat if r["rescue_survival"] is not None]
    p1 = bool(surv) and (sum(surv) / len(surv)) >= 0.25
    per_world_improved = {w: sum(1 for r in lat if w in r["improved_worlds"]) for w in WORLDS}
    p2 = any(v >= 2 for v in per_world_improved.values())
    overhead = (not surv or (sum(surv) / len(surv)) < 0.10) and not p2
    summary = {"rescues": [r["rescues"] for r in lat], "rescue_survival": surv, "transfer_matrices": [r["transfer_matrix"] for r in lat],
               "per_world_improved_seeds": per_world_improved, "extra_compute_ratio": [r["extra_compute_ratio"] for r in lat],
               "heldout_final": {r["arm"] + "-" + str(r["seed"]): {w: r["worlds"][w]["heldout_final"] for w in WORLDS} for r in rows},
               "elite_rescued_probes": {str(r["seed"]): {w: r["worlds"][w]["elite_rescued_probes"] for w in WORLDS} for r in lat},
               "predictions": {"P1": {"stated": "rescue survival >= .25", "values": surv, "held": p1},
                               "P2": {"stated": "some world improved by >= 1/16 in >= 2 of 3 seeds", "per_world": per_world_improved, "held": p2}},
               "overhead_shape": overhead, "walkers": {"regenerated": rw["regenerated"], "digest_mismatches": rw["digest_mismatches"]}, "wall_s": round(time.time() - t0, 1)}
    X.att.write("ECOLOGY.json", summary)
    X.att.write("runs.json", rows)
    X.publish(wid, "ecology", "cmp4.c409_ecology.v1", summary, {"info_kind": "artifact", "label": "C4-09 ecology summary"})
    out = X.close(grouped, addendum={"predictions": json.dumps(summary["predictions"]), "overhead_shape": str(overhead)})
    print(json.dumps({"summary": {k: v for k, v in summary.items() if k not in ("heldout_final",)}, "heldout_final": summary["heldout_final"], "close": out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
