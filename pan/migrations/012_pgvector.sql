-- Pan migration 012: pgvector in prometheus_fire (PAN-28, QUESTIONS.md Q-001). pgvector 0.8.7 was built and
-- installed on M1 by Atlas under the operator's instruction (comms #2056, file sha256 receipts; steps 1-3 of
-- roles/Pan/docs/PGVECTOR_INSTALL_PACKET.md). This is step 4, Pan's part.
--
-- Deviation from the packet, on purpose: no new halfvec columns. HNSW indexes are built on an EXPRESSION over the
-- existing real[] columns (vec::halfvec(N)), partial on the one model each table holds. Nothing is rewritten (the
-- packet's UPDATE fill would have left ~0.8 GB of dead tuples in pan.embedding), new rows are indexed as they are
-- inserted with no change to the writers, and rollback is DROP INDEX (or DROP EXTENSION vector CASCADE).
-- Queries must use the same expression to hit the index: ORDER BY (vec::pan.halfvec(384)) operator(pan.<=>) $q.
create extension if not exists vector with schema pan;
set local maintenance_work_mem = '1GB';
create index if not exists embedding_hnsw_bge_small on pan.embedding
    using hnsw ((vec::pan.halfvec(384)) pan.halfvec_cosine_ops) where model = 'BAAI/bge-small-en-v1.5';
create index if not exists doc_embedding_hnsw_qwen3 on pan.doc_embedding
    using hnsw ((vec::pan.halfvec(512)) pan.halfvec_cosine_ops) where model = 'Qwen/Qwen3-Embedding-0.6B';
create index if not exists frontier_embedding_hnsw_qwen3 on pan.frontier_embedding
    using hnsw ((vec::pan.halfvec(512)) pan.halfvec_cosine_ops) where model = 'Qwen/Qwen3-Embedding-0.6B';
