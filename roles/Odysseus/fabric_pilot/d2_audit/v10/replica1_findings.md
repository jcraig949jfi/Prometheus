# Holdout D2 firewall — independent adversarial re-audit v10

- Auditor: an Odysseus replica (task tsk-6a1fef0c94fc, attempt att-ab0acb81e35c). This is a disposable worker with no seat identity.
- Audited commit: `a823b596c48262b7607f8738adf5eecdf3d1a8fd`. It is a merge of origin/main into `nestor/d2v10-2026-09-29`. The v10 code is commit `784d55b63`.
- Method: I read the code and the history only (`rogit`, Read, Grep). **I did not run the self-tests or any code.** Every boolean below that comes from `SELFTEST_PROTOCOL.json` is the committed value, not one I reproduced.
- Scope: FIREWALL.md section "v10" first, because the brief asks for it. Claims 1–6 are then re-checked for regressions.
  - v10 changed only `runner.py`, `custody.py`, `selftest_protocol.py`, `SELFTEST_PROTOCOL.json`, FIREWALL.md and AUDIT_BRIEF.md (`rogit show --stat 784d55b63`).
- Earlier Odysseus verdicts (v1–v9) exist in the repo. I did not use their findings as inputs. Where my result agrees with a known-open item (S1), I say so.

## Summary

| # | Claim | Verdict |
|---|---|---|
| 1 | Opacity | HOLDS (plaintext length declared) |
| 2 | Secrets never in git | HOLDS for what the repo can show. The key-holder side is CANNOT-VERIFY-FROM-REPO |
| 3 | Enforced order | HOLDS mechanically. **BROKEN on authentication: S1, known OPEN (#925), blocks-PASS** |
| 4 | Controlled reveal | HOLDS (notes N8, N10) |
| 5 | Predictor isolation / terminal outcome | HOLDS for isolation. The per-world deadline can be bypassed (V10-1, should-fix) |
| 6 | Draw integrity | HOLDS for the repo-checkable part. Single-draw provenance is declared |
| v10-a | Every attribution label is truthful | HOLDS with defects: V10-2 (should-fix), N3, N4, N5, N9 (notes) |
| v10-b | seal-terminal seals every spent, unterminated run and never removes or forges a verifying record | **BROKEN (should-fix):** V10-3 (concurrent live run), V10-4 (a verifying final record without its newline is truncated) |

No new blocks-PASS finding. The only blocks-PASS finding is S1, which is known and declared OPEN.

---

## v10-a. Attribution labels (runner.py `abort`, `_predict_one`, `_spawn_probe`, `_stop_worker`)

Labels written at runner.py:840-846: `phase`, `error_type`, `n_predictions_recorded`, `exposed`, `current_world`, `in_predictor_io`, `child_exitcode`, `child_world`, `disk_chain_matched`.

The attacks I tried are listed below.

### A. Pre-exposure start failure
- runner.py:951-954 sets `_cur_world=i` and `_in_predictor_io=bool(_exposed)` before the (re)start.
- `_exposed` becomes True only after the first predict send returns (runner.py:955-961).
- A first-start failure therefore gives `exposed=false, in_predictor_io=false, current_world=0`. That is truthful.

### B. Restart failure after exposure
- The flag is sticky (it is never reset), so every later abort carries `exposed=true`. That is truthful.

### C. Package code runs before exposure
- After `go`, the package module is executed at import time (runner.py:335-341), before any world is sent.
- So "pre-exposure" does not mean "no package code was live". The package cannot learn anything about a world before the predict send (the child receives only `probe`, `go` and then `predict`), so `exposed=false` is still truthful.
- But `in_predictor_io=false` on a pre-exposure abort does not show that the package was inactive. It is covered by the declared A3-3 statement. **Note only.**

### D. Async interrupt between send and flag (N9)
- `_send` (runner.py:198-199) is a single `send_bytes` of a small message, so the parent does not block on it.
- A KeyboardInterrupt landing after the write completes but before runner.py:960 would give `exposed=false` although world 0 was delivered.
- The window is a few bytecodes, and the child cannot time it (it must first read the message and then signal). **Note.**
- The converse also exists: `exposed=true` can be recorded when the child died during import and never read the message. That direction is conservative.

### E. `child_world` / `child_exitcode` pairing (A3-2) — N3
- `_spawn_probe` assigns `self._proc = ctx.Process(...)` (runner.py:793) BEFORE `start()` (794). It sets `_child_world` only after `start()` returns (796).
- Scenario: world 5's child is killed on TIMEOUT, so `_last_exit={"world":5,"exitcode":-9}` and `_proc=None` (runner.py:915-916). The restart for world 6 then fails inside `Process.start()`, for example with a CreateProcess/spawn OSError. That exception is not inside any guard in `_predict_one` (runner.py:953-954), so the run aborts.
- `abort` sees `proc is not None` and reports `child_exitcode = proc.exitcode` = None (the child never started) together with `child_world = self._child_world` = 5 (stale).
- The real exit code of world 5's child (-9) is lost, and the null is paired with the wrong world.
- The selftest `v10_restart_after_exposure_labelled` (selftest_protocol.py:1294-1304) replaces `_start_worker` entirely, so it never exercises this path.
- **Note.** Fix: set `_child_world` and clear `_proc` before `start()`, or wrap `start()` so that failure resets `_proc=None`.

### F. Stale `current_world` at the top of `_predict_one` — N4
- runner.py:946-947 build `medium.ReactiveChannel(self._worlds[i])` BEFORE the labels are updated at 951-952.
- A failure there (for example MemoryError) is labelled `current_world=i-1, in_predictor_io=false` (for i=0: `None`).
- It should be world i, or "between worlds". **Note.**

### G. `disk_chain_matched` — N5
- The value is `repair()`'s return (runner.py:835, 430-444). That is the state AFTER truncation.
- A torn tail that was repaired reports `true`, exactly like an intact file, so the label cannot show that a repair happened.
- **Note.** Also record the number of bytes truncated.

### H. The custodian seal-terminal abort
- All labels are null and `error_type` is `SEALED_BY_CUSTODIAN` (runner.py:1180-1183). That is truthful: it asserts no cause.
- **But see V10-2:** the null `exposed` cannot be recovered from any other record.

### V10-2 (should-fix): exposure is recorded only in the runner's own abort, never as a receipt
- Addendum H (roles/Harmonia/rulings/RECORD_D2_GOVERNING_AUDIT_AND_SEAL_GATE_2026-09-29.md:279-284) makes VOID vs FORFEIT depend on whether the first world was delivered.
- No receipt marks that event. The chain shows it only indirectly, through a `prediction` record for world 0.
- **Scenario:**
  1. The package receives world 0 (V, k and oracle access to its physics for up to `predict_timeout`).
  2. It makes the runner die or hang with no runner abort. It can do this with V10-1 (hang, then the operator kills the process), or with the DECLARED child-to-parent signal residual (FIREWALL.md:332; for example a console CTRL_BREAK, for which Python keeps the default terminate action — only SIGINT is ignored, and only inside `abort`, runner.py:828-829).
  3. The custodian runs `seal-terminal` and gets `n_predictions_recorded=0, exposed=null` (runner.py:1180-1183).
  4. That chain is byte-for-byte the same shape as an honest pre-exposure crash, for example an interrupt after the `os.replace` at runner.py:395, which also leaves `open` only.
- **Impact:**
  - Integrity holds only if Harmonia reads `exposed=null` as exposed. Addendum F item 2's burden rule (lines ~231-236) supports that reading, but it is not stated for seal-terminal aborts.
  - The same gap makes an honest pre-exposure crash FORFEIT.
- **Fix:** append a `deliver` (exposure) receipt for world 0 BEFORE the first predict send. Any chain without it is then provably pre-exposure, and every chain with it is provably post-exposure.
- Severity: should-fix. Ask Harmonia to rule on `exposed=null` explicitly.

---

## v10-b. seal-terminal (runner.py:1143-1188; custody.py:236-249)

The attacks I tried are listed below.

### A. Torn tail, no terminal record
- The tail is truncated to the longest verifying prefix, a custodian abort is appended and RESULT.json is rebuilt. It works as designed.
- Committed self-test: `v10_seal_terminal_torn_unterminated_run: true`.

### B. CLOSED run, RESULT.json lost
- `result_from_records` is deterministic (runner.py:1112-1135), so the rebuild is byte-identical. HOLDS.

### C. Forge a verifying record
- The only record seal-terminal writes is a custodian `abort` with a fixed body. It never writes `close`, `prediction` or `certify`. HOLDS.
- The receipt chain itself is unkeyed sha256 (runner.py:355-356). Anyone who can write the run directory can build a whole verifying chain. That means the runner account or the custodian. The child cannot: the isolation probe denies it, runner.py:639-640 and 697-706. This is trusted-operator scope, not Cosmos's, and v10 does not change it.

### V10-3 (should-fix): seal-terminal has no liveness check against a running runner
Records can be removed in both directions:
- `custody.seal_terminal` takes no lock and checks nothing about the runner process (custody.py:237-249).
- `runner.seal_terminal` appends straight to the file (runner.py:1176-1184).
- The live runner appends in `"a"` mode (runner.py:415). Its `repair()` truncates anything the file holds beyond its in-memory chain whenever the file starts with that chain (runner.py:437-438).

**Scenario 1:** a slow certify (certify has no timeout) or a V10-1 hang looks like a dead run.
1. The custodian runs seal-terminal, and the file becomes `[.., X, abort_c]`.
2. The custodian result-seals head `abort_c`.
3. The runner resumes and `close()` appends `close` (prev = X). `close()` does not call `_gate`.
4. RESULT.json is overwritten with CLOSED.
5. The chain now breaks at `close`, and reveal refuses (RESULT hash mismatch).
6. Running seal-terminal again truncates the runner's genuine `close`, a record that verifies in the runner's chain.
7. A genuinely CLOSED run ends as a custodian ABORTED, which is FORFEIT under Addendum H.

**Scenario 2:** the runner aborts before appending anything.
1. `repair()` finds disk = memory + `abort_c`.
2. `startswith` is true, so it truncates the custodian's `abort_c`.

**Assessment:**
- This needs a custodian action. Cosmos cannot trigger seal-terminal.
- But nothing prevents the action, and v10's claim "never removes a verifying record" is stated absolutely.
- **Fix:** the runner holds an OS-level exclusive lock for its whole lifetime (`msvcrt.locking` / `fcntl.flock` on the claim file), and seal-terminal must acquire that lock first.

### V10-4 (should-fix): a complete, verifying final record without its trailing newline is truncated
- runner.py:1153 iterates `raw.split(b"\n")[:-1]`, so the last line is dropped when it has no `\n`.
- `verify_receipts` (runner.py:452-455) reads with `for line in f` and ACCEPTS such a line.
- **Scenario:**
  1. Power loss persists `close`'s JSON but not its final `\n`. With a 4 KiB sector write this happens when `\n` is the first byte of the next sector.
  2. RESULT.json was not written.
  3. seal-terminal is the only tool that rebuilds RESULT.json. It truncates the verifying `close` and appends a custodian abort, turning CLOSED into ABORTED.
- The probability is low, and it is inside the declared crash residual. But it breaks the stated invariant, and the fix is trivial: accept a final verifying line without a newline and append `\n`.

### Divergences and notes
- **N1:**
  - seal-terminal and `verify_receipts` disagree on blank or whitespace lines: `verify_receipts` skips them (runner.py:454), seal-terminal breaks and truncates everything after them.
  - A non-dict JSON line raises AttributeError, and a body that `record_hash` cannot hash raises TypeError. custody catches neither (custody.py:246), so the result is a traceback with no REFUSED entry in the custody log.
  - These cases need tampering. Note.
- **N2:**
  - The `custody.seal_terminal` docstring says "open record carrying the designation nonce", but the code checks only `run_dir.name` (custody.py:243). It does not check the open record's `run_nonce` or `spec_id`, and does not require the directory to be under `RUN_OUT_ROOT`.
  - result-seal checks nonce, spec_id and package later (custody.py:262-267), so no gate opens wrongly.
  - The custodian could still truncate or append to any `run_<nonce>/receipts.jsonl`. Note.
- **Coverage:** can every spent, unterminated run be sealed?
  - Every spent run has an atomically created, fsynced open record (runner.py:387-395), so the longest-prefix rule always finds record 0. HOLDS, except in one case.
  - **N7 (the exception):** the directory is not fsynced after `os.replace` (runner.py:395). On power loss the rename can be lost while the later key-copy unlink (runner.py:785-786) persists. The result is a consumed release with no marker, which seal-terminal refuses ("no verifying open record").
  - Addendum F item 1 reads this as VOID (pre-exposure, infrastructure), so it is a note, not a gap.
- **N6:**
  - A stale `receipts.jsonl.claim` left by a crash between claim creation and the rename (runner.py:384-395) is detected only in `open()`, after the key is read (runner.py:763, 782). `prepare()` checks only `receipts.jsonl` (runner.py:691-693).
  - Nothing is consumed: the key copy stays intact. But the run stays blocked until the custodian removes the claim by hand, and that step is not documented.
  - Checking the claim in `prepare()` as well would fix it. Note.
- **Cannot verify from the repo:** whether the custodian account can write the run directory. The runner account creates it under `RUN_OUT_ROOT` (protocol.py:58), and the ACL is host state.

---

## V10-1 (should-fix): the per-world deadline does not bound the parent's reply send, so a package can hang the runner indefinitely after exposure
- `_predict_one` enforces the deadline only through `poll` (runner.py:962-972).
- A `call` is answered with a blocking `_send(self._conn, reply)` (runner.py:986-989), which is `conn.send_bytes` (runner.py:198-199).
- **Scenario:**
  1. The package calls `init(200000)` (allowed: `MAX_E_PER_CALL = 200_000`, runner.py:89 and 921). The reply is megabytes of base64 JSON.
  2. The package then never reads again, for example with `while True: pass`.
  3. The Windows multiprocessing `PipeConnection` write waits INFINITE once the buffer (8 KiB) is full. On POSIX the socketpair `write` blocks.
  4. No TIMEOUT fires, no receipt is written, and the child is never killed.
- **Recovery:**
  - Ctrl-C in the runner's console most likely interrupts the wait. Whether that becomes a per-world PROTOCOL_ERROR (an `InterruptedError` caught at runner.py:999) or a KeyboardInterrupt abort is CANNOT-VERIFY without running it on M1.
  - Killing the runner leaves an unterminated run. seal-terminal then records null labels, which leads to V10-2.
  - The procedure is not documented in FIREWALL.md.
- **Integrity:** with Addendum F's burden rule this is FORFEIT, not VOID. So it is should-fix, not blocks-PASS.
- **Fix:** enforce the deadline on sends. Use a writer thread with a timeout, or a watchdog that kills the child at the deadline, so that a blocked write fails with BrokenPipe and becomes that world's PREDICTOR_CRASH.

---

## Claim-by-claim (regression check)

### 1. Opacity — HOLDS
Attacks tried:
- Look for secret-derived fields in the manifest.
- Look for leaks in labels and error text.
- Look at sizes.

Evidence:
- The manifest (MANIFEST_D2.json) carries only public parameters, the IV, hashes and the commitment. `ciphertext_bytes: 17227` reveals the plaintext length; this is declared (FIREWALL.md:149, 220).
- My check: `sha256(hidden_D2.enc)=f75ba333…fc9f` and `sha256(MANIFEST_D2.json)=78874e9d…71fe`, both equal to the brief.
- Error replies to the child carry the type name only (runner.py:987-988). The abort carries type names only (runner.py:841).
- v10 adds no new public field. The custody log `SEAL_TERMINAL` event (custody.py:248) carries hashes and counts only.
- `SELFTEST_PROTOCOL.json` diff: booleans only.

### 2. Secrets never in git — HOLDS (repo side); key-holder side CANNOT-VERIFY
- `rogit log --all --stat -- prometheus/cosmos/c3_holdout_D2`: no `*.key*`, `*.salt*`, `*.plain*` or `.hex` path has ever existed.
- The only commit touching `hidden_D2.enc`, `MANIFEST_D2.json`, `draw.py`, `sealbox.py` and `__init__.py` is 95b31a30d.
- `firewall_check` results on M1 cannot be established from the repo. Nestor's published booleans would settle it.

### 3. Enforced order — HOLDS mechanically; BROKEN on authentication (S1)
- v10 did not change protocol.py or entry.py. `check_gates` resolves the ref once (protocol.py:488-489).
- The following are unchanged and hold as read:
  - once-added records (protocol.py:334-358);
  - allow-list-filtered governing audit (513-532);
  - stale-code binding (533-547).
- v10 makes custody `_test_decrypt` use the resolved commit (custody.py:171-175, 204). HOLDS.
- **N8:** `reveal()` still re-reads the manifest and ciphertext by ref name (custody.py:312-313) after the gates. That affects only `verify_reveal` inputs. Note.
- **S1 (blocks-PASS, known OPEN #925):**
  - Records are authenticated only by the custodian allow-list (protocol.py:461-473).
  - Entries are added from comms messages whose `sender` field is client-supplied (FIREWALL.md:156-158).
  - main is unprotected.
  - So anyone who can push to main and post on comms can produce "allow-listed" audit, commitment or designation records.
  - Unchanged; the brief declares it open.

### 4. Controlled reveal — HOLDS
- release: gates, once (log plus git), preflight, test-decrypt at the resolved commit, restricted destination (custody.py:188-225).
- reveal: RESULT_SEAL gate, chain re-verified, head/package/spec/nonce/result hash checked, once (custody.py:282-324).
- v10's widened `except` (ValueError) frees the lock on a malformed key (custody.py:211). Other exception types, for example a KeyboardInterrupt mid-write, leave the lock held and fail closed. Note.
- **N10:** result-seal checks only `RESULT.json.chain_head == head` (custody.py:268-270). Since v10 RESULT is a pure function of the receipts, result-seal could require `RESULT.json == result_from_records(recs)` byte for byte. Defence in depth; note.

### 5. Predictor isolation — HOLDS (isolation); V10-1 (deadline)
- The child is separate, spawned, pickle-free (runner.py:170-206, `allow_pickle=False`), and probed before the key and on every restart (runner.py:790-813, 897-901).
- The v10 poll guard (runner.py:965-969) holds.
- The blocking reply send is V10-1.

### 6. Draw integrity — HOLDS (repo-checkable part)
- sha256 of `__init__.py` `d38d3b0c…63c8`, `draw.py` `800e0b5d…687b` and `sealbox.py` `dec9b915…ed2` on this commit equals `d2_src_sha256_at_draw`.
- `c3_holdout_D/medium.py` hashes to `09559e69…cde4` = `family_src_sha256`.
- I used raw sha256; the files are LF.
- The CSPRNG nonce and single-draw provenance are custodian statements (declared).

---

## The seven mandatory classes (v10 delta)
1. **Unbound code with secrets:**
   - `custody.seal_terminal` imports `runner` (custody.py:239). runner is in AUDITED_FILES and is served by the entry guard.
   - v10 adds `import signal, threading` (stdlib) inside `abort`. F-3P covers stdlib/site-packages (declared).
   - No new unbound path found.
2. **Same-account readability:** unchanged; declared (OS account is the boundary).
3. **Static-audit bypass:** unchanged heuristic. V10-1 needs no forbidden construct: it uses only the System interface plus a busy loop.
4. **Git ref ambiguity / history simplification:** unchanged code (protocol.py:301-358); holds as read.
5. **Unauthenticated / rewritable records:**
   - S1 (open).
   - Receipts are an unkeyed hash chain, writable by the runner and custodian accounts (trusted-operator scope).
   - seal-terminal/runner write races (V10-3).
6. **Public fields that narrow hidden content:**
   - plaintext length (declared);
   - timing N-1 (declared);
   - no new field.
7. **Spoofable host/identity checks:**
   - The comms sender (S1).
   - Host from `socket.gethostname()`: same-account state, declared.

## Declared residual risks — assessment
- **Key holder is not bounded by gates:** acceptable as declared.
- **Predictor is Python as an OS account; AST audit is a heuristic:** acceptable. The separate child account (host capability) and V7-E (no code yet to start the child under it; it will need its own audit) remain preconditions for ANY release. Today every preflight fails closed (ChildNotIsolated).
- **Single-draw provenance:** acceptable as declared.
- **System interface exposes physics:** acceptable by contract.
- **Crash-after-release, child-signals-parent, disk exhaustion, direct-child-only kill (A3-3):** acceptable as declared, WITH the gap in V10-2. These residuals are exactly the paths to a null-exposure custodian abort.

**Missing from the list:**
- (a) The package can make the runner hang without bound after exposure (V10-1). This is not the same as "pressure": no timeout applies.
- (b) seal-terminal must never run on a live run, and nothing enforces that (V10-3).
- (c) Records written by the custodian's seal-terminal carry no exposure evidence (V10-2).

## Verdict
- No new blocks-PASS finding in v10.
- Should-fix: V10-1, V10-2, V10-3, V10-4.
- Notes: N1–N10.
- S1 (#925) remains OPEN and blocks PASS, together with branch protection (the operator's decision).

**OVERALL: FAIL** (solely on S1).
