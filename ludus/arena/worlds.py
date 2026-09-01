"""The first vertical slice: five structurally different executable worlds.

Chosen to BREAK the interface, not to confirm it. Each one stresses a different
assumption, and each has externally known ground truth so W6 verification is
possible rather than aspirational.

  World         Stresses                        Ground truth
  -----------   -----------------------------   ---------------------------
  TicTacToe     baseline; sequential perfect    perfect play draws
                information
  Nim           solved in CLOSED FORM           Sprague-Grundy: XOR of heaps
  Pig           CHANCE nodes; the STOP axis     exact DP value
  RPS           SIMULTANEOUS action             NE value 0, uniform strategy
  KuhnPoker     PRIVATE observation, chance,    NE value -1/18 to player 0
                imperfect information

Rules provenance is recorded per world. Nim, tic-tac-toe and RPS are folk games
with no publisher; Pig follows Neller and Presser's canonical description; Kuhn
poker follows Kuhn (1950). None of these has been audited against a physical
rulebook, so the honest source class is EXPERT_INTERPRETATION at best -- see
each world's `ruleset_source`.
"""
from __future__ import annotations

from core import CHANCE, SIMULTANEOUS, TERMINAL, State, World


# ==========================================================================
# 1. Tic-tac-toe -- the baseline
# ==========================================================================

class TicTacToeState(State):
    def __init__(self, world):
        super().__init__(world)
        self.n = world.params["size"]
        self.board = [None] * (self.n * self.n)
        self.to_move = 0
        self._winner = None
        self._done = False

    def _lines(self):
        n = self.n
        for r in range(n):
            yield [r * n + c for c in range(n)]
        for c in range(n):
            yield [r * n + c for r in range(n)]
        yield [i * n + i for i in range(n)]
        yield [i * n + (n - 1 - i) for i in range(n)]

    def _check(self):
        for line in self._lines():
            v = self.board[line[0]]
            if v is not None and all(self.board[i] == v for i in line):
                self._winner, self._done = v, True
                return
        if all(x is not None for x in self.board):
            self._done = True

    def current_player(self):
        return TERMINAL if self._done else self.to_move

    def legal_actions(self, player=None):
        if self._done:
            return []
        return [i for i, v in enumerate(self.board) if v is None]

    def _apply(self, player, action):
        self.board[action] = player
        self.to_move = 1 - player
        self._check()

    def is_terminal(self):
        return self._done

    def returns(self):
        if self._winner is None:
            return [0.0, 0.0]
        return [1.0, -1.0] if self._winner == 0 else [-1.0, 1.0]

    def public_state(self):
        return {"board": list(self.board), "to_move": self.to_move,
                "done": self._done, "winner": self._winner}

    def observation(self, player):
        return self.public_state()      # perfect information

    def describe_action(self, action):
        return "place at (%d,%d)" % (action // self.n, action % self.n)


class TicTacToe(World):
    name = "TIC_TAC_TOE"
    ruleset_version = "folk-3x3"
    ruleset_source = "COMMUNITY_CONSENSUS"
    num_players = 2
    declared = {"exogenous_process": "NONE", "information": "PERFECT",
                "interaction": "COMPETITIVE", "turn_structure": "STRICT_TURN",
                "loss_shape": "OPPORTUNITY_ONLY", "horizon": "VARIABLE",
                "scoring_shape": "WINNER_TAKE_ALL", "tractability": "EXACT"}

    def default_params(self):
        return {"size": 3}

    def new_initial_state(self, rng):
        return TicTacToeState(self)


# ==========================================================================
# 2. Nim -- solved in closed form, so it can verify the harness
# ==========================================================================

class NimState(State):
    def __init__(self, world):
        super().__init__(world)
        self.heaps = list(world.params["heaps"])
        self.to_move = 0
        self.misere = world.params["misere"]

    def current_player(self):
        return TERMINAL if self.is_terminal() else self.to_move

    def legal_actions(self, player=None):
        if self.is_terminal():
            return []
        return [(h, k) for h, size in enumerate(self.heaps)
                for k in range(1, size + 1)]

    def _apply(self, player, action):
        h, k = action
        self.heaps[h] -= k
        self.to_move = 1 - player

    def is_terminal(self):
        return all(h == 0 for h in self.heaps)

    def returns(self):
        # normal play: the player who takes the last object WINS, so the player
        # now to move has just lost. misere inverts it.
        loser = self.to_move
        winner = 1 - loser
        if self.misere:
            winner, loser = loser, winner
        return [1.0, -1.0] if winner == 0 else [-1.0, 1.0]

    def public_state(self):
        return {"heaps": list(self.heaps), "to_move": self.to_move,
                "misere": self.misere}

    def observation(self, player):
        return self.public_state()

    def describe_action(self, action):
        return "take %d from heap %d" % (action[1], action[0])


class Nim(World):
    name = "NIM"
    ruleset_version = "normal-play"
    ruleset_source = "EXPERT_INTERPRETATION"   # Bouton 1901
    num_players = 2
    declared = {"exogenous_process": "NONE", "information": "PERFECT",
                "interaction": "COMPETITIVE", "turn_structure": "STRICT_TURN",
                "loss_shape": "OPPORTUNITY_ONLY", "horizon": "VARIABLE",
                "scoring_shape": "WINNER_TAKE_ALL", "tractability": "EXACT"}

    def default_params(self):
        return {"heaps": (3, 4, 5), "misere": False}

    def new_initial_state(self, rng):
        return NimState(self)


# ==========================================================================
# 3. Pig -- CHANCE nodes and a live STOP axis
# ==========================================================================

class PigState(State):
    """The bench's r0003 shape in miniature: accumulate or bank, bust on a 1."""

    def __init__(self, world):
        super().__init__(world)
        self.scores = [0, 0]
        self.turn_total = 0
        self.to_move = 0
        self.pending_roll = False    # True => a CHANCE node is due
        self.target = world.params["target"]
        self.sides = world.params["sides"]
        self.bust_face = world.params["bust_face"]

    def current_player(self):
        if self.is_terminal():
            return TERMINAL
        return CHANCE if self.pending_roll else self.to_move

    def legal_actions(self, player=None):
        if self.is_terminal() or self.pending_roll:
            return []
        return ["roll", "hold"]

    def chance_outcomes(self):
        if not self.pending_roll:
            return []
        p = 1.0 / self.sides
        return [(f, p) for f in range(1, self.sides + 1)]

    def _apply(self, player, action):
        if self.pending_roll:                     # resolving the die
            face = action
            self.pending_roll = False
            if face == self.bust_face:
                self.turn_total = 0               # TOTAL_RUIN of the turn pot
                self.to_move = 1 - self.to_move
            else:
                self.turn_total += face
            return
        if action == "roll":
            self.pending_roll = True
        elif action == "hold":
            self.scores[self.to_move] += self.turn_total
            self.turn_total = 0
            self.to_move = 1 - self.to_move

    def is_terminal(self):
        return max(self.scores) >= self.target

    def returns(self):
        if self.scores[0] >= self.target:
            return [1.0, -1.0]
        if self.scores[1] >= self.target:
            return [-1.0, 1.0]
        return [0.0, 0.0]

    def public_state(self):
        return {"scores": list(self.scores), "turn_total": self.turn_total,
                "to_move": self.to_move, "pending_roll": self.pending_roll,
                "target": self.target}

    def observation(self, player):
        return self.public_state()

    def describe_action(self, action):
        return "rolled %s" % action if isinstance(action, int) else str(action)


class Pig(World):
    name = "PIG"
    ruleset_version = "neller-presser"
    ruleset_source = "EXPERT_INTERPRETATION"
    num_players = 2
    declared = {"exogenous_process": "IID", "information": "PERFECT",
                "interaction": "COMPETITIVE", "turn_structure": "STRICT_TURN",
                "loss_shape": "TOTAL_RUIN", "horizon": "RACE_TO_TARGET",
                "scoring_shape": "RACE_POSITION", "tractability": "EXACT_WITH_CUT",
                "live_axes": ["STOP"]}

    def default_params(self):
        return {"target": 100, "sides": 6, "bust_face": 1}

    def new_initial_state(self, rng):
        return PigState(self)


# ==========================================================================
# 4. Rock-paper-scissors -- SIMULTANEOUS action
# ==========================================================================

class RPSState(State):
    BEATS = {("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")}

    def __init__(self, world):
        super().__init__(world)
        self.rounds = world.params["rounds"]
        self.played = 0
        self.score = [0, 0]

    def current_player(self):
        return TERMINAL if self.is_terminal() else SIMULTANEOUS

    def legal_actions(self, player=None):
        if self.is_terminal():
            return []
        return ["rock", "paper", "scissors"]

    def _apply_simultaneous(self, actions):
        a, b = actions[0], actions[1]
        if (a, b) in self.BEATS:
            self.score[0] += 1
        elif (b, a) in self.BEATS:
            self.score[1] += 1
        self.played += 1

    def is_terminal(self):
        return self.played >= self.rounds

    def returns(self):
        d = self.score[0] - self.score[1]
        s = 1.0 if d > 0 else (-1.0 if d < 0 else 0.0)
        return [s, -s]

    def public_state(self):
        return {"played": self.played, "rounds": self.rounds,
                "score": list(self.score)}

    def observation(self, player):
        # each player sees the running score, never the opponent's pending throw
        return self.public_state()


class RockPaperScissors(World):
    name = "ROCK_PAPER_SCISSORS"
    ruleset_version = "folk"
    ruleset_source = "COMMUNITY_CONSENSUS"
    num_players = 2
    declared = {"exogenous_process": "NONE", "information": "SIMULTANEOUS",
                "interaction": "COMPETITIVE", "turn_structure": "SIMULTANEOUS",
                "loss_shape": "OPPORTUNITY_ONLY", "horizon": "FIXED",
                "scoring_shape": "WINNER_TAKE_ALL", "tractability": "EXACT",
                "live_axes": ["COMMIT_BLIND"]}

    def default_params(self):
        return {"rounds": 1}

    def new_initial_state(self, rng):
        return RPSState(self)


# ==========================================================================
# 5. Kuhn poker -- PRIVATE observation, chance, imperfect information
# ==========================================================================

class KuhnState(State):
    """Kuhn (1950). 3-card deck, one card each, one betting round.

    The world that forces observation(player) != public_state(): a player must
    see their own card and never the opponent's.
    """

    def __init__(self, world):
        super().__init__(world)
        self.deck = list(range(world.params["cards"]))   # 0=J 1=Q 2=K
        self.cards = [None, None]
        self.pot = [1, 1]              # antes
        self.bets = []                 # sequence of "check"/"bet"/"call"/"fold"
        self.to_move = 0
        self._done = False
        self._folder = None

    def current_player(self):
        if self._done:
            return TERMINAL
        if any(c is None for c in self.cards):
            return CHANCE
        return self.to_move

    def chance_outcomes(self):
        if not any(c is None for c in self.cards):
            return []
        remaining = [c for c in self.deck if c not in self.cards]
        p = 1.0 / len(remaining)
        return [(c, p) for c in remaining]

    def legal_actions(self, player=None):
        if self._done or any(c is None for c in self.cards):
            return []
        if not self.bets or self.bets == ["check"]:
            return ["check", "bet"]
        return ["fold", "call"]        # facing a bet

    def _apply(self, player, action):
        if any(c is None for c in self.cards):        # dealing
            idx = 0 if self.cards[0] is None else 1
            self.cards[idx] = action
            if all(c is not None for c in self.cards):
                self.to_move = 0
            return
        self.bets.append(action)
        if action == "bet":
            self.pot[player] += 1
        elif action == "call":
            self.pot[player] += 1
            self._done = True
        elif action == "fold":
            self._folder = player
            self._done = True
        elif action == "check":
            if self.bets == ["check", "check"]:
                self._done = True
        self.to_move = 1 - player

    def is_terminal(self):
        return self._done

    def returns(self):
        if not self._done:
            return [0.0, 0.0]
        if self._folder is not None:
            w = 1 - self._folder
            amt = float(self.pot[self._folder])
            return [amt, -amt] if w == 0 else [-amt, amt]
        w = 0 if self.cards[0] > self.cards[1] else 1
        amt = float(min(self.pot))
        return [amt, -amt] if w == 0 else [-amt, amt]

    def public_state(self):
        return {"bets": list(self.bets), "pot": list(self.pot),
                "to_move": self.to_move, "done": self._done,
                "cards_dealt": sum(c is not None for c in self.cards)}

    def observation(self, player):
        o = self.public_state()
        o["my_card"] = self.cards[player]
        # the opponent's card is deliberately absent
        return o

    def describe_action(self, action):
        if isinstance(action, int):
            return "dealt card %s" % "JQK"[action]
        return str(action)


class KuhnPoker(World):
    name = "KUHN_POKER"
    ruleset_version = "kuhn-1950"
    ruleset_source = "EXPERT_INTERPRETATION"
    num_players = 2
    declared = {"exogenous_process": "DEPLETING_DECK",
                "information": "HIDDEN_PRIVATE", "interaction": "COMPETITIVE",
                "turn_structure": "STRICT_TURN", "loss_shape": "PARTIAL_DECAY",
                "horizon": "FIXED", "scoring_shape": "LINEAR_ACCUMULATION",
                "tractability": "EXACT", "live_axes": ["BID", "BLUFF"]}

    def default_params(self):
        return {"cards": 3}

    def new_initial_state(self, rng):
        return KuhnState(self)


REGISTRY = {
    "TIC_TAC_TOE": TicTacToe,
    "NIM": Nim,
    "PIG": Pig,
    "ROCK_PAPER_SCISSORS": RockPaperScissors,
    "KUHN_POKER": KuhnPoker,
}
