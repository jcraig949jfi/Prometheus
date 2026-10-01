# RSI BOUNDARY REVISITED -- 2026-09-30

Seat: Aphrodite (inference harvest). Tier 1-3. No positive RSI claim is made or implied anywhere in this document.

Aphrodite has tested recursive improvement at ENGINE scale since 2026-09-17. That work produced:
- S4 ABSTRACTION_TRANSPLANT = YES;
- BOUNDED_RSI = NOT YET ESTABLISHED;
- G1_RECURRENT_STEPPING_STONE = YES under CONSTRUCTED recurrence, mechanism only;
- G1_STEPPING_STONE = NO under natural supply.

This document lifts those distinctions to LAB scale (Prometheus as the candidate improver). It also tightens them so that
none can be satisfied by "the system produced more artifacts".

---------------------------------------------------------------------------------------------------------------------

## 1. Three things that are routinely conflated

| Term | What changes | Minimal formal statement | What it is NOT |
|---|---|---|---|
| **Improvement** | the object-level output | the system at time t2 produces more validated information per resource than at t1 on matched tasks | more output; output on easier tasks; output with more resources |
| **Improvement-process improvement (IPI)** | the function that maps resources to improvements | producing an improvement costs less, or pays more, at generation g+1 than at g | one good tool; a governance document; a ruler that is merely stricter |
| **Recursive self-improvement (RSI)** | the IPI loop closes inside the system | the generation-(g+1) improvement process was produced by generation-g outputs of the SAME system, not by an external agent, and the gain persists or grows for at least 2 successive generations under a fixed external envelope | IPI driven by an operator; IPI driven by a model upgrade; one generation of IPI |

Two qualifiers are mandatory in any claim:
- **bounded**: the claim holds inside a stated resource envelope, model version and task family, and is not
  extrapolated beyond them;
- **scope**: ENGINE-scale (inside one search/abstraction system, e.g. Aphrodite's G1->G2) versus LAB-scale (Prometheus
  as a whole). An engine-scale result is never evidence for lab-scale RSI, and vice versa.

---------------------------------------------------------------------------------------------------------------------

## 2. The ladder

Each rung has: a criterion, a ruler, hostile controls, and a falsifier. A rung may be claimed only when every lower
rung holds for the SAME lineage. "Lineage" is defined in the causal model, s5.

Notation: eta = information yield per resource vector (causal model s1.2), computed at matched task difficulty, with X1
(model version) held fixed or event-studied and X2 (operator-minutes) metered.

### L0 -- ACTIVITY (not a rung; listed so that it can be excluded)
More commits, packets, messages, experiments, seats, tokens or core-hours.
**Never** evidence for L1+. Any claim whose ruler reduces to an L0 quantity is rejected without review.

### L1 -- OBJECT-LEVEL IMPROVEMENT
- Criterion: eta(t2) > eta(t1) on a FIXED task family, paired, lower 95% bound > 0.
- Ruler: VIU surprisal under calibrated pooled priors (causal model s1.1), per component resource.
- Hostile controls:
  - equal-resource replay: re-run the t1 configuration with t2's resources;
  - within-seat decomposition (rules out C8 selection);
  - per-seat normalisation (rules out C9 parallelism).
- Falsifier: the t1 configuration at t2's resources matches t2 (the gain was resources). Or the gain disappears
  within seat at matched task type (the gain was selection).

### L2 -- INSTRUMENT IMPROVEMENT THAT TRANSFERS
- Criterion: a tool/ruler/infrastructure change e raises eta on downstream work that did NOT motivate e. The lower 95%
  bound must be > 0 against a matched stream without e.
- Ruler: payoff(e) (causal model s5) over a preregistered horizon.
- Hostile controls:
  - **sham instrument**: an announced, equally visible change of equal ceremony that does nothing (a checklist of
    platitudes; a no-op validator). This tests whether attention/Hawthorne effects explain the gain;
  - stale-ruler re-scoring: the new and the old ruler score the same outputs. If the "gain" exists only under the new
    ruler, it is a ruler change, not an improvement.
- Falsifier: payoff concentrated on the commissioning experiment; the sham matches; or the gain is a ruler artifact.

### L3 -- REUSABLE EXPERIMENTAL SKILL (cross-substrate)
- Criterion: a procedure P learned on substrate A lowers the INVALID + UNTESTABLE rate, or raises eta, on a substrate B
  that has NO project history, compared with a matched B-run where P is ablated from context, tools and packets.
- Hostile controls:
  - lesson ablation;
  - a generic-advice control (equal-length generic methodology text);
  - fresh-context agents on both arms (rules out C3 memory);
  - same model version.
- Falsifier: the ablated arm matches; the generic-advice arm matches; or the effect requires B-specific hints.
- Example candidate from history: Aphrodite's "pre-freeze supply screens are mandatory" (T49, after A20-A22 failed on
  supply). It has never been tested cross-substrate.

### L4 -- IMPROVEMENT-PROCESS IMPROVEMENT (IPI)
- Criterion: across improvement generations g = 1..G, the cost of producing an L2-qualifying improvement falls, or its
  payoff rises, at fixed operator-minutes and model version. The metric is the slope of log(payoff/cost) on g, with lower
  95% bound > 0.
- Hostile controls:
  - an operator-effort covariate (operator-minutes per improvement event);
  - a model-version event study;
  - a **difficulty control**: early improvements pick the low-hanging fruit, so the cost of producing them would RISE
    at constant capability. The comparison is against a fitted diminishing-returns null, not against a flat line.
- Falsifier: slope <= 0 after controls; or fully explained by operator effort or the model switch.

### L5 -- AUTONOMOUS IPI
- Criterion: L4 holds on lineages whose internal nodes are system-originated. Origin is SEAT-AUTONOMOUS or BUILDER, with
  no OPERATOR-originated design and no human hand-edit. Operator-minutes per generation must be non-increasing.
- Ruler: the authorship audit (Observatory `improvement_event.origin`), verified against operator text in MWOs, CWOs and
  comms.
- Hostile control: **operator-quiet windows**. The lineage must continue to produce qualifying generations during
  preregistered windows where the operator issues no directives. The 2026-09-30 -> 10-01 05:00 harvest window is an
  example shape, though it is too short.
- Falsifier: lineage nodes trace to operator directives; or production stops in quiet windows.

### L6 -- BOUNDED RSI (lab scale)
- Criterion: L5 for at least 3 consecutive generations. The per-generation gain must be non-decreasing, or decreasing
  slower than the preregistered diminishing-returns null. It must hold inside a fixed external envelope (model version,
  compute cap, operator-minutes cap). The generation-(g+1) process must CAUSALLY depend on generation-g outputs.
- Hostile controls:
  - a **sham lineage**: equal-cost process changes produced without access to the previous generation's outputs
    (fresh-context Builders with the same budget). This is the lab analogue of SHAM_k in AMENDMENT 15 R4;
  - **generation knockout**: remove generation g's output and re-run generation g+1. If g+1 is unchanged, g was not causal.
    This is the analogue of R1 G1-DEPENDENCE.
- Falsifier: the sham lineage matches; the knockout has no effect; or the gain is flat or decreasing faster than the null.

### L7 -- OPEN-ENDED RSI
Not specified as a target. It is listed only to mark the boundary: no finite experiment establishes it. Any document
asserting L7 is rejected.

---------------------------------------------------------------------------------------------------------------------

## 3. Mapping existing results (engine scale vs lab scale)

| Result | Scope | Highest rung it could support | Status |
|---|---|---|---|
| S4 ABSTRACTION_TRANSPLANT = YES (A14/S4) | engine | engine-L2/L3 analogue: an abstraction derived on one family transfers to unseen-body families | accepted by the operator 2026-09-24; ENGINE scope only |
| TRANSFERABLE_SEARCH_LEVERAGE = YES_LOCAL (Tier 3B/3C) | engine | engine-L2 | local; equal expressivity |
| BOUNDED_RECURSIVE_SELF_IMPROVEMENT = NO (Tiers 3A-3C); BOUNDED_RSI not established (A15, A16, A17) | engine | engine-L6 FAILED or UNTESTABLE | standing |
| G1_STEPPING_STONE = NO (A19/C2) | engine | engine-L5 analogue FAILED under natural supply | standing |
| G1_RECURRENT_STEPPING_STONE = YES, GENERIC 3/3 (A23) | engine | the MECHANISM by which an L4-analogue could arise; under CONSTRUCTED recurrence only | not an RSI claim; capability is budget-relative; G1 not privileged |
| Prometheus as a lab | lab | at most L1/L2 candidates; NO lab-scale lineage data exist | see INFERENCE_HARVEST_HANDOFF s2-s3 |

The A23 result says something precise. **When a task family recurs, an inherited abstraction acts as a stepping stone.**
That is a CONDITIONAL mechanism.

W8 then showed that recurrence in natural lineages lands where the pristine search cannot see it (recurrence x
visibility, TH-019). The lab-scale analogue is a warning. Prometheus's own "lessons" may recur mostly in places where its
rulers cannot see them. A ruler that cannot see the recurrence cannot credit the improvement, and it also cannot detect
false credit.

---------------------------------------------------------------------------------------------------------------------

## 4. Traps that make the ladder easy to climb falsely

1. **Governance recursion.** Documents about the process, audits of audits, and work orders about work orders form a lineage
   of process changes whose generations do depend on each other. That superficially satisfies L5's lineage clause. They
   count only if each generation passes L2, meaning a measurable object-level payoff on work that did not motivate them.
   Without L2, governance recursion is L0.
2. **The operator inside the loop.** If the operator reads the system's output and writes the next directive, the loop
   is closed THROUGH a human. That is human-in-the-loop improvement, and it can be excellent. It is not RSI.
   Operator-minutes and the origin field exist to make this visible.
3. **Model upgrades as fake generations.** A new model version raises every seat at once. If generations are dated, a
   model switch inside a lineage invalidates the slope for that interval unless an event study removes it.
4. **Ruler co-evolution.** If the ruler is improved in the same generation as the thing it measures, gains can be
   created by the ruler. Rule: score every generation with BOTH its own ruler and the frozen generation-1 ruler. Report
   both and claim only what survives both. Where they disagree, that is a ruler finding, not an improvement finding.
5. **Self-caught defects as progress.** A rising rate of self-found defects is equally predicted by better self-review
   and by worse first drafts. Only a planted-defect battery at a fixed protocol separates them (AGENT_SCIENCE E8).
6. **Difficulty drift.** Generations that pick easier targets look like IPI. Each improvement event needs a difficulty
   estimate frozen before production, e.g. a forecast of the cost to produce it.
7. **Survivorship.** Only improvement lineages that "worked" get recorded as lineages. The Observatory must record
   abandoned improvement attempts with their costs. Otherwise payoff/cost is computed on survivors only.

---------------------------------------------------------------------------------------------------------------------

## 5. Operational decision table

A claim of the form "Prometheus is getting better at producing future improvements" is admissible at rung L only if:

| Rung | Data needed | Exists today? |
|---|---|---|
| L1 | VIU records with p_pred at freeze; matched task families; resource meters | partial: verdicts exist; p_pred absent; operator-minutes unmetered |
| L2 | improvement-event records with downstream payoff vs a matched stream | no: Builders started 2026-09-30; no matched streams |
| L3 | a cross-substrate transfer experiment with lesson ablation | no: designed in AGENT_SCIENCE E4 |
| L4 | at least 3 improvement generations with cost and payoff | no |
| L5 | origin audit plus operator-quiet windows | origin is recoverable retrospectively for MWO/CWO-era changes; quiet windows not instrumented |
| L6 | sham lineages plus generation knockouts | no |

Current admissible statement (lab scale): **"No rung above L0 is currently established for Prometheus as a lab. Some
L1/L2 candidates are identifiable retrospectively, but not establishable with existing records."** See the handoff for
which candidates these are.
