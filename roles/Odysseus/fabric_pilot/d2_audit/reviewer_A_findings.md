# Holdout D2 firewall audit (adversarial): findings

- Auditor: independent adversarial worker (fabric task tsk-fe7759a0e631, attempt att-093d7e467252)
- Audited tree: repository commit `bec1d275c` (= `origin/main` in this checkout). The D2 package there is last
  touched by `e66f57208` (brief), `06f53ae24` (protocol layer) and `95b31a30d` (seal).
- Scope: the firewall layer only. No law, predictions or science were read or needed.
- Method: I read every file in `prometheus/cosmos/c3_holdout_D2/`, the modules it imports, and the git history
  (`git log`, `git show`, `git log -G`).
- Tool limits:
  - I could not run Python.
  - The sandbox also denied `sha256sum`, `git diff` and `git cat-file` pipelines.
  - So I could not recompute the published sha256 values (see "CANNOT-VERIFY" items).

**Overall: FAIL (do not commit a PASS record).** There are 3 blocks-PASS findings (F1, F2, F3) and several
should-fix and note items.

---

## Summary table

| # | Claim | Verdict |
|---|---|---|
| 1 | Opacity | **HOLDS** cryptographically. Note: the ciphertext length leaks one noisy aggregate (N1) |
| 2 | Secrets never in git | **HOLDS as far as the repository can show**. Full proof is CANNOT-VERIFY: it needs the key-holder scan, and that scan has gaps (S4) |
| 3 | Enforced order | **BROKEN**. F1 (hash-binding gap and import shadowing) and F2 (record swap through git-log history simplification) both block PASS. S1 (unauthenticated records) is should-fix |
| 4 | Controlled reveal | **HOLDS in its own logic**, but it inherits F1/F2 because it relies on `check_gates`. S2 and S3 are should-fix (run multiplicity, key path outside custody) |
| 5 | Predictor isolation | **BROKEN** in substance: the committed package can read the plaintext, seeds and key from disk with zero AST flags (F3, blocks-PASS). The narrow wording (the key is not in the child's memory, the pipe carries no pickle, errors carry type names) holds |
| 6 | Draw integrity | **HOLDS** in code. The published sha256 values are CANNOT-VERIFY here, and single-draw provenance is declared |

---

## Claim 1: Opacity

Attacks tried:

**1a. Brute-force a candidate world set against the commitment.**
- The commitment is `sha256(salt || plaintext)` with a 32-byte secret salt: `sealbox.py:64-67`, drawn at
  `draw.py:104` via `secrets.token_bytes` (`sealbox.py:52-53`).
- There are 2^256 salts, so it is infeasible. **Holds.**

**1b. Nonce/IV misuse or key weakness in AES-GCM.**
- The key is 32 CSPRNG bytes (`sealbox.py:48-49`) and the IV is 12 random bytes (`sealbox.py:56-57`).
- There is exactly one encryption under this key (`draw.py:106`), so the IV is never reused.
- The AAD is public by design (`sealbox.py:60-61`, `MANIFEST_D2.json:2`). **Holds.**

**1c. Public manifest fields that narrow the hidden set.**
- `MANIFEST_D2.json:1-35` carries no worlds, knobs, seeds, nonce or salt.
- `draw_utc` (`:18`) is public, but it is also inside the plaintext (`draw.py:83`), so it is known, not secret.
- **Note N1 (length leak).** `ciphertext_bytes: 17227` (`MANIFEST_D2.json:5`, written at `draw.py:129`).
  - AES-GCM output is the plaintext length plus a 16-byte tag, so the plaintext is exactly 17211 bytes.
  - Everything in the plaintext is public or of fixed length except the decimal lengths of the world values and
    run seeds (`draw.py:76-85`): format strings, lattice, 64-hex nonce, and the public `draw_utc`.
  - Knob values have variable-length reprs (`medium.py:204-216`):
    - `0.05` vs `0.0`/`0.2` for D and sigma;
    - `0.25` for v;
    - `0.01`/`0.03` for p_decay;
    - `12`/`16` for d_patch.
  - So the file size tells Cosmos one integer: (number of "long-form" knob values across 128 worlds) + (total digits
    of the 128 run seeds) + digits of `rejected`.
  - Rough size of the effect: seed-digit noise has sd ≈ 5.6 characters, and the knob aggregate has sd ≈ 11.
    That is under about 1 bit about the aggregate composition and nothing per world.
  - This contradicts the letter of "no distributional summaries" (AUDIT_BRIEF.md:27-28), but the effect is
    negligible.
  - Severity: **note**. For future seals, pad the plaintext to a fixed size.
- Excluding exposed-D worlds (`draw.py:67`) tells Cosmos that 128 known points (out of about 6.2×10^6 lattice
  points) are absent: negligible. **Note.**

**1d. Receipts and records.**
- Receipts carry an index plus `world_tag = HMAC(key, world||seed)` (`runner.py:467-468`, `604`, `655`), never
  knobs or seeds.
  - `selftest_D2.receipts_ok` checks this (`selftest_D2.py:114-117`), and a negative control fires
    (`SELFTEST_D2.json:29`).
- `certify` results are stripped of `r['system']`, whose name encodes the knobs (`runner.py:407-412`).
- The RESULT_SEAL record holds hashes plus `n_receipts` (`custody.py:140-142`). `n_receipts` is constant at
  1+128+1+128+1 = 259, because runs require exactly one prediction and one certify per world
  (`runner.py:613`, `679`). **Holds.**

**1e. Error messages and SELFTEST files.**
- Gate and custody refusal strings contain class names, paths, hostnames and commit ids only
  (`protocol.py:141-270`, `custody.py:85`, `196`).
- The runner's error replies are type names only (`runner.py:579-580`).
- `SELFTEST_D2.json` and `SELFTEST_PROTOCOL.json` are booleans and exception-class names only (read in full).
- **Holds.**

**1f. Pre-commitment code execution in a key-holder process.**
- This is the practical route to breaking opacity. It is F1 (claim 3) and F3 (claim 5).
- Opacity itself is sound only while no Cosmos-authored code runs as the M1 operator account.

**Verdict: HOLDS** (cryptographic layer), with note N1.

---

## Claim 2: Secrets never in git

Attacks tried:

**2a. Secret-shaped filenames anywhere in history.**
- I ran `git log --all --format= --name-only | sort -u` and filtered for key/salt/plain/secret/hidden_D2.
- The only D2 hit is `prometheus/cosmos/c3_holdout_D2/hidden_D2.enc`, added only in `95b31a30d`.
- Unrelated hits: `Aether/.../secrets.py` and catalog .json names.
- `git log --all --stat -- prometheus/cosmos/c3_holdout_D2` shows 3 commits (`95b31a30d`, `06f53ae24`,
  `e66f57208`), and none of them holds a key, salt or plain file. **Holds.**

**2b. Bare 64-hex lines (the key and salt file format, `draw.py:110-111`) committed under any name.**
- I ran `git log --all -G'^[0-9a-fA-F]{64}\s*$' -- prometheus/cosmos roles/Nestor roles/Cosmos`.
- It returns only `roles/Cosmos/campaigns/c0b/run_21fd1b2cc/STORE_SHA256.txt` (`8006c2eb0`) and
  `.../c0/run2_f31339054/STORE_SHA256.txt` (`54ca84228`).
- Both are C0 store hashes from commits that predate the D2 draw (2026-09-28T09:27:46Z, `MANIFEST_D2.json:18`), so
  they cannot hold D2 secrets.
- **Limits:**
  - I could not search the whole repository or all blob objects (sandbox denial).
  - I cannot test for the key or salt value without knowing it.
  - I cannot test raw-binary or base64 encodings.

**2c. Code paths that write secrets into a repository.**
- `draw.seal` refuses a secrets directory inside git (`draw.py:101-102`) and writes with `O_EXCL`
  (`draw.py:91-94`).
- `custody._dest_ok` refuses release/reveal destinations inside git or inside the secrets directory
  (`custody.py:88-94`).
- The runner refuses a key or output directory inside git (`runner.py:444-447`).
- The only other plaintext use is in memory (`runner.py:460-469`). **Holds.**

**2d. Gaps in the key-holder scan (should-fix, S4).**
- `firewall_check.git_grep` searches only the refs it is given, by default `HEAD origin/main`
  (`firewall_check.py:89`, `100-101`; checklist `FIREWALL.md:77`).
  - It does not search all history, other pushed branches, stashes or reflogs.
  - So a secret committed on a side branch, or committed and then reverted, is missed.
- The git grep patterns exclude run seeds and the plaintext hash (`firewall_check.py:97`), and there is no binary or
  base64 form.
- `.git` directories are skipped by the working-tree scan (`firewall_check.py:28`, `54`).
- Fix: grep `$(git rev-list --all)` (or `--all` with `--no-index` over packs), and add base64/raw forms of the key and
  salt.

**2e.**
- CANNOT-VERIFY that the secrets directory is unsynced (OneDrive, Dropbox) and that the released-key destination is
  unsynced. `_dest_ok` does not check sync.
- **Request to Nestor (booleans):** re-run `firewall_check` with `--git-ref $(git rev-list --all)` and all
  worktrees. Also report `secrets_dir_is_synced`, and whether the key copy at the release destination was deleted
  after the run.

**Verdict: HOLDS as far as the repository shows.** A complete negative (all history, all encodings) is
CANNOT-VERIFY without the key holder. S4 (scan covers only two refs) is should-fix.

---

## Claim 3: Enforced order: **BROKEN**

Attacks tried: (a) read records from the working tree instead of the committed tree; (b) compare the wrong commits;
(c) rewrite a record after the fact; (d) change code without making the audit stale; (e) forge a record; (f) reach a
key path before the gates.

**What holds:**
- Records come from `git show ref:path` (`protocol.py:124-126`, `166-173`), never from the working tree. The
  selftest case `commitment_only_in_worktree` is refused (`SELFTEST_PROTOCOL.json:26`).
- The runner reads the manifest and ciphertext from working-tree paths (`runner.py:448-455`, `710-711`), but binds
  them to the gate's committed `spec_id` and ciphertext hash (`runner.py:449-455`). **Holds.**
- The order comparisons are correct and strict:
  - seal < audit (`protocol.py:215`);
  - audit < commitment (`:235`);
  - audit < designation (`:251`);
  - commitment and designation < result seal (`:269`);
  - with `_strict_ancestor` = `merge-base --is-ancestor` and `a != b` (`:134-135`).
- Code staleness is checked against both the committed tree and the working tree (`protocol.py:217-224`).
- Every key path in runner and custody sits after `check_gates`:
  - `runner.py:442` before `:459`;
  - `custody.py:106` before `:109`;
  - `custody.py:153` before `:163`.

### F1 (blocks-PASS): AUDITED_FILES does not bind the code that actually runs in the key-holding process, and modules can be shadowed without changing any audited file

`AUDITED_FILES` (`protocol.py:58-64`) hashes 13 specific files. Code outside that list still runs inside the
runner, custody and evidence processes on M1.

**(i) Unbound imported modules:**
- `prometheus/cosmos/c3/probe.py`. It is imported by `certify.py:15` and `system.py:20`, and it computes the P1
  statistic (`cv_ce_bits`) that the runner's certification result depends on (`runner.py:651`, `664`).
- `prometheus/__init__.py`, `prometheus/cosmos/__init__.py`, `prometheus/cosmos/c3/__init__.py` and
  `prometheus/cosmos/c3_holdout_D/__init__.py`. These run on every `python -m prometheus.cosmos.c3_holdout_D2.*`,
  before any gate. That includes `firewall_check`, which loads all secrets with no gate at all
  (`firewall_check.py:38-46`).
- Git history shows the c3 code is Cosmos-authored and Cosmos-committed on main (commit `940b486f2` "Cosmos C3 …"
  touched `probe.py` and `c3/__init__.py`).

**(ii) Module shadowing.**
- Python's path finder picks a directory `X/` that contains `__init__.py` (or `__init__.pyc` or `.pyd`) over a
  sibling `X.py`.
- The records directory is `prometheus/cosmos/c3_holdout_D2/protocol/` (`protocol.py:43`), next to `protocol.py`,
  and Cosmos commits a file into exactly that directory (the commitment record).
- A committed `prometheus/cosmos/c3_holdout_D2/protocol/__init__.py` would therefore replace the gate module for
  every `from prometheus.cosmos.c3_holdout_D2 import protocol` (`runner.py:76`, `custody.py:36`, `evidence.py:32`).
  - `protocol.py`'s hash is unchanged, so nothing goes stale.
- The same works for `c3/certify/__init__.py` shadowing the audited `certify.py`, and so on.

**Scenario A (result manipulation):**
1. After Odysseus commits the PASS audit and after Cosmos's commitment, a commit on main edits `c3/probe.py` (or adds
   `c3/certify/__init__.py`).
2. `check_gates` reports nothing stale, because none of these paths is in `AUDITED_FILES` (`protocol.py:219-224`).
3. The runner then imports that code. It executes inside the process that holds the decrypted worlds and seeds
   (`runner.py:465-466`) and computes the certify results. It can bias them toward the committed predictions or
   write out the plaintext.
4. The open receipt records only `certify.py`'s hash (`runner.py:501`), so the receipts do not show it either.

**Scenario B (pre-commitment leak):**
1. A change to `prometheus/cosmos/__init__.py` (Cosmos's seat, `prometheus/cosmos/__init__.py:10`) reads
   `C:/Users/jcrai/nestor_secrets/holdout_D2/hidden_D2.plain.json` (the path is public: `custody.py:39`,
   `draw.py:41`, `firewall_check.py:26`) when present.
2. It runs the next time Nestor runs any `python -m prometheus.cosmos...` command on M1, including the checklist's
   `firewall_check` (`FIREWALL.md:77`), before Cosmos has committed its package.
3. No gate can stop it: it runs at import time.

**Fix:**
- Bind a tree hash (for example the git tree ids of `prometheus/cosmos/c3`, `c3_holdout_D`, `c3_holdout_D2` minus
  `protocol/`, and every parent `__init__.py`).
- At gate time, assert that every loaded module in `sys.modules` under `prometheus.` resolves to an audited path
  whose hash matches.
- Forbid any `__init__*` file under `protocol/`.
- Treat "Cosmos-authored code imported on M1" as the key-holder boundary. This is missing from the residual risks.

### F2 (blocks-PASS): the "added once / never modified" check is bypassable through git-log history simplification

`_commits_touching` runs plain `git log --format=%H <ref> -- <rel>` (`protocol.py:129-131`). With default history
simplification, git follows only one TREESAME parent of a merge and hides the other side.

**Scenario:**
1. Record R (say `FIREWALL_AUDIT.json` or `PREDICTION_COMMITMENT.json`) is added on main in commit A.
2. Someone creates branch S from a commit that is after the audit but before A. On S they add R with different
   content in commit B.
3. They merge S into main, resolving R to B's content.
4. The merge is TREESAME to parent S for R, so git log follows only S and prints just B. A disappears.
5. Result: `len(cs) == 1` (`protocol.py:142`), `_added_once` returns B, and the ordering checks pass for B (B is a
   descendant of the audit).

Consequences:
- The committed package hash can be swapped after a first run. This is usable because the runner has no once-only
  guard; see S2.
- An audit record can be replaced by one that binds new code hashes (re-blessing modified code without the auditor;
  combine with S1).
- The result seal can be pointed at a different run.

The selftest's `commitment_rewritten` only covers a linear second commit (`selftest_protocol.py:169-170`).

**Fix:**
- Use `git log --full-history` (lists A and B, so `len == 2` and it is refused).
- Also reject any merge commit whose version of R differs from either parent.
- Or pin each record's commit id in the next record: for example, the commitment record names the audit commit, and
  the designation names both.

### S1 (should-fix): records are unauthenticated

- `protocol.py:8` says the audit is "written by the independent auditor", but only `format`, `spec_id`, `verdict`
  and the code hashes are checked (`protocol.py:211-224`). `auditor` is only copied (`:225`).
- There is no signature and no committer check. In this repository the commits of different seats share one git
  identity (for example, Cosmos's commit `940b486f2` has author "James Craig").
- Anyone who can push to main (Cosmos must, for record 3: `FIREWALL.md:94`) can commit a PASS
  `FIREWALL_AUDIT.json` binding the current `--code-hashes` output before Odysseus does. It then becomes immutable.
- Symmetrically, a junk record permanently blocks a stage.
- Fix: signed records (ssh/gpg commit signatures checked with `git verify-commit` against a pinned key per role), or
  at minimum a hash-bound allow-list of record committers.

### S5 (should-fix): the seal, spec_id and reference freshness are not pinned

- The SEAL gate accepts any self-consistent manifest and ciphertext pair (`protocol.py:192-204`). The public anchors
  (`95b31a30d`, `spec_id e2d3…`) are not constants in the audited code.
- `origin/main` is a local remote-tracking ref (`protocol.py:45`), and it is never fetched or compared to the remote.
- `--ref` and `--gate-ref` are free CLI arguments (`custody.py:185`, `runner.py:717`, `evidence.py:91`).
- Against the key holder this is declared. Against a force-push rewriting origin's history it depends on branch
  protection, which is **CANNOT-VERIFY** from the repository (ask the operator for the GitHub branch-protection
  setting on main).
- Fix: pin `SEAL_COMMIT` and `SPEC_ID` in `protocol.py`.
- The brief's audit record has an `audited_commit` field, which `check_gates` ignores. Checking that the committed
  code hashes equal the hashes at `audited_commit` would also help.

### N2 (note): source vs bytecode

- The working-tree check hashes `.py` sources (`protocol.py:157-163`). A crafted `__pycache__/*.pyc` with matching
  mtime and size executes other code. This needs local write access on M1 (key-holder class).
- numpy, scipy and cryptography from the environment are not bound at all (runner records only the numpy and python
  versions: `runner.py:504`).

**Verdict: BROKEN** (F1, F2 block PASS; S1 and S5 are should-fix).

---

## Claim 4: Controlled reveal

Attacks tried: (a) get the key without designation; (b) reveal or bundle before the result seal; (c) seal or reveal
a tampered run; (d) run on M2; (e) choose among runs.

**What holds:**
- `release_key`:
  - checks the destination (`custody.py:105`);
  - checks the gates through DESIGNATION with runner_id and host (`:106`, `protocol.py:249-259`);
  - enforces once per spec_id (`:107-108`);
  - reads the key only after all of that (`:109`).
- `reveal` requires the RESULT_SEAL gate (`custody.py:153`), a matching chain head and result hash (`:154-158`), and
  once-only (`:159-160`).
- `evidence.build` requires the RESULT_SEAL gate, a fully verified chain ending at the sealed head, and the result
  hash (`evidence.py:54-59`).
- `result_seal_record` verifies the chain, the close record, the committed package and the spec (`custody.py:125-137`).
- The only public output before reveal is hashes (`custody.py:140-144`). **Holds in its own logic.** But every one of
  these steps trusts `check_gates`, so F1 and F2 carry through.

**S2 (should-fix): run multiplicity and cherry-picking.**
- The runner has no once-only guard. With the released key file it can be run any number of times into fresh `--out`
  directories (`runner.py:729`), with different `--predict-timeout`, `--max-episode-steps` and `--allow-flagged`
  (`runner.py:712-717`).
- None of these parameters is fixed in a public record before the run.
- The custodian then picks which closed run to result-seal.
- The "post the predictions-sealed head before certifying" step is advice only (`FIREWALL.md:61-62`,
  `runner.py:25`): no gate requires it.
- Fix:
  - bind the run parameters in `RUNNER_DESIGNATION.json`;
  - make the runner refuse a second `open` for a spec_id (custody log);
  - require the predictions-seal head to be committed before `--phase certify`.

**S3 (should-fix): key release is not required by the runner.**
- The runner accepts any key path (`runner.py:459`), including the secrets-directory original. The still-published
  "original flow" instructs exactly that (`FIREWALL.md:60-61`).
- `runner_id` is a free string compared to the record (`protocol.py:258`).
- So "key release only to the designated runner" is a label, not a control. This is key-holder class, but it should
  be stated as such or enforced: the runner could refuse a key path inside `SECRETS_DIR` and require a matching
  `KEY_RELEASED` event.

**Notes:**
- `reveal` checks only the last receipt hash and does not re-verify the chain (`custody.py:154-156`). `evidence`
  does re-verify it.
- The released key copy is never destroyed.
- The world_tag HMAC reuses the AES key (`runner.py:467`): acceptable, but key separation is cleaner.
- The host checks use `socket.gethostname()` (`protocol.py:253`, `custody.py:71`) and are spoofable by renaming the
  machine. This is harmless against Cosmos because M2 never holds the secrets, but it is not an authentication.

**Verdict: HOLDS** (conditional on fixing F1 and F2), with S2 and S3 should-fix.

---

## Claim 5: Predictor isolation: **BROKEN** in substance

Attacks tried: (a) inject code into the runner through the pipe; (b) use the error channel as an oracle; (c) read
secrets from inside the child; (d) evade the AST audit.

**What holds:**
- There is a separate spawned process (`runner.py:509-514`), and its arguments are only the pipe, the package
  directory and the entry (`:512`).
- Both directions use JSON plus `np.load(allow_pickle=False)` (`runner.py:143-176`). The child cannot inject pickles
  into the parent, and object arrays are refused (`:145-146`).
- Error replies are the type name only (`runner.py:579-580`).
- The key and plaintext are deleted from the parent's locals before any prediction (`runner.py:469`).
- The child receives V and k by contract (`runner.py:563`).

### F3 (blocks-PASS): the committed package can read the plaintext (worlds and hidden run seeds) and the key from disk with zero audit flags

- The child runs as the same OS account, with the same environment and working directory.
- Under multiprocessing spawn, the child's `sys.argv` is the parent's, which includes `--key <path>`.
- The plaintext path is hard-coded and public (`custody.py:39-40`, `draw.py:41-43`).
- The AST audit (`runner.py:307-334`) is evadable without a single flag:
  - It only flags calls whose function is a bare `ast.Name` (`runner.py:327`). Attribute calls such as
    `np.fromfile("C:/Users/jcrai/nestor_secrets/holdout_D2/hidden_D2.plain.json", dtype=np.uint8)`, `np.loadtxt`,
    `np.genfromtxt` or `np.memmap` pass. numpy is allowed, and numpy's text loaders also accept URLs, which gives an
    exfiltration channel.
  - It audits only `*.py` members (`runner.py:374-376`), but the package directory is put first on `sys.path`
    (`runner.py:224`). An `import helper` that resolves to a shipped `helper.pyc` (sourceless import) or
    `helper.pyd` runs arbitrary native or bytecode code that was never audited.
  - The path string can be built dynamically, so reading the source (the declared mitigation) does not reliably
    reveal it.

**Scenario:**
1. Cosmos commits a package whose `predict()` reads the plaintext and looks up world i.
2. It has the knob values and the exact hidden run seed, so it can run the allowed `prometheus.cosmos.c3.certify`
   (`runner.py:100`) on a local system with that seed, or simply emit the right classes.
3. The prediction receipts record a perfect score.
4. The runner docstring's claim "a SEPARATE process that never holds the key, plaintext or knob values"
   (`runner.py:19-21`, `FIREWALL.md:40-42`) does not hold against the one party whose code runs there.

This is a stronger form of declared residual risk 2 (see below). The declared mitigation is optional
(`FIREWALL.md:51-53`: "A stronger option (Nestor's call)").

**Fix (needed for PASS):**
- Make the low-privilege execution mandatory and checked: the child runs under a separate account, and the secrets
  directory, the release destination and the receipts directory are ACL-denied to it.
- At start-up, the runner spawns the child and asserts that it cannot open the key path or the plaintext path.
- Clear `sys.argv` and the environment in the child.
- Refuse any non-`.py`, non-`package.json` member (or any `.pyc`, `.pyd`, `.so`, `.pth`) in the zip.
- Flag `ast.Attribute` calls to numpy I/O.

**Verdict: BROKEN** (F3, blocks-PASS). The narrow sub-claims (no key in child memory, pickle-free pipe, type-name
errors) hold.

---

## Claim 6: Draw integrity

Attacks tried: (a) weak or predictable nonce; (b) non-uniform draw or a biased rejection; (c) non-reproducible
redraw; (d) draw code changed after the draw.

- **CSPRNG:** `secrets.token_hex(32)` (`draw.py:154`). The rng is seeded with `int(nonce,16) mod 2^128`
  (`draw.py:63`), which gives 128 bits of entropy: fine. **Holds.**
- **Uniform:** per-knob uniform with rejection on the geometric constraint (`medium.py:228-236`) is uniform over valid
  lattice points. Rejecting the exposed-D set (`draw.py:65-70`) keeps it uniform over the remainder.
  - The canonical comparison normalises types through `world_from_dict(...).as_dict()` on both sides
    (`draw.py:59`, `66-67`).
  - Duplicates *within* D2 are not rejected. That is consistent with the stated rule (`MANIFEST_D2.json:16`).
  - **Holds.**
- **Reproducible:** `verify_reveal.verify(..., redraw=True)` re-derives the worlds, seeds and rejected count from the
  plaintext nonce (`verify_reveal.py:54-58`). `evidence` uses it (`evidence.py:73-77`). **Holds** in code.
  - Note: the redraw reads `sealed_spec_D.json` from the current tree (`draw.py:57-59`), and `verify_reveal` does not
    check `predecessor_sealed_spec_sha256` (`MANIFEST_D2.json:30`). Add that check.
- **Code unchanged since the draw:**
  - `git log` shows `draw.py`, `sealbox.py` and `__init__.py` in the D2 package touched only by `95b31a30d` (commit
    `06f53ae24` does not list them).
  - `prometheus/cosmos/c3_holdout_D` (including `medium.py`) was last touched by `a56ef7787` on origin/main.
  - The AAD binds the medium hash, and the runner checks it (`runner.py:456-460`).
  - **CANNOT-VERIFY here** that sha256-LF of the committed `draw.py`, `sealbox.py` and `__init__.py` equals
    `MANIFEST_D2.json:12-14`, that `medium.py` equals `:21`, or the brief's ciphertext, manifest and spec hashes:
    hashing was not available in this sandbox.
  - To settle it, anyone can run `sha256` over `git show 95b31a30d:<file>` with CRLF→LF and compare. The fabric's
    selftest checks `real_*` (`SELFTEST_D2.json:10-13`), which covers the manifest, ciphertext and medium hashes but
    not the at-draw source hashes.
  - The ciphertext size in git (17227 bytes, per `git log --stat`) matches `MANIFEST_D2.json:5`.
- **Single draw / nonce grinding:** the custodian could have drawn many times and kept one. This is declared (R3) and
  not detectable.

**Verdict: HOLDS** (at-draw hash equality is CANNOT-VERIFY here; single-draw provenance is declared).

---

## Declared residual risks

**R1: the gates are not a boundary against the key holder.**
- Acceptable as declared, but **incomplete**. "Key holder" in practice means *any code executed as the operator
  account on M1*.
- That includes Cosmos-authored repository code imported by every D2 tool (F1). The boundary against Cosmos
  ("custody", `FIREWALL.md:105-109`) therefore holds only if no Cosmos-authored code that the audit has not bound
  runs on M1.
- This must be declared and mitigated (bind the import closure; pin and inspect before any `git pull` on M1).

**R2: the prediction package runs as the operator; the AST audit is a heuristic.**
- **Not acceptable as declared.**
- The mitigation is optional, "read the source" does not cover `.pyc`/`.pyd` members or dynamically built paths, and
  the secret the package needs sits at a public, fixed path with the hidden run seeds (F3).
- Make the low-privilege account mandatory and checked by the runner.

**R3: single-draw provenance is a custodian statement.** Acceptable as declared. Optional hardening for future
seals: derive the nonce from a pre-committed value combined with a public randomness beacon after the commitment.

**R4: the System interface exposes the world's physics.**
- Acceptable (contract design, `FIREWALL.md:46-47`).
- Note that packages may import `prometheus.cosmos.c3.certify` (`runner.py:100`) and run the reference certificate
  through the stub (declared at `FIREWALL.md:54-55`).

**Missing from the list:**
- M-a: unbound import closure and module shadowing (F1).
- M-b: record swap through history simplification (F2).
- M-c: unauthenticated records, where any main pusher can pre-empt or poison a stage (S1).
- M-d: unlimited runner invocations and unbound run parameters, which allow cherry-picking the sealed run (S2).
- M-e: the runner accepts the secrets-directory key directly (S3).
- M-f: the leak scan covers two refs only (S4).
- M-g: the seal, spec_id and remote freshness are unpinned, and branch protection is unknown (S5).
- M-h: plaintext length is public (N1).
- M-i: third-party libraries and bytecode are unbound (N2).

---

## Findings index

| id | severity | claim | one line |
|---|---|---|---|
| F1 | **blocks-PASS** | 3 (also 1, 5) | `AUDITED_FILES` omits `c3/probe.py` and the parent `__init__`s, and `X/__init__.py` (for example `protocol/__init__.py`) shadows audited modules. Unaudited Cosmos-authored code runs in key-holding processes and decides certify results |
| F2 | **blocks-PASS** | 3 | `git log ref -- path` history simplification hides one side of a merge, so a record can be swapped while still showing "1 commit" |
| F3 | **blocks-PASS** | 5 (R2) | the package reads the plaintext, seeds and key from the public fixed path via numpy file I/O or a shipped `.pyc`/`.pyd`, with zero AST flags. Low-privilege execution is optional |
| S1 | should-fix | 3 | records are unsigned; auditor identity is not checked; anyone who can push to main can pre-empt or poison a stage |
| S2 | should-fix | 4 | runner has no once-only guard; run parameters are unbound; the custodian can pick among runs; the predictions-head post is not enforced |
| S3 | should-fix | 4 | runner does not require a custody-released key (the documented flow uses the secrets key); runner_id is a free string |
| S4 | should-fix | 2 | `firewall_check` greps only `HEAD`/`origin/main`, not all history; no base64 or raw forms |
| S5 | should-fix | 3 | seal commit and spec_id are not pinned in code; `origin/main` freshness is unchecked; force-push protection is CANNOT-VERIFY |
| N1 | note | 1 | `ciphertext_bytes` reveals the plaintext length, a noisy aggregate of long-form knob values (under about 1 bit) |
| N2 | note | 3 | `.pyc` caches and site-packages (numpy, scipy, cryptography) are not bound |
| N3 | note | 4 | reveal checks only the last receipt hash; the released key copy is never destroyed; HMAC reuses the AES key; the host check is not authentication |
| N4 | note | 6 | redraw does not verify `predecessor_sealed_spec_sha256` |

**Requests to Nestor (booleans):**
1. `firewall_check --git-ref $(git rev-list --all)` → all_clean.
2. Is the secrets directory synced by any cloud client?
3. Was the release-destination key deleted after the run?
4. Is GitHub branch protection (no force-push) on for main?
5. sha256-LF of `draw.py`, `sealbox.py` and `__init__.py` at `95b31a30d` equals `MANIFEST_D2.json:12-14`.
