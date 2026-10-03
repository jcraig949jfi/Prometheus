You are an adversarial reviewer. Your job is to find what is WRONG in a small package before it is committed. Do not validate, summarise or praise. I want a defect list. Assume the author overclaims: three earlier review rounds on this author's previous work each found that summary sentences said more than the evidence, and that the author blamed sources for lacking things they contain.

## What is under review (all READ-ONLY for you)

Folder: F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\hardening\FABLE-5.1\
- 01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md  (compares two reviews; critiques a hardening package)
- 02_HARDENING_DESIGN_v0.2_FABLE.md               (the author's own hardening design)
- 03_TEST_HARNESS_SPEC_FABLE.md                   (the author's own harness specification)
- 00_README.md, check_hardening.py
- harness\  (rso_harness\*.py, tests\test_harness.py, run_harness.py, RECEIPT_harness_v0.json, README.md)

The author is "FABLE-5.1 / seat Dionysus" (called A in the documents).

## The sources the documents talk about

- A, the author's earlier review: F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\review\FABLE-5.1\ (RESPONSE_1_REVIEW_REPORT.md, RESPONSE_2_RSO_WIND_TUNNEL_v0.1.md, RESPONSE_3_RACE_CAR_PORTFOLIO_R0-R9.md, 00_README.md, counterfeit\README.md and the RECEIPT_*.json files there).
- B, a review by another model (ASTRA-6.0 / seat Enceladus): F:\Prometheus-worktrees\enceladus-rso-review-2026-10-01\docs\phase3\reviews\ASTRA-6.0\rso-v0.1\ . Read ONLY these five files there: README.md, REVIEW_PACKET_2026-10-01.md, VALIDATION.md, "reports\Wind tunnel charter review.md", "research_notes\Wind tunnel charter review\reviewed_findings.md". Open nothing else in that worktree.
- C, a hardening package by a third model: F:\Prometheus-worktrees\dionysus-base-role\roles\Dionysus\prompts\2026-10-02_hardening_v0.2\ (chatgpt56_01_HARDENING_DESIGN_v0.2.md, chatgpt56_02_TEST_HARNESS_SPEC.md, chatgpt56_03_ARCHITECTURE_PORTFOLIO_v0.2.md, chatgpt56_05_90_DAY_HARDENING_PLAN.md, chatgpt56_06_NEXT_REVIEW_CHARTER.md, 00_README.md).
- The original documents both reviews were about: F:\Prometheus-worktrees\dionysus-base-role\roles\Dionysus\prompts\2026-10-01_review_charter\ (03_RSO_WIND_TUNNEL_DESIGN_v0.1_as_pasted.md and 04_RACE_CAR_PORTFOLIO_R0-R9_as_pasted.md; the documents call them 01 and 02).

## Attacks I want, in this order of priority

1. FAIRNESS AND ACCURACY TOWARD B AND C. For every statement in document 1 about what B says, what C says, what C took from whom (section 7), what C dropped (section 8) and what C lacks (section 9): open the source and check. Flag every place where the document says a source lacks something it contains, misattributes an idea, quotes out of context, or states B's or C's position more weakly or more strongly than the text. Check section 1's side-by-side table row by row. Check section 4 ("where I think my review is stronger") for claims B's text contradicts.

2. THE COMMON-BUCKET TABLE (document 1, section 6). Check each number against the three sources, and attack the mapping: is A's 45 really "tunnel core, and running experiments"? Are B's R8 controls and R4 specimen fairly counted as organisms? Is "the reviews differ by five points on every row" an artefact of the author's bucket choice?

3. THE HARNESS. Read every module. For each of the 21 gates in rso_harness\meta.py:
   - try to construct a broken case that the gate PASSES (an escape) that is not one of the two listed in known_escapes();
   - try to find a sound case it rejects;
   - check that each registered mutant is rejected for the reason its name says, not for an unrelated reason;
   - check that the tests in tests\test_harness.py can fail (a test that cannot fail is a defect).
   Also check the arithmetic: stats.py (critical count 51 for 64 trials at alpha 1e-6; clopper_pearson; zero_hit_upper), search.exact_reach (compare with a brute-force simulation if you can), the claim that NEEDLE under the strict rule has cold reach exactly 0, the panel scores, and audits.py against the receipts it reads (docs\phase3\review\FABLE-5.1\counterfeit\RECEIPT_gauntlet2.json and RECEIPT_gauntlet3.json).
   You may run the harness, but NOT in place: copy the harness folder to a scratch folder first (see limits below) and run there with `python -B`. Note that meta.py locates the receipts relative to its own path, so in a copy you will need to point COUNTERFEIT at F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\review\FABLE-5.1\counterfeit (set meta.COUNTERFEIT before calling, or edit your copy).

4. THE ORDER LADDER (document 2, section 5; document 3, section 9). Is the exact-null argument for the order-4 key world correct (is each family's map really a uniformly random permutation for a policy that carries nothing across the boundary; is 3.38 of 16 really the bound for the first family of an epoch)? Is "content below the claimed order is redrawn, so cargo about content cannot help" right? Is the statement that the ladder "answers both reviews" an overclaim? Is the "operational form for found organisms" coherent? Does anything in the three documents claim the ladder does more than "certify retention of random content at a stated order"?

5. CONSISTENCY. Numbers and statements that disagree between the three documents, the README, the harness receipt and the author's earlier review (for example: 85 defects, 72 checks, run numbers such as 313.5 and 20.5, the kit table against audits.KIT, the gate table against the receipt, GATE 15/30/45/60 content, the allocation). Anything the checker (check_hardening.py) claims to check and does not, or checks in a way that cannot fail.

6. OVERCLAIMS in headlines and summary sentences (for example "nearly one plan under three labels", "a fair merge", "the two counterfeits are one", "21 gates run today", "would not have started"). For each, say what the evidence supports.

7. READABILITY for a reader who has seen none of the earlier documents: undefined terms and labels in the first 60 lines of each document, sentences that cannot be parsed, tables whose columns do not line up.

## Limits on you (strict)

- READ-ONLY. Do not create, edit or delete any file under F:\Prometheus-worktrees\ or F:\prometheus. Scratch files go ONLY in C:\Users\jcrai\AppData\Local\Temp\claude\F--prometheus\3815a3b9-a31a-46a9-be9d-0e7abfa3cbf8\scratchpad\verify2\ (create it).
- Do not run run_harness.py in place (it rewrites its receipt). Do not run gauntlet.py, gauntlet2.py, gauntlet3.py or keys.py without --design. Use `python -B` so no __pycache__ is written.
- Do not open or list anything under docs/phase3/design/ other than docs/phase3/design/FABLE-5.1/, nor roles/Enceladus, nor roles/Epimetheus, nor anything in the Enceladus worktree other than the five files named above.
- Every repository search must exclude holdout and nestor_secrets paths in any case: git grep ... -- <paths> ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*'. Never open a path containing "holdout" or "nestor_secrets". Never read a credential file (credentials.py, secrets.py, *.env, a repository-level keys.py; the file docs\phase3\review\FABLE-5.1\counterfeit\keys.py is an experiment script and is fine).
- No git command that changes anything. No network.
- Aim for about 40 minutes.

## What to return

A defect list, blockers first, each with: severity (BLOCKER, MAJOR, MINOR), file and line, what the text or code says, what you found, and the smallest fix. One line per item where possible. Then a short section "Probes run" (what you executed and its result) and "Checked and found sound" (short). No praise, no summary of the documents.
