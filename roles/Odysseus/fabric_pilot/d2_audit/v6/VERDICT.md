# Holdout D2 v6 firewall re-audit: auditor-of-record verdict FAIL

- **Auditor of record:** Odysseus (ubu001), 2026-09-29, under MWO-0001.
- **Audited commit:** 7c7b0b836 (Nestor #958). The c3_holdout_D2 package is unchanged on origin/main since then.
- **Scope:** the firewall layer only. No law, prediction or science content.
- **Protocol record:** NONE written.

## The run (Nestor's submission; no seat chose the reviewers)

| Task | what | worker / model | result |
|---|---|---|---|
| tsk-76beeeeab3ae | replica 1/2, audit.security.adversarial, fabric.runtime==0.2 | worker.ubu001, claude-opus-5-5 | **OVERALL: FAIL** |
| tsk-8dd16e12e036 | replica 2/2, same | worker.ubu001, claude-opus-5-5 (2nd attempt; the 1st was lost to DEF-ODY-011, 2nd occurrence) | **OVERALL: FAIL** |
| tsk-7cd8cf31e4d6 | selftest_protocol (script, max_attempts 1) | worker.ubu001.sci | **FAILED**: selftest_pass false; the single false check is `v6_account_sid_equality`. The v5 failure (`v4_DEST_key_acl_restricted`) now passes. BP-1 controls pass: a flagged package is refused with PackageAuditRefusal, a wrong hash with PackageHashMismatch. |
| tsk-66a2d7180670 | selftest_D2 (script) | worker.ubu001.sci | selftest_pass true |

Evidence (sha256 prefix): replica1_final_text d153a285, replica1_findings e0810db3, replica2_final_text 770a9ca3,
replica2_findings 32819314, selftest_protocol_output 3315d414, selftest_D2_output e7f766a0.

## Adjudication

**The replicas AGREE: FAIL.**

v6 fixed what v5 asked for most directly: package VALIDATION now runs before the key is read (`validate_package()`,
then preflight, then the key read and delete, confirmed by the auditor at `runner.py` ~609-614). But both replicas
independently find that the v5 condition, "every package check and every probe completes BEFORE the key is read",
is still not met in three places. Each lets the one-time release be consumed and then refused, which permanently
deadlocks the spec_id:

1. **Package EXTRACTION happens after the key is read** (replica 1 V6-2; replica 2 B1). Member names that pass
   validation but cannot be written (colliding paths, Windows-invalid characters, over-long names) fail on
   extraction after consumption. The v5 verdict asked for the package to be staged before the key is read.
2. **Part of the child isolation probe runs after the key is read** (replica 1 V6-3; replica 2 B3). The receipts
   read/append probe runs in `_start_worker`, after consumption. The preflight cannot cover it, because the file
   does not exist yet.
3. **The package can void an evaluation after seeing the hidden worlds** (replica 1; replica 2 B2). A package can
   deliberately crash the parent during PREDICT after probing through the System interface, so no seal and no
   result ever exist. This gives Cosmos an option to discard an unfavourable evaluation. It survives even a
   separate child account. The replica findings files carry the mechanism.

**The self-test fails at the audited commit.** `v6_account_sid_equality` is false on the Linux fabric node and is
not labelled not-applicable like the other Windows checks. This is the same pattern as v5: a Windows-only check
needs a label with a stated reason, or it needs to pass.

**Undeclared residual both replicas add:** any crash after the key is read (out of memory, power loss, full disk)
permanently deadlocks the spec_id, because resume is refused.

**Should-fix:**
- the required preflight record is self-reported JSON with no host binding;
- the runner's output folder is shared with the custodian's allow-list, custody log and lock (depends on M1
  permissions);
- exceptions other than the intervention ValueError are uncaught after predictions are sealed.

**S1** (the root of trust for protocol records) is still OPEN: an operator decision (#925).

## What would change the verdict (v7)

1. Stage, meaning extract and write every member, and run every isolation probe, including an equivalent of the
   receipts probe, BEFORE the key is read.
2. A package-initiated abort or crash after PREDICT begins must not destroy the evaluation silently. It must leave
   a sealed, attributable outcome (for example a recorded forfeit), not a deadlock. Self-tests are needed for each
   of the three paths.
3. Decide and declare the crash-after-release policy (recovery or explicit residual).
4. selftest_protocol passes on the audited commit.
5. S1: resolved by the operator's #925 choice.
