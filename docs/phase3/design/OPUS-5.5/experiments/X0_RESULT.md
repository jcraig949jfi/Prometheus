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

**DEPTH-FIRST CONFIRMED.** Kappa exceeds the 0.40 floor, so the outcome stands. The architecture adopts one primary
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
