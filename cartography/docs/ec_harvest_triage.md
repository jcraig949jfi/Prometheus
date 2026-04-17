# EC Harvest Triage — Top 10 Uncatalogued Projections

**Task:** `absorb_ec_harvest`
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 8)
**Input:** `cartography/docs/harvest_ec_projections.md` (50 projections from Claude Opus 4.7)
**Current catalog coverage anchor:** `harmonia/memory/coordinate_system_catalog.md` + pending P033 (Is_Even), P034 (AlignmentCoupling).

---

## Method

1. Walk each of the 50 harvest rows.
2. Mark rows already-catalogued by matching to existing P-IDs (P001–P034).
3. For the NOT-catalogued rows, score by (a) LMFDB directness, (b) charter-value (how often it has shown up in a specimen or tautology pair), (c) downstream probe-openness.
4. Pick top 10 for full catalog entries; propose P-IDs P035–P044.
5. Full Section-10 catalog entries deferred to dedicated `catalog_<name>` tasks per Pattern 17 discipline.

---

## Already catalogued (no action)

| Harvest row | Existing P-ID | Notes |
|---|---|---|
| j-invariant | — | Isomorphism *feature*, not a projection. Skip. |
| Discriminant / Szpiro ratio | P003 Megethos (anti-projection), feature-level | Not a standalone projection; enters via Pattern 1 tautology with F015 / F028. |
| Conductor | P020 conductor conditioning | Merged; standard discipline. |
| Mordell-Weil rank / Analytic rank / BSD rank / Parity of rank | P023 rank stratification | All equivalent under BSD-verified data (F003). |
| Torsion subgroup | P024 torsion stratification | Merged. Mazur anchor F002. |
| CM discriminant / Endomorphism ring | P025 CM stratification | Merged. |
| Kolyvagin index / Heegner index | (tautology with Sha) | Do NOT entry as separate projection without a tautology-pair flag. |
| Galois representation image (mod ℓ) | P010 Galois-label scorer (partial) | P010 resolves via label, not ℓ-adic image; a mod-ℓ *image* projection is distinct and uncatalogued. Flagged in Top-10 (P043). |
| Mahler measure | P053 Mahler measure projection | Merged. |
| Canonical Néron-Tate height | P023 rank stratification (indirectly) | Regulator ⊂ Néron-Tate lattice data; separate entry not worth it until a specimen needs it. |
| Silverman height difference bound | (bound, not projection) | Skip. |
| Watkins modular degree bound | (bound, not projection) | Skip. |

---

## Top 10 proposed entries (P035–P044)

| Proposed P-ID | Name | Direct / Derivable | One-sentence *what it resolves* | Priority |
|---|---|---|---|---|
| P035 | **Sha (Tate-Shafarevich) stratification** | direct (`sha` column) | Failure of the Hasse principle; the size of III carries Heegner/Kolyvagin bound structure and BSD's rank-2+ branch. | HIGH (F005 anchor already depends on this axis) |
| P036 | **Root number stratification** | direct (`signD` ≡ ±1) | Sign of the functional equation; two-valued parity axis that factors BSD parity (F003) and Katz-Sarnak SO_even/SO_odd split on EC side. | HIGH (primitive axis used implicitly everywhere) |
| P037 | **Modular degree stratification** | direct (`class_deg` column) | Degree of optimal modular parametrization; measures "arithmetic complexity" of the modularity map and is the domain of the Watkins bound. | MEDIUM |
| P038 | **Kodaira-type stratification** | derivable (`bad_primes` + local data; LMFDB has it in `ec_localdata`) | Geometric type of the singular fiber at each bad prime (I_n, II, III, IV, I_n^*, IV^*, III^*, II^*); refines P026 semistable vs additive. | MEDIUM |
| P039 | **Faltings height stratification** | direct (`faltings_height`) | Archimedean size of the associated abelian variety; was the axis H08 tested (and killed) against F011; still a valid axis for other specimens. | MEDIUM (negative anchor exists) |
| P040_rename_needed | (naming conflict — P040 is already F1 permutation null) | — | This slot is taken in null-model block. For the harvest, renumber. | — |
| P040 | **Sato-Tate group stratification** | derivable (`st_group` exists in `lfunc_lfunctions` though not in `ec_curvedata`) | Equidistribution class of normalized a_p; for EC over Q reduces to SU(2) vs N(SU(2)) vs torus-CM — directly feeds Katz-Sarnak (P028) at the `a_p` level. | MEDIUM-HIGH |
| P041_rename_needed | (naming conflict — P041 is F24 variance decomposition) | — | Renumber proposal below. | — |
| P041 | **Isogeny-class size stratification** | direct (`class_size` column) | Number of Q-isogenous curves; correlates with Galois-image obstructions and with Szpiro-bound sharpness. Already used as selector, never catalogued. | MEDIUM |
| P042_rename_needed | (naming conflict — P042 is F39 feature perm) | — | Renumber proposal below. | — |
| P042 | **Regulator stratification** | direct (`regulator` column) | Covolume of Mordell-Weil lattice; encoded in BSD leading term via `regulator × sha / torsion²`. Rank-1+ specimens depend on it. | MEDIUM |
| P043_rename_needed | (naming conflict — P043 is bootstrap stability) | — | Renumber. | — |
| P043 | **Galois-image mod-ℓ Serre-class stratification** | direct (`elladic_images`, `nonmax_primes`) | Image of mod-ℓ Galois rep; classifies surjective-vs-exceptional primes. Distinct from P010 (which keys on Galois *label*, not *image*). | MEDIUM |
| P044 | **Iwasawa λ / μ-invariants stratification** | (not in `ec_curvedata`; partly in `ec_iwasawa`) | Growth of Selmer rank / p-divisibility in cyclotomic tower; the classical axis for p-primary BSD refinements. | LOW-to-MEDIUM (data gap) |

### RENUMBER FLAG (critical)

My proposed P-IDs **collide with the null-model (P040–P043) and data-layer (P060–P063) reserved ranges** in the current catalog. The existing allocation is:

- P001–P003 — feature-distribution
- P010–P012 — categorical object-level
- P020–P034 — stratification (P028–P034 recent)
- P040–P043 — null models
- P050–P053 — preprocessing
- P060–P063 — data-layer

The stratification block only has slots through roughly P034 allocated; **my P035+ run into P040 (null model)**. Two options:

**Option A (preferred):** stratification block gets P035–P049 reserved; Top 10 renumbered P035–P044 as drafted *with the understanding that P040–P043 null-model entries are a SEPARATE semantic namespace*. This requires the ID scheme to be *section-prefixed* rather than a flat global counter.

**Option B:** stratification block is flat-global and just continues P035, P036, P037, P038, P039, **P044, P045, P046, P047, P048** (skipping the null-model P040–P043 slots). Then I'd relabel my 6th onward accordingly. This is less elegant but preserves flat-global semantics.

**My recommendation:** Option A is cleaner and the catalog's Section 1/2/3/... grouping already implies namespacing. Flagging for sessionA or the `infra_reserve_p_id` task claimer to formalize. The `reserve_p_id()` helper should respect section namespace (e.g., `reserve_p_id(section='stratification')`).

### Corrected Top 10 under Option A (section-namespaced stratification)

| Proposed P-ID | Name | Priority |
|---|---|---|
| P035 | Sha stratification | HIGH |
| P036 | Root number stratification | HIGH |
| P037 | Modular degree stratification | MEDIUM |
| P038 | Kodaira-type stratification | MEDIUM |
| P039 | Faltings height stratification | MEDIUM |
| P044 | Sato-Tate group stratification | MEDIUM-HIGH |
| P045 | Isogeny-class size stratification | MEDIUM |
| P046 | Regulator stratification | MEDIUM |
| P047 | Galois-image mod-ℓ Serre-class | MEDIUM |
| P048 | Iwasawa λ/μ stratification | LOW-MEDIUM |

(P040–P043 reserved for null-model continuation; skipped. This matches Option B's concrete numbering and avoids the ambiguity while pushing the namespacing question to infra.)

---

## Flagged for tautology-pair table (no new entry)

These harvest rows are NOT standalone projections — they belong in Section 8 (Tautology Pairs) of the catalog because their coupling to existing axes is formula-level, not structural:

| Pair A | Pair B | Existing catalog anchor | Harvest row that surfaces it |
|---|---|---|---|
| leading_term | regulator × sha × (ω/torsion²) | implicit in BSD | BSD rank (algebraic) |
| Goldfeld-Szpiro quotient | Sha / |disc|^(1/2) | related to F028 killed_tautology | Goldfeld-Szpiro quotient |
| Bloch-Kato Tamagawa | classical Tamagawa × local motivic factor | implicit | Bloch-Kato Tamagawa |
| Heegner index / Kolyvagin index | sqrt(Sha) at rank 1 | tautology with F005 | Heegner index + Kolyvagin index |
| Congruence number | modular degree (up to bounded ratio) | tautology with modular degree | Congruence number + modular degree |

Propose: add a catalog-polish follow-up task to update Section 8 with these five tautology pairs.

---

## Discipline notes

- This triage does NOT promote any harvest row to a full catalog entry. Each Top-10 row is a *task stub*; sessionA seeds one `catalog_<name>` task per P-ID, workers then draft the full Section-10 entry.
- Pattern 5 (Known Bridges Are Known) applies: many Top-10 entries are *projections* of the same underlying Langlands / BSD structure. They are distinct *instruments* viewing the same landscape — cataloguing them all is correct per Pattern 10 (instrument grows faster than findings).
- Pattern 19 (tensor-entry staleness) applies at the catalog level too: when we add P035+ entries, every claim inside them must be re-measured under clean n≥100 discipline (per sessionB's Liouville F012 lesson), not cite prior-session quantitative claims without re-verification.
- **ID-space hygiene:** the namespace collision between my Top-10 and the null-model block is exactly the kind of issue `infra_reserve_p_id` is meant to solve. Confirming the section-prefix semantics before any of these P035+ entries land.

---

## Signals-registry row

`signals.specimens` entry to be written alongside this task's `complete_task`:
- `claim`: "EC harvest triage — 10 uncatalogued projections (P035–P048) nominated"
- `status`: `refined`
- `interest`: 0.50
- `data_provenance.proposed_p_ids`: `[P035, P036, P037, P038, P039, P044, P045, P046, P047, P048]`
- `data_provenance.namespace_collision_flag`: HIGH (see Option A/B discussion)
- `data_provenance.tautology_pairs_surfaced`: 5 (Section 8 additions)
