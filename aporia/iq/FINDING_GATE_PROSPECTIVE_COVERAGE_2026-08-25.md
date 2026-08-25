# The gate's first prospective test found a hole in the gate

BATTERY (`86b1e582`) said its own retro-validation was a fit statistic and that the gate's value
would be decided **prospectively**, by binding SELECTOR before SELECTOR runs. That test has now
been run, and it found something I did not anticipate — in the gate, not in SELECTOR.

## What happened

The SELECTOR preregistration was expressed as a structured claim object and submitted to
`aporia/iq/battery.py` before any experiment code existed.

    VERDICT: ADMISSIBLE     (deterministic on repeat)

**But that verdict is only 5 of 7 gates deep.** Measured by source scan over which fields each
gate reads, against which fields exist at preregistration time:

    _gate_class      intervention_class                        fires
    _gate_mandatory  falsifiers_run, intervention_class        fires
    _gate_floor      thresholds                                fires
    _gate_perturb    probe_modifies_measured_quantity          fires
    _gate_branch     branch_table_partitions                   fires
    _gate_vacuous    readings                                  INERT — no readings exist yet
    _gate_inert      is_null_result, positive_control_ran      INERT — outcome unknown yet

**5 of 7 can fire prospectively. Two are structurally inert on any preregistration**, because
they key exclusively on fields that only exist after the run.

## Why this is the finding rather than a footnote

The two inert gates are **G-VACUOUS and G-INERT** — and those encode two of the three defect
classes this arc committed most often. G-VACUOUS in particular is the one most relevant to
SELECTOR, whose own preregistration predicts a **VACUOUS** outcome at pre-flight.

So the gate cannot enforce the vacuity check at the moment it would be cheapest to enforce it.
I had to write SELECTOR's PF3 pre-flight — *"if fewer than three candidates have ΔE > 0, report
VACUOUS, never 'no selector beat random'"* — **by hand**, which is exactly the analyst-attention
mechanism BATTERY exists to replace.

## What it means for BATTERY's own claim

BATTERY's headline stands: the gate discriminates on **post-hoc** claims, admitting six rungs and
rejecting all six when a falsifier is ablated. That was measured and is unaffected.

What is now qualified is the **scope**: it is a post-hoc admissibility gate, and its prospective
coverage is 5/7 with the two most-committed defect classes among the missing. Reported as a
measured limitation rather than discovered later by a rung that slips through.

**The gate did its job in the only sense available to it here** — it produced a finding I had not
anticipated on first prospective use. That the finding is about its own coverage rather than
about SELECTOR is not a lesser outcome; an instrument that reports its own blind spot on first
use is behaving correctly.

## The fix, named but not made

G-VACUOUS and G-INERT need **prospective forms** keyed on declared intent rather than realised
outcome:

    G-VACUOUS-PRE   the claim declares an attainable range for every reading it will take,
                    and no declared range is degenerate
    G-INERT-PRE     the claim declares whether a null is a possible outcome, and if so names
                    the positive control that will be run

Both are cheap. **Neither is built here**, because BATTERY is committed and adding gates after
seeing what they would have caught is the retune-to-pass failure its own preregistration warned
about. They go in a preregistered amendment, ahead of the next claim that needs them.

## Standing note

SELECTOR's preregistration is ADMISSIBLE under the five gates that can fire, and its PF3
pre-flight covers by hand what G-VACUOUS-PRE would cover by machine. That is recorded so the
hand-written check is not mistaken for machine enforcement.
