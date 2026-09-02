"""Curated seeds, chosen to fill named cells of the declared grid.

Why this file exists. Every other probe slices the space by CLASS, EPOCH or
REGION -- properties of a game's surface and provenance. None of them can reach a
MECHANISM, and the atlas's biggest holes are all mechanical. After five ticks the
catalog held 323 worlds and not one push-your-luck game: no Yahtzee, no Farkle,
no Pig, no Can't Stop, no Incan Gold. `loss_shape=TOTAL_RUIN` was empty, and that
is the precondition r0003's entire scope statement rests on
(`ludus/atlas/CIRCUIT_LEDGER.md`). Wikipedia has no press-your-luck category to
crawl -- it was checked, and returns zero members.

So this is charter v2 s41 (active selection) applied to the catalog: name the
empty cell, then name the worlds that occupy it. Each entry carries the cell it
was chosen for, so a seed that fails to land in its target cell after enrichment
is a visible classifier bug rather than a silent miss.

Curated seeds skip the Wikidata membership gate: they are hand-verified, and the
gate exists to filter generous enumeration pages, not this list.
"""
from __future__ import annotations

# (wikipedia title, cell this seed is meant to fill)
SEEDS = [

    # ---- loss_shape = TOTAL_RUIN --------------------------------------
    # The empty cell that matters most to the bench.
    ("Yahtzee", "TOTAL_RUIN"),
    ("Farkle", "TOTAL_RUIN"),
    ("Pig (dice game)", "TOTAL_RUIN"),
    ("Can't Stop (board game)", "TOTAL_RUIN"),
    ("Incan Gold", "TOTAL_RUIN"),
    ("Cosmic Wimpout", "TOTAL_RUIN"),
    ("Zombie Dice", "TOTAL_RUIN"),
    ("Blackjack", "TOTAL_RUIN"),
    ("Bank (dice game)", "TOTAL_RUIN"),
    ("Ten Thousand (dice game)", "TOTAL_RUIN"),
    ("Left, Center, Right", "TOTAL_RUIN"),
    ("Perudo", "TOTAL_RUIN"),

    # ---- information = PERFECT, exogenous = NONE, tractability = EXACT --
    ("Chess", "PERFECT/NONE"),
    ("Go (game)", "PERFECT/NONE"),
    ("Draughts", "PERFECT/NONE"),
    ("Nim", "PERFECT/NONE/EXACT"),
    ("Tic-tac-toe", "PERFECT/NONE/EXACT"),
    ("Connect Four", "PERFECT/NONE/EXACT"),
    ("Reversi", "PERFECT/NONE"),
    ("Hex (board game)", "PERFECT/NONE"),
    ("Nine men's morris", "PERFECT/NONE/EXACT"),
    ("Shogi", "PERFECT/NONE"),
    ("Xiangqi", "PERFECT/NONE"),
    ("Hnefatafl", "PERFECT/NONE"),
    ("Oware", "PERFECT/NONE"),
    ("Gomoku", "PERFECT/NONE"),
    ("Hive (game)", "PERFECT/NONE"),
    ("Onitama", "PERFECT/NONE/EXACT"),
    ("Abalone (board game)", "PERFECT/NONE"),
    ("Arimaa", "PERFECT/NONE"),
    ("Game of the Amazons", "PERFECT/NONE"),
    ("Quarto (board game)", "PERFECT/NONE/EXACT"),
    ("Santorini (game)", "PERFECT/NONE"),
    ("Dou shou qi", "PERFECT/NONE"),
    ("Fanorona", "PERFECT/NONE"),
    ("Alquerque", "PERFECT/NONE"),
    ("Konane", "PERFECT/NONE"),

    # ---- turn_structure = SIMULTANEOUS ---------------------------------
    ("Rock paper scissors", "SIMULTANEOUS"),
    ("7 Wonders (board game)", "SIMULTANEOUS"),
    ("Sushi Go!", "SIMULTANEOUS"),
    ("RoboRally", "SIMULTANEOUS"),
    ("Diplomacy (game)", "SIMULTANEOUS"),
    ("Pit (game)", "SIMULTANEOUS"),
    ("Jungle Speed", "SIMULTANEOUS"),
    ("Dutch Blitz", "SIMULTANEOUS"),
    ("Spoons (card game)", "SIMULTANEOUS"),
    ("Captain Sonar", "SIMULTANEOUS"),

    # ---- turn_structure = ACTION_POINT / VARIABLE_ORDER / PRIORITY_QUEUE
    ("Pandemic (board game)", "ACTION_POINT"),
    ("Agricola (board game)", "ALLOCATE/ACTION_POINT"),
    ("Caylus (board game)", "ALLOCATE/VARIABLE_ORDER"),
    ("Tzolk'in: The Mayan Calendar", "ALLOCATE"),
    ("Thebes (board game)", "PRIORITY_QUEUE"),
    ("Patchwork (board game)", "PRIORITY_QUEUE"),
    ("Glen More (board game)", "PRIORITY_QUEUE"),
    ("Through the Ages", "ACTION_POINT"),
    ("Lords of Waterdeep", "ALLOCATE"),
    ("Viticulture (board game)", "ALLOCATE"),
    ("Le Havre (board game)", "ALLOCATE"),

    # ---- horizon = RACE_TO_TARGET --------------------------------------
    ("Backgammon", "RACE_TO_TARGET"),
    ("Pachisi", "RACE_TO_TARGET"),
    ("Ludo", "RACE_TO_TARGET"),
    ("Snakes and ladders", "RACE_TO_TARGET"),
    ("Sorry! (game)", "RACE_TO_TARGET"),
    ("Mille Bornes", "RACE_TO_TARGET"),
    ("Ticket to Ride (board game)", "RACE_TO_TARGET"),
    ("Formula Dé", "RACE_TO_TARGET"),

    # ---- loss_shape = NONE / OPPORTUNITY_ONLY --------------------------
    ("Splendor (game)", "NONE/OPPORTUNITY_ONLY"),
    ("Azul (board game)", "OPPORTUNITY_ONLY"),
    ("Sagrada (board game)", "OPPORTUNITY_ONLY"),
    ("Kingdomino", "OPPORTUNITY_ONLY"),
    ("Carcassonne (board game)", "NONE"),
    ("Wingspan (board game)", "NONE"),

    # ---- interaction = PARALLEL / SEMI_COOPERATIVE ---------------------
    ("Bingo (American version)", "PARALLEL"),
    ("Take It Easy (game)", "PARALLEL"),
    ("Cartographers (board game)", "PARALLEL"),
    ("Welcome To...", "PARALLEL"),
    ("Karuba", "PARALLEL"),
    ("Dead of Winter: A Crossroads Game", "SEMI_COOPERATIVE"),
    ("Archipelago (board game)", "SEMI_COOPERATIVE"),

    # ---- BID axis -------------------------------------------------------
    ("Contract bridge", "BID"),
    ("Modern Art (board game)", "BID"),
    ("Ra (board game)", "BID"),
    ("High Society (game)", "BID"),
    ("For Sale (game)", "BID"),          # bench BACKLOG.md item 1
    ("Amun-Re (board game)", "BID"),
    ("Skat", "BID"),

    # ---- exogenous = HIDDEN_FIXED --------------------------------------
    ("Minesweeper (video game)", "HIDDEN_FIXED"),
    ("Battleship (game)", "HIDDEN_FIXED"),
    ("Mastermind (board game)", "HIDDEN_FIXED"),
    ("Cluedo", "HIDDEN_FIXED"),
    ("Sudoku", "HIDDEN_FIXED"),
    ("Nonogram", "HIDDEN_FIXED"),
    ("Hangman (game)", "HIDDEN_FIXED"),

    # ---- ancient / cultural depth (epoch + region coverage) ------------
    ("Senet", "DEEP_ANTIQUITY"),
    ("Royal Game of Ur", "DEEP_ANTIQUITY"),
    ("Mehen (game)", "DEEP_ANTIQUITY"),
    ("Liubo", "ANCIENT/EAST_ASIA"),
    ("Ludus latrunculorum", "ANCIENT/EUROPE_SOUTH"),
    ("Petteia", "ANCIENT/EUROPE_SOUTH"),
    ("Patolli", "CENTRAL_AMERICA"),
    ("Bul (game)", "CENTRAL_AMERICA"),
    ("Yut", "EAST_ASIA"),
    ("Sugoroku", "EAST_ASIA"),
    ("Bao (game)", "AFRICA"),
    ("Omweso", "AFRICA"),
    ("Sungka", "SOUTHEAST_ASIA"),
    ("Congkak", "SOUTHEAST_ASIA"),
    ("Chaupar", "SOUTH_ASIA"),
    ("Ashta Chamma", "SOUTH_ASIA"),
    ("Surakarta (game)", "SOUTHEAST_ASIA"),
    ("Tab (game)", "WEST_ASIA"),
    ("Mu Torere", "OCEANIA"),
    ("Bagh-Chal", "SOUTH_ASIA"),

    # ---- real-time / continuous-time, high complexity ------------------
    ("Tetris", "CONTINUOUS_TIME"),
    ("StarCraft", "CONTINUOUS_TIME"),
    ("Dota 2", "CONTINUOUS_TIME"),
    ("Rubik's Cube", "NONE/EXACT"),
    ("Civilization (video game)", "SAMPLING_ONLY"),
    ("Poker", "HIDDEN_PRIVATE/BLUFF"),
    ("Texas hold 'em", "HIDDEN_PRIVATE/BLUFF"),
    ("Mahjong", "DEPLETING_DECK/EAST_ASIA"),
    ("Scrabble", "TILE_BAG"),
    ("Bridge (card game)", "BID"),
]


def pending(con, k=40):
    """Seed titles not yet in the atlas, with their target cells."""
    have = {r[0] for r in con.execute(
        "SELECT wp_title FROM worlds WHERE wp_title IS NOT NULL")}
    have |= {r[0] for r in con.execute("SELECT name FROM worlds")}
    out = [(t, cell) for t, cell in SEEDS if t not in have]
    return out[:k]


def audit(con):
    """Did each landed seed reach the cell it was chosen for?

    A seed that misses its target cell is a classifier bug made visible. This is
    the cheapest standing check the atlas has on its own classification quality.
    """
    rows = {r["wp_title"]: dict(r) for r in con.execute(
        "SELECT wp_title, loss_shape, information, exogenous_process, horizon,"
        "       turn_structure, interaction, tractability, epoch, region,"
        "       live_axes, catalog_state"
        "  FROM worlds WHERE wp_title IS NOT NULL")}
    hits, misses, absent = [], [], []
    for title, cell in SEEDS:
        w = rows.get(title)
        if not w:
            absent.append((title, cell))
            continue
        vals = {str(v) for v in w.values() if v}
        blob = " ".join(vals)
        want = [p for p in cell.split("/")]
        if any(p in blob for p in want):
            hits.append((title, cell))
        else:
            misses.append((title, cell, w.get("catalog_state")))
    return hits, misses, absent
