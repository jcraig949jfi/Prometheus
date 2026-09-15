"""H-R4-2 (round 4 P0, builder H): F12's clause A axis on SCREENED worlds only.

Screen: primordial/ledger/qd/worlds_r4.json, written by builder G (G-R4-4; schema agreed on the bus,
H 1789433688592-0, A 1789433714703-0, G 1789433928197-0). The active variant is
`<q1_floor_policy>|<q2_policy>` from the file (operator message 13: gate_in|HOLD). Nothing here
re-derives a floor or a verdict of the screen: the floor is verdicts[variant]["floor"], the baseline is
the cell's baseline block.

  screen status   SURVIVED -> judged; HELD, CULLED, NOT_REACHED, UNSCREENED (absent, or no file) ->
                  INELIGIBLE(<status>) and never scored; the judge is not consulted for them.

Clause A, round 4 binding (SWARM_R4 s4), per candidate on a SURVIVED cell:
  progress = (median_candidate - floor) / (median_baseline - floor)
  PASS iff progress >= 0.95 AND bytes < baseline bytes; BELOW_FLOOR iff progress < 0; FAIL otherwise;
  INELIGIBLE if oracles unclean, a cheat control did not fail, < 8 run seeds, or the cell is not SURVIVED.
  The candidate's bootstrap CI (primordial.metric.ci.median_ci) is mapped through the same formula and
  reported, not judged.

`qd_ledger check` is the only judge (its `clause_a_r4` block, G-R4-5). F12 scores a PASS only when the
judge says PASS and `s4_verdict` below, computed from the screen's numbers, agrees; a disagreement is
recorded as MISMATCH and scores nothing. A judge without a clause_a_r4 block reads NO_JUDGE.
"""
from __future__ import annotations

import json
import pathlib

from primordial.score.round2 import ROOT

WORLDS_R4 = ROOT / "primordial" / "ledger" / "qd" / "worlds_r4.json"
PASS_PROGRESS = 0.95                 # SWARM_R4 s4 (operator message 12); read here, never tuned
MIN_RUNS = 8
SCREEN = ("SURVIVED", "HELD", "CULLED", "NOT_REACHED")
PROGRESS_TOL = 1e-9


def load_worlds(path=WORLDS_R4) -> dict | None:
    p = pathlib.Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def active_variant(doc: dict) -> str:
    return f"{doc['q1_floor_policy']}|{doc['q2_policy']}"


def screen_of(doc: dict | None, world: str, pressure: str) -> dict:
    """The screen status of (world, pressure) under the file's active variant, read from the file only."""
    if doc is None:
        return {"status": "UNSCREENED", "why": "no worlds_r4.json"}
    variant = active_variant(doc)
    hits = [c for c in doc.get("cells", []) if c.get("world") == world and c.get("pressure") == pressure]
    if len(hits) != 1:
        return {"status": "UNSCREENED", "variant": variant, "why": f"{len(hits)} cells for {world} {pressure}"}
    v = (hits[0].get("verdicts") or {}).get(variant) or {}
    st = v.get("verdict")
    if v.get("cull_reason") == "NOT_REACHED":
        st = "NOT_REACHED"
    if st not in SCREEN:
        return {"status": "UNSCREENED", "variant": variant, "why": f"verdict {st!r} under {variant}"}
    return {"status": st, "variant": variant, "cell": hits[0], "floor": v.get("floor"),
            "cull_reason": v.get("cull_reason")}


def _ineligible(why: str, **kw) -> dict:
    return {"verdict": "INELIGIBLE", "why": why, **kw}


def s4_verdict(screen: dict, median: float, nbytes: int, runs: int, held=None,
               oracle_clean: bool = True, cheats_fail: bool = True) -> dict:
    """SWARM_R4 s4 from the screen's numbers (the cross-check on the judge)."""
    if screen["status"] != "SURVIVED":
        return _ineligible(screen["status"])
    if not oracle_clean:
        return _ineligible("oracles not clean")
    if not cheats_fail:
        return _ineligible("a cheat control did not fail")
    if runs < MIN_RUNS:
        return _ineligible(f"{runs} run seeds < {MIN_RUNS}")
    floor, base = screen.get("floor"), screen["cell"].get("baseline") or {}
    if floor is None or base.get("median") is None or base.get("bytes") is None:
        return _ineligible("worlds_r4.json lacks the variant floor or the baseline median/bytes")
    den = float(base["median"]) - float(floor)
    if not den > 0:
        return _ineligible(f"denominator {den} <= 0 on a SURVIVED cell (screen defect)")
    progress = (float(median) - float(floor)) / den
    out = {"progress": progress, "floor": float(floor), "baseline_median": float(base["median"]),
           "baseline_bytes": int(base["bytes"]), "bytes": int(nbytes), "variant": screen.get("variant")}
    if held is not None:
        from primordial.metric.ci import median_ci
        lo, hi = median_ci(list(held.values()) if isinstance(held, dict) else list(held))
        out["progress_ci"] = [(lo - float(floor)) / den, (hi - float(floor)) / den]
    if progress < 0:
        return {"verdict": "BELOW_FLOOR", **out}
    if progress >= PASS_PROGRESS and int(nbytes) < int(base["bytes"]):
        return {"verdict": "PASS", **out}
    return {"verdict": "FAIL", **out}


def _agrees(judge: dict, mine: dict) -> bool:
    if judge.get("verdict") != mine["verdict"]:
        return False
    if "progress" in mine:
        jp = judge.get("progress")
        return jp is not None and abs(float(jp) - mine["progress"]) <= PROGRESS_TOL
    return True


def compression_r4(qd: list[dict], lane: str, window, doc: dict | None, check=None) -> dict:
    """F12 compression axis, round 4: PASS on a SURVIVED cell, judged by check and confirmed from the screen."""
    from primordial.score.progress import _cell, _in
    if check is None:
        from primordial.ops.qd_ledger import check
    mine = [r for r in qd if r.get("cohort") == lane and not r.get("baseline") and not r.get("floor")
            and _in(r.get("ts"), window)]
    superseded = {(r["supersedes"]["exp_id"], _cell(r)) for r in mine if isinstance(r.get("supersedes"), dict)}
    tally: dict[str, int] = {}
    scored, mismatches = [], []
    for r in mine:
        f = r.get("fitness") or {}
        if r.get("status") != "record" or f.get("held64_median") is None or (r.get("exp_id"), _cell(r)) in superseded:
            continue
        c = r["cell"]
        nbytes, runs, held = int(r["footprint"]["genome_bytes"]), int(f.get("n_runs") or 0), f.get("held64_by_run_seed")
        scr = screen_of(doc, c["world"], c["pressure"])
        if scr["status"] != "SURVIVED":
            key = f"INELIGIBLE({scr['status']})"
            tally[key] = tally.get(key, 0) + 1
            continue
        mine_v = s4_verdict(scr, f["held64_median"], nbytes, runs, held)
        hl = list(held.values()) if isinstance(held, dict) else held
        judge = (check(qd, c["world"], c["pressure"], f["held64_median"], f.get("iqr") or 0.0, nbytes, runs,
                       held=hl) or {}).get("clause_a_r4")
        if judge is None:
            key = "NO_JUDGE"
        elif not _agrees(judge, mine_v):
            key = "MISMATCH"
            mismatches.append({"exp_id": r.get("exp_id"), "cell": list(_cell(r)), "judge": judge, "screen_s4": mine_v})
        else:
            key = judge["verdict"]
            if key == "PASS":
                scored.append({"exp_id": r.get("exp_id"), "cell": list(_cell(r)), "genome_bytes": nbytes,
                               "progress": mine_v["progress"], "progress_ci": mine_v.get("progress_ci")})
        tally[key] = tally.get(key, 0) + 1
    return {"value": len(scored), "verdicts": tally, "scored": scored, "mismatches": mismatches,
            "superseded_dropped": len(superseded), "variant": active_variant(doc) if doc else None}
