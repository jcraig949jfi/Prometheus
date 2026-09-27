# T-005 -- semantic change to the causal lens and adapters (2026-09-27)

Basis: T-004_RESULT.md. Decision: **yes, a semantic change is needed, and it is narrow.**

## The change (contract v0.3 = v0.2 + three-referent governance)
Implementation: `archaeon/causal_lens/schema_v03.py` (v0.2 frozen and untouched; v0.3 subclasses it and does not mutate it).
- "Which code governed the copy" is recorded under three separate fields, each with a declared `referent`:
  * `context_authorship` = WHO (executing context or body);
  * `code_location_share` = WHERE (location of the executing instruction);
  * `write_governing` / `execution_share` = WHAT (the material of the executing instruction). The meaning is unchanged from v0.2 and
    is now enforced.
- **J21:** a WHAT field may not be filled from a WHO or WHERE reading. If an engine records only WHO or WHERE, write_governing is
  NOT_IDENTIFIABLE.
- **J22:** the autonomy names AUTONOMY_WRITE / AUTONOMY_EXEC are WHAT claims. Location- or context-based autonomy must say so:
  AUTONOMY_WRITE_LOCATION, AUTONOMY_WRITE_CONTEXT.
- Limit: J21 checks the declared referent and word-bounded source wording. A mis-declaring adapter could pass, so the four real
  adapters' declarations are regression-tested on committed fixtures.

## Adapter mappings (`archaeon/causal_lens/adapters_v03.py`)

| engine | native field | v0.3 meaning |
|---|---|---|
| BEE | by_own_code (copy op pc < L), own/win/other steps | WHERE only. Never write governance |
| BEE | writer id | WHO |
| BEE | FULL replay code-byte provenance (T-001/T-002 probe) | WHAT; without it, write_governing = NOT_IDENTIFIABLE |
| NPE | prov / prov_lit | WHO only. Never write governance |
| NPE | T-003 probe (code-byte provenance at the pc) | WHAT and WHERE; without it, write_governing = NOT_IDENTIFIABLE |
| Archaeon | taint fetch labels (exec_counts) | WHAT (native) |
| Archaeon | exec_foreign | WHERE |

## What each engine can claim WITHOUT a special replay, under v0.3
- **Archaeon:** WHO, WHERE and WHAT, all native. For 'mixed' executions, write governance is not decided per write.
- **BEE:** WHO and WHERE from preserved rows. WHAT requires a FULL replay with the code-material probe.
- **NPE:** WHO from lineage/p11. WHERE and WHAT require the observation-only replay (T-003).

## Tests
- `archaeon/tests/test_causal_lens_v03.py`: 8 tests.
  * Synthetic: WHERE-only engine; location-sourced and context-sourced WHAT rejected; missing or mismatched referent rejected;
    location autonomy under the WHAT name rejected.
  * Real fixtures committed in `archaeon/tests/fixtures_v03/` (108 KB): 60 BEE r038751 rows with their code-provenance, all 34 T-003
    NPE births, and 200 block-13 Archaeon events. They check that location-only BEE never yields write governance, that FULL BEE
    does, and that NPE WHO != WHAT holds at the majority level in 13/34 births.
- With the v0.2 (44) and corpus (27) suites: 79/79.

## What this decision deliberately does NOT change
- Counterfactual tests (P-11 C2/C4/C5, ENVGATE arms): unaffected. They are interventions, not governance readings.
- Heredity edges and material contributors: unaffected. B6 is about the CODE that governed; the value material of the child is a
  separate, already separate, question.
- B1 continuity: that is E-002.
- No engine's native field or verdict is renamed in its own files. The mapping lives in Archaeon's adapters.
