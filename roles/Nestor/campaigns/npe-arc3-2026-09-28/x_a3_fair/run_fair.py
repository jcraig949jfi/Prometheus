"""X-A3-FAIR (EXPLORE, RULER / treatment-blind competence; ARC3 Blocks B and A). Declared before running. Theory-aware.

P2 (C-ZERO-SPECIFIC, confirmed): with implanted donors certified COMPETENT from the zero register state, establishment is
rescued only by a ZERO reset. Circularity: the ruler certifies from zeros, so it may select exactly the zero-dependence later
called a mechanism. Block A rival: the donors may need only "one predictable constant" (or a structured pattern), not zero.
Questions:
  B  Does specialization to the environment's initialization emerge when the discovery ruler does not privilege any single
     initialization?
  A  Does specialization track WHATEVER constant the world supplies (0x5A world -> 0x5A specialists), or is literal zero special?

Fair ruler (treatment-blind): entry-state battery E = {Z: all-zero, K: all bytes 0x5A, R1, R2: two fixed random vectors drawn
once from a fixed seed and recorded}. In the assay BOTH organisms enter in state e (the world's reset applies to both). For each
distinct live genome: a 2-seed stage-1 per e; any pass -> 20-seed stage-2 for that e; COMPETENT_e iff rate >= 0.5. DONOR iff
COMPETENT_e for ANY e in E. Results cached per (genome, e). Profile = the set of e where competent. Classes (post-selection
stratification): Z_ONLY, K_ONLY, BOTH_CONST (Z and K, no R), ROBUST (any R), OTHER.
Worlds (lib/reset_axis.py, applied to both organisms before every pair interaction): CARRIED (the default NPE world), ZERO,
CONST:5A. Random populations, dense VM (as W1/P2), ATOMIC runner, cells 7ae3 and ffa6, fresh seeds 24_000_000 + s, s < 24, per
cell per world: 144 runs, 2000 epochs, screen every 100 epochs.
Readouts per run: first-donor epoch and its genome's profile (all donor genomes at that checkpoint), class shares of donors at the
last checkpoint, world causal depth (L4 >= 20).
Specialist-of-world share S_W over donor runs: ZERO world -> first-donor genome Z-competent and not K-competent; CONST:5A world
-> K-competent and not Z-competent.
Classification:
  SIGNAL (label TRACKS_WORLD)    if both reset worlds have >= 10 donor runs and S_ZERO >= 0.6 and S_5A >= 0.6;
  SIGNAL (label ZERO_LITERAL)    if S_ZERO >= 0.6 and (CONST:5A has <= 3 donor runs or S_5A <= 0.2);
  CLEAN_NULL (NO_SPECIALIZATION) if both reset worlds have >= 10 donor runs and specialist shares are both <= 0.3;
  WEAK_SIGNAL otherwise.
Reported, never decisive: CARRIED-world class shares (Block B: what the default world discovers under a fair ruler); acquisition
and L4 per world.
Self-tests before launch: reset_axis.selftest; the fair assay's entry state reaches z8.run for both organisms.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
W1 = ROOT / "npe-w1-donor-discovery-2026-09-26"
for p in (ROOT.parent / "lib", W1 / "x_dd_dense_copy", W1 / "x_donor_discovery", ROOT / "c9x-explore-2026-09-24" / "x_donor_swap",
          ROOT / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
CELLS = {"7ae3": "7ae3f9c1437c8000-s54765-tL-a0", "ffa6": "ffa6b3fb06df72a7-s55806-tL-a0"}
WORLDS = ("CARRIED", "ZERO", "CONST:5A")
N = 24
SEED0 = 24_000_000
EVERY = 100
_r = random.Random(20260928)
ENTRY = {"Z": (None, 0, 0), "K": ([0x5A] * 8, 0, 0),
         "R1": ([_r.randrange(256) for _ in range(8)], _r.randrange(2), _r.randrange(2)),
         "R2": ([_r.randrange(256) for _ in range(8)], _r.randrange(2), _r.randrange(2))}


def fair_assay(world, r, g, e, tag, k):
    n = r.L
    t = bytearray(world._pow2(2 * n))
    t[0:len(g)] = g
    t[n:n + len(g)] = g
    tl = len(t)
    st = ENTRY[e]
    hits = 0
    for i in range(k):
        ok = False
        for side in (0, 1):
            ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
            res = world.p11.assay(world.z8, n=n, tape_len=tl, ga=ga, gb=gb,
                                  st_a=(None if st[0] is None else list(st[0]), st[1], st[2]),
                                  st_b=(None if st[0] is None else list(st[0]), st[1], st[2]),
                                  budget=r.t["slice"], ops_mask=r._ops_mask(), cmr=r.copy_mut,
                                  victim_side=1 - side, seed=("X-A3-FAIR", tag, e, i, side))
            ok = ok or res["pass"]
        hits += ok
    return hits / k


def profile(world, r, g, cache):
    if g in cache:
        return cache[g]
    out = []
    for e in ENTRY:
        if fair_assay(world, r, g, e, g.hex(), 2) > 0 and fair_assay(world, r, g, e, g.hex() + "/2", 20) >= 0.5:
            out.append(e)
    cache[g] = tuple(out)
    return cache[g]


def klass(p):
    s = set(p)
    if not s:
        return None
    if s & {"R1", "R2"}:
        return "ROBUST"
    if s == {"Z"}:
        return "Z_ONLY"
    if s == {"K"}:
        return "K_ONLY"
    if s == {"Z", "K"}:
        return "BOTH_CONST"
    return "OTHER"


def job(args):
    world_policy, cell, seed = args
    import world
    import run_dc
    import run_ds
    import reset_axis
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[CELLS[cell]]
    prng = random.Random(repr(("X-A3-FAIR", seed, world_policy)))
    cache, cps = {}, []

    class F(reset_axis.with_reset(run_ds.runner_cls(world), world_policy, prng)):
        def step(self):
            super().step()
            if self.epoch % EVERY == 0:
                gs = sorted({bytes(self._genome(o)) for o in self.orgs if o.alive})
                profs = {g.hex(): profile(world, self, g, cache) for g in gs}
                donors = {h: p for h, p in profs.items() if p}
                cps.append({"epoch": self.epoch, "distinct": len(gs), "donors": len(donors),
                            "classes": {c: sum(klass(p) == c for p in donors.values())
                                        for c in ("Z_ONLY", "K_ONLY", "BOTH_CONST", "ROBUST", "OTHER")},
                            "donor_profiles": dict(list(donors.items())[:20])})

    r = F(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    rec = {"world": world_policy, "cell": cell, "seed": seed, "depth": out["max_causal_replication_depth"], "checkpoints": cps}
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results" / ("%s_%s_%d.json" % (world_policy.replace(":", ""), cell, seed))).write_text(json.dumps(rec))
    return rec


def jobs():
    return [(w, c, SEED0 + s) for s in range(N) for c in CELLS for w in WORLDS]


def selftests():
    import world
    import run_dc
    import run_ds
    import reset_axis
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[CELLS["7ae3"]]
    ok1, st1 = reset_axis.selftest(world, run_ds.runner_cls(world), dict(a["cell"], atlas_axis="NONE"), a["tier"])
    r = world.Runner(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
    seen = []
    orig = world.z8.run

    def spy(ctx, pc, budget, ops_enabled=0xFF):
        seen.append([0] * 8 if ctx.regs is None else list(ctx.regs))
        return orig(ctx, pc, budget, ops_enabled)
    world.z8.run = spy
    try:
        fair_assay(world, r, bytes(r._pad(b"\x00")), "K", "selftest", 1)
    finally:
        world.z8.run = orig
    ok2 = len(seen) >= 2 and seen[0] == [0x5A] * 8 and seen[1] == [0x5A] * 8
    return ok1 and ok2, {"reset_axis": st1, "fair_entry_reaches_both": ok2}


def main():
    ok, st = selftests()
    (HERE / "SELFTEST.json").write_text(json.dumps({"ok": ok, **st, "entry_states": {k: [v[0], v[1], v[2]] for k, v in ENTRY.items()}}))
    assert ok, st
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    done = {p.stem for p in (HERE / "results").glob("*.json")}
    todo = [t for t in jobs() if "%s_%s_%d" % (t[0].replace(":", ""), t[1], t[2]) not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    summ = {"per_world": {}}
    for w in WORLDS:
        rows = [r for r in res if r["world"] == w]
        first = []
        for r in rows:
            cp = next((c for c in r["checkpoints"] if c["donors"] > 0), None)
            if cp:
                first.append(list(cp["donor_profiles"].values()))
        spec = None
        if w == "ZERO":
            spec = [all("Z" in p and "K" not in p for p in f) for f in first]
        elif w == "CONST:5A":
            spec = [all("K" in p and "Z" not in p for p in f) for f in first]
        last = {c: sum(r["checkpoints"][-1]["classes"][c] for r in rows if r["checkpoints"])
                for c in ("Z_ONLY", "K_ONLY", "BOTH_CONST", "ROBUST", "OTHER")}
        summ["per_world"][w] = {"runs": len(rows), "donor_runs": len(first), "L4": sum(r["depth"] >= 20 for r in rows),
                                "specialist_of_world_share": round(sum(spec) / len(spec), 4) if spec else None,
                                "first_donor_classes": {c: sum(klass(p) == c for f in first for p in f)
                                                        for c in ("Z_ONLY", "K_ONLY", "BOTH_CONST", "ROBUST", "OTHER")},
                                "last_checkpoint_donor_classes": last}
    z, k = summ["per_world"]["ZERO"], summ["per_world"]["CONST:5A"]
    sz, sk = z["specialist_of_world_share"] or 0, k["specialist_of_world_share"] or 0
    if z["donor_runs"] >= 10 and k["donor_runs"] >= 10 and sz >= 0.6 and sk >= 0.6:
        cls, lab = "SIGNAL", "TRACKS_WORLD"
    elif sz >= 0.6 and (k["donor_runs"] <= 3 or sk <= 0.2):
        cls, lab = "SIGNAL", "ZERO_LITERAL"
    elif z["donor_runs"] >= 10 and k["donor_runs"] >= 10 and sz <= 0.3 and sk <= 0.3:
        cls, lab = "CLEAN_NULL", "NO_SPECIALIZATION"
    else:
        cls, lab = "WEAK_SIGNAL", None
    if len(res) != len(jobs()):
        cls = "INVALID"
    summ.update({"classification": cls, "label": lab})
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
