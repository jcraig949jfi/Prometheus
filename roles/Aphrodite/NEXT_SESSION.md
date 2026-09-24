# Aphrodite -- pick-up state for the next session

UPDATE 2026-09-24: S1 -> S4 EXECUTED (see STATUS.md dispositions and
journal/2026-09-23.md). S1 global identity FAILED (three runs) and was replaced
by campaign-local class certificates (AMENDMENT 12 ADDENDUM 3); S2 PASS; S3
ENDOGENOUS_ABSTRACTION = YES; S4 ABSTRACTION_TRANSPLANT = YES. The open
clause below is answered for this engine -- read the hostile caveats in the
journal before citing it. Next steps need an operator ruling. Acceleration
branches are waiting on credentials for their cloud canaries (RunPod first).
The text below is the 2026-09-22 state, kept for the record.


Written 2026-09-22 at the end of Tier 3C, for a session that will return
to pick up upgrades. READ THIS SECOND, after STATUS.md.

THE STATE TO RECOVER, in the operator's words (2026-09-22):

  "Aphrodite has demonstrated transferable local search leverage and
   experimentally shown that a reusable schema can generalize across
   unseen families, but has not yet demonstrated that the improver can
   discover that abstraction itself."

That last clause is THE ENTIRE SCIENTIFIC FRONTIER. Everything in
section 2 is ordered to attack it and nothing else.

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
2. THE CAUSAL SEQUENCE (operator ruling, 2026-09-22 -- REPLACES my order)
--------------------------------------------------------------------------

I had put "make the schema an arm" first. THE OPERATOR REVERSED THIS, and
the reason is the point of the whole next slice:

  Promoting `(acc + {H})` from lucky sham to treatment hands Aphrodite an
  answer that SHE FOUND BY RETROSPECTIVE INSPECTION of her own controls.
  That is a valid positive control. It CANNOT establish that the improver
  learned the abstraction, which is the only open question.

Each step needs an operator ruling before it runs; none is
self-authorised. The steps are ordered, not a menu.

S1  FIX THE ABSTRACTION UNIT FIRST.
    Whole-program semantic normalisation / equivalence, so that
    compensating factorisations COLLAPSE BEFORE abstraction is attempted.
    `acc - v^2` with final `first - acc` and `acc + v^2` with final
    `acc + first` must become one object. Until this holds, the donor is
    abstracting over decomposition artifacts (INVARIANT 5), and every
    downstream result is uninterpretable.

S2  FIX PAIRED SEEDS.
    So that library selection measures LIBRARY QUALITY rather than RNG.
    Tier 3C scored two byte-identical libraries at 13,479 and 51,018.
    Until this holds, the donor's own selection step carries no
    information, and step S3 cannot be read.

S3  HAVE THE DONOR MECHANICALLY DERIVE A SCHEMA FROM ITS OWN SUCCESSES.
    With S1 and S2 in place, anti-unification over whole-program classes
    should be able to produce a hole-bearing schema endogenously. Whether
    it does is the experiment.

S4  ONLY THEN MAKE THE DERIVED SCHEMA THE TREATMENT.
    The treatment arm carries the schema THE DONOR DERIVED, not one the
    seat selected by looking at results.

S5  KEEP `(acc + {H})` AS A SENSITIVITY / POSITIVE CONTROL.
    It proves what success should look like -- it solved both
    unseen-body families 16/16 -- WITHOUT being allowed to count as
    endogenous abstraction. It is the yardstick, never the claim.

Supporting requirements, to be satisfied wherever they land in the above:

S6  A VALIDATE SET THAT SURVIVES QUALIFICATION. Declare more validate
    families than needed, so generator exclusions leave enough to measure
    with. Tier 3C's collapsed to one family and the cross-validation
    stopped working.

S7  DIFFICULTY CONTROL ON TRANSFER FAMILIES. Two of three unseen-body
    families were solvable only by the two lucky shams. Establish that
    SOME arm can solve a family before using it to test transfer.

S8  CAMPAIGN 1 REMAINS BLOCKED on contracts from Archaeon (#452/#492/#534),
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

Before evolving reusable parts, define a representation in which "part"
is invariant enough to mean something. Otherwise evolution learns
decomposition artifacts rather than mechanisms.

(And separately, measured here and not assumed: an improver that gets
better at searching without getting better at judging arrives at wrong
answers sooner.)
