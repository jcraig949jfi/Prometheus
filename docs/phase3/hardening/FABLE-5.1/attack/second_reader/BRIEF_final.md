# Brief to the second reader for its final read, of version three

Verbatim, as sent.

---

Final closure read: version three of the FABLE-5.1 hardening package is on disk; please verify closure of your 8 blockers and 38 majors, score the tests at first sight with a fresh set of changes, and attack the gates once more. Same rules as before, restated below. Keep it short: a defect list, no praise. Work alone this time (no forks) unless you truly need one.

## Where
F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\hardening\FABLE-5.1\  (still uncommitted; ignored by .gitignore; I will add -f by explicit paths)
- 01, 02, 03 documents rewritten and cut. Document 2 section 5 and document 3 section 8 now claim only: a score above the bound on the ninth pair says information from at least three separately shown families was combined, nothing about how; the excluded class is named; the control is the eight shown families drawn from another key under the same labels; SCHEMA_CACHE, TWO_TABLES, HIDER and SANDBAGGER are in harness/rso_harness/ladder.py and in the tables; falsifiers 4 and 6 of document 2 section 17 are rewritten; no verdict on reuse of built parts is given anywhere, and audits.RUNS registers all 26 receipt cells.
- harness/: third version. 21 gates, 48 sound cases, 215 mutants, 24 known escapes (meta.known_escapes, at least one per gate), 103 unit tests. mutation_probe.py carries your 32 changes (F01-F32), your fork's 36 (H01-H36), the closure reader's 44, the first reader's 25 and my 30.
- check_hardening.py rewritten; PINS are empty and five placeholders (FINAL_READ_PLACEHOLDER, CHECKS_PLACEHOLDER, FIRE_PLACEHOLDER) are in the text on purpose: they will be filled with the results of this read. Do not report those, the pins, or the missing MANIFEST.md files. Run it as: python -B check_hardening.py --no-fire --no-manifests --no-pins
- attack/second_reader/ holds your report, your forks' reports, your brief and your scripts as records; attack/second_version/ is the harness you attacked.

## Three jobs, in this order
1. FIRST-SIGHT SCORE OF THE TESTS. BEFORE you open harness/tests/test_harness.py or harness/mutation_probe.py of version three, read only harness/rso_harness/*.py and write at least 40 one-line changes to gate logic (spread over all eleven modules; none copied from your earlier sets, the fork's, or the closure reader's; mark any you believe alter no verdict). Then run the 103 unit tests on a scratch copy per change and report: changes, noticed, unnoticed, and of the unnoticed how many alter no verdict on any input. This is the one honest measure of the tests; please keep the order (changes written before the tests are read) and say in the report that you did.
2. CLOSURE. Your blockers 1-8 and majors 9-46: one line each, CLOSED / PARTLY / OPEN with file:line. For blockers 1, 2 and majors 9-15 re-run what you need (your comp.py organisms against the new control; is the excluded class as stated in D2 section 5 correct; can falsifier 6 now fire; does the new control catch your sandbagger).
3. ONE MORE ATTACK. Up to 15 broken cases against the version-three gates that PASS and are not in meta.known_escapes(), and any sound case that is refused. Say which gate each belongs to. I expect some: the documents now say the list of escapes is not complete, so what matters is whether any statement in documents 2 or 3 about what a gate catches is false.

## Rules (unchanged)
- READ-ONLY in F:\Prometheus-worktrees\ and F:\prometheus: create, edit, delete nothing there; no git write of any kind. Scratch: C:\Users\jcrai\AppData\Local\Temp\claude\F--prometheus\3815a3b9-a31a-46a9-be9d-0e7abfa3cbf8\scratchpad\verify6\ . Always python -B; leave no __pycache__ in the worktree. Copies of the harness find the review receipts through the env var RSO_COUNTERFEIT=F:/Prometheus-worktrees/dionysus-base-role/docs/phase3/review/FABLE-5.1/counterfeit ; a copy of the checker reads git objects through HARDENING_GIT_ROOT=F:/Prometheus-worktrees/dionysus-base-role .
- Search rule, verbatim: every search must exclude holdout and nestor_secrets paths in any case: git grep ... -- <paths> ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*' ; listings: git ls-files -- ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*' | grep '^<prefix>/' ; never give git ls-files one positive slashed path plus an exclusion; never pipe an unfiltered file list into grep -c / wc / cat; never open any path containing holdout or nestor_secrets.
- Do not open any directory under docs/phase3/design/ other than FABLE-5.1, nor roles/Enceladus, roles/Epimetheus, nor anything in the Enceladus worktree. Do not open credentials.py, secrets.py, a repository-level keys.py, any .env file, evidence_wiki/config.json or mnemosyne/STATE.md. Keep every search scoped to docs/phase3/hardening/FABLE-5.1, docs/phase3/review/FABLE-5.1 and roles/Dionysus/prompts.

## Output
Sections: 1 first-sight score (with the list of unnoticed changes, one line each); 2 closure table; 3 defects still open or new (BLOCKER / MAJOR / MINOR, each with file:line and a one-line fix); 4 new passing faults by gate; 5 what you did not check. Plain ASCII please.
