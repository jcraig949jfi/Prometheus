"""The Moonshot coordinator over Fabric (C-012-T003; contract moonshot/nf/INTERFACE_CONTRACT.md s3).

Four trusted roles, each acting through its own database role (moonshot.nf.pg):
- dispatcher  reads the chain head and submits ONE Fabric script task per replica (fabric.store.submit): the approved
              executor at the chain's approved_code_sha, the epoch's inputs in its args, the expectations
              (parent digest, generation) in its metadata. Idempotent per (schema, namespace, chain, epoch,
              generation, replica). Fabric owns claims, leases, heartbeats, attempts and retries; Moonshot keeps
              no lease or queue of its own.
- publisher   for every SUCCEEDED Fabric attempt not yet classified: reads the four canonical files from Fabric's
              artifacts, checks provenance (executor, module, base_sha, worktree head, namespace, position) and
              calls moonshot.publish, which classifies it. Failed attempts are Fabric's business (it retries).
              Execution accounting (task, attempt, host, SHAs, times, bytes) goes into the attempt's detail,
              never into the canonical files.
- validator   replays each published epoch on THIS host from its lineage input and records VALIDATED,
              MISMATCH or INVALID about the digest it examined.
- resolver    replays a contested epoch and lets the database compute the verdict.

`receipt` writes a canonical, content-addressed receipt of a chain into the schema (record_receipt).
No git: nothing here fetches, pushes or reads a remote."""
import base64
import datetime
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from moonshot.epoch import canonical as C
from moonshot.epoch import model
from moonshot.nf import pg

MODULE = "moonshot.epoch.fabric_exec"
CAPS = ["fabric.runtime==0.2", "moonshot.epoch.v1"]
FILES = {"manifest": "MANIFEST.json", "spec": "SPEC.json", "trace": "TRACE", "checkpoint": "CHECKPOINT"}
RECEIPT_SCHEMA = "moonshot.nf.receipt.v1"


class CoordinatorError(Exception):
    pass


def _iso(v):
    return v.isoformat() if isinstance(v, (datetime.datetime, datetime.date)) else v


def _arg(args, flag):
    try:
        return args[args.index(flag) + 1]
    except (ValueError, IndexError, AttributeError):
        return None


class Coordinator:
    def __init__(self, schema="moonshot", *, principal="Themis", campaign="C-012", actor="Themis", fabric_conn=None):
        from fabric import store as S
        self.S, self.schema, self.principal, self.campaign, self.actor = S, schema, principal, campaign, actor
        self._own_fab = fabric_conn is None
        self.fab = fabric_conn or S.connect()
        self.host = socket.gethostname().lower()
        self._handles = {}
        self.reader = self._h("reader")

    def _h(self, role):
        if role not in self._handles:
            self._handles[role] = pg.Moonshot(pg.connect(), self.schema, role=role, actor=self.actor)
        return self._handles[role]

    def close(self):
        for h in self._handles.values():
            h.close()
        self._handles.clear()
        if self._own_fab:
            self.fab.close()

    # ------------------------------------------------------------------------------------------- chains
    def create_chain(self, genesis, *, namespace):
        return self._h("coordinator").create_chain(genesis, namespace=namespace,
                                                   approved_code_sha=genesis.obj["approved_code_sha"])

    # ------------------------------------------------------------------------------------------- dispatch
    def dispatch(self, chain_id, *, replicas=1, hosts=None, base_sha=None, wall_s=300, max_attempts=3, tag=""):
        """Submit the next epoch of an OPEN chain as `replicas` Fabric tasks (optionally pinned to `hosts`).
        `base_sha` overrides the approved SHA -- only to demonstrate that the publisher refuses it."""
        h = self.reader.head(chain_id)
        if h["state"] != "OPEN":
            raise CoordinatorError("chain {} is {}, not OPEN".format(chain_id, h["state"]))
        if hosts is not None and len(hosts) != replicas:
            raise CoordinatorError("one host per replica")
        k, gen, ns = h["head_index"] + 1, h["generation"], h["namespace"]
        gbytes = C.canonical_bytes(self.reader.genesis(chain_id))
        inp = self.reader.checkpoint_at(chain_id, h["head_index"])
        if C.sha256_hex(inp) != h["head_checkpoint_sha256"]:
            raise CoordinatorError("stored head checkpoint does not match its address")
        args = ["--namespace", ns, "--genesis-b64", base64.b64encode(gbytes).decode("ascii"), "--epoch-index", str(k),
                "--input-b64", base64.b64encode(inp).decode("ascii"), "--input-sha256", h["head_checkpoint_sha256"]]
        meta = {"moonshot": {"schema": self.schema, "chain_id": chain_id, "namespace": ns, "epoch_index": k,
                             "expected_parent": h["head_epoch_digest"], "expected_generation": gen}}
        sha = base_sha or h["approved_code_sha"]
        out = []
        for i in range(replicas):
            key = "moonshot/{}/{}/{}/{}/g{}".format(self.schema, ns, chain_id, k, gen)
            key += ("-r{}".format(i) if replicas > 1 else "") + ("-sha{}".format(sha[:12]) if base_sha else "") + tag
            t = self.S.submit(self.fab, self.principal, "Moonshot epoch {} #{} (generation {})".format(chain_id, k, gen),
                              "script", title="moonshot {}/{}#{} g{}".format(ns, chain_id, k, gen),
                              required_caps=CAPS, campaign_id=self.campaign, base_sha=sha,
                              params={"module": MODULE, "args": args, "wall_s": wall_s}, idempotency_key=key,
                              host_affinity=hosts[i] if hosts else None, metadata=meta, max_attempts=max_attempts)
            out.append(dict(t, idempotency_key=key, epoch_index=k, generation=gen))
        return out

    # ------------------------------------------------------------------------------------------- publish
    def _candidates(self, only_attempts=None):
        """(task, attempt) pairs: a succeeded Fabric attempt of a Moonshot task of THIS schema, not yet classified."""
        done = self.reader.classified_attempt_ids()
        # A completed Fabric task has exactly one succeeded attempt, so a task Moonshot has classified is finished
        # for good. (Fabric clears tasks.current_attempt when an attempt ends: it cannot serve as the skip key.)
        done_tasks = self.reader.classified_task_ids()
        found = []
        for row in self.S.list_tasks(self.fab, principal=self.principal, state="completed", limit=100000):
            if row["task_id"] in done_tasks:
                continue
            t = self.S.get_task(self.fab, row["task_id"])
            m = (t.get("metadata") or {}).get("moonshot") or {}
            if m.get("schema") != self.schema:
                continue
            for a in t["attempts"]:
                if a["status"] == "succeeded" and a["attempt_id"] not in done and                         (only_attempts is None or a["attempt_id"] in only_attempts):
                    found.append((t, a))
        found.sort(key=lambda ta: (ta[0]["metadata"]["moonshot"]["chain_id"], ta[0]["metadata"]["moonshot"]["epoch_index"],
                                   str(ta[1].get("ended_at"))))
        return found

    def _refusals(self, t, a, chain):
        """Provenance checks, keyed by check; {} = approved. The bytes are checked separately (publisher + database)."""
        m, params = t["metadata"]["moonshot"], t.get("params") or {}
        args, receipt = params.get("args") or [], a.get("env_receipt") or {}
        why = {}
        if t.get("executor") != "script":
            why["executor"] = "executor {!r} is not script".format(t.get("executor"))
        if params.get("module") != MODULE or params.get("script"):
            why["module"] = "module {!r} is not {}".format(params.get("module") or params.get("script"), MODULE)
        if t.get("base_sha") != chain["approved_code_sha"]:
            why["base_sha"] = "task base_sha {} is not the chain's approved_code_sha".format(t.get("base_sha"))
        if a.get("base_sha") != t.get("base_sha"):
            why["attempt_base_sha"] = "attempt base_sha {} is not the task's".format(a.get("base_sha"))
        if receipt.get("worktree_head") != chain["approved_code_sha"]:
            why["worktree_head"] = "worktree_head {} is not the approved_code_sha".format(receipt.get("worktree_head"))
        if _arg(args, "--namespace") != chain["namespace"] or m.get("namespace") != chain["namespace"]:
            why["namespace"] = "namespace {!r} is not the chain's {!r}".format(_arg(args, "--namespace"),
                                                                             chain["namespace"])
        if _arg(args, "--epoch-index") != str(m.get("epoch_index")):
            why["epoch_index"] = "epoch_index in args and metadata differ"
        return why

    def _prepare(self, t, a):
        m = t["metadata"]["moonshot"]
        chain = self.reader.head(m["chain_id"])
        arts = {x["name"]: x for x in t["artifacts"] if x["attempt_id"] == a["attempt_id"]}
        files, size = {}, 0
        for key, name in FILES.items():
            if name in arts:
                files[key] = self.S.artifact_content(self.fab, arts[name]["artifact_id"])["content"]
                size += len(files[key])
        receipt = a.get("env_receipt") or {}
        acct = {"task_id": t["task_id"], "attempt_id": a["attempt_id"], "seq": a.get("seq"), "agent": a.get("agent"),
                "instance": a.get("instance"), "host": a.get("host"), "base_sha": t.get("base_sha"),
                "worktree_head": receipt.get("worktree_head"), "started_at": _iso(a.get("started_at")),
                "ended_at": _iso(a.get("ended_at")), "exit_code": a.get("exit_code"), "artifact_bytes": size,
                "idempotency_key": t.get("idempotency_key")}
        return {"task": t, "attempt": a, "meta": m, "chain": chain, "files": files, "acct": acct,
                "refused": self._refusals(t, a, chain)}

    def _publish_one(self, p, handle, hooks=None):
        m, acct = p["meta"], p["acct"]
        args = (acct["attempt_id"], acct["task_id"], m["chain_id"], m["epoch_index"], m["expected_parent"],
                m["expected_generation"])
        if set(p["files"]) != set(FILES):
            res = handle.record_attempt_outcome(*args, "INVALID", detail={
                "fabric": acct, "errors": ["missing artifacts: {}".format(sorted(set(FILES) - set(p["files"])))]})
        else:
            res = handle.publish(*args, p["files"], detail={"fabric": acct, "refused": p["refused"]},
                                 approved=not p["refused"], **(hooks or {}))
        return dict(res, task_id=acct["task_id"], attempt_id=acct["attempt_id"], chain_id=m["chain_id"],
                    epoch_index=m["epoch_index"], host=acct["host"])

    def publish_ready(self, *, parallel=1, only_attempts=None, _hold_before_commit_s=0.0, _lose_acks=0):
        """Classify every succeeded, unclassified attempt (or only `only_attempts`). With parallel > 1 the
        publications start together on separate connections, so racing results meet in the database, not in this
        process. The underscored hooks pass to Moonshot.publish (crash and lost-acknowledgement demonstrations)."""
        hooks = {k: v for k, v in (("_hold_before_commit_s", _hold_before_commit_s), ("_lose_acks", _lose_acks)) if v}
        prepared = [self._prepare(t, a) for t, a in self._candidates(only_attempts)]
        if not prepared:
            return []
        if parallel <= 1 or len(prepared) == 1:
            return [self._publish_one(p, self._h("publisher"), hooks) for p in prepared]
        barrier = threading.Barrier(min(parallel, len(prepared)))

        def go(p):
            h = pg.Moonshot(pg.connect(), self.schema, role="publisher", actor=self.actor)
            try:
                try:
                    barrier.wait(timeout=60)
                except threading.BrokenBarrierError:
                    pass
                return self._publish_one(p, h, hooks)
            finally:
                h.close()

        with ThreadPoolExecutor(max_workers=min(parallel, len(prepared))) as ex:
            return list(ex.map(go, prepared))

    # ------------------------------------------------------------------------------------------- validate / resolve
    def validate(self, chain_id, *, epochs=None):
        """Replay published epochs on this host. Default: every live epoch still UNVALIDATED."""
        g = self.reader.genesis(chain_id)
        out = []
        for p in self.reader.lineage(chain_id):
            k = p["epoch_index"]
            if epochs is not None and k not in epochs:
                continue
            if epochs is None and self.reader.validation_state(chain_id, k) != "UNVALIDATED":
                continue
            files = self.reader.epoch_files(chain_id, k)
            inp = self.reader.checkpoint_at(chain_id, k - 1)
            errs = model.verify_epoch(files, C.sha256_hex(inp))
            replay = model.execute(g, k, inp)
            state = "INVALID" if errs else ("VALIDATED" if replay.epoch_digest == p["epoch_digest"] else "MISMATCH")
            self._h("validator").record_validation(chain_id, k, p["epoch_digest"], state, ["BYTES", "REPLAY"],
                                                   replay.epoch_digest, self.host)
            out.append((k, state))
        return out

    def resolve(self, chain_id, *, replays=2, extra_digests=()):
        """Resolve the chain's open contest by deterministic replay on this host (plus any replays run elsewhere)."""
        c = self.reader.open_contest(chain_id)
        if c is None:
            raise CoordinatorError("chain {} has no open contest".format(chain_id))
        k = c["epoch_index"]
        g = self.reader.genesis(chain_id)
        inp = self.reader.checkpoint_at(chain_id, k - 1)
        digests = [model.execute(g, k, inp).epoch_digest for _ in range(replays)] + list(extra_digests)
        files = self.reader.epoch_files(chain_id, k)
        bytes_ok = files is not None and model.verify_epoch(files, C.sha256_hex(inp)) == []
        return self._h("resolver").resolve_contest(c["contest_id"], digests, bytes_ok)

    # ------------------------------------------------------------------------------------------- receipts
    def receipt(self, chain_id):
        """A canonical receipt of the chain as it stands, stored content-addressed in the schema."""
        r = self.reader
        head = r.head(chain_id)
        lineage = []
        for p in r.lineage(chain_id):
            a = r.attempt(p["attempt_id"]) or {}
            acct = (a.get("detail") or {}).get("fabric") or {}
            lineage.append({"epoch_index": p["epoch_index"], "epoch_digest": p["epoch_digest"], "work_id": p["work_id"],
                            "generation": p["generation"], "publication_id": p["publication_id"],
                            "attempt_id": p["attempt_id"], "fabric_task_id": acct.get("task_id"),
                            "fabric_attempt_id": acct.get("attempt_id"), "host": acct.get("host"),
                            "validation": r.validation_state(chain_id, p["epoch_index"])})
        body = {"schema": RECEIPT_SCHEMA, "moonshot_schema": self.schema, "chain_id": chain_id,
                "genesis_sha256": C.sha256_hex(C.canonical_bytes(r.genesis(chain_id))),
                "head": {k: head[k] for k in ("head_index", "head_epoch_digest", "head_checkpoint_sha256", "generation",
                                              "state", "epochs_target", "approved_code_sha", "namespace")},
                "lineage": lineage,
                "rejected": [{"epoch_index": k, "epoch_digest": d} for k, d in r.rejected_epochs(chain_id)],
                "contests": r.contests(chain_id), "attempt_outcomes": r.attempt_outcomes(chain_id),
                "issued_by": self.actor, "issued_on": self.host,
                "issued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        sha = self._h("coordinator").record_receipt(chain_id, C.canonical_bytes(body))
        return {"sha256": sha, "receipt": body}


def main(argv=None):
    """`python -m moonshot.nf.coordinator publish --schema S [--only-attempt A] [--hold-before-commit-s N]`: one
    publisher pass in its own process (the two-node demonstration kills it mid-transaction). Prints JSON lines."""
    import argparse
    import json
    import sys
    ap = argparse.ArgumentParser(prog="moonshot.nf.coordinator")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("publish")
    p.add_argument("--schema", required=True)
    p.add_argument("--principal", default="Themis")
    p.add_argument("--campaign", default="C-012")
    p.add_argument("--actor", default="Themis")
    p.add_argument("--only-attempt", action="append")
    p.add_argument("--hold-before-commit-s", type=float, default=0.0)
    p.add_argument("--parallel", type=int, default=1)
    a = ap.parse_args(argv)
    co = Coordinator(a.schema, principal=a.principal, campaign=a.campaign, actor=a.actor)
    try:
        for r in co.publish_ready(parallel=a.parallel, only_attempts=set(a.only_attempt) if a.only_attempt else None,
                                  _hold_before_commit_s=a.hold_before_commit_s):
            print(json.dumps(r, default=str, sort_keys=True), flush=True)
    finally:
        co.close()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
