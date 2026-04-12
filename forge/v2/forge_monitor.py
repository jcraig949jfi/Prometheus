"""Forge V2 Pipeline Monitor — periodic health check + DeepSeek-summarized report.

Checks all three pipeline components (Nous T2, Hephaestus T2, Nemesis T2),
summarizes health/wins/problems via DeepSeek, checks token balance,
writes a timestamped report, and commits+pushes it.

Usage:
    python forge_monitor.py              # one-shot report
    python forge_monitor.py --loop 1800  # repeat every 30 min
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib import request, error as urlerror

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent          # forge/v2
_FORGE = _HERE.parent                            # forge
_REPO = _FORGE.parent                            # F:\Prometheus

HEPH_ROOT = _HERE / "hephaestus_t2"
NOUS_ROOT = _HERE / "nous_t2"
NEMESIS_ROOT = _HERE / "nemesis_t2"

LEDGER = HEPH_ROOT / "ledger_t2.jsonl"
HEPH_RUNS = HEPH_ROOT / "runs"
NOUS_RUNS = NOUS_ROOT / "runs"
NEMESIS_REPORTS = NEMESIS_ROOT / "reports"
NEMESIS_RESULTS = NEMESIS_ROOT / "adversarial" / "adversarial_results_t2.jsonl"

REPORT_DIR = _HERE / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# API key loading (reuse forge's loader)
# ---------------------------------------------------------------------------

sys.path.insert(0, str(_REPO))
from keys import get_key as _central_get_key


def _load_deepseek_key() -> str:
    try:
        return _central_get_key("DEEPSEEK")
    except ValueError:
        pass
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key:
        return key
    kf = _REPO / "DeepseekKey.txt"
    if kf.exists():
        return kf.read_text().strip()
    raise RuntimeError("DeepSeek API key not found")


# ---------------------------------------------------------------------------
# DeepSeek helpers
# ---------------------------------------------------------------------------

def deepseek_summarize(system: str, data: str, max_tokens: int = 512) -> str:
    """Ask DeepSeek to summarize a data blob. Returns summary text."""
    key = _load_deepseek_key()
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": data},
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")

    req = request.Request(
        "https://api.deepseek.com/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[DeepSeek call failed: {e}]"


def deepseek_balance() -> str:
    """Query DeepSeek balance. Returns formatted string."""
    try:
        key = _load_deepseek_key()
        req = request.Request(
            "https://api.deepseek.com/user/balance",
            headers={"Authorization": f"Bearer {key}"},
            method="GET",
        )
        with request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for info in data.get("balance_infos", []):
            if info.get("currency") == "USD":
                return f"${info['total_balance']} (topped up: ${info['topped_up_balance']}, granted: ${info['granted_balance']})"
        return str(data)
    except Exception as e:
        return f"[Balance check failed: {e}]"


# ---------------------------------------------------------------------------
# Data collectors
# ---------------------------------------------------------------------------

def collect_hephaestus() -> str:
    """Collect recent Hephaestus T2 ledger data for summarization."""
    if not LEDGER.exists():
        return "No ledger found."

    lines = LEDGER.read_text(encoding="utf-8").strip().splitlines()
    total = len(lines)

    # Parse all entries
    entries = []
    for line in lines:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            pass

    # Stats
    forged = [e for e in entries if e.get("status") == "forged"]
    scrapped = [e for e in entries if e.get("status") == "scrap"]

    # Recent entries (last 20)
    recent = entries[-20:]

    # Reason breakdown for scrapped
    reasons = {}
    for e in scrapped:
        r = e.get("reason", "unknown")
        # Simplify reason to first token
        r_key = r.split(":")[0] if ":" in r else r
        reasons[r_key] = reasons.get(r_key, 0) + 1

    # Provider breakdown
    providers = {}
    for e in entries:
        p = e.get("provider", "unknown")
        providers[p] = providers.get(p, 0) + 1

    # Scores for recent
    recent_scores = [(e.get("tool_id", "?"), e.get("score", 0), e.get("reason", ""))
                     for e in recent]

    # Latest run checkpoint
    checkpoint_info = "No checkpoint found"
    if HEPH_RUNS.exists():
        runs = sorted([r for r in HEPH_RUNS.iterdir() if r.is_dir()])
        if runs:
            cp = runs[-1] / "checkpoint.json"
            if cp.exists():
                checkpoint_info = cp.read_text(encoding="utf-8")[:500]

    # Check for hallucination rejections specifically
    halluc_count = sum(1 for e in entries if "Hallucinated" in e.get("reason", ""))

    blob = f"""HEPHAESTUS T2 STATUS
Total ledger entries: {total}
Forged (PASS): {len(forged)}
Scrapped: {len(scrapped)}
Hallucination rejections: {halluc_count}
Provider breakdown: {json.dumps(providers)}
Scrap reason breakdown: {json.dumps(reasons, indent=2)}

Latest checkpoint: {checkpoint_info}

Last 20 entries (tool_id, score, reason):
"""
    for tid, sc, reason in recent_scores:
        blob += f"  {tid}: score={sc:.2f}, reason={reason}\n"

    if forged:
        blob += "\nFORGED TOOLS:\n"
        for e in forged:
            blob += f"  {e['tool_id']}: score={e.get('score',0):.2f}, category={e.get('category','?')}\n"

    return blob


def collect_nous() -> str:
    """Collect recent Nous T2 data."""
    if not NOUS_RUNS.exists():
        return "No Nous runs found."

    runs = sorted([r for r in NOUS_RUNS.iterdir() if r.is_dir()])
    total_runs = len(runs)

    # Check last 3 runs
    recent_runs = runs[-3:] if runs else []
    run_info = []
    for rd in recent_runs:
        resp_file = rd / "responses.jsonl"
        if resp_file.exists():
            lines = resp_file.read_text(encoding="utf-8").strip().splitlines()
            count = len(lines)
            # Parse top scores
            top_scores = []
            for line in lines[:5]:
                try:
                    entry = json.loads(line)
                    sc = entry.get("score", {})
                    cs = sc.get("composite_score", 0) if isinstance(sc, dict) else sc
                    concepts = entry.get("concept_names", [])
                    top_scores.append((cs, concepts))
                except json.JSONDecodeError:
                    pass
            run_info.append(f"  Run {rd.name}: {count} suggestions, top scores: {top_scores[:3]}")
        else:
            run_info.append(f"  Run {rd.name}: no responses.jsonl")

    blob = f"""NOUS T2 STATUS
Total runs: {total_runs}
Recent runs (last 3):
"""
    blob += "\n".join(run_info)
    return blob


def collect_nemesis() -> str:
    """Collect recent Nemesis T2 data."""
    if not NEMESIS_REPORTS.exists():
        return "No Nemesis reports found."

    reports = sorted(NEMESIS_REPORTS.glob("nemesis_report_*.md"))
    total_reports = len(reports)

    # Read latest report
    latest_content = ""
    if reports:
        latest = reports[-1]
        latest_content = latest.read_text(encoding="utf-8")[:2000]

    # Count adversarial results
    adv_count = 0
    if NEMESIS_RESULTS.exists():
        adv_count = sum(1 for _ in NEMESIS_RESULTS.read_text(encoding="utf-8").strip().splitlines())

    blob = f"""NEMESIS T2 STATUS
Total reports: {total_reports}
Total adversarial test cases: {adv_count}

Latest report:
{latest_content}
"""
    return blob


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a pipeline health monitor for Project Prometheus's Forge V2.
Analyze the raw data provided and produce a concise status report section.
Focus on:
1. HEALTH: Is the component running? Any errors or stalls?
2. WINS: Successful outputs, improvements, milestones reached.
3. PROBLEMS: Failures, regressions, concerning patterns.
4. RECOMMENDATIONS: Brief suggestions if problems exist.

Be direct and factual. Use bullet points. No filler."""


_EASTERN = ZoneInfo("America/New_York")


def generate_report() -> str:
    """Generate the full monitor report."""
    now = datetime.now(_EASTERN)
    ts = now.strftime("%Y-%m-%d %H:%M %Z")

    print(f"[{ts}] Collecting pipeline data...")

    # Collect raw data
    heph_data = collect_hephaestus()
    nous_data = collect_nous()
    nemesis_data = collect_nemesis()

    print("  Summarizing Hephaestus T2 via DeepSeek...")
    heph_summary = deepseek_summarize(SYSTEM_PROMPT, heph_data)

    print("  Summarizing Nous T2 via DeepSeek...")
    nous_summary = deepseek_summarize(SYSTEM_PROMPT, nous_data)

    print("  Summarizing Nemesis T2 via DeepSeek...")
    nemesis_summary = deepseek_summarize(SYSTEM_PROMPT, nemesis_data)

    print("  Checking DeepSeek balance...")
    balance = deepseek_balance()

    report = f"""# Forge V2 Pipeline Monitor — {ts}

## Hephaestus T2 (Forge)

{heph_summary}

## Nous T2 (Substrate Mining)

{nous_summary}

## Nemesis T2 (Adversarial)

{nemesis_summary}

## DeepSeek Balance

{balance}

---
*Auto-generated by forge_monitor.py*
"""
    return report


# ---------------------------------------------------------------------------
# Git commit + push
# ---------------------------------------------------------------------------

def commit_and_push(report_path: Path):
    """Commit just the report file and push to remote."""
    # Use absolute paths for git add to avoid Windows path separator issues.
    # --force is needed because **/reports/ is gitignored globally.
    report_abs = str(report_path.resolve())
    latest_abs = str((REPORT_DIR / "LATEST.md").resolve())

    # Stage the report + LATEST (force past gitignore)
    for fpath in [report_abs, latest_abs]:
        subprocess.run(
            ["git", "add", "--force", "--", fpath],
            cwd=str(_REPO), capture_output=True,
        )

    # Check if there's anything staged
    status = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=str(_REPO), capture_output=True, text=True,
    )
    if not status.stdout.strip():
        print("  Nothing to commit (files may already be committed).")
        return False

    # Commit
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    result = subprocess.run(
        ["git", "commit", "-m", f"Forge V2 monitor report {ts}"],
        cwd=str(_REPO), capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  Git commit failed: {result.stdout.strip()} {result.stderr.strip()}")
        return False

    print(f"  Committed: {report_path.name}")

    # Pull --rebase to stay ahead of other auto-committers (e.g. Apollo monitor)
    result = subprocess.run(
        ["git", "pull", "--rebase", "--autostash"],
        cwd=str(_REPO), capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  Git pull --rebase failed: {result.stderr.strip()}")
        # Abort the rebase so we don't leave ghost state
        subprocess.run(
            ["git", "rebase", "--abort"],
            cwd=str(_REPO), capture_output=True, text=True,
        )

    # Push
    result = subprocess.run(
        ["git", "push"],
        cwd=str(_REPO), capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  Git push failed: {result.stderr.strip()}")
        return False

    print("  Pushed to remote.")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Forge V2 Pipeline Monitor")
    parser.add_argument("--loop", type=int, default=1800,
                        help="Repeat every N seconds (default: 1800 = 30 min, 0 = one-shot)")
    args = parser.parse_args()

    while True:
        try:
            report = generate_report()

            # Write report
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = REPORT_DIR / f"monitor_{ts}.md"
            report_path.write_text(report, encoding="utf-8")
            print(f"  Report written: {report_path.name}")

            # Also overwrite latest symlink-style file for quick reading
            latest_path = REPORT_DIR / "LATEST.md"
            latest_path.write_text(report, encoding="utf-8")

            # Commit and push
            commit_and_push(report_path)

            print(f"  Done. Sleeping {args.loop}s..." if args.loop else "  Done.")

        except Exception as e:
            print(f"  ERROR: {e}")

        if args.loop <= 0:
            break

        time.sleep(args.loop)


if __name__ == "__main__":
    main()
