"""Substrate-Tester Fire #57 harness — process Aporia restart decisions.

Aporia commit 370b28c6 (2026-05-09 02:14) ratified substrate-tester's
pivot proposal + named 5 unified meta-primitives. Fire #57 processes
the response:

Lane 1 — verify decision parsing: confirm pivot/restart_decisions_2026-05-09.md
exists, contains expected meta-primitive names.
Lane 2 — mark 5 substrate-tester strategic-coordination tickets
(ST-fire41-002 through ST-fire45-002) as RESOLVED-PIVOT-ACCEPTED in
aporia_inbox.jsonl.
Lane 3 — file ack-and-plan-update ticket back to Aporia.

Outputs:
  charon/diagnostics/substrate_tester_fire_57_results.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


def lane_1_verify_decision_doc() -> Dict[str, Any]:
    target = REPO / "pivot" / "restart_decisions_2026-05-09.md"
    if not target.exists():
        return {"lane": "1_verify_decision_doc", "verdict": "FAIL", "reason": "decision doc missing"}

    text = target.read_text(encoding="utf-8")
    expected_meta_primitives = [
        "TensorNetwork",
        "ConstructiveExistenceWitness",
        "GenericityAlmostEverywhereCert",
        "RepresentationTheoreticInvariant",
        "MomentPolytope",
    ]
    found = {p: (p in text) for p in expected_meta_primitives}
    expected_phrases = [
        "Substrate-Tester pivot",
        "ACCEPTED",
        "5-tier",
        "RESOLVED-PIVOT-ACCEPTED",
    ]
    phrase_found = {p: (p in text) for p in expected_phrases}
    return {
        "lane": "1_verify_decision_doc",
        "doc_path": str(target.relative_to(REPO)).replace("\\", "/"),
        "doc_size_chars": len(text),
        "meta_primitives_found": found,
        "phrases_found": phrase_found,
        "verdict": ("PASS" if all(found.values()) and all(phrase_found.values())
                    else "FAIL"),
    }


def lane_2_verify_ticket_status_updated() -> Dict[str, Any]:
    inbox = REPO / "aporia" / "meta" / "queue" / "aporia_inbox.jsonl"
    if not inbox.exists():
        return {"lane": "2_verify_ticket_status_updated", "verdict": "FAIL"}
    targets = {
        "T-2026-05-08-ST-fire41-002",
        "T-2026-05-08-ST-fire42-002",
        "T-2026-05-08-ST-fire43-002",
        "T-2026-05-08-ST-fire44-002",
        "T-2026-05-08-ST-fire45-002",
    }
    statuses: Dict[str, str] = {}
    for line in inbox.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get("id") in targets:
            statuses[obj["id"]] = obj.get("status", "?")
    all_resolved = all(statuses.get(tid) == "RESOLVED-PIVOT-ACCEPTED" for tid in targets)
    return {
        "lane": "2_verify_ticket_status_updated",
        "n_targets": len(targets),
        "statuses": statuses,
        "all_resolved": all_resolved,
        "verdict": "PASS" if all_resolved else "FAIL",
    }


def lane_3_verify_ack_filed() -> Dict[str, Any]:
    inbox = REPO / "aporia" / "meta" / "queue" / "aporia_inbox.jsonl"
    if not inbox.exists():
        return {"lane": "3_verify_ack_filed", "verdict": "FAIL"}
    target_id = "T-2026-05-09-ST-fire57-001"
    found = False
    for line in inbox.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get("id") == target_id:
            found = True
            break
    return {
        "lane": "3_verify_ack_filed",
        "target_id": target_id,
        "found_in_inbox": found,
        "verdict": "PASS" if found else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 57,
        "posture": "process Aporia restart decisions; mark coordination chain RESOLVED",
        "lanes": [1, 2, 3],
        "lane_1": lane_1_verify_decision_doc(),
        "lane_2": lane_2_verify_ticket_status_updated(),
        "lane_3": lane_3_verify_ack_filed(),
        "aporia_response_summary": {
            "decision_1_pivot": "ACCEPTED",
            "decision_2_meta_primitives": [
                "TensorNetwork (Tier A++)",
                "ConstructiveExistenceWitness/StructuredEquivalenceClass (Tier B)",
                "GenericityAlmostEverywhereCert (Tier D)",
                "RepresentationTheoreticInvariant (Tier E)",
                "MomentPolytope/SecantVarietyEquation (Tier C)",
            ],
            "decision_3_ergon_sequence": "E007 first → E009 second → defer training",
            "tickets_collapsed_into_meta_primitives": 8,
        },
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_57_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1 (decision doc): {summary['lane_1']['verdict']}")
    print(f"Lane 2 (5 tickets RESOLVED): {summary['lane_2']['verdict']}")
    print(f"Lane 3 (ack filed): {summary['lane_3']['verdict']}")
    return summary


if __name__ == "__main__":
    run()
