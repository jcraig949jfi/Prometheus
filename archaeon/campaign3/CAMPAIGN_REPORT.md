+=====================================================================+
|  ARCHAEON -- SFE AUTONOMOUS CAMPAIGN 3 -- FINAL REPORT               |
|  Workspace / Serendipity Ecology (WSE), Proteus organisms            |
|  Author: Archaeon (seat m2-411504ab, machine M2 / SPECTREX5)         |
|  Date:   2026-09-17                                                  |
|  For:    HITL (James) + external reviewers                           |
|  Status: CLOSED -- ten science slots attempted, all ten reported     |
|  Self-contained: every load-bearing number is inline. No repo        |
|  access is needed to read or attack this document.                   |
+=====================================================================+

-----------------------------------------------------------------------
0. SUMMARY AND VERDICT
-----------------------------------------------------------------------

Campaign 3's instruction was "DO NOT IMPROVE THE STORY. IMPROVE THE
MACHINE." Ten discriminating experiments were preregistered, run and
reported. Seven returned CAPABLE_NEGATIVE, two WEAK_POSITIVE, one
INCONCLUSIVE. Zero engine errors on every attempt of record. Two slots
failed their own positive control on first execution, were repaired at
the machine level and re-preregistered before re-running.

The five results that matter:

  1. NO K=2 POPULATION REACHED THE SUMMIT. Zero confirmed summits in
     24 runs of 300 generations on W2_K2 (C3-SFE-01), zero in 54 K=2
     runs across the corridor map (C3-SFE-04), zero under an
     all-or-nothing payoff (C3-SFE-08). The cell's ceiling is not a
     budget effect, not a reward-shaping artefact and not reachable by
     initialization from any mature source tested.

  2. THE SHELF IS A ONE-VALUE MEMORY AND PARTIAL CREDIT BUILDS IT.
     Shelf organisms answer every ask with one remembered PUT value
     (C3-SFE-02). Removing partial credit cuts shelf arrivals from
     11/12 to 8/12 and produces a different organism -- five runs whose
     held-out EPISODE credit equals their per-ask credit, i.e. they
     answer both asks or neither -- and still reaches no summit
     (C3-SFE-08). The payoff selects the plateau and the creature; it
     does not set the ceiling.

  3. THE DELAY LADDER BUILDS DELAY INVARIANCE. 11 of 12 seeds become
     general on delays 0/1/2/4 (held-out 1.0), and all 11 read delays
     8 and 16 -- never trained -- at held-out 1.0, while matched-budget
     direct search reaches d8 in 0/6 runs and d16 in 1/6. Mature W0
     solvers score 0.0 on both, so the invariance is the ladder's
     product, not W0 competence (C3-SFE-03, C3-SFE-04).

  4. IMPORT TAKEOVER IS MECHANICS, NOT CAPABILITY. Mature solvers and
     opcode-permuted incompetent controls take over equally (12/12 vs
     12/12 at dose 4, no cap) while a no-import arm never does (0/12).
     One organism in 200 suffices. Only the offspring cap moves the
     clock (C3-SFE-10).

  5. TWO GEOMETRY CLAIMS DIED. Basin share's apparent out-of-family
     replication (pooled rho -0.568) is a two-strata artefact
     (C3-SFE-06), and using it to steer a real evolutionary run changes
     nothing beyond ordering noise (C3-SFE-07). The CA "localized
     delayed recall" is equally localized in a hand-designed rule that
     never evolved for the task, fits neither named mechanism class,
     and largely survives permuting the reset lattice (C3-SFE-09).

VERDICT: the machine is materially better than campaign 2's and the
scientific news is mostly negative, which is the correct outcome for a
campaign that spent its budget on discrimination rather than
confirmation. Three of the ten slots produced findings that constrain
campaign 4's design; four killed lines outright.

-----------------------------------------------------------------------
1. WHAT DID WE RETIRE?
-----------------------------------------------------------------------

Retired BEFORE execution, per the directive, and confirmed not
reopened: fragment / organ / whole-genotype failed-material transfer;
half-battery episode transport; opcode-neighbourhood representation
unlocks; cap-32 retention comparisons. Retired lines accidentally
reopened: 0.

Retired DURING campaign 3 by its own evidence:

  - C3-SFE-08 as originally specified (wall-clock producer-consumer
    under a FULL-solve criterion). Its outcome variable does not exist:
    C3-SFE-01 found no full-solve regime. Replaced before execution
    (D3-013).
  - Basin geometry as a design variable (C3-SFE-06 + C3-SFE-07).
  - The CA delayed-recall mechanism line as a "computation" claim
    (C3-SFE-09): the effect survives as an executable hypothesis about
    a position-keyed reset readout, not as computation.
  - "Summit by reward shaping" on W2_K2 (C3-SFE-08).

-----------------------------------------------------------------------
2. WHAT DID WE REPLACE IT WITH?
-----------------------------------------------------------------------

C3-SFE-08 became PARTIAL-CREDIT REMOVAL: does the half-credit readout
build the shelf? It required a real machine change (all-or-nothing
episode credit in the evaluator and the evolution loop, both readouts
reported on every evaluation) and it answered its question: partial
credit builds the shelf, and the ceiling is elsewhere.

-----------------------------------------------------------------------
3. DID ANY K=2 POPULATION REACH THE SUMMIT?
-----------------------------------------------------------------------

No. Not once, under any condition tested.

  W2_K2, fresh, G300, n=12               0 summits, 0 candidates
  W2_K2, preserved shelf start, G300     0 summits (import share 1.0)
  W2_K2, all-or-nothing credit, G300     0 summits
  W2_K2 / W3_K2 / W7_K2, corridor map    0 summits in 54 runs
  Best training excursions               0.875 (28/32 asks), held-out 0.60

The reachability table now classes the W2_K2 summit OBSERVED_UNREACHABLE
AT BUDGET at every ladder point through G300 (95% upper band 0.22 at
n=14 baseline runs; below 0.13 including treated runs).

-----------------------------------------------------------------------
4. WHAT IS THE SHELF-TO-SUMMIT GEOMETRY?
-----------------------------------------------------------------------

Measured directly (C3-SFE-02, 12 shelf elites, 400 grammar children
each, 4,800 children total):

  useful children                     1 in 4,800
  neutral / destructive               0.64 / 0.36
  second-stream gains                 58 children
  second-stream gains keeping the
    first stream                      0 of 58
  greedy 3-step paths reaching 0.90   0 of 480
  strategy                            first-PUT value 6/12,
                                      last-PUT value 4/12, mixed 2/12

The shelf is a one-value memory paying ~0.5 because half the asks
concern the remembered stream. Every single edit that raises the other
stream's credit does so by switching WHICH value is remembered, losing
the credit it had. The summit needs a two-value keyed memory that the
one-step and three-step neighbourhoods do not contain.

C3-SFE-08 adds the causal half: under all-or-nothing credit the search
does build two-value organisms (held-out episode credit equal to
per-ask credit, 0.438-0.646, in 5 of 12 runs) but tops out around 0.65
against the 0.90 the summit requires.

-----------------------------------------------------------------------
5. WHERE DOES DELAY GENERALITY APPEAR?
-----------------------------------------------------------------------

At the delay-1 rung, abruptly, once (C3-SFE-03, n=12, rung 0 held until
climbed):

  delay-general (all rungs >= 0.75,
    held-out 1.0 on d0/1/2/4)         11 of 12 seeds
  rung at which it appears            rung 1 in 7, rung 2 in 3, rung 0 in 1
  generations after the hold          10-50 (median 35)
  R3 competence appears abruptly      8 of 11 (one probe interval)
  adaptation cost to d2 and d4        0 generations in 11 of 11
  already-general organism promoted
    at the first delay-1 battery      5 of 12 seeds

Two readings follow. The corridor is W0 -> delay 1 and then free: rungs
d2 and d4 add nothing. And part of the corridor's work is SELECTION
among variation the W0 population already contained, not construction.

-----------------------------------------------------------------------
6. WHAT CORRIDORS WERE DISCOVERED?
-----------------------------------------------------------------------

The corridor table holds 155 rows, 82 from campaign 3. Four edge types
were separated (C3-SFE-04; mature sources only, direct probes first):

  FREE            delay_general -> W1_d8, W1_d16: direct held-out 1.0
                  in 11/11 sources. Matched direct search: 0/6 and 1/6.
  HALF FREE       delay_general -> W2_K2 (0.54), W3_K2 (0.58): the
                  half-credit shelf arrives at generation 0 and no arm
                  reaches a summit.
  TIME ADVANTAGE  delay_general -> W7_K2 (direct 0.15, nothing
                  inherited): median foothold generation 20 against the
                  baseline's 82; the permuted control is WORSE than no
                  import (2/6, median 95).
  NO CORRIDOR     W0_solver -> the delay family: direct 0.00 at d8/d16.

Reachability classes corrected by budget in the same run: W7_K2
REACHABLE at G100 (4/6 to the shelf) after OBSERVED_UNREACHABLE at G60;
W1_d8 OBSERVED_UNREACHABLE (0/6) and W1_d16 RARE (1/6), both previously
UNESTABLISHED.

-----------------------------------------------------------------------
7. WHAT IS THE RETENTION BREAK-EVEN?
-----------------------------------------------------------------------

Above 0.05 and at most 0.10 (C3-SFE-05, n=12 per arm):

  revisit share p          0      0.05    0.10    0.20
  mean final rung-0        0.764  0.892   1.000   1.000
  runs below 0.75          3/12   2/12    0/12    0/12
  revisit episodes/run     0      75      150     225
  adaptation cost          0 generations in 57 of 58 general runs

And the price stops at generality. The p0.10-then-0 arm drops revisits
the moment the elite is general: rung-0 retention 1.0 in 12/12, the
same 11/12 generality at the same generations, for a MEDIAN of 22
revisit episodes instead of 150. Retention is a transient pressure, not
a standing tax.

Caveat recorded: the forgetting cliff fires in a MINORITY of seeds
(3/12 at p=0), which is why campaign 2's n=6 could neither price nor
bound it.

-----------------------------------------------------------------------
8. DID BASIN SHARE GENERALIZE?
-----------------------------------------------------------------------

No, and the way it failed is the finding (C3-SFE-06, INCONCLUSIVE).

The preregistered pooled primary returns Spearman rho = -0.568 over 48
rows, which would have replicated campaign 2's -0.59 almost exactly. It
is a TWO-POINT correlation: the two score tables differ 13x in basin
share (0.026-0.034 vs 0.410-0.435) and an order of magnitude in
difficulty, so pooling them produces a strong negative by construction.

  within skelA, first-improvement climber    rho = -0.527
  within skelA, population climber           rho = +0.187
  within skelB, first-improvement            rho = -0.042
  within skelB, population                   undefined (all hit at
                                             evaluation 1)

One of four cells replicates. Two cannot express the measurement at all
because skelB's adaptive target fell at the 1/16 chance level.

-----------------------------------------------------------------------
9. DID MANIPULATING BASIN/DECEPTION GEOMETRY PREDICT SEARCH?
-----------------------------------------------------------------------

No (C3-SFE-07, CAPABLE_NEGATIVE). With task, operator masses (max
deviation 0.008), budget and generation 0 fixed, and only the opcode
neighbourhood rewritten:

  arm            grammar  high basin  low basin  rand A  rand B
  confirmed      8/12     8/12        9/12       7/12    8/12
  median gen     21       24          25         15      13
  basin share    --       0.0338      0.0256     0.0305  0.0305

Effect -0.083, wrong direction, against a declared +0.25. Two RANDOM
orderings matched on basin share differ by the same 0.083, so the
preregistered kill condition fires: the contrast is ordering noise. The
intervention did apply (567-573 opcode rewrites per treated run).

-----------------------------------------------------------------------
10. DID PRODUCER-CONSUMER ECONOMICS SURVIVE A FULL-SOLVE CRITERION?
-----------------------------------------------------------------------

The question could not be posed. A full-solve regime does not exist on
the cell it would have used: 0 summits in 24 runs of 300 generations.
The slot was replaced before execution rather than run on a criterion
its own parent evidence had already voided (D3-013). Campaign 2's
wall-clock producer-consumer result (+0.109, WEAK, 0/24 full solves)
therefore stands unreplicated and unextended, and is listed under
CONDITIONAL below.

-----------------------------------------------------------------------
11. WHAT CA MECHANISM SURVIVED INTERVENTION?
-----------------------------------------------------------------------

None of the named ones (C3-SFE-09, n=8 seeds x 3 genomes).

  single site carries, particle2      0.56-1.68 of the margin
  single site carries, GKL            0.45-1.39 of the margin
  primary (particle2 - GKL)           0.966 vs 0.976, effect -0.011
  local storage flag                  0 of 8
  routing flag                        2 of 8
  site clamped one step earlier       removes 0.000-0.034
  neighbourhood clamped one step
    earlier                           removes 0.000-0.086
  site-alone readout, true reset      0.486-0.629
  site-alone readout, PERMUTED reset  0.530-0.573 (as good in 5 of 8)

Campaign 2's localization replicates exactly and turns out to be
uninformative: a hand-designed rule never selected for delayed recall
is just as localized. Nothing measurable arrives at the responsible
site one step before it matters, which rules out both preregistered
classes. What survives is an executable hypothesis a later run can
falsify: particle2's d=2 margin requires no information transport and
should be reproducible by a position-keyed reset readout alone.

-----------------------------------------------------------------------
12. WHAT IMPORT DOSE BECOMES TAKEOVER?
-----------------------------------------------------------------------

Any dose (C3-SFE-10, 228 runs). At N=200 with tournament 4 and elitism
4:

  arm (no cap)          takeover   median takeover generation
  no import             0/12       --
  mature dose 1         12/12      4.5
  mature dose 4         12/12      3
  mature dose 32        12/12      2
  control dose 1        11/12      8
  control dose 4        12/12      6
  control dose 32       12/12      3.5

The permuted controls are incompetent by construction (direct held-out
0.0-0.125 against the mature sources' 1.0) and take over anyway. Dose
sets speed, not outcome. The offspring cap is the only control
parameter: at 0.05 takeover slips to generations 15-22 (mature) and
26-57 (control) and is the only setting leaving any pure-resident
lineage alive at generation 60 (5-6 of 12 control runs). Nothing tested
prevents takeover. Origin takeover is NOT clonal collapse: distinct
genomes stay at 0.78-0.99 throughout.

-----------------------------------------------------------------------
13. WHAT DECISIONS MOVED INTO DETERMINISTIC MACHINERY?
-----------------------------------------------------------------------

Phase A (built and tested before any science ran): three reach levels
with held-out-confirmed summits; right-censoring of stopped runs;
monotone budget lookup; the corridor table; dense transition probes;
the injection cap and per-ask credit; per-campaign parametrization of
the shared machine. 5 groups IMPLEMENTED_AND_TESTED, 1 PARTIAL.

Phase B (forced by the science, each with its ledger entry):

  B1  ladder.rung0_max -- hold rung 0 until the population climbs it,
      then run the fixed schedule (L3-011). A fixed first rung released
      the ladder before W0 was climbed in 7 of 12 seeds.
  B2  evaluate(reward_mode) / Evolution(reward_mode) -- all-or-nothing
      episode credit; both readouts returned on every evaluation.
  B3  matched permuted-block controls for every import experiment
      (D3-014).
  B4  publish-then-fetch instead of self-import (an ISOLATED world
      cannot import from itself; L3-015).
  B5  per-table data-derived search thresholds (D3-021), with the
      chance-level defect recorded (L3-030).
  B6  states.disposition_candidate skips rows lacking the primary
      metric instead of crashing, and never reads a missing
      measurement as zero (L3-039).

Ledger: 41 entries (12 LANDSCAPE, 12 RECOVERY, 7 BUG, 5 ASSAY_STATE, 3
MISSING_TELEMETRY, 1 REPLACEMENT, 1 TO_MACHINERY). Three block future
runs until honoured: L3-016 (cap or declare replacement), L3-029
(stratified rank correlations), L3-039 (fixed).

-----------------------------------------------------------------------
14. WHAT SHOULD NEVER BE RUN AGAIN?
-----------------------------------------------------------------------

  - Any W2_K2 summit attempt that changes only the budget or the
    payoff. Three independent attempts, 0 of 60 runs.
  - Basin share (or deceptive share) as a knob to steer search.
  - Localization claims without a non-evolved comparison rule measured
    the same way.
  - Frozen-readout margins without a permuted-structure control.
  - Pooled rank correlations over strata of different difficulty.
  - Injection experiments without a cap and without reporting realized
    origin shares.
  - The four lines retired before the campaign began.

-----------------------------------------------------------------------
15. CAMPAIGN ACCOUNTING
-----------------------------------------------------------------------

Per slot (machine disposition = recorded disposition except where
noted):

  slot  ancestry     n    disp              atts  pc     engine
  01    original     24   CAPABLE_NEGATIVE  2     n/a    clean
  02    original     18   CAPABLE_NEGATIVE  3     n/a    clean
  03    original     12   WEAK_POSITIVE     5     pass*  clean
  04    replacement  66   WEAK_POSITIVE     3     n/a    clean
  05    original     60   CAPABLE_NEGATIVE  3     pass   clean
  06    original     48   INCONCLUSIVE**    5     pass*  clean
  07    replacement  60   CAPABLE_NEGATIVE  2     pass   clean
  08    replacement  24   CAPABLE_NEGATIVE  2     pass   clean
  09    original     24   CAPABLE_NEGATIVE  2     n/a    clean
  10    replacement  228  CAPABLE_NEGATIVE  2     pass   clean

  *  passed only after a machine repair and re-preregistration; the
     first engine attempt was POSITIVE_CONTROL_FAILED (slots 03, 06).
  ** machine candidate WEAK_POSITIVE; recorded INCONCLUSIVE because the
     preregistered primary is confounded. This is the only slot where
     the agent's disposition is stricter than the machine's.

Campaign totals:

  science slots attempted / 10             10 / 10
  original planned experiments run          6
  planned experiments replaced              4 (three before campaign 3
                                            began, one -- slot 08 --
                                            during it, D3-013)
  capable assays                           10 / 10 (two after repair)
  summit outcomes                           0
  shelf outcomes                           W2_K2 11/12 fresh; the
                                           corridor delivers the shelf
                                           at generation 0
  floor-only outcomes                      C3-SFE-10 no-import arm
                                           (0/12), 4/12 episode-credit
                                           runs, W1_d8 baseline 0/6
  capable negatives                         7
  weak positives                            2
  stronger supported results                0
  inconclusive                              1
  claims killed                             4 (basin as a knob; basin's
                                           out-of-family replication;
                                           CA localization as a
                                           mechanism signature; summit
                                           by reward shaping)
  mechanisms localized                      1, and shown uninformative
  corridor edges discovered                 82 new rows, 4 edge types
  deterministic machinery changes           6 Phase-A groups + 6 Phase-B
  recurring defects                         1 pattern, twice: an
                                           instrument gated on a fixed
                                           constant rather than on the
                                           measured state of its own
                                           space (slots 03 and 06)
  full recreations                          0
  successful resumes                        1 (slot 09 a04 replayed 29
                                           verified steps)
  engine errors on attempts of record       0
  retired lines accidentally reopened       0

Wall clock, attempts of record: 6.1 hours of compute across ten slots
(largest: C3-SFE-10 at 1512 s, C3-SFE-01 at 1235 s, C3-SFE-04 at 919 s,
C3-SFE-08 at 906 s). Reachability table 1,265 rows (486 from campaign
3); corridor table 155 rows (82 from campaign 3).

-----------------------------------------------------------------------
16. WHAT THIS DOES AND DOES NOT ESTABLISH
-----------------------------------------------------------------------

Establishes, at the stated n and budgets: the W2_K2 summit is
unreachable by this organism/search/payoff system through 300
generations; the delay ladder produces delay-invariant readers; the
retention break-even and its transient schedule; that import takeover
is mechanics; that basin share is not causal here; that the CA
localization is not distinctive.

Does NOT establish: that any of these are properties of the WSE in
general (one grammar, one VM, N=200, E=16); that the summit is
impossible (bands, not proofs); that initialization beats direct search
in general (the pooled corridor effect is dominated by inherited
competence); that basin share is refuted as a descriptive statistic.

Two claims in this report rest on n=6: the W7_K2 time advantage and the
matched-budget delay-cell comparators. Both are labelled WEAK.

-----------------------------------------------------------------------
17. EXACT RECOMMENDATIONS FOR CAMPAIGN 4
-----------------------------------------------------------------------

The test applied: does another DISCRIMINATING experiment remain?

CONTINUE

  C4-1  THE DELAY-INVARIANT READER. What is it? The ladder reliably
        produces organisms that read arbitrary delays, including d8 and
        d16 they never saw, and matched direct search almost never
        finds one. Anatomise it the way C3-SFE-02 anatomised the shelf:
        genotype, minimum lesion, and whether the invariance is one
        instruction or a program shape. This is the campaign's only
        reproducible positive capability and it is unexplained.

  C4-2  SELECTION VERSUS CONSTRUCTION IN THE CORRIDOR. In 5 of 12
        seeds the first delay-1 battery promoted an organism the W0
        population ALREADY contained. Probe the whole population, not
        the elite, at each transition: what fraction is already
        general, and does the ladder mostly select or mostly build?
        A discriminating design exists (population-level rung probes,
        already specified in L3-020's telemetry note).

  C4-3  W2_K2 BY CHANGING THE ORGANISM OR THE SEARCH. Budget, payoff
        and initialization are all exhausted. What remains
        discriminating: a register/addressing primitive the grammar
        lacks, or a search operator that can cross the two-value
        valley (campaign 2 showed crossover crosses valleys single-step
        mutation cannot). State the mechanism first, then test it.

  C4-4  THE INJECTION CAP AS AN ECOLOGY. C3-SFE-10 found the cap is
        the only lever and that no tested setting preserves residents.
        The discriminating question is whether a cap plus a protected
        resident niche keeps both lineages alive AND lets imported
        capability spread -- the condition every future transfer
        experiment silently assumes.

CONDITIONAL

  C4-5  PRODUCER-CONSUMER WALL-CLOCK. Run ONLY on a cell with a
        demonstrated full-solve regime. W1_d4 via the ladder now
        qualifies (11/12 general, held-out 1.0). Condition: the
        producer's product must be maturity-gated and the consumer's
        criterion must be full solve, as originally specified.

  C4-6  RETENTION AT A FINER GRID. Condition: only if a campaign-4
        curriculum actually pays a retention cost. The break-even is
        bracketed to (0.05, 0.10] and the then-0 schedule makes the
        cost small; a finer grid is only worth it if some experiment
        depends on the exact value.

  C4-7  THE CA POSITION-KEYED RESET HYPOTHESIS. Condition: cheap, and
        only as a falsification. Reproduce particle2's margin with a
        readout over the reset lattice alone. If it reproduces, the CA
        line closes permanently; if it does not, the mechanism is
        somewhere the lesion probes did not look.

STOP

  C4-8  BASIN / DECEPTION GEOMETRY AS A DESIGN VARIABLE. Two
        independent attacks, both negative, one of them a direct causal
        intervention with a matched-noise control. No discriminating
        experiment remains at this scale.

  C4-9  W2_K2 SUMMIT BY BUDGET OR PAYOFF. Three attempts, 0 of 60
        runs. Not a sample-size question.

  C4-10 CA DELAYED RECALL AS AN EVOLVED COMPUTATION. Superseded by
        C4-7's falsification; there is no remaining discriminating
        version of the original claim.

  C4-11 THE FOUR PRE-RETIRED TRANSFER LINES. Still retired. Campaign 3
        gives no reason to reopen any of them, and C3-SFE-10 explains
        why their apparent effects looked real: injection mechanics
        move populations regardless of what is injected.

+=====================================================================+
|  END. A reviewer who concludes "not worth continuing" is giving a    |
|  first-class answer, and this report is written to make that         |
|  conclusion reachable: seven of ten slots returned negatives, and    |
|  the campaign's single reproducible positive capability (the         |
|  delay-invariant reader) is still unexplained.                       |
+=====================================================================+
