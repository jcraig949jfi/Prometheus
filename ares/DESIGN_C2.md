# DESIGN_C2 -- Ares cycle 2: ATTACK THE MECHANISM (preregistered)

Currency: 2026-09-23. Operator directive verbatim at
roles/Ares/prompts/2026-09-23_cycle2_directive/ (MANIFEST beside it).
Committed BEFORE any cycle-2 GA run. One round only; the stopping rule
in s8 is the operator's and is harsher than cycle 1's. Post-result
changes go in a dated ADDENDUM, never the body.

## 0. The corrected claim this cycle starts from

Cycle 1 must NOT be reported as "a mechanism no human conceived".
Recurrent state as memory is textbook. The correct and narrower claim,
which is what this cycle interrogates:

    In this substrate, a carrier the experimenter did NOT designate
    (recurrence: an edge a node can grow back to itself or around a
    cycle) was independently rediscovered in 10/10 lineages and
    preferred over the carrier the experimenter DID designate (keep:
    a leak coefficient supplied for exactly this purpose), which was
    selected 0/10.

That is evidence the substrate routes around design intent. Whether it
routes around it because recurrence is BETTER or because recurrence is
EASIER TO REACH is the question of this cycle, and cycle 1 cannot
answer it. (Operator correction, 2026-09-23; LEDGER row same day.)

## 1. Instrument repairs (all verified before this file was committed)

I1 BALANCED SHUFFLED CUES. W4/W13 draw a second hidden binary in
   shuffled mode (which cue is SHOWN). balance_key now returns
   (regime, shown), so the shuffled held-out set is 8/8/8/8 and a pure
   cue reflex scores 0.50 there, not 0.59 (cycle-1 s4 defect).
I2 EDGE- AND SCC-AWARE ABLATION. ares/carriers.py replaces node-only
   attribution: it cuts each carrier CLASS (self_loops, all recurrent
   edges, keep, plasticity, and all cross-step channels at once), each
   strongly connected component, and each recurrent EDGE separately.
   Control: an output-node self-loop organism, which cycle-1 node
   ablation reports as having no ablatable structure at all, is
   correctly attributed here (tests/test_carriers.py).
I3 FRESH SEEDS, NO RE-EVALUATIONS. GA seeds 201-210 (never used in
   cycle 0 or 1); held-out seed sets built from start=40000. All 10
   lineages per arm are independent by construction; no cycle-0/1
   lineage is re-scored anywhere in this cycle.
I4 OPPORTUNITY-NORMALISED COUNTS. carriers.opportunity() measures
   P(one mutation CREATES carrier X | X absent) on the substrate the
   GA actually uses, so "keep 0/10" can be separated from "keep was
   rarely reachable". Reported as created/eligible, not as a raw count.
I5 Per-generation snapshots retained (they falsified the cycle-1
   accretion narrative).

## 2. Measured BEFORE any GA run (hand-wired reference organisms)

Both carriers were hand-built and measured on the repaired held-out
sets (tests/test_carriers.py; empty organism scores 0.00 everywhere):

    world                      hand-wired RECUR   hand-wired KEEP
    W4  (plain hidden regime)        24.56              33.75
    W14 (activation noise sd .5)     20.06              -4.31
    W15 (4 reset events)              8.88              11.69
    W16 (variable cue timing)         6.38               7.00

Three facts follow, and they set the predictions:
 (a) On W4 the DESIGNATED carrier is not merely usable, it is BETTER
     hand-built than the one evolution chose. So "recurrence won
     because it is intrinsically superior on this task" is already
     improbable before a single GA run.
 (b) W14 is an attack on the LEAKY INTEGRATOR, not on recurrence: a
     saturating self-loop is intrinsically noise-robust (-18%) while a
     linear keep-integrator accumulates the noise and dies (-113%).
     The label "hostile to recurrence" belongs to W15, not W14. This
     is stated here so the result is not later read the other way.
 (c) W15 and W16 damage BOTH activation carriers heavily, leaving
     plasticity as the only intact cross-step channel. If mechanism
     substitution happens anywhere, W15 is where.

## 3. Apparatus and arms

Substrate default Config; GA P=128, G=120, eps=4, elites 16; snapshots
on; 32 balanced held-out episodes per world/mode; seeds 201-210.
Fitness is world reward only. New Config flags are CONSTRAINTS or
COSTS, never rewards: no arm adds fitness for using any mechanism. The
"keep subsidy" the directive asks for is implemented as MUTATIONAL
opportunity (keep_mut_weight), not as a fitness bonus, because a bonus
would directly reward a designated mechanism and violate the charter.

Q1 CARRIER AVAILABILITY (world W4, 10 seeds each, 50 runs)
    c1_all          default (control)
    c1_only_recur   allow_keep=False, allow_plasticity=False
    c1_only_keep    forbid_recurrence=True, allow_plasticity=False
    c1_only_plast   allow_keep=False, forbid_recurrence=True
    c1_none         all three off (floor arm)

Q2 EXCLUSION, TAX AND SUBSIDY (world W4, 10 seeds each, 60 runs)
    c2_no_selfloop     forbid_self_loops=True (cycles of length >1 legal)
    c2_no_recur        forbid_recurrence=True (keep AND plasticity legal)
    c2_tax_low         recur_tax=0.05 per recurrent edge
    c2_tax_high        recur_tax=0.25 per recurrent edge
    c2_keep_subsidy    keep_mut_weight=8.0
    c2_recur_unstable  recur_mut_noise=0.5 (heritability attack)
  The tax is applied to TRAINING fitness only (it is the selection
  pressure); held-out fitness is always reported raw so arms stay
  comparable on one scale.

Q4 HOSTILE WORLDS (present and shuffled, 10 seeds each, 60 runs)
    W14 activation noise, W15 reset events, W16 variable delay.

Q3 needs no GA: it reuses the champions of Q1/Q2/Q4.
Total 170 GA runs.

## 4. Floors, attainables, thresholds

    world  floor  attainable       threshold
    W4      0.00   40.0 (cap)        8.00
    W14     0.00   40.0 (cap)        8.00
    W15     0.00   40.0 (cap)        8.00
    W16     0.00   10.0 (cap, reward only in the last 10 steps)  2.00
Floor 0.00 is structural: regimes are balanced, so every fixed policy
and the empty organism score 0.00 (verified s2). threshold = 20% of the
cap. Caps are structural maxima, not claims that they are reachable.

## 5. Per-champion measurements (recorded, never optimised)

carrier_class from the edge/SCC-aware cut set: RECUR / KEEP / PLAST /
MIXED:a+b / REDUNDANT (cut_all collapses, no single cut does) / NONE
(no cross-step cut collapses) / AT_FLOOR. Plus: inventory (self-loops,
self-loops on outputs, recurrent edges, SCC sizes, keep nodes, plastic
edges), load-bearing recurrent EDGES, per-SCC deltas, time-to-threshold
(first logged generation at or above threshold), and the behaviour
probe (late-life accuracy by regime).

## 6. Q1 causal battery (no GA; run once per arm/champion set)

 - opportunity(): P(create | absent) for recurrence, keep, plasticity,
   with the mutation draw histogram (the denominator).
 - single_mutation_gradient(): take a champion, strip ALL carriers,
   apply one mutation 300 times, and record the fitness change split by
   which carrier that mutation created. This measures the gradient each
   carrier offers AT THE MOMENT IT FIRST APPEARS, which is what
   selection actually sees.
 - time-to-threshold from the Q1 single-carrier arms.
 - robustness: each arm's champion re-evaluated on W14 and W15.
 - cost: edges, nodes, recurrent-edge count of each arm's champions.

## 7. Predictions (each can lose; I have lost count-predictions in
    both previous cycles by being pessimistic, so these are widened)

 P1 c1_only_keep reaches threshold in >= 7/10 (keep is viable when it
    is the ONLY option). If this loses, "accessibility" is wrong and
    superiority is live.
 P2 c1_only_keep's median time-to-threshold is LATER than c1_only_recur's
    (keep is viable but slower to find).
 P3 opportunity: p_create(keep) >= p_create(recurrent). (alter_keep is
    one of ten mutation types and always succeeds; a self-loop needs
    add_edge to draw i==j.) If keep is MORE reachable per mutation and
    still never selected, accessibility-by-raw-opportunity is refuted
    and the explanation must be the GRADIENT, not the opportunity.
 P4 single_mutation_gradient: mean fitness change for mutations that
    create recurrence > that for mutations that create keep. This is my
    primary causal hypothesis: one self-loop mutation buys a usable
    carrier immediately, whereas a useful keep needs a LARGE coefficient
    (~0.98 hand-built) that a single N(0,0.3) step cannot reach.
 P5 c2_no_recur: >= 7/10 reach threshold (evolution routes around), and
    the majority carrier class there is KEEP or PLAST, not NONE. This is
    mechanism substitution; I expect it to succeed, which makes the
    "recurrence is necessary" reading losable.
 P6 c2_tax_high reduces recurrent-edge counts relative to c1_all in
    >= 7/10 but does NOT change the carrier class in >= 7/10 (a tax
    trims, an exclusion substitutes).
 P7 c2_keep_subsidy does NOT flip the majority class to KEEP (if
    opportunity were the whole story, an 8x subsidy should flip it;
    predicting no flip is predicting P4 over P3).
 P8 W15 (reset) produces the largest class shift away from RECUR of any
    hostile world; PLAST becomes the majority class in >= 5/10 there.
 P9 Transplant: portable in <= 4/10 even with the edge-aware splice
    (the carrier is context-dependent), BUT swap recovery >= 0.5 in
    >= 5/10 (a donor's carrier restores a host's cut function), because
    a swap preserves the host's wiring context and a transplant does not.
 P10 No arm produces a champion above threshold with class NONE (no
    unenumerated cross-step channel exists in this substrate).

## 8. Stopping rule (operator, 2026-09-23; mechanical)

Ares earns further work ONLY if at least one gate opens:

 GATE A  SUBSTITUTION / NEW CARRIER. In at least one exclusion, tax or
   hostile arm, >= 5/10 champions reach that arm's threshold with a
   majority carrier class DIFFERENT from RECUR. Strong form
   (NEW_CARRIER): >= 5/10 above threshold with class NONE, i.e. a
   cross-step route outside the three enumerated channels -- which is
   treated as an INSTRUMENT question (a world leak) and chased as one
   before any claim.
 GATE B  CAUSAL EXPLANATION. The Q1 battery decides between
   ACCESSIBILITY and SUPERIORITY by this rule, fixed now:
     UNDECIDED    if c1_only_recur itself reaches threshold in < 7/10:
                  the apparatus failed and NOTHING is concluded about
                  either carrier. (Guard added 2026-09-23 after the
                  smoke test and BEFORE any cycle-2 GA run: without it,
                  an arm that simply never learns would be scored as
                  evidence FOR recurrence's superiority.)
     SUPERIORITY  if c1_only_recur reaches threshold in >= 7/10 AND
                  c1_only_keep reaches it in < 5/10 (keep is not viable
                  alone) -- recurrence won on merit.
     ACCESSIBILITY if c1_only_keep reaches threshold in >= 7/10 AND
                  (p_create(recurrent) > p_create(keep) OR the mean
                  single-mutation gradient of recurrence exceeds
                  keep's by >= 2.0) -- keep works but is not what
                  selection can find from where it stands.
     MIXED/UNDECIDED otherwise, and the gate does NOT open.
 GATE C  TRANSPLANTABLE CARRIER. Edge-aware transplant portable in
   >= 5/10, OR swap recovery >= 0.5 in >= 5/10.

If no gate opens -- i.e. the result is only "recurrence wins again" --
Ares CLOSES: the report says so, the machinery is packaged for export
to Nyx / Theophrastus / SFE, and no cycle 3 is proposed. The seat does
not self-authorise a continuation under any outcome; gates opening is a
recommendation to the operator, not permission.

## 9. Exit artifacts either way

ARES_CYCLE2_REPORT.md with the disposition and the gate table; a review
packet; the carrier instrumentation and pressure catalogue packaged for
export with a named consumer; artifacts to Nyx/Harmonia without waiting
for their vocabulary; STATUS -> PARKED or CLOSED per s8; ledger rows.

## ADDENDA (dated, appended only)

ADDENDUM 1 (2026-09-23, after the gates ran; two defects in the
cycle-2 apparatus found by auditing its own output, and one
falsification arm added with its prediction stated first).

D1 SELECTION ON THE HELD-OUT SET. search.run picks the final champion
   by argmax over the final population EVALUATED ON THE HELD-OUT
   episodes, so `final.heldout` is a max-of-128 statistic. It inflates
   any noisy score: the shuffled controls read 4.22 / 13.47 / 1.41 /
   1.50 when the clean number (the training-selected champion's
   held-out score, already in every run's log) is 0.00 / -2.38 /
   -0.14 / 0.00. Every arm at the structural cap is unaffected (40.0
   cannot be inflated), which is where every headline result of this
   cycle sits. ares/recheck_c2.py re-derives everything from the clean
   number; the worlds do NOT leak -- the apparatus did.
D2 BIASED SWAP STATISTIC. phase_gates scored gate C with the BEST
   donor per host (max over 9 donors). The operator's criterion is
   survival of substantial genomic-context change, so the per-PAIR
   statistic is correct: 16/59 pairs recover >= 0.5, median 0.02.
   GATE C is therefore SHUT, not open as first printed.

EXPLORATORY ARM c3_keep_reachable, added after the result and labelled
as post-hoc. The cycle's causal finding is that one mutation creates a
USABLE recurrent edge with p=0.0173 and a USABLE keep (>=0.90) with
p=0.0000 (0 of 8000), because alter_keep steps by N(0, 0.3) from zero.
That is a claim about the MUTATION OPERATOR and it is directly
falsifiable: widen the step to sigma=1.5 (one step reaches 0.9 with
p~0.27) and keep should become reachable. PREDICTION, recorded before
the arm was run: KEEP becomes load-bearing in >= 3/10 champions
(against 1/10 in c1_all) and keep's time-to-threshold falls toward
recurrence's. If the class distribution does NOT move, the step-size
explanation is wrong and the cycle's causal claim fails.
