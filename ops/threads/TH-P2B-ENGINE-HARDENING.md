# TH-P2B-ENGINE-HARDENING -- Phase 2-B Engine Hardening & Re-exploration

epic: EP-PHASE2B

Status: OPEN. Type: PROGRAM THREAD (many campaigns over time). Declared 2026-10-03 by the operator (verbatim:
roles/Achilles/prompts/2026-10-03_epics_phase2b/01_OPERATOR_DIRECTIVE_verbatim.md, s6-s11, s16, s21-s22). Recorded by Achilles.

## Mission
Revisit Phase 2 engines and scientific seats using the failure corpus and Phase 3 forensic findings; repair
instrumentation and implementation faults, replay important experiments, and continue bounded exploration
where there remains plausible scientific value. One campaign per engine re-entry (and later per follow-on);
never one enormous campaign.

## Posture
Phase 2 produced real value even though many conclusions were weakened. The deep dives found: seeded vs
endogenous lineage confusion; weak provenance; rulers that could not detect their target; trivial baseline
failures; memorization mistaken for intelligence; location/coordinate leakage; source-reading mistaken for
causal mechanism; search/reachability failures; controls that could not fail; reset/carryover defects; answer
leakage; holdout contamination; same-substrate self-agreement; instrumentation that favoured familiar
architectures; scheduler/engine defects; stale and under-used experiments; promising ideas never cleanly
tested. Treat this as a repair and opportunity map. No old positive is presumed valid; no old null is presumed
final; many results are "worth re-running after apparatus repair".

Favour: repaired historical experiments; falsification of old positives; resurrection of apparatus-limited
nulls; cheap discriminators suggested by the deep dives; branches latent in engine backlogs; deterministic
searches that need no model inference; campaigns that use idle CPU/GPU windows; cross-engine comparison where
instrumentation is now adequate. Do not wait for RSO integration: the old engines are experimental apparatus.

## Entering Phase 2-B (for a seat told "enter Phase 2-B")
1. Boot as usual (roles/base-role/WAKE_DIRECTIVE.md). Your charter stays yours: Phase 2-B adds a program
   objective and routing context; it does not rename or homogenize any seat.
2. Read your forensic file(s): `docs/phase3/intake/*/seats/<YourSeat>.md` (and `_frag/<YourSeat>.*.jsonl`
   for the artifact/engine indexes), then the sources below that apply to your engine.
3. Instantiate your re-entry campaign:
   `python -m workgraph new-campaign P2B-ENGINE-REENTRY --owner <YourSeat> --subject "<engine>" --by <YourSeat[tag]>`
   You are its coordinator. Tailor tasks A and B with your actual sources, make them READY, commit and push the
   campaign directory (a rejected push means the C-id was taken: fetch and re-instantiate).
4. Work A -> B; create C/D/E/F packets only from what triage actually found. A first campaign may legitimately
   close with NO_JUSTIFIED_FURTHER_WORK; a previously parked engine may reopen if its null was
   apparatus-limited. Do not reactivate an engine just because it exists.
5. Tasks for others: you may write packets for yourself, other Phase 2-B seats, and shared support seats
   (Harmonia, Techne, Nyx, Atlas, others whose charters permit the work) as `owner_role` or `eligible_roles`.
   The RSO Builder Cell cannot take them (its SCOPE.json).
6. Machines: priority class 4 (registered experiments) or 5 (exploratory sweeps) on shared hardware; take idle
   capacity through leases with ceilings; never preempt a higher-priority active lease (DISTRIBUTED_WORK.md s10).

## Candidate engines / seats (likely; canonical owners are in the seats' charters and the forensic mappings)
Archaeon / SFE; Nestor / NPE; Bellerophon / BEE; Aether / AGE; Ensorain / TensorTrain worlds; Cosmos / CWE;
Crius (where residual work remains meaningful); Aphrodite; Harmonia; Techne; Nyx; Theophrastus; and other
Phase 1/2 engines identified by the forensic crawlers. None is reactivated by this list.

## Forensic sources (linked, not copied)
- Phase 3 forensic intake (Sisyphus, Tantalus, Tityos, Ixion): docs/phase3/intake/{sisyphus,tantalus,tityos,ixion}/
  -- REPORT.md, artifact_index.jsonl, engine_index.jsonl, seats/<Seat>.md (per-seat findings; e.g. Nestor and
  Archaeon under sisyphus/, Aether, Cosmos, Ensorain and Aphrodite under tantalus/, Harmonia, Techne and Nyx
  under tityos/). ixion/ adds an inference dependency map and an institutional timeline.
- Failure-to-gate mapping and audits of the crawlers: docs/phase3/design/ASTRA-6.0/FAILURE_TO_GATE_MAP.md,
  docs/phase3/design/ASTRA-6.0/evidence/{SISYPHUS,TANTALUS,TITYOS,IXION}_AUDIT.md.
- Phase 3 challenges and design packages: docs/phase3/PHASE3_CHALLENGES.md, docs/phase3/design/.
- Doctrine of past failures: aporia/doctrine/critical_memories.md.
- Engine-specific history: each seat's own roles/<Seat>/ (journal, reviews, calibration ledger, backlog) and
  the campaigns/threads already in ops/ (ops/threads/TH-001..TH-021, ops/campaigns/C-001..C-003).

## Campaigns
None yet. Each engine owner adds its own from the template.
