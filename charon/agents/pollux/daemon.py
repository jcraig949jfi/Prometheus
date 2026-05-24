"""Pollux — numerical-coincidence scanner (Charon swarm v0.5).

MVP scope: per tick, pick one pair of Mossinghoff Mahler-measure
subsets, compute Spearman correlation BEFORE and AFTER mean-spacing
normalization (per feedback_scale_vs_shape: "for ANY gap comparison,
test mean-spacing normalization FIRST"), emit a kill_ledger row in
Theseus's shape so Hecate's gradient archaeology consumes it.

Three outcomes encoded as kill_patterns:
  - "pollux_sign_flips_under_normalization"  -> structural artifact;
    the raw correlation was scale-driven, not shape-driven.
  - "pollux_correlation_survives_normalization" -> the pair carries
    real shape signal worth promoting to Stygian for v10 battery.
  - "pollux_no_correlation_observed" -> null result; recorded for
    decay tracking.

generator_id="pollux" is the second non-Theseus operator class to
populate the kill_ledger (Stygian is the first). Cross-generator MI
audit in Hecate becomes meaningful as Pollux/Stygian/Theseus build
up parallel coverage of the kill_pattern space.

Future scope (v0.6+):
  - Cross-database pairs (Mahler vs OEIS sleeping vs knots vs genus2)
  - Prime-power detrending before correlation (per project_microscope:
    "96%+ of cross-dataset structure is primes; detrend before testing")
  - Battery-call hook so Pollux can pre-validate kills with Stygian's
    executor before emitting (avoids inflating Hecate's MI with
    Pollux-self-generated noise)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from charon.agents._base import CharonAgent
from harmonia.agents._base import REPO_ROOT


# Where Pollux's kill_ledger rows land. Hecate's LEDGER_CANDIDATES is
# updated in parallel to merge this source alongside Theseus + Stygian.
POLLUX_KILL_LEDGER = (
    REPO_ROOT / "charon" / "agents" / "pollux" / "state" / "kill_ledger.jsonl"
)

# Test-pair rotation. Each tick scans ONE pair; pairs round-robin via
# rotation_idx state. Pair definitions are (subset_a_spec, subset_b_spec)
# where each spec is a dict consumed by _load_subset().
TEST_PAIRS: list[dict] = [
    {
        "name": "deg10_vs_deg12",
        "a": {"kind": "mahler_by_degree", "degree": 10},
        "b": {"kind": "mahler_by_degree", "degree": 12},
        "rationale": "Adjacent-degree Mahler subsets; expect minimal correlation if Mahler measures are scale-independent.",
    },
    {
        "name": "deg14_vs_deg16",
        "a": {"kind": "mahler_by_degree", "degree": 14},
        "b": {"kind": "mahler_by_degree", "degree": 16},
        "rationale": "Higher-degree adjacent pair; tests whether correlation pattern persists at scale.",
    },
    {
        "name": "salem_vs_pisot",
        "a": {"kind": "mahler_by_class", "salem_class": True},
        "b": {"kind": "mahler_by_class", "salem_class": False},
        "rationale": "Salem-class vs non-Salem; tests whether class membership shapes the M distribution distinctly.",
    },
    {
        "name": "smyth_extremal_vs_rest",
        "a": {"kind": "mahler_smyth_extremal"},
        "b": {"kind": "mahler_non_smyth"},
        "rationale": "Smyth-extremal floor vs everything-else; tests floor-vs-interior shape contrast.",
    },
]

# Correlation thresholds for verdict classification
CORR_SIGNIFICANT = 0.30  # |spearman| >= this is "real correlation"
CORR_FLIPPED_DELTA = 0.20  # post-norm |corr| < raw |corr| - this AND sign flips


def _load_subset(spec: dict) -> tuple[list[float], str]:
    """Load a Mahler-measure subset per spec. Returns (values, description).
    Returns ([], err_msg) on failure.

    Imports mahler lazily to avoid PARI init noise unless Pollux fires.
    """
    try:
        from prometheus_math.databases.mahler import (
            smallest_known, all_below, smyth_extremal,
        )
    except Exception as e:
        return [], f"mahler import failed: {e}"

    kind = spec.get("kind")
    try:
        if kind == "mahler_by_degree":
            deg = spec["degree"]
            entries = [e for e in all_below(2.0) if e.get("degree") == deg]
            values = [
                float(e["mahler_measure"]) for e in entries
                if e.get("mahler_measure") is not None
            ]
            return values, f"Mossinghoff entries at degree {deg} (n={len(values)})"
        elif kind == "mahler_by_class":
            salem = spec.get("salem_class", True)
            entries = all_below(2.0)
            values = [
                float(e["mahler_measure"]) for e in entries
                if e.get("mahler_measure") is not None
                and bool(e.get("salem_class")) == salem
            ]
            label = "Salem-class" if salem else "non-Salem"
            return values, f"Mossinghoff {label} entries (n={len(values)})"
        elif kind == "mahler_smyth_extremal":
            entries = smyth_extremal()
            values = [
                float(e["mahler_measure"]) for e in entries
                if e.get("mahler_measure") is not None
            ]
            return values, f"Smyth-extremal entries (n={len(values)})"
        elif kind == "mahler_non_smyth":
            entries = [
                e for e in all_below(2.0)
                if not e.get("is_smyth_extremal")
                and e.get("mahler_measure") is not None
            ]
            values = [float(e["mahler_measure"]) for e in entries]
            return values, f"Non-Smyth-extremal entries (n={len(values)})"
        else:
            return [], f"unknown subset kind: {kind}"
    except Exception as e:
        return [], f"subset load failed: {e}"


def _spearman(xs: list[float], ys: list[float]) -> Optional[float]:
    """Pure-python Spearman rank correlation. Returns None if inputs
    are too short or degenerate. No scipy dep so Pollux stays light."""
    n = min(len(xs), len(ys))
    if n < 10:
        return None
    xs, ys = xs[:n], ys[:n]
    # Rank both
    def _rank(vs):
        sorted_idx = sorted(range(len(vs)), key=lambda i: vs[i])
        ranks = [0.0] * len(vs)
        for r, i in enumerate(sorted_idx):
            ranks[i] = float(r)
        return ranks
    rx = _rank(xs)
    ry = _rank(ys)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = sum((rx[i] - mx) ** 2 for i in range(n)) ** 0.5
    dy = sum((ry[i] - my) ** 2 for i in range(n)) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def _mean_spacing_normalize(vs: list[float]) -> list[float]:
    """Sort, take consecutive gaps, normalize by mean gap. Returns the
    normalized-gap series. Length = len(vs) - 1. This is the
    feedback_scale_vs_shape transform that strips scale-driven
    correlation."""
    if len(vs) < 2:
        return []
    sv = sorted(vs)
    gaps = [sv[i + 1] - sv[i] for i in range(len(sv) - 1)]
    mean_gap = sum(gaps) / max(1, len(gaps))
    if mean_gap == 0:
        return gaps
    return [g / mean_gap for g in gaps]


def _classify(corr_raw: Optional[float], corr_norm: Optional[float]) -> str:
    """Map (raw_corr, normalized_corr) to a kill_pattern label."""
    if corr_raw is None or corr_norm is None:
        return "pollux_correlation_unmeasurable"
    raw_sig = abs(corr_raw) >= CORR_SIGNIFICANT
    norm_sig = abs(corr_norm) >= CORR_SIGNIFICANT
    sign_flips = (corr_raw * corr_norm) < 0
    if raw_sig and sign_flips and abs(corr_norm) < abs(corr_raw) - CORR_FLIPPED_DELTA:
        return "pollux_sign_flips_under_normalization"
    if raw_sig and norm_sig and (corr_raw * corr_norm) > 0:
        return "pollux_correlation_survives_normalization"
    if not raw_sig:
        return "pollux_no_correlation_observed"
    # Borderline cases: raw significant but normalization weakens / sign-flips
    # without crossing the delta threshold
    return "pollux_correlation_attenuates_under_normalization"


def _record_id(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _emit_kill_ledger_row(row: dict) -> Path:
    POLLUX_KILL_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with POLLUX_KILL_LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return POLLUX_KILL_LEDGER


class PolluxAgent(CharonAgent):
    """Numerical-coincidence scanner. Per-tick: pick one pair, compute
    pre/post-normalization correlation, emit kill_ledger row."""

    name = "Pollux"
    role = "numerical-coincidence scanner (cross-database correlation under normalization)"

    def self_generate_backlog(self) -> list[dict]:
        """Always one item: scan the next pair in rotation."""
        idx = int(self.load_state("pair_rotation_idx", 0) or 0)
        pair = TEST_PAIRS[idx % len(TEST_PAIRS)]
        return [{"pair": pair, "idx": idx}]

    def _pick_and_advance(self) -> dict:
        idx = int(self.load_state("pair_rotation_idx", 0) or 0)
        pair = TEST_PAIRS[idx % len(TEST_PAIRS)]
        self.save_state("pair_rotation_idx", (idx + 1) % len(TEST_PAIRS))
        return pair

    def _emit_artifact(self, pair: dict, result: dict) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"scan_{pair['name']}_{utc}.md"
        body_lines = [
            f"# Pollux scan -- {pair['name']}",
            "",
            f"- emitted_at: {datetime.now(timezone.utc).isoformat()}",
            f"- emitted_by: Pollux (charon/agents/pollux/daemon.py)",
            f"- rationale: {pair['rationale']}",
            f"- subset_a: {result['subset_a_desc']}",
            f"- subset_b: {result['subset_b_desc']}",
            f"- n_paired: {result['n_paired']}",
            "",
            "## Correlation under mean-spacing normalization",
            "",
            f"- raw spearman: **{result['corr_raw']}**",
            f"- normalized spearman: **{result['corr_norm']}**",
            f"- kill_pattern: `{result['kill_pattern']}`",
            f"- verdict: {result['verdict']}",
            "",
            "Per feedback_scale_vs_shape: any raw correlation that vanishes "
            "or sign-flips under mean-spacing normalization is scale-driven, "
            "not shape-driven. Pollux flags both and emits the kill_pattern "
            "for Hecate's clustering.",
            "",
        ]
        return self.write_artifact(fname, "\n".join(body_lines))

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "pair_scanned": None,
            "corr_raw": None,
            "corr_norm": None,
            "kill_pattern": None,
            "verdict": None,
            "kill_ledger_row_id": None,
        }
        pair = self._pick_and_advance()
        stats["pair_scanned"] = pair["name"]

        if dry_run:
            stats["items_processed"] += 1
            return stats

        a_vals, a_desc = _load_subset(pair["a"])
        b_vals, b_desc = _load_subset(pair["b"])
        if not a_vals or not b_vals:
            stats["errors"] += 1
            stats["verdict"] = f"subset_load_failed: a={len(a_vals)} b={len(b_vals)}"
            # Still emit a kill_ledger row so silent ticks don't happen
            self._emit_short_circuit(pair, stats["verdict"])
            return stats

        # Truncate to shared length so spearman has paired indices
        n = min(len(a_vals), len(b_vals))
        a_paired = sorted(a_vals)[:n]
        b_paired = sorted(b_vals)[:n]

        corr_raw = _spearman(a_paired, b_paired)
        a_norm = _mean_spacing_normalize(a_paired)
        b_norm = _mean_spacing_normalize(b_paired)
        n_norm = min(len(a_norm), len(b_norm))
        corr_norm = _spearman(a_norm[:n_norm], b_norm[:n_norm]) if n_norm >= 10 else None

        kp = _classify(corr_raw, corr_norm)
        verdict = (
            "PROMOTED" if kp == "pollux_correlation_survives_normalization"
            else "REJECTED" if kp in (
                "pollux_sign_flips_under_normalization",
                "pollux_no_correlation_observed",
            )
            else "UNVERIFIED"
        )
        stats["corr_raw"] = round(corr_raw, 4) if corr_raw is not None else None
        stats["corr_norm"] = round(corr_norm, 4) if corr_norm is not None else None
        stats["kill_pattern"] = kp
        stats["verdict"] = verdict

        result = {
            "subset_a_desc": a_desc,
            "subset_b_desc": b_desc,
            "n_paired": n,
            "corr_raw": stats["corr_raw"],
            "corr_norm": stats["corr_norm"],
            "kill_pattern": kp,
            "verdict": verdict,
        }
        try:
            out = self._emit_artifact(pair, result)
            stats["artifacts_written"] += 1
        except Exception as e:
            self.log.exception(f"artifact emit failed: {e}")
            stats["errors"] += 1

        # Emit kill_ledger row in Theseus shape so Hecate consumes uniformly
        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            "pair_name": pair["name"],
            "subset_a": pair["a"],
            "subset_b": pair["b"],
            "corr_raw": stats["corr_raw"],
            "corr_norm": stats["corr_norm"],
            "kill_pattern": kp,
            "emitted_at": now_iso,
        }
        rid = _record_id(payload)
        row = {
            "batch_id": f"pollux-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            "record_id": rid,
            "canonical_claim_text": (
                f"Pollux scan {pair['name']}: spearman raw={stats['corr_raw']}, "
                f"normalized={stats['corr_norm']} on n={n} paired Mahler measures "
                f"({a_desc} vs {b_desc})"
            ),
            "claim_kind": "pollux_correlation_scan",
            "claim_payload": payload,
            "convergence_status": "exact",
            "diversity_score": None,
            "emitted_at": now_iso,
            "extras": {
                "rationale": pair["rationale"],
                "subset_a_desc": a_desc,
                "subset_b_desc": b_desc,
            },
            "generator_id": "pollux",
            "info_density": None,
            "kill_pattern": kp,
            "kill_vector": {
                "corr_raw": stats["corr_raw"],
                "corr_norm": stats["corr_norm"],
                "n_paired": n,
            },
            "method": "spearman_with_meanspacing_normalization",
            "novelty_estimate": None,
            "parent_record_id": None,
            "precision_dps": 4,
            "sigma_claim_id": None,
            "sigma_symbol_ref": None,
            "step_trace": None,
            "training_weight": None,
            "verdict": verdict,
        }
        _emit_kill_ledger_row(row)
        stats["kill_ledger_row_id"] = rid
        stats["items_processed"] += 1
        self.log_work(
            "pollux_tick_complete",
            summary=(
                f"pair={pair['name']} kp={kp} verdict={verdict} "
                f"raw={stats['corr_raw']} norm={stats['corr_norm']}"
            ),
            success=stats["errors"] == 0,
        )
        return stats

    def _emit_short_circuit(self, pair: dict, reason: str) -> None:
        """Emit an UNVERIFIED kill_ledger row when scan can't run.
        SELF_AUDIT_NULL discipline -- silent ticks forbidden."""
        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            "pair_name": pair["name"],
            "skip_reason": reason,
            "emitted_at": now_iso,
        }
        rid = _record_id(payload)
        row = {
            "batch_id": f"pollux-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            "record_id": rid,
            "canonical_claim_text": f"Pollux scan {pair['name']} aborted: {reason}",
            "claim_kind": "pollux_correlation_scan",
            "claim_payload": payload,
            "convergence_status": "skipped",
            "diversity_score": None,
            "emitted_at": now_iso,
            "extras": {},
            "generator_id": "pollux",
            "info_density": None,
            "kill_pattern": "pollux_scan_aborted",
            "kill_vector": None,
            "method": "spearman_with_meanspacing_normalization",
            "novelty_estimate": None,
            "parent_record_id": None,
            "precision_dps": None,
            "sigma_claim_id": None,
            "sigma_symbol_ref": None,
            "step_trace": None,
            "training_weight": None,
            "verdict": "UNVERIFIED",
        }
        _emit_kill_ledger_row(row)
