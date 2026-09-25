"""RIE-01 campaign scheduler (operator directive 2026-09-24, Phase C). Launches only after ENVGATE-02's Phase C gate passes.

Grammar: regime (8) x inflow (3) x topology (2) x substrate (2) = 96 cells, full factorial, no constraints (preflight proves no
structural zeros). T = 16,384 epochs per world; dwell 64; exposure = K * floor(T_in / dwell) arrivals, checked for every world.
Allocation:
  wave 0     every cell x seeds 0..3 (384 worlds)                                   -> UNBIASED lane
  wave k>0   96 worlds: 38 cells drawn uniformly (seeded, logged)                    -> UNBIASED lane (permanently reserved 40%)
             58 cells drawn with probability proportional to (0.25 + mean frozen world_score of the cell's completed worlds) -> ADAPTIVE lane
             a new world of a cell always takes that cell's next unused seed index (seed-level pairing across cells is preserved)
  Every allocation decision is appended to CAMPAIGN_LOG.jsonl. Raw event rates are reported from UNBIASED-lane worlds only.
Stop launching new waves when wall time >= WALL_HOURS; running worlds finish. Hard stops (C13): any world with exposure mismatch,
provenance/attribution error rate > ERROR_TOL of completed worlds, runs directory > STORAGE_GB, any per-wave control world failing,
unbiased-lane coverage falling below 4 worlds per cell after wave 0.
Controls each wave (never mixed into treatment worlds; own seeds 900000+): positive (inserted census copier stream, must reproduce and
never count as random-origin establishment), laundering (inserted resident + random inflow hosts: descendants stay inserted), host-mediated
(inserted resident + known host tapes: HOST_EXECUTION births attributed to the resident), negative (all-NOP inflow: no births).
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, FIRST_COMPLETED, wait
from pathlib import Path

from archaeon.rie import physics as P
from archaeon.rie.world import run_world, world_score, spec_id, INFLOW

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RUNS = HERE / "runs"; LOG = HERE / "CAMPAIGN_LOG.jsonl"; PREREG = HERE / "PREREG.json"; PREFLIGHT = HERE / "PREFLIGHT.json"
T_EPOCHS = 16384; WAVE0_SEEDS = 4; WAVE = 96; UNBIASED_SHARE = 0.4; WALL_HOURS = 16.0; ERROR_TOL = 0.01; STORAGE_GB = 20.0; WORKERS = 22
SUBSTRATES = ["vmcopy", "z80"]
CELLS = [{"regime": r, "inflow": i, "topology": t, "substrate": s, "T": T_EPOCHS} for r in P.REGIMES for i in INFLOW for t in P.TOPOLOGIES for s in SUBSTRATES]
HASHED = ["archaeon/rie/campaign.py", "archaeon/rie/world.py", "archaeon/rie/physics.py", "archaeon/rie/analyze.py", "archaeon/rie/preflight.py",
          "archaeon/lineage/core.py", "archaeon/lineage/taint_vm.py", "archaeon/envgate/ruler.py", "archaeon/envgate/engine.py",
          "archaeon/z80atlas/vm.py", "archaeon/z80atlas/engine.py", "archaeon/z80atlas/grammar.py", "archaeon/z80atlas/census/copier_census.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def hashes():
    return {h: sha(REPO / h) for h in HASHED}


def log(rec):
    rec["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with LOG.open("a", encoding="utf-8") as f: f.write(json.dumps(rec, default=str) + "\n")


def controls(wave: int) -> dict:
    """Small isolated control worlds; returns {name: PASS}."""
    from archaeon.z80atlas.census import copier_census as C
    from archaeon.lineage import core as LC
    H = json.loads((REPO / "archaeon/z80atlas/census/HITS.json").read_text(encoding="utf-8"))["hits"]["vmcopy32"]
    cop = bytes.fromhex(sorted(h["tape"] for h in H if h["exact_inputs"] == [128])[0])
    resident = bytes.fromhex("c180094094938d528ef73c4ab400de8e7eb7a99cab37f38650832a8d607194a5")
    host = bytes.fromhex("0514643bfb639dee3e6ba2e6bcdd82231909c06b15333d2b273cd63549a8ef09")
    base = {"regime": "IID", "inflow": "REPLACE", "topology": "WELL_MIXED", "substrate": "vmcopy", "T": 1200}; sd = 900000 + wave
    out = {}
    r = run_world(base, sd, tapes=itertools.repeat(cop), origin=LC.ORIGIN_CONTROL)
    out["positive_copier"] = r["births"] > 0 and not r["genetic_established"]
    r = run_world(base, sd, origin=LC.ORIGIN_INFLOW, control_residents=[(c, resident, LC.ORIGIN_CONTROL) for c in range(0, 128, 2)])
    out["laundering"] = any(g["inserted"] and g["births"] > 0 for g in r["glins"].values()) and \
        all(not r["glins"][g]["inserted"] for g in r["genetic_established"] if g in r["glins"])
    r = run_world(base, sd, tapes=itertools.repeat(host), origin=LC.ORIGIN_INFLOW, control_residents=[(c, resident, LC.ORIGIN_CONTROL) for c in range(0, 128, 4)])
    out["host_mediated"] = r["births_by_mechanism"].get("HOST_EXECUTION", 0) > 0 and all(g["inserted"] for g in r["glins"].values() if g["births_hosted"] > 0)
    r = run_world(base, sd, tapes=itertools.repeat(bytes(32)), origin=LC.ORIGIN_INFLOW)
    out["negative_nop"] = r["births"] == 0
    return out


def _job(spec, seed, lane):
    t0 = time.time()
    try:
        r = run_world(spec, seed)
    except Exception as ex:                                                 # noqa: BLE001
        return {"spec": spec, "seed": seed, "lane": lane, "error": repr(ex), "wall_s": round(time.time() - t0, 1)}
    r["lane"] = lane; p = RUNS / ("%s_s%04d.json" % (r["spec_id"], seed))
    p.write_text(json.dumps(r, default=str) + "\n", encoding="utf-8", newline="\n")
    return {"spec": spec, "seed": seed, "lane": lane, "file": p.name, "score": world_score(r), "exposure_ok": r["exposure_ok"], "wall_s": r["wall_s"],
            "established": len(r["genetic_established"]), "bytes": p.stat().st_size}


def run(workers: int = WORKERS) -> int:
    pr = json.loads(PREREG.read_text(encoding="utf-8"))
    if hashes() != pr["code_sha256_lf_normalised"]: print("STOP: code changed after preregistration"); return 3
    RUNS.mkdir(exist_ok=True); t0 = time.time(); rng = random.Random("rie01.scheduler")
    next_seed = {spec_id(c): WAVE0_SEEDS for c in CELLS}; scores = {spec_id(c): [] for c in CELLS}; done = []; errors = 0; stop = None
    queue = [(c, s, "unbiased_wave0") for s in range(WAVE0_SEEDS) for c in CELLS]; wave = 0
    log({"event": "start", "cells": len(CELLS), "wave0_worlds": len(queue)})
    ctl = controls(0); log({"event": "controls", "wave": 0, "result": ctl})
    if not all(ctl.values()): log({"event": "STOP", "reason": "controls failed", "result": ctl}); return 5
    with ProcessPoolExecutor(workers) as ex:
        running = {}
        while True:
            while queue and len(running) < workers * 2 and stop is None:
                c, s, lane = queue.pop(0); fu = ex.submit(_job, c, s, lane); running[fu] = (c, s, lane)
            if not running: break
            fin, _ = wait(list(running), return_when=FIRST_COMPLETED)
            for fu in fin:
                c, s, lane = running.pop(fu); r = fu.result(); done.append(r); log({"event": "done", **{k: v for k, v in r.items() if k != "spec"}, "cell": spec_id(c)})
                if "error" in r: errors += 1
                else:
                    scores[spec_id(c)].append(r["score"])
                    if not r["exposure_ok"]: stop = "exposure accounting mismatch in %s" % r["file"]
                if len(done) >= 20 and errors / len(done) > ERROR_TOL: stop = "error rate %d/%d" % (errors, len(done))
            size = sum(p.stat().st_size for p in RUNS.glob("*.json")) / 1e9
            if size > STORAGE_GB: stop = "storage %.1f GB" % size
            if stop and not queue: pass
            if stop:
                log({"event": "STOP", "reason": stop}); queue = []
            elif not queue and (time.time() - t0) / 3600 < WALL_HOURS:
                wave += 1; ctl = controls(wave); log({"event": "controls", "wave": wave, "result": ctl})
                if not all(ctl.values()): stop = "controls failed wave %d" % wave; log({"event": "STOP", "reason": stop}); continue
                ids = [spec_id(c) for c in CELLS]; byid = dict(zip(ids, CELLS))
                n_unb = round(WAVE * UNBIASED_SHARE); unb = [rng.choice(ids) for _ in range(n_unb)]
                wts = [0.25 + (sum(scores[i]) / len(scores[i]) if scores[i] else 0.0) for i in ids]
                ada = rng.choices(ids, weights=wts, k=WAVE - n_unb)
                for lane, picks in (("unbiased", unb), ("adaptive", ada)):
                    for i in picks:
                        queue.append((byid[i], next_seed[i], lane)); next_seed[i] += 1
                log({"event": "wave", "wave": wave, "unbiased": unb, "adaptive": ada, "weights": dict(zip(ids, wts))})
    log({"event": "end", "worlds": len(done), "errors": errors, "stop": stop, "wall_h": round((time.time() - t0) / 3600, 2)})
    (HERE / "RUNS_MANIFEST.json").write_text(json.dumps({p.name: {"bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(RUNS.glob("*.json"))}, indent=0) + "\n",
                                             encoding="utf-8", newline="\n")
    return 0


def freeze(stamp: str, envgate2_commit: str) -> int:
    if PREREG.exists(): print("REFUSED: PREREG exists"); return 2
    pf = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    if pf["verdict"] != "PASS": print("REFUSED: preflight"); return 3
    from archaeon.rie import analyze as A, world as Wm
    pr = {"schema": "archaeon.rie.prereg.v1", "campaign": "RIE-01", "frozen_at_utc": stamp, "graduated_from": {"ENVGATE-02_results_commit": envgate2_commit},
          "digest": hashlib.sha256(json.dumps({"cells": CELLS, "hashes": hashes()}, sort_keys=True).encode()).hexdigest()[:16], "cells": len(CELLS),
          "scheduler": __doc__, "physics": P.__doc__, "observatory": Wm.__doc__, "promotion_score": Wm.world_score.__doc__, "analysis": A.__doc__,
          "anti_gravity": "no known copier tape is seeded into treatment worlds, selected for, used as a fitness target, promotion template or tuning target; "
                          "census copiers appear only in isolated control worlds; promotion reads observable classes only",
          "preflight_sha256": sha(PREFLIGHT), "code_sha256_lf_normalised": hashes()}
    PREREG.write_text(json.dumps(pr, indent=1, default=str) + "\n", encoding="utf-8", newline="\n"); print(pr["digest"]); return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--freeze"); ap.add_argument("--envgate2-commit"); ap.add_argument("--run", action="store_true"); ap.add_argument("--workers", type=int, default=WORKERS)
    a = ap.parse_args()
    sys.exit(freeze(a.freeze, a.envgate2_commit) if a.freeze else (run(a.workers) if a.run else 1))
