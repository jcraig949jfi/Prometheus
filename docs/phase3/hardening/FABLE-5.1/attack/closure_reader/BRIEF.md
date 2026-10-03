# Brief to the closure reader

Sent to the first reader, resumed, after the package was revised against its report. Verbatim.

---

Closure read: the package you attacked has been revised against your 11 blockers and 46 majors; please verify closure and attack the revision. Same rules as before, restated below.

## What changed (same folder: F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\hardening\FABLE-5.1\)

- 01, 02, 03 and 00_README.md were rewritten. Document 1 now has an O column (the original design) and restates every "C lacks / B says" claim; section 6 is an as-stated allocation table; section 5 no longer calls the two counterfeits one object. Document 2 section 5 is rewritten around your order-4 simulation (the ladder is now called a retention certificate; a corrected rule; a "general point" marked ARGUED; a new proposal, composition on an unseen pair). Document 3 is rewritten around the new harness.
- harness\ is a second version: stats.py (five-way classify, equivalence, attainability computed from the verdict table), registration.py, retain1.py (new faults, a weak positive), rulers.py (G3 with a bracketing panel; inverted outcome), torture.py (whole-run comparison incl. final state; reset against a fresh runtime; restart into a used runtime at every step; G8 by equivalence with a fitted table baseline), search.py (reports are replayed; positive control computed by the gate), audits.py (kit registry read from four receipts, per claim and per setting; clause isolation), claims.py (facets with sources; kinds), ladder.py (EXPLORATORY: your order-4 world and a new unseen-pair world), meta.py (148 mutants, 44 sound cases, 11 pinned known escapes), tests (59), mutation_probe.py (55 one-line changes; it claims 54 are noticed).
- attack\ is new: your brief and your report as received, the first harness version, your scripts p04-p07, p09, p10, p11, and replay_attack.py, which replays your attack on the first version (it reports 65 of 71 broken cases passed, 12 of 12 sound cases rejected, 22 of 25 logic changes unnoticed).
- check_hardening.py is rewritten: quotes are registered with a source; statements are rebuilt from receipts and sources; tables are parsed; the sequence of all numbers in each file is pinned. It reports 50 checks, 0 failed. My own fire test of it caught 46 of 47 planted errors (the 47th was a bad pattern of mine).

## What I want, in this order

1. CLOSURE. For each of B1-B11 and M1-M46 in your report: CLOSED, PARTLY or OPEN, with file:line evidence for anything not CLOSED. Then the minors, briefly. Do not take my word for any of it: where I say "taken" or "fixed", open the file.

2. RE-ATTACK THE HARNESS. Port your 71 broken cases and 12 sound cases to the new API and run them in a scratch copy. Report: how many broken cases still PASS (list each, and say whether it is one of the 11 pinned known escapes in meta.known_escapes() or a NEW escape); how many sound cases are still rejected (list each, and say whether the rejection is defensible). Then look for new escapes and wrongly rejected sound cases in the gates that changed most: G3 (bracket), G6 (final state; reset against fresh; restart into a used runtime), G7.report (replay), G8 (equivalence, fitted table), G10.ruler (registry and receipts), G11, G12. Check each registered mutant is rejected for the reason its name says.
   - In a copy the harness finds the review receipts through the environment variable RSO_COUNTERFEIT (set it to F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\review\FABLE-5.1\counterfeit).

3. THE NEW TESTS AND THE MUTATION PROBE. Are the 55 changes in harness\mutation_probe.py a fair sample or chosen to be caught? Write at least 20 one-line logic changes of your own against the new code and report how many the 59 tests miss.

4. FIRE-TEST THE NEW CHECKER on a scratch mirror, as you did before: your 33 plants adapted to the new text, plus plants that change words and not digits (verdict words, "not built", attributions, a quote swapped for another registered quote). Report what passes. Check whether the README's description of the checker (00_README.md, section Checks) is now true.

5. NEW DEFECTS INTRODUCED BY THE REWRITE. Fairness and accuracy toward B, C and O in document 1 as rewritten (sections 1, 3, 4, 5, 7, 8, 9: every statement about what a source says or lacks); numbers that disagree between the six files and the receipts; statements in document 3 section 5 about what a gate does that the code does not do; headline and summary overclaims (including the README's ten lines and "How this pass was reviewed"). Is anything now unfair to MY first draft or to you, i.e. does the account of your findings misstate them?

6. Document 2 section 5 and document 3 section 9, first world only: are B9, B10 and M33-M38 really closed, and does the new text still claim more for the two-boundary world than your simulation supports? (A second, fresh reader is attacking the unseen-pair world and the "general point"; you may attack them too if you have time.)

## Limits on you (strict, as before)

- READ-ONLY. Do not create, edit or delete any file under F:\Prometheus-worktrees\ or F:\prometheus. Scratch files go ONLY in C:\Users\jcrai\AppData\Local\Temp\claude\F--prometheus\3815a3b9-a31a-46a9-be9d-0e7abfa3cbf8\scratchpad\verify3\ (create it; you may read your earlier scratch in ...\scratchpad\verify2\).
- Do not run in place: run_harness.py, mutation_probe.py, attack\replay_attack.py (each rewrites a receipt). Copy first and run the copy with `python -B`. check_hardening.py and the unit tests may be run in place with `python -B` (they write nothing). Do not run gauntlet.py, gauntlet2.py, gauntlet3.py or keys.py without --design.
- Do not open or list anything under docs/phase3/design/ other than docs/phase3/design/FABLE-5.1/, nor roles/Enceladus, nor roles/Epimetheus, nor anything in the Enceladus worktree other than the five files named in your first brief (README.md, REVIEW_PACKET_2026-10-01.md, VALIDATION.md, "reports\Wind tunnel charter review.md", "research_notes\Wind tunnel charter review\reviewed_findings.md").
- Every repository search must exclude holdout and nestor_secrets paths in any case: git grep ... -- <paths> ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*'. Never open a path containing "holdout" or "nestor_secrets". Never read a credential file (credentials.py, secrets.py, *.env, a repository-level keys.py; docs\phase3\review\FABLE-5.1\counterfeit\keys.py is an experiment script and is fine).
- No git command that changes anything. No network.
- Aim for about 45 minutes.

## What to return

A closure table first (one line per finding, only non-CLOSED ones with detail). Then a defect list of what is NEW or still open, blockers first, each with severity (BLOCKER, MAJOR, MINOR), file and line, what the text or code says, what you found, and the smallest fix. Then the counts: broken cases that still pass (known escape / new), sound cases still rejected, your logic changes that survive, planted errors that pass the checker. Then "Probes run" and "Checked and found sound" (short). No praise, no summary of the documents.
