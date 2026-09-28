# W-F REPORT  T-CT-1 carrier census over all C1 SIGNAL cells

(Saved by Ananke from W-F's final message; the harness refused the
worker's write. PLAN.md (frozen before any census run), LOG.md (A0-A6),
census.py, analyze.py, explore_nonhold.py (post hoc, labelled),
out/census_s{0,1}.jsonl, out/census_table.csv, out/model.json,
out/explore_nonhold.txt and smoke runs are in this directory. The census
finished with 0 errors in ~80 min on two GPU shards x 1 thread (cpu8 was
held by another seat). The GPU lease was renewed once, then released. On
one smoke cell the CPU and GPU tables were bit-identical.)

Namespace 0x5EA, 64 worlds = 32 mirror pairs, 99% pair bootstrap.

TESTED: all 166 C1 evolve cells with held lo99 > .55 (HOLD 97, RELAY 50,
MAJ 19). lens.carrier_table after the c1b "mid" tick of every trial; arms
site_all, channel_all, channel_content, channel_count, pay<k>, w; a joint
swap only when no single arm FLIPped (F1, classification only). Secondary
checks: late tick ro-1 (F2), pre-cue t0-1 (F6), arm_identical (F4).

CENSUS (mid tick)     CHANNEL  ELSEWHERE  JOINT  SITE  UNREADABLE
  HOLD                   1         3        0     81      12
  RELAY                  6         2       12     10      20
  MAJ                    6         0        2      1      10
Readable 124/166. In all 124: the pre-cue swap never FLIPs (no F6 history
effect); w is NO-EFFECT; every SITE cell's site swap took effect
(arm_identical False).

DECISION (frozen rule): depth-2 tree on 8 physics dials CV 0.730 vs
family-only 0.797; gain -0.067 (95% over 20 repeats -0.126 to -0.028) ->
FAMILY SELECTS. The physics-only tree collapses to "SITE". Physics+family
0.807.

HELD
- HOLD is site-carried (81/85 readable). The only HOLD CHANNEL cell is
  the M2 echo 4ab2ba01 (pay1).
- CHANNEL cells carry the bit on ONE payload component (pay1 x7, pay0 x3,
  pay3 x2). One cell (a02aa099) is COUNT-coded.
- All 6 MAJ CHANNEL cells share one physics point (dest all, decay 3,
  lat_base 4, pw 4, delta 4 = the M3 physics) and stay channel-carried at
  the late tick.
- The 12-cell pilot agrees on 10/12.

SURPRISES
1 At a fixed physics point the carrier is NOT fixed (post hoc): one RELAY
  physics+env point holds SITE 4 / CHANNEL 4 / JOINT 4. Across non-HOLD
  readable cells (n=39, 11 physics points) no model beats ~0.40 (family
  .384, tree .398, logistic .403, majority .285). "Family selects" holds
  only because HOLD is uniform. Inside RELAY/MAJ the evolved program and
  its timing decide the carrier.
2 JOINT is a per-trial PHASE MIXTURE, not a joint code: in 14/14 JOINT
  cells site_acc + chan_acc = 1.00 (mean .999). At the late tick 5 JOINT ->
  SITE and 9 -> ELSEWHERE; the CHANNEL cells 31cd2a8a, 4316f167 and
  ed16c553 -> SITE. Reading: a channel -> site-latch handoff whose transit
  time varies. The 2 pilot disagreements follow (the mid tick is up to 1
  later: 62a7fff9 CHANNEL->SITE, c16d5231 CHANNEL->JOINT). This fits the
  4781b0a1 reframing.
3 ELSEWHERE is mostly the absolute FLIP threshold biting weak champions
  (3/5 are HOLD with site acc .31-.37 ~ 1 - normal, hi99 just over .40; two
  read SITE late). 2 RELAY cells (42716814, d3c0d182) are CHANCE on every
  arm.
4 25% UNREADABLE (normal lo99 < .60), incl. 20/50 RELAY.

PREDICTIONS: P1 held for HOLD, but RELAY was not channel-dominant. P2
untestable (decay > 0 and lat_base 4 appear almost only at the M3 point).
P3 held (partly degenerate). P4 held (25% UNREADABLE).

IMPLICATION FOR C2: in RELAY/MAJ a single-tick carrier class is a PHASE
reading. Map the unloaded carrier over every tick of the interval, per
champion, before reading any load boundary. For HOLD a single-tick SITE
reading is safe.

PROPOSED: T-CT-2 carrier trajectory (a site/channel swap at every tick
t0..ro for the 39 readable RELAY/MAJ cells; handoff time per champion);
T-CT-3 a per-trial JOINT mixture test (does the split follow latency
jitter or dup?); T-CT-4 why the MAJ pw4/dest-all/lat4 point is always
channel-carried (physics sweep + re-evolution); T-CT-5 a relative FLIP
threshold (acc <= 1 - normal + margin) to recover weak cells (needs an
instrument ruling first).
