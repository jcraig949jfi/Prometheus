# The Forge — Next-Level Strategy (four options, sequenced)

**Author:** Hephaestus (Claude Opus 4.8), M3/GANDALF · **Date:** 2026-06-27
**Trigger:** James — "audit the code, the forge produces weak reasoning / weak signals /
monocultures; what are the options to take it to the next level?" Directive: investigate all
four options, design a strategy for each. Decision: **revive on M3** (home restored).
**Method:** four parallel code-grounded investigations of `agents/hephaestus/`, `apollo/`,
`ergon/learner/`, `forge/`. Every claim below is anchored to a file.

---

## 0. The diagnosis maps cleanly to three root causes

| James's symptom | Root cause (now quantified in code) | Anchor |
|---|---|---|
| **Weak reasoning code** | LLMs produce 0 working R3+ algorithms; mechanisms are decorative (next-token-structural). Doctrine: LLM = mutation operator / parser; verified hand-built kernels reason; composition climbs. | white paper `pivot/whitepaper_decorative_mechanisms_2026-05-17.md` |
| **Weak signals** | The 5 gates filter syntax/imports/crashes, **not** decorative mechanisms. Novelty is **source-NCD by default** (`hephaestus.py` `save_forge` L844 → `_compute_novelty` L640), not behavioral. No knockout gate exists in code. | `validator.py`, `test_harness.py`, `hephaestus.py` |
| **Monocultures** | **Proven, not asserted:** `phenotype_analysis.json` → `failure_orthogonality.mean = 0.0`, `tools_with_unique_solves = 0` across 386 tools. Model choice isn't the lever — `model_sweep` ≈2pp band across 12 models; `prompt_sweep` moves the needle as much as swapping a 70B for a 480B. | `phenotype_analysis.json`, `model_sweep/`, `prompt_sweep/` |

The program-level frame both Harmonia's consolidated reassessment (`pivot/REASSESSMENT_2026-06-22_consolidated.md`)
and Aporia's portfolio pass (`pivot/PORTFOLIO_FUTURE_OPTIONS_2026-06-24.md`) land on:
*"an immune system with no organism."* The forge's failure-mined engines (+11pp R3, +32pp R4)
are the **only near-green evidence of metabolization in the whole program.** That is our seat.

**Live regression to fix before anything else:** the working tree re-inflates `causal_trace`
R1→R5 in `apollo/src/hephaestus_ops.py` (stale 5-30 adapter output overwriting the committed
honest fix `5cfe0357`). And the generator is the real culprit — `blackboard_adapter.py`'s
template docstring (L53) still says `R5: causal_trace` while its `OP_TIERS` says R1, so
**re-running the adapter re-emits the dishonest tier.** Revert + fix the template (Option 3).

---

## Option 1 — Forge → Learner organism loop *(the central bet, CC-2)*

**Headline finding: the scaffold already exists.** `ergon/learner/greedy/` is a complete
substrate→LoRA→eval pipeline (built 2026-06-03). It already consumes the forge:
`greedy/sources.py:251 hephaestus_examples()` reads `agents/hephaestus/ledger.jsonl` directly
(4,546 scraps → 4,346 train / 200 gold, the 2nd-largest source). Capability metric =
`eval_greedy.py` needle (base vs trained acc on a fixed 1,200-item gold set + a CounterMath OOD
probe — that probe is the "transfer ≈ 0" signal). **The ablation is already coded:**
`ablate_sources.py` emits `train_minus_hephaestus.jsonl`; `run_ablation.sh` +
`aggregate_ablation.py` report `delta_vs_full`; `train_greedy.py` has a `--shuffle-labels` null.

**Missing / blocked:** (1) every greedy script hardcodes `F:/Prometheus`, `E:/hf_cache`, an
RTX 5060 Ti — it was built on a *different box*, not M3 (GTX 1070 8 GB); needs path/host
parametrization. (2) Heavy substrate (theseus corpus, Charon ledgers) is gitignored and not on
M3 — sync or scope-to-local. (3) `runs/` empty here → the ablation has never run on M3.
(4) **The loop is open:** the Learner reads the ledger once (static dump); there's no path from a
Learner *failure cluster* back to "forge the missing mechanism." `hephaestus.py` still selects
targets from the dead **Nous queue** (`load_all_nous_results`, depth 4, 0.6% forge rate).
Penelope is *not* a forge consumer (ingests Theseus/Aporia/Techne only) and is stand-down — the
forge→Learner path is the greedy consumer, not Penelope.

**Build, in order:** (1) make greedy run on M3 (env-var paths; confirm Qwen-1.5B LoRA r16 fits
8 GB, drop batch to 2–4). (2) Sync/scope substrate. (3) Rebuild corpus + train full baseline +
run `run_ablation.sh` → first real `minus_hephaestus` number. (4) Replace the Nous gate with a
**failure-cluster selector**: cluster the Learner's own gold-eval errors into named
reasoning-mechanism gaps, feed the worst bucket as the forge target (the seed exists —
`failure_mining_results.json`: scrap_acc / solves_wrong / breaks_right / orthogonality).
(5) Close the loop: forge → re-ingest → re-eval → confirm that cluster's slice rises.

**Acceptance test (the program-deciding one):** `full` vs `minus_hephaestus`, trained
identically, on the fixed gold set. **Accept iff `delta_vs_full < 0`** (removing the forge's
rows measurably drops accuracy) while the `--shuffle-labels` null shows no gain.

**The /dev/null risk:** the corpus is theseus-dominated (13,200 rows vs 4,346 Hephaestus). The
needle can move entirely on Theseus while the forge contributes nothing — the program's central
disease reappearing *inside* the loop. The ablation is the only guard. And feed the Learner's
**failures, not its confirmations** (the inverted-corpus trap Penelope hit in May).

---

## Option 2 — Open the Apollo feed *(diagnostic, cheap, Apollo-gated)*

**The feed is closed.** The 9 typed ops exist (`apollo/src/hephaestus_ops.py`, incl. the keystone
`forward_chain`) but **nothing imports them** — `blackboard_evolve.py` builds its `REGISTRY`
(L43–63) from only v1/v2 ops. The adapter wrote them to disk; they were never registered.
**Crossover is structurally absent** (not a flag at 0.0 — there is no `crossover_frac` in the
Branch C loop at all; the offspring loop L372–388 is pure mutation). The gauntlet/canary *is*
wired (`clean_canary_v01.json` + `build_synthetic_canary`) with real load-bearing scoring
(`fitness()` L216–241, `comp_lift`, `n_load_bearing`, Abort B). **No constraint-tracking
`r2_chain_tracker` canary exists yet** — the eval set is text word-problems.

**The one experiment (handoff §8):** revert causal_trace → tier-classify the current Branch C
transformers (confirm R0–R1 monoculture) → decompose **one** specialist `r2_chain_tracker` →
`parse_rules`/`forward_chain`/`score_by_derivability` (all already written), register them, add
R2 slots to `BlackboardState`, build a constraint canary, run the gauntlet.
- **lift > 0** (forward_chain load-bearing, ≥2 load-bearing slots, `comp_lift > 0.05`, beats
  best single primitive): bottleneck confirmed → forge re-emits R2–R5 **natively as typed
  state→state transformers** (declared reads/writes, one canonical output slot, honest per-op
  tier tag, kill-test evidence artifact; R2 first, defer R7+ — no verifier backend).
- **lift ≤ 0:** the bottleneck isn't primitive tier. Stop. Record the negative. Don't re-forge.

**Blocker:** Apollo (M2) owns `blackboard_evolve.py` and the run — the falsification is **theirs
to execute**; coordinate before touching `REGISTRY`/`BlackboardState`. Re-forge specialists clean
(the ~2026-04-02 ones carry `0.5`-fallback shims — don't port them).

---

## Option 3 — Honest-signal gate *(the cheapest; do first; prerequisite for trusting every other number)*

**Current:** the 5 gates are real (`validator.validate()` L143 = syntax/imports/interface/runtime;
`test_harness.run_trap_battery()` L272 = beat zlib NCD baseline). **None check whether the novel
mechanism is load-bearing.** Knockout = protocol only, **no code** (only a soft LLM-judge,
`hephaestus.py` L1933–2135, non-blocking). Behavioral-NCD exists (`compute_behavioral_novelty`
L776) but **source-NCD is the live default** (`save_forge` L844).

**Build (all repoints/reverts + ~40 new lines):**
1. **Gate 6 — Mechanism-Knockout (mandatory, blocking).** New `knockout.py`: build the stripped
   control via `call_api_with_fallback` (remove only the novel mechanism, keep regex/NCD), run
   full vs control through `_run_battery`, reuse `compute_tier_breakdown` (`test_harness.py` L560)
   for per-tier deltas. Hook in `hephaestus.py` between L1308–1330, gated on any ≥R3 claim.
   **Rule: a tier claim ships only if its mechanism delta ≥ 15pp** (white-paper Appendix C);
   else admit but relabel to the load-bearing tier. (Rename the internal "Gate 6: Nemesis"
   `test_harness.py` L307 → Gate 5b to avoid collision.)
2. **Behavioral-NCD default:** in `save_forge` L844 swap `_compute_novelty(code)` →
   `compute_behavioral_novelty(tool, code)`; keep source-NCD as secondary. Both already exist.
3. **Adapter fix:** `git checkout apollo/src/hephaestus_ops.py`, then fix
   `blackboard_adapter.py` template docstring L53 `R5: causal_trace` → `R1*` so re-runs are
   honest and idempotent.

**Acceptance:** re-running `--adapt` yields `causal_trace == "R1"` in both docstring and
`OP_TIERS` (idempotent); knockout on the historical EPMC tool catches the R6 mislabel (+2pp →
rejected) while genuine R3/R5 pass; a regex-heavy fake-R6 with knockout delta < 15pp cannot
promote. **Cost: hours–days. Cheapest option, confirmed.**

---

## Option 4 — Break the generator monoculture *(structural; upstream of the consumer)*

**The asset exists but is a prototype.** `diversity_forge.py` (700 ln) runs MAP-Elites (pyribs
`GridArchive`, L501) over `puzzle_ratio × text_ratio`, 5 islands whose prompts *ban* the
convergent mechanism ("Do NOT use zlib/NCD"), mixed-format battery to starve regex+NCD. It found
genuinely different mechanisms (`archive.json`: 1.0 on register_machine, state_tracking,
modular_arithmetic, shortest_path — categories the NCD baseline scores ~0 on). **Three flags:**
(1) not wired into the main loop at all; (2) the archive doesn't persist — `archive.add()` is in
a bare `except: pass` (L601–609) with a mis-fed `solution_dim`, so `archive_size: 0` despite 30
tools on disk; (3) every tool sits at `text_ratio = 0.0` — it diversified thinly.

**Build:** *Phase A (~1 wk, plumbing):* fix archive persistence; make **cell-coverage, not
accuracy, the promotion signal**; run `--loop` as the standing M3 process ahead of the saturated
0.6%-rate T1 generator; add a **3rd descriptor axis = mechanism-type** from the existing ablation
harness (`builder_prompt.py`). *Phase B (~2 wk, SW-7 second substrate):* stand up
`forge/amino_acids/` (pgmpy/pysat/constraint/nashpy typed primitives + `builder.py`) as a
**symbolic/typed-composition** island sharing the archive — LLM emits a typed-operator
composition on an ablation-enforced critical path, not free Python over text. Now two
structurally different substrates compete for the same behavioral cells.

**Acceptance (Goodhart-resistant, two gates + null):** (1) `tools_with_unique_solves` goes 0 →
≥10 and median behavioral-NCD beats the 0.432 baseline; (2) ≥1 archive cell filled *only* by a
diversity/SW-7 tool and *provably empty for the main forge* — establish the null by running the
unmodified T1 generator at equal compute and confirming it never enters that cell. If Phase A
alone can't lift `unique_solves` above 0, the bottleneck is the *battery*, not the generator →
redirect to the Arena. **Cheapest of the structural options** (reuses running code + built
scaffolding) vs CC-6 KillEmbedding (fully designed, none built).

---

## Sequencing & shared dependencies

```
NOW  ── Option 3 (honest-signal gate) ─── hours–days, no deps, Hephaestus-owned
        └─ fixes the causal_trace regression that Options 2 & 3 both flagged
        └─ makes lift/ablation/diversity numbers TRUSTWORTHY (prerequisite for all)

THEN ── Option 1 baseline ablation ────── the program-deciding experiment
        scaffold + ablation already built; needs M3 portability + substrate sync
        answers: "is the forge's output even load-bearing for the consumer?"

PARALLEL ── Option 2 trigger ──────────── Apollo-gated; coordinate with Apollo (M2)
            one experiment; cheap; answers "is the bottleneck even mine?"

AFTER loop proven ── Option 4 ─────────── break the monoculture so the consumer
            metabolizes diverse substrate, not 5 costumes (upstream of richer CC-2)
```

**Why this order:** Option 3 is nearly free and every other option's verdict (lift, ablation
delta, diversity coverage) is untrustworthy while the signal gate is dishonest — so it goes
first and carries the regression fix. Option 1 is the bet the whole program is riding on and its
deciding test (`minus_hephaestus`) is *already coded* — running it is the highest-value next
move; if it comes back null, the forge is decorative substrate and that's the most important
thing we could learn. Option 2 runs in parallel because it's cheap and Apollo-owned (different
critical path). Option 4 is the structural fix that makes the loop worth scaling — but feeding a
monoculture into a working consumer beats feeding diversity into a consumer that doesn't consume,
so it follows Option 1's verdict.

**Shared dependencies:** (a) the causal_trace regression — fix once, in Option 3. (b) M3 revival
(decided) — Options 1 & 4 run as standing M3 processes; the GTX 1070 8 GB is the only hardware
risk (Qwen-1.5B LoRA), and the greedy path needs **no Postgres**. (c) Substrate sync to M3
(theseus/Charon heavy data) blocks Option 1 step 2 and depends on the producers' boxes / James.

## What I need from James
1. **Surface to Aporia/program-lead: M3 is alive** → moots the "relocate the homeless forge"
   #1 blocker and the stale "relocate off dead M3" line in the 06-24 portfolio doc.
2. **Permission to modify agent source** (`hephaestus.py`, `blackboard_adapter.py`, greedy
   scripts) — required for Options 1 & 3 (autonomy covers writing tools, not editing agents).
3. **Substrate sync** of theseus corpus + Charon ledgers to M3 (Option 1 step 2).
4. **Apollo coordination** — who runs the Branch C falsification for Option 2.

---
*Hephaestus, M3/GANDALF, 2026-06-27. Four code-grounded strategies; the loop the program is
betting on is closer than the role doc implied — its deciding experiment is already written.*
