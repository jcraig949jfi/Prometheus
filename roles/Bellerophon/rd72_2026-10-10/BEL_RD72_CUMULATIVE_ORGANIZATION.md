# BEL-RD-72 CUMULATIVE ORGANIZATION (Workstream C)

Status: C1 (as E1 / E1b), C2, C2R, C3 and F1 complete. Every number
below is from a frozen analysis unless marked descriptive or exploratory; receipts in receipts/, prereg sections cited.

## 1. The question as tested
Can a population (a) acquire a computational capability, (b) keep it, (c) acquire a second one, (d) hold both in one
organism? Does possessing the first change the reachability of the second (C3)? Does a capability survive the loss of
the lineage that carried it, and if so, is it held by heritable reconstruction or by the environment (C2)?
Substrate: z80atlas v3 (coupled resource ledger, K40 income), GRID LOCAL, lifespan 40. Task COND_ONE (x < 128 -> x, else
x + 1) or COND_MULTI (else (x ^ 0x55) + 3). Its low half is solved by ECHO and its high half (COND_ONE) by INC; the
composite needs a compare-and-branch.

## 2. C1 -- sequential acquisition (E1 / E1b, prereg s6, s6-D1, s6-A)
- E1 (first setting) STOPPED at 16/80 runs: the setting kept no replicators (my pilot measured "alive", not FUNC); disclosed.
- E1b (150 worlds, 3,000 ticks), frozen tests:
  - E1-a (LO, paid > unpaid): 15/80 vs 6/30, p 0.67, NOT SUPPORTED.
  - E1-b (BOTH): 0 vs 0, NOT SUPPORTED.
  - E1-c (ordering of composite events): nothing to order.
- Survival dominates: about 80% of worlds lose every replicator before tick 500 in every cell.
- Among established worlds (FUNC at t500; descriptive):
  - LO 15/16 paid vs 6/11 unpaid (p 0.027); HI 13/16 vs 0/11.
  - LO retention median 0.97 paid vs 0.06 unpaid. Payment does keep a capability once it exists (acquire + preserve: YES).
- Second capability: in 13 paid COND_ONE worlds an LO solver and an HI solver COEXISTED for up to 2,800 ticks (acquire a
  second: YES, in the population).
- Both in one organism: NEVER (0/150 worlds). Third, dependent capability: not reached.
- Triviality (ruler, RU-E1b): every LO solver is a whole ECHO machine (34/34) and every HI solver a whole INC machine
  (13/13), with 1-7 critical bytes each. The "halves" are two independent minimal programs, not partial composites.
- Geometry (DP, exploratory): from these tapes and from splices of the coexisting pair, 0 one-step routes (~3.9M
  neighbours) and 0/52,000 sampled 3-step paths reach the composite. A positive control shows the probe sees routes
  where they exist.
- The directive's controls are not all run: fresh vs reset populations, equal total budget, final-task-immediately.
  With 0 composites in the treatment arm there is no order advantage to explain, so these controls would have nothing
  to discriminate; they stay in NEXT_CAMPAIGN for a setting where composites occur.

## 3. C3 -- mechanism dependency (prereg s7)
- C3-P1 (A-present vs ablated vs sham) and C3-P2 (A transplanted into foreign backgrounds vs sham): NOT_TESTABLE, with 0
  composite events in all 64 runs.
- Whether A (ECHO) makes B (the composite) reachable is therefore UNANSWERED by evolution. Geometry answers the narrower
  static question: possessing ECHO, or ECHO + INC side by side, puts the composite no closer than 4 steps (DP + triviality
  audit s2: no rung below COND_ONE has a one-step route to it).
- Descriptive: implanting a foreign ECHO solver raised end-state LO presence (6/10 vs 4/10) and FUNC survival (8/10 vs
  5/10). Small n, no test.

## 4. C2 / C2R -- lineage-independent persistence (prereg s7, s9)
- C2-b, frozen: after every LO carrier is removed, LO returns in 12/16 worlds, faster than its original acquisition in
  8 (slower 1, ties 3), sign p 0.0195. HOLDS.
- C2R, frozen, which separates the reading the directive asked for:
  - Removing only carriers: return 16/16, median delay 60 ticks.
  - Also removing near-carriers (Hamming <= 16): 12/16, median 80. REMOVE was faster in 10/12 decided worlds, p 0.019.
  - Replacing the whole population with fresh copiers (no world material): 9/16, median 140. REMOVE was faster in 13/15,
    p 0.0037.
- Classification (directive C2): ENVIRONMENTAL REGENERATION. The capability is held by non-carrier, near-functional
  material that copiers re-complete, plus some fresh re-invention, because ECHO is cheap. It is not heritable
  reconstruction by a continuing lineage, and it is shown for a MINIMAL capability only.
- Limits: re-acquisition = first appearance (some do not last to the next 100-tick census); the NEAR arm removes more
  organisms (no size-matched sham).

## 5. F1 -- crossing the composite desert from controlled distances (prereg s10; RESULTS_LOG F1)
Founders at controlled distances from a verified composite witness:
- W0 (the composite itself), 1, 2 or 4 knockouts, an ECHO hybrid, or the bare copier;
- payment ON and OFF, 20 worlds each.
Results:
- The planted composite is NOT kept. Paid, it survives to the end in 1 of 14 worlds that keep replicators and decays
  into ECHO / INC half-solvers. Unpaid, it is gone before tick 100.
- 0 crossings from any founder, including those one substitution away.
By the frozen rule, the E1b null is DESTRUCTIVE SELECTION / INSTABILITY, not inaccessibility. The composite is
downhill-unstable in this setting.
Cause, by two frozen manipulations:
- F2: removing half-credit (paired-halves payment) does NOT rescue maintenance (2/20 vs 1/20). The half-credit
  hypothesis is rejected.
- F3: lowering the mutation rate DOES rescue it, 1/20 (MED) -> 13/20 (LOW) -> 17/20 (VLOW), p 2.0e-7. An error threshold.
- So cumulative organization in this substrate is bounded by a variation-maintenance conflict. The mutation rate that
  lets populations find cheap capabilities destroys a ~10-critical-byte composite.
- The only evolved composite in the campaign (F2, f2_00022) is a distance-1 repair; F4 tests crossing at LOW mutation.

## 6. Disposition for Workstream C
- Accumulation of two INDEPENDENT minimal capabilities in one population, kept by payment: observed.
- Composition of them into one organism: not observed; geometrically far. A PLANTED composite is not maintained either
  (F1): in this setting the composite is unstable, so cumulative organization is limited by maintenance, not only by
  reachability.
- Dependency of the second mechanism on the first: not testable in this substrate at this horizon. The reason is now
  known: at the search mutation rate the composite is above the error threshold (F3); payment structure is not the cause
  (F2).
- Lineage-independent persistence: real, confirmed, and environmental (stored near-functional material) for a minimal
  capability.
- No case was found in which an evolved mechanism changed the accessibility of a future computational mechanism (the
  directive's "strongest result").
