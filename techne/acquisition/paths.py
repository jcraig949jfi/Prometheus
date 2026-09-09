"""Where acquired bytes land. Host-local, never a hardcoded drive letter.

Resolution order, identical in spirit to archaeon.fossils._default_sfe_db:

    TECHNE_TOOL_CACHE env var
      -> techne/config.local.json  key "tool_cache"   (gitignored, per-host)
      -> <repo>/vault/techne_tools                    (vault/ is gitignored:
                                                       "cloned repos and model weights")

The cache is deliberately OUTSIDE the tracked tree. Wheels, cloned repositories and
isolated virtual environments are not artifacts of this repository; their hashes are.
"""
from __future__ import annotations

import json
import os
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ACQ_ROOT = pathlib.Path(__file__).resolve().parent


def tool_cache() -> pathlib.Path:
    env = os.environ.get("TECHNE_TOOL_CACHE")
    if env:
        return pathlib.Path(env)
    local = REPO_ROOT / "techne" / "config.local.json"
    try:
        cfg = json.loads(local.read_text(encoding="utf-8"))
        if cfg.get("tool_cache"):
            return pathlib.Path(cfg["tool_cache"])
    except (OSError, ValueError):
        pass
    return REPO_ROOT / "vault" / "techne_tools"


def downloads() -> pathlib.Path:
    return tool_cache() / "downloads"


def repos() -> pathlib.Path:
    return tool_cache() / "repos"


def env_root(env_name: str) -> pathlib.Path:
    """Isolated virtual environment root. `env_name` comes from the manifest entry,
    so DreamCoder's ancient stack never shares an interpreter with stitch_core."""
    return tool_cache() / "envs" / env_name


def manifest_path() -> pathlib.Path:
    return ACQ_ROOT / "MANIFEST.json"


def budget_path() -> pathlib.Path:
    return ACQ_ROOT / "BUDGET_PROFILES.json"


def host_capacity_path() -> pathlib.Path:
    return ACQ_ROOT / "HOST_CAPACITY.json"


def locks() -> pathlib.Path:
    return ACQ_ROOT / "locks"


def receipts() -> pathlib.Path:
    return ACQ_ROOT / "receipts"
