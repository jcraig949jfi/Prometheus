**OVERALL: FAIL.** Two findings block a PASS, both in tools the protocol itself runs as the custodian account on M1.

This was a static audit of commit e6e482ae6. Per the skill I ran no repository code: no self-tests and no `entry.py gates SEAL`. I did hash the sealed files with `sha256sum` and used `rogit` for history. All public hashes match the brief, including the at-draw hashes of `draw.py`, `sealbox.py` and `__init__.py`. The exposed D set is byte-identical to a56ef7787. No secret-shaped file appears anywhere in git history. The full audit is in `out/findings.md`.

**Verdict per claim**
- **Claim 1, Opacity:** HOLDS. The plaintext length is visible in the manifest (declared). There is also a small undeclared timing channel: the predictor controls how long the run takes, and the public records carry timestamps.
- **Claim 2, Secrets never in git:** HOLDS on the repository side. The key-holder scan is CANNOT-VERIFY: it rests on Nestor's published booleans.
- **Claim 3, Enforced order:** HOLDS for the gate logic. Should-fix: custody, runner and evidence accept any `refs/...` via `--ref`/`--gate-ref`, so records need not come from origin/main.
- **Claim 4, Controlled reveal:** BROKEN (B-1 below).
- **Claim 5, Predictor isolation:** HOLDS narrowly (no pickle, error replies carry type names only). The production run path is broken (S-1 below).
- **Claim 6, Draw integrity:** HOLDS.
- **v4 P1:** HOLDS for a module planted in the package directory. The wider claim that plain `python entry.py` is safe fails: a `sitecustomize.py` or `usercustomize.py` on PYTHONPATH runs before stage 1 (should-fix).
- **v4 P2:** HOLDS inside the Python process that entry.py launches. The gaps are in code run outside it (B-1, B-2, S-1).
- **v4 P3:** HOLDS for `entry.py gates`. The full end-to-end run through entry.py cannot complete (S-1).
- **F-CWD repair:** BROKEN (B-1, B-2). F-GITENV, F-FETCH, F-GOV, F-ONCE, F-AST, F-NET and the claim-6 redraw check hold, with minor notes in the file.

**Blocks-PASS findings**
- **B-1 (key release runs `icacls.exe` from the cwd):**
  - Where: `custody.py:141` calls `subprocess.run(["icacls", ...])` by bare name, after the key has been written to the destination.
  - Why the cwd copy runs: Windows searches the current directory before System32. The custodian's own self-test confirms this on M1: `SELFTEST_PROTOCOL.json:77`, `v4_CWD_control_cwd_git_exe_is_found: true`.
  - Why the planted file survives: entry.py does not check files at the repository root.
  - Scenario: anyone who can push to main (Cosmos must, to commit its prediction commitment, and branch protection is off) commits an `icacls.exe` at the root. The custodian runs `custody release-key` from the root after pulling, and that program runs as the custodian account.
  - The v4 repair covered only git.
- **B-2 (allowlist.py runs unaudited repository code):**
  - Where: `allowlist.py:40` calls `git` by bare name, without the GIT_* stripping. It also imports `comms` from the working tree, and `comms/api.py:78-80` puts the repository root first on the import path and imports `evidence_wiki`. That contradicts v4's "appends the repository root last".
  - This step is mandatory: it is the only way any record becomes governing.
  - Scenario: Cosmos changes `comms/api.py` on main, posts its commitment, and knows Nestor will now run `allowlist.py add`. That runs Cosmos's code as jcrai, and that account can read the key, salt and plaintext.

**Most important should-fix (fix before any real key release)**
- **S-1:** a run through entry.py cannot complete, and it fails only after the one-time key release has been used up.
  - Cause: entry.py removes the repository root from the import path, so the spawned predictor child cannot import `prometheus`.
  - Timing: the child dies after the key has been read and deleted and KEY_RELEASED is on record, so the spec_id is permanently deadlocked.
  - Why tests missed it: no test runs the runner through entry.py.
  - Same timing problem: the declared ChildNotIsolated refusal also fires after release.

**Other should-fixes**
- **S-2:** `firewall-check` is never bound to the audit. It always runs whatever is committed on origin/main, with all three secrets loaded.
- **S-5:**
  - If the icacls step fails, the key copy is left in the destination with no release record.
  - The ACL grant takes the account name from the `USERNAME` environment variable.
- **S-6:** `once_record_present` treats a git error as "no record" (fail-open).

**Declared residuals:** S1 (record authentication, #925) and branch protection are still open. The declared residuals omit that unprotected main is a path for Cosmos to run code as the custodian account (B-1, B-2, S-2). That path is not contained by S1, as FIREWALL.md v2 argued.

`OVERALL: FAIL`