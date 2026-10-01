"""W2-1 check I: X-A3-WITHDRAW sweep timing. For the 12 established runs per arm, pooled robust share among sampled
founder genomes at each checkpoint (epochs 300, 400, 500, ..., 2000). Tests U-C5's 'within 100 epochs' against FINDINGS'
'within ~1700 epochs'. Read-only."""
import json, pathlib, collections
R = pathlib.Path(__file__).resolve().parents[2] / "campaigns/npe-arc3-2026-09-28/x_a3_withdraw/results"
by = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
nrun = collections.Counter()
for p in sorted(R.glob("*.json")):
    r = json.loads(p.read_text())
    cps = {c["epoch"]: c for c in r["checkpoints"]}
    c300 = cps.get(300)
    if not c300 or c300["sampled"] == 0:
        continue
    nrun[r["arm"]] += 1
    for e, c in cps.items():
        if e >= 300 and c["sampled"]:
            by[r["arm"]][e][0] += c["robust"]; by[r["arm"]][e][1] += c["sampled"]
out = {}
for arm in sorted(by):
    out[arm] = {e: round(a / b, 3) for e, (a, b) in sorted(by[arm].items())}
    print(arm, "runs", nrun[arm], out[arm])
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
