"""Shared runner for priority-loop perturbation experiments.

One contract for all ten: PREREG.json is written BEFORE the run and hashed; RESULT.json is
stamped with that hash; EVIDENCE.jsonl and STATE.jsonl are appended (never rewritten). Old
world modules are imported through `import_world` and wrapped, never edited.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import pathlib
import sys
import time

import numpy as np

LOOP = pathlib.Path(__file__).resolve().parent
CAMPAIGN = LOOP.parent
sys.path.insert(0, str(CAMPAIGN / "lib"))
import recordsafety as RS      # noqa: E402
import seeds as S              # noqa: E402,F401


def js(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    return str(o)


def import_world(exp, name):
    """Import a frozen experiment module by path, without touching it."""
    p = CAMPAIGN / "experiments" / exp / (name + ".py")
    d = str(p.parent)
    if d not in sys.path:
        sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_cfg(exp, attempt_id):
    cfg = json.loads((CAMPAIGN / "experiments" / exp / "WORLD.json").read_text(encoding="utf-8"))
    cfg["attempt_id"] = attempt_id
    return cfg


def prereg(exp_dir, spec):
    """Write PREREG.json before any evaluation; returns its sha256. Refuses to overwrite."""
    p = pathlib.Path(exp_dir) / "PREREG.json"
    if p.exists():
        old = json.loads(p.read_text(encoding="utf-8"))
        return old["prereg_sha256"]
    spec = dict(spec)
    spec["written"] = time.strftime("%Y-%m-%d %H:%M:%S")
    body = json.dumps(spec, sort_keys=True, ensure_ascii=True, default=js)
    h = hashlib.sha256(body.encode()).hexdigest()
    spec["prereg_sha256"] = h
    p.write_text(json.dumps(spec, indent=1, ensure_ascii=True, default=js), encoding="utf-8")
    RS.require_ascii_safe(p)
    return h


def result(exp_dir, res, prereg_hash):
    res = dict(res)
    res["prereg_sha256"] = prereg_hash
    res["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    p = pathlib.Path(exp_dir) / "RESULT.json"
    p.write_text(json.dumps(res, indent=1, ensure_ascii=True, default=js), encoding="utf-8")
    RS.require_ascii_safe(p)
    return p


def append_evidence(trajectory_id, perturbation_id, summary, material_change, detail=None, state=None, state_reason=None):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with (LOOP / "EVIDENCE.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"trajectory_id": trajectory_id, "perturbation_id": perturbation_id, "ts": ts,
                             "summary": summary, "material_change": material_change, "detail": detail or {}},
                            ensure_ascii=True, default=js) + "\n")
    if state:
        with (LOOP / "STATE.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"trajectory_id": trajectory_id, "ts": ts, "state": state,
                                 "reason": state_reason or "", "after": perturbation_id}, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(LOOP / "EVIDENCE.jsonl")
    RS.require_ascii_safe(LOOP / "STATE.jsonl")


def relabel_diff(x_a, x_b, n_max=20000, seed=0):
    """Difference of means b - a with the exact relabelling null (all splits) or a seeded
    Monte Carlo subset when the exact count exceeds n_max. Returns effect, p05, p95, n_null."""
    x = np.concatenate([np.asarray(x_a, float), np.asarray(x_b, float)])
    na, nb = len(x_a), len(x_b)
    n = na + nb
    eff = float(np.mean(x_b) - np.mean(x_a))
    from math import comb
    total = comb(n, nb)
    null = []
    if total <= n_max:
        for c in itertools.combinations(range(n), nb):
            m = np.zeros(n, bool)
            m[list(c)] = True
            null.append(float(x[m].mean() - x[~m].mean()))
    else:
        rng = np.random.Generator(np.random.PCG64(seed))
        for _ in range(n_max):
            m = np.zeros(n, bool)
            m[rng.choice(n, nb, replace=False)] = True
            null.append(float(x[m].mean() - x[~m].mean()))
    null = np.array(null)
    return {"effect": eff, "p05": float(np.percentile(null, 5)), "p95": float(np.percentile(null, 95)),
            "n_null": int(len(null)), "exact": bool(total <= n_max),
            "above_p95": bool(eff > np.percentile(null, 95)), "below_p05": bool(eff < np.percentile(null, 5))}


def relabel_ancova(y_a, C_a, y_b, C_b, n_max=20000, seed=0):
    """c in y = a + b*C + c*[group b], exact relabelling null over group labels."""
    y = np.concatenate([np.asarray(y_a, float), np.asarray(y_b, float)])
    C = np.concatenate([np.asarray(C_a, float), np.asarray(C_b, float)])
    na, nb = len(y_a), len(y_b)
    n = na + nb

    def fit(mask):
        X = np.column_stack([np.ones(n), C, mask.astype(float)])
        return float(np.linalg.lstsq(X, y, rcond=None)[0][2])

    lab = np.zeros(n, bool)
    lab[na:] = True
    c = fit(lab)
    from math import comb
    total = comb(n, nb)
    null = []
    if total <= n_max:
        for cc in itertools.combinations(range(n), nb):
            m = np.zeros(n, bool)
            m[list(cc)] = True
            null.append(fit(m))
    else:
        rng = np.random.Generator(np.random.PCG64(seed))
        for _ in range(n_max):
            m = np.zeros(n, bool)
            m[rng.choice(n, nb, replace=False)] = True
            null.append(fit(m))
    null = np.array(null)
    return {"c": c, "p05": float(np.percentile(null, 5)), "p95": float(np.percentile(null, 95)),
            "n_null": int(len(null)), "exact": bool(total <= n_max),
            "above_p95": bool(c > np.percentile(null, 95)), "below_p05": bool(c < np.percentile(null, 5))}
