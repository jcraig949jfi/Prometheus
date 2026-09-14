# NEM-14 -- preregistration: the instrument floor census

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Written BEFORE any instrument was classified and
committed in its own commit so the order is in git history. Commissioned
by the operator after NEMESIS-01:

> Find out how many of Prometheus's numbers are presently being
> interpreted without knowing what nothing scores.

Built from 488a9b36c in D:\Prometheus-worktrees\nemesis-adopt on branch
nemesis/nem14-floor-census-2026-09-11.

## Scope limit, stated first

This is a CENSUS, not an attack. No instrument is executed against an
adversarial population in this pass. NEMESIS-02 is selected from the
result; it is not run here. No other seat's files are modified.

## Population

    TIER 1 (audited in full)
      every tracked module under roles/<Seat>/science/ or
      roles/<Seat>/contracts/, excluding __init__.py, tests/ and test_*.
      Enumerated by INDEX TRUTH (git ls-files). Count at 488a9b36c: 53,
      across 10 seats.

    TIER 2 (audited if named)
      any instrument outside Tier 1 that is named in a
      roles/base-role/MONITORS.md row or a roles/<Seat>/STATUS.md.

    EXCLUDED, with the reason recorded: legacy modules under agents/ that
      no current seat document names. They are mostly dormant lineages;
      including them would measure 2026-03 rather than the numbers being
      interpreted now. This is a real limit on coverage and the census
      reports it rather than implying completeness.

## The four states (fixed before looking)

    F3  EXPLICIT EMPIRICAL / NULL FLOOR
        a baseline computed from a null distribution -- shuffle,
        permutation, random draw, dead-world control, constant or
        degenerate responder -- present in the instrument's own output or
        in a committed companion document beside its headline number.

    F2  ANALYTICALLY JUSTIFIED FLOOR
        a closed-form baseline with its justification stated: 1/k for k
        classes, the majority-class rate, an expected value under a
        stated model.

    F1  IMPLICIT BUT UNPUBLISHED
        the floor is computable from what is already committed, but no
        number is published beside the headline. A reader cannot tell
        from the artifact what nothing scores.

    F0  NO DEFENSIBLE BASELINE
        a headline number with no baseline published and none derivable
        without new work.

    NA  emits no headline number (plumbing, IO, schema). Excluded with a
        reason; the count of NA is reported so the denominator is visible.

## Method, in order

1. ENUMERATE by index truth only (`git ls-files`, `git show HEAD:<path>`).
   No filesystem walk decides membership or content. See the
   audit-the-auditor requirement below.
2. SCREEN automatically: extract floor-EVIDENCE LINES from each module's
   blob and its seat's companion documents by a fixed vocabulary
   (chance, baseline, null, floor, majority, random, shuffle, permutation,
   control, eligible, expected under).
3. READ each module and classify from the EVIDENCE, never from the
   keyword hit. A keyword is a pointer to a line to read, not a state.
4. Record for each instrument the seven columns the commission asks for:
   instrument, headline metric, claimed capability, published floor/null,
   cheapest known shortcut, terminal consequence, Nemesis priority.
5. Select NEMESIS-02: the highest-consequence instrument whose headline
   currently has no defensible baseline.

## Predictions, each able to lose

Q1  Among instruments that emit a headline number (Tier 1, NA excluded),
    F0 + F1 together are >= 50 per cent.
    LOSES IF < 50 per cent, which would mean the program publishes floors
    far more often than this seat expects and the census is mostly good
    news.

Q2  MY OWN SCREEN OVER-CALLS: fewer than 60 per cent of keyword-positive
    modules reach F2 or F3 on reading.
    LOSES IF >= 60 per cent, which would mean keyword presence is a
    decent proxy for a published floor and my screen is stronger than I
    credit it.

Q3  At least one instrument with a TERMINAL consequence -- it settles a
    state, gates admission, promotes, demotes or disables without a human
    in the loop -- sits at F0 or F1.
    LOSES IF every terminal instrument carries an F2/F3 floor.

Q4  RECORDED, NOT PREDICTED (already measured before this file was
    written, so it is not offered as a prediction): enumerating
    instrument-shaped modules from the FILESYSTEM in this seat's sparse
    worktree yields 40; from the INDEX, 376. A filesystem-enumerating
    auditor here sees 10.6 per cent of the population and reports the
    remainder as absent.

## Audit the auditor (operator requirement, from NEMESIS-01)

Any instrument inspection that depends on filesystem enumeration
silently inherits sparse-checkout visibility, and D-23 mandates exactly
the worktree topology that produces it. Nemesis could manufacture
ABSENCE by standing in the wrong worktree.

Therefore:
- membership and content come from `git ls-files` and `git show HEAD:`;
- the census tool ships a control that runs BOTH enumerations and FAILS
  if it is ever asked to decide membership from the filesystem;
- the divergence is reported as a first-class number, not a caveat.

## My own cheapest shortcut, declared in advance

The cheapest way to fake this census is to grep for "null" and call every
hit a published floor. That shortcut would inflate F2/F3 and produce a
reassuring answer. Q2 is the measurement of exactly that shortcut, run
against my own screen. If Q2 loses, the screen is doing real work and I
say so; if Q2 holds, the screen is a word detector and every F2/F3 in
this census rests on the hand-read, not the tool.

## Conflicts of interest

- Nemesis benefits from a frightening answer: a program full of F0
  numbers justifies this seat's existence. Q1 is written so that the
  comfortable outcome is the one that falsifies my expectation, and the
  per-instrument rows are committed so anyone can re-classify them.
- roles/Nemesis/science/cheatlib.py is in the Tier 1 population. It is
  classified by the same rule as everything else and the conflict is
  noted on its row.
- Harmonia owns 28 of the 53 Tier 1 modules. A census that lands hardest
  on one seat will look like an attack on that seat; it is not, and the
  per-seat counts are reported with the denominator beside them.

## What this census does NOT establish

- NOT that an F0 instrument is wrong. An absent floor is an absent
  BASELINE, not a false number.
- NOT that an F3 instrument is trustworthy. A published floor can itself
  be wrong, and this pass does not attack any of them.
- NOT completeness. The excluded legacy population is named above.
