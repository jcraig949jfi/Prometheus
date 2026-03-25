"""Hephaestus — The Automated Forge.

Takes top-scoring Nous concept combinations, hammers them into testable
Python code via a large model, validates the code, and runs it against
a reasoning trap battery.
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from code_extractor import extract_code
from prompts import build_code_gen_prompt
from test_harness import run_trap_battery, load_tool_from_code
from validator import validate

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HEPHAESTUS_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = HEPHAESTUS_ROOT / "runs"
FORGE_DIR = HEPHAESTUS_ROOT / "forge"
SCRAP_DIR = HEPHAESTUS_ROOT / "scrap"
LEDGER_PATH = HEPHAESTUS_ROOT / "ledger.jsonl"
COEUS_ENRICHMENTS_DIR = HEPHAESTUS_ROOT.parent / "coeus" / "enrichments"
COEUS_SRC = HEPHAESTUS_ROOT.parent / "coeus" / "src"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_PATH = HEPHAESTUS_ROOT / "hephaestus.log"

logger = logging.getLogger("hephaestus")
logger.setLevel(logging.INFO)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_sh = logging.StreamHandler(sys.stdout)
_sh.setFormatter(_fmt)
logger.addHandler(_sh)
_fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
_fh.setFormatter(_fmt)
logger.addHandler(_fh)

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "qwen/qwen3.5-397b-a17b"
API_BASE = "https://integrate.api.nvidia.com/v1"


def make_client() -> OpenAI:
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        logger.error("NVIDIA_API_KEY not set")
        sys.exit(1)
    return OpenAI(base_url=API_BASE, api_key=api_key, timeout=120.0)


def call_api(client: OpenAI, prompt: str, model: str,
             max_retries: int = 5, backoff_base: float = 2.0) -> str | None:
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=4096,
            )
            return resp.choices[0].message.content
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower():
                wait = backoff_base ** (attempt + 1)
                logger.warning("Rate limited, waiting %.1fs (attempt %d)", wait, attempt + 1)
                time.sleep(wait)
            elif any(code in err for code in ("500", "502", "503")):
                wait = backoff_base ** attempt
                logger.warning("Server error, waiting %.1fs (attempt %d)", wait, attempt + 1)
                time.sleep(wait)
            else:
                logger.error("API error: %s", err)
                return None
    logger.error("Exhausted retries")
    return None


# ---------------------------------------------------------------------------
# Checkpoint
# ---------------------------------------------------------------------------

def load_checkpoint(run_dir: Path) -> set[str]:
    """Load set of already-processed combination keys."""
    cp_path = run_dir / "checkpoint.json"
    if cp_path.exists():
        data = json.loads(cp_path.read_text(encoding="utf-8"))
        return set(data.get("processed", []))
    return set()


def save_checkpoint(run_dir: Path, processed: set[str]):
    cp_path = run_dir / "checkpoint.json"
    cp_path.write_text(
        json.dumps({"processed": sorted(processed)}, indent=2),
        encoding="utf-8",
    )


def load_ledger() -> dict[str, dict]:
    """Load the global ledger of all previously attempted combinations.

    Returns dict mapping combo_key -> {status, reason, timestamp, ...}.
    """
    if not LEDGER_PATH.exists():
        return {}
    ledger = {}
    with open(LEDGER_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entry = json.loads(line)
                ledger[entry["key"]] = entry
    return ledger


def append_ledger(key: str, status: str, concept_names: list[str],
                  reason: str = "", accuracy: float = 0.0,
                  calibration: float = 0.0,
                  margin_accuracy: float = 0.0,
                  margin_calibration: float = 0.0):
    """Append a single result to the global ledger."""
    record = {
        "key": key,
        "concept_names": concept_names,
        "status": status,
        "reason": reason,
        "accuracy": accuracy,
        "calibration": calibration,
        "margin_accuracy": margin_accuracy,
        "margin_calibration": margin_calibration,
        "timestamp": datetime.now().isoformat(),
    }
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def find_latest_run() -> Path | None:
    if not RUNS_DIR.exists():
        return None
    runs = sorted(RUNS_DIR.iterdir(), reverse=True)
    for r in runs:
        if (r / "checkpoint.json").exists():
            return r
    return runs[0] if runs else None


# ---------------------------------------------------------------------------
# Forge helpers
# ---------------------------------------------------------------------------

def combo_key(entry: dict) -> str:
    """Unique key for a Nous combination."""
    names = entry.get("concept_names", [])
    return " + ".join(sorted(names))


def load_enrichment(entry: dict) -> dict | None:
    """Load Coeus enrichment for a Nous entry, if available."""
    key = combo_key(entry)
    safe_key = key.replace(" ", "_").replace("+", "x")
    path = COEUS_ENRICHMENTS_DIR / f"{safe_key}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def safe_filename(names: list[str]) -> str:
    """Turn concept names into a filesystem-safe filename."""
    joined = "_x_".join(n.replace(" ", "_") for n in names)
    # Truncate if too long
    if len(joined) > 120:
        joined = joined[:120]
    return joined.lower()


def save_forge(code: str, entry: dict, test_results: dict, run_dir: Path):
    """Save a successfully forged tool."""
    fname = safe_filename(entry["concept_names"])
    forge_path = FORGE_DIR / f"{fname}.py"
    forge_path.write_text(code, encoding="utf-8")

    # Sidecar with metadata
    meta = {
        "concept_names": entry["concept_names"],
        "concept_fields": entry.get("concept_fields", []),
        "nous_composite_score": entry.get("score", {}).get("composite_score"),
        "test_accuracy": test_results["accuracy"],
        "test_calibration": test_results["calibration"],
        "forged_at": datetime.now().isoformat(),
    }
    meta_path = FORGE_DIR / f"{fname}.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # Also log in run dir
    log_path = run_dir / "forged.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(meta) + "\n")

    logger.info("FORGED: %s (acc=%.0f%% cal=%.0f%%)",
                " + ".join(entry["concept_names"]),
                test_results["accuracy"] * 100,
                test_results["calibration"] * 100)


def save_scrap(code: str | None, entry: dict, reason: str, run_dir: Path):
    """Save a failed forge attempt."""
    fname = safe_filename(entry["concept_names"])
    if code:
        scrap_code_path = SCRAP_DIR / f"{fname}.py"
        scrap_code_path.write_text(code, encoding="utf-8")

    meta = {
        "concept_names": entry["concept_names"],
        "concept_fields": entry.get("concept_fields", []),
        "nous_composite_score": entry.get("score", {}).get("composite_score"),
        "failure_reason": reason,
        "scrapped_at": datetime.now().isoformat(),
    }
    meta_path = SCRAP_DIR / f"{fname}.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # Also log in run dir
    log_path = run_dir / "scrapped.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(meta) + "\n")

    logger.info("SCRAP: %s — %s", " + ".join(entry["concept_names"]), reason)


# ---------------------------------------------------------------------------
# Rankings
# ---------------------------------------------------------------------------

def write_rankings(forged: list[dict], scrapped: list[dict], run_dir: Path):
    """Write a rankings.md summary of the run."""
    lines = [
        f"# Hephaestus Forge Run — {run_dir.name}",
        "",
        f"**Forged**: {len(forged)} | **Scrapped**: {len(scrapped)} | "
        f"**Total**: {len(forged) + len(scrapped)}",
        "",
    ]

    if forged:
        # Sort by accuracy descending, then calibration
        forged.sort(key=lambda x: (x.get("test_accuracy", 0),
                                    x.get("test_calibration", 0)), reverse=True)
        lines.append("## Forged Tools (passed trap battery)")
        lines.append("")
        lines.append("| Rank | Concepts | Nous Score | Accuracy | Calibration |")
        lines.append("|------|----------|-----------|----------|-------------|")
        for i, f in enumerate(forged, 1):
            concepts = " + ".join(f.get("concept_names", []))
            nous = f.get("nous_composite_score", "?")
            acc = f"{f.get('test_accuracy', 0) * 100:.0f}%"
            cal = f"{f.get('test_calibration', 0) * 100:.0f}%"
            lines.append(f"| {i} | {concepts} | {nous} | {acc} | {cal} |")
        lines.append("")

    if scrapped:
        lines.append("## Scrapped (failed)")
        lines.append("")
        lines.append("| Concepts | Nous Score | Reason |")
        lines.append("|----------|-----------|--------|")
        for s in scrapped:
            concepts = " + ".join(s.get("concept_names", []))
            nous = s.get("nous_composite_score", "?")
            reason = s.get("failure_reason", "unknown")
            lines.append(f"| {concepts} | {nous} | {reason} |")
        lines.append("")

    (run_dir / "rankings.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

NOUS_ROOT = HEPHAESTUS_ROOT.parent / "nous"


def load_nous_results(path: Path) -> list[dict]:
    """Load and parse a Nous responses.jsonl file."""
    results = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


def load_all_nous_results() -> tuple[list[dict], list[Path]]:
    """Load results from ALL Nous run folders.

    Returns (results, source_files) where results is the combined list
    and source_files is the list of JSONL paths that were loaded.
    """
    runs_dir = NOUS_ROOT / "runs"
    if not runs_dir.exists():
        return [], []

    results = []
    sources = []
    seen_keys = set()

    for run_dir in sorted(runs_dir.iterdir()):
        jsonl = run_dir / "responses.jsonl"
        if not jsonl.exists():
            continue
        sources.append(jsonl)
        for entry in load_nous_results(jsonl):
            # Deduplicate across runs by combo key
            names = entry.get("concept_names", [])
            key = " + ".join(sorted(names))
            if key not in seen_keys:
                seen_keys.add(key)
                results.append(entry)

    return results, sources


def _composite(entry: dict) -> float:
    """Get composite score, treating None/missing as 0."""
    return entry.get("score", {}).get("composite_score") or 0.0


def _load_coeus_scores() -> dict:
    """Load Coeus concept scores for priority ranking."""
    scores_path = COEUS_ENRICHMENTS_DIR.parent / "graphs" / "concept_scores.json"
    if not scores_path.exists():
        return {}
    try:
        return json.loads(scores_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _forge_priority(entry: dict, coeus_scores: dict) -> float:
    """Compute forge priority score using Nous composite + Coeus causal data.

    priority = composite_score + sum(concept_forge_effects) + sum(pair_synergies)

    This pushes concepts with high causal forge affinity to the front of the
    queue, instead of just relying on Nous theoretical scores.
    """
    composite = _composite(entry)
    names = entry.get("concept_names", [])

    # Sum causal forge effects for each concept in the triple
    concept_influence = coeus_scores.get("concept_influence", {})
    forge_boost = 0.0
    for name in names:
        influence = concept_influence.get(name, {})
        forge_boost += influence.get("forge_effect", 0)

    # Add pair synergies
    pair_synergy = coeus_scores.get("pair_synergy", {})
    synergy_boost = 0.0
    for i, c1 in enumerate(names):
        for c2 in names[i+1:]:
            for key_form in [f"{c1} + {c2}", f"{c2} + {c1}"]:
                if key_form in pair_synergy:
                    synergy_boost += pair_synergy[key_form]

    return composite + forge_boost + synergy_boost


def filter_results(results: list[dict], top_n: int | None = None,
                   min_score: float | None = None,
                   include_unscored: bool = False) -> list[dict]:
    """Filter Nous results by top-N or minimum composite score.

    If include_unscored is True, entries with composite_score=0 (scorer
    couldn't parse ratings) are kept — useful when Nous responses have
    content but the scorer failed to extract numeric ratings.

    Results are sorted by Coeus forge priority (if available), falling
    back to composite score.
    """
    # Remove explicitly unproductive
    filtered = [r for r in results
                if not r.get("score", {}).get("is_unproductive", False)]
    # Remove empty responses
    filtered = [r for r in filtered if r.get("response_text", "").strip()]

    if min_score is not None:
        if include_unscored:
            filtered = [r for r in filtered
                        if _composite(r) >= min_score or _composite(r) == 0.0]
        else:
            filtered = [r for r in filtered
                        if _composite(r) >= min_score]

    # Sort by Coeus forge priority (falls back to composite if no Coeus data)
    coeus_scores = _load_coeus_scores()
    if coeus_scores:
        filtered.sort(key=lambda r: _forge_priority(r, coeus_scores), reverse=True)
        logger.info("Sorted by Coeus forge priority")
    else:
        filtered.sort(key=_composite, reverse=True)

    if top_n is not None:
        filtered = filtered[:top_n]

    return filtered


def forge_one(client: OpenAI, entry: dict, model: str,
              run_dir: Path) -> dict | None:
    """Process a single Nous result through the full forge pipeline."""
    names = entry.get("concept_names", [])
    score_data = entry.get("score", {})
    ratings = score_data.get("ratings", {})
    response_text = entry.get("response_text", "")

    logger.info("Forging: %s (composite=%.1f)",
                " + ".join(names), score_data.get("composite_score", 0))

    # 0. Load Coeus enrichment if available
    enrichment = load_enrichment(entry)
    if enrichment:
        logger.info("  Coeus enrichment loaded")

    # 1. Build prompt and call API
    prompt = build_code_gen_prompt(names, response_text, ratings, enrichment=enrichment)
    raw_response = call_api(client, prompt, model)
    if raw_response is None:
        save_scrap(None, entry, "api_call_failed", run_dir)
        return {"status": "scrap", "reason": "api_call_failed"}

    # 2. Extract code
    code, extract_status = extract_code(raw_response)
    if code is None:
        save_scrap(None, entry, extract_status, run_dir)
        return {"status": "scrap", "reason": extract_status}

    # 3. Validate
    valid, reason = validate(code)
    if not valid:
        save_scrap(code, entry, f"validation:{reason}", run_dir)
        return {"status": "scrap", "reason": f"validation:{reason}"}

    # 4. Run trap battery
    try:
        tool = load_tool_from_code(code)
        test_results = run_trap_battery(tool)
    except Exception as e:
        save_scrap(code, entry, f"test_harness_error: {e}", run_dir)
        return {"status": "scrap", "reason": f"test_harness_error: {e}"}

    if not test_results["passed"]:
        ncd_info = ""
        if "ncd_accuracy" in test_results:
            ncd_info = (f" ncd_acc={test_results['ncd_accuracy']:.0%}"
                        f" ncd_cal={test_results['ncd_calibration']:.0%}")
        reason = (f"trap_battery_failed (acc={test_results['accuracy']:.0%} "
                  f"cal={test_results['calibration']:.0%}{ncd_info})")
        save_scrap(code, entry, reason, run_dir)
        return {"status": "scrap", "reason": reason}

    # 5. Save to forge
    save_forge(code, entry, test_results, run_dir)
    return {
        "status": "forged",
        "accuracy": test_results["accuracy"],
        "calibration": test_results["calibration"],
        "margin_accuracy": test_results.get("margin_accuracy", 0),
        "margin_calibration": test_results.get("margin_calibration", 0),
    }


def _trigger_coeus():
    """Re-run Coeus to rebuild the causal graph with latest forge data."""
    if not COEUS_SRC.exists():
        logger.warning("Coeus src not found at %s, skipping rebuild", COEUS_SRC)
        return
    try:
        logger.info("Triggering Coeus rebuild...")
        _saved_path = sys.path[:]
        sys.path.insert(0, str(COEUS_SRC))
        try:
            import importlib
            coeus_mod = importlib.import_module("coeus")
            importlib.reload(coeus_mod)
            coeus_mod.main()
            logger.info("Coeus rebuild complete — enrichments and priority scores updated")
        finally:
            sys.path[:] = _saved_path
            sys.modules.pop("coeus", None)
    except Exception as e:
        logger.warning("Coeus rebuild failed: %s (continuing forge)", e)


def _trigger_reports():
    """Rebuild human-readable reports (incremental — only changed entries)."""
    try:
        logger.info("Rebuilding human-readable reports (incremental)...")
        import importlib
        saved_argv = sys.argv[:]
        sys.argv = ["build_reports.py"]  # incremental mode (default)
        try:
            reports_mod = importlib.import_module("build_reports")
            importlib.reload(reports_mod)
            reports_mod.main()
        finally:
            sys.argv = saved_argv
        logger.info("Reports rebuild complete")
    except Exception as e:
        logger.warning("Reports rebuild failed: %s (continuing forge)", e)


def _load_nous(args, run_dir: Path) -> tuple[list[dict], str]:
    """Load Nous results based on CLI args. Returns (results, source_label)."""
    if args.nous_run:
        nous_path = Path(args.nous_run)
        if not nous_path.exists():
            logger.error("Nous file not found: %s", nous_path)
            sys.exit(1)
        results = load_nous_results(nous_path)
        logger.info("Loaded %d Nous results from %s", len(results), nous_path)
        return results, str(nous_path)

    if args.resume and not args.nous_run:
        meta_path = run_dir / "meta.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            src = meta.get("nous_run")
            if src and src != "all_runs":
                nous_path = Path(src)
                if nous_path.exists():
                    results = load_nous_results(nous_path)
                    logger.info("Loaded %d Nous results from %s", len(results), nous_path)
                    return results, str(nous_path)

    results, sources = load_all_nous_results()
    logger.info("Loaded %d Nous results from %d run folders", len(results), len(sources))
    return results, "all_runs"


def _forge_batch(client: OpenAI, filtered: list[dict], args,
                 run_dir: Path, processed: set[str],
                 total_count: int, shutdown_flag: list) -> tuple[list, list, int]:
    """Process one batch of candidates. Returns (forged, scrapped, new_count)."""
    forged_results = []
    scrapped_results = []
    count = 0

    for entry in filtered:
        if shutdown_flag[0]:
            break

        key = combo_key(entry)
        if key in processed:
            continue

        result = forge_one(client, entry, args.model, run_dir)

        processed.add(key)
        count += 1
        running_total = total_count + count

        names = entry.get("concept_names", [])
        if result and result["status"] == "forged":
            forged_results.append({
                "concept_names": names,
                "nous_composite_score": entry.get("score", {}).get("composite_score"),
                "test_accuracy": result.get("accuracy"),
                "test_calibration": result.get("calibration"),
            })
            append_ledger(key, "forged", names,
                          accuracy=result.get("accuracy", 0),
                          calibration=result.get("calibration", 0),
                          margin_accuracy=result.get("margin_accuracy", 0),
                          margin_calibration=result.get("margin_calibration", 0))
        elif result:
            scrapped_results.append({
                "concept_names": names,
                "nous_composite_score": entry.get("score", {}).get("composite_score"),
                "failure_reason": result.get("reason"),
            })
            append_ledger(key, "scrap", names, reason=result.get("reason", ""))

        # Checkpoint
        if count % 5 == 0:
            save_checkpoint(run_dir, processed)

        # Periodic Coeus rebuild
        if (args.coeus_interval > 0 and running_total % args.coeus_interval == 0
                and running_total > 0 and not shutdown_flag[0]):
            _trigger_coeus()

        # Periodic reports rebuild
        if (args.reports_interval > 0 and running_total % args.reports_interval == 0
                and running_total > 0 and not shutdown_flag[0]):
            _trigger_reports()

        # Rate limit
        if not shutdown_flag[0]:
            time.sleep(args.delay)

    save_checkpoint(run_dir, processed)
    return forged_results, scrapped_results, count


def main():
    parser = argparse.ArgumentParser(
        description="Hephaestus — forge Nous concepts into tested reasoning tools"
    )
    parser.add_argument("--nous-run", type=str, default=None,
                        help="Path to a specific Nous responses.jsonl (omit to scan all Nous runs)")
    parser.add_argument("--top-n", type=int, default=None,
                        help="Take top N results by composite score")
    parser.add_argument("--min-score", type=float, default=None,
                        help="Minimum composite score threshold")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help="Model to use for code generation")
    parser.add_argument("--delay", type=float, default=3.0,
                        help="Seconds between API calls")
    parser.add_argument("--all", action="store_true",
                        help="Process all non-unproductive results (no score filter)")
    parser.add_argument("--include-unscored", action="store_true",
                        help="Include entries where scorer returned 0 (ratings unparsed)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume the most recent run")
    parser.add_argument("--runonce", action="store_true",
                        help="Process current candidates and exit (default: run continuously)")
    parser.add_argument("--poll-interval", type=float, default=300,
                        help="Seconds between Nous re-scans in continuous mode (default: 300)")
    parser.add_argument("--coeus-interval", type=int, default=50,
                        help="Re-run Coeus every N forges to update causal graph (0=disable)")
    parser.add_argument("--reports-interval", type=int, default=50,
                        help="Rebuild human-readable reports every N forges (0=disable)")
    args = parser.parse_args()

    # Default filter: --all in continuous mode, top 20 in runonce
    if args.top_n is None and args.min_score is None and not args.resume:
        if args.runonce and not args.all:
            args.top_n = 20
        else:
            args.all = True

    # Resolve run directory
    if args.resume:
        run_dir = find_latest_run()
        if run_dir is None:
            logger.error("No previous run found to resume")
            sys.exit(1)
        logger.info("Resuming run: %s", run_dir.name)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = RUNS_DIR / ts
        run_dir.mkdir(parents=True, exist_ok=True)
        logger.info("New run: %s", run_dir.name)

    # Setup graceful shutdown
    shutdown_flag = [False]

    def handle_signal(sig, frame):
        shutdown_flag[0] = True
        logger.info("Shutdown requested, finishing current item...")

    signal.signal(signal.SIGINT, handle_signal)

    client = make_client()
    total_forged = []
    total_scrapped = []
    total_count = 0
    cycle = 0

    mode = "runonce" if args.runonce else "continuous"
    logger.info("Mode: %s", mode)

    while not shutdown_flag[0]:
        cycle += 1

        # (Re-)load Nous results each cycle to pick up new data
        results, nous_source = _load_nous(args, run_dir)

        if not results:
            if args.runonce:
                logger.error("No Nous results found")
                sys.exit(1)
            logger.info("No Nous results found, waiting...")
            time.sleep(args.poll_interval)
            continue

        # Load ledger fresh each cycle
        ledger = load_ledger()
        processed = load_checkpoint(run_dir)
        already_done = set(ledger.keys()) | processed
        logger.info("Ledger: %d globally processed, checkpoint: %d this run",
                    len(ledger), len(processed))

        # Strip already-processed
        unprocessed = [r for r in results if combo_key(r) not in already_done]
        logger.info("After ledger filter: %d unprocessed Nous results", len(unprocessed))

        filtered = filter_results(
            unprocessed, top_n=args.top_n, min_score=args.min_score,
            include_unscored=args.include_unscored or args.all,
        )
        logger.info("Filtered to %d candidates", len(filtered))

        # Save run metadata
        meta = {
            "nous_run": nous_source,
            "top_n": args.top_n,
            "min_score": args.min_score,
            "model": args.model,
            "mode": mode,
            "cycle": cycle,
            "n_candidates": len(filtered),
            "started_at": datetime.now().isoformat(),
        }
        (run_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        if not filtered:
            if args.runonce:
                logger.info("No unprocessed candidates — nothing to forge")
                break
            logger.info("No new candidates. Sleeping %ds before re-scanning Nous...",
                        int(args.poll_interval))
            # Sleep in short chunks so Ctrl+C is responsive
            slept = 0.0
            while slept < args.poll_interval and not shutdown_flag[0]:
                time.sleep(min(5.0, args.poll_interval - slept))
                slept += 5.0
            continue

        # Forge the batch
        forged, scrapped, batch_count = _forge_batch(
            client, filtered, args, run_dir, processed,
            total_count, shutdown_flag,
        )
        total_forged.extend(forged)
        total_scrapped.extend(scrapped)
        total_count += batch_count

        # Write rankings after each batch
        write_rankings(total_forged, total_scrapped, run_dir)

        if args.runonce:
            break

        if not shutdown_flag[0]:
            logger.info("Batch complete (%d forged, %d scrapped). "
                        "Sleeping %ds before re-scanning Nous...",
                        len(forged), len(scrapped), int(args.poll_interval))
            slept = 0.0
            while slept < args.poll_interval and not shutdown_flag[0]:
                time.sleep(min(5.0, args.poll_interval - slept))
                slept += 5.0

    # Final summary
    logger.info("=" * 60)
    logger.info("FORGE COMPLETE")
    logger.info("  Forged:   %d", len(total_forged))
    logger.info("  Scrapped: %d", len(total_scrapped))
    logger.info("  Total:    %d", len(total_forged) + len(total_scrapped))
    logger.info("  Cycles:   %d", cycle)
    if total_forged:
        logger.info("  Top performers:")
        total_forged.sort(key=lambda x: x.get("test_accuracy", 0), reverse=True)
        for f in total_forged[:5]:
            logger.info("    %s — acc=%.0f%% cal=%.0f%%",
                        " + ".join(f["concept_names"]),
                        f["test_accuracy"] * 100,
                        f["test_calibration"] * 100)
    logger.info("  Results: %s", run_dir)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
