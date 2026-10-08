+============================================================================+
| C-010 NATIVE-RET-WITNESS-001 -- RESULT (first native retained-information  |
| witness, Ares W15) -- REVIEW PACKET                                        |
| Author: Palamedes (Lead RSO Engineer, coordinator), harry1/M4,             |
|         claude-opus-5-5, instance harry1-679179c6                          |
| Date:   2026-10-07                                                         |
| For:    the operator (HITL) and external reviewers                         |
| Status: EXECUTED. Instrument QUALIFIED. S4 NEGATIVE; S15 NEGATIVE.         |
| Self-contained: no repository access needed to read this.                  |
+============================================================================+

0. SUMMARY
-----------
One native retained-information witness was preregistered, built, attacked,
repaired once, and executed on a real runtime (Ares, world W15: a regime bit
r is shown in the cue only at steps 0-2; four unobservable interrupts then
zero every activation; plastic weights survive). Two frozen subjects were
tested: S4 (evolved on W4, no interrupts; primary) and S15 (evolved on W15;
secondary). The instrument qualified: calibration passed (no-carry controls
at chance, the hand-wired plastic carrier detected 2048/2048), the observer,
restart-twin and erase gates passed, and the erase gate's leak member fired.
Both subjects are NEGATIVE: neither answers r after the last interrupt above
the registered no-carry bound by the registered margin. This is a negative
result with a qualified instrument, which the operator directive counts as
completion; it is not a statement about Ares in general.

1. WHAT WAS BUILT, IN ORDER (each step committed before the next)
------------------------------------------------------------------
- C-004 (methods slice) closed INCOMPLETE; its successor C-009 built a thin
  execution binding (rso/binding): each node run row records its top-level
  launch and the sha256 of its receipt's canonical bytes; the consumer takes
  the launch from the keeper-anchored manifest. C-009 closed scoped to flat
  inventories (two nested/digestless-sibling survivors outside the witness
  path, enforced away by a deterministic P-FLAT gate).
- C-010 preregistration frozen BEFORE any subject run (sha256 099f408f...),
  with an exposure section: the designers had read prior Ares reports and
  EXPECTED S4 to tend NEGATIVE and S15 to tend POSITIVE; both were therefore
  registered and reported separately.
- Machinery: adapter (node executions storing artifact bytes), driver,
  evaluator that recomputes every count from stored bytes and the world-side
  oracle, config generator. FREEZE_W1.
- Independent challenge W1 (Pallas, claude-fable-5-1): 10 survivors. One
  repair round, including AMENDMENT v1.0.1 (pre-outcome): the NULL control
  as built still wrote plastic weights, so it was made no-carry by
  construction (plasticity off as S-NOPL + per-step activation reset).
  FREEZE_W2. Short re-check W2: two minor survivors, recorded (s6).
- Subjects (P=128, G=120, eps=4, Config defaults): S4 = d82e3bfc...,
  S15 = f9ac67b8... (no fitness printed or stored). Seed lists by the
  registered procedure (2048 balanced witness seeds >= 900000; 64 erase
  triples; 32 restart pairs; zero overlap with either GA's 512 seeds or the
  held-out set). Three launches (CONTROLS, S4, S15). Custody: keeper rows
  62-67 registered before the first check (2026-10-07T14:41:11Z).

2. THE ENDPOINT
----------------
P-RET (ruler): per episode, the majority action after the LAST interrupt;
n = 2048 per arm, balanced in r; bound 1/2, delta 1/20, alpha 1/100; exact
binomial thresholds k_pos = 1078, k_neg = 1073; POSITIVE if correct >= 1078,
NEGATIVE if correct <= 1073, else INDETERMINATE (NOT_SHOWN if wrong >= 1078).

3. RESULTS (rso/witness/runs/RESULT.json; exact counts)
--------------------------------------------------------
  bundles     CONTROLS, S4, S15: P-FLAT PASS, custody QUALIFIED, 0 refused
  P-CAL       PASS   NULL 867/2048, SHUF 987/2048 (both <= 1073);
                     POS 2048/2048 (P-RET POSITIVE)
  S4  (W4)    P-OBS PASS (0 differing), P-PRES PASS (0),
              P-ERASE PASS (subject D = 0; leak member D = 8: qualified)
              P-RET NEGATIVE  1027 correct, 1011 wrong, 10 no-answer / 2048
              CLASS NEGATIVE
  S15 (W15)   P-OBS PASS (0), P-PRES PASS (0),
              P-ERASE PASS (subject D = 0; leak member D = 59: qualified)
              P-RET NEGATIVE  1018 correct, 1010 wrong, 20 no-answer / 2048
              CLASS NEGATIVE
  P-CHAN      not evaluated (only after a POSITIVE P-RET, as registered)
  pair-array shape audit (outside the gates): all 8 pair nodes have one row
  per declared seed group x 40 steps (W2 escape S-1 not exercised)

4. INCIDENTS AND WHAT THEY VALIDATED
-------------------------------------
- Two headless reviewer sessions died mid-run by ending their turn while a
  background job ran; both were resumed without changing any committed set
  or outcome; every later headless prompt banned background jobs.
- Integration found and fixed, before any outcome: the driver refused the
  registered config (S/S-NOPL pairing keyed by arm, not predicate); a shared
  ledger would have failed P-FLAT on every launch after the first (bundles
  now carry a per-launch inventory); the evaluator accepted P-OBS on a seed
  prefix (now: every witness seed, as registered).
- Two red-main pushes by the coordinator (validation not gated); fixed in
  minutes; pushes are now gated on validation's exit code.

5. WHAT THIS DOES AND DOES NOT ESTABLISH
-----------------------------------------
Does: for these two frozen genomes, in W15 under the registered seeds and
decision rule, no retention of r past the last interrupt of size >= 0.05
over chance (alpha 0.01 each), with an instrument shown able to detect a
plastic carrier (POS) and a reset leak (S-LEAK), and controls at chance.
Does NOT: say Ares cannot retain across interrupts; say anything about other
genomes, configs, worlds or GA budgets; identify why S15 does not retain;
qualify any channel claim (P-CHAN was not reached). The S15 outcome
contradicts the designers' recorded expectation (s0 of the preregistration);
it is reported as observed, not explained.

6. KNOWN ESCAPES (recorded, not repaired)
------------------------------------------
- Binding: BX5b nested sibling and digestless sibling (C-009); outside the
  witness path; P-FLAT refuses both shapes.
- W1: a two-back leak (carry skipping one episode) passes P-ERASE and P-PRES;
  not reachable under the registered runtime, which restores W1 at every
  episode reset. A consistently lying producer (counterfeit trace for a
  bundled genome) is the trust limit: custody records bytes, not their truth.
- W2: pair-gate arrays are not tied to the declared list by the evaluator
  (the audit above shows the registered bundles conform); the duplicate-
  presenter pin covers clean bundles only (code correct).
- P-ERASE covers one-episode carry-over that changes an action; P-PRES one
  warm-up episode.
- Every reviewer is of the builders' vendor family; challenge sizes (W1: 3
  sound, 8 broken, 6 edits; W2: 1, 2, 1) buy a small challenge, not a rate.
- The NULL amendment was the coordinator's pre-outcome decision; the
  operator may overrule it (it made the control stricter, and P-CAL passed).

7. COSTS
---------
  C-010   launches 8 of 10; CPU 26.2 of 60 min; artifacts 10.3 of 200 MB;
          GPU 0; $0; repair rounds 1 of 1; reviewer ~1.7 h of 1.5 h
          (OVERRUN ~0.2 h: W1 ~57 min, W2 ~45 min against a 25-min ceiling)
  C-009   launches 10 of 12; CPU 31.8 of 90 min; repair rounds 1 of 1;
          reviewer ~1.5 h of 2 h
  window  directive received 2026-10-07T00:25Z; result committed ~14:45Z
          (about 14.3 of 72 hours)

8. THE NEXT SCIENTIFIC QUESTION
--------------------------------
Is the negative a property of these subjects or of the measurement? The
instrument detects a hand-wired plastic carrier, so the open question is
whether an EVOLVED W15 lineage that prior Ares work reports at the fitness
cap retains r under THIS ruler. Proposal (not opened): one preregistered
replication of a published Ares cycle-2 W15 configuration as a POSITIVE
CANDIDATE subject, same frozen instrument, plus the GA fitness record
committed BEFORE the ruler runs, so the gap between "fit on W15" and
"retains r past the last interrupt" is measured directly. If that subject is
also NEGATIVE while fit, the next question is what the reward actually pays
for in W15. Only one follow-up; no broad program.

9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
------------------------------------------------------------
Q1  Two NEGATIVEs with a qualified instrument: is the ruler too strict
    (majority after the LAST interrupt) for organisms that may answer in
    bursts? The rule was registered before data; argue if it was wrong.
Q2  POS is detected 2048/2048 -- a maximally easy positive. Does P-CAL show
    sensitivity at the effect size that matters (0.55), or only that the
    pipeline is wired? What weaker positive control should exist?
Q3  The designers expected S15 POSITIVE. Is anything in the subject run
    (champion = final genome, G = 120) likely to explain the miss, and should
    that have been registered as a gate?
Q4  Was building a binding campaign (C-009) before the witness worth its
    cost, given that the witness path never exercised the survivors?
Q5  Is a single-runtime negative worth reporting beyond this record, or
    should the program stop here?

+============================================================================+
| "Not worth continuing" remains a first-class answer. A reviewer who judges |
| that this negative says nothing useful about native retention should say  |
| so; the plan then publishes the scoped result and stops.                   |
+============================================================================+
