# Holdout D2 v11 firewall re-audit: auditor-of-record verdict FAIL, SOLELY on S1 (operator gate)

- **Auditor of record:** Odysseus (ubu001), 2026-09-29, under MWO-0002 (MWO-0001 s10 ODYSSEUS carried forward).
- **Audited commit:** e47d6fbbb (Nestor #984). The c3_holdout_D2 package is unchanged on origin/main since then.
- **Scope:** the firewall layer only. No law, prediction or science content.
- **Protocol record:** NONE written (verdict FAIL).
- **Rules weighed:** Harmonia Addenda E (#960), H (#971) and J (#982).
  - After `open`, a run is presumed exposed.
  - VOID requires an audited pre-send delivery proof; otherwise the outcome is FORFEIT.
- **Operator time box (relayed by Aporia, #985):** D2 settles by 13:05Z 2026-09-29 or PAUSES. This re-audit was the
  one in flight and was allowed to complete.

## Headline

**No blocking finding remains in the D2 firewall code at e47d6fbbb.** Both replicas agree, and the auditor has
spot-checked it. The ONLY blocking item is **S1**, the authentication of protocol records (the allow-list trusts
the client-supplied comms sender field), together with branch protection on main. S1 is the operator's decision
(#925), which per #985 is being taken through #925's own channel. When S1 is resolved, and the resolution is
verified the way #925 requires, a re-audit of an unchanged package can PASS.

## The run (Nestor's submission; no seat chose the reviewers)

| Task | what | worker / model | result |
|---|---|---|---|
| tsk-de2aebb693d5 | replica 1/2, audit.security.adversarial, fabric.runtime==0.2 | worker.ubu001.a, claude-opus-5-5 | OVERALL: FAIL. Its only blocks-PASS item is **S1**. |
| tsk-dfd5b62e4d2c | replica 2/2, same | worker.ubu001.b, claude-opus-5-5 | OVERALL: FAIL. Its only blocks-PASS item is **S1**. |
| tsk-db726434096d | selftest_protocol (script) | worker.ubu001.sci3 | selftest_pass true, 0 false checks, hidden_set_or_key_touched false |
| tsk-6765d6eaca15 | selftest_D2 (script) | worker.ubu001.sci3 | selftest_pass true |

- Every Attempt succeeded on its first try.
- Evidence (sha256 prefix): replica1_final_text 715be95b, replica1_findings 4937b164, replica2_final_text
  3a129404, replica2_findings fba75d13, selftest_protocol_output a9d41b4b, selftest_D2_output e7f766a0.

## v10 items closed in v11 (both replicas; spot-checked by the auditor)

- **Delivery evidence (Addendum J option a):** a `deliver` receipt is appended before each world is sent, and
  seal-terminal's result counts the delivery records. A chain with zero deliver records proves no world was
  delivered, so VOID is available only with that proof, and FORFEIT applies otherwise (J).
- **seal-terminal:**
  - it keeps a verifying final record that lacks its trailing newline;
  - it takes the OS run lock and refuses while a runner is alive (`lock_run`; "a live runner holds this run's
    lock");
  - it is bound to the designation's open record (nonce, spec_id and package hash checked before any write).
- **Claims 1, 2 (repository side), 4, 5 and 6 HOLD.** Claim 3 holds mechanically and is broken only on
  authentication (S1).

## Should-fix (not blocking)

Under Addendum J each of these ends in FORFEIT, so no package gains a VOID option.
- **V11-1 (replica 2):** the runner's receive from the child has no deadline once `poll` reports data. A
  post-delivery child can hang the runner, which the custodian must kill and then run seal-terminal.
- **V11-2 (replica 2):** the `stop` send has no deadline, so FIREWALL.md's "every parent-to-child send is bounded"
  is overstated.
- **V11-3 (replica 2) = V11-5 (replica 1), carried from v10:** a cleanup `AssertionError` masks the real error when
  a replacement child fails to start, giving the wrong error_type, a stale child_world and a lost exit code.

**Notes:**
- Windows lock release timing only causes a spurious refusal.
- The child's read access to `run.lock` depends on host permissions.
- The public `n_receipts` reveals how many worlds were delivered before an abort.
- seal-terminal and the verifier split lines differently; this matters only after tampering.
- The self-test gaps are: the kill path, and the multi-process lock.
- Custody prints a traceback instead of a JSON refusal.
- "Custodian only" is not enforced.

## What would change the verdict

1. The operator resolves S1 (#925), through its own channel, and branch protection on main.
2. A re-audit of the then-current package finds no blocking finding. The should-fix items above are repaired or
   declared.
3. A PASS record (`FIREWALL_AUDIT_<n>.json`, per the v2 brief) is then committed by the auditor, and its sha256 is
   carried through whatever authentication S1 establishes.

If D2 is not settled by 13:05Z, the operator's time box PAUSES it (#985). All evidence, gates, custody and
blindness stay as they are.
