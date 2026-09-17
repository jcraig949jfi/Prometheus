"""Cut: clips-6.4.2-nasa (the CLIPS production-rule engine; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; position 23 of the
2026-09-17 NOT_CUT order). Read: core/drive.c NetworkAssert / NetworkAssertRight 84-330 (the join network's right activation);
core/agenda.c 100-330 (activation placement, salience groups, strategy hooks, GetNextActivation); core/engine.c Run() head. NOT read:
rulebld.c (network construction), reteutil.c (beta memories, hashing), the pattern (alpha) network, factmngr.c, the object system,
the 340 other files. Nothing ran (C; not on M3).
"""
from nyx.atlas.author import Cut

D = "vault:clips-6.4.2-nasa/upstream/tree/clips_core_source_642/core/drive.c"; A = "vault:clips-6.4.2-nasa/upstream/tree/clips_core_source_642/core/agenda.c"; E = "vault:clips-6.4.2-nasa/upstream/tree/clips_core_source_642/core/engine.c"
c = Cut("clips-6.4.2-nasa", mode="ANCESTRY_AWARE", inspected=["core/drive.c 84-330", "core/agenda.c 100-330", "core/engine.c Run() head"], evidence=[("SOURCE_READ", D + ":84-330"), ("SOURCE_READ", A + ":100-330"), ("SOURCE_READ", E + ":1-80")],
        note="a Rete engine: facts enter a join network from the right, are matched against the left memory of each join by hash then by test expression, and successful partial matches drive down to the next join; a complete match becomes an activation placed on an agenda ordered by salience group and a strategy; Run pops and fires; the three are separable and are the three files read")

join = c.organ("join_node_activation_from_the_right_with_hashed_left_memory_and_a_network_test_expression", human_name="NetworkAssert / NetworkAssertRight / EvaluateJoinExpression / PPDrive (drive.c)", status="ACCEPTED",
    mechanism="a new partial match entering a join from the right (a new fact) is compared against the join's left beta memory, fetched by hash value so only bucket-mates are scanned; matching hash and no blocking marker lead to the join's compiled test expression (variable bindings across patterns); success drives the combined partial match to the child joins (PPDrive); negated and exists patterns instead add blocked links and retract dependents; the first join of a rule short-circuits (EmptyDrive); incremental reset can skip joins not being rebuilt",
    input="a partial match from the alpha side; the join's left memory", output="new partial matches downstream, or blocked links", state="beta memories (per join, hashed), markers, blocked links", update="per fact assert/retract",
    assumptions=["most joins fail early, so hashing the beta memory on the join's equality tests pays; state (partial matches) is retained between cycles so matching is incremental (the Rete premise: many rules, slowly changing facts)"],
    fitness_value_in_ancestor="matching cost per fact change is proportional to the change, not to the rule base", failure_landscape="by reading: beta memories can grow combinatorially on cross-product joins (the classic Rete failure); the DEVELOPER counters in the source measure exactly that",
    human_prior="Forgy 1982 Rete; the hashed beta memories are CLIPS 6.30's addition", evidence_ref=D + ":84-330", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="drive.c's assert path",
    coverage={"input_topology": "GRAPH", "output_topology": "SET", "state_amount": "SUPERLINEAR", "state_persistence": "PERSISTENT", "memory": "ARCHIVE", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN", "failure_mode": "DEGRADES"})

agenda = c.organ("agenda_of_activations_ordered_by_salience_group_then_conflict_resolution_strategy", human_name="AddActivation / PlaceActivation / salienceGroup / GetNextActivation (agenda.c); Strategy (depth, breadth, LEX, MEA, complexity, simplicity, random)", status="ACCEPTED",
    mechanism="a complete match becomes an activation carrying the rule, the matched facts, a time tag and a salience (evaluated when defined, at activation, or every cycle per a setting); activations live in per-module agendas partitioned into salience groups (a linked list ordered by salience, reused per value); within a group a strategy orders them (default DEPTH: newest first; also breadth, LEX and MEA on fact recency, complexity/simplicity on rule size, random); Run takes the first",
    input="complete matches", output="the next rule to fire", state="the agenda lists; salience groups", update="per match and per fire",
    assumptions=["the programmer's salience says what matters; the strategy breaks ties; nothing about the facts' content beyond recency is used"], fitness_value_in_ancestor="the only place 'which rule when' is decided; every expert-system control idiom is a salience/strategy pattern",
    failure_landscape="by reading: salience is a global scalar, so control logic leaks into rule priorities (the well-known expert-system maintenance problem)", human_prior="OPS5's conflict-resolution strategies (Forgy) with CLIPS's salience groups as an efficiency structure",
    evidence_ref=A + ":100-330", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="agenda.c's placement and retrieval",
    coverage={"input_topology": "SET", "output_topology": "SCALAR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "stochasticity": "SEEDED_RANDOM", "update_topology": "PRIORITY", "competition": "ARBITRATES"})

run = c.organ("recognise_act_cycle_that_pops_an_activation_fires_its_actions_and_re_enters_matching", human_name="Run() (engine.c)", status="CANDIDATE",
    mechanism="while activations remain and the run limit is not reached: take the first activation, mark the rule firing, evaluate its right-hand side (which asserts/retracts facts, re-entering the join network immediately), count the firing, handle garbage collection of transient values and the debugging watches; a re-entrant call is refused (AlreadyRunning)",
    input="the agenda", output="fired rules; changed facts", state="the fact base; the agenda", update="per cycle", assumptions=["a rule's actions change the world and the match is incremental, so the cycle is match-select-act with match amortised"],
    fitness_value_in_ancestor="the production-system loop; everything else exists to make its match step cheap", failure_landscape="UNKNOWN by run", evidence_ref=E + ":Run() head (read to the statistics block only)", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="Run(); CANDIDATE because only the head was read",
    coverage={"input_topology": "SET", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "feedback": "CLOSED_LOOP", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN"})

c.reject("rulebld.c (compiling rules into the network), reteutil.c (beta memory structures, hashing), the alpha/pattern network, factmngr.c, deftemplates, the object system (COOL), the parser and I/O, the 340 other files", reason="OTHER", evidence="NOT READ (~170,000 lines); residue", note="rulebld.c is where node sharing between rules (Rete's other half) is decided; unread")
c.reject("'expert system shell' / 'Rete' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the join network, the agenda and the cycle are three files with three separable mechanisms; Rete names only the first")

c.edge(join, agenda, "feeds", note="complete matches"); c.edge(agenda, run, "feeds"); c.edge(run, join, "feeds", note="asserts and retracts re-enter the network")

c.pressure("many_condition_action_rules_must_be_matched_against_a_slowly_changing_set_of_facts_at_a_cost_proportional_to_the_change",
    condition="R rules with multi-pattern conditions over F facts; each cycle changes a few facts; the organism must find every newly satisfied rule instance and choose one to fire", resource_or_constraint="memory for retained partial matches; time per fact change",
    failure_condition="re-matching every rule against every fact per cycle (cost R x F^k), or memory blow-up on cross-product joins", world_punishes="stateless matching; unhashed joins", world_rewards="retained, hashed partial matches shared across rules",
    observable_consequence="time per cycle vs R and F with the beta memories enabled vs disabled; memory vs join selectivity", vacuity_condition="one rule or one fact change per run", trivial_shortcuts="a world where facts never change",
    cheat_control="an organism told which rules changed status must fire the same sequence at zero match cost; naive re-matching must show the R x F^k scaling: the world must show both",
    cost_class="CPU-scale", source_evidence="drive.c; agenda.c; record tags production-rules / pattern-matching", purpose="PURPOSE: production-rule inference (CLIPS, NASA 1985-)")

c.ancestry("algorithm_from", "Forgy 1982 (Rete); OPS5 conflict resolution; CLIPS at NASA JSC from 1985", note="from the code and the record")
c.residue("LARGE_RESIDUE", ["only three of 345 files read", "network construction and node sharing unread", "nothing ran"], note="the three mechanisms that define a production system are located; the engine's size is why this is COARSE")
c.save(state="COARSE")
