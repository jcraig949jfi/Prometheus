"""Deep artifacts for one world: object model, state transition diagram,
simulated turn/clock trace, and the dossier that binds them.

IMPORTANT about what these artifacts are. They are generated from the world's
DECLARED VECTOR -- the atlas's own structural classification -- and not from a
rulebook. A state diagram here is the shape of the world's *decision interface*,
not a claim about how the published game plays. That distinction is the same one
ludus/bench/RULES_AUDIT.md draws: the machinery is game-agnostic and correct;
any claim about a named commercial game stays HYPOTHESIZED until audited.

The trace exists because a structural vector is easy to nod along to and hard to
check. Forcing the atlas to emit a concrete sequence of events makes an incoherent
classification obvious -- a world tagged STOP with loss_shape NONE produces a
trace where the stopping decision visibly does not matter, and that is a bug
report about the classification, not a curiosity.
"""
from __future__ import annotations

import random
import textwrap

import taxonomy as T  # noqa: F401  (vocabulary reference)

# --------------------------------------------------------------- object model

ENTITY_BY_MEDIUM = {
    "BOARD": [("Board", "spatial substrate; cells carry position and occupancy"),
              ("Piece", "movable token owned by a player")],
    "CARD": [("Deck", "ordered multiset, drawn without replacement"),
             ("Hand", "private multiset held by one player"),
             ("DiscardPile", "public accumulation of spent cards")],
    "DICE": [("DicePool", "n dice, each an iid categorical draw"),
             ("Roll", "realised outcome of a pool")],
    "TILE": [("TileBag", "unordered draw source"), ("Layout", "placed tiles and their adjacencies")],
    "RPG": [("Character", "persistent stat block owned by a player"),
            ("GameMaster", "adjudicating agent outside the scoring loop"),
            ("Scenario", "authored state the players traverse")],
    "VIDEO": [("WorldState", "simulation state advanced by the engine"),
              ("Avatar", "player-controlled agent"), ("Clock", "frame or tick counter")],
    "SPORT": [("Pitch", "bounded physical region"), ("Player", "embodied agent with a foul count"),
              ("Clock", "counts down; stoppages are rule events"),
              ("Official", "detects infractions and applies penalties")],
    "PUZZLE": [("Configuration", "the arrangement to be resolved"),
               ("Constraint", "predicate a legal configuration must satisfy")],
    "MANCALA": [("Pits", "cyclic array of counts"), ("Store", "player's banked seeds")],
    "TRICK_TAKING": [("Trick", "one card per player; a winner is determined"),
                     ("Trump", "suit that dominates the ordering")],
}

AXIS_ENTITY = {
    "STOP": ("Pot", "value accumulated this episode and at risk until banked"),
    "SELECT": ("OptionSet", "the choices available after an exogenous draw"),
    "ALLOCATE": ("ResourcePool", "divisible capacity committed across slots"),
    "BID": ("Auction", "priced competition resolving to one winner"),
    "ORDER": ("Sequence", "the permutation under the player's control"),
    "DISCARD": ("DiscardChoice", "what is given up to satisfy a limit"),
    "TRADE": ("Offer", "proposed exchange between two agents"),
    "NEGOTIATE": ("Agreement", "non-binding or binding commitment between agents"),
    "SPATIAL": ("Placement", "position subject to geometric legality"),
    "TIMING": ("Initiative", "who acts, and when, relative to others"),
    "BLUFF": ("Belief", "what an observer is induced to think is true"),
    "COMMIT_BLIND": ("SealedChoice", "irrevocable choice made without observation"),
}


def object_model(w):
    """-> markdown object model derived from media + live axes + conditions."""
    ents, seen = [], set()
    for m in w.get("media") or []:
        for name, doc in ENTITY_BY_MEDIUM.get(m, []):
            if name not in seen:
                seen.add(name)
                ents.append((name, doc))
    for ax in w.get("live_axes") or []:
        pair = AXIS_ENTITY.get(ax)
        if pair and pair[0] not in seen:
            seen.add(pair[0])
            ents.append(pair)
    if not ents:
        ents = [("State", "opaque; no medium or axis evidence was found"),
                ("Player", "an agent that selects among legal successors")]

    lines = ["```", "Episode", "  players      : %s" % (w.get("players_notation") or "?"),
             "  turn_structure: %s" % (w.get("turn_structure") or "?"),
             "  horizon       : %s" % (w.get("horizon") or "?"),
             "  scoring       : %s" % (w.get("scoring_shape") or "?"), ""]
    for name, doc in ents:
        lines.append("%-14s %s" % (name, "-- " + doc))
    lines.append("```")
    return "\n".join(lines)


# ----------------------------------------------------------- state diagrams

def state_diagram(w):
    """-> mermaid stateDiagram-v2 for the world's decision interface."""
    axes = set(w.get("live_axes") or [])
    exo = w.get("exogenous_process") or "NONE"
    loss = w.get("loss_shape") or "NONE"
    ts = w.get("turn_structure") or "STRICT_TURN"
    horizon = w.get("horizon") or "VARIABLE"

    L = ["stateDiagram-v2", "    [*] --> Setup"]

    if ts == "REAL_TIME":
        L += ["    Setup --> Tick",
              "    Tick --> Resolve : clock advances dt",
              "    Resolve --> Tick : no termination",
              "    note right of Tick",
              "        continuous time: agents act without a turn boundary",
              "    end note"]
        term = "Resolve"
    elif ts == "SIMULTANEOUS":
        L += ["    Setup --> Commit",
              "    Commit --> Reveal : all players choose blind",
              "    Reveal --> Resolve"]
        term = "Resolve"
    elif ts == "AUCTION_ROUND":
        L += ["    Setup --> Bid", "    Bid --> Resolve : highest bid wins",
              "    Resolve --> Bid : lots remain"]
        term = "Resolve"
    elif ts == "TRICK_ROUND":
        L += ["    Setup --> Lead", "    Lead --> Follow",
              "    Follow --> AwardTrick : all players played",
              "    AwardTrick --> Lead : cards remain"]
        term = "AwardTrick"
    else:
        # the canonical LUDUS bench shape: draw -> select -> stop
        if exo == "NONE":
            L += ["    Setup --> Choose"]
            cur = "Choose"
        else:
            L += ["    Setup --> Draw",
                  "    Draw --> Options : exogenous %s" % exo]
            cur = "Options"
        if "SELECT" in axes:
            L += ["    %s --> Select : k options" % cur,
                  "    Select --> Taken"]
            cur = "Taken"
        else:
            L += ["    %s --> Taken : forced, single option" % cur]
            cur = "Taken"
        if "STOP" in axes:
            L += ["    Taken --> StopDecision",
                  "    StopDecision --> Bank : stop",
                  "    StopDecision --> Draw : continue"]
            term = "Bank"
        else:
            L += ["    Taken --> Draw : continue" if exo != "NONE"
                  else "    Taken --> Choose : continue"]
            term = "Taken"

    # loss edge
    if loss == "TOTAL_RUIN":
        L += ["    Draw --> Bust : no legal option",
              "    Bust --> [*] : pot forfeited entirely"]
    elif loss == "PARTIAL_DECAY":
        L += ["    Draw --> Decay : adverse outcome",
              "    Decay --> Draw : holdings degraded, episode continues"]
    elif loss == "ELIMINATION":
        L += ["    %s --> Eliminated : threshold breached" % term,
              "    Eliminated --> [*] : player leaves play"]

    # termination edge
    end = {"RACE_TO_TARGET": "target reached",
           "CLOCK_LIMITED": "clock expires",
           "FIXED": "fixed round count reached",
           "VARIABLE": "supply exhausted",
           "OPEN_ENDED": "operator halts"}.get(horizon, "terminal condition")
    L += ["    %s --> [*] : %s" % (term, end)]
    return "\n".join(L)


# ------------------------------------------------------------------ traces

DRAW_FLAVOUR = {
    "IID": ("roll", "d6 pool"),
    "DEPLETING_DECK": ("draw", "deck"),
    "HIDDEN_FIXED": ("reveal", "fixed layout"),
    "CONTINUOUS_TIME": ("tick", "clock"),
    "OPPONENT_GENERATED": ("observe", "opponent move"),
    "NONE": ("none", "deterministic"),
}


def turn_trace(w, seed=None, max_events=26):
    """A concrete example episode, generated from the declared vector.

    Turn-based worlds get an event log. Worlds with no turn boundary get a clock
    trace instead, which is what the research item asks for: something to point at
    when the world has no 'move' to enumerate.
    """
    rng = random.Random(seed if seed is not None else (w.get("slug") or "x").__hash__() & 0xFFFF)
    ts = w.get("turn_structure") or "STRICT_TURN"
    if ts in ("REAL_TIME", "CONTINUOUS", "TICK_BASED"):
        return _clock_trace(w, rng, max_events), "CLOCK_TRACE"
    return _turn_trace(w, rng, max_events), "TURN_TRACE"


def _hdr(w, kind):
    return [
        "# %s -- %s" % (w.get("name"), kind),
        "# generated from the DECLARED vector, not from a rulebook.",
        "# structure: exo=%s loss=%s horizon=%s scoring=%s axes=%s" % (
            w.get("exogenous_process"), w.get("loss_shape"), w.get("horizon"),
            w.get("scoring_shape"), ",".join(w.get("live_axes") or []) or "-"),
        "",
    ]


def _turn_trace(w, rng, max_events):
    axes = set(w.get("live_axes") or [])
    exo = w.get("exogenous_process") or "NONE"
    loss = w.get("loss_shape") or "NONE"
    verb, src = DRAW_FLAVOUR.get(exo, ("draw", "source"))
    pmin = w.get("players_min") or 2
    n_players = max(1, min(pmin or 2, 4))

    out = _hdr(w, "simulated turn events")
    out.append("t=0    SETUP        players=%d  pot=0  capacity=%s"
               % (n_players, rng.randint(3, 8)))
    pot, t, bust_p = 0.0, 1, 0.10
    player = 1
    for _ in range(max_events):
        if t > max_events:
            break
        if exo != "NONE":
            k = rng.randint(1, 6)
            out.append("t=%-4d %-12s p%d %s from %s -> outcome #%d  (p=%.3f)"
                       % (t, "DRAW", player, verb, src, k, rng.random() * 0.3))
            t += 1
        n_opt = rng.randint(0, 4) if loss == "TOTAL_RUIN" else rng.randint(1, 4)
        if n_opt == 0 and loss == "TOTAL_RUIN":
            out.append("t=%-4d %-12s p%d no legal option -- BUST. pot %.1f -> 0.0"
                       % (t, "DEATH", player, pot))
            out.append("t=%-4d %-12s loss_shape=TOTAL_RUIN: entire pot forfeited"
                       % (t + 1, "NOTE"))
            break
        if "SELECT" in axes:
            ch = rng.randint(1, max(n_opt, 1))
            gain = round(rng.uniform(0.5, 3.5), 1)
            out.append("t=%-4d %-12s p%d %d options; take #%d  (pot_gain=+%.1f, capacity=-%d)"
                       % (t, "SELECT", player, n_opt, ch, gain, rng.randint(0, 2)))
            pot += gain
            t += 1
        else:
            gain = round(rng.uniform(0.5, 2.0), 1)
            pot += gain
            out.append("t=%-4d %-12s p%d single legal option taken (pot_gain=+%.1f)"
                       % (t, "FORCED", player, gain))
            t += 1
        for extra in ("BID", "ALLOCATE", "TRADE", "DISCARD", "SPATIAL", "BLUFF"):
            if extra in axes and rng.random() < 0.4:
                out.append("t=%-4d %-12s p%d %s" % (t, extra, player, {
                    "BID": "sealed bid of %d against %d rivals" % (rng.randint(1, 9), n_players - 1),
                    "ALLOCATE": "commits %d of %d capacity across %d slots"
                                % (rng.randint(1, 3), 5, rng.randint(2, 4)),
                    "TRADE": "offers 2:1 exchange to p%d" % (1 + (player % max(n_players, 2))),
                    "DISCARD": "discards to hand limit",
                    "SPATIAL": "places at (%d,%d); adjacency legal"
                               % (rng.randint(0, 7), rng.randint(0, 7)),
                    "BLUFF": "represents a holding it does not have",
                }[extra]))
                t += 1
        if "STOP" in axes:
            bust_p = min(0.85, bust_p + rng.uniform(0.05, 0.18))
            ev_cont = round(rng.uniform(0.4, 2.2), 2)
            stop = bust_p * pot >= ev_cont
            out.append("t=%-4d %-12s p%d pot=%.1f  P(bust|continue)=%.2f  E[gain]=%.2f -> %s"
                       % (t, "STOP?", player, pot, bust_p, ev_cont,
                          "BANK" if stop else "CONTINUE"))
            t += 1
            if stop:
                out.append("t=%-4d %-12s p%d banks %.1f  (pot now safe)" % (t, "BANK", player, pot))
                t += 1
                if w.get("horizon") == "RACE_TO_TARGET":
                    out.append("t=%-4d %-12s p%d progress toward target" % (t, "PROGRESS", player))
                    t += 1
                pot, bust_p = 0.0, 0.10
                player = 1 + (player % n_players)
        else:
            if rng.random() < 0.25:
                player = 1 + (player % n_players)
                out.append("t=%-4d %-12s turn passes to p%d" % (t, "ENDTURN", player))
                t += 1
    out.append("")
    out.append("terminal: %s" % (w.get("horizon") or "VARIABLE"))
    return "\n".join(out)


def _clock_trace(w, rng, max_events):
    """For worlds with no turn boundary: ticks, contention, and rule events."""
    out = _hdr(w, "simulated clock trace (no turn boundary)")
    n = max(2, min(w.get("players_max") or 4, 10))
    out.append("clk=0.000s  START        agents=%d  clock=%s" % (
        n, "counts down" if w.get("horizon") == "CLOCK_LIMITED" else "free running"))
    clk, fouls = 0.0, {i: 0 for i in range(1, n + 1)}
    for _ in range(max_events):
        clk += round(rng.uniform(0.2, 3.0), 3)
        a = rng.randint(1, n)
        r = rng.random()
        if r < 0.12:
            fouls[a] += 1
            out.append("clk=%.3fs  INFRACTION   a%d commits infraction (count=%d)"
                       % (clk, a, fouls[a]))
            if fouls[a] >= 5:
                out.append("clk=%.3fs  ELIMINATE    a%d reaches threshold -> removed from play"
                           % (clk, a))
                fouls[a] = -999
        elif r < 0.30:
            out.append("clk=%.3fs  CONTEST      a%d and a%d contend for the same resource"
                       % (clk, a, 1 + (a % n)))
        elif r < 0.45:
            out.append("clk=%.3fs  SCORE        a%d scores (+%d)" % (clk, a, rng.randint(1, 3)))
        elif r < 0.55:
            out.append("clk=%.3fs  STOPPAGE     clock halts; state frozen" % clk)
        else:
            out.append("clk=%.3fs  ACTION       a%d acts continuously; no turn boundary crossed"
                       % (clk, a))
    out.append("")
    out.append("note: elapsed time, not move count, is the episode's ordering variable.")
    return "\n".join(out)


# ------------------------------------------------------------------ dossier

def dossier(w, conditions, extract=None):
    axes = ", ".join(w.get("live_axes") or []) or "-"
    media = ", ".join(w.get("media") or []) or "-"
    trace, trace_kind = turn_trace(w)

    def row(k, v):
        return "| %s | %s |" % (k, v if v not in (None, "", []) else "--")

    md = ["# %s" % w.get("name"), ""]
    if w.get("description"):
        md += ["*%s*" % w["description"], ""]
    md += [
        "`%s` &nbsp; state: **%s** &nbsp; method: **%s**"
        % (w.get("slug"), w.get("catalog_state"), w.get("method")), "",
        "## Found layer (recorded, not trusted)", "",
        "| field | value |", "| --- | --- |",
        row("wikidata", w.get("qid")),
        row("wikipedia", w.get("wp_title")),
        row("genres (source)", ", ".join(w.get("genres") or [])),
        row("instance of (source)", ", ".join(w.get("instances") or [])),
        row("country of origin", w.get("country")),
        "",
        "## Declared layer (orders bench work)", "",
        "| field | value |", "| --- | --- |",
        row("year created", w.get("year_created")),
        row("epoch", w.get("epoch")),
        row("region", w.get("region")),
        row("media", media),
        row("players", w.get("players_notation")),
        row("age band", w.get("age_band")),
        row("exogenous process", w.get("exogenous_process")),
        row("loss shape", w.get("loss_shape")),
        row("live axes", axes),
        row("horizon", w.get("horizon")),
        row("scoring shape", w.get("scoring_shape")),
        row("information", w.get("information")),
        row("interaction", w.get("interaction")),
        row("turn structure", w.get("turn_structure")),
        row("tractability", w.get("tractability")),
        row("randomness", ", ".join(w.get("randomness_sources") or [])),
        row("luck factor", w.get("luck_factor")),
        row("rules complexity", w.get("rules_complexity")),
        row("strategic depth", w.get("strategic_depth")),
        row("novelty", w.get("novelty")),
        row("solved status", w.get("solved_status")),
        row("strategies", ", ".join(w.get("strategies") or [])),
        row("algorithms", ", ".join(w.get("algorithms") or [])),
        "",
        "## Object model", "", object_model(w), "",
        "## State transition diagram", "",
        "```mermaid", state_diagram(w), "```", "",
        "## Research item -- %s" % trace_kind.replace("_", " ").lower(), "",
        "```", trace, "```", "",
    ]

    if conditions:
        md += ["## Conditions", "",
               "| kind | threshold | effect | trigger |", "| --- | --- | --- | --- |"]
        for kind, sent, th, eff in conditions:
            md.append("| %s | %s | %s | %s |"
                      % (kind, th or "--", eff or "--", sent.replace("|", "/")[:220]))
        md.append("")

    if extract:
        md += ["## Source extract", "",
               textwrap.fill(extract[:1200], 96), "",
               "<sub>Wikipedia, CC BY-SA. Retained as evidence for the structural",
               "classification above. Every rule inferred from it is HYPOTHESIZED",
               "until audited against a rulebook.</sub>", ""]
    return "\n".join(md)
