"""Populate the corridor table from campaign-2 evidence (mature sources only; instrument, not
transfer claims): C2-SFE-03 mature W0 sources -> W2_K2 (segments of solved organisms as
generation-0 material), C2-SFE-04 solved W0 populations -> W3_K2 (direct reuse + init),
C2-SFE-05 W2_K2 streams -> sealed query cells (direct reuse ceilings), C2-SFE-06 the delay
ladder W0 > W1_d1 > W1_d2 > W1_d4 (route), C2-SFE-07 W0 producer elites -> W2_K2 (injection).

    python -m archaeon.campaign3.corridor_import
"""
from __future__ import annotations

import json
from pathlib import Path

from archaeon.wse import corridor as CT
from archaeon.wse import reachability as R

REPO = Path(__file__).resolve().parents[2]
C2 = REPO / "archaeon" / "campaign2"
F16 = R.default_foundry_id()


def _rows(exp: str):
    p = C2 / exp / "rows.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def _rec(exp: str):
    p = C2 / exp / "RECEIPT.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _init(r: dict, dose: int, N: int) -> dict:
    tb = r.get("trace_best") or []
    best = max(tb) if tb else 0.0
    return {"dose": dose, "N": N, "level": R.level_of(best, r.get("competence_heldout")), "first_foothold_gen": r.get("first_solved_gen"),
            "first_shelf_gen": R.first_at(tb, R.SHELF_MIN), "summit_candidate_gen": R.first_at(tb, R.SUMMIT_MIN),
            "first_summit_gen": (R.first_at(tb, R.SUMMIT_MIN) if (r.get("competence_heldout") or 0) >= R.SUMMIT_MIN else None),
            "seed": r.get("seed"), "heldout": r.get("competence_heldout")}


def main() -> dict:
    rows = []
    src = {"campaign": "cmp2"}
    # C2-SFE-03: components (segments) of SOLVED W0 sources spliced into every gen-0 organism of a W2_K2 search
    rec = _rec("C2-SFE-03")
    for r in _rows("C2-SFE-03"):
        if r["arm"] == "mature_source":
            rows.append(CT.row(source_cell="W0", target_cell="W2_K2", kind="init", source=dict(src, experiment="C2-SFE-03", arm="mature_source", attempt=2),
                               source_maturity={"solved": True, "note": "pooled segments of 10 solved W0 sources (first solved 0-31)"}, source_competence=1.0,
                               source_foundry=F16, target_foundry=F16, source_budget={"N": 200, "G": 100, "E": 16}, target_budget={"N": 200, "G": 60, "E": 16},
                               init=_init(r, 200, 200) | {"material": "2-4 instruction segments, one per organism"},
                               note="segments, not whole organisms; every gen-0 organism modified"))
    # C2-SFE-04: whole solved W0 populations (100 of 100) as generation 0 of a W3_K2 search; direct reuse recorded
    rec4 = _rec("C2-SFE-04")
    for r in _rows("C2-SFE-04"):
        if r["arm"] == "evolved_solved":
            s = rec4.get("sources", {}).get("solved", {}).get(str(r["seed"]), {})
            rows.append(CT.row(source_cell="W0", target_cell="W3_K2", kind="init", source=dict(src, experiment="C2-SFE-04", arm="evolved_solved", attempt=2),
                               source_maturity={"solved": bool(s.get("solved")), "elite": s.get("elite"), "first_solved_gen": s.get("first_solved_gen")},
                               source_competence=s.get("elite"), source_foundry=F16, target_foundry=F16, source_budget={"N": 200, "G": 60, "E": 16},
                               target_budget={"N": 100, "G": 40, "E": 16}, direct_reuse={"best": r.get("direct_best"), "n_sources": 100},
                               init=_init(r, 100, 100) | {"material": "final population of the solved source (rebuilt manifests)"}))
    # C2-SFE-05: W2_K2 stream organisms (top-64 by source score) on the sealed query cells: direct reuse only
    rec5 = _rec("C2-SFE-05")
    qcells = {"q00": "W0", "q01": "W1_d1", "q02": "W1_d4", "q03": "W1_d16", "q04": "W3_K2"}
    for s, v in rec5.get("per_seed", {}).items():
        mat = v.get("maturity", {})
        for q, cell in qcells.items():
            rows.append(CT.row(source_cell="W2_K2", target_cell=cell, kind="direct", source=dict(src, experiment="C2-SFE-05", arm="stream_s%s" % s, attempt=2),
                               source_maturity={"solved": mat.get("solved"), "elite": mat.get("source_elite_reward")}, source_competence=mat.get("source_elite_reward"),
                               source_foundry=F16, target_foundry=F16, source_budget={"N": 200, "G": v.get("generations"), "E": 16},
                               direct_reuse={"best": v["ceiling"].get(q), "n_sources": 64},
                               note="stream top-64 by source score; source at the shelf (solved=%s)" % mat.get("solved")))
    # C2-SFE-06: the delay ladder as a ROUTE (p >= 0.1 arms); level on W1_d4 at the end from the rung-3 competence
    for r in _rows("C2-SFE-06"):
        if r["p"] >= 0.1:
            fin = r.get("final_r3"); peak = r.get("peak_r3")
            rows.append(CT.row(source_cell="ladder:W0>W1_d1>W1_d2>W1_d4(p=%s)" % r["p"], target_cell="W1_d4", kind="ladder",
                               source=dict(src, experiment="C2-SFE-06", arm=r["arm"], attempt=2), source_maturity={"route": True}, source_foundry=F16, target_foundry=F16,
                               target_budget={"N": 200, "G": 100, "E": 16, "rung_gens": 25},
                               init={"level": ("SUMMIT" if (fin or 0) >= R.SUMMIT_MIN else "SHELF" if (fin or 0) >= R.SHELF_MIN else "FLOOR"), "seed": r["seed"],
                                     "final_r3": fin, "peak_r3": peak, "first_summit_gen": next((m["gen"] for m in r.get("matrix", []) if m.get("R3", 0) >= R.SUMMIT_MIN), None)},
                               note="revisit share p; competence on delay 4 probed every 5 generations"))
    # C2-SFE-07: W0 producer elites injected into a running W2_K2 consumer (parallel arm)
    rec7 = _rec("C2-SFE-07")
    for r in _rows("C2-SFE-07"):
        if r["arm"] == "parallel" and r.get("imported"):
            p = rec7.get("producers", {}).get(str(r["seed"]), {})
            rows.append(CT.row(source_cell="W0", target_cell="W2_K2", kind="init", source=dict(src, experiment="C2-SFE-07", arm="parallel", attempt=2),
                               source_maturity={"solved": True, "elite": p.get("elite"), "first_solved_gen": p.get("first_solved_gen")}, source_competence=p.get("elite"),
                               source_foundry=F16, target_foundry=F16, source_budget={"N": 200, "G": p.get("generations"), "E": 16}, target_budget={"N": 200, "G": 60, "E": 16},
                               init=_init(r, 4, 200) | {"material": "top-4 elites injected at generation %s" % r.get("arrival_gen"), "arrival_gen": r.get("arrival_gen")}))
    n = CT.record(rows)
    return {"candidate_rows": len(rows), "appended": n}


if __name__ == "__main__":
    print(main())
    print(CT.table_text())
