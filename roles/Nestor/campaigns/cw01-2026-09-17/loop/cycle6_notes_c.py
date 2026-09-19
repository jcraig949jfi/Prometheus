"""Cycle-6 reconciler notes, part C: P-H08 (heritability vs edit robustness) and P-H10 (grammar B)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-X17", "P-H08", "RECONCILER: NEUTRALITY_PRESERVES - heritability along walks is NOT edit robustness. Unfiltered random mutants lose the shape (keep-shape at 16 operations: ask-time .02, schedule .02, periodic .08, start-anchored .45) and lose reward (0-.02), while neutral walkers at the same depth keep the shape (ask-time 1.0, periodic 1.0, start-anchored .91, schedule .62) and reward (1.0). The shapes travel along neutral walks because the neutrality filter preserves the FUNCTION they are bound to; the start-anchored shape is the most edit-robust (.45 after 16 unfiltered operations) - consistent with its compact, fully-reached code (P-H09). The heritability claim of P-F02 is refined: shape is inherited with function, not with the genome as such.", True)
    L.append_evidence("T-ARCH5", "P-H10", "RECONCILER (grammar B importable; reactivation read): reading MIXED by rule (gaps at depth 16, B minus A keep-shape: start-anchored -.13, periodic 0, ask-time 0, schedule -.19). Substantively NEAR-INVARIANT: under grammar B's operator set the periodic and ask-time shapes are kept by 16/16 walkers at every depth, start-anchored by .81 (vs .94 under v0.4), schedule by .44 (vs .62). Every walk reaches depth 16 under both grammars. The schedule shape is the least stable under any neutral walk (it decays along both grammars); representation is not a coordinate for the other three.", True,
                      state="ACTIVE", state_reason="T-ARCH5 reactivated: representation B is usable on classified programs; continuation: evolution under grammar B in nonstationary worlds")
    L.append_evidence("T-X17", "P-H10", "cross: representation near-invariance of the geometries (grammar B vs v0.4 walks): periodic / ask-time invariant, start-anchored -.13, schedule -.19.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes C appended")


if __name__ == "__main__":
    main()
