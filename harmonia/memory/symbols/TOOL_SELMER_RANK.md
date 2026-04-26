---
name: TOOL_SELMER_RANK
type: tool
version: 1
tier: 1
language: python
interface: selmer_2_rank(ainvs, effort=1) -> int
also:
  - selmer_2_data(ainvs, effort=1) -> dict (dim_sel_2, rank_lo, rank_hi, rank_proved, sha2_lower, dim_E2)
dependencies: [cypari]
complexity: dominated by 2-descent in PARI ellrank
tested_against: rank 0/1/2/3 trivial-Sha; 571.b1 (Sel_2=2); 66.b1 (Sel_2=3 with 2-tors); 210.e1 (unproved rank, Sel_2=3)
failure_modes:
  - Formula subtlety dim Sel_2 equals max(rank_lo + s, rank_hi) + dim E(Q)[2]. When rank is proved (rank_lo==rank_hi), s = dim Sha[2] exactly. When rank unproved, s=0 and rank_hi is the Selmer bound.
  - Higher-prime Selmer (p=3, 5, ...) not implemented; PARI has no built-in p-Selmer for p > 2. Would need Magma or hand-rolled p-descent.
  - For curves with very large conductor ellrank may be slow; consider precomputed LMFDB values.
  - For unproved-rank curves (rank_lo != rank_hi), effort can be raised but at runtime cost.
requested_by: Charon
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P03, P08, P17]
references:
  - REQ-007
  - Reports #14 and #54 (BKLPR Selmer distribution test)
---

# TOOL_SELMER_RANK — 2-Selmer rank of an elliptic curve

```python
from techne.lib.selmer_rank import selmer_2_rank, selmer_2_data

selmer_2_rank([0, -1, 1, -10, -20])         # 11.a1 trivial Sha -> 0
selmer_2_rank([0, -1, 1, -929, -10595])     # 571.b1 Sha=(Z/2)^2 -> 2

selmer_2_data([1, 0, 0, -1920800, -1024800150])   # 210.e1
# {'dim_sel_2': 3, 'rank_lo': 0, 'rank_hi': 2,
#  'rank_proved': False, 'sha2_lower': 0, 'dim_E2': 1}
```

## Why this tool exists

- **BKLPR Selmer distribution** (Reports #14, #54): the primary statistic for
  testing the Bhargava-Kane-Lenstra-Poonen-Rains heuristic on Sha ranks.
  Need dim_F2 Sel_2 across a large family of curves.
- **BSD consistency**: combine with `analytic_sha` to check
  Sha_an[2]-structure matches the Sha-ranks predicted by 2-descent.

## The formula, explained

The 2-Selmer group sits in  0 → E(Q)/2E(Q) → Sel_2(E) → Sha(E)[2] → 0, so

    dim Sel_2 = rank + dim Sha[2] + dim E[2](Q)

PARI's `ellrank` returns `[rank_lo, rank_hi, s, points]`:
- `rank_lo`: lower bound on rank (via exhibited points)
- `rank_hi`: 2-descent Selmer bound (rank + dim Sha[2] ≤ rank_hi)
- `s`: when `rank_lo == rank_hi`, `s = dim Sha[2]` exactly. Else `s = 0`.

Hence  `dim Sel_2 = max(rank_lo + s, rank_hi) + dim E[2](Q)`  in all cases.

## When NOT to use

- You need p-Selmer for p > 2: not supported; requires Magma or hand-rolled
  p-descent (not in our current toolchain).
- You need Sha itself, not Sha[p]: use TOOL_ANALYTIC_SHA and sanity-check
  against dim Sel_2.
- Very large conductor (10^8+) with unproved rank: increase `effort` or
  consult LMFDB precomputed values.
