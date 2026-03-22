#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║                      THE NIGHT WATCHMAN                             ║
║                                                                     ║
║   "Sleeps while the GPU works. Wakes to read the shadows."          ║
║                                                                     ║
║   A background analysis daemon for Ignis marathon runs.           ║
║   Periodically snapshots live output files, runs multi-pass         ║
║   analysis, and builds a cumulative scientific digest.              ║
║                                                                     ║
║   Does NOT touch live files directly — copies first, reads copies.  ║
╚══════════════════════════════════════════════════════════════════════╝

Design consensus: Claude (architecture), Gemini (trap correlation, vector drift,
N-1 rule), ChatGPT (cosine-fitness correlation, logit selectivity, regime
classification as primary signals). 2026-03-18.

Usage:
    python night_watchman.py                          # defaults (5-min interval)
    python night_watchman.py --interval 600           # wake every 10 min
    python night_watchman.py --results-dir /path/to/results/ignis
    python night_watchman.py --once                   # single pass, no loop

Outputs (written to {results_dir}/watchman/):
    digest_latest.md        — full markdown report, overwritten each cycle
    digest_history.jsonl    — append-only record of every wake cycle
    alerts.log              — anomalies only, persistent

Seven analysis passes per cycle:
    1. Discovery log     — fitness trajectory, zones, trap performance, alignment gaps
    2. Trap correlation  — Pearson r between trap score vectors (shared mechanism signal)
    3. Ghost trap        — four-quadrant cos_with_residual × fitness compatibility
    4. Logit selectivity — Δ(correct tokens) - Δ(wrong tokens) per genome
    5. Falsification     — pass rate, directional margin, sign-flip asymmetry
    6. Vector drift      — cosine(inception_seed, gen_N_best) over time (N-1 rule)
    7. CMA-ES state      — sigma, mean_norm, plateau count from state.json
"""

import argparse
import hashlib
import json
import math
import shutil
import sys
import time
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path

# Optional — degrade gracefully if not installed
try:
    import torch
    _TORCH_OK = True
except ImportError:
    _TORCH_OK = False

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─── Configuration ────────────────────────────────────────────────────────────

DEFAULT_INTERVAL    = 300           # seconds between wake cycles
DEFAULT_RESULTS_DIR = "results/ignis"
BASELINE_THRESHOLD  = 0.30          # must match ignis_orchestrator.py
COS_HIGH_THRESHOLD  = 0.30          # four-quadrant compatibility split
WATCHMAN_STOP_FILE  = "WATCHMAN_STOP"  # relative to results_dir; written by stop_ignis.py


# ─── Snapshot Logic ───────────────────────────────────────────────────────────

def _md5(path: Path) -> str:
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def snapshot_files(results_dir: Path, watchman_dir: Path) -> dict:
    """
    Copy live files to watchman/snapshots/ using MD5 comparison to skip
    unchanged files. Never opens live files for reading — copy first, analyze copy.
    """
    snap_dir = watchman_dir / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    hash_file = watchman_dir / ".file_hashes.json"

    old_hashes: dict = {}
    if hash_file.exists():
        try:
            old_hashes = json.loads(hash_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    targets: dict = {}

    # Root-level files
    for f in results_dir.glob("*.jsonl"):
        targets[str(f)] = snap_dir / f.name
    for f in results_dir.glob("gen_*_outputs.json"):
        targets[str(f)] = snap_dir / f.name
    for f in results_dir.glob("*.csv"):
        targets[str(f)] = snap_dir / f.name
    state = results_dir / "state.json"
    if state.exists():
        targets[str(state)] = snap_dir / "state.json"
    for f in results_dir.glob("gen_*_best.pt"):
        targets[str(f)] = snap_dir / f.name

    # Most-recently-modified log
    log_dir = results_dir / "logs"
    if log_dir.exists():
        logs = sorted(log_dir.glob("ignis*.log"), key=lambda p: p.stat().st_mtime)
        if logs:
            targets[str(logs[-1])] = snap_dir / "ignis.log"

    # Model subdirectories
    for subdir in results_dir.iterdir():
        if not subdir.is_dir() or subdir.name in ("logs", "watchman", "snapshots", "archives"):
            continue
        prefix = subdir.name
        for f in subdir.glob("*.jsonl"):
            targets[str(f)] = snap_dir / f"{prefix}_{f.name}"
        for f in subdir.glob("gen_*_outputs.json"):
            targets[str(f)] = snap_dir / f"{prefix}_{f.name}"
        for f in subdir.glob("*.csv"):
            targets[str(f)] = snap_dir / f"{prefix}_{f.name}"
        for f in subdir.glob("gen_*_best.pt"):
            targets[str(f)] = snap_dir / f"{prefix}_{f.name}"
        seed = subdir / "gen_inception_seed.pt"
        if seed.exists():
            targets[str(seed)] = snap_dir / f"{prefix}_gen_inception_seed.pt"
        sub_state = subdir / "state.json"
        if sub_state.exists():
            targets[str(sub_state)] = snap_dir / f"{prefix}_state.json"

    new_hashes: dict = {}
    copied: dict = {}
    for src_str, dst in targets.items():
        src = Path(src_str)
        if not src.exists():
            continue
        try:
            h = _md5(src)
            new_hashes[src_str] = h
            if old_hashes.get(src_str) == h and dst.exists():
                copied[dst.name] = "unchanged"
                continue
            shutil.copy2(src, dst)
            copied[dst.name] = "updated"
        except (PermissionError, OSError) as e:
            copied[dst.name] = f"FAILED: {e}"

    try:
        hash_file.write_text(json.dumps(new_hashes, indent=2), encoding="utf-8")
    except Exception:
        pass

    return copied


# ─── JSONL Analysis ───────────────────────────────────────────────────────────

def analyze_discovery_log(snap_dir: Path) -> dict:
    """Parse all *discovery_log.jsonl snapshots for scientific signals."""
    results = {
        "total_genomes":     0,
        "generations_seen":  set(),
        "fitness_trajectory": {},       # gen -> best fitness
        "fitness_all":       [],
        "zone_counts":       defaultdict(int),
        "layer_fitness":     defaultdict(list),
        "explore_fitness":   {"MAIN": [], "SCOUT": []},
        "scout_by_layer":    defaultdict(list),
        "trap_scores":       defaultdict(list),
        "trap_score_matrix": [],        # per-genome {trap: score} for correlation
        "falsification_results": [],
        "logit_by_trap":     defaultdict(list),
        "alignment_gaps":    [],        # logit_score - marker_fitness
        "ghost_trap":        [],        # {cos, pre_norm, post_norm, fitness, gen, layer, model}
        "logit_selectivity": [],        # {selectivity, fitness, gen}
        "min_trap_scores":   [],        # min(trap_scores) per genome — passive trap-balance signal
        "norm_ratios":       [],        # post_norm / pre_norm per genome — injection aggressiveness
        "best_genome":       None,
        "best_fitness":      -1.0,
        # Per-model tracking — ghost trap entries keyed by model stem.
        # cos_with_residual distributions differ structurally across model scales,
        # so cross-model mixing produces spurious cos-fitness correlations.
        "per_model_ghost_trap": defaultdict(list),
        "model_mtimes":          {},    # model_stem -> file mtime (to identify active model)
    }

    for jf in snap_dir.glob("*discovery_log.jsonl"):
        # Extract model key from filename: "qwen_qwen2_5-1_5b-instruct_discovery_log.jsonl"
        # → "qwen_qwen2_5-1_5b-instruct"
        model_key = jf.name.replace("_discovery_log.jsonl", "")
        try:
            results["model_mtimes"][model_key] = jf.stat().st_mtime
        except OSError:
            results["model_mtimes"][model_key] = 0
        try:
            for line in jf.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue

                results["total_genomes"] += 1
                gen     = rec.get("gen", -1)
                fitness = rec.get("fitness", 0.0)
                layer   = rec.get("layer")
                explore = rec.get("explore", "UNKNOWN")
                results["min_trap_scores"].append(rec.get("min_trap_score"))

                results["generations_seen"].add(gen)
                results["fitness_all"].append(fitness)

                if gen not in results["fitness_trajectory"] or fitness > results["fitness_trajectory"][gen]:
                    results["fitness_trajectory"][gen] = fitness
                if fitness > results["best_fitness"]:
                    results["best_fitness"] = fitness
                    results["best_genome"]  = rec

                results["zone_counts"][rec.get("zone", "UNKNOWN")] += 1

                if layer is not None:
                    results["layer_fitness"][layer].append(fitness)
                if explore in results["explore_fitness"]:
                    results["explore_fitness"][explore].append(fitness)
                if explore == "SCOUT" and layer is not None:
                    results["scout_by_layer"][layer].append(fitness)

                # Trap scores
                per_genome_scores = {}
                for trap_name, score_info in (rec.get("trap_scores") or {}).items():
                    if isinstance(score_info, dict):
                        results["trap_scores"][trap_name].append(score_info)
                        per_genome_scores[trap_name] = score_info.get("score", 0)
                    else:
                        results["trap_scores"][trap_name].append({"score": score_info})
                        per_genome_scores[trap_name] = score_info
                if per_genome_scores:
                    results["trap_score_matrix"].append(per_genome_scores)

                # Rolling correlation check for key trap pair is computed later

                # Logit by trap
                for trap_name, lv in (rec.get("logit_by_trap") or {}).items():
                    if isinstance(lv, (int, float)):
                        results["logit_by_trap"][trap_name].append(lv)

                # Alignment gap
                marker_f = rec.get("marker_fitness")
                logit_f  = rec.get("logit_score")
                if marker_f is not None and logit_f is not None:
                    results["alignment_gaps"].append(logit_f - marker_f)

                # Ghost trap — injection_snapshot contains cos_with_residual
                snap = rec.get("injection_snapshot") or {}
                cos_r = snap.get("cos_with_residual")
                if cos_r is not None:
                    entry = {
                        "cos":      cos_r,
                        "pre_norm":  snap.get("pre_norm"),
                        "post_norm": snap.get("post_norm"),
                        "fitness":  fitness,
                        "gen":      gen,
                        "layer":    layer,
                        "model":    model_key,
                    }
                    results["ghost_trap"].append(entry)
                    results["per_model_ghost_trap"][model_key].append(entry)

                # Norm ratio — injection aggressiveness
                pre = snap.get("pre_norm")
                post = snap.get("post_norm")
                if pre is not None and post is not None and pre > 1e-10:
                    results["norm_ratios"].append(post / pre)

                # Logit selectivity — Δ(correct tokens) - Δ(wrong tokens)
                # From ChatGPT: selectivity = max(delta_correct) - max(delta_wrong)
                delta = (rec.get("logit_shift_signature") or {}).get("delta") or {}
                if delta:
                    correct_tokens = {"right", "true", "same"}
                    wrong_tokens   = {"left", "false", "heavier"}
                    cd = [delta[k] for k in correct_tokens if k in delta]
                    wd = [delta[k] for k in wrong_tokens  if k in delta]
                    if cd and wd:
                        results["logit_selectivity"].append({
                            "selectivity": max(cd) - max(wd),
                            "fitness": fitness,
                            "gen": gen,
                        })

                # Falsification
                falsif = rec.get("falsification")
                if falsif and isinstance(falsif, dict):
                    f2 = dict(falsif)
                    f2["fitness"] = fitness
                    f2["gen"]     = gen
                    f2["layer"]   = layer
                    results["falsification_results"].append(f2)

        except Exception as e:
            results.setdefault("parse_errors", []).append(str(e))

    results["generations_seen"] = sorted(results["generations_seen"])
    results["rolling_corr"] = compute_rolling_trap_correlation(
        results["trap_score_matrix"],
        "Decimal Magnitude", "Density Illusion",
        [50, 100, 200, 300]
    )
    # Determine the active model: the one whose snapshot file was most recently
    # modified. This prevents cross-model artifact in cos_fit_r when multiple
    # model directories coexist (e.g., 3B finished but still present alongside 1.5B).
    if results["model_mtimes"]:
        results["active_model"] = max(results["model_mtimes"], key=results["model_mtimes"].get)
    else:
        results["active_model"] = None
    return results


def compute_rolling_trap_correlation(trap_score_matrix: list[dict], trap_a: str, trap_b: str, milestones: list[int]) -> dict:
    """Compute Pearson r(trap_a, trap_b) at milestone genome counts."""
    out = {}
    if not trap_score_matrix:
        return out
    for n in milestones:
        if len(trap_score_matrix) < n:
            continue
        xs, ys = [], []
        for row in trap_score_matrix[:n]:
            if trap_a in row and trap_b in row:
                xs.append(row[trap_a])
                ys.append(row[trap_b])
        if len(xs) >= 5:
            out[f"r_{n}"] = _pearson_r(xs, ys)
    return out


# ─── State / Scout Parsers ────────────────────────────────────────────────────

def analyze_state(snap_dir: Path) -> dict:
    """
    State files are written by torch.save() (PyTorch binary), not JSON.
    Requires torch; degrades gracefully if unavailable.
    """
    states = {}
    for sf in snap_dir.glob("*state.json"):
        if not _TORCH_OK:
            states[sf.stem] = {"error": "torch not available"}
            continue
        try:
            data = torch.load(sf, map_location="cpu", weights_only=False)
            mean_norm = None
            if "mean_vector" in data:
                mean_norm = round(float(data["mean_vector"].norm().item()), 4)
            states[sf.stem] = {
                "gen_count":     data.get("gen_count"),
                "sigma":         round(float(data["sigma"]), 6) if "sigma" in data else None,
                "best_fitness":  data.get("last_best_fitness"),
                "plateau_count": data.get("plateau_count"),
                "mean_norm":     mean_norm,
            }
        except Exception as e:
            states[sf.stem] = {"error": f"parse failed: {e}"}
    return states


def analyze_scout_map(snap_dir: Path) -> dict:
    layers = {}
    for cf in snap_dir.glob("*scout_layer_map.csv"):
        try:
            lines = cf.read_text(encoding="utf-8").splitlines()
            for line in lines[1:]:
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    layer = parts[0].strip()
                    layers[layer] = {
                        "best_fitness": float(parts[1]) if parts[1] else 0,
                        "evals":        int(parts[2])   if parts[2] else 0,
                    }
        except Exception:
            pass
    return layers


# ─── Vector Drift (Gemini) ────────────────────────────────────────────────────

def _extract_vector(obj) -> "torch.Tensor | None":
    """Extract raw tensor from saved Genome object or direct tensor."""
    if not _TORCH_OK:
        return None
    if isinstance(obj, torch.Tensor):
        return obj
    if hasattr(obj, "vector"):
        return obj.vector
    if isinstance(obj, dict) and "vector" in obj:
        return obj["vector"]
    return None


def analyze_vector_drift(snap_dir: Path) -> dict:
    """
    Compare each model's inception seed to its gen_N-1_best.pt (N-1 rule:
    skip the most recent file to avoid racing a live write).

    Returns cosine similarity — tells you whether CMA-ES is refining the
    inception seed direction or has drifted to a different area of the model.
    """
    if not _TORCH_OK:
        return {"_note": "torch not available — install to enable drift analysis"}

    results = {}
    for seed_file in snap_dir.glob("*_gen_inception_seed.pt"):
        prefix = seed_file.name.replace("_gen_inception_seed.pt", "")
        best_files = sorted(snap_dir.glob(f"{prefix}_gen_*_best.pt"))
        if len(best_files) < 2:
            continue  # N-1 rule: need at least 2 to safely load the second-to-last
        target = best_files[-2]
        try:
            sv = _extract_vector(torch.load(seed_file, map_location="cpu", weights_only=False))
            bv = _extract_vector(torch.load(target,    map_location="cpu", weights_only=False))
            if sv is None or bv is None:
                results[prefix] = {"error": "could not extract vector tensor"}
                continue
            sv = sv.float().flatten()
            bv = bv.float().flatten()
            cos = float((sv @ bv) / (sv.norm() * bv.norm() + 1e-10))
            results[prefix] = {
                "cosine_to_inception": round(cos, 4),
                "inception_norm":      round(float(sv.norm()), 4),
                "best_norm":           round(float(bv.norm()), 4),
                "best_file":           target.name,
            }
        except Exception as e:
            results[prefix] = {"error": str(e)}

    return results


# ─── Trap Correlation (Gemini) ────────────────────────────────────────────────

def _pearson_r(xs: list, ys: list) -> float | None:
    n = len(xs)
    if n < 5:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    num  = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dxs  = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dys  = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dxs < 1e-10 or dys < 1e-10:
        return None
    return round(num / (dxs * dys), 4)


def analyze_trap_correlations(trap_score_matrix: list) -> dict:
    """
    Pearson r between each pair of trap score vectors across all genomes.
    High positive r: traps co-activate -> possible shared circuit.
    Negative r: traps compete -> different or opposing heuristics.
    """
    if not trap_score_matrix:
        return {}
    trap_lists: dict = defaultdict(list)
    for row in trap_score_matrix:
        for trap, score in row.items():
            trap_lists[trap].append(score)

    traps = sorted(trap_lists.keys())
    corr  = {}
    for i, ta in enumerate(traps):
        for tb in traps[i + 1:]:
            xs, ys = trap_lists[ta], trap_lists[tb]
            n = min(len(xs), len(ys))
            r = _pearson_r(xs[:n], ys[:n])
            if r is not None:
                corr[f"{ta} x {tb}"] = r
    return corr


# ─── Digest Computation ───────────────────────────────────────────────────────

def compute_digest(disc: dict, state: dict, scouts: dict, drift: dict) -> dict:
    digest = {
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "total_genomes": disc["total_genomes"],
        "generations":   len(disc["generations_seen"]),
        "max_generation": max(disc["generations_seen"]) if disc["generations_seen"] else -1,
        "best_fitness":  disc["best_fitness"],
        "alerts":        [],
        "signals":       [],
    }

    # ── Fitness trajectory ──────────────────────────────────────────────────
    traj = disc["fitness_trajectory"]
    if len(traj) >= 2:
        gens   = sorted(traj.keys())
        early  = traj[gens[0]]
        latest = traj[gens[-1]]
        delta  = latest - early
        digest["fitness_climb"] = {
            "first_gen": gens[0],  "first_fit": round(early, 4),
            "last_gen":  gens[-1], "last_fit":  round(latest, 4),
            "delta":     round(delta, 4),
        }
        if delta < -0.05 and len(gens) > 5:
            digest["alerts"].append("FITNESS DECLINING — CMA-ES may be diverging")
        if delta > 0.1:
            digest["signals"].append(
                f"Strong fitness climb: {early:.4f} -> {latest:.4f} (+{delta:.4f})"
            )

    # ── Zone distribution ───────────────────────────────────────────────────
    total = sum(disc["zone_counts"].values())
    if total > 0:
        productive_pct = disc["zone_counts"].get("productive", 0) / total * 100
        digest["zones"] = {
            k: {"count": v, "pct": round(v / total * 100, 1)}
            for k, v in disc["zone_counts"].items()
        }
        if productive_pct < 10 and len(disc["generations_seen"]) > 5:
            digest["alerts"].append(
                f"Low productive rate ({productive_pct:.1f}%) after "
                f"{len(disc['generations_seen'])} gens"
            )
        if productive_pct > 30:
            digest["signals"].append(f"Healthy productive rate: {productive_pct:.1f}%")

    # ── Trap performance ────────────────────────────────────────────────────
    trap_summary = {}
    for trap_name, scores in disc["trap_scores"].items():
        tier_counts  = defaultdict(int)
        score_vals   = []
        for s in scores:
            if isinstance(s, dict):
                tier_counts[s.get("tier", "UNKNOWN")] += 1
                score_vals.append(s.get("score", 0))
            else:
                score_vals.append(s)
        n = len(scores)
        trap_summary[trap_name] = {
            "n":          n,
            "mean_score": round(sum(score_vals) / n, 4) if score_vals else 0,
            "floor_pct":  round(tier_counts.get("FLOOR",  0) / n * 100, 1) if n else 0,
            "credit_pct": round(tier_counts.get("CREDIT", 0) / n * 100, 1) if n else 0,
        }
    digest["traps"] = trap_summary
    digest["rolling_corr"] = disc.get("rolling_corr", {})

    # Single-trap dominance alert
    credit_pcts = {k: v["credit_pct"] for k, v in trap_summary.items()}
    if credit_pcts:
        max_trap = max(credit_pcts, key=credit_pcts.get)
        max_pct  = credit_pcts[max_trap]
        others   = [v for k, v in credit_pcts.items() if k != max_trap]
        if max_pct > 40 and others and all(o < 5 for o in others):
            digest["alerts"].append(
                f"TRAP SPECIALIZATION: {max_trap} dominates ({max_pct:.0f}% CREDIT), "
                f"others at {', '.join(f'{o:.0f}%' for o in others)}"
            )

    # ── Trap correlations (Gemini) ──────────────────────────────────────────
    corr = analyze_trap_correlations(disc["trap_score_matrix"])
    if corr:
        digest["trap_correlations"] = corr
        strong_pos = {k: v for k, v in corr.items() if v > 0.5}

    rolling_corr = disc.get("rolling_corr", {})
    if rolling_corr:
        digest["rolling_correlation"] = rolling_corr
        # a small stabilization signal
        latest_key = sorted(rolling_corr.keys(), key=lambda x: int(x.split("_")[1]))[-1]
        latest_r = rolling_corr.get(latest_key)
        if latest_r is not None and abs(latest_r) < 0.05:
            digest["signals"].append(
                f"Rolling correlation stable near zero at milestone {latest_key[2:]} genomes (r={latest_r:.3f})"
            )
        if strong_pos:
            pairs = ", ".join(
                f"{k}={v:.2f}"
                for k, v in sorted(strong_pos.items(), key=lambda x: -x[1])
            )
            digest["signals"].append(
                f"Trap co-activation (shared mechanism candidate): {pairs}"
            )
        strong_neg = {k: v for k, v in corr.items() if v < -0.3}
        if strong_neg:
            pairs = ", ".join(
                f"{k}={v:.2f}"
                for k, v in sorted(strong_neg.items(), key=lambda x: x[1])
            )
            digest["alerts"].append(
                f"Trap anti-correlation (competing heuristics): {pairs}"
            )

    # ── Falsification quality ───────────────────────────────────────────────
    falsif = disc["falsification_results"]
    if falsif:
        margins, flip_deltas, passed_flags = [], [], []
        for f in falsif:
            primary = f.get("fitness", 0)
            noise   = f.get("noise",   0)
            ortho   = f.get("ortho",   0)
            shuffle = f.get("shuffle", 0)
            flip    = f.get("flip",    0)
            margins.append(primary - max(noise, ortho, shuffle))
            flip_deltas.append(primary - flip)
            passed_flags.append(bool(f.get("passed", False)))

        n_passed       = sum(passed_flags)
        sign_flip_asym = sum(1 for d in flip_deltas if d > 0.05)
        digest["falsification"] = {
            "total":                  len(falsif),
            "passed":                 n_passed,
            "pass_rate_pct":          round(n_passed / len(falsif) * 100, 1),
            "mean_margin":            round(sum(margins) / len(margins), 4),
            "max_margin":             round(max(margins), 4),
            "sign_flip_asymmetric":   sign_flip_asym,
            "sign_flip_pct":          round(sign_flip_asym / len(falsif) * 100, 1),
        }
        if sign_flip_asym / len(falsif) > 0.5:
            digest["signals"].append(
                f"Strong directional signal: {sign_flip_asym}/{len(falsif)} genomes "
                f"show sign-flip asymmetry"
            )

    # ── Layer productivity ──────────────────────────────────────────────────
    layer_data = {}
    for layer, fits in disc["layer_fitness"].items():
        above_bl = sum(1 for f in fits if f >= BASELINE_THRESHOLD)
        layer_data[layer] = {
            "n":                   len(fits),
            "mean":                round(sum(fits) / len(fits), 4),
            "max":                 round(max(fits), 4),
            "above_baseline_pct":  round(above_bl / len(fits) * 100, 1),
        }
    digest["layers"] = layer_data

    # ── Scout analysis ──────────────────────────────────────────────────────
    scout_fits = disc["explore_fitness"].get("SCOUT", [])
    if scout_fits:
        above = sum(1 for f in scout_fits if f >= BASELINE_THRESHOLD)
        digest["scouts"] = {
            "total":           len(scout_fits),
            "mean":            round(sum(scout_fits) / len(scout_fits), 4),
            "max":             round(max(scout_fits), 4),
            "above_baseline":  above,
            "layers_explored": sorted({l for l in disc["scout_by_layer"]}),
        }
        if above == 0 and len(scout_fits) > 20:
            digest["alerts"].append(
                f"No scouts above baseline after {len(scout_fits)} evaluations"
            )

    # ── Alignment gap ───────────────────────────────────────────────────────
    gaps = disc["alignment_gaps"]
    if gaps:
        mean_gap           = sum(gaps) / len(gaps)
        expression_failures = sum(1 for g in gaps if g > 0.3)
        digest["alignment"] = {
            "mean_gap":                  round(mean_gap, 4),
            "expression_failures":       expression_failures,
            "expression_failure_pct":    round(expression_failures / len(gaps) * 100, 1),
        }
        if len(gaps) > 0 and expression_failures / len(gaps) > 0.3:
            digest["alerts"].append(
                f"High expression failure rate ({expression_failures}/{len(gaps)}) — "
                f"model knows answers but markers miss them. Add marker variants."
            )

    # ── Ghost trap: four-quadrant compatibility (ChatGPT primary signal) ────
    # Use only the ACTIVE model's ghost_trap data for the primary cos_fit_r.
    # cos_with_residual distributions differ structurally across model scales,
    # so mixing models (e.g., 3B has negative cos, 1.5B has positive cos)
    # produces a spurious cross-model correlation that looks like a native signal.
    active_model = disc.get("active_model")
    per_model_gt = disc.get("per_model_ghost_trap", {})
    if active_model and active_model in per_model_gt:
        cos_data_active = per_model_gt[active_model]
    else:
        cos_data_active = disc["ghost_trap"]   # fallback: use all (single model case)

    cos_data_all = disc["ghost_trap"]

    # Quadrant counts from active model only
    if cos_data_active:
        hf_hc = sum(1 for d in cos_data_active
                    if d["fitness"] >= BASELINE_THRESHOLD and d["cos"] >  COS_HIGH_THRESHOLD)
        hf_lc = sum(1 for d in cos_data_active
                    if d["fitness"] >= BASELINE_THRESHOLD and d["cos"] <= COS_HIGH_THRESHOLD)
        lf    = sum(1 for d in cos_data_active if d["fitness"] < BASELINE_THRESHOLD)

        cos_vals = [d["cos"]     for d in cos_data_active]
        fit_vals = [d["fitness"] for d in cos_data_active]
        cos_fit_r = _pearson_r(cos_vals, fit_vals)

        # Also compute per-model r values for transparency
        per_model_cos_r = {}
        for mk, entries in per_model_gt.items():
            if len(entries) >= 5:
                cv = [e["cos"] for e in entries]
                fv = [e["fitness"] for e in entries]
                per_model_cos_r[mk] = _pearson_r(cv, fv)

        digest["compatibility"] = {
            "total_measured":              len(cos_data_active),
            "native_circuit_candidates":   hf_hc,
            "artificial_bypass_candidates": hf_lc,
            "low_fitness":                 lf,
            "cosine_fitness_corr":         cos_fit_r,
            "active_model":                active_model,
            "per_model_cos_r":             per_model_cos_r,
        }
    elif cos_data_all:
        # Fallback: no per-model data, use combined (flag as potentially mixed)
        hf_hc = sum(1 for d in cos_data_all
                    if d["fitness"] >= BASELINE_THRESHOLD and d["cos"] >  COS_HIGH_THRESHOLD)
        hf_lc = sum(1 for d in cos_data_all
                    if d["fitness"] >= BASELINE_THRESHOLD and d["cos"] <= COS_HIGH_THRESHOLD)
        lf    = sum(1 for d in cos_data_all if d["fitness"] < BASELINE_THRESHOLD)
        cos_vals = [d["cos"]     for d in cos_data_all]
        fit_vals = [d["fitness"] for d in cos_data_all]
        cos_fit_r = _pearson_r(cos_vals, fit_vals)
        digest["compatibility"] = {
            "total_measured":              len(cos_data_all),
            "native_circuit_candidates":   hf_hc,
            "artificial_bypass_candidates": hf_lc,
            "low_fitness":                 lf,
            "cosine_fitness_corr":         cos_fit_r,
        }
    if "compatibility" in digest:
        if hf_hc > hf_lc and hf_hc > 3:
            digest["signals"].append(
                f"NATIVE CIRCUIT SIGNAL: {hf_hc} high-fitness genomes aligned with "
                f"natural residual (vs {hf_lc} bypasses)"
            )
        elif hf_lc > hf_hc and hf_lc > 3:
            digest["alerts"].append(
                f"Bypass dominance: {hf_lc} high-fitness genomes orthogonal to native "
                f"computation — finding artificial routes, not native circuits"
            )
        if cos_fit_r is not None and abs(cos_fit_r) > 0.3:
            direction = "positive" if cos_fit_r > 0 else "negative"
            digest["signals"].append(
                f"Cosine-fitness correlation r={cos_fit_r:.3f} ({direction}): "
                + ("native alignment is being rewarded" if cos_fit_r > 0
                   else "bypass routes are being rewarded — check if this is intentional")
            )

    # ── Trap coupling trajectory (mean |r| across all pairs this cycle) ─────
    corr_vals = list((digest.get("trap_correlations") or {}).values())
    if corr_vals:
        mean_abs_r = round(sum(abs(r) for r in corr_vals) / len(corr_vals), 4)
        digest["trap_coupling"] = {
            "mean_abs_r": mean_abs_r,
            "n_pairs": len(corr_vals),
        }
        if mean_abs_r > 0.3:
            digest["signals"].append(
                f"Trap coupling rising: mean |r|={mean_abs_r:.3f} — traps may be co-activating"
            )

    # ── Layer-wise native density (native candidates per layer) ─────────────
    # Use active model data to avoid cross-model layer contamination
    cos_data = cos_data_active if cos_data_active else disc.get("ghost_trap", [])
    if cos_data:
        layer_total: dict = Counter()
        layer_native: dict = Counter()
        for d in cos_data:
            l = d.get("layer")
            if l is not None:
                layer_total[l] += 1
                if d["fitness"] >= BASELINE_THRESHOLD and d["cos"] > COS_HIGH_THRESHOLD:
                    layer_native[l] += 1
        if layer_total:
            digest["layer_native_density"] = {
                str(l): {
                    "native": layer_native.get(l, 0),
                    "total": layer_total[l],
                    "density": round(layer_native.get(l, 0) / layer_total[l], 3),
                }
                for l in sorted(layer_total.keys())
            }

    # ── First native candidate detection ────────────────────────────────────
    compat = digest.get("compatibility", {})
    if compat.get("native_circuit_candidates", 0) > 0:
        best = disc.get("best_genome") or {}
        first_gen = best.get("gen", "?")
        digest["signals"].insert(0,
            f"*** FIRST NATIVE CIRCUIT CANDIDATE DETECTED "
            f"(gen={first_gen}, total={compat['native_circuit_candidates']}) ***"
        )
        digest["alerts"] = [a for a in digest["alerts"] if "Bypass dominance" not in a]

    # ── Logit selectivity (ChatGPT) ─────────────────────────────────────────
    sel_data = disc["logit_selectivity"]
    if sel_data:
        sel_vals = [d["selectivity"] for d in sel_data]
        mean_sel = sum(sel_vals) / len(sel_vals)
        high_sel = sum(1 for s in sel_vals if s > 0.5)
        digest["logit_selectivity"] = {
            "n":                    len(sel_vals),
            "mean":                 round(mean_sel, 4),
            "high_selectivity":     high_sel,
            "high_selectivity_pct": round(high_sel / len(sel_vals) * 100, 1),
        }
        if mean_sel > 0.5:
            digest["signals"].append(
                f"High mean logit selectivity ({mean_sel:.3f}) — steering vectors "
                f"consistently elevate correct-answer token probabilities"
            )

    # ── Trap balance (min_trap_score aggregation) ──────────────────────────
    min_traps = [s for s in disc["min_trap_scores"] if s is not None]
    if min_traps:
        digest["trap_balance"] = {
            "n":              len(min_traps),
            "mean_min_trap":  round(sum(min_traps) / len(min_traps), 4),
            "worst_min_trap": round(min(min_traps), 4),
            "pct_floor":      round(sum(1 for s in min_traps if s < 0.1) / len(min_traps) * 100, 1),
        }
        if digest["trap_balance"]["mean_min_trap"] < 0.05:
            digest["alerts"].append(
                f"Trap imbalance: mean min-trap score is "
                f"{digest['trap_balance']['mean_min_trap']:.4f} "
                f"— genomes are consistently failing at least one trap"
            )

    # ── Scout layer map (from analyze_scout_map CSV) ─────────────────────
    if scouts:
        digest["scout_layer_map"] = {}
        for layer_key, info in scouts.items():
            digest["scout_layer_map"][layer_key] = {
                "best_fitness": info["best_fitness"],
                "evals":        info["evals"],
            }
        total_evals = sum(info["evals"] for info in scouts.values())
        productive_layers = [
            l for l, info in scouts.items()
            if info["best_fitness"] >= BASELINE_THRESHOLD
        ]
        digest["scout_layer_map"]["_summary"] = {
            "total_layers":     len(scouts),
            "total_evals":      total_evals,
            "productive_layers": len(productive_layers),
        }

    # ── Norm ratio distribution (injection aggressiveness) ───────────────
    norm_ratios = disc.get("norm_ratios", [])
    if norm_ratios:
        sorted_nr = sorted(norm_ratios)
        n_nr = len(sorted_nr)
        mean_nr = sum(sorted_nr) / n_nr
        digest["norm_ratio"] = {
            "n":           n_nr,
            "mean":        round(mean_nr, 4),
            "max":         round(sorted_nr[-1], 4),
            "min":         round(sorted_nr[0], 4),
            "median":      round(sorted_nr[n_nr // 2], 4),
            "pct_above_1": round(sum(1 for r in sorted_nr if r > 1.0) / n_nr * 100, 1),
        }
        if mean_nr > 2.0:
            digest["alerts"].append(
                f"High norm_ratio (mean={mean_nr:.2f}): "
                f"injections are amplifying residual stream norms"
            )

    # ── Vector drift (Gemini, N-1 rule) ────────────────────────────────────
    if drift:
        non_trivial = {k: v for k, v in drift.items() if "_note" not in k}
        if non_trivial:
            digest["vector_drift"] = non_trivial
            for model, info in non_trivial.items():
                if isinstance(info, dict) and "cosine_to_inception" in info:
                    cos = info["cosine_to_inception"]
                    if abs(cos) < 0.1:
                        digest["alerts"].append(
                            f"Vector drift: {model} best is near-orthogonal to inception "
                            f"seed (cos={cos:.3f}) — CMA-ES explored far from init"
                        )
                    elif cos > 0.8:
                        digest["signals"].append(
                            f"Vector stable: {model} best aligned with inception seed "
                            f"(cos={cos:.3f}) — refining inception direction"
                        )

    digest["cma_state"] = state
    return digest


# ─── Markdown Rendering ───────────────────────────────────────────────────────

def render_markdown(digest: dict) -> str:
    ts = digest["timestamp"]
    lines = [
        "# The Night Watchman -- Digest",
        f"**Wake time:** {ts}",
        f"**Genomes analyzed:** {digest['total_genomes']}",
        f"**Generations:** {digest['generations']} (max: {digest['max_generation']})",
        f"**Best fitness:** {digest['best_fitness']:.4f}",
        "",
    ]

    if digest["alerts"]:
        lines.append("## Alerts")
        for a in digest["alerts"]:
            lines.append(f"- **{a}**")
        lines.append("")

    if digest["signals"]:
        lines.append("## Positive Signals")
        for s in digest["signals"]:
            lines.append(f"- {s}")
        lines.append("")

    climb = digest.get("fitness_climb")
    if climb:
        lines += [
            "## Fitness Trajectory",
            f"Gen {climb['first_gen']}: {climb['first_fit']:.4f} -> "
            f"Gen {climb['last_gen']}: {climb['last_fit']:.4f} "
            f"(delta: {climb['delta']:+.4f})",
            "",
        ]

    zones = digest.get("zones", {})
    if zones:
        lines.append("## Zone Distribution")
        for zone, info in sorted(zones.items()):
            bar = "#" * int(info["pct"] / 2)
            lines.append(f"- {zone}: {info['count']} ({info['pct']}%) {bar}")
        lines.append("")

    traps = digest.get("traps", {})
    if traps:
        lines += [
            "## Trap Performance",
            "| Trap | N | Mean | FLOOR% | CREDIT% |",
            "|------|---|------|--------|---------|",
        ]
        for trap, info in sorted(traps.items()):
            lines.append(
                f"| {trap} | {info['n']} | {info['mean_score']:.3f} | "
                f"{info['floor_pct']:.0f}% | {info['credit_pct']:.0f}% |"
            )
        lines.append("")

    corr = digest.get("trap_correlations")
    if corr:
        lines += ["## Trap Correlation Matrix", "| Pair | r | Signal |", "|------|---|--------|"]
        for pair, r in sorted(corr.items(), key=lambda x: -abs(x[1])):
            sig = "shared mechanism?" if r > 0.5 else ("competing heuristics?" if r < -0.3 else "")
            lines.append(f"| {pair} | {r:.3f} | {sig} |")
        lines.append("")

    falsif = digest.get("falsification")
    if falsif:
        lines += [
            "## Falsification Quality",
            f"- Tests run: {falsif['total']}  |  Passed: {falsif['passed']} "
            f"({falsif['pass_rate_pct']:.0f}%)",
            f"- Mean directional margin: {falsif['mean_margin']:.4f}  "
            f"|  Max: {falsif['max_margin']:.4f}",
            f"- Sign-flip asymmetric: {falsif['sign_flip_asymmetric']}/{falsif['total']} "
            f"({falsif['sign_flip_pct']:.0f}%)",
            "",
        ]

    layers = digest.get("layers", {})
    if layers:
        lines += [
            "## Layer Productivity",
            "| Layer | N | Mean | Max | Above BL% |",
            "|-------|---|------|-----|-----------|",
        ]
        for layer in sorted(layers.keys(), key=lambda x: int(x) if str(x).isdigit() else 0):
            info = layers[layer]
            lines.append(
                f"| {layer} | {info['n']} | {info['mean']:.4f} | "
                f"{info['max']:.4f} | {info['above_baseline_pct']:.0f}% |"
            )
        lines.append("")

    scout = digest.get("scouts")
    if scout:
        lines += [
            "## Scout Report",
            f"- Total scouts: {scout['total']}  |  Mean: {scout['mean']:.4f}  "
            f"|  Best: {scout['max']:.4f}",
            f"- Above baseline: {scout['above_baseline']}",
            f"- Layers explored: {scout['layers_explored']}",
            "",
        ]

    alignment = digest.get("alignment")
    if alignment:
        lines += [
            "## Marker-Logit Alignment",
            f"- Mean gap (logit - marker): {alignment['mean_gap']:.4f}",
            f"- Expression failures (high logit, low marker): "
            f"{alignment['expression_failures']} ({alignment['expression_failure_pct']:.0f}%)",
            "",
        ]

    compat = digest.get("compatibility")
    if compat:
        lines += [
            "## Ghost Trap -- Mechanistic Compatibility",
            f"- Genomes measured: {compat['total_measured']}",
            f"- Native circuit candidates (high fit + cos > {COS_HIGH_THRESHOLD}): "
            f"{compat['native_circuit_candidates']}",
            f"- Artificial bypass candidates (high fit + cos <= {COS_HIGH_THRESHOLD}): "
            f"{compat['artificial_bypass_candidates']}",
        ]
        if compat.get("cosine_fitness_corr") is not None:
            lines.append(f"- Cosine-fitness correlation: r={compat['cosine_fitness_corr']:.3f}")
        lines.append("")

    rolling_corr = digest.get("rolling_correlation", {})
    if rolling_corr:
        lines += [
            "## Rolling Correlation Stability",
            "(Decimal Magnitude x Density Illusion at milestones)",
        ]
        for k in sorted(rolling_corr.keys(), key=lambda x: int(x.split("_")[1])):
            lines.append(f"- {k}: {rolling_corr[k]}")
        lines.append("")

    coupling = digest.get("trap_coupling")
    if coupling:
        lines += [
            "## Trap Coupling Trajectory",
            f"- Mean |r| across all trap pairs: {coupling['mean_abs_r']:.4f}  "
            f"({coupling['n_pairs']} pairs)",
            "",
        ]

    lnd = digest.get("layer_native_density")
    if lnd:
        has_any = any(v["native"] > 0 for v in lnd.values())
        if has_any:
            lines += [
                "## Layer-wise Native Density",
                "| Layer | Native | Total | Density |",
                "|-------|--------|-------|---------|",
            ]
            for layer, info in lnd.items():
                if info["total"] > 0:
                    lines.append(
                        f"| {layer} | {info['native']} | {info['total']} | {info['density']:.3f} |"
                    )
            lines.append("")

    sel = digest.get("logit_selectivity")
    if sel:
        lines += [
            "## Logit Selectivity",
            f"- Mean selectivity (delta_correct - delta_wrong): {sel['mean']:.4f}",
            f"- High selectivity genomes (>0.5): {sel['high_selectivity']} "
            f"({sel['high_selectivity_pct']:.0f}%)",
            "",
        ]

    drift = digest.get("vector_drift", {})
    if drift:
        lines.append("## Vector Drift (vs Inception Seed)")
        for model, info in drift.items():
            if isinstance(info, dict) and "cosine_to_inception" in info:
                lines.append(
                    f"- {model}: cos={info['cosine_to_inception']:.4f}  "
                    f"(seed_norm={info['inception_norm']:.2f}, "
                    f"current_norm={info['best_norm']:.2f})"
                )
            elif isinstance(info, dict) and "error" in info:
                lines.append(f"- {model}: {info['error']}")
        lines.append("")

    cma = digest.get("cma_state", {})
    if cma:
        lines.append("## CMA-ES State")
        for name, info in cma.items():
            if isinstance(info, dict) and "error" not in info:
                lines.append(
                    f"- **{name}**: gen={info.get('gen_count')}, "
                    f"sigma={info.get('sigma')}, "
                    f"best={info.get('best_fitness')}, "
                    f"plateau={info.get('plateau_count')}"
                )
        lines.append("")

    lines += ["---", f"*Night Watchman v1.1 -- generated {ts}*"]
    return "\n".join(lines)


# ─── Alert Logger ─────────────────────────────────────────────────────────────

def write_alerts(digest: dict, alerts_path: Path) -> None:
    if not digest["alerts"]:
        return
    with open(alerts_path, "a", encoding="utf-8") as f:
        ts = digest["timestamp"]
        for alert in digest["alerts"]:
            f.write(f"[{ts}] {alert}\n")


# ─── Main Loop ────────────────────────────────────────────────────────────────

def run_cycle(results_dir: Path, watchman_dir: Path) -> dict:
    """Execute one wake cycle: snapshot -> analyze -> digest -> write."""
    snap_dir = watchman_dir / "snapshots"
    copied   = snapshot_files(results_dir, watchman_dir)
    disc     = analyze_discovery_log(snap_dir)
    state    = analyze_state(snap_dir)
    scouts   = analyze_scout_map(snap_dir)
    drift    = analyze_vector_drift(snap_dir)
    digest   = compute_digest(disc, state, scouts, drift)
    digest["files_copied"] = copied

    (watchman_dir / "digest_latest.md").write_text(
        render_markdown(digest), encoding="utf-8"
    )

    with open(watchman_dir / "digest_history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(json.loads(json.dumps(digest, default=str))) + "\n")

    write_alerts(digest, watchman_dir / "alerts.log")
    return digest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The Night Watchman — background analysis for Ignis marathon runs"
    )
    parser.add_argument(
        "--results-dir", default=DEFAULT_RESULTS_DIR,
        help=f"Ignis results directory (default: {DEFAULT_RESULTS_DIR})"
    )
    parser.add_argument(
        "--interval", type=int, default=DEFAULT_INTERVAL,
        help=f"Seconds between wake cycles (default: {DEFAULT_INTERVAL})"
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Single analysis pass then exit"
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Results directory not found: {results_dir}")
        print("Provide the correct path with --results-dir")
        sys.exit(1)

    watchman_dir = results_dir / "watchman"
    watchman_dir.mkdir(parents=True, exist_ok=True)

    # Clear any stale WATCHMAN_STOP semaphore from a previous pipeline run
    stale_stop = results_dir / WATCHMAN_STOP_FILE
    if stale_stop.exists():
        try:
            stale_stop.unlink()
            print(f"  Cleared stale {WATCHMAN_STOP_FILE} semaphore from previous run.")
        except OSError:
            pass

    interval_str = f"{args.interval}s" + (" (single pass)" if args.once else "")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║              THE NIGHT WATCHMAN -- ACTIVE                   ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print(f"║  Results:  {str(results_dir)[:50]:<50} ║")
    print(f"║  Output:   {str(watchman_dir)[:50]:<50} ║")
    print(f"║  Interval: {interval_str:<44} ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    cycle_num = 0
    while True:
        cycle_num += 1
        wake_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{wake_time}] Wake cycle {cycle_num}...", end=" ", flush=True)

        try:
            digest    = run_cycle(results_dir, watchman_dir)
            n_alerts  = len(digest.get("alerts",  []))
            n_signals = len(digest.get("signals", []))
            parts = [
                f"gen={digest.get('max_generation', -1)}",
                f"genomes={digest.get('total_genomes', 0)}",
                f"best={digest.get('best_fitness', 0):.4f}",
            ]
            if n_alerts:  parts.append(f"ALERTS={n_alerts}")
            if n_signals: parts.append(f"signals={n_signals}")
            print(" | ".join(parts))
            for alert  in digest.get("alerts",  []): print(f"  !  {alert}")
            for signal in digest.get("signals", []): print(f"  +  {signal}")

        except Exception as e:
            import traceback
            print(f"ERROR: {e}")
            traceback.print_exc()

        if args.once:
            print(f"\nDigest written to: {watchman_dir / 'digest_latest.md'}")
            break

        # Check for pipeline stop signal before sleeping
        watchman_stop = results_dir / WATCHMAN_STOP_FILE
        if watchman_stop.exists():
            print("  Pipeline stopped — running final wake cycle then standing down.")
            try:
                watchman_stop.unlink()
            except OSError:
                pass
            try:
                digest = run_cycle(results_dir, watchman_dir)
                print(f"  Final digest written: {watchman_dir / 'digest_latest.md'}")
            except Exception as e:
                print(f"  Final cycle ERROR: {e}")
            print("Watchman standing down. Goodnight.")
            break

        print(f"  Sleeping {args.interval}s...", flush=True)
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nWatchman standing down. Goodnight.")
            break


if __name__ == "__main__":
    main()
