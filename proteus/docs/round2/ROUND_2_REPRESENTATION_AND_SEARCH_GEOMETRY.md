# Proteus Round 2: Representation & Search Geometry -- design v0 and the seat's ruling

    seat        Proteus[m2-7d051790]; built from 4a6457fbb, merged 3f2920d6a; branch
                proteus/boot-2026-09-17
    authority   operator message in chat 2026-09-17 ("you have the final say"), verbatim at
                roles/Proteus/prompts/2026-09-17_round2/00_OPERATOR_MESSAGE_ROUND2.md (MANIFEST
                beside it); the point-release review of the same day (proteus/docs/
                point_release_2026-09/PROTEUS_POINT_RELEASE_REVIEW.md) is the evidence base
    status      DESIGN ONLY. No profile minted, no grammar version added, no run proposed for
                launch. Nothing here may start before the point-release items it depends on
                (section 5) exist and Stage 3 has closed.
    currency    2026-09-17

-----------------------------------------------------------------------------------------------
## 0. Ruling

ADOPTED as the seat's next design lane, under the operator's name "Proteus Round 2:
Representation & Search Geometry", with the operator's rule taken verbatim:

    Do not design organisms to solve W2_K2 or delay tasks. Design substrate variants that
    change the classes of computation evolution can cheaply express, then let the existing
    worlds tell us whether those variants matter.

and with three amendments that the day's evidence forces. They narrow the round; they do not
soften it.

AMENDMENT A -- lane 2 (minimal neutral expressiveness) is RE-SEQUENCED behind the anatomy and
lane 3, and given an admission gate. The candidates the operator lists for lane 2 -- generic
indexed state, indirect addressing, additional bounded registers/data slots -- are already in
the frozen ISA: LD/ST are register-indirect over a tape of up to 1024 words, the tape persists
under persist in {tape, all}, n_regs is a manifest limit up to 16. The keyed two-value memory
that motivates the lane is a 12-instruction program at 9 ops/tick under the frozen runtime,
witnessed today with a negative control that reproduces the half-credit shelf and a cheat
control (review s1.5). So lane 2's question is not "can the language express it" (yes) but
"would a CHEAPER encoding change reachability" -- and that is only answerable after lane 3 has
shown what the existing operators can and cannot reach on the same class. A primitive is
admitted to lane 2 only when BOTH hold, pre-registered: (i) the anatomy or lane 3 names a class
of computation that is expressible under every grammar profile and reached by none; (ii) a
cheaper encoding of that class is written by hand, witnessed on a neutral probe, and shown to
be reachable by the FROZEN grammar from the frozen foundry on that probe (if the frozen grammar
reaches the cheap form but not the expensive one, cost is the barrier; if it reaches neither,
the barrier is not cost and a new primitive is the wrong tool). Until then lane 2 holds one
deferred candidate that survives the neutrality test by construction and is motivated by lane 4
rather than by W2_K2: the cost query (the brief's R1 lists it; the ISA lacks it; it has many
uses and no task knowledge). Any opcode addition is a runtime transition (25 -> 26 re-decodes
every genome) and so lands, if ever, inside the PROTEUS-19 bundle as a NEW runtime version with
the old one frozen beside it.

AMENDMENT B -- lane 3 (structural search) is GRAMMAR MASS PROFILES over the existing twelve
operators, not new operators. Every operator the operator names -- segment duplication, block
insertion/deletion, recombination (splice with a mate), variable-length mutation -- exists in
proteus.grammar.v0.4 with a hashed weight (MUTATION_GRAMMAR.md). Every campaign ran all of
them. A "second search geometry" is therefore a second WEIGHT VECTOR, minted as a new
grammar_version with its own grammar_hash, never an edit of v0.4. Three profiles, minimum:
    G0  proteus.grammar.v0.4              the frozen control (twelve weights as hashed)
    G-  POINT-ONLY                         a RESTRICTION: replacement, operand_perturbation,
                                           reference_redirection, zeroing, randomization,
                                           config_perturbation; zero mass on every operator
                                           that changes length or moves blocks (insertion,
                                           deletion, duplication, movement, region_swap,
                                           splice, unreachable_removal). This is the
                                           operator's "point mutation only" control, and it
                                           is what "single-step local mutation" in C3-SFE-02
                                           actually names once the pooled neighbourhood is
                                           stratified.
    G+  STRUCTURAL-HEAVY                   splice, duplication, movement, insertion, deletion,
                                           region_swap carry the majority of the mass; point
                                           operators keep non-zero mass so the profile is
                                           still ergodic on operands
Each profile carries its own R4 neutrality measurement (expected size drift under no
selection) and its own detailed-balance / current measurement with the V0.5 instrument
(d511974eb): the registry's NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT is a fact about ONE
kernel, and a new weight vector is a new kernel with an unknown current. G- trivially satisfies
"growth is not the default" (it cannot change length); that is stated, not claimed as a pass.
Splice needs a MATE, and mate choice lives in the selection loop (archaeon.wse.evolve.reproduce),
so the operator's matrix row "Recombination -- control: mutation-only" is a PAIR of settings:
the grammar profile (Proteus) and the mate policy (Archaeon). The design names both and
neither seat changes the other's.

AMENDMENT C -- the control matrix gains two rows that campaign 3 paid for: (i) the mutation-
kernel current per profile (above); (ii) a NOISE-FLOOR row for every geometry statistic -- the
same profile under re-keyed seeds -- because C3-SFE-07 found two random orderings differing by
exactly the treatment effect (0.083). No geometry difference between profiles is reported
without the same-profile floor beside it.

The anatomy of the delay-invariant readers comes FIRST, as the operator says, and it splits
cleanly along the firewall: Proteus computes STRUCTURE (descriptor, static reachable set,
motif and state-use patterns, ablation SETS) on manifests handed to it; Archaeon measures
BEHAVIOUR (lesion outcomes on the delay family, which is a world) with the ablation sets
Proteus emits. Proteus never runs a reader against a delay cell.

-----------------------------------------------------------------------------------------------
## 1. The four lanes, as the seat will run them

    lane  name                          Proteus artifact                          decides whether it mattered
    L1    frozen control                nothing new: runtime 73f110e2, grammar    -- (it is the baseline every
                                        v0.4, affordances v0, regimes instr1-16   other lane competes against)
                                        /32/64 as catalogued (P1). Guarantee:
                                        every Round 2 run names its profile id;
                                        a run that cannot is not a Round 2 run
    L0    anatomy (before L2/L3)        proteus/eval/structural_descriptor.py     Archaeon (lesion outcomes on
          the 11/12 delay-general       (P3) over the elites + matched W0         the delay family, using the
          readers as specimens          solvers; static_reachable; motif census;  ablation sets); Harmonia
                                        state-use pattern (persist, tape          audits the comparison
                                        addresses touched under the neutral
                                        probe); ablation SETS per organism
                                        (proteus/compose ablation_report
                                        pattern). Output: a structural
                                        SEPARATION statement with its chance
                                        floor (does any structural statistic
                                        separate readers from W0 solvers beyond
                                        what re-labelling gives?)
    L3    structural search             grammar profiles G-, G+ as new            Archaeon's worlds, under the
          (mass profiles)               grammar_versions; per-profile R4 and      control matrix; Proteus
                                        current measurements; P6 stratifier so    supplies P6 so the answer is
                                        the neighbourhood anatomy is per operator per operator, not pooled
    L2    minimal neutral               HELD behind the L2 admission gate          --
          expressiveness                (Amendment A). One deferred candidate:
                                        cost query (runtime transition; PROTEUS-
                                        19 bundle; new runtime version only)
    L4    richer-interaction ABI        DESIGN ONLY: proteus/contracts/            nobody yet; a design has no
          (design only)                 WORLD_INTERFACE_v1_PROPOSAL.md -- the      consumer until a world asks
                                        smallest generic extension per pressure
                                        class (channels already generic; delayed
                                        observations already tick-native;
                                        resource accounting = cost query;
                                        peers = channels + the world's
                                        assignment; persistent/ephemeral
                                        objects and partial observability are
                                        WORLD-side under A1). Expected result:
                                        most rows say "no ABI change; the
                                        world does it"; the one candidate is
                                        the cost query

-----------------------------------------------------------------------------------------------
## 2. Control matrix (the operator's rows, corrected against what exists, plus Amendment C)

    proposed change              C3 motivation                  neutrality risk              search-space cost           control                       status today
    indexed state /              one-value -> two-value         could encode keyed memory    larger state/action space   current VM                    EXISTS (LD/ST register-
    indirect access              barrier                        if typed                                                                                indirect; witnessed 12 instr).
                                                                                                                                                        L2 admission gate applies
    segment duplication          preserve a partial program     low                          genome bloat                G- (point-only)               EXISTS (duplication 0.04);
                                 while extending                                                                                                        L3 varies its MASS
    recombination                combine viable partials to     medium                       provenance / epistasis      G- + mutation-only mate       EXISTS (splice 0.05); mate
                                 cross a valley                                                                          policy (Archaeon)             policy is Archaeon's knob
    variable genome length       length geometry may constrain  low-medium                   bloat                       G- (length-fixed by           EXISTS (insertion/deletion/
                                 composition (L2-029 cliff)                                                              construction)                 duplication; genome_instr_range
                                                                                                                                                        is a regime variable -> P1)
    richer I/O ABI               future dynamic worlds          architecture leakage if      substantially larger        current ABI                   L4 design only; one candidate
                                                                semantic                                                                               (cost query)
    [C] mutation-kernel current  registry qualification is per  a profile with a larger      none                        V0.5 detailed-balance         instrument EXISTS (d511974eb);
    per grammar profile          kernel                         current biases every                                     instrument on each profile    run per profile before any
                                                                geometry statistic                                                                     geometry comparison
    [C] same-profile re-keyed    C3-SFE-07: random orderings    --                           compute only                the statistic's own noise     required beside every
    seeds (noise floor)          differed by the treatment                                                               floor                         difference reported
                                 effect

-----------------------------------------------------------------------------------------------
## 3. Release criteria (the operator's seven), mapped to mechanisms

    the new profile is generic                    a grammar profile is a weight vector over the existing
                                                  syntactic operators (A3: no operator knows what an
                                                  instruction means); a runtime profile, if ever, passes
                                                  the R1 ontology gate (minimal computational affordance,
                                                  never a cognitive function)
    old profiles remain frozen                    new grammar_version / runtime version only; v0.4 and
                                                  runtime 73f110e2 byte-identical; audit_identity binds them
    exact foundry/runtime provenance              P1 profile id on every organism and run (regime +
                                                  runtime_hash + grammar_hash + affordance_hash + kernel
                                                  qualification)
    primitives materially alter measurable        P6 per-operator neighbourhood table + basin/deceptive
    search geometry                               share on Proteus's own exhaustive-neighbourhood tool for
                                                  small genomes (C2 recommendation 4), each with the [C]
                                                  noise floor; "materially" = beyond the same-profile floor,
                                                  pre-registered
    controls separate representation effect       lanes are orthogonal by construction: L3 changes grammar
    from operator effect                          only (runtime fixed); L2, if admitted, changes runtime
                                                  only (grammar fixed); a 2x2 is then possible
    Proteus tells Vivarium the exact start        P2 population_manifest.v1 with foundry_profile inside
    population/profile                            population
    PEW describes capabilities without feeding    P4 shape + P5 quarantine test; selection on a capability
    them back                                     is a treatment recorded in population_manifest.
                                                  selection_criteria

-----------------------------------------------------------------------------------------------
## 4. Sequencing and dependencies

    step  what                                              needs                                   owner
    1     P1, P2, P3, P5, P6 land (point release Stage 4)    Stage 3 closed; scope frozen            Proteus
    2     L0 anatomy: Archaeon publishes the 11 delay-       prompt posted 2026-09-17 (comms);       Archaeon (manifests),
          general elite manifests + 11 matched W0 solvers    P3                                       Proteus (structure)
          (SFE artifact digests -> manifests); Proteus
          emits descriptors, motif census, ablation sets
    3     L3 profiles G-, G+ minted as grammar versions;     step 1                                  Proteus
          R4 + current measured per profile; P6 stratified
          neighbourhood on the C3-SFE-02 shelf elites if
          Archaeon publishes them
    4     Archaeon designs the Round 2 runs under the         steps 2-3; Harmonia audit of the        Archaeon (design),
          control matrix (mate policy, cells, budgets);        instruments                            Harmonia (audit)
          Proteus supplies profiles and population manifests
          and does not choose cells or read results
    5     L2 admission gate evaluated on step 3-4 evidence    steps 3-4                               Proteus proposes;
                                                                                                     operator decides
                                                                                                     (runtime transition)
    6     L4 proposal document                                none; can be written now              Proteus

No science run starts in this round on Proteus's initiative (R8; base-role: the seat does
not adjudicate its own science). Steps 1, 3 and 6 are executable now (design and additive
code in this worktree); 2 waits on Archaeon's manifests; 4-5 are other seats' or the
operator's.

-----------------------------------------------------------------------------------------------
## 5. Point-release items Round 2 depends on (and why the review's REJECT of P8 stands)

P1 (profile ids) is the identity Round 2 runs on; P2 (population manifests) is how the frozen
control and every treated population are named to Vivarium; P3 (descriptor) is the anatomy's
instrument; P5 (quarantine) is the seventh criterion; P6 (stratifier) is lane 3's instrument.
The review's REJECT of P8 -- a new ISA primitive for W2_K2 -- is exactly Amendment A: the
primitive exists, so the round does not begin by adding one; it begins by measuring what the
existing operators reach. The operator's lane 2 survives as an admission-gated lane, which is
stricter than the review's DEFER and consistent with it.

-----------------------------------------------------------------------------------------------
## 6. What Proteus needs from other seats (posted 2026-09-17)

    Archaeon    (delegation) the 11 delay-general elite manifests of C3-SFE-03 and 11 matched
                W0 solvers (same regime, same budget class), as committed JSON or SFE artifact
                digests Proteus can fetch by reference; the C3-SFE-02 shelf elites (12) for the
                stratified neighbourhood; a statement of which mate policy reproduce() uses
                today (for the recombination control pair). Proteus returns structure only.
    Harmonia    (question) whether the V0.5 detailed-balance instrument is acceptable as the
                per-profile current measurement, or which instrument Harmonia would audit.
    Vivarium    nothing new: bundle.population = P2 (already proposed).
    Mnemosyne   nothing new: capability rows = P4 shape (already proposed).

-----------------------------------------------------------------------------------------------
## 7. Falsifiers and stop conditions

- If the L0 anatomy finds NO structural statistic separating readers from W0 solvers beyond
  the re-labelling floor, "the capability is a program shape" is dead and the readers are a
  selection story (the operator's own alternative); Round 2 then has no representation lane
  and is a search-geometry round only.
- If G- (point-only) reaches every class G0 reaches on the P6 table, the "single-step cannot
  cross" reading of C3-SFE-02 was about the neighbourhood, not the operator set, and lane 3
  is dead as posed.
- If G+ changes no geometry statistic beyond the same-profile noise floor, mass profiles are
  parameter noise (the operator's own criterion) and PROTEUS-19's operator-rate adaptation
  stays a MAJOR VERSION CANDIDATE with no evidence behind it.
- If a Round 2 run reaches the W2_K2 summit under G0 (the frozen control) with a changed mate
  policy alone, the answer to Campaign 4's question was "the search operator, in Archaeon's
  layer" and Proteus's lanes 2-3 were unnecessary. That is a first-class outcome.
- Not worth continuing: if the operator decides Campaign 4 will not vary the substrate, this
  document is filed as design residue and nothing is minted.

-----------------------------------------------------------------------------------------------
## 8. Self-dissent (the seat attacking its own ruling first)

Against Amendment A: "expressible" is not "cheaply expressible", and the operator's rule is
about what evolution can CHEAPLY express. Nine ops per tick and twelve instructions is cheap by
the VM's budget (tick_budget 16-256) but the witness says nothing about how many mutations away
the program is from a shelf organism. The admission gate exists because of this: it demands the
reachability comparison before any primitive, rather than assuming the answer either way.
Against Amendment B: three weight vectors are three points in a twelve-dimensional simplex;
"mass profiles" could be as much a two-point correlation as C3-SFE-06's pooled rho. Mitigation:
the P6 table is per operator, so the profiles are read through their strata, not as three
scalars; and the noise-floor row is mandatory.
Against the whole round: the seat that built the frozen substrate is now the seat proposing
that the substrate is fine and the operators should be studied. Conflict declared in the
review (s8); the round's structure (Archaeon designs the runs, Harmonia audits the instruments,
the operator admits any runtime change) is the guard.
