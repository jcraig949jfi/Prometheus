# V0.6 addendum: the n=12,000 precision gate FAILED, and the target was NOT changed

Filed 2026-09-03, after the first production attempt and before the second.

## What happened

The frozen G3 precision gate is median row TV <= 0.010 and p95 row TV <= 0.020 between two
independent full-space kernel estimates. At the frozen n = 12,000 the run produced:

    median row TV   0.010333    limit 0.010    FAIL
    p95    row TV   0.016333    limit 0.020    PASS
    p99    row TV   0.018833
    max    row TV   0.023250    (reported, never a criterion)
    edge-presence disagreements   0
    escaped valid structural states  0

The run stopped there, by design, before computing any current, stationary distribution, entropy
production, cycle affinity or attribution. Result preserved as `RESULT_FULL_n12000_GATE_FAIL.json`.

## Why it failed: my sizing error

The pilot fitted median TV = 1.0775 / sqrt(n) on a 103-state positional subset. The full space
gives 1.1320 / sqrt(n) — the pilot constant was 5.1% low, because a stride-20 positional subset
under-represents the rows with larger support. I then chose n = 12,000 against a predicted median
of 0.00984, leaving only 1.7% margin. A 5% error in the constant was therefore fatal. The defect
is the margin, not the fit.

## What was done, and what was NOT done

**NOT done:** the threshold was not lowered, loosened, or re-expressed. Median <= 0.010 and
p95 <= 0.020 stand exactly as frozen.

**Done:** the sampling effort was increased to n = 20,000 per state per kernel, which the
re-estimated constant predicts will give median 0.0080 and p95 0.0127 — margins of 20% and 37%.
Increasing effort to meet an unchanged target is not moving a goalpost.

**Why this cannot be outcome-motivated:** the gate is checked before any substantive quantity is
computed, and the run exited at that point. Nothing about any current, stationary distribution or
attribution has been observed. The only thing seen is a precision statistic. This is exactly the
situation the gate ordering was designed to produce.

## Instrument change

Kernel transition counts are now persisted immediately after each kernel is measured, rather than
after the gates. The failed attempt discarded roughly 100 minutes of measurement because the
counts were only written later. This also lets a future higher-power run pool batches instead of
restarting.

## What is reported regardless

The n = 12,000 attempt is permanent evidence and appears in the final packet as a failure mode,
together with the pilot's 5.1% underestimate and the thin margin I chose.
