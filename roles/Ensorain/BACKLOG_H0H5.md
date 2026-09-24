# Ensorain backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-23 (charter day). Items 01-05 start today. Items past
ENSORAIN-20 exist only if E0 returns A; they are listed so that the
B branch visibly cancels them.

ENSORAIN-01 | Commit the founding directive verbatim with MANIFEST and rewrite RESPONSIBILITIES.md around it | ENGINE | program | S | none | roles/Ensorain/prompts/2026-09-23_charter/MANIFEST.md verifying; RESPONSIBILITIES.md rewritten
ENSORAIN-02 | Commit PREREG_E0 part 1 (gates, seeds, verdict rule) before any confirmatory data | ENGINE | alpha | S | none | ensorain/PREREG_E0.md in a commit preceding every run row
ENSORAIN-03 | Build the E0 TT core (entry eval, SGD update, TT-SVD, rank-of-order probe) with unit tests against dense reconstruction | ENGINE | alpha | S | none | ensorain/e0/tt.py + tests passing
ENSORAIN-04 | Build the E0 world generator (C, R, M_lambda; directed graph; scrambled observed order) with invariance tests (R preserves histogram and graph) | ENGINE | alpha | S | none | ensorain/e0/world.py + tests passing
ENSORAIN-05 | Build memory arms with MemoryAudit and the lifetime simulator with compute charges | ENGINE | alpha | M | ENSORAIN-03/04 | ensorain/e0/memories.py, life.py; cheat control refused by the audit in a test
ENSORAIN-06 | Run dev-seed engineering: planted-order TT positive control, economy calibration, TT_TUNED grid | ENGINE | alpha | S | ENSORAIN-05 | journal rows + runs/dev_*.jsonl committed
ENSORAIN-07 | Commit PREREG_E0 part 2 (economy constants, TT_TUNED constants) before confirmatory seeds | ENGINE | alpha | S | ENSORAIN-06 | ensorain/PREREG_E0_part2.md commit SHA preceding confirmatory rows
ENSORAIN-08 | Evolve TT_EVOLVED genomes on training seeds 1000-1999 at C=96 and C=168; commit genomes and fitness trajectories | ENGINE | alpha | M | ENSORAIN-07 | runs/evolve_*.jsonl + frozen genome files
ENSORAIN-09 | Run the confirmatory matrix (arms x caps x worlds x instances 10000-10039) | ENGINE | alpha | M | ENSORAIN-08 | runs/confirm_*.jsonl
ENSORAIN-10 | Run the three controls (negative/positive/cheat) on the confirmatory tree | ENGINE | alpha | S | ENSORAIN-09 | runs/controls_*.jsonl + control table
ENSORAIN-11 | Evaluate H1/H2/H3 by the frozen scorer and write the verdict A/B with rows in the same commit | EVIDENCE | alpha | S | ENSORAIN-10 | ensorain/E0_VERDICT.md + scorer output
ENSORAIN-12 | Run the cross-class control (genome evolved on C1 tested on C2) | EVIDENCE | alpha | S | ENSORAIN-08 | runs/crossclass_*.jsonl
ENSORAIN-13 | Produce the review packet for E0 (pure ASCII, committed, pushed) | EVIDENCE | alpha | S | ENSORAIN-11 | roles/Ensorain/reviews/E0_review_packet.txt
ENSORAIN-14 | Replace the INTERIM efficiency measure with the directive's s12 once the remainder arrives; annotate every number that used the interim | EVIDENCE | alpha | S | operator (rest of the directive) | PREREG annotation + re-scored table
ENSORAIN-15 | Commit the remainder of the directive (sections 12+) as 02_ beside 01_ with MANIFEST update | ENGINE | program | S | operator | MANIFEST verifying with 02_ file
ENSORAIN-16 | Write PROVENANCE.md for TT-SVD / TT SGD / NLMS step and any borrowed idea, with citations | LIT | alpha | S | none | ensorain/PROVENANCE.md
ENSORAIN-17 | Record calibration-ledger rows for every seat prediction in PREREG s7 once scored | EVIDENCE | alpha | S | ENSORAIN-11 | calibration/LEDGER.md rows
ENSORAIN-18 | Submit the E0 result (positive or negative) to the evidence wiki | EVIDENCE | alpha | S | ENSORAIN-11 | wiki receipt id in journal
ENSORAIN-19 | Post the E0 verdict report to comms (report, to *) with the committed path | ENGINE | alpha | S | ENSORAIN-11 | comms message id in journal
ENSORAIN-20 | Add a budget-audit fuzz test: random organism objects with hidden containers must all be refused | TOOLS | alpha | S | ENSORAIN-05 | test passing
ENSORAIN-21 | (A only) Add P4 contraction-lock puzzles with a real contraction-order cost | ENGINE | beta | M | E0 verdict A | puzzle family + control
ENSORAIN-22 | (A only) Add P5 spectral gates and P7 delayed-relevance regions with a matched control | ENGINE | beta | M | E0 verdict A | puzzle family + control
ENSORAIN-23 | (A only) Within-life rank adaptation (TT rounding under cap) under selection | ENGINE | beta | M | E0 verdict A | arm + gate result
ENSORAIN-24 | (A only) Scale the world 4096 -> 65536+ nodes on the local GPU; test H3 at scale | ENGINE | beta | L | E0 verdict A | scaling table
ENSORAIN-25 | (A only) Runpod escalation proposal with a cost ceiling | ENGINE | 1.0 | XL | NEW: operator authorises cloud spend | proposal file + operator ruling
