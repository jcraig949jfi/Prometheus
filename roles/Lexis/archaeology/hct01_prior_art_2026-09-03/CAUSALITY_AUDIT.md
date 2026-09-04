# CAUSALITY AUDIT — "accessibility causes acquisition", treated as hostile

Directive §6. Every candidate is audited against the same eleven questions. The audit is applied
first to HC-T01 **as executed**, because that is the only member of this family whose full internal
record this programme can inspect.

---

## 1. HC-T01, as executed 2026-09-03

| Question | Answer |
|---|---|
| What is manipulated? | `beta`, the rate of second-type mutations — an operator parameter, not a selection parameter. |
| What changes immediately by definition? | The offspring distribution. **Measured**, and it is small: turning the knob now moves the detector by 0.003–0.027, at or below the 0.021 noise floor. |
| What is evolved? | The operator content of the genome, and genome structure generally (`glen`, `nops`, `ousage` are all recorded per generation). |
| What is merely read out afterward? | The one-step reachable distribution under a frozen common probe. |
| Is accessibility a functional of the same map that determines acquisition? | **Partly.** Both are read off the same evolved genome under the same operator set. Not as tightly coupled as in Kouvaris 2017, where both readouts are functionals of one frozen matrix, because here the acquisition outcome comes from continued evolution rather than from re-reading the same object. |
| Could a common change in architecture explain both readouts? | **YES, and this is the unresolved confound.** `beta = 0` genomes cannot contain second-type operators at all. The contrast is therefore *genome-with-operators* versus *genome-without-operators*, probed with an operator-creating mutation. A difference in the response to that probe is expected on machinery-presence grounds alone. |
| Is detector movement temporally prior, or merely observed earlier? | **Not tested.** X6-T2 is recorded `NOT ATTEMPTED`. |
| Is there a cross-run predictive statistic? | **Yes**, and it is the K7 table: Spearman rho between a predictor at `t` and subsequent best-fitness gain, `n = 30` runs. |
| Is there a mediation analysis? | **No.** |
| Is there a negative/control arm? | Yes, `beta = 0` — but it is the arm that carries the confound. |
| Is the detector independently validated? | **Yes, and this matters for §7.** V2: neutral degree rises 0.504 → 0.657 against Toussaint's historical 0.45 → 0.70, within about 1.1 run-to-run SD of figure-read values. The detector was calibrated against an external historical result *in the substrate where it is used*. |
| Is held-out acquisition outside the detector's construction? | **No.** There is no held-out target. Acquisition is best-fitness gain toward the same single optimum. |

### 1a. What HC-T01 actually established, stated precisely

Two things, and they are real:

1. **A same-probe history effect.** `H(t) = +1.96` at generation 100, 93× the noise floor, Holm-adjusted
   `p = 0.0002`, 30 paired runs per alpha, paired permutation over run pairs. The contemporaneous
   mechanical effect is 0.003–0.027 against a historical effect up to 2.41. **The separation of
   "turning the knob now" from "having had the knob" was achieved.** That is a genuine methodological
   success and it is the part of the residual cell that HC-T01 did deliver.
2. **Matched-capability divergence.** At identical phenotype and identical fitness — 12 of 12 run
   pairs both sitting exactly at the optimum — the two arms have different one-step reachable
   distributions.

### 1b. Why the acquisition leg failed, and why the failure is structural rather than unlucky

K7 asked whether accessibility predicts subsequent acquisition better than a cheap state variable.
Measured (execution packet §10), Spearman rho against subsequent best-fitness gain:

```
predictor                                a=.03 100-500   a=.03 50-200   a=.06 50-200
current best fitness        CHEAP              -1.000          -0.686         -0.987
avgfit          HISTORICAL CONTROL             -0.975          -0.683         -0.954
modular degree  ACCESSIBILITY                  -0.950          -0.624         -0.949
```

**Lexis's reading, which goes beyond what the seat wrote.** The outcome is *gain toward a bounded
optimum*. Gain is therefore bounded above by `(ceiling − fitness(t))`, so `corr(fitness(t), gain)` is
strongly negative **as an arithmetic consequence**, not as a finding. Any predictor correlated with
current fitness inherits a negative correlation with gain, attenuated in proportion to how weakly it
tracks fitness. The cheapest state variable is the sufficient statistic for the ceiling constraint, so
**it must win unless the challenger carries information about gain that is orthogonal to fitness**.

The seat noticed one instance of this and wrote that the 100→500 column is "partly degenerate". The
defect is not confined to that column; it is a property of the outcome variable. **K7 as specified is
therefore close to unwinnable regardless of whether accessibility carries real information**, and its
firing is weaker evidence against the hypothesis than it appears.

That cuts both ways and both must be said:

- It **rescues** the accessibility hypothesis from the strongest-sounding disconfirmation in the record.
- It **convicts** the HC-T01 design, because a kill condition that cannot be passed is not a test.
  This programme has recorded that defect before under the heading of gates that cannot fire.

### 1c. The two re-analyses this implies, both on data already committed

Neither requires new compute. `derived/grid/` holds 120 per-run CSVs (30 seeds × 2 alpha × 2 beta),
each a per-generation series whose columns are declared in `derived/analyze.py`:
`tag gen best mean md_on md_off nd_on nd_off mit_on mit_off mia_on mia_off miu_on miu_off af_on af_off
glen nops ousage al_on al_off minlen geno`.

**RA-1 — re-score K7 as a partial correlation.** Residualise gain on `best(t)`, then test whether
`md_on(t)` explains the residual. Equivalently, Spearman partial correlation of accessibility with
gain controlling for current fitness. This is the marginal-versus-partial distinction, and HC-T01
reported only the marginal. Wagner 2023 does the definitional version of the same correction
(`L_STEALABLE_METHODS` SM-01).

**RA-2 — test the machinery-presence confound directly, within the treated arm.** `nops`, the operator
count, is recorded per run per generation. `beta = 0` runs necessarily have `nops = 0`, which is the
confound. But `beta = 0.1` runs vary in `nops`. Ask whether the accessibility difference scales with
operator count *within* the treated arm, and whether the history effect survives conditioning on
`nops`. If accessibility is a monotone function of operator count, the effect is machinery presence.
If it is not, the "history reorganised comparable machinery" reading gains support for the first time.

**Both are re-analyses of committed rows. Neither is an experiment.** They are specified here and, per
§12, not run.

---

## 2. The other candidates, same audit, compressed

| Work | Manipulated | Immediate-by-definition | Common-cause risk | Precedence tested | Conditioning on cheap state | Verdict |
|---|---|---|---|---|---|---|
| **Kouvaris 2017** | fitness function / environment | nothing — operator untouched | **Severe.** Both readouts are deterministic functionals of the same frozen `B`. | no | no | Cleanest intervention, worst coupling. |
| **Kounios 2016** | representation on/off (one-to-one map vs GRN) | the map itself | **Severe**, and the same machinery-presence shape as HC-T01: the one-to-one arm has no map to reorganise. | partial | no | Shares HC-T01's confound; does not cure it. |
| **Parter 2008** | goal schedule (FG/MVG/NBVG) | nothing — operator fixed | moderate | no | no | Local + exhaustive + all arms + SE; wrong intervention class. |
| **Petak 2025** | environment (static vs variable) | nothing | moderate | no | no | Best local longitudinal detector; selection-side. |
| **Tiso 2024** | GRN architecture × transfer function | the architecture | high — architectures differ in more than variation structure | descriptive only | no | Closest single work; no control-arm detector, `n = 1` link. |
| **Draghi 2010 SI 6.2** | nothing ablated | n/a | **fatal for the question**: accessibility was *modelled as a function of* robustness, so they are collinear by design | within-run design present | **attempted and impossible** | The only within-run `t → t+n` accessibility design found; cannot answer the conditioning question. |
| **Wagner 2023** | nothing ablated | n/a | **low — uniquely** | no (static landscape) | **YES, by definition** | Solves conditioning; not longitudinal, not an ablation. |
| **Cowperthwaite 2008** | nothing ablated | n/a | low | n/a | effectively yes | **Published negative:** founding accessibility predicted nothing (`r = −0.023`, `P = 0.17`) while target abundance predicted arrival (`r = 0.76`). |
| **Ancel & Fontana 2000** | nothing ablated | n/a | **tautology**: the accessibility measure *is* neutrality, i.e. robustness | no | impossible, same number | **Sign inverted:** the richest-history class became a dead end. |

## 3. The three family-wide hazards, and which are confirmed

**H-1 — COUPLING. CONFIRMED, family-wide.** In every design where the accessibility statistic and the
acquisition outcome are both read off one frozen object, their agreement is close to definitional.
Kouvaris 2017 is the extreme case. HC-T01 is a weaker case because acquisition comes from continued
evolution. Ancel & Fontana is the degenerate case where the two are literally the same number. The
one clean exception found anywhere is Wagner 2023, and it is clean precisely because the current-state
term is subtracted in the definition.

**H-2 — CEILING-BOUNDED OUTCOME. CONFIRMED for HC-T01, and it is new here.** Not previously named in
this programme. Any outcome of the form "gain toward a fixed optimum" is arithmetically dominated by
distance from the optimum, which makes current fitness the sufficient statistic and any accessibility
challenger a loser by construction. This is distinct from H-1 and is a property of the *outcome*, not
of the detector.

**H-3 — MACHINERY PRESENCE. CONFIRMED for HC-T01 and for Kounios 2016.** When a mechanism ablation
removes a class of machinery rather than reorganising it, the ablated arm differs from the treated arm
in *what exists*, not only in *how it is arranged*. Every downstream difference is then explicable
without any appeal to evolved reorganisation. **This is the direct answer to directive question 6, and
the answer is that the operator ablation made causal identification worse, not better.** A selection-side
intervention of the Kouvaris/Parter type does not have this problem: there, both arms possess the same
machinery class and differ only in how selection shaped it.

## 4. Is "local accessibility predicts future acquisition" separable at all? (directive §5)

**In the substrates surveyed, usually not — but for three different reasons that must not be
collapsed.**

1. *Definitional coupling* (H-1): detector and outcome are two reads of one object. Fixable by
   changing the design so acquisition is genuinely subsequent and on held-out targets.
2. *Arithmetic coupling* (H-2): the outcome is ceiling-bounded. Fixable by changing the outcome
   variable, or by partialling out current state.
3. *Tautology* (Ancel & Fontana): the accessibility measure and the cheap state variable are the same
   quantity. Fixable only by choosing a different accessibility measure.

**It is separable in principle, and Wagner 2023 shows the construction that separates it**: define the
accessibility statistic as a residual after the current-state contribution is removed, at which point
it becomes formally equivalent to average positive epistasis. That the field has a name and a theory
for the object should discipline how Prometheus describes it.

Whether it is separable *in this programme's substrates* is unknown, because the one design that could
have told us — HC-T01's K7 — was scored with marginal rather than partial correlations against a
ceiling-bounded outcome. **That is a question the committed data can answer without a new experiment.**
