# Hermes (original) — Deprecation Note

**Date:** 2026-05-17
**Author:** Aletheia, after architecture clarification from James.
**Decision:** The original `agents/hermes/src/hermes.py` is deprecated in favor of `scripts/send_brief_email.py`. The original Hermes script is no longer called from `pronoia.py`'s `_run_cycle`.

---

## Why

The original Hermes was designed to send a daily email digest combining outputs from a single pipeline (the intelligence pipeline: Eos digest + Aletheia stats + Clymene reports). It read from filesystem artifacts and emailed via Gmail SMTP.

The reporting needs evolved during the 2026-05 multi-machine orchestration work:

- **Reporting needs to be machine-agnostic.** Hephaestus on M3, Apollo on M2, Nous on M4 all produce signal. The email needs to surface state from anywhere, not just from the intelligence pipeline's filesystem outputs on one machine.
- **Reporting needs to aggregate across pipelines.** The portfolio brief (from Metis-portfolio reading Agora state), the intelligence-pipeline stage log (from Postgres `agora.intelligence_outputs`), and reference catalogs all belong in one daily email.
- **Reporting needs to be a routing layer.** Each email is a pointer into the GitHub repo, not a self-contained report.

`scripts/send_brief_email.py` was built for these needs:

- Reads `docs/portfolio_brief.md` (the Metis-portfolio output)
- Reads `agora.intelligence_outputs` from Postgres (cross-pipeline stage log)
- Auto-detects mentioned agents and prepends their reference docs
- Appends a static References catalog (project synthesis, autopsies, design docs, etc.)
- Sends multipart plain-text + HTML via Gmail SMTP

It does what Hermes did + does it in a pipeline-agnostic way.

## What changed in code

`pronoia.py` `_run_cycle`:
- The `run_hermes(logs=logs)` call is commented out.
- A `_log_stage(cycle_id, "hermes_deprecated", True, summary="hermes original retired; email owned by scripts/send_brief_email.py", ...)` row is written for one cycle of visibility, so anyone reading `agora.intelligence_outputs` sees the transition.
- After one verification cycle, the commented-out call can be removed entirely.

`agents/hermes/`:
- Code remains on disk in case anything still imports from it.
- Will be removed in a future cleanup pass once we confirm no other code references it.

## What stays

- The `HERMES_GMAIL_ADDRESS`, `HERMES_GMAIL_APP_PASSWORD`, `HERMES_RECIPIENT` env vars are still used — `send_brief_email.py` reads them from `agents/eos/.env`.
- Daily email delivery is unchanged from the user's perspective. Subject + body shape may be richer (References, intelligence outputs, etc.) but the cadence and recipient are the same.

## Future Hermes-like extensions

Multi-channel notification (SMS via Twilio, Slack via webhook, etc.) gets added to `scripts/send_brief_email.py` (which should probably be renamed `notifier.py` or similar when we add channels beyond email). Don't resurrect the `agents/hermes/` path for new channels — the parallel-implementation drift was the problem the first time.

## Architecture principle this surfaces

This deprecation is an instance of a broader principle from the 2026-05-17 architecture discussion:

> Workflows and pipelines are not bound to machines. Inputs and outputs are many-to-many. Each pipeline owns its concern; reporting aggregation is its own pipeline that reads across all of them.

Hermes was bound to one pipeline (intelligence). The reporting pipeline (`scripts/send_brief_email.py` + `metis_portfolio.py` + `portfolio_monitor.py` + `agora_persist.py`) is not — it reads from any pipeline that writes to Agora's shared substrate (Redis streams + Postgres tables).

Future pipelines should follow the same pattern: write standardized telemetry to the shared substrate, never assume a particular reader. The reporting pipeline picks up new pipelines automatically once their telemetry lands.
