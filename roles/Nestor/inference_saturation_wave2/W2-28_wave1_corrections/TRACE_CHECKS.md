# W2-28 trace checks: two claims traced to data

**Written:** 2026-10-01T02:30:30Z (`date -u`). The computations ran between 02:26:46Z and 02:28:28Z.
**How it was done:**
- read-only;
- no git writes;
- no world or evolution runs;
- under 1 CPU-min in total (JSON reads plus closed-form Poisson and binomial sums).

The code is inlined in the appendix, so every number can be re-derived from the paths named there.

## Verdicts

| claim | where it is made | verdict | supported replacement |
|---|---|---|---|
| "Intermediates (27–162 births): predicted 2.4%, observed 1 vs 7.7 expected over 320 runs (P = 0.004)" | `W2-2_near_miss/REPORT.md:29`; repeated in W2-2's "second regime" reading | **UNTRACEABLE to any script, and CONTRADICTED by its own source data.** The figure *can* be reconstructed arithmetically: it is a denominator mismatch. | **f = 1 pool (192 runs = 128 X-TICKET + 64 X-DECAY f = 1):** 1 observed vs 4.6 expected, P = 0.054 (binomial) / 0.056 (Poisson). **X-TICKET alone (128):** 0 vs 3.1, P = 0.045. Both have data-chosen edges. **All 320 runs:** 8 observed vs 7.7 expected, P(≤ 8) = 0.64, so there is no deficit. |
| "Establishment is decided within 3–10 epochs" | `NPE_MECHANISTIC_SYNTHESIS_2026-09-30.md:160` and `:243`; `NPE_UNMINED_EVIDENCE.md:28` (U-T1); `INFERENCE_HARVEST_HANDOFF.md:115`; dossier D U5 | **TRACED to data** (dossier D U5: S1 epochs in `npe-p2-endogenous-heredity-2026-09-27/{c_zero_specific,x_p2_bridge,x_p2_regstate}/results/*.json`). **CONTRADICTED as worded.** The data show that *failure* is mostly decided early, and that *success* is not. | See §2. In short, an early first copy is near-necessary and about a coin flip for success: P(established \| first founder copy by epoch 10) = 196/389 = 0.50. |

---

## 1. W2-2: "1 vs 7.7 over 320 runs, P = 0.004"

### 1.1 Search for a source
- No script in `W2-2_near_miss/` computes an expected count for the 27–162 bin or a P value for it:
  - `a2_rulers.py` only counts observed `intermediate_27_162` per f;
  - `a7_gw_vs_ticket.py` only produces predicted bin *fractions*.
- Grepping every W2-2 file for `7.7`, `7.68`, `0.004`, `0.0040` and `0.0037` finds only `REPORT.md:29`. There is one unrelated hit: `a3_atomic_core.json:1346`, a 7ae3_ATOMIC chain-index value of 7.688.
- The red-team finding (W2-25 F9) is confirmed: **no script computes the claim.**

### 1.2 Reconstruction
The figure reproduces exactly from two inputs:
- the law's fraction for the gap bin, `a7_gw_vs_ticket.json` `7ae3_BASE_causal/predicted/27-162` = **0.024**;
- the 320-run pool that `a2_rulers.py` builds (`depth_vs_B.n` = 320: 128 X-TICKET + 192 X-DECAY over f ∈ {1, 0.25, 0}).

The calculation is then: expected = 0.024 × 320 = **7.68**, and Poisson P(X ≤ 1 | 7.68) = **0.0040** (binomial 0.0037).

The observed "1", however, is **the f = 1 sub-pool count** (`a2_rulers.json` `B_hist_by_f["1.0"].intermediate_27_162` = 1, over n_runs = 192). It is not a 320-run count. So the numerator comes from 192 runs and the expectation from 320.

**Recount from the raw campaign files** (`campaigns/c9x-explore-2026-09-24/{x_ticket,x_decay}/results/*.json`, using the same field choices as `a2_rulers.py`):

| pool | runs | observed B in 27–162 | expected at 0.024 | P(X ≤ obs), binomial / Poisson |
|---|---|---|---|---|
| X-TICKET only (f = 1) | 128 | 0 | 3.07 | 0.045 / 0.046 |
| f = 1 (X-TICKET + X-DECAY f = 1) | 192 | 1 (X-DECAY, B = 35, depth 8) | 4.61 | **0.054 / 0.056** |
| f = 0.25 (X-DECAY) | 64 | 3 | 1.54 | not a deficit |
| f = 0 (X-DECAY) | 64 | 4 | 1.54 | not a deficit |
| all 320 (the claim's denominator) | 320 | **8** | 7.68 | 0.64 / 0.64 |

With the law's unrounded value (0.0243) the results are 0.0034–0.0037 for the claim's arithmetic and 0.051–0.053 for the f = 1 pool.

### 1.3 Verdict and replacement wording
- **Verdict.** UNTRACEABLE to any script. CONTRADICTED by `a2_rulers.json` and by the raw files: on its own 320-run denominator the gap holds 8 runs, which is on expectation. The P = 0.004 comes from pairing an f = 1 numerator with an all-f denominator.
- **A further objection.** The law (`a7`) was built for the f = 1 BASE world, so applying it to the f < 1 arms would be wrong anyway.
- **Replacement wording:**

  > "The 27–162 gap is an f = 1 feature: 1 run in 192 against 4.6 expected (P ≈ 0.054–0.056); X-TICKET alone 0/128 against 3.1 (P ≈ 0.045). Both edges were chosen from the data (s2 ends at B = 26, s14 at B = 163), so these P values are optimistic. The gap fills at f < 1 (7/128). Not evidence for a second regime by itself."

- **Consistency with other records.**
  - This agrees with W2-14 §1b (P = 0.045, X-TICKET) and with W2-25 F9 (about 0.056).
  - The ledger's "the supported figure is about 0.056" (INFERENCE_LEDGER W2-25 item 6) is right for the f = 1 pool. The X-TICKET-only figure (0.045) should be quoted alongside it.

---

## 2. Synthesis: "Establishment is decided within 3–10 epochs"

### 2.1 Trace
- **The chain of citations.** SYN:160 cites U-T1, which cites dossier D U5. The dossier's table reads:
  - "C-ZERO-SPECIFIC ZERO: S1 epoch 0–3 in all 26 S5 runs";
  - "failed CONST median 325, RANDOM median 104";
  - "BRIDGE STATELESS max 10, **BRIDGE PERSIST max 82**".
- **The 3–10 range** is the range of the *maximum first-copy epoch among established runs*, in the two arms the summary quoted. PERSIST's 82 was dropped from the summary line (D:782, "~3-10 epochs").
- **Stage definitions** (`x_p2_bridge/run_br.py:28-31`):
  - S1 = the first accepted replication event from L;
  - S2 = the first P-11 causal birth from the founder;
  - S4 = the first P-11 causal birth from a non-founder member;
  - S5 = world causal depth ≥ 20 by epoch 500 AND final anc0 ≥ 0.9.
- **The dossier's numbers reproduce exactly:**
  - CZ ZERO: max S1 among S5 runs = 3, n = 26;
  - CZ CONST: failed-run S1 median 325;
  - CZ RANDOM: 104;
  - BRIDGE PERSIST: max 82;
  - BRIDGE STATELESS: max 10.
- **The "median 325 / 104" is computed only over failed runs that copied at all.** 42 of the 46 CONST failures and 37 of the 45 RANDOM failures never copied.

### 2.2 What the same files show when read as a decision claim
All 704 runs of the three experiments are pooled (C-ZERO-SPECIFIC 192, X-P2-BRIDGE 256, X-P2-REGSTATE 256); 199 are established (S5).

| condition | established |
|---|---|
| first founder copy (S1) by epoch 3 | 175/341 = 0.51 |
| S1 by epoch 10 | **196/389 = 0.50** |
| S1 after epoch 10 | 3/48 = 0.06 |
| founder never copies | 0/267 |
| first certified founder birth (S2) by epoch 10 | 171/314 = 0.54 |
| first certified grand-offspring birth (S4) by epoch 10 | 147/184 = 0.80 |
| S4 by epoch 20 | 158/216 = 0.73 |
| no S4 at all | 30/451 = 0.07 |

**Established runs by first-copy epoch:**
- 196/199 had S1 ≤ 10, and 175/199 had S1 ≤ 3.
- The 3 later ones are all BRIDGE PERSIST, at epochs 25, 31 and 82.

**Per arm, P(S5 | S1 ≤ 3) ranges from 5/27 (CZ CARRY) to 26/42 (CZ ZERO).** Even in the arm the claim was built on (CZ ZERO), 16 of the 42 runs that copied by epoch 3 failed.

**Separately, for X-TICKET under BASE** (not the panel experiments above):
- runaways and bursts are indistinguishable until about epoch 10 (U-T2; W2-2 §1, "nothing on disk distinguishes it before epoch 10");
- the best discriminator is births in epochs 11–15 (W2-2 EW-1: 4/4 hit, 0/124 false alarms);
- the 27th causal birth falls at epochs 9–15 in the 4 runaways (W2-25 F2);
- side-0 morphs arrive at epochs 10–51 (W2-25 F2).

### 2.3 Verdict and replacement wording
- **Verdict.**
  - TRACED: the numbers exist and reproduce.
  - CONTRADICTED as worded: "fate is decided" overstates a necessary condition as a decision. Within 10 epochs the data decide *failure* (no copy by epoch 10 → 3/48; never → 0/267), but success remains about a coin flip (0.50). Even a grand-offspring certified birth by epoch 10 leaves 20% failing.
  - The synthesis's own U-T2 (divergence at epochs 10–20) is in tension with it.
- **Supported replacement:**

  > "Failure is usually decided early, and success is not. In the implanted-panel experiments (704 runs, S5 at epoch 500), 196 of 199 established runs made their first accepted founder copy by epoch 10, and runs without one by then establish 3/48. But only 196/389 (0.50) of runs with a first copy by epoch 10 establish, and 147/184 (0.80) even with a certified grand-offspring birth by epoch 10. In X-TICKET under BASE, burst and runaway are indistinguishable before epoch 10, and whether a burst becomes a runaway is settled by post-27 persistence at about epochs 10–50."

## 3. Ledger-style summary

- **Question.** Can W2-2's "1 vs 7.7, P = 0.004" and SYN's "fate decided in 3–10 epochs" be traced to scripts or data, and what figures do the data support?
- **Evidence.**
  - `W2-2_near_miss/{a2_rulers,a7_gw_vs_ticket}.{py,json}` and the raw `x_ticket`/`x_decay` results;
  - dossier D U5;
  - `npe-p2-endogenous-heredity-2026-09-27/{c_zero_specific,x_p2_bridge,x_p2_regstate}/results/*.json` (704 runs);
  - `x_p2_bridge/run_br.py:28-31`.
- **Inference.**
  - The W2-2 P value is a denominator mismatch: an f = 1 numerator against an all-f expectation. The supported figure is P ≈ 0.054–0.056 (f = 1), or 0.045 (X-TICKET only), with data-chosen edges.
  - "3–10 epochs" is a necessary-condition window misread as a decision. The supported figure is P(S5 | early first copy) ≈ 0.50.
- **Confidence.**
  - High: both are direct recounts that reproduce the source tables exactly.
  - Moderate that the reconstruction is *how* 0.004 arose. It matches to 2 significant figures, but no script records it.
- **Strongest objection.**
  - X-DECAY f = 1 may not be exactly X-TICKET physics, so the 192-pool would mix cells. The X-TICKET-only figure (0.045) avoids this and gives the same conclusion.
  - S5 is judged at epoch 500, not 2000.
- **Unresolved.**
  - Whether the X-DECAY `cbirths` readout equals X-TICKET's traj B. `a2_rulers.py` treats them as equal, and this check did not verify it.
- **Next.**
  - Pre-register the gap edges before any future "empty gap" claim (W2-14 next-5).
  - Report establishment as P(S5 | stage-by-epoch) curves, not as windows.

## Appendix: code run (verbatim; under 1 CPU-min)

```python
# (A) W2-2 gap figure - run from roles/Nestor/inference_saturation_wave2/W2-2_near_miss
import json, glob, pathlib, math
C = pathlib.Path('.').resolve().parents[1] / "campaigns" / "c9x-explore-2026-09-24"
L = lambda p: [json.load(open(f)) for f in sorted(glob.glob(str(C / p)))]
TK = L("x_ticket/results/*.json"); XD = L("x_decay/results/*.json")
rows = [("tk", 1.0, r["traj"][-1][2]) for r in TK] + [("xd", r["f"], r["cbirths"]) for r in XD]
# per-f and pooled counts of 27 <= B <= 162; expected = 0.024 * n
def pois_le(k, mu): return sum(math.exp(-mu) * mu**i / math.factorial(i) for i in range(k + 1))
def binom_le(k, n, p): return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k + 1))
# outputs: 320 pool k=1 (claimed): exp 7.68, Pois 0.0040, Binom 0.0037; 320 actual k=8: 0.637;
#          f=1 (192) k=1: exp 4.61, Pois 0.0559, Binom 0.0539; ticket (128) k=0: exp 3.07, 0.0463 / 0.0446

# (B) Establishment timing - run from roles/Nestor/campaigns/npe-p2-endogenous-heredity-2026-09-27
import json, glob
allr = [json.load(open(f)) for e in ("c_zero_specific", "x_p2_bridge", "x_p2_regstate")
        for f in sorted(glob.glob(e + "/results/*.json"))]
def p(cond): v = [r for r in allr if cond(r)]; return sum(r["S5"] for r in v), len(v)
# p(lambda r: r["S1"] is not None and r["S1"] <= 10) -> (196, 389); <= 3 -> (175, 341); > 10 -> (3, 48)
# p(lambda r: r["S1"] is None) -> (0, 267); S2 <= 10 -> (171, 314); S4 <= 10 -> (147, 184); S4 <= 20 -> (158, 216)
```
