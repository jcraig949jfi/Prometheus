"""Append-only JSONL ledgers with a workspace receipt on every row.

    ledgers/cells.jsonl     every cell PROPOSED (accepted or refused, with why)
    ledgers/rows.jsonl      every EXECUTION attempt (completed or failed)
    ledgers/contrasts.jsonl every contrast evaluated, with its disposition
    ledgers/signals.jsonl   THEO-SIGNAL-#### emissions
    ledgers/dead.jsonl      dead neighbourhoods (consumed by later traversal)
    ledgers/cheats.jsonl    the cheat rows and what caught them (never mixed)

Nothing is ever rewritten; a correction is a new row that names the old one.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from archaeon import workspace as _ws              # noqa: E402

DEFAULT_DIR = REPO / "roles" / "Theophrastus" / "ledgers"
NAMES = ("cells", "rows", "contrasts", "signals", "dead", "cheats")


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def receipt() -> Dict[str, Any]:
    """base_sha / branch / worktree_path / dirty (WORKING_CONTRACT s4)."""
    try:
        return _ws.receipt()
    except Exception as exc:                        # noqa: BLE001
        return {"error": "%s: %s" % (type(exc).__name__, str(exc)[:120])}


class Ledger:
    def __init__(self, directory: Optional[Path] = None):
        self.dir = Path(directory or DEFAULT_DIR)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._receipt = receipt()

    def path(self, name: str) -> Path:
        if name not in NAMES:
            raise ValueError("unknown ledger %r" % name)
        return self.dir / (name + ".jsonl")

    def append(self, name: str, row: Dict[str, Any]) -> Dict[str, Any]:
        row = {"ts": now(), "workspace": self._receipt, **row}
        with self.path(name).open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True, default=str) + "\n")
            f.flush()
        return row

    def read(self, name: str) -> Iterator[Dict[str, Any]]:
        p = self.path(name)
        if not p.exists():
            return iter(())
        return (json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip())

    def rows_by_spec_hash(self) -> Dict[str, list]:
        out: Dict[str, list] = {}
        for r in self.read("rows"):
            out.setdefault(r.get("spec_hash"), []).append(r)
        return out

    def dead_cell_ids(self) -> set:
        return {r["cell_id"] for r in self.read("dead") if r.get("cell_id")}
