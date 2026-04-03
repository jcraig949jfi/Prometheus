"""Test Frame H (Primordial Soup) against the Nous backlog.

Runs forge_one with Frame H forced on every attempt, using the Augment API.
Designed to be run as multiple parallel instances with --slice N/M.

Usage:
    python test_frame_h.py --slice 0/5 --duration 20
    python test_frame_h.py --slice 1/5 --duration 20
    ...
    python test_frame_h.py --slice 4/5 --duration 20
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from collections import Counter

# Ensure src/ is on path
sys.path.insert(0, str(Path(__file__).parent))

import hephaestus as heph
from hephaestus import (
    make_client, make_aggie_client, call_aggie_api, call_api,
    build_code_gen_prompt, extract_code, validate, load_enrichment,
    load_tool_from_code, run_trap_battery, safe_filename,
    combo_key, load_ledger, FORGE_DIR, SCRAP_DIR,
    _inject_missing_imports,
)
from prompts import build_code_gen_prompt, FRAME_H_SUFFIX

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("test_frame_h")


def load_all_nous() -> list[dict]:
    """Load all Nous results across all run folders."""
    runs_dir = Path(__file__).parent.parent.parent / "nous" / "runs"
    results = []
    if not runs_dir.exists():
        return results
    for run_dir in sorted(runs_dir.iterdir()):
        resp_file = run_dir / "responses.jsonl"
        if resp_file.exists():
            for line in resp_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        results.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return results


def forge_one_frame_h(aggie_client, entry: dict, run_dir: Path) -> dict:
    """Forge a single item using Frame H only."""
    names = entry.get("concept_names", [])
    score_data = entry.get("score", {})
    ratings = score_data.get("ratings", {})
    response_text = entry.get("response_text", "")

    log.info("Forging [H]: %s", " + ".join(names))

    # Load enrichment
    enrichment = load_enrichment(entry)

    # Build prompt with Frame H forced
    prompt = build_code_gen_prompt(
        names, response_text, ratings,
        enrichment=enrichment, frame="H",
    )

    # Call Augment API
    raw_response = call_aggie_api(aggie_client, prompt)
    if raw_response is None:
        return {"status": "scrap", "reason": "api_call_failed", "frame": "H"}

    # Extract code
    code, extract_status = extract_code(raw_response)
    if code is None:
        return {"status": "scrap", "reason": extract_status, "frame": "H"}

    code = _inject_missing_imports(code)

    # Validate
    valid, reason = validate(code)
    if not valid:
        return {"status": "scrap", "reason": f"validation:{reason}", "frame": "H"}

    # Run battery
    try:
        tool = load_tool_from_code(code)
        test_results = run_trap_battery(tool)
    except Exception as e:
        return {"status": "scrap", "reason": f"test_harness_error: {e}", "frame": "H"}

    if not test_results["passed"]:
        ncd_info = ""
        if "ncd_accuracy" in test_results:
            ncd_info = (f" ncd_acc={test_results['ncd_accuracy']:.0%}"
                        f" ncd_cal={test_results['ncd_calibration']:.0%}")
        reason = (f"trap_battery_failed (acc={test_results['accuracy']:.0%} "
                  f"cal={test_results['calibration']:.0%}{ncd_info})")
        # Save scrap code for analysis
        fname = safe_filename(names)
        scrap_path = run_dir / "scraps" / f"{fname}.py"
        scrap_path.parent.mkdir(parents=True, exist_ok=True)
        scrap_path.write_text(code, encoding="utf-8")
        return {"status": "scrap", "reason": reason, "frame": "H",
                "accuracy": test_results["accuracy"],
                "calibration": test_results["calibration"]}

    # Save forged tool
    fname = safe_filename(names)
    forge_path = run_dir / "forged" / f"{fname}.py"
    forge_path.parent.mkdir(parents=True, exist_ok=True)
    forge_path.write_text(code, encoding="utf-8")

    return {
        "status": "forged",
        "accuracy": test_results["accuracy"],
        "calibration": test_results["calibration"],
        "frame": "H",
    }


def main():
    parser = argparse.ArgumentParser(description="Test Frame H against Nous backlog")
    parser.add_argument("--slice", type=str, default="0/1",
                        help="Which slice to process: N/M (e.g. 0/5 = first fifth)")
    parser.add_argument("--duration", type=int, default=20,
                        help="Max runtime in minutes (default: 20)")
    parser.add_argument("--aggie-model", type=str, default="sonnet4.5",
                        help="Augment model (default: sonnet4.5)")
    parser.add_argument("--delay", type=float, default=3.0,
                        help="Seconds between API calls")
    args = parser.parse_args()

    slice_idx, slice_total = [int(x) for x in args.slice.split("/")]

    log.info("=" * 60)
    log.info("FRAME H TEST — Primordial Soup")
    log.info("  Slice: %d/%d  Duration: %d min  Model: %s",
             slice_idx, slice_total, args.duration, args.aggie_model)
    log.info("=" * 60)

    # Setup run directory
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(__file__).parent.parent / f"test_frame_h_{ts}_slice{slice_idx}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Load and filter candidates
    log.info("Loading Nous results...")
    all_results = load_all_nous()
    log.info("Loaded %d total Nous results", len(all_results))

    ledger = load_ledger()
    already_done = set(ledger.keys())
    unprocessed = [r for r in all_results
                   if combo_key(r) not in already_done
                   and r.get("response_text", "").strip()
                   and not r.get("score", {}).get("is_unproductive", False)]
    log.info("After ledger filter: %d unprocessed", len(unprocessed))

    # Sort by composite score descending
    unprocessed.sort(
        key=lambda r: r.get("score", {}).get("composite_score", 0),
        reverse=True,
    )

    # Take our slice
    chunk_size = len(unprocessed) // slice_total
    start = slice_idx * chunk_size
    end = start + chunk_size if slice_idx < slice_total - 1 else len(unprocessed)
    candidates = unprocessed[start:end]
    log.info("Slice %d/%d: items %d-%d (%d candidates)",
             slice_idx, slice_total, start, end, len(candidates))

    # Create Augment client
    try:
        aggie_client = make_aggie_client(model=args.aggie_model)
        log.info("Augment API client created (model=%s)", args.aggie_model)
    except Exception as e:
        log.error("Failed to create Augment client: %s", e)
        sys.exit(1)

    # Forge loop
    deadline = time.time() + args.duration * 60
    results = []
    forged_count = 0
    scrap_count = 0
    frame_accuracies = []

    for i, entry in enumerate(candidates):
        if time.time() > deadline:
            log.info("Duration limit reached (%d min)", args.duration)
            break

        names = entry.get("concept_names", [])
        result = forge_one_frame_h(aggie_client, entry, run_dir)
        results.append({
            "concepts": names,
            **result,
        })

        if result["status"] == "forged":
            forged_count += 1
            log.info("  FORGED [H]: %s (acc=%.0f%% cal=%.0f%%)",
                     " + ".join(names),
                     result["accuracy"] * 100,
                     result["calibration"] * 100)
        else:
            scrap_count += 1
            acc = result.get("accuracy")
            reason_short = result["reason"][:60]
            if acc is not None:
                log.info("  SCRAP [H]: %s — %s (acc=%.0f%%)",
                         " + ".join(names), reason_short, acc * 100)
            else:
                log.info("  SCRAP [H]: %s — %s", " + ".join(names), reason_short)

        # Track battery accuracy even for scraps (to see how close H gets)
        if result.get("accuracy") is not None:
            frame_accuracies.append(result["accuracy"])

        # Progress every 10 items
        total = forged_count + scrap_count
        if total % 10 == 0:
            elapsed = (time.time() - (deadline - args.duration * 60))
            rate = total / elapsed * 60 if elapsed > 0 else 0
            pass_rate = forged_count / total * 100 if total > 0 else 0
            mean_acc = sum(frame_accuracies) / len(frame_accuracies) * 100 if frame_accuracies else 0
            log.info("  --- Progress: %d/%d forged (%.0f%%), mean_acc=%.0f%%, %.0f items/min ---",
                     forged_count, total, pass_rate, mean_acc, rate)

        time.sleep(args.delay)

    # Cleanup
    try:
        aggie_client.close()
    except Exception:
        pass

    # Final report
    total = forged_count + scrap_count
    pass_rate = forged_count / total * 100 if total > 0 else 0
    mean_acc = sum(frame_accuracies) / len(frame_accuracies) * 100 if frame_accuracies else 0

    log.info("=" * 60)
    log.info("FRAME H TEST COMPLETE — Slice %d/%d", slice_idx, slice_total)
    log.info("  Forged:    %d", forged_count)
    log.info("  Scrapped:  %d", scrap_count)
    log.info("  Total:     %d", total)
    log.info("  Pass rate: %.1f%%", pass_rate)
    log.info("  Mean battery accuracy (all attempts): %.1f%%", mean_acc)
    if frame_accuracies:
        log.info("  Max accuracy: %.0f%%", max(frame_accuracies) * 100)
        log.info("  Median accuracy: %.0f%%",
                 sorted(frame_accuracies)[len(frame_accuracies) // 2] * 100)
    log.info("  Results: %s", run_dir)
    log.info("=" * 60)

    # Save summary
    summary = {
        "slice": f"{slice_idx}/{slice_total}",
        "duration_min": args.duration,
        "model": args.aggie_model,
        "forged": forged_count,
        "scrapped": scrap_count,
        "total": total,
        "pass_rate": pass_rate,
        "mean_accuracy": mean_acc,
        "max_accuracy": max(frame_accuracies) * 100 if frame_accuracies else 0,
        "results": results,
        "completed_at": datetime.now().isoformat(),
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
