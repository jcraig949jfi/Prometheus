-- Pan migration 013: rebuild the HNSW indexes of 012 with a denser graph (m = 32, ef_construction = 200; 012 used
-- pgvector's defaults m = 16, ef_construction = 64). Why, measured 2026-10-10 (roles/Pan/reports/controls/PGVECTOR_*):
-- 012 passed the packet's recall gate (chunk vectors as queries: recall@10 0.966 at ef_search 40) but real QUERY
-- vectors (bge query instruction; 62 frozen queries + 438 chunk headings) reached only 0.659 at ef 40, 0.825 at 100,
-- 0.934 at 400. The same 500 queries against m = 32 / ef_construction = 200, built and measured inside a rolled-back
-- transaction: 0.797 / 0.916 / 0.973 (build 127 s, 548 MB vs 448 MB). The table is locked while the chunk index
-- rebuilds (about two minutes); readers on M2 use the in-process matrix and are not affected.
set local maintenance_work_mem = '1536MB';
drop index if exists pan.embedding_hnsw_bge_small;
create index embedding_hnsw_bge_small on pan.embedding
    using hnsw ((vec::pan.halfvec(384)) pan.halfvec_cosine_ops) with (m = 32, ef_construction = 200)
    where model = 'BAAI/bge-small-en-v1.5';
drop index if exists pan.doc_embedding_hnsw_qwen3;
create index doc_embedding_hnsw_qwen3 on pan.doc_embedding
    using hnsw ((vec::pan.halfvec(512)) pan.halfvec_cosine_ops) with (m = 32, ef_construction = 200)
    where model = 'Qwen/Qwen3-Embedding-0.6B';
drop index if exists pan.frontier_embedding_hnsw_qwen3;
create index frontier_embedding_hnsw_qwen3 on pan.frontier_embedding
    using hnsw ((vec::pan.halfvec(512)) pan.halfvec_cosine_ops) with (m = 32, ef_construction = 200)
    where model = 'Qwen/Qwen3-Embedding-0.6B';
