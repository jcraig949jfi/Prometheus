# REPRESENTATION LOCK-IN ANALYSIS

The Prometheus concern: a successful early representation may create a later ceiling. A
mechanism that raises evolvability along one basis while lowering orthogonal accessibility
is a local evolvability attractor, not open-ended improvement.

This file separates what the historical data show from what they merely permit.

================================================================================
1. WHAT MVG DEMONSTRABLY INCREASES
================================================================================

  modularity            Q_m 0.12 -> 0.54 (circuits), 0.15 -> 0.35 (neural)
  adaptation speed      95x to 700x on the hardest goals, five substrates
  reuse                 adaptation to a previously seen goal in 1-2 mutations, often
                        within a single generation
  neighbourhood quality FV measure rises significantly faster than FG over generations
  intra-module effect   0.12 -> 0.14 (circuits, p<1e-4); 0.28 -> 0.36 (RNA, p<1e-9)
  modular independence  pleiotropy 0.04 -> 0.01 in circuits (p<1e-4)

================================================================================
2. WHAT THE DATA SHOW ABOUT THE COST -- AND WHAT THEY DO NOT
================================================================================

The honest answer is narrower than the Prometheus hypothesis wants, and stating it
correctly is the point of this file.

MEASURED: on goals outside the modularity language, MVG organisms perform NO WORSE than
FG organisms. Verbatim: "MVG adaptation toward non-modular goals was not significantly
different from FG's." Competition on random goals: "populations had equal chance to be
taken over by either FG or MVG genomes."

So the historical record shows a NULL, not a penalty. The advantage vanishes outside the
authored family; it does not invert. No measured ceiling.

This matters because the tempting narrative -- specialisation buys local speed at the
price of general reach -- is NOT what was observed. The observed shape is:

  inside the authored family    large advantage
  outside it                    parity

An earlier automated reading of this paper claimed MVG was "as slow, or even slower" than
FG on random goals, which would have been direct evidence of lock-in cost. That reading is
wrong; see PRIMARY_SOURCE_LEDGER.md correction 1. This review declines to build a lock-in
finding on a sentence the source does not contain.

================================================================================
3. WHERE LOCK-IN EVIDENCE ACTUALLY DOES APPEAR
================================================================================

Three real signals, none of them a fitness ceiling:

L1. THE GAIN IS NOT RETAINED. The clearest lock-in-adjacent result runs the opposite way
    from the usual worry: the acquired property DECAYS when the environment stops
    supplying structure. "Facilitated variation rapidly decays when goal becomes constant
    over time" (2008, Fig 9D), and modularity decays "within a few tens of generations"
    under a fixed goal (2005, Fig 3). The representation is not a ratchet and not a
    trap. It is a maintained state.
    Implication for Prometheus: this mechanism cannot by itself produce compounding. A
    property that dissipates when the pressure is removed cannot accumulate across
    epochs unless something else holds it.

L2. DIRECTIONAL, NOT SCALAR, RESTRUCTURING. Reduced pleiotropy means mutations are
    confined within module boundaries. That is by construction a restriction on the
    mutational move set relative to the authored partition: cross-module coordinated
    change becomes rarer. Any target requiring simultaneous coordinated change ACROSS the
    authored boundary is, mechanically, harder to reach. The programme never tested such
    a target, so the predicted cost was never measured. This is the strongest theoretical
    case for lock-in in the corpus and it is UNTESTED, not established.

L3. SUBSTRATE-DEPENDENCE OF THE MECHANISM. RNA showed enhanced intra-module effect but
    NOT significantly reduced pleiotropy (NS in Table 1), and the RNA model showed no
    significant FG/MVG difference on novel-module goals. The mechanism that would produce
    lock-in (pleiotropy reduction) is exactly the one that failed to replicate across
    substrates.

================================================================================
4. THE UNRUN EXPERIMENT THAT WOULD SETTLE IT
================================================================================

Lock-in as a claim requires a target class chosen ADVERSARIALLY against the authored
partition, not a random one. Random truth tables are not adversarial; most of them are
simply hard for everyone, which is why the comparison lands on parity.

  the right test: construct goals that are EASY in absolute terms but require coordinated
  change across the authored module boundary -- for example a goal whose natural circuit
  shares a subexpression between the {x,y} and {w,z} halves. Difficulty-match to the
  within-language goals using the paper's own procedure (Text S1 6.2). Then compare MVG
  and FG.

  prediction if lock-in is real: MVG is SLOWER than FG here -- the first inversion in the
  corpus. Reduced pleiotropy is a liability when the target needs pleiotropy.
  prediction if lock-in is not real: parity again, and the mechanism is purely additive.

Until that is run, this review records:

  REPRESENTATION LOCK-IN: NOT DEMONSTRATED, NOT EXCLUDED, AND THE DISCRIMINATING
  EXPERIMENT WAS NEVER RUN. The corpus contains parity outside the family, decay of the
  property when structure is withdrawn, and a mechanism (pleiotropy reduction) whose
  logical consequence is a cost that nobody measured.

================================================================================
5. LOCAL EVOLVABILITY ATTRACTOR -- VERDICT
================================================================================

On the evidence, MVG produces a MAINTAINED, DIRECTIONAL, NON-COMPOUNDING change in the
variation distribution, aligned to an externally supplied basis, with no measured cost
along orthogonal directions and no measured benefit there either.

That is best described not as an attractor with a ceiling, but as a MIRROR: the genotype
comes to reflect the structure the environment keeps presenting, holds that reflection
only while the environment keeps presenting it, and gains nothing where the environment
was silent. Whether a mirror can be made to compound -- by making its own reflection part
of the next environment -- is precisely the composition question in
CANDIDATE_COMPUTATIONAL_PARTS.jsonl, and it is not answered anywhere in this lineage.
