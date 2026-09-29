# Holdout D2 firewall re-audit v8: adversarial findings (replica, task tsk-f3fcbe5f914b)

- **Audited commit:** a02b9b20c (HEAD of this checkout). The c3_holdout_D2 package was last changed by b674889ed (v8).
- **Method:** static reading plus `rogit` history only. I executed no repository code, and shell hashing was denied
  in this environment. Wherever a verdict depends on runtime behaviour, it says so.
- **Scope:** the firewall layer only. S1 (#925) and branch protection are acknowledged as OPEN operator decisions and
  are not re-argued here.
- **v8 focus:** find a consumed release without a VERIFIABLE terminal record, and find a refusing check or probe
  that runs after the key is read.

---

## Headline finding (blocks-PASS)

### V8-1: a failed receipt append leaves the on-disk chain and the in-memory chain out of step, so the abort record written afterwards can never verify

Evidence:
- `runner.py:398-406`, `Receipts.append`, runs in this order:
  1. It computes `seq = len(self.records)` and `prev = self.head` from memory.
  2. It writes the line, then calls `f.flush()` and `os.fsync()`.
  3. Only after that does it call `self.records.append(rec)`.
- If anything raises after the bytes have reached the file but before step 3, the record is on disk and missing
  from memory. Examples: `os.fsync` raising `OSError`, a `KeyboardInterrupt` raised at the bytecode after `write`,
  `flush` or `fsync`, or a `MemoryError` at `records.append`.
- `run_all` (`runner.py:804-807`) then calls `abort()`. `abort()` calls `self.receipts.append("abort", ...)`
  (`runner.py:780`), which reuses the stale `seq`/`prev`. The file now holds `..., rec_k(seq k), abort(seq k,
  prev=hash_{k-1})`.
- `verify_receipts` (`runner.py:421-423`) returns "seq break at k+1".
- If `flush` fails partway through a write (for example on ENOSPC), the torn line runs into the abort line and the
  result is "unreadable: ValueError".
- The same happens on the certify path: `certify_all`'s `except Exception` calls `self._gate(i)`
  (`runner.py:1022-1023`). `_gate` compares the disk chain with memory (`runner.py:973-974`) and raises
  `OrderViolation`, which reaches `abort`, which writes the duplicate-seq record.

Consequence:
- `custody.result_seal_record` refuses: "receipt chain does not verify" (`custody.py:230-232`). Reveal and evidence
  refuse the same way (`custody.py:264-266`, `evidence.py:57-59`).
- The run cannot be re-run: receipts exist (`runner.py:1099-1100`, `runner.py:654-655`), and KEY_RELEASED is once
  only.
- The designation is therefore spent with no sealable outcome: neither VOID nor FORFEIT can be recorded.

Minimal scenario:
1. A designated run is in the PREDICT phase and `receipts.append("prediction", ...)` is running for world 17.
2. `os.fsync` raises `OSError` (a device or I/O error), or the operator presses Ctrl+C while the fsync is in
   progress. Fsync is the slow part of the append, so this is the likeliest place for a Ctrl+C to land.
3. The prediction line for world 17 is on disk, but `self.records` does not include it.
4. `abort()` appends `{"seq":18, ...}` when seq 19 is expected, with `prev` equal to the hash of record 17.
5. The chain does not verify, so result-seal is refused, and nothing further is possible for this spec_id.

Package-driven variant:
- The v8 residual says the child can send Windows console control events to the shared console group
  (`FIREWALL.md:332`).
- A package that does so right after it sends `done` hits the parent while the parent is inside the fsync of that
  world's prediction append. This window is the same every time and lasts milliseconds, so the package can hit it
  reliably.

Related window in `open()`:
- A `KeyboardInterrupt` after `os.replace` inside `create_with_open` (`runner.py:389-392`), but before
  `self.receipts` is assigned (`runner.py:726`), leaves `self.receipts is None`.
- `run_all` then re-raises (`runner.py:805-806`). The chain is `[open]` with no terminal record, and result-seal
  refuses with "no terminal record" (`custody.py:233-234`).

Why this blocks PASS:
- FIREWALL.md v8 claims: "an ordinary exception can no longer spend the designation without a sealable terminal
  record" (`FIREWALL.md:334`). A `KeyboardInterrupt` is explicitly within v7's claim (`FIREWALL.md:305`, item c).
  An `OSError` from fsync is an ordinary exception.
- The declared crash residual lists only "power loss, OS kill, disk full while writing the abort"
  (`FIREWALL.md:312`). Here the abort write itself SUCCEEDS; the chain is unverifiable because of the earlier
  divergence.
- This is the same class and the same standard as V7-1, which the v7 auditor ruled blocking "whatever the
  likelihood" (`roles/Odysseus/fabric_pilot/d2_audit/v7/VERDICT.md:32-41`).

Not covered by any self-test:
- The v8 tests inject a failure only in `create_with_open` (`selftest_protocol.py:1115-1131`).
- They test abort right after open only on a clean chain (`selftest_protocol.py:1137-1139`).

Fix sketch:
- In `Receipts.append`, note the file size before writing. On any `BaseException`, truncate back to that size,
  then re-raise.
- Alternatively, make `abort()` re-read the on-disk chain first: truncate a torn tail, adopt a fully written
  trailing record, then append.
- Assign `self.receipts` inside a guard that cannot be skipped.
- Add a test that injects an `OSError` from `os.fsync` after a prediction record is written and asserts that the
  run can be result-sealed.

---

## Claim-by-claim

### Claim 1: Opacity. HOLDS (with the note below)

Attacks tried:
- **Manifest fields.** `MANIFEST_D2.json:1-36` carries the IV, the ciphertext hash and length, the salted
  commitment, versions, at-draw code hashes and the draw time. There are no worlds, knobs, seeds or nonce. The
  length is a declared residual (`FIREWALL.md:149-150`).
- **New v8 receipt fields.** The abort carries `current_world` (an index), `in_predictor_io` and `child_exitcode`
  (`runner.py:780-784`). Receipts stay on M1 until reveal.
- **Public result seal.** RESULT_SEAL carries only hashes plus `terminal` and `n_receipts` (`custody.py:246-249`).
- **Pipe error replies.** They carry type names only (`runner.py:914-916`).
- **Brute force against the commitment.** It is salted with 32 bytes (`sealbox.py:64-67`).

Note (N-1 extension): after an abort, `n_receipts` in the public RESULT_SEAL encodes the world at which the run
ended. The package controls that point, so it is a small covert count channel that opens after the predictions are
frozen. It is the same class as the declared timing channel (`FIREWALL.md:254`). Add it to that declaration.

### Claim 2: Secrets never in git. HOLDS for everything the repository can show; the M1 side CANNOT-VERIFY

- `rogit log --all --name-status -- prometheus/cosmos/c3_holdout_D2` shows only code, docs, the manifest and the
  ciphertext. No `*.key*`, `*.salt*` or `*.plain.json` was ever added.
- `rogit log --all -- *.key.hex *.salt.hex *.plain.json *nestor_secrets*` returns nothing.
- Whether the key, salt and plaintext exist only on M1 depends on the key holder's `firewall-check` booleans. That
  can only be settled on M1.

### Claim 3: Enforced order. HOLDS (unchanged since v7)

- v8 touched only `runner.py` and the self-tests.
- Attacks re-tried in reading:
  - A merge carrying a replaced record is caught: `_added_once` uses full history with `-m` and requires one blob
    (`protocol.py:334-358`).
  - Tag shadowing of origin/main is refused (`protocol.py:301-311`, `entry.py:218-220`).
  - Grafts and shallow files are refused (`protocol.py:209-219`).
  - Code changed after the audit is refused, both committed and in the working tree (`protocol.py:533-542`).
  - The guard compiles from the bytes it just hashed (`entry.py:161-172`).
- The runner runs the gates in `prepare()` before the key is read (`runner.py:631-634`, `runner.py:723`).
- Records are unauthenticated (S1), which is OPEN by declaration.

### Claim 4: Controlled reveal. HOLDS

- Release requires the DESIGNATION gates, the once-only records, a preflight and an ACL restricted before the key
  is written (`custody.py:177-213`).
- Reveal requires an allow-listed RESULT_SEAL, the chain head and the result hash (`custody.py:255-297`).
- Evidence requires the same (`evidence.py:55-61`).
- The only weakness here is V8-1: the result seal becomes unreachable. The reveal ordering itself is not broken.

### Claim 5: Predictor isolation. HOLDS as declared; the v8 attribution evidence is partly broken

- The pipe carries no pickle: JSON plus `.npy` with `allow_pickle=False` (`runner.py:170-206`).
- Messages are capped at 64 MiB (`runner.py:202-206`).
- A malformed message becomes a per-world PROTOCOL_ERROR (`runner.py:906-929`).
- The `predict` send is inside the guard (`runner.py:890-894`).

Findings:
- **V8-2 (should-fix): `child_exitcode` is always `None`.**
  - `abort()` first calls `self._stop_worker(kill=True)` (`runner.py:773`), which sets `self._proc = None`
    (`runner.py:854`). Only then does it read `proc = getattr(self, "_proc", None)` (`runner.py:779`).
  - The Q3 exit-code evidence is therefore never recorded.
  - The self-test checks only that the key is present (`selftest_protocol.py:1165-1166`).
  - Fix: capture `proc` and its exit code before stopping the worker.
- **V8-3 (should-fix): a post-key refusal is misattributed.**
  - Each worker restart after a TIMEOUT or crash re-runs the isolation probe AFTER the key was read
    (`runner.py:887-888`, `runner.py:836-840`, `runner.py:745-762`). It can raise `PredictorChildFailed` or
    `ChildNotIsolated` and abort the run.
  - That is a refusing probe after the key read. It is declared as a sealed abort (`FIREWALL.md:304`).
  - The attribution is wrong, though. `_cur_world` and `_in_predictor_io` are set only AFTER `_start_worker()`
    (`runner.py:889`), so the abort names the PREVIOUS world with `in_predictor_io: false`, and the exit code is
    `None` (V8-2).
  - A restart failure that the package induced (a hung child that forced the restart, with load left behind)
    therefore reads as infrastructure, which Addendum E makes VOID.
- **V8-5 (note, PLAUSIBLE, Windows only).**
  - `self._conn.poll(...)` (`runner.py:898`) is outside the per-world `try`.
  - On Windows, `PipeConnection._poll` calls `PeekNamedPipe`, which raises `BrokenPipeError` when the pipe is
    empty and the child has exited.
  - A child that exits in the short gap after the parent's reply send, for example with an AST-clean
    `raise SystemExit`, would abort the whole run instead of producing a per-world PREDICTOR_CRASH. The abort is
    attributed (`in_predictor_io: true`).
  - The v8 PIPE_CLOSER test always leaves a message in the pipe (`selftest_protocol.py:1089-1093`), so it never
    exercises this path.
  - It is a race. Settle it on M1 with a package whose `predict` makes one System call and then raises
    SystemExit, run over 128 worlds.

### Claim 6: Draw integrity. HOLDS

- `rogit diff 95b31a30d HEAD` over `draw.py`, `sealbox.py`, `__init__.py`, `hidden_D2.enc`, `MANIFEST_D2.json` and
  `c3_holdout_D/` is empty: all are byte-identical to the seal.
- The CSPRNG nonce comes from `secrets.token_hex(32)` (`draw.py:154`).
- Exposed-D duplicates are rejected (`draw.py:62-72`).
- I could not recompute the sha256 values myself because hashing was denied. They were already checked by earlier
  replicas and by `verify_reveal`'s `redraw_code_matches_manifest`.

### v8-specific claims

| v8 item | verdict | evidence |
|---|---|---|
| V7-1 atomic marker (open record created atomically) | HOLDS for the open record | `runner.py:376-392`, `runner.py:671-697`, `runner.py:723-726` |
| "no ordinary exception can spend the designation unsealed" | **BROKEN (V8-1)** | see above |
| V7-A stand-in probed for read and append | HOLDS | `runner.py:667` |
| V7-B closed pipe is per-world | HOLDS on Linux; one race on Windows (V8-5) | `runner.py:890-905`, `runner.py:898` |
| Q3 attribution evidence | PARTLY BROKEN (V8-2, V8-3) | `runner.py:773-784`, `runner.py:887-889` |
| V7-F 64 MiB cap | HOLDS | `runner.py:202-206`; the caller maps the OSError to PREDICTOR_CRASH at `runner.py:903` |
| V7-D operator/faulthandler flagged | HOLDS; still a heuristic | `runner.py:103` |

---

## Standard classes (1-7)

1. **Unbound code with secrets.** No change in v8. F-3P (site-packages and `.pth` files) remains declared.
2. **Same-account readability.** Declared. Every production run fails closed until a separate child account
   exists.
3. **Static-audit bypasses.**
   - The AST audit is still bypassable. `raise SystemExit` / `KeyboardInterrupt` is not flagged. It is declared a
     heuristic, and it matters only for V8-5.
4. **Git reference ambiguity and history simplification.** HOLDS (`protocol.py:301-358`).
5. **Unauthenticated or rewritable records.**
   - S1 is OPEN.
   - Receipts can be rewritten by the same account, which is declared.
   - V8-1 is a self-inflicted unverifiable record.
6. **Public fields.** The `n_receipts` count channel is a note under Claim 1.
7. **Spoofable host or identity checks.** The host comes from `socket.gethostname()` (`protocol.py:581`). It is
   same-account state and was already declared.

## Declared residuals: assessment

- **Key holder / OS account boundary:** acceptable as declared.
- **AST audit is a heuristic:** acceptable.
- **Single-draw provenance:** acceptable as a custodian statement.
- **System interface exposes physics:** acceptable, by the contract's design.
- **Crash-after-release (v7):** acceptable for crashes truly outside the process. It does NOT cover V8-1, which is
  an in-process ordinary exception.
- **"The child can signal or pressure the parent … the resulting abort carries attribution evidence"**
  (`FIREWALL.md:332`): incomplete.
  - (a) Two console control events in a row: the second `KeyboardInterrupt` interrupts `abort()` itself, because
    `abort` catches only `Exception` around `_stop_worker` and nothing around the append (`runner.py:772-784`). No
    terminal record is written at all.
  - (b) One event timed into the append makes the chain unverifiable (V8-1).
  - (c) Disk exhaustion by the child account on the same volume is not listed. It gives torn appends or a failed
    abort.
  - (d) The exit-code evidence is always `None` (V8-2).
- **Missing from the list:**
  - The `n_receipts` count channel.
  - RESULT.json is written non-atomically (`runner.py:790-791`, `runner.py:1050-1051`). A crash there leaves a
    verifiable terminal chain that result-seal cannot use (`custody.py:241-243`), and there is no documented
    recovery. Note: the custodian can rebuild it by hand, since result-seal checks only `chain_head`.
  - If writing RESULT.json fails after `close`, `abort` returns `{"status": "CLOSED"}` and `_run_cli` then raises
    `KeyError` on `chain_head` (`runner.py:770-771`, `runner.py:1114`).
  - A prepare-time check that the child can actually READ the staged package is missing. With an inherited ACL
    that denies the child read on the run directory, every world becomes PREDICTOR_CRASH after the release is
    consumed, and the run CLOSES on an infrastructure misconfiguration. No step before the key read tests
    importability (`runner.py:663-669` probes with `pkg_dir=""`). Should-fix: probe that the staged entry file
    reads as "opened" before the key.

## Severity summary

| id | severity | one line |
|---|---|---|
| V8-1 | **blocks-PASS** | exception after a receipt write but before the in-memory update → abort duplicates seq → unverifiable chain, spec_id spent unsealed |
| V8-2 | should-fix | `child_exitcode` is always None: the worker is killed and nulled before the exit code is read |
| V8-3 | should-fix | a restart-probe failure after the key read is attributed to the previous world with in_predictor_io=false |
| V8-6 | should-fix | no check before the key that the child can read and import the staged package |
| V8-4 | note | residual wording: a double ctrl event defeats abort; disk pressure not declared |
| V8-5 | note | Windows `poll()` outside the guard: a narrow race turns a child exit into a whole-run abort |
| V8-7 | note | RESULT.json not atomic; KeyError after a failed RESULT write in close; `n_receipts` count channel |
| S1, branch protection | OPEN (operator) | not assessed further |

OVERALL: FAIL
