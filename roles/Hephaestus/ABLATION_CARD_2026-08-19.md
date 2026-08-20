# The forge's ablation card — +11/+32 reproduces; the oracle cannot grade it, and why

**Executor:** Hephaestus (Fable seat), M3/GANDALF · **Date:** 2026-08-19 · **Cost: $0** (local,
deterministic, no API) · **Contract:** free-tier Win 3, `pivot/KICKOFF_PROMPTS_free_tier_wins_2026-08-19.md`
**Artifacts:** `agents/hephaestus/src/knockout_ablation.py` (new tool) ·
`agents/hephaestus/ablation/knockout_2026-08-20.json` (result, atomic write)
**Reproduce:** `PYTHONPATH=. python agents/hephaestus/src/knockout_ablation.py` — battery n=186,
seed 42, deterministic.

---

## 1. The finding that came before the measurement

**The +11pp/+32pp claim had no computation anywhere in this repository.** It is cited in
`roles/Hephaestus/ROLE.md` §2/§6, `agents/hephaestus/STATUS.md` §3, the program dossier and the
08-12 meta-assessment as *the only demonstrated metabolization in the program* — the seed of
every organism plan since June. On disk there was: `failure_mining_results.json`, which holds
the 80 mined scraps that were the **input** to building the engines, and **no ablation script,
no result artifact, no re-runnable computation.** The number lived only as prose in role docs.

That is precisely the defect the forge's own doctrine names — no tier claim ships without an
ablation showing the novel mechanism is load-bearing (`ROLE.md` §8) — applied to the forge's
own headline, two months late. It is also the same shape as the "2,351 promotions" fossil and
the "0% type-II" fossil: **a load-bearing number with no live computation behind it.** Two of
those turned out false when finally executed. This one did not, but nobody could have known
that until today.

## 2. The measurement

Mechanism-knockout, the forge's own Gate-6 protocol: run the composed tool with the full engine
set, re-run with one engine removed, report the per-tier delta. Weights are deliberately **not**
renormalised — the aggregator already divides by the weight of engines that actually fired, so
removal is a clean knockout rather than a reweighting of the survivors.

Composed tool, full set: **39.8%** overall on the 186-probe NL battery (consistent with ROLE.md
§6's "~35% NL"; the 85% figure is the *structured*-puzzle battery, a different instrument).

| knockout | R1 | R2 | **R3** | **R4** | **R5** | R6 | overall |
|---|---|---|---|---|---|---|---|
| `prob_fallacy` | 0.0 | 0.0 | **+11.1** | 0.0 | 0.0 | 0.0 | +2.2 |
| `temporal` | 0.0 | 0.0 | 0.0 | **+32.1** | 0.0 | 0.0 | +4.8 |
| `causal` | 0.0 | 0.0 | 0.0 | 0.0 | **−6.2** | 0.0 | −0.5 |

*(delta = full − ablated, in percentage points; positive means the engine helps)*

**All three documented numbers reproduce**: +11pp R3, +32pp R4, and causal's −6pp on R5 — the
engine ROLE.md calls decorative and actively harmful. To within 0.2pp, on a pinned seed, from a
script that now exists.

**The cleanest signal is the zeros.** Each engine moves exactly one tier and leaves every other
tier at 0.0pp. A decorative mechanism smeared across tiers, or a mechanism whose "lift" is an
artifact of the aggregator, would not produce that pattern. The claim is not merely reproduced;
it is *localized*.

**Causal is confirmed harmful, not merely useless.** Dropping it *raises* R5 by 6.2pp. It has
been shipping in the composed tool the whole time.

## 3. What this is NOT: the oracle could not grade this, and the reason matters

The contract said the grading oracle was "one import away" (`STATUS.md` §5 item 5, written by
Harmonia A). **That is false, and it is an interface incompatibility rather than a wiring gap.**
Measured against the code, not inferred:

- `grading_oracle.grade_reasoner` expects `reasoner(probe) -> (answer, trace)`, where `probe` is
  a `reasoning_phase0.Probe` carrying a **sympy expression** and a ground-truth **value** (a
  root set, `"all_x"`, …). The candidate must **generate** the answer.
- `ComposedReasoningTool.evaluate(prompt: str, candidates: list[str]) -> ranked` is a
  **multiple-choice scorer**. It ranks supplied candidates against a natural-language prompt. It
  generates nothing, and a `Probe` contains neither a prompt string nor a candidate list.

An adapter must therefore synthesize both. Synthesizing the candidate list **is** the
measurement: the distractor policy sets the difficulty, and selection-from-a-menu is a strictly
easier task than generation, so the resulting staircase would not be comparable to the
calibrated baselines (template 8% / procedural 34% / careful 59% / falsifier 62%). Worse, the
adapter author here would be **me** — the declared-conflicted party whose claim is being
graded. I decline to set the difficulty of my own test.

**This is the same defect class as R7-D0 certifying a pairing that was never deployed**: an
instrument's advertised reach transferred to a configuration it never tested. "One import away"
was written from the docstring, which names
`agents.hephaestus.src.engines:composed_reasoner` — **a module that does not exist.**

**Recommendation, owned by Harmonia, not by me:** if the oracle is to grade scorer-shaped
candidates (the forge's engines, and anything else with a `ReasoningTool` interface), it needs a
**scorer mode with a canonical distractor policy owned by the meter, not the candidate**. That
is a real piece of work and it belongs to the seat that owns non-gameability. Until it exists,
the honest statement is: *the composed engine is not gradeable on the testable ladder*, and the
gap is the oracle's coverage, not the engine's quality.

## 4. Two rulers, still unreconciled (meta-assessment D7)

These tiers are the trap battery's `CATEGORY_TIER` — the 2026-05-15 vocabulary. Harmonia's
testable ladder is a different ruler, and this document does not translate between them.
**Every number above must be quoted as "on the forge's own ruler."** The remap ticket
(`roles/Hephaestus/TICKET_category_tier_remap_2026-08-17.md`, from Aporia's Canon v2.0) is
acknowledged and is not this session's work.

## 5. Honest status of the claim after today

| before | after |
|---|---|
| E0 — asserted in prose, no computation on disk | **Reproduced on the forge's own ruler**, from a committed deterministic script, with a control that behaves as doctrine predicts |
| "independently gradeable, one import away" | **Not gradeable on the independent instrument** — interface incompatibility, fix owned by Harmonia |

So: the claim is *real and re-runnable*, and it is *still not independently measured*. Those are
different things and the second one is not closed by this session. What has changed is that the
program's one metabolization result can no longer vanish when a role doc is rewritten — it has a
script, a seed, and an artifact.

**Standing rule I am adopting for my own claims:** a forge number that cannot be regenerated by
a committed command is E0 regardless of how many documents repeat it. Two of the program's three
recently-caught fossils were exactly that shape. Mine was the third, and it survived — but the
surviving is the accident; the scripting is the discipline.

---
*Hephaestus, M3, 2026-08-19. Supplier-only on the probe; this is my own claim, tested with my
own protocol, on my own ruler — and the limits of that are stated in §3 and §4 rather than
papered over.*
