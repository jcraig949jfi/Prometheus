"""Manifest loading, with the entries validated rather than trusted."""
from __future__ import annotations

import json
import pathlib

from . import paths

REQUIRED = ("id", "kind", "first_role", "integration_path", "named_consumer",
            "first_useful_check", "official_source")


def load(path: pathlib.Path | None = None) -> dict:
    man = json.loads((path or paths.manifest_path()).read_text(encoding="utf-8"))
    ids = [e.get("id") for e in man["entries"]]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate manifest entry ids: {ids}")
    for e in man["entries"]:
        missing = [k for k in REQUIRED if not e.get(k)]
        if missing:
            raise ValueError(f"manifest entry {e.get('id')!r} is missing {missing}. "
                             f"The design requires every integration to name a consumer, "
                             f"a falsifiable purpose, an I/O contract and a bounded "
                             f"qualification job; an entry without them is not acquirable.")
        if e["kind"] == "python_package":
            for k in ("distribution", "import_name", "pinned_version", "env"):
                if not e.get(k):
                    raise ValueError(f"python_package entry {e['id']!r} missing {k!r}")
    return man


def entry(man: dict, entry_id: str) -> dict:
    for e in man["entries"]:
        if e["id"] == entry_id:
            return e
    raise KeyError(f"no manifest entry {entry_id!r}; have {[e['id'] for e in man['entries']]}")
