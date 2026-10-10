-- Pan migration 006: the catalog describes itself (PAN-22). Every table carries its
-- producer command and its meaning; roles/Pan/docs/DATA_DICTIONARY.md is generated from
-- these comments by `python -m pan dictionary`.
comment on table pan.run is 'One row per Pan collector run (inventory, commits, chunk, embed, refresh, frontier-*, consolidate, modelbench...): host, git SHA, params, counts, status. Producer: every pan command.';
comment on table pan.store is 'Every store the program writes on any host: repository tree at a SHA, data roots, databases, schemas, SQLite/DuckDB files (kind file_sqlite/file_duckdb verified by header bytes). Producer: python -m pan inventory.';
comment on table pan.artifact is 'One row per artifact: a git blob at the catalog SHA (source git), a comms message (source comms), or a file on a host (source fs). Kind and seat come from path rules (conventions, not content). Producer: inventory, refresh, comms-index.';
comment on table pan.chunk is 'Text chunks of artifacts with line ranges, a heading path and a stored english tsvector (heading weight A, body B). Producer: python -m pan chunk / refresh / comms-index.';
comment on table pan.embedding is 'Chunk vectors (L2-normalised real[]; pgvector pending, Q-001), several models side by side keyed by model name. Producer: python -m pan embed.';
comment on table pan.doc_embedding is 'One vector per text artifact (path + title + heading outline + opening text), Qwen3-Embedding-0.6B 512 d. doc_blob is the blob the vector was computed from. Producer: python -m pan embed --docs.';
comment on table pan.commit is 'Git history reachable from the catalog SHA; seat/instance parsed from a "Seat[instance]:" subject prefix (a lower bound on attribution). Producer: python -m pan commits / refresh. Oracle: count equals git rev-list --count.';
comment on table pan.commit_file is 'Files changed per commit (name-status, no rename detection): co-change and lineage queries. Producer: python -m pan commits.';
comment on table pan.pg_relation is 'Every table/view/matview/foreign table in the program databases on the canonical cluster, with sizes and row estimates. Producer: python -m pan inventory.';
comment on table pan.pg_column is 'Every column of every relation in pan.pg_relation, with type and comment. Producer: python -m pan inventory.';
comment on table pan.frontier_item is 'Outside research items (arXiv via export.arxiv.org, Hugging Face daily papers) with the seed queries that surfaced them; eos_type uses Eos''s vocabulary and defaults to UNTYPED. Producer: python -m pan frontier arxiv / hf-daily.';
comment on table pan.frontier_embedding is 'Paper vectors (title + abstract) in the SAME space as pan.doc_embedding, for "outside work like this file". Producer: python -m pan frontier embed.';
comment on table pan.hf_model is 'Hugging Face models from seed orgs and discovery queries, with a 16 GB local-fit ESTIMATE (arithmetic on parameter counts; quantized repos marked unreliable). Producer: python -m pan frontier hf-models.';
comment on table pan.intake_call is 'Every external HTTP call made by the intake, for the rate audit (75 percent of documented limits). Producer: frontier intake.';
comment on table pan.model_bench is 'Local model smoke tests: one row per (run, model, probe) with a deterministic verdict (executed hidden tests, exact integers, JSON shape), tokens/s, load time, GPU share. Producer: python -m pan modelbench.';
comment on table pan.lexeme_df is 'Document frequency of every lexeme in pan.chunk (ts_stat); OR full-text keeps the 12 rarest query lexemes. Producer: python -m pan lexdf / refresh.';
comment on table pan.migration is 'Applied Pan migrations with their sha256 (a changed applied migration is an error).';
