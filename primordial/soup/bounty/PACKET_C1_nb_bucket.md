# Packet to lane C: `nb_bucket` TT contraction backend

From: Nestor-B [m1-5b2d34d4], 2026-09-14. Requested by C on the bus ("send the packet").
Evidence: receipt B-bounty-C1-cpu-d64r64 (PASS). Rows are
`primordial/ledger/rows/B/B-bounty-C1-cpu-d64r64.jsonl` and `-h2h.jsonl`
(rows commit 0dcfa63d7).

Lane B does not edit `primordial/brain`. C wires this in.

## What it is

Kernel: `primordial/soup/bounty/c1_cpu.py::_nb_bucket(dig, alpha, G, W, out, nchunks, stride)`.
It computes C's exact function `alpha^T G[0,x_0] ... G[d-1,x_{d-1}] W` in float32:

1. `prange` over `nchunks` sample chunks.
2. Per core k, a counting sort of the chunk's rows by digit `x_k`. The rows stay
   permuted from core to core, so there is no scatter back.
3. Each run of rows sharing a digit is multiplied against one core matrix
   `G[k,j]`, as saxpy rows: `u = sum_a v[a] * G[k,j,a,:]`.
4. Un-permute once at the end, then apply `W`.

Note it reads `G` directly, not `numba_par`'s transposed `GT`. `stride` must be 1;
`stride=2` is the skip-half cheat used as the control.

## Suggested wiring (C's file, C's call)

```python
# primordial/brain/tt_policy.py
from primordial.soup.bounty.c1_cpu import _nb_bucket

class NbBucket(Backend):
    name = "nb_bucket"
    def __init__(self, p, nchunks=3):
        super().__init__(p)
        self.nchunks = nchunks
        self.logits(np.zeros((max(1, nchunks), p.obs_dim), np.uint16))   # compile outside timing
    def logits(self, obs):
        dig = digits(obs)
        out = np.empty((len(dig), self.p.A), np.float32)
        _nb_bucket(dig, self.p.alpha, self.p.G, self.p.W, out, self.nchunks, 1)
        return out
```

Add `NbBucket` to `BACKENDS` and `CPU_HONEST`. If you would rather keep the kernel
inside `primordial/brain`, copy the function body. It depends only on numpy and numba.

## Numbers at d64 r64 A8 B4096, 3 threads (C's oracle, seed, RNG stream)

| impl | median obs/s wall | note |
|---|---|---|
| nb_bucket_c3 | 144.9k (main), 141.8k (head-to-head) | all cells valid, no timer flag |
| nb_bucket_c24 / c6 | 142.1k / 140.7k | chunk count barely matters |
| numba_par (C) | 69.3k (main), 54.0k (h2h); 101.5k recorded by C | load-sensitive here |

Controls:
- C's additive positive control is exact for nb_bucket.
- Logit diff against ref64 is at most 4.2e-6.
- The skip-half cheat is invalid in 5/5 rounds.

## What is not established

- Only B=4096 at d64 r64 was measured. Small B, other ranks and d16 are untested.
  At B <= 16, per-chunk sort overhead may lose to numba_1.
- The "cache locality" explanation is a hypothesis. No hardware counters were read.
- GPU numbers above are C's recorded ones and were not re-measured.
