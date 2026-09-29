# Holdout D2 firewall re-audit v13 (the final round under MWO-0004 D2-2): adversarial findings

- **Auditor:** independent replica, audit.security.adversarial v1. Task tsk-833387561512, attempt att-94776a780153.
- **Audited commit:** b17320e64c145bb6b10df9f9aa568614da1e85e5.
  - It merges origin/main into nestor/d2v13.
  - The D2 package and every AUDITED_FILES path are byte-identical to the v13 repair commit 2a552834d:
    `git diff --stat 2a552834d b17320e64 -- <package, prometheus/__init__.py, cosmos/__init__.py, c3/, c3_holdout_D/>`
    is empty.
- **Baseline:** v12 audited b0763ebaa. The v13 delta was read in full with `git diff b0763ebaa b17320e64`.
  - Code changes: allowlist.py +19, custody.py +4, entry.py +54, protocol.py +90, runner.py +2.
  - Tests and records: selftest_protocol.py +105, SELFTEST_PROTOCOL.json +14.
- **Method:** static reading plus read-only git only.
  - Per the skill, I ran no repository code, including the self-tests and `protocol --code-hashes`. Bash `sha256sum`
    was also denied in this sandbox.
  - Anything that needs execution is marked CANNOT-VERIFY, together with what would settle it.
- **Out of scope, untouched:** Cosmos's law, its predictions, and any science.

## 0. Scope: the v12 verdict items (FIREWALL.md v13, lines 430-443)

### V12-1: the anchor governs; an anchored record that no longer verifies is REFUSED, not skipped
**Implementation:**
- `protocol.verify_anchor_state` (protocol.py:515-543) runs for every anchor entry whose role is in
  RECORD_ROLES = AUDIT, COMMITMENT, DESIGNATION, RESULT_SEAL, KEY_RELEASED, REVEALED (protocol.py:508). For each
  entry it checks, in order:
  1. the record exists at the resolved origin/main commit (:529-531);
  2. it has the anchored LF sha256 there (:532-533);
  3. the anchored commit exists and is equal to, or an ancestor of, ref_commit (:534-537);
  4. the anchored commit holds the anchored blob (:538-541).

  Any failure raises AnchorMismatch, a GateRefusal (:511).
- `check_gates` (protocol.py:605-617) runs it after the stage checks, for every stage except SEAL, on the same
  `st["ref_commit"]`.
- entry.py has the same rule in `_verify_anchor_state` (entry.py:238-260). `verify()` calls it before any audit is
  selected or any code is bound (entry.py:341-342). It runs for every target, pre-audit tools included.

**Attacks tried:**
1. **Delete the later anchored FAIL** (FIREWALL_AUDIT_2) by an ordinary commit on main.
   - At ref_commit, `_show` returns None, so AnchorMismatch (protocol.py:529-531).
   - entry.py: `git show ref_c:rel` returns rc != 0, so REFUSED (entry.py:246-248).
   - Result: blocked in both.
2. **Edit the anchored FAIL to PASS.** The blob sha changes, so it is refused in both (protocol.py:532; entry.py:249).
   The edited file also stops matching its anchor entry, so the tree filter ignores it; it cannot become a new
   governing PASS either.
3. **Force-push main back to before the FAIL.**
   - The FAIL is missing at the tip, so it is refused (check 1).
   - A rewritten history that keeps the same FAIL blob at the tip still has to contain the anchored commit as an
     ancestor. Otherwise it is refused at protocol.py:534-537 and entry.py:251-254.
   - If the old object has been pruned, `cat-file -e` fails, which also refuses.
4. **Re-add the deleted FAIL with the identical blob** to satisfy check 1.
   - `verify_anchor_state` passes.
   - But the audit-ordering loop runs `_added_once` over every anchored audit (protocol.py:662-666). The history now
     contains a D status, so RecordRewritten (protocol.py:347-348).
   - Result: still refused, which is fail-closed.
5. **Plant an unanchored higher-n PASS** (FIREWALL_AUDIT_3.json) to outrank the anchored FAIL.
   - The tree filter keeps only anchored role/record/sha entries (protocol.py:654-658; entry.py:344-347), so it is
     ignored.
   - Because every anchored audit must be present (V12-1 check), the effective audit set equals the set of anchored
     AUDIT entries.
   - The governing audit is therefore max-n over the anchor, as v12 item 1 required.
6. **Skip the re-verification through a gated step.** Every gated caller goes through check_gates at a stage past SEAL:
   - runner.prepare (runner.py:688-691) and runner._run_cli (runner.py:1318-1319);
   - custody.release_key (custody.py:196), seal_terminal (:244), result_seal_record (:259) and reveal (:292);
   - evidence (evidence.py:55-56).

   The only stage that skips it is `gates SEAL`, which runs no key step, and entry.py has already verified the anchor
   state for it (entry.py:342).

   The pre-audit tools (firewall-check, allowlist) do not call check_gates, but they cannot skip the check either:
   entry.py applies it before binding them.
7. **Malformed anchor entries.**
   - An empty `path` refuses in protocol (`rel` falsy gives None, :529).
   - In entry.py, `git show <c>:` prints the root tree with rc 0, but its sha cannot equal the anchored sha, so it
     refuses (:249).
   - An empty commit refuses at `cat-file`.
8. **Monkeypatch or aliasing of the check.** The defect control replaces `protocol.verify_anchor_state` and shows that
   a rollback then passes (selftest_protocol.py v13_checks), so check_gates resolves the name at call time. A
   production process cannot patch it: entry.py binds protocol.py by hash (entry.py:355-359, 155, 169-173).

**Verdict: HOLDS.**

Test-coverage notes (not blocking; the code is correct by inspection):
- **N-1:** The three entry-path cases assert only that `"anchored AUDIT record"` appears in the output
  (selftest_protocol.py v13_checks, `res["v13_entry_%s..."]`). That substring appears both in entry.py's message
  (entry.py:248, 250, 253) and in protocol's AnchorMismatch text (protocol.py:531, 533, 536).
  - Without entry.py's own check, the `gates` target would still be refused later by protocol.check_gates, so these
    tests do not isolate `entry._verify_anchor_state`.
  - They would not catch its removal for the pre-audit targets (firewall-check, allowlist). Those never call
    check_gates, so entry.py's check is their only protection.
  - Fix: assert on `"REFUSED: anchored"` (entry-only wording), or run the case with target `firewall-check`.

### V12-3: KEY_RELEASED and REVEALED are anchored; one run location
**Implementation:**
- allowlist ROLES include both records (allowlist.py:34-37).
- custody refuses when `protocol.anchored_role(..., "KEY_RELEASED"/"REVEALED")` is true (custody.py:199-200,
  306-307). This happens after the gates and before the key read (:205) and the secrets copy (:311-312).
- The runner refuses any `--out-root` other than RUN_OUT_ROOT (runner.py:1321-1322; DEFAULT_OUT_ROOT =
  protocol.RUN_OUT_ROOT, runner.py:85).

**Attacks tried:**
1. **Force-push the committed KEY_RELEASED.json away and delete the custody log**, to get a second release.
   - The anchored KEY_RELEASED is now missing, so `_gates` raises AnchorMismatch before anything else
     (protocol.py:529-531).
   - `anchored_role` would refuse as well.
2. **Point the runner at a second output root**, to evade the `receipts.jsonl` consumption marker.
   - Refused (runner.py:1321-1322).
   - The key is also deleted after reading (delete_key=True, runner.py:1330), and release is once-only, so a second run
     would have no key anyway.
3. **Truncate the anchor to drop the KEY_RELEASED entry.** This needs the M1 custodian account, which is the declared
   residual. The committed record (custody.py:201) and the custody log (:197) still refuse independently.
4. **Refuse after consuming anything.** `anchored_role` reads only the anchor, and a broken chain raises NotAllowListed,
   a GateRefusal. It is caught at custody.py:213, which unlinks the lock and logs the refusal before the key is read.

**Verdict: HOLDS.**

Note:
- **N-2:** `v13_anchored_key_release_refuses_second_release` commits KEY_RELEASED.json in git (`r.put`). The
  `once_record_present` check (custody.py:201) therefore refuses on its own, and the test passes even without the new
  `anchored_role` line.
  - The new line is also effectively redundant: an anchored KEY_RELEASED that git has "forgotten" is already refused by
    `verify_anchor_state` inside `_gates`.
  - Harmless defence in depth. It is not independently tested.

### V12-4: `allowlist add` requires --expect-commit and --expect-sha256
**Implementation:** allowlist.py:90-92 refuses unless all four arguments are present. The adding commit from
`_added_once` must equal `expect_commit` exactly (full string, :63-64), and the LF sha must equal the lower-cased
`expect_sha256` (:65-66). Both checks run before the once-only check and the append (:67-73).

**Attacks tried:**
1. **Race a fixed-name record onto main first.**
   - The custodian passes the author's published commit and sha.
   - A squatted record has a different adding commit and sha, so it is refused.
   - A squatted FIREWALL_AUDIT_1 also blocks the real auditor from adding the same name. `_added_once` would see two
     adds or a modify, and the auditor would move to `_2`. The squatter's file stays unanchored and is ignored. This is
     DoS only.
2. **Abbreviated or case-variant expect-commit.** The exact-string compare refuses it, which is fail-closed.
3. **Call `add()` without the expect arguments.** Only in-process tests can do this. The CLI (`main`) requires them
   (:90). The CLI is reachable only through entry.py (:84-86), which binds allowlist.py by hash.

**Verdict: HOLDS.**

### V12-2: anchor rollback detectable or precisely declared
**Implementation:**
- An edited, reordered or partially written entry breaks the chain (protocol.py:453-476; entry.py:210-232).
- Appends are serialised by an O_EXCL `<anchor>.lock` (protocol.py:484-490, 502-503; entry.py:264-270, 282-283).
- Tail truncation and a complete re-chained rewrite by the M1 custodian account are declared as undetected
  (FIREWALL.md:439). That writer can already read the key (the account residual).

**Attacks tried:**
1. **Truncate the tail.** Undetected, as declared.
2. **Rewrite the anchor with a recomputed chain.** Undetected, as declared. `_entry_hash` is an unkeyed sha256
   (protocol.py:448-450), so anyone with write access can recompute the chain.
3. **Concurrent appends.** Refused by the lock (test `v13_concurrent_append_refused`).
4. **A reader during an append.**
   - Readers take no lock.
   - A torn last line gives "not JSON" and a refusal (protocol.py:470-471; entry.py:226-227).
   - The refusal is transient and fail-closed.
5. **Crash mid-write.**
   - If the process dies after a partial `os.write`, the anchor carries a torn line permanently and every reader
     refuses.
   - A stale `.lock` blocks further appends.
   - Both are fail-closed, but recovery requires a manual rewrite, which is exactly the undetectable operation.

**Verdict: HOLDS as declared** (declared precisely, and consistent with the v4 account residual). See R-B below for
who else might be able to write the anchor.

## 1-6. The brief's standing claims (re-checked where v13 could affect them; otherwise carried)

| # | claim | attacks tried | verdict | evidence |
|---|---|---|---|---|
| 1 | Opacity | (a) Check public manifest fields for world ids, knobs, seeds or nonce: none. MANIFEST_D2.json:1-36 holds hashes, IV, sizes, versions and the draw rule text only. (b) New v13 public outputs: AnchorMismatch and EntryRefusal texts carry only role, record name and a 12-hex commit prefix (protocol.py:531-541; entry.py:248-257). Anchor entries hold role, record, path, sha256, commit and utc (allowlist.py:72-73). (c) Size side channel: `ciphertext_bytes` 17227 (MANIFEST_D2.json:5) reveals the plaintext length (17211 bytes). That is a weak aggregate, pre-existing, not new. | HOLDS (size note N-3) | as cited |
| 2 | Secrets never in git | (a) `git log --all --diff-filter=A` for `*.key.hex`, `*.salt.hex`, `*plain.json`, `*nestor_secrets*`, `*ANCHOR.jsonl` and `*custody.jsonl`: no results. (b) `git log --all --full-history -m -- .../protocol`: no protocol records exist anywhere yet. That is consistent with "no audit record exists yet" and means no pre-existing FIREWALL_AUDIT_1 would break `_added_once`. (c) The anchor is written outside the repo (protocol.py:59). The key-holder scan (firewall_check on M1) cannot be verified from the repo. | HOLDS (M1 scan: CANNOT-VERIFY; settled by Nestor's published booleans) | |
| 3 | Enforced order | (a) Seal: `git log --all --full-history -m` on hidden_D2.enc and MANIFEST_D2.json shows one non-merge add, 95b31a30d. Every other hit is a merge carrying the blob, which `_added_once` counts as n=2, not an add (protocol.py:352). SEAL_COMMIT is pinned (protocol.py:55). (b) Shadow refs: `git show-ref` has no refs/tags/origin/main, refs/heads/origin/main or refs/tags/main (checked against protocol.py:307 and entry.py:304). (c) V12-1 above: rollback, deletion and edit are now refused. (d) The order checks are unchanged (protocol.py:661-666, 700, 720, 747). | HOLDS | |
| 4 | Controlled reveal | (a) Second release or reveal: log, anchor and git each refuse (custody.py:197-202, 304-309). (b) The gates run before the key read and before the secrets copy (custody.py:196 before 205; 292 before 311). ForbiddenHost is checked at protocol.py:716-727 and custody.py:135-136. | HOLDS | |
| 5 | Predictor isolation | runner.py is unchanged except the two lines at 1321-1322 (git diff b0763ebaa). The pickle-free pipe, type-name-only errors and the spawn guard (entry.py:176-181) are as audited through v11/v12. | HOLDS (carried; unchanged code) | |
| 6 | Draw integrity | (a) draw.py, sealbox.py, medium.py and the package `__init__.py` are unchanged since the seal commit (`git diff --stat 95b31a30d b17320e64` and `git log 95b31a30d..b17320e64` are both empty), so the at-draw hashes in the manifest (MANIFEST_D2.json:11-15) still apply to main. (b) The nonce is `secrets.token_hex(32)` (draw.py:154), and exposed D worlds are rejected (draw.py:156). The RNG seed is the nonce mod 2^128 (draw.py:63), giving 128-bit effective entropy, which is sufficient. I could not recompute sha256 values here (execution denied). | HOLDS (sha recompute: CANNOT-VERIFY here; settled by `sha256sum` or `--code-hashes`) | |

## Standard classes

1. **Unbound code with secrets.**
   - `PKG_PY` (entry.py:62-63) matches the on-disk package exactly.
   - The package directory has no `__pycache__` and no `protocol/` directory.
   - `_VerifiedSourceLoader` compiles from the hashed source and never reads `.pyc` (entry.py:162-173).
   - The v13 delta adds no import.
   - HOLDS.
2. **Same-account readability.** This is the declared account residual (FIREWALL.md v4/v12). See R-B for the
   runner/child accounts and the anchor.
3. **Static-audit bypass.** The v13 delta does not touch the AST audit. Carried.
4. **Git reference ambiguity and history simplification.**
   - No shadow refs exist.
   - `--full-history -m` is used (protocol.py:319, 567).
   - Rollback is now caught by the ancestry and presence checks.
   - HOLDS.
5. **Unauthenticated records.**
   - Records are authenticated by the M1 anchor, with the published commit and sha checked at add time.
   - The anchor chain is unkeyed; see the V12-2 declaration.
   - See R-A for who is allowed to supply the expected values.
6. **Public narrowing fields.** The ciphertext size (N-3). The v13 error texts are public identifiers only.
7. **Host and identity spoofing.**
   - The host comes from `socket.gethostname()` (protocol.py:723). The account comes from the OS
     (protocol.py:224-234), and the account is SID-compared (protocol.py:256-262).
   - v13 changes none of this.
   - Carried.

## Residual risks

Declared residuals (the key holder; the package runs as Python and the AST audit is a heuristic; single-draw
provenance; physics exposed by the System interface; anchor rollback by the custodian account; S1 as resolved by
MWO-0004): all acceptable as declared.

Missing or imprecise items (none blocks PASS):
- **R-A (note; governance, not code): a FAIL supersedes only once it is anchored, and anchoring has no author
  authentication.**
  - An auditor's FAIL committed on main is ignored until the custodian runs `allowlist add` (protocol.py:654-658).
  - The expected commit and sha come from a comms post that is "notification only" (FIREWALL.md:395).
  - Supersession therefore rests on the custodian anchoring promptly and on the custodian's out-of-band judgement of
    who published the record.
  - That is inside MWO-0004's accepted root of trust, but FIREWALL.md should say it explicitly.
- **R-B (note; CANNOT-VERIFY from the repo): write access to the anchor by non-custodian accounts.**
  - RUN_OUT_ROOT (`.../nestor_receipts/holdout_D2/runs`, protocol.py:60) sits beside ANCHOR.jsonl (protocol.py:59).
  - The designated runner is a different OS account (protocol.py:718-719) that must write under `runs/`.
  - If M1's ACL on `holdout_D2/` grants that account, or the predictor child's account, inheritable write access, then
    the anchor, its lock, and custody.jsonl are writable by a non-custodian principal.
  - The child isolation probe tests secrets, receipts and file creation in `runs/` (runner.py:654-663). It does not
    test ANCHOR.jsonl or `ANCHOR.jsonl.lock`.
  - Impact is limited because git and the custody log hold independently: DoS through a planted lock, or removal of an
    anchored post-run FAIL. It is not key access.
  - Settle it with an M1 boolean: "runner account and child account cannot write ANCHOR.jsonl, ANCHOR.jsonl.lock or
    custody.jsonl". Optionally add those paths to the child write probe.
- **R-C (note; availability): any principal with push access to main can halt D2 permanently.** Deleting or rewriting
  any record (anchored or governing) leaves a D or M status in full history that `_added_once` refuses forever
  (protocol.py:347-356). This is fail-closed and consistent with MWO-0004 ("detects it and stops execution"). Declare
  it as an availability residual.
- **R-D (note):** a crash mid-append leaves a torn anchor line or a stale lock. That is fail-closed, but its repair is a
  manual rewrite. Declare it alongside V12-2.
- **R-E (doc precision):** FIREWALL.md:414 says check_gates "requires the anchored commit to be the commit that added
  the record".
  - That holds for the governing records only (protocol.py:674, 702, 722, 742).
  - It does not hold for non-governing audits or for KEY_RELEASED/REVEALED in `verify_anchor_state`.
  - It is not exploitable: add() always anchors the `_added_once` commit (allowlist.py:59, 72).

## Not verifiable here (what would settle it)

- **Self-test execution:** 179 checks plus 4 defect controls. The committed SELFTEST_PROTOCOL.json shows
  `selftest_pass: true`, `all_defect_controls_true: true`, no false checks and `hidden_set_or_key_touched: false`, but
  it is custodian-produced. Settle it with the separate Fabric script runs of selftest_protocol and selftest_D2 at
  b17320e64.
- **The `code_sha256` map** for FIREWALL_AUDIT_1.json: run
  `python -m prometheus.cosmos.c3_holdout_D2.protocol --code-hashes --ref <audited commit>`.
- **Whether b17320e64 (or 2a552834d) is on origin/main.** The local `refs/remotes/origin/main` is stale (5266cceb). A
  fresh fetch settles it.
- **M1 state:** the anchor file ACLs (R-B) and the firewall-check booleans.

## Verdicts

- V12-1: HOLDS
- V12-3: HOLDS
- V12-4: HOLDS
- V12-2: HOLDS as declared
- Claims 1-6: HOLD. Where the check needed execution (the M1 scan in claim 2; recomputing sha256 values in claim 6),
  it is CANNOT-VERIFY here.
- blocks-PASS findings: none.
- should-fix / notes: N-1, N-2, N-3, R-A to R-E.

OVERALL: PASS
