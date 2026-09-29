I found no new blocking finding in v11, but the overall verdict is still FAIL, and only because S1 (#925) is open. The v10 must-close items are closed in code: the deliver receipt, the seal-terminal newline fix, the lock and the binding to the open record. I ran no code: every self-test value below is the committed value in `SELFTEST_PROTOCOL.json`, and I could not recompute any sha256 because I had no hashing tool. The full audit is in `out/findings.md`.

**Audited commit:** e47d6fbbb. Its audited code is identical to origin/main (6baa07bd8). Since v10, only `runner.py` and `custody.py` changed in the audited files.

**Per-claim verdicts:**
- **v11-a, deliver receipt before every world is sent: HOLDS.** It is written to disk before the send (runner.py:1015-1020). No world data reaches the child before it, and nothing can remove it afterwards. So under Addendum J, "no deliver receipt" does prove the world was never delivered.
- **v11-b, bounded sends: HOLDS** for the world and reply sends. **BROKEN as stated** ("every parent-to-child send"):
  - **V11-1 (should-fix):** the final `stop` send (runner.py:966, 1083) and the receive after a successful poll (runner.py:224, 1036) have no deadline, so a package can still hang the runner after it has seen a world.
  - This affects liveness only. The runner is killed and the run sealed by the custodian, which is FORFEIT under Addendum J; there is no VOID option and no leak.
- **v11-c, seal-terminal keeps a verifying final record that lacks its newline: HOLDS.** Blank lines inside the file still cause truncation, but only after tampering (note).
- **v11-d, seal-terminal refuses while a runner holds the run lock: HOLDS.** The lock is not inherited by the child processes, and the v10 race scenarios are closed. Two notes:
  - **V11-2:** on Windows the lock is closed without an explicit unlock, so it may be released late. That only causes a spurious refusal, and a retry works.
  - **V11-3:** nothing checks whether the child account can read `run.lock`; this depends on host file permissions.
- **v11-e, seal-terminal is bound to this designation's open record: HOLDS.** Nonce, spec_id and package hash are checked before anything is written (runner.py:1248-1252). "Custodian only" is still not enforced (note).
- **Claim 1, opacity: HOLDS.** The plaintext length is visible, as declared. **V11-4 (note):** the public result-seal's `n_receipts` now also shows how many worlds were delivered before an abort.
- **Claim 2, secrets never in git: HOLDS** for the repo side:
  - No key, salt or plaintext file has ever been committed.
  - Every commit or merge touching the sealed files carries the same blobs as 95b31a30d.
  - The key-holder scan cannot be verified from the repo.
- **Claim 3, enforced order: HOLDS mechanically; BROKEN on authentication (S1).** There are no shadowing or replace refs, the full-history "added once" rule is unchanged, and no `protocol/` records exist yet.
- **Claim 4, controlled reveal: HOLDS.**
- **Claim 5, predictor isolation: HOLDS.** **V11-5 (should-fix, carried from the v10 replica 2):** when a replacement child fails to start, a cleanup `AssertionError` hides the real error. The abort then records the wrong `error_type`, a stale `child_world` and a lost exit code (runner.py:819-822, 965-968, 1081-1085).
- **Claim 6, draw integrity: HOLDS** for what the repo can show. The blobs match the seal commit; the sha256 values themselves are unverified here.

**Blocks-PASS findings:**
- **S1 (#925), with branch protection on main:** protocol records count once they are in the custodian's allow-list, and that list is fed from comms messages whose sender field is client-supplied. It stays open and is the operator's decision.

OVERALL: FAIL