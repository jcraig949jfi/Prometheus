"""X-TASK-GATE (NPE frontier; Aporia dispatch #1150, CWO-2026-09-30C s7). Instrument for PREREG.md in this directory.
DESIGN + FREEZE ONLY under #1150: this file is NOT to be run until a separate Aporia execution dispatch.

Question: in the endogenous pair-tape replicator regime (ffa6 cell, dense VM, ATOMIC runner, random populations, no implant),
does a TASK-COUPLED interaction gate make task competence spread through the organisms' own causal replication -- or is any
competence a gating/sorting artifact, an input artifact (answer without reading), or bookkeeping (label-only births)?

Arms (fresh seeds SEED0 + s):
  Stage 0 (planted positive for the competence ruler and the coupling statistic; read alone, first):
    EXT_TG    reproduction EXTERNAL, pressure TASK_GATED_INTERACTION (the manager picks the fittest of 3)     s < 6
    EXT_NONE  reproduction EXTERNAL, pressure NONE_IMPLICIT (the manager picks a random parent)              s < 6
  Stage 1 (only if Stage 0 PASSES):
    TG        PAIR_EXECUTION, TASK_GATED_INTERACTION: a pair interacts with p = 0.15 + 0.85 * max(comp_a, comp_b)  s < 18
    SHUF      PAIR_EXECUTION, the same gate reading max(comp) of TWO OTHER random live organisms (private RNG):
              the same interaction-rate distribution (pairs are uniformly random), decoupled from the pair           s < 18
Per organism, provenance is recorded at birth (INIT = placed at epoch 0 and never overwritten; P11 = born by an accepted
pair-tape replication whose P-11 causal assay passed; LABEL = accepted by the predecessor criterion but not P-11 causal;
EXT = an external (manager) birth). Readouts at the final epoch, over live organisms:
  competent  held >= 0.5 AND reader (reads_at_answer >= cue_index + 1: the answer follows the key byte)
  CS = competent share;  CD = share that is competent AND provenance P11;  sorting = competent with provenance INIT
  regime = max causal replication depth >= 20 (runaway)

    python run_xtg.py stage0   -> results/stage0/ + STAGE0.json
    python run_xtg.py stage1   -> results/stage1/ + VERDICT.json   (refuses unless STAGE0.json says PASS)
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import random
import statistics
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
W1 = ROOT / "npe-w1-donor-discovery-2026-09-26"
for p in (W1 / "x_donor_discovery", W1 / "x_dd_dense_copy", ROOT / "c9x-explore-2026-09-24" / "x_donor_swap",
          ROOT / "z80atlas-verify-2026-09-22", ROOT.parent / "lib"):
    sys.path.insert(0, str(p))

CELL = "ffa6"
SEED0 = 31_000_000
POOL = 8
ARMS = {"EXT_TG": ("EXTERNAL", "TASK_GATED_INTERACTION", 6, 0),
        "EXT_NONE": ("EXTERNAL", "NONE_IMPLICIT", 6, 0),
        "TG": ("PAIR_EXECUTION", "TASK_GATED_INTERACTION", 18, 1),
        "SHUF": ("PAIR_EXECUTION", "TASK_GATED_INTERACTION", 18, 1)}
HELD_MIN, SHARE_MIN = 0.5, 0.10


def jobs(stage):
    return [(arm, SEED0 + s) for arm, (_r, _p, n, st) in ARMS.items() if st == stage for s in range(n)]


def _run(arm, seed):
    import world
    import run_dc
    import run_dd
    import run_ds
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS[CELL]]
    repro, pressure, _n, stage = ARMS[arm]
    cell = dict(a["cell"], atlas_axis="NONE", reproduction=repro, pressure=pressure)
    prov = {}
    shuf_rng = random.Random(seed * 1_000_003 + 17)          # private: the world RNG never sees the shuffle

    class Xt(run_ds.runner_cls(world)):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if self.cell["reproduction"] == "EXTERNAL":
                prov[child] = "EXT"
            elif p11_rec is not None:
                prov[child] = "P11" if p11_rec.get("pass") else "LABEL"
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def _pair_epoch(self):
            if arm != "SHUF":
                return super()._pair_epoch()
            # world._pair_epoch with the gate's competence read from two other random organisms (TASK_GATED branch only;
            # this cell's pressure is TASK_GATED_INTERACTION and has_task holds, asserted below).
            alive = [o for o in self.orgs if o.alive]
            self.rng.shuffle(alive)
            for i in range(0, len(alive) - 1, 2):
                a_, b_ = alive[i], alive[i + 1]
                c_, d_ = alive[shuf_rng.randrange(len(alive))], alive[shuf_rng.randrange(len(alive))]
                if self.rng.random() > 0.15 + 0.85 * max(c_.comp, d_.comp):
                    continue
                self._pair_interact(i, a_, b_)

    r = Xt(cell, seed, tier=a["tier"])
    assert r.d["has_task"] and r.cell["pressure"] == pressure and r.cell["reproduction"] == repro
    t0 = time.time()
    out = r.run()
    r._validate(force=True)          # readout only, after the run: competence as of the final epoch, not <= 10 epochs stale
    ci = r.spec.cue_index()
    alive = [o for o in r.orgs if o.alive]
    comp = [o for o in alive if o.held >= HELD_MIN and o.probe >= ci + 1]
    n = max(1, len(alive))
    rec = {"arm": arm, "seed": seed, "stage": stage, "alive": len(alive), "wall_s": round(time.time() - t0, 1),
           "depth": out["max_causal_replication_depth"], "held_max_final": out["held_max_final"],
           "p11_events": out.get("p11_events"),
           "CS": round(len(comp) / n, 4),
           "CD": round(sum(prov.get(o.oid) == "P11" for o in comp) / n, 4),
           "sorting": round(sum(o.oid not in prov for o in comp) / n, 4),
           "label_only": round(sum(prov.get(o.oid) == "LABEL" for o in comp) / n, 4),
           "competent_nonreader": round(sum(o.held >= HELD_MIN and o.probe < ci + 1 for o in alive) / n, 4)}
    d = HERE / "results" / ("stage%d" % stage)
    d.mkdir(parents=True, exist_ok=True)
    (d / ("%s_%d.json" % (arm, seed))).write_text(json.dumps(rec))
    return rec


def _job(args):
    return _run(*args)


def _pool(todo, stage):
    d = HERE / "results" / ("stage%d" % stage)
    done = {p.stem for p in d.glob("*.json")} if d.exists() else set()
    with mp.Pool(POOL, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(_job, [t for t in todo if "%s_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted(d.glob("*.json"))]
    assert len(res) == len(todo), (len(res), len(todo))
    return res


def stage0():
    res = _pool(jobs(0), 0)
    tg = [r for r in res if r["arm"] == "EXT_TG"]
    no = [r for r in res if r["arm"] == "EXT_NONE"]
    diff = statistics.mean(r["held_max_final"] for r in tg) - statistics.mean(r["held_max_final"] for r in no)
    k = sum(r["CS"] >= SHARE_MIN for r in tg)
    v = {"stage0": "PASS" if diff >= 0.15 and k >= 3 else "FAIL", "mean_held_diff": round(diff, 4),
         "ext_tg_runs_CS_ge_0.10": k, "wall_s": sum(r["wall_s"] for r in res), "runs": res}
    (HERE / "STAGE0.json").write_text(json.dumps(v, indent=1))
    print(json.dumps({x: y for x, y in v.items() if x != "runs"}, indent=1))


def verdict(res):
    arm = {a: [r for r in res if r["arm"] == a] for a in ("TG", "SHUF")}
    reg = {a: sum(r["depth"] >= 20 for r in v) for a, v in arm.items()}
    c = {a: sum(r["CS"] >= SHARE_MIN for r in v) for a, v in arm.items()}
    n = {a: sum(r["CD"] >= SHARE_MIN for r in v) for a, v in arm.items()}
    if min(reg.values()) < 4:
        cls = "NO_REPLICATOR_REGIME"
    elif c["TG"] < 3:
        cls = "FLOOR"
    elif n["TG"] < 2:
        cls = "GATE_OR_SORTING_ARTIFACT"
    elif n["TG"] >= 4 and n["TG"] >= n["SHUF"] + 3:
        cls = "ENDOGENOUS_TASK_COUPLED"
    elif n["TG"] >= 4 and n["SHUF"] >= n["TG"] - 2:
        cls = "ENDOGENOUS_UNCOUPLED"
    else:
        cls = "MIXED"
    return {"verdict": cls, "regime_runs": reg, "runs_CS_ge_0.10": c, "runs_CD_ge_0.10": n}


def stage1():
    s0 = json.loads((HERE / "STAGE0.json").read_text())
    if s0["stage0"] != "PASS":
        raise SystemExit("Stage 0 did not PASS: verdict INSTRUMENT_UNREACHABLE; Stage 1 is not run")
    res = _pool(jobs(1), 1)
    v = dict(verdict(res), wall_s=sum(r["wall_s"] for r in res), runs=res)
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps({x: y for x, y in v.items() if x != "runs"}, indent=1))


if __name__ == "__main__":
    {"stage0": stage0, "stage1": stage1}[sys.argv[1]]()
