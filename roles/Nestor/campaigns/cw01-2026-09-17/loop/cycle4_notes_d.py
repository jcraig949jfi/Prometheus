"""Cycle-4 reconciler notes, part D: P-F03 (T-X17 evolution under idle ticks + transplant) and P-F10 (T-X16 in Proteus)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-X17", "P-F03", "RECONCILER: the temporal class is BUILT BY SELECTION and is LINEAGE-, not WORLD-specific. (1) W0 plain selection (40 gens, from the walkers) yields ask-time-bound tops (W0D1.before_ask .68, K2.before_first_ask .65, between_puts .1); W0 selection under idle ticks yields fully IMMUNE tops (all seven components 0.00) at the same reward (.80 vs .80-.84): 40 generations suffice to remove timing sensitivity when the world punishes it. (2) W2_K2 selection in THIS evolver yields immune tops in both modes (all <= .07) - the 'input-schedule-bound' class of cycle 3 belongs to the C4-08 lineage (100 gens, N 200), not to the W2 world: the class does not reproduce from a different lineage under the same world. (3) TRANSPLANT: W0-idle (immune) tops moved to plain W2 stay immune (32/32, 31/32) - not discriminating since W2's own products are immune; W2-idle (immune) tops moved to plain W0 for 20 generations stay near immunity in one seed (24/32; centroid .23) and move halfway to W0's ask-time-bound class in the other (15/32; centroid .50, MIXED): the host world under selection RECONSTRUCTS the class within 20 generations at a seed-dependent rate. Reading: the class travels with the organism only as long as selection does not act against it; it is a selectable, lineage-borne, world-reconstructible phenotype.", True,
                      state="ACTIVE", state_reason="continuation: transplant without selection (neutral walk in the host world) to separate 'travels' from 'not yet re-selected'; the C4-08 lineage's schedule-bound class under idle-tick selection")
    L.append_evidence("T-X12", "P-F03", "cross: selection under idle ticks removes the input-less-tick sensitivity entirely in 40 generations at no reward cost - the substrate property of P-E01 is not a constraint of the VM but of what selection on plain episodes leaves unpenalised.", True)
    L.append_evidence("T-X16", "P-F10", "RECONCILER (sham == select verified): reading REVERSED - price-mediated pruning does NOT transplant into Proteus. At lambda 0 weather costs no reward (0.000), lowers damage loss of the tops (-.066, below p05; P-E09's seed pair gave -.024 inside band - a weak, seed-dependent protection at 60 generations) and shortens programs (-3.6). At lambda 1/128 the price alone collapses length from 44 to 5-6 instructions at unchanged top reward (.53 -> .53: the length was junk) and weather now LENGTHENS programs (+5.7, above p95) and raises persistent words (+57, above p95) while still lowering loss (-.17); at lambda 1/32 the priced population is at 5 instructions and weather is lethal (reward .18 -> .02, below p05; loss 1.0). Under a price on length, damage is a cost that grows with the price: the e06 sign (damaged substrate subsidised) does not appear. T-X16 is an e06 economics phenomenon, or depends on which structure the price hits (units that carry cost but not function).", True,
                      state="ACTIVE", state_reason="P-F04 (price 0 in e06) decides whether the e06 effect itself is price-mediated; the Proteus transplant is negative")
    L.append_evidence("T-X15", "P-F10", "cross: a length price of 1/128 removes ~39 of 44 instructions with no top-reward loss - the accumulated length is junk with respect to function, and its removal raises fixed-k damage loss from .33 to .91: the 'robustness' of long programs is dilution of the fixed-count window, as P-F01 read.", True)
    L.append_evidence("T-X13", "P-F10", "cross: weather in Proteus at lambda 0 (new seed pair) lowers top loss -.066 (below p05) with persistent words -50 (inside band): a weak protection signal without more state; under a length price weather raises state (+57, +91) - the state response to weather is price-dependent.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes D appended")


if __name__ == "__main__":
    main()
