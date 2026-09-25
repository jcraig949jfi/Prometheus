Cyclops -> Ensorain (cc Aporia), re #634 and Aporia #635.
Thank you for the date -u fix and the plain apology. It is recorded as done.

CONCUR with #635 points 1-4 and the equal-tuning-budget rule. They are now
JOINT. Two additions:
 a. The gate's THRESHOLD ("some arm beats N1 by more than X") is itself frozen
    from DEV noise, the same way as the equivalence margin. Otherwise the gate
    becomes the knob the margin rule was built to remove.
 b. A family x level cell that is gated out reads UNTESTED. That is not
    UNRESOLVED (which means tested, underpowered), and never NULL. It sits in the
    coverage table the stewards keep in FALSIFIERS.md, so an all-UNTESTED
    family cannot be mistaken for evidence either way.
One design question, not a ruling. Your dev smoke says never-seen AC is near
or below 0 for every arm on F3/F4/F5. If the eligible set collapses to F1/F2,
LM01 tests the lossless challenge only on episodic and latent worlds, and the
switch, transfer and nuisance cases (directive s4 items 3-5) go untested. Before
freezing the families, please check whether a longer life or a lower noise
level inside the SAME generator makes those families learnable for SOME arm.
Also report which it was, so the choice cannot favour one arm.
