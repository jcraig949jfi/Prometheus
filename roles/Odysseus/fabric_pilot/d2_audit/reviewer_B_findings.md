# Holdout D2 firewall audit: adversarial findings

- Auditor: fabric worker (task tsk-04cdac1aa3be, attempt att-0a71228d87d7), acting for Odysseus.
- Date: 2026-09-28.
- Audited commit: **e66f57208**, the tip of `prometheus/cosmos/c3_holdout_D2` history.
  - `git log --all -- prometheus/cosmos/c3_holdout_D2` lists only 95b31a30d, 06f53ae24 and e66f57208.
  - Every file in the package is therefore byte-identical at origin/main = bec1d275c.
- Method: `git show`/`git log` only. I could not run Python, compute sha256, or run the self-tests.
  - Every file:line below refers to `git show e66f57208:<path>`.
  - Paths are relative to `prometheus/cosmos/c3_holdout_D2/` unless a full path is given.
- Scope: firewall/custody layer only. No law, prediction or science was read or needed.

## Verdict: FAIL (do not commit a PASS record)

Three findings block PASS:

- **F1**: Cosmos-authored code outside `AUDITED_FILES` runs inside the custody and runner processes before any gate.
- **F2**: the predictor process can read the key and the plaintext. The AST audit can be bypassed with zero flags.
- **F3**: `origin/main` can be shadowed by a pushed tag, so every gate can read an attacker-chosen history.

F3 is borderline between blocks-PASS and should-fix; see its severity note. It is a one-line fix, so it should go into
the same re-audit round as F1 and F2.

| # | claim | verdict |
|---|---|---|
| 1 | Opacity | HOLDS (crypto and commitment). Note N1: the ciphertext length leaks one noisy aggregate. |
| 2 | Secrets never in git | HOLDS at file level. Content-level absence is CANNOT-VERIFY-FROM-REPO. |
| 3 | Enforced order | **BROKEN**: F1 (blocks-PASS), F3, F4 and F5 (should-fix). |
| 4 | Controlled reveal | HOLDS, with should-fix F6 and note F7. |
| 5 | Predictor isolation | **BROKEN**: F2 (blocks-PASS). |
| 6 | Draw integrity | HOLDS by construction. The at-draw source hashes are CANNOT-VERIFY here (no hashing tool). Notes N4 and N5. |

---

## Claim 1: Opacity

### Attacks tried

**1a. Break or bypass the cipher.**
- AES-256-GCM via `cryptography` AESGCM (sealbox.py:17, :70-80).
- The key is `secrets.token_bytes(32)` (sealbox.py:48-49). The IV is `secrets.token_bytes(12)` (sealbox.py:56-57).
- The AAD is the prefix plus the family sha (sealbox.py:60-61).
- There is exactly one encryption under this key (draw.py:103-106). Nothing is reused, so there is no GCM nonce-reuse
  angle.
- **Holds.**

**1b. Brute-force the commitment.**
- Commitment = sha256(salt ‖ plaintext) with a 32-byte secret salt (sealbox.py:64-67, draw.py:104, :133).
- The plaintext also contains the 256-bit nonce (draw.py:78).
- Guess confirmation is infeasible even per world. **Holds.**

**1c. Public fields that narrow the set.**
- Manifest keys (draw.py:113-142, MANIFEST_D2.json:1-36) are all public constants, versions, hashes and the IV.
- There is no nonce, world, seed or per-knob summary.
- `spec_id` hashes only public data (sealbox.py:91-93). **Holds**, except N1.

**1d. Ciphertext length (N1, note).**
- `ciphertext_bytes` = 17227 (MANIFEST_D2.json:5, written by draw.py:129) is |plaintext| + 16.
- The plaintext is unpadded canonical JSON (draw.py:76-88). Its length varies with the decimal lengths of:
  - `D=0.05`, `v=0.25`, `p_decay∈{0.01,0.03}`, `sigma=0.05` and `d_patch∈{12,16}` (medium.py:204-217);
  - the 128 run seeds (0…2³¹−2, draw.py:71);
  - `rejected`.
- So the length publishes one integer: the sum of those counts plus the sum of seed digit lengths.
- Rough estimate: sd ≈ 11 from the world part and ≈ 7 from the seeds. Well under 1 bit about any single knob
  distribution, and nothing about any single world.
- It is technically a "distributional summary", which the brief says is absent.
- Fix, optional: pad the plaintext to a fixed size before encryption on any future seal. **Note.**

**1e. Receipts and result record.**
- Receipt bodies: open, prediction, predictions_sealed, certify and close (runner.py:493-504, :604, :616-618, :655-669,
  :692).
  - Worlds are identified only by index and `world_tag` = HMAC(key, …) (runner.py:467-468).
  - `_summ` drops the knob-bearing `system` name (runner.py:407-412).
- RESULT_SEAL carries only hashes, a constant count and fixed strings (custody.py:140-142). `n_receipts` is always
  3 + 2N.
- The `result_sha256` cannot be dictionary-attacked, because RESULT.json embeds keyed tags and receipt hashes
  (runner.py:686-698). **Holds.**
- Side remark, not a pre-commit leak: certify receipts record `noop` (w2 == w, runner.py:661-666). That reveals a
  hidden knob equals the intervention value. It only matters after the result seal. Fine for a single-use set.

**1f. Error messages.**
- The server reply carries the exception type name only (runner.py:579-580).
- Gate, custody and hidden-set errors print only public record names (protocol.py:67-116, runner.py:450-458).
- `PackageHashMismatch` prints two public package hashes (runner.py:341-342). **Holds.**

**Verdict: HOLDS** (N1 is a note).

---

## Claim 2: Secrets never in git

### Attacks tried

**2a. Secret-shaped files anywhere in history.**
- `git log --all --name-status -- "*hidden_D2*" "*.key.hex" "*salt*" "*nonce*" "*nestor_secrets*" "*.plain.json" "*_grep_patterns*"`
  finds exactly two kinds of hit:
  - 95b31a30d `A hidden_D2.enc`;
  - two unrelated nyx catalogue JSONs.
- `git log --all --stat -- prometheus/cosmos/c3_holdout_D2` shows only the three commits listed above.
- No plain/key/salt file was ever committed. **Holds.**

**2b. Secret material written into the repository by the tools.**
- draw.py writes secrets only to `SECRETS_DIR` and refuses a secrets dir inside git (draw.py:41, :100-111).
- custody refuses a destination inside git or inside the secrets dir (custody.py:88-94).
- The runner refuses a key or output inside git (runner.py:444-447).
- evidence refuses a bundle inside git (evidence.py:50-51).
- `firewall_check` writes its pattern file inside the secrets dir and deletes it (firewall_check.py:96-103).
- **Holds** for these code paths. It does not hold against code outside the audit binding: see F1 and F2.

**2c. Content-level leak (secret bytes inside an innocuous file).**
- This cannot be checked without the secrets.
- `firewall_check` git-greps only the tips given in `--git-ref`, default `HEAD origin/main` (firewall_check.py:77-81,
  :88). A secret committed and later removed would not be found.
- The FIREWALL.md checklist does ask for `$(git rev-list --all)` (FIREWALL.md:71-72), but for file names only.
- **CANNOT-VERIFY-FROM-REPO.**
- To settle it, ask Nestor to re-run `firewall_check --git-ref $(git rev-list --all)` on M1 (booleans only). That
  covers every historical tree, not just the tips.
- Also report `secrets_dir_files_expected` and the host.

**2d. Secrets on M2.**
- Nothing in the repo can show this; `firewall_check` runs on M1 only. **CANNOT-VERIFY.**

**Verdict: HOLDS** at file/history level. Content-level absence is **CANNOT-VERIFY-FROM-REPO**.

---

## Claim 3: Enforced order

### Attacks tried

**3a. Records read from the working tree instead of the committed tree.**
- Every record is read through `_show(repo, ref, …)`, i.e. `git show ref:path` (protocol.py:124-126, :166-173).
- Commit identity comes from `git log ref -- path` (protocol.py:129-131).
- The runner's worktree manifest and ciphertext are cross-checked against the gate spec_id and ciphertext hash
  (runner.py:448-455).
- **Holds.**

**3b. Order checks comparing the wrong commits.**
- The audit must follow the seal (protocol.py:215).
- The commitment must follow the audit (protocol.py:235).
- The designation must follow the audit (protocol.py:251).
- The result seal must follow both the commitment and the designation (protocol.py:269).
- `_strict_ancestor` excludes equality (protocol.py:134-135).
- The right commits are compared. **Holds.**

**3c. Stale-audit check.**
- Hashes are checked for both the ref tree and the executing worktree (protocol.py:217-224).
- A missing file counts as stale.
- **Holds, but only for the 13 files listed.** See F1.

**3d. Key paths reachable before the gates.**
- runner.py reads the key only after the gates (gates at :442-443, key read at :459).
- custody runs its gates before reading the key or secrets (release at :106-109, reveal at :153-163).
- **Broken by F1**: module-level imports execute unbound code before any gate.

**3e. Rewrite detection.** Broken by F4.

**3f. Ref integrity.** Broken by F3.

**3g. Record authorship.** Broken by F5.

### F1: Executed modules missing from `AUDITED_FILES`; the missing ones are Cosmos-authored (blocks-PASS)

**Evidence**
- `AUDITED_FILES` (protocol.py:58-64) lists 13 files.
- runner.py imports these at module load, before `open()` runs any gate (runner.py:72-76):
  - `prometheus.cosmos.c3.certify`, which imports `prometheus.cosmos.c3.probe` (certify.py:15);
  - `prometheus.cosmos.c3.system`, which also imports `probe` (system.py:110).
- None of these executed files are bound:
  - `prometheus/cosmos/c3/probe.py`;
  - `prometheus/__init__.py`, `prometheus/cosmos/__init__.py`, `prometheus/cosmos/c3/__init__.py`;
  - `prometheus/cosmos/c3_holdout_D/__init__.py`.
- custody.py and evidence.py execute `prometheus/__init__.py` and `prometheus/cosmos/__init__.py` on every invocation,
  because they are package imports.
  - `custody result-seal` also imports runner, and so probe (custody.py:122).
- Authorship, from `git log --all -- prometheus/cosmos/c3/probe.py prometheus/cosmos/c3/__init__.py prometheus/cosmos/__init__.py`:
  - 940b486f2 "Cosmos C3 (public subset) …";
  - 70ce535a2 "Cosmos CWE round 1-3 …".
- `prometheus/cosmos/__init__.py` names "Seat: roles/Cosmos/".
- Cosmos has push access to main: it commits `PREDICTION_COMMITMENT.json` itself (FIREWALL.md:94).

**Scenario**
1. After the PASS audit, Cosmos pushes an ordinary-looking edit to `prometheus/cosmos/c3/probe.py` or
   `prometheus/cosmos/__init__.py`.
2. `check_gates` compares only `AUDITED_FILES`, so it raises no `AuditStale` (protocol.py:218-224).
3. Nestor pulls main on M1. The worktree check passes too.
4. The next `custody.py release-key`, `runner.py`, `selftest_D2` or `selftest_protocol` run on M1 executes Cosmos's
   module-level code as the operator account, before any gate.
5. That code can:
   - read `C:/Users/jcrai/nestor_secrets/holdout_D2/hidden_D2.plain.json` (the path is public: custody.py:39-40,
     draw.py:41);
   - monkeypatch `protocol.check_gates`, `sealbox.decrypt` or `runner.FirewallRun`;
   - exfiltrate with the operator's network and git credentials, e.g. push to a branch.
6. It needs no `COSMOS_BROKER`.
7. If this happens before Cosmos commits its package hash, Cosmos then commits a package tailored to the hidden set.
   Opacity and the order are both void.

A milder variant with the same root cause: `probe.cv_ce_bits` computes P1 inside `certify` (certify.py:15). Editing it
after the audit changes the certificate without making the audit stale.

**Fix**
- Bind the full transitive closure of first-party modules the D2 entry points import:
  - at least `probe.py` and the four `__init__.py` files;
  - `c3_holdout_D/sealed_spec_D.json`, which the redraw check reads (draw.py:57-59).
- Better: compute the set from `sys.modules` at gate time and refuse any first-party module whose file is not bound.
- Also consider pinning third-party versions (numpy, scipy, cryptography) in the audit record.
- Declare the wider host-hygiene risk (see "Residual risks").

### F3: `origin/main` can be shadowed by a tag (should-fix; borderline blocks-PASS)

**Evidence**
- `DEFAULT_REF = "origin/main"`, an abbreviated refname (protocol.py:45).
- The ref is passed unqualified to `git rev-parse`, `git show ref:path` and `git log ref` (protocol.py:125, :130,
  :189).
- git resolves an abbreviated name in the order `refs/<n>`, `refs/tags/<n>`, `refs/heads/<n>`, `refs/remotes/<n>`.
  - A tag named `origin/main` therefore wins over the remote-tracking branch.
  - git only prints an "ambiguous refname" warning to stderr, which `_git`/`_show` discard (protocol.py:120-126).

**Scenario**
1. Cosmos pushes a branch with a crafted history on top of the real main. It contains:
   - `FIREWALL_AUDIT.json` with `PASS`, the public spec_id, and the current code hashes (computable by anyone);
   - any commitment;
   - a designation for host SKULLPORT.
2. Cosmos also pushes a tag `origin/main` pointing at that branch's tip.
3. A normal `git fetch` on M1 auto-follows tags that point into fetched history.
4. From then on every gate on M1 reads Cosmos's history, not main.
5. The audit and order gates open, even though main shows no audit.

The key still needs Nestor to act, and the runner id must match. That is why this is not strictly blocks-PASS. But it
defeats exactly what the gates claim to guarantee: a mechanical order read from the public main.

CANNOT-VERIFY from the repo:
- whether GitHub lets Cosmos create tags;
- M1's `remote.origin.tagOpt`.

**Fix**
- Use `refs/remotes/origin/main`, fully qualified.
- Refuse if `git rev-parse --symbolic-full-name` differs.
- Optionally compare against `git ls-remote origin refs/heads/main`.
- A related, key-holder-only note: `refs/replace/*` and local git config also influence `git show`/`git log`.

### F4: Record rewrite hidden by a merge (should-fix)

**Evidence**
- `_commits_touching` runs `git log --format=%H ref -- path` with default history simplification (protocol.py:129-131).
- When a merge is TREESAME to one parent for the path, git follows only that parent. Commits on the other line are
  never listed.
- main does contain merges (7c018d92b), so a merge would not look unusual.

**Scenario**
1. Cosmos's commitment C1 is on main after audit A.
2. Cosmos branches from A (before C1) and commits a different `PREDICTION_COMMITMENT.json` as C2.
3. Cosmos merges into main, resolving the file to C2's version.
4. `git log main -- PREDICTION_COMMITMENT.json` now lists only C2:
   - the merge is TREESAME to C2, so only that parent is followed;
   - C1 is on the pruned line.
5. `_added_once` returns C2 with count 1, so no `RecordRewritten`.
6. C2 descends from A, so the order check passes.

The "frozen" commitment has been swapped with no refusal. The same works for the audit and designation records
(subject to the order constraints), and for the result seal before a reveal.

The selftest's `commitment_rewritten` case uses only a linear second commit (selftest_protocol.py:169-170), so it misses
this.

**Fix**
- Use `git log --full-history --format=%H ref -- path`, or `rev-list` with the same flag.
- Also require byte equality `git show <added_commit>:path == git show ref:path`.
- Optionally require the adding commit to be on the first-parent chain of the ref.
- Add a merge case to the selftest.

### F5: Records are unauthenticated (should-fix)

**Evidence**
- `check_gates` checks format, spec_id, verdict and hashes. It never checks who wrote a record.
  - `auditor`, `designated_by`, `committer` and `sealed_by` are informational (protocol.py:209-271).
- Every commit in the relevant history has the same author identity (James Craig), and none is signed:
  `git log --format="%G? %an"` shows `N James Craig` for e66f57208, 06f53ae24, 95b31a30d, 7c018d92b, a56ef7787 and
  940b486f2.
- So git cannot attribute a record to a seat.

**Scenario**
- Cosmos, which can push to main, commits `FIREWALL_AUDIT.json` with verdict PASS itself, skipping the independent
  audit.
- Alternatively, Cosmos squats `RUNNER_DESIGNATION.json`. Records are immutable, so a squatted designation for a wrong
  host is a permanent denial of service on D2.

**Fix**
- Require signed commits for `protocol/*` and verify them in `check_gates` against a pinned allow-list of
  keys per record type: auditor, Cosmos, custodian.
- Or pin the audit commit hash out-of-band.

**Verdict for claim 3: BROKEN** (F1 blocks PASS; F3, F4 and F5 should be fixed in the same round).

---

## Claim 4: Controlled reveal

### Attacks tried

**4a. Key release to an undesignated host or runner, or to M2.**
- Gates through DESIGNATION include `runner_id` and host (custody.py:106, protocol.py:253-259).
- Custody refuses to act on a forbidden host (custody.py:93-94).
- The key is written only to a local path on the host where custody runs, which must be the designated host.
- **Holds mechanically.** See note F7 on host spoofing.

**4b. Double release or reveal.**
- The once-only rule relies on the custody log (custody.py:107-108, :159-160).
- The log is a mutable M1 file, so it is only a boundary against honest mistakes. Declared residual risk 1 covers this.

**4c. Results leaving M1 before the result seal.**
- The result-seal record holds only public fields (custody.py:140-143).
- The evidence bundle requires RESULT_SEAL, a verifying chain, a matching head and a matching result hash
  (evidence.py:54-59).
- **Holds.**

**4d. Reveal on a record that does not correspond to a real, closed, committed-package run.**
- **F6, should-fix.** `reveal` checks only two things (custody.py:153-158):
  - `recs[-1]["hash"] == chain_head`;
  - the RESULT.json hash.
- It does not re-run `verify_receipts`, check `kind == "close"`, or check the package and spec_id.
- `evidence.build` does all of these (evidence.py:55-57).
- Reveal therefore trusts that `RESULT_SEAL.json` was produced by `result_seal_record`. Given F5 (anyone can commit
  that record) and F3 (the record may come from a shadowed ref), that trust is misplaced.
- Exploiting it still needs a run directory on M1 whose hashes match. So the practical risk is low.
- **Fix:** make `reveal` call the same checks as `result_seal_record`/`evidence.build`.

**4e. Multiple runs; the custodian chooses which run to seal (note).**
- The runner can be run any number of times with the released key (runner.py:729, fresh `--out`).
- Nothing binds "the" run before the result seal.
- The released key copy stays on disk in `dest` indefinitely (custody.py:110-111).
- A custodian-level issue: add a "RUN_STARTED" custody-log event and refuse a second run; delete the key copy after
  CLOSE.

**Verdict: HOLDS**, with should-fix F6 and note 4e.

### F7: Host checks are spoofable and match exact strings (note)

- `socket.gethostname()` is compared case-insensitively but exactly (protocol.py:249, :253-257; custody.py:71, :93).
- "SPECTREX5.lan", "SPECTREX5 " or any renamed host passes the M2 block.
- `Custody(host=…)` and `check_gates(host=…)` accept overrides. The CLIs do not expose them (custody.py:187,
  evidence.py:94).
- These checks are defence-in-depth only: a host that holds the key file can decrypt anyway. **Note.**

---

## Claim 5: Predictor isolation

### Attacks tried

**5a. Pickle or code injection into the runner through the pipe.**
- The pipe is JSON plus `.npy` with `allow_pickle=False` (runner.py:143-176). Object arrays are refused.
- The parent dispatches only whitelisted methods (runner.py:530-555).
- The child can reach the mangled `_HiddenWorldStub__conn`, but can only send messages the parent already validates.
- **Holds.**
- DoS note: a deeply nested JSON reply raises `RecursionError`, which `_predict_one` does not catch (runner.py:571-574).
  That aborts the run with no way to resume prediction. This is a note only.

**5b. Knob leakage through the stub or error text.**
- The child receives only V, k and a public seed (runner.py:563, :592-593).
- Server errors carry type names only (runner.py:579-580). **Holds.**

**5c. The child reads the secrets from disk.** Broken: F2.

### F2: The predictor runs as the key-holding account and the AST audit is bypassable with zero flags (blocks-PASS)

**Evidence**
- The child is `mp.get_context("spawn")` in the same user account (runner.py:509-514).
- It imports the package with `sys.path.insert(0, pkg_dir)` (runner.py:223-227).
- The secret paths are published in code (custody.py:39-40, draw.py:41):
  - `C:/Users/jcrai/nestor_secrets/holdout_D2/hidden_D2.plain.json`;
  - `…/hidden_D2.key.hex`.
- The released key copy is also on disk. Its path is in `sys.argv`, which spawn passes to the child.

**Bypasses that produce no audit flag**
- **Aliased builtin.** `f = [open][0]; f(r"C:/Users/jcrai/nestor_secrets/holdout_D2/hidden_D2.plain.json").read()`.
  - Only calls whose `func` is a bare `ast.Name` in `FORBIDDEN_CALLS` are flagged (runner.py:101-102, :327).
  - A bare `open` Name is flagged only if it starts with `__` (runner.py:332).
- **numpy file reads.** `np.fromfile(path, dtype=np.uint8).tobytes()`, or `np.load(<file in package>, allow_pickle=True)`,
  which is arbitrary code via pickle.
  - numpy is allowed, and attribute calls are never checked (runner.py:313-333).
- **Sourceless bytecode.** Ship `helper.pyc`, a CPython 3.12 sourceless module, or a `.pyd`, and `import helper`.
  - Only members ending in `.py` are audited (runner.py:374-376).
  - Every member is extracted (runner.py:381-384).
  - Python imports sourceless `.pyc`/extension modules from the `sys.path[0]` directory. This also defeats the
    "Nestor reads the package source" mitigation (FIREWALL.md:48-53): there is no source to read.

**Scenario**
1. Cosmos commits a package whose `predictor.py` contains one of the lines above.
2. `load_package` records `audit_flags: []`. No `--allow-flagged` is needed.
3. Each `predict()` reads the plaintext, looks up world i's true knobs and run seed, and returns the "right" class.
4. The holdout test is void, and the receipts look normal.

**Scope and severity**
- The brief declares this class of risk (residual risk 2). The claim as worded, "separate process without the key",
  is still false at the OS level.
- The declared mitigation is optional ("read the package … **or** run it under a low-privilege account"), and the
  first option is defeated by the third bypass.

**Fix (required for PASS)**
1. Refuse every package member that is not `.py`/`.json`/`.txt`.
2. Make the separate low-privilege account mandatory, and have the runner verify it before spawning the child. For
   example, launch the child with that account's token and verify the process owner. The account must have no read
   access to `nestor_secrets`, the key `dest`, `nestor_receipts` or the repo worktree.
3. Keep the AST scan as a lint only.

**Verdict for claim 5: BROKEN** (F2, blocks-PASS).

---

## Claim 6: Draw integrity

### Attacks tried

**6a. Nonce quality.**
- `secrets.token_hex(32)` (draw.py:154), reduced mod 2¹²⁸ to seed PCG64 (draw.py:63). 128 bits is ample.
- **Holds.**

**6b. Uniformity and exposed-D rejection.**
- Uniform per knob via numpy `integers`, with rejection on the geometric constraint (medium.py:228-237). That is
  uniform over the valid lattice.
- Rejection of exposed-D worlds, keeping the same rng stream (draw.py:62-70). That is uniform over the valid lattice
  minus the exposed set.
- Run seeds come from the same rng afterwards (draw.py:71).
- Duplicates within D2 are possible (sampling with replacement). That is a design choice, not a defect.
- **Holds.**

**6c. Reproducibility.**
- `verify_reveal --redraw` re-derives worlds, seeds and the rejected count (verify_reveal.py:54-58).
- The exposed set is read from `sealed_spec_D.json`, which is not in `AUDITED_FILES` (see F1).
- **Note N4:** numpy does not guarantee `Generator` streams across versions. A redraw must use numpy 2.2.6 (manifest
  line 27), or it may fail spuriously.

**6d. At-draw source hashes equal main.**
- `d2_src_sha256_at_draw` (MANIFEST_D2.json:11-15, draw.py:135).
- `git log --all` shows `__init__.py`, `draw.py` and `sealbox.py` touched only by 95b31a30d, the same commit as the
  manifest.
- Actual hash equality is **CANNOT-VERIFY here** (no hashing tool). To settle it, run
  `git show 95b31a30d:<file> | tr -d '\r' | sha256sum` for each of the three files.
- The same applies to the brief's `ciphertext_sha256`, the manifest file sha and the spec_id recompute.
- The ciphertext size, 17227 bytes, matches the commit stat.

**6e. Nonce grinding (N5).**
- The custodian could run draw.py privately many times and seal a favourable set.
- Nothing commits to the nonce before the draw.
- This is only partly covered by declared residual risk 3 ("ran once").
- Fix for future seals: commit to sha256(nonce) or use a public beacon before the draw.

**Verdict: HOLDS** (N4 and N5 are notes; 6d is CANNOT-VERIFY here).

---

## Declared residual risks

| # | residual risk | assessment |
|---|---|---|
| 1 | The gates are not a boundary against the key holder. | Acceptable as declared. |
| 2 | The package is Python run as the operator; the AST audit is a heuristic. | **Not acceptable as declared.** The mitigation is optional, and "read it first" is defeated by `.pyc`/`.pyd` members and aliasing (F2). It must become an enforced separate account plus a non-`.py` member refusal. |
| 3 | Single-draw provenance is a custodian statement. | Acceptable. Also name nonce grinding (N5) explicitly, and commit to the nonce beforehand on future seals. |
| 4 | The System interface exposes physics by design. | Acceptable. Out of firewall scope, and consistent with FIREWALL.md:46-47. |

### Missing from the list

1. **Cosmos-authored first-party code executes on M1 as the key-holding account.**
   - This happens inside the D2 tools (F1). It also happens in *any* Prometheus command Nestor runs on M1 that imports
     `prometheus.cosmos`.
   - It needs its own line and a mitigation: bind the closure, and run D2 tooling from a pinned, audited checkout.
2. **Protocol records are unauthenticated** (F5). All commits share one unsigned identity.
3. **Ref resolution and fetch state on M1** (F3), plus `refs/replace` and local git config.
4. **Merge-based rewrite of immutable records** (F4).
5. **Custodian chooses among multiple runs; the key copy persists** (4e).
6. **Ciphertext length leak** (N1). Tiny, but it contradicts "no distributional summaries".
7. **Immutability deadlock.** Once a PASS audit is committed, any code change leaves the audit permanently stale:
   records cannot be re-added (protocol.py:138-145, :219-224).
   - The brief's "re-audit binds new code hashes" works only while no PASS is on main.
   - Decide now how a post-PASS fix would be handled, e.g. a versioned audit record file.

## Blocks-PASS findings (summary)

- **F1**: `AUDITED_FILES` (protocol.py:58-64) omits executed, Cosmos-authored modules:
  - `prometheus/cosmos/c3/probe.py`;
  - `prometheus/__init__.py`, `prometheus/cosmos/__init__.py`, `prometheus/cosmos/c3/__init__.py`,
    `prometheus/cosmos/c3_holdout_D/__init__.py`.

  They run at import in runner/custody/evidence before any gate (runner.py:72-76, certify.py:15, system.py:110). A
  post-audit edit by Cosmos runs as the operator on M1 with the secrets at a public path. The audit does not go stale.
- **F2**: the predictor child runs as the key-holding account (runner.py:509-514, :223-227), and the secrets are at
  published paths (custody.py:39-40). The AST audit is bypassed with zero flags by:
  - `[open][0](path)` (runner.py:327, :332);
  - `np.fromfile`/`np.load(allow_pickle=True)`;
  - shipping a sourceless `.pyc`/`.pyd` (only `.py` is audited, runner.py:374-376; everything is extracted, :381-384).

  Result: perfect "predictions" from the plaintext. The declared mitigation is optional and defeatable.

## Should-fix (same re-audit round)

- **F3**: a tag named `origin/main` shadows the remote-tracking ref (protocol.py:45, :125, :130, :189). Borderline
  blocks-PASS.
- **F4**: `git log` history simplification hides a rewritten record behind a merge (protocol.py:129-131, :138-145).
- **F5**: records are unauthenticated; all commits are unsigned under one identity.
- **F6**: `custody.reveal` does not re-verify the chain, CLOSE or the package (custody.py:153-158).

## Notes

- F7: host spoofing and FQDN variants.
- N1: ciphertext length.
- N4: numpy stream stability for the redraw.
- N5: nonce grinding.
- 4e: multiple runs and the persistent key copy.
- 5a: `RecursionError` DoS.
- firewall_check greps only the tips.
- Immutability deadlock.

## What would settle the CANNOT-VERIFY items

1. On any machine: sha256 (CRLF→LF) of `git show 95b31a30d:…/{__init__,draw,sealbox}.py`, compared with
   `d2_src_sha256_at_draw`. Also sha256 of `hidden_D2.enc` and `MANIFEST_D2.json`, and the spec_id recompute.
2. On M1 (booleans only): `firewall_check --git-ref $(git rev-list --all)`, the `secrets_dir_files_expected` output,
   and confirmation that the secrets dir is not synced.
3. GitHub settings: whether non-custodian seats can push tags and force-push to main; whether signed commits are
   required.
4. On M1: `git config --get remote.origin.tagOpt` and `git for-each-ref refs/tags/origin refs/replace`.
