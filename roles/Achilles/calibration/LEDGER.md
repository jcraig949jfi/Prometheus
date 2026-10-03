# Achilles calibration ledger

Currency: 2026-09-30. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-10-01..03 | (operator-chat sessions on ELSA, infrastructure work on the ubuNNN nodes and fleet docs) ran `git pull` and committed directly in the canonical checkout C:/prometheus, moving it: commits ffa083fad, 9b5525084, c07725fac, 563ee7c36, 3afecc198, f017ac08d, ce3d94bed, a9ee5f4e9 were made there and pushed to main | WORKING_CONTRACT s1/s3 forbid any mutating git operation and any file edit in the canonical checkout; this is an incident (the pulls MOVED the checkout), not a boot transient | found by this seat on 2026-10-03 while reading the contract for the RSO cell setup | all work since uses a worktree (Prometheus-worktrees/achilles-rso-cell, branch achilles/rso-builder-cell-2026-10-03, base 2af086e79); read WORKING_CONTRACT before the first git command of any session, including operator-chat sessions
