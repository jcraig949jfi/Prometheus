# D-18 amendment v1: a declared non-uniform reset

    amendment   D-18
    version     v1
    status      PROPOSED. NOT APPLIED to ca_stream_v1.
    author      Herakles, 2026-09-10
    code path   herakles/ca_stream/reset_v2.py  (imported by nothing in core)
    evidence    herakles/ca_stream/d18_development.json
                herakles/ca_stream/d18_horizon_evidence.json

Applying this creates **`ca_stream_v2`, a new kind**, because changing the
reset changes what every number under the old reset meant. The alpha keeps its
all-zero reset and its obstruction result exactly as recorded.

---

## 1. What changes, and what does not

    ca_stream_v1   reset to all zeros
    D-18 v1        reset to a seeded Bernoulli lattice at a declared density

Unchanged: inject at declared ports, exactly one CA step, read the post-step
lattice; the capacity-limited linear readout over the current lattice; the
matched direct-input and frozen-random baselines at equal readout width; the
disjoint train / dev / confirmation partitions.

## 2. Seed coupling, and the check that makes it evidence

The reset randomness must carry no information about any target. The reset
seed is derived from the stream's POSITION in the catalogue, never from its
content:

    reset_seed(i) = sha256("ca_stream.d18.v1|<reset_root>|<i>")[:8]

Position is not the target: adjacent positions have unrelated targets.

That argument is not trusted. `reset_leakage_probe` fits the declared readout
on the reset lattices with **no input injected at all** and asks whether it can
predict the target anyway. Measured on the development partitions,
`delayed_recall` at delay 2, density 0.5:

    rule    accuracy   base rate   leaks
    GKL       0.5234      0.5234   False
    par       0.5052      0.5234   False

GKL lands exactly on the base rate and par below it. No leakage.

## 3. Relaxation time, undriven

How long a live lattice survives with NO input. Density 0.5, 200 samples,
censored at 200 steps.

    rule        median   min   max   reached uniform   censored
    maj              2     1     4                23        177
    exp              6     2    19               200          0
    par             14     2    37               200          0
    particle1       12     3    35               194          6
    particle2       13     2    39               195          5
    GKL             13     2    52               200          0

**`maj` is the odd one and it matters.** It reaches a uniform lattice in only
23 of 200 samples; the other 177 are censored. It is not relaxing to uniform
at all, it is settling into a frozen non-uniform pattern. A naive relaxation
statistic would have reported "median 2, very fast" and hidden that.

## 4. Driven response, and why it is a separate measurement

Two runs from the **identical** reset lattice, differing only in the injected
stream. If the trajectories never differ, the substrate is not listening and
its activity is transient, not computation.

Mean Hamming divergence by step, first ten steps, 200 samples:

    maj        2.04 2.11 2.04 1.97 1.84 1.80 1.70 1.70 1.67 1.67   DECAYS
    exp        2.71 3.86 3.97 3.42 2.89 2.20 1.90 1.65 1.70 1.63   PEAKS, DECAYS
    par        2.62 3.88 4.47 4.80 4.96 5.08 5.16 5.33 5.36 5.55   GROWS
    particle1  2.56 4.12 4.86 5.47 5.87 6.16 6.45 6.72 6.96 7.13   GROWS
    particle2  2.37 4.07 5.13 6.05 6.83 7.29 7.76 8.05 8.16 8.37   GROWS
    GKL        1.55 2.38 2.90 3.38 3.73 4.11 4.42 4.87 5.18 5.30   GROWS

**This is the transient / computation distinction the amendment exists to
draw.** `maj` and `exp` are busy and then forget: their response to input
peaks early and decays. The other four carry the input forward.

## 5. The mean was checked against the distribution

A rising mean could be a few runs landing in opposite uniform states, which
would be one dramatic effect rather than a general one. It is not. Divergence
at the final step, 400 samples, horizon 16:

    rule        zero   1..5   6..30   =31 (opposite)   mean
    maj          149    210      41                0   1.66
    exp          325     55      20                0   1.40
    par          173     71     155                1   5.34
    particle1    206     38     147                9   6.96
    particle2    149     47     198                6   8.29
    GKL          167     72     159                2   5.28

At most 9 of 400 reach opposite attractors. The effect is broad, not driven by
a handful of dramatic cases.

## 6. The horizon, chosen from the evidence rather than inherited

Fraction of resets where the input is **entirely forgotten** by the horizon,
and fraction retaining a divergence of at least 3 cells, 400 samples:

    rule         h=8 forgotten  h=8 div>=3   h=16 forgotten  h=16 div>=3
    maj                   0.39        0.23             0.37         0.21
    exp                   0.64        0.22             0.81         0.16
    par                   0.23        0.64             0.43         0.50
    particle1             0.22        0.61             0.52         0.44
    particle2             0.09        0.82             0.37         0.57
    GKL                   0.24        0.55             0.42         0.51

**Recommendation: keep the horizon at 8.** It was inherited from the brief;
it is now supported. At 16, between 37 and 52 per cent of resets have lost the
input entirely for the four responsive rules, and `exp` has lost it in 81 per
cent. At 8, `particle2` retains the input in 91 per cent of resets and the
other three responsive rules in about 77 per cent.

**Recommendation: reset density 0.5**, tested here and not leaking.

**A caution I would not want skipped.** `maj` and `exp` should be expected to
score at baseline under this amendment too, for a reason that is now measured
rather than assumed: they forget the input. If they were to score above
baseline, that would indicate leakage rather than computation, and the leakage
probe should be run again before the number is believed.

## 7. What is still forbidden until the operator decides

- The amendment is **not applied**. `core.py` imports nothing from
  `reset_v2.py` and the alpha run is unchanged.
- **No rule search.** That is beta and it comes after the re-run, not before.
- **Confirmation is untouched.** Every measurement above used only the reset
  lattices themselves or the development partitions. `relaxation_time` and
  `driven_response` take no stream partition at all, and the leakage probe was
  given the training and development indices only. There is no argument in any
  of these functions through which the confirmation partition could arrive.

## 8. Reproduction

    python -c "from herakles.ca_stream import reset_v2 as r; \
               print(r.relaxation_time(<rule_hex>, 31, 0.5, 20260910, 200, 200))"
    python -c "from herakles.ca_stream import reset_v2 as r; \
               print(r.driven_response(<rule_hex>, 31, (0,), 0.5, 20260910, 200, 16))"

Both write nothing and touch no global RNG. The two evidence files in the
header carry the full outputs.
