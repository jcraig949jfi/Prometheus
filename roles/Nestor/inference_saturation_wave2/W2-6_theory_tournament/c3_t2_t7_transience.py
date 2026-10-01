"""W2-6 check C3 (T2 vs T7 on transience): what kind of event is a "transient" internalization?

T2 (steady demand -> steady positive selection) is said to be strained because 4/8 C-A3 events are gone by epoch 2000;
T7 reads transience as drift balance. The two readings differ in WHERE loss happens: T2-with-strong-selection forbids
loss of a variant that has reached a large share while its competent population persists; demographic (T7) loss is
concentrated in variants that never left low copy number. Read-only over the C-A3 per-run checkpoint JSON.
Also reports the selection coefficient implied by X-A3-WITHDRAW's sweep, and the T2-with-that-s probability that a
variant first seen at n copies is lost (Haldane, P(loss) ~ exp(-2 s n), generation := epoch; an approximation only).
Output: c3_t2_t7_transience.json
"""
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
CA3 = HERE.parents[1] / "campaigns" / "npe-arc3-2026-09-28" / "c_a3_internalize"
v = json.load(open(CA3 / "VERDICT.json"))
ev = {(c, s) for c, s in v["event_runs"]}
events = []
for f in sorted((CA3 / "results").glob("*.json")):
    d = json.loads(f.read_text())
    if (d["cell"], d["seed"]) not in ev:
        continue
    cps = d["checkpoints"]
    sh = [(c["epoch"], c["free"] / c["competent"] if c["competent"] else 0.0, c["free"], c["competent"], c["L_share"]) for c in cps]
    first = next(x for x in sh if x[2] > 0)
    peak = max(sh, key=lambda x: x[1])
    last = sh[-1]
    seen = [x for x in sh if x[2] > 0]
    gaps = sum(1 for a, b in zip(sh, sh[1:]) if a[2] > 0 and b[2] == 0)
    kind = ("SWEPT_PERSISTS" if peak[1] >= 0.5 and last[2] > 0 else
            "SWEPT_THEN_COMPETENCE_COLLAPSE" if peak[1] >= 0.5 and last[3] <= 5 else
            "SWEPT_THEN_LOST" if peak[1] >= 0.5 else
            "LOW_COPY_FLICKER" if peak[1] < 0.2 else "INTERMEDIATE")
    events.append({"cell": d["cell"], "seed": d["seed"], "first_seen": first[0], "first_count": first[2],
                   "peak_share": round(peak[1], 3), "peak_count": peak[2], "peak_epoch": peak[0],
                   "final_free": last[2], "final_competent": last[3], "final_L": last[4],
                   "checkpoints_with_free": len(seen), "disappearances": gaps, "kind": kind,
                   "max_count_ever": max(x[2] for x in sh)})
# selection strength implied by X-A3-WITHDRAW ABRUPT: robust share 0.22 -> 0.96 within ~100 epochs
logit = lambda p: math.log(p / (1 - p))
s_wd = (logit(0.96) - logit(0.22)) / 100.0
# T2-with-s_wd probability that each low-copy appearance is lost (independent appearances = separated by a zero)
p_all_lost = 1.0
detail = []
for e in events:
    if e["kind"] != "LOW_COPY_FLICKER":
        continue
    d = json.loads((CA3 / "results" / ("%s_%d.json" % (e["cell"], e["seed"]))).read_text())
    runs, cur = [], 0
    for c in d["checkpoints"]:
        if c["free"] > 0:
            cur = max(cur, c["free"])
        elif cur:
            runs.append(cur); cur = 0
    if cur:
        runs.append(cur)
    lost = runs if e["final_free"] == 0 else runs[:-1]
    for n in lost:
        pl = math.exp(-2 * s_wd * n)
        p_all_lost *= pl
        detail.append({"run": e["seed"], "max_count": n, "P_loss_under_T2_s": round(pl, 3)})
kinds = {}
for e in events:
    kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
out = {"events": events, "kinds": kinds, "s_implied_by_withdraw_per_epoch": round(s_wd, 4),
       "low_copy_losses": detail, "P_all_low_copy_losses_under_T2_s": p_all_lost,
       "caveats": ["free counts are single assay calls per checkpoint (no repeatability re-assay; RT B6)",
                   "generation := epoch is an assumption; s from a different arm/world (X-A3-WITHDRAW 7ae3)",
                   "appearances within a run are not independent if the same lineage persists below detection"]}
(HERE / "c3_t2_t7_transience.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
