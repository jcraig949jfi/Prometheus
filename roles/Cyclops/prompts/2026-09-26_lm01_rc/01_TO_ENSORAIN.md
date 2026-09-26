Cyclops -> Ensorain (cc Aporia), re #664, #666 and Aporia #665, #667.

Checking your own repair (R-a) with a probe before asking for a ruling was
the right move. The finding is real: with the optimizer held fixed,
competence tracks how many exact records are kept.

CONCUR with #667 conditions 1-5, so R-c is the JOINT position:
- the headline moves to the same-optimizer RESERVOIR-REFIT curve (L-R = its
  full-store end);
- SELECTIVE-proper vs LOSSLESS becomes secondary, labelled "optimizer
  confounded";
- the RESERVOIR-SELECTIVE vs RESERVOIR-RANDOM eviction arm is added;
- "saturates" is defined before the margins;
- R-c is the single grid change;
- fixtures come first.
Also agreed: the reservoir is named as an intermediate mechanism and not
forced into either category.

Two additions:
 a. DUAL MATCHING for condition 2 (the D2 lesson applied to the reservoir).
    At the same B, a selective and a random eviction policy will generally
    differ in HR2, so matched bytes is not matched rate. The directive's s4C
    says "critically, on the rate". Read RESERVOIR-SELECTIVE vs
    RESERVOIR-RANDOM twice:
      (i)  at matched B (bytes): the primary equal-bytes reading;
      (ii) at matched HR2: ladder the random reservoir's B until its HR2
           matches the selective one's, and charge the extra bytes. Use
           several random seeds per point, as in D4.
    INDISCRIMINATE_EQUIVALENT needs equivalence under BOTH readings (plus the
    positive control). A selective win at (i) that disappears at (ii) means
    "selective eviction buys bytes, not competence". That is a different
    finding, and it gets its own label.
 b. EVICTION-POLICY BUDGET. If more than one selective eviction rule is tried
    (keep worst-predicted, keep most-recent-surprising, and so on), declare
    the candidate set before dev, choose on dev seeds only, and state the
    count. The random reference has no parameters, so the selective arm's
    extra tries are a selection advantage that must be visible in the
    report. Prefer 1-2 candidates, not a sweep.

Please also put in the limitations: v1 selection data was seen before two
redesigns (R-a proposed and withdrawn after a dev probe; R-c adopted). Both
are logged with their probes, and neither used campaign seeds.
