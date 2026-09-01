# World backlog — ordered by expected information gain

Charter v2 §41: *"Eventually LUDUS should choose the next game according to expected information gain.
Which world would most strongly distinguish our competing hypotheses?"* This file is that choice,
made explicitly and revised whenever the matrix moves.

**The problem with the bench right now is a monoculture.** All four worlds are push-your-luck. Every
circuit in the registry was written while looking at push-your-luck worlds, and every retention
number was measured in them. Charter §40 is blunt about what that means: *keep breaking whatever
representation currently appears sufficient.* Adding a fifth push-your-luck world would raise the
cell count and teach almost nothing.

So the backlog is ordered by **which world most threatens the current bet** — that transfer is
mediated by declared interfaces rather than by genre — not by which is easiest to build.

---

## 1. FOR SALE — the monoculture breaker (highest priority)

**What it threatens.** A world with a live SELECT axis and **no STOP axis at all**. Right now every
SELECT measurement (`r0010`, `r0012`, `r0014`, `r0011`) comes from Martian Dice and Can't Stop, both
push-your-luck. If SELECT circuits only work when they sit next to a stopping decision, they are not
interface-mediated — they are genre-mediated, and the bet in `ROLE.md` §0 is wrong.

**Prediction to register before building:** `r0012` (one-ply lookahead) retains >= 0.90 and `r0011`
(min-consumption) stays near the bottom, as in Martian Dice. If the ordering of SELECT circuits
*reverses* outside push-your-luck, the interface bet takes real damage.

**Structure.** Two phases: a bidding phase for properties, then a sealed reveal phase selling them
for cheques. The second phase is a pure simultaneous SELECT with no randomness at the point of
decision — a very different shape from claiming dice.

## 2. COLORETTO — the interface-boundary probe

**What it threatens.** `r0003` assumes **death loses the whole pot**. Coloretto's repeated decision
is *draw another card into a row, or take a row* — there is a risk of the row degrading, but there is
no total-loss bust. If the STOP interface only supports circuits when death is total, then the
interface as currently declared is too coarse and needs splitting into
`STOP-with-ruin` and `STOP-with-decay`.

That is the most likely way the current architecture is wrong, which is exactly why it should be
built early rather than late.

## 3. PIRATEN KAPERN — completes charter §17's nominated family

Fifth of the five. Lower information gain than the two above precisely *because* it is more
push-your-luck, but it closes the family §17 named, and its card modifiers give it a per-episode
parameter shift the other four lack.

## 4. CAN'T STOP, FULL GAME — solitaire turn vs the real objective

The bench currently plays one turn from an empty board and values progress as fraction-of-column-
completed. The real game is a race to claim three columns, which makes progress value **non-linear
and opponent-dependent**. A circuit that is optimal for one-turn progress may be badly wrong for the
race. This is the cheapest available test of whether the solitaire scope cut is load-bearing.

## 5. SPLENDOR — a genuinely different genre

Engine building. No stopping decision; a long-horizon SELECT with compounding. Charter §18 warns
against assuming the engine worlds resemble each other. This is where "different surface, different
mechanism" gets its negative control.

---

## Deliberately NOT next

- **More push-your-luck worlds.** The family is characterised; §17's question is answered.
- **Bigger versions of solved worlds.** Scaling Flip 7's deck does not test a new interface.
- **Any world chosen because it is easy to implement.** Ease of implementation is uncorrelated with
  information gain, and following it is how an atlas becomes a collection.

## Standing constraint on all of them

Every world added is `HYPOTHESIZED` until its rules are audited — see
`ludus/bench/RULES_AUDIT.md`. Building proceeds without the audit; **promotion of any claim about a
named commercial game does not.**
