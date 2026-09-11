"""Manifest hashing that identifies the REPOSITORY ARTIFACT, not the checkout.

A cryptographic manifest whose value changes because git checked a text
file out with CRLF is not identifying the artifact (operator ruling
2026-09-11, after Diomedes, Lexis, Alethelia and Hephaestus reproduced the
defect within an hour of the comms queue going live). The byte
representation is therefore DEFINED here: text files are hashed with CRLF
and lone CR normalised to LF, which equals the git blob for a normalised
text file; binary files (a NUL byte in the first 8 KiB) are hashed as-is.

    python -m comms.manifest write <dir>      # (re)write <dir>/MANIFEST.md
    python -m comms.manifest verify <dir>     # exit 1 on any mismatch
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

LINE = re.compile(r"^- (\S+)\s+sha256:([0-9a-f]{64})(.*)$")


def is_binary(raw: bytes) -> bool:
    return b"\x00" in raw[:8192]


def normalised(raw: bytes) -> bytes:
    if is_binary(raw):
        return raw
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def artifact_hash(path: Path) -> str:
    return hashlib.sha256(normalised(path.read_bytes())).hexdigest()


def entries(dirpath: Path) -> List[Path]:
    return sorted(p for p in dirpath.iterdir() if p.is_file() and p.name != "MANIFEST.md")


def write(dirpath: Path, title: str = None, extra: Dict[str, str] = None) -> Path:
    lines = ["# " + (title or "Manifest for {}".format(dirpath.name)), "",
             "sha256 over LF-normalised bytes (equals the git blob for text files); see comms/manifest.py.", ""]
    for p in entries(dirpath):
        lines.append("- {}  sha256:{}{}".format(p.name, artifact_hash(p), ("  " + extra[p.name]) if extra and p.name in extra else ""))
    out = dirpath / "MANIFEST.md"
    out.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    return out


def verify(dirpath: Path) -> Tuple[int, List[str]]:
    text = (dirpath / "MANIFEST.md").read_bytes().decode("utf-8")
    checked, bad = 0, []
    for line in text.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        p = dirpath / m.group(1)
        if not p.exists():
            bad.append("{} missing".format(p.name)); continue
        h = artifact_hash(p)
        checked += 1
        if h != m.group(2):
            bad.append("{}: manifest {} != artifact {}".format(p.name, m.group(2)[:12], h[:12]))
    return checked, bad


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 2 or argv[0] not in ("write", "verify"):
        print(__doc__); return 2
    d = Path(argv[1])
    if argv[0] == "write":
        print("wrote", write(d)); return 0
    n, bad = verify(d)
    print("verified {} entries; {} mismatches".format(n, len(bad)))
    for b in bad:
        print("  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
