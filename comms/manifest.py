"""Manifest hashing that identifies the REPOSITORY ARTIFACT, not the checkout.

A cryptographic manifest whose value changes because git checked a text
file out with CRLF is not identifying the artifact (operator ruling
2026-09-11, after Diomedes, Lexis, Alethelia and Hephaestus reproduced the
defect within an hour of the comms queue going live). The byte
representation is therefore DEFINED here: text files are hashed with CRLF
and lone CR normalised to LF, i.e. sha256 over the CONTENT git stores for a
normalised text file (not the git blob id, which is SHA-1 over a header plus
content); everything else is hashed as-is.

A file is text only if it has no NUL byte in its first 8 KiB AND decodes as
UTF-8 (Aporia #1283, 2026-10-04: the NUL test alone called short binaries
text, so 9f0d44e1 and 9f0a44e1 hashed EQUAL). verify() checks CONTENT: a
listed file that is missing or changed is a mismatch, and so is a manifest
with no entries (it used to verify as (0, [])). Coverage is separate:
unlisted() names files beside the manifest that it does not list. The CLI
fails on either.

    python -m comms.manifest write <dir>      # (re)write <dir>/MANIFEST.md
    python -m comms.manifest verify <dir>     # exit 1 on any mismatch or unlisted file
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

LINE = re.compile(r"^- (.+?)\s+sha256:([0-9a-f]{64})(.*)$")       # names may contain spaces (#1283)


def is_binary(raw: bytes) -> bool:
    if b"\x00" in raw[:8192]:
        return True
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


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
             "sha256 over LF-normalised bytes for UTF-8 text, raw bytes otherwise; see comms/manifest.py.", ""]
    for p in entries(dirpath):
        lines.append("- {}  sha256:{}{}".format(p.name, artifact_hash(p), ("  " + extra[p.name]) if extra and p.name in extra else ""))
    out = dirpath / "MANIFEST.md"
    out.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    return out


def verify(dirpath: Path) -> Tuple[int, List[str]]:
    text = (dirpath / "MANIFEST.md").read_bytes().decode("utf-8")
    checked, bad, listed = 0, [], set()
    for line in text.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        listed.add(m.group(1))
        p = dirpath / m.group(1)
        if not p.exists():
            bad.append("{} missing".format(p.name)); continue
        h = artifact_hash(p)
        checked += 1
        if h != m.group(2):
            bad.append("{}: manifest {} != artifact {}".format(p.name, m.group(2)[:12], h[:12]))
    if not listed:
        bad.append("MANIFEST.md lists no entries")
    return checked, bad


def unlisted(dirpath: Path) -> List[str]:
    """Files beside MANIFEST.md that it does not list (an injected file passes verify())."""
    text = (dirpath / "MANIFEST.md").read_bytes().decode("utf-8")
    listed = {m.group(1) for m in map(LINE.match, text.splitlines()) if m}
    return [p.name for p in entries(dirpath) if p.name not in listed]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 2 or argv[0] not in ("write", "verify"):
        print(__doc__); return 2
    d = Path(argv[1])
    if argv[0] == "write":
        print("wrote", write(d)); return 0
    n, bad = verify(d)
    extra = unlisted(d)
    print("verified {} entries; {} mismatches; {} unlisted".format(n, len(bad), len(extra)))
    for b in bad:
        print("  " + b)
    for name in extra:
        print("  {} present but not in the manifest".format(name))
    return 1 if (bad or extra) else 0


if __name__ == "__main__":
    sys.exit(main())
