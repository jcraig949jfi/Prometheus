"""
phase_transition_study.py — Phase transition investigation for Qwen2.5-1.5B-Instruct.

Three-part study to characterize the 1.5B model's reasoning phase transitions:

PT-1: Phase Transition Map
    For each (layer, trap) pair, sweep epsilon and fit sigmoid vs linear models.
    Use BIC to determine which fits better. Report genuine phase transitions.
    Also test random orthogonal direction as null baseline.
    Output: heatmap of delta-BIC, JSON results.

PT-2: Precipitation-Specific Fitness Calibration
    Run all traps at baseline to determine which the model fails.
    Report the fitness landscape and recommend an injection layer from PT-1.
    Output: calibration table, JSON results.

PT-3: Ordinal Trap Replication Study
    Define 20 ordinal-position reasoning traps. For each, measure baseline margin,
    steered margin, and phase transition detection via epsilon sweep.
    Report how many ordinal traps show phase transitions.
    Output: bar chart, JSON results.

Context:
    Pivoting from Qwen3-4B (flat fitness landscape) to Qwen2.5-1.5B-Instruct
    which shows genuine binary phase transitions on 2/4 traps. The 1.5B model
    has 28 layers, d_model=1536, fits in ~4GB VRAM.

Usage:
    python phase_transition_study.py --model Qwen/Qwen2.5-1.5B-Instruct --device cuda
    python phase_transition_study.py --genome path/to/genome.pt --phases 1 2 3
    python phase_transition_study.py --phases 1 --layers 7 14 21 27
"""

import argparse
import json
import logging
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from scipy.stats import norm as scipy_norm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
    make_steering_hook,
)
from preflight import run_preflight_with_base

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.phase_transition")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Key layer depths in the 28-layer Qwen2.5-1.5B model
DEFAULT_LAYERS = [7, 14, 21, 23, 25, 26, 27]

# Epsilon sweep grid for phase transition detection
DEFAULT_EPSILONS = np.linspace(-12.0, 12.0, 25).tolist()

# BIC threshold: delta-BIC > 10 is "very strong" evidence (Kass & Raftery 1995)
BIC_THRESHOLD = 10.0

# ---------------------------------------------------------------------------
# Ordinal Trap Battery (PT-3)
# ---------------------------------------------------------------------------

ORDINAL_TRAPS = [
    {
        "name": "Overtake 2nd",
        "prompt": "You overtake the person in second place in a race. What position are you in now? Answer: First or Second?",
        "target_token": "Second",
        "anti_token": "First",
    },
    {
        "name": "Overtake Last",
        "prompt": "You overtake the last-place runner. What position are you in now? Answer: Last or Second-to-last?",
        "target_token": "Second",  # Can't overtake last if you're behind them
        "anti_token": "Last",
    },
    {
        "name": "Finish Before 3rd",
        "prompt": "You finish a race just before the person in 3rd place. What position do you finish in? Answer: Second or Third?",
        "target_token": "Third",
        "anti_token": "Second",
    },
    {
        "name": "Elevator Floor",
        "prompt": "You are on the 5th floor and go down 3 floors, then up 7 floors. What floor are you on? Answer: 9 or 12?",
        "target_token": "9",
        "anti_token": "12",
    },
    {
        "name": "Queue Position",
        "prompt": "You are 4th in a queue. Two people ahead of you leave. What position are you in? Answer: Second or Fourth?",
        "target_token": "Second",
        "anti_token": "Fourth",
    },
    {
        "name": "Day After Tomorrow",
        "prompt": "If today is Wednesday, what day is the day after tomorrow? Answer: Friday or Thursday?",
        "target_token": "Friday",
        "anti_token": "Thursday",
    },
    {
        "name": "Counting Fence Posts",
        "prompt": "A straight fence has 10 sections. How many fence posts are there? Answer: 11 or 10?",
        "target_token": "11",
        "anti_token": "10",
    },
    {
        "name": "Meeting Point",
        "prompt": "Two trains 100km apart approach each other at 50km/h each. A bird flies between them at 100km/h. How far does the bird fly before they meet? Answer: 100 or 200?",
        "target_token": "100",
        "anti_token": "200",
    },
    {
        "name": "Handshakes",
        "prompt": "4 people all shake hands with each other once. How many handshakes total? Answer: 6 or 12?",
        "target_token": "6",
        "anti_token": "12",
    },
    {
        "name": "Siblings",
        "prompt": "A girl has as many brothers as sisters. Her brother has twice as many sisters as brothers. How many children in the family? Answer: 7 or 5?",
        "target_token": "7",
        "anti_token": "5",
    },
    {
        "name": "Clock Angle",
        "prompt": "At 3:00, the angle between clock hands is 90 degrees. At 3:30, is the angle 90 or 75 degrees? Answer: 75 or 90?",
        "target_token": "75",
        "anti_token": "90",
    },
    {
        "name": "Staircase Steps",
        "prompt": "You climb 2 steps at a time on a 10-step staircase. How many steps do you take? Answer: 5 or 10?",
        "target_token": "5",
        "anti_token": "10",
    },
    {
        "name": "Cutting Rope",
        "prompt": "You make 5 cuts on a rope. How many pieces do you get? Answer: 6 or 5?",
        "target_token": "6",
        "anti_token": "5",
    },
    {
        "name": "Month Ordering",
        "prompt": "What is the 6th month of the year? Answer: June or July?",
        "target_token": "June",
        "anti_token": "July",
    },
    {
        "name": "Birthday Paradox Direction",
        "prompt": "In a room of 23 people, is the probability of a shared birthday above or below 50%? Answer: Above or Below?",
        "target_token": "Above",
        "anti_token": "Below",
    },
    {
        "name": "Rank Reversal",
        "prompt": "In a class of 30, you rank 12th from the top. What is your rank from the bottom? Answer: 19 or 18?",
        "target_token": "19",
        "anti_token": "18",
    },
    {
        "name": "Pages in Book",
        "prompt": "A book is open. The two visible page numbers add up to 47. Are the pages 23 and 24, or 22 and 25? Answer: 23 or 22?",
        "target_token": "23",
        "anti_token": "22",
    },
    {
        "name": "Round Robin Games",
        "prompt": "In a round-robin tournament with 5 teams, how many games are played? Answer: 10 or 20?",
        "target_token": "10",
        "anti_token": "20",
    },
    {
        "name": "Overlapping Intervals",
        "prompt": "Event A runs from 1pm to 4pm. Event B runs from 3pm to 6pm. How many hours do they overlap? Answer: 1 or 2?",
        "target_token": "1",
        "anti_token": "2",
    },
    {
        "name": "Off-by-One Inclusive",
        "prompt": "How many integers are there from 1 to 10 inclusive? Answer: 10 or 9?",
        "target_token": "10",
        "anti_token": "9",
    },
]

# ---------------------------------------------------------------------------
# Sigmoid and linear model definitions
# ---------------------------------------------------------------------------

def sigmoid(x, L, k, x0, b):
    """Sigmoid: L / (1 + exp(-k*(x - x0))) + b"""
    return L / (1.0 + np.exp(-k * (x - x0))) + b


def linear(x, m, c):
    """Linear: m*x + c"""
    return m * x + c


def compute_bic(n, k, rss):
    """Bayesian Information Criterion. n=data points, k=params, rss=residual sum of squares."""
    if rss <= 0 or n <= k:
        return np.inf
    return n * np.log(rss / n) + k * np.log(n)


def fit_dose_response(epsilons, margins):
    """
    Fit sigmoid and linear models to a dose-response curve.
    Returns dict with fit parameters, BIC values, and delta-BIC.
    """
    eps_arr = np.array(epsilons, dtype=np.float64)
    margin_arr = np.array(margins, dtype=np.float64)
    n = len(eps_arr)

    result = {
        "n_points": n,
        "epsilons": epsilons,
        "margins": margins,
    }

    # --- Linear fit ---
    try:
        popt_lin, _ = curve_fit(linear, eps_arr, margin_arr)
        pred_lin = linear(eps_arr, *popt_lin)
        rss_lin = float(np.sum((margin_arr - pred_lin) ** 2))
        bic_lin = compute_bic(n, 2, rss_lin)
        result["linear"] = {
            "params": {"m": float(popt_lin[0]), "c": float(popt_lin[1])},
            "rss": rss_lin,
            "bic": bic_lin,
        }
    except Exception as e:
        log.warning(f"Linear fit failed: {e}")
        bic_lin = np.inf
        result["linear"] = {"params": None, "rss": np.inf, "bic": np.inf, "error": str(e)}

    # --- Sigmoid fit ---
    try:
        # Initial guesses: L=range of data, k=1, x0=midpoint, b=min
        L0 = float(margin_arr.max() - margin_arr.min())
        k0 = 1.0
        x0_0 = 0.0
        b0 = float(margin_arr.min())
        p0 = [L0, k0, x0_0, b0]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            popt_sig, _ = curve_fit(
                sigmoid, eps_arr, margin_arr, p0=p0,
                maxfev=10000,
                bounds=(
                    [-np.inf, 0.01, -20.0, -np.inf],  # k > 0 for proper sigmoid
                    [np.inf, 50.0, 20.0, np.inf],
                ),
            )

        pred_sig = sigmoid(eps_arr, *popt_sig)
        rss_sig = float(np.sum((margin_arr - pred_sig) ** 2))
        bic_sig = compute_bic(n, 4, rss_sig)
        result["sigmoid"] = {
            "params": {
                "L": float(popt_sig[0]),
                "k": float(popt_sig[1]),
                "x0": float(popt_sig[2]),
                "b": float(popt_sig[3]),
            },
            "rss": rss_sig,
            "bic": bic_sig,
        }
    except Exception as e:
        log.warning(f"Sigmoid fit failed: {e}")
        bic_sig = np.inf
        result["sigmoid"] = {"params": None, "rss": np.inf, "bic": np.inf, "error": str(e)}

    # --- BIC comparison ---
    delta_bic = bic_lin - bic_sig  # positive = sigmoid wins
    result["delta_bic"] = float(delta_bic)
    result["is_phase_transition"] = delta_bic > BIC_THRESHOLD
    result["preferred_model"] = "sigmoid" if delta_bic > 0 else "linear"

    return result


# ---------------------------------------------------------------------------
# Probe direction: SVD of unembedding matrix
# ---------------------------------------------------------------------------

def compute_svd_probe(model, top_k: int = 1) -> torch.Tensor:
    """
    Extract leading right singular vector of the unembedding matrix W_U.
    This gives the direction of maximum variance in logit space.
    Returns unit vector of shape [d_model].
    """
    log.info("Computing SVD probe direction from unembedding matrix...")
    W_U = model.W_U  # shape: [d_model, vocab_size]
    # We want the direction in residual stream space that most affects logits
    # That's the leading left singular vector of W_U (or right singular vector of W_U^T)
    U, S, Vh = torch.linalg.svd(W_U.float(), full_matrices=False)
    # U columns are directions in d_model space, ordered by singular value
    probe = U[:, 0]  # leading direction
    probe = probe / (probe.norm() + 1e-8)
    log.info(f"SVD probe: shape={probe.shape}, leading singular value={S[0]:.2f}")
    return probe


def random_orthogonal_direction(d_model: int, device: str = "cuda") -> torch.Tensor:
    """Generate a random unit vector of shape [d_model]."""
    v = torch.randn(d_model, device=device)
    v = v / (v.norm() + 1e-8)
    return v


# ---------------------------------------------------------------------------
# Epsilon sweep for a single (layer, trap, direction)
# ---------------------------------------------------------------------------

def epsilon_sweep(model, trap: dict, direction: torch.Tensor, layer: int,
                  epsilons: list) -> list:
    """
    Run epsilon sweep: inject epsilon * direction at given layer.
    Returns list of margin values corresponding to each epsilon.
    """
    margins = []
    target_id = model.to_tokens(trap["target_token"], prepend_bos=False)[0][0].item()
    anti_id = model.to_tokens(trap["anti_token"], prepend_bos=False)[0][0].item()
    tokens = model.to_tokens(trap["prompt"])

    for eps in epsilons:
        hook_name, hook_fn = make_steering_hook(direction, layer, epsilon=eps)
        with torch.no_grad():
            logits = model.run_with_hooks(tokens, fwd_hooks=[(hook_name, hook_fn)])
        final = logits[0, -1, :]
        margin = (final[target_id] - final[anti_id]).item()
        margins.append(margin)

    return margins


# ═══════════════════════════════════════════════════════════════════════════
# PT-1: Phase Transition Map
# ═══════════════════════════════════════════════════════════════════════════

def run_pt1(base: AnalysisBase, layers: list, epsilons: list) -> dict:
    """
    Phase Transition Map: for each (layer, trap), sweep epsilon and determine
    whether the dose-response is sigmoid (phase transition) or linear.
    Also run random orthogonal baseline for comparison.
    """
    print("\n" + "=" * 70)
    print("PT-1: PHASE TRANSITION MAP")
    print("=" * 70)
    print(f"  Layers: {layers}")
    print(f"  Epsilons: {len(epsilons)} points from {epsilons[0]:.1f} to {epsilons[-1]:.1f}")
    print(f"  Traps: {len(LOGIT_TRAPS)} core + {len(HELD_OUT_TRAPS)} held-out")
    print()

    model = base.model

    # Get probe direction
    if base.vector is not None:
        log.info("Using genome vector as probe direction")
        probe = base.v_hat
        probe_source = "genome"
    else:
        probe = compute_svd_probe(model)
        probe_source = "svd_unembed"

    # Random orthogonal baseline
    rand_dir = random_orthogonal_direction(base.d_model, base.device)
    # Make it orthogonal to probe
    rand_dir = rand_dir - (rand_dir @ probe) * probe
    rand_dir = rand_dir / (rand_dir.norm() + 1e-8)

    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS
    trap_names = [t["name"] for t in all_traps]

    # Results storage
    delta_bic_matrix = np.full((len(layers), len(all_traps)), np.nan)
    delta_bic_rand = np.full((len(layers), len(all_traps)), np.nan)
    detailed_results = []

    total = len(layers) * len(all_traps)
    count = 0

    for i, layer in enumerate(layers):
        for j, trap in enumerate(all_traps):
            count += 1
            tag = f"[{count}/{total}] L{layer}/{trap['name']}"

            # --- Probe direction ---
            margins = epsilon_sweep(model, trap, probe, layer, epsilons)
            fit = fit_dose_response(epsilons, margins)
            delta_bic_matrix[i, j] = fit["delta_bic"]

            pt_flag = "PHASE-TRANSITION" if fit["is_phase_transition"] else "linear"
            print(f"  {tag}: dBIC={fit['delta_bic']:+.1f} [{pt_flag}]")

            detailed_results.append({
                "layer": layer,
                "trap": trap["name"],
                "direction": probe_source,
                "fit": fit,
            })

            # --- Random baseline ---
            margins_rand = epsilon_sweep(model, trap, rand_dir, layer, epsilons)
            fit_rand = fit_dose_response(epsilons, margins_rand)
            delta_bic_rand[i, j] = fit_rand["delta_bic"]

            detailed_results.append({
                "layer": layer,
                "trap": trap["name"],
                "direction": "random_orthogonal",
                "fit": fit_rand,
            })

    # --- Summary ---
    n_phase_transitions = int(np.sum(delta_bic_matrix > BIC_THRESHOLD))
    n_rand_transitions = int(np.sum(delta_bic_rand > BIC_THRESHOLD))

    print(f"\n  Summary:")
    print(f"    Phase transitions (probe):  {n_phase_transitions}/{total}")
    print(f"    Phase transitions (random): {n_rand_transitions}/{total}")

    # Best layer = row with most phase transitions
    pt_counts_by_layer = np.sum(delta_bic_matrix > BIC_THRESHOLD, axis=1)
    best_layer_idx = int(np.argmax(pt_counts_by_layer))
    best_layer = layers[best_layer_idx]
    print(f"    Best layer: {best_layer} ({int(pt_counts_by_layer[best_layer_idx])} transitions)")

    # --- Heatmap plot ---
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for ax, matrix, title in [
        (axes[0], delta_bic_matrix, f"delta-BIC (probe: {probe_source})"),
        (axes[1], delta_bic_rand, "delta-BIC (random orthogonal)"),
    ]:
        im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn",
                        vmin=-20, vmax=40)
        ax.set_xticks(range(len(trap_names)))
        ax.set_xticklabels(trap_names, rotation=45, ha="right", fontsize=8)
        ax.set_yticks(range(len(layers)))
        ax.set_yticklabels([f"L{l}" for l in layers])
        ax.set_title(title)
        ax.set_xlabel("Trap")
        ax.set_ylabel("Injection Layer")
        plt.colorbar(im, ax=ax, label="delta-BIC (>10 = phase transition)")

        # Mark phase transitions
        for ii in range(matrix.shape[0]):
            for jj in range(matrix.shape[1]):
                val = matrix[ii, jj]
                if not np.isnan(val):
                    marker = "*" if val > BIC_THRESHOLD else ""
                    ax.text(jj, ii, f"{val:.0f}{marker}",
                            ha="center", va="center", fontsize=7,
                            color="white" if abs(val) > 15 else "black")

    fig.suptitle("PT-1: Phase Transition Map (Qwen2.5-1.5B-Instruct)", fontsize=14)
    plt.tight_layout()
    plot_path = base.save_plot(fig, "pt1_heatmap")
    plt.close(fig)

    results = {
        "phase": "PT-1",
        "model": base.model_name,
        "probe_source": probe_source,
        "layers": layers,
        "epsilons": epsilons,
        "bic_threshold": BIC_THRESHOLD,
        "n_phase_transitions_probe": n_phase_transitions,
        "n_phase_transitions_random": n_rand_transitions,
        "best_layer": best_layer,
        "pt_counts_by_layer": {str(l): int(c) for l, c in zip(layers, pt_counts_by_layer)},
        "delta_bic_matrix": delta_bic_matrix.tolist(),
        "delta_bic_random": delta_bic_rand.tolist(),
        "trap_names": trap_names,
        "detailed": detailed_results,
        "plot": str(plot_path),
    }

    json_path = base.save_json(results, "pt1_phase_transition_map")
    return results


# ═══════════════════════════════════════════════════════════════════════════
# PT-2: Precipitation-Specific Fitness Calibration
# ═══════════════════════════════════════════════════════════════════════════

def run_pt2(base: AnalysisBase, pt1_results: dict = None) -> dict:
    """
    Run all traps at baseline to determine which the model fails.
    Report calibration and recommend injection layer from PT-1.
    """
    print("\n" + "=" * 70)
    print("PT-2: PRECIPITATION-SPECIFIC FITNESS CALIBRATION")
    print("=" * 70)

    model = base.model
    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS

    print(f"  Testing {len(all_traps)} traps at baseline (no steering)...")
    print()

    calibration = []
    n_pass = 0
    n_fail = 0

    for trap in all_traps:
        tokens = model.to_tokens(trap["prompt"])
        target_id = model.to_tokens(trap["target_token"], prepend_bos=False)[0][0].item()
        anti_id = model.to_tokens(trap["anti_token"], prepend_bos=False)[0][0].item()

        with torch.no_grad():
            logits = model(tokens)
        final = logits[0, -1, :]
        margin = (final[target_id] - final[anti_id]).item()

        passed = margin > 0
        status = "PASS" if passed else "FAIL"
        if passed:
            n_pass += 1
        else:
            n_fail += 1

        # Determine trap category
        trap_name = trap["name"]
        if any(t["name"] == trap_name for t in LOGIT_TRAPS):
            category = "core"
        elif any(t["name"] == trap_name for t in HELD_OUT_TRAPS):
            category = "held_out"
        else:
            category = "ordinal"

        calibration.append({
            "name": trap_name,
            "category": category,
            "margin": float(margin),
            "passed": passed,
        })

        print(f"  [{status}] {trap_name:30s} margin={margin:+8.3f}  ({category})")

    print(f"\n  Calibration: {n_pass} pass, {n_fail} fail out of {len(all_traps)}")
    print(f"  Failure rate: {n_fail/len(all_traps)*100:.1f}%")

    # Recommend injection layer from PT-1
    recommended_layer = None
    if pt1_results and "best_layer" in pt1_results:
        recommended_layer = pt1_results["best_layer"]
        print(f"\n  Recommended injection layer (from PT-1): {recommended_layer}")
    else:
        print("\n  No PT-1 results available — run PT-1 first for layer recommendation")

    # Fitness landscape summary
    failed_traps = [c for c in calibration if not c["passed"]]
    passed_traps = [c for c in calibration if c["passed"]]

    print(f"\n  Failed traps ({len(failed_traps)}):")
    for t in sorted(failed_traps, key=lambda x: x["margin"]):
        print(f"    {t['name']:30s} margin={t['margin']:+8.3f}  [{t['category']}]")

    print(f"\n  Passed traps ({len(passed_traps)}):")
    for t in sorted(passed_traps, key=lambda x: x["margin"], reverse=True):
        print(f"    {t['name']:30s} margin={t['margin']:+8.3f}  [{t['category']}]")

    results = {
        "phase": "PT-2",
        "model": base.model_name,
        "n_traps": len(all_traps),
        "n_pass": n_pass,
        "n_fail": n_fail,
        "failure_rate": n_fail / len(all_traps),
        "recommended_layer": recommended_layer,
        "calibration": calibration,
    }

    json_path = base.save_json(results, "pt2_calibration")
    return results


# ═══════════════════════════════════════════════════════════════════════════
# PT-3: Ordinal Trap Replication Study
# ═══════════════════════════════════════════════════════════════════════════

def run_pt3(base: AnalysisBase, pt1_results: dict = None,
            epsilons: list = None) -> dict:
    """
    Ordinal trap replication: measure baseline margin, steered margin,
    and phase transition for each of 20 ordinal traps.
    """
    print("\n" + "=" * 70)
    print("PT-3: ORDINAL TRAP REPLICATION STUDY")
    print("=" * 70)
    print(f"  Testing {len(ORDINAL_TRAPS)} ordinal reasoning traps")

    if epsilons is None:
        epsilons = DEFAULT_EPSILONS

    model = base.model

    # Determine probe direction and injection layer
    if base.vector is not None:
        probe = base.v_hat
        inject_layer = base.layer
        probe_source = "genome"
        log.info(f"Using genome vector at layer {inject_layer}")
    else:
        probe = compute_svd_probe(model)
        probe_source = "svd_unembed"
        # Use best layer from PT-1 if available, else default to layer 23
        if pt1_results and "best_layer" in pt1_results:
            inject_layer = pt1_results["best_layer"]
        else:
            inject_layer = 23  # reasonable default for 28-layer model
        log.info(f"Using SVD probe at layer {inject_layer}")

    print(f"  Probe: {probe_source}, injection layer: {inject_layer}")
    print(f"  Epsilon sweep: {len(epsilons)} points")
    print()

    ordinal_results = []
    n_phase_transitions = 0

    for idx, trap in enumerate(ORDINAL_TRAPS):
        tag = f"[{idx+1}/{len(ORDINAL_TRAPS)}] {trap['name']}"

        # Baseline margin
        tokens = model.to_tokens(trap["prompt"])
        target_id = model.to_tokens(trap["target_token"], prepend_bos=False)[0][0].item()
        anti_id = model.to_tokens(trap["anti_token"], prepend_bos=False)[0][0].item()

        with torch.no_grad():
            logits = model(tokens)
        baseline_margin = (logits[0, -1, target_id] - logits[0, -1, anti_id]).item()

        # Steered margin at epsilon=1.0
        hook_name, hook_fn = make_steering_hook(probe, inject_layer, epsilon=1.0)
        with torch.no_grad():
            logits_steered = model.run_with_hooks(tokens, fwd_hooks=[(hook_name, hook_fn)])
        steered_margin = (logits_steered[0, -1, target_id] - logits_steered[0, -1, anti_id]).item()

        # Epsilon sweep for phase transition detection
        margins = epsilon_sweep(model, trap, probe, inject_layer, epsilons)
        fit = fit_dose_response(epsilons, margins)

        is_pt = fit["is_phase_transition"]
        if is_pt:
            n_phase_transitions += 1

        pt_flag = "PHASE-TRANSITION" if is_pt else "linear"
        baseline_flag = "PASS" if baseline_margin > 0 else "FAIL"

        print(f"  {tag}: baseline={baseline_margin:+.3f} [{baseline_flag}], "
              f"steered={steered_margin:+.3f}, dBIC={fit['delta_bic']:+.1f} [{pt_flag}]")

        ordinal_results.append({
            "name": trap["name"],
            "baseline_margin": float(baseline_margin),
            "steered_margin": float(steered_margin),
            "delta_margin": float(steered_margin - baseline_margin),
            "baseline_pass": baseline_margin > 0,
            "is_phase_transition": is_pt,
            "delta_bic": float(fit["delta_bic"]),
            "fit": fit,
        })

    # --- Classification ---
    total = len(ORDINAL_TRAPS)
    if n_phase_transitions >= 8:
        classification = "CATEGORY_EFFECT"
        description = "Phase transitions generalize across ordinal reasoning category"
    elif n_phase_transitions >= 4:
        classification = "PARTIAL_GENERALIZATION"
        description = "Phase transitions partially generalize (subset of ordinal traps)"
    else:
        classification = "PROMPT_SPECIFIC"
        description = "Phase transitions are prompt-specific, not categorical"

    print(f"\n  Results: {n_phase_transitions}/{total} ordinal traps show phase transitions")
    print(f"  Classification: {classification}")
    print(f"  Interpretation: {description}")

    # --- Bar chart ---
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    names = [r["name"] for r in ordinal_results]
    baselines = [r["baseline_margin"] for r in ordinal_results]
    steered = [r["steered_margin"] for r in ordinal_results]
    delta_bics = [r["delta_bic"] for r in ordinal_results]

    x = np.arange(len(names))
    width = 0.35

    # Plot 1: Margins
    ax1 = axes[0]
    bars1 = ax1.bar(x - width/2, baselines, width, label="Baseline", color="steelblue", alpha=0.8)
    bars2 = ax1.bar(x + width/2, steered, width, label="Steered", color="coral", alpha=0.8)
    ax1.axhline(y=0, color="black", linewidth=0.5)
    ax1.set_ylabel("Logit Margin")
    ax1.set_title("Ordinal Traps: Baseline vs Steered Margins")
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=45, ha="right", fontsize=7)
    ax1.legend()

    # Plot 2: Delta-BIC
    ax2 = axes[1]
    colors = ["forestgreen" if db > BIC_THRESHOLD else "gray" for db in delta_bics]
    ax2.bar(x, delta_bics, color=colors, alpha=0.8)
    ax2.axhline(y=BIC_THRESHOLD, color="red", linewidth=1, linestyle="--",
                label=f"BIC threshold ({BIC_THRESHOLD})")
    ax2.set_ylabel("delta-BIC (sigmoid vs linear)")
    ax2.set_title(f"Phase Transition Detection: {n_phase_transitions}/{total} "
                  f"[{classification}]")
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=45, ha="right", fontsize=7)
    ax2.legend()

    fig.suptitle("PT-3: Ordinal Trap Replication Study (Qwen2.5-1.5B-Instruct)",
                 fontsize=14)
    plt.tight_layout()
    plot_path = base.save_plot(fig, "pt3_ordinal_traps")
    plt.close(fig)

    results = {
        "phase": "PT-3",
        "model": base.model_name,
        "probe_source": probe_source,
        "inject_layer": inject_layer,
        "n_ordinal_traps": total,
        "n_phase_transitions": n_phase_transitions,
        "classification": classification,
        "description": description,
        "ordinal_results": ordinal_results,
        "plot": str(plot_path),
    }

    json_path = base.save_json(results, "pt3_ordinal_replication")
    return results


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Phase Transition Study — 1.5B model investigation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python phase_transition_study.py --phases 1 2 3
  python phase_transition_study.py --phases 1 --layers 7 14 21 27
  python phase_transition_study.py --genome path/to/genome.pt --phases 1 2 3
        """,
    )

    parser.add_argument("--phases", type=int, nargs="+", default=[1, 2, 3],
                        choices=[1, 2, 3],
                        help="Which phases to run (default: all)")
    parser.add_argument("--layers", type=int, nargs="+", default=None,
                        help="Override layer list for PT-1 (default: 7 14 21 23 25 26 27)")
    parser.add_argument("--n-epsilon", type=int, default=25,
                        help="Number of epsilon points in sweep (default: 25)")
    parser.add_argument("--eps-min", type=float, default=-12.0,
                        help="Minimum epsilon (default: -12)")
    parser.add_argument("--eps-max", type=float, default=12.0,
                        help="Maximum epsilon (default: 12)")

    AnalysisBase.add_common_args(parser)
    args = parser.parse_args()

    # Resolve layers
    layers = args.layers if args.layers else DEFAULT_LAYERS

    # Build epsilon grid
    epsilons = np.linspace(args.eps_min, args.eps_max, args.n_epsilon).tolist()

    # Validate layers will be within model range (28 layers -> 0..27)
    for l in layers:
        if l < 0 or l > 27:
            parser.error(f"Layer {l} out of range for 28-layer model (valid: 0-27)")

    print("=" * 70)
    print("PHASE TRANSITION STUDY — Qwen2.5-1.5B-Instruct")
    print("=" * 70)
    print(f"  Model:    {args.model}")
    print(f"  Genome:   {args.genome or '(none — using SVD probe)'}")
    print(f"  Device:   {args.device}")
    print(f"  Phases:   {args.phases}")
    print(f"  Layers:   {layers}")
    print(f"  Epsilons: {len(epsilons)} points [{args.eps_min}, {args.eps_max}]")
    print(f"  Output:   {args.output_dir}")
    print("=" * 70)
    print()

    # --- Load model ---
    log.info("Initializing AnalysisBase...")
    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    # Sanity check model dimensions
    log.info(f"Model loaded: {base.n_layers} layers, d_model={base.d_model}")
    if base.n_layers != 28 or base.d_model != 1536:
        log.warning(
            f"Expected 28 layers / d_model=1536 for Qwen2.5-1.5B-Instruct, "
            f"got {base.n_layers} / {base.d_model}. Adjusting layer list if needed."
        )
        # Filter layers that are within range
        layers = [l for l in layers if 0 <= l < base.n_layers]
        if not layers:
            log.error("No valid layers after filtering. Aborting.")
            sys.exit(1)

    # --- Preflight ---
    log.info("Running preflight checks...")
    preflight_result = run_preflight_with_base(base)
    if not preflight_result.all_passed:
        log.error("Preflight FAILED. Aborting experiment.")
        sys.exit(1)
    print()

    # --- Run phases ---
    pt1_results = None
    pt2_results = None
    pt3_results = None

    if 1 in args.phases:
        pt1_results = run_pt1(base, layers, epsilons)

    if 2 in args.phases:
        pt2_results = run_pt2(base, pt1_results)

    if 3 in args.phases:
        pt3_results = run_pt3(base, pt1_results, epsilons)

    # --- Final summary ---
    print("\n" + "=" * 70)
    print("PHASE TRANSITION STUDY COMPLETE")
    print("=" * 70)

    if pt1_results:
        print(f"  PT-1: {pt1_results['n_phase_transitions_probe']} phase transitions "
              f"(best layer: {pt1_results['best_layer']})")
    if pt2_results:
        print(f"  PT-2: {pt2_results['n_fail']}/{pt2_results['n_traps']} traps fail at baseline "
              f"(failure rate: {pt2_results['failure_rate']*100:.1f}%)")
    if pt3_results:
        print(f"  PT-3: {pt3_results['n_phase_transitions']}/{pt3_results['n_ordinal_traps']} "
              f"ordinal traps [{pt3_results['classification']}]")

    print(f"\n  Results saved to: {base.output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
