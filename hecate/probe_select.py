"""Probe round 1 world selection, exactly as preregistered in
roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md (E1-E5, lowest cost,
ties by id). Written before any world spec was read.

    python -m hecate.probe_select      # prints one line per frozen program
"""

from __future__ import annotations

import json
import os
import re

from hecate.schema import validate_program

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FROZEN = os.path.join(ROOT, "roles", "Hecate", "prereg",
                      "2026-09-29_first_selection", "FROZEN_IDS.txt")

COMPARATORS = ("<", ">", "=", "at least", "at most", "exceeds", "below",
               "above", "less than", "more than", "fewer than")


def parse_cost(v):
    """Core-minutes as a float, or None if unparseable. Takes the LARGEST
    number in the string (a range '2-5 core-minutes' counts as 5); seconds
    and hours are converted when named."""
    if isinstance(v, (int, float)):
        return float(v)
    if not isinstance(v, str):
        return None
    s = v.lower()
    unit = r"\s*(?:-|to)?\s*(?:cpu\s*)?(?:core[\s-]*)?min"
    mins = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)" + unit, s)]
    if mins:
        return max(mins)
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", v)]
    if not nums:
        return None
    n = max(nums)
    if re.search(r"\bsec|\bseconds?\b|\bs\b", s) and "min" not in s:
        n /= 60.0
    elif re.search(r"\bhours?\b|\bh\b", s) and "min" not in s:
        n *= 60.0
    return n


def eligible(prog, w):
    reasons = []
    if validate_program(prog):
        reasons.append("E1 program invalid")
    c = parse_cost(w.get("cost_estimate"))
    if c is None or c > 10:
        reasons.append(f"E2 cost {w.get('cost_estimate')!r}")
    for k in ("null_twin", "positive_control", "control"):
        if not str(w.get(k) or "").strip():
            reasons.append(f"E3 missing {k}")
    sc = str(w.get("success_criterion") or "").lower()
    if not (re.search(r"\d", sc) and any(t in sc for t in COMPARATORS)):
        reasons.append("E4 criterion not quantitative")
    if len(w.get("stupid_explanations") or []) < 3:
        reasons.append("E5 < 3 stupid explanations")
    return reasons, c


def choose(prog, exclude=()):
    ok = []
    rejected = {}
    for w in prog.get("experiments") or []:
        if w.get("id") in exclude:
            continue
        reasons, c = eligible(prog, w)
        if reasons:
            rejected[w.get("id")] = reasons
        else:
            ok.append((c, str(w.get("id")), w))
    ok.sort(key=lambda t: (t[0], t[1]))
    return (ok[0][2] if ok else None), rejected


def main():
    with open(FROZEN, encoding="utf-8") as fh:
        ids = [l.split("\t")[0] for l in fh if l.strip()]
    out = []
    for tid in ids:
        with open(os.path.join(ROOT, "hecate", "programs", tid, "program.json"),
                  encoding="utf-8") as fh:
            prog = json.load(fh)
        w, rej = choose(prog)
        out.append({"triplicateId": tid,
                    "probe_world": w.get("id") if w else None,
                    "status": "SELECTED" if w else "NO_ELIGIBLE_WORLD",
                    "cost": parse_cost(w.get("cost_estimate")) if w else None,
                    "rejected": rej})
    return out


def round2():
    """Round 2 (roles/Hecate/prereg/2026-09-30_probe_round2/): every frozen
    program whose round-1 world was not SIGNAL gets its next eligible world,
    same rule, round-1 world excluded."""
    with open(os.path.join(ROOT, "hecate", "programs", "PROBE_ROUND1_REPORT.json"),
              encoding="utf-8") as fh:
        r1 = {w["triplicateId"]: w for w in json.load(fh)["worlds"]}
    out = []
    for tid, w1 in sorted(r1.items()):
        if w1["outcome"] == "SIGNAL":
            continue
        with open(os.path.join(ROOT, "hecate", "programs", tid, "program.json"),
                  encoding="utf-8") as fh:
            prog = json.load(fh)
        w, rej = choose(prog, exclude={w1["world"]})
        out.append({"triplicateId": tid, "round1": [w1["world"], w1["outcome"]],
                    "probe_world": w.get("id") if w else None,
                    "status": "SELECTED" if w else "NO_ELIGIBLE_WORLD",
                    "cost": parse_cost(w.get("cost_estimate")) if w else None,
                    "rejected": rej})
    return out


if __name__ == "__main__":
    import sys
    rows = round2() if sys.argv[1:] == ["round2"] else main()
    for r in rows:
        print(json.dumps(r, sort_keys=True))
