# Worker H: what computational roles does dynamic rule switching provide?

ID W-H. Output workers/W-H/. Namespace 0x5ED. Read COMMON_RULES.md and
COMMON_RULES_ARC3.md first. Budget ~4 h. CPU-first.

QUESTION
In some PTE champions, sites switch program variants (SETRULE) during
operation, not only at start-up. Pick a SMALL number of specimens that
discriminate distinct mechanisms (not an enumeration). For each:
(1) decompile the branch; (2) identify the condition (what state or input
selects the rule); (3) identify the consequence (what the selected
variant does differently); (4) run a targeted counterfactual (force or
forbid the branch at the relevant tick, or replace the switching program
with a fixed-rule program). Then answer: does dynamic rule switching
EXPAND computational capability in these cells, or merely COMPRESS
something a fixed-rule program of the same length could do? Candidate
roles (not an exhaustive list): conditional branch, phase selection,
routing selection, state-machine transition, readout gating, temporary
specialization.

EVIDENCE (raw)
- A previous 42-cell census with scripts and raw outputs: workers/W-B/
  (census.py, deepdive.py, phase.py, gate.py, disasm.py, out/*.json). Cell
  ids named in its outputs include b59e6c3a, 63d17a90, b059e735, 311c465f,
  faafa5b0, dd6fdf49, 8e1caf6b, 9bbe8637 (find full ids in
  roles/Ananke/pte/c1_rows/cells.jsonl.gz).
- Engine semantics: prometheus/ananke/engine.py (SETRULE: r_next = A mod
  rules, applied after the program; genome shape [rules, L, 5]; r
  initialized from rng INIT). Decompilation: plants.regmap / plants.OPS.
- Prior art on switching systems / finite-state control / task-set vs item
  memory: PRIOR_ART_temporal_distributed_computation.md s4, s6.
REQUIRED: PLAN.md frozen before counterfactuals; for the "capability vs
compression" question, state in advance what would count as evidence of
EXPANSION (e.g. no fixed-rule program of equal length reaching the same
competence under a bounded search you define).
DELIVERABLE: the report in your final message; DISAGREEMENTS.
STOP: 4 h.
