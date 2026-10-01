# X0 -- Desk audit of historical apparatus nulls and false positives (RESULT)

Preregistration: experiments/X0_DESK_AUDIT_PREREG.md, frozen in commit d6f555fd7 before any item was coded.
Coding: workflow wf_30376741-75c (six primary coders x 35 items; one blind second coder on the 41-item hash sample).
Codes: experiments/X0_codes.jsonl (210 primary rows + 41 blind rows, each with a one-line reason).

## Numbers

    population coded                               210 / 210 (no missing, no duplicates)

    A. cheapest repair                             count    share
       RULER                                         113    0.538
       PROVENANCE_IMPLEMENTATION                      29    0.138
       WORLD                                          18    0.086
       STATISTICS                                     17    0.081
       SEARCH                                         11    0.052
       CAPACITY_SAME_SUBSTRATE                        11    0.052
       OTHER                                           7    0.033
       INDEPENDENCE                                    4    0.019
       SECOND_SUBSTRATE                                0    0.000

    B. shared element (items with one)             count    share of 55
       DATA                                           21    0.382
       RULER_OR_NULL_CODE                             15    0.273
       WORLD_GENERATOR                                 7    0.127
       AUTHOR                                          5    0.091
       PROMPT                                          3    0.055
       MODEL_FAMILY                                    3    0.055
       SUBSTRATE                                       1    0.018
       (NONE                                         155)

    p2 = 0 / 210 = 0.000          (rule: < 0.10 for depth-first)
    s  = 1 / 55  = 0.018          (rule: < 0.25 for depth-first)
    reliability: Cohen's kappa on A = 0.935 (observed agreement 0.951, chance 0.247, n = 41); blind coder's p2 = 0.000;
    agreement on B = 0.927.

## Outcome under the frozen rule

**DEPTH-FIRST CONFIRMED** (as recorded at freeze; relabelled NON-DISCRIMINATING for substrate count by the final review
-- see the addendum at the end). Kappa exceeds the 0.40 floor, so the outcome stands under the frozen rule. The architecture adopts one primary
substrate with a physics-ablation lattice, and commissions a second substrate only on the measured triggers in
RSE_ARCHITECTURE.md s3.

The single SUBSTRATE-coded item (sis-b:NES-1031) is the NPE case in which the world's own recombination splice
manufactured the matches a replication check credited to organisms. Its cheapest repair was still a ruler fix (measure
on a private replay before world variation), not a different substrate.

## What this result does and does not show (stated before interpretation creeps in)

- It shows that, for 210 historical failures, an in-substrate repair would have made the result interpretable. Ruler
  qualification alone was the cheapest repair for more than half. This is direct support for making the instrument
  qualification layer (E1) and the world forge (E2) the first-quarter priority, ahead of any search breadth.
- It does NOT show that a second substrate has no discovery value. The coding question asks for the CHEAPEST repair,
  and a second substrate is rarely cheapest by construction. The anti-gravity and convergence value of a second
  substrate is a different question, which the triggers and E7 address.
- Both coders are Claude-family agents (independence class I1), coding from reader digests and cited artifacts, not
  from re-execution. High agreement between same-family coders is weak evidence of validity. A cross-family
  re-derivation of a sample is listed in OPEN_QUESTIONS.md and FALSIFIERS.md.
- The population inherits the readers' primary classifications (evidence/historical_profiles.jsonl).

## Addendum (final review, 2026-10-01)

The final review (workflow wf_335d0a49-a24) found that X0 could not have selected its alternative and that several
inputs overstate it. Recorded here rather than by editing the result above:

- NON-DISCRIMINATING for substrate count. CAPACITY_SAME_SUBSTRATE included "added affordance within the same
  substrate", and SECOND_SUBSTRATE was coded only when nothing else could settle an item; every physics change can be
  phrased as an added affordance, and the coders did so (tan-b:AP-5, tan-b:AP-1, sis-b:ARES-TRANSFER). The population
  also excluded the 20 surviving anomalies, the class where a second substrate is the only discriminator. p2 = 0 was
  therefore close to guaranteed. The decision rule came from the judge whose recommendation it then confirmed. X0
  supports instrument priority (E1, E2 first); it does not decide the substrate count.
- Four apparatus nulls were excluded by a classification error. tit-a:TE-3, tan-b:TY-8, tan-a:ANA-XOR-NULL and
  tit-b:TB-03 carried primary_class true_negative although their own reclassification text says they are not; they are
  corrected in evidence/historical_profiles.jsonl ('correction' field) but were not coded here. The population would be
  214; p2 can rise to at most 4/214 = 0.019, so the recorded outcome cannot flip.
- Kappa is inflated. Both coders read the row, including the readers' primary_class and reclassification, and the
  repair code restates primary_class in most axis-classed items, so kappa 0.935 largely measures agreement on reading
  one label.
- The population is not purely historical seat results: it includes external-literature rows (ext:*) and Atlas rows
  that duplicate seat rows (for example atl:ATL-20 = sis-b:NES-1031).
- "Rescued" overstates the result: the criterion is "made interpretable", and 43 of the 113 RULER codes are false
  positives that a ruler repair would have caught, not rescued. RULER also covers planted controls, baseline ladders
  and leak audits, not ruler qualification alone.
- The 92 READER_ERROR rows in evidence/verification.jsonl were not propagated into the profiles X0 coded.

X0b (preregistered before the day-60 gate; RSE_ARCHITECTURE.md s9) asks the substrate question properly: the 20
surviving anomalies and 17 true negatives coded on "would a second substrate change the interpretation?", a separate
SUBSTRATE_CHANGE code for any change to primitives or affordances, >= 10 synthetic positive-control items that only a
physics change settles, coders blind to primary_class and reclassification, ext:* rows dropped and atl:* rows
deduplicated, a decision rule whose portfolio branch is shown reachable, and a conclusion scoped to the historical
demand regime (at most a one-cue latch).

### Sensitivity of the shares (verification pass, wf_1b94ed0a-e44)

Recomputed from X0_codes.jsonl (primary coder) and evidence/historical_profiles.jsonl, where 38 rows now carry a
reader_errors flag naming the verification.jsonl lines whose READER_ERROR verdicts mention them (17 of the 210 coded
items are flagged):

    population                                            n     RULER          SECOND_SUBSTRATE
    as coded                                              210   113 (53.8%)    0
    excluding ext:* (external literature)                 200   104 (52.0%)    0
    excluding ext:* and atl:* (Atlas, partly duplicate)   190    97 (51.1%)    0
    ... and excluding reader-error-flagged rows           177    89 (50.3%)    0

Kappa on the 41-item reliability sample is 0.935; without ext:* and atl:* items it is 0.932 (n = 38). Neither
removes the shared-label inflation described above, which needs blind re-coding (X0b). The ruler share is stable at
50-54% across these variants; the substrate result is unchanged and remains non-discriminating by construction.
