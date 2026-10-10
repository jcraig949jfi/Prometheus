# REACH01 R1 / TEST-4 RESULT: recoil + exchange -- information or arithmetic?

Freeze a2ce3c471. Production 09:39Z-12:5xZ on 2026-10-10:
- decode 32/32 and trace 33/33 rc=0;
- clamp / non-ancestor 64/64 rc=0;
- dup_RX_s0 identical.
Evidence: R1/evidence/ (reductions, non-ancestor check, ledgers). Features (npz) in
C:/Prometheus-data/aether_reach01/R1/decode/ (untracked).
Laws: bit-identical to aeth03_variants (V1, X = mob_r0x1e0, R = mob_r1x0e0, RX = mob_r1x1e0). Ruler fixtures 3/3
(exchange decodes at r=1 only; relay chain decodes at r=1..6; label-unrelated divergence at chance).

## Disposition: RECOIL_EXCHANGE_CAUSAL_REACH_NOT_SUPPORTED
Both preregistered conditions fail.

### 1. Decodability of the planted value (held-out, leave-one-seed-out, chance 0.125)
Mean accuracy by radius (over ticks and seeds):

| radius | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| RX recoil + exchange | 0.619 | 0.190 | 0.141 | 0.126 | 0.125 | 0.125 |
| X exchange only | 0.531 | 0.141 | 0.125 | 0.125 | 0.125 | 0.125 |
| R recoil only | 0.889 | 0.185 | 0.126 | 0.126 | 0.125 | 0.125 |
| V1 | 0.871 | 0.142 | 0.125 | 0.125 | 0.125 | 0.125 |

- Dstat (mean excess over chance, r = 2..6): RX 0.014-0.020, X 0.001-0.005, R 0.010-0.018, V1 0.001-0.005.
  Label-shuffled null ~0.000.
- RX exceeds X in 8/8 seeds, but by ~0.010-0.015, below the preregistered margin of 0.02: **0/8 seeds qualify**.
- RX's radius-2/3 information is real but small (accuracy 0.19 at r=2, 0.14 at r=3).
- Recoil ALONE gives almost the same radius-2 information (0.185). The excess over exchange is mostly recoil's,
  not the composition's.
- Beyond radius 3 nothing is decodable in any law.

### 2. Causal descendants (PROP01 tracer, payload bit impulse, 3000 ticks)

| law | MULTIGENERATION seeds | of these, non-ancestor control keeps >= 0.5 of descendants | max gen / sites / radius |
|---|---|---|---|
| RX | 3 (s3, s4, s5) | 2 (s4, s5; s3 had no non-tree site at B's distance) | 8 / 42 / 6 |
| X | 3 (s2, s3, s6) | 3 | 2 / 3 / 2 |
| R | 3 (s3, s6, s7) | 3 | 4 / 13 / 2 |
| V1 | 2 (s4, s7) | 2 | 2 / 3 / 1 |

- The rule (RX certified >= 3 AND >= X + 2) fails: 2 vs 3.

Shape (descriptive; not promoted):
- RX produces by far the deepest causal trees in the Aether record.
  - s4: 6 generations, 18 sites. Clamping intermediate B removes all 13 of its descendants; clamping a
    non-ancestor at B's distance keeps all 13.
  - s3: 8 generations, 42 sites, 34 STRUCT events at gen >= 2 (the divergence changes WHO writes, repeatedly).
    Its clamp removes B's 9 descendants, but the control was unavailable.
- X's "chains" are 1-descendant affairs.
- So recoil + exchange can sustain genuinely multi-generation causal trees: A alters B, B alters C, and clamping B
  removes C, with a non-ancestor clamp leaving C intact.
- It does so in 2-3 of 8 seeds, not reproducibly enough, and its content information still dies by radius 3.

## Reading
TEST-3's P1 mobility finding is retained, NOT promoted to computational circuitry. Recoil + exchange is "a local
dynamical regime" with occasional deep causal trees, whose trees mostly carry divergence in WHO writes (STRUCT) rather
than decodable content.
- The information it carries beyond radius 1 is small and largely attributable to recoil.
- Answer to the R1 question: mostly arithmetic and transport, with rare structural cascades. It is not
  information-preserving transmission through multiple interactions.

## Cognitive accounting
- Substrate: the local laws.
- Certifier: decoder, tracer, clamps.
- No search and no developmental machinery.

## Limitations
- One impulse type (payload value / bit) and one origin rule.
- Horizon 200 ticks (decode) / 3000 (trace).
- 512^2, D50, P0, B_balanced (TEST-3 used 128^2 and a perturbation-ON warm-up).
