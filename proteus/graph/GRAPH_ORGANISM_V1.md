# proteus.graph_organism.v1 -- the graph organism runtime profile

    opened      2026-09-18, operator ruling "Yes" to PROTEUS-43 (roles/Proteus/prompts/2026-09-18_campaign6/
                01_OPERATOR_RULING_PROTEUS-43.md): ONE new runtime profile for Campaign 6, v0 frozen as control
    identity    runtime proteus.runtime.graph.v1 (proteus/graph/identity.py RUNTIME_HASH, sha256 over the
                LF-normalised affordances.py + vm.py + grammar.py + the node-kind table hash); grammar
                proteus.graph_grammar.v1; profile pfp1:2595e1aefd59975f (proteus/graph/GRAPH_PROFILE_CATALOG.json).
                The profile id moved once after the opening receipt (pfp1:3081a8ef...) when GraphMeter.as_dict
                gained the v0 call shape (vm.py is a runtime source); both ids are in the receipt
    v0          UNTOUCHED: runtime 73f110e2..., grammar v0.4, affordances v0, catalog 42e4db36... recompute
                byte-identically (test_graph_profile.py::test_v0_catalog_is_untouched_by_the_graph_package)
    status      BUILT and controlled; NO world has run it; its own falsifier (PROTEUS-46) FAILED as formulated
                (s5); graph-dependent frontier transformations blocked as formulated, reopen conditions stand
    currency    2026-09-18

## 1. Why a graph (the evidence, one line each)

C4-01/02: the flat genome's damage boundary is a cliff at every radius. C4-03: the v0 interpreter is
total -- nothing to insulate. C4-04: insertion (+.215) and movement (+.193) break routing because jump
targets are positions. C4-06: splice births are 8 points less viable and add no novelty. C4-08:
selection builds LENGTH and neutrality, no structural mechanism. C5 Phase A: OLD_SUBSTRATE_EXHAUSTED;
"selection under the frozen grammar does not climb these worlds at all." Operator (D5-015): "the failure
has moved upstream" to the searchable program structure. Every structural operator the Campaign 6
directive lists already existed in grammar v0.4 and was measured inert or destructive because a flat
genome has no PART -- a functioning structure is a set of addresses whose meaning depends on position.
Here structure is connectivity, and the grammar acts on connectivity.

## 2. Genome

    nodes[i]        {kind, params, persist}      kind from the 25-row table (s3); params = one immediate for
                                                 CONST only; persist keeps the node's value across ticks
    data_edges      [src, dst, port]             at most one per (dst, port); an unconnected input reads 0
    control_edges   [src, port, dst]             at most one per (src, port); no edge on the selected port ends
                                                 the tick (halt)
    entry           first node on a fresh tick
    limits          state_words 4..1024, tick_budget 4..4096 node executions/tick, out_cap 1..64,
                    call_depth_max 0..16, persist_state (bool), n_nodes 1..256
    canonical form  edges sorted, params lists, persist explicit -> organism_id = sha256 over it; two genomes
                    with the same connectivity hash the same (vm.canonicalize)

DORMANT: a node that is neither the entry nor the target of any control edge never executes and costs
nothing (vm.live_nodes). Neutral structure is first-class, not an accident of jump targets.

## 3. Node kinds (the R1 affordance table; proteus/graph/affordances.py, AFFORDANCE_HASH)

Categories are v0's nine. Removed relative to v0: JMP/JZ/JNZ (positional). Added: ROUTE (a predicate
selects control port 0 or 1) and CALL/RETURN (indirection over CONTROL: CALL pushes its `after` port on a
bounded stack and enters `body`; RETURN pops; at the depth limit CALL continues at `after` without
pushing and the meter counts the refusal). Renamed for the graph: LDC -> CONST, MOV -> ID (a wire).
LD/ST address a state array (indirection). IN/INQ/OUT speak the SAME opaque channel protocol as v0 (A1),
so every existing world runs a graph organism unchanged.

R1 justification of the two new control rows, stated for the reviewer: ROUTE is "branch" -- v0 had it as
JZ/JNZ over positions; CALL/RETURN is "indirection" applied to control instead of data, with no
arguments, no names, no notion of a procedure: a subgraph is only a connected set of nodes. If the
reviewer rejects CALL/RETURN, recurrence remains through back-edges and the two rows are removed in a
new runtime version; nothing else in the design depends on them.

## 4. Grammar (proteus/graph/grammar.py, GRAMMAR_HASH carries the weight vector)

Thirteen operators over connectivity, each producing an EDIT LIST of primitive edits; the child IS
`apply_edits(parent, edits)`; the lineage record (proteus.lineage_record.v1) carries the edits and
`verify_record` replays them (test: 300 random descents rebuild byte-for-byte; a tampered record is
refused). Masses pre-registered; R4 measured under NO selection (3 seeds x 100 organisms x 60-100
mutations): node-count drift -0.0023 / +0.0016 / -0.0069 per step at the shipped masses (.07 NODE_ADD /
.11 NODE_REMOVE), inside the pre-registered |drift| <= 0.02 band; the two earlier mass drafts
(-0.026 shrink; +0.006/+0.019 growth) are kept in the grammar docstring. Mutation current: NOT measured
(the V0.5 instrument is admitted as a detector only, Harmonia #412); no neutrality claim is made.

## 5. Witness (proteus/graph/witness.py, KEYED_MEMORY_WITNESS_GRAPH.json)

The keyed two-value memory of the v0 witness, as connectivity: 12 nodes, 72 ops on the two-key probe
(v0: 12 instructions, 81 ops); 6/6 and 16/16. One-value control exactly 3/6 (the shelf); inert 0/6; echo
0/6 on the honest probe, 6/6 only when the probe leaks. Expressiveness is held EQUAL across the two
substrates, so PROTEUS-46's second half -- per-operator neighbourhood anatomy of the same programs under
graph_grammar.v1 vs v0.4 -- compares SEARCH geometry with expressiveness controlled. That measurement is
the falsifier of this whole profile.

RESULT (2026-09-18, preregistered at main eb58691fc, proteus/round2/PROTEUS-46_FALSIFIER.{json,md}):
CLIFF_SURVIVES -> FALSIFIER_FAILED as formulated. One-value parent, two-key probe, K=400 per
operator: USEFUL 0/4,267 (v0.4) vs 0/4,881 (graph); GRADED_DOWN .0075 vs .0006 (floor .0028);
DESTROYED .70 vs .36; NEUTRAL .27 vs .64. Greedy 3-step search (width 50) never scored above the
parent's 3/6 on EITHER substrate: the one-value -> two-value step is a coordinated change with no
intermediate the probe can see, in both representations. Connectivity edits made the neighbourhood
SAFER (the dormant-attach operators are neutral by construction), not more GRADED. Under the operator's
ruling of 2026-09-18 this is FALSIFIER_FAILED / blocked as formulated, NOT retirement: one hand-written
parent pair on one probe exhausts nothing, and the reopen conditions (a different topology of the same
function, a different operator set or mass profile, a developmental regime, a representation change)
stand. The profile stays available as a substrate; the claim "connectivity removes the cliff" is dead.

## 6. Fingerprint fields (Axis T, organism side; GraphMeter.as_dict)

ops, ops_by_category, node_exec (per node), nodes_executed, route_taken per ROUTE node,
call_depth_max_reached, call_depth_refused, in_reads/out_writes/out_dropped, rnd_draws, state_writes,
state_addresses_written, ticks, budget_exhausted_ticks, statuses. No timings (the 09-05 lesson).
`proteus.behavior_fingerprint.v1` (PROTEUS-45) wraps these for both substrates.

## 6a. Handover to executors (proteus/graph/handover.py)

`substrate_of / player_for / meter_for / organism_record_for / descend_for / generate_for /
fingerprint_for` dispatch on the manifest's schema_version with the exact v0 call shapes Archaeon's
evaluator and segment loop already use; a v0 manifest can never receive the graph runtime hash or
vice versa, and a cross-substrate mate is refused. `resolve_profile("graph")` in the executor is
then: evaluate built on player_for/meter_for; descend_for; answers built on player_for. Start
populations for graph transformations come from generate_for(graph foundry manifest) -- v0 parents
cannot be lifted into graph form and no lift is offered.

## 7. What this does NOT do

Run a world (none has run it). Score an organism. Choose Campaign 6 cells, pressures or fixtures. Promote
Representation B (adoption is PROTEUS-42, separate). Change anything under proteus/foundry.

## 8. Tests (proteus/tests/test_graph_*.py)

identity new + v0 untouched; replay byte-identical over a random population; dormant costs 0 and changes
nothing; ROUTE by predicate and behaviour invariant under re-indexing; CALL/RETURN reuse from two sites
and depth refusal; YIELD/HALT resume; persistence flags; validation refusals; live-node/ABI shape; import
hygiene (only stdlib + proteus.foundry.{prng,identity}); grammar reconstruction + determinism + operator
shapes + R4 band + weight-bearing hash; witness controls; profile recompute + no-alias + v0 catalog frozen.
