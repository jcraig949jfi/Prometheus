# Holdout D2 firewall: independent adversarial re-audit, v11

- **Auditor:** a disposable Odysseus replica (task tsk-de2aebb693d5, attempt att-d413cabf764e). It has no seat identity.
- **Audited commit:** `e47d6fbbb1ad8a9d761801b2f480dfc1d3412fe1`. This is a merge of origin/main into `nestor/d2v11-2026-09-29`. The v11 code is commit `d7f9d4797`.
- **Same code on origin/main:** `rogit diff --stat e47d6fbbb 6baa07bd8` (6baa07bd8 = refs/remotes/origin/main) over every AUDITED_FILES directory is empty.
- **Method:** I read the code and the history only (Read, Grep, `rogit`).
  - **I ran no code:** no self-test, and no `protocol --code-hashes`.
  - Plain shell and sha256 tools were not available, so I could not recompute any sha256 value myself.
  - Every self-test boolean I quote is the COMMITTED value in `SELFTEST_PROTOCOL.json`. `not_applicable_on_this_os` is `[]` there, so it was produced on Windows (M1).
- **Scope:** FIREWALL.md section "v11" (FIREWALL.md:374-385) first, then a regression check of claims 1-6.
- **What changed since v10:** only `runner.py`, `custody.py`, `selftest_protocol.py`, `SELFTEST_PROTOCOL.json`, FIREWALL.md and AUDIT_BRIEF.md. Evidence: `rogit diff --stat 784d55b63 HEAD` over `prometheus/__init__.py`, `prometheus/cosmos/__init__.py`, `c3/`, `c3_holdout_D/` and `c3_holdout_D2/`.

## Summary

| # | Claim | Verdict |
|---|---|---|
| v11-a | A deliver receipt is written before every world is sent, and is truthful | HOLDS |
| v11-b | Bounded parent-to-child sends | HOLDS for the world and reply sends. BROKEN as stated ("every parent-to-child send"): the `stop` send and the receive are unbounded (V11-1, should-fix, liveness only) |
| v11-c | seal-terminal keeps a verifying final record that lacks its newline | HOLDS |
| v11-d | seal-terminal lock / liveness | HOLDS (notes V11-2, V11-3) |
| v11-e | seal-terminal is bound to the designation's open record | HOLDS (note N1 carried) |
| 1 | Opacity | HOLDS (plaintext length declared; note V11-4) |
| 2 | Secrets never in git | HOLDS for the repo side. The key-holder scan is CANNOT-VERIFY-FROM-REPO |
| 3 | Enforced order | HOLDS mechanically. **BROKEN on record authentication: S1, known OPEN (#925), blocks-PASS** |
| 4 | Controlled reveal | HOLDS |
| 5 | Predictor isolation | HOLDS. The label defect V10-1 of the replica-2 report is still unfixed (V11-5, should-fix) |
| 6 | Draw integrity | HOLDS for the part the repo can show. The sha256 values are CANNOT-VERIFY here (no hashing tool); the blob identity is verified |

**No new blocks-PASS finding.** The only blocks-PASS item is S1, together with branch protection. Both are declared OPEN and are the operator's decisions.

---

## v11-a. Deliver receipts: HOLDS

Code, in `_predict_one`:
- runner.py:1009-1012: the world label is set and the child is (re)started.
- runner.py:1015: `receipts.append("deliver", {"i", "world_tag", "utc"})`.
- runner.py:1016-1017: `_exposed` and `_in_predictor_io` are set.
- runner.py:1020: only THEN is the world sent.
- `Receipts.append` writes, flushes and fsyncs before it returns (runner.py:430-444). A failed write is rolled back (runner.py:438-442) and raises before the send, which becomes an abort through run_all (runner.py:923-926).

Attacks tried:
1. **World data reaching the child before its deliver record.** I checked every parent-to-child message:
   - `probe` carries paths only (runner.py:823).
   - `go` carries nothing (runner.py:959).
   - `predict` is sent only after deliver (runner.py:1020). It carries `i`, V, k and `predictor_seed(i)`, which is a public function of the package hash (runner.py:1067-1068), not the hidden run seed.
   - `ret`/`err` replies are sent only inside the same `_predict_one` call (runner.py:1045-1053).
   - Certification runs in the parent with no child (runner.py:1128-1149).
   - A restarted child receives nothing about world i before deliver(i).

   No path found.
2. **Removing a deliver record after the fact.**
   - The child cannot append to or read the receipts: the isolation probe runs on every (re)start (runner.py:958, 836-839; write probe default runner.py:658; extra read path runner.py:1329).
   - The runner's `repair()` truncates only bytes beyond its in-memory chain (runner.py:449-463), and a deliver record is in memory once `append` returns.
   - seal-terminal keeps the longest verifying prefix (runner.py:1230-1245), so a complete deliver record survives.
3. **A deliver record without a delivery.** This happens if the send fails or the thread cannot start. The record then over-states exposure. That direction is conservative and cannot give a package a VOID.
4. **The labels.** `deliver_records` in the runner abort (runner.py:869) and in the custodian abort (runner.py:1268) is a count over the chain, so it is truthful by construction.

Under Harmonia Addendum J (roles/Harmonia/rulings/RECORD_D2_GOVERNING_AUDIT_AND_SEAL_GATE_2026-09-29.md:344-351), "no deliver receipt in a verifying chain" proves non-delivery. The code above supports that reading. The package's module does execute before deliver(0), because `go` is sent before any world (runner.py:354-360). The package has no world data at that point, so a VOID then is correct.

Committed self-test: `v11_deliver_receipt_before_each_world: true`.

## v11-b. Bounded sends: HOLDS for world and reply sends; the claim is overstated (V11-1)

`_send_bounded` (runner.py:892-911) runs the send in a daemon thread and joins it with a timeout. On expiry it kills the child and returns False. It is used for:
- `predict`, with the full `predict_timeout` (runner.py:1020-1021);
- every reply, with the remaining deadline or at least 0.05 s (runner.py:1051-1053).

Attacks tried:
1. **A child that never reads, with a large reply** (the v10 scenario). The send returns after the deadline and the world is TIMEOUT. The reply-path exceptions fall in the outer `except Exception` → PROTOCOL_ERROR (runner.py:1063-1065). HOLDS.
2. **A grandchild keeps the pipe end open, so the kill does not unblock the write** (the declared A3-3 direct-child-only kill). `t.join(10)` expires, `_send_bounded` still returns False, and the main thread continues. The only effect is a leaked daemon thread. HOLDS.
3. **The helper thread raises a non-OSError on the predict path** (for example an AssertionError in the Windows PipeConnection, or a thread-start RuntimeError). This escapes `_predict_one` (the except at runner.py:1022 catches only OSError/ValueError/EOFError) and becomes an abort with `exposed=true`. That is after a deliver record, so it is conservative. Note.

### V11-1 (should-fix; liveness only, not a VOID vector): two parent-side waits are still unbounded
- **(a) The `stop` send.** `predict_all`'s `finally` calls `_stop_worker()` with `kill=False` (runner.py:1081-1085). That path does a plain `_send(self._conn, ["stop"])` (runner.py:966) to a child that has run package code.
  - A package can leave replies unread: it sends `call` messages without reading the `ret`s, then sends `done`. It can do this with only the stub interface plus timing, or trivially with an AST bypass.
  - If it fills the parent-to-child buffer so that each reply still fits but the final `stop` does not, the parent blocks forever after the last prediction is recorded and before `predictions_sealed`.
  - Whether the exact fill is achievable depends on the OS pipe/socket accounting: AF_UNIX `sk_sndbuf` on POSIX, the 8 KiB named-pipe quota on Windows. That part is CANNOT-VERIFY without running it.
- **(b) The receive.** `_recv` → `conn.recv_bytes(64 MiB)` (runner.py:224-225) is called after `poll()` says bytes are ready (runner.py:1028-1036).
  - A child that writes a length header and then only part of the payload (POSIX: a raw `os.write` on the connection fd, which needs an AST bypass; the AST audit is a declared heuristic) blocks `recv_bytes` without a deadline.
  - On Windows message-mode pipes this is harder to stage. CANNOT-VERIFY.
- **Consequence.** The runner hangs after a deliver record. The custodian must kill it; seal-terminal is refused while it lives, which is correct. seal-terminal then appends a custodian abort with `deliver_records ≥ 1`, which is FORFEIT under Addendum J item 2.
  - No leak, no gate opens, and no VOID option.
  - FIREWALL.md:382 ("Every parent-to-child send ... runs with a deadline") is false for `stop`. The procedure "kill a hung runner, then seal-terminal" is not documented.
- **Fix.** Send `stop` through `_send_bounded` (or kill at the end of PREDICT), and run a per-world watchdog that kills the child at the deadline whatever the parent is blocked in.
- **Test gap.** `v11_send_has_deadline` (selftest_protocol.py:1396-1403) uses an in-process Pipe with `_proc=None`, so `_stop_worker` is a no-op. It shows that the join returns, not that killing the child unblocks the write.

## v11-c. The newline repair: HOLDS

runner.py:1227-1245 treats a non-empty final fragment as an unterminated candidate. If it parses and verifies, it is kept and `fix_newline` is set. runner.py:1253-1261 then appends `\n` without truncating anything, because `keep == len(raw)`.

Attacks tried:
1. **A verifying close with its newline stripped.** Kept as close; no custodian abort. Committed self-test: `v11_seal_terminal_keeps_close_without_newline: true`.
2. **A torn final fragment that is invalid JSON.** Truncated; the previous record stays last. Correct.
3. **A blank line, NUL fill or CR in the middle.** seal-terminal breaks at the first non-JSON line and truncates the rest. `verify_receipts` skips blank lines (runner.py:472-474), so after TAMPERING a record that the verifier accepts can still be dropped (N1 carried from v10).
   - The runner never writes blank lines or CR: `newline="\n"` and compact JSON (runner.py:408-409, 434-435).
   - Note.

## v11-d. Lock and liveness: HOLDS

The lock:
- `lock_run` (runner.py:199-214): flock with LOCK_EX|LOCK_NB, or `msvcrt.locking(LK_NBLCK)` on byte 0.
- The runner takes it BEFORE the consumption marker. If it cannot, it refuses with nothing consumed and the key intact, since the key is deleted only after the marker (runner.py:800-812).
- It is released only after a terminal record plus RESULT.json (runner.py:877, 1172). A failed abort or close write keeps it until the process exits.
- seal-terminal takes the same lock first and refuses if it cannot (runner.py:1214-1221).

Attacks tried:
1. **seal-terminal against a live runner.** Refused. Committed: `v11_seal_terminal_refused_while_runner_live: true`.
2. **Runner starts while seal-terminal holds the lock.** The runner refuses before the marker. Correct.
3. **Lock inherited by the predictor child, so a dead runner's lock survives.**
   - Python file handles are non-inheritable.
   - The children use `mp.get_context("spawn")` (runner.py:817). On POSIX, spawn passes only the listed fds; on Windows, CreateProcess runs with bInheritHandles=False.
   - Not inherited. HOLDS (from the CPython sources, not run).
4. **The v10 V10-3 scenarios.** Scenario 1 is a slow runner being custodian-sealed. Scenario 2 is the runner's `repair()` truncating a custodian abort. Both need seal-terminal to run while the runner lives, and the lock now prevents that. HOLDS.

### V11-2 (note): the Windows lock is closed without an unlock
- `_release_lock` and `seal_terminal` call `close()` without `LK_UNLCK` (runner.py:888, 1221).
- LockFile documents that closing with an outstanding lock releases it "depending on available system resources", i.e. asynchronously.
- A seal-terminal right after a runner exits could be refused spuriously. That fails closed, and a retry works.

### V11-3 (note): nothing probes the child's access to run.lock
- A surviving grandchild of the child account (declared A3-3) that can READ `run.lock` could take a shared or exclusive lock after the runner dies. seal-terminal would then be refused until the custodian kills that process.
- The pre-key probe requires the child to be denied READ of the receipts stand-in in the same directory (runner.py:716, 724). With ACL inheritance, run.lock should be denied too.
- CANNOT-VERIFY: this is host ACL state. It fails closed.

## v11-e. Binding to the open record: HOLDS
- custody passes the designation's `run_nonce`, `spec_id` and the committed `package_sha256` (custody.py:245-246).
- runner.py:1248-1252 compares them with record 0's body BEFORE any truncation or write (the write is at runner.py:1253).
- A mismatch → ChainBroken, which custody catches and logs as REFUSED (custody.py:247-248).
- Committed: `v11_seal_terminal_bound_to_open_record: true`.

Attacks tried:
1. Another designation's run directory with the right name. Refused by the nonce check.
2. A non-dict `package`, or a non-dict JSON line. These raise AttributeError/TypeError, which custody's except tuple (custody.py:247) does not catch, so the result is a traceback with no REFUSED log entry. Tampering only. Note (N1).

"Custodian only" is still not enforced: custody's `main` has no account check (custody.py:328-357). The v10 verdict item 3 listed it, but it was not among the closure criteria. Note.

---

## Claims 1-6 (regression; audited code unchanged except runner.py and custody.py)

### 1. Opacity: HOLDS
- **Attack: public fields.** The manifest is unchanged: the blob `db3d442d…` at HEAD equals the blob at 95b31a30d (`rogit ls-tree HEAD`; `rogit log --all --full-history -m --raw`).
- **Attack: the new v11 fields.**
  - The deliver receipt carries `i`, the HMAC `world_tag` and utc, and stays in the receipts on M1 (runner.py:1015).
  - The abort fields are counts and type names.
  - The custody log `SEAL_TERMINAL` event carries hashes and counts (runner.py:1274-1275).
- **V11-4 (note):** the public RESULT_SEAL `n_receipts` (custody.py:276-277) now counts deliver records too. For an aborted run it shows how far the run got, which is public progress information after predictions were frozen. It does not narrow the hidden content beyond the declared timing residual N-1.
- The plaintext length is visible through `ciphertext_bytes` (declared).

### 2. Secrets never in git: HOLDS (repo side)
- `rogit log --all --format= --name-only --diff-filter=A -- prometheus/cosmos/c3_holdout_D2` lists no key, salt, plain or hex file.
- Every commit in any ref that touches `hidden_D2.enc`, `MANIFEST_D2.json`, `draw.py`, `sealbox.py` or `__init__.py` carries the SAME blobs as 95b31a30d. Those commits are 95b31a30d and the merges e51c8dec6, db0bcad58, e5b95744f, 85b198a5b and ebe1307ea, all diffed per parent.
- The key-holder `firewall-check` booleans are CANNOT-VERIFY from the repo. Nestor's published output would settle it.

### 3. Enforced order: HOLDS mechanically; BROKEN on authentication (S1)
- **Attack: ref shadowing.**
  - `rogit show-ref` shows no `refs/tags/main`, no `refs/tags/origin/main`, no `refs/heads/origin/main` and no `refs/replace/*`.
  - The code refuses shadows (protocol.py:302-305) and short refs.
- **Attack: merge rewrites.** The `_added_once` full-history `-m` rule (protocol.py:315-358) is unchanged. The real history carries a single blob per sealed file, as above.
- **Attack: stale audit.** The code_sha256 binding is exact and is checked in both the committed tree and the working tree (protocol.py:533-542). v11 changes runner.py and custody.py, so any audit record must bind the NEW hashes. No `protocol/` records exist at HEAD.
- **S1 (blocks-PASS, known OPEN):**
  - Records count once they are in the allow-list (protocol.py:461-473).
  - That list is fed from comms messages whose `sender` field is client-supplied (FIREWALL.md:156-158).
  - main is unprotected.
  - Unchanged.

### 4. Controlled reveal: HOLDS
- The code is unchanged except seal-terminal: release at custody.py:188-225, result-seal at custody.py:253-280, reveal at custody.py:283-325.
- **Attack: have seal-terminal turn a CLOSED run into an ABORT.** Blocked by the lock (v11-d) and the newline repair (v11-c).
- **Attack: seal a foreign run.** Blocked by the binding (v11-e).

### 5. Predictor isolation: HOLDS
- The child is spawned, pickle-free and probed before package code on every start. This is unchanged (runner.py:347-360, 816-839).

### V11-5 (should-fix, carried from the v10 replica-2 report as its V10-1): a failed replacement-child start gets a false error_type
The sequence:
1. `_spawn_probe` assigns `self._proc` before `start()` and `_child_world` after it (runner.py:819-822).
2. If `start()` raises, `predict_all`'s `finally` calls `_stop_worker()` → `self._proc.join(10)` on an unstarted Process → AssertionError (runner.py:965-967). The except tuple at runner.py:968 does not catch it, and neither does the one at runner.py:1084.
3. The abort then records `error_type: AssertionError`, a stale `child_world` and `child_exitcode: null`. The previous child's real exit code is lost.

The VOID/FORFEIT reading rests on the deliver records, which are truthful, so this is not a VOID vector. But the labels are untruthful.

Fix: set `_proc` only after a successful `start()`, or catch AssertionError in the cleanup.

### 6. Draw integrity: HOLDS (repo-checkable part)
- The blobs of `draw.py`, `sealbox.py`, `__init__.py`, `hidden_D2.enc` and `MANIFEST_D2.json` at HEAD equal those of 95b31a30d. The mapping of those blobs to the manifest's sha256 values is not re-hashed here: CANNOT-VERIFY with my tools; earlier replicas recorded it.
- The CSPRNG nonce and single-draw provenance are custodian statements (declared).

---

## The seven mandatory classes (v11 delta)
1. **Unbound code with secrets:** v11 adds `threading` at the top of runner.py, plus `msvcrt`/`fcntl` imported lazily. All are stdlib, covered by the F-3P / stdlib residual. The entry guard and the closure check are unchanged. No new unbound repository module.
2. **Same-account readability:** unchanged and declared. `run.lock` holds no secret.
3. **Static-audit bypass:** unchanged heuristic. V11-1(b) needs a bypass; V11-1(a) arguably does not.
4. **Git ref ambiguity / history simplification:** checked on the real refs; see claim 3. HOLDS.
5. **Unauthenticated or rewritable records:**
   - S1 is OPEN.
   - Receipts are an unkeyed chain that the runner and custodian accounts can write (trusted-operator scope).
   - The v10 seal-terminal race is closed by the lock.
6. **Public fields that narrow hidden content:** plaintext length (declared); timing N-1 (declared); `n_receipts` progress (V11-4, note).
7. **Spoofable host/identity checks:**
   - The comms sender (S1).
   - `gethostname` is same-account state (declared).
   - seal-terminal has no account check (note).

## Declared residual risks: assessment
- **The gates are no boundary against the key holder:** acceptable as declared.
- **The predictor is Python and the AST audit is a heuristic:** acceptable. The separate child account and V7-E (no launcher code yet; it will need its own audit) remain preconditions for ANY release; the preflight fails closed today.
- **Single-draw provenance:** acceptable as declared.
- **The System interface exposes physics:** acceptable by contract.
- **Crash-after-release, child-to-parent signals, disk exhaustion, direct-child-only kill:** acceptable. With deliver receipts and Addendum J, none of them yields a VOID after delivery.
- **Missing from the list:**
  - (a) The runner can still be hung after exposure through the unbounded `stop` send or receive (V11-1). The recovery procedure (kill the runner, then seal-terminal) should be documented.
  - (b) The Windows lock is released asynchronously (V11-2).

## Verdict
- No new blocks-PASS finding in v11. The v10 must-close items (deliver evidence, seal-terminal newline, lock and binding) are closed in code.
- Should-fix: V11-1 and V11-5.
- Notes: V11-2, V11-3, V11-4, N1, "custodian only", and N6 (a stale `.claim` is detected only after the key read: runner.py:710-712 vs 403-405; nothing is consumed).
- Blocks-PASS: **S1** (#925) together with branch protection, both OPEN and the operator's decisions.

**OVERALL: FAIL** (solely on S1)
