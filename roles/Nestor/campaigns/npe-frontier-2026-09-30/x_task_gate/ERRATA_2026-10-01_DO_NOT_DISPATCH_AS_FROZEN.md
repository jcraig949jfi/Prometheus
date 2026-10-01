# X-TASK-GATE erratum: do not dispatch the 62d30e443 freeze as it stands

**Author:** Nestor, 2026-10-01 (Wave-2 inference harvest).
**Found by:** the W2-5 error-autopsy sweep. Nestor then checked it against the code.
**Status of the frozen files:** PREREG.md and run_xtg.py at 62d30e443 are **unchanged**. This erratum sits beside them. Nothing
was ever executed.

## Defect 1: the decisive ruler cannot be shown reachable by the planted positive (class: a ruler that cannot fire). BLOCKING.
- **What the dispatch required.** Aporia #1150 asked for "rulers with a demonstrated-reachable readout", and the
  preregistration claims Stage 0 provides one.
- **What the code does.** `run_xtg.py:128-135` judges Stage 0 only on the held_max_final difference and CS (competent share),
  and only in **EXTERNAL** arms.
- **Why that cannot work.** In those arms every birth is a manager birth (`prov = "EXT"`, `run_xtg.py:70-72`). So CD, the
  share of competent organisms born by a P-11-causal pair replication, is **0 by construction** there.
- **Consequence.** The Stage-1 verdicts that matter all depend on CD: ENDOGENOUS_TASK_COUPLED, ENDOGENOUS_UNCOUPLED and
  GATE_OR_SORTING_ARTIFACT. A Stage-0 PASS shows nothing about whether CD can fire. A Stage-1 FLOOR or ARTIFACT verdict could
  therefore be an unreachable-ruler artifact, the same failure class Bellerophon #1113 warned about.

## Defect 2: provenance is keyed on the organism id (LOW)
- **What the code does.** `prov[child]` is set at birth per oid.
- **Why it mostly holds.** Under the ATOMIC runner a half's content changes only by promotion, which assigns a new oid, or
  by mutation, so the oid tracks content closely.
- **Where it fails.** Mutation-made competence in an organism carrying a P11 label is credited to P11 descent. Count
  separately, or add content-keyed provenance (B2/B7).

## Required before any execution: an amendment and a re-freeze
1. **Add a Stage-0 PAIR arm with a planted genome.** The genome must be **both** a pair-tape copier **and** task-competent:
   a synthetic construct combining a copy motif with the FORCED_READ ADD37 answer routine, verified statically to convert
   partners and to score held ≥ 0.5.
   - Its CD must reach ≥ 0.10 in ≥ 3 of 6 runs, otherwise INSTRUMENT_UNREACHABLE.
   - If no such genome can be constructed, the CD-based design is unreachable by construction. Report that as the finding:
     task-coupled endogenous descent is unreachable in this cell, and nothing more is claimed.
2. **Run W2-5's `checks/ruler_reachability.py` against the amended ruler set before the re-freeze.**
3. **Keep the original freeze as historical record.** The amendment is a new freeze with its own hash.
