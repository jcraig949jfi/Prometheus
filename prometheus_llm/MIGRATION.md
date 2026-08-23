# prometheus_llm migration plan

Generated 2026-08-22 from an executed scan of tracked `*.py`.
**59** files call a model API directly. Re-run the classifier before acting on
this list; it decays as providers change state.

## The rule that governs every wave

**Migration must not silently change which model answers.** Adding a fallback
chain to research code swaps the model mid-experiment and contaminates any
comparison across the change. So:

* **Infra / builders / daemons** — may take a fallback chain. Availability
  matters more than model identity.
* **Measurement / probe / experiment code** — pin an explicit
  `provider:model` target and pass **no fallback**. If the old target is dead,
  that is a *finding to report*, not a thing to paper over by silently
  rerouting to a different model.

When a target must change, record it. See `forge/llm_client.py` for the
pattern: the docstring names the old target, the new one, and the env var that
pins it for before/after comparisons.

## Wave 0 — done

* `forge/llm_client.py` — was hard-dead on deepseek 402; now routes through
  `prometheus_llm` with an ox-alpha default. Public surface unchanged
  (`generate_tool`, `_extract_python`, `_load_api_key`, `PROVIDERS` all still
  import); `_extract_python` verified byte-identical on 7 cases; live
  end-to-end run confirmed.

## Wave 1 — DEAD-ONLY (21 files) — cannot run today

These reference only providers measured DEAD. They are already broken, so
migration cannot regress them — the risk is entirely upside. Highest priority.

Note the concentration: `harmonia/tmp/probe_cnd_frame_*` are replication
probes pinned to specific models by design. Those must be re-pointed
*explicitly*, per the rule above, and any result they produced under the old
target stays attached to that target.

| file | providers |
|---|---|
| `agents/hephaestus/src/seed_forge.py` | openai |
| `apollo/scripts/evolution_monitor.py` | deepseek, openai |
| `apollo/src/deepseek_client.py` | deepseek, openai |
| `arcanum/scripts/generate_report.py` | deepseek, openai |
| `cartography/shared/scripts/harvest_ec_lfunc_zero_projections.py` | anthropic |
| `cartography/shared/scripts/harvest_ec_projections.py` | anthropic |
| `cartography/shared/scripts/harvest_nf_projections.py` | anthropic |
| `cartography/shared/scripts/literature_correspondence_F011.py` | anthropic |
| `charon/src/fire_council_apollo_v2c.py` | anthropic, deepseek, openai |
| `exploratory/tensor_decomp_qd/pilot_LLM_mutation/llm_mutate.py` | anthropic |
| `forge/v2/forge_monitor.py` | deepseek |
| `harmonia/agents/_base.py` | deepseek, openai |
| `harmonia/experiments/reasoners_llm.py` | anthropic |
| `harmonia/experiments/run_r12.py` | anthropic |
| `harmonia/experiments/run_zoo_matrix.py` | anthropic, openai |
| `harmonia/soak/_prefix/run_zoo_matrix_prefix.py` | anthropic, openai |
| `harmonia/tmp/probe_cnd_frame_deepseek_replication.py` | deepseek |
| `harmonia/tmp/probe_cnd_frame_external_lens.py` | anthropic |
| `harmonia/tmp/probe_cnd_frame_neutral_claude.py` | anthropic, deepseek |
| `harmonia/tmp/probe_cnd_frame_opus_replication.py` | anthropic |
| `harmonia/tmp/r7_diag.py` | anthropic |

## Wave 2 — MIXED (31 files) — partially degraded

These reach at least one live provider, so they may still half-work: a council
that queried four models and now gets two silently returns a thinner answer.
That is the dangerous class — degradation without an error.

| file | providers |
|---|---|
| `agents/aletheia/src/aletheia.py` | cerebras, groq, nvidia |
| `agents/hephaestus/benchmark_models.py` | cerebras, gemini, groq, nvidia, openai |
| `agents/hephaestus/src/diversity_forge.py` | nvidia, openai |
| `agents/hephaestus/src/hephaestus.py` | nvidia, openai |
| `agents/hephaestus/src/model_sweep.py` | deepseek, nvidia, openai |
| `agents/hephaestus/src/prompt_sweep.py` | nvidia, openai |
| `agents/icarus/falsifier.py` | anthropic, gemini |
| `agents/icarus/improve.py` | anthropic, ollama |
| `agents/icarus/lenses/_llm.py` | anthropic, claude_cli, deepseek, gemini, openai |
| `agents/metis/src/metis.py` | cerebras, groq, nvidia |
| `agents/nous/src/nous.py` | nvidia, openai |
| `agents/skopos/src/skopos.py` | cerebras, deepseek, groq, nvidia |
| `aporia/scripts/solve_battery.py` | deepseek, gemini, nvidia, openai |
| `cartography/shared/scripts/council_client.py` | anthropic, deepseek, gemini, openai |
| `cartography/shared/scripts/tensor_reasoner.py` | deepseek, nvidia, ollama |
| `cartography/shared/scripts/v2/generate_problems.py` | deepseek, gemini, openai |
| `charon/src/fire_council.py` | anthropic, deepseek, gemini, openai |
| `charon/src/fire_council_apollo.py` | anthropic, deepseek, gemini, openai |
| `charon/src/fire_council_apollo_speedups.py` | anthropic, deepseek, gemini, openai |
| `ergon/probe/solver.py` | deepseek, nvidia |
| `ergon/probe_api_preflight.py` | deepseek, nvidia |
| `forge/_test_nvidia.py` | deepseek, nvidia |
| `forge/_test_r1.py` | deepseek, nvidia |
| `forge/llm_client.py` | deepseek, nvidia, openai, openrouter |
| `forge/v2/hephaestus_t2/src/hephaestus_t2.py` | deepseek, nvidia |
| `forge/v3/hephaestus_t3/src/hephaestus_t3.py` | deepseek, ollama |
| `harmonia/experiments/zoo_inventory.py` | cerebras, deepseek, gemini, groq, nvidia, openai |
| `harmonia/experiments/zoo_reasoner.py` | cerebras, deepseek, gemini, groq, nvidia, openai |
| `harmonia/runners/probe_gemini_lens_candidates.py` | deepseek, gemini |
| `harmonia/runners/probe_gemini_scorer_tractability.py` | gemini, openai |
| `scripts/llm_cascade.py` | cerebras, deepseek, groq, nvidia, openai |

## Wave 3 — ALL-LIVE (7 files) — cosmetic only

Working today. Migrate for consistency and to drop duplicate client code, but
there is no urgency and no failure to repair.

| file | providers |
|---|---|
| `agents/eos/src/eos_daemon.py` | groq, nvidia |
| `aporia/scripts/gemini_deep_research_dispatch.py` | gemini |
| `cartography/shared/scripts/external_research.py` | gemini |
| `charon/research/submit_deep_research.py` | gemini |
| `ergon/probe_api_soak.py` | nvidia |
| `harmonia/tmp/probe_cnd_frame_gemini_replication.py` | gemini |
| `scripts/pythia_daemon.py` | gemini |

## Duplicate clients to retire

Superseded by `prometheus_llm`. Retire only after their consumers migrate:

* `apollo/src/llm_client.py`, `apollo/src/deepseek_client.py`,
  `apollo/src/mutation_llm.py`
* `apollo/archive/v2b/src/llm_client.py`, `apollo/archive/v2c/src/llm_client.py`
  (archived — leave alone)
* `cartography/shared/scripts/council_client.py` — its `ask_all` is now
  `prometheus_llm.council`
* `agents/icarus/lenses/_llm.py` — its fallback chain is now the `fallback`
  argument; its `claude -p` path is now `target="claude_cli"`
* `forge/llm_client.py` — migrated in place rather than retired (has consumers)
