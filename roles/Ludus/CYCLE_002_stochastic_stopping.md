# LUDUS Cycle 002 — the stochastic-stopping family

**Date:** 2026-08-26. **Seat:** Ludus (Claude Code, Opus 5), M1 / F:\.
**Charter:** v2 §17 — *"LUDUS must determine whether these games actually require the same underlying
reasoning. Perhaps 'push your luck' is a genuine strategic family. Perhaps it conceals several
unrelated computations. Both outcomes are valuable."*
**Status:** first result. **Disposition: the family is REAL but NEARLY EMPTY.**
**Model calls: zero.** **Code:** `ludus/stopworlds.py`, `ludus/stopgate.py`.
**Ledgers:** `ludus/ledgers/cycle002_*.json`.

---

## 1. The affordability finding, first, because it changes what LUDUS can do

This entire cycle is dynamic-programming tables and constructed policies. **No LLM is involved at any
point.** That has three consequences worth stating before any result:

- The §35 cheat ledger is **inert** here. There is nothing to memorise, no game identity to leak, no
  strategy guide to launder, no evaluator to game. Cycle 001 spent four of its eight harness defects
  on the transport and token layers alone; none of those failure modes exists in this cycle.
- The exhausted paid lanes (`project_probe_lanes_and_burn`) **stop being the binding constraint**.
  Charter v2 §26's simulation bootstrap is runnable today, on this machine, for free.
- Both worlds are solved **exactly**, not sampled. Flip 7's core has 8,192 reachable states; Martian
  Dice collapses to 6,176 because the "which symbols have been claimed" mask is redundant with the
  counts — you may only claim a symbol you actually rolled, so a claimed symbol always has count >= 1.
  Optimal play is a table, not an estimate, and every number below is exact arithmetic.

Cycle 001's amendment A1 said the transfer programme was unaffordable because there is no training
loop. `ROLE.md` §3 already retired that. This cycle is the demonstration.

## 2. Rules provenance — the HITL contract, stated up front

Every rule in `ludus/stopworlds.py` is **reconstructed from memory. No rulebook was consulted.** Under
v1 §8's epistemic states every one is `HYPOTHESIZED`, and charter v2 §4 names exactly what that is
for: the operator can cheaply detect fabricated rules, impossible moves and missing mechanics.

**Every verdict in this document is conditional on that audit.** `RULES_AUDIT` in
`ludus/stopworlds.py` is the sheet. The two constants carrying the most weight:

- **Martian Dice: each die has faces tank, ray, ray, human, cow, chicken** — the *doubled ray face*.
  If that is wrong, the ray-vs-tank constraint changes character and §4's result moves.
- **Flip 7: rank r appears r times (rank 0 once), 7 distinct ranks scores +15 and ends the round.**

Two deliberate scope cuts, which are *not* rule claims and must not be read as ones:

- **Flip 7 action and modifier cards are not implemented** (Freeze, Flip Three, Second Chance, and
  the +2/+4/+6/+8/+10/x2 modifiers). Only the number-card core.
- **Both worlds are solitaire.** The stopping computation is isolated from opponent interaction. That
  is the right first cut — §17's claim is about the CONTINUE/STOP decision — and it is a real
  limitation: Incan Gold's entire character is that other players leaving changes your split, and
  Can't Stop is a race.

## 3. GATE-W1 applied to the family, with the criteria fixed first

Pre-registered before the numbers were computed:

- a world is **not measurable at the stopping decision** if the best cheap policy retains >= 0.98 of
  optimal expected value;
- the r0001-comparable bar stays action gap >= 0.20, on **visitation-weighted** states.

Two measures, kept separate because they answer different questions. EV retention is what matters in
a stochastic world — a policy that picks the optimal action 70% of the time while losing 1% of value
has demonstrated nothing a threshold cannot do. Action gap is kept only so cycle 001 and cycle 002
stay comparable.

```
FLIP 7                    exact optimal EV = 18.5652
  policy                       EV   retention   gap(uniform)  gap(visitation)
  always_flip              5.7433      0.3094         0.5718           0.1773
  MYOPIC one-step         18.5494      0.9991         0.1870           0.0024
  threshold_25            18.4061      0.9914         0.1990           0.0505
  threshold_20            18.2451      0.9828         0.2988           0.0853
  count_3                 17.6637      0.9514         0.4067           0.1113
```

**Flip 7 is NOT MEASURABLE at the stopping decision.** The textbook one-step rule — flip iff
`E[gain] > P(bust) * pot` — retains **0.9991** of optimal, losing 0.016 points per round, and picks
the optimal action **99.76%** of the time in states optimal play actually visits.

### 3.1 The two weightings disagree by 78x, and that is cycle 001's lesson recurring

For the myopic rule the uniform action gap is **0.1870** and the visitation-weighted gap is
**0.0024**. Read uniformly, the rule looks wrong nearly a fifth of the time. Weighted by the states
competent play reaches, it is wrong one time in four hundred.

Cycle 001 §5.3 was burned by exactly this: uniform sampling over reachable states over-weighted
positions no competent play visits and inflated a reading from 0.412 to 0.900. The fix was carried
into this cycle's instrument before it was needed, and it fired immediately. Uniform weighting would
have passed Flip 7 through the gate as measurable. It is not.

## 4. The transfer test — charter §22's critical cell

Different surface, candidate-same mechanism. Flip 7 is cards and numbers with a depleting deck.
Martian Dice is thirteen dice, aliens, tanks and livestock. If §17's family is real, **the rule that
retains 0.9991 in Flip 7 should carry into Martian Dice untuned.**

It was transplanted with no tuning whatsoever.

```
MARTIAN DICE              exact optimal EV = 2.0938
  best hand-tuned threshold (claim-most, stop at 3)      1.7822    retention 0.8512
  best fixed dice rule      (claim-most, stop dice<=4)   1.7278    retention 0.8252
  MYOPIC TRANSPLANT from Flip 7 (claim-most)             1.9043    retention 0.9095
  MYOPIC TRANSPLANT with a bad claim rule (score_max)    1.0191    retention 0.4867
```

**The transplant carries.** Untuned, it beats every hand-tuned threshold and every fixed dice rule in
the world it was not designed for. That is a genuine, surface-crossing transfer of an executable
structure, and it is the first one LUDUS has recorded.

## 5. And then the ablation empties it out

The transplant leaves 0.0905 of value on the table in Martian Dice, against 0.0009 in Flip 7 — a
hundredfold difference in residual. Where does that residual live? Martian Dice has **two** decision
axes: which symbol to claim from the roll, and whether to stop. Cross each against its optimal
counterpart:

```
configuration                                              EV    retention
cheap claim (most)  + cheap stop (myopic transplant)   1.9043      0.9095
cheap claim (most)  + OPTIMAL stop                     1.9033      0.9090
OPTIMAL claim       + cheap stop (myopic transplant)   2.0670      0.9872
OPTIMAL claim       + OPTIMAL stop                     2.0938      1.0000

recovered by upgrading ONLY the stop rule :  -0.0005
recovered by upgrading ONLY the claim rule:  +0.0777
total residual to close                   :  +0.0905
```

**86% of the residual lives in the claim axis. The stop axis recovers nothing.**

Paired with a competent claim rule, the transplanted myopic stopper retains **0.9872** — essentially
the same verdict as in Flip 7. Martian Dice's stopping decision is myopically solved too.

*(The −0.0005 is not noise and should not be smoothed over: the "optimal stop" rule is optimal
**given optimal continuation**. Bolted onto a cheap claim rule it is mismatched, and very slightly
worse than the myopic rule that at least evaluates the continuation it will actually get. That is a
real property of swapping one component of a policy for a component optimised against a different
partner, and it is worth remembering the next time an ablation is read as a clean decomposition.)*

## 6. The answer to §17

> **"Push your luck" is a real family, and it is nearly empty.**

Both halves matter and neither should be dropped:

- **Real.** One executable rule — `stop iff P(bust) * pot >= E[immediate gain]` — is optimal-to-within
  0.13% in Flip 7 and optimal-to-within 1.3% in Martian Dice, across a surface gap about as wide as
  the founding corpus offers, with **zero tuning between the two**. That is not a vocabulary
  coincidence and it is not a genre label. It is a transferring computation.
- **Nearly empty.** It accounts for almost none of what makes Martian Dice hard. 86% of that game's
  difficulty is a *set-collection choice under a satisfiability constraint* — which symbol to claim,
  given that rays must finally outnumber tanks and each symbol may be claimed only once. Push-your-luck
  does not name that decision, does not measure it, and does not transfer it.

The genre label groups these games **by their shared easy part**. That is charter §16's prediction
arriving on the first family tested: standard mechanism labels collapse, split, or prove strategically
irrelevant. Here the label survives as a real primitive and is simultaneously demoted from
"the strategic content of these games" to "a small solved component of them".

## 7. r0003, registered

```
r0003  myopic stopping sufficiency
       In a world with an accumulate-or-bank decision, the one-step rule
           STOP  iff  P(bust | continue) * pot  >=  E[gain | continue]
       retains a fraction rho of exactly-optimal expected value.
       rho -> 1 means the stopping axis of that world carries no depth.
```

- **Executable:** `ludus/stopgate.py`; exact policy evaluation, no model, no sampling.
- **First observed:** Flip 7 rho = **0.9991**; Martian Dice rho = **0.9872** (paired with a competent
  claim rule), **0.9095** (paired with the naive claim-most rule).
- **Expected effect:** any world where rho is near 1 cannot carry a reading at its stopping decision,
  whatever its genre label says. It may still be deep on another axis — Martian Dice is the worked
  example of exactly that.
- **Intervention that would kill it:** find a founding world in the §17 list where rho is materially
  below 1 with a competent partner policy on every other axis. Can't Stop is the strongest candidate
  and is named as the next test in §8.
- **Confidence:** moderate, and bounded by §2. Two worlds, both solitaire, both with rules I
  reconstructed from memory, one with its action and modifier cards removed. The result is exact
  arithmetic on a possibly-wrong world.

## 8. What this changes about which world to enter next (charter v2 §46)

1. **Can't Stop is now the decisive next world, and it is a prospective prediction, not a
   preference.** It is the one §17 game whose stop decision is entangled with a second axis the way
   Martian Dice's is — column choice and three runners — but unlike Martian Dice its second axis is
   *spatial and racing*, not set-collection. **Registered before running (§32):** r0003 will show
   rho >= 0.97 in Can't Stop when paired with a competent column-choice rule, and the residual will
   again localise off the stop axis. If rho comes back materially below 0.97, r0003 is wrong and the
   family has real stopping depth after all.
2. **Incan Gold is the control that must be run despite being uninteresting alone.** It is the §17
   game whose entire character is the *opponent* interaction this cycle scoped out. Running it
   solitaire should look like Flip 7; if the multiplayer version's rho drops, that localises the
   depth in the interaction rather than the stopping, which is a different claim than either branch
   of §6.
3. **Stop treating "which axis carries the value" as a footnote and make it the atlas's primary
   field.** §5 is the shape of the result LUDUS should be producing: not "this world is hard" but
   "this world's difficulty is 86% in axis X". A world entry that records only a difficulty score
   would have recorded Martian Dice as measurable and left the reason invisible.
4. **The rules audit blocks promotion, not exploration.** §6's verdict cannot be promoted past
   provisional until the operator checks `RULES_AUDIT` — specifically the doubled ray face. Cycle 003
   may proceed on Can't Stop in parallel; the two do not block each other.

## 9. Answering v2 §46's daily questions

- **What did we think yesterday?** That the transfer programme needed a training loop and could not
  be run (cycle 001, A1), and that authored worlds were the way in (A2).
- **What evidence changed that?** Charter v2 §26, then this cycle: constructed policy ladders plus
  exact DP measure transfer with no learner and no model calls at all.
- **What representation survived?** GATE-W1, and visitation weighting — which fired correctly on its
  first use outside the cycle that motivated it (§3.1).
- **What representation died?** "Push your luck" as a description of what makes these games hard.
- **What shortcut did we discover?** The myopic one-step rule, and it is a *real* shortcut: it is very
  nearly the whole stopping computation in both worlds.
- **What failure became reusable?** Cycle 001's uniform-sampling defect became this cycle's default
  weighting, and it changed a verdict here rather than merely being remembered.
- **What new distinction became executable?** Stop-axis depth vs claim-axis depth, measured by
  ablation rather than asserted (§5).
- **What does the current basis predict?** r0003 §8.1, frozen before Can't Stop is built.
- **Are new worlds becoming easier for the right reason?** Too early — but the first surface-crossing
  transfer LUDUS has recorded is real, untuned, and simultaneously much less important than it looks.
