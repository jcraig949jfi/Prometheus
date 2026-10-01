# W2-31: HARV × write confinement — decomposing the side-1 CVT-R residual

> Saved by Nestor from the worker's returned text, condensed with every number kept. The harness blocks subagents from writing report files.
> - **Timing:** PREREG frozen 2026-10-01T02:28:33Z (HEAD 53bbba00a), before any VM build. Scoring 02:30:35–02:31:42Z.
> - **Compute:** about 1.5 CPU-min.
> - **Files:** PREREG.md, `_arms.py`, `st_selftest.py`/SELFTEST.json, `score.py`/score.json, `decomp.py`/decomp.json, `d1_residual.py`/.json, RESULTS.json.

## Answer
**Both pre-registered predictions PASS.** The HARV_HALT control reproduces W2-23 exactly: 10/17, 895/1020, and classes 759 / 114 / 147.

- **Store confinement nearly closes the gap.** Under order-protected confinement of both block and byte-store writes, the partner may not write into the copier's half before the copier runs. Side-1 CVT-R goes from 10/17 to **16/17**, and good copies go from 895 to **1020/1020**, matching the no-partner baseline.
- **Block confinement alone gets most of the way.** CVT-R is **15/17** and good copies 996/1020: 24 bad, against 19 predicted.
- **D1 residual: one genome, b:q1_competent:59.**
  - Its base lineage collapses at generation 2 even with no partner (fidelity 0.016).
  - Its no-partner CVT-R pass rests on 9 recurring signatures inside lineages that are already garbage.
  - The residual travels through the **read path**. The copier's own ~252-byte LDIR wraps through the partner's half and copies the partner's edits.
- **Partner writes into the copier's half explain all 125 bad copies and 6 of the 7 CVT-R failures under HARV.**

## Design
Confinement is **order-protected**: a context may not write into the other half while that half's owner has not yet run. The rule depends only on execution order and is symmetric across sides.

- **A blanket "own half only" rule also stops the copier writing its child.** Blanket HARV×BLOCK_OWN and HARV×STORE_OWN both give 0/17 CVT-R, 0/1020 good copies, and 0/17 P-11.
- **Cost:** the first mover can never convert, so side-0 copiers drop from 13/18 to 0/18 (0/1080 good). **This is a causal diagnostic, not a viable physics.**
- All 5,100 scored traced interactions were asserted byte-identical to `p11.interact`.

## Predictions

| # | criterion | observed | verdict |
|---|---|---|---|
| Control | HARV_HALT reproduces W2-23 | exact | reproduced |
| P1′ | side-1 CVT-R ≥ 15/17 under STORE_OWN_OP | **16/17** (1020/1020) | **PASS** |
| P1″ | bad copies in [11, 28] under BLOCK_OWN_OP (predicted 19) | **24** (CVT-R 15/17) | **PASS** |
| P1″ secondary (not scored) | pre-damage events fall 261 → ~147 | 173 | HALT's BLOCK class overcounts; 26 of its events also carry byte damage |
| D1 | no residual iff 17/17 and 1020/1020 | 16/17, 1020/1020 | residual of 1 genome, via the read path |

| arm | CVT-R | good copies | P-11 |
|---|---|---|---|
| HALT | 10 | 895 | 17 |
| BLOCK_OWN_OP | 15 | 996 | 17 |
| STORE_OWN_OP | 16 | 1020 | 17 |
| blanket BLOCK_OWN | 0 | 0 | 0 |
| blanket STORE_OWN | 0 | 0 | 0 |
| no partner | 17 | 1020 | – |

## Decomposition of HALT's 125 bad copies

| partner damage type | interactions | bad under HALT | bad under BLOCK_OWN_OP | bad under STORE_OWN_OP |
|---|---|---|---|---|
| block only | 88 | 85 | 0 | 0 |
| block + byte | 20 | 20 | 4 | 0 |
| byte only | 154 | 20 | 20 | 0 |
| none | 758 | 0 | 0 | 0 |

- **Shares:** block writes are necessary in **101/125 (0.81)**; byte stores alone account for **24 (0.19)**.
- **Bytes changed:** 13,910 via block writes, 611 via byte stores.
- **No harm from BLOCK_OWN_OP:** it never turned a good copy bad.
- **HARV activity:** fired in 629/1020 interactions.
- **Per-genome CVT-R:**
  - STORE_OWN_OP rescues q1:2, q1:7, q1:84, q1:86, q1:88 and c_zero:13.
  - BLOCK_OWN_OP rescues all of these except q1:2 (CVT 177/172/0).
  - q1:59 fails in every arm with a partner.

## Self-tests (all pass)
- **ST0:** the HALT source is identical to W2-7's.
- **ST1:** each arm is bit-identical to HARV_HALT wherever its counter is 0, and changes state wherever it fires.

  | arm | identical where counter = 0 | changed where it fires |
  |---|---|---|
  | BLOCK_OWN_OP | 1177/1177 | 323/323 |
  | STORE_OWN_OP | 859/859 | 641/641 |
  | blanket BLOCK_OWN | 883/883 | 617/617 |
  | blanket STORE_OWN | 314/314 | 1186/1186 |

- **ST2:** blanket BLOCK_OWN equals W2-7's BLOCK_OWN wherever HARV did not fire (259/259).
- **ST3:** hand-assembled programs behave as specified, including protection reset on a fresh tape.
- **ST4:** `p11.assay` = `alien_pair.assay` on 12/12 per arm, and the counters fire inside the CVT-R step.

## Adversarial round
1. **Tailored to the copier?** No. The rule depends only on execution order, and side-0 copiers drop to 0/18. It is not claimed as a viable physics.
2. **Is STORE_OWN_OP just the no-partner arm?** No. Children differ in 12 interactions and in 379/1245 q1:59 step calls, and nearly all of those differing bytes are the copier's own. The read path is live.
3. **Was P1″'s band wide?** It was pre-registered. The 5 extra bad copies are byte-only events inside mixed interactions.
4. **Is 16/17 noise?** CVT-R is single-seed. q1:59 is not a working lineage anyway.
5. **Depends on HARV.** Yes. Order protection without HARV is untested.
6. **Tape state could leak.** Tapes are fresh in every driver used. A world that reused tapes would break the rule.
7. **All static.**

## Ledger entry (W2-31)
- **Inference.** Under HARV, side-1 failure is the partner's data-path writes before the copier runs: about 81% need a block write and about 19% are byte-only. Removing them restores no-partner fidelity. Side-1 failure therefore needs three things:
  1. the partner's pc executing the copier's code (removed by HARV);
  2. the partner's own data-path writes (removed by order protection);
  3. a small read-path coupling through wraparound LDIRs.
- **Confidence:**
  - high for the per-interaction decomposition;
  - moderate for CVT-R counts, which are single-seed.
- **Strongest objection:** order protection is a diagnostic, not a fair physics.
- **Next:**
  1. STORE_OWN_OP without HARV.
  2. CVT-R over K reseeds.
  3. Audit CVT-R acceptance of genomes whose lineage collapses (q1:59).
  4. A symmetric order rule as a candidate physics.
