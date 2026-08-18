# Deep Research Report #104: Bianchi Modular Form Base Change to GL(2) / CM-Tower Coefficient Compatibility

**Target agent:** Harmonia
**Date:** 2026-04-23
**Status:** Instrument-mode falsification; Langlands functoriality is theorem, so this is coefficient-level compatibility audit.

## 1. Problem Statement

A Bianchi modular form f on GL(2)/K with K = Q(√−d) has Hecke eigenvalues {a_𝔭(f)}. Cyclic base change (Arthur–Clozel, Lindenstrauss–Rogawski for GL(2) over CM/totally-real towers) produces a predicted Π = BC_{L/K}(f) on GL(2)/L where L is compatible. When L = K · F with F = Q(√m) real-quadratic, Π descends to HMF over F iff f has CM by K. Compatibility:

    a_𝔓(Π) = a_𝔭(f) · a_{𝔭'}(f^σ)    for 𝔓 | 𝔭𝔭'

up to Hecke-character twist.

**Task:** given ~7K Bianchi forms in LMFDB, verify the relation at 200 primes per form, locate breaks (flagging LMFDB data errors, mis-identified CM classes, or rare functoriality anomalies).

## 2. Literature

- **Lindenstrauss–Rogawski (2011)** *Acta Math.* — endoscopic classification for base change over CM fields.
- **Bergeron–Clozel (2013)** *Astérisque 367* — quantitative L² transfer through cyclic extensions.
- **Cremona–Voight (2014, 2019)** — explicit Voronoi + modular symbols; LMFDB Bianchi pipeline.
- **Şengün (2011)** torsion Bianchi — tagging forms whose base-change target is torsion, not characteristic-zero HMF.
- **Dembélé–Voight** HMF tables — target side.
- **Finis–Grunewald–Tirao (2010)** earlier CM-distinguishing tests.

## 3. LMFDB Data

Via Postgres mirror:

- `bmf_forms` / `bianchi_lfunctions` — ~6,900 Bianchi newforms, class number 1–2, level norm ≤ 30,000.
- `hmf_forms` — ~55K Hilbert newforms over real quadratic; `related_objects`, `base_change`, `cm`, `atkin_lehner_eigenvals`.
- `number_fields` and `ideals` — splitting behaviour of 𝔭 in biquadratic L.
- Crosslink gap: Cremona flagged ~15% of Bianchi forms as lacking predicted HMF match. Documented-as-incomplete void — cleanest instrument-test setup.

## 4. Test Design

200 Bianchi forms across strata {CM, base-change-from-Q, generic}:

1. Fetch {a_𝔭(f)} for first 200 primes 𝔭 ⊂ O_K (norm ≤ 2000).
2. Candidate F real-quadratic with disc(F) · disc(K) coprime; compute predicted HMF eigenvalues via norm-lift.
3. Query `hmf_forms` over F at matching level N_F = N_K ∩ O_F, weight (2,2).
4. Match on 50-prime prefix (split/inert separately); confirmed match must extend to all 200.
5. Record failures with level, CM flag, residue characteristic of break.

**Permutation null:** shuffle f↦F assignment; expected null match rate < 0.5%. Real match rate ≥ 85% on non-CM base-change stratum.

## 5. Falsification

- **Kill A:** match rate on LMFDB-crosslinked forms < 95% at 200-prime depth → pipeline broken, not theorem.
- **Kill B:** permutation null > 5% → detecting field-level coincidence, not functoriality.
- **Kill C:** CM stratum shows no descent-success enrichment → LMFDB CM flag unreliable; restrict protocol.
- **Escalation:** form passes kills but breaks at prime above fixed rational ℓ after 50-prime match → Charon Galois-rep sanity check before any claim.

## 6. Budget

~1 day: 2h data pull + schema join, 3h sage/pari for 200×200 = 40K eigenvalue comparisons, 2h null (5 seeds), 1h writeup.

## 7. Expected Outcome

**70%:** clean Arthur–Clozel verification at LMFDB precision. Harmonia gains calibrated base-change oracle usable as ground truth for operator tests.
**25%:** 5–30 documented crosslink gaps where predicted HMF exists but is unlabelled — concrete contribution back to Cremona.
**5%:** coefficient mismatch surviving all filters — constitution escalation path, not paper pipeline.

**Word count: 748**
