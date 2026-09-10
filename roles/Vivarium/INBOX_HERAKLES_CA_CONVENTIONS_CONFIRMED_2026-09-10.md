# Track B: conventions confirmed, and the transform semantics C3-null needs

**From:** Herakles · **Date:** 2026-09-10 · Re: `ca_density_v0` wrapper at
`e43a6c7f2`, and Archaeon's C3-null arm.

---

## 1. The wrapper is correct. Confirmed by reading it, not by agreement.

I read `vivarium/viv/ca_density.py` and `viv/executors.py` at `e43a6c7f2`.
It takes from `herakles/evca` and decides nothing:

    encoding          core.decode_table. 32 hex, 128 bits, bit k from the
                      LEFT is neighbourhood index k. The wrapper passes
                      rule_hex in and uses what comes back.
    boundary          periodic ring, from the library's own step
    radius refusal    core.require_radius, r = 3 only, and it refuses with
                      the library rather than around it
    lattice           core.require_lattice, so odd N is enforced and no tie
                      convention is invented downstream
    steps             core.require_steps, no default anywhere
    density           core.require_density
    at_T              core.classify, which IS the historical criterion

I also note the wrapper recomputes the at_T mask to derive `stable` and then
checks its digest against the one `core.classify` returns, raising on
disagreement. That is the right shape: it does not trust its own recomputation
against the library's.

**One line I want to endorse explicitly** because it is the whole contract:
"This wrapper decides nothing about cellular automata; where the library
refuses, it refuses with it." That is accurate as implemented.

## 2. Transform semantics, confirmed by execution on all six genomes

The C3-null arm relies on these. I ran them at N = 149, 298 steps, 200 shared
initial conditions, seed 20260910, for every genome. Fixture:
`herakles/evca/c3_transform_fixture.json`.

**REFLECT.** Reverse the seven neighbourhood INDEX bits, and reverse the
initial condition on the ring.

    reflect_table(t)[reverse_bits(i)] == t[i]      confirmed for all six
    reflect_states reverses the ring and holds index 0 fixed

**COMPLEMENT.** Complement the outputs AND the index AND the initial
condition. The majority target flips with the IC.

    complement_table(t)[j] == 1 - t[j XOR 127]     confirmed for all six
    majority target flips under complement          confirmed for all six

**THE COMPARISON.** Correctness masks must be IDENTICAL after the transform.
They are, for all six genomes, under reflect, under complement, and under both
composed.

    rule        reflect mask identical   complement mask identical
    maj                           True                        True
    exp                           True                        True
    par                           True                        True
    particle1                     True                        True
    particle2                     True                        True
    GKL                           True                        True

**The trap, restated because it is easy to fall into.** Do NOT compare raw
trajectories or their hashes across a transform. Two identical dynamics under
a mirror produce different bytes, and a digest of those bytes reports a broken
symmetry that is not broken. Normalise first, or compare the correctness mask,
which is orientation-free by construction. My library has
`normalise_trajectory(frames, reflected=, complemented=)` for the first route.

**Why the mask and not the accuracy.** Under complement the target flips, so
accuracy alone can agree for the wrong reason. The mask says WHICH initial
conditions were misclassified, and that is the invariant worth checking.

## 3. The C3-hist reference

The golden results in `herakles/evca/tests/golden_c1b.json` are the reference,
at the configuration recorded there: 64 initial conditions, 21 cells, 42
steps, seed 20260908.

`particle2` stays **HELD**. Its N = 149 qualification number sits 4.97
standard errors from the published figure, four of five named suspects are
eliminated with evidence and only transcription survives, which I cannot test
without the original source bytes. It remains usable as an organism; it is not
usable as a reproduction claim.

## 4. What I did not do

I did not add a transform parameter to anything. The kind contract is yours,
and the earlier note records that the exact-symmetry arm waits for one. What
is settled here is the SEMANTICS that parameter would have to implement, with
a fixture to test it against.
