# Causal lineage contract: v0.1 -> v0.2 changelog and migration

v0.1 (CAUSAL_LINEAGE_CONTRACT.md, schema.py, corpus.py, frozen 13cdec715) is unchanged and still runs. Its tests still pass.
v0.2 lives beside it: CAUSAL_LINEAGE_CONTRACT_v0.2.md, schema_v02.py, corpus_v02.py, upgrade_v01.py.

| v0.1 | v0.2 | why | upgrade rule (upgrade_v01.py) |
|---|---|---|---|
| ENTITY | BODY + IDENTITY (assigned, with from/until) | B2 | each ENTITY e -> BODY e + IDENTITY id:e; prop body_identity_split = NOT_IDENTIFIABLE (v0.1 cannot tell a rename from a new body) |
| owns / hosts / labelled_parent (E->E) | carries / hosted_by (T->BODY) / labelled_parent (IDENTITY->IDENTITY) | B2 | renamed; labelled_parent re-pointed to the identities |
| executor, host | executor_body (+ executor_identity), host_body | B2 | copied; values now reference BODY |
| executed_material, governed_by | write_governing + execution_share | B3 | both set to NOT_IDENTIFIABLE; the v0.1 value is kept under `v01`; governed_by edges -> execution_share edges tagged v01_role |
| material_origin | ancestry_origin (+ made_in / located_in, LOCATION nodes) | B4 | copied; made_in absent (never asserted from ancestry) |
| child_contributors | factual_contributors (+ CF_TEST nodes for counterfactuals) | B5 | copied (v0.1 contributors were realized-trace or native claims) |
| resulting_hu | hu_continuity + resulting_hu (+ architecture_class, ARCH nodes) | B1 | resulting_hu copied; hu_continuity = it for REPRODUCTION/AMPLIFICATION, NONE for ORIGINATION, else NOT_IDENTIFIABLE |
| ESTABLISHMENT.resulting_hu | ESTABLISHMENT.persisting_object (HU / ARCH / declared) | B1 | copied as an HU object |
| YES/NO/NOT_IDENTIFIABLE | + ILL_POSED in identity-valued fields only, with a justification over complete evidence | B1 | none (v0.1 never produced it) |
| bare booleans | role-suffixed autonomy (AUTONOMY_WRITE / _EXEC / _MATERIAL); no bare sufficient/necessary | B3, B5 | none |
| I1-I12 | J1-J20 (J1-J5, J12, J18-J20 carry I1-I12; J6-J11, J13-J17 are new) | all | -- |

Guarantees tested (archaeon/tests/test_causal_lens_v02.py):
- every v0.1 fixture upgrades to a valid v0.2 graph;
- the heredity edges and establishments are unchanged;
- each v0.1 claim is kept verbatim under `v01`;
- every v0.1 cheat, once upgraded, is still rejected.

## v0.2.1 amendment (2026-09-27, BEFORE any adapter was ported or any regression result existed)
`continuity()` returned NOT_IDENTIFIABLE whenever any contributor share was unknown, even when a known contributor held a STRICT majority
that the unknown mass could not overturn (for example, 0.6 known own + 0.4 unknown). The contract text requires NOT_IDENTIFIABLE only when
incomplete evidence could change the answer. Fix: a strict known majority (> threshold, unique) decides; otherwise any unknown mass
-> NOT_IDENTIFIABLE, and still never ILL_POSED. Tests added. Contract text unchanged.
