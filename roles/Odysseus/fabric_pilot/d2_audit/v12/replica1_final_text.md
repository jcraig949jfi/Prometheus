I found no blocks-PASS finding in the v12 root of trust (commit `b0763ebaa`, whose `prometheus/cosmos` tree is identical to `acaf14df4`), so this replica's verdict is PASS with three should-fix items. I did not run any code: the sandbox refused Python. That means I did not run `selftest_protocol` (165 checks) or `selftest_D2`, did not run `entry.py gates SEAL` against the real history, and could not compute `--code-hashes` for the audit record. Where I cite self-test results, they are the values committed in `SELFTEST_PROTOCOL.json` (all anchor tests true, `selftest_pass: true`). The full audit is in `out/findings.md`.

**Verdict per claim**
- **V12-a (a record governs without a verifying anchor entry):** HOLDS. Unanchored audits are filtered out before the highest n is chosen (`protocol.py:582-588`, `entry.py:305-309`). A missing anchor file refuses everything, and no command-line path can turn the check off.
- **V12-b (forge, edit, reorder or truncate the anchor undetected):** BROKEN as literally claimed, but contained by the declared M1-account residual. Editing or reordering entries is caught. Cutting entries off the end is not, and the hash chain has no key, so anyone who can write the file can rebuild it. FIREWALL.md:400 overclaims ("a removed entry breaks the chain").
- **V12-c (anchored commit not an ancestor, or not the commit that added the record):** HOLDS in `check_gates` for all four roles. `entry.py` skips the adding-commit check, which is declared (FIREWALL.md:414) and harmless because the gates catch it.
- **V12-d (a gated step skips re-verification):** HOLDS for AUDIT, COMMITMENT, DESIGNATION and RESULT_SEAL: every key-holding action runs `check_gates` after entry fetches. `KEY_RELEASED.json` and `REVEALED.json` are not anchored (SF-3).
- **1. Opacity:** HOLDS. The anchor holds identifiers and hashes only.
- **2. Secrets never in git:** HOLDS for the repository history. The key-holder scan on M1 cannot be verified from the repo.
- **3. Enforced order:** HOLDS.
- **4. Controlled reveal:** HOLDS.
- **5. Predictor isolation:** HOLDS as audited through v11; v12 does not touch `runner.py`.
- **6. Draw integrity:** HOLDS for the hash bindings. Single-draw provenance is declared.

**Should-fix items**
- **SF-1:** `allowlist add` anchors a record by file name only (`allowlist.py:50-84`).
  - It takes no expected commit or sha256, and it writes the entry before the custodian sees which commit it anchored.
  - `check_gates` never checks the `auditor` field.
  - Branch protection is off, so anyone who pushes a `FIREWALL_AUDIT_1.json` first, or force-pushes over the real one, before the custodian runs `add` gets their version anchored.
  - The custodian can detect this by comparing the printed commit with the one I post, and recover with a `FIREWALL_AUDIT_2`, but this "integrity, not authorship" gap is not declared as a residual.
  - Fix: require `--expect-commit` and `--expect-sha256`.
- **SF-2:** Rolling the anchor back (dropping its last lines) is undetected. It can bring back a PASS audit that a later FAIL superseded, or a revoked tool-pin batch. The fix is to correct the FIREWALL.md claim, declare this, and optionally publish each new head hash.
- **SF-3:** A force-push that removes the `KEY_RELEASED` or `REVEALED` records is not detected, contrary to MWO D2-1 ("each protocol record"). The M1 custody log still refuses a second release, but the public git record of the release can be erased silently.
- **Notes:**
  - Appending to the anchor has no lock, so two concurrent writes or a torn line break the chain; every gate then refuses until a hand edit that looks like tampering.
  - A malformed anchor line gives a traceback instead of a clean refusal. It happens before the key is read, so it still fails closed.

**Blocks-PASS findings:** none.

OVERALL: PASS (conditional on the self-tests re-running green on M1 or Fabric; SF-1 to SF-3 should be fixed or declared before the custodian anchors FIREWALL_AUDIT_1)