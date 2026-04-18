# Thread A: F011 Rank-0 Residual — The Genuine Frontier

## Status: OPEN — strongest unresolved finding

### The Finding
Harmonia discovered (sessionB, 2026-04-18): rank-0 EC L-function first-gap variance has a 31% deficit vs exact GUE (Gaudin distribution), with z=5.02 from zero after fitting an excised-ensemble decay model. The deficit is 54.6% at lowest conductors, decaying to ~44% at highest, with a residual asymptote of 31±6%.

### What's Been Ruled Out

1. **Wigner-vs-Gaudin reference error**: Harmonia used Gaudin (var=0.178), not Wigner (var=0.273). Verified by Ergon's DHKMS prediction script. NOT the explanation.

2. **DHKMS finite-N correction**: At our conductor range (N~40-270), effective matrix size N_eff~0.5-1.4. DHKMS predicts variance ABOVE Gaudin at small N_eff (approaching Poisson), not below. Goes the WRONG direction.

3. **First-moment deflation**: Normalizing by per-curve mean gap reduces the deficit somewhat (from ~46% to ~40%) but doesn't eliminate it. Would need 25% mean bias to fully explain — implausibly large.

4. **Sample artifact**: z=5.02 across 773K rank-0 curves. Not a fluctuation.

### What Remains

1. **Systematic unfolding error**: If the procedure that converts raw zero heights to normalized spacings has a systematic bias at low conductor, it could compress gaps. This is testable: apply different unfolding methods (local density vs per-curve mean vs smooth N(T) formula) and check if the deficit is method-dependent. The earlier Ergon analysis found the deficit IS method-dependent (14% with first-gap, 40% with pooled), but both methods show a deficit.

2. **Genuine arithmetic suppression**: The arithmetic structure of elliptic curves (Euler product, functional equation) may impose constraints on zero spacings beyond what a random matrix can capture. This would be a real finding — evidence of "hidden order" in L-function zeros.

3. **Excised ensemble at higher order**: The DHKMS model is leading-order. Sub-leading corrections (1/log(N)^2 terms) could be larger than expected. Needs analytic number theorist input.

### Decisive Tests

1. **Independent unfolding comparison**: Use the smooth counting function N(T) = T/(2π) · log(NT²/(4π²e²)) instead of per-curve normalization. If deficit changes dramatically → unfolding artifact. If stable → genuine.

2. **Cross-family comparison**: Compute the same deficit for Dirichlet L-functions (character origins in lfunc). If the deficit is the same → generic unfolding issue. If different → EC-specific arithmetic constraint.

3. **Higher-gap analysis**: Compute gap2 (z3-z2), gap3 (z4-z3) deficits. If deficit is concentrated in gap1 → excised ensemble extended. If uniform across gaps → deeper phenomenon.

4. **LMFDB-independent verification**: Compute zeros de novo using the explicit formula for a subset of curves. Compare to LMFDB stored zeros. If they agree → zeros are correct, deficit is real.

### Connection to Other Findings

- The F041a finding (rank-2+ nbp slope interaction) lives in the same space — higher-rank L-function behavior not predicted by classical RMT.
- Aporia's fingerprints report identifies the "missing operator" (Berry-Keating/Connes) as the theoretical framework gap. The deficit could be a signature of this operator.
- The Scholz reflection result shows arithmetic constraints CAN be perfectly rigid (zero violations). If zero spacing constraints are equally rigid, the deficit is structural.

### Priority
This is the project's strongest frontier finding — a 5-sigma deviation from the best available RMT model, robust across conductor range, not explained by any known correction. It directly connects to the Hilbert-Polya conjecture (does an operator exist whose eigenvalues are the zeros?).
