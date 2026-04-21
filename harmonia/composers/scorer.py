"""Composition scoring (gen_10).

Score = expected information gain per compute unit. Components per
`docs/prompts/gen_10_composition_enumeration.md`:

  score = (novelty + resolving_prior + 0.5 * stratification_fanout) / sqrt(cost)

- novelty            : (F, P) tensor cells touched that are currently untested
- resolving_prior    : prior signal count from the operators' SIGNATURE history
- stratification_fanout : expected sub-cell count if the composition stratifies
- cost               : expected runtime from operator metadata (seconds; default 10)

A composition's "novelty" in the current substrate is measured against
the tensor: if the composition would produce a result applicable to a
cell that is currently 0 (untested), that cell contributes +1.

Since the full tensor plumbing for "which cells would this touch?" is
not yet live at gen_10 first-pass, we use a tractable proxy:
    novelty     = count of currently-zero cells for the projection the
                  composition's output would most resemble (proxy:
                  operator-only compositions score novelty = unknown;
                  operator-on-dataset compositions score novelty =
                  zero-cell count on the dataset's canonical projection
                  if declared, else 0).
    resolving_prior = per-operator reference count in symbols:refs:*.
    stratification_fanout = 1 for non-stratifying ops, else n_bins (default 10).
    cost = 10 seconds default (operator metadata doesn't carry runtime
           yet — follow-up to operationalize).
"""
from __future__ import annotations

import math
import os
from typing import Optional

import redis


def _get_redis():
    host = os.environ.get("AGORA_REDIS_HOST", "192.168.1.176")
    password = os.environ.get("AGORA_REDIS_PASSWORD", "prometheus")
    return redis.Redis(host=host, password=password, decode_responses=True)


def _refs_count(r, symbol_ref: str) -> int:
    """Count refs-to this symbol version (resolves_prior proxy)."""
    return int(r.scard(f"symbols:refs:{symbol_ref}") or 0)


def score_composition(
    outer_meta: dict,
    inner_meta: dict,
    tensor_zero_cells: Optional[int] = None,
    r: Optional[redis.Redis] = None,
) -> dict:
    """Compute score components and total.

    outer_meta / inner_meta are the frontmatter dicts for the two
    symbols. Expected keys include `name`, `type`, `version`, and
    optionally `precision.n_bins_default` for fanout estimation.

    Returns a dict with all score components.
    """
    if r is None:
        r = _get_redis()

    outer_name = outer_meta.get("name")
    inner_name = inner_meta.get("name")
    outer_ver = outer_meta.get("version", 1)
    inner_ver = inner_meta.get("version", 1)
    outer_ref = f"{outer_name}@v{outer_ver}"
    inner_ref = f"{inner_name}@v{inner_ver}"

    outer_type = outer_meta.get("type", "unknown")
    inner_type = inner_meta.get("type", "unknown")

    # resolving_prior: reference count of the outer operator (it's
    # doing the applying). For operator ∘ operator, sum both.
    rp_outer = _refs_count(r, outer_ref)
    rp_inner = _refs_count(r, inner_ref) if outer_type == "operator" and inner_type == "operator" else 0
    resolving_prior = rp_outer + rp_inner

    # novelty proxy: number of currently-zero tensor cells. At gen_10
    # first pass this is a global scalar provided by the driver. 0 if
    # tensor_zero_cells is None.
    novelty = float(tensor_zero_cells) if tensor_zero_cells is not None else 0.0
    # Operator ∘ operator compositions target a downstream computation
    # that can expand to many cells; credit them conservatively.
    if outer_type == "operator" and inner_type == "operator":
        novelty *= 0.5
    elif outer_type == "operator" and inner_type == "dataset":
        novelty *= 1.0
    elif outer_type == "shape" and inner_type == "dataset":
        novelty *= 1.0

    # stratification_fanout: n_bins for stratifier-carrying nulls.
    fanout = 1.0
    prec_outer = outer_meta.get("precision") or {}
    prec_inner = inner_meta.get("precision") or {}
    if isinstance(prec_outer, dict) and prec_outer.get("n_bins_default"):
        try:
            fanout = float(prec_outer["n_bins_default"])
        except (TypeError, ValueError):
            pass
    elif isinstance(prec_inner, dict) and prec_inner.get("n_bins_default"):
        try:
            fanout = float(prec_inner["n_bins_default"])
        except (TypeError, ValueError):
            pass

    # cost proxy: if outer symbol declares `precision.n_perms_default` or
    # `precision.n_samples_default`, cost scales with it. Default 10.
    cost = 10.0
    if isinstance(prec_outer, dict):
        for key, c in (("n_perms_default", 0.02), ("n_boot_default", 0.02),
                       ("n_samples_default", 0.001)):
            if prec_outer.get(key):
                try:
                    cost = max(cost, float(prec_outer[key]) * c)
                except (TypeError, ValueError):
                    pass

    score = (novelty + resolving_prior + 0.5 * fanout) / math.sqrt(cost)

    return {
        "composition": f"{outer_ref} ∘ {inner_ref}",
        "outer": outer_ref,
        "inner": inner_ref,
        "outer_type": outer_type,
        "inner_type": inner_type,
        "novelty": novelty,
        "resolving_prior": resolving_prior,
        "stratification_fanout": fanout,
        "cost": cost,
        "score": score,
    }
