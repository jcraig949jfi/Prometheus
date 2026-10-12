-- Pan migration 005: lexeme document frequencies over pan.chunk (rebuilt by
-- `python -m pan lexdf` and by refresh). Used by OR full-text search to keep only the
-- rarest query lexemes: long queries (commit subjects of 20+ words) made the v1/v2 OR
-- query match most of the corpus and run 30+ s each (measured 2026-10-09).
create table if not exists pan.lexeme_df (
    lexeme   text primary key,
    ndoc     integer not null,
    nentry   integer not null
);
