The D2 v7 firewall re-audit at commit e4efb487e is a FAIL. v7 still leaves one path where the release is used up with no sealable record, and S1 remains open. The full audit is in `out/findings.md`. I read the code but couldn't run it, so both self-tests are unrun here.

**v7 focus questions**
- **Q1, release used up without a terminal record: BROKEN (blocks-PASS).** See V7-1 below.
- **Q2, checks or probes after the key read that can refuse: partly BROKEN.** It's the same window as V7-1. Every other check now runs before the key is read, in `prepare()` (`runner.py:602-648`).
- **Q3, the package ending the run without a sealed, attributable outcome: should-fix.** Every failure after the open record becomes a sealed abort. But the abort record carries only the phase, the error type name and a count (`runner.py:744`). It doesn't say which world was running or which side raised, so deciding FORFEIT (package's fault) versus VOID (infrastructure) rests on a type name.

**Claims in the brief**
1. **Opacity: HOLDS.** The plaintext length is visible in the manifest, which is already declared.
2. **Secrets never in git: CANNOT-VERIFY-FROM-REPO.** The git history shows no key- or salt-shaped files. Proving the key and salt bytes are absent needs Nestor's key-holder scan (`firewall-check`) on M1, reporting `all_clean: true` for this commit.
3. **Enforced order: BROKEN only through S1.** S1 (authenticating the records) is declared open, pending #925. The added-once, ordering, stale-code and import-guard checks hold.
4. **Controlled reveal: HOLDS.** Accepting `abort` as a terminal record is consistent across custody and evidence, but V7-1 can leave nothing to reveal.
5. **Predictor isolation: HOLDS as declared.** A child running as the runner's own account is refused; the separate child account is a host capability still to be provided.
6. **Draw integrity: HOLDS.** `draw.py` and `sealbox.py` are unchanged in v7.

**Blocks-PASS finding**
- **V7-1:** `FirewallRun.open()` reads the key and creates `receipts.jsonl`, the file that marks the release as used (`runner.py:679`). Only then does it build and write the first ("open") record (`runner.py:681-693`).
  - **What goes wrong:** if that step raises, `run_all` calls `abort()`, which writes `abort` as the first record. The chain check requires the first record to be `open` (`runner.py:401-403`), so the chain never verifies.
  - **Result:** result-seal, reveal and evidence all refuse. A rerun refuses because `receipts.jsonl` exists, and a second release refuses. The spec_id is spent with no sealed outcome.
  - **Triggers:**
    - Environment triggers are certain: that step does file I/O on the manifest, `runner.py` and `certify.py` that `prepare()` never did, plus the write and fsync.
    - A package trigger is plausible but not established: the open record embeds the package's `package.json` verbatim, and it is never serialised or hashed before the key read.
  - **Tests:** nothing covers this window. The v7 abort test only fails after the open record exists (`selftest_protocol.py:1071-1085`).
  - **Fix:** build the whole open record in `prepare()`, then create the file and write record 0 in one step. Or let the chain be sealed without an open record. Either way, add a test that injects a failure at `runner.py:681`.

**Residual risks:** the declared ones are acceptable as declared, including the crash-after-release policy. One is missing from the list: an ordinary, catchable exception can spend the designation (V7-1), which is not the same as a crash outside the runner's control.

**Still open by operator decision:** S1 (#925) and branch protection on main.

Part of my earlier response was stopped by a safety classifier. After that I kept these findings at the level of code behaviour, with no worked package inputs for triggering the failures.

OVERALL: FAIL