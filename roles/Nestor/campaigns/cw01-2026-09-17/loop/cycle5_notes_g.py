"""Cycle-5 reconciler notes, part G: P-G02 (the ruler reread) and the T-X15 state change."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-ARCH4/M1", "P-G02", "RECONCILER - RULER AUDIT (qualified scattered ruler, f .05/.10/.20): (a) P-D01 'loss is a dose in units / length protects' -> DISAPPEARS (slope of loss on log length +.03 / +.01 / +.00, all inside +-.07). P-D01 'operand hits softer than deletions' -> SURVIVES (operand - delete -.19 at f .10, below p05, 124 pairs; old .36 vs .72). P-D01 'C4-08 tops ~.20 more robust' -> SHRINKS: tops .32 vs rest .41 (-.09, below p05; length-conditioned -.12, band +-.095), while P-G08's independent draw set found +.01 (inside band): the residual set effect is draw-sensitive and small - UNRESOLVED as a coordinate. (b) P-E05 'orig walks lose less with depth (-.10), no_growth more (+.10), rule effect +.27' -> ALL DISAPPEAR (orig .423 -> .419; no_growth .439 -> .442; rule +.02; every band +-.06). (c) P-F06 'selection lowers loss vs ancestors and vs the competent drift control in 6/6 seeds' -> SHRINKS: select .355 vs ndrift .436 vs ancestor .474; length-conditioned select coefficient -.071 (band +-.05; was -.144); the promotion rule holds in 0/6 seeds (select < ancestor in 2, select < ndrift in 2, never both). Length carries nothing (-.02, inside band). Conclusion: of the seven fixed-count claims, one survives (operand softness), two shrink to small and unpromotable effects (set, selection), four were ruler geometry.", True,
                      state="ACTIVE", state_reason="the damage surface is re-based on the scattered ruler: operand slot / category and reach remain; length, depth-growth and most of the selection effect were the ruler")
    L.append_evidence("T-X15", "P-G02", "RECONCILER: the coordinate that named this node - length as damage robustness, with carried state beneath it - is RULER-GENERATED (P-G08, P-G02) and carried state is entangled with function (P-G03). The node is retired as a coordinate and kept as the record of a false coordinate (specimen SPEC-R01-FALSE-COORDINATE).", True,
                      state="TEMPORAL_STASIS[coordinate=length-retired x state=entangled-with-function]", state_reason="escape: a subset-persistence or bounded-duration intervention that keeps reward inside its band for >= 30 programs, or a representation in which state and function separate")
    L.append_evidence("T-R01", "P-G02", "cross: changing the ruler changed four of seven conclusions - the ruler was a mechanism of the campaign's damage results.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes G appended")


if __name__ == "__main__":
    main()
