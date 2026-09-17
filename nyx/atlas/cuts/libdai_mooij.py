"""Cut: libdai-mooij (libDAI, Mooij; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; position 27 of the 2026-09-17 NOT_CUT order).
Read: src/bp.cpp -- run() 261-353 (the three update schedules, convergence test), calcNewMessage() 207-259 (the product/marginal
step), function list. NOT read: the other 20+ inference algorithms (junction tree, mean field, TRW, GBP, Gibbs, ...), the factor
graph and region graph classes, the tests. Nothing ran (C++; not on M3).
"""
from nyx.atlas.author import Cut

B = "vault:libdai-mooij/upstream/tree/src/bp.cpp"
c = Cut("libdai-mooij", mode="ANCESTRY_AWARE", inspected=["src/bp.cpp: run, calcNewMessage, beliefV, function list"], evidence=[("SOURCE_READ", B + ":207-353")],
        note="loopy belief propagation on a factor graph, cut where libDAI differs from the LDPC decoder in the vault: three message schedules (parallel, sequential random, sequential by maximum residual), a log-domain option, sum-product vs max-product in one code path, and convergence measured on beliefs, not messages")

msg = c.organ("factor_to_variable_message_as_the_marginal_of_the_factor_times_all_other_incoming_messages", human_name="BP::calcNewMessage / calcIncomingMessageProduct (bp.cpp 164-259)", status="ACCEPTED",
    mechanism="for edge (variable i, factor I): multiply the factor by every message into I except the one from i (extrinsic), then sum out (SUMPROD) or max out (MAXPROD) every variable but i, normalise, store as the NEW message (not yet applied); in log domain the product is a sum with the max subtracted before exponentiation; a unary factor short-circuits to its own table",
    input="the factor table; incoming messages", output="a new message (a distribution over i's states)", state="new-message buffer per edge", update="per edge visit",
    assumptions=["the graph is a tree, or close enough that extrinsic products approximate marginals (the 'loopy' assumption)"], fitness_value_in_ancestor="the sum-product rule in its general form, one code path for MAP (max) and marginals (sum)",
    failure_landscape="by reading: on loopy graphs messages can oscillate or converge to wrong marginals; libDAI's damping (not read) and the schedules exist because of that", human_prior="Pearl 1988 / Kschischang, Frey & Loeliger 2001 sum-product", evidence_ref=B + ":164-259", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the two functions",
    coverage={"input_topology": "GRAPH", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "DETERMINISTIC", "uncertainty": "DISTRIBUTION", "hidden_state": "ESTIMATES"})

sched = c.organ("three_message_schedules_parallel_random_sequential_and_maximum_residual", human_name="BP::run (bp.cpp 261-353): PARALL, SEQRND, SEQMAX; findMaxResidual / updateResidual", status="ACCEPTED",
    mechanism="PARALL: compute every new message from the old ones, then apply all (Jacobi); SEQRND: shuffle the edge list each iteration and compute-and-apply edge by edge (Gauss-Seidel in random order); SEQMAX: keep a priority queue of residuals (L-inf distance between a computed new message and the current one), always apply the edge with the largest residual, then recompute the residuals of the messages it influences",
    input="the schedule setting; residuals", output="the order of updates", state="the residual heap (SEQMAX); the edge permutation", update="per iteration",
    assumptions=["on loopy graphs the schedule changes both speed and WHETHER convergence happens; residual scheduling (Elidan, McGraw & Koller 2006) converges where parallel does not"],
    fitness_value_in_ancestor="the same messages under three orders, selectable at run time; the residual schedule is the library's edge over a textbook BP", failure_landscape="by reading: SEQMAX's queue makes each update O(log E); the parallel schedule can oscillate with period 2 on bipartite structures",
    evidence_ref=B + ":261-353, 155-163, 463-472", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the schedule branches in run() and the residual helpers",
    coverage={"input_topology": "GRAPH", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "SEEDED_RANDOM", "update_topology": "PRIORITY", "order_sensitivity": "SENSITIVE", "failure_mode": "OSCILLATES"})

conv = c.organ("convergence_declared_on_the_maximum_change_of_any_belief_not_of_any_message", human_name="BP::run: maxDiff over beliefV/beliefF vs _oldBeliefs; props.tol, maxiter, maxtime", status="ACCEPTED",
    mechanism="after each iteration every variable and factor belief is recomputed and compared (L-inf) with the previous iteration's; the largest change is the convergence measure; the loop stops when it falls below tol, or at maxiter, or at maxtime seconds; the final maxDiff is reported (and warned about) either way",
    input="beliefs per iteration", output="maxDiff; a stop decision", state="_oldBeliefsV/F", update="per iteration", assumptions=["belief stability is what the user cares about; messages may keep changing in ways that cancel"],
    fitness_value_in_ancestor="a stopping rule on the observable quantity, with three independent budgets", failure_landscape="by reading: recomputing all beliefs per iteration costs as much as an iteration; on oscillation maxDiff never falls and the run ends by budget with a warning, not an error",
    evidence_ref=B + ":304-352", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the tail of run()",
    coverage={"input_topology": "VECTOR", "output_topology": "DECISION", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "DETERMINISTIC", "resource_dependence": "TIME"})

c.reject("the other inference algorithms in libDAI (exact junction tree, mean field, TRW-BP, generalised BP, Gibbs, LC, ...), the factor graph / region graph data structures, the MATLAB/Python bindings, the tests", reason="OTHER", evidence="NOT READ (~30,000 lines); residue", note="the junction tree (exact) is the oracle for a Stage C world on small graphs, in the same body")
c.reject("'belief propagation' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the message rule, the schedule and the stopping rule are separately replaceable; the vault's ldpc-codes-neal-2001 (cut 09-17) holds the same message rule with a fixed parallel schedule and a parity-check stopping rule", note="RECURRENCE candidate R1: the sum-product message rule in ldpc dec.c iterprp vs bp.cpp calcNewMessage")

c.edge(sched, msg, "schedules"); c.edge(msg, conv, "feeds"); c.edge(conv, sched, "gates", note="stop"); c.edge(msg, sched, "feeds", note="residuals")

c.pressure("beliefs_on_a_cyclic_constraint_graph_must_be_refined_by_local_messages_whose_order_of_application_decides_whether_they_settle_at_all",
    condition="the same local message rule as on a tree, but the graph has cycles; the organism chooses the order in which edges are updated; some orders oscillate", resource_or_constraint="updates per iteration; a residual heap or a random permutation",
    failure_condition="no convergence within the budget, or convergence to beliefs far from the exact marginals", world_punishes="parallel updates on bipartite-like structure; wasted updates on edges that are already settled",
    world_rewards="updating where the residual is largest", observable_consequence="iterations to tol and final belief error vs the junction-tree oracle, per schedule, on graphs with increasing cycle count",
    vacuity_condition="a tree (any order converges in one sweep)", trivial_shortcuts="exact inference on small graphs", cheat_control="the exact junction tree (in the body) is the ceiling; the parallel schedule on a 4-cycle with strong couplings must oscillate: the world must show both",
    cost_class="CPU-scale", source_evidence="bp.cpp run(); record tags approximate-inference / factor-graphs", purpose="PURPOSE: approximate inference on factor graphs (libDAI, Mooij 2010)")

c.ancestry("algorithm_from", "Pearl 1988; Kschischang et al. 2001; residual BP (Elidan et al. 2006)", note="from the code's schedule names; not verified against the record")
c.residue("PARTIALLY_EXPLAINED", ["only bp.cpp read; damping, the log-domain details and the belief computations for factors read by name", "nothing ran; the body's junction tree is the oracle"], note="the BP core's three mechanisms are accounted for")
c.save(state="COARSE")
