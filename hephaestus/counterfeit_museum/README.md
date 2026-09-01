# Counterfeit Museum

Known ways to score on a reasoning task without performing the reasoning. Every Master Smith reads
this before minting; every apprentice attempt is measured against the relevant exhibits. Vocabulary
from `aporia/docs/DOCTRINE_counterfeit_battery_and_ladder_2026-08-25.md` (eight classes: retrieval,
parse, answer, search, budget, distribution, composition, evaluation).

| # | Exhibit | Class | Where it lives | Falsifier that catches it |
|---|---|---|---|---|
| 001 | **Keyword `'vacuous' in cl`** — `if 'true' in cl and 'vacuous' in cl: return (1.0, "structural:vacuous_truth")`; 98 of 375 files in `agents/hephaestus/forge_v4/` | answer | the forge's own tree (E3, 2026-09-01) | NEARMISS_VACUOUS_WORD dev kind: the word appears, domain non-empty, claim false; keyword scorer answers yes |
| 002 | **Constant-Yes scorer on Apollo's canary** — `vacuous_truth` canary has 2 prompts / 5 tasks, correct first token "Yes" 5/5; a text-blind scorer scores 5/5 | evaluation (degenerate target) | `apollo/scripts/gen_clean_canary_v01.py:191-208`; measured by `aporia/iq/probe_synth1_target_degeneracy.py` | never read a mint on this canary; use a held-out generator with balanced yes/no/undetermined |
| 003 | **`'no' ∧ 'every' → yes` regex** — the obvious first heuristic | answer / parse | every cheap-model attempt so far (see `mint_queue/MINT-0001/attempts/`) | NEARMISS_NO_KEYWORD (a 'no' on a different noun phrase), NONEMPTY_UNIV_ALL (no 'no', answer yes), every→some flip |
| 004 | **Retrieval reported as synthesis** — "let the forge mint `all_but_n`" when `fp.all_but_n` existed since v1 | retrieval | caught before it ran, `aporia/docs/CYCLE_156S_SEVERED_LIBRARY_2026-08-24.md` | mechanical absence check against v1 catalog + forge library + every prior registry; delta class fixed in advance |
| 005 | **Template-matched parser passing as capability** — Apollo routed on `problem_text.startswith("is ")`; blind battery 40/42 abstained | distribution | `apollo/cycles/campaign_20260825/E9_FINDINGS.md` | a battery written by a different author (Charon) |
| 006 | **Concentration gate that an all-zero tool passes** — `forge/tester.py:410-420` tests contribution share, so a tool whose primitives all have delta 0.000 passes; `FAIL_ABLATION` fired 0 times in 198 verdicts | evaluation | `roles/Lexis/notes/G1_ABLATION_2026-08-25.md` | gate on the impact threshold the tester already computes (`min_ablation_impact` 0.20) |
| 007 | **Byte-identical PASS verdicts** — two T2 tools with identical five-seed score vectors `[0.3333, 0.5, 0.375, 0.375, 0.4167]` | evaluation (instrument artifact) | `roles/Lexis/notes/G0_FORGE_RATCHET_2026-08-25.md` | dedupe verdicts on their measurement vector before counting PASSes |

**Adding an exhibit:** one row, with the falsifier that catches it. An exhibit without a falsifier is a
complaint, not a museum piece.
