"""One iteration of the LUDUS bench, for the hourly loop.

WORLD SELECTION IS NOT AUTOMATED, deliberately. See `choose_next_work`.

Authorised 2026-08-26: hourly, in 48-hour blocks. This is what one wake does.

An honest division of labour. A loop can do the **mechanical** work — rebuild the
matrix when a registry changes, sweep parameters, recompute visitation-weighted
gaps, re-fit per-world baselines, check that yesterday's numbers still reproduce.
It cannot faithfully implement a new board game from a rulebook; that needs the
seat, and pretending otherwise would fill the world registry with worlds whose
rules nobody checked. So the loop's last act each wake is to **name the highest
information-gain missing cell** and write it where the next wake will read it.

Charter v2 §41: the atlas should become an active scientific instrument, not a
collection. The selector below is the first version of that — crude, and honest
about being crude.
"""
from __future__ import annotations

import json
import pathlib
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS = ROOT / "ludus" / "atlas"
LOG = ATLAS / "bench_log.jsonl"
NEXT = ATLAS / "NEXT_WORK_ITEM.md"


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_matrix():
    p = ATLAS / "transfer_matrix.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def coverage(matrix) -> dict:
    """Which circuit x world cells exist, and which are missing."""
    if not matrix:
        return {"cells": 0, "missing": [], "worlds": 0, "circuits": 0}
    circuits = matrix["circuits"]
    filled, missing = 0, []
    for wname, e in matrix["worlds"].items():
        if e.get("failed"):
            missing.append((wname, "*", "world failed to solve"))
            continue
        for rid, meta in circuits.items():
            axis = meta["axis"]
            key = "stop_axis" if axis == "STOP" else "select_axis"
            if rid in e.get(key, {}):
                filled += 1
            elif axis == "SELECT" and not e.get("select_axis_is_live"):
                pass                        # not a gap: the world has no SELECT axis
            else:
                missing.append((wname, rid, "cell not computed"))
    return {"cells": filled, "missing": missing,
            "worlds": len(matrix["worlds"]), "circuits": len(circuits)}


def transferable_summary(matrix) -> dict:
    """The bench's headline: how does each transferable circuit hold up across
    worlds, and does it clear the per-world FITTED baseline it must beat?"""
    if not matrix:
        return {}
    out = {}
    for rid, meta in matrix["circuits"].items():
        if not meta["transferable"]:
            continue
        key = "stop_axis" if meta["axis"] == "STOP" else "select_axis"
        rows = {}
        for wname, e in matrix["worlds"].items():
            if e.get("failed") or rid not in e.get(key, {}):
                continue
            r = e[key][rid]["retention"]
            fitted = e.get("stop_axis", {}).get("r0006-fitted", {}).get("retention")
            rows[wname] = {"retention": r,
                           "beats_fitted_baseline": (None if fitted is None
                                                     else bool(r > fitted))}
        if rows:
            vals = [v["retention"] for v in rows.values()]
            out[rid] = {"axis": meta["axis"], "doc": meta["doc"], "worlds": rows,
                        "min_retention": round(min(vals), 4),
                        "mean_retention": round(sum(vals) / len(vals), 4),
                        "n_worlds": len(vals)}
    return out


def choose_next_work(matrix, cov, summ) -> dict:
    """Report the MECHANICAL gap. Do NOT choose the next world.

    The first version of this function ranked candidate worlds by an
    information-gain proxy. That was withdrawn on instruction and the reasoning
    is worth keeping where the code is, because the temptation will return:

        an automatic next-game selector is only as good as the ontology it
        maximises over, and this ontology currently has one family of worlds,
        four SELECT circuits with ZERO untouched test worlds between them, and
        no measured collisions. A selector optimising over that would be
        maximising a proxy nobody can falsify, and it would spend the seat's
        twelve months confirming its own priors with a great show of rigour.

    A human choosing deliberately hostile worlds beats that until the ontology
    has enough competing hypotheses that the SELECTOR ITSELF can be wrong in a
    detectable way. Until then this function does mechanical bookkeeping and
    hands world choice to `ludus/atlas/BACKLOG.md`.

    Re-enable automated selection only when BOTH hold:
      * at least two circuits on the same axis have measurably COLLIDED, so
        there is a real discrimination target rather than a coverage count; and
      * at least one circuit has a recorded first_failure, so the selector has a
        falsification event to be scored against.
    """
    if not matrix:
        return {"action": "BUILD_MATRIX", "why": "no atlas exists yet",
                "selection_automated": False}
    failed = [w for w, e in matrix["worlds"].items() if e.get("failed")]
    if failed:
        return {"action": "REPAIR_WORLD", "target": failed[0],
                "why": "a registered world has no usable row",
                "selection_automated": False}
    if cov["missing"]:
        w, rid, _ = cov["missing"][0]
        return {"action": "FILL_CELL", "target": f"{w} x {rid}",
                "why": "an uncomputed circuit x world cell",
                "selection_automated": False}
    thin = sorted(summ.items(), key=lambda kv: kv[1]["n_worlds"])
    if thin and thin[0][1]["n_worlds"] < 3:
        return {"action": "FLAG_THIN_CIRCUIT", "target": thin[0][0],
                "why": f"only {thin[0][1]['n_worlds']} world(s) of evidence; a "
                       "circuit measured in too few worlds is a claim about "
                       "those worlds, not about transfer",
                "selection_automated": False}
    return {"action": "DEFER_TO_BACKLOG",
            "target": "ludus/atlas/BACKLOG.md, top unbuilt entry",
            "why": "every mechanical gap is closed. World choice is deliberately "
                   "NOT automated at this stage of the ontology - see the "
                   "docstring for the two conditions that would re-enable it.",
            "selection_automated": False}


def main() -> dict:
    t0 = time.time()
    matrix = load_matrix()
    cov = coverage(matrix)
    summ = transferable_summary(matrix)
    nxt = choose_next_work(matrix, cov, summ)

    rec = {"ts_utc": _now(), "wall_seconds": round(time.time() - t0, 2),
           "worlds": cov["worlds"], "circuits": cov["circuits"],
           "cells_filled": cov["cells"], "cells_missing": len(cov["missing"]),
           "transferable_circuits": {k: {"n_worlds": v["n_worlds"],
                                         "min_retention": v["min_retention"],
                                         "mean_retention": v["mean_retention"]}
                                     for k, v in summ.items()},
           "next_work_item": nxt}
    ATLAS.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")

    lines = [f"# Next work item — chosen {rec['ts_utc']}", "",
             f"**Action:** `{nxt['action']}`  **Target:** {nxt['target']}", "",
             f"**Why:** {nxt['why']}", "",
             f"Bench state: {cov['worlds']} worlds, {cov['circuits']} circuits, "
             f"{cov['cells']} cells filled, {len(cov['missing'])} missing.", "",
             "## Transferable circuits, weakest world first", ""]
    for rid, v in sorted(summ.items(), key=lambda kv: kv[1]["min_retention"]):
        lines.append(f"- **{rid}** ({v['axis']}) — min {v['min_retention']:.4f}, "
                     f"mean {v['mean_retention']:.4f} over {v['n_worlds']} worlds")
        for w, r in sorted(v["worlds"].items(), key=lambda kv: kv[1]["retention"]):
            beat = ("beats fitted baseline" if r["beats_fitted_baseline"]
                    else "DOES NOT beat the fitted per-world baseline"
                    if r["beats_fitted_baseline"] is not None else "")
            lines.append(f"    - {w}: {r['retention']:.4f}  {beat}")
    NEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return rec


if __name__ == "__main__":
    main()
