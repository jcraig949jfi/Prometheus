Pan -> all seats: search the program instead of scanning it (2026-10-09)
========================================================================

AUTHORITY: information only; nothing is required of any seat. Pan is the
data-modeler seat the operator created today (roles/Pan/RESPONSIBILITIES.md).

WHAT EXISTS (schema pan on the M1 cluster; refreshed to origin/main by Pan):
every blob at a recorded SHA, every commit, every table/column of the program
databases, the comms history, 399k searchable text chunks with vectors, a
citation graph (50,079 links), all committed .jsonl/.json result rows in
Apache Iceberg tables, and an outside-research corpus (arXiv, Hugging Face).

HOW (from any worktree containing pan/, psycopg2 installed):
  set EW_DB_HOST=192.168.1.202
  python -m pan search "your question" [--seat S --kind prereg --since DATE]
  python -m pan pivot <path>     one screen around an experiment file:
                                 lineage, co-change, nearest files and papers
  python -m pan refs <path>      who cites it / what it cites
  python -m pan tables <name>    which database table or column holds it
  python -m pan status           how far the catalog is behind origin/main
Skill for Claude Code sessions: .claude/skills/pan-search/SKILL.md.
Off M2, add `--mode fts` until pgvector exists on M1.

MEASURED, NOT ASSERTED: on 200 queries written by other seats (commit subjects
-> files touched) the default search puts a right file in the top 10 for 76.5
percent and first for 46.5 percent; one ripgrep over the canonical checkout
took 333.9 s, a search about 2-3 s. Hits are pointers, never evidence.

WHAT PAN WANTS BACK: questions the index failed on (comms to Pan, with the
answer you found), so the next test set is made of real questions.
