# W-O LOG (E-ANANKE-W-O, T-SWAP-AUDIT, successor of T-SWAP-LOWACC thr-5df816e9b844, MWO-0001)

Context contamination (ARC3 rule 2): before PLAN I read, as the brief instructed,
W-N REPORT.md RESULTS + DISAGREEMENTS, W-N out/verdict_changes.csv, and the tail of
W-N out/specimens_c1.log / grep of W-N LOG.md (timings, lease lines). I read the code
of W-F census.py/analyze.py, W-I main.py/analyze.py/traj.py, W-E ret_census.py,
spikes/s_ct.py, W-N plants_rel.py/swap_rel.py/run_specimens.py (to find designs and
loaders). I did not read SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD.md, ARC3_PRIORITIES.md.

A1 2026-09-29 06:55Z inventory.py (read-only over records) -> out/inventory.csv,
   out/inventory_counts.json. 733 recorded swap CHANCE verdicts:
   W-F 281 (71 specimens; 170 of them on specimens with normal lo99 < .60, class UNREADABLE),
   W-I 448 (30 specimens; 68 unreadable), spikes/s_ct 4 (2 specimens; upstream of W-E
   class labels). delay+1 CHANCE in s_ct excluded (perturbation, cannot FLIP).
   W-E out, W-G out, pte/c1b LABEL_TABLES.json, C1B_SUMMARY.json, c1b_rows: 0 swap
   verdicts, 0 CHANCE. Out of brief scope but containing CHANCE strings (not audited):
   W-B deepdive*, W-C x1b_x5/x4, W-H cf, W-J e2/e3/e6, W-L carriers_champs (already
   re-run by W-N), spikes s_joint_4781, s_m2.
73eecd8a77a0c4e5bb1a46857201a52e89fcbc4da14a0c993477b6a38c0c4930 *out/inventory.csv
   (inventory frozen before any re-run)
A2 07:05Z selfcheck.py (2 threads, no lease, ~3 min): fork_single == lens_swap.run_arms
   SINGLE on 42716814 o=9 M=64 (normal, site_all, channel_all, S, pay0 first 4 trials:
   all True); lens_swap.selfcheck all True; must-fail fork at offset+1 identical=False
   (fails as required). Timing M=512 T=228: fork 3 arms 26 s, EVERY 3 arms 48 s.
   Full-inventory estimate: SINGLE ~11 ks, SINGLE+EVERY ~33 ks (2-thread proc-s).
A3 07:20Z PLAN.md frozen (EVERY on preregistered 25 % stratified subset; SINGLE on all).
A4 07:25Z ka_repro.py: KA5 733/733 recorded CIs re-derive CHANCE; must-fail (hi .39)
   does not read CHANCE. KA6 reproduced recorded swap acc exactly at original design
   for W-F mid site_all (c939c3c7), W-F pre (6a9c62c7), W-I S o0 (00c5d3b6), s_ct
   sitestate (c16d5231). Must-fail offset+1: did NOT reproduce for 3 of 4; for
   W-F c939c3c7 mid (o 9 -> 10) it DID reproduce (the swap is time-invariant there),
   so that must-fail was not discriminating for that one row; the other three are.
   (clock correction: A2-A4 timestamps above were estimates; real clock: lease acquired
   06:59:39Z, so A2-A4 happened 06:52-06:59Z.)
A5 06:59Z Fabric lease skullport:cpu8 --as Ananke ACQUIRED lse-9ef8ebed677c (ttl 1 h,
   renew planned). Launched audit.py shards 0..6 of 7, 1 torch thread each (7 threads).
A6 07:00Z ka_plants.py (8th thread): KA2 hold_latch on 4ab2ba01 physics: site_all FLIP
   (swap 0.0), channel_all NO-EFFECT (trivially: plant sends no packets, swap == normal);
   must-fail (NO-EFFECT check fed site_all) -> FLIP, fails as required. KA3 half-pair
   latch mixture -> CHANCE (.4375 [.359,.520]); must-fail all pairs -> FLIP. KA1 W-L
   n1_s3 M=512 ns 0x601: normal .716, S and site_all FLIP (.270 [.253,.284]),
   channel_all NO-EFFECT; must-fail (FLIP check fed channel_all) -> NO-EFFECT. All PASS.
A7 07:07Z first groups done: EVERY-subset groups cost 140-440 s at 1 thread; projected
   shard finish ~09:00Z (inside budget).
A8 07:17Z DEVIATION (order only, no threshold/rule change). The EVERY subset is the
   lowest-hash 25 % per stratum and shards also run in hash order, so the 7 shards were
   running the costly EVERY groups first (12 groups in 18 min; projected > 5 h for the
   full inventory). Stopped the 7 shards (PIDs 22864 27008 2224 15888 27636 25772 26824,
   matched on exact cmdline 'python.exe audit.py <i> 7 1'); their in-progress groups
   were lost, 12 completed groups kept. Relaunched as 8 shards x 1 thread with
   WO_MODE=single (SINGLE + census for every remaining group, primary first); EVERY for
   the remaining subset groups will run afterwards with WO_MODE=every
   (out/rerun_every_s*.jsonl) as time allows; any subset group without EVERY is
   reported as EVERY NOT_RUN.
A9 07:20Z lease lse-9ef8ebed677c RENEWED ttl 7200 s.
A10 07:50Z BUG: audit.arm_names parsed s_ct arm "payload" as pay<k> -> ValueError on group SCT 4781b0a1 (recorded as error line in rerun_s4.jsonl; errors are excluded from done-sets). Fixed (pay<digits> only); group to be re-run after the shards.
A11 08:55-09:01Z tail balancing: shards 0/2/7 lagging; added WO_REVERSE helper mode
   (same shard list reversed, writes rerun_s<i>r.jsonl; duplicates harmless, last wins
   in summarize). Helpers launched for shards 2, 0, 7, 4 only when a thread freed
   (<= 8 processes x 1 thread at all times). Helper 4 also re-runs the errored SCT group.
A12 09:14Z coverage 249/249 groups SINGLE. Stopped the 6 remaining duplicate workers (exact cmdline 'audit.py <i> 8 1'); process count 0. EVERY for the remaining 55 subset groups NOT RUN (budget). Lease lse-9ef8ebed677c RELEASED 09:14Z; status shows it gone.
A13 09:18Z summarize.py -> out/summary.json, summary.txt, rerun_table.csv,
   corrections_WF.csv, corrections_WI.csv. 733/733 verdicts re-run SINGLE (249 groups);
   EVERY on 29 verdicts (12 subset groups) only. The 'errors 1' in summary.json is the
   superseded SCT 4781b0a1 error line (re-run successfully by helper 4).
   Checks of the re-derivation code: re-deriving the RECORDED W-F class from recorded
   verdicts matches 166/166 records (0 mismatches); re-deriving W-I reader/sub_chance/
   sub_flip from recorded verdicts matches 135/135 audited table rows.
   Predictions vs outcome: FLIP 30+-10 % -> 12.3 %; NO-EFFECT 15+-10 % -> 3.8 %;
   CHANCE 55+-15 % -> 83.9 % (all three outside the predicted bands). Readable FLIP
   ~40 % -> 7.9 %; unreadable FLIP <= 10 % -> 21.4 % (117/238 "unreadable" verdicts
   sit on specimens whose normal lo99 exceeds .60 at M=512). SINGLE/EVERY agreement
   28/29. D1 call: PARTIAL (readable CHANCE->FLIP 39/495, cluster 99 % [.037, .125]).
