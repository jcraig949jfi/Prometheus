"""Cycle-7 reconciler notes, part B: P-I02 (what evolved - the plateau named), P-I03 (prefix dissection), P-H06 (reach / slot promotion), P-I08 (census of context-evolved tops)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-X21", "P-I02", "RECONCILER - THE PLATEAU NAMED (36 organisms, behaviour first): every top in A and C answers IDENTITY (answer == v on 100 percent of asks; stimulus dependence 0); B tops answer identity 46 percent and 'other' 50 percent - the cue word changes their answer in 94 percent of asks (cue causality .94) but toward the correct other-regime answer only 58 percent: the cue is ingested as data and perturbs the output without a correct conditional. In world A the regime word is READ INTO A REGISTER (a register whose value predicts the regime with accuracy 1.0 in every top, e.g. values {0, 1}) and NEVER USED: overwriting that register with its other-regime value changes 0 percent of answers. World C: adaptation flat (.47-.56 by trials since switch), anticipation at chance (.50), recovery after state clearing flat (.50), transfer .50 everywhere. The exploited invariant is IDENTITY; the obstruction is a ZERO-GRADIENT PLATEAU: from identity, every single mutation scores <= .5 (the conditional complement needs read + branch + NOT + AND assembled at once) while the information (r in a register) is already present. This is the loophole record: information without a fitness path to its use.", True,
                      state="ACTIVE", state_reason="successor world specified: a regime transform reachable in ONE instruction from identity (v XOR r), so that the ingested register has a fitness path; ceilings computed and preregistered as P-J01 (cycle 8)")
    L.append_evidence("T-X17", "P-I03", "RECONCILER: the prefix is NOT a control interface. Host insertions of a donor prefix transfer competence in 0 percent of 640 cells at every k (geometry <= .42 even at k 8); a JMP into the host at 0 or mid changes nothing (0 percent). ASK-TIME donors are compact (~9 instructions): the first 8 instructions alone keep the geometry (1.0) and 75 percent of reward, k <= 4 keeps geometry (.75-1.0) without reward; RELOCATING the first k <= 4 instructions to the end destroys the geometry (0) - the ask-time shape is SEQUENCE CONTENT RUN FROM ITS ENTRY; a jump over one NOP into the intact donor keeps everything (1.0). START-ANCHORED donors (~20 instructions): no truncation up to 8 keeps geometry (0) or reward (0) - whole-program; relocation of the first k <= 4 keeps geometry .5-.75 and reward .5-.75 - content-position-tolerant. Reading UNRESOLVED by the rule (no family >= .2 competence except truncation k8 .15 / jump_entry k1 .2): the causal object is the donor's own program executed from its own entry (ask-time) or the donor as a whole (start-anchored); neither transplants into a foreign body. Prefix dominance in splices (P-H02) is explained: the prefix donor's program runs first and the suffix rarely executes.", True,
                      state="ACTIVE", state_reason="the prefix line closes: geometry = the program that runs, from its entry; no separable interface")
    L.append_evidence("T-X19", "P-I03", "cross: start-anchored is whole-program (no truncation <= 8 keeps it) and tolerant to moving its first 1-4 instructions to the end (.5-.75).", True)
    L.append_evidence("T-ARCH4/M1", "P-H06", "RECONCILER: damage loss lives in REACHED code: scattered deletion restricted to reached instructions loses .40 vs .05 for unreached (Wilson bands disjoint; 122 / 93 programs). Within reached rows the slot ordering holds (a .48 > b .14 > c .05). FLOOR-CONDITIONED PROMOTION: on programs whose held-out baseline is above the floor (W1_d1: 59 programs; W2_K2d1: 91) the ordering a < c on held-out reward deltas holds in every stratum on both families -> the operand-slot ordering is PROMOTED as a grammar-level mechanism: the register-field operand is the fragile slot in every lineage, on held-out families, within reached code.", True)
    L.append_evidence("T-R01", "P-H06", "cross: reachability is the first coordinate of damage (reached .40 vs unreached .05); any damage ruler should report hits by reach.", True)
    L.append_evidence("T-ARCH4/W1", "P-I08", "RECONCILER: context-evolved tops are inside the known manifold (NEW 0/208): world A tops are immune 25 / ask-time 20 / start-anchored 3; world B tops are IMMUNE 48/48 (and B-destroyed tops ask-time 32/32: the cue's presence selects idle-tick immunity - the cue tick is an extra tick before the PUT); world C tops ask-time 48/48. No crossing, so no shape coincides with crossing.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes B appended")


if __name__ == "__main__":
    main()
