"""WTP-05 analysis (PREREG_WTP05 s7.2, s7.3, s11): cell tables, kill rule, DEEP sizing, run-length curves,
primary verdict.
    python -m ensorain.wtp5.analyze5 screen            -> runs/wtp05/screen/analysis.json (+ survivors, deep plan)
    python -m ensorain.wtp5.analyze5 final             -> runs/wtp05/final_analysis.json (+ curves png)
"""
import collections
import glob
import json
import os
import sys

import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp05")
COMPOSED = ("A-R2", "A-R3", "B-R2", "B-R3", "N-R2", "N-R3")


def load(stage):
    rows = {}
    for f in sorted(glob.glob(os.path.join(ROOT, stage, "summaries_*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            key = (r["spec"], r["arm"], r["seed"])
            if key not in rows or r["evals"] >= rows[key]["evals"]:
                rows[key] = r
    return list(rows.values())


def metric(r):
    """Best certified rung (C: 1 if SWITCH_TRACKED else -1; search.py already encodes it so)."""
    return r["best_rung"]


def cells(rows):
    C = collections.defaultdict(list)
    for r in rows:
        C[(r["spec"], r["arm"])].append(r)
    out = {}
    for (spec, arm), rs in sorted(C.items()):
        m = np.array([metric(r) for r in rs])
        out[f"{spec}|{arm}"] = dict(spec=spec, arm=arm, n=len(rs), rungs=sorted(m.tolist()), mean=float(m.mean()),
                                    max=int(m.max()), n_at_max=int((m == m.max()).sum()),
                                    n_R2plus=int((m >= 2).sum()), evals=int(np.mean([r["evals"] for r in rs])),
                                    wall=float(np.mean([r["wall"] for r in rs])), thr=float(np.mean([r["evals"] / max(r["wall"], 1e-9) for r in rs])),
                                    done=sum(bool(r["done"]) for r in rs))
    return out


def ucb90(x, n_boot=4000, seed=0):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    bs = rng.choice(x, (n_boot, len(x)), replace=True).mean(1)
    return float(np.quantile(bs, 0.90))


def kill_rule(tab):
    survivors = []
    for k, c in tab.items():
        if c["arm"] == "base":
            continue
        b = tab.get(f"{c['spec']}|base")
        if b is None:
            continue
        up = ucb90(c["rungs"])
        new_rung = c["max"] > b["max"]
        ok = (up > b["mean"] and c["mean"] >= b["mean"]) or new_rung
        c["ucb90"], c["base_mean"], c["survives"] = up, b["mean"], bool(ok)
        if ok:
            survivors.append(k)
    survivors.sort(key=lambda k: (-(tab[k]["mean"] - tab[k]["base_mean"]), -tab[k]["n_at_max"] / tab[k]["n"]))
    survivors = survivors[:12]
    bases = sorted({f"{tab[k]['spec']}|base" for k in survivors})
    return survivors, bases


def deep_budget(tab, n_runs, hours=36, workers=3):
    thr = np.mean([c["thr"] for c in tab.values() if not c["spec"].startswith("C")])
    return int(min(400_000, hours * workers * 3600 * thr / max(1, n_runs))), float(thr)


def curves(rows, path_png=None):
    """Median best rung / archive size / best fitness vs evaluations per cell."""
    C = collections.defaultdict(list)
    for r in rows:
        C[(r["spec"], r["arm"])].append(r["telemetry"])
    out = {}
    for (spec, arm), tels in C.items():
        grid = sorted({t["evals"] for tel in tels for t in tel})
        def at(tel, e, key):
            v = [t[key] for t in tel if t["evals"] <= e]
            return v[-1] if v else None
        rows_ = []
        for e in grid[:: max(1, len(grid) // 40)]:
            br = [at(tel, e, "best_rung") for tel in tels]
            ar = [at(tel, e, "archive") for tel in tels]
            bf = [at(tel, e, "best_fit") for tel in tels]
            br = [x for x in br if x is not None]
            rows_.append(dict(evals=e, best_rung_median=float(np.median(br)) if br else None,
                              best_rung_max=max(br) if br else None,
                              share_R2plus=float(np.mean([x >= 2 for x in br])) if br else None,
                              archive_median=float(np.median([x for x in ar if x is not None])) if any(x is not None for x in ar) else None,
                              best_fit_median=float(np.median([x for x in bf if x is not None])) if any(x is not None for x in bf) else None))
        out[f"{spec}|{arm}"] = rows_
    if path_png:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        specs = sorted({k.split("|")[0] for k in out})
        fig, axes = plt.subplots(len(specs), 2, figsize=(11, 2.2 * len(specs)), squeeze=False)
        for i, spec in enumerate(specs):
            for k, rows_ in out.items():
                if k.split("|")[0] != spec:
                    continue
                e = [r["evals"] for r in rows_]
                axes[i, 0].plot(e, [r["best_rung_max"] for r in rows_], label=k.split("|")[1])
                axes[i, 1].plot(e, [r["archive_median"] or 0 for r in rows_], label=k.split("|")[1])
            axes[i, 0].set_title(f"{spec}: max best rung vs evals", fontsize=8)
            axes[i, 1].set_title(f"{spec}: median archive size vs evals", fontsize=8)
            axes[i, 0].legend(fontsize=6)
        fig.tight_layout()
        fig.savefig(path_png, dpi=90)
    return out


def verdict(screen_tab, deep_tab, admission, controls_ok, planted_ok):
    v = {}
    v["INSTRUMENT_FAILURE"] = (not planted_ok) or not any(a["label"] in ("DESERT_CONTROL", "GOLDILOCKS") for a in admission)
    final = deep_tab or screen_tab
    crossed = []
    for k, c in final.items():
        world = "-".join(c["spec"].split("-")[:2])
        if world in COMPOSED and c["spec"].endswith("desert") and c["arm"] != "base":
            b = final.get(f"{c['spec']}|base")
            if b and c["n_R2plus"] >= 4 and b["n_R2plus"] <= 1:
                crossed.append(k)
    attributed = [k for k in crossed if controls_ok.get(k)]
    v["DESERT_CROSSED"] = bool(attributed)
    v["desert_crossings_unattributed"] = [k for k in crossed if k not in attributed]
    step = []
    for world in COMPOSED:
        st = [c for c in final.values() if c["spec"] == f"{world}-stepping"]
        de = [c for c in final.values() if c["spec"] == f"{world}-desert"]
        yo = [c for c in final.values() if c["spec"] == f"{world}-yoked"]
        if st and max(c["n_R2plus"] for c in st) >= 3 and all(c["n_R2plus"] == 0 for c in de) and all(c["n_R2plus"] <= 1 for c in yo):
            step.append(world)
    v["STEPPING_STONES_REQUIRED"] = step
    if deep_tab:
        rises = [k for k, c in deep_tab.items() if k in screen_tab and c["max"] > screen_tab[k]["max"]]
        denser = [k for k, c in deep_tab.items() if k in screen_tab and c["max"] == screen_tab[k]["max"]
                  and c["n_at_max"] > screen_tab[k]["n_at_max"]]
        v["max_rung_rose"], v["denser_at_reached_rung"] = rises, denser
        v["RARITY_ONLY"] = (not rises) and bool(denser)
    else:
        v["RARITY_ONLY"] = None
    v["COMPOSITION_WALL_CONFIRMED"] = all(c["n_R2plus"] == 0 for c in final.values()
                                          if "-".join(c["spec"].split("-")[:2]) in COMPOSED and c["spec"].endswith("desert"))
    order = ["INSTRUMENT_FAILURE", "DESERT_CROSSED", "STEPPING_STONES_REQUIRED", "RARITY_ONLY", "COMPOSITION_WALL_CONFIRMED"]
    v["primary"] = next((o for o in order if v.get(o)), "NONE_OF_THE_PREREGISTERED_CLASSES")
    return v


if __name__ == "__main__":
    stage = sys.argv[1]
    if stage == "screen":
        rows = load("screen")
        tab = cells(rows)
        surv, bases = kill_rule(tab)
        n_runs = 8 * (len(surv) + len(bases))
        B, thr = deep_budget(tab, n_runs)
        cur = curves(rows, os.path.join(ROOT, "screen", "curves.png"))
        out = dict(n_runs=len(rows), cells=tab, survivors=surv, base_refs=bases, deep_budget=B, screen_thr=thr, curves=cur)
        json.dump(out, open(os.path.join(ROOT, "screen", "analysis.json"), "w"), indent=1)
        plan = dict(budget=B, log_every=max(2000, B // 40), seeds=list(range(51_000_001, 51_000_009)),
                    cells=[k.split("|") for k in surv + bases])
        json.dump(plan, open(os.path.join(os.path.dirname(__file__), "plans", "deep.json"), "w"), indent=1)
        for k, c in tab.items():
            print(f"{k:28s} rungs {c['rungs']} mean {c['mean']:.2f} R2+ {c['n_R2plus']} evals {c['evals']} "
                  f"{'SURVIVES' if c.get('survives') else ''}")
        print("survivors", surv, "bases", bases, "deep budget", B, "thr %.1f" % thr)
