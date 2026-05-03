# SHADOW_CATALOG_FINDINGS

Catalog-miss DiscoveryRecords surfaced by the four-counts pilot.

This file is the convention going forward: every pilot run that surfaces
a `terminal_state == "SHADOW_CATALOG"` (sub-Lehmer band, polynomial not
in any of the 5 consulted catalogs, survived the kill-path battery)
appends one entry below. `PROMOTED` records (the same survival shape
plus the spec's stricter promotion criteria) are also logged here.

Both classes are "discovery candidates worth manual review" per
`harmonia/memory/architecture/discovery_via_rediscovery.md`. The
distinction between SHADOW_CATALOG and PROMOTED is essentially how
loud we declare the find — either way, a hand-check is mandatory
before any external claim.

## Entry template

```
### [YYYY-MM-DD] <pilot tag> seed=<n> agent=<random_null|reinforce_agent>
- candidate_hash: <sha256 hex>
- coeffs: [c_0, c_1, ..., c_d]   (ascending, palindromic)
- mahler_measure: <float>        (in (1.001, 1.18))
- terminal_state: <SHADOW_CATALOG|PROMOTED>
- consulted_catalogs: <list>     (e.g., Mossinghoff, Smyth, Boyd, ...)
- battery_pass: F1 / F6 / F9 / F11 / reciprocity / irreducibility
- kill_pattern: <none — by definition; record any non-null for diagnosis>
- claim_symbol: <kernel claim symbol id, if minted>
- notes: <human comment, what to verify next>
```

## Findings log

### 2026-04-29 four-counts pilot 10K x 3 seeds — random_null + reinforce_agent

- pilot harness: `prometheus_math/four_counts_pilot.py`
- driver: `prometheus_math/_run_10k_rich.py`
- raw output: `prometheus_math/four_counts_10k_shadow.json`
- total episodes: 60,000 (10K x 2 conditions x 3 seeds)
- SHADOW_CATALOG records: **0**
- PROMOTED records: **0**

No discovery candidates surfaced. The catalog-miss → claim-into-kernel
rate at this configuration is 0/60000 — a tighter joint upper bound
than the 1K result (0/6000). The action space + prior + battery
collectively admit fewer than ~1/60000 sub-Lehmer survivors at degree
10 / Discrete(7) coefficients / cost_seconds=0.5.

This is the expected outcome at this scale per Lehmer's conjecture
and the +100/+20/+5 reward shape. The next move (per spec §6.2.5) is
either widening the action set, raising degree, or loosening the
battery — not increasing episode count further within the same env.

---

(future entries appended below this line)
