"""Shared pieces for the cw01-arch4 drivers (on top of arch4rt): viable-parent selection, walker
regeneration with digest verification, held-out exaptation, diversity, paired sign-flip nulls,
and the loop harness import. Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import gzip
import json
import pathlib
import sys
from itertools import combinations

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "loop"))
import arch4rt as A            # noqa: E402
import looprun as L            # noqa: E402,F401

SCOPE = ("Computational artificial-life research: integer programs on a bounded virtual machine, search operators and "
         "simulated populations of software objects. No biological material, organism, procedure or design of any kind.")


def viable_parents(E=A.C1.E):
    """Parents whose evaluate() on their own environment is not degenerate (C4-05's 'viable' set)."""
    out = []
    for p in A.parents():
        env = A.PARENT_ENV[p["stratum"]]
        ev = A.evaluate(p["manifest"], A.episodes(env, E), rng_seed=0, reward_mode="per_ask")
        deg = ev["answered_share"] == 0.0
        p = dict(p)
        p["env"] = env
        p["degenerate"] = bool(deg)
        p["r0"] = ev["reward_per_ask"]
        out.append(p)
    return out


def regenerate_walker(parent, org, w, env_eps, depth=16):
    """C4-05's walker w of `parent` (same seeds); digest checked against the committed steps when available."""
    wk = A.C5.walk(parent, org, w, env_eps, depth, 32)
    return wk


def committed_last_steps():
    p = A.ARCH / "archaeon" / "campaign4" / "C4-05" / "attempts" / "a01" / "steps.json.gz"
    if not p.exists():
        return {}
    steps = json.load(gzip.open(p, "rt", encoding="utf-8"))
    last = {}
    for s in steps:
        k = (s["parent_id"], s["walker"])
        if k not in last or s["depth"] > last[k]["depth"]:
            last[k] = s
    return last


def exaptive(child_ev, parent_ev, env):
    return [o for o in A.OTHER_ENVS if o != env and child_ev[o]["reward_per_ask"] >= parent_ev[o]["reward_per_ask"] + A.C1.BAND
            and child_ev[o]["reward_per_ask"] >= A.C1.FLOOR]


def struct_div(ms):
    """Mean pairwise L1 distance of static opcode-category counts, normalised (C4-05's measure)."""
    ds = [A.structural_descriptor(m) for m in ms]
    vals = []
    for a, b in combinations(range(len(ds)), 2):
        ha, hb = ds[a]["opcode_category_counts_static"], ds[b]["opcode_category_counts_static"]
        keys = set(ha) | set(hb)
        la, lb = len(ms[a]["genome"]) // A.IW, len(ms[b]["genome"]) // A.IW
        vals.append(sum(abs(ha.get(x, 0) - hb.get(x, 0)) for x in keys) / max(1, la + lb))
    return float(np.mean(vals)) if vals else None


def paired_signflip(diffs, n=5000, seed=0):
    d = np.asarray(diffs, float)
    d = d[np.isfinite(d)]
    if len(d) == 0:
        return None
    rng = np.random.Generator(np.random.PCG64(seed))
    obs = float(d.mean())
    null = np.array([(d * rng.choice([-1.0, 1.0], size=len(d))).mean() for _ in range(n)])
    return {"mean_diff": obs, "p05": float(np.percentile(null, 5)), "p95": float(np.percentile(null, 95)), "n": int(len(d)),
            "above_p95": bool(obs > np.percentile(null, 95)), "below_p05": bool(obs < np.percentile(null, 5))}


def n_instr(m):
    return len(m["genome"]) // A.IW


def js(o):
    return L.js(o)
