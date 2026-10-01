# D2 v8 firewall re-audit (commit a02b9b20c): one blocking finding, OVERALL FAIL

I didn't run anything: the self-tests, `entry.py` and hashing were all blocked here, so this audit is static reading plus git history only. The full audit is in `out/findings.md`. S1 and branch protection on main remain open as operator decisions and are not counted as findings.

## Verdict per claim
- **1. Opacity:** HOLDS. The manifest shows the plaintext length, which is already declared.
- **2. Secrets never in git:** HOLDS on the repository side. Only commit 95b31a30d adds the sealed files, and no key, salt or plaintext file name appears anywhere in history. The key-holder scan on M1 is CANNOT-VERIFY from here.
- **3. Enforced order:** HOLDS, apart from S1.
- **4. Controlled reveal:** the reveal itself HOLDS. The v8 open path is BROKEN (V8-1 below).
- **5. Predictor isolation:** HOLDS as declared. The new abort attribution fields are partly broken (V8-2, V8-3).
- **6. Draw integrity:** HOLDS, but I couldn't check it all. `draw.py` and `sealbox.py` are unchanged since the seal commit. I couldn't recompute their hashes against the manifest, and single-draw provenance is declared.
- **v8 "no check that can refuse runs after the key is read":** BROKEN (V8-1).
- **v8 "no consumed release without a verifiable terminal record":** HOLDS for ordinary exceptions. The remaining gaps are environment-only (V8-5, a note).

## Blocks-PASS finding
**V8-1:** the key is only checked for correctness after the run has been marked as consumed.
- **Where:** the runner reads the key (`runner.py:723`), which checks only its format and length. It then writes the consumption marker (`runner.py:726`) and deletes the key file (`runner.py:729`). Decryption, which is what actually rejects a wrong key, comes after that (`runner.py:730-741`). Custody also copies the key without testing it (`custody.py:195-196`).
- **Scenario:** the runner passes `--key` pointing at any well-formed 64-hex-character file that isn't the D2 key.
  - Every gate and probe passes, the marker is written and that file is deleted.
  - Decryption then fails, and the run is sealed as an abort.
  - A rerun is refused and a second key release is refused, so D2 is spent (VOID) with no package code ever run.
  - The real released key is left on disk.
- **Why it blocks:** this is exactly what the v8 brief asked us to find. An argument error that can be recovered from ends up spending the release.
- **Fix:** decrypt and run the consistency checks before writing the marker, or have custody test-decrypt before releasing. Add a self-test with a well-formed wrong key.

## Should-fix findings
- **V8-2:** the abort's `child_exitcode` is always null. `abort()` shuts down the worker, which clears the process handle (`runner.py:854`), before the exit code is read (`runner.py:779`). The self-test only checks that the field exists (`selftest_protocol.py:1165`).
- **V8-3:** after a world's crash, the next world starts a fresh child and probes it outside the per-world guard (`runner.py:887-888`). If that probe fails, the whole run aborts and the record names the previous world with `in_predictor_io=false`. That reads as an infrastructure failure (VOID).

## Notes
- **V8-4:** on Windows, `poll` sits outside the per-world guard (`runner.py:898`), so a child that exits at the wrong moment could abort the whole run. This is plausible but unverified, and the abort would still point to FORFEIT.
- **V8-5:** if writing RESULT.json fails, the chain has a terminal record that result-seal can't seal, and there's no tool to rebuild RESULT.json from the receipts.
- **V8-6:** an aborted run can leave the released key copy on disk.

OVERALL: FAIL