# Holdout D2 firewall audit (v2) — adversarial findings

- **Auditor role:** independent adversarial security auditor (Odysseus lane), disposable worker.
- **Audited commit:** `f4cde414d74eb3cfa4a3cd50014b4c04ee1b2604` (working checkout, read-only).
- **Spec:** `e2d3213b02aae58b0b20bbd6b5a296545b6335078ae6a0a382ceaf346dc0d9fe`.
- **Scope:** coordinate/firewall layer only (custody, opacity, commitments, enforced order, leak behaviour).
  Cosmos's law and its scientific merit are out of scope and were not examined.

## Environment limits on this audit (read honestly)
This worker could run **no shell commands**: `git` and `python` were both denied. Therefore:
- Every claim that requires walking git history, recomputing a file sha256, or *re-running* the selftests is
  marked **CANNOT-VERIFY-FROM-REPO** below, with the exact command that would settle it. I reviewed the code
  paths that implement those checks and the *recorded* `SELFTEST_*.json` artifacts, but I did not regenerate
  them, and a recorded boolean is not a re-run.
- All source-level reasoning (control flow, gate logic, what is and is not published) was done by reading the
  files and is reported as HOLDS / BROKEN normally.

---

## Claim 1 — Opacity

**1a. Ciphertext AES-256-GCM, random 256-bit key, AAD bound to family source hash.**
- Attack: look for the key or a key-derivation seed reachable from public data. `sealbox.encrypt/decrypt`
  (`sealbox.py:70-80`) use `AESGCM(key)` with a 32-byte key from `secrets.token_bytes` (`sealbox.py:48-49`);
  AAD = `AAD_PREFIX + family_src_sha256` (`sealbox.py:60-61`). The key is generated in `draw.seal`
  (`draw.py:103`) and written only under `SECRETS_DIR` on M1 (`draw.py:109-111`). Nothing public carries it.
- Attack: forge/replay ciphertext under a different family. AAD binds to `family_src_sha256`; a wrong AAD
  raises `InvalidTag` on decrypt (`sealbox.py:76-80`). GCM tag prevents silent tampering.
- **Verdict: HOLDS.**

**1b. Commitment salted with 32 secret bytes → no brute-force confirmation of a candidate world.**
- Attack: brute-force the commitment over the lattice. `commitment = sha256(salt || plaintext_bytes)`
  (`sealbox.py:64-67`), salt 32 bytes, secret until reveal. Independently of the salt, the committed
  plaintext embeds the **256-bit secret nonce** (`draw.build_plaintext`, `draw.py:75-88`), so a brute-force
  over the small world lattice cannot reproduce the pre-image. Confirmation is infeasible.
- **Verdict: HOLDS.**

**1c. Nothing public carries world identities, knob values, seeds, nonce or distributional summaries.**
- `MANIFEST_D2.json`: family metadata, IV (public by design), ciphertext sha256/length, salted commitment,
  spec_id, versions, at-draw source hashes. No world, knob, seed or nonce. Reviewed field-by-field.
- `SELFTEST_D2.json` / `SELFTEST_PROTOCOL.json`: booleans / exception-type names only (reviewed).
- Receipts (`runner.py`): each world is named by index and `world_tag = HMAC-SHA256(key, canon([w,s]))`
  (`runner.py:532-533`); no knob value or run seed is written. `_summ` (`runner.py:454-459`) drops
  `r["system"]` (whose name encodes knobs) and keeps only P1/P2 statistics — and those receipts stay on M1
  and are **not** published before the result seal (see Claim 4). The public `RESULT_SEAL.json` carries only
  `chain_head`, `result_sha256`, `package_sha256`, `run_nonce` (`custody.py:148-151`; `protocol.py:404-409`).
- **One narrowing field (declared):** `MANIFEST_D2.json.ciphertext_bytes = 17227` reveals the plaintext
  length. See Finding N1. **Verdict: HOLDS** (length leak noted, already declared by Nestor).

---

## Claim 2 — Secrets never in git

- `draw.py` writes plaintext/salt/key only under `SECRETS_DIR` on M1 and refuses if that directory is inside
  a git repo (`draw.py:101-102`, `_write_excl` O_EXCL). `firewall_check.py` implements a key-holder leak scan
  (working trees + `git grep` of refs + `git log --all -S --no-textconv` over all history) that prints
  booleans/counts only and fails closed on a git error (`firewall_check.py:107-119`). The design is sound.
- Attacks I *could not run here* (git denied):
  - `git log --all --stat -- prometheus/cosmos/c3_holdout_D2` (no `*.plain.json` / `*.key*` / `*.salt*` ever).
  - `git grep`/`git log --all -S` for key/salt/nonce hex and each hidden world's canonical JSON.
  - Confirm `hidden_D2.enc` + `MANIFEST_D2.json` were added in exactly one commit `95b31a30d`.
- **Verdict: CANNOT-VERIFY-FROM-REPO.** Settled by running `firewall_check --all-history --scan <every
  checkout> --git-ref HEAD refs/remotes/origin/main` on M1 and by the two git commands above returning empty.
  The recorded provenance states the latest pass was clean; I could not reproduce it.

---

## Claim 3 — Enforced order (seal < audit PASS < commitment < designation < result seal)

**3a. Order is mechanically enforced.**
- `check_gates` (`protocol.py:289-413`) walks SEAL→AUDIT→COMMITMENT→DESIGNATION→RESULT_SEAL. Each record is
  loaded from the committed tree via `git show <ref>:<path>` (`_show`, `protocol.py:159-161`); `_added_once`
  uses `git log --full-history` and refuses a merge commit (`npar>1`) or more than one touching commit
  (`protocol.py:192-200`, F4). `_strict_ancestor` enforces strict precedence between stages
  (`protocol.py:188-189`, used at 328, 364, 384, 410). Seal commit and spec_id are pinned in code
  (`protocol.py:54-55`) and re-checked (`protocol.py:313-314`, S5).
- Ref is fully qualified; `resolve_ref` refuses short names and refuses if `refs/tags/origin/main`,
  `refs/heads/origin/main` or `refs/tags/main` exist (`protocol.py:164-174`, F3).
- `check_records_dir` refuses any file in `protocol/` other than the named records, in committed **and**
  working tree (`protocol.py:208-217`, the `protocol/__init__.py` shadow, F1-variant).
- **Verdict: HOLDS** for the mechanical ordering itself. I found no way to satisfy a later stage before an
  earlier one, to slip a record in via a merge, or to shadow `origin/main` with a tag.

**3b. The audit binds the executing code (stale-audit / loaded-closure).**
- `set(bound) != set(AUDITED_FILES)` is required (`protocol.py:340-341`); committed **and** worktree hashes
  must match the binding (`protocol.py:342-348`); with `verify_loaded=True` every loaded `prometheus.*`
  module must be in the binding and hash-match, with non-`.py`, no-file, and outside-repo modules reported
  and refused (`protocol.py:236-258`, `349-353`). `entry.py` re-checks committed+worktree by path before any
  prometheus import (`entry.py:84-94`). Class-1/3 bypasses (a `.pyc`, a package `__init__` shadow, a module
  outside the repo) are all caught. **Verdict: HOLDS.**

**3c. Records are authenticated (S1 allow-list).** — see **Finding F-COMMS (should-fix)**. The *ordering* is
enforced, but the allow-list that backs record *authenticity* trusts an unauthenticated comms sender field.

- **Overall Claim 3 verdict: HOLDS mechanically, with one should-fix on the authentication backing (F-COMMS).**

---

## Claim 4 — Controlled reveal (custody.py, evidence.py)

- Key release: `release_key` calls `_dest_ok` (dest not inside git, not inside secrets dir, host not M2) then
  `check_gates("DESIGNATION", runner_id=...)` — allow-list included — before reading the key, and refuses a
  second release per spec_id (`custody.py:108-124`). CLI requires `C3D2_ENTRY=verified` (`custody.py:202-204`).
- Results public as hashes only: `result_seal_record` writes only hashes/nonce (`custody.py:127-154`);
  RESULT.json/receipts stay on M1.
- Reveal only after the result seal: `reveal` requires `check_gates("RESULT_SEAL")`, re-verifies the whole
  chain, the close record, package/spec/nonce, and RESULT.json hash, refuses a second reveal, and only then
  copies plaintext/salt/key and runs `verify_reveal` (`custody.py:157-190`, S3). Evidence bundle refuses
  unless RESULT_SEAL passes and the chain ends at the sealed head (`evidence.py:47-61`).
- Attack: get the key on M2. `FORBIDDEN_HOSTS = {"SPECTREX5"}` blocks M2 in the designation host, the live
  host, and custody's `_dest_ok` (`protocol.py:51,380-389`; `custody.py:99-100`). Key is only ever written to
  a dir on the machine custody runs on (M1). **Verdict: HOLDS.**

---

## Claim 5 — Predictor isolation (runner.py)

- Separate `spawn` process holding no key/plaintext (`runner.py:575-589`); the child gets only the public
  `System` stub over a pipe.
- Pickle-free codec: JSON + `np.save/np.load(..., allow_pickle=False)` (`runner.py:160-193`); object arrays
  refused; a malicious `{"__nd__": ...}` cannot execute code.
- Error replies to the child carry exception **type names only** (`runner.py:653-655`).
- Isolation probe (F2): before importing any package code the child must fail to open the released key path,
  the three secret paths and the run receipts; anything not `denied`/`missing` (including a directory or any
  OSError) counts as readable → `ChildNotIsolated`, fail-closed (`runner.py:257-262, 581-589, 240-254`). The
  released key file is deleted right after it is read (`runner.py:523-524`, S5), before the child exists.
- AST audit heuristic refuses filesystem/process/network/introspection imports, forbidden builtins **and
  aliases/attributes** (`np.fromfile`, `read_text`, `[open][0]`, dunders) (`runner.py:348-379`); non-`.py/.json/.txt`
  members refused, no `.pyc` (`runner.py:110, 396-397`). The audit is explicitly a heuristic, not a sandbox
  (declared); the empirical probe is the real guard and it fails closed.
- **Verdict: HOLDS.** Note the declared residual: the child runs as the same OS account and could read that
  process's own memory; mitigated by the account-≠-custodian rule (but that name check is spoofable — Finding
  F-ACCT) and by the empirical file probe, which is not spoofable.

---

## Claim 6 — Draw integrity (draw.py)

- CSPRNG nonce: `secrets.token_hex(32)` (`draw.py:154`). **HOLDS.**
- Uniform over the unchanged public family lattice with rejection of exposed-D duplicates: worlds from
  `medium.draw_worlds` (per-knob uniform + geometric rejection, `medium.py:228-235`), plus rejection of any
  world equal to an exposed-D world (`draw.py:62-72`); every world asserted in-lattice (`draw.py:86-87`). The
  family source hash is bound in the AAD and manifest. **HOLDS** (family code unchanged is itself a
  git-history claim — see below).
- Reproducible from the nonce after reveal: `verify_reveal.verify(..., redraw=True)` re-derives worlds+seeds
  and compares, plus decrypt/commitment/canonical checks (`verify_reveal.py:31-60`; `evidence.py:73-80`).
  Logic **HOLDS**; I could not execute it (COSMOS_BROKER redraw needs python).
- `draw.py`/`sealbox.py` on main hash to the at-draw values in the manifest
  (`MANIFEST_D2.json.d2_src_sha256_at_draw`): **CANNOT-VERIFY-FROM-REPO** — settled by
  `python -m ...protocol --code-hashes` / an sha256-LF of the two files vs the manifest values
  (`sealbox.py` → `dec9b915…`, `draw.py` → `800e0b5d…`, `__init__.py` → `d38d3b0c…`). Not a firewall-opacity
  issue either way; it is provenance.
- `c3_holdout_D/` byte-identical to `a56ef7787`: **CANNOT-VERIFY-FROM-REPO** (`git diff a56ef7787 -- ...`).
- **Overall Claim 6 verdict: HOLDS in code; the hash-equality and history sub-points are CANNOT-VERIFY here.**

---

## Findings

### F-COMMS — S1 record authentication rests on an unauthenticated comms sender (should-fix)
- **Where:** `allowlist.py:38-65` (`comms_message` / `add`), backed by `comms/api.py:150-166` (`post`) and
  `comms/identity.py` (whole file).
- **What:** The S1 fix authenticates a governing record by requiring a comms message from the record's author
  (`SENDERS = {"AUDIT": {"Odysseus"}, ...}`, `allowlist.py:28`) that contains the record sha256. But the comms
  layer does not authenticate senders: `api.post(conn, sender, ...)` takes the seat name as a caller-supplied
  parameter (`comms/api.py:150,159-163`), and `split_sender` simply parses `"Seat[tag]"` from that string
  (`comms/api.py:55-62`). `comms/identity.py` proves only *which database* was reached (system_identifier),
  explicitly **not** who wrote a row ("No credential is read… here", and the motivating note that an
  attestation "is recorded on the row and never compared" — identity is about the store, not the author).
- **Failure scenario:** any party able to write to the comms bus posts a message with `--from Odysseus` whose
  body contains the sha256 of an attacker-authored `FIREWALL_AUDIT_n.json`. `allowlist.py add` accepts it
  (sender field says "Odysseus", body contains the sha), the record enters the allow-list, and `check_gates` /
  `entry.py` then treat that audit as governing. Combined with branch protection being **OFF** (declared
  residual) and a forged PASS audit that binds attacker-modified `AUDITED_FILES`, the audit gate can be made
  to pass on code the real auditor never saw.
- **Why should-fix, not blocks-PASS:** two human/host steps sit in the path that the repo cannot bypass — the
  custodian (Nestor) runs `allowlist.py` on M1 and separately decides to release the key, and the declared
  threat actor (Cosmos on M2) is not stated to hold comms-write-as-Odysseus. If Cosmos (or any untrusted
  party) *can* post to the bus as another seat, this rises to **blocks-PASS**; that ACL is outside the audited
  package and I could not verify it here.
- **Fix direction:** authenticate the author channel (signed record, or a per-seat comms secret), or have the
  custodian confirm the record hash over a channel whose sender identity is cryptographic, not a free field.

### F-ACCT — designated-account check uses spoofable `getpass.getuser()` (should-fix)
- **Where:** `runner.py:806` (`account = getpass.getuser()`), consumed at `protocol.py:382-383, 394-395`
  (must ≠ custodian; must == designation account).
- **What:** `getpass.getuser()` derives the name from `LOGNAME`/`USER`/`USERNAME` environment variables and is
  trivially spoofable by the process that launches the runner. So "the designated runner account must not be
  the custodian's" and "this OS account matches the designation" are advisory string checks, not a real
  privilege boundary.
- **Failure scenario:** the runner is launched on M1 while actually running under the custodian account, but
  with `USERNAME`/`LOGNAME` set to the designated non-custodian name. Both account checks pass.
- **Why not blocks-PASS:** the *empirical* isolation probe still runs as the real (custodian) account, so the
  child would then be able to open the secret paths → `ChildNotIsolated` → fail-closed (`runner.py:585-588`).
  The spoof therefore cannot actually expose secrets; it only defeats a defence-in-depth label. The FIREWALL.md
  residual sentence "so on M1 the secrets directory is unreadable to it" is enforced by the probe, not by the
  name check — the doc slightly over-credits the name check.
- **Fix direction:** derive the account from a non-environment source (OS token / SID), or state plainly that
  the probe, not the account name, is the boundary.

### N1 — plaintext length disclosed by `ciphertext_bytes` (note; already declared)
- **Where:** `MANIFEST_D2.json` `ciphertext_bytes: 17227`; also derivable from `sha256(hidden_D2.enc)`'s
  pre-image size. GCM adds a fixed 16-byte tag, so length ≈ plaintext length.
- **What:** reveals the size of the hidden set's canonical JSON. Nestor already declares this (FIREWALL.md v2
  residual: "a future seal should pad"). It narrows nothing beyond n_worlds (already public) in practice.
- **Severity: note.**

---

## Residual-risk assessment (declared list)

| Declared residual | Assessment |
|---|---|
| Gates are not a boundary against the key HOLDER on M1 | **Acceptable as declared.** Correct and unavoidable; the boundary against Cosmos is custody + the public order record, which holds. |
| Prediction package is Python; AST audit is a heuristic, not a sandbox | **Acceptable as declared**, and stronger than stated because the empirical isolation probe fails closed. Keep the "read the package first / low-priv account" guidance. |
| Single-draw provenance is a custodian statement, not cryptographic | **Acceptable as declared.** Genuinely unverifiable from the repo; correctly labelled. |
| System interface reveals physics by contract design | **Acceptable as declared** and out of scope. |
| Child can read its own process memory (same account) | **Acceptable as declared.** Interacts with F-ACCT: the name check that is meant to keep this account non-custodial is spoofable, but the file probe backstops the file-read path. |
| Branch protection on main is OFF | **Acceptable only jointly with a sound S1.** This is the amplifier for F-COMMS: with main writable and S1's author check spoofable, forged allow-listed records become the concern. Enabling branch protection, or hardening S1, closes it. |
| `ciphertext_bytes` length leak | Acceptable; see N1. |

**Missing from the declared list:** the two authentication weaknesses above (F-COMMS sender spoofing, F-ACCT
`getpass` spoofing) are not called out as residuals. Neither is a standalone mechanical bypass in the declared
threat model, but both should be listed so the custodian does not over-trust the S1 allow-list or the account
name.

---

## Summary of attacks that did NOT break a gate (sanity of the v2 repairs)
- Tag/branch shadowing of `origin/main` → refused (`resolve_ref`).
- Record introduced via a merge, or modified after recording → refused (`_added_once` + `--full-history`).
- `protocol/__init__.py` shadow (committed or worktree) → `RecordDirPolluted`.
- Unaudited/`.pyc`/outside-repo module loaded with the key → `UnboundCodeLoaded` / audit member refusal.
- Commitment before the governing audit; audit before seal; designation before commitment → order violations.
- M2 as designated host or live host → `ForbiddenHost`.
- A child that can open a secret path → `ChildNotIsolated`; key deleted after read.
None of these opened.
