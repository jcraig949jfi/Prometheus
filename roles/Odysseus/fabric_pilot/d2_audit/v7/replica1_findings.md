# Holdout D2 firewall re-audit v7: adversarial findings

- **Auditor:** independent replica (audit.security.adversarial v1), task tsk-24ad3df260b9, attempt att-dd0e9cfa7632.
- **Audited commit:** e4efb487e (merge). The c3_holdout_D2 package was last changed at bfcd26e3c ("D2 v7").
- **Scope:** the firewall layer only: custody, opacity, commitments, enforced order, leak behaviour. No law or science.
- **Method:** read-only repository reading plus `rogit` history. I did not execute any code: the self-tests,
  `entry.py gates SEAL` and `protocol --code-hashes` were NOT run by this replica. Every "PLAUSIBLE" item below
  needs a self-test to confirm it.

## Verdict summary

| # | claim | verdict |
|---|---|---|
| 1 | Opacity | HOLDS (plaintext length is visible; already declared) |
| 2 | Secrets never in git | HOLDS for what the repo can show; the key-holder scan is CANNOT-VERIFY-FROM-REPO |
| 3 | Enforced order | **BROKEN**: S1 is open, so records are unauthenticated (known, #925). Everything else in the gate logic holds on reading |
| 4 | Controlled reveal | HOLDS in code, subject to S1. See V7-C: some aborted runs cannot be result-sealed |
| 5 | Predictor isolation + the v7 "nothing refusable after the key; every package-induced end is sealed and attributable" | **BROKEN** (V7-A, V7-B) |
| 6 | Draw integrity | HOLDS for the code hashes; single-draw provenance is CANNOT-VERIFY (declared) |

**OVERALL: FAIL.** S1 blocks the PASS on its own. Apart from S1, two new v7 findings block the PASS (V7-A, V7-B).

---

## v7-specific findings

### V7-A (blocks-PASS). The READ half of the receipts probe still runs only after the key read

**Claim under test.** FIREWALL.md:294 says prepare() probes "a receipts STAND-IN in the run directory (read +
append)". FIREWALL.md:304 says the stand-in "is read/append-probed in prepare()". The v6 verdict's condition 1 was
"run every isolation probe, including an equivalent of the receipts probe, BEFORE the key is read".

**Code.**
- In prepare(), the stand-in is passed ONLY as a write path: `self._spawn_probe("", "", self.probe_paths,
  [str(stand)], dirs)` (runner.py:643). `_probe_write` opens it with `"ab"` only (runner.py:255).
- The read paths in prepare() are `probe_paths` = key, secret paths and `extra_probe_paths`
  (runner.py:574). The CLI sets `extra_probe_paths=[out/"receipts.jsonl"]` (runner.py:1058). At prepare() time
  that file does not exist, so its read probe returns `"missing"`, which is accepted (runner.py:726).
- After the key read and the open record (runner.py:677-681), `predict_all -> _predict_one -> _start_worker ->
  _spawn_probe` read-probes the real, now-existing receipts.jsonl (runner.py:800, 849). If the file can be opened,
  the result is `ChildNotIsolated`, which becomes a sealed abort (runner.py:727-729, 765-768).
- The self-test `v7_1_receipts_standin_probed_before_key` uses a same-account child, which the APPEND probe already
  refuses (selftest_protocol.py:1045-1051). It never exercises the read half.

**Scenario (environment-controlled, deterministic).**
1. The host capability arrives: a separate child account. That account must READ the staged package at
   `<RUN_OUT_ROOT>/run_<nonce>/package`. No code sets an ACL on that directory, so it inherits from the run directory.
2. The natural host set-up is an inheritable read/execute grant for the child account on `RUN_OUT_ROOT`, with no
   write access.
3. prepare() passes: the stand-in APPEND is denied, receipts.jsonl is "missing", and mkfile is denied.
4. open() reads the key, writes receipts.jsonl and the open record (consumption), and deletes the key copy.
5. The first `_start_worker` read-probes receipts.jsonl and gets `"opened"`. The result is ChildNotIsolated, then a
   sealed abort.
6. The release is spent. No second release and no resume are possible (FIREWALL.md:314-316), so D2 is spent before
   any prediction is made.

This is exactly the v6 item-2 class (a refusable probe after consumption). The v7 documentation claims it is closed,
and it is not.

**Fix.** Add `str(stand)` to the READ paths of the prepare() probe, which becomes
`self._spawn_probe("", "", self.probe_paths + [str(stand)], [str(stand)], dirs)`. Add a positive control in which
the child can read, but not append to, the run directory.

### V7-B (blocks-PASS). A package can deterministically turn its own action into a RUN-level abort that reads as an infrastructure pipe failure

**Claim under test.** FIREWALL.md:305 (3a) says "ANY malformed or unexpected child message, or a failed reply, is
that world's PROTOCOL_ERROR: recorded, sealed with the predictions, and the run continues." The v6 verdict's
condition 2 requires "a sealed, attributable outcome".

**Code.**
- In `_predict_one`, the request `_send(self._conn, ["predict", i, ...])` is OUTSIDE the per-world `try`
  (runner.py:850). Only the reply send is inside it (runner.py:864-885).
- A `BrokenPipeError` or `OSError` raised there propagates out of `predict_all` (runner.py:894-901) into
  `run_all`'s `except BaseException`, which calls `abort(e)` (runner.py:765-768).
- The abort record carries only `phase`, `error_type`, `n_predictions_recorded` and `utc` (runner.py:744-745). It
  records no child exit code, no last child message and no marker that the failure happened on predictor I/O.

**AST-clean package (no `--allow-flagged`).** Nothing below is flagged by `audit_source` (runner.py:417-453):
`operator` is not a forbidden module, `attrgetter`, `send_bytes` and `close` are not forbidden attributes, and the
private name is a string constant, not an `ast.Attribute`.

```python
import json, operator
_n = [0]
def predict(system, task, seed):
    i = _n[0]; _n[0] += 1
    if i == 40:                                   # any world the package chooses, after probing worlds 0..39
        c = operator.attrgetter("_HiddenWorldStub__conn")(system)
        c.send_bytes(json.dumps(["done", i, {"class": "NONE", "intervention": {"class": "NONE"}}]).encode())
        c.close()
        raise ValueError                           # the child's _send(["fail"]) on the closed conn raises -> child exits
    ...
```

**What happens.**
1. The parent receives a valid `done` for world 40 and records it as OK (runner.py:874-878, 899).
2. For world 41, the self-sent request `_send(["predict", 41, ...])` hits the closed peer: EPIPE on a Linux
   socketpair, ERROR_NO_DATA on a Windows named pipe. Both raise `BrokenPipeError`.
3. The result is `abort` with `error_type: "BrokenPipeError"` and RESULT ABORTED.

The package has seen worlds 0..40 through the System interface. It has turned a per-world event into a run-level stop,
at a point it chose, and the record reads as a transport failure. Harmonia Addendum E (9f6abdce6) returns VOID for
"infrastructure crashes ... with their evidence" and FORFEIT for package-attributable ones. The runner records none of
the evidence needed to tell the two apart. This is the v6 "option to discard" in a weaker form: sealed, but with its
attribution left to argument. The committed control `HOSTILE_PIPE_PREDICTOR` (selftest_protocol.py:985-990) sends
garbage but never closes the connection, so it misses this path.

**Fix.**
- Put the request send, and `_start_worker`, inside the per-world handling: any send failure becomes that world's
  `PREDICTOR_CRASH`, followed by a worker restart.
- In every abort, record whether the failure arose on predictor I/O, plus the child's exit code and the last child
  message kind, so that Addendum E can attribute it.
- Add a control that closes the connection.

### V7-C (should-fix; PLAUSIBLE, needs a self-test). A failure while writing the OPEN record leaves an abort as record 0, a chain that never verifies, and a run that cannot be result-sealed

**Code.**
- `Receipts(rpath, genesis, create=True)` creates receipts.jsonl, the consumption marker (runner.py:679).
- Next, `append("open", body)` computes `record_hash` through `canon_bytes` (runner.py:681, 351-352). If that raises,
  `run_all` calls `abort()`, because `self.receipts` is not None. abort() then appends `"abort"` as seq 0
  (runner.py:744).
- `verify_receipts` requires record 0 to be `"open"` and otherwise returns "bad open record" (runner.py:401-403).
- custody `result-seal` and `reveal`, and evidence, all refuse a chain that does not verify (custody.py:231-232,
  265-266; evidence.py:57-59).
- The result: receipts exist (no rerun, runner.py:631, 1051), KEY_RELEASED is committed (no second release), and no
  seal can be made. This is a deadlock with no sealable outcome.

**Package-controlled trigger (PLAUSIBLE).**
- The open body embeds the package's `meta` verbatim, including the free-form `adjudication` JSON
  (runner.py:688, 496).
- `meta` is parsed once, before the key, by `json.loads` (runner.py:488), but is never re-encoded before the key.
- In the open record it sits 3 container levels deeper (record -> body -> package -> meta).
- An `adjudication` value nested just under the C recursion limit therefore parses at validation and raises
  `RecursionError` in the post-key `canon_bytes`.
- The manifest publishes the exact interpreter (3.12.10, Windows), so the depth can be tuned offline.

Non-package triggers of the same state: Ctrl-C, or an OSError reading `MANIFEST_D2.json` or `certify.py` for the
body (runner.py:683, 689-690), occurring between runner.py:679 and :681.

No hidden world has been served at that point, so the package gains no information. The v7 invariant ("after the open
record, every path ends in a terminal record custody can seal") still does not hold.

**Fix.**
- Canonicalise the full open body (at least `meta`) in `validate_package()`, before the key.
- In `abort()`, if no open record exists, write a minimal open record first, or seal an abort-only chain in a form
  that `verify_receipts` accepts.

### V7-D (note). The v7 AST private-attribute flag is bypassed trivially
`operator.attrgetter("_HiddenWorldStub__conn")`, as in V7-B, is not flagged. `faulthandler.dump_traceback_later(t,
exit=True)` is also unflagged and gives a timed hard exit of the child. Both are within the declared residual ("the AST
audit is a heuristic"). I list them because FIREWALL.md:305(d) presents the flag as a v7 repair. The real repair for
the pipe is V7-B's fix, not the flag.

### V7-E (note). The separate child account, the premise of the isolation boundary, has no code path
- The child is always started with `mp.get_context("spawn")` under the runner's own account (runner.py:713-716).
- There is no CreateProcessAsUser / LogonUser or equivalent anywhere in the package (grep for
  `CreateProcessAsUser|LogonUser|runas|set_executable|child_account` finds nothing).
- Every production run therefore fails closed at prepare(), which is declared. It also means the code that will
  actually run a real evaluation does not exist yet and will need its own audit. V7-A must be fixed before it.

### V7-F (note). A package can create memory or compute pressure in the parent; abort attribution is ambiguous
- `_serve` accepts a child-supplied `state` whose E dimension is unbounded (only the key set is checked,
  runner.py:837) and an `obs` of any length (the budget counts it only when `max_episode_steps` is set, runner.py:834).
- `predict_timeout` is checked only between calls (runner.py:853), so one call can run long.
- A child that sends `done` and then allocates heavily is still alive while the parent appends the receipt
  (runner.py:874-878, 899). A parent `MemoryError` there becomes an abort recorded as "MemoryError", which Addendum E
  would read as "out of memory not caused by the package" unless evidence says otherwise.
- On Linux the OOM killer could end the parent without a terminal record.
- Suggested bounds: E per call, obs length, and killing the child before any parent-side receipt write.

### V7-G (note). Post-key refusals that remain are infrastructure and sealed
Key-copy unlink failure, `InvalidTag` and `HiddenSetMismatch` (runner.py:696-708) all occur after the open record
and end in a sealed abort. This is acceptable under the declared policy. Validating the key against a GCM-authenticated
dummy before the marker would move InvalidTag earlier, if desired.

---

## Claims

### Claim 1: Opacity. HOLDS
Attacks tried:
- **Public manifest fields that narrow the plaintext.** The manifest (MANIFEST_D2.json) carries the IV, hashes,
  versions, draw time and `ciphertext_bytes` 17227, which gives the plaintext length (already declared,
  FIREWALL.md:149). There are no world, knob, seed or nonce fields.
- **Brute force of the commitment over the lattice.** The salt is 32 bytes from `secrets` (sealbox.py:52-53,
  64-67), so this is infeasible.
- **Leaks through receipts or errors.**
  - Prediction errors carry the child's own text (runner.py:347, 880). That is not secret-derived.
  - Parent-side serve errors are type names only (runner.py:871-872).
  - Abort carries the type name only (runner.py:744-745).
  - `CERTIFY_ERROR` is a type name only (runner.py:976-977).
  - `_summ` drops `system`, whose name encodes the knobs (runner.py:543-548).
- **Timing.** Declared (N-1).
- **Code-hash cross-check.** sha256(hidden_D2.enc) = f75ba333... and sha256(MANIFEST_D2.json) = 78874e9d...,
  matching the brief (computed with sha256sum).

### Claim 2: Secrets never in git. HOLDS (repo part); key-holder scan CANNOT-VERIFY
- `rogit log --all --name-status -- prometheus/cosmos/c3_holdout_D2` shows only code, docs, the manifest, the
  ciphertext and selftest JSON. The seal is 95b31a30d, the only adder of the .enc and the manifest.
- `rogit log --all --diff-filter=A` for `*.key.hex`, `*.salt.hex`, `*plain.json` and `*nestor_secrets*` returns
  nothing.
- `rogit diff a56ef7787 HEAD -- prometheus/cosmos/c3_holdout_D` is empty, so holdout D is byte-identical.
- The content-level scan (key/salt hex, base64, seed clusters) needs the key and is CANNOT-VERIFY-FROM-REPO. What
  would settle it: `entry.py firewall-check` booleans from M1, including `--all-history` and a comms dump.

### Claim 3: Enforced order. BROKEN (S1)
Attacks tried:
- **Shadow refs.** Tags or heads named origin/main or main are refused (protocol.py:301-311; entry.py:218-220).
- **Replacement through a merge, or rewriting.** `_added_once` checks the full history per parent
  (protocol.py:314-358).
- **Grafts or shallow history.** Refused (protocol.py:209-219).
- **GIT_* variables or replace refs.** Neutralised (protocol.py:185-191).
- **git.exe in the cwd.** git is run by absolute path (protocol.py:164-182).
- **Stale code.** The audit binds exactly AUDITED_FILES, checked at the committed tree, the working tree and the loaded
  closure (protocol.py:533-547).
- **Order by ancestry.** Each record must be a strict ancestor of the next (protocol.py:520-524, 558, 578, 605).

All of these hold on reading. **But** the records' AUTHORS are not authenticated:
- The allow-list trusts the comms `sender`, which the client supplies (FIREWALL.md:156-158).
- main is unprotected.
- Anyone who can push to main and get a hash into the allow-list through a forged comms sender can author an audit,
  commitment or designation.

This is **blocks-PASS** (known, S1, #925).

### Claim 4: Controlled reveal. HOLDS (subject to S1)
- **Key release.**
  - It requires the DESIGNATION gates, a fresh destination, the lock, both once-only checks (the log and git history),
    and a matching preflight.
  - The ACL is set before the key is written, and a failed release is cleaned up (custody.py:177-213).
  - M2 is refused both as the designated host and as the current host (protocol.py:574-585; custody.py:135-136).
- **Result seal and reveal.** Both require a verified chain, a terminal record, and a match on package, spec and
  nonce. Reveal additionally requires an allow-listed RESULT_SEAL and a RESULT hash match (custody.py:225-297).
  Evidence mirrors this (evidence.py:55-61).
- **Preflight forgery.** A same-account forger can write `PREFLIGHT_<nonce>.json` (protocol.py:263-274). This is
  declared (FIREWALL.md:309). The real run's prepare() repeats every check, except that the read half of the
  receipts probe is missing (V7-A).
- **Gap.** V7-C: an abort written as record 0 can never be result-sealed.

### Claim 5: Predictor isolation / v7 post-key behaviour. BROKEN
Attacks tried:
- **Pickle in the pipe.** None: JSON plus npy with `allow_pickle=False` (runner.py:169-202). Holds.
- **Garbage in the pipe.** Per-world PROTOCOL_ERROR (runner.py:864-885). Holds.
- **Closing the pipe.** Run-level abort that looks like infrastructure. V7-B, blocks-PASS.
- **Receipts probe after the key.** The read half is still post-key. V7-A, blocks-PASS.
- **Unstageable member names.** Refused at validation (runner.py:474-483). Holds on reading; the collision check is
  case-insensitive.
- **Staging failure.** Refused before the key (runner.py:633-639). Holds.
- **Spawn child loads unbound code.** The `__mp_main__` guard comes from C3D2_BOUND (entry.py:175-180), and sys.path
  is pruned (entry.py:40-43). Holds on reading. The package directory lies outside the repository, so the guard
  lets it load, as intended.

### Claim 6: Draw integrity. HOLDS (code); single draw CANNOT-VERIFY
- The sha256 values of draw.py (800e0b5d...), sealbox.py (dec9b915...), `__init__.py` (d38d3b0c...) and medium.py
  (09559e69...) equal the manifest's `d2_src_sha256_at_draw` and `family_src_sha256`.
- The nonce is `secrets.token_hex(32)` (draw.py:154). Exposed-D rejection is at draw.py:57-83.
- Note: the world RNG uses the nonce mod 2^128 (draw.py:63), giving 128-bit effective entropy. That is sufficient.
- Single-draw provenance is a custodian statement (declared).

---

## Always-check classes
1. **Unbound code with secrets.**
   - The entry guard serves `prometheus` only from the binding and compiles from hashed source with no pyc
     (entry.py:125-172). Other in-repo modules are refused (entry.py:134-143).
   - site-packages and `.pth` files remain unbound (declared F-3P).
   - No new unbound import was found in the v7 diff.
2. **Same-account readability.** Declared. Production is fail-closed until a separate child account exists (V7-E).
3. **Static-audit bypass.** `operator.attrgetter` with a string, and `faulthandler` (V7-D). Declared heuristic.
4. **Git ref ambiguity and history simplification.** Handled (claim 3).
5. **Unauthenticated records.** S1 is OPEN, which blocks PASS. The preflight record is self-reported (declared).
6. **Public fields that narrow hidden content.** Plaintext length and timing (declared). The abort `error_type` and
   `n_predictions_recorded` are public after the result seal only (as hashes before it).
7. **Spoofable host or identity.**
   - Host comes from `socket.gethostname()` and the account from GetUserNameW/SID (protocol.py:222-260). Same-account
     state (declared).
   - The comms sender is spoofable (S1).

## Declared residual risks: assessment
- **The key holder can decrypt.** Acceptable as declared.
- **The package is Python run as the operator; the AST audit is a heuristic.** Acceptable as declared. V7-D shows the
  v7 private-attribute flag adds little.
- **Single-draw provenance.** Acceptable as declared.
- **The System interface exposes physics.** Acceptable (contract design).
- **Crash-after-release policy (FIREWALL.md:311-316).**
  - Acceptable for true infrastructure crashes.
  - Missing: the list counts "OS kill" as outside the runner's control. A child that can signal or terminate its
    parent (same account, or the same console group for Ctrl-C events) turns a package action into such a crash.
    The separate-account requirement should explicitly include "the child cannot open the parent process or send it
    console control events", for example a new process group or detached console.
  - Missing: abort records carry no attribution evidence (V7-B, V7-F).
- **Not listed.** The separate-child-account path is unimplemented code (V7-E), so any PASS now cannot cover the code
  that would run a real evaluation.

## What would change the verdict
1. **V7-A:** read-probe the stand-in (or the run directory's read access) before the key, with a read-only-child
   control.
2. **V7-B:** make request-send failures per-world. Record the child's exit code and the I/O context in abort. Add a
   close-the-pipe control.
3. **V7-C (should-fix):** canonicalise the open body before the key, and make abort-before-open sealable.
4. **S1:** resolved by the operator's #925 decision.
5. **Self-tests:** not run by this replica. The committed SELFTEST_PROTOCOL.json reports `selftest_pass: true` with
   an empty `not_applicable_on_this_os` (M1). A Linux run should be attached by the script task.
