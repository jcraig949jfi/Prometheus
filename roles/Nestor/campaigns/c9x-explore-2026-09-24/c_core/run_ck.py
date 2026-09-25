"""C-CORE (CONFIRM lane, fresh and frozen). Parent: X-CORE (EXPLORE, WEAK_SIGNAL).

NOTHING HERE MAY CHANGE AFTER COMMIT: cell, seeds, arm, endpoint, rules, allocation.

Observation (X-CORE, post hoc): in all 5 tagged runaway replays in 7ae3's cell, the founder material
(z8taint FOUNDER tag) held by >= 80% of the final population sits at the same four genome positions,
23-24 (ED 32 = OP_SELF, the self-location world op) and 52-53 (ED B0 = LDIR, block copy), plus a few
run-specific positions; everything else has turned over (X-CONTENT: founder bytes 13% median).
Claim under test: runaway pair-tape heredity in 7ae3's cell conserves the founder's two world-op
instructions (SELF and LDIR) as material, and little else.

Design: 7ae3's cell (H2 B-arm cell, atlas_axis NONE, manifest tier), ATOMIC write-back (C-ATOMIC logic,
X-DONOR-SWAP runner, amendment A1), 7ae3 genome implanted as the single founder, founder bytes tagged
FOUNDER = 254 at the first epoch (X-CONTENT runner). Fresh seeds 14_000_000 + s, s < 64. One job per process.
Per run at the end: freq[p] = share of live organisms whose position p is FOUNDER material.
A run is a RUNAWAY if world max causal depth >= 20 and anc0 share >= 0.9 (the C-SWAP-ACQUIRE endpoint).
Per runaway run: CORE4 = all of positions 23, 24, 52, 53 have freq >= 0.8; SPECIFIC = fewer than 20% of
the other positions (genome positions except the four) have freq >= 0.8.
CONFIRMED iff at least 15 runaway runs AND at least 60% of runaway runs are CORE4 AND SPECIFIC.
INSUFFICIENT if fewer than 15 runaway runs (no claim either way). NOT_CONFIRMED otherwise.
Eligibility (before freezing): C-ATOMIC C1 had 46/80 runaways in this cell and arm; expected ~37 of 64
(P(< 15) negligible). The classifier was dry-run before freezing on X-CORE's
records: own-cell runs 4/5 CORE4-and-SPECIFIC (12000000 misses position 53), all five 9cba runs fail
CORE4, an all-conserved genome fails SPECIFIC, a short genome fails both. The bar is 60%, not 80%,
because the exploratory rate is 4/5: at a true rate of 0.8 and ~37 runaways P(pass) ~ 0.99, at 0.6
about 0.5. Chance level: with ~10% of positions conserved per run, four named positions all conserved
by chance is ~1e-4 per run. Secondary, never decisive: per-position conservation counts across runaways;
the same statistics for positions 23/24 and 52/53 separately.

    python run_ck.py -> RESULTS.json, VERDICT.json
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "x_content"))
sys.path.insert(0, str(HERE.parent / "x_donor_swap"))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
N = 64
SEED0 = 14_000_000
CORE = (23, 24, 52, 53)


def job(seed):
    import world
    import run_ds
    import run_xc
    arm = run_ds.cells()[SPEC]

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

    r = Tg(dict(arm["cell"], atlas_axis="NONE"), seed, tier=arm["tier"],
           implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    out = r.run()
    alive = [o for o in r.orgs if o.alive and o.orig]
    Lmax = max(len(o.orig) for o in alive) if alive else 0
    freq = [0.0] * Lmax
    for o in alive:
        for p, t in enumerate(o.orig):
            if t == run_xc.FOUNDER:
                freq[p] += 1
    freq = [x / len(alive) for x in freq] if alive else []
    rec = {"seed": seed, "depth": out["max_causal_replication_depth"],
           "anc0_share": round(sum(o.anc == 0 for o in r.orgs if o.alive) / max(1, sum(o.alive for o in r.orgs)), 4),
           "alive": len(alive), "freq": [round(x, 4) for x in freq]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%d.json" % seed)).write_text(json.dumps(rec))
    return rec


def classify(r):
    f = r["freq"]
    core4 = all(p < len(f) and f[p] >= 0.8 for p in CORE)
    others = [f[p] for p in range(len(f)) if p not in CORE]
    specific = (sum(x >= 0.8 for x in others) < 0.2 * len(others)) if others else False
    return core4, specific


def main():
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [SEED0 + s for s in range(N) if str(SEED0 + s) not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    assert len(res) == N, len(res)
    run = [r for r in res if r["depth"] >= 20 and r["anc0_share"] >= 0.9]
    cls = [classify(r) for r in run]
    both = sum(c and s for c, s in cls)
    if len(run) < 15:
        verdict = "INSUFFICIENT"
    else:
        verdict = "CONFIRMED" if both >= 0.6 * len(run) else "NOT_CONFIRMED"
    per_pos = {}
    for r in run:
        for p, x in enumerate(r["freq"]):
            if x >= 0.8:
                per_pos[p] = per_pos.get(p, 0) + 1
    v = {"verdict": verdict, "runaways": len(run), "n": N, "core4_and_specific": both,
         "core4": sum(c for c, _ in cls), "specific": sum(s for _, s in cls),
         "secondary": {"self_23_24": sum(all(p < len(r["freq"]) and r["freq"][p] >= 0.8 for p in (23, 24)) for r in run),
                       "ldir_52_53": sum(all(p < len(r["freq"]) and r["freq"][p] >= 0.8 for p in (52, 53)) for r in run),
                       "positions_conserved_count": dict(sorted(per_pos.items()))}}
    (HERE / "RESULTS.json").write_text(json.dumps(res))
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
