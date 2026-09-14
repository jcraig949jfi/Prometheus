"""Where the consumer's per-host mutable state lives (stop flags, park
records, its own log). One answer for every checkout.

THE DEFECT THIS CLOSES (backlog C7, hit for real 2026-09-11). The stop flag
lived at `<package>/../var/`, i.e. INSIDE the checkout the daemon happened to
be started from. Under D-23 the daemon runs from a pinned worktree while every
seat works in another, so a `stop` issued from the natural place wrote a flag
nothing would ever read -- and reported success with the path it had just
written. The state directory is now resolved from configuration, in the same
precedence order as everything else in this seat:

    VIV_VAR_DIR (environment)  >  config `var_dir`  >  <package>/../var

The default keeps every existing test and every existing local setup working;
production sets `var_dir` in the gitignored config.local.json to a directory
outside any worktree, and the daemon writes the resolved path into its
heartbeat so `stop` and `unpark` can find it without guessing.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

ENV = "VIV_VAR_DIR"
CONFIG_KEY = "var_dir"

#: The pre-C7 location, kept as the default so nothing that relied on it
#: moves without being asked to.
DEFAULT = Path(__file__).resolve().parent.parent / "var"


def resolve(cfg: Optional[dict] = None, *, create: bool = True) -> Path:
    """The state directory, resolved and (by default) created."""
    raw = os.environ.get(ENV) or (cfg or {}).get(CONFIG_KEY)
    if raw:
        p = Path(str(raw)).expanduser()
        if not p.is_absolute():
            # Relative to the repository root, never to the cwd: a daemon's
            # cwd is wherever it was launched from.
            p = DEFAULT.parent.parent / p
    else:
        p = DEFAULT
    p = p.resolve()
    if create:
        try:
            p.mkdir(parents=True, exist_ok=True)
        except OSError:                              # pragma: no cover
            pass
    return p
