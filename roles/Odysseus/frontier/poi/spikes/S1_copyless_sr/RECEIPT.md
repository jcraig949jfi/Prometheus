# Spike S1 -- "self-replicators" that cannot copy themselves (BEE coupling campaign)

Currency: 2026-09-27. Odysseus, ubu001. Frontier thread: POI-004 (BACKLOG.md).
Origin: internal harvest I1 (raw/I1_z80_lineage_worlds.md, D2) flagged 15 of 68
"de novo competent self-replicators" with no copy instruction.

## Question
Are the dominant "competent self-replicating" tapes of Bellerophon's coupling
campaign (roles/Bellerophon/coupling_2026-09-24/COUPLING_ORIGIN_LEDGER.jsonl,
68 rows) able to copy themselves? The world labels an organism a
self-replicator by how it was BORN -- sr_depth > 0 means its birth was a
self-replication event of its WRITER (prometheus/z80atlas/world.py
_competence_summary) -- and the ledger's architecture descriptor
(adjudication.arch_descriptor) runs each tape ONCE: input 42, zero window.

## Method (probe.py, stdlib, frozen VM at commit ade0d6243)
For each of the 68 tapes: run it alone for all 256 input values with the
window holding (a) zeros, (b) a copy of itself, (c) fixed random bytes; score
self-copy with repro_descriptor's own rule (>= 0.9 L window bytes written by
own-tape-sourced copy ops, >= 90% from own code, fidelity >= 0.9). For the 15
copy-less tapes, count single-byte edits (64 x 255) that make the tape a
self-copier on input 42 / zero window.
Command: `python3 roles/Odysseus/frontier/poi/spikes/S1_copyless_sr/probe.py result.json`
(231 s, 16 MB, ubu001). Rows: result.json beside this file.

## Result
- Copy-less by the ledger (n_copy_ops == 0): 15. Of these, 14 write NOTHING to
  the window under any of 256 inputs x 3 window contents; 1 (c009689,
  SHUFFLED K40) self-copies for exactly 1 input with a random window.
- Copy-bearing controls: 53. 47 self-copy (for 249-256 of 256 inputs); 6
  carry copy instructions but never self-copy (all 6 already have
  self_copy=false in the ledger; arms OFF x3, YOKED, SHUFFLED x2).
- So 20 of 68 (29%) dominant "competent self-replicators" do not copy
  themselves under any condition tested (14 never, 6 copy-op-bearing
  non-copiers; c009689 counted as a copier on its one input).
- By arm: ON 3 of 42 (7%); non-ON arms 17 of 26 (65%).
- 9 of the 15 copy-less tapes become self-copiers with ONE byte edit
  (35 to 244 distinct edits each); 5 have none. Consistent with -- not proof
  of -- sterile mutant descendants of a real replicator.

## What it changes
- "Competent self-replicator" in this campaign is a BIRTH label, not a
  capability. In the control arms it mostly names tapes that cannot copy
  themselves. The ON-vs-control contrast in de novo competent SR is therefore
  partly a contrast between real copiers (ON) and sterile, label-carrying
  dominants (controls). The contrast in REAL copiers is 39/42 vs 9/26 --
  larger in ratio, smaller in count than the labelled one -- but the question
  shifts: how does a tape that cannot copy itself become the dominant
  "self-replicator" of a run?
- The same label feeds the running multi-day campaign's primary endpoint
  (I6 exposure list: world.py sr_depth). Reported to Bellerophon (owner).
- Failure shape: label read as property (the program's most recurrent,
  raw/I6_failures_reversals.md).

## Limits
Isolation test only: the world's birth semantics (target_fill preserve, copy
cost, lifespan, neighbour execution) are not replayed; a tape could
reproduce in-world by a route this isolation rule does not see. That route
would itself be the finding. Not run: in-world replay of any of the 20.
