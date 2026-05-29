"""Sprint-1 A7: stable low-rank tensor structure (Phase 2, ITER-51).

Hypothesis (from roadmap v2 line 89):
> "Effective rank of kill tensor over time"
> Pass: rank stabilizes (not linear in N) -> real geometry, not
> duplicates.

## Operationalizing "effective rank stabilizes"

If the substrate's emissions are drawn from a finite underlying
structure, the kill_tensor's populated-cell count should
SATURATE as the stream grows -- the marginal new-cell rate
should decline. If emissions add cells linearly (each new
emission adds a new cell), the tensor is just accumulating
duplicates of axis values; no underlying geometry.

A7 measures the ratio of EARLY new-cell rate to LATE new-cell
rate. If late rate / early rate is below threshold, the tensor
is saturating -- effective rank is bounded.

## A7 protocol

1. Generate a stream of N=500 synthetic emissions from a finite
   underlying cell space (4 plugins x 3 domains x 5 invariants
   x 6 kps = 360 max cells).
2. Take RankSnapshots at 10 evenly-spaced checkpoints
   (50, 100, 150, ..., 500).
3. Compute new-cell rate at each checkpoint:
     rate(t) = (n_populated(t) - n_populated(t - 50)) / 50
4. Compare early_rate = rate(100) to late_rate = rate(500).
5. Pass if late_rate / early_rate < 0.5
   (late growth is less than half of early growth -- the tensor
   is saturating, not growing linearly).

## Why this is the right test

The roadmap's "rank stabilizes (not linear in N)" is the
substrate's "real geometry" criterion: if the kill_tensor never
saturates, it's not finding a bounded structure. The substrate's
emissions would be wasting ticks on duplicates.

The 0.5 threshold is conservative -- the late rate must be HALF
the early rate to count. A flat substrate (no saturation) would
have late rate ~= early rate -> ratio ~= 1.0 -> fail.

A failure (ratio >= 0.5) means: even after 500 emissions from a
finite 360-cell space, the substrate is still discovering new
cells at near-early rates. The underlying structure is not low-
rank in any detectable sense.
"""
from __future__ import annotations

import random

from charon.agents.erebos._kill_tensor import KillTensor
from charon.agents.erebos._rank_expansion import RankSnapshot
from charon.agents.erebos.sprint1 import SprintResult


N_EMISSIONS = 500
N_SNAPSHOTS = 10
PLUGINS = ["g01", "g02", "g03", "g04"]
DOMAINS = ["d1", "d2", "d3"]
INVARIANTS = ["inv_1", "inv_2", "inv_3", "inv_4", "inv_5"]
KPS = ["kp_a", "kp_b", "kp_c", "kp_d", "kp_e", "PROMOTED"]
SEED = 421
PASS_THRESHOLD_RATIO = 0.5  # late_rate / early_rate must be < 0.5


def _generate_stream(n: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        kp = rng.choice(KPS)
        rows.append({
            "plugin_id": rng.choice(PLUGINS),
            "domain": rng.choice(DOMAINS),
            "invariant": rng.choice(INVARIANTS),
            "kill_pattern": None if kp == "PROMOTED" else kp,
        })
    return rows


def run_a7() -> SprintResult:
    rows = _generate_stream(N_EMISSIONS, SEED)
    checkpoint_step = N_EMISSIONS // N_SNAPSHOTS  # 50

    tensor = KillTensor()
    snapshots: list[RankSnapshot] = []
    for i, row in enumerate(rows, start=1):
        tensor.add_row(row)
        if i % checkpoint_step == 0:
            snapshots.append(RankSnapshot.take(tensor, timestamp=i))

    # Compute new-cell rate between consecutive snapshots
    deltas = []
    for prev, curr in zip(snapshots, snapshots[1:]):
        deltas.append(curr.n_populated - prev.n_populated)

    # Early rate: average of first 2 deltas (between snapshot 1->2
    # and 2->3, i.e., across ticks 50->150)
    # Late rate: average of last 2 deltas (across ticks 400->500)
    if len(deltas) < 4:
        early_rate = deltas[0] if deltas else 0
        late_rate = deltas[-1] if deltas else 0
    else:
        early_rate = sum(deltas[:2]) / 2.0
        late_rate = sum(deltas[-2:]) / 2.0

    ratio = late_rate / early_rate if early_rate > 0 else float("inf")
    passed = ratio < PASS_THRESHOLD_RATIO

    return SprintResult(
        experiment_id="A7",
        hypothesis=(
            "Kill tensor's new-cell discovery rate saturates: late "
            "growth is less than half of early growth"
        ),
        metric_name="late_rate_over_early_rate",
        metric_value=ratio,
        pass_threshold=PASS_THRESHOLD_RATIO,
        comparator="<",
        passed=passed,
        protocol_summary=(
            f"Stream of N={N_EMISSIONS} synthetic emissions from a "
            f"finite cell space ({len(PLUGINS)}x{len(DOMAINS)}x"
            f"{len(INVARIANTS)}x{len(KPS)}="
            f"{len(PLUGINS) * len(DOMAINS) * len(INVARIANTS) * len(KPS)} "
            f"max cells); snapshots every {checkpoint_step} ticks; "
            f"early_rate = avg of first 2 inter-snapshot deltas, "
            f"late_rate = avg of last 2. Ratio = late / early."
        ),
        notes=(
            f"n_snapshots={len(snapshots)}; "
            f"final_n_populated={snapshots[-1].n_populated}; "
            f"final_shape={snapshots[-1].axis_cardinalities}; "
            f"deltas={deltas}; "
            f"early_rate={early_rate}; late_rate={late_rate}; "
            f"ratio={ratio:.4f}; pass_threshold<{PASS_THRESHOLD_RATIO}"
        ),
    )
