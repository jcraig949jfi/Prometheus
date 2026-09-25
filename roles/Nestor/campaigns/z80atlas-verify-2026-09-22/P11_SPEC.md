# P-11 -- PAIR_EXECUTION copy causality (prospective specification)

Status: **SPECIFIED AND TESTED BEFORE ANY OF THE 1,031 PREDECESSOR CASES WERE INSPECTED.**
Governing text: operator directive 2026-09-23, section S2
(`roles/Nestor/prompts/2026-09-23_s1_s4_execution/DIRECTIVE_VERBATIM.md`). Where this
file and that one differ, the directive wins and this file is wrong.

Implementation: `p11.py`. Thresholds: `constants.py` (`C`, pinned sha256
`ade1f755eaff9598e32eb9c768bd57b7094b4e0c7de555b0ebf2eb34b0b019ce`).
Tests: `tests/test_p11.py`, receipt `T_P11_RECEIPT.json`.

## 1. What P-11 replaces and what it keeps

The predecessor credited a pair-tape replication when, after one interaction:

- final victim fidelity to the donor's pre-interaction genome >= 0.90;
- victim fidelity to its own prior bytes < 0.90;
- the donor context's `writes_other` >= n/4.

**Kept unchanged:** the phenotype threshold (0.90, per the directive), the self-change
clause, and the write-count clause as a prefilter. P-11 is therefore strictly stronger
than the predecessor: every P-11 event is a predecessor event.

**Added:** a matched randomized-victim assay. The write count does not say whether the
writes carried the donor's bytes. Three fixtures in `tests/test_p11.py` are accepted by
the predecessor with no causal copy: writes to tape padding, writes that the victim later
overwrites, and a genuine 30-byte partial copy on top of 66 bytes of existing similarity.

## 2. The assay

The candidate interaction is **re-executed** from its exact pre-interaction state: both
genomes, both register files and flags, the execution order (a then b), the slice budget,
the world-op mask and the copy-mutation rate. It runs on a private tape with a private
RNG, so the world's own trajectory is unchanged. For each of `P11_DRAWS` = 3 draws:

| # | criterion | rule |
|---|---|---|
| 1 | randomize | victim half (n bytes) := uniform random bytes; record initial donor fidelity |
| 2 | rebuild | final victim fidelity to donor >= `P11_FINAL_FIDELITY` (0.90) |
| 3 | directed set | D = positions where initial victim byte != donor byte and final == donor byte |
| 4 | authorship | >= `P11_AUTHORSHIP` (0.90) of D authored by the donor during the interaction; empty D fails |
| 5 | matched control | same draw, donor's writes outside its own half blocked (z8 OWN policy), same victim bytes, same copy RNG: final fidelity < `P11_CONTROL_MAX` (0.90) |

A draw passes iff 2, 4 and 5 all hold. **An event is P-11 causal iff it passes the
predecessor criterion and at least `P11_MAJORITY` = 2 of the 3 draws pass.**

## 3. Choices this specification makes, stated before any data were seen

These choices are mine, not the directive's. Each is fixed here and must not be changed
after the 1,031 are examined.

1. **Authorship is recorded as the last value change, not the last write.** z8 keeps two
   arrays per tape position. `prov` holds the context that last **changed** the byte's
   value, and C4 reads it. `prov_lit` holds the context that last wrote the byte at all,
   and is reported beside every verdict. Why: a genuine block copier copies itself into
   the victim, and the victim, now running copied code, re-copies those same bytes onto
   itself. Under last-write-at-all the victim becomes the "author" of bytes the donor
   placed, and a genuine replicator fails. The test `block copier: victim re-copies
   itself` shows prov share 1.00 against prov_lit share 0.00. **This is a reading of
   "last-written by the donor" and is flagged for operator review.** Both numbers are
   reported for the 1,031, so either reading can be applied afterwards.
2. **Three draws, majority two.** One random victim is a one-draw bar. The randomized
   victim's own code runs during the interaction and can damage the donor by chance, so
   a single draw would reject genuine copiers at a rate set by that accident.
3. **Victim registers are kept.** Only the victim's bytes are randomized. Its register
   file and flags stay as observed, so the intervention changes one thing.
4. **Measured before world mutation.** The assay reads the tape immediately after the
   interaction. It tests the interaction, not the post-interaction mutation operator.
   The phenotype clause on the observed event keeps the predecessor's post-mutation
   reading, unchanged.
5. **Donor fidelity is measured against the donor's pre-interaction genome**, exactly as
   in the predecessor.
6. **Seeds.** Victim bytes and copy RNG for draw k are derived from a sha256 of
   (run seed, epoch, pair index, victim side, k), so a replay regenerates them exactly.
7. **Scope.** Only events that pass the predecessor criterion are assayed. Because P-11
   requires the predecessor criterion, events outside it cannot become P-11 events.

## 4. Known limit of criterion 5

C5 is nearly implied by C2 and C4. If the donor rebuilt at least 90% of a random victim
and authored at least 90% of those changes, then blocking its writes leaves the victim
mostly random. C5 can fire only when the randomized victim could rebuild the donor by
itself. The test proves it **can** fire by injecting a victim that pulls the donor into
itself; P-11 then fails, and the mutant without C5 passes. With truly random victims C5
is expected to be almost never decisive. It is kept because the directive requires it,
and this limit is recorded so no one reads a C5 pass rate as evidence.

## 5. Causal replication depth

`max_causal_replication_depth` for pair-tape runs is computed over lineage edges that are
**P-11 causal**. The predecessor-criterion depth is kept beside it under the name
`max_predecessor_replication_depth`. Neither replaces the other in reporting.

## 6. What P-11 does not do

It does not rewrite the frozen predecessor result. The frozen record says **1,031
admissible under the predecessor criterion**, and that stays true. The P-11 reassay is a
new forensic assay, reported as **N surviving the stricter causal reassay**, beside the
predecessor number and never in its place.
