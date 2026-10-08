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

## Review B -- scientific validity (completed 2026-10-08 ~06:00Z; reviewed d36012f0b)

Verdict: SOUND_WITH_LIMITS. Each repair fixes its target defect and biases nothing; none measures what its name
suggests (parentage / CRN variance reduction / replication). Its executed specimens were re-run against the repaired
kernel (ebc3daaae, scratch reviewB_on_fix/):

| question | B verdict | specimens | on the repaired kernel | disposition |
|---|---|---|---|---|
| Q1 provenance = parentage? | LIMITED (+1 WRONG) | S1a inert-majority writer over a partner's replicator -> 'writer'; S1b one-hop laundering -> 'writer' (32,31); S1c window-to-window self copy -> 'capture' (22,42); S1d 8-byte prefix replicator under PARTIAL -> 'target'; S1e PAIR_EXECUTION: only the partner's code ran, A credited | S1b -> target (0,63) CORRECT; S1c -> writer (64,0) CORRECT (both fixed by the multi-hop origin of dc1833bc2; S1b now a kernel test); S1a, S1d, S1e unchanged: count-based material ancestry, not functional parentage | LIMIT DISCLOSED. The campaign never uses the 2-way label alone: it records the per-byte origin vector + founder tags (heredity.py) and the critical-byte origins (functional weighting) |
| Q2 multi-parent | WRONG for a 2-way label | X builds bytes 0-3, Y builds 4-7 over inert Z on later ticks: working replicator labelled Z's; 13-16% of random-world births execute bytes of both origins | unchanged (a 2-way label cannot express it) | LIMIT DISCLOSED; this is exactly what heredity.py's per-byte founder tags + critical-set origins measure (W2) |
| Q3 PAIRED | LIMITED | streams split at tick 0 under COPY with a replicator transplant, 0-40 ticks otherwise; paired/independent variance ratio 0.977 / 1.006 / 1.318; no bias (z = -0.72) | unchanged | LIMIT DISCLOSED: alignment of initialisation only; no CRN power claim; seeds remain the unit (W1-P8 tests exactly this) |
| Q4 written rule | WRONG both ways | FP1 zero-sprayer passes v1+written; FP2-FP4 sterile near-copies pass; FN1 prefix replicator, FN2 shifted copier rejected; on 474 evolved tapes v1 == written on every tape | FP1/FP1b now FAIL 'written' (fixed); FP2-FP4 and FN1/FN2 unchanged | LIMIT DISCLOSED: 'written' = near-complete own-position self-copy in one execution. The campaign's FUNC has the same single-generation scope; TRB requires a FUNC CHILD (a sterile copy cannot chain); and B's k-generation functional() is adopted as an additional OFFLINE measurement on stored specimens (FUNCK) -- not a change of any frozen definition |
| Q5 0.9 over L | LIMITED | prototype functional(): 4 generations x {zero, random} backgrounds, shift-tolerant heritability of the writing behaviour | -- | adopted as FUNCK (analysis only) |

Additional disclosure from B: PAIR_EXECUTION registers a birth on ANY change of the partner half (no minimum-write
check) -- a pre-existing physics fact, recorded, not changed.

## Integration decision

Review A: PASS_WITH_FIXES, fixes applied and re-verified (dc1833bc2; 478/478 identity, golden replay, 21 regression
tests). Review B: SOUND_WITH_LIMITS, limits disclosed above and in the code comments, its two defect specimens fixed.
Both pass under the directive's rule ("if a reviewer identifies a defect, repair it, rerun the adversarial tests,
and proceed"). The branch is merged to main by fast-forward after merging origin/main into it and re-running the
z80atlas suite.
