# Campaign 6 -- Proteus scope: AXIS O (organism expansion) and the organism side of AXIS T

    seat        Proteus[m2-7d051790], M2; worktree proteus-boot-2026-09-17 (merged origin/main 677f8f825)
    authority   operator directive "SFE CAMPAIGN 6 -- CAMBRIAN EXPANSION / OBSERVATORY STRESS"
                (roles/Proteus/prompts/2026-09-18_campaign6/, MANIFEST beside it); the operator's
                Campaign 5 closure (archaeon/campaign5/CAMPAIGN_REPORT.md s6a, D5-015): "Next work
                must alter generative/search structure -- the searchable program structure or
                grammar of useful behaviours -- not continue fault-boundary tuning: the failure has
                moved upstream." Representation B handed to Proteus as an instrument, not a VM.
    status      SCOPE AND DESIGN v0, read-only. Nothing minted; the frozen v0 substrate (runtime
                73f110e2 / grammar v0.4 / affordances v0 / profile pfp1:625bc70456ebfa20) is
                UNTOUCHED and becomes Campaign 6's CONTROL substrate.
    currency    2026-09-18

-----------------------------------------------------------------------------------------------
## 0. What changed since the point-release review (2026-09-17), and what it means for Axis O

On 09-17 this seat wrote "organism expressiveness is not the frontier constraint" and rejected a
new ISA primitive. That was about EXPRESSIVENESS and it stands: the keyed memory is a 12-
instruction program in the frozen ISA. Campaigns 4 and 5 then measured the SEARCH STRUCTURE of
the same substrate and retired it:

    C4-01/02  the damage boundary is a cliff: an edit leaves the answer vector untouched or
              replaces most of it; 1-3% fall between; no single edit (0/5,472) and no random
              multi-step edit (0/2,280) improved any parent on its own environment
    C4-03     the interpreter is total: 932/932 parent words decode by modulo; there is no
              invalid operation, no local failure, nothing to insulate
    C4-04     addressing damage: insertion +.215 and movement +.193 above the pooled effect --
              structural operators break routing because jump targets are positions
    C4-05/06  the neutral network is large and cheap to walk (188/188 to depth 16) and buys
              exaptation .016 -> .043, under the bar; splice births are 8 points less viable and
              add no novelty; nothing crosses the W2_K2 valley
    C4-08     selection builds robustness as LENGTH and behavioural neutrality (19 -> 62
              instructions; coherent share .15 -> .04), not as a structural mechanism
    C5 A      OLD_SUBSTRATE_EXHAUSTED: the deep walk's gradient is bought by evaluations a single
              edit spends as well; in most cells the elite IS the starting parent after 36,000
              evaluations. "Selection under the frozen grammar does not climb these worlds at all."
    C5 B      a narrow encoding (Representation B) creates a real, countable, cheap local failure
              -- and buys no discovery at equal compute (0 held-out gains in 96 cells)

Reading for Axis O, stated as the seat's stand: the flat 4-word genome plus a SYNTACTIC grammar
(twelve operators over aligned instruction blocks, blind to function) is a search structure whose
units of variation are positions, not parts. Every structural operator the directive lists
already exists in v0.4 (duplication, deletion, movement, splice, insertion) and every one of them
was measured destructive or inert, because there is no organism-side object for them to copy,
disconnect, reconnect or rewire: a "functioning structure" in a flat genome is a set of addresses
whose meaning depends on where it sits. The directive's own list -- reusable substructures,
callable subgraphs, evolvable interfaces between modules, rewiring that preserves components --
names the missing object exactly: an organism whose genome is a GRAPH of small primitive nodes,
where structure is connectivity, and where the mutation grammar acts on connectivity.

That is a NEW runtime profile, not an edit. The frozen v0 stays as the control (directive: "one
available substrate/control"); Representation B stays as a second instrument (adopted under
proteus/ verbatim, s5). The prior rule "do not add an opcode: it re-decodes every genome" is
untouched: a graph organism is a different runtime with its own hash; no v0 genome is re-keyed.

-----------------------------------------------------------------------------------------------
## 1. Axis O requirement -> what exists in v0 -> what the graph profile supplies

    requirement                       frozen v0 (control)                        graph profile (proposal, s2)
    persistent internal state         EXISTS: persist in {none,regs,tape,all}    node state slots with per-node persist flag
    reusable substructures            ABSENT: positions, no parts                 a subgraph is a part; COPY is a grammar op
    conditional routing               EXISTS as JZ/JNZ on immediate offsets;      routing is an EDGE from a predicate port;
                                      breaks under movement (C4-04)               moving a subgraph moves its edges with it
    duplication / deletion            EXIST, syntactic, blind (v0.4)              SUBGRAPH_COPY / SUBGRAPH_DELETE by connectivity
    rewiring                          reference_redirection on operand words       EDGE_RETARGET (keeps both endpoints' nodes)
    parameter mutation                operand_perturbation / config_perturbation  NODE_PARAM (immediates, thresholds, slot ids)
    structural mutation               insertion/deletion/movement/region_swap     NODE_ADD / NODE_REMOVE / SUBGRAPH_MOVE
    callable or recurrent subgraphs   ABSENT: no indirect jump, no return          CALL edge into a subgraph with a return port;
                                                                                   back-edges permitted (recurrence) under the
                                                                                   op budget
    inherited state/configuration     EXISTS (persist; manifest limits)           node-level persist + inherited slot values
    evolvable interfaces between      ABSENT (no module)                           a subgraph's boundary ports ARE its interface;
    modules                                                                        mutable by EDGE ops only
    variable organism size            EXISTS                                       node count within a published bound
    copy functioning structure        no notion of "functioning"                   COPY of the statically CONNECTED component
                                                                                   containing a chosen node (function = reach)
    insert copied structure elsewhere insertion of random words only               COPY + REATTACH at a chosen port set
    disconnect without deleting       accidental (unreachable code; C5-08: 11%)    EDGE_CUT: nodes persist, provably neutral
    reconnect neutral structure       accidental (a jump landing on dead code)      EDGE_ADD from live port to a dormant node
    alter routing, preserve parts     no                                           EDGE_RETARGET by definition
    neutral structural growth         insertion into unreachable region            NODE_ADD unconnected (dormant by construction)
    ancestry to reconstruct the change lineage_record.v0: operators + seeds + pre/   the same, PLUS an explicit edit list per child
                                      post hash (replayable, not diffable)          (which nodes/edges/params; diff = the record)

-----------------------------------------------------------------------------------------------
## 2. Proposal: `proteus.graph_organism.v1` (design only; a NEW runtime, v0 untouched)

Primitives stay SMALL and stay the v0 affordance classes (R1 ontology gate: arithmetic,
comparison, branch = routing, memory read/write = state slots, indirection, costed random draw,
opaque channel I/O). No node is named for a function. A genome is:

    nodes[]   {node_id, kind in AFFORDANCE_KINDS_V1 (the 25 v0 semantics minus positional jumps,
               plus ROUTE and CALL/RETURN as routing affordances), params (immediates), state_slot
               or null, persist flag}
    edges[]   {from_node, from_port, to_node, to_port}   data edges (values) and control edges
              (which node runs next); a ROUTE node has two control out-ports selected by its
              predicate input; CALL has an entry edge into a subgraph and a RETURN port
    entry     the node that runs first each tick
    limits    max_nodes, max_ops_per_tick, state_words, out_cap (manifest limits, as today)

Execution: one tick = follow control edges from `entry`, each node consuming its data inputs
(default 0 when unconnected, exactly as v0's IN on an empty channel) and writing its outputs;
budget counted in node executions; HALT/YIELD nodes end the tick; every unconnected node is
DORMANT (never runs, costs nothing) -- neutral structure is first-class, not an accident of
jump targets. Determinism and replay as v0 (SplitMix64, externally supplied random stream).

Grammar `proteus.graph_grammar.v1` (pre-registered masses, subtraction mass non-zero, R4):
    NODE_ADD (dormant) / NODE_REMOVE / NODE_KIND / NODE_PARAM / EDGE_ADD / EDGE_CUT /
    EDGE_RETARGET / SUBGRAPH_COPY (connected component of a chosen node, copied dormant) /
    SUBGRAPH_COPY_ATTACH (copy + attach its boundary ports to chosen live ports) /
    SUBGRAPH_MOVE (re-attach a component's boundary to other ports) / CROSSOVER_SUBGRAPH
    (take a connected component from a mate, attach dormant or live) / STATE_SLOT_PERTURB.
Every operator is defined over connectivity, never over positions; every operator records the
exact node/edge/param delta in the child's lineage record.

Ancestry (directive: "reconstruct exactly what changed"): `proteus.lineage_record.v1` adds
`edits: [{op, nodes_added, nodes_removed, edges_added, edges_cut, params_changed}]` beside the
v0 fields; a child's genome must equal parent + edits (asserted by test) and the pre/post hashes
still bind it.

Behavioural fingerprint T0 (Axis T, organism side; `proteus.behavior_fingerprint.v1`), one
object per evaluation, deterministic (no timings -- the T2 rule of 09-05, 40/40 reproduced):
    v0 and graph alike:  ops_by_category, branches/routes taken, in/out counts per channel,
                          out values summary (count, distinct, first-8 hash), budget_exhausted
                          ticks, state slots/tape addresses WRITTEN (set size + hash of the set),
                          registers/slots READ, RND draws
    graph only:          node execution counts (which parts ran), route decisions per ROUTE
                          node, CALL depth reached, dormant-node count, connected-component
                          count, boundary-port count per component
    plus the structural descriptor of the genotype (P3) so genotype and phenotype structural
    change are both fingerprinted.
Comparison against ancestors/siblings/peers/other worlds is a distance over these fields, which
is Archaeon's/Harmonia's to define; Proteus supplies the fields and their reproducibility proof.

Escalation (protocol steps 1-9, organism side) is R8 already written as code paths: freeze =
manifest + lineage_record + checkpoint (lineage.checkpoint/restore exist); replay packet = seed +
runtime hash + grammar hash; ablation set (anatomy.py knockouts -> per-NODE knockouts for the
graph); neighbourhood under each operator (P6 stratifier, PROTEUS-34); matched fresh controls
(generate under the same profile). Parent/ancestor/sibling RETRIEVAL is the executor's record
(Vivarium/Archaeon), not Proteus's.

-----------------------------------------------------------------------------------------------
## 3. Neutrality risks, named before the build (R1 ontology gate, R7 lens rule)

    risk                                       guard
    "module" becomes a semantic unit            a component is defined by CONNECTIVITY only; no
                                                node kind, param or name says "module"; the
                                                quarantine string audit runs on the graph runtime
    CALL/RETURN smuggles a program theory        CALL is a routing affordance (control edge with a
                                                return port); it has no notion of arguments beyond
                                                data edges; the R1 table row must justify it as
                                                "indirection over control", or it is dropped and
                                                recurrence alone is kept (back-edges)
    the grammar's masses author a growth ladder  R4 neutrality run under no selection for the
                                                graph grammar before any world sees it; the V0.5
                                                current instrument as DETECTOR (Harmonia #412);
                                                absence of current is NOT claimed
    dormant structure is free                    dormant nodes cost nothing per tick BUT count
                                                against max_nodes and are reported in the
                                                fingerprint; whether a world charges structure is
                                                the world's (Axis W cost channels)
    a graph organism cannot enter old worlds     the world ABI is unchanged (A1 opaque channels):
                                                IN/INQ/OUT nodes speak the same channel protocol,
                                                so W0..W7 and the 57 C4 parents' worlds run
                                                graph organisms without change; the frozen v0
                                                population stays the control in every cell
    Proteus designs toward Axis O's list         the list is the operator's; the seat's addition is
                                                only "connectivity is the unit"; every item is
                                                mapped in s1 to an existing v0 fact

-----------------------------------------------------------------------------------------------
## 4. Sequencing (nothing below runs science; Archaeon runs Campaign 6)

    step  what                                                     needs                  owner
    1     THIS scope + Stage 3 criticism from Archaeon (world ABI    now                    Proteus, peers
          stays A1 channels?), Harmonia (R4 + current battery for a
          graph grammar), Vivarium (fingerprint fields it will carry)
    2     Adopt Representation B verbatim under proteus/repb/ as      D5-015 "default yes"   Proteus
          `proteus.runtime_profile.repb.v1` (hash, tests, catalog
          row); an INSTRUMENT, not the platform VM
    3     graph_organism.v1 runtime + generate + validate + replay   operator: open ONE new  Proteus
          tests; quarantine audit extended; fingerprint.v1 for v0    runtime profile (this
          AND graph; lineage_record.v1 edits                          is the PROTEUS-19 class
                                                                      decision, now motivated
                                                                      by C5 s6a)
    4     graph_grammar.v1 + R4 neutrality + current detector run;    step 3; Harmonia's      Proteus (build),
          catalog rows; population_manifest for a mixed v0/graph      battery                Harmonia (qualify)
          start population (the profile per member is already a
          field)
    5     expressiveness witnesses on the graph substrate (keyed      step 3                 Proteus
          memory, delay reader) + the same programs' NEIGHBOURHOOD
          anatomy per operator -- the C3/C4 controls re-measured on
          the new geometry BEFORE any world
    6     hand to Archaeon: profiles, start populations, fingerprint  steps 4-5              Archaeon
          fields, ablation/neighbourhood tools; Proteus never picks
          the worlds, the pressures or the winners

Estimated size: step 3 is the largest Proteus build since V0 (M-L); steps 2, 4, 5 are M each.
None starts before step 1's peer answers and the operator's step-3 decision. The frozen v0 and
the 57 C4 parents remain available for every Campaign 6 control cell throughout.

-----------------------------------------------------------------------------------------------
## 5. Representation B (C5), adoption stance

D5-015 hands `archaeon/campaign5/repb/{vm_b, gen_b, grammar_b, evaluate_b, evolve_b}.py` to
Proteus "for adoption after (default yes)" as an experimental instrument. Stance: adopt the
RUNTIME and GENERATOR halves (vm_b, gen_b, grammar_b) under proteus/repb/ byte-identical with a
hash and the C5-03 qualification cited, as a catalog profile with its own kernel qualification
("qualified under D5-008 post-hoc amendment; a01 PREREGISTRATION_FAILED") carried on the row;
evaluate_b/evolve_b are selection-side and stay Archaeon's. Adopted, not promoted: no world
defaults to it, and the directive's "do not promote merely for Campaign 6" is honoured by
keeping it out of DEFAULT_FOUNDRY_MANIFEST and out of the graph profile's design.

-----------------------------------------------------------------------------------------------
## 6. What Proteus will NOT do in Campaign 6

Choose worlds, pressures, schedules or fixtures; know where planted fixtures are (the seat that
supplies organisms must not know where the anti-gravity fixtures sit, or its ablation sets could
leak them); run detectors; score an organism; declare a mechanism (UNKNOWN_MECHANISM is a label
Archaeon/Harmonia apply; Proteus only ever says "expressible / reachable / neutral / different").

-----------------------------------------------------------------------------------------------
## 7. Falsifiers of this scope, written to be lost

- If the graph grammar's per-operator neighbourhood anatomy (step 5) shows the SAME cliff as v0.4
  (destructive share ~.36, useful ~1/4,800) on the same witness programs, "connectivity is the
  unit" bought nothing and the profile is a second exhausted substrate; say so and stop.
- If Harmonia's R4 run shows the graph grammar grows genomes by default under no selection, the
  masses are an authored ladder and the profile does not enter any world until re-massed.
- If Representation B's FIZZLE mode, adopted as a control, matches the graph profile on every
  Campaign 6 control cell, the graph profile's extra machinery is not earning its complexity.
- Not worth continuing: if the operator reads C5 s6a as "alter the GRAMMAR of behaviours" meaning
  a behaviour-library / composition layer above organisms (Archaeon's or Vivarium's lane) rather
  than the organism representation, this document is filed as design residue.

-----------------------------------------------------------------------------------------------
## 8. Conflicts

The seat that built and defended the frozen substrate for a week now proposes to build its
successor: the incentive runs toward the build. The guard is the sequence in s4 (operator
decision before step 3; Harmonia qualifies the grammar; Archaeon runs the science; the frozen
v0 is the control in every cell) and the falsifiers in s7.
