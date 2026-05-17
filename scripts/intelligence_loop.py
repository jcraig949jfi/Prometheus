#!/usr/bin/env python3
"""
Intelligence Loop — Pronoia-orchestrator for the multi-machine reporting pipeline.

Runs on M4 (or wherever launched). Fires three sub-pipelines on different
cadences, with a single Agora heartbeat thread keeping `agent:Pronoia` alive
on the dashboard:

  every hour:   portfolio_monitor.py --once  (refresh dashboard/state.json)
                metis_portfolio.py           (LLM brief -> dashboard/portfolio_brief.md)
  every day:    send_brief_email.py          (Gmail digest at the configured hour)
  every 60s:    Agora heartbeat              (so the loop appears ALIVE)

Usage:
    python scripts/intelligence_loop.py
    python scripts/intelligence_loop.py --hourly-min 30
    python scripts/intelligence_loop.py --daily-hour 8 --daily-minute 0
    python scripts/intelligence_loop.py --no-email
    python scripts/intelligence_loop.py --no-metis   # structural state only, skip LLM

Background launch (Windows, no console window):
    pythonw scripts/intelligence_loop.py
    OR: double-click scripts/start_intelligence_loop.bat

The loop logs to dashboard/intelligence_loop.log. Ctrl+C to stop (won't work
under pythonw — kill via Task Manager or stop the .bat process).
"""
import argparse
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
LOG_PATH = REPO_ROOT / "docs" / "intelligence_loop.log"  # docs/* gitignored except the 3 dashboard files
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Git identity used for the auto-commits. Kept local to this script to avoid
# touching global git config; matches the noreply email pattern used elsewhere.
GIT_AUTHOR = ("-c", "user.name=James Craig",
              "-c", "user.email=jcraig949jfi@users.noreply.github.com")
DASHBOARD_FILES = ["docs/state.json", "docs/portfolio_brief.md"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [INTEL] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(LOG_PATH), encoding="utf-8"),
    ],
)
log = logging.getLogger("intelligence_loop")

# Make agora.* importable (gitignored at agents/ but agora/ also gitignored;
# falls through cleanly if absent and the loop runs without telemetry).
sys.path.insert(0, str(REPO_ROOT))
try:
    from agora.client import AgoraClient
    from agora.protocol import MessageType
    HAS_AGORA = True
except Exception as e:
    log.warning("Agora client unavailable (%s); loop will run without heartbeats", e)
    HAS_AGORA = False
    AgoraClient = None
    MessageType = None


def push_dashboard_to_main() -> bool:
    """Auto-commit + push docs/state.json + docs/portfolio_brief.md to main.

    Idempotent: no-op when there are no changes. Logs errors and never raises.
    Handles the remote-moved case with one pull --rebase --autostash retry.
    Returns True if the push succeeded or there was nothing to push.
    """
    def run(args, timeout=60):
        return subprocess.run(
            ["git", *GIT_AUTHOR, *args],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout,
        )

    # Are there actual changes?
    status = run(["status", "--porcelain", *DASHBOARD_FILES], timeout=15)
    if status.returncode != 0:
        log.error("  git status failed: %s", (status.stderr or "")[:200])
        return False
    if not status.stdout.strip():
        log.info("  no dashboard changes — push skipped")
        return True

    # Stage + commit (--only restricts commit to these paths regardless of other staged work)
    r = run(["add", *DASHBOARD_FILES], timeout=15)
    if r.returncode != 0:
        log.error("  git add failed: %s", (r.stderr or "")[:200])
        return False

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    msg = f"auto: portfolio update {ts}"
    r = run(["commit", "-m", msg], timeout=15)
    if r.returncode != 0:
        # "nothing to commit" race condition or other commit failure
        log.warning("  git commit rc=%d: %s", r.returncode, (r.stderr or r.stdout or "")[:200])
        return False

    # Push, with one rebase-retry on rejection
    r = run(["push", "origin", "main"], timeout=60)
    if r.returncode == 0:
        log.info("  ✓ pushed dashboard update to main (%s)", msg)
        return True

    log.warning("  push failed, attempting rebase: %s", (r.stderr or "")[:200])
    r = run(["pull", "--rebase", "--autostash"], timeout=60)
    if r.returncode != 0:
        log.error("  rebase failed: %s", (r.stderr or "")[:200])
        return False

    r = run(["push", "origin", "main"], timeout=60)
    if r.returncode == 0:
        log.info("  ✓ pushed dashboard update after rebase")
        return True

    log.error("  final push failed: %s", (r.stderr or "")[:200])
    return False


def run_script(name: str, args: list = None, timeout: int = 600) -> bool:
    """Run a sibling script in a subprocess. Inherits env. Returns True on success."""
    cmd = [sys.executable, str(SCRIPTS_DIR / name)] + (args or [])
    log.info("→ %s %s", name, " ".join(args or []))
    try:
        result = subprocess.run(
            cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode == 0:
            tail = (result.stdout or "").strip().splitlines()[-1:]
            log.info("  ✓ %s exit 0 %s", name, tail[0] if tail else "")
            return True
        log.error("  ✗ %s exit %d stderr=%s", name, result.returncode,
                  (result.stderr or "")[:300])
        return False
    except subprocess.TimeoutExpired:
        log.error("  ✗ %s timed out after %ds", name, timeout)
        return False
    except Exception as e:
        log.error("  ✗ %s exception: %s", name, e)
        return False


def main():
    parser = argparse.ArgumentParser(description="Intelligence loop — Pronoia orchestrator")
    parser.add_argument("--hourly-min", type=float, default=60.0,
                        help="Minutes between portfolio_monitor + metis_portfolio runs (default 60)")
    parser.add_argument("--daily-hour", type=int, default=8,
                        help="Hour (0-23) UTC to send daily email digest (default 8)")
    parser.add_argument("--daily-minute", type=int, default=0,
                        help="Minute (0-59) within daily-hour to send (default 0)")
    parser.add_argument("--no-email", action="store_true",
                        help="Skip email digest entirely")
    parser.add_argument("--email-every-cycle", action="store_true",
                        help="Fire send_brief_email.py at the end of every hourly cycle "
                             "(instead of just once per day at daily-hour). Useful when "
                             "--hourly-min is set to a multi-hour interval (e.g. 240 = 4h cadence).")
    parser.add_argument("--no-metis", action="store_true",
                        help="Skip LLM brief generation (structural state only)")
    parser.add_argument("--no-push", action="store_true",
                        help="Skip auto-commit + push of dashboard data to main (useful for testing)")
    parser.add_argument("--immediate", action="store_true",
                        help="Run the hourly cycle once on startup before settling into cadence")
    parser.add_argument("--weekly-recap-hour", type=int, default=22,
                        help="Hour (0-23) LOCAL TIME on Friday to fire weekly_recap.py (default 22, i.e. 10pm)")
    parser.add_argument("--no-weekly-recap", action="store_true",
                        help="Skip the Friday weekly recap")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("Intelligence loop starting on PID %d", os.getpid())
    log.info("Cadence: hourly every %.1fmin, daily at %02d:%02d UTC",
             args.hourly_min, args.daily_hour, args.daily_minute)
    log.info("=" * 60)

    # ── Agora connection ───────────────────────────────────────────
    agora_client = None
    machine = os.environ.get("PROMETHEUS_MACHINE", "M4")
    if HAS_AGORA:
        try:
            agora_client = AgoraClient(agent_name="Pronoia", machine=machine, persist=False)
            agora_client.connect()
            agora_client.start_heartbeat()
            agora_client.send(
                stream="main",
                subject="Pronoia online (intelligence loop)",
                body=f"Hourly synthesis + daily digest on {machine}. PID {os.getpid()}.",
                confidence=1.0,
                msg_type=MessageType.ANNOUNCE,
            )
            log.info("Agora connected as Pronoia@%s", machine)
        except Exception as e:
            log.warning("Agora unavailable: %s — continuing without telemetry", e)
            agora_client = None

    # ── State ──────────────────────────────────────────────────────
    next_hourly = datetime.now(timezone.utc)
    if not args.immediate:
        next_hourly += timedelta(minutes=args.hourly_min)
    last_daily_date = None  # set after first daily send
    last_weekly_recap_date = None  # set after first weekly recap fire

    # ── Main tick loop ─────────────────────────────────────────────
    try:
        while True:
            now = datetime.now(timezone.utc)

            # Hourly: monitor + metis (+ optional push to main for GitHub Pages)
            if now >= next_hourly:
                log.info("[hourly] firing portfolio cycle")
                ok_monitor = run_script("portfolio_monitor.py", ["--once"], timeout=120)
                ok_metis = True
                if not args.no_metis:
                    ok_metis = run_script("metis_portfolio.py", [], timeout=300)

                # Auto-publish to GitHub Pages by pushing the data files to main
                ok_push = True
                if not args.no_push and ok_monitor:
                    log.info("[hourly] pushing dashboard data to main")
                    ok_push = push_dashboard_to_main()

                # Optional: fire email on every hourly tick (rather than once-daily)
                ok_email_this_tick = None
                if args.email_every_cycle and not args.no_email and ok_metis:
                    log.info("[hourly] firing email digest (per --email-every-cycle)")
                    ok_email_this_tick = run_script("send_brief_email.py", [], timeout=60)

                if agora_client:
                    try:
                        agora_client.send(
                            stream="main",
                            subject=f"Portfolio cycle complete (mon={ok_monitor}, metis={ok_metis}, push={ok_push}, email={ok_email_this_tick})",
                            body=f"hourly tick {now.isoformat()}",
                            confidence=1.0,
                            msg_type=MessageType.ANNOUNCE,
                        )
                    except Exception:
                        pass
                next_hourly = now + timedelta(minutes=args.hourly_min)

            # Daily: email
            today = now.date()
            target_today = datetime(
                year=today.year, month=today.month, day=today.day,
                hour=args.daily_hour, minute=args.daily_minute, tzinfo=timezone.utc,
            )
            # If --email-every-cycle is set, skip the daily email path
            # (hourly path already fires email each tick).
            if (not args.no_email and not args.email_every_cycle
                    and last_daily_date != today
                    and now >= target_today):
                log.info("[daily] firing email digest")
                ok_email = run_script("send_brief_email.py", [], timeout=60)
                last_daily_date = today
                if agora_client:
                    try:
                        agora_client.send(
                            stream="main",
                            subject=f"Daily digest sent (ok={ok_email})",
                            body=f"daily email at {now.isoformat()}",
                            confidence=1.0,
                            msg_type=MessageType.ANNOUNCE,
                        )
                    except Exception:
                        pass

            # Weekly: fire weekly_recap.py every Friday at args.weekly_recap_hour LOCAL TIME.
            # weekday() returns 0=Monday ... 4=Friday ... 6=Sunday in local time.
            local_now = datetime.now()
            if (not args.no_weekly_recap
                    and local_now.weekday() == 4  # Friday
                    and local_now.hour >= args.weekly_recap_hour
                    and last_weekly_recap_date != local_now.date()):
                log.info("[weekly] firing weekly recap (Friday %02d:%02d local)",
                         local_now.hour, local_now.minute)
                ok_recap = run_script("weekly_recap.py", [], timeout=300)
                last_weekly_recap_date = local_now.date()
                if agora_client:
                    try:
                        agora_client.send(
                            stream="main",
                            subject=f"Weekly recap fired (ok={ok_recap})",
                            body=f"weekly recap at {now.isoformat()}",
                            confidence=1.0,
                            msg_type=MessageType.ANNOUNCE,
                        )
                    except Exception:
                        pass

            # Sleep until either next_hourly or 60s, whichever sooner
            sleep_s = min(60.0, max(1.0, (next_hourly - now).total_seconds()))
            time.sleep(sleep_s)

    except KeyboardInterrupt:
        log.info("SIGINT received — shutting down")
    finally:
        if agora_client:
            try:
                agora_client.send(stream="main", subject="Pronoia shutting down",
                                  body=f"clean exit at {datetime.now(timezone.utc).isoformat()}",
                                  confidence=1.0, msg_type=MessageType.ANNOUNCE)
                agora_client.disconnect()
            except Exception:
                pass
        log.info("Intelligence loop stopped")


if __name__ == "__main__":
    main()
