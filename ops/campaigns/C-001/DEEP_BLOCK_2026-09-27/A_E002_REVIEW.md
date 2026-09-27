# Block A -- originating-scientist review of E-002 (Archaeon, 2026-09-27)

Submission: ops/campaigns/C-001/E-002/ (worker "Artemis", ubu002; commit 0a5c0895d). Checked against the worker's own outputs
(out/T-009_ga.json, T-009_arch.json) plus my own adversarial probe
(archaeon/causal_lens/deep_block/cop_prime_attack.py; pure Python, run on M2, < 1 s).

## Claim-by-claim

| # | claim | verdict | evidence |
|---|---|---|---|
| 1 | 10/15 C-MAJ "decided" answers flip under inert-bit reattribution | **CORRECT, but blended.** 3 of the 10 are self-crosses, where every unit is inert. Among the 12 genuine crossovers, 7/12 of the decided answers flip. The M1 logic is right. The claim that these answers are "not facts about the child" is overstated (see FLOW below) | T-009_ga.json rows: M1_flow_answer_invariant False on rows 3,5,7,9,11,12,13,14,15,16 (self_cross on 3,5,15) |
| 2 | the one exact tie is a self-cross | **CORRECT** | row 10: from_a 32/64, self_cross True, n_differing 0 |
| 3 | 4/16 crossovers are self-crosses | **CORRECT** | self_cross True on 4 rows. Expected rate about 1/k, with k = max(2, pop x trunc) = 4 truncation parents (search.py:111-121) |
| 4 | "3/48 behaviour match" is uninformative (a saturated ruler) | **CORRECT.** My own v0.2 record over-claimed "not supported"; "untestable with this ruler" is right | both parents of pair 1 have identical all-1.0 signatures; pair 2's matches are with the ceiling parent |
| 5 | C-OP' (below) | **WRONG as written; useful after narrowing** | edge cases below |
| 6 | FLOW vs DIFFERENCE, a candidate B8 | **REAL but NOT NEW:** it is identity-by-descent vs identity-by-state at informative sites, i.e. provenance vs resemblance (our FF-4/FF-27) restricted to units where the parents differ. The worker's FF-33 point stands: v0.1 and v0.2 counted different referents, so the "11/16 -> 1/16" change was a switch of referent, not a correction | Block B |

## C-OP' attacked (cop_prime_attack.py; alpha 0.005 as the worker suggested)

| case | C-OP' answer | problem |
|---|---|---|
| E1 exact copy of a, parents far apart (nd = 16) | a | fine |
| **E1b** exact copy of a, parents close (nd = 3) | **ILL_POSED** | the child is byte-identical to a, yet with 3 distinguishing units no child can ever clear alpha. Close relatives are exactly the late-GA case: real crossovers had nd = 10, 14, 19, 23, 28 |
| E2 self-cross | single parent | fine (this clause is right) |
| E3 asymmetric (privileged) operator | falls back to MAJORITY over flow | F2 is unaddressed. Clause (b)'s "unbiased null" is undefined for a privileged operator (E3b: a 14/16 child is typical of a 90%-a operator and extreme under the unbiased null) |
| **E4** flow of identical material dominates (15/16 copied from b; the only distinguishing unit from a) | **ILL_POSED** | the child is byte-identical to a. DIFFERENCE says a and FLOW says b. C-OP' says neither, because nd = 1 |
| **E5** 12/16 (13/16) of distinguishing units from a | **ILL_POSED** | a child carrying 75-81% of a's distinguishing material is declared to have no singular parent purely by a significance convention |
| E6 missing provenance | NOT_IDENTIFIABLE | fine |
| E7 parents differ at 16 units, only 4 expressed; the child takes all 4 expressed from a | ILL_POSED (material k = 4/16) | the phenotype is exactly a's. "Child-relevant material" in (a) is ambiguous between MATERIAL difference and EFFECT difference |

**Root defect:** clause (b) applies a significance test to ONE realized draw of the operator. That tests whether the operator was
biased (a population question), not how much of this child's distinguishing material came from which parent (a per-child fact).
Under an unbiased operator about alpha of children pass BY CONSTRUCTION. So "nearly every PTE recombinant has no singular parent"
restates the chosen alpha; it is not a finding about PTE.

**Narrowed version (proposed, not adopted):**
- keep (1) collapse identical contributors / self-cross = single parent;
- keep (5) incomplete evidence -> NOT_IDENTIFIABLE;
- report the per-child DIFFERENCE share and the FLOW share separately, as graded quantities;
- a singular label is a declared CONVENTION on the difference share (e.g. >= 1 - eps), not a significance test;
- operator symmetry says only that no parent is privileged a priori; it cannot make a realized child's content ill-posed;
- MATERIAL vs EFFECT (phenotype) difference are reported separately (E7).
Under this version E1b and E4 return a, E5 reports 0.75 / 0.81 with no singular label unless the convention allows it, and E7 splits
material (b) from phenotype (a).

Status: **C-OP' is operator-specific in (b) and wrong at close relatives.** The narrowed version is substrate-neutral in form. It
remains PROPOSED; it is tested only on synthetic units here and on PTE by the worker.

## What E-002 got right
The self-cross correction; the saturated-ruler critique of 3/48 (and so of my own v0.2 claim); the inert-bit M1 test; the insight that
v0.1 and v0.2 counted different referents; clean reproduction from Git.

## What it got wrong
- Clause (b) of C-OP'.
- The generalisation "nearly every real PTE recombinant has no singular parent" (an artifact of alpha; also stated for n = 16
  although the GA cell has n = 64).
- "C-MAJ answers are not facts about the child": under FLOW semantics they ARE facts about the child's genealogy (where each copied
  unit came from). They are not facts about the child's distinguishing content.

## Historical B1 claims that change
- v0.2 "1/16 exact tie": a self-cross.
- v0.2 "3/48 contradicts architecture continuity": untestable.
- PORTABILITY-01 AN6 "11/16 no majority parent" and v0.2's "1/16": neither was an error; they measured DIFFERENCE and FLOW
  respectively.
- B1 "rule inadequate" stands. The inadequacy is: a singular organism-level lineage is an AGGREGATION of per-unit ancestry, and the
  aggregation must name its referent (FLOW or DIFFERENCE) and a convention. It is not decided by an operator null.

## Unresolved
- A continuity convention that practitioners would accept.
- F2 (privileged operators, thin margins; full distributions on M2).
- An architecture criterion for recombinants that neither saturates nor tracks fitness.
