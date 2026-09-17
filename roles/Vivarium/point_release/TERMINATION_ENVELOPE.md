# Termination / censoring envelope (point release, MUST SHIP)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 (Vivarium m2-fce3fe0b). Stage 1 design (operator s7; Amendment 1 s5.A on the SFE side).

## 0. Why (Campaigns 2-3)

    L2-026    stop-rule runs were recorded as 'treated', losing valid right-censored baselines -> C3 group B: stopped_on_solve +
              monotone pooling
    C3-SFE-01 "residence censored at 300 everywhere": every run reached the horizon; the absence of a summit is UNOBSERVED
              BEYOND THE HORIZON, not absent
    C3 report the vocabulary now in use: completed / stopped-on-solve / budget exhausted / target not reached / prerequisite
              failed / instrument invalid / deliberately terminated / censored before event
    Vivarium  today a budget stop is a FAILURE (failure_class BUDGET_EXCEEDED, runner.py:428/438/781): a run that produced
    today     eleven valid observations and hit max_seconds is recorded like a crash. That is the defect this envelope closes.

## 1. The envelope (execution_attempt.termination jsonb; every attempt gets one at close)

    {
      "envelope_version":      "viv.termination.v1",
      "termination_reason":    one of the CLOSED set below,
      "terminal_state":        COMPLETED | FAILED | CANCELLED | STRANDED          (== execution_attempt.terminal_state)
      "horizon":               {"kind": "generations" | "evaluations" | "observations" | "seconds" | "ticks" | "UNKNOWN",
                                "declared": <n>}                                  from repeat.budget / the bundle's budget, verbatim
      "budget_consumed":       {"observations": n, "seconds": s, "generations": g | "UNKNOWN", "evaluations": e | "UNKNOWN",
                                "cost_events": c}                                measured by Vivarium where it can (observations, seconds,
                                                                                  cost events it reserved) and copied from the kind's
                                                                                  result where declared (generations, evaluations); UNKNOWN
                                                                                  otherwise
      "logical_time_reached":  {"generation": n} | {"tick": n} | "UNKNOWN",       from the kind's result or the engine (s5.A) once SFE stamps it
      "stopped_on_condition":  {"condition_id": ..., "at": {...}} | null,         a producer-declared stop rule that fired (stop-on-solve is
                                                                                  ONE such rule; Vivarium evaluates it like a gate and
                                                                                  records which one)
      "censored":              true | false,                                      TRUE iff the attempt ended for a reason other than the
                                                                                  producer's own stop condition or a scientific completion:
                                                                                  horizon reached, budget exhausted, cancelled, stranded,
                                                                                  instrument invalid. Mechanical, from termination_reason.
      "censoring_reason":      the termination_reason when censored, else null,
      "partial":               true | false,                                      observations exist but fewer than repeat.count
      "observations_recorded": n,
      "terminal_receipt_ref":  {"receipt_digest": ..., "last_step_id": ...}
    }

## 2. termination_reason (CLOSED set, v1; extension = a new envelope_version)

    COMPLETED_ALL_REPEATS       every repeat produced its observation
    STOPPED_ON_CONDITION        a producer-declared stop rule fired (stop-on-solve etc.); observations before it are complete
    HORIZON_REACHED             the declared logical horizon (generations/ticks) was reached without a stop condition
    BUDGET_EXHAUSTED            max_seconds / max_observations / a reserved cost envelope was consumed before the horizon
    PREREQUISITE_FAILED         a gate with on_fail abort_attempt failed (PREREQUISITE_GATE_RECEIPT.md)
    INSTRUMENT_INVALID          the kind reported INDETERMINATE for the whole attempt (D3) or a result-contract refusal
    EXECUTOR_ERROR              the executor raised (today's EXECUTOR_ERROR)
    ENGINE_TRANSPORT            engine unreachable / lease lost (today's classes)
    CANCELLED                   operator cancel
    STRANDED                    worker death; resolved only by release
    UNKNOWN                     pre-release attempts (backfill): the status is known, the reason is not fabricated

Mapping to terminal_state (mechanical): COMPLETED_ALL_REPEATS, STOPPED_ON_CONDITION,
HORIZON_REACHED, BUDGET_EXHAUSTED -> COMPLETED (with censored true for the
last two); PREREQUISITE_FAILED, INSTRUMENT_INVALID, EXECUTOR_ERROR,
ENGINE_TRANSPORT -> FAILED; CANCELLED; STRANDED.

The behavioural change: BUDGET_EXHAUSTED and HORIZON_REACHED become
COMPLETED-and-censored instead of FAILED. The row's observations are
fossilized as today; the outcome_rule is evaluated over the observations
that exist with `aggregate` as declared, and the fossil carries censored:
true. The queue's failed count stops absorbing censored science.

## 3. What Vivarium does NOT infer

Whether "target not reached" is FLOOR, SHELF or SUMMIT-limited; whether a
censored residence was "probably" heading somewhere; whether a stop
condition was scientifically right. The envelope says whether an event was
OBSERVED or UNOBSERVED-BEYOND-THE-HORIZON, which is the one distinction a
projection cannot recover afterwards.

## 4. Fossil and outbox

The envelope is copied verbatim into the PEW encounter (resources_used already
carries execution inputs; `termination` joins it) and is one outbox event
(ATTEMPT_TERMINATED) with the attempt id as its source.

## 5. Acceptance (Stage 4)

    positive   a kind that runs 5 of 12 repeats in max_seconds ends COMPLETED / BUDGET_EXHAUSTED / censored true / partial true /
               observations_recorded 5; the fossil carries it; the outcome_rule sees 5 observations
    positive   a producer stop rule "first observation with accuracy >= 0.9" fires at repeat 3 -> STOPPED_ON_CONDITION, censored false,
               stopped_on_condition names the rule and the repeat
    negative   an executor raise -> FAILED / EXECUTOR_ERROR / censored false (an error is not censoring)
    cheat      a run that completes all repeats but whose kind reports logical_time below the declared horizon is COMPLETED_ALL_REPEATS
               with logical_time_reached < horizon.declared visible -- the envelope does not paper over a short run
    old rows   backfilled attempts carry termination_reason UNKNOWN with terminal_state from status; never a guessed reason;
               parsing an old row's error text into a reason is FORBIDDEN (Stage-2 Q5) and a test asserts the backfill never does
