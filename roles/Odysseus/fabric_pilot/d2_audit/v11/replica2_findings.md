# Holdout D2 firewall re-audit v11: adversarial findings

- Task tsk-dfd5b62e4d2c, attempt att-d7db9ffa3ee7. I am an independent replica.
- Audited commit: e47d6fbbb1ad8a9d761801b2f480dfc1d3412fe1. The D2 package code is identical to d7f9d4797, the v11 commit.
- Scope: the firewall layer only, as described in AUDIT_BRIEF.md v1-v11 and FIREWALL.md section "v11". No science is in scope.
- Method: static reading plus read-only git. **I did not run any code.** The self-tests and
  `entry.py gates SEAL` on the real history are therefore CANNOT-VERIFY here. The committed
  `SELFTEST_PROTOCOL.json` lists 160 checks, all true, plus 4 defect controls, all true (`SELFTEST_PROTOCOL.json:4-176`).
- v11 delta checked: `git diff a823b596c e47d6fbbb -- prometheus/cosmos/c3_holdout_D2`.
  - Only runner.py (109 lines changed), custody.py (5 lines), selftest_protocol.py and the docs changed.
  - entry.py, protocol.py, allowlist.py, evidence.py, draw.py and sealbox.py are unchanged since v10.

## Hash and history facts (verified here)

| item | result | evidence |
|---|---|---|
| sha256(hidden_D2.enc) | f75ba333... equals the manifest and the brief | `sha256sum`; `MANIFEST_D2.json:7` |
| sha256(MANIFEST_D2.json) | 78874e9d... equals the brief | `sha256sum` |
| draw.py, sealbox.py and `__init__.py` | match `d2_src_sha256_at_draw` exactly | `MANIFEST_D2.json:11-15` |
| medium.py | 09559e69... equals `family_src_sha256` | `MANIFEST_D2.json:21` |
| `c3_holdout_D/` vs a56ef7787 | no diff | `git diff --stat a56ef7787 e47d6fbbb -- prometheus/cosmos/c3_holdout_D` is empty |
| commit adding hidden_D2.enc / MANIFEST | only 95b31a30d | `git log --all --diff-filter=A` |
| protocol/ records ever committed | none | same log, `-- .../protocol` is empty |
| key/salt/plain/`nestor_secrets` file names in any history | none | `git log --all --name-only -- *hidden_D2.key* *hidden_D2.salt* *hidden_D2.plain* *nestor_secrets* *.key.hex *.salt.hex` is empty |

---

## Claim 1: Opacity. Verdict: HOLDS

Attacks tried:
- (a) Public manifest fields that narrow the set.
  - The fields are cipher, IV, hashes, versions, draw time, the draw rule and counts (`MANIFEST_D2.json:1-36`).
  - `ciphertext_bytes` reveals the plaintext length. This is declared (FIREWALL.md:149-150).
  - No knob, seed or nonce is public.
- (b) New v11 receipt fields.
  - The `deliver` record is `{i, world_tag, utc}` (`runner.py:1015`).
  - The abort record adds only `deliver_records`, a count (`runner.py:869`, `runner.py:1268`).
  - Receipts stay on M1. RESULT.json carries no deliver data (`runner.py:1177-1200`).
  - The public RESULT_SEAL carries `n_receipts` and `terminal` (`custody.py:274-277`). For an abort, `n_receipts` now also counts deliver records, so it shows how far the run got. That is public only after the result seal. It is a note, not a leak of hidden content.
- (c) Self-test JSONs.
  - `SELFTEST_PROTOCOL.json` holds booleans, exception type names and one file path (`closure_extras`) (`:166-219`).
  - `SELFTEST_D2.json` holds booleans only (`:1-33`).
- (d) Error text to the predictor.
  - Replies carry `type(e).__name__` only (`runner.py:1049-1050`).
  - The child's own failure string is the package's own text (`runner.py:370`).

## Claim 2: Secrets never in git. Verdict: HOLDS (repo side); CANNOT-VERIFY (M1 side)

Attacks tried:
- (a) File-name search across `--all` history. Clean (table above).
- (b) Records or tools that could write secrets into the repo.
  - `_write_once_record` writes public fields only (`custody.py:223`, `:322-323`).
  - `seal-terminal` writes only to the run directory (`runner.py:1224-1275`).
  - The key copy is refused inside git (`custody.py:131-132`; `runner.py:694-697`).

The M1 half (files outside git, `firewall_check` booleans) cannot be established from the repository. It is settled by Nestor's `entry.py firewall-check` output on M1.

## Claim 3: Enforced order. Verdict: BROKEN on S1 only (blocks-PASS, declared OPEN)

- **S1 (blocks-PASS).**
  - A record governs iff its sha256 is in the allow-list (`protocol.py:461-473`, `:514-516`, `:532`, `:560`, `:580`, `:600`).
  - The allow-list is fed from comms rows whose `sender` column is client-supplied (`allowlist.py:37-39`, `:74`, `:95`).
  - Main has no branch protection (FIREWALL.md:147-148).
  - Scenario: any comms client posts as sender "Odysseus" with the sha256 of a forged PASS `FIREWALL_AUDIT_1.json` pushed to main. Nestor allow-lists it and the AUDIT gate opens.
  - Operator decision #925.
- Everything else HOLDS. v11 did not touch protocol.py or entry.py. Attacks re-tried against the unchanged code:
  - Shadowing tag or branch: refused (`protocol.py:305-307`; `entry.py:218-220`).
  - Replace refs and GIT_* variables: stripped (`protocol.py:185-191`).
  - grafts or shallow: refused (`protocol.py:209-219`).
  - Record replaced through a merge: one blob across `--full-history -m` (`protocol.py:334-358`).
  - Stale code: committed and working tree (`protocol.py:533-542`).
  - Loaded closure (`protocol.py:543-547`).
- New stdlib imports in v11 (`threading` at `runner.py:67`; `msvcrt`/`fcntl` at `runner.py:205,209`):
  - They resolve from the interpreter paths only (`entry.py:317-330`, `:341`).
  - They are covered by residual F-3P and need no new binding.
- The runner and custody still refuse before touching the key:
  - Gates run in `prepare()` (`runner.py:688-691`) before `open()` reads the key (`runner.py:782`).
  - Custody gates run before `read_hex_file` (`custody.py:196-203`).

## Claim 4: Controlled reveal. Verdict: HOLDS (subject to S1)

- (a) Release before the gates or to another host.
  - `_gates("DESIGNATION", runner_id)` binds the host, account and nonce (`protocol.py:574-593`).
  - It refuses M2 (`protocol.py:574-583`; `custody.py:135-136`).
  - It requires a preflight (`custody.py:201-202`) and a proven key (`custody.py:203-204`).
- (b) Reveal before the result seal, or a mismatched run. The RESULT_SEAL gate plus a chain, head, nonce and RESULT hash re-check apply (`custody.py:290-305`).
- (c) Do v11 deliver records break result-seal, reveal or evidence? No. They check only the terminal kind and the head (`custody.py:261`, `:295`; `evidence.py:58`).
- RESULT_SEAL authenticity is again S1.

## Claim 5: Predictor isolation. Verdict: HOLDS for confidentiality; runner liveness is only partly bounded (should-fix V11-1, V11-2)

- The child is spawned with no key.
  - The key is proven before the marker (`runner.py:782-799`).
  - The released copy is deleted after the marker and before any child (`runner.py:811-812`).
  - The first `_start_worker` is at `runner.py:1011-1012`.
- The pipe is JSON only (`runner.py:217-225`), and errors carry type names only (`runner.py:1049-1050`).
- The isolation probe runs before any package import (`runner.py:347-360`, `:816-839`).
- A same-account child is refused (declared residual; separate account required).

## Claim 6: Draw integrity. Verdict: HOLDS (hashes); CANNOT-VERIFY (single-draw provenance, declared)

- The nonce comes from `secrets.token_hex(32)` (`draw.py:154`).
- Exposed-D worlds are rejected (`draw.py:57-62`, `:156`).
- draw.py, sealbox.py and `__init__.py` hash to the at-draw values (table above).
- Note: the world RNG uses `int(nonce,16) mod 2^128` (`draw.py:79`). That is 128 bits of effective entropy, adequate.
- I could not run the redraw.

---

## v11 items (FIREWALL.md:374-385)

### Deliver evidence (Addendum J option a). Verdict: HOLDS

I tried two attacks:
1. Get a world to the package without a `deliver` record.
2. Get a `deliver` record whose label claims exposure falsely in the VOID direction.

What the code does:
- Every parent-to-child message carrying world data is inside `_predict_one(i)`, after `receipts.append("deliver", ...)` (`runner.py:1015`). That covers the predict tuple (`:1020`) and every call reply (`:1048-1052`).
- `append` writes and fsyncs before it returns (`runner.py:430-444`).
- The probe and `go` messages carry only paths and no world data (`runner.py:823`, `:959`).
- A timed-out helper thread keeps the OLD pipe, so it cannot feed a restarted child (`runner.py:895`, `:818`).
- If the deliver append fails, `repair()` removes the partial line. The exception aborts with `_exposed` still at its old value, and that world was never sent (`runner.py:438-442`, `:1016`). The label is truthful.
- A chain with zero deliver records therefore proves that no world reached the package. The package's import-time code sees no hidden data.

### Bounded sends (V10-1). Verdict: PARTIAL (should-fix V11-1, V11-2; not blocks-PASS)

The predict send and every reply are bounded (`runner.py:892-911`, `:1020`, `:1052`). Two unbounded pipe operations remain after exposure. Both need raw access to the pipe from the package, which requires getting past the AST heuristic. V10-1 assumed exactly the same threat class: a child that stops reading can only be one that sends `call` without using the stub.

- **V11-1 (should-fix): the parent RECEIVE is unbounded.**
  - `ready = self._conn.poll(left)` only says that some bytes are available (`runner.py:1028`).
  - `_recv` then calls `conn.recv_bytes(64 MiB)`, which blocks until the whole announced length arrives (`runner.py:224-225`, `:1036`).
  - Scenario:
    1. World i is delivered (deliver record i written).
    2. The package writes a message header announcing 1 MiB, writes 10 bytes and sleeps.
    3. The runner blocks forever in `_recv`, holding `run.lock`.
  - Outcome:
    - No runner terminal record exists. The custodian must kill the runner and run seal-terminal, which appends a custodian abort with `deliver_records` = i+1.
    - Under Addendum J that is presumed exposed, so FORFEIT. No VOID option arises, which is why this is not blocking.
  - Fix: a watchdog that kills the child at the world deadline (EOF unblocks `recv_bytes`), or receive in the helper thread.
- **V11-2 (should-fix / doc accuracy): `_stop_worker(kill=False)` sends `["stop"]` with no deadline.**
  - The send is at `runner.py:966`. It is reached from `predict_all`'s `finally` after the last world (`runner.py:1083`).
  - A child that has left the parent's send buffer full stalls it. Example: it sent raw `call`s without reading the replies, then `done`, then slept.
  - The consequence is the same as V11-1 (hang, custodian kill, seal-terminal, FORFEIT).
  - FIREWALL.md:382 says "Every parent-to-child send ... runs with a deadline", which is not literally true.
  - Fix: `kill=True` there, or `_send_bounded`.
- Test note: `v11_send_has_deadline` runs with `fr2._proc = None` (`selftest_protocol.py`, v11_checks). The "kill unblocks the pipe" path is never exercised. The result comes from the 10 s `t.join` fallback, and the helper thread stays blocked.

### seal-terminal newline. Verdict: HOLDS (note V11-4)

- A verifying last record without its newline is kept, and one `\n` is appended (`runner.py:1227-1261`).
- The offsets are correct: `keep == len(raw)`, so `truncated == 0`.
- A torn JSON prefix cannot parse, so no partial record is kept.
- **V11-4 (note):**
  - seal-terminal splits on `b"\n"` and stops at the first blank line (`runner.py:1227-1235`).
  - `verify_receipts` reads with universal newlines and skips blank lines (`runner.py:471-474`).
  - A file with `rec0\n\nrec1\n`, or a lone `\r` between records, verifies under `verify_receipts`. seal-terminal would still truncate `rec1`.
  - The runner never writes such bytes (`runner.py:409`, `:435`), so only the custodian or runner account could plant them.
  - Fix: one parser, and refuse rather than truncate when non-canonical bytes precede the tail.

### seal-terminal liveness (lock). Verdict: HOLDS

- The runner takes `flock`/`msvcrt.locking` on `run.lock` before the marker (`runner.py:801-808`).
- It releases the lock only after a terminal record and RESULT.json exist (`runner.py:877`, `:1172`). Otherwise the OS releases it at process death.
- seal-terminal refuses while the lock is held (`runner.py:1215-1217`).
- Ordering: the lock is taken before `receipts.jsonl` exists, so seal-terminal can never see a marker whose live runner lacks the lock.
- File objects are non-inheritable and spawn does not pass them, so the child cannot inherit the lock.
- If a package child survives a runner crash, it holds no lock.
- Notes:
  - A hung live runner (V11-1/V11-2) blocks seal-terminal until the custodian kills it. There is no guidance for this.
  - The lock-refusal self-test is in-process only; cross-process behaviour follows from OS semantics.
  - A stale `.claim` still blocks a retry, as in the v10 note (`runner.py:403-405`).

### seal-terminal binding. Verdict: HOLDS

- Custody passes the designation's `run_nonce`, `spec_id` and `package_sha256` (`custody.py:245-246`).
- These are compared with the open record's `run_nonce`, `spec_id` and `package.sha256` (`runner.py:1248-1252`).
- They are the same field names the runner writes (`runner.py:735-742`), so a real run is never falsely refused.
- Note: custody `main` does not catch `runner.ChainBroken` (`custody.py:353`). A refusal is logged and then surfaces as a traceback, not as JSON. Cosmetic.
- "Custodian only" is still not enforced (v10 item 3c). Under Addendum J the custodian abort's null labels carry no VOID weight, so this remains a note.

### Carried from v10 and not addressed in v11: V11-3 (should-fix; was v10 replica-2 V10-1)

A spawn failure on restart still turns into `AssertionError` and a stale `child_world`:
1. `_spawn_probe` assigns `self._proc` and then calls `start()` (`runner.py:819-820`). `_child_world` is set only after `start()` (`:822`).
2. If `start()` raises, `predict_all`'s `finally` calls `_stop_worker()` with `kill=False` (`runner.py:1083`).
3. That sends `stop` (the child end is still open) and then calls `self._proc.join(10)` on an unstarted Process. This raises AssertionError (`runner.py:966-967`).
4. AssertionError is not in `(OSError, ValueError, EOFError)` (`runner.py:968`, `:1084`), so it replaces the real exception.
5. The abort then records `error_type: "AssertionError"` and the previous child's world.

The labels are untruthful, but the adjudication impact is nil under Addendum J: a post-exposure abort is FORFEIT, and at world 0 there are zero deliver records either way.

---

## Always-check classes

1. **Code running with secrets but not bound by hashes.**
   - v11 adds stdlib only.
   - entry's guard and binding are unchanged (`entry.py:125-172`, `:252-286`).
   - F-3P (site-packages, `.pth`) remains a declared residual.
2. **Same-account readability of secrets.** Declared residual. A separate custodian account and a separate child account are required (FIREWALL.md:209-216, 248-251).
3. **Static-audit bypasses.** The AST audit is a declared heuristic. V11-1 and V11-2 show that the pipe still partly depends on it for liveness, but not for confidentiality or verdict attribution.
4. **Git ref ambiguity and merges.** Unchanged and holds (claim 3).
5. **Unauthenticated records.** S1 (blocks-PASS). The receipts are same-account files. Their integrity rests on child isolation and on the custodian.
6. **Public fields that narrow hidden content.** `ciphertext_bytes` (declared). `n_receipts` in RESULT_SEAL shows abort progress after the seal (note). The timing channel is declared (N-1).
7. **Spoofable host or identity checks.**
   - `socket.gethostname()` (`protocol.py:581`) and the comms sender (S1) are both spoofable by the account.
   - The OS account comes from GetUserNameW/pwd (`protocol.py:222-232`).

## Declared residual risks: assessment

- **Key holder not bounded:** acceptable as declared.
- **Package is Python on M1, AST heuristic only:** acceptable only with the separate child account, which is required by the fail-closed probe.
- **Single-draw provenance:** acceptable as a custodian statement.
- **System interface exposes physics:** by design.

Missing from the list:
- A package with raw pipe access can hang a live runner after exposure (V11-1, V11-2). The outcome is FORFEIT via deliver receipts plus seal-terminal, but the list should say so.
- seal-terminal parses differently from `verify_receipts` (V11-4).

## Findings summary

| id | severity | finding | evidence |
|---|---|---|---|
| S1 | **blocks-PASS** (operator #925, declared OPEN) | protocol records and allow-list are not authenticated (client-supplied comms sender; main unprotected) | allowlist.py:37-39,95; protocol.py:461-473 |
| V11-1 | should-fix | parent `recv_bytes` after `poll` is unbounded, so a raw-pipe child can hang the runner after exposure (outcome FORFEIT, no VOID) | runner.py:224-225,1028,1036 |
| V11-2 | should-fix | `stop` send in `_stop_worker(kill=False)` has no deadline; FIREWALL.md:382 "every send" is overstated | runner.py:966,1083 |
| V11-3 | should-fix (carried v10 V10-1) | unstarted-join AssertionError masks the real error; stale `child_world` | runner.py:819-822,966-968,1083-1085 |
| V11-4 | note | seal-terminal's line parser differs from `verify_receipts` (blank line / CR), so planted bytes can truncate records the verifier accepts | runner.py:1227-1235 vs 471-474 |
| V11-5 | note | `v11_send_has_deadline` does not exercise the kill path; the lock test is in-process only | selftest_protocol.py v11_checks |
| V11-6 | note | custody `main` does not catch ChainBroken (traceback); "custodian only" not enforced | custody.py:247-248,353 |

**OVERALL: FAIL.** The only blocks-PASS item is S1, which is declared open. Every other claim holds, with the should-fix items above.
