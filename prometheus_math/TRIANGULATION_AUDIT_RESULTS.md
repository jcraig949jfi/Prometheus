# TriangulationProtocol Independence Audit Results

_Generated: 2026-05-07 09:58:12 UTC_
_Per inbox ticket T-2026-05-07-T009 (prometheus_math/triangulation_independence_audit.py)_

## Methodology

Per `feedback_mi_bias`: MI on sparse histograms is biased upward. The audit corrects observed pairwise MI between falsifier-triggered flags by subtracting the mean MI of a random-pairing null (per-component flag vectors are independently shuffled to destroy joint dependence while preserving each component's marginal). Bias-corrected MI > threshold is flagged as a triangulation-violation candidate.

## Run Parameters

- **Kill-record store:** `F:\Prometheus\prometheus_math\_native_kill_vector_pilot.json`
- **Records audited:** 24000
- **Active components (non-constant marginal):** 1
- **Bias-correction null shuffles:** 50
- **Flagging threshold (bits):** 0.300
- **Elapsed seconds:** 4.88

## Result: No Active Pairs

**Substrate finding (data-shape gap):** 24000 kill records loaded, but only 1 component(s) have a non-constant trigger marginal. TriangulationProtocol's independence assumption cannot be empirically tested on this corpus because the records are **first-fail-only-coded** (each kill_vector captures only the single falsifier that fired first; all other components have always-0 marginals).

To unblock empirical independence verification, the kill-record pipeline must be extended to capture **joint** falsifier outcomes per claim — i.e. each candidate is evaluated against ALL falsifiers (not short-circuited at first kill) so the joint distribution is observable. Until then, this audit reports only the data-shape gap, not an independence verdict.
