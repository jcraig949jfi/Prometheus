# Proteus point-release review -- organisms / foundry / player registry (READ-ONLY, Stage 0-2 + Stage 3 replies)

    seat        Proteus[m2-7d051790] (M2 / SPECTREX5), model claude-opus-5
    built from  4a6457fbb in Prometheus-worktrees/proteus-boot-2026-09-17, branch
                proteus/boot-2026-09-17, dirty at boot: false
    authority   operator directive PROMPT 3 + Amendment 1 s8/s14
                (roles/Mnemosyne/prompts/2026-09-17_point_release/, MANIFEST verified 3/3)
    campaign 3  CLOSED at cb9135104; archaeon/campaign3/CAMPAIGN_REPORT.md read as authoritative
    mutation    NONE to any frozen profile. Two additive files (a witness + its test) in this
                worktree; runtime_hash, grammar_hash, affordance table, registry untouched
                (audit_identity FRESH 3ae4ee8b773e0fcf; quarantine STRING LAYER PASS;
                determinism check matches committed registry: True; 332 passed / 2 skipped)
    currency    2026-09-17

This document is the "equivalent scope critique" Amendment 1 s14 asks Proteus to return before
the point-release scope freezes. Section 2 answers the s8 questions one by one. Section 6 is
the Stage 3 criticism of the three peer deltas that name Proteus. Nothing here is implemented
beyond the expressiveness witness (section 1.5), which is a measurement, not a feature.

-----------------------------------------------------------------------------------------------
## 0. The one-paragraph answer

Every organism in campaigns 1-3 was a Proteus organism: Archaeon's runner imports
`proteus.foundry` (generate, grammar, lineage.descend, vm, prng) directly, so the frozen v0
runtime (`73f110e2...`), grammar v0.4 (`5043f5e1...`) and affordance table v0 (25 opcodes) ARE
the organism substrate the campaigns measured. Three campaigns exposed three organism-side
facts that belong in this release: (1) the generation-0 regime is part of the experimental
regime and Proteus has no regime-level identity for it (Archaeon minted `instr1-16:6528b9dc`
by its own rule; L2-017); (2) no population start state can be named or reproduced from
fields today (Vivarium's bundle.population is "UNKNOWN until Proteus defines it"); (3) every
campaign ran the mutation kernel whose own registry qualification says
`NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT`, and no campaign document names that
coordinate (grep of DECISIONS/REPORT/wse for USE_B, "authored current", "neutrality": 0 hits).
Organism EXPRESSIVENESS is not the frontier constraint: the two-value keyed memory that the
W2_K2 summit needs and that 0/60 runs found is a 12-instruction program in the frozen ISA
(section 1.5, witnessed with controls). The release should therefore ship identity, start
manifests and structural descriptors -- boring things -- and NOT a richer instruction set.

-----------------------------------------------------------------------------------------------
## 1. Stage 0 -- evidence inventory (organism side only)

### 1.1 Campaign 1 lessons relevant to organisms (archaeon/campaign1/CAMPAIGN_REPORT.md)

    lesson                                              where it landed          organism-side residue
    ---------------------------------------------------  ----------------------  -----------------------------------
    harness-seeded fills replaced generation 0 (L-008,   evolve.gen0/common_fill  a population start state has no
    L-030); "gen0 provenance and import lineage share"                            identity field anywhere -> P2
    named highest-value telemetry #3
    genome-length / opcode-composition summaries named   telemetry.genome_summary per-organism structural descriptor
    as telemetry #6 (length confounds, L-027)            (Archaeon's, ad hoc)     is not a Proteus artifact -> P3
    "Proteus foundry + RUNTIME_HASH: every organism,     receipts carry           runtime_hash present; foundry
    failure seen: none"                                  runtime_hash             REGIME id absent -> P1

### 1.2 Campaign 2 lessons

    L2-017  reachability pooled two generation-0 foundries (instr1-16 vs instr1-32) under one
            key; fixed by keying on Archaeon's foundry_id. THE generation-0 regime is part of
            the experimental regime. Proteus's `foundry_identity(fm)` hashes the manifest WITH
            seed and n (a population id), so Archaeon had to invent a regime id. -> P1
    L2-029  genome LENGTH is a cliff (random genomes at the failed set's mean 20.8
            instructions reached 1/10 vs 4/10 at the cell's own 5.9). Genome-size rules are
            a regime variable -> part of the profile (P1) and of the structural summary (P3).
    L2-037/48  substituted evolved material takes the population over within ~10 generations.
            Not a Proteus defect; a start-state fact -> lineage_composition in P2.
    C2-SFE-02  opcode-neighbourhood REWRITES (a representation change, masses matched within
            0.01) do not unlock W1_d4; "stop unless a STRUCTURAL operator set is proposed".
            The structural set already exists (section 2.11) -> P6, not a new operator.
    section 10  "Proteus foundry + grammar: every organism; grammar masses read at run time"
            -- the frozen twelve weights are a regime coordinate -> grammar_hash in P1.

### 1.3 Campaign 3 lessons (authoritative report)

    C3-SFE-02/08  the W2_K2 shelf is a ONE-value memory; 1 useful child in 4,800 grammar
            children (0.64 neutral / 0.36 destructive); the summit needs a two-value KEYED
            memory the one- and three-step neighbourhoods do not contain. C4-3 asks whether
            the cause is "a register/addressing primitive the grammar lacks, or a search
            operator". Answered by construction in 1.5: the primitive exists.
    C3-SFE-03/04  the delay ladder builds delay INVARIANCE (11/12, held-out 1.0 on never-
            trained d8/d16); "the campaign's only reproducible positive capability and it is
            unexplained"; C4-1 asks to anatomise it (genotype, minimum lesion, one instruction
            or a program shape). Proteus-side prerequisites: structural descriptor (P3),
            ordered activation tracing (PROTEUS-19/T10, a runtime transition -> DEFER).
    C3-SFE-10  import takeover is mechanics: incompetent permuted controls take over as fast
            as mature solvers; "apply a cap and report realized origin shares, or state that
            you are measuring a replaced population". Vivarium records realized dose; Proteus
            supplies the identities the dose is made of (P2 lineage_composition).
    section 16  "one grammar, one VM, N=200, E=16" is the stated scope limit of every result.
            That is the foundry profile in prose. P1 makes it a field.
    section 14  "Frozen-readout margins without a permuted-structure control" -- the same
            discipline applies to any capability label Proteus would ever export (P4).

### 1.4 Recurring defects, local patches, missing instrumentation, discretion

    recurring       an identity minted by the consumer because the owner had none
                    (foundry_id in archaeon/wse/reachability.py; gen0 provenance dict in
                    evolve.common_fill; genome_summary in wse/telemetry.py). Three instances,
                    all in Archaeon's layer, all stable across C2-C3 -> promote the IDENTITY
                    and the SHAPE to Proteus (P1, P2, P3); Archaeon keeps the science.
    local patches   none in proteus/ during C1-C3 (0 commits to proteus/foundry since the
                    closure pass 6ca171129; the campaigns changed nothing in the substrate).
    missing         regime-level foundry profile id; population manifest; per-organism
    instrumentation structural descriptor as a Proteus artifact; operator-stratified
                    neighbourhood tool; the T9 docstring defect (LDC immediate slot) that
                    cost this seat a wrong test once and would cost anyone hand-writing a
                    genome from the table prose.
    deterministic   profile id, population manifest hash, structural descriptor, the
    candidates      "matched structure, unmatched capability" diff (Vivarium s3) -- all pure
                    functions of committed bytes.
    stays above     which assay measures "capability"; whether a label is TRUE; which
    Proteus         population to start from; the dose; every threshold. Proteus mints
                    identities and shapes; it never scores.

### 1.5 The expressiveness witness (new, additive, controlled)

`proteus/eval/keyed_memory_witness.py` + `proteus/tests/test_keyed_memory_witness.py` +
`proteus/eval/KEYED_MEMORY_WITNESS.json`. Hand-written genome under the FROZEN runtime, run
on a Proteus-owned neutral probe (two input channels: key, value-or-empty; one output
channel; keys 0..15; persist=tape; code_writable=false). NOT a qualification world; W2_K2's
protocol was not read.

    program        instr   two-key probe   all-keys probe   ops (two-key)   status
    keyed memory    12       6/6            16/16            81 (9/tick)     halt every tick
    one-value       10       3/6             1/16            63              (the shelf strategy)
    inert NOP       12       0/6             0/16           144

    controls   negative: the last-PUT program scores exactly half on the two-key probe -- the
               half-credit shelf reproduced on a world-free probe; inert outputs nothing.
               cheat: an echo program scores 0/6 under the honest probe and 6/6 under a probe
               that leaks the expected value on the value channel (so 6/6 is evidence of
               memory, not of a leaky channel). identity: replay byte-identical, ops == 81.
    verdict    ISA_EXPRESSES_KEYED_MEMORY (register-indirect LD/ST over a persisted tape).
    does NOT   establish that search under grammar v0.4 reaches it (C3: 0/60 on W2_K2), or
    establish  anything about W2_K2's protocol, or minimality.

Consequence: C4-3's first branch ("a primitive the grammar lacks") is closed for THIS
question. What remains is the second branch -- search geometry -- and that is a property of
(grammar weights x selection x N x G), of which Proteus owns only the grammar.

-----------------------------------------------------------------------------------------------
## 2. Amendment 1 s8 -- the minimum questions, answered

### 2.1 What is immutable registry identity?

    layer              field(s)                                    where
    organism           organism_id = sha256 over the canonical      generate.organism_record;
                       manifest (proteus.player_manifest.v0)       registry entry.organism_id
    registry entry     entry_id (over the whole entry); registry_id proteus.player_registry.v1
                       (over the registry)
    lineage            lineage_id (root organism_id); generation    entry; lineage_record.v0
    runtime identity   identity.{runtime_hash, grammar_hash,        entry.identity
                       grammar_version, affordance_hash,
                       manifest_schema_version}
    provenance         provenance.{foundry_identity (population-   entry.provenance
                       level: includes seed and n), generation_
                       manifest_id, population_seed, index_in_
                       population, derivation, source}
    new families       organism_ref over IDENTITY_BEARING =         proteus/eval/identity.py
    (PR-ID)            (family, representation_version,             (SPECIMEN_AND_COMPOSITION_
                       semantic_version, body); evaluation_ref      IDENTITY.md)
                       (org_ref, runtime_hash, affordance_hash,
                       library_version, ...); observation_ref
                       (eval_ref, world_binding_id, occurrence)
    derived CA players mint record proteus.rule_table_mint.v1:      proteus/eval/rule_table_mint.py
                       player_id evca:r3:<hex>, parent_player,
                       mate_player, mutation_ref (Herakles
                       derivation_id), hash-chained ledger

Immutable by construction: manifest, identity, provenance, resource_envelope (a pure function
of the manifest), validation. Historical accident to name: `foundry_identity` is a POPULATION
identity (seed and n inside the hash), which is why Archaeon needed a regime id (2.4).

### 2.2 What is dictionary evidence?

Today: the registry entry's `extrinsic` block ("owner: not Proteus; Harmonia/Mnemosyne may
attach observations here"; `phenotype: "UNKNOWN"` with the note that UNKNOWN is a permanent,
legitimate state); PEW `ew.fossil_players.{phenotype, resources}` jsonb; PEW claims/evidence/
relations with CLAIM_STATUS / EVIDENCE_TYPE / EPISTEMIC_CLASS; Archaeon's reachability (1,265
rows) and corridor (155 rows) tables, which are competence observations keyed on cell x regime
x foundry. Proteus holds NO dictionary evidence and this review recommends it never store any
(2.5, P4): it supplies the typed SHAPE of an observation and the refs, and PEW holds the rows.

### 2.3 What current profiles are scientifically frozen?

    runtime          proteus VM v0, runtime_hash 73f110e21b9df879...   every specimen, every campaign
    grammar          proteus.grammar.v0.4, grammar_hash 5043f5e11a72...  twelve weights, hashed description
                     (v0.2, v0.3 historical; v0/v0.1 failed the neutrality gate; see MUTATION_GRAMMAR.md)
    affordances      affordance_table.v0 (25 opcodes), affordance_hash f1607ee8be68...
    manifest schema  proteus.player_manifest.v0; foundry manifest proteus.foundry_manifest.v0
    registry         proteus.player_registry.v1, registry_id b15e0a7f5f2d..., 64 specimens,
                     source_qualification: permitted USE_A_FROZEN_SPECIMEN_SOURCE, prohibited
                     USE_B_NEUTRAL_EVOLUTIONARY_OPERATOR, mutation_neutrality
                     NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT, operational_significance
                     NOT_YET_ADJUDICATED
    foundry regimes  (Archaeon's ids, recomputed here from the dicts; see section 5)
    that ran           instr1-16:6528b9dc  campaigns 1, 2 (default), 3 (FOUNDRY_C1 == FOUNDRY_C2)
                       instr1-32:199105b4  campaign 2 W1_d1 8-bit rows (evolve.FOUNDRY default)
                       instr1-64:97ce0af8  the 64-specimen registry build (proteus default)
    lineage/mint     proteus.lineage_record.v0; proteus.rule_table_mint.v1 (0 rows)

All of these are frozen in the strict sense: a byte change re-keys every specimen (runtime_hash
is a sha256 over the LF-normalised vm/affordances/grammar files, docstrings included -- TODO
T9). Any change is a NEW version, never an edit (PROTEUS-19 is the bundled transition and an
operator decision).

### 2.4 What fields already exist for parents / representation version / semantic version / genome hash / runtime-foundry identity?

    parents                  lineage_record.v0.parent_ids (array: mate included); mint record
                             parent_player + mate_player; PEW fossil_players.parent_player +
                             mate_player (migration 013)
    representation version   PR-ID artifact_manifest.representation_version (IDENTITY_BEARING);
                             PEW fossil_players.representation_version (013). v0 program
                             specimens carry it implicitly as manifest_schema_version.
    semantic version         PR-ID artifact_manifest.semantic_version; PEW semantic_version
                             (013); for VM programs the semantics are runtime_hash +
                             affordance_hash.
    genome hash              organism_id (v0: sha256 over the manifest, which contains the
                             genome and its limits); PR-ID organism_ref; PEW genome_hash.
                             NOTE: there is no hash of the genome WORDS ALONE; two manifests
                             with the same genome and different tick_budget are different
                             organisms, by design (the limits are part of what runs).
    runtime identity         identity.runtime_hash, grammar_hash, grammar_version,
                             affordance_hash -- present on every entry and every campaign
                             receipt.
    foundry identity         provenance.foundry_identity (population-level) and
                             generation_manifest_id. ABSENT: a regime-level profile id that
                             excludes seed/n and INCLUDES runtime + grammar identity. Archaeon's
                             `instr<lo>-<hi>:<8hex>` excludes runtime and grammar, so the same
                             string would name a different regime under a different runtime.
                             The triple (Archaeon string, runtime_hash, grammar_hash) is
                             recoverable from every C1-C3 receipt, so nothing is lost -- but
                             it is three fields where one should exist. -> P1

### 2.5 What would a capability/evidence model duplicate?

A Proteus-side dictionary STORE would be a fourth copy of: PEW claims/evidence/relations (the
vocabularies already exist), PEW fossil_players.phenotype, Archaeon's reachability/corridor
tables (competence per cell x regime), and Vivarium's observation rows / PEW outbox. It would
also be the one copy nearest the generator, i.e. the one most able to become an invisible
fitness function (directive s3). Proteus should supply: the typed observation SHAPE
(`proteus.capability_observation.v1`, ~100 LOC schema + validator), the refs (organism_ref,
evaluation_ref, observation_ref -- already defined in PR-ID), and the vocabulary alignment
(2.8). The store is PEW's; the queries are PEW projections; the assays are Archaeon's.

### 2.6 What organism ABI extensions are genuinely required by richer worlds?

None demonstrated by campaigns 1-3. Of the directive's s4 list, the frozen ABI ALREADY has:
multiple input/output channels (IN/INQ/OUT take a channel index in a register), optional
persistent local state (persist in {none, regs, tape, all}), bounded addressable state
(tape_words), indirect addressing (LD/ST are register-indirect), a costed random draw (RND),
explicit per-tick op budget and output cap (tick_budget, out_cap), delayed feedback (a world
concern; the ABI is tick-based and already supports it -- the delay family ran on it).
Opaque, untyped observations are A1's boundary and stay: typing is the world's, not the
player's. Two candidates are CONDITIONAL on a world that needs them, and neither is required
by C4-1..C4-4:
    cost query      the brief's R1 lists "a cost query" as a permitted minimal affordance; the
                    ISA has none (budget is invisible to the player). Enables resource-aware
                    behaviour under dynamic resource markets (directive s9). Runtime
                    transition -> bundle with PROTEUS-19; DEFER with the condition "a world
                    that charges a variable price exists".
    peer channels   already expressible as channels; the world assigns meaning. No ABI change.

### 2.7 Which extensions would merely explode the search space?

    new opcodes           opcode = word mod N_OPCODES: 25 -> 26 re-decodes EVERY existing genome
                          (a runtime transition that re-keys all 64 specimens and every campaign
                          organism) and dilutes the uniform word distribution over all opcodes.
                          The witness shows the summit-relevant primitive exists; a "MEMORY" or
                          "KEY" opcode would be the directive's own anti-pattern.
    wider ranges          genome_instr_range beyond 16: L2-029 measured length as a cliff
                          (1/10 vs 4/10). n_regs/tape ranges: each widens the config_perturbation
                          axis; unmeasured benefit.
    typed observations    would move world semantics into the player (A1 violation) and make
                          every world a new ABI.
    segment-typed ops     "subtree replacement where semantics permit": in a flat 4-word ISA
                          there is no subtree; any segment typing is a theory of program shape
                          smuggled into the grammar (R7). REJECT.

### 2.8 How should TRUE / FALSE / UNKNOWN / NOT_MEASURED / CONFLICTING_EVIDENCE align with PEW's typed vocabularies?

Two different UNKNOWNs are in play and must not be merged:
    Mnemosyne's envelope literal 'UNKNOWN' = "an owner exists and the value was not supplied"
    (ingestion contract s2) -- that is the directive's NOT_MEASURED.
    The registry's extrinsic.phenotype "UNKNOWN" = "no observation has been made" -- also
    NOT_MEASURED, and should be annotated as such (registry v1 stays byte-frozen; the
    annotation goes in the schema's documentation, not the file).
    The directive's UNKNOWN = measured, indeterminate.

Proposed alignment (Proteus proposes; Mnemosyne owns the vocabulary and decides):

    five-valued              PEW CLAIM_STATUS            OUTCOME_CANONICAL   RELATION / note
    TRUE                     SUPPORTED | ESTABLISHED     CONFIRMED           evidence rows required
    FALSE                    REFUTED                     REFUTED             evidence rows required
    UNKNOWN                  UNADJUDICABLE | OPEN        NULL_RESULT | NA    measured, indeterminate
    NOT_MEASURED             (no claim row)              (none)              envelope 'UNKNOWN';
                                                                             absence is NOT a
                                                                             negative capability
    CONFLICTING_EVIDENCE     OPEN with >= 2 evidence     MIXED               CONTRADICTS between
                             rows of opposite sign                           the evidence rows

`proteus.capability_observation.v1` would carry the five-valued field verbatim plus
measurement_refs[] (observation_ref / PEW evidence ids), so a TRUE that points at zero
measurements is invalid by schema.

### 2.9 What can be exported to PEW without letting PEW contaminate generation/selection?

Everything Proteus mints is exportable one-way: manifests, identities, lineage/mint records,
structural descriptors (P3), resource vectors, population manifests (P2), profile catalog
(P1). The firewall is mechanical, not a promise: `proteus/audits/quarantine.py` already
allowlists the player runtime's import graph; P5 extends the same audit to assert that
`proteus.foundry` and `proteus.eval` import nothing from `evidence_wiki` / `ew` and that no
generator, grammar or lineage function accepts a capability argument. Capability-based
selection then has exactly one legal home: the EXPERIMENT layer, recorded in
population_manifest.selection_criteria != "NONE" with selection_evidence_ref (a treatment,
directive s3).

### 2.10 What exact start-population manifest should Vivarium consume?

`proteus.population_manifest.v1` (P2), one object, sorted-key canonical JSON, hashed:

    schema_version        "proteus.population_manifest.v1"
    foundry_profile       pfp1:<16 hex>  (P1)  -- or "UNKNOWN" for a hand-built population
    count                 N
    members               EITHER organism_refs: [sorted organism_id or PR-ID organism_ref]
                          OR recipe: {generator: "proteus.foundry.generate.generate",
                          foundry_manifest_seed, n, foundry_profile} -- a recipe REPRODUCES,
                          a list PINS; both may be present and must agree
    manifest_hash         sha256 over the sorted member refs (the identity Vivarium binds)
    lineage_composition   {"gen0": n, "<import tag>": n, ...} by origin tag, summing to count
    gen0_provenance       Archaeon's common_fill provenance block VERBATIM (fill, campaign_seed,
                          cell_seed, n, n_substituted, substitute_tag, position,
                          verified_common) or "UNKNOWN"
    imported              [{organism_ref, source_world | source_artifact digest, tag}] for every
                          non-gen0 member (the identities the realized dose is made of)
    selection_criteria    "NONE" | a declared string (a treatment)
    selection_evidence_ref  PEW ref | null (null only when selection_criteria == "NONE")
    structural_summary    aggregate of P3 over members: genome_instructions {min, q25, median,
                          q75, max}, opcode_category_counts (static), persist mix, tape_words
                          mix, code_writable share -- this is what makes Vivarium's "matched
                          structure, unmatched capability" diff mechanical

Emitted from gen0()/common_fill() output or from the 64-specimen registry; no runtime change;
acceptance = the same population on two hosts gives one manifest_hash (the cross-host fixture
pattern already used for PR-ID).

### 2.11 Which structural operators constitute genuinely new search geometry rather than parameter noise?

The grammar ALREADY IS a structural operator set: insertion, deletion, duplication, movement
(block move), replacement, operand_perturbation, reference_redirection, region_swap, splice
(recombination with a mate), zeroing, randomization, unreachable_removal, config_perturbation
-- twelve named, weighted, hashed operators, with subtraction mass pre-registered (R4). Every
campaign ran all of them. Campaign 2's "stop unless a STRUCTURAL operator set is proposed"
therefore does not ask for new operators; the unmeasured variable is the PER-OPERATOR anatomy
of the neighbourhood. C3-SFE-02's 4,800 children (1 useful / 0.64 neutral / 0.36 destructive)
were pooled over operators; `mutate(manifest, rng, mate, name=...)` already lets a caller
choose the operator, so the stratified anatomy costs no grammar change (P6). Only after that
table exists can one say which of these is new geometry rather than noise:
    operator mass profiles (rate adaptation)    a NEW grammar version with declared weights;
                                                 justified only if P6 shows a stratum that
                                                 differs -> DEFER / MAJOR VERSION CANDIDATE
    splice dose and mate policy                  splice is 0.05 of mass; mate choice is the
                                                 selection loop's (Archaeon). "Crossover crosses
                                                 valleys single-step mutation cannot" is C2's
                                                 own finding; the knob is in Archaeon's layer.
    segment-typed operators                      REJECT (2.7)

### 2.12 Are current organism limitations the frontier constraint? (Amendment s8, last paragraph)

NO. Stated with its evidence: the W2_K2 ceiling is unreached in 0/60 runs across budget,
payoff and initialization (C3 sections 3, 14); the program that reaches it exists in the frozen
ISA at 12 instructions / 9 ops per tick (1.5). The constraint is search geometry under (grammar
v0.4 masses x tournament/elitism x N=200 x G<=300) -- and, unstated in any campaign document,
under a mutation kernel whose current is authored (2.3). The delay-invariant reader (C4-1) is
the other frontier and it needs INSTRUMENTATION (descriptor, lesion, ordered activation), not a
richer organism. The operator asked for "better organisms"; the evidence asks for better
IDENTITY and better INSTRUMENTS around the same organisms.

-----------------------------------------------------------------------------------------------
## 3. Stage 1 -- proposed delta (organism layer), classified

Legend: class in {FIX, HARDEN, INSTRUMENT, GENERALIZE, NEW CAPABILITY, DEFER, REJECT};
ship in {MUST, SHOULD IF CHEAP, DEFER, MAJOR VERSION CANDIDATE, REJECT}.

    id  item                                   class          ship        runtime change?  owner / consumers
    P1  foundry profile v1 + catalog +          GENERALIZE     MUST        no               Proteus / Archaeon (receipts,
        translation from Archaeon's ids                                                     optional), PEW envelope,
                                                                                            Vivarium bundle
    P2  population manifest v1                  NEW CAPABILITY MUST        no               Proteus / Vivarium bundle.
        (2.10)                                  (small)                                     population, Archaeon gen0
    P3  per-organism structural descriptor v1   INSTRUMENT     SHOULD      no               Proteus / PEW, Vivarium
        (pure function of the manifest)                        IF CHEAP                     structural_summary, C4-1
    P4  capability_observation v1 SHAPE +       GENERALIZE     MUST for    no               Proteus (shape) / Mnemosyne
        vocabulary alignment (2.8); NO store                   the shape;                   (store, projections)
                                                               DEFER store
    P5  execution-quarantine test: foundry +    HARDEN         MUST        no               Proteus
        eval import nothing from PEW; no
        capability argument on any generator/
        grammar/lineage function
    P6  operator-stratified neighbourhood tool  INSTRUMENT     SHOULD      no               Proteus (tool) / Archaeon
        (children per operator, seeded)                        IF CHEAP                     (runs it; C4-3 branch 2)
    P7  operator mass profiles (grammar v0.5)   NEW CAPABILITY DEFER /     yes (grammar     after P6 shows a stratum
                                                               MAJOR       version)
    P8  new ISA primitive for W2_K2             --             REJECT      --               witness 1.5
    P9  cost-query affordance                   NEW CAPABILITY DEFER       yes (runtime)    condition: a world that
                                                                                            charges a variable price
    P10 runtime transition bundle (T9 LDC       FIX + INSTR    MAJOR       yes              operator decision
        docstring + ordered activation tracing;                VERSION                      (PROTEUS-19; re-stamps 64
        PROTEUS-19)                                            CANDIDATE                    specimens, Harmonia fossils)
    P11 PEW fossil_players export exercised     FIX            MUST        no               Proteus / Mnemosyne route
        (PROTEUS-06/28; route built, 013)                                                   (#292)
    P12 mutation-kernel qualification carried   INSTRUMENT     MUST        no               folded into P1 (the catalog
        on every profile row                                                                row carries the registry's
                                                                                            source_qualification)
    P13 ecological properties as Proteus        --             REJECT      --               Vivarium records realized
        storage (takeover, compatibility...)                                                dose/origin shares; PEW stores
    P14 mechanistic hypotheses as Proteus       --             REJECT      --               PEW claims, EPISTEMIC_CLASS
        storage                                                                             HYPOTHESIZED

For each MUST, the eleven fields the directive asks for:

    P1  problem/evidence   L2-017; 2.4; three regimes ran under a consumer-minted id
        change            `proteus.foundry_profile.v1` = {regime: foundry manifest minus seed/n,
                          runtime_hash, grammar_hash, grammar_version, affordance_hash,
                          registry_source_qualification}; id "pfp1:" + 16 hex of sha256 over the
                          canonical record; catalog file with every profile that has run and a
                          translation table Archaeon-string -> pfp1 (section 5); a test that
                          recomputes Archaeon's three strings from the catalog dicts
        owner/consumers   Proteus / Archaeon, PEW, Vivarium
        compat            additive; Archaeon's strings stay verbatim in every old receipt and
                          are never re-rendered (evidence is not edited); PEW stores the
                          Archaeon string in foundry_profile as it does now and MAY add
                          foundry_profile_scheme; the catalog supplies the join
        migration         none (files + tests)
        sci risk          low; the risk is a catalog row that does not match what ran ->
                          mitigated by recomputing from the committed dicts, not by hand
        ops risk          none
        cost              ~150 LOC + JSON
        acceptance        recomputed ids == the three strings in C1-C3 receipts; profile id
                          changes when any of runtime/grammar/affordance/regime changes and
                          not when seed/n change
        rollback          delete the files; nothing depends on them until Stage 4
    P2  problem/evidence   L-008/L-030, L2-037/48, C3-SFE-10, Vivarium bundle "UNKNOWN until
                          Proteus defines it"
        change            schema + emitter (2.10) from gen0()/common_fill() output and from
                          the registry; validator
        compat            additive; C1-C3 populations can be re-described from trace[0]
                          provenance where present, else "UNKNOWN" (never inferred)
        sci risk          a manifest that lists members but not the realized population ->
                          the manifest describes INTENDED start; Vivarium's receipt records
                          realized; the two hashes differ visibly (Vivarium R3)
        cost              ~200 LOC; acceptance = cross-host hash equality + a negative
                          (lineage_composition not summing to count is refused) + a cheat (a
                          member listed twice is refused)
        rollback          delete; Vivarium keeps "UNKNOWN"
    P4  change            schema + validator only; TRUE/FALSE require >= 1 measurement_ref;
                          CONFLICTING requires >= 2; NOT_MEASURED forbids any
        acceptance        positive/negative/cheat fixtures; the cheat is a TRUE with an
                          empty measurement list, refused
    P5  change            extend quarantine.py: import-graph check over proteus.foundry and
                          proteus.eval against a denylist {evidence_wiki, ew, requests,
                          httpx, psycopg}; AST check that no public function in
                          foundry/{generate,grammar,lineage}.py has a parameter named like
                          capability/phenotype/evidence/score/fitness
        acceptance        the audit fails on a planted import in a scratch copy (cheat) and
                          passes on the tree
    P11 change            run PEW_EXPORT against the live route in namespace "test" during
                          the read-only phase; the first "prod" mint waits for (a) a real
                          derivation request (PROTEUS-27) and (b) the deploy window; a prod
                          row for a child nobody asked for would be a fabricated specimen

-----------------------------------------------------------------------------------------------
## 4. Stage 2 -- self-critique

    question                                          answer                                      result
    Does this encode the answer to a scientific       P1-P3 are identities and pure functions     KEEP
    question?                                         of committed bytes; P4 forbids a label
                                                      without measurements
    Does it turn an interpretation into fact?         P4's five values are the OBSERVER's         KEEP; MODIFY 2.8 so
                                                      status of an assay, never Proteus's; the    NOT_MEASURED is a
                                                      registry's "UNKNOWN" is renamed in docs     documented rename, not
                                                      to NOT_MEASURED semantics                   a file edit
    Could it contaminate old results?                 nothing re-renders an old receipt; Archaeon MODIFY P1: the catalog
                                                      strings stay verbatim; the catalog is a     is a JOIN table, PEW
                                                      join, not a replacement                     keeps the source string
    Future-information leakage?                       P2.selection_evidence_ref could point at    ADD to P2: the ref must
                                                      evidence measured AFTER the population ran  carry the evidence row's
                                                      if a manifest is rebuilt later              recorded_at, and the
                                                                                                  validator refuses one
                                                                                                  later than the bundle seal
    More flexible or merely more complex?             P1/P2 replace three consumer-minted ad hoc  KEEP
                                                      objects with two owned ones
    Survives long runs / restarts / duplicates?       all are content-addressed; duplicate        KEEP
                                                      emission is idempotent by hash
    Reconstructible after a crash?                    pure functions of committed inputs          KEEP
    Expensive telemetry nobody queries?               P3 per-organism descriptors at N=200 x       MODIFY P3: emit per
                                                      G=300 x 12 seeds = 720k rows if per gen     population (aggregate)
                                                                                                  by default; per organism
                                                                                                  only for published
                                                                                                  artifacts and elites
    Generic for unimagined worlds?                    P1-P5 know nothing about worlds; P9 is the  KEEP
                                                      only world-facing item and is deferred
    Self-serving instrument?                          the witness is hand-written by the seat     DROP nothing; the
                                                      whose substrate it defends; the seat        witness ships with a
                                                      benefits if "not the frontier" is           cheat control and its
                                                      accepted (no runtime transition)            genome is 12 lines any
                                                                                                  reader can execute
    The prior seat's enthusiasm (RESPONSIBILITIES     the operator asked for "better organisms"   KEEP the refusal; it is
    s5, s9)?                                          and this review says no -- the temptation   Amendment s8's own
                                                      ran the other way this time                 instruction

-----------------------------------------------------------------------------------------------
## 5. Foundry profile catalog -- DRAFT, computed (P1 preview; no ids minted until Stage 4)

Recomputed in this worktree from the committed dicts with Archaeon's own rule
(archaeon/wse/reachability.foundry_id: sha256 over the dict minus seed/n, 8 hex):

    Archaeon id          regime (proteus.foundry_manifest.v0 minus seed/n)                          where it ran
    instr1-16:6528b9dc   genome_instr_range [1,16]; tape_words_choices [16,32,64,128,256];       C1 (FOUNDRY_C1), C2 default
                         tick_budget_choices [16,64,256]; n_regs_range [2,16]; out_cap [1,4];     (FOUNDRY_C2, identical dict),
                         code_writable_weights [1,1]; persist_weights [1,1,1,1]                   C3 (c3base imports FOUNDRY_C2)
    instr1-32:199105b4   as above with genome_instr_range [1,32]                                  C2 W1_d1 8-bit rows
                                                                                                  (evolve.FOUNDRY default)
    instr1-64:97ce0af8   genome_instr_range [1,64]; tape_words up to 1024; tick_budget up to      the 64-specimen registry
                         1024; out_cap [1,4,16]                                                   (proteus DEFAULT_FOUNDRY_
                                                                                                  MANIFEST)

Common to all three: runtime_hash 73f110e21b9df879..., grammar proteus.grammar.v0.4
5043f5e11a72..., affordance_hash f1607ee8be68..., mutation kernel qualification
NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT (operational significance NOT_YET_ADJUDICATED).
Proposed pfp1 ids (sha256 over {regime, runtime_hash, grammar_hash}, first 16 hex) for the
reviewer to check the rule, NOT yet identities: a803cba43f057874 / ec4381139c668d4a /
553d234ec6b53d24. The final record adds grammar_version and affordance_hash and the
qualification; the ids will change and will be minted once, in Stage 4, with the test.

Answer to Mnemosyne's question (#327, contract s9): "instr1-16:6528b9dc" is ARCHAEON's
rendering of a PROTEUS-schema object -- the generation-0 sampling regime, a
`proteus.foundry_manifest.v0` dict minus seed and n -- hashed by Archaeon's rule. It is
neither the grammar hash nor a full profile: it omits runtime_hash and grammar_hash, which the
same receipts carry separately. PEW should keep the string verbatim under foundry_profile (it
is what the evidence says), may tag the scheme "archaeon.wse.reachability.foundry_id.v1", and
joins to the full profile through the P1 catalog. Nothing should be re-rendered at ingest.

-----------------------------------------------------------------------------------------------
## 6. Stage 3 -- criticism of the peer deltas that name Proteus

### 6.1 Daedalus (#328, D4): CONFIRMED with one addition

D4's manifest may cite a foundry profile id BY VALUE and the engine must NOT validate it --
confirmed; the engine understanding a Proteus id would be the interpretation-downward
movement Amendment s2 forbids. Addition: reserve the key name `foundry_profile` inside the
manifest so PEW's envelope and Vivarium's bundle read the same key, and state in the D4
envelope rule that the engine treats it as an opaque string (no length or format check
beyond "string"). The rest of the SFE delta touches no organism. One question back: D2's
typed termination should be able to carry `budget_consumed` in the WORLD's units; a player's
resource vector (Meter.as_dict minus timings) is per organism and stays out of the engine --
agreed that the engine never holds organism state (your Stage 2 row says so).

### 6.2 Vivarium (#330 A7, #333 s12, #304 axes)

A7 string forms (carried slots; UNKNOWN until minted):
    foundry/runtime profile   "pfp1:<16 hex>" (P1) -- until Stage 4, carry Archaeon's
                              "instr<lo>-<hi>:<8 hex>" verbatim with scheme
                              "archaeon.wse.reachability.foundry_id.v1"; never re-render
    organism                  v0 program specimens: organism_id, 64 hex (sha256 over the
                              manifest); PR-ID families: organism_ref as
                              proteus/eval/identity.py renders it; CA rule tables:
                              "evca:r3:<32 hex>" (Herakles's spelling, verbatim)
    lineage                   lineage_id, 64 hex (the root organism_id); for minted CA
                              players the mint record's parent_player/mate_player/
                              mutation_ref, not a lineage_id
    genotype/runtime hash     runtime_hash 64 hex; grammar_hash 64 hex; both from
                              proteus.foundry.identity / grammar at run time, never from a
                              config file
bundle.population (s12): the P2 object in 2.10 is the proposal; until it exists your
`{manifest_hash, manifest_ref}`-only fallback is right and should be labelled with
`population_schema: "UNKNOWN"` so a later P2 manifest is a visible upgrade, not an overwrite.
Two criticisms of the bundle: (a) `foundry_profile` appears both at top level and inside
population -- keep ONE (inside population; a bundle with a hand-built population has no
profile, and the top-level slot would then be a duplicate UNKNOWN); (b) the "matched structure,
unmatched capability" comparison needs the structural summary to be computed by the SAME code
on both sides -- Proteus will supply the function (P3), you call it; do not re-implement the
histogram. Axes for `cegis_boolean_v1` (#304): the kind is registered in Vivarium's tree and I
do not edit it; my assignment for the owner to enter: `n_inputs`=world, `max_expr_size`=budget,
`max_candidates`=budget, `target_table`/task set=pressure, `ordering_seed_policy`=intervention,
`grammar_version`=mechanism; anything not in that list UNCLASSIFIED on purpose. If the kind's
parameter names differ from these, the registry is authoritative and I will re-issue against
the printed contract.

### 6.3 Mnemosyne (#327 contract, #292 mint, #332)

instr1-16 answered in section 5. Vocabulary: adopt the alignment in 2.8 or amend it -- the one
thing this review asks you to hold is that the envelope's 'UNKNOWN' (not supplied) and a
capability observation's UNKNOWN (measured, indeterminate) never share a column. Ingestion
contract s2 lists foundry_profile / grammar_hash / runtime_hash as three Proteus-minted
fields; that is correct today and P1 does not remove any of them (the profile is a join over
the three, not a replacement). #292: the route and the round trip are acknowledged; the
"post your first prod mint" step is held for the two conditions in P11 (a real derivation
request, and the deploy window), and a namespace "test" rehearsal is what I will run during
the read-only phase and report with its player_id/mint_id. The token file exists on M2 at the
path you named (existence checked, contents not read).

### 6.4 Archaeon (arbiter; no question posed to Proteus, one offered)

If ownership of the regime id is disputed: the string was minted in your layer and belongs
verbatim in your receipts forever; the OBJECT it hashes is a Proteus schema instance, so the
canonical profile record and catalog are Proteus's. I propose no change to reachability.py.
Offered for C4-3 branch 2: the P6 stratifier, so a C3-SFE-02-style anatomy can report
useful/neutral/destructive PER OPERATOR; and for C4-1: the P3 descriptor on the eleven
delay-general elites, which Proteus will compute if you publish their manifests (it never
touches the world).

-----------------------------------------------------------------------------------------------
## 7. Directive PROMPT 3 items this review declines or narrows, with the reason

    s1 E (mechanistic hypotheses in the organism record)   REJECT as Proteus storage: PEW claims
                                                            with EPISTEMIC_CLASS HYPOTHESIZED
    s1 D (ecological properties)                            REJECT as Proteus storage: Vivarium
                                                            realized-dose receipts + PEW
    s4 (richer ABI)                                         none required by C1-C3; two
                                                            conditional candidates deferred (2.6)
    s6 (structural operators)                               already present; measure per operator
                                                            first (P6); no new operator
    s7 (capability vectors)                                 shape + refs only (P4); vectors are PEW
                                                            projections over Archaeon's assays
    s9 (better organisms for better worlds)                 "current organism limitations are NOT
                                                            yet the frontier constraint" -- said,
                                                            with the witness
    s10 (benchmarks)                                        deferred to Stage 6 after Stage 3
                                                            closes; the witness is the first
                                                            known-answer fixture and its shape
                                                            (positive/negative/cheat/identity) is
                                                            the template
    closing artifacts                                       PROTEUS_POINT_RELEASE_REVIEW.md (this);
                                                            FOUNDRY_PROFILE_CATALOG.md drafted as
                                                            section 5; ORGANISM_SCHEMA_DELTA.md,
                                                            ORGANISM_BENCHMARK_RECEIPT.md,
                                                            PROTEUS_RELEASE_PACKET.md wait for
                                                            Stage 3 to close and the window

-----------------------------------------------------------------------------------------------
## 8. Conflicts of interest, and what would falsify this review

Conflicts: this seat built the substrate under review and wrote the witness that defends it;
the seat gains from "no runtime transition" (the frozen identity it curates stays valid).
The prior seat's calibration record over-claims under enthusiasm; this review's direction
(refuse the richer organism) is the less exciting one, which is a weaker but not zero guard.

Falsifiers: (a) a W2_K2-family protocol in which the keyed memory of 1.5 is NOT the summit
mechanism (only Archaeon can say; the witness is protocol-free by design); (b) a C4 run in
which the 12-instruction program, injected at dose 1 with a cap, does NOT reach the summit
(would show the ceiling is not expressiveness AND not reachability-from-a-solver, i.e. the
payoff or the world); (c) P6 finding that no operator stratum differs (then operator work is
dead and P7 is not even a candidate); (d) Mnemosyne rejecting the 2.8 alignment (then P4's
shape changes before it ships). Not worth continuing: if the operator decides Campaign 4 does
not need reproducible start populations, P2 has no consumer and should not be built.

-----------------------------------------------------------------------------------------------
## 9. What was NOT done

No production write, no PEW row, no mint, no runtime/grammar/affordance change, no registry
change, no campaign artifact opened beyond the three reports and the consumer call sites
listed in READ_LEDGER.md (2026-09-17 entries), no world protocol read, no organism scored.
