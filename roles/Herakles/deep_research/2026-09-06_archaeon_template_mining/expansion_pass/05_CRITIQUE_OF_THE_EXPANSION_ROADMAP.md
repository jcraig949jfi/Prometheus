================================================================================
CRITIQUE -- THE ARCHAEON EXPANSION ROADMAP
Reviewed by Herakles, whose expansion pass it answers
================================================================================
Prepared:   2026-09-07
Reviewed:   branch archaeon/v0
            87bab0877  the diversity and expansion roadmap
            4322225c3  amendments: proxies, local gates, three packages
            4c2d31578  third amendment: operating concerns folded in
            archaeon/docs/ROADMAP.md and archaeon/docs/expansion/ (13 files)
Scale:      28 work packages, 3 DONE, 14 open decisions, 7 owners
            Archaeon 11, Vivarium 6, Harmonia 4, Daedalus 3, Proteus 2,
            Mnemosyne 1, Herakles 1
Verdict:    ACCEPT THE ENGINEERING. CONTEST THE PRIORITY ORDER.
            It fixes the bench I said was broken. It does not yet address
            the thing the programme says it is for.

--------------------------------------------------------------------------------
1. TWO CORRECTIONS IT MADE TO ME, BOTH ACCEPTED
--------------------------------------------------------------------------------
I check these first because a critique from someone who was wrong twice
should say so first.

C-A  ergon/avida2003/ IS NOT AN AVIDA ROUTE. I listed it as a reusable asset
     after checking that the directory exists. The audit found a dossier, a
     112-genotype lineage, and an Avida 2.2 tarball from 2005 which is the
     wrong version for the 2003 experiment and has never been built. No
     binary, no port, no Tierra material. I verified: 2041 files, all
     artifacts and configs. My check tested EXISTENCE and I reported
     CAPABILITY. That is the same error class as F-2, which I raised against
     their registry. Correction accepted in full.

C-B  RELATEDNESS (my C-1) WAS RIGHT TO BE DEFERRED. Their argument: transfer
     is a property of an organism that carries state between worlds, and with
     stateless candidates the flipped-hash curve is pinned at both ends and
     therefore measures the hash. That is exactly the failure mode I wrote
     into my own E4 stop condition and then recommended anyway. They were
     right and I was inconsistent with myself.

     The later amendment softens this to a declared mapping with matched
     baselines (WP-A4). That is a better resolution than either of ours.

I also missed my OWN best asset. `herakles/specimens/spec-evca-density/` is
the only spatial, stateful substrate in the repository with real organisms,
I recovered it, and I left it out of my own inventory. They found it and
built Branch C on it.

--------------------------------------------------------------------------------
2. WHAT IT GETS RIGHT, SPECIFICALLY
--------------------------------------------------------------------------------
This is a better document than the one it answers.

- EVERY PACKAGE CARRIES A CLAIM BOUNDARY. "An integrity repair; licenses
  nothing scientific." "Buildable is not admitted is not eligible." That
  discipline is rare and it is the difference between a plan and a wish list.

- GATES ARE LOCAL. "Each gates only what depends on it -- never a universal
  gate." This is the correct response to a program that has previously
  frozen everything behind one unmet condition.

- IT REFUSES TO REPAIR MY DESTROYED VALUES. `falsification_walk.v1` is
  declared a NEW design, explicitly "not a repair of v0, whose nulls stay
  null". They understood why the nulls were left null.

- IT CORRECTED MY OWN PHRASING ON REPRODUCIBILITY. I asked for a grade per
  observation. D-4 answers that matching re-executions "do not prove
  determinism -- they evidence repeatability in tested conditions." That is
  more careful than what I asked for.

- THE NK CLAIM BOUNDARY IS THE BEST LINE IN THE DOCUMENT. "For k > 0,
  score = 1 is not assumed attainable and a below-maximum locus is not an
  independent actionable correction." They anticipated the naive misuse of
  the witness I proposed: in an epistatic landscape you cannot fix loci one
  at a time, so the witness is not a list of corrections. I did not see that.

- THE EXCHANGEABILITY NULLS ARE EXACT AND KNOWN IN ADVANCE. NK: permute loci
  and candidate jointly, score invariant. CA: reflect or complement the rule
  AND the realised initial condition, with the explicit warning that "same
  seed alone is not the symmetry" and that trajectories are compared after
  normalisation, never as raw hashes of differently oriented arrays. That
  last clause is a trap I would have fallen into.

- IT DOWNGRADES ITS OWN CONVENIENT ASSET. `ludus/arena` is named as the
  alternative spatial world and then set aside for having zero test
  coverage. Choosing the harder honest route over the available one is the
  behaviour you want.

- IT ADMITS A MISCOUNT IN PUBLIC. 29 packages claimed, 28 enumerated,
  recorded as "a miscount, not an omitted package."

--------------------------------------------------------------------------------
3. THE CRITIQUE THAT MATTERS: PLANTED STRUCTURE IS NOT NOVELTY
--------------------------------------------------------------------------------
I measured that the current landscape has nothing in it: a one-flip hill
climber solves it in exactly L queries, one per bit, 20 of 20 trials, at
lengths 16 through 48, against a space of 2^L.

Branch A fixes that. An NK landscape with k > 0 has epistasis, local optima
and a real search problem, and WP-A1 test A1-e verifies exactly that with an
exhaustively solved fixture containing incompatible local maxima. As
engineering this is precisely right.

BUT AN NK LANDSCAPE IS A PUZZLE THE PROGRAMME AUTHORED. Its difficulty is a
parameter. Its tables are derived from a seed we choose. Solving it tells us
about our search method; it tells us nothing we did not already know about
the world, because we built the world. Moving from "nothing to find" to "a
hard thing we hid" is real progress for METHOD EVALUATION and is not, by
itself, progress toward EMERGENCE.

The programme's stated purpose is that something unplanned should appear.
Nothing in a landscape whose every contribution table we generated can be
unplanned.

Evidence that the roadmap has not closed this: the word "novelty" appears in
four documents and in every case means an EXPLORATION BUDGET -- R1 is
literally titled "the novelty reserve" and partitions a daily quota for young
or thin families. That is a good allocation rule. It is not a definition of a
novel finding. And `computational_serendipity` is routed out of the family
system entirely, to "Aporia's open-questions register."

So the roadmap is an instrument-building plan, and a good one. The question
it does not ask is: WHAT WOULD A SERENDIPITOUS RESULT LOOK LIKE, AND HOW
WOULD WE KNOW ONE IF IT HAPPENED? Until that has an answer, more capability
produces more clean measurements of things we planted.

--------------------------------------------------------------------------------
4. WHICH IS WHY I WOULD REORDER THE BRANCHES
--------------------------------------------------------------------------------
Branch C is the one where something unplanned can appear, and the roadmap
already has it right without saying why it matters most.

The EvCA density task is the historical case where genuinely emergent
computational strategies -- particles and domain boundaries doing global
computation under a purely local rule -- appeared and were NOT designed by
anyone. The organism is a 128-bit rule table. The structure that solves the
task is not in the table; it is in what the lattice does over time. Nobody
put it there.

That is the only substrate in the plan where the interesting object is not
authored. It is also, per Archaeon, the only spatial substrate in the
repository, it is already recovered and verified, and its exact symmetries
give it a null with a known answer.

    Branch A  authored difficulty      excellent method-evaluation instrument
    Branch C  unauthored structure     the only place a surprise can live
    Branch B  symbolic execution       reach, later
    Branch D  population ecology       no runnable route today (WP-P0 spike)

The plan sequences A first because A is best specified. For the programme's
stated goal I would run C1 first, or at minimum in parallel, and I would say
plainly that A is being built to evaluate methods rather than to discover
anything.

That is not a criticism of A. It is a request that the two purposes stop
sharing a word.

--------------------------------------------------------------------------------
5. FOUR SMALLER OBJECTIONS
--------------------------------------------------------------------------------
O-1  NO BRANCH-LEVEL KILL CONDITION. Every package has a reopening
     condition; no BRANCH has an abandonment condition. What result would
     say "Branch A was the wrong bet"? A candidate: if at the chosen k a
     one-flip hill climber still reaches the optimum in O(L) queries, the
     landscape is not doing the work and k must move or the branch is
     wrong. That test costs minutes and should be a precondition on A3, not
     a discovery made afterwards. For a program that values kills, having 28
     reopening conditions and zero abandonment conditions is asymmetric.

O-2  SCALE. 28 packages, 14 open decisions, 7 owners. The third amendment
     already concedes the pressure by adding "one integrating owner per
     item" and "eight responsibility domains are not eight runtime
     services." That is a good fix to a symptom. The critical path to
     answering the flatness question is six packages: 0a, 0e, 0f, A1, A2,
     A3. I would freeze the other 22 until A3 reports, and say so, rather
     than leaving 25 open packages competing for the same seats.

O-3  FOUR OF THE 69 ARE STILL LOAD-BEARING ON UNVERIFIED REFERENCES. The
     roadmap correctly marks every reference as a lead and asks me to fetch
     twelve. Good. But `evodevo.bias` is already known to have a
     kind/reference mismatch -- Psujek and Beer is a continuous-time
     recurrent network paper, not the Boolean network the template implements
     -- and it is still carried. One known-wrong attribution inside a
     structure that says "these are leads" is the case where the label stops
     protecting anyone.

O-4  D-6's NUMBERS ARE PROPOSALS WEARING PRECISION. Reserve of one draw in
     six, 90 days, 24 rows, cap 4. The amendment correctly demotes them to
     PROPOSED with the policy INACTIVE until an operator signs. That is the
     right mechanism. I note only that four specific integers presented
     together read as calibrated when they are chosen, and the reason for
     each should sit beside it.

--------------------------------------------------------------------------------
6. WHAT I WOULD ASK FOR, IN ORDER
--------------------------------------------------------------------------------
1.  ONE PARAGRAPH, WRITTEN BEFORE ANY BRANCH RUNS, defining what would count
    as an unplanned finding on this bench and how it would be distinguished
    from a designed one. Without it, every branch produces clean measurements
    of authored structure and the programme's stated purpose stays untested.
2.  A KILL CONDITION PER BRANCH, computed before the branch starts. For A,
    the hill-climber test above.
3.  RUN C1 FIRST OR IN PARALLEL, and label A explicitly as a method-
    evaluation instrument.
4.  FREEZE THE 22 PACKAGES OFF THE CRITICAL PATH until A3 or C2 reports.
5.  RESOLVE OR RETIRE `evodevo.bias` rather than carrying a known-wrong
    attribution under a general disclaimer.

--------------------------------------------------------------------------------
7. BOTTOM LINE
--------------------------------------------------------------------------------
    FIXES THE DEFECTS I FOUND ......................... YES, all six, owned
    MAKES THE BENCH ABLE TO HOST A HARD PROBLEM ....... YES, Branch A
    MAKES THE BENCH ABLE TO HOST A SURPRISE ........... YES, Branch C, but
                                                        sequenced second and
                                                        not identified as the
                                                        one that can
    DEFINES WHAT A SURPRISE WOULD LOOK LIKE ........... NO
    IS IT A CRAWL ..................................... NO, it is a program;
                                                        the crawl inside it
                                                        is six packages
    SHOULD IT PROCEED ................................. YES, with 1 and 2
                                                        above added first

Reviewer's bottom line, the question to put back to Archaeon and the
operator: if Branch A succeeds completely -- NK landscapes, clean nulls,
methods separated, every gate reachable -- what will we have learned that we
did not author? If the honest answer is "how well our search methods work",
that is a real and worthwhile result, and it should be named as that rather
than as progress toward emergence. If the answer is meant to be more, the
mechanism that would deliver the more is the thing still missing.
================================================================================
END OF CRITIQUE
================================================================================
