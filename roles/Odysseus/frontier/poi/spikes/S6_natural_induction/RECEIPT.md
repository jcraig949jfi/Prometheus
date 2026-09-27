# Spike S6 -- natural induction (Watson, Buckley, Mills 2011) in a stdlib toy

Currency: 2026-09-27. Odysseus spike worker (disposable). Feasibility test for
NEWLENS.md L2 "the learning rule nobody installed" / raw/E5 PART 3 L7.
Web: NOT used. The protocol was reconstructed from memory of the paper and is
stated in PREREG.md; deviations from the paper are listed under LIMITS.

## 0. Verdict (one paragraph)

The effect REPRODUCES in the toy, but the preregistered headline family (F_MOD,
the paper's modular setting) came out NOT REPRODUCED under the preregistered
rules, because the pilot picked a yield rate that turned out too fast for the
main instances. F_SK REPRODUCED under the preregistered rules, passing every
control on 5/5 seeds. A POST-HOC run, labelled as such (posthoc.py, fresh seeds
6-10, F_MOD at delta=3e-4, a rate taken from the main grid), passed D1-D3 on
5/5 seeds for both families. The ingredient that matters most is timescale
separation. Yield that is too fast (or too long without reset) memorises
whichever attractor comes early and does no better than plain relaxation.
Caveat: in these small instances, natural induction (NI) does NOT beat
best-of-1000 plain random restarts (that baseline found the target minimum on
every instance). What NI adds is that it turns the system into one that falls
into a good minimum from most starts. It does not find minima that restart
search cannot.

## 1. Protocol (frozen in PREREG.md before any run; file not edited since)

- Units s_i in {-1,+1}. W0 = original couplings. Dynamics run on W0+WL. WL
  starts at 0.
- F_SK: N=50, W0 = +/-1 symmetric.
- F_MOD: N=60 = 12 modules x 5. Intra-module weight +1. Inter-module weight
  0.05*c_AB, with c_AB = +/-1 per module pair. The exact ground state comes
  from enumerating all 2^12 module configurations.
- One reset:
  - start from a random state;
  - run up to T=10 asynchronous zero-temperature sweeps;
  - after every sweep, the couplings yield: WL_ij += delta*s_i*s_j. A
    converged state is "idled" for the remaining sweeps, so most of the yield
    happens at attractors.
- R=1000 resets, with checkpoints at 100, 300 and 1000.
- Evaluation (paired, the same 100 random starts in every condition):
  1. freeze WL;
  2. relax on W0+WL;
  3. then POLISH: relax on W0 alone, so every scored state is a true local
     minimum of the original problem.
- M = mean E0 over the 100 polished states (lower is better). Also recorded:
  E0 before polishing, and the fraction of starts that reach the target (exact
  ground state for F_MOD; best-known E0 for F_SK).
- Seeds: pilot 999; main 1-5; post-hoc 6-10. All RNG streams are seeded by
  string, so results are deterministic.
- Controls (at the primary delta):
  - noyield: delta = 0.
  - anti: the yield sign is reversed.
  - shuf_oth: WL is driven by the state sequence visited by the NI run on a
    DIFFERENT instance.
  - perm: own states, but unit labels are permuted by a fresh permutation
    each reset.
- Ablations:
  - fast: delta = 0.1 (removes timescale separation).
  - noreset: one start, then R*T sweeps with no reset.
  - nodiss: no relaxation; the yield sees fresh random states.
- Decision rules:
  - D1: NI beats noyield on at least 4/5 seeds, and the median gain is at
    least 0.5 SD of the noyield distribution.
  - D2: NI beats anti on at least 4/5 seeds.
  - D3: NI beats both shuffle controls on at least 4/5 seeds.

## 2. Results -- PREREGISTERED main run (seeds 1-5, R=1000)

Pilot choice of delta (seed 999): F_MOD 1e-3, F_SK 1e-4 (pilot.json).

M values are the mean over seeds, with the seed range in brackets. frac is the
mean fraction of starts that reach the target.

F_SK, delta=1e-4: REPRODUCED (D1, D2 and D3 all pass)

| Condition | M | frac |
|---|---|---|
| noyield | -220.9 [-228.1..-212.3] | 0.05 |
| NI | -246.4 [-253.0..-240.1] | 0.71 |
| anti | -212.1 [-215.9..-208.0] | 0.03 |
| perm | -220.9 (same as noyield) | 0.05 |
| shuf_oth | -221.0 [-230.5..-210.9] | 0.04 |

- Wins: NI beats every control on 5/5 seeds.
- Effect in noyield-SD units: 1.89, 2.04, 1.43, 1.19, 1.88.
- The attractor E0 during learning falls steadily. Seed 1, per 100 resets:
  -221, -223, -225, -232, -238, -242, -244, -246, -245, -247.

F_MOD, delta=1e-3: NOT REPRODUCED (D1 fails; D2 and D3 pass)

| Condition | M | frac |
|---|---|---|
| noyield | -132.8 [-135.1..-131.4] | 0.01 |
| NI | -135.5 [-145.0..-125.0] | 0.00 |
| anti | -131.5 | - |
| perm | -117.5 | - |
| shuf_oth | -118.5 | - |

- NI beats noyield on only 3/5 seeds.
- Effect in noyield-SD units: -0.79, 0.45, -0.01, 0.66, 1.38 (median 0.45,
  below the 0.5 threshold).
- Mechanism of the failure: by about reset 200 the learned W has collapsed
  onto a single early attractor, which is often mediocre. The trajectory
  flatlines, for example at -125 on seed 1 (ground state -150).
- Under the preregistered rules the ablation labels are not interpretable for
  F_MOD in this run. results.json still prints them, but they are void.

Sensitivity grid (main seeds 1-5). Each cell gives the median effect in
noyield-SD units, then how many seeds out of 5 had at least 50% of starts
reaching the target.

F_MOD:

| delta | R=100 | R=300 | R=1000 |
|---|---|---|---|
| 1e-4 | 0.01, 0/5 | 0.18, 0/5 | 1.51, 1/5 |
| 3e-4 | 0.22, 0/5 | 1.45, 2/5 | 2.18, 3/5 (100% ground on 3 seeds) |
| 1e-3 | 0.47, 0/5 | 0.45, 0/5 | 0.45, 0/5 (frozen) |
| 3e-3 | 0.11, 0/5 | 0.11, 0/5 | 0.11, 0/5 (frozen) |

F_SK:

| delta | R=100 | R=300 | R=1000 |
|---|---|---|---|
| 1e-4 | 0.00, 0/5 | 0.93, 1/5 | 1.88, 4/5 |
| 3e-4 | 0.65, 1/5 | 1.50, 3/5 | 1.50, 3/5 |
| 1e-3 | 1.54, 3/5 | 1.54, 3/5 | 1.54, 3/5 (frozen by R=100) |
| 3e-3 | 1.23, 1/5 | 1.23, 1/5 | 1.23, 1/5 |

Reading: the gain depends on the product delta*T*R, which is roughly the
accumulated learned weight, and on how slowly that weight builds up. It works
best when WL reaches the |W0| scale only after many hundreds of resets. When
delta is faster, WL "commits" to an attractor that was found early. Slower
settings were still improving at R=1000. The window is narrow: in F_MOD only
1e-4 and 3e-4 worked.

## 3. POST-HOC confirmation (NOT preregistered; fresh seeds 6-10)

Rates fixed from the main grid: F_MOD delta=3e-4, F_SK delta=1e-4. The code
path and analysis are the same as the main run (posthoc.py, posthoc.json).

F_MOD, delta=3e-4: passes D1, D2 and D3 on 5/5 seeds

| Condition | M | frac |
|---|---|---|
| noyield | -133.0 | 0.02 |
| NI | -148.4 [-152.5..-145.0] | 0.32 |
| anti | -132.6 | - |
| perm | -120.5 | - |
| shuf_oth | -119.7 | - |

Effect in noyield-SD units: 1.17, 2.45, 1.69, 1.53, 1.46.

F_SK, delta=1e-4: passes D1, D2 and D3 on 5/5 seeds

| Condition | M | frac |
|---|---|---|
| noyield | -225.7 | 0.06 |
| NI | -246.4 | 0.30 |
| anti | -215.7 | - |
| perm | -225.7 | - |
| shuf_oth | -222.9 | - |

Effect in noyield-SD units: 1.16, 1.58, 1.36, 1.08, 1.52.

## 4. Controls -- what each one shows

- noyield: this is the baseline. It lands in random-restart minima and reaches
  the target from 1-9% of starts.
- anti (reversed sign): consistently worse than noyield, by about 8-10 E0 in
  F_SK. Reversing the sign flips the direction of the effect, so it is the
  Hebbian sign that does the work.
- shuf_oth (states from another instance's run): no better than noyield.
  - F_MOD: much worse (-119 against -133), because the foreign module
    patterns get burned in. Before polishing, the E0 in F_SK is very high,
    reaching positive values.
  - So the states have to be the system's own visited states.
- perm (own states, labels permuted): with slow delta the permuted yield is
  incoherent across resets. In F_SK it averages out, and M is identical to
  noyield. In F_MOD it is worse (-117 to -120), because the modular structure
  makes permuted states coherent enough to learn wrong cross-module pairings.
  Either way it confers no benefit.

## 5. Ablations -- which ingredient carries the effect

Numbers are G_x/G, the ablated gain divided by the NI gain. The label is valid
for F_SK main, F_SK post-hoc and F_MOD post-hoc.

- Timescale separation removed (fast, delta=0.1). Ratios: F_SK main -0.06,
  F_SK post-hoc -0.14, F_MOD post-hoc -0.40, all at or below 0.25, so it
  CARRIES the effect.
  - The first reset's attractor is burned in immediately. Its average quality
    is that of a random minimum, so the result is at best no better than
    noyield, and often worse.
  - The grid shows the same thing smoothly: delta of 1e-3 and above freezes.
- Repeated reset removed (noreset). Ratios: +0.04, -0.17, -0.40, so it CARRIES
  the effect. Identical to fast in F_MOD (the same single attractor gets
  burned in).
- Dissipation / relaxation removed (nodiss). Ratios: 0.00, 0.00, -0.08, so it
  CARRIES the effect. With the yield driven by unrelaxed random states, WL
  averages to about zero: in F_SK the result is identical to noyield.
- By the preregistered 25% rule, all three ingredients are individually
  necessary. None of them can be dropped.

The most informative of these is the grid. The yield rate has an optimum
window that must be much slower than relaxation and slow compared with
attractor sampling: roughly delta*T*R_commit ~ |W0|, with R_commit in the
hundreds. That is the C1 "separated timescales" condition in E5, and it is
the fragile knob. The pilot-chosen rate already fell outside the window.

## 6. What a Prometheus engine would have to expose to host this

1. A fast state variable with DISSIPATIVE relaxation to local minima of an
   energy or potential. This means zero or low temperature, or an explicit
   descent rule.
2. A slow, mutable coupling layer (WL) that is separate from the frozen
   original constraints (W0). Both must be readable. Scoring has to be done
   against W0 only.
3. A local yield hook: couplings change as a function only of the states at
   their two endpoints (stress = s_i*s_j*w_ij). The rate must be a
   first-class, sweepable parameter, because it is the knob that decides
   success.
4. A perturbation or reset scheduler that is independent of the yield, and a
   way to idle a converged state (cheaply accumulate yield at a fixed point).
5. Evaluation hooks:
   - freeze plasticity;
   - evaluate from a fixed, paired set of starts;
   - polish on W0.
6. Control switches as configuration, not code:
   - yield off;
   - sign flip;
   - foreign-state replay (record and replay a visited-state stream across
     instances);
   - label permutation;
   - no-reset;
   - no-relaxation.
7. A problem generator with a known or cheap target (an exactly enumerable
   modular superspin structure) plus a best-of-K restart baseline at equal
   count. Without that baseline the result is easily overclaimed.

## 7. Limits and deviations

- Protocol from memory. Paper details that may differ:
  - the exact modular weights (inter 0.01 in the paper vs 0.05 here);
  - N=100;
  - yield applied per asynchronous update vs per sweep here;
  - learning-rate values;
  - reset interval.
  Not checked against the paper text.
- Small N (50 and 60), with 5+5 seeds. In F_MOD the effect sizes are lumpy
  because the evaluations often all collapse onto one attractor (M is then
  just that attractor's E0).
- NI does not beat best-of-1000 plain restarts on any instance tested; that
  baseline always hit the target. The toy therefore shows "optimisation
  without an installed objective", but not superiority over restart search.
  Showing the paper's stronger claim (reaching minima that restarts
  essentially never find) needs larger or harder modular instances than this
  budget allowed.
- There is no weight decay and no clipping. Forgetting (C3 in E5) was not
  tested.
- Only zero-temperature relaxation was used. The "dissipation" ablation
  removes relaxation entirely rather than varying temperature.
- The primary delta is fragile. The preregistered pilot mis-chose it for
  F_MOD, and the F_MOD success rests on a post-hoc rate choice, even though
  that choice was confirmed on fresh seeds.
- Incident: posthoc.py's analysis temporarily overwrote results.json. It was
  restored byte-for-byte from a scratch backup taken before the post-hoc run.
  results_raw.json (the main run) was never touched.
- Compute: pilot 23 s, main 321 s, post-hoc 294 s wall, on 4 workers.

## 8. Files (under this directory)

- PREREG.md: the frozen protocol.
- toy.py: the model, pilot and main run, and analysis.
- pilot.json: the pilot's delta choice.
- results.json: per-seed metrics for the main run, the grid, decisions and
  ablations.
- results_raw.json: raw per-start energies for the main run.
- posthoc.py and posthoc.json: the post-hoc confirmation.
- RECEIPT.md: this file.
