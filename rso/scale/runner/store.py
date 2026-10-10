"""Durable bytes on one host (C-013-T022): a content-addressed object store, atomic JSON, append-only JSONL, and
a lock file. Architecture s3.6 names the retained store as the missing component; this is its LOCAL layout (a
sha256-addressed directory tree) without the network part, so the same keys move to a remote store unchanged.

Every write survives a kill at any instant: objects and JSON are written to a temporary file, fsynced and
renamed; a JSONL row is one fsynced append, and a reader skips a torn (partially written) row and counts it.
"""
import hashlib
import json
import os
import socket
import time
import uuid

import psutil

HOST = socket.gethostname()


class IntegrityError(Exception):
    """Bytes that do not hash to their key, a missing object, or a write-once violation."""


def _fsync_dir(path):
    if os.name != "nt":                                         # directory fsync is a POSIX notion
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def _replace(src, dst):
    # Windows refuses a rename onto a file another process has open for a moment; retry briefly.
    for i in range(200):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if i == 199:
                raise
            time.sleep(0.01)


def atomic_write_bytes(path, data):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    tmp = os.path.join(d, ".tmp-{}-{}".format(os.getpid(), uuid.uuid4().hex[:8]))
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    _replace(tmp, path)
    _fsync_dir(d)


def atomic_write_json(path, obj):
    atomic_write_bytes(path, (json.dumps(obj, sort_keys=True, indent=1) + "\n").encode("utf-8"))


def read_json(path):
    for i in range(200):
        try:
            with open(path, "rb") as f:
                return json.loads(f.read().decode("utf-8"))
        except PermissionError:                                 # mid-rename on Windows
            if i == 199:
                raise
            time.sleep(0.01)


def append_jsonl(path, obj):
    """One fsynced row. If the file ends in a torn row (its writer was killed mid-write), the torn row is sealed
    with a newline first, so it stays one unparseable line instead of corrupting this one."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    line = (json.dumps(obj, sort_keys=True) + "\n").encode("utf-8")
    with open(path, "ab+") as f:
        f.seek(0, os.SEEK_END)
        if f.tell() > 0:
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                f.write(b"\n")
        f.write(line)
        f.flush()
        os.fsync(f.fileno())


def read_jsonl(path):
    """(rows, torn): every parseable row in order, and the count of lines that were not (killed writers)."""
    rows, torn = [], 0
    if not os.path.exists(path):
        return rows, torn
    with open(path, "rb") as f:
        data = f.read()
    for raw in data.split(b"\n"):
        if not raw.strip():
            continue
        try:
            rows.append(json.loads(raw.decode("utf-8")))
        except (UnicodeDecodeError, ValueError):
            torn += 1
    return rows, torn


class ObjectStore:
    """root/<sha[:2]>/<sha>. Write-once (an existing key with different bytes is refused); verified on read."""

    def __init__(self, root):
        self.root = root

    def path(self, sha):
        return os.path.join(self.root, sha[:2], sha)

    def put(self, data):
        data = bytes(data)
        sha = hashlib.sha256(data).hexdigest()
        p = self.path(sha)
        if os.path.exists(p):
            with open(p, "rb") as f:
                if f.read() != data:
                    raise IntegrityError("object {} exists with different bytes".format(sha))
            return sha
        atomic_write_bytes(p, data)
        return sha

    def get(self, sha):
        p = self.path(sha)
        try:
            with open(p, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            raise IntegrityError("object {} is missing".format(sha)) from None
        if hashlib.sha256(data).hexdigest() != sha:
            raise IntegrityError("object {} does not hash to its key".format(sha))
        return data

    def total_bytes(self):
        n = 0
        for d, _, files in os.walk(self.root):
            n += sum(os.path.getsize(os.path.join(d, f)) for f in files if not f.startswith(".tmp-"))
        return n


def pid_alive(pid, create_time=None):
    """A process with this pid exists (and, when known, was created at create_time: pid reuse is not life)."""
    try:
        p = psutil.Process(pid)
        if create_time is not None and abs(p.create_time() - create_time) > 0.5:
            return False
        return p.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
        return False


def my_identity():
    return {"pid": os.getpid(), "create_time": psutil.Process(os.getpid()).create_time(), "host": HOST}


class FileLock:
    """Mutual exclusion between processes on one host: an O_EXCL lock file naming its holder. A lock whose
    holder is dead (killed while holding it) is broken; a live holder is waited for."""

    def __init__(self, path, timeout=60.0):
        self.path, self.timeout = path, timeout

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        deadline = time.time() + self.timeout
        me = json.dumps(my_identity()).encode("utf-8")
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(fd, me)
                finally:
                    os.close(fd)
                return self
            except (FileExistsError, PermissionError):          # PermissionError: Windows, file mid-delete
                try:
                    with open(self.path, "rb") as f:
                        holder = json.loads(f.read().decode("utf-8") or "{}")
                except (OSError, ValueError):
                    holder = {}
                if holder and holder.get("host") == HOST and not pid_alive(holder["pid"], holder.get("create_time")):
                    try:
                        os.remove(self.path)                    # its holder was killed while holding it
                    except OSError:
                        pass
                    continue
                if time.time() > deadline:
                    raise TimeoutError("lock {} held by {}".format(self.path, holder))
                time.sleep(0.005)

    def __exit__(self, *exc):
        for i in range(200):
            try:
                os.remove(self.path)
            except FileNotFoundError:
                break
            except PermissionError:                             # Windows: a waiter has it open to read the holder
                if i == 199:
                    raise
                time.sleep(0.01)
            else:
                break
        return False
