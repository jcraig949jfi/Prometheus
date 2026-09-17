# SFE-09 -- REPRESENTATION UNLOCK (record; directive IV shape)

## A. STARTUP

- experiment ID: SFE-09
- question: is the solver's failure on a measurably stuck task partly
  imposed by representational geometry? Same problem, same VM, same
  resource accounting; the search's representation changes.
- starting commit: fdb25a749 + the descend_fn hook in archaeon/wse/
  evolve.py (25 tests pass); harness sfe09.py.
- the stuck task (evidence declared before running): W1_d4 (K=1, D=1,
  delay 4, 4-bit) -- fresh search 0/3 footholds in SFE-03 (N=200 G=60
  4-bit), 0/3 in wse-survey-v01 (N=200 G=100 8-bit), 0/3 in SSF cycle 3
  ARM 1 (N=512 G=200 4-bit).
- representations (semantics and costs identical: every child is a
  Proteus manifest the same VM executes and meters):
    A_words         Proteus's grammar over raw 32-bit words (opcode =
                    word mod 25; operand words mod n_regs; immediates raw)
    B_fields        instructions decoded to (op, a, b, c); mutation is
                    field-wise (uniform op; register index; small signed
                    delta on immediates/offsets); insert/delete/duplicate
                    at instruction granularity; crossover at instruction
                    boundaries; manifest limits stepped as the grammar
                    does; canonical re-encoding
    C_fields_class  B with opcode mutation confined to the affordance
                    class with probability 0.75
- control cell: W1_d1 (reachable) under every representation, so an
  unlock on W1_d4 is separable from a uniform speed-up.
- design: 3 representations x 2 cells x 3 seeds = 18 searches; N=200,
  G=60, E=16; IDENTICAL generation 0 for every arm (canonical sampling
  from the campaign foundry); common random numbers; held-out 48 episodes.
- services: engine v2 (one ISOLATED world; the representation descriptors
  + stuck evidence as a hypothesis-kind artifact; experiment +
  observation per arm x cell x seed).
- assay capability: A_words on W1_d1 is the positive control (v01: 2/3 at
  8-bit); A_words on W1_d4 must stay stuck (0/3) for the question to be
  posed; if B/C also stay at 0/3 on W1_d4 the outcome is NULL for the
  unlock (not INCONCLUSIVE, since the control cell shows the arms work).
- time: 18 x ~1 min on 18 procs; engine seconds.

## B. EXECUTION

- one engine attempt (RECEIPT.json, rows.json; 73.2 s: startup 0.59,
  search 67.5 on 18 procs, records 4.89, teardown 0.22; 0 errors) after a
  dry run. Engine: 1 session, 1 world, 1 hypothesis, 1 representation
  descriptor artifact (with the declared stuck evidence), 18 experiments
  + 18 observations.
- design as planned; identical generation 0 across arms (canonical
  sampling); the descend_fn hook in the loop carries the alternative
  representation; ancestry operator histograms recorded per elite.
- decisions: none new. Failures: none. Restart: n/a.

## C. SCIENCE

- primary outcomes (held-out competence, 48 episodes):
    arm / cell                s1     s2     s3     footholds  first-solved gen
    A_words / W1_d4 (stuck)   1.000  0.062  0.125  1/3        52
    B_fields / W1_d4          0.083  0.042  0.062  0/3        -
    C_fields_class / W1_d4    0.083  0.062  0.021  0/3        -
    A_words / W1_d1 (control) 0.000  0.083  0.042  0/3        -
    B_fields / W1_d1          0.083  0.062  0.042  0/3        -
    C_fields_class / W1_d1    0.104  0.062  0.042  0/3        -
  best training reward reached on W1_d4: A 1.000/0.250/0.250; B
  0.250/0.312/0.250; C 0.250/0.312/0.250.
- controls: the reachable control cell W1_d1 under every representation
  (0/3 for ALL arms, including the baseline); identical generation 0;
  common RNG.
- assay capability: FAILED. The positive control (A_words on W1_d1) did
  not reach a foothold in 3/3 seeds at N=200 G=60 4-bit (v01 reached it
  2/3 at G=100 8-bit), so "the arms work" was not shown, and the rule in
  section A ("NULL, not INCONCLUSIVE, since the control cell shows the
  arms work") does not apply: the outcome is INCONCLUSIVE.
- evidence: no unlock observed for B or C (0/6 rows) but the assay
  could not have shown one below the baseline's own reach; and the
  baseline solved the "stuck" cell once (seed 1, generation 52) --
  across four campaigns the W1_d4 baseline is now 1/12 footholds: not
  stuck, rare. The field representations reached the same 0.25-0.31
  training shelves as the words representation and no higher.
- confounders: n=3; G=60 is below the generation at which the one
  baseline success arrived (52) for two thirds of the runs' variance
  window; the field representations' mutation mix (operator histograms)
  differs from the grammar's in ways that were not matched (insert/delete
  rates), so "representation" here bundles geometry with operator mix.
- must NOT be claimed: that representation does not matter (SFE-06
  showed it does on a fixed evaluator); that W1_d4 is stuck (1/12).

## D. TEARDOWN

- 1 world TERMINATED (0.22 s); no orphans; clean for SFE-10: yes.

## E. BENCH IMPROVEMENT

BUGS: none. FRICTION: none new. MISSING TELEMETRY: L-028 ("stuck" was
declared from three prior campaigns without a pooled reachability
estimate; a per-cell reachability table -- L-017 again -- would have said
1/12 with a confidence band and sized G accordingly). AUTOMATION: the
descend_fn hook makes representations pluggable (deterministic
machinery). TO MACHINERY: operator-mix matching between representations
(L-029: the field grammar's insert/delete/op rates should be set to the
word grammar's mass so only the geometry differs). KEEP POLICY: which
representations to compare. MISSING FAILURE STATE: POSITIVE_CONTROL_
FAILED (the run should label itself INCONCLUSIVE when the control cell
is not reached by the baseline). MISSING RECOVERY: none. PORTABILITY:
none. OBSERVABILITY: none new.

## F. LANDSCAPE / GRADIENT NOTES

- The training-reward shelves (0.25, 0.3125 = 4/16, 5/16) are the same
  under every representation: the landscape's steps are the evaluator's
  (episode count granularity), not the representation's. A finer E
  (more episodes per evaluation) would resolve whether the field
  representations climb the shelf faster even when neither reaches 0.5.
- Operator histograms on the elite's ancestry (recorded) are a
  representation-specific landscape: under A the elite's lineage is
  operand_perturbation-heavy; under B/C register-field mutations
  dominate. Which operator class precedes each shelf transition is
  computable from ancestry + traces and would locate the geometry that
  matters.

DISPOSITION: INCONCLUSIVE (positive control not reached by any arm at
this budget; no unlock observed for B/C; the "stuck" premise weakened to
1/12). Instrument: 0 errors.
