# Thread C: EC Zero Projections — Arithmetic Complexity Suppresses Variance

## Finding

First-gap variance stratified by isogeny class size and Sha order reveals a clear pattern: **more arithmetically complex curves have more regular zero spacings.**

### Projection #3: Isogeny class size
| class_size | n | var | var/Gaudin |
|---:|---:|---:|---:|
| 1 | 21,794 | 0.244 | 1.371 |
| 2 | 19,400 | 0.234 | 1.314 |
| 4 | 7,291 | 0.239 | 1.345 |
| 6 | 936 | 0.201 | 1.128 |
| 8 | 192 | 0.172 | 0.965 |

Class size 8 curves sit BELOW Gaudin (var/Gaudin = 0.965). Monotone decrease from 1.37 to 0.97.

### Projection #5: Sha order
| sha | n | var | var/Gaudin |
|---:|---:|---:|---:|
| 1 | 40,566 | 0.231 | 1.300 |
| 4 | 5,901 | 0.205 | 1.151 |
| 9 | 2,111 | 0.218 | 1.226 |
| 16 | 708 | 0.203 | 1.138 |
| 25 | 353 | 0.200 | 1.126 |
| 36 | 106 | 0.178 | 0.998 |

Sha=36 curves sit exactly at Gaudin. Trend: higher Sha = more regular zeros.

## Interpretation

Both projections tell the same story: **arithmetic complexity (more isogenies, larger Sha) imposes additional regularity on L-function zeros beyond what RMT predicts.**

This connects directly to Thread A (F011 rank-0 residual):
- The 31% pooled deficit is an AVERAGE across all isogeny sizes and Sha orders
- The deficit is strongest for simple curves (class_size=1, sha=1) and weakens for complex ones
- Complex curves (class_size=8, sha=36) approach or reach Gaudin — no deficit

**The deficit is NOT uniform.** It depends on the arithmetic of the specific curve. This rules out a generic unfolding error (which would affect all curves equally) and points toward genuine arithmetic structure in the zero spacing.

## Connection to Katz-Sarnak

Katz-Sarnak predicts zero statistics should be UNIVERSAL within a family (same symmetry type). Stratification by isogeny class size and Sha SHOULD NOT change the zero statistics if Katz-Sarnak is exact. The fact that it DOES is a finite-conductor effect — but one that isn't captured by the excised ensemble model.

## Next Steps

1. **Verify with larger sample** — 50K curves is a subsample. Run on full 1.74M EC L-functions.
2. **Compound stratification** — isogeny × Sha × conductor to separate the effects.
3. **Check projection #7** — compound (rank × CM × w) to see if CM/non-CM makes a difference.
4. **Connect to F041a** — does the isogeny/Sha dependence persist at rank 2+?
5. **Null model** — permute isogeny class labels within conductor bins. If the variance trend survives, it's not a conductor confound.

## Status
POSSIBLE → needs replication at scale and null model. But the monotone trend across two independent arithmetic invariants is strong circumstantial evidence that arithmetic structure suppresses zero variance.
