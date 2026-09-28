REPORT -- random-inflow ecology: liberation vs acquisition of dependence
========================================================================

1. WHAT I SET OUT TO TEST
-------------------------
The program has a built but never-run random-inflow ecology (archaeon/rie/,
committed 87f51c5ee, unchanged through origin/main 6ff2b2f8a). Random 32-byte
tapes keep arriving into a 128-cell world. The observatory is meant to measure
two things. (a) Do lineages evolve OUT of dependence ("liberation": a founder
that copies exactly only at some input bytes leaves a dominant descendant that
copies exactly at more inputs, or at all of them) or INTO it ("acquisition": a
copier founder whose dominant descendant is a non-copier that is mostly
reproduced by other executors)? What are the unbiased rates of each? (b) Is
copier emergence under continuous inflow common, merely possible, or invisible?
The full campaign (96 cells, about 100 CPU-hours for wave 0 alone) cannot fit a
1 CPU-hour budget. So I asked a narrower question: with the committed data and a
pilot, can this instrument estimate those rates at all, and does it measure what
it claims?

2. WHAT I DID
-------------
Code: exported archaeon/{rie,lineage,envgate,z80atlas} and proteus/foundry at
origin/main 6ff2b2f8ad035d50aaf21d9f3b60e16c556683f2 into src/. There is no diff
from 87f51c5ee in any file the instrument hashes. I ran everything with
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE PYTHONPATH=src.
Data: archaeon/envgate2/RESULTS.json and PREREG.json @ 6ff2b2f8a. These are the
committed per-lineage records of the environmental-gating assay: 24 blocks,
2048 chambers x 512 refills = 1,048,576 random arrivals per world, vmcopy32,
well-mixed. Its uniform-input arm is the same physics as the ecology's
IID/STRONG/WELL_MIXED/vmcopy cell.
Scripts (all in /home/jcraig/artemis-selftest/work/R-33):
 - tp.py         throughput probe (IID/STRONG, T=400, both substrates; ruler cost)
 - mutscan.py    for each of the 28 distinct founder tapes of the 39 established
                 lineages in the committed gating-assay records: 400 random
                 single-byte mutants (seeded), each classified by the frozen
                 copier ruler (archaeon/envgate/ruler.measure). I recorded whether
                 each mutant gains exact-copy inputs, loses them, or stops being a
                 copier. Output: out/mutscan.json; summary: summarize_scan.py
 - pilot.py      one real ecology world, run_world(IID, STRONG, WELL_MIXED,
                 vmcopy, seed 0) with T=4096 (out/pilot_s0_T4096.json). A T=16384
                 attempt was lost when its wrapper was killed at about 20 CPU-min
                 before it finished.
 - ctl.py        the campaign's own four control worlds, controls(0).
 - I also ran small inline analyses over the gating-assay records: Garwood
   rates, lineage lifetimes, and snapshot capture.

3. RESULT
---------
(a) Emergence rate (from committed data, not new runs). In the uniform arm there
were 24 genetic establishments over 25.2M random arrivals: 0.95 per million
arrivals (95% CI 0.61-1.42). Of these, 13 had exact-gated founders, 9 had
near-copier founders and 2 had ungated exact-copier founders. In 3 of 24 worlds a
lineage took over (the same founder in every arm of the block). This agrees with
the earlier census sizing of about 7e5 tapes per surviving lineage. Under
continuous inflow, copier emergence in vmcopy32 is therefore "possible, about 1
per 1e6 arrivals" and not common. By the census it is invisible in the z80
substrate. Projected to the staged design: a STRONG world gets 520,192 arrivals
(about 0.5 establishments), a REPLACE world 65,024 (about 0.06) and a BELOW world
8,128 (about 0.008). The whole wave 0 would yield roughly 30-36 establishments,
nearly all in the 16 vmcopy STRONG cells, and about 18 of them exact-gated.

(b) Liberation is mutationally inaccessible. Every exact-gated founder (13 of 13)
copies exactly at input 128 only. Their single-byte mutants: 0 of 5200 gained any
exact input (95% upper bound 5.8e-4 per mutant); 22.1% became non-copiers; 0.9%
stayed copiers but lost the exact input; 76.5% kept exactly {128}. Near-copier
founders (0 exact inputs) gained a gated exact input in 2.0% of mutants (90 of
4400), always to a gated set and never to all 256. The instrument does not count
that transition as either liberation or acquisition. Ungated founders: 0 of 800
mutants widened (they cannot), 18.6% became non-copiers. Transient established
lineages have about 70-400 births and a maximum genetic generation of about 10-13.
At copy noise 0.004 per byte that gives roughly 10-50 mutant births per lineage.
So the chance that such a lineage even produces a liberating mutant is well below
about 0.03, before it would also have to become dominant. Expected liberation
events in the whole wave 0: well below 1. Acquisition also needs hosted births to
exceed self births over the lineage's life. That held for 1 of 39 established
lineages in the committed records.

(c) Instrument defects found:
 1. Missed snapshots become "novel mechanisms". The dominant genome is read only
    from snapshots every 500 epochs, and only glins with at least 5 members count.
    Transient established lineages live about 250-670 epochs. When no snapshot
    catches them, dominant_class is None, and the mechanism rule falls through to
    UNCLASSIFIED_REPRODUCTIVE_MECHANISM. world_score scores that +2 as a novelty,
    and the adaptive lane allocates on it. In the pilot, the only established
    lineage (an ordinary exact-gated {128} copier, alive at epochs 1152-1489, 71
    births) was labelled exactly this way, and the world scored 3.0. In the
    committed gating-assay records, 7 of 25 transient establishments have no
    snapshot-epoch observation with at least 5 members. So about a quarter to a
    third of all establishments would be mislabelled. For the same lineages,
    liberation and acquisition are forced to False, because the dominant class is
    None.
 2. Takeover has no minimum population. Takeover is ">= 90% of occupied cells" at
    any population size. The pilot logged 4 takeover observations by glins with
    9 or fewer births (and one with fewer than 3) while the ecology was nearly
    empty. The takeover counts in tier-1 rates would be inflated.
 3. Docstring and code disagree. The docstring defines liberation as "... or early
    hosted -> later self". The code implements only the ruler-based branch, so the
    hosting route to liberation is never counted.
 4. The dependency map is incomplete. Near-copier to gated-exact (the only widening
    of exact copying that is mutationally common, 2%) is not counted as anything.
Items that worked: the exposure accounting was exact (126,976 arrivals as
expected), and all four campaign controls passed (positive, laundering,
host-mediated, negative).
Cost facts: a STRONG vmcopy world costs about 0.11 CPU-s per epoch once it is
populated, so about 30 CPU-min at T=16384. The controls cost about 14 CPU-min per
wave. Wave 0 is of order 100 CPU-hours.

Plain conclusion: As staged, the instrument cannot answer the liberation vs
acquisition question. Its liberation events are essentially unreachable in this
substrate, because gated copiers are all {128}-only and no single mutation widens
them. Its classification of established lineages is biased by the snapshot
cadence toward a spurious "unclassified mechanism" label. Its takeover metric
counts near-empty worlds. Copier emergence under inflow is possible but rare,
about 1 per million arrivals in vmcopy32.

4. DID IT RESOLVE THE QUESTION
------------------------------
Partly. I did not measure the unbiased liberation and acquisition rates: that
would need the campaign, at about 100 CPU-hours or more. What I did show, with
committed data plus a pilot, is that the question is badly posed for this
instrument. For the expected yield of the planned design, the rates would come
out as zero or near zero with wide upper bounds. For mechanistic reasons,
liberation is close to structurally impossible in vmcopy32. And the observatory
has a labelling defect that would contaminate the headline "novel mechanism" and
the takeover outputs. The emergence sub-question is answered from existing data
(rare-but-possible, about 1e-6 per arrival).

5. CONSEQUENCES
---------------
- Instrument defects, which the owning seat (Archaeon, archaeon/rie/world.py)
  should fix before any freeze:
  (i) get the dominant genome from the lineage's own record, or snapshot on
  establishment, instead of the 500-epoch cadence. Never let a missing
  observation fall through to UNCLASSIFIED_REPRODUCTIVE_MECHANISM; use an
  explicit UNOBSERVED class that scores 0.
  (ii) require a minimum occupied population (e.g. the core's MIN_POP = 32) for
  takeover and coexistence.
  (iii) implement the hosted-to-self branch of liberation, or delete it from the
  docstring.
  (iv) add NEAR -> EXACT_GATED ("acquiring exact-copy gating") as a counted
  transition. It is the common one.
- False premise: the premise that liberation and acquisition rates are estimable
  from an unbiased lane of this size. For liberation, a mutational-neighbourhood
  scan (as done here, about 15 CPU-min) is a cheaper and more informative
  instrument than an ecology campaign. It says that no single-step path from
  {128}-gated to wider gating exists.
- Reproduction of something already known: the inflow establishment rate
  (about 1e-6 per arrival) matches the census sizing.
- No new positive result. Who should know: Archaeon (owner of the ecology and
  lineage core), and whoever decides whether to unpark this experiment. As staged,
  its promotion score would chase mislabelled ordinary gated copiers.

6. COST
-------
Wall time about 1.3 h of my work. CPU: about 57 CPU-min in total (throughput probe
1, lost full-length world attempt about 20, mutational scan 13.4, T=4096 pilot
world 7.7, controls 14.3), with at most 2 processes and a peak RSS of about
450 MB. What I could not do: run any full-length (T=16384) world to completion,
any non-IID regime, the GRID topology or the z80 substrate, or any part of the
actual campaign. The mutational scan sampled 400 of 8160 single-byte mutants per
founder and looked at single mutations only, not multi-step paths.
