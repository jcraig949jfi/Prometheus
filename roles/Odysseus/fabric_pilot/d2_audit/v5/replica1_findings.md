# Holdout D2 firewall re-audit v5: adversarial findings (one replica)

- **Skill:** audit.security.adversarial v1
- **Audited commit:** 57c809387c65a2f691fe5aa28e23ba00188a0c3e (HEAD; "D2 v5: repairs after the v4 re-audit FAIL")
- **Scope:** FIREWALL.md section "v5" plus the six brief claims. Out of scope: the law, the science, S1 (#925) and branch protection.
- **Method:** static reading of the D2 package and its import closure, plus `rogit log/show` over the history. I could NOT
  execute code: the Bash tool was denied in this session, except for `rogit`. I therefore did not run either selftest,
  `entry.py gates SEAL`, or `protocol --code-hashes`. Wherever a statement depends on execution, it is marked
  CANNOT-VERIFY, or it relies on the committed M1 output `SELFTEST_PROTOCOL.json`.

## Summary

| # | claim | verdict |
|---|---|---|
| 1 | Opacity | HOLDS (declared length note) |
| 2 | Secrets never in git | HOLDS (name level); content level CANNOT-VERIFY (key-holder scan) |
| 3 | Enforced order | HOLDS, apart from S1 (open, excluded) and notes N-2, N-3 |
| 4 | Controlled reveal | HOLDS for confidentiality; see BP-1 (irreversible release consumption) |
| 5 | Predictor isolation | HOLDS (fails closed); see SF-2 (the declared remedy needs code, not only a host capability) |
| 6 | Draw integrity | HOLDS (at-draw hashes: files unchanged since 95b31a30d; not recomputed by me) |
| v5 B-1 | no bare-name executables in key-holding tools | HOLDS inside the tools; SF-4 (documented `python` invocation) |
| v5 B-2 | allowlist runs only bound code | HOLDS for code; SF-3 (trust input is unbound working-tree data) |
| v5 S-1 | runner never fails after consuming the release | **BROKEN: BP-1, blocks-PASS** |
| v5 S-2 | pre-audit pinning | HOLDS as stated; SF-1 (no revocation, mix-and-match, entry.py unpinned) |
| v5 S-3 | only `-I -B` | HOLDS |
| v5 S-4 | origin/main only | HOLDS |
| v5 S-3/S-5 key hygiene | HOLDS; N-4 (account alias) |
| v5 S-5 git | HOLDS for entry and protocol; N-1 (firewall_check lacks the hardening), N-2 (commit-graph) |
| v5 S-6 | HOLDS |
| spawn child | HOLDS |

**OVERALL: FAIL**, on BP-1.

---

## BLOCKS-PASS

### BP-1: the runner still refuses AFTER it consumes the one-time key release (the v4 S-1 class is not closed)

**Claim under test.** FIREWALL.md:238 says: "`FirewallRun.preflight()` ... BEFORE the key is read or deleted and
before the run directory exists. A refusal consumes nothing." The v4 verdict made this the condition for PASS: "the
runner completes through entry.py BEFORE the release is consumed" (roles/Odysseus/fabric_pilot/d2_audit/v4/VERDICT.md:64).

**Evidence (order inside `FirewallRun.open`).**
- `runner.py:605-606`: preflight (the isolation probe only).
- `runner.py:607`: the key is read.
- `runner.py:608-609`: the released key file is deleted (`_run_cli` always passes `delete_key=True`, `runner.py:935`).
- `runner.py:638`: the run directory `run_<nonce>` is created.
- `runner.py:641`: `load_package(...)` runs only now, and it can refuse in several ways:
  - `PackageHashMismatch`: the zip bytes differ from the committed hash (`runner.py:454-457`). The gates compared only
    the command-line hash string with the commitment (`protocol.py:511-512`), never the file's bytes.
  - `PackageInvalid`: member names or suffixes, package.json, entry, or the intervention range (`runner.py:460-489`).
  - `PackageAuditRefusal`: the AST heuristic (`runner.py:490-495`). `FORBIDDEN_ATTRS` contains `load` and `loads`
    (`runner.py:109`), so an innocuous `json.loads(...)` or `np.load(...)` in the package is flagged.
- `runner.main` turns any of these into `{"refused": true}` with rc 3 (`runner.py:918-920`). The key copy is already
  gone.
- `entry.py runner --preflight` calls only `run.preflight()` (`runner.py:937-940`). It never hashes, unpacks or audits
  the package, so it cannot predict these refusals.
- Custody does not require a passed preflight before it releases (`custody.py:174-208`).

**Why the refusal is irreversible.**
- A second release is refused by the custody log and by the committed KEY_RELEASED record (`custody.py:183-186`,
  record written at `custody.py:206`, which "counts forever": `protocol.py:402-410`).
- A rerun is also refused because the run directory now exists (`runner.py:929-930`).
- So D2 cannot be evaluated under the protocol again. The only way forward breaks the enforced order (a manual key copy
  by the key holder) or needs a new seal.

**Minimal scenario.**
1. State: gates pass through DESIGNATION, and the host provides a separate child account, so the preflight passes.
   Cosmos commits the sha256 H of `package.zip`. Its entry module contains `import json` and `json.loads("{}")`.
2. Nestor runs `entry.py runner --preflight`: PASS. Then `entry.py custody release-key`: the key is released and
   KEY_RELEASED.json is written and committed.
3. Nestor runs `entry.py runner --package package.zip --package-sha256 H --key <dest>/hidden_D2.key.hex ...`.
   - Preflight passes.
   - The key is read and deleted.
   - `run_<nonce>` is created.
   - `load_package` raises `PackageAuditRefusal: package.py:N attribute .loads`.
4. Result: rc 3, the key copy is deleted, the release is spent, and the protocol for spec_id e2d3213b... is deadlocked.

The same outcome follows if the operator passes a wrong or corrupted zip path (`PackageHashMismatch`). Cosmos, the
declared adversary, can cause it deliberately with a hash-committed package that trips the heuristic.

**A second path to the same outcome.** The preflight probes read, and file creation in the output root
(`runner.py:686`). The receipts read and append probes run only in `_start_worker` (`runner.py:691-695`, extra read
path `runner.py:936`), which comes after the key has been consumed.
- Suppose the output-root ACL lets the account create folders but not files. That is a natural attempt to satisfy the
  preflight.
- A same-account child then passes the preflight and fails `ChildNotIsolated` only after the release is spent.

**Test gap.** `v5_S1_run_refused_before_key_consumed` covers only the ChildNotIsolated preflight refusal
(`selftest_protocol.py:893-898`). No test submits a flagged or mismatching package through entry after a release.

**Fix.**
- Run `load_package` (hash of the bytes, member rules, AST audit, intervention check) into a scratch directory before
  the preflight and before the key is read. Include it in `--preflight`.
- Have custody release-key require evidence that this check passed, or run the package check itself on the committed
  hash.
- Make the preflight mirror every in-run probe: read and append on a scratch run directory created with the same
  ACL/owner as the real one.

**Severity: blocks-PASS.**
- It is the S-1 class that the v4 verdict made a condition of PASS, and v5 claims it is repaired.
- It needs no special privilege and can be triggered by the adversary.

---

## Claim-by-claim

### Claim 1: Opacity. HOLDS

Attacks tried:
- (a) Recover plaintext or confirm guesses from public fields.
- (b) Get hidden-derived data out through receipts, errors or selftest JSON.
- (c) Brute-force the result-seal hashes.

Evidence:
- AES-256-GCM with a 32-byte CSPRNG key and a 12-byte CSPRNG IV (`sealbox.py:48-57, 70-80`). There is exactly one
  encryption under the key (`draw.py:103-107`).
- The AAD is the family hash (`sealbox.py:60-61`).
- The commitment is `sha256(salt||pt)` with a 32-byte secret salt (`sealbox.py:64-67`, `draw.py:104`).
- Manifest fields are constants, versions, hashes, the IV and `draw_utc` (`MANIFEST_D2.json:1-36`). There is no nonce,
  knob, seed or summary.
- `SELFTEST_D2.json:1-33` and `SELFTEST_PROTOCOL.json:1-176` hold booleans, exception type names and public file
  names only.
- Receipts identify worlds by index and by `world_tag = HMAC(key, world||seed)` (`runner.py:617-618`). certify bodies
  drop `r['system']` (`runner.py:524-529`). Error replies to the child are type names only (`runner.py:760-761`).
- RESULT_SEAL publishes `chain_head`, `result_sha256` and `n_receipts` (`custody.py:241-244`).
  - Both hashes cover world_tags, which are keyed HMACs, so they cannot be brute-forced.
  - `n_receipts` is the constant 2N+3.
- Note (declared): `ciphertext_bytes: 17227` reveals the plaintext length (`MANIFEST_D2.json:5`).
- Note (declared N-1): run duration and commit times leak after predictions are frozen.

### Claim 2: Secrets never in git. HOLDS at name level; content level CANNOT-VERIFY

- `rogit log --all --stat -- prometheus/cosmos/c3_holdout_D2` shows eight commits. None adds `*.key*`, `*.salt*`,
  `*.plain.json` or any secrets path.
- `rogit log --all --name-only -- *.key* *.salt* *.plain.json *nestor_secrets* *hidden_D2.* *.pem` returns only
  `95b31a30d hidden_D2.enc`.
- Searching commit contents for the actual key or salt bytes needs the secrets. That is `entry.py firewall-check` on
  M1, which I cannot run. The "latest pass all clean" is a custodian statement (CANNOT-VERIFY). To settle it, publish
  the booleans of `entry.py firewall-check` at 57c809387.
- Scan-quality notes (N-6):
  - `history_scan` walks `rev-list --all` (`firewall_check.py:111`). That excludes reflog-only objects such as older
    `stash@{n}` entries (this repository shares a stash stack across worktrees).
  - World detection is exact-canonical JSON only (`firewall_check.py:46, 149`).
  - Both are heuristics.

### Claim 3: Enforced order. HOLDS (S1 excluded)

Attacks tried:
- (a) Replace a record through a merge.
- (b) An evil merge that adds a record with no parent carrying it.
- (c) A tag or branch shadowing origin/main.
- (d) Replace refs or GIT_* environment variables.
- (e) grafts or shallow.
- (f) An unauthenticated later audit.
- (g) Code changed after the audit, in the committed tree or the working tree.
- (h) A commitment in a side branch forked before the audit.

Evidence:
- The full-history rule is at `protocol.py:266-310`. With `-m`:
  - a merge that brings in a second blob is refused, because the blobs set is larger than 1 (`:299-301`);
  - an evil-merge add has no non-merge `A`, so `len(adds) != 1` (`:302-306`).
- Ancestry order is checked for audit, commitment, designation and result seal (`protocol.py:470-474, 508, 528, 555`).
- Fully qualified ref plus shadow refusal: `protocol.py:253-263` and `entry.py:216-221`.
- `GIT_*` is stripped and `GIT_NO_REPLACE_OBJECTS=1` is set (`protocol.py:179-185`).
- grafts and shallow are refused (`protocol.py:203-213`).
- The audit binding must equal `AUDITED_FILES` exactly, in both the committed tree and the working tree
  (`protocol.py:484-492`). The loaded closure is checked at `:493-497`.
- Real history: the sealed blobs are added by exactly one non-merge commit (95b31a30d). Four merges (db0bcad5,
  e5b95744, 85b198a5, ebe1307e) carry the same blobs (10c7b600…, db3d442d…), as shown by
  `rogit log --all --full-history -m --raw`. So SEAL passes under `_added_once`. I did not execute it; the committed
  M1 run records `v3_real_history_seal_passes: true`.
- The runner and custody gates run before the key is touched (`runner.py:584-587` before `:607`; `custody.py:182`
  before `:190`).
- Notes:
  - N-2: a forged commit-graph file (`objects/info/commit-graph`) re-parents history exactly as grafts do.
    `git_state_ok` does not check for it, and `-c core.commitGraph=false` is not set. It needs same-account write
    access, so it falls under the declared account residual. It is a gap in the S-5 statement.
  - N-3: `entry.verify` picks the highest allow-listed PASS audit without the `_added_once`/order/format checks
    (`entry.py:254-271`). For runner, custody, evidence and gates, `check_gates` re-checks. firewall-check and
    allowlist do not call `check_gates`. Exploiting that still needs an allow-listed PASS audit (S1).

### Claim 4: Controlled reveal. HOLDS for confidentiality; BP-1 for liveness

- Release:
  - Gates through DESIGNATION with the runner id and host (`custody.py:182`).
  - Once only, by log and by git (`:183-186`).
  - Destination: local fixed drive, not UNC, not OneDrive, outside git and the secrets directory, and must not
    already exist (`:111-133`, `:179-180`).
  - Directory ACL is cut to the custodian plus ONE user account BEFORE the key is written, with icacls called by its
    system path (`:148-166`, `:52-62`).
  - Cleanup on failure (`:194-202`).
- M2 is refused as the designated host and as the running host (`protocol.py:524-535`, `custody.py:132-133`). The
  hostname is not a boundary: the key simply never leaves M1.
- Reveal: gates through RESULT_SEAL (allow-listed, `protocol.py:550`), the chain head and result hash are re-verified,
  and it runs once (`custody.py:257-272`).
- Evidence bundle requires RESULT_SEAL (`evidence.py:55-61`).
- Note N-4:
  - The "not the custodian" check compares names only (`protocol.py:526`). `SKULLPORT\jcrai` passes it and
    `is_single_user_account`.
  - The runner then refuses on the account mismatch (`protocol.py:538`), but only after custody has spent the release.
  - This is a custodian-error path to the BP-1 outcome. Fix: compare SIDs.
- Note N-5: `ALLOWLIST.json`, `custody.jsonl` and `custody.lock` live in the same directory as the runner's default
  output root (`protocol.py:57`, `custody.py:42`, `runner.py:83`).
  - The designated (non-custodian) runner account must create `run_<nonce>` there.
  - With an ordinary inherited Modify grant, the runner account can therefore rewrite the allow-list, which is the S1
    root.
  - Separate the output root from the trust files, or specify the ACL.

### Claim 5: Predictor isolation. HOLDS (fails closed); SF-2

- Spawn context: no memory is inherited (`runner.py:661-664`).
- The pipe carries JSON plus `.npy` with `allow_pickle=False` (`runner.py:166-200`).
- Hostile reply shapes are handled (`runner.py:753-755`), and errors carry type names only (`:760-761`).
- The key is deleted before any child exists (`:607-609`).
- The probe covers the key, secrets and receipts (`:674-677`).
- The AST audit is trivially bypassable, as declared. For example, `pandas.read_csv(<secret path>)` and
  `scipy.io.mmread(...)` are not flagged (`runner.py:92-112`). The boundary is the account.
- **SF-2 (should-fix, declared residual mis-stated):**
  - The child is always started by `mp.get_context("spawn").Process` under the runner's own token
    (`runner.py:661-664`). No code path launches it as another account: no `set_executable`, no
    CreateProcessAsUser/WithLogon.
  - So the "separate predictor-child account" is not just a host capability (FIREWALL.md:249-251). It also needs a
    runner code change, which invalidates any audit bound now.
  - As audited, a real run through entry.py can never complete on any host. It is always refused ChildNotIsolated,
    safely before consumption.
  - The residual should say this plainly.

### Claim 6: Draw integrity. HOLDS

- CSPRNG nonce (`draw.py:154`). The seed is `int(nonce,16) mod 2^128` (`draw.py:63`), i.e. 128-bit.
- Exposed-D rejection (`draw.py:67-69`).
- Redraw: `verify_reveal.py:54-63`, with `redraw_code_matches_manifest` (`:57-60`).
- `draw.py`, `sealbox.py`, `__init__.py` and `medium.py` are untouched since 95b31a30d / a56ef7787
  (`rogit log --all` on those paths). The v1 audit verified the LF hashes against `MANIFEST_D2.json:11-15` by
  execution (roles/Odysseus/fabric_pilot/d2_audit/VERDICT.md:40). I did not recompute them.
- Note: numpy `Generator` streams are not guaranteed across versions. The redraw should use numpy 2.2.6
  (`MANIFEST_D2.json:27`).

---

## v5 repairs

### B-1: no bare-name executables. HOLDS in the tools

- Every `subprocess` or process start in a key-holding module was checked:
  - entry: git by absolute path (`entry.py:77-110`);
  - protocol: the same (`protocol.py:158-200`);
  - custody: icacls from `GetSystemDirectoryW` (`custody.py:52-62, 161`);
  - firewall_check: git via `protocol.git_exe` (`firewall_check.py:61-63`);
  - runner: multiprocessing spawn uses `sys.executable`;
  - ctypes: `windll.advapi32` and `kernel32` are KnownDLLs.
- `NoDefaultCurrentDirectoryInExePath=1` is set for the process and its children (`entry.py:43`).
- **SF-4 (should-fix, procedure):** the only documented invocation is `python -I -B <repo>/.../entry.py`
  (FIREWALL.md:228; entry.py:3-5), with `python` resolved by the custodian's shell.
  - cmd.exe searches the current directory first. A `python.exe`/`python.cmd` committed at the repository root runs as
    the custodian before entry exists.
  - Document an absolute interpreter path (e.g. `H:\Python312\python.exe -I -B ...`).
  - Which shell M1 seats use: CANNOT-VERIFY from the repository.
- Note N-7:
  - `selftest_protocol` is run on M1 as the custodian with `python -m`: working-tree code, unbound.
  - It calls `icacls` by bare name (`selftest_protocol.py:746`) with the cwd at the repository root.
  - It holds no real key, but it runs as the account that can read the secrets. That is an instance of the declared
    account residual, which the brief's own procedure exercises.

### B-2: allowlist. HOLDS for code; SF-3

- entry-only (`allowlist.py:109-111`), git through protocol (`:42-46`), and no comms/evidence_wiki import
  (`:61-75`).
- **SF-3 (should-fix, S1-adjacent):**
  - The DB host, database and user come from WORKING-TREE files `evidence_wiki/config.json` and `config.local.json`
    (`allowlist.py:49-58`). Neither is bound nor read from origin/main.
  - Anyone who can push to main (unprotected) can point the lookup at their own Postgres. That server returns
    `sender='Odysseus'` with any sha256, and `add` then allow-lists a forged AUDIT (`allowlist.py:84-99`).
  - This widens the S1 gap from "anyone who can post to comms" to "anyone who can push to main".
  - Read the settings from a custodian-owned file outside the repository.

### S-1: spawn child, preflight, PredictorChildFailed

- Spawn child: HOLDS.
  - The child runs `python -I -B` (flags inherited via `_args_from_interpreter_flags`).
  - The parent's `sys.path` is interpreter-only (`entry.py:336`).
  - `__mp_main__` re-executes entry, filters the path and installs the guard from `C3D2_BOUND` before the Process
    object is unpickled (`entry.py:34-43, 175-180`).
  - `prometheus.*` is served only from bound source, compiled from the hashed bytes (`entry.py:144-172`).
  - Without the binding, the repository is not on the path, so nothing loads.
  - A planted `.pyd`, `.pyc` or package directory shadowing a bound module yields a non-`.py` origin or an unbound
    rel, so it is refused (fails closed).
- "A refusal consumes nothing": **BROKEN (BP-1)**.

### S-2: pre-audit pinning. HOLDS as stated; SF-1

- `pin-tools` executes only entry.py itself (`entry.py:284-309`).
- A digest mismatch is refused (`:291-292`).
- Pre-audit targets are bound to committed bytes that equal the working tree (`:239-247, 275`).
- **SF-1 (should-fix):**
  - (a) Pins are only ever appended and are matched per file across all entries (`entry.py:276-277, 299-300`). A
    reviewed-then-superseded version stays runnable forever, and files from different pinned commits can be mixed into
    a combination nobody reviewed. There is no revocation, and the stored `commit` is never checked.
  - (b) `entry.py` is not in `PRE_AUDIT_FILES` (`entry.py:69-70`). Before an audit, the key-holding `firewall-check`
    therefore runs under an entry.py nothing pins. The declared mitigation ("compare its printed sha256 with the
    governing audit") has nothing to compare against.
  - Fix: pin the digest as a set together with entry.py, and require the custodian to hash entry.py independently.

### S-3, S-4, S-5, S-6

- S-3: `-I -B` is enforced (`entry.py:34-35`). HOLDS.
- S-4: other refs are refused (`runner.py:911-913`, `custody.py:307-309`, `evidence.py:98-100`). HOLDS.
- S-5 git: `GIT_HARDEN` is used by entry and protocol (`entry.py:105-109`, `protocol.py:189-200`); grafts and shallow
  are refused.
  - N-1: firewall_check's `grep`, `rev-list` and `cat-file` calls omit `GIT_HARDEN` (`firewall_check.py:61-63, 100,
    111-125`). So "every git call" is not literally true. None of those subcommands runs hooks or auto-gc, so there is
    no exploit.
  - N-2: commit-graph, see claim 3.
- S-6: a git error raises (`protocol.py:407-409`). HOLDS.
- Key hygiene (S-3/S-5): single user SID type, fresh destination, ACL before the write, cleanup (`custody.py:148-202`).
  HOLDS, apart from N-4.

---

## Mandatory classes

1. **Unbound code with secrets:**
   - The package `__init__` files are bound (`protocol.py:74-82`).
   - `.pyc` is never read (`entry.py:161-172`).
   - Shadowing packages and extension modules fail closed.
   - site-packages and `.pth` files are declared F-3P.
   - Remaining: entry.py is self-vouching (declared; SF-1(b)) and the selftests run unbound (N-7).
2. **Same-account readability:** declared. The child is always refused (SF-2). Trust files are shared with the runner
   output root (N-5).
3. **Static-audit bypasses:** the AST audit is bypassable (pandas/scipy readers), as declared.
4. **Git ambiguity and simplification:** HOLDS. `--full-history -m` is used, and the fully qualified ref wins over
   dwim. commit-graph: N-2.
5. **Unauthenticated records:**
   - S1 is open, and SF-3 widens it.
   - KEY_RELEASED and REVEALED are unauthenticated (declared, fail closed).
   - Receipts use unkeyed chaining, anchored only by RESULT_SEAL (a key-holder residual).
6. **Narrowing public fields:** length (declared), timing (declared N-1), error text as type names only.
7. **Spoofable identity:**
   - The hostname is not a boundary.
   - The comms sender is S1.
   - Account alias: N-4.

## Declared residual risks: assessment

- **Gates are not a boundary against the key holder:** acceptable as declared.
- **Prediction package is Python as the operator account; the AST audit is a heuristic:** acceptable only because the
  isolation probe fails closed. As SF-2 shows, the separate-account remedy needs code as well as a host capability.
- **Single-draw provenance is a custodian statement:** acceptable as declared.
- **The System interface exposes physics by design:** acceptable.
- **v5 additions** (account boundary, F-3P, git config, timing N-1, DoS N-2, entry self-vouch, length): acceptable.
- **Missing from the list:**
  - BP-1 (irreversible release consumption; not a residual, a defect);
  - SF-2 (a code change is required for the child account);
  - SF-3 (unbound allow-list DB config);
  - SF-4 (bare `python` in the documented invocation);
  - N-5 (trust files in the runner-writable output root);
  - N-2 (commit-graph);
  - N-7 (the selftest procedure runs unbound code as the custodian).

## Not done / CANNOT-VERIFY

- I could not execute anything, so I did not run:
  - `selftest_protocol` or `selftest_D2`;
  - `entry.py gates SEAL` against the real history (claim 3 is reasoned from `rogit log`);
  - `protocol --code-hashes`;
  - the recomputation of the at-draw hashes.
- The M1 key-holder scan booleans were not available to me.
- Which shell the M1 seats use (for SF-4) cannot be established from the repository.
