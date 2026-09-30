"""SPIKE K11 (after C1 = UNTESTABLE-supply): which compositions of which
inherited schemas yield T4-ADMISSIBLE task families at all? Task-side only
(tribunal_t4.family_profile on the witness; no recipient). For G1 and for 40
candidate single-hole schemas (NEW_FINAL vs G1): per composition, sample up to
12 accumulating W5 instances x init {0,1} x 3 finals, and report the admissible
rate and the dominant rejection reasons. Forensic, not a disposition."""
import json
import os
import random
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENG = HERE.parents[2] / "engine"
sys.path.insert(0, str(ENG))
os.environ["A17_FASTEVAL"] = "1"
import a18  # noqa: E402
from a18 import G, T3D, I  # noqa: E402

FINALS = ["acc", "(acc + first)", "(acc % last)"]


def job(args):
    a18.worker_init()
    import ruler_v2 as R
    import tribunal_t4 as T4
    owner, comp_schema = args
    rng = random.Random(comp_schema)
    inst = [b for b in T3D.instantiate(comp_schema) if R.accumulating(b)]
    rng.shuffle(inst)
    n = ok = 0
    reasons = Counter()
    for b in inst[:12]:
        for init in G.H1_SPACE:
            for f in FINALS:
                prof = T4.family_profile(("fold", init, b, f))
                n += 1
                ok += prof["admissible"]
                for x in prof["reasons"]:
                    reasons[x] += 1
    return {"owner": owner, "composition": comp_schema, "n": n, "admissible": ok,
            "rate": ok / n if n else 0.0, "reasons": dict(reasons.most_common(3))}


if __name__ == "__main__":
    import ruler_v2 as R
    a18.use_world("W5")
    sp, tsp = R.span_of_schema(a18.G1), R.traj_span(R.reexpression_bodies(a18.G1))
    rng = random.Random(I._seed("APHRODITE/A18/K11/SCHEMAS/v1"))
    owners, seen = {"G1": a18.G1}, {a18.G1}
    while len(owners) < 41:
        s = a18._random_schema(rng)
        if not s or s in seen:
            continue
        seen.add(s)
        v = R.verdict_full(s, a18.G1, sp, tsp)
        if v["NEW_FINAL"] and v["accumulating"] >= 20 and len(a18.compositions(s)) >= 20:
            owners["S%02d" % len(owners)] = s
    jobs = [(k, w) for k, s in owners.items() for w in a18.compositions(s)]
    with ProcessPoolExecutor(int(os.environ.get("K11_WORKERS", "6")), initializer=a18.worker_init) as ex:
        rows = list(ex.map(job, jobs, chunksize=4))
    summ = {}
    for k, s in owners.items():
        rr = [r for r in rows if r["owner"] == k]
        good = [r for r in rr if r["rate"] >= 0.25]
        summ[k] = {"schema": s, "compositions": len(rr), "admissible_families": sum(r["admissible"] for r in rr),
                   "sampled": sum(r["n"] for r in rr), "compositions_rate>=0.25": len(good),
                   "mean_rate": round(sum(r["rate"] for r in rr) / max(1, len(rr)), 3)}
    (HERE / "K11_ADMISSIBLE_COMPOSITIONS.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1))
    for k, v in sorted(summ.items(), key=lambda kv: -kv[1]["mean_rate"]):
        print(k, v)
    g1 = sorted([r for r in rows if r["owner"] == "G1"], key=lambda r: -r["rate"])
    print("G1 best compositions:", [(r["composition"], round(r["rate"], 2)) for r in g1[:12]])
