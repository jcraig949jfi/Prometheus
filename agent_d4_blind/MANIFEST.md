# AGENT D-4 — BLIND ACCESSIBILITY GEOMETRY

Date opened: 2026-08-27
Agent: independent coding/research agent, clean state.
Prior-attempt artifacts: NOT searched, NOT inspected, NOT imported, NOT imitated.

## Question

Can fixed machine-native computational physics provide a navigable space of
executable self-transformation in which useful directions of change are not
already strongly privileged by the designer?

This is an adversarial experiment. The goal is not to demonstrate learning.
The goal is to determine whether a fair substrate for testing learning can
exist. A clean negative is a successful experiment.

## Phase discipline

- Phase 1 ONLY: executable phenotype geometry, accessibility, navigation,
  mutation bias, baseline fairness. No learner. No M1. No worlds. No
  transfer experiment. No recursive-learning claim.
- Claim ladder tested: P1–P4 only.
  - P0 executable self-transformations exist
  - P1 generic mutation reaches viable behavioral diversity
  - P2 the viable phenotype space is intrinsically navigable
  - P3 navigation is not strongly dependent on designer-privileged corridors
  - P4 strong history-free M0 can fairly navigate it
  - P5/P6 NOT claimed under any outcome.

## Constitution order (binding)

1. PREREG-INSTRUMENT.md — operational definitions of intrinsic privilege and
   navigability; synthetic geometry controls with known pathologies;
   instrument-validation criteria. Iteration on the INSTRUMENT is permitted
   until the instrument validation gate passes; all iterations preserved in
   git history.
2. Instrument validation run on synthetic controls. If the metric suite
   cannot distinguish the known pathologies, repair the instrument BEFORE
   freezing anything else. (Repairing the instrument on synthetic controls
   is calibration, not evidence about any real substrate.)
3. PREREG-PHASE1.md — frozen substrates, mutation physics, probes, targets,
   navigators, counterfactuals, budgets, gates, verdict vocabulary. Hashed
   and committed BEFORE any real-substrate measurement exists.
4. Binding run. After the binding run begins: no primitive addition/deletion,
   no threshold movement, no mutation reweighting outside preregistered
   counterfactuals, no probe/target/navigator repair, no horizon extension.
   Fatal defects discovered mid-run: preserve the run, mark invalid, stop.
5. VERDICT-PHASE1.md + machine-readable phase1_verdict.json, committed in
   the SAME commit as all raw rows that support it.

## Hard rules inherited from the charter

- Human mutation/edit taxonomies are never a positive metric. They return
  only as red-team attacks that can weaken, never strengthen, a verdict.
- Validity is a coordinate, not the objective. Diversity is a coordinate,
  not the objective.
- Distinguish and never collapse: expressivity, validity, viability,
  diversity, accessibility, connectivity, navigability, privilege.
- Oracle information never enters any M0 navigator.
- All machine-visible information is enumerated in anti_cheat/.
- No LLM in the loop. No host-language introspection inside substrate
  state. No filesystem information entering substrate state.
- Forbidden conclusions: AGI, intelligence, consciousness, understanding,
  autonomous diagnosis, human-independent cognition, elimination of human
  priors, open-ended evolution.

## Strongest allowed Phase-1 claim (if earned)

"Under the frozen computational physics, executable behavioral change forms
a substantially diverse, reproducibly navigable accessibility geometry under
multiple generic history-free search processes, without evidence that
navigation is dominated by a small designer-privileged set of mutation
corridors." Nothing stronger.

## Layout

- d4core/            shared library: substrate interface, meters, distances,
                     metrics, navigators, classifier, oracle
- substrates/        frozen real computational bases (Phase-1 constitution)
- mutation/          frozen generic mutation physics (raw-encoding level)
- probes/            frozen behavioral probe suites
- synthetic_geometry_controls/  known-pathology toy geometries + results
- intrinsic_metrics/ privilege/accessibility metric outputs
- navigation/        M0 navigator run outputs
- targets/           deterministic target-selection outputs
- classifiers/       mutation-source identifiability outputs
- counterfactuals/   counterfactual mutation-physics outputs
- anti_cheat/        machine-visible-information enumeration + static checks
- ledgers/           append-only run ledgers (all rows preserved)
- results/           aggregated machine-readable results
