# Coeus Necromancer evidence (2026-09-10)

Reproducible scripts + their captured outputs for `../coeus.dossier.json`.
Run from repo root: `python engine/necropolis/dossiers/coeus_evidence/<script>.py`
(each stubs `openai` so `agents/hephaestus/src/hephaestus.py` imports without the package — LAW N14 apparatus control).

| script | question | result file |
|---|---|---|
| `coeus_signal_test.py` | Do the SHIPPED scores (`agents/coeus/graphs/concept_scores.json`) rank forge outcomes above chance, in-sample and out-of-sample? Is the autopsy's "positions change" observable informative? | `coeus_signal_result.json` |
| `coeus_within_regime.py` | Within the pre-2026-03-27 forge regime, do concept indicators predict forge success held-out (stratified 5-fold)? What does the ledger say about the post-03-27 collapse? | `coeus_within_regime_result.json` |
| `coeus_attacks.py` | Four attacks on the in-sample positive: exclude `api_call_failed` rows; leave-one-Nous-run-out; leave-one-forge-day-out; within-single-forge-day CV. Plus run×forge-day crosstab. | `coeus_attacks_result.json` |

Order matters: each script was written AFTER the previous one's result, as a targeted attack. Read the dossier's
`autopsy.kill_boundary` for the synthesis. Data inputs: `agents/nous/runs/*/responses.jsonl` (5727 entries),
`agents/hephaestus/forge/*.json` via `hephaestus.load_ledger()` (6651 entries), `agents/coeus/graphs/*.json`.
