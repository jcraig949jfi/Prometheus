"""First-pass classifier.

Everything this module produces is `method='heuristic'`: keyword evidence over a
Wikidata description, genre/instance labels and a Wikipedia lead extract. That is
enough to place a world on the grid and to rank it for deepening. It is NOT
evidence about a named game, and the store's merge policy will let any 'reviewed'
value overwrite it without argument.

The contamination risk here is the same one that flagged r0011 and r0014 in
ludus/atlas/CIRCUIT_LEDGER.md: a classifier that reaches for the atlas's own
vocabulary rather than the text in front of it will manufacture agreement. So
every rule below fires on words that appear in SOURCE TEXT, never on a prior
belief about what the game 'must' be, and a world with no keyword hits is left
NULL rather than defaulted.
"""
from __future__ import annotations

import math
import re

import taxonomy as T

# (value, weight, pattern) -- patterns are matched case-insensitively against
# the pooled text: name + description + genre labels + instance labels + extract.
RULES = {
    "media": [
        ("BOARD", 3, r"\bboard game|game board|gameboard|playing board\b"),
        ("CARD", 3, r"\bcard game|playing cards?|deck of cards|card-?based\b"),
        ("DICE", 3, r"\bdice game|\bdice\b|die is rolled|rolling dice|knucklebone|astragal"),
        ("TILE", 2, r"\btile[- ]?(laying|based)|\btiles\b|domino|mahjong|rummikub"),
        ("VIDEO", 3, r"\bvideo game|arcade game|computer game|console|playstation|nintendo|xbox|steam\b"),
        ("PUZZLE", 3, r"\bpuzzle|brain ?teaser|solitaire logic|sudoku|crossword|riddle"),
        ("RPG", 3, r"\brole-?playing game|tabletop role|\brpg\b|dungeon master|game master"),
        ("MEMORY", 3, r"\bmemory game|memorisation|memorization|concentration game|recall the"),
        ("PARTY", 2, r"\bparty game|social gathering|icebreaker"),
        ("DEXTERITY", 2, r"\bdexterity|flick|stack(ing)? blocks|balance|physical skill|reflex"),
        ("WORD", 2, r"\bword game|anagram|letters? are|vocabulary|spelling"),
        ("SPORT", 3, r"\bsport\b|team sport|athletic|played on a (pitch|court|field)"),
        ("PLAYGROUND", 2, r"\bplayground|schoolyard|street game|children play"),
        ("MINIATURES", 2, r"\bminiature|tabletop wargame|figures? are moved"),
        ("ABSTRACT", 2, r"\babstract strategy|no theme|perfect information.*abstract"),
        ("WARGAME", 2, r"\bwargame|war game|military simulation|hex(agon)? map"),
        ("TRICK_TAKING", 3, r"\btrick-?taking|takes the trick|follow suit|trump suit"),
        ("MANCALA", 3, r"\bmancala|sowing game|count-and-capture|seeds? are sown"),
        ("COLLECTIBLE", 2, r"\bcollectible card|trading card game|booster pack"),
        ("SOLITAIRE", 2, r"\bsolitaire|patience (card )?game|single-?player"),
        ("GAMBLING", 2, r"\bgambling|casino|wager|betting|stakes are"),
        ("EDUCATIONAL", 1, r"\beducational game|teaching|pedagog"),
        ("PAPER_AND_PENCIL", 2, r"\bpaper[- ]and[- ]pencil|pen and paper|roll[- ]and[- ]write|flip[- ]and[- ]write"),
    ],
    "randomness_sources": [
        ("DICE", 3, r"\bdice|die\b|d6|roll(ing|s|ed)? (the |a )?(dice|die)|knucklebone"),
        ("DECK_SHUFFLE", 3, r"\bshuffl|deck is (cut|dealt)|dealt from|draw pile|drawn at random"),
        ("DECK_DEPLETING", 2, r"\bwithout replacement|deck (is )?depleted|as the deck|remaining cards"),
        ("SPINNER", 2, r"\bspinner|teetotum|dreidel|spinning top"),
        ("TILE_BAG", 2, r"\bfrom a bag|tile bag|drawn from the bag"),
        # A clock is a CONSTRAINT, not a chance device. The old rule matched the
        # bare word "timer", so Bejeweled's timer bar and Perfection's 60-second
        # dial were filed as randomness -- which then contradicted their correct
        # information=PERFECT. Real-time play belongs in turn_structure, and a
        # time limit in horizon=CLOCK_LIMITED; both fields already exist.
        # What IS genuinely stochastic in this family is physical execution: a
        # flicked disc or a tottering tower does not land where it was aimed.
        ("PHYSICAL_EXECUTION", 2,
         r"\bflick(ing|ed|s)?\b|\bdexterity\b|stack(ing)? blocks|\btopple|"
         r"\bcollaps(e|es|ing)\b|\btumbl|\bbalanc(e|ing) (the|a|blocks|pieces)|"
         r"\bsteady hand\b|\bthrow(ing|n)? (the )?(disc|ring|beanbag|hoop)"),
        ("NONE", 2, r"\bno (element of )?(luck|chance)|perfect information|purely (abstract|strategic)|no randomness"),
        ("PROCEDURAL_GENERATION", 2, r"\bprocedural(ly)? generat|randomly generated (level|world|map)"),
    ],
    "information": [
        ("PERFECT", 3, r"\bperfect information|no hidden|all information.*visible|open information"),
        ("HIDDEN_PRIVATE", 3, r"\bprivate hand|hand of cards|hidden role|secret objective|concealed hand"),
        ("SIMULTANEOUS", 2, r"\bsimultaneous(ly)?|sealed bid|blind bid|reveal(ed)? at once"),
        ("ASYMMETRIC", 2, r"\basymmetric|different (powers|abilities|roles)|one player controls"),
        ("IMPERFECT", 2, r"\bimperfect information|bluff|deduc|uncertain(ty)? about"),
    ],
    "interaction": [
        # 'one player' alone is not evidence of a solitaire game -- "one player
        # deals", "one player leads to the first trick" appear in essentially
        # every card-game rules section. It made 44 multiplayer card games
        # (Preferans, Lupfen, Russian Schnapsen) read as SOLITAIRE while their
        # own players_max said 3-5. The phrase must be about how many players
        # the GAME takes, not about which player acts.
        ("SOLITAIRE", 3, r"\bsolitaire\b|\bsingle-?player\b|\bplayed alone\b|"
                         r"\bpatience (card )?game\b|\bfor one player\b|"
                         r"\bone[- ]player game\b|\bplayed by (a |one )single player\b|"
                         r"\bsolo (game|play|variant)\b|\bwithout an opponent\b"),
        ("COOPERATIVE", 3, r"\bcooperative|co-?op\b|players work together|all players win"),
        ("SEMI_COOPERATIVE", 2, r"\bsemi-?cooperative|shared goal but"),
        ("TRAITOR", 3, r"\bsocial deduction|hidden traitor|hidden role|werewolf|mafia|impostor"),
        ("TEAM", 2, r"\bin (fixed )?teams\b|\bteams? of (two|three|four|\d)\b|"
                    r"partnership|partners sit (across|opposite)|two teams of"),
        ("NEGOTIATION", 2, r"\bnegotiat|trade|diplomacy|deals? (are|between) player"),
        ("PARALLEL", 3, r"\bmultiplayer solitaire|little (direct )?interaction|"
                        r"players rarely interact|no direct interaction|"
                        r"\beach player has (their|his or her) own "
                        r"(board|sheet|grid|map|player board)|"
                        r"\ball players use the same (dice|cards?|draw)|"
                        r"\broll[- ]and[- ]write|\bflip[- ]and[- ]write|"
                        r"\bevery player (fills|marks|draws) (in|on) their own"),
        ("COMPETITIVE", 1, r"\bopponent|compet|beat(s)? the other|against each other|two-?player"),
    ],
    "turn_structure": [
        ("REAL_TIME", 3, r"\breal-?time|no turns|simultaneously and continuously|as quickly as possible"),
        ("SIMULTANEOUS", 3, r"\bsimultaneous(ly)?\b|"
                            r"all players (act|choose|play|select|reveal)[^.]{0,30}"
                            r"(at (the same time|once)|simultaneously)|"
                            r"\beach player secretly (chooses|selects|picks)|"
                            r"\bface[- ]down[^.]{0,40}then (revealed|turned)|"
                            r"\bat the same time\b"),
        ("TRICK_ROUND", 3, r"\btrick-?taking|each trick|leads to the trick"),
        ("AUCTION_ROUND", 3, r"\bauction|bidding round|bids? are placed"),
        ("ACTION_POINT", 3, r"\baction points?\b|\bap\b per turn|spend(s|ing)? actions?|"
                            r"\b(two|three|four|five|\d+) actions? (per|each|on (their|his|her)) turn|"
                            r"\bmay (take|perform) (up to )?(two|three|four|five|\d+) actions|"
                            r"\btakes? (two|three|four|five|\d+) actions\b"),
        ("PHASE_STRUCTURED", 2, r"\bphases?\b|upkeep phase|each round consists of"),
        ("VARIABLE_ORDER", 2, r"\bturn order (varies|is determined)|initiative is"),
        ("PRIORITY_QUEUE", 2, r"\bpriority|initiative track|time track"),
        ("TICK_BASED", 2, r"\btick|clock advances|time step"),
        ("STRICT_TURN", 1, r"\btakes? turns?|in turn|alternat(e|ing) turns|on (his|her|their|your) turn"),
    ],
    "exogenous_process": [
        ("NONE", 3, r"\bno (element of )?(luck|chance)|perfect information|deterministic|no randomness"),
        ("IID", 3, r"\bdice|die is rolled|each roll|with replacement|spinner"),
        ("DEPLETING_DECK", 3, r"\bshuffl|draw pile|deck (is )?dealt|without replacement|remaining cards|discard pile"),
        ("HIDDEN_FIXED", 3, r"\bdealt at the start|face-?down (board|layout|grid)|"
                            r"revealed as play|minefield|\bmines? (are|is) (randomly )?(placed|hidden)|"
                            r"\bhidden (layout|arrangement|solution|configuration|code|pattern)|"
                            r"\bfixed at the (start|beginning)[^.]{0,30}revealed|"
                            r"\bsecret (code|arrangement|pattern|combination)"),
        ("CONTINUOUS_TIME", 2, r"\breal-?time|timer|continuous play"),
        ("OPPONENT_GENERATED", 1, r"\bopponent(?:'s)? (choice|move)|adversar"),
    ],
    "loss_shape": [
        ("TOTAL_RUIN", 3, r"\bbust|lose (all|everything|the entire)|forfeits? (all|everything)|lose your (entire )?(turn|hoard|pot)|score(s)? zero"),
        ("ELIMINATION", 3, r"\beliminat|knocked out|out of the game|last player (standing|remaining)|captured and removed"),
        ("PARTIAL_DECAY", 2, r"\blose (one|a|some)|penalt(y|ies)|negative points|deduct"),
        ("NONE", 2, r"\bcannot lose|points are kept|banked (points|score)|no penalty"),
        ("OPPORTUNITY_ONLY", 1, r"\bforgo|opportunity cost|misses? the chance"),
    ],
    "horizon": [
        ("RACE_TO_TARGET", 3, r"\bfirst (player )?to (reach|score|get|collect)|race to|wins? (immediately )?(on|upon) reaching|\b\d+ points? wins"),
        ("CLOCK_LIMITED", 3, r"\btime limit|timer|\d+ minutes? (long|half|period)|until time expires"),
        ("FIXED", 2, r"\b(over|lasts?|consists? of) \d+ rounds?|fixed number of (turns|rounds)|\d+ turns each"),
        ("VARIABLE", 2, r"\buntil the deck (runs out|is exhausted)|until (all|no) .* remain|game ends when"),
        ("OPEN_ENDED", 1, r"\bno fixed end|indefinit|campaign|legacy"),
    ],
    "scoring_shape": [
        ("WINNER_TAKE_ALL", 3, r"\bwinner takes|last player standing|checkmate|first to win|sole survivor"),
        ("RACE_POSITION", 3, r"\bfirst (to reach|past|across) the (finish|end|home)|race\b|finish line"),
        ("SET_COLLECTION_CONVEX", 3, r"\bsets? of|collect(ing)? sets|melds?|runs? of (three|four)|full house|the more .* the more"),
        ("NEGATIVE_AVOIDANCE", 3, r"\blowest score wins|avoid (taking|collecting)|penalty points|negative points"),
        ("SURVIVAL", 2, r"\bsurviv|stay in the game|outlast"),
        ("NONLINEAR", 2, r"\bsquared|exponential|multiplier|doubl(e|ing) (the )?score|triangular"),
        ("LINEAR_ACCUMULATION", 1, r"\bpoints? (are )?(scored|awarded|added)|highest (total|score) wins|accumulat"),
    ],
    "live_axes": [
        ("STOP", 3, r"\bpress your luck|push your luck|bank (the|your)|stop or continue|continue rolling|quit while"),
        ("SELECT", 2, r"\bchoose (one|which|a)|select(s|ing)? (one|a)|may (take|play) (one|any)|options?"),
        ("ALLOCATE", 2, r"\ballocat|distribut(e|ing) (workers|resources)|assign (workers|dice)|worker placement"),
        ("ORDER", 2, r"\bturn order|sequence(s|d)?|order in which|scheduling"),
        ("BID", 3, r"\bbid(s|ding)?\b|auction|sealed bid"),
        ("COMMIT_BLIND", 2, r"\bsimultaneous(ly)?|face-?down (selection|commitment)|blind"),
        ("DISCARD", 2, r"\bdiscard(s|ing)?\b|must shed|throw away a card"),
        ("TRADE", 2, r"\btrad(e|ing)|exchang(e|ing)|barter"),
        ("NEGOTIATE", 2, r"\bnegotiat|diplomacy|form alliances"),
        ("SPATIAL", 2, r"\bplace(s|d|ment)? (a|the|tiles|pieces) on|adjacen|orthogonal|grid|board (position|square)"),
        ("TIMING", 2, r"\btempo|initiative|when to (play|use)|timing"),
        ("BLUFF", 3, r"\bbluff|deceiv|lie about|misrepresent"),
    ],
    "solved_status": [
        ("SOLVED_STRONG", 3, r"\bstrongly solved|solved (game|in \d{4})|complete (endgame )?tablebase"),
        ("SOLVED_WEAK", 3, r"\bweakly solved"),
        ("SOLVED_ULTRA_WEAK", 3, r"\bultra-?weakly solved"),
        ("PARTIALLY_SOLVED", 2, r"\bpartially solved|solved for (small|\d+)"),
    ],
    "algorithms": [
        ("minimax", 2, r"\bminimax|game tree search"),
        ("alpha_beta", 2, r"\balpha-?beta"),
        ("monte_carlo_tree_search", 2, r"\bmonte carlo tree search|\bmcts\b"),
        ("alpha_zero_self_play", 2, r"\balpha ?(go|zero)|self-?play|deep reinforcement learning"),
        ("endgame_tablebase", 2, r"\btablebase|endgame database"),
        ("retrograde_analysis", 2, r"\bretrograde analysis"),
        ("dynamic_programming", 2, r"\bdynamic programming|backward induction"),
        ("counterfactual_regret_minimisation", 2, r"\bcounterfactual regret|\bcfr\b|libratus|pluribus"),
        ("opening_book", 2, r"\bopening (book|theory)|book moves"),
        ("constraint_propagation", 2, r"\bconstraint propagation|backtracking search"),
        ("exact_cover_dancing_links", 2, r"\bdancing links|exact cover|algorithm x"),
        ("nash_equilibrium_solving", 2, r"\bnash equilibrium|game[- ]theoretic(ally)? optimal|\bgto\b"),
        ("expectimax", 2, r"\bexpectimax|expectiminimax"),
        ("heuristic_evaluation", 1, r"\bevaluation function|heuristic"),
    ],
    "strategies": [
        ("push_your_luck", 2, r"\bpress your luck|push your luck"),
        ("bluffing", 2, r"\bbluff|deceiv|misdirect"),
        ("card_counting", 2, r"\bcard counting|count the (cards|deck)|track which cards"),
        ("memory_recall", 2, r"\bremember|memoris|memoriz|recall"),
        ("deduction", 2, r"\bdeduc|logical inference|work out which"),
        ("set_collection", 2, r"\bsets? of|collect(ing)? sets|meld"),
        ("area_control", 2, r"\barea control|majority|control (of )?(regions|territor)"),
        ("route_optimisation", 2, r"\broute|network|connect(ing)? cities|shortest path"),
        ("engine_building", 2, r"\bengine[- ]building|production (chain|engine)|compounding"),
        ("tableau_building", 2, r"\btableau"),
        ("hand_management", 2, r"\bhand management|manage (your|their) hand"),
        ("opening_theory", 2, r"\bopening (theory|book|repertoire)"),
        ("sacrifice", 2, r"\bsacrific|gambit"),
        ("zugzwang", 2, r"\bzugzwang"),
        ("tempo", 2, r"\btempo|initiative"),
        ("blocking", 2, r"\bblock(ing|ade)|deny (the|your) opponent"),
        ("spatial_packing", 2, r"\bpack(ing)?|fit (pieces|tiles) into|polyomino"),
        ("probability_estimation", 2, r"\bprobabilit|odds|expected value"),
        ("opponent_modelling", 2, r"\bread (your|the) opponent|opponent model|tells?\b"),
        ("coalition_forming", 2, r"\balliance|coalition|gang up"),
        ("signalling", 2, r"\bsignal|convention|partner communication"),
    ],
}

# Conditions worth extracting verbatim: the 'five fouls and you are benched'
# layer. Matched against whole sentences, so a captured trigger is always a
# complete, quotable rule rather than a fragment.
CONDITION_PATTERNS = [
    ("WIN", r"\bwins? (?:the (?:game|match|round)|immediately)\b|\bis (?:the|declared) winner\b|\bvictory (?:is|goes)\b"),
    ("WIN", r"\bfirst (?:player |team )?to (?:reach|score|collect|claim|complete|get)\b"),
    ("LOSE", r"\blos(?:es|e) the (?:game|match|round)\b|\bis defeated\b"),
    # ELIMINATE must be about a PLAYER. Without the subject requirement this
    # matched any component leaving play: "captured seeds are removed from the
    # game" (Andada), "the cards that are removed from the game" (Weiss
    # Schwarz). Three of four sampled matches were pieces, not people, and a
    # coherence repair built on them would have written loss_shape=ELIMINATION
    # across 47 worlds that have no player elimination at all.
    ("ELIMINATE", r"\b(?:player|team|participant|competitor|opponent|side)\w*\b"
                  r"[^.]{0,70}?\b(?:eliminat\w*|knocked out|sent off|fouls? out|"
                  r"fouled out|benched|disqualif\w*|ejected|out of the game|"
                  r"leaves the game|drops? out|is removed from (?:the game|play))\b"
                  r"|\b(?:eliminat\w*|knocked out|sent off|fouled out|disqualif\w*|"
                  r"ejected)\b[^.]{0,50}?\b(?:player|team|participant|competitor)\b"
                  r"|\blast (?:player|team|one) (?:standing|remaining|left)\b"),
    # BOUNDARY requires a NUMBER. 'at least' and 'maximum' on their own match
    # ordinary prose -- 'at least not being used as if it is worth anything'
    # was filed as a rule of Monopoly. 45% of extracted BOUNDARY rows were that
    # kind of noise. A boundary with no threshold is not machine-checkable,
    # which is the entire reason thresholded conditions rank first.
    ("BOUNDARY", r"\b(?:maximum|at most|no more than|hand limit|limit(?:ed)? (?:of|to)|"
                 r"cannot exceed|may not exceed|up to a maximum|capped at|"
                 r"no fewer than|at least)\b[^.]{0,40}?"
                 r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
                 r"eleven|twelve|fifteen|twenty)\b"),
    ("TERMINATE", r"\b(?:the game ends|game is over|play ends|the round ends|"
                  r"ends immediately|ends when|final round)\b"),
    ("PENALTY", r"\b(?:penalt\w*|foul\w*|infraction|forfeit\w*|yellow card|"
                r"red card|free throw|technical)\b"),
]

WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
            "twelve": 12, "fifteen": 15, "twenty": 20}

THRESHOLD_RE = re.compile(
    r"\b(\d{1,4}|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"fifteen|twenty)\s+"
    r"(personal fouls?|fouls?|cards?|points?|tokens?|lives?|strikes?|turns?|"
    r"rounds?|pieces?|tricks?|players?|columns?|seconds?|minutes?|warnings?|"
    r"penalt(?:y|ies)|hits?|wounds?|tiles?|chips?|coins?|sets?)\b", re.I)

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\"'“])")


def sentences(text):
    for para in (text or "").split("\n"):
        para = para.strip()
        if len(para) < 20 or para.startswith("=="):
            continue
        for s in _SENT_SPLIT.split(para):
            s = " ".join(s.split())
            if 25 <= len(s) <= 400:
                yield s


# Historical and imprecise polities that Wikidata gives as country of origin
# ('Northern Song dynasty', 'Ancient Egypt', 'Achaemenid Empire'). Matched as
# substrings after the exact table misses, so the region column survives the
# fact that most old games predate modern states.
REGION_HINTS = [
    ("EAST_ASIA", r"china|chinese|song dynasty|tang|ming|qing|han dynasty|"
                  r"japan|nippon|korea|joseon|goryeo|taiwan|mongol"),
    ("SOUTH_ASIA", r"india|bharat|mughal|maurya|sri lanka|ceylon|nepal|pakistan|bengal"),
    ("SOUTHEAST_ASIA", r"thai|siam|indonesia|java|philippin|vietnam|malay|burma|myanmar|khmer"),
    ("WEST_ASIA", r"persia|iran|achaemenid|sasanian|mesopotamia|sumer|babylon|assyria|"
                  r"turkey|ottoman|anatolia|levant|syria|iraq|arabia|israel|judea|phoenicia"),
    ("CENTRAL_ASIA", r"uzbek|kazakh|turkestan|sogdia|tajik"),
    ("AFRICA", r"egypt|nubia|ethiopia|abyssinia|nigeria|ghana|ashanti|mali|songhai|"
               r"kenya|tanzania|zanzibar|sudan|somali|congo|zimbabwe|africa|yoruba|igbo"),
    ("EUROPE_SOUTH", r"rome|roman|italy|italian|greece|greek|hellen|byzant|spain|"
                     r"spanish|portugal|etruscan|sicil"),
    ("EUROPE_WEST", r"england|english|britain|british|united kingdom|france|french|"
                    r"german|prussia|netherlands|dutch|belgi|austria|swiss|switzerland|ireland|wales|scotland"),
    ("EUROPE_NORTH", r"sweden|norway|denmark|danish|finland|iceland|norse|viking|"
                     r"estonia|latvia|lithuania|scandinav"),
    ("EUROPE_EAST", r"poland|polish|russia|soviet|ukrain|czech|bohemia|hungary|"
                    r"romania|bulgaria|serbia|croatia|slovak|balkan"),
    ("NORTH_AMERICA", r"united states|u\.s\.|america(n)?\b|canada|inuit|iroquois|"
                      r"navajo|cherokee|apache"),
    ("CENTRAL_AMERICA", r"mexico|maya|aztec|mexica|guatemala|cuba|caribbean|taino|olmec"),
    ("SOUTH_AMERICA", r"brazil|argentin|peru|inca|chile|colombia|bolivia|andes"),
    ("OCEANIA", r"australia|aborigin|new zealand|maori|hawaii|polynesia|fiji|"
                r"samoa|papua|melanesia|micronesia"),
]


def region_for(country):
    """Country-of-origin string -> region, tolerant of historical polities."""
    if not country:
        return None
    hit = T.COUNTRY_REGION.get(country)
    if hit:
        return hit
    low = country.lower()
    for region, pat in REGION_HINTS:
        if re.search(pat, low):
            return region
    return None


def pool_text(rec):
    parts = [rec.get("name") or "", rec.get("description") or ""]
    parts += rec.get("genres") or []
    parts += rec.get("instances") or []
    parts.append(rec.get("wp_extract") or "")
    return " \n ".join(parts)


def _score(text, rules):
    hits = {}
    for value, weight, pat in rules:
        n = len(re.findall(pat, text, re.I))
        if n:
            hits[value] = hits.get(value, 0) + weight * min(n, 3)
    return hits


SINGLE = ("information", "interaction", "turn_structure", "exogenous_process",
          "loss_shape", "horizon", "scoring_shape", "solved_status")
MULTI = ("media", "randomness_sources", "live_axes", "strategies", "algorithms")


def classify(rec):
    """-> dict of declared fields. Absent evidence yields absent keys, not defaults."""
    text = pool_text(rec)
    out = {}

    for field in SINGLE:
        hits = _score(text, RULES[field])
        if hits:
            out[field] = max(hits, key=hits.get)

    for field in MULTI:
        hits = _score(text, RULES[field])
        if hits:
            cut = max(hits.values()) * 0.34
            out[field] = sorted([v for v, s in hits.items() if s >= cut])

    # --- temporal -------------------------------------------------------
    inc = rec.get("inception")
    year = None
    if inc:
        m = re.match(r"^(-?\d{1,6})-", str(inc))
        if m:
            year = int(m.group(1))
    if year is None:
        # 'dated to c. 2620 BCE' / 'invented in 1935' from the extract
        m = re.search(r"\b(\d{3,4})\s*BCE?\b", text)
        if m:
            year, out["year_precision"] = -int(m.group(1)), "century"
        else:
            m = re.search(r"\b(?:invented|introduced|published|released|created|devised)"
                          r"[^.]{0,40}?\b(1[5-9]\d{2}|20[0-2]\d)\b", text, re.I)
            if m:
                year, out["year_precision"] = int(m.group(1)), "exact"
    else:
        out["year_precision"] = "exact"
    if year is not None:
        out["year_created"] = year
        out["epoch"] = T.epoch_for(year)

    # --- cultural -------------------------------------------------------
    c = rec.get("country")
    if c:
        out["region"] = region_for(c)

    # --- players --------------------------------------------------------
    pmin, pmax = rec.get("players_min"), rec.get("players_max")
    pmin = int(pmin) if pmin not in (None, "") else None
    pmax = int(pmax) if pmax not in (None, "") else None
    if pmin is None or pmax is None:
        m = re.search(r"\b(\d+)\s*(?:to|-|–)\s*(\d+)\s+players\b", text, re.I)
        if m:
            pmin = pmin or int(m.group(1))
            pmax = pmax or int(m.group(2))
        else:
            m = re.search(r"\bfor\s+(two|three|four|five|six|2|3|4|5|6)\s+players\b", text, re.I)
            if m:
                w = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
                v = w.get(m.group(1).lower(), None) or int(m.group(1))
                pmin = pmin or v
                pmax = pmax or v
    if pmin is not None:
        out["players_min"] = pmin
    if pmax is not None:
        out["players_max"] = pmax
    if pmin is not None or pmax is not None:
        a, b = pmin, pmax
        out["players_notation"] = (str(a) if a == b else
                                   "%s-%s" % (a if a is not None else "?",
                                              b if b is not None else "+"))
        out["solitaire_capable"] = 1 if (a == 1) else 0
    if out.get("interaction") == "SOLITAIRE":
        out["solitaire_capable"] = 1
    if out.get("interaction") == "TEAM":
        out["team_play"] = 1

    # --- age ------------------------------------------------------------
    m = re.search(r"\bages?\s+(\d{1,2})\s*(?:\+|and up|or older)", text, re.I)
    if m:
        out["min_age"] = int(m.group(1))
        out["age_band"] = T.age_band_for(out["min_age"])
    elif re.search(r"\bchildren's game|\bkids'? game|\bplayed by (young )?children\b"
                   r"|\bnursery (game|rhyme)|\bplayground game", text, re.I):
        # a bare mention of 'children' is not an audience claim -- most game
        # articles mention children somewhere. Require the phrase to be about
        # the game itself.
        out["age_band"] = "CHILD"

    # --- length ---------------------------------------------------------
    m = re.search(r"\b(\d{1,3})\s*(?:to|-|–)?\s*(\d{1,3})?\s*minutes?\b", text, re.I)
    if m:
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        out["length_minutes"] = (lo + hi) // 2

    # --- determinism by absence -----------------------------------------
    # Abstract games rarely assert 'perfect information' or 'no luck'; they
    # simply never mention chance. Chess and Nim both came back with NO
    # exogenous_process at all because every positive pattern needs a phrase
    # that is not there. Across a long article, the ABSENCE of all chance
    # vocabulary is itself evidence -- but only across a long article, so this
    # is gated on having enough text for the silence to mean something.
    if len(text) > 3000:
        chance = re.search(
            r"\bdice|\bdie\b|shuffl|random|\bluck|chance|deal(t|s)? (from|out)|"
            r"draw pile|spinner|coin flip|probabilit|face-?down|hidden|"
            r"\bbag\b|deck\b", text, re.I)
        turnish = re.search(r"\bmoves?\b|\bturns?\b|\bpieces?\b|\bplayers? move", text, re.I)
        if not chance and turnish:
            out.setdefault("exogenous_process", "NONE")
            out.setdefault("information", "PERFECT")
            out.setdefault("randomness_sources", ["NONE"])
            if "loss_shape" not in out:
                out["loss_shape"] = "OPPORTUNITY_ONLY"

    # --- derived scores -------------------------------------------------
    out["luck_factor"] = _luck(out, text)
    out["rules_complexity"] = _rules_complexity(out, text)
    out["strategic_depth"] = _depth(out, text)
    out["information_score"] = _information(out)
    out["complexity_score"] = round(
        0.4 * (out["rules_complexity"] / 5.0)
        + 0.4 * (out["strategic_depth"] / 5.0)
        + 0.2 * out["information_score"], 4)
    out["tractability"] = _tractability(out)
    out["zero_sum"] = 0 if out.get("interaction") in ("COOPERATIVE", "SOLITAIRE") else 1
    return out


def _luck(out, text):
    """0..1 share of outcome attributable to chance under equal skill, or None.

    Returns None when the text supports no conclusion either way. This module's
    own contract is that a world with no keyword hits is left NULL rather than
    defaulted, and this function was the one place violating it: an absent
    randomness set used to score 0.35, a confident-looking 'moderately lucky'
    for worlds where nothing at all had been observed. Gomoku and Fanorona --
    deterministic perfect-information abstracts -- carried 0.35 on that basis.
    A NULL luck_factor is a true statement; 0.35 was a fabricated one.
    """
    src = set(out.get("randomness_sources") or [])
    determinism = re.search(
        r"\bno (element of )?(luck|chance)|perfect information|deterministic|"
        r"no randomness", text, re.I)
    if "NONE" in src and len(src) == 1:
        base = 0.02
    elif not src:
        if out.get("exogenous_process") == "NONE" or determinism:
            base = 0.03          # positively deterministic, just not enumerated
        else:
            return None          # genuinely no evidence -- say so
    else:
        base = 0.30
        if "DICE" in src:
            base += 0.28
        if "DECK_SHUFFLE" in src or "DECK_DEPLETING" in src:
            base += 0.18
        if "SPINNER" in src or "TILE_BAG" in src:
            base += 0.12
    if out.get("exogenous_process") == "NONE":
        base = min(base, 0.05)
    if re.search(r"\bpure(ly)? (luck|chance)|no (skill|strategy)|entirely (luck|chance)", text, re.I):
        base = 0.95
    if re.search(r"\bno (element of )?(luck|chance)|perfect information", text, re.I):
        base = min(base, 0.08)
    if "SOLVED_STRONG" == out.get("solved_status"):
        base = min(base, 0.05)
    return round(min(max(base, 0.0), 1.0), 3)


def _rules_complexity(out, text):
    """1..5, BGG-weight-like. Proxied by rule-surface signals in the text."""
    s = 1.6
    s += 0.30 * len(out.get("live_axes") or [])
    if out.get("turn_structure") in ("PHASE_STRUCTURED", "ACTION_POINT",
                                     "PRIORITY_QUEUE", "VARIABLE_ORDER"):
        s += 0.7
    if out.get("interaction") in ("TRAITOR", "NEGOTIATION", "SEMI_COOPERATIVE"):
        s += 0.5
    if "RPG" in (out.get("media") or []) or "WARGAME" in (out.get("media") or []):
        s += 1.2
    if re.search(r"\bexpansion|supplement|advanced rules|optional rules", text, re.I):
        s += 0.4
    n_words = len(text.split())
    s += min(n_words / 2000.0, 0.8)
    return round(min(max(s, 1.0), 5.0), 2)


def _depth(out, text):
    s = 2.0
    s += 0.25 * len(out.get("strategies") or [])
    s += 0.30 * len(out.get("algorithms") or [])
    if out.get("information") == "PERFECT":
        s += 0.4
    if out.get("solved_status") in ("SOLVED_STRONG", "SOLVED_WEAK"):
        s -= 0.6
    # luck_factor may be None (no evidence); an unknown must not be treated
    # as a low value and silently inflate strategic depth.
    lf = out.get("luck_factor")
    if lf is not None:
        s -= 1.6 * max(lf - 0.5, 0)
    return round(min(max(s, 1.0), 5.0), 2)


def _information(out):
    """Rough 0..1 'how much is there to know' -- drives deepening priority."""
    axes = len(out.get("live_axes") or [])
    rnd = len(out.get("randomness_sources") or [])
    bonus = 0.0
    if out.get("information") in ("HIDDEN_PRIVATE", "IMPERFECT", "ASYMMETRIC"):
        bonus += 0.15
    if out.get("interaction") in ("TRAITOR", "NEGOTIATION"):
        bonus += 0.15
    if out.get("turn_structure") in ("REAL_TIME", "SIMULTANEOUS"):
        bonus += 0.1
    return round(min(axes / 8.0 * 0.5 + rnd / 5.0 * 0.25 + bonus, 1.0), 4)


def _tractability(out):
    media = set(out.get("media") or [])
    # A game the literature calls solved is, by construction, one whose state
    # space someone has actually enumerated. That is the tractability claim,
    # and it is the only cheap positive evidence for EXACT available from text.
    if out.get("solved_status") in ("SOLVED_STRONG", "SOLVED_WEAK",
                                    "SOLVED_ULTRA_WEAK"):
        return "EXACT"
    if media & {"VIDEO", "RPG", "SPORT", "LARP", "MINIATURES"}:
        return "SAMPLING_ONLY"
    if out.get("turn_structure") == "REAL_TIME":
        return "SAMPLING_ONLY"
    if out.get("interaction") == "NEGOTIATION":
        return "INTRACTABLE"
    axes = len(out.get("live_axes") or [])
    if axes <= 2 and (out.get("exogenous_process") in ("IID", "DEPLETING_DECK", "NONE")):
        return "EXACT_WITH_CUT"
    return "SAMPLING_ONLY"


def extract_conditions(text, limit=24):
    """-> [(kind, trigger_sentence, threshold, effect)] for the conditions table.

    Sentence-scoped, so a trigger is always a complete quotable rule. Sentences
    carrying an explicit threshold ('six personal fouls') are ranked first --
    those are the ones that make a condition machine-checkable rather than prose.
    """
    scored, seen = [], set()
    compiled = [(k, re.compile(p, re.I)) for k, p in CONDITION_PATTERNS]
    for sent in sentences(text):
        key = sent.lower()
        if key in seen:
            continue
        kinds = [k for k, rx in compiled if rx.search(sent)]
        if not kinds:
            continue
        seen.add(key)
        # ELIMINATE/WIN/TERMINATE are more informative than a bare PENALTY hit
        order = ["ELIMINATE", "WIN", "TERMINATE", "LOSE", "BOUNDARY", "PENALTY"]
        kind = sorted(set(kinds), key=lambda k: order.index(k))[0]
        m = THRESHOLD_RE.search(sent)
        th = None
        if m:
            n = m.group(1).lower()
            th = "%s %s" % (WORD_NUM.get(n, n), m.group(2).lower())
        eff = None
        me = re.search(r"\b(?:is|are|shall be|must)\s+"
                       r"(benched|ejected|sent off|eliminated|disqualified|"
                       r"removed|out of the game|awarded [^,.]{0,40})", sent, re.I)
        if me:
            eff = me.group(1)
        scored.append((0 if th else 1, kind, sent[:400], th, eff))
    scored.sort(key=lambda r: (r[0], order_index(r[1])))
    return [(k, s, th, eff) for _, k, s, th, eff in scored[:limit]]


def order_index(kind):
    order = ["ELIMINATE", "WIN", "TERMINATE", "LOSE", "BOUNDARY", "PENALTY"]
    return order.index(kind) if kind in order else 9


def novelty(out, seen_counts, total):
    """Rarity of this world's declared vector against what the atlas already holds.

    Directly implements charter v2 s41: the next world should be the one that most
    changes what we know. A world whose every declared value is already common
    scores near 0; one occupying an empty cell scores near 1.
    """
    if total <= 0:
        return 1.0
    acc, n = 0.0, 0
    for f in T.DECLARED_VECTOR:
        v = out.get(f)
        if not v:
            continue
        c = seen_counts.get((f, v), 0)
        acc += math.exp(-3.0 * (c / float(total)))
        n += 1
    if not n:
        return 0.5
    return round(acc / n, 4)


if __name__ == "__main__":
    import json
    import sys

    import wikipedia
    title = sys.argv[1] if len(sys.argv) > 1 else "Can't Stop (board game)"
    ex = wikipedia.extract([title]).get(title, "")
    rec = {"name": title, "wp_extract": ex, "genres": [], "instances": []}
    out = classify(rec)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    print("\nconditions:")
    for k, s, th in extract_conditions(ex):
        print(" ", k, "|", th, "|", s[:110])
