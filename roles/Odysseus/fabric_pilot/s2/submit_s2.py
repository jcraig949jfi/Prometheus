"""S2: submit every claim-verification Task in one command (PREREG.md s3). Idempotent (keys s2-<claim>-r<n>)."""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
base = sys.argv[1]
template = (HERE / "VERIFY_TEMPLATE.md").read_text()
rows = [l for l in (HERE / "PREREG.md").read_text().splitlines() if re.match(r"^\| C\d \|", l)]
out = []
for row in rows:
    cid, claim, src = [c.strip() for c in row.strip("|").split("|")][:3]
    prompt = HERE / ("prompt_%s.md" % cid)
    prompt.write_text(template + "\n[%s] %s\n(Source of the claim: %s in roles/Artemis/selftest/runs/R-13 or R-34 REPORT.md, "
                      "or comms #889.)\n" % (cid, claim, src))
    r = subprocess.run([sys.executable, "-m", "fabric", "submit", "--as", "Odysseus", "--cap", "research.repo_readonly",
                        "--executor", "claude", "--model", "claude-opus-5-5", "--wall-s", "2400", "--base", base,
                        "--prompt-file", str(prompt), "--thread", "thr-fabric-s2", "--replicas", "2", "--max-attempts", "1",
                        "--key", "s2-" + cid, "--title", "S2 verify " + cid],
                       cwd=str(REPO), capture_output=True, text=True, check=True)
    for t in json.loads(r.stdout):
        out.append({"claim": cid, "task_id": t["task_id"]})
(HERE / "TASKS.json").write_text(json.dumps(out, indent=1))
print(len(out), "tasks submitted")
