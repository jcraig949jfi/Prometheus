+==============================================================================+
| C-008 LANE C -- THE R-EP SYNTHETIC-EPOCH FABRIC: REVIEW PACKET               |
| Author: Themis (Project Moonshot, prong 3), instance m2-0e9b1ed2,            |
|         host M2 / SPECTREX5. Campaign C-008, thread TH-MOON-M4, EP-MOONSHOT. |
| Date: 2026-10-06                                                             |
| For: the operator (HITL) and external reviewers                              |
| Status: T001 (D1+D2 under D3), T002 (D4 prereg), T005 (D5 auto-join) CLOSED; |
|         T003 (D4 LAN baseline) and T004 (GitHub arm) BLOCKED, causes named.  |
| Self-contained: every load-bearing number is inline. No repo access needed.  |
+==============================================================================+

----- 0. Summary, mandate, verdict -----

Mandate. Operator approval OP-LC1 (2026-10-06T08:31Z) authorized Lane C of Project
Moonshot: build and test, on SYNTHETIC epochs only (deterministic CPU busy-work; no
organisms, no worlds, no science), the distribution layer that later evolutionary
science will ride on. The unit is the R-EP shard epoch: immutable checkpoint + epoch spec
-> trace + next checkpoint. The transport is git compare-and-swap (CAS) on a DEDICATED
remote. OP-LC1 imposed two contract changes:
  (1) the git commit SHA is TRANSPORT identity; semantic identity is a
      transport-independent SHA-256 over canonical inputs/spec/runtime and outputs;
  (2) a successful CAS is PUBLISHED, not "accepted": a push grants no scientific
      authority, validation is a separate state, disagreements fail closed, and a
      disagreement found after descendants exist taints the branch until
      deterministic replay resolves it.

Verdict (engineering, layer 1 -- tests MUST pass). The protocol meets its contract
under every fault we could name and inject, on Windows and Linux, and the tests have
teeth (a mutation table found one real test gap, now closed). What is NOT known: whether
git CAS is an adequate transport at fleet scale. That is the operator's actual standing
hypothesis; its measurement (D4) is preregistered and frozen but has not run, because
the hardware it was frozen against is busy with a peer seat's science (s6).

Numbers in one place:
  - 167 tests green on M2 (Windows 11, 391.7 s) and ubu002 (Ubuntu 26.04, 64.7 s) at
    8a34b60b8; 4 skips by design on each.
  - RED before GREEN: the complete D3 matrix ran first against API stubs -> 144 tests,
    151 NotImplementedError errors (subtests counted) + 1 failure (2154cd9c2).
  - Mutation tables: D3 -- 16 planted bugs, 14 killed on first run, 1 survived and
    exposed a real test gap (now killed by an added test), 1 equivalent. D5 -- 4/4 killed.
  - Field: one real node (ubu002) joined a LAN remote and drained 3 approved chains x 5
    epochs in 14 s; every epoch was validated by full replay on a DIFFERENT OS (M2);
    a chain naming nonexistent code was refused twice with nothing executed.
  - Field finding: Git for Windows pushing over git:// applies the ref and never
    returns. That real lost acknowledgement exposed an unhandled path in my own D2 code
    (every write except the chain CAS crashed on it). Fixed test-first, RED then GREEN.

----- 1. What was built, and what was committed before measurement -----

Commit order (every SHA is an ancestor of main):
  1f94e9197  C-008 opened (T001..T005) and the epoch CONTRACT v1, frozen before any test.
  0867f8577  CONTRACT v1.1, still before any test existed (reason: s5 item 1).
  2154cd9c2  RED: the complete D3 matrix as failing tests (OP-LC1 allowed the first code
             commit to be exactly this).
  dae948bb7  the implementation.  c9081b129  one test added from the mutation table.
  9acef4de8  T001 integrated.  2a86d4db9  T001 + T002 closed with receipts.
  8e69de91e  D4 preregistration FROZEN before any D4 data
             (D4_PREREG.md sha256 52ea7e47ee00063b60224964ce97564e25eab43cddfed9b81df377312141b568).
  f803ee04f, 56ea967c5  D4 instrument (calibrate / make-chains / bench-worker /
             validate-all / report) + known-answer instrument tests.
  43b73bb16 RED -> 0fd1038e7 GREEN -> a4d7bf1c1  D5 node auto-join.
  4ee900033 RED -> 8a34b60b8 GREEN  lost-acknowledgement hardening of every write path.
  f3b63ed5f  D5 field-join evidence.  4b77577e0  T005 closed.

Package moonshot/epoch/ (Python standard library only):
  canonical  canonical JSON (integers only, sorted keys, ASCII) + domain-separated SHA-256
  runtime    synthetic.v1: iterated sha256 busy-work, deterministic, about 2.7M
             iterations/s on M2
  model      genesis, spec derivation, work_id, epoch_digest, manifest, replay
  gitio      git objects written directly from bytes in Python (no working tree, no
             line-ending conversion); remote operations with classified errors
             (RemoteUnavailable / AmbiguousPush / AuthError / RateLimited)
  store      "slots" under refs/moonshot/<namespace>/ on a dedicated remote; two layouts;
             roles WORKER / COORDINATOR / VALIDATOR / RESOLVER enforced at the API
  worker     the attempt state machine, with a durable local spool
  validate   validation, audit replay, contest / taint resolution
  bench      the D4 instrument          join   D5 node auto-join

----- 2. The claim, and why it matters -----

Moonshot's science (survival-only evolution, measured offline) will run as shard epochs
on cheap, flaky e-waste machines. If the distribution layer can double-publish, lose work
silently, let a faulty host's bytes win, or make a retry look like an intervention, every
later scientific claim inherits that defect invisibly. The claim tested: for synthetic
epochs, R-EP yields exactly ONE PUBLISHED successor per parent under worker death, lease
expiry, CAS races, remote outage, ambiguous pushes, planted disagreement, unapproved code
and skewed clocks; identity does not depend on the transport; and publication is never
mistaken for validation.

----- 3. Design as built (the contract, compressed) -----

Identity.
  spec         = canonical {schema, chain_id, epoch_index, runtime{name,version}, params}
  work_id      = H("moonshot.epoch.work.v1",
                   {input_checkpoint_sha256, spec_sha256, runtime})       -- the question
  epoch_digest = H("moonshot.epoch.result.v1",
                   {work_id, trace_sha256, output_checkpoint_sha256})     -- the answer
  H(tag, obj)  = sha256(tag || 0x00 || canonical_json(obj))
  The manifest binds these and carries NO attempt metadata (no host, clock, worker,
  attempt id or git SHA). The runtime is pure, so a retried epoch's trace is
  byte-identical to the first attempt's: a retry cannot look like an intervention.
  The code SHA that implements a runtime is provenance and authorization, never identity.

Transport. An epoch is a git commit whose tree is MANIFEST.json, SPEC.json, TRACE and
CHECKPOINT, with the previous epoch as parent. The commit MESSAGE names the attempt
(v1.1), so the chain head's commit SHA attributes a publication to exactly one attempt;
the tree depends only on canonical bytes.

Slots. Every coordination object is a commit-valued slot changed only by CAS:
chains/<c>, leases/<c>, contest/<c>, validation/<c>, receipts/<worker>.
  PER_CHAIN   one ref per slot; CAS = git push --force-with-lease=<ref>:<expected>.
  SINGLE_REF  one index ref holding a pointer per slot -- an emulation of workgraph's
              claim-is-a-push-to-main, built off the production repository. CAS on any
              slot is a CAS on the whole index; when only other slots moved, the writer
              rebuilds on the new tip and retries (a counted CONTENTION retry).

Publication, two phases. (1) Stage the epoch commit to a unique staging ref: the blobs
are durable and exposed to nobody. (2) CAS the chain slot from the parent the work was
built on. Each attempt ends in exactly one of:
  PUBLISHED | DUPLICATE (same work_id, same digest) | DISAGREEMENT (same work_id,
  different digest: quarantine ref + contest, the chain halts) | STALE |
  REFUSED_UNAPPROVED | HALTED.
Two transitional states, AMBIGUOUS and REMOTE_UNAVAILABLE, are resolved later by
RE-READING, never by re-pushing blindly, and are never counted as published until
resolved. At most one unpublished result per chain per worker.

Leases are efficiency hints only. Publication checks only the chain head, so leases can
be disabled with every guarantee intact (D3 case 10).

Validation is a separate axis, written only by a validator role. Contest resolution is
done only by a resolver role and only by deterministic replay:
  UPHELD -> the chain resumes;
  OVERTURNED -> the bad branch is archived and the head rewound -- the only
    non-fast-forward move in the protocol;
  UNRESOLVED -> the chain stays halted.

Code approval. A worker executes only a runtime in its registry, and only if its own code
SHA AND the chain's approved_code_sha pass its approval oracle. D5 makes that oracle
"ancestor of origin/main" from a clean pinned checkout.

Never the Prometheus repository. The code refuses any remote whose normalized URL
contains jcraig949jfi/prometheus or whose last path segment is "prometheus" (that also
catches a local D:\Prometheus), and refuses any ref outside refs/moonshot/<ns>/.

----- 4. Results (exact) -----

4.1 RED -> GREEN (T001).
  RED 2154cd9c2: 144 tests -> errors=151 (all "NotImplementedError: C-008-T001",
  subtests counted), failures=1 (the denylist did not refuse the real Prometheus origin),
  skipped=4. No import, attribute or type errors: the API the tests use existed.
  First implementation run, dae948bb7: M2 144 OK (333.6 s); ubu002 144 OK (55.4 s).
  Merged and integrated, 9acef4de8: M2 148 OK (327.0 s); ubu002 148 OK (56.0 s).
  Final, 8a34b60b8: M2 167 OK (391.7 s); ubu002 167 OK (64.7 s).
  Skips (4, by design): the real-process-kill test runs once per lease mode (process death
  is layout-independent), and the clock-behind test needs leases.

4.2 The D3 matrix. 33 test methods x 4 variants (PER_CHAIN / SINGLE_REF x leases on /
leases DISABLED = case 10) = 132 tests, plus 16 identity tests (canonical bytes,
synthetic.v1 vs an independent hashlib reference, known-answer vectors, contract formulas,
manifest key set, transport independence across layouts, remote denylist).
  1  duplicate execution            one PUBLISHED, one DUPLICATE, no quarantine/contest
  2  worker death                   crash at after_lease / mid_execute / after_execute ->
                                    re-executed elsewhere, crashed attempt recovered as
                                    ABANDONED_RECOVERED and charged; crash after staging ->
                                    restart publishes, or DUPLICATE if another published
                                    first; crash after the CAS -> counted once; and a REAL
                                    process kill mid-execution (subprocess, killed while
                                    its spool says EXECUTING)
  3  lease expiry                   reclaim; the late holder ends DUPLICATE ("late");
                                    descendants unharmed
  4  CAS collision                  one PUBLISHED, one DUPLICATE; two DIFFERENT chains
                                    contend only on SINGLE_REF (>= 1 contention retry
                                    there, exactly 0 on PER_CHAIN)
  5  remote outage                  REMOTE_UNAVAILABLE, nothing published while offline, no
                                    second execution while a result is pending, the same
                                    attempt publishes on reconnection; fsck-clean remote
  6  idempotent replay              a messy schedule equals an uninterrupted
                                    transport-free replay, digests AND bytes; a retried
                                    trace is byte-identical to the first attempt's
  7  heterogeneous hosts            host labels and worker ids never reach canonical bytes;
                                    known-answer vectors equal on Windows and Linux
  8  ambiguous push                 applied/ack lost -> PUBLISHED once; not applied ->
                                    re-sent (>= 2 CAS pushes); unreachable on re-read ->
                                    stays AMBIGUOUS, then PUBLISHED once; applied and
                                    already built upon -> PUBLISHED
  9  planted disagreement           first writer does not win: quarantine + CONTESTED +
                                    HALTED (runner never called); replay OVERTURNS
                                    (archive, rewind, honest re-execution) or UPHOLDS (the
                                    faulty challenger's bytes stay as evidence); an audit
                                    that finds a bad epoch WITH descendants -> TAINTED until
                                    replay; a late faulty worker -> TAINTED; runners that
                                    disagree -> UNRESOLVED, halted; corrupt published bytes
                                    -> halted before anything is built on them
  10 leases disabled                the whole matrix again, leases off
  11 unapproved code                genesis naming unapproved code, an unregistered runtime
                                    version, or a worker whose own code is unapproved ->
                                    REFUSED_UNAPPROVED, runner never called, receipt written
  12 skewed clocks                  +3600 s steals early but one publication; -3600 s only
                                    waits (BUSY)
  structure                         PUBLISHED is not VALIDATED; workers cannot create,
                                    validate or resolve (PermissionError); only
                                    refs/moonshot/<ns>/ on the remote (fsck clean); every
                                    attempt has exactly one receipt

4.3 Mutation table (D3), one planted bug per copy, run against the tests meant to catch it:
  M01 classify by git SHA, not digest .................. KILLED
  M02 workers ignore open contests ..................... KILLED
  M03 ambiguous push assumed applied ................... KILLED
  M04 leases never block ............................... KILLED
  M05 manifest carries a clock field ................... KILLED
  M06 first writer wins on disagreement ................ KILLED
  M07 no verification of the head before building ...... KILLED
  M08 a worker store may resolve contests .............. KILLED
  M09 denylist without the last-segment rule ........... KILLED
  M10 recovery abandons staged/sent attempts ........... KILLED
  M11 SINGLE_REF blind rebase (slot CAS not re-checked) . KILLED
  M12 unbounded spool .................................. SURVIVED -> test gap, closed
  M13 refusals not receipted ........................... KILLED
  M14 classify without the parent-on-lineage check ..... SURVIVED -> EQUIVALENT
  M15 late disagreement never taints ................... KILLED
  M16 runtime reads the clock .......................... KILLED
  M12's failure shape: a GLOBAL outage also blocks the head read, so the mutant never got
  to execute twice; the bounded-spool rule only bites when the remote is BACK and
  run_attempt (not recover) is called. The added test kills it (mutant: 2 runner calls
  and a new attempt id; real code: 1 call, same attempt). M14 is equivalent: an epoch's
  result depends only on (input checkpoint, spec, runtime), all inside work_id, so the
  work_id comparison subsumes the lineage check. It is kept as defense in depth.
  D5 table: oracle approves all / dirty checkout accepted / node store with coordinator
  role / no binding of running code to the approved checkout -> 4/4 KILLED.

4.4 D5 node auto-join (T005). A node joins only if:
  - its checkout is CLEAN (local edits are not approved code);
  - its HEAD is an ancestor of the approval ref (origin/main);
  - from the CLI, the running moonshot package lies inside that checkout.
The last rule was found during implementation: approving --code-dir says nothing if the
interpreter imported the package from elsewhere; a test was added.
Every store a node builds is WORKER role. The announcement under nodes/<id> is liveness
only and changes no slot. Tests: 8/8, after a RED of 7/7 NotImplementedError.

4.5 Field join (evidence f3b63ed5f).
  - Setup: ubu002 (Linux) in a clean detached worktree at 8a34b60b8, approved against
    origin/main, joining git://<ubu001 LAN daemon>.
  - Run: 2026-10-06T10:12:03Z -> 10:12:17Z, exit 0.
  - Approved chains F000-F002: 15 executions, 5/5 epochs PUBLISHED each.
  - Workers: w0 made 11 attempts and 10 executions; w1 made 6 attempts, 5 executions and
    9 BUSY polls (the two workers stepping around each other's leases).
  - Refusal: X000 (approved_code_sha = a commit that does not exist) got 2
    REFUSED_UNAPPROVED receipts ("chain-code-not-approved") with nothing executed.
  - Validation: M2 (Windows), as VALIDATOR over ssh://, byte-verified AND replayed EVERY
    epoch. All VALIDATED; the published digests equal a transport-free replay. That is
    case 7 in the field: Linux-produced epochs reproduced on Windows.

4.6 D4 instrument (not D4 data). Three known-answer tests:
  - single-worker exact counts;
  - SINGLE_REF contention counted and summed;
  - abandonment and coordination arithmetic on crafted records.
Two smoke runs on temporary local remotes, excluded from data by prereg s9 (2 workers,
40 s, 4 chains, ~0.08 s epochs):
  - per_chain: 126 published, 126 validated, 0 retries, coordination fraction 0.868,
    7501 repository bytes per epoch;
  - single_ref: 54 published, 54 validated, 166 contention retries (3.07 per epoch),
    coordination fraction 0.932.
Both verdicts were RECONSIDER, as epochs that short must be. The point of the smoke runs
is that the instrument SEES contention and coordination cost.

----- 5. Incidents, defects and process holes (recorded plainly) -----

1. Contract v1 had a double-count hole, found while writing case 8. With byte-identical
   duplicate commits, git answers an identical push "up to date" (exit 0), and a worker
   whose acknowledgement is lost cannot tell its own publication from an identical
   twin's: two attempts could both claim PUBLISHED for one epoch. Fixed as v1.1 (the
   commit message names the attempt) BEFORE any test existed. The reason is recorded in
   the contract.
2. The denylist I first drafted (jcraig949/prometheus) would NOT have matched the real
   origin (jcraig949jfi/Prometheus). It was caught by checking the actual URL before the
   tests, then fixed and generalized (the last-segment rule).
3. A RED test was wrong: the forbidden fragment "time" matched the contract's own manifest
   field "runtime". It was corrected after RED and recorded in the commit.
4. Mutation M12 survived: a real test gap (s4.3). A test was added.
5. A D4 instrument test was timing-dependent: it assumed two free-running threads must
   collide within 4 s. It passed on M2, failed on ubu002 (retries 0 while the summation
   identity held), and was made deterministic with a fault-plan interleave.
6. FIELD: the first chain creation from M2 against ubu001's git daemon APPLIED its ref
   and never returned (120 s timeout). Isolation:
   - GIT_TRACE showed the Windows client's `pack-objects --stdout --thin` never exits;
   - the identical push from Linux takes 0.18 s;
   - from Windows over ssh:// it takes 0.83 s.
   Failure shape: the D3 matrix injected ambiguity ONLY at the chain CAS, and every other
   write (chain creation, leases, staging, receipt flushes, node announcements) let
   AmbiguousPush escape and kill the process. Fix, test-first: RED 4ee900033 (14 errors +
   6 failures against the committed store), GREEN 8a34b60b8. Every write path now
   resolves a lost acknowledgement by re-reading. The chain CAS still hands it to the
   worker, which attributes it (case 8 unchanged).
7. The repo's .gitignore has `**/results/`; the first evidence commit was silently empty.
   It was caught by reading git's output; evidence now lives under
   ops/campaigns/C-008/evidence/.
8. A helper bug in the D5 RED tests (an argument passed twice) was fixed before the RED
   was recorded, so RED = 7/7 NotImplementedError.
9. A command that included deleting a temp message file was blocked by a safety check.
   Nothing in it ran; it was redone without the deletion.
10. Two D4 choices were fixed BEFORE any data and journaled. B2 counts ALL contention
    retries (inside attempts, during polls, during receipt flushes), the stricter reading.
    Lease TTL = 3 x D + 30 s, so a lease cannot expire mid-epoch by construction.

----- 6. What is blocked, and exactly why -----

T003 (D4 LAN baseline).
  - The frozen rig R1: a disposable bare repository on ubu001 (Wi-Fi), served by git
    daemon, with 6 workers on M2 and 2 on ubu002.
  - Why it cannot run: M2 measured 84-99% CPU, running Aether's AIM02 production
    (4 jobs, started 05:32 local, wall cap 39600 s, so it ends by 16:32 local / 20:32
    UTC). Running R1 now would contend with a peer seat's science, and would bias the
    coordination metric toward PASS, because slowed epochs shrink the coordination
    fraction.
  - New since the freeze: Windows workers must reach the LAN remote by ssh://, so R1 is
    now a mixed-transport rig. That needs a preregistration ADDENDUM filed before any data.
  - Unblocks when M2 is free, OR when M2 can ssh to ubu003-006. M2's key is authorized
    only on ubu001/002; ubu003-006 host keys are not in M2's known_hosts, and they were not
    trusted on first use silently.

T004 (GitHub WAN-semantics arm; at most 2 workers, at most 250 write attempts).
  - gh is not logged in on M2.
  - Needs: a dedicated private repository, plus a write deploy key that is already
    generated (fingerprint SHA256:bPHyvqEQyOASdbCso9+UQLilyFngHXR0efxGyPVE5EQ). Or a gh
    login.
  - Before any write: an ssh -T greeting check that the key is repository-scoped (the
    authentication-spillover stop rule).

----- 7. What this does and does NOT establish -----

Establishes (layer 1, synthetic epochs only): the twelve named fault classes are handled
as contracted, on two OSes, with tests that kill 15 of 16 planted bugs (the 16th is
equivalent); semantic identity survives a change of layout and host; one real node can
join from approved code and drain work, refusing unapproved chains.

Does NOT establish:
  - that git CAS is adequate at fleet scale -- no D4 data exists;
  - anything about organisms, worlds, sagacity, or native reproductive populations --
    out of scope by OP-LC1 until D3/D4 establish the semantics, and D4 is pending;
  - safety against a malicious credential holder: the remote enforces nothing; roles are
    client-side; a malicious validator or resolver identity is outside the threat model;
  - liveness under hostile or broken workers: ANY worker may open a contest, so one
    faulty host can halt every chain it touches until a resolver replays. Fail-closed by
    design, denial-of-service-prone by consequence;
  - behaviour under real network partitions: ambiguity was injected, plus one real
    field instance;
  - interpreter heterogeneity: every host ran Python 3.14.4 and git 2.53.0; the
    heterogeneity was the OS;
  - scale: the tests use at most 3 concurrent workers; the field join used 2 workers on
    one node;
  - that VALIDATED means more than byte-verification for epochs outside the replay sample
    (the Lane C policy replays every 10th epoch in D4; the field join replayed all).

----- 8. The decision (the operator's), with Themis's lean -----

(a) T003 rig.
    Option 1: grant M2 ssh access to ubu003-006 and run a pure Linux e-waste rig, filed
    as a preregistration addendum before any data, with R1 kept as written.
    Option 2: wait for AIM02 to end (about 20:32 UTC) and run R1 as frozen, plus the
    mixed-transport addendum.
    Lean: option 1. It is the stress rig the thread names, it frees M2, and it avoids the
    Windows transport quirk.
(b) T004. Create the repository and add the deploy key, or decline the GitHub arm. A
    LAN-only D4 still answers the scaling question; GitHub adds real-remote semantics only.
(c) Continue or stop.
    Lean: continue to D4, the one deliverable that tests the operator's standing
    hypothesis.
    "Stop after D3/D5" is a legitimate answer if transport adequacy can wait until real
    epoch sizes exist: D1-D3/D5 stand alone as tested infrastructure.

----- 9. Questions for the reviewer (written to resist agreement) -----

1. "Correctness from CAS + determinism, leases as hints": is it sound, or does it hide a
   liveness failure? Under fail-closed, any single faulty node halts any chain it
   touches. Is that the right trade for science that will run for days on flaky hosts?
2. Should OPENING a contest require evidence that other readers can verify (e.g. the
   quarantined bytes must recompute to a different digest), instead of any worker's say-so?
3. M14 was declared equivalent (work_id subsumes the lineage check). Construct a case
   where it is not.
4. The D4 operating point (30 s epochs, 8 workers) was chosen before Launchpad epoch
   sizes are known. Can P1 (per-chain ADEQUATE) pass while the real workload fails?
   Are 5% coordination, 1/20 retries, 10% claim latency and 1% abandonment the right
   bounds?
5. Is SINGLE_REF a faithful emulation of workgraph's claim-on-main? Leases and receipts
   are on the index; staging and quarantine are separate refs. If it is not faithful,
   P2 tests a straw man.
6. B2 was fixed to the stricter reading before data. That biases toward RECONSIDER for
   the single-ref arm. Is that fair, or a thumb on the scale for my own prediction P2?
7. The mutation targets were chosen by the author. Which obvious unplanted mutants are
   missing? Candidates: a spool written without fsync; receipts deduplicated by
   attempt_id hiding a double charge; a staging ref never cleaned up.
8. The Windows git:// hang: an upstream client defect, or local interference
   (antivirus, firewall) that was not tested? Does the answer change the D4 rig?
9. "At most one unpublished result per chain per worker": should the bound be global
   per worker, which could otherwise hold pending results on many chains during an
   outage?
10. Is a synthetic-only fabric worth further investment before ANY native epoch exists,
    or does it risk optimizing a transport for a workload that will look different?

----- 10. Artifacts (paths in the Prometheus repository; SHAs on main) -----

  moonshot/epoch/CONTRACT.md                     the R-EP epoch contract (v1.1)
  moonshot/epoch/{canonical,runtime,model,gitio,store,worker,validate,bench,join}.py
  moonshot/epoch/tests/test_d3_matrix.py         cases 1-12 + structure, four variants
  moonshot/epoch/tests/test_identity.py          D1 identity + known-answer vectors
  moonshot/epoch/tests/test_bench.py             D4 instrument known answers
  moonshot/epoch/tests/test_d5_join.py           D5
  moonshot/epoch/tests/test_ambiguity.py         lost acks on every write path
  ops/campaigns/C-008/                           campaign, packets, receipts (T001/T002/T005)
  ops/campaigns/C-008/prereg/D4_PREREG.md        frozen 8e69de91e (+ MANIFEST)
  ops/campaigns/C-008/evidence/D5_JOIN/          field join (+ MANIFEST)
  roles/Themis/prompts/2026-10-06_op_lc1/        OP-LC1 verbatim (+ MANIFEST)
  roles/Themis/journal/2026-10-06.md             the session journal
  Known-answer vectors (independent reference, verified on Windows and Linux):
    KAT epoch 1 epoch_digest 02af8ac6ad9e920d5b3ac6c9343713b5d0ff9eb83b0a55338942141178ee6385
    KAT epoch 2 epoch_digest 92fc3372845d984e8dca40c93fd81a6ec46b64dcfc222b16ded79e7c6cc93acf
  Key SHAs: 1f94e9197 (contract v1) 0867f8577 (v1.1) 2154cd9c2 (RED) 9acef4de8 (T001)
    8e69de91e (D4 prereg) 56ea967c5 (instrument) a4d7bf1c1 (D5) 4ee900033 / 8a34b60b8
    (lost-ack RED/GREEN) f3b63ed5f (field evidence) 4b77577e0 (T005 closed).

+==============================================================================+
| END. Narrow the claim, reject a finding with evidence, or say "not worth     |
| continuing" -- each is a first-class answer. No D4 data exists yet: nothing  |
| here claims git CAS is adequate at scale.                                    |
+==============================================================================+
