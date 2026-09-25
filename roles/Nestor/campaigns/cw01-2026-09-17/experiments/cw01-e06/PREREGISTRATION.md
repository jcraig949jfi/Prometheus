# cw01-e06 — Representation ecology (PRE-REGISTRATION)

Written before implementation and before any organism is evaluated. This is the
anti-fitting device: the science is fixed here, the verdict contract is hashed from
it, and a criterion change during EXECUTE voids the attempt and opens a new
`attempt_id`.

## The question

Do representational forms acquire different **ecological roles** under shared
environmental pressure — persistence, invasion, displacement, coexistence,
specialization, frequency dependence?

## The question this is NOT

Which representation computes the task better. **Task success is not ecological
success.** A representation that dominates because it began with a small intrinsic
task advantage, with no interaction whatsoever, is a benchmarking result and an
ecological null. The design and the statistic must be able to tell those apart.

## World

**Representation-blind task.** Organisms map inputs to outputs and are scored on
outputs alone. The reward function never reads the substrate label, and no
representation-specific bonus exists anywhere in scoring or selection.

**Attempt-stable latent facts** (CW01-D029/D037). The target structure is drawn ONCE
per `attempt_id`; the items presented are drawn PER EPISODE from that structure.
Matched latent worlds: both substrates face the same opportunity structure, from the
same stream seeds.

**Two substrates, mechanically different, expressing overlapping solutions.**

| | TREE | TAPE |
|---|---|---|
| form | expression tree | linear instruction list over registers |
| compactness | compact for the same function | longer for the same function |
| mutation locality | subtree replacement: non-local, large effect | single-instruction edit: local, small effect |
| recombination | subtree crossover, TREE partner required | one-point crossover, TAPE partner required |
| intermediate structure | implicit, free | explicit registers, maintained at cost |
| incremental modification | coarse | fine |

Every difference above arises **mechanically from the substrate**. None is a scoring
rule. The reachable function sets overlap substantially, so the same solution can be
expressed in either.

## Hypothesised ecological mechanism

**Recombination compatibility is assortative by substrate.** TREE×TREE and TAPE×TAPE
recombine; TREE×TAPE does not. A rare substrate therefore finds fewer compatible
partners, so its recombination yield falls with its own frequency — predicting
POSITIVE frequency dependence and contingent, history-dependent dominance.

A competing mechanism is also live: the cost of maintaining explicit intermediate
structure may vary with population composition, which would produce NEGATIVE
frequency dependence and coexistence.

Both remain reachable. So does no frequency dependence at all.

## Three layers, measured separately and never collapsed

- **TASK** — output score; what the organism can compute.
- **REPRESENTATION** — substrate label, program size, realised edit locality,
  recombination yield, resource cost.
- **ECOLOGY** — frequency trajectory through time, invasion success when rare,
  resistance to invasion when common, lineage survival, extinction/displacement time,
  representation transitions where permitted.

Frequency **trajectories** are recorded, not merely endpoints.

## Interventions

**M1 — REPRESENTATION SWAP.** Hold task, initial capability and resource budget fixed;
change only the substrate. Does the subsequent ecological trajectory change?

**M2 — ECOLOGICAL CONTACT.** Run each substrate ALONE, then TOGETHER. Essential: if A
beats B in isolation that says nothing about ecology. Measures invasion, persistence
and displacement under shared environment.

**M3 — PRESSURE NEUTRALISATION.** Make recombination substrate-agnostic (cross-substrate
crossover permitted at equal yield) while leaving representation LABELS intact. If the
ecological effect survives neutralisation, then representation identity is acting as a
proxy, or the measurement is contaminated. Minimal by design, as with e05's M3.

## Primary statistic (to be frozen in the verdict contract)

The decisive quantity separates representation QUALITY from ecological INTERACTION.

Let `r_A(f)` be the per-capita growth advantage of substrate A measured in MIXED
populations seeded at frequency `f`, over `f in {0.10, 0.25, 0.50, 0.75, 0.90}`.
Let `s_solo` be A's advantage implied by SOLO lanes on matched worlds — the purely
intrinsic term, which is frequency-independent by construction.

    interaction(f)  =  r_A(f)  -  s_solo
    beta            =  slope of interaction(f) with respect to f

- `beta ~ 0` — frequency-independent. The mixed outcome is explained by intrinsic
  advantage alone. **This is an ecological NULL even if one substrate fixes.**
- `beta < 0` — negative frequency dependence; rare-advantage; coexistence predicted.
- `beta > 0` — positive frequency dependence; common-advantage; contingent dominance.

Terminal abundance is recorded but is **never** the verdict quantity.

## Nulls and controls

- **A — same substrate, different lineage labels.** Estimates ecological noise with NO
  representational difference. Supplies the measured band for `beta` and for every
  ecological quantity. Thresholds come from here, before treatment is inspected.
- **B — different labels, mechanism neutralised (M3).** Tests whether labels leak into
  scoring or execution.
- **C — solo versus mixed.** Separates intrinsic task advantage from
  interaction-dependent ecological advantage.
- **D — replica executor from a relocatable checkout at a DIFFERENT directory depth**
  than the canonical tree. Proves CW01-D046 is actually dead rather than asserted.

Every effect claim must clear its measured null via `infometrics.effect_clears_null`
in a pre-declared direction. A sign test is never sufficient (CW01-D035).

## Dispositions — fixed now

- **NEGATIVE** — the world produces no task-capable organisms in either substrate, or
  the task is unlearnable; the instrument, not the ecology, is the finding.
- **NULL** — substrates compute differently but no ecological quantity clears its
  measured null: `beta` inside control A's band AND no invasion asymmetry, displacement
  or coexistence signal clearing its own null. **Reachable and expected if
  representation is ecologically inert.**
- **INCONCLUSIVE** — the ecological interaction was not genuinely exercised (e.g. one
  substrate extinct before contact), or a measure cannot clear its null, or IX is not
  discharged, or the effect does not replicate across attempt seeds.
- **COMPLETE** — representation changes an ecological quantity under the frozen
  contract; the decisive effect clears its null; it survives control A; it is abolished
  or materially reduced by M3; and it holds in EVERY replicate.

**COMPLETE is explicitly not "TREE wins".** A substrate fixing is not by itself
evidence of ecology.

## Reachability requirement

The minimal experiment must permit all of: TREE fixes, TAPE fixes, stable coexistence,
contingent/history-dependent dominance, and no meaningful ecological difference. A
design in which one substrate is structurally destined to dominate is not an ecology
experiment. QUALIFY must demonstrate each outcome is attainable before budget is spent.

## Thresholds

Derived from control A's measured noise band, declared before treatment is inspected,
and never selected from the first successful replicate (CW01-D016/D041).

## Amendment 1 — PRE-DATA (CW01-D052/D053/D054)

No contract has been hashed and no organism has been evaluated under a frozen
criterion. The **question, the primary statistic, the controls and the dispositions
above are unchanged.** What changed is the world, because three PREFLIGHT probes showed
the original could not express the question at all.

**D052 — the world was a fixation lottery.** 18/18 runs fixed, 0/18 coexisted, and
control A (two labels on ONE substrate, no representational difference) fixed 6/6.
Fixation therefore carried no information about representation. Assortative
recombination is a *positive* frequency-dependence mechanism and on its own can only
accelerate fixation. Added a representation-blind negative-FD channel: each item is a
**resource** and solvers **split its value**. Selection changed from deterministic
truncation to a tournament.

**D053 — my diagnosis of why that fix failed was wrong, and I measured before acting.**
I hypothesised a single-niche world in which sharing is a monotonic rescaling. Both
halves were false: Jaccard overlap between the item sets TREE and TAPE solve is 0.531,
with 23 TREE-exclusive and 15 TAPE-exclusive items, and sharing reorders fitness (rank
correlation +0.629, 12/24 top-quartile overlap). Recorded so no later session re-tests
a refuted hypothesis.

**D054 — the real cause, and the error was mine.** The target was generated as a
depth-3 **expression tree**: one substrate's native form. The reward function was
representation-blind, but the *world* was not. Generation-zero measurement over
frequencies {0.10, 0.25, 0.50, 0.75, 0.90} showed TREE's measured **lower envelope**
(0.345) exceeding TAPE's measured **upper envelope** (0.289), so there is **no observed
crossing and no mutual invasibility in the exercised domain**, and requirement 4 is
violated there.

*Correction, and the overclaim was mine:* an earlier version of this section said
coexistence was "impossible, not merely unlikely". That is stronger than the evidence.
The curves were never analytically bounded over the full frequency interval; upgrading
this to a proof requires deriving monotonic bounds from the generation-zero fitness
function. Until then it is an empirical bound over the tested range.

This satisfied design requirement 1 literally, in the reward function, while violating
its spirit in the target **generator** — a *substrate leak*. The emerging doctrine:
representation neutrality has at least three layers — neutral reward, neutral task
generation, neutral ecological bookkeeping. Layer one was satisfied and layer two was
accidentally violated.

**Constraints on the redesign (operator-authorised):**
1. The target language must be genuinely **prior to both substrates** — an operation
   graph with explicit dependencies and reuse, which each substrate independently
   realises while paying its own mechanical cost. A straight-line instruction list
   would be "TAPE semantics with a TREE compiler" and is not acceptable.
2. **Reuse is an environmental axis, not a representation label.** Swept over
   preregistered bands. The precondition is not that some TREE-friendly world and some
   TAPE-friendly world exist, but that *one substrate-neutral generator* produces
   regions where Δ(r) = F_TREE(r) − F_TAPE(r) is positive and regions where it is
   negative.
3. **Mutual invasibility is a hard QUALIFY gate.** Evaluated before any evolutionary
   run; if either type cannot invade when rare against the resident, the configuration
   is refused rather than burning compute. The pre-fix world is retained as an
   adversarial **fixture**: the gate must be shown *refusing* it, so the new world earns
   admission rather than merely looking better.

Targets are now straight-line **DAGs spanning a reuse spectrum**. Low reuse is a tree,
which TREE expresses compactly; high reuse re-references intermediates, which TAPE holds
in registers and TREE must duplicate. Neither substrate is native to the family as a
whole. This is squarely inside design requirement 2, which names *cost of maintaining
intermediate structure* as a legitimate mechanical difference.

**Promoted to a gate.** *Mutual invasibility at generation zero* — each label must be
fitter than the other when rare — is the mathematical precondition for coexistence. It
is now a Q16 sub-predicate, measured before any budget is spent, so this failure is
caught by a cheap check rather than by eighteen evolutionary runs.

**Still outstanding and deliberately not changed in the same step:** control A fixes at
generation 26 against a neutral-drift expectation of ~96, so its noise floor is *lineage
hitchhiking*, not drift. One variable at a time; that is addressed only after the target
fix is measured.

## Stated limitations, in advance

Small programs, not rich organisms. Two substrates only. A coarse frequency grid.
Assortative recombination is one mechanism among several that could generate frequency
dependence; refuting it does not refute representation ecology in general.
