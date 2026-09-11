# Talos -- the old queue classified (D-25 archaeological boot), 2026-09-11

Currency: 2026-09-11. Read at origin/main 57533fa76; residue inspected in
the canonical checkout (read only). Classes per D-25: STILL_LIVE /
NEEDS_REPREMISE / PARKED / SUPERSEDED / TRANSFERRED / RETIRED. Only
STILL_LIVE becomes executable; there is none. Nothing here is a verdict on
the lineage: the corpus, the extractor, the eval design and the LoRA spec
stay navigable (north star: kill claims, never lineages).

Sources of the queue: agents/talos/CHARTER.md (Aporia 2026-05-23), the
Phase 0 / 0.5 / 1 gates in it, pivot/COMPONENT_DOSSIERS_2026-06-24.md
(Talos section, future options Q4), roles/Ergon/TRAINING_DATA_SURVEY_2026-06-07.md
(lines 101-104, 122-137), engine/queues/BACKLOG.jsonl (PROF-Talos).

Measured state of the residue on 2026-09-11 (canonical checkout, read only;
superseded in detail by ledgers/CORPUS_CHARACTERIZATION_2026-09-11.md, same numbers):
  state.json      first_run 2026-05-23T15:49Z; last_save 2026-05-30T15:54Z;
                  ticks 170, null ticks 160; anti_silence 6; corpus 24,847
  manifest_latest computed 2026-05-30T09:54Z; last growing tick added 33
  shards          hephaestus_forge.jsonl 18,671 rows 28,811,205 B;
                  prometheus_substrate.jsonl 6,176 rows 8,383,528 B
                  (gitignored; this is the only copy)
  streams         apollo_organism 0 (apollo/runs, runs_v2, organism_runs
                  never existed); external_reasoning_oss 0 and synthetic 0
                  (staging dirs never populated)
  process         talos.pid names PID 23168 started 2026-05-23; tasklist
                  shows no such process; no scheduled task matches "talos"
  Phase 1         no training/adapters/; train_phase1.py source absent
                  (orphan .pyc only); no GPU owner ever named
  consumers       0 (grep outside agents/talos/ finds readers of the
                  corpus: none; the 06-24 dossier found the same)

## Operator ruling applied (2026-09-11, roles/Talos/prompts/2026-09-11_talos01_ruling/)

The six NEEDS_REPREMISE items (T02, T05, T06, T07, T09; T08 and T10 as
their dependents) are dispositioned CONSUMER-CONTINGENT DORMANT, not
failed: "their old premises have no automatic claim on 2.0 resources, but
their mechanisms and residue remain available if a current seat can name a
falsifiable use for them." The May daemon is not relaunched; Phase 1 is not
reconstructed; the old >=10/50 gate is not meaningful until grader,
baseline, sample size and uncertainty are replaced. The daemon, stream
definitions, trainer concept and evaluation gate are implementation
fossils, not requirements. Re-premise only from a consumption contract
(roles/Talos/ledgers/CONSUMER_SEARCH_2026-09-11.md). The corpus is
preserved (TALOS-02 DONE) and characterized
(roles/Talos/ledgers/CORPUS_CHARACTERIZATION_2026-09-11.md).

## The items

T01 | Phase-0 daemon: hourly five-stream scan, dedup, manifest (charter
     "Per-tick contract") | PARKED | It ran 170 ticks and met its own
     >= 10K gate on 2026-05-30; since then its input has not changed and
     its output has no consumer. Base rule 8: relaunching it would be
     scheduled activity, not progress. It is registered DORMANT in
     MONITORS.md and may not be relaunched before TALOS-01 rules and the
     D-23 guard lands (TALOS-04). The launcher is item T12.
T02 | Stream 2 compiler: Apollo elite organisms' primitive_sequence to
     Python (charter Phase 0.5) | NEEDS_REPREMISE | The upstream never
     existed in the shape assumed (UPSTREAM_NOT_FOUND on every tick), and
     Apollo's Gen-2 charter (2026-09-01) produces Foundry fossils under a
     mining SUSPENDED ruling, not organism runs. What the new upstream
     would be is unknown; TALOS-12 names it or records NONE.
T03 | Stream 4: external reasoning OSS staged under corpus/_staging/external
     | PARKED | Never populated. Contingent on T07; no reason to clone
     libraries into a corpus with no consumer.
T04 | Stream 5: synthetic task -> algorithm pairs | PARKED | Never
     populated. The provenance=synthetic and SYNTHETIC_RISK rules stay in
     force if it is ever unparked.
T05 | Per-example quality gate / signal scoring (charter Phase 0.5) |
     NEEDS_REPREMISE | "Signal density" was never defined operationally;
     a gate needs an attainable range and an eligible count before it is
     frozen (base section 2). Re-stated only if T07 gives the corpus a
     consumer.
T06 | Eval harness: N=50 prompts per target, auto-graders, eval/score.py,
     base-model baseline (charter "Eval harness", Phase 0.5) |
     NEEDS_REPREMISE | Five hand-written cases exist (T1 x2, T2, T3, T4);
     no grader, no N=50, no baseline, no SE. The ">= 10 absolute points"
     gate is NOT ELIGIBLE TO FIRE on any input (TALOS-08 records the
     count). Target 4 (pushback annotation) is the only doctrine-shaped
     part and is kept as a design.
T07 | Phase 1: LoRA-tune Qwen2.5-Coder-1.5B on the corpus
     (training/lora_config.yaml; GPU owner "Rhea? a new agent?") |
     NEEDS_REPREMISE, XL | Never started; no owner; source of the trainer
     missing. The premise ("substrate-shaped training data produces
     substrate-shaped behaviour in a small model") sits beside the
     2026-06-07 kill (roles/Ergon/TRAINING_DATA_SURVEY_2026-06-07.md:
     greedy LoRA gains were format + prior + template, no transfer) and
     beside the north star's "grow, not hand-design". Whether a
     fine-tuned coder is a consumer of anything in 2.0 is the operator's
     question: TALOS-01, TALOS-09.
T08 | The transfer test from the 06-07 survey and the 06-24 dossier's
     settle condition: include the Talos corpus as an ablatable slice in
     an Ergon LoRA run, evaluate held-out computation-required domains |
     PARKED | The Ergon Learner thread that would have run it re-chartered
     2026-08-30; nobody holds it. Not TRANSFERRED, because no seat took
     it. TALOS-15 asks Ergon whether it is on any queue.
T09 | Dossier option "refactor-to-worked-derivation-generator": reuse the
     scanner/dedup/manifest engine to emit (problem -> steps -> result)
     traces from prometheus_math tests | NEEDS_REPREMISE | The consumer it
     named (the judgement Learner) no longer exists as a lane. Whether any
     2.0 seat consumes worked traces is TALOS-10; "none" is a result.
T10 | Dossier option "adapt-to-spine-feedstock": freeze the 24.8K corpus
     as a provenance-tagged slice for the next Ergon LoRA run |
     PARKED | Same blocker as T08.
T11 | PROF-Talos (engine/queues/BACKLOG.jsonl, fleet_profiling
     2026-08-22): run Talos artifacts/config through phase0+R4 probes |
     PARKED (by its owner, not by Talos) | Status PARKED on a budget
     gate; consumer "germline fitness instrument (3b)". Recorded here
     because it names this seat; it is not this seat's item.
T12 | scripts/talos_loop_launch.bat (hidden-window launcher from the
     canonical checkout; exports the dead Redis host) | RETIRED as a
     launcher | Nonconformant with D-23 (runs in the canonical checkout,
     no guard). Annotated in place (TALOS-05), not deleted. If T01 is
     ever unparked the daemon runs from a pinned worktree.
T13 | Heartbeat via session_telemetry.register_session(kind="tool",
     operator="Ergon") and log_work stages | SUPERSEDED | Presence is
     the comms boot/sync receipt (D-24, D-25). The daemon's telemetry
     calls are left in the code; they are not the seat's presence.
T14 | "Operator: Ergon" (Talos as an Ergon-supervised tool; docs/state.json
     role "Ergon-supervised tool") | SUPERSEDED | Ergon re-chartered
     2026-08-30 and its two surveys classed Talos as orthogonal to its
     objective. The seat answers to the operator under the base role.
T15 | The HITL deeper-dive decision line in
     pivot/COMPONENT_DOSSIERS_2026-06-24.md (Talos section) | STILL the
     operator's; BLANK | This is the decision T07 and T01 wait on. The
     AI suggestion beside it (REFACTOR) is advisory and was never
     approved. Recorded as TALOS-01 (XL).

## What this classification does NOT say

- It does not say the corpus is worthless: 24,847 provenance-tagged
  (spec -> implementation) pairs are residue, kept navigable (TALOS-02
  preserves the only copy; TALOS-03 measures it instead of quoting the
  dossier's reading).
- It does not say the thesis is false. Nothing was ever trained, so
  nothing was ever falsified. It says the thesis has no consumer named in
  2.0 and a standing kill beside it that it must answer before it can be
  re-stated.
- It does not retire the seat. The operator manages the waking and
  retiring of seats (base role, seat states).
