# H2 alpha: a precise interface obstruction, not a null result

**Herakles, 2026-09-09.** `ca_stream_v1`, alpha stage.

The alpha contract, fixtures, controls and one real CA run are complete and
27 tests pass. The run found that the configuration the brief specifies
produces an **inert substrate**, provably, for all six recovered genomes. The
design says an honest alpha receipt OR a precise interface obstruction is an
acceptable outcome. This is the second.

I have NOT changed the injection semantics to make it work. That would change
scientific meaning, and the brief routes such changes to the designer with a
minimal failing example and concrete alternatives.

---

## 1. The minimal failing example

    from herakles.ca_stream import core as cs
    from herakles.evca import genomes as G
    s = cs.CaSubstrate(G.rule_hex("GKL"), 31, (0,))
    for bit in (1, 1, 0, 1):
        print(int(s.step(bit).sum()))          # 0, 0, 0, 0

Over the complete 256-stream catalogue, for every one of the six genomes:

    total non-zero feature entries: 0 of 63488

## 2. The mechanism, proven rather than observed

Every one of the six rules outputs 0 for every neighbourhood whose popcount
is at most 1. Measured at the eight relevant indices:

    neighbourhood indices with popcount <= 1: 0, 1, 2, 4, 8, 16, 32, 64
    maj        0 0 0 0 0 0 0 0
    exp        0 0 0 0 0 0 0 0
    par        0 0 0 0 0 0 0 0
    particle1  0 0 0 0 0 0 0 0
    particle2  0 0 0 0 0 0 0 0
    GKL        0 0 0 0 0 0 0 0

So: the lattice resets to all zeros; injecting one bit at one port gives at
most a single 1; every cell then has a neighbourhood of popcount at most 1;
one step returns the all-zero lattice; the next step begins from the fixed
point again. The substrate cannot leave all-zeros through a single binary
port, for any input stream, at any horizon.

**This is a property of density-classification rules, not a defect.** A rule
whose purpose is to drive the lattice to the majority state MUST annihilate a
lone minority cell. The six genomes are good at their job, and their job is
incompatible with single-port injection from a uniform reset.

## 3. Why the instrument is nonetheless proven

Every control behaved exactly as designed on the same code path, which is
what makes the CA number readable rather than merely low.

    substrate                delayed_recall d=2   temporal_xor d=1
    ----------------------   ------------------   ----------------
    shift register                       1.0000             0.5104
    shift + xor cell, d=1                1.0000             1.0000
    direct input (equalised)             0.4922             0.5039
    frozen random (null)                 0.4922             0.4974
    any of the six CA rules              0.4922             0.4974

    direct input at delay 0              1.0000

Four facts worth keeping:

- The shift register solves delayed recall EXACTLY at every delay tested, so
  the task, the masks and the readout can pass.
- The shift register FAILS temporal XOR. That is a limitation of the LINEAR
  READOUT, not of memory: XOR of two stored bits is not linear in them. A low
  CA score on XOR is therefore not evidence that a CA lacks memory.
- The shift-plus-XOR control solves XOR only at ITS OWN declared delay, which
  is what a positive control should do and is why two of them are run.
- The direct-input baseline solves delay 0 and nothing else, and the CA rows
  match the null baseline to the last digit. If those two ever diverge,
  something is leaking input into the readout; a test now asserts they do not.

## 4. Concrete alternatives, for the designer to choose between

None of these is implemented. Each changes scientific meaning, and the first
two change it least.

1. **Non-uniform reset.** Reset to a declared random lattice at a stated
   density instead of all zeros. The rules are then operating in the regime
   they were evolved for, and an injected bit perturbs a live lattice rather
   than a fixed point. Smallest change; the reset state is already a declared
   parameter. Risk: the lattice relaxes to a uniform state within the horizon
   and the substrate dies a few steps later instead of immediately, so the
   relaxation time must be measured before the horizon is chosen.
2. **Wider injection.** Inject the bit at k ports at once, or as a block of
   k contiguous cells, with k declared. A large enough perturbation survives
   a density rule. Risk: at k near half the lattice the injection IS the
   answer to the density task, so k must stay well below the majority
   threshold and that bound should be computed before k is chosen.
3. **Different rules.** These six were evolved for density classification.
   The brief's beta stage is rule search; the alpha simply has no rule that
   suits streaming. Reaching for rule search now would skip the alpha.
4. **XOR injection instead of overwrite.** Flip the port cell rather than
   setting it. Preserves lattice mass and cannot be annihilated as easily.
   This is the largest change: it alters what "inject" means.

> **CORRECTION, 2026-09-10, from the operator. Alternative 4 above is wrong
> as written and the original text is kept above so the error stays visible.**
>
> I wrote that XOR injection "preserves lattice mass and cannot be annihilated
> as easily". It does not preserve mass, and the claim does not survive its
> own proof. From an all-zero reset, XOR-ing a bit into the port cell gives
> `0 XOR 1 = 1`, which is exactly one live cell, the same state that overwrite
> injection produces. Every cell then has a neighbourhood of popcount at most
> one, all six rules answer 0 there, and the lattice is annihilated in one
> step. The proof in section 2 applies unchanged.
>
> XOR injection is therefore NOT an escape from this obstruction on its own.
> It only differs from overwrite once the lattice is already live, which makes
> it a possible companion to alternative 1 and never a substitute for it.
>
> Verified below in `test_xor_injection_is_also_annihilated`.

**My recommendation, offered not taken:** alternative 1 first, with the
relaxation time measured before the horizon is fixed, because it changes one
already-declared parameter and keeps the injection semantics the brief pinned.

## 5. What this alpha does and does not license

**Does.** The streaming contract, the reset discipline, the hand-computed
temporal fixtures, the warm-up masks, the frozen catalogue, the disjoint
partitions with confirmation structurally out of reach of fitting, the
instrument-positive controls, the equalised-budget baselines and the cost
receipt all exist and run.

**Does not.** Nothing here is a discovered-component claim, and nothing here
is evidence that a CA cannot compute. The measured statement is narrower and
exact: *these six rules, from an all-zero reset, through one binary port,
never leave the all-zero fixed point.* Change any one of those three
conditions and the measurement says nothing.

## 6. Reproduction

    python -m pytest herakles/ca_stream/tests/ -q     # 27 passed
    python -m herakles.ca_stream.run_alpha            # writes alpha_results.json
