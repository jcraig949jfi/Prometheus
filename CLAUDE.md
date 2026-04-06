# Prometheus — Claude Code Instructions

## Security: API Keys

**NEVER read .env files, key files, credential files, or any file matching `*Key*`, `*secret*`, `*credential*`, `*.env`.** If you need to verify a key exists, check the file exists with `ls` — don't `cat`, `Read`, or display its contents.

All API keys are loaded via `keys.py` at the repo root. Scripts should `from keys import get_key` rather than reading key files directly.
