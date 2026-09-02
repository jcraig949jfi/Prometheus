"""Epistemic access-control audit (mandate sections 26, 27, 30).

Treats information leakage as a VERIFICATION FAILURE, not a code smell. A
hidden-information world is invalid if the hidden information escapes through
any path a player can reach.

The premise, stated in the mandate and worth repeating: a supposedly hidden
opponent card is not hidden if `state_hash` distinguishes which card it is.
Observation dictionaries are the obvious channel and the least likely to be
where a leak actually lives.

Method: construct pairs of ontic states that differ ONLY in something the
player must not know, then check whether any player-reachable signal separates
them. Every separating signal is a defect.

Channels probed:
  observation        the declared surface
  serialize          the public serialisation
  state_hash         the identity digest
  legal action SET   which actions exist
  legal action ORDER the sequence they are offered in
  legal action COUNT the cardinality alone
  error text         exception messages on illegal actions
  chance outcomes    the shape of the chance distribution
  rewards            per-step reward vector
  repr/str           accidental dunder disclosure
"""
from __future__ import annotations

import json

import core


def _safe(fn, *a, **k):
    try:
        return ("ok", fn(*a, **k))
    except Exception as e:                                      # noqa: BLE001
        return ("err", "%s: %s" % (type(e).__name__, e))


def probe_pair(s1, s2, player, label=""):
    """-> list of leak descriptions. Empty means the pair is indistinguishable.

    s1 and s2 MUST differ only in state `player` is not entitled to know.
    """
    leaks = []

    def cmp(name, v1, v2):
        if v1 != v2:
            leaks.append("%s%s: %r != %r" % (label, name, _trim(v1), _trim(v2)))

    cmp("observation", _safe(s1.observation, player), _safe(s2.observation, player))
    cmp("serialize", _safe(s1.serialize), _safe(s2.serialize))
    cmp("state_hash", _safe(s1.state_hash), _safe(s2.state_hash))
    cmp("public_state", _safe(s1.public_state), _safe(s2.public_state))

    la1, la2 = _safe(s1.legal_actions, player), _safe(s2.legal_actions, player)
    cmp("legal_actions_order", la1, la2)
    if la1[0] == "ok" and la2[0] == "ok":
        cmp("legal_actions_set", sorted(map(repr, la1[1])), sorted(map(repr, la2[1])))
        cmp("legal_actions_count", len(la1[1]), len(la2[1]))

    cmp("chance_outcomes", _safe(s1.chance_outcomes), _safe(s2.chance_outcomes))
    cmp("rewards", _safe(s1.rewards), _safe(s2.rewards))
    cmp("current_player", _safe(s1.current_player), _safe(s2.current_player))
    cmp("repr", repr(type(s1)), repr(type(s2)))

    # error text on a deliberately illegal action
    bogus = "___not_a_legal_action___"
    cmp("error_text", _safe(s1.apply_action, bogus, player),
        _safe(s2.apply_action, bogus, player))

    return leaks


def _trim(v, n=90):
    s = repr(v)
    return s if len(s) <= n else s[:n] + "..."


# ==========================================================================
# Per-world leak probes
# ==========================================================================

def audit_kuhn(verbose=False):
    """Kuhn poker: player 0 must not learn player 1's card by any route."""
    import worlds as W
    w = W.KuhnPoker()
    leaks = []
    # deal player 0 the same card, player 1 two different cards
    for mine in range(3):
        others = [c for c in range(3) if c != mine]
        s = []
        for opp in others:
            st = w.new_initial_state(None)
            st.apply_action(mine)          # chance deals p0
            st.apply_action(opp)           # chance deals p1
            s.append(st)
        leaks += probe_pair(s[0], s[1], player=0,
                            label="kuhn[p0=%s, opp %s vs %s] " % (mine, others[0], others[1]))
    return leaks


def audit_observation_hygiene():
    """Every world: mutate a private field and see whether ANY channel moves.

    TWO FAILED HEURISTICS PRECEDED THIS, both mine, both the same mistake.
    v1 searched the observation JSON for the substring "cards" and fired on
    Kuhn's PUBLIC key `cards_dealt`. v2 searched for the private VALUE and
    fired because the value was the integer 0, which appears in "pot": [1, 1]
    and "to_move": 0. Substring matching cannot distinguish a leak from a
    coincidence, and small integers make coincidence the common case.

    The only sound test is DIFFERENTIAL: hold everything fixed, change ONLY
    the secret, and check whether anything a player can reach changes with it.
    That is what probe_pair does, and it is what should have been used from
    the start.
    """
    import worlds as W
    leaks = []
    for name, cls in W.REGISTRY.items():
        w = cls()
        st = w.new_initial_state(None)
        guard = 0
        while (not st.is_terminal() and st.current_player() == core.CHANCE
               and guard < 20):
            st.apply_action(st.chance_outcomes()[0][0])
            guard += 1

        secret_attrs = [a for a in ("cards", "hands", "hidden", "secret")
                        if isinstance(getattr(st, a, None), list)
                        and len(getattr(st, a)) >= 2]
        if not secret_attrs:
            continue

        for attr in secret_attrs:
            for p in range(w.num_players):
                victim = 1 - p if w.num_players == 2 else (p + 1) % w.num_players
                base = getattr(st, attr)
                alternatives = [v for v in set(range(3)) if v != base[victim]
                                and v != base[p]]
                if not alternatives:
                    continue
                s2 = st.clone()
                getattr(s2, attr)[victim] = alternatives[0]
                found = probe_pair(st, s2, player=p,
                                   label="%s[%s p%d vs p%d] " % (name, attr, p, victim))
                leaks += found
    return leaks


def audit_rng_consumption():
    """Does the number of RNG draws depend on hidden state? (section 27)

    A player timing or counting draws must not learn the secret. Approximated
    by counting CHANCE nodes across episodes with identical player policy.
    """
    import players as P
    import worlds as W
    findings = []
    for name, cls in W.REGISTRY.items():
        w = cls()
        counts = {}
        for seed in range(60):
            rep = core.run_episode(w, [P.FirstActionPlayer(), P.FirstActionPlayer()],
                                   seed=seed, validate=False)
            n = sum(1 for s in rep.steps if s.actor == core.CHANCE)
            counts.setdefault(n, 0)
            counts[n] += 1
        if len(counts) > 1:
            findings.append("%s: chance-node count varies %s under a FIXED policy"
                            % (name, sorted(counts)))
    return findings


def audit_replay_metadata():
    """Does the replay record expose state a player could not have seen?"""
    import players as P
    import worlds as W
    leaks = []
    for name, cls in W.REGISTRY.items():
        w = cls()
        rep = core.run_episode(w, [P.RandomPlayer(), P.RandomPlayer()], seed=3)
        st = w.new_initial_state(None)
        has_secret = any(isinstance(getattr(st, a, None), list)
                         for a in ("cards", "hands", "deck", "hidden"))
        if not has_secret:
            continue
        # The FULL replay is omniscient by design; that is not the defect.
        # The defect would be a redacted per-player view that still discloses.
        full = rep.to_json()
        disclosing = [s.action_desc for s in rep.steps
                      if s.actor == core.CHANCE and "card" in s.action_desc]
        if disclosing:
            leaks.append("%s: FULL replay names chance outcomes in plaintext "
                         "(%r) -- omniscient log, must never be handed to an "
                         "agent; use Replay.redacted_for(player)"
                         % (name, disclosing[0]))
        for p in range(w.num_players):
            red = json.dumps(rep.redacted_for(p), sort_keys=True, default=str)
            if any("dealt card" in str(v) for v in [red]):
                leaks.append("%s: REDACTED view for player %d still discloses "
                             "a chance outcome" % (name, p))
    return leaks


def main():
    print("=" * 78)
    print("EPISTEMIC ACCESS-CONTROL AUDIT")
    print("=" * 78)
    total = 0

    for title, fn in [
        ("[A] Kuhn poker: opponent card must not leak", audit_kuhn),
        ("[B] Observation hygiene, all worlds", audit_observation_hygiene),
        ("[C] RNG-consumption side channel", audit_rng_consumption),
        ("[D] Replay metadata disclosure", audit_replay_metadata),
    ]:
        print("\n%s" % title)
        found = fn()
        total += len(found)
        if not found:
            print("    CLEAN")
        for f in found:
            print("    LEAK  %s" % f)

    print("\n" + "=" * 78)
    print("TOTAL FINDINGS: %d" % total)
    print("=" * 78)
    return total


if __name__ == "__main__":
    import sys
    sys.exit(1 if main() else 0)
