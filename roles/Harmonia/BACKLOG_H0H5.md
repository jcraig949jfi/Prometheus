# Harmonia backlog -- H0-H5 qualification

Schema: `roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md`.
Priority order. The first five are what I start today. 34 items.

Seat scope: controls, units, qualification, and what the evidence permits. I
own no execution and gate no release -- a scientific verdict and a software
milestone are separate axes (QR-1.1.0).

    ID | item | lane | milestone | size | blocked_on | evidence of done

## Start today

HARM-01 | Amend the four-cell analysis file to dedup by spec hash, record fresh==S00 as one baseline under two labels, and state the shared-arm correlation between the transport contrast and G | H0 | alpha | S | none | `roles/Harmonia/qualification/h0h5/h0_analysis_plan.json` with three distinct payload hashes and four labels, and a refusal test that fires when one hash appears under two cell labels
HARM-02 | Add the exchangeability diagnostic to the QR module (serial r against `committed_seq`, trend fraction, and the three-class label at the 0.577/0.816 cuts) so any detector output can carry it | ENGINE | beta | S | none | `exchangeability.py` plus a test reproducing 12/5/23 on the live dossier
HARM-03 | Write the vacuous-reading register and seed it with H2-over-C3-2, `stable`-vs-`at_T`, and the H1 relevance arm at 3 bits | EVIDENCE | program | S | none | `roles/Harmonia/VACUOUS_READINGS.md`, one row per question with the corpus that could not answer it and the reason
HARM-04 | Extend the adversarial battery to AF-1.1.0 with a degenerate-replicate fixture, a structural-floor fixture, and a non-exchangeable-rows fixture | ENGINE | beta | M | none | `adversarial_fixtures.py` at AF-1.1.0 with 9/9 detected and each new detector's silence verified on a clean control
HARM-05 | State the QR-1.2.0 beta and 1.0 gate for H1, with attainable range and eligibility count per gate | H1 | beta | M | none | `qualification_rules.py` at QR-1.2.0 with `lane_gate("H1")` returning both gates and their attainable ranges

## Qualification rules, one lane at a time

HARM-06 | State the QR beta and 1.0 gate for H0, with the joint-treatment and interaction contrasts sized separately from a pilot-estimated Sigma | H0 | beta | M | HARM-05 | `lane_gate("H0")` plus a worked sizing at the pilot Sigma
HARM-07 | State the QR beta and 1.0 gate for H2, keeping computation, causal contribution and frozen reuse as three separate results | H2 | beta | M | none | `lane_gate("H2")` with three gates, not one
HARM-08 | State the QR beta and 1.0 gate for H3, with prospective utility as the endpoint and archive diversity explicitly excluded from it | H3 | beta | M | none | `lane_gate("H3")` and a refusal test that rejects diversity as an endpoint
HARM-09 | State the QR beta and 1.0 gate for H4 under `H4-ADAPTIVE-1.0.0`, with the frozen-suite endpoint and the training-task prohibition mechanical | H4 | beta | M | none | `lane_gate("H4")` plus a test that refuses any endpoint computed on training tasks
HARM-10 | State the QR beta and 1.0 gate for H5, with the analytic access bound predeclared so only the excess over construction counts | H5 | beta | M | none | `lane_gate("H5")` carrying the <=8 vs 12 bound as a declared constant
HARM-11 | Declare the multiplicity rule ACROSS lanes, so six lanes reporting primaries do not accumulate an unstated family-wise rate | program | 1.0 | M | none | `MULTIPLICITY.md` with the declared family, the correction, and the family-wise rate under it
HARM-12 | Publish the three-quantity separation (meaningful effect, precision, power) as a one-page rule every lane cites when it sizes | program | beta | S | none | `SIZING_RULE.md` and every `lane_gate` naming which of the three it promises

## Detectors and calibration

HARM-13 | Apply the exchangeability diagnostic to D1, D2 and D4-D6 and report each detector's class distribution on the live corpus | ENGINE | beta | M | HARM-02 | a committed table, detector x class, with the eligible count per detector
HARM-14 | Declare the calibration-corpus policy: which detectors may be calibrated on i.i.d. draws, and which need a trajectory-structured null | ENGINE | beta | M | HARM-13 | `CALIBRATION_CORPUS_POLICY.md` naming, per detector, the null family its rate is valid under
HARM-15 | Build the trajectory-structured null and recalibrate D3 under it at the live geometry | ENGINE | beta | L | HARM-14 | a rate with its binomial SE at (n=40, k=4) under trended rows, beside the i.i.d. rate
HARM-16 | Record the three EXCHANGEABLE survivors as a watch-list with their geometry and class, and the reopening condition | ENGINE | program | S | none | `D3_WATCHLIST.md` with three rows and the condition that would license a study
HARM-17 | Recompute my binomial-null calibration at the family's actual L under the trajectory null, since the i.i.d. result does not apply to the live corpus | ENGINE | beta | M | HARM-15 | an amended calibration file stating which corpus each rate is valid for
HARM-18 | Adjudicate d3.v2 (detrended statistic) if the operator admits it, with its own calibration and its own eligibility count | ENGINE | 1.1 | XL | operator decision NEW: admit or refuse d3.v2 as a new detector version | a ruling file, or a recorded refusal with the reason

## Corpora and analyses

HARM-19 | Rule the C3-3 readout against R-C3-1..6 once Archaeon issues it, including the support size, p_mode and f | C3 | beta | M | Archaeon (C3-3 issue) | a ruling file with the eligibility count printed before any gate
HARM-20 | Register the X1 variance-ratio test across descriptor regions as H2's instrument for C3-3, with its null and attainable range | C3 | beta | M | HARM-19 | a frozen `analysis.v1` manifest hashed before the corpus is read
HARM-21 | Rule the H1 beta readout once the pool condition (P >= 4K) is measured and reported | H1 | beta | M | Archaeon, Proteus (pool measurement) | a ruling with the realised pool, K, and mean inter-arm pack overlap
HARM-22 | Rule the H0 four-cell readout once the artifact cells run, reporting G and I separately with the measured SE ratio | H0 | beta | M | Vivarium (`reserve_budget` 404) | a ruling with both estimands, the pilot Sigma, and `se_ratio_report`
HARM-23 | Freeze `nk.k_variance_ratio.v1` and commit its manifest hash before the A3 corpus is read | C1 | beta | S | Archaeon (A3 corpus), NK length reconciliation | the committed manifest and its hash, timestamped before the first source read
HARM-24 | Declare the PEW encounter analyses nobody has declared yet, one `analysis.v1` manifest per question the encounter record can answer | EVIDENCE | program | L | none | one manifest per analysis, each with unit, null, eligible count and mode
HARM-25 | Declare the analysis for H3's prospective-utility comparison before its stream is generated | H3 | beta | M | none | a frozen manifest with the four policies as arms and the shared caps recorded

## Contracts and instruments

HARM-26 | Regenerate the SFE contract at live schema 7 and re-verify the gate in both directions | ENGINE | beta | M | Daedalus (scratch engine at build parity) | a new `sfe_contract.json`, its diff reviewed, and `conformance_check.py` CONFORMANT on live and DRIFT on a mismatched engine
HARM-27 | Extend the contract procedure to schema 8 without adding version-range tolerance to the gate | ENGINE | 1.1 | S | HARM-26 | the schema-8 contract and a test proving the gate still fails closed on any mismatch
HARM-28 | Add a payload-determinism attestation to the contract-fixture stage, so a replay is recorded as an attestation and never enters an analysis as a replicate | ENGINE | alpha | S | none | a fixture that passes on bit-identical replay and a refusal test that rejects replay rows used as replicates
HARM-29 | Add a structural-floor precheck that any corpus must pass before issue: report modal mass, support size and non-degenerate fraction | ENGINE | beta | M | none | `floor_precheck.py` that refuses a corpus with p_mode > 0.50 and reproduces C3-2's f = 0.000
HARM-30 | Add the shared-arm correlation to `paired_contrast` so contrasts sharing a baseline are not reported as independent | ENGINE | beta | S | HARM-01 | the function returning the induced correlation, with a test on the fresh/S00 case

HARM-35 | Extend the SFE contract to model the RESPONSE surface, so a removed or renamed response field is DRIFT rather than silence | ENGINE | beta | L | none | contract records per-route response fields; a fixture proving a removed response field reports DRIFT where today it reports CONFORMANT

## Standing and program

HARM-31 | Write the standing-rules index so HA-1.1-1.6, R-C3-1..6 and the exchangeability cut are findable from one file | program | program | S | none | `roles/Harmonia/STANDING_RULES.md` linking every rule to the ruling that established it
HARM-32 | Audit every number quoted in my own rulings for the population it was measured on, and correct any quoted outside its scope | program | program | M | none | an audit file listing each quoted number, its population, and any correction
HARM-33 | Run the grant and verify Archaeon's read scope end to end once the credential exists | ENGINE | alpha | S | operator (harmonia-m2 credential) | rows, census and out-of-scope isolation verified, or a recorded reissue path
HARM-34 | Rule whether a diagnostic alpha may ever be promoted to confirmatory evidence, and write the refusal into `validate_plan` | program | 1.0 | S | none | a test proving a DIAGNOSTIC plan cannot be relabelled CONFIRMATORY after its data is read

## Blocked, listed rather than hidden

    HARM-18  operator decision on d3.v2
    HARM-21  the pool measurement (Archaeon, Proteus)
    HARM-22  Vivarium's `reserve_budget` 404
    HARM-23  the NK length discrepancy (BRANCHES 24 vs packet v2 N=16)
    HARM-26  a scratch engine at live-7 build parity (Daedalus)
    HARM-33  the harmonia-m2 credential (operator), and F-6 (Daedalus)

XL rows needing an operator decision, so the operator's queue is derivable:
**HARM-18** only.
