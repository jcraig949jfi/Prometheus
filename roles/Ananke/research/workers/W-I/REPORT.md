<!-- DEPOSITED VERBATIM by Ananke for worker W-I; sha256(report)=7ebedafcc1f9eff6; delimited; see REPORT.provenance.json -->
W-I REPORT: how causally used information moves through carriers over time
Worker W-I, namespace 0x5EE, 2026-09-28. PLAN.md was frozen before the main runs. LOG.md has attempts A0-A10.
The GPU was BUSY the whole time (W-H, then W-J). I queued the job and ran the same frozen experiment on CPU: a cpu8 lease with 4 processes x 2 threads, then 2 threads for the robustness runs. The GPU was never used.

WHAT I TESTED
- 33 C1 champions:
  - PANEL: 20 cells that share one physics (d9ccb6a7: ring 144, sample). These are 18 RELAY cells (census SITE 7, CHANNEL 6, JOINT 5), plus HOLD M2 4ab2ba01 and MAJ 4781b0a1.
  - SPAN: 13 cells across global, torus, smallworld and ring, in HOLD, RELAY and MAJ, covering every census class.
  - 42716814 was UNREADABLE (lo99 .577) and gets no reader labels.
- Reader axis:
  - Mirror-pair swaps at every tick offset from cue onset -1 to readout -1, applied in every trial.
  - Arms: site_all, channel_all, joint, S, inbox, channel_content, channel_count, plus Kp/r/w/E where the physics allows.
  - All arms are batched as independent 64-world blocks of one World. This is bit-identical to lens.run: checked on 3 specimens and 3 arms.
- Physical axis:
  - Single-cue twins on trials 3, 5 and 7.
  - Per tick, I recorded which state differs: S, inbox, Kp, r, w, E, in-flight count (N), in-flight payload with equal count (V), who fires (F), emitted payload (P).
  - I also recorded the spatial spread of the S differences (distance from the source and from the actuator).
- Reader labels per offset: S (site FLIP), C (channel FLIP), D (both), M (joint FLIP and phi &lt;= -.3), J (other joint FLIP), E (all NO-EFFECT), X (otherwise).
- phi is the correlation between "site swap wrong" and "channel swap wrong" over trials where the normal run is correct.
- Robustness conditions: loss +.2, jitter +2, latency +2, a distractor channel, and size x2. Retention = (acc - .5) / (base - .5).

WHAT HELD
1. The F6 pre-cue control is clean: offset -1 is E (NO-EFFECT) in all 32 readable specimens.
2. The census replicates on new seeds. At W-F's mid tick my label matches the census class in 30/32. The mismatches are 0187372b (ELSEWHERE, I get S) and 613162a3 (SITE, I get M).
3. The mid-tick census class is a PHASE reading, not the carrier.
   - All 7 panel RELAY cells the census calls "SITE" have a channel phase first: C at offsets 1-4, then S (CCCCSSS, or CCCCJSSSSSSSSSS for delta 16).
   - Not one panel RELAY specimen is site-only.
   - Physically, the source fires once (F at offset 1, fire_at_src = 1.0). Packets fly for 2-5 ticks. Then several sites latch, and the S-difference front moves out from the source (mean distance 0 -&gt; 1 -&gt; 2). The actuator latches at offset about 5 (S_act .54 -&gt; .77).
4. Motifs that pass the frozen recurrence rule (&gt;= 3 readable specimens and &gt;= 2 physics digests):
   - R1 SITE-ONLY RETENTION: 8 specimens, 8 digests. All HOLD, off the panel.
   - R4 CHANNEL-&gt;LATCH (C then S at the reader): 14 specimens, 2 digests. 13 are panel physics, plus torus 63d17a90, so it only just passes.
   - R2 CHANNEL-ONLY DELAY: 3 specimens, 2 digests. All are delta-4 cells (a02aa099, dcd404a9, M3 0a23398f), where latency is about equal to the interval.
   - P1 TRAVELLING WAVE: 10 specimens, 2 digests.
   - P2 SOURCE-PRESENCE: 18 specimens, 6 digests.
   - P3 PAYLOAD-VALUE: 10 specimens, 4 digests.
   - P4 SITE-ONLY PHYSICAL: 3 specimens, 3 digests.
   - Seen but not recurring (1-digest or too few):
     - R3 store-&gt;channel: 78f3b0ec, 4781b0a1.
     - R5 S-&gt;C-&gt;S regeneration: 31cd2a8a, bbef66a1, ed16c553. This is the brief's store -&gt; emit -&gt; channel -&gt; readout at the reader level.
     - R6 mixture band: 3 specimens, all panel.
     - R7 split band: 369f5a5b, 4781b0a1.
5. The two axes dissociate, so the reader's register cannot stand in for the physical code (F7 holds on real champions).
   - Presence code read as content: 6 panel specimens (e9196cae, 62a7fff9, 35c721fd, bf82cb29, bbef66a1, 31cd2a8a). Physically the in-flight difference is count/presence (N, no V), yet the reader FLIPs on channel_content.
   - The opposite also occurs. 78f3b0ec, e06701a5 and a02aa099 have physical N and the reader FLIPs on channel_count.
   - M2 4ab2ba01 is physically payload-value (V at 9/9 offsets, no firing difference). This agrees with the principal's content reading.
6. Cue-dependent state that is present but unused:
   - HOLD 7b7b025e: the twins differ in-flight (N, V, F, P) at all 9 interval ticks, because the source re-emits every 2 ticks. Still, channel swaps leave the readout trace bit-identical at 9/9 offsets and the reader is S only. ab089e45 and 1c0a1bc7 show the same pattern.
   - Routing w differs between twins in 8 of the 20 panel specimens. The w swap is never FLIP or CHANCE.

ROBUSTNESS (frozen test)
- Panel test (primary): INCONCLUSIVE by the frozen eligibility rule, because SITE-ONLY n = 0 and all 18 are CHANNEL-USING.
- Across all specimens (secondary, confounded by physics and family: every SITE-ONLY specimen is a HOLD cell):

| Condition | Median retention, SITE-ONLY (n=8) | Median retention, CHANNEL-USING (n=23) | Difference [95% CI] | Frozen decision |
|---|---|---|---|---|
| latency | 1.00 | .91 | .09 [.02, .46] | H1 NOT SUPPORTED |
| jitter | 1.00 | .97 | .03 [.01, .12] | H2 NOT SUPPORTED |
| loss | 1.00 | .87 | .13 [.12, .15] | H3 NOT SUPPORTED: direction as predicted, below the .20 bar |
| distractor | 1.00 | .41 | .59 [-.08, .92] | H4: no difference (two-sided) |
| size | 1.00 | 1.01 | about 0 | H5: no difference (two-sided) |

- EXPLORATORY (post hoc, explore.py; not a test):
  - Latency tolerance tracks "slack", the ticks between the last C/M label and the readout. Spearman .52, n = 23.
  - Every channel-carried specimen with slack &lt;= 1, except one, lost most of its latency retention: a02aa099 .00, dcd404a9 .00, M3 .02, M2 4ab2ba01 .06, bf82cb29 .21, ed16c553 .54.
  - The exception is 78f3b0ec (1.01). Its source keeps re-emitting a count code, so a late arrival is replaced by the next one.
  - Slack &gt;= 2: mostly &gt;= .85, but 35c721fd (.47) and e9196cae (.35) fall below.
  - The panel is hurt badly by distractor traffic (median retention .19).

SURPRISES
- An instrument identity. Mirror partners share every exogenous draw. After a swap, world B's site-swapped state (site_A, chan_B) is exactly world A's channel-swapped state. When no input arrives before the readout, site_acc + chan_acc = 1 by construction.
  - identity_check.py: 100% of trials identical for 2dccdaa5, 4ab2ba01 and 78f3b0ec; 98% for 4781b0a1; 62-68% for 369f5a5b, where history carries across trials.
  - So "sum is about 1" is not evidence of a mixture.
  - What does discriminate is phi, which equals minus the correlation of the two partners' site-swap failures.
- Census JOINT cells at the mid tick:
  - Real per-trial mixtures (M): 2dccdaa5 (phi -.94), c16d5231 (-.72), 78f3b0ec (-.63).
  - Not mixtures (J):
    - 8c37f32e -.24, e06701a5 -.28.
    - 369f5a5b: phi +.12 to +.29 across all 14 offsets.
    - 4781b0a1: phi about +.05 through offsets 5-10. That fits the principal's "two stages holding the same bit" conflict, not a mid-transit handoff.
- M2's reader trajectory is channel for 8 ticks and site only at ro-1 (CCCCCCCCS). I predicted S/C regeneration; that was wrong. Regeneration shows only physically: the emitted payload differs every other tick.
- My prediction Q2 failed: 3 of the 4 global HOLD site-latches also emit cue-dependent traffic that nothing reads.

DISAGREEMENTS (with SYNTHESIS_2026-09-28_ARC2 / the instrument card F5' / PTE_ENGINE_CARD; I read them only after all runs, LOG A8)
- D1 "All 14 JOINT cells are per-trial phase mixtures (site_acc + chan_acc = 1.00)": not supported.
  - The sum is forced by the mirror-pair design.
  - By phi, 3 of the 7 census-JOINT cells I retested are mixtures at the census mid tick. 4 are not.
  - 369f5a5b stays non-mixture J for its whole interval.
  - F5' should be changed to use phi, or a per-pair identity test, not the sum.
- D2 "Routing: infrastructure only / never carried the bit": I agree for the reader (w never FLIP or CHANCE). But routing is not cue-free: the twins differ in w in 8 of the 20 panel specimens. The bit is written into routing and not used.
- D3 The census-era "RELAY SITE" class (10 cells): in the 7 panel RELAY SITE cells here, the bit is in the channel first and at the site only after it lands. There is no site-only RELAY mechanism in that set.
- No disagreement:
  - M2's content code (confirmed physically, V).
  - F7 (confirmed on 6 champions).
  - "In RELAY/MAJ the carrier is a trajectory" (confirmed, and it extends to census-SITE RELAY cells).

PROPOSED THREADS
- T-CT-3 (preregistered): does slack predict latency tolerance?
  - Use a latency dose of +1, +2 and +3 on the 20-cell panel and fresh d9cc champions with delta 4, 8 and 16.
  - Prediction: retention is about 0 when the added latency exceeds slack, unless the source regenerates. Treat 78f3b0ec as the named exception.
- T-INS-6: rewrite F5' with the phi / partner-identity test. Add a single-trial-swap variant, so history does not break the identity. Promote traj.py (batched arms plus the two-axis twin profile) into lens after review.
- T-CT-4: a census of present-but-unused state across all 166 cells: twin difference exists but the swap has NO-EFFECT (w, HOLD re-emission).
- T-CT-5: the panel's distractor fragility (median .19) against its reader register (content vs count).

FILES (roles/Ananke/research/workers/W-I/)
- PLAN.md, LOG.md, QUEUE.md (Q1 marked VOID).
- Code: traj.py, main.py, robust.py, analyze.py, explore.py, identity_check.py, smoke.py.
- out/table_&lt;cell&gt;.csv: 33 per-specimen, per-offset two-axis tables.
- out/traj_&lt;cell&gt;.json: raw data.
- out/traj_table.csv, motifs.json, robust.json, robust_tests.json, explore.json, identity_check.json, analyze_console.txt.
