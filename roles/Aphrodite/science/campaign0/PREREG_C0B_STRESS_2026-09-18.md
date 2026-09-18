# Campaign 0B preregistration: adversarial stress qualification of the frozen assay (2026-09-18)

EVIDENCE TIER 2. Committed BEFORE any Campaign 0B code. Authority: the
operator's disposition of 2026-09-18 (prompts/2026-09-18_c0_disposition/
OPERATOR_DISPOSITION_verbatim.md): "one Campaign 0B stress test ... No
new scientific claim. Just adversarial assay qualification under three
generator pathologies". Not a new campaign; no GPU; no LLM.

## 1. What is frozen

The assay is used EXACTLY as run in Campaign 0 (assay.py at 6195af410):
same contrasts, t across lineages, Holm over 16, TOST at delta 0.03,
Lakens verdicts, flags, recovery rules, reliability bar (>= 0.90 with
Wilson lower >= 0.85). The operator: "Stop tuning the assay to improve
recovery on the current nine worlds." No analysis change is made in
response to 0B results inside 0B; a failure is reported, and any repair
is a later, separately preregistered step.
The nine worlds keep their MEAN planted effects; each pathology changes
only HOW an effect is distributed across lineages and families.

## 2. The three pathologies (each applied alone to all nine worlds)

P1 HEAVY-TAILED LINEAGES. Every lineage-level random quantity -- the
   machinery heterogeneity h_l, the lineage baseline v_l, and W9's null
   shift z_l -- is drawn from a Student-t with 2.5 degrees of freedom,
   rescaled so its scale parameter equals the C0 standard deviation
   (heavy tails; variance finite but large, occasional extreme lineages).
P2 SIGN-CHANGING FAMILY INTERACTIONS. Per lineage and family, the
   machinery effect is multiplied by a factor drawn from {4.0, 1.333, 0,
   -1.333} with equal probability (mean 1.0): outstanding on some
   families, harmful on others, inert on the rest. Applied to MACH only
   (the effect under test). W9's z_l is likewise multiplied per family.
P3 JACKPOT LINEAGES. Each lineage is a jackpot with probability 0.10;
   the machinery effect is multiplied by 10 in jackpot lineages and by 0
   elsewhere (mean preserved; ~10% of lineages carry the whole gain).
   W9's null becomes a jackpot null: z_l = +1.0 in jackpot lineages and
   -0.111 elsewhere (mean zero).
Memory (m), worker (w) and compute (kappa) effects are unchanged: the
pathologies target the claim the program cares most about -- transfer
of machinery -- and the nulls.

## 3. Grid

L in {32, 64}; R = 200 per (pathology, world, L); fixed seeds distinct
from Campaign 0.

## 4. Pass condition (fixed now)

Calibration first. 0B PASSES iff at L = 64, under EVERY pathology:
(a) both nulls (W6, W9) keep the false-positive Wilson upper bound
    <= 0.10; and
(b) every non-null world meets the Campaign 0 reliability bar.
Reported separately, because the operator's question is whether the
assay stays CALIBRATED: a pathology that lowers recovery but keeps
false positives controlled is a POWER loss (the assay becomes
conservative); a pathology that raises false positives is a
CALIBRATION failure (the assay is fooled). The report names which.
On a fail: stop and report; no repair inside 0B.

## 5. Also run in the same job (the operator asked for the delta consequences)

A delta table (re-analysis only, no new worlds): for delta in {0.02,
0.03, 0.05} and L in {16, 32, 64}, on the Campaign 0 generator:
(i) TRANSFER recovery over the MDE shift grid {0.1 .. 0.6} and the MDE;
(ii) the rate at which the exact null is shown EQUIVALENT;
(iii) W4 (specialisation) recovery. The operator owns delta; this table
only states what each choice buys.

## 6. What this cannot show

A 0B pass raises confidence that the assay is not fooled by these three
structures; it does not cover every realistic violation (e.g. temporal
dependence across generations, correlated lineages from a shared seed
artifact). It remains tier 2 and authorises nothing.

## 7. Eligibility, checked before freezing

- P3 at L = 64: expected ~6.4 jackpot lineages; P(no jackpot) = 0.9^64
  ~ 0.1%. A W1 jackpot lineage gains ~4 logit, so the across-lineage
  mean is detectable but skewed: recovery MAY fall below the bar (a
  power loss); that is a legitimate outcome, not an ineligible gate.
- W9 under P3: mean zero in logit; in solved share ~+0.0015 (Jensen),
  negligible against delta 0.03.
- W6 is essentially untouched by P2 and P3 (no machinery to redistribute)
  and by P1 except through v_l, which cancels within every contrast; W9
  therefore carries the calibration test.
