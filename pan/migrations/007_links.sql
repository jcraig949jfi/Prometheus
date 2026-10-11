-- Pan migration 007: the reference graph (charter C4, pivots). One row per (citing
-- artifact, cited artifact): a path mentioned in the citing artifact's text that
-- resolves to a catalogued git artifact, exactly or relative to the citing file's
-- directory. Ambiguous bare file names are NOT linked. Producer: python -m pan links.
create table if not exists pan.link (
    src_id     bigint not null references pan.artifact(artifact_id) on delete cascade,
    dst_id     bigint not null references pan.artifact(artifact_id) on delete cascade,
    n_mentions integer not null,
    how        text not null,            -- exact | relative
    primary key (src_id, dst_id)
);
create index if not exists link_dst_idx on pan.link (dst_id);
comment on table pan.link is 'Reference graph: citing artifact -> cited artifact, from file paths written in text (exact or relative to the citing file); bare ambiguous names are not linked. Producer: python -m pan links.';
