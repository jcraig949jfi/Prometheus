"""C3-SFE-04 -- CORRIDOR MAP (campaign 3, slot 4; replaces a dead campaign 1/2 transfer lane).

    python -m archaeon.campaign3.c3_sfe04 [--seeds 1..6] [--G 100] [--dry-run]

Which solved tasks are natural stepping stones into which difficult cells? Mature sources only:
  W0_solver       a W0-competent elite harvested here (held-out >= 0.9 on W0, NOT delay-general)
  delay_general   a C3-SFE-03 elite (held-out 1.0 on delays 0/1/2/4)
Targets: the delay family beyond the ladder (d8, d16), the two-stream family (W2_K2, W3_K2) and
one OBSERVED_UNREACHABLE cell (W7_K2 ASK2).

Two phases, cheap first (the directive's rule: spend evolutionary budget only on informative edges):
  1 DIRECT REUSE (free): every source organism on every target's 48 held-out episodes. An edge
    whose direct competence is already >= 0.9 needs no search; one at chance may still have an
    initialization advantage.
  2 SEARCH (informative edges only): per target, three arms at matched budget and CRN --
    baseline (fresh), init_mature (dose 4 of the best-direct mature source family) and
    init_control (dose 4 of the SAME manifests with their instruction blocks permuted: same
    length, same opcode multiset, no competence). Measured: time-to-foothold, time-to-shelf,
    time-to-full-solve, final level, held-out competence, import share.

Edge types recorded in the corridor table: direct competence / initialization advantage /
time-to-foothold / time-to-full-solve / no measurable corridor. The baseline arm doubles as the
matched-budget direct-search comparator C3-SFE-03 lacked (L3-013).
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
from archaeon.wse.evolve import Evolution, common_fill, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2
from archaeon.campaign3.c3base import CAMPAIGN_3, CAMPAIGN_SEED, Experiment3, level_fields
from archaeon.campaign3.c3_sfe10 import make_control

W0 = WorldSpec("W0", value_bits=4)
TARGETS = [WorldSpec("W1_d8", delay=8, value_bits=4), WorldSpec("W1_d16", delay=16, value_bits=4),
           WorldSpec("W2_K2", K=2, value_bits=4), WorldSpec("W3_K2", K=2, ask_mode="one", value_bits=4),
           WorldSpec("W7_K2", K=2, ask_kind="ASK2", value_bits=4)]
FAMILIES = ["W0_solver", "delay_general"]
DOSE = 4
HELDOUT_N = 48
DIRECT_SOLVED = 0.9            # an edge with direct competence >= this needs no search
CHANCE = {"W1_d8": 1 / 16, "W1_d16": 1 / 16, "W2_K2": 1 / 16, "W3_K2": 1 / 16, "W7_K2": 1 / 16}


def harvest_w0(job: dict) -> dict:
    """A mature W0 source: evolve W0 until the elite solves it (held-out >= 0.9) or G runs out."""
    seed, N, E, G_ = job["seed"], job["N"], job["E"], job["G"]
    ev = Evolution(W0, REGIMES["E0"], CAMPAIGN_SEED, 9000 + seed, N=N, E=E, branch="c3-sfe04-harvest", foundry=FOUNDRY_C2)
    ho = episodes_for(W0, CAMPAIGN_SEED, "heldout", 9000 + seed, HELDOUT_N)
    best = None
    for g in range(G_):
        row = ev.evaluate_generation(last=(g == G_ - 1))
        if row["best_reward"] >= 0.9:
            m = ev.scored[0][1]["manifest"]
            r = evaluate(m, ho, rng_seed=7)["reward"]
            if r >= 0.9:
                best = {"manifest": m, "heldout": round(r, 4), "gen": g}
                break
        if g < G_ - 1:
            ev.reproduce()
    res = ev.result()
    if best is None:
        r = evaluate(res["elite"]["manifest"], ho, rng_seed=7)["reward"]
        best = {"manifest": res["elite"]["manifest"], "heldout": round(r, 4), "gen": G_ - 1}
    best["seed"] = seed
    best["final_rewards"] = [z["reward"] for z in res["final_population"]]
    best["wall_s"] = round(time.time() - job["t0"], 1) if job.get("t0") else None
    return best


def direct_probe(job: dict) -> dict:
    """Held-out competence of one source organism on one target cell (no search)."""
    spec = WorldSpec(**job["spec"])
    eps = episodes_for(spec, CAMPAIGN_SEED, "heldout", job["seed"], HELDOUT_N)
    e = evaluate(job["manifest"], eps, rng_seed=7)
    return {"family": job["family"], "source_index": job["source_index"], "target": spec.name, "seed": job["seed"],
            "direct": round(e["reward"], 4), "per_ask": [round(x, 4) for x in e.get("per_ask_reward", [])]}


def run_target(job: dict) -> dict:
    arm, seed, N, E, G_ = job["arm"], job["seed"], job["N"], job["E"], job["G"]
    spec = WorldSpec(**job["spec"])
    t0 = time.time()
    init = prov = None
    if arm != "baseline" and job.get("manifests"):
        init, prov = common_fill(CAMPAIGN_SEED, seed, N, job["manifests"][:DOSE], tag="import", foundry=FOUNDRY_C2)
    ev = Evolution(spec, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c3-sfe04-" + spec.name + "-" + arm,
                   foundry=FOUNDRY_C2, init_pop=init, gen0_provenance=prov)
    ho = episodes_for(spec, CAMPAIGN_SEED, "heldout", seed, HELDOUT_N)
    for g in range(G_):
        ev.evaluate_generation(last=(g == G_ - 1))
        if g < G_ - 1:
            ev.reproduce()
    res = ev.result()
    e = evaluate(res["elite"]["manifest"], ho, rng_seed=7)
    lv = level_fields(res, e["reward"])
    tb = [t["best_reward"] for t in res["trace"]]
    return {"arm": arm, "target": spec.name, "seed": seed, "G": G_, "family": job.get("family"),
            "competence_heldout": round(e["reward"], 4), "heldout_per_ask": [round(x, 4) for x in e.get("per_ask_reward", [])], **lv,
            "foothold": int(res["first_solved_gen"] is not None), "shelf": int(lv["first_shelf_gen"] is not None),
            "summit": int(lv["first_summit_gen"] is not None), "best_train_g20": round(max(tb[:21]), 4),
            "import_share_final": res["trace"][-1]["origin_shares"].get("import", 0.0), "elite_origins": res["elite_origins"],
            "elite_summary": res["elite_summary"], "trace_best": tb, "gen0_provenance": res["gen0_provenance"],
            "warnings": res["warnings"], "wall_s": round(time.time() - t0, 1), "_res": res}


class CorridorMap(Experiment3):
    ID = "C3-SFE-04"
    TITLE = "corridor map"
    PARENTS = ["C3-SFE-03", "C3-SFE-01", "C2-SFE-05"]
    METRICS = ("competence_heldout", "first_foothold_gen", "first_shelf_gen", "first_summit_gen", "summit")
    ARM_FIELD = "arm"


def load_general(path: Path) -> List[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [{"seed": r["seed"], "manifest": r["elite_manifest"], "heldout_by_rung": r["heldout_by_rung"]}
            for r in sorted(rows, key=lambda r: r["seed"]) if r.get("general_heldout") == 1 and r.get("elite_manifest")]


def med(xs):
    xs = sorted(x for x in xs if x is not None)
    return None if not xs else xs[len(xs) // 2]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--G", type=int, default=100)
    ap.add_argument("--harvest-G", type=int, default=60)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--source-rows", default=str(CAMPAIGN_3["root"] / "C3-SFE-03" / "rows.json"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = CorridorMap(dry_run=a.dry_run, procs=a.procs)
    t0 = time.time()
    general = load_general(Path(a.source_rows))
    harvest = X.pool_map(harvest_w0, [{"seed": s, "N": a.N, "E": a.E, "G": a.harvest_G, "t0": time.time()} for s in a.seeds], "harvest_s")
    w0_solvers = [h for h in harvest if h["heldout"] >= 0.9]
    sources = {"W0_solver": [h["manifest"] for h in w0_solvers], "delay_general": [g["manifest"] for g in general]}
    # phase 1: direct reuse (free)
    probes = []
    for fam, ms in sources.items():
        for i, m in enumerate(ms):
            for spec in TARGETS + [W0]:
                probes.append({"family": fam, "source_index": i, "manifest": m, "spec": spec.knobs(), "seed": 1})
    direct = X.pool_map(direct_probe, probes, "direct_s")
    dmap: Dict[tuple, List[float]] = {}
    for d in direct:
        dmap.setdefault((d["family"], d["target"]), []).append(d["direct"])
    direct_tbl = {"%s->%s" % k: {"n": len(v), "best": max(v), "median": med(v), "solved": sum(1 for x in v if x >= DIRECT_SOLVED)} for k, v in sorted(dmap.items())}
    # preregistered edge selection: a target is informative unless EVERY mature family already solves it directly
    informative = [spec for spec in TARGETS if max(max(dmap.get((f, spec.name), [0.0])) for f in FAMILIES) < DIRECT_SOLVED]
    best_family = {spec.name: max(FAMILIES, key=lambda f: max(dmap.get((f, spec.name), [0.0]))) for spec in TARGETS}
    X.att.timing("phase1_s", t0)
    reach = X.reachability_for([(spec, a.N, a.G, a.E, "E0") for spec in TARGETS])
    X.seal({
        "question": "Which mature solutions are stepping stones into which difficult cells? For sources %s and targets %s: what does a mature solution already "
                    "contain (direct held-out competence), and where it does not solve the target, does initializing a search with dose %d of it change "
                    "time-to-foothold, time-to-shelf, time-to-full-solve or the final level against a matched fresh baseline and a permuted-control import?"
                    % (FAMILIES, [s.name for s in TARGETS], DOSE),
        "parent_evidence": "C3-SFE-03: 11 delay-general elites (held-out 1.0 on delays 0/1/2/4) and the corridor W0 -> d1 -> free; its comparator gap (direct W1_d4 "
                           "measured at G60 only) is L3-013, closed here by the baseline arm at G%d. C3-SFE-01: W2_K2 summit OBSERVED_UNREACHABLE through G300; its "
                           "shelf material is NOT mature (shelf, not solved) and is therefore excluded as a source. Campaign-2 corridor rows: W0 -> W3_K2 direct 0.54 "
                           "(n=10), W2_K2 -> W1_d4 direct 0.96 (n=6). Table: W1_d8/W1_d16 UNESTABLISHED, W2_K2 REACHABLE/summit OBSERVED_UNREACHABLE, W3_K2 REACHABLE "
                           "(N=100 only), W7_K2 OBSERVED_UNREACHABLE (0/10 at G60). Direct-probe table measured before sealing: %s" % (a.G, direct_tbl),
        "why_this_slot": "the reachability table says which cells are hard; nothing says which hard cells are hard FROM WHERE. A sparse traversable graph turns every "
                         "later rare-cell question into a route choice instead of a fresh search, and the same run supplies the matched-budget direct comparator "
                         "C3-SFE-03 could not claim without.",
        "assay_capability_requirement": "at least 4 mature W0 solvers harvested (held-out >= 0.9 on W0) and >= 8 delay-general sources; the baseline arm must reach a "
                                        "foothold on at least one target (else the targets are all out of reach at this budget and only direct reuse is readable)",
        "positive_control": "the delay_general family solves W1_d8/W1_d16 directly, or the baseline arm reaches a foothold on W2_K2 (table: REACHABLE 24/51)",
        "reachability_estimate": reach,
        "arms": ["baseline", "init_mature", "init_control"],
        "crn_policy": "default; per (target, seed) the three arms share generation 0 (common fill: the import REPLACES the first %d organisms of the same base "
                      "population) and every per-generation battery; the permuted control uses the SAME manifests as init_mature. Targets a mature family already "
                      "solves directly get the baseline arm ONLY, to fill their direct-search class in the reachability table (W1_d8/W1_d16 are UNESTABLISHED)" % DOSE,
        "budget": {"N": a.N, "E": a.E, "G": a.G, "seeds": a.seeds, "dose": DOSE, "harvest_G": a.harvest_G, "heldout_n": HELDOUT_N,
                   "targets": [s.knobs() for s in TARGETS], "informative_targets": [s.name for s in informative],
                   "table_fill_baselines": [s.name for s in TARGETS if s not in informative],
                   "runs": len(informative) * 3 * len(a.seeds) + (len(TARGETS) - len(informative)) * len(a.seeds), "direct_probes": len(probes)},
        "primary_observable": "per informative edge: first_foothold_gen, first_shelf_gen, first_summit_gen and final held-out competence, init_mature vs baseline "
                              "(paired by seed); the machine primary is the pooled foothold rate init_mature vs baseline",
        "claim_ceiling": "a sparse map at n=%d per edge and G=%d: which edges show a measurable initialization advantage over a matched baseline, with the permuted "
                         "control as the capability test; no claim that the advantage transfers structure rather than search time" % (len(a.seeds), a.G),
        "falsification_condition": "init_mature does not beat baseline on foothold rate by >= 0.25 pooled over informative edges => no measurable corridor at this "
                                   "budget beyond direct competence",
        "kill_condition": "fewer than 4 mature W0 solvers or fewer than 8 delay-general sources (no mature source set); or every target is solved directly (no "
                          "search question left)",
        "typed_failure_conditions": ["IMMATURE_ARTIFACT", "TARGET_UNREACHABLE", "POSITIVE_CONTROL_FAILED", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["direct-reuse matrix (family x target)", "levels and transition generations per run", "import share", "corridor rows (direct and init)",
                                       "reachability rows for every target incl. the UNESTABLISHED delay cells"],
        "replacement_condition": "if C3-SFE-03 had found no reliable corridor the map would have no mature multi-cell source; it did (11/12 delay-general)",
        "ancestry": "replacement (queue slot 4; the retired campaign 1/2 transfer lane). This is NOT 'does transferred residue help': every source is mature and the "
                    "question is which subsequent searches its capability makes reachable",
        "machine_changes_exercised": ["C corridor table (direct + init rows)", "A levels", "B reachability rows for UNESTABLISHED cells", "F common_fill dose"],
        "decl": {"n_min": len(a.seeds) * max(1, len(informative)),
                 "primary": {"treatment": "init_mature", "control": "baseline", "metric": "foothold", "min_effect": 0.25},
                 "battery": [{"name": "permuted_control_gives_no_advantage", "passed": None},
                             {"name": "advantage_survives_excluding_directly_solved_edges", "passed": None},
                             {"name": "advantage_is_not_only_generation_0", "passed": None}]},
    })
    X.decision("D3-016: mature sources only -- W0 solvers harvested here (held-out >= 0.9) and C3-SFE-03 delay-general elites; the W2_K2 shelf material is excluded (not solved)")
    X.decision("D3-017: edge selection is preregistered and cheap-first: a target is informative unless a mature family already solves it directly (>= %.2f held-out)" % DIRECT_SOLVED)
    X.open("C3-SFE-04 corridor map: direct reuse then informative-edge searches")
    wid = X.world("map", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    if not a.dry_run and w0_solvers:
        mat = T.maturity("W0", max(h["heldout"] for h in w0_solvers), [h["heldout"] for h in w0_solvers], chance=1 / 16,
                         budget={"campaign": "cmp3/C3-SFE-04", "N": a.N, "G": a.harvest_G, "E": a.E},
                         competence=max(h["heldout"] for h in w0_solvers), lineage={"seeds": [h["seed"] for h in w0_solvers], "gens": [h["gen"] for h in w0_solvers]})
        X.publish(wid, "w0_solvers", "cmp3.pop.w0_solvers.v1", {"manifests": sources["W0_solver"], "heldout": [h["heldout"] for h in w0_solvers]},
                  {"info_kind": "artifact"}, maturity=mat)
        X.publish(wid, "direct_matrix", "cmp3.corridor.direct.v1", {"table": direct_tbl, "probes": direct}, {"info_kind": "observation"})
    # phase 2: searches on informative edges
    jobs = []
    controls: Dict[str, list] = {}
    ho0 = episodes_for(W0, CAMPAIGN_SEED, "heldout", 1, HELDOUT_N)
    for spec in informative:
        fam = best_family[spec.name]
        ms = sources[fam][:DOSE]
        if fam not in controls:
            controls[fam], _ = make_control(sources[fam][:DOSE], ho0)
        for s in a.seeds:
            jobs.append({"arm": "baseline", "spec": spec.knobs(), "seed": s, "N": a.N, "E": a.E, "G": a.G, "manifests": None, "family": None})
            jobs.append({"arm": "init_mature", "spec": spec.knobs(), "seed": s, "N": a.N, "E": a.E, "G": a.G, "manifests": ms, "family": fam})
            jobs.append({"arm": "init_control", "spec": spec.knobs(), "seed": s, "N": a.N, "E": a.E, "G": a.G, "manifests": controls[fam], "family": fam + "_permuted"})
    for spec in TARGETS:                                   # table fill: direct-search class for the cells a mature family already solves
        if spec in informative:
            continue
        for s in a.seeds:
            jobs.append({"arm": "baseline", "spec": spec.knobs(), "seed": s, "N": a.N, "E": a.E, "G": a.G, "manifests": None, "family": None})
    rows = X.pool_map(run_target, jobs, "search_s")
    fid = R.default_foundry_id()
    for r in rows:
        res = r.pop("_res")
        spec = next(s for s in TARGETS if s.name == r["target"])
        X.reach_row(spec, res, N=a.N, G=a.G, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["competence_heldout"],
                    kind=None if r["arm"] == "baseline" else "treated", heldout_per_ask=r["heldout_per_ask"] or None)
        if r["arm"] != "baseline":
            base = next((b for b in rows if b["arm"] == "baseline" and b["target"] == r["target"] and b["seed"] == r["seed"]), None)
            X.corridor_row(arm=r["arm"], source_cell=("W0" if r["family"].startswith("W0") else "ladder:W0>W1_d1>W1_d2>W1_d4"), target_cell=r["target"], kind="init",
                           source_maturity={"solved": r["arm"] == "init_mature", "family": r["family"]},
                           source_competence=max(dmap.get((r["family"].replace("_permuted", ""), r["target"]), [0.0])),
                           source_foundry=fid, target_foundry=fid, source_budget={"campaign": "cmp3", "family": r["family"]},
                           target_budget={"N": a.N, "G": a.G, "E": a.E},
                           init={"dose": DOSE, "N": a.N, "level": r["level"], "seed": r["seed"], "first_shelf_gen": r["first_shelf_gen"],
                                 "first_summit_gen": r["first_summit_gen"], "first_foothold_gen": r["first_foothold_gen"],
                                 "heldout": r["competence_heldout"], "baseline_level": None if base is None else base["level"],
                                 "baseline_foothold_gen": None if base is None else base["first_foothold_gen"]})
    for fam in FAMILIES:
        for spec in TARGETS:
            v = dmap.get((fam, spec.name))
            if v:
                X.corridor_row(arm="direct", source_cell=("W0" if fam == "W0_solver" else "ladder:W0>W1_d1>W1_d2>W1_d4"), target_cell=spec.name, kind="direct",
                               source_maturity={"solved": True, "family": fam}, source_competence=max(v), source_foundry=fid, target_foundry=fid,
                               source_budget={"campaign": "cmp3", "family": fam}, target_budget={"heldout_episodes": HELDOUT_N},
                               direct_reuse={"best": max(v), "median": med(v), "n_sources": len(v)}, note="direct reuse probe, no search")
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "arm": r["arm"], "target": r["target"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E,
                          "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("trace_best", "elite_summary", "gen0_provenance")},
                 "SURVIVED" if r["foothold"] else "FALSIFIED", (r["target"], r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    # battery
    def sel(arm, target=None):
        return [r for r in rows if r["arm"] == arm and (target is None or r["target"] == target)]
    def rate(rs, key="foothold"):
        return round(sum(r[key] for r in rs) / len(rs), 4) if rs else None
    ctrl_adv = (rate(sel("init_control")) or 0) - (rate(sel("baseline")) or 0)
    mat_adv = (rate(sel("init_mature")) or 0) - (rate(sel("baseline")) or 0)
    not_solved = [s.name for s in informative if max(max(dmap.get((f, s.name), [0.0])) for f in FAMILIES) < 0.5]
    sub_m = [r for r in sel("init_mature") if r["target"] in not_solved]; sub_b = [r for r in sel("baseline") if r["target"] in not_solved]
    g20 = (med([r["best_train_g20"] for r in sel("init_mature")]), med([r["best_train_g20"] for r in sel("baseline")]))
    battery = [{"name": "permuted_control_gives_no_advantage", "passed": bool(ctrl_adv < max(0.1, mat_adv / 2)), "value": {"control_advantage": ctrl_adv, "mature_advantage": mat_adv}},
               {"name": "advantage_survives_excluding_directly_solved_edges", "passed": bool(sub_m and sub_b and (rate(sub_m) - rate(sub_b)) >= 0.25), "value": {"targets": not_solved, "mature": rate(sub_m), "baseline": rate(sub_b)}},
               {"name": "advantage_is_not_only_generation_0", "passed": bool(g20[0] is not None and g20[1] is not None and g20[0] > g20[1]), "value": {"median_best_by_g20_mature": g20[0], "median_best_by_g20_baseline": g20[1]}}]
    summ: Dict[str, dict] = {"table_fill": {spec.name: {"foothold": sum(r["foothold"] for r in sel("baseline", spec.name)), "shelf": sum(r["shelf"] for r in sel("baseline", spec.name)),
                                             "summit": sum(r["summit"] for r in sel("baseline", spec.name)), "n": len(sel("baseline", spec.name)),
                                             "heldout_med": med([r["competence_heldout"] for r in sel("baseline", spec.name)])} for spec in TARGETS if spec not in informative},
                             "direct": direct_tbl, "harvest": {"n": len(w0_solvers), "heldout": [h["heldout"] for h in w0_solvers], "gens": [h["gen"] for h in w0_solvers]},
                             "informative": [s.name for s in informative], "best_family": best_family, "edges": {}}
    for spec in informative:
        e = {}
        for arm in ("baseline", "init_mature", "init_control"):
            rs = sorted(sel(arm, spec.name), key=lambda r: r["seed"])
            e[arm] = {"n": len(rs), "foothold": sum(r["foothold"] for r in rs), "shelf": sum(r["shelf"] for r in rs), "summit": sum(r["summit"] for r in rs),
                      "foothold_gen": [r["first_foothold_gen"] for r in rs], "shelf_gen": [r["first_shelf_gen"] for r in rs],
                      "heldout_med": med([r["competence_heldout"] for r in rs]), "import_final": med([r["import_share_final"] for r in rs])}
        summ["edges"][spec.name] = e
    X.receipt["summary"] = summ; X.receipt["battery"] = battery
    out = X.close(rows, meas_extra={"battery": battery})
    print(json.dumps({"summary": summ, "battery": battery, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
