"""Slots on a dedicated remote, under refs/moonshot/<namespace>/ (CONTRACT s3).

Every coordination object is a SLOT whose value is a commit, changed only by compare-and-swap:
chains/<chain>, leases/<chain>, contest/<chain>, validation/<chain>, receipts/<worker>.

PER_CHAIN: one ref per slot; CAS = `git push --force-with-lease=<ref>:<expected>`.
SINGLE_REF: one ref, refs/moonshot/<ns>/index, whose tree holds a pointer file per slot; each index commit
also takes the slot's new commit as a parent so it stays reachable. CAS on a slot is a CAS on the whole
index: when the index moved but the slot did not, the writer rebuilds on the new tip and retries (a
CONTENTION retry). That is workgraph's claim-is-a-push-to-main, emulated off the production repository.

Unique, never-contended refs: staging/<attempt>, quarantine/<chain>/<k>/<attempt>, rejected/<chain>/<k>.
Roles are enforced here; a remote cannot tell roles apart, which is why a push grants nothing (s6, s8)."""
import json
import re
from dataclasses import dataclass
from typing import Optional

from . import canonical as C
from .gitio import (AmbiguousPush, ForbiddenRef, ForbiddenRemote, GitError, LocalRepo,  # noqa: F401
                    MissingRef, RemoteUnavailable)

PER_CHAIN = "per_chain"
SINGLE_REF = "single_ref"
LAYOUTS = (PER_CHAIN, SINGLE_REF)

WORKER = "worker"
COORDINATOR = "coordinator"
VALIDATOR = "validator"
RESOLVER = "resolver"
ROLES = (WORKER, COORDINATOR, VALIDATOR, RESOLVER)

# OP-LC1 #1: never the Prometheus repository. A remote is refused if its normalized URL (lowercase, "\\" and ":"
# as "/", no trailing "/" or ".git") contains a denylisted path, OR its last path segment is "prometheus" -- which
# also refuses a local clone such as D:\Prometheus used by mistake as the data-plane remote.
DEFAULT_DENYLIST = ("jcraig949jfi/prometheus",)

OPEN_CONTEST_STATES = ("CONTESTED", "TAINTED", "UNRESOLVED")
MAX_CONTENTION = 64
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


class Contention(GitError):
    """SINGLE_REF: the index kept moving for MAX_CONTENTION retries."""


@dataclass(frozen=True)
class PublishedEpoch:
    epoch_index: int
    commit: str
    manifest: dict
    work_id: str
    epoch_digest: str


@dataclass(frozen=True)
class ChainView:
    chain_id: str
    head_commit: str
    head_index: int
    genesis_obj: dict
    contest: Optional[dict]

    @property
    def halted(self) -> bool:
        return bool(self.contest) and self.contest.get("state") in OPEN_CONTEST_STATES

    @property
    def complete(self) -> bool:
        return self.head_index >= self.genesis_obj["epochs"]


@dataclass(frozen=True)
class CasResult:
    applied: bool
    current: Optional[str]
    retries: int = 0


def check_remote(url, denylist=DEFAULT_DENYLIST):
    n = str(url).strip().lower().replace("\\", "/").replace(":", "/").rstrip("/")
    if n.endswith(".git"):
        n = n[:-4].rstrip("/")
    if n.rsplit("/", 1)[-1] == "prometheus" or any(d.lower() in n for d in denylist):
        raise ForbiddenRemote("refusing data-plane remote {!r} (OP-LC1 #1)".format(url))


def _jbytes(obj) -> bytes:
    """Coordination records: canonical when integer-only, else sorted compact JSON (receipts carry floats)."""
    try:
        return C.canonical_bytes(obj)
    except C.CanonicalError:
        return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


class Store:
    def __init__(self, remote_url, *, namespace, layout, local_dir, role=WORKER, actor="",
                 denylist=DEFAULT_DENYLIST, push_hook=None):
        check_remote(remote_url, denylist)                  # before anything touches the disk
        if not NAME_RE.match(namespace or ""):
            raise ValueError("namespace must match " + NAME_RE.pattern)
        if layout not in LAYOUTS or role not in ROLES:
            raise ValueError("unknown layout or role")
        self.remote_url = remote_url
        self.namespace = namespace
        self.layout = layout
        self.local_dir = local_dir
        self.role = role
        self.actor = actor
        self.denylist = tuple(denylist)
        self.push_hook = push_hook
        self.repo = LocalRepo(local_dir)
        self.ops = self.repo.oplog
        self.push_attempts = 0
        self.contention_retries = 0
        self.ambiguity_resolutions = 0
        self._tip, self._root, self._slots = None, {}, {}   # SINGLE_REF view
        self._pointers = {}                                   # pointer blob -> commit
        self._memo = {}                                       # commit -> (index, parent, root)
        self._manifests = {}
        self._geneses = {}

    def close(self):
        self.repo.close()

    # ------------------------------------------------------------------------------------------- refs, roles

    def ref(self, *parts) -> str:
        return "refs/moonshot/{}/{}".format(self.namespace, "/".join(parts))

    def _guard(self, ref):
        if not ref.startswith("refs/moonshot/{}/".format(self.namespace)) or ".." in ref:
            raise ForbiddenRef(ref)

    def _require(self, *roles):
        if self.role not in roles:
            raise PermissionError("a {} store may not do this (needs {})".format(self.role, "/".join(roles)))

    def _push(self, updates, wrap=None):
        for _, dst, _ in updates:
            self._guard(dst)

        def real():
            self.push_attempts += 1
            if self.push_hook:
                return self.push_hook(self.repo.push, self.remote_url, updates)
            return self.repo.push(self.remote_url, updates)

        return wrap(real) if wrap else real()

    # ------------------------------------------------------------------------------------------- reading refs

    def _read_refs(self, refs, glob=None) -> dict:
        """Current remote values (ls-remote), fetching whatever objects we lack."""
        for _ in range(4):
            found = self.repo.ls_remote(self.remote_url, [glob] if glob else refs)
            if glob is None:
                found = {r: found.get(r) for r in refs}
            need = [r for r, v in found.items() if v and not self.repo.has(v)]
            if not need:
                return found
            try:
                specs = ["+{}:refs/view/{}".format(glob, glob[len("refs/moonshot/"):])] if glob else \
                        ["+{}:refs/view/{}".format(r, r[len("refs/moonshot/"):]) for r in need]
                self.repo.fetch(self.remote_url, specs)
            except MissingRef:
                continue
            if all(self.repo.has(found[r]) for r in need):
                return found
        raise RemoteUnavailable("refs kept moving under the fetch")

    def _pointer(self, blob_sha) -> str:
        if blob_sha not in self._pointers:
            self._pointers[blob_sha] = self.repo.read_blob(blob_sha).decode("ascii").strip()
        return self._pointers[blob_sha]

    def _refresh_index(self):
        tip = self._read_refs([self.ref("index")])[self.ref("index")]
        if tip == self._tip and tip is not None:
            return
        root, slots = {}, {}
        if tip:
            root = self.repo.read_tree(self.repo.read_commit(tip)["tree"])
            for d, v in root.items():
                if isinstance(v, tuple):
                    for name, b in self.repo.read_tree(v[1]).items():
                        if not isinstance(b, tuple):
                            slots[d + "/" + name] = self._pointer(b)
        self._tip, self._root, self._slots = tip, root, slots

    def read_slots(self, slots) -> dict:
        if self.layout == PER_CHAIN:
            vals = self._read_refs([self.ref(s) for s in slots])
            return {s: vals[self.ref(s)] for s in slots}
        self._refresh_index()
        return {s: self._slots.get(s) for s in slots}

    def list_slots(self, prefix) -> dict:
        if self.layout == PER_CHAIN:
            vals = self._read_refs(None, glob=self.ref(prefix + "*"))
            base = len(self.ref(""))
            return {r[base:]: v for r, v in vals.items() if v}
        self._refresh_index()
        return {s: v for s, v in self._slots.items() if s.startswith(prefix)}

    # ------------------------------------------------------------------------------------------- slot CAS

    def _index_tree_with(self, slot, new) -> str:
        d, name = slot.split("/", 1)
        root = dict(self._root)
        sub = self.repo.read_tree(root[d][1]) if d in root else {}
        if new:
            sub[name] = self.repo.blob((new + "\n").encode("ascii"))
        else:
            sub.pop(name, None)
        if sub:
            root[d] = ("tree", self.repo.tree(sub))
        else:
            root.pop(d, None)
        return self.repo.tree(root)

    def cas_slot(self, slot, expected, new, wrap=None, resolve_ambiguity=True) -> CasResult:
        """Move `slot` from `expected` (None = absent) to `new` (None = delete). Applied, or the value that
        won. A lost acknowledgement is resolved by re-reading (slot = new: applied; slot = expected: not
        applied, sent again; anything else: rejected) unless resolve_ambiguity is False, as for the chain
        CAS, whose AmbiguousPush the worker resolves and attributes itself (CONTRACT s4). Commits are
        unique per writer, so "slot = new" can only mean this write landed."""
        if self.layout == PER_CHAIN:
            for _ in range(4):
                try:
                    res = self._push([(new, self.ref(slot), expected or "")], wrap)
                except AmbiguousPush:
                    if not resolve_ambiguity:
                        raise
                    self.ambiguity_resolutions += 1
                    cur = self.read_slots([slot])[slot]
                    if cur == new:
                        return CasResult(True, new)
                    if cur != expected:
                        return CasResult(False, cur)
                    continue                                 # it did not apply: send it again
                if res.applied:
                    return CasResult(True, new)
                return CasResult(False, self.read_slots([slot])[slot])
            raise AmbiguousPush("CAS on {} stayed ambiguous".format(slot))
        retries, refreshed = 0, False
        if self._tip is None:
            self._refresh_index()
            refreshed = True
        while True:
            if self._slots.get(slot) != expected:
                if not refreshed:
                    self._refresh_index()
                    refreshed = True
                    continue
                self.contention_retries += retries
                return CasResult(False, self._slots.get(slot), retries)
            tip = self._tip
            tree = self._index_tree_with(slot, new)
            parents = ([tip] if tip else []) + ([new] if new else [])
            commit = self.repo.commit(tree, parents, "moonshot index: {} -> {}\n".format(slot, new or "(deleted)"))
            try:
                res = self._push([(commit, self.ref("index"), tip or "")], wrap)
            except AmbiguousPush:
                if not resolve_ambiguity:
                    raise
                self.ambiguity_resolutions += 1
                self._refresh_index()
                refreshed = True
                if self._slots.get(slot) == new:
                    self.contention_retries += retries
                    return CasResult(True, new, retries)
                continue                                     # not applied, or the slot moved: re-checked above
            if res.applied:
                self._tip, self._root = commit, self.repo.read_tree(tree)
                if new:
                    self._slots[slot] = new
                else:
                    self._slots.pop(slot, None)
                self.contention_retries += retries
                return CasResult(True, new, retries)
            retries += 1
            if retries > MAX_CONTENTION:
                self.contention_retries += retries
                raise Contention("index moved {} times".format(retries))
            self._refresh_index()
            refreshed = True

    def _new_unique_ref(self, ref, commit):
        """Create a never-contended ref (staging, quarantine, rejected), resolving a lost acknowledgement."""
        for _ in range(4):
            try:
                res = self._push([(commit, ref, "")])
            except AmbiguousPush:
                self.ambiguity_resolutions += 1
                cur = self._read_refs([ref])[ref]
                if cur == commit:
                    return ref
                if cur is not None:
                    raise GitError("unique ref already exists: " + ref)
                continue
            if not res.applied:
                raise GitError("unique ref already exists: " + ref)
            return ref
        raise AmbiguousPush("unique ref push stayed ambiguous: " + ref)

    # ------------------------------------------------------------------------------------------- objects

    def json_commit(self, name, obj, parent=None, message=None) -> str:
        tree = self.repo.tree({name: self.repo.blob(_jbytes(obj))})
        return self.repo.commit(tree, [parent] if parent else [], message or "moonshot {}\n".format(name))

    def read_json(self, commit, name):
        if not commit:
            return None
        b = self.repo.read_blob("{}:{}".format(commit, name))
        return None if b is None else json.loads(b.decode("utf-8"))

    def genesis_commit(self, genesis) -> str:
        tree = self.repo.tree({"GENESIS.json": self.repo.blob(genesis.bytes),
                               "CHECKPOINT": self.repo.blob(genesis.initial_checkpoint)})
        return self.repo.commit(tree, [], "moonshot genesis {}\n".format(genesis.chain_id))

    def epoch_commit(self, result, parent, attempt_id) -> str:
        """The tree is canonical bytes only; the message names the attempt (CONTRACT v1.1)."""
        f = result.files()
        tree = self.repo.tree({"MANIFEST.json": self.repo.blob(f["manifest"]), "SPEC.json": self.repo.blob(f["spec"]),
                               "TRACE": self.repo.blob(f["trace"]), "CHECKPOINT": self.repo.blob(f["checkpoint"])})
        msg = "moonshot epoch {} #{}\n\nwork {}\nepoch {}\nattempt {}\n".format(
            result.chain_id, result.epoch_index, result.work_id, result.epoch_digest, attempt_id)
        return self.repo.commit(tree, [parent], msg)

    def _info(self, commit):
        """(epoch_index by lineage position, parent, root) -- structural, never trusted from a manifest."""
        if commit not in self._memo:
            stack, c = [], commit
            while c not in self._memo:
                parents = self.repo.read_commit(c)["parents"]
                stack.append((c, parents[0] if parents else None))
                if not parents:
                    break
                c = parents[0]
            for c, parent in reversed(stack):
                if parent is None:
                    self._memo[c] = (0, None, c)
                else:
                    pidx, _, root = self._memo[parent]
                    self._memo[c] = (pidx + 1, parent, root)
        return self._memo[commit]

    def manifest(self, commit):
        if commit not in self._manifests:
            b = self.repo.read_blob("{}:MANIFEST.json".format(commit))
            try:
                self._manifests[commit] = None if b is None else C.parse_canonical(b)
            except C.CanonicalError:
                self._manifests[commit] = {}
        return self._manifests[commit]

    def genesis_of(self, commit) -> dict:
        root = self._info(commit)[2]
        if root not in self._geneses:
            self._geneses[root] = C.parse_canonical(self.repo.read_blob("{}:GENESIS.json".format(root)))
        return self._geneses[root]

    def epoch_bytes(self, commit) -> dict:
        get = lambda n: self.repo.read_blob("{}:{}".format(commit, n))  # noqa: E731
        return {"manifest": get("MANIFEST.json"), "spec": get("SPEC.json"), "trace": get("TRACE"),
                "checkpoint": get("CHECKPOINT")}

    def checkpoint(self, commit) -> bytes:
        return self.repo.read_blob("{}:CHECKPOINT".format(commit))

    def published(self, commit) -> PublishedEpoch:
        m = self.manifest(commit) or {}
        return PublishedEpoch(self._info(commit)[0], commit, m, m.get("work_id", ""), m.get("epoch_digest", ""))

    def commit_at(self, head, k):
        """The commit at lineage position k (0 = genesis) below `head`, or None."""
        idx, c = self._info(head)[0], head
        if k > idx or k < 0:
            return None
        for _ in range(idx - k):
            c = self._info(c)[1]
        return c

    # ------------------------------------------------------------------------------------------- chains

    def create_chain(self, genesis) -> str:
        self._require(COORDINATOR)
        c = self.genesis_commit(genesis)
        if not self.cas_slot("chains/" + genesis.chain_id, None, c).applied:
            raise ValueError("chain {} already exists".format(genesis.chain_id))
        return c

    def _view(self, chain_id, vals) -> ChainView:
        head = vals["chains/" + chain_id]
        if not head:
            raise KeyError("no chain " + chain_id)
        contest = self.read_json(vals.get("contest/" + chain_id), "CONTEST.json")
        return ChainView(chain_id, head, self._info(head)[0], self.genesis_of(head), contest)

    def chain_view(self, chain_id) -> ChainView:
        return self._view(chain_id, self.read_slots(["chains/" + chain_id, "contest/" + chain_id]))

    def snapshot(self, chain_id):
        """(ChainView, lease_commit, lease) from one read: what a worker needs to decide an attempt."""
        vals = self.read_slots(["chains/" + chain_id, "contest/" + chain_id, "leases/" + chain_id])
        lc = vals["leases/" + chain_id]
        return self._view(chain_id, vals), lc, self.read_json(lc, "LEASE.json")

    def lineage(self, chain_id) -> list:
        head = self.chain_view(chain_id).head_commit
        out, c = [], head
        while self._info(c)[0] > 0:
            out.append(self.published(c))
            c = self._info(c)[1]
        return out[::-1]

    def stage(self, attempt_id, commit) -> str:
        self._require(WORKER)
        return self._new_unique_ref(self.ref("staging", attempt_id), commit)

    def unstage(self, attempt_id, commit):
        try:
            self._push([(None, self.ref("staging", attempt_id), commit)])
        except GitError:
            pass                                             # a leftover staging ref is garbage, not meaning

    def cas_chain(self, chain_id, expected, new, wrap=None) -> CasResult:
        self._require(WORKER)
        return self.cas_slot("chains/" + chain_id, expected, new, wrap, resolve_ambiguity=False)

    def quarantine(self, chain_id, epoch_index, attempt_id, commit) -> str:
        self._require(WORKER, VALIDATOR)
        return self._new_unique_ref(self.ref("quarantine", chain_id, str(epoch_index), attempt_id), commit)

    def rewind(self, chain_id, expected_head, to_commit, epoch_index) -> CasResult:
        """Resolver only: archive the rejected branch, then move the head back by CAS (CONTRACT s7)."""
        self._require(RESOLVER)
        name, n = self.ref("rejected", chain_id, str(epoch_index)), 0
        while True:
            try:
                self._new_unique_ref(name if n == 0 else "{}-{}".format(name, n), expected_head)
                break
            except GitError:
                n += 1
                if n > 20:
                    raise
        return self.cas_slot("chains/" + chain_id, expected_head, to_commit)

    # ------------------------------------------------------------------------------------------- nodes (D5)

    def announce_node(self, node_id, record) -> str:
        """Liveness only (CONTRACT s3 nodes/<node>): it grants nothing and touches no slot."""
        self._require(WORKER)
        if not NAME_RE.match(node_id or ""):
            raise ValueError("node_id must match " + NAME_RE.pattern)
        ref = self.ref("nodes", node_id)
        for _ in range(4):
            cur = self._read_refs([ref])[ref]
            c = self.json_commit("NODE.json", dict(record, node_id=node_id), cur, "moonshot node {}\n".format(node_id))
            try:
                if self._push([(c, ref, cur or "")]).applied:
                    return ref
            except AmbiguousPush:
                self.ambiguity_resolutions += 1
                if self._read_refs([ref])[ref] == c:
                    return ref
        raise GitError("could not announce node " + node_id)

    def nodes(self) -> dict:
        vals = self._read_refs(None, glob=self.ref("nodes/*"))
        base = len(self.ref("nodes/"))
        return {r[base:]: self.read_json(v, "NODE.json") for r, v in vals.items() if v}

    # ------------------------------------------------------------------------------------------- records

    def contest(self, chain_id):
        return self.read_json(self.read_slots(["contest/" + chain_id])["contest/" + chain_id], "CONTEST.json")

    def open_contest(self, chain_id, record) -> bool:
        """Detectors (workers, validators) may OPEN a contest; only a resolver closes one. An already open
        contest is left as it is: the chain already fails closed."""
        self._require(WORKER, VALIDATOR)
        for _ in range(8):
            cur = self.read_slots(["contest/" + chain_id])["contest/" + chain_id]
            old = self.read_json(cur, "CONTEST.json")
            if old and old.get("state") in OPEN_CONTEST_STATES:
                return False
            c = self.json_commit("CONTEST.json", record, cur, "moonshot contest {} {}\n".format(chain_id, record["state"]))
            if self.cas_slot("contest/" + chain_id, cur, c).applied:
                return True
        raise GitError("could not open contest on " + chain_id)

    def close_contest(self, chain_id, record) -> bool:
        self._require(RESOLVER)
        cur = self.read_slots(["contest/" + chain_id])["contest/" + chain_id]
        c = self.json_commit("CONTEST.json", record, cur, "moonshot contest {} {}\n".format(chain_id, record["state"]))
        return self.cas_slot("contest/" + chain_id, cur, c).applied

    def validation(self, chain_id):
        return self.read_json(self.read_slots(["validation/" + chain_id])["validation/" + chain_id],
                              "VALIDATION.json")

    def write_validation(self, chain_id, record) -> bool:
        self._require(VALIDATOR)
        for _ in range(8):
            cur = self.read_slots(["validation/" + chain_id])["validation/" + chain_id]
            c = self.json_commit("VALIDATION.json", record, cur, "moonshot validation {}\n".format(chain_id))
            if self.cas_slot("validation/" + chain_id, cur, c).applied:
                return True
        raise GitError("could not write validation for " + chain_id)

    def write_lease(self, chain_id, expected, lease) -> Optional[str]:
        """CAS the lease slot; the new lease commit, or None if someone else moved it first."""
        self._require(WORKER)
        c = self.json_commit("LEASE.json", lease, expected, "moonshot lease {} #{} {} {}\n".format(
            chain_id, lease["epoch_index"], lease["state"], lease["attempt_id"]))
        return c if self.cas_slot("leases/" + chain_id, expected, c).applied else None

    def append_receipts(self, worker_id, receipts: dict) -> str:
        """receipts: attempt_id -> receipt dict. One commit per batch, chained by parent (single writer)."""
        self._require(WORKER)
        slot = "receipts/" + worker_id
        for _ in range(8):
            cur = self.read_slots([slot])[slot]
            tree = self.repo.tree({aid + ".json": self.repo.blob(_jbytes(r)) for aid, r in receipts.items()})
            c = self.repo.commit(tree, [cur] if cur else [], "moonshot receipts {} ({})\n".format(worker_id, len(receipts)))
            if self.cas_slot(slot, cur, c).applied:
                return c
        raise GitError("could not append receipts for " + worker_id)

    def read_receipts(self) -> list:
        seen = {}
        for _, head in sorted(self.list_slots("receipts/").items()):
            c = head
            while c:
                meta = self.repo.read_commit(c)
                for name, b in self.repo.read_tree(meta["tree"]).items():
                    if name.endswith(".json") and not isinstance(b, tuple):
                        r = json.loads(self.repo.read_blob(b).decode("utf-8"))
                        seen.setdefault(r["attempt_id"], r)
                c = meta["parents"][0] if meta["parents"] else None
        return list(seen.values())
