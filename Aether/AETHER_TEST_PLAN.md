# Aether -- test plan

Currency: 2026-09-20. EMPTY. No milestone exists yet to test.

Governing loop for every future entry (operator, 2026-09-20):

    testable contract -> tests -> minimal design -> minimal code that
    passes -> review -> next increment

Rules that will apply once entries exist:
- A capability's tests are written from its stated invariant/observable
  behavior BEFORE the minimal design or code for it.
- Do not redesign around a failing test unless we explicitly decide the
  specification (AETHER_SPEC.md) is wrong; that decision is itself logged
  in AETHER_DECISIONS.md.
- Every milestone (AETH-nn) lists: the contract it tests, the test
  file(s), what a pass means, and what a fail means (per the base role's
  "no scientific claim based solely on a detector firing" -- a passing
  test is evidence the code matches the contract, not evidence the
  contract is scientifically interesting).
- Positive, negative and cheat controls are required wherever the test
  claims to detect something (emergence, a physics violation, a specific
  pattern), not just wherever convenient.

First entry will be AETH-00, defined jointly once enough design material
has been captured.
