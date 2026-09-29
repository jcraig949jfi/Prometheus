# Ananke status

Currency: 2026-09-29T03:34Z (MWO-0001 adoption). Machine-readable state:
WORK_STATE.json. Work map (thr-/C-/E- ids): research/THREADS.md.

seat state: ACTIVE under MWO-0001 (mwo_commit 7e4c09f2c). Nothing running,
  no leases held, no Fabric tasks, no operator decision pending.
done: PTE-C1 (6596 rows; C1_REPORT.md, C1_ERRATA.md). PTE-C1b ran as frozen
  under the operator C1B HOLD RELEASE of 2026-09-26 (27/27 cells, package
  cc98596dd; pte/c1b/REVIEW_PACKET_PTE_C1b.txt). Research arcs 1-3 closed:
  SYNTHESIS_2026-09-27 (c34cbb463), _ARC2 (8eabc990b), _ARC3 (7fc642367).
what it asserts (ARC3): search reachability, not physics, bounds what PTE
  shows (H6); no nontrivial retention regime in evolved champions, SI01
  CLOSED for current champions (W-G); carriers are trajectories (W-I);
  receiver semantics act through aggregation gain (W-J); no universal
  intervention-reach check, lens.verify_reach built (W-K).
leases: Fabric only (lease cutover 8370083ae is in this branch);
  research/lease.py is a Fabric frontend. No host-file leases.
next executable action: small bounded CPU blocks (MACHINE_WORK.md B-8
  T-INS-6, B-10 T-SWAP-LOWACC). No new large PTE campaign under MWO-0001.

---
## SUPERSEDED (2026-09-25 text, kept verbatim)

# Ananke status

Currency: 2026-09-25T00:10Z (from date -u).

seat state: ACTIVE. PTE-C1 DONE (2026-09-24T12:04Z -> 2026-09-25T00:06Z,
  12 h 02 m, 0 failed cells, 6596 rows).
what it asserts: PRESENT, ACTIVE, PRODUCTIVE. VALID (the campaign's
  question), graded: COMM_DEPENDENT + CAUSAL_SUPPORT + REPRODUCED for
  RELAY routed relay (size-free to N=2304; topology-bound); no cross-family
  transfer; XOR/FLIP NULL; SUPPORTED phase boundaries gate a hand design,
  not evolved machinery. Not yet adversarially reviewed.
evidence: roles/Ananke/pte/C1_REPORT.md, REVIEW_PACKET_PTE_C1.txt,
  c1_report/ (report.py output), c1_a0/, c1_posthoc/.
monitors owned: none running (AnankePTE_C1 row set DONE; task Disabled).
blockers: adversarial review requested from Kairos (#564) and Elenchus
  (#565); not blocking.
next executable action: PTE-C1b prereg (adjudicate delay-line HOLD memory
  and self-modifying MAJ properly), then PTE-C2 prereg (weather in the
  causally verified habitable zone, three load axes, fixed boundary rule).
