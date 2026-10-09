---
name: pan-search
description: Search the Prometheus catalog (Pan's index over the whole repository, git history, every database table, and outside research/models) INSTEAD of grepping or reading the repository. Use FIRST for broad questions -- "where did we test X", "which file says Y", "what changed together with this file", "which table/column holds Z", "what outside papers or runnable models relate to this" -- and before claiming a gap. Returns ranked pointers (path:lines at a catalog SHA, table names, arXiv ids, HF repo ids), never verdicts.
---

# pan-search (roles/Pan)

Pan keeps a catalog of every blob in the repository at a recorded SHA, every
commit, every relation and column on the M1 cluster, 394,952 searchable text
chunks with embeddings, and a frontier corpus (arXiv, Hugging Face daily
papers, Hugging Face models with a 16 GB fit estimate). Measured 2026-10-09:
one ripgrep over the canonical checkout took 333.9 s; a ranked search takes
about 0.1-2.6 s.

A hit is a POINTER, never evidence. Open the file at the cited lines before
relying on it, and remember the catalog may be behind origin/main.

## Setup (any host)

Run from a worktree that contains `pan/` (origin/main), with the M1 cluster
reachable. psycopg2 is required; vector modes also need numpy +
sentence-transformers (M2's Pan venv has them).

    set EW_DB_HOST=192.168.1.202            (bash: export EW_DB_HOST=192.168.1.202)
    python -m pan status                    catalog SHA vs origin/main, last runs

On hosts without the Pan lake (anything but M2) use `--mode fts` for now:
vector search loads its matrix from the lake on M2 or, failing that, pulls it
from Postgres (slow) until pgvector exists on M1 (roles/Pan/QUESTIONS.md Q-001).

## Commands

    python -m pan search "QUESTION" [-k 10] [--mode hybrid|fts|vector]
                         [--seat Archaeon,Nestor] [--kind prereg,result,journal,charter,doc,code,prompt]
                         [--path substring] [--since 2026-09-01] [--json]
    python -m pan cochange PATH          files changed in the same commits as PATH (lineage, pivots)
    python -m pan similar PATH           artifacts nearest to PATH by embedding (M2)
    python -m pan tables NAME            which database.schema.table / column matches NAME
    python -m pan frontier search "Q"    outside papers (arXiv + HF daily) by full-text
    python -m pan frontier models Q [--fits]   HF models, optionally only those estimated to fit 16 GB at Q4
    python -m pan stats                  row counts of every Pan table

Kinds come from path rules (a convention, not content): journal, prompt,
prereg, review, receipt, status, charter, code, result, data, doc, config.
Seats come from roles/<Seat>/ paths and mapped top-level directories.

## Reading results

    1. roles/base-role/RESPONSIBILITIES.md:379-414  [charter - 2026-10-03] fts#1 vec#3 rr
          # Base role ... > 2a. Work-conserving research loop
          snippet ...

- `path:start-end` are line numbers at the catalog SHA (`python -m pan status`).
- `[kind seat last-commit-date]`; `via` shows which lists found it
  (fts / vec / doc) and their ranks; `rr` = reranked; `canon>N` = moved above
  a later copy of near-identical text.
- Quality, measured against frozen known-answer queries (written by Pan, so
  an upper bound): v1 hybrid recall@10 0.75 on held-out queries; full-text
  recall@10 0.80 on keyword-style questions; abstract paraphrases are the
  weak case. When a search misses, try fewer, more specific words with
  `--mode fts`, or filter by `--seat` / `--kind`.

## Do not

- Do not cite a hit as evidence of a claim; it is a retrieval result.
- Do not query or write schema pan by hand for anything a command covers;
  report gaps to Pan (comms) instead.
- Do not run whole-checkout greps on M2's SMR disk during working sessions
  (they starve git for minutes; Pan's calibration ledger 2026-10-09).
