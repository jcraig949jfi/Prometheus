# Instrument line FROZEN 2026-09-30 (PKG-F / LM02 / LM01)

Authority: operator direction 2026-09-30, step 3: "Then freeze this line."

Frozen at: bf90a73bb (branch ensorain/base-role-adopt-2026-09-23).

What later collider work inherits:

| component | status | where |
|---|---|---|
| Strict drift gate (gate of record) | FROZEN. Low power => QUARANTINED; leak 3e-4 | ensorain/arc3/pkgf_obs.py (obs_keep; DELTA .25, 1.645 TOST, tau_eff fallback 5n/6) |
| PKG-F-HIER | FROZEN as a LABELED experimental arm, never the gate of record. POPULATION_SUPPORTED is kept distinct from CERTIFIED_FRESH. Valid only under a declared representativeness assumption; falsified by HIDDEN (.124 > .10) | ensorain/arc3/lm02/assay.py (hier_keep) |
| Window policies | WINDOW_NOT_SUPPORTED: no window preserves attainable competence. Ordering and anomaly conclusions are robust at WINDOW_3 (82/88, 83/88) | ensorain/arc3/lm02/RESULTS_LM02_ASSAY.md |
| Change detector v9b | UNCHANGED. Mid-ramp placement documented, and not the cause of the RAMP failures | ensorain/arc3/RESULTS_PKGF_PROBE.md |
| LM01 (WTP-LM01 v0.3.2 @ ee8cbe0c8) | HOLD. Not launched merely because it is ready; revisit only if a collider result makes it the right falsifier | ensorain/PREREG_WTP_LM01.md |

Rules for collider experiments that use history:
- A claim computed on retained history states which gate built the record set.
- Any POPULATION_SUPPORTED records are reported separately, with the stratum bound.
- Competence comparisons across memory policies are made against ATTAINABLE, never against a full-life reference,
  unless data availability is the question.
- No further PKG-F / LM02 development without a new operator order.
