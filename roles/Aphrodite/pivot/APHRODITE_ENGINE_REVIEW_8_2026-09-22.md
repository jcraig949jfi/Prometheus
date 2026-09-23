+==============================================================================+
| APHRODITE LOCAL ENGINE -- TIER 3A: TRANSPLANTABLE IMPROVER MODIFICATION      |
|                                                                              |
| Author:  Aphrodite (RSI science seat), machine M4                            |
| Date:    2026-09-22                                                          |
| For:     HITL (James) + external reviewers (no repo access needed)           |
| Status:  BOUNDED_RECURSIVE_SELF_IMPROVEMENT = NO                             |
|          Criterion C5 failed. My SHAM contained the answer. See section 2.   |
| Self-contained: every load-bearing number is inline.                         |
+==============================================================================+

------------------------------------------------------------------------------
0. VERDICT
------------------------------------------------------------------------------

    BOUNDED_RECURSIVE_SELF_IMPROVEMENT = NO

The criterion requires all six conditions. C5 -- "outperforms SHAM" -- is not
met on mt_sum_minus_last, where SHAM beat EVOLVED by 18x. The reason is a
defect in how I BUILT the sham, not a fact about the evolved artifact, and I
am reporting the NO rather than rebuilding the control and re-running. A
control repaired after seeing the result it decided is not a control.

What the run does show, and what it does not, is below. Nothing here is
Campaign 1 evidence; Campaign 1 remains unchanged and unrun.

------------------------------------------------------------------------------
1. RESULTS, PER FAMILY (primary = censored mean effort over ALL recipients)
------------------------------------------------------------------------------

  mt_sum_minus_last          [body kind SEEN by the donor]
    arm        censored effort   qualified   winners-med*   false pos
    EVOLVED         26,111         15/16         1,386          1
    PRISTINE        45,742         16/16        24,999          0
    SHAM             1,429         16/16         1,424          0     <-- C5 FAILS

  mt_gcd_plus_first          [body kind SEEN by the donor]
    EVOLVED        350,002          2/16            15         14
    PRISTINE       400,000          0/16             -         16
    SHAM           400,000          0/16             -         16

  mt_summod_times_first      [body kind UNSEEN by the donor]
    EVOLVED        400,000          0/16             -          5
    PRISTINE       395,259          1/16       324,136          5
    SHAM           400,000          0/16             -          5

  * winners-only medians are TELEMETRY and cannot establish improvement.

  marginal inheritance value (censored effort saved per recipient):
    mt_sum_minus_last       +19,631   (ratio 1.75)
    mt_gcd_plus_first       +49,998   (ratio 1.14)
    mt_summod_times_first    -4,742   (ratio 0.99)   <-- over-specialisation tax

------------------------------------------------------------------------------
2. WHY C5 FAILED: I BUILT A SHAM THAT CONTAINED THE ANSWER
------------------------------------------------------------------------------

The sham was declared as "the specialising entry built from the donor's FAILED
bodies rather than its successful ones". I implemented "failed" as "the first
eight bodies of the grammar that are not among the donor's observed success
STRINGS". The donor's observed body for summation was the string `(v + acc)`.
The canonical string `(acc + v)` was therefore classified as failed -- and it
is the second-simplest body in the entire grammar.

    SHAM bodies: (acc + acc), (acc + v), 0, 1, acc, first, last, v

So the sham library contains the exact optimal body for every summation
family, in a tiny 8-body entry searched first. On mt_sum_minus_last it finds
the answer in ~1,400 charges. It is not a sham; it is an excellent library
that I mislabelled.

THE DEEPER ERROR is the same one this program keeps finding: I compared
PROGRAMS BY THEIR SOURCE STRINGS rather than by their SEMANTICS. `(v + acc)`
and `(acc + v)` are the same function. Every equivalence test in this slice
that used string identity inherits the bug. The evolved library shows the
same fingerprint from the other direction -- its seven "specialised" bodies
include `(acc * math.gcd(abs(v), abs(v)))` and
`math.gcd(abs(v), abs(math.gcd(abs(acc), abs(acc))))`, which are baroque
spellings of `acc * v` and `gcd(acc, v)`. The donor abstracted its own
successes without ever recognising their canonical forms.

------------------------------------------------------------------------------
3. WHAT THE EVOLVED ARTIFACT DID DO
------------------------------------------------------------------------------

Against PRISTINE -- the comparison C5 does not touch -- the evolved library
helped on two of three families and cost slightly on the third:

  - mt_sum_minus_last:  26,111 vs 45,742 censored effort (1.75x)
  - mt_gcd_plus_first:  350,002 vs 400,000, and 2/16 qualified vs 0/16.
    PRISTINE never solved this family at all within escrow.
  - mt_summod_times_first: 400,000 vs 395,259 -- EVOLVED is WORSE. This is
    the over-specialisation tax, on the one family whose body kind the donor
    never saw: the evolved improver must exhaust 2,520 specialised candidates
    before reaching the general entry, and that cost is pure waste here.

I predicted the direction of all three of these before the run, from the
contents of the frozen library. That is the one part of this slice that went
exactly as designed.

------------------------------------------------------------------------------
4. THE FINDING I DID NOT EXPECT: FASTER SEARCH, FASTER WRONG ANSWERS
------------------------------------------------------------------------------

On mt_gcd_plus_first the evolved improver's winners-only median is FIFTEEN
charges. It finds a development-exact program almost immediately. And 14 of
its 16 recipients produced a FALSE POSITIVE -- a program exact on all four
development instances that the hostile tribunal then rejected.

    false positives      EVOLVED 20/48      PRISTINE 21/48      SHAM 21/48

A better search coordinate accelerates the discovery of programs that fit the
development set. It does not improve the development set's power to tell right
from wrong. The result is that the improved improver reaches plausible-but-
wrong artifacts faster, and only the tribunal -- which no improver can read --
distinguishes them. On gcd families with four development instances, spurious
exact fits are the norm rather than the exception for every arm.

If there is one transferable lesson from Tier 3A, it is this one, and it is
not about recursion: making a search faster is not the same as making it
better, and a system that improves its own search without improving its own
evaluation will get to wrong answers sooner.

------------------------------------------------------------------------------
5. COST ACCOUNTING (both efficiencies, separately, as required)
------------------------------------------------------------------------------

    MARGINAL INHERITANCE VALUE   mean 21,629 charges saved per recipient per
                                 family (including the negative family)
    META-SEARCH COST              2,022,419 charges
    BREAK-EVEN DESCENDANTS        93.5

The library must be transplanted into roughly 94 fresh improvers before the
downstream savings repay the meta-search that produced it. This slice used 48
recipients across three families, so the experiment as run is ECONOMICALLY
NEGATIVE by about a factor of two. A mechanism may qualify scientifically and
still not pay for itself; this one did neither, but the accounting is reported
because hiding an expensive meta-search behind cheap descendants is exactly
what the ruling forbids.

------------------------------------------------------------------------------
6. WHAT THIS ESTABLISHES
------------------------------------------------------------------------------

ESTABLISHED:
  - the Tier-3A machinery works end to end: one mutable component, an artifact
    frozen at a positional boundary and hashed, fresh improvers with no donor
    history, a tribunal no improver can read, and exactly one meta-generation
  - a bounded modification to improvement machinery CAN be extracted,
    transplanted, and measured
  - the evolved library beat PRISTINE on two of three unseen families and
    cost a little on the third, in the directions predicted pre-run
  - over-specialisation is real and measurable, on the one family that
    survived to test it

NOT ESTABLISHED, and explicitly denied:
  - BOUNDED_RECURSIVE_SELF_IMPROVEMENT. C5 failed.
  - runaway improvement, indefinite recursion, monotonic improvement across
    generations, general intelligence improvement, autonomous goal
    modification. None of these were tested and none may be inferred.
  - any claim that the evolved library is better than a good library. My
    accidental sham beat it on the family where both were applicable.

------------------------------------------------------------------------------
7. WHAT A CORRECTED RUN WOULD NEED (not performed, not self-authorised)
------------------------------------------------------------------------------

  R1 SEMANTIC equivalence classes everywhere. Bodies must be canonicalised by
     behaviour on a fixed probe battery, not by source string. This fixes the
     sham construction, the "observed successes" set, and the over-
     specialisation measurement simultaneously.
  R2 A sham defined POSITIVELY: an entry of equal size and interface whose
     bodies are drawn from behaviour classes the donor's successes did NOT
     occupy, verified to solve none of the meta-dev families.
  R3 Development sets sized so that false positives are not the norm. On gcd
     families four instances is plainly too few; the right number should be
     set by a pre-run false-positive measurement, not by taste.
  R4 More than one unseen-body family, since ADDENDUM 1 cost the design half
     its over-specialisation probe.
  R5 A meta-search budget declared against a target break-even descendant
     count, so the economics are a design parameter rather than an afterthought.

I am not implementing any of this. A corrected Tier-3A run requires a new
ruling, and it should be explicit that the corrected run is a REPLACEMENT for
this one rather than a second attempt whose best result gets reported.

------------------------------------------------------------------------------
8. QUESTIONS FOR THE REVIEWER
------------------------------------------------------------------------------

Q1. Is reporting NO correct here, or is it excessive self-punishment for a
    control defect that is clearly identified and clearly not the evolved
    artifact's fault? I chose NO because the alternative is repairing a
    control after seeing what it decided.
Q2. The string-vs-semantics bug has now appeared three times in this program
    under different disguises. Is there a structural fix, or is it simply the
    permanent tax on symbolic experiments?
Q3. Section 4: is "improves its search without improving its evaluation" the
    right general worry about self-improving systems, or is it an artifact of
    my four-instance development sets?
Q4. Break-even is 94 descendants against 48 recipients used. At what point
    does an economically negative mechanism stop being scientifically
    interesting?
Q5. EVOLVED solved mt_gcd_plus_first 2/16 where PRISTINE solved it 0/16 --
    a family neither could reliably do. Is a 2/16 improvement on an
    almost-impossible family evidence, or noise dressed as a result?

------------------------------------------------------------------------------
9. ARTIFACTS
------------------------------------------------------------------------------

  branch aphrodite/engine-2026-09-21
  fe1ca23c6  AMENDMENT 9, frozen before gate/meta-development/transplant
  roles/Aphrodite/engine/AMENDMENT_9_ADDENDUM_1_2026-09-22.md
  roles/Aphrodite/engine/TIER3A_ARTIFACT_2026-09-22.json  (evolved library
                                       61d6a1370587bfd4..., meta cost 2,022,419)
  roles/Aphrodite/engine/TIER3A_RESULTS_2026-09-22.json
  roles/Aphrodite/engine/{improver.py, meta_tribunal.py,
                          run_meta_development.py, run_tier3a.py}

+==============================================================================+
| END. "Your sham was better than your treatment and you are reporting a NO"   |
| is the correct summary. "Fix the semantics bug and run it again" is a        |
| first-class answer, as is "stop -- the false-positive rate means this        |
| apparatus cannot tell improvement from acceleration."                        |
+==============================================================================+
