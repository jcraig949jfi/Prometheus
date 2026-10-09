# Prometheus data architecture -- v0.1 (Pan, PAN-02)

Currency: 2026-10-09 (first version; written after inventory
inv-20261009T1054Z-spectrex5 and the first build/measure cycle). Status:
DESIGN + PARTIAL BUILD. Every number below is measured on the date given
unless marked as an estimate. Charter: roles/Pan/prompts/2026-10-09_charter/.

## 0. The requirement in one line

A seat (or the operator) asks a broad question -- "where did we test X",
"what came before this failure", "which table holds Y", "what outside work
is like this" -- and gets pointers (path:lines at a SHA, table names, paper
ids) in seconds, from any host, without an agent reading the repository.

## 1. What exists (reports/INVENTORY_2026-10-09.md)

Four temperature classes, by measured modification time and use:

    HOT    repository at origin/main      73,037 blobs     4.0 GB  13,128 commits; 7,256 in Sept from 52 seats
           prometheus_fire (M1)           ~300 relations   3.5 GB  comms, ew, atlas, viv, fabric, agora ...
    WARM   M2 NVMe evidence + SFE ledger  517 files       14.9 GB  Sept campaigns
    REF    lmfdb (M1)                     7 relations     ~392 GB  read-mostly reference
    COLD   untracked in canonical (M2)    294,343 files  278.7 GB  92 percent April 2026
           backup root (M2)               46,438 files    38.4 GB  April

Row data is mostly stored as TEXT: 131.8 GB of untracked JSON Lines, and
2.6 GB of committed .json/.jsonl result rows.

## 2. Principles

P1  SOURCES STAY AUTHORITATIVE. Every Pan layer is derived and rebuildable
    from sources by a committed command; dropping schema pan loses nothing
    that cannot be regenerated. Pan never moves or deletes a source.
P2  ONE CROSS-HOST TRUTH. Anything more than one host must see goes to
    Postgres on M1 (topology ruling 2026-09-16: Postgres and Redis are the
    shared services). The lake is a derived, bulk, analytical tier.
P3  INDEX TEXT, COLUMNARISE ROWS, VECTORISE MEANING, VERSION WHAT EVOLVES.
    Text -> Postgres full-text. Row data -> Parquet. Meaning -> embeddings
    (pgvector). Tables that grow and change shape over time -> Iceberg.
P4  EVERY LAYER CARRIES ITS OWN FALSIFIER: an independent oracle where one
    exists (git rev-list for history; source line counts for conversions),
    and POSITIVE / NEGATIVE / CHEAT controls for retrieval (pan/tests/).
P5  CHEAPEST TIER THAT ANSWERS. Measured latencies decide (s6), not taste.

## 3. Tier assignment

    data class                 examples                         tier                       status 2026-10-09
    ---------------------------------------------------------------------------------------------------------
    seats' operational state   comms, fabric, viv, atlas, ew    Postgres, owner's schema   EXISTS; Pan reads only
    catalog / pointers         every blob, store, commit,       Postgres pan.artifact,     BUILT (73,037 artifacts,
                               relation, column                 store, commit, pg_*        13,128 commits, 345 rels)
    text for search            docs, code, prompts, journals,   Postgres pan.chunk         BUILT (394,952 chunks,
                               receipts, small JSON             (stored tsvector + GIN)    1.1 GB)
    embeddings                 chunk and paper vectors          pgvector HNSW on M1        GATED (Q-001); interim
                                                                (interim: real[] + lake    real[] 791 MB + Parquet
                                                                Parquet + in-process)      shards 570 MB
    committed row data         .jsonl/.json result ledgers      Parquet; Iceberg when a    DESIGNED (PAN-16)
                               (2.6 GB)                         series grows over time
    cold row data              cartography convergence          Parquet conversion on      NOT STARTED; needs a
                               (128.8 GB jsonl), logs           demand of a consumer       consumer (s8)
    history of the catalog     inventory runs, frontier         Iceberg (snapshot per      BUILT for the Iceberg
                               snapshots, commit tables         run; time travel)          layer (controls pass)
                               [CORRECTION 2026-10-09T13:00Z (commit bafd4af10): at v0.1 only the LAYER existed; no history table
                               did. Created about 12:59Z: pan.inv_repo_blobs 73,037, inv_fs_files 342,019,
                               inv_pg_relations 345, git_commits 13,128, git_commit_files 143,310 -- each equal
                               to its source count. pan.result_rows 2,253,498 (PAN-16).]
    engine ledgers (SQLite)    SFE engine.db                    owner's store; read-only   NOT PAN'S (SFE point
                                                                Parquet export with ack    release is Daedalus/Viv)
    model weights              vault/, apollo/.hf_cache         catalog rows only (path,   DESIGNED
                               (75 GB safetensors)              size, hash, HF repo id)
    reference data             lmfdb (392 GB in Postgres),      stays in Postgres          EXISTS; catalogued
                               lmfdb_dump (24 GB json)          (indexed relational)
    frontier corpus            arXiv, HF daily papers,          Postgres pan.frontier_item BUILT (4,702 arXiv
                               HF models                        + pan.hf_model; Iceberg    items; HF running)
                                                                snapshots for history

Why Postgres for the catalog and text: small (2.2 GB for everything Pan
holds), joinable with the seats' own schemas, concurrently readable from
every host, and full-text search runs server-side. Why NOT Postgres for
bulk rows: 132 GB of JSON Lines in a row store would multiply the shared
cluster's size by about 25x for data read rarely; columnar Parquet with
zstd typically shrinks such data several-fold and is scanned only when a
consumer asks (ratio to be measured on a real set, PAN-16).

Why Iceberg (and not only Parquet): Iceberg adds what plain files lack and
this program needs to "pivot when an experiment fails or succeeds":
snapshots (every append is a version), time travel (read the table as of a
snapshot), rollback, schema evolution, and reads through metadata rather
than directory listings. Measured 2026-10-09 against the live catalog
(pan/tests/test_iceberg.py, 1 passed): append round-trip; time travel to
snapshot 1 excludes later rows; a Parquet file planted in the table's data
directory OUTSIDE Iceberg is invisible until committed through Iceberg; a
column added by schema evolution reads back with nulls for old rows.

Where the Iceberg catalog lives: schema pan_iceberg on M1 (PyIceberg
SqlCatalog). Every host can see which tables exist, their schemas,
snapshots and file lists; the data files live under PAN_LAKE on M2's NVMe
until Q-003 decides otherwise. Windows note: PyIceberg 0.12.0's PyArrow
FileIO turns file:///C:/... into /C:/... (WinError 123); Pan uses the
fsspec FileIO.

## 4. The catalog model (schema pan, migrations 001-002)

    run           one row per collector run (what, where, SHA, counts, status)
    store         every store on every host (repo tree, data root, database,
                  schema, SQLite/DuckDB file) with size, count, freshness
    artifact      one row per blob/file: path, blob SHA, kind, owning seat,
                  first/last commit, title, chunk count, indexed blob
    chunk         text chunks with line ranges, heading path, stored tsvector
    embedding     (chunk, model) -> vector; several models side by side
    commit        git history with seat/instance parsed from the subject
    commit_file   (commit, path, status) -- co-change and lineage
    pg_relation   every relation in every program database, sizes, row est.
    pg_column     every column, type, comment
    frontier_item papers (arXiv, HF daily), Eos type column (UNTYPED default)
    hf_model      HF models with a 16 GB local-fit estimate
    intake_call   every external call (rate audit)

Seat attribution is by path rule (roles/<Seat>/, mapped top-level
directories) and by commit-subject prefix; both are lower bounds, and the
columns say which rule produced them.

## 5. Indices and their controls

- Full-text: Postgres tsvector (english), heading weighted above body.
  v0 used AND semantics (websearch_to_tsquery). v1 uses OR semantics ranked
  by COVERAGE (distinct query lexemes present) then cover density, with a
  minimum-should-match of 34 percent of the query's lexemes.
- Vector: bge-small-en-v1.5 (384 d) over all 394,952 chunks, chosen for
  throughput (measured on M2's RTX 5060 Ti: ~1,050 chunks/s versus ~34 for
  Qwen3-Embedding-0.6B; full catalog in 558 s, about 0.16 GPU-h, under a
  Fabric lease). Cached as a float16 matrix (394,952 x 384, built from local
  Parquet shards in 4.3 s when their row count equals the database's).
- Hybrid: reciprocal-rank fusion per artifact; optional cross-encoder rerank.
- Controls (frozen before runs): 22 dev queries, 20 held-out queries, two
  nonsense queries, one planted document. v0 FAILED its positive thresholds
  (hybrid recall@10 0.68 < 0.80); NEGATIVE and CHEAT passed
  (reports/controls/CONTROLS_20261009T1117Z.json). v1 is being developed on
  the dev set and will be judged only on the held-out set.

## 6. Measured latencies (2026-10-09, from M2 against M1)

    operation                                          time
    full-text, AND (v0), per query                     0.06-0.08 s
    full-text, OR + coverage (v1), per query           1.1-1.4 s
    vector, in-process over 394,952 chunks             0.34 s median (incl. query embedding)
    hybrid v1 (fts-or + vector + fusion)               1.7 s median; +0.2-0.3 s with a small reranker
    git grep -l -i at a SHA (whole tree), cold cache   83.8 s
    git grep -l -i at a SHA, warm cache                2.95-3.16 s
    recursive grep over the canonical checkout         > 900 s (killed at the timeout; it reads the
      (md/py/json/txt incl. untracked)                 278.7 GB untracked tree on the SMR disk)
    inventory (all four collectors)                    146.1 s
    git history parse (13,128 commits)                 1.8-75 s (warm vs cold pack reads)

Reading: a grep is fast only when the cache is warm and the question is
lexical; it returns file names, not ranked passages, and it cannot answer
paraphrased questions or table-discovery questions at all.

## 7. Pivot support (charter C4)

    python -m pan cochange <path>    files that change in the same commits
    python -m pan similar <path>     nearest artifacts by mean chunk embedding
    python -m pan search ... --seat S --kind prereg --since DATE
    python -m pan tables <name>      which relation/column holds a thing
    python -m pan frontier search    outside papers matching a question
    python -m pan frontier models --fits   runnable local models

Planned: lineage(path) (prereg -> result -> successors by commit order and
cross-references), and "outside work like this file" (frontier embeddings).

## 8. What is deliberately not done

- No conversion of the 132 GB cold JSON Lines until a consumer asks for a
  specific family: converting April data nobody queries is utilisation, not
  progress (base role 2a I). The conversion recipe (PAN-16) will be proven on
  committed result sets first, with source line counts as the oracle.
- No migration of anyone's SQLite ledger (owner's point release).
- No DuckDB store or engine (Q-006).
- No writes outside schema pan / pan_iceberg and the lake.

## 9. Open decisions and costs

- Q-001 pgvector (hard gate). Q-002 Aporia integration. Q-003 lake location.
  Q-004 other hosts. Q-005 API keys. Q-006 DuckDB. Q-007 disk budget on M1.
- Cost on the shared cluster: schema pan + pan_iceberg = 2.2 GB measured;
  prometheus_fire grew from 3,477 MB to 5,698 MB. Embeddings are 791 MB of
  that as real[] (pgvector halfvec would roughly halve it). Pan caps itself
  at 10 GB on M1 until the operator sets a budget (Q-007).
- Lake on M2 NVMe: 0.6 GB used (vectors 570 MB).

## 10. Next iterations (backlog order)

v1 retrieval verdict on the held-out set -> frontier embeddings and
"outside work like this" -> PAN-16 consolidation recipe on committed result
sets (Parquet + Iceberg, line-count oracle) -> incremental refresh loop
(PAN-17) -> pan-search skill for every seat (PAN-18) -> local-model smoke
tests (PAN-19).
