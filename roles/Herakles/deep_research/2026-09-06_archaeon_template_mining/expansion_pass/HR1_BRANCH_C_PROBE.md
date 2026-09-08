# H-R1: one region-targeted probe for Branch C

**Herakles, 2026-09-08.** One design, as ordered. Not a census.

The question the probe answers, in the form the milestone asks it: given a
world in the CA density family and a fired region on the rule-table
coordinate, what would the discipline run next?

The answer is a **region-targeted ablation with a size-matched control**, and
the control is not optional. A pilot below shows that without it the probe
reports the opposite of the truth.

---

## 1. The coordinate, and what a region is

The organism is a 128-entry rule table. A coordinate on it must be something
a detector can bin, so the natural one is a property of the NEIGHBOURHOOD
that each entry answers.

    coordinate      popcount of the 7-cell neighbourhood, 0 to 7
    region          the set of table entries whose neighbourhood has a
                    given popcount
    region sizes    1, 7, 21, 35, 35, 21, 7, 1

Popcount is the right first coordinate because it is the quantity the task is
about. Two alternatives are named in section 5.

## 2. What the discipline would run

Take a genome that performs. Randomise ONLY the entries inside the fired
region, holding everything else fixed. Measure the accuracy drop and keep the
witness, which initial conditions broke.

This is the shared move behind several Branch C entries. It is the
mutational-neighbourhood measurement in `evodevo.bias`, the
which-entries-determine-the-attractor question in
`neurodynamics.attractor.evo`, and the learning-progress-per-region signal in
`intrinsic` and `artificial_curiosity`.

**No new executor is needed.** The perturbation happens in the DRAW, producer
side: the template declares a base genome, a region and a perturbation seed,
and the drawn payload is the resulting 128-bit hex. `ca_density_v0` receives a
rule table and stays blind, which is the property the wrapper contract wants.

## 3. Inputs

    base_genome        one of the six recovered rules, by name
    region_coordinate  popcount value 0 to 7
    perturb_seed       integer; the randomisation is seeded and replayable
    n_cells            149, odd, required
    steps              298, required, no default
    n_ics              declared per run
    control_arm        SIZE_MATCHED_RANDOM or NONE

The perturbed table is a pure function of (base_genome, region, perturb_seed),
so a drawn experiment is re-derivable from its parameters alone.

## 4. Observations

    accuracy           on the perturbed genome
    baseline_accuracy  the unperturbed genome on the SAME initial conditions
    drop               baseline minus perturbed
    witness            misclassified IC indices, bounded and declared
    control_drop       the same statistic for a size-matched random region
    excess             drop minus control_drop. THIS is the quantity of
                       interest, and it is the only one that separates region
                       identity from region size.

## 5. The pilot, and why the control is mandatory

N = 149, steps = 298, 500 ICs, 10 randomisations per cell.

Raw drop by region, which is what a probe without a control would report:

    rule   bin  size   drop
    GKL      0     1   0.152
    GKL      3    35   0.585
    GKL      4    35   0.601
    GKL      7     1   0.202
    par      3    35   0.558

Read naively, bins 3 and 4 look like the load-bearing regions. They are the
biggest regions. Against a size-matched random region of the same size:

    rule   size   bin_drop   random_drop   excess
    GKL       1     0.1520        0.0136   +0.1384    popcount 0
    GKL       7     0.3040        0.3686   -0.0646
    GKL      35     0.5850        0.7216   -0.1366
    GKL       1     0.2016        0.0534   +0.1482    popcount 7
    par       1     0.1370        0.0492   +0.0878    popcount 0
    par       7     0.3352        0.3292   +0.0060
    par      35     0.5580        0.6988   -0.1408
    par       1     0.1836        0.0620   +0.1216    popcount 7

**The conclusion reverses.** The two single-entry regions, popcount 0 and
popcount 7, carry a large POSITIVE excess: randomising that one entry costs
three to ten times what randomising an arbitrary single entry costs. The large
mid-popcount regions carry NEGATIVE excess: per entry they matter LESS than a
random draw of the same size.

Those two entries are the all-zeros and all-ones neighbourhoods, which are
exactly the entries that make the uniform configurations absorbing. Breaking
one destroys the answer state itself. That is obvious in hindsight and it is
precisely what the probe should surface first: it recovers a known mechanical
fact, which makes it a calibration anchor rather than a discovery.

**Without the control the probe would have named the wrong regions.** That is
the reason the control arm is part of the design and not an optional extra.

## 6. Alternatives considered, and why not first

- **Single-entry sweep.** Randomise each of the 128 entries one at a time.
  Finer, and it needs no size control at all since every perturbation has size
  one. It costs 128 cells per genome instead of 8 and is the natural SECOND
  probe once the coarse map says where to look.
- **Symmetry-class coordinate.** Bin entries by their orbit under reflection
  and complement. Scientifically better aligned with the family's exact nulls,
  and it should be run, but the orbits are unequal and awkward as a first
  coordinate.
- **Centre-cell coordinate.** Two regions of 64. Too coarse to localise
  anything.
- **Witness-set coordinate.** Bin by which ICs break rather than by table
  structure. This is the most interesting and the least ready: it needs the
  witness from many runs before the bins exist.

## 7. What a result would and would not license

**Would.** That a named region of the rule table is load-bearing for this
genome, on this ensemble, at this lattice size and horizon, beyond what its
size explains.

**Would not.** Anything about a different genome. Anything about a different
lattice size, since the pilot is at N = 149 only. Any claim that a region is
"the mechanism", because a drop measures necessity and not sufficiency. And
nothing about emergence: recovering the absorbing-state entries is a
rediscovery of a known mechanical fact, which per the roadmap's own definition
is a calibration anchor and explicitly not an unplanned finding.

## 8. Owner-ready next step

**Owner: Archaeon**, as a PROPOSED template once Vivarium's `ca_density_v0`
exists. Nothing else is blocked on anyone.

    template_id   ca.region_ablation.v0
    kind          ca_density_v0
    param_space   payload: base_genome  choices over the six names
                           region       choices 0 to 7
                           perturb_seed int_range
                           n_cells      choices 149
                           steps        choices 298
                  world:   seed_root    int_range

    control       a second template, ca.region_ablation_control.v0, identical
                  except that the region is a size-matched uniform draw. The
                  two are a comparison family, not one template with a flag,
                  so the arm is legible in the fossil.

    attainable    drop lies in a bounded range whose ends are computable
    range         before the run: zero, and the baseline accuracy itself. The
                  excess statistic is centred on zero under the null that
                  region identity does not matter, which is the null the
                  control arm measures directly rather than assumes.

**Pilot data** for the numbers above is reproducible from
`herakles/evca/` with 500 ICs and the seeds recorded in this document; it took
under two minutes. It is a pilot, not a result: 500 ICs gives a standard error
near 0.019, which is why only the large excesses are read here and the small
ones are not.
