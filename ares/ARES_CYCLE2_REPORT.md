# ARES_CYCLE2_REPORT -- ATTACK THE MECHANISM

Currency: 2026-09-23. Ares, M2. Prereg ares/DESIGN_C2.md on main at
ab137f52b before any run; 190 GA runs (180 preregistered + a 10-seed
post-hoc falsification arm) under ares/runs/sweep_c2/; gates.txt,
recheck.json, basin.json. Seeds 201-210, held-out sets from 40000: every
lineage in this cycle is independent and none was re-evaluated from an
earlier cycle. EXPLORATORY analyses are labelled where they appear.

## 0. Headline

The question "why does recurrence win?" is answered, and the answer is
NOT the one this cycle preregistered. All three carriers the substrate
offers are individually sufficient; recurrence is not better at the
task (hand-built, the DESIGNATED carrier scores 33.75 against
recurrence's 24.56); and making the designated carrier equally
reachable does NOT dislodge recurrence. What separates them is the
shape of their viable parameter region:

    carrier           best   viable region (>= 50% of best)
    KEEP (designated) 33.75  3 of 25 swept values, only [0.94, 0.98]
    RECUR (undesig.)  40.00  14 of 23 swept values, [2.75, 6.0], and
                             saturating: 4.0 -> 40, 6.0 -> 40

Keep works only in a 4%-wide sliver pressed against its own clip
ceiling; recurrence works across a wide, flat, open-ended region where
more is never worse. Evolution took the wide basin, not the higher
peak. Reachability was necessary but not sufficient -- proved by a
falsification arm that lost my own prediction (s4.3).

Second result, independent of the first: blocking recurrence costs
nothing. Under forbid_recurrence all ten lineages still reach the cap,
substituting plasticity (load-bearing 7/10) and keep (3/10), at a cost
of about ten generations. Mechanism substitution is real in this
substrate.

Third: this cycle overturns one of cycle 1's own headline numbers (s5).

## 1. Gates (operator's stopping rule, DESIGN_C2 s8)

    GATE A substitution      OPEN   (robust; at-cap numbers)
    GATE B causal explanation OPEN  (on substance; the rule's NAMED
                                     explanation is refuted -- see s4)
    GATE C transplantable     SHUT  (corrected from the first printout)

Disposition by the rule: CONTINUE_RECOMMENDED. Per the directive this
is a RECOMMENDATION to the operator, not permission; Ares does not
self-authorise cycle 3 and parks pending the decision (s8).

## 2. GATE A -- substitution (open)

c2_no_recur (recurrence forbidden outright; keep and plasticity legal):
all 10 lineages reach the 40.0 cap. Carrier classes PLAST 6, KEEP 2,
REDUNDANT 1, MIXED:keep+plasticity 1. Cutting recurrence collapses
0/10 (the constraint bound), plasticity 7/10, keep 3/10. Median time to
threshold 20 generations against 10 for the unconstrained control.
    Blocking the preferred carrier costs ten generations and nothing else.
c2_tax_high (0.25 per recurrent edge): median recurrent-edge count 0.0
(control 2.0), classes PLAST 5, KEEP 2, RECUR 2, MIXED 1, still 10/10
at cap. A tax does not merely trim recurrence, it substitutes it -- the
second clause of P6 lost.
W15 (reset events, the true anti-activation world): 10/10 at cap;
plasticity becomes load-bearing in 7/10 while recurrence STAYS
load-bearing in 8/10, and the median recurrent-edge count rises from
2.0 to 9.0. Under attack the lineages did not swap carriers, they built
REDUNDANCY across both (majority class MIXED:plasticity+recurrent 5/10).
NEW_CARRIER (a champion above threshold with no cross-step channel):
0 occurrences anywhere. P10 held; no unenumerated channel exists here.

## 3. GATE C -- transplantable carrier (shut, corrected)

The first gate printout said OPEN with "median recovery 1.0". That used
the BEST donor of nine per host -- a max-of-9 statistic. The operator's
criterion is survival of substantial genomic-context change, so the
per-PAIR number is the right one, restricted to the 59 pairs where
cutting the host's own carrier actually broke it:

    per pair      median recovery 0.02; >= 0.5 in 16/59
    per host best >= 0.5 in 6/8   (the biased statistic)
    edge-aware transplant into naive hosts: portable in 4/9

A carrier restores function in a foreign genome only for a favourable
host-donor pairing, not in general. This is the cycle-1 conclusion
again, now with the edge-aware splice that CAN move an output-node
self-loop, so it is no longer explainable by the old blind spot.
Gate C is SHUT. LEDGER row for the biased statistic.

## 4. GATE B -- why recurrence wins

4.1 All three carriers are individually sufficient. Single-carrier arms
on W4, clean held-out (s6), cap 40.0:
    c1_only_recur  10/10 at cap, median time-to-threshold 10 gens
    c1_only_plast  10/10 at cap, median 17.5
    c1_only_keep    9/10 at cap, median 30   (tail to 90)
    c1_none         0/10, median 2.30        (floor arm: the exclusion
                                              machinery works)
    c1_all         10/10 at cap, median 10   -- identical to the
                   recurrence-only arm: when everything is available,
                   recurrence sets the pace.
So the preference is a SPEED phenomenon, not a capability one.

4.2 Three candidate explanations, two of them killed.
 - INTRINSIC SUPERIORITY: killed before the cycle ran. Hand-built on
   W4, keep scores 33.75 and recurrence 24.56 (DESIGN_C2 s2). The
   carrier evolution never chooses has the better optimum.
 - GRADIENT AT FIRST APPEARANCE (my primary hypothesis, P4): killed.
   Taking a champion, stripping every carrier and applying one mutation
   300 times: mean fitness change is about zero for both carriers and
   the probability of an immediate improvement is 0.00 in four of five
   lineages. Selection does not see an immediate payoff for either.
 - RAW OPPORTUNITY (P3): recurrence is only 1.32x more reachable per
   mutation (0.0487 vs 0.0368), and an 8x mutational subsidy on keep
   raised its creation rate to 0.1767 without flipping the carrier
   (c2_keep_subsidy: RECUR 5, REDUNDANT 4, PLAST 1; keep present at a
   median of 4 nodes but load-bearing in 1/10). P7 held.

4.3 The USEFUL-reachability explanation, and its falsification.
Counting only carriers that are immediately usable changes the picture
sharply: one mutation creates a usable recurrent edge (|w| >= 1) with
p = 0.0173 and a usable keep (>= 0.90) with p = 0.0000 -- zero times in
8000 trials -- because alter_keep steps by N(0, 0.3) from zero and a
working leak needs ~0.9+. That looked like the answer, so it was tested
directly rather than asserted. EXPLORATORY arm c3_keep_reachable
(keep_mut_sigma 1.5, which raises usable-keep creation to 0.0231, ABOVE
recurrence's 0.0173), prediction recorded before the run: keep
load-bearing in >= 3/10.
    RESULT: 2/10. PREDICTION LOST.
    Classes RECUR 8, KEEP 2. The manipulation demonstrably worked at
    the genotype level -- 7/10 champions now carry a keep node at 0.98,
    against effectively none before -- and selection still routed
    function through recurrence.
Reachability is necessary and NOT sufficient.

4.4 What does explain it (EXPLORATORY, post-hoc, hand-wired organisms).
Sweeping each carrier's own parameter and asking how much of the range
still works (ares/runs/sweep_c2/basin.json):
    KEEP  best 33.75 at 0.98; viable in 3/25 swept values, [0.94, 0.98]
          profile 0.90:14  0.96:28  0.98:34
    RECUR best 40.00 at 4.0; viable in 14/23 swept values, [2.75, 6.0]
          profile 3.0:25  3.5:36  4.0:40  5.0:40  6.0:40 (saturates)
Keep is a knife-edge against its own ceiling: it must be loaded AND
held by one scalar, and as it approaches 1 the input term (1-keep)
vanishes, so the working region is a 4%-wide sliver. A self-loop has no
such trade-off -- above a threshold weight, larger is never worse, so
the viable region is wide, flat and open-ended.
Two independent observations corroborate this and were not designed to:
 - c2_recur_unstable (N(0,0.5) jitter added to every recurrent edge at
   every reproduction) did not dislodge recurrence at all: RECUR 7/10,
   and the FASTEST median time-to-threshold of any arm (5 gens). Jitter
   inside a flat basin is harmless. The same jitter applied to a keep
   at 0.98 would leave the viable sliver immediately.
 - keep's time-to-threshold has the long tail (10 to 90 generations)
   expected of a target that must be found AND held, while recurrence's
   is tight (5 to 25).

4.5 The statement this cycle supports.
    A supplied primitive is not "available" to an evolutionary search
    merely because it exists, is usable, and is reachable in one
    mutation. It is available when its VIABLE REGION IS WIDE AND ITS
    GRADIENT FLAT. The substrate routed around design intent because
    the designated carrier's working region was a sliver and the
    undesignated one's was a plateau.
Status: the exclusion, subsidy, step-size and tax arms are
preregistered and at 10 seeds; the basin measurement behind the
explanation is POST-HOC and on HAND-WIRED organisms, so it explains the
evolved result rather than being measured on it. The decisive
independent test is named in s7.

## 5. Correction to cycle 1 (a headline number does not replicate)

Cycle 1 reported, for W4: activation memory load-bearing 10/10,
plasticity 0/10. On ten FRESH lineages with edge- and SCC-aware
attribution, the unconstrained control c1_all gives:
    cutting recurrence collapses  7/10
    cutting plasticity collapses  4/10
    cutting keep collapses        1/10
    classes: RECUR 4, MIXED:plasticity+recurrent 2, PLAST 2,
             MIXED:keep+recurrent 1, REDUNDANT 1
So "plasticity 0/10" does not replicate; plasticity is load-bearing in
about 4 of 10 fresh W4 lineages. Under this cycle's proportions, a
0/10 sample has probability about 0.6%, so the two samples genuinely
differ and I cannot fully explain the gap beyond (a) lineage sampling
and (b) cycle 1's coarser config-level ablation, which could not
separate keep from recurrence and labelled both "ACT". The cycle-2
instrument is the one to trust. The cycle-1 claim that SOME cross-step
carrier is always required does replicate (c1_none 0/10, median 2.30).
The claim that recurrence is the universal carrier does not: it is the
most common one, not the only one.

## 6. Instrument defects found in this cycle's own apparatus

D1 SELECTION ON THE HELD-OUT SET. search.run chooses the final champion
   by argmax over the final population evaluated ON the held-out
   episodes, making `final.heldout` a max-of-128 statistic. Measured:
   the shuffled controls read 4.22 / 13.47 / 1.41 / 1.50 while the
   clean number (the training-selected champion evaluated on held-out,
   already logged every run) is 0.00 / -2.38 / -0.14 / 0.00. Every
   headline in this report sits at the structural cap, which cannot be
   inflated, and ares/recheck_c2.py re-derives every count from the
   clean number. The important consequence is reassuring: with the
   selection bias removed the shuffled controls sit exactly at the
   floor, so the worlds do not leak -- the apparatus did.
D2 BIASED SWAP STATISTIC (s3).
Both are LEDGER rows. Neither changes a disposition except D2, which
changes gate C from open to shut.

## 7. If the operator continues: the three tests that matter

 1. DIRECT TEST OF THE BASIN EXPLANATION, on evolved genomes rather
    than hand-wired ones: re-parameterise keep so its viable region is
    wide (for example store and mutate log(1/(1-keep)), making the
    useful range broad and unbounded like a weight) and re-run c1_all.
    Prediction to record first: keep's share of load-bearing carriers
    rises above recurrence's. This is the falsification that the c3
    arm could not deliver, because c3 fixed reachability and left the
    sliver intact.
 2. BASIN WIDTH AS A PREDICTOR ACROSS PRIMITIVES: measure the viable
    region of every primitive the substrate offers and test whether
    basin width, not expressiveness or reachability, predicts which
    one evolution selects. If it does, this is a design rule for any
    substrate in the program, not a fact about this toy.
 3. WHY REDUNDANCY UNDER ATTACK: W15 produced dual-carrier lineages
    (recurrence load-bearing 8/10 AND plasticity 7/10, recurrent edges
    up 4.5x) rather than substitution. Whether redundancy is selected
    or is a by-product of a harder task is untested and is the only
    result here that pointed somewhere nobody predicted.

## 8. Disposition

Gates A and B open, C shut, so by the operator's rule Ares earns
further work -- as a RECOMMENDATION. The seat parks now and does not
self-authorise cycle 3. The export package is prepared regardless
(s9), so closing the seat costs nothing if the operator prefers it.

Honest summary of what was and was not established: substitution is
established (at cap, 10 seeds, preregistered). The refutations of
intrinsic superiority, gradient and reachability are established. The
basin-width explanation that replaces them is supported but post-hoc
and measured on hand-wired carriers; it deserves the s7.1 test before
anyone builds on it. Transplantability is refuted twice, now with the
instrument that could have detected it.

## 9. Export package (ready whether or not cycle 3 happens)

For Nyx / Theophrastus / SFE, with named consumers:
 - ares/carriers.py: edge- and SCC-aware carrier attribution, carrier
   taxonomy, mutational-opportunity and basin measurement, edge-aware
   transplant and swap. Reusable against any graph-structured organism.
 - ares/PRESSURE_CATALOG.json: 12 built pressures with falsifiers, 6
   candidates never built.
 - ares/worlds.py: 16 batched toy worlds with present/absent/shuffled
   modes and per-world balanced held-out seeding.
 - The design rule of s4.5, as a hypothesis for other substrates.
 - Two instrument warnings that generalise: never select the reported
   champion on the held-out set (D1); never score a transfer claim with
   a best-of-N statistic (D2).
