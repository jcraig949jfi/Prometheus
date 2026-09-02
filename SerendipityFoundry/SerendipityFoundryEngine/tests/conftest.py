import os
import sys

import pytest

# make the `sfe` package importable when running the Engine's tests from its own
# tree (whether or not it has been pip-installed).
_ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_ROOT not in sys.path:
    sys.path.insert(0, _ENGINE_ROOT)

from sfe.runtime import Foundry


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "sfe.db")


@pytest.fixture
def foundry(db_path):
    f = Foundry(db_path)
    yield f
    f.close()


@pytest.fixture
def owned_world(foundry):
    c = foundry.create_client("owner")
    s = foundry.create_session(c, "session")
    w = foundry.create_world(s, "w")
    foundry.start_world(w["world_id"], c)
    return foundry, c, w["world_id"]
