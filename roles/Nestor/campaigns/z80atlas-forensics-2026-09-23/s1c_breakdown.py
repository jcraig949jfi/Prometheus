"""S1-C event-level breakdown: why predecessor events fail P-11, by atlas axis.

Categories (per predecessor-criterion event, majority over draws):
  P11_CAUSAL            passes P-11
  PARTIAL_COPY          fails C2 (cannot rebuild a random victim) but the donor authored
                        >= 90% of the donor-directed changes on the OBSERVED event: a real
                        partial copy riding on pre-existing similarity (fixture T5's shape)
  NOT_DONOR_AUTHORED    fails C2 and the donor authored < 90% of the observed directed
                        changes, or there were almost none: the match was made by
                        something other than the donor's writes (the post-interaction
                        mutation/recombination step, the victim itself, or it pre-existed)
  OTHER                 any remaining combination
-> S1C_BREAKDOWN.json
"""
import gzip, json, pathlib
from collections import Counter, defaultdict
HERE = pathlib.Path(__file__).resolve().parent
rows = {json.loads(l)["run_id"]: json.loads(l) for l in open(HERE / "P11_REASSAY.jsonl")}
cat = defaultdict(Counter)
few = Counter()
for rid, r in rows.items():
    axis = r["cell"]["atlas_axis"]
    for line in gzip.open(HERE / "replays" / "p11" / (rid + ".events.jsonl.gz"), "rt"):
        e = json.loads(line)
        if e["p11"]:
            c = "P11_CAUSAL"
        elif not e["C2"] and e["donor_authored_share_ordinary"] >= 0.9 and e["n_directed_ordinary"] >= 0.5 * e["n"]:
            c = "PARTIAL_COPY"
        elif not e["C2"]:
            c = "NOT_DONOR_AUTHORED"
        else:
            c = "OTHER"
        cat[axis][c] += 1
        cat["ALL"][c] += 1
        if e["n_directed_ordinary"] < 0.1 * e["n"]:
            few[axis] += 1
out = {"by_axis": {k: dict(v) for k, v in cat.items()},
       "events_with_under_10pct_directed_changes_on_observed_event": dict(few)}
(HERE / "S1C_BREAKDOWN.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
