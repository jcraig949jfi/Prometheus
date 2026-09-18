+=====================================================================+
|  C5-01 -- DEEP NEUTRAL WALK: PREREGISTRATION                          |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Campaign 5, Phase A (operator directive 2026-09-18, verbatim on     |
|  file under roles/Archaeon/prompts/2026-09-18_campaign5/)            |
+=====================================================================+

QUESTION
  Does held-out exaptation continue increasing materially beyond
  neutral depth 16, or has the neutral network entered a yield plateau?
  The issue is MARGINAL discovery yield per additional accepted neutral
  step (and per evaluation), not monotonicity.

UNCHANGED FROM C4-05 (by the directive)
  band 1/16 around the ORIGINAL parent's reward on its environment (no
  ratcheting); frozen grammar v0.4 and weights (name=None); held-out
  exaptation = the D6 rule (>= parent + 1/16 AND >= 3/16 on another of
  the four C4 environments); competent / degenerate separation by the
  D4-003 flag; 32 proposals per step; noop proposals are not proposals;
  the same CRN episode sets (family train, index 1, E=16).

CHANGED, WITH THE MEASUREMENT-RESOLUTION ARGUMENT
  depth 64 (was 16), archived at 0/16/32/48/64; 6 walkers per parent
  (was 4). C4-05 at 188 walkers gave a depth-16 Wilson half-width of
  about .03 (rate .043, band [.022, .082]); the directive's question is
  a difference of rates between depths, and a 2-point difference cannot
  be resolved at that width. 47 competent parents x 6 = 282 walkers per
  depth: half-width about .02 at rates near .05 (Wilson), which is the
  smallest effect the branches below use. Walkers 1-4 reproduce C4-05's
  walks exactly (same seeds; the first 16 steps are byte-identical by
  construction and are checked); walkers 5-6 are new draws.

MEASUREMENTS
  per archived depth d: exaptation rate r_d with Wilson band; connected
  depth (share of walkers reaching d); acceptance by depth bin (1-16,
  17-32, 33-48, 49-64); structural and behavioural diversity as C4-05;
  reference-break share of accepted steps;
  YIELD PER EVALUATION: cumulative evaluations to reach depth d = the
  walk's proposals (one evaluation each, on the parent environment) plus
  the exposures (5 environments per archived walker); discovery yield
  Y_d = cumulative exaptive walkers found at or before depth d divided
  by cumulative evaluations. The comparator is a random single edit:
  C4-01's D6 rate .006 per edit at 5 evaluations per edit (parent env +
  4 others) = .0012 exaptive discoveries per evaluation.
  MARGINAL YIELD per accepted step between archives: (r_d2 - r_d1) /
  (d2 - d1) per walker-step.

PREREGISTERED BRANCHES (r_16 is C5-01's own depth-16 rate, not C4-05's)
  continued gradient   r_32 - r_16 >= .02 AND r_64 - r_32 >= .02 AND
                       r_64's Wilson lower bound > r_16
  plateau              |r_64 - r_16| < .02
  degradation          r_64 < r_16 - .02
  (a mixed outcome, e.g. a rise then a fall, is reported as MIXED with
   the numbers; it is not forced into a branch)
  PRESERVE_NEUTRAL_MECHANISM requires the continued-gradient branch AND
  Y_64 >= 2 x .0012 (neutral depth buys discovery at least twice as
  efficiently per evaluation as random single edits); otherwise, for
  Phase A's disposition, the neutral mechanism is NOT preserved.

CONTROLS
  replication   walkers 1-4 at depth 16 reproduce C4-05's committed rows
                (rates and step digests) -- the instrument is the same
  identity      the identity-proposal walker reaches depth 64 in 64
                proposals; randomize-all stalls at 0 (self-test)
  cheat         a hand-set walker with reward 1.0 elsewhere reads exaptive
  determinism   one parent's 6 walks reproduce byte-for-byte

DISPOSITION VOCABULARY
  CONTINUED_GRADIENT / PLATEAU / DEGRADATION / MIXED, each with the
  preserve decision; INSTRUMENT_INVALID on a control failure.

BUDGET
  47 x 6 x 64 steps at ~1.8 proposals per step ~ 32k evaluations + 282 x
  5 x 5 exposures ~ 7k; about a minute of compute. Degenerate gen0
  parents are walked and reported apart as before.
