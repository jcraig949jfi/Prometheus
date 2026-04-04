"""
checkpointer.py — Atomic population snapshots with configurable paths.

Writes to a temp file then renames, so a crash mid-write never corrupts
the latest good checkpoint. Keeps the last N checkpoints (default 5).
"""

import glob
import os
import pickle
import tempfile
from pathlib import Path

from logger import log_info, log_warning, log_error


def save_checkpoint(population, archive, generation: int,
                    checkpoint_dir: str | Path = "checkpoints",
                    keep_last: int = 5):
    """Atomically save a checkpoint.

    Writes to a temp file in the same directory, then renames.
    This guarantees that the checkpoint file is always complete.
    """
    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    target = checkpoint_dir / f"checkpoint_gen_{generation:06d}.pkl"

    data = {
        "population": population,
        "archive": archive,
        "generation": generation,
    }

    # Atomic write: temp file in same dir (same filesystem) then rename
    fd, tmp_path = tempfile.mkstemp(
        dir=str(checkpoint_dir), suffix=".tmp", prefix="ckpt_"
    )
    try:
        with os.fdopen(fd, "wb") as f:
            pickle.dump(data, f)
        # On Windows, target must not exist for rename
        if target.exists():
            target.unlink()
        os.rename(tmp_path, str(target))
    except Exception as e:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        log_error(f"Checkpoint save failed: {e}",
                  stage="checkpoint", generation=generation)
        raise

    log_info(f"Checkpoint saved: {target.name}",
             stage="checkpoint", generation=generation)

    # Prune old checkpoints
    checkpoints = sorted(glob.glob(str(checkpoint_dir / "checkpoint_gen_*.pkl")))
    while len(checkpoints) > keep_last:
        old = checkpoints.pop(0)
        try:
            Path(old).unlink()
        except OSError:
            pass


def load_checkpoint(checkpoint_dir: str | Path = "checkpoints"):
    """Load the most recent checkpoint. Returns (population, archive, generation) or None."""
    checkpoint_dir = Path(checkpoint_dir)
    checkpoints = sorted(glob.glob(str(checkpoint_dir / "checkpoint_gen_*.pkl")))
    if not checkpoints:
        return None

    path = checkpoints[-1]
    try:
        with open(path, "rb") as f:
            data = pickle.load(f)
        gen = data.get("generation", 0)
        log_info(f"Loaded checkpoint: {Path(path).name} (gen {gen})",
                 stage="checkpoint", generation=gen)
        return data.get("population"), data.get("archive"), gen
    except Exception as e:
        log_warning(f"Checkpoint load failed ({Path(path).name}): {e}",
                    stage="checkpoint")
        # Try the next most recent
        if len(checkpoints) > 1:
            log_info("Trying previous checkpoint...", stage="checkpoint")
            fallback = checkpoints[-2]
            try:
                with open(fallback, "rb") as f:
                    data = pickle.load(f)
                gen = data.get("generation", 0)
                log_info(f"Loaded fallback: {Path(fallback).name} (gen {gen})",
                         stage="checkpoint", generation=gen)
                return data.get("population"), data.get("archive"), gen
            except Exception as e2:
                log_error(f"Fallback checkpoint also failed: {e2}",
                          stage="checkpoint")
        return None


def checkpoint_exists(checkpoint_dir: str | Path = "checkpoints") -> bool:
    return bool(glob.glob(str(Path(checkpoint_dir) / "checkpoint_gen_*.pkl")))
