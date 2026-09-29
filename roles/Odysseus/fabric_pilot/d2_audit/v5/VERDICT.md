# Holdout D2 v5 firewall re-audit: auditor-of-record verdict FAIL

- **Auditor of record:** Odysseus (ubu001), 2026-09-29, under MWO-0001.
- **Audited commit:** 57c809387 (Nestor #949). The c3_holdout_D2 package is unchanged on origin/main since then.
- **Scope:** the firewall layer only. No law, prediction or science content.
- **Protocol record:** NONE written.

## The run (Nestor's submission; no seat chose the reviewers)

| Task | what | worker / model | result |
|---|---|---|---|
| tsk-e315db41ef2e | replica 1/2, audit.security.adversarial, fabric.runtime==0.2 | worker.ubu001, claude-opus-5-5 | **OVERALL: FAIL**: blocking BP-1 |
| tsk-76b0bf1e5a78 | replica 2/2, same | worker.ubu001, claude-opus-5-5 | **OVERALL: FAIL**: blocking F1 (the same finding as BP-1) |
| tsk-f78419646fb3 | selftest_protocol (script) | worker.ubu001.sci, 3 attempts | **FAILED**: `selftest_pass false` in all three attempts; the single false check is `v4_DEST_key_acl_restricted` |
| tsk-9e65cbcac8c8 | selftest_D2 (script) | worker.ubu001.sci | selftest_pass true |

Evidence (sha256 prefix): replica1_final_text fa5bb33f, replica1_findings 51188087, replica2_final_text 1bb6208e,
replica2_findings 359c7c09, selftest_protocol_output 3290c142 (last attempt), selftest_D2_output e7f766a0.

## Adjudication

**The replicas AGREE: FAIL.**

1. **BP-1 / F1: the one-time key release can be consumed by a recoverable error. Blocks PASS.**
   - Both replicas find this independently.
   - Confirmed by the auditor: `runner.py:607` reads the released key, `:609` deletes it, and only at `:641` does
     `load_package` check the package hash, its members and the AST audit.
   - A refusal at that point (an AST flag on an innocent construct, a disallowed member, or the wrong zip path)
     happens after the key is spent.
   - A second release is then refused (KEY_RELEASED record plus the custody log), and a rerun is refused (the run
     directory exists). The spec_id is permanently deadlocked, and the declared adversary could trigger this on
     purpose.
   - `--preflight` does not validate the package, and custody does not require a preflight before release.
   - No self-test covers it.
   - **Fix (both replicas):** hash, validate, audit and stage the package, and run the receipts/isolation probes,
     BEFORE the key is read. Include the same checks in `--preflight`, and make custody require a passing
     preflight before release.
2. **The self-test fails at the audited commit. Must be explained or fixed before a PASS.**
   - `selftest_protocol` reports `selftest_pass: false` in three identical attempts on the Linux fabric node. The
     only false check is `v4_DEST_key_acl_restricted`.
   - The same check passed on this node in v4 (tsk-c889e48bc5f1). v5 changed the ACL step (B-1 repair: icacls by
     absolute system path), and the check is not in the run's `not_applicable_on_this_os` list, unlike the five
     other Windows checks.
   - Either the non-Windows ACL path regressed, or the check is Windows-only and lacks its label. The fabric's
     Linux node cannot settle which; the M1 self-test output can.
   - Hygiene note: the retries were spent on a deterministic failure (3 of 3). This is the same pattern as
     DEF-ODY-009.
3. **S1, root of trust for protocol records: still OPEN.** It is an operator decision (#925). Replica 2 (F2) and
   replica 1 (SF-3) add that `allowlist.py` takes its database host from committed repository config, so anyone
   who can push to main could redirect the allow-list lookup. That widens S1.

**v4 blockers:**
- B-1 (bare-name executables) HOLDS inside the tools, per replica 1. The documented entry command's own `python`
  lookup is noted (SF-4).
- B-2 (allowlist runs only bound code) HOLDS for code, per replica 1. Replica 2 records it as only partly repaired
  (F2, the database configuration).

**Should-fix items:**
- pins are irrevocable and per file;
- the account check compares names rather than SIDs;
- `firewall_check` git calls lack the hardening flags;
- the allow-list path is not absolute on POSIX;
- a force-push can remove the once-only records.

The full lists are in the findings files.

## What would change the verdict (v6)

1. Every package check and every probe completes BEFORE the key is read. `--preflight` covers them, and custody
   requires a passing preflight. Add a self-test proving that a refused package does not consume the release.
2. `selftest_protocol` passes on the audited commit: fix `v4_DEST_key_acl_restricted`, or label it not-applicable
   with a stated reason.
3. S1: resolved by the operator's #925 choice. It includes the allow-list's database configuration.
