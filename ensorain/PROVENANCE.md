# Ensorain provenance

Currency: 2026-09-23. Every external idea or algorithm used in ensorain/,
with its source. No external code was copied; everything is written from
the cited descriptions.

| used in | idea | source |
|---|---|---|
| e0/tt.py TT, tt_svd | tensor-train format; TT-SVD (sequential truncated SVD of unfoldings); TT ranks = ranks of the sequential unfoldings | I. V. Oseledets, "Tensor-Train Decomposition", SIAM J. Sci. Comput. 33(5):2295-2317, 2011, doi:10.1137/090752286 |
| e0/tt.py ranks_of_order | TT rank depends on mode ordering (the rank of each unfolding changes under permutation) | same; standard MPS observation |
| e0/tt.py update "joint" | normalised LMS step (error times gradient over squared gradient norm) applied to the multilinear map | B. Widrow, M. E. Hoff (1960) LMS; NLMS textbook form (e.g. Haykin, Adaptive Filter Theory) |
| e0/tt.py update "sgd" | plain stochastic gradient on squared error with step clipping | standard |
| e0/als_ceiling.py | alternating least squares for TT completion from sampled entries (the "literature" reference arm) | L. Grasedyck, M. Kluge, S. Kraemer, "Variants of alternating least squares tensor completion in the tensor train format", SIAM J. Sci. Comput. 37(5):A2424-A2450, 2015, doi:10.1137/130942401 |
| e0/memories.py RF | random ReLU features + linear readout | A. Rahimi, B. Recht, "Random Features for Large-Scale Kernel Machines", NIPS 2007 |
| e0/memories.py LOWRANK | online matrix factorisation by SGD on observed entries of an unfolding | standard (e.g. Koren, Bell, Volinsky, IEEE Computer 2009, doi:10.1109/MC.2009.263) |
| e0/memories.py HASH | direct-mapped table with collisions (sketch-like memory); Knuth multiplicative hash constant 2654435761 | D. Knuth, TAOCP vol. 3 s6.4 |
| e0/evolve.py | (mu+lambda)-style GA, tournament selection, elitism with re-evaluation | standard evolutionary computation |

Prometheus-internal borrowings: archaeon/workspace.py (canonical guard,
receipts), comms/manifest.py (LF-normalised manifests); doctrine on
positive/negative/cheat controls from roles/base-role/RESPONSIBILITIES.md s2.
