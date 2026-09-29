# Scoring protocol (procedural detail of PREREG A2.6; written before any scoring)

- Bundles: build_scoring.py redacts ids and package-format cues and relabels
  runs X### with a key kept outside the repo (commit-reveal: key sha256 is
  logged when built). RUBRIC.md = the frozen "Outcome categories" section of
  the prereg, verbatim.
- Scorer 1 and scorer 2 are independent roles. Each role is carried by two
  fresh disposable sessions of 18 reports each (reports are long); role 1
  splits the labels in sorted order, role 2 in a seeded shuffled order, so no
  single session sees the same 18 as another. A comms-volunteered scorer, if
  one appears before scoring starts, replaces role 1.
- Scorers get SCORER_TEMPLATE.md + RUBRIC.md + redacted reports only. They are
  told not to read anything else. No cohort, prediction, effect size or
  hypothesis is visible to them.
- Disagreement on CONSEQUENTIAL between roles 1 and 2 -> a third fresh session
  scores that report alone (same template); its call decides. Category
  disagreement -> majority of the three (role 3 scores all disputed reports);
  no majority -> AMBIGUOUS, counted NOT consequential in both cohorts, with the
  opposite coding reported as a sensitivity.
- Artemis unseals the cohort mapping only after all scores are final and
  committed.
