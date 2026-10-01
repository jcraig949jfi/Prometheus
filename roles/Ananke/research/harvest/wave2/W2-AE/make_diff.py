"""Build promotion.diff: one git-style unified diff that ADDS every file under pkg/ at its repository path.

Refuses (exit 1) if any target path already exists in the repository (the package must be purely additive), if
a file is not UTF-8 text, or if a cache file is present. Writes LF line endings. usage: python make_diff.py"""
from __future__ import annotations

import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE / "pkg"
REPO = HERE.parents[5]
OUT = HERE / "promotion.diff"


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def main() -> int:
    files = sorted(p for p in PKG.rglob("*") if p.is_file())
    bad = [p for p in files if "__pycache__" in p.parts or p.suffix in (".pyc", ".pyo") or ".pytest_cache" in p.parts]
    if bad:
        print("cache files present:", bad)
        return 1
    chunks, listing = [], []
    for p in files:
        rel = p.relative_to(PKG).as_posix()
        if (REPO / rel).exists():
            print("NOT ADDITIVE, exists in repository:", rel)
            return 1
        data = p.read_bytes().replace(b"\r\n", b"\n")
        text = data.decode("utf-8")
        lines = text.split("\n")
        noeol = not text.endswith("\n")
        if not noeol:
            lines = lines[:-1]
        if not lines:
            print("empty file not allowed:", rel)
            return 1
        h = [f"diff --git a/{rel} b/{rel}", "new file mode 100644", f"index 0000000..{blob_sha(data)[:7]}",
             "--- /dev/null", f"+++ b/{rel}", f"@@ -0,0 +1,{len(lines)} @@" if len(lines) != 1 else "@@ -0,0 +1 @@"]
        body = ["+" + l for l in lines]
        if noeol:
            body.append("\\ No newline at end of file")
        chunks.append("\n".join(h + body) + "\n")
        listing.append((rel, len(lines), hashlib.sha256(data).hexdigest()))
    OUT.write_bytes("".join(chunks).encode("utf-8"))
    for rel, n, sha in listing:
        print(f"{n:5d}  {sha[:12]}  {rel}")
    print(f"{len(listing)} files, {sum(n for _, n, _ in listing)} lines -> {OUT.name} sha256 "
          f"{hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
