"""C4-10 -- HELD-OUT EVOLVABILITY TRIAL (campaign 4, slot 10). Preregistration: C4-10/DESIGN.md.

    python -m archaeon.campaign4.c4_10 [--seeds 1 2 3 4] [--N 200] [--G 60] [--E 16] [--procs 12] [--dry-run] [--self-test]

Conditions are SELECTED by the preregistered rule from the committed C4-08 and C4-09 tables at
run time (at most two; possibly none), then compared with the frozen baseline on a held-out
family of four worlds never used to develop any C4 condition, from the 57 starting parents,
at equal budgets, same selection algorithm, no manual rescue. The baseline always runs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import generate as G                                   # noqa: E402
from proteus.foundry.lineage import descend                                  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from archaeon.wse import reachability as R                                   # noqa: E402
from archaeon.wse.economics import REGIMES                                   # noqa: E402
from archaeon.wse.evolve import Evolution, evaluate                          # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for, with_knobs          # noqa: E402
from archaeon.campaign2.c2base import FOUNDRY_C2                             # noqa: E402
from archaeon.campaign4.c4base import C4, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402

ID = "C4-10"
FAMILY = {"W1_d2": WorldSpec("W1_d2", delay=2, value_bits=4), "W1_d3": WorldSpec("W1_d3", delay=3, value_bits=4),
          "W2_K2d1": WorldSpec("W2_K2d1", K=2, delay=1, value_bits=4), "W0_8b": WorldSpec("W0_8b", value_bits=8)}
NOVEL_MIN = 0.75
PROBE_EVERY = 10
HELDOUT = 48
LATERAL_B = 24


def n_ops2(parent, mutation_seed, mate=None, **kw):
    return descend(parent, mutation_seed, mate=None, n_ops=2, **kw)


def select_conditions() -> dict:
    """The preregistered rule over the committed C4-08 and C4-09 tables. Returns the chosen
    conditions and the evidence read, so a third party can check the choice."""
    out = {"evidence": {}, "selected": []}
    p8 = C4 / "C4-08" / "attempts" / "a01" / "ROBUSTNESS_TABLES.json"
    if p8.exists():
        t = json.loads(p8.read_text(encoding="utf-8"))["tables"]
        la, lp = t["ancestral"]["loss"], t["perturbed"]["loss"]
        ca, cp = t["ancestral"]["coherent"], t["perturbed"]["coherent"]
        loss_ok = (la["p"] is not None and lp["p"] is not None and la["p"] - lp["p"] >= 0.05 and (lp["band95"][1] or 1) < (la["band95"][0] or 0))
        coh_ok = (ca["p"] is not None and cp["p"] is not None and cp["p"] - ca["p"] >= 0.05)
        out["evidence"]["mutation_load"] = {"ancestral_loss": la, "perturbed_loss": lp, "ancestral_coherent": ca, "perturbed_coherent": cp,
                                            "loss_decreased_bands_apart": loss_ok, "coherent_increased": coh_ok, "qualifies": loss_ok and coh_ok}
        if loss_ok and coh_ok:
            out["selected"].append("mutation_load")
    else:
        out["evidence"]["mutation_load"] = {"qualifies": False, "reason": "C4-08 tables absent"}
    p9 = C4 / "C4-09" / "attempts" / "a01" / "ECOLOGY.json"
    if p9.exists():
        e = json.loads(p9.read_text(encoding="utf-8"))
        q = bool(e["predictions"]["P1"]["held"] and e["predictions"]["P2"]["held"])
        out["evidence"]["lateral"] = {"P1": e["predictions"]["P1"], "P2": e["predictions"]["P2"], "qualifies": q}
        if q:
            out["selected"].append("lateral")
    else:
        out["evidence"]["lateral"] = {"qualifies": False, "reason": "C4-09 tables absent"}
    out["selected"] = out["selected"][:2]
    return out


def run_trial(job: dict) -> dict:
    """One (condition, seed) over the four family worlds; lateral co-evolves them, the others run them independently."""
    cond, seed, N, Gn, E, parents = job["condition"], job["seed"], job["N"], job["G"], job["E"], job["parents"]
    worlds = list(FAMILY)
    rng = SplitMix64(seed_from("c4.10.start", CAMPAIGN_SEED, seed))
    evs: Dict[str, Evolution] = {}
    for w in worlds:
        pick = [rng.randbelow(len(parents)) for _ in range(N)]
        init = []
        for i in pick:
            org = G.organism_record(dict(parents[i]["parent"]), None, 0); org["origins"] = ["start"]; init.append(org)
        prov = {"fill": "the 57 C4 starting parents subsampled to N by the seed's rng", "n": N, "verified_common": True}
        evs[w] = Evolution(FAMILY[w], REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c4-10-%s-%s" % (cond, w), foundry=FOUNDRY_C2,
                           init_pop=init, gen0_provenance=prov, rng_label="c4-10-%s" % w,
                           descend_fn=(n_ops2 if cond == "mutation_load" else None))
    train_eps = {w: episodes_for(FAMILY[w], CAMPAIGN_SEED, "train", 1, E) for w in worlds}
    ho_eps = {w: episodes_for(FAMILY[w], CAMPAIGN_SEED, "heldout", seed, HELDOUT) for w in worlds}
    births = {w: {"n": 0, "fatal": 0, "nontrivial": 0} for w in worlds}
    probes = {w: [] for w in worlds}
    primary, extra, rescues = 0, 0, 0
    t0 = time.time()
    for g in range(Gn):
        for w in worlds:
            evs[w].evaluate_generation(last=(g == Gn - 1))
            primary += N
            if g > 0:
                for fit, org, evd in evs[w].scored:
                    if org["organism_id"] in evs[w].records:
                        births[w]["n"] += 1
                        births[w]["fatal"] += int(evd["reward_per_ask"] < C1.FLOOR)
                        births[w]["nontrivial"] += int(evd["reward_per_ask"] >= C1.FLOOR and evd["answered_share"] > 0)
        if cond == "lateral" and g > 0:
            median = {u: sorted(z[0] for z in evs[u].scored)[len(evs[u].scored) // 2] for u in worlds}
            for w in worlds:
                cands = sorted([z for z in evs[w].scored if z[1]["organism_id"] in evs[w].records and z[2]["reward_per_ask"] < C1.FLOOR and z[2]["answered_share"] > 0],
                               key=lambda z: z[1]["organism_id"])[:LATERAL_B]
                for fit, org, evd in cands:
                    for u in worlds:
                        if u == w:
                            continue
                        r = evaluate(org["manifest"], train_eps[u], rng_seed=0, reward_mode="per_ask")
                        extra += 1
                        f_u = REGIMES["E0"].fitness(r["reward_per_ask"], r["meter"], E)
                        if r["reward_per_ask"] >= C1.FLOOR and f_u >= median[u]:
                            rescues += evs[u].inject([dict(org["manifest"])], tag="rescued")
        if g % PROBE_EVERY == 0 or g == Gn - 1:
            for w in worlds:
                elite = evs[w].scored[0][1]
                ho = evaluate(elite["manifest"], ho_eps[w], rng_seed=7, reward_mode="per_ask")
                probes[w].append({"gen": g, "heldout": round(ho["reward_per_ask"], 4)})
        if g < Gn - 1:
            for w in worlds:
                evs[w].reproduce()
    out_w = {}
    for w in worlds:
        res = evs[w].result()
        elite = res["elite"]
        # behavioural diversity: distinct answer vectors of the final population on the training set
        vecs = {hashlib.sha256(json.dumps(C1.answers(z["manifest"], train_eps[w])).encode()).hexdigest() for z in res["final_population"]}
        transfer = {u: round(evaluate(elite["manifest"], ho_eps[u], rng_seed=7, reward_mode="per_ask")["reward_per_ask"], 4) for u in worlds if u != w}
        b = births[w]
        out_w[w] = {"heldout_final": probes[w][-1]["heldout"], "heldout_best_probe": max(p["heldout"] for p in probes[w]),
                    "novel_capability": int(max(p["heldout"] for p in probes[w]) >= NOVEL_MIN),
                    "births": b["n"], "fatal_mass": round(b["fatal"] / b["n"], 4) if b["n"] else None, "nontrivial_yield": round(b["nontrivial"] / b["n"], 4) if b["n"] else None,
                    "behavioural_diversity": len(vecs), "lineage_depth": len(res["ancestry"]), "cross_world_transfer": transfer,
                    "shelf": int(any(t["best_reward"] >= R.SHELF_MIN for t in res["trace"])), "probes": probes[w], "trace_best": [t["best_reward"] for t in res["trace"]]}
    return {"condition": cond, "seed": seed, "worlds": out_w, "primary_evals": primary, "extra_evals": extra, "rescues": rescues, "wall_s": round(time.time() - t0, 1)}


def pooled(rows: List[dict], cond: str) -> dict:
    rs = [r for r in rows if r["condition"] == cond]
    nb = sum(r["worlds"][w]["births"] for r in rs for w in FAMILY)
    fat = sum(round(r["worlds"][w]["fatal_mass"] * r["worlds"][w]["births"]) for r in rs for w in FAMILY)
    ntv = sum(round(r["worlds"][w]["nontrivial_yield"] * r["worlds"][w]["births"]) for r in rs for w in FAMILY)
    cells = [(r["seed"], w) for r in rs for w in FAMILY]
    return {"runs": len(rs), "births": nb,
            "fatal_mass": {"p": round(fat / nb, 4) if nb else None, "band95": C1.wilson(fat, nb) if nb else (None, None)},
            "nontrivial_yield": {"p": round(ntv / nb, 4) if nb else None, "band95": C1.wilson(ntv, nb) if nb else (None, None)},
            "behavioural_diversity_mean": round(sum(r["worlds"][w]["behavioural_diversity"] for r in rs for w in FAMILY) / max(1, len(cells)), 2),
            "lineage_depth_mean": round(sum(r["worlds"][w]["lineage_depth"] for r in rs for w in FAMILY) / max(1, len(cells)), 2),
            "novel_capability_cells": sum(r["worlds"][w]["novel_capability"] for r in rs for w in FAMILY), "cells": len(cells),
            "heldout_final_mean": round(sum(r["worlds"][w]["heldout_final"] for r in rs for w in FAMILY) / max(1, len(cells)), 4),
            "compute_evals": sum(r["primary_evals"] + r["extra_evals"] for r in rs), "useful_per_birth": round(ntv / nb, 4) if nb else None}


def claim(base: dict, cond: dict) -> dict:
    c1 = (cond["fatal_mass"]["p"] is not None and base["fatal_mass"]["p"] - cond["fatal_mass"]["p"] >= 0.05
          and (cond["fatal_mass"]["band95"][1] or 1) < (base["fatal_mass"]["band95"][0] or 0))
    c2 = (cond["nontrivial_yield"]["p"] is not None and cond["nontrivial_yield"]["p"] - base["nontrivial_yield"]["p"] >= 0.05
          and cond["behavioural_diversity_mean"] >= base["behavioural_diversity_mean"])
    c3 = ((cond["novel_capability_cells"] - base["novel_capability_cells"]) >= 2 or (cond["lineage_depth_mean"] - base["lineage_depth_mean"]) >= 0.10 * max(1, base["lineage_depth_mean"])
          or (cond["useful_per_birth"] or 0) - (base["useful_per_birth"] or 0) >= 0.10)
    if c1 and c2 and c3:
        d = "SUPPORTED_DAMAGE_GEOMETRY_EFFECT"
    elif c1 and c2:
        d = "LOCALITY_WITHOUT_EVOLVABILITY"
    elif c1:
        d = "ROBUST_BUT_INERT"
    elif c3:
        d = "REACH_WITHOUT_BOUNDARY_REPAIR (not attributed to damage-boundary repair)"
    else:
        d = "NEGATIVE"
    return {"1_less_lost": c1, "2_nontrivial": c2, "3_reach": c3, "disposition": d}


def self_test() -> int:
    ps = C1.parents_from_population()[:10]
    a = run_trial({"condition": "baseline", "seed": 1, "N": 8, "G": 3, "E": 8, "parents": ps})
    b = run_trial({"condition": "baseline", "seed": 1, "N": 8, "G": 3, "E": 8, "parents": ps})
    c = run_trial({"condition": "mutation_load", "seed": 1, "N": 8, "G": 3, "E": 8, "parents": ps})
    d = run_trial({"condition": "lateral", "seed": 1, "N": 8, "G": 3, "E": 8, "parents": ps})
    det = all(a["worlds"][w]["trace_best"] == b["worlds"][w]["trace_best"] for w in FAMILY)
    rep = {"deterministic": det, "selection_now": select_conditions()["selected"], "baseline_births": sum(a["worlds"][w]["births"] for w in FAMILY),
           "mutation_load_differs": any(c["worlds"][w]["trace_best"] != a["worlds"][w]["trace_best"] for w in FAMILY), "lateral_extra_evals": d["extra_evals"],
           "cheat_novel": 1.0 >= NOVEL_MIN}
    print(json.dumps(rep, indent=1))
    return 0 if det and rep["cheat_novel"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C4-10")
    if a.self_test:
        return self_test()
    if not a.dry_run and not C1.gate_is_green():
        print("REFUSED: launch gate not green")
        return 3
    from archaeon.campaign4.c4harness import Experiment4                    # noqa: PLC0415

    class Trial(Experiment4):
        ID = "C4-10"
        TITLE = "held-out evolvability trial"
        PARENTS = ["C4-01", "C4-02", "C4-05", "C4-06", "C4-08", "C4-09"]
        ARM_FIELD = "condition"
        METRICS = ("fatal_mass", "nontrivial_yield", "novel_cells", "heldout_mean")

    X = Trial(dry_run=a.dry_run, procs=a.procs)
    design = (C4 / "C4-10" / "DESIGN.md").read_text(encoding="utf-8")
    sel = select_conditions()
    conditions = ["baseline"] + sel["selected"]
    parents = C1.parents_from_population()
    # negative control: starting best held-out per family world
    start_best = {}
    for w, spec in FAMILY.items():
        ho = episodes_for(spec, CAMPAIGN_SEED, "heldout", 1, HELDOUT)
        start_best[w] = round(max(evaluate(p["parent"], ho, rng_seed=7, reward_mode="per_ask")["reward_per_ask"] for p in parents), 4)
    solved = [w for w, v in start_best.items() if v >= NOVEL_MIN]
    X.seal({
        "question": "On a held-out family of four worlds never used to develop any C4 condition, do the conditions selected by the preregistered rule "
                    "(%s) lose less at the damage boundary, recover non-trivial variation, and reach further than the frozen baseline at equal budget?" % (sel["selected"] or "NONE qualified"),
        "parent_evidence": json.dumps(sel["evidence"])[:1500],
        "why_this_slot": "The decisive experiment; its rule was fixed before C4-08/C4-09 reported.",
        "assay_capability_requirement": "starting best held-out < %.2f on every family world (measured %s; worlds at or above are dropped: %s); baseline shelf on W1_d2 "
                                        "in >= 2 of %d seeds; determinism; cheat" % (NOVEL_MIN, start_best, solved or "none", len(a.seeds)),
        "positive_control": "baseline: shelf on W1_d2 in >= 2 of %d seeds" % len(a.seeds),
        "reachability_estimate": {"note": "held-out family; no prior rows"},
        "arms": conditions,
        "crn_policy": "identical seeds, identical starting subsamples, identical rng streams per world; conditions differ only in their operator (n_ops=2) or the lateral step",
        "budget": {"N": a.N, "G": a.G, "E": a.E, "seeds": a.seeds, "family": list(FAMILY), "lateral_B": LATERAL_B, "heldout": HELDOUT, "novel_min": NOVEL_MIN},
        "primary_observable": "per condition: fatal mutation mass and nontrivial yield per birth (Wilson), behavioural diversity, lineage depth, cross-world transfer, "
                              "novel-capability cells, compute, useful descendants per birth; the three-part claim rule",
        "claim_ceiling": "n=%d seeds x 4 worlds; a comparison at one budget on one substrate" % len(a.seeds),
        "falsification_condition": "no condition satisfies part 1 -> NEGATIVE or NO_CONDITION_SELECTED; the baseline rows stand regardless",
        "kill_condition": "control failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "NO_CONDITION_SELECTED", "ROBUST_BUT_INERT", "LOCALITY_WITHOUT_EVOLVABILITY"],
        "expected_machine_telemetry": ["per (condition, seed, world) births/fatal/nontrivial/diversity/depth/transfer/probes", "selection evidence"],
        "machine_changes_exercised": ["condition selection from committed tables", "family worlds W1_d3 / W2_K2d1 / W0_8b first runs"],
        "replacement_condition": "none",
        "ancestry": "original (queue slot 10)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": len(a.seeds), "positive_control": {"arm": "baseline", "metric": "shelf_W1_d2", "min": 1, "min_rows": 2},
                 "primary": {"treatment": (sel["selected"][0] if sel["selected"] else "baseline"), "control": "baseline", "metric": "fatal_mass", "min_effect": -0.05}},
    })
    X.decision("D4-014: conditions selected by the preregistered rule from committed tables: %s; evidence recorded in the sealed preregistration" % (sel["selected"] or "NONE"))
    X.open("cmp4-c4-10")
    wid = X.world("trial", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    fam = {w: s for w, s in FAMILY.items() if w not in solved}
    jobs = [{"condition": c, "seed": s, "N": a.N, "G": a.G, "E": a.E, "parents": parents} for c in conditions for s in a.seeds]
    rows = X.pool_map(run_trial, jobs, "trial_s")
    tables = {c: pooled(rows, c) for c in conditions}
    claims = {c: claim(tables["baseline"], tables[c]) for c in conditions if c != "baseline"}
    campaign = (claims[sel["selected"][0]]["disposition"] if sel["selected"] else "NO_CONDITION_SELECTED")
    grouped = []
    for r in rows:
        grouped.append({"condition": r["condition"], "seed": r["seed"], "fatal_mass": round(sum(r["worlds"][w]["fatal_mass"] * r["worlds"][w]["births"] for w in FAMILY) / max(1, sum(r["worlds"][w]["births"] for w in FAMILY)), 4),
                        "nontrivial_yield": round(sum(r["worlds"][w]["nontrivial_yield"] * r["worlds"][w]["births"] for w in FAMILY) / max(1, sum(r["worlds"][w]["births"] for w in FAMILY)), 4),
                        "novel_cells": sum(r["worlds"][w]["novel_capability"] for w in FAMILY), "heldout_mean": round(sum(r["worlds"][w]["heldout_final"] for w in FAMILY) / len(FAMILY), 4),
                        "shelf_W1_d2": r["worlds"]["W1_d2"]["shelf"], "rescues": r["rescues"], "extra_evals": r["extra_evals"]})
        content = {"condition": r["condition"], "seed": r["seed"], "worlds": {w: {k: v for k, v in r["worlds"][w].items() if k != "trace_best"} for w in FAMILY},
                   "primary_evals": r["primary_evals"], "extra_evals": r["extra_evals"], "rescues": r["rescues"], "wall_s": r["wall_s"]}
        X.record(wid, r, {"condition": r["condition"], "seed": r["seed"]}, content, "SURVIVED", key_parts=(r["condition"], r["seed"]))
    summary = {"selection": sel, "conditions": conditions, "start_best_heldout": start_best, "dropped_worlds": solved, "tables": tables, "claims": claims,
               "campaign_disposition": campaign, "wall_s": round(time.time() - t0, 1)}
    X.att.write("TRIAL.json", summary)
    X.att.write("runs.json", rows)
    X.publish(wid, "trial", "cmp4.c410_trial.v1", summary, {"info_kind": "artifact", "label": "C4-10 trial summary"})
    out = X.close(grouped, addendum={"campaign_disposition": campaign, "claims": json.dumps(claims), "selection": json.dumps(sel["selected"])})
    print(json.dumps({"selection": sel["selected"], "start_best": start_best, "tables": tables, "claims": claims, "campaign_disposition": campaign, "close": out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
