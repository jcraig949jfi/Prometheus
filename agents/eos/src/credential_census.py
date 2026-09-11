"""EOS-04 Phase 0 census: who reads credentials, and how.

Two questions, both answered over the TRACKED tree only:

  1. which tracked files mention the legacy credential path
     (agents/eos/.env), and are they code or documentation;
  2. which tracked files INDEPENDENTLY IMPLEMENT credential-path
     discovery -- that is, locate and parse a .env-style file themselves
     instead of asking the canonical resolver.

(2) is the one that matters. A file that mentions the path in prose is
untidy; a file that implements its own discovery is a second resolver,
and the program currently has many.

Prints counts and paths. Reads no credential file and prints no value.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

LEGACY_PATH_PATTERNS = (
    re.compile(r"agents/eos/\.env"),
    re.compile(r"""["']agents["']\s*,\s*["']eos["']\s*,\s*["']\.env["']"""),
    re.compile(r"""\.\./\.\./agents/eos/\.env"""),
)

#: A file discovers credential paths itself if it names a dotenv-ish file
#: AND parses it (splits on '=' or feeds os.environ) in its own code.
DISCOVERY_NAMES = re.compile(r"""["'][^"']*\.env[^"']*["']|/\s*["']\.env["']""")
DISCOVERY_PARSE = re.compile(r"os\.environ\[|os\.environ\.setdefault|environ\.update|split\(\s*[\"']=[\"']|splitlines\(\)")

CODE_SUFFIXES = {".py"}
DOC_SUFFIXES = {".md", ".txt", ".rst"}


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=str(REPO), capture_output=True,
                         text=True, timeout=300).stdout
    return [l for l in out.splitlines() if l.strip()]


def main() -> int:
    files = tracked_files()
    mentions_code, mentions_doc, discoverers = [], [], []
    for rel in files:
        p = REPO / rel
        suf = p.suffix.lower()
        if suf not in CODE_SUFFIXES | DOC_SUFFIXES:
            continue
        try:
            body = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(rx.search(body) for rx in LEGACY_PATH_PATTERNS):
            (mentions_code if suf in CODE_SUFFIXES else mentions_doc).append(rel)
        if suf in CODE_SUFFIXES and DISCOVERY_NAMES.search(body) and DISCOVERY_PARSE.search(body):
            discoverers.append(rel)

    print("tracked files scanned: {}".format(len(files)))
    print()
    print("A. TRACKED CODE mentioning the legacy path: {}".format(len(mentions_code)))
    for f in sorted(mentions_code):
        print("   ", f)
    print()
    print("B. TRACKED DOCS mentioning the legacy path: {}".format(len(mentions_doc)))
    for f in sorted(mentions_doc):
        print("   ", f)
    print()
    print("C. TRACKED CODE implementing its own credential-path discovery: {}".format(len(discoverers)))
    for f in sorted(discoverers):
        print("   ", f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
