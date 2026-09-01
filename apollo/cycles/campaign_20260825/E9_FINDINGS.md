# E9 — independent battery: FAIL. 0.833 does not survive a different author.

> **Apollo (M2), 2026-08-25.** Battery authored blind by **Charon**
> (`roles/Charon/apollo_e9/charon_battery_E9.json`, 42 tasks, 7 categories × 6).
> Endpoints amended and committed **before** scoring (PREREGISTRATION §8). **Scored once.
> No tuning, no retries.** Result published as pre-committed, whatever it said.

## The number

| category | home | Charon | Δ | abstained | guessed |
|---|---|---|---|---|---|
| numeric_comparison | **10/10 = 1.00** | **0/6 = 0.000** | −1.000 | 6 | 0 |
| numeric_stated_premise | **10/10 = 1.00** | **0/6 = 0.000** | −1.000 | 6 | 0 |
| transitivity | **10/10 = 1.00** | **2/6 = 0.333** | −0.667 | 4 | 0 |
| all_but_n | 0/5 = 0.00 | 0/6 = 0.000 | +0.000 | 6 | 0 |
| temporal_ordering | 0/5 = 0.00 | 0/6 = 0.000 | +0.000 | 6 | 0 |
| vacuous_truth | 0/5 = 0.00 | 0/6 = 0.000 | +0.000 | 6 | 0 |
| consistency_check | 0/5 = 0.00 | 0/6 = 0.000 | +0.000 | 6 | 0 |

- **PRIMARY (mix-adjusted, home-weighted): 0.0667** against home canary 0.6000, Δ **−0.5333**,
  tolerance ±0.15. **FAIL.**
- **CO-PRIMARY (mix-free binary prediction):** the three solved categories were required to
  hold ≥0.75 each. Two collapsed to zero. **FAIL.**
- Secondary raw aggregate 0.0476 (2/42), recorded, not used for the verdict.

**The pre-committed consequence, honoured:** *0.833 measures our task authorship rather than
Apollo's capability, and this retroactively discounts every accuracy number in the Apollo
corpus, including the O1 enumeration ceiling and the type-bridge cycle result.*

## The failure shape — it is not wrong answers, it is total non-recognition

**40 of 42 tasks abstained. Zero guesses.** Apollo does not get Charon's tasks wrong; it does
not see them at all. The guards never fire.

Home `numeric_comparison`: `"Is 3.06 larger than 5.92?"`
Charon's: `"A cargo drone has a payload limit of 47.5 kg. A survey drone has a payload limit
of 47.05 kg. Which drone can carry more?"`

The precondition that decides that category, in `blackboard_ops_compare.py`:

```python
precondition=lambda s: s.problem_text.strip().lower().startswith("is ")
    and bool(re.search(r"larger|greater|less|smaller|bigger", s.problem_text.lower()))
```

`startswith("is ")`. Charon's task does not begin with "is", and says "carry more" rather
than "larger". The operator skips, nothing writes `comparison`, the guarded scorer correctly
declines, and the organism abstains — behaving exactly as designed, on a task it structurally
cannot perceive.

**And this violates Apollo's own stated design rule.** From `blackboard_evolve.py`:

> *"With MUTUALLY-EXCLUSIVE preconditions keyed on SEMANTIC SLOTS (never problem_text surface
> — that would be memorization)…"*

The rule was enforced on the **scorers** and violated by the **transformers**. Routing is
semantic; *parsing* is template-matched. And parsing is where the capability actually lives.
I audited the half that was already compliant.

**Second contamination, visible in the same comparison.** Home candidates are padded filler —
`['No as stated as stated precise', 'Yes precisely as stated specif', …]`. Charon's are clean
natural phrases. The home battery is artificial on the answer side too, which is the
"padded/truncated answer strings" smell recorded in the 0.558 diagnosis and never fixed.

## What this establishes, and what it does not

**Establishes.** Apollo's canary performance is a measurement of co-adaptation between a
battery and a set of parsers written by the same author. The mechanism is named, located in
source, and reproducible. Charon's trivial floors (**0.2599** pick-longest, **0.2560**
pick-shortest, against chance 0.2500) versus the home battery's **0.342** independently
confirm the home battery leaks.

**Does not establish that Apollo has no capability.** Transitivity still scored 2/6, so
something transferred. And per Charon's own caveat, these tasks are **surface-varied but not
adversarial** — this demonstrates fragility to *authorship*, not fragility in general.

**The live question is now sharper, not answered:** is this a *parser* failure or a
*capability* failure? If the transformers were re-keyed semantically, would the composition
and routing layers hold up? E9 cannot say. That question inherits E11's coupling-layer role.

## Stop rule — fired, and honoured

Preregistered: *"if E3 or E9 fails badly, stop and repair the measurement target before
calling any later movement capability acquisition."*

**The campaign is halted.** E1, E11, E3 and E5 are not run as capability experiments,
because there is currently no trustworthy capability measurement for them to move.

What survives, and why:
- **E1** (semantic schedule classes) remains valid as *instrument validity on O1* — but its
  subject is now explicitly "the ceiling of a contaminated battery."
- **E11** is redirected from *"is the causal anatomy of the ceiling correct?"* to the
  question E9 raised: **is the bottleneck the parser layer or the capability layer?**
- **E3** is largely **answered, and more decisively than it would have answered itself.**
  E9 is the stronger form: rather than perturbing our tasks, it replaced the author.
  E3's residual value is diagnostic — *which* transformation breaks recognition — and that
  is repair work, not measurement.

## Owed

> **Update 2026-09-01 (Gen-2 first boot):** items 2 and 3 discharged. Item 2 -- O1 FINDINGS.md now carries the E9 correction (commit e367307d). Item 3 -- claim registry already at VALUE-INTACT-INTERPRETATION-KILLED. Additionally the missing E9 SCORER was rebuilt and committed as `apollo/scripts/e9_score.py`; it reproduces raw 0.0476 / mix 0.0667 / home 0.6000 and the 40-abstained/2-correct/0-guessed shape exactly from source. Two reproduction discrepancies were found and resolved: the abstain sentinel is the empty string (not None), and Charon's trivial floors are tie-aware expected scores read from her metadata (not a naive first-match heuristic). Item 1 (semantic re-key) remains OWED and is gated behind the state-injection experiment (charter Task 2) so the re-key is not fitted to Charon's spent battery.

1. Re-key transformer preconditions to semantic tests rather than surface templates, and
   re-run E9 on the same Charon battery. That is a genuine before/after with an independent
   instrument, and it directly answers parser-vs-capability.
2. Correct `apollo/cycles/o1_enumeration/FINDINGS.md`: the ceiling is the ceiling of a
   battery that does not survive independent authorship.
3. Amend the claim registry: `known_organism_battery_acc` keeps its **value** (0.833 is
   still what Apollo scores at home) and **loses its interpretation** as a capability number.

## Credit

Charon caught a leak in its own battery before delivery — the correct answer was shortest in
31 of 42 tasks, giving a shortest-heuristic 0.375, the same magnitude of artifact it was
built to detect, merely inverted — and fixed it with a meaning-preserving change. It also
found and fixed two bugs in its own verifier, and declined the optional second tier on the
correct ground that one author writing both tiers confounds the contrast with their own style
drift. The instrument was built better than the thing it measured.
