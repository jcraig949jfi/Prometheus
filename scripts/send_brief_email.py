#!/usr/bin/env python3
"""
Send the latest portfolio brief via Gmail SMTP.

Reads dashboard/portfolio_brief.md and emails it to HERMES_RECIPIENT.
Designed to run after metis_portfolio.py — typically as the daily digest
step in the hourly/daily reporting loop.

Credentials expected in agents/eos/.env (or as env vars):
- HERMES_GMAIL_ADDRESS — sender Gmail account
- HERMES_GMAIL_APP_PASSWORD — Gmail App Password (16 chars, generated at
  myaccount.google.com -> Security -> App passwords)
- HERMES_RECIPIENT — destination email (typically same as the sender)
- HERMES_ENABLED — set to "false" to disable sending (default enabled)

Usage:
    python scripts/send_brief_email.py
    python scripts/send_brief_email.py --subject "Custom subject"
    python scripts/send_brief_email.py --brief path/to/other.md
    python scripts/send_brief_email.py --dry-run    # print what would send, don't send
"""
import argparse
import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BRIEF = REPO_ROOT / "docs" / "portfolio_brief.md"  # GitHub Pages serves from main/docs

# --- GitHub link catalog -----------------------------------------------------
# Email is meant to be a router into the repo, not a self-contained report.
# Edit this registry as new agents / docs / pivot artifacts land.
GITHUB_REPO = "https://github.com/jcraig949jfi/Prometheus"
GITHUB_BLOB = f"{GITHUB_REPO}/blob/main"
GITHUB_TREE = f"{GITHUB_REPO}/tree/main"
GITHUB_COMMITS = f"{GITHUB_REPO}/commits/main"
PAGES_URL = "https://jcraig949jfi.github.io/Prometheus/"

# Per-agent reference docs. When the brief mentions an agent, these get
# surfaced in a "Mentioned in this brief" section above the static catalog.
AGENT_REFS = {
    "Hephaestus": [
        ("Hephaestus autopsy",        f"{GITHUB_BLOB}/pivot/autopsy_hephaestus_2026-05-13.md"),
        ("Hephaestus RESUME",         f"{GITHUB_BLOB}/pivot/agents_hephaestus_resume_2026-05-12.md"),
    ],
    "Apollo": [
        ("Apollo autopsy",            f"{GITHUB_BLOB}/pivot/autopsy_apollo_2026-05-13.md"),
        ("Apollo RESUME",             f"{GITHUB_BLOB}/apollo/RESUME.md"),
        ("Apollo v2.1 roadmap",       f"{GITHUB_BLOB}/apollo/ROADMAP.md"),
    ],
    "Nous": [
        ("Nous RESUME",               f"{GITHUB_BLOB}/pivot/agents_nous_resume_2026-05-13.md"),
    ],
    "Ergon": [
        ("Forge autopsies (consolidated, covers Learner context)",
                                       f"{GITHUB_BLOB}/pivot/autopsy_forges_consolidated_2026-05-13.md"),
    ],
    "Agora": [
        ("Agora architecture (in repo)", f"{GITHUB_TREE}/roles/Agora"),
    ],
}

# Always-on references. Top of the catalog is "Current cycle" — what this
# email's data came from. Then project-level frame docs and activity links.
STATIC_REFS = [
    ("Current cycle", [
        ("Live dashboard (GitHub Pages)",   PAGES_URL),
        ("Latest brief",                    f"{GITHUB_BLOB}/docs/portfolio_brief.md"),
        ("Dashboard state.json",            f"{GITHUB_BLOB}/docs/state.json"),
        ("Manual out-of-band status",       f"{GITHUB_BLOB}/docs/manual_status.json"),
    ]),
    ("Project frame", [
        ("Prometheus synthesis (thesis-level)",
                                            f"{GITHUB_BLOB}/pivot/prometheus_synthesis_2026-05-14.md"),
        ("Forge autopsies — consolidated",  f"{GITHUB_BLOB}/pivot/autopsy_forges_consolidated_2026-05-13.md"),
        ("Agent portfolio + monitoring design",
                                            f"{GITHUB_BLOB}/pivot/agent_portfolio_and_monitoring_2026-05-12.md"),
        ("Dashboard deployment plan",       f"{GITHUB_BLOB}/pivot/dashboard_deployment_plan_2026-05-15.md"),
    ]),
    ("Activity", [
        ("Recent commits on main",          GITHUB_COMMITS),
        ("All pivot docs",                  f"{GITHUB_TREE}/pivot"),
        ("All scripts",                     f"{GITHUB_TREE}/scripts"),
    ]),
]


def find_brief_mentions(brief_md: str) -> dict:
    """Return AGENT_REFS entries whose agent name appears in the brief text.
    Lets the email surface relevant docs first."""
    mentions = {}
    for agent, refs in AGENT_REFS.items():
        if agent in brief_md:
            mentions[agent] = refs
    return mentions


def fetch_intelligence_outputs() -> list:
    """Query agora.intelligence_outputs for the last 24h of pipeline runs.
    Returns [] on any failure (Postgres unreachable, etc.)."""
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import agora_persist
        return agora_persist.read_recent_intelligence_outputs(hours=24, limit=50)
    except Exception:
        return []


def _path_to_github_url(path: str) -> str:
    """Convert a local file path to its GitHub blob URL, or None if not in tracked area."""
    if not path:
        return None
    norm = path.replace("\\", "/")
    # Only docs/ + pivot/ + apollo/ + roles/ + scripts/ are tracked at top level
    for prefix in ("docs/", "pivot/", "apollo/", "roles/", "scripts/", "whitepapers/"):
        idx = norm.find(prefix)
        if idx >= 0:
            rel = norm[idx:]
            return f"{GITHUB_BLOB}/{rel}"
    return None


def _exclude_dr_events(rows: list) -> list:
    """DR events have their own dedicated section; don't duplicate them here."""
    return [r for r in rows if not (r.get("stage") or "").startswith("deep_research_")]


def build_intelligence_outputs_md(rows: list) -> str:
    """One line per cycle. DR events excluded (their own section)."""
    rows = _exclude_dr_events(rows)
    if not rows:
        return ""
    cycles = {}
    for r in rows:
        cycles.setdefault(r["cycle_id"], []).append(r)
    cycle_order = sorted(cycles.keys(),
                         key=lambda cid: max(r["finished_at"] for r in cycles[cid]),
                         reverse=True)
    lines = ["", "---", "", "## Recent pipeline cycles", ""]
    for cycle_id in cycle_order[:5]:
        stages = cycles[cycle_id]
        ok = sum(1 for s in stages if s["success"])
        stage_names = ", ".join(sorted({s["stage"] for s in stages}))
        latest = max(s["finished_at"] for s in stages)
        lines.append(f"- `{cycle_id[:8]}` {ok}/{len(stages)} ok — {stage_names} _(at {latest})_")
    lines.append("")
    return "\n".join(lines)


def build_intelligence_outputs_html(rows: list) -> str:
    """One line per cycle. DR events excluded (their own section)."""
    rows = _exclude_dr_events(rows)
    if not rows:
        return ""
    cycles = {}
    for r in rows:
        cycles.setdefault(r["cycle_id"], []).append(r)
    cycle_order = sorted(cycles.keys(),
                         key=lambda cid: max(r["finished_at"] for r in cycles[cid]),
                         reverse=True)
    parts = []
    parts.append('<hr style="border:none;border-top:1px solid #ccc;margin:24px 0">')
    parts.append('<h2 style="color:#222;margin-top:24px;border-bottom:1px solid #eee;padding-bottom:4px">Recent pipeline cycles</h2>')
    parts.append('<ul style="margin:4px 0 8px 0;padding-left:20px;font-size:13px">')
    for cycle_id in cycle_order[:5]:
        stages = cycles[cycle_id]
        ok = sum(1 for s in stages if s["success"])
        stage_names = ", ".join(sorted({s["stage"] for s in stages}))
        latest = max(s["finished_at"] for s in stages)
        color = "#444" if ok == len(stages) else "#a02020"
        parts.append(
            f'<li style="color:{color}"><code>{cycle_id[:8]}</code> {ok}/{len(stages)} ok '
            f'&mdash; {stage_names} <span style="color:#888">({latest})</span></li>'
        )
    parts.append('</ul>')
    return "\n".join(parts)


def build_mentions_md(brief_md: str) -> str:
    """Inline per-agent quick-links to surface right after the brief.
    Replaces the old 'Mentioned in this brief' subsection that was buried in References."""
    mentions = find_brief_mentions(brief_md)
    if not mentions:
        return ""
    lines = ["", "---", "", "## Agents mentioned above — quick links", ""]
    for agent, refs in mentions.items():
        link_inline = " · ".join(f"[{label}]({url})" for label, url in refs)
        lines.append(f"- **{agent}** — {link_inline}")
    lines.append("")
    return "\n".join(lines)


def _dr_tldr_fragment(state: dict) -> str:
    """Short ' · DR X/20 · N reports today' string, or empty if no DR signal."""
    dr = state.get("deep_research") or {}
    budget = dr.get("budget") or {}
    received = dr.get("report_count_24h") or 0
    dispatched = dr.get("dispatch_count_24h") or 0
    if not budget and received == 0 and dispatched == 0:
        return ""
    parts = []
    if budget.get("budget") is not None:
        parts.append(f"DR {budget.get('used', 0)}/{budget['budget']}")
    if received or dispatched:
        parts.append(f"{received} received / {dispatched} dispatched")
    return " · " + " · ".join(parts) if parts else ""


_DR_REPORTS_IN_EMAIL = 10


def _short_summary(text: str, limit: int = 140) -> str:
    """Collapse multi-line summaries to a single tight line."""
    if not text:
        return ""
    s = " ".join(text.split())  # collapse whitespace incl. newlines
    s = s.lstrip("# *-")
    if len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0] + "…"
    return s


def build_deep_research_md(state: dict) -> str:
    """Brief Deep Research section — received reports only, capped."""
    dr = state.get("deep_research") or {}
    reports = dr.get("reports") or []
    budget = dr.get("budget")
    received = [r for r in reports if (r.get("stage") or "") == "deep_research_received"]
    dispatched = dr.get("dispatch_count_24h") or sum(
        1 for r in reports if (r.get("stage") or "") == "deep_research_dispatched"
    )
    if not received and not budget:
        return ""
    lines = ["", "---", "", "## Deep Research (past 24h)", ""]
    if budget:
        used = budget.get("used", 0)
        total = budget.get("budget", 20)
        remaining = budget.get("remaining")
        if remaining is None and used is not None and total is not None:
            remaining = total - used
        agent = budget.get("agent") or "?"
        over = " (over budget)" if used is not None and total is not None and used > total else ""
        lines.append(f"**Budget:** {used}/{total} tokens{over} · {len(received)} received · {dispatched} dispatched · via `{agent}`")
        lines.append("")
    if not received:
        lines.append("*(no completed reports in last 24h yet)*")
        lines.append("")
        return "\n".join(lines)
    for r in received[:_DR_REPORTS_IN_EMAIL]:
        summary = _short_summary(r.get("output_summary") or r.get("summary") or "(no summary)", 140)
        path = r.get("output_path")
        if path:
            lines.append(f"- [{summary}](https://github.com/jcraig949jfi/Prometheus/blob/main/{path})")
        else:
            lines.append(f"- {summary}")
    if len(received) > _DR_REPORTS_IN_EMAIL:
        lines.append(f"- *…and {len(received) - _DR_REPORTS_IN_EMAIL} more on the dashboard*")
    lines.append("")
    return "\n".join(lines)


def build_deep_research_html(state: dict) -> str:
    """Brief Deep Research section — received reports only, capped (HTML)."""
    dr = state.get("deep_research") or {}
    reports = dr.get("reports") or []
    budget = dr.get("budget")
    received = [r for r in reports if (r.get("stage") or "") == "deep_research_received"]
    dispatched = dr.get("dispatch_count_24h") or sum(
        1 for r in reports if (r.get("stage") or "") == "deep_research_dispatched"
    )
    if not received and not budget:
        return ""
    parts = []
    parts.append('<hr style="border:none;border-top:1px solid #ccc;margin:24px 0">')
    parts.append('<h2 style="color:#222;margin-top:24px;border-bottom:1px solid #eee;padding-bottom:4px">Deep Research (past 24h)</h2>')
    if budget:
        used = budget.get("used", 0)
        total = budget.get("budget", 20)
        remaining = budget.get("remaining")
        if remaining is None and used is not None and total is not None:
            remaining = total - used
        agent = budget.get("agent") or "?"
        over = ' <span style="color:#dc2626">(over budget)</span>' if used is not None and total is not None and used > total else ""
        parts.append(
            f'<p style="margin:8px 0 12px 0;font-size:14px;color:#444">'
            f'<strong>Budget:</strong> {used}/{total} tokens{over} &middot; '
            f'{len(received)} received &middot; {dispatched} dispatched &middot; '
            f'via <code>{agent}</code></p>'
        )
    if not received:
        parts.append('<p style="color:#666;font-style:italic">(no completed reports in last 24h yet)</p>')
        return "\n".join(parts)
    parts.append('<ul style="margin:4px 0 8px 0;padding-left:20px">')
    for r in received[:_DR_REPORTS_IN_EMAIL]:
        summary = _short_summary(r.get("output_summary") or r.get("summary") or "(no summary)", 140)
        path = r.get("output_path")
        if path:
            parts.append(
                f'<li style="margin:4px 0"><a href="https://github.com/jcraig949jfi/Prometheus/blob/main/{path}" '
                f'style="color:#0366d6;text-decoration:none">{summary}</a></li>'
            )
        else:
            parts.append(f'<li style="margin:4px 0;color:#333">{summary}</li>')
    if len(received) > _DR_REPORTS_IN_EMAIL:
        parts.append(f'<li style="color:#888;font-style:italic">…and {len(received) - _DR_REPORTS_IN_EMAIL} more on the dashboard</li>')
    parts.append('</ul>')
    return "\n".join(parts)


def build_tldr_md(state: dict) -> str:
    """One-paragraph executive header pulled from state.json."""
    if not state:
        return ""
    alive = sum(1 for a in state.get("agents", []) if a.get("status") == "ALIVE")
    expected = sum(1 for a in state.get("agents", []) if a.get("expected"))
    anomalies = len(state.get("anomalies") or [])
    infra = state.get("infra_status") or {}
    infra_note = ""
    if infra:
        infra_note = f" · infra: Redis {infra.get('redis', '?')}"
        if infra.get("postgres"):
            infra_note += f" / Postgres {infra.get('postgres')}"
    cycles = {}
    for r in state.get("intelligence_outputs") or []:
        cycles.setdefault(r["cycle_id"], []).append(r)
    last_cycle_line = ""
    if cycles:
        cycle_id, stages = max(cycles.items(), key=lambda kv: max(s["finished_at"] for s in kv[1]))
        ok = sum(1 for s in stages if s["success"])
        last_cycle_line = f" · last intel cycle {cycle_id[:8]}: {ok}/{len(stages)} stages ok"
    lines = ["", "**TL;DR** — "
             f"agents alive {alive}/{expected}"
             f" · anomalies {anomalies}"
             f"{infra_note}"
             f"{last_cycle_line}"
             f"{_dr_tldr_fragment(state)}", ""]
    return "\n".join(lines)


def build_references_md(brief_md: str) -> str:
    """Return a markdown block of follow-up links to append at the bottom of the email."""
    lines = ["", "---", "", "## References & follow-up", ""]
    for section_title, refs in STATIC_REFS:
        lines.append(f"### {section_title}")
        for label, url in refs:
            lines.append(f"- [{label}]({url})")
        lines.append("")
    lines.append("---")
    lines.append("*Edit `scripts/send_brief_email.py` to add/remove links from this catalog.*")
    return "\n".join(lines)


def build_mentions_html(brief_md: str) -> str:
    """Inline per-agent quick-links as HTML, placed right after the brief."""
    mentions = find_brief_mentions(brief_md)
    if not mentions:
        return ""
    parts = []
    parts.append('<hr style="border:none;border-top:1px solid #eee;margin:16px 0">')
    parts.append('<h3 style="color:#444;margin-top:8px">Agents mentioned above — quick links</h3>')
    parts.append('<ul style="margin:4px 0 8px 0;padding-left:20px">')
    for agent, refs in mentions.items():
        links = " · ".join(
            f'<a href="{url}" style="color:#0366d6;text-decoration:none">{label}</a>'
            for label, url in refs
        )
        parts.append(f'<li><strong>{agent}</strong> — {links}</li>')
    parts.append('</ul>')
    return "\n".join(parts)


def build_tldr_html(state: dict) -> str:
    """One-line executive header pulled from state.json, rendered as HTML."""
    if not state:
        return ""
    alive = sum(1 for a in state.get("agents", []) if a.get("status") == "ALIVE")
    expected = sum(1 for a in state.get("agents", []) if a.get("expected"))
    anomalies = len(state.get("anomalies") or [])
    infra = state.get("infra_status") or {}
    infra_note = ""
    if infra:
        infra_note = f" · infra: Redis {infra.get('redis', '?')}"
        if infra.get("postgres"):
            infra_note += f" / Postgres {infra.get('postgres')}"
    cycles = {}
    for r in state.get("intelligence_outputs") or []:
        cycles.setdefault(r["cycle_id"], []).append(r)
    last_cycle_line = ""
    if cycles:
        cycle_id, stages = max(cycles.items(), key=lambda kv: max(s["finished_at"] for s in kv[1]))
        ok = sum(1 for s in stages if s["success"])
        last_cycle_line = f" · last intel cycle <code>{cycle_id[:8]}</code>: {ok}/{len(stages)} stages ok"
    return (
        '<p style="padding:8px 12px;background:#eef;border-left:3px solid #88a;margin:0 0 16px 0;font-size:14px">'
        f'<strong>TL;DR</strong> — agents alive {alive}/{expected} · anomalies {anomalies}{infra_note}{last_cycle_line}{_dr_tldr_fragment(state)}'
        '</p>'
    )


def build_references_html(brief_md: str) -> str:
    """Return an HTML block of follow-up links, styled for email clients."""
    parts = []
    parts.append('<hr style="border:none;border-top:1px solid #ccc;margin:24px 0">')
    parts.append('<h2 style="color:#222;margin-top:24px;border-bottom:1px solid #eee;padding-bottom:4px">References &amp; follow-up</h2>')

    for section_title, refs in STATIC_REFS:
        parts.append(f'<h3 style="color:#444;margin-top:16px">{section_title}</h3>')
        parts.append('<ul style="margin:4px 0 8px 0;padding-left:20px">')
        for label, url in refs:
            parts.append(
                f'<li><a href="{url}" style="color:#0366d6;text-decoration:none">{label}</a></li>'
            )
        parts.append('</ul>')

    parts.append('<hr style="border:none;border-top:1px solid #eee;margin:16px 0">')
    parts.append(
        '<p style="color:#888;font-size:11px;font-style:italic">'
        'Edit <code>scripts/send_brief_email.py</code> to add or remove links from this catalog.'
        '</p>'
    )
    return "\n".join(parts)


def load_env():
    """Load agents/eos/.env into os.environ if present."""
    env_path = REPO_ROOT / "agents" / "eos" / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def render_html(markdown_text: str) -> str:
    """Minimal markdown-ish to HTML — bold + headings + lists, no full parser."""
    lines = markdown_text.splitlines()
    out = ["<html><body style=\"font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 700px; margin: 20px auto; line-height: 1.5;\">"]
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h2 style='color:#222;border-bottom:1px solid #eee;padding-bottom:4px;margin-top:24px'>{stripped[3:]}</h2>")
        elif stripped.startswith("# "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h1 style='color:#111'>{stripped[2:]}</h1>")
        elif stripped.startswith("---"):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("<hr style='border:none;border-top:1px solid #eee;margin:16px 0'>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            content = stripped[2:]
            # bold inline
            while "**" in content:
                content = content.replace("**", "<strong>", 1)
                content = content.replace("**", "</strong>", 1)
            out.append(f"<li>{content}</li>")
        elif stripped.startswith("*") and stripped.endswith("*") and len(stripped) > 2:
            # italic line (e.g., timestamp)
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p style='color:#888;font-style:italic;margin:4px 0'>{stripped.strip('*')}</p>")
        elif stripped == "":
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("<br>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            # bold inline in plain paragraphs
            content = stripped
            while "**" in content:
                content = content.replace("**", "<strong>", 1)
                content = content.replace("**", "</strong>", 1)
            out.append(f"<p>{content}</p>")
    if in_list:
        out.append("</ul>")
    out.append("</body></html>")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Email the latest Metis portfolio brief")
    parser.add_argument("--brief", type=Path, default=DEFAULT_BRIEF,
                        help="Path to brief markdown (default: dashboard/portfolio_brief.md)")
    parser.add_argument("--subject", default=None,
                        help="Override email subject (default: 'Prometheus Portfolio — <date>')")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be sent; don't actually send")
    args = parser.parse_args()

    load_env()

    if os.environ.get("HERMES_ENABLED", "true").lower() == "false":
        print("HERMES_ENABLED=false — exiting without sending.")
        return

    sender = os.environ.get("HERMES_GMAIL_ADDRESS")
    password = os.environ.get("HERMES_GMAIL_APP_PASSWORD")
    recipient = os.environ.get("HERMES_RECIPIENT", sender)

    if not sender or not password:
        print("ERROR: HERMES_GMAIL_ADDRESS and HERMES_GMAIL_APP_PASSWORD must be set "
              "(in agents/eos/.env or env). Aborting.", file=sys.stderr)
        sys.exit(1)

    if not args.brief.exists():
        print(f"ERROR: brief file {args.brief} does not exist. "
              f"Run `python scripts/metis_portfolio.py` first.", file=sys.stderr)
        sys.exit(1)

    brief_md = args.brief.read_text(encoding="utf-8")
    # Defense-in-depth: strip any LLM chain-of-thought preamble that leaked
    # through the brief file, in case metis_portfolio's own strip missed it.
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from metis_portfolio import _strip_chain_of_thought
        brief_md = _strip_chain_of_thought(brief_md)
    except Exception:
        pass
    # TL;DR header pulled from current state.json
    state = {}
    state_path = REPO_ROOT / "docs" / "state.json"
    if state_path.exists():
        try:
            import json as _json
            state = _json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            state = {}
    tldr_md = build_tldr_md(state)
    tldr_html = build_tldr_html(state)
    mentions_md = build_mentions_md(brief_md)
    mentions_html = build_mentions_html(brief_md)
    intel_rows = fetch_intelligence_outputs()
    intel_md = build_intelligence_outputs_md(intel_rows)
    intel_html = build_intelligence_outputs_html(intel_rows)
    # Deep Research surfacing — budget + reports past 24h (Aletheia 96ea9322).
    # Pythia's reports surface through this section once log_work fires
    # stage='deep_research_received' with the report's output_path.
    dr_md = build_deep_research_md(state)
    dr_html = build_deep_research_html(state)
    refs_md = build_references_md(brief_md)
    refs_html = build_references_html(brief_md)
    body_md = (tldr_md + "\n" + brief_md + "\n" + mentions_md + "\n"
               + dr_md + "\n" + intel_md + "\n" + refs_md)
    body_html = (tldr_html + render_html(brief_md) + mentions_html
                 + dr_html + intel_html + refs_html)

    now = datetime.now(timezone.utc)
    subject = args.subject or f"Prometheus Portfolio — {now.strftime('%Y-%m-%d %H:%M UTC')}"

    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body_md, "plain", "utf-8"))
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    if args.dry_run:
        print(f"DRY-RUN — would send to {recipient} from {sender}")
        print(f"Subject: {subject}")
        print(f"Body length: {len(body_md)} chars markdown / {len(body_html)} chars html")
        print("---FIRST 500 CHARS OF MARKDOWN BODY---")
        print(body_md[:500])
        return

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, [recipient], msg.as_string())
        print(f"[{now.isoformat()}] sent '{subject}' to {recipient}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"AUTH FAIL: {e}. Check that HERMES_GMAIL_APP_PASSWORD is a Gmail App "
              f"Password (not your normal account password) and that 2FA is enabled "
              f"on the account.", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"SEND FAIL: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
