Audited commit is `742243972e6e`, which has the same audited code as origin/main `7c12fb175`. I read the code and used read-only git only; I did not run the selftests or the protocol module, because this worker may not execute code. For DEF-HARM-D2-001 I rebuilt the SEAL-gate git query by hand instead.

**Verdict per claim**
- **Claim 1, Opacity: HOLDS.**
  - AES-256-GCM with random key and IV, salted commitment.
  - Receipt chain heads and the result hash can't be brute-forced, because every receipt carries a keyed HMAC tag.
  - The only public leak is the plaintext length in `ciphertext_bytes`, which is already declared.
- **Claim 2, Secrets never in git: HOLDS on the repo side.** No key, salt or plaintext file appears anywhere in history. The key-holder scan is CANNOT-VERIFY: it doesn't require `--all-history`, doesn't search seeds in history, and doesn't scan comms.
- **Claim 3, Enforced order: BROKEN** (P1, P2, P3 below; S1 still open).
  - What holds: the gates run before the key is read, and refs must be fully qualified.
  - The added-once rule also holds, and the SEAL gate passes on the real origin/main history. Each sealed file has one blob and one non-merge add, in `95b31a30d`, which matches the pinned seal commit.
- **Claim 4, Controlled reveal: HOLDS in the gate logic,** but reveal and the evidence bundle can't be reached through `entry.py` (P3). Note: `--dest` for the released key accepts any path, including a network share on M2.
- **Claim 5, Predictor isolation: HOLDS as stated,** because it fails closed.
  - Every real run is refused with `ChildNotIsolated`: the child runs as the runner's own account, and no code exists to start it under another.
  - Should-fix: the AST audit misses `from numpy import fromfile as ff` and similar aliased imports.
  - Should-fix: nothing blocks the child's network access, so a package could stream what it observes to M2 or fetch logic its hash doesn't cover.
- **Claim 6, Draw integrity: HOLDS.** `draw.py`, `sealbox.py` and `__init__.py` are byte-identical to the seal commit. Whether they match the at-draw sha256 values in the manifest is CANNOT-VERIFY; it needs a hash run.
- **B1, `entry.py` loads only bound code: BROKEN** (P1 and P2).

**Blocks-PASS findings**
- **P1 (`entry.py:17-24,145`):** the first stage runs by file path without isolation, so the package directory comes first on `sys.path`.
  - It imports `json`, `hashlib`, `subprocess` and `pathlib` before anything is checked, and nothing refuses extra files in `c3_holdout_D2/`.
  - A committed `c3_holdout_D2/json.py` would run as the custodian account before verification and could read and push the key.
- **P2 (`entry.py:60-61,162`):** in the verified key-holding process the repo root is first on `sys.path`, and the import guard covers only `prometheus.*`.
  - A root-level `__future__.py`, `numpy.py`, `argparse.py` or `scipy/` would be loaded without any binding. The loaded-module check doesn't see it either.
  - The repo root has no such file today; the next commit to main could add one.
- **P3 (`entry.py:33` against `protocol.py:63-65` and `custody.py:126`):** `entry.py`'s allowed record names leave out `KEY_RELEASED.json` and `REVEALED.json`.
  - Once the key-release record is committed as instructed, `entry.py` refuses the runner, reveal and evidence, so the protocol deadlocks.
  - The selftest never runs `entry.py` end to end, which is why it wasn't caught.
- **S1 (known open, #925):** protocol records are still unauthenticated. The comms sender field is client-supplied, the allow-list is a plain file, and main is unprotected.

**Main should-fix items** (full list with `file:line` evidence in `findings.md`)
- Tools that hold secrets run outside `entry.py`:
  - `firewall_check.py`, which loads key, salt and plaintext, is started with `python -m`, so a committed unchecked-hash `.pyc` would execute in it.
  - `allowlist.py` runs as the custodian account and imports `comms`.
- `entry.py` picks the highest-numbered audit before filtering by the allow-list, so any unauthenticated later audit file blocks every key-holding command.
- `entry.py` ignores a failed `git fetch` and silently checks a stale origin/main.
- Needs confirmation on M1: on Windows, `git` may be found in the current directory before PATH, so a committed `git.exe` at the repo root could run.

**Residual risks:** the "key holder" residual is incomplete. It should say that the operator account runs code from main, which Cosmos can write, and the protocol's own tools do this. Also missing from the list:
- child network egress;
- third-party and site-packages code running in the key-holding process;
- the unrestricted `--dest` path;
- the protocol being impossible to run end to end today.

No `FIREWALL_AUDIT_1.json` was produced, since the verdict is FAIL and this worker is read-only.

Files are in `/home/jcraig/fabric-work/worker.ubu001/attempts/att-c752d7f08d56/out`:
- findings.md

OVERALL: FAIL