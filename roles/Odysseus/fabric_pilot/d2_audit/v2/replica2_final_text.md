My last response was stopped by a safety classifier while I was writing `findings.md`. **Nothing was written: the output directory is empty.** Below is a shorter summary, without step-by-step attack detail.

Limits of this audit: Bash and access to the git object store were denied here, so I couldn't run any `git log`, `git show` or sha256. Everything that depends on history or on a hash value is CANNOT-VERIFY. The rest comes from reading code at f4cde414d.

## Verdict per claim
1. **Opacity: HOLDS in the code and in the public files.** AES-256-GCM with the AAD bound to the family hash (`sealbox.py:60-80`); a 32-byte salt (`sealbox.py:64-67`). The manifest and both `SELFTEST_*.json` files carry nothing secret. The known plaintext-length leak is already declared. I couldn't check the actual ciphertext and manifest hash values.
2. **Secrets never in git: CANNOT-VERIFY-FROM-REPO.** Running the brief's `git log --all` and `git grep` over all revisions would settle it.
   - Should-fix: `firewall_check.py:112` passes the key, salt and nonce hex as `git log -S` command-line arguments. That contradicts the module docstring and exposes them to process listing and command-line logging on M1.
3. **Enforced order: BROKEN** (B1, B2 below). The ordering, full-history and fully-qualified-ref checks are otherwise correct as written (`protocol.py:164-200, 322-413`).
4. **Controlled reveal: HOLDS, with should-fix items.**
   - `RESULT_SEAL.json` is not on the allow-list, so anyone who can push can block the real seal (denial of service only).
   - An unauthenticated higher-numbered FAIL audit also supersedes the governing one (`protocol.py:336`, checked before the allow-list).
   - "Once only" rests on a log file that can be edited (`custody.py:113, 174`).
   - The `result-seal` subcommand does not require `entry.py`.
5. **Predictor isolation: HOLDS for its three narrow claims** (separate process, pickle-free pipe, type-name-only errors).
   - Should-fix: production adds `receipts.jsonl` to the probe (`runner.py:817`). The child runs as the same account, so it can open that file, and the real run should always stop with `ChildNotIsolated`. The self-test's positive path probes a path that doesn't exist instead (`selftest_protocol.py:389`).
   - Should-fix: the same-account child can write the run's receipts, and the receipt chain has no key.
   - Should-fix: the default output directory is the same directory as `ALLOWLIST.json` and `custody.jsonl`.
6. **Draw integrity: HOLDS in the code.** The nonce comes from the OS CSPRNG, the draw is uniform over the lattice, exposed-D worlds are rejected, and `verify_reveal --redraw` reproduces it (`draw.py:62-72`, `medium.py:228-236`). I couldn't check that the files on main hash to the at-draw values. Note: the redraw needs numpy 2.2.6, since NumPy doesn't promise the same random stream across versions.

## Blocks-PASS findings
- **B1: the F1 "verified before import" guarantee is incomplete.**
  - `entry.py` and `check_gates` check the bytes of the files in `AUDITED_FILES`. They don't control which file Python actually loads for an import.
  - `entry.py` runs with its own directory first on the import path. Afterwards it puts the repo root first (`entry.py:17-24, 112`).
  - Shadowing packages, extension modules or `__pycache__` bytecode in the wrong place are not refused. The only shadow check covers `protocol/` (`protocol.py:208-217`).
  - The loaded-module check only inspects `prometheus.*` modules, only after they have run, and hashes the `.py` file rather than what was executed (`protocol.py:236-258`).
  - With push access to main (which Cosmos has, and branch protection is off), unaudited code can run in a key-holding process.
  - The fix is to run with `-I`/`-P` and `-B`, and to refuse any file not in the audited tree across the import paths.
- **B2: the S1 allow-list trusts an unauthenticated comms sender.**
  - `allowlist.py:62` checks only the `sender` column.
  - That value is whatever the client passes (`comms/__main__.py:30`, `comms/api.py:159-163`), and the database credentials are shared (`evidence_wiki/ew/db.py:14-29`).
  - So a record whose allow-list message claims to be from "Odysseus" or "Nestor" proves nothing.
  - In addition, `allowlist.py` imports unaudited `comms` and `evidence_wiki` code under the custodian account.

## Residual risks
The four declared residuals are acceptable as stated. These are missing from the list:
- other unverified code that runs under the custodian account (`allowlist.py`, `result-seal`, the self-tests, `firewall_check`);
- third-party libraries (numpy, scipy, cryptography) and interpreter start-up hooks are not bound by the audit;
- the same-account child can tamper with results;
- the two denial-of-service paths in claim 4.

OVERALL: FAIL