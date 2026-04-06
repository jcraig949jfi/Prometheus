"""
Council Review — Multi-provider critique of research cycle stages.
===================================================================
After each research cycle, fires a review prompt to all 4 council members
(DeepSeek, ChatGPT, Claude, Gemini) in parallel. Each receives:
  - The stage descriptions and actual code snippets
  - The most recent cycle results (hypotheses, searches, battery, verdicts)
  - A request to critique and suggest improvements

Produces a structured review report in convergence/reports/review_{cycle_id}.md

Usage:
    from council_review import run_review
    report_path = run_review(cycle_id="20260406-092956")

Or standalone:
    python council_review.py --cycle-id 20260406-092956
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
import cycle_logger
from council_client import ask_all

SCRIPTS_DIR = Path(__file__).parent
REPORT_DIR = Path(__file__).resolve().parents[2] / "convergence" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = Path(__file__).resolve().parents[2] / "convergence" / "logs"
THREADS_FILE = Path(__file__).resolve().parents[2] / "convergence" / "data" / "active_threads.json"


# ---------------------------------------------------------------------------
# Code snippet extraction — read real code, don't fabricate
# ---------------------------------------------------------------------------

STAGE_FILES = {
    "1_hypothesis_generation": SCRIPTS_DIR / "research_cycle.py",
    "2_search_engine": SCRIPTS_DIR / "search_engine.py",
    "3_evaluation": SCRIPTS_DIR / "research_cycle.py",
    "4_falsification_battery": SCRIPTS_DIR / "falsification_battery.py",
    "5_thread_tracking": SCRIPTS_DIR / "thread_tracker.py",
    "6_structured_logging": SCRIPTS_DIR / "cycle_logger.py",
    "7_council_client": SCRIPTS_DIR / "council_client.py",
}

# Line ranges to extract for each stage (start, end) — the key logic, not boilerplate
STAGE_SNIPPETS = {
    "1_hypothesis_generation": {
        "file": "research_cycle.py",
        "description": "Asks DeepSeek to propose 3 testable cross-domain hypotheses given our data inventory.",
        "extract": "DATA_INVENTORY_PROMPT",  # Extract the prompt template
    },
    "2_search_engine": {
        "file": "search_engine.py",
        "description": "Dispatches searches across 5 datasets: OEIS (392K sequences), LMFDB (134K objects in DuckDB), mathlib (8.4K modules), Metamath (46K theorems), Materials Project (1K crystals).",
        "extract": "SEARCH_REGISTRY",  # Extract the registry
    },
    "3_evaluation": {
        "file": "research_cycle.py",
        "description": "Sends search evidence to DeepSeek for assessment. Advisory only — battery overrides.",
        "extract": "EVALUATE_PROMPT",
    },
    "4_falsification_battery": {
        "file": "falsification_battery.py",
        "description": "11 computational kill tests. No LLM. Permutation null, subset stability, effect size, confound sweep, normalization sign-flip, Bonferroni, dose-response, direction consistency, baseline comparison, outlier sensitivity, cross-validation.",
        "extract": "run_battery",
    },
    "5_thread_tracking": {
        "file": "thread_tracker.py",
        "description": "JSON-based state machine: pending → searching → evaluating → confirmed/falsified/open. JSONL append-only audit log.",
        "extract": "VALID_STATUSES",
    },
}


def _extract_snippet(filepath: Path, marker: str, context_lines: int = 40) -> str:
    """Extract a code snippet around a marker string."""
    if not filepath.exists():
        return f"# File not found: {filepath.name}"
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if marker in line:
            start = max(0, i - 2)
            end = min(len(lines), i + context_lines)
            return "\n".join(lines[start:end])
    # Marker not found — return first context_lines lines
    return "\n".join(lines[:context_lines])


def _load_recent_cycle(cycle_id: str = None) -> dict:
    """Load the most recent cycle results for review context."""
    # Find cycle report
    if cycle_id:
        report_path = REPORT_DIR / f"cycle_{cycle_id}.md"
        log_path = LOG_DIR / f"cycle_{cycle_id}.jsonl"
    else:
        # Find most recent
        reports = sorted(REPORT_DIR.glob("cycle_*.md"), reverse=True)
        if not reports:
            return {"error": "no cycle reports found"}
        report_path = reports[0]
        cycle_id = report_path.stem.replace("cycle_", "")
        log_path = LOG_DIR / f"cycle_{cycle_id}.jsonl"

    result = {"cycle_id": cycle_id}

    if report_path.exists():
        result["report"] = report_path.read_text(encoding="utf-8")

    # Extract key events from JSONL log
    if log_path.exists():
        events = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    ev = json.loads(line)
                    events.append(ev)
                except json.JSONDecodeError:
                    pass
        result["log_events"] = len(events)

        # Summarize key metrics from log
        api_calls = [e for e in events if e.get("event") == "api_call"]
        searches = [e for e in events if e.get("event") == "search_completed"]
        battery_tests = [e for e in events if e.get("component") == "battery"
                         and e.get("event", "").startswith("test_")]
        cycle_complete = [e for e in events if e.get("event") == "cycle_completed"]

        result["metrics"] = {
            "api_calls": len(api_calls),
            "total_tokens": sum(e["data"].get("total_tokens", 0) for e in api_calls),
            "searches": len(searches),
            "total_results": sum(e["data"].get("n_results", 0) for e in searches),
            "battery_tests": len(battery_tests),
            "battery_passes": sum(1 for e in battery_tests if "pass" in e.get("event", "")),
            "battery_fails": sum(1 for e in battery_tests if "fail" in e.get("event", "")),
        }
        if cycle_complete:
            result["metrics"]["elapsed_s"] = cycle_complete[-1]["data"].get("elapsed_s", 0)

    # Load active threads for this cycle
    if THREADS_FILE.exists():
        threads = json.loads(THREADS_FILE.read_text(encoding="utf-8"))
        cycle_threads = {k: v for k, v in threads.items()
                        if v.get("cycle_id") == cycle_id}
        result["threads"] = cycle_threads

    return result


# ---------------------------------------------------------------------------
# Build the review prompt
# ---------------------------------------------------------------------------

REVIEW_SYSTEM = (
    "You are a senior research engineer reviewing an autonomous scientific research pipeline. "
    "You have deep expertise in MLOps, scientific methodology, statistics, API design, and "
    "data engineering. Your job is to find weaknesses, suggest concrete improvements, and "
    "prioritize what to fix first. Be specific — cite line-level issues, name specific tests "
    "that should be added, and propose concrete code changes. No flattery."
)

def build_review_prompt(cycle_data: dict) -> str:
    """Build the full review prompt with code snippets and cycle results."""

    sections = []

    sections.append("# AUTONOMOUS RESEARCH CYCLE — REVIEW REQUEST")
    sections.append("")
    sections.append("We run an autonomous loop that generates hypotheses about cross-domain "
                    "mathematical correlations, searches real datasets, evaluates results, "
                    "and runs an 11-test falsification battery. The LLM generates hypotheses "
                    "but code adjudicates — the battery overrides LLM verdicts.")
    sections.append("")

    # Stage code snippets
    sections.append("## STAGE CODE SNIPPETS")
    sections.append("")

    for stage_name, stage_info in STAGE_SNIPPETS.items():
        filepath = SCRIPTS_DIR / stage_info["file"]
        snippet = _extract_snippet(filepath, stage_info["extract"])
        sections.append(f"### Stage: {stage_name}")
        sections.append(f"**Description:** {stage_info['description']}")
        sections.append(f"**File:** `{stage_info['file']}`")
        sections.append(f"```python\n{snippet}\n```")
        sections.append("")

    # Recent cycle results
    sections.append("## MOST RECENT CYCLE RESULTS")
    sections.append("")

    metrics = cycle_data.get("metrics", {})
    sections.append(f"- Cycle ID: {cycle_data.get('cycle_id', 'unknown')}")
    sections.append(f"- API calls: {metrics.get('api_calls', '?')}")
    sections.append(f"- Total tokens: {metrics.get('total_tokens', '?')}")
    sections.append(f"- Searches: {metrics.get('searches', '?')}")
    sections.append(f"- Total results: {metrics.get('total_results', '?')}")
    sections.append(f"- Battery tests: {metrics.get('battery_tests', '?')} "
                    f"({metrics.get('battery_passes', '?')} pass, {metrics.get('battery_fails', '?')} fail)")
    sections.append(f"- Elapsed: {metrics.get('elapsed_s', '?')}s")
    sections.append("")

    # Thread summaries
    threads = cycle_data.get("threads", {})
    if threads:
        sections.append("### Threads:")
        for tid, t in threads.items():
            status = t.get("status", "?")
            hyp = t.get("hypothesis", "?")[:120]
            n_searches = len(t.get("searches_run", []))
            n_evidence = len(t.get("evidence", []))
            sections.append(f"- **{tid}** [{status}]: {hyp}")
            sections.append(f"  Searches: {n_searches} | Evidence items: {n_evidence}")
        sections.append("")

    # Cycle report excerpt (truncated to avoid token bloat)
    report = cycle_data.get("report", "")
    if report:
        # Take first 2000 chars of report
        sections.append("### Cycle Report (excerpt):")
        sections.append(f"```\n{report[:2000]}\n```")
        sections.append("")

    # The actual review questions
    sections.append("## REVIEW QUESTIONS")
    sections.append("")
    sections.append("For each stage, answer:")
    sections.append("1. **What is the biggest weakness?** (be specific — name the failure mode)")
    sections.append("2. **What concrete improvement would have the highest impact?** (suggest code changes)")
    sections.append("3. **What test or check is missing?** (name it, describe it)")
    sections.append("")
    sections.append("Also answer globally:")
    sections.append("4. **What is the most likely way this pipeline produces false positives?**")
    sections.append("5. **What data source or search capability would most improve hypothesis quality?**")
    sections.append("6. **Rank the stages from weakest to strongest.** Justify.")
    sections.append("7. **If you could change ONE thing about this pipeline, what would it be?**")
    sections.append("")
    sections.append("Be ruthless. This pipeline's job is to NOT publish bad science.")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Generate the review report
# ---------------------------------------------------------------------------

def generate_review_report(cycle_id: str, responses: dict[str, dict],
                           prompt: str) -> Path:
    """Compile council responses into a review report."""
    now = datetime.now()
    report_path = REPORT_DIR / f"review_{cycle_id}.md"

    lines = [
        f"# Council Review: Cycle {cycle_id}",
        f"## Generated: {now.strftime('%Y-%m-%d %H:%M')}",
        f"## Providers: {', '.join(responses.keys())}",
        "",
        "---",
        "",
        "## Response Summary",
        "",
        f"| Provider | Status | Time | Tokens |",
        f"|----------|--------|------|--------|",
    ]

    for name, r in responses.items():
        if "error" in r:
            lines.append(f"| {name} | FAILED | — | — |")
        else:
            elapsed = r.get("elapsed_s", 0)
            tokens = r.get("prompt_tokens", 0) + r.get("completion_tokens", 0)
            lines.append(f"| {name} | OK | {elapsed:.1f}s | {tokens} |")

    lines.extend(["", "---", ""])

    # Individual responses
    for name, r in responses.items():
        lines.append(f"## {name.upper()}")
        lines.append(f"**Model:** {r.get('model', '?')}")
        lines.append(f"**Time:** {r.get('elapsed_s', 0):.1f}s")
        lines.append("")

        if "error" in r:
            lines.append(f"**ERROR:** {r['error']}")
        else:
            lines.append(r.get("text", "(no response)"))

        lines.extend(["", "---", ""])

    # Prompt used (for reproducibility)
    lines.append("## Prompt Sent to Council")
    lines.append("")
    lines.append("<details>")
    lines.append("<summary>Click to expand full prompt</summary>")
    lines.append("")
    lines.append(f"```\n{prompt}\n```")
    lines.append("")
    lines.append("</details>")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_review(cycle_id: str = None, providers: list[str] = None) -> Path:
    """Run a full council review of the most recent (or specified) cycle."""
    t0 = time.time()

    # Always create a fresh logger for review (cycle logger may be closed)
    review_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    log = cycle_logger.init(f"review_{review_id}", console=True)

    log.info("review", "review_started", {"cycle_id": cycle_id or "latest"},
             msg=f"COUNCIL REVIEW — cycle: {cycle_id or 'latest'}")

    # Load cycle data
    cycle_data = _load_recent_cycle(cycle_id)
    if "error" in cycle_data:
        log.error("review", "no_cycle_data", {"error": cycle_data["error"]},
                  msg=f"Cannot load cycle: {cycle_data['error']}")
        return None

    actual_cycle_id = cycle_data.get("cycle_id", cycle_id or "unknown")
    log.info("review", "cycle_data_loaded", {
        "cycle_id": actual_cycle_id,
        "has_report": "report" in cycle_data,
        "n_threads": len(cycle_data.get("threads", {})),
        "metrics": cycle_data.get("metrics", {}),
    }, msg=f"Loaded cycle {actual_cycle_id}: {cycle_data.get('metrics', {})}")

    # Build prompt
    prompt = build_review_prompt(cycle_data)
    log.info("review", "prompt_built", {
        "prompt_length": len(prompt),
    }, msg=f"Review prompt: {len(prompt)} chars")

    # Fire to all providers in parallel
    if providers is None:
        providers = ["deepseek", "openai", "claude", "gemini"]

    log.info("review", "council_firing", {"providers": providers},
             msg=f"Firing to: {', '.join(providers)}")

    responses = ask_all(prompt, system=REVIEW_SYSTEM, providers=providers,
                        max_tokens=4096, temperature=0.3)

    # Generate report
    report_path = generate_review_report(actual_cycle_id, responses, prompt)
    elapsed = time.time() - t0

    succeeded = sum(1 for r in responses.values() if "text" in r)
    failed = sum(1 for r in responses.values() if "error" in r)

    log.info("review", "review_completed", {
        "cycle_id": actual_cycle_id,
        "elapsed_s": round(elapsed, 1),
        "succeeded": succeeded,
        "failed": failed,
        "report_path": str(report_path),
    }, msg=f"REVIEW COMPLETE: {succeeded} responded, {failed} failed, {elapsed:.1f}s | {report_path}")

    return report_path


def main():
    parser = argparse.ArgumentParser(description="Council Review of Research Cycle")
    parser.add_argument("--cycle-id", type=str, default=None,
                        help="Cycle ID to review (default: most recent)")
    parser.add_argument("--providers", type=str, nargs="+",
                        default=["deepseek", "openai", "claude", "gemini"],
                        help="Which council members to query")
    args = parser.parse_args()

    report = run_review(cycle_id=args.cycle_id, providers=args.providers)
    if report:
        print(f"\nDone. Review at: {report}")


if __name__ == "__main__":
    main()
