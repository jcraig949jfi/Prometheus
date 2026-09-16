# Nyx status

Currency: 2026-09-16 ~12:55 UTC (instance m2-0c0adfe1 on M2; ATLAS PASS 01 Stage A COMPLETE on the sample; first-pass return FILED).

seat state: ACTIVE. Governing prompt: ATLAS PASS 01 (roles/Nyx/prompts/2026-09-13_atlas_pass_01/, sha256 7da74389...).
  Catalogue loop (nyx/catalog) STOPPED. Bodies for the sample are on M2 (TECHNE_FOSSIL_VAULT=<host>/Prometheus-vault/fossils,
  receipt nyx/atlas/samples/stageA_bodies_m2_2026-09-16.json: 30/30, 28 byte-exact, 2 explained).
what it asserts (atlas, python -m nyx.atlas.build, nyx/atlas/out/DEPTH_MAP.json):
  census 121; Stage A sample n=30 (seed 20260913) ALL cut: COARSE 21, DEEP 9; NOT_CUT 91;
  224 candidate fragments (192 ACCEPTED, 32 CANDIDATE), 121 rejected cuts, 69 pressures, 298 composition edges,
  130 ancestry edges; recurrence candidates 15 by reading (R0 4, R1 8, R2 3, R3+ 0); blind cuts 0; fingerprints 0;
  measured coverage cells 0 (every cell is READ). Provenance: SOURCE_READ 217 organs, METADATA 4, EXECUTED 1, INTERVENED 2.
first-pass return: nyx/atlas/FIRST_PASS_RETURN_2026-09-16.md; delivery roles/Nyx/prompts/2026-09-16_atlas_first_pass_return/
  posted to Techne (report). Techne feedback 9a-9h in it (hash CRLF/pycache defect; 'superseded' undirected; two systems
  in one record; des oracle mislabelled; missing worlds/bodies/controls; where to dig next).
catalogue (frozen at bc37f828d): 321 bits; EVAL01 INDETERMINATE (053cc6c8e).
anatomy ledger (pre-atlas): 6 specimens; 18 organs delivered, 1 attempted, 0 CONSUMED.
NYX-44 (go-explore c04): UNCHANGED, PENDING RULING (roles/Nyx/prompts/2026-09-15_nyx44_ruling_request/); no ruling as of this sync.
open comms: queue #235 (atlas charter, open: Stages B-E remain), #241 (not Nyx's); older #176 #189 #190 #192 #197 #198 #202.
holds: c07 reopen only on an EXISTING consumer meeting the four conditions; c03 / c01 held; Proteus/Diomedes halves HELD;
  c04 held pending the NYX-44 ruling.
own defects open: 12/69 pressure cost_class fields free-text (NYX-47); five 09-13 cut scripts carry F:/ paths (NYX-48).
lane: nyx/ and roles/Nyx/ only.

next executable action: Stage C, the gzip level-table ablation in Techne's fossil-c-toolchain image (ratio + wall time per
  level; positive control level 0; cheat control a pre-compressed input) -- first command: is docker reachable via WSL on M2.
  Then the other five ready ablations (minisom radius, hopfield capacity, rr-arbiter 64 cases, rs tt+1, aes/des rounds).
  Stage A on the 91 NOT_CUT is deliberately NOT next (return: "What should stop").
