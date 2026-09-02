"""Epistemic tests (mandate section 29: the test comes first).

Each test asserts a distinction that a naive observation-driven model collapses.
A passing suite does not mean the epistemics are right; it means these specific
confusions are ruled out.
"""
from __future__ import annotations

import sys

import core
import epistemic as E
import worlds_epistemic as WE
from worlds_epistemic import DESTROYED, NOT_VISIBLE, UNKNOWN

RESULTS = []


def t(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print("  %-52s %s  %s" % (name, "PASS" if ok else "FAIL", detail))
    return bool(ok)


def drive(world, declare=None, sensor_forced=None):
    """Advance a ball world, waiting until a declaration is legal.

    `declare` is only offered at the horizon, so a driver that fires it
    immediately gets IllegalAction -- which is the world behaving correctly.
    """
    st = world.new_initial_state(None)
    forced = list(sensor_forced or [])
    while not st.is_terminal():
        if st.current_player() == core.CHANCE:
            outs = st.chance_outcomes()
            pick = outs[0][0]
            if st._pending == "sense" and forced:
                want = forced.pop(0)
                for a, _ in outs:
                    if a[1] == want:
                        pick = a
                        break
            st.apply_action(pick)
        else:
            legal = st.legal_actions(0)
            want = ("declare", declare)
            a = want if (declare is not None and want in legal) else legal[0]
            st.apply_action(a, player=0)
    return st


def main():
    print("=" * 78)
    print("EPISTEMIC TEST SUITE")
    print("=" * 78)

    # ---------------------------------------------------------------
    print("\n[1] OCCLUSION IS NOT DESTRUCTION")
    w = WE.E0_occlusion()               # ball starts AT the occluded position
    st = w.new_initial_state(None)
    while st.current_player() == core.CHANCE and st._pending in ("move", "sense"):
        st.apply_action(st.chance_outcomes()[0][0])
    obs = st.observation(0)
    t("sensor reports NOT_VISIBLE", obs["sensor"] == NOT_VISIBLE,
      "sensor=%r" % obs["sensor"])
    t("ball still EXISTS in ontic state", st.ontic()["ball"] != DESTROYED,
      "ontic ball=%r" % st.ontic()["ball"])
    t("observation does NOT contain the ball's position", "ball" not in obs,
      "obs keys=%s" % sorted(obs))
    iset = WE.ball_information_set(w, [NOT_VISIBLE])
    t("information set excludes DESTROYED when destruction impossible",
      all(c["ball"] != DESTROYED for c in iset),
      "candidates=%s" % sorted({str(c['ball']) for c in iset}))
    t("information set is non-empty (ball did not leave the universe)",
      len(iset) > 0, "n=%d" % len(iset))

    # ---------------------------------------------------------------
    print("\n[2] NOT_VISIBLE IS NOT None, AND NOT ABSENCE")
    t("NOT_VISIBLE is a distinct sentinel, not None", NOT_VISIBLE is not None)
    t("NOT_VISIBLE != DESTROYED", NOT_VISIBLE != DESTROYED)

    # ---------------------------------------------------------------
    print("\n[3] E4: OCCLUSION AND DESTRUCTION BECOME INDISTINGUISHABLE")
    w4 = WE.E4_genuine_removal()
    iset4 = WE.ball_information_set(w4, [NOT_VISIBLE])
    vals = {str(c["ball"]) for c in iset4}
    t("both 'hidden at 2' and 'destroyed' remain possible",
      "2" in vals and DESTROYED in vals, "candidates=%s" % sorted(vals))
    t("truth is therefore UNKNOWABLE from this history", len(vals) > 1,
      "|candidates|=%d" % len(vals))

    # ---------------------------------------------------------------
    print("\n[4] REFUSING TO GUESS IS SCORED AS CORRECT")
    st = drive(w4, declare=UNKNOWN, sensor_forced=[NOT_VISIBLE, NOT_VISIBLE, NOT_VISIBLE])
    t("declaring UNKNOWN when unresolvable scores +1", st.returns() == [1.0],
      "returns=%s declared=%r" % (st.returns(), st.declared))
    st2 = drive(w4, declare=2, sensor_forced=[NOT_VISIBLE, NOT_VISIBLE, NOT_VISIBLE])
    t("a confident guess is NOT rewarded above refusal",
      st2.returns()[0] <= 1.0, "returns=%s" % st2.returns())

    # ---------------------------------------------------------------
    print("\n[5] RESOLVABLE CASES ARE STILL RESOLVED")
    w0 = WE.E0_occlusion()
    st3 = drive(w0, declare=UNKNOWN, sensor_forced=[NOT_VISIBLE, NOT_VISIBLE, NOT_VISIBLE])
    iset0 = WE.ball_information_set(w0, [NOT_VISIBLE, NOT_VISIBLE, NOT_VISIBLE])
    resolvable = len({str(c["ball"]) for c in iset0}) == 1
    t("static+occluded is resolvable by elimination", resolvable,
      "candidates=%s" % sorted({str(c['ball']) for c in iset0}))
    t("UNKNOWN on a RESOLVABLE case scores 0, not 1",
      st3.returns() == [0.0], "returns=%s" % st3.returns())

    # ---------------------------------------------------------------
    print("\n[6] HIDDEN MOTION: BELIEF MOVES WITHOUT OBSERVATION")
    # This test originally asserted only that the two candidate sets DIFFER,
    # and it PASSED because the second set was EMPTY -- a contradiction, not a
    # belief update. A green check that is green for the wrong reason is worse
    # than a red one. It now asserts the actual claim.
    w1 = WE.E1_hidden_motion()
    i1 = WE.ball_information_set(w1, [NOT_VISIBLE])
    v1 = {str(c["ball"]) for c in i1}
    t("after one hidden step the ball is tracked to position 2",
      v1 == {"2"}, "candidates=%s" % sorted(v1))
    t("belief moved although the ball was never observed",
      v1 != {"1"}, "start=1 -> believed %s" % sorted(v1))

    # ---------------------------------------------------------------
    print("\n[6b] CONTRADICTION IS NOT UNCERTAINTY")
    i2 = WE.ball_information_set(w1, [NOT_VISIBLE, NOT_VISIBLE])
    t("an impossible history yields an EMPTY information set",
      len(i2) == 0, "candidates=%s" % sorted({str(c['ball']) for c in i2}))
    st_c = drive(WE.E1_hidden_motion(), declare=UNKNOWN,
                 sensor_forced=[NOT_VISIBLE] * 3)
    t("resolution() reports MODEL_CONTRADICTION, not UNCERTAIN",
      st_c.resolution() == E.CONTRADICTION, st_c.resolution())
    t("UNKNOWN is NOT rewarded on an impossible history",
      st_c.returns() == [0.0], "returns=%s" % st_c.returns())
    st_u = drive(WE.E4_genuine_removal(), declare=UNKNOWN,
                 sensor_forced=[NOT_VISIBLE] * 3)
    t("genuine uncertainty still pays +1",
      st_u.returns() == [1.0] and st_u.resolution() == E.UNCERTAIN,
      "%s %s" % (st_u.resolution(), st_u.returns()))

    # ---------------------------------------------------------------
    print("\n[7] E2: MULTIPLE HYPOTHESES ARE MAINTAINED")
    w2 = WE.E2_multiple_exits()
    i = WE.ball_information_set(w2, [NOT_VISIBLE, NOT_VISIBLE])
    t("random motion under occlusion yields >1 candidate", len(set(
        str(c["ball"]) for c in i)) > 1,
      "candidates=%s" % sorted({str(c['ball']) for c in i}))

    # ---------------------------------------------------------------
    print("\n[8] OBSERVATIONAL EQUIVALENCE (section 17)")
    wk = __import__("worlds").KuhnPoker()
    s1 = wk.new_initial_state(None); s1.apply_action(2); s1.apply_action(0)
    s2 = wk.new_initial_state(None); s2.apply_action(2); s2.apply_action(1)
    verdict, witness = E.observationally_equivalent(wk, [s1, s2], player=0, depth=2)
    t("Kuhn: opponent J vs Q indistinguishable to p0 pre-showdown",
      verdict == "OBSERVATIONALLY_EQUIVALENT",
      "%s witness=%s" % (verdict, witness))

    # ---------------------------------------------------------------
    print("\n[9] INFORMATION-SET API")
    iset = E.InformationState(0, [{"ball": 2}, {"ball": DESTROYED}])
    t("status() distinguishes KNOWN / POSSIBLE / IMPOSSIBLE",
      iset.status(lambda s: s["ball"] == 2) == E.POSSIBLE
      and iset.status(lambda s: True) == E.KNOWN
      and iset.status(lambda s: s["ball"] == 99) == E.IMPOSSIBLE)
    t("entropy_bits is the uniform bound, not a fabricated posterior",
      abs(iset.entropy_bits() - 1.0) < 1e-9, "%.4f bits" % iset.entropy_bits())

    # ---------------------------------------------------------------
    print("\n[10] LAWFUL FORWARD MODEL (section 9, fixes packet-4 F2)")
    lm = E.LawfulModel([s1, s2], player=0)
    t("hidden-info model has >1 root; cannot see true state",
      not lm.is_determined() and len(lm.roots()) == 2,
      "roots=%d" % len(lm.roots()))
    ttt = __import__("worlds").TicTacToe()
    lm2 = E.LawfulModel([ttt.new_initial_state(None)], player=0)
    t("perfect-info model collapses to a single root", lm2.is_determined())

    n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
    print("\n" + "=" * 78)
    print("%d checks, %d pass, %d FAIL" % (len(RESULTS), len(RESULTS) - n_fail, n_fail))
    print("=" * 78)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
