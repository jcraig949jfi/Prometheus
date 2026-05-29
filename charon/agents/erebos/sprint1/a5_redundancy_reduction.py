"""Sprint-1 A5: redundancy reduction over iterations (Phase 2, ITER-49).

Hypothesis (from roadmap v2 line 87):
> "Mean ticks-to-novel-emission as ledger grows"
> Pass: downward trend -> memory reduces wasted exploration.

## Operationalizing "downward trend"

As the kill_ledger accumulates emissions, two things can happen:
  (a) The eligibility gate sees more priors -> catches more
      duplicates as exhaust -> the rate of "eligible per tick"
      DECLINES as memory grows. THIS IS THE MEMORY-IS-WORKING
      CASE.
  (b) The gate's behavior is roughly constant regardless of
      ledger size -> memory is NOT filtering accumulating
      duplicates. Layer 2's exhaust filter is not load-bearing
      over time.

A5 measures the slope of (cumulative_eligible / tick_n) over a
stream of duplicate-heavy emissions. If memory is reducing
wasted exploration, the eligibility rate DECLINES as the ledger
grows -- slope < 0.

## A5 protocol

1. Generate a stream of N=300 synthetic emissions where K=120
   (40%) are duplicates of earlier emissions.
2. Walk the stream chronologically, building memory ledger
   context. At each tick, assess eligibility.
3. At each tick t, compute eligibility_rate(t) =
   cumulative_eligible(t) / t.
4. Fit a linear slope of eligibility_rate(t) over t, restricted
   to the second half of the stream (avoids early-tick noise
   where t is small).
5. Pass if slope < 0 (eligibility rate declines as memory grows).

## Why this is the right test

If memory has no effect, eligibility_rate stays constant ->
slope ~ 0. If memory catches accumulating duplicates,
eligibility_rate declines over time -> slope < 0. The sign of
the slope is the substrate's directional signal.

The duplicate density (40%) is realistic per A1's protocol; the
duplicate stream embeds the same "should be filtered" structure.
The metric does not require knowing which specific emissions are
duplicates -- the rate slope is sufficient.

A failure (slope >= 0) means: even as duplicates accumulate
beyond the first few ticks, the gate's eligibility rate stays
flat or rises. Memory is not reducing wasted exploration in
the substrate's observable behavior.
"""
from __future__ import annotations

from charon.agents.erebos._residue_eligibility import (
    LedgerContext,
    assess_residue_eligibility,
)
from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a1_memory_ablation import (
    _build_ledger_context,
    generate_synthetic_stream,
)


N_EMISSIONS = 300
DUP_FRACTION = 0.40
SEED = 271
PASS_THRESHOLD_SLOPE = 0.0   # slope must be < 0 to PASS


def _linear_slope(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return 0.0
    return num / den


def run_a5() -> SprintResult:
    stream = generate_synthetic_stream(
        n=N_EMISSIONS, dup_fraction=DUP_FRACTION, seed=SEED,
    )

    seen: list = []
    cumulative_eligible = 0
    eligibility_rate_series: list[tuple[int, float]] = []

    for tick_idx, emission in enumerate(stream, start=1):
        ctx = _build_ledger_context(seen)
        v = assess_residue_eligibility(
            plugin_id=emission.plugin_id,
            new_kill_pattern=emission.kill_pattern,
            verdict=emission.verdict_dict,
            domain=emission.domain,
            ledger_context=ctx,
            input_signature=emission.input_signature,
        )
        if v.eligible:
            cumulative_eligible += 1
        eligibility_rate_series.append(
            (tick_idx, cumulative_eligible / tick_idx)
        )
        seen.append(emission)

    # Slope over the second half of the stream
    second_half = eligibility_rate_series[N_EMISSIONS // 2:]
    xs = [t for t, _ in second_half]
    ys = [r for _, r in second_half]
    slope = _linear_slope(xs, ys)

    initial_rate = eligibility_rate_series[N_EMISSIONS // 2][1]
    final_rate = eligibility_rate_series[-1][1]

    passed = slope < PASS_THRESHOLD_SLOPE

    return SprintResult(
        experiment_id="A5",
        hypothesis=(
            "Eligibility rate declines as memory accumulates "
            "(slope of cumulative_eligible / tick over second "
            "half of stream is negative)"
        ),
        metric_name="eligibility_rate_slope_second_half",
        metric_value=slope,
        pass_threshold=PASS_THRESHOLD_SLOPE,
        comparator="<",
        passed=passed,
        protocol_summary=(
            f"Stream of N={N_EMISSIONS} synthetic emissions "
            f"(dup_fraction={DUP_FRACTION}, seed={SEED}). Walk "
            f"chronologically; assess eligibility per tick with "
            f"growing LedgerContext. Slope = linear regression of "
            f"(cumulative_eligible / tick) over t, restricted to "
            f"second half (ticks {N_EMISSIONS // 2 + 1}..{N_EMISSIONS})."
        ),
        notes=(
            f"cumulative_eligible_final={cumulative_eligible}; "
            f"second_half_initial_rate={initial_rate:.4f}; "
            f"second_half_final_rate={final_rate:.4f}; "
            f"slope={slope:.6f}; pass_threshold<{PASS_THRESHOLD_SLOPE}"
        ),
    )
