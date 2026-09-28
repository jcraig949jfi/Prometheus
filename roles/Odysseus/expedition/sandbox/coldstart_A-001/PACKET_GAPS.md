# PACKET_GAPS -- sandbox/PACKET.md, cold-start trial coldstart_A-001

Currency: 2026-09-28. Worker: fresh subagent, no oral context beyond the
operator's local adjustments (output path, no git writes, 1 process, 45 min,
no comms). Worktree /home/jcraig/Prometheus-worktrees/odysseus-base-role at
HEAD 02800d2b5 (origin/main 7720539d4). Pure ASCII.

Everything below is something I had to work out that PACKET.md did not tell
me. BLOCKING = a worker following the packet literally, on another machine
or without this operator's adjustments, could not complete the task or
would produce a wrong/destructive result. MINOR = cost time or needed a
judgement call.

## Gaps

G1 BLOCKING -- "Inputs (all in git)" is false. The whole
   roles/Odysseus/expedition/sandbox/ directory is UNTRACKED (git status
   '??'); `git log --all -- roles/Odysseus/expedition/sandbox` is empty; no
   remote ref contains world.py, battery.py, known_answer.json, PREREG.md or
   the packet itself. The trial only worked because I was pointed at a
   working tree on the machine that built it. "Reproduce the gate from git
   alone" is impossible today. Same for the referenced
   accumulation/ACCUMULATION_v0.md: tracked, but its s8 "REVISION v0.1" is
   an UNCOMMITTED modification (git diff: +59 lines). Also untracked:
   foreign/raid_A, census/ (cited by ACCUMULATION v0.1 as evidence).

G2 BLOCKING (hazard) -- no reproduction command is given, and the obvious
   one (`python3 run_battery.py known`, the documented usage) OVERWRITES
   known_answer.json in place, i.e. destroys the fixture it is supposed to
   be compared with (and, since the files are untracked, irrecoverably).
   It also hard-codes multiprocessing Pool(4). I wrote a serial runner
   (run_coldstart.py) that imports the originals read-only and writes into
   my directory. The packet should give: command, output path, process
   count, expected wall, and "compare to known_answer.json with tolerance X".

G3 MINOR -- the fixture gives no tolerance or comparison level (bit-exact
   per-world values? rung verdicts only?), and the Python version that
   produced known_answer.json is not recorded (the result depends on
   CPython's `random` stream being stable across versions). I defined
   REPRODUCED-EXACT / REPRODUCED-VERDICT in my PREREG. (Here: Python 3.14.4.)

G4 MINOR -- which ladder version scores a new cheat? Packet freezes
   ../PREREG.md (monotone ladder: each rung requires every lower one), but
   ACCUMULATION_v0.1 A3 (uncommitted) says rungs are awarded INDEPENDENTLY
   and redefines R0; A2 makes convention 3-way. For my cheat the two
   readings could differ, so I preregistered reporting both.

G5 MINOR -- "catches" is undefined for a new cheat world: highest rung
   below R3? any decisional test fails? a non-decisional report (episode
   permutation, fresh-world transfer) flags it? I fixed: caught iff
   highest(T) < R3 under frozen decide().

G6 MINOR -- "May change: afterwards, new cheat worlds" does not say whether
   a cheat world may change the PHYSICS (a new environment family) or only
   the planted genomes. Mine needed a new environment family (per-colony
   bias); I kept the three physics draws per colony so the event-stream
   guarantee (DESIGN s3) holds, and added an identity control (the extended
   copies reproduce original P and C per-world values exactly).

G7 MINOR -- the packet's example cheats ("record POSITION or write-timing")
   point at what the apparatus is already built to catch: the
   equal-capacity random intervention preserves the BLANK pattern exactly,
   so any presence/position-only reader has Dr = 0 by construction, and
   organisms cannot observe write timing at all (they see only the record
   tuple). A worker following the hint literally tests nothing new.

G8 MINOR -- PREREG.md and code disagree on two planted arms; the packet
   does not say which is authoritative (the fixture was produced by code):
   (i) C readers on BLANK go to site 1 in code (planted_genomes 'C'),
   PREREG s2 says "a random site"; (ii) N_b writers write a constant
   per-genotype symbol (i % 4) in code and DESIGN, PREREG s2 says "a
   uniformly random symbol every generation". Neither changes the gate, but
   a re-implementer from PREREG would build different worlds.

G9 MINOR -- prior experiments: the packet names none. DESIGN.md s0 has a
   good prior-work section (Archaeon W-artifacts null without a positive
   control; E5 notes; Ananke T-ENV-1), and RESULT.md s4 lists the known
   defects C1-C8, but the packet does not point at them; no
   prior_work_search log sits beside the packet (READY_PROTOCOL's SEARCHED
   state). I ran expedition/prior_work_search.sh (log in this directory):
   no other world-record sandbox or known-answer cheat battery in any ref.
   Relevant cheat-control precedents: ares/DESIGN_C0.md (W2/W4 shuffled
   controls), crius/tests/test_sandbox.py (cheat control on the assay).

G10 MINOR -- the fixture omits P4 (secondary: R4 detection unvalidated) and
   the A/A validity criterion, both of which are gate criteria or reported
   gate facts; the falsifier ("any of P/N_a/N_b/C mis-scored") omits A/A,
   the criterion that actually failed run 1.

G11 MINOR -- output location, artifact contents (RESULT_COLDSTART.md
   sections) and whether a preregistration is required for the cheat are
   not stated in the packet (00_READ_FIRST says prereg everything; the
   operator supplied the path).

G12 MINOR -- running tests/ as documented writes __pycache__ into the
   original directory (run_battery sets dont_write_bytecode, the tests do
   not); use PYTHONDONTWRITEBYTECODE=1. Not needed for the gate.

## The six READY questions

(a) find every input ................ YES here, NO from git (G1, BLOCKING)
(b) identify important prior exps ... YES, via DESIGN.md s0 + my search,
                                      not via the packet (G9)
(c) state frozen vs may-change ...... YES with judgement calls (G4, G6)
(d) reproduce known-answer fixture .. YES, bit-exact (5040/5040 values, gate
                                      identical), with a self-written serial runner (G2)
(e) state the falsifier ............. YES (packet states it; G10 caveat)
(f) produce the artifacts ........... YES (RESULT_COLDSTART.md, this file)

## READY judgement

NOT READY. The science is sound: the fixture reproduces bit for bit. Two
gaps are BLOCKING:
- G1: none of the inputs are in git.
- G2: the only documented command destroys the fixture.
Both are cheap to fix:
- Commit sandbox/ together with the v0.1 revision of ACCUMULATION_v0.md.
- Give the packet a non-destructive reproduction command with an explicit
  tolerance.
Once they are fixed, a second cold-start trial should be able to reach
READY. Recommend adding T (nest tag) to the known-answer set: the frozen
battery awards it R3 (RESULT_COLDSTART.md s2).
