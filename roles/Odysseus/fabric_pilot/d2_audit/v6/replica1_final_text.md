I audited the v6 commit and the verdict is **FAIL**: three blocking findings, all ways the one-time key release can still be spent and then deadlocked. I only read the code; I couldn't run it, and I did not run either self-test (shell commands other than `rogit` were denied).

The full audit is in `out/findings.md`.

**Claim verdicts**
1. Opacity: HOLDS. Only the plaintext length (manifest `ciphertext_bytes`) and a timing channel are visible, and both are already declared. Unchanged since v5.
2. Secrets never in git: HOLDS for what the repository can show. No key, salt or plaintext file was ever added under `c3_holdout_D2`. Whether key or salt contents appear anywhere in history can't be checked from the repo; Nestor's `firewall-check` booleans from M1 would settle it.
3. Enforced order: HOLDS, except S1 (unauthenticated records), which is open as declared. Finding V6-5 below may widen S1 to a second account, depending on M1's folder permissions.
4. Controlled reveal / key release: BROKEN (V6-1, V6-2 and V6-3 below; plus V6-4 and V6-5, should-fix).
5. Predictor isolation: BROKEN (V6-1).
6. Draw integrity: HOLDS. Unchanged since v5.
- Self-tests: CANNOT-VERIFY. The committed `SELFTEST_PROTOCOL.json` says `selftest_pass: true` (including `v4_DEST_key_acl_restricted`), but none of its checks exercises V6-1, V6-2 or V6-3.

**Blocking findings**
- **V6-1: a malformed message from the predictor crashes the runner after the key is deleted** (`runner.py:777`, `:783`).
  - Only the message decoding is error-handled. A message like `5`, `[]` or `["done"]` raises an uncaught TypeError, IndexError or KeyError.
  - The package can reach the raw pipe through `system._HiddenWorldStub__conn.send_bytes(...)`. The static package check doesn't flag that name, because it only flags names that start and end with `__`.
  - Result: key gone, run directory exists, rerun and second release both refused, so the spec_id is permanently deadlocked.
  - The package can choose to do this after probing the hidden worlds, so Cosmos gets an option to void an evaluation it doesn't like.
- **V6-2: the package is extracted only after the key is read and deleted** (`runner.py:612-614` then `:646`).
  - The early validation doesn't check whether member names can actually be written. These all pass it and then fail on extraction with an uncaught OSError:
    - `a.txt` together with `a.txt/b.txt`;
    - `q?.txt` on Windows (M1);
    - a 300-character name.
  - The result is the same deadlock, and Cosmos can trigger it on purpose.
  - The v5 verdict asked for the package to be staged before the key is read.
- **V6-3: part of the isolation probe still runs after the key is read.**
  - The check that the child can't read or append to `receipts.jsonl` runs only in `_start_worker`, after the key is read and deleted.
  - The preflight can't cover it, because the file doesn't exist yet and "missing" counts as a pass.
  - Example: on Linux with the default umask the file is world-readable, so a correctly separated child passes the preflight, then fails this probe after the release is spent.
  - This breaks the v5 condition that every probe completes before the key is read.

**Should-fix and notes**
- **V6-4:** the preflight record custody requires is plain, self-reported JSON with no host binding. Anyone who can write the output folder can forge it, including the runner account; the self-test itself hand-writes one to pass the release.
- **V6-5:** the output folder that the runner account must write to is the same folder that holds `ALLOWLIST.json`, the custody log and the custody lock. A second account could then create the lock (blocking release and reveal) or replace the allow-list. Whether it can depends on M1's permissions on that folder, which I can't see.
- **V6-6:** a residual that isn't declared. Resume is refused, so any crash after the key is read (out of memory, power loss, full disk, the predictor child failing to start) permanently deadlocks the spec_id.

The four declared residual risks are acceptable as written. The list should add V6-6, V6-5 and the self-reported preflight record (V6-4).

OVERALL: FAIL