"""
checkpointer.py — Population snapshots every 10 generations. Keep last 5.
"""

import pickle
import glob
from pathlib import Path


def save_checkpoint(population, archive, generation: int,
                    path: str = "F:/Prometheus/apollo/checkpoints/"):
    Path(path).mkdir(parents=True, exist_ok=True)
    filepath = Path(path) / f"checkpoint_gen_{generation:06d}.pkl"
    data = {
        'population': population,
        'archive': archive,
        'generation': generation,
    }
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)

    # Keep only last 5
    checkpoints = sorted(glob.glob(str(Path(path) / "checkpoint_gen_*.pkl")))
    while len(checkpoints) > 5:
        Path(checkpoints.pop(0)).unlink()


def load_checkpoint(path: str = "F:/Prometheus/apollo/checkpoints/"):
    checkpoints = sorted(glob.glob(str(Path(path) / "checkpoint_gen_*.pkl")))
    if not checkpoints:
        return None
    with open(checkpoints[-1], 'rb') as f:
        data = pickle.load(f)
    return data.get('population'), data.get('archive'), data.get('generation', 0)


def checkpoint_exists(path: str = "F:/Prometheus/apollo/checkpoints/") -> bool:
    return bool(glob.glob(str(Path(path) / "checkpoint_gen_*.pkl")))
