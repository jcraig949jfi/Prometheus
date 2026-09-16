# Nyx status

Currency: 2026-09-16 ~14:10 UTC (instance m2-0c0adfe1 on M2; Mechanism Archaeology Pipeline Amendment 3 N1-N4 executed).

seat state: ACTIVE. Governing directives: Mechanism Archaeology Pipeline (Founding Charter + Amendments 2, 3;
  roles/Nyx/prompts/2026-09-16_mechanism_archaeology_pipeline/, Amendment 1 NOT received) over the ATLAS PASS 01 charter
  (roles/Nyx/prompts/2026-09-13_atlas_pass_01/), whose Stage C/D adjudication by Nyx is SUPERSEDED (R32). Nyx owns
  Stage A/B (dissection, cuts), C' (prediction packets), D' (assimilating typed returns).
what it asserts (atlas, python -m nyx.atlas.build):
  census 121; sample n=30 all cut (COARSE 21, DEEP 9); NOT_CUT 91; 224 fragments (192 ACCEPTED); 121 rejected; 69 pressures;
  298 composition edges; recurrence candidates 15 by reading (R3+ 0); blind cuts 0; fingerprints 0; measured cells 0.
  R34 provenance on all 30 cuts: 98 files hashed on M2, 87 match Techne's recorded hashes, 10 mismatch (all the known
  CRLF class: libfec-karn 7, corewar 3), 12 refs unresolved (receipts / prose, listed per fossil).
gates (nyx/atlas/gates/LEDGER.json): cuts_created 30; cuts_returned_with_verdict 0; handoffs open 3 (max age 0 ticks).
pipeline objects (this session):
  MECH-GZIP-LEVELTABLE-001  frozen sha256 861dded070d138e3... (nyx/atlas/predictions/); boundary deflate.c:225-245, 286-356
    bound to payload hashes; 4 interventions (I0 baseline, I1 table-flatten, I2 flatten+switches [decisive], I3 chain-only);
    cheat control C-CHEAT-PRECOMPRESSED; positive control C-POS-LEVEL-EXTREMES; CUT_KILL and INDETERMINATE defined.
    SELF-FOUND CORRECTION before adjudication: the level is consumed at THREE sites, not one (deflate.c:667 fast/lazy switch;
    trees.c:987 flush heuristic); the cut record and script carry the annotation; the original sentence is preserved.
  RS_CALIBRATION_PAIR_001  (nyx/atlas/calibration/): Rockliff 1991 -> Karn; ruler must find R-ID-1/2 identical, R-DIV-1
    divergent (tt+1: silent pass-through vs -1).
  Preservation status of the gzip lineage: NON_CANONICAL / PRESERVATION_GATE_OPEN (R38; TECHNE-65 undecided).
first-pass return (ATLAS): nyx/atlas/FIRST_PASS_RETURN_2026-09-16.md; comms #296 to Techne (queued; Techne offline at post).
NYX-44 (go-explore c04): UNCHANGED, PENDING RULING. Older holds unchanged (c07 / c03 / c01; Proteus/Diomedes halves).
own defects open: 12/69 pressure cost_class free text (NYX-47); five 09-13 cut scripts carry F:/ paths (NYX-48; their
  provenance is now hashed regardless); tunnel.py hardcodes WSL distro "Ubuntu" (M2 has Ubuntu-24.04) -- irrelevant to Nyx
  under R32 unless a SCOUT run is wanted.
lane: nyx/ and roles/Nyx/ only.

next executable action: Stage A/B on the 91 NOT_CUT under nyx.atlas/1-provenance (N1), in the census's stratified order,
  reporting cuts_created beside cuts_returned_with_verdict (0 until Harmonia's lane currency exists). Assimilate the first
  typed return (CUT_SUPPORTED / CUT_CHALLENGE / PREDICTION_*) on MECH-GZIP-LEVELTABLE-001 when it arrives (D').
