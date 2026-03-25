"""Failure analysis and blind spot detection for Nemesis.

Produces human-readable reports and machine-readable JSONL for Coeus.
"""

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from map_elites import MAPElitesGrid

log = logging.getLogger("nemesis.reporter")


def generate_report(grid: MAPElitesGrid, tools: dict,
                    output_dir: Path) -> str:
    """Generate a full failure analysis report.

    Returns the report text and writes it to output_dir.
    """
    tasks = grid.tasks
    n_tasks = len(tasks)
    n_tools = len(tools)

    if not tasks or not tools:
        return "No data to report."

    # Per-tool statistics
    tool_stats = {}
    for name in tools:
        correct = sum(1 for t in tasks
                      if t.tool_results.get(name, {}).get("correct", False))
        broken_by = n_tasks - correct
        tool_stats[name] = {
            "correct": correct,
            "broken_by": broken_by,
            "survival_rate": correct / n_tasks if n_tasks else 0,
        }

    # Blind spots
    blind_spots = grid.blind_spots()

    # MR category analysis
    mr_category_breaks = defaultdict(int)
    for t in tasks:
        if t.tools_broken > 0:
            for mr in t.mr_chain:
                mr_category_breaks[mr] += 1

    # Most effective MR chains
    chain_effectiveness = Counter()
    for t in tasks:
        if t.mr_chain and t.tools_broken > 0:
            chain_key = " → ".join(t.mr_chain)
            chain_effectiveness[chain_key] += t.tools_broken

    # Build report
    lines = [
        f"# Nemesis Failure Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"**Grid coverage**: {grid.n_filled}/100 cells filled ({grid.n_empty} empty)",
        f"**Adversarial tasks**: {n_tasks}",
        f"**Tools evaluated**: {n_tools}",
        f"**Blind spots** (all tools wrong): {len(blind_spots)}",
        "",
        "---",
        "",
        "## Tool Robustness Ranking",
        "",
        "| Rank | Tool | Survival Rate | Broken By |",
        "|------|------|--------------|-----------|",
    ]

    ranked_tools = sorted(tool_stats.items(),
                          key=lambda x: x[1]["survival_rate"], reverse=True)
    for i, (name, stats) in enumerate(ranked_tools, 1):
        lines.append(
            f"| {i} | {name:50s} | {stats['survival_rate']:.0%} | {stats['broken_by']}/{n_tasks} |"
        )

    # Blind spots section
    if blind_spots:
        lines.extend(["", "---", "", "## Blind Spots (no tool handles these)", ""])
        for t in blind_spots:
            lines.append(f"- **{t.category}** [{t.complexity},{t.obfuscation}]: {t.prompt[:80]}")
            lines.append(f"  MR chain: {' → '.join(t.mr_chain)}")
            lines.append(f"  Correct: {t.correct}")
            lines.append("")

    # Most effective mutations
    if chain_effectiveness:
        lines.extend(["---", "", "## Most Effective Mutation Chains", ""])
        lines.append("| Chain | Total Tools Broken |")
        lines.append("|-------|-------------------|")
        for chain, count in chain_effectiveness.most_common(10):
            lines.append(f"| {chain} | {count} |")

    # Per-MR breakdown
    if mr_category_breaks:
        lines.extend(["", "---", "", "## MR Category Effectiveness", ""])
        lines.append("| MR | Tasks That Broke Tools |")
        lines.append("|----|----------------------|")
        for mr, count in sorted(mr_category_breaks.items(), key=lambda x: -x[1]):
            lines.append(f"| {mr} | {count} |")

    # Grid visualization
    lines.extend(["", "---", "", "## Grid Coverage", "", "```"])
    lines.append(grid.summary())
    lines.append("```")

    # Lineage depth analysis
    max_lineage = max((t.lineage_depth for t in tasks), default=0)
    deep_lineages = [t for t in tasks if t.lineage_depth >= 2]
    if deep_lineages:
        lines.extend(["", "---", "", "## Deep Adversarial Lineages (depth >= 2)", ""])
        for t in sorted(deep_lineages, key=lambda x: -x.lineage_depth):
            lines.append(f"- Depth {t.lineage_depth}: [{t.complexity},{t.obfuscation}] "
                         f"{t.prompt[:60]}")
            lines.append(f"  MR chain: {' -> '.join(t.mr_chain)}")
            lines.append("")

    # Per-tool difficulty model
    weak = grid.difficulty_model.weakest_tools(n=5)
    if weak:
        lines.extend(["", "---", "", "## Weakest Tools (lowest adversarial pass rate)", ""])
        lines.append("| Tool | Pass Rate |")
        lines.append("|------|-----------|")
        for name, rate in weak:
            lines.append(f"| {name[:50]} | {rate:.0%} |")

    # Empty cell analysis
    empty = grid.empty_cells()
    if empty:
        lines.extend(["", "### Under-explored regions", ""])
        # Group empty cells by region
        low_complexity = [(r, c) for r, c in empty if r < 3]
        mid_complexity = [(r, c) for r, c in empty if 3 <= r < 7]
        high_complexity = [(r, c) for r, c in empty if r >= 7]
        if high_complexity:
            lines.append(f"- High complexity (rows 8-10): {len(high_complexity)} empty cells")
        if mid_complexity:
            lines.append(f"- Mid complexity (rows 4-7): {len(mid_complexity)} empty cells")
        if low_complexity:
            lines.append(f"- Low complexity (rows 1-3): {len(low_complexity)} empty cells")

    report_text = "\n".join(lines)

    # Write report
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"nemesis_report_{ts}.md"
    report_path.write_text(report_text, encoding="utf-8")
    log.info("Report written: %s", report_path)

    return report_text


def write_adversarial_results(grid: MAPElitesGrid, output_path: Path):
    """Write adversarial results JSONL for Coeus consumption.

    Tagged with provenance='adversarial' to enforce the data separation invariant.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for task in grid.tasks:
            record = {
                "provenance": "adversarial",  # HARD TAG — never enters training
                "prompt": task.prompt,
                "candidates": task.candidates,
                "correct": task.correct,
                "category": task.category,
                "mr_chain": task.mr_chain,
                "complexity": task.complexity,
                "obfuscation": task.obfuscation,
                "disagreement": task.disagreement,
                "tools_broken": task.tools_broken,
                "blind_spot": task.blind_spot,
                "lineage_depth": task.lineage_depth,
                "tool_results": task.tool_results,
                "timestamp": datetime.now().isoformat(),
            }
            f.write(json.dumps(record) + "\n")
    log.info("Adversarial results written: %s (%d tasks)", output_path, grid.n_filled)
