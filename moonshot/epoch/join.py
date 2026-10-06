"""D5: node auto-join without auto-authorization (CONTRACT s8; design v0.3 N3/N7; C-008-T005).

A node needs Python, git, a CLEAN pinned checkout of the code, read access to the approval ref (production:
origin/main) and a data-plane credential. Joining:
  1. refuses a dirty checkout (local edits are not approved code) and code that is not an ancestor of the
     approval ref -- and, from the CLI, code that is not the code actually running;
  2. announces the node under refs/moonshot/<ns>/nodes/<node>: liveness only, it grants nothing;
  3. drains the namespace's chains with WORKER-role workers whose approval oracle is the same ancestry test.
Joining never creates chains, validates, resolves or approves: every store it builds is WORKER role."""
import os
import platform
import re
import subprocess
import sys
import threading
import time

from . import bench
from .store import NAME_RE, WORKER, Store, check_remote

_SHA = re.compile(r"^[0-9a-f]{40}$")


class JoinRefused(Exception):
    """The node may not join: dirty checkout, unapproved code, or a missing prerequisite."""


def _git(code_dir, *args, timeout=120):
    return subprocess.run(["git", "-C", code_dir] + list(args), capture_output=True, timeout=timeout)


class AncestryOracle:
    """approved(sha) iff sha names a commit that is an ancestor of approval_ref in code_dir. Unknown objects
    and malformed names are never approved. Only approvals are cached: if the approval ref advances, a
    refusal can become an approval, never the reverse."""

    def __init__(self, code_dir, approval_ref):
        self.code_dir, self.approval_ref, self._yes = code_dir, approval_ref, set()

    def __call__(self, sha) -> bool:
        if not isinstance(sha, str) or not _SHA.match(sha):
            return False
        if sha in self._yes:
            return True
        if _git(self.code_dir, "merge-base", "--is-ancestor", sha, self.approval_ref).returncode == 0:
            self._yes.add(sha)
            return True
        return False


def code_identity(code_dir):
    """(HEAD sha, dirty) of a checkout; untracked files are ignored because nothing imports them."""
    head = _git(code_dir, "rev-parse", "HEAD")
    if head.returncode != 0:
        raise JoinRefused("not a git checkout: {}".format(code_dir))
    status = _git(code_dir, "status", "--porcelain", "--untracked-files=no")
    if status.returncode != 0:
        raise JoinRefused("cannot read the checkout status of {}".format(code_dir))
    return head.stdout.decode().strip(), bool(status.stdout.strip())


def running_code_inside(code_dir) -> bool:
    """Is the moonshot package this process imported located inside code_dir? Otherwise approving
    code_dir says nothing about the code that runs."""
    here = os.path.normcase(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    there = os.path.normcase(os.path.abspath(code_dir))
    try:
        return os.path.commonpath([here, there]) == there
    except ValueError:                                      # different drives
        return False


def preflight(code_dir, approval_ref) -> dict:
    if sys.version_info < (3, 10):
        raise JoinRefused("python >= 3.10 is required")
    try:
        gv = subprocess.run(["git", "--version"], capture_output=True, timeout=30).stdout.decode().strip()
    except OSError:
        raise JoinRefused("git is required") from None
    sha, dirty = code_identity(code_dir)
    if dirty:
        raise JoinRefused("the checkout has local modifications; local edits are not approved code")
    if not AncestryOracle(code_dir, approval_ref)(sha):
        raise JoinRefused("code {} is not an ancestor of {}".format(sha[:12], approval_ref))
    return {"code_sha": sha, "python": platform.python_version(), "git": gv, "host": platform.node(),
            "platform": platform.platform()}


def node_store(remote, *, namespace, layout, local_dir, node_id) -> Store:
    """Every store a joined node builds is a WORKER store: it cannot create, validate or resolve."""
    return Store(remote, namespace=namespace, layout=layout, local_dir=local_dir, role=WORKER, actor=node_id)


def join(remote, *, namespace, layout, code_dir, approval_ref="origin/main", node_id=None, workers=1, duration_s,
         data_dir, leases=True, ttl=60, host_label=None, fetch=False, bind_running_code=False) -> dict:
    check_remote(remote)                                    # before anything touches the disk
    node_id = node_id or (re.sub(r"[^A-Za-z0-9_-]", "-", platform.node())[:40] or "node")
    if not NAME_RE.match(node_id):
        raise JoinRefused("node_id must match " + NAME_RE.pattern)
    if fetch and _git(code_dir, "fetch", "-q", "origin").returncode != 0:
        raise JoinRefused("could not fetch the approval ref's remote")
    if bind_running_code and not running_code_inside(code_dir):
        raise JoinRefused("the running moonshot package is not inside {}".format(code_dir))
    info = preflight(code_dir, approval_ref)
    oracle = AncestryOracle(code_dir, approval_ref)
    os.makedirs(data_dir, exist_ok=True)
    st = node_store(remote, namespace=namespace, layout=layout, local_dir=os.path.join(data_dir, "announce"),
                    node_id=node_id)
    try:
        st.announce_node(node_id, dict(info, workers=workers, joined_unix=int(time.time()),
                                       approval_ref=approval_ref, layout=layout, namespace=namespace))
        chains = sorted(s[len("chains/"):] for s in st.list_slots("chains/"))
    finally:
        st.close()
    summaries = []

    def run(i):
        wid = "{}-w{}".format(node_id, i)[:64]
        ws = node_store(remote, namespace=namespace, layout=layout, local_dir=os.path.join(data_dir, wid),
                        node_id=node_id)
        try:
            summaries.append(bench.bench_worker(
                ws, wid, chains, code_sha=info["code_sha"], approved=oracle,
                spool_dir=os.path.join(data_dir, "spool-" + wid), leases=leases, duration_s=duration_s,
                lease_ttl_s=ttl, start=i * max(1, len(chains) // max(1, workers)), host_label=host_label))
        finally:
            ws.close()

    if chains:
        threads = [threading.Thread(target=run, args=(i,)) for i in range(workers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    return {"node_id": node_id, "code_sha": info["code_sha"], "chains": len(chains), "workers": summaries}
