"""Stage 3: score out/matrix.json with the rule frozen in PLAN.md.
Writes out/scores.json and out/matrix.md (fixture x check matrix)."""
import itertools
import json
import os

HERE = os.path.dirname(__file__)
m = json.load(open(os.path.join(HERE, "out", "matrix.json")))
fids = list(m)
checks = list(next(iter(m.values()))["checks"])
broken = [f for f in fids if m[f]["truth"] == "BROKEN"]
valid = [f for f in fids if m[f]["truth"] == "VALID"]


def st(f, k):
    s = m[f]["checks"][k]["status"]
    return "NA" if s == "ERROR" else s


scores = {}
for k in checks:
    fl_b = [f for f in broken if st(f, k) == "FLAG"]
    fl_v = [f for f in valid if st(f, k) == "FLAG"]
    na_b = [f for f in broken if st(f, k) == "NA"]
    na_v = [f for f in valid if st(f, k) == "NA"]
    cl, fal = len(fl_b) / len(broken), len(fl_v) / len(valid)
    cs, fas = (len(fl_b) + len(na_b)) / len(broken), (len(fl_v) + len(na_v)) / len(valid)
    runs = sum(m[f]["checks"][k]["runs"] for f in fids) / len(fids)
    wall = sum(m[f]["checks"][k]["wall"] for f in fids) / len(fids)
    scores[k] = {"catch": cl, "false_alarm": fal, "J": cl - fal, "catch_strict": cs,
                 "fa_strict": fas, "J_strict": cs - fas, "caught": fl_b, "false_alarms": fl_v,
                 "na_broken": na_b, "na_valid": na_v, "mean_extra_runs": runs,
                 "mean_wall_s": round(wall, 2),
                 "errors": [f for f in fids if m[f]["checks"][k]["status"] == "ERROR"]}

# sufficiency per broken fixture: FLAG on it and not on its twin
suff = {}
for f in broken:
    tw = m[f]["twin"]
    suff[f] = [k for k in checks if st(f, k) == "FLAG" and st(tw, k) != "FLAG"]

# minimum evidence set: zero-FA checks, exhaustive, min total wall
zero = [k for k in checks if not scores[k]["false_alarms"]]


def covers(S):
    return all(any(st(f, k) == "FLAG" for k in S) for f in broken)


best = None
for r in range(1, len(zero) + 1):
    for S in itertools.combinations(zero, r):
        if covers(S):
            c = sum(scores[k]["mean_wall_s"] for k in S)
            if best is None or c < best[1] or (c == best[1] and len(S) < len(best[0])):
                best = (S, c)
    if best:
        min_size = r
        break
all_min = []
if best:
    for S in itertools.combinations(zero, min_size):
        if covers(S):
            all_min.append((list(S), round(sum(scores[k]["mean_wall_s"] for k in S), 2)))
out = {"n_broken": len(broken), "n_valid": len(valid), "scores": scores,
       "sufficient_checks_per_broken": suff, "zero_fa_checks": zero,
       "min_cover": {"set": list(best[0]) if best else None, "wall_s": best[1] if best else None,
                     "all_min_size_covers": sorted(all_min, key=lambda x: x[1])},
       "uncovered_by_zero_fa": [f for f in broken if not any(st(f, k) == "FLAG" for k in zero)]}
json.dump(out, open(os.path.join(HERE, "out", "scores.json"), "w"), indent=1)

sym = {"PASS": ".", "FLAG": "X", "NA": "-", "ERROR": "E"}
lines = ["# W-K fixture x check matrix (X = FLAG, . = PASS, - = NA, E = ERROR)", "",
         "| fixture | truth | reading | " + " | ".join(checks) + " |",
         "|---|---|---|" + "---|" * len(checks)]
for f in fids:
    lines.append(f"| {f} | {m[f]['truth'][0]} | {m[f]['reading']['reading']} | " +
                 " | ".join(sym[m[f]['checks'][k]['status']] for k in checks) + " |")
lines += ["", "| check | catch | false alarm | J | J strict | extra runs/fixture | wall s/fixture |",
          "|---|---|---|---|---|---|---|"]
for k in checks:
    s = scores[k]
    lines.append(f"| {k} | {len(s['caught'])}/{len(broken)} | {len(s['false_alarms'])}/{len(valid)} "
                 f"| {s['J']:.2f} | {s['J_strict']:.2f} | {s['mean_extra_runs']:.1f} | {s['mean_wall_s']} |")
lines += ["", f"min zero-FA cover: {out['min_cover']}",
          f"uncovered by zero-FA checks: {out['uncovered_by_zero_fa']}"]
open(os.path.join(HERE, "out", "matrix.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
