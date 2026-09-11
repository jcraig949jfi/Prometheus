# Atalanta -- the old queue, classified (2026-09-11)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Required by the base role's D-25 rule: booting an old seat is an
archaeological event, not an instruction to resume its last queue. Every
item of the May queue is classified against the current north star and
ecosystem. Only STILL_LIVE is executable work.

Base for every read below: origin/main 8714b2709, worktree
D:\Prometheus-worktrees\atalanta-base-role, branch
atalanta/base-role-adopt-2026-09-11, dirty: only roles/Atalanta/ additions
plus the two registry rows and the charter annotation.

Counts over 22 items:

    STILL_LIVE        0
    NEEDS_REPREMISE   7
    PARKED            5
    SUPERSEDED        8
    TRANSFERRED       0
    RETIRED           2

## A. The per-tick contract (agents/atalanta/CHARTER.md, steps 1-14)

  1 | single-instance pid lock                     | PARKED
      Sound mechanism, no process to guard. Revives with the loop or not
      at all.

  2 | session_telemetry heartbeat, operator=Aporia | SUPERSEDED
      Presence is now the comms boot/sync receipt (D-24, D-25). Old
      heartbeat "online" fields are labels whose meaning has expired
      (base role, "presence is derived from observed activity"). The
      roster rows of 05-26 and 05-28 that read "Atalanta ... active,
      online, 22m, 96 ev" are exactly such a label: the agent was online
      and producing events while producing nothing.

  3 | read state/state.json                        | PARKED
      The file does not exist on this host (section 4 of the seat file).

  4 | scan apollo/runs, runs_v2, organism_runs     | SUPERSEDED
      The three paths have never existed. Re-verified today by direct
      test at 8714b2709. This is the whole failure. Any successor reads a
      configured path, never a hardcoded one.

  5 | parse organism log, count primitive usage    | NEEDS_REPREMISE
      Never executed once. The key it parses (primitive_sequence) is
      still live in apollo/src; the container it expects (per-run JSON
      with run_id/completed_at/organisms) is not what Apollo writes
      (checkpoint pickles, novel_discovery.jsonl). Re-premise is a
      reader, not a redesign.

  6a | high-reuse primitive detection              | NEEDS_REPREMISE
      MIN_REUSE_FOR_CANDIDATE = 3 was chosen before any organism was
      ever counted. It has no attainable-range calculation and no
      eligible count behind it (base doctrine). Any revival computes the
      distribution first and sets the threshold after.

  6b | unnamed length-2/3 composite chain mining   | NEEDS_REPREMISE
      Same defect on MIN_COMPOSITE_FOR_CANDIDATE = 3. The algorithm
      itself (daemon.py aggregate_primitive_signals) is the salvage IP
      named by the June dossier and is worth keeping.

  7 | anti-greedy bucket rotation                  | PARKED
      Never exercised; no evidence it is needed until a candidate stream
      exists.

  8 | build the Type-E DR prompt                   | NEEDS_REPREMISE
      The template's calibration-pattern clause (cite 2 of 5 mandated
      patterns) and its evidence_organisms requirement are the parts
      worth keeping. The five named patterns are May-era and would have
      to be re-checked against today's doctrine before any reuse.

  9 | enqueue to agora.research_queue              | SUPERSEDED
      The April Redis Agora is retired; comms (Postgres schema comms)
      replaced it on 2026-09-11 (comms/README.md, D-24). agora_persist
      and the research_queue table are not the current channel.

 10 | dispatch artifact + log_work                 | NEEDS_REPREMISE
      Artifacts are right; what was wrong is that an absence report was
      written to the same stream as a result, so the artifact count rose
      while nothing happened. A successor separates result artifacts
      from gate artifacts.

 11 | NULL_TICK sentinel on no new runs            | RETIRED
      Never fired: the daemon never got far enough to have "no NEW runs",
      only "no runs directory".

 12 | UPSTREAM_NOT_FOUND sentinel                  | RETIRED
      This is the mechanism that produced 354 of 354 artifacts. It is
      retired as a per-tick behaviour and survives only as its own
      lesson: upstream-liveness is a LAUNCH precondition, not a per-tick
      observation (autopsy P47). The instrument was honest and useless:
      it correctly reported absence 354 times to nobody.

 13 | anti-silence alarm at 50 consecutive nulls   | SUPERSEDED
      The threshold fired at tick 50 and the agent ran to 354. The alarm
      had no route (base rule 7: an alarm with no route is not an alarm;
      pivot/orchestration_monitoring_2026-05-24.md records the
      atalanta/pheme sentinel telemetry being read as noise). The base
      role's MONITORS registry now owns this function.

 14 | persist state, release lock                  | PARKED

## B. The downstream chain (charter, "Downstream consumer")

 15 | Pythia dispatches the Type-E query            | SUPERSEDED
      No Type-E query was ever enqueued, so the arm was never exercised.
      Pythia's own daemon is not in the current monitor registry.

 16 | manual ingestion to techne/registry/primitive_candidates/ | NEEDS_REPREMISE
      Techne is a live seat today. If a successor ever produces a
      candidate, the handoff is a comms delegation to Techne, not a
      manual file drop, and promotion stays Techne's call (hard stop,
      unchanged).

 17 | verdict_back_to tag protocol                  | PARKED

 18 | consume Pheme's demand_latest.json bias       | SUPERSEDED
      Doubly dead. Pheme produced 0 profiles in its own 354 ticks (same
      week, same launch batch, same failure class), and the June dossier
      records the seam between them as broken anyway: Pheme emits dicts
      where Hypatia/Atalanta read strings. A contract that was never
      exercised was also never correct.

## C. Items other seats filed about Atalanta

 19 | AUTOPSY-ATALANTA (engine/queues/BACKLOG.jsonl:92) | RETIRED
      status DONE. Filed by Aporia P47 on 2026-08-20 as DEAD-GATING,
      maximal form. Reviewed by Elenchus (REVIEWS.jsonl, pass P47,
      verdict UNDERCLAIMED -- and note the underclaim finding was about
      the Coeus null in the same batch, not about Atalanta).

 20 | PROF-Atalanta (engine/queues/BACKLOG.jsonl:660) | PARKED
      Ladder profile via phase0+R4 probes. status PARKED on a budget
      gate (API spend). Owner is the fleet profiler, not this seat.

 21 | Necropolis ROSTER row                          | PARKED
      engine/necropolis/ROSTER.jsonl on branch necropolis/foundation:
      apparent_family "autopsy:DEAD-GATING",
      proposed_investigation_status UNQUEUED. Atalanta is one of the
      48 roster agents. If the Necropolis Keeper queues it, that
      investigation is the Keeper's lane, and this seat is its subject,
      not its investigator -- a conflict of interest declared here in
      advance (base doctrine).

## D. The June dossier's four options (pivot/COMPONENT_DOSSIERS_2026-06-24.md)

 22 | the four options, as one decision               | NEEDS_REPREMISE
      retire-after-HITL (the advisory suggestion, NOT approved) /
      refactor-to-config-driven-upstream /
      adapt-to-eval-feedstock (read-only reuse analyzer, drop the DR arm) /
      retire-and-lift-asset (keep aggregate_primitive_signals and the
      evidence-anchored DR template, archive the agent).
      The HITL line is blank. This is ATALANTA-01, and it is the whole
      queue: nothing above it is executable until it is ruled.

## Why STILL_LIVE is zero

Not clerical. Every surviving item is downstream of an Apollo organism
stream, and Apollo is DORMANT by ruling (mining SUSPENDED, HITL
2026-09-01; roles/base-role/MONITORS.md). Reviving a consumer ahead of
its producer is the same error as launching one ahead of its producer,
which is the error this agent is the program's cleanest specimen of.
Recording zero is the honest count, and the seat does not manufacture a
lane to look busy.

The nearest-to-live item is not in the table because it is not
Atalanta's work: the autopsy's representation hint (upstream-liveness as
a launch precondition with a typed park-and-stop gate) is a program-wide
design rule that belongs in the base role or in a shared entry-point
guard. It is written up as a proposal to Archaeon
(prompts/2026-09-11_seat_adoption/) and is NOT executed by this seat.
