"""Extract empirical SO(even) strata for the RMT simulation."""
import duckdb, json, numpy as np
from collections import defaultdict
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "charon.duckdb"

con = duckdb.connect(str(DB), read_only=True)
rows = con.execute("""
    SELECT ec.lmfdb_iso, ec.conductor, ec.rank, oz.zeros_vector[21] as root_num
    FROM elliptic_curves ec
    JOIN object_zeros oz ON ec.object_id = oz.object_id
    WHERE oz.zeros_vector IS NOT NULL AND oz.n_zeros_stored >= 20
    ORDER BY ec.object_id
""").fetchall()
con.close()

seen = set()
so_even = []
for iso, cond, rank, rn in rows:
    if iso in seen:
        continue
    seen.add(iso)
    if float(rn) == 1.0:
        so_even.append({"conductor": int(cond), "rank": int(rank or 0)})

by_cond = defaultdict(lambda: {"r0": 0, "r2": 0})
for d in so_even:
    if d["rank"] == 0:
        by_cond[d["conductor"]]["r0"] += 1
    elif d["rank"] == 2:
        by_cond[d["conductor"]]["r2"] += 1

eligible = []
for c, counts in sorted(by_cond.items()):
    total = counts["r0"] + counts["r2"]
    if total >= 5 and counts["r0"] > 0 and counts["r2"] > 0:
        eligible.append({"conductor": c, "n_r0": counts["r0"], "n_r2": counts["r2"]})

print(f"Eligible strata: {len(eligible)}")
print(f"Total rank-0: {sum(s['n_r0'] for s in eligible)}")
print(f"Total rank-2: {sum(s['n_r2'] for s in eligible)}")
sizes = [s["n_r0"] + s["n_r2"] for s in eligible]
r2s = [s["n_r2"] for s in eligible]
print(f"Strata sizes: min={min(sizes)}, max={max(sizes)}, median={np.median(sizes):.0f}")
print(f"Rank-2 per stratum: min={min(r2s)}, max={max(r2s)}, median={np.median(r2s):.0f}")

out = Path(__file__).parent.parent / "data" / "empirical_strata_so_even.json"
with open(out, "w") as f:
    json.dump(eligible, f)
print(f"Saved to {out}")
