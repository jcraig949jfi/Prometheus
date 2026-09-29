The verdict is **FAIL**, and the only reason is S1: protocol records are still unauthenticated, which is the declared-open operator decision. Leaving S1 and branch protection aside, I found nothing else that blocks a PASS in the firewall code at a823b596c.

Limits: the audit is from reading code and read-only git. I could not run anything, because shell commands other than `rogit` were denied in this worker. So I did not run the self-tests or compute any sha256. The committed `SELFTEST_PROTOCOL.json` says `selftest_pass: true`, but that is the author's run, not mine.

The full audit is in `out/findings.md`.

**Claim verdicts**
1. **Opacity: HOLDS.** The salted commitment and AES-256-GCM hold up, and nothing public carries world identities or knobs. The plaintext length visible in the manifest is already declared.
2. **Secrets never in git: HOLDS on the repository side.** No key, salt or plaintext file was ever added on any ref, and nothing was ever committed under `protocol/`. Whether secret contents are embedded inside other files needs the key-holder scan (`firewall-check`), so that part is CANNOT-VERIFY.
3. **Enforced order: BROKEN on S1 (blocks-PASS).** The allow-list takes the comms sender at its word, and main is unprotected. The rest of the mechanics hold: fully qualified refs, full-history merge checks, code bound before import, and the key read only after every check.
4. **Controlled reveal: HOLDS**, with should-fix items on the new seal-terminal tool (below).
5. **Predictor isolation: HOLDS as designed.** A child running as the runner's own account is always refused before the key is read. There is a should-fix on attribution labels (V10-1).
6. **Draw integrity: HOLDS.** `draw.py`, `sealbox.py`, `__init__.py`, the ciphertext, the manifest and `c3_holdout_D/` are unchanged since the seal commit. Two things are CANNOT-VERIFY: whether their hashes match the at-draw values (I had no way to hash), and the declared single-draw provenance.

**v10 scope**
- **Attribution labels:** `exposed`, `in_predictor_io` and `current_world` are truthful.
  - **V10-1 (should-fix):** if starting a replacement child fails, the cleanup raises an `AssertionError` that replaces the real error. The abort record then shows the wrong `error_type` and the previous child's `child_world`.
- **seal-terminal "never removes a verifying record": BROKEN (should-fix, V10-2).** Its parser can drop records that the project's own verifier accepts: a final record missing only its trailing newline, which could be a terminal `close`, or any record after a blank line.
- **V10-3 (should-fix), three gaps in seal-terminal:**
  - It checks only the directory name, not the open record's nonce/spec_id/package, and not that the directory is under the run root.
  - It takes no lock and does not check whether the run is still live.
  - "Custodian only" is not enforced, so the `SEALED_BY_CUSTODIAN` label proves nothing about who ran it.
- **Notes:** timeouts use wall-clock time; a few bytecodes-wide Ctrl-C windows exist around writing the close record; Ctrl-Break (`SIGBREAK`) is not masked during abort; `disk_chain_matched` is false on any read error; malformed input gives an uncaught exception with no refusal logged; a stale `.claim` file after a hard crash blocks the run with no guidance.

**blocks-PASS findings**
- **S1:** protocol records (audit, commitment, designation, result seal) count once their hash is in the custodian's allow-list. That list is fed from comms messages whose sender field is client-supplied, and main has no branch protection. So anyone who can push to main and forge a comms sender can get an allow-listed PASS audit, commitment or designation. Only the operator's #925 decision can close this (`protocol.py:461-473`; `FIREWALL.md:357`).

OVERALL: FAIL