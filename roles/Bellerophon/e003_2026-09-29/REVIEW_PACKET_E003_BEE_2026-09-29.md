+==============================================================================+
| REVIEW PACKET -- E-003 BEE LEG: byte-level ancestry replay of BEE r022153     |
| Author: Bellerophon (M2 / SPECTREX5)            Date: 2026-09-29              |
| For: HITL operator + external reviewers                                       |
| Status: RESULT REPORTED (VALIDATED, both readings); merge review queued       |
| Self-contained: no repo access needed; every load-bearing number is inline.   |
+==============================================================================+

-----
0. SUMMARY
-----
Question (Archaeon's attribution arc, campaign C-001): when a BEE organism writes
a child, can each child byte be attributed to a donor byte by copy-descent, and
does a singular-donor record ("attribution v0") describe that without loss?
Owner of the BEE leg: Bellerophon. Spec: ANCESTRY_PREREG v4 + v5 through
amendment C11, written and amended by Archaeon, reviewed adversarially 7 times
before any production data.

Result on one run (r022153; 32,827 births): VALIDATED under both readings of
the one undefined case (B-P1). Value dependence outside {donor, performer} is
0.115% [0.098, 0.134] of loci in the transmission class; the ceiling for
VALIDATED is 5%. This is a finding about the INSTRUMENT and the representation,
not about heredity.

-----
1. WHAT WAS BUILT, AND FROZEN BEFORE MEASUREMENT
-----
- A shadow tracer: a label-carrying twin of the frozen VM (git 16fc6c2a). It
  was written from the spec TEXT only; the other two tracers were not read. It
  is value-checked against the frozen VM on every call.
- Fixtures 28/28. Tracer frozen at cfb57f67a (sha256 823cbef1) and never changed.
- A world replay with persisted per-byte origins (ORIG / NEW / MUT at the RNG
  draw); Q4 capability tests; interventional tests (R1 arms, C7.2 prefix flip,
  R5 completeness); an analysis whose verdict is computed in code; a v0
  round-trip.
- Manifest re-frozen twice, each time before production and each tied to a
  ruling: #951 (flip-coverage denominator, TIED class) and #956 (B-P1 dual
  reading). No tracer change.
- One disclosed post-dry change: NO_MATERIAL removed from the gates (R1 says
  reported, not gated). The dry numbers are not citable.

-----
2. INTEGRITY CHAIN
-----
- Preserved births reproduced bit-for-bit: 32,827 / 32,827.
- Tracer vs the world's own execution: 123,210 interactions, 0 mismatches.
- The B-P1 probe, observing the frozen tracer, was asserted on 2,878,487 loci.
- Three-way tracer agreement (owner / independent reference / Archaeon):
  * fresh set 1: owner = Archaeon, 1.0 on every field;
  * production sample: FAILED on an Archaeon-side reading of constant-only
    computations. C11 adopted the owner's literal reading; Archaeon repaired
    its own tracers AFTER seeing the owner's output. This is flagged;
  * fresh set 2, the independent test: 1.0 on every field in every class,
    32,000 loci, 0 discrepancies.
- The production start receipt passed; outputs were sealed before their
  location was posted; every committed blob was re-verified against the seal.

-----
3. RESULTS (production/E003_RESULTS.json)
-----
Gates, point estimate vs floor:
  flip coverage:      self 0.822, other 0.543 (MARGINAL: CI 0.44-0.65),
                      none 0.720 (floor 0.50)
  flip FAILED:        0 in every class (ceiling 1%)
  completeness leak:  0 in every class (ceiling 5%)
  identifiable births 0.968 (floor 0.80); transmission class 31,401 (>= 30)
  v0 round-trip       PASS, 32,827 records
Predictions:
  P1 positional homology 0.962 [0.960, 0.964] >= 0.90   HOLDS
  P5 Q8c upper bound < 5%                               HOLDS
  P2 (engine-native) the native "target" label disagrees with copy-descent
     in 0.504 [0.456, 0.552] of such births             HOLDS
Descriptives:
  Q4 isolated-capable children 0.810, host-assisted 0.817.
  17% of transmission-class children carry the writer's material but cannot
  copy in isolation.
  Existence dependence (Q8c-whether, birth suppression when randomising):
  writer 0.73; occupant 0.93 in occupant-performed births vs 0.016 in
  self-performed; input 0.002.
Reading dependence: only one birth's class changes (self -> none); no gate or
verdict changes.

-----
4. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES: on this run, births are L1 written and L2 causally donor-written, by
intervention, and a singular-donor v0 record plus the agreed extensions
describes them losslessly by the frozen tests. BEE's native "material" label is
not a descent label.
DOES NOT:
- say anything about inheritance or transmission (L3 later reproduction, L4
  persistence and L5 heredity are unmeasured);
- give Q5 (its drift null was not built);
- generalise beyond one run of one cell;
- test the persisted ORIGIN attributes with any agreement check (they were
  exported only);
- avoid the reading-A-only draw of the s4 sample and the Q4 host pool.

-----
5. INCIDENTS
-----
- Post-dry correction (NO_MATERIAL gating), disclosed before the freeze.
- Production s4.3 FAIL resolved by C11; Archaeon's side repaired post-exposure
  and flagged; the independent fresh set 2 passed.
- run.log was caught by a *.log ignore rule; force-added so the seal holds.
- An EMPTY-window mislabel in the replay, caught and fixed pre-freeze.

-----
6. DECISION / NEXT
-----
Merge the branch after the queued Fabric review (tsk-20587454511f,
tsk-5617cacdfcfe). Archaeon writes the cross-engine E-003 synthesis; the NPE leg
is INCONCLUSIVE by design (its corpus is below the R3 minimum). No new BEE work
is authorised by MWO-0002.

-----
7. QUESTIONS FOR THE REVIEWER (please try to disagree)
-----
1. VALIDATED rests on one run. Is the round-trip criterion strong enough, or does
   it only check that v0 can hold what the tracer emits?
2. Existence dependence on the occupant is 0.93 in occupant-performed births. Is
   excluding existence from Q8c (R2) hiding exactly the dependence that matters?
3. Archaeon repaired its tracers after seeing the owner's output. Does fresh
   set 2 fully restore independence?
4. Should the 17% "material without capability" figure change how "descent"
   is presented?

-----
8. ARTIFACTS
-----
Branch bellerophon/e003-bee-ancestry-2026-09-29 @ 1afd47c9f (report f9a93eb6d).
roles/Bellerophon/e003_2026-09-29/: E003_BEE_RESULT.md, production/,
FREEZE_MANIFEST.json, agreement/, receipts/, tools/, README.md.
Spec and gates: archaeon/attribution-arc-2026-09-28:ops/campaigns/C-001/
ATTRIBUTION_ARC_2026-09-28/ (ANCESTRY_PREREG_v4/v5, gate_close/).

+==============================================================================+
| END. "Not worth continuing" is a first-class answer.                          |
+==============================================================================+
