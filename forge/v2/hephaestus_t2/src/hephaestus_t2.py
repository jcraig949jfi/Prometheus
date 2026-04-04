"""
Tier 2 Hephaestus — Autonomous forge loop.

Generates candidate reasoning tools via DeepSeek (primary) / NVIDIA (fallback),
validates through the runner/tester pipeline, writes passing tools to forge/.

Polls Nous T2 for substrate suggestions and uses gap analysis to prioritize
which categories to target. Runs continuously until stopped.

Usage:
    python hephaestus_t2.py --poll-interval 300
    python hephaestus_t2.py --runonce
    python hephaestus_t2.py --resume
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import shutil
import signal
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, error as urlerror

# ---------------------------------------------------------------------------
# Paths — all relative to repo root
# ---------------------------------------------------------------------------

_SRC = Path(__file__).resolve().parent
_T2_ROOT = _SRC.parent                     # forge/v2/hephaestus_t2
_FORGE_V2 = _T2_ROOT.parent               # forge/v2
_FORGE = _FORGE_V2.parent                  # forge
_REPO = _FORGE.parent                      # F:\Prometheus

FORGE_DIR = _T2_ROOT / "forge"
SCRAP_DIR = _T2_ROOT / "scrap"
RUNS_DIR = _T2_ROOT / "runs"
LEDGER_PATH = _T2_ROOT / "ledger_t2.jsonl"
NOUS_RUNS = _FORGE_V2 / "nous_t2" / "runs"
CANDIDATES_DIR = _FORGE / "candidates"
VERDICTS_DIR = _FORGE / "verdicts"

for _d in [FORGE_DIR, SCRAP_DIR, RUNS_DIR, CANDIDATES_DIR, VERDICTS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# Add imports
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "agents" / "hephaestus" / "src"))
sys.path.insert(0, str(_FORGE))

from forge.builder import generate_tool_prompt, T2_CATEGORIES
from forge.llm_client import _load_api_key, _extract_python, PROVIDERS
from forge.runner import (
    check_banned_patterns,
    check_composition_requirements,
    get_existing_tool_paths,
)
from forge.tester import evaluate_tool as tester_evaluate

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("hephaestus_t2")

# ---------------------------------------------------------------------------
# Shutdown handling
# ---------------------------------------------------------------------------

_shutdown = [False]


def _signal_handler(sig, frame):
    logger.info("Shutdown requested — finishing current item...")
    _shutdown[0] = True


signal.signal(signal.SIGINT, _signal_handler)

# ---------------------------------------------------------------------------
# API providers
# ---------------------------------------------------------------------------

DEEPSEEK = {
    "url": "https://api.deepseek.com/chat/completions",
    "model": "deepseek-chat",
    "key_env": "DEEPSEEK_API_KEY",
    "headers": {},
    "timeout": 120,
}

NVIDIA = {
    "url": "https://integrate.api.nvidia.com/v1/chat/completions",
    "model": "qwen/qwen3.5-397b-a17b",
    "key_env": "NVIDIA_API_KEY",
    "headers": {},
    "timeout": 120,
}


def _call_llm(
    system_prompt: str,
    provider: dict,
    api_key: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    max_retries: int = 3,
) -> str | None:
    """Call an LLM API with retries. Returns raw response text or None."""
    payload = json.dumps({
        "model": provider["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate the ReasoningTool class now. Output ONLY Python code."},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    headers.update(provider.get("headers", {}))

    timeout = provider.get("timeout", 120)

    for attempt in range(max_retries):
        try:
            req = request.Request(
                provider["url"], data=payload, headers=headers, method="POST",
            )
            with request.urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]

        except urlerror.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:200]
            code = e.code
            if code in (401, 403):
                logger.error("Auth error (%s %d): %s", provider["model"], code, body)
                return None  # Don't retry auth errors
            logger.warning(
                "HTTP %d from %s (attempt %d/%d): %s",
                code, provider["model"], attempt + 1, max_retries, body,
            )

        except Exception as e:
            logger.warning(
                "%s error (attempt %d/%d): %s",
                provider["model"], attempt + 1, max_retries, e,
            )

        if attempt < max_retries - 1:
            wait = (2 ** attempt) + random.random()
            time.sleep(wait)

    return None


def call_with_fallback(system_prompt: str) -> tuple[str | None, str]:
    """Try DeepSeek first, fall back to NVIDIA. Returns (response, provider_name)."""
    # DeepSeek primary
    try:
        ds_key = _load_api_key(DEEPSEEK["key_env"])
        result = _call_llm(system_prompt, DEEPSEEK, ds_key)
        if result:
            return result, "deepseek"
        logger.info("DeepSeek returned empty — trying NVIDIA fallback...")
    except RuntimeError as e:
        logger.warning("DeepSeek key not found: %s — trying NVIDIA...", e)

    # NVIDIA fallback
    try:
        nv_key = _load_api_key(NVIDIA["key_env"])
        result = _call_llm(system_prompt, NVIDIA, nv_key)
        if result:
            return result, "nvidia"
        logger.warning("NVIDIA also returned empty.")
    except RuntimeError as e:
        logger.warning("NVIDIA key not found: %s", e)

    return None, "failed"


# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------

def load_ledger() -> dict[str, dict]:
    """Load T2 ledger. Returns {tool_id: record}."""
    ledger = {}
    if LEDGER_PATH.exists():
        for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                ledger[rec["tool_id"]] = rec
            except (json.JSONDecodeError, KeyError):
                pass
    return ledger


def append_ledger(tool_id: str, status: str, category: str,
                  score: float = 0.0, verdict: str = "",
                  provider: str = "", fields: list[str] | None = None,
                  reason: str = ""):
    """Append one record to the T2 ledger."""
    record = {
        "tool_id": tool_id,
        "status": status,
        "category": category,
        "score": round(score, 4),
        "verdict": verdict,
        "provider": provider,
        "fields": fields or [],
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Checkpoint
# ---------------------------------------------------------------------------

def save_checkpoint(run_dir: Path, state: dict):
    cp = run_dir / "checkpoint.json"
    cp.write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_checkpoint(run_dir: Path) -> dict:
    cp = run_dir / "checkpoint.json"
    if cp.exists():
        return json.loads(cp.read_text(encoding="utf-8"))
    return {"processed": [], "forged": 0, "scrapped": 0, "total": 0}


# ---------------------------------------------------------------------------
# Category prioritization
# ---------------------------------------------------------------------------

def prioritize_categories() -> list[str]:
    """Return T2 categories ordered by need (least-covered first)."""
    # Count passing tools per category from verdicts
    cat_passes: Counter[str] = Counter()
    for vf in VERDICTS_DIR.glob("t2_*_verdict.json"):
        try:
            v = json.loads(vf.read_text(encoding="utf-8"))
            if v.get("verdict") == "PASS":
                for cat, result in v.get("per_category", {}).items():
                    if result.get("pass"):
                        cat_passes[cat] += 1
        except Exception:
            pass

    # Sort: categories with fewest passes first, then alphabetical
    categories = list(T2_CATEGORIES.keys())
    categories.sort(key=lambda c: (cat_passes.get(c, 0), c))
    return categories


# ---------------------------------------------------------------------------
# Nous T2 integration
# ---------------------------------------------------------------------------

def load_nous_suggestions() -> list[dict]:
    """Load Nous T2 triples for enrichment context."""
    suggestions = []
    if not NOUS_RUNS.exists():
        return suggestions
    for run_dir in sorted(NOUS_RUNS.iterdir()):
        jsonl = run_dir / "responses.jsonl"
        if not jsonl.exists():
            continue
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                suggestions.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return suggestions


# ---------------------------------------------------------------------------
# Tool ID generation
# ---------------------------------------------------------------------------

def _next_tool_id(category: str) -> str:
    """Generate next sequential tool ID for a category."""
    existing = list(CANDIDATES_DIR.glob(f"t2_{category}_*.py"))
    # Also check forge and scrap dirs
    existing += list(FORGE_DIR.glob(f"t2_{category}_*.py"))
    existing += list(SCRAP_DIR.glob(f"t2_{category}_*.py"))

    max_num = -1
    for p in existing:
        stem = p.stem
        # Strip _gem, _FAILED suffixes
        parts = stem.replace("_gem", "").replace("_FAILED", "").split("_")
        try:
            num = int(parts[-1])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            pass

    return f"t2_{category}_{max_num + 1:03d}"


# ---------------------------------------------------------------------------
# Forge one tool
# ---------------------------------------------------------------------------

def forge_one(
    category: str,
    rng: random.Random,
    run_dir: Path,
    delay: float = 1.0,
) -> dict:
    """Generate, validate, and evaluate one T2 tool.

    Returns dict with status, tool_id, score, verdict, provider, reason.
    """
    tool_id = _next_tool_id(category)
    logger.info("Forging %s (category: %s)...", tool_id, category)

    # 1. Build prompt
    try:
        prompt, fields = generate_tool_prompt(2, category, rng)
    except Exception as e:
        logger.error("Prompt generation failed: %s", e)
        return {"status": "scrap", "tool_id": tool_id, "reason": f"prompt_error:{e}",
                "score": 0, "category": category, "provider": "", "fields": []}

    # 2. Call API with fallback
    raw, provider_used = call_with_fallback(prompt)
    if raw is None:
        append_ledger(tool_id, "scrap", category, reason="api_failed", provider="failed")
        return {"status": "scrap", "tool_id": tool_id, "reason": "api_failed",
                "score": 0, "category": category, "provider": "failed", "fields": fields}

    logger.info("  Got response from %s (%d chars)", provider_used, len(raw))

    # 3. Extract code
    code = _extract_python(raw)
    if "class ReasoningTool" not in code:
        reason = "no_reasoning_tool_class"
        logger.warning("  %s: %s", tool_id, reason)
        # Save failed response for debugging
        debug_path = SCRAP_DIR / f"{tool_id}_FAILED.txt"
        debug_path.write_text(raw, encoding="utf-8")
        append_ledger(tool_id, "scrap", category, reason=reason, provider=provider_used, fields=fields)
        return {"status": "scrap", "tool_id": tool_id, "reason": reason,
                "score": 0, "category": category, "provider": provider_used, "fields": fields}

    # 4. Save candidate
    tool_path = CANDIDATES_DIR / f"{tool_id}.py"
    tool_path.write_text(code, encoding="utf-8")

    # Save metadata
    meta_path = CANDIDATES_DIR / f"{tool_id}_meta.json"
    meta_path.write_text(json.dumps({
        "tool_id": tool_id,
        "tier": 2,
        "category": category,
        "science_fields": fields,
        "provider": provider_used,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2), encoding="utf-8")

    logger.info("  Saved candidate: %s", tool_path.name)

    # 5. Law checks
    ban_violations = check_banned_patterns(str(tool_path))
    if ban_violations:
        reason = f"law2_banned:{ban_violations[0][:80]}"
        logger.warning("  %s: %s", tool_id, reason)
        shutil.copy2(tool_path, SCRAP_DIR / f"{tool_id}.py")
        append_ledger(tool_id, "scrap", category, reason=reason,
                      provider=provider_used, fields=fields)
        return {"status": "scrap", "tool_id": tool_id, "reason": reason,
                "score": 0, "category": category, "provider": provider_used, "fields": fields}

    comp_issues = check_composition_requirements(str(tool_path), tier=2)
    if comp_issues:
        reason = f"law2_composition:{comp_issues[0][:80]}"
        logger.warning("  %s: %s", tool_id, reason)
        shutil.copy2(tool_path, SCRAP_DIR / f"{tool_id}.py")
        append_ledger(tool_id, "scrap", category, reason=reason,
                      provider=provider_used, fields=fields)
        return {"status": "scrap", "tool_id": tool_id, "reason": reason,
                "score": 0, "category": category, "provider": provider_used, "fields": fields}

    logger.info("  Passed law checks. Evaluating...")

    # 6. Evaluate via tester
    try:
        existing_paths = get_existing_tool_paths(2)
        verdict_data = tester_evaluate(str(tool_path), tier=2,
                                       existing_tool_paths=existing_paths)
    except Exception as e:
        reason = f"eval_error:{e}"
        logger.error("  Evaluation crashed: %s", e)
        shutil.copy2(tool_path, SCRAP_DIR / f"{tool_id}.py")
        append_ledger(tool_id, "scrap", category, reason=reason,
                      provider=provider_used, fields=fields)
        return {"status": "scrap", "tool_id": tool_id, "reason": reason,
                "score": 0, "category": category, "provider": provider_used, "fields": fields}

    score = verdict_data.get("overall_score", 0)
    verdict = verdict_data.get("verdict", "UNKNOWN")

    # 7. Handle result
    if verdict == "PASS":
        dest = FORGE_DIR / f"{tool_id}.py"
        shutil.copy2(tool_path, dest)
        logger.info(
            "  FORGED %s — score=%.1f%%, verdict=%s, provider=%s",
            tool_id, score * 100, verdict, provider_used,
        )
        append_ledger(tool_id, "forged", category, score=score, verdict=verdict,
                      provider=provider_used, fields=fields)
        return {"status": "forged", "tool_id": tool_id, "score": score,
                "verdict": verdict, "category": category,
                "provider": provider_used, "fields": fields}
    else:
        shutil.copy2(tool_path, SCRAP_DIR / f"{tool_id}.py")
        logger.info(
            "  SCRAP %s — score=%.1f%%, verdict=%s, provider=%s",
            tool_id, score * 100, verdict, provider_used,
        )
        append_ledger(tool_id, "scrap", category, score=score, verdict=verdict,
                      provider=provider_used, fields=fields, reason=verdict)
        return {"status": "scrap", "tool_id": tool_id, "score": score,
                "verdict": verdict, "category": category,
                "provider": provider_used, "fields": fields}


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

def forge_batch(
    categories: list[str],
    run_dir: Path,
    batch_size: int,
    delay: float,
    rng: random.Random,
) -> tuple[int, int]:
    """Forge a batch of tools across prioritized categories.

    Returns (forged_count, scrapped_count).
    """
    forged = 0
    scrapped = 0
    state = load_checkpoint(run_dir)
    processed = set(state.get("processed", []))

    for i in range(batch_size):
        if _shutdown[0]:
            break

        # Round-robin through prioritized categories
        category = categories[i % len(categories)]

        result = forge_one(category, rng, run_dir, delay)

        tool_id = result.get("tool_id", f"unknown_{i}")
        processed.add(tool_id)

        if result["status"] == "forged":
            forged += 1
        else:
            scrapped += 1

        # Checkpoint every 5
        total = state.get("total", 0) + forged + scrapped
        if (forged + scrapped) % 5 == 0:
            save_checkpoint(run_dir, {
                "processed": sorted(processed),
                "forged": state.get("forged", 0) + forged,
                "scrapped": state.get("scrapped", 0) + scrapped,
                "total": total,
            })

        # Rate limit
        if i < batch_size - 1 and not _shutdown[0]:
            time.sleep(delay)

    # Final checkpoint
    save_checkpoint(run_dir, {
        "processed": sorted(processed),
        "forged": state.get("forged", 0) + forged,
        "scrapped": state.get("scrapped", 0) + scrapped,
        "total": state.get("total", 0) + forged + scrapped,
    })

    return forged, scrapped


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Tier 2 Hephaestus — Autonomous forge loop",
    )
    parser.add_argument("--poll-interval", type=float, default=300,
                        help="Seconds between forge cycles (default: 300)")
    parser.add_argument("--batch-size", type=int, default=12,
                        help="Tools to forge per cycle (default: 12, one per category)")
    parser.add_argument("--delay", type=float, default=2.0,
                        help="Seconds between API calls (default: 2.0)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed (default: time-based)")
    parser.add_argument("--runonce", action="store_true",
                        help="Run one batch and exit")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from latest run checkpoint")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else int(time.time())
    rng = random.Random(seed)

    # Set up run directory
    if args.resume:
        # Find latest run
        runs = sorted(RUNS_DIR.iterdir()) if RUNS_DIR.exists() else []
        runs = [r for r in runs if r.is_dir() and (r / "checkpoint.json").exists()]
        if runs:
            run_dir = runs[-1]
            logger.info("Resuming from %s", run_dir.name)
        else:
            logger.warning("No runs to resume from — starting fresh")
            run_dir = RUNS_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
            run_dir.mkdir(parents=True, exist_ok=True)
    else:
        run_dir = RUNS_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir.mkdir(parents=True, exist_ok=True)

    # Save run metadata
    meta = {
        "seed": seed,
        "batch_size": args.batch_size,
        "poll_interval": args.poll_interval,
        "delay": args.delay,
        "started": datetime.now(timezone.utc).isoformat(),
    }
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    logger.info("=" * 60)
    logger.info("  Tier 2 Hephaestus — The Forge")
    logger.info("=" * 60)
    logger.info("  Run dir: %s", run_dir)
    logger.info("  Batch size: %d", args.batch_size)
    logger.info("  Poll interval: %.0fs", args.poll_interval)
    logger.info("  API delay: %.1fs", args.delay)
    logger.info("  Seed: %d", seed)
    logger.info("  Mode: %s", "runonce" if args.runonce else "continuous")
    logger.info("  API priority: DeepSeek → NVIDIA fallback")
    logger.info("=" * 60)

    cycle = 0
    total_forged = 0
    total_scrapped = 0

    while not _shutdown[0]:
        cycle += 1
        logger.info("\n--- Cycle %d ---", cycle)

        # Prioritize categories by coverage gaps
        categories = prioritize_categories()
        logger.info("Category priority: %s", ", ".join(categories[:5]) + "...")

        # Load ledger for stats
        ledger = load_ledger()
        forged_count = sum(1 for v in ledger.values() if v["status"] == "forged")
        logger.info("Ledger: %d total, %d forged", len(ledger), forged_count)

        # Forge batch
        forged, scrapped = forge_batch(
            categories, run_dir, args.batch_size, args.delay, rng,
        )

        total_forged += forged
        total_scrapped += scrapped
        logger.info(
            "Cycle %d complete: %d forged, %d scrapped (session: %d/%d)",
            cycle, forged, scrapped, total_forged, total_scrapped,
        )

        if args.runonce:
            break

        # Sleep with interruptible 5s chunks
        logger.info("Sleeping %.0fs until next cycle...", args.poll_interval)
        slept = 0.0
        while slept < args.poll_interval and not _shutdown[0]:
            chunk = min(5.0, args.poll_interval - slept)
            time.sleep(chunk)
            slept += chunk

    logger.info("\n" + "=" * 60)
    logger.info("  Hephaestus T2 shutdown.")
    logger.info("  Session totals: %d forged, %d scrapped", total_forged, total_scrapped)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
