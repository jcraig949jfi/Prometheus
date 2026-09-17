"""Cut: tscp-1.81-kerrigan-1997 (Tom Kerrigan's Simple Chess Program 1.81; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; position
25 of the 2026-09-17 NOT_CUT order). Read in full: search.c (293 lines: think, search, quiesce, reps, sort_pv, sort, checkup). Read by
structure: eval.c (piece-square tables, pawn structure, king safety), board.c (gen, gen_caps, makemove/takeback, hash). NOT read: main.c
(xboard protocol), book.c, data.c. Nothing ran (C; not on M3).
"""
from nyx.atlas.author import Cut

S = "vault:tscp-1.81-kerrigan-1997/upstream/tree/tscp181/search.c"
E = "vault:tscp-1.81-kerrigan-1997/upstream/tree/tscp181/eval.c"; B = "vault:tscp-1.81-kerrigan-1997/upstream/tree/tscp181/board.c"
c = Cut("tscp-1.81-kerrigan-1997", mode="ANCESTRY_AWARE", inspected=["search.c (all)", "eval.c, board.c (function lists and table headers)"], evidence=[("SOURCE_READ", S), ("SOURCE_READ", E + ":25-113"), ("SOURCE_READ", B + ":100-476")],
        note="a 1997 teaching engine: negamax alpha-beta with a quiescence search on captures, iterative deepening with a time check by longjmp, principal-variation ordering, a history heuristic, and a static evaluation from piece-square tables; each is a separate function")

ab = c.organ("negamax_alpha_beta_with_check_extension_and_repetition_draw", human_name="search() (search.c)", status="ACCEPTED",
    mechanism="depth-first negamax: at each node the moves are generated, ordered, and searched with the window (-beta, -alpha) negated; a score >= beta cuts the node; a score > alpha raises alpha and records the move into the principal variation; a repeated position (hash equal to any in the last fifty-move window) returns 0; being in check extends depth by one; no legal move is mate (-10000 + ply) or stalemate (0); the fifty-move rule returns 0",
    input="alpha, beta, depth; the board", output="a score; pv[] filled", state="ply, the pv triangle, nodes", update="per node",
    assumptions=["the evaluation is symmetric (negamax); alpha-beta's soundness needs a consistent ordering only for speed, not for correctness"],
    fitness_value_in_ancestor="the effective branching factor drops from ~35 toward ~6 with good ordering", failure_landscape="by reading: no transposition table, no null move, no futility: the 1997 minimum; the horizon effect is handled only by quiescence",
    human_prior="Knuth & Moore 1975 alpha-beta in negamax form; check extension as the one extension", evidence_ref=S + ":search", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="search()",
    coverage={"input_topology": "TREE", "output_topology": "SCALAR", "state_amount": "LOG", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE", "order_sensitivity": "SENSITIVE"})

qs = c.organ("quiescence_search_over_captures_with_stand_pat", human_name="quiesce() (search.c)", status="ACCEPTED",
    mechanism="at depth 0 the static evaluation is taken as a lower bound (stand pat: if it is >= beta cut; if > alpha raise alpha); then only captures are generated and searched recursively with the same window, so the search stops at a quiet position instead of a mid-exchange one",
    input="alpha, beta; the board", output="a score", state="the same pv triangle", update="per leaf", assumptions=["the side to move can always decline to capture (stand pat) -- false in zugzwang but harmless in tactical exchanges"],
    fitness_value_in_ancestor="cures the horizon effect for exchanges: no evaluation is taken in the middle of a capture sequence", failure_landscape="by reading: unbounded capture chains are possible in principle; MAX_PLY caps them",
    evidence_ref=S + ":quiesce", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="quiesce()",
    coverage={"input_topology": "TREE", "output_topology": "SCALAR", "state_amount": "LOG", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE"})

idp = c.organ("iterative_deepening_with_a_time_check_that_unwinds_by_longjmp", human_name="think() / checkup() (search.c)", status="ACCEPTED",
    mechanism="search depth 1, 2, ... up to max_depth; before each iteration set follow_pv so the previous iteration's principal variation is searched first; every 1024 nodes checkup() compares the clock with stop_time and, if over, longjmps out of the recursion back into think(), which unwinds the move stack (takeback until ply 0) and keeps the last completed iteration's pv; mate scores stop the deepening early; an opening-book move short-circuits everything",
    input="a time budget; max_depth", output="the best move (pv[0][0])", state="the pv triangle across iterations; history[]", update="per iteration",
    assumptions=["a shallow completed search is worth more than a deep incomplete one; the previous pv is the best guess for ordering the next iteration"],
    fitness_value_in_ancestor="a fixed time budget with anytime behaviour; the ordering benefit makes deepening nearly free", failure_landscape="by reading: longjmp abandons the current iteration's partial results entirely (no fail-soft use of the interrupted search)",
    evidence_ref=S + ":think, checkup", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="think() and checkup()",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "resource_dependence": "TIME", "recovery": "ROLLS_BACK", "temporal_horizon": "EPISODE"})

ord_ = c.organ("move_ordering_by_principal_variation_then_history_heuristic_then_selection_sort", human_name="sort_pv() / sort() / history[][] (search.c)", status="ACCEPTED",
    mechanism="the pv move from the previous iteration gets +10,000,000; captures get MVV/LVA scores at generation (board.c); every move that raises alpha adds depth to history[from][to], and moves carry their history score; sort() does one selection-sort step per move searched, so only the moves actually visited are ordered",
    input="the generated move list; pv[]; history[]", output="the next move to search", state="history (64x64 ints, reset per think)", update="per node",
    assumptions=["moves that were good elsewhere in the tree are likely good here (the history heuristic, Schaeffer 1983)"], fitness_value_in_ancestor="ordering is what makes alpha-beta cut; the incremental sort avoids sorting moves never searched",
    failure_landscape="UNKNOWN by run", evidence_ref=S + ":sort_pv, sort; history increments in search()", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the two sort functions and the history array",
    coverage={"input_topology": "SET", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "memory": "SUMMARY_STATISTIC", "stochasticity": "DETERMINISTIC", "adaptation": "PARAMETER"})

ev = c.organ("static_evaluation_as_material_plus_piece_square_tables_plus_pawn_structure_and_king_safety_terms", human_name="eval() and its tables (eval.c 25-113 read; 113-398 by function list)", status="CANDIDATE",
    mechanism="material by piece_value[]; positional bonuses from 64-entry piece-square tables (pawn, knight, bishop, king, king-endgame) flipped for the dark side; pawn terms (doubled, isolated, backward, passed) from per-file pawn_rank arrays; king safety from the pawn shield in front of the king; the endgame king table switches on when material is low",
    input="the board", output="a score from the side to move's view", state="none", update="per leaf", assumptions=["a linear sum of hand-tuned terms approximates the game-theoretic value well enough for a shallow search"],
    fitness_value_in_ancestor="the only knowledge in the program; everything else is search", failure_landscape="UNKNOWN by run", human_prior="every number in the tables is the author's judgement", evidence_ref=E + ":25-113 (tables); eval() 113-398 by structure", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="eval.c; CANDIDATE because eval() itself was read by function list only",
    coverage={"input_topology": "MATRIX", "output_topology": "SCALAR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "representation_sensitivity": "SENSITIVE"})

c.reject("move generation, make/unmake with the history stack, Zobrist hashing (board.c), the xboard protocol and book (main.c, book.c)", reason="OTHER", evidence="read by function list only; generic chess mechanics and I/O", note="the Zobrist hash is the repetition detector's input (an organ elsewhere in the vault's hash lineage)")
c.reject("'chess engine' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="search, quiescence, deepening, ordering and evaluation are separately replaceable and are the axes along which every later engine differs")

c.edge(idp, ab, "feeds"); c.edge(ab, qs, "feeds", note="at depth 0"); c.edge(ord_, ab, "feeds"); c.edge(ab, ord_, "updates", note="history"); c.edge(idp, ord_, "feeds", note="previous pv"); c.edge(ev, qs, "feeds"); c.edge(ev, ab, "feeds", note="at the ply caps")

c.pressure("a_two_player_game_tree_far_larger_than_the_budget_must_be_searched_to_a_decision_within_a_time_limit_using_a_cheap_leaf_estimate",
    condition="an adversarial game with branching ~35; the organism has a clock, a static estimate of positions, and no tree it can exhaust; it must return the best move it can by the deadline", resource_or_constraint="nodes per second; the deadline",
    failure_condition="a move chosen from an unfinished search, or a leaf estimate taken mid-exchange (horizon)", world_punishes="depth-first commitment without pruning; estimates in unstable positions", world_rewards="pruning by bounds, ordering, deepening with a completed-iteration fallback, and quiescence",
    observable_consequence="nodes to reach a given depth with ordering on/off; blunder rate with quiescence on/off; move quality vs time", vacuity_condition="a game small enough to solve", trivial_shortcuts="a tablebase or an oracle",
    cheat_control="an organism given the game-theoretic value of every position must play perfectly at depth 1; the ancestor with alpha-beta disabled (plain negamax) must search ~35x more nodes per ply: the world must show both",
    cost_class="CPU-scale", source_evidence="search.c; record domain game-tree-search", purpose="PURPOSE: chess play under a clock (Kerrigan 1997, a teaching program)")

c.ancestry("algorithm_from", "Knuth & Moore 1975 (alpha-beta); Slate & Atkin 1977 (iterative deepening); Schaeffer 1983 (history heuristic); the quiescence search of the Shannon/Turing era", note="from the code's structure; not verified against sources")
c.residue("PARTIALLY_EXPLAINED", ["eval() body read by function list only (organ is CANDIDATE)", "board.c and main.c not read line by line", "nothing ran"], note="search.c is accounted for line by line")
c.save(state="COARSE")
