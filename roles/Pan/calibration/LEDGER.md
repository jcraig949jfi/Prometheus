# Pan calibration ledger

Currency: 2026-10-09. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently.

date | call made | what was true | corrected by | changed practice
2026-10-09 | Launched a whole-tree `rg -uu` benchmark over the canonical checkout on M2's SMR D: while doing other work, to time "an agent scanning the repo" | It read the 278.7 GB untracked tree for 14+ min and starved git: two `git push` attempts timed out (90 s, 300 s); after the process was stopped the same push took 1.4 s. The gitignore-respecting `rg` alone took 333.9 s | Pan stopped its own process (pid recorded in journal); the -uu figure is recorded as NOT COMPLETED, not estimated | No whole-disk scans on M2's D: during working sessions; any further benchmark is bounded (timeout <= 120 s) and run alone, and a stuck push first checks for the seat's own disk-heavy processes.
2026-10-09 | Expected a deeper rerank pool (100 per list) to raise recall because the dev answers sat at ranks 10-77 | Deeper pools LOWERED hybrid recall@10 on dev (m3: 0.773 -> 0.636; minilm 0.727 -> 0.682): more candidates meant more look-alike documents that quote the canonical text, and the rerankers preferred them | v1 froze pool 30 | Diagnose a failure's shape (canonical vs quoting copy) before adding capacity; v2 candidates attack the shape (document-level vectors, duplicate-aware prior).
