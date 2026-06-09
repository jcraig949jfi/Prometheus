# Audit: F044 rank-4 LMFDB selection — companion to frame-based-resample

**Auditor:** Harmonia_M2_auditor
**Run at:** 2026-04-22
**Task:** `audit_F044_rank4_lmfdb_selection` (sessionA, 2026-04-19)
**Companion audit:** `cartography/docs/audit_F044_framebased_resample_results.md` (Harmonia_M2_auditor, same date)

This audit answers the four sub-questions of the LMFDB-selection task. Items (1) and (3) are partial duplicates of the companion audit's findings; cross-reference and extend rather than repeat.

---

## Summary

Same verdict as the companion: **Pattern-4 selection-frame artifact, RETRACTED.**

The companion audit (`audit_F044_framebased_resample`) showed that at conductor ≥ 10⁸, ALL ranks 2-5 in LMFDB are 100% nbp=1 + semistable. This audit adds:

- (1) The 1 exception is `234446.a1` and its structure is fully characterized below
- (2) Direct LMFDB-source-table inspection is not exposed in the local mirror's column set, but the conductor + reduction-type fingerprint of the rank-4 and rank-5 sets is consistent with rank-record-construction sourcing
- (3) Rank-5 verification: ALL 19 LMFDB rank-5 EC are nbp=1 + semistable + non-CM, conductors all prime in [1.9·10⁷, 2.9·10⁸] — confirming the pattern extends to rank 5 and is a continuous high-conductor effect, not a rank-4-discrete one
- (4) Literature-scan for rank ≥ 4 ↔ additive-reduction theorems: deferred to Aporia or a future literature-diff cycle; the companion's cross-rank evidence is already decisive without it

Recommended action is identical to the companion audit: F044 tier `live_specimen` → `killed_selection_frame`; cells (P020/P023/P026) PROVISIONAL +1 → −2; description rewrite + Pattern-4 anchor add. **Conductor approval needed.** Not executed.

---

## Sub-question (1) — the 1 exception

The single rank-4 EC in LMFDB with `nbp ≠ 1` is:

| Field | Value |
|---|---|
| label | `234446.a1` |
| conductor | 234446 = 2 · 117223 |
| num_bad_primes | 2 |
| bad_primes | [2, 117223] |
| ainvs | `[1.0, -1.0, 0.0, -79.0, 289.0]` |
| jinv | `[54915331401.0, 468892.0]` |
| structure | `y² + xy = x³ - x² - 79x + 289` over Q |
| LMFDB conductor rank | LOWEST conductor of the 2086 rank-4 EC in LMFDB |

Position: this curve sits at the LOW boundary of LMFDB's rank-4 conductor range (the next-lowest is much higher). It is in the conductor band where exhaustive enumeration covers (Cremona-style up to ~10⁵–10⁶) and the rank-record construction filter does not yet dominate the curve population. Its existence as an exception, and the fact that no other rank-4 EC with composite conductor appears anywhere in the 2086-curve set, is exactly the signature of a single curve falling into the exhaustive-enumeration window while all the rest came from a different sourcing methodology.

If LMFDB ever extends exhaustive enumeration further into the 10⁶–10⁷ range, the count of "rank-4 with composite conductor" would grow as a function of how much exhaustive coverage is added — not from any new mathematical content.

## Sub-question (2) — LMFDB rank-4 source bias

**Direct query of LMFDB's source-table provenance is not available in the local mirror.** The `ec_curvedata` table I have access to (52 columns) does not expose a `source_table` or `provenance` field that would distinguish "found via Cremona exhaustive enumeration" from "imported from Stein/Elkies/Dujella rank-record tables." Inspection of the LMFDB upstream documentation would be needed to characterize the sourcing pipeline directly.

**Indirect evidence from the conductor + reduction fingerprint:**

The 2086 rank-4 EC distribute by conductor decade:

| Decade | n | Cumulative |
|---|---|---|
| 10⁵–10⁶ | 8 | 8 (0.4%) |
| 10⁶–10⁷ | 75 | 83 (4.0%) |
| 10⁷–10⁸ | 722 | 805 (38.6%) |
| 10⁸–10⁹ | 1281 | 2086 (100%) |

96% of LMFDB's rank-4 set lives at conductor ≥ 10⁷. Cremona's exhaustive enumeration historically covers conductor up to roughly 5×10⁵ (with extensions into 10⁶ partially). Above ~10⁶, the curve population is dominated by curated additions: BSD verifications, isogeny-class extensions of seed curves, and rank-record constructions specifically. The 96%-above-10⁷ fingerprint is consistent with rank-record-construction dominance.

The reduction-type fingerprint sharpens this: rank-record constructions use methods (Heegner-point liftings, congruent-number families, isogeny walks from seed curves of known small rank, X² + Y³ = N family searches) that systematically produce curves with **simple bad-reduction structure** — typically prime conductor with multiplicative reduction. Constructions that produce composite conductor or additive reduction tend to be filtered out or never explored, because such curves are harder to verify rank for and the constructive methods often don't produce them in the first place.

The companion audit's smoking gun — at conductor ≥ 10⁸ ALL ranks 2-5 are 100% prime-conductor + semistable — is the cleanest expression of this. The selection filter is so strong above 10⁸ that it homogenizes the curve population across all ranks examined.

## Sub-question (3) — rank-5 verification

LMFDB has **19 rank-5 EC**. ALL 19:

- nbp = 1 (single bad prime = prime conductor)
- semistable = True
- cm = 0 (non-CM)
- conductor in [19,047,851, 288,935,749] — all prime, all in the rank-record-construction range

Per-curve summary:

| Conductor | Label | First few `a_invs` |
|---|---|---|
| 19,047,851 | `19047851.a1` | `[0,0,1,-79,342]` |
| 64,921,931 | `64921931.a1` | `[0,0,1,-169,930]` |
| 67,445,803 | `67445803.a1` | `[0,1,1,-30,390]` |
| 74,129,723 | `74129723.a1` | `[0,0,1,-301,2052]` |
| 84,602,123 | `84602123.a1` | `[0,0,1,-457,3786]` |
| 106,974,317 | `106974317.a1` | `[1,0,0,-575,5236]` |
| 111,061,427 | `111061427.a1` | `[1,0,0,-245,1366]` |
| 117,138,251 | `117138251.a1` | `[0,-1,1,-82,622]` |
| 122,882,843 | `122882843.a1` | `[0,-1,1,-400,3262]` |
| 138,437,407 | `138437407.a1` | `[1,-1,1,-147,420]` |
| 161,759,189 | `161759189.a1` | `[0,1,1,-142,182]` |
| 169,624,549 | `169624549.a1` | `[0,0,1,-139,72]` |
| 177,858,971 | `177858971.a1` | `[0,0,1,-679,6840]` |
| 185,220,011 | `185220011.a1` | `[0,-1,1,-482,4290]` |
| 214,371,643 | `214371643.a1` | `[0,1,1,-100,770]` |
| 232,113,701 | `232113701.a1` | `[0,1,1,-8506,299132]` |
| 238,055,563 | `238055563.a1` | `[0,1,1,-214,1346]` |
| 271,522,949 | `271522949.a1` | `[0,1,1,-332,2082]` |
| 288,935,749 | `288935749.a1` | `[0,0,1,-259,1380]` |

19/19 = 100% prime-conductor + semistable. No exceptions at rank 5. This continuity with the companion audit's high-conductor finding (100% across ranks 2-5 above 10⁸) confirms that whatever filter produces the rank-4 fingerprint applies just as strongly to rank 5. The pattern is rank-monotone in concentration only because the lower ranks include conductor regimes (10⁴–10⁶) where the filter does not yet dominate.

If F044's "theorem hiding in plain sight" hypothesis were correct, we would expect rank-5 to also be uniformly nbp=1 + semistable — which it is, but this is unfortunately not informative because it is what BOTH the theorem-hypothesis AND the selection-frame-hypothesis predict. The discriminating evidence remains the cross-rank comparison at the same conductor band as in the companion audit.

## Sub-question (4) — literature scan for rank ≥ 4 ↔ additive-reduction theorems

**Deferred.** A theorem search for "rank ≥ 4 forbids additive reduction" or "rank ≥ k constrains conductor type" would close this question independently. I have no direct external-search infrastructure in this audit context, and the cross-rank evidence in the companion audit is already decisive — the literature scan would be insurance, not the load-bearing argument.

A heuristic note from general arithmetic-geometry intuition: there is no widely-known theorem of the form "rank ≥ k implies semistable reduction" or "rank ≥ k forbids additive reduction." Local-global considerations (Tate's algorithm, Néron models) constrain global rank weakly through bad-reduction Tamagawa contributions in the BSD formula, but the connection runs in the opposite direction (rank → torsion / Sha / Tamagawa correlations) rather than rank → reduction-type-restriction. The Birch-Swinnerton-Dyer leading-term identity does not single out additive reduction at high rank in any way I am aware of.

If a theorem search later surfaces a known constraint, this audit's verdict should be re-examined. Until then, the selection-frame interpretation is the strongest hypothesis consistent with the data.

A future task `lit_check_rank4_additive_reduction_theorem` would close this cleanly via Aporia's literature-diff infrastructure (`gen_07`).

---

## Recommended actions (same as companion)

The recommended tensor mutations are unchanged from the companion audit:

1. F044 tier: `live_specimen` → `killed_selection_frame`
2. F044 cells (P020, P023, P026): PROVISIONAL +1 → −2
3. F044 description rewrite: Pattern-4 selection-frame interpretation; cite both audits
4. Pattern 4 anchor update: F044 as fourth anchor (construction-biased-sample sub-class)
5. Optionally seed `lit_check_rank4_additive_reduction_theorem` via gen_07 to close sub-question (4) independently

Conductor approval needed for items 1-4. I have not executed any of them.

## Cross-references

- `cartography/docs/audit_F044_framebased_resample_results.md` — companion audit; the cross-rank comparison evidence
- `harmonia/memory/build_landscape_tensor.py` — F044 entry to be rewritten on conductor approval
- `harmonia/memory/decisions_for_james.md` — 2026-04-22 23:30 UTC entry on F044 retraction recommendation
- LMFDB `ec_curvedata` table on `192.168.1.176:5432 lmfdb/lmfdb@lmfdb`

— Harmonia_M2_auditor, 2026-04-22.
