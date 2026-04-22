# Materialization Sprint — Kodaira / Modular-Degree / Truncated Euler Product

**Status:** Paste-ready task spec. Ergon or Techne claims; not Harmonia.
**Source:** `harmonia/memory/trajectory_proposals.md` §Instance 3 Proposal 2.
**Scope owner:** Mnemosyne (DBA) + Ergon or Techne (compute).
**Drafted by:** Harmonia_M2_sessionD, 2026-04-22 (wave 0, task T4).
**Qualification:** `ergon_or_techne` — requires Postgres write access on
the prometheus-side shadow schema, PARI/GP or Sage installation, and
patience for a multi-million-row compute pass.
**Priority for Agora seed:** -1.5 (high — unblocks ~5 pending specimens).

---

## Why this exists

Three catalog entries (`P035` Kodaira, `P052` microscope, `P103`
modular_degree) and one worker pipeline (`U_B` split/non-split) all
wall against the same infrastructure gap: **LMFDB has the answer
*derivable* per-curve, but our read-only mirror doesn't store it.**

Running Tate's algorithm or Sage `modular_degree` per request, per
worker, is untenable at scale. A one-time sprint that writes three
materialized columns to a prometheus-side shadow table unblocks every
downstream specimen simultaneously.

**Key Pattern-1 discipline:** materialization alone is not a
*finding*. It is the infrastructure that lets subsequent workers
produce findings that survive audit. The sprint's ROI is measured in
"specimens a block-shuffle null can actually test" after it ships,
not in any claim about the materialized values themselves.

---

## Three sub-tasks (each stands alone; order matters for dependencies)

### Sub-task A — Kodaira per prime per EC

**Goal:** write one row per `(lmfdb_label, prime)` pair for each
curve's bad primes, carrying the Kodaira symbol and split/non-split
flag.

**Target schema (prometheus-side shadow):**

```sql
CREATE TABLE ec_kodaira_per_prime (
    lmfdb_label text NOT NULL,
    prime bigint NOT NULL,
    kodaira_symbol text NOT NULL,          -- 'I_1', 'II', 'III', 'IV',
                                            -- 'I_0*', 'I_n*' (with n), 'II*',
                                            -- 'III*', 'IV*'
    multiplicative boolean NOT NULL,        -- true iff I_n (any n >= 1)
    split_multiplicative boolean NULL,      -- true if split I_n; false if
                                            -- non-split; null if additive
    tamagawa_local integer NOT NULL,        -- c_p
    conductor_exponent_local integer NOT NULL, -- f_p (for sanity check
                                            -- against Ogg's formula)
    computed_at timestamptz NOT NULL DEFAULT now(),
    computed_by text NOT NULL,              -- 'PARI 2.17' or 'Sage 10.5', etc.
    PRIMARY KEY (lmfdb_label, prime)
);
CREATE INDEX ec_kodaira_by_label ON ec_kodaira_per_prime (lmfdb_label);
CREATE INDEX ec_kodaira_by_symbol ON ec_kodaira_per_prime (kodaira_symbol);
```

**Compute path (choose one; document which in every
`computed_by` value):**

- **PARI/GP** `ellglobalred` — fastest for batch (C-compiled, Tate's
  algorithm native). Returns Kodaira + c_p + f_p in one call per curve.
  Example:
  ```gp
  e = ellinit([a1, a2, a3, a4, a6]);
  gr = ellglobalred(e);   \\ [N, [fact of N], c, [[p, f_p, c_p, kodaira], ...]]
  ```
  The per-prime tuple is `[prime, f_p, c_p, kodaira_code]`. Kodaira
  codes: 1→I_0, 2→I_1,…, 4→II, 5→III, 6→IV, negative codes for
  starred types per PARI convention. Tate classification is proven
  (see `P035` catalog entry §Calibration anchors).

- **Sage** `EllipticCurve(ainvs).local_data(p)` — returns a
  `EllipticCurveLocalData` object with `.kodaira_symbol()`,
  `.tamagawa_number()`, `.conductor_valuation()`. Slower than PARI
  (Python wrapper) but human-readable. Useful for spot-checks.

- **LMFDB public endpoint** — rate-limited, NOT for the 3.8M sweep.
  Use only for cross-validation on a sampled subset.

**Acceptance criteria:**

1. All 3.8M rows of `lmfdb.ec_curvedata` with `num_bad_primes >= 1`
   have at least one row in `ec_kodaira_per_prime`.
2. For every curve, `count(*) = num_bad_primes` (strict equality).
3. For every curve, `sum(conductor_exponent_local)` when joined with
   the curve's bad-prime factorization matches `ec_curvedata.conductor`
   exponent-wise — Ogg's formula sanity check. Any mismatch is a
   data-integrity violation; log to
   `cartography/docs/materialization_sprint_kodaira_ogg_mismatches.json`.
4. 1% random-sampled cross-check against Sage
   `EllipticCurve.local_data(p).kodaira_symbol()` — agreement required at
   ≥99.9% rate (three nines). Any disagreement is a calibration-level
   finding and must be reported, not silently resolved.
5. Known-answer spot-check: curve `11.a1` has Kodaira type `I_1`
   at p=11 with c_11 = 1 (split multiplicative). Every implementation
   must pass this before running the full sweep.

**Unblocks:**

- `catalog_P035_active` — P035 flips from PLACEHOLDER to live-queryable.
- `wsw_F044_P035_audit` — rank-4 corridor under Kodaira refinement
  (currently blocked at +1 deferred).
- `wsw_F011_kodaira_stratified` — F011 GUE deficit stratified by
  dominant Kodaira symbol (new lens, complements the 7 existing F011
  projections).
- `P035 × P103 joint` — nested-vs-orthogonal question from P035
  tautology-profile §2 resolvable.

### Sub-task B — Modular degree per EC

**Goal:** write one column per `lmfdb_label`: the modular degree
`deg(φ): X_0(N) → E`, plus the Manin constant and optimality flag.

**Target schema:**

```sql
CREATE TABLE ec_modular_degree (
    lmfdb_label text PRIMARY KEY,
    modular_degree bigint NOT NULL,         -- deg(phi); positive integer
    manin_constant integer NOT NULL,        -- c_E; usually 1
    is_optimal boolean NOT NULL,            -- true for the distinguished
                                             -- isogeny-class rep
    computed_at timestamptz NOT NULL DEFAULT now(),
    computed_by text NOT NULL
);
CREATE INDEX ec_modular_degree_by_optimal ON ec_modular_degree (is_optimal);
```

**Compute path:**

- **Sage** `EllipticCurve(ainvs).modular_degree()` — provable for
  conductor `N <= 10^6` (via Cremona's tables and the L-symbolic
  computation); heuristic beyond. Returns a positive integer.
  Manin constant via `EllipticCurve.manin_constant()`.
- **LMFDB mirror pickle/CSV** — if available via a sister archive (not
  in our read-only mirror). Check with James / Mnemosyne first;
  avoids the 3.8M Sage-compute pass.
- **Magma** `ModularDegree` — alternative, comparable runtime.

**Acceptance criteria:**

1. All 3.8M rows of `lmfdb.ec_curvedata` covered.
2. Every isogeny class has exactly one `is_optimal=true` row — violated
   rows logged to
   `cartography/docs/materialization_sprint_modular_degree_optimal_anomalies.json`.
3. For every non-optimal curve in a class, `modular_degree` is an
   integer multiple of the class's optimal-curve modular degree (per
   `P103` catalog §What it resolves, item 5). Anomalies logged.
4. Known-answer spot-check: curve `11.a1` has `modular_degree = 1`.
5. Cross-domain calibration: `modular_degree × manin_constant` is an
   isogeny-class invariant (Edixhoven-Jong). Verify per class;
   anomalies logged.
6. Rows with conductor `> 10^6` carry a `computed_by` value that
   explicitly flags heuristic vs. provable (convention:
   `'Sage 10.5 (heuristic: N > 1e6)'` or
   `'Sage 10.5 (provable: N <= 1e6)'`).

**Unblocks:**

- `catalog_P103_active` — P103 flips from PLACEHOLDER to live-queryable.
- `wsw_F005_P103_check` — F005 High-Sha cohort vs `modular_degree`
  (per P103 catalog §Follow-ups item 5).
- `audit_edixhoven_jong_pattern1_check` — Faltings-height ↔ modular
  degree Pattern-1 formula-lineage audit.
- Ribet-Taylor-Wiles congruence-prime questions across the full 3.8M.

### Sub-task C — Truncated Euler product p ≤ 200 per EC

**Goal:** materialize `L_p(1, E) = 1 / (1 - a_p·p^{-1} + ε·p·p^{-2})`
for every `(curve, p)` pair with `p ≤ 200, p good`. Product across
these truncations approximates `L(1, E)` well enough to feed `P052`
microscope and `U_B` split/non-split analyses.

**Target schema (two-table design: raw a_p + truncated product):**

```sql
CREATE TABLE ec_ap_per_prime (
    lmfdb_label text NOT NULL,
    prime integer NOT NULL,              -- p, always <= 200
    ap bigint NOT NULL,                  -- a_p = p + 1 - #E(F_p)
    is_bad_prime boolean NOT NULL,       -- p | N_E
    epsilon integer NULL,                 -- +1 / -1 per BSD sign
                                          -- (only for good primes;
                                          -- always 1 for p in Euler product)
    computed_at timestamptz NOT NULL DEFAULT now(),
    computed_by text NOT NULL,
    PRIMARY KEY (lmfdb_label, prime)
);
CREATE INDEX ec_ap_by_prime ON ec_ap_per_prime (prime);

CREATE TABLE ec_euler_truncated (
    lmfdb_label text PRIMARY KEY,
    prime_cutoff integer NOT NULL DEFAULT 200,
    l_at_1_truncated double precision NOT NULL,  -- L_good(1,E; p<=200)
    n_good_primes_used integer NOT NULL,
    n_bad_primes_in_window integer NOT NULL,
    computed_at timestamptz NOT NULL DEFAULT now(),
    computed_by text NOT NULL
);
```

**Compute path:**

- **PARI/GP** `ellap(E, p)` — fastest per-curve, per-prime. Batch over
  the 46 primes ≤ 200 per curve; 3.8M × 46 ≈ 175M rows in
  `ec_ap_per_prime`. Budget ~20-60 minutes on a single modern machine
  depending on parallelism.
- **Sage** `EllipticCurve.ap(p)` — slower Python wrapper; useful for
  spot-checks.
- **Naive point-counting** `ergon/murmuration_isogeny.py:count_points_mod_p`
  already exists; reuse for cross-validation but do NOT use for the
  full sweep (O(p^2) per curve per prime is infeasible at p=199).

**Euler product definition (truncated, good primes only):**

```
L_good(1, E; p <= 200) = prod_{p good, p <= 200} (1 - a_p·p^{-1} + p·p^{-2})^{-1}
```

Bad primes in the window are counted in `n_bad_primes_in_window` but
do NOT contribute to the truncated product — their local factor is
`(1 - a_p·p^{-1})^{-1}` with no `ε·p·p^{-2}` correction, and including
them here would double-count against Kodaira-derived Tamagawa factors
downstream.

**Acceptance criteria:**

1. All 3.8M rows covered in both tables.
2. Every `(curve, p)` row in `ec_ap_per_prime` satisfies the Hasse
   bound: `|a_p| <= 2·sqrt(p)`. Violations logged to
   `cartography/docs/materialization_sprint_hasse_violations.json`.
3. Known-answer spot-check: curve `11.a1` has `a_2 = -2, a_3 = -1,
   a_5 = 1, a_7 = -2, a_{11} = 1` (bad prime, multiplicative). Every
   implementation must pass.
4. 1% random-sampled cross-check against Sage `ap(p)` — 100%
   agreement required (this is an identity, not an approximation).
5. `l_at_1_truncated` is a positive real for rank-0 curves in ≥99% of
   cases. Negatives or near-zeros for rank-0 curves are a
   calibration-level finding (candidate BSD / Manin-constant
   anomaly) — do NOT suppress; flag in
   `cartography/docs/materialization_sprint_euler_rank0_negatives.json`.

**Unblocks:**

- `P052 microscope` — the prime-decontamination pipeline needs
  per-prime `a_p` values; currently the scripts call PARI per query,
  which is the bottleneck. Materialization makes P052 cheap.
- `U_B split/non-split worker` — currently blocked on per-prime
  access to `a_p` at moderate cost; materialization unblocks.
- `audit_F011_P035_P103_triple_stratify` — joint Kodaira × modular
  degree × Euler product analysis on F011 cohort.
- `wsw_F001_a_p_agreement_at_scale` — F001 EC↔MF `a_p` agreement
  theorem check across 3.8M curves × 46 primes = 175M identity
  verifications. Calibration anchor sanity at scale.

---

## Sprint-level acceptance criteria

1. All three tables exist in the prometheus-side shadow schema
   (confirmed via `\d` in psql).
2. Row counts match pre-sprint coverage estimates: ~3.8M × 1 for
   modular_degree, ~3.8M × 1 for euler_truncated, 175M for ap_per_prime,
   variable for kodaira_per_prime (depends on `num_bad_primes`
   distribution; expected ~5-10M rows total).
3. All five known-answer spot-checks (one per sub-task's
   acceptance criterion 3/4/5) pass without silent correction.
4. Anomaly logs (`*_anomalies.json`, `*_mismatches.json`,
   `*_violations.json`, `*_negatives.json`) are produced and
   committed, *even if empty*. Empty anomaly files are a positive
   signal of clean materialization; missing anomaly files are a
   procedure violation.
5. The downstream sessionE worker is notified via Agora
   `share_discovery` on completion; the notification cites the commit
   hash of the materialization, row counts, and anomaly log paths.
6. `harmonia/memory/coordinate_system_catalog.md` P035 and P103
   entries are updated to remove the DERIVABLE-NOT-STORED caveats
   and replace with "materialized as of <date> via <path>; query via
   <join>". Paired commit; Harmonia (not Ergon/Techne) does this edit
   after the compute ships.

## Unblocks list (total 5+ pending specimens)

After the sprint lands, the following become actionable:

1. **`wsw_F044_P035_audit`** (rank-4 corridor × Kodaira) — blocked on A.
2. **`wsw_F005_P103_check`** (High-Sha × modular degree) — blocked on B.
3. **`P052 microscope at scale`** (currently per-query PARI bottleneck) —
   blocked on C.
4. **`U_B split/non-split worker`** (needs per-prime `a_p` at scale) —
   blocked on C, benefits from A (`split_multiplicative` column).
5. **`audit_edixhoven_jong_pattern1_check`** (Faltings × modular degree
   Pattern-1 tautology audit) — blocked on B.
6. **`wsw_F001_a_p_agreement_at_scale`** (calibration-anchor sanity at
   scale) — blocked on C.

Harmonia will file follow-up tasks for each once the sprint completes.

## Non-goals (explicit)

- **No derived analyses during the sprint.** Ergon/Techne materializes;
  Harmonia analyses come after. Mixing material-compute with
  specimen-hunting during a single task violates the purity contract
  and produces Pattern-1 formula-lineage risk.
- **No schema migrations beyond the three tables above.** If a
  downstream analysis needs a fourth column, it files a separate task.
- **No LMFDB upstream writes.** All materialized tables live in the
  prometheus-side shadow schema, *never* in `lmfdb.*`.
- **No silent anomaly suppression.** Every spot-check failure is
  logged and surfaced, not resolved in-line. Calibration anchors
  depend on knowing the failure rate honestly.

## Post-sprint retrospective checklist

At sprint completion, the claimant writes a brief retrospective in
`decisions_for_james.md` covering:

- Total runtime per sub-task.
- Anomaly rates observed vs. expected (Ogg mismatches, optimal-curve
  anomalies, Hasse violations, rank-0 Euler negatives).
- Any sub-task that could not be completed at the stated scope (and
  why — data, compute, license).
- Concrete numbers to feed into the next cycle's
  investment_priorities analysis.

---

## Version log

- **v1** 2026-04-22 — initial paste-ready spec by Harmonia_M2_sessionD
  (wave 0 task T4). Source: trajectory_proposals.md Instance 3
  Proposal 2. Dependencies on P035 and P103 catalog entries (both
  in coordinate_system_catalog.md at catalog-draft status). Agora
  seed to follow at priority -1.5.
