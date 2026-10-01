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

## Addendum: defects found by the W2-8 executable-semantics audit (`inference_saturation_wave2/W2-8_semantics_audit/`)

These come on top of Defect 1. Each is reproduced in `demos/`. Patches are in `patches/` (world_patch P1, xtg_patch readout),
with tests in `tests/test_w2_8.py`.

- **D1, cross-niche competence cache (INVALIDATES).**
  - `world.py:576-584` keys `val_cache` on genome bytes only.
  - ffa6 is COEVO_ENV with 4 niches. For seed 31,000,000 the niche tasks are XOR5A FR, XOR5A FR, ADD1 ABR and XOR1 FR.
  - An organism's `held` and `probe` can therefore be its genome's score on another niche's task. Demonstrated: recorded 1.0 vs true 0.25.
- **D6, reader filter uses the base cue index for every niche (INVALIDATES).** A perfect ANSWER_BEFORE_READ-niche reader (held 1.0, probe 2.0) fails `probe ≥ 3`.
- **D15, regime-blind reader counted as competent (INVALIDATES the CS/CD reading).** A program that echoes v^key scores held 0.738 with probe 3, and counts as competent in 200/200 draws.
- **D7.** The post-run `_validate(force=True)` is 100% cache hits, and the "not stale" comment is false.
- **D9.** A relabelled organism keeps the destroyed genome's competence, which then feeds the gate.
- **D13.** INIT ≠ "sorting survivors" under ATOMIC: INIT organisms mutate in place.
- **D14.** The Stage-0 positive control runs on the private-slot path only. This is the same as Defect 1, confirmed independently.

**Required before any re-freeze (in addition to the above):**
1. Fix the cache with P1.
2. Use the `xtg_patch` readout: own niche task, VALLEY scoring, own cue index, no cache.
3. Pin the environment to STATIC, or report per niche.
4. Rename INIT.
5. Add a pair-path planted positive for CD.

W2-10 (static) is testing whether a genome that is both a copier and task-competent can be constructed at all.

## Addendum 2: W2-10 static construction study (`inference_saturation_wave2/W2-10_copier_task_genome/`)
- **Reachability:** a genome that is both copier and task-competent EXISTS. CT_UA:
  - COMPETENT 1.0;
  - state-free R1/R2;
  - FORCED_READ ADD37 held 0.997, with the reader check passing every time;
  - 89/120 P-11 conversions;
  - children 6/6 and grandchildren 22/24 still both copier and competent.
- **Further ruler defects in this cell:**
  1. Under COEVO_ENV the niche tasks come from {XOR1, ADD1, XOR15, XOR5A}. **ADD37 is never scored after epoch 25.**
  2. The NEUTRAL_BRIDGE floor lets a cue-reading-but-ignoring program (CT_U) pass "competent and reader" in 400/400 draws.
  3. Pairing, cache and cue-index issues, as in Addendum 1.
- **Amendment requirements (consolidated):**
  - STATIC environment, or niche-aware scoring with each niche's own cue index;
  - (genome, task)-keyed cache;
  - a competence bar above the bridge floor, or a cue-flip use test;
  - planted positive: CT_UA on the pair path;
  - negative controls: CT_U (reads, does not use) and COPY_ONLY (`2E001E40E5`, random padding);
  - `ruler_reachability` checked on the amended CD before the re-freeze.
