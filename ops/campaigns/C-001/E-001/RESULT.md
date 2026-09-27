# E-001 RESULT -- B6: Who / Where / What (closed 2026-09-27)

Question: when reproduction occurs, can we distinguish the executing entity, the execution location, the code material, and the
material governing the inherited writes?

## Answer: yes, in all three engines. They separate differently, and that difference is the result.

| engine | where the three referents come apart (measured) | what the engine records natively |
|---|---|---|
| BEE | WHERE != WHAT: writers copy themselves into the window and run the copy. In r038751, 27,083 of the 28,163 births that look foreign-governed by location are governed by the writer's own material (1,726,650 writes by self-copied code vs 941 by foreign code). In r016299, genuine foreign-material governance exists: 8,166 births | WHO (writer), WHERE (pc region). WHAT only by FULL replay |
| NPE | WHO != WHAT: each organism's thread runs the other's code. In 26.4% of 481 directed writes (34 pair births) the writing thread ran the other organism's code; at the majority level WHO != WHAT in 13/34 births. Relocated code (WHERE != WHAT) is rare: 3.5% | WHO (prov / prov_lit). WHERE and WHAT only by observation-only replay |
| Archaeon | both occur, and neither misleads Archaeon, because WHAT is native. Self-copying: no divergence detected (19,615 births). Block-15 hosting: 2,570 of 3,594 resident-emitting births run resident material in place (WHO != WHAT); 1,024 run host material relocated into the neighbour region (WHERE != WHAT) | WHO, WHERE (exec_foreign), WHAT (taint labels) |

The same conceptual question exposes different causal structure: location decoupling in BEE, thread decoupling in NPE, both in
Archaeon. None of the three is "the" B6. Forcing one vocabulary onto all three hides two of them.

Mechanistic lead, not a proof: in NPE, host-conditioned births (the donor cannot rebuild a random victim, P-11 C2 false; 25 births)
show cross-execution in 46% of directed writes, against 11% in the 9 births where the donor can. That fits the donor using the host's
material as code.

## Instrument consequence (T-005): contract v0.3
Governance is recorded under three fields: WHO context_authorship, WHERE code_location_share, WHAT write_governing /
execution_share. J21 forbids filling WHAT from WHO or WHERE. The adapters are re-mapped. 79/79 tests pass on M2 and on ubu001.
See T-005_DECISION.md.

## Historical interpretations

| earlier interpretation | status after E-001 |
|---|---|
| ENVGATE-01 R2: an inert host executes the resident's copier code and emits the resident's genome | **SURVIVES** (Archaeon measured material). Refined: that route covers 71.5% of block-15 hosting births; the other 28.5% run the host's own relocated material, a second route to the same outcome |
| PORTABILITY-01 AN1: BEE executor/material decoupling (233,499 births) | **CHANGES**: mostly a location-accounting artifact; a real minority of foreign-material governance remains (substrate phenomenon) |
| BEE native "own code" / SR criterion (pc < L) | **REINTERPRETED** as a WHERE claim. Whether BEE's SR under-counts self-replication run from self-copied code is **UNRESOLVED** (-> TH-002). No BEE verdict is rewritten |
| NPE native "donor authored" (prov) | **REINTERPRETED** as WHO. It names a different material than the governing code in 26.4% of directed writes |
| PORTABILITY-01 / v0.2 NPE continuity and AN3 (host-conditioned, 16/34) | **SURVIVES**; now has a cross-execution association (-> TH-003) |
| v0.2 defects D2 (BEE adapter) and D3 (NPE adapter labelling) | **CONFIRMED field-mapping errors; FIXED** in v0.3 mappings |
| v0.2 B6 statement ("engines persist WHO or WHERE, rarely WHAT") | **CONFIRMED** by measurement in all three engines |
| AN8 NPE donor writes not necessary in situ (11/34) | **UNRESOLVED** (-> TH-004) |
| BEE writes by code outside both modelled regions (pc >= 2L; 528,897 in r016299) | **NOT_IDENTIFIABLE** by the current probe (-> TH-005) |

## What this does NOT establish
- BEE: 2 runs, chosen for being rich in "decoupled" births, not a random sample.
- NPE: 34 births, one specimen.
- Archaeon's panel: one resident, 63 hosts. The divergence counts are exact multiples of 256, which suggests a few hosts on every input.
- No universal claim about "all substrates".

## Tasks and attempts
All in TASKS.md, including the failed attempts (T-001 A-001, T-004 A-001), which were caused by my own script defects. Execution ran on
ubu001 and ubu002; verification against M2-only evidence and the Git relay ran on M2.

Experiment status: **CLOSED**. Open lines were moved to Threads TH-002 .. TH-006 and are not pursued here.
