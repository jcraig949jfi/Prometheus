"""Baseline players. Controls and comparators, not contenders.

The mandate is explicit that LLM players get no privilege here. These are the
calibration instruments: a system beating RandomPlayer has demonstrated almost
nothing, and the only way to know that is to have RandomPlayer's distribution
in hand.

Every player sees ONLY what `observation(player)` returned. None of them can
reach into the state. That is enforced by construction -- `act()` receives the
observation dict and the legal action list, and nothing else.
"""
from __future__ import annotations

from core import Player


class RandomPlayer(Player):
    name = "random"

    def act(self, observation, legal_actions, time_budget=None):
        return self.rng.choice(legal_actions)


class FirstActionPlayer(Player):
    """Null control: reads nothing at all. The floor beneath random."""
    name = "first"

    def act(self, observation, legal_actions, time_budget=None):
        return legal_actions[0]


class NimOptimalPlayer(Player):
    """Bouton's solution: move to a position with heap-XOR zero.

    Present as GROUND TRUTH, not as a contender. If the harness is correct this
    player must never lose from a winning position, and that is a check on the
    arena rather than on the player.
    """
    name = "nim_optimal"

    def act(self, observation, legal_actions, time_budget=None):
        heaps = observation["heaps"]
        x = 0
        for h in heaps:
            x ^= h
        if x != 0:
            for i, h in enumerate(heaps):
                target = h ^ x
                if target < h:
                    return (i, h - target)
        return self.rng.choice(legal_actions)


class PigHoldAtNPlayer(Player):
    """Hold at N: the classic Pig heuristic, and the STOP axis in one line.

    This is the same shape as the bench's r0003 -- bank once the accumulated
    pot passes a threshold -- which is why Pig is in the slice at all.
    """
    name = "pig_hold_at_25"

    def __init__(self, n=25):
        self.n = n
        self.name = "pig_hold_at_%d" % n

    def act(self, observation, legal_actions, time_budget=None):
        if "hold" not in legal_actions:
            return legal_actions[0]
        me = observation["to_move"]
        score = observation["scores"][me]
        turn = observation["turn_total"]
        if score + turn >= observation["target"]:
            return "hold"
        return "hold" if turn >= self.n else "roll"


class KuhnEquilibriumPlayer(Player):
    """A Nash equilibrium strategy for Kuhn poker, parameterised by alpha.

    Kuhn (1950): player 0's equilibria form a one-parameter family with
    alpha in [0, 1/3]; player 1's equilibrium is unique. The game value is
    -1/18 per hand to player 0. Used to VERIFY the implementation: if the
    world is faithful, this pair must produce -1/18 within sampling error.

    Cards: 0=J, 1=Q, 2=K.
    """
    name = "kuhn_nash"

    def __init__(self, alpha=1.0 / 3.0):
        self.alpha = alpha
        self.name = "kuhn_nash_a%.3f" % alpha

    def act(self, observation, legal_actions, time_budget=None):
        card = observation["my_card"]
        bets = observation["bets"]
        a = self.alpha
        p = self.rng.random()

        if self.player_id == 0:
            if not bets:                                   # first decision
                if card == 0:
                    return "bet" if p < a else "check"
                if card == 1:
                    return "check"
                return "bet" if p < 3 * a else "check"
            if bets == ["check", "bet"]:                   # facing a raise
                if card == 0:
                    return "fold"
                if card == 1:
                    return "call" if p < a + 1.0 / 3.0 else "fold"
                return "call"
        else:
            if bets == ["check"]:
                if card == 0:
                    return "bet" if p < 1.0 / 3.0 else "check"
                if card == 1:
                    return "check"
                return "bet"
            if bets == ["bet"]:
                if card == 0:
                    return "fold"
                if card == 1:
                    return "call" if p < 1.0 / 3.0 else "fold"
                return "call"
        return legal_actions[0]


class MinimaxPlayer(Player):
    """Exact minimax with memoisation, for small deterministic perfect-info
    worlds. Ground truth for tic-tac-toe (perfect play must draw)."""
    name = "minimax"

    def initialize(self, world_spec, player_id, rng):
        super().initialize(world_spec, player_id, rng)
        self._cache = {}

    def set_state_source(self, state_getter):
        """Minimax needs the STATE, not an observation.

        This is a deliberate and documented violation of the player contract,
        allowed only for a ground-truth oracle. It is the reason MinimaxPlayer
        cannot be used as a comparator against agents that see observations
        only -- it is strictly better informed than the interface permits.
        """
        self._get_state = state_getter

    def act(self, observation, legal_actions, time_budget=None):
        st = self._get_state()
        _, mv = self._search(st, st.current_player())
        return mv if mv is not None else legal_actions[0]

    def _search(self, state, me):
        if state.is_terminal():
            return state.returns()[me], None
        key = (state.state_hash(), me)
        if key in self._cache:
            return self._cache[key]
        cur = state.current_player()
        best, best_mv = (-1e9 if cur == me else 1e9), None
        for a in state.legal_actions(cur):
            nxt = state.clone()
            nxt.apply_action(a, player=cur)
            v, _ = self._search(nxt, me)
            if cur == me:
                if v > best:
                    best, best_mv = v, a
            else:
                if v < best:
                    best, best_mv = v, a
        self._cache[key] = (best, best_mv)
        return best, best_mv
