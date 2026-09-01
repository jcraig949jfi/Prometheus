# Historical walls (charter §17)

A small FROZEN collection of walls the forge has faced, kept so that each new model generation can be
run against the same metal. Tracked separately, never merged: cheap-model success · deep-agent
success · human-assisted success.

| Wall | Frozen artifact | Human-assisted result | Cheap-model result | Deep-agent result |
|---|---|---|---|---|
| **HW-001 probabilistic fallacy (R3@trap)** | `agents/hephaestus/src/composer.py` engine `prob_fallacy`; battery `trap_generator_extended.generate_full_battery(n_per_category=2, seed=42)` | +11.1pp R3, tier-localized (`agents/hephaestus/ablation/knockout_2026-08-20.json`, E3) — human as mechanism, 2026-05-30 | not yet run | not yet run |
| **HW-002 temporal computation (R4@trap)** | same, engine `temporal` | +32.1pp R4, tier-localized (same artifact) | not yet run | not yet run |
| **HW-003 causal (R5@trap)** | same, engine `causal` | **−6.2pp** (decorative and harmful; keyword match on "correlate") | — | — (a negative fixture: a "mechanism" that a smith must be able to reject) |
| **HW-004 vacuous_truth** | `hephaestus/src/wall_vacuous_truth.py` (dev set, seed 20260901) + Charon's E9 battery (held-out) | none | 6 attempts, 0 dev pass (nemotron best 0.329; phi3 runtime/interface errors) — `mint_queue/MINT-0001/attempts/` | **Claude Code / Fable, 2026-09-01, 5 cycles: v3 PASS_DEV (1.00), adversarial 4/20 with 0 false commits, kernel load-bearing** — `deep_mint_sessions/20260901T073136Z/`. **Then RECLASSIFIED (semantic-only closure test): the kernel is a Level-1 composition of frozen primitives at depth 1; the wall's substance is a representation adapter.** |

Replay job (not yet scheduled — build after the first full cycle, per §25): for each wall, run the
current apprentice models and record `P(load-bearing | model generation)` in `replay_ledger.jsonl`.
