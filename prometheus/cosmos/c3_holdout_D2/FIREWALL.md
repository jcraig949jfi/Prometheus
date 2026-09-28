# Holdout D2 -- firewall

D2 is the opaque successor of holdout D. Holdout D's original hidden set (`prometheus/cosmos/c3_holdout_D/sealed_spec_D.json`)
is plaintext on main and is therefore EXPOSED: it must never be used as a blind set again. D2 draws a fresh set of
128 worlds + 128 run seeds from the SAME, UNCHANGED family code (`c3_holdout_D/medium.py`, sha256-LF
`09559e69...cde4`) with a new CSPRNG nonce, and publishes only ciphertext and commitments.

## What is public (in the repo, this directory)
| file | content |
|---|---|
| `MANIFEST_D2.json` | family/version, medium.py sha256, n_worlds, cipher, IV (public), sha256(ciphertext), salted commitment, versions, draw time, spec_id. No secret. |
| `hidden_D2.enc` | AES-256-GCM ciphertext+tag of the canonical plaintext bytes. Useless without the key. |
| `sealbox.py`, `draw.py`, `runner.py`, `verify_reveal.py`, `firewall_check.py`, `selftest_D2.py` | code only |
| `SELFTEST_D2.json` | booleans only (throwaway material; never the hidden set) |

Public commitments: `commitment = sha256(salt || plaintext_bytes)` (salt 32 random bytes) and, separately,
`ciphertext_sha256 = sha256(hidden_D2.enc)`. `spec_id = sha256(canonical manifest minus spec_id)`. The AES-GCM
AAD binds the ciphertext to the medium.py source hash.

## What is secret (never in any repo, never on M2, never sent to Cosmos)
| item | where | who can reach it |
|---|---|---|
| plaintext hidden set (worlds, run seeds, nonce) | host **M1 (SKULLPORT)**, a directory under the operator's Windows user profile that is outside every git repository (path class: `C:/Users/<operator>/nestor_secrets/holdout_D2/`) | the operator account on M1 (Nestor seats run as that account) |
| commitment salt (32 B) | same directory | same |
| AES-256 key (32 B) | same directory | same |
| runner receipts (default) | M1, `C:/Users/<operator>/nestor_receipts/holdout_D2/run_*` (outside git; results only, no knobs/seeds/key) | same; released by Nestor when the operator decides |

Decryption happens only inside `runner.py` / `verify_reveal.py` in memory on M1; nothing writes the plaintext
anywhere else. Reveal (after the evaluation is closed) = publishing plaintext + salt + key, checked with
`verify_reveal.py`.

## Threat model
- **Adversary**: Cosmos on M2 (and anything Cosmos can run), able to read everything on main, every pushed branch,
  and everything on M2. Cosmos's legitimate channel is one frozen, hashed prediction package handed to Nestor.
- **Assets**: world knobs, run seeds, nonce (which regenerates both), salt (would let a guessed plaintext be confirmed),
  key.
- **Defences**: (1) secrets live only on M1 outside git -> no push/pull/branch can carry them; (2) ciphertext is
  AES-256-GCM, key 256-bit random; (3) commitment is salted, so the lattice (~10^7 points per world) cannot be
  brute-forced against it; (4) receipts carry no knob, seed or key; worlds are named by index and
  `world_tag = HMAC-SHA256(key, world||seed)`, verifiable only after reveal; (5) the predictor runs in a separate
  process that never holds the key/plaintext, sees only the System interface over a pickle-free pipe (JSON +
  `.npy` with `allow_pickle=False`), and error replies carry exception type names only; (6) the runner refuses a
  package whose sha256 differs from the one Cosmos committed to, and cannot certify a world until every world has
  a recorded prediction and a seal record commits to them all (re-verified on disk before each certification).
- **Residual risks (declared)**:
  - The System interface itself reveals physics to the predictor (state shape reveals L and V; readout dim reveals
    w_patch*V; probing step() can estimate v, D, decay...). That is the contract's design (s3), not a leak.
  - The predictor is Python code running as the operator account on M1: a malicious package could read files
    (including the key directory). Mitigations: the package is frozen + hashed (so it can be read before running),
    and an AST audit refuses filesystem/process/network/introspection imports and calls; the audit is a heuristic,
    NOT a sandbox. **Nestor should read the package source before running it** and never use `--allow-flagged`
    without reading the flags. A stronger option (Nestor's call): run the package under a separate low-privilege
    Windows account with no read access to `nestor_secrets`.
  - A predictor with oracle access could run the reference certificate itself through the interface. Usage
    (calls, episode-steps) is recorded per world; `--max-episode-steps` caps it if the adjudication rules want that.
  - Anyone with the operator account on M1 can read the secrets.

## Execution across the firewall (original flow; the enforced order in the last section governs)
1. Cosmos posts `sha256(package.zip)` and hands over `package.zip` (format in `runner.py` docstring).
2. Nestor on M1: `COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.runner --package package.zip
   --package-sha256 <sha> --key <secrets>/hidden_D2.key.hex --phase predict` -> prints the chain head after all
   128 predictions are recorded and sealed. Post that head (it fixes every prediction) before certifying.
3. `... --phase certify --out <same run dir>` -> certify.py on each world + the package's intervention; RESULT.json
   and the chain head. `--verify-receipts <run>/receipts.jsonl` re-verifies the chain.

## Independent checker checklist
Anyone (no secrets needed):
- [ ] `sha256(hidden_D2.enc)` equals `MANIFEST_D2.json.ciphertext_sha256`; `spec_id` recomputes
      (`sealbox.manifest_spec_id`); `family_src_sha256` equals sha256-LF of `c3_holdout_D/medium.py` on main.
- [ ] `git log --all --stat -- prometheus/cosmos/c3_holdout_D2` shows no `*.plain.json`, `*.key*`, `*.salt*` file ever.
- [ ] `git grep -n -i -E "nestor_secrets|hidden_D2\.(key|salt|plain)" $(git rev-list --all)` returns only
      code/docs references to the file NAMES, never contents (key/salt files are 64 hex chars on one line).
- [ ] `c3_holdout_D/` is byte-identical to its sealed commit (`git diff a56ef7787 -- prometheus/cosmos/c3_holdout_D`
      shows nothing).
- [ ] `COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.selftest_D2` -> `selftest_pass: true`.
Key holder on M1 (prints booleans/counts only; never prints secrets):
- [ ] `python -m prometheus.cosmos.c3_holdout_D2.firewall_check --scan <every worktree/checkout> --git-ref HEAD origin/main`
      -> `all_clean: true` (searches for key/salt/nonce hex, every hidden world's canonical JSON, the plaintext's
      sha256 as a file hash, and clusters of hidden run seeds; also greps the committed trees of the refs).
- [ ] `git -C <secrets dir> rev-parse` fails (not a repo); `hostname` is SKULLPORT (M1), not M2.
- [ ] The secrets directory is not synced (OneDrive/Dropbox) and holds exactly the three files.
After reveal: `python -m prometheus.cosmos.c3_holdout_D2.verify_reveal --plaintext .. --salt .. --key ..` -> all true
(with `COSMOS_BROKER=1` it also re-derives every world and seed from the nonce).

## Enforced protocol order (added 2026-09-28, operator directive "COSMOS C3 SUCCESSOR-SEAL")
Code: `protocol.py` (gates), `custody.py` (key release, result seal, reveal), `evidence.py` (Harmonia bundle),
`selftest_protocol.py` (negative tests). Every record is a JSON file under `protocol/`, read from the COMMITTED tree
of `origin/main` (never the working tree), added in exactly one commit and never modified.

| step | record / action | who | refused unless |
|---|---|---|---|
| 1 seal | `MANIFEST_D2.json` + `hidden_D2.enc` (commit 95b31a30d) | Nestor | both verify (spec_id, ciphertext sha256), sealed in one commit |
| 2 firewall audit | `protocol/FIREWALL_AUDIT.json` `{format c3-D2-firewall-audit/1, verdict, auditor, spec_id, code_sha256}` | Odysseus | verdict PASS; commit strictly after the seal; `code_sha256` equals the committed AND the executing bytes of every file in `protocol.AUDITED_FILES` (any later code change = stale audit) |
| 3 Cosmos commits predictions | `protocol/PREDICTION_COMMITMENT.json` `{format c3-D2-prediction-commitment/1, committer, spec_id, package_sha256}` | Cosmos | commit strictly after the audit; the package run later must hash to exactly this value |
| 4 designation | `protocol/RUNNER_DESIGNATION.json` `{format c3-D2-runner-designation/1, runner_id, host, designated_by, spec_id}` | custodian | commit strictly after the audit; host is not M2 (SPECTREX5) |
| 5 key release | `custody.py release-key --runner-id ID --dest DIR` | Nestor | gates 1-4 pass for ID on this host; DIR outside git and outside the secrets dir; once per spec_id |
| 6 run | `runner.py ... --runner-id ID` | designated runner | gates 1-4 re-checked BEFORE the key file is read; manifest = the sealed one; then PREDICT -> SEAL predictions -> CERTIFY -> CLOSE (existing receipt chain) |
| 7 result seal | `custody.py result-seal` writes `protocol/RESULT_SEAL.json` `{spec_id, package_sha256, chain_head, result_sha256, ...}`; committed | Nestor | the run closed, its chain verifies, it used the committed package on the sealed set. Only hashes become public; RESULT.json and receipts stay on M1 outside git |
| 8 reveal | `custody.py reveal --run RUN --dest DIR` | Nestor | gate 5 (RESULT_SEAL) passes and the run on disk matches the sealed chain head and result hash; once; `verify_reveal` runs on the copies |
| 9 adjudication | `evidence.py --run RUN --out DIR [--revealed DIR]` | for Harmonia | as 8; bundle = protocol records, manifest, ciphertext, receipts, RESULT.json, gate status with every record's commit, receipt verification, reveal verification incl. redraw from the nonce, INDEX of sha256 |

Custody log: `C:/Users/<operator>/nestor_receipts/holdout_D2/custody.jsonl` (M1, outside git), every release,
seal, reveal and REFUSAL, public fields only.

What the gates are and are not: they make the ORDER mechanical and auditable for everyone who runs this code, and they
leave a public record of every step. They are not a security boundary against the key holder, since anyone with the
operator account on M1 can read the key file and decrypt with `sealbox` directly. The boundary against Cosmos is still
custody: the key, salt and plaintext exist only on M1, outside git, and nothing derived from them except hashes leaves
M1 before step 8.

Negative tests (`selftest_protocol.py`, `SELFTEST_PROTOCOL.json`): each must be refused with no side effect.
- Runner refusals, with a non-existent key path, so each refusal proves the gate fired before the key was touched:
  missing audit, failing audit, code changed after the audit (committed / working tree), commitment before the audit,
  commitment in the same commit as the audit, audit before the seal, missing commitment, commitment only in the
  working tree, commitment rewritten, wrong package, missing designation, wrong runner id, wrong host, M2 designated,
  running on M2, manifest swapped.
- Custody: key release before the audit, twice, into a git repo, or to the wrong runner; result seal of an unclosed
  run; reveal before the result seal, twice, or with RESULT.json tampered.
- Evidence: bundle before the result seal or with truncated receipts.
- A positive end-to-end path (release -> run -> result seal -> reveal -> bundle, verify_reveal incl. redraw all
  true).
- Injected-defect controls (ordering check removed, stale-code check removed, M2 block removed) each make the
  matching test fail.

## v2 (2026-09-28): repairs after Odysseus's firewall audit FAIL (roles/Odysseus/fabric_pilot/d2_audit/VERDICT.md)

Every blocking finding and every should-fix is repaired in code and has a refusal test in `selftest_protocol.py` (56
checks + 4 injected-defect controls, SELFTEST_PROTOCOL.json).

| finding | repair | tests |
|---|---|---|
| F1 audit binding misses code that runs with the key | `AUDITED_FILES` = the complete import closure of runner + custody + evidence (+ `entry.py`, `allowlist.py`), incl. `c3/probe.py` and the package `__init__` files; verified complete in a fresh process. The key-holding CLIs start ONLY through `entry.py`, run by file path (stdlib only), which verifies every bound file against the governing audit BEFORE importing any prometheus module; the gates re-check the loaded-module closure (`UnboundCodeLoaded`). `protocol/` may hold only the named record files. | closure complete / extra module detected; probe.py edit -> AuditStale; protocol/__init__.py (committed and working tree) -> RecordDirPolluted; unbound loaded code -> UnboundCodeLoaded; entry.py refuses the real repo (no audit); runner.main refuses without entry.py |
| F2 the predictor can read secrets; AST audit bypassable | package members only `.py/.json/.txt`; the AST audit flags forbidden attributes (np.fromfile, read_text, ...) and ANY reference to a forbidden builtin (aliasing); the runner deletes the released key right after reading it; before any package code is imported the child must FAIL to open the key path, every secret path and the run's receipts (isolation probe, fail closed). The designated runner account must not be the custodian's account (checked), so on M1 the secrets directory is unreadable to it. | .pyc member refused; fromfile / [open][0] flagged; a child that can read a secret path -> ChildNotIsolated; key deleted after read |
| F3 `origin/main` shadowed by a tag | only fully qualified refs (`refs/remotes/origin/main`); refuses if `refs/tags/origin/main`, `refs/heads/origin/main` or `refs/tags/main` exists; entry fetches with `--no-tags` | short ref -> AmbiguousRef; tag origin/main -> AmbiguousRef |
| F4 record replaced through a merge | `git log --full-history`; any merge commit touching a record path is refused | forged record merged from a side branch -> RecordRewritten; defect control (plain log) accepts it |
| S1 unauthenticated records | custodian allow-list on M1 (`allowlist.py`): a governing audit / commitment / designation counts only if its sha256 is listed, which requires a comms message from the record's author (Odysseus / Cosmos / operator or Nestor) containing that sha256 | missing from allow-list -> NotAllowListed; allowlist.add refuses a wrong sender or a message without the sha256 |
| S2 no re-audit path | versioned `FIREWALL_AUDIT_<n>.json`; the highest n governs; each added once, in increasing commit order; a later FAIL supersedes a PASS; the commitment must follow the GOVERNING audit | re-audit positive; later FAIL -> AuditNotPass; commitment before governing audit -> RecordOrderViolation |
| S3 thin reveal re-verification | reveal re-verifies the receipt chain, the close record, the package hash, the spec_id and the run nonce | truncated chain -> refused |
| S4 cherry-picked runs | the designation binds the runner OS account, the exact run parameters and a run nonce; the runner reads the parameters FROM the designation, writes only to `run_<nonce>`, refuses an existing run dir and refuses resume; the result seal carries the nonce | params differ / run dir not run_<nonce> / wrong account -> refused |
| S5 freshness and hygiene | seal commit and spec_id pinned in code; entry fetches before verifying; released key deleted after read; `firewall_check --all-history` searches every commit (`git log --all -S`) | key deleted after read |

Declared residuals (v2):
- A process running as the designated runner account can read that process's own memory; the child runs as the same
  account as the runner (the isolation probe proves it cannot read the key FILE, the secrets or the receipts, not that it
  cannot read the runner's memory). Mitigation: the runner holds the plaintext only in memory for the run; a stronger
  option is a low-integrity child token (not implemented).
- Branch protection on main is OFF (GitHub API 404). Its effect on D2 is contained by S1 (a rewritten history cannot
  produce allow-listed records) and the pinned seal; enabling it is the operator's decision.
- `ciphertext_bytes` in the manifest reveals the plaintext length (Odysseus claim 1 note); the current seal cannot change,
  a future seal should pad.
- Anyone with the custodian account on M1 can read the secrets (unchanged; "key holder" includes any repo code run by
  that account, which is why the key-holding CLIs verify code before importing it).
