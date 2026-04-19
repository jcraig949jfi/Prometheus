# Track B — F011 Rank-0 Residual Independent-Unfolding Check

**Role:** Single-purpose audit
**Delegated:** 2026-04-19 by Harmonia sessionA
**Status:** in flight
**Expected deliverables:**
  - `cartography/docs/F011_independent_unfolding_check.md`
  - `cartography/docs/F011_independent_unfolding_results.json`
  - `WORK_COMPLETE` sync message with verdict: SURVIVES | METHOD_SENSITIVE | COLLAPSES

---

## Paste-ready prompt

```
You are [Harmonia sessionB (recommended — continuity) or Koios].
Role: single-purpose audit. F011's rank-0 ~23% residual (under
classical 1/log(N) ansatz, z_block = 4.19 with torsion_bin stratifier)
is now the most interesting non-calibration, non-tautology signal
after F043's retraction. It is flagged PROVISIONAL pending an
independent unfolding check. Your job: run that check.

Working directory: Prometheus clone. Pull latest first.

Read first:
  harmonia/memory/build_landscape_tensor.py  — F011 current description
  harmonia/memory/decisions_for_james.md    — the retraction context
  harmonia/memory/symbols/EPS011.md          — the constant spec
  harmonia/wsw_F011_rank0_residual.py        — sessionB prior fit code
  harmonia/wsw_F011_rank0_deep.py            — three-ansatz decay fit

Task: test whether the rank-0 ~23% residual survives an alternative
unfolding convention — i.e., whether the finding depends on LMFDB's
specific zero-spacing normalization or is method-independent.

Method (minimum viable — do at least one):

Option 1 (preferred if tractable): pull zeros from a non-LMFDB source
  for a rank-0 EC sample. Candidates:
    - Sage's L-function zero computation for a sampled subset
      (sage.math.lmfdb may not work but Sage directly can compute
      Dirichlet coefficients + zeros from a_p)
    - Rubinstein's lcalc if available
    - Magma's L-function machinery

  If ANY independent source available: compute gamma_1_unfolded on
  ~1000 rank-0 EC from that source, fit the same classical
  1/log(N) ansatz, compare eps_0 to the LMFDB-based 22.90 +/- 0.78.
  Match within 2 sigma -> F011 residual survives.
  Gap > 2 sigma -> LMFDB-specific unfolding contributes > noise;
  F011 LAYER 2 becomes "LMFDB-dependent," downgrade.

Option 2 (fallback if no independent source): apply two different
  unfolding conventions on the same LMFDB data:
    - Standard: gamma_unfolded = gamma * log(N) / (2*pi) (what we
      currently use)
    - Alternative: density-based via the Riemann-von Mangoldt formula
      directly, N(T) = (T/(2*pi)) log(T/(2*pi*e)) — refit at each
      conductor decade, recompute eps_0 under both
  If eps_0 agrees across conventions within 10%: unfolding is not
  the dominant artifact source.
  If diverges: LAYER 2 claim is method-sensitive; downgrade.

Option 3 (sanity check, cheap, always run): shuffle the rank-0
  population by rank-preserving random permutation of conductor,
  refit decay. This is a plain-null baseline; a meaningful residual
  should give eps_0 = 0 +/- noise. If the shuffle gives nonzero
  eps_0, our fit is finding structure in random conductor-gamma
  assignments — which would be a methodological issue we need to
  know.

Constraints:
  - Do NOT touch any other F-ID or projection
  - Report eps_0 with CI under each method you ran
  - Pattern 30 check: eps_0 is a decay parameter on first-gap variance
    vs conductor; log(N) is inside the ansatz by construction but is
    not itself the dependent variable — so not an algebraic-identity
    case. Still, confirm in writing.

Output:
  - cartography/docs/F011_independent_unfolding_check.md with:
      methodology chosen, eps_0 per method, CIs, verdict
  - cartography/docs/F011_independent_unfolding_results.json
  - Commit prefix: "F011 unfolding audit:"
  - WORK_COMPLETE on agora:harmonia_sync with the headline verdict:
      SURVIVES | METHOD_SENSITIVE | COLLAPSES
  - If SURVIVES: also post an ε₀₁₁@v2 symbol draft updating the
    constant symbol with the independent-method cross-check added
  - If METHOD_SENSITIVE or COLLAPSES: flag for sessionA conductor
    review; do not update the tensor F011 cell unilaterally

Charter context: after F043's retraction, this is THE test of whether
the tensor still contains any non-trivial frontier claim at all.
Either outcome is informative: SURVIVES means we have one real
frontier observation to build on; COLLAPSES means the first wave
produced zero surviving frontier findings, which is also a useful
data point about the approach at current density.
```

---

## Background motivation

After F043's retraction (commit df20f900), F011's rank-0 ~23% residual
is the single most interesting non-calibration, non-tautology signal
in the tensor. The residual survived a block-shuffle-within-torsion-bin
null at `z_block = 4.19`, but the external reviewer flagged it as
provisional pending an independent unfolding check: the finding may
depend on LMFDB's specific zero-spacing normalization rather than
being method-independent structure.

Either outcome of this audit is informative:
- SURVIVES → one real frontier observation remains to build on post-F043
- COLLAPSES → the first wave produced zero surviving frontier findings
  at current density, which is itself useful data about the approach

The task is tractable — Option 3 alone (shuffle sanity check) is
cheap and catches the worst failure mode (residual from random
conductor assignment).
