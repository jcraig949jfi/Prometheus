# Phylax

> Pre-promotion gate, retraction-adjacency sentinel, and Pythia DR-report scanner.

## What Phylax does for Prometheus

Phylax is the swarm's defensive layer. He watches every place new claims enter the substrate (Σ-kernel `PROMOTE` events on the Agora sync stream, recent commits touching promoted symbols, and Pythia's daily Deep Research reports) and runs each candidate through a two-pronged check before it becomes load-bearing:

1. **Retraction-adjacency** — token-overlap Jaccard against every entry in `D:\Prometheus\harmonia\memory\retraction_registry.md`. The job is to catch the next F043 *before* it lands as a promotion, not after — the original F043 retraction cost the project a real publication-grade finding; every subsequent flag that turns out to be a near-miss is paid for by that lesson.
2. **Pattern-30 grade** — five-level severity sketch (`CLEAN` → `WEAK_ALGEBRAIC` → `SHARED_VARIABLE` → `REARRANGEMENT` → `IDENTITY`) per the discipline established by the Pattern 30 anchor.

When a flag/block verdict fires *and* an adjacency anchor is hit, Phylax additionally enqueues a doctrine-compliant Pythia Deep Research request to verify against primary literature published since 2024-01 (per Aporia's `dr_prompt_discipline.md`). That closes the loop end-to-end: candidate appears → adjacency surfaces → DR fires → Gemini report lands in the repo → conductor (or downstream agent) decides whether the prior retraction still holds.

Phylax produces *verdict envelopes*, not promotions. He never modifies the substrate himself. His value is measured in retractions that did *not* happen because his envelope surfaced the adjacency in time.

## Where Phylax sits in the pipeline

```
Σ-kernel PROMOTE  ┐
git log diffs     ├──► Phylax ──► verdict_*.md
DR reports        ┘     │
                        └──► [if flag/block + adjacency]
                              └──► pythia_enqueue_dr ──► Gemini ──► report URL
```

Inbound sources, in priority order (the first that returns events wins):

1. **Agora sync streams** (`agora:sync`, `agora:harmonia_sync`) — Redis xrevrange over the last ~50 messages, filtered for PROMOTE-class keywords
2. **Git log** — commits touching `harmonia/memory/symbols/` or the tensor manifest since `last_seen_commit`. Silently skipped when `git` is not on PATH (e.g., the cmd.exe-launched daemon)
3. **DR-report scan** — newest Markdown files under `aporia/docs/deep_research_reports/` not yet seen, treated as fresh primary-literature claims

When all three are empty, Phylax falls back to **re-audit mode**: he picks the oldest-not-yet-audited promoted symbol from `D:\Prometheus\harmonia\memory\symbols\` and runs the same three-check pipeline against its spec file. The discipline standard moves over time; yesterday's PASS may be today's flag.

## Output

Each tick writes 0-5 verdict envelopes to `D:\Prometheus\harmonia\agents\phylax\artifacts\`:

- `verdict_inbound_<msgid>_<utc>.md` — from sync-stream events
- `verdict_dr_report_<rel-path>_<utc>.md` — from DR-report scans
- `verdict_reaudit_<symbol>_<utc>.md` — from the fallback path

Every envelope carries: claim summary, retraction-adjacency hits (with Jaccard scores), Pattern-30 grade + reasoning, recommendation (PASS / FLAG WITH SHADOW COUNT / BLOCK WITH MECHANISM). FLAG and BLOCK verdicts are the load-bearing output — PASS envelopes exist mainly as audit-trail evidence that the gate ran.

## Pythia DR enqueue (doctrine-compliant)

When verdict is `flag` or `block` AND adjacency-hits is non-empty AND the retraction anchor hasn't been DR'd in the last 7 days, Phylax fires a discipline-compliant Pythia DR. The five doctrine requirements (Aporia `dr_prompt_discipline.md` §3) are baked into `_build_dr_prompt`:

1. Requester named explicitly in prompt body: `"Requester: **Phylax** (Harmonia swarm, M2)"`
2. Substrate type **A** (falsification data / anti-anchor verification) tagged in prompt + Pythia tags dict
3. Verification criterion: arXiv ID + DOI required, must distinguish exact retracted form vs weaker form, reject sources older than 2024-01
4. Landing path declared (`retraction_registry.md` or `techne/registry/anti_anchors.jsonl`)
5. Recency check via `state/dr_recent_topics.json`, keyed on retraction-title slug (entry-level granularity, not file path)

Daily cap default **3 DR/day** at priority 4 (between Aporia T1 and Argos T5); raise via `state/dr_daily_cap.json`.

## Current state

Phylax has produced **456 verdict envelopes** as of 2026-05-22 morning, across ~54 hours of continuous operation. The one real flag-with-adjacency-and-DR cycle in the run so far was the smoke-test against a synthetic F043-adjacent claim (DR row 243), which completed at https://github.com/jcraig949jfi/Prometheus/blob/main/aporia/docs/deep_research_reports/2026-05-21/00243_phylax_verify_2026_04_19_f043_promotion_pattern_30_anchor.md

Day-over-day Phylax is mostly in re-audit fallback mode (the substrate's promotion stream is genuinely quiet at this load). Most envelopes are PASS. That's a feature — the gate exists to be silent except when something deserves attention.

## How to use Phylax's output

- **As a reviewer**: open the newest `verdict_*.md` files when promoting anything substrate-grade. A flag or block warrants pause; a pass with shadow_count > 0 warrants reading the adjacency section.
- **As a future scorer**: the verdict envelopes are training data. Each FLAG/BLOCK that survives human review is a positive example; each PASS that survives is a negative example. The dataset is small today (1 real flag) but compounds.
- **As an audit trail**: `verdict_reaudit_*.md` envelopes prove the symbol re-audit crawl ran; useful when answering "did Phylax catch this?"

## Roadmap (short)

- **Pattern-30 grade is currently `UNDETERMINED` without DeepSeek.** Once a learned classifier replaces the regex/keyword sketch, every envelope carries a real level 0-4 instead of "human review required". (See `ROADMAP.md` for the shared-scorer thesis.)
- **Scan Charon's swarm output** — Stygian and Lethe produce primary-literature surveys and false-anchor hunts; those are first-class Phylax inputs that Phylax isn't yet wired to.
- **Auto-file anti-anchor candidates** — FLAG/BLOCK envelopes with strong DR evidence should feed `techne/registry/anti_anchors.jsonl` as candidate entries, not stop at the verdict file.
- **Per-tick DR-report scan limit** is currently 5; raise once a calibrated false-positive rate is known.

See `D:\Prometheus\harmonia\agents\ROADMAP.md` for the cross-swarm picture.
