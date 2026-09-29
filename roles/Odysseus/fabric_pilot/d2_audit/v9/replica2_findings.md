# Holdout D2 v9 firewall re-audit: adversarial replica findings

- Audited commit: 2aa834ab1 (package content = ece679b89, D2 v9). `rogit diff --stat a02b9b20c 2aa834ab1` over the
  package, c3, c3_holdout_D and the package `__init__` files shows that only these changed since the v8-audited code:
  runner.py, custody.py, selftest_protocol.py, SELFTEST_PROTOCOL.json, FIREWALL.md and AUDIT_BRIEF.md.
- Method: static reading plus git history. No code was executed; this replica cannot run code. Runtime claims rest on
  the committed `SELFTEST_PROTOCOL.json`: 148 checks all true, 4 defect controls true, `not_applicable_on_this_os: []`
  (lines 1-208).
- Scope: the firewall layer only.
- Still open as operator decisions: S1 (#925) and branch protection on main.

## Context that governs severity

- A same-account predictor child is always refused before the key is read (`runner.py:688-699`, `FIREWALL.md:249-250`).
- The launcher for a separate-account child does not exist yet (V7-E, `FIREWALL.md:333`), and it needs its own audit.
- So every post-key finding below is latent: no production run can reach it with this code.
- Severities follow the standard of earlier rounds: an unsealable or unattributable spend of the one-time release is
  judged on the code as written.

## v9 items

### Item 1: the key is proven before the consumption marker. HOLDS

Attacks tried:
- (a) A well-formed wrong key.
  - `open()` reads the key (`runner.py:750`) and decrypts with the AES-GCM tag checked (`runner.py:751-755`).
  - It then checks consistency with the manifest (`:756-759`) and builds the worlds, seeds and tags (`:760-767`).
  - All of this happens BEFORE `create_with_open` (`:769`) and the unlink (`:772-773`).
  - A wrong key raises HiddenSetMismatch while `self.receipts` is None, so `run_all` re-raises (`:843-845`) and
    nothing is consumed.
  - Self-test: `selftest_protocol.py:1195-1197`.
- (b) A malformed key or a non-dict plaintext.
  - The error raised (ValueError / AttributeError) is still before the marker, so nothing is consumed.
  - Cosmetic: it surfaces as a traceback rather than a `refused` JSON line (`runner.py:1126-1130` catches
    RunnerRefusal only).
- (c) Custody releasing a wrong key.
  - `_test_decrypt` (`custody.py:171-179`) runs before `dest.mkdir` (`:202-204`).
  - A missing blob from `_show` (returns None, `protocol.py:203-206`) becomes a CustodyRefusal through the broad
    except, so the lock is cleaned up.
  - Note (pre-existing): a malformed custody key file raises ValueError from `read_hex_file` (`sealbox.py:83-88`),
    which is not in the except tuple (`custody.py:210`). The custody lock is left stale. This fails closed.

### Item 2: an interrupted write stays sealable. HOLDS, with one carried note

Attacks tried:
- (a) A write/fsync failure mid-append.
  - `append` rolls back through `repair()` (`runner.py:401-410`, `417-431`).
  - Append-only writes keep the disk content prefixed by the in-memory chain, so the truncation is exact.
  - `abort()` repairs before writing its terminal record (`:813`).
  - Self-test: `selftest_protocol.py:1209-1232`.
- (b) A record that is durable on disk but missing in memory (interrupt after the `with` block).
  - repair truncates it. The chain stays consistent with memory, and nothing external had observed that record.
- (c) Carried from v8 (replica 2, V8-5): an operator/OS interrupt between `os.replace` (`runner.py:389`) and the
  assignment `self.receipts = ...` (`:769`) still leaves a marker with `receipts is None`.
  - `run_all` then re-raises (`:844-845`), giving a chain with no terminal record.
  - No package code has run at that point, so this is operator/OS only.
  - Severity: **note** (not declared in v9).

### Item 3: attribution labels are truthful. BROKEN (should-fix; labels NOT certified)

- **A3-1: a failure of the FIRST worker start is labelled as predictor I/O on world 0.**
  - v9 sets `_cur_world=i, _in_predictor_io=True` before `_start_worker()` (`runner.py:927-929`).
  - For i=0 this is the first start. `_worker_main` answers the isolation probe BEFORE any package code is imported
    (`runner.py:330-341`: the probe, then "go", then the import). No world has been sent (the send is at `:931`).
  - Scenario: a post-key start failure caused by the host, such as the 120 s probe timeout under load (`:785-790`),
    or `Process.start()` / the probe `_send` raising outside the guard (`:780-783`).
  - Result: an abort with `current_world=0, in_predictor_io=true, n_predictions_recorded=0`.
  - Under Harmonia Addendum H cl.1, the truthful state is pre-exposure (VOID). The label reads as post-exposure
    (FORFEIT).
  - v8 got this case right (None/False). v9 regressed it while fixing restarts.
  - The self-test enshrines the wrong label: `selftest_protocol.py:1241-1253` makes the FIRST start fail at world 0
    and asserts `in_predictor_io is True`.
  - Partial recovery: PredictorChildFailed or ChildNotIsolated with `current_world=0` can only come from the first
    start. But a raw OSError from `start()` or the probe `_send` (`:780-783`) is not distinguishable from a world-0
    I/O abort.
  - Fix: record a distinct `in_worker_start` flag and a `worlds_delivered` count (set just before the send at
    `:931`). Better still, start the first worker (probe plus import) inside `prepare()` so that no probe runs
    after the key.
- **A3-2: `child_exitcode` can be stale or come from a different process.**
  - `abort()` kills the worker first (`:809-812`), so it always reports `_last_exitcode` (`:818`, `:893`).
  - With no child running at abort time, that value comes from an earlier process. Examples:
    - the key unlink fails after the marker (`:772-773`): the value is the exit code of the prepare-probe child
      (`:694`);
    - an abort in the SEALED phase: the value is the exit code of the child stopped at the end of PREDICT (`:985-989`).
  - For a live child, the value is the parent's own kill code.
  - The self-test checks only that the value is not null (`selftest_protocol.py:1240`), in a certify-phase abort.
  - Fix: null when no child is live; add a `killed_by_runner` flag.
- **A3-3 (evidence caveat for Harmonia):** `in_predictor_io=false`, phase SEALED or `child_exitcode` do not show that
  the package was inactive.
  - The worker is killed as a single process. There is no process-tree or Job Object kill (grep: none in the package).
  - The AST audit is a declared heuristic (`FIREWALL.md:48-53`).
  - These labels must not be read as "cause outside the package's control" (Addendum F item 2).
- Consequence: Addendum H cl.2 stays in force: every post-exposure abort is FORFEIT whatever its label. Integrity is
  not harmed, because every mislabel found points toward FORFEIT. The harm is fairness to the predictor.

### V8-6: staged package readable before the key. HOLDS (note)

- `must_read` is the staged entry file, probed in `prepare()` (`runner.py:692-693`, `791-795`).
- Only the entry file is checked. Other members that are unreadable would give per-world crashes, not a refusal.
  Low likelihood, because all members inherit the same ACL.

## Other attacks on the "no verifiable terminal record" criterion

- **B-1: a console-control / SIGINT interrupt during `abort()` itself. should-fix.**
  - `abort()` guards `_stop_worker` with `except Exception` (`runner.py:809-812`). KeyboardInterrupt is not an
    Exception, and nothing in the package ignores SIGINT during the run (grep: no signal handling).
  - A further interrupt while `abort()` runs escapes `run_all`. The chain verifies but has no terminal record, so
    custody cannot result-seal it (`custody.py:244-245`).
  - The v8 residual text "The resulting abort carries the attribution evidence" (`FIREWALL.md:332`) is therefore
    not always true.
  - Adjudication: Addendum F item 3 already rules this state FORFEIT, so the package gains nothing. An operator's
    repeated Ctrl-C would, however, be scored FORFEIT.
  - Fix: ignore SIGINT and console control events in the parent from the marker onwards; start the child in its own
    process group. The V7-E launcher audit must cover this. Add a custodian tool that terminates an unterminated
    verifying chain (as recommended in v8).
- **B-2: `poll` outside the per-world guard. note; v9 documentation inaccurate.**
  - `FIREWALL.md:350` says "A per-world poll failure is a per-world status". The poll at `runner.py:938` is still
    outside any try block.
  - Effect: the whole run aborts with the label in_predictor_io=true, which counts against the predictor.
- **B-3: runner exclusivity regression. note.**
  - v8 replaced the exclusive create with exists() + a fixed tmp name + `os.replace` (`runner.py:381-389`).
  - Two concurrent runner invocations could both pass the check. On Windows this needs microsecond alignment,
    because an open tmp handle blocks the other process's replace.
  - Operator-only.
  - Fix: `os.link` or `O_EXCL` for the marker, or a run lock.
- **B-4: RESULT.json write failure after the terminal record. note (partly declared).**
  - After `close` this is declared (`FIREWALL.md:351`). After `abort` (`runner.py:829-830`) it is the same problem
    but undeclared.
  - After `close`, the CLI also hits a KeyError on `res["chain_head"]` (`runner.py:807-808` return value used at
    `:1154`).

## Claims 1-6 (brief)

The package code is unchanged since the v8-audited commit except for the v9 hunks reviewed above.

| # | claim | verdict | evidence / attacks |
|---|---|---|---|
| 1 | Opacity | HOLDS (note: `ciphertext_bytes` declared) | See below. |
| 2 | Secrets never in git | HOLDS (repo side); key-holder scan CANNOT-VERIFY | See below. |
| 3 | Enforced order | HOLDS except S1 (OPEN, declared) | See below. |
| 4 | Controlled reveal | HOLDS | See below. |
| 5 | Predictor isolation | HOLDS as declared (heuristic AST; same-account child refused) | See below. |
| 6 | Draw integrity | HOLDS (single-draw provenance declared) | See below. |

**Claim 1 (Opacity):**
- The manifest carries public fields only (`MANIFEST_D2.json:1-36`); the IV is public by design.
- Receipts identify worlds only by index and an HMAC tag (`runner.py:762-763`).
- Error replies carry type names only (`:955-956`).
- The v9 additions (the decrypt-before-marker exception text, `child_exitcode`) are type names or local receipts.
  Nothing new is public before reveal.

**Claim 2 (Secrets never in git):**
- `rogit log --all --name-only` over `prometheus/cosmos/c3_holdout_D2` and `roles/Nestor` shows no key, salt, plain,
  hex, pyc or `protocol/` file ever.
- The key-holder scan runs on M1; only its booleans are published.

**Claim 3 (Enforced order):**
- AUDITED_FILES is unchanged (`protocol.py:76-84`) and includes the changed runner.py and custody.py. v9 adds no
  imports.

**Claim 4 (Controlled reveal):**
- Custody now releases only a proven key (`custody.py:202-203`).
- result-seal requires a terminal record (`custody.py:244-245`).

**Claim 5 (Predictor isolation):**
- The pipe is pickle-free (`runner.py:170-206`).
- The probe runs before the import (`:330-341`).

**Claim 6 (Draw integrity):**
- `draw.py` and `sealbox.py` are unchanged since the seal.
- `d2_src_sha256_at_draw` is present (`MANIFEST_D2.json:11-15`).

## The seven standard classes

1. Unbound code: no new imports; the v9 files are bound. F-3P (third-party code) is declared.
2. Same-account readability: declared (the account is the boundary).
3. AST audit: a declared heuristic. It remains bypassable through non-flagged standard-library module attributes;
   do not rely on it. It is no longer load-bearing for the pipe.
4. Git refs: unchanged; v8 held.
5. Records: S1 OPEN.
6. Public narrowing: `ciphertext_bytes` is declared. No new public field.
7. Host checks: unchanged; v8 held.

## Declared residuals

- Acceptable as declared:
  - key holder;
  - AST audit as a heuristic;
  - single-draw provenance;
  - the System interface exposing physics.
- The v8 residual "child can signal the parent ... the resulting abort carries the attribution evidence" is
  inaccurate (B-1) and should be restated.
- Missing from the list:
  - the stale or ambiguous attribution labels (A3-1, A3-2), which are not certified truthful;
  - no process-tree kill (A3-3);
  - RESULT.json after abort (B-4).

## Verdict

- No finding lets Cosmos learn hidden content, or breaks custody or the order, apart from S1.
- Every label defect points toward FORFEIT, so integrity holds under Addenda F and H.
- The attribution labels are NOT certified truthful (A3-1, A3-2). Harmonia Addendum H cl.2 therefore stays in force.

OVERALL: PASS for everything except S1 and branch protection, which are open operator decisions and are not
assessed. The should-fix items A3-1, A3-2 and B-1 are recommended before any release.
