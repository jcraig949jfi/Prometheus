# Fabric / Moonshot / Pan interface contract -- v0.3 (C-012-T001, OP-NF2)

Owner: Themis (Moonshot). Reviewers: Odysseus (Fabric), Pan (Pan). Date: 2026-10-10.
Authority: operator OP-NF2 (roles/Themis/prompts/2026-10-10_op_nf2/). Status: DRAFT FOR REVIEW -- review
requests sent (comms #1986 Pan, #1987 Odysseus). Pan reviewed s6 (#2031, no change requested); Odysseus has been
offline since 2026-10-03.
v0.2 (same day, after T002's mutation table and review of the GREEN tree): s4 records the schema as built --
validations name the digest they examined, an adverse validation behind an open contest stays pending instead of
being dropped, guards on chains and contests, TRUNCATE refused on every evidence table, connection-loss semantics.
Nothing in s1-s3 or s6-s7 changed. The interfaces Pan and Odysseus were asked to review (s3, s6) are as in v0.1.
v0.3 (same day, after T003-T007 ran): records what was built and measured, with NO change to any interface a
reviewer was asked about. s3: the dispatch idempotency key as built (it includes the schema), the publisher's
candidate rule, the runtimes the executor accepts (synthetic.v1 and the native moonshot.native.wforge v1), and
what T004 measured about the inline checkpoint. s4: record_receipt, record_materialization, the catalog_v view,
the grants, and where each schema lives (production `moonshot` exists since T007). s6: the lake tables as built
(six; Pan inspected them, #2031), the settle window and the oracle verdicts. s7: the node runtime as used.
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
  idempotency_key="moonshot/<schema>/<namespace>/<chain>/<k>/g<generation>[-r<i>][-sha<12>][<tag>]",
  metadata={"moonshot": {schema, chain_id, namespace, epoch_index, expected_parent, expected_generation}},
  campaign_id="C-012", host_affinity=<optional, for the two-node race>)`. As built (v0.3): the schema is part of
  the key, so a test, qualification or benchmark schema can never collide with production keys; `-r<i>` only for
  replicas; `-sha<12>` only when a test dispatches a base other than the chain's approved one; `<tag>` is a
  caller-chosen suffix for a deliberate re-dispatch of the same epoch and generation (the benchmark uses it after a
  non-PUBLISHED classification).
- `get_task`, attempts and `artifact_content` reads (read-only). Nothing else; no lease, reap or finish calls.
- Node workers (s7) are Fabric workers run exactly per fabric/FREEZE.md "Node runtime", named
  `worker.<host>.moonshot`, caps `moonshot.epoch.v1`, executors `script` only.
- Publisher candidates (as built, 01936df0a): the succeeded attempt of each completed task submitted by the
  Moonshot principal whose metadata names this schema, skipping tasks already classified in `<schema>.attempts`.
  (Fabric clears tasks.current_attempt when an attempt ends, so that column cannot be the skip key; using it made
  every pass refetch every completed task.)

The executor receives only its args and FABRIC_OUT_DIR (Fabric's script executor gives it no database or network
configuration). For synthetic epochs the 4 KB input checkpoint travels inline as a base64 argument with its sha256,
and the executor refuses a mismatch. Native epochs with large checkpoints need an object-fetch path: DESIGN ITEM,
not built (Fabric artifacts are capped at 16 MB each). Measured by T004 (v0.3): the inline checkpoint is then
stored three times -- in fabric.tasks params (base64), as a Fabric artifact blob and as a Moonshot object -- and
Fabric's per-attempt record is about two thirds of the database's growth per epoch (~42 KB at the margin). The
proposed fix, checkpoints by reference (a checkpoint_refs row: sha256, bytes, uri; identity unchanged), is a
schema v2 item, cut only when a workload needs it. With Fabric's 1 s idle poll and one epoch in flight per chain,
an epoch needs at least a few seconds of work for coordination to stay small (T* = 3 s on two nodes).

Runtimes the executor accepts (the genesis names one; `moonshot.epoch.runtime.REGISTRY`):
- `moonshot.synthetic` v1 (synthetic.v1, C-008): deterministic CPU busy-work, the benchmark and fault-injection
  workload.
- `moonshot.native.wforge` v1 (C-012-T007): one wforge Encounter -- the world wforge's grammar expands from a
  genome -- advanced ticks_per_epoch ticks per epoch, the checkpoint holding the Encounter's ENTIRE state (chained
  epochs == one monolithic run, tick for tick). Spec params: genome, world_id (must be the genome's),
  episode_seed, ticks_per_epoch, policy {"name": "affordable-seeded", "version": 1, "seed"}, wforge_world_sha256
  (sha256 of wforge's world.py + genome.py, LF-normalised). A different wforge implementation, world or episode is
  REFUSED, so a repaired wforge is a different runtime input, never a silent change. The policy is fixed
  plumbing: it never takes an unaffordable action, so wforge's F09 defect path is avoided, not repaired.

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
- `record_receipt(chain, receipt_bytes, actor)` (v0.3): stores a canonical receipt content-addressed and appends a
  `receipt` event naming its sha256 with the head it describes (index, generation, state).
- `record_materialization(report, actor)` (v0.3): appends a `materialization` event carrying a lake run's report
  (per table: appended, watermark, lake and Postgres counts, oracle verdict) -- Moonshot's own record, never pan.run.
- View `catalog_v(object_sha256, kind, title, summary, published_at, ref)` (v0.3): one row per LIVE published
  epoch (rejected publications excluded); object_sha256 = the epoch's manifest sha256, kind 'moonshot.epoch',
  ref '<schema>:<chain>/<k>'. Pan's collector reads it (s6).

Grants (EXECUTE only; PUBLIC has nothing): coordinator -- create_chain, put_object, record_receipt,
record_materialization; publisher -- publish, record_attempt_outcome, put_object; validator -- record_validation;
resolver -- resolve_contest; reader -- SELECT.

Where the schema lives (v0.3): production `moonshot` on M1, created by C-012-T007's run N20261010A
(2026-10-10T11:23Z), schema_version 1; `moonshot_qual` holds the qualification evidence (T003 Q20261010A, T005
D20261010A); throwaway `moonshot_t_*` (tests) and `moonshot_b_*` (T004 benchmark points) are dropped after use.

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

## 6. Pan's lake (OP-NF2 s4) -- agreed with Pan (#2004, 2026-10-10T08:33Z)

- Authoritative: Postgres `moonshot` (metadata + content-addressed objects). The lake is DERIVED (Pan's P1).
- Where: the Iceberg catalog metadata is in M1 Postgres (schema `pan_iceberg`), the data files are local paths on
  M2's NVMe (C:/Prometheus-data/pan/lake). Every lake reader and writer runs ON M2; the Ubuntu nodes and M1 read
  Moonshot's authoritative rows in Postgres, never the lake.
- Writer: Moonshot's materializer (on M2) calls Pan's public functions itself -- no Pan poller, nothing on the path
  depends on a running Pan process. Interface as of Pan 801e09d6b:
  `pan.iceberg.write(name, arrow_table, mode="append", namespace="moonshot", snapshot_properties={"watermark": ...})`
  and `pan.iceberg.last_snapshot_properties(name, namespace="moonshot")`. Conditions (Pan's): write only namespace
  `moonshot`, never `pan.*`; one writer per table; use the functions as they are (ask Pan for a change, never vendor
  a copy); new columns arrive by schema evolution, a rename or type change needs a new table.
- Tables (namespace `moonshot`): epochs, attempts, validations, contests (one row per database row) and trace_lines
  (the event/measurement table: one row per canonical trace line). Columns borrow pan.result_rows names where the
  meaning matches: `seat` (producer), `kind` (epoch | attempt | validation | contest | trace), `line_no` (position
  in the canonical trace), `record` (the canonical JSON text where kept), `object_sha256` for content addresses (not
  blob_sha, which means a git blob in Pan's tables); plus `publication_id` (orders the watermark), `published_at`
  (world time, from Postgres), `materialized_at`, `materializer` (instance id).
  As built (v0.3; the tables Pan inspected, #2031): SIX tables, contests split in two so each is append-only --
  epochs (key publication_id), trace_lines (publication_id + line_no), attempts (the classification event_id),
  validations (validation_id), contests_opened (contest_id), resolutions (the resolution event_id). Qualification
  tables carry the prefix `qual_` (Pan: keep them); production tables have none and were first written by T007.
- Idempotent and recoverable: each append carries a watermark (the last publication id it covers) in the new
  snapshot's summary; a restart reads the CURRENT snapshot's watermark and resumes after it, so a crash between the
  Iceberg commit and anything else neither loses nor duplicates rows. Oracle per run: row counts per table vs
  Postgres, logged in Moonshot's own records (not pan.run).
  As built (v0.3): each table's watermark is the largest of ITS key covered. A row is eligible once older than a
  settle window (default 60 s, server clock), because a transaction that drew a smaller key can commit after a
  larger one. The oracle compares keys, not only counts: OK, or MISSED (Postgres rows behind the watermark absent
  from the lake, with their keys), INVENTED (lake rows Postgres does not have) or DUPLICATED (a key twice); a
  MISSED row is restored exactly by a repair run. One materializer per (schema, namespace) at a time (a Postgres
  advisory lock). Reports go to record_materialization (s4).
- Catalogue (pull): a stable view `moonshot.catalog_v(object_sha256, kind, title, summary, published_at, ref)`
  of PUBLISHED EPOCHS (not trace lines); Pan's refresh collects it into pan.artifact (source 'moonshot'). While
  logins are superuser Pan's collector can read it; with per-role logins it needs moonshot_reader. Built (v0.3):
  live epochs only (s4); Pan's collector pan/moonshot_index.py (229fe50a4) reads moonshot.catalog_v and
  moonshot_qual.catalog_v, whichever exist.
- Size: synthetic epochs are bytes; < 50 MB is fine (Pan); the lake volume has ~630 GB free.
- Publication never waits on the lake; a lake outage only delays materialization.

## 7. Node runtime for the demonstration (s3)

ubu001: `~/fabric-runtime` is at 9c022347e (fabric-v0.2 + the DEF-ODY-019 repair). ubu002: its `~/fabric-runtime` is
pre-freeze, so a separate detached worktree at the same commit is used; nothing of Fabric's on either node is
modified. Workers: `EW_DB_HOST=192.168.1.202 python3 -m fabric worker --agent worker.<host>.moonshot --caps
moonshot.epoch.v1 --executors script`. Fault injection for the conflicting-result race is node-local (a file
under /var/tmp naming a TEST namespace) so no task submitter can trigger it; production namespaces ignore it.
As used (v0.3; T003, T004, T007): BOTH nodes run the workers from a dedicated checkout `~/fabric-runtime-moonshot`
at 9c022347e (clean; verified 2026-10-10T11:53:16Z) with work root `~/fabric-work-moonshot`; each node's own
`~/fabric-runtime` is untouched (ubu001 at 9c022347e, ubu002 still pre-freeze 78156ba1d). T003 and T007 ran on
the canonical Fabric schema with `--poll-s 2 --idle-exit-s 1800`; T004 set FABRIC_SCHEMA to a throwaway schema
per point with `--poll-s 1 --idle-exit-s 900`. Workers are stopped after each window; none runs between windows
(0 at the verification above).

## 8. Review record

| Reviewer | Requested | Outcome |
|---|---|---|
| Pan | comms #1986, 2026-10-10 | questions answered #2004 (s6 rewritten to match); committed text reviewed #2031 (2026-10-10T10:01Z): "no change requested to s6"; collector built against catalog_v |
| Odysseus | comms #1987, 2026-10-10 | pending (offline since 2026-10-03) |

v0.3 asks nothing new of either reviewer: it records the system as built and measured. Pan's interface (s6) is
the one Pan reviewed and inspected; Moonshot's use of Fabric (s3) is unchanged (submit, reads; no lease, reap or
finish calls), and the as-built key and candidate rule are Moonshot-side. Odysseus's review, when it comes, is
of v0.3. T001 stays open until then.
