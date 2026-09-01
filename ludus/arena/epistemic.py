"""The epistemic layer: existence, visibility, knowledge, and their failures.

THE OPERATING DISTINCTION (mandate section 34), which every name here serves:

    THE UNIVERSE           ontic state -- what is true
    THE PLAYER'S VIEW      observation -- what it is permitted to perceive
    THE PLAYER'S MODEL     information state -- what it can conclude

An object leaving a player's view has not left the universe. A card a player
cannot see still exists. `None` in an observation must never be read as
"absent from the world", and this module exists so that the difference has
somewhere to live.

WHAT THIS MODULE DOES NOT DO. It does not implement modal logic, exact belief
distributions over large state spaces, or higher-order knowledge beyond what a
concrete world has forced. Mandate section 11 is explicit that the schema must
not prohibit K_i(K_j(X)) while also not building an engine for it speculatively.
"""
from __future__ import annotations

import itertools


# ==========================================================================
# Information taxonomy (mandate section 4)
# ==========================================================================

INFORMATION_CLASSES = [
    "FULLY_OBSERVABLE",       # all strategically relevant state is visible
    "PRIVATE",                # exists, directly known to some players only
    "OCCLUDED",               # exists, temporarily inaccessible by geometry
    "LATENT",                 # affects outcomes, never directly observed
    "STALE",                  # observed once; the world may have moved since
    "FORGOTTEN",              # was made available; the AGENT failed to retain
    "NOISY",                  # observation probabilistically corrupted
    "PARTIAL",                # a coarsening or subset of the truth
    "DELAYED",                # becomes observable only later
    "CENSORED",               # rules forbid transmission
    "MANIPULATED",            # another agent chooses what to reveal or fake
    "DESTROYED",              # unrecoverable from any accessible future state
    "UNKNOWN_EXISTENCE",      # the agent does not know the variable exists
]

# FORGOTTEN is deliberately separated from OCCLUDED and CENSORED. The
# environment must be able to say "this was available and the agent lost it",
# which is a property of the agent, versus "this was never available", which is
# a property of the world. Collapsing them makes memory failure and perception
# failure indistinguishable in the failure taxonomy (section 21).

VISIBILITY = ["PUBLIC", "PRIVATE", "SHARED", "COMMON_KNOWLEDGE", "HIDDEN",
              "DERIVED"]

# Epistemic readiness ladder (mandate section 28). Deliberately orthogonal to
# the W0-W8 execution ladder: a world can run perfectly and still leak.
EPISTEMIC_LADDER = [
    "E0_OBSERVATION_DECLARED",
    "E1_VISIBILITY_AUDITED",
    "E2_LEAKAGE_TESTED",
    "E3_HISTORY_SUFFICIENCY_TESTED",
    "E4_INFORMATION_SET_VALIDATED",
    "E5_INFORMATION_FLOW_VERIFIED",
    "E6_EXTERNAL_CROSS_CHECKED",
    "E7_EPISTEMIC_EXPERIMENT_READY",
]


# ==========================================================================
# Knowledge propositions (mandate section 11)
# ==========================================================================

class Prop:
    """A proposition about the world, e.g. ('ball_at', 'A') or ('card', 2, 'red').

    Kept as a plain tuple wrapper rather than a logic term: worlds have not yet
    forced anything richer, and section 11 warns against building a modal
    engine because it is conceptually attractive.
    """

    __slots__ = ("key",)

    def __init__(self, *key):
        self.key = tuple(key)

    def __eq__(self, o):
        return isinstance(o, Prop) and self.key == o.key

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return "P%s" % (self.key,)


KNOWN, POSSIBLE, IMPOSSIBLE, UNKNOWABLE = "KNOWN", "POSSIBLE", "IMPOSSIBLE", "UNKNOWABLE"
# Resolution states. CONTRADICTION is deliberately NOT a kind of uncertainty.
UNCERTAIN, CONTRADICTION = "UNCERTAIN", "MODEL_CONTRADICTION"


class InformationState:
    """What a player can lawfully conclude, given its history.

    Backed by an explicit set of candidate ontic states -- an INFORMATION SET
    in the classical sense (mandate section 10):

        s1 ~_i s2   iff   O_i(s1) == O_i(s2) and nothing in i's history
                          distinguishes them

    Exact enumeration only. Worlds too large for that must supply a sampled or
    factored implementation and say so; this class will not pretend.
    """

    def __init__(self, player, candidates, history=None, exact=True):
        self.player = player
        self.candidates = list(candidates)
        self.history = list(history or [])
        self.exact = exact

    def __len__(self):
        return len(self.candidates)

    def is_contradiction(self):
        """No ontic state explains the history: the MODEL is wrong.

        This is a third condition, not a flavour of uncertainty, and conflating
        it with uncertainty is a live failure mode rather than a hypothetical.
        In the E1 drift world a forced history of three NOT_VISIBLE readings
        yields an empty candidate set -- the ball must have drifted into an
        unoccluded position and been seen. The scorer read that empty set as
        'more than one answer remains', rewarded a declaration of UNKNOWN with
        +1, and thereby paid an agent for humility about a world that cannot
        exist.

        KNOWN            exactly one candidate
        UNCERTAIN        several candidates
        CONTRADICTION    zero candidates -- the model or the observations are
                         wrong, and no answer about the ball is meaningful
        """
        return len(self.candidates) == 0

    def resolution(self):
        if self.is_contradiction():
            return CONTRADICTION
        return KNOWN if len(self.candidates) == 1 else UNCERTAIN

    def status(self, predicate):
        """KNOWN / POSSIBLE / IMPOSSIBLE for a predicate over ontic states."""
        if not self.candidates:
            return IMPOSSIBLE
        hits = [bool(predicate(s)) for s in self.candidates]
        if all(hits):
            return KNOWN
        if not any(hits):
            return IMPOSSIBLE
        return POSSIBLE

    def knows(self, predicate):
        return self.status(predicate) == KNOWN

    def possible_values(self, extractor):
        """The set of values a hidden variable could take, given what is known."""
        return sorted({extractor(s) for s in self.candidates}, key=repr)

    def entropy_bits(self):
        """log2 of the information-set size: uncertainty under a uniform prior.

        This is NOT H(S|O) under the true posterior. It is the uniform upper
        bound, reported because inventing a prior would violate the fail-closed
        rule against fabricated belief probabilities (mandate section 30).
        """
        import math
        return math.log2(len(self.candidates)) if self.candidates else float("-inf")


def observationally_equivalent(world, states, player, actions=None, depth=1):
    """Are these ontic states distinguishable by player, now or by experiment?

    Implements mandate section 17. Returns (verdict, witness) where verdict is
    'OBSERVATIONALLY_EQUIVALENT' or 'DISTINGUISHABLE', and witness is the
    action sequence that separated them, if any.

    A negative result is bounded by `depth`: it means "no experiment of this
    length distinguishes them", not "nothing ever could". The caller must not
    upgrade that into structural unknowability without saying at what horizon.
    """
    obs = [_obs_key(s, player) for s in states]
    if len(set(obs)) > 1:
        return "DISTINGUISHABLE", ()
    if depth <= 0:
        return "OBSERVATIONALLY_EQUIVALENT", ()

    acts = actions
    if acts is None:
        acts = states[0].legal_actions(player) if not states[0].is_terminal() else []
    for a in acts:
        nxts = []
        ok = True
        for s in states:
            c = s.clone()
            try:
                if c.current_player() == player:
                    c.apply_action(a, player=player)
                else:
                    ok = False
                    break
            except Exception:                                   # noqa: BLE001
                ok = False
                break
            nxts.append(c)
        if not ok or len(nxts) != len(states):
            continue
        if len({_obs_key(n, player) for n in nxts}) > 1:
            return "DISTINGUISHABLE", (a,)
        v, w = observationally_equivalent(world, nxts, player, None, depth - 1)
        if v == "DISTINGUISHABLE":
            return v, (a,) + w
    return "OBSERVATIONALLY_EQUIVALENT", ()


def _obs_key(state, player):
    import json
    try:
        o = state.observation(player)
    except Exception as e:                                      # noqa: BLE001
        return "ERR:%s" % type(e).__name__
    return json.dumps(o, sort_keys=True, default=str)


# ==========================================================================
# Information-flow events (mandate section 13)
# ==========================================================================

class InfoEvent:
    """Who learned what, from where, and whether it is still true."""

    __slots__ = ("t", "observer", "source", "fact", "channel", "reliability",
                 "scope", "still_valid")

    def __init__(self, t, observer, fact, source=None, channel="observation",
                 reliability=1.0, scope="PRIVATE", still_valid=True):
        self.t = t
        self.observer = observer
        self.fact = fact
        self.source = source
        self.channel = channel
        self.reliability = reliability
        self.scope = scope
        self.still_valid = still_valid

    def as_dict(self):
        return {"t": self.t, "observer": self.observer, "fact": repr(self.fact),
                "source": self.source, "channel": self.channel,
                "reliability": self.reliability, "scope": self.scope,
                "still_valid": self.still_valid}

    def __repr__(self):
        return "InfoEvent(t=%s p%s <- %r via %s)" % (
            self.t, self.observer, self.fact, self.channel)


# ==========================================================================
# Lawful forward model (mandate section 9) -- resolves the Minimax defect
# ==========================================================================

class LawfulModel:
    """The only search surface a player is entitled to.

    Packet #4 recorded F2: MinimaxPlayer needed the true state and was therefore
    excluded as a comparator. That was a workaround, not a fix. The fix is this:
    a player searches over the states its information set ADMITS, using publicly
    knowable dynamics, and can never reach the true state except when its own
    information happens to determine it uniquely.

    Under perfect information the information set is a singleton, so this
    reduces exactly to ordinary search -- minimax over one root. Under hidden
    information it is a set, and the player must search all of it. Nothing here
    can consult world truth: the constructor takes candidate states, and the
    caller obtains those from the information set, never from the environment.
    """

    def __init__(self, candidates, player):
        self.candidates = [c.clone() for c in candidates]
        self.player = player

    def roots(self):
        return [c.clone() for c in self.candidates]

    def transition(self, candidate_state, action, player=None):
        """Hypothetical: if the world were HERE and THIS happened, what follows?"""
        nxt = candidate_state.clone()
        p = player if player is not None else nxt.current_player()
        nxt.apply_action(action, player=p)
        return nxt

    def is_determined(self):
        return len(self.candidates) == 1


def build_information_set(world, player, enumerator, observed_key, history=None):
    """Generic exact information set: every ontic state matching the observation.

    `enumerator` yields candidate ontic states; `observed_key` is the player's
    actual observation key. Exhaustive, so only for tiny worlds -- which is
    precisely where mandate section 19 says to start.
    """
    cands = [s for s in enumerator() if _obs_key(s, player) == observed_key]
    return InformationState(player, cands, history=history, exact=True)


def all_assignments(domains):
    """Cartesian product helper for building candidate ontic states."""
    keys = list(domains)
    for combo in itertools.product(*(domains[k] for k in keys)):
        yield dict(zip(keys, combo))
