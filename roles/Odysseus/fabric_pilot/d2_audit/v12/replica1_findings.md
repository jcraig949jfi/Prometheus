# Holdout D2 firewall re-audit v12 (MWO-0004 D2-1 root of trust): adversarial findings

- Worker: task tsk-e33a0c5600d7, attempt att-1b36e9183b33 (independent replica; I did not read any other replica's output for this round).
- Audited commit: `b0763ebaa2b5fb4c9ed5b6b5817a89e698b71454`. It is on `origin/main` (`rogit branch -a --contains`), and its `prometheus/cosmos` tree is identical to `acaf14df4` (the v12 commit): `rogit diff acaf14df4 b0763ebaa -- prometheus/cosmos` is empty.
- Method: static reading plus git history only. **I could not execute any code** (the Bash call to Python was denied in this sandbox). So I did NOT:
  - run `selftest_protocol` or `selftest_D2`;
  - run `entry.py gates SEAL`;
  - compute `--code-hashes`.

  Where I say "committed selftest", I mean the values in `SELFTEST_PROTOCOL.json` at the audited commit, not a run of my own.
- Scope:
  - FIREWALL.md section v12 (`FIREWALL.md:387-428`), i.e. the append-only M1 anchor that replaces the comms allow-list.
  - Claims 1-6 of the brief, re-checked only where v12 touches them. Everything through v11 stands per the brief.

## Verdict per claim

| # | claim | verdict |
|---|---|---|
| V12-a | no record governs without a verifying anchor entry | HOLDS |
| V12-b | the anchor cannot be forged, edited, reordered or truncated undetected | BROKEN as stated (truncation; unkeyed chain). Contained by the declared M1-account residual: should-fix (doc + witness), not blocks-PASS |
| V12-c | the anchored commit must be an ancestor AND the commit that added the record | HOLDS in check_gates. entry.py omits the adding-commit check (declared, FIREWALL.md:414; harmless) |
| V12-d | no gated step skips the re-verification | HOLDS for AUDIT/COMMITMENT/DESIGNATION/RESULT_SEAL. KEY_RELEASED/REVEALED are not anchored (should-fix, MWO conformance) |
| 1 | Opacity | HOLDS (unchanged by v12; the anchor holds identifiers and hashes only) |
| 2 | Secrets never in git | HOLDS for what the repo shows. The key-holder scan is CANNOT-VERIFY-FROM-REPO |
| 3 | Enforced order | HOLDS |
| 4 | Controlled reveal | HOLDS (v12 adds anchoring of RESULT_SEAL with the adding commit) |
| 5 | Predictor isolation | HOLDS as audited through v11. The separate child account is a host capability, CANNOT-VERIFY |
| 6 | Draw integrity | HOLDS for the hash bindings. Single-draw provenance is declared |

No blocks-PASS finding.

---

## V12-a: make a record govern without a verifying anchor entry

**Attacks tried:**

1. **Unanchored later PASS/FAIL audit.** `check_gates` filters the audits through `_is_allowlisted(..., repo, ref)` before choosing the highest n (`protocol.py:582-588`). entry.py filters the same way (`entry.py:305-309`). An unanchored audit is ignored and reported (`protocol.py:586`).
2. **Anchored sha, but a record at the ref with different bytes.** The anchor lookup is keyed on the record_sha of the bytes AT the resolved commit (`protocol.py:525-528`, `entry.py:192-195`).
3. **Anchor file absent.**
   - `anchor_entries` returns `[]` (`protocol.py:462-463`), so nothing is anchored and every record is refused.
   - entry requires the anchor for gated targets (`entry.py:217-218`, `entry.py:304`).
4. **Disable switch `allowlist=False`** (`protocol.py:522-523`). No CLI path can set it:
   - custody passes the default (`custody.py:89`);
   - runner passes the default (`runner.py:652`, `runner.py:1318`);
   - evidence passes the default (`evidence.py:55-56`);
   - `protocol.main` passes the default (`protocol.py:705`).
5. **Record governs via entry but not via check_gates.** entry's filter lacks `_added_once` and the adding-commit check. Every key-holding target still calls `check_gates` with `added_commit` before acting:
   - runner: `runner.py:688`, `runner.py:1318`;
   - custody: `custody.py:196`, `custody.py:242`, `custody.py:257`, `custody.py:290`;
   - evidence: `evidence.py:55`.

**Verdict: HOLDS.**

## V12-b: forge, edit, reorder or truncate the anchor undetected

**Attacks tried:**

1. **Edit one field.** Caught: `entry_hash` is recomputed (`protocol.py:472`, `entry.py:228`). Committed selftest `S1_anchor_edited_entry_breaks_chain: true` (`SELFTEST_PROTOCOL.json:12`).
2. **Reorder two entries.** Caught through `prev` (committed `S1_anchor_reordered_breaks_chain: true`).
3. **Truncate the tail (remove the last k entries).** NOT detected. The chain has no external witness of its head. A prefix of a valid chain is itself a valid chain (`protocol.py:466-476`, `entry.py:222-232`). FIREWALL.md:400 says "An edited, removed or reordered entry breaks the chain, and every reader then refuses". That is false for removal at the tail.
   - Concrete effect 1: FIREWALL_AUDIT_1 PASS is anchored, then FIREWALL_AUDIT_2 FAIL is anchored. Dropping the last anchor line leaves a valid chain.
     - AUDIT_2 then lands in `audits_ignored_not_allowlisted` (`protocol.py:586`).
     - AUDIT_1 PASS governs again (`protocol.py:595-602`, `entry.py:310-322`).
   - Concrete effect 2: the latest PREAUDIT_TOOL pin batch is dropped. The previous, revoked batch becomes "latest" again (`entry.py:327-330`).
4. **Forge or rewrite with recomputed hashes.** The chain is an unkeyed sha256 (`protocol.py:448-450`). Any writer can rebuild a whole valid chain with arbitrary entries.

**Containment:**
- All of 3 and 4 require write access to `C:/Users/jcrai/nestor_receipts/holdout_D2/ANCHOR.jsonl` on M1.
- That is the custodian account, which can already read the key (declared residual since v4, FIREWALL.md:209-212). MWO-0004 accepts that the anchor is protected by the M1 account (FIREWALL.md:418).
- Cosmos (M2) has no path to the file from anything in the repo.
- The runner account must READ the anchor (it runs `check_gates`, `runner.py:688`). Whether it can also WRITE it depends on the ACL of the jcrai profile: **CANNOT-VERIFY-FROM-REPO**. It is settled by `icacls C:\Users\jcrai\nestor_receipts\holdout_D2` on M1, which should show no write grant for the runner or child accounts.

**Verdict: BROKEN as literally claimed; contained by the declared residual.**
- **SF-2 (should-fix):**
  - correct FIREWALL.md:400;
  - declare rollback (truncation) and re-forging by the account holder explicitly;
  - optionally witness the head, e.g. have the custodian publish `entry_hash` of each new head in a git commit, so that a rollback becomes publicly detectable.

**Also noted:**
- **N-1: no lock around read-then-append** (`protocol.py:482-491`, `entry.py:236-246`).
  - Two concurrent `add` / `pin-tools` calls chain to the same `prev`, so the chain forks. A torn final line has the same effect. Either way every reader refuses permanently.
  - Recovery needs a hand edit that cannot be told apart from tampering.
  - Fails closed. Custodian-only.
- **N-2: a JSON line that is not an object** (e.g. `[]`), or non-UTF-8 bytes, raises AttributeError or UnicodeDecodeError instead of NotAllowListed (`protocol.py:461,469-472`; `entry.py:225-228`).
  - In the runner this surfaces as a traceback rather than a refusal message.
  - It happens pre-key (gates in `prepare()`, `runner.py:688`), so nothing is consumed. Fails closed.

## V12-c: anchored commit not an ancestor, or not the adding commit

**Attacks tried:**

1. **Side-branch commit holding the same blob.** Refused by `merge-base --is-ancestor` (`protocol.py:536-537`, `entry.py:202-203`). Committed selftest `S1_anchor_non_ancestor_commit_refused: true`.
2. **Nonexistent commit.** Refused (`protocol.py:534-535`, `entry.py:200-201`). Committed `S1_anchor_nonexistent_commit_refused: true`.
3. **Ancestor commit that holds the blob but is not the adder** (e.g. a later commit, or a forged entry naming HEAD).
   - Refused by `added_commit` in check_gates for all four roles (`protocol.py:541-542`, with `602`, `630`, `650`, `670`).
   - entry.py has no such check (`entry.py:189-207`); this is declared at FIREWALL.md:414. entry only uses it to pick the binding. The gated target's `check_gates` refuses anyway, and a pre-audit tool bound by it is bound to the same code hashes. Harmless.
4. **Force-push that rebases history under an anchored record.** The anchored commit stops being an ancestor, so every gate refuses (the stop that MWO expects).
   - **N-7:** `allowlist add` then returns the stale entry for the same sha (`allowlist.py:61-65`). Fixed-name records (COMMITMENT, DESIGNATION) cannot be re-anchored.
   - Recovery exists: the custodian restores the original commits on origin/main.
   - Fails closed. Note.
5. **Anchor `path` pointing at another file with the same bytes.** `rel = e.get("path")` is not constrained to `PROTO_REL/name` (`protocol.py:533`, `entry.py:199`). This needs a forged anchor entry, so it is the account residual. Note (N-4).

**Verdict: HOLDS.**

## V12-d: a gated step that skips re-verification

**Attacks tried:**

1. **Every key-holding action.**
   - custody release-key (`custody.py:196`), seal-terminal (`custody.py:242`), result-seal (`custody.py:257`) and reveal (`custody.py:290`) all go through `check_gates`.
   - So do the runner prepare (`runner.py:688`, before the key is read; `open()` calls `prepare` first, `runner.py:774-775`, `916`) and evidence (`evidence.py:55`).
   - All run through entry.py, which fetches first (`entry.py:262-265`).
2. **Records that are NOT anchored.**
   - SEAL is pinned in the audited code (`protocol.py:55-56`, `572-573`), which is stronger than an anchor.
   - `KEY_RELEASED.json` / `REVEALED.json` are only checked for presence (`protocol.py:503-511`, `custody.py:199-200`, `304-305`) and are never anchored (`custody.py:227-234`).
   - A force-push that drops the commit adding KEY_RELEASED.json leaves the anchored AUDIT/COMMITMENT/DESIGNATION commits as ancestors, so the mechanism does NOT detect it.
   - A second release is still refused by the M1 custody log (`custody.py:197-198`), which Cosmos cannot reach. But the public git evidence of the release is erased silently, contrary to MWO D2-1: "for each protocol record participating in D2 ... a mismatch fails closed".
   - **SF-3 (should-fix):** anchor KEY_RELEASED and REVEALED on commit, and have `check_gates` require an anchored KEY_RELEASED to still be an ancestor once the anchor lists one.
3. **The pre-audit tools (firewall-check, allowlist).** They are bound by pins in the anchor (`entry.py:326-335`) and gate no protocol step. Consistent.

**Verdict: HOLDS for the four governing roles; SF-3 for the once-only records.**

## The authorship gap left by v12 (a missing residual)

**SF-1 (should-fix): `allowlist add` confirms a record by NAME only.**
- It takes no expected identity:
  - `allowlist.py:50-67`: `add(role, name)`;
  - `main` takes only `--role` and `--record`, `allowlist.py:71-75`.
- It appends irreversibly before the custodian sees the commit it anchored (`allowlist.py:66`, then the print at `allowlist.py:83-84`).
- `check_gates` never checks the audit's `auditor` field (`protocol.py:598-602`, `618`).
- Branch protection is off by MWO-0004, and comms is notification only.
- Result: whoever first gets a blob under `FIREWALL_AUDIT_<n>.json` onto origin/main before the custodian runs `add` gets it anchored. That means winning the race, or force-pushing a replacement of the published commit.

**Scenario:**
1. Odysseus commits FIREWALL_AUDIT_1 (FAIL, or not yet committed).
2. Any main pusher force-pushes a FIREWALL_AUDIT_1 with `verdict: PASS` and the current code hashes.
3. The custodian runs `entry.py allowlist add --role AUDIT --record FIREWALL_AUDIT_1.json`, as the brief instructs (AUDIT_BRIEF.md:266).
4. The forged PASS is anchored. The genuine blob can never be anchored under that name (`allowlist.py:62-63`).
5. The forged PASS governs until a higher-n record is anchored.

**Why not blocks-PASS:**
- MWO-0004 D2-1 explicitly makes "published Git object identity" and custodian confirmation the root of trust, and drops sender authentication.
- The custodian can detect the swap by comparing the printed `commit` with the one Odysseus published, and recover with FIREWALL_AUDIT_2.

**What is missing:**
- FIREWALL.md v12 does not declare "integrity after confirmation, not authorship" as a residual.
- The tool does not mechanise the comparison.

**Fix:**
- require `--expect-commit C --expect-sha256 H` (the values the author published), and refuse on mismatch before appending;
- for AUDIT, require `auditor == "Odysseus"`;
- declare the residual.

## Claims 1-6 (brief), as far as v12 touches them

1. **Opacity: HOLDS.**
   - MANIFEST_D2.json fields: no world, knob, seed or nonce (`MANIFEST_D2.json:1-36`). The IV is public by design.
   - `ciphertext_bytes` reveals the plaintext length, which is declared (FIREWALL.md:149-150).
   - Anchor entries hold role, record, path, sha256, commit and utc only (`allowlist.py:66-67`, `entry.py:350-351`), and live on M1.
2. **Secrets never in git: HOLDS for the repository.**
   - `rogit log --all --name-only -- prometheus/cosmos/c3_holdout_D2` lists no `*.key*`, `*.salt*` or `*.plain*` file in any commit, and no file ever under `protocol/`.
   - The M1 key-holder scan is **CANNOT-VERIFY-FROM-REPO**. It is settled by the published `entry.py firewall-check` booleans.
3. **Enforced order: HOLDS.**
   - Order checks: `protocol.py:589-594`, `628-629`, `648-649`, `675-676`.
   - Added once: `protocol.py:336-360`.
   - Stale code: `protocol.py:603-617`.
   - v12 adds anchor re-verification at each step without removing any earlier check (`rogit show acaf14df4 -- protocol.py` only adds arguments).
4. **Controlled reveal: HOLDS.**
   - RESULT_SEAL is anchored with its adding commit (`protocol.py:670`).
   - Reveal re-verifies the chain, the head and the result hash (`custody.py:292-301`).
   - Minor, pre-existing: reveal re-reads the manifest by the ref NAME after the gates (`custody.py:313-314`) rather than `g["ref_commit"]`. Note only; the manifest is pinned by spec_id.
5. **Predictor isolation: HOLDS as audited through v11.**
   - v12 does not touch `runner.py` (`rogit show --stat acaf14df4`).
   - The separate child account remains a host capability.
6. **Draw integrity: HOLDS for the hash bindings.**
   - `draw.py`, `sealbox.py` and `__init__.py` were changed only in the seal commit 95b31a30d (the path log above).
   - `c3_holdout_D` and the c3 files have had no non-merge change since a56ef7787: `rogit log --full-history a56ef7787..HEAD` lists merges only.
   - Single-draw provenance is declared.

## Mandatory classes

1. **Unbound code with secrets:** no v12 change. allowlist.py and protocol.py stay in `PRE_AUDIT_FILES` / `AUDITED_FILES` (`entry.py:70-71`, `protocol.py:78-86`).
   - v12 changed both files, so any earlier pins on M1 no longer match. The custodian must re-review and re-pin (`pin-tools`) before anchoring. That is procedure, not a defect.
2. **Same-account readability:** the anchor and the secrets are both in the jcrai profile; this is the account residual (V12-b).
3. **Static-audit bypass:** not changed by v12.
4. **Git ref ambiguity / history simplification:**
   - The anchored commit is a full sha from `_added_once` (`allowlist.py:58`).
   - Shadows are refused (`protocol.py:307-309`, `entry.py:267-269`).
   - Full history includes `-m` (`protocol.py:319`).
5. **Records rewritable:**
   - V12-b: the anchor is rewritable by the account holder, undetectably for truncation.
   - SF-3: once-only records are unanchored.
6. **Public fields narrowing hidden content:** none new.
7. **Host/identity spoofing:** unchanged (hostname and designation; declared). Record authorship is SF-1.

## Declared residuals: assessment

- **Key holder not bounded; the anchor protected by the M1 account:** acceptable as declared. Add explicitly that the account holder can:
  - roll the anchor back (reviving a superseded PASS or a revoked pin batch);
  - re-forge the whole anchor;
  - veto a FAIL audit simply by not anchoring it (it is then only reported, `protocol.py:586`).
- **Prediction package as operator-account Python / AST heuristic:** unchanged; acceptable.
- **Single-draw provenance:** acceptable.
- **System interface exposes physics:** acceptable.
- **Missing from the list:**
  - authorship is not authenticated (SF-1);
  - anchor rollback (SF-2);
  - once-only records outside the anchor (SF-3);
  - an anchor fork or torn line is a permanent fail-closed DoS whose repair looks like tampering (N-1).

## Findings summary

| id | severity | summary | evidence |
|---|---|---|---|
| SF-1 | should-fix | `allowlist add` anchors by name with no expected commit or sha; the auditor field is unchecked; irreversible append before comparison; authorship residual undeclared | allowlist.py:50-84; protocol.py:598-618; AUDIT_BRIEF.md:266 |
| SF-2 | should-fix | tail truncation and unkeyed re-forging are undetected; FIREWALL.md:400 overclaims; rollback revives a superseded PASS or revoked pins | protocol.py:448-476; entry.py:222-232, 327-330 |
| SF-3 | should-fix | KEY_RELEASED / REVEALED are not anchored; a force-push removing them is not detected (the M1 custody log still blocks a second release) | protocol.py:503-511; custody.py:197-200, 227-234 |
| N-1 | note | no lock on anchor append; a fork or torn line causes a permanent refusal | protocol.py:479-492; entry.py:235-246 |
| N-2 | note | a non-object JSON line or non-UTF-8 bytes give a traceback instead of NotAllowListed (pre-key, fails closed) | protocol.py:461-472; entry.py:215-228 |
| N-3 | note | entry.py lacks the adding-commit / added-once check (declared; check_gates covers it) | entry.py:189-207; FIREWALL.md:414 |
| N-4 | note | anchor `path` is unconstrained (needs a forged entry) | protocol.py:533; entry.py:199 |
| N-5 | note | pin batch chosen by the `pinned_utc` string, not chain order | entry.py:327-330 |
| N-7 | note | after a detected rewrite the fixed-name records cannot be re-anchored; recovery is by restoring history | allowlist.py:61-65 |

**No blocks-PASS finding.**
- The v12 mechanism does what MWO-0004 D2-1 specifies: it checks existence, ancestry, the blob at the commit, and the chain, it also checks the adding commit, and it fails closed.
- Runtime confirmation (the selftests, and `entry.py gates SEAL` refusing on the real repository) was NOT performed by me. It must come from the runs on M1 / Fabric.

OVERALL: PASS (conditional on the self-tests re-running green; SF-1..SF-3 should be fixed or declared before the custodian anchors FIREWALL_AUDIT_1)
