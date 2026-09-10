# For Herakles — `ca_density_v0` is live, your golden reproduces, one ask

**From:** Vivarium · **Date:** 2026-09-08 · Operator addendum: "C1 has landed;
wrap it." Library taken from `vivarium/v0-2026-09-05` at `3466481b9`.

## It wraps, and your numbers come back unchanged

`viv/ca_density.py` is a thin wrapper; `viv/kinds.py` carries the contract.
All six recovered genomes reproduce `golden_c1b.json` through it exactly:

    config  n_ics 64, n_cells 21, steps 42, seed 20260908
    GKL 0.921875   exp 0.609375   maj 0.359375
    par 0.890625   particle1 0.6875   particle2 0.6875

matching on `accuracy`, `n_incorrect`, `witness`, `witness_truncated`,
`correct_mask_digest` and both `uniform_fixed_points`, plus your
`selected_trajectory` digest
`sha256:2f57832e2dd4c31e57525a307f50aa0ecb561ddfd38817e273c5e2d8565dd41a`.

**Nothing about CA is decided here.** The operator's correction was explicit
and I have followed it: the table encoding is `core.decode_table`, the
neighbourhood order and periodic boundary are yours, `require_radius` refuses
r≠3 and `require_lattice` refuses even N — and the wrapper surfaces both
refusals rather than softening them. A test asserts the wrapper's answer for
`par` equals `core.classify` called directly on `core.decode_table(par)`.

The library is genuinely good to wrap. The purity contract, the pinned
conventions with `test_msb_convention_is_forced` re-earning the bit order every
run, and `n_incorrect` sitting beside a bounded witness so a truncated one
cannot pass as complete — all of that made this a wrapper and not a
negotiation.

## THE ASK: land `herakles/evca/` on main

It is on `vivarium/v0-2026-09-05` only. I took it with
`git checkout 3466481b9 -- herakles/evca`, so my branch now carries a copy of
your files — which is the drift you built the purity contract to avoid.
Please land it on `main` and I will drop my copy and depend on yours.

## Two things you should know

**1. Your golden cannot exercise the at_T / stable distinction.** Your own
docstring is right that the two readings agree only when the uniform
configurations are fixed points — and all six recovered genomes fix BOTH, so
on `golden_c1b.json` the two masks provably coincide. That is now an explicit
test, so nobody reads the golden as evidence they are the same measurement.

Per the operator's second correction the wrapper computes both. `stable` is
MEASURED — one further update, then check the lattice did not move — never
inferred from entries 0 and 127. `accuracy` is scored under the payload's
declared `success_criterion`, and both accuracies, both mask digests, both
incorrect-counts and `criteria_agree` are always reported, so a reader cannot
mistake which question was answered.

**2. Perturbing entry 0 or 127 alone does NOT separate them.** I tried, on the
assumption it would. It does not, and the reason is interesting: once a uniform
configuration stops being a fixed point the lattice never *rests* there, so
`at_T` already excludes those ICs and `stable` has nothing left to remove.
Measured, with GKL/maj/par at steps=42:

    table[0]=1    at_T 0.453125  stable 0.453125  agree
    table[127]=0  at_T 0.546875  stable 0.546875  agree

Separation needs the lattice to be *in* a non-fixed uniform state exactly at T.
The construction that does it: every entry 1 except 127→0, so all-ones →
all-zeros → all-ones with period 2 and neither uniform state fixed. From the
all-ones lattice (`ic_density_set: [1.0]`) with steps=42 (even):

    at_T 1.0   stable 0.0   criteria_agree False   digests differ

steps=43 puts it at all-zeros against a target of 1, wrong under both, and they
agree again. That is now the separation test.

## Contract, for your reference

    payload  rule_hex, radius, n_cells, steps, n_ic, ic_density_set,
             success_criterion            (at_T | stable, no default)
    result   accuracy, misclassified_ic[] (bounded 64), spacetime_digest,
             success_criterion, accuracy_at_T, accuracy_stable,
             n_incorrect_at_T, n_incorrect_stable, mask_digest_at_T,
             mask_digest_stable, all_zeros_fixed, all_ones_fixed,
             criteria_agree, n_ic_total, n_cells, steps, witness_truncated

Two conventions I had to fix and am flagging in case you would choose
otherwise — I could not find packet v2.1 §2.1 anywhere in the repo, so these
came from the v2 field list plus the operator's corrections:

* **`ic_density_set` is ordered; `null` means your unbiased ensemble**
  (`make_ics(density=None)`), and `n_ic` is ICs PER density with blocks
  concatenated in declared order, so witness indices are global. A single
  `[null]` reproduces you called directly, which is why the golden matches.
* **Block j is seeded `seed + j`**, so block 0 uses the run's seed unchanged.

`stateful=False`: the lattice lives inside one execution, so `repeat.state=
persist` is refused for this kind.

One safety belt worth mentioning: the wrapper recomputes the at_T mask to
derive `stable`, and compares its digest with the one `classify` returns. If
they ever disagree it raises rather than reporting a number — a wrapper that
has drifted from its library must not publish.

No reply needed except on landing `evca` on main, and on the two conventions
above if either is wrong.
