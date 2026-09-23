# Aphrodite status

Currency: 2026-09-22 (Tier 3C closed; engine work paused for upgrades).

seat state: ACTIVE on its charter (APHRODITE-08 APPROVED 2026-09-18).
what it asserts: PRESENT (comms), ACTIVE, PRODUCTIVE (engine tiers 1-3
  and ten review packets committed); VALID not asserted. Evidence held:
  TIER 1 (E1-E4, X1, X2, S1-S4, X-S3, X-Z). TIER 2: Campaign 0/0B/0C
  and the local engine, all apparatus. TIER 3: designs, frozen
  prereg + amendments. TIER 4: none, and none in prospect.
workspace: worktree aphrodite-base-role, branch
  aphrodite/engine-2026-09-21 (pushed, head 4469736ca). Host harry1 (M4).
guard: linked worktree (git-dir differs from git-common-dir).
comms: M1 canonical store via EW_DB_HOST=192.168.1.202.

READ NEXT: NEXT_SESSION.md -- pick-up state, the ORDERED causal sequence
S1-S8 (operator ruling 2026-09-22; the steps are ordered, not a menu) and
the standing gates G1-G5.

The open question, in the operator's words: Aphrodite has demonstrated
transferable local search leverage and experimentally shown that a
reusable schema can generalise across unseen families, but has NOT yet
demonstrated that the improver can discover that abstraction itself.

## Dispositions on record (never pooled with each other)

  DIRECT_COMPETENCE_REUSE             NO         slice 3
  STRUCTURAL_SEARCH_LEVERAGE          YES        slice 4, equal expressivity
  TRANSFERABLE_SEARCH_LEVERAGE        YES_LOCAL  Tier 3B 47x, Tier 3C 345x
  BOUNDED_RECURSIVE_SELF_IMPROVEMENT  NO         Tiers 3A, 3B, 3C
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
