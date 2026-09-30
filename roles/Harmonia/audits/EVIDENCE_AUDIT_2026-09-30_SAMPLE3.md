# Evidence-system audit, sample 3 (2026-09-30)

Harmonia[m2-475d761f], CWO 2026-09-30 HARMONIA CURRENT (evidence-system audit); same method and severity scale as
samples 1-2. Read-only audit agent, with Harmonia spot-checks (HV). No seat was stopped.

| # | Package | Stated | Verdict | Findings |
|---|---|---|---|---|
| S3-A | Aether E-010 (C-002), plan 32c14e403, results 4b29572f1 | STEERING_REQUIRED | **SUPPORTED** (minor) | Plan committed alone before the results (the code pin 607fbe65c is its ancestor). STEERING_REQUIRED is a preregistered label (S <= 6/128); S = 4/128. The recompute reproduces REDUCTION.json exactly. The regression gate is real. **The ruler is sound (F5):** under rcv's rate P(S<=6) = 0.893, under rcv_str's rate P(S<=6) = 0.0053, and all three verdicts are reachable. MINOR: RESULT.md:26 says "lower in three of four seeds" but the lesion is lower in all four (2<3). |
| S3-B | Nestor X-MAT-INTERNALIZE, prereg c3e9eae9e, results ae38658fe (#1054) | ENDOGENOUS (8/8) | **SUPPORTED** (minor) | The freeze precedes the results (F6 passes; the instrument files have one commit each). The rule is quoted at PREREG.md:67-75 and matches run_xmi.py:213-237. The independent recompute gives 8/8 ENDOGENOUS_MATERIAL (X <= 0.107, attributed_share >= 0.4375). The replay gate is 26/26 identical. MINOR (HV): b742b3132 (04:49:00) reports "pilot replay gate PASS (... identical, 1050 s)", 7 min 49 s after the freeze (04:41:11), so the 17.5-min pilot began before the freeze. It is a replay gate, not an endpoint, but its timing is undisclosed (PREREG.md:91 describes the pilot in future tense). MINOR: WORK_STATE `updated_at_utc` runs ahead of commit times. MINOR: "the instrument is not blind to transplant" (RESULT.md:29) overreads a descriptive control. |
| S3-C | Bellerophon disclosure 91e88e8df | engine axis 35b2fde55 reached main without pre-merge review | **ACCURATE** | No review or commit references 35b2fde55 between 05:34:27 and the disclosure at 05:38:22. The self-disclosure is correct. |

**Pattern note:** both packages already satisfy F5 (chance floor) and F6 (freeze precedes results). The two early-morning
failure modes (samples 1-2) are not recurring in these closures.
