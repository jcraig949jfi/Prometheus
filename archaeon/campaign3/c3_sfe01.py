"""C3-SFE-01 -- SHELF-TO-SUMMIT BUDGET SCAN on W2_K2 (campaign 3, slot 1; parents C2-SFE-03/07, SFE-10).

    python -m archaeon.campaign3.c3_sfe01 [--seeds 1..12] [--N 200 --E 16 --G 300] [--dry-run]

Does W2_K2 4-bit have a reachable FULL-solution transition under the current organism /
evaluator / search system, and on what timescale? One run per seed to G_max generations;
the preregistered budget ladder (60, 100, 150, 200, 300) is read off each trace (reach is
monotone in G; the table's monotone lookup pools the same rows at every ladder point).

Arms (common random numbers; identical generation 0 except the substitution):
  fresh   the cell's own generation 0
  shelf   generation 0 with 4 preserved campaign-2 SHELF organisms substituted (dose 4 of
          200; C2-SFE-05 top_k archives fetched from campaign 2's engine world under
          campaign 2's principal; kept iff held-out on W2_K2 is in [0.45, 0.90)), so
          time-to-shelf and shelf-to-summit separate.

Per run, from the trace and probes: first shelf generation (training best >= 0.45), first
foothold (0.5), summit CANDIDATES (training best >= 0.9) each confirmed at once by a 48-episode
held-out probe of that generation's elite (first_summit_gen = first confirmed), shelf
residence (first summit - first shelf, censored at G), which stream (ask position) the elite
solves per generation and how often the identity switches, regression from the shelf
(generations below 0.45 after first reaching it), end-of-run held-out per ask, lineage
ancestry (operators) of the final elite and of the first confirmed summit.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from typing import Dict, List, Optional

from archaeon.wse import digest as D
from archaeon.wse import reachability as R
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, common_fill, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2, REPO
from archaeon.campaign3.c3base import CAMPAIGN_SEED, Experiment3, level_fields

TARGET = WorldSpec("W2_K2", K=2, value_bits=4)
LADDER = [60, 100, 150, 200, 300]
ARMS = ["fresh", "shelf"]
SHELF_DOSE = 4
STREAM_SOLVED = 0.75          # an ask position counts as solved for the elite when its per-ask reward >= this


def stream_profile(per_ask: List[float]) -> str:
    return "".join("1" if v >= STREAM_SOLVED else "0" for v in per_ask) or "-"


def run_arm(job: dict) -> dict:
    arm, seed, N, E, G_ = job["arm"], job["seed"], job["N"], job["E"], job["G"]
    t0 = time.time()
    init = prov = None
    if arm == "shelf" and job.get("shelf_manifests"):
        init, prov = common_fill(CAMPAIGN_SEED, seed, N, job["shelf_manifests"][:SHELF_DOSE], tag="shelf", foundry=FOUNDRY_C2)
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c3-sfe01-" + arm, foundry=FOUNDRY_C2, init_pop=init, gen0_provenance=prov)
    ho_eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48)
    candidates: List[dict] = []
    first_summit = None; summit_elite = None; summit_ancestry = None
    profiles: List[str] = []
    for g in range(G_):
        row = ev.evaluate_generation(last=(g == G_ - 1))
        profiles.append(stream_profile(row.get("elite_per_ask", [])))
        if row["best_reward"] >= R.SUMMIT_MIN and (not candidates or candidates[-1]["gen"] < g - 0 and len(candidates) < 40):
            elite = ev.scored[0][1]
            ho = evaluate(elite["manifest"], ho_eps, rng_seed=7)
            candidates.append({"gen": g, "train": row["best_reward"], "heldout": round(ho["reward"], 4), "per_ask": ho["per_ask_reward"],
                               "confirmed": ho["reward"] >= R.SUMMIT_MIN})
            if first_summit is None and ho["reward"] >= R.SUMMIT_MIN:
                first_summit = g; summit_elite = elite["manifest"]; summit_ancestry = ev.ancestry(elite["organism_id"])
        if g < G_ - 1:
            ev.reproduce()
    res = ev.result()
    ho = evaluate(res["elite"]["manifest"], ho_eps, rng_seed=7)
    tb = [t["best_reward"] for t in res["trace"]]
    first_shelf = R.first_at(tb, R.SHELF_MIN)
    below_after = sum(1 for i, b in enumerate(tb) if first_shelf is not None and i > first_shelf and b < R.SHELF_MIN)
    switches = sum(1 for a, b in zip(profiles, profiles[1:]) if a != b and "1" in a and "1" in b)
    seen = sorted({p for p in profiles if "1" in p})
    lv = level_fields(res, ho["reward"])
    lv["first_summit_gen"] = first_summit
    lv["level"] = "SUMMIT" if first_summit is not None else ("SHELF" if first_shelf is not None else "FLOOR")
    return {"arm": arm, "seed": seed, "G": G_, "competence_heldout": ho["reward"], "heldout_per_ask": ho["per_ask_reward"], "train_last": res["elite_eval"]["reward"],
            "first_solved_gen": res["first_solved_gen"], "reached": 1 if res["first_solved_gen"] is not None else 0, **lv,
            "shelf_reached": 1 if first_shelf is not None else 0, "summit": 1 if first_summit is not None else 0,
            "summit_candidates": len(candidates), "summit_candidates_confirmed": sum(1 for c in candidates if c["confirmed"]),
            "candidates": candidates[:12], "shelf_residence": (None if first_shelf is None else ((first_summit if first_summit is not None else G_) - first_shelf)),
            "shelf_residence_censored": first_summit is None, "gens_below_shelf_after": below_after,
            "ladder": {str(g): {"shelf": int(first_shelf is not None and first_shelf < g), "foothold": int(res["first_solved_gen"] is not None and res["first_solved_gen"] < g),
                                "summit": int(first_summit is not None and first_summit < g), "best": round(max(tb[:g]) if tb[:g] else 0.0, 4)} for g in LADDER if g <= G_},
            "stream_profiles_seen": seen, "stream_switches": switches, "final_profile": profiles[-1], "profile_first_gen": {p: profiles.index(p) for p in seen},
            "pop_max_per_ask_last": res["trace"][-1].get("pop_max_per_ask"), "elite_summary": res["elite_summary"], "elite_origins": res["elite_origins"],
            "import_share_final": res["trace"][-1]["origin_shares"].get("shelf", 0.0), "ancestry_ops_final": _ops(res["ancestry"]),
            "ancestry_ops_summit": _ops(summit_ancestry) if summit_ancestry else None, "summit_elite_manifest": summit_elite, "final_elite_manifest": res["elite"]["manifest"],
            "trace_best": tb, "trace_mean": [t["mean_reward"] for t in res["trace"]], "trace_profile": profiles,
            "gen0_provenance": res["gen0_provenance"], "warnings": res["warnings"], "wall_s": round(time.time() - t0, 1), "_res": res}


def _ops(anc: Optional[list]) -> Optional[dict]:
    if not anc:
        return None
    h: Dict[str, int] = {}
    for a in anc:
        for o in a["operators"]:
            h[o] = h.get(o, 0) + 1
    return {"depth": len(anc), "ops": h}


class ShelfSummit(Experiment3):
    ID = "C3-SFE-01"
    TITLE = "shelf-to-summit budget scan on W2_K2"
    PARENTS = ["C2-SFE-03", "C2-SFE-07", "SFE-10"]
    METRICS = ("competence_heldout", "first_shelf_gen", "first_summit_gen", "summit_candidates", "shelf_residence")


def fetch_shelf(X: ShelfSummit, n_keep: int = 8) -> tuple:
    """Campaign-2 shelf organisms: C2-SFE-05 top_k archives (W2_K2 stream elites) read under
    campaign 2's principal; keep those whose held-out on W2_K2 is in [SHELF_MIN, SUMMIT_MIN)."""
    r5 = json.loads((REPO / "archaeon" / "campaign2" / "C2-SFE-05" / "RECEIPT.json").read_text(encoding="utf-8"))
    wid = r5["worlds"]["retention"]
    if X.dry_run:
        from proteus.foundry import generate as G
        return [o["manifest"] for o in G.generate(dict(FOUNDRY_C2, seed=77, n=n_keep))], {"dry_run": True}
    rd = X.eng.read_campaign(REPO / "archaeon" / "campaign2" / "config.local.json")
    kept, prov = [], {"world": wid, "archives": {}, "dry_run": False}
    eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", 0, 48)
    for name, art in sorted(r5["artifacts"].items()):
        if not name.startswith("archive_top_k_"):
            continue
        obj, info = X.att.step("fetch_shelf", lambda a=art: X.eng.fetch(wid, a["artifact_id"], expected=a.get("declared"), client=rd), parts=(name,), kind="engine")
        scored = []
        for m in obj.get("manifests", []):
            try:
                ho = evaluate(m, eps, rng_seed=7)
                scored.append((ho["reward"], ho["per_ask_reward"], m))
            except Exception:                                        # noqa: BLE001
                pass
        shelf = [(r, pa, m) for r, pa, m in scored if R.SHELF_MIN <= r < R.SUMMIT_MIN]
        prov["archives"][name] = dict(info, n=len(scored), n_shelf=len(shelf), best=max((r for r, _, _ in scored), default=None))
        kept.extend(sorted(shelf, key=lambda z: -z[0]))
    kept.sort(key=lambda z: -z[0])
    prov["kept"] = [{"heldout": round(r, 4), "per_ask": pa} for r, pa, _ in kept[:n_keep]]
    return [m for _, _, m in kept[:n_keep]], prov


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=list(range(1, 13)))
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--G", type=int, default=300)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = ShelfSummit(dry_run=a.dry_run, procs=a.procs)
    reach = X.reachability_for([(TARGET, a.N, g, a.E, "E0") for g in LADDER if g < a.G] + [(TARGET, a.N, a.G, a.E, "E0")])
    X.seal({
        "question": "Does W2_K2 4-bit (N=%d, E=%d) have a reachable FULL solution (held-out >= 0.90) under the current organism/evaluator/search system within %d "
                    "generations, and on what timescale; and does starting on the half-credit shelf (preserved campaign-2 shelf organisms, dose %d of %d) shorten "
                    "the shelf-to-summit time?" % (a.N, a.E, a.G, SHELF_DOSE, a.N),
        "parent_evidence": "Campaign 2: 0/24 training-best >= 0.9 at G60 (L2-039); every foothold on the 0.50-0.56 shelf (L2-025); table at G60: 27 runs, 16 SHELF, "
                           "0 confirmed SUMMIT, 1 training-only candidate (0.9375 at 54, held-out 0.53).",
        "why_this_slot": "Every economics and transfer question on K=2 cells measured time-to-shelf; whether a summit exists at all is the campaign's highest-value "
                         "unresolved boundary and gates C3-SFE-02 and C3-SFE-08.",
        "assay_capability_requirement": "the fresh arm reaches the SHELF in >= 1 of %d seeds (else TARGET_UNREACHABLE for the shelf, a table contradiction); a summit "
                                        "counts only when a 48-episode held-out probe of the candidate generation's elite reads >= 0.90" % len(a.seeds),
        "positive_control": "fresh arm shelf arrival (table: 16/27 at G60); the SHELF organisms' held-out in [0.45, 0.90) checked before use",
        "reachability_estimate": reach,
        "arms": ARMS,
        "crn_policy": "default; identical generation 0 for both arms except the %d substituted shelf organisms; one run per seed to G=%d, ladder points read off the trace" % (SHELF_DOSE, a.G),
        "budget": {"N": a.N, "E": a.E, "G": a.G, "ladder": [g for g in LADDER if g <= a.G], "seeds": a.seeds, "heldout_episodes": 48, "shelf_dose": SHELF_DOSE,
                   "summit_min": R.SUMMIT_MIN, "shelf_min": R.SHELF_MIN, "stream_solved": STREAM_SOLVED},
        "primary_observable": "confirmed summit frequency per arm at G=%d (summit = 1/0 per run) and first_summit_gen; shelf residence (censored); secondary: shelf arrival, "
                              "stream identity per generation and switches, regression from the shelf, candidates vs confirmations" % a.G,
        "claim_ceiling": "at n=%d per arm: 0 summits through G=%d is a CAPABLE NEGATIVE for summit reachability at this budget (upper band reported); "
                         "k summits give a timescale, not a mechanism" % (len(a.seeds), a.G),
        "falsification_condition": "summit frequency (shelf arm) - (fresh arm) < 0.10 => shelf start does not shorten the transition; 0 confirmed summits in %d runs => "
                                   "the summit is OBSERVED_UNREACHABLE at G=%d (band reported)" % (2 * len(a.seeds), a.G),
        "kill_condition": "if the fresh arm reaches the shelf in < 1/%d seeds the table is wrong and the slot stops; if summits are confirmed in >= 6 of 12 fresh runs by "
                          "G=100 the 'summit is hard' premise dies and C3-SFE-02 becomes an anatomy of the transition instead of the shelf" % len(a.seeds),
        "typed_failure_conditions": ["TARGET_UNREACHABLE (fresh shelf 0/%d)" % len(a.seeds), "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE",
                                     "IMMATURE_ARTIFACT is not applicable: the shelf organisms are deliberately partial (recorded, not gating)"],
        "expected_machine_telemetry": ["per-generation elite per-ask profile and population max per ask", "summit candidates with held-out confirmations",
                                       "shelf residence (censored)", "regression from shelf", "ancestry operator histograms (final elite; first summit elite)",
                                       "ladder rows in the reachability table via the monotone lookup", "corridor rows (shelf organisms -> W2_K2)"],
        "replacement_condition": "none: this slot is the campaign's first priority; its outcome replaces C3-SFE-08 if no summit regime exists",
        "ancestry": "original (queue slot 1)",
        "machine_changes_exercised": ["A levels + candidates + confirmation", "B monotone lookup at ladder points", "C corridor rows", "F common_fill dose", "per_ask credit"],
        "decl": {"target": {"baseline_arm": "fresh", "reach_metric": "shelf_reached", "reach_min": 1, "reachability_class": reach["W2_K2"]["at_budget"]["class"]},
                 "n_min": len(a.seeds),
                 "primary": {"treatment": "shelf", "control": "fresh", "metric": "summit", "min_effect": 0.10}},
    })
    X.decision("D3-007: a summit is counted only when confirmed by a 48-episode held-out probe at the candidate generation (D3-006 applied); ladder points are read off one G=%d trace per seed" % a.G)
    X.open("cmp3-sfe01")
    wid = X.world("scan", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    shelf, sprov = fetch_shelf(X)
    X.receipt["shelf_source"] = sprov
    X.att.timing("fetch_s", t0)
    if shelf and not a.dry_run:
        from archaeon.wse import telemetry as T
        mat = T.maturity("W2_K2", max(k["heldout"] for k in sprov["kept"]), [k["heldout"] for k in sprov["kept"]], chance=1 / 16,
                         budget={"campaign": "cmp2/C2-SFE-05", "N": 200, "G": "<=70", "E": 16}, lineage={"archives": list(sprov["archives"])})
        X.publish(wid, "shelf_organisms", "cmp2.pop.shelf_seed.v1", {"manifests": shelf, "kept": sprov["kept"]}, {"info_kind": "artifact"}, maturity=mat)
    jobs = [{"arm": arm, "seed": s, "N": a.N, "E": a.E, "G": a.G, "shelf_manifests": (shelf if arm == "shelf" else None)} for arm in ARMS for s in a.seeds]
    rows = X.pool_map(run_arm, jobs, "scan_s")
    for r in rows:
        res = r.pop("_res")
        X.reach_row(TARGET, res, N=a.N, G=a.G, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["competence_heldout"],
                    kind=None if r["arm"] == "fresh" else "treated", heldout_per_ask=r["heldout_per_ask"])
        if r["arm"] == "shelf":
            X.corridor_row(arm="shelf", source_cell="W2_K2(shelf)", target_cell="W2_K2", kind="init", source_maturity={"solved": False, "shelf": True},
                           source_competence=max((k["heldout"] for k in sprov.get("kept", [])), default=None), source_foundry=R.default_foundry_id(), target_foundry=R.default_foundry_id(),
                           source_budget={"campaign": "cmp2/C2-SFE-05"}, target_budget={"N": a.N, "G": a.G, "E": a.E},
                           init={"dose": SHELF_DOSE, "N": a.N, "level": r["level"], "first_shelf_gen": r["first_shelf_gen"], "first_summit_gen": r["first_summit_gen"],
                                 "first_foothold_gen": r["first_solved_gen"], "seed": r["seed"], "heldout": r["competence_heldout"]})
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "arm": r["arm"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E, "target": TARGET.knobs(), "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("trace_best", "trace_mean", "trace_profile", "elite_summary", "gen0_provenance", "summit_elite_manifest", "final_elite_manifest", "candidates")},
                 "SURVIVED" if r["summit"] else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    summ = {}
    for arm in ARMS:
        rs = sorted([r for r in rows if r["arm"] == arm], key=lambda r: r["seed"])
        summ[arm] = {"shelf": sum(r["shelf_reached"] for r in rs), "summit": sum(r["summit"] for r in rs), "candidates": sum(r["summit_candidates"] for r in rs),
                     "first_shelf": [r["first_shelf_gen"] for r in rs], "first_summit": [r["first_summit_gen"] for r in rs],
                     "residence": [r["shelf_residence"] for r in rs], "heldout": [round(r["competence_heldout"], 3) for r in rs],
                     "best": [round(r["best_train_max"], 3) for r in rs], "profiles": [r["stream_profiles_seen"] for r in rs], "switches": [r["stream_switches"] for r in rs],
                     "ladder": {str(g): {"shelf": sum(r["ladder"][str(g)]["shelf"] for r in rs), "summit": sum(r["ladder"][str(g)]["summit"] for r in rs)} for g in LADDER if g <= a.G}}
    X.receipt["summary"] = summ
    out = X.close(rows)
    print(json.dumps({"summary": summ, "shelf_source": {k: v for k, v in sprov.items() if k != "archives"}, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
