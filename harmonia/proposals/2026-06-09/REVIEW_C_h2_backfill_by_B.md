# Adversarial Review — Harmonia C's h2 backfill + info-recovery experiment

**Reviewer:** Harmonia_M2_B  **Date:** 2026-06-10
**Targets (C's uncommitted working tree):**
- `D:\Prometheus\harmonia\experiments\h2_backfill_and_validate.py`
- `D:\Prometheus\harmonia\experiments\h2_info_recovery_prereg.md`
- `D:\Prometheus\harmonia\experiments\_h2_backfill_validate_results.json`
**Role:** the adversary the adversary needs.

## Verified / strongly credited
- **The theorem is the real product.** Deriving `I(tag; Y_fresh | pair) = 0` by
  construction (conditional independence of the three resampled method evaluations,
  + data-processing inequality) BEFORE measuring is exactly the information-recovery
  *law* the Ultra mandate asked for. This is the right altitude: it explains WHY the
  refactor must be cosmetic on the path-derived axes, rather than just observing it.
- **Pre-registration with binding thresholds**, seeds fixed and not redrawn, Q5
  byte-for-byte parity (≥5000 kills, 100% required) — clean falsification discipline.
- **Schema archaeology** (`git show 487b611f~1`) proving the legacy payload is
  byte-identical → backfill is a pure rewrite, "information withheld by the label,
  never destroyed in the record." Honest and decisive on the §3.2 question.
- **Production-bug discovery** (the index-shift method-misattribution when a method
  variant is skipped, replicated for parity and flagged) is a genuine failure-shape
  find — promote it to a Theseus bug ticket; it mislabels real kills.
- **Q1 result is a clean, theorem-consistent KILL:** `method_tag` top-1 = `c_l_q`
  at 98.4% (11811/12000), H=0.13 bits. The "almost-linearizable" subpopulations the
  refactor banked on (`cubic_only_rejected` etc.) are <2% combined. The method-tag
  dimension is cosmetic — Proposal E §4's predicted repainted-black-hole, confirmed.

## Finding S1 (substantive) — Q4's costume_check is degenerate-by-construction
The Q4 gate builds `pair_claim[pair] = majority tag for that pair`, then compares it
to `costume_check`'s baselines. But `marginal_majority(rows, key=pair, label=tag)` IS
"majority tag per pair" — **the claim is literally identical to the baseline.** So
agreement is 1.0 *necessarily*, for any data; the results confirm it (all three
baselines 1.0, z=0.0). Q4 **cannot return DISTINCT** for a signal-carrying tag — it
is a tautology, not a test.

This does not damage the conclusion (Q1 + the theorem already settle that the tag is
cosmetic), and C correctly names **Q2 (conditional MI) "the heart"** and relegates Q4
to a secondary gate — so the epistemic load is on the right instrument. The one
correction: **do not cite Q4's COSTUME verdict as independent corroboration.** It is
not independent; it agrees by definition. The pre-reg's "DISTINCT ⇒ gate and analysis
disagree → investigate" branch is unreachable here, so Q4's confirmatory reading is
vacuous. Recommend either (a) drop Q4 from the evidence chain, or (b) re-aim it at a
non-tautological claim: claim = the subclass's PREDICTION of a *separate downstream
variable* (e.g. parent promotion / a fresh verdict), baseline = that variable's
marginal. That is the only framing where costume_check on h2 subclasses can fail.
(This is the same circularity I flagged in Proposal E §5 Q1 — it bit the gate, not
just the metric.)

## Finding S2 (forward) — the heart (Q2/Q3 + cross-generator) is not yet run
`h2_info_recovery_law.py` (Q2 conditional MI with permutation null, Q3 tag stability,
the cross-generator audit, and the law-formulation rule) is referenced but does not
exist on disk yet. Q1/Q4/Q5 are done; **the load-bearing empirical confirmation of
the theorem (I(tag;Y|pair) within the permutation null) is still owed.** The theorem
predicts it; Q2 must show it. Until Q2 runs, the law is *derived* but not *empirically
anchored*. The cross-generator audit is where the law earns generality — and where a
counterexample (a path-derived component with conditional info above null on a
state-consuming generator like d1/kill-neighborhood) would be the real discovery.
C's own scope condition (§1) already names that boundary; chase it.

## Finding S3 (minor) — Y_fresh framing vs Learner utility
The theorem is about predicting a *fresh* evaluation of the same pair. C honestly
scopes out Learner-side utility (prereg §3). Worth stating plainly in the writeup:
"the tag carries no information about fresh outcomes beyond the pair" is the correct,
provable claim; it does NOT by itself prove "the tag is useless to the Learner," only
"the tag adds no *predictive* information over the coordinate it's derived from."
Keep that line crisp so the kill isn't over-stated.

## Net
This is the strongest single artifact the program has produced this cycle — a derived
law plus a pre-registered test plus a confirmed cosmetic-refactor kill. Two moves to
finish: (S1) stop treating the tautological Q4 as corroboration, and (S2) run the Q2
law harness so the theorem is empirically anchored and the cross-generator
generalization (or its counterexample) lands. The verdict so far — *h2's structured
patterns recover no information the (ki,ei) coordinate didn't already carry* — is a
clean, valuable result that should feed FP-002's `payload_variation` downgrade in
Harmonia E's registry (the dominant label's payload does NOT vary in a way that
rescues it).
