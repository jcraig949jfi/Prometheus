"""Test harness for the D3 matrix: real git, real bare remotes in a temp directory.

The adversary-side helpers (tampering, refs, offline) use RAW git, never the package under test."""
import os
import shutil
import stat
import subprocess
import tempfile

from moonshot.epoch import model, runtime
from moonshot.epoch import store as S
from moonshot.epoch import worker as W

APPROVED_SHA = "c0de" * 10
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def git(*args, cwd=None, input_=None):
    r = subprocess.run(["git"] + list(args), cwd=cwd, input=input_, capture_output=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError("git {} failed: {}".format(" ".join(args), r.stderr.decode(errors="replace")[:400]))
    return r.stdout


class FakeClock:
    def __init__(self, t=1_700_000_000):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds


class OffsetClock:
    def __init__(self, base, offset):
        self.base, self.offset = base, offset

    def __call__(self):
        return self.base() + self.offset


class CountingRunner:
    """Wraps a runner (default: the real synthetic.v1) and counts invocations."""

    def __init__(self, inner=None):
        self.inner = inner
        self.calls = 0

    def __call__(self, input_checkpoint, spec):
        self.calls += 1
        return (self.inner or runtime.run_synthetic_v1)(input_checkpoint, spec)


def planted_runner(flip_at=0):
    """Claims synthetic.v1 but flips one checkpoint bit: a faulty host or a drifted library, not a new runtime."""

    def run(input_checkpoint, spec):
        trace, ckpt = runtime.run_synthetic_v1(input_checkpoint, spec)
        b = bytearray(ckpt)
        b[flip_at % max(1, len(b))] ^= 0x01
        return trace, bytes(b)

    return run


def _rm_readonly(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


class Harness:
    def __init__(self, layout, leases=True, namespace="t"):
        self.dir = tempfile.mkdtemp(prefix="mse-")
        self.remote = os.path.join(self.dir, "remote.git")
        self.dead_url = os.path.join(self.dir, "no-such-remote.git")
        git("init", "-q", "--bare", self.remote)
        self.layout, self.leases, self.ns = layout, leases, namespace
        self.clock = FakeClock()
        self._stores = []
        self.coordinator = self.store("coordinator", role=S.COORDINATOR)

    # -------------------------------------------------------------------------------------------- fixtures

    def cleanup(self):
        for st in self._stores:
            try:
                st.close()
            except Exception:
                pass
        if os.path.isdir(self.remote + ".offline"):
            os.rename(self.remote + ".offline", self.remote)
        shutil.rmtree(self.dir, onerror=_rm_readonly)

    def store(self, name, role=S.WORKER, url=None, push_hook=None):
        st = S.Store(url or self.remote, namespace=self.ns, layout=self.layout,
                     local_dir=os.path.join(self.dir, "local-" + name), role=role, actor=name, push_hook=push_hook)
        self._stores.append(st)
        return st

    def validator(self):
        return self.store("validator", role=S.VALIDATOR)

    def resolver(self):
        return self.store("resolver", role=S.RESOLVER)

    def chain(self, chain_id="C1", epochs=3, iterations=40, checkpoint_bytes=64, approved=APPROVED_SHA,
              runtime_=None, initial=b"genesis\n"):
        kw = {"runtime": runtime_} if runtime_ else {}
        g = model.make_genesis(chain_id, epochs=epochs,
                               params={"work_iterations": iterations, "trace_every": 10,
                                       "checkpoint_bytes": checkpoint_bytes},
                               approved_code_sha=approved, initial_checkpoint=initial + chain_id.encode(), **kw)
        self.coordinator.create_chain(g)
        return g

    def worker(self, wid, *, clock_offset=0, clock=None, leases=None, respect_leases=True, runner=None, faults=None,
               host_label=None, code_sha=APPROVED_SHA, approved=(APPROVED_SHA,), url=None, ttl=60):
        st = self.store(wid, url=url)
        w = W.Worker(st, wid, code_sha=code_sha, approved=set(approved),
                     spool_dir=os.path.join(self.dir, "spool-" + wid),
                     clock=clock or OffsetClock(self.clock, clock_offset),
                     leases=self.leases if leases is None else leases, respect_leases=respect_leases,
                     lease_ttl_s=ttl, runner=runner, faults=faults, host_label=host_label)
        w._harness_kw = dict(clock_offset=clock_offset, clock=clock, leases=leases, respect_leases=respect_leases,
                             host_label=host_label, code_sha=code_sha, approved=approved, url=url, ttl=ttl)
        return w

    def restart(self, worker, runner=None):
        """The same worker id, local repository and spool, after a process death: no faults, honest runner."""
        worker.store.close()
        return self.worker(worker.worker_id, runner=runner, **worker._harness_kw)

    # -------------------------------------------------------------------------------------------- remote, raw git

    def take_remote_offline(self):
        os.rename(self.remote, self.remote + ".offline")

    def bring_remote_online(self):
        os.rename(self.remote + ".offline", self.remote)

    def remote_refs(self):
        out = git("--git-dir", self.remote, "for-each-ref", "--format=%(refname) %(objectname)")
        return dict(line.split(" ", 1) for line in out.decode().splitlines() if line.strip())

    def read_remote_blob(self, ref, path):
        return git("--git-dir", self.remote, "cat-file", "blob", "{}:{}".format(ref, path))

    def assert_remote_consistent(self, testcase):
        """No partial state: every object reachable from every ref is present and well formed."""
        git("--git-dir", self.remote, "fsck", "--no-dangling", "--no-progress")
        for ref in self.remote_refs():
            testcase.assertTrue(ref.startswith("refs/moonshot/{}/".format(self.ns)), ref)

    def tamper_head(self, chain_id):
        """Replace the published head's TRACE bytes, keeping its MANIFEST: transport-level corruption."""
        g = ["--git-dir", self.remote]
        if self.layout == S.PER_CHAIN:
            ref = "refs/moonshot/{}/chains/{}".format(self.ns, chain_id)
            head = git(*g, "rev-parse", ref).decode().strip()
        else:
            ref = "refs/moonshot/{}/index".format(self.ns)
            tip = git(*g, "rev-parse", ref).decode().strip()
            head = git(*g, "cat-file", "blob", "{}:chains/{}".format(tip, chain_id)).decode().strip()
        bad = git(*g, "hash-object", "-w", "--stdin", input_=b"forged trace\n").decode().strip()
        entries = []
        for line in git(*g, "ls-tree", head).decode().splitlines():
            meta, name = line.split("\t", 1)
            mode, typ, sha = meta.split()
            entries.append("{} {} {}\t{}".format(mode, typ, bad if name == "TRACE" else sha, name))
        tree = git(*g, "mktree", input_=("\n".join(entries) + "\n").encode()).decode().strip()
        parent = git(*g, "rev-parse", head + "^").decode().strip()
        env = dict(os.environ, GIT_AUTHOR_NAME="x", GIT_AUTHOR_EMAIL="x@x", GIT_COMMITTER_NAME="x",
                   GIT_COMMITTER_EMAIL="x@x")
        r = subprocess.run(["git", "--git-dir", self.remote, "commit-tree", tree, "-p", parent, "-m", "tampered"],
                           capture_output=True, env=env, timeout=60)
        forged = r.stdout.decode().strip()
        if self.layout == S.PER_CHAIN:
            git(*g, "update-ref", ref, forged)
            return forged
        blob = git(*g, "hash-object", "-w", "--stdin", input_=(forged + "\n").encode()).decode().strip()
        root = []
        for line in git(*g, "ls-tree", tip).decode().splitlines():
            meta, name = line.split("\t", 1)
            mode, typ, sha = meta.split()
            if name == "chains":
                sub = []
                for sl in git(*g, "ls-tree", sha).decode().splitlines():
                    smeta, sname = sl.split("\t", 1)
                    smode, styp, ssha = smeta.split()
                    sub.append("{} {} {}\t{}".format(smode, styp, blob if sname == chain_id else ssha, sname))
                sha = git(*g, "mktree", input_=("\n".join(sub) + "\n").encode()).decode().strip()
            root.append("{} {} {}\t{}".format(mode, typ, sha, name))
        rtree = git(*g, "mktree", input_=("\n".join(root) + "\n").encode()).decode().strip()
        r = subprocess.run(["git", "--git-dir", self.remote, "commit-tree", rtree, "-p", tip, "-p", forged,
                            "-m", "tampered"], capture_output=True, env=env, timeout=60)
        git(*g, "update-ref", ref, r.stdout.decode().strip())
        return forged
