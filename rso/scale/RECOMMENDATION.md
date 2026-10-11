# C-013 closeout recommendation -- FINAL (C-013-T040)

Palamedes[harry1-679179c6]. Draft 2026-10-10 ~23:40Z; FINAL 2026-10-11 ~10:10Z. C-013 closed EARLY under the operator's
Continuous Observatory directive of 2026-10-11 s1 (roles/Palamedes/prompts/2026-10-11_continuous_observatory/), which
accepts s1 below as the next engineering investment and opens the successor campaign C-016.
Sources: rso/scale/RSO_SCALING_ASSESSMENT.md, rso/scale/PROMETHEUS_SAGACITY_SCALING_ROADMAP.md (s4, s12, s13),
rso/reach/RESULT.md + INTEGRATION_D1.md, rso/scale/LONG_DURATION_EXECUTION_ARCHITECTURE.md, rso/scale/runner/.

## 1. Next engineering investment

**Event-driven integration plus a qualified-component registry.** This replaces my v1 provisional choice, the P-4
port of the runner onto C-012's transport.

- Why: in C-013, with headless seats launched the moment a packet went READY, claim latency fell to a median of
  5 min. 85% of the remaining waiting (312 of 367 min) was packets waiting for the integrator's hourly poll
  (assessment s2; an upper bound, because that time includes the integrator's own checks). B1 (bespoke
  qualification) is still the largest cost per new evidence path. The registry makes a qualified component (ledger,
  binding, receipts, mutation runner, certifier, stratified/Holm analysis) carry its qualification stage and its
  pinning tests, so a reuse pays only for its adapter. First entry: D1's analyzer, re-deriving `discovery` from its
  components (INTEGRATION_D1.md s2).
- Why not P-4 now: no Observatory run has needed a second host. Host capacity did bind once (thermal throttling cut
  D1 to 15 of 24 rounds), but the remedy is running one whole seat on a cooler machine, which needs no cross-host
  transport. C-012's owner makes the same "ahead of demand" argument about its own fabric (C012_NF2_REVIEW s7, lean
  A). Revisit P-4 when a registered workload exceeds one host; C-012's N2/N4/N5 are measured and N1/N3 are small
  (comms #2043/#2044), so the port stays cheap.
- Size: small. A comms-triggered integrator wake, plus a registry file with pinning tests. Single-host. No paid compute.

## 2. Next scientific experiment

**The D1 protocol, sized properly, on one audited desert with a near-zero chain baseline at every stratum.** The
desert is Ananke FLIP (0/290), run by its owner.

- D1 was a weak null: NOTHING SEPARATES at N = 15. Power for a +0.20 effect was 0.49; the plain chain scored 4/15 at
  d = 1, and every arm scored 0 at d = 8. Re-running D1 bigger on the same world would buy little.
- Sizing at a 0.01 baseline: N = 24 per (arm, d) detects +0.20 (power 0.95); N = 32 detects +0.15 (power 0.92). At
  Ananke's 3,456-55,296 evaluations per search, this is small and local.
- Proposal sent to the owner (#2083) as an offer, not a redirect. No reply at close. Per the operator (2026-10-11 s1)
  it belongs in Ananke's own program, and no Observatory campaign depends on it. If Ananke reports FLIP is no
  longer near-zero (PTE-C3S graded retention), the fallback is SFE W2_K2 (0/395), routed to its owner.
- The Observatory's own next experiment is set by the operator: a second native runtime, Ensorain (C-016).

## 3. Costs of this window

- Paid compute: $0 (zero-spend authorization). GPU: 0 s.
- CPU, about 4.8 core-hours in all, every hour of it on harry1. Measured: D1 run 3.243 (T012 receipt and ledger) and
  the runner fire test 0.08 (286 CPU-s; FIRE_TEST.md). Estimated by the seats in their receipts: T010 development
  0.6, T011 challenge 0.6, T013 repair 0.1. The integrator's re-checks (two suite runs, re-certification, power
  simulations) were about 0.15, estimated. T020/T021/T023-T025 receipts carry no CPU figure (documents and short
  test suites; minutes). The Observatory's discovery cost is still small next to its proof cost: the D1 run was 2.0 h
  of wall time inside about 9 h from freeze to integration.
- Model sessions launched by me: Argus x3 (Opus T010, Opus T013, Sonnet T012); Pallas x1 (Fable 5.1, T011);
  Eupalamus x4 (T020, T022, T023, T024 -- T025 claimed by the same instance harry1-13757eac); Cadmus x1 (Sonnet, T021).
  Every runtime model was verified from the session init record.

## 4. D1 as recorded (operator 2026-10-11 s1)

D1 is preserved as the under-powered result it produced, and must not be read as evidence that archive-based search has
no benefit.
- Preregistration v1.0.1 (sha256 4e3c10a0) and freeze 8ddaa4f19.
- Actual N = 15 of 24 rounds; the CPU cap truncated it on a thermally throttled host.
- Power 0.49 for +0.20.
- Limitations: rso/reach/RESULT.md s7 and INTEGRATION_D1.md.
- REACHABILITY_CARTOGRAPHY_V0.md is left byte-identical, because it is pinned in FROZEN_D1.json; the result lives in
  RESULT.md and INTEGRATION_D1.md beside it.
- D1 is not re-run.

## 5. Pending and disagreements (not resolved here)

- REVIEW_PENDING: Astra and Fable packets are prepared (rso/scale/review/) but no review has occurred. Hestia's
  review was requested (#1992) and has no reply. No claim here depends on them.
- Open disagreements: roadmap s12, plus P-4 vs registry above. Fabric ownership: Odysseus. The defect packet was
  sent; nothing was restarted.
