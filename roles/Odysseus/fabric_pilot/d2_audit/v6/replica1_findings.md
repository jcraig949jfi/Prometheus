# Holdout D2 firewall re-audit v6: adversarial findings (task tsk-76beeeeab3ae, attempt att-ee590b1f29e3)

- **Audited commit:** 7c7b0b8361a54b2e8088960c1ae8a7a055b64db9 (read-only checkout). The v6 code is from ab2a3efcb.
- **Method:** static reading only. I could not run code: Bash was denied except for `rogit`. Neither self-test was
  executed by me.
- **Scope:** the firewall layer. No law, prediction or science content was read or needed.
- **v6 focus from the brief:** (a) any path on which a recoverable error happens AFTER the key is read or the release
  is consumed; (b) satisfying custody's preflight requirement without a real passing preflight.

## Summary

| # | finding | severity |
|---|---|---|
| V6-1 | A hostile reply shape from the predictor crashes the runner after the key is consumed. The package can decide to do this after it has probed the hidden worlds, which gives it an option to abort the evaluation. | **blocks-PASS** |
| V6-2 | The package is extracted (staged) only AFTER the key is read and deleted. Member names that pass validation but cannot be written raise an uncaught OSError after the release is consumed. | **blocks-PASS** |
| V6-3 | The run-time isolation probe (read and append on `receipts.jsonl`) runs only AFTER the key is read. The preflight cannot cover it, because that file does not exist yet at preflight time. | **blocks-PASS** |
| V6-4 | The PREFLIGHT record is a plain, self-reported JSON file. Anyone who can write the out root can forge it, including the non-custodian runner account. The self-test forges it itself. | should-fix |
| V6-5 | RUN_OUT_ROOT holds both runner-written files (run directories, PREFLIGHT records) and the custodian's trust store (ALLOWLIST.json, custody.jsonl, custody.lock). A second account must be able to write there. | should-fix (M1 ACL: CANNOT-VERIFY) |
| V6-6 | Missing residual: there is no resume. ANY crash after the key is read permanently deadlocks the spec_id (OOM, power loss, disk full, a transient spawn failure). | note / declare |
| - | S1 (#925) and branch protection are still OPEN, as the brief declares. | known |

---

## V6-1: a hostile reply shape crashes the parent after the key is consumed (blocks-PASS)

**Evidence**
- The parent parses every child message with `_recv` (`runner.py:199-200`). That returns ANY JSON value: an int, `[]`
  or a dict.
- Only the `_recv` call is inside the try (`runner.py:772-776`). The shape accesses that follow are outside any
  handler:
  - `msg[0]` (`runner.py:777`);
  - `msg[1]` (`runner.py:783`, `:788`).
- A message of `5` raises TypeError. A message of `[]` raises IndexError. A message of `{}` raises KeyError. So does
  `["done"]`.
- `predict_all` has only a `finally` (`runner.py:801-808`), and `main` catches only `RunnerRefusal` / `GateRefusal`
  (`runner.py:939`). The exception therefore becomes a traceback.
- The package can reach the raw pipe. `_HiddenWorldStub` stores it as `self.__conn` (`runner.py:217-218`), which Python
  name-mangles to `_HiddenWorldStub__conn`.
- The AST audit does not flag that name:
  - it flags only attributes that start AND end with `__` (`runner.py:444-446`);
  - it flags only names that start with `__` (`runner.py:447`);
  - `send_bytes` is not in `FORBIDDEN_ATTRS` (`runner.py:109-112`).
- v4 claimed "hostile reply shapes ... are caught as PREDICTOR_CRASH" (FIREWALL.md:205). That covers decode errors
  only, not the shape of a message that decodes.

**Scenario**
1. Cosmos commits a package whose `predict` does the following:
   - probes the world through the System interface, as the contract allows;
   - if a condition on what it learned holds, runs `system._HiddenWorldStub__conn.send_bytes(b"5")`;
   - returns a valid prediction.
2. It passes the hash, member, metadata and AST checks and the preflight.
3. The custodian releases the key. The runner reads and DELETES it (`runner.py:612-614`), creates `run_<nonce>`
   (`:643`), writes the open receipt and starts predicting.
4. At the chosen world the parent raises TypeError at `:777`.

**Result**
- The key copy is gone and `run_<nonce>` exists, so a rerun is refused (`runner.py:950-951`).
- The KEY_RELEASED record and the custody log refuse a second release (`custody.py:186-189`).
- The spec_id is permanently deadlocked, and no result is ever produced.
- Because the trigger can depend on hidden-world physics observed through the interface, this gives the adversary an
  option to void an unfavourable evaluation after seeing the data. That is the cherry-picking harm that S4 was meant to
  close.

**Fix**
- Validate the message shape inside the handled region. Any non-list, a wrong length or an unknown tag must give
  PROTOCOL_ERROR. The `_send` in the error path (`runner.py:782`) must also be guarded, because a child that has
  exited makes it raise OSError.
- Treat EVERY exception in `_predict_one` after the key is read as a recorded per-world status, never as a crash.
- Add a self-test with a package that sends `5`, `[]` and `["done"]` over the mangled attribute.
- Consider flagging `_<Class>__` mangled names in the AST audit (defence in depth only).

## V6-2: extraction (staging) happens after the key is read and deleted (blocks-PASS)

**Evidence**
- `validate_package()` calls `load_package(..., extract_to=None)` (`runner.py:685-689`). That checks only the
  following (`runner.py:466-470`):
  - no leading `/` or `\`;
  - no `..` part;
  - no `:`;
  - the suffix is .py, .json or .txt.
- These are all checked, but the actual extraction happens after `key = read_hex_file(...)` and `unlink()`
  (`runner.py:612-614`), after `self.out.mkdir` (`:643`), at `load_package(..., self.out / "package", ...)`
  (`:646`), where the members are written (`:500-505`).
- The v5 verdict asked for this step explicitly: "hash, validate, audit and **stage** the package ... BEFORE the key is
  read" (roles/Odysseus/fabric_pilot/d2_audit/v5/VERDICT.md:35-37).

**Scenario** (any one is enough; each package passes `validate_package`, the AST audit and the preflight)
- (a) Members `a.txt` and `a.txt/b.txt`. Depending on order, extraction raises one of:
  - FileExistsError from `p.parent.mkdir(..., exist_ok=True)` onto a file;
  - NotADirectoryError;
  - IsADirectoryError / PermissionError from `write_bytes` onto a directory.
- (b) On M1 (Windows), a member `q?.txt` or `a|b.py` raises OSError EINVAL. `<>|?*"` are not rejected; only `:` is.
- (c) A member whose name component is 300 characters long raises ENAMETOOLONG on Linux, or a path/length error on
  Windows.
- (d) Windows case folding: `A.txt` and `a.txt/x.txt` behave like (a).

**Result**
- Each is an OSError, which is not a RunnerRefusal. It is raised with the key already deleted and `run_<nonce>`
  already created, so the deadlock is the same as in V6-1.
- The package is Cosmos's, so the adversary can trigger this deliberately.
- The v6 tests use only a wrong hash and an AST-flagged package (`selftest_protocol.py:928-953`). Both fail at
  validation, so this case is untested.

**Fix**
- Extract into a staging directory BEFORE the key is read, then move or rename it into `run_<nonce>`. Alternatively,
  validate names strictly: a safe character class, a length cap, and no file/directory or case-folded collisions.
- Add the three packages above as refusal-before-key tests.

## V6-3: the run-time isolation probe runs after the key is read (blocks-PASS)

**Evidence**
- `open()` runs `preflight()` before the key is read (`runner.py:610-611`). That preflight probes:
  - the read paths;
  - mkfile in `out.parent`;
  - an EMPTY write-probe list (`runner.py:707`).
- `receipts.jsonl` is among the read paths (`extra_probe_paths`, `runner.py:957`), but it does not exist yet. It
  reports "missing", which passes (`runner.py:680`).
- The full probe runs in `_start_worker` (`runner.py:712-716`, `write_probe_paths`, `:563-564`). It re-checks read
  access to the now-existing `receipts.jsonl` and APPEND access to it, from `predict_all`, which is after the key is
  read and deleted, the run dir is created and the open receipt is written.

**Scenario**
- On POSIX with the default umask 022, `Receipts(create=True)` makes `receipts.jsonl` mode 0644 (`runner.py:358`), and
  the run dir 0755.
- A correctly separated child account cannot create files in the out root, so the preflight passes.
- That account CAN read `receipts.jsonl`, so `_spawn_probe` raises ChildNotIsolated (`runner.py:681-683`) after the
  release is consumed.
- On Windows the same happens whenever the out root carries an inheritable read ACE for the child account or a group it
  belongs to, for example Users:(OI)RX without directory write.

**Result**
- The deadlock is the same as in V6-1. The trigger here is configuration, not the adversary.
- This fails the v5 condition "Every package check and every probe completes BEFORE the key is read"
  (v5 VERDICT.md:69-70).

**Fix**
- Create `run_<nonce>` and an empty `receipts.jsonl` with the run's real ACL/mode, and run the FULL probe (read +
  append + mkfile) BEFORE the key is read.
- Or make the run-time probe a pure re-assertion whose failure leaves the key re-usable. That is not possible after
  `unlink`, so the probe must move.

## V6-4: the preflight requirement is satisfiable without a preflight (should-fix)

**Evidence**
- `protocol.preflight_ok` (`protocol.py:263-274`) reads `PREFLIGHT_<nonce>.json` from RUN_OUT_ROOT and compares
  self-reported fields.
- Nothing in the record is bound to an actual probe or to the host:
  - no probe results;
  - no hash of the validated package bytes beyond the committed hash that is already public;
  - no host check;
  - no signature or MAC.
- The runner writes the record with a plain `write_text` (`runner.py:691-698`).
- The v6 self-test "passes" the release by hand-writing exactly such a JSON (`selftest_protocol.py:964-975`). That
  demonstrates the forgery.
- Anyone who can create files in RUN_OUT_ROOT can do the same, beyond the custodian account. That includes the
  designated RUNNER account, which is a different account and must be able to write there, because its run dirs and
  the preflight record live there (`runner.py:83`, `:962`).

**Impact**
- Limited. `open()` re-runs the preflight before the key is read (`runner.py:610-611`), and a failure there leaves the
  released copy in place.
- A forged record therefore only lets custody spend the once-only release before a real preflight. It does not by
  itself cause key exposure.
- However, V6-2 and V6-3 show that the in-run checks before the key are incomplete, so the custody gate is currently
  advisory, not a guarantee.

**Fix**
- Record the probe results and the host in the preflight record, and have custody compare the host.
- Consider having custody re-run a package validation itself. It is the custodian's own process, so it can run
  `validate_package` on the committed package without the key.

## V6-5: the out root is shared by the runner account and the custodian's trust store (should-fix; M1 ACL CANNOT-VERIFY)

**Evidence**
- `DEFAULT_ALLOWLIST` and `RUN_OUT_ROOT` are the same directory `C:/Users/jcrai/nestor_receipts/holdout_D2`
  (`protocol.py:57-58`, `entry.py:57`).
- CUSTODY_LOG and `custody.lock` are there too (`custody.py:42`, `:141`).
- v6 requires the runner account, which by design is not the custodian (FIREWALL.md:139), to create
  `PREFLIGHT_<nonce>.json` and `run_<nonce>` in that directory.

**Scenario**
- With directory-level create rights, the runner account can do the following:
  - create `custody.lock`, blocking release and reveal (DoS, fails closed);
  - create ALLOWLIST.json if it does not yet exist;
  - on POSIX with write on the directory, or on Windows with inherited Modify / delete-child, replace ALLOWLIST.json,
    which is the S1 trust store.
- That is a second account able to write the allow-list: a widening of S1 across accounts, beyond the declared
  same-account residual.

**Settle:** the M1 ACL of that directory once the runner account exists. Better, move the preflight records and the
run dirs to a separate directory from ALLOWLIST.json and the custody log.

## V6-6: missing residual, no recovery after the key is read (note)

- Resume is refused (`runner.py:584-585`) and the key is deleted at `:614`. After that point:
  - an OOM kill;
  - a power loss;
  - a full disk during certification;
  - a transient `PredictorChildFailed` in `_start_worker` (`runner.py:673-679`; it passed the preflight but can still
    fail at run time)

  each permanently deadlock the spec_id.
- The predictor child also has no resource limits. A package that exhausts host memory can get the parent killed (the
  same effect as V6-1, but platform-dependent).
- This is not in the declared residuals. It should be declared, together with the operator's recovery procedure
  (successor seal D3).

---

## Per-claim verdicts

### Claim 1: Opacity. HOLDS (not re-attacked in depth; unchanged since v5)
- **Attack: public fields narrowing hidden content.** The manifest (`MANIFEST_D2.json:1-36`) carries the IV, the
  hashes, the commitment and versions. It carries no world, knob, seed or nonce. `ciphertext_bytes: 17227`
  (`:5`) reveals the plaintext length; that is declared (FIREWALL.md:149, 257).
- **Attack: brute force of the commitment.** The commitment is salted with 32 random bytes
  (`sealbox.py:52-53`, `:64-67`). It cannot be brute-forced without the salt.
- **Attack: the cipher.** `decrypt` binds the AAD (`sealbox.py:76-80`).
- **Attack: receipts carrying hidden values.** The receipts carry `world_tag = HMAC(key, …)` (`runner.py:622-623`) and
  omit the system name (`runner.py:528-533`).
- The timing side channel is declared (FIREWALL.md:254).

### Claim 2: Secrets never in git. HOLDS for what the repository can show; the key-holder scan is CANNOT-VERIFY
- **Attack:** `rogit log --all --diff-filter=A --name-only -- prometheus/cosmos/c3_holdout_D2` lists only code, docs,
  the manifest, `hidden_D2.enc` and the selftest JSONs. There is no `*.key*`, `*.salt*` or `*.plain*` file.
- **Attack:** a full-content secret scan needs the key, so it is CANNOT-VERIFY from the repository.
  `firewall_check` booleans from M1 would settle it.

### Claim 3: Enforced order. HOLDS for the order itself, except S1 (OPEN, declared)
- The runner and custody re-check the gates before the key (`runner.py:588-591`, `custody.py:185`).
- The v6 once-only logic is unchanged (`custody.py:186-189`).
- **Attack:** a forged governing record. Still possible, because the records are unauthenticated: that is S1, which is
  declared.
- I did not re-attack `check_gates` internals beyond v5; nothing in v6 changed them in a way I found exploitable.
- V6-5 widens S1 to a second account, depending on the M1 configuration.

### Claim 4: Controlled reveal / key release. BROKEN (V6-2, V6-3; V6-4, V6-5 should-fix)
- **Attack:** make the release be consumed by a recoverable error. It succeeds three ways: V6-1, V6-2 and V6-3.
- **Attack:** satisfy the preflight requirement without a preflight. It succeeds (V6-4).
- The key file ACL and the destination checks are unchanged from v5 (`custody.py:114-169`).

### Claim 5: Predictor isolation. BROKEN (V6-1)
- **Attack:** a hostile message shape on the pipe crashes the parent, which is not isolated from the child's protocol
  errors (V6-1).
- **Attack:** raw pipe access from the package through the mangled name. The AST audit misses it
  (`runner.py:444-447`).
- The pickle-free codec itself holds (`runner.py:167-200`), and error replies to the child are type names only
  (`runner.py:781-782`).

### Claim 6: Draw integrity. HOLDS (not re-attacked; unchanged since v5)
- `d2_src_sha256_at_draw` is present in the manifest (`MANIFEST_D2.json:11-15`).
- Single-draw provenance is a custodian statement (declared).

### Self-tests: CANNOT-VERIFY (not executed by me)
- The committed `SELFTEST_PROTOCOL.json` reports:
  - `selftest_pass: true` (`:184`);
  - `v4_DEST_key_acl_restricted: true` (`:79`);
  - the v6 checks true (`:123-128`).
- None of them exercises V6-1, V6-2 or V6-3.

## Declared residual risks

- **The gates are not a boundary against the key holder.** Acceptable as declared.
- **The package is Python running as an operator account; the AST audit is a heuristic.** Acceptable as declared.
  V6-1 shows a practical bypass that matters for availability.
- **Single-draw provenance.** Acceptable.
- **The System interface exposes physics.** Acceptable. Note, however, that combined with V6-1 it turns into a
  selective-abort capability.
- **Missing:**
  - V6-6 (no recovery after the key is read);
  - V6-5 (a second account writing next to the trust store);
  - the preflight record being self-reported (V6-4).

## Classes checked

| class | result |
|---|---|
| 1. Unbound code | entry/guard unchanged from v5; no new import path found in v6 |
| 3. Static-audit bypass | mangled private attribute (V6-1) |
| 5. Unauthenticated records | S1; PREFLIGHT (V6-4); co-location (V6-5) |
| 6. Public-field narrowing | length and timing, both declared |
| 7. Host/identity spoofing | the preflight record has no host binding (V6-4) |

## OVERALL: FAIL

The blocking findings are V6-1, V6-2 and V6-3: the one-time release can still be consumed and then deadlocked by
recoverable errors after the key is read. The first two can be triggered by the adversary's package.
