"""C5-02 -- FAIR LATERAL ECOLOGY (campaign 5, Phase A). Preregistration: C5-02/DESIGN.md.

    python -m archaeon.campaign5.c5_02 [--seeds 1..6] [--N 50] [--G 100] [--E 16] [--B 24] [--procs 12] [--dry-run] [--self-test]

Frozen screened worlds (D5-005), the 57 parents as the starting class, the C4-09 lateral rule
(D4-013), and a control at EQUAL TOTAL COMPUTE (extra generations = the lateral arm's transfer
evaluations). Attribution: the improved elite must carry the rescued origin and the improvement
must follow the first rescue into that world.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
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
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from archaeon.wse.economics import REGIMES                                   # noqa: E402
from archaeon.wse.evolve import Evolution, evaluate                          # noqa: E402
from archaeon.wse.worlds import episodes_for                                 # noqa: E402
from archaeon.campaign2.c2base import FOUNDRY_C2                             # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign5.screen_worlds import CANDIDATES, BEST_MAX            # noqa: E402

ID = "C5-02"
WORLDS = ("W2_K2d1", "W2_K2_rand", "W3_K3", "W4_K4")
SPECS = {w: CANDIDATES[w] for w in WORLDS}
PROBE_EVERY = 10
HELDOUT = 48
SCREEN = C5 / "WORLD_SCREEN_2026-09-18.json"


def run_ecology(job: dict) -> dict:
    """arm 'lateral' (G generations, B>0) or 'control' (G_c generations, no lateral step)."""
    arm, seed, N, Gn, E, B, parents = job["arm"], job["seed"], job["N"], job["G"], job["E"], job["B"], job["parents"]
    rng = SplitMix64(seed_from("c5.02.start", CAMPAIGN_SEED, seed))
    evs: Dict[str, Evolution] = {}
    for w in WORLDS:
        pick = [rng.randbelow(len(parents)) for _ in range(N)]
        init = []
        for i in pick:
            org = G.organism_record(dict(parents[i]["parent"]), None, 0); org["origins"] = ["start"]; init.append(org)
        prov = {"fill": "57 C4 parents subsampled to N by the seed's rng", "n": N, "verified_common": True}
        evs[w] = Evolution(SPECS[w], REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c5-02-%s-%s" % (arm, w), foundry=FOUNDRY_C2,
                           init_pop=init, gen0_provenance=prov, rng_label="c5-02-%s" % w)
    train_eps = {w: episodes_for(SPECS[w], CAMPAIGN_SEED, "train", 1, E) for w in WORLDS}
    ho_eps = {w: episodes_for(SPECS[w], CAMPAIGN_SEED, "heldout", seed, HELDOUT) for w in WORLDS}
    transfers = Counter(); first_rescue_gen: Dict[str, Optional[int]] = {w: None for w in WORLDS}
    probes = {w: [] for w in WORLDS}
    primary, extra, rescues = 0, 0, 0
    t0 = time.time()
    for g in range(Gn):
        for w in WORLDS:
            evs[w].evaluate_generation(last=(g == Gn - 1)); primary += N
        if arm == "lateral" and B > 0 and g > 0:
            median = {u: sorted(z[0] for z in evs[u].scored)[len(evs[u].scored) // 2] for u in WORLDS}
            for w in WORLDS:
                cands = sorted([z for z in evs[w].scored if z[1]["organism_id"] in evs[w].records and z[2]["reward_per_ask"] < C1.FLOOR and z[2]["answered_share"] > 0],
                               key=lambda z: z[1]["organism_id"])[:B]
                for fit, org, evd in cands:
                    for u in WORLDS:
                        if u == w:
                            continue
                        r = evaluate(org["manifest"], train_eps[u], rng_seed=0, reward_mode="per_ask"); extra += 1
                        f_u = REGIMES["E0"].fitness(r["reward_per_ask"], r["meter"], E)
                        if r["reward_per_ask"] >= C1.FLOOR and f_u >= median[u]:
                            n_in = evs[u].inject([dict(org["manifest"])], tag="rescued")
                            if n_in:
                                rescues += n_in; transfers[(w, u)] += n_in
                                if first_rescue_gen[u] is None:
                                    first_rescue_gen[u] = g
        if g % PROBE_EVERY == 0 or g == Gn - 1:
            for w in WORLDS:
                elite = evs[w].scored[0][1]
                ho = evaluate(elite["manifest"], ho_eps[w], rng_seed=7, reward_mode="per_ask")
                probes[w].append({"gen": g, "heldout": round(ho["reward_per_ask"], 4), "elite_rescued": "rescued" in elite.get("origins", []),
                                  "elite_train": round(evs[w].scored[0][2]["reward_per_ask"], 4)})
        if g < Gn - 1:
            for w in WORLDS:
                evs[w].reproduce()
    out_w = {}
    for w in WORLDS:
        res = evs[w].result(); pop = res["final_population"]
        n_res = sum(1 for z in pop if "rescued" in z.get("origins", []))
        out_w[w] = {"heldout_final": probes[w][-1]["heldout"], "heldout_best_probe": max(p["heldout"] for p in probes[w]),
                    "rescued_share_final": round(n_res / max(1, len(pop)), 4), "first_rescue_gen": first_rescue_gen[w],
                    "elite_rescued_final": probes[w][-1]["elite_rescued"], "probes": probes[w], "trace_best": [t["best_reward"] for t in res["trace"]],
                    "elite_ancestry_depth": len(res["ancestry"]), "elite_origins": res["elite_origins"]}
    return {"arm": arm, "seed": seed, "N": N, "G": Gn, "E": E, "B": B, "worlds": out_w, "rescues": rescues,
            "transfer_matrix": {"%s->%s" % k: v for k, v in transfers.items()}, "primary_evals": primary, "transfer_evals": extra,
            "total_evals": primary + extra, "wall_s": round(time.time() - t0, 1)}


def attribute(lat: dict, ctl: dict) -> dict:
    """Per world: improvement (lateral - control final held-out >= 1/16) and attribution."""
    out = {}
    for w in WORLDS:
        L, Cc = lat["worlds"][w], ctl["worlds"][w]
        improved = (L["heldout_final"] - Cc["heldout_final"]) >= C1.BAND
        fr = L["first_rescue_gen"]
        # first probe at which the lateral elite's held-out exceeded the control's final by >= band
        first_imp = next((p["gen"] for p in L["probes"] if p["heldout"] - Cc["heldout_final"] >= C1.BAND), None)
        attributable = bool(improved and L["elite_rescued_final"] and fr is not None and first_imp is not None and first_imp >= fr)
        out[w] = {"improved": improved, "lateral_final": L["heldout_final"], "control_final": Cc["heldout_final"], "elite_rescued": L["elite_rescued_final"],
                  "first_rescue_gen": fr, "first_improvement_probe": first_imp, "attributable": attributable, "rescued_share_final": L["rescued_share_final"]}
    return out


def self_test() -> int:
    ps = C1.parents_from_population()
    a = run_ecology({"arm": "lateral", "seed": 1, "N": 8, "G": 4, "E": 8, "B": 0, "parents": ps})
    b = run_ecology({"arm": "control", "seed": 1, "N": 8, "G": 4, "E": 8, "B": 0, "parents": ps})
    c = run_ecology({"arm": "lateral", "seed": 1, "N": 8, "G": 4, "E": 8, "B": 0, "parents": ps})
    neg = all(a["worlds"][w]["trace_best"] == b["worlds"][w]["trace_best"] for w in WORLDS)
    det = json.dumps(a, sort_keys=True, default=str) == json.dumps(c, sort_keys=True, default=str)
    d = run_ecology({"arm": "lateral", "seed": 1, "N": 8, "G": 4, "E": 8, "B": 8, "parents": ps})
    fake_l = {"worlds": {w: {"heldout_final": 1.0, "elite_rescued_final": True, "first_rescue_gen": 1, "probes": [{"gen": 3, "heldout": 1.0}], "rescued_share_final": .5} for w in WORLDS}}
    fake_c = {"worlds": {w: {"heldout_final": 0.5} for w in WORLDS}}
    cheat = all(v["attributable"] for v in attribute(fake_l, fake_c).values())
    screen = json.loads(SCREEN.read_text(encoding="utf-8"))
    rep = {"negative_B0_equals_control": neg, "deterministic": det, "cheat_attribution": cheat, "lateral_B8_rescues": d["rescues"], "transfer_evals": d["transfer_evals"],
           "screen_eligible_all": all(screen["worlds"][w]["eligible"] for w in WORLDS), "screen_best": {w: screen["worlds"][w]["best"] for w in WORLDS}}
    print(json.dumps(rep, indent=1))
    return 0 if (neg and det and cheat and rep["screen_eligible_all"]) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--N", type=int, default=50)
    ap.add_argument("--G", type=int, default=100)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--B", type=int, default=24)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C5-02")
    if a.self_test:
        return self_test()
    from archaeon.campaign5.c5base import harness                            # noqa: PLC0415

    class FairEcology(harness()):
        ID = "C5-02"
        TITLE = "fair lateral ecology (screened worlds, equal total compute, attribution)"
        PARENTS = ["C4-09", "C4-10"]
        ARM_FIELD = "arm"
        METRICS = ("rescues", "worlds_improved", "worlds_attributable", "total_evals")

    X = FairEcology(dry_run=a.dry_run, procs=a.procs)
    design = (C5 / "C5-02" / "DESIGN.md").read_text(encoding="utf-8")
    screen = json.loads(SCREEN.read_text(encoding="utf-8"))
    parents = C1.parents_from_population()
    # screen control: re-measure the frozen worlds' best parent held-out at run time
    remeasure = {}
    for w in WORLDS:
        eps = episodes_for(SPECS[w], CAMPAIGN_SEED, "heldout", 1, HELDOUT)
        remeasure[w] = round(max(evaluate(p["parent"], eps, rng_seed=7, reward_mode="per_ask")["reward_per_ask"] for p in parents), 4)
    screen_ok = all(remeasure[w] == screen["worlds"][w]["best"] and remeasure[w] < BEST_MAX for w in WORLDS)
    X.seal({
        "question": "Does lateral rescue produce reproducible improvement attributable to lateral entry, at EQUAL TOTAL COMPUTE, on worlds screened for headroom "
                    "against every starting parent? Or is it takeover without improvement, or no effect?",
        "parent_evidence": "C4-09: rescues 335-460/seed, survival .30-.55, takeover, one live world improved in 1/3 seeds, extra compute .65-.74 not equalized; "
                           "C4-10: three worlds pre-solved.",
        "why_this_slot": "Phase A's second live signal, with only the identified defects repaired.",
        "assay_capability_requirement": "screen re-measured at run time equals the receipt (%s; all < %.2f: %s); B=0 lateral equals control (self-test); cheat; determinism; "
                                        "control total evaluations within one generation of the lateral arm's" % (remeasure, BEST_MAX, screen_ok),
        "positive_control": "controls arm: screen_ok >= 1.0",
        "reachability_estimate": {"note": "screened worlds; per-world lookups not applied"},
        "arms": ["lateral", "control", "controls"],
        "crn_policy": "identical seeds, starting subsamples and rng streams per world; the control's extra generations use the same streams continued",
        "budget": {"worlds": list(WORLDS), "N": a.N, "G_lateral": a.G, "E": a.E, "B": a.B, "seeds": a.seeds, "heldout": HELDOUT,
                   "screen_receipt": str(SCREEN.relative_to(REPO)).replace("\\", "/"), "screen_sha256": hashlib.sha256(SCREEN.read_bytes()).hexdigest()},
        "primary_observable": "per world: improvement (lateral - control final held-out >= 1/16) and attribution (elite carries rescued origin; first improvement probe "
                              "at or after the first rescue into that world); outcome classes A/B/C; rescued share; compute equality per seed",
        "claim_ceiling": "6 seeds x 4 screened worlds at equal total compute; a count of attributable improvements; no mechanism",
        "falsification_condition": "B requires attributable improvement in >= 4 of 6 seeds on some world; else A (takeover) or C",
        "kill_condition": "screen mismatch or control failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "UNDERPOWERED"],
        "expected_machine_telemetry": ["per-world probes with elite origin", "transfer matrix", "first rescue generation", "compute counts per arm"],
        "machine_changes_exercised": ["equal-total-compute control", "origin-based attribution with timing"],
        "replacement_condition": "none",
        "ancestry": "original (Phase A, slot 2)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": len(a.seeds), "positive_control": {"arm": "controls", "metric": "screen_ok", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "lateral", "control": "control", "metric": "worlds_improved", "min_effect": 1.0}},
    })
    X.decision("D5-006: control generations G_c = ceil(T_lateral / (4 x N)) per seed, computed from the lateral run's measured total; lateral runs first")
    X.open("cmp5-c5-02")
    wid = X.world("fair-ecology", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    lat_jobs = [{"arm": "lateral", "seed": s, "N": a.N, "G": a.G, "E": a.E, "B": a.B, "parents": parents} for s in a.seeds]
    lat = X.pool_map(run_ecology, lat_jobs, "lateral_s")
    ctl_jobs = [{"arm": "control", "seed": r["seed"], "N": a.N, "G": int(math.ceil(r["total_evals"] / (len(WORLDS) * a.N))), "E": a.E, "B": 0, "parents": parents} for r in lat]
    ctl = X.pool_map(run_ecology, ctl_jobs, "control_s")
    by_l = {r["seed"]: r for r in lat}; by_c = {r["seed"]: r for r in ctl}
    attr = {s: attribute(by_l[s], by_c[s]) for s in a.seeds}
    per_world = {w: {"improved_seeds": sum(1 for s in a.seeds if attr[s][w]["improved"]), "attributable_seeds": sum(1 for s in a.seeds if attr[s][w]["attributable"]),
                     "rescued_share_mean": round(sum(attr[s][w]["rescued_share_final"] for s in a.seeds) / len(a.seeds), 4),
                     "lateral_final_mean": round(sum(attr[s][w]["lateral_final"] for s in a.seeds) / len(a.seeds), 4),
                     "control_final_mean": round(sum(attr[s][w]["control_final"] for s in a.seeds) / len(a.seeds), 4)} for w in WORLDS}
    B_cls = any(v["attributable_seeds"] >= 4 for v in per_world.values())
    takeover_worlds = sum(1 for v in per_world.values() if v["rescued_share_mean"] >= 0.5)
    A_cls = (not B_cls) and takeover_worlds >= 2
    outcome = "B_REPRODUCIBLE_ATTRIBUTABLE_IMPROVEMENT" if B_cls else "A_TAKEOVER_WITHOUT_IMPROVEMENT" if A_cls else "C_NO_MEANINGFUL_LATERAL_EFFECT"
    compute = {s: {"lateral_total": by_l[s]["total_evals"], "control_total": by_c[s]["total_evals"], "control_G": by_c[s]["G"],
                   "within_one_generation": abs(by_l[s]["total_evals"] - by_c[s]["total_evals"]) <= len(WORLDS) * a.N} for s in a.seeds}
    grouped = [{"arm": "controls", "screen_ok": float(screen_ok), "n": 1}]
    for r in lat + ctl:
        s = r["seed"]
        grouped.append({"arm": r["arm"], "seed": s, "rescues": r["rescues"], "total_evals": r["total_evals"], "G": r["G"],
                        "worlds_improved": sum(1 for w in WORLDS if attr[s][w]["improved"]) if r["arm"] == "lateral" else 0,
                        "worlds_attributable": sum(1 for w in WORLDS if attr[s][w]["attributable"]) if r["arm"] == "lateral" else 0,
                        **{"heldout_%s" % w: r["worlds"][w]["heldout_final"] for w in WORLDS}})
        content = {k: v for k, v in r.items() if k != "worlds"} | {"worlds": {w: {k: v for k, v in r["worlds"][w].items() if k != "trace_best"} for w in WORLDS}}
        X.record(wid, r, {"arm": r["arm"], "seed": s}, content, "SURVIVED", key_parts=(r["arm"], s))
    summary = {"outcome": outcome, "preserve_lateral_mechanism": B_cls, "per_world": per_world, "attribution": attr, "compute": compute,
               "screen": {"remeasured": remeasure, "ok": screen_ok}, "transfer_matrices": {s: by_l[s]["transfer_matrix"] for s in a.seeds},
               "rescues": {s: by_l[s]["rescues"] for s in a.seeds}, "wall_s": round(time.time() - t0, 1)}
    X.att.write("ECOLOGY.json", summary)
    X.att.write("runs.json", lat + ctl)
    X.publish(wid, "ecology", "cmp5.c502_ecology.v1", summary, {"info_kind": "artifact", "label": "C5-02 fair ecology summary"})
    out = X.close(grouped, addendum={"outcome": outcome, "per_world": json.dumps(per_world), "compute": json.dumps(compute)})
    print(json.dumps({"outcome": outcome, "per_world": per_world, "compute": compute, "screen": summary["screen"], "rescues": summary["rescues"], "close": out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
