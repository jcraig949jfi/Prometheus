# Nyx status

BOOT NOTE: read roles/Nyx/RESUME_2026-09-25.md FIRST on every bootstrap -- boot commands, the
  frozen-artifact hashes, what is in flight on other seats, the holds, my debts, and the traps
  that have actually bitten this seat. Then this file. Then `python -m comms sync Nyx`.

2026-09-25 (instance gandalf-226cd218, rebooted): booted per the resume record; comms sync 0 new
  after #571 (no POET ruling, no HARM-56 disposition; every hold stands). Validators green
  (123 fossils / 6 mechanisms / probes intact / 45 tests). DEBT 1 PAID: the Ares W4 fossil
  reading (#518/#535/#538) -- roles/Nyx/reports/ARES_W4_READING_2026-09-25.md, apparatus
  nyx/readings/ares_w4_reading.py, run log ..._run.txt. Headline: the seed-3 carrier is a
  3-node ring THROUGH OUTPUT NODE 15 (13->7->15->13, gain 3.92, clip-bistable), not a GATE<->MAX
  2-cycle; both GATEs are always-open identities, the MAX is a dispensable rectifier; 3 of 5
  hidden nodes are neutral; a 2-edge output self-loop is sufficient (lineage 9 IS that circuit).
  Ten lineages: 10/10 hold the bit as the sign of a saturated positive-feedback loop, gain > 1
  closed through the clip, on or driving an output node (8/10 with the output inside the loop).
  Predictions held: W16 floor 10/10; evolved-ring gain basin wide/flat/open-ended (s >= 0.8 up
  to gain 106). Atlas: NOVEL as an organ (nearest registered organs are gain-1 saturating
  accumulators and a clocked latch), known engineering motif outside it.

Currency: 2026-09-25 ~13:30 UTC (instance gandalf-226cd218 on M3/GANDALF).

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
what it asserts (atlas, python -m nyx.atlas.build): STAGE A FROZEN (operator directive 2026-09-18 s1) -- census 121 FROZEN + 2 operator-directed ALife bodies (asal-sakana-2024, poet-original-2019) = 123 atlas fossils; cut 122
  (COARSE 72, DEEP 45, ORGAN0 4); NOT_CUT 1 (pari-gp-2.17, ORIGIN_UNREACHABLE/SSL from this host); 475 accepted organs. 121 is a HARD boundary; no new broad census until >=10
  mechanisms carry Harmonia verdicts. The atlas is now the RESERVOIR; the scoreboard is the output.
SCOREBOARD (nyx.scoreboard/3, operator directives 2026-09-19 s9 + 2026-09-19b s2 -- investigations, and MECHANISM
  counts over UNIQUE mechanism_ids from the mechanism ledger, never packets or supported clauses):
  packets_issued 4, packets_adjudicated 2, predictions_tested 7, predictions_falsified 2, cuts_technically_supported 2,
  mechanisms_registered 6, mechanisms_isolated 6, mechanisms_evidence_supported 2, observer_stable_mechanisms 0,
  observer_dependence_unresolved 2, unresolved_anomalies 1, MECHANISMS_THAT_SURVIVED_TRANSPLANT 0 (headline target;
  cannot be claimed without a SUPPORTED transplant row -- validator-enforced). Open packets/lane {m3-native-python: 1} cap 3.
MECHANISM LEDGER (nyx/atlas/gates/MECHANISMS.json, schema nyx.mechanism_ledger/1; python -m nyx.atlas.mechanisms):
  MECH-ASAL-OE-SCORE EVIDENCE_SUPPORTED (observer UNKNOWN, transplant OFFERED) | MECH-ASAL-FRAME-SAMPLING PROPOSED |
  MECH-PARTICLES-ESS-TRIGGER EVIDENCE_SUPPORTED | MECH-POET-NOVELTY-ESTIMATOR PROPOSED (packet 291a22ed out for ruling) |
  MECH-POET-MINIMAL-CRITERION PROPOSED | MECH-POET-FIFO-DISCARD PROPOSED.
PROBE BATTERY frozen (nyx/atlas/probes.py, source sha256 53f63df5...; probes.FREEZE): 14 declared probes + open-channel
  descriptor, synthetic fixtures only, open-channel output is a NOMINATION not evidence.
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

next executable action (operator directive 2026-09-19b "NEXT PIPELINE DIRECTION",
  roles/Nyx/prompts/2026-09-19b_next_pipeline_direction/; the earlier 2026-09-19 directive is in .../2026-09-19_asal_pipeline_direction/):
  DONE this tick: mechanism ledger built (a mechanism is NOT a packet -- review q9.1 answered NO); scoreboard -> /3 with
  mechanism counts over unique ids; probe battery implemented and FROZEN under two channels (declared + open), synthetic
  fixtures only; stop-condition corrected (PROBE_BATTERY_FOUND_NO_SEPARATOR is not homogeneity); POET cut + the first POET
  packet frozen and posted (#494); directive relayed (#495); two Techne record defects reported.
  NEXT, in order:
  (1) AWAIT the POET novelty ruling (MECH-POET-NOVELTY-ESTIMATOR-001, 291a22ed). It is M3-runnable on the fossil's own
      bytes, so it can return without any AVX host. Assimilate in Stage D' into the mechanism ledger entry.
  (2) AVIDA ancestry cut, concurrently -- A5 definedness on a 30-organism fixture per degradation before any prereg hash
      (parent-edge recall is undefined for endpoints-only history; those arms are refused at plan time) and A9 (keep
      survivors' ancestry, never invent parent ids: missing beats unverified).
  (3) poet-enhanced-2020 (PATA-EC over world x contemporary population, with the basis-population ablation) AFTER the
      POET novelty ruling returns -- one mechanism completed beats several cuts accumulated.
  (4) FULL-DOMAIN REPLICATION packet -- author it the moment HARM-56 returns a disposition A/B/C. Domain must be
      demonstrably executable BEFORE the first score (100% executable or explicitly excluded; coverage is a GATE, not a
      statistic); catalogue by stable positional INDEX not code (#479: 63 duplicated codes); both observers where feasible.
  (5) BEHAVIORAL CUTS on stable + discordant regions, only after (4) executes. Battery already frozen.
  HOLDS: no replication packet until HARM-56; no behavioral cuts until it executes; no new search objective; no
  transplant nomination until the low-score region is cut by behavior; no port-development campaign. HARM-55's Flax
  column is Techne/Harmonia on an AVX host, not this seat (original-observer column already bit-identical, #488).
