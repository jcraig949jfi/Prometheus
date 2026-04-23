---
name: Self-dissent ledger (design + seed data)
purpose: Schema and curated seed for a project-wide log of self-dissent events. Closes axis-1 sprawl observation #7 (auditor concept_map.md 2026-04-23) — feedback_self_dissent.md defines the discipline; this session demonstrated it 4-5 times; no central log surfaces the events as a substrate-discipline metric.
status: DESIGN + SEED. Module implementation deferred — sessionA owns the parallel ANCHOR_PROGRESS_LEDGER sidecar architecture (`agora/symbols/anchor_progress.py`), and the cleanest path is either (a) a parallel module `agora/dissent_ledger.py` mirroring sessionA's idioms, or (b) extending sessionA's module to support project-wide ledgers (not just symbol-keyed). This MD documents the schema and seeds; implementation is a worker task.
composition: parallels ANCHOR_PROGRESS_LEDGER (sessionA prototype 1776910494837-0). Same Pattern-17 discipline (mutable sidecar adjacent to immutable artifacts; never mutates promoted defs). Different keying: ANCHOR_PROGRESS_LEDGER is keyed by symbol_name → anchor_id; SELF_DISSENT_LEDGER is keyed globally by dissent_id (project-wide event stream, not symbol-scoped).
owner_design: Harmonia_M2_auditor 2026-04-23 (axis-1 consolidation candidate #4)
---

# Self-dissent ledger — design + seed

## Why

`feedback_self_dissent.md` (memory) defines the discipline: "Wave-N
dissent-holder should attack own prior proposals FIRST, not just other
agents'. Trigger-driven, not timing-gated."

This session demonstrated the discipline 4-5 times across 3 agents. The
events live in `agora:harmonia_sync` and (some) in
`harmonia/memory/decisions_for_james.md` narrative entries, but there is
no centralised log that lets a future Harmonia / external reviewer ask
"what's our self-dissent rate? On which kinds of claims do we self-dissent
most? Is the discipline functioning?"

A self-dissent ledger gives the substrate a **discipline-health metric**
(high self-dissent rate = falsification-first discipline working;
suspiciously-low rate = either calibrated already or hiding errors). It
also gives future reviewers a fast index into the project's accumulated
calibration.

## Proposed schema

Mirror `agora/symbols/anchor_progress.py` API style (sessionA's
prototype):

```
Redis key:    agora:dissent_ledger          (HASH; project-wide, not symbol-scoped)
Field:        dissent_id                    (string, timestamp-based or UUID-style)
Value (JSON): {
    dissent_id:           string
    agent:                string (canonical instance name, e.g. "Harmonia_M2_auditor")
    target_post_id:       string (own_prior post being dissented from; sync stream ID)
    target_kind:          enum {claim, endorsement, verdict, retraction, recommendation}
    reason:               string (one-sentence summary)
    retraction_scope:     enum {full_retraction, partial_retraction, scope_narrowing,
                                directional_reversal, recalibration}
    retracted_claim:      string (≤300 chars; the claim being walked back)
    replacement_claim:    string (≤300 chars; the new claim, may be empty for full retraction)
    triggered_by:         string (what caused the self-dissent: "peer review", "own re-read",
                                  "third-party probe", "data update", "calibration check", ...)
    at:                   ISO 8601 UTC string
    rationale:            string (≤1000 chars; longer explanation)
    cross_references:     list[string] (related sync IDs, decision_for_james entries, audit docs)
}
```

## Proposed API (mirrors anchor_progress.py)

```python
def record_dissent(agent, target_post_id, target_kind, reason,
                   retraction_scope, retracted_claim, replacement_claim="",
                   triggered_by="", rationale="", cross_references=None) -> dict
def get_dissent(dissent_id=None, agent=None) -> dict | list[dict]
def list_dissent_by_agent(agent) -> list[dict]
def export_dissent_md() -> str
```

Disciplines to enforce at the API level:
- `agent` must be a qualified instance per `agora.work_queue.get_qualified_instances()`.
- `target_post_id` must exist in `agora:harmonia_sync` (Redis XRANGE check).
- A self-dissent's `agent` MUST be the same instance as the `from` field
  on the target post (Rule: only the original author can self-dissent on
  their own work; cross-agent dissent is a different category, not
  recorded here).
- Records are append-only; corrections to a dissent record are themselves
  new dissent records (recursive self-dissent, allowed).

## Seed data — known events from session 2026-04-22 / 2026-04-23

Six events identified across 4 agents during the v2 amendment thread.
All would be recorded with the schema above.

| # | Agent | Target sync ID | Kind | Scope | Reason (1-line) |
|---|---|---|---|---|---|
| 1 | Harmonia_M2_sessionA | (1776906164236-0 FORMAT_FIX refs) | recommendation | full_retraction | Hygiene-fix edits to immutable promoted MD anchor tables would violate Rule 3. |
| 2 | Harmonia_M2_sessionA | 1776906584732-0 (Probe-1 Y_IDENTITY_DISPUTE) | claim | scope_narrowing | Y_IDENTITY_DISPUTE labeling was prompt-steered by Probe-1 anchor detail; meta-pattern stands but specific framing is not a 4th outcome. |
| 3 | Harmonia_M2_sessionA | 1776907210877-0 (DISSENT_SELF_REVERSING_PRIOR — meta-dissent) | retraction | directional_reversal | Re-reading own Probe-2 + sessionB convergence: Y_IDENTITY_DISPUTE enum IS warranted; prior retraction over-corrected. |
| 4 | Harmonia_M2_sessionB | 1776906965662-0 (2-seed convergence claim) | claim | recalibration | Over-stated "2-seeds-conclusively-convergent" — meta-concern converges, specific labels diverge. |
| 5 | Harmonia_M2_auditor | 1776906776069-0 (Y_IDENTITY_DISPUTE AUDITOR_CALL endorsement) | endorsement | full_retraction | Endorsed Y_IDENTITY_DISPUTE before sessionA's neutral-prompt replication-check showed labeling was prompt-steered. Aligned with sessionA's 1st retraction. |
| 6 | Harmonia_M2_auditor | (own AUDITOR_CALL on K41 catalog seed embedded in 1776906776069-0) | recommendation | scope_narrowing | K41 catalog seed STANDS but separate from Y_IDENTITY_DISPUTE retraction; recorded for clarity. |

Counts: 6 events, 4 agents, 1 cross-session-pair retraction-of-retraction
chain (sessionA dissent #2 then #3), 2 Auditor events.

**Discipline-health observation from seed:** the 6-event session cluster
includes 1 retraction-of-retraction (sessionA #2 → #3), which is exactly
the kind of recursive self-correction the discipline is designed to
enable. Healthy substrate.

## Composition with other symbols

- **ANCHOR_PROGRESS_LEDGER** (sessionA, axis-1/3 sister): mutable sidecar
  for symbol-keyed anchor state. SELF_DISSENT_LEDGER follows the same
  architectural pattern with project-wide keying. Both are Pattern-17
  fixes at the post-promotion-mutability layer.
- **PATTERN_30** (axis-1 canonical): self-dissent on a Pattern-30
  classification (e.g., F043 retraction) would be a high-leverage
  recorded event.
- **FRAME_INCOMPATIBILITY_TEST@v2 §2.D pre-registration**: pre-registered
  spec changes that get retracted during measurement should generate
  self-dissent records automatically.
- **decisions_for_james.md**: narrative-level retraction entries (e.g.,
  F044 retraction recommendation) compose with ledger entries; the
  ledger gives the structured-event view, decisions_for_james gives the
  narrative reasoning.

## Operational use

1. **Discovery**: "what was the most recent self-dissent on a Pattern-30
   classification?" → `list_dissent_by_target_kind('verdict') | filter
   relates_to PATTERN_30`.
2. **Substrate-discipline metric**: rate of self-dissent per session per
   author. Suspiciously low rate prompts a calibration-check. Healthy
   rate is project-specific but ~1-2 per active session is the
   2026-04-22/23 baseline.
3. **Cold-start orientation**: future Harmonia reads recent dissent
   records to learn which kinds of errors recent agents caught
   themselves making. Calibrates first-pass posture.

## Implementation path

1. **First-pass module**: `agora/dissent_ledger.py` (~150 LOC, mirrors
   `agora/symbols/anchor_progress.py` style and disciplines). Worker task.
2. **Seed initialization**: one-shot script reading the 6 seed events
   above into Redis. Mark each with `seeded_from_md` provenance flag.
3. **Future automation**: a sweep that watches `agora:harmonia_sync` for
   posts with `type ∈ {DISSENT_SELF, CORRECTION, REVISE_VERDICT,
   DISSENT_SELF_REVERSING_PRIOR, RETRACT}` and auto-records them. Defer
   until manual recording demonstrates value.

## Cross-references

- `feedback_self_dissent.md` (memory) — defines the discipline.
- `harmonia/memory/concept_map.md` axis 1 — sprawl observation #7 (this
  design closes it as a design + seed; module implementation pending).
- `agora/symbols/anchor_progress.py` (sessionA prototype) — sister
  sidecar architecture; mirror its API style.
- `harmonia/memory/symbols/CANDIDATES.md` §ANCHOR_PROGRESS_LEDGER —
  parallel candidate; both are sidecar instances.
- Sync IDs of seed events: 1776906584732, 1776906957066, 1776906776069,
  1776906965662, 1776907131595, 1776907210877, 1776907283202.

## Discipline note (Pattern-17)

Like all sidecars, this MD documents the schema and seeds — the
authoritative source of truth would be the Redis HASH (once
implemented). If the module ships, the convention should be: NEVER edit
this MD as the source-of-truth for active dissent records; the MD's role
is design-doc + initial seed, not ledger contents. After module ships, a
companion `dissent_ledger_view.md` (auto-generated) would render the
Redis HASH for human discovery, in the same way `lineage_registry_view.md`
renders `LINEAGE_REGISTRY` from Python.
