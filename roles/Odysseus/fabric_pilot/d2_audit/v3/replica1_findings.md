# Holdout D2 firewall re-audit v3: adversarial findings

- Auditor: independent fabric worker (skill audit.security.adversarial v1), task tsk-d0454ab252b9 / att-c752d7f08d56
- Audited commit: `742243972e6e5b334d0f4787470c39897140cb02`. `rogit diff 742243972 refs/remotes/origin/main` shows no
  difference in `prometheus/cosmos/c3_holdout_D2`, `c3`, `c3_holdout_D` or the package `__init__` files, so the code
  audited here is the code on origin/main (`7c12fb175`).
- Method: static reading plus read-only git (`rogit`). **No code was executed.** The skill forbids it and the host
  denies it. Everything that needs execution (the selftests, `protocol` against the real history, sha256 values) is
  marked CANNOT-VERIFY, or I replicated the git query it depends on by hand.
- Scope: the firewall layer only (custody, opacity, commitments, enforced order, leak behaviour). No science.

## Summary of verdicts

| # | claim | verdict |
|---|---|---|
| 1 | Opacity | HOLDS (declared length leak only) |
| 2 | Secrets never in git | HOLDS for the repo history; key-holder scan CANNOT-VERIFY |
| 3 | Enforced order | **BROKEN**: B1 import control is bypassable (the entry path loads unbound code); the entry path also deadlocks once KEY_RELEASED.json exists; S1 is still open (known) |
| 4 | Controlled reveal | HOLDS in gate logic; reveal and evidence are **unreachable through entry.py** (same deadlock) |
| 5 | Predictor isolation | HOLDS as stated (fails closed); network egress and the AST bypasses are should-fix |
| 6 | Draw integrity | HOLDS; exact sha256 of the at-draw hashes CANNOT-VERIFY (files unchanged since the seal commit) |
| B1 | "entry path cannot load unbound code" (v3) | **BROKEN** (two independent vectors) |
| DEF-HARM-D2-001 | SEAL gate passes on the real history | HOLDS (git query replicated by hand; not executed) |

Blocks-PASS findings: **P1**, **P2**, **P3**, plus the known-open **S1**.

---

## Blocks-PASS findings

### P1: entry.py stage 1 imports stdlib modules from the package directory before any verification (B1 bypass)
- Evidence:
  - Documented usage is `python <repo>/prometheus/cosmos/c3_holdout_D2/entry.py ...`, run by path and not isolated
    (`entry.py:3`).
  - With a plain `python script.py`, CPython puts the script directory (`prometheus/cosmos/c3_holdout_D2/`) at
    `sys.path[0]`.
  - Before anything is checked, entry.py runs `import hashlib, json, os, re, site, subprocess, sys` and
    `from pathlib import Path` (`entry.py:17-24`), then `import importlib.machinery` (`entry.py:77`).
  - Only after that does it re-execute itself under `-I -B` (`entry.py:145-150`).
  - Modules that are not preloaded at interpreter start-up (`json`, `hashlib`, `subprocess`, `pathlib`, ...) are
    therefore resolved from the package directory first.
  - Nothing restricts which files may exist in `c3_holdout_D2/`. Only `protocol/` is checked (`entry.py:104-111`,
    `protocol.py:231-240`), and `AUDITED_FILES` binds named files but never refuses extra ones (`protocol.py:73-81`).
- Scenario:
  1. Any committer to main (main is unprotected, FIREWALL.md:147,176; Cosmos is expected to commit to main,
     FIREWALL.md:94) adds `prometheus/cosmos/c3_holdout_D2/json.py`. Its body loads the real `json` via importlib,
     then reads `C:/Users/jcrai/nestor_secrets/holdout_D2/hidden_D2.key.hex` and pushes it to a branch.
  2. Nestor pulls main and runs `python .../entry.py custody release-key ...` (or `runner`) as documented.
  3. The planted code runs as the custodian account before `verify()` is reached. The key, the salt and the plaintext
     leak to Cosmos.
  4. The same file also shadows `json` for `allowlist.py`, which is likewise run by path (`allowlist.py:3`).
- Severity: **blocks-PASS**. This directly defeats FIREWALL.md v3 B1 ("run by file path (stdlib only) ... before
  importing any prometheus module").
- Fix direction:
  - Make stage 1 import nothing except builtins/frozen modules before re-exec. For example, `sys.path.pop(0)` as the
    first statement, before any import, or require `python -I -B` and refuse otherwise without importing anything.
  - Refuse unexpected `*.py` files and `__pycache__` in `c3_holdout_D2/`.

### P2: in the key-holding process, the repo root is first on sys.path and the guard only covers `prometheus.*` (B1 bypass)
- Evidence:
  - `sys.path[:] = [str(REPO)] + [interpreter paths]` (`entry.py:162`).
  - `AuditedImportGuard.find_spec` returns `None` for every non-`prometheus` name (`entry.py:60-61`), so those names
    fall through to the normal PathFinder, which searches REPO first.
  - The loaded-closure check also looks only at `prometheus.*` modules (`protocol.py:264-266`).
  - After the switch, the key-holding modules import many stdlib and third-party modules that were not yet loaded:
    - runner: `from __future__ import annotations`, `argparse`, `ast`, `base64`, `datetime`, `hmac`, `zipfile`,
      `multiprocessing`, `socket`, `numpy` (`runner.py:47-70`);
    - custody: `argparse`, `datetime`, `socket` (`custody.py:29-33`);
    - through the audited modules: `scipy` (`c3/probe.py:11`) and `cryptography` (`sealbox.py:17`).
  - `__future__` is not frozen, so the first `from __future__ import annotations` triggers a PathFinder lookup that
    finds `<REPO>/__future__.py`.
- Scenario:
  1. A committer adds a repo-root `__future__.py` (or `numpy.py`, `argparse.py`, or `scipy/__init__.py`) that
     re-exports the real module and also copies the key.
  2. Nestor runs `entry.py runner|custody` exactly as intended. `verify()` passes, because it checks only the bound
     files, and the guard is installed.
  3. Importing `runner` or `custody` executes the root file inside the verified, key-holding process. An untracked file
     in the M1 working tree works the same way.
  4. Right now the repo root has no `*.py` files and no packages with colliding names (Glob of `*/__init__.py`), so this
     is not exploited today. It is open to the next commit.
- Severity: **blocks-PASS** (B1 is the v3 repair under test).
- Fix direction:
  - Do not put REPO on `sys.path`. Serve `prometheus` only through the meta-path guard, for example by resolving
    `prometheus` from an explicit path inside the guard.
  - Or make the guard refuse any top-level module whose origin is inside REPO.
  - Extend `loaded_closure` to report every module whose file is inside REPO.

### P3: entry.py rejects the protocol's own once-only records, so the protocol deadlocks after key release
- Evidence:
  - `entry.FIXED = {"PREDICTION_COMMITMENT.json", "RUNNER_DESIGNATION.json", "RESULT_SEAL.json"}` (`entry.py:33`).
  - protocol.py allows `KEY_RELEASED.json` and `REVEALED.json` as well (`protocol.py:63-65`).
  - `release_key` writes `protocol/KEY_RELEASED.json` into the working tree "for the custodian to COMMIT immediately"
    (`custody.py:126,129-136`).
  - entry.py refuses any name outside FIXED or the audit pattern, whether committed or in the working tree
    (`entry.py:104-111`).
- Scenario:
  1. Step 5 (release) succeeds, and KEY_RELEASED.json is committed as instructed.
  2. Step 6 `entry.py runner ...` fails with `REFUSED: unexpected files ... KEY_RELEASED.json`. This happens at once if
     the runner shares the working tree.
  3. Step 8 `entry.py custody reveal` and step 9 `entry.py evidence` are refused the same way.
  4. The only ways forward are to not commit the record (which gives up the v3 "once-only via git" repair) or to bypass
     entry.py (which gives up B1).
- Why the selftest missed it: it never runs entry.py past "no audit" (`selftest_protocol.py:323-338`), and its
  end-to-end path calls `FirewallRun` and `Custody` directly (`selftest_protocol.py:341-419`).
- Severity: **blocks-PASS**. The protocol cannot be completed as specified; this is the same class as
  DEF-HARM-D2-001. Fixing it changes `entry.py`, which is in AUDITED_FILES, so a new audit is needed anyway.
- Fix: derive entry's allowed set from the same constant as `protocol.FIXED_RECORDS`, and add an end-to-end test that
  runs through entry.py.

### S1 (known open, #925): records are not authenticated
- The allow-list trusts the client-supplied comms `sender` (`allowlist.py:30-32,66`).
- The allow-list file is a plain JSON file writable by any process running as the custodian account
  (`allowlist.py:73-74`).
- Main is unprotected.
- Unchanged, and still blocks PASS per the brief.

---

## Claim-by-claim

### Claim 1: Opacity. HOLDS
Attacks tried:
1. **Cipher and nonce reuse.**
   - Key, IV and salt come from `secrets.token_bytes` (`sealbox.py:48-57`), used via `draw.seal` defaults
     (`draw.py:103-105`).
   - AES-GCM with AAD = prefix plus the family hash (`sealbox.py:60-80`). The IV is used once.
   - Holds.
2. **Brute-force the commitment against the lattice.**
   - The commitment is sha256(32-byte secret salt ‖ plaintext) (`sealbox.py:64-67`), so candidates cannot be confirmed.
   - Holds.
3. **Public fields that narrow the hidden content.**
   - Manifest fields (`MANIFEST_D2.json:1-36`) carry no knob, seed or nonce.
   - `ciphertext_bytes: 17227` gives the plaintext length (17211 B) and so a few bits about digit counts of
     seeds and knobs (declared, FIREWALL.md:149-150,178).
   - The `d2_src_sha256_at_draw`, `draw_utc` and version fields are public anyway.
   - `SELFTEST_D2.json` and `SELFTEST_PROTOCOL.json` hold booleans, gate outcome names and closure paths only.
   - PROVENANCE_D2.md has no counts or summaries (the rejected-duplicate count is only in the plaintext,
     `draw.py:83`).
4. **Receipts and posted hashes.**
   - Receipts carry an index, `world_tag` = HMAC(key, ...) (`runner.py:568-569`) and certify summaries without
     `system` (`runner.py:485-490`).
   - The publicly posted chain head, `RESULT_SEAL.result_sha256` and `n_receipts` (always 259) cannot be brute-forced,
     because every record includes the secret-keyed tags.
   - Error replies to the child are type names only (`runner.py:690-691`).
   - Note: receipts, which stay private until the result seal, contain `INVALID_AT_WORLD`/`noop` per world and
     arbitrary predictor-chosen JSON (`runner.py:468-481,767-778`). The evidence bundle made after the result seal
     (`evidence.py:68-69`) therefore carries per-world information before the reveal. Acceptable because the set is
     single-use, but say so.

### Claim 2: Secrets never in git. HOLDS (repo side); CANNOT-VERIFY (key-holder side)
Attacks tried:
1. **Secret-named files anywhere in history.**
   - `rogit log --all --name-status -- *hidden_D2* *.key.hex *.salt.hex *.plain.json *nestor_secrets*` shows only
     `A hidden_D2.enc` in 95b31a30d.
   - `rogit log --all --stat -- prometheus/cosmos/c3_holdout_D2` shows no key, salt or plain file ever.
2. **Bare 64-hex files.**
   - `rogit log --all --diff-filter=A -G '^[0-9a-fA-F]{64}$' -- *.hex *.key *.salt *.txt *.secret *.bin` finds only
     11 unrelated hash-list files (Cosmos STORE_SHA256, evidence_wiki gold hashes, ...).
   - Shape alone cannot rule them out; only the key-holder scan can.
3. **Quality of the key-holder scan** (`firewall_check.py`):
   - `all_clean` does not require `--all-history` (`firewall_check.py:156`).
   - `history_scan` does not search run seeds (`firewall_check.py:101-125`).
   - Only the hex, lower-cased form of the key and salt is searched (no raw bytes or base64).
   - comms, which Cosmos can read, is not scanned at all.
   - The "latest pass all clean" result is a custodian statement: CANNOT-VERIFY. Settle it by re-running
     `firewall_check --all-history --scan <all checkouts>` and publishing the booleans.
   - Note that running it is itself exposed to finding **F-KH** below.

### Claim 3: Enforced order. BROKEN (P1, P2, P3; S1 known)
What holds:
- **Gate before key.**
  - `FirewallRun.open` calls `check_gates` (`runner.py:537-540`) before reading the key (`runner.py:558`).
  - `release_key` gates (`custody.py:112`) before reading the key (`custody.py:117`).
  - Holds.
- **Ref ambiguity (F3).**
  - Only a `refs/...` ref is accepted, and shadowing tags or branches are refused (`protocol.py:166-176`,
    `entry.py:98-103`). Fetch uses `--no-tags` (`entry.py:97`).
  - I found no other shadow of a fully qualified ref, because rev-parse rule 1 (`$GIT_DIR/<refname>`) wins.
  - Holds.
- **History simplification (F4) and DEF-HARM-D2-001.**
  - `_record_history` uses `--full-history -m --raw` (`protocol.py:182`).
  - `_added_once` requires one blob, exactly one non-merge add, no D/R/M/T, and the blob at the ref
    (`protocol.py:206-223`).
  - Replicated by hand:
    `rogit log --full-history -m --raw --no-abbrev --format="C %H %P" refs/remotes/origin/main -- hidden_D2.enc MANIFEST_D2.json`.
    It shows a single blob per file (`10c7b600…` for enc, `db3d442d…` for the manifest) and one non-merge `A` in
    `95b31a30d06d…`, which equals the pinned `SEAL_COMMIT` (`protocol.py:54`).
  - The other entries are merges e5b95744f, 85b198a5b and ebe1307ea, each adding the same blob against one parent.
    So SEAL passes on the real history.
  - Not executed; the spec_id and ciphertext sha256 recomputation (`protocol.py:345`) is CANNOT-VERIFY here.
  - Other attacks all fail closed: an evil merge that introduces a record (0 non-merge adds leads to
    `RecordRewritten`), a mode change, and a replacement through a merge.
  - Holds.
- **Code binding.**
  - `set(bound) == AUDITED_FILES` and the committed-tree plus working-tree hashes are checked
    (`protocol.py:380-389`). The prometheus closure matches (`SELFTEST_PROTOCOL.json:73-78`; imports checked by hand:
    `c3/certify.py:15-17`, `system.py:20`, `probe.py:11`, `c3_holdout_D/medium.py:46-47`).
  - CRLF→LF normalisation cannot hide a semantic change, because Python's tokenizer normalises newlines.
  - Holds for `prometheus.*` only (see P2).

What breaks:
- **P1, P2**: unbound code runs in the entry and key-holding processes.
- **P3**: the entry path deadlocks after key release.
- **S1**: known open.

Should-fix and note items for this claim:
- **F-GOV (should-fix):** entry.py picks the governing audit as the highest `n` among committed and working-tree
  names, before any allow-list filter (`entry.py:112-127`). protocol.py considers only allow-listed audits
  (`protocol.py:360-365`).
  - Scenario: anyone commits an unauthenticated `FIREWALL_AUDIT_2.json` (PASS or FAIL). entry.py then refuses every
    target ("not in the custodian's allow-list"), so every key-holding CLI is DoSed.
  - This contradicts the v3 claim "an unauthenticated later FAIL/PASS is ignored", which is only true inside
    protocol.py. It fails closed, so no leak.
- **F-FETCH (should-fix):** the fetch return code is ignored (`entry.py:96-97`). An offline or blocked fetch silently
  verifies against a stale `origin/main`, where a later superseding FAIL audit would not be seen. S5 freshness is
  asserted but not enforced.
- **F-ONCE (note):**
  - `KEY_RELEASED.json` and `REVEALED.json` are only checked for presence (`protocol.py:306-309`), not with
    `_added_once`. A later commit deleting `KEY_RELEASED.json`, together with a cleared custody log (M1 access),
    re-enables a second release.
  - Anyone can pre-commit either file to DoS the release or reveal.
  - Two concurrent `release-key` calls to different `--dest` both pass the log and git checks (no lock).
- **F-GITENV (note):** git is run with the ambient environment and config. `refs/replace/*`, `info/grafts`, `GIT_DIR`
  and `GIT_REPLACE_REF_BASE` could present a forged history. All of these need access to the M1 account (key-holder
  level). `--no-replace-objects` would close it cheaply.

### Claim 4: Controlled reveal. HOLDS in logic; unreachable through entry (P3)
Attacks tried:
1. **Reveal or bundle before the result seal.**
   - Refused: `custody.py:174` and `evidence.py:55` use `through="RESULT_SEAL"`.
   - RESULT_SEAL must be allow-listed (`protocol.py:447`) and must follow the designation (`protocol.py:452`).
   - Reveal re-verifies the chain, the close record, the package, the spec, the nonce and the RESULT hash
     (`custody.py:176-185`).
   - Holds (subject to S1).
2. **Key release to M2 or a wrong runner.**
   - The host must equal the designation host and not SPECTREX5 (`protocol.py:421-432`, `custody.py:99-100`), and
     the runner id is checked (`protocol.py:433-434`).
   - **Note F-DEST:** `--dest` is constrained only to be outside git and outside the secrets directory
     (`custody.py:94-98`). A UNC path to `\\SPECTREX5\...`, a mapped drive or a OneDrive-synced folder is accepted,
     and the key file gets the default ACL (`custody.py:102-105`). "Never M2" for the key copy rests on the custodian
     typing a correct path. Refuse UNC or network drives and synced roots, and set an explicit ACL granting only the
     designated account.
3. **Result exposure before the seal.**
   - `result-seal` writes hashes only (`custody.py:160-164`).
   - RESULT.json and the receipts stay under the M1 out-root (`runner.py:83`).
   - Holds.
4. **evidence main has no `C3D2_ENTRY` check** (`evidence.py:88-101`). It holds no secrets unless `--revealed`, so this
   is a note.

### Claim 5: Predictor isolation. HOLDS as stated (fails closed)
Attacks tried:
1. **Pickle over the pipe.**
   - Child→parent traffic is `recv_bytes` + JSON + `np.load(allow_pickle=False)` (`runner.py:178-193`), and object
     arrays are refused on send (`runner.py:162-163`).
   - Holds.
   - Note: a crafted `.npy` header with a huge shape, or deeply nested JSON, can raise MemoryError/RecursionError,
     which `_predict_one` does not catch (`runner.py:681-685`). That crashes the runner and burns the one-shot
     designation. It is self-harm by the package, so a note only.
2. **Reading the key or secrets from the child.**
   - The key file is deleted before the child exists (`runner.py:559-560`, `runner.py:851`).
   - The probe opens the key, secret and receipts paths before package import (`runner.py:288-293,611-625`).
   - With the child spawned under the runner's own account (mp `spawn`, `runner.py:612-615`), the receipts
     write-probe always succeeds, so **every production run is refused with ChildNotIsolated**. That is declared and
     intentional (FIREWALL.md:170).
   - No code exists to start the child under another account, so the runner can never run at this commit. Any fix
     changes `runner.py` and needs a re-audit.
3. **Static-audit bypass (class 3), should-fix F-AST.**
   - `audit_source` never inspects the names in `from X import name` (`runner.py:389-398`); it only checks the module.
   - `from numpy import fromfile as ff`, `from codecs import open as o`, `from numpy import load` and
     `import fileinput; fileinput.input(p)` all pass unflagged. `codecs`, `fileinput`, `gzip`, `logging`, `xmlrpc`,
     `imaplib`, `poplib` and `telnetlib` are not in `FORBIDDEN_MODULES` (`runner.py:92-99`).
   - The claim "np.fromfile / aliasing flagged" (FIREWALL.md:133) is true only for the attribute form.
   - Declared a heuristic; the probe is the real gate.
4. **Network egress (class 3/6), should-fix F-NET, missing residual.**
   - Nothing blocks the child's network access. The probe tests files only, and `xmlrpc.client` or
     `logging.handlers.HTTPHandler` pass the AST audit.
   - Even with the separate child account, the frozen package can stream what it observes about each hidden world to
     Cosmos on M2 during the run, and can fetch logic that `package_sha256` does not bind. That breaks the premise
     that Cosmos's only channel is one frozen package (FIREWALL.md:33-34).
   - Mitigation: a firewall rule or AppContainer/low-integrity token for the child account, plus flagging
     network-capable modules.
5. **Error replies.**
   - Type names only (`runner.py:690-691`). Holds.
   - Note: type names and call timing are a small side channel, dominated by the declared "System interface reveals
     physics" residual.

### Claim 6: Draw integrity. HOLDS; hashes CANNOT-VERIFY
1. **CSPRNG.**
   - `secrets.token_hex(32)` (`draw.py:154`), then `default_rng(int(nonce,16) mod 2^128)` (`draw.py:63`), giving
     128-bit effective seed entropy. Holds.
2. **Uniform over the lattice with exposed-D rejection.**
   - Per-knob uniform with rejection on the geometric constraint (`c3_holdout_D/medium.py:228-235`), which is uniform
     over the feasible lattice.
   - Exposed-D worlds are rejected (`draw.py:65-70`).
   - Deterministic: `verify_reveal --redraw` compares worlds, seeds and the rejected count (`verify_reveal.py:54-58`).
   - Holds.
3. **Unchanged public family.**
   - `rogit diff --stat a56ef7787 refs/remotes/origin/main -- prometheus/cosmos/c3_holdout_D` is empty.
4. **At-draw hashes.**
   - `rogit diff --stat 95b31a30d refs/remotes/origin/main -- draw.py sealbox.py __init__.py MANIFEST_D2.json hidden_D2.enc`
     is empty, so the files are byte-identical to the seal commit.
   - Whether their sha256-LF equals `d2_src_sha256_at_draw` (`MANIFEST_D2.json:11-15`) requires hashing, so it is
     CANNOT-VERIFY here. `sha256sum` after CRLF→LF on the three files settles it.

---

## Additional findings (classes 1, 2 and 7)

- **F-KH (should-fix; the residual is under-declared): tools running as the key-holding account execute unbound code.**
  - `firewall_check` loads the plaintext, salt and key (`firewall_check.py:38-46`) but is started as
    `python -m ...firewall_check` (`firewall_check.py:3`, FIREWALL.md:77). That path is unguarded: cwd is on
    `sys.path`, the package `__init__` files load, and `__pycache__` is honoured.
  - A committed `prometheus/__pycache__/__init__.cpython-312.pyc` in unchecked-hash mode (PEP 552) is executed
    regardless of the source, while the process holds every secret.
  - `allowlist.py` runs as the custodian account, imports `comms.api` from the repo (`allowlist.py:42-44`) and has the
    script directory on its path. The v3 declaration "never runs in a key-holding process" (FIREWALL.md:172) is not a
    boundary: on M1 the secrets are protected by the account's ACL, not by the process.
  - Together with an unprotected main that Cosmos writes to, the "boundary against Cosmos = custody" depends on the
    custodian never running main-writable code as the operator account. The protocol's own tools, and the selftests
    (`python -m`, COSMOS_BROKER=1), do exactly that.
  - Fix: run firewall_check and allowlist through a verified entry as well, or from a separate verified read-only
    checkout. Declare the dependency explicitly.
- **F-CWD (should-fix; PLAUSIBLE, confirm on M1):**
  - `subprocess.run(["git", ...])` (`entry.py:43,97`; `protocol.py:158,162`) on Windows uses CreateProcess search
    order, which checks the parent's current directory before PATH.
  - A committed `git.exe` at the repo root would be executed by entry.py, before verification, if the custodian's cwd
    is the repo root.
  - Settle it by testing a harmless `git.exe` in cwd on M1. Fix by resolving git to an absolute path, or by setting
    `NoDefaultCurrentDirectoryInExePath`.
- **F-3P (note; missing residual):** numpy, scipy, cryptography and site-packages `.pth` files run unbound in the
  key-holding process (`entry.py:152-162` keeps interpreter paths). If Python is a per-user install on M1, those
  paths are writable by the custodian account (and by any `pip install`).
- **Class 7 (identity):**
  - The account comes from GetUserNameW/pwd (`runner.py:258-268`). Holds against environment spoofing.
  - Host is `socket.gethostname()`, which is self-reported. Acceptable, since only the M1 custodian ever acts.
  - `C3D2_ENTRY=verified` is an environment flag (`runner.py:837`, `custody.py:218`). A stale or pre-set value lets
    `python -m ...runner` run unguarded, for example with a planted pyc. Note: the flag only guards against mistakes.
- **Timing and TOCTOU (note):** `check_gates` re-resolves `ref` on every `git show` (`protocol.py:161-163`). A
  concurrent fetch can mix trees. Records are append-only, so the impact is low. Pin `ref_commit` once and use it.

## Declared residual risks: assessment
1. **Gates are no boundary against the key holder.** Acceptable as a statement, but **incomplete**. It must say that
   the key holder includes any code that the operator account runs from main, which Cosmos can write. As shown in
   P1, P2 and F-KH, the protocol's own tools run such code. Needs S1 plus branch protection plus a verified-checkout
   rule.
2. **Prediction package runs as Python; AST is a heuristic.** Acceptable only with the separate child account, which
   the code cannot currently use. Add the network-egress residual (F-NET).
3. **Single-draw provenance is a custodian statement.** Acceptable as declared.
4. **System interface exposes physics by design.** Acceptable, but only for the predictor. Exfiltration to M2
   (F-NET) is not covered by it.
5. **Plaintext length visible.** Acceptable (a few bits).
6. **Missing from the list:**
   - network egress of the child (F-NET);
   - third-party and site-packages code in the key process (F-3P);
   - `--dest` being any path, including UNC or synced folders (F-DEST);
   - the protocol being currently unrunnable end to end (P3 plus the child-account gap), which invites bypass;
   - comms as an unscanned leak channel (claim 2).

## Requested executions (not performed)
I did not run `COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.protocol` against the real history, or the
selftests: this worker may not execute code. The SEAL-gate git query was replicated with `rogit` (claim 3 above) and
passes. AUDIT is expected to fail with `AuditMissing`, because there is no `protocol/` directory on origin/main and no
allow-list on this host.

## Record
No `FIREWALL_AUDIT_1.json` is produced. The verdict is FAIL, and this worker is read-only; findings go to Nestor
(cc operator).

OVERALL: FAIL
