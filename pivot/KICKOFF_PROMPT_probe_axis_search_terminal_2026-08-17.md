# Kickoff Prompt — Axis Search, Terminal Round (with a pre-declared stopping rule)

**Why this file exists.** Three difficulty axes are now measured dead — operand magnitude
(non-monotone, v1), answer-space width (fixed three defects, changed no difficulty), and
compositional depth across nine rungs from 1 to 20 (r = +0.394; a 20-step chain solved 40/40).
Each kill was clean and informative. But the program's documented failure mode is exactly this
shape: instrument work that is always defensible and never terminates. **So this round runs
under a stopping rule declared before the data, not after it** — the same discipline the band
ruling was held to.

**Run order:** Ergon (M1) alone. Charon and Harmonia B are consulted only if the terminal
branch fires (§4 below).

---

## THE PROMPT (paste everything between the rules)

---

You're Ergon @roles/Ergon on M1 — `git pull origin main` first. You are the probe's single
owner (R12). Read `roles/Ergon/TASK_FAMILY_V2_2026-08-17.md` §4 (your own open problem, now
four items narrowed), then `stations/M1_STATUS.md`.

**THIS ROUND IS TERMINAL FOR THE AXIS SEARCH.** Three axes are dead. Two candidates remain
inside the computable-gold arithmetic domain. If neither produces a leveled manifest under the
jointly-ruled band, the conclusion is **not** "try a fourth axis" — it is a finding about the
domain, and §4 tells you exactly what to do with it. Read §4 before you start §1, so the
stopping rule is in hand before any data exists.

### §1 — Candidate A: adversarial near-misses on the PROPERTY

Your own §4.1 negative implies this ordering: since failure does not live in execution length,
try where **recognition** fails. Instances that look like one thing and are another —
Carmichael numbers against primality; a perfect square times a squarefree unit against
perfect-square detection; coprimality that fails only at a large shared prime factor; a
pseudoprime to the tested base. Gold computed, never judged (R1). Balanced by construction,
asserted before write (the June 80/…/14 defect must stay impossible). Difficulty parameter
**measured, not assumed** — the whole reason three axes died is that their effect on accuracy
was hypothesised; measure the rungs you pre-declare, all of them, under Bonferroni per the
joint ruling.

### §2 — Candidate B: multi-constraint satisfaction

If A fails: tasks requiring two or three properties held jointly, so partial reasoning yields a
confidently wrong answer **with a locatable error**. Note this candidate is doubly attractive —
a locatable error is precisely the residue shape the 06-07 training-data survey named as
missing, so it scores on both requirements at once.

### §3 — The requirement that outranks headroom

For whichever family you level, state the **residue-plausibility argument** explicitly:
*for this family, what would a prior failed attempt record that could help the next one?*
If the honest answer is "nothing," the family is wrong for this probe however good its
headroom. Note the sharpened form of this after Charon's through-line (`30a1fa95`): Δ_carry is
interpretable at **D0 alone**, because F-null asks "is this residue for THIS problem?" and only
D0's F-prom is selected by task identity. So the residue-plausibility argument must hold at D0
specifically, and you must say what the ladder measures at D1–D3 now that F-null is
INADMISSIBLE there — a different comparator, a redesign of the strata so selection is
task-specific at every distance, or an honest reduction of the probe's scope to D0 carry plus a
separately-named distance measurement.

### §4 — THE STOPPING RULE (pre-declared; read before §1)

**If both A and B fail to produce a manifest that is IN-BAND under the joint ruling (point
estimate in [0.35,0.60], dispersion term movable-share ≥ 0.30, all pre-declared rungs measured
under Bonferroni), do NOT propose a fourth arithmetic axis.** The finding is then, stated
plainly and committed:

> *This solver has no headroom on computable-gold arithmetic. The probe's task domain is
> wrong, not its difficulty parameter.*

That is a real result about the substrate, and it costs the program nothing to say — the
harness, the assembler, the controls, the analysis path and the wall corpus are all
domain-independent and survive it intact.

On firing, propose (do not unilaterally adopt — it is a domain change, so it goes to the
co-signers and to James) the two domains where this solver is *known* to fail:

1. **Lean-checkable claims.** The in-repo harness (`agents/_shared/proof_search/`,
   `external_deps/mathlib_repl/`, 36 tests green, unconsumed since May 29) gives
   non-model ground truth by certificate rather than by computation — and per the spec's own
   distinction, *computation-checkable ≠ decidable-in-a-theory*, so this is a different
   difficulty regime, not a re-skin of the same one.
2. **The NL-parsing gap.** The forge's composed engine measures 85% on structured input vs
   ~34% on natural language — a 51pp gap that is the largest measured headroom anywhere in
   the program's record. **Conflict on the record:** that family is forge-sourced and
   Hephaestus is the declared-conflicted residue supplier. If this branch is taken, the
   decision is James's and the co-signers', made *before* any extraction — not arrived at by
   elimination. Hephaestus supplies on request and does not grade.

**Third candidate, deliberately NOT in the A→B sequence:** the forge's trap battery
(`agents/hephaestus/src/trap_generator*.py`). It sits under the same conflict as (2) above, so
it is a §4 decision item rather than a §1–§2 default. Do not fall into it by elimination.

### §5 — Constraints

No new architecture (the heredity rule). No spec edits; prereg amendments only where the joint
ruling requires them. Every rung measured and committed — a dial whose effect you did not
measure is the exact defect that killed three axes. Suite green before push. Commit and push
each step; update `stations/M1_STATUS.md` at session end with, at minimum: which candidate was
measured, its rungs, whether §4 fired, and the residue-plausibility argument for whatever
survives.

**One thing to hold onto.** Three axes died this week and each death sharpened the question —
that is the loop working, not the loop failing. The stopping rule exists so the *fourth* death,
if it comes, produces a decision rather than a fifth attempt.

---

*Committed by Hephaestus (M3), 2026-08-17. Supplier-only, non-signing. The stopping rule is
declared before the data on purpose; if it fires, the conflict-bearing branches go to James and
the co-signers, not to me.*
