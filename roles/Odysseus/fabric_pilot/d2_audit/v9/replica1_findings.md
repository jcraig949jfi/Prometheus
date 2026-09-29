# Holdout D2: v9 firewall re-audit (adversarial replica)

- **Task:** tsk-5c232d68f717, attempt att-155ff2e50749. Skill: audit.security.adversarial v1.
- **Audited commit:** 2aa834ab18b530bb045b8065a94f1b97d2da535d. The D2 code is at ece679b89 ("D2 v9").
- **Method:** read-only static review. I could not run any code, so the self-tests and the real-history
  `entry.py gates` run are not re-executed here.
- **Scope:** FIREWALL.md "v9" (lines 336-352) and the v9 ask: "a recoverable error (argument, key, environment, I/O)
  that consumes the release without a verifiable terminal record, or a post-key path whose attribution labels are
  untruthful". The other claims are re-checked against the code delta since v8.
- **No law, prediction or science content** was read or needed.

## 0. What changed since the v8-audited code (a02b9b20c)

`rogit diff --stat a02b9b20c 2aa834ab1` over the D2 package, `c3/`, `c3_holdout_D/` and the package `__init__` files
shows code changes in exactly two files:
- `runner.py`, +94/-32;
- `custody.py`, +13/-2.

The rest of the delta is docs (AUDIT_BRIEF.md, FIREWALL.md), `SELFTEST_PROTOCOL.json` and `selftest_protocol.py`.

`entry.py`, `protocol.py`, `evidence.py`, `allowlist.py`, `firewall_check.py`, `draw.py`, `sealbox.py` and
`verify_reveal.py` are byte-unchanged since v8. The v8 verdicts on them therefore carry forward unchanged (v8
VERDICT.md; replica findings under roles/Odysseus/fabric_pilot/d2_audit/v8/).

Public commitments re-checked:
- `sha256(hidden_D2.enc)` is `f75ba333...dc9f` and `sha256(MANIFEST_D2.json)` is `78874e9d...71fe` (sha256sum on the
  checkout). Both match the brief.
- `rogit log --all --name-only -- prometheus/cosmos/c3_holdout_D2` lists no `*.key*`, `*.salt*` or `*.plain*` file and
  no `protocol/` record in any commit. `hidden_D2.enc` and `MANIFEST_D2.json` appear only in 95b31a30d.

## 1. v8 items: are they repaired?

### Item 1 (V8-1, wrong-key spend): REPAIRED. HOLDS

Attacks tried:
- **(a) A well-formed wrong key.**
  - `open()` reads the key (runner.py:750) and decrypts under AES-GCM with the AAD (runner.py:751-755). InvalidTag
    raises HiddenSetMismatch before the marker.
  - The plaintext consistency checks (runner.py:756-759) and the world count (766-767) also run before
    `Receipts.create_with_open` (runner.py:769).
  - `delete_key` runs only after the marker (runner.py:772-773), so the key copy is intact on a refusal.
  - `run_all` re-raises when `self.receipts is None` (runner.py:844-845).
  - The self-test `v9_1_wrong_key_refused_before_marker` asserts exactly this (selftest_protocol.py, v9_checks).
- **(b) A malformed key (bad hex, wrong length, non-ASCII).**
  - `read_hex_file` raises ValueError or UnicodeDecodeError (sealbox.py:83-88) before the marker. Nothing is consumed.
  - Cosmetic: main() catches only RunnerRefusal and GateRefusal (runner.py:1128), so this prints a traceback.
- **(c) Custody.**
  - `release_key` now reads and test-decrypts the key before `dest.mkdir` (custody.py:202-204). `_test_decrypt`
    wraps everything, including a `_show` that returns None (protocol.py:203-206 returns None on error), into
    CustodyRefusal (custody.py:171-179).
  - Small gap (note N-4): a malformed CUSTODY key file raises ValueError from `read_hex_file` (custody.py:202). That
    error is outside the handled tuple (custody.py:210), so the lock file stays behind and no REFUSED event is
    logged. Nothing is released.
- **(d) A decrypt-then-mismatch race between prepare() and open().**
  - `ct` and `fam` are captured in prepare() (runner.py:671-676) and used for the proof.
  - The manifest's ciphertext hash is tied to the gated spec_id (runner.py:667-673).
  - I found no way to prove against one ciphertext and run on another.

### Item 2 (V8-1 replica 2, interrupted write): REPAIRED for the ordinary cases. HOLDS, with note N-1

Attacks tried:
- **(a) An fsync or flush failure after a complete write.**
  - `append` catches BaseException and calls `repair()` (runner.py:401-410).
  - `repair` truncates the file to `_expected_bytes()` when the file starts with it (runner.py:417-431).
  - The in-memory record is not appended, so disk equals memory.
  - Covered by `v9_2_*`: fsync fails on call 3, the abort seals, and custody result-seals it.
- **(b) An async interrupt after a successful write but before `self.records.append` (runner.py:406-411).**
  - The file holds one record more than memory.
  - `abort()` calls `repair()` first (runner.py:813). That drops the extra full line, because the file starts with
    the expected bytes. The chain stays consistent.
- **(c) A torn partial line.** Truncated by the same prefix rule.
- **(d) A serialisation mismatch between `_expected_bytes` and the writers.**
  - Record 0 is written with the same `json.dumps(sort_keys, separators)` call and `newline="\n"` (runner.py:385-386)
    as `append` (runner.py:402-403) and `_expected_bytes` (runner.py:415).
  - `ensure_ascii` is the default, so there is no encoding drift.
- **(e) repair() itself fails.** See N-1: abort ignores the result.

### Item 3a (V8-2, child_exitcode always null): REPAIRED, but the value is stale outside the predict phase. Note N-3

- `_stop_worker` now records `_last_exitcode` (runner.py:893).
- `abort()` calls `_stop_worker(kill=True)` first (runner.py:810), so `proc` is None and `_last_exitcode` is used
  (runner.py:817-818).

### Item 3b (V8-3, restart-probe attribution): the respawn case is REPAIRED, but the first start is now mislabelled. BROKEN (should-fix S-A)

### V8-6 (child can read the staged package, pre-key): REPAIRED. HOLDS

- `prepare()` passes `must_read=[<run>/package/<entry>]` (runner.py:692-693).
- `_spawn_probe` refuses PredictorChildFailed unless the child reports "opened" (runner.py:791-795).
- must_read paths are excluded from the isolation list (runner.py:796), and no secret path can equal a path inside
  `<run>/package`.
- Only the ENTRY file is probed. Other members inherit the same directory ACL, so this is acceptable.

## 2. The v9 ask, attacked

### S-A (should-fix): the FIRST child start (world 0) is labelled `in_predictor_io=true, current_world=0`, although no package code has run and no world has been delivered

**Evidence:**
- runner.py:927 sets `self._cur_world, self._in_predictor_io = i, True` BEFORE `if self._proc is None:
  self._start_worker()` (runner.py:928-929).
- At world 0, `_proc` is always None:
  - prepare() stops its probe child and nulls `_proc` (runner.py:694-695);
  - open() starts none (runner.py:739-774).
- So the post-key world-0 start (spawn, isolation probe, "go") always runs under the label "in predictor I/O, world 0".
- The package is imported only after "go" (runner.py:335-341).
- The world's (V, k, seed) is sent only at runner.py:931, which is Harmonia Addendum H's exposure point ("the first
  per-world predict send").
- The v9 self-test `v9_3_restart_failure_labelled_with_world` asserts exactly this label for a start failure at
  world 0. It is the first start, not a restart: fr.prepare(); fr.open(); `_start_worker` replaced; predict_all.

**Scenario:**
1. The key is proven and the marker is written.
2. At world 0 the spawn is slow (host load, antivirus scanning the new interpreter) and misses the 120 s probe answer
   (runner.py:785-786), or `Process.start()` raises OSError (runner.py:781, unguarded).
3. The run aborts with `{phase: OPEN, current_world: 0, in_predictor_io: true, n_predictions_recorded: 0,
   error_type: PredictorChildFailed}`.
4. The truth is pre-exposure infrastructure: VOID under Addendum H Clarification 1. The label says the failure was
   inside predictor I/O for world 0, which reads as post-exposure and package-side (FORFEIT under Clarification 2).

**Why only should-fix:**
- The truth can be recovered by reading the code: `PredictorChildFailed` or `ChildNotIsolated` together with
  `current_world == 0` and `n_predictions_recorded == 0` can only come from the world-0 `_spawn_probe`.
- The package cannot trigger this path, because none of its code has run.
- It is the mirror of V8-3, which was graded should-fix.
- But Addendum H makes labels evidence only once "a governing audit has found that label truthful". This label is not
  truthful, and the self-test certifies the wrong semantics.

**Fix:**
- Record exposure explicitly, for example `delivered: bool` set True right after a successful `predict` send;
- or use a distinct `phase`/`where` value (`child_start`) for a start or probe failure;
- or set `in_predictor_io=True` for a restart only when a previous child has actually run package code.
- Change `v9_3_restart_failure_labelled_with_world` to cover a real respawn (after a per-world crash), and add a
  first-start case that asserts `delivered == false`.

### S-B (should-fix): FIREWALL.md v9 "Windows poll timing: ... A per-world poll failure is a per-world status" is false in the code

**Evidence:**
- `self._conn.poll(...)` is still outside every try (runner.py:938). Only `_recv` (runner.py:941-945) and message
  handling (runner.py:948-969) are guarded.
- On Windows, `PipeConnection._poll` calls `_winapi.PeekNamedPipe`, which raises BrokenPipeError when the child end
  is closed and nothing is buffered. This is PLAUSIBLE, from CPython; it cannot be verified from the repo.
- So a child that exits (for example `raise SystemExit` in predict(): `SystemExit` is not a forbidden name, and the
  worker catches only `Exception`, runner.py:350) gives a RUN-LEVEL abort, not a per-world status.
- This is the v8 replica-1 V8-4 note, still unfixed. v9 now documents the opposite of what the code does.

**Impact:**
- Labels are truthful here (world i, in_predictor_io true), and post-exposure is FORFEIT anyway, so the package gains
  nothing.
- But a declared statement under audit is inaccurate, and a whole run is lost to a per-world event.

**Fix:** move the poll inside the per-world guard (a `(OSError, EOFError)` there means PREDICTOR_CRASH), or correct
the FIREWALL.md sentence. M1 can settle the Windows behaviour with the existing "pipe close" test using a package that
exits without sending first.

### S-C (should-fix, carried from v8 V8-5 and replica-2 V8-4): a consumed release can still end without a sealable terminal record, and no tool closes it

1. **The abort append itself fails.**
   - Examples: disk full, or a transient Windows sharing-violation lock by AV, backup or indexer software that also
     caused the preceding append failure.
   - `abort()` raises from `self.receipts.append("abort", ...)` (runner.py:819), and run_all propagates it
     (runner.py:846).
   - The chain verifies, because repair keeps disk equal to memory, but it has no terminal record, so result-seal
     refuses (custody.py:244-245).
   - The declared crash residual (FIREWALL.md:311-316) names "disk full while writing the abort" as outside the
     runner's control. It does not say the PACKAGE can cause it: the child account can fill the shared C: volume
     from its own profile once the AST heuristic is bypassed, which is a declared heuristic. v8's added residual
     (FIREWALL.md:332) lists memory and compute pressure only.
2. **RESULT.json write failure after `close` or `abort`.**
   - result-seal needs RESULT.json with a matching head (custody.py:252-254).
   - After a close, run_all's abort returns `{"status": "CLOSED"}` (runner.py:807-808), and `_run_cli` then raises
     KeyError on `res["chain_head"]` (runner.py:1154).
   - Declared in v9 notes (FIREWALL.md:351), with no tool.
3. **A KeyboardInterrupt between `os.replace` (runner.py:389) and the assignment `self.receipts = ...`
   (runner.py:769).** This leaves a marker with no terminal record. Operator or OS only; a tiny window.

**Fix (single):** a custodian `seal-terminal` tool, run through entry.py. It appends `abort` to a verifying
unterminated chain and rebuilds RESULT.json from the receipts. This closes the whole class. Also add package-caused
disk exhaustion to the declared residuals, with a disk quota on the child account or a separate volume for the runs
root as mitigation.

### N-1 (note): abort() ignores repair()'s result

`self.receipts.repair()` (runner.py:813) returns False when the file cannot be opened or does not start with the
expected bytes. abort then appends anyway, so a torn tail left by a failed repair gets the abort line glued onto it.
The whole file becomes unverifiable (`verify_receipts` raises ValueError on the merged line, runner.py:439-444).

This needs a repair failure followed by a successful append, which is a transient condition only.

**Fix:** if `repair()` is False, retry, and never write the terminal record after unexpected bytes.

### N-2 (note): the post-key world-0 start is still a refusing probe after the key read

`_start_worker` re-probes the key path, the secrets and the REAL receipts (runner.py:875-879, 1146). The results
should equal prepare()'s stand-in results:
- receipts.jsonl is created by tmp and rename in the same directory as the stand-in (runner.py:384-389), so it gets
  the same inherited ACL;
- the key has already been deleted, so it reads "missing".

Its refusal is a sealed abort, declared since v7 (FIREWALL.md:304). It is also the trigger for S-A.

### N-3 (note): stale attribution values outside the predict phase

- An abort in the SEALED phase (certify) reports `current_world = N-1` (last set at runner.py:927) and the exit code
  of the predict worker that was stopped normally (runner.py:893, 987). That code is usually 0.
- An abort at `key_path.unlink()` (runner.py:772-773) reports the exit code of the PRE-KEY probe child (runner.py:694).
- `v9_3_child_exitcode_recorded` tests exactly the certify-phase case and asserts only `is not None`.
- `phase` disambiguates these cases. Better: clear `_cur_world`, `_in_predictor_io` and `_last_exitcode` when leaving
  predict_all, and in open().

### N-4 (note): custody lock left stale on a malformed custody key

See 1 item 1(c) (custody.py:202, 210). Fails closed.

### N-5 (note): custody `_test_decrypt` reads by ref name, not the gates' resolved commit

`_test_decrypt` reads `self.ref` again by name (custody.py:173-174) instead of the commit that the gates resolved.
The seal is pinned by spec_id, so a moved ref cannot change the result in a way that matters. This is TOCTOU hygiene
only.

## 3. Per-claim verdicts (brief claims 1-6)

| # | claim | attacks tried (≥2) | verdict |
|---|---|---|---|
| 1 | Opacity | (a) A new public field or receipt field carrying hidden content: v9 adds `child_exitcode` and `current_world` (indexes and ints) to the abort (runner.py:819-823) and nothing world-derived. The open record is built pre-key from public inputs only (runner.py:699-715). (b) Refusal text after decryption: HiddenSetMismatch messages carry type names and fixed text only (runner.py:755, 759, 767). (c) Timing: key proof time is constant for a fixed set. The N-1 timing residual is declared (FIREWALL.md:254). | **HOLDS** (plaintext length is visible, declared) |
| 2 | Secrets never in git | (a) Full-history name scan: no key, salt or plain file (section 0). (b) v9 custody writes the key only to `dest` after the proof (custody.py:202-208). The runner writes no plaintext. The key-holder scan cannot be run here. | **HOLDS** from the repo. The key-holder booleans are CANNOT-VERIFY: Nestor's `entry.py firewall-check` on M1 settles them. |
| 3 | Enforced order | (a) Records are unauthenticated: S1 (FIREWALL.md:156-158, 338). A main pusher can forge the audit, commitment or designation records; the allow-list sender is client-supplied. (b) Code binding: unchanged since v8 (protocol.py:534-546). v9 changes are in AUDITED_FILES (protocol.py:76-82), so any v9 edit makes an audit stale. (c) Runner and custody refuse before the key: gates run in prepare() before the read (runner.py:656-659), and custody gates run before `read_hex_file` (custody.py:195-202). | **BROKEN: S1 (declared OPEN, operator #925), blocks-PASS.** Everything else HOLDS. |
| 4 | Controlled reveal | (a) Release without a proven key: fixed (custody.py:202-203). (b) Reveal or result-seal of an unterminated chain: refused (custody.py:244-245, 278-279). (c) Once-only records: unchanged since v8. | **HOLDS** (S1 caveat as in 3; S-C for liveness) |
| 5 | Predictor isolation | (a) Pickle: the pipe is JSON plus npy with `allow_pickle=False` (runner.py:170-206). (b) Error replies: type name only (runner.py:955-956). (c) The key is deleted before any post-key child (runner.py:772-773, then 928-929). (d) A same-account child is always refused (declared). A separate-account launcher does not exist yet (V7-E, declared). | **HOLDS** as declared (heuristic AST; the account residual) |
| 6 | Draw integrity | draw.py, sealbox.py and verify_reveal.py are unchanged since v8. Their hashes are bound by AUDITED_FILES. The manifest and ciphertext are unchanged. | **HOLDS** (carried from v8; single-draw provenance is a custodian statement, declared) |
| v9 | No recoverable error consumes the release without a verifiable terminal record | the key proof (item 1), the torn write (item 2), the abort-append failure, the RESULT write, the KeyboardInterrupt window (S-C), and a repair failure (N-1) | **HOLDS for recoverable argument, key and ordinary I/O errors.** Residual S-C (should-fix; environment or package disk pressure; no seal-terminal tool). |
| v9 | Post-key attribution labels truthful | first start (S-A), the Windows poll (S-B), stale fields (N-3) | **BROKEN** (S-A should-fix; S-B should-fix) |

## 4. The mandatory classes

1. **Unbound code with secrets:**
   - No change to entry.py or the guard; v8 findings carry.
   - The v9 edits sit in bound files.
   - F-3P (site-packages, `.pth`) is declared.
2. **Same-account readability:** declared. The same-account child is always refused at preflight.
3. **AST bypasses:** `raise SystemExit` and `exit` are not flagged (feeds S-B). The audit is heuristic by
   declaration; the pipe does not depend on it.
4. **Git ref ambiguity and history simplification:** unchanged since v8, HOLDS.
5. **Unauthenticated or rewritable records:** S1 OPEN (blocks-PASS, declared). Branch protection is off (declared).
6. **Public fields narrowing hidden content:** the new abort fields are indexes and exit codes only. Wall-clock
   timing is declared.
7. **Spoofable host or identity checks:**
   - `socket.gethostname()` goes into the open record (runner.py:704).
   - Host designation is unchanged since v8. Same-account spoofing sits within the account residual.

## 5. Declared residuals

- **Key holder not bounded; AST not a sandbox; single-draw provenance; System interface exposes physics:**
  acceptable as declared.
- **Crash-after-release (FIREWALL.md:311-316):** acceptable only once it (i) states that the package, through the
  child account, can cause disk exhaustion (S-C), and (ii) a seal-terminal tool exists. Otherwise "no recovery path"
  covers events that are recoverable in practice (for example a transient AV lock).
- **v9 notes (FIREWALL.md:350-352):**
  - The poll note is inaccurate (S-B).
  - The RESULT.json note is accurate but has no tool (S-C).
  - The released-key-after-abort note is acceptable.
- **Missing from the list:**
  - the world-0 start mislabel (S-A);
  - package-induced disk pressure (S-C);
  - a stale custody lock on a malformed custody key (N-4).

## 6. Blocks-PASS findings

- **S1: records are unauthenticated** (declared OPEN, operator #925). No other blocks-PASS finding in the v9 scope.

## OVERALL: FAIL

- The only blocker is S1, which is declared open.
- Excluding S1 and the declared host capabilities, v9 repairs the v8 blockers.
- The remaining items are should-fix: S-A (first-start label untruthful), S-B (poll claim false), S-C (no
  seal-terminal path; disk pressure undeclared).
