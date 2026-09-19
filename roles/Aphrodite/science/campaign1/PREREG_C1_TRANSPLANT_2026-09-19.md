# Campaign 1 preregistration: TRANSMISSIBLE IMPROVEMENT (design frozen 2026-09-19)

STATUS: DESIGN FROZEN BEFORE ANY CAMPAIGN 1 DATA EXISTS. Evidence tier of
this file: 3 (design). Campaign 1 EXECUTION IS NOT AUTHORISED; it needs a
separate operator decision after the gates in s10. Authority and inputs:
the operator's relay of 2026-09-19 ("choose to adapt as you see fit";
verbatim at prompts/2026-09-19_c1_transplant/RELAY_verbatim.md); all prior
directives (charter; Campaign 0 / 0B / 0C dispositions; benchmark
directives and freeze amendment). Where this file adapts the relay, s11
says how and why.

## 1. The question

Did evolution alter REUSABLE ALGORITHMIC MACHINERY, or merely accumulate
useful state or resources? An improvement counts as algorithmic ONLY to
the extent that its competence follows a bounded, explicitly identified
artifact into a FRESH recipient after episodic history, caches,
accumulated observations, evaluator access and excess compute are
removed. "The lineage got better over time" is never an endpoint.

## 2. Parameters bound by rules already frozen (not chosen here)

- SUBSTRATE: the served variant returned by the preregistered economics
  (science/benchmark/economics.py in bundle 732dbedf...), or
  NO_ELIGIBLE_SUBSTRATE, in which case Campaign 1 does not start.
- LINEAGES: L = 64 if the decision-throughput projection of the FULL
  design (s8) fits the 30-day ceiling after the operator's resize ladder;
  otherwise L = 32 with the claims automatically narrowed to the 32-
  lineage column of s9. Never 16. delta = 3 points, never widened.
- TASKS: the four frozen procedural families (bundle), or Archaeon's
  sealed generators via a design amendment with starting accuracy
  re-qualified (operator rule).

## 3. Lineages and the world

64 (or 32) independent lineages from the same I_0 (five typed modules:
search, verify, allocate, memory, evidence; code-level mutation with the
two-phase commit), each with its own seed, 8 generations, EVALUATOR-BLIND
(the improver sees only its own scores, never the evaluator's code,
tasks or answers).
REGIME SHIFT (relay item 5): at the start of generation 5 the world's
rules change in a way that retaining the original policy cannot solve --
the task families switch to a declared shifted variant (e.g. a changed
output convention or operator semantics), specified as a fixture in the
task contract BEFORE execution. Every lineage experiences the shift.

## 4. The transplant assay (the primary instrument)

For each lineage l, artifacts are EXTRACTED at the end of generation 8:
  X_l   the evolved improvement machinery: the code of I_8's five modules
  M_l   the accumulated state: memory store, caches, archive, logs
  W_l   the evolved worker
A RECIPIENT is fresh: I_0's worker A_0, empty memory, new seed, blind
evaluator, the SAME externally enforced escrow as every other arm. Cells
per lineage, all on FRESH sealed tasks (post-shift world; plus pre-shift
for the frontier):
  SCRATCH      recipient with I_0                         (baseline)
  TRANSPLANT   recipient with X_l                          (the claim)
  MEMORY-ONLY  recipient with I_0 + M_l                    (state, not mechanism)
  SHAM         recipient with a structurally matched edit set from l's
               own REJECTED mutation archive (real edits, same modules
               and size, that selection did not keep)       (negative control)
  POSITIVE     recipient with a hand-written, known-useful module
               (a verify module that checks candidate answers against the
               task's checkable form), fixed before execution (positive control)
  EQ-COMPUTE   recipient with I_0 given one extra generation of its own
               improvement on development tasks with compute equal to
               the transplant arm's evaluation escrow      (is X_l worth more
                                                             than compute?)
  AS-RUN       the donor lineage itself with M_l, W_l and unenforced
               budget                                       (the naive score)
  MODULE SWAPS I_0 + each single module of X_l (sufficiency) and X_l minus
               each module (necessity)
Transplant-boundary receipts (Vivarium): every cell records exactly what
crossed into the recipient (file hashes) and proves the forbidden state
did not.

## 5. Endpoints and their qualification status

  CONFIRMATORY (qualified by Campaign 0 / 0B / 0C at tier 2)
  P1 TRANSPLANT vs SCRATCH on fresh sealed post-shift tasks, lineage-level,
     Holm within the confirmatory family, TOST at delta 3 -- the Campaign 0
     D_VAULT contrast. Verdict SUPERIOR / EQUIVALENT / TRIVIAL /
     INDETERMINATE; "BELOW RESOLUTION" stated when neither superiority nor
     equivalence is established.
  P2 MEMORY-ONLY vs SCRATCH (Campaign 0 D_MEM): state value.
  P3 compute: AS-RUN vs enforced, and the meter (Campaign 0 D_COMP + meter).
  P4 module necessity / sufficiency (Campaign 0 NEC/SUF): which part of X_l
     carries it -- reliable only when one module dominates (C0 finding).
  S1 SECONDARY rare transmissible discovery: Campaign 0C procedure on
     TRANSPLANT (screen on development transplants, decide and estimate on
     separate fresh sealed sets), rho_P reported with q_screen,
     q_confirm and the confirmed effect. Never alters P1.

  EXPLORATORY (NOT qualified; reported with intervals; no confirmatory
  claim, no pass/fail)
  E1 SHAM and POSITIVE vs SCRATCH (the controls' own behaviour; a POSITIVE
     arm that does not beat SCRATCH invalidates the run's sensitivity --
     see s7)
  E2 EQ-COMPUTE vs TRANSPLANT
  E3 CROSS-LINEAGE: lineages randomly paired (32 disjoint pairs at L = 64);
     X_A into B's evolved agent (B's worker and state) vs B alone, and
     the reverse; co-adaptation index = own-lineage transplant gain minus
     cross-lineage gain; the pair is the unit
  E4 REGIME SHIFT: per lineage, generations to recover the pre-shift
     score, which module(s) changed at the shift (code diff), a CAPABILITY
     LADDER label from logged behaviour -- reflex (no change after the
     shift), detector (the evidence module registers the shift without a
     policy change), switch (policy changes after the shift), persistent
     state (the change is retained across later episodes), predictive
     (behaviour changes before the shift is observed; reserved, expected
     rare) -- and SHIFT-TRANSPLANT: X_l taken at the end of generation 4
     vs 8 into a fresh recipient on the shifted world
  E5 ARTIFACT SEARCH (relay: "search broadly over what the transferable
     artifact can be"): candidate artifacts per lineage = each single
     module, each module pair, X_l, M_l, and any bounded diff the lineage
     itself declares; screened on development transplants, confirmed on
     fresh sealed tasks, estimated on a further set (the 0C structure),
     Holm across all screened (lineage, artifact) pairs
  E6 EVALUATOR-VISIBLE ARM: 16 additional lineages evolved with the
     evaluator visible, ONLY if the 30-day budget admits them after
     everything above (s8); exploit indicators and P1-style transplant
     compared descriptively with the blind lineages

## 6. What would count as what (fixed now)

- TRANSMISSIBLE MECHANISM: P1 SUPERIOR, P2 not SUPERIOR or smaller than
  P1, P3 clean, E1 POSITIVE detected and SHAM null. Strengthened (not
  required) by E3 cross-lineage transfer and E5 identifying a bounded
  artifact.
- ACCUMULATED STATE: P2 SUPERIOR while P1 EQUIVALENT or BELOW RESOLUTION.
- COMPUTE: advantage only in AS-RUN, vanishing under enforced escrow.
- CO-ADAPTATION (exploratory): own-lineage transplant gain clearly above
  cross-lineage gain.
- NULL, stated narrowly: under this substrate, task distribution,
  mutation language, compute regime and horizon, evolution produced no
  detectable transmissible improvement larger than the resolution floor.

## 7. Validity conditions (a run failing one is reported, not interpreted)

- POSITIVE arm must beat SCRATCH (P1-style test at alpha 0.05): otherwise
  the pipeline could not have seen a transmissible improvement -> the run
  is INSENSITIVE, and nulls are uninterpretable.
- SHAM must not beat SCRATCH beyond delta: otherwise transplantation
  itself (not the mechanism) changes performance -> the run is
  CONFOUNDED for P1.
- Harmonia's cheat fixtures and Vivarium's reset/boundary fixtures (s10)
  must all be caught in a pre-run check on the production path.
- Any lineage with an unmetered call, escrow breach or forbidden-state
  crossing is FLAGGED; all results are reported with and without flagged
  lineages (kill/resize rule K4).

## 8. Compute priority (for the 30-day resize ladder)

If the full design does not fit, arms are removed in this order before
the operator's ladder reaches "reduce lineages": E6 first, then E5's pair
candidates, then E4's SHIFT-TRANSPLANT, then E3, then E2. SCRATCH,
TRANSPLANT, MEMORY-ONLY, SHAM, POSITIVE, AS-RUN, enforced escrow and the
module swaps are never removed (they define P1-P4 and validity).

## 9. Claims supported (from the qualification; tier 2 basis)

At L = 64: P1-P4 as qualified by Campaign 0 (floor ~4.7 points;
specialisation fragile; single-module attribution only); S1 as qualified
by 0C (10-20% prevalence with +24 to +42-point discoveries; not 1-2%,
not +11 points, not family-specialised). At L = 32: P1 (floor ~7.1), P2,
single-module P4, S1 at 20% prevalence; no specialisation, mixed-cause or
EQUIVALENT claims (reported as BELOW RESOLUTION). All E-endpoints at
either L: exploratory only.

## 10. Gates before any execution (unchanged plus relay item 6)

1. Substrate closed by the mechanical economics (benchmark receipts from
   Nestor / M1 and Archaeon / M2; the >= 5-point anomaly rule
   investigated if it fires). 2. Archaeon: sealed task-generator contract
   INCLUDING the regime-shift fixture. 3. Harmonia: HOSTILE adjudication
   contract whose cheat fixtures (memory leakage into a recipient,
   evaluator exploitation, increased token/compute budget, task
   memorisation, lineage-ID shortcuts) are caught. 4. Vivarium: HOSTILE
   execution contract -- resets proven to destroy forbidden state, and a
   receipt per transplant cell proving exactly what crossed the boundary.
   5. The POSITIVE-arm module committed and hashed. 6. Operator review and
   authorisation.

## 11. Adaptations of the relay (the seat's choices, stated)

- Cross-lineage transplantation, regime-shift adaptation and the artifact
  search are EXPLORATORY here: none has been qualified by a planted-truth
  calibration, and the operator ruled against adding synthetic worlds
  without a concrete need. Promoting any of them to confirmatory status
  requires its own qualification first.
- "Equal-compute retraining" is operationalised as one extra generation
  of the recipient's own improvement at the transplant arm's escrow; a
  larger equal-compute arm would compete with the primary for budget.
- "Evaluator-visible vs evaluator-blind": all primary lineages are blind
  (DGM reported more hacking when checkers were visible); a visible arm is
  the first thing removed under compute pressure.
- The transplant core is the Campaign 0 assay renamed: P1 = D_VAULT with
  the transplanted object named as I_8's code, so the primary endpoint
  keeps its qualification.
