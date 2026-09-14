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

Next / steal: closed-loop needs more training seeds or a regulariser before any
generalisation claim; C3's representation ecology (dense/CP/Tucker/TT/bitset)
is the natural next genome comparison. E4b = archive-level positive (QD coverage/qd_score vs the same
number of random genomes inserted into an archive), closed-loop genomes (C's TT
policy on obs), and B's numba form for eval. B's batched Encounter to replace the NK stub; C1's TT cores as
the genome for E1; E2 branch points with a random-filler control; E3 with
repeated restarts per load gene (n>=5) to beat the 4.6% A/A floor.
