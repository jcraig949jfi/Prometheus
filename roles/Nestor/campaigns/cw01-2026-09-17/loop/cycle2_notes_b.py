"""Cycle-2 reconciler notes, part B (P-D11, P-D13, P-D01) + defect D076. Run after all drivers exit."""
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

LEDGER = HERE.parent / "DEFECTS.jsonl"
D076 = {"id": "CW01-D076", "experiment_id": "cw01-loop2", "phase": "EXECUTE", "severity": "medium", "category": "control", "status": "OPEN",
        "defect_class": "A - sham not draw-matched",
        "title": "P-D13: the sham arm consumed draws from the SHARED evolution rng, so SHAM != STATIC (final TREE .885 vs .75)",
        "evidence": "damage_pop() calls r.choice() on the evolution rng in both DAMAGE and SHAM arms; STATIC makes no such draws, so the downstream random stream diverges and the sham is not a control for STATIC (e06's own rule: draws must be unconditional and identical across arms). DAMAGE vs SHAM remains a valid draw-matched comparison; STATIC is reported as a third arm only.",
        "proposed_fix": "In a descendant, draw the damage picks from a SEPARATE rng keyed on (attempt, generation) in every arm, or make STATIC consume identical draws. Not re-run inside this cycle.",
        "found_by": "P-D13 sham_identical_to_static check"}


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    if D076["id"] not in existing:
        rec = {"id": D076["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
        rec.update({k: v for k, v in D076.items() if k != "id"})
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(LEDGER)
    L.append_evidence("T-E06", "P-D11", "RECONCILER: 80-generation mixed runs seeded 50/50 COEXIST in 2/4 (t3 r.5, TREE .53/.58), 1/4 (t2 r.5), 2/4 (t3 r1.0), 3/4 (t2 r1.0). e06 never ran mixed 80-generation runs after adding resource sharing (its gate refused on rare invasion), so 'coexistence unreachable' was a statement about invasion from 10%, not about coexistence from parity. Coexistence without mutual invasibility - a protected or slow-fixing regime - is now on record; continuation: 240 generations, seeded-frequency sweep.", True,
                      state="ACTIVE", state_reason="a new regime (parity coexistence) is reachable; the question e06 asked can be posed from parity")
    L.append_evidence("T-X01", "P-D11", "RECONCILER: tournament 2 x recombination 1.0 gives the most coexisting runs (3/4) and TREE .73; tournament 2 alone lowers TREE (.54) and coexistence (1/4). The two axes do not simply add.", True)
    L.append_evidence("T-E06", "P-D13", "RECONCILER (D076: sham not draw-matched to STATIC; read DAMAGE vs SHAM): blind deletion of 10% of body units per generation tilts the ecology toward TAPE (final TREE .43 vs .885 under sham; growth -.006 vs +.044) and raises coexistence (2/4 vs 1/4); TREE bodies shrink (8.5 vs 13-16 units). Subtree contraction hurts trees more than instruction loss hurts tapes: representation-blind damage is not substrate-neutral in effect.", True,
                      state="ACTIVE", state_reason="damage is a new axis for the ecology; continuation: dose f, damage one substrate, draw-matched sham")
    L.append_evidence("T-E07", "P-D13", "cross: e07's damage family in e06's ecology changes which representation wins (see T-E06)", True)
    p = HERE.parent / "experiments" / "cw01-arch4" / "P-D01" / "RESULT.json"
    if p.exists():
        r = json.loads(p.read_text(encoding="utf-8"))
        coef, mg = r["regression_loss"], r["marginals"]
        L.append_evidence("T-ARCH4/M1", "P-D01", "RECONCILER: locality DOSE SURFACE (%d rows, %d cells, 126 programs, held-out W2_K2d1): loss per doubling of units lost k %+.3f vs per doubling of sites s %+.3f - the law is mostly a dose in units, with a small locality term (k=8 spread over 1 site .66 vs 8 sites .77, +.05 outside the paired band; k 2->8 at one site .43->.66, +.40). Kind: operand damage .36 vs delete/opcode/move .72-.75 (operands are the soft coordinate). Decode trap (%+.3f) and placement (%+.3f) inert. Genotype set: parents and 16-step walkers lose ~.20 more than C4-08 selected tops (selection built robustness to structural loss). Continuation manifold: instruction-role map of the operand softness; pairwise site epistasis at fixed k; other held-out families; C4-08 tops vs their own ancestors."
                          % (r["n_rows"], r["cells"], coef["log2_k"], coef["log2_s"], coef["decode=nop"], coef["place=random"]), bool(r["material"]),
                          detail={"regression": coef, "marginals": mg, "contrasts": r["contrasts"]},
                          state="ACTIVE", state_reason="a surface exists; continuation: instruction role, pairwise epistasis, other held-out families")
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes B appended")


if __name__ == "__main__":
    main()
