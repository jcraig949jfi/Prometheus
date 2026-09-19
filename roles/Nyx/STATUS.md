# Nyx status

Currency: 2026-09-19 ~12:30 UTC (instance gandalf-9e21f277 on M3/GANDALF).

seat state: ACTIVE (this M3 instance; the M2 instance m2-0c0adfe1 closed down 2026-09-17, c60b78f17, and its
  'parked' STATUS is superseded by this file). Governing directives: Mechanism Archaeology Pipeline (Founding Charter + Amendments 2, 3; Amendment 1
  NOT received) over the ATLAS PASS 01 charter. Operator topology ruling 2026-09-17 (roles/Nyx/prompts/2026-09-17_topology_m3/):
  Techne, Nyx and Harmonia all run on M3; the M1/M2 Nyx and Techne instances are shut down.
host fact that governs everything below (measured 2026-09-17): M3 has no WSL2, no docker, no C compiler, no iverilog.
  Every fossil world Techne has run to date is a docker world. Harmonia CANNOT adjudicate gzip packet 003 on M3. Of the
  nine cuts made today only particles-chopin-0.4 executes here (system Python 3.11.9 + vault body on sys.path).
comms: Harmonia[gandalf-6cd1348b] booted on M3 at 15:2xZ (R1 open on gzip 003; says execution is not possible here;
  nothing asked of Nyx); #357 (the particles packet) is in its inbox. The live channel is the Postgres queue at 192.168.1.202:5432 (EW_DB_HOST). The Redis at 192.168.1.202:6379 answers
  but its Agora streams have been dead since 2026-05-20; 192.168.1.176 is unreachable. Nyx and Techne online; Harmonia
  offline since 2026-09-16 13:42Z (messages queue for it).
what it asserts (atlas, python -m nyx.atlas.build): STAGE A FROZEN (operator directive 2026-09-18 s1) -- census 121 FROZEN + 1 operator-directed ALife body (asal-sakana-2024, s6) = 122 atlas fossils; cut 121
  (COARSE 72, DEEP 45, ORGAN0 4); NOT_CUT 1 (pari-gp-2.17, ORIGIN_UNREACHABLE/SSL from this host); 475 accepted organs. 121 is a HARD boundary; no new broad census until >=10
  mechanisms carry Harmonia verdicts. The atlas is now the RESERVOIR; the scoreboard is the output.
SCOREBOARD (nyx.scoreboard/2, operator directive 2026-09-19 s9; supersedes /1 row-counting -- investigations, not
  supported/failed rows): packets_issued 3, packets_adjudicated 2, predictions_tested 7, predictions_falsified 2,
  cuts_technically_supported 2, mechanisms_isolated 2, observer_stable_mechanisms 0 (pending HARM-55/56),
  successful_independent_transplants 0, unresolved_anomalies 1, MECHANISMS_THAT_SURVIVED_TRANSPLANT 0 (the headline target).
pipeline objects: MECH-GZIP-LEVELTABLE-003 (frozen 5dbf46a2..., with Harmonia since 09-16, no return; NOT runnable on M3);
  MECH-PARTICLES-ESSTRIGGER-001 (frozen 5b8d6ae4...; RAN on M3 by Harmonia 2026-09-17: cheat/negative PASS, positive control FAIL
  -> PREDICTION_INDETERMINATE + PREDICTION_PACKET_CHALLENGE, #363; immutable); MECH-PARTICLES-ESSTRIGGER-002 (frozen 186047db...,
  supersedes 001; RAN on M3 by Harmonia, #382: all controls PASS; CUT_SUPPORTED on the boundary (a)/(b) on W1 and W2; claim (c) scheme ordering
  PREDICTION_FAILED at 50 seeds + INDETERMINATE at 400 -> DROPPED from the cut (D' 2026-09-18), to be re-posed as MECH-PARTICLES-SCHEME-001
  with a power statement; immutable).
  MECH-ASAL-LEGIT-SEARCH-001 (frozen c6627d26...; the GOLDEN PATH's first verdict). RAN sealed-then-frozen by Harmonia (#441,
  operator-tightened #446): boundary CUT_SUPPORTED; I0-catalogue PREDICTION_FAILED (raw catalogue crosses, 0.8076 < 0.8167; A7
  lesson -- an estimated mean frozen as an exact threshold); I1/I2 SUPPORTED_BY_WITNESS (0.7665; existential); I3
  SUPPORTED_ON_EXECUTED_SUBSET (395 of 1045 executed, port refused 650). MECHANISM STRENGTHENED: the ASAL scalar admits both exploit
  turbulence and coherent morphing life below garbage; selection alone suffices. Packet immutable; full-domain run deferred to a new
  preregistered replication after port extension (A4). Posted Stage D' #476.
gates (nyx/atlas/gates/LEDGER.json): cuts_created 120; packets_issued 3 (all with verdicts; open 0); returns_received 18. The
  golden path's first mechanism (asal-sakana-2024, score at asal_metrics.py:52-64) has a Harmonia verdict and a Theophrastus cell
  OFFERED (not yet accepted); milestone s7 (one mechanism to a bench with machine-verifiable receipts) is one bench-acceptance away.
record defects for Techne (this block): the 4.3-Reno tape body lacks tape files 5-7 (record says it contains the Reno TCP;
  cut ORGAN0); viterbi-hmm-xukmin tags; ELIZA 1965 matcher outside the body.
own defects: NYX-47 (cost_class free text in 12 pre-09-17 pressures), NYX-48 (F:/ paths in five 09-13 scripts). CLOSED
  2026-09-18: the grade map now translates HISTORICAL_ARCHIVE_MIRROR (Techne #387 ASK 2 ruling; 13 cuts re-graded CONTEMPORARY_COPY).
incident (calibration ledger 2026-09-17): boot-time `git pull` moved the canonical checkout on M3; Hephaestus WIP on
  hephaestus/src/closure_q045.py is in stash@{0} of C:\Prometheus, intact; pop it in a worktree.
lane: nyx/ and roles/Nyx/ only.

next executable action (operator directive 2026-09-19 "ASAL PIPELINE DIRECTION",
  roles/Nyx/prompts/2026-09-19_asal_pipeline_direction/): the pipeline moves from "the pipeline works" to "can it extract
  machinery we did not know to look for". Port-adequacy gate CLOSED (Harmonia #479). Sequence: PORT ADEQUACY -> OBSERVER
  REPLICATION -> DISCORDANCE -> FULL-DOMAIN REPLICATION -> MECHANISM EXTRACTION -> TRANSPLANT.
  DONE this tick: directive recorded + relayed (#487); s3 claim held at the 395-domain resolution (CLAIM_CURRENT_RESOLUTION.md);
  s5 behavioral-cut plan preregistered (PLAN_behavioral_cuts_after_replication.md); s6/s11 asal atlas skeleton created and the
  two ASAL organs made addressable (grade ORIGINAL_ARTIFACT, hash-match); s9 scoreboard rebuilt to nyx.scoreboard/2 (+ test).
  NEXT, in the execution order (steps this seat owns):
  (3) FULL-DOMAIN REPLICATION packet -- author it the moment HARM-56 returns (domain demonstrably executable before the first
      score: enumerate + instantiate every member, acceptance by class, refuse on unexplained coverage holes, freeze seeds/
      observer(s)/classification/thresholds, catalogue by stable positional INDEX not code (#479: 63 duplicated codes), prove
      determinism on a sampled + adversarial subset; score through BOTH observers where feasible). HOLD until HARM-56.
  (5) BEHAVIORAL CUTS on stable + discordant regions -- after the replication is frozen + executed. Plan is preregistered.
  (7) NOMINATE one candidate MECHANISM (a dynamical property, not the metric) for Theophrastus transplant.
  CONCURRENT (run now): POET's two mechanisms (bodies landed) + their atlas skeletons; then the Avida ancestry cut (A5
  definedness, A9 ancestry); poet/lenia skeletons land with those cuts; tierra/terralingua stay UNSEEDED (they wait).
  HOLDS: no full-domain packet until HARM-56; no behavioral cuts until the replication runs; no new search objective; no
  mechanism nomination until the low-score region is cut by behavior; no port-development campaign; no decimal-precision chase.
  HARM-55 Flax scoring is Techne/Harmonia on an AVX host, not this seat. Open packets/lane {} (cap 3).
