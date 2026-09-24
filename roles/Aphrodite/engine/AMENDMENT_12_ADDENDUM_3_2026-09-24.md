# AMENDMENT 12, ADDENDUM 3 -- GLOBAL IDENTITY FAIL; CAMPAIGN-LOCAL CLASS
# CERTIFICATION. FROZEN AND COMMITTED BEFORE THE CERTIFIER IS CODED AND
# BEFORE ANY CLASS IS CERTIFIED.

Dated 2026-09-24. Applies the operator's ruling "S1 DISPOSITION -- GLOBAL
IDENTITY FAIL / CAMPAIGN-LOCAL CERTIFICATION AUTHORIZED" (option A,
tightened). Campaign 1 remains FROZEN and UNRUN.

--------------------------------------------------------------------------
1. DISPOSITIONS (permanent, recorded separately)
--------------------------------------------------------------------------

    GLOBAL_BEHAVIOR_IDENTITY   = FAIL   (runs 1, 2, 3; run 3 is NOT relabelled)
    CAMPAIGN_RELEVANT_IDENTITY = PASS / FAIL, decided by section 5

Global residual false-merge rate, reported wherever identity is used:
13 / 3,445 classes (run-3 sample, D_TASK_T3_v1) and 74 / 7,808 classes over
the donor member space H1 x H2 x FINAL. Every known case is an
internal-overflow threshold: fast-growing accumulators that cross 10^40 one
step apart on rare valid inputs.

behavior_id is from now on a PROVISIONAL EQUIVALENCE BUCKET: a fast candidate
relation with known residual false merges. It is not a claim of semantic
identity. A class may influence science only through a CLASS CERTIFICATE.

--------------------------------------------------------------------------
2. WHAT MUST BE CERTIFIED
--------------------------------------------------------------------------

Before it influences abstraction, library selection, treatment construction
or scientific interpretation:
  C1 every donor-observed success class entering S3 (AMENDMENT 14 D2);
  C2 every member set enumerated for anti-unification (D3), i.e. each
     class's members in M;
  C3 every class whose members' bodies are carried in any candidate or
     selected library (MEMORISE, SCHEMA_k witness pairs);
  C4 every S4 class used to classify transfer or generalisation (criterion
     condition 7: the solving program's class vs the donor's observed
     classes).
Plus, at the S1-LOCAL GATE (section 5), before S2: the witness class of every
Tier-3D family and its member set in M.
Classes used only for telemetry are not certified and do not block.

--------------------------------------------------------------------------
3. THE CERTIFICATE (frozen here, before any class is seen)
--------------------------------------------------------------------------

A class certificate for a member set S (all programs placed in one
provisional bucket) PASSES iff every member of S returns the identical value
(FAIL included) on every input of BOTH:

  (i) FRESH VALID-DOMAIN BATTERY B_CERT: 20,000 inputs inside D_TASK_T3_v1,
      the B2 v3 mixture under the independent seed "APHRODITE/S1/CERT/v1".
      It is shared by all certificates and never used for any identity.

  (ii) THRESHOLD-ADVERSARIAL BATTERY A(S), generated per member set by a
      FROZEN procedure that uses the programs' structure but NOT the
      certificate outcome:
        BASES: the 29 constant sequences c^200 (c in 2..30); 40 two-valued
        sequences (alternating pairs (a, b) drawn under seed
        "APHRODITE/S1/ADV/v1"); 40 uniform random sequences of length 200
        (same seed). Query values q in {1, 2, 3, 7, 32, 33, 96, 97}.
        BRACKETING: for every member p in S, every base and every q, evaluate
        p on the prefixes base[:L] + [q] for every L in the domain's length
        set, and find the smallest L* at which p FAILS (crosses the ceiling
        or fails). Add the inputs at L*-1, L* and L*+1 (where they lie in
        the domain). At L*, also add the variants whose LAST sequence element
        is replaced by each value in {2, 3, 29, 30}, and whose query runs over
        every q in 1..97.
        A(S) is the union over members, deduplicated, and capped at 60,000
        inputs by a seeded uniform subsample if larger.
      Because each member contributes its OWN crossing boundary, two members
      that cross one step apart are evaluated exactly where they disagree.
      The generator is fixed here; it is not tuned after any class splits.

POWER, reported and not a gate: the certifier is also run on the 13 known
run-3 false merges and on the 74 member-space false merges, and the number
it splits is reported.

--------------------------------------------------------------------------
4. SPLITS
--------------------------------------------------------------------------

If a provisional class fails its certificate, it is SPLIT into the
sub-buckets on which its members agree over B1 u B_CERT u A(S). The class
carrying the observed program (or the witness) keeps only the members that
agree with that program. Only derived objects that have NOT yet entered an
experimental result are recomputed (member sets, LGG candidates, candidate
libraries), and the split is recorded.

If a split is discovered AFTER an artifact was frozen or an experimental arm
has run, nothing is repaired silently: the affected result is marked
INVALID / INCONCLUSIVE and the seat returns to the operator.

--------------------------------------------------------------------------
5. THE S1-LOCAL GATE (before S2)
--------------------------------------------------------------------------

CAMPAIGN_RELEVANT_IDENTITY = PASS iff
  - the witness class and member set in M of EVERY Tier-3D family is
    certified with ZERO splits;
  - conformance stays zero-mismatch (the 21,600 sweep, plus whole-program
    checks on the Tier-3D witnesses over B1 v3 and the boundary battery,
    emitter v2);
  - the global residual rate of section 1 is written into the report.
From then on the certificates of section 2 (C1-C4) are applied as each
class arises, under section 4.

--------------------------------------------------------------------------
6. S2-S4
--------------------------------------------------------------------------

On CAMPAIGN_RELEVANT_IDENTITY = PASS, S2, S3 and S4 run under AMENDMENTS 13
and 14 EXACTLY as frozen: the same families, arms, thresholds and criteria.
The only additions are the certificates of section 2 and the precondition
file (S1_LOCAL_GATE instead of an S1_PASS). No S1 diagnostic changes S2-S4.

ACCELERATION: certification sweeps are nonadaptive and parallel, and they are
the intended first scientific-support workload for the RunPod fasteval
backend, but only after its CLOUD canary passes. Until then the reference
engine computes every certificate.
