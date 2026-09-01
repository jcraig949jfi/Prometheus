# MINT-0004 — consistency_check (PARSER gap + missing consistency predicate over an existing structure)
**STATUS:** `COMPOSITION-SUSPECTED` · **updated** 2026-09-01T09:13:00Z · missing-for-READY: WHAT_SHOULD_HAVE_HAPPENED, MINIMAL_REPRODUCER, POSITIVE_EXAMPLES, NEGATIVE_EXAMPLES, BOUNDARY_EXAMPLES, CURRENT_PRIMITIVES, PRIMITIVE_SET_HASH, WHY_COMPOSITION_APPEARS_INSUFFICIENT, CLOSURE_EVIDENCE, CHEAP_MODEL_ATTEMPTS, CHEAP_MODEL_FAILURES, COUNTERFEIT_TESTS, KNOWN_SHORTCUTS, FORBIDDEN_SHORTCUTS, REPRESENTATION_PERTURBATIONS, DESIRED_TYPED_INTERFACE, INDEPENDENT_EVALUATOR, SUCCESS_CRITERION, KILL_CRITERION

## PRIORITY
- **score**: 0.219
- **dimensions**: - **cheap_search_exhaustion**: 0.0
- **distinct_models**: 0
- **distinct_failure_families**: 0
- **evidence_current_set_cannot_express**: 0.0
- **frequency_across_worlds**: 0.25
- **number_of_independent_origins**: 0.5
- **potential_cross_world_utility**: 0.5
- **quality_of_reproducer**: 0.0
- **quality_of_falsifier**: 0.0
- **minimality_of_required_extension**: 0.5
- **rationale**: Likely Level 0/1 (composition of existing primitives + a parser). Not a Level-2 candidate until closure evidence says otherwise. Held until MINT-0001 completes one cycle (charter §25).

## SOURCE_WORLD
Apollo canary, category consistency_check

## SOURCE_AGENT
Apollo / Aporia

## FAILURE_FAMILY
consistency_check (PARSER gap + missing consistency predicate over an existing structure)

## WHAT_FAILED
check_transitivity / solve_constraints exist; no parser feeds them a cycle-detection question; no predicate 'is this relation set consistent' is exposed as an op.

## WHAT_SHOULD_HAVE_HAPPENED
_(missing)_

## MINIMAL_REPRODUCER
_(missing)_

## POSITIVE_EXAMPLES
_(none yet)_

## NEGATIVE_EXAMPLES
_(none yet)_

## BOUNDARY_EXAMPLES
_(none yet)_

## CURRENT_PRIMITIVES
_(none yet)_

## PRIMITIVE_SET_HASH
_(missing)_

## WHY_COMPOSITION_APPEARS_INSUFFICIENT
_(missing)_

## CLOSURE_EVIDENCE
_(none yet)_

## SEMANTIC_KERNEL_SPEC
unknown — not yet asked; likely 'cycle detection over a relation set' which check_transitivity already computes

## REPRESENTATION_ADAPTER_SPEC
parser: recognise a consistency question and feed relations to the existing structure

## SEARCH_ALREADY_ATTEMPTED
_(none yet)_

## CHEAP_MODEL_ATTEMPTS
_(none yet)_

## CHEAP_MODEL_FAILURES
_(none yet)_

## BEST_FAILED_CANDIDATE
_(missing)_

## KNOCKOUT_RESULTS
- **note**: Baseline (no op) = Apollo's current behaviour: abstain on every item; accuracy_decidable 0.0. Any candidate's holdout accuracy is therefore its own knockout delta.; **n_executed_attempts**: 0; **n_pass_dev**: 0

## COUNTERFEIT_TESTS
_(none yet)_

## KNOWN_SHORTCUTS
_(none yet)_

## FORBIDDEN_SHORTCUTS
_(none yet)_

## REPRESENTATION_PERTURBATIONS
_(none yet)_

## DESIRED_TYPED_INTERFACE
_(missing)_

## RESOURCE_CONSTRAINTS
_(missing)_

## INDEPENDENT_EVALUATOR
_(missing)_

## SUCCESS_CRITERION
_(missing)_

## KILL_CRITERION
_(missing)_

## PROVENANCE
- **ref**: aporia/docs/CYCLE_155S_FOUR_ARE_NOT_FOUR_2026-08-24.md:72-75
- **ref**: aporia/docs/CYCLE_156S_SEVERED_LIBRARY_2026-08-24.md
