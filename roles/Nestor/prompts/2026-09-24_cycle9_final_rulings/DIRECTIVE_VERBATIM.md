# Operator directive, 2026-09-24 -- final Cycle-9 rulings, freeze and launch

Captured VERBATIM. Nothing below the rule is edited, reflowed or summarised. This file is
authoritative and wins over any later summary. Issued in answer to the S4 review
(`campaigns/z80atlas-verify-2026-09-22/S4_CANDIDATE.md`), after the merge to main at
d64e85e4e.

---

Apply these final Cycle-9 rulings.

Do not perform more general mining of the 72-hour predecessor.

1. H4 = WITHHOLD.
    Remove H4 from this campaign. Preserve the H4 autopsy and record A-4 as withdrawn. Do not redesign H4 before Cycle 9.
2. H2:

* keep the 16-specimen P-11 panel;
* 16 shared seeds/specimen;
* primary strong endpoint = max_causal_replication_depth >= 5;
* specimen supports the strong endpoint iff B >= 8/16 and C <= 2/16;
* panel-level support requires at least TWO supporting specimens from different frozen strata;
* exactly one supporting specimen = isolated candidate, not a panel-level positive;
* preregister depth >=2 and depth >=3 as secondary readouts only.

3. P-11 authorship:
    Primary definition = causal_value_authorship: the donor receives causal credit when it is the last context to CHANGE a byte into its final donor-matching value.

A later same-value rewrite does not erase that causal attribution.

Keep literal-last-write attribution as mandatory sensitivity analysis.

Report both:

* primary P-11 reassay: 57 surviving runs;
* literal sensitivity: 48.

Do not rewrite the frozen predecessor result of 1,031 under its historical criterion.

4. H3 / C9-D11:
    Do NOT replace H3 with EXTERNAL reproduction.

Repair the reservoir ancestry certificate so every hereditary PAIR_EXECUTION edge it traverses must itself be P-11 causal. A predecessor-only/non-P-11 pair edge breaks the causal certificate.

Add fail-on-old-code tests for:

* fully P-11-causal easy->migration->hard-cross chain: PASS;
* otherwise identical chain with a non-P-11 edge: FAIL;
* mixed chain containing one noncausal edge: FAIL.

Repick H3 prospectively from the completed P-11 record.

Use the TWO unique RESERVOIR cells represented by:

* 4931614d912c52b2-s1190-tL-a0 and its same-cell survivor;
* a62116831aa6d956-s7926-tM-a0.

Use 32 shared seeds per cell and three arms:
A easy niche + migration
B homogeneous niches + identical migration
C easy niche + migration disabled

H3 total = 192 runs.

5. Final manifest should therefore be approximately:

* H1: 240
* H2: 768
* H3: 192
* H4: 0
    Total approximately 1,200 runs.

Use the generated manifest count as authoritative.

Do not pad runtime to fill 24 hours.

6. Amend PREREGISTRATION.md and its amendment log. Regenerate the manifest, panel/protocol hashes and timing projection.
7. Run every pre-freeze gate including:

* existing P-1 through P-11 gates;
* S3 tests;
* new H3 P-11-causal ancestry test;
* report audit;
* prefreeze calibration;
* manifest validation;
* hash reproducibility.

If all gates pass, no new validity defect appears, and projected runtime remains acceptable:

FREEZE CYCLE 9.

At freeze:

* write final grammar/protocol/manifest/panel/constants hashes into the preregistration;
* create CALIBRATION.json only through the explicit freeze path;
* record the launch commit;
* create the production observatory only after freeze succeeds.

Then LAUNCH the fixed manifest.

After launch:

* no HITL;
* no result-dependent allocation;
* no threshold changes;
* no replacement jobs;
* no scientific steering from interim results.

Consume the frozen manifest, drain cleanly, adjudicate everything, produce the audited report, and return only when the campaign is complete.

If a NEW scientific-validity defect appears before launch, stop instead of repairing across the freeze boundary.
