# Odysseus backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-26 (charter adopted; pre-charter backlog at
superseded/BACKLOG_H0H5_pre-charter_2026-09-25.md). First five start today.

ODYSSEUS-01 | Run the odysseus/tests suite on a Windows host and commit its receipt | TOOLS | alpha | S | a Windows seat (delegation to M1/M2) | receipt file with python version, OS build, pytest tail
ODYSSEUS-02 | Run a two-host UDP brain ubu001 <-> ubu002 and verify against the in-process reference | ENGINE | alpha | S | Artemis (node on ubu002) | committed run receipt + verify output + reference match count
ODYSSEUS-03 | Measure tick rate, datagrams/tick and bytes/tick vs loss rate on one host and commit the table | EVIDENCE | alpha | S | none | odysseus/measurements/ table with commands
ODYSSEUS-04 | Commit a node install note for Linux and Windows (python only, firewall rule, bind address) | TOOLS | alpha | S | none | odysseus/INSTALL.md
ODYSSEUS-05 | Add a cross-host run launcher that starts nodes from a fleet manifest (host, port, shard, cap) | ENGINE | alpha | M | none | odysseus/brain/fleet.py + test with loopback manifest
ODYSSEUS-06 | Replicate every keyframe and log segment to a second host and prove recovery after deleting the original | ENGINE | beta | M | ODYSSEUS-02 | test that deletes a shard dir and replays from the replica
ODYSSEUS-07 | Replace the per-shard in-memory log index with an on-disk tick index so logs of millions of ticks open in O(1) | ENGINE | beta | M | none | test opening a 10^6-tick log under a time bound
ODYSSEUS-08 | Make shard state memory-mapped by default in nodes with a per-host byte cap from the fleet manifest | ENGINE | beta | S | ODYSSEUS-05 | test that a node refuses a shard larger than its cap
ODYSSEUS-09 | Global (multi-shard) fork: resume the whole brain from a keyframe tick with an intervention over UDP | ENGINE | beta | M | none | test: no-op global fork reproduces recorded roots; ablation diverges
ODYSSEUS-10 | Replay a shard's escaped fork across only the shards it reaches (light-cone replay) | ENGINE | beta | L | ODYSSEUS-09 | test: effect set equals full global fork's
ODYSSEUS-11 | Record per-tick telemetry (probe values) in an indexed side file and query it to find candidate ticks | ENGINE | beta | M | none | test: planted weak signal is found by query and rewound to
ODYSSEUS-12 | Add delta frames (changed words only) between keyframes and measure storage vs seek cost | EVIDENCE | beta | M | ODYSSEUS-03 | measurement table + round-trip tests
ODYSSEUS-13 | Re-shard a running brain (versioned partition map per tick) and prove rewind across the re-shard | ENGINE | 1.0 | L | ODYSSEUS-07 | test: roots before/after re-shard unchanged
ODYSSEUS-14 | Add a node joining/leaving protocol (lease, heartbeat, restore-from-replica on loss) | ENGINE | 1.0 | L | ODYSSEUS-06 | test: kill a node mid-run, run completes, roots match reference
ODYSSEUS-15 | Add multicast for tick/barrier announcements with unicast fallback and measure on the LAN | ENGINE | 1.0 | M | ODYSSEUS-02 | LAN measurement receipt (wired and WiFi separately)
ODYSSEUS-16 | Accept an explicit per-shard synapse table (grown/learned connectivity) beside procedural connectivity | ENGINE | 1.0 | M | a consumer's model | test: table and procedural give identical runs when equal
ODYSSEUS-17 | Numpy-backed shard step with bit-identity to the pure-Python step (pinned versions) | ENGINE | 1.0 | M | numpy on the host | test: 1000 ticks identical hashes across both paths
ODYSSEUS-18 | Offer the substrate to Aether with a mapping of its replay-identity tuple onto run.json | ENGINE | 1.0 | S | Aether | committed prompt to Aether + its reply
ODYSSEUS-19 | Register the resident node agent in roles/base-role/MONITORS.md with bound N and accountable seat before first launch | EVIDENCE | beta | S | ODYSSEUS-05 | MONITORS.md row
ODYSSEUS-20 | Evaluate Aeron (C media driver) against the stdlib transport on measured traffic and record keep/replace | LIT | 1.1 | M | ODYSSEUS-03 | decision note with numbers
ODYSSEUS-21 | Decide the fleet donation policy: per-host RAM/disk caps and hours | TOOLS | beta | XL | NEW: operator sets per-host donation caps | cap table in the fleet manifest
ODYSSEUS-22 | Open Windows firewall UDP ports for brain nodes on each Windows host | TOOLS | alpha | XL | NEW: operator approves inbound UDP rule per host | rule names + a cross-host run receipt
ODYSSEUS-23 | Build the older-laptop clone image notes (python, repo checkout, node service) for u00x machines | TOOLS | beta | S | ODYSSEUS-04 | odysseus/INSTALL.md section + one clone booted
