"""X-CORE (EXPLORE, MEASUREMENT / localization; child of X-CONTENT). Declared before running.

X-CONTENT (WEAK_SIGNAL): anc-descended runaway populations carry a minority of founder material --
median founder-tagged byte share 0.13 (7ae3's cell) and 0.25 (9cba/e160), and almost no organism is
>= 50% founder bytes, although anc0 share is 1.0. Question: is the surviving founder material a
CONSERVED CORE (the same genome positions kept across the population, e.g. the copy machinery) or
scattered residue?

Sample: X-CONTENT's first 5 OWN runs and first 5 FOREIGN runs (by the X-CONTENT plan order), replayed
with the same tagged ATOMIC runner (world depth must equal the record). At the end, for each live
organism, the positions whose byte carries the FOUNDER tag, in genome coordinates. Per run:
freq[p] = share of live organisms whose position p is founder material; the 16-byte window (cyclic
not allowed) with the highest mean freq, its mean, and the founder bytes at those positions.
INVALID if any replay depth differs from its record.
Classification: SIGNAL (conserved core) if in >= 7 of 10 runs some window of <= 16 contiguous
positions has mean freq >= 0.8; CLEAN_NULL (scattered) if in no run does any single position reach
freq 0.5; WEAK_SIGNAL otherwise. Also reported: whether the best windows of different runs overlap
in founder coordinates (same core) -- descriptive only.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
XC = HERE.parent / "x_content"
sys.path.insert(0, str(XC))
sys.path.insert(0, str(HERE.parent / "x_donor_swap"))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
W = 16


def plan():
    import run_xc
    todo = run_xc.plan()
    own = [t for t in todo if t[0] == "OWN"][:5]
    foreign = [t for t in todo if t[0] == "FOREIGN"][:5]
    return own + foreign


def job(args):
    group, sp, seed, recorded = args
    import world
    import run_ds
    import run_xc
    arm = run_ds.cells()[sp]
    captured = {}

    Base = run_ds.runner_cls(world)

    class Tg(Base):
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
                captured["founder"] = bytes(self._genome(f))
                self.tagged = True
            super().step()

    r = Tg(dict(arm["cell"], atlas_axis="NONE"), seed, tier=arm["tier"],
           implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    out = r.run()
    alive = [o for o in r.orgs if o.alive and o.orig]
    Lmax = max(len(o.orig) for o in alive)
    freq = [0.0] * Lmax
    for o in alive:
        for p, t in enumerate(o.orig):
            if t == run_xc.FOUNDER:
                freq[p] += 1
    freq = [x / len(alive) for x in freq]
    best = max(range(max(1, Lmax - W + 1)), key=lambda i: sum(freq[i:i + W]))
    wmean = sum(freq[best:best + W]) / min(W, Lmax - best)
    rec = {"group": group, "specimen": sp, "seed": seed, "depth": out["max_causal_replication_depth"],
           "recorded_depth": recorded, "alive": len(alive), "max_pos_freq": round(max(freq), 4),
           "best_window_start": best, "best_window_mean": round(wmean, 4),
           "founder_window_bytes": captured["founder"][best:best + W].hex(),
           "freq": [round(x, 4) for x in freq]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%s_%d.json" % (group, sp[:4], seed))).write_text(json.dumps(rec))
    return rec


def main():
    todo = plan()
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%s_%d" % (t[0], t[1][:4], t[2]) not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    mism = [(r["group"], r["specimen"][:4], r["seed"]) for r in res if r["depth"] != r["recorded_depth"]]
    core = sum(r["best_window_mean"] >= 0.8 for r in res)
    anyhalf = sum(r["max_pos_freq"] >= 0.5 for r in res)
    cls = ("INVALID" if mism or len(res) != len(todo) else "SIGNAL" if core >= 7 else
           "CLEAN_NULL" if anyhalf == 0 else "WEAK_SIGNAL")
    summ = {"classification": cls, "replay_mismatches": mism, "runs_with_core_window": core,
            "runs_with_any_position_ge_0.5": anyhalf,
            "per_run": [{k: r[k] for k in ("group", "specimen", "seed", "max_pos_freq", "best_window_start",
                                            "best_window_mean", "founder_window_bytes")} for r in res]}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
