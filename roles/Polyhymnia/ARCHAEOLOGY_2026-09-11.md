# Polyhymnia archaeology, 2026-09-11 (base role: booting an old seat is an archaeological event)

Currency: 2026-09-11. Read from origin/main 57533fa76 and from the
untracked runtime files in the canonical checkout (read-only; nothing
there was modified). Every number below has its source beside it.

## 0. What the seat was

Charter: agents/polyhymnia/CHARTER.md, authored by Aporia (a sibling
seat, then acting as this seat's "operator") on 2026-05-24; commits
38e0ca5e9 (Phase 0), 5c3fb5111 (v0.2, "Omnitensor" terminology),
ccac80738 (fix), 2b4d12eb6 (SelfImprovingDaemon mixin adoption),
df9153e0b (cross-agent mutation registry).

Thesis: "There's one tensor" -- a sparse, content-addressable,
N-dimensional store into which everything tensor-shaped (datasets,
equations, algorithms, researchers, papers, libraries, fringe mentions)
is ingested by "scours", read by "lenses", played by "games". Ingest
first, classify later; the fringe is the point. Not the reasoner: a
sensory organ for a species that would see the world tensor-first.

## 1. What actually ran (from agents/polyhymnia/events.jsonl and state/state.json, untracked)

- first_run_at 2026-05-24T20:00:17Z; last tick_end 2026-05-30T16:02:55Z
  (tick_number 280 at tick_start; 297 tick_end events in the log).
- Scours shipped: ONE (prometheus_self, a grep of this repository).
  Rounds 2-4 of the charter (17 more scours) were never written.
- Tick outcomes: scour_prometheus_self_integrated 47, scour_prometheus_self_null 250.
  The single source saturated within days (Harmonia,
  roles/Harmonia/SESSION_JOURNAL_E_20260610.md: "Polyhymnia =
  source_saturated (single scour)"; "health on a dead channel").
- Self-improvement mixin: 163 approval_requested events, all for the same
  adaptation SPAWN_SIBLING_SCOUR, posted into Aporia's inbox
  (aporia/meta/queue/aporia_inbox.jsonl, id
  T-2026-05-26-Polyhymnia-approval-SPAWN_SIBLING_SCOUR, three copies
  survive). Never answered. Aporia's 824a668b4 "fix self-improving spam"
  addressed the flood, not the request.
- Tensor body: agents/polyhymnia/tensor/tesserae.jsonl, 4,917 lines,
  11,529,754 bytes, mtime 2026-05-30, GITIGNORED (agents/polyhymnia/.gitignore).
  It exists in exactly one place: the canonical checkout on this host.
  relations.jsonl (17 edges) and tensor/axes/*.jsonl (8 registries) are
  tracked. Not verified: whether the 4,917 rows are 4,917 distinct
  coordinate signatures (the integrator merges on signature; the count
  is lines, not cells).
- Lock file agents/polyhymnia/polyhymnia.pid: pid 23960, host SKULLPORT,
  started 2026-05-25T11:41Z. That pid is not running (tasklist, 2026-09-11).
  No process with "polyhymnia" on its command line; no scheduled task
  whose name contains "poly" (schtasks, 2026-09-11).
- The 2026-06-15 reset (aporia/docs/STATUS_2026-06-15_reset.md s7) listed
  "Icarus pilot + Polyhymnia (named operators)" under KEEP. The keep
  expired de facto sixteen days earlier: nothing ran after 05-30.

Seat state on 2026-09-11, in the base role's words: the daemon was
EXPECTED to operate (KEEP) and was not -- DORMANT since 2026-05-30, and
because the pid file is stale and no task exists it is also not PRESENT.
Registered in roles/base-role/MONITORS.md on this pass as DORMANT.

## 2. Two tensors share a word; they are not the same object

aporia/doctrine/critical_memories.md HARD-3 ("Tensor first") names the
UNIFIED, SIGNATURE-KEYED TENSOR of Prometheus 1.0 findings with
operator-derived structural partitions -- the map the calibration
arsenal runs over. The Omnitensor is a KNOWLEDGE AGGREGATE of things
called tensors. Harmonia's 2026-06-10 journal records that Polyhymnia is
code-independent of that program. This file does not claim the
Omnitensor advances HARD-3, and it does not claim the reverse. It is a
different object with the same word on it; any future claim linking
them is a claim to be measured, not inherited.

## 3. The old queue, classified against the north star (2026-09-11)

Classes: STILL_LIVE, NEEDS_REPREMISE, PARKED, SUPERSEDED, TRANSFERRED,
RETIRED. Only STILL_LIVE is executable; NEEDS_REPREMISE must be re-stated
first; the rest are recorded. Nothing below is marked dead: residue,
weak signals and gradients stay navigable (base role, "nothing is marked
dead prematurely").

  item                                          class            note
  --------------------------------------------  ---------------  ----------------------------------------------------------
  The thesis: one heterogeneous, append-only,   NEEDS_REPREMISE  Under the north star this is a REPRESENTATION SUBSTRATE
  content-addressable tensor of tensor-shaped                    (information organisms consume), not the reasoner. Live
  knowledge; ingest first, classify later                        only once a consumer in the SFE ecology is named. None is.
  Daemon loop (30-min tick, round-robin scours) PARKED           Dead since 05-30; single input saturated; no consumer.
                                                                 Not restarted on this pass (operator: execute nothing).
  Scour prometheus_self (shipped)               PARKED           Saturated: 47 integrating ticks then 250 nulls. Re-run
                                                                 only behind a consumer and a productivity signal.
  Scours round 2 (wikipedia, oeis, arxiv,       NEEDS_REPREMISE  Each is an ingest job. Before any: who reads the tensor,
  prometheus_math_lib)                                           and what does a row change downstream? (rule 8: a loop
                                                                 that produces rows nobody consumes is activity, not progress)
  Scours rounds 3-4 (mathworld ... art_history) PARKED           Same premise gap, larger cost. Fringe list retained as the
                                                                 operator's "leave no stone unturned" posture.
  Lenses (by_decade, discipline_x_kind,         NEEDS_REPREMISE  A lens is a read path. Which lens a consumer needs is the
  researcher_lineage, rank_n, missing)                           consumer's question; "missing" (gap finding) is the one
                                                                 weak signal here worth restating first.
  Games (random_walk, connect_two,              NEEDS_REPREMISE  Their stated consumer, "the Learner", is gone (Ergon was
  complete_the_slice, twenty_questions,                          re-chartered 2026-08-30 as memory-metabolism). As
  mendeleev)                                                     task/world generators for the SFE ecology they are an
                                                                 UNTESTED idea, to be restated, never assumed.
  SelfImprovingDaemon mixin; PolyhymniaSelfImprover;  SUPERSEDED  Base role: no LLM adjudicates; admission is a human act.
  SPAWN_SIBLING_SCOUR adaptation                                 163 unanswered approval requests are the residue. Icarus was
                                                                 the program's one self-improvement pilot (2026-06-10 audit).
  Approval request T-2026-05-26-...             RETIRED          Its channel (Aporia's JSONL inbox) is superseded by comms
  SPAWN_SIBLING_SCOUR (Aporia inbox, x3)                         (D-24); its want (a second scour) folds into round 2 above.
  Heartbeat via session_telemetry / Agora       SUPERSEDED       comms (Postgres schema comms) replaced the Redis Agora on
  register_session                                               2026-09-11; presence is a sync receipt, not a heartbeat label.
  "Operator: Aporia" (charter header)           SUPERSEDED       The HITL operator is James; Aporia is a sibling seat.
  Storage section of the charter (cells.jsonl,  SUPERSEDED       v0.2 renamed the body to tesserae.jsonl and edges to
  lineage.jsonl)                                                 relations.jsonl; the charter text was never updated (rule 5:
                                                                 currency is correctness). Annotated, not rewritten, on this pass.
  Hard stops: append-only; never auto-classify  STILL_LIVE       Consistent with the base role's doctrine; carried forward as
  substrate_yield_type without a named basis;                    seat rules in RESPONSIBILITIES.md. (These bind conduct; they
  never silently drop content                                    are not work items.)
  "Leave no stone unturned; fringe is the       STILL_LIVE       Posture, attributed to James by Aporia in the charter (second
  point"                                                         hand; no verbatim operator text in git). Governs HOW a
                                                                 re-premised ingest would choose sources, not WHETHER.
  The tensor body itself (4,917 rows, one       PARKED           Residue with exactly one copy, untracked. Preserving it is a
  untracked copy)                                                decision for the operator (backlog POLY-XL-01), not for the seat.

Counts: STILL_LIVE 2 (both conduct rules, 0 executable work items),
NEEDS_REPREMISE 4, PARKED 5, SUPERSEDED 4, RETIRED 1, TRANSFERRED 0.

The executable queue after archaeology is therefore EMPTY. That is the
result, not a gap: the seat has no work it may start without a
re-premise, and the re-premise (who consumes an Omnitensor row inside
the Prometheus 2.0 ecology) is a charter question the operator holds.

## 4. Calibration entries this archaeology creates

Recorded in roles/Polyhymnia/calibration/LEDGER.md: the 163-request
approval flood (a seat that asked the same question 163 times without
deduplicating was reporting activity, not blocked work); and 250 null
ticks logged as healthy heartbeats (silence read as health -- base rule 7
names this exact defect).

## 5. What was NOT examined

- The content of the 4,917 tesserae (no row was opened; the count is
  wc -l). Whether they are distinct cells: not verified.
- agents/polyhymnia/tensor.py and daemon.py internals beyond the
  docstring and the .gitignore: not read for change on this pass.
- Whether any seat's code imports agents/polyhymnia: only
  agents/_shared/mutation_registry.py names it (a registry row), per
  git grep at 57533fa76.
