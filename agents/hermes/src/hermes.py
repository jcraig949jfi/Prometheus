"""
Hermes — The Messenger

Collects reports from all Prometheus agents in the current cycle,
compiles a unified digest, and emails it via Gmail SMTP.

Dedup: tracks content hashes of each section. Only sends an email when
at least one section has genuinely new content since the last send.

Usage:
    python hermes.py --once              # Collect + email (only if new content)
    python hermes.py --collect           # Collect digest only (no email)
    python hermes.py --force             # Collect + email even if no new content
    python hermes.py --test-email        # Send a test email to verify config
"""

import argparse
import hashlib
import json
import logging
import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERMES_ROOT = Path(__file__).resolve().parent.parent
PROMETHEUS_ROOT = HERMES_ROOT.parent.parent
DIGESTS_DIR = HERMES_ROOT / "digests"
CONFIG_PATH = HERMES_ROOT / "config.json"
SENT_STATE_PATH = HERMES_ROOT / "data" / "sent_state.json"

# Agent output locations
EOS_REPORTS = PROMETHEUS_ROOT / "agents" / "eos" / "reports"
ALETHEIA_DATA = PROMETHEUS_ROOT / "agents" / "aletheia" / "data"
METIS_BRIEFS = PROMETHEUS_ROOT / "agents" / "metis" / "briefs"
CLYMENE_REPORTS = PROMETHEUS_ROOT / "agents" / "clymene" / "reports"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [HERMES] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("hermes")

# Load .env from eos (shared API keys)
_env_file = PROMETHEUS_ROOT / "agents" / "eos" / ".env"
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    """Load Hermes config. Environment variables override config.json."""
    base = {}
    if CONFIG_PATH.exists():
        try:
            base = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    # Environment variables always win over config.json
    return {
        "gmail_address": os.environ.get("HERMES_GMAIL_ADDRESS") or base.get("gmail_address", ""),
        "gmail_app_password": os.environ.get("HERMES_GMAIL_APP_PASSWORD") or base.get("gmail_app_password", ""),
        "recipient": os.environ.get("HERMES_RECIPIENT") or base.get("recipient", ""),
        "enabled": (os.environ.get("HERMES_ENABLED", "").lower() == "true") or base.get("enabled", False),
    }


def save_default_config() -> None:
    """Write a template config file if none exists."""
    if CONFIG_PATH.exists():
        return
    template = {
        "gmail_address": "",
        "gmail_app_password": "",
        "recipient": "",
        "enabled": False,
        "_instructions": (
            "1. Go to myaccount.google.com → Security → 2-Step Verification → App passwords. "
            "2. Generate an app password for 'Prometheus Hermes'. "
            "3. Paste it into gmail_app_password. "
            "4. Set gmail_address to your Gmail. "
            "5. Set recipient to where you want digests sent. "
            "6. Set enabled to true. "
            "Alternatively, set HERMES_GMAIL_ADDRESS, HERMES_GMAIL_APP_PASSWORD, "
            "and HERMES_RECIPIENT as environment variables or in agents/eos/.env."
        ),
    }
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(template, indent=2), encoding="utf-8")
    log.info(f"Template config written to {CONFIG_PATH}")
    log.info("Fill in Gmail credentials and set enabled=true to activate email delivery.")


# ---------------------------------------------------------------------------
# Sent-state tracking (dedup)
# ---------------------------------------------------------------------------

def _content_hash(text: str) -> str:
    """SHA-256 hash of content, ignoring timestamps and whitespace variance."""
    # Normalize: strip lines, collapse whitespace, remove time-specific tokens
    import re
    normalized = re.sub(r"\d{2}:\d{2}(:\d{2})?", "", text)  # strip HH:MM(:SS)
    normalized = re.sub(r"Compiled by Hermes at .*", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def load_sent_state() -> dict:
    """Load the record of what was last sent."""
    if SENT_STATE_PATH.exists():
        try:
            return json.loads(SENT_STATE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"section_hashes": {}, "last_sent": None, "send_count": 0}


def save_sent_state(state: dict) -> None:
    """Persist sent state."""
    SENT_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SENT_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def diff_sections(sections: dict, sent_state: dict) -> dict:
    """
    Compare current sections against last-sent hashes.
    Returns only sections with new content.
    """
    old_hashes = sent_state.get("section_hashes", {})
    new_sections = {}

    for key, content in sections.items():
        current_hash = _content_hash(content)
        if old_hashes.get(key) != current_hash:
            new_sections[key] = content
            log.info(f"  [{key}] NEW content (hash changed)")
        else:
            log.info(f"  [{key}] unchanged — skipping")

    return new_sections


# ---------------------------------------------------------------------------
# Digest collection
# ---------------------------------------------------------------------------

def find_todays_file(directory: Path, pattern: str) -> Path | None:
    """Find a file matching today's date in the given directory."""
    today = datetime.now().strftime("%Y-%m-%d")
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not directory.exists():
        return None

    for f in sorted(directory.glob(pattern), reverse=True):
        if today in f.name or today_utc in f.name:
            return f
    return None


def collect_digest() -> dict:
    """
    Gather today's outputs from all agents.
    Returns a dict with section name → content.
    """
    sections = {}

    # Metis brief (most important — lead with this)
    brief = find_todays_file(METIS_BRIEFS, "*_brief.md")
    if brief:
        sections["metis_brief"] = brief.read_text(encoding="utf-8")
        log.info(f"Collected Metis brief: {brief.name}")
    else:
        log.info("No Metis brief found for today")

    # Eos digest
    digest = find_todays_file(EOS_REPORTS, "*.md")
    if digest:
        content = digest.read_text(encoding="utf-8")
        # Truncate Eos digest to keep email reasonable (first 3000 chars)
        if len(content) > 3000:
            content = content[:3000] + "\n\n... [truncated — full digest on GitHub]"
        sections["eos_digest"] = content
        log.info(f"Collected Eos digest: {digest.name}")
    else:
        log.info("No Eos digest found for today")

    # Clymene hoard report
    hoard = find_todays_file(CLYMENE_REPORTS, "*_hoard.md")
    if hoard:
        sections["clymene_report"] = hoard.read_text(encoding="utf-8")
        log.info(f"Collected Clymene report: {hoard.name}")
    else:
        log.info("No Clymene report for today (cooldown or not run)")

    # Aletheia knowledge graph stats
    kg_path = ALETHEIA_DATA / "knowledge_graph.db"
    if kg_path.exists():
        import sqlite3
        try:
            conn = sqlite3.connect(str(kg_path))
            counts = {}
            for table in ["techniques", "reasoning_motifs", "tools", "terms", "claims"]:
                try:
                    row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                    counts[table] = row[0] if row else 0
                except sqlite3.OperationalError:
                    pass
            conn.close()
            if counts:
                lines = ["## Aletheia Knowledge Graph", ""]
                for table, count in counts.items():
                    lines.append(f"- **{table}:** {count} entries")
                sections["aletheia_stats"] = "\n".join(lines)
                log.info(f"Collected Aletheia stats: {counts}")
        except Exception as e:
            log.warning(f"Could not read Aletheia DB: {e}")

    return sections


def format_digest(sections: dict, new_only: dict = None) -> str:
    """
    Format collected sections into a single digest document.
    If new_only is provided, marks which sections have new content.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    parts = [
        f"# Prometheus Cycle Digest — {today}",
        "",
        f"*Compiled by Hermes at {datetime.now().strftime('%H:%M')}*",
    ]

    if new_only is not None:
        changed = list(new_only.keys())
        if changed:
            parts.append(f"*New content in: {', '.join(changed)}*")
    parts.append("")

    if not sections:
        parts.append("No agent outputs found for today. Pipeline may not have run.")
        return "\n".join(parts)

    # Only include sections that have new content (if filtering)
    include = new_only if new_only is not None else sections

    # Metis brief first (the executive summary)
    if "metis_brief" in include:
        parts.append("---")
        parts.append("")
        parts.append(include["metis_brief"])
        parts.append("")

    # Aletheia stats (only if changed)
    if "aletheia_stats" in include:
        parts.append("---")
        parts.append("")
        parts.append(include["aletheia_stats"])
        parts.append("")

    # Clymene report (only if changed)
    if "clymene_report" in include:
        parts.append("---")
        parts.append("")
        parts.append(include["clymene_report"])
        parts.append("")

    # Eos digest (only if changed, truncated, at the end)
    if "eos_digest" in include:
        parts.append("---")
        parts.append("")
        parts.append("## Eos Raw Findings (truncated)")
        parts.append("")
        parts.append(include["eos_digest"])
        parts.append("")

    return "\n".join(parts)


def save_digest(content: str) -> Path:
    """Save digest to digests/ directory."""
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    ts = datetime.now().strftime("%H%M")
    path = DIGESTS_DIR / f"{today}_{ts}_digest.md"
    path.write_text(content, encoding="utf-8")
    log.info(f"Digest saved: {path}")
    return path


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

def send_email(subject: str, body_markdown: str, config: dict) -> bool:
    """Send digest email via Gmail SMTP."""
    address = config.get("gmail_address", "")
    password = config.get("gmail_app_password", "")
    recipient = config.get("recipient", "") or address  # Default: send to self

    if not address or not password:
        log.warning("Gmail credentials not configured — skipping email")
        log.info("Run with --test-email after configuring config.json")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Prometheus Hermes <{address}>"
    msg["To"] = recipient

    # Plain text version (markdown is readable as plain text)
    msg.attach(MIMEText(body_markdown, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(address, password)
            server.sendmail(address, [recipient], msg.as_string())
        log.info(f"Email sent to {recipient}")
        return True
    except smtplib.SMTPAuthenticationError:
        log.error(
            "Gmail authentication failed. Make sure you're using an App Password, "
            "not your regular password. See: myaccount.google.com → Security → "
            "2-Step Verification → App passwords"
        )
        return False
    except Exception as e:
        log.error(f"Email failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Hermes — collect agent reports and email digest",
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Collect digest and email it (only if new content)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Collect + email even if no new content",
    )
    parser.add_argument(
        "--collect", action="store_true",
        help="Collect digest only (no email)",
    )
    parser.add_argument(
        "--test-email", action="store_true",
        help="Send a test email to verify config",
    )
    args = parser.parse_args()

    # Ensure config template exists
    save_default_config()
    config = load_config()

    if args.test_email:
        log.info("Sending test email...")
        success = send_email(
            subject="Prometheus Hermes — Test Email",
            body_markdown=(
                "# Test Email\n\n"
                "If you're reading this, Hermes is configured correctly.\n\n"
                f"*Sent at {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
            ),
            config=config,
        )
        sys.exit(0 if success else 1)

    if not args.once and not args.collect and not args.force:
        parser.print_help()
        sys.exit(1)

    # Collect all sections
    log.info("Collecting agent outputs...")
    sections = collect_digest()

    if not sections:
        log.info("Nothing to report — no agent outputs found for today")
        return

    # Dedup: compare against last sent
    sent_state = load_sent_state()
    log.info("Checking for new content...")
    new_sections = diff_sections(sections, sent_state)

    if not new_sections and not args.force:
        log.info("No new content since last send — skipping email")
        log.info(f"(Last sent: {sent_state.get('last_sent', 'never')}, "
                 f"total sends: {sent_state.get('send_count', 0)})")
        return

    if args.force and not new_sections:
        log.info("No new content, but --force specified — sending anyway")
        new_sections = sections

    # Format digest with only new content
    digest_text = format_digest(sections, new_only=new_sections)
    digest_path = save_digest(digest_text)

    # Email (if --once/--force and email is configured)
    should_email = (args.once or args.force) and config.get("enabled", False)
    if should_email:
        today = datetime.now().strftime("%Y-%m-%d")
        changed_names = list(new_sections.keys())
        subject = f"Prometheus Digest — {today}"

        # Add urgency hint if Metis has new "Act on this" items
        metis_text = new_sections.get("metis_brief", "")
        if "act on this" in metis_text.lower():
            subject = f"[ACTION] {subject}"

        # Add summary of what changed
        if len(changed_names) < len(sections):
            short = ", ".join(k.replace("_", " ").title() for k in changed_names)
            subject = f"{subject} ({short})"

        sent = send_email(subject, digest_text, config)

        if sent:
            # Update sent state with current hashes
            new_hashes = {k: _content_hash(v) for k, v in sections.items()}
            sent_state["section_hashes"] = new_hashes
            sent_state["last_sent"] = datetime.now(timezone.utc).isoformat()
            sent_state["send_count"] = sent_state.get("send_count", 0) + 1
            save_sent_state(sent_state)
            log.info(f"Sent state updated ({len(new_hashes)} section hashes saved)")
    elif args.once or args.force:
        log.info("Email not enabled — digest saved locally only")
        log.info(f"Configure {CONFIG_PATH} to enable email delivery")

    log.info("Done.")


if __name__ == "__main__":
    main()
