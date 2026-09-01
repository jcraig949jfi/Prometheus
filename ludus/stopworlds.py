"""Cycle 002 — the stochastic-stopping family (charter v2 §17), solved exactly.

Charter v2 §17 nominates Can't Stop, Incan Gold, Martian Dice, Piraten Kapern and
Flip 7 as the first natural family, and asks the question that matters:

    is "push your luck" a genuine strategic family, or does it conceal several
    unrelated computations?

Before that can be asked, cycle 001's gate has to be applied to the family
itself. Cycle 001 killed three authored worlds because a four-line heuristic
played them optimally. If a fixed banking threshold plays these games within a
couple of percent of optimal, the family is the same dead end wearing dice, and
LUDUS should learn that from a DP table rather than from a season of simulators.

Two properties make this cycle cheap and clean:

  * **No model is involved anywhere.** These are DP tables and constructed
    policies. The whole §35 cheat ledger is inert here, and the exhausted paid
    lanes are not a constraint. Compare cycle 001, where every number cost a
    free-lane call and four defects came from the transport layer alone.
  * **Both worlds implemented here are solved EXACTLY**, not sampled. Flip 7's
    core has 2^13 reachable states; Martian Dice collapses to 8,568 because the
    "which symbols have been claimed" mask is redundant with the counts (you may
    only claim a symbol you actually rolled, so a claimed symbol always has
    count >= 1). Optimal play is a table, not an estimate.

SOLITAIRE SCOPE — stated, not hidden. Both are implemented single-player: the
stopping computation is isolated from opponent interaction. That is deliberate
for a first cut (it is the CONTINUE/STOP decision that §17 claims is shared) and
it is a real limitation: Incan Gold's whole character is that other players
leaving changes your split, and Can't Stop is a race. Those enter when the family
question has been asked of the isolated computation first.

RULE PROVENANCE — every rule below is reconstructed from memory, NOT from a
verified rulebook, and is therefore `HYPOTHESIZED` in the v1 §8 sense. Charter v2
§4 says exactly what this is for: the operator can cheaply detect fabricated
rules, impossible moves and missing mechanics. `RULES_AUDIT` at the bottom of
this file is the sheet for that check, and every verdict this cycle produces is
conditional on it.
"""
from __future__ import annotations

import functools
import itertools
import json
import math
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ludus" / "ledgers"


# ==========================================================================
# FLIP 7 (number-card core)
# ==========================================================================

#: Rank r appears r times, except rank 0 which appears once. 1 + (1+..+12) = 79.
F7_COUNTS = {0: 1, **{r: r for r in range(1, 13)}}
F7_TOTAL = sum(F7_COUNTS.values())
F7_BONUS = 15
F7_BONUS_AT = 7


class Flip7:
    """Solitaire Flip 7, number cards only.

    State is the SET of ranks already collected. That is sufficient: each rank is
    held at most once (a second copy busts you), so the remaining deck is a
    function of the collected set. 2^13 = 8192 states, exactly solvable.
    """

    name = "FLIP7"
    surface = "cards, numbers, a deck that depletes"

    def initial(self) -> frozenset:
        return frozenset()

    def pot(self, s: frozenset) -> int:
        return sum(s)

    def terminal(self, s: frozenset) -> bool:
        return len(s) >= F7_BONUS_AT

    def outcomes(self, s: frozenset):
        """(probability, next_state_or_None, immediate_score_if_terminal).

        next_state None means BUST -- the whole pot is lost.
        """
        remaining = F7_TOTAL - len(s)
        if remaining <= 0:
            return []
        out = []
        bust = sum(F7_COUNTS[r] - 1 for r in s)
        if bust:
            out.append((bust / remaining, None, 0))
        for r, c in F7_COUNTS.items():
            if r in s:
                continue
            out.append((c / remaining, s | {r}, None))
        return out

    def score_if_stop(self, s: frozenset) -> int:
        return sum(s) + (F7_BONUS if len(s) >= F7_BONUS_AT else 0)


# ==========================================================================
# MARTIAN DICE
# ==========================================================================

#: Faces on each of the 13 dice: one tank, TWO death rays, one each of human,
#: cow, chicken. The doubled ray face is the single most load-bearing constant
#: in this file and the one most worth the operator checking.
MD_DICE = 13
MD_FACE_WEIGHTS = {"tank": 1, "ray": 2, "human": 1, "cow": 1, "chicken": 1}
MD_FACES = ("tank", "ray", "human", "cow", "chicken")
MD_DENOM = sum(MD_FACE_WEIGHTS.values())
MD_CLAIMABLE = ("ray", "human", "cow", "chicken")
MD_SET_BONUS = 3


@functools.lru_cache(maxsize=None)
def _md_roll_dist(n: int):
    """Every (tanks, rays, humans, cows, chickens) roll of n dice, with weight."""
    out = []
    for t in range(n + 1):
        for r in range(n - t + 1):
            for h in range(n - t - r + 1):
                for c in range(n - t - r - h + 1):
                    ch = n - t - r - h - c
                    coeff = math.factorial(n) // (
                        math.factorial(t) * math.factorial(r) * math.factorial(h)
                        * math.factorial(c) * math.factorial(ch))
                    w = (MD_FACE_WEIGHTS["tank"] ** t * MD_FACE_WEIGHTS["ray"] ** r
                         * MD_FACE_WEIGHTS["human"] ** h * MD_FACE_WEIGHTS["cow"] ** c
                         * MD_FACE_WEIGHTS["chicken"] ** ch)
                    out.append(((t, r, h, c, ch), coeff * w / (MD_DENOM ** n)))
    return out


class MartianDice:
    """Solitaire Martian Dice.

    State = (tanks, rays, humans, cows, chickens) set aside. The "already claimed"
    mask is redundant: a symbol can only be claimed if it was rolled, so it is
    claimed exactly when its count is non-zero. 8,568 states, exactly solvable.

    Two decisions per round trip, not one: WHICH symbol to claim from the roll,
    and THEN whether to stop. That makes this world strictly richer than a pure
    stop/continue world -- which is precisely what §17 is asking about.
    """

    name = "MARTIAN_DICE"
    surface = "dice, aliens, tanks and livestock"

    def initial(self):
        return (0, 0, 0, 0, 0)

    def dice_left(self, s) -> int:
        return MD_DICE - sum(s)

    def score_if_stop(self, s) -> int:
        tanks, rays, h, c, ch = s
        if rays < tanks:
            return 0
        base = h + c + ch
        if h >= 1 and c >= 1 and ch >= 1:
            base += MD_SET_BONUS
        return base


# ==========================================================================
# Exact optimal play
# ==========================================================================

def solve_flip7(world: Flip7):
    """V(s) = max(bank now, expected value of one more flip). Exact."""
    memo: dict = {}
    order = sorted((frozenset(c) for k in range(len(F7_COUNTS) + 1)
                    for c in itertools.combinations(F7_COUNTS, k)),
                   key=lambda s: -len(s))
    for s in order:
        if world.terminal(s):
            memo[s] = float(world.score_if_stop(s))
            continue
        ev = 0.0
        for p, nxt, term in world.outcomes(s):
            if nxt is None:
                continue                      # bust contributes 0
            ev += p * (world.score_if_stop(nxt) if world.terminal(nxt) else memo[nxt])
        memo[s] = max(float(world.pot(s)), ev)
    return memo


def flip7_continue_ev(world: Flip7, memo: dict, s: frozenset) -> float:
    ev = 0.0
    for p, nxt, _ in world.outcomes(s):
        if nxt is None:
            continue
        ev += p * (world.score_if_stop(nxt) if world.terminal(nxt) else memo[nxt])
    return ev


def solve_martian(world: MartianDice):
    """V(s) is the value of ABOUT TO ROLL from s. Exact.

    V(s)  = sum over rolls  P(roll) * max over claimable symbols present of W(s')
            ( no claimable symbol present -> the turn busts, value 0 )
    W(s') = score(s')                 if no dice remain
          = max(score(s'), V(s'))     otherwise
    """
    memo: dict = {}

    def W(sp):
        if world.dice_left(sp) == 0:
            return float(world.score_if_stop(sp))
        return max(float(world.score_if_stop(sp)), V(sp))

    def V(s):
        if s in memo:
            return memo[s]
        n = world.dice_left(s)
        if n == 0:
            memo[s] = float(world.score_if_stop(s))
            return memo[s]
        total = 0.0
        for (t, r, h, c, ch), p in _md_roll_dist(n):
            tanks, rays, hh, cc, cch = s
            tanks += t
            best = None
            for sym, got in (("ray", r), ("human", h), ("cow", c), ("chicken", ch)):
                if got == 0:
                    continue
                idx = {"ray": 1, "human": 2, "cow": 3, "chicken": 4}[sym]
                if s[idx] > 0:            # already claimed this symbol
                    continue
                sp = [tanks, rays, hh, cc, cch]
                sp[idx] += got
                v = W(tuple(sp))
                if best is None or v > best:
                    best = v
            total += p * (best if best is not None else 0.0)
        memo[s] = total
        return total

    V(world.initial())
    return memo


RULES_AUDIT = {
    "epistemic_state": "HYPOTHESIZED — reconstructed from memory, no rulebook consulted",
    "why_it_matters": "charter v2 §4: the operator can cheaply detect fabricated "
                      "rules; every cycle-002 verdict is conditional on this sheet",
    "FLIP7": [
        "deck: rank r appears r times for r in 1..12, rank 0 appears once (79 cards)",
        "flipping a rank you already hold BUSTS you; the round scores 0",
        "banking scores the sum of held ranks",
        "holding 7 distinct ranks scores +15 and ends your round immediately",
        "SCOPE CUT (not a rule claim): action cards (Freeze, Flip Three, Second "
        "Chance) and modifier cards (+2/+4/+6/+8/+10/x2) are NOT implemented",
    ],
    "MARTIAN_DICE": [
        "13 dice; each die has faces tank, ray, ray, human, cow, chicken "
        "(the DOUBLED RAY FACE is the highest-leverage constant here)",
        "all tanks rolled are set aside compulsorily",
        "you must then claim ALL dice of exactly one symbol you have not claimed "
        "before this turn; if you cannot, the turn ends scoring 0",
        "after claiming you may stop or reroll the remaining dice",
        "scoring: rays must be >= tanks or the turn scores 0; otherwise score is "
        "humans + cows + chickens",
        "+3 bonus for holding at least one human AND one cow AND one chicken",
    ],
    "SOLITAIRE_SCOPE": "both worlds are single-player; opponent interaction "
                       "(Incan Gold's splitting, Can't Stop's race) is out of "
                       "scope for this cut and is stated as a limitation",
}


def main() -> None:
    LEDGER.mkdir(parents=True, exist_ok=True)
    f7, md = Flip7(), MartianDice()
    m7 = solve_flip7(f7)
    mm = solve_martian(md)
    out = {
        "purpose": "exact optimal play for two founding stochastic-stopping worlds",
        "no_model_calls": True,
        "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "FLIP7": {"states_solved": len(m7),
                  "optimal_ev_per_round": round(m7[f7.initial()], 4)},
        "MARTIAN_DICE": {"states_solved": len(mm),
                         "optimal_ev_per_turn": round(mm[md.initial()], 4)},
        "rules_audit": RULES_AUDIT,
    }
    print(json.dumps({k: v for k, v in out.items() if k != "rules_audit"}, indent=2))
    (LEDGER / "cycle002_exact_solutions.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", LEDGER / "cycle002_exact_solutions.json")


if __name__ == "__main__":
    main()
