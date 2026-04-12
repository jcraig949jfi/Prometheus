# Finding #34 Deep Dive: Isogeny-Knot Overlap
## VERDICT: SIZE ARTIFACT — Downgrade to KILLED

### The claim
Primes that are knot determinants have different isogeny graph structures (eta²=0.047, 3.35x Benford enrichment).

### The confound
Knot determinants are ALL small odd numbers: range 3-377, mean=154, median=150.
Isogeny primes span 3-30000+, mean=14361. The "overlap" is 60 primes in the 3-377 range.

Small primes have structurally different isogeny graphs by the Deuring mass formula:
- Fewer nodes (13 vs 1197, ratio 0.011)
- Smaller diameters (3.2 vs 7.8, ratio 0.41)
- Higher spine fraction (54% vs 7%, Cohen's d=6.5)

ALL 19 significant features are driven by prime size, not by "knot-determinant-ness."

### Size-controlled comparison
Even restricting to primes 100-10000: knot-det primes still cluster small (mean 158 vs 410). The comparison is not size-matched.

### Kill
This is the same failure mode as Finding #56 (Benford artifact) but harder to see because it passed the 3.35x enrichment threshold. The enrichment is real but explained by: both datasets sample from small integers, and small primes have small isogeny graphs.

No mathematical mechanism connects knot determinants to supersingular isogeny structure. The overlap is numerological.
