"""S3-2. One immutable, hash-covered object holding every load-bearing threshold.

THE DEFECT THIS REPAIRS. `CROSS` and `MARGIN` were defined twice, once in adjudicate.py
and once in bundles.py, with a comment promising that "if they ever diverge the campaign
gate says so". No gate said so. The world's crossing threshold (`CROSS_THRESH`, which
decides `crossed_ever` and `crossed_at_final` - the very fields the adjudicator reads) and
the replication-evidence gates were a third and fourth copy, written as bare literals.
Four copies of one number drift independently and nothing notices, which matters most
after a long unattended run whose verdicts cannot be regenerated cheaply.

THE SHAPE. Every module that makes a verdict-bearing comparison reads `C[...]` from here
and defines no threshold of its own. `C` is a read-only mapping, and `CONSTANTS_SHA256`
covers its canonical JSON. `tests/test_s3_repairs.py` asserts:
  * the hash of the live object equals `PINNED_SHA256` below (a changed value is caught);
  * no campaign module assigns any of these names at module level (a re-declared local
    copy is caught - that was the drift path);
  * the modules that used to hold copies read the SAME object as this one.

Changing a value is allowed only by editing this file, re-pinning, and saying so in the
amendment log of PREREGISTRATION.md. After freeze the pin is part of the protocol hash.
"""
from __future__ import annotations

import hashlib
import json
from types import MappingProxyType

C = MappingProxyType({
    # ---- competence (world, adjudicate, bundles) ----
    "CROSS": 0.90,                    # held-out competence that counts as crossing
    "MARGIN": 0.25,                   # minimum separation from the matched control
    "CAUSAL_DEPTH": 5,                # H2 self-sustaining bar, on causal replication depth
    # ---- private-slot replication evidence (world._on_birth) ----
    "REPL_FIDELITY": 0.90,            # child fidelity to parent
    "REPL_WROTE_SHARE": 0.50,         # parent placed at least this share of the child
    # ---- pair-tape phenotype, retained from the predecessor (world._pair_epoch) ----
    "PAIR_FID_OTHER_MIN": 0.90,       # final victim fidelity to donor
    "PAIR_FID_SELF_MAX": 0.90,        # victim must have changed: fidelity to itself below
    "PAIR_DONOR_WROTE_SHARE": 0.25,   # predecessor write-count gate (kept as a prefilter)
    # ---- P-11 randomized-victim causal assay (p11.py) ----
    "P11_FINAL_FIDELITY": 0.90,       # criterion 2: rebuilt victim reaches this
    "P11_AUTHORSHIP": 0.90,           # criterion 4: donor authored this share of changes
    "P11_CONTROL_MAX": 0.90,          # criterion 5: donor-disabled control stays BELOW
    "P11_DRAWS": 3,                   # independent randomized victims per event
    "P11_MAJORITY": 2,                # draws that must pass
    # ---- H2 decision rule (operator ruling 2026-09-24) ----
    "H2_SEEDS": 16,                   # shared seeds per specimen
    "H2_B_MIN": 8,                    # arm B reaching depth >= CAUSAL_DEPTH in >= 8 of 16
    "H2_C_MAX": 2,                    # arm C reaching it in <= 2 of 16
    "H2_PANEL_MIN_SPECIMENS": 2,      # supporting specimens from DIFFERENT strata
    # ---- H3 decision rule (rev B, unchanged) ----
    "H3_SEPARATION": 0.20,            # certificate rate A exceeds B and C by at least this
    "H3_MIN_CERTIFICATES": 5,         # fewer in arm A: not demonstrated
})


def canonical(obj=C):
    return json.dumps(dict(obj), sort_keys=True, separators=(",", ":"))


CONSTANTS_SHA256 = hashlib.sha256(canonical().encode("ascii")).hexdigest()

# Pinned at S3 (2026-09-23); re-pinned 2026-09-24 when the H2/H3 rules were added. A test compares the live hash to this; they must agree.
PINNED_SHA256 = "b1c8a904d092dd61eff970f581424635c591475f8d441351d6a01caf89cccffb"

NAMES = tuple(C)
# Module-level names that used to hold private copies; none may be re-declared.
LEGACY_NAMES = ("CROSS", "MARGIN", "CAUSAL_DEPTH", "CROSS_THRESH")
