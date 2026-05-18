"""
Clio v0.3 — Sigma kernel CLAIM submitter

Reads claim extractions from agora.clio_claim_extractions that have no
sigma_claim_id yet, builds Sigma kernel CLAIM(...) arguments, submits via
the kernel, and writes the returned claim_id back so the extraction is
linked to the substrate's claim ledger.

Kill paths are derived from claim_type via a small template table; if no
type is known, a generic investigative kill path is used.

Backend (Sigma kernel):
    - Default: sqlite at data/clio/sigma_claims.db (cross-process linearity
      on M1; works out of the box, no infra).
    - --backend postgres: connects to the prometheus_fire `sigma` schema
      once Mnemosyne provisions sigma_kernel/migrations/001_create_sigma_schema.sql.

Usage:
    python scripts/clio_submitter.py --once                # one batch
    python scripts/clio_submitter.py --batch-size 5
    python scripts/clio_submitter.py --backend postgres
    python scripts/clio_submitter.py --loop --interval 300

Design seams (for testability):
    - kill_path_for(claim_type)                    — pure function
    - build_claim_args(extraction)                 — pure function
    - submit_extraction(extraction, kernel, …)     — DI kernel for tests
    - run_submission_batch(…)                      — DI reader/writer/kernel
"""
import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Callable, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    import agora_persist
    HAS_PG = True
except Exception:
    HAS_PG = False

try:
    from sigma_kernel.sigma_kernel import SigmaKernel, Tier
    HAS_SIGMA = True
except Exception:
    HAS_SIGMA = False
    SigmaKernel = None  # type: ignore
    Tier = None  # type: ignore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CLIO-SUBMIT] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("clio_submitter")


# ---------------------------------------------------------------------------
# Kill-path templates
# ---------------------------------------------------------------------------

KILL_PATH_TEMPLATES = {
    "theorem":        "find counterexample to claim or expose an error in the published proof",
    "conjecture":     "find counterexample to claim",
    "empirical":      "replicate the computation; demonstrate the stated result is not reproducible",
    "counterexample": "verify the counterexample object exists and actually falsifies the prior claim",
    "erratum":        "verify the corrected statement against the original and check the correction is itself error-free",
    "construction":   "verify constructed object exists and satisfies the stated properties",
}

DEFAULT_KILL_PATH = "investigate primary source; propose specific kill path before promotion beyond Conjecture"


def kill_path_for(claim_type: Optional[str]) -> str:
    """Pure function: claim_type -> kill_path string. Always returns a non-empty string."""
    if not claim_type:
        return DEFAULT_KILL_PATH
    return KILL_PATH_TEMPLATES.get(claim_type.lower().strip(), DEFAULT_KILL_PATH)


# ---------------------------------------------------------------------------
# CLAIM-arg construction
# ---------------------------------------------------------------------------

def build_claim_args(extraction: dict) -> dict:
    """Compose the kwargs for SigmaKernel.CLAIM(...) from a Clio extraction row.

    Pure function; no I/O. Tests verify the contract.
    """
    paper_ext = (extraction.get("paper_external_id") or "").strip()
    paper_title = (extraction.get("paper_title") or "").strip()
    target_name = f"arxiv:{paper_ext}" if paper_ext else (paper_title[:80] or f"clio_paper_{extraction.get('paper_id')}")

    hypothesis = (extraction.get("claim_text") or "").strip()
    if not hypothesis:
        raise ValueError(f"extraction id={extraction.get('id')} has empty claim_text")

    paper_url = extraction.get("paper_url") or None
    paper_abstract = extraction.get("paper_abstract") or ""

    # v0.5: prefer LLM-suggested kill_path (paper-aware, epistemic-posture-respecting)
    # over the static claim_type template. Falls back when LLM didn't provide one
    # or provided a non-string. The fallback covers most cases at acceptable
    # quality; the suggestion handles the cases the template gets wrong (e.g.
    # theorems where "find counterexample" is inappropriate per James 2026-05-18).
    llm_kp = extraction.get("kill_path_suggestion")
    if isinstance(llm_kp, str) and llm_kp.strip():
        kill_path = llm_kp.strip()
        kill_path_source = "llm"
    else:
        kill_path = kill_path_for(extraction.get("claim_type"))
        kill_path_source = "template"

    evidence = {
        "source_paper_title": paper_title,
        "source_paper_url": paper_url,
        "source_paper_external_id": paper_ext or None,
        "abstract_excerpt": paper_abstract[:500] if paper_abstract else None,
        "clio_paper_id": extraction.get("paper_id"),
        "clio_extraction_id": extraction.get("id"),
        "claim_type": extraction.get("claim_type"),
        "paradigm_hint": extraction.get("paradigm_hint"),
        "open_problem_hint": extraction.get("open_problem_hint"),
        "extractor_confidence": extraction.get("confidence"),
        "kill_path_source": kill_path_source,
    }
    return {
        "target_name": target_name,
        "hypothesis": hypothesis,
        "evidence": evidence,
        "kill_path": kill_path,
    }


# ---------------------------------------------------------------------------
# Submission
# ---------------------------------------------------------------------------

def submit_extraction(extraction: dict, kernel, target_tier=None) -> str:
    """Submit one extraction to Sigma. Returns the resulting claim.id (string).

    Raises on any submission error; the batch runner catches and records.
    """
    args = build_claim_args(extraction)
    if target_tier is not None:
        args["target_tier"] = target_tier
    elif Tier is not None:
        args["target_tier"] = Tier.Conjecture
    claim = kernel.CLAIM(**args)
    return claim.id


def run_submission_batch(
    batch_size: int = 10,
    kernel=None,
    reader: Optional[Callable] = None,
    on_success: Optional[Callable] = None,
    on_error: Optional[Callable] = None,
) -> dict:
    """One submission batch. Returns stats dict.

    Defaults:
      reader     = agora_persist.read_unsubmitted_extractions
      on_success = agora_persist.mark_extraction_submitted
      on_error   = agora_persist.mark_extraction_submission_error
    """
    if reader is None:
        reader = agora_persist.read_unsubmitted_extractions if HAS_PG else (lambda **kw: [])
    if on_success is None:
        on_success = agora_persist.mark_extraction_submitted if HAS_PG else (lambda **kw: False)
    if on_error is None:
        on_error = agora_persist.mark_extraction_submission_error if HAS_PG else (lambda **kw: False)

    extractions = reader(limit=batch_size)
    stats = {
        "submitted": 0,
        "failed": 0,
        "claim_ids": [],
    }

    for ext in extractions:
        try:
            claim_id = submit_extraction(ext, kernel)
            on_success(ext["id"], claim_id)
            stats["submitted"] += 1
            stats["claim_ids"].append(claim_id)
            log.info(f"extraction {ext['id']} -> sigma claim {claim_id}")
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            try:
                on_error(ext["id"], err)
            except Exception:
                pass
            stats["failed"] += 1
            log.exception(f"extraction {ext.get('id')} submission failed: {err}")

    return stats


# ---------------------------------------------------------------------------
# Kernel factory
# ---------------------------------------------------------------------------

def _bridge_postgres_env_vars() -> None:
    """If PROMETHEUS_FIRE_* aren't set but AGORA_POSTGRES_* are, bridge them.

    Sigma kernel's Postgres adapter uses thesauros.prometheus_data.pool which
    reads PROMETHEUS_FIRE_HOST/PORT/USER/PASSWORD. agora_persist uses
    AGORA_POSTGRES_*. Same physical DB, different naming. Bridge silently so
    `--backend postgres` works without manual env-var management.
    """
    import os
    bridge_map = [
        ("PROMETHEUS_FIRE_HOST", "AGORA_POSTGRES_HOST"),
        ("PROMETHEUS_FIRE_PORT", "AGORA_POSTGRES_PORT"),
        ("PROMETHEUS_FIRE_USER", "AGORA_POSTGRES_USER"),
        ("PROMETHEUS_FIRE_PASSWORD", "AGORA_POSTGRES_PASSWORD"),
    ]
    for fire_key, agora_key in bridge_map:
        if not os.environ.get(fire_key):
            v = os.environ.get(agora_key)
            if v is not None:
                os.environ[fire_key] = v
    # Defaults (match agora_persist defaults if neither set)
    os.environ.setdefault("PROMETHEUS_FIRE_HOST", "192.168.1.176")
    os.environ.setdefault("PROMETHEUS_FIRE_PORT", "5432")
    os.environ.setdefault("PROMETHEUS_FIRE_USER", "postgres")
    os.environ.setdefault("PROMETHEUS_FIRE_PASSWORD", "prometheus")


def build_kernel(backend: str = "sqlite", db_path: Optional[str] = None):
    """Construct a SigmaKernel instance.

    sqlite default path: data/clio/sigma_claims.db (cross-process linearity on M1).
    postgres uses the prometheus_fire / sigma schema. Migrations 001-005 must
    be applied (006 is no-op); see sigma_kernel/migrations/.
    """
    if not HAS_SIGMA:
        raise RuntimeError("sigma_kernel unavailable on this machine")
    if backend == "sqlite":
        if db_path is None:
            data_dir = REPO_ROOT / "data" / "clio"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "sigma_claims.db")
        return SigmaKernel(db_path, backend="sqlite")
    elif backend == "postgres":
        _bridge_postgres_env_vars()
        return SigmaKernel(backend="postgres")
    else:
        raise ValueError(f"unknown backend {backend!r}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Clio v0.3 — Sigma claim submitter")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--once", action="store_true", help="Single batch, then exit (default)")
    parser.add_argument("--loop", action="store_true", help="Loop with --interval delay")
    parser.add_argument("--interval", type=int, default=300, help="Loop interval seconds (default 300)")
    parser.add_argument("--backend", choices=["sqlite", "postgres"], default="sqlite")
    parser.add_argument("--db-path", type=str, default=None, help="Override sqlite path")
    args = parser.parse_args()

    if not HAS_PG:
        log.error("agora_persist unavailable. Aborting.")
        return 1
    if not HAS_SIGMA:
        log.error("sigma_kernel unavailable. Aborting.")
        return 1

    kernel = build_kernel(backend=args.backend, db_path=args.db_path)

    print("=" * 60)
    print("  CLIO-SUBMIT — Sigma CLAIM submitter (v0.3)")
    print(f"  Backend:    {args.backend}")
    print(f"  Mode:       {'loop @ ' + str(args.interval) + 's' if args.loop else 'single batch'}")
    print(f"  Batch size: {args.batch_size}")
    print("=" * 60)

    if args.loop:
        while True:
            try:
                stats = run_submission_batch(batch_size=args.batch_size, kernel=kernel)
                log.info(f"batch: submitted={stats['submitted']}, failed={stats['failed']}")
            except Exception as e:
                log.exception(f"batch failed: {e}")
            time.sleep(args.interval)
    else:
        stats = run_submission_batch(batch_size=args.batch_size, kernel=kernel)
        print(json.dumps({k: v for k, v in stats.items() if k != "claim_ids"}, indent=2))
        if stats["claim_ids"]:
            print(f"Sample claim_id: {stats['claim_ids'][0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
