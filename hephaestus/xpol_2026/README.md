# xpol_2026 -- cross-pollination replay with 2026-09 models

Currency: 2026-09-19 (runs in progress; see runs/*/DONE.json for what has finished).
Operator directive (2026-09-19, verbatim intent): "One of the original premises was that we
could come up with wacky novel solutions by cross pollinating bizarre fields of science and
asking models to produce a weird combo solution. ... take a 100 or so of the ones that
produced interesting results and try the same experiment with the newest models. Explore.
Do not pollute what was previously done. Extract."

Temporary mission for the Hephaestus seat; it does not replace the 2.0 position in
roles/Hephaestus/journal/2026-09-19.md. Nothing under agents/ is modified; this directory
is the only writer.

## The 1.0 experiment being replayed (frozen corpus, read-only)

    agents/nous/runs/*/responses.jsonl   5,918 rows, 5,727 unique concept triples
                                          (95 concepts x 18 fields), 2026-03-24..27,
                                          nvidia/nemotron-3-super-120b (3 by qwen3.5-397b)
    agents/hephaestus/ledger.jsonl        6,661 rows: 385 forged / 6,276 scrap
                                          (2,861 api_call_failed), 2026-03-24..05-28
    agents/hephaestus/forge/*.py          366 tools + json (March era, 15-trap certificates
                                          shown vacuous by the Necropolis, 2026-09-10)
    agents/hephaestus/scrap/*.py          2,648 failed candidates
    agents/hephaestus/novelty_scores.json 412 behavioural-novelty rows

Two prompts, both era-versioned in templates/ (sha256 in MANIFEST.json):
Nous (analysis of a triple -> mechanism + 4 ratings) and CODE_GEN (analysis -> a
`ReasoningTool` class, numpy + stdlib, with frame suffix B..H from 2026-03-28 on).

## What is extracted (packets/selection.json, 114 packets)

Six preregistered lenses (extract.py docstring): L1 honest-era forged 26, L2 March forged
acc>=.50 22, L3 near-miss scraps 30, L4 behavioural novelty>=.70 6, L5 Nous-top never fairly
attempted 20, L6 Nous composite>=8.0 10. No operator list of "interesting" exists; the
lenses are proxies and every packet names its lens. 68 packets carry their original code
(sha256); the 26 honest-era (2026-04/05) tools were forged on M3 and never committed --
their ledger rows survive, their code does not.

## The replay (replay.py)

Stages per packet: O (original code re-scored on the honest ruler), N (Nous prompt,
reconstructed verbatim with the concept descriptions of the run's commit), C_new (CODE_GEN
with the arm's own analysis), C_orig (CODE_GEN with the ORIGINAL 2026-03 analysis held
constant). Post-processing is the 1.0 chain byte-for-byte (legacy_helpers.py is
AST-extracted from hephaestus.py; code_extractor / validator imported from the legacy
source). The ruler is the 1.0 honest battery: trap_generator_extended n_per_category=2
seed=42, 186 traps / 89 categories / tiers R1-R6.

Floors (floors.json, computed before any call):
    position-majority decoy (always index 1)  0.4032   <- the cheapest counterfeit
    NCD baseline (the 1.0 pass comparator)     0.3925 / cal 0.4516
    random ranking (200 seeds)                 mean 0.3252, p95 0.3817, max 0.4086
    chance                                     0.3238
A tool below 0.41 has not been shown to do anything a constant index does not.

Arms: fable51 (claude -p, tools off; subscription CLI -- the raw Anthropic key is unfunded,
so this is an agent harness with a fixed system prompt, temperature not settable);
gpt6astra (openrouter:openai/gpt-6-astra, DEFINED BUT BLOCKED: 402 no credits, 2026-09-19);
gemini (gemini-3.6-flash) and groq (gpt-oss-120b) as free 2026-09 cheap-model contrasts.

Deviations from 1.0, all deliberate and recorded per call: Coeus enrichment omitted;
hosted arms get 4x the 1.0 token budget (thinking tokens); PYTHONUTF8=1 (1.0 scrapped 85
tools on cp1252 UnicodeEncodeError -- an environment artefact its own sanitizer was
written to remove); claude_cli temperature unset.

## Known so far (pilot, XP-001 Quantum Mechanics + Neural Plasticity + Model Checking, frame D)

    fable51  C_new 0.5161 (pilot)  0.3656 (full run, same prompt)  C_orig 0.4731
    gemini   C_new 0.3602  C_orig 0.4086
    groq     C_new 0.4086  C_orig scrap (syntax)
    original 1.0 tools on the same ruler: median 0.355, max 0.473 (n=65)
Single samples of the same prompt differ by 0.15 on this arm; read nothing from one draw.
