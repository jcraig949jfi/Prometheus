"""Composition loader v2: EREBOS-G15-* (Cross-Generator MI) with
control-flow row filter applied before MI computation.

The v1 loader (composition_g15_ledger_mi) computed Shannon MI on
the full union of kill_ledgers and produced MI = 1.41 nats. Per
pivot/erebos_substrate_finding_iter13_g15_ledger_mi_2026-05-26.md
follow-up #1: 73.8% of v1's paired observations are control-flow
tags (kill_patterns ending in `_pending`,
`_no_loader_registered`, `_not_yet_implemented`, etc.), not real
falsification verdicts. The v1 MI was inflated by substrate
bookkeeping.

v2 filters these out before MI computation. If v2 MI < 0.10 nats,
the v1 signal was control-flow circularity (G15's expected_kill_
pattern, `uncorrelated_residual_failures`). If v2 MI >= 0.10
nats, the underlying mathematical coupling is real.

v1 + v2 coexist; v2 fires when composed_id contains "v2" or
"real_verdict".
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders.composition_g15_ledger_mi import (
    LEDGER_PATHS,
    MI_THRESHOLD_NATS,
    MIN_PAIRED_ROWS,
    _extract_kill_pattern,
    _extract_plugin_id,
    _shannon_mi,
)


# Suffix-based control-flow detection. Any kill_pattern ending in one
# of these is treated as bookkeeping, not a real verdict.
CONTROL_FLOW_SUFFIXES = (
    "_pending",
    "_no_loader_registered",
    "_not_yet_implemented",
    "_loader_pending",
    "_loader_not_yet_implemented",
    "_composition_data_load_failed",
    "_composition_insufficient_sample",
    "_composition_obligation_unknown",
    "_composition_no_obligations",
    "_composition_empty_adversarial_band",
    "_composition_payload_lookup_failed",
    "_composition_fit_failed",
    "_composition_import_failed",
    "_composition_no_survivors",
    "_hecate_meta_test_not_yet_implemented",
    "_battery_verdict_possible",  # POSSIBLE is intermediate, not falsification
)


def _is_control_flow(kp: Optional[str]) -> bool:
    if not kp:
        return True
    kp_lower = kp.lower()
    for suffix in CONTROL_FLOW_SUFFIXES:
        if kp_lower.endswith(suffix):
            return True
    return False


def _read_ledger_rows() -> list[dict]:
    """Re-implementation (decoupled from v1 to keep both loaders
    independent in case v1 changes)."""
    rows: list[dict] = []
    for path in LEDGER_PATHS:
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        continue
        except Exception:
            continue
    return rows


def run_g15_v2_real_verdict_mi() -> dict:
    """Filter control-flow rows; compute MI over real-verdict rows
    only."""
    rows = _read_ledger_rows()
    if not rows:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "no rows found in ledgers",
        }

    # Two passes: v1-style joint (everything) + v2-style joint
    # (real verdicts only). We report both so the comparison is
    # explicit.
    joint_all: dict[tuple, int] = {}
    joint_real: dict[tuple, int] = {}
    n_total = 0
    n_real = 0
    n_control = 0
    for r in rows:
        pid = _extract_plugin_id(r)
        kp = _extract_kill_pattern(r)
        if not pid or not kp:
            continue
        n_total += 1
        joint_all[(pid, kp)] = joint_all.get((pid, kp), 0) + 1
        if _is_control_flow(kp):
            n_control += 1
        else:
            n_real += 1
            joint_real[(pid, kp)] = joint_real.get((pid, kp), 0) + 1

    if n_real < MIN_PAIRED_ROWS:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "n_paired_total": n_total,
            "n_paired_real": n_real,
            "n_paired_control": n_control,
            "min_paired_real_needed": MIN_PAIRED_ROWS,
            "notes": (
                f"only {n_real} real-verdict paired observations "
                f"(after filtering {n_control} control-flow rows); "
                f"need >= {MIN_PAIRED_ROWS}"
            ),
        }

    mi_v1 = _shannon_mi(joint_all)
    mi_v2 = _shannon_mi(joint_real)

    delta_mi_nats = mi_v1["mi_nats"] - mi_v2["mi_nats"]

    if mi_v2["mi_nats"] >= MI_THRESHOLD_NATS:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"v2 MI (real verdicts only) = {mi_v2['mi_nats']:.4f} nats "
            f">= threshold {MI_THRESHOLD_NATS}. After removing "
            f"{n_control} control-flow rows from {n_total} total, "
            f"cross-plugin failure structure persists. "
            f"v1->v2 MI drop: {delta_mi_nats:.4f} nats "
            f"(v1={mi_v1['mi_nats']:.4f}, v2={mi_v2['mi_nats']:.4f}). "
            f"Underlying mathematical coupling is real."
        )
    else:
        verdict = "REJECTED"
        kp = "uncorrelated_residual_failures"
        notes = (
            f"v2 MI (real verdicts only) = {mi_v2['mi_nats']:.4f} nats "
            f"< threshold {MI_THRESHOLD_NATS}. The v1 signal "
            f"({mi_v1['mi_nats']:.4f} nats) was substrate-bookkeeping "
            f"circularity; after filtering {n_control} control-flow "
            f"rows, residual plugin-pattern coupling collapses. "
            f"Matches G15's expected_kill_pattern. ITER-13 self-audit "
            f"prediction confirmed."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "mi_v1_nats": round(mi_v1["mi_nats"], 4),
        "mi_v2_nats": round(mi_v2["mi_nats"], 4),
        "mi_v2_bits": round(mi_v2["mi_bits"], 4),
        "mi_v2_normalized": round(mi_v2["mi_normalized"], 4),
        "delta_mi_v1_to_v2_nats": round(delta_mi_nats, 4),
        "mi_threshold_nats": MI_THRESHOLD_NATS,
        "n_paired_total": n_total,
        "n_paired_real": n_real,
        "n_paired_control": n_control,
        "control_fraction": round(n_control / n_total, 4) if n_total else 0.0,
        "n_distinct_plugins_real": mi_v2["n_x"],
        "n_distinct_kill_patterns_real": mi_v2["n_y"],
        "notes": notes,
    }


class G15V2RealVerdictMILoader:
    plugin_id = "g15_cross_gen_mi"
    composition_id = "g15_v2_real_verdict_mi"
    description = (
        "Composition loader v2 for EREBOS-G15-* claims. Filters "
        "control-flow kill_patterns (_pending, _no_loader_registered, "
        "etc.) before computing MI. Closes ITER-13 finding doc "
        "follow-up #1."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g15_cross_gen_mi":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        # v2 fires when composed_id contains "v2" or "real_verdict";
        # default G15 emissions route to v1.
        return "v2" in composed_id.lower() or "real_verdict" in composed_id.lower()

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g15_v2_real_verdict_mi()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                "EREBOS-G15 v2 composition: Shannon MI(plugin_id; "
                "kill_pattern) on REAL-VERDICT rows only (control-flow "
                "rows filtered)."
            ),
            "data_source": (
                "Live read of charon/agents/{stygian,pollux,erebos}/"
                "state/kill_ledger.jsonl with control-flow suffix "
                "filter applied."
            ),
            "result": result,
            "notes": (
                "G15 v2 closes the self-audit loop from ITER-13. "
                "If v2 MI < threshold, the v1 signal was substrate-"
                "bookkeeping; if v2 MI >= threshold, real "
                "mathematical coupling remains."
            ),
        }


register(G15V2RealVerdictMILoader())
