"""Session-independent local runner (C-013-T022, P-1; rso/scale/LONG_DURATION_EXECUTION_ARCHITECTURE.md s3-s4).

The job, not the conversation, owns its state. A run directory holds an immutable run manifest, one
Moonshot-identity checkpoint chain per seed partition, a content-addressed object store, append-only event
shards and a final account. A detached host supervisor drives one worker process at a time; any of them, and
the session that launched them, can die, and a later supervisor resumes from the last verified checkpoint.

Modules: engine (the runtime-agnostic interface), aether (first client, read only), store, lease, run
(manifest, chains, publication), resume (s3.8 verification), worker, supervisor, account, control, fire_test.
"""
