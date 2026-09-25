I would authorize one final, separately preregistered cheap assay of the C=384 signal — and make it a hard closure gate.

E1 did kill the original strong claim: under severe memory pressure, TT did not earn its complexity. LOWRANK won at 128 and 192, and that result survived compute-cost perturbation. We should preserve that result exactly as-is.

But I would not throw away the 384 observation without one clean test. The reason is not merely that TT won there. The qualitative transition is interesting: held-out R^2 jumps to 0.97, lock success to 0.70, and efficiency to 5.71, while LOWRANK remains materially worse. That looks less like noise and more like a possible representation/learnability phase transition: an overcomplete TT may need temporary representational slack before ALS can discover a compact factorization.

If real, that is actually relevant to Ensorain. It would mean the important resource may not simply be final memory capacity, but working representational headroom required to discover compression.

I would therefore give Ensorain exactly one more experiment:

E1.5 — The Compression Headroom Assay

Do not change the world. Do not add new toys. Do not evolve anything. Do not GPU-optimize.

Sweep memory densely through the suspected transition, something like:

128, 160, 192, 224, 256, 320, 384, 512

For every cap, compare TT against the strongest appropriately scaled non-TT baselines, especially LOWRANK, under matched persistent memory and compute accounting.

Crucially, give the positive-control latent-order TT its own independently calibrated learning constants. Never inherit constants from TT_TUNED again. That control must pass before interpreting the sweep.

Measure separately:

* held-out R^2;
* held-out lock success;
* utility;
* compute spent learning;
* persistent parameter count;
* actual TT ranks after consolidation;
* temporary scratch/workspace;
* final compressed size.

The killer measurement is the relationship between training headroom and final representation size.

Suppose a TT needs 384 floats during learning but can subsequently round itself to 150 floats while retaining almost all of its R^2, lock success, and utility.

That would be genuinely interesting.

It would say:

Compression can require a larger transient search space than the representation eventually discovered.

That’s a much better phenomenon than “TT needs more memory.”

Conversely, if it simply needs 384 persistent floats forever, then E1 already told us what is happening: give the model more parameters and it fits better. Close it.

I’d add one very cheap intervention. At the end of every successful TT life, progressively round/compress the learned TT and measure the degradation curve:

384 \rightarrow 320 \rightarrow 256 \rightarrow 192 \rightarrow 160 \rightarrow 128

No retraining.

That gives us a direct answer to an important question E0/E1 didn’t ask:

Did the organism need 384 floats to represent what it learned, or merely to find it?

Those are profoundly different.

And I’d impose this hard verdict:

INTRIGUING — WORTH EXPLORING only if there is a reproducible transition where TT beats the strongest matched non-TT memory by >10% across at least two adjacent caps, the positive control passes, and either:

1. the learned representation can subsequently be substantially compressed without destroying competence, or
2. TT’s advantage demonstrably comes from reusable higher-order structure that the matrix baseline cannot represent efficiently.
