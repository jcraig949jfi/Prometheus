"""Non-LLM baselines for the alien-lawful assay (directive step 6).

Structure-detection cues (score per system; higher = "more lawful"):
  compress   -(zlib ratio of the observation text)
  recur      fraction of observed states that repeat within a trajectory
Next-state predictors (from the observed transitions only):
  identity   next = current
  nn         successor of the nearest observed state (Hamming)
  affine     best affine map mod m per component (exhaustive), fit on observations
  localtab   per component, best (j, k)-indexed lookup of value or increment
Invariant search:
  linsearch  linear functionals conserved on every observed transition,
             then checked exhaustively on the full state space

    python -m hecate.alien.baselines      # -> hecate/alien/data/BASELINES.json
"""

from __future__ import annotations

import itertools
import json
import os
import zlib
from collections import Counter, defaultdict

import numpy as np

from hecate.alien.dataset import OUT
from hecate.alien.systems import all_states, dims_of, parse_state, step


def _transitions(p, pub):
    ts = []
    for traj in pub["observations"]:
        st = [parse_state(p, s) for s in traj]
        ts += list(zip(st[:-1], st[1:]))
    return ts


def cue_scores(pub):
    text = "\n".join(" ; ".join(t) for t in pub["observations"]).encode()
    rep = 0
    tot = 0
    for t in pub["observations"]:
        seen = set()
        for s in t:
            tot += 1
            rep += s in seen
            seen.add(s)
    return {"compress": -len(zlib.compress(text, 9)) / len(text), "recur": rep / tot}


def pred_identity(ts, q, dims):
    return tuple(q)


def pred_nn(ts, q, dims):
    best = min(ts, key=lambda t: sum(a != b for a, b in zip(t[0], q)))
    return best[1]


def fit_affine(ts, dims):
    """Per component i: best (a, b) with x'_i = a.x + b mod d_i, exhaustive over
    small coefficient ranges; ties broken by lexicographic order."""
    n = len(dims)
    models = []
    for i in range(n):
        m = dims[i]
        X = np.array([t[0] for t in ts])
        y = np.array([t[1][i] for t in ts])
        best, bestc = None, -1
        rng = range(m) if m <= 7 else range(-3, 4)
        for coef in itertools.product(rng, repeat=n):
            base = (X @ np.array(coef)) % m
            for b in range(m):
                c = int(np.sum((base + b) % m == y))
                if c > bestc:
                    best, bestc = (coef, b), c
            if bestc == len(ts):
                break
        models.append(best)
    return models


def pred_affine(models, q, dims):
    return tuple(int((np.dot(c, q) + b) % d) for (c, b), d in zip(models, dims))


def fit_localtab(ts, dims):
    n = len(dims)
    models = []
    for i in range(n):
        best, bestscore = None, (-1, -1)
        for j, k in itertools.combinations_with_replacement(range(n), 2):
            for target in ("value", "inc"):
                tab = defaultdict(Counter)
                for s, s2 in ts:
                    out = s2[i] if target == "value" else (s2[i] - s[i]) % dims[i]
                    tab[(s[j], s[k])][out] += 1
                cons = sum(c.most_common(1)[0][1] for c in tab.values())
                score = (cons, -len(tab))
                if score > bestscore:
                    bestscore = score
                    best = (j, k, target, {key: c.most_common(1)[0][0] for key, c in tab.items()})
        models.append(best)
    return models


def pred_localtab(models, q, dims):
    out = []
    for i, (j, k, target, tab) in enumerate(models):
        v = tab.get((q[j], q[k]))
        if v is None:
            out.append(q[i])
        elif target == "value":
            out.append(v)
        else:
            out.append((q[i] + v) % dims[i])
    return tuple(out)


def _acc(preds, truth):
    ex = np.mean([tuple(p) == tuple(t) for p, t in zip(preds, truth)])
    comp = np.mean([np.mean([a == b for a, b in zip(p, t)]) for p, t in zip(preds, truth)])
    return float(ex), float(comp)


def linsearch(p, ts, dims):
    """Linear functionals (coefficients 0..m-1 over same-modulus components)
    conserved on all observed transitions; then verified on all states."""
    if len(set(dims)) != 1 and p["family"] != "vm":
        return {"found": 0, "true": 0}
    idx = list(range(len(dims))) if p["family"] != "vm" else [1, 2, 3]
    m = dims[idx[0]]
    if m > 7:
        return {"found": 0, "true": 0}
    found = []
    for w in itertools.product(range(m), repeat=len(idx)):
        if not any(w):
            continue
        if all(sum(wi * s[j] for wi, j in zip(w, idx)) % m ==
               sum(wi * s2[j] for wi, j in zip(w, idx)) % m for s, s2 in ts):
            found.append(w)
    true = 0
    states = all_states(dims)[::7]
    for w in found[:50]:
        if all(sum(wi * s[j] for wi, j in zip(w, idx)) % m ==
               sum(wi * v for wi, v in zip(w, [step(p, s)[j] for j in idx])) % m for s in states):
            true += 1
    return {"found": len(found), "true": true, "checked": min(50, len(found))}


def run():
    with open(os.path.join(OUT, "public.json"), encoding="utf-8") as fh:
        public = {e["id"]: e for e in json.load(fh)}
    with open(os.path.join(OUT, "answer_key.json"), encoding="utf-8") as fh:
        key = json.load(fh)
    rows = []
    for sid, pub in sorted(public.items()):
        k = key[sid]
        p = k["params"]
        dims = dims_of(p)
        ts = _transitions(p, pub)
        q2 = [tuple(s) for s in k["answers"]["q2_states"]]
        a2 = [tuple(s) for s in k["answers"]["t2"]]
        ev = [tuple(s) for s in k["answers"]["eval_states"]][:100]
        evn = [tuple(s) for s in k["answers"]["eval_next"]][:100]
        aff = fit_affine(ts, dims) if max(dims) <= 7 and len(dims) <= 5 else None
        lt = fit_localtab(ts, dims)
        row = {"id": sid, "class": k["class"], "null_type": k["null_type"],
               "family": k["family"], "adversarial": k.get("adversarial", False),
               **cue_scores(pub)}
        for name, f in (("identity", lambda q: pred_identity(ts, q, dims)),
                        ("nn", lambda q: pred_nn(ts, q, dims)),
                        ("localtab", lambda q: pred_localtab(lt, q, dims)),
                        ("affine", (lambda q: pred_affine(aff, q, dims)) if aff else None)):
            if f is None:
                continue
            row[f"{name}_t2_exact"], row[f"{name}_t2_comp"] = _acc([f(q) for q in q2], a2)
            row[f"{name}_eval_exact"], row[f"{name}_eval_comp"] = _acc([f(q) for q in ev], evn)
        row["linsearch"] = linsearch(p, ts, dims)
        rows.append(row)
    return rows


def auc(pos, neg):
    if not pos or not neg:
        return None
    wins = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg)
    return wins / (len(pos) * len(neg))


def summarize(rows):
    def grp(r):
        if r["class"] == "MATCHED_NOISE":
            return "N/" + r["null_type"]
        return ("A/ADV" if r["adversarial"] else "A") if r["class"] == "ALIEN_LAWFUL" else "K"
    out = {"by_group": {}, "cue_auc": {}}
    groups = defaultdict(list)
    for r in rows:
        groups[grp(r)].append(r)
    for g, rs in sorted(groups.items()):
        out["by_group"][g] = {k: round(float(np.mean([r[k] for r in rs if k in r])), 3)
                              for k in rs[0] if k.endswith(("_exact", "_comp")) or k in ("compress", "recur")}
        out["by_group"][g]["n"] = len(rs)
    incomp = [r for r in rows if r["class"] == "MATCHED_NOISE" and r["null_type"] != "DESTROY"]
    for cue in ("compress", "recur", "localtab_eval_comp", "nn_eval_comp"):
        for lawful in ("K", "A"):
            pos = [r[cue] for r in rows if grp(r).split("/")[0] == lawful and cue in r]
            out["cue_auc"][f"{cue}:{lawful}_vs_incompressible_noise"] = round(auc(pos, [r[cue] for r in incomp if cue in r]), 3)
    return out


if __name__ == "__main__":
    rows = run()
    s = summarize(rows)
    with open(os.path.join(OUT, "BASELINES.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"summary": s, "rows": rows}, indent=1, default=str) + "\n")
    print(json.dumps(s, indent=1))
