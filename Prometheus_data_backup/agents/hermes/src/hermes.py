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

# Structured logging
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from shared.structured_log import get_logger as _get_slog
    _slog = _get_slog("hermes", log_dir=Path(__file__).resolve().parent.parent / "logs")
except ImportError:
    _slog = None

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

# Forge pipeline paths
HEPH_LEDGER = PROMETHEUS_ROOT / "agents" / "hephaestus" / "ledger.jsonl"
HEPH_FORGE_DIR = PROMETHEUS_ROOT / "agents" / "hephaestus" / "forge"
NEMESIS_GRID = PROMETHEUS_ROOT / "agents" / "nemesis" / "grid" / "grid.json"
NEMESIS_REPORTS = PROMETHEUS_ROOT / "agents" / "nemesis" / "reports"
COEUS_GRAPH = PROMETHEUS_ROOT / "agents" / "coeus" / "graphs" / "concept_scores.json"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [HERMES] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("hermes")

# Load .env — root .env first, then eos/.env fallback
for _env_file in [PROMETHEUS_ROOT / ".env", PROMETHEUS_ROOT / "agents" / "eos" / ".env"]:
    if _env_file.exists():
        for line in _env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break  # use first found


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
    """SHA-256 hash of content, ignoring timestamps, dates, and volatile stats.

    The goal is to make the hash change ONLY when the actual findings change,
    not when scan counts, timestamps, or formatting differ between cycles.
    """
    import re
    normalized = text
    # Strip timestamps: HH:MM, HH:MM:SS, ISO datetimes
    normalized = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?Z?", "", normalized)
    normalized = re.sub(r"\d{2}:\d{2}(:\d{2})?", "", normalized)
    # Strip dates: YYYY-MM-DD
    normalized = re.sub(r"\d{4}-\d{2}-\d{2}", "", normalized)
    # Strip Hermes compile line
    normalized = re.sub(r"Compiled by Hermes at .*", "", normalized)
    # Strip scan/cycle statistics that change every run
    normalized = re.sub(r"Scanned \d+ (?:papers|repos|items|results)", "", normalized)
    normalized = re.sub(r"\d+ new,\s*\d+ known", "", normalized)
    normalized = re.sub(r"Total:?\s*\d+", "", normalized)
    normalized = re.sub(r"Rate limit.*", "", normalized)
    # Strip forge pipeline stats that change continuously (counts, rates)
    normalized = re.sub(r"Forge rate:?\s*[\d.]+%", "", normalized)
    normalized = re.sub(r"\d+ forged,\s*\d+ scrapped", "", normalized)
    normalized = re.sub(r"Grid:?\s*\d+/\d+", "", normalized)
    # Collapse whitespace
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

def _collect_audit_summary() -> str | None:
    """Run the Auditor agent and collect pipeline health summary."""
    auditor_script = PROMETHEUS_ROOT / "agents" / "auditor" / "src" / "auditor.py"
    if not auditor_script.exists():
        return None
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(auditor_script), "--json"],
            capture_output=True, text=True, timeout=30,
            cwd=str(auditor_script.parent),
        )
        if result.returncode != 0:
            return None
        report = json.loads(result.stdout)

        lines = [
            "## Pipeline Health",
            "",
            f"**Status: {report.get('overall_status', 'unknown').upper()}**",
            "",
        ]

        # Agent status table
        agents = report.get("agents", {})
        if agents:
            lines.append("| Agent | Status | Last Activity |")
            lines.append("|-------|--------|---------------|")
            for name, a in agents.items():
                last = (a.get("last_activity") or "—")[:19]
                lines.append(f"| {a.get('display', name)} | {a['status']} | {last} |")
            lines.append("")

        # Alerts
        alerts = report.get("alerts", [])
        if alerts:
            lines.append("### Alerts")
            lines.append("")
            for alert in alerts[:5]:
                lines.append(f"- {alert}")
            lines.append("")

        return "\n".join(lines)
    except Exception as e:
        log.warning(f"Auditor failed: {e}")
        return None


def _collect_forge_summary() -> str | None:
    """Build a forge pipeline summary from live data.

    Reports: tool counts, architecture era, battery coverage, top tools,
    Nemesis grid, recent activity.
    """
    lines = []
    from pathlib import Path as _P

    # Count tools across all forge directories
    forge_root = PROMETHEUS_ROOT / "agents" / "hephaestus"
    total_py = 0
    for d in sorted(forge_root.glob("forge*")):
        if d.is_dir():
            n = len(list(d.glob("*.py")))
            total_py += n

    # Hephaestus ledger stats
    if HEPH_LEDGER.exists():
        try:
            with open(HEPH_LEDGER, encoding="utf-8") as f:
                entries = [json.loads(l) for l in f]
            forged = [e for e in entries if e.get("status") == "forged"]
            total = len(entries)
            rate = (len(forged) / total * 100) if total else 0

            lines.append("## Forge Pipeline Status")
            lines.append("")
            lines.append(f"- **{total_py} tool files** across all forge directories")
            lines.append(f"- Ledger: {len(forged)} forged / {total} attempts ({rate:.1f}% rate)")
            lines.append(f"- **Architecture: computation-first (Frame E/F/G)**")
            lines.append(f"- Battery: 113 categories (89 Tier 1 + 24 Tier 2)")

            # Top 5 from ledger by accuracy
            top = sorted(forged, key=lambda x: x.get("accuracy", 0), reverse=True)[:5]
            if top:
                lines.append("")
                lines.append("### Top Performers (from ledger)")
                lines.append("")
                lines.append("| Tool | Accuracy | Margin over NCD |")
                lines.append("|------|----------|-----------------|")
                for t in top:
                    name = t.get("key", "?")
                    acc = t.get("accuracy", 0) * 100
                    m_acc = t.get("margin_accuracy", 0) * 100
                    lines.append(f"| {name} | {acc:.0f}% | +{m_acc:.0f}% |")

            # Note: v7 Opus tools not in ledger
            v7_count = len(list((forge_root / "forge_v7").glob("*.py"))) if (forge_root / "forge_v7").exists() else 0
            if v7_count:
                lines.append("")
                lines.append(f"### v7 Opus-Forged Tools: {v7_count} files")
                lines.append("- Best: ensemble_evaluator (0.734 weighted)")
                lines.append("- Best single: frame_e_v3_definitive (0.679 weighted)")
                lines.append("- Architecture: computation-first (parse → IR → compute → match)")

            # Recent forges (last 24h)
            from datetime import timedelta
            now = datetime.now(timezone.utc)
            cutoff = (now - timedelta(hours=24)).isoformat()
            recent = [e for e in forged if e.get("timestamp", "") > cutoff]
            if recent:
                lines.append("")
                lines.append(f"### New in last 24h: {len(recent)} tools forged")
                lines.append("")
                for r in sorted(recent, key=lambda x: x.get("accuracy", 0), reverse=True)[:5]:
                    name = r.get("key", "?")
                    acc = r.get("accuracy", 0) * 100
                    lines.append(f"- {name} ({acc:.0f}% acc)")

        except Exception as e:
            log.warning(f"Could not read Hephaestus ledger: {e}")

    # Nemesis grid status
    if NEMESIS_GRID.exists():
        try:
            grid = json.loads(NEMESIS_GRID.read_text(encoding="utf-8"))
            filled = grid.get("filled_cells", 0)
            total_cells = grid.get("total_cells", 100)
            lines.append("")
            lines.append(f"### Nemesis Adversarial Grid: {filled}/{total_cells} cells")
        except Exception as e:
            log.warning(f"Could not read Nemesis grid: {e}")

    # Latest Nemesis report (just the summary section)
    if NEMESIS_REPORTS.exists():
        try:
            reports = sorted(NEMESIS_REPORTS.glob("nemesis_report_*.md"), reverse=True)
            if reports:
                report_text = reports[0].read_text(encoding="utf-8")
                # Extract just the Goodhart gap table if present
                if "Goodhart" in report_text or "goodhart" in report_text:
                    lines.append("")
                    lines.append("*Nemesis: Goodhart signals detected — see full report*")
        except Exception as e:
            log.warning(f"Could not read Nemesis reports: {e}")

    # Coeus top drivers
    if COEUS_GRAPH.exists():
        try:
            scores = json.loads(COEUS_GRAPH.read_text(encoding="utf-8"))
            influences = scores.get("concept_influence", {})
            top_drivers = sorted(
                ((k, v.get("forge_effect", 0)) for k, v in influences.items()),
                key=lambda x: x[1], reverse=True
            )[:5]
            if top_drivers:
                lines.append("")
                lines.append("### Coeus Top Forge Drivers")
                lines.append("")
                for name, effect in top_drivers:
                    lines.append(f"- {name}: +{effect:.3f}")
        except Exception as e:
            log.warning(f"Could not read Coeus scores: {e}")

    if not lines:
        return None
    return "\n".join(lines)


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

    # Pipeline health audit (Auditor agent)
    audit_summary = _collect_audit_summary()
    if audit_summary:
        sections["pipeline_audit"] = audit_summary
        log.info("Collected pipeline health audit")
    else:
        log.info("No audit data available")

    # Forge pipeline summary
    forge_summary = _collect_forge_summary()
    if forge_summary:
        sections["forge_pipeline"] = forge_summary
        log.info("Collected forge pipeline summary")
    else:
        log.info("No forge pipeline data available")

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

    # Constitutional substrate health (Law 1 enforcement)
    try:
        _ingest_path = str(Path(__file__).resolve().parent.parent.parent / "aletheia" / "src")
        if _ingest_path not in sys.path:
            sys.path.insert(0, _ingest_path)
        from ingest import get_substrate_health
        health = get_substrate_health(hours=24)
        total_24h = health["entities_24h"] + health["relationships_24h"] + health["gaps_24h"]
        status = "HEALTHY" if total_24h >= 5 else "STARVATION"
        lines = [
            "## Constitutional Substrate Health", "",
            f"**Status: {status}** (last 24h)",
            f"- Entities added: {health['entities_24h']}",
            f"- Relationships added: {health['relationships_24h']}",
            f"- Gaps identified: {health['gaps_24h']}",
            f"- **Total growth: {total_24h}** (minimum: 5)", "",
            f"Substrate totals: {health['total_entities']} entities, "
            f"{health['total_relationships']} relationships, "
            f"{health['open_gaps']} open gaps",
        ]
        if status == "STARVATION":
            lines.append("")
            lines.append("**LAW 1 VIOLATION: The substrate is the product. Run intelligence pipeline before GPU experiments.**")
        sections["substrate_health"] = "\n".join(lines)
        log.info(f"Substrate health: {status} ({total_24h} additions in 24h)")
    except Exception as e:
        log.warning(f"Could not check substrate health (non-fatal): {e}")

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

    # Pipeline health audit (first after Metis — James sees health status immediately)
    if "pipeline_audit" in include:
        parts.append("---")
        parts.append("")
        parts.append(include["pipeline_audit"])
        parts.append("")

    # Forge pipeline (after audit, before supporting detail)
    if "forge_pipeline" in include:
        parts.append("---")
        parts.append("")
        parts.append(include["forge_pipeline"])
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

def _markdown_to_html(md: str) -> str:
    """Convert markdown digest to styled HTML for Gmail readability."""
    import re as _re
    lines = md.split("\n")
    html_parts = [
        "<html><head><style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; ",
        "  max-width: 700px; margin: 0 auto; padding: 20px; color: #333; line-height: 1.5; }",
        "h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 8px; font-size: 22px; }",
        "h2 { color: #2980b9; font-size: 18px; margin-top: 24px; }",
        "h3 { color: #7f8c8d; font-size: 15px; margin-top: 16px; }",
        "table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }",
        "th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; }",
        "th { background: #f5f6fa; font-weight: 600; }",
        "hr { border: none; border-top: 1px solid #eee; margin: 20px 0; }",
        "code { background: #f5f6fa; padding: 2px 5px; border-radius: 3px; font-size: 13px; }",
        ".meta { color: #95a5a6; font-size: 13px; font-style: italic; }",
        "ul { padding-left: 20px; }",
        "li { margin-bottom: 6px; }",
        "strong { color: #2c3e50; }",
        "</style></head><body>",
    ]

    in_table = False
    for line in lines:
        stripped = line.strip()
        # Horizontal rule
        if stripped == "---":
            if in_table:
                html_parts.append("</table>")
                in_table = False
            html_parts.append("<hr>")
            continue
        # Table rows
        if "|" in stripped and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(c.replace("-", "").replace(":", "") == "" for c in cells):
                continue  # Skip separator row
            if not in_table:
                html_parts.append("<table>")
                in_table = True
                tag = "th"
            else:
                tag = "td"
            row = "".join(f"<{tag}>{c}</{tag}>" for c in cells)
            html_parts.append(f"<tr>{row}</tr>")
            continue
        if in_table and "|" not in stripped:
            html_parts.append("</table>")
            in_table = False
        # Headers
        if stripped.startswith("# "):
            html_parts.append(f"<h1>{stripped[2:]}</h1>")
        elif stripped.startswith("## "):
            html_parts.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("### "):
            html_parts.append(f"<h3>{stripped[4:]}</h3>")
        # Italic metadata lines
        elif stripped.startswith("*") and stripped.endswith("*") and len(stripped) > 2:
            html_parts.append(f"<p class='meta'>{stripped[1:-1]}</p>")
        # List items
        elif stripped.startswith("- "):
            content = stripped[2:]
            # Bold inline
            content = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
            content = _re.sub(r'_(.+?)_', r'<em>\1</em>', content)
            html_parts.append(f"<li>{content}</li>")
        # Empty line
        elif not stripped:
            continue
        # Regular text
        else:
            content = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
            content = _re.sub(r'_(.+?)_', r'<em>\1</em>', content)
            html_parts.append(f"<p>{content}</p>")

    if in_table:
        html_parts.append("</table>")
    html_parts.append("</body></html>")
    return "\n".join(html_parts)


def send_email(subject: str, body_markdown: str, config: dict) -> bool:
    """Send digest email via Gmail SMTP with both HTML and plain text."""
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

    # Plain text version (fallback)
    msg.attach(MIMEText(body_markdown, "plain", "utf-8"))

    # HTML version (preferred by Gmail)
    try:
        html_body = _markdown_to_html(body_markdown)
        msg.attach(MIMEText(html_body, "html", "utf-8"))
    except Exception as e:
        log.warning(f"HTML conversion failed, sending plain text only: {e}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(address, password)
            server.sendmail(address, [recipient], msg.as_string())
        log.info(f"Email sent to {recipient} (HTML + plain text)")
        if _slog:
            _slog.event("email_sent", recipient=recipient, subject=msg["Subject"],
                        body_length=len(body_markdown), html=True)
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
    if _slog:
        _slog.event("cycle_start")
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

    if _slog:
        _slog.event("cycle_complete", sections_collected=len(sections),
                     new_sections=len(new_sections) if new_sections else 0,
                     email_sent=should_email if 'should_email' in dir() else False)
    log.info("Done.")


if __name__ == "__main__":
    main()
