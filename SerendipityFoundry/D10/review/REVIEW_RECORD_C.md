# Reviewer C — statistics, units, power, multiplicity, cost (findings + adjudication)

Companion to `REVIEW_RECORD.md` (A) and `REVIEW_RECORD_B.md` (B).

---

## C-0 — the headroom figure quoted in the brief came from planted reference programs, not from a corpus
`SEVERITY: FATAL` · **CONFIRMED, and independently superseded**

The brief quoted "matched-foreign ~0.09, oracle same-family ~0.57" from `p5b`,
which injects the *actual same-family reference programs and the family root* —
artifacts no history phase produces. The only end-to-end number at review time
was `p7`: oracle 0.130, uniform 0.019, and `history_solves: 0`.

**Adjudication: accepted.** The reviewer is right that the p5b figures are not
headroom. Two later probes, run after the brief was issued, supersede both:

| probe | history | N | U | PP1 (oracle) |
|---|---|---|---|---|
| `p9` `N_TRAIN=6`, `B_hist=3200` | 48 trials, **1** test-solve | 0.000 | 0.000 | 0.042 |
| `p9` `N_TRAIN=10`, `B_hist=3200` | 48 trials, **3** test-solves | 0.010 | 0.010 | 0.188 |
| `p10` `N_TRAIN=10`, `B_hist=12800`, 96 trials | **11** test-solves, 25 solver genotypes, corpus 3,962 | **0.021** | **0.031** | **0.344** |

So the operating point the reviewer correctly condemned has been replaced. At
the provisioned operating point the realisable ceiling is **0.344 against 0.031
unorganized memory — a 0.313 absolute, ~11x relative dynamic range**, and the
corpus contains real material. `C-0`, `C-8` and gate `G2` are resolved by
measurement, not by argument.

## C-1 — the experimental unit is the lineage; naive pooling gives 29–49 % Type-I error
`SEVERITY: FATAL` · ACCEPTED-UNVERIFIED (simulation), **CONFIRMED (structural)**

Every trial inside a lineage-arm cell is driven by *one* draw of an organizer,
so `L` is the sample size, not `L x T x S`. Reviewer-simulated Type-I of the
naive pooled two-proportion test under a true null: 0.128 at σ_org=0 (family
clustering alone), rising to 0.488 at σ_org=0.04.

**Adjudication: accepted; the reviewer's plan supersedes mine.** My draft
already made the lineage the unit and used a Wilcoxon over per-lineage paired
differences, which is not wrong, but the reviewer's procedure is strictly
better and is adopted verbatim: exact one-sided **sign-flip permutation test**
over `{d_l}` (exhaustive to L≈22), **two-way cluster bootstrap** over lineages
*and* eval families for the CI, GLMM as sensitivity only with non-convergence
pre-declared as "not a result", and the invalid pooled analysis reported and
labelled invalid so no reader mistakes it for evidence.

## C-2 — the correlated hierarchy is task ⊂ family, and F is far too small
`SEVERITY: SERIOUS` · **CONFIRMED.** With `n_mut=1`, family members are
near-duplicate programs, so effective df is `min(L, F) − 1`; `F=6` caps it at 5
regardless of L. **Adjudication: accepted** — `F_eval >= 24` distinct eval
families, at most 2 members each; `F`, not `T`, is reported as the task-side
sample size. Task generation is cheap enough that this is free.

## C-3 — the design already has common-random-numbers pairing; use it, and the Court throws it away
`SEVERITY: MINOR (opportunity) / SERIOUS (Court)` · **CONFIRMED**

`acquire` evaluates the injected `k` first and then fills from `create_s`, so
for a fixed trial seed the fresh members are byte-identical across organized
arms — free variance reduction. But `foundry/court/predicates.py`
`_two_arm_effect` draws `arm_a` and `arm_b` from **different** seed streams,
discarding the pairing exactly where it matters. **Adjudication: accepted** —
analyse paired trial differences, report the realised `ρ_CRN`, and do not route
the primary contrast through the Court's two-arm machinery.

## C-4 / C-5 — L ≥ 8 is a hard floor, and required L is governed by σ_org, which is unmeasured
`SEVERITY: SERIOUS (C-4) / FATAL (C-5)` · **CONFIRMED (arithmetic)**

The exact sign-flip test has minimum one-sided `p = 2^-L`, so L=5 can never
reach p<0.031. And the reviewer's power table shows the structural result:
**once σ_org ≥ Δ, required L is 8–15 and is essentially independent of effect
size, T, S and F; once σ_org ≥ 2Δ, required L is 27–33 and adding tasks and
seeds buys nothing.** The between-lineage variance of organizer quality is the
whole ballgame, and the draft proposed to spend its compute on the one axis
that does not help.

**Adjudication: accepted in full, and this is now the top-priority missing
measurement.** `L` cannot be preregistered until σ_org is measured from ≥ 4
pilot lineages run through the complete history → organizer-GA → eval pipeline.
Recommended design point pending that number: `L=16`, `F=24`, `T=48`, `S=5`.

## C-6 — the ceiling was measured with history and eval tasks from the same families
`SEVERITY: FATAL as stated` · **CONFIRMED, partially misdirected**

Correct about the probes. But same-family eval is the *deliberate* primary
condition (shared structure is what the organization is meant to find);
`p10`'s 0.344 is therefore the primary-condition ceiling and is valid for it.
**Adjudication: partially accepted** — the finding is fully correct about the
**transfer** endpoint, whose ceiling is entirely unmeasured. A family-disjoint
oracle-ceiling probe is added as a pre-freeze gate; if the transfer headroom is
below threshold, the transfer endpoint is dropped rather than run underpowered.

## C-7 — rare-event information starvation
`SEVERITY: SERIOUS` · **CONFIRMED.** Effective information scales with the
number of *successes*, not trials. **Adjudication: accepted** — pre-register
≥ 8 expected successes per lineage-arm cell in the weakest organized arm. At
the new operating point (`p_U ≈ 0.031`) that is ~260 trials/cell, which the
recommended `T=48 x S=5` grid meets.

## C-8 — floor effects break N-vs-U and variance estimation
`SEVERITY: SERIOUS` · **CONFIRMED, largely resolved.** At the old operating
point N=U=0.000 and Fisher p=1.0. At the provisioned point N=0.021, U=0.031 —
still a weak contrast but no longer degenerate. **Adjudication: accepted** —
Clopper-Pearson/Wilson intervals only (Wald forbidden), Firth penalisation
pre-declared for any separated cell, and `U − N` placed **last** in the
fixed-sequence family precisely because it is expected to fail.

## C-9 — the obvious continuous secondary endpoints do not work here
`SEVERITY: SERIOUS` · **CONFIRMED, and it corrects my draft.**
My draft named "evaluations-to-first-test-exact-solve, censored" as the
secondary. The reviewer shows it is **not measurable**: `acquire` halts on the
first *train*-exact success, so there is no time-to-test-solve. Train-based
endpoints carry zero extra information at the chosen operating point (`p5b`
`L12/m1`: train and test rates identical in every condition) and
`best_train_fitness` is the search's own signal.

**Adjudication: accepted; the reviewer's endpoint is adopted** — *number of the
20 held-out test cases passed by the final best-by-train individual* (ordinal,
0–20). Not the search signal, never visible to the search, and it converts a
Bernoulli(0.03) into a count with real dispersion. Pre-declared caveats: it is
not the claim; it correlates with train fitness so the train/test gap is
co-reported; and chance pass rate is reported.

## C-11 — no multiplicity design; the contrast count is far larger than six
`SEVERITY: SERIOUS` · **CONFIRMED, including the part about me.** The reviewer
counts 15 pairwise contrasts, 2 counterfactuals, transfer, L per-lineage
results, 2 endpoints — **plus the 72 preflight cells already swept**, which is
a partly-walked garden of forking paths.

**Adjudication: accepted; the reviewer's scheme supersedes my Holm plan.**
Single primary `E − R`, one-sided, α=0.05, uncorrected. **Fixed-sequence
gatekeeping** secondary family in the pre-declared order E−R, E−H-fit, R−U,
H-fixed−U, H-fit−H-fixed, U−N, stopping at first non-rejection (costs zero α).
Counterfactuals become **gates with pre-declared thresholds**, not tests —
failing a gate invalidates the primary claim regardless of its p-value.
Per-lineage results are descriptive only. Everything else is BH-FDR q=0.10 and
labelled exploratory. **The operating-point cell is frozen now, before any eval
task is generated.**

## C-12 — `R` may collapse to evidence-insensitivity, so `E − R` may not isolate what it claims
`SEVERITY: SERIOUS` · **CONFIRMED (mechanism).** A GA fit under a deranged
objective selects for a `KQ` that ignores evidence, since a constant `KQ`
maximises a scrambled objective. Then `E − R` conflates task-conditional
relevance with *any* evidence-sensitivity.

**Adjudication: accepted, and the reviewer's `R2` is adopted as the primary
null.** `R2` = E's own winning organizer, but at retrieval time the query key
is computed from a randomly chosen *other* eval task's evidence.
Within-organizer, perfectly compute-matched, zero extra construction cost, and
it isolates task-conditionality with nothing else varying. `R` is retained as
the compute-matched secondary null, with R's realised `KQ` sensitivity (number
of distinct query keys over the eval pool) measured and reported.

## C-13 — winner's curse ≈ 4x the plausible true effect
`SEVERITY: FATAL if fitting fitness is ever reported as an effect` · **CONFIRMED
(arithmetic).** 684 GA candidates, fitness estimated from ~24 Bernoulli draws
→ the winner's fitting-set fitness overstates its true value by ≈0.20. It does
not bias `E − R` because the endpoint is measured on held-out eval tasks — but
only if selection intensity is matched in *effective*, not FLOP, terms, and if
no eval information touches selection.

**Adjudication: accepted.** Report per lineage-arm the winner's fitting
fitness, its eval rate, and the **shrinkage** between them (a large positive
shrinkage in E and near-zero in R is the expected signature and is a planned
diagnostic). Enforce structurally: the winner's content address is written to a
sealed, hashed file **before the eval-phase process starts**, and the eval
runner refuses to run against an unsealed winner. All completing lineages are
analysed; exclusion only for a mechanical pre-declared reason adjudicated from
logs containing zero eval outcomes.

## C-14 — the Foundry Court's default margins make the gates simultaneously unreachable and unfailable
`SEVERITY: FATAL` · **CONFIRMED-BY-REPRODUCTION**

```
DEFAULT_MARGINS = {'exact_effect': 0.25, 'ablation': 0.25, 'control': 0.1,
                   'transfer': 0.25, 'null': 0.1, 'cost': 0.0}
measured max attainable delta (p10) = 0.344 - 0.031 = 0.313
  exact_effect 0.25 / transfer 0.25 : passable only by a near-oracle organizer
  control 0.10  : passes iff |delta| <= 0.10 -> cannot fail at realistic deltas
  cost 0.0      : COST passes on any positive delta at ANY cost
  selection_penalty default 0.0 -> the multiple-comparison mechanism is INERT
  CourtHarness.n_trials default = 8
```

This is precisely the charter's "impossible positive controls" plus a set of
vacuous negative controls. **Adjudication: accepted in full.** All margins are
re-derived from the measured operating range and sealed before the eval phase;
`selection_penalty > 0` with `n_candidates_considered` set to the mechanically
metered total organizer-genome count across all lineages and arms, committed
into the hashed case manifest; and the margin comparison uses the **lower**
confidence bound of delta for `effect_present=True` and the **upper** bound for
`effect_present=False`, since every predicate currently thresholds a point
estimate with no uncertainty quantification at all.

## C-17 — there is no compute-matched cold-search arm, and it may dominate everything
`SEVERITY: FATAL for the utility claim` · **CONFIRMED (structural)**

The referee's first question is: what if the organizer-construction compute
were simply spent searching longer? At the draft's parameters `C_org` amortises
to ~33k evaluations per query against `B=600` — **55x the query budget** — and
crossover needs ~164,000 downstream queries per lineage.

**Adjudication: accepted in full. This is the single best addition any reviewer
made.** Arm **`N+`** (cold start at `B' = B + C_org/(T·S)`) is added, and the
missing preflight — cold-start solve rate at `B ∈ {600, 2000, 6000, 20000,
60000}` — is added as a **pre-freeze requirement** (~30 min of compute). My own
budget curve already covers part of it (`p8`, L=8: 0.000 / 0.042 / 0.167 /
0.208 at B = 200 / 800 / 3200 / 12800), and notably it **plateaus** above
B≈3200, which is evidence against the reviewer's exponential extrapolation —
but the curve must be extended to `B'` before any cost claim is made.

## C-18 — what a total-cost loss does and does not invalidate
**Adjudication: accepted verbatim into the preregistration.** A cost loss does
not invalidate the mechanism claim (settled by the equal-marginal-budget `E−R`
contrast); it does invalidate every engineering, efficiency and
"pays-for-itself" claim. **And if `N+ >= E`, the organization is dominated by
simply searching longer: the mechanism claim survives, the utility claim fails
even though the primary contrast is positive.** That outcome and its wording
are pre-declared. Also confirmed: `predicates.py` `run_cost` with
`DEFAULT_MARGINS['cost'] = 0.0` passes on any positive delta at any cost.

## C-V3 — budget equality is structurally impossible for an arm that works
`SEVERITY: FATAL` · **CONFIRMED-BY-REPRODUCTION**

```
_two_arm_effect: passed = bool(beq and delta > eff)          -> True
_budget_equal:   tolerance defaults to 0                     -> True
acquire():       halts on first train-exact success          -> True
```

A more effective arm consumes *fewer* evaluations, so realised counts differ,
so `beq` is False, so **a real effect fails the gate precisely because it is
real**. **Adjudication: accepted.** Parity is redefined as **cap-parity** —
identical `B` in every arm and `realised <= B` — with realised counts reported
descriptively and never used as an equality gate.

## C-V5 — the organization itself is not reproducible
`SEVERITY: FATAL` · **CONFIRMED-BY-REPRODUCTION** (`run_key` passes
`timeout_s=5.0`)

A key program running near the wall-clock backstop produces a *different key*
on a loaded machine than on an idle one, so the primary object of study is
machine-load-dependent. It also makes total wall clock unbounded: at ~1.6e8 key
computations per lineage-arm, 0.1 % hitting a 5 s wall is 9 days.

**Adjudication: accepted.** The key meter becomes purely step-based; `timeout_s`
is set so it can never bind before `KEY_MAX_STEPS`; a timeout is recorded as a
hard error and voids the trial.

## C-19 — the experiment is affordable; corpus keying is the unaccounted cost
`SEVERITY: SERIOUS (accounting)` · ACCEPTED-UNVERIFIED

~10–14 h wall clock on 16 cores at `L=16`, gen 15–30, with a capped corpus.
The unaccounted cost is corpus keying: `n_candidates x |corpus| x KEY_MAX_STEPS`
VM steps, which roughly **doubles** wall clock at a 240k corpus. **Adjudication:
accepted** — a fixed corpus subsample size is pre-declared and metered
(the `p10` corpus rule already yields 3,962, well inside the safe range), and
the pre-declared cut order if compute is tight is **S, then GEN, then T —
never L**.
