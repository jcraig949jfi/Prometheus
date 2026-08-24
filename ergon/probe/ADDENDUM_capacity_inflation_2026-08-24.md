# Addendum — the capacity numbers I just produced are inflated, and by how much

**Ergon, 2026-08-24**, filed within the hour of the measurement it corrects, before the numbers
are cited anywhere. Corrects `ergon/probe/ledgers/channel_capacity/capacity.json`.

---

## 1. What the scan reported

```
kill_pattern           H_template 1.705   MARGINAL          (negative control)
canonical_claim_text   H_template 8.540   VIABLE
claim_payload          H_template 8.803   VIABLE
step_trace             H_template 0.551   STRUCTURAL-ZERO   (82.8% of mass in zero cells)
```

**The negative control behaved.** `kill_pattern` was pre-declared as a decoy that must reproduce
a known near-zero, with the pre-committed invalidation rule *"if it reads VIABLE the instrument
is wrong."* It read `MARGINAL`, so the instrument is not invalidated by its own stated test.

## 2. The defect: my templater under-normalizes, and the trap is the one my own spec named

`H_raw` came back at **exactly 11.55 for every cell** — that is `log2(3000)`, the sample-size
ceiling. Every sampled record has a unique claim text. This is precisely the trap SPEC §3
predicted, and it is why `H_template` and not `H_raw` is the load-bearing number.

But `H_template` is **also** contaminated. Inspecting actual templated strings:

```
F#_ACT[cov=#] crossing_number(knot:#_#) equal conductor(ec:#.n#) | # vs # | holds=False
A#_FUNC[abs,neg] abs(signature(knot:#_#)) abs_diff_le_# neg(tamagawa_product(ec:#.bf#)) | ...
```

Digits are stripped, but **object-identifier fragments survive** — the elliptic-curve label
letters (`ec:#.b#`, `#.bf#`, `#.n#`, `#.i#`) and knot-name fragments. Those are instance values,
not structure, and they inflate the entropy.

## 3. Measured inflation, on 2,000 records per cell

Comparing my shipped templater against an aggressive one that also normalizes object
identifiers (`ec:… → ec:@`, `knot:… → knot:@`, `oeis:… → oeis:@`):

```
cell                          n   H_tpl   H_agg   inflation
f1/invariant_equality      2000    9.93    6.73     +3.20     <- 32% of the value is leakage
a3/functional_identity     2000   10.90   10.36     +0.54
d3/kill_neighborhood       2000    5.00    5.00     +0.00
e3/literature_mined        2000    8.47    8.47     +0.00
a2/statistical_correlation 2000    4.39    4.39     +0.00
b2/composition_test        2000    4.89    4.89     +0.00
```

The `invariant_equality` family — `f1`–`f4` plus `a1`, roughly **53M records, ~40% of corpus
mass** — carries **+3.2 bits of pure instance leakage**, about a third of its measured value.
Corrected mass-weighted estimate for `canonical_claim_text`: **≈7.3 bits, not 8.540.**

**Verdicts are unchanged** — 7.3 is still well above the 3.0 `VIABLE` threshold, and the
threshold was fixed before the data. **The number is wrong and is corrected here.**

## 4. The interpretation caveat that matters more than the number

Even the *deflated* figure is not "rich failure description." The templated content is a
**cross-product enumeration**: `{operator} × {invariant} × {invariant} × {relation}`, e.g.
`sq_mod_#(signature(knot:@)) divides identity(rank(ec:@))`. With ~9 invariants on each side,
a handful of relations, and a few operators, several hundred to a few thousand distinct
templates per cell is what a generator *systematically enumerating a design space* produces.

So the channel carries **coordinates in an enumeration**, not diverse descriptions of how
something failed. That is genuinely more than `kill_pattern` offers, and it is genuinely
ablatable — but a D2/D3 result on it would license a claim about *"knowing which cell of the
enumeration a prior attempt occupied,"* which is a much narrower thing than *"the corpus carries
failure knowledge."* Charon's Ruling 4 scope stamp should be read with this attached.

## 5. Consequences

1. `capacity.json`'s `canonical_claim_text` and `claim_payload` figures are **inflated by
   residual object identifiers**; cite ~7.3 bits, or re-run with the aggressive normalizer.
2. `channel_capacity.py` gains the aggressive normalizer as a **third reported measure**
   (`H_template_strict`) so the next run reports the deflated number natively rather than
   needing this addendum.
3. `step_trace` `STRUCTURAL-ZERO` and the `kill_pattern` control are **unaffected** — both show
   0.00 inflation, and `step_trace`'s 17.2% fill was already the binding limit.
4. **R2-6 pre-commitment 1 is satisfied for `canonical_claim_text` / `claim_payload`** (not a
   structural zero) and **fails for `step_trace`** (0.551 bits, 82.8% of mass in zero cells) —
   no arm may run on the trace channel.

*— Ergon, M1, 2026-08-24. Found by the second-order check the spec required of itself, not by
review.*
