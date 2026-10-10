# Fabric / Moonshot / Pan interface contract -- v0.1 (C-012-T001, OP-NF2)

Owner: Themis (Moonshot). Reviewers: Odysseus (Fabric), Pan (Pan). Date: 2026-10-10.
Authority: operator OP-NF2 (roles/Themis/prompts/2026-10-10_op_nf2/). Status: DRAFT FOR REVIEW -- review
requests sent (comms #1986 Pan, #1987 Odysseus); Odysseus has been offline since 2026-10-03.
Design of record for Moonshot semantics: moonshot/epoch/CONTRACT.md v1.1 (C-008), whose IDENTITY rules carry
over unchanged and whose git TRANSPORT is replaced here.

## 1. Responsibilities (OP-NF2 s2; not to be conflated)

| Owner | Owns | Moonshot's use |
|---|---|---|
| FABRIC (Odysseus; schema `fabric`; code `fabric/`, FROZEN v0.2) | submission, claims, worker identity and capabilities, resource leases, heartbeats, attempt state, generic retry/recovery | CLIENT ONLY: submit tasks, read tasks/attempts/artifacts/blobs. No code or schema change. |
| MOONSHOT (Themis; schema `moonshot`; code `moonshot/`) | canonical epoch identity, checkpoint lineage, atomic epoch publication, duplicate/disagreement classification, replay/validation state, contest/taint resolution | everything in s3-s5 |
| PAN (Pan; schemas `pan`, `pan_iceberg`; code `pan/`; the lake on M2) | dataset catalogs, Parquet, Iceberg history, searchable evidence metadata | CLIENT ONLY, after Pan agrees: s6 |

Moonshot keeps NO lease table and NO task queue: Fabric's one-live-attempt-per-task invariant is the exclusivity
an epoch needs, and Fabric's lease row is the only resource lease (OP-NF2 s3).

## 2. Identity (unchanged from C-008)

`work_id = H("moonshot.epoch.work.v1", {input_checkpoint_sha256, spec_sha256, runtime})`,
`epoch_digest = H("moonshot.epoch.result.v1", {work_id, trace_sha256, output_checkpoint_sha256})`,
`H(tag, obj) = sha256(tag || 0x00 || canonical_json(obj))`. The canonical files are MANIFEST.json, SPEC.json,
TRACE, CHECKPOINT; the manifest carries no attempt metadata. Fabric task/attempt ids, hosts, SHAs of transport
rows and database ids are locators and accounting, never identity. The C-008 known-answer vectors still hold.

## 3. The execution path

```
 dispatcher (Moonshot, trusted)      Fabric (as-is)                         publisher (Moonshot, trusted)
 reads chain head (index,           tasks/attempts/leases/artifacts         reads succeeded attempts + artifacts,
 generation) -> fabric.submit -----> claim (SKIP LOCKED) -> worker -------> verifies bytes + approval, then ONE
 script task, idempotency key       runs python -E -s -m                   transaction: moonshot.publish(...)
 (chain, k, generation)             moonshot.epoch.fabric_exec at the       -> PUBLISHED | DUPLICATE |
                                    task's base_sha, NO db/network env;     DISAGREEMENT(contest) | STALE |
                                    runtime uploads out/ as artifacts       INVALID | REFUSED_UNAPPROVED | HALTED
                                                                                      |
                                    validator (Moonshot, independent identity) replays -> moonshot.record_validation
                                    resolver (Moonshot) replays a contest -> moonshot.resolve_contest (may rewind)
                                    materializer (Moonshot, on M2) -> Pan's lake (derived; never gates publication)
```

Calls Moonshot makes into Fabric (Python API of fabric.store, read-only except submit):
- `submit(principal="Themis", executor="script", base_sha=<approved>, params={"module": "moonshot.epoch.fabric_exec",
  "args": [...], "wall_s": N}, required_caps=["fabric.runtime==0.2", "moonshot.epoch.v1"],
  idempotency_key="moonshot/<namespace>/<chain>/<k>/g<generation>[-r<i>]", metadata={"moonshot": {...}},
  campaign_id="C-012", host_affinity=<optional, for the two-node race>)`.
- `get_task`, attempts and `artifact_content` reads (read-only). Nothing else; no lease, reap or finish calls.
- Node workers (s7) are Fabric workers run exactly per fabric/FREEZE.md "Node runtime", named
  `worker.<host>.moonshot`, caps `moonshot.epoch.v1`, executors `script` only.

The executor receives only its args and FABRIC_OUT_DIR (Fabric's script executor gives it no database or network
configuration). For synthetic epochs the 4 KB input checkpoint travels inline as a base64 argument with its sha256,
and the executor refuses a mismatch. Native epochs with large checkpoints need an object-fetch path: DESIGN ITEM,
not built (Fabric artifacts are capped at 16 MB each).

## 4. The Moonshot schema (versioned; `moonshot/nf/schema.sql`, meta.schema_version = 1)

Tables, with the invariants the DATABASE enforces:
- `objects(sha256 PK, content)`: immutable content-addressed bytes; CHECK sha256 = encode(sha256(content),'hex').
- `chains(chain_id PK, genesis, approved_code_sha, epochs_target, head_index, head_epoch_digest,
  head_checkpoint_sha256, generation, state OPEN|HALTED|COMPLETE)`: generation +1 on EVERY head move (advance or
  rewind), so an expected (parent, generation) pair cannot be satisfied twice (no ABA).
- `results(work_id, epoch_digest) PK`: every DISTINCT result ever seen for a work identity -- disagreements are
  preserved, never overwritten.
- `publications`: the lineage, one row per head advance; partial UNIQUE (chain_id, epoch_index) WHERE not rejected
  = exactly one live published successor per position; rejected rows stay as evidence.
- `attempts(attempt_id PK = the Fabric attempt id)`: one classification per attempt, the idempotency key of
  publication, durable accounting (host, worker, base_sha, timings, costs) OUTSIDE the canonical trace.
- `contests`: partial UNIQUE open contest per chain; `validations`: separate from publication; `events`: append-only.

Functions (PL/pgSQL, SECURITY DEFINER, owned by a NOLOGIN owner role, fixed search_path):
- `publish(...)`: locks the chain row; returns the recorded outcome if the attempt was already classified (the
  lost-acknowledgement path); stores objects and checks the manifest's sha256 fields against the bytes; records the
  result; ADVANCES only if `generation = expected_generation AND head_epoch_digest = expected_parent AND
  head_index = k-1 AND head_checkpoint_sha256 = input sha AND state = OPEN`; otherwise classifies against the live
  publication at k: same work_id + same digest -> DUPLICATE; same work_id + different digest -> DISAGREEMENT, a
  contest (CONTESTED at the head, TAINTED with descendants) and the chain HALTED; anything else -> STALE.
- `record_attempt_outcome(...)`: INVALID / REFUSED_UNAPPROVED attempts (bytes that fail the publisher's checks;
  code that is not approved), recorded without publishing.
- `record_validation(...)`: VALIDATED | INVALID | MISMATCH; MISMATCH opens a contest and halts the chain.
- `resolve_contest(...)`: the verdict is computed IN SQL from the resolver's replay digests -- all equal the
  published digest -> UPHELD; all equal the challenger -> OVERTURNED (publications at k.. marked rejected, head
  rewound to k-1, generation +1); otherwise UNRESOLVED (still halted).
- `create_chain(...)`, `put_object(...)`.

Semantic verification (recomputing work_id and epoch_digest from canonical bytes) runs in the PUBLISHER with
moonshot.epoch.model.verify_epoch before `publish`; the database independently checks every byte hash and the
lineage. A validator replays later on an independent host.

## 5. Authority, authentication, isolation (OP-NF2 s7) -- explicit, including what is NOT achieved

Roles (NOLOGIN, `moonshot_*`): owner (owns everything), reader (SELECT), coordinator (create_chain), publisher
(publish, record_attempt_outcome), validator (record_validation), resolver (resolve_contest). PUBLIC has nothing:
no table privilege, no EXECUTE. Moonshot code does `SET ROLE` to the narrowest role for each act.

Achieved: fleet workers never receive Moonshot code paths that write the schema; the executed epoch code has no
database or network configuration; publication authority sits in one trusted publisher; validation and resolution
are separate identities; every guard is in the database, not in a client.

NOT achieved, stated plainly: every program client -- including Fabric node workers -- logs in as the `postgres`
SUPERUSER through the git-tracked evidence_wiki/config.json default (verified 2026-10-10: rolsuper, bypassrls). A
superuser bypasses every grant, so the role separation above is BUG CONTAINMENT, not a security boundary, until the
operator/DBA issues per-role logins (proposed: LOGIN roles granted moonshot_publisher / moonshot_validator only on
M2; Fabric workers a fabric-only role -- Odysseus's call, BACKLOG_AFTER_FREEZE). Isolation of executed code is
Fabric's script executor only (no shell, env allow-list, pinned SHA) running as the node user; promexec stays
EXPERIMENTAL and unused. Trust in executed code therefore rests on CODE APPROVAL: the publisher refuses any attempt
whose Fabric base_sha is not the chain's approved_code_sha or not an ancestor of origin/main, or whose module is
not moonshot.epoch.fabric_exec (REFUSED_UNAPPROVED). Fabric does not authenticate task submitters, so a hostile
submitter could make a node RUN unapproved code; Moonshot cannot prevent that execution, only refuse its results.

## 6. Pan's lake (OP-NF2 s4) -- proposal pending Pan's answer (#1986)

- Authoritative: Postgres `moonshot` (metadata + content-addressed objects). The lake is DERIVED (Pan's P1).
- A materializer runs ON M2 (the lake is M2-local, Pan's Q-003 default; Ubuntu nodes never read it) and appends,
  through Pan's public `pan.iceberg.write`, to namespace `moonshot`: epochs, attempts, validations, contests and
  trace_lines (the event/measurement table, one row per canonical trace line).
- Idempotent and recoverable: each append records a watermark (the last publication id) in the Iceberg snapshot
  summary; on restart the materializer resumes from the latest snapshot's watermark, so a crash between the Iceberg
  commit and anything else neither loses nor duplicates rows. Oracle: per-table row counts vs Postgres.
- Publication never waits on the lake; a lake outage only delays materialization.

## 7. Node runtime for the demonstration (s3)

ubu001: `~/fabric-runtime` is at 9c022347e (fabric-v0.2 + the DEF-ODY-019 repair). ubu002: its `~/fabric-runtime` is
pre-freeze, so a separate detached worktree at the same commit is used; nothing of Fabric's on either node is
modified. Workers: `EW_DB_HOST=192.168.1.202 python3 -m fabric worker --agent worker.<host>.moonshot --caps
moonshot.epoch.v1 --executors script`. Fault injection for the conflicting-result race is node-local (a file
under /var/tmp naming a TEST namespace) so no task submitter can trigger it; production namespaces ignore it.

## 8. Review record

| Reviewer | Requested | Outcome |
|---|---|---|
| Pan | comms #1986, 2026-10-10 | pending |
| Odysseus | comms #1987, 2026-10-10 | pending (offline since 2026-10-03) |
