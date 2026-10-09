# THESEUS-39 part R: known-mechanism reproduction of the 20 admitted SYN concepts

Prereg: roles/Theseus/prereg/2026-10-09_syn_reinject/PREREG.md (0e93f7ac7), part R.
Command: PYTHONHASHSEED=0 python -m theseus.synth.syn_repro --workers 2.
This pass runs BEFORE any claim about the concepts.

## R1: battery fingerprint vs the known library
Library rebuilt from the source run's frozen CAL.json (seed master + 11, 40 per family).

| verdict | count |
|---|---|
| REPRODUCED_BY_KNOWN (dist <= tau_rep) | 2 |
| PARTIALLY_REPRODUCED (<= 2 tau) | 17 |
| NOT_REPRODUCED_YET | 1 |

The nearest families vary (predator-prey 7, forced-dissipative 4, phase lattice 3, others 1
each). As dynamical systems, the concepts sit near but mostly outside the known library's
reach at this refinement budget.

## R2: task fingerprint (8 variants) vs 75 hand-built store+release mechanisms

| verdict | count |
|---|---|
| REPRODUCED_BY_KNOWN (every variant within .05) | 13 |
| PARTIALLY_REPRODUCED (within .15) | 3 |
| NOT_REPRODUCED_YET | 4 |

- The 13 REPRODUCED concepts score J = 1.0 (or .99) on every variant, exactly like the
  simplest hand-built remember+inject program. On the task they are indistinguishable from a
  known store+release mechanism.
- Ceiling caveat: the task fingerprint saturates at 1.0, so "indistinguishable" here means
  "equally perfect". It does not establish that the internal mechanism is the same.
- The 4 NOT_REPRODUCED concepts are not better than the known mechanism. Each is WORSE on
  some variant, where the references stay at 1.0:
  - delay k 16 (J .26-.76);
  - alphabet V 8 (J .44-1.0).
  None beats the references on any variant.

## Reading for the claim language
- On the task, no SYN concept does anything a hand-written two-rule store+release program
  does not do as well or better.
- The concepts differ from it as whole dynamical systems (R1), and their essential task step
  is a collision-generated law (THESEUS-13). That is a different implementation of a known
  function, not a new function.
- Claim ceiling: "the ecology re-derived the known store+release function through its own
  generated interaction laws"; never "new mechanism".

## Predictions
- P5 (R2: >= 10/20 REPRODUCED or PARTIAL, p .65): 16/20, RIGHT.
- P6 (R1: <= 5/20 REPRODUCED_BY_KNOWN, p .7): 2/20, RIGHT.
