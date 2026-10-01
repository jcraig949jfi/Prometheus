"""Task 2 table from out/tune_part1.json + out/tune_part2.json."""
from r_common import *
rows_ = []
for f in ("tune_part1.json", "tune_part2.json"):
    p = OUT / f
    if p.exists():
        rows_ += json.load(open(p))["rows"]
print(f"{'tag':10s} {'cell':8s} {'fam':5s} nz lb dl  native  " + " ".join(f"{k:>8s}" for k in ("lat-1", "lat+1", "lat+2", "delta-2", "delta-1", "delta+1", "delta+2")) + "  best  disc   confirm[lo,hi]")
n_conf = n_conf_lo = n_disc = 0
for r in rows_:
    v = r["var"]
    cells = " ".join(f"{v[k]['gain'][0]:+8.3f}" if k in v else f"{'-':>8s}" for k in ("lat-1", "lat+1", "lat+2", "delta-2", "delta-1", "delta+1", "delta+2"))
    c = r.get("confirm")
    cs = f"{c['gain'][0]:+.3f} [{c['gain'][1]:+.3f},{c['gain'][2]:+.3f}]" if c else ""
    print(f"{r['tag']:10s} {r['cell'][:8]} {r['fam']:5s} {r['noise']:2d} {r['lat_base']:2d} {r['delta']:2d}  {r['native'][0]:.3f}  {cells}  {r['best']:7s} {r['best_gain']:+.3f}  {cs}")
    n_disc += r["best_gain"] >= .03
    if c and c["gain"][0] >= .03:
        n_conf += 1
        n_conf_lo += c["gain"][1] > 0
comm = [r for r in rows_ if r["fam"] != "HOLD"]
print(f"\nchampions swept: {len(rows_)} (comm {len(comm)}, HOLD {len(rows_) - len(comm)})")
print(f"discovery best-of-variants gain >= .03: {n_disc}; confirmed point >= .03: {n_conf}; of those lo99 > 0: {n_conf_lo}")
d = [(r["best_gain"], r["confirm"]["gain"][0]) for r in rows_ if r.get("confirm")]
if d:
    print("winner's curse: mean discovery gain of confirmed-attempted", round(np.mean([a for a, b in d]), 3), "-> mean confirmation", round(np.mean([b for a, b in d]), 3))
print("max |gain| over all HOLD variants:", max(abs(x["gain"][0]) for r in rows_ if r["fam"] == "HOLD" for x in r["var"].values()))
print("comm champions: median best discovery gain", np.median([r["best_gain"] for r in comm]))
