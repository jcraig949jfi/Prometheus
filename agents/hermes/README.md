# Hermes — The Messenger

> *Hermes, messenger of the gods. He carries word between Olympus and the mortal world.*

Hermes collects reports from all Prometheus agents at the end of each cycle,
compiles a unified digest, and emails it to you via Gmail.

## Pipeline Position

| Upstream | This Agent | Downstream |
|----------|-----------|------------|
| Clymene | **Hermes** — compiles digest and delivers via email | Audit (Pronoia) |

**Reads from:** Metis briefs, Aletheia knowledge graph, Clymene reports, Eos digests
**Writes to:** `agents/hermes/digests/YYYY-MM-DD_digest.md`, email via Gmail SMTP

---

## What Hermes Collects

| Agent | What | Source |
|-------|------|--------|
| **Metis** | Executive brief (Act/Watch/Record) | `agents/metis/briefs/YYYY-MM-DD_brief.md` |
| **Aletheia** | Knowledge graph entity counts | `agents/aletheia/data/knowledge_graph.db` |
| **Clymene** | Hoard report (new clones, updates) | `agents/clymene/reports/YYYY-MM-DD_hoard.md` |
| **Eos** | Raw scan findings (truncated) | `agents/eos/reports/YYYY-MM-DD.md` |

The digest leads with Metis (the 3-5 things that matter) and appends
supporting detail from other agents. The Eos raw dump is truncated to
keep emails readable.

## Setup

### 1. Generate a Gmail App Password

1. Go to [myaccount.google.com](https://myaccount.google.com) → Security
2. Enable **2-Step Verification** (required for app passwords)
3. Go to **App passwords** → Generate one for "Prometheus Hermes"
4. Copy the 16-character password

### 2. Configure Hermes

**Option A: config.json** (created automatically on first run)

Edit `agents/hermes/config.json`:

```json
{
  "gmail_address": "you@gmail.com",
  "gmail_app_password": "xxxx xxxx xxxx xxxx",
  "recipient": "you@gmail.com",
  "enabled": true
}
```

**Option B: environment variables** (in `agents/eos/.env`)

```
HERMES_GMAIL_ADDRESS=you@gmail.com
HERMES_GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
HERMES_RECIPIENT=you@gmail.com
HERMES_ENABLED=true
```

### 3. Test it

```powershell
python agents/hermes/src/hermes.py --test-email
```

## Usage

```powershell
# Collect + email (normal mode, called by Pronoia)
python agents/hermes/src/hermes.py --once

# Collect digest only, no email
python agents/hermes/src/hermes.py --collect

# Test email delivery
python agents/hermes/src/hermes.py --test-email
```

## In the Pipeline

Hermes runs as the **last step** in Pronoia's scan cycle, after all other
agents have written their outputs:

```
Eos → Aletheia → Skopos ASSESS → Metis → Clymene (if due) → Hermes → Audit → Skopos GENERATE → Publish
```

## Email Triggering Logic

- Hermes always saves the digest locally to `agents/hermes/digests/YYYY-MM-DD_digest.md`
- If email is configured (`config.json` or env vars) and `enabled` is true, the digest is emailed via Gmail SMTP (SSL, port 465)
- If Metis's brief contains "Act on this" items, the email subject is prefixed with `[ACTION]` so you can spot it in your inbox
- If email is not configured, Hermes degrades gracefully — digest is saved locally only, no error

## Output

- **Digest file:** `agents/hermes/digests/YYYY-MM-DD_digest.md`
- **Email:** sent via Gmail SMTP (SSL, port 465) when configured

## Security

- App passwords are scoped — they can't change your Google account settings
- `config.json` is gitignored — credentials never hit GitHub
- Gmail's daily send limit is 500 emails — more than enough

## Design Principles

- **No new dependencies** — uses Python stdlib only (smtplib, email)
- **Graceful degradation** — if email isn't configured, just saves the digest locally
- **Lead with what matters** — Metis brief first, raw data last
- **Truncate ruthlessly** — Eos output is capped at 3000 chars in email
