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

Iteration 3 (T+69). No asks to E; epoch 2 boundary passed; no E jobs queued (CPU or GPU). D-R5-2 rows landed as
269a55d84. Nothing new submitted: the only remaining E work (Clause B live pair, h2d-median fix in bench_cell) is
over the stage budget or not assigned. Holding for asks until NO_NEW_WORK (T+100).

A stand-down (T+~85). A had assigned E both missing machine checks at 07:25 (1789471470799-0); I never read it, because
`bus inbox | tail` cut it off (the 09-14 truncation lesson, repeated). A then stood E down before NO_NEW_WORK: nothing
built, and both were filed as PRODUCTION_CANDIDATE 1789474379663-0 (file_candidate, ~45 min) and -1 (sha by patch-id,
~70 min), hand-filed. Rule for me: read the inbox untruncated and grep for "E" in `to` before calling an iteration idle.

ROUND 5 FINAL (T+116). No verdicts, receipts or open claims. Clause B pair = PRODUCTION_CANDIDATE 1789471324763-0; tooling
PCs 1789474379663-0/-1; GPU-1/2 exact (Warp wins from (1024,4096], no reversal to 65536 after D-R5-2; B6 CPU beats CUDA graph
4-6x at 8192); 65536 reversal withdrawn. Worker and gpuq arbiter stopped at close; loop stopped.

# ROUND 6 -- Nestor-E[m1-77e78a19], cohort WATCHMAKERS (prompts_r6/E.md, SWARM_R6 s5 E), PRODUCTION stage

Iteration 1 (boot ~11:12, T+12). ff to 59f6047db, suite 437 passed rc 0 (sparse), worker E up. E-R6-1 Clause B live pair:
predicate E-R6-1-clauseB-live-w14-w13 pinned at 59f6047db (bus 1789485387411-0, prediction FAIL), job 6b88a2fff5d1
(PRODUCTION, wall 2400, cpu 6000, checkpointable) admitted, 8 threads, ~90 s/run seed. E-R6-2 B2 build: soup/b2/compiled.py
(numba prange, RefB2 tick + obs + skip_mutation; record -> adapter's sha256) + oracle/throughput job cohorts/e/r6_b2_compiled.py,
13 tests green; dev smoke oracle clean, ~16 us/episode linear vs RefB2 ~1.5 ms (smoke only, not quoted). E-R6-3: nv/dispatch_surface.py
builds E_R6_3_DISPATCH_SURFACE.md from committed E-R5-3 + D-R5-2 rows (32 cells, UNMEASURED list, no new timing).
B2 code not pushed yet: my RowWriter is live and origin is ahead, so ops.push would rebase under it; push after E-R6-1 ends.

Iteration 2 (~11:36, T+36). E-R6-1 done (1 segment, 1066 s, 3158 CPU-s, 50 rows @ 520260e4e): check_b v2 FAIL, gates clean --
graft-scratch -0.011 (p .506), graft-sham -0.018 (p .513), as predicted. Zero-shot: graft 138 and sham 146 vs scratch 80, so the
early lead is the donor's value structure, not its observation mapping; final held64 graft 169 < scratch 176. file_candidate on PC
1789471324763-0 filed. Receipt guard dry-run refuses sample_rule CANDIDATE_N (a Clause A minimum applied to this Clause B verdict,
16/1/16): not filed, not relabelled; ruling asked of A. Pushed B2 + dispatch code adf146468 (ops.push rc 0); predicate
E-R6-2-b2-compiled-rollout pinned there (bus 1789486511529-0), job 63b7c33725f8 queued, waiting for a CPU token.
A ruled (b) (D13, A's sample-rule defect in SWARM_R6): E-R6-1 is an OBSERVATION below the verdict sample rule, not a Clause B
verdict; no receipt; rows stay as UNRECEIPTED_OBSERVATION. New PC 1789486665691-0 "family-aware Clause B at CANDIDATE_N 32/4/8"
filed (est 2132 s / 6316 CPU-s for 32 runs + family plumbing). Lesson: dry-run the receipt guard on a synthetic receipt with the
planned sample BEFORE the predicate, not after the rows.

Iteration 3 (~11:47). E-R6-2 job 63b7c33725f8 ok (14 s wall, 141 rows @ 52c80ead2). Oracle EXACT: O1 96/96 (32 specs x random /
forager / linear: hash + charges + moving), O2 skip_mutation detected 32/32 moved specs and == RefB2's cheat 32/32, O3 64-episode
batch == per-episode RefB2. Throughput, planted spec, medians: RefB2 table 1.47 ms, RefB2 linear 14.0 ms; compiled table 6.9 us (t1),
linear 14.4 us (t1) / 6.7 us (t3; the worker child's NUMBA_NUM_THREADS was 3 although the token granted 8). b2_screen.pilot_cost:
~746 h (R5, table basis) -> 6.7 h single worker at t1 linear (3.1 h at t3); full screen 13.4 h. Caveat: G's R5 1.6 ms timed a TABLE
policy; the pilot evaluates linear genomes, whose RefB2 cost (14 ms) would have given ~6,500 h -- like-for-like speedup ~970x
(linear), ~212x (table). QD mutation/archive overhead still outside the estimate. t3 CPU-s/episode 20 us is process_time-coarse.
Receipt E-R6-2 PASS 1789486928415-0 (guard 10/10 OK, rows 78e65ac89); PC 1789468339986-0 re-costed by file_candidate. E-R6-3 posted
(1789486933439-0). Items 1-3 complete.

Iteration 4 (11:58, after EPOCH 1 boundary). Inbox untruncated: no asks to E (A's D13 ruling already applied). No job queued. Holding
for asks until NO_NEW_WORK 14:20; nothing new started (no item left in prompts_r6/E.md).

Iterations 5-6 (12:29, 13:00). No asks to E. A ruling 1789489756428-0 (F-R6-2 gap: the worker fingerprints only the job fn module,
not its imports): restart the F7 worker after editing any harness module. E check: worker E started 11:14, before soup/b2/compiled.py
existed, so E-R6-2 imported that module fresh (the pinned adf146468 code); no harness module edited since. Any later E job gets a worker
restart first. Note: the bus stream is pm:swarm (my 11:37 monitor watched a wrong key for A's reply; the inbox read covered it).

ROUND 6 FINAL (14:21, after NO_NEW_WORK). 1 receipt: E-R6-2 PASS 1789486928415-0 (EXACT; B2 pilot 746 h -> 6.7 h). Unreceipted rows:
E-R6-1 only (ruling b, OBSERVATION: check_b v2 FAIL gates clean, 16/1/16). E-R6-3 dispatch table committed (no rows). PCs filed:
1789471324763-0, 1789486665691-0 (new, family-aware Clause B 32/4/8), 1789468339986-0. Open claims none. Own errors: no guard dry-run
before E-R6-1's predicate; monitor on a wrong bus key; numba 3 threads vs token 8 unnoticed before E-R6-2. Final posted to A; worker
stopped; loop stopped.

# ROUND 7 R7-BUILD -- Nestor-E[m1-77e78a19] (prompts_bld_r7/E.md; SWARM_R7 s3 E-R7-1..3), 16:29 -> cap 18:35

Build 1 (16:29-16:52). ff dfdb22a8a. E-R7-1: transfer_v2 family axis (streams prefixed by F; None keeps r5/r6 streams),
check_b v2 pairs on (family, run seed) and refuses mixed axes; signflip exact n <= 20 else seeded MC (2^32 enumeration was
impossible at 32/4/8); tests 6 new + old pass. Predicates E-R7-1-val-positive/negative (32/4/8, CLAUSE_B sample block; the first
attempt was refused SAMPLE_RULE_MISMATCH by H's new post_predicate for lacking experiment_class -- nothing pinned). E-R7-2:
nv/r7_gpu_eval.py lockstep (32 runs, one evaluation per generation; G's per-run archives + streams untouched), oracle vs
numba every generation + elites vs G's baseline_run, lease projection guard, decision widened by A (best exact backend,
amendment posted before any timing row), G hook baseline_runs_lockstep; GPU dev smoke under a bus lease EXACT, 0.07x at
2 runs x 3 gens (not a verdict). E-R7-3: cohorts/e/r7_b2_overhead.py. r6 residue (stop flag + closed r6 clock) blocked
every admission; A cleared it (counted, D18). Code 935a31e5a; jobs queued: worker 438f1f7b5c00 / 72d76b705c37 / b11d7e858e31,
GPU 198efb6b735e (w13 t8) / 2f5abcb6bb9e (w13 t128).

Build 2 (16:53). E-R7-1 planted positive at 32/4/8: check_b v2 PASS, gates clean, graft-scratch +8.27, graft-sham +4.41 (MC p
5e-6 both), sham-scratch +3.86; 94.8 s. Both E-R7-2 cell jobs refused themselves projected_over_lease (no oracle, no timing): one
device batch per generation is ~15x SLOWER on the GPU than numba (t8: 0.749 vs 0.050 s at 32,768 episodes; t128: 12.98 vs 0.78 s
at 524,288). The gpuq child ran numba at 3 threads (inherited env beat setdefault): forced. Procedural amendment before any timing
row: 1 oracle job + 3 single-rep timing jobs per cell, median over reps; train128 stays unmeasured; GPU jobs wait for worker idle.

Build 3 (~17:00). E-R7-1 planted NEGATIVE judged PASS at 32/4/8 (graft-scratch +0.757 p .037, graft-sham +0.508 p .049): the
re-validation does not hold (receipt FAIL 1789505772057-0; positive PASS 1789505767100-0). A ruled O8 (no tuning): K=40 fresh
planted-negative draws in the clock, INSTRUMENT_ADMISSIBLE iff false_pass <= 5/40, live w14->w13 pair only then. Built
cohorts/e/r7_clauseb_calibration.py (fresh donor tag 27000+d AND fresh run seeds 2000+8d per draw, so the 40 draws are
independent; decide()) + transfer_v2 random_tag (default 1707 unchanged) + tests. E-R7-3 receipt 1789505775862-0: B2 search
overhead 3.1 ms/gen vs rollout 148 ms/gen (2.1%), episode 9.04 us at 3 threads -- the F7 worker child ALSO ran numba at 3
threads under an 8-thread token (A files D19). GPU arbiter now registers lane gpu (F-R7-1 residue.register/refresh/unregister)
+ test. G-R7-2: E chose option (b): G's production lockstep must match E's measured lockstep elites and cpu_sequential on
w13 train8 and sit within 10% of E's wall before set_decision writes pm:r7:backend. E-R7-2 oracle + 3 timing GPU jobs running.
Owed by 18:35: stop worker E + gpuq in nestor-r6-e (lane E moves to nestor-r7-e for the clock).

Build 4 (~17:10). E-R7-2 oracle job: cpu_lockstep PASS (32/32 elites == G's sequential), gpu_lockstep FAIL (6 fitness + 3 cells
mismatched in 819,200 evaluations vs numba; elites still 32/32; anomaly 1789505981534-0). Timing, 3 single-rep jobs, whole baseline
stage: cpu_sequential 21.7/23.2/22.3 s, cpu_lockstep 21.8/27.1/21.7 s, gpu_lockstep 166.9/155.4/159.8 s. decide(): cpu_sequential,
GPU_REJECT (cpu_lockstep 1.02x < 1.25; gpu ineligible and ~7x slower end to end); pm:r7:backend + pm:r7:gpu_adopt written;
receipt 1789506653147-0. Lockstep buys nothing here: at 32 x 128 x 8 the fused rollout is already ~0.02 s/gen and per-run
sequential calls are not the bottleneck. O8 predicate pinned f790dbb52 (bus 1789506659352-0); draws run in the clock from nestor-r7-e.
gpuq registration pushed 3143ecd39 (7 gpuq tests pass). Push lesson: ops.push refuses to rebase a dirty tree; set the
uncommitted edit aside by file copy (never stash), push, restore, test, commit. Worker E and gpuq arbiter STOPPED (~17:00, ~17:09).

# ROUND 7 CLOCK -- Nestor-E[m1-cf4b44f6] (prompts_r7/E.md; SWARM_R7 s5 E + O8), worktree nestor-r7-e

Boot (~17:55, epoch 1). ff ab1787d14; comms boot m1-cf4b44f6; warmup ok; bus hello. Read the R7-BUILD DONE record and journal.
Item 0 (O8) first: predicate E-R7-O8-clauseB-false-pass-calibration already pinned f790dbb52 (bus 1789506659352-0, seed list
27000+d / 2000+8d committed); f790dbb52 is an ancestor of HEAD and no judged path (cohorts/e, score/transfer_b, metric/floors,
fabric, evidence_n) changed since. Dry-runs on the predicate's envelope: evidence_n.admission_reasons [], envelope.admit ok
(PRODUCTION, noncheckpointable 900 s); receipt guard on a synthetic 40-draw receipt: sample_rule OK, only ROWS_MISSING /
UNCOMMITTED / RUN_START_UNKNOWN (no rows yet). pm:jobs:E clean (0 consumers, 0 pending). Suite running; worker after it.

Iteration 1 (17:58). Suite 568 passed / 1 skipped rc 0. Worker E pid 24596 started from nestor-r7-e and registered (round r7,
tag m1-cf4b44f6). O8: 40 draw jobs queued 17:58:34 (kwargs {draw: d} only; envelope = the predicate's, re-admitted ok before
submit); queue note to A 1789509545408-0. Draw 0 writing rows (~78 at 35 s). pm:r7:gpu_adopt GPU_REJECT -> item 3 off, no
GPU arbiter. No harness module edited this session.

Iteration 2 (~18:04). A (cross-session, ruling 1789509847892-0 on C 1789509820818-0): C's code-drawn DISTANT_QD cell needs the
torch_gpu substrate and nothing consumed pm:gpu:jobs; GPU_REJECT covered only the R16 screen backend. Started the GPU arbiter
from nestor-r7-e (no idle exit): pm:worker:reg:gpu:27084, round r7, tag m1-cf4b44f6; gpu-arbiter consumers 1 (was 0, no
leftover consumer), pending 0. Posted "E: gpuq up" to A,C. Stop it at the FINAL along with worker E. O8 draws unaffected (CPU).

Iteration 3 (18:15). O8 draws 0-17 committed (9edd3653f), all check_b FAIL with gates clean (p_max .24-.96); ~36 s per draw at
8 threads. My first draw monitor watched pm:jobs:E:done for exp_id, a field those entries do not carry, so it was silent; replaced
by a rows-file check_b monitor. A 300 s "stall" after draw 17 is the FIFO broker: both k*=2 tokens are held (C eca39ef50161 since
18:09, G w6 train8 cell since 18:14, leases to ~18:51/18:56); worker E alive, 0 pending, draw 18 waiting for a token. No action; no
decide() before 40 check_b rows.

Iteration 4 (18:20). Correction to iteration 3: the broker is NOT FIFO across lanes (A D22, 1789509956511-0): my ~36 s O8 jobs
re-took slot 1 seven times and starved D; A: no hand throttling, bounded by O8. D 1789510133837-0: gpuq children run with
cwd/PYTHONPATH = nestor-r7-e, so a GPU job needs its module in THIS tree. My first plan (ff after O8) was wrong and corrected
on the bus (1789510560665-0 -> correction): the tree is 19 ahead (O8 rows + journal) / 3 behind origin (C AP-01 CPU harness, D-R7-1,
D-R7-2), so the route is ops.push once the O8 RowWriter is idle, before item 1. C's torch_gpu harness is not on origin yet.
gpuq itself has no fingerprint/repo check and spawns a child per job, so no arbiter restart unless nv/gpuq.py changes.
Item 1 prepared (scratchpad e_r7_live.py): LIVE7 families x run seeds 16..23, checkpointable, wall 2400/seg, cpu 12000;
dry-run admit ok, evidence_n [], guard sample_rule OK (only pre-run refusals). O8 decide(): 18/40, 0 PASS, PENDING.

Iteration 5 (18:40). O8 23/40 check_b, 0 PASS, 0 error rows, gates clean on all. Draw 22 (job ebadac01b269) PAUSED at the
EPOCH 1 boundary (18:37:49 stop flag) after 16/32 runs, 48 rows committed 9e0d43371 without a check_b row; the worker requeued its
segment 1 as b8a02eab75ef behind draws 24-39 (resumable, F9 checkpoint per run, same streams). decide() counts only check_b rows, so
the order is irrelevant; draw 22 is neither dropped nor re-run. Own envelope inaccuracy: the O8 envelope says checkpointable false,
but draw_job goes through transfer_v2._runs, which checkpoints per run, so an epoch boundary resumes it rather than aborting.
Disclose in the receipt. C freed its token at 18:26 (AP-01 INDETERMINATE); G holds slot 0 (w5 t128), E slot 1.

Iteration 6 (18:50). O8 25/40: 24 FAIL gates clean, 1 INDETERMINATE (draw 24), 0 PASS, 0 error rows. Draw 24: graft run 2101|2192
graft_fused_eq_numpy False (bytes unmodified True): FusedRollout != E7.rollout on the 16 untrained donor genomes over train128;
the only such run of ~800 graft runs; check_b v2 correctly INDETERMINATE (p .999). Filed as an anomaly for D with a zero-search
discriminator (rebuild the 16 genomes from PCG64([2101, 27024, 2192, 13]), per genome x seed, K=1/16, threads 1/8, first diverging
tick, argmax near-tie?). decide() counts it completed, not PASS; no rule change. Checked envelope.admit: a continuation segment
is refused only past NNW, so draw 22's segment 1 (b8a02eab75ef) is admissible.

Iteration 7 (~19:00; the iteration 6 header said 18:50, but the clock read 18:40 at that point). O8 31/40: 29 FAIL gates clean, 2 INDETERMINATE,
0 PASS, 0 error rows. Second graft_fused_eq_numpy False: draw 31 run 2101|2255 (donor_tag 27031). Both mismatches are in family 2101
(2/1020 graft runs; chance of both in one named family 1/16, so a lead only). Addendum to anomaly 1789512027239-0 posted to D,A.

Iteration 8 (18:49). O8 COMPLETE: 40/40 check_b rows committed (last ea108a92e, draw 22 segment 1). decide() over the rows at HEAD:
INSTRUMENT_ADMISSIBLE -- false_pass 0/40 (rule <= 5), judged INDETERMINATE 2 (draws 24, 31: graft_fused_eq_numpy False, anomaly
1789512027239-0 + addendum), error rows 0. Prediction was ADMISSIBLE with 1-4 false passes; observed 0, so E-R7-1's single
negative PASS (p_max .049) did not recur in 40 independent draws. Worker idle (0 pending) -> ops.push now, then receipt, then item 1.

Iteration 9 (18:52). ops.push: first attempt rejected non-ff (concurrent push), retry rc 0 -> 3b59f0a66 on integration
(merge-base verified); it contains C's 2778c4ea3 torch_gpu harness; nv/gpuq.py unchanged (no arbiter restart); no item-1 judged
code changed since f790dbb52. Posted 'E: pushed at 3b59f0a66' (1789512677260-0). O8 RECEIPT 1789512697580-0 (guard 10/10 OK;
status PASS = the calibration holds, decision INSTRUMENT_ADMISSIBLE; discloses judged_indeterminate [24, 31], the draw 22 epoch
pause under checkpointable false, and D22). A 1789512067159-0: counting stands; D takes the fused != numpy anomaly as priority 1; a
recurrence in the live pair gives INDETERMINATE. ITEM 1: predicate E-R7-1-clauseB-live-w14-w13 pinned 3b59f0a66 (bus
1789512700124-0; prediction FAIL); LIVE7 families x run seeds 16..23, M2 800x128, checkpointable, 2400 s/segment, cpu 12000;
submitted. E-R6-1 untouched, not pooled.

Iteration 10 (~18:58). Item 1 job 90f1b50b9cb2 admitted, CPU slot 1 at 8 threads since 18:51:50 (G on slot 0); monitor armed on the
rows (integrity, check_b, error/paused). Item 2 prep (read-only): metric.b2_screen.admission_cost_v2 on E-R7-3's committed row
(episode 9.04 us, measured at 3 threads (D19); overhead 3.13 ms/gen): 4 specs x 32/4/8 = 30,340 s rollout + 641 s search = 8.43 h
single worker. That does not fit ~7.6 h left after item 1 (fits only at workers=2, i.e. taking G's slot). No B2 v2 screen job fn
exists in the repo either (no caller of admission_cost_v2). Expected route after item 1: admit -> refusal -> PC with this projection
(scratchpad e_r7_b2.py). No trimming; no re-measurement at 8 threads (the figure is the measured one).

Iteration 11 (19:18). ITEM 1 DONE, job 90f1b50b9cb2 ok, 1 segment, 1560 s wall / 11709 CPU-s, 98 rows at 7d9c0b06b.
FIRST ADMISSIBLE CLAUSE B VERDICT: check_b v2 FAIL, gates clean (problems []). graft - scratch +0.738 (p .046), graft - sham
-0.662 (p .852) -> graft_p_max .852, Holm .852. Sham BEAT graft: sham - scratch +1.400, sham_below_scratch_p .998. So the
feature-permuted donor transfers MORE than the donor itself; against scratch alone this pair would have read as a PASS at p .046.
Integrity 32/32 graft (bytes + fused==numpy; no recurrence of the O8 anomaly), sham_integrity 32/32; oracles clean (world honest
0/16 failing, skip_lin 16/16 caught, brain 0 mismatched rows, cheat 16/16). p_method montecarlo_200000_seed20260915.
FLAG to disclose: pair.rederived_equals_harness false (harness_graft_p_max .85148 vs rederived .85243) -- reading the judge code now.

Iteration 12 (19:20). Pushed e7d095a19 (rc 0 first try). ITEM 1 RECEIPT 1789514378793-0, guard 10/10 OK, status FAIL -- the first
Clause B verdict admissible under EVIDENCE_N_v1. file_candidate against PC 1789486665691-0 refused ALREADY_FILED (my r6 session
filed the ESTIMATE 2132 s / 6316 CPU-s at filing time); the MEASURED cost is 1560 s wall / 11709 CPU-s (32 runs, 1 segment, 8
threads) -- CPU-s ~1.85x the estimate because the estimate scaled E-R6-1's CPU-s linearly while the wall halved on 8 threads.
Reported to A rather than re-filed (no second filing exists for a stub).
ITEM 2: admission refused by code -- admit reasons CPU_WALL_OVER_CEILING + PROJECTED_PAST_ROUND_END on the measured projection
(4 specs x 32/4/8: rollout 30,340 s + search overhead 641 s = 8.61 h single worker vs 7.80 h to drain). PC stub 1789514379229-0
filed with that projection (envelope.refuse + file_candidate ok). No trimming, no re-measurement, no spec dropped. Also recorded:
no B2 v2 screen job fn exists in the repo (nothing calls admission_cost_v2).

Iteration 13 (19:22). Verified the rederived_equals_harness flag rather than assuming: transfer.signflip_p's MC branch (n > 20)
draws ONE seeded sign matrix PCG64(20260915), so the p depends on the ORDER of the paired diffs. Same 32 diffs (identical multiset,
mean -0.6624): judge order (sorted) p_sham .85243 / p_scratch .04626; harness order (4200 first) .85148 / .04549. E defect, mine;
the verdict is unaffected (same side of alpha both ways) but near alpha it could flip a verdict. NOT fixed mid-round (it would
change a judge that has already emitted a verdict); reported to A for the packet / a round 8 PC. Posted item 1 + item 2 + the defect
to A. All three prompt items are now closed (item 3 off: GPU_REJECT). Idle for asks until NO_NEW_WORK 02:37:49.

Iteration 14 (19:23). A ruling 1789514517552-0: E-R7-1 FAIL STANDS (no rerun/re-judge/pooling); the order-sensitivity is D25,
credited to E, packet defect + round 8 PC, fix NOT applied tonight; item 2's refusal correct; D26 = a PC stub accepts only ONE
filing, so E's MEASURED item-1 cost (1560 s / 11709 CPU-s) could not supersede the r6 ESTIMATE (2132 s / 6316 CPU-s).
D25 PC FILED: stub 1789514596470-0 + file_candidate ok (evidence: the four recomputed p-values). DISCLOSED: file_candidate cannot
OPEN a PC (only envelope.refuse creates stubs, and it publishes a refusal event; no job was refused here), so I wrote the stub dict
by hand in refuse()'s schema with source_event E_DISCLOSED_DEFECT_D25 -- auditable, precedent E r5 1789471324763-0; asked F for an
envelope.open_candidate as D26's sibling.
C's GPU job 14100077cf4d ran through my arbiter earlier (rows written into MY repo by its RowWriter, committed c0f79af3c). After
ops.push that sha is ORPHANED (rc 1); the rows are on origin at 0c280c564, content identical (sha256 1c5a7b90..., 100 lines).
Told C to cite the post-push sha or the guard's rows_committed check fails. My arbiter log stays empty (the arbiter logs to the bus,
not stdout), which is why I checked the queue/keys instead.
E s5 items all closed. Idle for asks until NO_NEW_WORK 02:37:49; gpuq + worker E stay up until the FINAL.

Iteration 15 (19:29). A (cross-session): residue scan rc 1, UNREGISTERED_ACTIVE_CONSUMER for my gpuq arbiter; no
pm:worker:reg:gpu:* key although I reported one at 18:05. Verified, then re-registered by code (residue.register, pid 27084,
tag m1-cf4b44f6, repo nestor-r7-e, round r7): scan rc 1 (19:28:20) -> rc 0, residue [] (19:29:20).
CAUSE (A's hypothesis was wrong; checked the code instead of accepting it): gpuq.serve already calls residue.refresh on EVERY
poll turn (nv/gpuq.py:254, block 5 s << TTL 90 s). residue.refresh is only r.expire(key, TTL) -- a NO-OP once the key has
expired -- and the loop cannot refresh while blocked inside run_job. C's C-R7-01 GPU job ran 217.6 s > 90 s TTL, so the key
died mid-job at ~19:06 and every later refresh silently did nothing (absent ~23 min). Any GPU job > 90 s reproduces it; the
GPU lease cap is 600 s.
No fabric edit and no arbiter restart (A's instruction; my poll loop is already correct). PC stub 1789514994865-0 filed with
measured evidence: fix = refresh() re-creates a missing registration + a heartbeat that survives a blocking job (+ maybe
REG_TTL > 600 s lease cap), with a regression test. Mitigation until close: my own background heartbeat re-registers pid 27084
every 30 s only while the pid exists AND verify_worker_cmdline says it is still the arbiter, so it cannot fake liveness.
The FINAL stops the arbiter and the heartbeat explicitly.

Iteration 16 (19:31). A ruling (cross-session): KEEP the heartbeat to the FINAL, on conditions I accepted -- stop it BEFORE the
arbiter at the FINAL, never re-register after the arbiter exits, log every re-registration, and state in the FINAL that it ran
(a disclosed live mitigation, not a silent fix). D28 recorded with MY cause, not A's; PC 1789514994865-0 accepted with both
halves + regression tests. A's packet also notes why F7 workers do not show this: their supervisor heartbeats while the child
computes, whereas the arbiter blocks in-process.
MY ERROR (posting): I wrapped the arbiter command line in backticks inside a double-quoted bus body, so bash ran it as a command
substitution ('-m: command not found') and note 1789515027621-0 lost that phrase. Verified by reading the posted body back
(2470 chars, other sections intact) and posted a correction. Rule for myself: no backticks in a double-quoted bus body, and read
back any long post.
Heartbeat live since 19:30:02; reg key present, TTL 85; 0 re-registrations so far.

Iteration 17 (19:45). D29 (row status vocabulary) does NOT touch lane E: checked all six E round 7 rows files against
fabric.rows.STATUSES -- only record / cheat / control, 0 rows outside the vocabulary, so nothing of mine was refused. A's standing
instruction for tonight (keep ROW status 'record' for an OBSERVATION-class job; the evidence class lives in the envelope and the
receipt) is noted for any ask I still serve; E has no queued work.
RELEVANT TO MY ANOMALY: D's D-R7-3 on the two fused != numpy loci I filed reports decision d24:BRAIN_NEAR_TIE | d31:BRAIN_NEAR_TIE
with controls ok and donor sha256 matching my rows -- i.e. a float32 argmax near-tie at the diverging brain row, not a genome-range
or world-step defect. D's rows are on origin inside 'aborted' payload wrappers (D29), so the analysis is recoverable, but its receipt
eligibility waits on D-R7-3b. I will cite it in my FINAL only if D files that receipt before drain; otherwise I report my two
INDETERMINATE draws with D's label as PRELIMINARY.
A's D29 design ruling (F's PC, no round 7 push): fail loudly on any refused row, no alias of evidence_class to a row status,
validate at first emit and at submit, and a CI lint that rows.STATUSES and evidence_n.EVIDENCE_CLASSES never overlap.

Iteration 18 (19:47). EPOCH 2 boundary 19:37:49 passed with no E job running (nothing paused; E has no queued work).
D-R7-3b (predicate 1789515684961-0, code 6bbd8db43) carries D's FULL DISCLOSURE of the mechanism behind my two INDETERMINATE O8
draws, and it is sharper than "fused is wrong": d24 genome 14, ONE env (84, train seed 9184), tick 30, kind idx -- the numpy
float32 EINSUM logits TIE EXACTLY (gap 0.0) and pick 0, while the fused kernel, a sequential float32 emulation, linear_act_row
direct AND the float64 reference all pick 4 (float64 top-2 gap 1.08e-07, clear_rows False). So the two paths differ only in how an
exact float32 argmax tie is broken (einsum vs sequential accumulation order), not in genome range, integer overflow or world step;
labels d24/d31 BRAIN_NEAR_TIE, controls ok, donor sha256 matching my rows. PRELIMINARY until D-R7-3b reproduces them on ACCEPTED
rows (D read the refused wrappers first and disclosed that). If D files that receipt before drain I cite it in my FINAL; otherwise
I report my 2 INDETERMINATE draws with D's label marked preliminary. Nothing here changes the O8 decision (they count completed,
not PASS) or the item 1 verdict (integrity 32/32 there).
gpuq registration heartbeat: 0 re-registrations since 19:30:02 (no lapse), for A's FINAL count.

Iteration 19 (19:48). Watcher hygiene: my first ask watcher (19:21:07) was still polling when I armed a replacement (19:47:11), so
asks would have been reported twice; stopped the old one and verified its pids are gone. Exactly one ask watcher and one gpuq
registration heartbeat (19:30:02) now run. Inbox gap check between the two watchers: empty, nothing to E was missed.
MY ERROR (diagnostic, harmless here): the psutil check matched ITSELF -- the process list entries at 19:47:43 were the checking
process, whose own `python -c` source text contains the very substrings it greps for. Same class as the kill-script-matching-itself
lesson: match argv TOKENS and skip your own pid; a substring search over cmdline text always finds the searcher.

Iteration 20 (19:55). MY ANOMALY IS RESOLVED INSIDE THE ROUND. D-R7-3b receipt 1789516880015-0 (rows ef6667f44, OBSERVATION):
both O8 mismatches are BRAIN_NEAR_TIE -- ONE env at ONE tick each (d24 genome 14, env 84 seed 9184, tick 30; d31 genome 13,
env 106 seed 9206, tick 1), float64 reference NOT clear (top-2 gaps 1.08e-07 / 1.78e-07). numpy Linear.logits is
einsum-then-bias, linear_act_row is bias-then-features; one order hits an EXACT float32 tie (gap 0.0) and argmax breaks it to the
lower action. NEITHER path is consistently right (d24: numpy ties, picks 0, kernel+f64 pick 4; d31: sequential ties, picks 3,
numpy+f64 pick 4). Deterministic: 1 thread == 8 threads, 3 repeats agree, no batch effect. Both rebuilt donor sets hash to my
committed donor_sha256.
A rulings 1789516925555-0: the exact-equality fused_eq_numpy gate STAYS unchanged tonight (B, G and E depend on it; three verdicts
already emitted under it); D files a tie-aware gate as a round 8 PC, not a patch; for the packet this is a tie-break artifact at a
~1e-7 margin, NOT a logic error, so it does not impugn B-R5-1 (32/32 clean), the R16 screen (42/42) or my Clause B verdict (32/32
integrity, no recurrence), and it explains why the 2-in-819,200 mismatch showed up only on UNTRAINED random-donor genomes, which sit
near ties far more often than trained ones. My draws 24/31 stay INDETERMINATE; E-R7-1 FAIL stands. Credit: E filed, D resolved.
FINAL draft updated (scratchpad E_ROUND7_FINAL_draft.md): the label is no longer preliminary and A's scope language is folded in.

Iteration 21 (20:20). A guardrail 1789517887578-0 (binds every lane for the rest of r7): do NOT name an anti-prior ARM, rank,
quantile or prior in any post addressed to or readable by C or R -- describe the cell and the mechanism instead. Those fields are
conductor/D-only while the round is live. I checked my own record rather than assuming: 0 of my r7 bus posts name an arm, rank,
quantile or prior (regex over every pm:swarm entry from lane E tag m1-cf4b44f6 since the clock started), and the apparent hits in
my journal and FINAL draft are unrelated words -- "armed" (watchers) and "priority 1" (A's routing of my fused != numpy anomaly).
Lane E ran no anti-prior work, so nothing needs redacting; the rule is recorded here so the FINAL and any remaining post keep to it.
Context accepted by A (D's finding): the two anti-prior-arm PASSes share no mechanism -- r6's was search saturation, AP-02's charge
only partially bound and its meter not at all -- so the packet treats it as a CELL/PRESSURE DESIGN issue for round 8 ("hard" cells
are often not hard because the pressure does not bite), not a scoring claim.
