"""The founding crucible driver: SOURCE -> REPRESENT -> PROPOSE -> EXECUTE ->
MEASURE -> PROBE NEIGHBOURS -> RECORD -> QUEUE OR KILL -> REPLAY.

    python -m theophrastus.crucible coverage     # 25 preregistered cells
    python -m theophrastus.crucible contrasts    # score the declared families
    python -m theophrastus.crucible replicate    # seed 20260914 for candidates + anchors
    python -m theophrastus.crucible replay       # same spec_hash, fresh world, twice
    python -m theophrastus.crucible report       # summary JSON to stdout

Every phase refuses to run from the canonical checkout, charges the ONE
founding budget (persisted in ledgers/budget.json), and appends rows as it
goes; nothing lives only in memory.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from archaeon import workspace as _ws              # noqa: E402
from theophrastus import contrast as X             # noqa: E402
from theophrastus import controls as K             # noqa: E402
from theophrastus import ecology as E              # noqa: E402
from theophrastus.cell import Cell                 # noqa: E402
from theophrastus.ledger import Ledger, now        # noqa: E402

REG_WORLDS = {w.label: w.identity for w in E.WORLDS.values()}
ENGINE_FILE = "budget.json"


# ------------------------------------------------------------ persistence
def _budget(ledger: Ledger) -> K.Budget:
    p = ledger.dir / ENGINE_FILE
    b = K.Budget(E.BUDGET_EXECUTIONS, E.BUDGET_WALL_S)
    if p.exists():
        st = json.loads(p.read_text(encoding="utf-8"))
        b.executions = int(st.get("executions", 0))
        b.t0 = time.monotonic() - float(st.get("wall_s", 0.0))
    return b


def _save_budget(ledger: Ledger, b: K.Budget) -> None:
    (ledger.dir / ENGINE_FILE).write_text(json.dumps(b.state(), indent=1), encoding="utf-8")


def _latest_rows(ledger: Ledger) -> Dict[str, dict]:
    """spec_hash -> the latest COMPLETED row (or the latest row if none completed),
    ignoring rows tagged as replays (they are scored by check_replay, not here)."""
    out: Dict[str, dict] = {}
    for r in ledger.read("rows"):
        if r.get("phase") == "replay":
            continue
        h = r["spec_hash"]
        cur = out.get(h)
        if cur is None or (r.get("status") == "COMPLETED" and cur.get("status") != "COMPLETED"):
            out[h] = r
    return out


def _by_labels(rows: Dict[str, dict], seed: int) -> Dict[tuple, dict]:
    out = {}
    for r in rows.values():
        l = r["labels"]
        if l["seed_root"] != seed:
            continue
        out[(l["mechanism"], l["world"], l["pressure"], l["intervention"])] = r
    return out


# --------------------------------------------------------------- execute
def _run_batch(ledger: Ledger, cells: List[Cell], *, phase: str,
               allow_duplicates: bool = False, mode: str = "coverage") -> dict:
    from theophrastus.adapter import Adapter       # noqa: PLC0415  (network)
    executed = {r["spec_hash"] for r in ledger.read("rows") if r.get("status") == "COMPLETED"}
    findings = K.check_batch(cells, registered_worlds=REG_WORLDS,
                             executed_spec_hashes=() if allow_duplicates else executed)
    accepted, refused = [], []
    for c in cells:
        f = findings[c.cell_id]
        rec = {"phase": phase, "cell_id": c.cell_id, "spec_hash": c.spec_hash,
               "execution_hash": c.execution_hash, "labels": c.labels,
               "cell": c.record(), "findings": f}
        if any(x["refuse"] for x in f):
            rec["accepted"] = False
            refused.append(c)
        else:
            rec["accepted"] = True
            accepted.append(c)
        ledger.append("cells", rec)
    order = K.select(accepted, dead=ledger.dead_cell_ids(), mode=mode)
    skipped_dead = [c for c in accepted if c not in order]
    for c in skipped_dead:
        ledger.append("cells", {"phase": phase, "cell_id": c.cell_id, "labels": c.labels,
                                "accepted": True, "executed": False,
                                "why": "inside a recorded dead neighbourhood (mode=%s)" % mode})
    budget = _budget(ledger)
    adapter = Adapter(ledger)
    done, blocked = [], []
    for c in order:
        charge = budget.charge()
        _save_budget(ledger, budget)
        if charge["refuse"]:
            ledger.append("cells", {"phase": phase, "cell_id": c.cell_id, "labels": c.labels,
                                    "accepted": True, "executed": False, "findings": [charge]})
            blocked.append(c)
            continue
        t0 = time.perf_counter()
        print("[theo] %s %s" % (phase, c.short()), flush=True)
        row = adapter.execute(c, attempt_tag=phase[:3], phase=phase,
                              budget_state=budget.state())
        ledger.append("cells", {"phase": phase, "cell_id": c.cell_id, "labels": c.labels,
                                "executed": True, "row_id": row["row_id"],
                                "status": row["status"], "outcome": row.get("outcome"),
                                "budget_after": budget.state(),
                                "adapter_wall_s": round(time.perf_counter() - t0, 3)})
        _save_budget(ledger, budget)               # wall includes this execution
        done.append(row)
    return {"phase": phase, "proposed": len(cells), "refused": len(refused),
            "accepted": len(accepted), "skipped_dead": len(skipped_dead),
            "executed": len(done), "budget_blocked": len(blocked),
            "completed": sum(1 for r in done if r["status"] == "COMPLETED"),
            "failed": sum(1 for r in done if r["status"] != "COMPLETED"),
            "budget": budget.state()}


# ------------------------------------------------------------- contrasts
def score_contrasts(ledger: Ledger, *, final: bool) -> dict:
    rows = _latest_rows(ledger)
    prim = _by_labels(rows, E.SEED_PRIMARY)
    rep = _by_labels(rows, E.SEED_REPLICATION)
    n = E.REPEAT.count
    out = {"eligible": 0, "declared": 0, "by_disposition": {}, "candidates": [],
           "contrasts": []}
    for d in X.declared_contrasts():
        a, b = prim.get(d["a"]), prim.get(d["b"])
        ev = X.evaluate(a, b, expected_repeats=n,
                        a_rep=rep.get(d["a"]) if final else None,
                        b_rep=rep.get(d["b"]) if final else None)
        rec = {"phase": "contrasts_final" if final else "contrasts_primary",
               "family": d["family"], "signal_type_if_fired": X.SIGNAL_TYPE[d["family"]],
               "labels_a": d["a"], "labels_b": d["b"],
               "rows_a": [a["row_id"]] if a else [], "rows_b": [b["row_id"]] if b else [],
               "cell_a": a["cell_id"] if a else None, "cell_b": b["cell_id"] if b else None,
               "stencil_cells": _stencil_for(d, prim), **ev}
        if "replication" in ev and isinstance(ev["replication"], dict):
            ra, rb = rep.get(d["a"]), rep.get(d["b"])
            rec["replication"]["rows"] = [ra["row_id"] if ra else None, rb["row_id"] if rb else None]
        ledger.append("contrasts", rec)
        out["declared"] += 1
        out["eligible"] += int(ev["eligible"])
        out["by_disposition"][ev["disposition"]] = out["by_disposition"].get(ev["disposition"], 0) + 1
        if ev.get("z") is not None and abs(ev["z"]) >= X.K_CANDIDATE:
            out["candidates"].append({"family": d["family"], "a": d["a"], "b": d["b"],
                                      "delta": ev["delta"], "z": ev["z"],
                                      "disposition": ev["disposition"]})
        out["contrasts"].append({"family": d["family"], "a": d["a"], "b": d["b"],
                                 "disposition": ev["disposition"],
                                 "delta": ev.get("delta"), "z": ev.get("z")})
    return out


def _stencil_for(d: dict, prim: Dict[tuple, dict]) -> List[str]:
    """The neighbouring cells that were actually executed around this
    contrast: every executed cell sharing >= 3 of the 4 label coordinates
    with either side, excluding the two sides."""
    out = set()
    for key, r in prim.items():
        for side in (d["a"], d["b"]):
            if key != side and sum(1 for i in range(4) if key[i] == side[i]) >= 3:
                out.add(r["cell_id"])
    return sorted(out)


# ------------------------------------------------------ queue or kill
def queue_or_kill(ledger: Ledger, scored: dict) -> dict:
    """Emit THEO-SIGNAL rows for admitted contrasts; record dead neighbourhoods
    for cells whose every contrast is NO_SIGNAL or INSTRUMENT-exact-zero."""
    signals, refused = [], []
    existing = sum(1 for _ in ledger.read("signals"))
    finals = [r for r in ledger.read("contrasts") if r.get("phase") == "contrasts_final"]
    for r in finals:
        gate = K.admit_signal(r)
        if gate["refuse"]:
            if r.get("disposition") == "REPRODUCIBLE_SIGNAL":
                refused.append({"family": r["family"], "gate": gate})
            continue
        existing += 1
        sig = {"signal_id": "THEO-SIGNAL-%04d" % existing,
               "disposition": r["disposition"], "signal_type": r["signal_type_if_fired"],
               "family": r["family"], "source_cells": [r["cell_a"], r["cell_b"]],
               "labels": {"a": r["labels_a"], "b": r["labels_b"]},
               "measured_contrast": {"delta": r["delta"], "se_delta": r["se_delta"], "z": r["z"]},
               "replication": r.get("replication"), "nearest_controls": r["stencil_cells"],
               "replication_count": 2, "rows": {"a": r["rows_a"], "b": r["rows_b"]},
               "why_queued": "pre-declared family %s cleared the 4-SE bar in the primary "
                             "pass and the replication pass with the same sign" % r["family"],
               "obvious_alternatives": ["IC sampling at n=800 per cell (bounded by SE)",
                                        "a horizon/step convention effect (C-RES stencil reports it)",
                                        "the transform implementation rather than the mechanism (C-INTERV)"],
               "representation_uncertainties": ["branch relation carried as sibling_of with "
                                                "published-characterisation evidence only; "
                                                "ancestry UNKNOWN"],
               "estimated_deeper_cost": "n_ic 1000 x repeat 8 at N in {149, 599, 999}: ~10 min",
               "gate": gate}
        ledger.append("signals", sig)
        signals.append(sig)
    # dead terrain: a cell whose contrasts are all NO_SIGNAL AND whose accuracy
    # is exactly 0 under the unbiased ensemble is structurally dead (maj)
    dead = []
    rows = _latest_rows(ledger)
    for r in rows.values():
        st = X.cell_stat(r, E.REPEAT.count)
        if st.get("ok") and st["p"] == 0.0:
            dead.append(r["cell_id"])
            ledger.append("dead", {"cell_id": r["cell_id"], "labels": r["labels"],
                                   "why": "accuracy exactly 0 over %d ICs; structural "
                                          "zero (MAJ_STRUCTURAL_ZERO.md)" % st["n"],
                                   "row_id": r["row_id"]})
    return {"signals": len(signals), "refused_at_gate": refused, "dead_recorded": len(dead),
            "signal_ids": [s["signal_id"] for s in signals]}


# ----------------------------------------------------------------- replay
def replay(ledger: Ledger, cells: List[Cell]) -> dict:
    res = _run_batch(ledger, cells, phase="replay", allow_duplicates=True, mode="expansion")
    by_hash = {}
    for r in ledger.read("rows"):
        by_hash.setdefault(r["spec_hash"], []).append(r)
    findings = {}
    for c in cells:
        f = K.check_replay(by_hash.get(c.spec_hash, []))
        findings[c.short()] = f
        ledger.append("cells", {"phase": "replay_check", "cell_id": c.cell_id,
                                "spec_hash": c.spec_hash, "labels": c.labels, "findings": f})
    return {**res, "replay_findings": findings}


# ----------------------------------------------------------------- report
def report(ledger: Ledger) -> dict:
    rows = list(ledger.read("rows"))
    cells = list(ledger.read("cells"))
    contrasts = list(ledger.read("contrasts"))
    finals = [c for c in contrasts if c.get("phase") == "contrasts_final"]
    prim = [c for c in contrasts if c.get("phase") == "contrasts_primary"]
    def disp(cs):
        d = {}
        for c in cs:
            d[c["disposition"]] = d.get(c["disposition"], 0) + 1
        return d
    wall = sum(float(r.get("elapsed_s") or 0) for r in rows)
    return {"generated": now(), "workspace": _ws.receipt(),
            "rows": len(rows), "completed": sum(1 for r in rows if r["status"] == "COMPLETED"),
            "failed": [{"row": r["row_id"], "class": r.get("failure_class"), "labels": r["labels"]}
                       for r in rows if r["status"] != "COMPLETED"],
            "distinct_spec_hashes": len({r["spec_hash"] for r in rows}),
            "pew_written": sum(1 for r in rows if (r.get("pew") or {}).get("written")),
            "outcomes": {o: sum(1 for r in rows if r.get("outcome") == o)
                         for o in ("SURVIVED", "FALSIFIED", "INCONCLUSIVE", None)},
            "proposed": sum(1 for c in cells if "accepted" in c),
            "refused": sum(1 for c in cells if c.get("accepted") is False),
            "contrasts_primary": {"n": len(prim), "eligible": sum(1 for c in prim if c["eligible"]),
                                  "dispositions": disp(prim)},
            "contrasts_final": {"n": len(finals), "eligible": sum(1 for c in finals if c["eligible"]),
                                "dispositions": disp(finals)},
            "signals": [s["signal_id"] + " " + s["family"] + " " + s["signal_type"]
                        for s in ledger.read("signals") if "signal_id" in s],
            "signal_annotations": sum(1 for s in ledger.read("signals") if "annotation_of" in s),
            "dead": len(list(ledger.read("dead"))),
            "budget": json.loads((ledger.dir / ENGINE_FILE).read_text()) if (ledger.dir / ENGINE_FILE).exists() else None,
            "executor_wall_s_total": round(wall, 1)}


# ------------------------------------------------------------------- main
def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__); return 2
    _ws.assert_not_canonical("theophrastus crucible")
    ledger = Ledger()
    phase = argv[0]
    if phase == "coverage":
        cells = (E.coverage_pass() + E.intervention_stencil() + E.resource_stencil()
                 + E.exact_null_stencil())
        out = _run_batch(ledger, cells, phase="coverage")
    elif phase == "contrasts":
        out = score_contrasts(ledger, final=False)
    elif phase == "replicate":
        scored = score_contrasts(ledger, final=False)
        need = {}
        for c in scored["candidates"]:
            for side in (c["a"], c["b"]):
                need[side] = E.cell(side[0], side[1], side[2], side[3], E.SEED_REPLICATION,
                                    "prereg:replication:candidate")
        for a in E.anchors():
            key = (a.labels["mechanism"], a.labels["world"], a.labels["pressure"], a.labels["intervention"])
            need.setdefault(key, a)
        out = _run_batch(ledger, list(need.values()), phase="replicate", mode="expansion")
        out["final"] = score_contrasts(ledger, final=True)
        out["queue_or_kill"] = queue_or_kill(ledger, out["final"])
    elif phase == "replay":
        out = replay(ledger, [E.cell("GKL", "W149", "P_iid", "NONE", proposer="prereg:replay"),
                              E.cell("exp", "W599", "P_iid", "NONE", proposer="prereg:replay")])
    elif phase == "report":
        out = report(ledger)
    else:
        print("unknown phase", phase); return 2
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
