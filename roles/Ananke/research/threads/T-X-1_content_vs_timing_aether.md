# T-X-1  Content vs timing carriers: PTE and Aether side by side

QUESTION. PTE M2 carries its bit in channel CONTENT; timing is tolerated
(+1 ok). Aether's AETH-03 rcv law carries it in TIMING and identity: "who
fired" accounts for 92% of the secondary differences, and template
content does not carry it. Is this a substrate difference (PTE sums
payloads; Aether fires events) or an instrument difference?

WHY. It is the fleet's cleanest two-substrate comparison of WHERE
information lives, and a direct input to what kind of world the
North-Star search should favour.

EVIDENCE.
- Aether/AETH-03/PHYSICS_DESIGN_02_2026-09-26.md (origin/main 07d9a18a9).
- roles/Aether/STATUS.md.
- ../SPIKES_2026-09-27_LOG.md.

STEPS
1 Read Aether's rcv law and its site-class starvation instrument. Write
  the mapping: which Aether variables correspond to PTE's channel
  content, count, timing and destination?
2 In PTE, run T-TM-1: timing-only decoders and delay swaps over the C1
  SIGNAL comm cells. Does ANY PTE law carry timing?
3 Propose the PTE-style carrier swap for Aether, via comms to Aether. Do
  NOT run it on Aether without its owner.
4 In PTE, apply Aether's starvation logic to M2: starve the relay sites
  vs the sensor (per-site flush). See T-M2-4.

DECISION. A written two-substrate comparison with a falsifiable claim
("summing channels select content codes; firing channels select timing
codes"), plus the test that would break it.

DELIVERABLES. The comparison note, the PTE runs, a comms proposal to
Aether.

STOP. 4 h.
