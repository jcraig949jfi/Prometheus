# E — PARAMETER CERTAINTY TABLE

Every reconstructed historical parameter carries exactly one certainty class
(directive §2 gate P4): `VERIFIED_EXACT` · `VERIFIED_RANGE` · `INFERRED` ·
`UNSPECIFIED` · `ASSUMED_FOR_RECONSTRUCTION`.

Nothing here is silently filled. A blank would be a defect; `UNSPECIFIED` is
the honest entry and it appears often.

**The dominant uncertainty in this table is version skew.** The oldest
surviving official Avida source is **2.2, released 2005-02-14**, roughly 21
months after the May 2003 paper. Every parameter read from source is therefore
`VERIFIED_EXACT` *for 2.2* and at best `INFERRED` for 2003, unless the
supplementary independently confirms it. Where the supplementary and the 2.2
source agree exactly, the parameter is promoted to `VERIFIED_EXACT`, and the
agreement itself is recorded as the reason.

| Parameter | Value | Certainty | Source / reasoning |
|---|---|---|---|
| Instruction alphabet size A | 26 | VERIFIED_EXACT | supplementary §I lists 26 instructions (a–z); `inst_set.default` in 2.2 lists the same 26 mnemonics in the same order. Two independent sources agree. |
| Instruction mnemonics and order | nop-A, nop-B, nop-C, if-n-equ, if-less, pop, push, swap-stk, swap, shift-r, shift-l, inc, dec, add, sub, nand, IO, h-alloc, h-divide, h-copy, h-search, mov-head, jmp-head, get-head, if-label, set-flow | VERIFIED_EXACT | supplementary §I table; `inst_set.default` letter comments a–z match one-for-one |
| Rewarded logic tasks | NOT, NAND, AND, OR_N, OR, AND_N, NOR, XOR, EQU (nine) | VERIFIED_EXACT | supplementary §IV legend names exactly these nine in this order; `environment.cfg` declares exactly nine REACTION lines with the same names |
| ECHO rewarded? | NO | VERIFIED_EXACT | supplementary §II lists ECHO as a one-input logic operation, but it is absent from the nine-function legend and absent from `environment.cfg`. ECHO is describable but unrewarded. |
| Reward exponents | NOT 1, NAND 1, AND 2, OR_N 2, OR 3, AND_N 3, NOR 4, XOR 4, EQU 5 | VERIFIED_EXACT | `environment.cfg` `process:value=` fields; identical to the "# nand" minimum-NAND row of supplementary §II. Independent agreement. |
| Reward function | `type=pow` → merit multiplier 2^value | VERIFIED_EXACT (2.2) / INFERRED (2003) | `environment.cfg` states `type=pow`. The supplementary does not restate the functional form, so the 2003 identity is inferred from exponent agreement. |
| Task credit rule | all 32 bit-wise problems must be correct | VERIFIED_EXACT | supplementary §II: "must return the correct values for an entire series of 32 bit-wise problems" |
| Reaction requisite | `max_count=1` (each task rewarded once) | VERIFIED_EXACT (2.2) / INFERRED (2003) | `environment.cfg`; not restated in the supplementary |
| Ancestral genome | `rucavccccccccccccccccccccccccccccccccccccutycasvab` (50 instructions) | VERIFIED_EXACT | supplementary §IV, phylogenetic depth 0 |
| Ancestral phenotype | 0 0 0 0 0 0 0 0 0 (no functions) | VERIFIED_EXACT | supplementary §IV, pd 0 |
| Line of descent length | 112 genotypes, pd 0–111 | VERIFIED_EXACT | supplementary §IV table, parsed to `lineage_of_descent.jsonl` |
| T_EQU (first EQU on the line of descent) | phylogenetic depth 111, birth update 27450 | VERIFIED_EXACT | supplementary §IV, first row with the ninth function bit set |
| Genome length along the line of descent | 50 → 61 instructions (min 50, max 61) | VERIFIED_EXACT | computed over the parsed lineage |
| Functions held at pd 111 | 6 of 9 | VERIFIED_EXACT | computed over the parsed lineage |
| Genotypes in the full line of descent (as distributed) | 345 | INFERRED | supplementary §IV says "functional-genomic arrays for all 345 genotypes in the line of descent" are at the (now dead) myxo URL. Our table holds 112 through EQU; the discrepancy is unexplained and is a **live archaeology question** — see §14 of the gate packet. |
| Population size | UNSPECIFIED | UNSPECIFIED | not in the supplementary; not recoverable from 2.2 defaults without the paper's own config. Herakles's seed row records 3600 as `MODEL_RECALL_UNVERIFIED` — NOT adopted here. |
| World geometry | UNSPECIFIED | UNSPECIFIED | as above; Herakles's 60×60 recall is not adopted |
| Point mutation rate | UNSPECIFIED | UNSPECIFIED | not in the supplementary; the paper's Methods are paywalled |
| Insertion / deletion rates | UNSPECIFIED | UNSPECIFIED | as above. **Load-bearing**: directive §8 requires knowing whether indels matter before defining M1 |
| Copy mutation rate | UNSPECIFIED | UNSPECIFIED | as above |
| Number of replicate populations | UNSPECIFIED | UNSPECIFIED | the supplementary refers to a single "case-study population"; the total number of replicates is in the paywalled main text |
| Run length (updates) | ≥ 27450 | VERIFIED_RANGE | the case-study lineage reaches EQU at update 27450, so the run is at least that long; the configured stop is unknown |
| Random seeds | UNSPECIFIED | UNSPECIFIED | no seed appears in any recovered artifact |
| Avida version used in 2003 | UNSPECIFIED | UNSPECIFIED | the supplementary names no version. Oldest surviving release is 2.2 (2005-02-14). |
| Contemporary (non-EQU) genotypes | NOT RECOVERED | UNSPECIFIED | **the binding gap.** See F and R. |

## What this table forbids

Directive §2: *"If H0 cannot establish the experiment tightly enough for
faithful reconstruction, stop and classify the specimen
`APPROXIMATE_RECONSTRUCTION_REQUIRED`. Do not compensate with confidence."*

Seven parameters needed to *re-run* the specimen are `UNSPECIFIED`: population
size, world geometry, three mutation rates, replicate count and seeds. A
faithful re-run is therefore **not currently possible**, and any re-run built
on today's evidence would be `APPROXIMATE_RECONSTRUCTION`.

That does **not** block the first analysis. H1A as specified is a *static*
analysis of genotypes, and the genotypes on the successful line of descent are
`VERIFIED_EXACT`. What blocks H1A is a different gap — the absence of
contemporaries — documented in F and R.
