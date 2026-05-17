# Pipelines — declarative manifests

**Status:** v0 sketch, 2026-05-17. Schema is intentionally minimal; we'll iterate as real consumers emerge.

---

## Why manifests

Per the 2026-05-17 architecture discussion: workflows and pipelines are not bound to machines. Inputs and outputs are many-to-many. Each pipeline owns its concern; reporting aggregation is its own pipeline that reads across all of them.

For that to scale beyond what we can hold in James's head, each pipeline should be **self-describing** — declare its inputs, outputs, stages, machine affinity, and current status in a manifest file. Then:

- **Discovery** — anyone (including future-Aletheia) can list `pipelines/*.yaml` and immediately know what pipelines exist and what they produce.
- **Reporting** — `scripts/send_brief_email.py` and `scripts/portfolio_monitor.py` can read manifests to know which artifacts to surface in the brief.
- **Orchestration** (future) — a smarter `pronoia.py` could route pipeline stages across machines based on manifest's `machine_affinity` + machine capabilities.
- **Dependency tracking** — when a stage's output is another stage's input, the manifests make the DAG explicit.

## Schema v0

A pipeline manifest is YAML at `pipelines/<pipeline_id>.yaml`. Required fields:

- `schema_version` — integer, currently 1
- `pipeline_id` — unique slug, kebab-case
- `display_name` — human-friendly name
- `purpose` — one-paragraph description; what this pipeline is for and who consumes its output
- `status` — `active` / `paused` / `archived`
- `owner` — who's responsible (agent name or "human")

Optional but recommended:

- `machine_affinity` — `{ preferred: [M2, M4], required: false }`. Null/omitted = runs anywhere.
- `schedule` — `{ trigger: event|cron|continuous, cadence: "..." }`
- `inputs` — list of `{ source, purpose }` pairs. `source` can be:
  - `agora.streams.<name>` (Redis stream)
  - `agora.<table>` (Postgres table)
  - `<filesystem-path>` (relative to repo root)
  - `<url>` (external API)
- `outputs` — list of `{ target, consumers }` pairs. Targets follow the same convention as inputs.
- `stages` — list of `{ id, runner, depends_on?, timeout_min?, machine_affinity? }` per stage.
- `related_docs` — list of repo-relative paths to design docs, autopsies, etc.
- `notes` — free-form.

## Current pipelines

- `intelligence-pipeline.yaml` — Eos→Aletheia→Skopos→Metis-paper→Clymene scan of external research.
- `forge-pipeline.yaml` — Nous→Hephaestus→Nemesis production of Python reasoning tools + adversarial Goodhart-gap testing.
- `reporting-pipeline.yaml` — Portfolio-monitor + Metis-portfolio + Email + Dashboard, the cross-pipeline observability layer.

## How manifests will be used (v1, not implemented yet)

- `scripts/portfolio_monitor.py` reads manifests to know which output targets to check for freshness.
- `scripts/send_brief_email.py` reads manifests to build the References section automatically from `related_docs` and `outputs` fields, instead of the hand-curated `STATIC_REFS` registry.
- `pronoia.py` (or a successor) reads manifests to plan execution: which stages to run, which machine to target based on affinity, what timeouts to enforce.

For now the manifests are **descriptive**, not yet load-bearing. They document the current state of each pipeline; they don't drive execution. Promote to load-bearing in a future cycle when the consumers above are wired.

## Out of scope for v0

- Manifest validation (jsonschema, etc.) — easy to add later.
- Cross-pipeline DAG visualization — neat but not urgent.
- Manifest auto-generation from agent introspection — would be elegant; not now.
- Manifest-driven failure routing (if stage X fails, escalate to Y) — depends on having a real orchestrator that consumes manifests.
