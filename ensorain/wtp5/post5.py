"""WTP-05 post-run drivers (PREREG_WTP05 s8, s9): controls / RG / accounting / transfer / tensor-op readout on
elites, and reachability assays with named bottlenecks for composed deserts that stayed below R2.

    python -m ensorain.wtp5.post5 controls <stage> [--workers 3]   -> runs/wtp05/<stage>/controls.jsonl
    python -m ensorain.wtp5.post5 assays <stage> [--workers 3]     -> runs/wtp05/<stage>/assays.jsonl

Targets for controls: every run whose best certified rung is R2+, plus the best run of every cell (max
best_rung, then best_fit). The ablated genome is the run's FINAL elite (summary 'elite'); its own certified rung
at the end ('final_rung') is reported next to best_rung, because the two can differ (disclosed limitation).
The certifier gap is not computed here (no training-distribution accuracy on held-out seeds): reported None.
"""
import argparse
import copy
import json
import multiprocessing as mp
import os

import numpy as np

from . import ablate, analyze5, assays
from .tape import W

ROOT = analyze5.ROOT
TENSOR_OPS = ("LIN", "BILIN", "DOT")


def _admission():
    return {a["spec"]: a for a in json.load(open(os.path.join(ROOT, "admission.json")))}


def _desert_acc(g, spec, plasticity):
    return ablate._acc(g, ablate.make("-".join(spec.split("-")[:2]) + "-desert"),
                       [8_800_000 + i for i in range(6)], plasticity=plasticity)["acc"]


def tensor_readout(g, spec, plasticity, full_acc):
    """s8 non-tensor-native readout: ablate each LIN / BILIN / DOT node of the main graph (output -> zeros)."""
    out = []
    for i, nd in enumerate(g["nodes"]):
        if nd["op"] in TENSOR_OPS:
            h = copy.deepcopy(g)
            h["nodes"][i] = dict(op="CONST", inp=[], v=np.zeros(W))
            out.append(dict(node=i, op=nd["op"], drop=full_acc - _desert_acc(h, spec, plasticity)))
    n_mod = sum(1 for m in g["modules"] for nd in m["nodes"] if nd["op"] in TENSOR_OPS)
    return dict(n_tensor_main=len(out), n_tensor_in_modules=n_mod, ablations=out,
                tensor_necessary=any(x["drop"] >= 0.1 for x in out))


def _arrays(g):
    """JSON elite -> genome with numpy parameters (summaries round parameters to 4 dp)."""
    g = copy.deepcopy(g)
    for nd in g["nodes"] + [n for m in g["modules"] for n in m["nodes"]]:
        for k, v in nd.items():
            if k != "inp" and isinstance(v, list):
                nd[k] = np.array(v, float)
    return g


def elite(row, stage):
    """Exact final elite from the run's checkpoint when present; else the 4-dp JSON copy (flagged)."""
    from .search import Run
    p = os.path.join(ROOT, stage, "ckpt", f"{row['spec']}__{row['arm']}__{row['seed']}.pkl")
    if os.path.exists(p):
        return Run.load(p).pop[0]["g"], "ckpt"
    return _arrays(row["elite"]), "json_4dp"


def _control_job(a):
    row, null_share, stage = a
    os.nice(10) if os.nice(0) < 10 else None
    (g, src), spec, arm = elite(row, stage), row["spec"], row["arm"]
    plast = "L" in arm
    rec = dict(spec=spec, arm=arm, seed=row["seed"], best_rung=row["best_rung"], final_rung=row["final_rung"],
               evals=row["evals"], elite_source=src)
    if spec.startswith("C"):
        rec["note"] = "C: rung = SWITCH_TRACKED; only the plasticity controls apply"
    ctrl = ablate.controls(g, spec, plast)
    rec["controls"] = ctrl
    lin = g.get("lineage", {})
    rec["accounting"] = ablate.accounting(ctrl, null_share, archive_lineage=dict(lin, through_archive=lin.get("archive", 0) > 0))
    if row["best_rung"] >= 2 and not spec.startswith("C"):
        rec["transfer"] = ablate.transfer(g, spec, plast)
    if not spec.startswith("C"):
        rec["tensor"] = tensor_readout(g, spec, plast, ctrl["full"]["acc"])
    return rec


def targets(rows):
    t = {(r["spec"], r["arm"], r["seed"]): r for r in rows if r["best_rung"] >= 2}
    by = {}
    for r in rows:
        k = (r["spec"], r["arm"])
        if k not in by or (r["best_rung"], r["best_fit"] or -9) > (by[k]["best_rung"], by[k]["best_fit"] or -9):
            by[k] = r
    for r in by.values():
        t[(r["spec"], r["arm"], r["seed"])] = r
    return [r for r in t.values() if r.get("elite")]


def run_controls(stage, workers):
    adm = _admission()
    rows = analyze5.load(stage)
    tg = targets(rows)
    out = os.path.join(ROOT, stage, "controls.jsonl")
    done = set()
    if os.path.exists(out):
        done = {(r["spec"], r["arm"], r["seed"]) for r in map(json.loads, open(out))}
    jobs = [(r, adm.get(r["spec"], {}).get("best_bounded_null", 0.5) - 0.5, stage) for r in tg
            if (r["spec"], r["arm"], r["seed"]) not in done]
    print(f"controls {stage}: {len(jobs)} targets", flush=True)
    with mp.get_context("spawn").Pool(workers) as pool, open(out, "a") as fh:
        for rec in pool.imap_unordered(_control_job, jobs):
            fh.write(json.dumps(rec, default=lambda x: np.round(x, 4).tolist() if isinstance(x, np.ndarray) else x.item()) + "\n")
            fh.flush()
            print(f"  {rec['spec']} {rec['arm']} s{rec['seed']} rung {rec['best_rung']} RG {rec['controls']['RG']}", flush=True)


def bottlenecks(spec, rep, part, adm, tab):
    """Mechanical assignment by the assays.py docstring rules."""
    world = "-".join(spec.split("-")[:2])
    target = int(spec.split("-")[1][1])
    b = []
    if not adm.get(spec, {}).get("planted_ok", True):
        b.append("EXPRESSIBILITY")
    if rep["n_broken"] and rep["repaired_of_broken"] < rep["n_broken"] / 2:     # only edits that broke it count
        b.append("OPTIMIZATION")
    else:
        b.append("REACHABILITY")
        if part["recovered"] < part["n"] / 2:
            b.append("CREDIT")
    st = [c for c in tab.values() if c["spec"] == f"{world}-stepping"]
    yo = [c for c in tab.values() if c["spec"] == f"{world}-yoked"]
    at = lambda c: int((np.array(c["rungs"]) >= target).sum())
    if st and max(at(c) for c in st) >= 1 and all(at(c) <= 1 for c in yo):
        b.append("REWARD")
    de = [c for c in tab.values() if c["spec"] == spec]
    if any(c.get("max_best_fit", 0) >= 0.9 for c in de):
        b.append("DETECTION")
    if any(c.get("rising_at_end") for c in de):
        b.append("RESOURCE")
    return b


def _assay_job(spec):
    os.nice(10) if os.nice(0) < 10 else None
    d = os.path.join(ROOT, "assays_ckpt")
    os.makedirs(d, exist_ok=True)
    return spec, assays.repair_probability(spec, out_dir=d), assays.partial_seed(spec, out_dir=d)


def run_assays(stage, workers):
    adm = _admission()
    rows = analyze5.load(stage)
    tab = analyze5.cells(rows)
    for c in tab.values():
        rs = [r for r in rows if r["spec"] == c["spec"] and r["arm"] == c["arm"]]
        c["max_best_fit"] = max((r["best_fit"] or 0) for r in rs)
        # still rising: the run's current best rung was first reached in the last 40% of its evaluations
        c["rising_at_end"] = any(r["best_rung"] >= 0 and r["first_rung_at"].get(str(r["best_rung"]), r["first_rung_at"].get(r["best_rung"], 0)) >= 0.6 * r["evals"] for r in rs)
    failed = sorted({c["spec"] for c in tab.values() if c["spec"].endswith("desert")
                     and "-".join(c["spec"].split("-")[:2]) in analyze5.COMPOSED}
                    - {c["spec"] for c in tab.values() if c["n_R2plus"] > 0})
    out = os.path.join(ROOT, stage, "assays.jsonl")
    print(f"assays {stage}: {failed}", flush=True)
    with mp.get_context("spawn").Pool(workers) as pool, open(out, "a") as fh:
        for spec, rep, part in pool.imap_unordered(_assay_job, failed):
            rec = dict(spec=spec, repair=rep, partial=part, bottlenecks=bottlenecks(spec, rep, part, adm, tab))
            fh.write(json.dumps(rec, default=lambda x: x.item() if hasattr(x, "item") else str(x)) + "\n")
            fh.flush()
            print(f"  {spec} repaired {rep['repaired_of_broken']}/{rep['n_broken']} broken partial {part['recovered']}/{part['n']} -> {rec['bottlenecks']}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("controls", "assays"))
    ap.add_argument("stage")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    (run_controls if a.what == "controls" else run_assays)(a.stage, a.workers)
