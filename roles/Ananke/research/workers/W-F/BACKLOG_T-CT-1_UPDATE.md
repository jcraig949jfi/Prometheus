Proposed replacement for the T-CT-1 entry in BACKLOG_TEMPORAL_DISTRIBUTED.md
(W-F cannot write outside its directory; Ananke applies):

T-CT-1 DONE 2026-09-28 (workers/W-F/REPORT.md, out/census_table.csv): all 166
  C1 SIGNAL cells, carrier_table at the c1b mid tick. 124 readable: SITE 92,
  JOINT 14, CHANNEL 13, ELSEWHERE 5 (42 UNREADABLE). HOLD is site-carried
  (81/85; the one CHANNEL is M2 4ab2ba01). Decision: FAMILY SELECTS (depth-2
  physics tree 0.730 vs family-only 0.797 CV; gain -0.07). Inside RELAY/MAJ
  nothing predicts the class (~0.40, 11 physics points), and one RELAY
  physics+env point holds SITE 4 / CHANNEL 4 / JOINT 4. Every JOINT cell has
  site_acc + chan_acc = 1.00: a per-trial mixture caught mid-handoff
  (channel -> site latch), not a joint code. Consequence for C2: the RELAY
  carrier is a TRAJECTORY; a single-tick class is a phase reading.
  Split into T-CT-2 (carrier trajectory over all ticks, RELAY/MAJ) and T-CT-3
  (per-trial mixture test for JOINT), T-CT-4 (why the MAJ pw4/dest-all point is
  always channel-carried).
