#!/usr/bin/env python3
"""
Ignis Log Analyzer — Pre-Archive Extraction
Scans a log file for scientific signals, errors, and key metrics
before you move it out of the way for a restart.

Usage: python ignis_log_analyzer.py <logfile>
"""

import sys
import re
from collections import defaultdict
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def parse_log(filepath):
    lines = Path(filepath).read_text(encoding="utf-8", errors="replace").splitlines()

    # ── Collectors ──
    errors = []
    warnings = []
    falsification_results = []   # old format: "falsification_scores" lines
    verdict_results = []         # new format: [STEP:falsification_verdict] lines
    crucible_results = []
    geometry_lines = []
    inception_data = []
    scout_results = []
    main_results = []
    baseline_data = []
    layer_hits = defaultdict(list)   # layer -> [fitness scores]
    trap_scores = defaultdict(list)  # trap_name -> [(tier, score)]
    zone_counts = {"PRODUCTIVE": 0, "DEAD": 0, "DESTRUCTIVE": 0}
    best_fitness_per_gen = {}
    logit_scores = []
    max_gen_seen = -1
    model_info = {}

    # ── New collectors (v3 logging upgrade) ──
    gen_summaries = {}           # gen_num -> {mean_fit, best_fit, sigma, productive_n,
                                 #             productive_total, falsified_n, best_layer, best_explore}
    scout_reports = {}           # gen_num -> {layers_explored, scout_best_fit, scout_best_layer}
    health_checks = defaultdict(list)  # trap_name -> [(marker_score, marker_tier, logit_score, signal)]
    gen_latencies = {}           # gen_num -> latency_s
    gen_vrams = {}               # gen_num -> vram_peak_gb

    for i, line in enumerate(lines, 1):

        # ── Errors and Warnings ──
        if " ERROR " in line:
            errors.append((i, line.strip()))
        if " WARNING " in line:
            warnings.append((i, line.strip()))

        # ── Model metadata ──
        if "Model geometry:" in line:
            model_info["geometry"] = line.strip()
        if "Model VRAM footprint:" in line:
            model_info["vram"] = line.strip()
        if "d_model=" in line and "n_layers=" in line and "Model loaded" in line:
            model_info["loaded"] = line.strip()
        if "GPU:" in line and "MB total" in line:
            model_info["gpu"] = line.strip()

        # ── Inception / PCA ──
        # Exclude seed-norm/warm-start lines; only capture actual PCA output
        if "inception_pca" in line or (
            "Inception" in line
            and "seed norm" not in line
            and "inception_seed" not in line
            and "Warm-started" not in line
        ):
            inception_data.append((i, line.strip()))

        # ── Random Direction Baseline ──
        if "Random Direction Baseline" in line or "random_baseline" in line.lower():
            baseline_data.append((i, line.strip()))

        # ── Generation tracking ──
        gen_match = re.search(r"\[GEN:(\d+)\]", line)
        if gen_match:
            gen_num = int(gen_match.group(1))
            max_gen_seen = max(max_gen_seen, gen_num)

        # ── [STEP:gen_summary] — single-grep trajectory line (new) ──
        # Format: [STEP:gen_summary] [GEN:003] mean_fit=0.2650, best_fit=0.4393,
        #         sigma=0.02978, productive=16/40, falsified=5/40,
        #         best_layer=21, best_explore=MAIN
        if "[STEP:gen_summary]" in line and gen_match:
            gn = int(gen_match.group(1))
            entry = {}
            for field, pat in [
                ("mean_fit",   r"mean_fit=([\d.]+)"),
                ("best_fit",   r"best_fit=([\d.]+)"),
                ("sigma",      r"sigma=([\d.]+)"),
            ]:
                m = re.search(pat, line)
                if m:
                    entry[field] = float(m.group(1))
            prod_m = re.search(r"productive=(\d+)/(\d+)", line)
            if prod_m:
                entry["productive_n"] = int(prod_m.group(1))
                entry["productive_total"] = int(prod_m.group(2))
            fals_m = re.search(r"falsified=(\d+)/(\d+)", line)
            if fals_m:
                entry["falsified_n"] = int(fals_m.group(1))
            bl_m = re.search(r"best_layer=(\d+)", line)
            if bl_m:
                entry["best_layer"] = int(bl_m.group(1))
            be_m = re.search(r"best_explore=(\w+)", line)
            if be_m:
                entry["best_explore"] = be_m.group(1)
            gen_summaries[gn] = entry

        # ── [STEP:scout_report] — per-generation scout layer exploration (new) ──
        # Format: [STEP:scout_report] [GEN:003] layers_explored=[15,18,22],
        #         scout_best_fit=0.2973, scout_best_layer=15
        if "[STEP:scout_report]" in line and gen_match:
            gn = int(gen_match.group(1))
            entry = {}
            layers_m = re.search(r"layers_explored=\[([^\]]*)\]", line)
            if layers_m:
                raw = layers_m.group(1).strip()
                entry["layers_explored"] = [int(x) for x in raw.split(",") if x.strip()]
            sbf_m = re.search(r"scout_best_fit=([\d.]+)", line)
            if sbf_m:
                entry["scout_best_fit"] = float(sbf_m.group(1))
            sbl_m = re.search(r"scout_best_layer=(\w+)", line)
            if sbl_m:
                raw = sbl_m.group(1)
                entry["scout_best_layer"] = int(raw) if raw.isdigit() else raw
            scout_reports[gn] = entry

        # ── [STEP:falsification_verdict] — new structured verdict (new) ──
        # Format: [STEP:falsification_verdict] PASSED direction_margin=0.1413,
        #         flip_delta=0.1451, noise_ratio=0.494, ortho_ratio=0.678,
        #         shuffle_ratio=0.619
        if "[STEP:falsification_verdict]" in line:
            entry = {"lineno": i, "passed": "PASSED" in line}
            for field, pat in [
                ("direction_margin", r"direction_margin=([\d.]+)"),
                ("flip_delta",       r"flip_delta=([\d.]+)"),
                ("noise_ratio",      r"noise_ratio=([\d.]+)"),
                ("ortho_ratio",      r"ortho_ratio=([\d.]+)"),
                ("shuffle_ratio",    r"shuffle_ratio=([\d.]+)"),
            ]:
                m = re.search(pat, line)
                if m:
                    entry[field] = float(m.group(1))
            if gen_match:
                entry["gen"] = int(gen_match.group(1))
            verdict_results.append(entry)

        # ── [STEP:generation_summary] — latency + VRAM (new fields) ──
        # The existing generation_summary line now includes latency_s and vram_peak_gb
        if "[STEP:generation_summary]" in line and gen_match:
            gn = int(gen_match.group(1))
            lat_m = re.search(r"latency_s=([\d.]+)", line)
            if lat_m:
                gen_latencies[gn] = float(lat_m.group(1))
            vram_m = re.search(r"vram_peak_gb=([\d.]+)", line)
            if vram_m:
                gen_vrams[gn] = float(vram_m.group(1))

        # ── [HEALTH] — per-trap marker vs logit health check (new) ──
        # Format: [HEALTH] Decimal Magnitude | marker=0.10 (FLOOR) | logit=0.723 (Strong)
        if "[HEALTH]" in line:
            health_m = re.match(
                r".*\[HEALTH\]\s+(.+?)\s*\|\s*marker=([\d.]+)\s*\((\w+)\)\s*\|\s*logit=([\d.]+)\s*\((\w+)\)",
                line
            )
            if health_m:
                trap_name   = health_m.group(1).strip()
                marker_score = float(health_m.group(2))
                marker_tier  = health_m.group(3)
                logit_score  = float(health_m.group(4))
                signal       = health_m.group(5)
                health_checks[trap_name].append(
                    (marker_score, marker_tier, logit_score, signal)
                )

        # ── Crucible results (per-genome fitness) ──
        if "[STEP:crucible]" in line and "Fitness:" in line:
            crucible_results.append((i, line.strip()))

            fit_match = re.search(r"Fitness:\s*([\d.]+)", line)
            fitness = float(fit_match.group(1)) if fit_match else None

            layer_match = re.search(r"Layer:\s*(\d+)", line)
            layer = int(layer_match.group(1)) if layer_match else None

            explore_match = re.search(r"\[EXPLORE:(\w+)\]", line)
            explore_type = explore_match.group(1) if explore_match else None

            zone_match = re.search(r"\[ZONE:(\w+)\]", line)
            zone = zone_match.group(1) if zone_match else None

            if zone and zone in zone_counts:
                zone_counts[zone] += 1

            if layer is not None and fitness is not None:
                layer_hits[layer].append(fitness)

            if explore_type == "SCOUT" and fitness is not None:
                scout_results.append((layer, fitness, gen_num if gen_match else None))
            elif explore_type == "MAIN" and fitness is not None:
                main_results.append((layer, fitness, gen_num if gen_match else None))

            if gen_match and fitness is not None:
                gn = int(gen_match.group(1))
                if gn not in best_fitness_per_gen or fitness > best_fitness_per_gen[gn]:
                    best_fitness_per_gen[gn] = fitness

        # ── Old-format falsification scores ──
        if "falsification_scores" in line:
            falsification_results.append((i, line.strip()))

        # ── Geometry metrics ──
        if "Geometry:" in line and "manifold_dim" in line:
            entry = line.strip()
            if not geometry_lines or geometry_lines[-1][1] != entry:
                geometry_lines.append((i, entry))

        # ── Trap-level scores ──
        trap_match = re.search(
            r"\[TRAP:(.*?)\].*?score=([\d.]+),\s*tier=(\w+)", line
        )
        if trap_match:
            trap_name = trap_match.group(1)
            score = float(trap_match.group(2))
            tier = trap_match.group(3)
            trap_scores[trap_name].append((tier, score))

        # ── Logit scores ──
        if "Logit trap" in line and "p_target" in line:
            logit_scores.append((i, line.strip()))

    return {
        "lines_total": len(lines),
        "errors": errors,
        "warnings": warnings,
        "falsification_results": falsification_results,
        "verdict_results": verdict_results,
        "crucible_results": crucible_results,
        "geometry_lines": geometry_lines,
        "inception_data": inception_data,
        "scout_results": scout_results,
        "main_results": main_results,
        "baseline_data": baseline_data,
        "layer_hits": dict(layer_hits),
        "trap_scores": dict(trap_scores),
        "zone_counts": zone_counts,
        "best_fitness_per_gen": best_fitness_per_gen,
        "logit_scores": logit_scores,
        "max_gen_seen": max_gen_seen,
        "model_info": model_info,
        # new
        "gen_summaries": gen_summaries,
        "scout_reports": scout_reports,
        "health_checks": dict(health_checks),
        "gen_latencies": gen_latencies,
        "gen_vrams": gen_vrams,
    }


def print_report(data, filepath):
    print("=" * 72)
    print(f"  Ignis LOG ANALYSIS — {Path(filepath).name}")
    print(f"  Lines scanned: {data['lines_total']}")
    print(f"  Generations seen: 0–{data['max_gen_seen']}")
    print("=" * 72)

    # ── Model Info ──
    if data["model_info"]:
        print("\n┌─ MODEL INFO ─────────────────────────────────────────────┐")
        for k, v in data["model_info"].items():
            cleaned = re.sub(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+\w+\s+", "", v)
            print(f"  {cleaned}")
        print("└──────────────────────────────────────────────────────────┘")

    # ── Errors ──
    print(f"\n{'─' * 40}")
    print(f"  ERRORS: {len(data['errors'])}")
    print(f"{'─' * 40}")
    if data["errors"]:
        seen_msgs = set()
        for lineno, line in data["errors"]:
            err_match = re.search(r"(FAILED.*?)$", line)
            err_key = err_match.group(1) if err_match else line[-80:]
            if err_key not in seen_msgs:
                seen_msgs.add(err_key)
                print(f"  Line {lineno}: {line[-120:]}")
        print(f"  ({len(data['errors'])} total error lines, {len(seen_msgs)} unique)")
    else:
        print("  None — clean run")

    # ── Warnings ──
    print(f"\n{'─' * 40}")
    print(f"  WARNINGS: {len(data['warnings'])}")
    print(f"{'─' * 40}")
    if data["warnings"]:
        seen = set()
        for lineno, line in data["warnings"][:10]:
            cleaned = re.sub(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+\w+\s+", "", line)
            if cleaned not in seen:
                seen.add(cleaned)
                print(f"  Line {lineno}: {cleaned[:120]}")
        if len(data["warnings"]) > 10:
            print(f"  ... and {len(data['warnings']) - 10} more")

    # ── Inception / PCA ──
    print(f"\n{'─' * 40}")
    print(f"  INCEPTION / PCA DATA")
    print(f"{'─' * 40}")
    if data["inception_data"]:
        for lineno, line in data["inception_data"]:
            cleaned = re.sub(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+\w+\s+", "", line)
            print(f"  Line {lineno}: {cleaned[:120]}")
    else:
        print("  No inception data found")

    # ── Random Baseline ──
    if data["baseline_data"]:
        print(f"\n{'─' * 40}")
        print(f"  RANDOM DIRECTION BASELINE")
        print(f"{'─' * 40}")
        for lineno, line in data["baseline_data"]:
            cleaned = re.sub(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+\w+\s+", "", line)
            print(f"  {cleaned[:120]}")

    # ── Zone Distribution ──
    print(f"\n{'─' * 40}")
    print(f"  ZONE DISTRIBUTION (all genomes)")
    print(f"{'─' * 40}")
    total_genomes = sum(data["zone_counts"].values())
    for zone, count in sorted(data["zone_counts"].items()):
        pct = (count / total_genomes * 100) if total_genomes > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"  {zone:>12}: {count:4d} ({pct:5.1f}%) {bar}")
    print(f"  {'TOTAL':>12}: {total_genomes}")

    # ── Generation Trajectory ──
    # Prefer rich gen_summaries; fall back to simple best_fitness_per_gen
    print(f"\n{'─' * 40}")
    print(f"  GENERATION TRAJECTORY")
    print(f"{'─' * 40}")
    gs = data["gen_summaries"]
    lats = data["gen_latencies"]
    vrams = data["gen_vrams"]
    if gs:
        print(f"  {'Gen':>4} {'MeanFit':>8} {'BestFit':>8} {'Sigma':>8} "
              f"{'Prod':>6} {'Fals':>5} {'BestL':>6} {'Lat(s)':>7} {'VRAM':>6}")
        for gen in sorted(gs.keys()):
            e = gs[gen]
            prod_str = (f"{e.get('productive_n', '?')}/{e.get('productive_total', '?')}")
            fals_n   = e.get('falsified_n', '?')
            lat_str  = f"{lats[gen]:.1f}" if gen in lats else "  —"
            vram_str = f"{vrams[gen]:.2f}" if gen in vrams else "  —"
            print(f"  {gen:>4} {e.get('mean_fit', 0):>8.4f} {e.get('best_fit', 0):>8.4f} "
                  f"{e.get('sigma', 0):>8.5f} {prod_str:>6} {str(fals_n):>5} "
                  f"{str(e.get('best_layer', '?')):>6} {lat_str:>7} {vram_str:>6}")
    elif data["best_fitness_per_gen"]:
        for gen in sorted(data["best_fitness_per_gen"].keys()):
            fit = data["best_fitness_per_gen"][gen]
            bar = "█" * int(fit * 40)
            print(f"  Gen {gen:3d}: {fit:.4f} {bar}")
    else:
        print("  No generation data found")

    # ── Scout Layer Exploration ──
    if data["scout_reports"]:
        print(f"\n{'─' * 40}")
        print(f"  SCOUT LAYER EXPLORATION (per generation)")
        print(f"{'─' * 40}")
        print(f"  {'Gen':>4} {'BestFit':>8} {'BestLayer':>10}  Layers Explored")
        for gen in sorted(data["scout_reports"].keys()):
            r = data["scout_reports"][gen]
            layers = r.get("layers_explored", [])
            print(f"  {gen:>4} {r.get('scout_best_fit', 0):>8.4f} "
                  f"{str(r.get('scout_best_layer', '?')):>10}  {layers}")

    # ── Layer Productivity Map ──
    print(f"\n{'─' * 40}")
    print(f"  LAYER PRODUCTIVITY MAP")
    print(f"{'─' * 40}")
    if data["layer_hits"]:
        print(f"  {'Layer':>6} {'Count':>6} {'Mean Fit':>9} {'Max Fit':>9} {'Above BL':>9}")
        for layer in sorted(data["layer_hits"].keys()):
            scores = data["layer_hits"][layer]
            mean_f = sum(scores) / len(scores)
            max_f = max(scores)
            above_baseline = sum(1 for s in scores if s >= 0.30)
            pct_above = above_baseline / len(scores) * 100
            print(f"  {layer:>6} {len(scores):>6} {mean_f:>9.4f} {max_f:>9.4f} {pct_above:>8.1f}%")
    else:
        print("  No layer data found")

    # ── Scout vs Main Comparison ──
    print(f"\n{'─' * 40}")
    print(f"  SCOUT vs MAIN PERFORMANCE")
    print(f"{'─' * 40}")
    if data["main_results"]:
        main_fits = [f for _, f, _ in data["main_results"]]
        print(f"  MAIN:  n={len(main_fits):4d}, mean={sum(main_fits)/len(main_fits):.4f}, "
              f"max={max(main_fits):.4f}")
    if data["scout_results"]:
        scout_fits = [f for _, f, _ in data["scout_results"]]
        print(f"  SCOUT: n={len(scout_fits):4d}, mean={sum(scout_fits)/len(scout_fits):.4f}, "
              f"max={max(scout_fits):.4f}")
        scout_by_layer = defaultdict(list)
        for layer, fit, _ in data["scout_results"]:
            if layer is not None:
                scout_by_layer[layer].append(fit)
        if scout_by_layer:
            print(f"\n  Scout breakdown by layer:")
            print(f"  {'Layer':>6} {'Count':>6} {'Mean Fit':>9} {'Max Fit':>9}")
            for layer in sorted(scout_by_layer.keys()):
                scores = scout_by_layer[layer]
                mean_f = sum(scores) / len(scores)
                max_f = max(scores)
                print(f"  {layer:>6} {len(scores):>6} {mean_f:>9.4f} {max_f:>9.4f}")
    if not data["main_results"] and not data["scout_results"]:
        print("  No explore tags found in logs")

    # ── Trap Performance ──
    print(f"\n{'─' * 40}")
    print(f"  TRAP PERFORMANCE SUMMARY")
    print(f"{'─' * 40}")
    if data["trap_scores"]:
        for trap_name, scores in sorted(data["trap_scores"].items()):
            tier_counts = defaultdict(int)
            for tier, score in scores:
                tier_counts[tier] += 1
            total = len(scores)
            mean_score = sum(s for _, s in scores) / total
            floor_pct = tier_counts.get("FLOOR", 0) / total * 100
            base_pct = tier_counts.get("BASELINE", 0) / total * 100
            credit_pct = tier_counts.get("CREDIT", 0) / total * 100
            print(f"\n  {trap_name}:")
            print(f"    Evaluations: {total}, Mean Score: {mean_score:.3f}")
            print(f"    FLOOR: {tier_counts.get('FLOOR', 0):4d} ({floor_pct:5.1f}%)  "
                  f"BASELINE: {tier_counts.get('BASELINE', 0):4d} ({base_pct:5.1f}%)  "
                  f"CREDIT: {tier_counts.get('CREDIT', 0):4d} ({credit_pct:5.1f}%)")
    else:
        print("  No trap score data found")

    # ── Health Check Summary (marker gap diagnosis) ──
    if data["health_checks"]:
        print(f"\n{'─' * 40}")
        print(f"  HEALTH CHECK SUMMARY (marker gap diagnosis)")
        print(f"{'─' * 40}")
        print(f"  Marker gap candidates: FLOOR marker + Strong logit = model answers correctly")
        print(f"  Genuine failure:        FLOOR marker + Weak logit  = vector is specializing")
        print()
        print(f"  {'Trap':>22} {'Evals':>6} {'FLOOR+Strong':>13} {'FLOOR+Weak':>11} {'FLOOR+Mid':>10}")
        for trap_name, entries in sorted(data["health_checks"].items()):
            total = len(entries)
            floor_strong = sum(1 for ms, mt, ls, sig in entries if mt == "FLOOR" and sig == "Strong")
            floor_weak   = sum(1 for ms, mt, ls, sig in entries if mt == "FLOOR" and sig == "Weak")
            floor_mid    = sum(1 for ms, mt, ls, sig in entries if mt == "FLOOR" and sig == "Mid")
            flag = "  <-- ADD MARKERS?" if floor_strong > total * 0.3 else ""
            print(f"  {trap_name:>22} {total:>6} {floor_strong:>13} {floor_weak:>11} {floor_mid:>10}{flag}")

    # ── Falsification Results ──
    # Prefer new verdict_results; fall back to old falsification_results
    vr = data["verdict_results"]
    fr = data["falsification_results"]
    print(f"\n{'─' * 40}")
    if vr:
        passed = [e for e in vr if e.get("passed")]
        failed = [e for e in vr if not e.get("passed")]
        print(f"  FALSIFICATION VERDICTS ({len(vr)} total — {len(passed)} PASSED, {len(failed)} FAILED)")
        print(f"{'─' * 40}")
        if passed:
            # Sort by direction_margin
            passed.sort(key=lambda x: x.get("direction_margin", 0), reverse=True)
            print(f"\n  Top directional signals (PASSED):")
            print(f"  {'Line':>6} {'Gen':>4} {'DirMrgn':>8} {'FlipDlt':>8} "
                  f"{'NoiseR':>7} {'OrthoR':>7} {'ShufR':>7}")
            for e in passed[:8]:
                print(f"  {e['lineno']:>6} {str(e.get('gen', '?')):>4} "
                      f"{e.get('direction_margin', 0):>8.4f} {e.get('flip_delta', 0):>8.4f} "
                      f"{e.get('noise_ratio', 0):>7.3f} {e.get('ortho_ratio', 0):>7.3f} "
                      f"{e.get('shuffle_ratio', 0):>7.3f}")

            asym = [e for e in passed if e.get("flip_delta", 0) > 0.05]
            print(f"\n  Sign-flip asymmetry (flip_delta > 0.05): {len(asym)}/{len(passed)} PASSED genomes")
    elif fr:
        print(f"  FALSIFICATION RESULTS ({len(fr)} tests)")
        print(f"{'─' * 40}")
        best_directional = []
        for lineno, line in fr:
            scores = {}
            for key in ["primary", "noise", "ortho", "flip", "shuffle"]:
                m = re.search(rf"{key}=([\d.]+)", line)
                if m:
                    scores[key] = float(m.group(1))
            if "primary" in scores and "noise" in scores:
                directional_margin = scores["primary"] - max(
                    scores.get("noise", 0),
                    scores.get("ortho", 0),
                    scores.get("shuffle", 0),
                )
                flip_delta = scores["primary"] - scores.get("flip", scores["primary"])
                best_directional.append({
                    "lineno": lineno,
                    "scores": scores,
                    "margin": directional_margin,
                    "flip_delta": flip_delta,
                })

        if best_directional:
            best_directional.sort(key=lambda x: x["margin"], reverse=True)
            print(f"\n  Top 5 strongest directional signals:")
            print(f"  {'Line':>6} {'Primary':>8} {'Noise':>8} {'Ortho':>8} "
                  f"{'Flip':>8} {'Shuffle':>8} {'Margin':>8}")
            for entry in best_directional[:5]:
                s = entry["scores"]
                print(f"  {entry['lineno']:>6} {s.get('primary', 0):>8.4f} "
                      f"{s.get('noise', 0):>8.4f} {s.get('ortho', 0):>8.4f} "
                      f"{s.get('flip', 0):>8.4f} {s.get('shuffle', 0):>8.4f} "
                      f"{entry['margin']:>8.4f}")
            asym = [e for e in best_directional if e["flip_delta"] > 0.05]
            print(f"\n  Genomes with sign-flip asymmetry (delta > 0.05): {len(asym)}")
            if asym:
                for entry in asym[:3]:
                    s = entry["scores"]
                    print(f"    Line {entry['lineno']}: +v={s['primary']:.4f}, "
                          f"-v={s.get('flip', 0):.4f}, "
                          f"delta={entry['flip_delta']:.4f}")
    else:
        print(f"  FALSIFICATION RESULTS")
        print(f"{'─' * 40}")
        print("  No falsification data found")

    # ── Geometry Evolution ──
    print(f"\n{'─' * 40}")
    print(f"  GEOMETRY EVOLUTION ({len(data['geometry_lines'])} snapshots)")
    print(f"{'─' * 40}")
    if data["geometry_lines"]:
        for lineno, line in data["geometry_lines"]:
            md_match = re.search(r"manifold_dim=([\d.]+)", line)
            ec_match = re.search(r"elite_cos=([\d.]+)", line)
            cr_match = re.search(r"cov_ratio=([\d.]+)", line)
            gen_match = re.search(r"\[GEN:(\d+)\]", line)
            gen = gen_match.group(1) if gen_match else "?"
            md = md_match.group(1) if md_match else "?"
            ec = ec_match.group(1) if ec_match else "?"
            cr = cr_match.group(1) if cr_match else "?"
            print(f"  Gen {gen:>3}: manifold_dim={md}, elite_cos={ec}, cov_ratio={cr}")
    else:
        print("  No geometry data found")

    # ── Logit Score Summary ──
    if data["logit_scores"]:
        print(f"\n{'─' * 40}")
        print(f"  LOGIT SCORES ({len(data['logit_scores'])} evaluations)")
        print(f"{'─' * 40}")
        scores = []
        for _, line in data["logit_scores"]:
            # Use normalized score= (p_target/(p_target+p_anti)), not raw p_target
            score_match = re.search(r"score=([\d.]+)", line)
            if score_match:
                scores.append(float(score_match.group(1)))
        if scores:
            print(f"  score: mean={sum(scores)/len(scores):.4f}, "
                  f"max={max(scores):.4f}, min={min(scores):.4f}")
            high_confidence = sum(1 for s in scores if s > 0.5)
            print(f"  High confidence (score > 0.5): {high_confidence}/{len(scores)}")

    # ── Summary Assessment ──
    print(f"\n{'=' * 72}")
    print(f"  ASSESSMENT")
    print(f"{'=' * 72}")

    issues = []
    findings = []

    if data["errors"]:
        issues.append(f"{len(data['errors'])} errors detected — review before restart")
    if data["zone_counts"]["PRODUCTIVE"] == 0:
        issues.append("No genomes reached PRODUCTIVE zone")
    if data["max_gen_seen"] < 5:
        issues.append(f"Only {data['max_gen_seen'] + 1} generations completed — very early run")

    # Marker gap warning from health checks
    for trap_name, entries in data["health_checks"].items():
        total = len(entries)
        if total == 0:
            continue
        floor_strong = sum(1 for ms, mt, ls, sig in entries if mt == "FLOOR" and sig == "Strong")
        if floor_strong > total * 0.3:
            issues.append(f"[HEALTH] {trap_name}: {floor_strong}/{total} FLOOR+Strong "
                          f"— likely marker gap, consider adding markers")

    if data["zone_counts"]["PRODUCTIVE"] > 0:
        pct = data["zone_counts"]["PRODUCTIVE"] / total_genomes * 100 if total_genomes > 0 else 0
        findings.append(f"{data['zone_counts']['PRODUCTIVE']} productive genomes ({pct:.1f}%)")
    if vr:
        findings.append(f"{len(vr)} falsification verdicts "
                        f"({sum(1 for e in vr if e.get('passed'))} PASSED)")
    elif fr:
        findings.append(f"{len(fr)} genomes reached falsification (old format)")
    if data["scout_results"]:
        findings.append(f"{len(data['scout_results'])} scout evaluations across "
                       f"{len(set(l for l, _, _ in data['scout_results']))} layers")
    if gs:
        best_gen = max(gs.items(), key=lambda kv: kv[1].get("best_fit", 0))
        findings.append(f"Best generation: Gen {best_gen[0]} — "
                        f"fit={best_gen[1].get('best_fit', 0):.4f}, "
                        f"sigma={best_gen[1].get('sigma', 0):.5f}")

    if issues:
        print("  ISSUES:")
        for issue in issues:
            print(f"    !  {issue}")
    if findings:
        print("  FINDINGS:")
        for finding in findings:
            print(f"    +  {finding}")

    print(f"\n{'=' * 72}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <logfile>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    data = parse_log(filepath)
    print_report(data, filepath)
