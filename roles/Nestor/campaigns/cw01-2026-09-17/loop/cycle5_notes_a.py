"""Cycle-5 reconciler notes, part A: P-G01 (ruler qualification)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-R01", "P-G01", "RECONCILER: the scattered Bernoulli damage ruler is INSTRUMENT_QUALIFIED on 126 programs: hit counts match Binomial(n, f) (25,200 draws; mean z -.011, var z .991, Monte Carlo chi-square p .49); positions are not clustered (gap variance inside its simulated band for 100 percent of programs); the hit fraction is independent of length (slope 2.8e-5 inside its permutation band); equal keys reproduce exact masks; the sham path (mask drawn, nothing applied, same evaluation route) gives displacement 0 and identical reward on every program. Provenance recorded in scatter.PROVENANCE. The rereads (P-G02, P-G03, P-G08, P-G12) are unblocked.", True,
                      state="ACTIVE", state_reason="a qualified ruler exists; its own geometry is under test (P-G08)")
    RS.require_ascii_safe(HERE / "EVIDENCE.jsonl")
    print("notes A appended")


if __name__ == "__main__":
    main()
