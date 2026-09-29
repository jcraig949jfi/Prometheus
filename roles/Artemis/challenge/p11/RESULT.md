# RESULT -- P-11 certifies construction, not heredity; CVT-2 is the weakest adequate heredity certificate

Executed 2026-09-28 (ubu002, 2 worker processes) under PREREG_P11.md (committed d5241a102 before execution) and two
amendments written before the runs they affect: AMENDMENT_2026-09-28.md (implementation details left open) and
AMENDMENT_2026-09-28b.md (two gate-code errors and one toy-ISA specimen defect, found by the first panel run, which is
kept unaltered as results/*_prerepair.*). Foreign NPE code ran only from git-archive copies (d7641744d, aa5833488) in
the scratch directory; SHA-256 of every copy is in results/GATES_PANEL.json and NATURAL_SUMMARY.json. No test suites,
no commits, nothing under roles/Nestor/ touched. Machine verdicts: results/VERDICT.json (verdict.py applies s5 of the
prereg mechanically). Cost: constructed panel 60 s wall (x3 for E0/E1), natural 9.5 s wall; far under 1 CPU-hour.

## 1. Gates
| gate | outcome |
|---|---|
| E0 VM equivalence | PASS. Forensic-substrate z8 vs verify z8 @d7641744d: full records (P-11, FERT, every CVT descendant digest) identical on all 8 z8 specimens. aa5833488 z8 (provenance off): identical tapes on all 8. |
| E1 determinism | PASS. Full constructed-panel records recomputed: identical for all 17. |
| E2 timing | PASS. Z1 pilot 0.47 s; no fallback needed. |
| G design facts | Pre-repair run: Z2 failed "child sterile" and (under the corrected exhaustive check) TV-1/TV-2 failed; causes and the single repair are in AMENDMENT b. Repaired run: ALL 17 PASS, none excluded. Notable measured facts: Z1 child = 0x36 x 96; Z2 child = (36 23) x 48, fid 89/96; Z3u96 copies a 72-byte prefix (fid 0.75); Z3n = z8.asm of NPE's source (hex matched), BIRTH in 3 slices, 0 blocked writes, REPL rule passes. |

## 2. Confusion table (repaired panel; A = accept, R = reject; x = wrong against ground truth)

| specimen | truth | P-11 (P0; pass rate) | FERT | LOCAL | CVT-1 (TB1) | CVT-2 (TB2) | CVT-R (TBR) | SHUF diag | DOM diag |
|---|---|---|---|---|---|---|---|---|---|
| Z1 z8 homopolymer painter | no, 0 | A x (P0; 1.00) | R | R | A x (2.00) | R (0) | R (0) | R | R |
| TV-1 closed homopolymer painter | no, 0 | A x (P0; 1.00) | A x | R | R (0) | R (0) | R (0) | R | R |
| Z2 z8 periodic painter | no, 0 | A x (P0; 0.90) | R | R | A x (2.81) | R (0) | R (0) | A x | A x |
| TV-2 closed periodic painter | no, 0 | A x (P0; 1.00) | A x | R | R (0) | R (0) | R (0) | A x | A x |
| Z3 block copier | yes | A (1.00) | A | A | A (6.29) | A (6.25) | A (6.25) | A | A |
| Z3b bytewise copier | yes | A (1.00) | A | A | A (6.07) | A (5.95) | A (5.95) | A | A |
| Z3u96 budget-limited bytewise copier | yes | R x (P0 fails; C2 0.00) | R x | A | A (7.59) | A (7.55) | A (7.55) | A | A |
| Z3n NPE seeded replicator (host) | yes | n/a (outside scope) | A (REPL gen 1+2) | A | A (7.34) | A (7.32) | A (7.32) | A | A |
| TV-3 toy copier | yes | A (1.00) | A | A | A (12.85) | A (12.85) | A (12.85) | A | A |
| TV-4 complement cycle | yes | R x (C2 0.00) | R x | A | A (12.85) | A (12.85) | A (12.85) | R x | A |
| Z5a host-mediated guest | yes | R x (P0: guest wrote 0) | R x | A | A (6.60) | A (6.60) | A (6.60) | A | A |
| TV-5b two cooperating tapes | yes | R x (C2 0.00) | R x | A | A (13.95) | A (13.95) | A (13.95) | R x | A |
| TV-6 two-state painter | yes, 1 bit | A (1.00) | A | R x | A (1.00) | A (1.00) | A (1.00) | R x | R x |
| TV-6k sixteen-state painter | yes, 4 bits | A (1.00) | A | R x | A (4.00) | A (4.00) | A (4.00) | R x | R x |
| Z6h low-entropy genuine copier (0x00 91.7%) | yes | A (0.75) | A | A | A (8.08) | A (8.06) | A (8.06) | A | R x |
| TV-7 STRESS hash scrambler | no (no resemblance) | R | R | R | A x (12.95) | A x (12.95) | R (0) | R | A x |
| TV-8 STRESS counter copier | yes | A (1.00) | A | A | A (12.85) | A (12.85) | A (12.80) | A | A |

TB = log2(1 + distinct transmitted difference classes); for copiers a lower bound set by the perturbation set (m = 3
per site for z8, exhaustive 255 per site for toys). Heritable fractions h2: Z3 0.78, Z3b 0.64, Z6h 0.92, TV-3 0.91;
painters 0. Every cell of this table equals the PREREG s3 prediction.

## 3. D1 -- is P-11 sound as a heredity certificate?
**UNSOUND FOR HEREDITY.** P-11 certifies all four zero-bit painters (Z1, Z2, TV-1, TV-2; assay pass rates 0.90-1.00)
and all six hereditary specimens inside its model (Z3, Z3b, TV-3, TV-6, TV-6k, Z6h). It gives the same verdict to
self-painting and copying. **OVER-STRICT flag: SET.** It rejects four genuine hereditary systems: TV-4 (complement
child, C2 = 0), Z5a (host executes guest; the guest writes nothing, so P0 fails), TV-5b (two cooperating tapes, C2 = 0)
and Z3u96 (a bytewise copier that cannot finish in one slice, C2 = 0).

## 4. A0 -- the one-slice budget prediction
**SUPPORTED.** Same cell and tier (Z8_SHARED n = 96, slice 360): the 3-step painter Z1 passes C2 in 20/20 assays; the
5-step bytewise copier Z3u96 passes C2 in 0/20 (it copies 72 of 96 bytes, fid 0.75) although CVT shows it is a
genuine replicator (TB2 7.55, re-copies in generation 2). In the 96-byte pair-tape cells P-11's C2 is reachable by
painting and unreachable by bytewise copying.

## 5. D2 -- weakest adequate certificate
**Selected: CVT-2** (counterfactual variant transmission with re-transmission: a single-byte parental difference must
produce a consistent offspring difference in generation 1 AND a consistent difference in generation 2).
- Adequate: CVT-2 and CVT-R. Both accept all 11 required hereditary specimens, reject all 4 painters, and calibrate
  exactly (TB: TV-6 = 1, TV-6k = 4, TV-1 = TV-2 = 0).
- Not adequate: CVT-1 (accepts Z1 and Z2: a sterile painter's operand "transmits" its colour once), FERT (accepts the
  closed painters TV-1/TV-2; rejects Z3u96, TV-4, Z5a, TV-5b), LOCAL (rejects the painter-family positive controls
  TV-6/TV-6k). SHUF and DOM were diagnostics only; for the record each misclassifies 4-6 specimens (SHUF accepts the
  periodic painters and rejects TV-4/TV-5b/TV-6; DOM accepts Z2/TV-2 and rejects the genuine copier Z6h).
- Acceptance-set sizes over the whole panel plus recertified natural donors: CVT-2 15, CVT-R 14, so CVT-2 is weakest.
- Stress (fixed wording, s5.3): "CVT2 is the weakest adequate certificate for the required panel; CVT-R is required if
  information-preserving but non-resembling reproduction (TV-7) must count as non-hereditary." CVT-R accepts the
  counter copier TV-8, so it is not over-strict on counters.
- Sensitivity (AMENDMENT b B3), pre-repair shared toy ISA: one substitution at site 0 turns a painter into a PERIOD or
  HASH reproducer, so the analytic truth there is TV-1 1 bit, TV-2 0, TV-6 log2 3 = 1.585, TV-6k log2 17 = 4.087.
  CVT-R reproduces all four exactly; CVT-2 and CVT-1 over-count (they also count the non-resembling HASH lineages).
  So on a richer ISA the ranking tightens toward CVT-R; on the preregistered panel CVT-2 is the weakest adequate.

## 6. The 57 natural P-11 survivors (NEW forensic assay: results/NATURAL_REAPPLY.jsonl, NATURAL_SUMMARY.json)
Nothing in S1-C is rescored: "1,031 admissible" and "57 surviving P-11" remain true of those instruments. This is a
fresh-state re-assay (the original events' registers and victims are not committed), following X-DONOR-RATE.
- Parameter cross-check vs world.Runner: 57/57 OK.
- Fresh-state P-11 (K = 50 per side): 6 of 57 recertify (rate >= 0.5); 10 more pass sometimes (0.02-0.42); 41 never.
  Like X-DONOR-RATE (12 of 16 donors at 0.0), P-11 competence is mostly state-dependent.
- Recertified: 1 BYTEWISE, 5 BLOCK. Selected certificate CVT-2:
  - 4 near-homopolymers (BYTEWISE 12ad3d5f 0x36; BLOCK dab251eb 0x36, 69fe5ba8 0x2a, c144e174 0x21): TB2 = 0 for all
    4 (prediction held 4/4). Mechanism audit: each writes ONE value into every victim cell it touches (0x36 x 96 writes
    on 32 cells; 0x2a on 63 cells; 0x21 on 64 cells). These are painters. Note that 3 of the 4 are in BLOCK cells: the
    painting route is not confined to the BYTEWISE arm.
  - 2 BLOCK copiers with ED B0/B8 and low dominance: 7ae3f9c1 (the C-RUNAWAY specimen, depth 2 in S1-C) TB2 7.39, and
    e1411055 TB2 7.36; both FERT-positive, writing 47-54 distinct values. Prediction held (2/2).
  - The other depth-2 run (c2a87e59) does not recertify fresh (rate 0.02).
- D3: N1 (BYTEWISE arm = construction without heredity) INCONCLUSIVE (1 BYTEWISE donor recertified, < 5). N2 (P-11
  heredity exists in the BLOCK arm) HOLDS (7ae3, e141). N3: 4 of 6 recertified P-11 donors carry zero transmitted bits,
  share 0.67 (exact 95% CI 0.22-0.96).

## 7. Other findings (not decision-bearing)
- Execution-order sensitivity: Z3 and Z3b, which are side-agnostic by construction, FAIL P-11 and carry TB2 = 0 when
  placed at side 1. The victim at side 0 runs first, its pc runs on into the donor's half, and it executes the donor's
  own copier with the victim's context, which overwrites the donor with random bytes before the donor ever runs. On
  the pair tape, whichever half sits second can have its copier hijacked by the first.
- Composition rules are misleading both ways here: Z6h is a genuine copier at 91.7% 0x00, inside the natural
  painters' 91-96% band, while Z2 is a painter at 48% dominance.

## 8. For Nestor
P-11 does what its specification says: it tests whether the donor's own writes rebuild a randomized partner half. It
never perturbs the donor, though, so it cannot tell a copier from a program that writes a fixed pattern matching
itself. On a preregistered panel it certified four zero-heredity painters exactly as readily as it certified block and
bytewise copiers (pass rates 0.90-1.00). Among the 57 S1-C survivors, the 6 that still pass P-11 from a fresh state
split into 4 single-value painters (0x36, 0x2a, 0x21; three of them in BLOCK cells) and 2 genuine copiers, one of them
your 7ae3 runaway founder. P-11 also rejects real hereditary systems that do not produce a byte-identical child in one
slice: complement children, host-executed guests, cooperating tapes, and, in the 96-byte cells, any bytewise copier,
because a one-slice budget admits painting at 3 steps per byte but not copying at 5 or more. None of this invalidates
P-11 as a construction-causality assay. The proposal is a companion certificate, CVT-2: perturb single parental bytes
(x^0x01, x^0x80, one random value per site), run two generations against common random victims, and count
consistent, re-transmitted offspring differences. It needs no new VM hooks, runs in seconds per donor, and every
specimen here, with its gate facts, can serve as a test fixture (roles/Artemis/challenge/p11/specimens.py). If your
own lineages ever show non-resembling transmission (hash-like re-encoding), use CVT-R, which adds a period-at-most-2
recurrence check. Two operational notes: P-11 competence is mostly state-dependent (41 of 57 donors never pass from a
fresh state), and a copier at side 1 can be hijacked by its partner executing its code first.

## 9. Files
Scripts (this directory): fetch_foreign.sh, common.py, tv.py, specimens.py, harness.py, certs.py, run_panel.py,
run_natural.py, verdict.py. Results (results/): PANEL.jsonl, CONFUSION.json, GATES_PANEL.json, NATURAL_REAPPLY.jsonl,
NATURAL_SUMMARY.json, VERDICT.json; pre-repair run kept as PANEL_prerepair.jsonl, CONFUSION_prerepair.json,
GATES_PANEL_prerepair.json. PREREG s6.4 named the human summary RESULT_P11.md; the coordinator asked for RESULT.md,
which is this file.

## Artemis reading (added after the result)

- ROBUST: P-11 is unsound for heredity. The certified painters include
  Z1 and Z2, built in NPE's own z8 VM (not the toy VM), so this verdict
  does not depend on the toy-specimen repair (AMENDMENT_2026-09-28b).
- ROBUST: P-11 is over-strict (rejects complement, guest-in-host,
  two-tape and one-slice-budget bytewise copiers), and A0 holds: in the
  same cell, a 3-step painter passes C2 20/20 while a genuine bytewise
  copier passes 0/20 for lack of time -- P-11 favours painters over
  copiers in the BYTEWISE arm by budget, not by evolution.
- REPAIR-SENSITIVE: the choice between CVT-2 (mechanical pick after the
  repair, which was applied to all nine toy specimens rather than only
  the two that failed) and CVT-R. On the unrepaired toy ISA only CVT-R
  matches the corrected truth. Artemis therefore recommends CVT-R as the
  certificate that is adequate under both readings; CVT-2 is the
  preregistered mechanical selection.
- NATURAL DONORS (new file, nothing rescored): from a fresh state only
  6/57 re-pass P-11 at all; 4 of those 6 carry 0 transmitted bits
  (painters, three of them in BLOCK cells); 2 are genuine copiers (7ae3,
  e141, ~7.4 bits). BYTEWISE claim N1 INCONCLUSIVE (1 recertified < 5).
