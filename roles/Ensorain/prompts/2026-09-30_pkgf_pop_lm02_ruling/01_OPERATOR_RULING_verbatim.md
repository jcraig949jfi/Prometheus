OPERATOR RULING

Allow population-level evidence as a separate experimental arm.

Do not alter or reinterpret the repaired strict PKG-F gate.

Name the new arm something like:

PKG-F-HIER
or
PKG-F-POP

The strict per-cell gate remains the conservative reference.

---

1. What the new arm is allowed to infer

The arm may infer:

Tested cells show sufficiently little evidence of change that some reuse of old information from currently untested cells may be justified.

It may NOT infer:

Untested cells are known fresh.

Keep those states distinct.

For example:

CERTIFIED_FRESH
POPULATION_SUPPORTED
QUARANTINED
CHANGED

Do not collapse POPULATION_SUPPORTED into CERTIFIED_FRESH.

Preserve provenance through downstream scoring.

---

2. Require a quantitative stale-risk bound

Population evidence must produce an explicit upper bound on the fraction of stale cells/records consistent with the observed tested sample.

For example, use a binomial/Beta-binomial/appropriate stratified confidence bound.

The exact statistical instrument may be chosen before the run, but preregister it.

Conceptually:

observed changed fraction among testable cells
    +
uncertainty
    <= p_max

Only then may population-supported reuse occur.

Test multiple declared p_max values if useful, but choose one governing value before evaluation data.

---

3. Stratify rather than pool blindly

Do not let ten stable cells in one region certify fifty unobserved cells in a structurally different region.

Pool evidence only within declared exchangeability classes such as:

region
tensor mode
graph community
drift regime
world component
other predeclared structural strata

A global pooled arm may exist as an intentionally weak baseline.

The scientifically serious version should be stratified.

---

4. Require coverage

Population inference is invalid if only a tiny or highly biased fraction of a stratum is observable.

Precommit a minimum:

number of tested cells
and/or
fraction of stratum tested

before population certification is possible.

Insufficient coverage means:

QUARANTINE

not freshness.

---

5. Test adversarial concentration

Build worlds where drift is:

diffuse
localized
community-specific
mode-specific
clustered in rarely revisited cells

The population gate should fail or become conservative when changed cells are systematically hidden from the tested sample.

This is the main falsifier.

If PKG-F-HIER works only because the tested cells happen to be representative in easy worlds, it has not solved the problem.

---

6. Prefer graded reuse if practical

A useful experimental variant is to weight old information according to the inferred freshness probability rather than admit it all-or-nothing.

For example:

weight_old = f(P(fresh | population evidence))

Keep this optional.

Do not make LM02 depend on inventing the perfect weighting function.

The binary population-supported arm is sufficient for the first assay.

---

LM02 FRAMING

Proceed with LM02, but now compare at least:

STRICT
    repaired per-cell PKG-F
WINDOW
    simple recent-window policy
POP/HIER
    bounded population-evidence reuse
FULL
    all historical information
ORACLE
    only truly nonstale historical information

The last two are diagnostic references, not realistic policies.

---

LM02's actual question

Do not ask merely:

What window length matches full-history statistics?

Ask:

Under what environmental regimes can bounded temporal memory preserve the downstream scientific conclusions we care about?

Score:

downstream competence
substrate ordering
anomaly detection
stale-record contamination
useful information retained
false freshness
unnecessary quarantine

Across:

stationary worlds
abrupt drift
gradual drift
multi-switch worlds
localized drift
several drift rates
several substrates

---

IMPORTANT: SEPARATE THE GRADUAL-DRIFT DEFECT

The mid-ramp detector placement issue is a separate instrument problem.

Do not let LM02 silently attribute its errors to insufficient windows.

For gradual-drift worlds, report at least two readings:

actual detector placement
oracle regime boundary

This tells us:

error due to detector placement

versus

error due to memory/window policy

Do not repair detector placement during LM02 unless a preregistered validation shows the experiment is otherwise uninterpretable.

---

LM02 VERDICT

Use a bounded result.

WINDOW_SUFFICIENT

A stable range of windows preserves the relevant downstream outcomes across the declared regime envelope.

POPULATION_EVIDENCE_ADDS_VALUE

The strict/window policy loses useful stationary or slowly changing information, while the population-evidence arm recovers a meaningful fraction without exceeding the stale-risk bound.

This may coexist with WINDOW_SUFFICIENT.

WINDOW_REGIME_DEPENDENT

No single window works generally, but window requirements follow identifiable world/drift variables.

This is scientifically interesting; report the dependency.

WINDOW_NOT_SUPPORTED

No stable sufficiency region exists, or preserving useful information requires unacceptable stale leakage.

Stop there.

Do not tune until success appears.

---

INTERPRETATION

The stationary-world +0.60 old-information gain is worth pursuing because it demonstrates that strict per-cell certification pays a real price.

The question is whether structural evidence about the population can recover that information safely.

If yes, we have something more interesting than a window heuristic:

a system deciding when knowledge about observed parts of a world can support bounded trust in unobserved parts.

If no, the result is equally valuable:

temporal knowledge cannot safely generalize across cells under these world dynamics without stronger structural assumptions.

Proceed with LM02 under this framing.
