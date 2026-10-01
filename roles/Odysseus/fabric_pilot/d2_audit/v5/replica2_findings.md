# Holdout D2 firewall re-audit v5: adversarial findings (one replica)

- Audited commit: 57c809387 (HEAD of this checkout). The paths are under `prometheus/cosmos/c3_holdout_D2/`.
- Method: I read the code statically and checked history with `rogit`. I executed no code under audit.
  I recomputed hashes with sha256sum and jq, and got:
  - `sha256(hidden_D2.enc) = f75ba333…fc9f`
  - `sha256(MANIFEST_D2.json) = 78874e9d…71fe`
  - `spec_id` recomputes to `e2d3213b…d9fe`
  - `draw.py`, `sealbox.py` and `__init__.py` hash to `d2_src_sha256_at_draw`
  - `medium.py` hashes to `family_src_sha256` (`09559e69…cde4`)
- **Not done: running the selftests.** I could not run `selftest_protocol` or `selftest_D2`, or run `entry.py gates SEAL`
  against the real history. The fabric script node would have to do that. Every verdict below is a code reading.
- Scope: the firewall layer only.

## Claim verdicts

### Claim 1: Opacity. HOLDS
- **Attack: brute-force a candidate world against the commitment.** The salt is 32 bytes from `secrets`
  (sealbox.py:52-53, 64-67), so a guessed world cannot be confirmed.
- **Attack: public fields.** The manifest (MANIFEST_D2.json:1-36) has IV, hashes, versions and draw_utc. It has no knob,
  seed or nonce. `ciphertext_bytes` = 17227 gives the plaintext length (17211). That is a declared residual.
- **Attack: public hashes of results.** The RESULT_SEAL fields are chain_head, result_sha256 and n_receipts
  (custody.py:241-244). They cannot be brute-forced back, because every certify and prediction receipt carries
  `world_tag = HMAC(key, …)` (runner.py:617-618). n_receipts is fixed at 2N+3.
- **Attack: error-reply channel.** The runner sends back only `type(e).__name__` (runner.py:760-761).
  - Exception-type variation is a small side channel that the interface itself creates (declared class).
  - Timing is declared as N-1.
- **Attack: the selftest files.** `SELFTEST_*.json` contain no 32+ hex strings (grep, 0 hits).
- **Note:** the same key is used for AES-GCM and for the world_tag HMAC (runner.py:617). This is acceptable, but a
  future seal should derive separate keys.

### Claim 2: Secrets never in git. HOLDS as far as the repository can show; CANNOT-VERIFY at content level
- **Attack: file names.**
  - `rogit log --all --full-history` on hidden_D2.enc and MANIFEST_D2.json shows exactly one adding commit, 95b31a30d.
    Every other commit that touches them is a merge that carries the same blob.
  - No `*key*`, `*salt*` or `*.plain*` file was ever in `c3_holdout_D2/`.
- **Attack: key-shaped content.** A 64-hex key looks like any other hash in the repo, so it cannot be told apart
  statically. This is settled only by the key-holder scan (`entry.py firewall-check`).
  - The scan looks for key and salt as hex, raw bytes and base64 (firewall_check.py:43-58, 105-155).
  - The scan cannot see objects that were pushed and then removed from the remote's refs. GitHub may keep them
    reachable by SHA. **Missing residual.**

### Claim 3: Enforced order. BROKEN (blocks-PASS, finding F1)
- **Order: HOLDS.**
  - Records are read only from the committed tree of `refs/remotes/origin/main`, resolved once (protocol.py:438-439).
  - Shadow refs are refused (protocol.py:253-263).
  - "Added once" uses `--full-history -m` (protocol.py:266-310), and ancestry is strict (protocol.py:470-474, 508, 528, 555).
  - An audit binds exactly AUDITED_FILES, in the committed tree and the working tree (protocol.py:484-492).
  - Grafts and shallow files are refused (protocol.py:203-213). Replace objects are off (protocol.py:179-185).
- **Attack: make the runner fail after it consumes the key. It succeeded; see F1.** The claim says "the runner … refuse[s]
  before touching the key" and v5 S-1 says "A refusal consumes nothing". Neither is true for package refusals.

### Claim 4: Controlled reveal. HOLDS, subject to S1 (open)
- **Key release.**
  - Release requires DESIGNATION gates on this host (custody.py:182). The host must equal the designation host and
    must not be SPECTREX5 (protocol.py:524-535, custody.py:132).
  - The destination must be a local fixed drive (custody.py:111-133) and fresh, and it is ACL-restricted before the
    write (custody.py:179-191).
  - icacls runs by absolute path (custody.py:52-62).
- **Once-only.** Enforced by the custody log, a committed record, and an O_EXCL lock (custody.py:183-186, 135-146).
- **Reveal.** Requires an allow-listed RESULT_SEAL plus a re-verified chain and result hash (custody.py:257-272).
  evidence.py:55-61 has the same checks.
- **Attack: force-push main to drop KEY_RELEASED.json.** `once_record_present` then reads false (protocol.py:402-410).
  The custody log is the remaining barrier, and it can be edited by the same account. This is inside the declared
  "branch protection off" residual, but the residual should say so explicitly (note).
- **Attack: name the custodian account in another form.**
  - `SKULLPORT\jcrai` passes the string check `!= "jcrai"` (protocol.py:526) and resolves as a SidTypeUser.
  - Custody would then grant the ACL to the custodian itself. The runner still fails closed, because GetUserNameW never
    equals that string (protocol.py:538).
  - Note: compare SIDs, not names.

### Claim 5: Predictor isolation. HOLDS as declared
- **The child.** It is a spawn child and receives no key. The pipe carries JSON plus `.npy` with `allow_pickle=False`
  (runner.py:167-200).
- **The probes.** Isolation probes run before the package is imported (runner.py:322-335). The preflight probe runs
  before the key is read (runner.py:605-607, 679-689).
- **Attack: spawn child loads unbound code.**
  - The child re-runs entry.py as `__mp_main__` and installs the guard from `C3D2_BOUND` before it unpickles its
    target (entry.py:175-180).
  - The flags `-I -B` are propagated by multiprocessing, so there is no `''` or cwd path entry.
  - The guard compiles from the hashed source and never reads `__pycache__` (entry.py:161-172).
  - A non-`.py` origin (.pyd, .so or .pyc `__init__`) is refused (entry.py:145-146).
  - This holds.
- **Same-account child.** It is always refused ChildNotIsolated, which is declared.

### Claim 6: Draw integrity. HOLDS
- **Nonce and draw.** The nonce is `secrets.token_hex(32)`, and exposed-D duplicates are rejected (draw.py:62-72, 154).
- **Hashes.** The at-draw hashes match the current files; I recomputed them.
- **Redraw.** It checks its own code against the manifest (verify_reveal.py:56-63).
- **Minor weakening.** The rng seed is `nonce mod 2^128`, which is 128-bit security.
- **Single-draw provenance.** A custodian statement, as declared.

### v5 items
| item | verdict | evidence |
|---|---|---|
| B-1 icacls | HOLDS | custody.py:52-62, 161; entry.py:43 sets NoDefaultCurrentDirectoryInExePath |
| B-2 allowlist | PARTIAL: no repo code is imported, but repo DATA steers authentication (F2) | allowlist.py:49-75 |
| S-1 preflight | BROKEN (F1) | runner.py:605-641 |
| S-2 binding/pins | HOLDS (note F6) | entry.py:250-281 |
| S-3 `-I -B` only | HOLDS | entry.py:34-43 |
| S-4 ref only origin/main | HOLDS | custody.py:307, runner.py:911, evidence.py:98 |
| S-5 git hardening | HOLDS except firewall_check (F4, note) | protocol.py:188-194; firewall_check.py:61-63 |
| S-6 fail closed | HOLDS | protocol.py:408-409 |
| Planted modules (package dir, repo root, cwd, `.pyc`, `-S`, PYTHONPATH, GIT_*, replace refs, git.exe in cwd) | HOLDS | entry.py:34-43, 77-110, 132-155, 231-235, 312-325. `.pth` in site-packages is the declared F-3P residual |

## Findings

### F1: package refusals come after the one-time key release is consumed. Severity: blocks-PASS
**Code path.** `FirewallRun.open()` runs these steps in order:
1. preflight (runner.py:605-606);
2. read the key (607);
3. delete the released key copy (608-609);
4. decrypt (610);
5. create the run directory (638);
6. only then `load_package` (641), which can raise PackageHashMismatch, PackageInvalid or PackageAuditRefusal
   (runner.py:452-495).

**Scenario.**
- Custody releases the key, and KEY_RELEASED.json is committed.
- Nestor runs `entry.py runner --package pkg.zip …`, and one of these is true:
  - the committed package has an AST flag, such as any bare `getattr` reference (runner.py:440-441);
  - it has a `.npy` or `.pyc` member (466-467);
  - the zip path points to a wrong or corrupted copy.
- The preflight passes, the key is read and deleted, `run_<nonce>/` is created, and then load_package refuses.

**Effect.**
- A rerun is refused, because the run directory exists (runner.py:929-930).
- A new release is refused, because of the committed record and the custody log (custody.py:183-186).
- No second designation is possible, because the record is added once. D2 is burned irreversibly by a recoverable
  error.
- `--preflight` never calls load_package (runner.py:937-940), so Nestor has no way to check this in advance.
  `--allow-flagged` has to be chosen before the flags are seen.
- The v5 selftest covers only the same-account ChildNotIsolated path (selftest_protocol.py:893-896). No test covers a
  refusal after the preflight passes.

**Smaller variants.**
- Decryption errors (InvalidTag, uncaught) also come after the key is deleted.
- The second isolation probe also runs after consumption. It checks the receipts-append probe in `_start_worker`
  (runner.py:691-695) against a probe the preflight does not make (it checks mkfile in the out root only).

**Fix.** Hash, validate, audit and stage the package, and run the receipts-write probe, BEFORE the preflight and the
key read. Include the load_package checks in `--preflight`.

**Why blocks-PASS.** The v4 verdict made "the runner completes … BEFORE the release is consumed" a verdict-changing
condition, and brief claim 3 states the property directly.

### F2: allowlist.py takes its comms database settings from the repository working tree. Severity: should-fix (S1 class)
**Code.** `_db_settings()` reads `REPO/evidence_wiki/config.json` (committed) and `config.local.json`. It connects with
psycopg2 to the `db_host` found there (allowlist.py:49-66).

**Scenario.**
- A main pusher (branch protection is off) commits `evidence_wiki/config.json` with `db_host` pointing at a server
  they control.
- The custodian has no `EW_DB_HOST` and no local override of `db_host`, and runs `entry.py allowlist add --role AUDIT …`.
- The attacker's server returns a row with sender `Odysseus` and the record's sha256, and the entry is allow-listed.
- The configured database password is also sent to that server. libpq will answer a cleartext-password request.
  Credential values are deliberately not reproduced here.

**Also relevant.** The committed config itself says that the M1 Postgres accepts connections from LAN peers with the
committed credentials. So any LAN peer, M2 included, can insert a comms row with any sender. That is a second
confirmation that S1 is open.

**Assessment.** B-2 removed code execution but kept repo-controlled data on the authentication path. Any S1
resolution that keeps this path must pin the host and the credentials outside the repository.

### F3: on non-Windows hosts the allow-list path is relative to the current directory. Severity: note / should-fix
**Code.** `Path("C:/Users/jcrai/…/ALLOWLIST.json")` appears in entry.py:57, protocol.py:57 and allowlist.py:34. On POSIX
it is a relative path.

**Scenario.** entry.py on Linux with cwd = the repo root would read a committed
`C:/Users/jcrai/nestor_receipts/holdout_D2/ALLOWLIST.json`. That lets a main pusher forge every governing record for
gates or evidence runs on that host. Key-holding runs only on M1 (Windows), so the key is not exposed.

**Fix.** Refuse on non-Windows, or require the path to be absolute.

### F4: firewall_check git calls lack GIT_HARDEN. Severity: note
firewall_check.py:61-63 uses git_exe and git_env but not `-c core.hooksPath=…`. That contradicts "every git call" in
FIREWALL.md v5 S-5. The commands it runs (grep, rev-list, cat-file) run no hooks, so there is no current exploit.

### F5: custody edge cases. Severity: note
- **After the key write** (custody.py:203-207): `_append` and `_write_once_record` are outside the try.
  - If they fail, the key is released with no committed record, and possibly no log entry.
  - The lock stays behind. If it is removed by hand, a second release is possible.
- **Reveal** (custody.py:273-279): a partial copy is not cleaned up on failure.
- **Parent directory of dest:** not checked. Another local account with delete-child rights on the parent could swap the
  directory between `_restrict` and the write.

### F6: pre-audit pins are per file. Severity: note
entry.py:276-277 checks each file on its own. Files pinned in different pin sessions can be combined into a set that was
never reviewed together. Pins also never expire. The fix is to pin the digest of the whole set.

### F7: other notes
- `--allow-flagged` is a command-line knob, not bound by the designation (runner.py:897, 933). It is recorded in the
  receipts.
- For the firewall-check and allowlist targets, entry.py does not check the governing audit's format, spec_id, n or
  order (entry.py:255-271). It relies on the allow-list alone.

## Declared residuals
All of them are acceptable as declared: key holder, same account, F-3P, git configuration, timing (N-1), DoS by a main
pusher (N-2), entry.py cannot vouch for itself, plaintext length, and single-draw provenance.

**Missing from the list:**
- F1: post-consumption refusal. This is not a residual; it has to be fixed.
- The repo-data steering of the allow-list's database (F2).
- The LAN-open comms database (strengthens S1).
- Force-push re-enabling a once-only action, with only the editable custody log as a barrier.
- Remote-side unreachable objects, which the key-holder scan cannot see.
- POSIX path semantics (F3).

**OVERALL: FAIL**, on F1. S1 and branch protection remain open, as declared.
