# s4 v2.1 conformance review (2 fresh Fabric replicas, ubu001)

Subject: tracer/s4v2.py v2.1, LF sha256 3d9eb155c54baf4324a3282b472bad82a4d498938fcc29da297876b3b6677a0c (commit 88b9d0a13 / b3f1e6015).

| replica | Fabric task | verdict |
|---|---|---|
| 1 | tsk-5b65fada2d69 (att-0e8528760bb0) | DOES NOT CONFORM |
| 2 | tsk-6e51a53bfbf6 (att-02d192786679) | DOES NOT CONFORM |

Both replicas report the same blocking finding, B1: the floor verdict was taken from the CI alone, and MARGINAL replaced the decision. Neither replica could run Python (the worker denied it), so the tallies were recomputed by hand from the committed files and the bootstrap CIs were not re-run. Every K_R1 total and point estimate reproduced exactly.

Consequence: the v2.1 tallies are NOT usable (GO_FINAL addendum 1: usable only if both replicas return CONFORMS). The repair is s4 v2.2 (tracer/s4v2.py docstring V1-V7). Its hash is posted before it runs, and it goes to 2 fresh replicas.

Correct K_R1 gates under the conforming rule, as both replicas state them (a reading, not usable):
- flip coverage FAILS in every gated class; "other" also carries the MARGINAL mark;
- FAILED share PASSES;
- completeness leak PASSES.

This does not broaden any claim. The ancestry replay remains INCONCLUSIVE on the frozen v4 s2.1 reading.
