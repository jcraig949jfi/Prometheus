# Techne TDD Log

Long-term audit log of test-driven-development quality across the
arsenal. Each entry: date, operation, A:authority P:property E:edge
C:composition scores (1-3 per category, see `.claude/skills/math-tdd/SKILL.md`),
and the commit that landed it.

This is the quality-history complement to ARSENAL.md (the
capability reference).

## Entries

| Date | Operation | Auth | Prop | Edge | Comp | Commit |
|---|---|---|---|---|---|---|
| 2026-04-25 | (audit pending — backfill from existing techne/lib/) | — | — | — | — | — |

---

## Backfill plan

The 21 existing Techne tools were forged before this skill existed.
Audit each retrospectively against the four-category rubric and either:
- Score and log if the existing tests cover all four (rare)
- Add missing tests and log the upgrade (most cases)
- Flag for refactor if tests are absent in any category

This backfill is itself a project (project #6 in the 1000 backlog:
"Property-based test suite for prometheus_math.number_theory").

## TDD-quality bar

A tool is "TDD-quality" iff it scores ≥ 2 in every category. The bar
for shipping new operations is TDD-quality. Existing operations may
fall below until backfilled.
