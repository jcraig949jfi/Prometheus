# AUTHORED CURRICULUM ANALYSIS

The adversarial test the assignment names as most important: is the observed acceleration
a general change in evolvability, or a specialisation to the decomposition deliberately
embedded in the training environments?

The historical programme answers this question against itself. The decisive evidence is
the authors' own null result, and it has been verified verbatim from the publisher XML.

================================================================================
1. THE DECISIVE QUOTATION
================================================================================

  "We find that MVG's outperformance occurred only toward goals within the modularity
   language. MVG adaptation toward non-modular goals was not significantly different
   from FG's (Figure 6E)."

  "In competition experiments between FG and MVG genomes toward novel-module goals,
   populations were taken over by MVG-genomes in about 70% of the runs (Figure 6D inset).
   In experiments toward randomly chosen goals, populations had equal chance to be taken
   over by either FG or MVG genomes (Figure 6E inset)."

The non-modular comparison goals were difficulty-matched, verbatim: "Goals with a
difficulty level similar to that of (D) were chosen, as evaluated (Text S1 section 6.2)."
So the null is not an artifact of the random goals being harder. The authors closed that
loophole themselves.

An earlier automated reading of this paper rendered this result as MVG being "as slow, or
even slower" than FG on random goals. That is wrong and it matters: the true result is a
clean null, not a reversal. Overstating it would have manufactured a lock-in cost that the
data do not show. Recorded in PRIMARY_SOURCE_LEDGER.md as correction 1.

================================================================================
2. VERDICT ON THE DISTINCTION THE ASSIGNMENT DEMANDS
================================================================================

STRUCTURAL_GENERALITY vs CURRICULUM_MATCHING
  -> CURRICULUM_MATCHING, decisively, at the level of the composition scheme.
  The advantage is switched on and off by whether the test goal parses under the
  experimenter's template. That is the definition of matching to an authored structure.

RECOMBINATION_OF_KNOWN_SUBPROBLEMS vs ACQUISITION_OF_NOVEL_FUNCTIONAL_DIMENSIONS
  -> Neither, cleanly. This is where a lazy reading goes wrong in the harsh direction.
  The novel-module experiments are NOT pure recombination: a previously unseen 2-input
  Boolean function (AND, NOR) replaces a XOR module, and MVG organisms still acquire it
  faster, winning ~70% of competitions. New CONTENT is acquired more cheaply. What is
  never acquired more cheaply is a new SCHEME.
  The precise statement: MVG buys cheap acquisition of novel content within a fixed
  compositional slot structure, and buys nothing outside that structure.

That middle position is the actual finding and it should not be collapsed in either
direction. Calling it "just recombination" understates it. Calling it "general
evolvability" overstates it by the width of Figure 6E.

================================================================================
3. THE SEVERITY OF THE AUTHORSHIP, QUANTIFIED
================================================================================

For the canonical circuit family:
  authored language     u(x,y,w,z) = f(g(x,y), h(w,z)), g,h in {XOR,EQ}, f in {AND,OR}
  language size         8 goals by construction; "all six Boolean goals studied"
  full phenotype space  4-input 1-output truth tables = 2^16 = 65,536
  fraction authored     ~1e-4 of the phenotype space
  advantage exists      inside that fraction only

The input partition ({x,y} against {w,z}) is fixed by the experimenter for every run in
every condition and is never itself varied, never discovered, and never tested. A system
that had genuinely learned "how to be modular" would be expected to transfer to a family
built on a DIFFERENT partition -- say f(g(x,w), h(y,z)). That experiment does not exist in
the retrieved record. It is the single cheapest test that would separate
"learned this decomposition" from "learned to decompose", and nobody ran it.

Registered as a composition-candidate experiment in CANDIDATE_COMPUTATIONAL_PARTS.jsonl.

================================================================================
4. THE COUNTER-ARGUMENT, TAKEN SERIOUSLY
================================================================================

The strongest defence of the programme against the authored-curriculum charge, which must
be stated before it is answered:

  (a) The objective contains no structural term. Fitness is agreement with a truth table.
      The system is never rewarded for modularity, for reuse, or for evolvability. The
      structural outcome is emergent under selection for function alone. That is a real
      and non-trivial result and no amount of curriculum criticism touches it.
  (b) Natural environments plausibly ARE modularly varying in this sense. If the claim is
      about biology rather than about open-ended machines, an authored decomposition that
      mirrors a real ecological regularity is a feature, not a confound.
  (c) The effect is substrate-general: five model systems in 2007, two in 2008, six
      Boolean goals and five RNA structures. It is not an artifact of one encoding.

The answer: all three are granted, and none of them addresses the boundary. (a) shows the
MECHANISM is emergent. (b) shifts the claim to a biological one, which is fine for biology
and inert for a machine intended to acquire dimensions nobody specified. (c) shows
robustness ACROSS SUBSTRATES while Figure 6E shows fragility ACROSS GOAL FAMILIES, and it
is the second axis that Prometheus cares about. Robustness to encoding and boundedness to
curriculum are compatible, and here both are true simultaneously.

================================================================================
5. WHAT THIS MEANS FOR PROMETHEUS WORLD DESIGN
================================================================================

The Incubator concern -- worlds should expose opportunities for qualitatively new
machinery without encoding the reasoning ladder itself -- is validated by this specimen as
an empirical hazard rather than a theoretical worry. Here is a world whose latent
decomposition was written by the experimenter; a system exposed to it acquired a genuine,
measurable, longitudinally-tracked change in its variation distribution; and that change
paid off ONLY on targets drawn from the same author's template.

The design rule this licenses, stated so it can be tested rather than admired:

  A world that supplies its own decomposition will produce systems that mirror that
  decomposition and will not distinguish mirroring from discovering. To make the
  distinction measurable, the held-out target family must be generated by a
  DIFFERENT decomposition than the training family -- different partition, different
  arity, or different slot topology -- and the transfer test must be run against that,
  not against new fillers in the same slots.

Kashtan/Alon ran the within-scheme version of this test and reported the honest result.
Prometheus must run the across-scheme version, and should expect, on this evidence, a
null. Designing so that the null is informative is the actual work.
