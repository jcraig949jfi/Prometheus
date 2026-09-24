Ensorain[m2-14baf7d5] E1.5 (final assay of the Tensor World Engine
premise) CLOSED 2026-09-23. Frozen rule: CLOSE (B). The operator's
"compression needs transient headroom" hypothesis is falsified: with the
right mode order and enough ALS sweeps a tensor-train memory learns the
world at EXACTLY its true size (192 floats, held-out R^2 0.96-0.98) and
cannot be rounded below it without losing most of its utility. At that
size it beats every other memory 4x per parameter in two replicate sets --
but the world is itself a tensor train, so that is matched inductive bias,
and the hard part (finding the mode order) came from random search, not
learning. Useful beyond Ensorain: a per-cap hyperparameter search that
hits or misses can masquerade as a capacity phase transition. Verdict:
ensorain/E1P5_VERDICT.md. No ask.
