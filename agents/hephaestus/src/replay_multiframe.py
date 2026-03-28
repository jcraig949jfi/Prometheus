#!/usr/bin/env python3
"""Replay existing Nous data through the multi-frame forge pipeline.

Re-forges triples that were already attempted with Frame A using Frames B, C, D.
Uses saved Nous responses — no API calls to Nous. Only calls code gen API.

Usage:
    python replay_multiframe.py --frame B --limit 120
    python replay_multiframe.py --all --limit 80
    python replay_multiframe.py --all --limit 80 --dry-run
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [REPLAY] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("replay")

HEPH_ROOT = Path(__file__).resolve().parent.parent
NOUS_ROOT = HEPH_ROOT.parent / "nous"


def load_all_nous_responses() -> list[dict]:
    """Load all saved Nous responses, deduplicated by triple."""
    results = []
    runs_dir = NOUS_ROOT / "runs"
    if not runs_dir.exists():
        return results

    for run_dir in sorted(runs_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        jsonl = run_dir / "responses.jsonl"
        if not jsonl.exists():
            continue
        with open(jsonl, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("concept_names") and entry.get("response_text"):
                        results.append(entry)
                except json.JSONDecodeError:
                    continue

    # Deduplicate: keep highest composite per triple
    seen = {}
    for entry in results:
        key = " + ".join(sorted(entry["concept_names"]))
        score = entry.get("score", {}).get("composite_score", 0)
        if key not in seen or score > seen[key].get("score", {}).get("composite_score", 0):
            seen[key] = entry

    return list(seen.values())


def load_ledger_keys() -> set[str]:
    """Load ledger and return set of 'key|frame' strings."""
    ledger_path = HEPH_ROOT / "ledger.jsonl"
    if not ledger_path.exists():
        return set()
    keys = set()
    with open(ledger_path, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line.strip())
                key = e.get("key", "")
                frame = e.get("frame", "A")
                keys.add(f"{key}|{frame}")
            except:
                continue
    return keys


def main():
    parser = argparse.ArgumentParser(description="Replay Nous data through multi-frame forge")
    parser.add_argument("--frame", choices=["B", "C", "D"], help="Specific frame")
    parser.add_argument("--all", action="store_true", help="Run all 3 new frames")
    parser.add_argument("--limit", type=int, default=80, help="Max triples per frame")
    parser.add_argument("--dry-run", action="store_true", help="Show plan only")
    parser.add_argument("--delay", type=float, default=3.0, help="Delay between API calls")
    args = parser.parse_args()

    if not args.frame and not args.all:
        parser.error("Must specify --frame or --all")

    frames = [args.frame] if args.frame else ["B", "C", "D"]

    # Load Nous data
    log.info("Loading Nous responses...")
    nous_data = load_all_nous_responses()
    log.info("Loaded %d unique Nous triples", len(nous_data))

    ledger_keys = load_ledger_keys()
    log.info("Ledger has %d entries", len(ledger_keys))

    # Sort by composite score descending
    nous_data.sort(key=lambda x: x.get("score", {}).get("composite_score", 0), reverse=True)

    # Import forge machinery
    if not args.dry_run:
        from hephaestus import (make_client, forge_one, append_ledger,
                                combo_key, load_enrichment)
        from prompts import build_code_gen_prompt, select_frame
        import prompts

        # Load .env for API key
        env_file = HEPH_ROOT.parent / "eos" / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

        client = make_client()

        # Create a run directory for replay
        from datetime import datetime
        run_dir = HEPH_ROOT / "runs" / f"replay_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        run_dir.mkdir(parents=True, exist_ok=True)

        # Get model
        try:
            from hephaestus import DEFAULT_MODEL
            model = DEFAULT_MODEL
        except ImportError:
            model = "nvidia/llama-3.1-nemotron-ultra-253b-v1"

    for frame in frames:
        log.info("")
        log.info("=" * 60)
        log.info("FRAME %s — %s", frame,
                 {"B": "Constructive Computer", "C": "Dynamics Tracker",
                  "D": "Judgment Calibrator"}[frame])
        log.info("=" * 60)

        # Find triples not yet attempted with this frame
        candidates = []
        for entry in nous_data:
            key = " + ".join(sorted(entry["concept_names"]))
            if f"{key}|{frame}" not in ledger_keys:
                candidates.append(entry)
            if len(candidates) >= args.limit:
                break

        log.info("Candidates: %d (limit: %d)", len(candidates), args.limit)

        if args.dry_run:
            for entry in candidates[:10]:
                names = entry["concept_names"]
                score = entry.get("score", {}).get("composite_score", 0)
                log.info("  Would forge: %s (composite=%.1f)", " + ".join(names), score)
            if len(candidates) > 10:
                log.info("  ... and %d more", len(candidates) - 10)
            continue

        # Override frame in BOTH the prompts module AND the hephaestus module
        # (hephaestus imports build_code_gen_prompt at module load time)
        import prompts as prompts_mod
        import hephaestus as heph_mod
        original_build = prompts_mod.build_code_gen_prompt

        def frame_override_build(concept_names, response_text, ratings,
                                  enrichment=None, frame_override=frame):
            return original_build(concept_names, response_text, ratings,
                                   enrichment=enrichment, frame=frame_override)

        # Patch in both namespaces
        prompts_mod.build_code_gen_prompt = frame_override_build
        heph_mod.build_code_gen_prompt = frame_override_build

        forged = 0
        scrapped = 0

        for i, entry in enumerate(candidates):
            names = entry["concept_names"]
            key = " + ".join(sorted(names))
            comp = entry.get("score", {}).get("composite_score", 0)

            log.info("[%d/%d] Frame %s: %s (composite=%.1f)",
                     i + 1, len(candidates), frame, " + ".join(names), comp)

            try:
                result = forge_one(client, entry, model, run_dir)

                if result and result.get("status") == "forged":
                    forged += 1
                    log.info("  FORGED (Frame %s): acc=%.0f%% cal=%.0f%%",
                             frame, result.get("accuracy", 0) * 100,
                             result.get("calibration", 0) * 100)
                else:
                    scrapped += 1
                    reason = result.get("reason", "unknown") if result else "no result"
                    log.info("  SCRAP (Frame %s): %s", frame, reason)

                # Track that this triple+frame was attempted
                ledger_keys.add(f"{key}|{frame}")

            except Exception as e:
                scrapped += 1
                log.error("  ERROR: %s", e)

            time.sleep(args.delay)

        # Restore original prompt builder in both namespaces
        prompts_mod.build_code_gen_prompt = original_build
        heph_mod.build_code_gen_prompt = original_build

        log.info("")
        log.info("Frame %s: %d forged, %d scrapped (%.1f%%)",
                 frame, forged, scrapped,
                 forged / max(forged + scrapped, 1) * 100)

    log.info("")
    log.info("Replay complete.")


if __name__ == "__main__":
    main()
