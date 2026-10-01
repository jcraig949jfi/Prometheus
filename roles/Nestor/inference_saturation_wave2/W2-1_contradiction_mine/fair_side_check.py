"""W2-1 check E: in X-A3-FAIR sweeps, which tape side do the sweeping state-free genomes copy from, versus the
Z-only genomes they replaced? Single-interaction P-11 assays only (no world run): zero entry state, 20 seeds,
donor at side 0 (victim side 1) vs donor at side 1 (victim side 0), exactly as run_fair.fair_assay but per side.
Genomes: the stored donor_profiles (first 20 distinct donors per checkpoint) of the sweep runs."""
import json, pathlib, sys, collections
HERE = pathlib.Path(__file__).resolve().parent
NEST = HERE.parents[1]
C = NEST / "campaigns"
for p in (NEST / "lib", C / "npe-w1-donor-discovery-2026-09-26/x_dd_dense_copy", C / "npe-w1-donor-discovery-2026-09-26/x_donor_discovery",
          C / "c9x-explore-2026-09-24/x_donor_swap", C / "z80atlas-verify-2026-09-22", C / "npe-arc3-2026-09-28/x_a3_fair"):
    sys.path.insert(0, str(p))
sys.dont_write_bytecode = True
import world, run_dc, run_ds, run_fair
world.z8 = run_dc.dense_z8()
CELLS = run_fair.CELLS
def side_rates(r, g, k=20):
    n = r.L; tl = world._pow2(2 * n); out = {}
    for side in (0, 1):
        hits = 0
        for i in range(k):
            ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
            res = world.p11.assay(world.z8, n=n, tape_len=tl, ga=ga, gb=gb, st_a=(None, 0, 0), st_b=(None, 0, 0),
                                  budget=r.t["slice"], ops_mask=r._ops_mask(), cmr=r.copy_mut, victim_side=1 - side,
                                  seed=("W2-1-side", g.hex(), i, side))
            hits += res["pass"]
        out[side] = hits / k
    return out
RES = C / "npe-arc3-2026-09-28/x_a3_fair/results"
targets = [("ZERO_ffa6_24000015", "ffa6"), ("ZERO_ffa6_24000003", "ffa6"), ("ZERO_ffa6_24000022", "ffa6"),
           ("CARRIED_ffa6_24000007", "ffa6"), ("CARRIED_7ae3_24000004", "7ae3"), ("CARRIED_ffa6_24000012", "ffa6")]
summary = []
for name, cell in targets:
    a = run_ds.cells()[CELLS[cell]]
    r = world.Runner(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
    d = json.loads((RES / (name + ".json")).read_text())
    tally = collections.Counter()
    for c in d["checkpoints"]:
        for h, prof in c["donor_profiles"].items():
            g = bytes.fromhex(h)
            sf = "R1" in prof and "R2" in prof
            if "Z" not in prof:
                continue
            s = side_rates(r, g)
            side = "0" if s[0] >= 0.5 and s[1] < 0.5 else "1" if s[1] >= 0.5 and s[0] < 0.5 else "both" if s[0] >= 0.5 else "neither"
            tally[("SF" if sf else "notSF", side)] += 1
    summary.append({"run": name, "tally": {"%s/%s" % k: v for k, v in sorted(tally.items())}})
    print(name, dict(tally), flush=True)
(HERE / "fair_side_check.json").write_text(json.dumps(summary, indent=1))
