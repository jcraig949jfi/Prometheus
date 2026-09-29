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

## v3 (2026-09-29): repairs after the v2 re-audit FAIL (roles/Odysseus/fabric_pilot/d2_audit/v2/VERDICT.md) and Harmonia DEF-HARM-D2-001

- **OPEN, the operator's decision (#925):** the root of trust for protocol records. The v2 decisive finding stands: the
  comms `sender` field is client-supplied, so the S1 allow-list does NOT authenticate authors, and main is unprotected.
  v3 does not claim S1 repaired.
- **Everything else is repaired in code** and has a refusal test in `selftest_protocol.py` (67 checks + 4 defect
  controls, SELFTEST_PROTOCOL.json).

| finding | v3 repair | test |
|---|---|---|
| DEF-HARM-D2-001: the SEAL gate is unpassable on the real history | "added once" = every commit in the full history (merges diffed against each parent) touching the record carries ONE blob; exactly one non-merge commit adds it; no non-merge modification, deletion or rename; the blob at the ref is that blob. A merge carrying the sealed blob unchanged passes; a replacement through a merge still fails (F4 kept). | SEAL passes on the REAL origin/main history; a side-branch seal merged into main passes; the F4 forgery through a merge is refused; the F4 defect control (plain log) still accepts it |
| B1: import control | entry.py re-executes itself with `python -I -B`, then installs a meta-path guard: every prometheus.* import must resolve inside the repo, be bound by the governing audit and be compiled by a loader from the SOURCE bytes it has just hashed. __pycache__ is never read, so a planted .pyc cannot load, and there is no check-then-read gap. | unbound module refused; changed source refused; verified source compiles |
| a later unauthenticated FAIL / PASS could supersede | only ALLOW-LISTED audit records are considered (the highest n governs); others are ignored and reported | an unauthenticated later FAIL is ignored; an unauthenticated later PASS is ignored |
| RESULT_SEAL not authenticated | RESULT_SEAL must be allow-listed (role RESULT_SEAL) | reveal refused until allow-listed |
| "once only" rests on an editable custody log | custody writes protocol/KEY_RELEASED.json and REVEALED.json for immediate commit; a committed record refuses a second release or reveal whatever the log says | second release refused from git after the custody log is cleared |
| secret-derived strings on the command line (firewall_check) | the all-history scan streams every reachable blob through `git cat-file --batch` over stdin and searches in-process; no secret appears in argv | (key-holder run) |
| the receipts can be written by the same-account child | the isolation probe also tries to APPEND to the run's receipts; the child must be denied. INTENTIONAL: with the child running as the runner's own account this always fails closed, so the designation must provide a separate child account (a host capability: MWO s6, no seat creates users) | a child that can append is refused |
| account from the environment | the OS account comes from GetUserNameW / pwd, not USERNAME | - |
| custodian tools import code outside AUDITED_FILES (allowlist.py -> comms) | declared: allowlist.py never runs in a key-holding process; comms stays outside the audited closure | - |

Residuals, restated:
- The S1 root of trust is open.
- Branch protection on main is off. That is the operator's setting.
- A same-account child could read the runner's memory; the separate child account (above) is required.
- The plaintext length is visible in the manifest (future seals should pad).

## v4 (2026-09-29): repairs after the v3 re-audit FAIL (roles/Odysseus/fabric_pilot/d2_audit/v3/VERDICT.md @ 2d7517600)

- **OPEN, the operator's decisions:**
  - the root of trust for protocol records (S1, #925);
  - branch protection on main.
  - v4 does not claim S1 repaired.
- **Every other blocking finding and should-fix is repaired in code.** Each repair has a test in `selftest_protocol.py` (98 checks + 4 defect controls, 31 of them new in v4). Every attack test has a POSITIVE CONTROL: the planted file, replace ref or fake git DOES act when the defence is absent.
- **Invocation is now:** `python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py runner|custody|evidence|gates|firewall-check ...`. Plain `python entry.py` also works, because stage 1 re-executes safely.

| finding | v4 repair | test (positive control) |
|---|---|---|
| **P1** (blocking): stage 1 imported json/hashlib/subprocess/... with the script directory first on sys.path | Stage 1 imports nothing from a path before re-executing. `sys` is built in. sys.path[0] is dropped FIRST; sys.path is then cut to the interpreter's standard-library directories (PYTHONPATH entries and site-packages removed); only then is `subprocess` imported. If site did not preload `os` (`-S`), stage 1 refuses. Defence in depth: any `*.py` in the package directory outside the known module list is refused. | A `json.py` planted in the package directory is NOT executed and is refused. (Control: the same plant runs when that directory is on the path.) |
| **P2** (blocking): the repository root was first on sys.path in the key-holding process; the guard covered prometheus.* only | The repository root is NOT on sys.path. `prometheus` is served only by the guard, from an explicit path. The guard refuses ANY other module that would resolve to a file inside the repository. `protocol.loaded_closure` reports every loaded module whose file is inside the repository, and check_gates refuses what the audit does not bind. | `argparse.py` and `__future__.py` planted at the repository root, with the custodian's cwd there, are NOT executed; the gates still pass. The closure reports a repo-root module. (Control: the plant runs when the root is on the path.) |
| **P3** (blocking): entry.py refused KEY_RELEASED.json / REVEALED.json, so the protocol deadlocked after release | entry's allowed record names include both. The selftest asserts `entry.FIXED == protocol.FIXED_RECORDS`. There is a new END-TO-END test THROUGH entry.py: a throwaway repository with a bare `origin`, a real fetch, and a `gates` target. | entry passes the gates, and still passes with both once-only records committed |
| F-GOV: entry picked the highest audit before the allow-list filter (DoS) | The allow-list filters first, exactly as in protocol.check_gates. | An unauthenticated later FAIL audit is ignored by entry and reported. |
| F-FETCH: fetch failure ignored; C3D2_NO_FETCH bypass | A failed fetch REFUSES. The bypass variable is removed. The reference is resolved ONCE to a commit, and every later read uses that commit (the TOCTOU note; the same in check_gates). | An unreachable origin is refused. |
| F-GITENV: GIT_* variables and replace refs could present a forged history | git runs with every GIT_* variable removed and GIT_NO_REPLACE_OBJECTS=1 (entry and protocol). | A local replace ref swapping the governing audit for a FAIL is ignored. (Control: plain git shows the forgery.) |
| F-CWD (CONFIRMED on M1): Windows CreateProcess searched the current directory for `git` | git runs by ABSOLUTE path from an absolute PATH entry that is neither the current directory nor inside the repository (entry, protocol, firewall_check). | A `git.exe` in the custodian's cwd (the repository root) is not executed. (Control: without the variable NoDefaultCurrentDirectoryInExePath, plain Python runs the planted `git.exe`.) |
| F-KH: key-holding tools started with `python -m` (cwd on the path, `.pyc` honoured) | `firewall_check` runs only through `entry.py firewall-check`. That target runs BEFORE any audit, so it is bound to the COMMITTED code at the resolved origin/main (the working tree must equal it). custody `result-seal` and `evidence` also require entry. allowlist.py drops its script directory first and appends the repository root LAST. | firewall-check through entry is clean on a throwaway repo; it finds a planted (upper-cased) key copy; it refuses without entry |
| F-ONCE: the once-only records were checked only at the ref; concurrent release possible | A record EVER committed in the full history counts. release and reveal hold an O_EXCL lock. | A record deleted later still counts. A second lock is refused. |
| F-DEST: `--dest` could be a UNC or network path or a synced folder; the key file had the default ACL | Only a local fixed drive is accepted: UNC, non-fixed drives and OneDrive roots are refused. The released key file's ACL is cut to the custodian plus the designated account (icacls, inheritance removed); release is refused if that fails. | A UNC path is refused; a local path is accepted; the ACL has no Everyone / Users / Authenticated Users entry |
| F-AST: `from X import name` aliases were not inspected | Imported NAMES are checked against the forbidden attributes and calls; `import *` is flagged. File- and network-capable modules are added (codecs, fileinput, gzip, bz2, lzma, logging, xmlrpc, imaplib, poplib, telnetlib, nntplib, socketserver, ssl, select, selectors, xml, wsgiref, _socket, _io, _thread). | `from numpy import fromfile as ff`, `from codecs import open`, `logging` and `xmlrpc` are flagged; the dummy package is clean |
| F-NET: nothing blocked the child's network | HEURISTIC: before any package code runs, the child replaces the socket constructors and resolvers with refusals. NOT a boundary; see residuals. | In a child, socket creation works before the block and is refused after it. |
| claim 2: key-holder scan quality | The history scan ALWAYS runs, and all_clean requires it. Key and salt are also searched as raw bytes and base64 / base64url; seed clusters are searched in history too. comms is scanned by dumping the messages to a directory outside git and passing it with `--scan` (custodian procedure). | positive control above |
| claim 6: the redraw did not check its own code | `verify_reveal` redraw reports `redraw_code_matches_manifest`: draw.py, sealbox.py and __init__.py against `d2_src_sha256_at_draw`, and medium.py against `family_src_sha256`. | the evidence bundle's REVEAL_VERIFY carries it |
| note: hostile reply shapes (MemoryError / RecursionError) crashed the runner | Hostile replies are caught as PREDICTOR_CRASH. | - |

Residuals, restated. These are NOT boundaries, and v4 does not claim them:
- The S1 root of trust is open (#925). Branch protection on main is off.
- **The OS account is the boundary, not the process.**
  - Every process of the custodian's account (jcrai on M1) can read the secrets directory. That includes every seat and tool that runs repository code as that account.
  - entry.py stops the protocol's OWN tools from executing unbound code; it cannot stop other code that the same account runs.
  - A real boundary needs a dedicated custodian account that holds the secrets and runs only verified code. That is a host capability request (MWO s6); no seat creates users.
- **Separate predictor-child account.**
  - Every production run still fails closed with ChildNotIsolated, because the child shares the runner's account.
  - That account is the second host capability request.
  - Network egress needs an outbound firewall rule for the child account, a third privileged host setting. The in-process socket block is a heuristic only.
- **Third-party code (F-3P).** numpy, scipy, cryptography and site-packages `.pth` files run unbound in the key-holding process. On M1, H:\Python312 site-packages is writable by the custodian account.
- **entry.py cannot vouch for itself.** A modified entry.py simply skips its checks. entry prints its own sha256 at start; the custodian compares it with the governing audit's binding before trusting a run.
- **A committed KEY_RELEASED or REVEALED record by anyone blocks release or reveal.** This fails closed; authenticating records is S1.
- **The plaintext length is visible in the manifest.** Future seals should pad.

## v5 (2026-09-29): repairs after the v4 re-audit FAIL (roles/Odysseus/fabric_pilot/d2_audit/v4/VERDICT.md @ d3600b21e)

- **OPEN, the operator's decisions:** S1, the root of trust (#925); branch protection on main.
- **Every v4 blocking and must-fix finding is repaired**, and so are the should-fix items.
- `selftest_protocol.py`: 118 checks + 4 defect controls, 20 of them new in v5. Every attack test has a positive control where the attack is demonstrable on this OS.

**The only invocation is `python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py <target>`.** Targets:
- `runner` (also `runner --preflight`);
- `custody`, `evidence`, `gates`;
- `firewall-check`, `allowlist`;
- `pin-tools [--confirm DIGEST]`.

| finding | v5 repair | test (positive control) |
|---|---|---|
| **B-1** (blocking): `icacls` by bare name in key release | icacls runs by absolute path in the system directory (GetSystemDirectoryW). entry sets NoDefaultCurrentDirectoryInExePath=1 for every verified process and its children. | An `icacls.exe` planted in the cwd is not executed; the ACL is really restricted. (Control: without the variable, plain Python runs the plant.) |
| **B-2** (blocking): allowlist.py ran a bare `git` and imported working-tree comms / evidence_wiki code as the custodian | allowlist runs ONLY through entry, bound by the governing PASS audit, or before one exists by the custodian-pinned pre-audit binding. git goes through protocol (absolute path, hardened). Records come from origin/main only. The comms message is read with psycopg2 directly; the evidence_wiki connection settings are read as DATA, and comms/evidence_wiki code is never imported. | Refused unpinned; runs after `pin-tools --confirm`; refuses without entry |
| **S-1** (must-fix): the runner could not complete through entry, and failed AFTER the key release was consumed | (a) The spawn child re-imports entry.py as `__mp_main__` and installs the parent's binding (C3D2_BOUND) before it unpickles its target, so it imports the runner through the same guard. (b) `FirewallRun.preflight()` starts a predictor child and runs the isolation probe (released key path, secret paths, file creation in the output root) BEFORE the key is read or deleted and before the run directory exists. A refusal consumes nothing. (c) `entry.py runner --preflight` (no key) is the check to run before custody releases the key. (d) A child that dies is PredictorChildFailed, a refusal rather than an uncaught EOFError. | END-TO-END THROUGH entry.py: `--preflight` and a full run both start the child under the guard and are refused ChildNotIsolated (same account); the key copy still exists and no run directory was made. In-process, the preflight refuses a readable key before reading it. |
| S-2: firewall-check was bound only to the committed code, even after a PASS audit | A governing allow-listed PASS audit binds EVERY target. Before one exists, only firewall-check and allowlist may run, and only if every file is PINNED by the custodian (allow-list role PREAUDIT_TOOL). The pin comes from `entry.py pin-tools`, which runs no repository code: it prints the files' sha256 and a digest; `--confirm DIGEST` pins them. | wrong digest refused; pinned run shows `pre-audit:pinned@<commit>` |
| S-3: plain `python entry.py` claimed safe | Only `-I -B` is accepted; anything else is refused. Under -I, sys.path entries inside the repository are dropped before any non-builtin import (N-2). | plain python refused |
| S-4: key-holding CLIs accepted any `refs/...` | custody, evidence and runner refuse any ref other than refs/remotes/origin/main. | custody and runner refuse another ref |
| S-3/S-5 (key hygiene) | The designated account must be ONE user account (LookupAccountNameW SidTypeUser; Everyone/Users refused). The destination must not exist; it is created and ACL-restricted (inheritance removed, custodian F plus runner M, inheritable) BEFORE the key is written. A failed release deletes the key and the directory. The custodian comes from the OS, not USERNAME. | groups refused; the current user accepted; a failed release leaves nothing; an existing dest is refused |
| S-5 (git): hooks, grafts, shallow | Every git call carries `-c core.hooksPath=<devnull> -c gc.auto=0 -c maintenance.auto=false`. entry and check_gates refuse a repository with `info/grafts` or `shallow`. | grafts refused by entry and by protocol |
| S-6: `once_record_present` failed open | A git error raises (AmbiguousRef); it never reads as "no record". | a bad ref raises |

Residuals, restated. These are NOT boundaries, and v5 does not claim them:
- S1 is open (#925); main is unprotected.
- **The OS account is the boundary, not the process.** Every process of the custodian's account can read the secrets. v5 removes every place where the PROTOCOL'S OWN tools ran unbound code. It cannot stop other code that the account runs; the comms client this seat uses is one example. A dedicated custodian account is a host capability request (MWO s6).
- **Separate predictor-child account.** A same-account child is always refused, now at the preflight, before anything is consumed.
  - That account, with an outbound firewall rule for it, is a host capability request.
  - It must be able to read the allow-list and the repository (`safe.directory`) and write the output root. The preflight checks the isolation half.
- **F-3P:** site-packages code (numpy, scipy, cryptography, psycopg2, `.pth` files) runs unbound.
- **Git configuration** (remote URL, `insteadOf`, fetch refspecs) is same-account state and stays within the account residual.
- **Timing side channel (N-1):** the predictor controls its run time, and commit and utc times are public after the predictions are frozen. That leaks a few bits about the hidden set, after commitment. Declared.
- **DoS by any main pusher (N-2):** a stray protocol/ record or a package `.py` makes entry refuse, which fails closed.
- **entry.py cannot vouch for itself:** compare its printed sha256 with the governing audit's binding.
- **The plaintext length is visible in the manifest.**

## v6 (2026-09-29): repairs after the v5 re-audit FAIL (roles/Odysseus/fabric_pilot/d2_audit/v5/VERDICT.md @ 01ac0fedf)

- **OPEN, the operator's decisions:** S1, the root of trust (#925); branch protection on main.
- **Branch protection also covers a force-push that removes the once-only records.** The custody log still refuses a second release on M1, but git is the durable record.

| finding | v6 repair | test |
|---|---|---|
| **BP-1 / F1** (blocking): the runner read and deleted the key BEFORE validating the package; custody did not require a preflight | (a) `FirewallRun.validate_package()` reads the package ONCE and checks hash, members, metadata and the AST audit BEFORE the preflight and BEFORE the key is read. The extraction later uses exactly those validated bytes. (b) `entry.py runner --preflight` runs the package checks, starts the child and probes isolation, then writes `<run out root>/PREFLIGHT_<designation nonce>.json` (public fields only). (c) custody `release-key` REQUIRES a PASS preflight record matching this designation's nonce, spec_id, committed package hash, runner id and account (`protocol.preflight_ok`). | A wrong-hash package (PackageHashMismatch) and an AST-flagged package (PackageAuditRefusal) are each refused with the key copy intact and no run directory. Release is refused with no preflight and with a mismatched one, and succeeds with a matching one. |
| self-test failed on the Linux node (`v4_DEST_key_acl_restricted`) | The test took the account from `$USER`, which the fabric script environment does not set. It now uses the OS account (`protocol.os_account()`); the POSIX path (chmod 0600) is unchanged. | passes on M1; expected to pass on Linux |
| should-fix: account compared by name | `protocol.same_account`: SID equality (LookupAccountNameW) when both resolve, otherwise case-insensitive names. Used for the designated-account and custodian checks. | the same account in another case compares equal |
| should-fix: pins irrevocable | Only the LATEST pin batch counts. A new `pin-tools --confirm` supersedes, and so revokes, every earlier pin. | - |
| should-fix: firewall_check git without hardening | uses `protocol.GIT_HARDEN` | - |
| should-fix: allow-list path relative on POSIX | entry and protocol refuse a non-absolute allow-list path. Custody is M1-only. | - |
| widened S1 (F2/SF-3): the allowlist database came from committed config | The database HOST and NAME come ONLY from the custodian's environment (EW_DB_HOST, EW_DB_NAME); committed config supplies credentials only. Sender authentication is still S1. | - |

**The documented command should name the interpreter by absolute path (SF-4):** `H:\Python312\python.exe -I -B <repo>\prometheus\cosmos\c3_holdout_D2\entry.py ...` on M1.

**Release procedure (v6):**
1. The runner account runs `entry.py runner --preflight --package P --package-sha256 H --runner-id R`, which writes the PREFLIGHT record.
2. The custodian runs `entry.py custody release-key`, which requires that record.
3. The runner runs `entry.py runner ... --key K`.

A same-account child fails step 1, so nothing is ever released until the separate child account exists (the host capability request).

## v7 (2026-09-29): repairs after the v6 re-audit FAIL (roles/Odysseus/fabric_pilot/d2_audit/v6/VERDICT.md @ 7567a018b)

- **OPEN, the operator's decisions:** S1 (#925); branch protection on main.
- **Adjudication rule (Harmonia #960, Addendum E @ 9f6abdce6), stated before any exposure:** a consumed release without a result seal is FORFEIT if attributable to the package, and VOID if infrastructure.

**The run is now two phases.**
- **`prepare()`: nothing consumed.** It runs:
  - the gates;
  - the run-directory, manifest and family checks;
  - package VALIDATION;
  - package STAGING into `<run>/package`, from the validated bytes;
  - the child isolation probe on the released key path, the secret paths, a receipts STAND-IN in the run directory (read + append), and file creation in the run directory and its root.
- **`open()`:**
  1. The key is READ into memory; a missing or bad key file consumes nothing.
  2. `receipts.jsonl` and the open record are written. This is the consumption marker; the run directory no longer is.
  3. The released copy is deleted and the key decrypted.
- **After the open record, `run_all()` ends every path in a TERMINAL record:** `close`, or `abort` with RESULT.json status ABORTED. custody `result-seal`, `reveal` and `evidence` accept both terminal kinds.

| v6 finding | v7 repair | test |
|---|---|---|
| 1. extraction after the key read | staging in prepare(). Member names that could not stage are refused at VALIDATION: portable characters only, no reserved device names or trailing dot, bounded length, no case-insensitive or file/directory collision. A staging failure is a refusal before the key. An earlier staging is reused only if byte-identical. | 4 unstageable names refused; blocked staging refused with the key intact and no receipts |
| 2. receipts probe after the key read | a receipts stand-in in the same directory is read/append-probed in prepare(), with file creation in the run directory. The post-key probe on the real receipts remains; its failure is now a sealed abort. | the stand-in is named by the pre-key refusal; no receipts |
| 3. the package can crash the parent through the pipe (`_HiddenWorldStub__conn`) and void the run | (a) ANY malformed or unexpected child message, or a failed reply, is that world's PROTOCOL_ERROR: recorded, sealed with the predictions, and the run continues. (b) A per-world certify exception is recorded as CERTIFY_ERROR. (c) Any other exception after the open record, KeyboardInterrupt and MemoryError included, becomes a terminal `abort` receipt plus RESULT ABORTED, which custody can result-seal; Harmonia then adjudicates FORFEIT or VOID. (d) The AST audit flags private attributes (`._X`). This is a heuristic; the pipe no longer depends on it. | A package writing garbage into the pipe (allow_flagged) gives PROTOCOL_ERROR for every world, and the run CLOSES. A simulated MemoryError after open gives a sealed abort that custody result-seals (terminal "abort"). The private attribute is flagged. |
| selftest on Linux | `v6_account_sid_equality` is None (not applicable) off Windows: SIDs exist on Windows only. | - |
| should-fix: run output shared with the allow-list and custody log | RUN_OUT_ROOT is `.../holdout_D2/runs` | - |
| should-fix: exceptions after the seal uncaught | per-world CERTIFY_ERROR, and abort for anything else | above |
| should-fix: the preflight record is self-reported | Declared. The record only gates the RELEASE. The run's own prepare() repeats every check and probe before the key is read, so a forged record cannot get a run past an unmet check; at worst a key copy is released early and sits unused. | - |

**Crash-after-release policy (declared, v6 item 3):** EXPLICIT RESIDUAL, no recovery path.
- A crash outside the runner's control after the open record (power loss, OS kill, disk full while writing the abort) leaves receipts without a terminal record.
- That attempt is an evaluation of record (Addendum E): package-attributable -> FORFEIT; infrastructure -> VOID.
- The once-only rules stand: no second release, and no resume, for this spec_id.
- D2 is then spent, and any further evaluation needs a successor seal, disclosed beside this attempt (Addendum E item 3).
- Resume stays refused because a resumable run would give the package a second look at the hidden set.

## v8 (2026-09-29): repairs after the v7 re-audit replicas (tsk-24ad3df260b9, tsk-6a58313857f2; both FAIL)

- **OPEN, the operator's decisions:** S1 (#925); branch protection on main.

| v7 finding | v8 repair | test |
|---|---|---|
| V7-1 / V7-C (blocking): the consumption marker existed before the open record, so a failure there left a chain starting with `abort` that never verifies, and the spec_id was spent unsealed | The WHOLE open record (every hash, the package meta, the run parameters) is built and serialised in prepare(); anything that cannot serialise is refused BEFORE the key. `Receipts.create_with_open` then writes record 0 to a temp file, fsyncs it and renames it to receipts.jsonl. The consumption marker therefore appears ATOMICALLY with a verifiable open record; a failure before the rename leaves no marker and the key intact. | A simulated write failure leaves no receipts and the key intact. A successful open starts with a verifiable open record. open followed by abort verifies. |
| V7-A (blocking): the receipts stand-in was only append-probed | The stand-in is probed for READ and append before the key. | the pre-key refusal lists the stand-in for both |
| V7-B (blocking): the parent's `predict` send was outside the per-world guard, so a package closing the pipe aborted the whole run with no attribution | The send is inside the guard: a broken or closed pipe is THIS world's PREDICTOR_CRASH and the run continues. A broken pipe at worker shutdown is not a run failure. | A package that closes the pipe every world gives per-world crash/protocol errors, and the run CLOSES. |
| Q3: an abort carried a type name only | The abort record carries attribution EVIDENCE for Harmonia's FORFEIT/VOID decision (Addendum E): current world, whether it failed inside predictor I/O, and the child's exit code. It is evidence, not a verdict. | the abort carries the fields |
| V7-F (note): unbounded child messages | Child messages are capped at 64 MiB; a longer message is that world's error. | - |
| V7-D (note): AST bypass via `operator.attrgetter` / `faulthandler` | operator, faulthandler, functools and copyreg are flagged. This is a heuristic; the pipe does not depend on it. | attrgetter flagged |

**Residuals added (declared, not boundaries):**
- **The child can signal or pressure the parent.** Examples: Windows console control events to the shared console group, and memory or compute pressure through legitimate System calls. The resulting abort carries the attribution evidence above; its reading is Harmonia's.
- **There is no code yet to start the predictor child under the separate account (V7-E).** That code will need its own audit before any designation.
- **Crash-after-release (v7 policy) is unchanged.** The atomic marker means an ordinary exception can no longer spend the designation without a sealable terminal record.

## v9 (2026-09-29): repairs after the v8 re-audit FAIL (roles/Odysseus/fabric_pilot/d2_audit/v8/VERDICT.md @ bea18a398)

- **OPEN, the operator's decisions:** S1 (#925); branch protection on main.
- **Adjudication reading:** Harmonia Addendum H (65329b9c5). Exposure is the first world delivered. Runner attribution labels count as evidence only once a governing audit finds them truthful.

| v8 finding | v9 repair | test |
|---|---|---|
| 1 (V8-1, replica 1; blocking): the key was proven only after the marker, so a wrong but well-formed key spent D2 | `open()` reads the key and PROVES it BEFORE the consumption marker: it must decrypt the sealed ciphertext (AES-GCM tag checked), and the plaintext must match the manifest. The worlds, seeds and tags are also built first. Only then is receipts.jsonl created (atomically, v8) and the released copy deleted. custody `release-key` test-decrypts the custody key before any copy is made. | A well-formed wrong key is refused with the key file intact and no receipts. Custody with a wrong key releases nothing. |
| 2 (V8-1, replica 2; blocking class): an interrupted record write could leave an unsealable chain | `Receipts.append` rolls a failed write/fsync back to the last complete record. `Receipts.repair()` truncates trailing bytes that are not in the in-memory chain, and `abort()` repairs before writing its terminal record. The chain on disk therefore always equals the chain in memory. | A simulated fsync failure on a later record: rolled back, the abort seals, the chain verifies, and custody result-seals it (terminal "abort"). |
| 3a (V8-2): `child_exitcode` always null | The exit code is kept when the worker is stopped and reported in the abort record. | the abort carries a non-null exit code |
| 3b (V8-3): a restart-probe failure was labelled as infrastructure | The world and the predictor-I/O label are set BEFORE the (re)start, so a restart refusal is attributed to that world. | a simulated restart failure gives an abort with current_world 0 and in_predictor_io true |
| note (V8-6): staged package readability not checked pre-key | The pre-key probe REQUIRES the child to be able to read the staged package entry; otherwise PredictorChildFailed, before the key. | an unreadable staging is refused pre-key |

**Notes carried:**
- **Windows `poll` timing:** plausible, unverified. A per-world poll failure is a per-world status; anything else is a sealed abort, labelled.
- **RESULT.json write failure after close:** the chain still ends in `close`. RESULT.json can be rebuilt from the receipts, but no tool does that yet; declared.
- **The released key copy after an abort:** it is deleted right after the marker; if that deletion itself fails, the run aborts and the copy remains on M1 under the restricted ACL; declared.

## v10 (2026-09-29): should-fix items from the v9 re-audit replicas (tsk-5c232d68f717 FAIL on S1 only; tsk-fe9b89e4c15c PASS excluding S1)

- **Neither replica found a new blocks-PASS finding.**
- **OPEN, the operator's decisions:** S1 (#925); branch protection on main.

| v9 finding | v10 repair | test |
|---|---|---|
| S-A / A3-1: a failure of the FIRST child start was labelled post-exposure | New `exposed` flag, set only after the first predict send succeeds (Harmonia Addendum H: exposure = first world delivered). Before a (re)start, `in_predictor_io` is true only once exposure has happened. The abort record carries `exposed`. | first-start failure: current_world 0, in_predictor_io false, exposed false; restart failure after exposure: world 1, in_predictor_io true, exposed true |
| A3-2: `child_exitcode` could come from another child | The exit code is tied to its child: `child_world` (the world at which that child was started) is recorded with it. | child_world and exit code of the stopped child |
| S-B / B-2: the per-world `poll` was outside the guard | The poll is inside the per-world guard; a poll failure is that world's PREDICTOR_CRASH. | - |
| S-C / B-4 / B-1: a spent run could end with no sealable terminal record, and no tool closed it | (a) `entry.py custody seal-terminal --run DIR`, custodian only, for THIS designation's run directory. It keeps the longest verifying prefix of complete records (truncating a torn tail), appends a custodian `abort` with null labels when there is no terminal record, and rebuilds RESULT.json from the receipts. It never removes a verifying record. (b) RESULT.json is a pure function of the receipts (`result_from_records`) for close, abort and seal-terminal alike; `abort()` after a CLOSED record whose RESULT write failed rebuilds it, and the CLI no longer raises a KeyError. (c) SIGINT is ignored while `abort()` runs. | a torn, unterminated run is sealed and custody result-seals it; a lost RESULT.json is rebuilt byte-identical; another designation's directory is refused |
| B-3: no exclusive creation of the marker | An O_EXCL `receipts.jsonl.claim` is taken before the atomic rename, and released if the write fails. | an existing claim refuses, with the key intact and no receipts |
| notes | Custody test-decrypts at the commit the gates resolved; a malformed custody key frees the custody lock; `abort()` records whether the disk chain matched memory (`disk_chain_matched`); no stale `current_world` outside PREDICT. | malformed key frees the lock |

**Declared for Harmonia (A3-3):**
- The runner kills its direct child only, not the child's process tree. So `in_predictor_io=false`, a SEALED phase or an exit code do not prove the package was inactive.
- Under Addendum H these labels are evidence only once audited truthful. Until then every post-exposure abort is FORFEIT.
- A custodian `seal-terminal` abort carries null labels by design: the custodian asserts no cause.
- **Package-induced disk exhaustion through the child account** is a declared residual: it aborts or, at worst, needs seal-terminal. The separate child account's quota is part of the host capability request.
