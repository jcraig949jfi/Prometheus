"""Cut: microkanren-scheme (Hemann & Friedman's microKanren, the 50-line final implementation from the paper; ancestry-aware, Stage A DEEP;
SOURCE_READ on M3; position 61 of the 2026-09-17 NOT_CUT order). Read: microKanren.scm in full (50 lines). Nothing ran (no Scheme on M3;
the body is small enough that a numbered transcription to Python would be a SCOUT, not done).
"""
from nyx.atlas.author import Cut

K = "vault:microkanren-scheme/upstream/microKanren.scm"
c = Cut("microkanren-scheme", mode="ANCESTRY_AWARE", inspected=["microKanren.scm 1-50"], evidence=[("SOURCE_READ", K + ":1-50")],
        note="relational programming reduced to four ideas in fifty lines: a substitution is an association list walked lazily (triangular, no occurs check); a goal is a function from a state (substitution, counter) to a STREAM of states; disjunction and conjunction are stream merge and stream bind; and completeness comes from immature streams (thunks) that mplus interleaves, so a diverging branch cannot starve its sibling")

subst = c.organ("triangular_substitution_as_an_association_list_walked_on_demand_with_a_structural_unifier_and_no_occurs_check", human_name="var / var? / var=? (vectors holding a counter); walk (5-7); ext-s (9); unify (18-27)", status="ACCEPTED",
    mechanism="a logic variable is a one-element vector holding its creation index; a substitution maps variables to terms; walk follows bindings until a non-variable or an unbound variable is reached (bindings are never composed, hence 'triangular'); unify walks both sides, binds a variable to the other side (ext-s conses a new pair), recurses on pairs, and otherwise requires eqv?; there is no occurs check, so a cyclic binding is possible",
    input="two terms and a substitution", output="an extended substitution or #f", state="none (persistent lists)", update="per ==", assumptions=["walking on demand is cheaper than composing substitutions; the user accepts the occurs-check omission (as Prolog does)"],
    fitness_value_in_ancestor="unification and substitution in nine lines; every extension is a cons", failure_landscape="by reading: walk is linear in the substitution length; a self-referential binding loops forever in walk", human_prior="Robinson 1965; the triangular form is from the miniKanren lineage (Byrd 2009)", evidence_ref=K + ":5-27", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="lines 5-27",
    coverage={"input_topology": "TREE", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE"})

goals = c.organ("goals_as_functions_from_a_state_to_a_stream_with_disjunction_as_stream_merge_conjunction_as_stream_bind_and_fresh_as_a_counter_increment", human_name="== (12-16: unit / mzero); call/fresh (29-32: the counter in the state); disj (34) = mplus; conj (35) = bind", status="ACCEPTED",
    mechanism="a state is a pair of substitution and a fresh-variable counter; == returns a one-element stream on success or the empty stream; call/fresh applies its body to a new variable made from the counter and increments it; disj runs both goals on the same state and merges their streams; conj runs the first goal and binds the second over every resulting state; goals therefore compose without any global search state",
    input="goals and a state", output="a stream of states", state="the counter inside each state", update="per goal application", assumptions=["monadic structure (unit, mzero, mplus, bind) is the whole of search; the counter makes fresh variables without side effects"],
    fitness_value_in_ancestor="a complete logic language whose interpreter is the host's function application", failure_landscape="UNKNOWN by run", human_prior="the list monad reading of logic programming (Wadler 1985; Spivey & Seres 2000)", evidence_ref=K + ":12-35", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="lines 12-35",
    coverage={"input_topology": "TREE", "output_topology": "STREAM", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE"})

inter = c.organ("interleaving_search_by_immature_streams_where_mplus_swaps_its_arguments_when_the_first_is_a_thunk", human_name="mplus (37-41): (procedure? $1) -> (lambda () (mplus $2 ($1))); bind (43-47): (procedure? $) -> (lambda () (bind ($) g))", status="ACCEPTED",
    mechanism="a stream is either empty, a pair (a mature answer and the rest), or a thunk (an immature stream: work not yet done); mplus of an immature first stream returns a thunk that, when forced, merges the SECOND stream with the forced first, so the two branches take turns; bind of an immature stream defers likewise; a recursive relation wrapped in a thunk (the paper's Zzz / snooze) therefore yields answers from every branch even when one branch is infinite",
    input="two streams", output="a merged stream", state="none", update="per force", assumptions=["swapping the arguments at every immature step is enough for fairness (breadth-like interleaving of depth-first branches)"],
    fitness_value_in_ancestor="completeness (every answer is eventually produced) that Prolog's depth-first search lacks, in five lines", failure_landscape="by reading: interleaving is fair between two branches at a time; deeply nested disjunctions are fair only asymptotically; the cost is a thunk per step", human_prior="Kiselyov, Shan, Friedman & Sabry 2005 (backtracking, interleaving, and terminating monad transformers)", evidence_ref=K + ":37-47", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="mplus and bind",
    coverage={"input_topology": "STREAM", "output_topology": "STREAM", "state_amount": "LOG", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE", "order_sensitivity": "SENSITIVE"})

c.reject("'logic programming' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="substitution, goal combinators and the interleaving are separable; the paper's whole point is that each is a few lines")

c.edge(subst, goals, "feeds", note="== calls unify"); c.edge(goals, inter, "feeds", note="disj/conj call mplus/bind"); c.edge(inter, goals, "gates", note="thunks decide when a goal runs")

c.pressure("a_search_over_relations_with_infinitely_many_solutions_in_some_branches_must_still_produce_the_solutions_of_every_branch_using_only_function_application_and_persistent_data",
    condition="an organism answers queries over relations defined recursively; some branches have infinitely many answers; the score is which answers appear in the first n and whether the organism terminates when asked for n; the organism may use only pure functions and persistent lists", resource_or_constraint="thunks; no mutable search state",
    failure_condition="starvation of a finite branch by an infinite one (Prolog's failure), or a diverging query for a finite n", world_punishes="depth-first streams; eager conjunction", world_rewards="immature streams with argument-swapping merge",
    observable_consequence="the set of answers among the first n for a query with one infinite and one finite branch, for the interleaving mplus vs an append-based mplus", vacuity_condition="finite relations", trivial_shortcuts="breadth-first with a queue (which needs mutable state or a much larger kernel)",
    cheat_control="an organism given the finite branch's answers must return them first; append-based mplus must never reach the finite branch when the infinite one is first; the interleaving mplus must reach it within 2 k steps: the world must show all three",
    cost_class="CPU-scale", source_evidence="microKanren.scm 37-47", purpose="PURPOSE: a minimal complete relational language (Hemann & Friedman 2013)")

c.ancestry("derived_from", "miniKanren (Friedman, Byrd, Kiselyov 2005) and the interleaving monad (Kiselyov et al. 2005); a functional cousin of Prolog (the atlas's gnu-prolog and swipl cuts hold the WAM route)", note="from the record and the paper")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["nothing unread", "nothing ran; a Python transcription would make it an M3 world (SCOUT candidate)"], note="fifty lines, three mechanisms, all located")
c.save(state="DEEP")
