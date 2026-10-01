"""Prediction from engine semantics: SENSE is read only by AWAKE sites (engine.py:301-319, 369) and is
not latched. A cue of cue_len ticks at a sensor with wake prob p is never seen w.p. (1-p)^cue_len, and
that trial can score at most 0.5 in expectation. Ceiling (single sensor) = 1 - 0.5*(1-p)^cue_len.
Check: no evolve/transfer row may exceed the ceiling by more than sampling error."""
import gzip, json, collections, pathlib, math
ROOT = pathlib.Path(__file__).resolve().parents[7]
R = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
c = collections.defaultdict(list)
for r in R:
    ph, env = r["physics"], r["env"]
    if r["kind"] not in ("evolve", "transfer") or ph["update_mode"] != "async": continue
    if env["family"] not in ("HOLD", "RELAY", "FLIP"): continue
    p = ph["update_p"]; cl = env["cue_len"]
    ceil_ = 1 - 0.5 * (1 - p) ** cl
    c[(env["family"], p)].append((r["result"]["held"]["acc"], r["result"]["held"]["hi99"], ceil_, r["cell_id"], r["wave"]))
for k in sorted(c):
    v = c[k]; mx = max(v)
    over = [x for x in v if x[0] > x[2] + 0.02]
    print(k, "n", len(v), "max held acc %.3f (cell %s %s)" % (mx[0], mx[3], mx[4]), "ceiling %.3f" % mx[2], "rows above ceiling+.02:", len(over))
# sync period 2 ceiling: cue_len 2 always overlaps one even tick -> no cue loss
