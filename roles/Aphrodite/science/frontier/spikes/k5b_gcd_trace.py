"""SPIKE K5b -- why did GCD_RICH supplies never yield gcd(acc, {H})?
Re-runs the PRISTINE donor on GCD_RICH_2 and GCD_RICH_4 (identical K5
regime construction) and prints each certified class's member bodies and
the LGG outcome of every cross-class member pair (hole count)."""
import json, random, sys, os
from pathlib import Path
from collections import Counter
ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG)); os.environ["A17_FASTEVAL"] = "1"
import a17, identity as I, tier3d as T3D  # noqa: E401,E402
import k5_supply_vs_mechanism as K5  # noqa: E402
HERE = Path(__file__).resolve().parent
rows = json.loads((HERE / "K2_ADMISSIBLE_SOLVABILITY.json").read_text())["rows"]
pool = [dict(r, name=K5.fam_name(i)) for i, r in enumerate(rows)
        if r["Q2_size"] is not None and r["PRISTINE"]["solved"] + r["L1"]["solved"] > 0]
ng = [r for r in pool if not r["g1_body"]]; g1 = [r for r in pool if r["g1_body"]]; gcd = [r for r in ng if r["op"] == "gcd"]
rng = random.Random("APHRODITE/FRONTIER/K5/v1"); regimes = {}
for k in range(6):
    s = rng.sample(gcd, 7); regimes["GCD_RICH_%d" % k] = (s[:4], s[4:])
    s = rng.sample(ng, 7); regimes["NONG1_MIX_%d" % k] = (s[:4], s[4:])
    a, b = rng.sample(g1, 2), rng.sample(ng, 5); regimes["G1_PLUS_%d" % k] = (a + b[:2], b[2:])
a17.worker_init()
for key in ("GCD_RICH_2", "GCD_RICH_4"):
    obs, val = regimes[key]
    fams = [dict(f, role="OBSERVE", qualified_dev_size=f["Q2_size"]) for f in obs] + \
           [dict(f, role="VALIDATE", qualified_dev_size=f["Q2_size"]) for f in val]
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fams}
    print("==", key, "observe witnesses:", [(f["init"], f["body"], f["final"]) for f in obs])
    d = a17.donor(("K5-" + key, "P", 0, fams, specs))
    cls = d["trace"]["classes"]
    for c in cls:
        print("  class", c["families"], "members", len(c["member_bodies"]), c["member_bodies"][:8])
    holes = Counter()
    for i in range(len(cls)):
        for j in range(i + 1, len(cls)):
            for a in cls[i]["member_bodies"]:
                for b in cls[j]["member_bodies"]:
                    g, t = T3D.lgg(I.normalise(I.parse(a)), I.normalise(I.parse(b)))
                    holes["root-hole" if g[0].startswith("hole") else "%d-hole" % len(t)] += 1
    print("  cross-class LGG hole counts:", dict(holes), "derived:", [c["schema"] for c in d["trace"]["candidate_schemas"]])
