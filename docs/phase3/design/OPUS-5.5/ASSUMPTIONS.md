# Assumptions -- OPUS-5.5 (Epimetheus)

Every major assumption the proposal depends on, with what it supports, how it could be checked, and what changes if it
is false. Grouped by layer. "Check" names the experiment or measurement that tests it (X-ids in ENGINE_PORTFOLIO.md).

## A. About the historical record

    id   assumption                                            supports                         check / if false
    A1   The four intake packages plus the twelve reader       the failure taxonomy, the        verifiers covering 10 of the 12
         digests characterise the historical apparatus well    binding-constraint ranking       digests checked 100 sampled
         enough to rank its binding constraints                (RSE s1)                         load-bearing claims (82
                                                                                                confirmed, 18 partial, 0
                                                                                                refuted) and logged 92 further
                                                                                                reader errors (verification.
                                                                                                jsonl, READER_ERROR); idx and
                                                                                                ext were not verified; if wrong,
                                                                                                the ranking weakens [A]
    A2   [A] The binding constraints were, by X0 cheapest      instrument priority (E1, E2     X0 supports the ranking but
         repair, ruler validity, provenance/implementation,    first) and many certified        cannot decide the substrate
         world demand and statistics, with search and same-    worlds                           count (non-discriminating);
         substrate capacity at 5% each and independence 2%                                      X0b, X10b, X1c and X11 test the
                                                                                                single-primary choice
    A3   Claude-family crawlers, readers and verifiers share   discounting of this package's    a cross-family re-derivation of
         blind spots with the Claude-family program            own reading (stated, not         X0 and of the salvage matrix;
                                                               corrected)                       if it disagrees materially, revise
    A4   Host-local and off-repo evidence (M2 ledgers, BEE     treating those results as        custody audit; recovered
         raw results, Icarus cycles, off-repo code) would not  UNKNOWN rather than as support   evidence could upgrade a few
         reverse the overall picture                                                            historical results

## B. About organisms and substrates

    B1   A graph of small register machines with              the DGM as primary substrate     X4 capacity and developability
         developmental instructions can express the target    (RSE s3)                         proofs; if not, replace the
         capabilities (keyed binding, hidden-state tracking,                                    primary substrate
         procedure reuse, self-modified learning rules)
    B2   The union of affordances does not inflate needle     search on the full lattice       X6; > 100x inflation fires the
         sizes beyond reach of CPU-bounded search                                               substrate trigger
    B3   Affordances can be implemented as switches on one    single-factor lattice contrasts  regression-hash gates in CI; if
         bit-identical code path                              (ORG-20)                         impossible, contrasts need
                                                                                                separate kernels and lose
                                                                                                causal cleanliness
    B4   Capacity proofs can be compiled or found by search   affordable ORG-14/DEV-13         X9 build receipt; if each proof
         at modest cost, so hand-writing is not required                                        costs > ~5M tokens, scope proofs
                                                                                                to fewer triples
    B5   Unfamiliar mechanisms, if any, will appear at the    tolerating a familiar computing  second substrate on triggers; E8
         level of organisation, not of the substrate's        ontology at the primitive level  familiarity measurement
         primitives
    B6   One CPU-trainable reference learner per family is    replacing three references       if L2 comparisons with familiar
         enough as a familiar control in year one                                               architectures arise, add the
                                                                                                transformer reference (AGR-08)

## C. About development and pressure

    C1   The developmental thesis (that what an organism can  E4-E6 and the developmental      X5 and E4; if structural
         become is a better object than what it does) is      control set                      development never beats the
         testable at CPU scale with small worlds                                                frozen controls with proofs
                                                                                                present, the thesis is reframed
    C2   The adaptive gap and payback ratio capture when      PRS-01, E3                       X1a; if transitions do not track
         development pays well enough to predict transitions                                    Delta and rho in two substrates,
                                                                                                the pressure theory is wrong
    C3   P3b-type sequences can be generated with a           E6 being phenomenon-level         F9 certificate construction; if
         certificate that fixed meta-rules fall behind                                          impossible, recursion nulls
                                                                                                remain apparatus-typed
    C4   Write-order tagging is feasible in the DGM without   the recursive-sagacity           DEV-14 qualification on planted
         prohibitive overhead                                 definition                        writers; if infeasible, E6 is
                                                                                                RECURSION_UNTESTABLE
    C5   Lifetimes long enough for development (>= 3x the     developmental nulls being        WLD-18 measurements; if
         developable genome's acquisition time) fit the CPU   interpretable                    unaffordable, developmental
         envelope                                                                               claims are limited to shorter
                                                                                                acquisition families

## D. About worlds and measurement

    D1   Small exactly solvable or exactly bounded POMDP       the depth certificate and the    X2 [A]; if certificates do not
         families can carry genuine cognitive depth            world forge                      beat the best proxy in
                                                                                                predicting held-out learner
                                                                                                performance, depth is
                                                                                                reframed before E4-E6
    D2   The certificate components chosen (memory, horizon,   world admission; the definition  WLD-15 open-demand tier and
         composition, hypotheses, value of information, non-   of reasoning                     d_unfam measure what falls
         stationarity, deliberation) do not omit the demand                                     outside; revise components if
         where unfamiliar strategies would show                                                 open-demand families dominate
    D3   Procedurally generated plants exercise rulers on      FAMILIAR-ONLY classification;    X3; if generated plants are all
         mechanisms outside the authors' ontology              ruler qualification against      trivially familiar, rulers'
                                                               the unfamiliar class             sensitivity to unfamiliar
                                                                                                mechanisms stays unknown
    D4   Interchange and matched ablation are meaningful on    L3 by the carrier-agnostic       qualification on planted
         DGM carriers (constrained alignment maps; untrained-  route                            carriers; external evidence that
         organism controls)                                                                     unconstrained maps reach 100% on
                                                                                                random models (evidence/ext.md)
    D5   A signed batch verdict job and a row-class filter     mechanical authority             E0 counterfeit suite
         are enough to keep model and seat writes out of the
         promotion path

## E. About resources, people and institutions

    E1   CPU capacity of roughly 50-90k core-hours per         the compute envelope             measured in receipts; if lower,
         quarter remains available                                                              fewer arms (concentration floor)
    E2   [A] Year-one build inference of roughly 200-600M      the build plan                   INF-06 build ledger within two
         tokens processed is affordable: the 90-day 60-200M                                     weeks; USD via NRG-03; if not,
         (RSE s7) plus the second substrate E7 (L-XL band),                                     cut scope to the slice plus
         the REP-02 reimplementation, F5-F10 generators, the                                    E1/E2 and keep the L2 ceiling
         write-order tracer and the E8 harness
    E3   The operator can hold routine attention at <= 90      HUM-04; scheduled sessions       weekly digest; if exceeded,
         minutes per week if sessions are scheduled                                             reduce concurrent work items
    E4   At least one non-Claude model family or human can     REP-08 audit before day 60;      [A] if unavailable, the day-60
         be engaged for the REP-08 audit, the probe kernel     probe kernel (AGR-07); REP-04    gate cannot pass, the probe
         and re-execution                                      at L4r/L4d; externalisation      kernel cannot be built, and
                                                                                                L4r/L4d claims and
                                                                                                externalisation are blocked,
                                                                                                not relaxed
    E5   The existing fleet's seats can be retasked under      execution of the build plan      if the control regime keeps
         the new authority model without regime churn                                           changing, HUM-02 dwell rule is
                                                                                                the remedy
    E6   The operator's charter request for externally         OUT requirements                 operator ruling (OPEN_QUESTIONS
         inspectable outputs supersedes the older doctrine                                      Q-OP1)
         against publication framing for this deliverable

## F. About the epistemic-escape question

    F1   Search-generated variation (mutation, recombination,  the operator-model-free arm as   E8; if the operator-model-free
         procedurally generated bases) explores regions an     the default                      arm finds nothing the LLM arm
         LLM operator would not                                                                 does not, the anti-gravity
                                                                                                rationale weakens
    F2   An executable familiarity reference can be built      AGR-12; E8's familiarity         reachability fixture; if the
         whose UNFAMILIAR outcome is reachable                 measurement                      reference can only say FAMILIAR,
                                                                                                novelty statements are withheld
    F3   Survival decided by deterministic worlds and rulers   the three-layer authority        canary catch rates and E0; if
         is sufficient protection against the corpus           design                           LLM-built infrastructure passes
         recognising itself, given isolated operators                                           counterfeits, tighten authority
