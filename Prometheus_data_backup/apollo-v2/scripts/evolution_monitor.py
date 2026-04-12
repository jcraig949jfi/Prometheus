"""
evolution_monitor.py — Periodic evolution analysis via DeepSeek API.

Collects data from all running Apollo instances, sends to DeepSeek
for analysis, saves report, and pushes to GitHub.
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

APOLLO_DIR = Path(__file__).parent.parent
PROJECT_ROOT = APOLLO_DIR.parent
REPORT_DIR = APOLLO_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

DEEPSEEK_KEY = "sk-0c89bfe76fa241f38573b5386931147a"

RUNS = {
    "v2_d (100% Qwen)": APOLLO_DIR / "run_v2d",
    "v2_d2 (50/50 Qwen+DeepSeek)": APOLLO_DIR / "run_v2d2",
    "v2_d3 (100% DeepSeek)": APOLLO_DIR / "run_v2d3",
}


def read_latest_dashboard(run_dir, n=20):
    """Read last N dashboard entries."""
    path = run_dir / "dashboard" / "status_v2.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        lines = f.readlines()
    entries = []
    for l in lines[-n:]:
        try:
            entries.append(json.loads(l))
        except json.JSONDecodeError:
            pass
    return entries


def read_latest_health(run_dir):
    """Read last health report from logs."""
    path = run_dir / "logs" / "apollo_run.jsonl"
    if not path.exists():
        return None
    last_health = None
    with open(path) as f:
        for line in f:
            if '"stage": "health"' in line and "HEALTH" in line:
                try:
                    last_health = json.loads(line)
                except json.JSONDecodeError:
                    pass
    return last_health


def read_llm_stats(run_dir):
    """Count LLM calls by client type."""
    path = run_dir / "logs" / "apollo_run.jsonl"
    if not path.exists():
        return {}
    stats = {"primary": 0, "alt": 0, "deepseek": 0, "batch": 0, "single": 0,
             "success": 0, "fail": 0}
    # Only read entries after the latest "Starting evolution at gen 1"
    last_start = 0
    lines = []
    with open(path) as f:
        all_lines = f.readlines()
    for i, l in enumerate(all_lines):
        if "Starting evolution at gen" in l:
            last_start = i
    for l in all_lines[last_start:]:
        if '"stage": "llm"' not in l:
            continue
        try:
            e = json.loads(l)
            d = e.get("data", {})
            client = d.get("client", "unknown")
            mode = d.get("mode", "unknown")
            success = d.get("success", False)
            if client == "alt" or mode == "deepseek":
                stats["alt"] += 1
            elif client == "primary":
                stats["primary"] += 1
            if "batch" in mode:
                stats["batch"] += 1
            else:
                stats["single"] += 1
            if success:
                stats["success"] += 1
            else:
                stats["fail"] += 1
        except json.JSONDecodeError:
            pass
    return stats


def read_lineage_mutations(run_dir, last_n=50):
    """Check what mutation types are in recent elites."""
    path = run_dir / "lineage" / "lineage_v2.jsonl"
    if not path.exists():
        return {}
    with open(path) as f:
        lines = f.readlines()
    from collections import Counter
    mut_types = Counter()
    for l in lines[-last_n:]:
        try:
            e = json.loads(l)
            for m in e.get("mutations_applied", []):
                mut_types[m] += 1
        except json.JSONDecodeError:
            pass
    return dict(mut_types.most_common())


def collect_data():
    """Collect evolution data from all runs."""
    report_data = {}
    for name, run_dir in RUNS.items():
        if not run_dir.exists():
            continue
        dashboard = read_latest_dashboard(run_dir, n=10)
        health = read_latest_health(run_dir)
        llm_stats = read_llm_stats(run_dir)
        mutations = read_lineage_mutations(run_dir, last_n=50)

        if not dashboard:
            continue

        latest = dashboard[-1]
        trajectory = []
        for d in dashboard:
            trajectory.append({
                "gen": d["generation"],
                "best_acc": round(d["best_accuracy_margin"], 3),
                "med_acc": round(d["median_accuracy_margin"], 3),
                "abl": round(d["best_ablation_delta"], 3),
            })

        report_data[name] = {
            "latest_gen": latest["generation"],
            "best_accuracy_margin": round(latest["best_accuracy_margin"], 3),
            "median_accuracy_margin": round(latest["median_accuracy_margin"], 3),
            "best_ablation_delta": round(latest["best_ablation_delta"], 3),
            "compilation_rate": latest.get("compilation_survival_pct", 1.0),
            "archive_size": latest.get("novelty_archive_size", 0),
            "ncd_weight": latest.get("ncd_decay_weight", 1.0),
            "median_primitives": latest.get("median_primitive_count", 0),
            "trajectory": trajectory,
            "health": health.get("message", "N/A") if health else "N/A",
            "llm_stats": llm_stats,
            "elite_mutations": mutations,
        }

    return report_data


def build_prompt(data):
    """Build analysis prompt for DeepSeek."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    prompt = f"""You are analyzing three parallel evolutionary runs of Apollo, a system that evolves reasoning organisms. Each run uses a different LLM for structural mutations:

- v2_d: 100% Qwen-7B (local, 8-bit quantized)
- v2_d2: 50% Qwen-7B / 50% DeepSeek-chat (API)
- v2_d3: 100% DeepSeek-chat (API)

All three share the same evolutionary engine (NSGA-III, racing evaluation, adaptive operator selection, difficulty curriculum, parameter annealing). The only variable is which LLM generates structural mutations (route logic, wiring, primitive swaps).

Report timestamp: {timestamp}

Here is the current data from all three runs:

"""
    for name, rd in data.items():
        prompt += f"\n### {name}\n"
        prompt += f"Generation: {rd['latest_gen']}\n"
        prompt += f"Best accuracy margin: {rd['best_accuracy_margin']:+.3f}\n"
        prompt += f"Median accuracy margin: {rd['median_accuracy_margin']:+.3f}\n"
        prompt += f"Best ablation delta: {rd['best_ablation_delta']:.3f}\n"
        prompt += f"Compilation rate: {rd['compilation_rate']:.0%}\n"
        prompt += f"Archive: {rd['archive_size']}\n"
        prompt += f"NCD weight: {rd['ncd_weight']}\n"
        prompt += f"Median primitives: {rd['median_primitives']}\n"
        prompt += f"Health: {rd['health']}\n"
        prompt += f"LLM stats: {rd['llm_stats']}\n"
        prompt += f"Elite mutations: {rd['elite_mutations']}\n"
        prompt += f"Trajectory (last 10 gens):\n"
        for t in rd['trajectory']:
            prompt += f"  gen {t['gen']:>4}: best={t['best_acc']:+.3f} med={t['med_acc']:+.3f} abl={t['abl']:.3f}\n"

    prompt += """
Analyze these runs. In your report, address:

1. **Comparison**: Which LLM variant is performing best? Is there a statistically meaningful difference yet, or is it too early to tell?

2. **LLM Mutation Survival**: Check the elite_mutations dict. Are any LLM-generated mutations (containing 'llm' or 'annealed') surviving to elite status? If not, why might that be?

3. **Trajectory Analysis**: Are the runs converging, diverging, or plateauing? What's the trend?

4. **Anomalies**: Anything unusual in the data — compilation failures, archive saturation, AOS collapse, stagnation?

5. **Recommendations**: What should change for the next restart? Specific, actionable suggestions.

Keep the report concise (under 500 words). Use markdown formatting. Be honest — if the data doesn't show a difference yet, say so.
"""
    return prompt


def call_deepseek(prompt):
    """Send prompt to DeepSeek API."""
    from openai import OpenAI
    client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are an expert in evolutionary computation analyzing experimental results. Be concise, specific, and honest about what the data shows."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2048,
        temperature=0.3,
    )
    return response.choices[0].message.content


def save_and_push_report(analysis, data):
    """Save report and push to GitHub."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_file = REPORT_DIR / f"evolution_report_{timestamp}.md"

    # Build the full report
    report = f"# Apollo Evolution Monitor — {timestamp}\n\n"
    report += "## Run Status\n\n"
    report += "| Run | Gen | Best Acc | Med Acc | Ablation | Prims | LLM Calls |\n"
    report += "|-----|-----|----------|---------|----------|-------|----------|\n"
    for name, rd in data.items():
        total_llm = rd['llm_stats'].get('success', 0) + rd['llm_stats'].get('fail', 0)
        alt_pct = rd['llm_stats'].get('alt', 0) / max(total_llm, 1) * 100
        report += (f"| {name} | {rd['latest_gen']} | "
                   f"{rd['best_accuracy_margin']:+.3f} | {rd['median_accuracy_margin']:+.3f} | "
                   f"{rd['best_ablation_delta']:.3f} | {rd['median_primitives']} | "
                   f"{total_llm} ({alt_pct:.0f}% DS) |\n")

    report += f"\n## DeepSeek Analysis\n\n{analysis}\n"

    report += "\n---\n*Auto-generated by evolution_monitor.py*\n"

    report_file.write_text(report, encoding="utf-8")
    print(f"Report saved: {report_file.name}")

    # Git add, commit, push — only the report file
    import subprocess
    try:
        subprocess.run(
            ["git", "add", "-f", str(report_file)],
            cwd=str(PROJECT_ROOT), check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m",
             f"Apollo evolution report {timestamp}\n\nCo-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"],
            cwd=str(PROJECT_ROOT), check=True, capture_output=True
        )
        result = subprocess.run(
            ["git", "push"],
            cwd=str(PROJECT_ROOT), check=True, capture_output=True, text=True
        )
        print(f"Pushed to GitHub: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Git push failed: {e.stderr if hasattr(e, 'stderr') else e}")
        # Try pull then push
        try:
            subprocess.run(
                ["git", "pull", "--no-edit"],
                cwd=str(PROJECT_ROOT), check=True, capture_output=True
            )
            subprocess.run(
                ["git", "push"],
                cwd=str(PROJECT_ROOT), check=True, capture_output=True
            )
            print("Pushed after pull")
        except subprocess.CalledProcessError as e2:
            print(f"Git push failed even after pull: {e2}")


def main():
    print(f"\n{'='*60}")
    print(f"  Apollo Evolution Monitor — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # Collect data
    print("Collecting data from runs...")
    data = collect_data()
    if not data:
        print("No active runs found. Skipping.")
        return

    for name, rd in data.items():
        print(f"  {name}: gen {rd['latest_gen']}, best={rd['best_accuracy_margin']:+.3f}")

    # Analyze with DeepSeek
    print("Sending to DeepSeek for analysis...")
    prompt = build_prompt(data)
    try:
        analysis = call_deepseek(prompt)
        print("Analysis received.")
    except Exception as e:
        analysis = f"*Analysis failed: {e}*"
        print(f"DeepSeek call failed: {e}")

    # Save and push
    print("Saving report and pushing to GitHub...")
    save_and_push_report(analysis, data)
    print("Done.\n")


if __name__ == "__main__":
    main()
