"""
logger.py — Structured logging for Apollo v2.

Three output streams:
  1. Console: human-readable, color-coded by level
  2. Run log: structured JSONL (every event, machine-parseable)
  3. Domain logs: lineage, graveyard, dashboard (append-only JSONL)

Every log record carries:
  - timestamp (ISO 8601)
  - level
  - stage (bootstrap | warmup | graduated | main | checkpoint | evaluation | shutdown)
  - generation (int or null)
  - message (human string)
  - data (dict of structured payload — optional)
"""

import json
import logging
import os
import time
from pathlib import Path


# ── Structured JSON formatter (file output) ──────────────────────────

class JSONFormatter(logging.Formatter):
    """Emit one JSON object per line with structured fields."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "stage": getattr(record, "stage", "general"),
            "generation": getattr(record, "generation", None),
            "message": record.getMessage(),
        }
        data = getattr(record, "data", None)
        if data:
            entry["data"] = data
        return json.dumps(entry, default=str)


# ── Human-readable console formatter ─────────────────────────────────

class ConsoleFormatter(logging.Formatter):
    """Compact single-line console output with stage prefix."""

    STAGE_WIDTH = 12

    def format(self, record: logging.LogRecord) -> str:
        stage = getattr(record, "stage", "")
        gen = getattr(record, "generation", None)
        prefix = f"[{stage:<{self.STAGE_WIDTH}}]" if stage else ""
        gen_str = f" gen {gen:>5d}" if gen is not None else ""
        return f"{prefix}{gen_str} | {record.getMessage()}"


# ── Logger factory ────────────────────────────────────────────────────

_apollo_logger: logging.Logger | None = None


def get_logger(log_dir: str | Path = None) -> logging.Logger:
    """Get or create the Apollo structured logger.

    Args:
        log_dir: Directory for the run log JSONL file.
                 If None, file logging is disabled (console only).
    """
    global _apollo_logger
    if _apollo_logger is not None:
        return _apollo_logger

    logger = logging.getLogger("apollo")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Console handler — INFO and above
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(ConsoleFormatter())
    logger.addHandler(console)

    # File handler — DEBUG and above (structured JSONL)
    if log_dir is not None:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        run_log_path = log_dir / "apollo_run.jsonl"
        fh = logging.FileHandler(str(run_log_path), encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(JSONFormatter())
        logger.addHandler(fh)

    _apollo_logger = logger
    return logger


def reset_logger():
    """Reset the singleton (for tests)."""
    global _apollo_logger
    if _apollo_logger:
        for h in _apollo_logger.handlers[:]:
            _apollo_logger.removeHandler(h)
    _apollo_logger = None


# ── Convenience emitters ──────────────────────────────────────────────

def _emit(level: int, msg: str, stage: str = "general",
          generation: int = None, data: dict = None):
    """Emit a structured log record."""
    logger = get_logger()
    record = logger.makeRecord(
        name="apollo", level=level, fn="", lno=0, msg=msg,
        args=(), exc_info=None,
    )
    record.stage = stage
    record.generation = generation
    record.data = data
    logger.handle(record)


def log_info(msg: str, **kwargs):
    _emit(logging.INFO, msg, **kwargs)


def log_debug(msg: str, **kwargs):
    _emit(logging.DEBUG, msg, **kwargs)


def log_warning(msg: str, **kwargs):
    _emit(logging.WARNING, msg, **kwargs)


def log_error(msg: str, **kwargs):
    _emit(logging.ERROR, msg, **kwargs)


# ── Domain-specific JSONL writers ─────────────────────────────────────

def _append_jsonl(path: str | Path, record: dict):
    """Append one JSON line to a file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")
        f.flush()


def log_organism(organism, fitness, generation: int, lineage_path: str | Path = None):
    """Log one organism to the lineage JSONL."""
    if lineage_path is None:
        return
    record = {
        "genome_id": organism.genome_id,
        "generation": generation,
        "parent_ids": organism.lineage.parent_ids,
        "mutations_applied": organism.lineage.mutations_applied,
        "primitive_count": organism.primitive_count,
        "primitive_names": organism.primitive_names,
        "wiring_hash": organism.wiring_hash(),
        "fitness": {
            "accuracy_margin": fitness.accuracy_margin,
            "calibration": fitness.calibration,
            "ablation_delta": fitness.ablation_delta,
            "generalization": fitness.generalization,
            "diversity": fitness.diversity,
            "parsimony": fitness.parsimony,
            "raw_accuracy": fitness.raw_accuracy,
        },
        "ablation_details": fitness.ablation_details,
        "crash_count": fitness.crash_count,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    _append_jsonl(lineage_path, record)
    log_debug(
        f"Logged organism {organism.genome_id} "
        f"(acc={fitness.accuracy_margin:+.3f}, abl={fitness.ablation_delta:.2f})",
        stage="lineage", generation=generation,
    )


def log_graveyard(organism, cause: str, generation: int,
                  graveyard_path: str | Path = None):
    """Log a dead organism with cause of death."""
    if graveyard_path is None:
        return
    record = {
        "genome_id": organism.genome_id,
        "generation": generation,
        "cause": cause,
        "primitive_names": organism.primitive_names,
        "parent_ids": organism.lineage.parent_ids,
        "mutations_applied": organism.lineage.mutations_applied,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    _append_jsonl(graveyard_path, record)
    log_debug(
        f"Graveyard: {organism.genome_id} died ({cause})",
        stage="graveyard", generation=generation,
    )


def log_autopsy(organism, cause: str, generation: int, details: dict = None,
                graveyard_path: str | Path = None):
    """Enhanced graveyard entry with full autopsy details."""
    record = {
        "genome_id": organism.genome_id,
        "generation": generation,
        "cause": cause,
        "primitive_names": organism.primitive_names,
        "primitive_count": organism.primitive_count,
        "parent_ids": organism.lineage.parent_ids,
        "mutations_applied": organism.lineage.mutations_applied,
        "router_logic_len": len(organism.router_logic) if organism.router_logic else 0,
        "parameter_count": len(organism.parameters),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if details:
        record["details"] = details
    if graveyard_path:
        _append_jsonl(graveyard_path, record)
    log_debug(
        f"AUTOPSY [{cause}] {organism.genome_id[:12]} | "
        f"prims={organism.primitive_count} | "
        f"parents={[p[:8] for p in organism.lineage.parent_ids]} | "
        f"mutations={organism.lineage.mutations_applied}",
        stage="graveyard", generation=generation,
        data=record,
    )


def log_dashboard(generation: int, population: list, fitness_vectors: list,
                  archive_size: int, compilation_survival: float,
                  ncd_weight: float = 1.0,
                  dashboard_path: str | Path = None):
    """Log population-level stats for the dashboard."""
    import numpy as np

    acc = [fv.accuracy_margin for fv in fitness_vectors]
    cal = [fv.calibration for fv in fitness_vectors]
    abl = [fv.ablation_delta for fv in fitness_vectors]
    gen = [fv.generalization for fv in fitness_vectors]
    prim_counts = [o.primitive_count for o in population]
    n_load_bearing = sum(1 for a in abl if a >= 0.20)

    record = {
        "generation": generation,
        "population_size": len(population),
        "compilation_survival_pct": compilation_survival,
        "ncd_decay_weight": ncd_weight,
        "best_accuracy_margin": float(max(acc)) if acc else 0.0,
        "median_accuracy_margin": float(np.median(acc)) if acc else 0.0,
        "median_calibration": float(np.median(cal)) if cal else 0.0,
        "best_ablation_delta": float(max(abl)) if abl else 0.0,
        "n_all_load_bearing": n_load_bearing,
        "best_generalization": float(max(gen)) if gen else 0.0,
        "novelty_archive_size": archive_size,
        "median_primitive_count": float(np.median(prim_counts)) if prim_counts else 0.0,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if dashboard_path:
        _append_jsonl(dashboard_path, record)

    log_info(
        f"pop={len(population):3d} | best_acc={record['best_accuracy_margin']:+.3f} | "
        f"med_acc={record['median_accuracy_margin']:+.3f} | "
        f"best_abl={record['best_ablation_delta']:.2f} | n_lb={n_load_bearing:2d} | "
        f"comp={compilation_survival:.0%} | arch={archive_size:3d} | ncd_w={ncd_weight:.1f}",
        stage="dashboard", generation=generation,
        data=record,
    )
