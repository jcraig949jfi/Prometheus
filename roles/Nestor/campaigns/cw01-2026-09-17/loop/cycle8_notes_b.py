"""Cycle-8 reconciler notes, part B: P-J03 (scaffold stripping) and P-J06 (gateway structure); companion
amendments for P-J04 / P-J05 (mandated by the directive, outside the frozen ten by the per-parent cap)."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402

PERT = HERE / "PERTURBATIONS.jsonl"


def main():
    L.append_evidence("T-X17", "P-J03", "RECONCILER (WITNESS-SEEDED, flagged): the scaffold ladder. Stage 0 (A', xor 1): 8 seeded witnesses fix by generation 5 in both seeds (top-4 held 1.0). Stage 1 (xor 3, 60 generations): NOT crossed - .69 / .56 vs the plateau lineage's .56 (the .69 is the XOR-1 relic: v XOR 1 equals v XOR 3 on half the regime-1 asks). Stage 2 (xor 15): NOT crossed (.58 / .56; plateau .50 / .56; fresh .42 / .50). The scaffold does NOT open xor 3 or xor 15: both need a LITERAL CONSTANT (an LDC whose 32-bit word equals 3 or 15: 2^-32 per uniform word draw, or a walk of ~16 specific single-bit flips under operand perturbation) and the one-edit census of the witness finds 0 hits toward xor 3 / 5 / 15. REMOVAL (xor 0, identity suffices): the xor-1 machinery, still partly present after the xor-15 stage (top-4 on xor 1 .80 / 1.0, 0-33 percent of the population at >= .9), is GONE after 60 generations without its world (top-4 on xor 1 .52 / .48): the acquired machinery decays at the mutation rate when unselected. Reuse (xor 5): nobody crosses. Gateway rule not met on the ladder. (The preregistered removal retest used the xor-15 sets; the addendum measured the right transform, post hoc, labelled.)", True,
                      state="ACTIVE", state_reason="the gateway exists for constant-free neighbours (P-J06) and closes for constant-bearing ones; continuation: a grammar or world in which constants are reachable by steps")
    L.append_evidence("T-X17", "P-J06", "RECONCILER (WITNESS-SEEDED scaffold, flagged): GATEWAY STRUCTURE, partial. The novel transform ADD 1 (regime 1 expects v + 1 mod 16; never used in the lineage's evolution) is CROSSED by the scaffolded lineage in seed 1 (top-4 held .984) and by neither the plateau-ladder lineage (.55 / .53) nor a fresh population (.55 / .53); seed 2's scaffolded lineage sits at .70 (the XOR-1 relic) and does not cross. The crossing is at GENERATION 0 of the add-1 stage: the scaffolded population already CONTAINED an add-1-competent individual, produced by neutral drift on the scaffold during the ladder (ADD is one opcode word from XOR at the witness's transform instruction; the one-edit census of the witness finds exactly 1 hit toward add 1, the XOR -> ADD replacement, and 0 toward xor 3 / 5 / 15). XOR 5 (needs a literal constant) is crossed by nobody. REUSE by intervention: the crossed tops read all three ask-tick words before answering (unread at OUT 0 vs 3 on the plateau) and hold the regime word literally in register 0 at the answering OUT - the witness's routing, reused; no control instruction is necessary (branch-free). READING: acquired machinery changes what is reachable next - its neutral neighbourhood contains the constant-free neighbouring transforms, which appear as standing variation before selection asks for them; transforms that need a literal constant stay unreachable within 60 generations because a specific 32-bit word is 2^-32 per draw or ~16 specific bit flips away, with no fitness signal along the walk. NOT PROMOTED as an evolutionary gateway: the scaffold was seeded, 1 of 2 seeds crossed, and the crossing pre-existed the stage; PROMOTION CANDIDATE 'standing-variation gateway of an acquired routing' pending a natural crossing or a replicated seeded ladder with >= 4 seeds.", True)
    L.append_evidence("T-X21", "P-J06", "cross: after a scaffold, the constant-free neighbour add 1 is reachable (standing variation), the constant-bearing xor 5 is not; the reused routing = read all three words then transform the answer with the regime register.", True)
    L.append_evidence("T-R01", "P-J03", "cross: the accessibility coordinate the ladder exposes is LITERAL CONSTANTS: a transform whose witness needs an LDC of a specific word is ~16 unrewarded single-bit flips (or one 2^-32 draw) away; register-to-register transforms are one edit apart.", True)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l).get("id") for l in PERT.read_text(encoding="utf-8").splitlines() if l.strip() and json.loads(l).get("executed_in")}
    with PERT.open("a", encoding="utf-8") as fh:
        for pid in ("P-J04", "P-J05"):
            if pid not in existing:
                fh.write(json.dumps({"id": pid, "amend": True, "executed_in": "CYCLE8_2026-09-19", "companion": "mandated by the cycle-8 directive as P-J01's forensics / genealogy; outside the frozen ten by the per-parent cap (T-X21: P-J01, P-J07)", "result": "experiments/cw01-arch4/%s/RESULT.json" % pid, "recorded": ts}, ensure_ascii=True) + "\n")
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl", PERT):
        RS.require_ascii_safe(f)
    print("notes B appended")


if __name__ == "__main__":
    main()
