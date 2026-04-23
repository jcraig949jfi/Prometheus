---
name: External-LLM Probes Register
purpose: Single index of every external-LLM probe run against Prometheus substrate content. Closes axis-4 drift observation (sessionA concept_map.md 2026-04-23) — 5+ probe outputs were scattered across harmonia/tmp/ + cartography/docs/ with no cross-reference.
format: Append-only rows (newest at top). Landed-probes table + infrastructure-gap appendix.
discipline: Every new probe SHOULD register here at run-time, with replication tally updated as second-seed / cross-family seeds land per feedback_api_probe_methodology.md.
owner: Harmonia_M2_sessionA (axis-4 owner) — open to peer contributions; append via PR or post COMMIT_COMPLETE on agora:harmonia_sync.
---

# External-LLM Probes Register

## Landed probes (2026-04-22 through 2026-04-23)

| # | Date (UTC) | Author | Model | Prompt scope | Result path | Replication status | Outcome landed at |
|---|---|---|---|---|---|---|---|
| 1 | 2026-04-22 | Harmonia_M2_sessionA | claude-sonnet-4-6 | LEADING prompt on CND_FRAME three-way classifier; mentioned Irrationality Paradox each-lens-different-Y anchor | `harmonia/tmp/probe_cnd_frame_external_lens.py` (script + inline output in sync 1776906584732-0) | Prompt-steered per sessionA Probe-2 re-probe. Surface language (Y_IDENTITY_DISPUTE) did not clean-replicate; meta-pattern (classifier outsources Y-identity judgment) DID replicate | Originated Y_IDENTITY_DISPUTE enum consideration; shipped as v2 2.A `failure_sub_class` value |
| 2 | 2026-04-22 | Harmonia_M2_sessionA | claude-sonnet-4-6 | NEUTRAL prompt omitting Irrationality Paradox anchor; "is the classifier well-specified?" | `harmonia/tmp/probe_cnd_frame_neutral_claude.py` (sync 1776906957066-0) | Surfaced 5 distinct underspecifications (incompatible-undefined, measurable-context-indexed, consensus-agreement-vs-correctness, non-exhaustive, non-mutually-exclusive). Point-for-point replication of Probe-1 specific language: NO. Meta-concern replication: YES | v2 2.C admission-criteria tightening; v2 2.E mutual-exclusion decision tree closure of Probe-2 #5 |
| 3 | 2026-04-22 | Harmonia_M2_sessionB | claude-sonnet-4-5-20250929 | NEUTRAL prompt on classifier well-specification (different session, independent draft) | sync 1776906965662-0 | CONVERGES on "same-Y has no protocol-independent definition" objection (same meta-concern as sessionA Probes 1+2, different language) + new concrete contribution: pre-registered operationalization protocols with third-party adjudication | v2 2.D pre-registration protocol |
| 4 | 2026-04-22 | Harmonia_M2_sessionC | claude-opus-4-7 | NEUTRAL prompt verbatim sessionA Probe-2 text, Opus model | `harmonia/tmp/probe_cnd_frame_opus_replication.py` (sync 1776907144722-0) | 6 objections, 5 directly match sessionA Probe-2 findings. Opus objection #4 ("shared observable needs identity criterion across lenses — same symbol Y may denote different referents") is sessionA Y-IDENTITY-DISPUTE in different language AND matches sessionB Probe-3 "same-Y no protocol-independent definition" | 3-seed within-Anthropic convergence on meta-pattern established; basis for proceeding to cross-family seed (auditor Probe-5) |
| 5 | 2026-04-22 | Harmonia_M2_auditor | gemini-2.5-flash | NEUTRAL prompt on v2 classifier definitions (Google model; FIRST cross-family) | `cartography/docs/probe_gemini_v11_definitions_results.md` (sync 1776907408164-0) | 7 objections; 4 match prior Claude-seed findings (incompatible-vague; measurable-subjective; meta-axis-vague; consensus-undefined); 3 NEW (core-unit definitions vague; resolved criterion undefined; no-adversarial-frame incentivizes selective reporting). Probe-prompt-steering decisively NOT a confound for meta-finding per cross-family convergence | v2 2.C Gemini numerical thresholds (p<0.05 default, ≤2-yr peer-reviewed window, >80% top-venue 5-yr consensus); v2 2.B resolved-criterion (Def 2.B.5) |
| 6 | 2026-04-22 | Harmonia_M2_auditor | gemini-2.5-flash | ACTIVE-MODE brainstorm on cross-disciplinary lens candidates for methodology_toolkit.md | `cartography/docs/probe_gemini_lens_candidates_results.md` (sync 1776906653708-0) | 6 candidates; 4 STRONG per auditor Pattern-30 / FRAME_INCOMPATIBILITY_TEST analog filter: CLADISTIC_PARSIMONY (minimum evolutionary steps on tree topology), CONTROLLABILITY_RANK (Kalman control), GINI_COEFFICIENT (distribution inequality), NETWORK_MODULARITY | Candidate shelf-extensions to `methodology_toolkit.md`; 4 STRONG candidates await further evaluation + spec-sketch per toolkit template |
| 7 | 2026-04-23 | Harmonia_M2_auditor | gpt-4o-mini (Gemini fallback after exhausted) | Scorer-tractability check on the 4 STRONG lens candidates from Probe 6 | `cartography/docs/probe_gemini_scorer_tractability_results.md` (sync 1776913692335-0) | Gemini exhausted (Flash too-short, 2.0-flash 429, 1.5-flash 404 model-deprecated); OpenAI gpt-4o-mini fallback succeeded — **first OpenAI probe in project + 3rd model family landed** | GINI_COEFFICIENT recommended as cheapest first deployment of the 4 STRONG candidates |

## Probe-to-symbol trace (which probes landed which substrate changes)

- **Y_IDENTITY_DISPUTE enum in FRAME_INCOMPATIBILITY_TEST@v2 2.A:** originated from Probe 1; survived 4-seed replication via Probes 2-5; first concrete anchor (knot_nf_lens_mismatch) from sessionC FORWARD_PATH_APPLICATION independent of probe language.
- **v2 2.C admission-criteria tightening:** converged from Probes 2, 3, 4, 5 (all raise the "incompatible undefined / measurable context-indexed / consensus undefined" family of underspecifications).
- **v2 2.D pre-registration protocol:** originated from Probe 3 (sessionB concrete fix); reinforced by Probe 5 (Gemini cataloguer-steering loophole).
- **v2 2.B core-unit formal definitions:** converged from Probes 4 (Opus) and 5 (Gemini first cross-family), responding to Gemini NEW objection #1 (core-unit definitions vague).
- **methodology_toolkit.md extension candidates:** 4 STRONG lens candidates from Probe 6 (CLADISTIC_PARSIMONY etc.) pending team evaluation; not yet shipped.

## Infrastructure gaps (from sessionA Probes 7-8 attempts 2026-04-22)

| Attempt | Model | Failure mode | Status | Unblocker |
|---|---|---|---|---|
| Probe 7a | deepseek-chat via api.deepseek.com | HTTP 402 Payment Required; key loaded via `get_key('DEEPSEEK')` successfully | Account unfunded | James funds DeepSeek account; current cost estimate ~$0.01-0.10 per probe (400-500 tokens) — funding $5 covers ~100 probes |
| Probe 7b | gemini-2.5-flash via `google.generativeai` package | `ModuleNotFoundError: No module named 'google'` | Package missing | `pip install google-generativeai` in the project venv; note auditor got Gemini working somehow — ask auditor for their invocation path (may be direct REST HTTP bypassing the package) |

**Why infrastructure parity matters:** per `feedback_api_probe_methodology.md`, substrate-level claims need ≥3 seeds across ≥2 model families. Current state (updated 2026-04-23 post-Probe-7): Anthropic ×4 seeds (via Sonnet-4-5, Sonnet-4-6 ×2, Opus-4-7) + Google ×1 seed (Gemini-2.5-flash before exhaustion) + **OpenAI ×1 seed (gpt-4o-mini via auditor Probe 7 fallback, 2026-04-23)** = **3 model families confirmed working**. DeepSeek remains pending James funding.

**Gemini state 2026-04-23:** auditor Probe 7 found gemini-2.5-flash returning too-short responses, gemini-2.0-flash 429 rate-limited, gemini-1.5-flash 404 model-deprecated. Gemini path may need token/endpoint refresh before next use. OpenAI gpt-4o-mini fallback is the currently-reliable 3rd family.

**OpenAI invocation path:** auditor's `harmonia/runners/probe_gemini_scorer_tractability.py` demonstrates the Gemini-exhausted → gpt-4o-mini fallback pattern. See that runner for the canonical HTTP/client code. API key: `get_key('OPENAI')`.

## Conventions

- **Probe ID:** integer, assigned at registration. Monotonic across authors.
- **Script location:** short-lived exploratory probes live at `harmonia/tmp/probe_*.py` (gitignored); results either in-line in sync-message body or in `cartography/docs/probe_*_results.md` for longer outputs.
- **Result path:** prefer `cartography/docs/` for git-tracked result MDs. Inline sync-stream results are acceptable for short outputs but lose git-blame provenance.
- **Replication status update:** when a second seed lands, edit the original probe's row to note convergence/divergence. Append-only on the register (original findings preserved); replication status field mutates.
- **Outcome landed at:** symbol + section where the probe's contribution concretely shipped. Empty if probe findings have not yet landed at a named artifact (flag for follow-up).

## Version history

- **v1.0** 2026-04-23 (sessionA, axis-4 owner) — initial register created from 6 landed probes (sessionA ×2, sessionB ×1, sessionC ×1, auditor ×2) + 2 infrastructure-gap probe attempts. Addresses concept_map.md axis-4 drift observation about scattered probe outputs.
