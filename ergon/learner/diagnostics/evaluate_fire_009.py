"""One-off evaluator for fire-009 v2 responses (decomposition_mode aware)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ergon.learner.diagnostics.probe_evaluator import (  # noqa: E402
    evaluate, make_ticket, _next_ticket_id, _now_iso,
)


def main() -> int:
    probes = json.loads(Path("ergon/learner/diagnostics/fire_009_probes.json").read_text(encoding="utf-8"))
    responses_v2 = json.loads(Path("ergon/learner/diagnostics/fire_009_responses.json").read_text(encoding="utf-8"))
    inbox = Path("aporia/meta/queue/ergon_inbox.jsonl")
    fire_id = "009"
    max_tickets = 5

    by_id = {r["id"]: r for r in responses_v2}
    today_str = datetime.now(timezone.utc).isoformat(timespec="seconds")[:10]
    next_idx = _next_ticket_id(inbox, today_str)

    evaluations = []
    tickets = []
    for probe in probes:
        pid = probe["id"]
        rec = by_id.get(pid)
        if rec is None:
            evaluations.append({"probe_id": pid, "verdict": "USELESS", "sub_type": "missing_response"})
            continue

        modes = list(rec["responses"].keys())  # e.g. ["ON","OFF"] or ["N/A"] or ["OFF"]
        for mode in modes:
            resp_v1 = {"completion": rec["responses"][mode]["completion"]}
            verdict, sub_type, severity = evaluate(probe, resp_v1)
            ev = {
                "probe_id": pid,
                "lane": probe.get("lane"),
                "decomp_mode": mode,
                "verdict": verdict,
                "sub_type": sub_type,
                "severity": severity,
                "completion_preview": resp_v1["completion"][:200],
            }
            evaluations.append(ev)
            if verdict == "USELESS" and len(tickets) < max_tickets:
                tid = f"T-{today_str}-{next_idx:04d}"
                next_idx += 1
                t = make_ticket(tid, probe, resp_v1, sub_type, severity)
                t["payload"]["decomposition_mode"] = mode
                tickets.append(t)

    inbox.parent.mkdir(parents=True, exist_ok=True)
    with inbox.open("a", encoding="utf-8") as f:
        for t in tickets:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    report = {
        "fire_id": fire_id,
        "computed_at": _now_iso(),
        "n_probes": len(probes),
        "evaluations": evaluations,
        "tickets_filed": [t["id"] for t in tickets],
        "useless_count": sum(1 for e in evaluations if e["verdict"] == "USELESS"),
        "useful_count": sum(1 for e in evaluations if e["verdict"] == "USEFUL"),
    }
    Path("ergon/learner/diagnostics/fire_eval.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    print(f"[fire {fire_id}] {report['useful_count']} USEFUL, "
          f"{report['useless_count']} USELESS, {len(tickets)} tickets filed")
    for e in evaluations:
        mode = e.get("decomp_mode", "?")
        print(f"  {e['probe_id']} [{e['lane']}|{mode}] -> {e['verdict']} ({e['sub_type']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
