# R-EP epoch contract v1 (moonshot/epoch)

Owner: Themis. Campaign C-008 (TH-MOON-M4, EP-MOONSHOT). Date: 2026-10-06.
Authority: operator OP-LC1 (roles/Themis/prompts/2026-10-06_op_lc1/02_OPERATOR_OP-LC1_verbatim.md),
design v0.3 R-EP / N1 / N3 / N4 / N5 / N7 (roles/Themis/design/MOONSHOT_DESIGN_v0.3.md), Astra F08.
Scope: SYNTHETIC epochs (Lane C). No organisms, world physics, S-meter or RSO evidence. Native
distributed reproductive populations are out of scope until D3/D4 establish these semantics.

This file is the contract the D3 matrix tests. It is frozen before the tests are written; a change
after D3 is green is a new contract version with its own note.

## 1. Canonical bytes and digests

- CANONICAL JSON: an object of strings, integers, booleans, null, lists and objects only (NO floats),
  serialized UTF-8 with sorted keys, separators `,` and `:`, ASCII escapes, no NaN. Bytes that do not
  round-trip to themselves are not canonical.
- Raw byte strings (checkpoints, traces, spec bytes) are identified by plain SHA-256 of the bytes
  (lowercase hex), so `sha256sum` can check them.
- Derived identities use domain-separated SHA-256: `sha256(TAG || 0x00 || canonical_json(obj))`.

## 2. Semantic identity (OP-LC1 contract change 1)

THE GIT COMMIT SHA IS TRANSPORT IDENTITY, NOT SCIENTIFIC IDENTITY. Semantic identity is defined over
canonical bytes only and is the same on any transport, layout, remote or host:

- `spec` = canonical JSON `{schema: "moonshot.epoch.spec.v1", chain_id, epoch_index, runtime:
  {name, version}, params}`, derived deterministically from the chain genesis and the epoch index.
- `work_id` = `H("moonshot.epoch.work.v1", {input_checkpoint_sha256, spec_sha256, runtime})`: the
  question (epoch inputs + spec + runtime).
- `epoch_digest` = `H("moonshot.epoch.result.v1", {work_id, trace_sha256, output_checkpoint_sha256})`:
  THE semantic identity of a completed epoch (inputs/spec/runtime + canonical outputs).
- `runtime` is the SEMANTIC runtime `{name, version}`. The git SHA of the code that implements it is
  provenance (attempt receipts) and authorization (s8), never identity.
- The MANIFEST (canonical JSON, schema `moonshot.epoch.manifest.v1`) binds chain_id, epoch_index,
  runtime, input_checkpoint_sha256, spec_sha256, work_id, trace_sha256 + length,
  output_checkpoint_sha256 + length, epoch_digest. It contains NO attempt metadata (no host, clock,
  worker, attempt id, retry count, git SHA). A manifest is valid iff every digest recomputes from the
  bytes it names.
- Execution is pure: `run(runtime, input_checkpoint, spec) -> (trace, output_checkpoint)`. A runtime
  may not read clock, environment, host, filesystem, network or unseeded randomness. The canonical
  trace therefore cannot carry attempt metadata: a retried epoch's trace is byte-identical to the
  first attempt's, so an ordinary retry can never look like an RSO content-reset intervention.
- Comparisons of MEANING use work_id and epoch_digest. Equal git SHAs are only a fast path; unequal git
  SHAs with equal epoch_digest are the SAME epoch (DUPLICATE, never DISAGREEMENT).

## 3. Transport: git locates bytes

- Data-plane refs live under `refs/moonshot/<namespace>/` on a DEDICATED remote, never the Prometheus
  repository, its main, or its production ref namespace (OP-LC1 #1). The code refuses to push any ref
  outside `refs/moonshot/` and refuses a remote URL on its denylist (the Prometheus origins).
- An epoch is stored as a commit whose tree is `MANIFEST.json`, `SPEC.json`, `TRACE`, `CHECKPOINT`;
  its parent is the previous epoch's commit (the chain's genesis commit for epoch 1, whose tree is
  `GENESIS.json`, `CHECKPOINT`). Objects are written with git plumbing (`hash-object --stdin`,
  `mktree`, `commit-tree`) so no working tree or line-ending conversion touches the bytes, with fixed
  author, committer, date and message, so honest duplicates usually produce one commit. That is an
  optimization; identity is s2.
- SLOTS. Every coordination object is a slot whose value is a commit, updated by compare-and-swap:
  `chains/<chain>` (the chain head), `leases/<chain>`, `contest/<chain>`, `validation/<chain>`,
  `receipts/<worker>`. Two layouts, identical semantics:
  - PER_CHAIN: one ref per slot, `refs/moonshot/<ns>/<slot>`; CAS = `git push
    --force-with-lease=<ref>:<expected>` (empty expected = must not exist).
  - SINGLE_REF: one ref `refs/moonshot/<ns>/index` whose tree holds, per slot, a pointer file with the
    slot's commit SHA; each index commit also takes the slot's new commit as a parent so it stays
    reachable. CAS on a slot = CAS on the whole index; when the index moved but the slot did not, the
    writer rebuilds on the new tip and retries (a CONTENTION retry, counted). This emulates workgraph's
    claim-is-a-push-to-main.
- Unique, never-contended refs: `staging/<attempt>`, `quarantine/<chain>/<epoch_index>/<attempt>`,
  `rejected/<chain>/<epoch_index>`, `nodes/<node>`.

## 4. Publication (OP-LC1 contract change 2)

Two phases, so output blobs are durable before the manifest is exposed:
1. STAGE: push the epoch commit to `staging/<attempt>` (expected absent). Blobs are now on the remote,
   exposed to nobody.
2. CAS the chain slot from the parent commit the work was built on to the staged commit.
3. Clean up the staging ref (best effort; a leftover staging ref is garbage, never meaning).

The ATTEMPT gets exactly one terminal publication outcome:

| Outcome | When |
|---|---|
| PUBLISHED | this attempt's CAS moved the chain head. A push grants NO scientific authority. |
| DUPLICATE | the published epoch at this index has the same work_id and the same epoch_digest. |
| DISAGREEMENT | same work_id, different epoch_digest. The attempt's commit goes to a QUARANTINE ref and the chain fails closed (s7). |
| STALE | this attempt's parent is no longer on the chain's lineage (the chain was rewound); nothing is compared or published. |
| REFUSED_UNAPPROVED | the spec names unapproved code (s8); nothing executed. |
| HALTED | the chain is CONTESTED or TAINTED (s7); nothing executed. |

and one transitional state that must be resolved before it counts as anything:

- AMBIGUOUS: the CAS push gave no definitive answer (lost acknowledgement, timeout). The worker
  re-reads the head: head = its commit -> PUBLISHED; head still = its parent -> the push did not apply,
  retry the CAS; otherwise classify as DUPLICATE / DISAGREEMENT / STALE. An unresolved AMBIGUOUS
  attempt stays in the worker's spool and is NEVER counted as published.
- REMOTE_UNAVAILABLE (also transitional): the remote cannot be reached. The worker keeps at most ONE
  unpublished result per chain in its durable spool, executes nothing further on that chain, backs
  off, and resolves the spooled attempt on reconnection exactly like a late attempt. Local completion
  is never publication; a worker that can push gains no authority.

A late attempt (head moved past its parent) compares its epoch_digest with the epoch published at its
own index on the current lineage: DUPLICATE or DISAGREEMENT (with descendants: TAINT, s7).

## 5. Leases are an efficiency hint, never authority

- `leases/<chain>` holds `LEASE.json` `{chain_id, epoch_index, holder, attempt_id, acquired_unix,
  expires_unix, state: HELD|RELEASED}`. Acquire by CAS when the slot is absent, RELEASED, or HELD and
  expired by the acquirer's own clock; release by CAS to a RELEASED tombstone.
- Publication checks only the chain head. A stolen, expired, skewed or missing lease therefore changes
  how much work is wasted, never what is published. Leases may be disabled entirely; every guarantee
  in this contract still holds (D3 case 10). Lease records are attempt metadata, outside the trace.

## 6. Validation is a separate state

Publication says only "these bytes are at the head". Validation is a separate axis, written ONLY by a
validator or resolver identity to `validation/<chain>`, never by a worker's push:

- UNVALIDATED: default for every published epoch.
- VALIDATED: the manifest's digests recompute from the published bytes, the lineage links (input
  checkpoint = previous output, spec = derived spec), and the chain's replay policy is met (for Lane
  C: every epoch byte-verified and the audited sample replay-verified by an independent execution).
- CONTESTED / TAINTED / REJECTED: s7.

"Accepted epoch" in D4 means VALIDATED. D4 reports per-PUBLISHED and per-VALIDATED denominators.

## 7. Disagreement fails closed

- CONTESTED: a disagreement at the chain head (no descendants). A worker that detects it writes the
  `contest/<chain>` marker (CAS; it may create, never clear) and quarantines its own result. Every
  worker HALTS on a contested chain. The first writer never wins silently.
- TAINTED: a disagreement found at epoch k after descendants k+1..n exist (late attempt or audit
  replay). Epochs k..n are TAINTED and the chain halts until DETERMINISTIC REPLAY resolves it.
- RESOLUTION, only by a resolver, only by replay: re-execute work_id from its input checkpoint on an
  independent executor and compare:
  - replay = published digest -> UPHELD: the challenger was faulty; the marker records RESOLVED_UPHELD
    and the chain resumes.
  - replay = challenger digest -> OVERTURNED: epochs k..n are REJECTED; the resolver archives the
    branch at `rejected/<chain>/<k>` and rewinds the head to epoch k-1 by CAS (the ONLY non-fast-
    forward move, and only the resolver makes it); epoch k is then re-executed normally.
  - neither, or the replays disagree -> UNRESOLVED: the chain stays halted (execution INVALID).
- Quarantined bytes are evidence. They are never promoted; a resolved chain re-executes instead.

## 8. No auto-authorization of code (N7)

A chain genesis names `runtime {name, version}` and `approved_code_sha`. A worker executes an epoch
only if the runtime is in its own registry (implemented by its own pinned code), `approved_code_sha`
passes its approval oracle (production: an ancestor of Prometheus origin/main), and its own code SHA
is approved. Otherwise REFUSED_UNAPPROVED: nothing runs, a receipt is written. Writing to the data
plane can never approve code, create authority, or validate an epoch.

## 9. Every attempt is charged, outside the canonical trace

Every attempt, whatever its outcome (including crashed-then-recovered, refused and halted), produces
one RECEIPT `{attempt_id, worker_id, host, platform, python, code_sha, chain_id, epoch_index, work_id,
epoch_digest, outcome, flags, timings, cpu, git_ops, push_attempts, contention_retries, bytes_pushed,
bytes_fetched, lease}`. It is written durably to the worker's local spool first, then appended to
`receipts/<worker>` (single writer). A worker that restarts flushes its spool first. Retry costs are
charged even when the result is discarded.

## 10. D3 acceptance matrix (all MUST pass, under both layouts)

1. Duplicate execution: one PUBLISHED, one DUPLICATE, no double effect.
2. Worker death mid-epoch (including a real process kill): re-execution from the input checkpoint;
   exactly one published successor; the dead attempt is recovered and charged.
3. Lease expiry: reclaim; the original holder's late completion is DUPLICATE; the chain is unharmed.
4. CAS collision: two completions race; one PUBLISHED, the other DUPLICATE.
5. Remote outage: REMOTE_UNAVAILABLE, bounded spool, nothing counted as published, no partial claim;
   resolution on reconnection.
6. Idempotent replay: two chained epochs replayed equal uninterrupted execution; a retried epoch's
   canonical trace is byte-identical to the first attempt's.
7. Heterogeneous-host canonical trace: the same epoch digests across hosts, platforms and layouts;
   host metadata only in receipts; renaming or reordering host metadata leaves canonical bytes equal.
8. Ambiguous push: resolves to PUBLISHED (applied) or a retried CAS (not applied); never double-counted.
9. Planted disagreement: QUARANTINE + CONTESTED + halt (first writer does not win); a late
   disagreement with descendants TAINTS the branch until replay resolves it (UPHELD and OVERTURNED).
10. Leases disabled: cases 1-9 hold.
11. Unapproved-code spec: REFUSED_UNAPPROVED everywhere; nothing executed; receipt written.
12. Skewed worker clock: early lease steal wastes work; exactly one published successor.
Plus: transport independence (different commit metadata or layout, same epoch_digest => DUPLICATE),
no push outside `refs/moonshot/`, workers never clear a contest or write validation.

## 11. Fault points

The attempt state machine exposes named points for injection: `after_head_read`, `after_lease`,
`mid_execute`, `after_execute`, `after_stage`, `cas_ambiguous` (the push applied, the
acknowledgement is lost), `after_cas`, `after_receipt_spool`, `before_lease_release`. A fault is a
CRASH (the attempt is abandoned with no cleanup, as a process death would leave it) or a CALLBACK
(used to interleave workers deterministically).
