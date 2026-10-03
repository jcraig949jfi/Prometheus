# Salvage digest: infrastructure -- execution, ledger, provenance, observability (R0 + institutional)

Evaluator: salvage evaluator for EPIMETHEUS (Phase 3 architect OPUS-5.5). Date 2026-10-01.
Worktree: C:/prometheus-worktrees/epimetheus-phase3 (HEAD 91f1c9c2d), read-only except as disclosed in s8.
Frozen inputs read first: docs/phase3/design/OPUS-5.5/RSE_ARCHITECTURE.md (R0..R5, s7 inference boundary) and
requirements.jsonl (ids cited below, e.g. PRV-03). Locators: evidence/ixi.md s1-s2, evidence/sis-a.md s1.2-1.3 and
s3, evidence/tit-a.md. Every verdict below was made after opening the source; most were also checked by running
the component's own tests and/or a planted-defect probe (s7).

Independence and safety: nothing under docs/phase3/design/ other than OPUS-5.5/ was opened; roles/Dionysus/ was not
opened. No path containing 'holdout' or 'nestor_secrets' was opened (evidence_wiki/ingest/ingest_holdout_v1.py and
evidence_wiki/gold/benchmark_holdout.json are known by name only). Credential-bearing files were NOT opened:
evidence_wiki/config.json, vivarium/config.json, the repo-root `keys` module imported by prometheus_llm, the fabric
node token file. Cosmos holdout directories lie outside this group and were not listed or touched (the Atlas Cosmos
harvester atlas/harvest/cosmos.py was not opened).

The question asked of every component: DOES THIS SATISFY A PHASE 3 REQUIREMENT BETTER THAN REBUILDING IT?

-----------------------------------------------------------------------------------------------------------------
## 0. Bottom line

1. NOTHING in this group is KEEP. No component satisfies an R0 requirement as it stands. The program built a great
   deal of provenance machinery, but it was built per seat, around a fleet of ~50 LLM seats and three stores
   (Vivarium queue, SFE ledger, PEW), and every piece is welded to that topology: M1 Postgres reached through the
   PEW credential loader, comms identity, Windows Task Scheduler one-shots, HTTPS services on M1, Linux-only
   workers.

2. The FOUR load-bearing R0 pieces have NO implementation anywhere (git grep, s5):
   - the signed verdict batch job (PRV-02, SCI-02): there is no signing code in any infra component;
   - dependency-driven demotion (SCI-16): nothing stores dependency hashes on verdict rows;
   - the row-class predicate filter (PRV-07): only a precursor (SFE evidence_class);
   - a session-log token harvester (INF-02): nothing reads agentic-session logs.
   These are REBUILD-from-nothing. They are also the pieces the architecture says ONLY R0 may own.

3. Two components are worth HARDENING into Phase 3 machinery:
   - Agent Fabric store + worker (fabric/): DB-enforced one-live-attempt-per-task, lease exclusivity with fencing
     tokens, late-finish rejection, DB-clock expiry, a runtime that captures artifacts even when the executor
     dies. It is the best existing candidate for CMP-04 (one job runner) and, through its disposable claude
     executor, for HUM-04 / INF-06 (scheduled, capped build sessions). Named defects in s3.1.
   - prometheus_llm: the right shape for the R5 model-call choke point (INF-01, INF-02, AGR-16) but it is a choke
     point in name only (about 5 importers against about 70 files with direct SDK/HTTP calls), its audit is opt-in
     and never enabled, and it drops billed retries and cache tokens.
   - (minor) productive_liveness: a pure function with a demonstrated defect that misreads every job longer than
     60 s.

4. Worth EXTRACTING (small, tested, generic; each is a pattern of tens to a few hundred lines, not an engine):
   - SFE ledger core: per-world hash chain (sfe/events.py) + the prospective-prediction window closed by an atomic
     commit + typed evidence class (ENGINE_WORK_RESULT vs CLIENT_ASSERTED) + typed replication. This is the
     closest thing in the repo to PRV-03, and its semantics should be ported. Its chain is NOT anchored: I
     truncated a chain and deleted a whole chain without detection (s7).
   - Vivarium sealed-spec + blinding contract: hash exactly the execution inputs, provenance outside the hash,
     explicit null, executor sees only (experiment_id, spec bytes, spec hash); DB-enforced state machine with an
     append-only event table; errata view instead of deletion.
   - toolbox receipt.py: content-hashed receipt id, per-file chain, strict read vs forensic scan, disjoint
     engineering/science ledgers, replay class, cpu_s. Tail truncation is undetected (s7).
   - comms.identity (fail-closed store identity), comms.manifest (LF-normalised artifact hash, PRV-01),
     archaeon.workspace (canonical-checkout refusal + receipt; exists in 8 drifting copies).
   - Alethelia's {value, query} | {unknown, query} field contract with tri-state rules (INF-03), Metis compose.py's
     dependence-collapse union-find (REP-06 / SCI-01 Rep axis), Atalanta null_bound's park contract (CMP-08).

5. RETIRE outright: comms queue, Fabric A2A gateway, promexec broker, Atlas comb + policy layer, Achilles census,
   PEW as a store/service, SFE as a service, Vivarium as a service (single global slot, 95-193 s per row of
   overhead around 0.1 s of science), the Vivarium PEW outbox and deadman.

6. HISTORICAL_CONTROL: the Atlas index (experiment/attempt/fact rows with commit/blob/line pointers) and the PEW
   campaign_observations table (32,938 rows with line provenance, ixi.md s1) are the best existing corpora for the
   requirement tests that re-score history (SCI-01 test "re-score 20 historical headline results", SCI-03 test
   "reclassify historical nulls"). Their classifiers must NOT be reused: Atlas maps INCOMPLETE, UNCONFIRMED,
   NOT_SUPPORTED, UNQUALIFIED and NOT_REPLICATED to POSITIVE (demonstrated, s7).

Estimated R0 + institutional build (new code incl. tests): ledger with segment files and anchored heads M (8-15M
tokens), signed verdict job + row-class filter + dependency demotion + derived multiplicity M-L (15-30M), Fabric
hardening as the one runner M (6-12M), receipts S (2-4M), session token harvester + build ledger + stop rule S-M
(3-6M), derived status/digest generator S (2-4M), prometheus_llm hardening S (1-3M). Total roughly 40-75M tokens.
Salvage saves perhaps 8-15M of design, invariant discovery and test fixtures (mostly Fabric's shaken-out
invariants and the SFE/Vivarium semantics), not the core R0 code.

-----------------------------------------------------------------------------------------------------------------
## 1. R0 and institutional needs vs what exists (one line each)

    need (requirement)                         best existing artefact                     verdict
    deterministic runner, keyed streams,       toolbox backends/local.py (other group);   none in this group; receipts
      snapshot/restore (REP-01, REP-07)          SFE executors' replay labels               EXTRACT only
    one job runner, idempotent by input        Fabric store+worker (key is CALLER-        HARDEN Fabric
      content hash; leases/fencing (CMP-04)      supplied, not a content hash)
    append-only hash-chained ledger with       SFE sfe/events.py (per world, unanchored); EXTRACT semantics, REBUILD
      segment files (PRV-03)                     toolbox receipt chain (per file);          ledger with anchored heads
                                                 Vivarium append-only trigger               and segment files
    prediction before observation (PRV-03,     SFE commit boundary: created_seq <         EXTRACT the rule; SCI-04 still
      SCI-04)                                    committed_seq; retrospective typed         needs git-ancestor prereg
    signed verdict batch job (PRV-02, SCI-02)  NOTHING (no signing code anywhere)         REBUILD from nothing
    row-class filter (PRV-07)                  SFE evidence_class; PEW MODEL_EXTRACTED;   REBUILD (precursors only)
                                                 Atlas parsed vs model-authored rows
    dependency-driven demotion (SCI-16)        NOTHING                                    REBUILD from nothing
    derived status, no model-written status    Alethelia (field/query/tri-state),         EXTRACT Alethelia contract;
      (INF-03), weekly digest (HUM-04)           productive_liveness, Achilles census       HARDEN liveness; RETIRE census
    token accounting incl. agentic sessions    Fabric env_receipt (cost/turns; token      REBUILD harvester; HARDEN
      (INF-02), build ledger + stop (INF-06)     counts discarded); prometheus_llm opt-in   prometheus_llm
                                                 audit; NO session-log harvester
    receipts with CPU/GPU/mem/energy/wall      toolbox receipt (wall, cpu_s); Fabric      EXTRACT toolbox schema + Fabric
      (CMP-02, NRG-01)                           env probe (packages, sha)                  env probe; add mem/energy/tok
    clean-tree receipts, no untracked inputs   workspace guard (dirty ignores untracked   EXTRACT + fix
      (PRV-04)                                   and ignored files); SFE release.py hash
    content addressing over canonical bytes    comms/manifest.py, SFE ids.canonical_bytes EXTRACT + fix
      (PRV-01)
    one primary store, derived views rebuilt   PEW (a SECOND store) raw-vs-projection     RETIRE store; keep idea
      (PRV-06)                                   split
    negative evidence never lost (PRV-08)      Fabric typed attempt outcomes; Vivarium    EXTRACT patterns
                                                 closed tick outcomes; SFE attestation
    no orphan services (CMP-08)                null_bound, Vivarium deadman/park,         EXTRACT contract
                                                 Achilles park (self-defeating predicate)
    no credentials in tracked files (PRV-11)   VIOLATED: ew/db.py:14-16 states tracked    fix before anything is reused
                                                 config.json carries cleartext secrets;
                                                 no secret scanner in repo
    operator is not the relay (HUM-03)         comms queue (model-written bodies);        Fabric tasks can carry it
                                                 Fabric tasks
    model choke point (INF-01, INF-05,         prometheus_llm                             HARDEN
      AGR-16)

-----------------------------------------------------------------------------------------------------------------
## 2. Tests run, and what they show

Run from a scratch directory with PYTHONDONTWRITEBYTECODE=1 and -p no:cacheprovider, timeouts <= 300 s:

    suite                                                       result        notes
    comms/tests/test_manifest.py                                2 passed      pure
    archaeon/tests/test_workspace.py (-k "not sfe_ledger")      5 passed      the deselected test fails BY DESIGN on
                                                                              a host without an SFE ledger (it is a
                                                                              deployment check inside a unit suite)
    fabric/tests/test_executors.py                              4 passed,     the 2 failures are `import fcntl` on
                                                                2 failed      Windows: the worker is Linux-only
    SFE tests/test_sfe_invariants.py                            23 passed     tmp SQLite; T15 tamper + mid-delete
    prometheus/toolbox/tests/test_integrity.py                  203 passed    NOT hermetic -- see s8
    agents/alethelia/test_alethelia.py                          7/7 controls  fixture-injected
    roles/Pronoia/science/test_productive_liveness.py           23 passed     pure
    roles/Atalanta/reference/test_null_bound.py                 9 passed      pure
    roles/Metis/season1/specimen/test_adversarial.py            13 passed     pure
    achilles/census/tests/test_census.py (-k "not mailer")      23 passed     3 mailer tests import
                                                                              scripts/send_brief_email.py; not run

Not run: fabric/tests/test_store.py, comms/tests/test_identity.py, test_comms.py, test_instances.py, all 590
vivarium tests, atlas index tests (all need the live M1 Postgres); prometheus_llm/tests/test_offline.py (imports the
repo-root keys module: credential surface); the remaining 33 SFE test files (not needed for the verdict).

What passing means here: every suite tests what its author feared. None tests the defects in s7. The pattern is
consistent: controls are strong on the failure that already happened and blind one step to the side of it.

-----------------------------------------------------------------------------------------------------------------
## 3. Components

### 3.1 Agent Fabric store + worker (fabric/store.py, worker.py, executors.py run_script, schema.sql)  -- HARDEN

What it really does. A Postgres task/attempt/lease/artifact/event store (schema.sql:33-146) with pull workers.
Invariants enforced in the DATABASE: one running attempt per task (partial unique index, schema.sql:91), one
unreleased lease per resource (schema.sql:131), one task per (principal, idempotency_key) (schema.sql:64), every
expiry on the DB clock. Claim takes the task and all resource leases in one transaction with SKIP LOCKED and a
savepoint per candidate (store.py:356-402); a reaped attempt that comes back late cannot finish the task
(store.py:496-525, `late_finish_rejected`). The worker checks out a detached worktree per base SHA, runs the
executor with a heartbeat thread, and the RUNTIME (not the executor) uploads final text, stdout, stderr, an
environment receipt, delivered files and a patch of any checkout change (worker.py:166-264). The script executor
runs a repo file or module at the pinned SHA with no shell and an env allow-list (executors.py:157-185).

Correctness. Invariants by schema; FP-001 kill-and-reap probe REPORTED passed; 23 defects found and repaired in 3
days (ixi.md s1), each logged under a freeze with a regression test (FREEZE.md). Usage: 347 tasks / 373 attempts,
all on ubu001/ubu002 (ixi.md). Store tests need live Postgres (not run); executor tests 4/6 pass on Windows.

Defects (named):
- CMP-04 says idempotent BY INPUT CONTENT HASH. Here idempotency is a caller-chosen key (store.py:168-197). Two
  submits of the same script/args/SHA with different keys run twice; the same key with different content returns
  the old task silently.
- Untracked-input hole (PRV-04): after an attempt, `_restore` runs `git reset --hard; git clean -fdq`
  (worker.py:162). Without -x, gitignored files written by one attempt survive into the next attempt on the same
  cached base, and `git status --porcelain` never saw them, so no patch records them. Demonstrated (s7).
- Receipt (worker.py:198-219) has host, python, platform, env-manifest sha, worktree head, exit code, model, but no
  CPU time, peak memory, energy or token fields (CMP-02, NRG-01).
- Linux-only: `import fcntl` at module top (worker.py:18), os.killpg/start_new_session (executors.py:73-95),
  PATH=/usr/bin:/bin. The program's main hosts are Windows; BACKLOG_AFTER_FREEZE.md lists "Windows node worker".
- Coupling: store.connect() imports evidence_wiki.ew.db (the PEW credential loader) and comms.identity
  (store.py:87-108); worktrees come from a canonical clone at ~/Prometheus (worker.py:35).
- `terminal states never change` is enforced only in Python (store.py:472), not by a trigger; `events` is
  "never updated" by convention only (no trigger, unlike Vivarium).
- Requires the M1 Postgres; a Phase 3 runner on one or two hosts could use the same invariants on a local store.

Slot: R0 "one job runner" (CMP-04, PRV-08 typed attempt outcomes, PRV-09 producers declare outputs via out/).
Serves: CMP-04, PRV-08, PRV-09, CMP-02 (after repair), REP-03 (host-labelled receipts). Cost: M (6-12M): content-
hash idempotency, -x clean or fresh worktree per attempt, receipt fields, ledger hand-off, portability decision,
decouple connector. Reason: the invariants are the expensive part, they are correct by construction and were
shaken out under real load; rebuilding would re-pay the 23-defect discovery cost.

### 3.2 Fabric claude executor (fabric/executors.py run_claude, tools/rogit.py)  -- HARDEN

What it really does. Runs a disposable `claude -p` with an EMPTY config dir, HOME set inside the attempt, an
explicit model, Read/Grep/Glob scoped to the worktree and out/, Write only to out/, plain git denied and a
read-only `rogit` wrapper on PATH, secret paths denied, a wall-time limit and cancel/fencing polling
(executors.py:103-150). The JSON result is parsed for final text, model ids and `total_cost_usd, num_turns,
duration_ms, session_id` (executors.py:143-147).

Defects: token counts are DISCARDED -- only the key names of `modelUsage` are kept (executors.py:144-145), so
input/cache-read/output tokens per model (INF-02) must be re-parsed from the raw stdout artifact (which is kept).
No token budget: the only cap is wall_s (INF-06 wants flag at 1.0x and stop at 1.5x of a token budget). No boot
packet generator (INF-07); the instruction is the prompt. Same Linux-only and Postgres coupling as 3.1.

Slot: institutional -- HUM-04 ("build sessions launched by a scheduler from a prioritised queue with per-session
caps and done criteria"), INF-06, HUM-03 (cross-model review tasks executed by code). Cost: S (2-4M) on top of 3.1.
Reason: the isolation recipe (empty config, scoped tools, rogit, denied secret paths) was attacked and repaired
(P7, D12 in the code comments) and is exactly what a Phase 3 build scheduler needs.

### 3.3 Fabric A2A gateway (fabric/gateway.py) and promexec broker (fabric/promexec/)  -- RETIRE

Gateway: stateless A2A v1.0 JSON-RPC over the store; "PILOT-ONLY deviations: no authentication (LAN only),
ListTasks is not scoped to the caller" (gateway.py:18-20). No Phase 3 slot needs an agent-interop protocol.
promexec: root sudo broker with systemd DynamicUser / PrivateNetwork for model-proposed Python; round-2 source
"NOT installed, NOT enabled" (STATUS_EXPERIMENTAL.md). Phase 3's only model-generated executable material in the
run path is DGM genomes (E8 variation), which execute inside the DGM interpreter, not as host Python. Cost NA.

### 3.4 comms queue (comms/api.py, schema.sql, __main__.py)  -- RETIRE

What it really does: a Postgres message queue between LLM seats (messages, receipts, per-seat task_queue,
per-instance presence), message sha256 over subject+body, pull-only, model self-declares its model id at boot
(schema.sql agents.model comment). 1,239 messages since 09-11, of which 86 heartbeats in ~25 h (ixi.md s2).
Reason: Phase 3 has at most three concurrent build sessions and forbids model-written status and heartbeats
(INF-03); cross-seat work becomes Fabric tasks (HUM-03). Model identity is self-declared, not runtime-reported
(MEA-06). Tests need live Postgres (not run).

### 3.5 comms.identity + evidence_wiki/ew/db.py identity guard  -- EXTRACT

What it really does: before the first statement, read pg_control_system().system_identifier + current_database()
from the LIVE connection and compare with a committed environment registry; refuse on mismatch, unknown
environment or unreadable identity (identity.py:103-186; ew/db.py:38-55, also on the pool fallback path,
ew/db.py:117-130). The residual (a physical basebackup clone passes) is stated, not hidden (identity.py:41-49).
Correctness: adversarial tests with positive / negative / cheat (perfect schema on the wrong cluster) controls
exist (test_identity.py) but need live clusters; not run.
Slot: R0 store connector (PRV-06 one primary store). Cost S (<1M). Defects: environments.json is keyed to two
physical clusters measured 2026-09-11; the db.py wrapper it ships in also loads a tracked config.json that the code
itself says carries cleartext db_password / auth_token / machine_tokens (ew/db.py:14-16) -- PRV-11 violated. Port
the 60-line check, not the connector.

### 3.6 comms.manifest (comms/manifest.py)  -- EXTRACT (fix first)

What it really does: sha256 over LF-normalised bytes for text, raw bytes for binary (NUL in first 8 KiB); writes
and verifies a MANIFEST.md for a flat directory (manifest.py:25-67). Tests 2/2 pass.
Defects: verify() checks only listed files -- a file ADDED after the manifest was cut passes (demonstrated, s7),
so it is not custody. "Equals the git blob" (docstring, test name) is false: the git blob id is SHA-1 over
"blob <len>\0"+content; this is SHA-256 over content. It ignores .gitattributes (a file committed with CRLF or
-text gets a hash different from its committed bytes); it rewrites lone CR; flat directory only.
Slot: R0 PRV-01 canonical bytes, PRV-04 custody. Cost S. Reason: the normalisation rule is the right one and is
already shared by SFE release.py and verify_deploy; the verifier must become complete (extra/missing both fail).

### 3.7 Workspace guard (archaeon/workspace.py and 7 copies)  -- EXTRACT (one copy, fixed)

What it really does: path-free main-worktree detection (git-dir == git-common-dir), fail-closed when git cannot
answer (ARCH-52), a receipt {base_sha, branch, worktree_path, dirty, repo_id} (archaeon/workspace.py:36-103).
Tests 5/5 pass (one deselected deployment test fails by design).
Defects: `dirty` uses `--untracked-files=no` (archaeon/workspace.py:82; ew/workspace.py:69; viv/workspace.py:150):
untracked and ignored inputs are invisible, which is exactly what PRV-04 must block. Eight copies drift (archaeon,
evidence_wiki, vivarium 220 lines, herakles, proteus, techne 174, crius 294, SFE 148); the PEW copy lacks repo_id.
Slot: R0 receipts (PRV-04). Cost S. Reason: trivial to rebuild, but the fail-closed and repo_id lessons are paid for.

### 3.8 Atlas index and harvesters (atlas/ harvest/, db.py, gitsrc.py, classify.py, sql/)  -- HISTORICAL_CONTROL

What it really does: versioned harvesters read git blobs, idle SQLite and Postgres of other engines (NPE, frontier,
Vivarium, PEW, Archaeon campaigns, Cosmos) into a 34-table `atlas` schema of campaign/experiment/attempt/segment/
fact/edge rows; each fact points at a source (commit, blob, line) (harvest/common.py:1-11; gitsrc.py is read-only
git). Counts match source in every sample (158 = 158, 130 = 130, 1,242 = 1,242; ixi.md s1).
Defects: classify.status_class (classify.py:106-126) is unanchored substring regex in a fixed order, so
COMPLETE/PASS/QUALIFIED -> POSITIVE (MEA-09 violation; 649 of 723 POSITIVE rows are Vivarium "completed", ixi.md)
and, demonstrated (s7), INCOMPLETE, UNCONFIRMED, NOT_SUPPORTED, UNQUALIFIED, NOT_REPLICATED, UNSUPPORTED,
NOT_ROBUST, PASSIVE_ARM -> POSITIVE and SKILL_TEST -> NEGATIVE. The unit test (test_atlas.py:24-29) checks five
easy words. Index lags activity by 8.6 d; adapters for 5 of 15 engines; model-authored catalogue/theory stored
beside parsed rows (16 strings disagree with their reference rows, ixi.md).
Slot: none in production (PRV-06: Phase 3 axes are born with the experiment, not retrofitted). As a fixture: the
row corpus is the input for SCI-01 / SCI-03 historical re-scoring tests and for X0-style audits. Cost NA (read as
data). Reason: numbers are trustworthy, classes are not; keep the rows, discard the classifier.

### 3.9 Atlas comb and policy layer (atlas/comb.py, policy.py)  -- RETIRE

comb: 13 SQL rules writing ATLAS_DERIVED signals; 192 signals, all OPEN, none consumed (ixi.md). policy: fixed
weights over model-written proposal fields (policy.py:23-26); the STRATEGY horizon appends a REDUCE directive and
the other branch a DEPRIORITIZE directive unconditionally (policy.py:203, 236); 92 scores, 0 outcomes ever. This is
a model-fed scalar steering layer, i.e. the AGR-13 / SCI-12 anti-pattern. No Phase 3 slot.

### 3.10 Achilles census (achilles/census/)  -- RETIRE (concept to INF-03)

What it really does: every 6 h on ELSA, roster from roles/ on all refs + a registry, S0-S6 activity rules over
commits, comms and ew, field-level provenance, HTML/email, commit + push (run.py:150-233). Tests 23/23 pass
(mailer tests not run). 10 of 14 seats right against git (ixi.md).
Defects: the park bound cannot fire on success: `productive` is true whenever origin/main moved (run.py:171-172),
and the census itself pushes every run, so the next run always sees a moved origin/main. Commit attribution falls
back to path majority (classify.py attribute_commit) -> Mnemosyne misattribution; status_md_state takes the FIRST
"seat state:" line; CLOSED -> RETIRED (classify.py:185-210). Its ontology (seats, fleet hosts, comms presence) does
not exist in Phase 3. Reason: INF-03 needs a deterministic status generator over the build ledger, receipts and
git; Alethelia's contract (3.18) is the better seed. Keep its three defects as negative controls for that
generator.

### 3.11 PEW / Evidence Wiki store and service (evidence_wiki/ew/store.py, service.py, migrations/)  -- RETIRE

What it really does: a second knowledge store (schema ew, 41 tables) with write-path gates (vocabulary refusal,
"derived_view_cannot_back_evidence", no provenance no write; store.py:23-321), a 2,003-line REST/wiki service on
port 8377, BM25/embedding/tensor projections. Curated layer frozen at 79 experiments; 143 of 147 claims
MODEL_EXTRACTED; DOWN since 09-23 with the watchdog's alarm unanswered 8 days (ixi.md s1).
Defects: it is a second authoritative store (PRV-06 wants one); model-extracted rows would be ignored by PRV-07
anyway; standing service with no owner response (CMP-08); tracked config.json with credentials (ew/db.py:14-16,
PRV-11); migration 015 applied from a dirty tree (ixi.md). Ideas worth keeping in R0 design: raw vs projection
tables, derived views cannot back evidence, content-addressed observation ids with an ingestion_conflicts table
instead of overwrite.

### 3.12 PEW campaign reader and campaign_observations (evidence_wiki/ew/campaign_ingest.py, migration 014)  -- HISTORICAL_CONTROL

What it really does: reads committed Archaeon campaign files at one commit and lands each producer row as one
content-addressed observation; labels stored as written, UNKNOWN vs NULL distinguished, reconstructed identity
marked (campaign_ingest.py:1-23). Hard-coded to campaigns 1-5 and their paths and seeds (campaign_ingest.py:57-66).
Slot: none in production; the landed 32,938 rows are a historical corpus with line provenance (fixture use as 3.8).

### 3.13 Daedalus SFE ledger core (SerendipityFoundryEngine/sfe/events.py, ids.py; runtime.py register_prediction / commit_experiment / record_observation)  -- EXTRACT

What it really does: every world state change appends an event in the same SQLite transaction; entry_hash =
sha256 over canonical JSON of (world_id, index, type, ts, actor, payload, refs, causal, artifacts, prev_hash)
(events.py:48-104); forks share the parent prefix by reference; verify_world recomputes the chain
(events.py:145-188). Predictions are content-hashed and sequence-stamped (runtime.py:2126-2160); commit_experiment
atomically seals the spec hash, closes the prospective window (only created_seq < committed_seq can ever be
prospective) and stamps the running engine source hash (runtime.py:2332-2359); record_observation refuses an
uncommitted experiment, types evidence as ENGINE_WORK_RESULT only when bound to a COMPLETED work item of that
experiment, else CLIENT_ASSERTED, and refuses CLIENT_ASSERTED in require_attestation worlds; duplicate bindings
must be explicit replications and can never re-adjudicate; post-commit predictions must be marked retrospective
(runtime.py:2361-2470). Tests: test_sfe_invariants.py 23/23 pass (T11 prediction-before-observation, T15 tamper
and mid-chain delete, T16 replay).
Defects (demonstrated, s7): the chain is anchored only by worlds.head_hash in the SAME database. Deleting the last
event and rewriting head_hash/next_index passes verify_world (ok=True, checked 4 of 5); deleting ALL of a world's
events passes (ok=True, checked=0) because the head check is skipped when no rows remain (events.py:185). A full
recompute of the chain by anyone with write access is likewise undetectable. ts is a float inside the hash. Chains
are per world (no global order commitment); no signature; no segment files.
Slot: R0 ledger (PRV-03) and the semantics of PRV-07 (evidence class) and SCI-04 (prospective window). SCI-04
additionally requires the preregistration to be a git ancestor of the first data commit, which SFE does not do.
Cost: S-M (3-8M) to port the rules into the new ledger; adopting the runtime itself would be XL. Reason: these are
the best-specified provenance rules in the program and they were attacked by auditors; the code around them is
not reusable.

### 3.14 SFE as a service (runtime.py 5,125 lines, api.py 1,599, serve.py, attestation.py, executors.py)  -- RETIRE

FastAPI over HTTPS on M1, SQLite single writer, clients/sessions/grants/budgets/sharing topologies, attestation
intent journal for lock failures. SFE contains no search, mutation, selection or simulation; only onemax, NK and a
nondeterminism control ever shipped (sis-a.md s1.3). A standing service whose only users were other seats'
pipelines (CMP-08 prefers batch jobs). The Gen-2 canary (identical RNG per arm, parity-preserving mutation) is a
HISTORICAL_CONTROL already listed in salvage/search.md.

### 3.15 SFE verify_deploy.py (+ sfe/release.py build identity)  -- RETIRE (fold the idea into receipts)

verify_deploy checks that pinned files are present and LF-identical, that the tree reproduces the pinned
engine_source_hash, and that the live HTTPS service reports it (verify_deploy.py:68-150; endpoint and m1.crt are
host-specific). It exists because the service ran from a shared checkout other roles switched branches in.
release.py hashes the LOADED sfe/*.py at import and stamps it into every commit event (release.py:22-41) -- a good
idea, but it covers only top-level sfe/*.py (no subpackages, no dependencies). Phase 3 receipts need code hash +
clean tree or applied-diff hash (PRV-04) for whatever ran; that is the receipt component (3.20), not a deploy
verifier for a service Phase 3 will not have.

### 3.16 Vivarium sealed spec + blind executor contract (vivarium/viv/spec.py, request.py, queue.py, migrations/001)  -- EXTRACT

What it really does: the sealed spec contains exactly the execution inputs; provenance (who/why/family/arm/
candidate set) lives in queue columns outside the hash; explicit null, never omission; payload must match the
kind's contract exactly; outcome_rule with a required indeterminate branch (spec.py:1-90; README "sealed
specification"). ExecutionRequest.from_queue_row projects exactly four columns and re-verifies the spec hash
(request.py:75-140); test_blinding.py asserts provenance cannot reach the executor and that any execution-input
change changes identity. The DB enforces the queue state machine, freezes terminal rows and the sealed request,
and refuses UPDATE/DELETE on the event table (001_vivarium_queue.sql:96-167). Contamination is recorded in an
errata view; analysis reads register_clean. Tests: 590, all on live Postgres (not run).
Defects: append-only trigger does not cover TRUNCATE; no hash chain; experiment_id is a random uuid (CMP-04 wants
content identity); README says crash recovery never requeues ("release always resolves to failed", README:219-229)
but deadman.release_new_attempt returns stranded rows to queued for attempt n+1 (deadman.py:158-175, 500-512) --
documentation drift on a scientific-integrity rule.
Slot: R0 runner input contract (CMP-04, REP-01, PRV-04) and the blinding of R2 rulers (s5 of the architecture:
ruler manifests forbid condition labels). Cost S (1-3M). Reason: the contract is the valuable part and it is short.

### 3.17 Vivarium as a service (daemon.py, loop.py, runner.py, deliver.py + outbox, deadman.py, kinds/executors)  -- RETIRE

One globally running experiment enforced by a unique index on a generated column (001_vivarium_queue.sql:41-52);
95-193 s per row around 0.1 s of science (sis-a.md, D-list); every kind wraps another seat's toy (onemax, CA rule
tables, ECA, 3-input CEGIS); no mutation, selection or pressure ever ran through it; science bypassed it from
Campaign 4 (sis-a.md s1.2). The PEW outbox (deliver.py) exists only because the record was split across three
stores; with one primary store it has no job. The deadman is a Windows scheduled one-shot that relaunches a
process and releases stranded rows. Keep the engineering record (10 production defects found by 11 canaries,
sis-a.md SV-05) as context, not code.

### 3.18 prometheus_llm (prometheus_llm/client.py, types.py, registry.py)  -- HARDEN

What it really does: one complete() over openai-compatible, gemini, anthropic and `claude -p` CLI adapters, raw
requests only; ok means usable content, not HTTP 200; auto-expand on empty content with finish_reason=length;
fallback chains; council (client.py:95-373). Per-call audit JSONL opt-in via PROMETHEUS_LLM_LOG (client.py:49-66).
Defects: audit is opt-in and no committed launcher sets it (git grep: only docs mention it); audit records ONE row
per target -- the final attempt (client.py:351, 365) -- so billed retries and the billed empty first call of an
auto-expand are never logged; anthropic cache_creation/cache_read tokens are dropped (client.py:205-212); the CLI
adapter records no usage and sets model_served to the REQUESTED name or "default" (client.py:241-243), which
violates MEA-06 runtime-reported identity; prompt hash is SHA-1 over the first 20,000 chars of the JSON messages
(client.py:331, 56); gemini adapter raises on a non-JSON body despite "never raises". Not a choke point: 5
importers (forge, hecate, hephaestus x2, eos test) against ~20 files using the anthropic SDK, ~18 the openai SDK,
~29 hitting chat/completions directly and 7 spawning `claude -p` (git grep). Imports the repo-root `keys` module.
Tests: offline suite exists (monkeypatched adapters); not run (keys import). No test covers the audit.
Slot: R5 boundary (INF-01 fork tag per call, INF-02, AGR-16 isolation of the E8 variation operator, INF-05 static
check that R0-R3 never import it). Cost S (1-3M). Reason: shape is right and dependency-free; make audit mandatory
and per attempt, require a fork tag and a budget id, capture cache tokens, and make it the ONLY import path.

### 3.19 Metis compose.py (roles/Metis/season1/specimen/compose.py)  -- EXTRACT

What it really does: union-find over declared load-bearing upstream tokens collapses N agreeing items into
independent reasons (compose.py:125-153); negative-existence claims without complete enumeration become UNKNOWN,
never ABSENT; undeclared ids are errors; competing explanations survive until an observed value eliminates them;
no scalar anywhere. Tests 13/13 pass. Validation: n=5 historical episodes, one encoder, post-hoc positive control
(ixi.md).
Slot: R0 verdict job, Rep axis of SCI-01 and REP-06 (count replications after dependence collapse). Only the
grouping kernel and the UNKNOWN-not-ABSENT rule carry over; in Phase 3 the upstream sets must be COMPUTED (import
graph overlap, shared rows, model family, shared seeds), not hand-encoded. Cost S (<1M).

### 3.20 prometheus.toolbox receipt (prometheus/toolbox/receipt.py, backends/local.py accounting)  -- EXTRACT

What it really does: one receipt per run; receipt_id = 96-bit truncated sha256 of the body; prev_receipt_id chains
records within a file; strict read refuses any defect, forensic scan names truncation/edit/duplicate/chain break by
line; engineering and science ledgers must be disjoint; closed status and replay-class vocabularies; kernel_hash
over the toolbox's own modules; wall_s and cpu_s (process_time) (receipt.py:20-188; local.py:425-491). Tests:
test_integrity.py 203 passed.
Defects (demonstrated, s7): dropping the LAST receipt line(s) leaves a valid file (scan defects=[], strict read
accepts) -- the chain only links backwards and nothing commits the head. kernel_hash covers only the 26 toolbox
modules, not the code under test outside it, and there is no git SHA, clean-tree flag or diff hash (PRV-04). No
memory, energy, GPU or token fields (CMP-02, NRG-01). Hash uses default=str, so any non-JSON value is hashed by its
str() form.
Slot: R0 receipts (CMP-02, MEA-09 by the disjoint ledgers, REP-01 replay class). Cost S (2-4M incl. the missing
fields and head anchoring). Reason: best receipt schema in the repo; the head must be committed to the ledger.

### 3.21 Alethelia (agents/alethelia/alethelia.py)  -- EXTRACT

What it really does: every report field is {value, query} or {unknown, query}; 7 deterministic rules each FIRED /
CLEAR / INDETERMINATE (a rule over an UNKNOWN field is INDETERMINATE, never CLEAR); the banner reads calm only with
zero UNKNOWN, zero FIRED and zero INDETERMINATE (alethelia.py:350-388). Tests: 7/7 controls pass (run).
Defects: the `query` is a documentation string, not the executed query -- e.g. q_postgres records a qtext that
differs from the SQL it executes (alethelia.py:68 vs 75-78), so traceability is asserted, not verifiable. All
sources are fleet objects (agora heartbeats, comms receipts, engine/queues BACKLOG, Elenchus shadow) that Phase 3
will not have. Unhosted since 09-11; a wrong-directory run once overwrote the canonical report (ixi.md).
Slot: R0 derived status (INF-03), weekly digest (HUM-04, NRG-02 envelope report). Cost S (1-2M). Reason: the
contract is the anti-confabulation property INF-03 needs; make each field's query the executed artefact.

### 3.22 productive_liveness (roles/Pronoia/science/productive_liveness.py)  -- HARDEN

What it really does: pure function from four timestamps + configured cadence to BOOTING / NO_WORK_OBSERVED /
WORKING / PRODUCTIVE / FAILING / STALLED / INCOHERENT; `now` injected; attempt staleness checked before success,
so a heartbeat cannot rescue a dead worker (productive_liveness.py:141-221). Tests 23/23 pass.
Defect (demonstrated, s7): `success > attempt + future_slack` -> INCOHERENT (productive_liveness.py:186) with a
60 s slack, so ANY successful job that ran longer than 60 s reads INCOHERENT when last_attempt_at records the
attempt start (10-minute job that succeeded 5 minutes ago, cadence 1 h -> "incoherent"). The tests place every
success exactly 60 s after its attempt, on the boundary. Phase 3 runs are 0.3 core-h each.
Slot: R0 derived status for the runner and any standing loop (INF-03, CMP-08). Cost S (<1M): define attempt
start vs end fields. Reason: right design, one wrong inequality.

### 3.23 Atalanta null_bound (roles/Atalanta/reference/null_bound.py)  -- EXTRACT (contract)

What it really does: a loop wrapper that refuses construction without an integer bound and an accountable seat,
counts consecutive ticks whose DOMAIN productivity signal is falsey (artifacts do not count), parks, and leaves a
ParkRecord (null_bound.py:52-126). Tests 9/9 pass.
Defects: the park record lives only in memory, so "a restart does not clear the park record" (null_bound.py:47) is
false for this implementation; the real versions (Vivarium var/park-*.json) persist. The mechanism is only as good
as the productivity predicate -- Achilles (3.10) shows a predicate the loop itself satisfies.
Slot: CMP-08 wrapper for the few standing processes Phase 3 allows. Cost S. Reason: a 100-line contract.

### 3.24 Signed verdict batch job (PRV-02, SCI-02, SCI-01, SCI-15)  -- REBUILD (no implementation exists)

git grep over every infra component finds no signing (no ed25519, no hmac, no signature verification); the only
"verdict" authority historically was whichever seat wrote the row. Precursors: SFE evidence classes and the
prospective rule (3.13), Vivarium outcome_rule (3.16), Metis grouping (3.19). Cost M-L (10-20M with the row-class
filter and derived multiplicity).

### 3.25 Dependency-driven demotion (SCI-16) and row-class filter (PRV-07)  -- REBUILD

No verdict row anywhere stores the hashes of its ruler qualification, world certificate, plant set, statistics
version or preregistration. Origin classes exist only as precursors: SFE ENGINE_WORK_RESULT vs CLIENT_ASSERTED,
PEW MODEL_EXTRACTED, Atlas parsed rows beside model-authored data. Cost folded into 3.24.

### 3.26 Session token harvester and build ledger (INF-02, INF-06, NRG-02)  -- REBUILD

Nothing reads agentic-session logs (git grep for cache_read_input_tokens finds only experiment code). Fabric keeps
the raw claude JSON as a stdout artifact (recoverable per task); interactive seat sessions are unmetered
(ixi.md s2 F). Cost S-M (3-6M): deterministic harvest from session logs, join to commits by the Claude-Session
trailer (Atlas already parses it: classify.py:19), weekly report, 1.0x flag / 1.5x stop.

-----------------------------------------------------------------------------------------------------------------
## 4. Coupling map (why almost nothing lifts out cleanly)

- evidence_wiki/ew/db.py is the shared connector for comms, atlas, fabric, archaeon and ludus (ixi.md s1); it loads
  the tracked config.json (credentials) and calls comms.identity. Lifting fabric or atlas lifts PEW's credential
  loader.
- comms.identity's registry names two physical M1/M2 clusters measured on 2026-09-11.
- Fabric workers: Linux, ~/Prometheus canonical clone, claude CLI, ~/.config/prometheus/claude.env token file.
- Vivarium: SFE HTTP API + PEW HTTP API + Postgres + Windows Task Scheduler one-shots (deadman, deliverer).
- SFE: FastAPI + uvicorn + HTTPS cert for M1; SQLite single writer.
- Atlas: registry.json host table; one adapter per engine; advisory locks shared with Atlas-M2.
- Achilles: ELSA scheduled task, pushes to origin/main every run, email via scripts/send_brief_email.py.
- prometheus_llm: repo-root `keys` module; requests.
- Pure and portable (lift as-is apart from the named fixes): comms/manifest.py, archaeon/workspace.py,
  productive_liveness.py, null_bound.py, compose.py, toolbox receipt.py, sfe/events.py + sfe/ids.py (sqlite3 only).

-----------------------------------------------------------------------------------------------------------------
## 5. Searches that establish absence

- Signing: git grep -i "ed25519|hmac.|nacl|Ed25519PrivateKey|sign(" over fabric, atlas, achilles, comms,
  evidence_wiki/ew, vivarium/viv, SFE sfe/, prometheus_llm, prometheus/toolbox, archaeon/*.py -> one false hit (SQL
  sign() in atlas/comb.py).
- Session token harvesting: git grep "cache_read_input_tokens|cacheReadInputTokens" and ".claude/projects" ->
  experiment and liveness scripts only; no harvester.
- Secret scanning: no pre-commit / gitleaks / detect-secrets configuration tracked.
- Model-call choke point coverage: importers of prometheus_llm vs direct SDK/HTTP callers, counts in 3.18.

-----------------------------------------------------------------------------------------------------------------
## 6. What the history says about this layer (one paragraph)

X0 (RSE_ARCHITECTURE.md s9) found the cheapest repair for 14% of historical apparatus failures was provenance or
implementation. This group is where those repairs were attempted, and the record is consistent: each seat repaired
the defect it had just suffered (CRLF hashes, wrong cluster, canonical checkout, dead consumer, empty-content
success) with a careful local mechanism and a control for that exact failure, and none composed into a single
authority. The result was 8 copies of one guard, 3 stores bridged by an outbox, 4 liveness/status systems, 2 hash
chains with no anchor, and no signer. Phase 3 should take the lessons and the short contracts, and build R0 once.

-----------------------------------------------------------------------------------------------------------------
## 7. Planted-defect probes (run in a scratch directory; nothing written to the repository)

    probe                                                              result
    SFE: delete last event, rewrite worlds.head_hash/next_index         UNDETECTED: verify_world ok=True, checked 4 (was 5)
    SFE: delete ALL events of a world, leave head_hash                  UNDETECTED: ok=True, checked=0
    toolbox: drop the last receipt line of a 4-receipt file             UNDETECTED: scan defects=[], strict read accepts
    atlas status_class on negated words                                 INCOMPLETE, UNCONFIRMED, NOT_SUPPORTED,
                                                                        UNQUALIFIED, NOT_REPLICATED, UNSUPPORTED,
                                                                        NOT_ROBUST, PASSIVE_ARM -> POSITIVE;
                                                                        SKILL_TEST -> NEGATIVE
    productive_liveness: 10-min job, success 5 min ago, cadence 1 h     "incoherent"
    comms.manifest verify after adding an unlisted file                 (1 checked, 0 mismatches): passes
    git reset --hard + git clean -fdq (Fabric _restore) on an           porcelain did not see it; file survives
      ignored cache/ file

-----------------------------------------------------------------------------------------------------------------
## 8. Disclosure: one test run wrote into the repository (repaired)

prometheus/toolbox/tests/test_integrity.py::test_kernel_hash_names_the_kernel_and_only_the_kernel appends a line to
prometheus/toolbox/series.py and tests/test_kernel.py and then restores them with newline="\n"
(test_integrity.py:369-387). On this Windows worktree (core.autocrlf=true) that converted both working copies from
CRLF to LF (content identical to the index; `git diff` empty, `git status` showed M). I restored both files to CRLF
byte-for-byte (LF -> CRLF), after which `git ls-files --eol` shows w/crlf like their siblings and `git status` is
clean. This is itself a finding: the toolbox conformance suite advertised as "pure stdlib" is not hermetic -- it
edits its own source tree in place (and tests/mutants.py rewrites source files by design). A Phase 3 rule: test
suites run against a read-only copy.

-----------------------------------------------------------------------------------------------------------------
## 9. Not checked

- Whether Fabric attempt env_receipts in the live store carry non-null total_cost_usd (no DB access used).
- The comms identity cheat control, Fabric store tests and all Vivarium tests (need live Postgres).
- prometheus_llm offline tests (keys import) and the audit path at runtime.
- Live counts quoted from ixi.md (1,239 comms messages, 347 fabric tasks, 32,938 PEW observations) were not re-run.

Files opened (code): fabric/{store,worker,executors,gateway(head)}.py, schema.sql, FREEZE.md, BACKLOG_AFTER_FREEZE.md,
promexec/{broker(head),STATUS_EXPERIMENTAL}.md/.py, tests/{test_store(head),test_executors}.py;
comms/{identity,manifest,api(outline)}.py, schema.sql, environments.json, tests/{test_manifest,test_identity(head)}.py;
evidence_wiki/ew/{db,workspace,store(head),campaign_ingest(head)}.py, migrations/014 (head), README.md;
archaeon/workspace.py, archaeon/tests/test_workspace.py; atlas/{classify,policy(parts),comb(head),db(head),gitsrc(head)}.py,
harvest/common.py (head), tests/test_atlas.py (head); achilles/census/{classify(parts),run(parts)}.py, tests (head);
vivarium/{README.md, viv/spec.py(head), viv/request.py(parts), viv/deadman.py(parts), viv/deliver.py(head),
viv/pew.py(head), migrations/001, tests/test_blinding.py(head), tests/conftest.py(head)};
SFE sfe/{ids,events,release}.py, runtime.py (2126-2470), attestation.py (head), deploy/verify_deploy.py,
tests/{conftest,test_sfe_invariants(parts)}.py; prometheus_llm/{client,types(part)}.py, README.md, tests (outline);
roles/Metis/season1/specimen/{compose(1-260),test_adversarial(head)}.py; agents/alethelia/{alethelia(parts),
test_alethelia(head)}.py; roles/Pronoia/science/{productive_liveness,test_productive_liveness(outline)}.py;
roles/Atalanta/reference/{null_bound,test_null_bound(head)}.py; prometheus/toolbox/{receipt.py, README.md(head),
tests/test_integrity.py(parts), tests/mutants.py(150-196)}.
