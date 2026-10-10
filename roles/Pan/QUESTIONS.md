# Pan -- questions for the operator

Currency: 2026-10-09T14:37Z. The operator reviews this file about every 6
hours (charter C8). No question here blocks the seat: each carries the
DEFAULT the seat runs until answered (MWO-0004 R1). Answer inline under
"ANSWER:" or in chat; the seat moves answered rows to the bottom with
the date. Newest questions are appended at the end of OPEN.

Kinds: HARD = an MWO-0004 Part 4 hard gate (the seat may not proceed on
that item without you); PREF = your preference changes the design, but a
safe default exists; FYI = a fact you asked to be told.

## OPEN

Q-001 | HARD (privileged host change on M1) | 2026-10-09
  pgvector is NOT installed on the M1 cluster (PostgreSQL 17.9, Windows
  build; measured 2026-10-09: `vector` absent from
  pg_available_extensions). Installing it means placing vector.dll and
  the extension's control/SQL files into the PostgreSQL 17 install
  directory on SKULLPORT (administrator rights), then
  `CREATE EXTENSION vector` in prometheus_fire. No server restart is
  needed. May I prepare the install packet (pgvector source tag, build
  or binary, sha256 of every file, exact copy commands, rollback) for
  you or a seat on M1 to execute?
  DEFAULT meanwhile: embeddings live in Postgres as real[] columns and in
  Parquet; vector search runs in process (exact cosine over a cached
  matrix). The schema is written so the switch to a `vector` column and
  an HNSW index is one migration.
  RECOMMENDATION: yes. Server-side HNSW is what makes vector search
  usable from every host without each host downloading the matrix.
  PACKET READY (2026-10-09): roles/Pan/docs/PGVECTOR_INSTALL_PACKET.md --
  pgvector v0.8.7 source build (VS C++ tools, admin x64 prompt), file
  hashes, acceptance gates fixed in advance, rollback.
  ANSWER:

Q-002 | PREF (fleet integration) | 2026-10-09
  Should Pan heartbeat Aporia and be dispatchable by it (CWO-C s7-s9,
  s13) during the 3-day window?
  DEFAULT meanwhile: no heartbeat, not in ops/fleet/QUEUE.json; Pan
  works only its own charter and answers comms messages addressed to it.
  ANSWER:

Q-003 | PREF (topology) | 2026-10-09
  Where should the Parquet/Iceberg lake live? The topology ruling of
  2026-09-16 shares only Postgres and Redis across machines; everything
  else lives on one machine. Options: (a) M2 NVMe only (fast, local;
  other hosts read through Postgres or a later export); (b) M1, next to
  the database; (c) a shared network path readable from every host.
  DEFAULT meanwhile: (a), at the path named by PAN_LAKE on M2's NVMe
  volume. The Iceberg catalog itself is in Postgres on M1, so every host
  can see WHAT tables exist even before it can read their files.
  ANSWER:

Q-004 | PREF (scope) | 2026-10-09
  Inventory scope beyond M2: should Pan index data roots on M1, M3, M4,
  the Ubuntu laptops and harry1 too? That needs a small collector run on
  each host (read-only stat and hash; no writes outside the pan schema).
  DEFAULT meanwhile: the repository at origin/main (every host's
  committed data), M2's local data roots, and every database on the M1
  cluster. A collector script other hosts can run will be committed;
  running it elsewhere waits for your answer.
  ANSWER:

Q-005 | PREF (keys) | 2026-10-09
  For higher rate limits, may the intake use keys already in the keyring
  through keys.py (GitHub token, Semantic Scholar key, a Hugging Face
  token if one exists)? The seat never reads the key files; keys.py does.
  DEFAULT meanwhile: anonymous, polite access only, at 75 percent or
  less of each documented anonymous limit.
  ANSWER:

Q-006 | FYI + PREF (DuckDB) | 2026-10-09
  You are removing SQLite/DuckDB as STORES. DuckDB can also be used as a
  query ENGINE over Parquet/Iceberg with no database file. DuckDB 1.5.1
  is already installed on M2.
  DEFAULT meanwhile: not used. Queries go through pyarrow/pyiceberg and
  Postgres. Sightings of SQLite/DuckDB files are reported in the
  inventory, as you asked of every seat.
  ANSWER:

Q-007 | PREF (shared-cluster disk) | 2026-10-09
  Schema pan now occupies 2.2 GB on the M1 cluster (measured; the
  prometheus_fire database grew from 3,477 MB to 5,698 MB). 791 MB of it is
  chunk embeddings stored as real[]; 1.1 GB is text chunks with their
  full-text index. Pan cannot see M1's free disk from SQL and will not run
  shell commands on M1. What budget may Pan use on M1?
  DEFAULT meanwhile: Pan caps itself at 10 GB on M1 and keeps bulk data
  (Parquet/Iceberg files, vector shards) in the lake on M2's NVMe.
  ANSWER:

Q-008 | PREF (cold data) | 2026-10-09
  The April cold data (cartography/convergence/data, 128.8 GB of JSON Lines
  in the canonical checkout on M2) would shrink to about 22 GB as Parquet,
  measured on samples (reports/COLD_DATA_CONVERSION_SAMPLE_2026-10-09.md:
  per-family ratios 4.0x to 15.5x; one family must NOT be typed, it grows
  2.2x). Do you want Pan to (a) convert these families into the lake as
  Parquet/Iceberg with a line-count oracle, sources untouched; (b) do (a)
  and then have the sources archived or removed (your call alone); or (c)
  leave them as they are until a seat asks for them?
  DEFAULT meanwhile: (c). Nothing converted beyond the measured samples.
  ANSWER:

Q-009 | PREF (user-level toolchain) | 2026-10-09
  The intake lists small Lean provers that fit the GPU (Goedel-Prover-V2-8B,
  Kimina, Pythagoras-Prover-4B). Testing them honestly needs a Lean 4
  toolchain as the verifier (elan, user-level, plus a Mathlib cache of
  several GB on M2's NVMe); without it a prover test would score the
  model's own claim of success. May Pan install elan + Mathlib for the
  user on M2 (no administrator rights, no system change)?
  DEFAULT meanwhile: not installed; provers stay catalogued, untested.
  ANSWER:

Q-010 | PREF (shared service on M2) | 2026-10-09
  The new release feeds show Ollama v0.40.2 (2026-10-08); M2 runs Ollama
  0.35.0, which every local-model seat on M2 shares. Pan's model numbers
  (smoke tests, HumanEval+) were measured on 0.35.0. Should Pan upgrade
  Ollama on M2, leave it to the seat that owns M2's model service, or leave
  it alone?
  DEFAULT meanwhile: leave it alone (a shared service; an upgrade can change
  model behaviour under other seats' runs). Pan now records the version in
  every benchmark run (pan.run params; today's 8 runs backfilled as 0.35.0).
  ANSWER:

Q-011 | PREF (fleet work, outward-facing) | 2026-10-10
  You want platform-wide code reviews done by the agents already working,
  not by you. Pan can build the parts inside its lane: (1) a ranked REVIEW
  QUEUE from the catalog (recently changed modules per seat, code no passing
  test imports, hard-coded hosts/paths, test files that fail in a clean
  sandbox), (2) a CALIBRATION SET of seeded bugs (PAN-34's sandbox can splice
  a known-broken function in) so each reviewer's hit rate is measured, and
  (3) a findings table and a portal view. Handing review units to other
  seats (Fabric tasks or comms, author never reviews own code, reviewers
  must run the code) changes their work, so it is yours to approve.
  DEFAULT meanwhile: Pan builds (1)-(3) after PAN-34 closes; no review task
  is dispatched to any seat until you answer.
  ANSWER:

Q-012 | PREF (trust store on M2) | 2026-10-10
  The new Machines tab measures the Linux nodes over read-only ssh from M2.
  ubu001-003 answered; ubu004, ubu005 and ubu006 were refused because M2 has
  never stored their ssh host keys (Achilles provisioned them from ELSA; no
  entry, not a changed key). Adding a host key is a trust decision on your
  admin machine, so Pan did not do it. May Pan accept those three keys on
  first contact (ssh StrictHostKeyChecking=accept-new; a changed key would
  still be refused)?
  DEFAULT meanwhile: no; those three rows show the register's values,
  labelled "register only".
  ANSWER:

## ANSWERED

(none yet)
