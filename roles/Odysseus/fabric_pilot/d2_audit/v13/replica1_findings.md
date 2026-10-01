# Holdout D2: v13 firewall re-audit (the FINAL round under MWO-0004 D2-2). Adversarial replica findings

- **Task / attempt:** tsk-786a631bbc11 / att-9c9c544cf557 (skill audit.security.adversarial v1).
- **Audited tree:** b17320e64 (merge of origin/main). The package's last change is 2a552834d, "D2 v13".
- **Diff base:** b0763ebaa, the v12 audited commit.
  - `rogit diff --stat b0763ebaa HEAD -- prometheus/cosmos/c3_holdout_D2` shows changes in allowlist.py, custody.py,
    entry.py, protocol.py, runner.py and selftest_protocol.py, plus docs and SELFTEST_PROTOCOL.json.
  - Audited files outside the package are unchanged: the diff for `prometheus/__init__.py`,
    `prometheus/cosmos/__init__.py`, `prometheus/cosmos/c3` and `prometheus/cosmos/c3_holdout_D` is empty.
- **Scope:** FIREWALL.md section "v13" (FIREWALL.md:430-443), which covers the v12 verdict items 1-3
  (roles/Odysseus/fabric_pilot/d2_audit/v12/VERDICT.md, "What would change the verdict").
  - Claims 1-6 were audited through v11/v12, and their code is unchanged apart from the lines below. They stand, and
    I re-checked only where v13 touches them.
  - Science and law content: out of scope, not examined.
- **Limits:** static analysis only. I could not run code: Bash is limited to read-only `rogit`. So the self-test and
  real-history results are taken from the committed `SELFTEST_PROTOCOL.json` and are CANNOT-VERIFY by execution
  here. The script replicas settle them.

---

## Item 1: V12-1. The ANCHOR governs, not the tree: a deleted, edited or rolled-back anchored record refuses

**Code**
- `protocol.verify_anchor_state` (protocol.py:515-543) loops over every anchor entry whose role is in `RECORD_ROLES`
  (protocol.py:508: AUDIT, COMMITMENT, DESIGNATION, RESULT_SEAL, KEY_RELEASED, REVEALED). It refuses with
  AnchorMismatch unless all of these hold:
  1. the anchored path exists at the resolved commit with the anchored LF sha256 (529-533);
  2. the anchored commit exists and is equal to, or an ancestor of, the resolved commit (534-537);
  3. the blob at the anchored commit matches (538-541).
- `check_gates` (605-617) runs it after `_check_gates_stages` for every stage except SEAL.
- `entry._verify_anchor_state` (entry.py:238-260) applies the same rule. `entry.verify` calls it at entry.py:342,
  before the audit filter and before any binding or import, for every target including the pre-audit ones.

**Attacks tried**
1. **Anchored PASS_1 + anchored FAIL_2; commit a deletion of FAIL_2** (the v12 scenario).
   - The stages pass: FAIL_2 is absent from `_proto_tree`, so PASS_1 governs.
   - Then `verify_anchor_state` finds `_show(ref, path)` returns None and raises AnchorMismatch (protocol.py:529-531).
   - entry refuses even earlier (entry.py:246-248).
   - Refused.
2. **Edit FAIL_2 to PASS in place.**
   - The filter drops the edited blob (`_allowlisted` sha mismatch, protocol.py:585-587).
   - The anchor check then refuses on the changed sha (532-533; entry.py:249-250).
   - Refused.
3. **Force-push origin/main back past FAIL_2's commit.**
   - The anchored commit object still exists locally, so `cat-file -e` passes, but `merge-base --is-ancestor` fails,
     and the check refuses (534-537; entry.py:251-254).
   - The fetch force-updates the remote-tracking ref (entry.py:299, default `+` refspec), so a stale ref cannot hide
     it.
   - Refused.
4. **Keep FAIL_2's bytes but make it drop out of the audit set without deleting it.**
   - Every condition under which `_is_allowlisted` (554-559 → 573-599) would drop an anchored audit is either
     identical to a condition `verify_anchor_state` refuses on, or impossible for an anchored record:
     - role, record and sha match;
     - the commit exists;
     - the commit is an ancestor;
     - the blob at the commit matches.
   - The only other route is a tree where `ls-tree` omits the file while `git show` finds it. That is impossible for
     one path in one tree.
   - Other variants all fail closed:
     - **Gitlink or symlink `protocol/` directory:** `_show` fails, so the anchor check refuses.
     - **Directory in place of the file:** `git show` prints a tree listing, the sha mismatches, and the check
       refuses.
     - **Mode change with the same blob (100644 → 120000):** it shows as an `M` in `_record_history`, so
       `_added_once` raises RecordRewritten (protocol.py:352-356).
     - **Modify then revert:** two non-merge touches, so RecordRewritten.
     - **Side-branch re-add of the same blob, merged in:** two non-merge adds, so RecordRewritten.
     - **Lower-case twin name:** `check_records_dir` refuses it (368-377).
   - No bypass found.
5. **Unanchored later PASS (FIREWALL_AUDIT_3) or a copy of PASS_1's bytes under a new name.**
   - The name differs, so it is not anchored and is ignored (protocol.py:585; entry.py:194).
   - FAIL_2 still governs, giving AuditNotPass.
6. **A gated step that skips the re-verification.**
   - Every key- or record-affecting path calls `check_gates` through DESIGNATION or RESULT_SEAL:
     - custody `release_key` (custody.py:196);
     - custody `seal_terminal` (244);
     - custody `result_seal_record` (259);
     - custody `reveal` (292);
     - evidence (evidence.py:55);
     - runner `prepare` (runner.py:688-691);
     - runner `_run_cli` (runner.py:1318).
   - entry re-verifies for every target (entry.py:342).
   - `gates SEAL` skips the protocol-side check (protocol.py:615), but it is reachable only through entry, which has
     already run `_verify_anchor_state`.
   - `pin-tools` (entry.py:376-396) does not verify anchor state. It is not a gated step: it runs no repository
     code and only appends PREAUDIT_TOOL pins, which never govern once a PASS audit exists.
   - No gated step skips.
7. **Could the new check add a refusable check after the key read** (the v6-v9 class)?
   - No. `check_gates` is called in the runner only in `prepare()` and in `_run_cli` before `FirewallRun` is built
     (runner.py:688, 1318).
   - In custody it runs before `read_hex_file` (custody.py:196 vs 205).
   - An AnchorMismatch or NotAllowListed is a GateRefusal. It is caught with the lock freed (custody.py:213-221) and
     reported by the runner CLI (runner.py:1311).
8. **Disabled anchor (`allowlist=False`).**
   - It is honoured only as a constructor or function argument used by tests (protocol.py:522, 549, 581).
   - No CLI exposes it:
     - custody.py:347 builds `Custody(ref=a.ref)`, so the default anchor is used;
     - evidence.py:102 uses the default;
     - the runner CLI passes nothing, so `FirewallRun` uses the default (runner.py:652).

**Tests** (selftest_protocol.py:1472-1525)
- Protocol-side cases:
  - control: FAIL_2 governs, giving AuditNotPass;
  - deleted, edited and rolled back, each giving AnchorMismatch;
  - defect control: with the check stubbed out, the rollback passes.
- entry.py cases: del, edit and force-push through a real bare origin, each refused with "anchored AUDIT record".
- All are true in SELFTEST_PROTOCOL.json:84-90 and 95.

**Verdict: HOLDS.**

## Item 1 (part 2): V12-3. KEY_RELEASED and REVEALED are anchored like every record

**Code**
- `allowlist.ROLES` includes both roles (allowlist.py:34-37), and `RECORD_ROLES` includes them (protocol.py:508;
  entry.py:235), so `verify_anchor_state` covers them.
- custody refuses a release or reveal when the anchor holds such a role (custody.py:199-200 and 306-307). This runs
  inside the custody lock and before the key is read.
- The runner output root is fixed (runner.py:1321-1322), after the gates and before `FirewallRun`.

**Attacks tried**
1. **A force-push that removes an anchored KEY_RELEASED.**
   - Every later gate refuses with AnchorMismatch (protocol.py:529-531).
   - So no release, run, result-seal or reveal proceeds until the history is restored.
   - If only the anchor entry were missing, custody's log (custody.py:197) and `once_record_present` (201) would
     still refuse.
   - Holds.
2. **A second run under the same designation through `--out-root <elsewhere>`.**
   - Now refused (runner.py:1321).
   - `Path` equality does not normalise `..` or aliases, so any alternative spelling is also refused. That fails
     closed.
   - Holds.
3. **Window before the custodian commits and anchors KEY_RELEASED.**
   - Nothing enforces anchoring. In that window the custody log and git still refuse a second release, and the
     released key copy is deleted by the run (FIREWALL.md v7-v9).
   - Procedure-dependent. Note N-8.

**Tests**
- `v13_key_released_anchored` and `v13_anchored_key_release_refuses_second_release` (selftest_protocol.py:1527-1537;
  JSON:82, 94).
- **Test-coverage note:** the record is also still committed, so `once_record_present` would refuse regardless. The
  test does not isolate `anchored_role` (N-2). Harmless, because `verify_anchor_state` makes an anchored-but-removed
  KEY_RELEASED refuse anyway.

**Verdict: HOLDS.**

## Item 2: V12-4. `allowlist add` requires `--expect-commit` and `--expect-sha256`

**Code**
- The CLI refuses unless all four arguments are given (allowlist.py:90-92).
- `add()` compares the adding commit from `_added_once` exactly with `expect_commit`, and compares the LF sha with the
  lower-cased `expect_sha256` (allowlist.py:63-66). Both checks run before any anchor read or append.
- This is the only production caller: `entry.py allowlist` goes through `mod.main` (entry.py:429-430).

**Attacks tried**
1. **A squatter lands `FIREWALL_AUDIT_1.json` first.**
   - The custodian runs `add` with Odysseus's posted commit and sha. The adding commit or the sha differs, so it is
     REFUSED (allowlist.py:63-66).
   - Holds. The squatted name blocks n=1, which is DoS only and fails closed; N-7.
2. **Abbreviated, upper-case or whitespace values.**
   - An abbreviated commit is refused, which fails closed.
   - An upper-case sha is normalised.
   - An upper-case commit is refused, which fails closed.
   - No acceptance path for a wrong value.
3. **Bypassing via `add(... expect_*=None)`.**
   - Only reachable by importing the module in-process, which only the test does.
   - The CLI enforces non-empty values.
4. **Record, commit and sha agree, but the post is forged** (unauthenticated comms sender).
   - That is authorship, not integrity. Under MWO-0004 D2-1, comms is notification only and the root of trust is Git
     identity + blob hash + anchor.
   - The custodian's reading of the post is the remaining human step. Out of v13 scope (operator order); noted in N-6.

**Tests**
- Wrong commit refused, wrong sha refused, matching values anchored (selftest_protocol.py:1539-1558; JSON:91-93).

**Verdict: HOLDS.**

## Item 3: anchor rollback is detected, or precisely declared

**Code and declaration**
- **Detection:** the chain check (protocol.py:453-476; entry.py:210-232) catches an edited, reordered or non-JSON
  entry.
- **Serialisation:** appends take an O_EXCL `<anchor>.lock`. The lock is taken before the chain is read and held
  through the write (protocol.py:479-503; entry.py:263-283, the same lock name).
- **Declaration:** tail truncation, or a complete re-chained rewrite, by a writer holding the M1 custodian account is
  not detected. That writer can already read the key (FIREWALL.md:439).

**Attacks tried**
1. **Truncate the last entry, for example an anchored FAIL_2.**
   - Undetected, and PASS_1 governs again. This is exactly what is declared.
   - Consistent with the standing statement that the gates are not a boundary against the key holder
     (FIREWALL.md:105-109, 209-212).
2. **A torn last line from a crash mid-append.**
   - It is not valid JSON, so NotAllowListed / REFUSED, which fails closed.
   - There is no repair tool: the custodian must fix it by hand. Note.
3. **Two concurrent appends.**
   - The second one's O_EXCL fails, so it is refused (protocol.py:485-489; test JSON:83).
   - A reader racing an append can see a partial line and refuse transiently. That fails closed.
4. **A writer that is NOT the custodian account.**
   - Is the declaration's premise ("only the custodian account can write the anchor") true on M1?
   - The chain is unkeyed. Anyone who can write `ANCHOR.jsonl` can append valid-looking entries or truncate, with no
     secret needed.
   - The designated runner account must read the anchor (`check_gates` in `prepare`) and write `RUN_OUT_ROOT`, which
     is `.../holdout_D2/runs` (protocol.py:60), a sibling of `ANCHOR.jsonl` in the same directory
     (protocol.py:59).
   - Granting that account Modify on `holdout_D2` would be a natural set-up mistake, and would give a non-key-holder
     anchor write access.
   - Nothing in code checks the anchor's ACL. The pre-key probe covers the key and the secrets (runner.py:156-158,
     654) and the receipts, but not the anchor.
   - CANNOT-VERIFY from the repository. Finding N-1 (should-fix: declare it, or check it).

**Documentation precision**
- FIREWALL.md:400 (v12) still says "An edited, **removed** or reordered entry breaks the chain". That is true only for
  a non-tail entry.
- v13 (FIREWALL.md:439) now states the tail case precisely, so this is a note (N-5).

**Verdict: HOLDS**, with the premise noted in N-1.

---

## Claims 1-6 (carried from v11/v12; re-checked only where v13 touches them)

| claim | v13 impact | verdict |
|---|---|---|
| 1 Opacity | none: no new public field. The new error texts carry record names and commit prefixes only (protocol.py:531-541; entry.py:248-258) | HOLDS (as v12) |
| 2 Secrets never in git | none: the anchor stays out of the repository (protocol.py:59) | HOLDS (as v12; key-holder booleans CANNOT-VERIFY here) |
| 3 Enforced order | strengthened by item 1. Every changed file is in AUDITED_FILES (protocol.py:78-86), so any later change makes the audit stale | HOLDS |
| 4 Controlled reveal | strengthened by V12-3 (custody.py:199, 306) | HOLDS |
| 5 Predictor isolation | runner.py changed by 2 lines (out-root check, pre-key) | HOLDS (as v12) |
| 6 Draw integrity | untouched | HOLDS (as v12) |

## Mandatory classes

1. **Unbound code with secrets.**
   - Every file v13 changed is in AUDITED_FILES and PKG_PY (protocol.py:78-86; entry.py:62-63).
   - There are no new imports: `verify_anchor_state` uses only `_show`, `_git` and `record_sha`.
   - Clean.
2. **Same-account readability.** Unchanged. The anchor-writer premise is N-1.
3. **Static-audit bypass.** Not touched by v13.
4. **Git reference ambiguity and history simplification.**
   - The new git calls use the resolved commit id and the anchored commit id.
   - `merge-base --is-ancestor` is correct across merges.
   - Replace objects are off, and grafts and shallow files are refused (protocol.py:211-221; entry.py:98-103,
     286-295).
   - An anchor-supplied `commit` beginning with `-` would be parsed as an option. That needs anchor write access,
     so it is the account residual (N-1).
5. **Records unauthenticated or rewritable.** Anchor tail truncation is declared (item 3). N-1 and N-6.
6. **Public fields narrowing hidden content.** Nothing new.
7. **Spoofable host or identity checks.** Unchanged.

## Declared residual risks

- **Key holder, account boundary, AST heuristic, single-draw provenance, System physics:** acceptable as declared
  (unchanged).
- **Anchor rollback by the custodian account (v13):** acceptable as declared, subject to N-1.

Missing from the residual list:
- **N-1:** write access to the anchor by any non-custodian account (runner, future child account, backup or sync
  agent). This is currently implied, not stated or checked.
- **N-6:**
  - A FAIL audit takes effect only when the custodian anchors it.
  - The anchor is not in the Harmonia bundle (evidence.py:62-83), so third parties cannot verify which records were
    anchored.
  - Publishing the anchor chain head in the evidence bundle, or in each record commit, would close both points.

## Findings (none blocks PASS)

| id | severity | finding | evidence |
|---|---|---|---|
| N-1 | should-fix (declaration or check) | The rollback declaration assumes only the custodian account can write `ANCHOR.jsonl`. The chain is unkeyed, the runner account needs read access to the anchor and write access to the sibling `runs/` directory, and no code checks the anchor ACL. **Scenario:** the custodian grants the runner account Modify on `holdout_D2` so it can write `runs/`. That account (not a key holder) can then truncate the anchor to drop an anchored FAIL, or append a chain-valid entry. **Fix:** check in custody or firewall-check that only the custodian account (and SYSTEM/Administrators) can write the anchor and its directory, or declare it explicitly. There is no production path today: every run fails closed at preflight until the separate accounts exist (FIREWALL.md:249, 333) | protocol.py:59-60, 453-503; runner.py:156-158, 654 |
| N-2 | note (test coverage) | The anchored-KEY_RELEASED test does not isolate `anchored_role`: the record is still committed, so `once_record_present` refuses anyway | selftest_protocol.py:1527-1537; custody.py:199-202 |
| N-3 | note | A non-object JSON anchor line (for example `1`) raises AttributeError on `e.get` instead of a clean refusal. Fails closed, before the key. Carried from v12 | protocol.py:469-472; entry.py:225-228 |
| N-4 | note | A crash while holding `ANCHOR.jsonl.lock` blocks all appends until the custodian removes it by hand (declared in the message). `lock.unlink()` in `finally` can mask the original exception if the lock is removed externally | protocol.py:484-503; entry.py:264-283 |
| N-5 | note (docs) | FIREWALL.md:400 says "removed" breaks the chain, which holds only for a non-tail entry. Two stale docstrings: allowlist.py:3-4 (four roles, no `--expect-*`), and protocol.py:29 (the comms-sender allow-list) | as cited |
| N-6 | note | A FAIL audit governs only once anchored, so its timing is at the custodian's discretion. The anchor is not exported in the evidence bundle. Authorship of a posted commit/sha rests on the custodian's reading of comms (MWO-0004: notification only) | protocol.py:654-658; evidence.py:62-83 |
| N-7 | note | Any main pusher can squat a fixed record name (for example `FIREWALL_AUDIT_1.json`). `--expect-commit` then refuses it, which fails closed. The auditor can use the next n | allowlist.py:63-66 |
| N-8 | note | Nothing forces the custodian to commit and anchor KEY_RELEASED or REVEALED. The custody log and git cover the window | custody.py:197-202, 222-226 |
| N-9 | note (pre-existing, outside v13) | `reveal` and `evidence` re-read the manifest, ciphertext and records by ref NAME after the gates, not by the resolved commit. This only affects the verify_reveal input and the bundle copies | custody.py:317-318; evidence.py:64-67 |

## Overall

- v13 implements the v12 verdict items 1-3 as specified.
- The anchor now governs in both `protocol.check_gates` and `entry.verify`, for all six record roles.
- `allowlist add` is bound to the author's published commit and sha256.
- Rollback is detected for edits, reordering and torn writes. Tail truncation by the custodian account is declared
  precisely, and is equivalent to the standing key-holder residual.
- I found no path that makes a record govern without a verifying anchor entry. None of these goes undetected: an
  anchored record deleted, edited, force-pushed away, or anchored at a non-ancestor commit.
- No gated step skips the re-verification, and no refusable check was added after the key read.
- The self-test results (179 + 4 controls) are taken from the committed JSON, not re-executed here.

**OVERALL: PASS.** Conditions:
- the script replicas confirm both self-tests green on this commit;
- N-1 is declared or checked before the first designation.
