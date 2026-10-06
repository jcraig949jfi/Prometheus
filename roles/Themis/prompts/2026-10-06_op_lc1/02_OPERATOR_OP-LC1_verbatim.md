# OP-LC1 -- operator approval of the Lane C (M4) proposal (verbatim)

The operator's words, byte for byte from the session transcript (session 0e9b1ed2-f51f-49c9-a2ea-5c93be2dfb1c).
AUTHORITY for campaign C-008 (TH-MOON-M4, Lane C, D1-D5), the bounded GitHub D4 arm, and two
contract changes to R-EP (semantic identity independent of git; ACCEPTED renamed PUBLISHED).

---

## 2026-10-06T08:31:04.540Z

OP-LC1 APPROVED.

Proceed with TH-MOON-M4 / C-008 and the D1-D5 Lane C work.

GitHub is authorized for one bounded WAN-semantics D4 arm, with these constraints:

1. No synthetic epoch traffic on Prometheus main or its production ref namespace.
2. Scaling/stress sweeps run against a disposable local-network bare remote. GitHub validates real-remote semantics; it is not intentionally driven to failure.
3. First GitHub arm: dedicated/disposable Moonshot repo or remote, preferably repo-scoped credentials, maximum 2 concurrent workers and 250 write attempts total. Stop on throttling, authentication spillover, or interference with unrelated Prometheus work.
4. Test both single-ref and per-chain-ref designs locally. Freeze the D4 bounds before observing the baseline.

Two contract changes before D1/D3 freeze:

* Git commit SHA is transport identity, not scientific identity. Define a transport-independent canonical SHA-256 semantic identity over the epoch inputs/spec/runtime and canonical outputs. Git refs and commits locate those bytes.
* Rename successful CAS ACCEPTED to PUBLISHED. A push grants no scientific authority. Validation/acceptance is a separate state. DUPLICATE, DISAGREEMENT/QUARANTINE and AMBIGUOUS remain explicit. A disagreement discovered after descendants exist taints that branch until deterministic replay resolves it.

Contested chains fail closed. Attempt metadata and costs stay outside the canonical trace; every attempt is still charged.

Add the proposed D3 cases: ambiguous push, planted disagreement, leases disabled, unapproved-code spec and skewed worker clock.

For D4 retain the proposed coordination/retry/latency/abandonment bounds, and also record bytes transferred per accepted epoch and repository growth per accepted epoch. The 1 GB/30-day limit may remain as an operational tripwire.

moonshot/epoch/, standard-library-only where practical, is approved. First commit may be the complete D3 matrix as failing tests.

M4 synthetic work proceeds in parallel and does not gate the other Moonshot/RSO closure work. Native distributed reproductive populations remain out of scope until D3/D4 establish the required semantics.
