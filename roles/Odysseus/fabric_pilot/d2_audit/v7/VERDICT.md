# Holdout D2 v7 firewall re-audit: auditor-of-record verdict FAIL

- **Auditor of record:** Odysseus (ubu001), 2026-09-29, under MWO-0002 (MWO-0001 s10 ODYSSEUS carried forward).
- **Audited commit:** e4efb487e (Nestor #962). The c3_holdout_D2 package is unchanged on origin/main since then.
- **Scope:** the firewall layer only. No law, prediction or science content.
- **Protocol record:** NONE written.
- **Rule weighed:** Harmonia's pre-exposure adjudication rule (#960; Addendum E @9f6abdce6): a consumed release
  without a result seal is FORFEIT; an infrastructure crash is VOID.

## The run (Nestor's submission; no seat chose the reviewers)

| Task | what | worker / model | result |
|---|---|---|---|
| tsk-24ad3df260b9 | replica 1/2, audit.security.adversarial, fabric.runtime==0.2 | worker.ubu001, claude-opus-5-5 | **OVERALL: FAIL**: blocking V7-A, V7-B; V7-C should-fix |
| tsk-6a58313857f2 | replica 2/2, same | worker.ubu001, claude-opus-5-5 (2nd attempt; the 1st was lost to DEF-ODY-011, 3rd occurrence) | **OVERALL: FAIL**: blocking V7-1 (= V7-C) |
| tsk-f153a88314f9 | selftest_protocol (script) | worker.ubu001.sci | **selftest_pass true**, 0 false checks, 6 Windows checks labelled not-applicable |
| tsk-9e813efe1dcc | selftest_D2 (script) | worker.ubu001.sci | selftest_pass true |

Evidence (sha256 prefix): replica1_final_text 77136935, replica1_findings 8dcf221a, replica2_final_text 19a52a70,
replica2_findings 1244cf89, selftest_protocol_output c671f198, selftest_D2_output e7f766a0.

## What v7 fixed (per both replicas)

- Staging and the probes now run before the key read; a refused package consumes nothing.
- The crash policy is declared.
- The added-once, ordering, stale-code and import-guard checks HOLD.
- Controlled reveal, predictor isolation (as declared) and draw integrity HOLD.
- Both self-tests pass. The v5 and v6 self-test failures are resolved.

## Adjudication (the replicas disagree on severity; the auditor rules)

1. **V7-1 (replica 2, blocking) = V7-C (replica 1, should-fix, "PLAUSIBLE"). Ruled BLOCKS PASS.**
   - Confirmed by the auditor: in `FirewallRun.open()` the key is read, then `Receipts(..., create=True)` creates
     `receipts.jsonl` (the consumption marker), and only then is the `open` record built and appended.
   - A failure in that window makes `abort` the first record. The chain check requires `open` first, so the chain
     never verifies, and result-seal, reveal and evidence all refuse. A rerun and a second release are also
     refused.
   - The spec_id is then spent with NO sealed outcome at all: neither VOID nor FORFEIT can be recorded.
   - Ruling: v7's declared crash policy relies on recording a VOID. An environment failure (I/O at that write) is
     exactly the class that policy exists for, and here it produces an unsealable state instead. This matches the
     v5/v6 standard (release consumed with no sealed outcome), so the severity is blocking whatever the
     likelihood of a package trigger.
2. **V7-B (replica 1, blocking): package-initiated end of run without attribution. Ruled BLOCKS PASS.**
   - Confirmed by the auditor: the per-world `predict` send lies before, and outside, the `try` that guards the
     reply.
   - Replica 1 shows a package that passes the AST check can end the run at a world of its choosing. The abort
     record then carries only an exception type name, the phase and a count, with nothing attributing the end to
     the predictor.
   - Weighed against Addendum E (#960): that rule makes a package-initiated end FORFEIT and an infrastructure crash
     VOID. It protects the evaluation only if the record lets the adjudicator tell the two apart. Here it cannot,
     so a deliberate end could be recorded as VOID.
   - This is the v6 verdict condition 2 ("a sealed, attributable outcome, not ... silent") left unmet.
   - Replica 2 did not examine attribution. It did not refute it.
3. **V7-A (replica 1, blocking): an isolation-probe gap between `prepare()` and the post-release probes. OPEN, not
   independently verified by the auditor this round.** A child with read access to the runs root passes
   `prepare()`, then fails ChildNotIsolated after consumption. It is carried to the v8 re-audit.
4. **S1 (root of trust for protocol records) and branch protection:** still OPEN, operator decisions (#925; MWO-0002
   s8).

**Notes:**
- The new private-attribute AST flag can be bypassed (replica 1 V7-D).
- There is no code yet for starting the child under a separate account, so the future code needs its own audit
  (V7-E).
- Package-induced parent resource pressure can look like an infrastructure out-of-memory (V7-F). This matters for
  the Addendum E attribution too.

## What would change the verdict (v8)

1. The open record is fully built before the key read, and it is written atomically with the creation of
   `receipts.jsonl`. Alternatively, a chain that begins with `abort` can be sealed as a recorded outcome. Add a
   self-test that injects a failure at that point.
2. Every predictor I/O failure (send or receive) is attributed in the abort record (for example child exit status,
   and predictor-I/O versus runner-internal) so that Addendum E can classify FORFEIT versus VOID. Add a self-test
   in which the package closes the pipe. Consider how package-induced resource exhaustion is attributed.
3. V7-A: the prepare-time probe covers the read paths the post-release probe checks.
4. S1: resolved by the operator's #925 choice.
