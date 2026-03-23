#!/usr/bin/env python3
"""
Pronoia — The Forethought Orchestrator

Launches and chains Prometheus agents so James doesn't have to remember.

Usage:
    python pronoia.py scan          # Eos scan → Metis brief (single pass)
    python pronoia.py scan --loop   # Eos daemon + Metis after each cycle
    python pronoia.py eos           # Eos only (single scan)
    python pronoia.py metis         # Metis only (analyze latest digest)
    python pronoia.py status        # What's been produced today?
    python pronoia.py review        # Run review_watchman on latest Ignis data
"""

import argparse
import subprocess
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (all relative to this script's location)
# ---------------------------------------------------------------------------

PROMETHEUS_ROOT = Path(__file__).resolve().parent
EOS_DAEMON = PROMETHEUS_ROOT / "agents" / "eos" / "src" / "eos_daemon.py"
ALETHEIA_SCRIPT = PROMETHEUS_ROOT / "agents" / "aletheia" / "src" / "aletheia.py"
METIS_SCRIPT = PROMETHEUS_ROOT / "agents" / "metis" / "src" / "metis.py"
CLYMENE_SCRIPT = PROMETHEUS_ROOT / "agents" / "clymene" / "src" / "clymene.py"
CLYMENE_LAST_RUN = PROMETHEUS_ROOT / "agents" / "clymene" / "data" / "last_run.txt"
CLYMENE_REPORTS = PROMETHEUS_ROOT / "agents" / "clymene" / "reports"
HERMES_SCRIPT = PROMETHEUS_ROOT / "agents" / "hermes" / "src" / "hermes.py"
EOS_REPORTS = PROMETHEUS_ROOT / "agents" / "eos" / "reports"
ALETHEIA_DATA = PROMETHEUS_ROOT / "agents" / "aletheia" / "data"
METIS_BRIEFS = PROMETHEUS_ROOT / "agents" / "metis" / "briefs"
IGNIS_SRC = PROMETHEUS_ROOT / "ignis" / "src"
REVIEW_WATCHMAN = IGNIS_SRC / "review_watchman.py"
IGNIS_RESULTS = IGNIS_SRC / "results" / "ignis"

# Clymene cooldown — default 72 hours (3 days)
CLYMENE_COOLDOWN_HOURS = 72

PYTHON = sys.executable  # Use the same Python that launched Pronoia


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def banner(text: str) -> None:
    width = 62
    print(f"\n{'=' * width}")
    print(f"  {text}")
    print(f"{'=' * width}\n")


# ---------------------------------------------------------------------------
# GitHub publish
# ---------------------------------------------------------------------------

def publish_reports() -> bool:
    """Commit and push latest reports/briefs/results to GitHub."""
    banner("PUBLISHING TO GITHUB")

    # Files to publish
    publish_paths = [
        "agents/eos/reports/",
        "agents/aletheia/data/",
        "agents/metis/briefs/",
        "agents/clymene/reports/",
        "agents/hermes/digests/",
        "docs/RESULTS.md",
        "docs/TODO.md",
        "agents/eos/data/paper_index.json",
    ]

    # Stage files that exist
    staged = []
    for p in publish_paths:
        full = PROMETHEUS_ROOT / p
        if full.exists():
            staged.append(p)

    if not staged:
        print(f"[{timestamp()}] Nothing to publish")
        return False

    try:
        # Stage
        for p in staged:
            subprocess.run(["git", "add", p], cwd=str(PROMETHEUS_ROOT),
                           capture_output=True)

        # Check if there are actual changes
        result = subprocess.run(["git", "diff", "--cached", "--quiet"],
                                cwd=str(PROMETHEUS_ROOT), capture_output=True)
        if result.returncode == 0:
            print(f"[{timestamp()}] No changes to publish")
            return False

        # Commit
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = f"pronoia: auto-publish reports {ts}"
        subprocess.run(["git", "commit", "-m", msg],
                       cwd=str(PROMETHEUS_ROOT), capture_output=True)

        # Push
        result = subprocess.run(["git", "push"], cwd=str(PROMETHEUS_ROOT),
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"[{timestamp()}] Published to GitHub")
            return True
        else:
            print(f"[{timestamp()}] Push failed: {result.stderr.strip()}")
            return False

    except Exception as e:
        print(f"[{timestamp()}] Publish error: {e}")
        return False


# ---------------------------------------------------------------------------
# Agent runners
# ---------------------------------------------------------------------------

def run_eos(once: bool = True) -> Path | None:
    """Run Eos and return the digest path if produced."""
    banner("EOS — Scanning the horizon")

    if not EOS_DAEMON.exists():
        print(f"[ERROR] Eos not found at {EOS_DAEMON}")
        return None

    cmd = [PYTHON, str(EOS_DAEMON)]
    if once:
        cmd.append("--once")

    print(f"[{timestamp()}] Launching: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(EOS_DAEMON.parent.parent))

    if result.returncode != 0:
        print(f"[WARN] Eos exited with code {result.returncode}")

    # Find today's digest
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    digest_path = EOS_REPORTS / f"{today}.md"
    if digest_path.exists():
        print(f"[{timestamp()}] Digest ready: {digest_path}")
        return digest_path
    else:
        print(f"[{timestamp()}] No digest found for {today}")
        return None


def run_aletheia() -> bool:
    """Run Aletheia to harvest knowledge from Eos findings."""
    banner("ALETHEIA — Harvesting knowledge")

    if not ALETHEIA_SCRIPT.exists():
        print(f"[{timestamp()}] Aletheia not found at {ALETHEIA_SCRIPT} — skipping")
        return False

    cmd = [PYTHON, str(ALETHEIA_SCRIPT), "--once"]
    print(f"[{timestamp()}] Launching: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ALETHEIA_SCRIPT.parent.parent))

    if result.returncode != 0:
        print(f"[WARN] Aletheia exited with code {result.returncode}")
        return False

    # Check if knowledge graph exists
    kg_path = ALETHEIA_DATA / "knowledge_graph.db"
    if kg_path.exists():
        size_kb = kg_path.stat().st_size / 1024
        print(f"[{timestamp()}] Knowledge graph: {size_kb:.0f} KB")
        return True
    else:
        print(f"[{timestamp()}] No knowledge graph produced")
        return False


def clymene_is_due() -> bool:
    """Check if enough time has passed since Clymene's last run."""
    if not CLYMENE_LAST_RUN.exists():
        return True  # Never run before
    try:
        last = datetime.fromisoformat(
            CLYMENE_LAST_RUN.read_text(encoding="utf-8").strip()
        )
        elapsed = (datetime.now(timezone.utc) - last).total_seconds() / 3600
        if elapsed >= CLYMENE_COOLDOWN_HOURS:
            return True
        print(f"[{timestamp()}] Clymene: last ran {elapsed:.1f}h ago "
              f"(cooldown: {CLYMENE_COOLDOWN_HOURS}h) — skipping")
        return False
    except (ValueError, OSError):
        return True  # Can't read timestamp — run anyway


def run_clymene() -> bool:
    """Run Clymene hoard cycle if cooldown has elapsed."""
    if not clymene_is_due():
        return False

    banner("CLYMENE — Hoarding knowledge")

    if not CLYMENE_SCRIPT.exists():
        print(f"[{timestamp()}] Clymene not found at {CLYMENE_SCRIPT} — skipping")
        return False

    cmd = [PYTHON, str(CLYMENE_SCRIPT), "--once"]
    print(f"[{timestamp()}] Launching: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(CLYMENE_SCRIPT.parent.parent))

    if result.returncode != 0:
        print(f"[WARN] Clymene exited with code {result.returncode}")
        return False

    # Check for today's report
    today = datetime.now().strftime("%Y-%m-%d")
    report = CLYMENE_REPORTS / f"{today}_hoard.md"
    if report.exists():
        print(f"[{timestamp()}] Hoard report: {report}")
        return True
    print(f"[{timestamp()}] Clymene completed (no report found)")
    return True


def run_hermes() -> bool:
    """Run Hermes to collect cycle reports and email digest."""
    banner("HERMES — Delivering the digest")

    if not HERMES_SCRIPT.exists():
        print(f"[{timestamp()}] Hermes not found at {HERMES_SCRIPT} — skipping")
        return False

    cmd = [PYTHON, str(HERMES_SCRIPT), "--once"]
    print(f"[{timestamp()}] Launching: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(HERMES_SCRIPT.parent.parent))

    if result.returncode != 0:
        print(f"[WARN] Hermes exited with code {result.returncode}")
        return False

    print(f"[{timestamp()}] Hermes delivered")
    return True


def run_metis(digest_path: Path = None) -> Path | None:
    """Run Metis and return the brief path if produced."""
    banner("METIS — Analyzing findings")

    if not METIS_SCRIPT.exists():
        print(f"[ERROR] Metis not found at {METIS_SCRIPT}")
        return None

    cmd = [PYTHON, str(METIS_SCRIPT)]
    if digest_path:
        cmd.extend(["--digest", str(digest_path)])

    print(f"[{timestamp()}] Launching: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(METIS_SCRIPT.parent.parent))

    if result.returncode != 0:
        print(f"[WARN] Metis exited with code {result.returncode}")

    # Find today's brief
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    brief_path = METIS_BRIEFS / f"{today}_brief.md"
    if brief_path.exists():
        print(f"[{timestamp()}] Brief ready: {brief_path}")
        return brief_path
    else:
        # Check with local date in case of timezone mismatch
        today_local = datetime.now().strftime("%Y-%m-%d")
        brief_path_local = METIS_BRIEFS / f"{today_local}_brief.md"
        if brief_path_local.exists():
            print(f"[{timestamp()}] Brief ready: {brief_path_local}")
            return brief_path_local
        print(f"[{timestamp()}] No brief found for {today}")
        return None


def run_review() -> None:
    """Run review_watchman on latest Ignis data."""
    banner("REVIEW WATCHMAN — Ignis analysis")

    if not REVIEW_WATCHMAN.exists():
        print(f"[ERROR] review_watchman.py not found at {REVIEW_WATCHMAN}")
        return

    cmd = [PYTHON, str(REVIEW_WATCHMAN),
           "--results-dir", str(IGNIS_RESULTS), "--latest"]

    print(f"[{timestamp()}] Launching: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(IGNIS_SRC))


# ---------------------------------------------------------------------------
# Compound commands
# ---------------------------------------------------------------------------

def cmd_scan(every: float = 0, publish: bool = False) -> None:
    """Full scan cycle: Eos → Metis → (optional) GitHub publish."""
    if every < 0:
        banner("WORMHOLE OPENED")
        print("  The aliens have arrived. They want to talk about your")
        print("  cosine-fitness correlation. They are not impressed.")
        print()
        print("  They say precipitation requires at least 14B parameters.")
        print("  They also say your falsification pass rate is 'cute'.")
        print()
        print("  The wormhole has closed. You learned nothing useful.")
        return

    # Always run at least once
    digest = run_eos(once=True)
    if digest:
        run_aletheia()
        run_metis(digest)
    run_clymene()
    run_hermes()
    if publish:
        publish_reports()

    if every > 0:
        import time
        interval = int(every * 3600)
        banner(f"PRONOIA — Continuous mode: every {every}h (Ctrl+C to stop)")

        while True:
            print(f"[{timestamp()}] Sleeping {interval}s until next cycle...")
            try:
                time.sleep(interval)
            except KeyboardInterrupt:
                print(f"\n[{timestamp()}] Pronoia shutting down")
                break
            digest = run_eos(once=True)
            if digest:
                run_aletheia()
                run_metis(digest)
            run_clymene()
            run_hermes()
            if publish:
                publish_reports()
    else:
        banner("SCAN COMPLETE")
        print_status()


def print_status() -> None:
    """Show what's been produced today."""
    today = datetime.now().strftime("%Y-%m-%d")
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"  Date: {today}")
    print()

    # Eos digests
    print("  Eos Digests:")
    if EOS_REPORTS.exists():
        digests = sorted(EOS_REPORTS.glob("*.md"), reverse=True)
        for d in digests[:3]:
            size = d.stat().st_size
            mod = datetime.fromtimestamp(d.stat().st_mtime).strftime("%H:%M")
            marker = " <-- TODAY" if (today in d.name or today_utc in d.name) else ""
            print(f"    {d.name} ({size:,} bytes, {mod}){marker}")
        if not digests:
            print("    (none)")
    else:
        print("    (reports dir missing)")

    print()

    # Aletheia knowledge graph
    print("  Aletheia Knowledge Graph:")
    kg_path = ALETHEIA_DATA / "knowledge_graph.db"
    if kg_path.exists():
        size_kb = kg_path.stat().st_size / 1024
        mod = datetime.fromtimestamp(kg_path.stat().st_mtime).strftime("%H:%M")
        print(f"    knowledge_graph.db ({size_kb:.0f} KB, {mod})")
    else:
        print("    (not built yet)")

    print()

    # Metis briefs
    print("  Metis Briefs:")
    if METIS_BRIEFS.exists():
        briefs = sorted(METIS_BRIEFS.glob("*.md"), reverse=True)
        for b in briefs[:3]:
            size = b.stat().st_size
            mod = datetime.fromtimestamp(b.stat().st_mtime).strftime("%H:%M")
            marker = " <-- TODAY" if (today in b.name or today_utc in b.name) else ""
            print(f"    {b.name} ({size:,} bytes, {mod}){marker}")
        if not briefs:
            print("    (none)")
    else:
        print("    (briefs dir missing)")

    print()

    # Clymene hoard reports
    print("  Clymene Hoard Reports:")
    if CLYMENE_REPORTS.exists():
        reports = sorted(CLYMENE_REPORTS.glob("*.md"), reverse=True)
        for r in reports[:3]:
            size = r.stat().st_size
            mod = datetime.fromtimestamp(r.stat().st_mtime).strftime("%H:%M")
            marker = " <-- TODAY" if (today in r.name or today_utc in r.name) else ""
            print(f"    {r.name} ({size:,} bytes, {mod}){marker}")
        if not reports:
            print("    (none)")
    else:
        print("    (no reports yet)")

    # Clymene cooldown status
    if CLYMENE_LAST_RUN.exists():
        try:
            last = datetime.fromisoformat(
                CLYMENE_LAST_RUN.read_text(encoding="utf-8").strip()
            )
            elapsed = (datetime.now(timezone.utc) - last).total_seconds() / 3600
            next_in = max(0, CLYMENE_COOLDOWN_HOURS - elapsed)
            print(f"    Next run in: {next_in:.1f}h")
        except (ValueError, OSError):
            pass
    else:
        print("    Never run — will run on next scan cycle")

    print()

    # Ignis results
    print("  Ignis Results:")
    if IGNIS_RESULTS.exists():
        # RPH evals
        rph_evals = sorted(IGNIS_RESULTS.glob("rph_eval_*.json"), reverse=True)
        for r in rph_evals[:3]:
            mod = datetime.fromtimestamp(r.stat().st_mtime).strftime("%H:%M")
            print(f"    {r.name} ({mod})")

        # Delta proj
        dp_files = sorted(IGNIS_RESULTS.glob("delta_proj_*.json"), reverse=True)
        for d in dp_files[:3]:
            mod = datetime.fromtimestamp(d.stat().st_mtime).strftime("%H:%M")
            print(f"    {d.name} ({mod})")

        if not rph_evals and not dp_files:
            print("    (no eval results)")

        # Watchman
        watchman_digest = IGNIS_RESULTS / "watchman" / "digest_latest.md"
        if watchman_digest.exists():
            mod = datetime.fromtimestamp(watchman_digest.stat().st_mtime).strftime("%H:%M")
            print(f"    watchman/digest_latest.md ({mod})")
    else:
        print("    (results dir missing)")

    # Multilayer results
    multilayer_dir = IGNIS_SRC / "results" / "ignis_multilayer"
    if multilayer_dir.exists():
        subdirs = [d for d in multilayer_dir.iterdir() if d.is_dir() and d.name.startswith("qwen")]
        if subdirs:
            print()
            print("  Multi-Layer Run:")
            for d in sorted(subdirs):
                jsonl = d / "discovery_log.jsonl"
                if jsonl.exists():
                    lines = sum(1 for _ in open(jsonl, encoding="utf-8"))
                    print(f"    {d.name}: {lines} genomes")
                else:
                    print(f"    {d.name}: (no data yet)")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Pronoia — The Forethought Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Commands:
  scan      Eos scan → Metis brief (full cycle)
  eos       Eos scan only
  metis     Metis analysis only (uses latest digest)
  status    Show what's been produced
  review    Run review_watchman on Ignis data
""")
    parser.add_argument("command", nargs="?", default="status",
                        choices=["scan", "eos", "metis", "status", "review"],
                        help="Command to run (default: status)")
    parser.add_argument("--every", type=float, default=0, metavar="HOURS",
                        help="Repeat every N hours (0=once, -1=wormhole). e.g. --every 2")
    parser.add_argument("--publish", action="store_true",
                        help="Push reports to GitHub after each cycle (read on phone)")
    args = parser.parse_args()

    sep = "=" * 62
    print(f"{sep}")
    print(f"  PRONOIA — The Forethought Orchestrator")
    print(f"  She who thinks ahead so you don't have to.")
    print(f"{sep}")

    if args.command == "scan":
        cmd_scan(every=args.every, publish=args.publish)
    elif args.command == "eos":
        run_eos(once=True)
    elif args.command == "metis":
        run_metis()
    elif args.command == "review":
        run_review()
    elif args.command == "status":
        print()
        print_status()


if __name__ == "__main__":
    main()
