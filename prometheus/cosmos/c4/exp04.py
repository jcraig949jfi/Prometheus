"""EXP-04: LOCAL SUFFICIENCY (exploratory; prereg roles/Cosmos/c4/prereg/EXP-04_LOCAL_SUFFICIENCY.md).

Per discovery world already labelled in EXP-01..03: fit the nonlinear one-step surrogate through LocalProbe and
compose it by simulation into a predicted linear-decoder accuracy (sysid_surrogate; zero label-fitted parameters).
Runs under prometheus.cosmos.supervise (spawn-safe, progress-watched):

    python -m prometheus.cosmos.supervise launch <rundir> --stall 900 -- \
        python -m prometheus.cosmos.c4.exp04 run <rundir> [workers]
    python -m prometheus.cosmos.c4.exp04 analyse <rundir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

RESULTS = Path(__file__).resolve().parents[3] / "roles" / "Cosmos" / "c4" / "results"
SOURCES = {"EXP-01": "EXP-01_discovery_b0.jsonl", "EXP-02": "EXP-02_discovery_b1_Q.jsonl",
           "EXP-03": "EXP-03_phase_b2.jsonl"}
V = 4
MIN_EXCESS = 0.10
RHO_MIN, BA_MIN = 0.70, 0.75


def excess(acc):
    return (np.asarray(acc, float) - 1.0 / V) / (1.0 - 1.0 / V)


def jobs():
    out = []
    for src, f in SOURCES.items():
        for x in (RESULTS / f).read_text().splitlines():
            if x.strip():
                r = json.loads(x)
                out.append({"key": f"{src}:{r['world_id']}", "source": src, "world_id": r["world_id"],
                            "family": r["family"], "knobs": r["knobs"], "k": r["k"], "B_acc": r["B_acc"],
                            "A": r["A"]})
    return out


def one(j: dict) -> dict:
    from prometheus.cosmos.c4 import exp01 as E
    from prometheus.cosmos.c4.sysid_local import LocalProbe
    from prometheus.cosmos.c4.sysid_surrogate import fit_surrogate, predicted_accuracy
    s, t = E.build(j["family"], j["knobs"], j["k"])
    S = fit_surrogate(LocalProbe(s, t.n_symbols, seed=int(j["world_id"][:8], 16)))
    return {**{k: j[k] for k in ("key", "source", "world_id", "family", "k", "B_acc", "A")},
            "pred_acc": predicted_accuracy(S, V, j["k"])}


def run(rundir: str, workers: int = 3):
    from prometheus.cosmos import supervise as SV
    return SV.run_jobs(one, jobs(), rundir, key="key", out="surrogate.jsonl", workers=workers, max_failures=0)


def _spearman(a, b):
    from scipy.stats import spearmanr
    return float(spearmanr(a, b).statistic)


def _ba(y, p):
    y, p = np.asarray(y, bool), np.asarray(p, bool)
    return float(np.mean([np.mean(p[y]) if y.any() else np.nan, np.mean(~p[~y]) if (~y).any() else np.nan]))


def analyse(rundir: str) -> dict:
    rows = [json.loads(x) for x in (Path(rundir) / "surrogate.jsonl").read_text().splitlines() if x.strip()]
    out = {}
    for fam in sorted({r["family"] for r in rows}):
        R = [r for r in rows if r["family"] == fam]
        act, pr = excess([r["B_acc"] for r in R]), excess([r["pred_acc"] for r in R])
        y, p = act >= MIN_EXCESS, pr >= MIN_EXCESS
        n1, n0 = int(y.sum()), int((~y).sum())
        informative = n1 >= 10 and n0 >= 10
        rho = _spearman(pr, act)
        ba = _ba(y, p) if informative else None
        holds = informative and rho >= RHO_MIN and ba >= BA_MIN
        out[fam] = {"n": len(R), "n_usable": n1, "n_not": n0, "informative": informative, "spearman": rho,
                    "usable_ba": ba, "pred_usable_rate": float(p.mean()), "mean_pred_excess": float(pr.mean()),
                    "mean_actual_excess": float(act.mean()),
                    "verdict": ("HOLDS" if holds else "FAILS") if informative else
                               ("NOT_REACHED (uninformative; spearman reported)")}
    v = {f: o["verdict"] for f, o in out.items()}
    ctrl = [f for f in ("rnn", "graph", "sediment") if f in v and v[f] != "NOT_REACHED (uninformative; spearman reported)"]
    if ctrl and all(v[f] == "FAILS" for f in ctrl):
        overall = "INSTRUMENT_DEFECT (surrogate fails on the control families)"
    elif any(v.get(f) == "HOLDS" for f in ("phase", "stig")):
        overall = "G-0007 failure was LINEARIZATION (nonlinear local composition holds where linear failed)"
    elif all(v.get(f) == "FAILS" for f in ("phase", "stig")) and any(v[f] == "HOLDS" for f in ctrl):
        overall = "LOCALITY INSUFFICIENT on stig and phase (holds elsewhere)"
    else:
        overall = "INCONCLUSIVE (pattern not covered by the prereg decision rules)"
    return {"families": out, "overall": overall, "n_rows": len(rows)}


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "run":
        run(a[2], int(a[3]) if len(a) > 3 else 3)
    elif a[1] == "analyse":
        print(json.dumps(analyse(a[2]), indent=1))
