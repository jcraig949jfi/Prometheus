"""LUDUS ARENA -- a universal world/player interface.

This is the execution layer. `ludus/atlas_of_worlds` catalogues what games
exist; this makes a small number of them RUN, under one interface, with
deterministic replay and verifiable invariants.

DESIGN NOTE ON WHERE THIS SHAPE CAME FROM. The mandate's candidate interface
was sequential: ApplyAction(player_id, action). Three of the five worlds in the
first slice break that immediately, and the breakage is the point:

  Pig                   the die roll is not any player's action
  Rock-paper-scissors   both players act at the same instant
  Kuhn poker            what a player may observe is not the public state

So `current_player()` returns one of a real player id, CHANCE, or SIMULTANEOUS,
and the caller dispatches. That is the same resolution OpenSpiel reached, and
converging on it independently is a mild point in its favour -- it also means an
OpenSpiel adapter (mandate section 5, independent cross-validation) is a
translation rather than a rewrite.

SEPARATION OF CONCERNS, enforced deliberately (mandate section 8):

    World   rules + parameters. Immutable. Identifies a RulesetVersion.
    State   one episode in progress. Cloneable, hashable, serialisable.
    Player  chooses among legal actions. Never consulted by the environment.

The environment contains objective truth only. `legal_actions()` belongs here;
`find_best_move()` does not, and there is no hook through which a strategy
oracle could be smuggled in. A World cannot call a Player.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

ARENA_VERSION = "0.1.0"

# current_player() sentinels
CHANCE = -1        # the environment resolves an exogenous draw
SIMULTANEOUS = -2  # every non-terminated player acts at once
TERMINAL = -4


class IllegalAction(Exception):
    pass


class InvariantViolation(Exception):
    pass


# ==========================================================================
# World  --  rules + parameters, immutable
# ==========================================================================

class World:
    """A ruleset at a specific version, with its parameters bound.

    `params` is the mandate's section 7 distinction made concrete: what
    identifies the GAME lives in the class and `ruleset_version`; what
    identifies THIS INSTANCE lives in `params`. Two Worlds differing only in
    params are counterfactual neighbours, which is what one-axis perturbation
    testing needs.
    """

    name = "UNNAMED"
    ruleset_version = "0.0"
    ruleset_source = "MACHINE_INFERENCE"   # see atlas provenance vocabulary
    num_players = 2
    # declared structure, mirroring the atlas vocabulary so the two layers join
    declared = {}

    def __init__(self, **params):
        self.params = dict(self.default_params())
        unknown = set(params) - set(self.params)
        if unknown:
            raise ValueError("%s: unknown params %s" % (self.name, sorted(unknown)))
        self.params.update(params)

    def default_params(self):
        return {}

    def new_initial_state(self, rng):
        raise NotImplementedError

    def spec(self):
        return {
            "name": self.name,
            "ruleset_version": self.ruleset_version,
            "ruleset_source": self.ruleset_source,
            "num_players": self.num_players,
            "params": dict(self.params),
            "declared": dict(self.declared),
            "arena_version": ARENA_VERSION,
        }

    def spec_hash(self):
        return hashlib.sha256(
            json.dumps(self.spec(), sort_keys=True).encode()).hexdigest()[:16]

    def __repr__(self):
        p = ",".join("%s=%s" % kv for kv in sorted(self.params.items()))
        return "%s[%s]" % (self.name, p)


# ==========================================================================
# State  --  one episode in progress
# ==========================================================================

class State:
    """Subclasses implement the methods marked REQUIRED."""

    def __init__(self, world):
        self.world = world
        self._history = []

    # -- REQUIRED -----------------------------------------------------
    def current_player(self):
        """-> player id, or CHANCE, or SIMULTANEOUS, or TERMINAL."""
        raise NotImplementedError

    def legal_actions(self, player=None):
        raise NotImplementedError

    def _apply(self, player, action):
        raise NotImplementedError

    def is_terminal(self):
        raise NotImplementedError

    def returns(self):
        """Per-player payoff. Defined only at terminal states."""
        raise NotImplementedError

    def public_state(self):
        raise NotImplementedError

    def observation(self, player):
        """What THIS player may see. Must not leak private state."""
        raise NotImplementedError

    # -- chance -------------------------------------------------------
    def chance_outcomes(self):
        """-> [(action, probability)]. Only when current_player() is CHANCE."""
        return []

    # -- optional -----------------------------------------------------
    def describe_action(self, action):
        return str(action)

    def rewards(self):
        """Per-step reward. Default: zero until terminal, then returns()."""
        n = self.world.num_players
        return list(self.returns()) if self.is_terminal() else [0.0] * n

    # -- provided -----------------------------------------------------
    def apply_action(self, action, player=None):
        cur = self.current_player()
        if cur == SIMULTANEOUS:
            raise IllegalAction("%s is simultaneous; use apply_actions()" % self.world.name)
        if self.is_terminal():
            raise IllegalAction("episode already terminal")
        actor = cur if player is None else player
        if cur != CHANCE:
            legal = self.legal_actions(actor)
            if action not in legal:
                raise IllegalAction("%r not legal for player %s; legal=%r"
                                    % (action, actor, legal))
        self._apply(actor, action)
        self._history.append((actor, action))

    def apply_actions(self, actions):
        """actions: {player_id: action}. Only for SIMULTANEOUS states."""
        if self.current_player() != SIMULTANEOUS:
            raise IllegalAction("%s is not simultaneous here" % self.world.name)
        for p, a in actions.items():
            legal = self.legal_actions(p)
            if a not in legal:
                raise IllegalAction("%r not legal for player %s; legal=%r"
                                    % (a, p, legal))
        self._apply_simultaneous(actions)
        self._history.append((SIMULTANEOUS, tuple(sorted(actions.items()))))

    def _apply_simultaneous(self, actions):
        raise NotImplementedError("%s declared SIMULTANEOUS but did not implement"
                                  % self.world.name)

    def history(self):
        return list(self._history)

    def serialize(self):
        return json.dumps(self.public_state(), sort_keys=True, default=str)

    def state_hash(self):
        return hashlib.sha256(self.serialize().encode()).hexdigest()[:16]

    def clone(self):
        import copy
        return copy.deepcopy(self)

    def validate(self):
        """-> list of invariant violations. Empty list means the state is sane.

        These are the checks the mandate's W6 rung asks for, applied at every
        step of every episode rather than once at the end.
        """
        errs = []
        term = self.is_terminal()
        cur = self.current_player()

        if term:
            if cur != TERMINAL:
                errs.append("terminal state reports current_player=%r" % cur)
            r = self.returns()
            if len(r) != self.world.num_players:
                errs.append("returns() has %d entries, expected %d"
                            % (len(r), self.world.num_players))
            if any(not isinstance(x, (int, float)) for x in r):
                errs.append("returns() contains non-numeric: %r" % (r,))
        else:
            if cur == TERMINAL:
                errs.append("non-terminal state reports TERMINAL")
            if cur == CHANCE:
                out = self.chance_outcomes()
                if not out:
                    errs.append("CHANCE node with no outcomes")
                else:
                    tot = sum(p for _, p in out)
                    if abs(tot - 1.0) > 1e-9:
                        errs.append("chance probabilities sum to %.12f, not 1" % tot)
                    if any(p < 0 for _, p in out):
                        errs.append("negative chance probability")
            elif cur == SIMULTANEOUS:
                for p in range(self.world.num_players):
                    if not self.legal_actions(p):
                        errs.append("simultaneous state: player %d has no legal actions" % p)
            else:
                if not self.legal_actions(cur):
                    errs.append("player %r to move with no legal actions" % cur)

        # observation must not be the private state of another player
        try:
            for p in range(self.world.num_players):
                self.observation(p)
        except Exception as e:                                  # noqa: BLE001
            errs.append("observation(%d) raised %s: %s" % (p, type(e).__name__, e))
        return errs


# ==========================================================================
# Player protocol
# ==========================================================================

class Player:
    """A world must be swappable without touching the player, and vice versa."""

    name = "player"

    def initialize(self, world_spec, player_id, rng):
        self.world_spec = world_spec
        self.player_id = player_id
        self.rng = rng

    def act(self, observation, legal_actions, time_budget=None):
        raise NotImplementedError

    def receive_outcome(self, outcome):
        pass


# ==========================================================================
# Episode runner + replay
# ==========================================================================

@dataclass
class Step:
    t: int
    actor: object                 # player id, CHANCE, or SIMULTANEOUS
    state_hash_before: str
    legal_actions: object
    action: object
    action_desc: str
    observations: dict            # {player_id: observation shown}
    state_hash_after: str
    rewards: list
    elapsed_ms: float


@dataclass
class Replay:
    world: str
    world_spec: dict
    spec_hash: str
    seed: int
    players: list
    steps: list = field(default_factory=list)
    returns: list = field(default_factory=list)
    violations: list = field(default_factory=list)
    terminated: bool = False
    n_steps: int = 0

    def _payload(self, timing):
        step = lambda s: {                                      # noqa: E731
            "t": s.t, "actor": s.actor, "before": s.state_hash_before,
            "legal": s.legal_actions, "action": s.action,
            "desc": s.action_desc, "after": s.state_hash_after,
            "rewards": s.rewards,
            **({"ms": round(s.elapsed_ms, 4)} if timing else {}),
        }
        return {
            "world": self.world, "spec_hash": self.spec_hash,
            "world_spec": self.world_spec, "seed": self.seed,
            "players": self.players, "returns": self.returns,
            "violations": self.violations, "terminated": self.terminated,
            "n_steps": self.n_steps,
            "steps": [step(s) for s in self.steps],
        }

    def to_json(self):
        """Full record INCLUDING timing -- for observability (mandate 18)."""
        return json.dumps(self._payload(timing=True), sort_keys=True, default=str)

    def redacted_for(self, player, observed_steps=None):
        """The replay as ONE PLAYER could lawfully have seen it.

        The full replay is an omniscient record: it names chance outcomes in
        plaintext, so a Kuhn episode literally contains "chance:dealt card K".
        That is correct for an experimenter's log and a disclosure channel the
        moment a replay is handed to an agent -- which mandate section 26 names
        explicitly as a path to test.

        This view removes what `player` never observed: chance outcomes are
        reduced to the fact that a draw occurred, other players' actions keep
        their action but lose any privileged description, and per-step reward
        vectors are narrowed to this player's entry.
        """
        out = []
        for s in self.steps:
            row = {"t": s.t, "actor": s.actor}
            if s.actor == CHANCE:
                row["action"] = "<chance>"
                row["desc"] = "a chance event occurred"
            elif s.actor == SIMULTANEOUS:
                row["action"] = "<simultaneous>"
                row["desc"] = "all players acted"
            else:
                row["action"] = s.action
                row["desc"] = s.action_desc if s.actor == player else "<opponent action>"
            row["reward"] = (s.rewards[player]
                             if isinstance(s.rewards, list)
                             and player < len(s.rewards) else None)
            out.append(row)
        return {"world": self.world, "player": player, "seed": "<withheld>",
                "n_steps": self.n_steps, "terminated": self.terminated,
                "my_return": (self.returns[player] if self.returns else None),
                "steps": out}

    def digest(self):
        """Replay IDENTITY, excluding wall-clock timing.

        Instrumentation is not identity. The first determinism check failed on
        all five worlds purely because `elapsed_ms` sat inside the compared
        payload: actions, state hashes and returns were bit-identical across
        runs, and only the microsecond timings differed. Anything that is
        legitimately non-deterministic -- timing, host, process id -- must be
        recorded but kept out of the thing that answers 'is this the same
        episode?'.
        """
        return hashlib.sha256(
            json.dumps(self._payload(timing=False), sort_keys=True,
                       default=str).encode()).hexdigest()


def run_episode(world, players, seed, max_steps=10_000, validate=True,
                record_observations=False):
    """Run one fully instrumented, deterministic episode.

    Determinism contract: the same (world.spec(), seed, player classes and their
    seeds) must reproduce the same replay exactly. Chance is drawn from the
    episode RNG, never from global random state.
    """
    import random as _random
    rng = _random.Random(seed)
    state = world.new_initial_state(rng)

    for pid, pl in enumerate(players):
        pl.initialize(world.spec(), pid, _random.Random(seed * 1000 + pid))

    rep = Replay(world=world.name, world_spec=world.spec(),
                 spec_hash=world.spec_hash(), seed=seed,
                 players=[p.name for p in players])

    t = 0
    while not state.is_terminal() and t < max_steps:
        if validate:
            rep.violations.extend("t=%d %s" % (t, e) for e in state.validate())

        before = state.state_hash()
        cur = state.current_player()
        t0 = time.perf_counter()
        obs = {}

        if cur == CHANCE:
            outs = state.chance_outcomes()
            r = rng.random()
            acc, chosen = 0.0, outs[-1][0]
            for a, p in outs:
                acc += p
                if r <= acc:
                    chosen = a
                    break
            legal = [a for a, _ in outs]
            state.apply_action(chosen)
            action, desc = chosen, "chance:%s" % state.describe_action(chosen)

        elif cur == SIMULTANEOUS:
            acts = {}
            for pid, pl in enumerate(players):
                la = state.legal_actions(pid)
                o = state.observation(pid)
                if record_observations:
                    obs[pid] = o
                acts[pid] = pl.act(o, la)
            legal = {pid: state.legal_actions(pid) for pid in range(len(players))}
            state.apply_actions(acts)
            action = tuple(sorted(acts.items()))
            desc = "simultaneous:%s" % (action,)

        else:
            legal = state.legal_actions(cur)
            o = state.observation(cur)
            if record_observations:
                obs[cur] = o
            action = players[cur].act(o, legal)
            state.apply_action(action, player=cur)
            desc = state.describe_action(action)

        elapsed = (time.perf_counter() - t0) * 1000.0
        rep.steps.append(Step(
            t=t, actor=cur, state_hash_before=before, legal_actions=legal,
            action=action, action_desc=desc, observations=obs,
            state_hash_after=state.state_hash(), rewards=state.rewards(),
            elapsed_ms=elapsed))
        t += 1

    rep.terminated = state.is_terminal()
    rep.n_steps = t
    if not rep.terminated:
        rep.violations.append("did not terminate within %d steps" % max_steps)
    else:
        if validate:
            rep.violations.extend("terminal %s" % e for e in state.validate())
        rep.returns = list(state.returns())
        for pid, pl in enumerate(players):
            pl.receive_outcome({"returns": rep.returns, "my_return": rep.returns[pid]})
    return rep
