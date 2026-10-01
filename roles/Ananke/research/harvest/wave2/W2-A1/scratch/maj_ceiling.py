"""Bayes-optimal MAJ accuracy when each of 5 sensors is (a) unseen w.p. m=(1-p)^cue_len (SENSE not
latched for asleep sites), else (b) correct w.p. .7. Optimal rule = majority of SEEN sensors, ties -> .5.
Compare with the INTEGRATION bar (lo99 > .70) and count C1 MAJ evolve rows per wake regime."""
import itertools, math, gzip, json, pathlib, collections
def ceil_(m, q=0.7, k=5):
    tot = 0.0
    for states in itertools.product((0, 1, -1), repeat=k):   # 0 unseen, 1 correct, -1 wrong
        pr = 1.0
        for s in states: pr *= m if s == 0 else (1 - m) * (q if s == 1 else 1 - q)
        v = sum(states); tot += pr * (1.0 if v > 0 else 0.5 if v == 0 else 0.0)
    return tot
for p in (None, 0.8, 0.5):
    m = 0.0 if p is None else (1 - p) ** 2
    single = (1 - m) * 0.7 + m * 0.5
    print(f"wake {'sync' if p is None else 'async p=%.1f' % p}: miss={m:.3f}  single-sensor ceiling={single:.3f}  5-sensor Bayes ceiling={ceil_(m):.3f}")
ROOT = pathlib.Path(__file__).resolve().parents[7]
R = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
c = collections.Counter(); best = collections.defaultdict(float)
for r in R:
    if r["kind"] == "evolve" and r["env"]["family"] == "MAJ":
        ph = r["physics"]; k = "sync" if ph["update_mode"] == "sync" else f"async{ph['update_p']}"
        c[k] += 1; best[k] = max(best[k], r["result"]["held"]["lo99"])
print("MAJ evolve rows by wake regime:", dict(c), " best lo99:", {k: round(v, 3) for k, v in best.items()})
