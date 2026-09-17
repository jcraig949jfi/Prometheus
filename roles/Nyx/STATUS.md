# Nyx status

Currency: 2026-09-17 ~16:45 UTC (instance gandalf-9e21f277 on M3/GANDALF).

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
what it asserts (atlas, python -m nyx.atlas.build): census 121; cut 48 (COARSE 34, DEEP 14); NOT_CUT 73; 335 fragments
  (300 ACCEPTED, 35 CANDIDATE); 181 rejected; 100 pressures; 453 composition edges; fingerprints 0; blind cuts 0; measured
  cells 0. Stage A order for the NOT_CUT population preregistered (seed 20260917); positions 1-10 done except avida.
pipeline objects: MECH-GZIP-LEVELTABLE-003 (frozen 5dbf46a2..., with Harmonia since 09-16, no return; NOT runnable on M3);
  MECH-PARTICLES-ESSTRIGGER-001 (frozen 5b8d6ae4..., posted #357 to Harmonia 2026-09-17; runnable on M3; R1 opens on it).
gates (nyx/atlas/gates/LEDGER.json): cuts_created 48; cuts_returned_with_verdict 0; handoffs open 4 (Harmonia x2 -- gzip
  003 and particles 001; Techne x2 -- #296 first-pass return, #358 census/asks); returns received 3 (all 09-16).
own defects: NYX-47 (cost_class free text in 12 pre-09-17 pressures), NYX-48 (F:/ paths in five 09-13 scripts), the
  Techne-grade map does not translate HISTORICAL_ARCHIVE_MIRROR (asked of Techne in #358 before fixing).
incident (calibration ledger 2026-09-17): boot-time `git pull` moved the canonical checkout on M3; Hephaestus WIP on
  hephaestus/src/closure_q045.py is in stash@{0} of C:\Prometheus, intact; pop it in a worktree.
lane: nyx/ and roles/Nyx/ only.

next executable action: assimilate Harmonia's return on #357 (D') when it arrives; meanwhile Stage A on positions 13, 18 and 21-30
  of the order; a second M3-runnable packet on cocagne-plain-paxos (pure Python, tests as oracle) once Techne answers ASK 1; write the packet for the
  4.2BSD TCP Karn-ambiguity claim only if a pure-Python simulation world is acceptable to Harmonia (ask, do not build).
