"""C3-SFE-10 -- IMPORT TAKEOVER / DOSE ECOLOGY (campaign 3, slot 10; replaces the retired failed-material-transfer programme).

    python -m archaeon.campaign3.c3_sfe10 [--doses 0 1 2 4 8 32] [--G 60] [--seeds 1..12] [--dry-run]
    python -m archaeon.campaign3.c3_sfe10 --recon          # cheap reconnaissance: doses 1/4/32, 2 seeds, 20 generations

How does import dose interact with source maturity and population takeover? Mature W0-general
solvers (C3-SFE-03's elites: solved W0, held-out 1.0 on every delay rung) and MATCHED CONTROL
organisms (the same manifests with their instruction blocks permuted: same length, same opcode
multiset, same VM knobs, no competence) are injected at generation 0 into a fresh population
evolving on W1_d4 (RARE by direct search), at a ladder of doses, with and without the offspring
cap (campaign 3 group F). Measured per generation: import share, pure-resident share, hybrid
share, distinct-genome share, best training reward; per run: takeover time (import share >= 0.9),
resident-lineage survival, target competence (held-out), shelf/summit arrival, whether the
elite descends from the import.

The discriminating contrast is mature vs control at the SAME dose and cap: if the control
takes over as often as the mature material, injection MECHANICS (elitism + tournament on a
small foreign set) amplify foreign lineage regardless of capability.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from archaeon.wse import reachability as R
from archaeon.wse import telemetry as T
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2
from archaeon.campaign3.c3base import CAMPAIGN_3, CAMPAIGN_SEED, Experiment3, level_fields
from proteus.foundry.prng import SplitMix64, seed_from

TARGET = WorldSpec("W1_d4", delay=4, value_bits=4)
SOURCE_CELL = "W0"
WORDS_PER_INSTR = 4
TAKEOVER = 0.9
DEFAULT_DOSES = [0, 1, 4, 32]                # reconnaissance: mature dose 1 of 200 takes over by generation 4-5, so the dose ladder spans 0.5%-16%
CAPS = [None, 0.25, 0.05]                    # the cap is the ecological control parameter the dose ladder turned out not to be
QUALITIES = ["mature", "control"]


def arm_name(quality: str, dose: int, cap: Optional[float]) -> str:
    return "%s_d%d_%s" % (quality if dose else "none", dose, ("cap%g" % cap) if cap else "nocap")


def permute_blocks(manifest: dict, seed: int) -> dict:
    """The matched control: the same instruction blocks in a different order (same length, same
    opcode multiset, same operands, same VM knobs)."""
    g = list(manifest["genome"])
    blocks = [g[i:i + WORDS_PER_INSTR] for i in range(0, len(g), WORDS_PER_INSTR)]
    rng = SplitMix64(seed_from("c3.sfe10.permute", seed) & ((1 << 62) - 1))
    order = list(range(len(blocks)))
    for i in range(len(order) - 1, 0, -1):                    # Fisher-Yates
        j = rng.next_u64() % (i + 1)
        order[i], order[j] = order[j], order[i]
    m = dict(manifest); m["genome"] = [w for k in order for w in blocks[k]]
    return m


def make_control(mature: List[dict], ho_eps, max_tries: int = 20) -> tuple:
    """Permute each mature manifest until it has no target competence (held-out < 0.25)."""
    out, direct = [], []
    for i, m in enumerate(mature):
        for t in range(max_tries):
            c = permute_blocks(m, i * 1000 + t)
            r = evaluate(c, ho_eps, rng_seed=7)["reward"]
            if r < 0.25 or t == max_tries - 1:
                out.append(c); direct.append(round(r, 4)); break
    return out, direct


def run_arm(job: dict) -> dict:
    quality, dose, cap, seed = job["quality"], job["dose"], job["cap"], job["seed"]
    N, E, G_ = job["N"], job["E"], job["G"]
    t0 = time.time()
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c3-sfe10-" + arm_name(quality, dose, cap), foundry=FOUNDRY_C2,
                   offspring_cap=cap, import_tags=("import",))
    ho_eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48)
    src = job["manifests"] or []
    imported = [dict(src[i % len(src)]) for i in range(dose)] if (dose and src) else []
    series = []
    takeover_gen = half_gen = None; first_import_elite = None
    for g in range(G_):
        row = ev.evaluate_generation(last=(g == G_ - 1))
        if g == 0 and imported:
            ev.inject(imported, tag="import")
            row = ev.trace[-1]                                  # origin shares after injection live in the same trace row
        shares = T.origin_shares(ev.pop)
        imp = shares.get("import", 0.0); gen0 = shares.get("gen0", 0.0)
        pure_res = round(max(0.0, 1.0 - imp), 4); hybrid = round(max(0.0, imp + gen0 - 1.0), 4)
        distinct = round(len({tuple(o["manifest"]["genome"]) for o in ev.pop}) / len(ev.pop), 4)
        elite = ev.scored[0][1]
        elite_imp = "import" in elite.get("origins", [])
        res_best = max((z[2]["reward"] for z in ev.scored if "import" not in z[1].get("origins", [])), default=None)
        series.append({"gen": g, "import": imp, "pure_resident": pure_res, "hybrid": hybrid, "distinct": distinct, "best": row["best_reward"],
                       "mean": row["mean_reward"], "elite_import": int(elite_imp), "resident_best": None if res_best is None else round(res_best, 4)})
        if takeover_gen is None and imp >= TAKEOVER:
            takeover_gen = g
        if half_gen is None and imp >= 0.5:
            half_gen = g
        if first_import_elite is None and elite_imp:
            first_import_elite = g
        if g < G_ - 1:
            ev.reproduce()
    res = ev.result()
    ho = evaluate(res["elite"]["manifest"], ho_eps, rng_seed=7)
    lv = level_fields(res, ho["reward"])
    last = series[-1]
    tb = [s["best"] for s in series]
    return {"arm": arm_name(quality, dose, cap), "quality": quality if dose else "none", "dose": dose, "dose_frac": round(dose / N, 4), "cap": cap if cap else 0.0, "cap_label": "cap" if cap else "nocap",
            "seed": seed, "G": G_, "n_imported": len(imported), "competence_heldout": round(ho["reward"], 4), **lv,
            "takeover": int(takeover_gen is not None), "takeover_gen": takeover_gen, "half_gen": half_gen, "first_import_elite_gen": first_import_elite,
            "import_share_final": last["import"], "pure_resident_final": last["pure_resident"], "hybrid_final": last["hybrid"],
            "resident_survives": int(last["pure_resident"] > 0.0), "resident_best_final": last["resident_best"], "elite_import_final": last["elite_import"],
            "distinct_final": last["distinct"], "distinct_min": min(s["distinct"] for s in series), "distinct_min_gen": min(series, key=lambda s: s["distinct"])["gen"],
            "shelf_reached": int(lv["first_shelf_gen"] is not None), "summit": int(lv["first_summit_gen"] is not None),
            "best_g10": round(max(tb[:11]), 4), "best_g30": round(max(tb[:31]), 4),
            "import_series": [s["import"] for s in series], "distinct_series": [s["distinct"] for s in series], "best_series": tb,
            "elite_origins": res["elite_origins"], "elite_summary": res["elite_summary"], "gen0_provenance": res["gen0_provenance"],
            "warnings": res["warnings"], "wall_s": round(time.time() - t0, 1), "_res": res}


class DoseEcology(Experiment3):
    ID = "C3-SFE-10"
    TITLE = "import takeover / dose ecology"
    PARENTS = ["C2-SFE-01", "C3-SFE-01", "C3-SFE-03"]
    METRICS = ("takeover", "takeover_gen", "pure_resident_final", "competence_heldout", "distinct_min", "elite_import_final")


def load_mature(path: Path) -> List[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for r in rows:
        if r.get("general_heldout") == 1 and r.get("elite_manifest"):
            out.append({"seed": r["seed"], "manifest": r["elite_manifest"], "heldout_by_rung": r["heldout_by_rung"], "general_gen": r["general_gen"]})
    return sorted(out, key=lambda x: x["seed"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=list(range(1, 13)))
    ap.add_argument("--doses", nargs="*", type=int, default=DEFAULT_DOSES)
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--source-rows", default=str(CAMPAIGN_3["root"] / "C3-SFE-03" / "rows.json"))
    ap.add_argument("--recon", action="store_true", help="reconnaissance only: doses 1/4/32 mature, no cap, 2 seeds, 20 generations; nothing sealed")
    ap.add_argument("--recon-note", default="", help="the reconnaissance reading, quoted into PARENT EVIDENCE")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    mature_rows = load_mature(Path(a.source_rows))
    mature = [m["manifest"] for m in mature_rows]
    ho_eps0 = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", 0, 48)
    mature_direct = [round(evaluate(m, ho_eps0, rng_seed=7)["reward"], 4) for m in mature]
    control, control_direct = make_control(mature, ho_eps0)
    if a.recon:
        jobs = [{"quality": "mature", "dose": d, "cap": None, "seed": s, "N": a.N, "E": a.E, "G": 20, "manifests": mature} for d in (1, 4, 32) for s in (1, 2)]
        X = DoseEcology(dry_run=True, procs=a.procs)
        rows = X.pool_map(run_arm, jobs, "recon_s")
        for r in rows:
            r.pop("_res")
            print(json.dumps({k: r[k] for k in ("arm", "seed", "takeover_gen", "half_gen", "import_share_final", "pure_resident_final", "best_g10", "competence_heldout", "distinct_min")}))
        print("mature_direct", mature_direct, "control_direct", control_direct)
        return 0
    X = DoseEcology(dry_run=a.dry_run, procs=a.procs)
    doses = sorted(set(a.doses))
    arms = [arm_name("none", 0, None)] if 0 in doses else []
    arms += [arm_name(q, d, c) for d in doses if d for q in QUALITIES for c in CAPS]
    takeover_dose = max(d for d in doses if d) if any(doses) else 0
    mid_dose = 4 if 4 in doses else (sorted(d for d in doses if d)[len([d for d in doses if d]) // 2] if any(doses) else 0)
    reach = X.reachability_for([(TARGET, a.N, a.G, a.E, "E0"), (WorldSpec(SOURCE_CELL, value_bits=4), a.N, a.G, a.E, "E0")])
    X.seal({
        "question": "When mature W0-general solvers or matched permuted controls are injected at generation 0 into a fresh W1_d4 population (N=%d) at doses %s, "
                    "without the offspring cap and with caps %s, when does the import take over (share >= %.1f), do resident lineages survive, and is the takeover "
                    "explained by capability (mature only) or by injection mechanics (control too)? Reconnaissance made the CAP the control parameter: mature dose 1 takes over anyway." % (a.N, doses, [c for c in CAPS if c], TAKEOVER),
        "parent_evidence": "C2-SFE-01: transported material took the population over while the treatment hurt (-0.16). C3-SFE-01 shelf arm: dose 4 of shelf organisms "
                           "reached import share 1.0 in 12/12 seeds by G300 with the cap off. C3-SFE-03: %d W0-general elites with held-out 1.0 on every rung (the mature "
                           "material). Mature direct competence on W1_d4 (held-out 48 episodes): %s; permuted controls: %s. Reconnaissance: %s"
                           % (len(mature), mature_direct, control_direct, a.recon_note or "none recorded"),
        "why_this_slot": "every later experiment that injects organisms needs the dose at which 'transfer' becomes population replacement, and whether the "
                         "replacement is driven by the material's competence or by the injection mechanics; neither number exists.",
        "assay_capability_requirement": "the mature material must be mature (source solved, held-out >= 0.9 on W0) and directly competent on the target (>= 0.5 held-out) "
                                        "else IMMATURE_ARTIFACT / INTERVENTION_NOT_APPLIED; controls must score < 0.25",
        "positive_control": "the takeover-prone dose (%d, mature, no cap) reaches import share >= %.1f within %d generations in >= 8 of %d seeds" % (takeover_dose, TAKEOVER, a.G, len(a.seeds)),
        "reachability_estimate": reach,
        "arms": arms,
        "crn_policy": "default; every arm of a seed shares generation 0 (common fill; the import REPLACES the worst-scored members after the first evaluation) and the "
                      "per-generation episode batteries; the cap redraws the primary parent among residents beyond %.2f of the children" % CAPS[1],
        "budget": {"N": a.N, "E": a.E, "G": a.G, "seeds": a.seeds, "doses": doses, "caps": [c or 0.0 for c in CAPS], "qualities": QUALITIES, "target": TARGET.knobs(),
                   "runs": len(arms) * len(a.seeds), "mature_sources": len(mature)},
        "primary_observable": "takeover (import share >= %.1f by G) and takeover_gen per run, as a function of dose x quality x cap; the declared machine contrast is "
                              "mature vs control at dose %d without the cap" % (TAKEOVER, mid_dose),
        "claim_ceiling": "an ecological reading of THIS loop (tournament 4, elitism 4, N=%d): the dose above which foreign lineage replaces the population, and whether "
                         "the replacement needs competence; no claim about transfer value" % a.N,
        "falsification_condition": "if the permuted control takes over at the same doses as the mature material, capability does not drive takeover: injection mechanics do "
                                   "(the C2 'transport hurts yet takes over' reading is mechanics); if neither takes over below dose %d, injection is ecologically safe "
                                   "at small doses and campaign-2 takeovers were dose effects" % takeover_dose,
        "kill_condition": "the mature material is not directly competent on W1_d4 (held-out < 0.5): the source is not 'mature relevant' and the slot must use another source",
        "typed_failure_conditions": ["IMMATURE_ARTIFACT", "INTERVENTION_NOT_APPLIED", "POSITIVE_CONTROL_FAILED", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["import / pure-resident / hybrid share per generation", "distinct-genome share per generation", "takeover and half-takeover generations",
                                       "resident best reward at the end", "elite origin", "target held-out competence and levels", "reachability rows (treated)"],
        "replacement_condition": "none: the slot is a replacement itself (failed-fragment transfer retired); it is moot only if no mature source exists",
        "ancestry": "replacement (queue slot 10; the retired failed-material-transfer programme)",
        "machine_changes_exercised": ["F inject + offspring_cap", "origin shares per generation", "levels + held-out", "reachability rows"],
        "decl": {"positive_control": {"arm": arm_name("mature", takeover_dose, None), "metric": "takeover", "min": 1, "min_rows": 8}, "n_min": len(a.seeds),
                 "primary": {"treatment": arm_name("mature", mid_dose, None), "control": arm_name("control", mid_dose, None), "metric": "takeover", "min_effect": 0.5},
                 "battery": [{"name": "control_takeover_at_mid_dose_below_half", "passed": None},
                             {"name": "mature_takeover_monotone_in_dose", "passed": None},
                             {"name": "cap_slows_takeover", "passed": None}]},
    })
    X.decision("D3-014: the matched control is the SAME instruction blocks permuted (length, opcode multiset, operands and VM knobs preserved; competence removed, verified < 0.25 held-out)")
    X.decision("D3-015: injection at generation 0 after the first evaluation (inject replaces the worst-scored residents); the cap arm uses offspring_cap=%.2f on the 'import' origin" % CAPS[1])
    X.open("C3-SFE-10 import takeover / dose ecology on W1_d4")
    wid = X.world("dose", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    if not a.dry_run:
        mat = T.maturity(SOURCE_CELL, max(mature_direct) if mature_direct else 0.0, [m["heldout_by_rung"]["R0"] for m in mature_rows], chance=1 / 16,
                         budget={"campaign": "cmp3/C3-SFE-03", "N": 200, "G": "hold+100", "E": 16}, competence=max(mature_direct) if mature_direct else None,
                         lineage={"seeds": [m["seed"] for m in mature_rows], "general_gen": [m["general_gen"] for m in mature_rows]})
        art = X.publish(wid, "mature_sources", "cmp3.pop.mature_w0.v1", {"manifests": mature, "direct_w1d4": mature_direct, "heldout_by_rung": [m["heldout_by_rung"] for m in mature_rows]},
                        {"info_kind": "artifact"}, maturity=mat)
        fetched = X.import_fetch("mature_sources", wid, wid, art)
        if fetched and isinstance(fetched, dict) and fetched.get("manifests"):
            mature = fetched["manifests"]                        # the run uses the bytes the consumer fetched back
        X.publish(wid, "control_sources", "cmp3.pop.control_permuted.v1", {"manifests": control, "direct_w1d4": control_direct}, {"info_kind": "artifact"}, maturity=mat | {"solved": False, "note": "permuted control"})
    jobs = []
    for d in doses:
        for q in (QUALITIES if d else ["none"]):
            for c in (CAPS if d else [None]):
                for s in a.seeds:
                    jobs.append({"quality": q, "dose": d, "cap": c, "seed": s, "N": a.N, "E": a.E, "G": a.G, "manifests": (mature if q == "mature" else control if q == "control" else None)})
    rows = X.pool_map(run_arm, jobs, "ecology_s")
    for r in rows:
        res = r.pop("_res")
        X.reach_row(TARGET, res, N=a.N, G=a.G, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["competence_heldout"], kind=None if r["dose"] == 0 else "treated")
        r["mature_direct"] = mature_direct; r["control_direct"] = control_direct
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "arm": r["arm"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E, "dose": r["dose"], "quality": r["quality"], "cap": r["cap"],
                          "target": TARGET.knobs(), "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("import_series", "distinct_series", "best_series", "elite_summary", "gen0_provenance")},
                 "SURVIVED" if r["takeover"] else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    # battery outcomes computed from the rows (names preregistered in decl.battery)
    def arm_rows(q, d, c):
        return [r for r in rows if r["arm"] == arm_name(q, d, c)]
    def rate(rs, key="takeover"):
        return (sum(r[key] for r in rs) / len(rs)) if rs else None
    ctrl_mid = rate(arm_rows("control", mid_dose, None))
    mat_rates = [rate(arm_rows("mature", d, None)) for d in doses if d]
    mono = all(x is not None and y is not None and y >= x for x, y in zip(mat_rates, mat_rates[1:]))
    def med(xs):
        xs = sorted(x for x in xs if x is not None); return None if not xs else xs[len(xs) // 2]
    tg_nocap = med([r["takeover_gen"] for r in arm_rows("mature", mid_dose, None)]); tg_cap = med([r["takeover_gen"] for r in arm_rows("mature", mid_dose, CAPS[1])])
    cap_rate_nocap = rate(arm_rows("mature", mid_dose, None)); cap_rate_cap = rate(arm_rows("mature", mid_dose, CAPS[1]))
    cap_slows = (cap_rate_cap is not None and cap_rate_nocap is not None and cap_rate_cap < cap_rate_nocap) or (tg_cap is not None and tg_nocap is not None and tg_cap > tg_nocap)
    battery = [{"name": "control_takeover_at_mid_dose_below_half", "passed": (ctrl_mid is not None and ctrl_mid < 0.5), "value": ctrl_mid},
               {"name": "mature_takeover_monotone_in_dose", "passed": mono, "value": mat_rates},
               {"name": "cap_slows_takeover", "passed": cap_slows, "value": {"rate_nocap": cap_rate_nocap, "rate_cap": cap_rate_cap, "median_gen_nocap": tg_nocap, "median_gen_cap": tg_cap}}]
    summ: Dict[str, dict] = {}
    for arm in arms:
        rs = sorted([r for r in rows if r["arm"] == arm], key=lambda r: r["seed"])
        if not rs:
            continue
        summ[arm] = {"n": len(rs), "takeover": sum(r["takeover"] for r in rs), "takeover_gen": [r["takeover_gen"] for r in rs], "half_gen_med": med([r["half_gen"] for r in rs]),
                     "resident_survives": sum(r["resident_survives"] for r in rs), "pure_resident_final_med": med([r["pure_resident_final"] for r in rs]),
                     "elite_import_final": sum(r["elite_import_final"] for r in rs), "heldout_med": med([r["competence_heldout"] for r in rs]),
                     "shelf": sum(r["shelf_reached"] for r in rs), "summit": sum(r["summit"] for r in rs), "first_summit_med": med([r["first_summit_gen"] for r in rs]),
                     "distinct_min_med": med([r["distinct_min"] for r in rs]), "resident_best_med": med([r["resident_best_final"] for r in rs])}
    X.receipt["summary"] = summ; X.receipt["battery"] = battery
    X.receipt["sources"] = {"mature_seeds": [m["seed"] for m in mature_rows], "mature_direct": mature_direct, "control_direct": control_direct}
    out = X.close(rows, meas_extra={"battery": battery})
    print(json.dumps({"summary": summ, "battery": battery, "sources": X.receipt["sources"], **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
