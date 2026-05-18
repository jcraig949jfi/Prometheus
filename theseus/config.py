"""Theseus configuration. Paths are repo-relative; never hardcode drives."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
THESEUS_ROOT = Path(__file__).resolve().parent

CORPUS_DIR = THESEUS_ROOT / "corpus"
JOURNAL_DIR = THESEUS_ROOT / "journals"
BATCH_LOG_PATH = JOURNAL_DIR / "BATCH_LOG.md"
BATCHES_JSONL_PATH = JOURNAL_DIR / "batches.jsonl"

DEFAULT_BATCH_HOURS = 1.0
DEFAULT_ACTIVE_GENERATORS = ("a1", "b5", "c1", "d1", "e1")
DEFAULT_BANDIT_EPSILON = 0.2

# Where generators look for inputs. Repo-relative.
DEEP_RESEARCH_BATCH_GLOB = REPO_ROOT / "aporia" / "docs"  # batch_* subdirs
KNOTS_DB_PATH = REPO_ROOT / "prometheus_math" / "databases" / "knots.json.gz"
BSD_RICH_DB_PATH = REPO_ROOT / "prometheus_math" / "databases" / "bsd_rich.json.gz"
GENUS2_DB_PATH = REPO_ROOT / "prometheus_math" / "databases" / "genus2.json.gz"

# Generator activation defaults. STUB = scaffolded but not yet implemented.
GENERATOR_STATUS = {
    # A — catalog-cross-product
    "a1": "active",
    "a2": "active",
    "a3": "stub",
    "a4": "stub",
    "a5": "stub",
    # B — operator-action
    "b1": "stub",
    "b2": "stub",
    "b3": "stub",
    "b4": "stub",
    "b5": "active",
    # C — mutation
    "c1": "active",
    "c2": "active",
    "c3": "stub",
    "c4": "active",
    "c5": "stub",
    # D — kill-neighborhood
    "d1": "active",
    "d2": "active",
    "d3": "stub",
    "d4": "stub",
    # E — literature mining
    "e1": "active",
    "e2": "stub",
    "e3": "stub",
    "e4": "stub",
    "e5": "stub",
    # F — probabilistic
    "f1": "stub",
    "f2": "stub",
    "f3": "stub",
    "f4": "stub",
    # G — symmetry/transformation
    "g1": "stub",
    "g2": "stub",
    "g3": "stub",
    "g4": "stub",
    "g5": "stub",
    # H — self-feeding
    "h1": "active",
    "h2": "stub",
    "h3": "stub_future",  # needs Learner
    "h4": "stub",
    # I — local LLM
    "i1": "stub_tier2",
    "i2": "stub_tier2",
    "i3": "stub_tier2",
    "i4": "stub_tier2",
    # J — frontier API
    "j1": "stub_tier3",
    "j2": "stub_tier3",
    "j3": "stub_tier3",
}
