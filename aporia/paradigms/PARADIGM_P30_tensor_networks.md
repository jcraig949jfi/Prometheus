# PARADIGM P30 — Tensor Network Contraction (worked example + decision tree + code skeleton)

Aporia P97, 2026-08-21. Source: taxonomy P30 (tensor round; DMRG/PEPS
exemplar; catalog refs #49-51, #75-78, #82-84). Consumer: Learner corpus
type C. Emitted to paradigm_trees.jsonl. Tier 29/30. **Cross-channel bind
#2: Techne's prometheus_math/tensor_train.py (cycle 002).**

**The move**: represent a big tensor as a network of small ones; computation
IS contraction order; approximation IS bond truncation (verb:
CONTRACT-THE-NETWORK; payoff verb: SIDESTEP-ENUMERATION-BY-REPRESENTATION).

## 1. Worked example — EXECUTED (`paradigm_p30_worked_example.py`)

- **A.** TT round-trips through Techne's engine on DERIVED-rank tensors:
  rank-1 outer product → TT ranks all 1; diagonal ⟨2⟩ on four axes → TT
  ranks all 2; both reconstructions exact. (opt_einsum probed absent — the
  derived DP below stood in.)
- **B.** Contraction order as optimization: the matrix-chain DP (derived
  in-code) gated against brute-force enumeration of ALL parenthesizations
  on 20 random chains — then the contrast at length 10: optimal 33,085
  multiplications vs left-to-right 95,040 (**2.87×**) — order IS the
  computation.
- **C.** The truncation trade, decline-capable: a random full tensor's error
  falls monotonically (0.93 → 0) as the cutoff tightens, while the
  structured rank-1 tensor truncates to 4e-16 immediately — structure IS
  compressibility, exhibited as a contrast. Verdict: **NETWORK-CONTRACTS**.

## 2. Decision tree

- Q1: Is the object a HIGH-ORDER tensor whose entries are needed only
  through CONTRACTIONS (expectations, marginals, inner products) — never
  all at once? — NO: if you need the dense tensor, networks only add
  plumbing.
- Q1 YES — Q2: Does the object plausibly have LOW BOND DIMENSION (1D-chain
  structure, limited entanglement, low TT ranks on probes)? — NO: bond
  dimensions grow exponentially for generic tensors (leg C's random case);
  networks without structure are dense storage in disguise.
- Q2 YES — Q3: Is the contraction ORDER optimized (DP/treewidth for chains
  and trees; heuristics gated on exact small cases for general graphs)?
  — NO: a bad order can cost more than enumeration; optimize or exit.
- Q3 YES — EXECUTE: verify round-trips exactly on derived-rank probes,
  quantify the truncation trade with monotone-error curves, and state
  which format (TT/PEPS/MERA) matches the object's connectivity.

## 3. Code skeleton

```python
def network_attack(tensor_probe, tt_engine, chains):
    """P30 template. Derived-rank round-trip gates; order-DP gated on brute
    force; the truncation curve is the honesty instrument."""
    for T, derived_ranks in tensor_probe:
        assert tt_engine.ranks(T) == derived_ranks
        assert exact(tt_engine.reconstruct(T), T)
    for dims in chains.small:
        assert chain_dp(dims) == min(brute_parenthesizations(dims))
    return {"order_gain": worst_cost / chain_dp(chains.target),
            "truncation_curve": error_vs_cutoff(tensor_probe.random)}
```

## 4. Catalog assignment

Primary: tensor_open_problems_v1.md #49-51, #75-78, #82-84 (taxonomy refs);
Prometheus-internal: THE paradigm for the unified-tensor build (HARD-3, per
the taxonomy) — the dissection tensor's eventual large-scale representation.
Cross-channel: Techne's TT lane is both supplier (this bind) and consumer.
Anti-assignment: all triage MATH rows; dense small tensors (Q1's guard).

## Provenance and honesty

TT/DMRG is settled numerics; the content is the second cross-channel bind
(consuming Techne's engine with derived-rank gates), the DP-gated order
contrast, and the structure-vs-random truncation exhibit. The PARI banner
noise in Techne's import chain is noted for that channel once more.
