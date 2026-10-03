# Brief to the second reader

Sent to a fresh reader that had seen neither the first version nor the first report. Verbatim.

---

You are an adversarial reviewer. Your job is to find what is WRONG in a small package before it is committed. Do not validate, summarise or praise. I want a defect list. Assume the author overclaims: on this author's previous work, three review rounds each found summary sentences that said more than the evidence, and sources blamed for lacking things they contain. A first draft of THIS package did not survive its first adversarial read (another reader found 11 blocking and 46 major defects). That reader is now checking closure of its own findings. You are a second, fresh reader: attack the NEW material that nobody has attacked yet.

## What is under review (all READ-ONLY for you)

Folder: F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\hardening\FABLE-5.1\
- 01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md  (compares two reviews A and B; critiques a hardening package C)
- 02_HARDENING_DESIGN_v0.2_FABLE.md               (the author's own hardening design)
- 03_TEST_HARNESS_SPEC_FABLE.md                   (the author's own harness specification)
- 00_README.md, check_hardening.py
- harness\  (rso_harness\*.py, tests\test_harness.py, run_harness.py, mutation_probe.py, two RECEIPT_*.json, README.md)
- attack\   (the first reader's brief and report, the first harness version, its scripts, replay_attack.py)

The author is "FABLE-5.1 / seat Dionysus" (called A in the documents).

## The sources the documents talk about

- A, the author's earlier review: F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\review\FABLE-5.1\ (RESPONSE_1_REVIEW_REPORT.md, RESPONSE_2_RSO_WIND_TUNNEL_v0.1.md, RESPONSE_3_RACE_CAR_PORTFOLIO_R0-R9.md, 00_README.md, counterfeit\README.md, counterfeit\keys.py and the RECEIPT_*.json and PREREG*.md files there).
- B, a review by another model (ASTRA-6.0 / seat Enceladus): F:\Prometheus-worktrees\enceladus-rso-review-2026-10-01\docs\phase3\reviews\ASTRA-6.0\rso-v0.1\ . Read ONLY these five files there: README.md, REVIEW_PACKET_2026-10-01.md, VALIDATION.md, "reports\Wind tunnel charter review.md", "research_notes\Wind tunnel charter review\reviewed_findings.md". Open nothing else in that worktree.
- C, a hardening package by a third model: F:\Prometheus-worktrees\dionysus-base-role\roles\Dionysus\prompts\2026-10-02_hardening_v0.2\ (chatgpt56_01_HARDENING_DESIGN_v0.2.md, chatgpt56_02_TEST_HARNESS_SPEC.md, chatgpt56_03_ARCHITECTURE_PORTFOLIO_v0.2.md, chatgpt56_05_90_DAY_HARDENING_PLAN.md, chatgpt56_06_NEXT_REVIEW_CHARTER.md, 00_README.md).
- O, the original documents both reviews were about: F:\Prometheus-worktrees\dionysus-base-role\roles\Dionysus\prompts\2026-10-01_review_charter\ (03_RSO_WIND_TUNNEL_DESIGN_v0.1_as_pasted.md and 04_RACE_CAR_PORTFOLIO_R0-R9_as_pasted.md).

## Attacks I want, in this order of priority

1. THE COMPOSITION CERTIFICATE (document 2, section 5 "WHAT THIS BUYS"; document 3, section 9; harness\rso_harness\ladder.py, world two). The author's previous proposal (a key world with a second nested boundary, called a ruler for nested improvement) was refuted by simulation: a cache with a fixed re-indexer passed it. The author now proposes "composition on an unseen pair" and claims: (a) for any organism to which the ninth map is a uniformly random permutation the best expected score is 3.38 of 16, and that this holds for every organism after the control history; (b) no stored table and no inherited re-indexing explains a score above the bound on the unseen pair, because the step from a seen table to the unseen one is a 44-bit permutation drawn in this life; (c) therefore an organism above the bound "has combined parts it acquired separately", and this is "reuse of built parts by a fixed builder", not the strong claim. Attack all three.
   - Write your OWN implementation of the world from the prose of document 3 section 9 (do not copy ladder.py) and check the author's numbers (3.37, 3.32, 16.00, 3.47).
   - Try hard to build an organism that scores above the bound on the unseen pair WITHOUT composing tables it acquired: exploit the labels, the order of presentation, the fact that the held-out pair is always (2,2), constraints among the eight seen tables, an inherited re-indexer richer than 256 moves, a partial composition, anything. Report what each attempt scores. If something cheap passes, that is a BLOCKER.
   - Is the control history sufficient (it withholds the move; what about withholding the table)? Does the certificate as coded (Hoeffding threshold, unit = life) hold? Is "exact bound" right when the organism has seen 8 related tables (are the nine maps independent given what was seen, when the move is withheld)?
   - Is the claim that this would give reuse of built parts "its first qualified ruler" honest about what is NOT yet done? Is document 2's falsifier 6 able to fail?

2. THE "GENERAL POINT" AND THE CORRECTED RULE (document 2, section 5). "A rule for acquiring things at one level is content at the next level up ... from behaviour, the most that can be shown is that the object at some level was acquired in this life"; "there is no behavioural ruler for the strong claim, and I do not think one can be defined"; "the two repairs are one rule seen from two sides: name the class you exclude". Is the argument sound, or is it an overclaim in the other direction (declaring something impossible on a one-paragraph argument)? Is it fair to B to say its cargo control "is an exclusion against a class of fixed learners" (check B's section 11 and its unresolved question 1)? Does the corrected rule (i)-(ii) actually block the cache counterexample, and is "8 bits" right?

3. THE SECOND VERSION OF THE HARNESS. Read every module. For each of the 21 gates in rso_harness\meta.py: try to construct a broken case the gate PASSES that is not among the 11 in known_escapes(); try to find a sound case it rejects; check each registered mutant is rejected for the reason its name says. Specific things to attack: stats.classify / equivalence / consistent / lower_bound (arithmetic and edge cases); the fitted table baseline in torture.py (can it miss a leak it should catch; does train/test separation hold); G7.report's replay (can a wrong report pass); the kit registry in audits.py (RUNS and UNBUILT: are the registered answers per claim and per setting justified by what the author's review says about those runs, or chosen so that the result reads well? compare with RESPONSE_1 sections on runs 1-3 and counterfeit\README.md); claims.py (kinds and facets); the "shown" evidence in known_escapes(). You may run the unit tests in place (`python -B -m unittest discover` from the harness folder; they write nothing).
   - To run anything else, copy the harness folder to scratch and run there with `python -B`. In a copy the harness finds the review receipts through the environment variable RSO_COUNTERFEIT (set it to F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\review\FABLE-5.1\counterfeit).

4. FAIRNESS TO B, C AND O IN DOCUMENT 1, with fresh eyes. For every statement about what B says, what C says, where C's design comes from (section 7), what C left out (section 8) and C's gaps (section 9): open the source and check. Flag every place where the document says a source lacks something it contains, misattributes an idea, quotes out of context, or states a position more weakly or more strongly than the text. Check the section 1 table row by row and section 6's allocation table against the three sources. Check section 4 ("what my review adds") for claims the sources contradict.

5. OVERCLAIMS in headlines, in the README's "result in ten lines" and "How this pass was reviewed", and in summary sentences such as "neither repair is complete", "both repairs end in the same place", "the first version ... let through 65 of 71" (are the 71 and the 12 the first reader's own labels, and does the text say so), "eleven gates have a fault they are known not to catch" (are there more than eleven), "54 of 55 changes noticed". For each, say what the evidence supports.

6. READABILITY for a reader on a phone who has seen none of the earlier documents: undefined terms in the first 60 lines of each document, sentences that cannot be parsed, tables whose columns do not line up or whose cells run into each other, documents too long for what they say (say what to cut).

## Limits on you (strict)

- READ-ONLY. Do not create, edit or delete any file under F:\Prometheus-worktrees\ or F:\prometheus. Scratch files go ONLY in C:\Users\jcrai\AppData\Local\Temp\claude\F--prometheus\3815a3b9-a31a-46a9-be9d-0e7abfa3cbf8\scratchpad\verify4\ (create it). Do not touch ...\scratchpad\verify2 or verify3 (another reader's).
- Do not run in place: run_harness.py, mutation_probe.py, attack\replay_attack.py (each rewrites a receipt). Do not run gauntlet.py, gauntlet2.py, gauntlet3.py or keys.py without --design. Use `python -B` so no __pycache__ is written.
- Do not open or list anything under docs/phase3/design/ other than docs/phase3/design/FABLE-5.1/, nor roles/Enceladus, nor roles/Epimetheus, nor anything in the Enceladus worktree other than the five files named above.
- Every repository search must exclude holdout and nestor_secrets paths in any case: git grep ... -- <paths> ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*'. Never open a path containing "holdout" or "nestor_secrets". Never read a credential file (credentials.py, secrets.py, *.env, a repository-level keys.py; the file docs\phase3\review\FABLE-5.1\counterfeit\keys.py is an experiment script and is fine).
- No git command that changes anything. No network.
- Aim for about 45 minutes.

## What to return

A defect list, blockers first, each with: severity (BLOCKER, MAJOR, MINOR), file and line, what the text or code says, what you found, and the smallest fix. One line per item where possible. Then a short section "Probes run" (what you executed and its result, with the numbers) and "Checked and found sound" (short). No praise, no summary of the documents.
