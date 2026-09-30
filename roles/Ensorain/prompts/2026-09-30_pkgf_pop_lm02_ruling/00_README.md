# 2026-09-30 operator ruling: PKG-F-HIER arm + LM02 framing (operator -> Ensorain, direct chat)

Received ~11:40Z in the Ensorain session (instance m2-a466d709). 01 is verbatim; the horizontal-rule glyph was
transliterated to "---", nothing else changed. Answers the population-evidence question raised after fe6393297.
- Population evidence is a SEPARATE arm (PKG-F-HIER). The strict gate (pkgf_obs.obs_keep) is untouched as the
  conservative reference.
- States: CERTIFIED_FRESH / POPULATION_SUPPORTED / QUARANTINED / CHANGED, with provenance kept through scoring.
- Requirements: a preregistered stale-risk upper bound <= p_max (one governing value); stratified pooling (a global
  pool only as a weak baseline); a coverage minimum; adversarial concentration worlds as the main falsifier; graded
  reuse optional.
- LM02: STRICT / WINDOW / HIER / FULL / ORACLE. Seven scores over the listed regimes. Gradual drift read at BOTH the
  detector placement and the oracle boundary. Verdicts: WINDOW_SUFFICIENT, POPULATION_EVIDENCE_ADDS_VALUE,
  WINDOW_REGIME_DEPENDENT, WINDOW_NOT_SUPPORTED (stop).
