"""W2-1 check C: re-express the C-A3 internalization hazard (U-T5) with exposure measured in COMPETENT-genome
checkpoints of the founder lineage instead of L organism-epochs. Read-only over c_a3_internalize/results.
Exposure: from the first checkpoint with L_share >= 0.5 until (excluding) the first checkpoint with free_in_L > 0,
sum of competent * L_share (competent is a distinct-genome count of zero-state COMPETENT live genomes; L_share a
population share) -- a proxy for copy-capable founder-lineage material. L organism-epochs = sum(L_share*256*100).
"""
import json, pathlib
R = pathlib.Path(__file__).resolve().parents[2] / "campaigns/npe-arc3-2026-09-28/c_a3_internalize/results"
res = {"7ae3": [0, 0, 0.0, 0.0], "ffa6": [0, 0, 0.0, 0.0]}  # runs, events, exp_comp, exp_orgepochs
rows = []
for p in sorted(R.glob("*.json")):
    r = json.loads(p.read_text())
    if not r["d0_free"] or any(r["d0_free"]):
        continue
    cps = r["checkpoints"]
    i = next((k for k, c in enumerate(cps) if c["L_share"] >= 0.5), None)
    if i is None:
        continue
    ec = eo = 0.0; ev = False
    for c in cps[i:]:
        if c["free_in_L"] > 0:
            ev = True; break
        ec += c["competent"] * c["L_share"]; eo += c["L_share"] * 256 * 100
    x = res[r["cell"]]; x[0] += 1; x[1] += ev; x[2] += ec; x[3] += eo
    rows.append((r["cell"], r["seed"], ev, round(ec, 1), int(eo)))
for row in rows: print(row)
for cell, (n, e, ec, eo) in res.items():
    print(cell, "takeover runs", n, "events", e, "exp_competent_cp", round(ec, 1), "exp_org_epochs", int(eo),
          "haz_comp", (e / ec if ec else None), "haz_org", (e / eo if eo else None))
a, b = res["ffa6"], res["7ae3"]
print("ratio ffa6/7ae3  competent-exposure:", (a[1] / a[2]) / (b[1] / b[2]), " org-epoch exposure:", (a[1] / a[3]) / (b[1] / b[3]))
