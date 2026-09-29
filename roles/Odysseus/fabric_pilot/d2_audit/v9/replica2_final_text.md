I found no blocks-PASS finding in v9. Everything passes except S1 (#925) and branch protection on main, which remain the operator's decisions, and v9 fixes both v8 blockers. The runner's attribution labels are still not truthful in every case (A3-1, A3-2), so Harmonia Addendum H cl.2 stays in force: every abort after exposure is FORFEIT whatever its label.

I read the code and git history only; I ran nothing. The self-test results come from the committed `SELFTEST_PROTOCOL.json` (148 checks true, 4 defect controls true). Since the v8-audited commit (a02b9b20c), only `runner.py`, `custody.py`, the self-tests and the docs changed. For the unchanged code, my verdicts combine that diff, spot checks and the v8 replicas' results. None of these findings can occur in production yet: the runner refuses a predictor child running as the same account before the key is read, and the separate-account launcher does not exist (V7-E).

**Claims:**
- 1 Opacity: **HOLDS**. The manifest length field is a declared residual; v9 adds nothing public before reveal.
- 2 Secrets never in git: **HOLDS** on the repository side. No key, salt, plaintext, `.pyc` or `protocol/` file appears in any commit. The key-holder scan on M1 is CANNOT-VERIFY from here.
- 3 Enforced order: **HOLDS** except S1, which is open and declared. `AUDITED_FILES` is unchanged and binds the changed files.
- 4 Controlled reveal: **HOLDS**. Custody now test-decrypts the key before any copy leaves (`custody.py:202-203`).
- 5 Predictor isolation: **HOLDS as declared**. The AST audit is a heuristic that can still be bypassed.
- 6 Draw integrity: **HOLDS**. Single-draw provenance is a declared residual.

**v9 items:**
- 1 Key proven before the consumption marker: **HOLDS** (`runner.py:750-769`). A wrong key is refused and nothing is consumed.
- 2 Interrupted write stays sealable: **HOLDS**. An interrupted record write is rolled back to the last complete record, and abort drops a partial trailing write before writing its own record. One carried note: an operator interrupt between the marker rename and the `self.receipts` assignment (`runner.py:389`, `769`) still leaves a chain with no terminal record.
- 3 Attribution labels truthful: **BROKEN, should-fix.**
- V8-6 staged package readable before the key: **HOLDS**, but only the entry file is checked (note).

**Blocks-PASS findings:** none. S1 and branch protection are out of scope as operator decisions.

**Should-fix items to address before any key release:**
- **A3-1:** if the *first* predictor child fails to start, the abort is labelled `current_world=0, in_predictor_io=true` (`runner.py:927-929`). No world had been sent, so the truth is pre-exposure (VOID), but the label reads as post-exposure (FORFEIT). v8 labelled this case correctly; v9 regressed it, and the self-test asserts the wrong label (`selftest_protocol.py:1241-1253`).
- **A3-2:** `child_exitcode` can come from an earlier or different process when no child is running at abort time (`runner.py:818`, `893`). The self-test only checks that it is not null.
- **A3-3 (caveat for Harmonia):** the runner kills only the direct child, not its process tree. So `in_predictor_io=false`, phase SEALED or the exit code do not prove the package was inactive.
- **B-1:** a second interrupt during `abort()` escapes it, because the guard there catches `Exception` only and nothing ignores SIGINT during the run. The chain then has no terminal record, so the v8 residual "the resulting abort carries the attribution evidence" is not always true. Addendum F item 3 already rules this FORFEIT, so the package gains nothing.

**Notes:**
- B-2: `FIREWALL.md:350` says a poll failure is a per-world status, but the poll at `runner.py:938` is still outside the per-world guard.
- B-3: v8 dropped the exclusive creation of `receipts.jsonl`, so two runner invocations started at the same moment could both pass the check. This is operator-only and needs microsecond timing on Windows.
- B-4: a failed RESULT.json write after `abort` is undeclared. After `close`, the CLI also raises a KeyError.

OVERALL: PASS

That verdict excludes S1 and branch protection, which I did not assess, and the attribution labels are explicitly not certified truthful. The full audit, with file:line evidence for every claim, is in `/home/jcraig/fabric-work/worker.ubu001.b/attempts/att-3f2a9a91b577/out/findings.md`.