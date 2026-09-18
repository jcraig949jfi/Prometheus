# Nyx status

Currency: 2026-09-18 ~11:45 UTC (instance gandalf-9e21f277 on M3/GANDALF).

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
what it asserts (atlas, python -m nyx.atlas.build): census 121; cut 107 (COARSE 62, DEEP 42, ORGAN0 3); NOT_CUT 14; 513 fragments
  (453 ACCEPTED, 60 CANDIDATE); 321 rejected; 157 pressures; 630 composition edges; fingerprints 0; blind cuts 0; measured
  cells 0. Stage A order for the NOT_CUT population preregistered (seed 20260917); positions 1-80 done except 13 (valgrind fixtures), 18 (souffle) and 49 (pari-gp: ORIGIN_UNREACHABLE, SSL); bodies present (79/80 MATCH).
pipeline objects: MECH-GZIP-LEVELTABLE-003 (frozen 5dbf46a2..., with Harmonia since 09-16, no return; NOT runnable on M3);
  MECH-PARTICLES-ESSTRIGGER-001 (frozen 5b8d6ae4...; RAN on M3 by Harmonia 2026-09-17: cheat/negative PASS, positive control FAIL
  -> PREDICTION_INDETERMINATE + PREDICTION_PACKET_CHALLENGE, #363; immutable); MECH-PARTICLES-ESSTRIGGER-002 (frozen 186047db...,
  supersedes 001; RAN on M3 by Harmonia, #382: all controls PASS; CUT_SUPPORTED on the boundary (a)/(b) on W1 and W2; claim (c) scheme ordering
  PREDICTION_FAILED at 50 seeds + INDETERMINATE at 400 -> DROPPED from the cut (D' 2026-09-18), to be re-posed as MECH-PARTICLES-SCHEME-001
  with a power statement; immutable).
gates (nyx/atlas/gates/LEDGER.json): cuts_created 107; cuts_returned_with_verdict 1 (particles-chopin-0.4, CUT_SUPPORTED, #382); handoffs open 4 (Harmonia x2 -- gzip
  003 and particles 001; Techne x2 -- #296 first-pass return, #358 census/asks); returns received 7 (3 on 09-16; #360 ACK, #363 INDETERMINATE + CHALLENGE on 09-17; #377 Techne POET/ALife autopsy, ACCEPT, answered #379 with ASK 3-5).
record defects for Techne (this block): the 4.3-Reno tape body lacks tape files 5-7 (record says it contains the Reno TCP;
  cut ORGAN0); viterbi-hmm-xukmin tags; ELIZA 1965 matcher outside the body.
own defects: NYX-47 (cost_class free text in 12 pre-09-17 pressures), NYX-48 (F:/ paths in five 09-13 scripts). CLOSED
  2026-09-18: the grade map now translates HISTORICAL_ARCHIVE_MIRROR (Techne #387 ASK 2 ruling; 13 cuts re-graded CONTEMPORARY_COPY).
incident (calibration ledger 2026-09-17): boot-time `git pull` moved the canonical checkout on M3; Hephaestus WIP on
  hephaestus/src/closure_q045.py is in stash@{0} of C:\Prometheus, intact; pop it in a worktree.
lane: nyx/ and roles/Nyx/ only.

next executable action: Stage A on positions 81-91 of the order (glpk, quadpack, openssl-heartbleed, lapack, py-vollib, redlock-py,
  filterpy, zlib, tinyscheme, ncompress, the 4.2 tape), then 13, 18, 49; five pure-Python packet candidates are recorded (sgp4,
  backoff, emcee, pid-autotune, pybreaker) behind the POET and scheme packets; two M3-runnable packet candidates recorded (python-sgp4
  with tcppver.out as oracle; backoff with its tests) behind the POET / scheme packets;
  the next packet on the ruler is the POET PATA-EC one if its body lands (H5), else MECH-PARTICLES-SCHEME-001 with a power statement; the operator's 2026-09-18 directive (roles/Nyx/prompts/2026-09-18_poet_alife_cut_into_bodies/) makes the POET /
  Avida / Tierra / ASAL / TerraLingua cuts the priority THE MOMENT Techne lands the bodies (ASK 3 in #379): POET's discard
  boundary first, then Avida's SavePopulation path (extend the existing cut, before any run); refresh the census when they land; the paxos packet is
  OFF (body is Python-2-only, SCOUT 2026-09-17); the next M3-runnable packet candidate is Lenia (pure numpy) once Techne
  clones it; write the packet for the
  4.2BSD TCP Karn-ambiguity claim only if a pure-Python simulation world is acceptable to Harmonia (ask, do not build).
