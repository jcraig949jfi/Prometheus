# Loop Cycle 014 — 2026-08-21

## The correction: the loop was numbering against a SUPERSEDED table

Self-caught before building R9. Cycles 001-013 used the rung numbers from
`pivot/reasoning_ladder_v01_2026-05-24.md`, which carries an explicit SUPERSEDED banner. The
canonical semantics are `aporia/doctrine/reasoning_ladder.md` §3 and differ from R2 up:
loop-R2/R3 are swapped, loop-R4/R8 are swapped, loop-R6 is canon R7, loop-R8 is canon R4.

My rung notes cite Canon v2.0 while using v0.1 numbers — a citation that does not match its
content, and a violation of canon §8's vocabulary law. **This is the fossil pattern the loop
has spent four cycles writing doctrine about, committed by the loop itself, in the same week.**
Full crosswalk (no silent renames): `rung_notes/RUNG_LABEL_CORRECTION.md`.

Three things the correction revealed:
- **Two canon rungs were never built**, and one is the most Prometheus-relevant of all:
  R5 invariant detection, and **R6 counterexample/falsification — canon's own words: "the
  battery's own discipline, miniaturized."**
- **Two loop builds are off-ladder axes, not rungs** (counterfactual/relational execution;
  plan revision). Better filed as state-topology axes, which is what the claims ledger
  already treats them as.
- **Canon R4 is flagged in the canon as "Grader missing — the canon's first build-debt."**
  Retagged, cycle 013's representation-shift work is a contribution against a named debt.
- The claims ledger's v1→v9 arc is unaffected: it was never about rung numbers.

## Canon R6 built — and the finding is sharper than planned

`canon_r6_falsification.py` + 9 tests. Circuits: BoundedSearcher (witness-carrying,
abstains past its horizon), EagerFalsifier (declares falsity on suspicion), CredulousAsserter
(never falsifies). Canon's named probe reproduced: n²+n+41 boundary found at exactly n=40.

**Measured, and it corrected my own hypothesis mid-cycle.** I expected the eager falsifier to
score perfect recall and be caught only by its phantom rate. Under WITNESS-REQUIRED scoring
its recall collapses to **zero** — it never produces the counterexample its claims assert.
So there are **two independent defences**, either sufficient:

1. **Mixed battery + phantom-rate scoring** (the canon's instruction), and
2. **the artifact requirement itself** — demand the counterexample, and the killer-of-
   everything is exposed with no true conjectures in the battery at all.

**6th instance of the competitor-relative law, and the first about SCORING rather than probe
composition:** under verdict-only scoring on an all-false battery, the eager falsifier and the
honest searcher are observationally identical (recall 1.0, phantom rate vacuously 0.0). Two
tests show either repair separates them.

## Track 1 — signature_index temporal stability (HITL #9 unanswered, so the fallback ran)

Insertion-order epochs (rowid = the honest clock; wall-clock untrustworthy per R14), 3 epochs
of ~1,103 rows. Occupied (generator, kind) cells vary — 22 / 12 / 37 — so generators come and
go. But: **zero of 56 generators ever emit a second claim_kind, in any epoch.**

That sharpens the June monoculture reading considerably. It is not that generators drifted
into a narrow band over time; each generator was born with exactly one claim_kind and never
broadened, across the ledger's entire history. Per-epoch TT ranks [9,4] / [4,3] / [7,4].
