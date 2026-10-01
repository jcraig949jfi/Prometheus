"""W2-34 static test: is ffa6 27000052's post-1600 'competence collapse' visible in a ruler-independent quantity?
Read-only over committed X-MAT replays (npe-frontier-2026-09-30/x_mat_internalize/results/*.json), which are bit-identical
replays of the C-A3 runs (replay_identical) carrying z8taint material tags. MUT = bytes written by the world's mutation
step after D0 (copies keep their tag). Under no copying MUT share only rises toward saturation; self-copying by a
sweeping copier lowers it. The tags are computed from world dynamics, not from any competence screen.
Intervals = consecutive 100-epoch checkpoints. Classes by the zero-context screen count at BOTH ends:
BLANK (competent == 0), COMP (competent >= 50), else MIXED. ffa6 only (7ae3 has ~0 opcode mutation, D4).
Run 52 is excluded from the reference classes. python -B mut_regime.py -> mut_regime.json"""
import json, pathlib, statistics as st, random
HERE = pathlib.Path(__file__).resolve().parent
R = HERE.parents[1] / "campaigns/npe-frontier-2026-09-30/x_mat_internalize/results"
LO, HI = 0.45, 0.72                     # matched MUT level window (run 52 post-1600 spans 0.54-0.65)
rows = []
for p in sorted(R.glob("ffa6_*.json")):
    r = json.loads(p.read_text())
    cps = {c["epoch"]: c for c in r["record"]["checkpoints"]}
    tg = r["tags"]
    for a, b in zip(tg, tg[1:]):
        if b["epoch"] - a["epoch"] != 100:
            continue
        m0 = a["all"]["MUT"] / a["all"]["bytes"]
        m1 = b["all"]["MUT"] / b["all"]["bytes"]
        c0, c1 = cps[a["epoch"]]["competent"], cps[b["epoch"]]["competent"]
        cls = "BLANK" if c0 == 0 and c1 == 0 else "COMP" if c0 >= 50 and c1 >= 50 else "MIXED"
        rows.append({"run": r["seed"], "t0": a["epoch"], "m0": round(m0, 4), "dm": round(m1 - m0, 4), "c0": c0, "c1": c1,
                     "L0": cps[a["epoch"]]["L_share"], "orgs": a["all"]["orgs"], "cls": cls})
ref = [x for x in rows if x["run"] != 27000052 and LO <= x["m0"] <= HI]
r52 = [x for x in rows if x["run"] == 27000052]
post = [x for x in r52 if x["t0"] >= 1600]
win = [x for x in r52 if 1200 <= x["t0"] < 1600]


def summ(xs):
    d = [x["dm"] for x in xs]
    runs = sorted({x["run"] for x in xs})
    per_run = [st.mean(x["dm"] for x in xs if x["run"] == q) for q in runs]
    return {"n_intervals": len(d), "n_runs": len(runs), "mean_dm": round(st.mean(d), 4) if d else None,
            "median_dm": round(st.median(d), 4) if d else None, "frac_dm_negative": round(sum(v < 0 for v in d) / len(d), 3) if d else None,
            "min": min(d) if d else None, "max": max(d) if d else None,
            "per_run_means": [round(v, 4) for v in per_run]}


out = {"window": [LO, HI], "ref": {k: summ([x for x in ref if x["cls"] == k]) for k in ("BLANK", "COMP", "MIXED")},
       "r52_window_1200_1600": {"intervals": win, **summ(win)}, "r52_post_1600": {"intervals": post, **summ(post)}}
# level-adjusted: OLS dm = a + b*m0 within each reference class; residual of run-52 post intervals
for k in ("BLANK", "COMP"):
    xs = [x for x in ref if x["cls"] == k]
    mx, my = st.mean(x["m0"] for x in xs), st.mean(x["dm"] for x in xs)
    b = sum((x["m0"] - mx) * (x["dm"] - my) for x in xs) / sum((x["m0"] - mx) ** 2 for x in xs)
    a = my - b * mx
    res = [x["dm"] - (a + b * x["m0"]) for x in xs]
    sd = st.pstdev(res)
    pr = [x["dm"] - (a + b * x["m0"]) for x in post]
    out["fit_" + k] = {"a": round(a, 4), "b": round(b, 4), "resid_sd": round(sd, 4),
                       "r52_post_pred": [round(a + b * x["m0"], 4) for x in post],
                       "r52_post_resid_mean": round(st.mean(pr), 4), "r52_post_resid_mean_in_sd_of_mean": round(st.mean(pr) / (sd / len(pr) ** .5), 2)}
# run-level permutation: is run 52's post-1600 mean dm (4 intervals) more like a random 4-interval block of BLANK or COMP runs?
rng = random.Random(34)
pm = st.mean(x["dm"] for x in post)
for k in ("BLANK", "COMP"):
    xs = [x for x in ref if x["cls"] == k]
    byrun = {}
    for x in xs:
        byrun.setdefault(x["run"], []).append(x["dm"])
    blocks = [v[i:i + 4] for v in byrun.values() for i in range(len(v) - 3)]   # consecutive 4-interval blocks within one run
    ms = [st.mean(bk) for bk in blocks]
    out["blocks_" + k] = {"n_blocks": len(ms), "P(block_mean >= r52)": round(sum(m >= pm for m in ms) / len(ms), 3) if ms else None,
                          "P(block_mean <= r52)": round(sum(m <= pm for m in ms) / len(ms), 3) if ms else None,
                          "block_means_q10_q50_q90": [round(sorted(ms)[int(q * (len(ms) - 1))], 4) for q in (.1, .5, .9)] if ms else None}
out["r52_post_mean_dm"] = round(pm, 4)
out["all_rows"] = rows
(HERE / "mut_regime.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "all_rows"}, indent=1))
