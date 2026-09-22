"""Consumer trace: who imports, reads or names a path (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: none.  A grep that is never piped through head.
Feedback law (2026-09-11): "a grep piped through head cannot support a
'nothing consumes X' claim" -- so this returns EVERY hit and the exact
command, and the caller reads the whole list.

NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::adapters_consumer_trace.*

Reads: the working tree via ripgrep (falls back to a python walk if rg is
absent).  Writes: nothing.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}
_DEFAULT_GLOBS = ("*.py", "*.md", "*.json", "*.jsonl", "*.txt", "*.toml", "*.yaml", "*.yml", "*.sh", "*.ps1")


def _patterns_for(target: str) -> list:
    p = Path(target)
    stem = p.stem
    mod = p.with_suffix("").as_posix().replace("/", ".") if p.suffix == ".py" else None
    pats = [re.escape(p.name)]
    if mod:
        pats.append(re.escape(mod))
        pats.append(r"import\s+" + re.escape(stem) + r"\b")
        pats.append(r"from\s+[\w.]*" + re.escape(stem) + r"\s+import")
    return pats


def trace(target: str, repo: Path, *, globs=_DEFAULT_GLOBS) -> dict:
    """All lines in the tree mentioning target (by filename, dotted module or import form)."""
    pats = _patterns_for(target)
    hits, cmd = [], None
    if shutil.which("rg"):
        cmd = ["rg", "-n", "--no-heading", "-e", "|".join(pats)]
        for g in globs:
            cmd += ["-g", g]
        cmd += ["."]
        r = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, encoding="utf-8", errors="replace")
        for line in r.stdout.splitlines():
            parts = line.split(":", 2)
            if len(parts) == 3 and parts[1].isdigit():
                f = parts[0].replace("\\", "/")
                if f.startswith("./"):
                    f = f[2:]
                hits.append({"file": f, "line": int(parts[1]), "text": parts[2][:200]})
    else:
        rx = re.compile("|".join(pats))
        for root, dirs, files in os.walk(repo):
            dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
            for f in files:
                if not any(Path(f).match(g) for g in globs):
                    continue
                fp = Path(root) / f
                try:
                    for i, line in enumerate(fp.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                        if rx.search(line):
                            hits.append({"file": fp.relative_to(repo).as_posix(), "line": i, "text": line[:200]})
                except OSError:
                    pass
    self_rel = Path(target).as_posix()
    external = [h for h in hits if h["file"] != self_rel]
    importers = [h for h in external if re.search(r"^\s*(from|import)\s", h["text"])]
    return {"target": target, "patterns": pats, "command": cmd, "n_hits": len(hits), "n_external": len(external),
            "n_importers": len(importers), "importers": importers, "hits": external, "truncated": False,
            "forbidden_inference": "zero external hits means no TEXTUAL consumer in the working tree; "
                                   "dynamic imports, subprocess strings built at runtime, and consumers "
                                   "on other hosts are not covered."}
