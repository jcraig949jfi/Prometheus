import os
import sys

# Make `import odysseus` work when pytest is run from anywhere in the repo.
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import pytest  # noqa: E402

from odysseus.brain.model import ModelSpec  # noqa: E402


@pytest.fixture
def spec4():
    """A small four-shard circuit that fires on most ticks."""
    return ModelSpec(n_neurons=240, n_shards=4, seed=7)


@pytest.fixture
def recorded(tmp_path, spec4):
    """A 60-tick run recorded in-process (no network), keyframe every 10."""
    from odysseus.brain.cluster import record_in_process

    path = tmp_path / "run"
    record_in_process(spec4, path, ticks=60, keyframe_interval=10)
    return path
