The v7 audit fails. S1 (unauthenticated protocol records, #925) blocks a pass on its own, and I found two new v7 defects that also block it. This was a code-reading and git-history audit only: I did not run `selftest_protocol`, `selftest_D2`, `entry.py gates SEAL` or `--code-hashes`, so the findings marked PLAUSIBLE need a self-test to confirm. The full audit is in `out/findings.md`.

**Audited commit:** e4efb487e. The D2 code was last changed at bfcd26e3c (v7).

**Per-claim verdicts**
1. **Opacity: HOLDS.** The manifest still shows the plaintext length (`ciphertext_bytes`), which is already declared. The ciphertext and manifest hashes match the brief.
2. **Secrets never in git: HOLDS** for what the repo can show. No key, salt or plaintext file was ever added in history, and `c3_holdout_D` is byte-identical to a56ef7787. The key-holder content scan is CANNOT-VERIFY-FROM-REPO.
3. **Enforced order: BROKEN, because of S1.** Records are not authenticated: the comms sender is set by the client and main is unprotected. The rest of the gate logic holds on reading: shadow refs, merge rewrites, grafts/shallow, `GIT_*` variables and code staleness.
4. **Controlled reveal: HOLDS**, subject to S1. Some aborted runs can never be result-sealed (V7-C).
5. **Predictor isolation and v7 post-key behaviour: BROKEN** (V7-A, V7-B).
6. **Draw integrity: HOLDS for the code.** `draw.py`, `sealbox.py`, `__init__.py` and `medium.py` all hash to the at-draw values in the manifest. "draw.py ran once" is CANNOT-VERIFY, as declared.

**Blocks-PASS findings**
- **S1 (known, #925):** anyone who can push to main and forge a comms sender can author an audit, commitment or designation record.
- **V7-A: part of the receipts probe still runs after the key is read.** FIREWALL.md claims the stand-in is probed for "read + append", but `runner.py:643` only probes it for append. The read probe on the real `receipts.jsonl` happens only after the key read and open record (`runner.py:800`); before that the file does not exist, so it reads as "missing" and passes. Scenario: a separate child account with an inherited read-only grant on the runs root. That is the natural set-up, because the child has to read `<run>/package`. It passes `prepare()`, then fails with ChildNotIsolated after the release is consumed, which spends D2. The existing self-test misses this because its same-account child is already refused by the append probe. Fix: add the stand-in to the read paths in `prepare()`.
- **V7-B: a package can end the run on purpose, and the record looks like an infrastructure failure.** The parent's request send (`runner.py:850`) is outside the per-world `try`, which contradicts FIREWALL.md v7 3(a). A package that passes the AST check can do this:
  - At any world it chooses, it gets the pipe with `operator.attrgetter("_HiddenWorldStub__conn")`, sends a valid `done`, then calls `close()`.
  - The parent's next send fails with BrokenPipeError, and the whole run aborts.
  - The abort record holds only the error type ("BrokenPipeError"), the phase and a count. There is no child exit code and nothing marking it as predictor I/O.

  So a package can stop the run whenever it chooses, and Harmonia's Addendum E (which relies on evidence to choose between VOID and FORFEIT) has nothing to decide with. Fix: treat send failures as that world's crash, record attribution evidence in the abort, and add a self-test in which the package closes the pipe.

**Should-fix and notes**
- **V7-C (should-fix, PLAUSIBLE):** if writing the open record fails, abort becomes record 0, the chain never verifies, and custody cannot result-seal the run. One package-controlled trigger is `adjudication` JSON nested so deep that it parses before the key read but fails when re-encoded after it. Ctrl-C at that moment does the same.
- **V7-D (note):** the new private-attribute AST flag is bypassed by `operator.attrgetter` and `faulthandler`.
- **V7-E (note):** there is no code for starting the child under a separate account, so a real evaluation cannot run yet and that future code will need its own audit.
- **V7-F (note):** a package can put memory or compute pressure on the parent, and the resulting abort would look like an infrastructure out-of-memory.
- **Residuals list:** it should say that the child must not be able to terminate or signal the parent (for example with console Ctrl-C events). It should also say that abort records currently carry no attribution evidence.

OVERALL: FAIL