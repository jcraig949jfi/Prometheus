"""Pilot driver for V3 root-space discovery at degree 14.

Spec: degree 14 (k=7 root pairs) × 5K samples × 3 seeds = 15K samples.

Outputs:
  * prometheus_math/_v3_root_space_pilot.json — per-seed summary
  * stdout — running progress + final headline
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from prometheus_math.discovery_env_v3 import DiscoveryEnvV3


def _run_cell(seed: int, n_samples: int, degree: int = 14) -> Dict[str, Any]:
    env = DiscoveryEnvV3(
        degree=degree,
        n_theta_bins=16,
        n_r_bins=8,
        seed=seed,
    )
    env.reset()
    n_integer = 0
    n_sub_lehmer = 0
    n_signal = 0
    integer_polys: List[Dict[str, Any]] = []
    m_values: List[float] = []
    t0 = time.time()
    for i in range(n_samples):
        rec = env.sample_one()
        if rec.coeffs_int is not None:
            n_integer += 1
            if math.isfinite(rec.mahler_measure):
                m_values.append(rec.mahler_measure)
                integer_polys.append(
                    {
                        "coeffs": list(rec.coeffs_int),
                        "M": float(rec.mahler_measure),
                        "is_sub_lehmer": bool(rec.is_sub_lehmer),
                        "is_signal_class": bool(rec.is_signal_class),
                        "terminal_state": rec.pipeline_terminal_state,
                        "kill_pattern": rec.pipeline_kill_pattern,
                    }
                )
        if rec.is_sub_lehmer:
            n_sub_lehmer += 1
        if rec.is_signal_class:
            n_signal += 1
    elapsed = time.time() - t0
    out = {
        "seed": seed,
        "n_samples": n_samples,
        "n_integer_coeffs": n_integer,
        "n_sub_lehmer": n_sub_lehmer,
        "n_signal_class": n_signal,
        "promote_rate": n_signal / max(1, n_samples),
        "fraction_integer": n_integer / max(1, n_samples),
        "best_m_overall": env.best_m_overall(),
        "m_min": float(min(m_values)) if m_values else None,
        "m_median": float(np.median(m_values)) if m_values else None,
        "m_max": float(max(m_values)) if m_values else None,
        "integer_polys": integer_polys[:20],  # first 20 only, for record
        "elapsed_s": elapsed,
    }
    env.close()
    return out


def _run_cyclotomic_aligned_cell(
    seed: int, n_samples: int, degree: int = 14
) -> Dict[str, Any]:
    """Variant: pin theta bins to cyclotomic-friendly angles (2*pi*k/n
    for small n).  This forces high integer-coefficient yield at the
    cost of nearly all polys being cyclotomic factors (M=1) — a useful
    *control* for the random-bin variant: it tells us whether the
    integer-coeff subspace within root space is genuinely M-diverse or
    collapses to cyclotomic, just as V2's coefficient search did."""
    import math as _math

    cyclo_thetas = [
        2 * _math.pi / n
        for n in (3, 4, 5, 6, 7, 8, 9, 10, 12, 15)
    ]
    # Add the supplementary angles (pi - theta) as separate cyclotomic
    # roots (e.g., theta and 2pi - theta give different Phi_n indices).
    cyclo_thetas += [_math.pi - t for t in cyclo_thetas if t < _math.pi]
    cyclo_thetas = sorted(set(cyclo_thetas))
    rng = np.random.default_rng(seed)
    env = DiscoveryEnvV3(degree=degree, n_theta_bins=16, n_r_bins=8, seed=seed)
    env.reset()
    n_integer = 0
    n_sub_lehmer = 0
    n_signal = 0
    integer_polys: List[Dict[str, Any]] = []
    m_values: List[float] = []
    t0 = time.time()
    from prometheus_math.discovery_env_v3 import (
        RootConfig,
        _config_to_coeffs_real,
        _round_to_integer_coeffs,
        _is_reciprocal,
    )

    for i in range(n_samples):
        # Sample: 1 Salem pair (random r, random theta); k_unit-1 unit
        # pairs from cyclotomic-aligned angles.
        r = float(env.r_min + (env.r_max - env.r_min) * rng.random())
        theta_salem = float(_math.pi * rng.random())
        n_unit = (degree - 4) // 2
        unit_thetas = tuple(
            float(cyclo_thetas[int(rng.integers(0, len(cyclo_thetas)))])
            for _ in range(n_unit)
        )
        cfg = RootConfig(
            unit_thetas=unit_thetas,
            salem_pair=(r, theta_salem),
            real_pair_rho=None,
        )
        rec = env._evaluate_config(cfg)
        if rec.coeffs_int is not None:
            n_integer += 1
            if _math.isfinite(rec.mahler_measure):
                m_values.append(rec.mahler_measure)
                if len(integer_polys) < 20:
                    integer_polys.append(
                        {
                            "coeffs": list(rec.coeffs_int),
                            "M": float(rec.mahler_measure),
                            "is_sub_lehmer": bool(rec.is_sub_lehmer),
                            "is_signal_class": bool(rec.is_signal_class),
                            "terminal_state": rec.pipeline_terminal_state,
                            "kill_pattern": rec.pipeline_kill_pattern,
                        }
                    )
        if rec.is_sub_lehmer:
            n_sub_lehmer += 1
        if rec.is_signal_class:
            n_signal += 1
    elapsed = time.time() - t0
    out = {
        "variant": "cyclotomic_aligned",
        "seed": seed,
        "n_samples": n_samples,
        "n_integer_coeffs": n_integer,
        "n_sub_lehmer": n_sub_lehmer,
        "n_signal_class": n_signal,
        "promote_rate": n_signal / max(1, n_samples),
        "fraction_integer": n_integer / max(1, n_samples),
        "best_m_overall": env.best_m_overall(),
        "m_min": float(min(m_values)) if m_values else None,
        "m_median": float(np.median(m_values)) if m_values else None,
        "m_max": float(max(m_values)) if m_values else None,
        "integer_polys": integer_polys,
        "elapsed_s": elapsed,
    }
    env.close()
    return out


def main() -> None:
    n_samples = 5_000
    seeds = (0, 1, 2)
    out_path = Path("prometheus_math/_v3_root_space_pilot.json")

    cells: List[Dict[str, Any]] = []
    t_global = time.time()
    print("=== variant: random-bin (default) ===")
    for seed in seeds:
        print(f"[{time.strftime('%H:%M:%S')}] running seed={seed} ...")
        res = _run_cell(seed, n_samples)
        print(
            f"  n_integer={res['n_integer_coeffs']} sub_lehmer={res['n_sub_lehmer']} "
            f"signal={res['n_signal_class']} best_M={res['best_m_overall']!r} "
            f"elapsed={res['elapsed_s']:.1f}s"
        )
        res["variant"] = "random_bin"
        cells.append(res)

    print("\n=== variant: cyclotomic-aligned (theta pinned to 2pi/n) ===")
    for seed in seeds:
        print(f"[{time.strftime('%H:%M:%S')}] running cyclo seed={seed} ...")
        res = _run_cyclotomic_aligned_cell(seed, n_samples)
        print(
            f"  n_integer={res['n_integer_coeffs']} sub_lehmer={res['n_sub_lehmer']} "
            f"signal={res['n_signal_class']} best_M={res['best_m_overall']!r} "
            f"elapsed={res['elapsed_s']:.1f}s"
        )
        cells.append(res)

    total = time.time() - t_global
    summary = {
        "n_samples_per_seed": n_samples,
        "seeds": list(seeds),
        "total_samples": n_samples * len(seeds) * 2,
        "total_elapsed_s": total,
        "cells": cells,
    }
    out_path.write_text(json.dumps(summary, indent=2, default=float))
    print(f"\nWrote {out_path} ({total:.1f}s total)")

    # Aggregate.
    for variant in ("random_bin", "cyclotomic_aligned"):
        rows = [c for c in cells if c.get("variant") == variant]
        n_int = sum(c["n_integer_coeffs"] for c in rows)
        n_sl = sum(c["n_sub_lehmer"] for c in rows)
        n_sig = sum(c["n_signal_class"] for c in rows)
        n_total = sum(c["n_samples"] for c in rows)
        print(
            f"\n[{variant}] Aggregate: n_integer={n_int}/{n_total} "
            f"sub_lehmer={n_sl} signal_class={n_sig}"
        )


if __name__ == "__main__":
    main()
