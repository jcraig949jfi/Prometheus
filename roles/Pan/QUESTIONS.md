# Pan -- questions for the operator

Currency: 2026-10-10T20:24Z. The operator reviews this file about every 6
hours (charter C8). No question here blocks the seat: each carries the
DEFAULT the seat runs until answered (MWO-0004 R1). Answer inline under
"ANSWER:" or in chat; the seat moves answered rows to the bottom with
the date. Newest questions are appended at the end of OPEN.

Kinds: HARD = an MWO-0004 Part 4 hard gate (the seat may not proceed on
that item without you); PREF = your preference changes the design, but a
safe default exists; FYI = a fact you asked to be told.

## OPEN

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
  FACT 2026-10-10 (Atlas, #2056, measured on M1): the cluster's data directory
  is on SKULLPORT C:, 90 GB free of 954 GB (91 percent used); F: has 2.1 TB
  free. Schema pan is now 3.6 GB (3,590 MB incl. 0.6 GB of HNSW indexes from
  PAN-28), so the 10 GB cap would be 11 percent of what C: has left.
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
  UPDATE 2026-10-10T20:21Z: Achilles added ubu007 (.3) and ubu008 (.231) to
  the fleet (#2099). ubu007 is refused the same way (no stored host key), so
  the question now covers ubu004-ubu007. ubu008 is different: ssh to
  192.168.1.231 port 22 timed out (not a key question; the node may only
  answer on its other address .232, or block port 22). All five rows now show
  Achilles' live hardware read of 2026-10-10, labelled "register + Achilles
  read", never "measured".
  UPDATE 2026-10-12T11:20Z (probe for the dashboard republish):
  - ubu001-003 answer.
  - Refused for lack of a stored host key: ubu004, ubu005, ubu006, ubu008
    (it now answers on port 22) and ubu009 (new in the register).
  - ubu007 (192.168.1.3) timed out on port 22.
  - The question now covers ubu004-006, ubu008 and ubu009. The default is
    unchanged: Pan adds no host keys.
  UPDATE 2026-10-12T13:22:09Z (Achilles, comms #2215):
  - A vetted source now exists at origin/main:infra/ubuntu_nodes/
    known_hosts.fleet (commit 8b2c14270). It holds the ed25519 host keys for
    ubu001-006, 008 and 009, both addresses each.
  - Achilles read them from /etc/ssh/ssh_host_ed25519_key.pub over his
    existing authenticated sessions; they were not accepted on first sight.
    ubu007 is absent (powered off).
  - If you approve, Pan would point its probe at that file
    (UserKnownHostsFile) rather than merging it into ~/.ssh/known_hosts.
  - Achilles asked Pan to stop probing ubu007 (HOLD) and ubu009 (SOAK).
    Done: PROBE_EXCLUDED in pan/fleet.py.
  ANSWER:

Q-013 | PREF (M2 memory; your machine) | 2026-10-10
  PAN-34's frozen size arm (A3: does qwen2.5-coder:32b beat the 14b by
  >= 0.08?) cannot run on M2 without spilling into system RAM. With the
  context PAN-34 uses (8192), Ollama sized it at 22 GB against the 16 GB GPU,
  ran it 35 % on the CPU, and llama-server took 14 GB of RAM. M2 reached 89 %
  RAM and Claude Code killed the run at about 23:05Z (low-memory guard).
  Pan stopped the leftovers, unloaded the model and released the leases by
  23:10Z (RAM back to 44 %); no rows of that run are used. Run it anyway, at
  a time you choose with nothing else on M2 (it holds ~14 GB of RAM for
  1-2 h), or drop the arm?
  DEFAULT meanwhile: dropped. Reported as NOT RUN (infeasible within M2's
  memory), not as a result. gpt-oss:20b@4096 (the last PAN-34 config) runs
  only after a load check shows it 100 % on the GPU.
  ANSWER:

Q-014 | PERMISSION (database roles on M1) | 2026-10-11
  Pan's MCP prototype (PAN-44) enforces access in the application plus a
  server-side read-only session, because every program session connects as
  the superuser postgres (RLS does not bind it; foundation map s6). Least
  privilege would be a login role (e.g. pan_mcp_ro) with SELECT on only
  pan.artifact/chunk/link/doc_embedding and atlas.fact/proposition/
  blind_spot, plus RLS on pan.artifact/pan.chunk keyed on access_class.
  The role prometheus_read exists but has no grants and cannot log in.
  This is a production authorization change, which the directive does not
  grant. Create the role (Pan writes the migration; the DBA applies it)?
  DEFAULT meanwhile: no. The MCP stays at application-level enforcement
  plus default_transaction_read_only, as recorded in
  MCP_INTERFACE_PROTOTYPE.md.
  ANSWER:

Q-015 | PREF (seat tooling) | 2026-10-11
  Should seats get Pan's MCP server by default, via a project-scoped .mcp.json
  in the canonical repo, or only by local opt-in (claude mcp add pan --
  <venv python> -m pan.mcpserve, run from a checkout)?
  DEFAULT meanwhile: local opt-in only. Nothing is registered anywhere. The
  directive approves a prototype, not a deployment.
  ANSWER:

Q-016 | PERMISSION (scheduled task on M2) | 2026-10-11
  After the window, should Pan's maintenance run unattended? That means a
  nightly Windows scheduled task on M2 running `pan refresh`, `pan atlas
  snapshot` and `pan frontier daily` (CPU embeddings), registered as a
  MONITORS row with a bound and a watcher (Aporia). Or should it stay
  session-driven, run by the successor seat (CONTINUITY_HANDOFF.md s0)?
  DEFAULT meanwhile: session-driven. Pan installs no scheduled task. Index
  currency decays visibly (every record carries its blob, commit and
  index_current) rather than silently.
  ANSWER:

Q-017 | SECURITY (outside Pan's authority) | 2026-10-11
  PAN-47 found committed files with credential-shaped CONTENT (comms #2129;
  values never read). The likeliest real ones:
  - three apollo/configs/config_v2d*.yaml and apollo/scripts/evolution_monitor.py
    (an "sk-" + 32-character provider-key shape);
  - evidence_wiki/config.json (a non-empty db_password);
  - apollo/scripts/launch_bakeoff_candidate.ps1.
  Pan has purged all 132 matching files from its index (paths kept). The
  values remain in git history and the working tree. Rotate the keys or
  passwords, and remove the values from the files (and from history)?
  DEFAULT meanwhile: Pan purges its index and nothing else. Owners (Apollo,
  Mnemosyne, Harmonia, Charon, Aporia) are told; rotation is theirs or
  yours.
  FACT (comms who, 2026-10-11T13:32Z): every owning seat is OFFLINE. Last
  syncs: Apollo 2026-09-11, Charon 09-11, Mnemosyne 09-18, Harmonia 10-01,
  Aporia 10-06. #2129 has no live reader but you, so in practice rotation
  is yours (or whoever you wake).
  URGENT FACT (2026-10-11T17:1xZ): origin is github.com/jcraig949jfi/Prometheus,
  and an anonymous GitHub API read returns visibility PUBLIC. These values
  have been publicly readable since they were committed:
  - apollo/configs/config_v2d2*.yaml, config_v2d3.yaml: 2026-04-04
    (6f042458b);
  - apollo/scripts/evolution_monitor.py: 2026-04-06 (d3381beaf);
  - apollo/scripts/launch_bakeoff_candidate.ps1: 2026-05-22 (e94ca44b1);
  - evidence_wiki/config.json: 2026-09-01 (c711c5bf6);
  - roles/Aphrodite/engine/accel/azure/azure.env: 2026-09-23 (96503f81a).
    This is a committed .env file, which Pan never opens; it may be a
    template.
  Treat any real key in these files as compromised. Rotate first. Making the
  repo private or rewriting history does not un-leak a value that was
  already public. Pan has taken no outward action.
  ROTATION RECIPE (from code, no values read): evidence_wiki/ew/db.py
  load_config states that the committed config.json carries cleartext
  db_password / auth_token / machine_tokens "as a V0 trusted-LAN default".
  Overrides need no code change. Precedence is: environment variable >
  untracked evidence_wiki/config.local.json (gitignored) > config.json.
  After rotating:
  - put the new values in each host's config.local.json or environment;
  - then blank them in config.json.
  The canonical checkout D:\Prometheus has a config.local.json; Pan's
  worktree does not. Pan will lose database access at rotation until one is
  supplied. That is expected; do not delay rotation for it.
  ANSWER:

Q-018 | PERMISSION (LAN service) | 2026-10-12
  Host the Data Map dashboard locally on an internal website, in addition to
  the claude.ai copy? Pan's proposed shape:
  - static files only: HTML plus the same JSON datasets, d3 vendored;
  - rebuilt by `pan refresh`;
  - served read-only by a tiny static server bound to the LAN address, with
    the firewall limited to 192.168.1.0/24;
  - no database connection in the web process;
  - kept running by a scheduled task (the same decision as Q-016).
  The Sagacity directive excluded new network-facing services, so this needs
  your word, plus the host and port.
  DEFAULT meanwhile: no local site. The claude.ai dashboard is republished
  by Pan's loop.
  ANSWER:

Q-019 | RE-RUN (intake stopped under memory pressure) | 2026-10-15
  Today's daily intake started 14:21:03Z on CPU after a load sample (M2 CPU
  6%, 14.4 GB free). ComfyUI (D:\skullport-gfx, not Pan's) started at
  14:30:28Z and took 11.4 GB; the session host then stopped the intake for
  low memory. Pan stopped its own leftover intake processes at 14:32:21Z
  (they still held ~5.4 GB) and marked the run KILLED.
  What finished: arXiv, HF daily, HF models, 35 feeds (38 new items) and
  29 GitHub owners (20 new items). What did not: vectors for the new items,
  and the 2026-10-15 digest.
  The host's rule is not to restart a stopped job unprompted. Re-run it?
  DEFAULT meanwhile: not re-run by Pan. The loop ends 2026-10-16T10:40Z,
  before tomorrow's intake; whichever run comes next embeds everything that
  has no vector, so nothing fetched is lost.
  ANSWER:

Q-020 | PREF (identity-learning coupling pre-registration) | 2026-10-16
  In chat before the 06:50Z tick you proposed an Identity-Learning
  Coupling Invariant (identity anchor, mutable theta, self/other boundary).
  Pan replied in chat with a minimal door-world design, T1-T6: attribution,
  same event / different update, contingency degradation, persistence and
  transplant, a transcript twin (the performative-identity control) and
  fabricated continuity. Actor labels are stripped so the measurement
  cannot carry its answer. Should Pan write it as a pre-registration
  under docs/sagacity before the loop ends at 10:40Z?
  DEFAULT meanwhile: not written; the design stays in chat. It is outside
  Pan's backlog, and nothing is run either way.
  ANSWER:

## ANSWERED

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
  EXECUTED 2026-10-10 (no ANSWER line was written here): Atlas built and
  installed pgvector 0.8.7 on M1 under the operator's chat instruction
  ("help get the pg_trgm installed, and anything else PAN might need"),
  relayed in comms #2056 with sha256 receipts (vector.dll cda04ce6...,
  vector.control 4c972b1a...). Pan verified `vector 0.8.7` in
  pg_available_extensions and did step 4 itself: migration 012 (extension in
  schema pan + HNSW expression indexes, no new columns) and 013 (denser
  graph after real query vectors recalled only 0.659 at ef 40). Controls
  roles/Pan/reports/controls/PGVECTOR_20261010T132524Z.json PASS 5/5.
  Rollback stays DROP EXTENSION vector CASCADE.


(none yet)
