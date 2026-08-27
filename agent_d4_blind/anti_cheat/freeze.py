"""Freeze the Phase-1 constitution: stamp threshold status and hash frozen
files. NO semantic changes — v4 rule after the red team confirmed that
rewriting thresholds at freeze time binds an instrument that never ran on
the controls. The gates.py in force at the last full validation run is the
gates.py that gets hashed, byte-identical except the status stamp.

Run exactly once, after instrument validity is confirmed under the exact
final code, and after the adversarial-review findings are resolved.
"""
from __future__ import annotations

import hashlib
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FROZEN_FILES = [
    "PREREG-INSTRUMENT.md",
    "PREREG-PHASE1.md",
    "d4core/interface.py",
    "d4core/synthetic.py",
    "d4core/navigators.py",
    "d4core/metrics.py",
    "d4core/classifier.py",
    "d4core/oracle.py",
    "d4core/gates.py",
    "d4core/pipeline.py",
    "substrates/vm_substrates.py",
    "substrates/run_phase1.py",
    "anti_cheat/static_checks.py",
]


def main():
    # 1. status stamp only (no threshold values change)
    gp = os.path.join(BASE, "d4core", "gates.py")
    s = open(gp, encoding="utf-8").read()
    assert '"status": "CALIBRATING"' in s or '"status": "FROZEN-2026-08-27"' in s
    s = s.replace('"status": "CALIBRATING"', '"status": "FROZEN-2026-08-27"')
    open(gp, "w", encoding="utf-8", newline="\n").write(s)

    # 2. hash frozen files
    hashes = {}
    for rel in FROZEN_FILES:
        h = hashlib.sha256(open(os.path.join(BASE, rel), "rb").read()).hexdigest()
        hashes[rel] = h

    # 3. record
    with open(os.path.join(BASE, "anti_cheat", "frozen_hashes.json"), "w") as fh:
        json.dump({"frozen": "2026-08-27", "note": "status stamp is the only "
                   "byte difference from the validated gates.py",
                   "sha256": hashes}, fh, indent=1)
    pp = os.path.join(BASE, "PREREG-PHASE1.md")
    s = open(pp, encoding="utf-8").read()
    lines = ["## FROZEN (2026-08-27)", "",
             "- thresholds: FROZEN-2026-08-27, byte-identical to the values "
             "used in the final full instrument-validation run (status stamp "
             "is the only change).",
             "- file hashes (SHA-256):"]
    for rel, h in hashes.items():
        lines.append(f"  - {rel}: {h}")
    lines.append("- binding runs: substrates/run_phase1.py {S1_REG,S2_STACK,"
                 "S3_REWRITE,S4_MEM}, executed once each after the freeze commit.")
    import re
    s = re.sub(r"## FROZEN[\s\S]*$", "\n".join(lines) + "\n", s)
    s = s.replace("Status: DRAFT — becomes BINDING",
                  "Status: BINDING (frozen 2026-08-27) — became binding")
    open(pp, "w", encoding="utf-8", newline="\n").write(s)
    print("FROZEN. Hashes written to anti_cheat/frozen_hashes.json")


if __name__ == "__main__":
    main()
