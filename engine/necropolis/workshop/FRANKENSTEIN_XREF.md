# Frankenstein cross-reference (harvest charter VIII)

Measured by `build_frankenstein_xref.py` -> `FRANKENSTEIN_XREF.json`.  No monster was run.
"Missing" means absent for the interpreter that produced the JSON (see its `_README`); the
same package may be present on M1/M2 (Techne inventory #193 lists Lean 32/32 and hypothesis
under H:/Python312, both absent here).

| monster | grave | organs located / listed | plan scripts found | workshop tools (status) | blocking before stage 0 |
|---|---|---|---|---|---|
| FRANK-002 | Nous | 10 / 16 (6 unlocated are schema/operator/hint prose) | 4 / 4 | NT-077 NEEDS_VALIDATION, NT-082 NEEDS_DEPENDENCY | frozen judge UNATTESTABLE: 0 / 6661 `agents/hephaestus/ledger.jsonl` rows carry `judge_version` or `api_state` (1352 carry `model`); `openai` absent here; stage 1 is LLM spend = outside CORONER RUN (X4/X5); consumer reachable_now=false |
| FRANK-003 | Erebos | 10 / 18 (8 unlocated: schemas.1-2, operators.0-2, hints) | 4 / 4 (`permutation_null.py` is ambiguous: 3 files of that name; the plan means `charon/agents/erebos/sprint1/phase3/permutation_null.py`) | NT-004 READY, NT-037 READY, NT-058/059/060/061/078 NEEDS_VALIDATION | no third-party package missing; the historical kill_ledger bytes are gone (gitignored state/), so stage 0 must regenerate; the 146 / 608+1 / 59 test counts were NOT re-run by the Keeper (AUTHOR_TESTS.json has author-run counts only) |
| FRANK-004 | Pollux | 9 / 19 (10 unlocated: data.0, schemas, operators.0, 6 hints) | 7 / 7 | NT-006 READY, NT-010 UNTRUSTED, NT-048 READY, NT-049 READY_WITH_CAVEAT | scipy + MAHLER_TABLE present; DESIGN dead before run: the split-half positive control is pinned at alpha for any iid continuous gap law (run_controls.py::adapters_resampling_null.PERTURBATION.split_half_control_fails_at_alpha_rate_for_iid_continuous, hit rate 0.0133, 0/30 resolvable) -> kill criterion (2) fires; see coroner_plans/CR-001 PRF-1 |

## What the workshop can and cannot give each monster

- FRANK-002: the workshop can replay the scorer (nous.tests.0) and the salvage
  reproduction (nous.tests.2) once `agents/nous/src` is on sys.path, and can census the
  forge ledger; it cannot attest a frozen judge because the ledger never recorded one.
  Cleric checklist (i) therefore resolves NEGATIVE on the bytes we have: the monster is
  not runnable as written.  The missing dependency is not a package, it is a field.
- FRANK-003: every stage-0 harness compiles and its imports resolve here; NT-004
  (residue eligibility) and NT-037 (BOCPD) are READY with Keeper controls; the Westfall-
  Young / bootstrap / kill-tensor / revocation organs (NT-058..061) have author tests
  only and need Keeper controls before a CORONER RUN may name them.  The stage-0
  regeneration step (plan (c), 60 rows with per-detector kp diversity) has no tool in
  the registry yet: it is a producer, and the workshop holds readers.
- FRANK-004: the tools exist and are controlled (NT-048 ancestor replay, NT-049
  resampling null with parity to scipy and a Poisson negative control); the plan is
  written (CR-001) but carries a pre-run finding that the proposer's positive control
  cannot pass.  Refile the read in the upper tail or with a location-sensitive distance
  before asking for HITL approval.

## Unlocated organs

Schema, operator and representation-hint organs have empty `location` in ORGANS.jsonl by
construction (they are prose).  Nothing in this cross-reference treats an unlocated organ
as missing code; the counts above separate the two.
