"""Cycle-4 reconciler notes, part C: P-E04 (surface coordinates)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-ARCH4/M1", "P-E04", "RECONCILER: the operand softness of P-D01 (.36 vs .72-.75) decomposes into an OPERAND-SLOT coordinate: a hit on the register field (slot a) loses .36, on slot b .11, on slot c .05 (Wilson bands disjoint; 1888 rows each) - a seven-fold range inside one 'kind'. Opcode CATEGORY of the hit instruction is a second coordinate: comparison .24 and control .22 vs halt_yield .035 and arithmetic .13 (bands disjoint from the grand mean .17). PAIRWISE SITES ARE ADDITIVE: epistasis -.007 (band +-.01) over 708 pairs and per program - two damaged sites combine as independent hits, so the surface has no site-interaction term at k=4. HELD-OUT families: exaptation <= .017 on every family; damage transfers loss, not gain. The dynamic-reach axis was dropped (no per-instruction trace in the frozen VM).", True,
                      state="ACTIVE", state_reason="the surface acquired two coordinates (slot, category) and lost one (site interaction); continuation: slot x category interaction, reach via a HALT probe")
    L.append_evidence("T-X15", "P-E04", "cross: sites are additive at k=4 - a 'topology' term (interaction between damaged sites) is absent from the damage surface; length effects cannot be site epistasis.", True)
    RS.require_ascii_safe(HERE / "EVIDENCE.jsonl")
    RS.require_ascii_safe(HERE / "STATE.jsonl")
    print("notes C appended")


if __name__ == "__main__":
    main()
