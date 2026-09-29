# AMENDMENTS to PREREG.md (PREREG.md itself is never edited)

## A1 -- 2026-09-28, after gate run 1, BEFORE any unplanted run

Gate run 1 (known_answer_run1_GATE_FAILED.json, n = 20 worlds/arm) FAILED
on exactly one criterion: AA_valid_all_arms. In arm C the A/A statistic
(two intact probes, eval seeds 0..15 vs 100..115) was 0.008, 95% CI
[0.004, 0.012], excluding 0. Every other gate criterion held (P: R3,
INSTALLED, no R4/R5; N_a: R0; N_b: none; C: R2 with R3 failing on
permutation and random-record content tests; P4: R4).

Diagnosis: PREREG s3 fixed the eval seeds as "0..15" for every world, so
the organism coin draws in the probe are IDENTICAL across worlds (common
random numbers across worlds, not only across arms within a world). The
per-world A/A differences are therefore correlated, and a bootstrap over
worlds treats them as independent -> the A/A CI is too narrow. In C every
world has identical deterministic readers, so the correlated coin noise
survives averaging and the CI excluded 0. This is an apparatus defect
(pseudo-replication), not a property of the cheat. The same defect
narrows every other CI slightly; the gate-relevant effects in run 1 are
10-60x larger than the A/A offset.

Repair (the only change): all probe RNG seeds are salted with a per-world
evaluator-side value (first word of the world's physics-RNG state at S*),
so eval noise is common across arms within a world (paired design kept)
but independent across worlds. Code: battery.world_salt(); s1(), window(),
fresh_world_transfer(). No threshold, arm, statistic or world parameter
changed. The gate is re-run in full (run 2 = known_answer.json) and its
verdict is the one that counts; run 1 is kept for the record.

Lesson for ACCUMULATION_v0 / PREREG template: "common random numbers"
must be specified as WITHIN-world pairing only; the A/A control caught
this, which is what it is for.
