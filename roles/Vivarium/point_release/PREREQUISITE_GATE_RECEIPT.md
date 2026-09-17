# Prerequisite / capability-gate receipt (point release, ADD)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 (Vivarium m2-fce3fe0b). Stage 1 design (operator s6).

## 0. Why (Campaign 3)

Twice in C3 an instrument gated on a fixed constant instead of on the
measured state of its own space (slots 03 and 06: POSITIVE_CONTROL_FAILED on
the first engine attempt, repaired, re-preregistered, re-run; report s15
"recurring defects: 1 pattern, twice"). L3-011: a fixed 25-generation rung 0
released the ladder before W0 was climbed in 7/12 seeds. L3-030: an adaptive
threshold selected the CHANCE level. In every case the gate's decision was
buried in harness control flow; the record shows the consequence, not the
measurement the gate saw.

The receipt makes the gate's EXECUTION explicit: what was measured, against
what rule and reference, supplied by whom, with what result, before the
attempt was allowed to proceed. Vivarium evaluates the rule mechanically
exactly as it evaluates outcome_rule today (pre-registered predicate,
INDETERMINATE branch required), and never supplies a threshold.

## 1. The gate, as declared (in the start bundle, `gates`: [...]; optional)

    {
      "gate_id":        "pc:w0_climbed",                      producer's id
      "phase":          "pre_execution" | "pre_step:<kind>" | "post_step:<kind>",
      "condition":      "the W0 control population reaches best >= reference within hold_gens",
                                                               prose, verbatim, for the record
      "measurement":    {"source": "step_result" | "observation" | "artifact" | "producer_supplied",
                         "ref": "<step kind/parts | obs field | artifact digest>", "field": "best_reward"},
      "rule":           {"op": ">=" | "<=" | "==" | "in" | "between", "reference": <value | {"ref": ...}>,
                         "if_indeterminate": "FAIL" | "NOT_EVALUABLE"},
                                                               the reference may itself be a measured ref ("the chance level of THIS
                                                               table"), which is the L3-030 lesson written as a rule
      "on_fail":        "abort_attempt" | "mark_and_continue" | "skip_step:<kind>",
      "definition_ref": "<prereg_digest>#gates[0]"            provenance of the gate definition
    }

## 2. The receipt (viv.gate_receipt; one per gate evaluation per attempt)

    receipt_id          uuid PK
    attempt_id          uuid FK -> execution_attempt
    step_id             uuid NULL FK -> execution_step         the step it guarded (if pre/post_step)
    gate_id             text NOT NULL                           UNIQUE (attempt_id, gate_id, evaluated_at)
    phase               text NOT NULL
    condition           text NOT NULL                           verbatim
    measurement_ref     jsonb NOT NULL                          where the value came from (resolved refs: step_id / obs id / digest)
    measured            jsonb NOT NULL                          the value(s) read, verbatim; "UNKNOWN" if unreadable
    rule                jsonb NOT NULL                          verbatim from the bundle
    reference           jsonb NOT NULL                          the reference as RESOLVED at evaluation time (a literal, or the measured
                                                                value a ref pointed at) -- so "gated on a constant" vs "gated on the
                                                                measured space" is visible in the row
    result              text NOT NULL                           PASS | FAIL | NOT_EVALUABLE
    action_taken        text NOT NULL                           proceeded | aborted_attempt | marked_and_continued | skipped_step:<kind>
    definition_ref      text NOT NULL
    evaluated_at        timestamptz NOT NULL DEFAULT now()

## 3. Evaluation (mechanical; the same evaluator as outcome_rule)

    - resolve measurement_ref; if unresolvable -> measured = "UNKNOWN", result = NOT_EVALUABLE, action = rule.if_indeterminate mapped
      through on_fail (NOT_EVALUABLE with if_indeterminate FAIL behaves as FAIL; with NOT_EVALUABLE it is recorded and the attempt
      proceeds ONLY if on_fail is mark_and_continue -- an unevaluable abort gate aborts)
    - resolve reference (literal or ref); compare with op; PASS/FAIL
    - write the receipt BEFORE taking the action; the action is then taken; a crash between the two leaves a receipt with
      action_taken NULL, which the next attempt reads as "gate evaluated, action unknown" and re-evaluates (gates are pure reads)

## 4. What this is not

Vivarium does not decide what a positive control is, what its threshold is,
or whether FAIL should abort. It records that a producer-declared predicate
was evaluated over a named measurement against a resolved reference, and
what happened next. A harness that keeps its gate in control flow may still
do so; then the record lacks the receipt and the qualification fixture (s16)
fails its "prerequisite gate" line, which is the point.

## 5. Acceptance (Stage 4)

    positive   a gate over a step result with a literal reference PASSes and the attempt proceeds; the receipt shows measured, reference
    positive   the same gate with reference {"ref": "step:calibration.chance_level"} resolves the measured chance level and records it
    negative   a gate whose measurement is missing -> NOT_EVALUABLE; with on_fail abort_attempt the attempt closes FAILED
               (failure_class PREREQUISITE_FAILED) before any world exists
    cheat      a gate whose rule compares a value to itself (reference ref == measurement ref) is recorded PASS with identical
               measured/reference -- visible as the L3-030 shape; Vivarium does not refuse it (not its call) but the receipt makes it
               greppable: measured == reference
