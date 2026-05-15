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
LOG_PATH = REPO_ROOT / "dashboard" / "intelligence_loop.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

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
                        help="Skip daily email digest")
    parser.add_argument("--no-metis", action="store_true",
                        help="Skip LLM brief generation (structural state only)")
    parser.add_argument("--immediate", action="store_true",
                        help="Run the hourly cycle once on startup before settling into cadence")
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

    # ── Main tick loop ─────────────────────────────────────────────
    try:
        while True:
            now = datetime.now(timezone.utc)

            # Hourly: monitor + metis
            if now >= next_hourly:
                log.info("[hourly] firing portfolio cycle")
                ok_monitor = run_script("portfolio_monitor.py", ["--once"], timeout=120)
                ok_metis = True
                if not args.no_metis:
                    ok_metis = run_script("metis_portfolio.py", [], timeout=300)
                if agora_client:
                    try:
                        agora_client.send(
                            stream="main",
                            subject=f"Portfolio cycle complete (mon={ok_monitor}, metis={ok_metis})",
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
            if (not args.no_email and last_daily_date != today
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
