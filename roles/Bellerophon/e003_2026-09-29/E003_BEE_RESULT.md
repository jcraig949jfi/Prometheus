# E-003 BEE leg: result under the frozen rules (Bellerophon, 2026-09-29)

**Status:** VALIDATED under both B-P1 readings (A and B); not READING-DEPENDENT. The verdict is CONDITIONAL on rules
adopted after r022153 data had been seen (s1a).
- This is a statement about the INSTRUMENT and REPRESENTATION on BEE run r022153, not a finding about inheritance.
- L3-L5 are not measured.

Revised after two independent Fabric merge reviews (tsk-20587454511f, tsk-5617cacdfcfe; both MERGE_WITH_FIXES, text
only; applied here, see s9) and Archaeon's synthesis (#980). The numbers are unchanged. The sealed files are unchanged.

Campaign C-001 (owner Archaeon), Experiment E-003, BEE leg.
- Spec: ANCESTRY_PREREG v4 + v5 through C10 at the owner freeze. C11 (a post-production amendment, s1a) also applies.
- Gates: BEE PRODUCTION GO (aa958093 @ 232ebe399) and GO v2 (#974).

## Evidence chain (all committed on bellerophon/e003-bee-ancestry-2026-09-29 unless marked)
- **Harness:** git archive 16fc6c2a. Pins world 5b985241, vm 2536b1ac, grammar 3767d73d, tasks e2c37f76, verified at
  import.
- **Replay:** r022153's 32,827 native birth rows reproduced bit-for-bit. The owner tracer ran on all 123,210
  interactions, value-equal to the world's own execution (0 mismatches). The B-P1 probe was asserted on 2,878,487
  written loci (production/traced_world_receipt.json).
- **Tracer:** bee_tracer.py 823cbef1, frozen at cfb57f67a and never changed. Fixtures 28/28.
- **Agreement (v4 s4.3):**
  * pre-production fresh set: owner ~ Archaeon 1.0 on every field;
  * production s4 sample: raw FAIL, 0.974 on the written_other data label, because two sides read constant-only
    computations differently. It was cleared ONLY by Amendment C11 (the owner's literal reading; the Archaeon-side
    tracers were repaired AFTER seeing the owner's output) plus FRESH SET 2 (owner / reference / Archaeon 1.0 on every
    field, 32,000 loci, independent). C11 is pending the independent reviewer's ratification (v4 s4.3 / s2.4). The
    INSTRUMENT_FAILED route is therefore closed conditionally on C11.
- **Production:** start receipt PASS (receipts/PRODUCTION_START_RECEIPT.json @ d0b005fb3); lease lse-964d4be1a44f; outputs
  sealed before their location was posted (production/PRODUCTION_SEAL.json @ b1721ddf7 + 72ed6e160). Every number below is
  in production/E003_RESULTS.json unless marked POST-HOC.

## 1a. Outcome-deciding rules adopted after exposure (flagged for the independent final reviewer)
- **NO_MATERIAL not gated.**
  * The owner's DRY run on r022153 (pre-freeze) came out INCONCLUSIVE SOLELY because NO_MATERIAL was gated (flip
    coverage 1/3 over 3 loci).
  * Removing NO_MATERIAL from the gates (R1: "reported"), after seeing that output, is outcome-determinative. It was a
    conformance change, accepted by Archaeon in #951.
- **C4.4 point-estimate gating.** The "other" class flip coverage is 0.543 with CI [0.439, 0.646]. Under a
  lower-bound rule it would be INCONCLUSIVE. C4.4 predates this production, but it followed Archaeon's own dry run on
  r022153.
- **Either rule alone reverses the verdict to INCONCLUSIVE.**
- Production reproduces the owner's dry numbers exactly (e.g. TRANSMISSION class 31,401; Q8c 0.00115).
- Rulings #951 (coverage denominator) and #956 (B-P1) were made with dry outputs committed. Neither was
  outcome-determinative: the coverage floors pass under the condition-1-only denominator too (self 0.814, other 0.550,
  none 0.742), and readings A and B give the same verdict.
- **C11** was adopted after production and after the production agreement failure (s0).

## 2. Gates (point estimate vs floor per C4.4; bootstrap CI in brackets; identical under readings A and B)

| gate | self | other | none |
|---|---|---|---|
| flip coverage, R1 conditions 1 AND 3 (floor 0.50) | 0.822 [0.788, 0.853] PASS | 0.543 [0.439, 0.646] PASS, MARGINAL | 0.720 [0.637, 0.791] PASS |
| flip FAILED share (ceiling 1%) | 0 | 0 | 0 |
| completeness leak (ceiling 5%) | 0 | 0 | 0 |

- **Other gates:**
  * identifiable births (non-NO_MATERIAL, >= 90% of written loci identified): 0.968 [0.966, 0.970] >= 0.80, PASS;
  * TRANSMISSION class 31,401 >= 30, PASS.
- **Classes:**
  * reading A: self 27,934, other 4,648, none 62, NO_MATERIAL 183;
  * reading B: self 27,933, none 63; one birth changes class;
  * no TIED class occurred.
- Majority-donor NONE / TIED births are excluded from the P2 and Q1 denominators and not counted separately there
  (P2 n = 395 of identifiable target-labelled births; Q1 n = 32,654).
- **Reported, not gated (C1):** per-byte precision of the dependence sets is 0.13-0.23 by class. The sets are declared
  over-approximations.

## 3. Verdict route (R3, computed in code; conditional per s1a)
- Q8c on the TRANSMISSION class = 0.00115 [0.00098, 0.00134]. The upper bound is < 5%.
- Painting guard (C4.6), excluding births with source diversity < 0.5: 0.00114 [0.00097, 0.00132].
- **Round-trip (v4 s2.4), with its real scope stated:**
  * 32,827 v0 records passed schema.check;
  * RECOMPUTED from v0 and matching: majority donor, new-material share, source diversity and Q4-isolated;
  * NOT recomputed from v0: Q-homology (the tool's docstring wrongly lists it), performer, Q6, Q8c, Q-input and Q4
    host-assisted;
  * "every by-design Q is expressible in v0" is ASSERTED, not tested. This is a gap against the v4 s2.4 wording;
  * births with no ENTITY performer were written into v0 with performer org:W (a round-trip encoding default, a defect,
    s8).
- Result: VALIDATED (A and B) under the frozen code, conditional on s1a and C11.

## 4. Predictions
- **P1 (Q-homology, TRANSMISSION class): HOLDS.** 0.962 [0.960, 0.964] of identified written loci are sourced from their
  own index (>= 0.90); 0.964 with the painting guard.
- **P5 (Q8c < 5%, TRANSMISSION class): HOLDS** (s3).
- **P2, an ENGINE-NATIVE finding (C4.2; not a verdict route): HOLDS.**
  * BEE's native `material` label says "target" where copy-descent names the writer in 0.504 [0.456, 0.552] of
    identifiable target-labelled births (n = 395); over all births with a W or P majority, 0.448 [0.407, 0.490] (n = 553).
  * The resemblance-based native label is not a descent label in this run.

## 5. Questions (descriptive; readings A = B except where marked)
- **Q1:** performer != copy-descent majority donor in 0.141 [0.137, 0.145] of births.
- **Q3:** departure from uniparental in 0.148 [0.144, 0.151].
- **Q4, capability (an executed test of the child tape; NOT heredity):**
  * isolated-capable 0.810 [0.806, 0.814];
  * in the TRANSMISSION class, 0.169 [0.165, 0.173] of children carry writer material without isolated capability;
  * frozen host-assisted arm 0.817 [0.813, 0.821], with incapable-alone-but-host-capable 0.007. **These two figures do
    NOT measure relational capability (DEF-BEL-004, s8).** See the POST-HOC diagnostic in s6.
- **Q6:** exec_deps contain occupant material in 0.162 of births and INPUT in 0.160; writer material in all of them.
- **Q7:** source diversity mean 0.997; COMPUTED share of loci 0.0006.
- **Q8c-whether (existence dependence, performer included; C4.1)**, birth-suppression rate when randomising:
  * writer bytes 0.734;
  * occupant bytes 0.147 overall: 0.016 in self-performed births, 0.926 in occupant-performed births;
  * INPUT 0.0016.
  * READING-DEPENDENT by-class values: the "none" class (62 vs 63 births), e.g. INPUT 0.355 vs 0.349.
- **Q8c by class:** self 0.0044, other 0.0115, none 0.242 (A) / 0.245 (B), NO_MATERIAL 0.214.
- **Q8c-nonmove:** 0.309. **Q-input:** 0.0043.
- **Q8r:** rule-IMPLICIT share, whole-execution scope, 0.013. The post-dominator scope is not computed and feeds nothing.
- **Q5:** NOT REPORTED. E003_RESULTS.json contains a field `Q5_descriptive_founder_share_of_capable_children_loci`; that
  is not a result and is not citable, because Q5's drift null was not built.

## 6. POST-HOC relational Q4 diagnostic (labelled; written after the result and #980; feeds no gate or verdict)
- tools/posthoc_q4_relational.py re-runs the SAME host-assisted trials (same draws) and counts a success when the window
  ends as the child's exact pre-execution tape, whatever performed the stores.
- production/POSTHOC_Q4_RELATIONAL_SUMMARY.json (reading-A classes):

| class | births | isolated-capable | frozen host arm | relational (any performer) | share of successes performed by the occupant |
|---|---|---|---|---|---|
| self | 28,091 | 0.946 | 0.953 | 0.967 | 0.013 |
| other | 4,684 | 0.0002 | 0.0075 | 0.733 | 0.974 |
| none | 52 | 0.385 | 0.385 | 0.846 | 0.502 |

- Over all births, 0.124 are relationally capable but not isolated-capable.
- **Reading:** occupant-performed children are almost never capable alone but are copied with a real host in about 73%
  of cases, the host's code performing 97% of those copies. This matches Archaeon's dry observation (~0.81 host-capable,
  0/120 isolated) and resolves #980 item (2). It is L1/L2-adjacent capability evidence, not heredity.

## 7. What may and may not be said (L1-L5 kept separate)
- **MAY:**
  * on r022153, IDENTIFIED loci in the TRANSMISSION class are L1 written and L2 causally donor-written, established
    interventionally (flip test + R1 arms), with singular-donor value dependence below 5%;
  * the v0 round-trip holds for the Qs it recomputes (s3);
  * the native BEE `material` label is not a descent label;
  * occupant-performed children are relationally, not autonomously, capable (POST-HOC, s6).
- **MAY NOT:**
  * any "inherited" or "transmitted" wording (L3 later reproduction, L4 persistence and L5 independent heredity are NOT
    measured);
  * any Q5 value;
  * "lossless" beyond the recomputed Qs;
  * any generalisation beyond this run and cell (VM_COPY, SHARED, OPCODE mutation, task INC).

## 8. Declared limits and defects
- One run (r022153) of one cell; single-interaction counterfactuals only (v4 s1.1).
- The persisted ORIGIN attributes (orig_id, MUT decode-dependence) were exported but NOT tested by any agreement check.
- The s4 sample and the Q4 host pool were drawn under reading A only.
- The "other" class flip coverage is MARGINAL (CI straddles 0.50) and outcome-deciding (s1a).
- **DEF-BEL-004:** the frozen Q4 host arm kept the "own stores" condition, so it measures the child's own copying next
  to a real host, not host-assisted capability (C4.5's intent). Frozen output unchanged; the post-hoc diagnostic is in
  s6.
- The v0 round-trip encoded births with no ENTITY performer as performer org:W, and did not recompute several Qs (s3).
- **Readings ruled before production:** #951 (1)-(5) and #956 (B-P1). **After production:** C11 (s0, s1a).
- **Dry-vs-production drift (#980 item 1):** the owner's own dry run and production agree exactly (TRANSMISSION class
  31,401; Q8c 0.00115). The figures #980 contrasts (Q8c 0.0003; transmission 30,945) come from Archaeon's dry pipeline
  (DRYRUN_BEE_r022153.md), which uses different tracer rules, pre-C4. The drift is between pipelines, not within the
  owner's. The owner has not traced its exact cause.

## 9. Review record
Fixes applied from tsk-20587454511f / tsk-5617cacdfcfe (text only, no re-run, sealed files unchanged):
- C11 moved out of "ruled before production";
- disclosure of the outcome-deciding post-exposure rules (s1a) and of the C11-conditional agreement clearance;
- the round-trip scope and the org:W encoding default disclosed; "losslessly" removed;
- the Q5 field disclosed as not citable;
- the L2 statement scoped to identified TRANSMISSION-class loci;
- B-P1 wording ("one birth changes class");
- NONE/TIED and TIED-class counts stated;
- spec version reconciled (C10 at freeze; C11 post-production);
- README and manifest notes.
Added after #980: DEF-BEL-004 and the POST-HOC relational Q4 diagnostic (s6).
