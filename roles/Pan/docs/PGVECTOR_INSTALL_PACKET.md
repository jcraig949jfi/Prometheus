# pgvector on the M1 cluster -- install packet (for QUESTIONS.md Q-001)

Currency: 2026-10-09. Status: PREPARED, NOT EXECUTED. Executing it is a privileged
host change on M1 (MWO-0004 Part 4 hard gate); it waits for the operator's yes.
Pan cannot run it: M2 has no shell on M1, and Pan does not install system software.

## Facts it rests on (measured 2026-10-09 unless marked)

- Cluster: PostgreSQL 17.9, x86_64-windows (msvc), data_directory
  C:/Program Files/PostgreSQL/17/data on SKULLPORT (M1), db_system_id
  7628127204585430828. `vector` is absent from pg_available_extensions.
- pgvector upstream (github.com/pgvector/pgvector, read 2026-10-09): latest tag
  v0.8.7; on Windows the supported route is a source build with Visual Studio C++
  tools; no official prebuilt Windows binary (conda-forge is community-maintained).
  HNSW indexes take up to 2,000 dimensions for vector and 4,000 for halfvec --
  Pan's vectors are 384 (chunks) and 512 (documents, papers).

## Steps on M1 (operator or an M1 seat, as administrator)

1. Prerequisite: Visual Studio 2022 Build Tools with "Desktop development with
   C++" (itself an install; skip if present). Git for Windows.
2. Open "x64 Native Tools Command Prompt for VS 2022" AS ADMINISTRATOR
   (upstream warns other prompts give architecture errors), then:

       set "PGROOT=C:\Program Files\PostgreSQL\17"
       cd %TEMP%
       git clone --branch v0.8.7 https://github.com/pgvector/pgvector.git
       cd pgvector
       nmake /F Makefile.win
       nmake /F Makefile.win install

3. Record, for the receipt, the sha256 of every installed file:

       certutil -hashfile "C:\Program Files\PostgreSQL\17\lib\vector.dll" SHA256
       dir "C:\Program Files\PostgreSQL\17\share\extension\vector*"

4. No server restart is needed. Tell Pan (comms) "pgvector installed", with the
   hashes; Pan does the rest from M2.

## What Pan then does (migration 007, reversible)

- `CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA pan;` in prometheus_fire
  (types live in schema pan; no other schema is touched).
- Adds halfvec columns beside the existing real[] (real[] kept until verified):
  pan.embedding.hv halfvec(384), pan.doc_embedding.hv halfvec(512),
  pan.frontier_embedding.hv halfvec(512); fills them from real[]; builds HNSW
  indexes (vector_cosine_ops on halfvec).
- Search switches from the in-process matrix to `ORDER BY hv <=> $q LIMIT k`,
  usable from every host with only psycopg2.

## Acceptance (fixed now, before any install)

- POSITIVE: `select '[1,2,3]'::pan.vector <-> '[1,2,4]'` returns 1.
- RECALL: on 1,000 random chunk vectors used as queries, HNSW top-10 overlaps
  exact top-10 (the current in-process search) by >= 0.95 on average.
- CHEAT: a vector inserted after the index build is found as its own nearest
  neighbour (the index sees new rows).
- The frozen retrieval controls (pan/tests/) give the same ranks as before
  within the recall tolerance.
- Size: report pan schema size before and after (halfvec halves the 791 MB of
  real[] chunk vectors; the HNSW index adds roughly the same again).

## Rollback

`DROP EXTENSION vector CASCADE;` removes only Pan's halfvec columns and indexes
(the real[] columns stay); delete the files copied in step 2; no restart.
