-- Pan migration 003: document-level embeddings (PAN-31, retrieval v2).
-- One vector per text artifact, built from path + title + heading outline + opening
-- text, so a stronger (slower) model can cover the catalog: ~62.6k documents instead
-- of ~395k chunks. real[] until pgvector exists (Q-001).
create table if not exists pan.doc_embedding (
    artifact_id  bigint not null references pan.artifact(artifact_id) on delete cascade,
    model        text not null,
    dims         integer not null,
    vec          real[] not null,
    doc_blob     text,                 -- blob_sha the vector was computed from (refresh key)
    created_at   timestamptz not null default now(),
    primary key (artifact_id, model)
);
