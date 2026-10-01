"""W2-2 a5: C-A3-INTERNALIZE takeover runs: do internalizers differ from the near-misses before the event? Read-only.
Records: cell, seed, depth, d0_epoch, d0_free, checkpoints[{epoch, L_share, competent, free, free_in_L}] (every 100 epochs).
python -B a5_ca3.py -> a5_ca3.json
"""
import json, glob, pathlib, statistics as st
HERE = pathlib.Path(__file__).resolve().parent
C = HERE.parents[1] / "campaigns" / "npe-arc3-2026-09-28" / "c_a3_internalize" / "results"
R = [json.load(open(f)) for f in sorted(glob.glob(str(C / "*.json")))]
rows = []
for r in R:
    ck = r["checkpoints"]
    if not ck or any(r["d0_free"]):
        continue
    tko = next((c["epoch"] for c in ck if c["L_share"] >= 0.5), None)
    if tko is None:
        continue
    ev = next((c["epoch"] for c in ck if c["free_in_L"] > 0), None)
    upto = ev if ev is not None else 10 ** 9
    pre = [c for c in ck if c["epoch"] < upto and c["epoch"] >= tko]
    allpost = [c for c in ck if c["epoch"] >= tko]
    expo_comp = sum(c["competent"] * c["L_share"] for c in pre) * 100   # competent-in-L organism-epochs (approx: competent x L share)
    expo_L = sum(256 * c["L_share"] for c in pre) * 100
    rows.append(dict(cell=r["cell"], seed=r["seed"], depth=r["depth"], d0=r["d0_epoch"], takeover=tko, event=ev,
                     cls="EVENT" if ev is not None else "NEARMISS",
                     comp_at_takeover=next(c["competent"] for c in ck if c["epoch"] == tko),
                     comp_median_post=st.median([c["competent"] for c in allpost]) if allpost else None,
                     comp_series=[(c["epoch"], c["competent"], round(c["L_share"], 2), c["free_in_L"]) for c in ck if c["epoch"] >= r["d0_epoch"]][:22],
                     L_min_post=min(c["L_share"] for c in allpost),
                     exposure_comp_pre=round(expo_comp), exposure_L_pre=round(expo_L),
                     zero_comp_checkpoints_post=sum(c["competent"] == 0 for c in allpost), n_post=len(allpost)))
out = dict(rows=rows)
for cls in ("EVENT", "NEARMISS"):
    sub = [x for x in rows if x["cls"] == cls]
    out[cls] = dict(n=len(sub), by_cell={c: sum(x["cell"] == c for x in sub) for c in ("7ae3", "ffa6")},
                    comp_median_post=[x["comp_median_post"] for x in sub],
                    depth=[x["depth"] for x in sub], exposure_comp_pre=[x["exposure_comp_pre"] for x in sub],
                    takeover_minus_d0=[x["takeover"] - x["d0"] for x in sub])
json.dump(out, open(HERE / "a5_ca3.json", "w"), indent=1)
for x in rows:
    print(x["cell"], x["seed"], x["cls"], "depth", x["depth"], "d0", x["d0"], "tko", x["takeover"], "ev", x["event"], "compMedPost", x["comp_median_post"],
          "expo", x["exposure_comp_pre"], "zeroComp", x["zero_comp_checkpoints_post"], "/", x["n_post"], "Lmin", x["L_min_post"])
    print("    ", x["comp_series"][:14])
