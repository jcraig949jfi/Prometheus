# PREREG-EVIDENCE — Evidence Protocol, Gates, Statistics (Phase 3)

Status: DRAFT. Freezes after: evidence preflight G0 verdict, hardness
calibration (engineering seeds), instrument validation (PREREG-TASKS section
8), and M0 comparator freeze. All [TBD] fields must be numeric at freeze; no
[TBD] may survive into a frozen document.

## 1. Arms
- M0a-HC, M0b-POP, M0c-RX: history-free suite (navigators/m0.py), frozen.
  MAIN COMPARATOR: the navigator with the best reach rate on the EVIDENCE
  PREFLIGHT rows (disjoint population from the task battery; section 37
  compliance). All arms run; gates evaluate against the main comparator.
- M1: identical base machinery to the main comparator; sole extra resource =
  admissible developmental history (machine-native artifacts + descriptors
  accumulated from prior tasks in the frozen sequence). Built LAST.

## 2. Developmental design
- Dev sequence: n_dev = [TBD ~50-60] tasks over F1-F4 + interleaved NEGX at
  frozen positions + CTRL tasks excluded from history accumulation? NO —
  CTRL tasks are part of the stream (unlabeled) but analyzed separately.
  Order = frozen at battery freeze from task-generation seeds (3000-3999).
- Replicates: 5 M0 lineages x 5 matched M1 lineages (seed-paired: same task
  order, same task seeds, same verifier; only history differs).
- Alien held-out: n_alien = [TBD ~20] tasks (seeds 6000+), zero-shot first
  with frozen M1 history, adaptation measured separately afterward.

## 3. Budget model (metered in exact-oracle verifier evaluations)
- Frozen ladder per task: [TBD after hardness calibration; provisional
  1000 / 3000 / 10000 / 30000]. Identical for all arms.
- M1 history operations are metered: any candidate drawn from or recombined
  with a history artifact costs one evaluation when verified, like any other;
  history LOOKUP cost is metered as [TBD: lookup-cost model, e.g. 1 evaluation
  per k retrievals]. No hidden intelligence outside the meter.

## 4. Primary metric and gates (thresholds numeric at freeze)
CFR = exact-solved / oracle-reachable (== expressible in RM-D5; the R==E
theorem is disclosed in PREREG-TASKS section 5).
- G1 oracle-solvable count: >= [TBD] EXPRESSIBLE tasks per family.
- G2 reachable count: == G1 by theorem (disclosed, carries no information).
- G3 M0 nontrivial competence: main comparator CFR at top rung in
  [TBD band, e.g. 10-70%] on the dev battery (not zero everywhere, not
  trivial everywhere; section 46).
- G4 findability: M1 CFR > M0 CFR by >= [TBD margin] at the top rung
  (task-level paired permutation test, alpha [TBD]).
- G5 acquisition cost: M1 median first-solve < M0 on jointly-solved reachable
  tasks (paired; censored-aware secondary analysis on all reachable tasks).
- G6 developmental trend: late-half relative advantage > early-half (paired
  task-level statistic, preregistered split at the sequence midpoint).
- G7 frozen alien transfer: M1 zero-shot CFR > M0 CFR on alien reachable
  tasks by >= [TBD margin].
- G8 control selectivity: on CTRL-RAND, M1 advantage <= [TBD small margin]
  (an M1 that beats M0 on structureless tasks is leaking or buying compute).
- G9 causal ablation: removing [TBD: artifact set / history trace] destroys
  >= [TBD fraction] of the G4 advantage (M1-ablation suite of PREREG-TASKS
  and constitution section 15: M1-no-history, M1-no-artifacts,
  M1-shuffled-history, M1-random-library).

## 5. Statistical plan
- Unit of inference: the TASK (within-lineage); lineage-level aggregation for
  between-arm comparisons. Candidate evaluations are never an n.
- Paired design: M0/M1 share task order, task seeds, and verifier; seed
  pairing documented per lineage.
- Tests: task-level paired permutation test for CFR deltas; bootstrap over
  tasks for cost ratios (HACR reported with full per-task distributions).
- Multiplicity: the gate family G4-G9 is reported jointly; primary claim
  requires G4 alone at alpha [TBD]; other gates label the verdict tier.
- Report every gate with its CI beside the verdict; a gate must sit further
  from the observed value than its own SE to count as informative.

## 6. Verdict mapping
- G0-G3 fail -> SUBSTRATE_INVALID / TASK_BATTERY_INVALID /
  ORACLE_COVERAGE_INSUFFICIENT as applicable.
- G4 fail (with G0-G3 pass) -> NO_HISTORY_ADVANTAGE (a preserved, useful
  negative).
- G4 pass -> HISTORY_FINDABILITY_ADVANTAGE; + G5 -> HISTORY_COST_ADVANTAGE;
  + G6 -> DEVELOPMENTAL_ACCELERATION; + G7 -> FROZEN_TRANSFER_ADVANTAGE;
  + G8 + G9 -> CAUSALLY_REUSED_DEVELOPMENTAL_STRUCTURE (top verdict).
- No verdict may use the words intelligence, cognition, understanding, AGI.

## 7. No-rescue clause
Identical to MANIFEST: after freeze, no task edits, budget raises, navigator
weakening, gate movement, or M1 patches. Fatal defect -> preserve, invalidate,
stop; lesson goes to a successor generation.
