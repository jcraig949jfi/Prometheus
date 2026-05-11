"""Post-process gemini_deep_research_dispatch outputs.

Earlier dispatcher runs saved the full Interaction model_dump (a JSON wrapper)
because extract_text_from_interaction looked for `output` (singular) but the
API returns `outputs` (plural). This script walks the batch dir and rewrites
each report file in-place with the clean extracted text.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEADER_RE = re.compile(
    r"^(# Prompt \d+:[^\n]+\n+\*\*Agent:\*\*[^\n]+\n\*\*Interaction ID:\*\*[^\n]+\n\*\*Elapsed:\*\*[^\n]+\n+---\n+)",
    re.DOTALL,
)


def extract(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    m = HEADER_RE.match(raw)
    if not m:
        print(f"  [skip] {path.name}: no recognizable header")
        return False
    header = m.group(1)
    body = raw[m.end():].strip()

    # If body doesn't start with a JSON brace, already-clean
    if not body.startswith("{"):
        print(f"  [skip] {path.name}: already clean")
        return False

    try:
        data = json.loads(body)
    except Exception as e:
        print(f"  [error] {path.name}: JSON parse failed: {e}")
        return False

    outputs = data.get("outputs") or data.get("output") or []
    if not isinstance(outputs, list):
        print(f"  [error] {path.name}: outputs not a list")
        return False

    parts: list[str] = []
    for item in outputs:
        if isinstance(item, dict) and "text" in item:
            parts.append(item["text"])
        elif isinstance(item, str):
            parts.append(item)
    text = "\n\n".join(p for p in parts if p)
    if not text:
        print(f"  [error] {path.name}: no text in outputs[]")
        return False

    new = header + text + "\n"
    path.write_text(new, encoding="utf-8")
    print(f"  [ok]   {path.name}: rewrote {len(text)} chars")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="batch directory")
    args = ap.parse_args()

    d = Path(args.dir)
    if not d.is_dir():
        print(f"ERROR: {d} not a directory")
        return 2

    files = sorted(p for p in d.glob("*.md") if not p.name.startswith("_"))
    print(f"Scanning {len(files)} files in {d}")
    rewrote = 0
    for p in files:
        if extract(p):
            rewrote += 1
    print(f"\nRewrote {rewrote}/{len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
