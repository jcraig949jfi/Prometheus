"""The classifier vocabulary for the Atlas of Game Worlds.

Two layers, and only one of them is trusted.

  FOUND     what a source asserts: genre tags, category labels, marketing copy.
            Recorded in full, never used to order bench work. It is the negative
            control -- the atlas claims retention is predicted by decision
            structure and NOT by genre, and that is only demonstrable if genre is
            a column you can regress against.

  DECLARED  what the atlas asserts about a world's decision structure. This is
            the layer that orders work, and every field in it exists because some
            circuit's scope statement depends on it (see ludus/atlas/CIRCUIT_LEDGER.md).

Every declared value also carries a METHOD (see METHODS): heuristic values are
machine-inferred from text and are not evidence. Only 'reviewed' and 'audited'
values may support a claim about a named game. This mirrors the rules_state
ladder in ludus/bench/RULES_AUDIT.md, for the same reason.
"""
from __future__ import annotations

# ------------------------------------------------------------------ ladder
CATALOG_STATES = [
    "CATALOGUED",   # name + source + found tags only
    "SPECIFIED",    # declared vector filled (heuristically), state space estimated
    "DEEPENED",     # dossier written: object model, STD, turn trace, conditions
    "IMPLEMENTED",  # a World subclass exists and ludus/bench/verify.py passes
    "AUDITED",      # rules checked against a real rulebook by the operator
]

METHODS = ["heuristic", "source", "reviewed", "audited"]

# ---------------------------------------------------------------- temporal
# (name, lower_bound_inclusive, upper_bound_exclusive); years are astronomical,
# so -3000 means 3001 BCE.
EPOCHS = [
    ("DEEP_ANTIQUITY", None,  -1000),
    ("ANCIENT",        -1000,   500),
    ("MEDIEVAL",         500,  1450),
    ("EARLY_MODERN",    1450,  1750),
    ("INDUSTRIAL",      1750,  1900),
    ("MODERN",          1900,  1970),
    ("DIGITAL",         1970,  2000),
    ("CONTEMPORARY",    2000,  None),
]

YEAR_PRECISION = ["exact", "decade", "century", "millennium", "attested_by", "unknown"]


def epoch_for(year):
    if year is None:
        return None
    for name, lo, hi in EPOCHS:
        if (lo is None or year >= lo) and (hi is None or year < hi):
            return name
    return None


# ------------------------------------------------------------------- medium
MEDIA = [
    "BOARD", "CARD", "DICE", "TILE", "PAPER_AND_PENCIL", "VIDEO", "PUZZLE",
    "RPG", "MEMORY", "PARTY", "DEXTERITY", "WORD", "SPORT", "PLAYGROUND",
    "MINIATURES", "LARP", "ESCAPE_ROOM", "ABSTRACT", "WARGAME", "TRICK_TAKING",
    "MANCALA", "COLLECTIBLE", "SOLITAIRE", "GAMBLING", "EDUCATIONAL",
]

# ----------------------------------------------------------------- audience
AGE_BANDS = ["PRESCHOOL", "CHILD", "FAMILY", "TEEN", "ADULT", "UNRESTRICTED"]


def age_band_for(min_age):
    if min_age is None:
        return None
    if min_age <= 4:
        return "PRESCHOOL"
    if min_age <= 7:
        return "CHILD"
    if min_age <= 11:
        return "FAMILY"
    if min_age <= 15:
        return "TEEN"
    return "ADULT"


# -------------------------------------------------------------- chance/skill
RANDOMNESS_SOURCES = [
    "NONE", "DICE", "DECK_SHUFFLE", "DECK_DEPLETING", "SPINNER", "TILE_BAG",
    "PHYSICAL_EXECUTION", "EXTERNAL_WORLD", "PROCEDURAL_GENERATION",
]
# REAL_TIME_PHYSICAL was replaced by PHYSICAL_EXECUTION 2026-09-01. It matched
# the bare word "timer", so Bejeweled's timer bar and Perfection's 60-second
# dial were recorded as chance. A clock constrains play; it does not randomise
# it, and turn_structure=REAL_TIME and horizon=CLOCK_LIMITED already carry that
# meaning. The replacement matches only genuine physical execution variance --
# flicking, toppling, dexterity -- which really is an outcome the player does
# not fully control. Same error class as the two values removed below.
# HIDDEN_INFO and SIMULTANEOUS_CHOICE were removed 2026-09-01. Neither is a
# chance device. Not knowing your opponent's hand is an INFORMATION property,
# and choosing at the same time as someone else is a TURN STRUCTURE property --
# both already have their own fields (`information`, `turn_structure`), and
# recording them here double-counted the same fact as randomness.
#
# The damage was concrete: 132 worlds carried one of these as a randomness
# source and 77 had nothing else, so genuinely deterministic perfect-information
# games -- Tic-tac-toe, Connect Four, Gomoku, Fanorona -- were recorded as
# containing chance. That inflated their `luck_factor` (an empty source set
# scores 0.02; a non-empty one starts at 0.30) and produced a standing
# contradiction against the determinism rule, which was correct all along.

# luck_factor is a 0..1 estimate of the share of outcome variance attributable to
# chance under equally-skilled play. 0.0 = chess, 1.0 = pure snakes and ladders.

# ------------------------------------------------------- information/interaction
INFORMATION = ["PERFECT", "IMPERFECT", "HIDDEN_PRIVATE", "SIMULTANEOUS", "ASYMMETRIC"]

INTERACTION = [
    "SOLITAIRE",        # one player, no opponent modelling at all
    "PARALLEL",         # multiplayer but players barely touch (multiplayer solitaire)
    "COMPETITIVE",      # direct zero-sum-ish conflict
    "COOPERATIVE",      # all players win or lose together
    "SEMI_COOPERATIVE", # shared goal, individual scoring
    "TEAM",             # fixed teams
    "TRAITOR",          # hidden roles / social deduction
    "NEGOTIATION",      # binding or non-binding deals are a primary move
]

TURN_STRUCTURE = [
    "STRICT_TURN", "SIMULTANEOUS", "REAL_TIME", "ACTION_POINT",
    "VARIABLE_ORDER", "PRIORITY_QUEUE", "PHASE_STRUCTURED", "TICK_BASED",
    "AUCTION_ROUND", "TRICK_ROUND",
]
# CONTINUOUS was removed 2026-09-01. It drew no distinction from REAL_TIME that
# anything could act on, and no classifier rule could ever set it -- so it was
# a permanently empty cell in the coverage grid, reported as a gap in the
# atlas's knowledge when it was really a defect in this list. A value that
# cannot be reached is worse than one value fewer: it makes the grid lie.
# `report.py` now checks reachability so this cannot recur silently.

# ------------------------------------------- declared structure (bench layer B)
# These are the fields the LUDUS bench actually consumes. Each maps to a
# precondition in some circuit's scope statement.

EXOGENOUS_PROCESS = [
    "NONE",              # deterministic; all uncertainty is about the opponent
    "IID",               # dice: independent draws, no memory
    "DEPLETING_DECK",    # sampling without replacement; the distribution moves
    "HIDDEN_FIXED",      # shuffled once, revealed by play (trick-taking, minesweeper)
    "OPPONENT_GENERATED",
    "CONTINUOUS_TIME",   # real-time; the process is the clock
]

LOSS_SHAPE = [
    "TOTAL_RUIN",        # bust forfeits the entire accumulated pot
    "PARTIAL_DECAY",     # a bad outcome degrades but does not erase
    "NONE",              # you cannot lose what you have banked
    "OPPORTUNITY_ONLY",  # the only cost is a foregone alternative
    "ELIMINATION",       # the player leaves the game entirely
]

DECISION_AXES = [
    "STOP",          # bank or continue
    "SELECT",        # which option after an exogenous draw
    "ALLOCATE",      # commit divisible resource across slots
    "ORDER",         # sequencing / scheduling
    "BID",           # priced or sealed competition for a slot
    "COMMIT_BLIND",  # simultaneous irreversible choice
    "DISCARD",       # what to give up
    "TRADE",         # exchange with another agent
    "NEGOTIATE",     # non-binding communication as a move
    "SPATIAL",       # placement under geometric constraint
    "TIMING",        # when, not what -- tempo and initiative
    "BLUFF",         # deliberate misrepresentation to an observer
]

HORIZON = ["FIXED", "VARIABLE", "RACE_TO_TARGET", "OPEN_ENDED", "CLOCK_LIMITED"]

SCORING_SHAPE = [
    "LINEAR_ACCUMULATION", "NONLINEAR", "SET_COLLECTION_CONVEX",
    "WINNER_TAKE_ALL", "RACE_POSITION", "SURVIVAL", "NEGATIVE_AVOIDANCE",
]

TRACTABILITY = [
    "EXACT",            # < ~1e6 reachable states: backward induction applies
    "EXACT_WITH_CUT",   # exact after a stated scope cut
    "SAMPLING_ONLY",    # too large; only Monte Carlo estimates
    "INTRACTABLE",
]

# --------------------------------------------------------------- conditions
# The 'five fouls and you are benched' layer: structured, thresholded rules.
CONDITION_KINDS = [
    "WIN",          # how the game is won
    "LOSE",         # how it is lost outright
    "ELIMINATE",    # how a player/piece leaves play before the end
    "BOUNDARY",     # hard caps: hand limits, resource ceilings, board edges
    "TERMINATE",    # what ends the game regardless of standing
    "PENALTY",      # a cost short of elimination
]

# ---------------------------------------------------------------- strategy
STRATEGY_TAGS = [
    "tempo", "initiative", "zugzwang", "tableau_building", "engine_building",
    "hate_drafting", "bluffing", "hand_management", "position_evaluation",
    "risk_of_ruin_management", "expected_value_maximisation", "card_counting",
    "probability_estimation", "opponent_modelling", "signalling", "blocking",
    "tempo_denial", "resource_conversion", "action_efficiency", "set_collection",
    "area_control", "route_optimisation", "spatial_packing", "memory_recall",
    "pattern_matching", "deduction", "misdirection", "coalition_forming",
    "endgame_conversion", "opening_theory", "sacrifice", "tempo_race",
    "push_your_luck", "stop_loss", "kingmaking_avoidance", "table_talk",
]

ALGORITHM_TAGS = [
    "minimax", "alpha_beta", "iterative_deepening", "transposition_table",
    "monte_carlo_tree_search", "expectimax", "backward_induction",
    "dynamic_programming", "counterfactual_regret_minimisation",
    "opening_book", "endgame_tablebase", "retrograde_analysis",
    "heuristic_evaluation", "proof_number_search", "alpha_zero_self_play",
    "bandit_ucb", "belief_state_tracking", "particle_filter",
    "constraint_propagation", "sat_solving", "exact_cover_dancing_links",
    "linear_programming", "nash_equilibrium_solving", "fictitious_play",
]

SOLVED_STATUS = [
    "SOLVED_STRONG", "SOLVED_WEAK", "SOLVED_ULTRA_WEAK",
    "PARTIALLY_SOLVED", "UNSOLVED", "NOT_APPLICABLE",
]

# ------------------------------------------------------------------ regions
REGIONS = [
    "AFRICA", "EAST_ASIA", "SOUTH_ASIA", "SOUTHEAST_ASIA", "CENTRAL_ASIA",
    "WEST_ASIA", "EUROPE_WEST", "EUROPE_EAST", "EUROPE_NORTH", "EUROPE_SOUTH",
    "NORTH_AMERICA", "CENTRAL_AMERICA", "SOUTH_AMERICA", "OCEANIA",
    "CIRCUMPOLAR", "GLOBAL",
]

COUNTRY_REGION = {
    "Egypt": "AFRICA", "Nigeria": "AFRICA", "Ghana": "AFRICA", "Ethiopia": "AFRICA",
    "Kenya": "AFRICA", "Tanzania": "AFRICA", "Sudan": "AFRICA", "Mali": "AFRICA",
    "South Africa": "AFRICA", "Somalia": "AFRICA", "Uganda": "AFRICA",
    "China": "EAST_ASIA", "Japan": "EAST_ASIA", "South Korea": "EAST_ASIA",
    "Korea": "EAST_ASIA", "Taiwan": "EAST_ASIA", "Mongolia": "EAST_ASIA",
    "India": "SOUTH_ASIA", "Pakistan": "SOUTH_ASIA", "Sri Lanka": "SOUTH_ASIA",
    "Nepal": "SOUTH_ASIA", "Bangladesh": "SOUTH_ASIA",
    "Thailand": "SOUTHEAST_ASIA", "Indonesia": "SOUTHEAST_ASIA",
    "Philippines": "SOUTHEAST_ASIA", "Vietnam": "SOUTHEAST_ASIA",
    "Malaysia": "SOUTHEAST_ASIA", "Myanmar": "SOUTHEAST_ASIA",
    "Iran": "WEST_ASIA", "Iraq": "WEST_ASIA", "Turkey": "WEST_ASIA",
    "Israel": "WEST_ASIA", "Syria": "WEST_ASIA", "Lebanon": "WEST_ASIA",
    "Saudi Arabia": "WEST_ASIA", "Jordan": "WEST_ASIA", "Armenia": "WEST_ASIA",
    "Uzbekistan": "CENTRAL_ASIA", "Kazakhstan": "CENTRAL_ASIA",
    "United Kingdom": "EUROPE_WEST", "England": "EUROPE_WEST",
    "France": "EUROPE_WEST", "Germany": "EUROPE_WEST", "Netherlands": "EUROPE_WEST",
    "Belgium": "EUROPE_WEST", "Ireland": "EUROPE_WEST", "Austria": "EUROPE_WEST",
    "Switzerland": "EUROPE_WEST", "Scotland": "EUROPE_WEST", "Wales": "EUROPE_WEST",
    "Poland": "EUROPE_EAST", "Russia": "EUROPE_EAST", "Ukraine": "EUROPE_EAST",
    "Czech Republic": "EUROPE_EAST", "Hungary": "EUROPE_EAST",
    "Romania": "EUROPE_EAST", "Bulgaria": "EUROPE_EAST", "Serbia": "EUROPE_EAST",
    "Slovakia": "EUROPE_EAST", "Croatia": "EUROPE_EAST",
    "Sweden": "EUROPE_NORTH", "Norway": "EUROPE_NORTH", "Denmark": "EUROPE_NORTH",
    "Finland": "EUROPE_NORTH", "Iceland": "EUROPE_NORTH", "Estonia": "EUROPE_NORTH",
    "Latvia": "EUROPE_NORTH", "Lithuania": "EUROPE_NORTH",
    "Italy": "EUROPE_SOUTH", "Spain": "EUROPE_SOUTH", "Portugal": "EUROPE_SOUTH",
    "Greece": "EUROPE_SOUTH", "Ancient Greece": "EUROPE_SOUTH",
    "Ancient Rome": "EUROPE_SOUTH", "Roman Empire": "EUROPE_SOUTH",
    "United States": "NORTH_AMERICA", "United States of America": "NORTH_AMERICA",
    "Canada": "NORTH_AMERICA", "Mexico": "CENTRAL_AMERICA",
    "Guatemala": "CENTRAL_AMERICA", "Cuba": "CENTRAL_AMERICA",
    "Brazil": "SOUTH_AMERICA", "Argentina": "SOUTH_AMERICA",
    "Peru": "SOUTH_AMERICA", "Chile": "SOUTH_AMERICA", "Colombia": "SOUTH_AMERICA",
    "Australia": "OCEANIA", "New Zealand": "OCEANIA", "Fiji": "OCEANIA",
    "Hawaii": "OCEANIA", "Papua New Guinea": "OCEANIA",
}

# ------------------------------------------------- the declared-vector fields
# The tuple used for novelty scoring and grid-coverage reporting. A world's
# position in THIS space is what decides whether building it teaches anything.
DECLARED_VECTOR = [
    "exogenous_process", "loss_shape", "horizon", "scoring_shape",
    "information", "interaction", "turn_structure", "tractability",
]

VOCAB = {
    "exogenous_process": EXOGENOUS_PROCESS,
    "loss_shape": LOSS_SHAPE,
    "horizon": HORIZON,
    "scoring_shape": SCORING_SHAPE,
    "information": INFORMATION,
    "interaction": INTERACTION,
    "turn_structure": TURN_STRUCTURE,
    "tractability": TRACTABILITY,
    "media": MEDIA,
    "randomness_sources": RANDOMNESS_SOURCES,
    "live_axes": DECISION_AXES,
    "strategies": STRATEGY_TAGS,
    "algorithms": ALGORITHM_TAGS,
    "solved_status": SOLVED_STATUS,
    "epoch": [e[0] for e in EPOCHS],
    "age_band": AGE_BANDS,
    "region": REGIONS,
    "catalog_state": CATALOG_STATES,
}
