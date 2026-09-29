# Holdout D2 firewall audit, v3: independent adversarial replica

- Skill: audit.security.adversarial (v1). Task tsk-ddfc5156be0d, attempt att-29d5f75da6ea, 2026-09-29.
- **Audited commit: 742243972e6e5b334d0f4787470c39897140cb02.** This is v3 = 05211e20b plus a merge that does not
  touch the audited paths. `refs/remotes/origin/main` (7c12fb175) contains 05211e20b. Between 742243972 and
  origin/main, no commit touches `prometheus/cosmos/c3_holdout_D2`, `c3`, `c3_holdout_D` or the package
  `__init__` files (`rogit log 742243972..refs/remotes/origin/main -- ...` returns nothing).
- Scope: the firewall layer only. No law, prediction or science content was read.
- **Method and limits.** I read the code and ran read-only git (`rogit`) and `sha256sum`. I did not execute any
  Python (the skill says "you cannot run code"). The brief asks for `python -m ...protocol` on the real history.
  In its place I reproduced by hand the exact git queries the SEAL gate uses (below). Every import-semantics
  statement in B1 is derived from documented CPython behaviour, not from a run. Each B1 item includes a
  reproduction recipe the self-test runner can execute.

## Verification of the public commitments (done, all match)

| item | evidence | result |
|---|---|---|
| sha256(hidden_D2.enc) = f75ba333... | `sha256sum` of the checkout; MANIFEST_D2.json:7 | match |
| sha256(MANIFEST_D2.json) = 78874e9d... | `sha256sum` | match |
| spec_id / commitment | MANIFEST_D2.json:8,34 equal the brief | match (spec_id recomputation needs Python: not run) |
| draw.py / sealbox.py / `__init__.py` at-draw hashes | `sha256sum`: 800e0b5d..., dec9b915..., d38d3b0c... = MANIFEST_D2.json:12-14 | match; git history shows these three files changed only in 95b31a30d |
| medium.py family hash | `sha256sum` 09559e69...cde4 = MANIFEST_D2.json:21 | match |
| original D byte-identical | `rogit diff --stat a56ef7787 742243972 -- prometheus/cosmos/c3_holdout_D` | empty |
| only 95b31a30d adds the sealed files | `rogit log --all --diff-filter=A` on `*hidden_D2*`, plus the full-history queries below | yes |

**DEF-HARM-D2-001, reproduced by hand.** I ran `git log --full-history -m --raw --no-abbrev --format="C %H %P"
refs/remotes/origin/main -- <file>` for both sealed files. This is the query in `protocol._record_history`
(protocol.py:182).
- hidden_D2.enc: 4 entries, ONE blob 10c7b600....
  - The only non-merge commit is the add in 95b31a30d.
  - The other three are merges (ebe1307ea, 85b198a5b, e5b95744f), each an `A` against the parent that lacks the file.
- MANIFEST_D2.json: the same pattern, ONE blob db3d442d....
- By protocol.py:209-223, `_added_once` returns 95b31a30d for both, which equals the pinned `SEAL_COMMIT`
  (protocol.py:54, 347-351).
- The SEAL gate therefore passes on the real history. This agrees with `v3_real_history_seal_passes: true` in
  SELFTEST_PROTOCOL.json.

---

## Claim 1: Opacity. Verdict: HOLDS (with the declared length note)

Attacks tried:
1. **Brute-force a candidate world against the commitment.**
   - `commitment = sha256(salt || plaintext)` with a 32-byte secret salt (sealbox.py:64-67, draw.py:104,133).
   - The plaintext also contains the 256-bit nonce (draw.py:78,154), so even an unsalted hash could not be
     confirmed by enumeration.
   - Holds.
2. **Public manifest fields that narrow content.**
   - MANIFEST_D2.json:1-36 carries: IV, sha256 hashes, versions, platform, draw_utc, n_worlds and
     `ciphertext_bytes`.
   - `ciphertext_bytes` (17227) gives the plaintext length: 17211 = 17227 - the 16-byte tag. This is a sum of
     decimal digit lengths, a negligible narrowing. It is declared (FIREWALL.md:149-150, 178).
   - `draw_utc` is public in both the manifest and the plaintext, so it adds nothing.
   - No world, knob, seed or nonce appears.
3. **Receipts and error text.**
   - Receipts name worlds by index plus `world_tag = HMAC(key, canon([w, s]))` (runner.py:568-569).
   - Replies to predictor errors carry `type(e).__name__` only (runner.py:690-691).
   - RESULT_SEAL publishes only hashes, the nonce and `n_receipts`, which is constant (custody.py:160-163).
   - The chain head posted after PREDICT is a hash over HMAC tags the predictor cannot compute, so the predictor
     cannot grind it to smuggle bits.
4. **SELFTEST_*.json.** Both contain booleans, class names of throwaway gate outcomes and repository file paths
   only (SELFTEST_D2.json, SELFTEST_PROTOCOL.json). They contain nothing derived from the hidden set.

Notes (not blocking):
- The AES key is reused as the HMAC key (runner.py:568). This is poor hygiene, but no attack follows.
- A predictor that already knows a world can signal one bit per run by crashing or refusing: whether a RESULT_SEAL
  ever appears. The capacity is negligible.

## Claim 2: Secrets never in git. Verdict: HOLDS for everything checkable; key-byte absence is CANNOT-VERIFY-FROM-REPO

Attacks tried:
1. **Key/salt/plain-shaped files anywhere in history.** `rogit log --all --diff-filter=A` over `*.key*`,
   `*.salt*`, `*.plain*`, `*nestor_secrets*`, `*hidden_D2*`, `*.hex` and `*secret*` finds only `hidden_D2.enc`
   (95b31a30d) and unrelated files: Aether `secrets.py`, nyx catalogue, ludus.
2. **Directory history.** `rogit log --all --full-history --stat -- prometheus/cosmos/c3_holdout_D2` shows only
   code, docs, the manifest, the ciphertext and SELFTEST JSON. There is no `protocol/` record yet, and no
   `__pycache__` or `.pyc` is tracked (Glob `prometheus/**/__pycache__/*.pyc`: none).
3. **Content search for the actual key/salt/nonce bytes.** This needs the secrets, so it is CANNOT-VERIFY here.
   It is settled by the key holder's `firewall_check --all-history` (firewall_check.py:84-128).
   - That scan streams every blob reachable from `rev-list --all --objects` in-process (no secret in argv).
   - Gap (note): it does not cover reflogs, unreachable objects, stashes of other clones, or other checkouts and
     repos on M1. It also skips blobs over 64 MB, although it reports the count.
   - Nestor's reported "all clean" is a custodian statement.

## Claim 3: Enforced order. Verdict: HOLDS for ordering logic; should-fix items below. The code binding is undermined by B1 (next section).

Attacks tried:
1. **Tag or branch shadowing (F3).**
   - Only `refs/...` names are accepted.
   - Refs named `refs/tags/origin/main`, `refs/heads/origin/main` or `refs/tags/main` are refused
     (protocol.py:166-176, entry.py:98-103).
   - Git's DWIM tries the literal full name first, so a fully qualified ref is unambiguous. Holds.
2. **Record replaced through a merge (F4), and a record added only by an evil merge.**
   - `_added_once` (protocol.py:199-223) requires one blob across the full `-m` history, exactly one non-merge
     add, no non-merge modification, deletion or rename, and the blob at the ref equal to that blob.
   - An evil merge that introduces the record has 0 non-merge adds, so it is refused.
   - A replacement through a merge brings a second blob, so it is refused. Holds.
3. **Commitment before the audit, same commit, audit before the seal.**
   - Strict ancestry is required between the adding commits (protocol.py:195-196, 366-371, 405-406, 425-426,
     452-453).
   - Commit hashes chain parents, so ancestry cannot be forged. Holds.
4. **Code changed after the audit.**
   - Every file in `AUDITED_FILES` is compared for the committed tree AND the working tree (protocol.py:380-389).
   - `set(bound) == set(AUDITED_FILES)` is required (protocol.py:381). Holds for those files. It does not cover
     code outside that list that still executes (B1).
5. **Refuse before the key is touched.**
   - Runner: `check_gates` runs at runner.py:537 before `read_hex_file` at runner.py:558. `main` also gates at
     runner.py:842.
   - custody release-key: gates at custody.py:112 before the key read at custody.py:117.
   - reveal: gates at custody.py:174 before reading the secrets at custody.py:192. Holds.
6. **Unauthenticated later audit supersedes.** protocol.py:360-365 considers ONLY allow-listed audits. That holds
   in `protocol.py`, but `entry.py` does not do the same (S-2 below).

Should-fix findings under claim 3:
- **S-1 (liveness, forces a code change): entry.py cannot run after a key release.**
  - `entry.FIXED` = {PREDICTION_COMMITMENT, RUNNER_DESIGNATION, RESULT_SEAL} (entry.py:33). It lacks
    `KEY_RELEASED.json` and `REVEALED.json`, which `protocol.FIXED_RECORDS` allows (protocol.py:63-65).
  - `release_key` writes `protocol/KEY_RELEASED.json` into the working tree at once (custody.py:126, 129-136).
    `entry.verify` scans working-tree and committed names (entry.py:104-111).
  - Scenario: Nestor runs release-key, then the designated runner runs `entry.py runner ...`. The result is
    `REFUSED: unexpected files in .../protocol: KEY_RELEASED.json`. The same refusal hits every later reveal and
    evidence run.
  - Step 6 (run) can therefore never follow step 5 through the mandated entry. It fails closed, but the audited
    code cannot complete the protocol, and the repair changes a bound file.
  - The self-test never drives `entry.py` on the positive path (selftest_protocol.py:323-338 only checks
    refusals), so it cannot catch this.
- **S-2 (DoS; inconsistent with the v3 repair): entry.py picks the governing audit differently.**
  - entry.py:112-127 takes the highest-n audit among committed AND working-tree names, then requires THAT one to be
    allow-listed. `protocol.py` ignores records that are not allow-listed.
  - Anyone who lands `protocol/FIREWALL_AUDIT_2.json` (any content) on main, or drops it in the working tree, makes
    every key-holding CLI refuse. This fails closed, but it is exactly the "unauthenticated later record governs"
    behaviour v3 says it removed.
- **S-3 (freshness bypass): a failed or disabled fetch is silently accepted.**
  - `subprocess.run(["git", "fetch", ...])` has its return code ignored (entry.py:97), and `C3D2_NO_FETCH=1` skips
    the fetch (entry.py:151; `-I` does not strip non-`PYTHON*` variables).
  - Scenario: the auditor records an allow-listed FIREWALL_AUDIT_2 (FAIL) on origin, and the custodian allow-lists
    it. If M1's fetch fails (network, auth, or an env var), `refs/remotes/origin/main` is stale and lacks _2.
    `protocol.py` then governs with the old PASS, because the allow-list entry for _2 has no committed record.
  - S2 supersession ("a later FAIL supersedes") is thereby bypassed. Refuse when the fetch fails, and drop or log
    the env override.
- **S-4 (note): the gate ref is chosen on the command line.**
  - `--gate-ref` / `--ref` accept any fully qualified ref (runner.py:829,842; custody.py:216; evidence.py:93).
  - `entry.py` verifies the audit on origin/main only, but the commitment, designation and result seal can then be
    read from another ref, e.g. `refs/remotes/origin/<side-branch>`.
  - Only the operator controls this. Pin it to `DEFAULT_REF` in the key-holding CLIs.
- **S-5 (note, class 4): git replace refs and grafts are not disabled.**
  - None of the git calls set `GIT_NO_REPLACE_OBJECTS=1` / `--no-replace-objects`.
  - A local `refs/replace/<commit>` would change what `log`, `show`, `ls-tree` and `merge-base` report.
  - This needs local write access to the M1 repo (not the default fetch refspec), so it is a note.
- **S-6 (note): ordering is by ancestry, not by author or time.**
  - Record bytes are predictable: the audit record is fully determined by public values.
  - Any pusher can author the commit that adds a byte-identical audit record, and the allow-list keys on content
    only.
  - This does not leak anything, but "audit commit" does not mean "committed by the auditor". It is part of the
    OPEN S1 question.

## B1 (v3): "entry path loads only audited code". Verdict: BROKEN, severity blocks-PASS

The v3 claim (FIREWALL.md:165; entry.py:51-54, 145-150) is that no unbound code can load on the entry path. The
guard, however, covers only module names that start with `prometheus` (entry.py:60). `loaded_closure` likewise
checks only `prometheus.*` (protocol.py:265). Everything else resolves through `sys.path`, and the repository
itself is placed on `sys.path` twice.

**B1-a: script-directory shadowing in the first (non-isolated) entry process.**
- The documented invocation is `python <repo>/prometheus/cosmos/c3_holdout_D2/entry.py custody release-key ...`
  (entry.py:3, FIREWALL.md:132).
- That first process is NOT isolated: `-I -B` is added only by the re-exec at entry.py:145-150. CPython therefore
  prepends the script's directory, `prometheus/cosmos/c3_holdout_D2/`, to `sys.path`.
- entry.py:17-24 then imports `hashlib`, `json`, `re`, `subprocess` and `pathlib`. None of these is preloaded at
  interpreter startup; only `sys`, `os` and `site` are guaranteed.
- Scenario:
  - A commit lands on main that adds `prometheus/cosmos/c3_holdout_D2/json.py` (or `hashlib.py`, `subprocess.py`,
    `fnmatch.py`, ...).
  - The file is not in `AUDITED_FILES`, and no gate looks for extra files outside `protocol/`
    (protocol.py:231-240, entry.py:104-111).
  - Nestor checks out main, and every audited file still hashes correctly.
  - Nestor runs the honest, unmodified entry.py as the custodian.
  - The attacker's `json.py` executes at entry.py:18, BEFORE `verify()`, as the custodian account. It reads
    `C:/Users/jcrai/nestor_secrets/holdout_D2/hidden_D2.key.hex` and the salt/plaintext, then imports the real
    `json` so everything proceeds normally.
- Reproduction (self-test runner): in a throwaway copy of the repository, create `c3_holdout_D2/json.py` containing
  `open("/tmp/pwned","w").write("x")` followed by the stdlib-restoring import. Run `python <copy>/.../entry.py
  runner --help` and check that `/tmp/pwned` exists even though entry refuses.

**B1-b: repository-root shadowing inside the isolated, key-holding child.**
- After `verify()`, entry.py:162 sets `sys.path[:] = [str(REPO)] + <interpreter paths>`, with the repo root FIRST.
- The guard returns `None` for every non-`prometheus` name (entry.py:60-61), so normal path search applies.
- Modules that are first imported after that line include:
  - custody: `argparse`, `datetime`, `socket` (custody.py:29-33);
  - protocol: `typing` (protocol.py:44);
  - sealbox: `secrets`, `cryptography` (sealbox.py:15-17);
  - runner: `argparse`, `ast`, `base64`, `hmac`, `multiprocessing`, `zipfile` (runner.py:54-66), `numpy`
    (runner.py:70), and `ctypes` at runner.py:261.
- Scenario:
  - A commit on main adds a top-level `argparse.py`, `hmac.py` or `numpy/__init__.py` at the repo root. The root
    already holds dozens of top-level packages, so a new one draws no attention.
  - `entry.py custody release-key` (custodian account), or `entry.py runner` (runner process, which reads the
    released key at runner.py:558), imports the attacker module.
  - The module can patch `sealbox.read_hex_file`/`builtins.open` and exfiltrate the key when it is read.
- `check_gates(verify_loaded=True)` cannot see it, because `loaded_closure` filters to `prometheus*` (protocol.py:265).

**B1-c (should-fix): other key-reading tools bypass entry.py entirely.**
- `firewall_check.py` reads key, salt and plaintext (firewall_check.py:38-46) and is run as
  `python -m prometheus.cosmos.c3_holdout_D2.firewall_check` (firewall_check.py:3; FIREWALL.md:77) by the custodian.
- `custody result-seal` (custody.py:218 exempts it) and `evidence` (evidence.py:88-101, no `C3D2_ENTRY` check at
  all) also run as the custodian account without entry.
- FIREWALL.md:132 says runner + custody + evidence start ONLY through entry.py. Evidence and result-seal do not.
- Under `python -m`, `prometheus/__init__.py` and the package `__init__` files are imported with the normal loader.
  It honours `__pycache__`, including unchecked hash-based `.pyc` files (PEP 552), which load without looking at
  the source. `sys.path[0]` is also the current directory.
- A tracked `prometheus/__pycache__/__init__.cpython-312.pyc` (committable with `git add -f` despite .gitignore:78)
  runs attacker code in the custodian process. `AUDITED_FILES` hashes cannot see it, because the `.py` file is
  unchanged.

**B1-d (should-fix): entry.py verifies itself.**
- entry.py checks its own hash (entry.py:128-137) only after it is already running.
- A modified `entry.py` that lands on main simply skips the check.
- The entry file, plus a clean directory, must be verified before execution. For example, run a `git archive` of
  the audited commit restricted to `AUDITED_FILES` into a fresh directory, and start it with `python -I -B -P`.

Why this is not S1: none of these vectors needs a forged protocol record. They need a benign-looking non-record file
on main, which is possible today (branch protection is OFF, declared at FIREWALL.md:147-148, 176). Even with branch
protection on, a reviewer has no reason to suspect a new top-level module. The v3 goal "remaining gap is S1 alone" is
therefore not met.

Suggested repair:
- Remove the script directory from `sys.path` as the very first statement (`import sys; del sys.path[0]` before any
  other import), or require an `-I -P` launcher.
- Never put `REPO` on `sys.path`. Instead, make the guard the only finder for `prometheus*` (use its own
  `ModuleSpec` with the repo path) and keep `sys.path` equal to the interpreter's stdlib/site-packages only.
- Extend `loaded_closure` to refuse ANY loaded module whose file lies inside the repo and is not bound.
- Route firewall_check, result-seal and evidence through entry, and enforce `C3D2_ENTRY` in all of them.

## Claim 4: Controlled reveal. Verdict: HOLDS in gating logic; notes

Attacks tried:
1. **Reveal before the result seal, twice, with a tampered RESULT or a truncated chain.**
   - `check_gates("RESULT_SEAL")` is required, and RESULT_SEAL must be allow-listed (protocol.py:445-453).
   - The chain, close record, package, spec_id and nonce are re-verified (custody.py:176-185).
   - Once-only uses the custody log plus a committed REVEALED record (custody.py:186-189). Holds.
2. **Key release to M2 or to the wrong runner.**
   - The designated host must not be SPECTREX5, and the current host must equal it (protocol.py:421-432).
   - custody refuses on a forbidden host (custody.py:99-100). The runner id and account are checked
     (protocol.py:433-436).
   - Notes:
     - The host is `socket.gethostname()` (class 7, spoofable by a host admin). The real boundary is that the key
       never leaves M1.
     - `--dest` may be a UNC path such as `\\SPECTREX5\share`. `_dest_ok` (custody.py:94-100) checks git, the
       secrets dir and the local host only, so "never M2" rests on the custodian not choosing such a path.
     - The released key file's ACL is not set, so any account that can read DEST can read the key.
3. **Results public as hashes only until the seal.** The evidence bundle is refused before the RESULT_SEAL gate
   (evidence.py:55-61). Holds.
4. **Notes:**
   - A KEY_RELEASED/REVEALED record is presence-only and unvalidated (protocol.py:306-309). Anyone who commits
     one blocks release or reveal (DoS).
   - Once-only via git needs a commit + push + fetch before a second attempt. Until then, only the editable log
     guards.
   - Combined with S-1, the committed KEY_RELEASED record also locks out the run.

## Claim 5: Predictor isolation. Verdict: HOLDS in its narrow properties; declared-heuristic bypass noted

Attacks tried:
1. **Key or plaintext reachable in the child.**
   - The child is started with the `spawn` context (runner.py:612-615), so no memory is inherited.
   - With `delete_key=True` (runner.py:559-560, 851) the key file is deleted before any child exists.
   - The probe refuses a child that can read the key path, a secret path or the receipts, or append to the
     receipts (runner.py:617-625, 240-255, 852).
   - With the child on the runner's own account this ALWAYS fails closed (runner.py:516-520; FIREWALL.md:170).
     Note: no code path exists to run a `multiprocessing` spawn child under another account, so the production
     run cannot complete as coded.
2. **Pickle or code injection over the pipe.** JSON plus `np.save/np.load(allow_pickle=False)` (runner.py:160-193)
   is safe.
3. **Error-text leak.** Only type names are sent (runner.py:690-691). Holds.
4. **AST audit bypass (class 3; declared a heuristic).**
   - `from prometheus.cosmos.c3 import gate` is allowed (runner.py:397). gate.py:9 imports `sys`.
   - `gate.sys.modules["builtins"].exec(src)` defeats the audit: `.sys`, `.modules` and `.exec` are not in
     `FORBIDDEN_ATTRS` (runner.py:106-109), and no bare `exec` name appears.
   - `os.execv`/`os.startfile` through the same route are not flagged either.
   - This is acceptable ONLY because the OS-level probe, not the AST audit, is the gate.
5. **Note:** the spawn child re-imports `prometheus...runner` WITHOUT the import guard (meta_path is not
   inherited), from `sys.path` = [REPO, ...].
   - It will load a planted `__pycache__` `.pyc`, so the probe code `_worker_main` / `_probe_paths` can be
     replaced.
   - Once a separate-account child exists, the probe result must not be trusted from child-side code (probe from
     the parent under the child's token instead).

## Claim 6: Draw integrity. Verdict: HOLDS (single-draw provenance declared)

Attacks tried:
1. **CSPRNG.** `secrets.token_hex(32)` (draw.py:154), then `default_rng(int(nonce,16) mod 2^128)` (draw.py:63). That
   gives 128 bits of seed entropy. Holds.
2. **Uniformity.**
   - `medium.draw_worlds` picks per-knob uniform values with WHOLE-world rejection on the geometric constraint
     (medium.py:228-236). That is uniform over the valid lattice.
   - Exposed-D worlds are rejected (draw.py:67-69). medium.py is unchanged (hash matches).
3. **Reproducible from the nonce.**
   - `verify_reveal --redraw` recomputes the worlds, seeds and rejection count (verify_reveal.py:54-58).
   - Note: the redraw uses the CURRENT draw.py/medium.py and does not itself compare them with
     `d2_src_sha256_at_draw` / `family_src_sha256`. Add that check.
4. **Hashes on main equal the at-draw values.** Verified with `sha256sum` (table above).

## Other v3 items

| v3 item | verdict | evidence |
|---|---|---|
| DEF-HARM-D2-001 seal gate on the real history | HOLDS | manual reproduction above |
| only allow-listed audits govern | HOLDS in protocol.py:360-365; NOT in entry.py (S-2) | |
| RESULT_SEAL allow-listed | HOLDS | protocol.py:447 |
| once-only via git records | HOLDS, but deadlocks entry (S-1) | custody.py:115,188 |
| firewall_check: no secret in argv | HOLDS | patterns go to a file (firewall_check.py:146-153); oids go over stdin (:103-110) |
| receipts write-probe | HOLDS (fail-closed) | runner.py:240-255, 519-520 |
| OS account from API | HOLDS | runner.py:258-268 |
| B1 import control | BROKEN | above |
| S1 authentication | OPEN (declared, not assessed further) | allowlist.py:30-32 |

## Declared residual risks

1. **Gates are no boundary against the key holder.** Acceptable as declared. Missing from the declaration:
   - The custodian account is an agent seat that routinely executes repository code.
   - Every `python -m prometheus...` run, self-test or tool run by that account is a potential key reader.
   - The entry guard covers only runner/custody release-key/reveal, and B1 shows even those leak.
   - Declare this explicitly, or require that nothing but the pinned entry ever runs as the custodian with the
     working tree.
2. **The AST audit is a heuristic.** Acceptable, provided the separate-account child exists (it does not yet; the
   run fails closed until it does). Record the concrete bypass (Claim 5, attack 4) so no one relies on the audit.
3. **Single-draw provenance.** Acceptable. It is a custodian statement, and the manifest hashes of draw.py match.
4. **The System interface exposes physics.** Acceptable by contract.

Missing from the list:
- B1-a/b/c/d (unbound code through `sys.path` and `.pyc`, outside the `prometheus*` guard).
- A stale reference after a failed fetch (S-3).
- The runner account needs read access to `C:/Users/jcrai/nestor_receipts/.../ALLOWLIST.json` and write access to
  the out-root under the custodian's profile (protocol.py:56, runner.py:83). How that ACL is granted without
  exposing `nestor_secrets` cannot be verified from the repo. The operator's ACL listing would settle it.
- The released-key file's ACL and the UNC `--dest` path (Claim 4).
- The production run cannot complete as coded: S-1 plus the same-account child.

## Overall

- Blocks-PASS: **B1 (a, b)**. An honest, fully hash-matching tree plus one extra unaudited file (`json.py` beside
  entry.py, or `argparse.py`/`hmac.py`/`numpy/` at the repo root) runs attacker code as the custodian or the
  key-holding runner, before or around the key read.
- The remaining gap is therefore NOT S1 alone.
- No FIREWALL_AUDIT record should be written for this commit.

OVERALL: FAIL
