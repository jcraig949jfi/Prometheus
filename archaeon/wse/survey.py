"""The cheap survey (DESIGN_v0.1 s7): cells x regimes x seeds, controls first, records per
directive XX, classification predicates of s9 applied mechanically.

    python -m archaeon.wse.survey --campaign wse-survey-v01 --seed 20260916 [--procs 26]
                                  [--N 200 --G 100 --E 24] [--controls-only] [--quick]
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
from proteus.foundry.prng import seed_from                     # noqa: E402

from archaeon import workspace as _ws                          # noqa: E402
from archaeon.wse import controls as C                         # noqa: E402
from archaeon.wse import interventions as I                    # noqa: E402
from archaeon.wse.economics import REGIMES, Regime             # noqa: E402
from archaeon.wse.evolve import FOUNDRY, MASK62, evaluate, run_cell   # noqa: E402
from archaeon.wse.worlds import GRAMMAR_VERSION, WorldSpec, episodes_for, erase_ceiling, with_knobs   # noqa: E402

LEDGERS = Path(__file__).resolve().parent / "ledgers"

# ------------------------------------------------------------------ the matrix (s7)
CELLS: List[WorldSpec] = [
    WorldSpec("W0"),
    WorldSpec("W1_d1", delay=1),
    WorldSpec("W1_d4", delay=4),
    WorldSpec("W1_d16", delay=16),
    WorldSpec("W2_K2", K=2),
    WorldSpec("W2_K4", K=4),
    WorldSpec("W2_K8", K=8),
    WorldSpec("W3_K2", K=2, ask_mode="one"),
    WorldSpec("W3_K4", K=4, ask_mode="one"),
    WorldSpec("W3_K8", K=8, ask_mode="one"),
    WorldSpec("W4_K2_D4_int", K=2, D=4, interleave="random", ask_timing="interleaved"),
    WorldSpec("W5_K4_D4", K=4, D=4, interleave="random"),
    WorldSpec("W6_f1_n8", K=1, ask_kind="ASKX", fanout=1, expensive=8),
    WorldSpec("W6_f4_n8", K=1, ask_kind="ASKX", fanout=4, expensive=8),
    WorldSpec("W7_K2", K=2, ask_kind="ASK2"),
    WorldSpec("W8_K2_D3", K=2, D=3, ask_kind="ASKO"),
    WorldSpec("W9_K2", K=2, D=2, op_mode="per_stream"),
    WorldSpec("W10_dag6", K=3, topology="dag", n_defs=3),
]
CELL_REGIMES: Dict[str, List[str]] = {c.name: ["E0", "E1"] for c in CELLS}
for nm in ("W4_K2_D4_int", "W6_f1_n8", "W6_f4_n8"):
    CELL_REGIMES[nm] = ["E0", "E1", "E2", "E3"]
SEEDS = [1, 2, 3]
HELDOUT_E = 48
CAPACITY_KS = [1, 2, 4, 8, 16]
FANOUTS = [1, 2, 4, 8]
NO_ADAPT_MARGIN = 0.10


def _cell(name: str) -> WorldSpec:
    for c in CELLS:
        if c.name == name:
            return c
    raise KeyError(name)


# ------------------------------------------------------------------ controls (s5)
def run_controls(campaign_seed: int, N: int = 200, E: int = 24, cells: Optional[List[WorldSpec]] = None) -> dict:
    cells = cells or CELLS
    out = {"campaign_seed": campaign_seed, "cells": {}, "cheat": {}, "verdict": "PASS", "failures": []}
    fm = dict(FOUNDRY); fm["seed"] = seed_from("wse.neg", campaign_seed) & MASK62; fm["n"] = N
    neg_pop = G.generate(fm)
    for spec in cells:
        eps = episodes_for(spec, campaign_seed, "controls", 0, E)
        rewards = [evaluate(o["manifest"], eps, rng_seed=1)["reward"] for o in neg_pop]
        row = {
            "world_id": spec.world_id(),
            "n_ticks_mean": sum(len(e.ticks) for e in eps) / len(eps),
            "n_asks_mean": sum(e.n_asks() for e in eps) / len(eps),
            "NEG_mean": sum(rewards) / len(rewards),
            "NEG_max": max(rewards),
            "NEG_p95": sorted(rewards)[int(0.95 * (len(rewards) - 1))],
        }
        for nm, m in C.NULLS.items():
            row["NULL_" + nm] = evaluate(m, eps, rng_seed=1)["reward"]
            if row["NULL_" + nm] >= 0.5:
                out["failures"].append(f"{spec.name}: NULL {nm} scores {row['NULL_' + nm]:.3f} (leak)")
        wkey = spec.name.split("_")[0]
        if wkey in C.POSITIVE:
            pr = evaluate(C.POSITIVE[wkey], eps, rng_seed=1)
            row["POS"] = pr["reward"]
            row["POS_ops"] = pr["ops_per_episode"]
            if pr["reward"] < 1.0:
                out["failures"].append(f"{spec.name}: POS scores {pr['reward']:.3f} < 1.0 (world misposed or control wrong)")
        out["cells"][spec.name] = row
    # cheat battery: the interventions must see the mechanism each POS was written with
    for label, m, spec in (("POS_REGS_on_W1_d4", C.POS_REGS, _cell("W1_d4")),
                           ("POS_TABLE_on_W2_K4", C.POS_TABLE, _cell("W2_K4"))):
        eps = episodes_for(spec, campaign_seed, "cheat", 0, E)
        base = evaluate(m, eps, rng_seed=2)["reward"]
        vec = {nm: round(base - evaluate(m, eps, intervention=nm, rng_seed=2)["reward"], 4) for nm in I.NAMES}
        out["cheat"][label] = {"base": base, "drop": vec, "erase_ceiling": round(erase_ceiling(eps), 4)}
    regs = out["cheat"]["POS_REGS_on_W1_d4"]
    table = out["cheat"]["POS_TABLE_on_W2_K4"]
    # The battery must reach >= 80 % of the attainable ceiling on the mechanism each POS was
    # written with, and < 0.05 on the store it does not use (DESIGN v0.1.1 annotation).
    if not (regs["drop"]["ERASE_REGS"] >= 0.8 * regs["erase_ceiling"] and regs["drop"]["ERASE_TAPE"] < 0.05):
        out["failures"].append("cheat: battery does not see the register mechanism of POS_REGS")
    if not (table["drop"]["ERASE_TAPE"] >= 0.8 * table["erase_ceiling"] and table["drop"]["SCRAMBLE_LOC"] >= 0.8 * table["erase_ceiling"]
            and table["drop"]["ERASE_REGS"] < 0.05):
        out["failures"].append("cheat: battery does not see the tape-table mechanism of POS_TABLE")
    if out["failures"]:
        out["verdict"] = "FAIL"
    return out


# ------------------------------------------------------------------ one job
def run_job(job: dict) -> dict:
    spec: WorldSpec = job["spec"]
    regime: Regime = job["regime"]
    cs, seed = job["campaign_seed"], job["seed"]
    t0 = time.time()
    res = run_cell(spec, regime, cs, seed, N=job["N"], G_=job["G"], E=job["E"],
                   init_pop=job.get("init_pop"), branch=job.get("branch", "B1_naive"), rng_label=job.get("branch", "B1_naive"))
    elite = res["elite"]
    m = elite["manifest"]
    # held-out families
    ho = evaluate(m, episodes_for(spec, cs, "heldout", seed, HELDOUT_E), rng_seed=7)
    hoK = hoD = None
    if spec.topology == "streams" and spec.ask_kind != "ASKO":
        if spec.K < 16:
            hoK = evaluate(m, episodes_for(with_knobs(spec, K=min(16, 2 * spec.K)), cs, "heldoutK", seed, HELDOUT_E), rng_seed=7)["reward"]
        if spec.D < 16 and spec.expensive == 0:
            hoD = evaluate(m, episodes_for(with_knobs(spec, D=min(16, 2 * spec.D)), cs, "heldoutD", seed, HELDOUT_E), rng_seed=7)["reward"]
    # interventions on the held-out intervention family
    ieps = episodes_for(spec, cs, "intervention", seed, HELDOUT_E)
    ibase = evaluate(m, ieps, rng_seed=9)["reward"]
    ivec = {nm: round(ibase - evaluate(m, ieps, intervention=nm, rng_seed=9)["reward"], 4) for nm in I.NAMES}
    iceil = round(erase_ceiling(ieps), 4)
    # capacity curve over K (cheap), fanout curve for W6
    capacity = None
    if spec.topology == "streams" and spec.ask_kind in ("ASK", "ASKX", "ASK2") and spec.K <= 8:
        capacity = {}
        for k in CAPACITY_KS:
            if spec.ask_kind == "ASK2" and k < 2:
                continue
            capacity[k] = round(evaluate(m, episodes_for(with_knobs(spec, K=k), cs, "capacity", seed, 24), rng_seed=11)["reward"], 4)
    fan = None
    if spec.ask_kind == "ASKX":
        fan = {}
        for f in FANOUTS:
            ev = evaluate(m, episodes_for(with_knobs(spec, fanout=f), cs, "fanout", seed, 24), rng_seed=13)
            fan[f] = {"reward": round(ev["reward"], 4), "ops_per_episode": round(ev["ops_per_episode"], 2)}
    neg_floor = job.get("neg_floor")
    result = {
        "reward_train_last": res["elite_eval"]["reward"],
        "fitness_train_last": res["elite_fitness"],
        "reward_heldout": ho["reward"],
        "reward_heldout_K2x": hoK,
        "reward_heldout_D2x": hoD,
        "answered_share_heldout": ho["answered_share"],
        "ops_per_episode": ho["ops_per_episode"],
        "persistent_words": ho["meter"].get("persistent_state_words"),
        "meter_heldout": ho["meter"],
        "persist": ho["persist"], "tick_budget": ho["tick_budget"], "tape_words": ho["tape_words"],
        "n_regs": ho["n_regs"], "code_writable": ho["code_writable"],
        "yield_share": ho["yield_share"], "tape_occupancy_max": ho["tape_occupancy_max"],
        "tape_writes_per_episode": ho["tape_writes_per_episode"],
        "intervention_base": ibase, "intervention_drop": ivec, "erase_ceiling": iceil,
        "capacity_curve_K": capacity, "fanout_curve": fan,
        "wall_s": round(time.time() - t0, 1),
    }
    interp = classify(spec, result, neg_floor)
    row = {
        "schema": "wse.experiment_record.v0.1",
        "campaign": job["campaign"],
        "world": {"world_id": spec.world_id(), "name": spec.name, "knobs": spec.knobs(),
                  "grammar": GRAMMAR_VERSION, "seed": seed, "campaign_seed": cs},
        "economics": regime.as_dict(),
        "organism": {"organism_id": elite["organism_id"], "lineage_id": elite["lineage_id"],
                     "generation": elite["generation"], "branch": res["branch"],
                     "ancestry_depth": len(res["ancestry"]),
                     "ancestry_operators": _op_hist(res["ancestry"]),
                     "manifest": m, "runtime_hash": RUNTIME_HASH, "grammar_hash": GRAMMAR_HASH},
        "hypothesis": {"pressure": spec.name.split("_")[0],
                       "competing": ["no adaptation", "trivial recurrence", "recomputation",
                                     "specialized memory", "structured"]},
        "experiment": {"N": job["N"], "G": job["G"], "E": job["E"], "train_family": "train",
                       "heldout_families": ["heldout", "heldoutK", "heldoutD", "intervention", "capacity", "fanout"],
                       "interventions": I.NAMES, "neg_floor": neg_floor},
        "result": result,
        "interpretation": interp,
        "trace": res["trace"],
        "final_elites": [e["organism_id"] for e in res["final_elites"]],
        "final_elite_manifests": [e["manifest"] for e in res["final_elites"]],
    }
    return row


def _op_hist(chain: list) -> dict:
    h: Dict[str, int] = {}
    for c in chain:
        for o in c["operators"]:
            h[o] = h.get(o, 0) + 1
    return dict(sorted(h.items()))


# ------------------------------------------------------------------ classification (s9)
def classify(spec: WorldSpec, r: dict, neg_floor: Optional[float]) -> dict:
    R = r["reward_heldout"]
    F = neg_floor if neg_floor is not None else 0.0
    d = r["intervention_drop"]
    out = {"R": R, "F": F, "class": "UNRESOLVED", "ruled_out": [], "remaining": [], "notes": []}
    if R - F < NO_ADAPT_MARGIN:
        out["class"] = "NO_ADAPTATION"
        out["notes"].append("held-out reward within %.2f of the generation-0 floor" % NO_ADAPT_MARGIN)
        return out
    hoK = r.get("reward_heldout_K2x")
    k_drop = (R - hoK) if hoK is not None else None
    if r["persist"] == "regs" and d["ERASE_TAPE"] < 0.05 and d["ERASE_REGS"] >= 0.10:
        out["class"] = "TRIVIAL_RECURRENCE"
    elif spec.ask_kind == "ASKX" and r.get("fanout_curve"):
        fc = r["fanout_curve"]
        slope = (fc[8]["ops_per_episode"] - fc[1]["ops_per_episode"]) / 7.0
        recompute_cost = 2.0 * max(1, spec.expensive)
        out["notes"].append("ops slope per extra consumer %.2f vs recompute cost %.1f" % (slope, recompute_cost))
        if slope >= 0.5 * recompute_cost and d["ERASE_ALL"] < 0.05:
            out["class"] = "RECOMPUTATION"
        elif d["ERASE_TAPE"] >= 0.10 or d["ERASE_REGS"] >= 0.10:
            out["class"] = "SPECIALIZED_MEMORY" if d["SCRAMBLE_LOC"] >= 0.10 else "STRUCTURED"
    if out["class"] == "UNRESOLVED":
        if d["ERASE_TAPE"] >= 0.10 and d["SCRAMBLE_LOC"] >= 0.10 and k_drop is not None and k_drop >= 0.20:
            out["class"] = "SPECIALIZED_MEMORY"
        elif d["ERASE_TAPE"] >= 0.10 and d["SCRAMBLE_LOC"] < 0.05:
            out["class"] = "STRUCTURED"
        elif d["SCRAMBLE_VAL"] >= 0.10 and d["SCRAMBLE_LOC"] < 0.05 and k_drop is not None and k_drop <= 0.10:
            out["class"] = "STRUCTURED"
    # what the vector rules out regardless of class
    if d["ERASE_ALL"] < 0.05:
        out["ruled_out"].append("dependence on any persistent state (ERASE_ALL costs < 0.05)")
    if d["ERASE_REGS"] < 0.05:
        out["ruled_out"].append("register-carried state")
    if d["ERASE_TAPE"] < 0.05:
        out["ruled_out"].append("tape-carried state")
    if d["RESET_IP"] < 0.05:
        out["ruled_out"].append("instruction-pointer resumption (YIELD) as load-bearing")
    if d["SCRAMBLE_LOC"] < 0.05 <= d["ERASE_TAPE"]:
        out["remaining"].append("tape content survives relocation: content- not position-keyed")
    if d["SCRAMBLE_LOC"] >= 0.10:
        out["remaining"].append("position-keyed tape use")
    if d["TRANSPLANT"] < 0.05 <= d["ERASE_ALL"]:
        out["notes"].append("state from another episode is as good as its own: state is episode-independent (suspicious; inspect)")
    return out


# ------------------------------------------------------------------ driver
def _jobs(campaign: str, cs: int, N: int, G_: int, E: int, controls: dict, only: Optional[List[str]]) -> List[dict]:
    jobs = []
    for spec in CELLS:
        if only and spec.name not in only:
            continue
        for rn in CELL_REGIMES[spec.name]:
            for seed in SEEDS:
                jobs.append({"campaign": campaign, "spec": spec, "regime": REGIMES[rn], "campaign_seed": cs,
                             "seed": seed, "N": N, "G": G_, "E": E,
                             "neg_floor": controls["cells"][spec.name]["NEG_mean"]})
    return jobs


def _write_json(path: Path, obj) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(obj, sort_keys=True, indent=1, default=str)
    path.write_text(data, encoding="utf-8", newline="\n")
    return hashlib.sha256(data.encode()).hexdigest()


def summarize(rows: List[dict]) -> str:
    lines = ["cell            regime seed  R_train R_held  R_K2x  R_D2x  floor persist tape ops/ep  ERASE_ALL ERASE_REGS ERASE_TAPE SCR_LOC SCR_VAL RESET_IP class",
             "-" * 150]
    for r in sorted(rows, key=lambda z: (z["world"]["name"], z["economics"]["name"], z["world"]["seed"])):
        res, d = r["result"], r["result"]["intervention_drop"]
        f = lambda x: "  -  " if x is None else "%.3f" % x
        lines.append("%-15s %-6s %-4d %s   %s   %s  %s  %.3f %-7s %-4d %-7.1f %s     %s      %s      %s   %s   %s   %s" % (
            r["world"]["name"], r["economics"]["name"], r["world"]["seed"], f(res["reward_train_last"]), f(res["reward_heldout"]),
            f(res["reward_heldout_K2x"]), f(res["reward_heldout_D2x"]), r["interpretation"]["F"], res["persist"], res["tape_words"],
            res["ops_per_episode"], f(d["ERASE_ALL"]), f(d["ERASE_REGS"]), f(d["ERASE_TAPE"]), f(d["SCRAMBLE_LOC"]), f(d["SCRAMBLE_VAL"]),
            f(d["RESET_IP"]), r["interpretation"]["class"]))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", default="wse-survey-v01")
    ap.add_argument("--seed", type=int, default=20260916)
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=100)
    ap.add_argument("--E", type=int, default=24)
    ap.add_argument("--procs", type=int, default=max(1, min(26, (os.cpu_count() or 2) - 2)))
    ap.add_argument("--controls-only", action="store_true")
    ap.add_argument("--only", nargs="*", default=None, help="cell names")
    ap.add_argument("--quick", action="store_true", help="N=40 G=8 E=8, for smoke")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run the WSE survey")
    if a.quick:
        a.N, a.G, a.E = 40, 8, 8
    out_dir = LEDGERS / a.campaign
    t0 = time.time()
    controls = run_controls(a.seed, N=a.N, E=a.E)
    controls["workspace"] = ws
    controls["runtime_hash"] = RUNTIME_HASH
    controls["grammar_hash"] = GRAMMAR_HASH
    _write_json(out_dir / "CONTROLS.json", controls)
    print("controls:", controls["verdict"], "(%.0fs)" % (time.time() - t0))
    for nm, row in controls["cells"].items():
        print("  %-15s ticks %5.1f asks %4.1f NEG mean %.3f max %.3f | CONST0 %.3f ECHO %.3f | POS %s" % (
            nm, row["n_ticks_mean"], row["n_asks_mean"], row["NEG_mean"], row["NEG_max"], row["NULL_CONST0"],
            row["NULL_ECHO_LAST"], ("%.3f" % row["POS"]) if "POS" in row else "-"))
    for lbl, c in controls["cheat"].items():
        print("  cheat", lbl, "base %.3f ceiling %.3f" % (c["base"], c["erase_ceiling"]), c["drop"])
    for fmsg in controls["failures"]:
        print("  FAIL:", fmsg)
    if controls["verdict"] != "PASS":
        print("survey NOT run: controls failed (DESIGN s10)")
        return 2
    if a.controls_only:
        return 0
    jobs = _jobs(a.campaign, a.seed, a.N, a.G, a.E, controls, a.only)
    print("jobs:", len(jobs), "procs:", a.procs)
    rows: List[dict] = []
    rows_dir = out_dir / "rows"
    with mp.Pool(processes=a.procs) as pool:
        for row in pool.imap_unordered(run_job, jobs):
            rows.append(row)
            nm = "%s__%s__s%d.json" % (row["world"]["name"], row["economics"]["name"], row["world"]["seed"])
            _write_json(rows_dir / nm, row)
            r = row["result"]
            print("%-15s %-3s s%d  held %.3f floor %.3f persist %-5s %s  (%.0fs, %d done)" % (
                row["world"]["name"], row["economics"]["name"], row["world"]["seed"], r["reward_heldout"],
                row["interpretation"]["F"], r["persist"], row["interpretation"]["class"], r["wall_s"], len(rows)), flush=True)
    summary = summarize(rows)
    (out_dir / "SUMMARY.txt").write_text(summary + "\n", encoding="utf-8", newline="\n")
    digest = hashlib.sha256("\n".join(sorted(json.dumps(r["result"], sort_keys=True) for r in rows)).encode()).hexdigest()
    _write_json(out_dir / "RUN.json", {"campaign": a.campaign, "campaign_seed": a.seed, "N": a.N, "G": a.G, "E": a.E,
                                       "n_rows": len(rows), "results_digest": digest, "wall_s": round(time.time() - t0, 1),
                                       "workspace": ws, "runtime_hash": RUNTIME_HASH, "grammar_hash": GRAMMAR_HASH,
                                       "grammar_version": GRAMMAR_VERSION})
    print(summary)
    print("results_digest", digest, "wall %.0fs" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
