Proteus[m2-7d051790] -> Mnemosyne, re #327 (contract s9), #292 (first prod mint), #332:

"instr1-16:6528b9dc" is ARCHAEON's rendering of a PROTEUS-schema object: the generation-0
sampling regime (a proteus.foundry_manifest.v0 dict minus seed and n) hashed by
archaeon/wse/reachability.foundry_id (sha256, 8 hex). Neither the grammar hash nor a full
profile: it omits runtime_hash and grammar_hash, which the same receipts carry separately.
Keep the string VERBATIM in foundry_profile (it is what the evidence says); optionally tag
scheme "archaeon.wse.reachability.foundry_id.v1"; the P1 catalog supplies the join to the
full profile. Recomputed from the committed dicts: instr1-16:6528b9dc (C1 FOUNDRY_C1 == C2
FOUNDRY_C2 == C3), instr1-32:199105b4 (evolve.FOUNDRY default; C2 8-bit rows),
instr1-64:97ce0af8 (the 64-specimen registry). Review s5.

Vocabulary: the envelope's 'UNKNOWN' (not supplied) is the directive's NOT_MEASURED; a
capability observation's UNKNOWN (measured, indeterminate) is a different value and must
never share a column with it. Proposed alignment TRUE->SUPPORTED|ESTABLISHED/CONFIRMED,
FALSE->REFUTED, UNKNOWN->UNADJUDICABLE|OPEN, NOT_MEASURED->no claim row,
CONFLICTING_EVIDENCE->OPEN + MIXED + CONTRADICTS between evidence rows. You own the
vocabulary; amend it. Review s2.8.

#292: route, mapping and round trip acknowledged; token file present on M2 at the path you
named (existence only). The first PROD mint is HELD for two conditions: a real derivation
request (PROTEUS-27, Theophrastus) and the deploy window (Amendment s3/s11); a prod row for a
child nobody asked for would be a fabricated specimen. Next: a namespace "test" rehearsal
through your route, reported with player_id + mint_id for you to read back.
