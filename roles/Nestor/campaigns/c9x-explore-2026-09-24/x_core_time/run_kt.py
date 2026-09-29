"""X-CORE-TIME (EXPLORE, MEASUREMENT / trajectory; child of C-CORE). Declared before running.

C-CORE (CONFIRMED): runaway heredity in 7ae3's cell ends with the founder's OP_SELF (positions 23-24)
and LDIR (52-53) bytes conserved as material in >= 80% of the population, and little else. Question
(bears on the selective-irreversibility program: what survives, what is lost, and when): is the core
HELD throughout while other founder material decays, or does founder material decay everywhere and the
core get re-fixed late (e.g. by a late sweep of one founder-rich clone)?

Sample: the first 8 C-CORE runaway runs by seed (not selected on the endpoint), replayed with the same
tagged ATOMIC runner; world depth must equal the C-CORE record. Every 100 epochs (and at the end):
freq[p] = share of live organisms whose position p is FOUNDER material.
Per run: core_min = min over checkpoints from epoch 200 on of the mean freq of positions 23, 24, 52, 53;
other_end = median freq of all other positions at the last checkpoint; other_mid = the same at epoch 500.
INVALID if any replay depth differs from its record.
Classification: SIGNAL (core held throughout) if in >= 6 of 8 runs core_min >= 0.6 AND other_end < 0.2;
CLEAN_NULL (late re-fixation) if in >= 6 of 8 runs core_min < 0.3; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
CK = HERE.parent / "c_core"
sys.path.insert(0, str(CK))
sys.path.insert(0, str(HERE.parent / "x_content"))
sys.path.insert(0, str(HERE.parent / "x_donor_swap"))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
CORE = (23, 24, 52, 53)
EVERY = 100


def plan():
    res = json.loads((CK / "RESULTS.json").read_text())
    run = sorted((r for r in res if r["depth"] >= 20 and r["anc0_share"] >= 0.9), key=lambda r: r["seed"])
    return [(r["seed"], r["depth"]) for r in run[:8]]


def freqs(r, founder_tag):
    alive = [o for o in r.orgs if o.alive and o.orig]
    if not alive:
        return []
    Lmax = max(len(o.orig) for o in alive)
    f = [0] * Lmax
    for o in alive:
        for p, t in enumerate(o.orig):
            if t == founder_tag:
                f[p] += 1
    return [round(x / len(alive), 4) for x in f]


def job(args):
    seed, recorded = args
    import world
    import run_ds
    import run_xc
    arm = run_ds.cells()[SPEC]
    traj = []

    class Tg(run_ds.runner_cls(world)):
        tagged = False

        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.track_material = True
            for o in self.orgs:
                if o.orig is None:
                    o.orig = bytearray([o.niche]) * o.length

        def _place(self, genome, anc, pid=None, niche=0):
            o = super()._place(genome, anc, pid, niche)
            if o.orig is None:
                o.orig = bytearray([niche]) * o.length
            return o

        def material_certificate(self):
            return None

        def step(self):
            if not self.tagged:
                f = next(o for o in self.orgs if o.anc == 0)
                f.orig = bytearray([run_xc.FOUNDER]) * f.length
                self.tagged = True
            super().step()
            if self.epoch % EVERY == 0:
                traj.append((self.epoch, freqs(self, run_xc.FOUNDER)))

    r = Tg(dict(arm["cell"], atlas_axis="NONE"), seed, tier=arm["tier"],
           implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    out = r.run()
    traj.append((r.epoch, freqs(r, run_xc.FOUNDER)))
    rec = {"seed": seed, "depth": out["max_causal_replication_depth"], "recorded_depth": recorded, "traj": traj}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%d.json" % seed)).write_text(json.dumps(rec))
    return rec


def core_mean(f):
    return sum(f[p] for p in CORE if p < len(f)) / len(CORE) if f else 0.0


def other_median(f):
    o = [f[p] for p in range(len(f)) if p not in CORE]
    return statistics.median(o) if o else 0.0


def main():
    todo = plan()
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(8, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if str(t[0]) not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    mism = [r["seed"] for r in res if r["depth"] != r["recorded_depth"]]
    rows = []
    for r in res:
        tr = r["traj"]
        late = [core_mean(f) for e, f in tr if e >= 200]
        mid = next((f for e, f in tr if e >= 500), tr[-1][1])
        rows.append({"seed": r["seed"], "core_min": round(min(late), 4) if late else 0.0,
                     "other_mid": round(other_median(mid), 4), "other_end": round(other_median(tr[-1][1]), 4),
                     "core_series": [round(core_mean(f), 3) for _, f in tr],
                     "other_series": [round(other_median(f), 3) for _, f in tr]})
    held = sum(x["core_min"] >= 0.6 and x["other_end"] < 0.2 for x in rows)
    refix = sum(x["core_min"] < 0.3 for x in rows)
    cls = ("INVALID" if mism or len(res) != len(todo) else "SIGNAL" if held >= 6 else
           "CLEAN_NULL" if refix >= 6 else "WEAK_SIGNAL")
    summ = {"classification": cls, "replay_mismatches": mism, "held": held, "refixed": refix,
            "checkpoint_epochs": [e for e, _ in res[0]["traj"]] if res else [], "per_run": rows}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "per_run"}, indent=1))


if __name__ == "__main__":
    main()
