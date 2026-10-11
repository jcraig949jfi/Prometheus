# Qualified-component registry (C-016-T010)

A manifest, not a database. `entries.py` is the hand-written half. It says what each component is, who owns it, its
stage, its qualified scope, what it is NOT qualified for, its tests and evidence, known counterexamples, dependencies,
what invalidates it, and who uses it. `REGISTRY.json` is that list with every file's sha256 (LF-normalised) and the
commit pinned.

    python -m rso.registry.registry for-adapter   # what a new adapter may reuse, at which stage and scope
    python -m rso.registry.registry show NAME     # one entry in full
    python -m rso.registry.registry check         # exit 1 if any entry is REQUALIFY_REQUIRED (bytes changed,
                                                  # directly or through a dependency) or MALFORMED
    python -m rso.registry.registry build         # re-pin after a deliberate requalification (commit the result)

## Rules

- **Stages.** AUTHOR_TESTED < CHALLENGED < QUALIFIED_SCOPED. There is no global QUALIFIED; the tool refuses it.
- **Scope travels with the component.** Reusing code is not reusing its authority outside `qualified_scope`.
  - A binding qualified for flat inventories says nothing about nested ones.
  - A ruler qualified for a binary endpoint says nothing about continuous prediction error.
  - Custody records bytes, not their truth.
- **Changed bytes invalidate.** `check` flags any changed byte in a pinned file, and the flag propagates to
  dependents. Re-pinning (`build`) is a deliberate act: commit it together with the evidence that requalified the
  entry.
- **Each new engine adds itself.** A new engine onboarding (C-016 Ensorain first) adds itself to `users` of each entry
  it reuses. It adds every scope limit it hits to `not_qualified_for` or `counterexamples`, so the next adapter
  inherits the lesson.

## Initial entries (2026-10-11, pinned at 3d807d569)

| Entry | Stage | Notes |
|---|---|---|
| exec-binding | QUALIFIED_SCOPED | Flat inventories only (P-FLAT) |
| custody-keeper | QUALIFIED_SCOPED | Bytes, not truth; timing rule still lives in the Ares evaluator |
| mutation-runner | CHALLENGED | Cannot tell a behavioural kill from a freeze-hash kill |
| receipt-canonical | QUALIFIED_SCOPED | Refuses floats |
| budget-ledger | AUTHOR_TESTED | Declared estimates, not billing |
| witness-driver-ares | QUALIFIED_SCOPED | Ares W15 only; reusable as a pattern, not code |
| ruler-binary-retention | QUALIFIED_SCOPED | Binary endpoint with a known chance bound |
| stratified-holm-analysis | CHALLENGED | analyze.py trusts the runner's `discovery` field |
