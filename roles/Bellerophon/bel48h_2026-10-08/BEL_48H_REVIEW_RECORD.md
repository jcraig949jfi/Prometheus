# BEL-48H review record -- adversarial reviews of the DEF-BEL-008/009/010 repairs

Object under review: d36012f0b (branch bellerophon/def-bel-008-010-2026-10-06). Two independent reviewers, run as
separate background agents with read-only scratch exports (directive s2). Scripts stay in the session scratchpad
(reviewA/, reviewA_base/, reviewA_taint/, ident.py; reviewB/); their outputs are summarised here with the numbers
they reported.

## Review A -- implementation correctness (completed 2026-10-08 ~05:38Z)

Verdict as shipped: FAIL; PASS_WITH_FIXES once 008's attribution is fixed.

| item | verdict | finding | disposition |
|---|---|---|---|
| 1 provenance causal | DEFECT | one-hop: a copy with source in [L,2L) always counted target, even when the writer wrote that byte earlier in the execution; scratch-staged copies counted 'constructed'. Measured on short SOUP runs (3 seeds x 60 ticks): shipped 'target' labels wrong in 335/540 COPY, 337/938 PARTIAL, 385/1,085 PAIR, 29/129 OVERWRITE | FIXED dc1833bc2: VM tracks pre-execution origin of every written byte (copy ops + register-A moves, multi-hop, across SEPARATED halves); tests added |
| 2 mixed origin / constructed | PASS w/ concerns | tie rule correct; 'constructed' consistent; credit change identical under RESEMBLANCE. Concerns: constructed bytes do not vote (1 W + 63 C = writer; 0 + 64 = constructed); 'captures' means different things under the two rules | recorded as ruler limits (comments + this record); campaign reports the per-byte vector, never the label alone |
| 3 paired init | PASS | 12 layouts collapse to 1 post-init state under PAIRED (3 under HISTORICAL); RNG stays paired through tick-0 interactions, diverges at tick-0 mutation (alive count differs: a treatment effect); separate finding: seeds use k < n//8 inside the transplant quarter, so with init_tapes no seed is ever placed | PASS; the seed/transplant overlap is a pre-existing layout fact, recorded, not changed |
| 4 written rule | CONCERN | a 6-byte tape sweeping scratch zeros over the window passes 'written' | FIXED dc1833bc2: a position counts only if its material origin is the same tape position |
| 5 byte identity | PASS | 478 full-output cases identical 5548ed819 vs d36012f0b | re-run on dc1833bc2: 478/478 identical; golden replay passes |
| 6 serialisation | PASS w/ concern | typos in switch values ran silently as historical | FIXED: ValueError on unknown glineage_rule / init_draws / rep_rule |
| 7 rest of diff | CONCERN | stale comments; tests missed window/scratch staging, PAIR/SEPARATED/COPYALL, validation, zero sweep | comments corrected; 7 tests added (window-staged, scratch-staged, register move, constructed vs shifted target, SEPARATED, validation, zero sweep) |

Effect on the campaign: belinst shared the one-hop vector, so the first W1 run (5618bd275) was stopped at 128 results
and superseded; W1 re-frozen as W1 v2 on dc1833bc2 (prereg amendment 1).

## Review B -- scientific validity

(pending at the time of writing; appended when it reports)
