"""Synthetic epistemic micro-worlds (mandate sections 3, 24).

BALL UNDER COUCH. A ball sits somewhere on a line. Some positions are occluded.
The ball may move, may be moved by someone else, may be destroyed, and the
player's sensor may lie in either direction. At the end the player must SAY
where the ball is -- or say that it cannot be known.

The point is not object permanence. It is that these are seven different
causal facts which a naive observation-driven model collapses into one:

    the ball is at position 3 and I can see it
    the ball is at position 3 and a barrier is in the way
    the ball moved somewhere while I could not see it
    someone moved it while I could not see it
    it was destroyed while I could not see it
    it is visible and my sensor missed it
    my sensor reported it somewhere it is not

Only the first is "observed". None of the others is "absent from the universe",
and `None` in an observation means the SEVENTH thing has not been ruled out --
never that the ball ceased to exist.

SCORING MAKES THE EPISTEMICS PAY. The player declares at the horizon:

    correct location or DESTROYED ........ +1
    "UNKNOWN" when truly unresolvable .... +1   <- refusing to guess is CORRECT
    "UNKNOWN" when it was resolvable ..... 0
    a confident wrong answer ............. -1

Mandate section 16 asks for exactly this: an agent must not fabricate certainty
because an answer was requested, and a correct refusal to collapse uncertainty
counts as success. Guessing between observationally equivalent hypotheses has
negative expected value here, by construction.
"""
from __future__ import annotations

from core import CHANCE, TERMINAL, State, World

DESTROYED = "DESTROYED"
UNKNOWN = "UNKNOWN"
NOT_VISIBLE = "NOT_VISIBLE"     # deliberately NOT None


class BallState(State):
    def __init__(self, world):
        super().__init__(world)
        pr = world.params
        self.n = pr["positions"]
        self.occluded = set(pr["occluded"])
        self.horizon = pr["horizon"]
        self.t = 0
        self.ball = pr["start"]          # int position, or DESTROYED
        self.declared = None
        self.sensor_says = None          # what the player last perceived
        self._pending = "move"           # move -> sense -> act
        self.probe_budget = pr["probe_budget"]

    # -- ontic truth, environment only ---------------------------------
    def ontic(self):
        return {"ball": self.ball, "t": self.t}

    def _visible(self, pos):
        return pos not in self.occluded

    # -- flow ----------------------------------------------------------
    def current_player(self):
        if self.is_terminal():
            return TERMINAL
        if self._pending in ("move", "sense"):
            return CHANCE
        return 0

    def chance_outcomes(self):
        pr = self.world.params
        if self._pending == "move":
            outs = []
            if self.ball == DESTROYED:
                return [(("move", DESTROYED), 1.0)]
            pd = pr["destroy_prob"]
            moves = self._move_targets(self.ball)
            pm = (1.0 - pd) / len(moves)
            if pd > 0:
                outs.append((("move", DESTROYED), pd))
            for m in moves:
                outs.append((("move", m), pm))
            return outs
        # sense
        truth = self.ball
        fn, fp = pr["false_negative"], pr["false_positive"]
        if truth != DESTROYED and self._visible(truth):
            outs = [(("sense", truth), 1.0 - fn), (("sense", NOT_VISIBLE), fn)]
        else:
            outs = [(("sense", NOT_VISIBLE), 1.0 - fp)]
            if fp > 0:
                vis = [p for p in range(self.n) if self._visible(p)]
                for p in vis:
                    outs.append((("sense", p), fp / len(vis)))
        tot = sum(p for _, p in outs)
        return [(a, p / tot) for a, p in outs]

    def _move_targets(self, pos):
        m = self.world.params["motion"]
        if m == "static":
            return [pos]
        if m == "drift":
            return [min(pos + 1, self.n - 1)]
        return sorted({max(0, pos - 1), pos, min(self.n - 1, pos + 1)})

    def legal_actions(self, player=None):
        if self.is_terminal() or self._pending != "act":
            return []
        acts = ["wait"]
        if self.probe_budget > 0:
            acts += [("probe", i) for i in range(self.n)]
        if self.t >= self.horizon - 1:
            acts = [("declare", DESTROYED), ("declare", UNKNOWN)] + \
                   [("declare", i) for i in range(self.n)]
        return acts

    def _apply(self, player, action):
        kind = action[0] if isinstance(action, tuple) else action
        if self._pending == "move":
            self.ball = action[1]
            self._pending = "sense"
            return
        if self._pending == "sense":
            self.sensor_says = action[1]
            self._pending = "act"
            return
        if kind == "wait":
            pass
        elif kind == "probe":
            self.probe_budget -= 1
            self.sensor_says = (self.ball if self.ball == action[1]
                                else ("probe_absent", action[1]))
        elif kind == "declare":
            self.declared = action[1]
        self.t += 1
        self._pending = "move"

    def is_terminal(self):
        return self.declared is not None or self.t >= self.horizon

    def returns(self):
        if self.declared is None:
            return [0.0]
        truth = self.ball
        import epistemic as E
        res = self.resolution()
        if res == E.CONTRADICTION:
            # Score nothing. The episode is evidence about the MODEL, not about
            # the agent, and paying out here would reward or punish an agent
            # for a world that cannot exist. Surfaced via `resolution()` so a
            # harness can quarantine the episode instead of averaging it in.
            return [0.0]
        if self.declared == UNKNOWN:
            return [1.0] if res == E.UNCERTAIN else [0.0]
        return [1.0] if self.declared == truth else [-1.0]

    def resolution(self):
        """KNOWN / UNCERTAIN / MODEL_CONTRADICTION for this episode's history.

        Three-valued on purpose. An EMPTY information set means no ontic
        trajectory explains the observations -- the model is wrong, or the
        readings are impossible -- and that is not a species of not-knowing.
        The first version of this returned a bool, so an impossible history
        fell through to "unresolvable" and a declaration of UNKNOWN was paid
        +1. An agent was being rewarded for humility about a world that
        cannot exist.
        """
        import epistemic as E
        iset = ball_information_set(self.world, self.history_observations())
        vals = {str(c["ball"]) for c in iset}
        if not vals:
            return E.CONTRADICTION
        return E.KNOWN if len(vals) == 1 else E.UNCERTAIN

    def history_observations(self):
        return [a[1] for who, a in self.history()
                if isinstance(a, tuple) and a and a[0] == "sense"]

    # -- views ---------------------------------------------------------
    def public_state(self):
        return {"t": self.t, "n": self.n, "occluded": sorted(self.occluded),
                "horizon": self.horizon, "phase": self._pending,
                "probe_budget": self.probe_budget}

    def observation(self, player):
        o = self.public_state()
        o["sensor"] = self.sensor_says
        o["sensor_history"] = self.history_observations()
        # NOTE what is absent: `ball`. NOT_VISIBLE is a sensor reading, not a
        # statement that the ball does not exist.
        return o

    def describe_action(self, action):
        if isinstance(action, tuple) and action[0] == "sense":
            return ("sensor: not visible" if action[1] == NOT_VISIBLE
                    else "sensor: position %s" % action[1])
        if isinstance(action, tuple) and action[0] == "move":
            return "world: ball -> %s" % action[1]
        return str(action)


class BallUnderCouch(World):
    """Parameterised occlusion laboratory. E0-E6 are parameter settings."""

    name = "BALL_UNDER_COUCH"
    ruleset_version = "synthetic-1"
    ruleset_source = "OFFICIAL_RULE"    # we are the publisher
    num_players = 1
    declared = {"exogenous_process": "IID", "information": "PARTIAL",
                "interaction": "SOLITAIRE", "turn_structure": "PHASE_STRUCTURED",
                "loss_shape": "OPPORTUNITY_ONLY", "horizon": "FIXED",
                "scoring_shape": "LINEAR_ACCUMULATION", "tractability": "EXACT"}

    def default_params(self):
        return {"positions": 4, "occluded": (2,), "start": 1, "horizon": 3,
                "motion": "static", "destroy_prob": 0.0,
                "false_negative": 0.0, "false_positive": 0.0,
                "probe_budget": 0}

    def new_initial_state(self, rng):
        return BallState(self)


# -- named difficulty rungs from the mandate ---------------------------
def E0_occlusion():
    return BallUnderCouch(positions=4, occluded=(2,), start=2, horizon=3,
                          motion="static")


def E1_hidden_motion():
    return BallUnderCouch(positions=4, occluded=(1, 2), start=1, horizon=3,
                          motion="drift")


def E2_multiple_exits():
    return BallUnderCouch(positions=5, occluded=(1, 2, 3), start=2, horizon=3,
                          motion="random")


def E4_genuine_removal():
    return BallUnderCouch(positions=4, occluded=(2,), start=2, horizon=3,
                          motion="static", destroy_prob=0.5)


def E5_noisy():
    return BallUnderCouch(positions=4, occluded=(), start=1, horizon=3,
                          motion="static", false_negative=0.5)


def E6_false_positive():
    return BallUnderCouch(positions=4, occluded=(2,), start=2, horizon=3,
                          motion="static", false_positive=0.5)


# ==========================================================================
# Exact information set over the ball world (mandate sections 10, 16, 17)
# ==========================================================================

def ball_information_set(world, sensor_history):
    """Every ontic trajectory consistent with what the sensor reported.

    Exhaustive forward enumeration. Returns a list of {"ball": final_value},
    which is the player's information set at the horizon. If it has more than
    one distinct entry, the truth is UNKNOWABLE from this history and declaring
    a specific answer is a guess.
    """
    pr = world.params
    n, occ = pr["positions"], set(pr["occluded"])
    live = [(pr["start"],)]
    for reading in sensor_history:
        nxt = []
        for traj in live:
            pos = traj[-1]
            targets = ([DESTROYED] if pos == DESTROYED
                       else _targets(pos, n, pr["motion"]))
            if pos != DESTROYED and pr["destroy_prob"] > 0:
                targets = targets + [DESTROYED]
            for tgt in targets:
                if _sensor_possible(tgt, reading, occ, n, pr):
                    nxt.append(traj + (tgt,))
        live = nxt
    return [{"ball": t[-1]} for t in live]


def _targets(pos, n, motion):
    if motion == "static":
        return [pos]
    if motion == "drift":
        return [min(pos + 1, n - 1)]
    return sorted({max(0, pos - 1), pos, min(n - 1, pos + 1)})


def _sensor_possible(truth, reading, occ, n, pr):
    visible = truth != DESTROYED and truth not in occ
    if reading == NOT_VISIBLE:
        return (not visible) or pr["false_negative"] > 0
    if truth == DESTROYED:
        return pr["false_positive"] > 0
    if reading == truth:
        return visible
    return pr["false_positive"] > 0 and reading not in occ
