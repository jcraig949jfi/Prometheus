# Aphrodite status

Currency: 2026-09-25 (seat reset requested; S1-S4 done, A15/A16 recursion attempts untestable -- see NEXT_SESSION.md).

seat state: ACTIVE on its charter (APHRODITE-08 APPROVED 2026-09-18).
workspace: worktree aphrodite-base-role, branch aphrodite/engine-2026-09-21
  (pushed). Host harry1 (M4). comms via EW_DB_HOST=192.168.1.202.

READ FIRST: NEXT_SESSION.md (pick-up state, open questions Q-A..Q-E, where to resume), then journal/2026-09-23.md.

## Dispositions on record (never pooled with each other)

  DIRECT_COMPETENCE_REUSE             NO         slice 3
  STRUCTURAL_SEARCH_LEVERAGE          YES        slice 4, equal expressivity
  TRANSFERABLE_SEARCH_LEVERAGE        YES_LOCAL  Tier 3B 47x, Tier 3C 345x
  BOUNDED_RECURSIVE_SELF_IMPROVEMENT  NO         Tiers 3A, 3B, 3C
  GLOBAL_BEHAVIOR_IDENTITY            FAIL       S1 runs 1-3 (AMENDMENT 12 + ADD 1-2)
  CAMPAIGN_RELEVANT_IDENTITY          PASS       S1-local gate (ADDENDUM 3)
  FAIR_META_SELECTION (S2)            PASS       AMENDMENT 13
  ENDOGENOUS_ABSTRACTION (S3)         YES        AMENDMENT 14: donor derived and
                                                 selected (acc + {H})
  ABSTRACTION_TRANSPLANT (S4)         YES        all 8 conditions; 5 unseen-body
                                                 families; break-even 41.2 < 64
                                                 ACCEPTED by operator 2026-09-24
  BOUNDED_RSI                         NOT YET ESTABLISHED (operator 2026-09-24);
                                                 A15: NO / UNTESTABLE_CATALOG
                                                 A16: E1/E2 UNTESTABLE (time)
  S1_NECESSITY (A16 E4)               INCONCLUSIVE WHOLE 3/3, BODY_ONLY 1/3
  Tier 3A also: PRIMARY_CAUSAL_INFERENCE = INCONCLUSIVE_CONTROL_INVALID

## Campaign 1

FROZEN and UNRUN. Design frozen 2026-09-19 with PATCH 1 and AMENDMENTS 2
(eligibility R1-R5, mechanism-class labelling). Execution blocked on
contracts from Archaeon (#452/#492/#534), Harmonia (#453/#490/#533) and
Vivarium (#454/#491/#532), and benchmark receipts from Nestor
(#471/#474) and Archaeon (#472/#475). The local engine is NOT an
eligible C1 substrate and no engine observation is C1 evidence.

## Authorised / not authorised

authorised: local-engine work under AMENDMENTs 2-11, all apparatus.
NOT authorised: Campaign 1 execution; a second recursive generation
  (IMPROVER_1 -> IMPROVER_2); live LLM experiments; GPU allocation;
  model-host deployment; any positive RSI claim.

## Apparatus state

conformance gate: GREEN (21,600 differential comparisons, 0 mismatches).
main test suite: 39 passed. historical regressions: 1 strict xfail.
generator qualification: in force; rejected 3 of 9 families in Tier 3C.
false positives: ZERO across three families and ten arms in Tier 3C
  (against 4.688/recipient in Tier 3B).
contaminated measurements: slice-4 and Tier-3A WALL-CLOCK only,
  permanently marked. Charge-based endpoints unaffected.
open process discipline: verify termination by PID; TaskStop does not
  kill the detached child.

## Monitors

news monitor: registered task AphroditeNewsWatch, ACTIVE. Last recorded
  pass 2026-09-21 (1 admitted, 3 inspected, empty streak 0). Liveness of
  the TASK is not liveness of the DATA -- cite the data timestamp.

## Open operator decisions

APHRODITE-31 (may Aphrodite ask other seats about the RSI program roles),
APHRODITE-32 (Campaign 1 after the Campaign 0 report), and each step of
the sequence S1-S7 in NEXT_SESSION.md -- none self-authorised.

PARKED 2026-09-22 by operator instruction: no further science until the
next session.

--------------------------------------------------------------------------
UPDATE 2026-09-26 -- AMENDMENT 16 CAMPAIGN, SECOND EXECUTION (AMENDMENT 17)
--------------------------------------------------------------------------
Operator lifted the Q-A..Q-E hold 2026-09-26 and authorised the campaign.
Report: pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md
Prereg: engine/AMENDMENT_17_2026-09-26.md @ 373d7ef28. 48 min of 4 h; $0.
  E0 CATALOG_A TESTABLE (O4/V3/T4); CATALOG_B UNTESTABLE (O2/V2), not redrawn
  E1_BOUNDED_RSI = NO   (valid R1 novelty failure: G1 donors only met successes
                         (acc + {H}) already explains and re-derived it)
  E2_BOUNDED_RSI = UNTESTABLE (catalog); REPLICATED = NO
  G4_REPRESENTATIONAL_CEILING = UNTESTABLE (E2 never reached donors)
  S1_NECESSITY = SUPPORTED (WHOLE 3/3, BODY_ONLY 0/3; F3 repaired to F3*)
  RUNPOD/AZURE_UNAVAILABLE_TO_APHRODITE.
Binding constraint now: family SUPPLY for non-additive G4 operators (Q3/Q2
reject degenerate draws; mul/mod/powr 0/32 in both catalogs). Any new sampler
is an operator design choice. Engineering now available: a17.py exact-fast
Q2 (gated) + checkpointing; fasteval admitted by a 288k-pair gate.
Comms: experiments are no longer managed via Aporia or Cyclops; ignore them.
Branch aphrodite/a16-campaign-2026-09-26 (pushed; not yet merged to main).
