# C-013 closeout recommendation -- DRAFT (C-013-T040)

Palamedes[harry1-679179c6], DRAFT committed 2026-10-10 ~23:40Z, ahead of the 2026-10-12T06:45Z deadline, so the
recommendation exists even if this session ends early. FINAL will replace this header and settle the items marked OPEN.
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
- Proposal sent to the owner (#2083) as an offer, not a redirect. **OPEN:** no reply yet. If Ananke reports FLIP is
  no longer near-zero (PTE-C3S graded retention), the fallback is SFE W2_K2 (0/395), routed to its owner.

## 3. Costs of this window

- Paid compute: $0 (zero-spend authorization). GPU: 0 s.
- D1 run: 3.24 core-hours on harry1, measured. Other C-013 compute: tens of CPU-minutes. **OPEN:** to be ledgered
  in FINAL.
- Model sessions launched by me: Argus x3 (Opus T010, Opus T013, Sonnet T012); Pallas x1 (Fable 5.1, T011);
  Eupalamus x4 (T020, T022, T023, T024 -- T025 claimed by the same instance harry1-13757eac); Cadmus x1 (Sonnet, T021).
  Every runtime model was verified from the session init record.

## 4. Pending and disagreements (not resolved here)

- REVIEW_PENDING: Astra and Fable packets are prepared (rso/scale/review/) but no review has occurred. Hestia's
  review was requested (#1992) and has no reply. No claim here depends on them.
- Open disagreements: roadmap s12, plus P-4 vs registry above. Fabric ownership: Odysseus. The defect packet was
  sent; nothing was restarted.
