# E-003 BEE leg: result under the frozen rules (Bellerophon, 2026-09-29)

**Status: VALIDATED under both B-P1 readings (A and B); not READING-DEPENDENT.**
- This is a statement about the INSTRUMENT and REPRESENTATION on BEE run r022153. On this run, attribution v0 plus the
  agreed extensions describes births without the losses the frozen rules test for.
- It is not a finding about inheritance. L3-L5 are not measured here.

Campaign C-001 (owner Archaeon), Experiment E-003, BEE leg. Spec: ANCESTRY_PREREG v4 + v5 through C11
(archaeon/attribution-arc-2026-09-28). Gates: BEE PRODUCTION GO (aa958093 @ 232ebe399) and GO v2 (#974).

## Evidence chain (all committed on bellerophon/e003-bee-ancestry-2026-09-29 unless marked)
- **Harness:** git archive 16fc6c2a. Pins world 5b985241, vm 2536b1ac, grammar 3767d73d, tasks e2c37f76, verified at
  import.
- **Replay:** r022153's 32,827 native birth rows reproduced bit-for-bit. The owner tracer ran on all 123,210
  interactions, value-equal to the world's own execution (0 mismatches). The B-P1 probe was asserted on 2,878,487
  written loci (production/traced_world_receipt.json).
- **Tracer:** bee_tracer.py 823cbef1, frozen at cfb57f67a and never changed. Fixtures 28/28.
- **Agreement (v4 s4.3):**
  * pre-production fresh set: owner ~ Archaeon 1.0 on every field;
  * production s4 sample: FAILED on an Archaeon-side reading of constant-only computations. Amendment C11 adopted the
    owner's literal reading; the owner's outputs are unchanged; the post-C11 re-run PASSES (post-exposure, supporting);
  * FRESH SET 2: owner / reference / Archaeon agree 1.0 on every field in every class (32,000 loci), 0 discrepancies
    (independent). Seals: agreement/OWNER_SEAL.json, OWNER2_SEAL.json.
- **Production:** start receipt PASS (receipts/PRODUCTION_START_RECEIPT.json @ d0b005fb3); lease lse-964d4be1a44f;
  outputs sealed before their location was posted (production/PRODUCTION_SEAL.json @ b1721ddf7 + 72ed6e160).
  Every number below is in production/E003_RESULTS.json.

## Gates (point estimate vs floor per C4.4; bootstrap CI in brackets; identical under readings A and B)

| gate | self | other | none |
|---|---|---|---|
| flip coverage, R1 conditions 1 AND 3 (floor 0.50) | 0.822 [0.788, 0.853] PASS | 0.543 [0.439, 0.646] PASS, MARGINAL mark | 0.720 [0.637, 0.791] PASS |
| flip FAILED share (ceiling 1%) | 0 | 0 | 0 |
| completeness leak (ceiling 5%) | 0 | 0 | 0 |

- **Other gates:**
  * identifiable births (non-NO_MATERIAL, >= 90% of written loci identified): 0.968 [0.966, 0.970] >= 0.80, PASS;
  * TRANSMISSION class: 31,401 births >= 30, PASS;
  * v0 round-trip: 32,827 records, 0 check failures, 0 mismatches, PASS.
- **Reported, not gated (C1):** per-byte precision of the dependence sets is 0.13-0.23 by class. The sets are declared
  over-approximations.
- **Class counts:**
  * reading A: self 27,934, other 4,648, none 62, NO_MATERIAL 183;
  * reading B: self 27,933, none 63. A single birth carries the B-P1 loci; every gate and verdict is unchanged.

## Verdict route (R3, computed in code)
- Q8c on the TRANSMISSION class = 0.00115 [0.00098, 0.00134]. The upper bound is < 5%, so the singular-donor record does
  not misstate value dependence.
- Painting guard (C4.6), excluding births with source diversity < 0.5: 0.00114 [0.00097, 0.00132].
- Every by-design Q is expressible in v0 plus the extensions, and the round-trip passes. Result: VALIDATED (A and B).

## Predictions
- **P1 (Q-homology, TRANSMISSION class): HOLDS.** 0.962 [0.960, 0.964] of identified written loci are sourced from their
  own index (>= 0.90); 0.964 with the painting guard. No positional-homology field is required for this cell.
- **P5 (Q8c < 5%, TRANSMISSION class): HOLDS** (see the verdict route).
- **P2, an ENGINE-NATIVE finding (C4.2; not a verdict route): HOLDS.**
  * BEE's native `material` label says "target" where copy-descent names the writer in 0.504 [0.456, 0.552] of
    identifiable target-labelled births (n = 395); over all births with a W or P majority, 0.448 [0.407, 0.490]
    (n = 553).
  * The resemblance-based native label is not a descent label in this run.

## Questions (descriptive; readings A = B except where marked)
- **Q1:** performer != copy-descent majority donor in 0.141 [0.137, 0.145] of births.
- **Q3:** departure from uniparental (second donor >= 10%, new material >= 10%, or performer != donor) in 0.148
  [0.144, 0.151].
- **Q4, capability (an executed test of the child tape; NOT heredity):**
  * isolated-capable children 0.810 [0.806, 0.814];
  * host-assisted capable 0.817 [0.813, 0.821];
  * incapable in isolation but capable with a real host 0.007 [0.006, 0.008];
  * in the TRANSMISSION class, 0.169 [0.165, 0.173] of children carry the writer's material without isolated capability.
- **Q6:** exec_deps contain occupant material in 0.162 of births and INPUT in 0.160; writer material in all of them.
- **Q7:** source diversity mean 0.997; COMPUTED share of loci 0.0006.
- **Q8c-whether (existence dependence, performer included; C4.1)**, birth-suppression rate when randomising each group:
  * writer bytes 0.734;
  * occupant bytes 0.147 overall: 0.016 in self-performed births, 0.926 in occupant-performed ("other") births;
  * INPUT 0.0016.
  * READING-DEPENDENT by-class values (A vs B): the "none" class (62 vs 63 births), e.g. INPUT 0.355 vs 0.349.
- **Q8c by class:** self 0.0044, other 0.0115, none 0.242 (62 births), NO_MATERIAL 0.214 (A). "none" under B: 0.245.
- **Q8c-nonmove** (CONST / COMPUTED loci): 0.309. **Q-input:** 0.0043.
- **Q8r:** rule-IMPLICIT share, whole-execution scope, 0.013. The post-dominator scope is not computed; it feeds nothing.
- **Q5:** NOT REPORTED. Its drift-only null was not built, and Q5 is not reported without it.

## What may and may not be said (L1-L5 kept separate)
- **MAY:**
  * on r022153, births are L1 written and L2 causally donor-written, established interventionally (flip test + R1 arms),
    with singular-donor value dependence below 5% in the TRANSMISSION class;
  * v0 represents them losslessly by the frozen round-trip;
  * the native BEE `material` label is not a descent label;
  * about 17% of TRANSMISSION-class children carry writer material but fail the isolated capability test.
- **MAY NOT:**
  * any "inherited" or "transmitted" wording. L3 (the child later reproduces), L4 (persistence) and L5 (independent
    heredity / recert) are NOT measured by E-003;
  * any Q5 value;
  * any generalisation beyond this run and cell (VM_COPY, SHARED, OPCODE mutation, task INC).

## Declared limits
- One run (r022153) of one cell.
- Single-interaction counterfactuals only (v4 s1.1).
- The exchange tested per-interaction labels. The persisted ORIGIN attributes (orig_id, MUT decode-dependence) were
  exported but NOT tested by any agreement check.
- The s4 sample and the Q4 host pool were drawn under reading A only.
- The "other" class flip coverage carries a MARGINAL mark (its CI straddles 0.50).
- Readings made and ruled before production: #951 (1)-(5), #956 (B-P1), C11 (constant-only COMPUTED).
- The owner's dry pipeline run before the freeze is disclosed and not citable (README).
