# Holdout D2 firewall re-audit v4: adversarial findings

- **Skill:** audit.security.adversarial v1. Task tsk-c69dc6012c70, attempt att-6aab9dd91671.
- **Audited commit:** e6e482ae60400cc90a4c5c3a3bc543721acafac4. The D2 package was last changed in b6f28bd43 ("D2 v4").
- **Scope:** the coordinate/firewall layer only, meaning FIREWALL.md section "v4" plus the six original claims. Law and science are out of scope.
- **Method:** static reading, `rogit` history, and `sha256sum` on the sealed files.
  - No repository code was executed. The skill forbids it. So no self-test was run and no `entry.py gates SEAL` was run by me.
  - Behavioural statements about CPython and Windows below come from documented interpreter/OS behaviour. Where it matters, they are corroborated by the custodian's own committed self-test output (`SELFTEST_PROTOCOL.json`, produced on Windows: `not_applicable_on_this_os: []`).

## 0. Public commitments (re-checked)

| item | result | evidence |
|---|---|---|
| sha256(hidden_D2.enc) | f75ba333…fc9f, matches | sha256sum; MANIFEST_D2.json:7 |
| sha256(MANIFEST_D2.json) | 78874e9d…71fe, matches | sha256sum |
| spec_id / commitment in manifest | as briefed | MANIFEST_D2.json:8,34 |
| draw.py / sealbox.py / __init__.py vs `d2_src_sha256_at_draw` | 800e0b5d…, dec9b915…, d38d3b0c…: all match | sha256sum; MANIFEST_D2.json:11-15 |
| medium.py vs family_src_sha256 | 09559e69…cde4, matches | sha256sum; MANIFEST_D2.json:21 |
| sealed files: one blob each, one non-merge add, at 95b31a30d | yes (4 later merges carry the same blob, status A vs 2nd parent) | `rogit log --all --full-history -m --raw -- …hidden_D2.enc …MANIFEST_D2.json` |
| `c3_holdout_D/` byte-identical to a56ef7787 | yes (empty diff) | `rogit diff --stat a56ef7787 e6e482ae6 -- prometheus/cosmos/c3_holdout_D` |
| pinned seal / spec_id in code | match | protocol.py:55-56 |
| shadowing refs (`refs/tags/main`, `refs/tags/origin/*`, `refs/heads/origin/*`) or `refs/replace/*` in this clone | none | `rogit for-each-ref` |

## 1. Verdict summary

| claim | verdict |
|---|---|
| 1 Opacity | HOLDS (declared length leak; timing note N-1) |
| 2 Secrets never in git | HOLDS repo-side; key-holder scan CANNOT-VERIFY-FROM-REPO (Nestor's booleans) |
| 3 Enforced order | HOLDS for the gate logic; should-fix S-4 (`--ref` lets gates read a non-origin ref) |
| 4 Controlled reveal / key release | **BROKEN**: B-1 (the key-release path executes a cwd `icacls.exe`) |
| 5 Predictor isolation | HOLDS narrowly (no pickle, type-name errors). Production path broken: S-1 |
| 6 Draw integrity | HOLDS (minor notes N-4) |
| v4 P1 (stage-1 import) | HOLDS for the planted-package-module case; the stronger wording is BROKEN under PYTHONPATH/usercustomize (S-3, should-fix) |
| v4 P2 (repo root off sys.path, guard) | HOLDS inside entry-launched Python. Code the same protocol runs outside that guard is B-1, B-2, S-1, S-2 |
| v4 P3 (once-only records / end-to-end) | HOLDS for `gates`. The end-to-end RUN through entry.py cannot complete (S-1) |
| F-CWD repair | **BROKEN**: B-1 (icacls), B-2 (allowlist.py `git`) |
| F-KH repair | partially: B-2 (allowlist), S-2 (firewall-check never audit-bound) |
| F-GOV, F-FETCH, F-ONCE, F-AST, F-NET, claim-6 redraw | HOLD as described (notes below) |
| F-GITENV | HOLDS for GIT_* and replace refs; config/graft/shallow steering remains (N-3, same-account) |
| F-DEST | HOLDS for UNC/fixed/OneDrive; the ACL step is B-1 plus S-5 |

**Blocks-PASS findings:** B-1 and B-2. S1 (record authentication) remains OPEN as declared.

**OVERALL: FAIL**

---

## 2. Blocking findings

### B-1: custody's key-release step runs `icacls` by bare name, so a planted `icacls.exe` in the cwd executes inside the verified key-holding process (blocks-PASS)

**Evidence**
- custody.py:139-144: `subprocess.run(["icacls", str(path), "/inheritance:r", ...])`. This is a bare program name, with no absolute path and no `NoDefaultCurrentDirectoryInExePath` in the *calling* process's environment.
- The env hardening applies only to the environment passed to git children: protocol.py:179-185 and entry.py:116-122. The search that matters is done by the parent's CreateProcess, which consults the parent's own environment. Nothing sets it in `os.environ` (grep over the audited files).
- CreateProcess search order for a bare name: the application directory, then the **current directory**, then System32. `icacls.exe` lives in System32, so the cwd copy wins.
- The custodian's own test proves that Python on M1 executes a cwd executable given by bare name:
  - selftest_protocol.py:676-680 (`v4_CWD_control_cwd_git_exe_is_found`);
  - SELFTEST_PROTOCOL.json:77 = true, run on Windows (`not_applicable_on_this_os: []`, :153).
- The v4 F-CWD repair covers only git in "entry, protocol, firewall_check" (FIREWALL.md:197).
- FIREWALL.md:211 claims "entry.py stops the protocol's OWN tools from executing unbound code". custody is such a tool, started through entry.py, and it executes an unbound executable.
- entry.py verifies only AUDITED_FILES, the names in protocol/ and the package `*.py` files (entry.py:212-257). Arbitrary files at the repository root are not checked. The P2 test itself models the custodian's cwd as the repository root (selftest_protocol.py:641-645).

**Scenario**
1. Branch protection is off, and Cosmos has push rights to main (it must commit PREDICTION_COMMITMENT.json there).
2. Anyone who can push commits `icacls.exe` at the repository root. The custodian's checkout pulls main.
3. On M1, from cwd = repository root, Nestor runs `python -I -B …/entry.py custody release-key --runner-id R --dest D:\rel`.
4. All gates pass. custody.py:165-167 reads the key and writes `D:\rel\hidden_D2.key.hex`. Then custody.py:141 runs `.\icacls.exe` as the custodian account.
5. That program receives the key path in argv and can read `nestor_secrets` (key, salt, plaintext). It exits 0, so the release completes normally and nothing is logged as abnormal.

**Fix**
- Call `%SystemRoot%\System32\icacls.exe` by absolute path, or set the ACL via Win32 API (`SetNamedSecurityInfoW`) through ctypes.
- In entry.py stage 2, set `os.environ["NoDefaultCurrentDirectoryInExePath"]="1"` before importing any target, so every bare-name spawn in a verified process is covered.
- Add a positive-control test for icacls like the git one.

### B-2: allowlist.py, a mandatory protocol step that runs as the custodian account, executes unbound repository code and a bare `git` (blocks-PASS)

**Evidence**
- allowlist.py is in AUDITED_FILES (protocol.py:79). It is the only way any record becomes governing (entry.py:235-244; protocol.py:354-364).
- It is not started through entry.py (usage at allowlist.py:3-5).
- allowlist.py:40 runs `subprocess.run(["git", ...])`. This is:
  - a bare name, so the cwd `git.exe` is searched first (the same F-CWD class, CONFIRMED on M1 per FIREWALL.md:197);
  - run with no GIT_* stripping and no GIT_NO_REPLACE_OBJECTS;
  - given `--ref` as any string (allowlist.py:89), including short names that tags can shadow.
- allowlist.py:46-49 appends the repository root to sys.path and imports `comms.api`.
  - `comms.api.connect()` then runs `sys.path.insert(0, str(REPO))` (comms/api.py:78-79), putting the repository root **first**, and imports `evidence_wiki.ew.db` (comms/api.py:80).
  - This defeats the v4 claim "allowlist.py … appends the repository root LAST" (FIREWALL.md:198).
  - It executes `comms/__init__.py`, `comms/api.py`, `comms/identity.py` and `evidence_wiki/ew/db.py` from the working tree, none of them bound by any audit, with `.pyc` honoured (no -B).
- v3 declared this acceptable because "allowlist.py never runs in a key-holding process" (FIREWALL.md:172). v4 redefines the boundary as the OS account (FIREWALL.md:209-212), and allowlist.py runs as that account, which can read `nestor_secrets`.

**Scenario**
1. Cosmos pushes a change to `comms/api.py` (or `evidence_wiki/ew/db.py`, or a repository-root `git.exe`) to unprotected main.
2. Cosmos posts its commitment. Nestor must now run `allowlist.py add --role COMMITMENT …` to make it govern. Cosmos therefore knows *when* its code will run.
3. That code runs as jcrai and reads `C:/Users/jcrai/nestor_secrets/holdout_D2/*`. This is a Cosmos-to-key path through the protocol's own procedure, needing no S1 forgery.

**Fix**
- Run allowlist through entry.py as a pre-audit target bound like firewall-check (better: bound to a custodian-pinned hash).
- Use protocol.git_exe/git_env.
- Do not import comms from the working tree in the custodian account. Pass the message text and id in and verify them out of band, or run the comms lookup in a separate account or process and hand over only the (sender, body) strings.

---

## 3. Should-fix findings

### S-1: the production RUN through entry.py cannot complete, and it fails *after* the once-only key release and the key read (should-fix; MUST-FIX before a real release)

**Why the child cannot start**
- entry.py:285 cuts sys.path to interpreter paths, so the repository root is not on it (the P2 repair).
- runner.py:635-638 starts the predictor with `mp.get_context("spawn")`. The spawn child receives the parent's `sys.path` in its preparation data and runs with the parent's `-I -B`.
- The child then unpickles the target `prometheus.cosmos.c3_holdout_D2.runner._worker_main`. `prometheus` cannot be found: there is no guard in the child, the repo is not on the path, and there is no pyproject/setup, so no installed package.
- The child exits. `_recv` at runner.py:643 raises EOFError, which is uncaught.

**Why that is too late**
- The key has already been read and deleted (runner.py:581-583). The run dir already exists (one run per designation; runner.py:869-870).
- The once-only KEY_RELEASED record blocks any second release (custody.py:161-164; protocol.py:347-351).
- So the first real attempt permanently deadlocks this spec_id. The declared ChildNotIsolated fail-closed (FIREWALL.md:213-215) has the same timing, and providing a separate child account would not fix the import failure.

**Why tests missed it**
- The only entry.py end-to-end test is `gates` (selftest_protocol.py:616-625).
- The run end-to-end tests call FirewallRun in-process with the repo on the path (selftest_protocol.py:341-419; selftest_D2 is run with `-m`).

**Related (CANNOT-VERIFY-FROM-REPO, depends on host ACLs):**
- The designated runner account (≠ jcrai) must read `C:/Users/jcrai/nestor_receipts/holdout_D2/ALLOWLIST.json` (entry.py:75,235) and write DEFAULT_OUT_ROOT in jcrai's profile (runner.py:83).
- It must also pass git's safe.directory ownership check on jcrai's repo for the fetch (entry.py:201-204).
- It must delete a key file on which custody granted it only `(R)` (custody.py:141 vs runner.py:582-583).

**Fix**
- Run the isolation probe and all host-capability checks *before* custody releases the key, and before the runner reads it.
- Make the child import through a verified path. For example, pass the repo path and bound hashes and install the guard in the child, or spawn `python -I -B entry.py predictor-child`.
- Add an entry.py end-to-end RUN test.

### S-2: `entry.py firewall-check` is never bound to the audit, even after a PASS audit governs (should-fix; missing from the residual list)

- entry.py:87-88 and :284 always use the PRE_AUDIT binding for firewall-check. That binding is whatever is committed at origin/main (entry.py:225-233).
- firewall-check loads plaintext, salt and key (firewall_check.py:43-58). Anyone who can push to main (Cosmos) decides the code that runs with all three secrets. The custodian merely has to sync the working tree, which entry *requires* (entry.py:230-231).
- entry.py:33-35 states this ("not against committed code"), but FIREWALL.md's residual list (:207-220) does not.
- **Fix:** once an allow-listed audit exists, bind firewall-check to it (it is in AUDITED_FILES). Before that, require a custodian-pinned hash.

### S-3: stage 1 does not "import nothing from a path" when started as plain `python entry.py` (should-fix)

- The interpreter's own startup runs before entry.py:42. Without `-I`, `site` executes `sitecustomize`/`usercustomize` found on sys.path, including PYTHONPATH entries and user site-packages.
- A `sitecustomize.py` in any PYTHONPATH directory (for example the repo root, a common developer setting) runs as the custodian before stage 1 can drop anything. It can then rewrite the re-exec (monkeypatch `subprocess`, change argv or `sys.executable`).
- PYTHONPATH entries under `base_prefix` also survive the stage-1 filter (entry.py:54-58).
- The documented `python -I -B …` invocation is immune.
- **Fix:** refuse (do not re-exec) unless started with `-I -B`, and drop the claim "Plain `python entry.py` also works" (FIREWALL.md:187; entry.py:7). The positive control only covers a package-directory `json.py` (selftest_protocol.py:631-640).

### S-4: the key-holding targets accept any `refs/...` as the record source (should-fix)

- custody `--ref` (custody.py:273), evidence `--ref` (evidence.py:93) and runner `--gate-ref` (runner.py:852) are passed to check_gates. That function only requires a `refs/` prefix (protocol.py:200-201).
- entry.py verifies the audit binding against refs/remotes/origin/main, but the gates can then read records (and the once-only check, custody.py:163) from, e.g., a local unpushed `refs/heads/x`. The "public order record" is then not public.
- Only a key-holder action. Still, it silently voids claim 3's "records are read from origin/main".
- **Fix:** when `C3D2_ENTRY=verified`, refuse any ref other than DEFAULT_REF.

### S-5: key-file ACL step hygiene (should-fix)

- If `_restrict` fails (custody.py:143-144), the key file written at custody.py:167 is **not deleted**. The except branch (custody.py:170-173) only drops the lock, and no KEY_RELEASED record is written. Repeated attempts to new `--dest` values leave unrecorded key copies with inherited ACLs.
- The grant uses `os.environ["USERNAME"]` (custody.py:140), contrary to the v3 "account from the OS" repair (runner.py:261-271). A spoofed USERNAME grants F to another principal.
- Between the write (custody.py:167) and the icacls call, the file carries the inherited ACL. Create it with a restrictive security descriptor instead.

### S-6: `once_record_present` fails open on a git error (should-fix, minor)

- protocol.py:216 returns `[]` when `git log` fails, and `_show` returns None on failure (protocol.py:192-195).
- `once_record_present` (protocol.py:347-351) then reports False, so a second release or reveal is gated only by the editable custody log.
- **Fix:** raise on a non-zero return code.

---

## 4. Notes

- **N-1 (timing channel, claim 1).** The predictor controls its run time (up to 1800 s per world, runner.py:698-703). KEY_RELEASED/RESULT_SEAL carry `utc`, and commit times are public (custody.py:186,215). A few bits about the hidden set can reach Cosmos after its predictions are frozen. Harmless for this one-shot set, but it should be declared. Error type names (runner.py:714) and 300-char predictor error strings (runner.py:329, receipts only) are also side channels. They stay on M1 until reveal.
- **N-2 (DoS by any main pusher).** A stray file in protocol/ or an extra `*.py` in the package directory makes entry refuse everything (entry.py:217-224). Only KEY_RELEASED/REVEALED are declared (FIREWALL.md:219).
- **N-3 (git steering beyond GIT_*).** `.git/config` (`remote.origin.fetch` refspec, `url.*.insteadOf`, `core.hooksPath` + `pre-auto-gc` after fetch), `.git/info/grafts` and `.git/shallow` can still present a different history. `GIT_NO_REPLACE_OBJECTS` does not disable grafts. These are same-account, so they fall inside the declared account residual. Worth listing.
- **N-4 (draw).**
  - The nonce is 256-bit, but the rng seed is `nonce mod 2^128` (draw.py:63), so there are 128 bits of effective entropy. That is sufficient.
  - The redraw does not check `sealed_spec_D.json` against `predecessor_sealed_spec_sha256` (verify_reveal.py:57-63; draw.py:57-59). It can only fail, not falsely pass.
  - The redraw depends on numpy's `integers` stream being stable across versions (the manifest records numpy 2.2.6).
- **N-5 (release destination).** `_dest_ok` does not detect a local folder that is exported as an SMB share (custody.py:98-120). CANNOT-VERIFY-FROM-REPO whether any share exists on M1.
- **N-6 (env-var entry marker).** `C3D2_ENTRY=verified` is just an environment string (runner.py:860; custody.py:275). `python -m` with that variable set bypasses entry. Then `loaded_closure` hashes the `.py` source, not the executed `.pyc` (protocol.py:308-321). This is custodian discipline, and the declared "entry.py cannot vouch for itself" residual covers it.

---

## 5. Claim-by-claim

### Claim 1: Opacity. HOLDS

**Attacks tried**
1. Search public fields for world, knob, seed or nonce content:
   - MANIFEST_D2.json:1-36 holds IV, hashes, versions, draw_utc, `ciphertext_bytes`;
   - SELFTEST_D2.json holds booleans only;
   - SELFTEST_PROTOCOL.json holds booleans and exception names from throwaway repos;
   - RESULT_SEAL holds hashes, nonce and count (custody.py:212-215);
   - KEY_RELEASED/REVEALED hold commit ids (custody.py:177,260-261).
   Nothing secret is present.
2. Brute-force the commitment: salted with 32 CSPRNG bytes (sealbox.py:52-53,64-67). Infeasible.
3. The cipher is AESGCM with a random 256-bit key, a random 96-bit IV, and AAD = prefix plus family hash (sealbox.py:48-80).
4. Receipts carry `world_tag` = HMAC(key, …) (runner.py:591-592). Knobs are absent (selftest_D2 negative control `knob_leak_in_receipts`).
5. The length leak (`ciphertext_bytes`) is declared.

**Residual:** timing (N-1).

### Claim 2: Secrets never in git. HOLDS repo-side; key-holder part CANNOT-VERIFY

**Attacks tried**
1. `rogit log --all --name-status -- "*hidden_D2*" "*.key.hex" "*.salt.hex" "*plain.json" "*nestor_secrets*"` finds only `hidden_D2.enc` at 95b31a30d.
2. `rogit log --all -- prometheus/cosmos/c3_holdout_D2` shows no key/salt/plain file in any of the 7 commits.
3. The history scan design is reviewed:
   - it streams every blob reachable from `--all` (firewall_check.py:105-155), including hex, raw, base64 and base64url forms and seed clusters;
   - blind spots are unreachable objects, other clones, reformatted world JSON, and GitHub-side data.

**What would settle the rest:** Nestor's `entry.py firewall-check` booleans. Note S-2: that tool's code is whatever main says.

### Claim 3: Enforced order. HOLDS (gate logic); S-4 should-fix

**Attacks tried**
1. Replace a record through a merge. `--full-history -m` gives one blob, one non-merge add and no D/R (protocol.py:211-255). The F4 control still works (selftest_protocol.py:468-479).
2. Evil merge introducing a record: no non-merge add, so it is refused (protocol.py:247-251).
3. Tag or branch shadowing origin/main: refused (protocol.py:198-208; entry.py:205-207). A 40-hex SHA is unambiguous.
4. TOCTOU between ref reads: the ref is resolved once (protocol.py:378-379; entry.py:211).
5. Unauthenticated later FAIL/PASS: filtered by the allow-list first (protocol.py:403-408; entry.py:238-244).
6. Code changed after the audit, committed or in the working tree: AuditStale (protocol.py:423-432). A loaded unbound module: UnboundCodeLoaded (protocol.py:433-437).
7. The key is touched only after the gates (runner.py:560-581; custody.py:158-165).
8. Non-origin ref as record source: **works** (S-4).
9. Rewriting origin/main by force-push is possible (branch protection off, declared). It can erase KEY_RELEASED from history; the custody log and lock still stop a second release (custody.py:161).

### Claim 4: Controlled reveal. BROKEN (B-1)

**Attacks tried**
1. Release before the audit, twice, into git, or to the wrong runner: all refused (tests in selftest_protocol.py:359-369).
2. Reveal before RESULT_SEAL, with the seal not allow-listed, a truncated chain, or a tampered RESULT.json: all refused (custody.py:228-243).
3. Release to M2: host must equal the designation *and* this host (protocol.py:464-475), so it is impossible without running on M2.
4. UNC or OneDrive destination: refused (custody.py:98-120).
5. **Planted `icacls.exe` in cwd: executed in the key-holding process** (B-1).
6. ACL-step failure leaves an unrecorded key copy (S-5).

### Claim 5: Predictor isolation. HOLDS narrowly; S-1

**Attacks tried**
1. Pickle injection: parent decoding is JSON plus `np.load(allow_pickle=False)` (runner.py:181-196). No pickle flows from child to parent.
2. Hostile shapes (deep JSON, huge npy): caught as PREDICTOR_CRASH (runner.py:706-708). `_serve` exceptions return the type name only (runner.py:713-714).
3. The child reads secrets: the probe runs before package import (runner.py:307-319, 642-648), but *after* the child has imported the runner (spawn unpickle).
4. Spawned-child import path: cannot import prometheus under entry (S-1).
5. The AST audit is a heuristic (declared). The network block is a heuristic (declared).

### Claim 6: Draw integrity. HOLDS

**Attacks tried**
1. At-draw code hashes: all three match (section 0).
2. Redraw self-check: `redraw_code_matches_manifest` is folded into `all_ok` (verify_reveal.py:57-64).
3. CSPRNG: `secrets.token_hex(32)` (draw.py:154).
4. Exposed-D rejection: draw.py:62-72. Notes in N-4.

### v4 P1: HOLDS for the tested shape (the package-directory plant); S-3 for PYTHONPATH/usercustomize

- entry.py:46-60 drops sys.path[0] first, filters to stdlib, and refuses under `-S` without os.
- `-S`: either refuses or re-execs. Not exploitable.

### v4 P2: HOLDS inside the entry-launched interpreter

- sys.path has no repo or cwd (entry.py:261-274, 285).
- The guard refuses any non-prometheus module resolving inside the repo (entry.py:154-163).
- prometheus.* loads only bound `.py` through a hash-then-compile loader. `__pycache__` is never read (entry.py:164-193).
- Extension/`.pyc`/package-dir shadows of bound names resolve to non-`.py` or unbound origins and are refused. That is fail-closed (DoS only).
- Outside this interpreter: B-1 (child executable), B-2 (allowlist), S-1 (spawn child), and F-3P (declared).

### v4 P3: HOLDS for `gates` (entry.py:78-79; selftest_protocol.py:620-625); the end-to-end run is S-1

### F-GITENV: HOLDS for GIT_*/replace refs (entry.py:116-122; protocol.py:179-185); N-3 for config/grafts/shallow

### F-FETCH / F-GOV / F-ONCE: HOLD (entry.py:201-204, 238-245; protocol.py:347-351; custody.py:122-133); S-6 minor

---

## 6. Always-check classes

| class | result |
|---|---|
| 1 code running with secrets but unbound | **B-1** (icacls), **B-2** (comms/evidence_wiki/git), S-2 (firewall-check), F-3P site-packages (declared). The whole `H:\Python312` tree, not only site-packages, is likely writable: CANNOT-VERIFY; it should be declared |
| 2 same-account readability | declared (FIREWALL.md:209-216). The pairing "custodian account runs code from unprotected main" (B-2, S-2) is not declared |
| 3 static-audit bypass | the AST audit is a heuristic (declared); `from X import name` and `*` are now flagged (runner.py:413-415) |
| 4 git ref ambiguity / simplification | HOLDS in entry/protocol. allowlist.py uses unqualified refs and a bare git (B-2). Grafts: N-3 |
| 5 unauthenticated records | S1 OPEN (declared). ALLOWLIST.json is writable by the custodian account |
| 6 public fields narrowing hidden content | length (declared); timing (N-1) |
| 7 spoofable host/identity | hostname via `socket.gethostname()` (protocol.py:471); the USERNAME env var in the ACL grant (S-5); the comms sender (S1, declared) |

## 7. Declared residual risks

| declared residual | assessment |
|---|---|
| Gates are no boundary against the key holder | Acceptable. But "key holder" now effectively includes **anyone who can push to main**, through B-1, B-2 and S-2. That is not declared and not acceptable |
| Prediction package is Python as the operator account; the AST audit is a heuristic | Acceptable as declared. Note that production runs cannot complete at present (S-1) |
| Single-draw provenance is a custodian statement | Acceptable |
| The System interface exposes physics | Acceptable (contract design) |
| Branch protection off | Not "contained by S1" as FIREWALL.md v2 argued. Unprotected main is a code-injection path into custodian-account processes (B-1, B-2, S-2) |
| Separate child account; network egress | Acceptable as host capability requests. They must be verified *before* key release (S-1) |
| F-3P third-party code | Acceptable as declared. Extend it to the whole interpreter tree if writable |
| entry.py cannot vouch for itself | Acceptable (the printed sha is compared by the custodian) |

**Missing from the list:**
- the Cosmos→custodian-account code path via unprotected main (B-2, S-2);
- the timing channel (N-1);
- protocol-directory/extra-`.py` DoS by any pusher (N-2);
- the fail-after-release deadlock (S-1).

## 8. What would change the verdict

1. **B-1:** run icacls (or any helper) by absolute path, or use the Win32 API. Set `NoDefaultCurrentDirectoryInExePath` in entry's own environment. Add a positive-control test.
2. **B-2:** start allowlist.py through entry with a binding; use hardened git; import no working-tree code in the custodian account.
3. Should-fix before a real release: S-1 (probe and capability checks before release; a child import path that works under entry; an entry end-to-end RUN test), S-2, S-3, S-4, S-5, S-6.
4. S1 (#925) and branch protection: operator decisions, still open.
