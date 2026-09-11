# Arachne run 2026-06-04 -- the only run to date, archived verbatim

Archived 2026-09-11 on the base-role adoption pass. These five files are
byte-for-byte copies of the gitignored runtime residue the June run left
at agents/arachne/{fabric,state}/ in what is now the canonical checkout
(agents/arachne/.gitignore excludes fabric/, state/, logs/). Hashes in
MANIFEST.md (sha256 over LF-normalised bytes, comms/manifest.py). The
originals are left in place; they are the operator's to clean up.

Provenance of the run: swarm.py run by hand on 2026-06-04 between about
06:20Z and 11:21Z (the swarm_state.json updated_at is 2026-06-04T11:21:33Z,
tick 700), across the commits 7a29f8583 .. 3b9d9ed15 of that day; the
code that produced the later ticks is 3b9d9ed15 or earlier the same day
(the residue does not record the SHA per tick -- a defect the receipt
rule of D-23 s4 now closes for any future run).

Files:
  edges.jsonl               21,209 edges; every edge {src, dst, op, landscape,
                            crawler, born_at, null_p}; 5,621 distinct nodes
  swarm_state.json          watcher state at tick 700: landscapes_available
                            (mathlib, lmfdb, algolib, oeis, knots, groups),
                            7 crawlers alive, graveyard 120, recent_dead
  population.json           the saved population (rulesets) at tick 700
  lineage.jsonl             470 events: branch 82, death 124, floor_revive 42,
                            rosetta_weave 219, operational_weave 3
  harvest_2026-06-04.md     traverse.harvest output: 5 verified computes
                            anchors, 58 void targets, edge mix, top hubs

What this residue supports: the calibration rows in
roles/Arachne/CALIBRATION.md, the archaeology in
roles/Arachne/ARCHAEOLOGY_2026-09-11.md, and the backlog items that read
it (ARACHNE-05, -10, -13, -14, -16, -26). What it does not support: any
claim of emergent organization (the one judge run was negative and the
partition, ablation and degree-preserving-null tests never ran).
