"""Adjudicate REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY: is the geometry ruler an instrument or noise?

For each run: rebuild (cfg, task) exactly, and CHECK the rebuild by reproducing the stored geometry.json scans
bit-for-bit with the frozen geometry.scan (else the row is REBUILD_MISMATCH and unused). Then, for the top specimen
(T) and the first replicator (F):
  null      the frozen scan procedure with the "mutant" == the unmutated tape: the fraction scored 'better' is
            the instrument's false-beneficial rate (a sound ruler reads 0)
  reseed    the frozen scan re-run with K fresh seeds: the sampling distribution of beneficial_density for the SAME
            tape, and of the gain T - F (does the flagged gain reproduce?)
  paired    a common-random-numbers scan: every mutant AND the base are scored on the SAME fixed input panel, over a
            fixed mutant set (every position x 16 fixed substitution deltas): a deterministic beneficial density
            with no input-sampling noise; gain_paired = BD_paired(T) - BD_paired(F)
    python geom_audit.py --set flagged --workers 18
    python geom_audit.py --set control --n 493 --seed 5      (runs with a defined gain that were NOT flagged)"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

HARNESS = "C:/Users/James/z80atlas_campaign_2026-09-19/code"
K_RESEED = 12
PANEL = 8
DELTAS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 128, 144, 170, 200, 233, 255)


def _mods():
    if HARNESS not in sys.path:
        sys.path.insert(0, HARNESS)
    from prometheus.z80atlas import geometry as Gm, grammar as G, vm
    from prometheus.z80atlas.tasks import Task, Environment, score
    return Gm, G, vm, Task, Environment, score


def _task0(cfg, seed, Environment, Task):
    env = Environment(cfg.task, cfg.env_dynamics, cfg.n_niches, seed * 7 + 1)
    if cfg.spatial == "RESERVOIR":
        env.tasks[0] = Task("ECHO")
    return env.task_for(0)


def _null_scan(Gm, tape, cfg, task, seed, n=40):
    """frozen scan() with the mutation step removed: mutant == base."""
    rng = random.Random(seed); L = cfg.L; tape = Gm._pad(tape, L)
    base = Gm._eval(tape, cfg, task, rng)
    better = 0
    for _ in range(n):
        rng.randrange(L); rng.randrange(1, 256)          # consume the same draws the mutation would
        e = Gm._eval(tape, cfg, task, rng)
        if e["score"] > base["score"] + 1e-9:
            better += 1
    return better / n


def _paired_bd(Gm, vm, score, tape, cfg, task, seed):
    L = cfg.L; tape = Gm._pad(tape, L)
    rng = random.Random(seed ^ 0x5EED)
    panel = [task.inputs(rng) for _ in range(PANEL)]
    sc = "ATOMIC" if cfg.scoring == "NEUTRAL" else cfg.scoring
    def sc_of(t):
        tot = 0.0
        for inputs in panel:
            mem = bytearray(256); mem[:L] = t
            for k, v in enumerate(inputs):
                mem[vm.IN_BASE + k] = v
            if cfg.layout == "SEPARATED":
                tr = vm.execute(mem, L, 0, cfg.budget // 2, inputs, region=(0, L // 2), allow_copyall=cfg.allow_copyall)
                tr2 = vm.execute(mem, L, L // 2, cfg.budget // 2, inputs, region=(L // 2, L), allow_copyall=cfg.allow_copyall)
                outs = tr.outputs + tr2.outputs
                fi = tr.first_in_step if tr.first_in_step is not None else tr2.first_in_step
                fo = tr.first_out_step if tr.first_out_step is not None else tr2.first_out_step
            else:
                tr = vm.execute(mem, L, 0, cfg.budget, inputs, allow_copyall=cfg.allow_copyall)
                outs, fi, fo = tr.outputs, tr.first_in_step, tr.first_out_step
            tot += score(task, outs, task.expected(inputs), sc, cfg.read_gate, fo, fi)
        return tot / PANEL
    b = sc_of(bytes(tape))
    better = same = 0; n = 0
    for p in range(L):
        for d in DELTAS:
            t = bytearray(tape); t[p] = (t[p] + d) & 0xFF
            s = sc_of(bytes(t)); n += 1
            if s > b + 1e-9:
                better += 1
            elif abs(s - b) < 1e-9:
                same += 1
    return {"base": round(b, 4), "bd": round(better / n, 4), "neutral": round(same / n, 4), "n": n}


def _one(rid: str) -> dict:
    Gm, G, vm, Task, Environment, score = _mods()
    cfg_j = Ld.run_file(rid, "config.json"); summ = Ld.run_file(rid, "summary.json"); geo = Ld.run_file(rid, "geometry.json")
    cfg = G.to_config(cfg_j["vec"], cfg_j["ticks"], cfg_j["cells"], cfg_j["budget"], tuple(cfg_j["init_tapes"] or ()))
    seed = cfg_j["seed"]
    task = _task0(cfg, seed, Environment, Task)
    hist = summ.get("env_history") or []
    if hist and hist[-1].get("why") != "init":                 # the runner scanned under the env state AT THE END of the run
        t0 = hist[-1]["tasks"][0]; task = Task(t0["kind"], k=t0["k"])
    T = bytes.fromhex(summ["top"][0]["tape"]); F = bytes.fromhex(summ["first_replication"]["tape"])
    re_top = Gm.scan(T, cfg, task, seed * 31 + 0, n=40)
    re_fr = Gm.scan(F, cfg, task, seed * 43, n=40)
    ok = (re_top["beneficial_density"] == geo["top"][0]["beneficial_density"] and re_top["base_score"] == geo["top"][0]["base_score"]
          and re_fr["beneficial_density"] == geo["first_replicator"]["beneficial_density"])
    row = {"run": rid, "vec": cfg_j["vec"], "task": task.to_dict(), "stored_gain": geo.get("beneficial_density_gain"),
           "status": "OK" if ok else "REBUILD_MISMATCH",
           "stored": {"T_bd": geo["top"][0]["beneficial_density"], "T_base": geo["top"][0]["base_score"],
                      "F_bd": geo["first_replicator"]["beneficial_density"], "F_base": geo["first_replicator"]["base_score"]}}
    if not ok:
        return row
    row["null_T"] = _null_scan(Gm, T, cfg, task, seed * 31 + 0)
    row["null_F"] = _null_scan(Gm, F, cfg, task, seed * 43)
    rs = []
    for k in range(K_RESEED):
        a = Gm.scan(T, cfg, task, 10 ** 9 + seed * 97 + k, n=40)["beneficial_density"]
        b = Gm.scan(F, cfg, task, 2 * 10 ** 9 + seed * 89 + k, n=40)["beneficial_density"]
        rs.append(round(a - b, 3))
    row["reseed_gains"] = rs
    row["reseed_gain_mean"] = round(sum(rs) / len(rs), 4)
    row["reseed_frac_gt_0p1"] = round(sum(1 for x in rs if x > 0.1) / len(rs), 3)
    pT = _paired_bd(Gm, vm, score, T, cfg, task, seed); pF = _paired_bd(Gm, vm, score, F, cfg, task, seed)
    row["paired_T"] = pT; row["paired_F"] = pF
    row["paired_gain"] = round(pT["bd"] - pF["bd"], 4)
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="*")
    ap.add_argument("--set", choices=("flagged", "control"), default=None)
    ap.add_argument("--n", type=int, default=493)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--workers", type=int, default=18)
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()
    ids = list(a.runs)
    if a.set == "flagged":
        ids += sorted({f["run"] for f in Ld.flags() if f["flag"] == "REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY"})
    elif a.set == "control":
        pool = [r["id"] for r in Ld.runs() if r.get("geometry") and r["geometry"].get("beneficial_density_gain") is not None
                and r["geometry"]["beneficial_density_gain"] <= 0.1]
        ids += random.Random(a.seed).sample(pool, a.n)
    tag = a.tag or a.set or "adhoc"
    with mp.Pool(a.workers) as pool:
        rows = pool.map(_one, ids, chunksize=1)
    p = Ld.write("GEOM_AUDIT_%s.json" % tag, {"tag": tag, "n": len(rows), "method": __doc__, "K_RESEED": K_RESEED, "PANEL": PANEL,
                                             "DELTAS": DELTAS, "rows": rows})
    from collections import Counter
    print(p, len(rows), Counter(r["status"] for r in rows))


if __name__ == "__main__":
    main()
