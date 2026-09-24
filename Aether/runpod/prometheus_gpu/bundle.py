"""Deterministic module packaging, without publishing a container.

Takes a module directory plus its spec and produces a bundle whose
identity is a function of its CONTENT, not of when or where it was
built. Two builds of the same files on different machines, at different
times, must produce the same bundle sha256, or "which bytes ran" is
unanswerable.

Determinism is not automatic. A tar archive records mtimes, uid/gid,
owner names and, depending on the filesystem, an arbitrary file order;
gzip records a timestamp of its own. All of those are pinned here.

HASHES ARE OVER LF-NORMALISED TEXT. A text file checked out with CRLF
on Windows and LF on Linux is the same repository artifact, and hashing
the checkout bytes makes the same content produce different identities
on different machines. This is the exact trap that broke an AETH-02
launch: the controller hashed CRLF bytes while the pod downloaded the LF
blob, so a correct file failed its own checksum gate. Binary files are
hashed raw.
"""

import fnmatch
import gzip
import hashlib
import io
import json
import os
import subprocess
import tarfile

DEFAULT_EXCLUDES = ("__pycache__/*", "*.pyc", ".git/*", ".pytest_cache/*",
                    "*.egg-info/*", ".DS_Store",
                    # A built bundle left inside the module directory would
                    # be swept into the NEXT bundle, so the hash would
                    # change on every rebuild and "same content, same
                    # hash" would quietly stop being true. Build products
                    # belong outside the module; this is the guard for
                    # when someone forgets.
                    "dist/*", "build/*", "*.tar.gz")
TEXT_SUFFIXES = (".py", ".json", ".txt", ".md", ".yaml", ".yml", ".cfg",
                 ".ini", ".sh", ".csv")
# Fixed epoch for every archive member and for gzip itself.
FIXED_MTIME = 0


def is_text(path):
    return path.lower().endswith(TEXT_SUFFIXES)


def file_digest(path):
    """sha256 of the repository artifact: LF-normalised for text."""
    with open(path, "rb") as fh:
        data = fh.read()
    if is_text(path):
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest(), len(data)


def _excluded(rel, excludes):
    return any(fnmatch.fnmatch(rel, pat) or
               fnmatch.fnmatch(os.path.basename(rel), pat) for pat in excludes)


def enumerate_files(module_dir, excludes=DEFAULT_EXCLUDES):
    """Every bundled file, relative, sorted. Sorting is what makes the
    archive order independent of the filesystem's walk order."""
    out = []
    for root, dirs, names in os.walk(module_dir):
        dirs.sort()
        for name in sorted(names):
            full = os.path.join(root, name)
            rel = os.path.relpath(full, module_dir).replace(os.sep, "/")
            if _excluded(rel, excludes):
                continue
            out.append(rel)
    return sorted(out)


def git_identity(module_dir):
    """Commit and cleanliness of the module's directory, when in a repo.

    Recorded, never required: a module may legitimately live outside a
    checkout. `dirty` is reported honestly rather than suppressed,
    because a bundle built from a dirty tree is reproducible only from
    the bundle itself.
    """
    def run(args):
        try:
            out = subprocess.run(args, cwd=module_dir, capture_output=True,
                                 timeout=30)
            return out.stdout.decode("utf-8", "replace").strip() if out.returncode == 0 else None
        except Exception:
            return None

    commit = run(["git", "rev-parse", "HEAD"])
    if commit is None:
        return {"available": False}
    status = run(["git", "status", "--porcelain", "--", "."])
    return {"available": True, "commit": commit,
            "dirty": bool(status), "dirty_paths": (status or "").splitlines()[:10]}


def build_manifest(module_dir, spec, excludes=DEFAULT_EXCLUDES):
    """The canonical description of what is in the bundle."""
    files = []
    total = 0
    for rel in enumerate_files(module_dir, excludes):
        digest, size = file_digest(os.path.join(module_dir, rel))
        files.append({"path": rel, "sha256": digest, "bytes": size})
        total += size
    entry = spec["entrypoint"]
    if entry not in [f["path"] for f in files]:
        raise FileNotFoundError(
            "entrypoint %r is not in the bundle; the module would start and "
            "immediately fail on the pod" % (entry,))
    manifest = {
        "schema": "prometheus-gpu/bundle-manifest/1",
        "module": spec.name,
        "version": spec.version,
        "entrypoint": entry,
        "file_count": len(files),
        "total_bytes": total,
        "files": files,
        "spec_sha256": hashlib.sha256(spec.canonical_json()).hexdigest(),
        "git": git_identity(module_dir),
        "dependencies": spec["dependencies"],
    }
    manifest["manifest_sha256"] = hashlib.sha256(
        json.dumps({k: v for k, v in manifest.items()
                    if k != "manifest_sha256"},
                   sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return manifest


def build_archive(module_dir, manifest, excludes=DEFAULT_EXCLUDES):
    """Deterministic .tar.gz bytes plus the bundle sha256.

    Every member gets a fixed mtime, uid/gid 0, empty owner names and a
    normalised mode; members are added in sorted order; gzip is given an
    explicit mtime of 0. Without all five, the same content produces a
    different bundle hash on every build.
    """
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.GNU_FORMAT) as tar:
        for rec in manifest["files"]:
            full = os.path.join(module_dir, rec["path"])
            with open(full, "rb") as fh:
                data = fh.read()
            if is_text(full):
                data = data.replace(b"\r\n", b"\n")
            info = tarfile.TarInfo(name=rec["path"])
            info.size = len(data)
            info.mtime = FIXED_MTIME
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mode = 0o755 if rec["path"].endswith(".sh") else 0o644
            tar.addfile(info, io.BytesIO(data))
    packed = io.BytesIO()
    with gzip.GzipFile(fileobj=packed, mode="wb", mtime=FIXED_MTIME,
                       compresslevel=9) as gz:
        gz.write(raw.getvalue())
    blob = packed.getvalue()
    return blob, hashlib.sha256(blob).hexdigest()


class Bundle(object):
    def __init__(self, spec, manifest, blob, digest):
        self.spec = spec
        self.manifest = manifest
        self.blob = blob
        self.sha256 = digest

    @property
    def bytes(self):
        return len(self.blob)

    def summary(self):
        return {
            "module": self.spec.identity,
            "bundle_sha256": self.sha256,
            "bundle_bytes": self.bytes,
            "file_count": self.manifest["file_count"],
            "manifest_sha256": self.manifest["manifest_sha256"],
            "spec_sha256": self.manifest["spec_sha256"],
            "git": self.manifest["git"],
        }


def build(module_dir, spec, excludes=DEFAULT_EXCLUDES):
    manifest = build_manifest(module_dir, spec, excludes)
    blob, digest = build_archive(module_dir, manifest, excludes)
    return Bundle(spec, manifest, blob, digest)
