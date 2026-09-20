# Aether -- specification

Currency: 2026-09-20. EMPTY. No semantics or invariants have been proposed
or frozen yet: the domain/phenomenon Aether studies has not been stated
(AETHER_OPEN_QUESTIONS.md, question 1), and per the operator's TDD
sequencing (testable contract -> tests -> minimal design -> minimal code)
a spec entry is written only once a contract for that capability exists.

Format, once entries exist: each capability gets a numbered section
(AETH-nn), stating its invariant(s)/observable behavior first, its status
(CANDIDATE or FROZEN), and a pointer to the tests in AETHER_TEST_PLAN.md
that check it. Superseded entries are annotated in place, never silently
rewritten (base-role rule: corrections are annotations beside the
original).
