# Holdout D2 v7 firewall re-audit — adversarial findings (replica)

- Audited commit: e4efb487e (package last changed at bfcd26e3c, "D2 v7").
- v7 diff scope (`git show --stat bfcd26e3c`): runner.py (+227/-81), custody.py, evidence.py, protocol.py (1 line),
  selftest_protocol.py, docs, SELFTEST_PROTOCOL.json. No other audited file changed since the v6 audit.
- Method: static reading only. No code was executed (read-only worker). Every self-test result below is taken from the
  committed JSON and is marked as such.
- Scope note: this replica reports defects at code level (which path fails, and what record it leaves). It
  deliberately gives no worked package inputs for triggering them.

## v7 focus questions

### Q1. Can a package-, argument- or environment-controlled failure consume the release WITHOUT a terminal record? — BROKEN (blocks-PASS)

**V7-1: a failure between the consumption marker and the open record leaves a chain that cannot be verified or sealed.**

`FirewallRun.open()` runs these steps in order:
1. reads the key (runner.py:677);
2. creates `receipts.jsonl` with `Receipts(..., create=True)` (runner.py:679; the file is created at runner.py:360).
   This file is the declared consumption marker (FIREWALL.md:297, runner.py:631, runner.py:1051);
3. assigns `self.receipts`;
4. builds and appends the `open` record (runner.py:681-693).

If step 4 raises, `self.receipts` is already set, so `run_all` calls `abort()` (runner.py:765-768). `abort()`
appends `abort` as record seq 0 (runner.py:744, runner.py:376), and `verify_receipts` then rejects the chain: record 0
must be kind `open` with a matching genesis (runner.py:401-403). The consequences:
- custody `result-seal` refuses: "receipt chain does not verify" (custody.py:230-232);
- reveal refuses (custody.py:264-266), and so does evidence (evidence.py:57-59);
- a rerun refuses because receipts.jsonl exists (runner.py:631, runner.py:1051);
- a second release is refused by the once-only rules.

The result is a consumed designation with no sealable terminal record, which is exactly the state v7 claims to remove
(FIREWALL.md:299).

Attempts made on this window:
- **(a) Environment and infrastructure.** Step 4 does fresh I/O that `prepare()` never exercised:
  - `sealbox.sha256_file(manifest_path)` (runner.py:683);
  - `src_sha_lf(__file__)` and `src_sha_lf(certify.py)` (runner.py:689-690);
  - `socket.gethostname()`;
  - the write and fsync (runner.py:378-381).

  An OSError at any of these lands in the window. These are not only crashes "outside the runner's control" (the
  FIREWALL.md:312 residual): they are ordinary exceptions that the code catches and then turns into an unverifiable
  chain.
- **(b) Package-controlled content.** The open body embeds the package's own `package.json` verbatim
  (`self.pkg["meta"]`, runner.py:688) and hashes it canonically (`record_hash` → `sealbox.canon_bytes`,
  runner.py:352, sealbox.py:26-27). Validation parses that metadata with `json.loads` (runner.py:488) but never runs
  it through `canon_bytes` or `record_hash` before the key read (runner.py:456-514, runner.py:629). So "the package
  metadata can be serialised into the open record" is a check that first runs AFTER the marker exists. I did not
  establish from the repository that a concrete metadata value fails there, so this trigger is PLAUSIBLE, not
  confirmed. The structural defect in the first paragraph does not depend on it.
- **(c) Test coverage.** The self-test covers only failures AFTER the open record: `fr.certify_all = boom` at
  selftest_protocol.py:1071-1085. Nothing tests the window at runner.py:679-693.

Minimal scenario: prepare() passes → the key is read → receipts.jsonl is created → building or writing the open
record raises → abort() writes `abort` as seq 0 → result-seal, reveal and evidence all refuse, a rerun refuses, a
second release refuses → the spec_id is spent with no sealed, attributable outcome.

Fix (small), either of:
- build the complete open-record body in `prepare()` (all hashes, and the canonical serialisation of `pkg["meta"]`),
  then create the file and write record 0 in one step; or
- make `abort()` able to seal a chain without an open record, and have custody accept it. Add a test that injects a
  failure at runner.py:681.

**Other paths checked (hold):**
- After the open record, every exception, including BaseException, becomes a sealed abort (runner.py:759-768). Covered
  by `v7_2_exception_after_open_is_sealed_abort` (committed JSON, true).
- Malformed child messages and failed replies become a per-world PROTOCOL_ERROR (runner.py:862-885). A hostile
  receive becomes PREDICTOR_CRASH (runner.py:857-861).
- Certify exceptions become a per-world CERTIFY_ERROR (runner.py:966-977).
- A failure of the post-key re-probe of the real receipts (runner.py:797-801) becomes a sealed abort.
- An abort whose own write fails (disk full) is the declared residual at FIREWALL.md:312. It is acceptable as
  declared.

### Q2. Does any check or probe still run after the key read and can it refuse? — PARTLY BROKEN (see V7-1)

- The pre-key refusals hold: gates, run-directory, manifest, family, package validation, staging, and the stand-in
  probe are all in `prepare()` (runner.py:602-648). Staging failures are converted to a refusal before the key
  (runner.py:633-639).
- A missing or bad key file raises at runner.py:677 before the marker exists. It is retryable (the key copy is intact
  and there is no receipts file).
- **Not held:** the open-record construction at runner.py:681-693 is effectively a check that runs after the marker.
  V7-1 above.
- **Declared, held:** the post-key probe of the real receipts (runner.py:800) can refuse, but it now ends in a sealed
  abort (FIREWALL.md:304).

### Q3. Can the package end the run without a sealed, attributable outcome? — should-fix

- A package-induced parent crash through the pipe is closed: the parent never trusts child message shapes
  (runner.py:862-885).
- **Attributability is weak (should-fix).** The abort record carries only `phase`, `error_type` and
  `n_predictions_recorded` (runner.py:744-745). There is no world index, no indication of which side raised, and no
  last child message kind. Harmonia's FORFEIT/VOID split (FIREWALL.md:286, 313) would rest on an exception type name.
  A package that can cause any parent-side exception during PREDICT gets an abort that may read as infrastructure
  (VOID) rather than package (FORFEIT). Recommendation: record the world index and a fixed provenance enum
  (`child_message`, `runner_io`, `certify`, `interrupt`) in the abort body. These are public fields only, with no knob
  content.
- **Resource exhaustion.** Filling disk or memory from the child is, with a separate child account, the declared
  crash residual (FIREWALL.md:311-315). It is acceptable as declared, with a note: attribution for these cases is a
  human judgement, and should be written down in Addendum E as such.

## Standing claims (carried forward; the v7 diff does not touch their code except as noted)

| # | claim | verdict | evidence / reasoning |
|---|---|---|---|
| 1 | Opacity | HOLDS (with the declared length residual) | sealbox.py:70-80 (AES-GCM, AAD = family hash); commitment is salted (sealbox.py:64-67); receipts carry an index plus an HMAC tag only (runner.py:704, 899); the abort record adds type names only (runner.py:744-750). `ciphertext_bytes` reveals the plaintext length (declared, FIREWALL.md:149). Attacks tried: new v7 abort/RESULT fields (type names and counts only); the PREFLIGHT record (runner.py:778-780, no secret). |
| 2 | Secrets never in git | CANNOT-VERIFY-FROM-REPO | `git log --all --stat -- prometheus/cosmos/c3_holdout_D2` shows only code, docs, manifest and ciphertext. Absence of key/salt bytes needs the key-holder scan (`entry.py firewall-check`) on M1; settled by Nestor publishing `all_clean: true` for the audited commit. |
| 3 | Enforced order | BROKEN only through S1 (declared OPEN, #925) | Records are unauthenticated at the root (the allow-list trusts a client-supplied comms sender; FIREWALL.md:156-158). Everything else holds: full-history added-once (protocol.py:334-358), ordering (protocol.py:519-524, 558, 578), the stale-code binding (protocol.py:533-547), and the entry guard (entry.py:125-172). No new v7 attack found on these. |
| 4 | Controlled reveal | HOLDS, except that V7-1 can leave nothing to reveal | custody.py:255-297 re-verifies the chain, head, result hash and nonce. v7 accepts `abort` as terminal (custody.py:233, 267; evidence.py:58). That is consistent, but it requires a verifiable chain, which V7-1 can prevent. |
| 5 | Predictor isolation | HOLDS as declared (same-account child refused; separate account is a host capability) | Pickle-free codec (runner.py:169-202); the probe runs before the package loads (runner.py:324-337); replies carry type names only (runner.py:871-872); the v7 private-attribute AST flag (runner.py:446-447) is a heuristic, and the pipe no longer depends on it. |
| 6 | Draw integrity | HOLDS (unchanged since v6; the redraw check is in verify_reveal) | draw.py and sealbox.py are not touched by bfcd26e3c. Single-draw provenance is the declared custodian statement. |

## Required classes (1-7), v7 delta
1. **Unbound code with secrets:** no new import in v7. runner.py imports only modules already bound
   (runner.py:49-77). `re` is stdlib.
2. **Same-account readability:** unchanged (declared account residual).
3. **Static-audit bypass:** the new private-attribute rule is a heuristic, and it is correctly no longer relied upon.
4. **Git ref ambiguity / history:** unchanged (protocol.py:301-311, 314-358).
5. **Unauthenticated records:** S1 is OPEN. The PREFLIGHT record is self-reported (declared, FIREWALL.md:309). I agree
   with the declaration: `prepare()` repeats every check before the key.
6. **Narrowing public fields:** the abort RESULT adds `error_type` and `abort_phase` only. The timing residual (N-1)
   still applies.
7. **Host spoofing:** unchanged (`socket.gethostname()`, protocol.py:581). This is within the same-account residual.

## Residual risks
- The declared residuals (key holder, AST heuristic, single-draw provenance, System interface physics, the
  crash-after-release policy) are acceptable as declared.
- **Missing from the list:** "an ordinary exception between creating receipts.jsonl and writing the open record spends
  the designation with no sealable record". This is not a crash outside the runner's control; it is fixable (V7-1).

## Self-tests
- The committed SELFTEST_PROTOCOL.json reports 134 checks all true, with `not_applicable_on_this_os: []`, so the M1 run
  passed.
- I could not execute either self-test. That is CANNOT-VERIFY here; a script task on the fabric node would settle it.

## Verdict
**OVERALL: FAIL**
- Blocking: V7-1.
- Open by operator decision: S1 and branch protection.
