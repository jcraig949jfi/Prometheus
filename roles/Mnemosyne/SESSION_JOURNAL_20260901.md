# Mnemosyne Session Journal — 2026-09-01 (world-state refresh, read-only)

## Session Overview

First Mnemosyne session since 2026-04-29. James's directive: get the state of
the world up to date; **no ingestion, no action**. Everything this session did
was read-only against the live databases plus two documentation writes
(`mnemosyne/STATE.md` rewrite, this journal). Zero database writes, zero queue
changes, zero bus posts.

Identity: Claude session under @roles/Mnemosyne per James. Running on M1.

---

## What I verified (live queries, 2026-09-01)

1. **Postgres spine is local and healthy on M1** — PostgreSQL 17.9 on
   localhost serves lmfdb (365 GB), prometheus_sci (320 MB), prometheus_fire
   (2.76 GB). The `.176` host in my April docs is dead.
2. **The spine is in active daily use** — `agora.machine_probes` (112K rows)
   and `agora.intelligence_outputs` (13K rows) have entries written TODAY;
   Pronoia (M4) and Elenchus (M2) heartbeating online.
3. **Redis retired → PgRedis** (`prometheus_fire.bus`), but the bus itself is
   nearly unused (8 entries ever, all tables empty now). Coordination moved to
   the `agora.*` relational tables.
4. **DuckDB retired** → `prometheus_fire.charon_duckdb.*` (14 tables, 1.24M
   rows).
5. **The rekey campaign landed**: xref.object_registry 134K → 2,118,642;
   zeros.object_zeros 121K → 2,009,089 (real COUNT(*), not estimates).
6. **zeros.dirichlet_zeros is now 0** (was 184,830; rows exist in the
   charon_duckdb mirror). Looks like dedup, but undocumented — flagged as an
   open question in STATE.md, not "fixed."
7. **sigma schema evolved** — 7 tables (was 3), 1,079 claims recorded,
   claims columns differ from the 04-29 MVP. Substrate-Tester fire commits
   own that history.
8. **nf_fields is FULL** (22.18M rows) — the old P6 partial-pull item is done.
9. **Queue**: REQ-001 (Bloom Erdős) and REQ-002 (MathNet) both still open;
   HELD per today's no-ingest directive. Statuses left untouched (append-only
   discipline; a hold is a directive, not a resolution).

## What was NOT done (deliberately)
- No ANALYZE (it's overdue, but it mutates stats — "take no action").
- No queue status edits, no agora/bus posts, no RESPONSIBILITIES.md rewrite.
- No git commit — the working tree carries another seat's in-flight work on
  branch daedalus/serendipity-foundry-engine; the two files written
  (`mnemosyne/STATE.md`, this journal) are left for James to commit or for a
  pathspec-scoped commit when authorized.

---

# Addendum (same session, later): data-existence audit + legacy-store sweep

## Data-existence audit (James-approved; read-only vs DBs)

Artifacts: `mnemosyne/data_existence_audit_20260901.{py,jsonl}` +
`mnemosyne/DATA_EXISTENCE_AUDIT_2026-09-01.md`. Key results over 534
catalog problems: 253 UNCLAIMED_CANDIDATE_DATA (bucket-C "no data coupling"
defaults whose subdomain HAS loaded spine data — number_theory 75,
additive_combinatorics 41, combinatorics 33, discrete_geometry 32, …),
222 NO_KNOWN_COUPLING, 22 pure-compute, 20 claimed-and-present, 17
requires-extension, 0 claimed-but-absent (no drift).

Join-integrity defects found in the catalog files (reported, not fixed):
- MATH-0491/0492/0493: id COLLISIONS — same id, two different problems.
- 18 authored A2 specs appended as duplicate triage lines over old
  bucket-C rows (safe for last-wins readers like backlog_gen.py:67 only).
- 24 questions (MATH-0514..0537) appended post-May, never triaged.

## Legacy-store inventory (Explore agent, read-only) + todo notes

Full verdicts recorded in STATE.md ("Legacy non-Postgres stores"). Headline:
**kill_taxonomy was never migrated because my own migrate_m2.py:231 loader
reads the wrong source and returns 0 as success** — 21 kills live in
`forge/v3/kill_taxonomy.db` (SQLite) and Ergon's hypothesis gate reads them
from there today. Also: charon/src IS repointed (fa8f625a1; the 06-24 audit
is stale on this), and the real duckdb-deletion blocker is ~180 legacy
read-only call sites in cartography/harmonia/koios.

Per James: placed `todo_20260901.md` in roles/{Charon, CrossDomainCartographer,
Harmonia, Koios, Ergon} — each specifies the outstanding repoint with
file:line, and the protocol: flip Status to DONE, Mnemosyne sweeps
`roles/*/todo_*.md`, and the `.duckdb`/SQLite files are deleted only after
all seats flip (row-for-row verification first). Charon's note was REVISED
mid-session when the inventory showed her main repoint already landed.

---

# Addendum 2 (same session): EVIDENCE WIKI V0 BUILT — role expansion executed

James issued the MNEMOSYNE ROLE EXPANSION + EVIDENCE WIKI / EVIDENCE TENSOR
V0 charter (committed verbatim at
`roles/Mnemosyne/prompts/CHARTER_EVIDENCE_WIKI_V0_2026-09-01.txt`, sha256
c81a21278fd084b4e40a2ef4403f422043599cc5fe000c631dacbaa758ba0ead).
V0 was built and adjudicated in-session. Everything lives under
`evidence_wiki/`; full verdict in its README + `benchmarks/results_v0.json`.

Headlines:
- Canonical substrate: schema `ew` in prometheus_fire (append-only, staged
  writes, content-addressed IDs, derived-view quarantine). 81 real findings
  from 9 seats ingested with verbatim quotes + spans + commits; 46 negative.
- REST service live on 0.0.0.0:8377 (firewall rule scoped to LAN), wiki UI
  at /wiki, agent skill `.claude/skills/evidence-wiki/`.
- Gates G1-G5, G7-G18 PASS (incl. 4-machine-identity demo, concurrent-writer
  single-record, idempotent retries, contamination quarantine,
  delete+rebuild hash-stable). G11 cross-host pending peers online.
- **G6 = TENSOR_NOT_YET_JUSTIFIED**: curated canonical labels beat
  everything on held-out cross-vocabulary pairs (MRR 0.605 vs CP 0.023);
  marginal baseline beats CP/Tucker/TT on missing cells; CP seed-unstable.
  The tensor thesis was allowed to lose, per charter §28.
- North-star loop closed once: A-003 x B-015 x C-004 cross-link produced a
  registered falsifiable Gen-2 experiment candidate (H-9b0a7922015e,
  HYPOTHESIZED).

Service ops note: no watchdog yet; restart by hand after reboot
(`python -m ew.service` in evidence_wiki/). V1 list in the review packet.

## Files changed this session
- `mnemosyne/STATE.md` — full rewrite (2026-09-01 snapshot) + legacy-store section
- `roles/Mnemosyne/SESSION_JOURNAL_20260901.md` — this file (NEW)
- `mnemosyne/data_existence_audit_20260901.py` + `.jsonl` +
  `mnemosyne/DATA_EXISTENCE_AUDIT_2026-09-01.md` (NEW)
- `roles/{Charon,CrossDomainCartographer,Harmonia,Koios,Ergon}/todo_20260901.md` (NEW)
- `evidence_wiki/**` (NEW subsystem) + `.claude/skills/evidence-wiki/SKILL.md`
- `roles/Mnemosyne/prompts/CHARTER_EVIDENCE_WIKI_V0_2026-09-01.txt` (NEW)

---

# Addendum 3 (2026-09-02): V1 QUALIFICATION CAMPAIGN EXECUTED

V1 charter committed verbatim (sha256 52d4a256...) + PREREGISTRATION_V1
frozen at a2898d196 BEFORE any campaign agent launched. Full adjudication in
evidence_wiki/benchmarks/gates_v1.json; docs under evidence_wiki/docs/.

Headline verdicts (none softened):
- G2 PASS: 4 independent annotators, mean any-overlap 0.956; free-form
  condition C converges 0.833 after blind normalization.
- G3 PASS: CANONICAL_MECHANISM_LAYER_QUALIFIED - 44 annotator-defined
  cross-agent pairs retrieved by annotator labels at MRR 0.451 vs 0.165 best
  text baseline; Mnemosyne excluded from both sides. Same-model caveat
  recorded.
- G7 METABOLIZATION_NOT_DEMONSTRATED: 8/8 task ties at 4/4 - the frozen
  checklist saturated; controls avoided every trap via repo search.
  Instrument-ceiling diagnosis + V2 design recorded.
- G8 PASS (phenomenon, not differential); G9 ADJUDICATED_NULL; G10 PASS on
  genuine pair B-025 vs B-001; G11 PENDING_PROSPECTIVE (15 blinded cells,
  sealed methods); G19 TENSOR_NOT_JUSTIFIED retained (147 coords).
- G4 demonstrated with real need: cross_domain_bridge + 3 substrate terms
  registered from convergent annotator demand.
- Corpus: 81 -> 111 findings; held-out corpus ingested with CONSENSUS labels
  (not the curator's); curator-community divergence 0.30-0.37 disclosed.
- Ops: watchdog + autostart (G15 kill/restart PASS), per-machine tokens,
  fixture namespace (G13), telemetry endpoint, write-path suite 16/16.
- G14 PARTIAL: cross-host probes await M2/M3/M4 pulling the branch.

23 subagents used: 3 harvest/1 heldout, 16 designers, 6 annotators + 1
normalizer (numbers per notifications; harvest agents from 09-01).

---

# Addendum 4 (2026-09-02): V2 MEMORY-ADVANTAGE CAMPAIGN EXECUTED AND ADJUDICATED

Charter sha 7e5d2dae...; prereg + task corpus + sealed gold (731b5b8c...)
frozen at cab825adc BEFORE any designer. ~70 agents: 2 pilots, 40 A/B
designers (sonnet+haiku), 5 retrieval + 5 pack designers, 4 blind scorer
agents, 7 quarantine replacements. Full adjudication: benchmarks/gates_v2.json.

VERDICT: RETRIEVAL_ADVANTAGE_WITHOUT_DESIGN_ADVANTAGE (MODEL_SPECIFIC).
- Retrieval: sonnet wiki arms +0.300 core-gold recall (+0.405 negative
  evidence, corrections doubled); haiku +0.011; pooled +0.151 fails the
  frozen 0.25 bar -> MODEL_SPECIFIC_ADVANTAGE_ONLY. Arm C EVIDENCE PACK
  strongest of all (0.90 core, 1.00 corrections) - the V3 interface.
- Design: blind 2-scorer composite delta -0.016 (threshold +0.40), 8/19
  wins -> NOT DEMONSTRATED; instrument ceiling flagged per frozen band
  (control 3.72 > 3.4). Clean-task delta -0.234 = exploratory
  retrieval-noise/anchoring harm signal.
- G9 misleading-resistance PASS (0 adoption everywhere); G17 blind scoring
  inter-rater 0.882/0.982.
- LEAKAGE EVENTS (both preserved, protocol-handled): (1) haiku controls
  violated the evidence_wiki access boundary 7/15 attempts (sonnet 0/12);
  cells quarantined + identically re-run; T10-haiku excluded after second
  violation. (2) THE BIG ONE: the agent harness injects the operator's
  project auto-memory into every subagent - designers cited memory doctrine
  that exists nowhere in the repo; Prometheus already runs an implicit,
  provenance-free memory channel that pre-seeded ~5 tasks' gold in BOTH
  arms. Parity held; wiki delta is a lower bound; James asked to rule on
  ingest-vs-isolate (HUMAN_AUDIT_PACKET_V2 q1).
- s17 ontology rulings encoded as HUMAN v2 registry rows. Gap slate still
  sealed. Tensor untouched. G14 cross-host still NOT_QUALIFIED.

---

# Addendum 5 (2026-09-02): PEW V3 EXECUTED — explicit memory, fossil record, incubator prep

Charter sha 0d24ff4f...; prereg 4f8f6c875 + AMENDMENT 1 (20560088e,
committed before any arm output was read). Full gates: benchmarks/gates_v3.json.

- AMBIENT MEMORY: fully inventoried (226 files, per-file sha manifest,
  LEGACY_AMBIENT_MEMORY packet). G3 FAIL, probe-proven three ways: the
  index is injected into ALL subagents, worktree does not isolate, and
  physical directory relocation does not isolate (parent-session caching).
  AMBIENT_MEMORY_CANNOT_YET_BE_SAFELY_REMOVED; DECLARED mode qualified.
- EXPLICIT MEMORY: s6 chain live (memory_artifacts + memory_influences).
  Execution experiment (deterministic, sealed truth 11f16bdd, no LLM
  judge): A 5/5/6 vs B(pack) 6/6/6 -> delta +0.111 = frozen MARGINAL band,
  floor-bounded by G6 saturation (control competence 0.867 > 0.80 band).
  The benefit concentrated exactly where knowledge, not skill, was binding
  (the dirichlet mirror). B agents verified pack claims live and twice
  OVERRODE the pack after verification (G9 anti-anchoring PASS).
- FOSSIL RECORD: 11,731 rows of REAL SFE history metabolized by reference
  (mode=ro, entry-hash anchored). 5 mining query classes at <=7ms; SVD
  exercise; q3 blocked by SFE phenotype coverage 2/6006 -> requirement
  handed upstream: Incubator organisms must emit phenotype observations.
- REINTERPRETATION: I1->I2 supersession on a hash-verified immutable event.
- FIREWALL: PEW-NATIVE surfaces scanner-clean vs live prose vocabulary.
- DISTRIBUTED: 4-identity concurrent ingest clean (0 dupes under retry +
  crash replay); envelope 7 / 712 / 8191 ev/s; cross-host still NOT READY.
- INCUBATOR DECISION: READY_WITH_LIMITATIONS (see gates_v3.json).
- V3 FROZEN; packet at evidence_wiki/V3_REVIEW_PACKET_2026-09-02.txt.
  Per charter s27: STOPPED here. No V4, no mass ingestion.

## ADDENDUM 6 — 2026-09-02 — V3 CLOSEOUT AND FREEZE
Closeout charter received (READY_WITH_LIMITATIONS accepted; NO V4); committed
verbatim, sha 0af9193d60ef0c0beb061bdfd55cd05b5787ec82b84c2863a7efd3e3378ef893.
- AMBIENT: LEGACY_AMBIENT_MEMORY ratified as distinct provenance class;
  disposition doc + pack-build guard in evidence_pack.py (_record drops any
  item whose claim or evidence packet is legacy_ambient_memory); guard PROVEN
  on both shapes via rolled-back probes. Corpus re-hashed: MEMORY.md sha
  05dbe05e... UNCHANGED since V3 audit; 226 files; inventory packet
  SP-a960f1327491.
- EXPERIMENT CLOSED verbatim (A 0.889 / B 1.000 / +0.111 / MARGINAL /
  SATURATED) in docs/V3_EXPERIMENT_CLOSURE.md; no rescoring, no extension.
- X5 amendment: docs/SCORING_POLICY_AMENDMENT_X5.md (6 mandatory prereg
  items; future-only).
- PHENOTYPE BOUNDARY: SFE owns emission, PEW consumes by hash reference;
  docs/PHENOTYPE_CONSUMER_REQUIREMENT.md + roles/Daedalus/todo_20260902.md.
- POOLING: ThreadedConnectionPool(2,16) behind ewdb.connect() proxy; first
  deploy hit a lazy-init RACE (two pools; 3/4 workers 500'd) -> lock +
  double-close guard; requalified: distributed test G17/G19 PASS, firewall
  PASS, replay adds 0 rows. Envelope now 48 / 3633 / 3616(replay) ev/s
  (was 7.1 / 712). G21 rerun reads false ONLY because the harness expects
  exactly 600 synthetic rows on a clean slate; append-only accumulation =
  2600 stored, 2600 DISTINCT, zero duplicates.
- MEMORY-CLEAN PROCEDURE written, labeled UNQUALIFIED
  (docs/MEMORY_CLEAN_SESSION_PROCEDURE.md); a running session cannot certify
  its own cleanliness.
- CROSS-HOST: BLOCKED — M2-M4 have not pulled mnemosyne/evidence-wiki-v0
  (remote tip 869755c2b; no peer evidence). Explicitly reported as such.
- FROZEN.md placed at evidence_wiki/ root. Seat state:
  PEW_FROZEN_WAITING_FOR_INCUBATOR.

## ADDENDUM 7 — 2026-09-03 — FIRST INTEGRATION READINESS (Harmonia handoff)
Charter committed verbatim, sha 54fe6133b891ea3f19fc0ad9082a3480c33ba006e74b
863d5837b82ef4342197. Freeze reopened under criterion 1 (real consumer
requirement); scope held to integration defects.
- DEFECTS FOUND AND FIXED (all pre-existing, all silent-failure class):
  (1) encounter_id was PK but Proteus mints it from the encounter SPEC, so a
      second execution of the same spec was dropped behind HTTP 200. Migration
      006 keys (encounter_id, run_id); differing duplicate now 409. 10,452
      rows preserved.
  (2) players/seed/budget/ecology/resources_used/occurred_ts were COLUMNS but
      not in the ingest model -> producer sends them, gets 200, data vanishes.
      Now accepted+persisted; unknown fields 422 (extra=forbid).
  (3) No read-back or query path existed for fossil rows at all. Added GET
      by encounter, and by run_id/world_id/player_id/episode_id, plus
      world/player anchor registration + reads.
  (4) MINE, caught by the battery: timestamps compared as STRINGS made an
      identical replay look like a conflict (409) across timezones; jsonb
      read back as dict vs its serialization did the same on anchors. Both
      now compare as instants / JSON-normalized. Wire format is UTC ISO-8601.
- BATTERY: integration/pew_battery.py, E0-E12 + anchor gate = 14/14 PASS.
  Write proved by INDEPENDENT read-back (different endpoint + direct SQL).
  E11/E12 use a REAL SFE run (exp_85723eed:wrk_cadfa047, world
  wld_4ec098bcd0b3bdf280e543d4) written in namespace 'test'.
- HARNESS FINDING: test_distributed_v3.py seeded its RNG with hash(machine),
  which PYTHONHASHSEED randomizes per process -> every rerun submitted
  DIFFERING content under the same encounter ids, and the old ON CONFLICT DO
  NOTHING hid it. Now sha256-seeded + per-run run_tag; G21 scored by the
  invariant (stored==distinct for this run).
- M2 PATH: verified over LAN 192.168.1.202:8377 — M2 token accepted, M2 token
  claiming M1 = 401, anonymous = 401. Traffic still originated on M1.
- Schema 3, fossil contract pew.fossil.v1. Runbook:
  docs/HARMONIA_FIRST_INTEGRATION_PEW.md.

## ADDENDUM 8 — 2026-09-03 — WORLD-PROVENANCE SEAM CLOSURE
Charter committed verbatim, sha 18615e89a8aa386faf258e54ee59d44cf9e468731f56
0194735d2cc1d4b0e012.
- Q1 sfe_entry_hash = SFE events.entry_hash, decided from DATA not names:
  5452/5452 prod anchors are in the events.entry_hash universe; blob_hash and
  artifact_id overlap by ZERO; (event_id, entry_hash) pairs verify 5452/5452
  against the live ledger. head_hash is NOT structurally separable (all 283
  live head_hash values ARE some event's entry_hash), so the class is pinned
  by REQUIRING the evt_-prefixed sfe_event_id, which 100% of historical rows
  already carry. Shape ^sha256:[0-9a-f]{64}$ enforced.
- Q2 binding = typed FK columns on ew.evidence (encounter_id,
  encounter_run_id -> fossil_encounters(encounter_id, run_key)). Relations
  were REJECTED as the mechanism: a relation carries one dst_id but encounter
  identity is a PAIR, so it would need an invented composite-string
  convention, and a new relation_type would broaden the ontology.
- Q3 migration 006 IS live (PK (encounter_id, run_key) present; service was
  already serving schema 3). 007 applied this pass; 124 evidence / 11,754
  encounter rows preserved exactly.
- DEFECT REPRODUCED FIRST (seam/D_silent_loss_BEFORE.txt): all 5 ordinary
  ingress models accepted world_id/run_id/encounter_id with HTTP 200 and
  discarded them. Fixed with extra=forbid; regression test added.
- MY OWN DEFECT, caught by gate G: the seam battery's ordinary evidence landed
  in ew.evidence_prod, because ew.object_namespace had NO API path — it had
  only ever been written by hand. Added validated namespace on
  Claim/Evidence/RelationIn; unknown namespace is 422 so a typo cannot leave a
  practice object in science. Probe artifacts classified 'test', NOT deleted.
- Seam battery A-J 12/12; integration battery 15/15; fail-closed regression
  8/8; pooled-write requalification G17 30/30, G19, G21 160/160, firewall PASS.
- Contract now pew.fossil.v2 / schema_version 4. Harmonia handoff:
  docs/HARMONIA_PEW_WRITE_CONTRACT.md.
