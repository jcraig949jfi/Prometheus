"""Code the CONTROL: principal coordination actions visible in Artemis's self-test ledger
(roles/Artemis/selftest/LEDGER.md). A lower bound: only what the orchestrator wrote down is counted.

    python3 control_count.py [LEDGER.md]  -> JSON
"""
import json
import re
import sys
from pathlib import Path

p = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[4] / "roles/Artemis/selftest/LEDGER.md")
rows, notes = [], []
for line in p.read_text().splitlines():
    if re.match(r"^R-\d\d \|", line):
        rows.append(line)
    elif line.startswith("- "):
        notes.append(line)
dispatched = {r.split(" |")[0] for r in rows if "| running |" in r}
completed = [r for r in rows if "| REPORT" in r]
salvage = [r for r in completed if re.search(r"Write( to REPORT\.md)? (was )?blocked|returned in (the worker's )?final (reply|message)|heredoc", r)]
audited = [r for r in completed if re.search(r"\| *(clean|CONTAMINATED|EXPOSED-NAMES|see audit line)", r)]
flagged = [r for r in completed if re.search(r"CONTAMINATED|EXPOSED-NAMES", r)]
cat = {
    "incident_or_mitigation": [n for n in notes if re.search(r"quota|mitigation|moved to|incident|symlink", n, re.I)],
    "isolation_rule_or_template_change": [n for n in notes if re.search(r"audit(-rule| classes)|template|clarification", n, re.I)],
    "concurrency_or_lease": [n for n in notes if re.search(r"concurrent|lease|Archaeon", n, re.I)],
    "routing_or_containment": [n for n in notes if re.search(r"blind-lane|notification|routed", n, re.I)],
    "scoring_shepherding": [n for n in notes if re.search(r"scor", n, re.I)],
}
out = {
    "source": str(p), "method": "regex coding of ledger rows/notes; lower bound",
    "runs_dispatched_manually": len(dispatched),
    "completions_noticed_and_recorded": len(completed),
    "isolation_audits_performed": len(audited),
    "isolation_flags_raised": len(flagged),
    "report_salvages": len(salvage),
    "notes_by_category": {k: len(v) for k, v in cat.items()},
    "notes_total": len(notes),
}
out["principal_actions_lower_bound"] = (out["runs_dispatched_manually"] + out["completions_noticed_and_recorded"]
                                        + out["isolation_audits_performed"] + out["report_salvages"] + out["notes_total"])
print(json.dumps(out, indent=1))
