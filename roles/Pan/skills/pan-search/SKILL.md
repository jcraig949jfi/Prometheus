---
name: pan-search
description: Search the Prometheus catalog (Pan's index over the whole repository, git history, every database table, and outside research/models) INSTEAD of grepping or reading the repository. Use FIRST for broad questions -- "where did we test X", "which file says Y", "what changed together with this file", "which table/column holds Z", "what outside papers or runnable models relate to this" -- and before claiming a gap. Returns ranked pointers (path:lines at a catalog SHA, table names, arXiv ids, HF repo ids), never verdicts.
---

# pan-search (roles/Pan)

Pan keeps a catalog of every blob in the repository at a recorded SHA, every
commit, every relation and column on the M1 cluster, 394,952 searchable text
chunks with embeddings, and a frontier corpus (arXiv, Hugging Face daily
papers, lab blogs, newsletters, tracked GitHub releases and repositories,
Hugging Face models with a 16 GB fit estimate). Measured 2026-10-09:
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
    python -m pan pivot PATH             ONE SCREEN around an experiment artifact: what it is, who cites
                                         it / what it cites, what changed with it, nearest artifacts
                                         (its ruling, seal, amendments usually appear), nearest papers
    python -m pan refs PATH              who cites PATH and what PATH cites (paths written in text;
                                         45,122 links incl. comms), oldest first -- prereg -> result -> successors
    python -m pan cochange PATH          files changed in the same commits as PATH (lineage, pivots)
    python -m pan similar PATH           artifacts nearest to PATH by embedding (M2)
    python -m pan tables NAME            which database.schema.table / column matches NAME
    python -m pan frontier search "Q"    outside work by full-text: arXiv, HF daily papers, 19 lab blogs /
                                         newsletters / ALife society, 16 tracked repos' releases ("owner repo release: tag"),
                                         repositories of 29 tracked GitHub owners ("owner name: description")
    python -m pan frontier models Q [--fits]   HF models, optionally only those estimated to fit 16 GB at Q4
    python -m pan frontier digest        ASCII digest: recent papers by topic, new 16 GB-fit models, feed entries + feed health
    python -m pan frontier like PATH     outside papers nearest to a repository file (exploratory: the
                                         cited paper is in the top 10 for 34.8 percent of 273 citing files)
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
- Quality (roles/Pan/reports/RETRIEVAL_VERDICTS_2026-10-09.md): on 200
  queries written by other seats (commit subjects -> the files they
  touched), the default hybrid puts a right file in the top 10 for 76.5
  percent and at rank 1 for 46.5 percent; on Pan's own held-out questions
  0.75. Abstract paraphrases are the weak case. When a search misses, try
  fewer, more specific words with `--mode fts`, or filter by `--seat` /
  `--kind`. The reranker runs only where a CUDA GPU exists (PAN_RERANK).

## Do not

- Do not cite a hit as evidence of a claim; it is a retrieval result.
- Do not query or write schema pan by hand for anything a command covers;
  report gaps to Pan (comms) instead.
- Do not run whole-checkout greps on M2's SMR disk during working sessions
  (they starve git for minutes; Pan's calibration ledger 2026-10-09).
