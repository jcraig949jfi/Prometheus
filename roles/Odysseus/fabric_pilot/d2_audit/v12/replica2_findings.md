# Holdout D2 firewall: v12 re-audit (adversarial, independent replica)

- Audited commit: `b0763ebaa2b5fb4c9ed5b6b5817a89e698b71454`. The v12 code is `acaf14df4`, merged into it.
- Scope: FIREWALL.md section v12 (the MWO-0004 D2-1 anchor), plus a carry-forward check of claims 1-6.
- Method: static reading plus `git log`/`git show` only. I could not run code, so the self-tests and `--code-hashes`
  were **not** executed by this replica.
- Files changed by v12 (`git show --stat acaf14df4`): AUDIT_BRIEF.md, FIREWALL.md, SELFTEST_PROTOCOL.json,
  allowlist.py, entry.py, protocol.py and selftest_protocol.py. runner.py, custody.py, evidence.py, draw.py and
  sealbox.py are unchanged since v11.

## Verdict: FAIL (one blocks-PASS finding, V12-1)

Under MWO-0004 D2-2 this is an ordinary implementation defect, so one final repair and one final re-audit are allowed.

---

## V12-1 (blocks-PASS): an anchored, superseding FAIL audit can be erased by an ordinary push, and the earlier PASS governs again

**Where**
- The audit set comes only from the files present in the tree at the ref:
  - `protocol.py:582`: `all_audits = ... _proto_tree(repo, ref)`
  - `entry.py:274-275, 306`: `ls-tree` of `ref_c`
- Then an anchored record that no longer verifies is **silently ignored** instead of refused:
  - `protocol.py:583-586` uses `_is_allowlisted`, which turns every `NotAllowListed` into False (`protocol.py:495-500`);
  - `entry.py:307-309` does the same; its `_allowlisted` just `continue`s on each mismatch (`entry.py:200-206`).
- Nothing checks that every anchored AUDIT entry is still present and verifying at the ref.

**What it contradicts**
- FIREWALL.md:137 (S2): "a later FAIL supersedes a PASS".
- FIREWALL.md:414: "Any mismatch fails closed".
- MWO-0004 D2-1 (`ops/work_orders/archive/MWO-0004_2026-09-29.md:137, 142-143`): "A mismatch fails closed"; history
  mutation is accepted "only insofar as this mechanism detects it and stops execution".

**Scenario (minimal)**
1. Start state on origin/main: seal 95b31a30d, then A1, then C, then D, then A2. Each record is anchored by the custodian:
   - A1 adds `FIREWALL_AUDIT_1.json` (PASS);
   - C adds `PREDICTION_COMMITMENT.json`;
   - D adds `RUNNER_DESIGNATION.json`;
   - A2 adds `FIREWALL_AUDIT_2.json` with verdict FAIL.

   The gates now refuse with AuditNotPass. That is the `S2_later_FAIL_supersedes_PASS` case (`selftest_protocol.py:274-275`).
2. Anyone who can push to main (branch protection is off, and MWO-0004 forbids adding it) pushes ONE ordinary,
   non-force commit E, using any one of these variants:
   - (a) `git rm prometheus/cosmos/c3_holdout_D2/protocol/FIREWALL_AUDIT_2.json`;
   - (b) edit any byte of FIREWALL_AUDIT_2.json (its LF sha256 no longer matches the anchor);
   - (c) force-push main back to D.
3. The custodian or runner then runs `entry.py ...`, which fetches:
   - In (a) and (c), FIREWALL_AUDIT_2.json is not in the tree, so it is never considered.
   - In (b), it fails the anchor match and lands in `audits_ignored_not_allowlisted` (`protocol.py:586`).
   - Either way, entry's `verify()` picks FIREWALL_AUDIT_1 PASS as the governing audit (`entry.py:310-322`).
   - check_gates also passes. `_added_once` runs only for the anchored audits still present (`protocol.py:590-594`).
     The ordering S < A1 < C < D holds. The code hashes are unchanged.
   - So `check_gates(..., "DESIGNATION")` returns PASS, and release-key, the preflight and the run all proceed.
4. Result: a governing FAIL is revoked, with no refusal and no custodian action on the anchor. In variant (b) the only
   trace is a name in `audits_ignored_not_allowlisted`, which is printed by `entry.py gates` only
   (`protocol.py:711`), not by custody or the runner.

**Why it is not covered**
- The self-tests cover an unanchored audit being ignored (`selftest_protocol.py:265-266`), which is intended so that a
  stray push is only noise.
- They do not cover an ANCHORED audit that is later deleted, edited or dropped from history. The v12 anchor tests
  (`selftest_protocol.py:429-491`) check a single record only.
- The same rollback is reachable through the anchor itself by tail truncation (V12-2), but that needs the M1 account.
  Variant (a)/(b) needs only a push to main.

**Repair (small)**
- Build the audit set FROM THE ANCHOR, not from the tree.
- For every anchored AUDIT name, require all of the following, or refuse (`RecordRewritten` / `NotAllowListed`, not
  "ignored"):
  - the record exists at the ref;
  - its LF sha256 equals the anchored one;
  - the anchored commit is an ancestor of the ref and is the adding commit.
- The governing audit = the highest anchored n.
- Keep ignoring tree-only audit names that have no anchor entry at all.
- Do the same in `entry.verify()`.
- Add refusal tests for (a), (b) and (c), each with a positive control.

---

## V12-2 (should-fix): the hash chain detects accidental damage, not an adversarial writer; tail truncation is undetectable

**Where**
- `protocol.py:453-476` and `entry.py:210-232` verify only internal consistency, from genesis `0*64`.
- No head hash or entry count is published or checked anywhere.
- `_entry_hash` is an unkeyed sha256 (`protocol.py:448-450`).

**Attacks**
1. **Truncation.** Drop the last k lines. What remains is a valid chain from genesis, so every reader accepts it.
   Effects:
   - removing the anchor entry of a superseding FAIL audit gives the same rollback as V12-1;
   - removing the latest PREAUDIT_TOOL batch revives an earlier, revoked pin batch (`entry.py:327-331`).
2. **Rewrite.** Edit any entry and recompute `entry_hash`/`prev` for it and every later entry. Every reader accepts it.

FIREWALL.md:400 says "An edited, removed or reordered entry breaks the chain, and every reader then refuses". That
holds only for naive edits. The tests only edit a single commit id or swap two lines without re-chaining
(`selftest_protocol.py:469-488`).

**Severity**
- This is within the declared residual "the anchor itself is protected by the M1 account" (FIREWALL.md:418; MWO-0004
  accepts it), so it is not blocks-PASS.
- The claim text should be corrected. The cheap real fix: publish the head (n_entries, entry_hash) after each append,
  e.g. in the comms notification and in the committed KEY_RELEASED / RESULT_SEAL records, and have readers refuse a
  regression below the last published head.

## V12-3 (should-fix): the once-only records (KEY_RELEASED, REVEALED) are not anchored; against history mutation they now rest on the unchained custody log alone

**Where**
- `once_record_present` reads git only (`protocol.py:503-511`). It is called by custody at `custody.py:199` and `:304`.
- These records are never written to the anchor.
- MWO-0004 D2-1 requires confirmation for "each protocol record participating in D2".

**Scenario**
1. After a release, force-push main to the parent of the commit that added KEY_RELEASED.json. MWO-0004 now forbids
   push lockdown, and v6 had relied on branch protection for exactly this (FIREWALL.md:262).
2. All anchored records remain ancestors, so the gates pass, and `once_record_present` returns False.
3. The only remaining guard is the custody log check (`custody.py:197`). That log is plain JSONL with no chain
   (`custody.py:100-108`), editable by the same M1 account.
4. The runner's "one run per designation" check looks only under the CLI-chosen `--out-root`
   (`runner.py:1287, 1321-1323`). So a second release can lead to a second run in another out-root.

**Fix:** have custody append KEY_RELEASED / REVEALED events to the chained anchor, and refuse on either the anchor or
git.

## V12-4 (should-fix): `allowlist add` anchors whatever is on main; the custodian's authorship check is manual, after the fact, and irreversible

**Where**
- `allowlist.py:50-67` takes only `--role` and `--record`. It anchors the blob and adding commit found at the fetched
  ref. There is no `--expect-commit` or `--expect-sha256` to compare against what the author announced.
- The result is printed only AFTER the append (`allowlist.py:82-84`).
- A wrong anchor for a fixed-name record (COMMITMENT, DESIGNATION, RESULT_SEAL) can never be replaced
  (`allowlist.py:61-63`), so the protocol is stuck.

**Consequences**
- With the sender check removed (FIREWALL.md:395), nothing mechanical links a record to its author. Anyone who can push
  can commit, for example, a `FIREWALL_AUDIT_1.json` PASS with `auditor: "Odysseus"` and valid code hashes before the
  real one.
- The only defence is the custodian comparing by eye against a comms notification, and comms' sender field is
  client-supplied (the v2 finding).
- MWO-0004 accepts this root-of-trust model, so this is not blocking.

**Fix**
- Make `--expect-commit` and `--expect-sha256` mandatory, and refuse before the append on any mismatch.
- State the authorship residual explicitly in FIREWALL.md v12.

## Notes

- **N1.** No lock around read-then-append (`protocol.py:479-492`, `entry.py:235-246`). Two concurrent appends get the
  same `prev`, the chain forks, and every reader refuses permanently until the file is repaired by hand. That repair is
  itself an undetectable rewrite (V12-2).
- **N2.** A torn append (crash mid-write) leaves a non-JSON last line. Every reader refuses (`protocol.py:470-471`) and
  no repair tool exists. Fail-closed DoS.
- **N3.** The "latest pin batch" is chosen by the maximum `pinned_utc` string (`entry.py:327-330`), not by chain
  position. If M1's clock goes backwards, a new batch does not revoke an older, later-stamped one. Use chain order.
- **N4.** Divergence between the two verifiers:
  - `entry._allowlisted` accepts ANY matching candidate (`entry.py:193-206`), while `protocol._allowlisted` checks
    `cands[0]` only (`protocol.py:531`);
  - entry never checks the adding commit;
  - both trust the entry's own `path` field (`entry.py:199`, `protocol.py:533`) instead of the canonical
    `PROTO_REL/name`.

  All of these are exploitable only by an anchor writer. Use one shared rule.
- **N5.** Custody re-resolves the ref NAME after the gates:
  - `once_record_present(self.repo, self.ref, ...)` at `custody.py:199` and `:304`;
  - the manifest and ciphertext for `verify_reveal` at `custody.py:313-314`.

  It should use `g["ref_commit"]`, as `_test_decrypt` already does (`custody.py:204`).
- **N6.** CANNOT-VERIFY-FROM-REPO: the ACL of `C:/Users/jcrai/nestor_receipts/holdout_D2/ANCHOR.jsonl`. The runner
  account must be able to READ it (the runner calls check_gates, `runner.py:688-691, 1318`) and must NOT be able to
  write it. `icacls` on M1 would settle this.

---

## v12 anchor claims

| # | claim (brief v12 "what to try") | attacks tried | verdict |
|---|---|---|---|
| A | a record governs without a verifying anchor entry | (1) an unanchored higher-n PASS audit: ignored (`protocol.py:583-588`); (2) a COMMITMENT/DESIGNATION/RESULT_SEAL whose blob differs from the anchor: `_allowlisted` raises (`protocol.py:526-528, 630, 650, 670`); (3) `allowlist=False` bypass: test-only, every CLI uses DEFAULT (`custody.py:89, 343`; `runner.py:652`; `evidence.py:55-56`) | HOLDS for the record that governs; but see V12-1: a record can wrongly govern because a superseding anchored record is ignored |
| B | forge, edit, reorder or truncate the anchor undetected | (1) tail truncation: accepted; (2) edit plus re-chain: accepted; (3) naive edit or swap: refused (tested) | BROKEN (V12-2), should-fix, within the declared M1-account residual |
| C | anchored commit a non-ancestor, or not the adding commit | (1) non-ancestor for the governing record: refused (`protocol.py:536-537`); (2) not the adding commit: refused in check_gates (`protocol.py:541-542`), not checked in entry (N4); (3) a non-ancestor anchored FAIL audit after a force-push: IGNORED, not refused | BROKEN via V12-1 (blocks-PASS) |
| D | a gated step that skips re-verification | (1) every key-holding CLI calls check_gates with the DEFAULT anchor (`runner.py:688, 1318`; `custody.py:96`; `evidence.py:55`); (2) the once-only records are never verified against the anchor (V12-3); (3) entry lacks the adding-commit check (N4) | HOLDS for the four governing roles; should-fix V12-3 |

## Brief claims 1-6

1. **Opacity: HOLDS.**
   - Attacks tried:
     - manifest fields (`MANIFEST_D2.json`): there are no world identities, knobs, seeds or draw nonce. `iv_hex` is a
       public GCM IV, and `ciphertext_bytes` (the length) is a declared residual (FIREWALL.md:149-150);
     - the anchor contents, which are identifiers and hashes only (`allowlist.py:66-67`, `entry.py:350-351`);
     - runner error replies to the predictor carry the type name only (`runner.py:1050`).
   - The sha256 values of MANIFEST_D2.json and hidden_D2.enc equal the brief's values (78874e9d... and f75ba333...;
     sha256sum run on the working tree).
2. **Secrets never in git: HOLDS from the repository; the key-holder scan is CANNOT-VERIFY-FROM-REPO.**
   - `git log --all --diff-filter=A` for `*.key.hex`, `*.salt.hex`, `*plain.json`, `*hidden_D2*` and
     `*nestor_secrets*` finds only `hidden_D2.enc`.
   - hidden_D2.enc and MANIFEST_D2.json are added only in 95b31a30d.
   - No protocol/ record exists in any ref yet.
   - `firewall_check` results come from M1 only.
3. **Enforced order: BROKEN, V12-1 (blocks-PASS).**
   - The seal pin, ordering, the adding commit and the code binding hold as audited through v11 (`protocol.py:561-617`).
   - But S2 supersession can be undone by an ordinary push.
4. **Controlled reveal: HOLDS**, with should-fix V12-3.
   - custody.py is unchanged since v11.
   - Release requires the gates, the preflight, a proven key and once-only checks (`custody.py:188-225`).
   - Reveal requires the RESULT_SEAL gate and a chain and result re-check (`custody.py:283-305`).
   - The once-only guarantee now rests on the custody log alone against history mutation.
5. **Predictor isolation: HOLDS** as audited through v11 (runner.py unchanged).
   - The pipe codec is pickle-free (`runner.py:170-192`).
   - The pre-key isolation probe fails closed (`runner.py:830-839`).
   - Declared: the separate child account is required, so a same-account child always refuses.
6. **Draw integrity: HOLDS** (the redraw is CANNOT-VERIFY here: it needs the nonce, which is secret until reveal).
   - The CSPRNG nonce comes from `secrets.token_hex(32)` (`draw.py:154`).
   - The on-main sha256 values of draw.py, sealbox.py and `__init__.py` equal the manifest's `d2_src_sha256_at_draw`
     (800e0b5d..., dec9b915..., d38d3b0c...).
   - Single-draw provenance is declared.

## Checklist classes

1. **Unbound code with secrets.** v12 adds no imports. `allowlist.py` imports only stdlib and `protocol`
   (`allowlist.py:21-28`), and the pre-audit binding covers it (`entry.py:70-71`). No new finding.
2. **Same-account readability.** The anchor sits in the custodian's profile; see N6 and V12-2 (declared account
   residual).
3. **Static-audit bypasses.** Not changed by v12.
4. **Git reference ambiguity and history simplification.**
   - Shadow refs are still refused (`protocol.py:307-309`, `entry.py:267-269`).
   - `--full-history -m` is still used (`protocol.py:319`).
   - New: deletion or modification of an ANCHORED record is treated as "not anchored" (V12-1).
5. **Unauthenticated or rewritable records.** V12-1, V12-2, V12-3 and V12-4.
6. **Public fields narrowing hidden content.** No change (`ciphertext_bytes` is declared). The anchor is not public.
7. **Host or identity spoofing.** The comms-sender check is gone by decree. The authorship residual is V12-4.

## Declared residuals

- **Key holder not bounded; the account is the boundary:** acceptable as declared. It should explicitly include "can
  truncate or re-chain the anchor" (V12-2).
- **The AST audit is a heuristic:** acceptable (unchanged).
- **Single-draw provenance:** acceptable.
- **System interface exposes physics:** acceptable (by the contract's design).
- **Missing from the list:**
  - that record authorship is not authenticated by any mechanism, only by custodian judgment (V12-4);
  - that the once-only records are outside the anchor (V12-3).
- **V12-1 is NOT a residual.** It is a fail-open defect that contradicts the MWO's own acceptance condition.

## What I did not do

- I did not run `selftest_protocol` (165 checks), `selftest_D2`, `entry.py gates SEAL` or `protocol --code-hashes`,
  because this replica cannot execute code.
- The SELFTEST_PROTOCOL.json values are the custodian's, not reproduced here.
