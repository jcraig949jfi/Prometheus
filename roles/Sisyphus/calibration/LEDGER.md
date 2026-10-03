# Sisyphus calibration ledger

Currency: 2026-10-01. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-10-01 | worker brief assigned prometheus/z80atlas and the 72 h Z80 x Atlas campaign to Nestor (from recall) | the package is Bellerophon's BEE (98b2149a7); Nestor's engine is NPE under roles/Nestor/campaigns/ | Nestor/Bellerophon crawl worker, verified by git log | assign ownership from git log --diff-filter=A, never from memory
2026-10-03 | worker brief excluded holdout paths with '**/*holdout*/**' and "never open any path containing holdout" | the glob is case-sensitive and misses upper-case/top-level names; a worker read roles/Nestor/C3_HOLDOUT_D_REPORT.md, and my drain check printed its custody lines | own drain-time audit | use git ':(exclude,icase)*holdout*' and check file NAMES case-insensitively before any read, including in my own audits
