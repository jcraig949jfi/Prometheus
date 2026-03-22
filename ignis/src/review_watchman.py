#!/usr/bin/env python3
"""Review Night Watchman scientific digests with narrative summaries.

Usage:
    python review_watchman.py --results-dir results/ignis
    python review_watchman.py --results-dir results/ignis --cycles 3
    python review_watchman.py --results-dir results/ignis --latest
"""

import argparse
import glob as glob_mod
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Force UTF-8 output on Windows consoles that default to cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_digests(history_path: Path) -> list[dict[str, Any]]:
    if not history_path.exists():
        raise FileNotFoundError(f"Watchman digest history not found: {history_path}")
    digests = []
    for line in history_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            digests.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return digests


# ---------------------------------------------------------------------------
# RPH eval loading
# ---------------------------------------------------------------------------

def load_rph_evals(results_dir: Path) -> list[dict[str, Any]]:
    """Load all rph_eval_*.json files from the results directory, newest first.

    Each file is a dict keyed by scale label ("0.5B", "3B", etc.) with per-scale
    RPH proxy results from eval_rph_survivors.py.  We wrap each in a container
    that also records the file timestamp for ordering.
    """
    pattern = str(results_dir / "rph_eval_*.json")
    paths = sorted(glob_mod.glob(pattern), reverse=True)  # newest first
    evals = []
    for p in paths:
        try:
            data = json.loads(Path(p).read_text(encoding="utf-8"))
            # Extract timestamp from filename: rph_eval_20260321_114530.json
            stem = Path(p).stem  # rph_eval_20260321_114530
            ts_part = stem.replace("rph_eval_", "")
            try:
                ts = datetime.strptime(ts_part, "%Y%m%d_%H%M%S")
            except ValueError:
                ts = None
            evals.append({"timestamp": ts, "path": p, "scales": data})
        except (json.JSONDecodeError, OSError):
            continue
    return evals


def _latest_rph_eval(results_dir: Path) -> Optional[dict[str, Any]]:
    """Return the most recent RPH eval, or None if none exist."""
    evals = load_rph_evals(results_dir)
    return evals[0] if evals else None


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _f(val: Any, places: int = 4) -> str:
    if val is None:
        return "-"
    if isinstance(val, float):
        return f"{val:.{places}f}"
    return str(val)


def _pct(val: Any) -> str:
    if val is None:
        return "-%"
    return f"{float(val):.0f}%"


def _top_corr_pair(digest: dict) -> Optional[tuple[str, float]]:
    """Return (pair_name, r) for the highest-|r| trap correlation pair."""
    corrs = digest.get("trap_correlations") or {}
    if not corrs:
        return None
    return max(corrs.items(), key=lambda kv: abs(kv[1]))


def _dominant_trap(digest: dict) -> Optional[tuple[str, dict]]:
    """Return (name, info) for the trap with highest credit_pct."""
    traps = digest.get("traps") or {}
    if not traps:
        return None
    return max(traps.items(), key=lambda kv: float(kv[1].get("credit_pct") or 0))


def _floor_traps(digest: dict) -> list[str]:
    """Return trap names where FLOOR% >= 90 (essentially never scoring)."""
    traps = digest.get("traps") or {}
    return [name for name, info in traps.items() if float(info.get("floor_pct") or 0) >= 90]


def _best_layer(digest: dict) -> Optional[tuple[str, float]]:
    """Return (layer_id, max_fitness) for the layer with highest max fitness."""
    layers = digest.get("layers") or {}
    if not layers:
        return None
    best = max(layers.items(), key=lambda kv: float(kv[1].get("max") or -999))
    return best[0], float(best[1].get("max") or 0)


def _native_layers(digest: dict) -> list[str]:
    """Return layer IDs that have any native circuit density."""
    lnd = digest.get("layer_native_density") or {}
    return [lid for lid, info in lnd.items() if float(info.get("density") or 0) > 0]


# ---------------------------------------------------------------------------
# Situation classifier
# ---------------------------------------------------------------------------

def _classify(digest: dict) -> set[str]:
    tags: set[str] = set()

    n = int(digest.get("total_genomes") or 0)
    compat = digest.get("compatibility") or {}
    native = int(compat.get("native_circuit_candidates") or 0)
    bypass = int(compat.get("artificial_bypass_candidates") or 0)
    cos_r = float(compat.get("cosine_fitness_corr") or 0.0)

    tc = digest.get("trap_coupling") or {}
    mean_abs_r = float(tc.get("mean_abs_r") or 0.0)

    trap_corrs = digest.get("trap_correlations") or {}
    max_corr_r = max((abs(v) for v in trap_corrs.values()), default=0.0)

    ft = digest.get("fitness_climb") or {}
    ft_delta = float(ft.get("delta") or 0.0)

    traps = digest.get("traps") or {}
    credit_vals = [float(t.get("credit_pct") or 0) for t in traps.values()]
    max_credit = max(credit_vals, default=0.0)
    floor_count = sum(1 for c in credit_vals if c < 10)

    falsif = digest.get("falsification") or {}
    pass_pct = float(falsif.get("pass_rate_pct") or 0)

    align = digest.get("alignment") or {}
    expr_fail_pct = float(align.get("expression_failure_pct") or 0)

    # --- Sample size ---
    if n < 30:
        tags.add("SMALL_N")
    if n >= 50:
        tags.add("CREDIBLE_N")
    if n >= 150:
        tags.add("LARGE_N")

    rolling = digest.get("rolling_correlation") or {}
    if rolling and len([v for v in rolling.values() if v is not None]) >= 2:
        latest_key = sorted(rolling.keys(), key=lambda x: int(x.split("_")[1]))[-1]
        latest_r = rolling.get(latest_key)
        if latest_r is not None and abs(latest_r) < 0.05:
            tags.add("ROLLING_STABLE")

    # --- Native / bypass state ---
    if native > 0 and bypass == 0:
        tags.add("NATIVE_LEADING")
    elif native > 0:
        tags.add("FIRST_NATIVE")

    if native == 0 and bypass > 5:
        if cos_r <= -0.05:
            tags.add("BYPASS_DOMINANT")
        else:
            tags.add("BYPASS_FORMING")

    if native == 0 and bypass > 20 and n > 100 and cos_r < -0.05:
        tags.add("NULL_CANDIDATE")

    if native == 0 and bypass > 40 and n > 150:
        tags.add("NULL_COMPLETE")

    # --- Trap coupling ---
    if mean_abs_r > 0.5:
        tags.add("COUPLING_STRONG")
    elif mean_abs_r > 0.3:
        tags.add("COUPLING_RISING")
    else:
        tags.add("COUPLING_FLAT")

    # --- Correlation signal relative to sample size ---
    if max_corr_r > 0.5:
        if "SMALL_N" in tags:
            tags.add("EARLY_SIGNAL")
        elif "CREDIBLE_N" in tags:
            tags.add("SIGNAL_HOLDING")
        else:
            tags.add("SIGNAL_MODERATE")

    # --- Trap skew ---
    if max_credit > 70 and floor_count >= 2:
        tags.add("TRAP_SKEW")

    # --- Fitness ---
    if ft_delta > 0.1:
        tags.add("FITNESS_CLIMBING")
    elif ft_delta < -0.05:
        tags.add("FITNESS_DECLINING")

    # --- Falsification ---
    if pass_pct >= 50:
        tags.add("FALSIF_PASSING")
    elif pass_pct >= 25:
        tags.add("FALSIF_WEAK")
    else:
        tags.add("FALSIF_FAILING")

    # --- Expression failures ---
    if expr_fail_pct > 15:
        tags.add("MARKER_GAP")

    # --- Trap balance ---
    tb = digest.get("trap_balance") or {}
    if float(tb.get("mean_min_trap") or 1.0) < 0.05 and float(tb.get("pct_floor") or 0) > 80:
        tags.add("TRAP_IMBALANCED")

    # --- Norm ratio ---
    nr = digest.get("norm_ratio") or {}
    nr_mean = float(nr.get("mean") or 1.0)
    if nr_mean > 1.5:
        tags.add("NORM_AMPLIFYING")
    elif nr_mean < 0.7:
        tags.add("NORM_SUPPRESSING")

    return tags


# ---------------------------------------------------------------------------
# Narrative paragraph builders
# ---------------------------------------------------------------------------

def _para_headline(digest: dict, tags: set[str]) -> str:
    n = int(digest.get("total_genomes") or 0)
    gen = digest.get("max_generation") or 0
    best = float(digest.get("best_fitness") or 0.0)
    compat = digest.get("compatibility") or {}
    native = int(compat.get("native_circuit_candidates") or 0)
    bypass = int(compat.get("artificial_bypass_candidates") or 0)
    cos_r = float(compat.get("cosine_fitness_corr") or 0.0)
    tc = digest.get("trap_coupling") or {}
    mean_abs_r = float(tc.get("mean_abs_r") or 0.0)
    top_pair = _top_corr_pair(digest)
    best_layer = _best_layer(digest)
    native_layers = _native_layers(digest)

    if "NATIVE_LEADING" in tags:
        layer_str = f" at Layer {', '.join(native_layers)}" if native_layers else ""
        return (
            f"Phase transition: native circuit candidates are now leading over bypass — "
            f"{native} native vs {bypass} bypass across {n} genomes (Gen {gen}){layer_str}. "
            f"Cosine-fitness correlation has moved to r={_f(cos_r, 3)}. "
            f"The search is finding vectors that are geometrically compatible with native residual flow, "
            f"not just routing around it. This is what the scale hypothesis predicts."
        )

    if "FIRST_NATIVE" in tags:
        return (
            f"First native circuit candidate detected: {native} genome with high fitness and "
            f"cos_with_residual > 0.3 across {n} genomes (Gen {gen}). "
            f"Bypass still leads at {bypass}, but the wall has been breached. "
            f"Watch whether the native count grows — if it does, the cosine-fitness correlation "
            f"should follow toward zero or positive."
        )

    if "EARLY_SIGNAL" in tags and top_pair:
        pair_name, pair_r = top_pair
        return (
            f"Early signal: {pair_name} shows r={_f(pair_r, 3)} at Gen {gen} with only {n} genomes. "
            f"The caveat is real — Pearson r is extremely unstable at small N and two correlated "
            f"random vectors can produce r={abs(pair_r):.2f} by chance. But the pairing isn't "
            f"arbitrary: these traps share structural overlap, which means co-activation would "
            f"follow task semantics if a shared circuit is present. "
            f"Trap coupling mean|r|={_f(mean_abs_r, 3)}. "
            f"The signal is tantalizing. Threshold to start believing it: still above r=0.5 at 50+ genomes."
        )

    if "SIGNAL_HOLDING" in tags and top_pair:
        pair_name, pair_r = top_pair
        return (
            f"Signal holding with credible N: {pair_name} at r={_f(pair_r, 3)} across {n} genomes "
            f"(Gen {gen}). At N={n}, Pearson r is meaningful — this is past the small-sample instability zone. "
            f"Trap coupling mean|r|={_f(mean_abs_r, 3)}. The co-activation is not random noise."
        )

    if "NULL_COMPLETE" in tags:
        layer_str = f" Best fitness {_f(best)}" + (f" at Layer {best_layer[0]}." if best_layer else ".")
        return (
            f"Null result is complete and clean: {bypass} bypass candidates, {native} native circuit "
            f"candidates across {n} genomes (Gen {gen}). Cosine-fitness correlation stable at "
            f"r={_f(cos_r, 3)} — the search is fully in bypass territory and not drifting.{layer_str} "
            f"This run has told its story. The data is ready for scale comparison."
        )

    if "NULL_CANDIDATE" in tags:
        return (
            f"Bypass dominance confirmed and persistent: {bypass} bypass candidates, {native} native "
            f"across {n} genomes (Gen {gen}). Cosine-fitness r={_f(cos_r, 3)} — stable negative. "
            f"CMA-ES is finding paths around the verification structure, not through it. "
            f"Best fitness {_f(best)}"
            + (f" at Layer {best_layer[0]}." if best_layer else ".")
        )

    if "BYPASS_DOMINANT" in tags:
        return (
            f"Bypass dominance forming: {bypass} artificial bypass candidates vs {native} native "
            f"circuit candidates across {n} genomes (Gen {gen}). "
            f"Cosine-fitness correlation r={_f(cos_r, 3)} is tracking negative — "
            f"high-fitness vectors are orthogonal to native residual flow. Best fitness {_f(best)}."
        )

    if "BYPASS_FORMING" in tags:
        return (
            f"Early bypass signal across {n} genomes (Gen {gen}): {bypass} high-fitness genomes "
            f"are orthogonal to native computation, {native} native candidates. "
            f"Cosine-fitness r={_f(cos_r, 3)} hasn't fully committed yet. Best fitness {_f(best)}."
        )

    # Neutral / too early
    return (
        f"Gen {gen}, {n} genomes, best fitness {_f(best)}. "
        f"Bypass={bypass}, native={native}, cosine-fitness r={_f(cos_r, 3)}. "
        f"No dominant pattern established yet — accumulating data."
    )


def _para_trap_detail(digest: dict, tags: set[str]) -> Optional[str]:
    traps = digest.get("traps") or {}
    if not traps:
        return None

    dom = _dominant_trap(digest)
    floor_names = _floor_traps(digest)
    top_pair = _top_corr_pair(digest)

    if "TRAP_SKEW" in tags and dom and floor_names:
        dom_name, dom_info = dom
        dom_credit = float(dom_info.get("credit_pct") or 0)
        floor_str = " and ".join(floor_names)
        are = "is" if len(floor_names) == 1 else "are"
        body = (
            f"Trap performance is skewed: {dom_name} is absorbing most of the fitness signal "
            f"at {_pct(dom_credit)} CREDIT while {floor_str} {are} sitting near floor. "
            f"CMA-ES is effectively optimizing for a single trap with the others as noise — "
            f"bypass vectors found for one trap aren't generalizing across the full task."
        )
        if top_pair:
            pair_name, pair_r = top_pair
            interp = "a meaningful shared-mechanism signal" if abs(pair_r) > 0.3 else "within noise"
            body += (
                f" Correlation-wise, {pair_name} shows r={_f(pair_r, 3)} — {interp}."
            )
        return body

    # Non-skewed — produce a compact credit table line
    parts = [f"{name}: {_pct(float(info.get('credit_pct') or 0))} CREDIT" for name, info in traps.items()]
    if top_pair:
        pair_name, pair_r = top_pair
        parts.append(f"top correlation {pair_name} r={_f(pair_r, 3)}")
    return "Trap breakdown — " + ", ".join(parts) + "."


def _para_trap_coupling(digest: dict, tags: set[str]) -> Optional[str]:
    tc = digest.get("trap_coupling") or {}
    mean_abs_r = float(tc.get("mean_abs_r") or 0.0)
    if mean_abs_r < 0.15:
        return None

    top_pair = _top_corr_pair(digest)
    n_pairs = tc.get("n_pairs", "?")

    if "COUPLING_STRONG" in tags:
        if top_pair:
            pair_name, pair_r = top_pair
            return (
                f"Trap coupling is strong: mean|r|={_f(mean_abs_r, 3)} across {n_pairs} pairs. "
                f"Lead signal: {pair_name} at r={_f(pair_r, 3)}. "
                f"Vectors that help one trap are reliably co-activating (or suppressing) others — "
                f"this is the shared-mechanism signature."
            )
        return f"Trap coupling strong: mean|r|={_f(mean_abs_r, 3)} across {n_pairs} pairs."

    if "COUPLING_RISING" in tags:
        if top_pair:
            pair_name, pair_r = top_pair
            return (
                f"Trap coupling rising: mean|r|={_f(mean_abs_r, 3)} across {n_pairs} pairs. "
                f"Top signal: {pair_name} r={_f(pair_r, 3)}. "
                f"Above the noise floor — watch whether this holds or climbs further."
            )
        return f"Trap coupling rising: mean|r|={_f(mean_abs_r, 3)} across {n_pairs} pairs."

    return f"Trap coupling: mean|r|={_f(mean_abs_r, 3)} ({n_pairs} pairs) — within noise."


def _para_rolling_corr(digest: dict, tags: set[str]) -> Optional[str]:
    rolling = digest.get("rolling_correlation") or {}
    if not rolling:
        return None

    entries = []
    for k in sorted(rolling.keys(), key=lambda x: int(x.split("_")[1])):
        entries.append(f"{k[2:]}={_f(rolling[k], 3)}")
    summary = ", ".join(entries)

    if any(abs(v) < 0.05 for v in rolling.values() if v is not None):
        note = "Correlation is stable near zero across milestones; small-N instability appears resolved."
    else:
        note = "Correlation is varying; watch for potential instability with small sample sizes."
    return f"Rolling trap correlation (Decimal Mag × Density Illusion): {summary}. {note}"


def _para_model_separation(digest: dict) -> Optional[str]:
    """Surface per-model cos_fit_r when multiple model logs are present.

    When multiple model subdirectories coexist (e.g., 3B still on disk while 1.5B runs),
    the Watchman computes per-model cos_fit_r to prevent cross-model artifacts.
    This paragraph makes the breakdown visible so mixed-model spurious signals are
    immediately flagged rather than silently inflating the headline r.
    """
    compat = digest.get("compatibility") or {}
    per_model = compat.get("per_model_cos_r") or {}
    active = compat.get("active_model")
    if not per_model or len(per_model) <= 1:
        return None  # Only useful when multiple models are present

    lines = []
    for model_key, r_val in sorted(per_model.items()):
        label = model_key.replace("qwen_qwen2_5-", "Qwen2.5-").replace("-instruct", "-Instruct").replace("_", "-")
        tag = " [ACTIVE]" if model_key == active else ""
        r_str = f"{r_val:.4f}" if r_val is not None else "n/a"
        lines.append(f"{label}: r={r_str}{tag}")

    primary_r = compat.get("cosine_fitness_corr")
    primary_str = f"{primary_r:.4f}" if primary_r is not None else "n/a"

    return (
        f"Per-model cos-fitness correlation (active model r={primary_str} used as primary): "
        + ", ".join(lines) + ". "
        "Cross-model r values are structural artifacts — each model scale has a different "
        "cos_with_residual baseline. Only the active model's within-run r is scientifically meaningful."
    )


def _para_falsification(digest: dict, tags: set[str]) -> Optional[str]:
    falsif = digest.get("falsification") or {}
    if not falsif:
        return None

    pass_pct = float(falsif.get("pass_rate_pct") or 0)
    flip_pct = float(falsif.get("sign_flip_pct") or 0)
    margin = float(falsif.get("mean_margin") or 0.0)
    max_margin = falsif.get("max_margin")
    n_tests = int(falsif.get("total") or 0)

    max_margin_str = f", best genome margin {_f(max_margin, 4)}" if max_margin is not None else ""

    if "FALSIF_FAILING" in tags:
        return (
            f"Falsification: {_pct(pass_pct)} pass rate ({n_tests} tests), "
            f"mean directional margin {_f(margin, 4)}{max_margin_str}, sign-flip asymmetry {_pct(flip_pct)}. "
            f"Weak directional evidence relative to noise/ortho/shuffle controls -- "
            f"consistent with bypass behavior. Genuine circuit vectors show a peaked, "
            f"directional response that these don't."
        )

    if "FALSIF_WEAK" in tags:
        return (
            f"Falsification: {_pct(pass_pct)} pass rate ({n_tests} tests), "
            f"mean margin {_f(margin, 4)}{max_margin_str}, sign-flip {_pct(flip_pct)}. "
            f"Weak but not zero -- watch whether this climbs as native candidates accumulate."
        )

    if "FALSIF_PASSING" in tags:
        return (
            f"Falsification passing at {_pct(pass_pct)} ({n_tests} tests), "
            f"mean margin {_f(margin, 4)}{max_margin_str}, sign-flip {_pct(flip_pct)}. "
            f"Strong directional evidence -- vectors are beating noise/ortho/shuffle controls."
        )

    return None


def _para_fitness(digest: dict, tags: set[str]) -> Optional[str]:
    ft = digest.get("fitness_climb") or {}
    if not ft:
        return None

    first = float(ft.get("first_fit") or 0)
    last = float(ft.get("last_fit") or 0)
    delta = float(ft.get("delta") or 0)
    best = float(digest.get("best_fitness") or 0.0)
    best_layer = _best_layer(digest)
    layer_str = f" at Layer {best_layer[0]}" if best_layer else ""

    if "FITNESS_DECLINING" in tags:
        return (
            f"Per-generation best trajectory: {_f(first)} -> {_f(last)} (D={_f(delta, 4)}). "
            f"This decline doesn't mean the run is failing -- the overall best is {_f(best)}{layer_str}, "
            f"and per-gen bests naturally shrink as CMA-ES tightens its search radius around "
            f"an already-exploited basin (sigma shrinkage and plateau decay). "
            f"This is normal convergence behavior, not divergence."
        )

    if "FITNESS_CLIMBING" in tags:
        return (
            f"Fitness climbing: per-gen trajectory {_f(first)} -> {_f(last)} (D={_f(delta, 4)}), "
            f"overall best {_f(best)}{layer_str}. Active improvement phase."
        )

    return None


def _para_alignment(digest: dict, tags: set[str]) -> Optional[str]:
    align = digest.get("alignment") or {}
    if not align:
        return None

    expr_fail_pct = float(align.get("expression_failure_pct") or 0)
    n_failures = int(align.get("expression_failures") or 0)
    mean_gap = float(align.get("mean_gap") or 0)

    if "MARKER_GAP" in tags:
        return (
            f"Expression failures at {_pct(expr_fail_pct)} ({n_failures} genomes): "
            f"high logit scores not converting to marker CREDIT. Mean logit-marker gap: {_f(mean_gap, 4)}. "
            f"This is a marker coverage problem, not a capability gap — the model may be getting "
            f"the answer right but phrasing it in a way the marker regex doesn't catch. Fixable at eval time."
        )

    if expr_fail_pct > 5:
        return (
            f"Marker-logit alignment: mean gap {_f(mean_gap, 4)}, "
            f"{_pct(expr_fail_pct)} expression failures. Modest but worth watching."
        )

    return None


def _para_zones(digest: dict, tags: set[str]) -> Optional[str]:
    zones = digest.get("zones") or {}
    if not zones:
        return None

    dead  = zones.get("dead") or {}
    prod  = zones.get("productive") or {}
    dest  = zones.get("destructive") or {}

    dead_pct = float(dead.get("pct") or 0)
    prod_pct = float(prod.get("pct") or 0)
    dest_pct = float(dest.get("pct") or 0)
    dead_n   = int(dead.get("count") or 0)
    prod_n   = int(prod.get("count") or 0)
    dest_n   = int(dest.get("count") or 0)

    if prod_pct >= 30:
        note = "High productive fraction -- search is finding useful directions."
    elif prod_pct >= 15:
        note = "Moderate productive fraction."
    elif prod_pct >= 5:
        note = "Low productive fraction -- most evaluations returning noise."
    else:
        note = "Very low productive fraction -- search space appears sparse."

    return (
        f"Zone distribution: {dead_pct:.0f}% dead ({dead_n}), "
        f"{prod_pct:.0f}% productive ({prod_n}), "
        f"{dest_pct:.0f}% destructive ({dest_n}). {note}"
    )


def _para_trap_balance(digest: dict, tags: set[str]) -> Optional[str]:
    """Narrate trap balance — are genomes consistently failing at least one trap?"""
    tb = digest.get("trap_balance") or {}
    if not tb:
        return None

    mean_min = float(tb.get("mean_min_trap") or 0)
    worst    = float(tb.get("worst_min_trap") or 0)
    pct_fl   = float(tb.get("pct_floor") or 0)
    n        = int(tb.get("n") or 0)

    if pct_fl > 80:
        note = (
            "search is specializing rather than generalizing — "
            "most genomes ace some traps but completely fail at least one"
        )
    elif pct_fl > 50:
        note = (
            "majority of genomes still bottleneck on at least one trap, "
            "but some are finding balanced solutions"
        )
    elif pct_fl > 20:
        note = "moderate imbalance — a minority of genomes hit the floor on their weakest trap"
    else:
        note = "search is finding balanced solutions — few genomes bottom out on any single trap"

    return (
        f"Trap balance: mean weakest-trap score {mean_min:.4f} across {n} genomes. "
        f"{pct_fl:.1f}% hit the floor on at least one trap — {note}."
    )


def _para_scout_layers(digest: dict, tags: set[str]) -> Optional[str]:
    """Narrate scout layer exploration from the scout_layer_map CSV data."""
    slm = digest.get("scout_layer_map") or {}
    summary = slm.get("_summary")
    if not summary:
        return None

    total_layers = int(summary.get("total_layers") or 0)
    total_evals  = int(summary.get("total_evals") or 0)
    prod_layers  = int(summary.get("productive_layers") or 0)

    if total_layers == 0:
        return None

    # Find the top layer by best_fitness
    layer_entries = {k: v for k, v in slm.items() if k != "_summary"}
    if layer_entries:
        top_layer = max(layer_entries.items(), key=lambda kv: kv[1].get("best_fitness", 0))
        top_str = f" Top layer: {top_layer[0]} (fitness {top_layer[1]['best_fitness']:.4f})."
    else:
        top_str = ""

    if prod_layers == 0:
        note = "No scout layers above baseline — all explored depths are unproductive."
    elif prod_layers == total_layers:
        note = "All explored layers above baseline."
    else:
        note = f"{prod_layers} of {total_layers} explored layers above baseline."

    return (
        f"Scout map: {total_layers} layers explored across {total_evals} evals. "
        f"{note}{top_str}"
    )


def _para_norm_ratio(digest: dict, tags: set[str]) -> Optional[str]:
    """Narrate injection norm ratio — how aggressively the steering vector changes residual norms."""
    nr = digest.get("norm_ratio") or {}
    if not nr:
        return None

    mean_val = float(nr.get("mean") or 1.0)
    min_val  = float(nr.get("min") or 1.0)
    max_val  = float(nr.get("max") or 1.0)
    pct_amp  = float(nr.get("pct_above_1") or 0)
    n        = int(nr.get("n") or 0)

    if mean_val > 2.0:
        note = (
            "steering is aggressive — injections are substantially amplifying "
            "residual stream norms, which may indicate brute-force bypass rather "
            "than gentle native-direction nudging"
        )
    elif mean_val > 1.2:
        note = (
            "steering is moderately aggressive — injections amplify norms but "
            "not overwhelmingly"
        )
    elif mean_val > 0.95:
        note = (
            "steering is gentle — norm ratios near 1.0 suggest the vector "
            "integrates smoothly into the residual stream without distorting it"
        )
    elif mean_val > 0.7:
        note = "steering is slightly suppressive — injections reduce residual norms"
    else:
        note = (
            "steering is suppressive — injections substantially dampen residual "
            "norms, which could indicate destructive interference"
        )

    return (
        f"Norm ratio (post/pre injection): mean {mean_val:.4f}, "
        f"range [{min_val:.4f}, {max_val:.4f}], "
        f"{pct_amp:.1f}% amplify (ratio > 1.0) across {n} genomes — {note}."
    )


def _para_logit_selectivity(digest: dict, tags: set[str]) -> Optional[str]:
    sel = digest.get("logit_selectivity") or {}
    if not sel:
        return None

    mean = sel.get("mean")
    if mean is None:
        return None

    mean_val    = float(mean)
    high_n      = int(sel.get("high_selectivity") or 0)
    high_pct    = float(sel.get("high_selectivity_pct") or 0)
    n           = int(sel.get("n") or 0)

    if mean_val < -0.1:
        sign_note = "net suppressing correct tokens relative to incorrect ones"
    elif mean_val < -0.01:
        sign_note = "slight net suppression of correct token logits"
    elif mean_val < 0.01:
        sign_note = "approximately neutral logit effect"
    elif mean_val < 0.1:
        sign_note = "slight net amplification of correct token logits"
    else:
        sign_note = "net amplifying correct tokens over incorrect ones"

    high_str = (
        f" High-selectivity genomes (delta > 0.5): {high_n} ({high_pct:.0f}%)."
        if high_n > 0
        else " No high-selectivity genomes (delta > 0.5)."
    )

    return (
        f"Logit selectivity: mean delta (correct - wrong) = {mean_val:.4f} across {n} genomes "
        f"-- {sign_note}.{high_str}"
    )


# ---------------------------------------------------------------------------
# RPH eval narrative paragraphs
# ---------------------------------------------------------------------------

_RPH_CLASS_EXPLAIN = {
    "PRECIPITATION_CANDIDATE": (
        "The steering vector passes at least two of the three RPH proxy criteria "
        "(Δ_cf, MI_step, Δ_proj). This means the vector is producing behavior consistent "
        "with genuine reasoning precipitation: steered outputs change meaningfully when "
        "input facts change (counterfactual sensitivity), and later token representations "
        "carry information about earlier ones (stepwise mutual information). "
        "This is what a native reasoning circuit vector looks like."
    ),
    "WEAK_SIGNAL": (
        "Exactly one RPH criterion passes. The vector shows partial evidence of "
        "precipitation behavior — it's not pure bypass, but doesn't clear the bar "
        "for a confident precipitation claim either. Could be a vector that partially "
        "engages native circuitry while still relying on shortcut pathways."
    ),
    "NULL": (
        "No RPH criteria pass. The vector is statistically indistinguishable from "
        "a bypass or random perturbation — it achieves fitness by routing around "
        "the model's verification structure rather than through it."
    ),
}


def _para_rph_eval(rph_eval: Optional[dict], tags: set[str]) -> Optional[str]:
    """Build narrative paragraph from eval_rph_survivors output."""
    if not rph_eval:
        return None

    scales = rph_eval.get("scales") or {}
    if not scales:
        return None

    ts = rph_eval.get("timestamp")
    ts_str = ts.strftime("%Y-%m-%d %H:%M") if ts else "unknown time"

    parts = [f"RPH proxy evaluation ({ts_str}):"]

    for scale in ["0.5B", "1.5B", "3B", "7B"]:
        r = scales.get(scale)
        if not r:
            continue

        classification = r.get("classification", "NULL")
        delta_cf = r.get("delta_cf", 0.0)
        delta_cf_p = r.get("delta_cf_p", 1.0)
        delta_cf_d = r.get("delta_cf_cohens_d", 0.0)
        cf_passes = r.get("delta_cf_passes", False)
        mi_step = r.get("mi_step", 0.0)
        mi_lo = r.get("mi_ci_low", 0.0)
        mi_hi = r.get("mi_ci_high", 0.0)
        mi_passes = r.get("mi_step_passes", False)
        n_passes = r.get("passes", 0)
        n_pairs = r.get("pairs_scored", 0)
        fitness = r.get("fitness", 0.0)
        layer = r.get("layer", "?")
        base_cf = r.get("base_delta_cf")

        # Build per-scale summary
        cf_verdict = "PASS" if cf_passes else "FAIL"
        mi_verdict = "PASS" if mi_passes else "FAIL"

        line = (
            f"\n  {scale} (layer {layer}, fitness {fitness:.4f}, {n_pairs} pairs scored):\n"
            f"    Δ_cf = {delta_cf:.4f} (Cohen's d={delta_cf_d:.3f}, p={delta_cf_p:.4f}) [{cf_verdict}]"
        )
        if base_cf is not None:
            uplift = delta_cf - base_cf
            line += f"  —  baseline Δ_cf={base_cf:.4f}, uplift={uplift:+.4f}"
        line += (
            f"\n    MI_step = {mi_step:.4f} (95% CI [{mi_lo:.4f}, {mi_hi:.4f}]) [{mi_verdict}]"
            f"\n    → {classification} ({n_passes}/3 criteria pass)"
        )

        parts.append(line)

    if len(parts) <= 1:
        return None

    return "\n".join(parts)


def _para_rph_explain(rph_eval: Optional[dict]) -> Optional[str]:
    """Plain-English explanation of what the RPH classifications mean."""
    if not rph_eval:
        return None

    scales = rph_eval.get("scales") or {}
    if not scales:
        return None

    # Find the classification(s) present
    classes_seen = set()
    for r in scales.values():
        classes_seen.add(r.get("classification", "NULL"))

    explanations = []
    for cls in ["PRECIPITATION_CANDIDATE", "WEAK_SIGNAL", "NULL"]:
        if cls in classes_seen:
            explanations.append(f"  {cls}: {_RPH_CLASS_EXPLAIN.get(cls, '')}")

    if not explanations:
        return None

    return "What the RPH classifications mean:\n" + "\n".join(explanations)


def _para_rph_scale_gradient(rph_eval: Optional[dict]) -> Optional[str]:
    """Narrate the cross-scale gradient — the core RPH prediction."""
    if not rph_eval:
        return None

    scales = rph_eval.get("scales") or {}
    ordered = [(s, scales[s]) for s in ["0.5B", "1.5B", "3B", "7B"] if s in scales]
    if len(ordered) < 2:
        return None

    # Track whether classification improves with scale
    class_rank = {"NULL": 0, "WEAK_SIGNAL": 1, "PRECIPITATION_CANDIDATE": 2}
    ranks = [(s, class_rank.get(r.get("classification", "NULL"), 0)) for s, r in ordered]
    improving = all(ranks[i][1] <= ranks[i + 1][1] for i in range(len(ranks) - 1))
    any_precip = any(r[1] == 2 for r in ranks)
    all_null = all(r[1] == 0 for r in ranks)

    # Track delta_cf trend
    cf_values = [(s, r.get("delta_cf", 0.0)) for s, r in ordered]
    cf_increasing = all(cf_values[i][1] <= cf_values[i + 1][1] for i in range(len(cf_values) - 1))

    if all_null:
        return (
            f"Scale gradient: all evaluated scales ({', '.join(s for s, _ in ordered)}) "
            f"classify as NULL. No precipitation signal at any scale tested. "
            f"The RPH predicts that precipitation emerges at sufficient model capacity — "
            f"either the threshold hasn't been reached, or the steering vectors found by "
            f"CMA-ES are fundamentally bypass vectors at every scale."
        )

    if improving and any_precip:
        precip_scale = [s for s, r in ranks if r == 2][0]
        return (
            f"Scale gradient supports RPH: classification improves monotonically with scale, "
            f"reaching PRECIPITATION_CANDIDATE at {precip_scale}. "
            f"Δ_cf {'also increases with scale' if cf_increasing else 'does not increase monotonically — partial support'}. "
            f"This is the signature the Reasoning Precipitation Hypothesis predicts: "
            f"larger models have deeper native reasoning circuits, and CMA-ES finds vectors "
            f"that engage those circuits rather than routing around them."
        )

    if any_precip and not improving:
        precip_scales = [s for s, r in ranks if r == 2]
        return (
            f"Scale gradient is non-monotonic: PRECIPITATION_CANDIDATE at {', '.join(precip_scales)} "
            f"but not consistently improving with scale. This could indicate scale-specific "
            f"circuit topology differences — the CMA-ES search may find different solution "
            f"families at different scales rather than a clean gradient."
        )

    # Mixed weak/null
    weak_scales = [s for s, r in ranks if r == 1]
    return (
        f"Scale gradient: WEAK_SIGNAL at {', '.join(weak_scales)}, "
        f"NULL elsewhere. Partial precipitation behavior is emerging but hasn't "
        f"crossed the threshold at any scale. The vectors are partially engaging "
        f"native circuitry — more generations or a larger model may push them over."
    )


def _para_rph_cross_ref(rph_eval: Optional[dict], digest: dict,
                         tags: set[str]) -> Optional[str]:
    """Cross-reference RPH eval results with the watchman's live classification."""
    if not rph_eval:
        return None

    scales = rph_eval.get("scales") or {}
    if not scales:
        return None

    # Get the watchman's verdict on the current run
    compat = digest.get("compatibility") or {}
    native = int(compat.get("native_circuit_candidates") or 0)
    bypass = int(compat.get("artificial_bypass_candidates") or 0)
    cos_r = float(compat.get("cosine_fitness_corr") or 0.0)

    # Determine the active model's scale from the watchman data
    active_key = compat.get("active_model") or ""
    active_scale = None
    for slug, label in [("0_5b", "0.5B"), ("1_5b", "1.5B"), ("3b", "3B"), ("7b", "7B")]:
        if slug in active_key:
            active_scale = label
            break

    # Find matching RPH eval for the active scale
    active_rph = scales.get(active_scale) if active_scale else None

    if not active_rph:
        # No RPH eval for the currently running model — note that
        eval_scales = ", ".join(scales.keys())
        note = f"RPH eval covers {eval_scales}"
        if active_scale:
            note += f" but the active run is {active_scale} (not yet evaluated)"
        else:
            note += " — active model scale could not be determined from watchman data"
        return f"Cross-reference: {note}."

    rph_class = active_rph.get("classification", "NULL")
    rph_passes = active_rph.get("passes", 0)

    # Build cross-reference narrative
    if "BYPASS_DOMINANT" in tags or "NULL_CANDIDATE" in tags or "NULL_COMPLETE" in tags:
        watchman_says = "bypass/null"
        if rph_class == "NULL":
            return (
                f"Cross-reference ({active_scale}): watchman and RPH eval agree — "
                f"watchman sees bypass dominance (cos-fitness r={cos_r:.3f}, "
                f"{bypass} bypass / {native} native), and the RPH eval confirms NULL "
                f"({rph_passes}/3 criteria). The steering vector achieves fitness by "
                f"routing around verification, not through native reasoning circuits."
            )
        elif rph_class == "WEAK_SIGNAL":
            return (
                f"Cross-reference ({active_scale}): partial disagreement — "
                f"watchman classifies as bypass (cos-fitness r={cos_r:.3f}), "
                f"but RPH eval shows WEAK_SIGNAL ({rph_passes}/3 criteria). "
                f"The vector may be partially engaging native circuitry despite "
                f"the geometric signature looking like bypass. Worth investigating "
                f"which criterion passed."
            )
        else:
            return (
                f"Cross-reference ({active_scale}): DISAGREEMENT — "
                f"watchman sees bypass dominance but RPH eval classifies as "
                f"PRECIPITATION_CANDIDATE ({rph_passes}/3 criteria). "
                f"This is surprising and warrants closer inspection. "
                f"Possible explanations: the cosine-fitness correlation may not "
                f"fully capture precipitation behavior, or the RPH eval prompts "
                f"are eliciting different behavior than the Ignis fitness traps."
            )

    if "NATIVE_LEADING" in tags or "FIRST_NATIVE" in tags:
        if rph_class == "PRECIPITATION_CANDIDATE":
            return (
                f"Cross-reference ({active_scale}): watchman and RPH eval converge — "
                f"watchman sees native circuit candidates emerging ({native} native, "
                f"cos-fitness r={cos_r:.3f}), and RPH eval confirms "
                f"PRECIPITATION_CANDIDATE ({rph_passes}/3 criteria). "
                f"Both lines of evidence point to genuine precipitation behavior."
            )
        elif rph_class == "NULL":
            return (
                f"Cross-reference ({active_scale}): DISAGREEMENT — "
                f"watchman sees native candidates ({native}) but RPH eval classifies "
                f"as NULL ({rph_passes}/3 criteria). The geometric compatibility "
                f"(positive cos_with_residual) isn't translating into counterfactual "
                f"sensitivity or MI structure. The 'native' candidates may be "
                f"geometrically aligned but functionally bypass."
            )

    # Generic fallback
    return (
        f"Cross-reference ({active_scale}): RPH eval = {rph_class} "
        f"({rph_passes}/3), watchman = {bypass} bypass / {native} native, "
        f"cos-fitness r={cos_r:.3f}."
    )


def _para_cmaes(digest: dict, tags: set[str]) -> Optional[str]:
    state = digest.get("cma_state") or {}
    drift = digest.get("vector_drift") or {}
    if not state:
        return None

    parts = []
    for key, info in state.items():
        if not isinstance(info, dict):
            continue
        err = info.get("error")
        if err:
            parts.append(f"  {key}: state unavailable ({err})")
            continue
        sigma = info.get("sigma")
        gen = info.get("gen_count")
        best = info.get("best_fitness")
        plateau = info.get("plateau_count") or 0
        mean_norm = info.get("mean_norm")

        # Pretty label: strip "_state" suffix, extract size token (e.g. "0_5b", "3b", "7b")
        name_clean = key.replace("_state", "")
        parts_label = name_clean.split("-")
        size_tok = next((p for p in reversed(parts_label) if p and p[-1] == "b" and p[0].isdigit()), None)
        label = size_tok if size_tok else name_clean.split("_")[0]

        detail = f"σ={_f(sigma, 6)}, gen={gen}, best={_f(best, 4)}"
        if plateau > 0:
            detail += f", plateau={plateau}"
        if mean_norm is not None:
            detail += f", mean_norm={_f(mean_norm, 2)}"

        # Add norm ratio from vector_drift (best_norm / inception_norm)
        drift_info = drift.get(name_clean) or {}
        if drift_info:
            inception_norm = drift_info.get("inception_norm")
            best_norm_val = drift_info.get("best_norm")
            if inception_norm and best_norm_val and float(inception_norm) > 0:
                ratio = float(best_norm_val) / float(inception_norm)
                ratio_note = ""
                if ratio > 1.5:
                    ratio_note = " [inflating]"
                elif ratio < 0.7:
                    ratio_note = " [contracting]"
                detail += f", norm_ratio={ratio:.2f}{ratio_note}"

        parts.append(f"  {label}: {detail}")

    if not parts:
        return None
    return "CMA-ES state:\n" + "\n".join(parts)


def _para_bottom_line(digest: dict, tags: set[str]) -> str:
    n = int(digest.get("total_genomes") or 0)
    gen = digest.get("max_generation") or 0

    if "NATIVE_LEADING" in tags:
        return (
            "Bottom line: Phase transition underway. Keep running and watch whether "
            "native count continues to climb and cosine-fitness correlation turns positive."
        )

    if "FIRST_NATIVE" in tags:
        return (
            "Bottom line: First breach. The null hypothesis is no longer clean. "
            "Run more — one candidate needs company before it means anything."
        )

    if "NULL_COMPLETE" in tags:
        return (
            "Bottom line: Null result confirmed and complete. "
            "Move to next scale — this run has delivered its baseline data."
        )

    if "NULL_CANDIDATE" in tags:
        return (
            f"Bottom line: Null result forming cleanly at {n} genomes (Gen {gen}). "
            "Bypass dominance is persistent and the cosine-fitness correlation is stable. "
            "This run is approaching its information limit."
        )

    if "EARLY_SIGNAL" in tags and "COUPLING_RISING" in tags:
        return (
            "Bottom line: Let it run. The next few digests will tell you whether "
            "the trap co-activation is real or small-N noise. "
            "Watch for it to hold above r=0.5 at 50+ genomes."
        )

    if "EARLY_SIGNAL" in tags:
        return (
            "Bottom line: Promising but too early to trust. "
            "Need 50+ genomes before acting on the correlation signal."
        )

    if "SIGNAL_HOLDING" in tags:
        return (
            "Bottom line: Signal is credible. Watch whether trap coupling continues "
            "to rise and cosine-fitness correlation moves toward zero or positive."
        )

    if "BYPASS_DOMINANT" in tags:
        return (
            "Bottom line: Bypass dominance established. "
            "Scale hypothesis predicts this resolves at higher model scale."
        )

    if "BYPASS_FORMING" in tags:
        if "CREDIBLE_N" in tags:
            return (
                "Bottom line: Bypass forming but cosine-fitness correlation hasn't committed. "
                "Watch whether it drifts negative as generations accumulate."
            )
        return (
            "Bottom line: Bypass pattern emerging. "
            "Let it accumulate to 50+ genomes for a cleaner picture."
        )

    return (
        "Bottom line: Run is active, no dominant signal yet. "
        "Continue accumulating data."
    )


# ---------------------------------------------------------------------------
# Full narrative assembly
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Comparison narrative (oldest -> latest)
# ---------------------------------------------------------------------------

def _compare_narrative(old: dict, new: dict) -> str:
    old_n = int(old.get("total_genomes") or 0)
    new_n = int(new.get("total_genomes") or 0)
    old_gen = old.get("max_generation") or 0
    new_gen = new.get("max_generation") or 0

    old_compat = old.get("compatibility") or {}
    new_compat = new.get("compatibility") or {}
    old_bypass = int(old_compat.get("artificial_bypass_candidates") or 0)
    new_bypass = int(new_compat.get("artificial_bypass_candidates") or 0)
    old_native = int(old_compat.get("native_circuit_candidates") or 0)
    new_native = int(new_compat.get("native_circuit_candidates") or 0)
    old_cos = float(old_compat.get("cosine_fitness_corr") or 0)
    new_cos = float(new_compat.get("cosine_fitness_corr") or 0)

    old_tc = float((old.get("trap_coupling") or {}).get("mean_abs_r") or 0)
    new_tc = float((new.get("trap_coupling") or {}).get("mean_abs_r") or 0)

    old_best = float(old.get("best_fitness") or 0)
    new_best = float(new.get("best_fitness") or 0)

    lines = [
        f"Since last digest ({old_n}->{new_n} genomes, Gen {old_gen}->{new_gen}):",
        f"  Best fitness:   {_f(old_best)} -> {_f(new_best)}  (D={_f(new_best - old_best, 4)})",
        f"  Bypass:         {old_bypass} -> {new_bypass}",
        f"  Native:         {old_native} -> {new_native}",
        f"  cos-fitness r:  {_f(old_cos, 3)} -> {_f(new_cos, 3)}",
        f"  Trap coupling:  {_f(old_tc, 3)} -> {_f(new_tc, 3)}",
    ]

    # Qualitative call-outs
    if new_native > old_native and new_native > 0:
        lines.append("  [+] Native candidates emerging -- watch the cosine-fitness correlation.")
    elif new_native == 0 and old_native == 0 and new_bypass - old_bypass > 10:
        lines.append("  [!] Bypass count climbing rapidly. Null result firming up.")

    cos_drift = abs(new_cos - old_cos)
    if cos_drift < 0.02 and new_bypass > 10:
        lines.append("  [=] Cosine-fitness correlation stable -- bypass pattern is locked in.")
    elif new_cos > old_cos + 0.05:
        lines.append(f"  [+] Cosine-fitness correlation shifting positive ({_f(old_cos,3)}->{_f(new_cos,3)}) -- promising.")
    elif new_cos < old_cos - 0.05:
        lines.append(f"  [-] Cosine-fitness correlation drifting more negative ({_f(old_cos,3)}->{_f(new_cos,3)}).")

    if new_tc > old_tc + 0.05:
        lines.append(f"  [+] Trap coupling rising ({_f(old_tc,3)}->{_f(new_tc,3)}) -- shared-mechanism signal strengthening.")
    elif new_tc < old_tc - 0.05:
        lines.append(f"  [-] Trap coupling declining ({_f(old_tc,3)}->{_f(new_tc,3)}) -- signal may be washing out.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ETA / throughput engine
# ---------------------------------------------------------------------------

def _fmt_duration(seconds: int) -> str:
    """Format seconds as compact human-readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"
    elif seconds < 86400:
        h, rem = divmod(seconds, 3600)
        m = rem // 60
        return f"{h}h {m}m"
    else:
        d, rem = divmod(seconds, 86400)
        h = rem // 3600
        return f"{d}d {h}h"


def _active_model_label(digest: dict) -> str:
    """Extract a human-readable model label from the digest."""
    # Prefer active_model from compatibility dict (set by per-model mtime tracking,
    # most recently modified file = truly active model, not highest gen_count which
    # picks the completed model when a new run starts with gen=0).
    compat = digest.get("compatibility") or {}
    active_key = compat.get("active_model")
    if active_key:
        # active_key format: "qwen_qwen2_5-1_5b-instruct"
        name = active_key
        parts = name.replace("qwen_qwen2_5-", "").split("-")
        size = next((p for p in reversed(parts) if p and p[-1] == "b" and p[0].isdigit()), None)
        if size:
            size_str = size.replace("_", ".").upper()
            if "qwen2_5" in name or "qwen2-5" in name or "qwen_qwen2_5" in name:
                return f"Qwen2.5-{size_str}-Instruct"
            elif "qwen" in name:
                return f"Qwen-{size_str}-Instruct"
        return active_key

    # Fallback: cma_state keys (highest gen_count)
    state = digest.get("cma_state") or {}
    best_key = None
    best_gen = -1
    for key, info in state.items():
        if isinstance(info, dict):
            g = int(info.get("gen_count") or 0)
            if g > best_gen:
                best_gen = g
                best_key = key
    if not best_key:
        # Fall back to vector_drift
        drift = digest.get("vector_drift") or {}
        best_key = next(iter(drift), None)
    if not best_key:
        return "unknown"

    # Parse: qwen_qwen2_5-3b-instruct_state -> Qwen2.5-3B-Instruct
    name = best_key.replace("_state", "")
    parts = name.split("-")
    # Find size token (ends with 'b', starts with digit, e.g. '3b', '0_5b', '7b')
    size = next((p for p in reversed(parts) if p and p[-1] == "b" and p[0].isdigit()), None)
    if size:
        size_str = size.replace("_", ".").upper()  # 0_5b -> 0.5B
        # Detect family from name
        if "qwen2_5" in name or "qwen2-5" in name:
            return f"Qwen2.5-{size_str}-Instruct"
        elif "qwen" in name:
            return f"Qwen-{size_str}-Instruct"
        return size_str
    return name


def _compute_eta(digests: list[dict]) -> dict:
    """Compute throughput rate, trend, and ETA for next generation boundary.

    Uses window-based rate comparison (30 min vs 90 min) to detect deceleration
    rather than noisy per-interval regression.
    """
    # Build unified time series
    series: list[tuple[float, int, int]] = []  # (unix_ts, total_genomes, max_gen)
    for d in digests:
        ts_str = d.get("timestamp")
        n = d.get("total_genomes")
        if ts_str and n is not None:
            try:
                ts = datetime.fromisoformat(ts_str)
                series.append((ts.timestamp(), int(n or 0), int(d.get("max_generation") or 0)))
            except Exception:
                pass

    if len(series) < 3:
        return {}
    series.sort()

    # Detect most recent run restart (gen number goes backward = new run)
    run_start_idx = 0
    for i in range(1, len(series)):
        if series[i][2] < series[i - 1][2]:
            run_start_idx = i
    run = series[run_start_idx:]
    if len(run) < 3:
        return {}

    # --- Estimate genomes per generation from gen transitions ---
    gen_first_seen: dict[int, int] = {}  # gen -> genome count when first seen
    for _, n, gen in run:
        if gen not in gen_first_seen:
            gen_first_seen[gen] = n

    gen_sizes = []
    sorted_gens = sorted(gen_first_seen)
    for i in range(1, len(sorted_gens)):
        size = gen_first_seen[sorted_gens[i]] - gen_first_seen[sorted_gens[i - 1]]
        if 5 < size < 500:
            gen_sizes.append(size)
    genomes_per_gen: Optional[int] = None
    if gen_sizes:
        gen_sizes.sort()
        genomes_per_gen = gen_sizes[len(gen_sizes) // 2]  # median

    # --- Window-based rate computation (genomes/hr) ---
    def _window_rate(pts: list, window_sec: float) -> Optional[float]:
        t_end = pts[-1][0]
        window = [p for p in pts if p[0] >= t_end - window_sec]
        if len(window) < 2:
            return None
        dt = window[-1][0] - window[0][0]
        dn = window[-1][1] - window[0][1]
        if dt < 60 or dn < 0:
            return None
        return dn / dt * 3600

    rate_30m = _window_rate(run, 30 * 60)
    rate_60m = _window_rate(run, 60 * 60)
    rate_90m = _window_rate(run, 90 * 60)
    rate_3h  = _window_rate(run, 3 * 3600)
    rate_all = _window_rate(run, (run[-1][0] - run[0][0]) + 1)

    # Best current rate estimate: prefer shorter windows (more recent)
    current_rate = rate_30m or rate_60m or rate_3h or rate_all
    if not current_rate or current_rate <= 0:
        return {}

    # Trend: compare short window (30m) to longer baseline (90m or 3h)
    baseline_rate = rate_90m or rate_3h or rate_all
    trend_pct = 0.0
    if baseline_rate and baseline_rate > 0:
        trend_pct = (current_rate - baseline_rate) / baseline_rate * 100

    # Effective rate for ETA: penalise if decelerating
    if trend_pct < -20:
        effective_rate = current_rate * 0.80  # significant slowdown
    elif trend_pct < -10:
        effective_rate = current_rate * 0.90
    else:
        effective_rate = current_rate

    # --- ETA for next generation ---
    current_gen = run[-1][2]
    current_n   = run[-1][1]
    next_gen_eta_sec: Optional[int] = None
    remaining_in_gen: Optional[int] = None

    if genomes_per_gen and genomes_per_gen > 0:
        gen_start_n = gen_first_seen.get(current_gen, run[0][1])
        genomes_into_gen = max(current_n - gen_start_n, 0)
        remaining_in_gen = max(genomes_per_gen - genomes_into_gen, 0)
        rate_per_sec = effective_rate / 3600
        if rate_per_sec > 0:
            if remaining_in_gen > 0:
                next_gen_eta_sec = round(remaining_in_gen / rate_per_sec)
            else:
                # Just crossed boundary; estimate next full gen
                next_gen_eta_sec = round(genomes_per_gen / rate_per_sec)

    # --- Run elapsed time ---
    run_start_unix = run[0][0]
    run_current_unix = run[-1][0]
    elapsed_sec = round(run_current_unix - run_start_unix)

    run_start_dt = datetime.fromtimestamp(run_start_unix, tz=timezone.utc)
    run_start_str = run_start_dt.strftime("%Y-%m-%d %H:%M UTC")

    return {
        "current_rate_gph":   round(current_rate, 1),
        "trend_pct":          round(trend_pct, 1),
        "genomes_per_gen":    genomes_per_gen,
        "remaining_in_gen":   remaining_in_gen,
        "next_gen_eta_sec":   next_gen_eta_sec,
        "elapsed_sec":        elapsed_sec,
        "run_start_str":      run_start_str,
        "decelerating":       trend_pct < -10,
    }


def _para_eta(eta: dict) -> Optional[str]:
    """Produce the throughput / ETA paragraph."""
    if not eta:
        return None

    rate  = eta.get("current_rate_gph")
    trend = eta.get("trend_pct", 0.0)
    gpg   = eta.get("genomes_per_gen")
    rem   = eta.get("remaining_in_gen")
    eta_s = eta.get("next_gen_eta_sec")
    decel = eta.get("decelerating", False)

    if not rate:
        return None

    # Rate description
    rate_str = f"{rate:.0f} genomes/hr"

    # Trend description
    if abs(trend) < 5:
        trend_str = "stable rate"
    elif trend <= -20:
        trend_str = f"decelerating sharply ({trend:+.0f}%/hr vs 90-min baseline -- ETA adjusted)"
    elif trend < -5:
        trend_str = f"decelerating ({trend:+.0f}%/hr)"
    elif trend >= 20:
        trend_str = f"accelerating ({trend:+.0f}%/hr)"
    elif trend > 5:
        trend_str = f"slightly accelerating ({trend:+.0f}%/hr)"
    else:
        trend_str = f"roughly stable ({trend:+.0f}%/hr)"

    parts = [f"Throughput: {rate_str}, {trend_str}."]

    if eta_s is not None:
        dur = _fmt_duration(eta_s)
        decel_note = " (deceleration factored in)" if decel else ""
        if rem is not None and gpg and gpg > 0:
            pct_done = round((gpg - rem) / gpg * 100)
            parts.append(
                f"Next generation boundary in ~{dur}{decel_note} "
                f"-- {pct_done}% through current gen, {rem} of {gpg} genomes remaining."
            )
        else:
            parts.append(f"Next generation boundary in ~{dur}{decel_note}.")

    return "  ".join(parts)


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def _print_cycle_header(digest: dict, idx: int, eta: Optional[dict] = None) -> None:
    ts   = digest.get("timestamp", "?")
    best = float(digest.get("best_fitness") or 0)
    gen  = digest.get("max_generation") or "?"
    total   = digest.get("total_genomes") or "?"
    alerts  = len(digest.get("alerts") or [])
    signals = len(digest.get("signals") or [])

    model_label = _active_model_label(digest)

    print(f"\n{'='*72}")
    print(f"[Cycle {idx}]  {ts}")
    print(f"Model: {model_label}")

    if eta:
        start_str   = eta.get("run_start_str", "?")
        elapsed_sec = eta.get("elapsed_sec")
        elapsed_str = _fmt_duration(elapsed_sec) if elapsed_sec else "?"
        print(f"Run started: {start_str}  |  Elapsed: {elapsed_str}")

    print(f"Gen {gen}  |  {total} genomes  |  best={best:.4f}  |  alerts={alerts}  signals={signals}")
    print("=" * 72)


def narrative_for(digest: dict, prev: Optional[dict] = None,
                  eta: Optional[dict] = None,
                  rph_eval: Optional[dict] = None) -> str:
    tags = _classify(digest)
    paragraphs = []

    paragraphs.append(_para_headline(digest, tags))

    model_sep_para = _para_model_separation(digest)
    if model_sep_para:
        paragraphs.append(model_sep_para)

    trap_para = _para_trap_detail(digest, tags)
    if trap_para:
        paragraphs.append(trap_para)

    coupling_para = _para_trap_coupling(digest, tags)
    if coupling_para:
        paragraphs.append(coupling_para)

    balance_para = _para_trap_balance(digest, tags)
    if balance_para:
        paragraphs.append(balance_para)

    falsif_para = _para_falsification(digest, tags)
    if falsif_para:
        paragraphs.append(falsif_para)

    fitness_para = _para_fitness(digest, tags)
    if fitness_para:
        paragraphs.append(fitness_para)

    align_para = _para_alignment(digest, tags)
    if align_para:
        paragraphs.append(align_para)

    zones_para = _para_zones(digest, tags)
    if zones_para:
        paragraphs.append(zones_para)

    scout_para = _para_scout_layers(digest, tags)
    if scout_para:
        paragraphs.append(scout_para)

    logit_para = _para_logit_selectivity(digest, tags)
    if logit_para:
        paragraphs.append(logit_para)

    norm_para = _para_norm_ratio(digest, tags)
    if norm_para:
        paragraphs.append(norm_para)

    cmaes_para = _para_cmaes(digest, tags)
    if cmaes_para:
        paragraphs.append(cmaes_para)

    rolling_para = _para_rolling_corr(digest, tags)
    if rolling_para:
        paragraphs.append(rolling_para)

    # RPH proxy evaluation (from eval_rph_survivors.py)
    rph_para = _para_rph_eval(rph_eval, tags)
    if rph_para:
        paragraphs.append(rph_para)

    rph_gradient = _para_rph_scale_gradient(rph_eval)
    if rph_gradient:
        paragraphs.append(rph_gradient)

    rph_xref = _para_rph_cross_ref(rph_eval, digest, tags)
    if rph_xref:
        paragraphs.append(rph_xref)

    rph_explain = _para_rph_explain(rph_eval)
    if rph_explain:
        paragraphs.append(rph_explain)

    eta_para = _para_eta(eta or {})
    if eta_para:
        paragraphs.append(eta_para)

    if prev:
        paragraphs.append(_compare_narrative(prev, digest))

    paragraphs.append(_para_bottom_line(digest, tags))

    return "\n\n".join(p for p in paragraphs if p)


def print_single(digest: dict, prev: Optional[dict] = None,
                 idx: int = 1, eta: Optional[dict] = None,
                 rph_eval: Optional[dict] = None) -> None:
    _print_cycle_header(digest, idx, eta=eta)
    print()
    print(narrative_for(digest, prev=prev, eta=eta, rph_eval=rph_eval))
    alerts  = digest.get("alerts") or []
    signals = digest.get("signals") or []
    if alerts:
        print(f"\nAlerts: {'; '.join(alerts)}")
    if signals:
        print(f"Signals: {'; '.join(signals)}")


def print_overview(digests: list[dict], cycles: int,
                   rph_eval: Optional[dict] = None) -> None:
    if not digests:
        print("No watchman digests found.")
        return

    eta = _compute_eta(digests)
    print(f"Found {len(digests)} total digests. Showing most recent {cycles}.\n")
    recent = digests[-cycles:]

    for i, d in enumerate(recent[::-1], start=1):
        prev = recent[-(i + 1)] if i < len(recent) else None
        full_narrative = (i == 1)  # full narrative only for most recent
        if full_narrative:
            print_single(d, prev=prev, idx=i, eta=eta, rph_eval=rph_eval)
        else:
            # Abbreviated: header + headline + bottom line only
            _print_cycle_header(d, i)
            tags = _classify(d)
            print()
            print(_para_headline(d, tags))
            print()
            print(_para_bottom_line(d, tags))
            alerts = d.get("alerts") or []
            if alerts:
                print(f"\nAlerts: {'; '.join(alerts[:2])}")

    # Show cross-run comparison table if multiple runs detected
    runs = _split_runs(digests)
    if len(runs) >= 2:
        _print_run_comparison_table(digests)

    print(f"\n{'='*72}")
    print("Run with --latest for just the most recent digest.")
    print("Run with --table for per-generation trajectory.")
    print("Open watchman/digest_latest.md for the full Markdown report.")


# ---------------------------------------------------------------------------
# Multi-run analysis
# ---------------------------------------------------------------------------

def _split_runs(digests: list[dict]) -> list[list[dict]]:
    """Split digest history into runs. A new run starts when max_generation goes backward."""
    if not digests:
        return []
    runs: list[list[dict]] = []
    current: list[dict] = [digests[0]]
    for i in range(1, len(digests)):
        prev_gen = int(digests[i - 1].get("max_generation") or 0)
        curr_gen = int(digests[i].get("max_generation") or 0)
        if curr_gen < prev_gen:
            runs.append(current)
            current = [digests[i]]
        else:
            current.append(digests[i])
    if current:
        runs.append(current)
    return runs


def _print_run_comparison_table(all_digests: list[dict]) -> None:
    """Print a cross-run summary table when multiple model runs are detected."""
    runs = _split_runs(all_digests)
    if len(runs) < 2:
        return

    print(f"\n{'='*72}")
    print("CROSS-RUN COMPARISON")
    print(f"{'='*72}")
    hdr = f"{'Model':<26} {'N':>5} {'Gen':>4} {'Best':>7} {'Bypass':>7} {'Native':>7} {'cos_r':>7} {'mean|r|':>8} {'Prod%':>6}  Verdict"
    print(hdr)
    print("-" * 72)

    for run_digests in runs:
        last = run_digests[-1]
        model = _active_model_label(last)
        n = int(last.get("total_genomes") or 0)
        gen = int(last.get("max_generation") or 0)
        best = float(last.get("best_fitness") or 0)
        compat = last.get("compatibility") or {}
        bypass = int(compat.get("artificial_bypass_candidates") or 0)
        native = int(compat.get("native_circuit_candidates") or 0)
        cos_r = float(compat.get("cosine_fitness_corr") or 0)
        tc = float((last.get("trap_coupling") or {}).get("mean_abs_r") or 0)
        zones = last.get("zones") or {}
        prod_pct = float((zones.get("productive") or {}).get("pct") or 0)

        tags = _classify(last)
        if "NULL_COMPLETE" in tags or "NULL_CANDIDATE" in tags:
            verdict = "NULL"
        elif "NATIVE_LEADING" in tags:
            verdict = "NATIVE"
        elif "BYPASS_DOMINANT" in tags or "BYPASS_FORMING" in tags:
            verdict = "BYPASS"
        else:
            verdict = "..."

        print(
            f"{model:<26} {n:>5} {gen:>4} {best:>7.4f} {bypass:>7} {native:>7} "
            f"{cos_r:>7.3f} {tc:>8.3f} {prod_pct:>5.0f}%  {verdict}"
        )

    print()


def _print_trajectory_table(all_digests: list[dict]) -> None:
    """Print a per-generation trajectory table for the current (most recent) run."""
    runs = _split_runs(all_digests)
    if not runs:
        return
    run = runs[-1]  # Current run

    # Build per-gen table: last snapshot per generation number
    per_gen: dict[int, tuple] = {}
    for d in run:
        gen  = int(d.get("max_generation") or 0)
        n    = int(d.get("total_genomes") or 0)
        best = float(d.get("best_fitness") or 0)
        compat  = d.get("compatibility") or {}
        bypass  = int(compat.get("artificial_bypass_candidates") or 0)
        native  = int(compat.get("native_circuit_candidates") or 0)
        cos_r   = float(compat.get("cosine_fitness_corr") or 0)
        tc      = float((d.get("trap_coupling") or {}).get("mean_abs_r") or 0)
        zones   = d.get("zones") or {}
        prod_pct = float((zones.get("productive") or {}).get("pct") or 0)

        # Active model sigma + plateau from cma_state
        state = d.get("cma_state") or {}
        sigma: Optional[float] = None
        plateau: Optional[int] = None
        best_gc = -1
        for key, info in state.items():
            if isinstance(info, dict):
                gc = int(info.get("gen_count") or 0)
                if gc > best_gc:
                    best_gc = gc
                    sigma   = info.get("sigma")
                    plateau = info.get("plateau_count") or 0

        per_gen[gen] = (n, best, bypass, native, cos_r, tc, sigma, plateau, prod_pct)

    model = _active_model_label(run[-1])
    print(f"\n{'='*72}")
    print(f"GENERATION TRAJECTORY  --  {model}")
    print(f"{'='*72}")
    print(f"{'Gen':>4} {'N':>5} {'Best':>7} {'Bypass':>7} {'Native':>7} {'cos_r':>7} {'mean|r|':>8} {'sigma':>10} {'Plat':>5} {'Prod%':>6}")
    print("-" * 72)

    for gen in sorted(per_gen):
        n, best, bypass, native, cos_r, tc, sigma, plateau, prod_pct = per_gen[gen]
        sig_str  = f"{sigma:.5f}" if sigma is not None else "         -"
        plat_str = str(plateau)   if plateau is not None else "-"
        print(
            f"{gen:>4} {n:>5} {best:>7.4f} {bypass:>7} {native:>7} {cos_r:>7.3f} "
            f"{tc:>8.3f} {sig_str:>10} {plat_str:>5} {prod_pct:>5.0f}%"
        )

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Review Night Watchman scientific digests with narrative summaries"
    )
    parser.add_argument(
        "--results-dir", default="results/ignis",
        help="Ignis results dir containing watchman output"
    )
    parser.add_argument(
        "--cycles", type=int, default=5,
        help="How many most recent watchman cycles to show (default: 5)"
    )
    parser.add_argument(
        "--latest", action="store_true",
        help="Show only the latest digest with full narrative"
    )
    parser.add_argument(
        "--table", action="store_true",
        help="Print per-generation trajectory table for the current run"
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    watchman_dir = results_dir / "watchman"
    history_path = watchman_dir / "digest_history.jsonl"

    try:
        digests = load_digests(history_path)
    except FileNotFoundError as e:
        print(str(e))
        return

    if not digests:
        print("Digest history is empty.")
        return

    eta = _compute_eta(digests)

    # Load RPH eval results (from eval_rph_survivors.py) if available
    rph_eval = _latest_rph_eval(results_dir)
    if rph_eval:
        ts = rph_eval.get("timestamp")
        ts_str = ts.strftime("%Y-%m-%d %H:%M") if ts else "unknown"
        n_scales = len(rph_eval.get("scales") or {})
        print(f"RPH eval found: {n_scales} scale(s) evaluated at {ts_str}\n")

    if args.table:
        _print_trajectory_table(digests)
        _print_run_comparison_table(digests)
    elif args.latest:
        prev = digests[-2] if len(digests) >= 2 else None
        print_single(digests[-1], prev=prev, idx=1, eta=eta, rph_eval=rph_eval)
    else:
        print_overview(digests, args.cycles, rph_eval=rph_eval)


if __name__ == "__main__":
    main()
