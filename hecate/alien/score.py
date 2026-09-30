"""Frozen mechanical scorer for the alien-lawful assay. Every number comes
from the simulator or an exhaustive check; subject labels are recorded as
behaviour and never used as truth.

    python -m hecate.alien.score <model>     # -> hecate/alien/runs/<model>/SCORES.json
"""

from __future__ import annotations

import json
import os
import random
import sys
from collections import Counter, defaultdict

import numpy as np

from hecate.alien import sandbox as SB
from hecate.alien import verify as V
from hecate.alien.generate import check_prop
from hecate.alien.runner import RUNS, load
from hecate.alien.systems import all_states, clamp_run, dims_of, parse_state, step

BOOT = 2000
BOOT_SEED = 20260930


# ---- per-call scoring ------------------------------------------------------------

def _states(p, xs):
    out = []
    for x in xs or []:
        try:
            s = parse_state(p, x)
            out.append(s if len(s) == len(dims_of(p)) else None)
        except Exception:
            out.append(None)
    return out


def acc(pred, truth):
    """(exact, component) accuracy; a missing/unparseable prediction scores 0."""
    ex, comp = [], []
    for i, t in enumerate(truth):
        p = pred[i] if i < len(pred) else None
        if p is None:
            ex.append(0.0)
            comp.append(0.0)
        else:
            ex.append(float(tuple(p) == tuple(t)))
            comp.append(float(np.mean([a == b for a, b in zip(p, t)])))
    return float(np.mean(ex)), float(np.mean(comp))


def score_t2(p, obj, ans):
    preds = _states(p, ((obj or {}).get("t2") or {}).get("predictions"))
    return acc(preds, [tuple(s) for s in ans["t2"]])


def score_t3(p, obj, ans):
    preds = ((obj or {}).get("t3") or {}).get("predictions") or []
    ex, comp = [], []
    for i, truth in enumerate(ans["t3"]):
        pr = _states(p, preds[i]) if i < len(preds) and isinstance(preds[i], list) else []
        e, c = acc(pr, [tuple(s) for s in truth])
        ex.append(e)
        comp.append(c)
    return float(np.mean(ex)), float(np.mean(comp))


def _tbl(p, cache):
    key = json.dumps(p, sort_keys=True)
    if key not in cache:
        cache[key] = V.table(p)
    return cache[key]


def score_claims(p, obj, planted, cache):
    """Each claim -> TRUE / FALSE / TRIVIAL / UNTESTABLE, evaluated on the full
    state space (exhaustive). Planted recall: a TRUE claim that captures a
    planted property (see _captures)."""
    claims = ((obj or {}).get("t4") or {}).get("claims") or []
    tbl = _tbl(p, cache)
    t, states, dims = tbl
    nxt = [states[i] for i in t]
    out = []
    for c in claims:
        if not isinstance(c, dict):
            out.append({"kind": "?", "status": "UNTESTABLE"})
            continue
        kind = c.get("kind")
        res = {"kind": kind, "expr": c.get("expr"), "k": c.get("k")}
        try:
            if kind in ("conserved", "advances"):
                vals = SB.run(SB.expr_to_fn(str(c["expr"])), "q", states + nxt)
                if isinstance(vals, dict) or any(v is None for v in vals):
                    res["status"] = "UNTESTABLE"
                else:
                    a, b = vals[:len(states)], vals[len(states):]
                    if len(set(a)) <= 1:
                        res["status"] = "TRIVIAL"
                    elif kind == "conserved":
                        res["status"] = "TRUE" if all(x == y for x, y in zip(a, b)) else "FALSE"
                        res["values"] = a
                    else:
                        k = int(c.get("k") or 0)
                        if k <= 1:
                            res["status"] = "TRIVIAL"
                        else:
                            res["status"] = "TRUE" if all((x + 1) % k == y % k for x, y in zip(a, b)) else "FALSE"
                            res["values"] = a
            elif kind == "one_predecessor":
                res["status"] = "TRUE" if V.bijective(p, tbl) else "FALSE"
            elif kind == "settles":
                ob = V.orbit_structure(p, tbl)
                res["status"] = "TRUE" if set(ob["periods"]) == {1} else "FALSE"
            elif kind == "symmetry":
                g = SB.run(SB.expr_to_fn(str(c["expr"]), "g"), "g", states)
                if isinstance(g, dict) or any(v is None or len(v) != len(dims) for v in g):
                    res["status"] = "UNTESTABLE"
                else:
                    gs = [tuple(v) for v in g]
                    if all(a == b for a, b in zip(gs, states)):
                        res["status"] = "TRIVIAL"
                    elif any(any(not 0 <= x < d for x, d in zip(v, dims)) for v in gs):
                        res["status"] = "FALSE"
                    else:
                        idx = {st: i for i, st in enumerate(states)}
                        res["status"] = "TRUE" if all(step(p, gs[i]) == gs[idx[nxt[i]]]
                                                      for i in range(len(states))) else "FALSE"
            else:
                res["status"] = "UNTESTABLE"
        except Exception as e:
            res["status"] = "UNTESTABLE"
            res["error"] = type(e).__name__
        out.append(res)
    captured = _captures(p, out, planted, tbl)
    for r in out:
        r.pop("values", None)
    return out, captured


def _captures(p, claims, planted, tbl):
    """Which planted properties a TRUE claim captures:
    conserved_linear / conserved_weights / cyclic_linear -> a TRUE conserved /
      advances claim whose value determines the planted quantity on every state;
    bijective -> TRUE one_predecessor; all_orbits_fixed -> TRUE settles;
    commutes_swap -> TRUE symmetry claim."""
    t, states, dims = tbl
    hit = {}
    for pr in planted:
        if not pr.get("primary", True):
            continue                                  # descriptive, not planted structure
        ty = pr["type"]
        name = json.dumps(pr, sort_keys=True)
        ok = False
        if ty in ("conserved_linear", "cyclic_linear", "conserved_weights"):
            if ty == "conserved_weights":
                pv = [sum(pr["w"][v] for v in s) % pr["mod"] for s in states]
            else:
                pv = [sum(w * v for w, v in zip(pr["w"], s)) % pr["mod"] for s in states]
            want = "conserved" if ty != "cyclic_linear" else "advances"
            for c in claims:
                if c.get("status") == "TRUE" and c["kind"] == want and "values" in c:
                    m = {}
                    if all(m.setdefault(q, v) == v for q, v in zip(c["values"], pv)):
                        ok = True
        elif ty == "bijective":
            ok = any(c.get("status") == "TRUE" and c["kind"] == "one_predecessor" for c in claims)
        elif ty == "all_orbits_fixed":
            ok = any(c.get("status") == "TRUE" and c["kind"] == "settles" for c in claims)
        elif ty == "commutes_swap":
            ok = any(c.get("status") == "TRUE" and c["kind"] == "symmetry" for c in claims)
        else:
            continue                                  # descriptive props not scored for recall
        hit[name] = ok
    return hit


def score_code(p, src, ans, cache):
    """Executable-model generalisation on 200 held-out states + intervention
    accuracy of the subject's step under the clamp interventions."""
    if not isinstance(src, str) or "def" not in src:
        return {"status": "NO_CODE"}
    ev = [tuple(s) for s in ans["eval_states"]]
    out = SB.run(src, "step", ev)
    if isinstance(out, dict):
        return {"status": "ERROR", "error": out["error"], "length": SB.code_length(src)}
    preds = [tuple(o) if isinstance(o, list) and len(o) == len(dims_of(p)) else None for o in out]
    ex, comp = acc(preds, [tuple(s) for s in ans["eval_next"]])
    iv_ex = []
    for spec, truth in zip(ans["t3_spec"], ans["t3"]):
        if spec["type"] != "clamp":
            continue
        s = list(spec["start"])
        s[spec["var"]] = spec["val"]
        traj = []
        for _ in range(3):
            o = SB.run(src, "step", [s])
            if isinstance(o, dict) or o[0] is None or len(o[0]) != len(s):
                traj.append(None)
                break
            s = list(o[0])
            s[spec["var"]] = spec["val"]
            traj.append(tuple(s))
        iv_ex.append(acc(traj + [None] * (3 - len(traj)), [tuple(x) for x in truth])[0])
    return {"status": "OK", "eval_exact": ex, "eval_comp": comp, "length": SB.code_length(src),
            "intervention_exact": float(np.mean(iv_ex)) if iv_ex else None}


def structure_score(obj):
    """T1 -> P(rule) in [0,1]: RULE conf, RANDOM 1-conf, UNCERTAIN 0.5."""
    t1 = (obj or {}).get("t1") or {}
    v = str(t1.get("verdict", "")).upper()
    try:
        c = float(t1.get("confidence", 0.5))
    except (TypeError, ValueError):
        c = 0.5
    c = min(1.0, max(0.0, c))
    return {"RULE": c, "RANDOM": 1 - c}.get(v, 0.5), v


def analogy_class(fam_obj, analogy_score, trivial_best):
    """Preregistered mapping (PREREG s5)."""
    o = fam_obj or {}
    name = o.get("analogy")
    try:
        conf = float(o.get("confidence") or 0)
    except (TypeError, ValueError):
        conf = 0.0
    if not name or str(name).lower() in ("null", "none") or conf < 0.3:
        return "NO_ANALOGY"
    if analogy_score is None:
        comp, ex = None, None
    else:
        ex, comp = analogy_score.get("eval_exact"), analogy_score.get("eval_comp")
    if ex is not None and ex >= 0.9:
        return "CORRECT_ANALOGY"
    if comp is not None and comp >= trivial_best + 0.2:
        return "USEFUL_PARTIAL_ANALOGY"
    if conf >= 0.6 and str(o.get("claimed_equivalence", "")).upper() in ("EXACT", "PARTIAL"):
        return "FALSE_COLLAPSE_TO_FAMILIAR"
    return "SUPERFICIAL_ANALOGY"


# ---- aggregation --------------------------------------------------------------

def grp(e):
    if e["class"] == "KNOWN_LAWFUL":
        return "K"
    if e["class"] == "ALIEN_LAWFUL":
        return "AADV" if e.get("adversarial") else "A"
    return "N_" + e["null_type"]


INCOMP = ("N_CONJ", "N_DSCRAMBLE", "N_SCRAMBLE", "N_SEDUCTIVE")


def auc(pos, neg):
    if not pos or not neg:
        return None
    return float(np.mean([(a > b) + 0.5 * (a == b) for a in pos for b in neg]))


def boot_diff(fn, items_a, items_b, seed=BOOT_SEED, n=BOOT):
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        a = [rng.choice(items_a) for _ in items_a]
        b = [rng.choice(items_b) for _ in items_b]
        v = fn(a, b)
        if v is not None:
            vals.append(v)
    vals.sort()
    return (vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]) if vals else (None, None)


def read(model, task):
    path = os.path.join(RUNS, model, f"{task}.jsonl")
    if not os.path.exists(path):
        return {}
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for l in fh:
            if l.strip():
                r = json.loads(l)
                rows[r["sid"]] = r                      # latest wins
    return rows


def trivial_best(key_e, pub_e):
    """Best of identity / nearest-neighbour component accuracy on the eval set
    (from the baselines file) -- the bar a prediction must beat."""
    return max(key_e.get("_baseline_identity", 0), key_e.get("_baseline_nn", 0))
