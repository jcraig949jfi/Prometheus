"""The observatory: what a run leaves behind, and the MECHANICAL signals the scheduler is allowed to act on.

Promotion means "allocate more experiments", never "scientific claim accepted". Every trigger below is a frozen
predicate on a run summary (no semantic judgement, no LLM); the thresholds are constants of this module and are part
of the campaign's frozen configuration (their hash is recorded with the grammar hash)."""
from __future__ import annotations

import hashlib
import inspect
import json
import pathlib
from typing import Dict, List, Optional

from prometheus.z80atlas.world import ENDOGENOUS

T = {  # frozen thresholds
    "persistent_alive_fraction": 0.30,
    "replication_rate": 0.05,
    "hifi": 0.90,
    "compression_ratio": 0.70,
    "solvers": 1.0,
    "coexistence_fraction": 0.50,
    "novelty_hamming": 24,
}


def triggers(summary: Dict, vec: Dict[str, str], ticks: int, control_summary: Optional[Dict] = None, archive_tapes: Optional[List[bytes]] = None) -> Dict[str, bool]:
    s = summary; endo = vec["reproduction"] in ENDOGENOUS
    fr = s.get("first_replication") or {}
    fid = s.get("mean_fidelity_tail") or 0.0
    rr = s.get("replication_rate_tail") or 0.0
    span0 = fr.get("span"); span_tail = s.get("repro_span_tail")
    t = {
        # persistence is only informative where nothing external keeps the population alive
        "persistent": endo and s.get("alive_fraction", 0) >= T["persistent_alive_fraction"] and not s.get("extinct") and (s.get("deaths") or 0) >= s.get("cells", 0),
        "persistence_above_control": bool(control_summary) and s.get("alive_fraction", 0) > (control_summary or {}).get("alive_fraction", 0) + 0.1,
        "replication": endo and rr >= T["replication_rate"] and fid >= T["hifi"],
        "spontaneous_replication": endo and vec["init"] == "RANDOM" and bool(fr) and not fr.get("seeded") and fid >= T["hifi"] and rr >= T["replication_rate"],
        "novel_architecture": endo and rr >= T["replication_rate"] and (s.get("arch_clusters_final") or 0) >= 3,
        "reproductive_compression": endo and bool(span0) and bool(span_tail) and span_tail <= T["compression_ratio"] * span0,
        "task_reproduction_coupling": endo and rr >= T["replication_rate"] and (s.get("solvers_tail") or 0) >= T["solvers"],
        "task_score": (s.get("solvers_tail") or 0) >= T["solvers"],
        "moat_crossing": bool(s.get("first_crossing")) and (vec["read_gate"] == "FORCED" or vec["task"] in ("COND_ONE", "COND_MULTI", "SUM2")),
        "escape": bool(s.get("escape_events")),
        "cross_niche_transport": (s.get("cross_niche_transport") or 0) >= 0.05 * s.get("cells", 10 ** 9) and vec["world"] == "NICHES",
        "environment_lineage": bool(s.get("env_lineage")),
        # coexistence = a FEW lineages stably sharing the world after turnover, not the un-collapsed initial diversity
        "coexistence": (s.get("coexistence_ticks") or 0) >= T["coexistence_fraction"] * ticks and 2 <= (s.get("lineages_final") or 0) <= 8
                       and (s.get("deaths") or 0) >= 2 * s.get("cells", 10 ** 9),
        "exploit_recorded": (s.get("n_exploits") or 0) > 0,
    }
    # novelty distance from the campaign specimen archive -- only a FUNCTIONAL specimen (it replicates or solves)
    # can be novel; random bytes are always far from everything
    top0 = (s.get("top") or [{}])[0]; top = top0.get("tape")
    functional = bool(top) and ((top0.get("replications") or 0) > 0 and fid >= T["hifi"] or (top0.get("score_ema") or 0) >= 0.85)
    if functional and archive_tapes:
        tb = bytes.fromhex(top)
        d = min(sum(1 for x, y in zip(tb, a) if x != y) for a in archive_tapes)
        t["novelty_distance"] = d >= T["novelty_hamming"]
    else:
        t["novelty_distance"] = functional and not archive_tapes
    return t


PROMOTING = ("persistence_above_control", "replication", "spontaneous_replication", "novel_architecture",
             "reproductive_compression", "task_reproduction_coupling", "task_score", "moat_crossing", "escape",
             "cross_niche_transport", "environment_lineage", "coexistence", "novelty_distance")


def trigger_score(t: Dict[str, bool]) -> int:
    return sum(1 for k in PROMOTING if t.get(k))


def high_value_flags(runs_by_family: Dict[str, List[Dict]], vec_of: Dict[str, Dict[str, str]]) -> List[Dict]:
    """The SPECIAL HIGH-VALUE RESULTS, computed across matched pairs (a family and its one-axis control)."""
    flags = []
    def solved(rs):
        return any((r["summary"].get("solvers_tail") or 0) >= 1 for r in rs)
    fam_ids = [f for f in runs_by_family if f in vec_of]
    by_vec = {json.dumps(vec_of[f], sort_keys=True): f for f in fam_ids}
    for f in fam_ids:
        v = vec_of[f]; rs = runs_by_family[f]
        if not rs:
            continue
        # endogenous reaches a computation its external control cannot
        if v["reproduction"] in ENDOGENOUS and solved(rs):
            cv = dict(v, reproduction="EXTERNAL")
            g = by_vec.get(json.dumps(cv, sort_keys=True))
            if g and runs_by_family.get(g) and not solved(runs_by_family[g]):
                flags.append({"flag": "REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL", "family": f, "control_family": g, "task": v["task"]})
        # incremental reaches what atomic cannot
        if v["scoring"] == "INCREMENTAL" and solved(rs):
            cv = dict(v, scoring="ATOMIC")
            g = by_vec.get(json.dumps(cv, sort_keys=True))
            if g and runs_by_family.get(g) and not solved(runs_by_family[g]):
                flags.append({"flag": "REACHED_INCREMENTAL_NOT_ATOMIC", "family": f, "control_family": g, "task": v["task"]})
        # reservoir crossing: solved with a reservoir, not without migration
        if v["spatial"] == "RESERVOIR" and solved(rs):
            cv = dict(v, spatial="NICHES_ISOLATED")
            g = by_vec.get(json.dumps(cv, sort_keys=True))
            if g and runs_by_family.get(g) and not solved(runs_by_family[g]):
                flags.append({"flag": "RESERVOIR_CROSSED_MOAT", "family": f, "control_family": g, "task": v["task"]})
        # reproductive architecture changed with task demand: span compression + task coupling in the same run
        for r in rs:
            tr = r.get("triggers", {})
            if tr.get("reproductive_compression") and tr.get("task_reproduction_coupling"):
                flags.append({"flag": "REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK", "family": f, "run": r["id"]})
            geo = r.get("geometry") or {}
            if geo.get("beneficial_density_gain") and geo["beneficial_density_gain"] > 0.1:
                flags.append({"flag": "REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY", "family": f, "run": r["id"], "gain": geo["beneficial_density_gain"]})
    # dedupe
    seen = set(); out = []
    for fl in flags:
        k = json.dumps(fl, sort_keys=True)
        if k not in seen:
            seen.add(k); out.append(fl)
    return out


def thresholds_hash() -> str:
    return hashlib.sha256((json.dumps(T, sort_keys=True) + inspect.getsource(triggers)).encode()).hexdigest()


def write_json(path: pathlib.Path, obj) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, default=str), encoding="utf-8", newline="\n")


def write_jsonl(path: pathlib.Path, rows: List[Dict]) -> None:
    path.write_text("".join(json.dumps(r, sort_keys=True, default=str) + "\n" for r in rows), encoding="utf-8", newline="\n")
