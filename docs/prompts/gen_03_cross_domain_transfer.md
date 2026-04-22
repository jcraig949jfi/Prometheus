# Generator #3 — Cross-Domain Projection Transfer Matrix

**Status:** Tier 0 (ready now, no new infra).
**Role:** Producer.
**Qualification:** any Harmonia session; familiarity with `harmonia/memory/coordinate_system_catalog.md`.
**Estimated effort:** one tick for domain catalog + first matrix pass; ongoing as new projections/domains added.

---

## Why this exists

A projection (P-ID) is a coordinate system. Some projections are domain-specific by construction (e.g., P028 Katz-Sarnak requires an L-function family). Others are domain-agnostic at their core but have only been tried against one domain (e.g., P052 prime decontamination was invented for NF/EC couplings; nothing in its logic prevents applying it to MF coefficients or Artin Frobenius traces).

**Every projection-that-transfers is a Langlands-flavored signal.** Every projection-that-doesn't is terrain (adds a negative dimension). The systematic enumeration produces a (P × D) matrix where every cell is a definite task.

---

## Inputs

- **Projection catalog:** `harmonia/memory/coordinate_system_catalog.md` — 42 projections as of 2026-04-19.
- **Domain catalog:** does not yet exist at a canonical path. First deliverable of this generator is to build it.
- **Data sources:** LMFDB Postgres mirror (EC, NF, MF, g2c, Artin, L-functions), knot data in `harmonia/data/knots/`, and anything else currently queryable.

---

## Process

### Phase 1 — build domain catalog

Create `harmonia/memory/domain_catalog.md`. Each domain entry carries:

```yaml
id: D_EC
name: Elliptic curves over Q
data_source: lmfdb.ec_curvedata + lmfdb.bsd_joined + lmfdb.lfunc_lfunctions
cardinality: 3824372
representative_fields: [conductor, rank, torsion_order, cm_disc, root_number, regulator, sha_order, Lhash]
typical_feature_classes: [arithmetic_invariants, L-function_statistics, zero_spacings, moment_ratios]
domain_specific_projections: [P023 rank, P025 CM, P026 semistable, P035 Kodaira]
```

Enumerate: `D_EC` (elliptic curves), `D_NF` (number fields), `D_MF` (modular forms), `D_ARTIN` (Artin reps), `D_G2C` (genus-2 curves), `D_KNOTS` (knots), `D_L` (L-functions), `D_HMF` (Hilbert/Bianchi MF if data present), `D_HIGHER_GENUS` (if present).

Target: ≥ 7 domains enumerated.

### Phase 2 — build transfer matrix

For each `(P, D)` pair:

1. **Applicability classification** — three-way:
   - `applies_directly`: the projection's logic is domain-agnostic; can be run as-is against D.
   - `applies_with_adaptation`: the projection's logic transfers but needs a domain-specific adapter (e.g., "conductor" becomes "level" for MF, "discriminant" for NF).
   - `inapplicable`: the projection references a D-irrelevant quantity (e.g., "rank of an elliptic curve" doesn't apply to knots).

2. **Cell fill:** if `applies_directly` or `applies_with_adaptation`, and not already tested, this is a new task.

3. **Task emission:** seed `transfer_P{ID}_to_D{ID}` on Agora at priority `-0.7` (background), higher (`-1.5`) for any P that resolved ≥ 2 features in its origin domain.

### Phase 3 — run the high-priority subset

Let workers claim tasks. Each completion writes:
- A new `SIGNATURE@v2` per (P, D) run.
- A cell in `harmonia/memory/transfer_matrix.json` with `{P, D, verdict, adapter_commit}`.
- If resolving, possibly a new feature F-ID in domain D.

---

## Outputs

- `harmonia/memory/domain_catalog.md` — the canonical domain enumeration.
- `harmonia/memory/transfer_matrix.json` — (P × D) cells with applicability + verdict.
- N ≥ 100 seeded Agora tasks at varying priorities.
- For every "applies_with_adaptation" cell: an adapter spec file in `harmonia/adapters/<P>_to_<D>.md`.

---

## Epistemic discipline

1. **An adapter is a new coordinate system, not a faithful transfer.** Any `applies_with_adaptation` run emits a new P-ID (via `reserve_p_id()`) for the adapted projection, not a re-use of the origin P-ID. Pattern 15 discipline ("machinery is the product") — the adapter is the instrument.
2. **Apparent transfers are Pattern 5 candidates.** A projection that "works" in two domains may be measuring a *shared known structure* (Langlands, class field theory, modularity). Before claiming novelty, run Pattern 5 check against the literature.
3. **Null-protocol claim-class check applies.** A transferred projection inherits its claim class; the class-appropriate null must run (`null_protocol_v1.md`).
4. **Pattern 30 gate mandatory for any correlation-based projection post-transfer.** Algebraic couplings can exist across domains (e.g., Mahler measure of NF discriminant polys vs EC conductors — both involve |Disc|).

---

## Acceptance criteria

- [ ] `domain_catalog.md` with ≥ 7 domains.
- [ ] `transfer_matrix.json` populated with applicability classification for all (42 × 7) = 294 cells.
- [ ] At least 50 high-priority tasks seeded.
- [ ] At least 3 tasks completed and verdicts recorded as proof-of-concept.
- [ ] Commit message cites this spec + counts.

---

## Composes with

- **#5 attention-replay** — new P-IDs from adapters trigger replays on killed F-IDs.
- **#2 null-family** — transfers land as `SIGNATURE@v2` with full family vector.
- **#9 cross-disciplinary transplants** — this generator is the intra-math analog; #9 is the outer ring (physics, CS, stats).
- **#6 pattern auto-sweeps** — mandatory gate on every transfer verdict.

---

## Claim instructions (paste-ready)

> Claim `gen_03_cross_domain_transfer_seed`. Execute Phase 1 (domain catalog) + Phase 2 (matrix population) per `docs/prompts/gen_03_cross_domain_transfer.md`. Seed ≥ 50 tasks. Commit `harmonia/memory/domain_catalog.md` + `transfer_matrix.json`. Post `WORK_COMPLETE` with counts and top-10 high-priority (P, D) picks.

---

## Version

- **v1.0** — 2026-04-20 — initial spec from generator pipeline v1.0.
