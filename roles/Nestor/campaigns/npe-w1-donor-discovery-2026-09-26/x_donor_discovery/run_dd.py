"""X-DONOR-DISCOVERY (EXPLORE, INITIAL_CONDITION / discovery; first node of NPE window W1, operator
directive 2026-09-26 prompts/2026-09-26_npe_window_donor_discovery/). Declared before running.
Theory-aware by date (this seat has been exposed to the selective-irreversibility hypothesis);
the question here is native to the Cycle-9 barrier chain.

Window question: how do competent hereditary donors arise from non-competent starting material,
and what barrier currently controls that transition?
Parents: X-ATOMIC-RANDOM (a random implant in 7ae3's cell under ATOMIC write-back never ran away,
0/80) and X-DONOR-RATE (12 of 16 panel donors never copy from a fresh state). Erosion is removed
by ATOMIC write-back (C-ATOMIC C1); the remaining candidate barrier is donor ACQUISITION.
Question: starting from genuinely random populations, how often and when do organisms appear that
pass a fresh-start causal-copy assay, and is that appearance the dominant limiting transition?

Cells (the 7ae3 / ffa6 class, where OP_SELF and the BLOCK copy primitive are in the ops mask):
  CELL_7AE3 = 7ae3's frozen H2 B-arm cell (Z8_64, WELL_MIXED), atlas_axis NONE, manifest tier M;
  CELL_FFA6 = ffa6's (Z8_SLOTTED, NICHES_HIGH_MIG), same.
Arms: RANDOM (no implant; the cell's own RANDOM seeding), ATOMIC write-back (X-DONOR-SWAP runner,
C-ATOMIC logic). Fresh seeds 15_000_000 + s, s < 48, per cell (96 runs). No known donor is seeded.

Ruler, four distinct levels (never merged):
  L1 CONTAINS   - a genome contains both world-op instructions as byte pairs, ED 32 (OP_SELF) and
                  ED B0 (LDIR), anywhere (static scan; says nothing about execution);
  L2 COMPETENT  - a genome passes the fresh-start P-11 assay (X-DONOR-SWAP / X-ACQUIRE assay: the
                  genome as donor on either tape side, blank partner, fresh register state, the
                  cell's ops mask, slice budget and copy mutation; world-shaped tape per X-ACQUIRE
                  A1). Screen: 4 seeds; any pass -> 20 seeds; COMPETENT iff rate >= 0.5.
  L3 DESCENDANT - in-world P-11 causal depth >= 2 (a certified copy's copy);
  L4 RUNAWAY    - in-world causal depth >= 20.
Checkpoints every 100 epochs (and the end): every distinct live genome is scanned (L1) and screened
(L2). Also per checkpoint, for mining if L2 is rare: best fid_final and best donor-authored share
over all screened draws, and counts of draws passing each of C2 / C4 / C5.
In-world: replication_events (predecessor criterion), p11_events, max causal depth.

Controls (ruler must be able to fire; labelled scaffolds, never treatments):
  PC-ASSAY - the 7ae3 genome through the same screen in CELL_7AE3 must be COMPETENT;
  PC-RUN   - 4 runs in CELL_7AE3 with the 7ae3 genome implanted (seeds 15_900_000 + s): the
             epoch-100 checkpoint must find >= 1 COMPETENT genome in >= 2 of 4.
INVALID if either control fails.
Classification (question: is donor acquisition the dominant limit?), over the 96 RANDOM runs:
  SIGNAL (acquisition-limited)  if a COMPETENT genome appears in <= 10% of runs;
  CLEAN_NULL (not acquisition)  if a COMPETENT genome appears in >= 30% of runs (the limit is then
                                downstream: L2 -> L3 -> L4);
  WEAK_SIGNAL otherwise.
Reported, never decisive: the L1/L2/L3/L4 funnel per cell, first-appearance epochs, and whether L1
precedes L2.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9X = HERE.parent.parent / "c9x-explore-2026-09-24"
sys.path.insert(0, str(C9X / "x_donor_swap"))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
CELLS = {"7ae3": "7ae3f9c1437c8000-s54765-tL-a0", "ffa6": "ffa6b3fb06df72a7-s55806-tL-a0"}
N = 48
SEED0 = 15_000_000
PC_SEED0 = 15_900_000
EVERY = 100
K1, K2 = 4, 20
SELF, LDIR = bytes((0xED, 0x32)), bytes((0xED, 0xB0))


def assay_one(world, r, g, tag, k):
    """k seeds, donor on either side; returns (passes, draw summaries)."""
    n = r.L
    t = bytearray(world._pow2(2 * n))
    t[0:len(g)] = g
    t[n:n + len(g)] = g
    tl = len(t)
    fresh = (None, 0, 0)
    hits, draws = 0, []
    for i in range(k):
        ok = False
        for side in (0, 1):
            ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
            res = world.p11.assay(world.z8, n=n, tape_len=tl, ga=ga, gb=gb, st_a=fresh, st_b=fresh,
                                  budget=r.t["slice"], ops_mask=r._ops_mask(), cmr=r.copy_mut,
                                  victim_side=1 - side, seed=("X-DONOR-DISCOVERY", tag, i, side))
            ok = ok or res["pass"]
            draws.extend(res["draws"])
        hits += ok
    return hits, draws


def screen(world, r, genomes, tag):
    """L1 + L2 over distinct genomes; returns a checkpoint record."""
    rec = {"distinct": len(genomes), "L1": 0, "self": 0, "ldir": 0, "stage1": 0, "L2": 0,
           "best_fid_final": 0.0, "best_auth_share": 0.0, "draws": 0, "C2": 0, "C4": 0, "C5": 0,
           "competent_genomes": []}
    for j, g in enumerate(genomes):
        hs, hl = SELF in g, LDIR in g
        rec["self"] += hs
        rec["ldir"] += hl
        rec["L1"] += hs and hl
        h, dr = assay_one(world, r, g, (tag, j, 1), K1)
        for d in dr:
            rec["draws"] += 1
            rec["C2"] += d["C2"]
            rec["C4"] += d["C4"]
            rec["C5"] += d["C5"]
            rec["best_fid_final"] = max(rec["best_fid_final"], d["fid_final"])
            rec["best_auth_share"] = max(rec["best_auth_share"], d["donor_authored_share"])
        if h:
            rec["stage1"] += 1
            h2, _ = assay_one(world, r, g, (tag, j, 2), K2)
            if h2 / K2 >= 0.5:
                rec["L2"] += 1
                rec["competent_genomes"].append({"hex": g.hex(), "rate": h2 / K2, "L1": hs and hl})
    rec["best_fid_final"] = round(rec["best_fid_final"], 4)
    rec["best_auth_share"] = round(rec["best_auth_share"], 4)
    return rec


def job(args):
    kind, cell, seed = args
    import world
    import run_ds
    arm = run_ds.cells()[CELLS[cell]]
    cps = []

    class Dd(run_ds.runner_cls(world)):
        def step(self):
            super().step()
            if self.epoch % EVERY == 0:
                gs = sorted({bytes(self._genome(o)) for o in self.orgs if o.alive})
                c = screen(world, self, gs, (kind, cell, seed, self.epoch))
                c["epoch"] = self.epoch
                c["p11_events_cum"] = self.ct["p11_events"]
                c["replication_events_cum"] = self.ct["replication_events"]
                cps.append(c)

    kw = {}
    if kind == "PC":
        kw = dict(implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    r = Dd(dict(arm["cell"], atlas_axis="NONE"), seed, tier=arm["tier"], **kw)
    out = r.run()
    rec = {"kind": kind, "cell": cell, "seed": seed, "depth": out["max_causal_replication_depth"],
           "p11_events": out["p11_events"], "replication_events": r.ct["replication_events"], "checkpoints": cps}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%s_%d.json" % (kind, cell, seed))).write_text(json.dumps(rec))
    return rec


def pc_assay():
    import world
    import run_ds
    arm = run_ds.cells()[CELLS["7ae3"]]
    r = world.Runner(dict(arm["cell"], atlas_axis="NONE"), 1, tier=arm["tier"])
    return screen(world, r, [bytes(r._pad(run_ds.donor_genome()))], ("PC-ASSAY",))


def jobs():
    j = [("PC", "7ae3", PC_SEED0 + s) for s in range(4)]
    return j + [("RANDOM", c, SEED0 + s) for s in range(N) for c in CELLS]


def main():
    pa = pc_assay()
    (HERE / "PC_ASSAY.json").write_text(json.dumps(pa, indent=1))
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [t for t in jobs() if "%s_%s_%d" % t not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    pc = [r for r in res if r["kind"] == "PC"]
    rnd = [r for r in res if r["kind"] == "RANDOM"]
    pc_run_ok = sum(any(c["L2"] > 0 for c in r["checkpoints"] if c["epoch"] == EVERY) for r in pc) >= 2
    pc_assay_ok = pa["L2"] == 1

    def ever(r, key):
        return any(c[key] > 0 for c in r["checkpoints"])

    def first(r, key):
        return next((c["epoch"] for c in r["checkpoints"] if c[key] > 0), None)

    funnel = {}
    for cell in list(CELLS) + ["ALL"]:
        rows = [r for r in rnd if cell == "ALL" or r["cell"] == cell]
        funnel[cell] = {"n": len(rows), "L1_any": sum(ever(r, "L1") for r in rows),
                        "stage1_any": sum(ever(r, "stage1") for r in rows),
                        "L2_any": sum(ever(r, "L2") for r in rows),
                        "L3_depth_ge2": sum(r["depth"] >= 2 for r in rows),
                        "L4_depth_ge20": sum(r["depth"] >= 20 for r in rows),
                        "any_p11_event": sum(r["p11_events"] > 0 for r in rows),
                        "any_replication_event": sum(r["replication_events"] > 0 for r in rows)}
    share = funnel["ALL"]["L2_any"] / max(1, funnel["ALL"]["n"])
    cls = ("INVALID" if not (pc_run_ok and pc_assay_ok) or len(res) != len(jobs()) else
           "SIGNAL" if share <= 0.10 else "CLEAN_NULL" if share >= 0.30 else "WEAK_SIGNAL")
    summ = {"classification": cls, "pc_assay_ok": pc_assay_ok, "pc_run_ok": pc_run_ok,
            "L2_share_of_runs": round(share, 4), "funnel": funnel,
            "first_epoch": {k: [first(r, k) for r in rnd if first(r, k) is not None] for k in ("L1", "stage1", "L2")},
            "max_best_fid_final": max((c["best_fid_final"] for r in rnd for c in r["checkpoints"]), default=0),
            "max_best_auth_share": max((c["best_auth_share"] for r in rnd for c in r["checkpoints"]), default=0)}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
