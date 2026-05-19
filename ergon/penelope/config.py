"""Penelope configuration — paths, defaults, source registry."""
from __future__ import annotations

from pathlib import Path

PENELOPE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PENELOPE_ROOT.parent.parent

JOURNAL_DIR = PENELOPE_ROOT / "journals"
BATCHES_JSONL_PATH = JOURNAL_DIR / "batches.jsonl"
BATCH_LOG_PATH = JOURNAL_DIR / "BATCH_LOG.md"
STATE_DIR = PENELOPE_ROOT / "state"
PROCESSED_LEDGER_PATH = STATE_DIR / "processed_ledger.jsonl"

INGEST_SCRIPT = REPO_ROOT / "ergon" / "learner" / "scripts" / "ingest_training_anchors.py"
CLAIM_RUNNER_MODULE = "prometheus_math.substrate_generation.tier_1_claim_runner"
CORPUS_DIR = REPO_ROOT / "ergon" / "learner" / "corpus" / "v1_0_tier_pending"

THESEUS_OUTBOX = REPO_ROOT / "theseus" / "handoff" / "ergon_outbox"
APORIA_STAGED_ROOT = REPO_ROOT / "aporia" / "docs" / "staged_substrate_blocks"
TECHNE_MINED_ROOT = REPO_ROOT / "aporia" / "docs" / "mined_substrate_blocks"

DEFAULT_INTERVAL_SECONDS = 300
DEFAULT_BATCHES = 1
LOCKFILE_PATH = STATE_DIR / "daemon.lock"

PENELOPE_AGENT_NAME = "Penelope"
