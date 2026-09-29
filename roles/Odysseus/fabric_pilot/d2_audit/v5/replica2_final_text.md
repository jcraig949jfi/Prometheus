I audited commit 57c809387 by reading the code and checking history with `rogit`. I did not run `selftest_protocol`, `selftest_D2` or `entry.py gates SEAL` against the real history, so every verdict below comes from reading the code. I recomputed the public hashes: the ciphertext, the manifest, the spec_id and the at-draw hashes of `draw.py`, `sealbox.py`, `__init__.py` and `medium.py` all match. The full audit is in `out/findings.md`.

**Claim verdicts**
1. **Opacity:** HOLDS. The commitment is salted, the manifest has no knobs, seeds or nonce, results are public only as hashes that include an HMAC tag, error replies carry type names only, and the `SELFTEST_*.json` files are booleans only. The plaintext length is visible, as declared.
2. **Secrets never in git:** HOLDS for file names; key-shaped content CANNOT-VERIFY from the repo. Only one commit (95b31a30d) adds the ciphertext and manifest, and no key, salt or plaintext file was ever in `c3_holdout_D2`. Whether key or salt bytes hide inside other files needs Nestor's key-holder scan on M1.
3. **Enforced order:** BROKEN. The order checks themselves hold, but "refuse before touching the key" does not (F1).
4. **Controlled reveal:** HOLDS, apart from S1, which is open.
5. **Predictor isolation:** HOLDS as declared. The spawn child imports only bound code, and a child running as the same account is refused at the preflight.
6. **Draw integrity:** HOLDS. The nonce comes from a CSPRNG, exposed-D worlds are rejected, the code hashes match the at-draw values, and the redraw checks its own code.

**v5 items**
- **Hold:** B-1 (icacls by absolute path), S-2, S-3, S-4 and S-6.
- **Every module plant the brief listed fails:** a planted module in the package directory, repo root or cwd, a `.pyc`, `-S`, PYTHONPATH, GIT_* variables, replace refs, and a `git.exe` in the cwd.
- **S-5 holds except in `firewall_check`**, which lacks the git hardening flags. That is a note: the commands it runs start no hooks.
- **B-2 is only partly repaired (F2).**
- **S-1 is BROKEN (F1).**

**blocks-PASS finding**
- **F1: the runner can refuse after the one-time key release is used up.**
  - **Code path:** `FirewallRun.open()` (`runner.py:605-641`) runs the preflight, reads the key, deletes the released copy, decrypts and creates `run_<nonce>/`. Only then does it call `load_package`, which can refuse the package for a hash mismatch, an invalid member or AST-audit flags.
  - **Scenario:** the committed package has an AST flag (for example a bare `getattr`) or a `.npy`/`.pyc` member, or `--package` points to a wrong copy.
  - **Why it is irreversible:** a rerun is refused because the run directory exists (`runner.py:929`). A second release is refused because of the committed KEY_RELEASED record and the custody log (`custody.py:183-186`). A new designation is impossible because records are added once. So D2 is burned by an error that could have been fixed.
  - **Nestor cannot catch it beforehand:** `--preflight` never loads the package, and `--allow-flagged` has to be chosen before the flags are seen.
  - **Fix:** hash, validate, audit and stage the package, and add the receipts-write probe, before the preflight and the key read. Make `--preflight` include those checks.

**should-fix findings**
- **F2: `allowlist.py` takes its database host from the repository** (`allowlist.py:49-66`, from `evidence_wiki/config.json`). Anyone who can push to main can point the allow-list lookup at their own server and get a forged "Odysseus" message accepted. The configured database password would also be sent to that server. The committed config also says the M1 Postgres accepts connections from LAN peers with the committed credentials, which is further evidence that S1 is open.
- **F3: on non-Windows hosts the allow-list path is relative to the current directory.** `C:/Users/...` is not absolute on POSIX, so running from the repo root would read a committed file. No key is exposed, because key holding is on M1 only.

**Notes:** a force-push can remove the once-only records, leaving only the custody log (which the same account can edit) as a barrier. The account check compares names, not SIDs. Custody has a few failure-path gaps. Pre-audit pins are per file, so files from different pin sessions can be combined. `--allow-flagged` is a command-line choice, not bound by the designation.

**Residual risks:** all the declared ones are acceptable as stated. Missing from the list:
- F1, which should be fixed rather than declared;
- F2 and F3;
- the database that is reachable from the LAN;
- a force-push re-enabling a once-only action;
- objects still held on the remote after removal, which the key-holder scan cannot see.

OVERALL: FAIL