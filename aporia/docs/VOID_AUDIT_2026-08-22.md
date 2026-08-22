# VOID AUDIT — the catalog's 500 "voids" were not a coverage gap

**Campaign B, pass 1 (of at most 3) — TERMINAL STATE: ADVANCE (campaign complete in one pass).**
Aporia P107, 2026-08-22. Script: `aporia/docs/void_audit.py`; per-row data:
`void_audit_results.json`. Branches were committed in the script's docstring before it ran.

## Result: B1 fires, and my prior claim is RETRACTED

I told the operator that "500 of 537 catalog rows have no paradigm routing," implying a
paradigm coverage gap. That inference was wrong, and the audit says so mechanically.

| quantity | count |
|---|---|
| catalog rows (actual) | **531** |
| routed (≥1 paradigm assigned) | 47 |
| unrouted | 484 |
| — of which **NOT executable** (no data binding or no finite observable) | **475** |
| — of which executable but unassigned | **9** |
| — — of those, blocked by an absent tool | 1 |
| executable rows overall | 40 |
| rows with no data binding at all | 489 |

**The dominant fact: 475 of the 484 unrouted rows are not attackable as written.** They carry
no data binding (489 rows are empty-or-placeholder) or no finite observable (473 rows carry a
placeholder `test_spec` such as "See specific test for MATH-xxxx"). The "500 voids" figure was
measuring **catalog executability**, not paradigm coverage.

**The real coverage gap is 9 rows, not 500.** Of the 40 rows that are genuinely executable,
**31 are routed — 77.5% coverage.** Paradigm coverage of attackable problems is good; it was
the catalog that was empty, not the tree set.

Corrected count note: the catalog holds **531** rows, not 537. The backlog generator's source
string `catalog_537` is a fossil, and I had been repeating 537 in briefs including the external
consult prompt. Corrected here.

## Branches that did NOT fire, and what that settles

- **B2 (genuine coverage gap)** — did not fire. Threshold was ≥20 executable-but-unassigned;
  actual is 9, spread thinly across number_theory (4), combinatorics (3),
  algebraic_number_theory (1), analytic_number_theory (1). No systematic paradigm blind spot.
- **B3 (tooling is the limiter)** — did not fire, and this is the useful negative. Exactly
  **2 rows in the entire catalog name an absent tool** (both GAP), and only **1**
  executable-unrouted row is tool-blocked. **Measured demand for Sage, Macaulay2, or a SAT
  solver is approximately zero.** Per the standing rule that tooling is installed on measured
  demand only, the audit closes the question: do not install them for the catalog's sake. If
  they are ever justified it will be by a different workload (P29's border-apolarity range
  remains the one named candidate, and it is one row).
- **B4 (catalog can't support the inference)** — did not fire in the strong sense; the
  classification derived cleanly from committed metadata. But the *spirit* of B4 is confirmed:
  the catalog cannot support coverage inferences because ~92% of it is unfilled stubs.

## What this changes

1. **The catalog is not a target source.** 491 of 531 rows are unattackable as written, and
   filling them is authoring work, not research. Targets should come from populated search
   spaces (the OEIS corpus, the tensor problem catalog, the mirror) rather than from this file.
2. **The paradigm tier is not under-covering.** Its 77.5% coverage of executable rows means the
   trees are not the bottleneck, which removes one motive for building more of them.
3. **The tooling question is answered with data instead of intuition.** No install is justified
   by this catalog.

## Campaign B checkpoint

**ADVANCE / complete.** The campaign's question — what does the unrouted mass mean — is
answered in one pass, and the answer changed what runs next (targets do not come from here).
Per the campaign discipline, B does not become a standing thread and no pass 2 is scheduled.
Continuation criterion satisfied: *a preregistered branch was discriminated* and *the result
changed what experiment should be run next*.
