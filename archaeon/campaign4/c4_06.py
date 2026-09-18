"""C4-06 -- LATENT STRUCTURE, RECOMBINATION, VALLEY CROSSING (campaign 4, slot 6).
Preregistration: C4-06/DESIGN.md.

    python -m archaeon.campaign4.c4_06 [--seeds 1..6] [--N 200] [--G 100] [--E 16] [--procs 12] [--dry-run] [--self-test]

Starting population: the depth-16 C4-05 walkers of the viable parents (regenerated from the
walk's seeds; each walker's final digest verified against the committed steps). Challenge:
W2_K2 summit (held-out >= 0.90), which no C4 parent reaches. Two arms at equal budget that
differ ONLY in whether a mate is passed to descend(): mutation_only (mate=None always) and
recombination (the evolver's existing mate policy). Nothing tuned.
"""
from __future__ import annotations

import argparse
import gzip
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
from proteus.foundry.lineage import descend                                  # noqa: E402
from proteus.eval.population_manifest import structural_descriptor           # noqa: E402
from archaeon.wse import reachability as R                                   # noqa: E402
from archaeon.wse.economics import REGIMES                                   # noqa: E402
from archaeon.wse.evolve import Evolution, evaluate                          # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for                      # noqa: E402
from archaeon.campaign2.c2base import FOUNDRY_C2                             # noqa: E402
from archaeon.campaign4.c4base import C4, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign4 import c4_05 as C5                                   # noqa: E402

ID = "C4-06"
TARGET = WorldSpec("W2_K2", K=2, value_bits=4)
ARMS = ("mutation_only", "recombination")
PROBE_EVERY = 10
HELDOUT_EPISODES = 48
WALK_DEPTH = 16


def mutation_only_descend(parent, mutation_seed, mate=None, **kw):
    return descend(parent, mutation_seed, mate=None, **kw)


def regenerate_walkers(parents: List[dict], E: int) -> dict:
    """Depth-16 walkers of every viable (non-degenerate) parent, digests verified against C4-05's steps."""
    steps = json.load(gzip.open(C4 / "C4-05" / "attempts" / "a01" / "steps.json.gz", "rt", encoding="utf-8"))
    last = {}
    for s in steps:
        k = (s["parent_id"], s["walker"])
        if k not in last or s["depth"] > last[k]["depth"]:
            last[k] = s
    out, mism, n = [], 0, 0
    for p in parents:
        env = C1.PARENT_ENV[p["stratum"]]
        eps = C1.episodes(env, E)
        pev = evaluate(p["parent"], eps, rng_seed=0, reward_mode="per_ask")
        if pev["answered_share"] == 0.0:
            continue
        for w in range(1, 5):
            wk = C5.walk(p["parent"], p["organism_id"], w, eps, WALK_DEPTH, 32)
            m = wk["archived"].get(wk["depth"])
            d = hashlib.sha256(json.dumps(m, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            ref = last.get((p["organism_id"], w))
            n += 1
            if ref is None or ref["digest"] != d or ref["depth"] != wk["depth"]:
                mism += 1
                continue
            out.append({"parent_id": p["organism_id"], "stratum": p["stratum"], "walker": w, "depth": wk["depth"], "manifest": m, "digest": d})
    return {"walkers": out, "regenerated": n, "digest_mismatches": mism}


def cat_vec(m: dict) -> tuple:
    d = structural_descriptor(m)
    c = d["opcode_category_counts_static"]
    return (tuple(sorted(c.items())), d["genome_instructions"])


def run_arm(job: dict) -> dict:
    arm, seed, N, Gn, E = job["arm"], job["seed"], job["N"], job["G"], job["E"]
    walkers = job["walkers"]
    init = []
    for i, w in enumerate(walkers):
        org = G.organism_record(dict(w["manifest"]), None, 0)
        org["origins"] = ["walker"]
        init.append(org)
    prov = {"fill": "c4-05 depth-16 walkers, repeated to N by the evolver's init_pop rule", "n": len(init), "N": N, "verified_common": True}
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c4-06-" + arm, foundry=FOUNDRY_C2, init_pop=init, gen0_provenance=prov,
                   descend_fn=(mutation_only_descend if arm == "mutation_only" else None))
    ho_eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, HELDOUT_EPISODES)
    start_vecs = {cat_vec(w["manifest"]) for w in walkers}
    seen_vecs = set(start_vecs)
    births = {"mutation": Counter(), "mated_splice": Counter(), "mated_no_splice": Counter()}
    novelty_by_gen, probes, elite_vectors = [], [], set()
    first_crossing, crossing_manifest = None, None
    t0 = time.time()
    for g in range(Gn):
        row = ev.evaluate_generation(last=(g == Gn - 1))
        # birth accounting for this generation's population (children born last reproduce())
        if g > 0:
            new_v = 0
            for fit, org, evd in ev.scored:
                rec = ev.records.get(org["organism_id"])
                if rec is None:
                    continue
                if len(rec["parent_ids"]) == 2:
                    kind = "mated_splice" if any(o["operator"] == "splice" and (o.get("args") or {}).get("mate_used") for o in rec["operators"]) else "mated_no_splice"
                else:
                    kind = "mutation"
                births[kind]["n"] += 1
                births[kind]["viable"] += int(evd["reward_per_ask"] >= C1.FLOOR)
                births[kind]["reward_sum"] += evd["reward_per_ask"]
                v = cat_vec(org["manifest"])
                if v not in seen_vecs:
                    seen_vecs.add(v); new_v += 1
            novelty_by_gen.append(new_v)
        if g % PROBE_EVERY == 0 or g == Gn - 1:
            elite = ev.scored[0][1]
            ho = evaluate(elite["manifest"], ho_eps, rng_seed=7, reward_mode="per_ask")
            vec = tuple(C1.answers(elite["manifest"], ho_eps))
            elite_vectors.add(hashlib.sha256(json.dumps(vec).encode()).hexdigest())
            probes.append({"gen": g, "train_best": row["best_reward"], "heldout": round(ho["reward_per_ask"], 4), "per_ask": ho["per_ask_reward"]})
            if first_crossing is None and ho["reward_per_ask"] >= R.SUMMIT_MIN:
                first_crossing, crossing_manifest = g, elite["manifest"]
        if g < Gn - 1:
            ev.reproduce()
    res = ev.result()
    tb = [t["best_reward"] for t in res["trace"]]
    return {"arm": arm, "seed": seed, "G": Gn, "N": N, "E": E, "wall_s": round(time.time() - t0, 1),
            "crossing": int(first_crossing is not None), "first_crossing_gen": first_crossing, "crossing_manifest": crossing_manifest,
            "shelf_reached": int(any(b >= R.SHELF_MIN for b in tb)), "first_shelf_gen": R.first_at(tb, R.SHELF_MIN),
            "train_best_final": tb[-1], "train_best_max": max(tb), "heldout_final": probes[-1]["heldout"],
            "births": {k: {"n": v["n"], "viable_share": round(v["viable"] / v["n"], 4) if v["n"] else None, "mean_reward": round(v["reward_sum"] / v["n"], 4) if v["n"] else None} for k, v in births.items()},
            "structural_novelty_total": sum(novelty_by_gen), "structural_novelty_by_gen": novelty_by_gen,
            "heldout_behaviour_distinct": len(elite_vectors), "probes": probes, "trace_best": tb,
            "trace_mean": [t["mean_reward"] for t in res["trace"]], "elite_summary": res["elite_summary"], "gen0_provenance": res["gen0_provenance"], "warnings": res["warnings"],
            "_res": res}


def self_test() -> int:
    ps = C1.parents_from_population()[:6]
    rw = regenerate_walkers(ps, 16)
    walkers = rw["walkers"][:8]
    a = run_arm({"arm": "recombination", "seed": 1, "N": 12, "G": 3, "E": 8, "walkers": walkers})
    b = run_arm({"arm": "recombination", "seed": 1, "N": 12, "G": 3, "E": 8, "walkers": walkers})
    same = json.dumps({k: a[k] for k in ("trace_best", "births", "probes")}, sort_keys=True) == json.dumps({k: b[k] for k in ("trace_best", "births", "probes")}, sort_keys=True)
    c = run_arm({"arm": "mutation_only", "seed": 1, "N": 12, "G": 3, "E": 8, "walkers": walkers})
    cheat = 1.0 >= R.SUMMIT_MIN
    rep = {"regenerated": rw["regenerated"], "digest_mismatches": rw["digest_mismatches"], "walkers_used": len(walkers), "deterministic": same,
           "mutation_only_has_no_mated_births": c["births"]["mated_splice"]["n"] == 0 and c["births"]["mated_no_splice"]["n"] == 0,
           "recombination_has_mated_births": (a["births"]["mated_splice"]["n"] + a["births"]["mated_no_splice"]["n"]) > 0, "cheat_crossing_detector": cheat,
           "births_recomb": a["births"], "wall_s": a["wall_s"]}
    print(json.dumps(rep, indent=1, default=str))
    ok = rw["digest_mismatches"] == 0 and same and rep["mutation_only_has_no_mated_births"] and rep["recombination_has_mated_births"] and cheat
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=100)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C4-06")
    if a.self_test:
        return self_test()
    if not a.dry_run and not C1.gate_is_green():
        print("REFUSED: launch gate not green")
        return 3
    from archaeon.campaign4.c4harness import Experiment4                    # noqa: PLC0415

    class Recomb(Experiment4):
        ID = "C4-06"
        TITLE = "latent structure, recombination, valley crossing"
        PARENTS = ["C4-05", "C3-SFE-01"]
        ARM_FIELD = "arm"
        METRICS = ("crossing", "shelf_reached", "heldout_final", "structural_novelty_total", "heldout_behaviour_distinct")

    X = Recomb(dry_run=a.dry_run, procs=a.procs)
    design = (C4 / "C4-06" / "DESIGN.md").read_text(encoding="utf-8")
    parents = C1.parents_from_population()
    rw = regenerate_walkers(parents, a.E)
    walkers = rw["walkers"]
    # negative control: the starting population does not already cross
    ho1 = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", 1, HELDOUT_EPISODES)
    start_best = max(evaluate(w["manifest"], ho1, rng_seed=7, reward_mode="per_ask")["reward_per_ask"] for w in walkers) if walkers else None
    reach = X.reachability_for([(TARGET, a.N, a.G, a.E, "E0")])
    X.seal({
        "question": "Can separately accumulated neutral changes (the depth-16 C4-05 walkers) combine into a capability ordinary one-step search rarely "
                    "reaches (a W2_K2 held-out summit >= 0.90)? Does the existing recombination machinery turn latent structure into useful computation "
                    "or multiply damage?",
        "parent_evidence": "C4-05: 188/188 walkers reach depth 16 inside the band, structural diversity .76, held-out exaptation .043; C3-SFE-01: 0/24 "
                           "confirmed W2_K2 summits; shelf COMMON.",
        "why_this_slot": "The one C4 slot that tests whether accumulated neutral structure is a stepping stone or dead weight; the C3 valley question with new geometry.",
        "assay_capability_requirement": "starting population's best W2_K2 held-out < 0.90 (measured %s); mutation_only reaches the shelf in >= 3 of %d seeds; "
                                        "walker digests equal C4-05's (%d/%d); determinism (self-test); crossing detector reads the field (cheat)"
                                        % (start_best, len(a.seeds), rw["regenerated"] - rw["digest_mismatches"], rw["regenerated"]),
        "positive_control": "mutation_only arm: shelf_reached >= 1 on >= 3 of %d seeds" % len(a.seeds),
        "reachability_estimate": reach,
        "arms": list(ARMS),
        "crn_policy": "identical cell seeds, identical init_pop (the walkers), identical evolver rng stream; the arms differ only in the mate passed to descend()",
        "budget": {"N": a.N, "G": a.G, "E": a.E, "seeds": a.seeds, "walkers": len(walkers), "heldout_episodes": HELDOUT_EPISODES, "probe_every": PROBE_EVERY,
                   "summit_min": R.SUMMIT_MIN, "shelf_min": R.SHELF_MIN, "floor": C1.FLOOR},
        "primary_observable": "crossings per arm (held-out >= 0.90 at a probe) and first_crossing_gen; viable share and mean reward by birth kind "
                              "(mutation / mated_splice / mated_no_splice); structural novelty per generation; distinct held-out elite behaviours; traces",
        "claim_ceiling": "at n=%d per arm: a count of crossings and a birth-kind damage table on one substrate; no mechanism" % len(a.seeds),
        "falsification_condition": "P1 lost: crossings(recombination) - crossings(mutation_only) < 2 => recombination does not cross more at this budget; "
                                   "INCONCLUSIVE if neither arm crosses and the shelf control holds",
        "kill_condition": "starting population already crosses (negative control) or shelf control fails -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["per-arm per-seed traces and probes", "birth-kind table", "structural novelty by generation", "crossing manifests"],
        "machine_changes_exercised": ["descend_fn override (mate=None)", "walker regeneration + digest verification"],
        "replacement_condition": "none",
        "ancestry": "original (queue slot 6)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": len(a.seeds), "positive_control": {"arm": "mutation_only", "metric": "shelf_reached", "min": 1, "min_rows": 3},
                 "target": {"baseline_arm": "*", "reach_metric": "crossing", "reach_min": 1, "reachability_class": reach["W2_K2"]["at_budget"].get("class_summit")},
                 "primary": {"treatment": "recombination", "control": "mutation_only", "metric": "crossing", "min_effect": 2 / max(1, len(a.seeds))}},
    })
    X.decision("D4-010: D* = 16 (every C4-05 walker reached it); the starting population is the %d depth-16 walkers of the non-degenerate parents, repeated to N by "
               "the evolver's init_pop rule; mutation_only = descend(mate=None) always; recombination = the evolver's mate policy unchanged" % len(walkers))
    if start_best is not None and start_best >= R.SUMMIT_MIN:
        X.decision("NEGATIVE CONTROL FAILED: the starting population already crosses (%.3f); slot INSTRUMENT_INVALID" % start_best)
    X.open("cmp4-c4-06")
    wid = X.world("recomb", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    jobs = [{"arm": arm, "seed": s, "N": a.N, "G": a.G, "E": a.E, "walkers": walkers} for arm in ARMS for s in a.seeds]
    rows = X.pool_map(run_arm, jobs, "evolve_s")
    for r in rows:
        X.reach_row(TARGET, r.pop("_res"), N=a.N, G=a.G, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["heldout_final"], kind="treated")
        content = {k: v for k, v in r.items() if k not in ("crossing_manifest", "trace_best", "trace_mean")}
        X.record(wid, r, {"arm": r["arm"], "seed": r["seed"]}, content, "SURVIVED" if r["crossing"] else "FALSIFIED", key_parts=(r["arm"], r["seed"]))
    summary = {arm: {"crossings": sum(r["crossing"] for r in rows if r["arm"] == arm), "shelf": sum(r["shelf_reached"] for r in rows if r["arm"] == arm),
                     "heldout_final": [r["heldout_final"] for r in rows if r["arm"] == arm],
                     "births": {k: {"n": sum(r["births"][k]["n"] for r in rows if r["arm"] == arm),
                                    "viable": sum(round((r["births"][k]["viable_share"] or 0) * r["births"][k]["n"]) for r in rows if r["arm"] == arm)} for k in ("mutation", "mated_splice", "mated_no_splice")},
                     "structural_novelty_total": [r["structural_novelty_total"] for r in rows if r["arm"] == arm],
                     "heldout_behaviour_distinct": [r["heldout_behaviour_distinct"] for r in rows if r["arm"] == arm]} for arm in ARMS}
    for arm in ARMS:
        for k, b in summary[arm]["births"].items():
            b["viable_share"] = round(b["viable"] / b["n"], 4) if b["n"] else None
    rc = summary["recombination"]; mc = summary["mutation_only"]
    ms, mu = rc["births"]["mated_splice"]["viable_share"], rc["births"]["mutation"]["viable_share"]
    summary["predictions"] = {"P1": {"stated": "crossings(recombination) - crossings(mutation_only) >= 2", "recombination": rc["crossings"], "mutation_only": mc["crossings"],
                                     "held": (rc["crossings"] - mc["crossings"]) >= 2},
                              "P2": {"stated": "catastrophic share among mate-splice births exceeds mutation births' by >= 0.10 (recombination arm)",
                                     "mated_splice_nonviable": None if ms is None else round(1 - ms, 4), "mutation_nonviable": None if mu is None else round(1 - mu, 4),
                                     "held": (ms is not None and mu is not None and (1 - ms) - (1 - mu) >= 0.10)}}
    summary["negative_control_start_best_heldout"] = start_best
    summary["walkers"] = {"regenerated": rw["regenerated"], "digest_mismatches": rw["digest_mismatches"], "used": len(walkers)}
    summary["wall_s"] = round(time.time() - t0, 1)
    X.att.write("SUMMARY.json", summary)
    X.att.write("runs.json", rows)
    X.publish(wid, "summary", "cmp4.c406_summary.v1", summary, {"info_kind": "artifact", "label": "C4-06 summary"})
    out = X.close([{k: v for k, v in r.items() if k not in ("crossing_manifest", "trace_best", "trace_mean", "probes", "structural_novelty_by_gen")} for r in rows],
                  addendum={"predictions": json.dumps(summary["predictions"]), "births": json.dumps({a_: summary[a_]["births"] for a_ in ARMS})})
    print(json.dumps({"summary": {k: v for k, v in summary.items() if k not in ARMS}, "arms": {a_: {k: v for k, v in summary[a_].items()} for a_ in ARMS}, "close": out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
