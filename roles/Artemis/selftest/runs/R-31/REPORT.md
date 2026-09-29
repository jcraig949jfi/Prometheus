# REPORT

## 1. WHAT I SET OUT TO TEST

Ares's cycle-2 report says that in its graph-organism substrate evolution
recruits the recurrent-edge memory carrier instead of the designated leak
("keep") carrier because recurrence has a wide, flat viable parameter region
and keep has a narrow one. It turns this into a design rule for primitives in
general. Two other explanations fit the same data. One is payoff: the first
usable carrier to appear wins if it scores higher, and the hand-wired keep
circuit peaks at 33.75 while recurrence reaches the cap of 40. The other is
arrival: whichever carrier shows up first wins. In the only swept data, basin
width and payoff move together. I used the champion snapshots Ares already
committed to ask three things. Did a keep carrier ever become functional first
(wired between the cue and the output, and actually carrying the bit)? When it
did, was it kept or displaced? Does the outcome follow the width of keep's
basin or the fitness keep reached? The confirmatory step was to re-run the
basin sweep under a decoupled-leak update rule and then run 20-40 GA runs. The
package marks that step as blocked until the operator rules on Ares's runs,
so I did not run it.

## 2. WHAT I DID

Data (all committed, read from a `git archive` export of origin/main
6ff2b2f8a; ares/ is unchanged from 3f68be2b9):
ares/runs/sweep_c2/c1_all_s201..s210.json and c3_keep_reachable_s201..s210.json.
Each file holds 120 per-generation champion snapshots and the run's held-out
eval seeds. I also read the *_dissect.json files, basin.json, and the
best_ever genomes of every sweep_c2 arm. The code used was
ares/substrate.py, search.py and carriers.py from the same export. No GA was
run and no repository test suite was run.

Scripts, all in /home/jcraig/artemis-selftest/work/R-31/, with outputs in out/:
- trace.py: covers 20 lineages x 120 generations = 2400 champions. For each
  champion it records:
  - keep >= 0.94 nodes lying on a directed cue(input 1) -> output path;
  - recurrent edges with |w| >= 1 on such a path;
  - held-out fitness intact, and with keep, recurrence, plasticity or all
    carriers cut;
  - the carrier class, using Ares's own classify() with floor 0.
  At generation 119 this reproduces Ares's dissect numbers exactly (19/20
  identical; c3 s201 differs because dissect used the best_ever genome).
  Output: out/trace.json.
- summarise.py: per-lineage first-arrival, load-bearing, displacement and cap
  generations, with train and held-out fitness at each event
  (out/summary.json, out/table.txt).
- readout.py EPS: re-evaluates every champion with the argmax readout changed
  so that |output| < EPS counts as exactly 0. Run at EPS = 1e-3, 1e-6 and 1e-30.
- readout_all.py: the same check on the best_ever champion of every sweep_c2
  arm (out/readout_all_finals.json).
- keepbasin.py: a basin sweep on evolved genomes. For the best keep-dependent
  snapshot of each lineage, it sweeps each cue-wired keep node over 0..0.98 in
  steps of 0.02, with both readouts. "Viable" means >= 50% of best, the
  report's own criterion (out/keepbasin.json).

## 3. RESULT

A. The readout has a defect that inflates keep's success. The action is the
argmax over three float32 output nodes, and exact-zero ties go to the lower
index. A leaky node therefore "remembers" the cue as long as its value is
still above zero, and that value decays toward the smallest subnormal. In
c3_keep_reachable s208, the final KEEP champion holds regime 1 through step
39 with output 16 = 2.8e-45 against exact 0.0, using a leak of only 0.27.
Its score is 40.0 with the stock readout, 6.2-6.8 when values below 1e-6 are
zeroed, and 27.2 even at a 1e-30 cutoff.

Across all sweep_c2 arms, 10 best_ever champions change under the 1e-6
readout. Nine are KEEP-classified and one is a keep+plasticity+recurrence mix.
No RECUR or PLAST champion changes. Breakdown by arm:

| Arm | Keep champions that fail |
|---|---|
| c1_only_keep | 3/10 (at cap: 6/10 before, 4/10 after) |
| c2_tax_high | 2/10 |
| c2_no_recur | 1/10 |
| c2_no_selfloop | 1/10 |
| c3_keep_reachable | 1/10 |
| W16_present | 2/10 |

The c3 result "keep load-bearing 2/10" is really 1/10 genuine keep, plus one
subnormal artifact.

B. Did keep arrive functionally? Counting a carrier as load-bearing when
cutting it drops held-out fitness to 25% or less of intact, with held-out
fitness >= 8:
- **c1_all (default step size):**
  - a keep >= 0.94 appears in 2/10 lineages and is cue-wired in 1/10 (s201);
  - even there it arrives at generation 35, after recurrence was already
    load-bearing at generation 24;
  - keep is the first load-bearing carrier in 0/10 lineages (s207 has a mixed
    keep+recurrence circuit with keep 0.04);
  - so in this arm functional keep arrival was essentially never delivered.
- **c3_keep_reachable:**
  - keep >= 0.94 appears in 8/10 lineages and is cue-wired in 7/10;
  - the first load-bearing carrier is KEEP in 5/10 (4 genuine plus the s208
    artifact), RECUR in 4/10 and PLAST in 1/10;
  - so this arm did deliver functional arrival, first, in 4/10 lineages.

C. What happened to keep when it arrived first. There are four genuine
lineages:

| Lineage | Keep-only phase | What happened next |
|---|---|---|
| s210 | Reached cap at generation 5 | Kept for 117 generations. Final KEEP. |
| s206 | Held-out fitness plateaued at 19-29.7, generations 12-30 | Recurrence became cue-wired at generation 30 (33.4) and replaced keep at generation 40 (40.0). |
| s209 | Held-out fitness plateaued at 14.6-34.75, generations 13-23 | Recurrence replaced keep at generation 29 (40.0). |
| s204 | Keep-only best 18.4; then a keep+recurrence mix reaching 39.97, generations 13-75 | Drifted to recurrence-only at the cap (generation 76 onward). |

In the two cleanly displaced lineages, the keep-only plateaus (29.7 and
34.75) sit at the hand-wired keep ceiling of 33.75. The one lineage that
kept keep got it to 40, so 33.75 is not a hard ceiling for evolved keep.
Displacement happened when recurrence offered a higher score. It did not
happen while keep was at the cap. s204 is the exception: there both carriers
were load-bearing at the cap and the drift was neutral.

D. Keep basin width on evolved genomes (thresholded readout). The viable
fraction of the keep range is:
- s201: 0.06, range 0.94-0.98
- s204: 0.20, range 0.80-0.98
- s206: 0.06
- s209: 0.26, range 0.74-0.98
- s210: 0.24, range 0.76-0.98

The hand-wired figure was 0.12. Every evolved keep basin sits against the
0.98 clip. Keep's basin width does not separate the retained lineage (s210:
0.24) from the displaced ones (0.20, 0.06, 0.26). The peak fitness the keep
circuit reached does separate them (40 versus 29.7 and 34.75), though with
n = 4. With the stock readout, s210's keep basin looks wide (0.92, from
0.08-0.98) only because of the subnormal tie described in A.

Conclusion: the committed snapshots contradict the premise that the
keep_mut_sigma = 1.5 arm (c3_keep_reachable) never delivered functional
arrival: keep arrived and carried the bit first in 4/10 lineages. Afterwards
it was displaced in 3 of 4. Within that small set, the outcome follows the
payoff keep had reached, not the width of keep's own basin. That is a pointer
toward the "first-carrier payoff" reading. It is not a demonstration,
because between carriers, width and payoff are still collinear.

## 4. DID IT RESOLVE THE QUESTION

Partly. The read-only step is done and answered its own question: arrival was
delivered in the keep-reachable arm, and displacement follows payoff within
keep lineages. It could not separate basin width from payoff as the cause of
recruitment, because nothing in the committed data varies one while holding
the other fixed. n = 4 lineages is descriptive only. The decisive test is a
payoff-matched decoupled-leak cell with keep's peak held at 33.75 while its
basin widens, plus a cell where the peak rises to 40. It needs new GA runs,
which are blocked pending an operator ruling. It should also only be run after
the readout defect is fixed, or its keep counts will be inflated as in A.

## 5. CONSEQUENCES

- **Instrument defect (new; Ares and Nyx should know).** Argmax over float32
  outputs, with exact-zero ties going to the lower index, lets a leaky node
  carry a bit in a 1e-45 subnormal residual. Every champion that depends on
  this is keep-classified, so every keep success rate in cycle 2 is inflated
  by up to 3/10 per arm. The "c1_only_keep 6/10 exactly 40" figure falls to
  4/10. The keep-reachable result falls from 2/10 to 1/10. Evolved keep
  basins look much wider than they are.
- **Any decoupled-leak arm is exposed to the same defect.** Under v = keep*v + f
  a residual never needs to decay at all, so that arm would likely be exposed
  even more.
- **Suggested fix before any rerun:** zero |output| < ~1e-6 before the
  argmax, or make ties abstain. Computing in float64 would make it worse.
  Rechecking the committed champions under the fix is cheap (minutes).
- **False premise corrected.** "c3 may not have tested functional arrival"
  is false. Keep was the first functional carrier in 4/10 lineages. Arrival
  was delivered and was not sufficient.
- **Weak positive pointer, not a result.** Within keep-first lineages,
  retention follows the fitness keep had reached (cap versus a plateau near
  30-35), not its basin width. This leans toward "first-carrier payoff", with
  "intermediate payoff" as the design lever. The design rule in s4.5 of the
  cycle-2 report should stay labelled a hypothesis.
- **Minor.** The edge-only "cue-wired |w| >= 1 recurrent edge" detector
  misses functional recurrence in several lineages (for example c1_all s209
  and s210). Ablation-based classification per snapshot is cheap and should
  replace it.
- **The hand-wired basin script is not committed** (only basin.json is), so
  I could not check whether the 33.75 and 3/25 figures are affected by the
  subnormal tie.

## 6. COST

About 1.5 hours of my time. About 8 CPU-minutes in total, single process
(trace 1m40s, readout variants about 1.5 min each, all-arm check about 2 min,
basin sweep under 1 min). No GA runs and no new basin sweep under the
decoupled rule, because that step is blocked pending an operator ruling. No
holdouts touched, and the repository was not modified. One repository-wide
git grep wrote its oversized output to a file under the session's projects
directory. I did not open that file.
