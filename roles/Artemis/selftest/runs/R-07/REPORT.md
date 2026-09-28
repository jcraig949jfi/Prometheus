# REPORT

## 1. WHAT I SET OUT TO TEST

Crius's closed campaign found that evolutionary search never put together a
procedural-reuse mechanism (recorder + invoker + planner) in its bytecode
substrate, even though the mechanism works, pays well and is short. The
campaign's essay calls this an "accessibility frontier": a flat valley, then a
ledge, then a cliff. Its own strongest objection is that the frontier might
come from the representation. In genotype-phenotype maps with percolating
neutral networks (Wagner 2008; Greenbury, Louis & Ahnert 2022), fitter
phenotypes can be reached without crossing valleys. I asked a narrower
question that can be tested: does Crius's own genotype-phenotype map lack such
neutral networks around the competent enumerator? Put another way, is there
really no non-deleterious single-mutation path from the enumerator to the
reuse mechanism, or does a neutral path exist that search simply failed to
follow? If neutral paths exist, "add neutral networks" cannot be the missing
ingredient. The obstacle would then be how rare the doorstep genotypes are,
and how that rarity biases where drift goes.

## 2. WHAT I DID

Code: crius/ exported with `git archive 7069c0ce6 crius` (the campaign's
closing commit) into work/R-07/src and run only there, with GIT_* unset. The
essay was read at 391395aac (docs/essays/2026-09-24-accessibility-frontier.md).
World/config: crius/configs/c2c.json (typed procedures + PSIM/PMATCH). Programs
are the hand-written PARTS sources in crius/parts_c2.py (P_BASE = 19-instruction
enumerator; P_INV; P_REC_INV = recorder+invoker "ledge"; P_PLAN;
P_REC_INV_PLAN = complete mechanism). Fitness is Crius's own lifetime fitness
(tasks solved + 0.5 x unspent-cost fraction).

Streams: generator namespace "search" with fresh seeds 9001-9003 (screening),
9001-9010 and 9101-9110 (confirmation). The gate seeds 301-310 were used only
to reproduce the published PARTS value. The sealed qualification namespace was
not touched.

Scripts (all in /home/jcraig/artemis-selftest/work/R-07):
- common.py: evaluation helper. It screens out a program early once it has
  failed 3 tasks that P_BASE solves on the first stream (these are infinite or
  broken loops, certainly deleterious). It is used only for cheap screening,
  never for confirmation.
- ref.py: P_BASE, P_INV and P_REC_INV on 10 gate + 10 fresh streams.
- e2_paths.py + an2.py: a Weinreich-style path census. Each target is exactly
  P_BASE plus inserted instructions (checked with difflib: 24 inserts for
  P_REC_INV, 45 for P_REC_INV_PLAN, no deletions or substitutions). The
  program is an assembler listing with labels, so each intermediate keeps
  its labels, and jumps fall through to the next instruction that is
  present. That is the same semantics as Crius's shift-aware insert
  mutation. I sampled random insertion orders (30 orders for the ledge, 12
  for the full mechanism) and evaluated every distinct intermediate
  (661 + 530 genotypes) against P_BASE, paired, on 3 streams. Neutral means
  |dfit| <= 0.01.
- e1_neutral.py + confirm.py: 3 neutral random walks x 40 steps from P_BASE
  using Crius's own `search.mutate` operator (one mutation per step). At each
  step I sampled 12 one-mutants, classified them, and moved to a random
  neutral one. That is 1440 neighbours of points on the enumerator's neutral
  network. I also tracked edit distance to P_REC_INV. Every 3-stream
  "beneficial" neighbour was re-evaluated on 10 fresh streams and
  disassembled.
- verify.py: the one fully neutral-then-up ordering to the complete
  mechanism, re-evaluated on 10 fresh streams at 0, 41, 42, 43, 44 and 45
  inserts.
Outputs: out/*.json, out/e1_P_BASE.log.

## 3. RESULT

Reproduction. On the gate streams, P_REC_INV vs P_BASE is +1.136 fitness,
positive on 7/10 streams (essay: +1.138, 7/10), and P_INV is -0.002, 0/10. On
10 fresh streams the ledge is smaller and noisy: +0.645, 7/10 positive, with
per-stream task changes from -4 to +5.

Crius's map is highly neutral around the enumerator. Of 1440 one-mutant
neighbours along neutral walks:
- 632 (44%) were neutral.
- 745 (52%) were broken or screened (mostly non-terminating loops).
- 40 (3%) were deleterious.
- 23 (1.6%) looked beneficial on 3 streams. On 10 fresh streams they are
  real but small (+0.10 to +0.60). Every one is an enumeration-order tweak,
  such as the start counter CONST R0 changed from 0 to 1 or 2. None
  involves a recorder, invoker or planner.

Zero reuse footholds were found. The neutral walks drifted away from the
ledge: edit distance to P_REC_INV went from 26 at the start to 36-37 after 40
steps in all three walks.

A neutral path to the ledge exists. On the 24-insert route from P_BASE to
P_REC_INV, single inserts are almost all neutral. Of 30 random orderings, 1 is
non-deleterious at every step. At least 7 distinct 23-insert genotypes
(missing, for example, PREC_END, PREC_BEGIN or PINVOKE) are neutral relative
to P_BASE, so the ledge is one mutation from the enumerator's neutral network.

A near-neutral path to the complete mechanism exists. On the 45-insert route
from P_BASE to P_REC_INV_PLAN, every one of the 12 orderings first turns
beneficial only at insert 37-45. Beneficial intermediates exist only at sizes
37-45. One ordering has 41 consecutive neutral inserts. I confirmed it on 10
fresh streams:

| Inserts from P_BASE | dfit vs P_BASE | Tasks solved |
|---|---|---|
| 41 | -0.004 | 0 change on all 10 streams |
| 42 (+BRNZ R6,EXEC1) | +1.234 | up on 6 streams, down on 1 |
| 43 | +1.223 | |
| 44 | +1.195 | |
| 45 (+INPUT R6,current) = complete mechanism | +13.811 | up on 10/10 streams (+1 to +23) |

So a single-instruction-insertion path from the enumerator to the full
mechanism exists. No step on it loses more than 0.03 fitness: 41 neutral
steps, a ledge, two near-neutral steps, and then a single insertion that
adds about 12.6. Most orderings are not like this: in the rest, about half of
the intermediates are broken loops. With tolerance 0.01 on 3 streams, 0 of 12
orderings pass stepwise; with tolerance 0.1, 1 of 12 does.

Plain conclusion: the premise that the frontier exists because the map lacks
neutral networks is false for Crius's substrate. The enumerator's neutral
network is large and reaches genotypes one insertion away from both the
ledge and the complete mechanism. What search lacks is direction. The doorstep
genotypes are a vanishingly small part of a very large neutral set, so
undirected drift goes elsewhere: no reuse neighbours in 1440 samples here, and
none in the campaign's roughly 260k children, where tied takeovers already
allowed drift. In Greenbury's terms, neutral connectivity is present and
phenotype bias is missing: the reuse phenotype is rare in genotype space, so
the neutral network is rarely next to it.

## 4. DID IT RESOLVE THE QUESTION

Partly.
- Resolved: the objection "a map with percolating neutral networks would make
  it reachable" assumes Crius's map lacks them. It does not. Neutral paths from
  the enumerator reach one edit from the mechanism. So neutrality as such is
  not what controls accessibility here.
- Not resolved: whether a different map, one where the reuse phenotype is
  high-frequency (strong phenotype bias, many genotypes per phenotype), would
  make search find it. That needs a second encoding and search runs, which do
  not fit in 1 CPU-hour.
- Caveats:
  - Paths were sampled only along the hand-written insertion route. Other
    routes may exist.
  - Neutrality was screened on 3 streams. The key genotypes were confirmed
    on 10 fresh streams, but not every intermediate was.
  - I did not measure the size of the neutral network, or the fraction of it
    that sits next to the mechanism. I only showed that such genotypes exist
    and that random drift did not approach them.

## 5. CONSEQUENCES

1. False premise, and a wrong ruler value in the essay. The essay says the
   accessible path length is "undefined; no such path was found to exist" and
   describes a flat valley. At single-instruction granularity, in Crius's own
   operator space, a non-deleterious path to the complete mechanism does
   exist (tolerance 0.03). The "valley" is a neutral plateau whose far edge
   touches the mechanism. The link-level PARTS table hid this because it
   measured only whole links. The essay's conclusion about accessibility
   survives, but its mechanism changes from "every path goes down or stays
   flat for too long" to "the neutral plateau is huge and its exit is a
   needle". The Crius essay's author(s), and anyone citing it, should correct
   the ruler.
2. Consequence for representation engines and the co-evolving-representation
   work: adding neutrality or redundancy alone should not be expected to help.
   The dial to test is phenotype bias, meaning an encoding in which
   reuse-shaped programs are frequent, or a way to bias drift toward the exit.
   The next experiment is a controlled pair: the same world, with Crius's
   encoding vs an encoding with high reuse-phenotype frequency. Measure
   neutral-network size and exit density, then the discovery rate.
3. Instrument note for anyone re-running path censuses on Crius-style VMs:
   about half of all intermediates and mutants are non-terminating loops,
   which cost roughly 20x a normal evaluation. An early-abort screen is
   needed to stay in budget.
4. Reproduction: the published ledge value (+1.138, 7/10) reproduced on the
   gate streams. On fresh streams it is weaker and noisy (+0.645, 3 of 10
   streams not positive), which is worth knowing when the ledge is called
   "the only foothold".
5. Not a new positive result about reachability. Nothing here shows that
   search would find the mechanism.

## 6. COST

- About 1.5 hours of my own work.
- Roughly 45-50 CPU-minutes, all with at most 2 worker processes and well
  under 2 GB RAM. That includes about 15 CPU-minutes lost on a first
  path-census run without early screening, which I killed, and a restarted
  neutral-walk run.
- Not done:
  - No alternative encoding was built or searched.
  - No estimate of neutral-network size or exit density.
  - Path orderings were sampled, not exhaustively enumerated (2^24 and 2^45
    subsets).
  - Only 3 neutral walks.
