"""Analyse ERROR_DATASET.json: class frequency, survival, catcher, recurrence after the lesson.

    python -B analyse_dataset.py   -> prints tables, writes DATASET_ANALYSIS.json
"""
import json
import os
import statistics
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "ERROR_DATASET.json"), encoding="utf-8"))
R = D["records"]

# Date the programme first wrote the lesson down as a rule (source in REPORT.md s2.3).
LESSON = {"SIM": "2026-09-19", "MAV": "2026-09-23", "RCF": "2026-09-04", "ABS": "2026-09-18",
          "IDA": "2026-09-24", "UNW": "2026-09-24", "LAC": "2026-09-24", "SUM": "2026-09-22",
          "PHT": "2026-09-24", "SCP": "2026-09-28", "PAD": "2026-09-19", "SCH": "2026-09-23",
          "RNG": "2026-09-28", "EAP": "2026-09-28", "CMP": "2026-09-24", "NDP": "2026-09-25"}

out = {}
prim = Counter(r["cls"] for r in R)
anyc = Counter(c for r in R for c in {r["cls"], r["cls2"]} if c)
out["n"] = len(R)
out["primary"] = prim.most_common()
out["any"] = anyc.most_common()

surv = defaultdict(list)
for r in R:
    for c in {r["cls"], r["cls2"]} - {None}:
        surv[c].append(r["survival_h"])
out["survival_by_class"] = {c: {"n": len(v), "median_h": statistics.median(v), "max_h": max(v),
                                "late_ge48h": sum(x >= 48 for x in v)} for c, v in surv.items()}
out["caught_by"] = Counter(r["caught_by"] for r in R).most_common()
cb_surv = defaultdict(list)
for r in R:
    cb_surv[r["caught_by"]].append(r["survival_h"])
out["survival_by_catcher"] = {k: {"n": len(v), "median_h": statistics.median(v)} for k, v in cb_surv.items()}
out["early_lt12h"] = sum(r["survival_h"] < 12 for r in R)
out["late_ge48h"] = sum(r["survival_h"] >= 48 for r in R)

# recurrence after the lesson was recorded (made strictly after lesson date)
rec = {}
for c, d in LESSON.items():
    hits = [r["id"] for r in R if c in (r["cls"], r["cls2"]) and r["made"] > d]
    before = [r["id"] for r in R if c in (r["cls"], r["cls2"]) and r["made"] <= d]
    rec[c] = {"lesson": d, "before_or_on": len(before), "after": len(hits), "after_ids": hits}
out["recurrence_after_lesson"] = rec

# by phase
phase = lambda m: "P1 09-01..22 (Z80A)" if m <= "2026-09-22" else ("P2 09-23..25 (C9/C9X)" if m <= "2026-09-25"
                                                                  else "P3 09-26..30 (W1/P2/ARC3/harvest)")
ph = defaultdict(Counter)
for r in R:
    ph[phase(r["made"])][r["cls"]] += 1
out["primary_by_phase"] = {k: v.most_common() for k, v in sorted(ph.items())}

json.dump(out, open(os.path.join(HERE, "DATASET_ANALYSIS.json"), "w", encoding="utf-8"), indent=1)
print("n =", out["n"])
print("primary:", out["primary"])
print("any:", out["any"])
print("caught_by:", out["caught_by"])
print("survival by catcher:", out["survival_by_catcher"])
print("early<12h:", out["early_lt12h"], " late>=48h:", out["late_ge48h"])
for c, v in sorted(out["survival_by_class"].items(), key=lambda kv: -kv[1]["n"]):
    print("  %-4s n=%2d median=%6.1fh max=%5.0fh late=%d" % (c, v["n"], v["median_h"], v["max_h"], v["late_ge48h"]))
print("recurrence after lesson:")
for c, v in sorted(rec.items(), key=lambda kv: -kv[1]["after"]):
    print("  %-4s lesson %s before=%d after=%d %s" % (c, v["lesson"], v["before_or_on"], v["after"], v["after_ids"]))
for k, v in out["primary_by_phase"].items():
    print(k, v)
