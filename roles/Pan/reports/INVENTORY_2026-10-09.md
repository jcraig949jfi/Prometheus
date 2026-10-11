# Pan inventory v0 -- every store the program writes (PAN-01, PAN-25)

Currency: 2026-10-09. Run inv-20261009T1054Z-spectrex5 (146.1 s), repository
tree at d6b2eeeca, host SPECTREX5 (M2), cluster prometheus-canonical (M1).
Rows: <lake>/inventory/inv-20261009T1054Z-spectrex5/*.parquet (repo_blobs,
fs_files, db_file_sightings, pg_relations, pg_columns, SUMMARY.json) and
schema pan (artifact, store, pg_relation, pg_column, run). Command:
`python -m pan inventory --sha origin/main`. Every population is enumerated
in full; nothing below is a sample. NOT inventoried: other hosts' data
roots (M1, M3, M4, laptops, harry1; Q-004) and other seats' linked
worktrees under the worktrees root (their untracked outputs are invisible to
this run).

## 1. The headline

    store                                   files/rels      bytes   newest
    repository at d6b2eeeca (git)               73,037     4.0 GB   2026-10-09
    canonical checkout, UNTRACKED (M2)         294,343   278.7 GB   2026-10
    backup root Prometheus_data_backup (M2)     46,438    38.4 GB   2026-04
    C:/Prometheus-data (M2, NVMe)                  517    14.9 GB   2026-09-29
    D:/Prometheus-data (M2, SMR)                   721     0.3 GB   2026-10-09
    cluster: lmfdb                         7 relations   ~392 GB   (reference)
    cluster: prometheus_fire             ~300 relations    3.5 GB   live
    cluster: prometheus_sci                 relations     0.3 GB

Three facts carry the design (docs/DATA_ARCHITECTURE.md):

1. COLD vs HOT. Of the 278.7 GB untracked in the canonical checkout, 256.8 GB
   was last modified in April 2026 and 18.6 GB in May; June-October add
   2.7 GB. The program's live record is the 4.0 GB repository plus the
   3.5 GB prometheus_fire database plus the 14.9 GB evidence on M2's NVMe.
2. THE BULK IS JSON LINES. Untracked: 131.8 GB of .jsonl in 66,259 files
   (cartography/convergence/data alone is 128.8 GB in 134 files). Tracked:
   1.35 GB .jsonl in 3,379 files and 1.25 GB .json in 24,248 files are
   result/data rows. These are row data stored as text; they are the
   Parquet/Iceberg candidates.
3. ACTIVITY IS RECENT AND WIDE. 13,128 commits; 7,256 of them in September
   2026 from 52 distinct seat prefixes, 1,392 in the first nine days of
   October from 34. A broad question now touches dozens of seats' files.

## 2. The repository at d6b2eeeca (73,037 blobs, 4.0 GB)

By path-derived kind (a path rule is a convention, not a content fact):

    kind       files      MB   chunks indexed
    data      15,890  1832.8      28,586   (small .json only; see s5)
    result    17,194  1376.1      23,093
    doc       18,653   472.8     192,370
    code      15,686   155.1     125,997
    receipt    1,293    53.2       4,151
    prompt     1,715     7.3       6,981
    prereg       687     3.8       3,502
    review       193     3.3       1,751
    journal      271     2.6       2,390
    status       223     1.8       1,121
    charter      185     1.5       1,712
    other/archive/media/config      ~1,047    65.4    3,298

Largest owners by bytes: (no seat by path rule) 563.9 MB, Nestor 430.4,
Ergon 336.5, Lexis 305.8, Crius 296.1, Tyche 278.5, Archaeon 245.7, Theseus
240.0, Aphrodite 180.3, Ensorain 166.2, Hephaestus 154.3 (18,047 files).
Largest single blobs: archaeon/frontier/registry/EVENTS.jsonl 85.5 MB;
roles/Nestor/campaigns/z80atlas-2026-09-19/observatory/SPECIMENS.jsonl
84.7 MB; prometheus_math/_region_densification_pilot.json 65.0 MB.

Git history: 13,128 commits reachable from d6b2eeeca (oracle: equals
`git rev-list --count`), 143,310 file changes. Only 2,909 commits (22
percent) carry a recognised "Seat[instance]:" subject prefix; the rest use
"SEAL:", "RESULT:", "Merge", or pre-September styles, so seat attribution by
subject is a lower bound.

## 3. Untracked data on M2 (canonical checkout, 278.7 GB)

    top dir        GB      files   newest      what it is (from names and extensions)
    cartography   162.2   173,551  2026-04-29  convergence/data 128.8 GB jsonl; lmfdb_dump 24.0 GB json;
                                               convergence/logs 4.9 GB in 65,892 files
    vault          56.6    73,038  2026-04-11  vault/models: HF model weights (mamba-2.8b, gemma-2-2b,
                                               Qwen3-4B, phi-3-mini, Qwen2.5-3B, R1-distill-1.5B, rwkv-6 ...)
    charon         28.1     5,509  2026-04-11  james_downloads/mmlkg 24.5 GB .graphml; charon.duckdb 1.18 GB
    apollo         18.7       491  2026-08-20  .hf_cache weights (phi4mini, dscoder13b, granite2b)
    ignis          11.6       513  2026-04-11  results/* with .safetensors and .pt artefacts
    .venv-m2        0.8    24,903  2026-09-17  a Python environment (not data)

By extension: .jsonl 131.8 GB (66,259 files), .safetensors 75.0 GB (24),
.json 29.2 GB (11,427), .graphml 24.5 GB (7), .bin 5.9 GB, .pt 3.1 GB.

Backup root (38.4 GB): cartography/convergence 37.6 GB in 78 files (the
same family as the untracked convergence data; whether they are copies is
NOT established -- no hashes were compared).

C:/Prometheus-data (NVMe, 14.9 GB): evidence/z80atlas_campaign_2026-09-19
14.2 GB in 3 files; Archaeon campaign evidence (portability01,
attribution_arc, contract_v02, envgate01/02, ops_pilot); the live SFE ledger.

## 4. The M1 cluster (345 relations, 4,323 columns in 3 databases)

    database.schema                 relations      MB      est rows
    lmfdb.public                            7  391,612   54,841,693
    prometheus_fire.zeros                   2    1,367    2,011,215
    prometheus_fire.charon_duckdb          14      909    1,238,191
    prometheus_fire.atlas                  43      527      120,226
    prometheus_fire.xref                    2      517    2,135,956
    prometheus_sci.analysis                 2      149      397,584
    prometheus_sci.algebra                  3      135      584,354
    prometheus_fire.ew                     48      103       75,690
    prometheus_fire.agora                  13       67      151,702
    prometheus_fire.viv                    17       56       10,111

Largest relations: lmfdb.public.lfunc_lfunctions 371.8 GB (24.4 M rows est),
nf_fields 10.3 GB, mf_newforms 4.1 GB, bsd_joined 2.7 GB, ec_curvedata 2.2
GB; prometheus_fire.zeros.object_zeros 1.4 GB; charon_duckdb.modular_forms
594 MB; xref.object_registry 514 MB; atlas.source 217 MB; atlas.fact 204 MB.
pgvector: not available on the cluster (Q-001). Extensions installed before
Pan: plpgsql only; Pan added pg_trgm WITH SCHEMA pan.

## 5. SQLite / DuckDB sightings (standing operator request; PAN-25)

Verified by header bytes, not by extension (the extension is a label):

    magic    MB       mtime             path
    sqlite   36.93    2026-09-25 11:20  C:/Prometheus-data/sfe/engine.db          (LIVE SFE ledger)
    sqlite  101.08    2026-09-17 22:54  D:/Prometheus-data/sfe-scratch/sfe_load_5szim74g/load.db
    sqlite   15.98    2026-09-17 19:26  D:/Prometheus-data/sfe/engine.db          (rollback copy)
    sqlite    2.65    2026-09-11 10:31  <canonical>/SerendipityFoundry/SerendipityFoundryEngine/var/engine.db
    sqlite    0.04    2026-04-29        <canonical>/sigma_kernel/a149_obstruction.db
    sqlite    0.03    2026-04-29        <canonical>/sigma_kernel/curvature_experiment.db
    sqlite    0.03    2026-04-29        <canonical>/sigma_kernel/demo_substrate.db
    sqlite    1.06    2026-04-11        <canonical>/archive/seti-v1/seti-pipeline/src/mlflow.db (+ backup copy)
    sqlite    0.43    2026-04-01        <backup>/agents/aletheia/data/knowledge_graph.db (+ worktree copy)
    sqlite    0.04    2026-03-31        <backup>/agents/clymene/data/vault_registry.db
    sqlite    0.02    2026-03-23        <backup>/agents/skopos/data/scores.db
    duckdb 1181.23    2026-04-04 01:59  <canonical>/charon/data/charon.duckdb
    duckdb   20.46    2026-04-11 16:54  <canonical>/noesis/v2/noesis_v2.duckdb
    in git (not sniffed): agents/aletheia/data/knowledge_graph.db, agents/clymene/data/vault_registry.db,
                          agents/skopos/data/scores.db, forge/v3/kill_taxonomy.db
    NOT databases despite the extension (header is neither): cartography/omf5_data/qf5.db,
      cartography/atlas/data/smallgrp/small7/sml512.db, .../id2/id256.ddb (+ backup copies) --
      data files of a small-groups library.

Reported as sightings, not verdicts. The cluster already holds a schema
named charon_duckdb (909 MB); whether it is a complete migration of
charon.duckdb is NOT established here.

## 6. What this run could not see, and the controls it has

- Other hosts (Q-004); other seats' worktrees; contents of binary files.
- The oracle on git history (rev-list count) passed. The inventory itself has
  no independent oracle yet: a second run must reproduce the counts exactly
  for an unchanged tree (next run will compare).
