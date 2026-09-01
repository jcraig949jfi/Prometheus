"""W6 verification: run seeded episodes, check invariants, compare against
externally known ground truth.

The mandate's readiness ladder says a simulator is not a verified game. This is
the difference. Every world in the slice has a result that is known independently
of this code, and the harness must reproduce it:

  TIC_TAC_TOE   perfect play draws                     minimax value == 0
  NIM           Bouton: XOR of heap sizes              optimal never loses a
                                                       won position
  PIG           the die is fair and the bust rule       hold-at-25 beats
                forfeits the turn pot                  hold-at-1 decisively
  RPS           uniform is a Nash equilibrium          value ~ 0 under random
  KUHN_POKER    Kuhn (1950): game value -1/18          NE pair yields -1/18

A green run is not proof the rules are right; it is proof that IF the rules are
right, the machinery does not corrupt them. Rule correctness is a separate gate
(W3) and none of these worlds has passed it.
"""
from __future__ import annotations

import statistics
import sys

import core
import players as P
import worlds as W
from core import run_episode


def sweep(world, plist, n=400, seed0=0, validate=True):
    """-> (mean_return_p0, violations, n_steps_mean, unterminated)"""
    rets, viols, steps, dead = [], [], [], 0
    for i in range(n):
        rep = run_episode(world, plist, seed=seed0 + i, validate=validate)
        if not rep.terminated:
            dead += 1
        else:
            rets.append(rep.returns[0])
        viols.extend(rep.violations)
        steps.append(rep.n_steps)
    return (statistics.fmean(rets) if rets else float("nan"),
            viols, statistics.fmean(steps), dead)


def check(label, ok, detail=""):
    print("  %-46s %s  %s" % (label, "PASS" if ok else "FAIL", detail))
    return bool(ok)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    allok = True
    print("=" * 78)
    print("ARENA W6 VERIFICATION   (%d episodes per cell, arena %s)"
          % (n, core.ARENA_VERSION))
    print("=" * 78)

    # ---------------------------------------------------------------- invariants
    print("\n[1] INVARIANTS -- random play, every world")
    for name, cls in W.REGISTRY.items():
        w = cls()
        mean, viols, msteps, dead = sweep(w, [P.RandomPlayer(), P.RandomPlayer()], n)
        allok &= check("%s: no violations, all terminate" % name,
                       not viols and dead == 0,
                       "steps~%.1f mean_p0=%+.3f%s" % (
                           msteps, mean,
                           "" if not viols else "  FIRST=%s" % viols[0]))

    # ---------------------------------------------------------------- determinism
    print("\n[2] DETERMINISM -- same seed reproduces the same replay")
    for name, cls in W.REGISTRY.items():
        w = cls()
        a = run_episode(w, [P.RandomPlayer(), P.RandomPlayer()], seed=12345)
        b = run_episode(w, [P.RandomPlayer(), P.RandomPlayer()], seed=12345)
        allok &= check("%s: replay digest identical" % name, a.digest() == b.digest(),
                       a.digest()[:16])

    # ---------------------------------------------------------------- tic-tac-toe
    print("\n[3] TIC_TAC_TOE -- perfect play must draw")
    ttt = W.TicTacToe()
    mm0, mm1 = P.MinimaxPlayer(), P.MinimaxPlayer()
    st_holder = {}

    def runner():
        return st_holder["s"]
    mm0.set_state_source(runner)
    mm1.set_state_source(runner)

    # minimax needs the live state; drive the loop by hand
    draws = 0
    for s in range(20):
        w = W.TicTacToe()
        state = w.new_initial_state(None)
        st_holder["s"] = state
        for pl, pid in ((mm0, 0), (mm1, 1)):
            pl.initialize(w.spec(), pid, __import__("random").Random(s))
        while not state.is_terminal():
            cur = state.current_player()
            act = (mm0 if cur == 0 else mm1).act(state.observation(cur),
                                                 state.legal_actions(cur))
            state.apply_action(act, player=cur)
            st_holder["s"] = state
        if state.returns() == [0.0, 0.0]:
            draws += 1
    allok &= check("minimax vs minimax always draws", draws == 20,
                   "%d/20 draws" % draws)

    # ---------------------------------------------------------------- nim
    print("\n[4] NIM -- Bouton's XOR theorem")
    w = W.Nim(heaps=(3, 4, 5))
    x = 3 ^ 4 ^ 5
    m, v, _, _ = sweep(w, [P.NimOptimalPlayer(), P.RandomPlayer()], n)
    allok &= check("(3,4,5) XOR=%d nonzero -> p0 optimal always wins" % x,
                   abs(m - 1.0) < 1e-9, "mean_p0=%+.3f" % m)
    w2 = W.Nim(heaps=(1, 2, 3))                       # XOR == 0, a P-position
    m2, _, _, _ = sweep(w2, [P.NimOptimalPlayer(), P.NimOptimalPlayer()], n)
    allok &= check("(1,2,3) XOR=0 -> player to move loses", abs(m2 + 1.0) < 1e-9,
                   "mean_p0=%+.3f" % m2)

    # ---------------------------------------------------------------- pig
    print("\n[5] PIG -- chance nodes and the STOP axis")
    w = W.Pig()
    m, _, msteps, _ = sweep(w, [P.PigHoldAtNPlayer(25), P.PigHoldAtNPlayer(1)],
                            n, seed0=7)
    allok &= check("hold-at-25 beats hold-at-1", m > 0.5,
                   "mean_p0=%+.3f steps~%.0f" % (m, msteps))
    m2, _, _, _ = sweep(w, [P.PigHoldAtNPlayer(25), P.PigHoldAtNPlayer(25)],
                        n, seed0=99)
    allok &= check("mirror match is near-even (first-player edge only)",
                   abs(m2) < 0.35, "mean_p0=%+.3f" % m2)
    # the die must be fair: bust face frequency over many chance draws
    busts = tot = 0
    for i in range(200):
        rep = run_episode(w, [P.PigHoldAtNPlayer(25), P.PigHoldAtNPlayer(25)],
                          seed=1000 + i)
        for s in rep.steps:
            if s.actor == core.CHANCE:
                tot += 1
                busts += 1 if s.action == 1 else 0
    freq = busts / max(tot, 1)
    allok &= check("die is fair: P(bust face) ~ 1/6", abs(freq - 1 / 6) < 0.02,
                   "observed %.4f over %d rolls" % (freq, tot))

    # ---------------------------------------------------------------- rps
    print("\n[6] ROCK_PAPER_SCISSORS -- simultaneous action")
    w = W.RockPaperScissors(rounds=1)
    m, v, _, _ = sweep(w, [P.RandomPlayer(), P.RandomPlayer()], n * 5)
    allok &= check("uniform vs uniform has value ~ 0", abs(m) < 0.08,
                   "mean_p0=%+.4f" % m)
    m2, _, _, _ = sweep(w, [P.FirstActionPlayer(), P.RandomPlayer()], n * 5)
    allok &= check("constant 'rock' vs uniform also ~ 0 (NE is unexploitable)",
                   abs(m2) < 0.08, "mean_p0=%+.4f" % m2)

    # ---------------------------------------------------------------- kuhn
    print("\n[7] KUHN_POKER -- private observation, value -1/18")
    w = W.KuhnPoker()
    # observation hygiene: player 0 must never see player 1's card
    st = w.new_initial_state(None)
    while st.current_player() == core.CHANCE:
        st.apply_action(st.chance_outcomes()[0][0])
    o0, o1 = st.observation(0), st.observation(1)
    leak = (o0.get("my_card") == st.cards[1] and st.cards[0] != st.cards[1]) \
        or "cards" in o0 or any(k for k in o0 if "opponent" in k.lower())
    allok &= check("observation(0) does not expose opponent card", not leak,
                   "o0 keys=%s" % sorted(o0))
    m, v, _, _ = sweep(w, [P.KuhnEquilibriumPlayer(1 / 3.0),
                           P.KuhnEquilibriumPlayer()], 12000, seed0=4242)
    allok &= check("NE pair yields -1/18 = -0.0556", abs(m - (-1 / 18)) < 0.02,
                   "mean_p0=%+.4f (n=12000)" % m)

    print("\n" + "=" * 78)
    print("OVERALL: %s" % ("ALL CHECKS PASS" if allok else "FAILURES PRESENT"))
    print("=" * 78)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
