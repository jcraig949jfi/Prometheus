"""
Retrospective sweep — run Pattern 30/20/19 on every existing +1/+2 cell.

This is the baseline calibration the spec asks for (acceptance criterion #3):
apply the sweeps to cells that landed *before* the filter existed, record
what WOULD have happened. Output goes to harmonia/memory/sweep_results_log.md.

For v1 we have full algebraic lineage only for the three anchor cases:
  F043 — Level 3 REARRANGEMENT (already retracted manually)
  F015 — Level 1 WEAK_ALGEBRAIC (caller-declared; already annotated)
  F041a — Level 1 partial (CFKRS arithmetic factor; caller-declared)

The remaining ~50 non-calibration non-tautology cells don't yet carry
algebraic_lineage metadata on their F-IDs. The retrospective sweep
logs those as NO_LINEAGE_METADATA — this is baseline data on how much
epistemic debt the substrate is carrying, not a proxy for correctness.

Usage:  PYTHONPATH=. python -m harmonia.sweeps.retrospective
"""
from __future__ import annotations

import datetime as dt
import json
import os
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from harmonia.sweeps.pattern_30 import (
    CouplingCheck,
    sweep as sweep30,
    bsd_f043_check,
    f015_szpiro_check,
)
from harmonia.sweeps.runner import sweep_signature, SWEEP_LOG_PATH


# ---------------------------------------------------------------------------
# Lineage registry — what we know about F-IDs that have been manually
# annotated with algebraic lineage so far. Extend as new F-IDs declare.
# ---------------------------------------------------------------------------

def _f041a_check() -> CouplingCheck:
    """F041a: CFKRS arithmetic factor is bad-prime-structure dependent —
    Pattern 5 gate and Pattern 30 gate collapse to the same gate. Declared
    weak_algebraic by methodology tightener b57f4afe."""
    import sympy
    nbp, k = sympy.symbols("nbp k", positive=True)
    return CouplingCheck(
        X_expr=nbp,
        Y_expr=sympy.symbols("moment_slope"),
        known_identities=[],
        severity_hint="weak_algebraic",
    )


LINEAGE_REGISTRY = {
    "F043": bsd_f043_check,        # Level 3 REARRANGEMENT
    "F015": f015_szpiro_check,     # Level 1 WEAK_ALGEBRAIC
    "F041a": _f041a_check,         # Level 1 WEAK_ALGEBRAIC
}


# ---------------------------------------------------------------------------
# Pull tensor state (from disk artifact, not Redis — idempotent)
# ---------------------------------------------------------------------------

def _load_tensor():
    import numpy as np
    root = Path(__file__).resolve().parent.parent / "memory"
    npz = np.load(root / "landscape_tensor.npz", allow_pickle=True)
    manifest = json.loads((root / "landscape_manifest.json").read_text(
        encoding="utf-8"))
    return npz["T"], manifest


def enumerate_active_cells():
    """Yield (feature_id, projection_id, verdict_int, feature_tier) for every
    +1 or +2 cell in the current tensor."""
    T, manifest = _load_tensor()
    features = manifest.get("features", [])
    projections = manifest.get("projections", [])
    for i, f in enumerate(features):
        fid = f.get("id")
        tier = f.get("tier", "unknown")
        if fid is None:
            continue
        for j, p in enumerate(projections):
            pid = p.get("id")
            if pid is None:
                continue
            v = int(T[i, j])
            if v >= 1:
                yield fid, pid, v, tier


# ---------------------------------------------------------------------------
# Retrospective runner
# ---------------------------------------------------------------------------

def run_retrospective(output_path: Optional[Path] = None) -> dict:
    output_path = output_path or SWEEP_LOG_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cells = list(enumerate_active_cells())
    by_feature: dict = {}
    for fid, pid, v, tier in cells:
        by_feature.setdefault(fid, {"tier": tier, "cells": []})
        by_feature[fid]["cells"].append((pid, v))

    lines = []
    lines.append("# Sweep Results Log (Pattern 30/20/19 retrospective)")
    lines.append("")
    lines.append(
        "Append-only record of every sweep verdict. "
        "Retrospective baseline created by `harmonia/sweeps/retrospective.py` "
        f"on {dt.datetime.now(dt.timezone.utc).isoformat()}."
    )
    lines.append("")
    lines.append(
        "Scope: every +1 or +2 cell in the current tensor. For F-IDs without "
        "algebraic_lineage metadata (most of them), Pattern 30 auto-check "
        "cannot run — this is logged as NO_LINEAGE_METADATA, which is the "
        "baseline epistemic debt, not a sweep pass. Pattern 20 and Pattern 19 "
        "cannot run retrospectively without per-cell stratified / prior-"
        "measurement data in a structured form — both are logged as "
        "NO_RETROSPECTIVE_DATA."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary counters
    counts: Counter = Counter()
    per_feature_summary: dict = {}

    for fid, info in sorted(by_feature.items()):
        tier = info["tier"]
        cells_ = info["cells"]
        lines.append(f"## {fid} ({tier}) — {len(cells_)} active cell(s)")
        lines.append("")
        cells_str = ", ".join(f"{pid}:+{v}" for pid, v in sorted(cells_))
        lines.append(f"**Cells:** {cells_str}")
        lines.append("")

        # Tier-based Pattern 30 interpretation
        if tier == "calibration":
            # Calibration anchors are Level 4 by design
            lines.append(
                "**Pattern 30 retrospective:** Level 4 IDENTITY (calibration "
                "anchor — verdict-semantics is theorem verification, not "
                "arithmetic-structure discovery)."
            )
            counts["pattern_30_level_4_calibration"] += 1
            per_feature_summary[fid] = "LEVEL_4_CALIBRATION"

        elif fid in LINEAGE_REGISTRY:
            chk = LINEAGE_REGISTRY[fid]()
            result = sweep30(chk)
            lines.append(
                f"**Pattern 30 retrospective:** Level {result.level} "
                f"{result.name} ({result.verdict}). {result.rationale}"
            )
            counts[f"pattern_30_level_{result.level}"] += 1
            per_feature_summary[fid] = f"LEVEL_{result.level}_{result.name}"

        else:
            lines.append(
                "**Pattern 30 retrospective:** NO_LINEAGE_METADATA. "
                "F-ID description does not declare algebraic_lineage; "
                "auto-check cannot run. Manual annotation required before "
                "any correlation-based promotion from this F-ID."
            )
            counts["pattern_30_no_metadata"] += 1
            per_feature_summary[fid] = "NO_LINEAGE_METADATA"

        lines.append(
            "**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. "
            "Stratified companion stats not structurally recorded in tensor "
            "manifest; run at next re-audit."
        )
        counts["pattern_20_no_data"] += 1

        lines.append(
            "**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. "
            "Prior-signature comparison needs signals.specimens history "
            "query, not done in this pass."
        )
        counts["pattern_19_no_data"] += 1
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Features audited: {len(by_feature)}")
    lines.append(f"- Total +1/+2 cells: {len(cells)}")
    lines.append("")
    lines.append("### Pattern 30 distribution")
    lines.append("")
    for k in sorted(counts):
        if k.startswith("pattern_30_"):
            lines.append(f"- `{k}`: {counts[k]}")
    lines.append("")
    lines.append("### Interpretation")
    lines.append("")
    lines.append(
        "- **Level 4 calibration**: expected — these are theorem anchors by "
        "design (F001-F005, F008, F009).\n"
        "- **Level 0-3 from registry**: F043 Level 3 (already retracted), "
        "F015 and F041a Level 1 (already annotated in descriptions).\n"
        "- **NO_LINEAGE_METADATA**: the baseline substrate debt. Every "
        "non-calibration F-ID that uses correlation should eventually have "
        "a declared `algebraic_lineage` block in its description. Until "
        "then, Pattern 30 auto-check degrades to manual gate."
    )
    lines.append("")
    lines.append(
        "No net-new retractions triggered by this pass — F043 was already "
        "retracted 2026-04-19; F015 and F041a Level-1 annotations were "
        "already applied by the methodology tightener."
    )
    lines.append("")
    lines.append("---")

    output_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "features_audited": len(by_feature),
        "total_cells": len(cells),
        "counts": dict(counts),
        "per_feature": per_feature_summary,
        "output_path": str(output_path),
    }


def main():
    summary = run_retrospective()
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
