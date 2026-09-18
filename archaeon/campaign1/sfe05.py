"""SFE-05 -- H4 ADAPTIVE CHALLENGES x TRANSFER through the live engine (campaign 1).

    python -m archaeon.campaign1.sfe05 [--seeds 1 2 3] [--N 200 --G 80 --E 16] [--dry-run]

2x2: challenges FIXED (W1 delay 4 every generation) vs ADAPTIVE (a sealed internal policy:
delay starts at 1 and steps up the ladder 1,2,4,8,16 when the population's mean training
reward >= 0.40, down when < 0.10, floor 1) x TRANSFER OFF (random generation 0) vs ON
(generation 0 = the v01 solver elites -- register last-value organisms from W0/W1 -- padded
with randoms). EVALUATION IS INDEPENDENT AND FIXED: a held-out battery over delays {1, 4, 16},
24 episodes each, family "eval", identical for every cell; primary = mean over the three
delays (and per delay). Common random numbers across cells. The adaptive schedule per
generation is recorded (a landscape). Engine: one world; transfer seed set + schedules as
artifacts; experiment + observation per cell x seed.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import generate as G                      # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH              # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from         # noqa: E402

from archaeon import workspace as _ws                          # noqa: E402
from archaeon.wse.economics import REGIMES                     # noqa: E402
from archaeon.wse import evolve as EV                          # noqa: E402
from archaeon.wse.evolve import evaluate, run_cell             # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for        # noqa: E402
from archaeon.campaign1.sfe01 import FOUNDRY_C1, CAMPAIGN_SEED, engine_client, sha   # noqa: E402
from archaeon.campaign1.ssf_seeds import v01_solver_pop        # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SFE-05"
LADDER = [0, 1, 2, 4, 8]          # D-012: difficulty knob = DISTRACTOR count Kd (delay saturated for the transfer set)
FIXED_DELAY = 4                    # (name kept; the value is the fixed Kd)
EVAL_DELAYS = [0, 4, 8]            # (name kept; eval Kd battery)
CELLS = [("fixed", "off"), ("fixed", "on"), ("adaptive", "off"), ("adaptive", "on")]
MASK62 = (1 << 62) - 1


def spec_for(kd: int) -> WorldSpec:
    """D-012: the W1-like stream cell with Kd distractor entities (delay set {4}) -- the
    transfer set's competence falls from 1.0 (Kd 0) toward chance as Kd grows."""
    return WorldSpec("A_Kd%d" % kd, K=1, D=1, Kd=kd, delays=(4,), topology="stream", op_mode="replace", value_bits=4)


def run_cell_job(job: dict) -> dict:
    chall, transfer, seed = job["challenge"], job["transfer"], job["seed"]
    N, G_, E = job["N"], job["G"], job["E"]
    init = None
    if transfer == "on":
        init = v01_solver_pop(N)
        fm = dict(FOUNDRY_C1); fm["seed"] = 555 + seed; fm["n"] = N - len(init)
        init = init + G.generate(fm)
    # generation-by-generation loop with an adaptive delay: run_cell is generation-atomic, so
    # the schedule is implemented by running ONE generation at a time and carrying the
    # population (the loop's RNG is re-derived per call from (campaign, world, regime, seed,
    # branch); we add the generation index to the branch label to keep streams distinct AND
    # identical across cells for the same generation index: common random numbers).
    schedule = []
    pop = init
    delay = LADDER[0] if chall == "adaptive" else FIXED_DELAY
    t0 = time.time()
    for g in range(G_):
        spec = spec_for(delay)
        res = run_cell(spec, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, G_=1, E=E, init_pop=pop,
                       branch="cmp1-sfe05-g%d" % g, rng_label="cmp1-sfe05-g%d" % g, foundry=FOUNDRY_C1)
        mean_r = res["trace"][-1]["mean_reward"]; best_r = res["trace"][-1]["best_reward"]
        schedule.append({"gen": g, "delay": delay, "mean_reward": mean_r, "best_reward": best_r})
        # children for the next generation = the loop's would-be next population: run_cell with
        # G_=1 returns only the scored generation, so rebuild children here with the same rule
        pop = _next_population(res, N, seed, g)
        if chall == "adaptive":
            i = LADDER.index(delay)
            if mean_r >= 0.40 and i < len(LADDER) - 1:
                delay = LADDER[i + 1]
            elif mean_r < 0.10 and i > 0:
                delay = LADDER[i - 1]
    elite = res["elite"]
    ev = {}
    for d in EVAL_DELAYS:
        ev[d] = evaluate(elite["manifest"], episodes_for(spec_for(d), CAMPAIGN_SEED, "eval", seed, 24), rng_seed=7)["reward"]
    return {"challenge": chall, "transfer": transfer, "seed": seed, "eval": ev, "eval_mean": sum(ev.values()) / len(ev),
            "final_delay": delay, "schedule": schedule, "elite_manifest": elite["manifest"], "persist": elite["manifest"]["persist"],
            "max_delay_reached": max(s["delay"] for s in schedule), "gens_at_max": sum(1 for s in schedule if s["delay"] == max(x["delay"] for x in schedule)),
            "wall_s": round(time.time() - t0, 1)}


def _next_population(res: dict, N: int, seed: int, g: int) -> List[dict]:
    """Elitism 4 + tournament-4 children, same as run_cell's inner rule, seeded per generation."""
    from proteus.foundry.lineage import descend
    scored = sorted(res["final_population"], key=lambda z: -z["fitness"])
    rng = SplitMix64(seed_from("cmp1.sfe05.next", CAMPAIGN_SEED, seed, g))
    recs = [G.organism_record(z["manifest"], None, 0) for z in scored]
    new = recs[:4]

    def tour():
        best = None
        for _ in range(4):
            i = rng.randbelow(len(scored))
            if best is None or scored[i]["fitness"] > scored[best]["fitness"]:
                best = i
        return recs[best]
    while len(new) < N:
        p, q = tour(), tour()
        child, _ = descend(p, rng.next_u64() & MASK62, mate=q if q is not p else None)
        new.append(child)
    return new


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=80)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run SFE-05")
    OUT.mkdir(parents=True, exist_ok=True)
    T = time.time()
    receipt: Dict = {"experiment": "SFE-05", "campaign_seed": CAMPAIGN_SEED, "workspace": ws, "runtime_hash": RUNTIME_HASH,
                     "engine_path": not a.dry_run, "timings": {}, "worlds": {}, "artifacts": {}, "errors": [],
                     "design": {"ladder": LADDER, "fixed_delay": FIXED_DELAY, "eval_delays": EVAL_DELAYS, "up_at": 0.40, "down_at": 0.10}}
    c = None
    if not a.dry_run:
        t0 = time.time(); c, _ = engine_client()
        sid = c.create_session("cmp1-sfe05")
        w = c.create_world(sid, "cmp1-sfe05-h4", sharing_policy="ISOLATED", seed_root=CAMPAIGN_SEED); c.start(w["world_id"]); wid = w["world_id"]
        receipt["worlds"]["h4"] = wid; receipt["session_id"] = sid
        receipt["hypothesis"] = c.hypothesis(wid, "Adaptive challenge delay and transfer of prior solvers reinforce each other on an independent "
                                                  "fixed evaluation battery (delays 1,4,16): the on/adaptive cell exceeds the sum of the two main effects.")
        tb = json.dumps({"transfer_seed_set": "v01 solver elites (W0 s1,s2; W1_d1 s1,s2; W1_d16 s1; W2_K2 s1; W3_K2 s1)",
                         "manifests": [o["manifest"] for o in v01_solver_pop(64)]}, sort_keys=True).encode()
        receipt["artifacts"]["transfer_set"] = c.artifact(wid, "cmp1.h4.transfer_set.v0", tb, {"info_kind": "artifact"}, expected_blob_hash=sha(tb))["artifact_id"]
        receipt["timings"]["startup_s"] = round(time.time() - t0, 2)
    jobs = [{"challenge": ch, "transfer": tr, "seed": s, "N": a.N, "G": a.G, "E": a.E} for ch, tr in CELLS for s in a.seeds]
    t0 = time.time()
    with mp.Pool(processes=min(a.procs, len(jobs))) as pool:
        rows = pool.map(run_cell_job, jobs)
    receipt["timings"]["cells_s"] = round(time.time() - t0, 1)
    if c is not None:
        t0 = time.time()
        for r in rows:
            try:
                sb = json.dumps({"cell": [r["challenge"], r["transfer"]], "seed": r["seed"], "schedule": r["schedule"]}, sort_keys=True).encode()
                aid = c.artifact(wid, "cmp1.h4.schedule.v0", sb, {"info_kind": "observation"}, expected_blob_hash=sha(sb))["artifact_id"]
                exp = c.experiment(wid, {"experiment": "SFE-05", "challenge": r["challenge"], "transfer": r["transfer"], "seed": r["seed"],
                                         "N": a.N, "G": a.G, "E": a.E, "design": receipt["design"], "runtime_hash": RUNTIME_HASH})
                obs = c.observation(wid, exp["exp_id"], {"eval": r["eval"], "eval_mean": r["eval_mean"], "max_delay_reached": r["max_delay_reached"]},
                                    "SURVIVED" if r["eval_mean"] >= 0.3 else "FALSIFIED")
                r["engine"] = {"exp_id": exp["exp_id"], "obs_id": obs, "schedule_artifact": aid}
            except Exception as e:                                   # noqa: BLE001
                receipt["errors"].append({"step": "record", "cell": [r["challenge"], r["transfer"]], "seed": r["seed"], "error": repr(e)})
        receipt["timings"]["records_s"] = round(time.time() - t0, 2)
        t0 = time.time()
        try:
            c.terminate(wid); receipt["teardown"] = {"h4": c.get_world(wid).get("state")}
        except Exception as e:                                       # noqa: BLE001
            receipt["teardown"] = {"h4": "ERROR " + repr(e)}
        receipt["timings"]["teardown_s"] = round(time.time() - t0, 2)
    m = {}
    for ch, tr in CELLS:
        v = [r["eval_mean"] for r in rows if r["challenge"] == ch and r["transfer"] == tr]
        m["%s/%s" % (ch, tr)] = sum(v) / len(v)
    eff = {"means": m, "adaptive_main": (m["adaptive/off"] + m["adaptive/on"]) / 2 - (m["fixed/off"] + m["fixed/on"]) / 2,
           "transfer_main": (m["fixed/on"] + m["adaptive/on"]) / 2 - (m["fixed/off"] + m["adaptive/off"]) / 2,
           "interaction": m["adaptive/on"] - m["adaptive/off"] - m["fixed/on"] + m["fixed/off"],
           "per_delay": {"%s/%s" % (ch, tr): {d: sum(r["eval"][d] for r in rows if r["challenge"] == ch and r["transfer"] == tr) / len(a.seeds) for d in EVAL_DELAYS} for ch, tr in CELLS},
           "max_delay_reached": {"%s/%s" % (ch, tr): [r["max_delay_reached"] for r in rows if r["challenge"] == ch and r["transfer"] == tr] for ch, tr in CELLS}}
    receipt["effects"] = eff
    receipt["timings"]["total_s"] = round(time.time() - T, 1)
    (OUT / "rows.json").write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    (OUT / "RECEIPT.json").write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({"effects": eff, "timings": receipt["timings"], "errors": receipt["errors"], "teardown": receipt.get("teardown")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
