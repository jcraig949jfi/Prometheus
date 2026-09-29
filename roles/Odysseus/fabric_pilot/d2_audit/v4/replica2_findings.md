# Holdout D2 firewall re-audit v4: adversarial findings (audit.security.adversarial v1)

- **Task / attempt:** tsk-93bad7474ae7 / att-64d56c6c4816. Disposable worker with no seat identity.
- **Audited commit:** `e6e482ae60400cc90a4c5c3a3bc543721acafac4`. It is on `refs/remotes/origin/main`
  (`rogit branch -a --contains e6e482ae6`).
  - `rogit diff --stat e6e482ae6 refs/remotes/origin/main -- prometheus/__init__.py prometheus/cosmos` is empty, so no
    audited path has changed on origin/main since this commit (origin/main tip at the time: b049b4058).
- **Scope:** the firewall layer only (custody, opacity, commitments, enforced order, leak behaviour). Nothing about the
  law or the science.
- **Method:** I read the code and the history with `rogit`.
  - I executed NOTHING: workers cannot run code, and `sha256sum` was also denied in this sandbox.
  - Every interpreter, OS or git behaviour cited below is documented CPython / Windows / git behaviour, or the
    project's own committed self-test evidence.
  - Where this matters I say CANNOT-VERIFY and name the test that would settle it.

---------------------------------------------------------------------------------------------------------------------

## 1. Blocking finding

### B-1 (blocks-PASS): the F-CWD repair is incomplete. The key-holding custody process runs `icacls` by bare name, so an `icacls.exe` in the current directory runs with the key just released

**Evidence**
- `custody.py:141`: `subprocess.run(["icacls", str(path), "/inheritance:r", ...])` uses a bare program name.
  - It runs inside `Custody.release_key` (`custody.py:169`), right after the key has been read from the secrets
    directory and written to `dest` (`custody.py:165-167`).
- The v4 F-CWD fix covers only git:
  - `entry.git_exe`/`git_env` (`entry.py:95-122`), `protocol.git_exe`/`git_env` (`protocol.py:158-185`), and
    firewall_check through protocol (`firewall_check.py:61-63`);
  - FIREWALL.md:197 lists "(entry, protocol, firewall_check)".
- `git_env()` returns a COPY with `NoDefaultCurrentDirectoryInExePath=1` (`entry.py:118-122`). `os.environ` of the
  key-holding process is never changed, so the `icacls` call inherits the custodian's shell environment.
- On M1, Python's bare-name subprocess search DOES reach the current directory. The project's own positive control
  shows it:
  - `selftest_protocol.py:677-680` runs `subprocess.run(['git', ...])` from a directory holding a planted `git.exe`;
  - `SELFTEST_PROTOCOL.json:77` records `"v4_CWD_control_cwd_git_exe_is_found": true` with
    `not_applicable_on_this_os: []` (a Windows run).
  - Windows CreateProcess also searches the parent's current directory BEFORE System32 when no path is given.
- The documented invocation runs from the repository root: `AUDIT_BRIEF.md:126`
  (`python -I -B prometheus/cosmos/c3_holdout_D2/entry.py ...`, a repo-relative path).
  - The v4 P2 and F-CWD tests use exactly that as the threat model: "the custodian's cwd is the repo root"
    (`selftest_protocol.py:641-646`, `675-683`).

**Minimal scenario**
1. An `icacls.exe` appears at the repository root. The route is the same as for the planted `git.exe` the brief asks
   about: committed to main (branch protection is off, FIREWALL.md:208) and pulled by the custodian, or planted in the
   working tree.
   - entry.py does not look for this: it checks only `protocol/` names and `*.py` in the package directory
     (`entry.py:212-224`).
2. All gates pass. The custodian, with cwd = repo root, runs
   `python -I -B prometheus/cosmos/c3_holdout_D2/entry.py custody release-key --runner-id R --dest D:\rel`.
3. `release_key` does the following:
   - reads the key (`custody.py:165`);
   - writes `D:\rel\hidden_D2.key.hex` (`:167`);
   - calls `_restrict`, which CreateProcess-resolves `icacls` to `<repo>\icacls.exe`.
4. The planted binary runs as the custodian account. It receives the key file path as argv[1] (and can read the
   secrets directory as well), exits 0, and custody reports the ACL as restricted.
5. `KEY_RELEASED` is logged and recorded as a clean release (`custody.py:174-177`).

**Why it blocks**
- v4's stated boundary is that entry.py "stops the protocol's OWN tools from executing code the audit did not bind"
  (FIREWALL.md:211).
- Here the protocol's own key-release tool executes an unbound executable at the moment the key is released. It is
  exactly the F-CWD class the brief asks to break ("a `git.exe` in the cwd"), with a different file name.

**Fix**
- Invoke `icacls` by absolute path from `GetSystemDirectoryW` (not `%SystemRoot%`, which comes from the
  environment).
- Better: set the DACL through the Win32 API, or create the file with an explicit security descriptor (this also
  closes S-3).
- Set `NoDefaultCurrentDirectoryInExePath=1` in `os.environ` at stage 2 as defence in depth.
- Add a positive control like `v4_CWD_*` with a planted `icacls.exe` through `entry.py custody release-key`.

---------------------------------------------------------------------------------------------------------------------

## 2. Claims

### Claim 1: Opacity. **HOLDS**
Attacks tried:
- (a) look for identity, knob, seed or nonce material in public fields;
- (b) brute-force the commitment or the result hash;
- (c) look for summaries in the self-test outputs, receipts and records.

Findings:
- Cipher: AES-256-GCM with a 32-byte key from `secrets` and a 12-byte random IV (`sealbox.py:48-57, 70-80`).
  - AAD = prefix + family_src_sha256 (`sealbox.py:60-61`).
- Commitment: `sha256(salt||plaintext)` with a 32-byte salt (`sealbox.py:64-67`). The plaintext also contains the
  256-bit nonce (`draw.py:78`), so a candidate world set cannot be confirmed.
- Manifest fields (`MANIFEST_D2.json:1-36`): no world, knob, seed or nonce. Only versions, the IV, hashes and
  `ciphertext_bytes` (the declared length residual, FIREWALL.md:220).
- `SELFTEST_D2.json` carries booleans only. `SELFTEST_PROTOCOL.json` carries booleans, gate-outcome class names and
  throwaway-repo path names only (`:104-151`).
- Receipts carry only index + `world_tag = HMAC(key, world||seed)` (`runner.py:591-592, 738`). The prediction child
  cannot compute these tags.
  - As a result, `result_sha256` / `chain_head` in RESULT_SEAL (`custody.py:212-215`) cannot be brute-forced, even
    though RESULT.json's other fields are low-entropy: RESULT.json embeds every world_tag (`runner.py:820-825`).
  - `n_receipts` is fixed at 1+N+1+N+1.

### Claim 2: Secrets never in git. **HOLDS (repository side); CANNOT-VERIFY (key-holder side)**
Attacks tried:
- (a) key/salt/plain-named files anywhere in history;
- (b) the seal files added more than once or on side branches;
- (c) gaps in the key-holder scan.

Findings:
- `rogit log --all --name-status -- "*.key" "*.key.*" "*.hex" "*salt*" "*.plain.json" "*nestor_secrets*" "*hidden_D2*"`
  returns ONLY `A hidden_D2.enc` in 95b31a30d.
- `rogit log --all -- "*MANIFEST_D2*" "*protocol/*"` returns only `A MANIFEST_D2.json` in 95b31a30d. No protocol
  record exists on any ref.
- `rogit log --all --stat -- prometheus/cosmos/c3_holdout_D2` shows 7 commits (95b31a30d, 06f53ae24, e66f57208,
  7d759a203, f4cde414d, 05211e20b, b6f28bd43). None adds a key, salt or plaintext file.
- Key-holder side: the booleans are Nestor's. I cannot re-run them. See S-2 on what code actually runs as
  `firewall-check`, and N-7 on the scan's gaps.
- What would settle it: Nestor re-runs `firewall-check` after S-2 is fixed. It should publish `all_clean`,
  `all_history.blobs_scanned == blobs_expected` and `blobs_skipped_large == 0`.

### Claim 3: Enforced order (`protocol.py`). **HOLDS (gate logic)**
Attacks tried:
- (a) shadow `origin/main` with tags or heads;
- (b) replace a record through a merge, or through a delete and re-add;
- (c) commit the commitment before the audit, or in the same commit;
- (d) an unauthenticated later audit;
- (e) a code change after the audit (committed or working tree);
- (f) key access before the gates.

Findings:
- Only a fully qualified ref is accepted, the shadow refs are refused, and the ref is resolved once
  (`protocol.py:198-208, 378-379`).
- Added-once rule (`protocol.py:231-255`):
  - one blob across `--full-history -m`;
  - exactly one non-merge add;
  - no D/R status.
  - An "evil merge" that adds a record only in a merge has zero non-merge adds and is refused.
- Order is ancestry-based (`protocol.py:410-414, 448, 468, 495`). A descendant commit cannot be made before its
  ancestor exists.
- Audits are filtered by the allow-list first (`protocol.py:403-408`). The binding must equal `AUDITED_FILES`
  exactly, in both the committed tree and the working tree (`protocol.py:424-432`).
- `AUDITED_FILES` (`protocol.py:74-82`) covers the import closure I traced: runner → certify/probe/system/task/medium;
  probe imports only numpy and scipy (`c3/probe.py:10-11`).
- The key is touched only after the gates:
  - runner: `runner.py:865-866` then `560-563` precede `581`;
  - custody release: `custody.py:158-164` precede `165`;
  - custody reveal: `custody.py:226-243` precede `246`.
- Remaining limits:
  - S1 is open (declared).
  - Anyone with push access can permanently brick the fixed-name records (N-5).
  - Grafts and shallow files are outside F-GITENV (S-5).

### Claim 4: Controlled reveal (`custody.py`, `evidence.py`). **BROKEN: B-1 (blocks-PASS), plus S-3**
Attacks tried:
- (a) release to M2 or a UNC path;
- (b) release twice or concurrently;
- (c) reveal or bundle before the result seal;
- (d) make the release path execute foreign code (B-1);
- (e) leave an unrestricted key copy behind (S-3).

What holds:
- Release requires designated host == this host, and custody refuses on M2 (`protocol.py:464-475`,
  `custody.py:119-120`). Since custody runs on M1, the key can only be released on M1.
- Destinations: UNC, non-fixed and OneDrive paths are refused (`custody.py:98-118`).
- Once-only uses the O_EXCL lock plus the log plus "ever committed in history" (`custody.py:122-133, 161-164`;
  `protocol.py:347-351`).
- Reveal and evidence require the allow-listed RESULT_SEAL, a verifying chain at the sealed head, and the
  RESULT.json hash (`custody.py:228-243`; `evidence.py:55-61`).

What breaks:
- **B-1** (above).
- **S-3** (below).

### Claim 5: Predictor isolation (`runner.py`). **HOLDS for the narrow properties; S-1 (availability), N-6 and N-8**
Attacks tried:
- (a) pickle injection through the pipe;
- (b) error text leaking knobs;
- (c) reaching the parent through the stub's private connection;
- (d) AST bypasses;
- (e) whether the child can start at all through entry.py.

Findings:
- The pipe carries JSON + `.npy` with `allow_pickle=False` (`runner.py:163-196`). The only pickling is the
  parent→child spawn bootstrap; the parent never unpickles anything from the child.
- Errors: the parent replies with `type(e).__name__` only (`runner.py:713-714`).
  - Hostile reply shapes are caught (`runner.py:706`).
  - `stub._HiddenWorldStub__conn` is reachable by the package, since the AST dunder rule only matches `__x__`
    (`runner.py:428-432`). But the parent serves only init/noise/step/readout_features/full_state for the current
    world (`runner.py:664-689, 715-724`), so it yields nothing beyond the interface.
- The separate process is spawned after `del key` (`runner.py:593`). The same-account memory read is declared
  (FIREWALL.md:213-216).
- The AST audit can be bypassed (N-6). This is declared a heuristic; the fail-closed probe is the real gate
  (`runner.py:640-648`).

### Claim 6: Draw integrity (`draw.py`). **HOLDS (code); hash equality CANNOT-VERIFY by me**
Attacks tried:
- (a) weak RNG;
- (b) exposed-D duplicates;
- (c) redraw code drifting from the at-draw code.

Findings:
- The nonce is `secrets.token_hex(32)` (`draw.py:154`). The seed is `int(nonce,16) mod 2^128` (`draw.py:63`):
  128-bit effective entropy, noted but not a weakness.
- Exposed-D rejection uses canonical equality (`draw.py:57-70`).
- Redraw compares the at-draw hashes and medium.py (`verify_reveal.py:57-63`).
- History: `__init__.py`, `draw.py` and `sealbox.py` in c3_holdout_D2 are touched ONLY by 95b31a30d (the `--stat`
  lists above), the same commit that wrote `d2_src_sha256_at_draw`.
- `rogit diff --stat a56ef7787 e6e482ae6 -- prometheus/cosmos/c3_holdout_D` is empty: holdout D is byte-identical
  to its seal.
- I could not compute sha256 in this sandbox. What would settle it: `sha256sum` (LF) of the three files against
  `MANIFEST_D2.json:11-15`.
- Single-draw provenance is a custodian statement (declared).

---------------------------------------------------------------------------------------------------------------------

## 3. v4 items ("break P1, P2, P3 again")

| item | verdict | evidence / attacks |
|---|---|---|
| P1: stage 1 imports from a path | **HOLDS** under `-I -B` and against script-dir plants. Overclaimed for plain `python` (N-1) | Stage 1 imports nothing before dropping `sys.path[0]` and cutting to base-prefix dirs (`entry.py:46-60`); `-S` refuses (`:49-51`); PKG_PY refuses extra `*.py` (`:220-224`). Tried: `json.py`/`subprocess.py`/`fcntl.py` in the package dir or cwd → not on the path at `import subprocess`. PYTHONPATH/usercustomize/encodings under plain `python` → run BEFORE line 1 (N-1). |
| P2: repo files in the verified process | **HOLDS** for Python imports (conditional gap N-2) | Guard: prometheus.* must be bound and verified, compiled from the hashed source (`entry.py:164-175, 189-193`); `.pyd`/`.pyc`/package-dir shadows → "no .py source" or "not bound" → refused (FileFinder order: dir, ext, .py, .pyc). Non-prometheus modules resolving into the repo → refused (`:154-163`). `sys.path` filtered (`:261-274, 285`). The loaded closure is re-checked (`protocol.py:291-322, 433-437`). But non-Python executables are not covered: **B-1**. |
| P3: records and end-to-end | Record names **HOLD** (`entry.py:78-79` = `protocol.py:66`). End-to-end for the runner through entry **BROKEN (S-1, should-fix)** | Only the `gates` target is tested end-to-end through entry (`selftest_protocol.py:616-625`); runner through entry only `--help` (`:326`); the runner e2e runs in-process (`:392-398`). |
| F-GOV | **HOLDS** | `entry.py:238-245` filters by the allow-list before picking the highest n. |
| F-FETCH | **HOLDS** | `entry.py:201-204`; ref resolved once `:208-211`. |
| F-GITENV | **HOLDS as stated** (GIT_* removed, replace refs off); **incomplete** for its threat class (S-5) | `entry.py:116-122`; `protocol.py:179-185` |
| F-CWD | **BROKEN** for `icacls` (B-1) and for `allowlist.py`'s `git` (S-4) | `custody.py:141`; `allowlist.py:40` |
| F-KH | **Partial** (S-2) | `entry.py:87-88, 284` |
| F-ONCE | **HOLDS** (N-4 ref choice) | `protocol.py:347-351`; `custody.py:122-133` |
| F-DEST | **Partial** (S-3) | `custody.py:98-118, 135-151, 165-173` |
| F-AST / F-NET | Heuristic, declared; bypass N-6 | `runner.py:92-113, 291-304` |
| claim-2 scan quality | Improved; gaps N-7 | `firewall_check.py:105-155` |
| claim-6 redraw self-check | **HOLDS** | `verify_reveal.py:57-60` |

---------------------------------------------------------------------------------------------------------------------

## 4. Should-fix findings

### S-1 (should-fix; must be fixed before any real run): the runner cannot complete through entry.py, and each attempt irreversibly burns the one-time key release
**(a) The predictor child cannot import the runner.**
- `_start_worker` uses the multiprocessing `spawn` context (`runner.py:635-638`).
- The spawn child:
  - receives the parent's `sys.path`, which entry has filtered to interpreter paths with NO repository root
    (`entry.py:285`);
  - re-runs entry.py as `__mp_main__`, where neither `main()` nor the guard runs (`entry.py:44, 294`);
  - must then unpickle `prometheus.cosmos.c3_holdout_D2.runner._worker_main`.
- With `prometheus` not on the path, that is a ModuleNotFoundError: the child dies, and `_recv` at `runner.py:643`
  raises EOFError, which nothing catches.
- If `prometheus` IS importable from site-packages on M1 (CANNOT-VERIFY), the child loads it WITHOUT the guard
  instead, and bytecode from `__pycache__` is honoured (N-8).

**(b) ChildNotIsolated has the same consequence.** It is declared to fire on every production run
(FIREWALL.md:214). It is raised from `_start_worker`.

In both cases the failure comes AFTER the released key was read and deleted (`runner.py:581-583`) and after the run
directory and receipts were created (`runner.py:612-616`). After that:
- the next attempt is refused ("run directory ... already exists", `runner.py:869-870`);
- a new release is refused once KEY_RELEASED exists (`custody.py:161-164`; `protocol.py:347-351`: "ever committed");
- so D2 cannot be evaluated without breaking the once-only records. This is a P3-class deadlock. It is not declared:
  FIREWALL.md:214 says only "fails closed".

**(c) Separate-account operation is unverified.**
- The runner must run as a non-custodian account (`protocol.py:466-467`), yet must read
  `C:/Users/jcrai/nestor_receipts/holdout_D2/ALLOWLIST.json` (`entry.py:75, 235`) and write under
  `C:/Users/jcrai/nestor_receipts` (`runner.py:83`).
- It must also run git on a repository owned by jcrai, which git refuses without `safe.directory`.
- CANNOT-VERIFY M1's ACLs.

**Fix**
- Start the worker and run the isolation probe BEFORE reading or deleting the key or creating the run directory.
- Give the child an explicit, audited import path (for example a bound child bootstrap that installs the same guard).
- Add a runner-through-entry end-to-end test.

### S-2 (should-fix): `firewall-check` never uses the governing audit
- `PRE_AUDIT.get("firewall-check")` is always non-None (`entry.py:87-88, 284`). Even after a PASS audit exists,
  `firewall-check` is bound only to "whatever is committed at origin/main" for six files.
  - Those files are `firewall_check.py`, `protocol.py`, `sealbox.py` and three `__init__` files.
  - `firewall_check.py` is in `AUDITED_FILES` (`protocol.py:79`).
- That process loads the key, salt and plaintext (`firewall_check.py:43-58`).
- Scenario: anyone with push access (branch protection is off) changes `firewall_check.py` on main. The custodian pulls
  and runs `entry.py firewall-check`, and the unaudited code executes with the secrets in memory.
- entry's docstring declares this (`entry.py:33-35`), but it is not in FIREWALL.md's residual list
  (FIREWALL.md:207-220).
- Fix: use the governing audit's binding whenever an allow-listed audit exists.

### S-3 (should-fix): key-release hygiene (F-DEST)
- On ACL failure, `_restrict` raises CustodyRefusal (`custody.py:143-144`), but the except path (`custody.py:170-173`)
  does not delete `dest/hidden_D2.key.hex`.
  - An unrestricted key copy remains, and nothing is logged as released, so a retry to another `dest` writes a second
    copy.
- The file is created with the inherited ACL and only restricted afterwards (`custody.py:148-151` then `169`). That
  leaves a race window: with a `dest` under `C:\`, BUILTIN\Users (RX) is inherited.
- "Me" comes from `os.environ["USERNAME"]` (`custody.py:140`), which contradicts the v3 "account from the OS".
- The designation `account` is not validated as a single user: `"Everyone"` or `"Users"` passes `protocol.py:466`,
  and `/grant:r Everyone:(R)` then makes the key world-readable.
  - The runner would later refuse, but the copy already exists.
  - Designations are unauthenticated while S1 is open.

### S-4 (should-fix): `allowlist.py` has none of the git hardening
- It runs `["git", "-C", ..., "show", ...]` by bare name, with the full environment and replace refs honoured, and
  uses the ref string as given (`allowlist.py:39-43`).
- It runs as the custodian account with the cwd typically at the repo root, and appends the repo root to import
  `comms.api` (`allowlist.py:46-49`).
- A `git.exe` at the repo root therefore runs as the account that can read the secrets (FIREWALL.md:210). The F-CWD
  plant works here unchanged.

### S-5 (should-fix, consistency): F-GITENV does not cover its whole threat class
- `GIT_NO_REPLACE_OBJECTS` disables replace refs only. The following remain active:
  - `.git/info/grafts` (a parent rewrite affects `merge-base --is-ancestor` and `log --full-history`);
  - `.git/shallow`;
  - repo or global config (`remote.origin.url`, fetch refspecs, `url.*.insteadOf`), with `HOME`/`XDG_CONFIG_HOME`
    not stripped (`entry.py:118-119`);
  - hooks that `git fetch` runs (`reference-transaction`, and `pre-auto-gc` through auto-gc).
- These are same-account local writes, the same class as the local replace ref the v4 test defends against
  (`selftest_protocol.py:663-674`).
- CANNOT-VERIFY that git honours grafts under `GIT_NO_REPLACE_OBJECTS=1`. What would settle it: the same positive
  control with a graft file.
- Fix: `-c core.hooksPath=<empty dir>`, `-c remote.origin.url=<pinned>`, and refuse if `info/grafts` or `shallow`
  exists.

---------------------------------------------------------------------------------------------------------------------

## 5. Notes

- **N-1:** "Plain `python entry.py` also works" (FIREWALL.md:187; `entry.py:7-12`) is overstated.
  - In non-isolated mode, PYTHONPATH (`sitecustomize.py`, even `encodings/`), user-site `.pth` files and
    `usercustomize` all run before entry.py's first line.
  - Document `-I -B` as the only invocation.
- **N-2 (conditional P2 gap):** stage 2 imports `hashlib/json/os/re/site/subprocess/pathlib` (`entry.py:62-68`) with the
  UNFILTERED `-I` path.
  - On Windows, `import subprocess` attempts non-existent modules (e.g. `fcntl`, `grp`, `pwd`), which search the
    whole path.
  - If any site-packages `.pth` adds a directory inside the repository (an editable install), a repo file such as
    `fcntl.py` runs before verification.
  - CANNOT-VERIFY M1's `.pth` files. Cheap fix: apply `interpreter_paths` at the top of stage 2, before any
    non-builtin import.
- **N-3:** `ALLOWLIST`, `SECRET_PATHS` and the log paths are Windows literals (`entry.py:75`, `protocol.py:57`,
  `runner.py:148-150`).
  - On a POSIX host they are relative to the cwd, so a committed `C:/Users/jcrai/.../ALLOWLIST.json` tree makes
    `entry.py gates` print PASSED on forged records.
  - This is informational only, because release requires M1.
- **N-4:** `--gate-ref` / `--ref` accept any `refs/...` (`runner.py:852`, `custody.py:273`, `evidence.py:93`). A local
  branch without KEY_RELEASED would re-enable release checks. Pin these to origin/main.
- **N-5:** any pusher can brick PREDICTION_COMMITMENT or RUNNER_DESIGNATION permanently by putting a second blob at the
  path anywhere in main's history, for example a side branch merged with `-s ours` (`protocol.py:241-246`).
  - Only KEY_RELEASED/REVEALED are declared (FIREWALL.md:219).
  - This is denial of service, not a leak.
- **N-6:** the AST audit can be bypassed with `from operator import attrgetter; attrgetter("__class__.__base__...")`.
  - `operator` is not forbidden, and the dunder is inside a string.
  - `scipy.io.savemat/loadmat/mmwrite` are not flagged either.
  - This is a declared heuristic.
- **N-7:** in the firewall_check history scan:
  - skipped blobs over 64 MB do not fail `all_clean` (`firewall_check.py:118-122, 155`);
  - compressed encodings are not searched;
  - `rev-list --all` excludes reflog-only objects.
- **N-8:** the spawn child has no import guard and honours `__pycache__`. The child is same-account and not
  key-holding (declared).

---------------------------------------------------------------------------------------------------------------------

## 6. Declared residual risks

| residual | assessment |
|---|---|
| S1 root of trust open (#925); branch protection off | Acceptable as declared (operator decisions). But branch protection being off is also the delivery route for B-1, S-2 and N-5, which are fixable in code now. |
| OS account is the boundary | Acceptable as a statement, but the claim that entry stops the protocol's OWN tools from running unbound code is false for `icacls` (B-1) and for `firewall-check` after an audit exists (S-2). |
| Separate predictor-child account needed; runs fail closed | Understated: failing closed irreversibly consumes the once-only release (S-1). |
| F-3P (numpy/scipy/cryptography, `.pth`) | Acceptable. Also include the install directory itself (e.g. `H:\Python312\fcntl.py` is on the stage-1 path) and N-2. |
| entry.py cannot vouch for itself | Acceptable. |
| Committed KEY_RELEASED/REVEALED blocks | Acceptable. Extend to all fixed-name records (N-5). |
| Plaintext length visible | Acceptable (small aggregate leak). |
| Gates not a boundary against the key holder; AST heuristic; single-draw provenance; the System interface exposes physics | Acceptable as declared. |

**Missing from the list:** B-1 (as a residual it would be unacceptable), S-1's irreversibility, S-2, N-3, N-5.

---------------------------------------------------------------------------------------------------------------------

## 7. Mandatory classes

1. **Unbound code with secrets:**
   - `icacls.exe` (B-1);
   - firewall-check's unaudited binding (S-2);
   - stage-2 pre-filter imports (N-2);
   - the child without a guard (N-8);
   - `.pth` / third-party code (declared).
   - The guard itself correctly refuses `.pyc`, `.pyd`, package-dir shadows and unbound modules.
2. **Same-account readability:** declared. S-3 adds a window where other accounts can read the released key.
3. **Static-audit bypass:** N-6.
4. **Ref ambiguity / history:** tags and heads are handled (F3). Merges are handled (`-m --full-history`). Grafts and
   shallow files are not (S-5). The seal commit is on origin/main and the file history is single-blob (verified).
5. **Unauthenticated records:** S1 is open (declared). RESULT_SEAL is allow-listed. The once-only records can be forged
   to block (declared); other records can be bricked (N-5).
6. **Narrowing public fields:** plaintext length only (declared). The result hash is not brute-forceable (HMAC tags).
   Error replies carry type names only.
7. **Host / identity spoofing:** the host is `socket.gethostname`; the M2 block is coupled to "release only on the
   designated host", and custody runs on M1. The account comes from GetUserNameW in the runner, but custody's ACL
   grant uses `USERNAME` (S-3).

---------------------------------------------------------------------------------------------------------------------

## 8. Verdict
- **OVERALL: FAIL**, on one blocks-PASS finding: B-1.
- S-1 to S-5 should be fixed before a real run. S-1 in particular must be fixed before any run is attempted, or D2 is
  consumed.
- Do NOT commit a PASS record. Nothing was committed (read-only worker).
