"""Epistemic-economy value metrics for the Erebos substrate.

Per Erebos v3 §4.5 ("closed-loop epistemic economy") + DR amendment.
Every ComposedClaim emission gets four prices attached:

  generation_cost_seconds   — wall-clock time plugin took to emit
  falsification_cost_seconds — wall-clock time loader took to run
  information_gain_nats     — KL divergence in routing distribution
                              before vs after this emission's verdict
  reuse_value_count         — count of downstream emissions whose
                              parent_record_ids include this row,
                              rolling 60-day window

The substrate's value metric:

  value_per_tick = sum(info_gain * reuse_value) / sum(costs)

This module ships the primitives; the daemon wires generation_cost
+ falsification_cost; this module computes the post-hoc fields by
scanning the kill_ledger.

Reading: pivot/erebos_v3_synthesis_2026-05-27.md §4.5
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


def value_per_tick(
    ledger_rows: list[dict],
    *,
    window_days: int = 60,
) -> float:
    """Compute sum(info_gain * reuse_value) / sum(generation_cost +
    falsification_cost) over the rolling window.

    Returns nat-equivalents per second. Higher is better.
    Returns 0.0 for an empty ledger (no division by zero).
    """
    if not ledger_rows:
        return 0.0

    cutoff_iso = _window_cutoff_iso(window_days)
    numerator = 0.0
    denominator = 0.0
    for row in ledger_rows:
        ts = row.get("emitted_at") or ""
        if ts < cutoff_iso:
            continue

        info_gain = row.get("information_gain_nats") or 0.0
        reuse = float(row.get("reuse_value_count") or 0)
        gen_cost = float(row.get("generation_cost_seconds") or 0.0)
        fal_cost = float(row.get("falsification_cost_seconds") or 0.0)

        numerator += info_gain * reuse
        denominator += gen_cost + fal_cost

    if denominator <= 0:
        return 0.0
    return numerator / denominator


def information_gain_estimate(
    routing_distribution_before: dict[str, float],
    routing_distribution_after: dict[str, float],
) -> float:
    """KL divergence in nats between routing distributions before
    and after an emission's verdict is recorded.

    Both distributions should be normalized (sum to 1). Returns 0
    if either is empty or if the distributions are identical.
    """
    if not routing_distribution_before or not routing_distribution_after:
        return 0.0

    # Get the union of keys for the divergence sum
    all_keys = set(routing_distribution_before) | set(routing_distribution_after)
    if not all_keys:
        return 0.0

    # Smooth to avoid log(0); add a tiny epsilon
    epsilon = 1e-12

    # Normalize both distributions
    b_total = sum(routing_distribution_before.values())
    a_total = sum(routing_distribution_after.values())
    if b_total <= 0 or a_total <= 0:
        return 0.0
    b_norm = {k: routing_distribution_before.get(k, 0.0) / b_total
              for k in all_keys}
    a_norm = {k: routing_distribution_after.get(k, 0.0) / a_total
              for k in all_keys}

    kl = 0.0
    for k in all_keys:
        p = a_norm[k] + epsilon
        q = b_norm[k] + epsilon
        # KL(after || before) = sum_k p_a(k) * log(p_a(k) / p_b(k))
        kl += p * math.log(p / q)
    # KL can come out marginally negative due to smoothing; clamp.
    return max(0.0, kl)


def update_reuse_value_counts(
    ledger_path: Path,
    window_days: int = 60,
) -> dict[str, int]:
    """For each row in the rolling window, count downstream emissions
    that reference it via parent_record_ids. Returns {record_id: count}.

    Best-effort: skips malformed lines, returns empty on missing file.
    """
    if not ledger_path.exists():
        return {}

    cutoff_iso = _window_cutoff_iso(window_days)
    counts: Counter = Counter()
    in_window_ids: set[str] = set()
    parent_refs: list[list[str]] = []

    try:
        with ledger_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                ts = row.get("emitted_at") or ""
                if ts < cutoff_iso:
                    continue
                rid = row.get("record_id")
                if rid:
                    in_window_ids.add(rid)
                parents = row.get("parent_record_ids") or []
                if isinstance(parents, list):
                    parent_refs.append([str(p) for p in parents if p])
    except Exception:
        return {}

    # Count downstream references
    for parents in parent_refs:
        for parent in parents:
            if parent in in_window_ids:
                counts[parent] += 1

    return dict(counts)


def summarize_economy(ledger_rows: list[dict], *, window_days: int = 60) -> dict:
    """High-level summary stats over the rolling window for dashboards
    and Sprint-1 baseline measurement."""
    if not ledger_rows:
        return _empty_summary(window_days)

    cutoff_iso = _window_cutoff_iso(window_days)
    in_window = [r for r in ledger_rows
                 if (r.get("emitted_at") or "") >= cutoff_iso]
    if not in_window:
        return _empty_summary(window_days)

    n = len(in_window)
    total_gen = sum(float(r.get("generation_cost_seconds") or 0.0)
                    for r in in_window)
    total_fal = sum(float(r.get("falsification_cost_seconds") or 0.0)
                    for r in in_window)
    total_info = sum(float(r.get("information_gain_nats") or 0.0)
                     for r in in_window)
    total_reuse = sum(int(r.get("reuse_value_count") or 0)
                      for r in in_window)
    vpt = value_per_tick(ledger_rows, window_days=window_days)

    return {
        "window_days": window_days,
        "n_emissions": n,
        "total_generation_cost_seconds": round(total_gen, 4),
        "total_falsification_cost_seconds": round(total_fal, 4),
        "total_information_gain_nats": round(total_info, 4),
        "total_reuse_value_count": total_reuse,
        "mean_generation_cost_per_emission": round(total_gen / n, 4) if n else 0.0,
        "mean_falsification_cost_per_emission": round(total_fal / n, 4) if n else 0.0,
        "value_per_tick_nat_per_sec": round(vpt, 6),
    }


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def _window_cutoff_iso(window_days: int) -> str:
    """Return the ISO timestamp for `window_days` ago."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    return cutoff.isoformat()


def _empty_summary(window_days: int) -> dict:
    return {
        "window_days": window_days,
        "n_emissions": 0,
        "total_generation_cost_seconds": 0.0,
        "total_falsification_cost_seconds": 0.0,
        "total_information_gain_nats": 0.0,
        "total_reuse_value_count": 0,
        "mean_generation_cost_per_emission": 0.0,
        "mean_falsification_cost_per_emission": 0.0,
        "value_per_tick_nat_per_sec": 0.0,
    }
