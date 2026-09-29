The D2 v3 firewall still fails: B1 (import control) is broken in a way that has nothing to do with S1, so S1 is not the only gap left. I audited commit 742243972; no audited file has changed on origin/main since then. The full audit is in `out/findings.md`.

I did not run any Python, because the skill says the auditor cannot run code. So I did not execute `python -m ...protocol` as the brief asked. Instead I re-ran by hand, with read-only git, the two history queries the seal check depends on, and checked hashes with `sha256sum`. Every public hash in the brief matches, and the files that must not change since the seal (the original D files, `draw.py`, `sealbox.py`, `medium.py`) have not. The B1 import-shadowing results are reasoned from documented Python import behaviour, not from a run.

**Verdicts per claim**
1. Opacity: **HOLDS**. The only leak is the plaintext length in the manifest, which is already declared. The AES key is also reused as the HMAC key; no attack follows from it.
2. Secrets never in git: **HOLDS** for filenames and history; no key-, salt- or plaintext-shaped file was ever added. Whether the actual key bytes appear anywhere is **CANNOT-VERIFY-FROM-REPO**; that needs Nestor's key-holder scan (`firewall_check --all-history`).
3. Enforced order: **HOLDS** for the ordering logic (ref shadowing, merge replacement, ancestry, stale-code check, gates run before the key is read). Should-fix:
   - **S-1:** `entry.py` does not list `KEY_RELEASED.json` or `REVEALED.json` as allowed records. Once the key is released, every later run, reveal and evidence step through the entry is refused, so the protocol cannot finish.
   - **S-2:** `entry.py` picks the highest-numbered audit even if it is not allow-listed. Anyone who adds a `FIREWALL_AUDIT_2.json` can block every key-holding command.
   - **S-3:** a failed `git fetch` is ignored, and `C3D2_NO_FETCH=1` skips it. A stale origin/main can hide a later allow-listed FAIL, so an old PASS keeps governing.
   - Notes: the ref can be chosen on the command line; git replace refs are not disabled; the order is by commit ancestry, not by who authored the record.
4. Controlled reveal: **HOLDS** in its gating logic. Notes: the host check is `gethostname()`; `--dest` may be a network path (e.g. `\\SPECTREX5\share`); the released key file's permissions are not set; a committed `KEY_RELEASED`/`REVEALED` record is checked for presence only, so anyone can commit one and block the release.
5. Predictor isolation: **HOLDS** in its narrow properties. The static package check can be bypassed (`gate.sys.modules["builtins"].exec(...)`), which is within the declared "heuristic" risk. The predictor child always shares the runner's account, so the isolation probe always refuses and a real run cannot complete as coded.
6. Draw integrity: **HOLDS**. The only gap: the redraw at reveal does not itself check `draw.py` and `medium.py` against the manifest hashes.
- DEF-HARM-D2-001 (seal gate on the real history): **HOLDS**. Each sealed file has one content version across full history, added only by 95b31a30d, which equals the pinned seal commit.
- B1 (import control): **BROKEN**, blocks-PASS.

**Blocks-PASS findings**
- **B1-a:** The documented call `python <repo>/.../entry.py ...` starts without isolation, so Python puts the script's own folder first on the import path. `entry.py` then imports `json`, `hashlib`, `subprocess`, `re` and `pathlib` before checking anything. Suppose a commit adds a file such as `prometheus/cosmos/c3_holdout_D2/json.py`, which no check covers. The honest, fully hash-matching `entry.py` then runs it as the custodian, who can read the key.
- **B1-b:** Inside the isolated process, `entry.py` puts the repository root first on the import path. The import guard and the loaded-module check only cover names starting with `prometheus`. A new top-level `argparse.py`, `hmac.py` or `numpy/` at the repo root would therefore load unverified inside the custody or runner process that reads the key.

Neither attack needs a forged protocol record, only one extra ordinary file on main, and branch protection is off.

Two related should-fix items:
- `firewall_check`, `custody result-seal` and `evidence` run as the custodian without going through the entry at all. There, a committed `.pyc` file would be loaded without looking at the unchanged source.
- `entry.py` checks its own hash only after it is already running, so a modified copy simply skips the check.

The declared residual risks are acceptable as written, but the list is missing:
- the B1 vectors and the stale-fetch problem;
- that the custodian account routinely runs repository code;
- how the runner account gets read access to the allow-list under the custodian's profile without exposing the secrets folder, which I can't verify from the repo;
- that the production run cannot complete as coded.

No FIREWALL_AUDIT record should be committed for this commit.

OVERALL: FAIL