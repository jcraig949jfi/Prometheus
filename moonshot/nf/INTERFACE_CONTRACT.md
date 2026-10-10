# Fabric / Moonshot / Pan interface contract -- v0.2 (C-012-T001, OP-NF2)

Owner: Themis (Moonshot). Reviewers: Odysseus (Fabric), Pan (Pan). Date: 2026-10-10.
Authority: operator OP-NF2 (roles/Themis/prompts/2026-10-10_op_nf2/). Status: DRAFT FOR REVIEW -- review
requests sent (comms #1986 Pan, #1987 Odysseus); Odysseus has been offline since 2026-10-03.
v0.2 (same day, after T002's mutation table and review of the GREEN tree): s4 records the schema as built --
validations name the digest they examined, an adverse validation behind an open contest stays pending instead of
being dropped, guards on chains and contests, TRUNCATE refused on every evidence table, connection-loss semantics.
Nothing in s1-s3 or s6-s7 changed. The interfaces Pan and Odysseus were asked to review (s3, s6) are as in v0.1.
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
  rewind), so an expected (parent, generation) pair cannot be satisfied twice (no ABA). A trigger enforces it: the
  identity columns never change, the generation never decreases, a head move that does not raise it is refused.
- `results(work_id, epoch_digest) PK`: every DISTINCT result ever seen for a work identity -- disagreements are
  preserved, never overwritten.
- `publications`: the lineage, one row per head advance; partial UNIQUE (chain_id, epoch_index) WHERE not rejected
  = exactly one live published successor per position; rejected rows stay as evidence (content immutable, a
  rejection is set once).
- `attempts(attempt_id PK = the Fabric attempt id)`: one classification per attempt, the idempotency key of
  publication, durable accounting (host, worker, base_sha, timings, costs) OUTSIDE the canonical trace.
- `contests`: partial UNIQUE open (CONTESTED | TAINTED | UNRESOLVED) contest per chain; the grounds never change,
  only the resolution moves, and UPHELD / OVERTURNED is final. `validations`, `events`: append-only.
- UPDATE/DELETE on objects, results, attempts, validations, events and TRUNCATE on every table but `meta` are refused
  by triggers. These guard against accidental rewrites (a bug, an ad-hoc statement); they are not a boundary against
  a superuser, who can disable triggers (s5).

Functions (PL/pgSQL, SECURITY DEFINER, owned by a NOLOGIN owner role, fixed search_path):
- `publish(...)`: locks the chain row; returns the recorded outcome if the attempt was already classified (the
  lost-acknowledgement path); stores the four objects (also for attempts it then refuses: evidence) and checks the
  manifest's claims against the bytes -- spec/trace/output-checkpoint sha256, trace_bytes, output_checkpoint_bytes,
  (chain_id, epoch_index) = the call, identity fields present -- any failure -> INVALID; records the result;
  ADVANCES only if `state = OPEN AND generation = expected_generation AND head_index = k-1 AND head_epoch_digest =
  expected_parent AND head_checkpoint_sha256 = the manifest's input sha`; otherwise, on a HALTED chain -> HALTED,
  else classifies against the live publication at k: same work_id + same digest -> DUPLICATE; same work_id +
  different digest -> DISAGREEMENT, a contest (CONTESTED at the head, TAINTED with descendants) and the chain
  HALTED; anything else -> STALE.
- `record_attempt_outcome(...)`: INVALID / REFUSED_UNAPPROVED attempts (bytes that fail the publisher's checks;
  code that is not approved), recorded without publishing; idempotent per attempt.
- `record_validation(chain, k, epoch_digest, state, checks, replay_digest, host, validator)`: VALIDATED | INVALID |
  MISMATCH about the named digest. Refused if that digest is no longer the live epoch k (overturned and re-published
  meanwhile: a stale validation is never re-attributed), if VALIDATED comes with a disagreeing replay digest, if a
  MISMATCH has none, or if a REPLAY check has no digest. MISMATCH (-> AUDIT_MISMATCH) and INVALID (-> CORRUPT_BYTES)
  open a contest and halt the chain. If another contest is already open, the adverse validation is recorded as
  PENDING; when that contest is resolved, the pending one opens its own contest and the chain stays halted.
- `resolve_contest(contest, replay_digests, published_bytes_ok, resolver)`: the verdict is computed IN SQL -- a
  unanimous replay equal to the published digest with the bytes ok -> UPHELD; unanimous and equal to the
  challenger, or the published bytes not ok -> OVERTURNED (publications at k.. marked rejected, head rewound to
  k-1 with that epoch's checkpoint, generation +1); otherwise UNRESOLVED (still open, still halted, resolvable
  later). After UPHELD or OVERTURNED, the earliest pending adverse validation of a live epoch opens the next contest.
- `create_chain(...)` (the genesis bytes must describe the row), `put_object(...)`.

Division of labour on verification. The database checks every byte hash, the manifest's position and the lineage
guard. It cannot recompute work_id and epoch_digest (jsonb is not canonical JSON), nor whether SPEC is the one the
chain's genesis derives at k. Those run in the PUBLISHER (moonshot.epoch.model.verify_epoch plus the derived-spec
check) before `publish`. A self-consistent forged identity or a look-alike chain's epoch is therefore stopped by the
publisher, not by the database -- which is why publication authority is one trusted role, and why a validator
replays later on an independent host.

Connection loss (pg.py). A Moonshot handle uses a DEDICATED connection, never evidence_wiki's pool: the pool returns
connections with session state intact, and a handle's SET ROLE leaked into the next borrower (found 2026-10-10). A
dead connection is replaced on the next call. `publish` is retried as a whole on a fresh connection after any
OperationalError/InterfaceError (connection loss, also lock timeout, deadlock, serialization failure): every step
is idempotent per attempt id, so an attempt is classified exactly once whether the connection died before the call,
inside the transaction (the server rolls back) or after COMMIT (the retry gets the recorded answer).

## 5. Authority, authentication, isolation (OP-NF2 s7) -- explicit, including what is NOT achieved

Roles (NOLOGIN, `moonshot_*`): owner (owns everything), reader (SELECT), coordinator (create_chain), publisher
(publish, record_attempt_outcome), validator (record_validation), resolver (resolve_contest). PUBLIC has nothing:
no table privilege, no EXECUTE. Moonshot code does `SET ROLE` to the narrowest role for each act.

Achieved: fleet workers never receive Moonshot code paths that write the schema; the executed epoch code has no
database or network configuration; publication authority sits in one trusted publisher; validation and resolution
are separate identities; every guard is in the database, not in a client.

NOT achieved, stated plainly: every program client -- including Fabric node workers -- logs in as the `postgres`
SUPERUSER through the git-tracked evidence_wiki/config.json default (verified 2026-10-10: rolsuper, bypassrls). A
superuser bypasses every grant and can disable the append-only triggers (ALTER TABLE ... DISABLE TRIGGER, or
session_replication_role = replica), so the role separation and the guards above are BUG CONTAINMENT, not a
security boundary, until the
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
