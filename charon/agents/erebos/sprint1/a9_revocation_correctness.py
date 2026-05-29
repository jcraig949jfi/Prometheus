"""Sprint-1 A9: residue revocation correctness (Phase 2, ITER-53).

Hypothesis (from roadmap v2 line 91):
> "When downstream falsifies a prior kill_pattern, the revocation
> mechanism marks it superseded AND downstream routing changes"
> Pass: >= 80% of revocations propagate to subsequent routing
> changes -> revocation is causally connected.

## Structural framing

ITER-39 shipped the revocation primitive (RevocationRegistry,
filter_active, is_revoked, superseded_by) but did NOT wire it to
the daemon's routing decision. The pre-committed real-data test
would measure runtime routing changes after a revocation; that
wire is pending.

A9 measures the STRUCTURAL correctness of the revocation
mechanism: of N revocations applied to a synthetic ledger, what
fraction are correctly excluded by Layer 2 query primitives
(filter_active) that downstream routing WOULD consult?

If structural propagation < 80%, the primitive itself is broken
and Phase 1B ITER-39 has a bug. If structural propagation >=
80%, the primitive's correctness is established; the daemon
wire becomes a separate (and tractable) concern.

## A9 protocol

1. Build a synthetic ledger of N=100 rows. Each row has a
   row_id, kill_pattern, plugin_id, and input_signature.
2. Revoke K=30 randomly-chosen rows (each gets superseded_by
   pointing to a DIFFERENT row).
3. For each revoked row, verify:
     (a) is_revoked(row_id) returns True
     (b) filter_active(all_rows) excludes that row
     (c) superseded_by(row_id) returns the assigned successor
4. propagation_rate = n_correctly_propagated / K.
5. Pass if propagation_rate >= 0.80.

## What this test does NOT cover

The pre-committed claim "downstream routing changes" requires
the daemon to consult filter_active before routing. That wire
is Phase 2+ work. A9's structural pass is necessary but not
sufficient for the real-data claim; the daemon-side runtime
test is deferred.
"""
from __future__ import annotations

import random

from charon.agents.erebos._residue_revocation import RevocationRegistry
from charon.agents.erebos.sprint1 import SprintResult


N_ROWS = 100
N_REVOKED = 30
SEED = 619
PASS_THRESHOLD = 0.80


def _build_synthetic_ledger() -> list[dict]:
    rng = random.Random(SEED)
    plugins = ["g01", "g02", "g03", "g04", "g05"]
    kps = ["kp_a", "kp_b", "kp_c", None]
    rows = []
    for i in range(N_ROWS):
        rows.append({
            "row_id": f"row_{i:04d}",
            "plugin_id": rng.choice(plugins),
            "kill_pattern": rng.choice(kps),
            "input_signature": f"sig:{i % 30:03d}",
        })
    return rows


def run_a9() -> SprintResult:
    rng = random.Random(SEED + 1)
    rows = _build_synthetic_ledger()
    reg = RevocationRegistry()

    # Randomly choose N_REVOKED rows to revoke; each gets a
    # successor pointing to a different randomly-chosen row
    revoked_indices = rng.sample(range(N_ROWS), N_REVOKED)
    revocations: list[tuple[str, str]] = []  # (revoked_id, successor_id)
    for idx in revoked_indices:
        row_id = rows[idx]["row_id"]
        # Pick a successor that's NOT the same row
        successor_idx = rng.choice([
            i for i in range(N_ROWS) if i != idx
        ])
        successor_id = rows[successor_idx]["row_id"]
        reg.revoke(
            row_id,
            superseded_by=successor_id,
            reason=f"sprint1_a9_test_revocation_{idx}",
        )
        revocations.append((row_id, successor_id))

    # Verify propagation: for each revocation, check three properties
    n_correctly_propagated = 0
    active_rows = reg.filter_active(rows)
    active_ids = {r["row_id"] for r in active_rows}
    for revoked_id, successor_id in revocations:
        # Property (a): is_revoked
        a = reg.is_revoked(revoked_id)
        # Property (b): excluded from filter_active
        b = revoked_id not in active_ids
        # Property (c): superseded_by returns assigned successor
        c = reg.superseded_by(revoked_id) == successor_id
        if a and b and c:
            n_correctly_propagated += 1

    propagation_rate = n_correctly_propagated / N_REVOKED

    passed = propagation_rate >= PASS_THRESHOLD

    return SprintResult(
        experiment_id="A9",
        hypothesis=(
            "Revocations structurally propagate to Layer 2 queries "
            "(is_revoked / filter_active / superseded_by all "
            "correctly identify revoked rows)"
        ),
        metric_name="revocation_propagation_rate",
        metric_value=propagation_rate,
        pass_threshold=PASS_THRESHOLD,
        comparator=">=",
        passed=passed,
        protocol_summary=(
            f"Build synthetic ledger of {N_ROWS} rows. Revoke "
            f"K={N_REVOKED} randomly-chosen rows with random "
            f"successors. For each revocation, verify is_revoked, "
            f"filter_active exclusion, and superseded_by lookup. "
            f"Propagation = fraction passing all three checks."
        ),
        notes=(
            f"n_rows={N_ROWS}; n_revoked={N_REVOKED}; "
            f"n_correctly_propagated={n_correctly_propagated}; "
            f"propagation_rate={propagation_rate:.4f}; "
            f"pass_threshold={PASS_THRESHOLD}; "
            f"STRUCTURAL TEST -- daemon-routing wire deferred"
        ),
    )
