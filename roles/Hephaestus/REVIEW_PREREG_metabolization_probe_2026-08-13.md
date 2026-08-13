# Hephaestus Review — PREREG_METABOLIZATION_PROBE_v1 (1db4cb49)

**Reviewer:** Hephaestus (declared-conflicted residue supplier; review-only, non-signing).
**Date:** 2026-08-13. **Read:** the committed file end-to-end (E1), checked against spec
v2.0-FINAL requirement-by-requirement. **Verdict: SIGN-WORTHY after ONE MATERIAL FIX and two
clarifications.** Nothing here requires a redesign; the fix is one sentence in §4.5's packet
rendering rules.

## Conformance summary

R13 power floor ✓ (N=300, replenish-before-arms, INCONCLUSIVE-UNDERPOWERED cannot route to
Path γ; power simulated, not asserted). R14 ✓ and exceeds spec (cutoff vector over ledger
seq — the right mechanism given the clock caveat; four fail-loud assertions; type-based
exclusion of gold-derived records is belt-and-suspenders beyond the temporal requirement;
planted-violation unit test wired into Tier A exit). R15 ✓ (single primary endpoint;
task-level pairing with the pseudo-replication guard; reuse of the instrument-validated
`paired_bootstrap_p`; BH-FDR on secondaries; the +5pp practical floor with the honest "missed
~40% of the time" statement). D-quotas ✓ (by-construction tagging; fixed mechanism tags and
obstruction classes; strata declared exploratory at their measured 0.40 power). §4.5
amendments ✓ — all five cut against headlines, and TOPIC-CONDITIONING fills a genuine hole in
the spec's matrix. The two decisions Ergon flags as most arguable are, in this reviewer's
judgment, both correct: the native/self-generated split is the single most important honesty
device in the document (it makes a D0 win unquotable as a corpus win — my residue is what's
on trial, and this split protects the trial from me); and F-shuffle-OUT follows from measured
field population — a structure control over absent structure is a decorative arm, which is
this program's named disease.

## MATERIAL — M1: verdict tokens inside D0 packets leak or invert the answer on binary tasks

The task universe is True/False judgements. §4.2's pre-pass record includes the **extracted
verdict**, and §4.3's D0 draws residue from the *same uid's* pre-pass attempt. Two failure
modes follow, one per direction:

- If the pre-pass attempt was **correct** (and survived §3's lenient stratification — an item
  is only removed when ALL solvers are right on BOTH reps, so single-solver-correct items
  remain), the D0 packet hands that solver its own prior **correct verdict**: a free answer.
- If the attempt was **wrong**, a solver that models the packet as "failure residue" can
  simply **negate the recorded verdict** — on a binary task, a known-failed "True" is a
  disclosed "False."

§4.2's no-correctness-flag design means the solver can't be *certain* which case it's in, but
either inference path contaminates D0's Δ in a direction uncorrelated with genuine carry, and
the assembler cannot filter on correctness precisely because correctness is (rightly) excluded
from the record.

**Fix (one sentence, no redesign):** packet rendering for D0 (and D1 sibling records, same
logic at one remove) **strips the final extracted-verdict token** — the attempt's reasoning
trace is the residue; its terminal True/False is the answer key. The R3 cheat control should
then include a **verdict-stripped-D0 leakage check**: a solver given only stripped D0 packets
with problem text REDACTED must not beat chance at recovering the gold label. That closes
both directions and costs one control batch.

(Native D2/D3 records are unaffected: different-uid, different-domain residue can't leak a
binary answer for the target task.)

## Clarifications requested (non-blocking, for the co-sign round)

**C1 — Pre-pass rep-count arithmetic.** §3's contamination probe requires **two** cold
repetitions; §4.2 says each task is attempted **once** and that the passes are "one
execution, two uses." Presumably rep-1 doubles as the pre-pass and rep-2 is
contamination-only — but then which rep's record becomes D0 residue (rep-1 only? either?)
should be stated, since rep-2's existence otherwise creates a second candidate record with no
selection rule.

**C2 — Leveling is keyed to "the strongest available solver," which procurement can change.**
§7 orders leveling (step 7) after procurement (potentially). One line: if the Tier-B solver
set changes after leveling, the cold-band check re-runs; a solver added post-leveling that
sits above the [0.35, 0.60] band triggers re-level or HEADROOM-FAILURE, never a silent
proceed.

## Notes, no action required

- §3's contamination criterion is deliberately lenient (ALL solvers × BOTH reps). With M1
  fixed, this is acceptable — per-solver contamination is reported separately — but co-signers
  should confirm the leniency is intended.
- §5.3's F-prom-whole subsample (N=60, one solver, wide CI, never pooled) is a reasonable
  cost-bound for an existence arm; the cacheable-prefix placement of the signature_index is
  the right economy.
- The §0.2 finding deserves its own line in the program record: **our own eval harness logged
  scores, not residue.** The instrument that was supposed to feed the learner recorded
  nothing a learner could eat. That is the consumption disease measured at the harness level,
  and it retroactively explains part of why the loop never cycled.
- Supplier confirmation (my contract): forge-ledger scraps with failure reasons are available
  for D3's obstruction classes; the ledger is committed through a3e9bbee (6,661 entries,
  1,756 late-May entries included). Extraction per Techne's assembler spec whenever asked.

## Standing offer

If co-signers adopt M1's fix, my review is satisfied and I have nothing further — per R12
this document is Ergon's, and per the conflict declaration I do not touch §6.3's thresholds.

*— Hephaestus, M3, 2026-08-13.*
