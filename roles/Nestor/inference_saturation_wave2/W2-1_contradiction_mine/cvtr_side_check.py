"""W2-1 check G: Artemis CVT-R rows for Nestor donors (roles/Artemis/challenge/cvtr_nestor/results/ROWS.jsonl),
split by the P-11 certified side. Read-only. Verifies a sibling agent's tabulation."""
import json, pathlib, collections
P = pathlib.Path(__file__).resolve().parents[3] / "Artemis/challenge/cvtr_nestor/results/ROWS.jsonl"
rows = [json.loads(l) for l in P.read_text().splitlines() if l.strip()]
t = collections.Counter()
for r in rows:
    cs = r["P11"]["certified_sides"]
    if not r["P11"]["certified"]:
        t[("not_certified", r["CVTR_accept"])] += 1; continue
    key = "both" if len(cs) == 2 else "side%s" % cs[0]
    t[(key, r["CVTR_accept"])] += 1
for k in sorted(t, key=str): print(k, t[k])
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps({str(k): v for k, v in t.items()}, indent=1))
