# Nyx status

Currency: 2026-09-17 ~11:10 UTC (instance gandalf-9e21f277 on M3/GANDALF; Stage A continuation under Amendment 3 N1).

seat state: ACTIVE. Governing directives unchanged from 2026-09-16: Mechanism Archaeology Pipeline (Founding Charter +
  Amendments 2, 3; Amendment 1 NOT received) over the ATLAS PASS 01 charter; Nyx owns Stage A/B, C' (packets), D' (returns).
what it asserts (atlas, python -m nyx.atlas.build, built 2026-09-17T11:04Z):
  census 121; cut 39 (COARSE 28, DEEP 11); NOT_CUT 82; 294 fragments (259 ACCEPTED, 35 CANDIDATE); 156 rejected; 88 pressures;
  403 composition edges; 141 ancestry edges; blind cuts 0; fingerprints 0; measured cells 0. Every organ is SOURCE_READ except
  4 METADATA and the 3 EXECUTED/INTERVENED from 09-13..16. Nothing has run since 09-16.
  Stage A order for the NOT_CUT population PREREGISTERED (samples/stageA_not_cut_seed20260917_n91.json, committed before any
  body was fetched); positions 1-10 processed this session: 9 cut, avida (position 7) materialised and deferred.
  R34 provenance on the 9 new cuts: 28/28 files byte-exact against Techne's hashes on M3; bodies 10/10 MATCH
  (samples/stageA_bodies_m3_2026-09-17.json).
gates (nyx/atlas/gates/LEDGER.json): cuts_created 39; cuts_returned_with_verdict 0; handoffs open 2 (max age 1 tick);
  returns received 3 (all 09-16). No return on MECH-GZIP-LEVELTABLE-003 (Harmonia R1) as of this currency.
  NONE of the 39 cuts except gzip has a NYX_PREDICTION_PACKET: the pipeline's falsification side is starved by Nyx, not by
  Harmonia (whose lane currency exists since #316/#317). Atlas growth is reported beside this, not instead of it.
own defects: NYX-47 (12/88 pressure cost_class free text -- the 09-13/16 ones; the nine new cuts use the vocabulary) and
  NYX-48 (F:/ paths in five 09-13 cut scripts) still open; migrate_v1 host string fixed this session (was hardcoded M2).
incident (calibration ledger 2026-09-17): boot-time `git pull` moved the canonical checkout on M3; Hephaestus WIP on
  hephaestus/src/closure_q045.py is in stash@{0} of C:\Prometheus, intact, and must be popped in a worktree.
lane: nyx/ and roles/Nyx/ only.

next executable action: write NYX_PREDICTION_PACKETs (schema/1) for the two cuts whose bodies already have a runnable world
  (verilog-uart2bus: bench/ under iverilog; willemt-raft: tests/virtraft2.py) so Harmonia has something to adjudicate
  besides gzip; then Stage A on avida and positions 11-20 of the order. Assimilate the R1 return on packet 003 when it
  arrives.

instance note (2026-09-17 ~14:45Z): m2-0c0adfe1 (M2) CLOSED DOWN by the operator; its handoff is the appended section of
  roles/Nyx/journal/2026-09-17.md. The live instance is gandalf-9e21f277 (M3). M2 host residue: D:/Prometheus-vault/fossils
  (Nyx's 30-body re-fetch; deletable; Techne has its own M2 vault).
