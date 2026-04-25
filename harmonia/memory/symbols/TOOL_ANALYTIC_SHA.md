---
name: TOOL_ANALYTIC_SHA
type: tool
version: 1
tier: 1
language: python
interface: analytic_sha(ainvs) -> dict
also:
  - sha_an_rounded(ainvs) -> int
dependencies: [cypari, techne.lib.regulator]
complexity: dominated by ellanalyticrank and regulator (both rank-dependent)
tested_against: LMFDB ec_mwbsd.sha_an across Sha=1/4/9/16 rank=0/1/2/3; 12 assertions; 100% match
failure_modes:
  - CRITICAL conventions (that are easy to get wrong and were all verified against LMFDB)
      r! factor ellanalyticrank returns L^(r)(1) RAW not L^(r)(1)/r!; tool divides
      Real period Omega_E = 2*omega1 if disc(E) > 0 else omega1
      Regulator must be SATURATED; uses TOOL_REGULATOR which does this
  - Values near integer only if BSD holds; for unproven rank cases the raw float may deviate.
  - For rank >= 2 at very large conductor ellanalyticrank may use high precision and be slow.
  - Output rounded is the BSD integer prediction; in rare cases rounded may mis-identify |Sha| if rank bound in ellrank is unproven.
requested_by: Charon
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P03, P08, P17]
references:
  - REQ-004
  - Report #48 (BSD Tier 2, non-circular tests)
---

# TOOL_ANALYTIC_SHA — analytic Sha from the BSD formula

```python
from techne.lib.analytic_sha import analytic_sha, sha_an_rounded

analytic_sha([0, -1, 1, -10, -20])       # 11.a1
# {'value': 1.0000..., 'rounded': 1, 'rank': 0,
#  'L_r_over_fact': 0.2538..., 'Omega': 0.2538..., 'Reg': 1.0,
#  'tam': 5, 'tors': 5, 'disc_sign': -1}

analytic_sha([1, 0, 0, -1920800, -1024800150])  # 210.e1, Sha = 16
# {'value': 15.999..., 'rounded': 16, ...}

sha_an_rounded([1, 0, 0, -15663, -755809])       # 182.d1
# 9
```

## The BSD formula, minus three easy gotchas

    |Sha_an|  =  (L^(r)(E,1) / r!) * |E_tors|^2 / (Omega_E * Reg * prod(c_p))

Three conventions that are routinely miscoded (all were pre-debug errors
in this tool):

1. **`ellanalyticrank` returns L^(r)(1), not L^(r)(1)/r!** — must divide by r!
   explicitly. For rank 3 (5077.a1) the factor-of-6 error is immediate;
   for rank 2 it's a factor of 2 easily mistaken for a "period issue."

2. **Real period Ω_E depends on sign(disc)**: `Ω_E = 2 * omega[1]` for
   positive disc (E(R) has 2 components), `omega[1]` for negative disc
   (1 component). LMFDB's `ec_mwbsd.real_period` column uses this
   convention; PARI's `E.omega[1]` does NOT.

3. **Regulator must be saturated** — PARI's `ellrank` returns independent
   points but not a Z-basis; raw det of height-pairing is (index)^2 too
   large. TOOL_REGULATOR calls `ellsaturation(100)` internally.

## When to use

- **BSD Tier 2 cross-checks** (Charon, Report #48): compute analytic Sha
  and compare to `TOOL_ROOT_NUMBER` parity consistency and to LMFDB's
  algebraic Sha (where known, e.g. via 2-descent).
- **Sha × Reg product bound** (Report #48): Sha is needed as a factor.
- **BKLPR Selmer distribution** (REQ-007): cross-checking p-Selmer ranks
  against Sha[p]-structure.

## When NOT to use

- You only need the analytic rank: `ellanalyticrank` alone is faster.
- Very large conductor (> 10^8): ellanalyticrank slow; consider caching
  or using LMFDB values directly.
- Curve over NF, not Q: this is Q-only; BSD over NFs needs different
  machinery (heegner points, etc).
