+=====================================================================+
|  DEEP FRONTIER -- OPERATING CHARTER v0.1 (preregistered before any    |
|  live run; live execution begins only after G6-0 closes)             |
|  Archaeon[m2-49ee5a4d]   2026-09-18                                  |
|  Directive verbatim: roles/Archaeon/prompts/2026-09-18_deep_frontier/ |
+=====================================================================+

0. WHAT EXISTS NOW (BEGIN 1-5, executed; nothing evaluated)
-----------------------------------------------------------------------
  registry   archaeon/frontier/registry/{LINEAGES,EVENTS}.jsonl -- append-
             only; a lineage record carries every field of directive s6;
             interpretations are a separate field with their own status
             (PROVISIONAL | OVERTURNED | SURVIVING) and never ground truth.
  queues     archaeon/frontier/queues/{EXPLORATION,EXPLOITATION,AUDIT,
             REVISIT}.jsonl; items name a lineage + one transformation +
             a lane label + a budget.
  allocation ALLOCATION_RULES_frozen.json (s3 below).
  ingest     12 seed lineages, 77 transformations (49 breadth, 8 depth,
             12 audit/blind-spot, 8 revisit): the unresolved observations
             of C4 (cliff; exaptation vs yield), C5 (flat elite; opcode
             vs register fault asymmetry; hidden load under FIZZLE), C6
             (population-churn blind spot; six UNABLE rulers; escalation
             volume; the five novelty misses), plus three breadth seeds
             (a 40-world procedural scatter with seeds 10000-10039
             reserved; the world-generator mutation lineage; the
             machinery-demanding pressure lineage).
  first frontier  PREPARED, NOT EXECUTED: the 77 pending transformations
             with their budgets (2.5e6 evaluations if all ran, well over
             the first epoch; the queues decide order, the allocation
             decides pool shares).

1. CORE LOOP (s1) as it will run
-----------------------------------------------------------------------
  GENERATE  pop the next item per pool share; turn its transformation
            into a segment spec (world record + schedule record +
            profile + population provenance + frozen detector table)
            with a sealed prereg-of-record; the lane label is the
            generator's, never the executor's.
  EXECUTE   run_segment through Vivarium's segment kind (checkpoint in/
            out, replay A available for every segment).
  OBSERVE   the admitted detectors; raw T0 rows kept regardless of what
            fired; UNABLE recorded.
  FREEZE    s5 tiers until Harmonia's policy supersedes.
  BRANCH    every firing, disagreement, classifier failure, weak
            persistent signal, unusual survival/transfer/robustness/
            fragility, forensic nomination or random audit sample may
            create descendants along the eighteen dims of s1; a
            descendant is a transformation added to the lineage's
            frontier, never a new unrelated run.
  COMPARE   before any interpretation is marked SURVIVING: replay A;
            at least one of B-G in a descendant; a seed control; an
            initialization control; a budget control where the claim is
            about efficiency.
  RETURN    registry events feed the next epoch's allocation (s3) and
            the candidate distribution (breadth seeds move toward
            regions where lineages branched; anti-collapse pulls them
            back, s7).

2. DEPTH RULE AND RETIREMENT (s2)
-----------------------------------------------------------------------
  A lineage is never retired for a failed first transformation. A
  negative result marks the transformation FAILED and narrows the
  frontier (the failed dims are recorded); the lineage stays OPEN while
  any transformation is PENDING or any branch rule (s1) can add one.
  Retirement requires one of A-E recorded with evidence AND a reopen
  condition; C uses the preregistered relevance floor: the effect
  bounded within +-1/16 on the lineage's primary observable by >= 3
  independent controlled descendants. Reopen is always available and
  is an event, not a new lineage.

3. ALLOCATION (s10; ALLOCATION_RULES_frozen.json)
-----------------------------------------------------------------------
  initial EXPLORATION .40 / EXPLOITATION .40 / AUDIT .20; floors .20 and
  .15, ceiling .60; epoch = 1e5 evaluations or 24 h; yield counted from
  registry events (corroborated events, new phenomenon families, blind
  spots with a new positive control, interpretations overturned,
  retirements with reopen); multiplicative +-25% step, max .10 move per
  epoch; AUDIT never rewarded for findings; anti-collapse: one lineage
  above .50 of EXPLOITATION for two epochs raises EXPLORATION by .10 and
  pushes a distant reopen (bin >= 7, unused seeds, unlabeled schedule).
  REVISIT items are charged to AUDIT.

4. TWO MODES (s3) AND THE BLIND-SPOT PROGRAM (s8)
-----------------------------------------------------------------------
  BREADTH runs on the PROCEDURAL lane by default (worlds, schedules and
  seeds from reserved ranges; LLMs inspect afterward). DEPTH alters
  dims across widening ranges (each descendant records from -> to).
  BLIND_SPOT lineages (C6-blind, C6-unable) exist to find regimes where
  UNABLE or weak detectors acquire positive controls; a threshold change
  happens only inside a recorded CALIBRATION EPOCH (a registry event
  naming the detector, the old and new table digests, and the controls),
  never against a discovery.

5. FREEZE ECONOMICS (s9) until Harmonia's policy is issued
-----------------------------------------------------------------------
  EVENT_RECORD   always: the verdict vector, the subject's T0 row and
                 the +-16-generation neighbourhood reference (archive
                 policy already keeps those rows); never discarded.
  PARTIAL        checkpoint + local provenance (subject, parent, mutation
                 chain, pressure window) when only detectors 10/11 fire,
                 or only an UNVALIDATED ruler fires.
  FULL           the nine-member forensic package when an ADMITTED
                 detector fires, or two independent rulers corroborate,
                 or the signal persists over >= 3 archived generations,
                 or the magnitude is exceptional (top 1% of the lineage's
                 scores), or the AUDIT pool draws it by controlled
                 sampling (1 in 50 event records at random).
  Campaign 6's G6-0 keeps its own policy (every firing full) until
  Harmonia rules; the frontier runs tiered from its first live segment.

6. RHYTHM, ESCALATION, DIGESTS (s12, s13)
-----------------------------------------------------------------------
  Autonomous: generate -> preregister -> execute -> inspect -> branch ->
  execute. Escalate to the operator only for a charter change, an
  evidence-integrity rule change, a destructive schema change, a
  compute-envelope increase, overriding Harmonia, disabling controls, or
  treating an interpretation as ground truth. Receipts are continuous
  (registry events, queue states, per-segment outputs). A human digest
  is produced on any s13 trigger and on a schedule of one per 7 days,
  and emphasises discoveries, contradictions, surviving mysteries and
  newly opened space, never volume.

7. ANTI-COLLAPSE AND SERENDIPITY (s7, s15)
-----------------------------------------------------------------------
  The fourteen branch triggers of s7 are all wired to the registry as
  event kinds; a random audit sample (1 in 50 ordinary segments) opens a
  branch with no reason recorded but the draw. Concentration is measured
  per epoch as the share of evaluations spent on descendants of the top
  lineage; above .50 for two epochs the distant reopen fires (s3).
  UNKNOWN_MECHANISM is a permitted and expected lineage state.

8. WHAT THIS CHARTER DOES NOT DO
-----------------------------------------------------------------------
  It does not name a phenomenon to find; it does not freeze the ten-
  feature world ontology (B-worldgen mutates the generator with recorded
  specs and seeds); it does not run before G6-0; it does not touch the
  Campaign 6 detector thresholds outside a calibration epoch; it does
  not decide the freeze policy Harmonia owns.
+=====================================================================+
