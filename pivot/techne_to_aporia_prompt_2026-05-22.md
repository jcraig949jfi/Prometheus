# Techne → Aporia paste-ready prompt

**Date:** 2026-05-22
**Context:** Techne is running the Theseus substrate loop (Fire #46 at time of writing, 200M+ lifetime records). Per `pivot/persona_seed_prompts_2026-05-21.md` Techne idea #5 (self-claim verification), Techne has scanned her own synthesis docs and produced 48 candidate claims for Aporia to verify. This closes the demand-supply loop — Penelope (Ergon) reports Theseus substrate is 90% duplicates downstream, and the substrate's claim space is saturated on a closed catalog. Techne's own synthesis writing is the next-best self-generated demand source for Pythia DR.

The ticket has been filed at `aporia/meta/queue/aporia_inbox.jsonl` as `T-2026-05-22-techne-self-claims-001`. This paste-ready prompt is the more direct delivery channel if Aporia's inbox loop isn't picking up new tickets.

---

**Paste-ready prompt for Aporia (single block):**

You are Aporia. Techne just filed `T-2026-05-22-techne-self-claims-001` in your inbox at `aporia/meta/queue/aporia_inbox.jsonl` — read it. The substantive ask: Techne ran `theseus/scripts/scan_synthesis_claims.py` over her own synthesis docs (pivot/techne*.md, pivot/substrate*.md, pivot/strategic_pivot*.md, pivot/prometheus_synthesis*.md, pivot/killembedding*.md, pivot/persona_seed_prompts*.md) and extracted 48 quantitative-claim candidates into `techne/handoff/aporia_outbox/techne_self_claims_2026-05-22.jsonl`. Each row: `{claim_id, source_path, claim_text, pattern_kind}` where pattern_kind ∈ {conjecture, implication, numeric_bound, rate_or_percentage, magnitude_change, other_quantitative}. Your job is three steps, in order. **First, triage**: open the JSONL, classify each claim into one of {VERIFIABLE, WORKFLOW_NOT_CLAIM, AMBIGUOUS, ALREADY_VERIFIED}. Most of the 48 will be workflow-style ("we plan to do X by date Y", "this implies Techne should do Z") — those go to WORKFLOW_NOT_CLAIM and drop out. Filter aggressively; we expect 5-15 truly verifiable claims, not 48. Write the triage decisions back to `aporia/handoff/techne_self_claims_triage_2026-05-22.jsonl` with `{claim_id, triage, reason}` per row. **Second, dispatch the VERIFIABLE subset via Pythia DR**: for each verifiable claim, formulate a DR query that asks "is this claim supported by current literature?" Use the existing `aporia/docs/gemini_research_queue/` mechanism — append each query as a markdown file with the claim_id embedded in the YAML frontmatter so verdicts route back. Tag conjecture/implication claims for full DR; numeric_bound/rate may just need lit-search. Don't blow your DR budget on weak claims — pick the 5-10 highest-value. **Third, wire verdict-back to Techne**: when each Pythia DR report lands at `aporia/docs/deep_research_reports/<date>/<id>.md`, parse the verdict and file a closeout ticket to `aporia/meta/queue/techne_inbox.jsonl` with `claim_id` in payload + verdict text + Pythia DR report path. Techne's loop reads techne_inbox and will update synthesis docs (or kill claims) accordingly. **Why this matters**: Theseus substrate is saturated on a closed catalog (Penelope reports 90% downstream dups; Techne Fire #46 saturation telemetry confirms). Techne's synthesis writing is the next demand source — claims she has made in pivot writing that lit can verify or falsify. Confirmed → strengthens future substrate. Falsified → becomes AA candidate. Either outcome is substrate value. **Log work**: after triage, call `log_work(stage="aporia_techne_claim_triage", summary="<n> verifiable of 48 candidates, <n> dispatched to Pythia", output_path="aporia/handoff/techne_self_claims_triage_2026-05-22.jsonl")`. After each Pythia verdict lands, `log_work(stage="aporia_verdict_to_techne", summary="<claim_id> verdict=<CONFIRMED|FALSIFIED|INCONCLUSIVE>")`. No preamble; the inbox ticket has full context including the scanner_summary and rerun_command. Start with triage — that's the unblock.

---

## Why this is high leverage

- **Closes the demand-supply loop**: Penelope's 90% downstream dups + Fire #46 saturation telemetry both confirm Theseus is producing redundant substrate from a fixed catalog. Techne's synthesis claims are the next-best demand source that doesn't require a catalog expansion (which is the longer-horizon mathlib import swing).
- **Cheap on Aporia's side**: triage is human-scale (48 claims, ~30 min to classify), dispatch is 5-10 DR queries (well within the 20/day cap noted in `feedback_use_or_lose_research_tokens`).
- **Closes the loop in 2-4 days**: Pythia DR turn-around is hours per query. Verdicts come back within a few cycles.

## Tracking

If Aporia activates on this prompt, the brief should show one or more of:
- `aporia_techne_claim_triage` event with N verifiable count
- `aporia_verdict_to_techne` events as DR reports land
- New ticket(s) in `aporia/meta/queue/techne_inbox.jsonl` with claim_id payloads

If none of these fire within 24h, the prompt didn't land — consider direct paste into Aporia's session.
