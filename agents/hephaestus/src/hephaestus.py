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

# Agora telemetry — optional. Hephaestus runs without it if unavailable.
try:
    from agora.client import AgoraClient
    from agora.protocol import MessageType
    HAS_AGORA = True
except Exception:
    HAS_AGORA = False
    AgoraClient = None
    MessageType = None

# Structured logging
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from shared.structured_log import get_logger as _get_slog
    _slog = _get_slog("hephaestus", log_dir=Path(__file__).resolve().parent.parent / "logs")
except ImportError:
    _slog = None

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
STATUS_PATH = HEPHAESTUS_ROOT / "STATUS.json"

# Auto-load agents/hephaestus/.env if present. Existing env vars take precedence.
_HEPH_ENV = HEPHAESTUS_ROOT / ".env"
if _HEPH_ENV.exists():
    try:
        for _line in _HEPH_ENV.read_text(encoding="utf-8").splitlines():
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
    except Exception:
        pass

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
# API — NVIDIA (primary)
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "qwen/qwen3.5-397b-a17b"
API_BASE = "https://integrate.api.nvidia.com/v1"

# ---------------------------------------------------------------------------
# API — Augment / auggie-sdk (fallback when NVIDIA times out)
# ---------------------------------------------------------------------------
AGGIE_DEFAULT_MODEL = "sonnet4.5"


def make_client() -> OpenAI:
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        logger.error("NVIDIA_API_KEY not set")
        sys.exit(1)
    return OpenAI(base_url=API_BASE, api_key=api_key, timeout=120.0)


def make_aggie_client(model: str = AGGIE_DEFAULT_MODEL):
    """Create an auggie-sdk Auggie instance for use as NVIDIA API fallback.

    On Windows the CLI ships as auggie.cmd — we resolve that explicitly so
    Python's subprocess can find it without a shell.

    Returns an Auggie instance (caller must call .close() when done).
    Raises ImportError if auggie_sdk is not installed.
    """
    import shutil
    import platform
    from auggie_sdk import Auggie  # type: ignore[import]

    cli_path: str | None = None
    if platform.system() == "Windows":
        # Prefer the .cmd shim; fall back to bare 'auggie' (may work via PATH)
        cli_path = shutil.which("auggie.cmd") or shutil.which("auggie")

    logger.info("Creating Augment API client (model=%s, cli=%s)", model, cli_path)
    return Auggie(model=model, timeout=180, cli_path=cli_path)


def call_aggie_api(aggie_client, prompt: str) -> str | None:
    """Call the Augment API via auggie-sdk.

    Used as NVIDIA fallback (--use-aggie-api) or primary forge engine (--force-aggie).
    Returns the raw text response, or None on failure.
    """
    try:
        logger.info("Calling Augment API (auggie-sdk)...")
        response = aggie_client.run(prompt, timeout=180, max_retries=1)
        logger.debug("Augment raw response type=%s repr=%r", type(response).__name__, response)
        text = str(response) if response is not None else None
        if text:
            logger.info("Augment API succeeded (%d chars)", len(text))
            if len(text) < 300:
                logger.warning("Augment response suspiciously short: %r", text)
            return text
        logger.warning("Augment API returned empty response")
        return None
    except Exception as e:
        logger.error("Augment API call failed: %s", e)
        return None


def call_api(client: OpenAI, prompt: str, model: str,
             max_retries: int = 5, backoff_base: float = 2.0) -> str | None:
    """Call API with exponential backoff. Returns None only on non-retryable errors."""
    import random
    
    def is_retryable(err_str: str) -> bool:
        """Determine if an error should trigger retry vs immediate failure."""
        err_lower = err_str.lower()
        # Retryable: rate limits, server errors, timeouts, connection issues
        if any(x in err_str for x in ["429", "500", "502", "503"]):
            return True
        if any(x in err_lower for x in ["rate", "timeout", "timed out", "connection", "temporarily unavailable"]):
            return True
        # Non-retryable: auth errors, bad requests, model refused
        if any(x in err_lower for x in ["unauthorized", "authentication", "forbidden", "invalid request", "model", "refused", "content policy"]):
            return False
        # Default: retry (better to retry once than lose gold)
        return True
    
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
            
            if not is_retryable(err):
                logger.error("Non-retryable API error: %s", err)
                return None
            
            if attempt < max_retries - 1:
                # Exponential backoff with jitter: base^attempt + random jitter
                wait = backoff_base ** attempt
                jitter = random.uniform(0, wait * 0.1)  # 0-10% jitter
                total_wait = wait + jitter
                logger.warning("API error (retryable), backoff %.2fs (attempt %d/%d): %s",
                             total_wait, attempt + 1, max_retries, err)
                time.sleep(total_wait)
            else:
                logger.error("API error after %d retries (last: %s)", max_retries, err)
    
    return None


# ---------------------------------------------------------------------------
# Import injection — fix common LLM code-gen omissions
# ---------------------------------------------------------------------------

# Map of bare names to the import line that provides them.
# Only covers stdlib/typing names that are safe to inject.
_IMPORT_FIXES: dict[str, str] = {
    "List": "from typing import List",
    "Dict": "from typing import Dict",
    "Tuple": "from typing import Tuple",
    "Set": "from typing import Set",
    "Optional": "from typing import Optional",
    "Union": "from typing import Union",
    "Any": "from typing import Any",
    "Callable": "from typing import Callable",
    "Sequence": "from typing import Sequence",
    "defaultdict": "from collections import defaultdict",
    "Counter": "from collections import Counter",
    "deque": "from collections import deque",
    "dataclass": "from dataclasses import dataclass",
    "field": "from dataclasses import field",
    "ABC": "from abc import ABC",
    "abstractmethod": "from abc import abstractmethod",
}


def _inject_missing_imports(code: str) -> str:
    """Scan generated code for bare names used without import and prepend them.

    Only injects safe stdlib/typing imports. If the code already imports the
    name (directly or via wildcard), it is left alone.  Consolidates multiple
    names from the same module into a single import line.

    Also injects 'import numpy as np' if 'np.' is used without an existing
    numpy import, and similar for other allowed third-party libraries.
    """
    import re

    # --- Aliased third-party + stdlib module imports ---
    _ALIAS_FIXES = [
        (r'\bnp\.', "import numpy as np", "numpy"),
        (r'\bnx\.', "import networkx as nx", "networkx"),
        (r'\bscipy\.', "import scipy", "scipy"),
        (r'\bsympy\.', "import sympy", "sympy"),
        # Stdlib modules commonly used bare
        (r'\bre\.', "import re", "re"),
        (r'\bmath\.', "import math", "math"),
        (r'\bjson\.', "import json", "json"),
        (r'\bitertools\.', "import itertools", "itertools"),
        (r'\bfunctools\.', "import functools", "functools"),
        (r'\bcollections\.', "import collections", "collections"),
        (r'\bzlib\.', "import zlib", "zlib"),
        (r'\bstring\.', "import string", "string"),
        (r'\brandom\.', "import random", "random"),
        (r'\bcopy\.', "import copy", "copy"),
        (r'\boperator\.', "import operator", "operator"),
    ]
    alias_lines = []
    for pattern, import_line, module in _ALIAS_FIXES:
        if re.search(pattern, code) and import_line not in code and f"import {module}" not in code:
            alias_lines.append(import_line)

    # --- Stdlib/typing name imports ---
    by_module: dict[str, list[str]] = {}  # module -> [names]
    for name, import_line in _IMPORT_FIXES.items():
        if import_line in code:
            continue
        module = import_line.split("from ")[-1].split(" import")[0]
        if f"import {module}" in code and f"from {module}" not in code:
            continue
        if re.search(rf'\b{name}\b', code):
            by_module.setdefault(module, []).append(name)

    stdlib_lines = []
    for module in sorted(by_module):
        names = sorted(by_module[module])
        stdlib_lines.append(f"from {module} import {', '.join(names)}")

    all_injections = alias_lines + stdlib_lines
    if not all_injections:
        return code

    return "\n".join(all_injections) + "\n\n" + code


def _sanitize_unicode(code: str) -> str:
    """Replace non-ASCII characters that crash Windows cp1252 encoding.

    LLMs frequently emit Unicode math symbols (≥, ≈, →, ∈, etc.) in
    strings and comments. These crash on Windows when written to files
    or printed to console with cp1252 encoding.
    """
    replacements = {
        "\u2248": "~=",   # ≈
        "\u2265": ">=",   # ≥
        "\u2264": "<=",   # ≤
        "\u2260": "!=",   # ≠
        "\u2192": "->",   # →
        "\u2190": "<-",   # ←
        "\u2208": "in",   # ∈
        "\u2209": "not in",  # ∉
        "\u221e": "inf",  # ∞
        "\u00d7": "*",    # ×
        "\u00f7": "/",    # ÷
        "\u2212": "-",    # −
        "\u03b1": "alpha",  # α
        "\u03b2": "beta",   # β
        "\u03b3": "gamma",  # γ
        "\u03b4": "delta",  # δ
        "\u03b5": "epsilon",  # ε
        "\u03bb": "lambda_",  # λ
        "\u03c0": "pi",   # π
        "\u03c3": "sigma",  # σ
        "\u03c4": "tau",   # τ
        "\u2026": "...",  # …
        "\u201c": '"',    # "
        "\u201d": '"',    # "
        "\u2018": "'",    # '
        "\u2019": "'",    # '
    }
    for char, replacement in replacements.items():
        code = code.replace(char, replacement)
    # Catch any remaining non-ASCII in string literals/comments
    # (leave actual Python identifiers alone)
    return code


def _fix_common_errors(code: str) -> str:
    """Fix common LLM code-gen errors that cause gate failures.

    Applied after import injection and Unicode sanitization. Handles:
    1. Missing confidence() method — inject a default stub
    2. Confidence returning None/bad type — append a safe wrapper
    3. Evaluate returning None — append a safe wrapper
    """
    import re as _re
    import ast

    if "class ReasoningTool" not in code:
        return code

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code  # Can't fix what won't parse

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ReasoningTool":
            method_names = [
                n.name for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]

            # 1. Missing confidence() — inject a default that delegates to evaluate()
            if "confidence" not in method_names and "evaluate" in method_names:
                stub = '''
    def confidence(self, prompt: str, answer: str) -> float:
        """Default confidence via evaluate()."""
        try:
            results = self.evaluate(prompt, [answer])
            if results:
                return max(0.0, min(1.0, float(results[0].get("score", 0.5))))
        except Exception:
            pass
        return 0.5
'''
                # Find end of class body and insert
                lines = code.split('\n')
                class_end = len(lines)
                indent_level = None
                in_class = False
                for i, line in enumerate(lines):
                    if 'class ReasoningTool' in line:
                        in_class = True
                        indent_level = len(line) - len(line.lstrip())
                        continue
                    if in_class and indent_level is not None and line.strip():
                        if not line[0:1].isspace() and i > 0:
                            class_end = i
                            break
                lines.insert(class_end, stub)
                code = '\n'.join(lines)

            # 2. Wrap confidence() to guarantee float return in [0,1]
            # Appended after the class — catches None returns, exceptions, out-of-range
            if "confidence" in method_names or "confidence" not in method_names:
                wrapper = '''

# --- Auto-fix: ensure confidence() returns float in [0, 1] ---
_orig_confidence = ReasoningTool.confidence
def _safe_confidence(self, prompt, answer):
    try:
        result = _orig_confidence(self, prompt, answer)
        if result is None:
            return 0.5
        return max(0.0, min(1.0, float(result)))
    except (TypeError, ValueError):
        return 0.5
ReasoningTool.confidence = _safe_confidence
'''
                if "_safe_confidence" not in code:
                    code = code.rstrip() + "\n" + wrapper

            # 3. Wrap evaluate() to guarantee list[dict] return
            eval_wrapper = '''

# --- Auto-fix: ensure evaluate() returns list[dict] ---
_orig_evaluate = ReasoningTool.evaluate
def _safe_evaluate(self, prompt, candidates):
    try:
        result = _orig_evaluate(self, prompt, candidates)
        if result is None:
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        if not isinstance(result, list):
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        return result
    except Exception:
        return [{"candidate": c, "score": 0.5, "reasoning": "error"} for c in candidates]
ReasoningTool.evaluate = _safe_evaluate
'''
            if "_safe_evaluate" not in code:
                code = code.rstrip() + "\n" + eval_wrapper
            break

    return code


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
            if not line:
                continue
            try:
                entry = json.loads(line)
                ledger[entry["key"]] = entry
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Skipping corrupt ledger line: %s", e)
    return ledger


def append_ledger(key: str, status: str, concept_names: list[str],
                  reason: str = "", accuracy: float = 0.0,
                  calibration: float = 0.0,
                  margin_accuracy: float = 0.0,
                  margin_calibration: float = 0.0,
                  frame: str = "A", model: str = "", **kwargs):
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
        "frame": frame,
        "model": model,
        "timestamp": datetime.now().isoformat(),
    }
    try:
        with open(LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError as e:
        logger.warning("Failed to write ledger entry for %s: %s", key, e)


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
        except Exception as e:
            logger.debug("Failed to load enrichment for %s: %s", key, e)
            return None
    return None


def _compute_novelty(code: str) -> dict:
    """Compute source-code NCD novelty against the existing forge library.

    Returns dict with:
        min_ncd: distance to nearest neighbor (higher = more novel)
        mean_ncd: average distance to all existing tools
        nearest: filename of most similar existing tool
        library_size: how many tools compared against
    """
    import zlib

    existing = []
    for py_file in FORGE_DIR.glob("*.py"):
        try:
            existing.append((py_file.name, py_file.read_bytes()))
        except Exception:
            continue

    if not existing:
        return {"min_ncd": 1.0, "mean_ncd": 1.0, "nearest": None, "library_size": 0}

    code_bytes = code.encode("utf-8")
    c_new = len(zlib.compress(code_bytes))

    ncds = []
    nearest_name = None
    min_ncd = 1.0

    for name, existing_bytes in existing:
        c_old = len(zlib.compress(existing_bytes))
        c_both = len(zlib.compress(code_bytes + existing_bytes))
        ncd = (c_both - min(c_new, c_old)) / max(c_new, c_old)
        ncds.append(ncd)
        if ncd < min_ncd:
            min_ncd = ncd
            nearest_name = name

    return {
        "min_ncd": round(min_ncd, 4),
        "mean_ncd": round(sum(ncds) / len(ncds), 4) if ncds else 1.0,
        "nearest": nearest_name,
        "library_size": len(existing),
    }


def safe_filename(names: list[str]) -> str:
    """Turn concept names into a filesystem-safe filename."""
    joined = "_x_".join(n.replace(" ", "_") for n in names)
    # Truncate if too long
    if len(joined) > 120:
        joined = joined[:120]
    return joined.lower()


def save_forge(code: str, entry: dict, test_results: dict, run_dir: Path,
               frame: str = "?"):
    """Save a successfully forged tool."""
    fname = safe_filename(entry["concept_names"])
    forge_path = FORGE_DIR / f"{fname}.py"
    forge_path.write_text(code, encoding="utf-8")

    # Compute novelty against existing library (before adding this tool)
    novelty = _compute_novelty(code)

    # Sidecar with metadata
    meta = {
        "concept_names": entry["concept_names"],
        "concept_fields": entry.get("concept_fields", []),
        "nous_composite_score": entry.get("score", {}).get("composite_score"),
        "test_accuracy": test_results["accuracy"],
        "test_calibration": test_results["calibration"],
        "frame": frame,
        "novelty_min_ncd": novelty["min_ncd"],
        "novelty_mean_ncd": novelty["mean_ncd"],
        "novelty_nearest": novelty["nearest"],
        "novelty_library_size": novelty["library_size"],
        "forged_at": datetime.now().isoformat(),
    }
    meta_path = FORGE_DIR / f"{fname}.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # Also log in run dir
    log_path = run_dir / "forged.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(meta) + "\n")

    logger.info("FORGED [%s]: %s (acc=%.0f%% cal=%.0f%% novelty=%.3f nearest=%s)",
                meta.get("frame", "?"),
                " + ".join(entry["concept_names"]),
                test_results["accuracy"] * 100,
                test_results["calibration"] * 100,
                novelty["min_ncd"],
                novelty["nearest"] or "none")
    if _slog:
        _slog.event("forge_success",
                     key=" + ".join(entry["concept_names"]),
                     accuracy=test_results["accuracy"],
                     calibration=test_results["calibration"],
                     n_categories=test_results.get("n_categories", 0))


def save_scrap(code: str | None, entry: dict, reason: str, run_dir: Path,
               frame: str = "?"):
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
        "frame": frame,
        "scrapped_at": datetime.now().isoformat(),
    }
    meta_path = SCRAP_DIR / f"{fname}.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # Also log in run dir
    log_path = run_dir / "scrapped.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(meta) + "\n")

    logger.info("SCRAP [%s]: %s — %s", meta.get("frame", "?"),
                " + ".join(entry["concept_names"]), reason)


# ---------------------------------------------------------------------------
# Rankings
# ---------------------------------------------------------------------------

def _log_frame_scoreboard(run_dir: Path):
    """Log per-frame success rates from this run's forged/scrapped JSONL files."""
    from collections import Counter

    frame_forged: Counter = Counter()
    frame_total: Counter = Counter()

    for jsonl_name, is_forge in [("forged.jsonl", True), ("scrapped.jsonl", False)]:
        path = run_dir / jsonl_name
        if not path.exists():
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                rec = json.loads(line)
                f = rec.get("frame", "?")
                frame_total[f] += 1
                if is_forge:
                    frame_forged[f] += 1
        except Exception:
            continue

    if not frame_total:
        return

    logger.info("  Frame scoreboard (this run):")
    frame_names = {
        "A": "Structural", "B": "Constructive", "C": "Dynamics",
        "D": "Judgment", "E": "Computational", "F": "Adversarial",
        "G": "Metacognitive", "H": "Primordial",
    }
    for f in sorted(frame_total.keys()):
        total = frame_total[f]
        forged = frame_forged[f]
        rate = (forged / total * 100) if total > 0 else 0
        name = frame_names.get(f, "?")
        logger.info("    Frame %s (%s): %d/%d forged (%.0f%%)", f, name, forged, total, rate)


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
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as e:
                logger.warning("Skipping corrupt line in %s: %s", path, e)
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
    except Exception as e:
        logger.debug("Failed to load Coeus scores: %s", e)
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


def forge_one_with_retry(client: OpenAI, entry: dict, model: str,
                         run_dir: Path, max_item_retries: int = 3,
                         aggie_client=None, force_aggie: bool = False) -> dict | None:
    """Attempt to forge an item multiple times with backoff on API failures.

    This wrapper retries at the item level when API failures occur, giving the
    API time to recover before discarding the item. Permanent failures (bad code,
    validation errors) are not retried.

    aggie_client: optional Auggie instance used as fallback inside forge_one()
                  when the NVIDIA call fails.  Only set when --use-aggie-api is active.
    force_aggie: if True, skip NVIDIA API entirely and use Augment API (aggie_client must be set).
    """
    import random

    for attempt in range(max_item_retries):
        result = forge_one(client, entry, model, run_dir, aggie_client=aggie_client, force_aggie=force_aggie)

        # If successful or permanent failure, return immediately
        if not result or result["status"] == "forged":
            return result

        # Only retry on API failures
        reason = result.get("reason", "")
        if reason != "api_call_failed":
            return result  # Permanent failure (validation, code extract, test) - don't retry

        # API failed - wait and retry
        if attempt < max_item_retries - 1:
            wait = 2 ** attempt + random.uniform(0, 1)  # 1-2s, 2-3s, 4-5s
            logger.warning("Item forge API failed, retrying in %.1fs (attempt %d/%d)",
                         wait, attempt + 1, max_item_retries)
            time.sleep(wait)
        else:
            logger.warning("Item forge exhausted retries after API failures")

    return result


def forge_one(client: OpenAI, entry: dict, model: str,
              run_dir: Path, aggie_client=None, force_aggie: bool = False) -> dict | None:
    """Process a single Nous result through the full forge pipeline.

    aggie_client: optional Auggie instance.  When the primary NVIDIA call_api()
                  fails (returns None) and aggie_client is provided, the same
                  prompt is sent to the Augment API as a one-shot fallback.
                  If the fallback also fails the item is scrapped as normal.
    force_aggie: if True, skip NVIDIA API entirely and call Augment API (aggie_client must be set).
    """
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

    # 1. Build prompt and call API (frame selected by prompts.py weighted rotation)
    from prompts import select_frame
    frame = select_frame()
    prompt = build_code_gen_prompt(names, response_text, ratings, enrichment=enrichment, frame=frame)

    # 1a. Use Augment API directly if --force-aggie
    if force_aggie and aggie_client is not None:
        logger.info("  Using Augment API (force-aggie mode)")
        raw_response = call_aggie_api(aggie_client, prompt)
    else:
        # Normal path: try NVIDIA first
        raw_response = call_api(client, prompt, model)
        # 1b. Augment API fallback — only when NVIDIA failed AND flag is active
        if raw_response is None and aggie_client is not None:
            raw_response = call_aggie_api(aggie_client, prompt)

    if raw_response is None:
        save_scrap(None, entry, "api_call_failed", run_dir, frame=frame)
        return {"status": "scrap", "reason": "api_call_failed", "frame": frame}

    # 2. Extract code
    code, extract_status = extract_code(raw_response)
    if code is None:
        save_scrap(None, entry, extract_status, run_dir, frame=frame)
        return {"status": "scrap", "reason": extract_status, "frame": frame}

    # 2b. Sanitize Unicode (LLMs emit math symbols that crash Windows cp1252)
    code = _sanitize_unicode(code)

    # 2c. Inject missing stdlib imports (LLMs frequently forget these)
    code = _inject_missing_imports(code)

    # 2d. Fix common LLM errors (missing confidence method, etc.)
    code = _fix_common_errors(code)

    # 3. Validate
    valid, reason = validate(code)
    if not valid:
        save_scrap(code, entry, f"validation:{reason}", run_dir, frame=frame)
        return {"status": "scrap", "reason": f"validation:{reason}", "frame": frame}

    # 4. Run trap battery
    try:
        tool = load_tool_from_code(code)
        test_results = run_trap_battery(tool)
    except Exception as e:
        save_scrap(code, entry, f"test_harness_error: {e}", run_dir, frame=frame)
        return {"status": "scrap", "reason": f"test_harness_error: {e}", "frame": frame}

    if not test_results["passed"]:
        # Novelty gate: admit tools that are structurally novel even if
        # they don't beat NCD on accuracy. Diverse substrate > convergent accuracy.
        novelty = _compute_novelty(code)
        if novelty["min_ncd"] > 0.85 and test_results["accuracy"] >= 0.20:
            # Novel enough to be valuable — forge it with novelty tag
            logger.info("  NOVELTY GATE: acc=%.0f%% below NCD but novelty=%.3f — forging as novel",
                        test_results["accuracy"] * 100, novelty["min_ncd"])
            test_results["passed"] = True  # Override for save_forge
            test_results["admitted_via"] = "novelty_gate"
            save_forge(code, entry, test_results, run_dir, frame=frame)
            return {
                "status": "forged",
                "accuracy": test_results["accuracy"],
                "calibration": test_results["calibration"],
                "margin_accuracy": test_results.get("margin_accuracy", 0),
                "margin_calibration": test_results.get("margin_calibration", 0),
                "frame": frame,
                "admitted_via": "novelty_gate",
            }

        ncd_info = ""
        if "ncd_accuracy" in test_results:
            ncd_info = (f" ncd_acc={test_results['ncd_accuracy']:.0%}"
                        f" ncd_cal={test_results['ncd_calibration']:.0%}")
        reason = (f"trap_battery_failed (acc={test_results['accuracy']:.0%} "
                  f"cal={test_results['calibration']:.0%}{ncd_info})")
        save_scrap(code, entry, reason, run_dir, frame=frame)
        return {"status": "scrap", "reason": reason, "frame": frame}

    # 5. Save to forge
    save_forge(code, entry, test_results, run_dir, frame=frame)
    return {
        "status": "forged",
        "accuracy": test_results["accuracy"],
        "calibration": test_results["calibration"],
        "margin_accuracy": test_results.get("margin_accuracy", 0),
        "margin_calibration": test_results.get("margin_calibration", 0),
        "frame": frame,
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
    except SystemExit as e:
        logger.warning("Coeus rebuild called sys.exit(%s) — caught, continuing forge", e.code)
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
    except SystemExit as e:
        logger.warning("Reports rebuild called sys.exit(%s) — caught, continuing forge", e.code)
    except Exception as e:
        logger.warning("Reports rebuild failed: %s (continuing forge)", e)


def _trigger_novelty_scoring():
    """Rescore all forge tools for novelty and complexity."""
    try:
        logger.info("Running novelty/complexity scoring on forge library...")
        import importlib
        saved_argv = sys.argv[:]
        sys.argv = ["novelty_scorer.py", "--update-ledger", "--quiet"]
        try:
            ns_mod = importlib.import_module("novelty_scorer")
            importlib.reload(ns_mod)
            ns_mod.main()
        finally:
            sys.argv = saved_argv
        logger.info("Novelty scoring complete — scores saved and ledger updated")
    except SystemExit as e:
        logger.warning("Novelty scorer called sys.exit(%s) — caught, continuing forge", e.code)
    except Exception as e:
        logger.warning("Novelty scoring failed: %s (continuing forge)", e)


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
                 total_count: int, shutdown_flag: list,
                 aggie_client=None, force_aggie: bool = False,
                 on_forge=None, on_scrap=None,
                 on_status=None) -> tuple[list, list, int]:
    """Process one batch of candidates. Returns (forged, scrapped, new_count).

    aggie_client: optional Auggie instance passed down to forge_one() as fallback.
    force_aggie: if True, skip NVIDIA API entirely and use Augment API (aggie_client must be set).
    on_forge/on_scrap: callbacks for Agora telemetry on forge/scrap events.
    on_status: callback(current_op, nous_queue_depth) for periodic STATUS emit.
    """
    forged_results = []
    scrapped_results = []
    count = 0

    for entry in filtered:
        if shutdown_flag[0]:
            break

        key = combo_key(entry)
        if key in processed:
            continue

        result = forge_one_with_retry(client, entry, args.model, run_dir,
                                      max_item_retries=3, aggie_client=aggie_client,
                                      force_aggie=force_aggie)

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
                          margin_calibration=result.get("margin_calibration", 0),
                          frame=result.get("frame", "A"),
                          model=args.model)
            if on_forge:
                on_forge(entry, result)
        elif result:
            scrapped_results.append({
                "concept_names": names,
                "nous_composite_score": entry.get("score", {}).get("composite_score"),
                "failure_reason": result.get("reason"),
            })
            append_ledger(key, "scrap", names, reason=result.get("reason", ""),
                          frame=result.get("frame", "A"),
                          model=args.model)
            if on_scrap:
                on_scrap(entry, result)

        # Checkpoint + periodic STATUS emit
        if count % 5 == 0:
            save_checkpoint(run_dir, processed)
            if on_status:
                on_status(
                    f"forging {' + '.join(entry.get('concept_names', []))}",
                    len(filtered) - count,
                )

        # Periodic Coeus rebuild
        if (args.coeus_interval > 0 and running_total % args.coeus_interval == 0
                and running_total > 0 and not shutdown_flag[0]):
            _trigger_coeus()

        # Periodic reports rebuild
        if (args.reports_interval > 0 and running_total % args.reports_interval == 0
                and running_total > 0 and not shutdown_flag[0]):
            _trigger_reports()

        # Periodic novelty scoring (same interval as reports)
        if (args.reports_interval > 0 and running_total % args.reports_interval == 0
                and running_total > 0 and not shutdown_flag[0]):
            _trigger_novelty_scoring()

        # Rate limit
        if not shutdown_flag[0]:
            time.sleep(args.delay)

    save_checkpoint(run_dir, processed)
    return forged_results, scrapped_results, count


def repair_scraps(max_items: int = 50, min_accuracy: float = 0.25):
    """Attempt to repair scrapped tools and score them for novelty.

    Targets two categories:
    1. Gate 1-3 failures (syntax/import/interface) — mechanical fixes
    2. Trap battery near-misses (acc >= min_accuracy) — novelty assessment

    Repaired tools that pass all 5 gates are moved to forge/.
    Near-misses with high novelty are logged for manual review.
    """
    logger.info("=" * 60)
    logger.info("SCRAP REPAIR PASS")
    logger.info("=" * 60)

    repaired = 0
    novel_finds = 0
    attempted = 0

    # Load existing ledger to avoid re-processing
    ledger = load_ledger()

    # Collect repair candidates
    candidates = []
    for json_file in sorted(SCRAP_DIR.glob("*.json")):
        try:
            meta = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        reason = meta.get("failure_reason", "")
        py_file = SCRAP_DIR / json_file.name.replace(".json", ".py")
        if not py_file.exists():
            continue

        # Category 1: fixable gate failures
        is_fixable = any(x in reason for x in [
            "validation:syntax", "validation:import", "validation:interface",
            "validation:runtime_error: NameError",
            "validation:runtime_error: ImportError",
        ])
        # Category 2: trap battery near-misses
        is_near_miss = "trap_battery_failed" in reason

        if is_fixable or is_near_miss:
            # Parse accuracy from near-miss reason
            acc = 0.0
            if is_near_miss:
                import re as _re
                m = _re.search(r"acc=(\d+)%", reason)
                if m:
                    acc = int(m.group(1)) / 100.0
                if acc < min_accuracy:
                    continue

            candidates.append({
                "py_file": py_file,
                "json_file": json_file,
                "meta": meta,
                "reason": reason,
                "is_fixable": is_fixable,
                "accuracy": acc,
            })

    logger.info("Found %d repair candidates (%d fixable, %d near-misses)",
                len(candidates),
                sum(1 for c in candidates if c["is_fixable"]),
                sum(1 for c in candidates if not c["is_fixable"]))

    # Sort: near-misses first (novelty targets), then fixable (cheap wins)
    candidates.sort(key=lambda c: (c["is_fixable"], -c["accuracy"]))

    for cand in candidates[:max_items]:
        attempted += 1
        code = cand["py_file"].read_text(encoding="utf-8")
        names = cand["meta"].get("concept_names", [])
        key = " + ".join(sorted(names))

        if cand["is_fixable"]:
            # Attempt mechanical repair
            code = _inject_missing_imports(code)
            valid, reason = validate(code)
            if not valid:
                logger.debug("  Repair failed for %s: %s", key, reason)
                continue

            # Try running trap battery
            try:
                tool = load_tool_from_code(code)
                test_results = run_trap_battery(tool)
            except Exception as e:
                logger.debug("  Repair runtime error for %s: %s", key, e)
                continue

            if test_results["passed"]:
                # Compute novelty and save to forge
                novelty = _compute_novelty(code)
                fname = safe_filename(names)
                forge_path = FORGE_DIR / f"{fname}.py"
                forge_path.write_text(code, encoding="utf-8")
                meta = {
                    "concept_names": names,
                    "concept_fields": cand["meta"].get("concept_fields", []),
                    "nous_composite_score": cand["meta"].get("nous_composite_score"),
                    "test_accuracy": test_results["accuracy"],
                    "test_calibration": test_results["calibration"],
                    "frame": cand["meta"].get("frame", "?"),
                    "novelty_min_ncd": novelty["min_ncd"],
                    "novelty_mean_ncd": novelty["mean_ncd"],
                    "novelty_nearest": novelty["nearest"],
                    "novelty_library_size": novelty["library_size"],
                    "repaired_from": "scrap",
                    "original_failure": cand["reason"],
                    "forged_at": datetime.now().isoformat(),
                }
                (FORGE_DIR / f"{fname}.json").write_text(
                    json.dumps(meta, indent=2), encoding="utf-8")
                logger.info("REPAIRED->FORGED: %s (acc=%.0f%% novelty=%.3f)",
                            key, test_results["accuracy"] * 100, novelty["min_ncd"])
                repaired += 1
            else:
                # Didn't pass battery but code now runs — check novelty anyway
                novelty = _compute_novelty(code)
                if novelty["min_ncd"] > 0.85:
                    logger.info("  HIGH NOVELTY NEAR-MISS: %s (acc=%.0f%% novelty=%.3f)",
                                key, test_results["accuracy"] * 100, novelty["min_ncd"])
                    novel_finds += 1

        else:
            # Near-miss: code already runs, compute novelty and forge if high
            code = _inject_missing_imports(code)
            code = _fix_common_errors(code)
            valid, vreason = validate(code)
            if not valid:
                continue
            novelty = _compute_novelty(code)
            if novelty["min_ncd"] > 0.85 and cand["accuracy"] >= 0.20:
                # Forge it via novelty gate
                fname = safe_filename(names)
                forge_path = FORGE_DIR / f"{fname}.py"
                forge_path.write_text(code, encoding="utf-8")
                meta = {
                    "concept_names": names,
                    "concept_fields": cand["meta"].get("concept_fields", []),
                    "nous_composite_score": cand["meta"].get("nous_composite_score"),
                    "test_accuracy": cand["accuracy"],
                    "test_calibration": 0.0,
                    "frame": cand["meta"].get("frame", "?"),
                    "novelty_min_ncd": novelty["min_ncd"],
                    "novelty_mean_ncd": novelty["mean_ncd"],
                    "novelty_nearest": novelty["nearest"],
                    "novelty_library_size": novelty["library_size"],
                    "admitted_via": "novelty_gate",
                    "repaired_from": "scrap",
                    "original_failure": cand["reason"],
                    "forged_at": datetime.now().isoformat(),
                }
                (FORGE_DIR / f"{fname}.json").write_text(
                    json.dumps(meta, indent=2), encoding="utf-8")
                logger.info("  NOVELTY FORGED: %s (acc=%.0f%% novelty=%.3f nearest=%s)",
                            key, cand["accuracy"] * 100,
                            novelty["min_ncd"], novelty["nearest"])
                novel_finds += 1

    logger.info("=" * 60)
    logger.info("REPAIR COMPLETE: %d attempted, %d repaired to forged, %d high-novelty finds",
                attempted, repaired, novel_finds)
    logger.info("=" * 60)


LLM_REPAIR_PROMPT = """\
The following Python code has an error that prevents it from running.
The error is: {error}

Fix ONLY the error. Do not change the algorithm, logic, or scoring strategy.
Do not add features or refactor. Minimal fix only.

If the error is a missing import, add it.
If the error is a syntax issue (unclosed bracket, bad indent, unterminated string), fix it.
If the error is a missing method, add a minimal implementation that delegates to existing methods.
If the error is a NameError, add the missing import or define the missing name.

Return the COMPLETE fixed Python code in a ```python code block.

```python
{code}
```"""


DEEP_INSPECT_PROMPT = """\
You are evaluating a Python reasoning tool for novelty of its computational strategy.
This tool scored {accuracy}% accuracy on a reasoning battery — close to but below
the {baseline}% baseline. The question is not whether it's accurate, but whether
its MECHANISM is genuinely novel and worth preserving.

The tool was generated from these concepts: {concepts}

Here is the code:

```python
{code}
```

Here is its tier profile (accuracy per reasoning tier):
{tier_profile}

Evaluate the following (be brutally honest, no flattery):

1. MECHANISM DESCRIPTION: In 2-3 sentences, what computational strategy does this
   code actually implement? Not what the docstring says — what does the code DO?

2. NOVELTY ASSESSMENT: Is this a genuinely unusual approach, or is it a standard
   pattern (regex + NCD + keyword matching) with cosmetic complexity?
   Rate: NOVEL / STANDARD / COSMETIC

3. TIER-MECHANISM MATCH: Does the code's mechanism match its strongest tier?
   (e.g., if it scores best on R3 abstraction, does the code actually do abstraction?)
   Rate: GENUINE / DECORATIVE / UNKNOWN

4. COMPOSITION VALUE: Would this tool add something unique if composed with others?
   What specific capability would it contribute that a regex-based tool cannot?
   Rate: HIGH / MODERATE / LOW

5. VERDICT: Should this near-miss be admitted to the forge library despite
   not beating the accuracy baseline?
   Answer: ADMIT / REJECT / NEEDS_LARGER_BATTERY

Respond with exactly these 5 sections."""


def inspect_near_misses(max_items: int = 20):
    """Deep inspection of near-miss scraps using tier profiling + LLM assessment.

    For each near-miss (accuracy >= 35%, failed the accuracy gate, failed the
    novelty NCD gate):
    1. Run tier profile (which tiers does it excel on?)
    2. Compute failure rarity (does it solve problems others don't?)
    3. If tier profile or rarity shows signal, send to LLM for mechanism assessment
    4. Admit tools the LLM rates as NOVEL + GENUINE + (HIGH or MODERATE)
    """
    import re as _re

    logger.info("=" * 60)
    logger.info("DEEP NEAR-MISS INSPECTION")
    logger.info("=" * 60)

    client = make_client()
    model = DEFAULT_MODEL

    # Load the expanded battery for tier profiling
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from trap_generator_extended import generate_full_battery
        battery = generate_full_battery(n_per_category=2, seed=42)
    except ImportError:
        logger.error("Extended battery unavailable, cannot run deep inspection")
        return

    from test_harness import _run_battery, _NCDBaseline, CATEGORY_TIER

    ncd_tool = _NCDBaseline()
    ncd_results = _run_battery(ncd_tool, battery)
    ncd_baseline_acc = ncd_results["accuracy"]

    # Collect existing library correct-answer sets for rarity scoring
    library_correct = []
    for py_file in FORGE_DIR.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        try:
            tool = load_tool_from_code(py_file.read_text(encoding="utf-8"))
            results = _run_battery(tool, battery)
            correct_set = set()
            for j, r in enumerate(results["trap_results"]):
                if r.get("is_correct"):
                    correct_set.add(j)
            library_correct.append(correct_set)
        except Exception:
            continue

    logger.info("Library profiled: %d tools for rarity comparison", len(library_correct))

    # Count how many library tools solve each probe
    probe_solve_count = [0] * len(battery)
    for cs in library_correct:
        for idx in cs:
            probe_solve_count[idx] += 1

    # Collect near-miss candidates from scrap
    candidates = []
    for json_file in sorted(SCRAP_DIR.glob("*.json")):
        try:
            meta = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        reason = meta.get("failure_reason", "")
        if "trap_battery_failed" not in reason:
            continue
        m = _re.search(r"acc=(\d+)%", reason)
        if not m:
            continue
        acc = int(m.group(1))
        if acc < 35:
            continue
        py_file = SCRAP_DIR / json_file.name.replace(".json", ".py")
        if not py_file.exists():
            continue
        candidates.append({
            "py_file": py_file, "meta": meta, "accuracy": acc / 100.0,
        })

    candidates.sort(key=lambda c: -c["accuracy"])
    logger.info("Found %d near-miss candidates (>=35%% accuracy)", len(candidates))

    inspected = 0
    admitted = 0

    for cand in candidates[:max_items]:
        names = cand["meta"].get("concept_names", [])
        key = " + ".join(sorted(names))

        code = cand["py_file"].read_text(encoding="utf-8")
        code = _sanitize_unicode(code)
        code = _inject_missing_imports(code)
        code = _fix_common_errors(code)

        # Validate
        valid, vreason = validate(code)
        if not valid:
            continue

        # Run tier profile
        try:
            tool = load_tool_from_code(code)
            results = _run_battery(tool, battery)
        except Exception:
            continue

        # Compute tier profile
        from collections import defaultdict
        tier_correct = defaultdict(int)
        tier_total = defaultdict(int)
        correct_set = set()
        for j, (r, trap) in enumerate(zip(results["trap_results"], battery)):
            tier = CATEGORY_TIER.get(trap.get("category", ""))
            if tier:
                tier_total[tier] += 1
                if r.get("is_correct"):
                    tier_correct[tier] += 1
                    correct_set.add(j)

        tier_profile = {}
        for tier in sorted(tier_total.keys()):
            n = tier_total[tier]
            tier_profile[tier] = round(tier_correct[tier] / n, 2) if n > 0 else 0.0

        # Compute rarity score
        if correct_set:
            rarities = [1.0 / max(probe_solve_count[idx], 1) for idx in correct_set]
            rarity = sum(rarities) / len(rarities)
        else:
            rarity = 0.0

        # Check for signal: excels on underrepresented tier OR solves rare problems
        best_tier = max(tier_profile.items(), key=lambda x: x[1]) if tier_profile else ("?", 0)
        has_signal = (
            (best_tier[0] in ("R4", "R5") and best_tier[1] >= 0.35)  # Strong on hard tiers
            or rarity > 0.015  # Solves rare problems
            or (best_tier[1] >= 0.50)  # Very strong on any tier
        )

        if not has_signal:
            continue

        inspected += 1
        logger.info("[%d] Inspecting: %s (acc=%.0f%%, best=%s=%.0f%%, rarity=%.4f)",
                    inspected, key, cand["accuracy"] * 100,
                    best_tier[0], best_tier[1] * 100, rarity)

        # Send to LLM for mechanism assessment
        tier_str = ", ".join(f"{t}={v:.0%}" for t, v in sorted(tier_profile.items()))
        prompt = DEEP_INSPECT_PROMPT.format(
            accuracy=f"{cand['accuracy']*100:.0f}",
            baseline=f"{ncd_baseline_acc*100:.0f}",
            concepts=", ".join(names),
            code=code[:3000],  # Truncate for API limits
            tier_profile=tier_str,
        )

        response = call_api(client, prompt, model)
        if response is None:
            logger.warning("  API failed, skipping")
            continue

        # Parse verdict — trust the LLM's ADMIT/REJECT and extract ratings
        response_lower = response.lower()

        # Extract ratings from each section
        def _extract_rating(section_name, positive_words, negative_words):
            if section_name not in response_lower:
                return "unknown"
            chunk = response_lower.split(section_name)[1][:200]
            for w in positive_words:
                if w in chunk:
                    return w
            for w in negative_words:
                if w in chunk:
                    return w
            return "unknown"

        novelty = _extract_rating("novelty assessment",
                                  ["novel"], ["standard", "cosmetic"])
        genuineness = _extract_rating("tier-mechanism match",
                                      ["genuine"], ["decorative", "unknown"])
        composition = _extract_rating("composition value",
                                      ["high", "moderate"], ["low"])

        # Verdict: ADMIT if LLM says admit, OR if novel+genuine, OR if high composition
        verdict_section = response_lower.split("verdict")[1][:200] if "verdict" in response_lower else ""
        llm_admits = "admit" in verdict_section and "reject" not in verdict_section
        should_admit = (
            llm_admits
            or (novelty == "novel" and genuineness == "genuine")
            or (novelty == "novel" and composition in ("high", "moderate"))
        )

        logger.info("  LLM: novelty=%s genuine=%s composition=%s verdict=%s",
                    novelty, genuineness, composition,
                    "ADMIT" if llm_admits else "REJECT")

        if should_admit:
            # Forge it
            novelty = _compute_novelty(code)
            fname = safe_filename(names)
            forge_path = FORGE_DIR / f"{fname}.py"
            forge_path.write_text(code, encoding="utf-8")
            meta = {
                "concept_names": names,
                "concept_fields": cand["meta"].get("concept_fields", []),
                "nous_composite_score": cand["meta"].get("nous_composite_score"),
                "test_accuracy": results["accuracy"],
                "test_calibration": results["calibration"],
                "frame": cand["meta"].get("frame", "?"),
                "novelty_min_ncd": novelty["min_ncd"],
                "novelty_mean_ncd": novelty["mean_ncd"],
                "novelty_nearest": novelty["nearest"],
                "novelty_library_size": novelty["library_size"],
                "tier_profile": tier_profile,
                "rarity_score": round(rarity, 4),
                "admitted_via": "deep_inspection",
                "llm_assessment": response[:500],
                "repaired_from": "scrap",
                "original_failure": cand["meta"].get("failure_reason", ""),
                "forged_at": datetime.now().isoformat(),
            }
            (FORGE_DIR / f"{fname}.json").write_text(
                json.dumps(meta, indent=2), encoding="utf-8")
            logger.info("  DEEP INSPECTION FORGED: %s (acc=%.0f%% %s=%.0f%% rarity=%.4f)",
                        key, results["accuracy"] * 100,
                        best_tier[0], best_tier[1] * 100, rarity)
            admitted += 1
        else:
            logger.info("  Rejected: %s", key[:60])

        time.sleep(2.0)

    logger.info("=" * 60)
    logger.info("DEEP INSPECTION COMPLETE: %d inspected, %d admitted", inspected, admitted)
    logger.info("=" * 60)


def repair_with_llm(max_items: int = 50):
    """Use NVIDIA API to fix syntax/import/interface errors in scrapped tools.

    For each fixable scrap:
    1. Send broken code + error to LLM with "fix only" prompt
    2. Extract fixed code
    3. Run through import injection + common fixes + validation + trap battery
    4. Forge if passes (accuracy gate OR novelty gate)
    """
    logger.info("=" * 60)
    logger.info("LLM REPAIR PASS")
    logger.info("=" * 60)

    client = make_client()
    model = DEFAULT_MODEL

    repaired = 0
    attempted = 0
    api_errors = 0

    # Collect fixable candidates
    candidates = []
    for json_file in sorted(SCRAP_DIR.glob("*.json")):
        try:
            meta = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        reason = meta.get("failure_reason", "")
        py_file = SCRAP_DIR / json_file.name.replace(".json", ".py")
        if not py_file.exists():
            continue

        is_fixable = any(x in reason for x in [
            "validation:syntax", "validation:import", "validation:interface",
            "validation:missing_methods",
            "validation:runtime_error: NameError",
            "validation:runtime_error: ImportError",
            "validation:confidence_bad_return_type",
            "validation:confidence_out_of_range",
        ])
        if is_fixable:
            candidates.append({
                "py_file": py_file,
                "json_file": json_file,
                "meta": meta,
                "reason": reason,
            })

    logger.info("Found %d LLM-fixable scrap candidates", len(candidates))

    for cand in candidates[:max_items]:
        attempted += 1
        names = cand["meta"].get("concept_names", [])
        key = " + ".join(sorted(names))
        error = cand["reason"].replace("validation:", "")

        code = cand["py_file"].read_text(encoding="utf-8")

        # Build repair prompt
        prompt = LLM_REPAIR_PROMPT.format(error=error, code=code)

        # Call API
        logger.info("[%d/%d] Repairing: %s (%s)", attempted, min(len(candidates), max_items), key, error[:60])
        response = call_api(client, prompt, model)
        if response is None:
            api_errors += 1
            logger.warning("  API failed, skipping")
            continue

        # Extract code from response
        fixed_code, extract_status = extract_code(response)
        if fixed_code is None:
            logger.debug("  Could not extract code from response")
            continue

        # Apply standard fixers
        fixed_code = _inject_missing_imports(fixed_code)
        fixed_code = _fix_common_errors(fixed_code)

        # Validate
        valid, vreason = validate(fixed_code)
        if not valid:
            logger.debug("  Still invalid after LLM fix: %s", vreason)
            continue

        # Run trap battery
        try:
            tool = load_tool_from_code(fixed_code)
            test_results = run_trap_battery(tool)
        except Exception as e:
            logger.debug("  Runtime error after fix: %s", e)
            continue

        # Compute novelty
        novelty = _compute_novelty(fixed_code)

        # Forge if passes accuracy gate OR novelty gate
        if test_results["passed"] or (novelty["min_ncd"] > 0.85 and test_results["accuracy"] >= 0.20):
            gate = "accuracy" if test_results["passed"] else "novelty"
            fname = safe_filename(names)
            forge_path = FORGE_DIR / f"{fname}.py"
            forge_path.write_text(fixed_code, encoding="utf-8")
            meta = {
                "concept_names": names,
                "concept_fields": cand["meta"].get("concept_fields", []),
                "nous_composite_score": cand["meta"].get("nous_composite_score"),
                "test_accuracy": test_results["accuracy"],
                "test_calibration": test_results["calibration"],
                "frame": cand["meta"].get("frame", "?"),
                "novelty_min_ncd": novelty["min_ncd"],
                "novelty_mean_ncd": novelty["mean_ncd"],
                "novelty_nearest": novelty["nearest"],
                "novelty_library_size": novelty["library_size"],
                "admitted_via": f"{gate}_gate",
                "repaired_from": "scrap_llm_fix",
                "original_failure": cand["reason"],
                "repair_model": model,
                "forged_at": datetime.now().isoformat(),
            }
            (FORGE_DIR / f"{fname}.json").write_text(
                json.dumps(meta, indent=2), encoding="utf-8")
            logger.info("  FORGED [%s gate]: acc=%.0f%% novelty=%.3f",
                        gate, test_results["accuracy"] * 100, novelty["min_ncd"])
            repaired += 1
        else:
            logger.debug("  Fixed but didn't pass (acc=%.0f%% novelty=%.3f)",
                         test_results["accuracy"] * 100, novelty["min_ncd"])

        # Rate limit
        time.sleep(2.0)

    logger.info("=" * 60)
    logger.info("LLM REPAIR COMPLETE: %d attempted, %d forged, %d API errors",
                attempted, repaired, api_errors)
    logger.info("=" * 60)


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
    # ---------------------------------------------------------------------------
    # Augment API fallback (--use-aggie-api, --force-aggie)
    # ---------------------------------------------------------------------------
    parser.add_argument("--use-aggie-api", action="store_true",
                        help="Enable Augment API (auggie-sdk) as fallback when NVIDIA call fails. "
                             "WARNING: burns Augment tokens — use only during NVIDIA outages.")
    parser.add_argument("--force-aggie", action="store_true",
                        help="Skip NVIDIA API entirely; use Augment API (auggie-sdk) for all forges. "
                             "WARNING: burns Augment tokens continuously. Implies --use-aggie-api.")
    parser.add_argument("--aggie-model", type=str, default=AGGIE_DEFAULT_MODEL,
                        choices=["haiku4.5", "sonnet4.5", "sonnet4", "gpt5"],
                        help=f"Augment model to use for fallback (default: {AGGIE_DEFAULT_MODEL})")
    parser.add_argument("--repair-scraps", action="store_true",
                        help="Run scrap repair pass: fix gate failures, score novelty on near-misses")
    parser.add_argument("--repair-with-llm", action="store_true",
                        help="Use LLM API to fix syntax/import/interface errors in scraps")
    parser.add_argument("--inspect-near-misses", action="store_true",
                        help="Deep inspection of near-miss scraps: tier profile + LLM mechanism assessment")
    parser.add_argument("--repair-max", type=int, default=50,
                        help="Max items to attempt in repair pass (default: 50)")
    parser.add_argument("--repair-min-acc", type=float, default=0.25,
                        help="Min accuracy for near-miss inclusion in repair (default: 0.25)")
    args = parser.parse_args()

    # Scrap repair mode — run and exit
    if args.repair_scraps:
        repair_scraps(max_items=args.repair_max, min_accuracy=args.repair_min_acc)
        return

    # LLM repair mode — run and exit
    if args.repair_with_llm:
        repair_with_llm(max_items=args.repair_max)
        return

    # Deep near-miss inspection — run and exit
    if args.inspect_near_misses:
        inspect_near_misses(max_items=args.repair_max)
        return

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

    # Augment API fallback client — created once, reused across the run
    aggie_client = None
    force_aggie = args.force_aggie  # Skip NVIDIA entirely if set
    if args.use_aggie_api or args.force_aggie:
        try:
            aggie_client = make_aggie_client(model=args.aggie_model)
            if args.force_aggie:
                logger.warning("Augment API PRIMARY MODE ENABLED (model=%s) — "
                               "skipping NVIDIA API entirely", args.aggie_model)
            else:
                logger.info("Augment API fallback ENABLED (model=%s) — "
                            "will activate only when NVIDIA call fails", args.aggie_model)
        except Exception as e:
            logger.error("Failed to create Augment API client: %s — fallback disabled", e)
            force_aggie = False

    total_forged = []
    total_scrapped = []
    total_count = 0
    cycle = 0

    mode = "runonce" if args.runonce else "continuous"
    logger.info("Mode: %s", mode)

    # -----------------------------------------------------------------------
    # Agora telemetry (optional — degrades gracefully if Redis unreachable)
    # -----------------------------------------------------------------------
    agora_client = None
    machine = os.environ.get("PROMETHEUS_MACHINE", "M3")
    if HAS_AGORA:
        try:
            agora_client = AgoraClient(agent_name="Hephaestus", machine=machine, persist=False)
            agora_client.connect()
            agora_client.start_heartbeat()
            agora_client.send(
                stream="main",
                subject="Hephaestus online",
                body=f"Forge daemon starting on {machine}, mode={mode}",
                confidence=1.0,
                msg_type=MessageType.ANNOUNCE,
            )
            logger.info("Agora connected as Hephaestus@%s", machine)
        except Exception as e:
            logger.warning("Agora unavailable, running without telemetry: %s", e)
            agora_client = None
    else:
        logger.info("Agora client not installed; running without telemetry")

    # Postgres heartbeat (survives Redis outages)
    import threading
    sys.path.insert(0, str(HEPHAESTUS_ROOT.parent.parent / "scripts"))
    HAS_POSTGRES_PERSIST = False
    agora_persist = None
    try:
        import agora_persist as _ap
        agora_persist = _ap
        agora_persist.write_heartbeat(
            agent_name="Hephaestus", machine=machine,
            status="online", pid=os.getpid(),
        )
        HAS_POSTGRES_PERSIST = True
        logger.info("Postgres heartbeat initialized")
    except Exception as e:
        logger.warning("agora_persist unavailable: %s", e)

    if HAS_POSTGRES_PERSIST:
        def _pg_heartbeat_loop():
            while True:
                time.sleep(60)
                try:
                    agora_persist.write_heartbeat(
                        agent_name="Hephaestus", machine=machine,
                        status="online", pid=os.getpid(),
                    )
                except Exception as e:
                    logger.warning("postgres heartbeat failed: %s", e)
        _pg_thread = threading.Thread(target=_pg_heartbeat_loop, daemon=True)
        _pg_thread.start()
        logger.info("Postgres heartbeat thread started")

    _session = {"forges": 0, "scraps": 0, "api_timeouts": []}

    def _emit_status(current_op="idle", nous_queue_depth=None):
        """Write STATUS.json and mirror to Redis hash agent:Hephaestus."""
        now_iso = datetime.utcnow().isoformat() + "Z"
        ledger_size = 0
        if LEDGER_PATH.exists():
            try:
                ledger_size = sum(1 for _ in open(LEDGER_PATH, encoding="utf-8"))
            except Exception:
                pass
        cutoff = time.time() - 3600
        recent_timeouts = sum(1 for t in _session["api_timeouts"] if t > cutoff)
        total = _session["forges"] + _session["scraps"]
        status = {
            "agent": "Hephaestus",
            "machine": machine,
            "status": "running",
            "last_heartbeat": now_iso,
            "pid": os.getpid(),
            "current_op": current_op,
            "key_metrics": {
                "session_forges": _session["forges"],
                "session_scraps": _session["scraps"],
                "forge_rate_pct": round(_session["forges"] / total * 100, 1) if total > 0 else 0.0,
                "current_forge_version": FORGE_DIR.name,
                "ledger_size": ledger_size,
                "api_timeouts_last_hour": recent_timeouts,
                "nous_queue_depth": nous_queue_depth,
            },
        }
        try:
            STATUS_PATH.write_text(json.dumps(status, indent=2, default=str), encoding="utf-8")
        except Exception:
            pass
        if agora_client and agora_client.r:
            try:
                agora_client.r.hset("agent:Hephaestus", mapping={
                    "status_json": json.dumps(status, default=str),
                    "last_status_update": now_iso,
                })
            except Exception:
                pass
        if HAS_POSTGRES_PERSIST:
            try:
                agora_persist.write_heartbeat(
                    agent_name="Hephaestus", machine=machine,
                    status="online", status_json=status, pid=os.getpid(),
                )
            except Exception as e:
                logger.warning("postgres status mirror failed: %s", e)

    def _on_forge(entry, result):
        """Track forge success and emit SHARE to agora:discoveries."""
        _session["forges"] += 1
        if not agora_client:
            return
        try:
            names = " + ".join(entry.get("concept_names", []))
            comp = entry.get("score", {}).get("composite_score", 0)
            acc = result.get("accuracy", 0)
            cal = result.get("calibration", 0)
            agora_client.share_discovery(
                subject=f"Hephaestus forged: {names}",
                body=(f"Concepts: {names}. "
                      f"Accuracy={acc:.0%}, Calibration={cal:.0%}, "
                      f"Frame={result.get('frame', '?')}"),
                evidence=f"gates_passed=5, composite={comp:.1f}",
                confidence=min(1.0, comp / 10.0) if comp else 0.5,
            )
        except Exception as e:
            logger.warning("Failed to emit forge event to Agora: %s", e)

    def _on_scrap(entry, result):
        """Track scrap; emit ANNOUNCE only on API failures."""
        _session["scraps"] += 1
        reason = result.get("reason", "")
        if reason == "api_call_failed":
            _session["api_timeouts"].append(time.time())
            if agora_client:
                try:
                    names = " + ".join(entry.get("concept_names", []))
                    agora_client.send(
                        stream="main",
                        subject="Hephaestus API degradation",
                        body=f"API call failed for: {names}",
                        confidence=0.5,
                        msg_type=MessageType.ANNOUNCE,
                    )
                except Exception:
                    pass

    def _emit_shutdown():
        """Write final STATUS and send shutdown announcement."""
        total = _session["forges"] + _session["scraps"]
        final_status = {
            "agent": "Hephaestus",
            "machine": machine,
            "status": "stopped",
            "last_heartbeat": datetime.utcnow().isoformat() + "Z",
            "pid": os.getpid(),
            "current_op": "shutdown",
            "key_metrics": {
                "session_forges": _session["forges"],
                "session_scraps": _session["scraps"],
                "forge_rate_pct": round(_session["forges"] / total * 100, 1) if total > 0 else 0.0,
                "current_forge_version": FORGE_DIR.name,
                "ledger_size": 0,
                "api_timeouts_last_hour": 0,
                "nous_queue_depth": None,
            },
        }
        try:
            STATUS_PATH.write_text(json.dumps(final_status, indent=2, default=str), encoding="utf-8")
        except Exception:
            pass
        if not agora_client:
            return
        try:
            agora_client.send(
                stream="main",
                subject="Hephaestus shutting down",
                body=f"Session: {_session['forges']} forged, {_session['scraps']} scrapped",
                confidence=1.0,
                msg_type=MessageType.ANNOUNCE,
            )
            agora_client.disconnect()
        except Exception:
            pass

    _emit_status("starting up")

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
            "aggie_fallback": args.use_aggie_api,
            "force_aggie": force_aggie,
            "aggie_model": args.aggie_model if (args.use_aggie_api or force_aggie) else None,
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
            total_count, shutdown_flag, aggie_client=aggie_client, force_aggie=force_aggie,
            on_forge=_on_forge, on_scrap=_on_scrap, on_status=_emit_status,
        )
        total_forged.extend(forged)
        total_scrapped.extend(scrapped)
        total_count += batch_count

        # Write rankings after each batch
        write_rankings(total_forged, total_scrapped, run_dir)

        if args.runonce:
            break

        if not shutdown_flag[0]:
            _log_frame_scoreboard(run_dir)
            logger.info("Batch complete (%d forged, %d scrapped). "
                        "Sleeping %ds before re-scanning Nous...",
                        len(forged), len(scrapped), int(args.poll_interval))
            slept = 0.0
            while slept < args.poll_interval and not shutdown_flag[0]:
                time.sleep(min(5.0, args.poll_interval - slept))
                slept += 5.0

    _emit_shutdown()

    # Clean up aggie client
    if aggie_client is not None:
        try:
            aggie_client.close()
            logger.info("Augment API client closed")
        except Exception as e:
            logger.debug("Error closing aggie client: %s", e)

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
    _log_frame_scoreboard(run_dir)
    logger.info("  Results: %s", run_dir)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
