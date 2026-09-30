"""Novelty autopsy Part B: run meta v1's detector, unchanged, on the neutral
exact rule texts of the frozen alien-assay systems (KNOWN, ALIEN standard,
DESTROY). PREREG: roles/Hecate/prereg/2026-09-30_novelty_autopsy/PREREG.md.

    python -m hecate.autopsy.reach run      # -> hecate/autopsy/reach_rows.jsonl
    python -m hecate.autopsy.reach score    # -> hecate/autopsy/REACH.json
"""

from __future__ import annotations

import json
import math
import os
import random
import sys
from collections import Counter

from hecate.alien.dataset import OUT
from hecate.alien.rules import describe
from hecate.gravity.run import run_items

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "reach_rows.jsonl")
SEED = 20260930


def items():
    with open(os.path.join(OUT, "answer_key.json"), encoding="utf-8") as fh:
        key = json.load(fh)
    out, klass = [], {}
    for sid, e in sorted(key.items()):
        c = e["class"]
        keep = (c == "KNOWN_LAWFUL" or (c == "ALIEN_LAWFUL" and not e.get("adversarial"))
                or e.get("null_type") == "DESTROY")
        if keep:
            out.append((sid, describe(e["params"])))
            klass[sid] = "KNOWN" if c == "KNOWN_LAWFUL" else "ALIEN" if c == "ALIEN_LAWFUL" else "DESTROY"
    random.Random(SEED).shuffle(out)
    return out, klass


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - r) / d, 3), round((c + r) / d, 3))


def score():
    its, klass = items()
    rows = {}
    with open(ROWS, encoding="utf-8") as fh:
        for l in fh:
            if l.strip():
                r = json.loads(l)
                rows[r["item"]] = r
    by = {}
    for sid, cl in klass.items():
        r = rows.get(sid) or {}
        p = r.get("parsed") or {}
        by.setdefault(cl, []).append({"id": sid, "ok": bool(r.get("ok")),
                                      "classification": p.get("classification"),
                                      "prior_fit": p.get("prior_fit"),
                                      "nearest": [x.get("name") for x in (p.get("nearest_priors") or [])][:3]})
    res = {"prereg": "roles/Hecate/prereg/2026-09-30_novelty_autopsy/PREREG.md", "groups": {}}
    for cl, rs in sorted(by.items()):
        ok = [r for r in rs if r["ok"]]
        cnt = Counter(r["classification"] for r in ok)
        n = len(ok)
        res["groups"][cl] = {"n": n, "failed_calls": len(rs) - n, "counts": dict(cnt),
                             "unfamiliar_rate": (cnt.get("UNFAMILIAR", 0) / n) if n else None,
                             "unfamiliar_wilson95": wilson(cnt.get("UNFAMILIAR", 0), n),
                             "median_prior_fit": sorted(r["prior_fit"] for r in ok if isinstance(r["prior_fit"], (int, float)))[n // 2] if n else None}
    ua = res["groups"].get("ALIEN", {}).get("unfamiliar_rate")
    uk = res["groups"].get("KNOWN", {}).get("unfamiliar_rate")
    if ua is None or uk is None:
        res["decision"] = "NOT_ELIGIBLE"
    elif ua <= 0.10:
        res["decision"] = "R1 DETECTOR_CANNOT_REACH_UNFAMILIAR"
    elif ua >= 0.50 and uk <= 0.10:
        res["decision"] = "R2 DETECTOR_DISCRIMINATES"
    else:
        res["decision"] = "R3 PARTIAL"
    res["alien_nearest"] = [(r["id"], r["classification"], r["nearest"]) for r in by.get("ALIEN", [])]
    with open(os.path.join(HERE, "REACH.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(res, indent=1) + "\n")
    return res


if __name__ == "__main__":
    if sys.argv[1] == "run":
        its, _ = items()
        run_items(its, ROWS)
        print(len(its), "items")
    else:
        r = score()
        print(json.dumps({k: v for k, v in r.items() if k != "alien_nearest"}, indent=1))
