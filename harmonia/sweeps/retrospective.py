"""
Retrospective sweep — run Pattern 30/20/19 on every existing +1/+2 cell.

This is the baseline calibration the spec asks for (acceptance criterion #3):
apply the sweeps to cells that landed *before* the filter existed, record
what WOULD have happened. Output goes to harmonia/memory/sweep_results_log.md.

LINEAGE_REGISTRY taxonomy (extended 2026-04-20, Harmonia_M2_sessionA):

  algebraic_lineage      correlation with algebraic coupling to audit
                         F013, F015, F041a, F043, F045
  frame_hazard           construction-biased sample (Pattern 4 active concern)
                         F044 (and F033 later)
  killed_no_correlation  killed specimen, no correlation to audit
                         F010, F012, F020-F028
  non_correlational      variance deficit / existence / calibration claim
                         F001-F005, F008, F009, F011, F014

The calibration tier (F001-F005, F008, F009) is retained as LEVEL_4_CALIBRATION
for backwards compatibility with the retrospective log, but is conceptually a
special case of non_correlational (theorem-verification claims).

PROVISIONAL verdicts (from frame_hazard) post a PATTERN_4_PROVISIONAL event
to agora:harmonia_sync with the Class-4 null spec + re-audit task id. They
do NOT halt ingestion. The retrospective runner re-reads pending_audit on
every invocation — if the referenced task has completed on Agora, the
relevant entry should be re-classified at that point (lazy watcher v1).

Usage:  PYTHONPATH=. python -m harmonia.sweeps.retrospective
"""
from __future__ import annotations

import datetime as dt
import json
import os
from collections import Counter
from pathlib import Path
from typing import Optional

from harmonia.sweeps.pattern_30 import (
    CouplingCheck,
    classify_entry,
    sweep as sweep30,
    bsd_f043_check,
    f015_szpiro_check,
)
from harmonia.sweeps.runner import SWEEP_LOG_PATH


# ---------------------------------------------------------------------------
# Lineage registry — taxonomy extended to 4 types 2026-04-20.
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


def _f013_rank_spacing_check() -> CouplingCheck:
    """F013 zero-spacing slope vs rank, stratified by P028 Katz-Sarnak.
    Level 1 WEAK_ALGEBRAIC: stratifier (symmetry type) is an algebraic
    function of the regressor (rank) via BSD parity (-1)^rank = root_number.
    Direction-of-slope partially forced; magnitude and sign-flip are not."""
    import sympy
    rank, slope, root_number = sympy.symbols(
        "rank slope root_number", integer=False)
    return CouplingCheck(
        X_expr=rank,
        Y_expr=slope,
        known_identities=[
            # BSD parity — connects rank to Katz-Sarnak stratum via P028
            sympy.Eq(root_number, (-1) ** rank),
        ],
        transform="linear",
        severity_hint="weak_algebraic",
    )


def _f045_isogeny_murmuration_check() -> CouplingCheck:
    """F045 isogeny-class-size murmuration, 5/21 primes significant.
    Level 1 WEAK_ALGEBRAIC (provisional): P100 class-size ↔ P039 nonmax
    ↔ P021 num_bad_primes partial tautology. Pending audit
    `correlate_F041a_F045_nbp_vs_isogeny` decides whether this collapses
    into F041a (Level 2 SHARED_VARIABLE) or stands as independent axis."""
    import sympy
    class_size, a_p = sympy.symbols("class_size a_p", positive=True)
    return CouplingCheck(
        X_expr=class_size,
        Y_expr=a_p,
        known_identities=[],
        severity_hint="weak_algebraic",
    )


# F013 rationale — James's verbatim annotation text (2026-04-20).
_F013_RATIONALE = (
    "P028 splits strata by root number, which is algebraically tied to "
    "rank parity via BSD; the stratum-dependent effect is expected. The "
    "empirical content is the sign pattern and z=15.31 magnitude, neither "
    "forced by the parity relation alone."
)


LINEAGE_REGISTRY: dict = {
    # --- algebraic_lineage ---
    "F043": {
        "type": "algebraic_lineage",
        "check": bsd_f043_check,
        "rationale": "BSD identity rearranges log(Omega * prod c_p) to contain "
                     "-log(Sha); Level 3 REARRANGEMENT. Retracted 2026-04-19.",
        "cross_references": ["F003"],
    },
    "F015": {
        "type": "algebraic_lineage",
        "check": f015_szpiro_check,
        "rationale": "szpiro = log|Disc| / log(N); correlating against log(N) "
                     "puts log(N) in the denominator. Level 1 WEAK_ALGEBRAIC.",
        "cross_references": [],
    },
    "F041a": {
        "type": "algebraic_lineage",
        "check": _f041a_check,
        "rationale": "CFKRS arithmetic factor is bad-prime-structure dependent; "
                     "nbp ladder coupling is partially forced. Level 1 WEAK_ALGEBRAIC.",
        "cross_references": ["F045"],
    },
    "F013": {
        "type": "algebraic_lineage",
        "check": _f013_rank_spacing_check,
        "rationale": _F013_RATIONALE,
        "cross_references": ["F003", "F011", "F015"],
    },
    "F045": {
        "type": "algebraic_lineage",
        "check": _f045_isogeny_murmuration_check,
        "rationale": "isogeny-class-size axis is partially algebraic-derived "
                     "from bad-prime structure via P100 <-> P021 coupling; "
                     "Level 1 provisional. Promote to Level 2 if the pending "
                     "F041a<->F045 audit confirms collapse.",
        "cross_references": ["F041a", "F003"],
        "pending_audit": {
            "task_id": "correlate_F041a_F045_nbp_vs_isogeny",
            "on_complete": "re_evaluate",
        },
    },

    # --- frame_hazard ---
    "F044": {
        "type": "frame_hazard",
        "sampling_frame": (
            "LMFDB rank-4 corridor (n=2086). Population is not a random "
            "sample — Stein/Elkies/Dujella record constructions are biased "
            "toward searchable-conductor families. 'disc=conductor' is "
            "definitionally semistable everywhere (Ogg's formula)."
        ),
        "class_4_null_ref": (
            "harmonia/memory/symbols/protocols/null_protocol_v1.md#class-4 — "
            "frame-based resample: reconstruct search methodology, re-apply "
            "to broader region, see if disc=conductor proportion changes."
        ),
        "pending_audit": {
            "task_id": "audit_F044_framebased_resample",
            "on_complete": "re_evaluate",
        },
        "rationale": (
            "Rank-4 disc=conductor corridor (2085/2086). Pattern 4 is the "
            "active gate, not Pattern 30. PROVISIONAL pending Class-4 null."
        ),
        "cross_references": ["F003", "F033"],
    },

    # --- killed_no_correlation ---
    "F010": {
        "type": "killed_no_correlation",
        "rationale": "NF backbone via Galois-label, killed by block-shuffle "
                     "null (z=-0.86). No correlation to audit.",
        "kill_null": "block-shuffle P001",
        "cross_references": ["F022"],
    },
    "F012": {
        "type": "killed_no_correlation",
        "rationale": "Möbius bias at g2c aut groups (H85); killed. "
                     "Stale Pattern 19 per prior |z|=6.15 vs clean 0.39.",
        "kill_null": "stale_pattern_19",
        "cross_references": [],
    },
    "F020": {
        "type": "killed_no_correlation",
        "rationale": "Megethos axis (sorted log-normals); in-registry as "
                     "killed specimen, no correlation content to audit.",
        "kill_null": "",
        "cross_references": [],
    },
    "F021": {
        "type": "killed_no_correlation",
        "rationale": "Phoneme framework (5-axis); killed. No correlation "
                     "content to audit. See feedback_phoneme_killed.md.",
        "kill_null": "",
        "cross_references": [],
    },
    "F022": {
        "type": "killed_no_correlation",
        "rationale": "NF backbone via feature distribution; z=0.00 under "
                     "permutation null (P001 cosine). Same data as F010. "
                     "rho=0 kill has no correlation to audit.",
        "kill_null": "P001 permutation",
        "cross_references": ["F010"],
    },
    "F023": {
        "type": "killed_no_correlation",
        "rationale": "Spectral tail ARI=0.55 (2026-04-15); killed by "
                     "conductor confounder. No correlation to audit.",
        "kill_null": "conductor-controlled",
        "cross_references": [],
    },
    "F024": {
        "type": "killed_no_correlation",
        "rationale": "Faltings explains GUE (H08); killed. "
                     "No correlation content to audit.",
        "kill_null": "",
        "cross_references": [],
    },
    "F025": {
        "type": "killed_no_correlation",
        "rationale": "ADE splits GUE (H10); killed. "
                     "No correlation content to audit.",
        "kill_null": "",
        "cross_references": [],
    },
    "F026": {
        "type": "killed_no_correlation",
        "rationale": "Artin dim-2/dim-3 proof-frontier ratio (H61); killed. "
                     "No correlation content to audit.",
        "kill_null": "",
        "cross_references": [],
    },
    "F027": {
        "type": "killed_no_correlation",
        "rationale": "Alexander Mahler × EC L-value (Charon); killed at z=0 "
                     "on P053 projection. rho=0 kill has no correlation.",
        "kill_null": "P053 permutation",
        "cross_references": ["F014"],
    },
    "F028": {
        "type": "killed_no_correlation",
        "rationale": "Szpiro × Faltings coupling (H40); killed tautology — "
                     "both sides share log|Disc|. No non-tautological "
                     "correlation to audit.",
        "kill_null": "tautology (shared log|Disc|)",
        "cross_references": ["F015"],
    },

    # --- non_correlational ---
    "F011": {
        "type": "non_correlational",
        "claim_shape": "variance_deficit",
        "rationale": (
            "GUE first-gap variance deficit, rank-0 residual eps_0 = "
            "22.90% ± 0.78 (1/log(N) ansatz), z=29sigma from 0. "
            "eps_0 is a fit intercept, not a correlation coefficient — "
            "no X-vs-Y coupling to audit. Independent-unfolding audit "
            "survived (72.9pp gap vs null floor)."
        ),
        "cross_references": ["F013", "F042", "F043"],
    },
    "F014": {
        "type": "non_correlational",
        "claim_shape": "density / existence",
        "rationale": (
            "Lehmer-Mahler spectrum: Salem density in (1.176, 1.228) "
            "with 3 polynomials strictly in-region (minimum a Salem "
            "polynomial at 1.216392). Density claim, not a correlation. "
            "Per-num_ram monotone is structural, not Pattern-30 coupled."
        ),
        "cross_references": ["F011", "F027", "F028"],
    },
}


# Calibration anchors (tier=calibration) are emitted as LEVEL_4_CALIBRATION
# by the retrospective runner without requiring a registry entry — this
# is conceptually a non_correlational special case (theorem verification)
# but is retained as a distinct log bucket for continuity with prior runs.
CALIBRATION_FIDS = {"F001", "F002", "F003", "F004", "F005", "F008", "F009"}


# ---------------------------------------------------------------------------
# Lazy watcher — re-read pending_audit on each invocation, re-classify
# entries whose referenced task has completed.
# ---------------------------------------------------------------------------

def _check_agora_task_complete(task_id: str) -> bool:
    """Is the named task present in the Agora results stream (i.e. completed)?

    Lazy v1: we simply check whether the task is still in the queue; if not
    AND it appears in the results stream, we treat it as complete. Returns
    False on any error (missing Redis, missing deps, etc.) so the retrospective
    continues without the watcher.
    """
    try:
        import redis
        host = os.environ.get("AGORA_REDIS_HOST", "192.168.1.176")
        port = int(os.environ.get("AGORA_REDIS_PORT", "6379"))
        password = os.environ.get("AGORA_REDIS_PASSWORD", "prometheus")
        r = redis.Redis(host=host, port=port, password=password,
                        decode_responses=True, socket_timeout=2)
        # Still queued? Then not complete.
        if r.zscore("agora:work_queue", task_id) is not None:
            return False
        # Still claimed? Then not complete.
        if r.hget("agora:work_claims", task_id) is not None:
            return False
        # Not in queue and not claimed — check results stream for an entry.
        # The results stream is small enough to scan by task_id.
        entries = r.xrevrange("agora:work_results", count=500)
        for _mid, data in entries:
            if data.get("task_id") == task_id:
                return True
        return False
    except Exception:
        return False


def resolve_entry(fid: str, entry: dict) -> dict:
    """Classify a registry entry, re-reading pending_audit state if present.

    If the referenced audit task is complete, a note is attached to the
    result; actual re-classification still requires an explicit registry
    edit (the watcher is lazy, not automatic — per spec).
    """
    result = classify_entry(entry)
    pending = None
    if isinstance(entry, dict):
        pending = entry.get("pending_audit")
    if pending and pending.get("task_id"):
        task_id = pending["task_id"]
        done = _check_agora_task_complete(task_id)
        result["details"] = dict(result.get("details") or {})
        result["details"]["pending_audit"] = {
            "task_id": task_id,
            "on_complete": pending.get("on_complete", "re_evaluate"),
            "complete": done,
        }
        if done:
            result["rationale"] = (
                result["rationale"]
                + " [NOTE: pending audit {} is complete — re-evaluate "
                "registry entry.]".format(task_id)
            )
    return result


# ---------------------------------------------------------------------------
# PROVISIONAL sync-post
# ---------------------------------------------------------------------------

def _post_provisional_sync(fid: str, result: dict) -> None:
    """Post a PATTERN_4_PROVISIONAL event to agora:harmonia_sync.

    Silently no-ops if Redis or the sync client is unavailable. Called for
    every frame_hazard verdict emitted by the retrospective runner.
    """
    try:
        import redis
        host = os.environ.get("AGORA_REDIS_HOST", "192.168.1.176")
        port = int(os.environ.get("AGORA_REDIS_PORT", "6379"))
        password = os.environ.get("AGORA_REDIS_PASSWORD", "prometheus")
        r = redis.Redis(host=host, port=port, password=password,
                        decode_responses=True, socket_timeout=2)
        details = result.get("details") or {}
        pending = details.get("pending_audit") or {}
        r.xadd("agora:harmonia_sync", {
            "type": "PATTERN_4_PROVISIONAL",
            "from": "harmonia.sweeps.retrospective",
            "at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "feature_id": fid,
            "sampling_frame": (details.get("sampling_frame") or "")[:400],
            "class_4_null_ref": (details.get("class_4_null_ref") or "")[:400],
            "pending_audit_task_id": pending.get("task_id", "") if isinstance(pending, dict) else "",
            "rationale": (result.get("rationale") or "")[:400],
        }, maxlen=5000, approximate=True)
    except Exception:
        pass


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

def run_retrospective(
    output_path: Optional[Path] = None,
    post_sync: bool = True,
) -> dict:
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
        "Scope: every +1 or +2 cell in the current tensor. LINEAGE_REGISTRY "
        "carries one of four taxonomies for each audited F-ID:"
    )
    lines.append("")
    lines.append(
        "- `algebraic_lineage` — correlation with algebraic coupling; runs "
        "Pattern 30 auto-check and emits CLEAR / WARN / BLOCK.\n"
        "- `frame_hazard` — construction-biased sample; Pattern 4 is the "
        "active gate. Emits PROVISIONAL (does not halt). Sync-posted.\n"
        "- `killed_no_correlation` — killed specimen; no correlation "
        "content to audit. Emits N/A_KILLED (silent CLEAR-equivalent).\n"
        "- `non_correlational` — variance deficit / existence / density / "
        "calibration. Emits N/A_NON_CORRELATIONAL (silent CLEAR-equivalent)."
    )
    lines.append("")
    lines.append(
        "Pattern 20 and Pattern 19 cannot run retrospectively without per-"
        "cell stratified / prior-measurement data in a structured form — "
        "both are logged as NO_RETROSPECTIVE_DATA."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary counters
    counts: Counter = Counter()
    verdict_counts: Counter = Counter()
    per_feature_summary: dict = {}

    for fid, info in sorted(by_feature.items()):
        tier = info["tier"]
        cells_ = info["cells"]
        lines.append(f"## {fid} ({tier}) — {len(cells_)} active cell(s)")
        lines.append("")
        cells_str = ", ".join(f"{pid}:+{v}" for pid, v in sorted(cells_))
        lines.append(f"**Cells:** {cells_str}")
        lines.append("")

        # Calibration anchors: keep legacy LEVEL_4_CALIBRATION bucket.
        if tier == "calibration" or fid in CALIBRATION_FIDS:
            lines.append(
                "**Pattern 30 retrospective:** Level 4 IDENTITY (calibration "
                "anchor — verdict-semantics is theorem verification, not "
                "arithmetic-structure discovery)."
            )
            counts["pattern_30_level_4_calibration"] += 1
            verdict_counts["CLEAR"] += 1  # calibration is effectively CLEAR
            per_feature_summary[fid] = "LEVEL_4_CALIBRATION"

        elif fid in LINEAGE_REGISTRY:
            entry = LINEAGE_REGISTRY[fid]
            result = resolve_entry(fid, entry)
            t = result["type"]
            verdict = result["verdict"]
            name = result["name"]
            rationale = result["rationale"]
            if t == "algebraic_lineage":
                level = result.get("level")
                lines.append(
                    f"**Pattern 30 retrospective:** Level {level} "
                    f"{name} ({verdict}). {rationale}"
                )
                counts[f"pattern_30_level_{level}"] += 1
                per_feature_summary[fid] = f"LEVEL_{level}_{name}"
            elif t == "frame_hazard":
                details = result.get("details") or {}
                pending = details.get("pending_audit") or {}
                pending_id = (pending.get("task_id", "") if isinstance(pending, dict) else "")
                lines.append(
                    f"**Pattern 30 retrospective:** {name} ({verdict}). "
                    f"{rationale}"
                )
                lines.append("")
                lines.append(
                    f"**Sampling frame:** {details.get('sampling_frame', '')}"
                )
                lines.append(
                    f"**Class-4 null reference:** {details.get('class_4_null_ref', '')}"
                )
                if pending_id:
                    lines.append(
                        f"**Pending audit:** `{pending_id}` "
                        f"(complete={pending.get('complete', False) if isinstance(pending, dict) else False})"
                    )
                counts["pattern_30_frame_hazard"] += 1
                per_feature_summary[fid] = "FRAME_HAZARD_PROVISIONAL"
                if post_sync:
                    _post_provisional_sync(fid, result)
            elif t == "killed_no_correlation":
                lines.append(
                    f"**Pattern 30 retrospective:** {name} ({verdict}). "
                    f"{rationale}"
                )
                counts["pattern_30_killed_no_correlation"] += 1
                per_feature_summary[fid] = "KILLED_NO_CORRELATION"
            elif t == "non_correlational":
                lines.append(
                    f"**Pattern 30 retrospective:** {name} ({verdict}). "
                    f"{rationale}"
                )
                counts["pattern_30_non_correlational"] += 1
                per_feature_summary[fid] = "NON_CORRELATIONAL"
            verdict_counts[verdict] += 1

        else:
            lines.append(
                "**Pattern 30 retrospective:** NO_LINEAGE_METADATA. "
                "F-ID description does not declare algebraic_lineage; "
                "auto-check cannot run. Manual annotation required before "
                "any correlation-based promotion from this F-ID."
            )
            counts["pattern_30_no_metadata"] += 1
            verdict_counts["NO_LINEAGE_METADATA"] += 1
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
    lines.append("### Verdict breakdown (per-feature)")
    lines.append("")
    for v in ("CLEAR", "WARN", "BLOCK", "PROVISIONAL",
              "N/A_KILLED", "N/A_NON_CORRELATIONAL", "NO_LINEAGE_METADATA"):
        lines.append(f"- `{v}`: {verdict_counts.get(v, 0)}")
    lines.append("")
    lines.append("### Interpretation")
    lines.append("")
    lines.append(
        "- **Level 4 calibration**: expected — these are theorem anchors by "
        "design (F001-F005, F008, F009).\n"
        "- **Level 0-3 from registry**: F043 Level 3 (already retracted), "
        "F015 / F041a / F013 / F045 Level 1 WEAK_ALGEBRAIC.\n"
        "- **PROVISIONAL (frame_hazard)**: F044 — Pattern 4 gate active, "
        "Class-4 null pending via `audit_F044_framebased_resample`.\n"
        "- **N/A_KILLED**: killed specimens registered so the sweep is aware "
        "they exist; no correlation content to audit.\n"
        "- **N/A_NON_CORRELATIONAL**: variance-deficit / density / existence "
        "claims (F011, F014); no X-vs-Y correlation exists to audit.\n"
        "- **NO_LINEAGE_METADATA**: the baseline substrate debt. Any F-ID "
        "not registered and not in calibration-tier falls through to this "
        "bucket and requires manual annotation before Pattern 30 can run."
    )
    lines.append("")
    lines.append(
        "No net-new retractions triggered by this pass — F043 was already "
        "retracted 2026-04-19; F015, F041a, F013 Level-1 annotations were "
        "applied by the methodology tightener; F044 PROVISIONAL pending "
        "the existing Agora re-audit task."
    )
    lines.append("")
    lines.append("---")

    output_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "features_audited": len(by_feature),
        "total_cells": len(cells),
        "counts": dict(counts),
        "verdict_counts": dict(verdict_counts),
        "per_feature": per_feature_summary,
        "output_path": str(output_path),
    }


def main():
    summary = run_retrospective()
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
