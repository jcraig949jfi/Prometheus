"""Git objects written directly from bytes, and remote operations with classified errors (CONTRACT s3).

LocalRepo is a bare scratch repository owned by one worker. Objects are written in Python (zlib +
SHA-1 over git's object format), so no working tree, filter or line-ending conversion ever touches the
bytes. Reads go through one persistent `git cat-file --batch`. Every remote operation is timed and its
transferred bytes parsed from git's progress output into an OpLog (D4's raw material)."""
import hashlib
import os
import re
import subprocess
import time
import zlib
from dataclasses import dataclass, field


class GitError(Exception):
    """A git operation failed."""


class RemoteUnavailable(GitError):
    """The remote could not be reached; nothing is known to have changed there."""


class AmbiguousPush(GitError):
    """A push gave no definitive answer; it may or may not have applied (CONTRACT s4)."""


class AuthError(GitError):
    """The remote refused the credential."""


class RateLimited(GitError):
    """The remote throttled us (a T004 stop condition)."""


class ForbiddenRef(GitError):
    """A ref outside refs/moonshot/<namespace>/ (CONTRACT s3)."""


class ForbiddenRemote(GitError):
    """A remote on the denylist, e.g. the Prometheus repository (OP-LC1 #1)."""


class MissingRef(GitError):
    """A fetched ref does not exist on the remote (it was deleted or never created)."""


FIXED_IDENT = "moonshot-epoch <epoch@moonshot.invalid>"
FIXED_WHEN = "1000000000 +0000"
_GIT_ENV = {"GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C", "LANG": "C", "GIT_CONFIG_NOSYSTEM": "1"}
_UNITS = {"bytes": 1, "byte": 1, "KiB": 1024, "MiB": 1024 ** 2, "GiB": 1024 ** 3}
_PROGRESS = re.compile(r"(Writing|Receiving|Unpacking) objects:\s+100% \(\d+/\d+\), ([\d.]+) (bytes|byte|KiB|MiB|GiB)")


@dataclass
class Op:
    kind: str
    wall_s: float
    ok: bool
    bytes_sent: int = 0
    bytes_received: int = 0
    cpu_s: float = None
    detail: str = ""


@dataclass
class OpLog:
    ops: list = field(default_factory=list)

    def mark(self) -> int:
        return len(self.ops)

    def since(self, mark: int) -> list:
        return self.ops[mark:]


@dataclass
class PushResult:
    applied: bool                                   # every requested ref update applied
    refs: dict                                      # dst -> (flag, summary)
    rejected: list
    stderr: str = ""


def _transfer_bytes(err: str):
    sent = received = 0
    for part in re.split(r"[\r\n]", err):
        m = _PROGRESS.search(part)
        if m:
            n = int(float(m.group(2)) * _UNITS[m.group(3)])
            if m.group(1) == "Writing":
                sent = max(sent, n)
            else:
                received = max(received, n)
    return sent, received


def _classify(err: str, is_push: bool):
    s = err.lower()
    if "429" in s or "rate limit" in s or "secondary rate" in s or "abuse detection" in s:
        return RateLimited
    if ("authentication failed" in s or "permission denied" in s or "could not read username" in s
            or "invalid username or password" in s or "error: 403" in s or "returned error: 403" in s):
        return AuthError
    if "couldn't find remote ref" in s:
        return MissingRef
    if is_push and ("hung up" in s or "early eof" in s or "broken pipe" in s or "connection reset" in s
                    or "unexpected disconnect" in s):
        return AmbiguousPush
    return RemoteUnavailable


def _children_cpu():
    if os.name != "posix":
        return None
    t = os.times()
    return t.children_user + t.children_system


class LocalRepo:
    def __init__(self, path, oplog=None, timeout_s=120):
        self.path = os.path.abspath(path)
        self.oplog = oplog if oplog is not None else OpLog()
        self.timeout_s = timeout_s
        self.env = dict(os.environ, **_GIT_ENV)
        self._batch = None
        if not os.path.isfile(os.path.join(self.path, "HEAD")):
            os.makedirs(self.path, exist_ok=True)
            subprocess.run(["git", "init", "-q", "--bare", self.path], check=True, capture_output=True,
                           env=self.env, timeout=self.timeout_s)

    # ------------------------------------------------------------------------------------------- objects

    def _write(self, typ: str, data: bytes) -> str:
        raw = "{} {}\0".format(typ, len(data)).encode() + data
        sha = hashlib.sha1(raw).hexdigest()
        d = os.path.join(self.path, "objects", sha[:2])
        p = os.path.join(d, sha[2:])
        if not os.path.exists(p):
            os.makedirs(d, exist_ok=True)
            tmp = "{}.tmp{}".format(p, os.getpid())
            with open(tmp, "wb") as f:
                f.write(zlib.compress(raw))
                f.flush()
                os.fsync(f.fileno())
            try:
                os.replace(tmp, p)
            except OSError:
                if not os.path.exists(p):
                    raise
                os.remove(tmp)
        return sha

    def blob(self, data: bytes) -> str:
        return self._write("blob", bytes(data))

    def tree(self, entries: dict) -> str:
        """entries: name -> sha for blobs, or name -> ("tree", sha) for subtrees. Git's order: a tree
        sorts as if its name ended in '/'."""
        items = []
        for name, v in entries.items():
            mode, sha = ("40000", v[1]) if isinstance(v, tuple) else ("100644", v)
            items.append((name + ("/" if mode == "40000" else ""), mode, name, sha))
        items.sort(key=lambda x: x[0].encode("utf-8"))
        data = b"".join(mode.encode() + b" " + name.encode("utf-8") + b"\0" + bytes.fromhex(sha)
                        for _, mode, name, sha in items)
        return self._write("tree", data)

    def commit(self, tree: str, parents, message: str) -> str:
        lines = ["tree " + tree] + ["parent " + p for p in parents]
        lines += ["author {} {}".format(FIXED_IDENT, FIXED_WHEN), "committer {} {}".format(FIXED_IDENT, FIXED_WHEN),
                  "", message if message.endswith("\n") else message + "\n"]
        return self._write("commit", "\n".join(lines).encode("utf-8"))

    # ------------------------------------------------------------------------------------------- reads

    def _reader(self):
        if self._batch is None or self._batch.poll() is not None:
            self._batch = subprocess.Popen(["git", "--git-dir", self.path, "cat-file", "--batch"],
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=subprocess.DEVNULL, env=self.env)
        return self._batch

    def invalidate(self):
        """Forget the reader after a fetch so new packs are certainly visible."""
        if self._batch is not None:
            try:
                self._batch.stdin.close()
                self._batch.wait(timeout=10)
            except Exception:
                self._batch.kill()
            finally:
                try:
                    self._batch.stdout.close()
                except Exception:
                    pass
            self._batch = None

    def close(self):
        self.invalidate()

    def read(self, spec: str):
        """(type, bytes) for an object name or '<commit>:<path>', or None if absent."""
        p = self._reader()
        p.stdin.write(spec.encode("utf-8") + b"\n")
        p.stdin.flush()
        header = p.stdout.readline()
        if not header or header.rstrip().endswith((b" missing", b" ambiguous")):
            return None
        _, typ, size = header.split()
        data = p.stdout.read(int(size))
        p.stdout.read(1)
        return typ.decode(), data

    def has(self, sha: str) -> bool:
        return self.read(sha) is not None

    def read_blob(self, spec: str):
        r = self.read(spec)
        return r[1] if r and r[0] == "blob" else None

    def read_tree(self, sha: str) -> dict:
        """name -> sha for blobs, name -> ("tree", sha) for subtrees."""
        r = self.read(sha)
        if not r or r[0] != "tree":
            raise GitError("not a tree: " + sha)
        data, out, i = r[1], {}, 0
        while i < len(data):
            sp = data.index(b" ", i)
            nul = data.index(b"\0", sp)
            mode, name, osha = data[i:sp], data[sp + 1:nul].decode("utf-8"), data[nul + 1:nul + 21].hex()
            out[name] = ("tree", osha) if mode == b"40000" else osha
            i = nul + 21
        return out

    def read_commit(self, sha: str) -> dict:
        r = self.read(sha)
        if not r or r[0] != "commit":
            raise GitError("not a commit: " + sha)
        head, _, message = r[1].decode("utf-8").partition("\n\n")
        tree, parents = None, []
        for line in head.splitlines():
            if line.startswith("tree "):
                tree = line[5:]
            elif line.startswith("parent "):
                parents.append(line[7:])
        return {"tree": tree, "parents": parents, "message": message}

    # ------------------------------------------------------------------------------------------- remote

    def _run(self, args, kind, is_push=False):
        t0, c0 = time.monotonic(), _children_cpu()
        try:
            r = subprocess.run(["git", "--git-dir", self.path] + args, capture_output=True, env=self.env,
                               timeout=self.timeout_s)
        except subprocess.TimeoutExpired:
            self.oplog.ops.append(Op(kind, time.monotonic() - t0, False, detail="timeout"))
            raise (AmbiguousPush if is_push else RemoteUnavailable)(kind + " timed out")
        err = r.stderr.decode("utf-8", "replace")
        sent, received = _transfer_bytes(err)
        c1 = _children_cpu()
        self.oplog.ops.append(Op(kind, time.monotonic() - t0, r.returncode == 0, sent, received,
                                 None if c0 is None else c1 - c0, "" if r.returncode == 0 else err[-300:]))
        return r, err

    def ls_remote(self, url, patterns) -> dict:
        r, err = self._run(["ls-remote", url] + list(patterns), "ls-remote")
        if r.returncode != 0:
            raise _classify(err, False)("ls-remote: " + err.strip()[-300:])
        out = {}
        for line in r.stdout.decode().splitlines():
            if "\t" in line:
                sha, ref = line.split("\t", 1)
                out[ref] = sha
        return out

    def fetch(self, url, refspecs):
        r, err = self._run(["fetch", "--no-tags", "--progress", "--no-write-fetch-head", url] + list(refspecs),
                           "fetch")
        self.invalidate()
        if r.returncode != 0:
            raise _classify(err, False)("fetch: " + err.strip()[-300:])

    def push(self, url, updates) -> PushResult:
        """updates: [(src_sha or None to delete, dst_ref, expect)] where expect is None (no lease), "" (the
        ref must not exist) or a sha (the ref must equal it). A lease makes the update a true CAS."""
        args = ["push", "--porcelain", "--progress"]
        for src, dst, expect in updates:
            if expect is not None:
                args.append("--force-with-lease={}:{}".format(dst, expect))
        args.append(url)
        args += ["{}:{}".format(src, dst) if src else ":" + dst for src, dst, _ in updates]
        r, err = self._run(args, "push", is_push=True)
        refs = {}
        for line in r.stdout.decode("utf-8", "replace").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3 and len(parts[0]) == 1:
                refs[parts[1].split(":", 1)[-1]] = (parts[0], parts[2])
        if not refs:
            if r.returncode == 0:
                raise AmbiguousPush("push reported no ref status")
            raise _classify(err, True)("push: " + err.strip()[-300:])
        rejected = [d for _, d, _ in updates if refs.get(d, ("!", ""))[0] == "!"]
        for d in rejected:
            summary = refs.get(d, ("", ""))[1].lower()
            if "permission" in summary or "denied" in summary:
                raise AuthError("push rejected: " + summary)
        missing = [d for _, d, _ in updates if d not in refs]
        if missing:
            raise AmbiguousPush("push did not report " + ", ".join(missing))
        return PushResult(not rejected, refs, rejected, err)
