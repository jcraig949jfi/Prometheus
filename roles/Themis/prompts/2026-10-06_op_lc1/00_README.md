# 2026-10-06 OP-LC1 -- Lane C (M4) approval

Operator approval of Themis's Lane C proposal, given in chat on SPECTREX5 (session
0e9b1ed2-f51f-49c9-a2ea-5c93be2dfb1c). This directory is the authority for campaign C-008 under
TH-MOON-M4 (EP-MOONSHOT) and for the contract changes below.

- 01_THEMIS_PROPOSAL_verbatim.md -- the proposal being approved (context only).
- 02_OPERATOR_OP-LC1_verbatim.md -- the operator's words, byte for byte (authority).

What OP-LC1 authorizes (summary; 02 governs where this differs):
- Proceed with TH-MOON-M4 / C-008 and D1-D5. Code in moonshot/epoch/, standard-library-only where
  practical. The first commit may be the complete D3 matrix as failing tests.
- No synthetic epoch traffic on Prometheus main or its production ref namespace.
- Scaling/stress sweeps only against a disposable local-network bare remote. Both single-ref and
  per-chain-ref designs are tested locally. D4 bounds are frozen before the baseline is observed.
- ONE bounded GitHub arm for WAN semantics: a dedicated/disposable Moonshot repo or remote,
  preferably repo-scoped credentials, at most 2 concurrent workers and 250 write attempts in
  total; stop on throttling, authentication spillover, or interference with unrelated Prometheus
  work. GitHub validates real-remote semantics; it is not driven to failure.
- Contract change 1: the git commit SHA is TRANSPORT identity, not scientific identity. A
  transport-independent canonical SHA-256 semantic identity is defined over the epoch
  inputs/spec/runtime and canonical outputs; git refs and commits only locate those bytes.
- Contract change 2: successful CAS is PUBLISHED (was ACCEPTED). A push grants no scientific
  authority; validation/acceptance is a separate state. DUPLICATE, DISAGREEMENT/QUARANTINE and
  AMBIGUOUS stay explicit. A disagreement discovered after descendants exist taints that branch
  until deterministic replay resolves it.
- Contested chains fail closed. Attempt metadata and costs stay outside the canonical trace; every
  attempt is still charged.
- D3 adds: ambiguous push, planted disagreement, leases disabled, unapproved-code spec, skewed
  worker clock.
- D4 keeps the coordination/retry/latency/abandonment bounds and also records bytes transferred and
  repository growth per accepted epoch; 1 GB/30 days stays as an operational tripwire.
- M4 does not gate other Moonshot/RSO closure work. Native distributed reproductive populations stay
  out of scope until D3/D4 establish the required semantics.

Themis disposition: ACCEPT in full. Where the operator's wording says "accepted epoch" in the D4
metrics, Themis reports both denominators -- per PUBLISHED epoch (the transport unit) and per
VALIDATED epoch -- so neither reading is lost (recorded in the C-008 preregistration).
