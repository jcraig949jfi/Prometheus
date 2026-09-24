I would authorize E1, but only as a deliberately hostile, cheap falsifier. E0 did its job: it found that the current world rewards coarse action-ranking, not faithful structural learning. That makes F1 very plausibly a world-design artifact rather than evidence against the broader Ensorain premise.

The giveaway is the combination of facts: TT and other learners can obtain substantial harvest with essentially zero held-out-cell R^2; evolved TT ranks collapse toward 1–2; mode order is unstable; and a 64×64 matrix factorization beats the TT. If survival only asks “which of these four local exits looks best?”, an organism can be catastrophically wrong about the world globally while still preserving enough ordering information locally to eat. In that regime, the world is selecting a cheap preference function, not a compressed world model.

The positive-control failure means E0 cannot answer the stronger question anyway. A planted TT world whose TT learner cannot recover its structure within the lifetime makes “TT versus non-TT” uninterpretable. That is exactly what INDETERMINATE (controls) should mean.

I would not rescue the E0 learner. The three preregistered learner rounds are exhausted, and continuing to tune it would contaminate the experiment. Freeze E0 permanently as a useful negative result.

What E1 should change

E1 should make fine structure causally necessary for survival. Not harder for hardness’s sake; specifically impossible to succeed by getting only local ranking approximately right.

I would build one small world with several coupled requirements. An organism should encounter delayed tensor locks where the answer depends on values or factors observed far earlier; pairs of locally indistinguishable states whose correct actions differ only because of latent context; puzzles where approximately correct ranking gives zero reward unless the reconstructed quantity crosses a tight tolerance; and unseen regions generated from the same factors so transfer is measurable. A rank-1 “good vibes about this neighborhood” representation should get slaughtered.

Most importantly, make the world require cross-context reuse. For example, hide factors A,B,C,D throughout the environment. Early chambers reveal different projections of them. Later locks require combinations such as A\otimes C, contractions involving B, or transformed versions of D. The organism never has enough memory to retain all observations. The shortest successful strategy should be discovering and storing reusable factors.

Then add the charged batch-consolidation operation you proposed. This fixes the current mismatch without giving TT a free advantage: every arm can spend energy to reorganize its bounded memory from accumulated samples. TT can use ALS/rounding; LOWRANK can use its appropriate factorization; vector/recurrent baselines get comparable fitting opportunities. Charge actual or proxy compute and count the temporary workspace against a separately declared scratch allowance.

I would make the decisive E1 criterion harsher than “TT gets more harvest”:

\text{useful representation efficiency}
=
\frac{
\text{held-out transfer utility}
+
\text{future compute saved}
+
\text{survival/puzzle utility}
}{
\text{persistent parameters}
}

That is essentially the remainder of the §12 idea that got cut off: compression only matters insofar as useful future information survives the compression. Small memory by itself is not success.

And I like the existing kill condition:

If any non-TT memory comes within 10% of the best TT at matched persistent memory and matched compute budget, B stands.

I’d make that the governing gate, not merely one secondary falsifier.

There are two additional controls I’d add. First, a latent-order oracle TT using the same learning machinery as the experimental TT. It must clear the positive-control threshold before TT-specific claims are even scored. Second, a world-basis rotation/permutation transplant: train on one representation of the latent factors and test on an equivalent transformed representation. If the organism learned reusable structure rather than coordinates or superficial geometry, some competence should survive or rapidly reacquire.

The interesting E1 result is therefore not “TT wins.” It is something much narrower and more valuable:

Under severe memory pressure, when survival genuinely requires retaining fine latent structure across contexts, a tensor-structured memory achieves materially more transferable competence per stored parameter and per unit compute than simpler representations.

If that doesn’t happen, I’d close this branch of Ensorain with a clean conscience.

If it does happen, then Ensorain has finally earned E2.

And I would keep GPU work off the critical path. E1 should be small enough to run cheaply on CPU/local GPU. No Runpod, no scale, no tensor weather, no societies. One more knife fight with the premise.
