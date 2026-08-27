# AGENT D-5 — BLIND HARD-TASK FINDABILITY

Start date: 2026-08-27
Agent: independent coding/research agent, clean state.

## Blind protocol
No artifact from any previous attempt at this or a related experiment has been
inspected, imported, imitated, or inferred from. Everything in `agent_d5_blind/`
is built fresh from the constitution supplied at launch.

## Question
Can accumulated executable history improve the findability of exact solutions to
hard, independently defined tasks, when solution existence and transformation
reachability are measured separately?

## The three-way split (core principle)
For every task, three separate classifications — never one bucket:

- E — EXPRESSIBLE: some artifact in the frozen substrate solves it exactly.
- R — REACHABLE: at least one solving artifact is reachable from the allowed
  starting repertoire under frozen transformation physics and budget model.
- F — FINDABLE: the admissible learner actually discovers a solving artifact
  under its own budget.

The central learning claim concerns F conditional on E and R.
Primary metric: CFR = learner-solved / oracle-reachable.

## Claim ladder (nothing above P7 may be claimed)
- P0 exact solving artifacts exist
- P1 exact solving artifacts are reachable under frozen mutation physics
- P2 strong history-free M0 can sometimes find them
- P3 accumulated executable history increases findability
- P4 accumulated history reduces acquisition cost
- P5 history-conditioned advantage transfers to held-out task families
- P6 learned machinery from prior tasks causally contributes to later acquisition
- P7 hard-task learning improves over developmental time

## Verdict hierarchy (conservative; forbidden words: intelligence, cognition, understanding, AGI)
SUBSTRATE_INVALID · TASK_BATTERY_INVALID · ORACLE_COVERAGE_INSUFFICIENT ·
REACHABILITY_COVERAGE_INSUFFICIENT · NO_HISTORY_ADVANTAGE ·
HISTORY_FINDABILITY_ADVANTAGE · HISTORY_COST_ADVANTAGE ·
DEVELOPMENTAL_ACCELERATION · FROZEN_TRANSFER_ADVANTAGE ·
CAUSALLY_REUSED_DEVELOPMENTAL_STRUCTURE

## Phase plan (order is constitutional — §49: M1 is built LAST)
1. PHASE 0 — substrate + preflight: choose primary substrate, preregister its
   accessibility preflight, implement, calibrate on engineering seeds, freeze
   thresholds, run evidence preflight. Gate G0.
2. PHASE 1 — task apparatus: task families, exact oracles, omniscient solution
   oracle, reachability oracle, difficulty strata, structureless control,
   instrument validation on synthetic batteries (§45). Freeze task battery.
3. PHASE 2 — M0 suite: three serious history-free navigators; calibration on
   engineering seeds; freeze main comparator (§37).
4. PHASE 3 — evidence protocol freeze: gates G0–G9 with exact thresholds,
   statistical plan (task-level units), budget meter, anti-cheat battery.
5. PHASE 4 — M1 build + developmental evidence runs + ablations + transfer.
6. PHASE 5 — verdict.

## Seed-stream policy (frozen now)
- 1000–1999: ENGINEERING seeds. Instrument calibration, wall-clock sizing,
  smoke tests. Results from these seeds NEVER enter evidence rows.
- 2000–2999: PREFLIGHT EVIDENCE seeds (Phase 0 evidence run).
- 3000–3999: TASK GENERATION seeds (frozen task battery).
- 4000–4999: M0 EVIDENCE seeds.
- 5000–5999: M1 DEVELOPMENTAL seeds.
- 6000–6999: ALIEN HELD-OUT family generation seeds (independent stream, §17).
- 7000–7999: ABLATION / CONTROL seeds.
- No Date/time/OS entropy anywhere in experiment code. All RNG is
  random.Random(seed) with logged seeds.

## No within-generation rescue (§44)
Once PREREG-EVIDENCE.md is frozen (hash committed): no easier tasks, no removed
failures, no weakened M0, no raised budgets, no altered physics, no moved gates,
no patched M1 after evidence. Fatal defect → preserve, invalidate, stop.

## Repository layout
As constituted: substrate/ mutation/ task_generators/ exact_oracle/
reachability_oracle/ navigators/ learner/ developmental_history/ ablations/
controls/ anti_cheat/ ledgers/ results/ preflight/ + PREREG-*.md + VERDICT.md.
All frozen artifacts hashed in anti_cheat/frozen_hashes.json.
Build history in ledgers/BUILD_LOG.md, appended as work happens.
