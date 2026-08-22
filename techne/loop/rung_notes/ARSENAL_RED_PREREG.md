# Pre-registration: are the arsenal's red tests DEFECTS or ARTIFACTS?

Cycle 045. Written and committed **before the failure list was inspected**.

## What I already knew (disclosed)

- The `prometheus_math` suite has stood at **30 failed / 3727 passed** across cycles 041 and 044 —
  stable, reproducible, and therefore measurable. Feasibility is established by that stability, not
  assumed.
- One sampled failure mentioned `ImportError` (`test_qp.py`), and `test_viz.py` fails at import on
  a missing `matplotlib`; `test_viz.py` is excluded from the run and counted separately.
- I have **not** looked at the failure list. The run producing it is executing as this is written.

## Population and sample size

**n = every failing test in `prometheus_math/tests`** on a single full run, `test_viz.py` excluded
and reported separately. Expected n ≈ 30 from the stable prior; the actual n is whatever the run
reports and is not trimmed.

## Classification, declared before looking

Each failure is assigned exactly one label, by the **first** matching rule:

    ARTIFACT-DEPENDENCY   ImportError / ModuleNotFoundError for an optional package
    ARTIFACT-ENVIRONMENT  missing external resource — database, network, absent data file
    TEST-BUG              the test asserts something false, or guards on a wrong precondition
    DEFECT-LOGIC          product code raises an unexpected exception
    DEFECT-MATH           product code returns a mathematically wrong value

`TEST-BUG` is placed **above** the `DEFECT-*` rules deliberately, so that "the test was wrong" must
be established before I get to call anything a product defect. Cycle 043 produced exactly that case
(a property guard on a proxy), and the ordering stops me flattering myself in the other direction.

## Predictions, committed

1. **A majority will be ARTIFACT-\*.** Confidence: **moderate.** The one sample I have is an
   ImportError, and a suite that has been stably red for many cycles is more consistent with
   missing optional dependencies than with live mathematical defects nobody hit.
2. **At least one DEFECT-MATH or DEFECT-LOGIC exists.** Confidence: **moderate.** 3757 tests over
   an arsenal this size, none of it under CI, makes zero real defects unlikely.
3. **At least one TEST-BUG exists.** Confidence: **low-to-moderate.**

## Decision rule and the PREDECLARED DECISION CONSEQUENCE

Both branches change what I do; neither is diagnosis for its own sake.

- **Any DEFECT-MATH / DEFECT-LOGIC** → **fix it in `prometheus_math`** and measure the
  postcondition: that test green, and a regression check against the other ~3727. This completes
  **detect → intervene → measure**, which no cycle since 042 has done.
- **Any TEST-BUG** → fix the test, with a written justification per test for why the assertion was
  false. A test I merely find inconvenient is not a TEST-BUG.
- **All ARTIFACT-\*** → then the arsenal carries a permanently-red background of ~30, and **that is
  itself the finding**: any new regression is invisible against it, so the suite has not been a
  working instrument for as long as the reds have existed. The decision that follows (install,
  guard at import, or accept) is reported to James with the count, **not taken unilaterally**.

## The guard I am setting on myself

The tempting move is to mark failures `skip`/`xfail` and report the count reaching zero. **That is
weakening a contract to make an instrument pass, and it is forbidden.** Any test I do not genuinely
fix stays red and is reported as red. The postcondition I report is the *fixed* count, never the
*silenced* count.

## What would make me wrong

If all 30 are genuine mathematical defects, prediction 1 fails and the arsenal is in far worse
condition than I have assumed while spending five cycles auditing another role's code. That outcome
is stated here so it cannot be softened later.
