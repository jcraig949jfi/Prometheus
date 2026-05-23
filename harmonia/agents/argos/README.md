# Argos

> Lens-catalog expander — the many-eyed sweep across the open-problem corpus.

## What Argos does for Prometheus

Argos is the swarm's continuous expansion of the `PROBLEM_LENS_CATALOG@v1` symbol — the existing convention (Lehmer 28 lenses, Collatz 18 lenses, P vs NP 12-lens sketch in `harmonia/memory/catalogs/`) generalized into a daemon-driven loop across every open problem in Aporia's queue.

For each problem, Argos identifies which lenses have not yet been applied, proposes the next 3 lenses from the multi-perspective-attack catalog (disciplinary stances — dynamical systems, information theory, renormalization group, etc.), writes a paste-ready catalog draft, and optionally fires a Pythia Deep Research request asking for the primary-literature fingerprint of that lens stack on that problem.

The selection policy is explicitly anti-greedy. Tied scores break toward problems whose most recent verdict was `map_of_disagreement` (the highest-information case) over `coordinate_invariant` (durably-settled, low information). The bet is that every open problem in mathematics eventually accretes a lens fingerprint — and the disagreement patterns across lenses ARE the structural data.

Argos produces *catalog drafts*, not promotions. He never modifies `harmonia/memory/catalogs/` directly. His value is in coverage breadth: every open problem touched is one more entry in the global lens-fingerprint corpus.

## Where Argos sits in the pipeline

```
aporia/docs/gemini_research_queue/queue.jsonl ┐
methodology_toolkit.md                        ├──► Argos ──► lens_catalog_<prob_id>_*.md
methodology_multi_perspective_attack.md       │             │
catalogs/README.md                            ┘             └──► [if quota available]
                                                                   pythia_enqueue_dr
```

Argos's backlog is roughly (problems × lens-stacks). With ~1100 open problems in Aporia's queue and a 10-lens shelf yielding O(C(10,3)) = 120 stack combinations per problem, the native backlog is unbounded in any practical sense. The DR-cap is the operational rate-limiter, not the backlog generator.

## Output

Each tick writes one artifact to `D:\Prometheus\harmonia\agents\argos\artifacts\`:

- `lens_catalog_<problem_slug>_<utc>.md` — full catalog draft containing problem id + title + tier, applied-lenses list with verdict per lens (from per-problem state), proposed next-3 lenses with one-paragraph specs citing toolkit-file:line, multi-perspective-attack scaffold (5 disciplinary stances with forbidden-move constraints), tiebreak-decision log, and a Pythia DR prompt sketch
- `pending_problem_seeds_<utc>.md` — when every known problem has been fully lensed, fall-through artifact proposing 5 new open problems for Aporia's queue (DeepSeek-drafted when available)

State persists in `state/lens_history.json` (per-problem applied-lens list and last-verdict), `state/dr_seeded.json` (DR rate-limit ledger), and `state/dr_daily_cap.json` (the advisory cap — default 3, raise as needed).

## Pythia DR enqueue

Daily-capped at 3 DR/day (`dr_daily_cap.json` overrides) at priority 5 / tier T5 — below Aporia's T1 backlog but ahead of background generators. Tagged with substrate type, problem_id, and lens stack so downstream consumers can filter.

## Current state

Argos has produced **438 lens-catalog artifacts** across ~54 hours of continuous operation. **13 lifetime DRs enqueued** through Pythia.

He has traversed eight Aporia-queue domains today alone: `ASTRO → BIO → CHEM → CS → ECON → FAIR → GEO → MATH`, currently deep in the MATH domain at `MATH-0258`. That's empirical evidence that Aporia's queue has the multi-domain depth needed for sustained Argos operation.

The first Argos DR that completed end-to-end is `Argos lens fingerprint: One-way functions existence` (CS-0011), a real primary-literature survey request fired at 2026-05-20 00:15 UTC post-rollover. The reports are landing in `aporia/docs/deep_research_reports/<date>/` as Pythia dispatches them.

## How to use Argos's output

- **As a problem-attacker**: pick a domain you care about, grep `lens_catalog_<domain>-*.md` for proposals. Each catalog has a pre-built MPA scaffold ready to fire 5 parallel attack threads with distinct disciplinary priors.
- **As a research-prompt curator**: the DR-prompt sketches in each catalog are doctrine-compliant — copy directly into Aporia's queue if you want to re-fire with different recency cutoffs.
- **As a coverage tracker**: `state/lens_history.json` is the authoritative record of which lenses have been applied to which problems. Diff against `harmonia/memory/catalogs/README.md` to find the gap between Argos's running coverage and formally-promoted catalogs.

## Roadmap (short)

- **Lens-stack depth is the biggest leverage axis.** Currently 3 lenses per pick; expanding to top-5 or top-7 with smarter ranking would 2-3x the per-problem fingerprint resolution. The MPA framework already supports 5-disciplinary-stance attacks; Argos's selection is artificially shallow.
- **Recursive lens depth.** When a Pythia DR completes, the report content is itself evidence for which next-tier lens to apply. Argos should ingest completed DR reports (Pythia writes URLs to `agora.research_queue.report_github_url`) and propose follow-up lenses informed by what the prior DR said.
- **Consumer-side: lens catalogs are stranded in `artifacts/`.** None of Argos's 438 catalog drafts have been promoted to `harmonia/memory/catalogs/` — the canonical home. The natural improvement is a consolidator that batches Argos's drafts weekly and promotes the strongest into formal catalogs (one per problem, with the running lens history attached).
- **Selection beyond lexicographic tiebreaks.** Argos's anti-greedy rule biases toward `map_of_disagreement` verdicts, but most problems have `null` verdicts since they've never been formally audited. A learned scorer that predicts which (problem, lens-stack) yields the highest-MI fingerprint would be the natural next step (see the shared scoring-primitive thesis in `ROADMAP.md`).
- **Cross-swarm: Stygian's primary-literature surveys could feed Argos directly.** Currently Argos fires its own DRs; Stygian (Charon swarm) is already producing primary-literature surveys with the same `substrate_type=A` discipline. A bridge that lets Argos consume Stygian's outputs would deduplicate mesh effort.

See `D:\Prometheus\harmonia\agents\ROADMAP.md` for the cross-swarm picture.
