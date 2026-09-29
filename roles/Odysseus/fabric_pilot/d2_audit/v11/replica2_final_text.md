# Holdout D2 firewall re-audit v11: replica verdict

The only item that blocks a PASS is S1, which was already declared open. The new v11 code adds no other blocker, but two v11 claims are only partly met. I read the code and git history at commit e47d6fbbb; I could not run any code. So I did not run the self-tests or `entry.py gates SEAL` on the real history, and the draw redraw is also unverified. The committed `SELFTEST_PROTOCOL.json` shows 160 of 160 checks and 4 of 4 defect controls true. The full audit is in `out/findings.md`.

## Verdict per claim
- **1. Opacity: HOLDS.**
  - Manifest and self-test outputs are public fields and booleans only.
  - The new `deliver` receipts stay on M1.
  - The abort record adds only a count of deliver records.
- **2. Secrets never in git: HOLDS on the repo side; CANNOT-VERIFY on M1.**
  - No key, salt or plaintext file name appears anywhere in the history.
  - No `protocol/` record has ever been committed.
  - The M1 side needs Nestor's `entry.py firewall-check` booleans.
- **3. Enforced order: BROKEN, on S1 only.** protocol.py and entry.py are unchanged since v10, and the ref, merge, stale-code and loaded-closure gates still hold.
- **4. Controlled reveal: HOLDS, subject to S1.** Deliver records do not break result-seal, reveal or evidence, which only check the terminal record and the chain head.
- **5. Predictor isolation: HOLDS for confidentiality.** Two paths can still hang the runner (V11-1, V11-2 below).
- **6. Draw integrity: HOLDS for the hashes; the single-draw statement CANNOT-VERIFY (declared).**
  - draw.py, sealbox.py, `__init__.py`, medium.py, `hidden_D2.enc` and `MANIFEST_D2.json` all match their committed values.
  - `c3_holdout_D` is byte-identical to a56ef7787.
- **v11 deliver evidence: HOLDS.**
  - Every message carrying world data is sent only after its `deliver` receipt is written and fsynced.
  - A chain with zero deliver records therefore proves that no world was delivered.
- **v11 bounded sends: PARTIAL.** Should-fix V11-1 and V11-2.
- **v11 seal-terminal:**
  - Newline handling: HOLDS, with note V11-4.
  - Lock and liveness: HOLDS.
  - Binding to the open record: HOLDS.

## Blocks-PASS findings
- **S1 (declared open, operator #925):** protocol records are not authenticated.
  - The allow-list trusts the comms `sender` field, which the posting client supplies (`allowlist.py:37-39`, `:95`).
  - Main has no branch protection.
  - So a forged PASS audit record, confirmed by a spoofed "Odysseus" message, would open the AUDIT gate.

## Should-fix items (not blocking)
All three hang or label issues need the package to reach the pipe directly, past the AST heuristic. That is the same threat class v10 assumed. In each case the outcome is FORFEIT under Addendum J, so the package never gets a VOID option.

- **V11-1:** the runner's receive from the child has no deadline once `poll` reports data (`runner.py:1036`, `:224-225`).
  - After a world is delivered, a child can announce a long message, send a few bytes and stop.
  - The runner then hangs holding `run.lock`.
  - The custodian must kill it and run seal-terminal, which records the deliver count.
- **V11-2:** the `stop` send at `runner.py:966` has no deadline (reached from `:1083`), so FIREWALL.md's "every parent-to-child send" is overstated. The effect is the same as V11-1.
- **V11-3 (carried from v10, not fixed):** if a replacement child fails to start, cleanup raises an `AssertionError` that replaces the real error. The abort then records the wrong error type and the previous child's world (`runner.py:819-822`, `:966-968`, `:1083-1085`).

## Notes
- **V11-4:** seal-terminal splits lines differently from `verify_receipts`. A blank line or stray carriage return planted between records would make it cut records the verifier accepts. The runner never writes such bytes.
- **V11-5:** the self-tests have two gaps.
  - The send-deadline test never exercises killing the child.
  - The lock test runs in one process only.
- **V11-6:** custody's `main` does not catch the seal-terminal refusal, so it prints a traceback instead of the JSON refusal. "Custodian only" is still not enforced.

OVERALL: FAIL