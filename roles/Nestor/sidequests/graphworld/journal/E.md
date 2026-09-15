# Lane E journal (Nestor-E[m1-f333105f], SELECTION)

## 2026-09-14 iteration 1 -- E3 engine-as-organism, E1 QD core

E3 (PASS). Stock FalkorDB 4.20.4 on private 6394, 8 container restarts over
load-time genes, 6 runtime genes, 16 Cypher variants over a seeded
25k-node/160k-edge corpus. The gate killed 16/16 cheat variants, 0/112 honest,
and 3/3 cheat runtime genes (RESULTSET_SIZE=100 caught only by the one query
with >100 rows: a corpus without a big result set would have let truncation
live). Rewrites carry all the gain: Q6 point-lookup UNWIND -> range scan 29-38x,
Q2 anchor-first ~2x, in 8/8 engines. CACHE_SIZE / OMP_THREAD_COUNT: 86-96 ms
totals against a 4.6% A/A pair, n=1 each -> INDETERMINATE, no gain claimed.
CACHE_SIZE, THREAD_COUNT, OMP_THREAD_COUNT are load-time only (restart ~6 s).
Fitness was separable, so it was censused, not evolved.

E1 (see receipt). Lua one-EVALSHA-per-batch archive: 262k offspring/s with 4
workers on the stub NK world, insert p50 2.9 ms per 1024. The first full run
showed the end-state exactness instrument BLIND at 300x1024: the racy
client-side cheat also scored 0 mismatched cells (the saturated grid heals
lost elites). Liar audit held: 873/873 lies present caught, 0 false flags.
Amended on the bus before re-running: 10 short runs (20x256). Result PASS:
racy4 detected 10/10 (7-46 cells lost), lua4 0/10. Lesson: an end-state
check on a converging search is only a detector early; E2 must use
event-level lineage, not the final archive.

## 2026-09-14 iteration 2 -- E2 branch points (INDETERMINATE)

Lineage from Lua-XADDed win events (one call does the win and the event).
300x1024, 3 reps, k=50: honest 140/141/162 branch points, ~0.33-0.43M per
CPU-h (CPU ~1.4 s/run worker+Redis, stub world). Filler cheat 0/0/0, but that
kill is BY CONSTRUCTION (its false parent edges fail hamming<=8), so it proves
the descent check reads edges, not that BPs mean anything. The real control
was the null world: transfer 60.5% on the 25%-redrawn world vs 6.7% on a fully
redrawn one; the posted bar was <=5%, so the transfer half is INDETERMINATE
as written. Likely cause (untested): z is taken against random genomes of
popcount ~32 while elites live in popcount-extreme cells; next = per-cell
random baseline. Null-world transfer by rep: k=10 5.4/5.0/2.5%, k=50
5.0/8.7/6.6%, k=100 1.0/3.6/12.4% -> 3 reps cannot pin a 5% bar; the rule was
set without an attainable-range check.
Analysis refactor (descendant DFS) proven equal to the ancestor-tuple version
on one recorded stream before the full run (a re-run could not prove it:
ZRANDMEMBER sampling is unseeded).

## 2026-09-14 iteration 3 -- E2b branch points vs a 20-world null (PASS)

Pre-check first (5 reps): a per-cell (popcount-matched) baseline moved the
single-null transfer only 5.3-7.0% -> 4.6-6.2%, so my E2 explanation was mostly
wrong; one null table is one draw for clustered lineages. Bar re-posted
against 20 null worlds. Full run (rows ab025ba26, receipt filed AFTER the push
this time): honest 182/164/201 BPs, transfer 70-81% vs null max 3.4-8.0%, 3/3.
New non-trivial cheat FAKEFIT (real descent, fitness shuffled per batch): 541-570
survivors but transfer 2.5/6.5/3.0%; it beat the null max ONCE (rep 1, 6.5% vs
4.7%). The rule allowed 1/3 so PASS stands, but the transfer half is thin at a
single max-of-20: next time compare against a per-condition null quantile with
more worlds, or require the honest margin as a ratio. Filler 0 edges, 0 BPs.
Board: ~0.5M excess BPs per CPU-h on the stub world (clock is ~15.6 ms coarse).

## 2026-09-14 iteration 4 -- E4 QD in B's batched Encounter (FAIL)

MAP-Elites (E1 archive) over open-loop action tensors in B's NpEncounter, worlds
gen_seed 1-5, 8 seeds/genome, 100 gens x 256. Oracle held everywhere: honest
elites 0/32 failing in 5/5 worlds (trace hash + final charge vs wforge), skip_lin
elites 32/32 failing in 5/5. Positive control FAILED: QD best > random search at
equal evaluations in 0/5 (ties 1728/276/1224, losses 1287<1890, 4675<4690).
Status FAIL as posted. Likely: "best vs random" was a weak QD positive (QD spends
its budget over 118-219 cells), and exact ties look like an open-loop ceiling.
Cheat detail worth keeping: skip_lin had 0 charge mismatches in 3/5 worlds and
HIGHER fitness in 2 (1818 vs 1287, 408 vs 276), so only the trace hash catches it.
Smoke found archive.order_key assumed 8-byte genomes; fixed (row rank), tests
green. np eval 22-46k episodes/s vs wforge 3-8k (B's world; no board claimed).

CORRECTION after filing: lane B had posted a note TO E before my record run
(exploit: unaffordable actions are free and still write; NbEncounter 46-70M
steps/s; trace equality misses ~20% of unaffordable-write differences). I read
only the 300-char bus summaries and missed it. E4's elites were not preserved,
so their exploit share is unknown and "honest 0/32" does not cover that
semantic. E4b adopts all three.

## 2026-09-14 iteration 5 -- E4b QD in B's Encounter vs a random-filled archive (PASS)

B's suggestions adopted: NbEncounter search (fitness == NpEncounter on a check
batch in 5/5 worlds), unpaid-tick audit, fix_unaffordable cheat. 5 worlds x 3
run seeds, 100x256. Positive held: QD coverage > random-filled archive 5/5 (e.g.
w4 224-231 vs 136-142 cells) and qd_score 5/5, every seed. Best fitness TIED
random in every world (one seed 4666 < 4690): E4's "best vs random" was measuring
a ceiling, not QD. Oracle: honest 0/32 in 5/5, skip_lin 32/32 in 5/5. Missed:
exploit prediction (elites with unpaid>0 more often than random in >=3/5) came
out 2/5 by share (random genomes are already 62-97% unpaid), 3/5 by mean ticks.
fix_unaffordable detection: failing elites == elites that exercised the
semantic in w1-w3, but 15/18 in w4 and 11/24 (46%) in w5 (T=256, delay 4) --
below B's ~80% floor; late unpaid writes after death are invisible to the hash.
Receipt filed after push; a first land attempt stopped because the journal edit
was uncommitted (rebase refused), and no receipt went out.

## 2026-09-14 iteration 6 -- E5 closed-loop TT brains in B's world (FAIL)

First three-lane piece: lane C's TTPolicy (r=3, A=8, + an 8xW action codebook)
as the genome, lane B's NpEncounter as the world, lane E's archive and a
population-batched float32 forward. 5 worlds, 60 gens x 128 (7,680 genomes).
Both oracles held everywhere: world (recorded actions replayed in wforge, hash +
charge) honest 0/16 failing and skip_lin 16/16 caught in 5/5; brain (C's ref64
argmax on recorded obs) 0 mismatches over 1,873-4,095 clear rows per world, and
the skip-odd-cores forward caught 16/16 in 5/5. Science FAILED: closed-loop best
> E4b open-loop best in 0/5 (586<1890, 1164<1728, 156<276, 1092<1224, tie 4690),
although brains filled more cells (353-472 vs 118-231). Caveat posted before the
run: 3.3x fewer genomes than E4b, so this does not show closed loop is worse,
only that it did not win at this budget. skip_lin again had 0 charge mismatches
in 3/5 worlds: only the trace hash sees it.

Next / steal: equal-budget E5b (25,600 genomes) before any claim about closed vs
open loop; C2's plastic rank as adapt() inside an episode.

## 2026-09-14 iteration 7 -- E5b closed-loop at equal budget (FAIL, as predicted)

Same code (--exp), 200 gens x 128 = 25,600 genomes per world (E4b's budget; one
seed vs E4b's median of 3). Oracles clean again in 5/5 (world honest 0/16,
skip_lin 16/16; brain 0 mismatched over 2,214-4,095 clear rows, skip-odd 16/16).
Budget moved the closed-loop best in 4/5 (586->942, 1164->1576, 156->228,
1092->1151; w5 4690 tie) but it still beat open loop 0/5; prediction "<2/5"
held. So E5's loss was not only budget. Untested candidates: r=3 TT over 36 hex
digits is a poor function class for these obs (corruption + delay in w1), the
8-entry codebook caps actions, or open loop simply suffices in fixed-seed worlds.
B1t (lane B) explained E4b w5's fix_unaffordable misses from my saved elites:
91/91 were unpaid writes landing after episode end.

## 2026-09-14 iteration 8 -- E6 held-out seeds, open vs closed loop (FAIL)

Pre-check first (random genomes): w2 seed-independent, w5 other seeds all-zero,
seed sets differ in difficulty, so compare conditions on the SAME held-out seeds
and never as ratios; eligible w1/w3/w4 fixed before the run. Both conditions
25,600 genomes on 8 train seeds, top-16 scored on 64 held-out seeds. Refuted,
the other way round: closed-loop generalised WORSE in 3/3 eligible (held-out
per seed 2.0 vs 45.9 in w1, 53.4 vs 90.3 in w3, 57.1 vs 87.3 in w4) although it
matched or beat open loop on the train seeds in w3/w4. TT brains overfit the
8 seeds more than fixed action sequences did. Leak control 3/3 (e.g. w1 237 vs
161 on the leaked seeds); oracle clean 5/5, skip_lin 16/16.
Eligibility miss: the random-genome pre-check called w2 seed-independent, but
w2 elites score 162 on train vs 196 held-out -- elites reach seed-dependent
states random genomes never do. A pre-check on random genomes can under-state
seed dependence; next time pre-check on a short QD run's elites.

## 2026-09-14 iteration 9 -- E6b 32 train seeds (INDETERMINATE)

E6 again with 32 train seeds. Primary held 3/3: closed-loop held-out rose
2.0->16.6 (w1), 53.4->78.1 (w3), 57.1->62.9 (w4) -- more seeds do cut the
overfit -- but it still trails open loop 0/3 (16.6<44.7, 78.1<95.4, 62.9<89.3).
Leak control failed its bar: 2/3, with w3 60.56 vs 60.70 (a tie) and w4 99.04 vs
98.71 (a hair). Only w1 shows a real leak effect (264 vs 146). So at 25,600
genomes the leak cannot demonstrate overfitting in w3/w4 and, by the posted rule,
E6b is INDETERMINATE even though its primary is clean. Lesson: E6 passed the same
control only narrowly outside w1; the held-out instrument is weak in w3/w4.
Lane B's B5: closed-loop rollout wall is 80-89% brain forward, 9-17% world.
Lane C's C4 families landed; E7 claimed.

## 2026-09-14 iteration 10 -- E7 lane C's C4 families under the held-out test (PASS, narrow)

Four C4 families (bytes from .nbytes) + E's codebook, E6 setup, w4/w1/w3.
Oracles clean in 12/12 family x world (world honest 0/16, skip_lin 16/16;
brain 0 mismatched clear rows, cheat=True 16/16). Bar "best held-out family is
linear or lut_top in >=2/3" met 2/3 -- but ONLY via linear (192-320 bytes): best
in w1 (38.8) and w3 (104.4); w4 went to tt_feat (87.7). lut_top (2.5-4.6 KB) was
at or near the bottom everywhere (0.1 in w1), so lumping it with linear as "small"
flattered the bar. Spearman(bytes, held-out) only -0.4/-0.2/-0.2. Linear beat
E6's open loop in w3 (104.4 vs 90.3); tt_feat tied it in w4 (87.7 vs 87.3).
Noise warning: tt_digits is E6's TT re-run with a different RNG and moved 53.4 ->
87.7 (w3), 57.1 -> 51.1 (w4), 2.0 -> 6.0 (w1): single-run top-16 held-out means
are noisy, so the family ranking needs repeats before anyone leans on it.

## 2026-09-14 iteration 11 -- E7b C4 families x 3 run seeds (PASS, inside the noise)

36 runs (4 families x w4/w1/w3 x run seeds 0-2), oracles clean in all 36.
Linear had the best MEDIAN held-out in 3/3 (w4 83.2, w1 29.7, w3 98.8), so the
posted bar passed. But its lead over the runner-up is inside the run-to-run range
in 3/3 worlds (w4 gap 2.0 vs range 31.0; w1 19.3 vs 23.6; w3 7.0 vs 21.8) -- I
predicted that for >=1 world and got it everywhere. tt_digits is the noisiest
(w3 17.5 .. 86.8); lut_top is reliably poor. What survives: linear is never worse
than second and is the only family that holds up in w1 (obs corruption + delay).
What doesn't: any claim that linear is separated from tt_feat/tt_digits.
B6 (lane B) fused closed-loop rollout passed meanwhile; next E work adopts it.

## 2026-09-14 iteration 12 -- E3b FalkorDB load genes, repeated (PASS, prediction missed)

While waiting on B6/C6: 6 genes x 5 round-robin restarts (30 containers), E3's
reference queries. Null held (default_b median 83.84 not < default_a min 83.13);
gate killed both cheat rewrites and held on 30/30 restarts. My "0 winners"
prediction missed on the letter of the rule: omp1 median 82.72 < 83.13. That is
a 0.5% margin with omp1's own restarts spanning 81.55-85.26, overlapping
default_a's 83.13-84.67; every gene's median is within 2% of default_a's min.
Honest reading: E3's load-time knobs are worth <=~1% on this corpus; the "median
< min" rule is loose enough that a 0.5% shift passes it. E3 stays: rewrites are
the only big lever.
C6 (lane C) audited B6 exact off-distribution; E8 (seed scaling on B6) running.

## 2026-09-14 iteration 13 -- E8 seed scaling on lane B's fused rollout (PASS 2/3; the E5/E6 story turns)

Closed-loop tt_digits via B6 (exact per B6 + C6) vs open-loop E4b QD, 102,400
genomes each, train seeds N = 8/32/128, 2 run seeds, w4/w1/w3, top-16 on E6's 64
held-out seeds; oracles clean on all 18 closed cells (world 0/16, skip_lin 16/16;
brain 0 mismatched rows, skip-odd 16/16). Closed held-out median N=8 -> N=128:
w4 87.4 -> 95.9 (gain 8.5 > noise 3.8), w3 68.8 -> 101.7 (32.9 > 18.4), w1 54.3 ->
63.9 (9.7 < noise 30.6: its two N=8 runs were 39.0 and 69.6). Primary 2/3 ->
PASS; my "3/3" prediction missed. My other prediction was WRONG: at N=128 closed
loop is not behind open loop -- it leads in w4 (95.9 vs 93.5) and w1 (63.9 vs 58.6)
and ties w3 (101.7 vs 102.2). So E5/E5b/E6's "closed loop loses and overfits" was
largely a few-seed artifact: E6/E6b trained on 8/32 seeds at a quarter of this
budget. Two run seeds per cell only; train scores are over different seed sets per
N and are not comparable across N (only held-out is).

## 2026-09-14 iteration 14 -- E9 family ranking, 8 run seeds on lane B's B6b (PASS 3/3; prediction wrong)

linear / tt_feat / tt_digits on B6b's fused rollout (exact per B6b + C6b), E7
setup, w4/w1/w3, 8 run seeds each (72 runs), oracles clean on run seed 0 of all
9 family x world cells (one brain-cheat cell 15/16, bar >=14). Linear beat the
runner-up (tt_feat in every world) by one-sided Mann-Whitney U: w4 p=0.00008
(median 89.9 vs 79.2), w1 p=0.019 (35.5 vs 17.1), w3 p=0.041 (103.2 vs 91.6) ->
3/3, PASS. I predicted w1 only (FAIL); 8 seeds lifted E7b's inside-the-noise
ranking out of it. Ordering linear > tt_feat > tt_digits holds in all three
worlds (tt_feat > tt_digits p=0.0005 w4, 0.007 w3, 0.14 w1).
CAVEAT, disclosed: the bar was p<0.05 per world with no multiple-comparison
correction; at Bonferroni 0.0167 only w4 would hold (w1 0.019, w3 0.041 just
outside). The verdict stands as posted; the strong claim is w4.
Joint reading with E8: a 192-320 byte linear brain is the best closed-loop
genome here, and closed loop is competitive with open loop once trained on
enough seeds.

## 2026-09-14 iteration 15 -- E10 linear closed loop vs open loop at 128 seeds (PASS 2/3; last run of the session)

Linear brain (lane C C4 + E codebook) on lane B's B6b fused rollout vs open-loop
E4b QD, both trained on 128 seeds, 102,400 genomes each, 4 run seeds, w4/w1/w3,
top-16 on E6's 64 held-out seeds; oracles clean on run seed 0 (world 0/16,
skip_lin 16/16; brain 0 mismatched rows, cheat 15-16/16). Closed > open by
one-sided Mann-Whitney U: w4 p=0.014 (98.8 vs 94.0, all 4 closed above all 4
open), w3 p=0.029 (105.6 vs 102.7), w1 p=0.44 (61.4 vs 60.5; one linear run 47.7).
2/3 -> PASS. Prediction (w4 + w1, not w3) wrong both ways. At Bonferroni 0.0167
only w4 holds. Combined with E8/E9: trained on enough seeds, a 192-320 byte linear
closed-loop brain beats fixed action sequences on unseen seeds in 2 of 3 worlds
and never loses clearly.
Loop stopped by the operator after this run.

Next / steal: closed-loop needs more training seeds or a regulariser before any
generalisation claim; C3's representation ecology (dense/CP/Tucker/TT/bitset)
is the natural next genome comparison. E4b = archive-level positive (QD coverage/qd_score vs the same
number of random genomes inserted into an archive), closed-loop genomes (C's TT
policy on obs), and B's numba form for eval. B's batched Encounter to replace the NK stub; C1's TT cores as
the genome for E1; E2 branch points with a random-filler control; E3 with
repeated restarts per load gene (n>=5) to beat the 4.6% A/A floor.

# ROUND 2 -- Nestor-E[m1-4b8ee0f4], cohort WATCHMAKERS (SWARM_R2 s3 E)

## 2026-09-14 r2 iteration 1 -- E-T1 transfer harness (validation FAIL on the cheat clause) + B's qd_ledger fix

Harness edb064317 primordial/cohorts/e/transfer.py; rows E-T1-transfer-harness (123).
A 1-seed dev smoke killed v0 before any record run: tiled grafts lose diversity (random graft
142 vs scratch 151) and best-so-far train fitness hits its ceiling at gen 1. v1 uses a common
filler + K=16 slots and a held-out checkpoint AUC. Record run (linear, w2->w4, w25->w1, w17->w3,
8 run seeds, 200x128): control self_graft detected 3/3 (p=0.004 each); integrity 24/24;
oracles clean 3/3. Cheat clause broken: rand_graft p=0.023 in w3. That arm is
distribution-equal to scratch, so this is a real false alarm at n=8. Posted verdict FAIL.
Post hoc, report-only: graft beats both cheats only in w4 (p=0.004); in w1 and w3 it does not beat rand_graft.
Lesson for E-T1b: acceleration has to be graft minus cheat (paired), not graft minus scratch; more run seeds.
Also fixed qd_ledger check (front over baselines only) on lane B's ask; the regression test fails on the old code.
E-T2: Transformer family (9007d558c), 680 params, 2744 B on w4; record run on w4 running.

## 2026-09-14 r2 iteration 2 -- E-T2 PASS, asks from B and D landed, E-T1b running

E-T2 (code c11aea5a3, rows 67bc4a5b7, receipt PASS): a 1-block Transformer (680 params, 2744 B)
through E7's numpy rollout, 25,600 genomes per run seed, 8 seeds at 166-206 s each. Oracles clean on
every seed: world 0/16, skip_lin 16/16, brain 0/4096. The skip-odd cheat caught 15/16 on seed 0
(bar >=14) but 13/16 on seeds 2 and 6. held64 median 95.56 (IQR 8.1) vs E9 linear 89.94 at 312 B
(report-only). The E-T2 hypothesis sha 9007d558c was orphaned by a rebase; corrected on the bus.
B ask (skip-odd blind on int2 brains): cohorts/e/oracles.py adds ablate_top (feature chosen on
half the rows, scored on the other half), shift_action (oracle floor) and an input_invariant flag.
Tested only on a planted brain; its power on B's real elites is unmeasured.
D ask: LuaArchive(sampler_seed=) seeded, atomic Lua sampler (33038855e).
Git: a rebase while E-T2's RowWriter held its rows file wedged (untracked block); fixed by
dropping the rows picks from the rebase todo; no rows lost. Push only fast-forward while a writer is live.

## 2026-09-14 r2 iteration 3 -- E-T1b PASS: the transfer harness read against its cheats

Rows 425083145, receipt PASS; posted before the run. Same harness (4c69b55ef), 16 run seeds per world.
Seeds 0-7 re-run bit-identical to E-T1 (120/120 rows). Planted self_graft beats both cheats in 3/3
worlds (p < 1e-4). rand_graft vs scratch no longer fires (p 0.83/0.15/0.32), so E-T1's w3 false alarm
was a small-n graft-minus-scratch artefact. Integrity 48/48, oracles clean 3/3.
Report-only: the w2->w4 linear graft beats both cheats (p_max 0.0003, +9.9/+8.4); w25->w1 and
w17->w3 do not. Told the conductor the clause B gate condition is met (E-T1 + E-T2 committed with
tests), recommending that clause B score graft against both cheats (Holm across worlds), not
graft against scratch.
Next: E-T3 asks as they come; an E-T2 fused kernel if B wants the Transformer in the QD loop at
E9 speed (numpy runs at ~180 s per 25,600 genomes).

## 2026-09-14 r2 epoch 2 close

EPOCH 2 posted: rows=243, receipts=2 (E-T2 PASS, E-T1b PASS), open_claims=none. C adopts the seeded
sampler and brain_oracle_cheats from C-R2-09 on. Correction: my note to B said the planted zero-weight
test "reproduced" B's blind skip-odd cheat; B's anomaly 1789418707943-0 already rules zero weights
out as B's mechanism (blind elites' odd zero-weight fraction .31-.34, inside the run's .19-.44).
Docstring and test comment fixed; the tool measures cheat power and makes no claim about why.
Liveness flagged E STALE once at ~17:03 (transcript age 618 s during a background run): beat every
<10 min while waiting.

## 2026-09-14 r2 QUIESCE -- test launch 1 over (EPOCH 3 final)

Conductor QUIESCE at 17:33. No task in hand; nothing new started. EPOCH 3 (final): rows=0 receipts=0,
open_claims=none. Round 2 totals for E: 3 receipts (E-T1 FAIL, E-T2 PASS, E-T1b PASS), 372 rows, plus
3 asks landed (B ledger fix, D seeded sampler, B cheat-power oracle). Carry forward: clause B reads
graft vs both cheats; E-T2 has no fused kernel; round 1 LuaArchive runs are not seed-replayable. Loop stopped.

# ROUND 4 -- Nestor-E[m1-2adb547f], cohort WATCHMAKERS (SWARM_R4 s5 E)

## 2026-09-15 r4 iteration 1 -- E-R4-1 clause B transfer into the survivor, predicate posted, record job running

Boot: ff to the sidequest tip, suite 209 passed rc 0, worker E up. One SURVIVED cell (w13 train128); only
w14 and w20 share its linear layout among the screened w1..w37, so the Holm family is 2 pairs into w13.
transfer.run_pair split (pair_base/run_seed/summarize) for per-seed F9 checkpoints; the split reproduces
committed E-T1b rows field for field. New job cohorts/e/r4_transfer.py (guard from worlds_r4.json, M2 budget
800x128 on TRAIN128, 16 run seeds, report-only check_b row) + tests, code 407b210ef.
Dev smoke (1 seed, 20 gens): 9.3 CPU-s, oracles clean, integrity true. Record job submitted, ttl 20000 CPU-s.

## 2026-09-15 r4 epoch 1 close

F14 stop at the EPOCH 1 boundary paused E-R4-1 cleanly after 9/32 run seeds (45 rows, 2910 CPU-s, ~323
CPU-s per seed -> ~10.3k total, inside ttl 20000); segment 1 queued (f82198bface6). Answered C/A on the
graphworld_b2 interface ask: not built without an operator ruling. No receipts yet.

## 2026-09-15 r4 QUIESCE -- E-R4-1 done: judge PASS x2, filed INDETERMINATE (a cheat failed its own null)

Job 10a0c1f7f05a ok (2 segments, 10.2k CPU-s, 163 rows at 4c29a41f8). check-b: w14->w13 PASS (p_max .023), w20->w13 PASS
(.0068), gates clean, planted self_graft p 1.5e-5. Being-fooled check: rand_graft (distribution-equal to scratch; init is
i.i.d. per row) lost to scratch on 13/16 seeds (p .0012), so graft-minus-rand is inflated. Scratch as the cheat: only w20->w13
survives Holm (.031). Graft vs scratch is ~0 AUC, final held64 below scratch; zero-shot is the robust part (132/152 vs 67).
Receipt INDETERMINATE. Next: rand vs scratch on seeds 16-63 at train128 + stream-swapped variant, before any clause B claim.
Worker stopped; loop stopped; ff to push lock 898900b4e.

## 2026-09-15 operator 15/16 -- reader, BASELINE_N, B2 adapter

R15-1 reader landed a70fcd841: primordial/metric/readout.py (top1_train) used by M2 baseline + candidates; check_r4
refuses READOUT_MISMATCH. Verified: w13 t128 reread == D-R4-4 top1 8/8, median 189.53125 (rows ff082667f).
R16 BASELINE_N: n_runs < 32 / families < 4 (3dd777386), then per-family < 8 or absent n_per_family (A caught the gap:
29+1+1+1 passed; my own note had waved it off as the screen's job). Lesson: every refusal condition in the ruling goes
in the judge, not in the writer. R15-2 B2 adapter de91fbd52: prey-controlled graphworld_b2 (obs 8 x uint16, a % 8,
charge); record oracles O1 gb/cy == ref 64/64, O2 skip_mutation caught 32/32 moving specs, O3 forager 440 CI [432,444]
> blind max 356.75. Suite 325 passed. Next: G screens B2 and re-screens 32x4 under the reader; E on asks.

# ROUND 5 P-BUILD -- Nestor-E[m1-2adb547f] (SWARM_R5 s3 E-R5-1..3), started 06:13, green at ~06:34

E-R5-1 hardened Clause B control clauseB_ctrl_v2_featperm (preregistered 1789467311525-0 before code; 3ba828c43):
sham = donor linear W row-permuted along the observation-feature axis by a seeded derangement (values, column
multisets, zeros, bias, codebook kept); check-b v2 requires graft > scratch AND > sham. Smoke validation at w13
train128 (gens 50, batch 64, seeds 100..107): planted positive PASS (+9.42 / +4.84, p .0039 each), planted negative
FAIL; sham - scratch +4.58 on the positive (harder than scratch, the E-R4-1 defect is gone). A accepted (gate 12).
Live pair at M2 budget ~20 min for 16 seeds -> PRODUCTION_CANDIDATE under O6 in the pilot.
E-R5-2 GPU queue + arbiter (nv/gpuq.py): F's admit(kind=gpu) + refuse, cap min(gpu_budget_s, 600), O5 lease for the
whole child, 19 s6 fields, timeout -> TIMEOUT event + candidate. First smoke crashed: child rows had no RowWriter
status and my test writer accepted anything (a test aimed beside the claim) -- fixed, the test writer enforces
rows.STATUSES. E-R5-3 wiring (nv/r5_harness.py): 1-cell smokes all exact, lease held, rows VALID. GPU-3 resident fp16
path is not in the P MVP -> PRODUCTION_CANDIDATE stub. Workers stopped for the P-PILOT cohort session.

# ROUND 5 P-PILOT -- Nestor-E[m1-cdc0934f] (prompts_r5/E.md), boot T+19

Iteration 1 (T+19..T+40). Code gap: transfer_v2 had no live-pair job -> live_job (O1 donor = o1_donors()[0], refuses any
other donor, seen seeds, non-SURVIVED recipient; test) at 2072511b0 (ops.push rebased my 288ae11a6; predicate cites the old sha).
Clause B w14->w13 seeds 16..31 (predicate 1789471264221-0): STAGE_BUDGET_REFUSAL (wall 1440 > 900, CPU 3200 > 1200) ->
PRODUCTION_CANDIDATE 1789471324763-0 with measured cost; not run, not trimmed. GPU queue: 6 jobs, all exact, lease held,
max wall 22 s. GPU-1 Warp beats t8 numba only at 4096/16384; loses at 65536 (h2d 34 ms) -> anomaly to D. GPU-2 at 8192:
B6 t8 beats CUDA graph kT 5.9x (linear) / 4.1x (tt_digits); B6 stops envs at done, torch steps all T. GPU-3 not run.
Missing machine checks: (1) admission stubs carry measured_cost null and no code files the measured cost (filed by hand);
(2) nothing ties a predicate's cited code sha to the pushed sha after a push rebase.

Iteration 2 (T+47). ff to 3a6beef19 for D (A ask; op 20 PILOT cpu_budget_s 2400); worker restarted on new CEILINGS.
Clause B still refused under op 20 (wall 1440 > 900, CPU 3200 > 2400): candidate stands, not resubmitted.
D-R5-2 REFUTED my 65536 "reversal": warm h2d 5.13 ms, cold 5.59 ms, kernel + copy 8.43 < numba 10.36; my 34 ms copy
did not reproduce (cause unidentified). Lesson: bench_cell's h2d is ONE cold call while the kernel is a median of reps;
I published a ratio of unlike estimators. Pushed D's arbiter rows (0deee846c) from this worktree.
