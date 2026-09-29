# Holdout D2 firewall re-audit v8: adversarial replica findings

- **Task:** tsk-40522d68e5fc, attempt att-ef518abff376 (disposable worker; skill audit.security.adversarial v1).
- **Audited commit:** a02b9b20c (the c3_holdout_D2 package was last changed in b674889ed, "D2 v8").
- **Scope:** the firewall layer only: FIREWALL.md sections v1 to v8, with the v8 focus. No law or science was examined.
- **Method:** static reading, plus `rogit` history queries. Nothing was executed: no self-test, no entry.py, no hashing
  (the sandbox refused a plain `sha256sum`).
- **Known open (not assessed as findings):** S1, the root of trust for protocol records (#925), and branch protection
  on main.

## Summary of verdicts

| # | claim | verdict |
|---|---|---|
| 1 | Opacity | HOLDS (plaintext length visible; declared) |
| 2 | Secrets never in git | HOLDS (repository side); CANNOT-VERIFY (key-holder scan on M1) |
| 3 | Enforced order | HOLDS, except S1 (declared open) |
| 4 | Controlled reveal | HOLDS for the reveal. The v8 open/abort path is **BROKEN** (V8-1, blocks-PASS). |
| 5 | Predictor isolation / attribution (v8 Q3, V7-B) | HOLDS as declared. The Q3 attribution is partly broken: V8-2 and V8-3 (should-fix). |
| 6 | Draw integrity | HOLDS / CANNOT-VERIFY-FROM-REPO (single-draw provenance; declared) |
| v8 | "no check or probe that can refuse runs after the key is read" | **BROKEN** (V8-1; V8-3 declared-adjacent) |
| v8 | "no consumed release without a VERIFIABLE terminal record" | HOLDS for ordinary exceptions. Residual paths: V8-5 (note). |

---

## V8 findings

### V8-1: key authenticity and plaintext consistency are checked only AFTER the consumption marker. blocks-PASS

**Evidence:**
- `runner.py:723`: `key = sealbox.read_hex_file(self.key_path, 32)`. This checks format and length only
  (`sealbox.py:83-88`).
- `runner.py:726`: `Receipts.create_with_open(...)` writes the consumption marker.
- `runner.py:728-729`: the key file is deleted (`delete_key=True` in the CLI, `runner.py:1105`).
- `runner.py:730`: `sealbox.decrypt(...)` runs only now. It raises `InvalidTag` for a wrong key (`sealbox.py:76-80`).
- `runner.py:732-741`: the `HiddenSetMismatch` consistency checks also run after the marker.
- `prepare()` (`runner.py:619-697`) never touches the key file content. It only checks `inside_git_repo(key_path)` at
  `runner.py:637`.
- Custody does not check the key either. `custody.py:195-196` copies whatever `secrets_dir/hidden_D2.key.hex` holds,
  with no decrypt test against the sealed ciphertext.

**Scenario (argument-controlled):**
1. The designated runner passes `--key` pointing to any well-formed 64-hex-character file that is not the D2 key. Examples:
   a throwaway self-test key, the key from an earlier trial, or a mistyped path to another key file.
2. All gates, validation, staging and the probes pass, because none of them depends on the key's content.
3. `open()` reads the key and writes `receipts.jsonl` with a verifiable open record. It then deletes that wrong file.
4. `decrypt` raises `InvalidTag`, and `run_all` (`runner.py:804-807`) seals an `abort` (error_type `InvalidTag`,
   phase OPEN).
5. From then on:
   - `_run_cli` refuses a rerun because the receipts exist (`runner.py:1099-1100`).
   - Custody refuses a second release (`custody.py:186-189`).
   - The real released key is left undeleted in the custody destination.
6. Under the v7 policy (FIREWALL.md:311-316), the outcome is VOID and D2 is spent. A successor seal is required, even
   though no package code ever ran.

The same holds if custody's own key file is not the sealed key.

**What this breaks:** this is exactly the v8 ask: "a check ... that can refuse runs after the key is read". It is also
the v6 criterion: "a recoverable error (package, probe, **argument**, environment) happens after the key is read or the
release is consumed". v5 BP-1 (validation after the key read) was ruled blocking on the same standard.

**Impact:** availability, not confidentiality. The hidden set is not exposed, but the holdout is irrecoverably spent by a
recoverable argument error.

**Fix (small):** check the key before the marker, in either of two ways:
- decrypt and run the consistency checks in `open()` BEFORE `create_with_open`. No child is running then, and the
  runner already holds the key, so this weakens nothing;
- or have custody test-decrypt before release.

Add a self-test with a well-formed wrong key: it must leave no receipts and the key copy intact.

### V8-2: the Q3 field `child_exitcode` is ALWAYS null. should-fix

**Evidence:**
- `abort()` calls `self._stop_worker(kill=True)` first (`runner.py:772-775`).
- `_stop_worker` ends with `self._proc = self._conn = None` (`runner.py:854`).
- Only after that does abort read `proc = getattr(self, "_proc", None)` (`runner.py:779`), which is now None. So
  `child_exitcode` is `None` on every path.
- Every per-world failure path also nulls `_proc` before any abort can happen (`runner.py:893, 899, 904, 928`).
- The self-test checks only that the KEY exists (`selftest_protocol.py:1165-1166`), so it cannot detect this.

**Scenario:** a package-initiated run-level abort (for example the Windows path in V8-4) records `child_exitcode: null`,
the same as a pure runner fault. FIREWALL.md:327 claims "the child's exit code", and that claim is false. The
FORFEIT/VOID evidence the v7 verdict asked for (condition 2, "child exit status") is not delivered.

**Fix:** capture `self._proc.exitcode` (after the kill and join) before nulling it, in `_stop_worker` or in abort. Add a
self-test that asserts a non-null value when a child existed.

### V8-3: a refusing probe still runs after the key read, with stale attribution. should-fix (declared-adjacent)

**Evidence:**
- `_predict_one` calls `self._start_worker()` whenever `_proc is None` (`runner.py:887-888`). That is world 0, and
  EVERY world after a per-world crash, timeout or protocol error, since each of those kills the child.
- `_start_worker` runs `_spawn_probe` (`runner.py:839`), which can raise `ChildNotIsolated` or `PredictorChildFailed`
  (120 s answer limit, `runner.py:752-762`).
- The call is outside the per-world guard, and runs BEFORE `_cur_world` and `_in_predictor_io` are set
  (`runner.py:889`).

**Scenario:**
1. World i ends as PREDICTOR_CRASH. `_in_predictor_io` is reset to False at `runner.py:943`.
2. At world i+1 the respawned child fails its probe or its start, for example:
   - host load;
   - an ACL change on the runs directory;
   - a repository file edited in the working tree between the parent's verification and the respawn, so the child's
     import guard fails (`entry.py:168-172`);
   - with an AST bypass (a declared heuristic), a grandchild left by the package that starves the new child.
3. Run-level abort. The record carries `current_world = i` (the PREVIOUS world), `in_predictor_io = false` and
   `child_exitcode = null`. That reads as a runner-internal or infrastructure failure, which points to VOID.

FIREWALL.md v7 (line 304) declares the post-key probe on the real receipts. It does not declare the respawn probes or
this misattribution.

**Fix:**
- set `_cur_world` and the flag before `_start_worker`;
- record a respawn-probe failure distinctly (for example `in_predictor_respawn`);
- or treat a failed respawn as that world's crash.

### V8-4: `Connection.poll` is outside the per-world guard. note (PLAUSIBLE, Windows only)

**Evidence:** `runner.py:898` calls `self._conn.poll(...)` outside any try. Only `_recv` (`runner.py:901-905`) and the
message handling (`runner.py:908-929`) are guarded.

**Expected behaviour (from CPython's `PipeConnection._poll`; not verified here):** on Windows it calls
`_winapi.PeekNamedPipe`, which raises `BrokenPipeError` when the child end is already closed and no data is buffered.

**Consequence:** a child that exits (for example `raise SystemExit` in predict: not flagged, and the worker catches only
`Exception`, `runner.py:350`) before the parent re-enters `poll` produces a run-level abort instead of a per-world
PREDICTOR_CRASH. This is a race; the parent usually wins.

`v8_V7B_pipe_close_is_per_world_and_run_closes` passes on M1 only because its package sends a message before closing
(`selftest_protocol.py:1090-1093`), so `PeekNamedPipe` sees buffered data.

**Impact:** the abort carries `in_predictor_io = true`, so it points towards FORFEIT. This is attribution, not a leak.
**Fix:** move the poll inside the guard.

### V8-5: a terminal record that cannot be sealed when the RESULT.json write fails. note (within the declared crash class)

**Evidence:**
- `close()` appends `close` and only then writes RESULT.json (`runner.py:1042-1051`). `abort()` does the same
  (`runner.py:780-791`).
- If that write fails (disk full, antivirus lock), the chain verifies and has a terminal record, but result-seal
  refuses because it needs RESULT.json with a matching chain_head (`custody.py:241-243`).
- In the close case, `run_all` calls `abort()`, which returns `{"status": "CLOSED"}` without a chain_head. `_run_cli`
  then raises `KeyError` on `res["chain_head"]` (`runner.py:1114`).
- No tool regenerates RESULT.json from the chain, although its content is derivable from it.
- Separately, a KeyboardInterrupt between `os.replace` (`runner.py:389`) and the assignment at `runner.py:726` leaves the
  marker with `self.receipts is None`, so `run_all` re-raises (`runner.py:805-806`). That chain has no terminal record.
  Operator/OS only, tiny window.

Both are environment/operator triggers, adjacent to the declared "disk full while writing the abort".

**Recommendation:** a custodian `seal-terminal` tool that appends `abort` to an unterminated verifying chain and rebuilds
RESULT.json from the receipts would close the whole crash-after-release class.

### V8-6: an aborted run can leave the released key copy on disk. note

**Evidence:** `abort()` never deletes `key_path`.
- If `unlink` at `runner.py:729` fails, the run aborts with the key still present.
- In V8-1 the real key is never touched.

**Impact:** within the account residual, but the custodian procedure should wipe the destination after any terminal
outcome.

---

## Claim-by-claim

### Claim 1: Opacity. HOLDS

**Attacks tried:**
- **Manifest fields as narrowing information** (`MANIFEST_D2.json:1-36`):
  - IV, hashes, versions, draw time, the at-draw source hashes: no knob, seed or nonce.
  - `ciphertext_bytes` = 17227 reveals the plaintext length (GCM tag is 16 bytes). This is declared (FIREWALL.md:149-150).
- **Brute force on the commitment:** it is `sha256(salt || plaintext)` with a 32-byte secret salt (`sealbox.py:64-67`), so
  a guessed world set cannot be confirmed without the salt.
- **Error text as a channel:**
  - System-call errors return type names only (`runner.py:915-916`);
  - the abort carries a type name and indices only (`runner.py:780-784`);
  - `PREDICTOR_ERROR` text is the package's own exception text (`runner.py:351, 924`).
- **Receipts:** worlds are named by index plus `world_tag = HMAC(key, world||seed)` (`runner.py:737-738`). `_summ` drops
  `system` (`runner.py:566-571`). The open record's contents are public-only (`runner.py:677-689`).
- **Timing:** declared (N-1, FIREWALL.md:254).

### Claim 2: Secrets never in git. HOLDS (repository side) / CANNOT-VERIFY (M1)

**Checks:**
- `rogit log --all --stat -- hidden_D2.enc MANIFEST_D2.json`: only 95b31a30d adds them.
- `rogit log --all --name-only -- "*.key*" "*.salt*" "*plain.json" "*nestor_secrets*"`: empty.

Content-level scans (key hex, seeds) need the key holder's `entry.py firewall-check` on M1. The booleans are not
reproducible here.

### Claim 3: Enforced order. HOLDS (S1 open)

**Attacks tried:**
- a record replaced through a merge, or deleted and re-added: `_added_once` uses the full history with `-m`, one blob,
  one non-merge add (`protocol.py:314-358`);
- the ordering: strict ancestry (`protocol.py:519-524, 558-559, 578-579, 605-606`);
- a stale audit: exact `AUDITED_FILES`, committed tree and working tree (`protocol.py:533-542`);
- ref shadowing (`protocol.py:301-311`, `entry.py:218-220`);
- unauthenticated later audit records: the allow-list filters first (`entry.py:257-260`, `protocol.py:513-518`);
- the runner gates BEFORE the key: `prepare()` runs `check_gates` first (`runner.py:631-634`). Custody gates before
  reading the key (`custody.py:185-195`).

Residual: record authorship (S1) and branch protection.

### Claim 4: Controlled reveal. HOLDS (the reveal); the v8 open path is BROKEN (V8-1)

**What holds:**
- Reveal requires a RESULT_SEAL gate on an allow-listed record, a chain that verifies and ends at the sealed head, and a
  matching RESULT.json hash, once (`custody.py:255-297`).
- Result-seal accepts close or abort only on a verifying chain (`custody.py:229-243`).
- Key release: the designated host is not M2 (`protocol.py:574-585`), a preflight record is required
  (`custody.py:190-191`), and the destination is checked (`custody.py:114-136`).

**What is broken:** the key is never validated before the consumption marker (V8-1).

### Claim 5: Predictor isolation. HOLDS as declared; Q3 attribution partly broken (V8-2, V8-3, V8-4)

**Attacks tried:**
- **Pickle:** there is none. The JSON codec loads arrays with `allow_pickle=False` (`runner.py:170-206`). Messages are
  capped at 64 MiB (`runner.py:202-206`).
- **Hostile replies:** every child message is guarded per world (`runner.py:901-929`).
- **The v8 send guard:** in place (`runner.py:890-894`).
- **Stand-in read probe (V7-A):** in place (`runner.py:667`). The probe reads 1 byte of an empty file, which succeeds, so a
  readable stand-in is caught.
- **The child's OS account and memory access:** declared residuals (FIREWALL.md:209-216, 249-251, 331-333).

### Claim 6: Draw integrity. HOLDS / CANNOT-VERIFY-FROM-REPO

- `draw.py`, `sealbox.py` and `__init__.py` were touched only by 95b31a30d (`rogit log`), so the files on main are the
  sealed-commit bytes.
- I did not recompute the sha256 values against `d2_src_sha256_at_draw` (`MANIFEST_D2.json:11-15`), because hashing was
  denied in this sandbox. `verify_reveal --redraw` settles it after the reveal.
- Single-draw provenance is a custodian statement (declared).

## Checked classes

| class | result |
|---|---|
| 1. unbound code with secrets | entry.py binds the closure (not re-broken this round); third-party code (F-3P) declared |
| 2. same-account secret readability | declared account residual |
| 3. AST bypass | heuristic, declared. `raise SystemExit` and `def __del__` are not flagged; this is relevant only to V8-4. |
| 4. ref ambiguity / merges | holds (claim 3) |
| 5. unauthenticated records | S1 open |
| 6. narrowing public fields | length (declared). The abort fields are public-safe. |
| 7. host/identity spoofing | `gethostname` is spoofable by a same-account user; within the account residual |

## Declared residual risks

| residual | assessment |
|---|---|
| gates not a boundary against the key holder | acceptable as declared |
| AST audit is a heuristic | acceptable |
| single-draw provenance | acceptable |
| the System interface reveals physics | acceptable (the contract's design) |
| the child can signal or pressure the parent (v8) | acceptable only if the attribution evidence is real; it is not yet (V8-2, V8-3) |
| crash-after-release (v7) | acceptable for power loss or a hard kill |

**Missing from the list:**
- a wrong-key or bad-plaintext failure after the marker (V8-1);
- a RESULT.json write failure after the terminal record, with no regeneration path (V8-5);
- the released key copy is not wiped after an abort (V8-6).

## Overall

- One blocks-PASS finding (V8-1). It is cheap to fix: decrypt before the marker.
- Two should-fix findings (V8-2, V8-3) on the Q3 attribution evidence.
- S1 and branch protection remain open by operator decision.

**OVERALL: FAIL**
