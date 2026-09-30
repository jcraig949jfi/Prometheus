"""W3 -- proposed repair (NOT frozen, forensic): apply RULER v2's own re-expression
closure to the STRUCTURAL relations too: rel*(S, G) = OR over r in reexpressions(G) of
relations(S, r). Scores the adversarial set, the A19 panel and the C2 selections."""
import json, os, sys
from pathlib import Path
os.environ.setdefault("A17_FASTEVAL", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "science" / "compounding" / "rb1"))
sys.path.insert(0, str(ROOT / "engine")); sys.path.insert(0, str(ROOT / "engine" / "accel"))
import ruler_v2 as R  # noqa: E402
G1 = "(acc + {H})"
def rel_closed(s, g=G1):
    out = {"REFINES": False, "COMPOSES": False, "EQUAL": False}
    for r in R.reexpressions(g):
        x = R.relations(s, r)
        for k in out:
            out[k] = out[k] or x[k]
    return out
panel = json.loads((ROOT / "engine/A19_C2/A18_PANEL_2026-09-28.json").read_text())["panel"]
donors = [json.loads(l) for l in (ROOT / "engine/A19_C2/A18_DONORS_2026-09-28.jsonl").read_text().splitlines()]
adv = [r["schema"] for r in json.loads((HERE / "W3_ADVERSARIAL_W5.json").read_text())]
res = {"reexpressions_of_G1": R.reexpressions(G1), "panel": {}, "selections": {}, "adversarial": {}}
for k, s in panel.items():
    res["panel"][k] = {"schema": s, "literal": R.relations(s, G1), "closed": rel_closed(s)}
for d in donors:
    if d["selected_schema"]:
        s = d["selected_schema"]
        res["selections"]["%s/%s" % (d["catalog"], d["arm"])] = {"schema": s, "literal": R.relations(s, G1), "closed": rel_closed(s)}
for s in adv:
    a, b = R.relations(s, G1), rel_closed(s)
    if a != b:
        res["adversarial"][s] = {"literal": a, "closed": b}
(HERE / "W3_RELCLOSURE.json").write_text(json.dumps(res, indent=1))
for k, v in res["panel"].items(): print("panel", k, v)
for k, v in res["selections"].items():
    if v["literal"] != v["closed"]: print("sel", k, v)
for k, v in res["adversarial"].items(): print("adv", k, v)
