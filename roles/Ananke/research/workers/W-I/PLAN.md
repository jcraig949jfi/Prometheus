# W-I PLAN  carrier trajectories: how causally used information moves through carriers

Written 2026-09-28 BEFORE any main run. Frozen: specimen set, tick grid,
verdict and label rules, motif criteria, robustness test. Only a smoke
test (bit-identity of the batched runner vs lens.run, and timing) was run
before this file; it produced no verdicts (see LOG.md A1).
Worker W-I, namespace 0x5EE. Rules: handoffs/COMMON_RULES.md + _ARC3.md.
Principal interpretation files (SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD,
ARC3_PRIORITIES, other REPORT.md) NOT read before this plan. Raw evidence
read: W-F census_table.csv / census_s0.jsonl head / W-F PLAN.md, W-C
wc_probe.py and x12.json head, lens.py, engine.py, envs.py, c1b.ticks.

## Question
For a representative set of C1 champions, track at EVERY tick from cue
onset to readout (a) the PHYSICAL difference class between single-cue
twins and (b) the READER-side carrier verdict from mirror-pair swaps.
Find recurring trajectory motifs; test whether trajectory class predicts
robustness.

## Specimens (33 C1 evolve champions; genome = result.champion)
PANEL (matched physics, digest d9ccb6a71d986501: ring 144, sample, C1 P2
D2 L16, cap 2, loss .1, lat_base 1, jitter 1, plastic_route, wimm) = all 18
RELAY cells with this physics in the W-F census that were READABLE there:
 SITE: 62a7fff9 35c721fd 72dd71d8 bbef66a1 e2afff1c e9196cae cd5b6fd6
 CHANNEL: 31cd2a8a 4316f167 a02aa099 bf82cb29 dcd404a9 ed16c553
 JOINT: 2dccdaa5 8c37f32e c16d5231 e06701a5 78f3b0ec
 + same physics, other family: HOLD 4ab2ba01 (M2), MAJ 4781b0a1.
 Justification: the only place in C1 where physics is held fixed while
 the census carrier class varies (SITE/CHANNEL/JOINT); it lets trajectory
 class be compared with robustness without the physics confound.
SPAN (span physics x family x census class): HOLD 85ca202e (global,
 content code), ab089e45 (global, presence code per W-C x12), 7b7b025e
 (global, mixed presence/content), 13127335 (global async), 00c5d3b6
 (torus all async), 1c0a1bc7 (torus all, rules 4), 65d840a8 (ring rules
 4, loss .6), 0187372b (torus, census ELSEWHERE); MAJ 0a23398f (M3, ring
 all, CHANNEL), 613162a3 (global SITE); RELAY 63d17a90 (torus all SITE),
 369f5a5b (smallworld JOINT), 42716814 (global ELSEWHERE).
Specimens with normal lo99 < 0.60 on my seeds are UNREADABLE: their
physical axis is reported but they get no reader labels, motifs or
robustness class.

## Seeds
Reader axis and robustness: assays.world_seeds(0x5EE, 64) (robustness:
0x5EE ^ 0x3). Twins: world_seeds(0x5EE ^ 0x7, 64). 64 worlds = 32 pairs,
99% pair bootstrap (lens.ci / swap_verdict).

## Tick grid
Offsets o relative to each trial's cue onset t0: o = -1 (pre-cue F6
control) and every o = 0 .. ro-1-t0 (ro = readout tick; ro-1 is the last
tick at which a between-tick swap can act on this readout). The swap is
applied after tick t0+o in EVERY trial (W-F convention); accuracy over
scored trials 1..T-1 (trial 0 has no o=-1 tick; excluded for all arms).
Offsets o < cue_len-1 are the CUE PHASE (cue still being written by the
schedule); they are reported but excluded from motif strings. The
INTERVAL is o = cue_len-1 .. ro-1-t0.
Implementation: traj.run_arms batches arms as independent 64-world blocks
of one World; selfcheck() must show bit-identical traces to lens.run
(done in smoke for normal, site_all, channel_all on 2 specimens).

## Axis (b) reader verdicts
Arms at every offset: site_all, channel_all, joint (site+channel, F1:
sanity only), S, inbox, channel_content, channel_count, and Kp / r / w / E
where the physics can change them. Verdict per arm = lens.swap_verdict
(FLIP hi99<.40; NO-EFFECT lo99 >= normal lo99-.05; CHANCE otherwise), plus
arm_identical (F4) against the normal arm.
Per-trial MIXTURE statistic phi: over (world, scored trial) with normal
outcome correct, phi = correlation between "site_all swap wrong" and
"channel_all swap wrong".
Reader label per offset (frozen):
 D  site_all FLIP and channel_all FLIP
 S  site_all FLIP only
 C  channel_all FLIP only
 M  neither FLIPs, joint FLIPs, |site_acc+chan_acc-1| <= 0.15, phi <= -0.3
    (per-trial mixture: a handoff caught mid-transit, F5')
 J  neither FLIPs, joint FLIPs, not M (split / joint code)
 E  site_all, channel_all and joint all NO-EFFECT (bit not in these arrays)
 X  otherwise (disrupted; no single array sufficient)
Always reported next to the label: site_acc, chan_acc, their sum, phi,
normal lo99, and which sub-arm FLIPs (S / inbox / content / count / Kp /
r / w).

## Axis (a) physical difference class (single-cue twins)
Twin trials k = 3, 5, 7 (batched), worlds identical except that trial k's
cue sign is negated. After every tick from t0-1 to ro, per pair: does it
differ in S, inbox (Acc_sum/cnt), Kp, E, r, w; in-flight COUNT (Mcnt:
presence/count; "N"); in-flight PAYLOAD with equal count ("V"); who FIRES
(last_emit differs; "F"); emitted payload differs when both fire ("P");
emitted channel differs ("H"). Spatial: #sites with S difference, mean
distance of those sites from the (first) sensor and from the actuator;
#firing-difference sites and whether the source fires differently.
Physical label per offset = the codes whose pair fraction (mean over the 3
twin trials) >= 0.5, e.g. "sNF".
The physical axis is NOT inferred from the reader register and vice versa.

## Motifs (criteria frozen)
Reader string = interval labels, run-length compressed.
 R1 SITE-ONLY RETENTION: every interval label in {S, D}.
 R2 CHANNEL-ONLY DELAY: every interval label C.
 R3 STORE->CHANNEL: the compressed string restricted to {S, C} is S..C
    and ends in C (store, emit, carried in flight to readout).
 R4 CHANNEL->LATCH: restricted to {S, C} is C..S, ends in S.
 R5 REGENERATION: >= 2 alternations between S and C (S C S, C S C, ...).
 R6 MIXTURE BAND: >= 2 consecutive M offsets.
 R7 SPLIT BAND: >= 2 consecutive J offsets.
 R8 CARRIER GAP: >= 2 consecutive E or X offsets inside the interval
    after the first S/C/D label (no single array sufficient mid-way).
Physical motifs:
 P1 TRAVELLING WAVE (RELAY/MAJ only, src != act): Spearman(offset,
    mean S-diff distance from source) >= 0.7 over the interval AND its max
    >= 2 hops.
 P2 SOURCE-PRESENCE: some interval offset with F >= .5 and N >= .5 and
    emit-payload-diff P < .2 (who fires carries it, not the value).
 P3 PAYLOAD-VALUE: some interval offset with V >= .5 and N < .2.
 P4 SITE-ONLY PHYSICAL: no interval offset with N, V, F >= .5.
A motif is NAMED (claimed as recurring) only if it occurs in >= 3 READABLE
specimens spanning >= 2 distinct physics digests; otherwise it is reported
as "observed, not recurring" (the matched panel alone cannot make a motif
recur, by the 2-digest clause).

## Robustness test (frozen)
Conditions (genome fixed, env unchanged, seeds 0x5EE^0x3):
 base; loss+0.2 (cap 0.9); jitter+2 (lat_jitter); latency+2 (lat_base);
 distractor (Controls distractor_chan=0); size x2 (n_sites doubled; torus
 / smallworld: side := round(side*sqrt 2)).
Retention R = (acc_cond - 0.5) / (acc_base - 0.5).
Trajectory robustness class (from the reader axis): SITE-ONLY = >= 80% of
interval labels in {S, D} and no C or M; CHANNEL-USING = >= 1 C or M
label; OTHER otherwise.
Primary test on the matched PANEL RELAY cells only (18; physics fixed).
Predictions: H1 latency, H2 jitter, H3 loss: median R(SITE-ONLY) -
median R(CHANNEL-USING) >= 0.2. H4 distractor, H5 size: no direction
(reported two-sided).
Decision per H: SUPPORTED iff point difference >= 0.2 AND the 95%
bootstrap CI (10 000 resamples of specimens within class, seed 0) has
lower bound > 0; CONTRADICTED iff CI upper bound < 0; else NOT SUPPORTED.
Eligibility: each class needs >= 4 panel specimens, else INCONCLUSIVE
(too few). Delta (4/8/16) is a residual confound inside the panel;
reported with a within-delta breakdown. The all-specimen comparison is
reported as secondary (physics-confounded; not decisional).

## Predictions (before data)
Q1 Most panel CHANNEL/JOINT cells show a C->S (channel then latch at the
   reader) or S/C mixture band near the readout; census JOINT = M bands.
Q2 HOLD global cells: R1 site-only, physically "s" only (N/V/F absent).
Q3 M2 4ab2ba01: store->channel->store regeneration (R5) (census HANDOFF).
Q4 H1-H3 supported at ~55% confidence.

## Compute
GPU lease (lease.py, owner W-I) for main + robustness (~45 min, <2 GB).
If BUSY: QUEUE.md, CPU twin profiles meanwhile. Outputs: out/traj_<cell>.json
(full per-offset tables), out/traj_table.csv, out/robust.json, out/motifs.json.
