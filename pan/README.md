# pan/ -- the program's data layer (owner: roles/Pan)

Users: read `.claude/skills/pan-search/SKILL.md`. This file is for maintainers.

## Where things live

    M1 cluster (prometheus-canonical), database prometheus_fire
      schema pan          catalog, chunks (+tsvector), embeddings (real[]), commits,
                          links, cluster catalog, frontier, HF models, model bench,
                          lexeme frequencies, run log, intake call log
      schema pan_iceberg  PyIceberg SqlCatalog tables (which Iceberg tables exist,
                          their snapshots and files)
    M2 (SPECTREX5) lake, path from pan/config.json or PAN_LAKE (NVMe, never SMR D:)
      iceberg/            data files of the Iceberg tables (result_rows, result_docs,
                          inv_*, git_*)
      vectors/            Parquet shards per embedding model + .npz caches
      inventory/<run>/    Parquet snapshots of each inventory run
      consolidated/typed/ per-file typed Parquet of committed .jsonl
      cold_sample/        conversion samples of the April cold data (deletable)
    M2 venv              <lake parent>/venv (pyarrow, pyiceberg, sentence-transformers)

Schema descriptions live IN the database (`comment on table`, migration 006);
`python -m pan dictionary` regenerates roles/Pan/docs/DATA_DICTIONARY.md.

## Rebuild from nothing (everything here is derived; sources stay authoritative)

    python -m pan migrate              # 001..007
    python -m pan inventory            # stores, artifacts, cluster catalog
    python -m pan commits              # history (oracle: git rev-list --count)
    python -m pan chunk                # text chunks (eval fixtures excluded: config)
    python -m pan embed                # chunk vectors (GPU; take a Fabric lease)
    python -m pan embed --docs         # document vectors (GPU; lease)
    python -m pan lexdf; python -m pan links
    python -m pan comms-index
    python -m pan consolidate; python -m pan consolidate --docs
    python -m pan frontier arxiv|hf-models|hf-daily|feeds|github; python -m pan frontier embed

Keep it fresh: `python -m pan refresh` (incremental: changed blobs only, then
lexdf + links + caches) and `python -m pan frontier daily` (skips if < 20 h).

## Controls (run before trusting a change)

    pan/tests/test_iceberg.py      POSITIVE / NEGATIVE (time travel) / CHEAT (planted
                                   file invisible until committed) / EVOLVE -- live catalog
    pan/tests/test_consolidate.py  parser modes + the line-count oracle
    pan/tests/test_fit.py          16 GB fit estimate incl. two cheat cases
    pan/tests/test_links.py        citation extraction incl. URL look-alikes
    pan/tests/test_feeds.py        feed parser: RSS/Atom known items, not-a-feed, undated and
                                   placeholder dates, entity bomb, local-path body, rate spacing
    pan/tests/test_ghwatch.py      repo item builder; anonymous-by-construction check
    python -m pan frontier github controls  live: owners answer, a nonexistent owner fails with
                                   0 items, re-sweep adds 0, gap >= 2 s, reserve kept
    python -m pan frontier feeds controls   live: every feed parses, report-listed dead URLs
                                   fail with 0 items, re-poll adds 0, min gap >= 2 s
    pan/tests/test_modelbench.py   probe checkers incl. hard-coded cheats and an
                                   independent derivation of every answer key
    python -m pan.controls         retrieval controls against frozen query sets
                                   (pan/tests/*answers*.json, commit_bench_cb200.json);
                                   rows land in roles/Pan/reports/controls/

Retrieval verdicts and why tuning stopped: roles/Pan/reports/RETRIEVAL_VERDICTS_2026-10-09.md.

## Known limits

- Vector search: M2 uses the exact in-process matrix from the lake; every other host uses
  pgvector HNSW in Postgres (migrations 012/013, pan/pgvec.py; PAN_VECTOR_BACKEND=local|pg
  overrides). HNSW is approximate: on real query vectors recall@10 is 0.94 at the default
  ef_search 200 and 0.98 at 400 (search asks for 400 candidates); on the 62 frozen queries
  chunk search off M2 loses 1 of 37 answers that the exact search finds (H10). Pivot,
  similar and `frontier like` need only psycopg2 + numpy; a TEXT query also needs the
  encoder on the host (sentence-transformers + bge-small, ~130 MB).
- Seat and kind columns come from path rules and commit-subject prefixes; they
  are lower bounds, not facts about content.
- The lake is M2-local (Q-003); the Iceberg catalog on M1 is visible everywhere.
