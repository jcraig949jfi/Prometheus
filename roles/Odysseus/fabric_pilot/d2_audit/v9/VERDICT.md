# Holdout D2 v9 firewall re-audit: auditor-of-record verdict FAIL, SOLELY on S1 (operator gate)

- **Auditor of record:** Odysseus (ubu001), 2026-09-29, under MWO-0002 (MWO-0001 s10 ODYSSEUS carried forward).
- **Audited commit:** 2aa834ab1 (Nestor #975). The c3_holdout_D2 package is unchanged on origin/main since then.
- **Scope:** the firewall layer only. No law, prediction or science content.
- **Protocol record:** NONE written (verdict FAIL).
- **Rules weighed:** Harmonia Addendum E (#960) and Addendum H (#971 @65329b9c5).
  - Exposure is the first world delivered to the package; a pre-exposure end is VOID.
  - Runner attribution labels are not evidence until audited truthful; every post-exposure abort is FORFEIT.

## Headline

**No blocking finding remains in the D2 firewall CODE at 2aa834ab1.** Both replicas and the auditor's own checks
agree. The verdict is FAIL only because S1 (authentication of protocol records; allow-list trust) is still open.
S1 has been the decisive blocker since v2, and it is an operator decision (#925; MWO-0002 s8), not a code defect
Nestor can close.

## The run (Nestor's submission; no seat chose the reviewers)

| Task | what | worker / model | result |
|---|---|---|---|
| tsk-5c232d68f717 | replica 1/2, audit.security.adversarial, fabric.runtime==0.2 | worker.ubu001.a, claude-opus-5-5 | OVERALL: FAIL. Its only blocks-PASS item is **S1** (declared open). v8 blockers FIXED. Should-fix S-A, S-B, S-C. |
| tsk-fe9b89e4c15c | replica 2/2, same | worker.ubu001.b, claude-opus-5-5 | **OVERALL: PASS**, with S1 and branch protection excluded as operator decisions. Labels explicitly not certified. Should-fix A3-1..A3-3, B-1. |
| tsk-b1f9c9dd2f2e | selftest_protocol (script) | worker.ubu001.sci | selftest_pass true, 0 false checks |
| tsk-6d7bb8774903 | selftest_D2 (script) | worker.ubu001.sci | selftest_pass true |

- Every Attempt succeeded on its first try.
- Evidence (sha256 prefix): replica1_final_text 3ec1751d, replica1_findings 58cf27f1, replica2_final_text
  7e48d717, replica2_findings 70699475, selftest_protocol_output e5c2dc39, selftest_D2_output e7f766a0.

## Adjudication

1. **v8 blockers: FIXED** (both replicas; confirmed by the auditor).
   - `FirewallRun.open()` reads the key, DECRYPTS the sealed set and checks it against the manifest. On failure it
     refuses with "nothing consumed".
   - Only then does `Receipts.create_with_open` create the consumption marker, and only then is the released key
     file deleted.
   - `custody.py` test-decrypts (`_test_decrypt`) before any copy.
   - An interrupted record write is rolled back to the last complete record, so the chain stays sealable.
2. **S1: OPEN. BLOCKS PASS.** The protocol records (the audit record included) are authenticated only through the
   allow-list path, whose trust the v2-v5 verdicts found forgeable (comms sender field, repository-controlled
   database configuration), and branch protection on main is off. Only the operator's #925 choice resolves it.
3. **Should-fix before any real key release** (not blocking on their own; the replicas agree on the class):
   - **Label regression A3-1 = S-A (confirmed).** The first child start at world 0 is labelled
     `in_predictor_io=true, current_world=0` although no world has been delivered. Under Addendum H labels are not
     evidence, and exposure is established from the receipts (whether a world was delivered). So adjudication is
     unaffected, but the v9 self-test asserts the wrong label. Fix the label, for example with an explicit
     `delivered` flag.
   - **A3-2:** `child_exitcode` can come from an earlier process.
   - **A3-3:** only the direct child is killed, so labels cannot prove the package was inactive. This is a caveat
     for Harmonia, consistent with Addendum H.
   - **Residual unsealed-chain paths (S-C / B-1):**
     - the abort record's own write fails (disk full, or package-driven exhaustion through the child account);
     - an operator interrupt in the tiny window after the marker rename;
     - a second interrupt during `abort()`;
     - a RESULT.json write failure after close (plus a CLI KeyError).

     Under Addenda E/H each of these has a defined ruling: pre-exposure VOID, post-exposure FORFEIT. So none is
     outcome-less the way V7-1 was. They should nevertheless be declared as residuals, or closed with a custodian
     `seal-terminal` tool that appends a terminal record and rebuilds RESULT.json from the receipts.
   - **S-B = B-2:** FIREWALL.md says a per-world poll failure is a per-world status, but the poll is still outside
     the per-world guard. Correct the document or the code.
   - **B-3:** exclusive creation of `receipts.jsonl` was dropped in v8 (operator-only concurrent-invocation race).

## What would change the verdict

1. **The operator resolves S1 (#925)** and decides on branch protection.
2. The should-fix items above are repaired, or each is explicitly accepted as a declared residual in FIREWALL.md.
3. A re-audit of the resulting commit (both replicas; `fabric.runtime==0.2`) finds no blocking finding. A PASS
   record (`FIREWALL_AUDIT_<n>.json`) can then be committed per the v2 brief, with its sha256 carried through
   whatever authentication S1 establishes.
