"""SSF -- Selective State Formation, cycle runner (DESIGN_v0.2).

    python -m archaeon.wse.ssf --campaign ssf-c1 --seed 20260917 [--procs 24] [--boundary-only]
                               [--N 256 --G 120 --E 16] [--only A_remember ...] [--quick]

Order: boundary map + nulls (s3) -> only selectivity-pays (cell, regime) pairs evolve ->
records with learning curves, transfer, curves over Kd/delay/K, interventions -> summary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from proteus.foundry import generate as G                      # noqa: E402
from proteus.foundry.grammar import GRAMMAR_HASH               # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH              # noqa: E402

from archaeon import workspace as _ws                          # noqa: E402
from archaeon.wse import controls as C                         # noqa: E402
from archaeon.wse import interventions as I                    # noqa: E402
from archaeon.wse.economics import RAMP_FOOTHOLD, REGIMES, Regime      # noqa: E402
RAMP_FOOTHOLD_V03 = 0.20          # DESIGN_v0.3 W1: m_g = clip((mean - chance) / 0.20, 0, 1)
from archaeon.wse.evolve import FOUNDRY, evaluate, run_cell    # noqa: E402
from archaeon.wse.readout import results_digest, strip_timing  # noqa: E402
from archaeon.wse.worlds import (GRAMMAR_VERSION, WorldSpec, episodes_for, erase_ceiling,   # noqa: E402
                                 null_scores, with_knobs)

LEDGERS = Path(__file__).resolve().parent / "ledgers"
V01_ROWS = LEDGERS / "wse-survey-v01" / "rows"

FOUNDRY_V02 = dict(FOUNDRY, genome_instr_range=[1, 16], tape_words_choices=[16, 32, 64, 128, 256],
                   tick_budget_choices=[16, 64, 256])

_S = dict(op_mode="replace", topology="stream", value_bits=4)
CELLS: List[WorldSpec] = [
    WorldSpec("A_remember", K=1, D=1, Kd=8, delays=(4, 16, 64), **_S),
    WorldSpec("B_update", K=1, D=4, Kd=4, delays=(4, 16), **_S),
    WorldSpec("C_forget", K=1, D=2, Kd=4, retire_rate=0.5, delays=(4, 16), op_mode="add", topology="stream",
              value_bits=4, recycle=True),      # v0.3: RETIRE recycles the tag; ASK expects the NEW fold only
    WorldSpec("D_bind2", K=2, D=2, Kd=8, delays=(4, 16), **_S),
    WorldSpec("E_bind4", K=4, D=2, Kd=8, delays=(4, 16), **_S),
    WorldSpec("F_compose", K=2, D=2, Kd=4, delays=(4, 16), ask_kind="ASK2", op_mode="add", topology="stream", value_bits=4),
    WorldSpec("G_interfere", K=2, D=2, Kd=8, delays=(4, 16), interfere=True, **_S),
    WorldSpec("H_timescale", K=2, D=1, Kd=8, delays=(4, 64), **_S),
]
CELL_REGIMES: Dict[str, List[str]] = {c.name: ["S0", "S1"] for c in CELLS}
for nm in ("A_remember", "D_bind2"):
    CELL_REGIMES[nm] = ["S0", "S1", "S2", "S3"]
TRANSFER_CELLS = ("A_remember", "B_update", "D_bind2")
SEEDS = [1, 2, 3]
HELDOUT_E = 48
CURVE_E = 24
BETA_SWEEP = [0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
ALPHA_SWEEP = [0.0, 0.02, 0.1]
SELECTIVITY_MARGIN = 0.10
V01_SOLVERS = ["W0__E0__s1", "W0__E0__s2", "W1_d1__E0__s1", "W1_d1__E0__s2", "W1_d16__E0__s1", "W2_K2__E0__s1", "W3_K2__E0__s1"]


def _cell(name: str) -> WorldSpec:
    for c in CELLS:
        if c.name == name:
            return c
    raise KeyError(name)


# ------------------------------------------------------------------ boundary map (s3)
def boundary_map(campaign_seed: int, cells: List[WorldSpec], E: int = 32) -> dict:
    out = {"campaign_seed": campaign_seed, "cells": {}, "eligible": {}, "void": {}, "notes": []}
    for spec in cells:
        eps = episodes_for(spec, campaign_seed, "controls", 0, E)
        nulls = null_scores(eps)
        chance = 1.0 / (1 << spec.value_bits)
        row = {"world_id": spec.world_id(), "n_ticks_mean": sum(len(e.ticks) for e in eps) / E,
               "n_asks_mean": sum(e.n_asks() for e in eps) / E, "nulls": {k: round(v, 4) for k, v in nulls.items()},
               "chance": chance, "organisms": {}}
        for nm, m in (C.BOUNDARY_ADD if spec.op_mode == "add" else C.BOUNDARY).items():
            ev = evaluate(m, eps, rng_seed=1)
            row["organisms"][nm] = {"reward": ev["reward"], "ops_per_episode": round(ev["ops_per_episode"], 1),
                                    "persistent_words": ev["meter"]["persistent_state_words"],
                                    "reads_writes": round((ev["meter"]["in_reads"] + ev["meter"]["out_writes"]) / E, 1),
                                    "meter": {k: ev["meter"][k] for k in ("ops", "in_reads", "out_writes", "persistent_state_words")}}
        # fitness under the regimes and the sweep (multiplier 1: the map is at full cost)
        fit = {}
        for rn in ("S0", "S1", "S2", "S3"):
            fit[rn] = {nm: round(REGIMES[rn].fitness(o["reward"], o["meter"], E), 4) for nm, o in row["organisms"].items()}
        sweep = {}
        for a in ALPHA_SWEEP:
            for b in BETA_SWEEP:
                rg = Regime("sweep", alpha=a, beta=b, gamma=0.02)
                f = {nm: rg.fitness(o["reward"], o["meter"], E) for nm, o in row["organisms"].items()}
                win = max(f, key=f.get)
                sweep["a%g_b%g" % (a, b)] = {"winner": win, "SELECTIVE_margin": round(f["SELECTIVE"] - max(f["FULL_LOG"], f["TRIVIAL"]), 4)}
        row["fitness"] = fit
        row["sweep"] = sweep
        pays = [rn for rn in ("S0", "S1", "S2", "S3")
                if fit[rn]["SELECTIVE"] - max(fit[rn]["FULL_LOG"], fit[rn]["TRIVIAL"]) >= SELECTIVITY_MARGIN]
        row["selectivity_pays"] = pays
        # void rule (annotation v0.2.1): STATELESS nulls only -- CONST0 (except retire cells,
        # where it is the retire floor) and ECHO_PREV_0 -- must sit below chance + 0.10.
        void = []
        if spec.retire_rate == 0 and nulls["CONST0"] >= chance + 0.10:
            void.append("CONST0 %.3f" % nulls["CONST0"])
        if nulls["ECHO_PREV_0"] >= chance + 0.10:
            void.append("ECHO_PREV_0 %.3f" % nulls["ECHO_PREV_0"])
        if row["organisms"]["SELECTIVE"]["reward"] < 0.9 and row["organisms"]["FULL_LOG"]["reward"] < 0.9:
            void.append("no positive control reaches 0.9 (SELECTIVE %.3f FULL_LOG %.3f)" % (
                row["organisms"]["SELECTIVE"]["reward"], row["organisms"]["FULL_LOG"]["reward"]))
        row["void"] = void
        out["cells"][spec.name] = row
        out["eligible"][spec.name] = [] if void else [rn for rn in CELL_REGIMES[spec.name] if rn in pays]
        if void:
            out["void"][spec.name] = void
    return out


def _v01_solver_pop(N: int) -> List[dict]:
    pop = []
    for nm in V01_SOLVERS:
        p = V01_ROWS / (nm + ".json")
        if not p.exists():
            continue
        r = json.loads(p.read_text(encoding="utf-8"))
        for m in r["final_elite_manifests"]:
            rec = G.organism_record(m, r["organism"]["lineage_id"], 0)
            rec["transfer_source"] = nm
            pop.append(rec)
    return pop[:N]


# ------------------------------------------------------------------ one job
def run_job(job: dict) -> dict:
    spec: WorldSpec = job["spec"]
    regime: Regime = job["regime"]
    cs, seed = job["campaign_seed"], job["seed"]
    branch = job.get("branch", "B1_naive")
    t0 = time.time()
    curve_eps = episodes_for(spec, cs, "curve", seed, CURVE_E)
    init_pop = None
    if branch == "B2_transfer":
        init_pop = _v01_solver_pop(job["N"])
        fm = dict(FOUNDRY_V02); fm["seed"] = 777 + seed; fm["n"] = job["N"] - len(init_pop)
        init_pop = init_pop + G.generate(fm)
    res = run_cell(spec, regime, cs, seed, N=job["N"], G_=job["G"], E=job["E"], init_pop=init_pop, branch=branch,
                   ramp=regime.name != "S0", ramp_foothold=RAMP_FOOTHOLD_V03, curve_every=10, curve_episodes=curve_eps,
                   foundry=FOUNDRY_V02, ramp_mode="mean", chance=1.0 / (1 << spec.value_bits))
    elite = res["elite"]
    m = elite["manifest"]
    ho_eps = episodes_for(spec, cs, "heldout", seed, HELDOUT_E)
    ho = evaluate(m, ho_eps, rng_seed=7)
    split = split_competence(m, ho_eps)
    hov = evaluate(m, episodes_for(with_knobs(spec, vocab="heldout"), cs, "heldout_vocab", seed, HELDOUT_E), rng_seed=7)
    changed = {
        "Kd_x2": evaluate(m, episodes_for(with_knobs(spec, Kd=2 * spec.Kd), cs, "changed", seed, HELDOUT_E), rng_seed=7)["reward"],
        "delay_x2": evaluate(m, episodes_for(with_knobs(spec, delays=tuple(2 * d for d in spec.delays)), cs, "changed", seed, HELDOUT_E), rng_seed=7)["reward"],
        "K_x2": evaluate(m, episodes_for(with_knobs(spec, K=2 * spec.K), cs, "changed", seed, HELDOUT_E), rng_seed=7)["reward"] if spec.ask_kind != "ASK2" or spec.K >= 2 else None,
    }
    ieps = episodes_for(spec, cs, "intervention", seed, HELDOUT_E)
    ibase = evaluate(m, ieps, rng_seed=9)["reward"]
    ivec = {nm: round(ibase - evaluate(m, ieps, intervention=nm, rng_seed=9)["reward"], 4) for nm in I.NAMES}
    curves = None
    if ho["reward"] >= 0.3:
        curves = {"Kd": {}, "delay": {}, "K": {}}
        for kd in (0, 4, 8, 16, 32):
            ev = evaluate(m, episodes_for(with_knobs(spec, Kd=kd), cs, "curveKd", seed, 24), rng_seed=11)
            curves["Kd"][kd] = {"reward": round(ev["reward"], 4), "ops": round(ev["ops_per_episode"], 1)}
        for d in (4, 16, 64, 128):
            ev = evaluate(m, episodes_for(with_knobs(spec, delays=(d,)), cs, "curveD", seed, 24), rng_seed=11)
            curves["delay"][d] = round(ev["reward"], 4)
        if spec.ask_kind != "ASK2":
            for k in (1, 2, 4, 8):
                ev = evaluate(m, episodes_for(with_knobs(spec, K=k), cs, "curveK", seed, 24), rng_seed=11)
                curves["K"][k] = round(ev["reward"], 4)
    lc = res["learning_curve"]
    slope = None
    if len(lc) >= 3:
        a, b = lc[-3], lc[-1]
        de = b["experience_episodes"] - a["experience_episodes"]
        slope = (b["competence"] - a["competence"]) / de * 1e4 if de else None      # competence per 10k episodes
    result = {
        "reward_train_last": res["elite_eval"]["reward"], "fitness_train_last": res["elite_fitness"],
        "competence_heldout": ho["reward"], "competence_heldout_vocab": hov["reward"],
        "competence_split_retired": split,
        "competence_changed": changed, "answered_share_heldout": ho["answered_share"],
        "experience_episodes": res["experience_episodes"], "experience_ticks": res["experience_ticks"],
        "persistent_words": ho["meter"]["persistent_state_words"], "peak_state": ho["tape_occupancy_max"] + ho["n_regs"],
        "reads_writes_per_episode": round((ho["meter"]["in_reads"] + ho["meter"]["out_writes"]) / HELDOUT_E, 2),
        "ops_per_episode": ho["ops_per_episode"], "meter_heldout": ho["meter"],
        "persist": ho["persist"], "tick_budget": ho["tick_budget"], "tape_words": ho["tape_words"], "n_regs": ho["n_regs"],
        "code_writable": ho["code_writable"], "yield_share": ho["yield_share"], "tape_occupancy_max": ho["tape_occupancy_max"],
        "intervention_base": ibase, "intervention_drop": ivec, "erase_ceiling": round(erase_ceiling(ieps), 4),
        "curves": curves, "learning_curve": lc, "learning_slope_per_10k": None if slope is None else round(slope, 5),
        "derived": {
            "competence_per_10k_episodes": round(ho["reward"] / max(1, res["experience_episodes"]) * 1e4, 5),
            "transfer_per_10k_episodes": round(hov["reward"] / max(1, res["experience_episodes"]) * 1e4, 5),
            "competence_per_persistent_word": round(ho["reward"] / max(1, ho["meter"]["persistent_state_words"]), 5),
            "competence_per_kop": round(ho["reward"] / max(1e-9, ho["ops_per_episode"] / 1000.0), 4),
        },
        "wall_s": round(time.time() - t0, 1),
    }
    interp = classify(spec, result, job.get("floor", 0.0))
    return {
        "schema": "wse.experiment_record.v0.2", "campaign": job["campaign"],
        "world": {"world_id": spec.world_id(), "name": spec.name, "knobs": spec.knobs(), "grammar": GRAMMAR_VERSION,
                  "seed": seed, "campaign_seed": cs},
        "economics": dict(regime.as_dict(), ramp=(regime.name != "S0"), ramp_foothold=RAMP_FOOTHOLD_V03, ramp_mode="mean"),
        "organism": {"organism_id": elite["organism_id"], "lineage_id": elite["lineage_id"], "generation": elite["generation"],
                     "branch": branch, "transfer_source": elite.get("transfer_source"), "ancestry_depth": len(res["ancestry"]),
                     "manifest": m, "runtime_hash": RUNTIME_HASH, "grammar_hash": GRAMMAR_HASH},
        "hypothesis": {"pressures": spec.name, "competing": ["no adaptation", "last value", "selective state", "history replay"]},
        "experiment": {"N": job["N"], "G": job["G"], "E": job["E"], "foundry": FOUNDRY_V02, "floor": job.get("floor"),
                       "families": ["train", "curve", "heldout", "heldout_vocab", "changed", "intervention", "curveKd", "curveD", "curveK"]},
        "result": result, "interpretation": interp, "trace": res["trace"],
        "final_elites": [e["organism_id"] for e in res["final_elites"]],
        "final_elite_manifests": [e["manifest"] for e in res["final_elites"]],
    }


def split_competence(m: dict, episodes) -> dict:
    """Competence on asks about RETIREd tags vs the rest (v0.3 C_forget)."""
    from proteus.foundry.prng import SplitMix64, seed_from
    from proteus.foundry.vm import Player
    p = Player(m)
    hit = {"retired": 0, "other": 0}
    tot = {"retired": 0, "other": 0}
    for ei, ep in enumerate(episodes):
        st = p.fresh_state()
        rng = SplitMix64(seed_from("wse.vmrng", 7, ei))
        ret = set(ep.meta.get("retired_asks", []))
        for ti, words in enumerate(ep.ticks):
            outs, _ = p.run_tick(st, [words], 1, rng)
            if ti in ep.expected:
                k = "retired" if ti in ret else "other"
                tot[k] += 1
                if outs[0] and outs[0][0] == ep.expected[ti]:
                    hit[k] += 1
    return {k: (round(hit[k] / tot[k], 4) if tot[k] else None) for k in tot} | {"n_retired": tot["retired"], "n_other": tot["other"]}


def classify(spec: WorldSpec, r: dict, floor: float) -> dict:
    R = r["competence_heldout"]
    d = r["intervention_drop"]
    out = {"R": R, "F": floor, "class": "UNRESOLVED", "notes": []}
    if R - floor < 0.10:
        out["class"] = "NO_ADAPTATION"
        return out
    kc = (r.get("curves") or {}).get("K") or {}
    kd = (r.get("curves") or {}).get("Kd") or {}
    if d["ERASE_REGS"] >= 0.10 and d["ERASE_TAPE"] < 0.05 and kc and kc.get(2, 1.0) <= 0.6 * max(1e-9, kc.get(1, 1.0)):
        out["class"] = "LAST_VALUE"
    elif R >= 0.5 and spec.Kd >= 8 and r["persistent_words"] <= 64 and r["competence_changed"]["Kd_x2"] >= 0.8 * R:
        out["class"] = "SELECTIVE_STATE"
    elif kd and r["persistent_words"] >= 256:
        ops0, ops32 = kd.get(0, {}).get("ops"), kd.get(32, {}).get("ops")
        if ops0 is not None and ops32 is not None and (ops32 - ops0) / 32.0 >= 2.0:
            out["class"] = "HISTORY_REPLAY"
    if d["ERASE_ALL"] < 0.05:
        out["notes"].append("no persistent state is load-bearing")
    if d["RESET_IP"] >= 0.10:
        out["notes"].append("instruction pointer carries reward (%.3f)" % d["RESET_IP"])
    return out


# ------------------------------------------------------------------ driver
def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, indent=1, default=str), encoding="utf-8", newline="\n")


def summarize(rows: List[dict]) -> str:
    lines = ["%-12s %-3s %-11s s  held  vocab Kdx2  dlyx2 Kx2   floor persist tape  ops/ep  ERASE_ALL ERASE_REGS ERASE_TAPE SCR_LOC RESET_IP slope   class" % ("cell", "reg", "branch"),
             "-" * 170]
    for r in sorted(rows, key=lambda z: (z["world"]["name"], z["economics"]["name"], z["organism"]["branch"], z["world"]["seed"])):
        res, d, ch = r["result"], r["result"]["intervention_drop"], r["result"]["competence_changed"]
        f = lambda x: " -   " if x is None else "%.3f" % x
        lines.append("%-12s %-3s %-11s %d  %s %s %s %s %s %.3f %-7s %-5d %-7.1f %s     %s      %s      %s   %s   %s %s" % (
            r["world"]["name"], r["economics"]["name"], r["organism"]["branch"], r["world"]["seed"],
            f(res["competence_heldout"]), f(res["competence_heldout_vocab"]), f(ch["Kd_x2"]), f(ch["delay_x2"]), f(ch["K_x2"]),
            r["interpretation"]["F"], res["persist"], res["tape_words"], res["ops_per_episode"],
            f(d["ERASE_ALL"]), f(d["ERASE_REGS"]), f(d["ERASE_TAPE"]), f(d["SCRAMBLE_LOC"]), f(d["RESET_IP"]),
            f(res["learning_slope_per_10k"]), r["interpretation"]["class"]))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", default="ssf-c2")
    ap.add_argument("--seed", type=int, default=20260917)
    ap.add_argument("--N", type=int, default=256)
    ap.add_argument("--G", type=int, default=120)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=max(1, min(24, (os.cpu_count() or 2) - 4)))
    ap.add_argument("--boundary-only", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--no-transfer", action="store_true")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--cycle3", action="store_true", help="DESIGN_v0.4 arms on A/B/D: naive S0 N=512 G=200; transfer S1p N=256 G=200")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run the SSF cycle")
    if a.quick:
        a.N, a.G, a.E = 40, 12, 8
    out_dir = LEDGERS / a.campaign
    t0 = time.time()
    cells = [c for c in CELLS if not a.only or c.name in a.only]
    bm = boundary_map(a.seed, cells)
    bm["workspace"] = ws
    bm["runtime_hash"] = RUNTIME_HASH
    _write_json(out_dir / "BOUNDARY_MAP.json", bm)
    print("boundary map (%.0fs)" % (time.time() - t0))
    for nm, row in bm["cells"].items():
        o = row["organisms"]
        print("  %-12s ticks %5.1f asks %3.1f | reward FULL %.3f SEL %.3f TRIV %.3f | ops %6.0f %6.0f %5.0f | pw %4d %4d %3d | pays %s | nulls c0 %.2f e0 %.2f e1 %.2f first %.2f%s" % (
            nm, row["n_ticks_mean"], row["n_asks_mean"], o["FULL_LOG"]["reward"], o["SELECTIVE"]["reward"], o["TRIVIAL"]["reward"],
            o["FULL_LOG"]["ops_per_episode"], o["SELECTIVE"]["ops_per_episode"], o["TRIVIAL"]["ops_per_episode"],
            o["FULL_LOG"]["persistent_words"], o["SELECTIVE"]["persistent_words"], o["TRIVIAL"]["persistent_words"],
            ",".join(row["selectivity_pays"]) or "-", row["nulls"]["CONST0"], row["nulls"]["ECHO_PREV_0"], row["nulls"]["ECHO_PREV_1"],
            row["nulls"]["ECHO_FIRST"], ("  VOID: " + "; ".join(row["void"])) if row["void"] else ""))
    if a.boundary_only:
        return 0
    # floors: generation-0 population reward per cell
    fm = dict(FOUNDRY_V02); fm["seed"] = 99; fm["n"] = 200
    neg = G.generate(fm)
    floors = {}
    for spec in cells:
        eps = episodes_for(spec, a.seed, "controls", 1, 16)
        rs = [evaluate(o["manifest"], eps, rng_seed=1)["reward"] for o in neg]
        floors[spec.name] = sum(rs) / len(rs)
    jobs = []
    if a.cycle3:
        for spec in cells:
            if spec.name not in TRANSFER_CELLS:
                continue
            for seed in SEEDS:
                base = {"campaign": a.campaign, "spec": spec, "campaign_seed": a.seed, "seed": seed, "E": a.E, "floor": floors[spec.name]}
                jobs.append(dict(base, regime=REGIMES["S0"], branch="B1_naive", N=512, G=200))
                jobs.append(dict(base, regime=REGIMES["S1p"], branch="B2_transfer", N=256, G=200))
        cells = []
    for spec in cells:
        for rn in bm["eligible"][spec.name]:
            for seed in SEEDS:
                base = {"campaign": a.campaign, "spec": spec, "regime": REGIMES[rn], "campaign_seed": a.seed, "seed": seed,
                        "N": a.N, "G": a.G, "E": a.E, "floor": floors[spec.name]}
                jobs.append(dict(base, branch="B1_naive"))
                if spec.name in TRANSFER_CELLS and not a.no_transfer and rn in ("S0", "S1"):
                    jobs.append(dict(base, branch="B2_transfer"))
    print("jobs:", len(jobs), "procs:", a.procs, "floors:", {k: round(v, 3) for k, v in floors.items()})
    rows: List[dict] = []
    with mp.Pool(processes=a.procs) as pool:
        for row in pool.imap_unordered(run_job, jobs):
            rows.append(row)
            nm = "%s__%s__%s__s%d.json" % (row["world"]["name"], row["economics"]["name"], row["organism"]["branch"], row["world"]["seed"])
            _write_json(out_dir / "rows" / nm, row)
            r = row["result"]
            print("%-12s %-3s %-11s s%d held %.3f vocab %.3f Kdx2 %.3f pw %4d ops %6.1f %s (%.0fs, %d done)" % (
                row["world"]["name"], row["economics"]["name"], row["organism"]["branch"], row["world"]["seed"], r["competence_heldout"],
                r["competence_heldout_vocab"], r["competence_changed"]["Kd_x2"], r["persistent_words"], r["ops_per_episode"],
                row["interpretation"]["class"], r["wall_s"], len(rows)), flush=True)
    summary = summarize(rows)
    (out_dir / "SUMMARY.txt").write_text(summary + "\n", encoding="utf-8", newline="\n")
    _write_json(out_dir / "RUN.json", {"campaign": a.campaign, "campaign_seed": a.seed, "N": a.N, "G": a.G, "E": a.E, "n_rows": len(rows),
                                       "results_digest": results_digest(rows), "wall_s": round(time.time() - t0, 1), "workspace": ws,
                                       "runtime_hash": RUNTIME_HASH, "grammar_hash": GRAMMAR_HASH, "grammar_version": GRAMMAR_VERSION,
                                       "floors": floors})
    print(summary)
    print("results_digest", results_digest(rows), "wall %.0fs" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
