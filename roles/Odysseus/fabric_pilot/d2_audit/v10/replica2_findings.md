# Holdout D2 firewall: adversarial re-audit v10

- **Task / attempt:** tsk-c2d0f2c43947 / att-650d5ac25361.
- **Skill:** audit.security.adversarial v1.
- **Audited commit:** a823b596c48262b7607f8738adf5eecdf3d1a8fd. The v10 code is 784d55b63; the D2 package differs from the v9-audited 2aa834ab1 only in `runner.py`, `custody.py`, `selftest_protocol.py`, `SELFTEST_PROTOCOL.json`, `FIREWALL.md` and `AUDIT_BRIEF.md` (`git diff --stat 2aa834ab1 a823b596c`).
- **Scope:** the firewall layer only. Nothing about the law, its predictions or the science was examined.

**Method and limits.** The audit was static reading plus read-only git (`rogit`). I could NOT execute anything: Bash other than `rogit` was denied in this worker, so I computed no sha256 and ran no self-test.
- Every runtime statement below comes from code reading, or it is marked CANNOT-VERIFY.
- The committed `SELFTEST_PROTOCOL.json` reports `selftest_pass: true`, and none of its checks is false (`SELFTEST_PROTOCOL.json:208-214`). That file is an artifact of the author's run, not my own run.

---

## Part A: the v10 scope (labels and seal-terminal)

### A1. "Every attribution label is truthful"

**What holds**
- `exposed` is set only after the first `predict` send succeeds (`runner.py:955-961`).
- Before any delivery, a (re)start failure is labelled `in_predictor_io=false` (`runner.py:951-954`).
- `_cur_world` is cleared after PREDICT on the normal path (`runner.py:1022`).
- The poll now sits inside the per-world guard (`runner.py:965-969`).
- The exit code is tied to the child that produced it (`runner.py:796`, `915`, `844-845`).

**Attacks tried**
1. **First child start fails at world 0.** `_start_worker` raises PredictorChildFailed or ChildNotIsolated, and nothing catches it per world. `predict_all`'s `finally` stops the (already stopped) worker, and `abort` records `exposed=false`, `in_predictor_io=false`, `current_world=0`. **Truthful.**
2. **Package import-time crash, then send.** `_worker_main` runs the package's module code after `go` and before any world (`runner.py:335-341`). If the child dies at import, the `predict` send can still succeed into the pipe buffer. `exposed` then becomes true although `predict()` never ran.
   - This is conservative: it pushes toward FORFEIT, not VOID.
   - The message does carry world data (V, k, seed; `runner.py:956`). "Delivered to the pipe" is therefore a defensible reading of Addendum H.
   - Severity: **note**.
3. **`Process.start()` itself fails on a restart after exposure** (EMFILE, ENOMEM or a CreateProcess failure, e.g. from process-table exhaustion by a previous child's orphans, A3-3). The sequence:
   - `runner.py:793-794` assigns `self._proc` to the new, unstarted Process. Then `start()` raises before line 796, so `_child_world` and `_last_exit` still describe the PREVIOUS child.
   - The exception unwinds to `predict_all`'s `finally` (`runner.py:1017-1021`), which calls `_stop_worker()` with `kill=False`.
   - `_send(self._conn, ["stop"])` succeeds, because the new pipe's child end is still referenced by the in-flight traceback frame.
   - `self._proc.join(10)` on an unstarted Process raises `AssertionError("can only join a started process")` (CPython `multiprocessing/process.py`; asserts are live under `-I -B`).
   - AssertionError is not in `(OSError, ValueError, EOFError)`, so it REPLACES the original exception.
   - `abort()` then records `error_type: "AssertionError"`, `child_exitcode: null` and `child_world` = the PREVIOUS child's world (`runner.py:838-846`, via `_stop_worker` at `runner.py:915`).
   - Two labels are therefore untruthful: the error type, and which child the exit evidence belongs to.
   - Adjudication impact is nil under Addendum H, since every post-exposure abort is FORFEIT. At world 0 the stale value is the preflight's `None`, so the exposure labels stay right.
   - **Finding V10-1, should-fix.** Fix: set `_child_world`/`_last_exit` before `start()`; in `_stop_worker`, skip `join` when `_popen is None`; catch BaseException in the `finally` or chain it.
4. **Per-world TIMEOUT from a wall-clock step.** `deadline` and `left` use `datetime.now().timestamp()` (`runner.py:962-964`), which is not monotonic. An NTP or manual clock step forward can end a world as `TIMEOUT` (a package-attributable status) with no predictor fault. A step backward extends the cap.
   - Pre-existing, but it is a label-truthfulness defect.
   - **V10-5, note.** Use `time.monotonic()`.
5. **Ctrl-C windows around the terminal write.**
   - Between `receipts.append("close")` and `self.phase = "CLOSED"` (`runner.py:1104-1105`): `abort()` sees phase SEALED and appends an `abort` AFTER a verifying `close`. `result_from_records` then reports ABORTED for a closed run (`runner.py:1131-1133`).
   - Between the fsync and `self.records.append` (`runner.py:418-424`): `abort()`'s `repair()` truncates the on-disk `close`, because disk startswith memory (`runner.py:437-440`).
   - Both windows are a few bytecodes long. A Ctrl-C is needed: from the operator, or from the child's or orphans' console control events, a residual already declared in v8.
   - **V10-6, note.**
6. **`SIGBREAK`.** The v10 SIGINT-ignore (`runner.py:825-829`) does not cover CTRL_BREAK_EVENT. That event's default action terminates the process during `abort()`, which leaves an unterminated chain. seal-terminal now recovers this, and the v8 console-event residual covers it. **Note.**
7. **`disk_chain_matched`.** It is false on ANY OSError inside `repair()` (`runner.py:443-444`), for example a Windows sharing violation from an AV scanner. In that case "false" means "could not confirm", not "did not match". **V10-7, note** (document the meaning).

**Verdict A1: HOLDS for the exposure labels (`exposed`, `in_predictor_io`, `current_world`).** The should-fix V10-1 covers `error_type`/`child_world` when a spawn fails; notes V10-5/6/7.

### A2. "seal-terminal can seal every spent, unterminated run and never removes or forges a verifying record"

**What holds**
- Spent = `receipts.jsonl` exists. It is created only by an atomic temp-file-plus-rename of a fully serialised open record (`runner.py:376-405`), after `prepare()` round-trips the body (`runner.py:729-733`). So every spent run has a verifying record 0, and `seal_terminal` can always seal it (`runner.py:1143-1188`).
- A CLOSED run with a lost RESULT.json is rebuilt from `result_from_records` (`runner.py:1112-1134`). The v10 self-test asserts byte-identity (`selftest_protocol.py:1320-1327`).
- The torn-tail case is tested (`selftest_protocol.py:1305-1319`).

**Attacks tried**
1. **A complete final record with no trailing newline** (a crash, or ENOSPC after all bytes but the `\n`, with `repair()` failing or never reached).
   - `verify_receipts` accepts it: it iterates lines, and the last line is parsed without a newline (`runner.py:452-455`). custody `result-seal` would therefore seal it, including when it is a terminal `close` (`custody.py:257-261`).
   - `seal_terminal` parses only `raw.split(b"\n")[:-1]` (`runner.py:1164`), so it TRUNCATES that record and, if it was the terminal record, appends a custodian `abort`.
   - Likewise, a whitespace-only line is skipped by `verify_receipts` (`runner.py:454`) but ends `seal_terminal`'s prefix (`runner.py:1166-1169`). Every verifying record after it would be truncated.
   - So seal-terminal CAN remove a record that the project's own verifier treats as verifying. The custodian's choice of tool (result-seal vs seal-terminal) then picks CLOSED vs ABORTED for such a file.
   - Rare, but it contradicts the stated invariant.
   - **Finding V10-2, should-fix.** Use `verify_receipts`' line semantics: accept a final unterminated line that parses and verifies, then append the missing `\n`.
2. **Directory binding.**
   - custody checks only `run_dir.name == "run_" + run_nonce` (`custody.py:243-244`). The docstring claims "open record carrying the designation nonce" (`custody.py:238`), but the open record's `run_nonce`, `spec_id` and package hash are NOT checked, and the path is not required to lie under `RUN_OUT_ROOT`.
   - Any directory named `run_<nonce>` anywhere is truncated or appended to, and gets a RESULT.json.
   - result-seal re-checks the open record (`custody.py:262-267`), so this cannot produce a sealable run on the wrong designation. The damage is a verifying custodian abort appended to an arbitrary file.
   - **V10-3a, should-fix.**
3. **Liveness and mutual exclusion.**
   - seal-terminal takes no lock (compare `_lock`, `custody.py:138-149`) and has no liveness test. `receipts.jsonl.claim` is created O_EXCL but is never removed on success (`runner.py:384-405`), so it cannot serve as a "run in progress" marker either.
   - Run on a live run, seal-terminal appends a custodian `abort`. The live runner's next append then forks the chain: its `seq` n duplicates the abort's.
   - Its `_gate` refuses (`runner.py:1043-1047`), its `abort()`/`repair()` cannot re-sync (`runner.py:437`), and a later seal-terminal truncates the runner's own records, including its attribution-bearing abort.
   - This needs the custodian, the key holder, who can kill the run anyway. The result: the protocol's own tool can erase runner-written records with no refusal.
   - **V10-3b, should-fix.** Refuse when the run is live (e.g. a runner-held O_EXCL `running` lock removed at terminal), or declare it.
4. **Who runs it.**
   - FIREWALL.md v10 says "custodian only" (FIREWALL.md:364). No OS-account check exists (`custody.py:237-249`; `entry.py` has no per-target account rule, `entry.py:333-348`).
   - The designated runner account can run `entry.py custody seal-terminal` on its own run directory. The receipts are modified (`runner.seal_terminal`) BEFORE the custody-log append (`custody.py:245-248`), which that account probably cannot write.
   - The resulting record is labelled `SEALED_BY_CUSTODIAN` (`runner.py:1180`) although no custodian acted.
   - The runner account can already rewrite its own unkeyed chain, so this is a label-authenticity point, not a new capability.
   - **V10-3c, should-fix.** Require `same_account(os_account(), CUSTODIAN_ACCOUNT)`.
5. **Forging.** The appended abort is the custodian's own record with null labels (`runner.py:1179-1183`). It does not forge a runner record. The chain is unkeyed (`runner.py:355-356`), so any writer can forge verifying records; that is outside seal-terminal. **HOLDS.**
6. **Tampered or odd input.**
   - A JSON line that is a list gives an AttributeError on `r.get` (`runner.py:1170`).
   - A forged `close` without `predictions_sealed` gives StopIteration (`runner.py:1122`).
   - Neither is in custody's `except` (`custody.py:246`), so there is no REFUSED log entry and the CLI dies with a traceback.
   - **V10-8, note.**
7. **Stale claim after a hard crash.** A stale claim left between claim creation and the rename (`runner.py:385-395`) makes every later `open()` fail with a bare FileExistsError after the key is read. That run consumed nothing: the key is intact and no receipts exist. But no tool or message tells the custodian to remove the claim. **V10-4, note.**

**Verdict A2: BROKEN as stated ("never remove a verifying record"), should-fix (V10-2).** "Can seal every spent unterminated run" HOLDS. Directory, account and liveness binding: should-fix (V10-3a/b/c).

---

## Part B: the six brief claims

### Claim 1: Opacity. HOLDS (declared length note)
- **Attack: brute-force the commitment.** `commitment = sha256(salt||plaintext)` with a 32-byte CSPRNG salt (`sealbox.py:52-53`, `64-67`; `draw.py:104`). The salt never appears in the manifest (`MANIFEST_D2.json` as shown at 95b31a30d). Lattice enumeration cannot confirm a candidate. **Holds.**
- **Attack: decrypt or forge the ciphertext.** AES-256-GCM, random 32-byte key and 12-byte IV (`sealbox.py:48-80`). The AAD binds the family hash (`sealbox.py:60-61`); decrypt checks the tag (`runner.py:765-768`). **Holds.**
- **Attack: the manifest fields.** No world, knob, seed or nonce appears. The IV is public by design. `ciphertext_bytes: 17227` exposes the plaintext length: declared (FIREWALL.md v2 residual), not shape-revealing beyond the fixed count of 128. **Note (declared).**
- **Attack: the receipt and result formats.**
  - Predictions carry `world_tag = HMAC(key, world||seed)` (`runner.py:775-776`), never the knobs.
  - `_summ` strips `system` (`runner.py:604-609`).
  - Error replies to the child carry the type name only (`runner.py:986-988`).
  - The public RESULT_SEAL carries hashes and counts (`custody.py:273-276`).
  - RESULT.json with per-world classes stays on M1 until the reveal.
  - **Holds.**
- **Attack: the child's usage and timing.** Declared (N-1 timing; the System interface reveals physics by design).
- **SELFTEST_\*.json:** booleans only (`SELFTEST_PROTOCOL.json`; `hidden_set_or_key_touched: false`).

### Claim 2: Secrets never in git. HOLDS (repo side); key-holder scan CANNOT-VERIFY
- **Attack: any secret-shaped file ever added under D2, on any ref.** `rogit log --all --diff-filter=A --name-only -- prometheus/cosmos/c3_holdout_D2` lists only code, docs, the manifest, the `.enc` file and the self-test JSONs. There is no `*.key*`, `*.salt*` or `*.plain*` file.
- **Attack: records or secrets committed under `protocol/`.** `rogit log --all --full-history -- .../protocol` is empty.
- **Attack: secrets embedded in content** (hex blobs inside other files). This needs the key to search for. It is the key holder's `firewall_check` (`entry.py firewall-check`), which I cannot run. **CANNOT-VERIFY.** It would be settled by Nestor publishing the booleans of `entry.py firewall-check` (all-history) at a823b596c.
- Secret paths are named in code only (`draw.py:41`, `runner.py:155-157`).

### Claim 3: Enforced order. BROKEN on S1 (blocks-PASS, declared open); the mechanics otherwise HOLD
- **Attack: unauthenticated records (S1).**
  - A governing audit, commitment, designation or result seal counts if its sha256 is in the custodian's allow-list (`protocol.py:461-473`, `513-532`, `560`, `580`, `600`; `entry.py:183-184`, `256-262`).
  - The allow-list is fed from a comms message whose `sender` field was found client-supplied (v2 verdict; FIREWALL.md:156-158). main has no branch protection.
  - Anyone able to push to main, together with a forged comms sender, can therefore produce an allow-listed PASS audit, commitment or designation.
  - The FIREWALL.md v10 table lists S1 as OPEN (FIREWALL.md:357).
  - **Blocks PASS.** It is an operator decision (#925), not a code defect Nestor can close.
- **Attack: ref ambiguity (tags against remote-tracking refs).** Only `refs/...` is accepted. Shadow refs (`refs/tags/origin/main`, `refs/heads/origin/main`, `refs/tags/main`) refuse (`protocol.py:301-311`, `entry.py:218-220`). The key-holding CLIs force DEFAULT_REF (`custody.py:339-341`, `runner.py:1217-1219`). **Holds.**
- **Attack: history simplification or merge rewrite.** `log --full-history -m --raw` with a one-blob, one-add, no-modify rule (`protocol.py:314-358`). Replace objects are off, GIT_* is scrubbed, grafts and shallow repos refuse, and hooks are off (`protocol.py:185-219`, `entry.py:97-110`, `200-209`). **Holds.**
- **Attack: stale code after the audit.** `code_sha256` must bind exactly AUDITED_FILES, committed AND working tree (`protocol.py:533-542`). `entry.py` re-verifies every bound file before import and serves `prometheus.*` only from verified source bytes, never `__pycache__` (`entry.py:125-172`, `268-272`, `341-342`). Repository-root and cwd plants are refused (`entry.py:39-42`, `134-143`, `317-330`). **Holds.** Site-packages and `.pth` files are the declared F-3P residual.
- **Attack: key touched before the gates.** `prepare()` runs the gates, then package validation and staging, then the isolation probe; the key is read only in `open()` (`runner.py:657-736`, `763`). The marker comes only after the key is proven (`runner.py:763-782`). **Holds.**
- **Current state.** No `FIREWALL_AUDIT_<n>.json` is committed, so `entry.py gates SEAL` and every key-holding target refuse (`entry.py:274-276`). That refusal is correct.

### Claim 4: Controlled reveal. HOLDS; should-fix on seal-terminal (A2)
- **Attack: release to the wrong host, account or M2.**
  - check_gates refuses M2 as the designated host or the current host, a mismatched host, the wrong runner or account, and a custodian account (`protocol.py:574-589`).
  - release requires the preflight record (`custody.py:201-202`), test-decrypts at the resolved commit (`custody.py:171-180`, `204`) and is once-only (log, git and lock; `custody.py:195-200`).
  - Destination checks: `custody.py:114-136`.
  - **Holds.** The preflight record is self-reported; that is declared, and `prepare()` repeats every check.
- **Attack: reveal before the result seal, or with a tampered RESULT.** Reveal requires `check_gates("RESULT_SEAL")` with an allow-listed RESULT_SEAL, the chain head and result sha256 matching, and once-only (`custody.py:289-304`). evidence requires the same gate (`evidence.py:55-57`). **Holds**, subject to S1: the RESULT_SEAL allow-listing inherits S1.
- **Attack: seal-terminal changes what gets result-sealed.** See A2: V10-2 and V10-3.

### Claim 5: Predictor isolation. HOLDS as designed (same-account child always refused)
- **Attack: the child reads the key or secrets.** The pre-key probe covers the key path, the secrets, the receipts stand-in (read and append), file creation, and a required readable package (`runner.py:701-709`, `790-813`). A same-account child fails here, before anything is consumed. **Holds.**
- **Attack: pickle or hostile pipe messages.** JSON plus `np.load(allow_pickle=False)` (`runner.py:170-206`). Messages are capped at 64 MiB (`runner.py:202-206`). Any malformed message is that world's PROTOCOL_ERROR (`runner.py:973-1001`).
- **Attack: exception text leakage.** Replies carry `type(e).__name__` only (`runner.py:986-988`). **Holds.**
- The AST audit is a heuristic (declared). There is no separate-account launcher yet (V7-E, declared).
- Labels: V10-1 and V10-5 above.

### Claim 6: Draw integrity. HOLDS; single-draw provenance CANNOT-VERIFY (declared)
- **CSPRNG nonce:** `secrets.token_hex(32)` (`draw.py:154`). The world RNG is seeded by the nonce mod 2^128 (`draw.py:63`); that is 128 bits of seed entropy, infeasible to search.
- **Exposed-D rejection:** `draw.py:57-59`, `65-69`. Lattice membership is asserted (`draw.py:86-87`).
- **Attack: code drift since the draw.**
  - `rogit diff --stat 95b31a30d a823b596c -- draw.py sealbox.py __init__.py hidden_D2.enc MANIFEST_D2.json c3_holdout_D/` is empty.
  - `rogit diff --stat a56ef7787 a823b596c -- prometheus/cosmos/c3_holdout_D` is empty.
  - So the files are byte-identical to the seal commit. Whether their hashes equal `d2_src_sha256_at_draw` was not computed by me (no hashing available). **CANNOT-VERIFY here.** `verify_reveal --redraw` reports `redraw_code_matches_manifest`.
- **Single-draw provenance:** a custodian statement (declared).

---

## Part C: mandatory classes
1. **Unbound code with secrets.** v10 adds `import signal, threading` (stdlib) and custody imports `runner` (bound). No new unbound path. F-3P (site-packages) is declared.
2. **Same-account readability.** Declared: the OS account is the boundary. Same-account children are refused pre-key.
3. **Static-audit bypass.** A heuristic, declared; the isolation probe is the gate.
4. **Git ambiguity and simplification.** Holds (claim 3).
5. **Unauthenticated or rewritable records.**
   - **S1: blocks PASS** (declared open).
   - The receipts chain is unkeyed. Anyone with write access to the run directory can forge a verifying chain; world_tags are verifiable only after the reveal. This sits inside the same-account residual.
   - seal-terminal's unenforced "custodian only" (V10-3c).
6. **Public narrowing fields.** Ciphertext length (declared) and timing (declared N-1). The abort `error_type` is a type name only.
7. **Spoofable host or identity.** `socket.gethostname()` is used for the host check (`protocol.py:581`), which the same account can influence. That is declared within the account residual. The comms sender is spoofable (S1).

## Part D: declared residual risks
- **Not a boundary against the key holder:** acceptable as declared.
- **The prediction package runs as Python on M1; the AST audit is a heuristic:** acceptable. It is mitigated further by the mandatory pre-key isolation probe, which refuses every same-account child.
- **Single-draw provenance:** acceptable as declared.
- **The System interface reveals physics:** acceptable (contract design).
- **Missing from the list and should be declared, or fixed:**
  - seal-terminal is not mutually exclusive with a live run and is not bound to the custodian account (V10-3b/c);
  - SIGBREAK is not covered by the abort's signal masking;
  - the per-world TIMEOUT uses wall-clock time (V10-5);
  - `disk_chain_matched=false` can mean "could not read" (V10-7);
  - a stale `.claim` blocks the run with no guidance (V10-4).

## Findings index
| id | severity | summary | evidence |
|---|---|---|---|
| S1 | **blocks-PASS** (declared open; operator #925) | protocol records unauthenticated (allow-list fed by a spoofable comms sender; main unprotected) | protocol.py:461-473; FIREWALL.md:357 |
| V10-2 | should-fix | seal-terminal truncates records that `verify_receipts` accepts (final line without `\n`; records after a blank line), possibly a terminal `close` | runner.py:1164-1169 vs 452-455 |
| V10-3a | should-fix | seal-terminal checks only the directory basename, not the open record's nonce, spec or package, nor RUN_OUT_ROOT (docstring claims otherwise) | custody.py:237-245 |
| V10-3b | should-fix | no lock or liveness check: it can append a custodian abort to a live run and later truncate the runner's own records | custody.py:237-249; runner.py:384-405, 1043-1047 |
| V10-3c | should-fix | "custodian only" not enforced; `SEALED_BY_CUSTODIAN` label unauthenticated | custody.py:237-249; runner.py:1180 |
| V10-1 | should-fix | a spawn failure on restart becomes AssertionError (unstarted join) and the abort carries the stale `child_world` and a wrong `error_type` | runner.py:793-796, 903-915, 1017-1021, 838-846 |
| V10-5 | note | TIMEOUT decided on the wall clock | runner.py:962-966 |
| V10-6 | note | Ctrl-C windows around the close append: abort-after-close, or repair removes the on-disk close | runner.py:418-424, 1104-1105 |
| V10-7 | note | `disk_chain_matched` false on any OSError | runner.py:430-444 |
| V10-8 | note | uncaught AttributeError/StopIteration in seal-terminal on malformed input; no REFUSED log entry | runner.py:1170, 1122; custody.py:246 |
| V10-4 | note | a stale `.claim` after a hard crash blocks the run with a bare FileExistsError | runner.py:385-386 |

**Excluding S1 and branch protection (operator decisions), there is no blocks-PASS finding in the firewall code at a823b596c.**

OVERALL: FAIL (solely S1, declared open; no new blocking code finding)
