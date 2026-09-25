"""FREEZE the Cycle-9 inner experiment. The only path that writes the freeze artifacts.

    python freeze.py

  1. every pre-freeze gate must PASS (run_gates.py);
  2. hashes are computed from source (proposed_hashes.compute); the manifest is written
     to MANIFEST_FROZEN.json and the hashes to FREEZE.json;
  3. CALIBRATION.json is produced ONLY here, by `controls.py --freeze`; if calibration is
     not PASS, FREEZE.json and MANIFEST_FROZEN.json are removed again (no half-freeze);
  4. the hashes are written into PREREGISTRATION.md's freeze block, which the protocol
     hash excludes by construction;
  5. run_campaign.verify_freeze() must then succeed - which proves writing the freeze
     block did not change the protocol hash.
The launch commit is recorded by run_campaign.py at launch (it refuses a dirty tree).
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main():
    if (HERE / "FREEZE.json").exists():
        print("already frozen; refusing to re-freeze (a frozen experiment is immutable)")
        return 2
    g = subprocess.run([sys.executable, "run_gates.py"], cwd=HERE, capture_output=True, text=True)
    if g.returncode != 0:
        print(g.stdout[-3000:])
        print("FREEZE REFUSED: gates did not pass")
        return 1
    import proposed_hashes as PH
    body, protocol, m, bad, panel = PH.compute()
    if bad:
        print("FREEZE REFUSED: manifest validation problems", bad[:5])
        return 1
    (HERE / "MANIFEST_FROZEN.json").write_text(json.dumps(m, sort_keys=True, indent=1))
    freeze = {"status": "FROZEN", "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "protocol_version": body["protocol_version"], "protocol_hash": protocol,
              "grammar_hash": body["grammar_hash"], "manifest_hash": body["manifest_hash"],
              "specimen_panel_hash": body["specimen_panel_hash"],
              "constants_sha256": body["constants_sha256"], "documents": body["documents"],
              "n_runs": m["n_runs"], "n_bundles": m["n_bundles"], "by_hypothesis": m["by_hypothesis"]}
    (HERE / "FREEZE.json").write_text(json.dumps(freeze, indent=1))
    c = subprocess.run([sys.executable, "controls.py", "--freeze"], cwd=HERE, capture_output=True, text=True)
    cal = HERE / "CALIBRATION.json"
    if c.returncode != 0 or not cal.exists() or json.loads(cal.read_text()).get("gate") != "PASS":
        for f in ("FREEZE.json", "MANIFEST_FROZEN.json", "CALIBRATION.json"):
            (HERE / f).unlink(missing_ok=True)
        print("FREEZE REFUSED: calibration not PASS; freeze artifacts removed")
        return 1
    pre = HERE / "PREREGISTRATION.md"
    t = pre.read_text(encoding="utf-8")
    block = ("<!-- FREEZE-BEGIN -->\n**FROZEN %s.**\n\n| hash | value |\n|---|---|\n"
             "| protocol | `%s` |\n| grammar | `%s` |\n| manifest | `%s` |\n| specimen panel | `%s` |\n"
             "| constants | `%s` |\n\n%d runs in %d bundles (%s). Calibration: `CALIBRATION.json` PASS.\n"
             "<!-- FREEZE-END -->") % (freeze["frozen_at"], protocol, freeze["grammar_hash"],
                                       freeze["manifest_hash"], freeze["specimen_panel_hash"],
                                       freeze["constants_sha256"], m["n_runs"], m["n_bundles"],
                                       json.dumps(m["by_hypothesis"]))
    head, rest = t.split("<!-- FREEZE-BEGIN -->", 1)
    t = head + block + rest.split("<!-- FREEZE-END -->", 1)[1]
    pre.write_text(t, encoding="utf-8")
    import run_campaign as RUN
    RUN.verify_freeze()
    print("FROZEN. protocol %s  manifest %s  runs %d" % (protocol, freeze["manifest_hash"], m["n_runs"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
