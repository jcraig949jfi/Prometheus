# Aphrodite -- pick-up state for the next session

Written 2026-09-22 at the end of Tier 3C, for a session that will return
to pick up upgrades. READ THIS SECOND, after STATUS.md.

--------------------------------------------------------------------------
1. WHERE THE SCIENCE STANDS (one paragraph)
--------------------------------------------------------------------------

The local engine works end to end: lineages evolve, artifacts freeze and
hash, fresh recipients receive them through a qualified membrane, and a
hostile post-freeze tribunal judges the results. Four dispositions stand:

    DIRECT_COMPETENCE_REUSE          NO        (slice 3)
    STRUCTURAL_SEARCH_LEVERAGE       YES       (slice 4, equal expressivity)
    TRANSFERABLE_SEARCH_LEVERAGE     YES_LOCAL (Tier 3B 47x, Tier 3C 345x)
    BOUNDED_RECURSIVE_SELF_IMPROVEMENT  NO     (Tiers 3A, 3B, 3C)

Nothing here is Campaign 1 evidence. Campaign 1 remains FROZEN and UNRUN.
Tier 3A, 3B and 3C are never pooled with each other or with anything else.

--------------------------------------------------------------------------
2. THE UPGRADE QUEUE, IN PRIORITY ORDER
--------------------------------------------------------------------------

Each needs an operator ruling before it runs; none is self-authorised.

U1  MAKE THE SCHEMA AN ARM, NOT A SHAM DRAW.
    Tier 3C's strongest evidence came from two randomly-seeded controls
    (SHAM_0, SHAM_5) that happened to carry `(acc + {H})` and solved both
    unseen-body families 16/16 while every schema-less library failed.
    The obvious next experiment makes a schema-bearing library the
    TREATMENT, with matched schema-free and wrong-schema controls.
    This is the single highest-value item.

U2  ABSTRACT OVER WHOLE-PROGRAM SEMANTIC CLASSES.
    The donor failed because it abstracted over loop BODIES, and a body
    is not invariant: `acc - v^2` with final `first - acc` is the same
    program as `acc + v^2` with final `acc + first`. Either abstract over
    the whole program's class, or canonicalise the body/final split
    first. Without this, abstraction-from-self-observation is unreliable
    in principle, not merely in practice.

U3  PAIRED SEEDS ACROSS ARMS AND CANDIDATE LIBRARIES.
    Two libraries with identical content scored 13,479 and 51,018 in
    Tier 3C because the search seed string contained the library name.
    Identical content must produce identical cost. This invalidated the
    donor's own selection step.

U4  A VALIDATE SET THAT SURVIVES QUALIFICATION.
    Declare more validate families than needed, so that generator
    exclusions leave enough to measure with. Tier 3C's collapsed to one
    family and the cross-validation stopped working.

U5  DIFFICULTY CONTROL ON TRANSFER FAMILIES.
    Two of three unseen-body families were solvable only by the two lucky
    shams. A pre-run control should establish that SOME arm can solve a
    family before it is used to test transfer.

U6  CAMPAIGN 1 REMAINS BLOCKED on contracts from Archaeon (#452/#492/#534),
    Harmonia (#453/#490/#533) and Vivarium (#454/#491/#532), and on
    benchmark receipts from Nestor (#471/#474) and Archaeon (#472/#475).
    Unchanged since 2026-09-21.

--------------------------------------------------------------------------
3. GATES AND DISCIPLINES THAT MUST NOT REGRESS
--------------------------------------------------------------------------

G1  THE CONFORMANCE GATE (engine/conformance.py) must be GREEN before any
    run. 21,600 differential comparisons, search evaluator vs emitted
    artifact evaluator, over normal / boundary / overflow / failure
    values. Four separate slices were damaged before this existed.
    Re-run it and report the number with every result.

G2  GENERATOR QUALIFICATION, not single-sample qualification. 200
    independent draws per candidate development size; grow the battery
    until the 95% upper bound on surviving wrong semantic classes is
    < 0.05; REJECT the family otherwise. This took false positives from
    4.688 per recipient to ZERO.

G3  SEMANTIC IDENTITY, never source-string identity, anywhere. The layer
    is engine/semantics.py with fixtures in engine/tests/test_semantics.py.
    Source strings are provenance only.

G4  PID-VERIFIED PROCESS TERMINATION. TaskStop does NOT kill the detached
    python child. Verify with Get-CimInstance / Get-Process that the PID
    is gone. Two orphans once survived for 18 hours at 3.8 GB and
    contaminated wall-clock across two slices.

G5  WALL-CLOCK FROM SLICE 4 AND TIER 3A IS PERMANENTLY CONTAMINATED and
    is marked so in their packets. Charge-based endpoints are unaffected;
    they are the primary endpoints in both amendments.

--------------------------------------------------------------------------
4. WHERE THINGS LIVE
--------------------------------------------------------------------------

  engine/                   the local engine, all tiers
    AMENDMENT_*.md          every frozen design, in order 2..11
    conformance.py          G1, the standing gate
    semantics.py            G3, layered identity
    tier3b.py, tier3c.py    frozen catalogs + qualification
    *_RESULTS_*.json        per-slice data, never edited after the fact
    SLICE2B_VALIDITY_SCAR.md  an impaired result, kept reproducible
  pivot/APHRODITE_ENGINE_REVIEW_*.md   ten review packets, 1..10
  library/METHODOLOGY.md    standing invariants
  library/THEORIES.md       T0-T10
  science/campaign1/        the frozen prereg and its amendments
  journal/2026-09-22.md     today, including every error in full

  branch aphrodite/engine-2026-09-21, pushed. Worktree
  C:\Prometheus-worktrees\aphrodite-base-role. Host M4.

--------------------------------------------------------------------------
5. THE ONE SENTENCE TO REMEMBER
--------------------------------------------------------------------------

An improver that gets better at searching without getting better at
judging arrives at wrong answers sooner; and an improver that abstracts
over a component of a factorisation will abstract over the wrong thing.
Both were measured here, neither was assumed.
