# ACCEL_CANARY_RUNPOD_v1 -- ADDENDUM 1 (pin portability; no change to any test)

Found while writing the RunPod kit, before any pod run: the sha256 pins in
ACCEL_CANARY_RUNPOD_v1.md were taken from the M4 working tree, which git checks
out with CRLF line endings (`core.autocrlf=true`). A Linux pod fetching the same
commit from GitHub receives the LF blobs, so the literal pins could never match
there and every pod run would report `reference_drift` -- a false NOT_EQUIVALENT.

Resolution (applies to every host): a pinned file matches iff the sha256 of its
bytes with CRLF normalised to LF equals the sha256 of the git blob at science SHA
cf601fa3e. The blob hashes are:

| file | sha256 of git blob (LF) |
|---|---|
| basis_v4.py | bdc601f2b0fae23bde5d1b9c2e0648d38d7d0400162aa85cfcfdcb001c34a1e4 |
| run_tier3c.py | 96ee9332627dc49176bd1a008c7927f3c451a69a8e801f7498268a6e360260f0 |
| tier3c.py | a7d2b6d16472acf206d94b466e114348298822d2aff065ccf5ec8436c530fb79 |
| conformance.py | db7c48be67cee2dd452e3e45dbabcda81be43a13838a69c626d21fa0a33caef2 |
| engine.py | 93bb1a259bbd90d0bf65b6753327a09bd189dafd9da41478ce072ad7d8a2adbe |
| meta_tribunal.py | 43ee32067d27bc339bf87b598d221777adb9554703c5ed467f2205f8eba202db |
| semantics.py | 775032a838e6805f5fadc7bf316c72689d5fcb8d260887bb5730521d39c181be |
| TIER3C_RESULTS_2026-09-22.json | b21bbbd86a342102252707e0991ad192a4609037fc786712521583388d56ee6c |
| TIER3C_ARTIFACT_2026-09-22.json | ccd36cf4f4278e0e6e4c856ae9724a2539dee38609620b879fc08b258bcf7aca |

The original CRLF pins remain valid on M4 and are still accepted there. Parts (a),
(b), (c), the battery, the comparison rule and the verdict rule are UNCHANGED.
