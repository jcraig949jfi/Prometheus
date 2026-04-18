# P-ID Namespace Allocation

**Authority:** `harmonia/memory/coordinate_system_catalog.md` is the source of truth.
**Mechanism:** `agora.work_queue.reserve_p_id()` scans the catalog on every call
and returns `max(counter, scan_floor) + 1` atomically via Lua (sessionB 2026-04-17).
**Rule:** Never reserve a P-ID by hand. Always via `reserve_p_id()`. The
function is self-healing — it reads the catalog max and can't collide.

---

## Section ranges (documentation of current state, NOT enforced)

| Range | Section | Purpose |
|---|---|---|
| P001–P019 | Section 1 (scorers) | Similarity/coupling scorers (P001 cosine, P002 distributional, P003 Megethos, P010 Galois-label object-keyed, P011 Lhash, P012 trace_hash, P034 AlignmentCoupling) |
| P020–P039 | Section 4 (stratifications, original) | First-generation stratifications (P020 conductor, P021 bad-prime count, P022 aut_grp, P023 rank, P024 torsion, P025 CM, P026 semistable, P027 ADE, P028 Katz-Sarnak, P029 MF weight, P030 MF level, P031 Frobenius-Schur, P032 char parity, P033 Is_Even, P034 alignment, P035 Kodaira, P036 root_number, P037 Sato-Tate, P038 Sha, P039 Galois l-image) |
| P040–P049 | Section 5 (null models) | P040 F1 perm null, P041 F24 variance decomp, P042 F39 feature perm null, P043 bootstrap. P044–P049 free. |
| P050–P059 | Section 6 (preprocessing) | P050 first-gap, P051 N(T) unfolding, P052 prime decontamination, P053 Mahler measure projection. P054–P059 free. |
| P060–P099 | Section 7 (data-layer) | P060 TT-Cross bond dim, P061 bsd_joined matview, P062 idx_lfunc_origin, P063 idx_lfunc_lhash. P064–P099 reserved for future data-layer additions. |
| P100+ | Section 4 (stratifications, continuation) | New stratifications after Section 4's original range filled. P100 isogeny_class_size, P101 regulator, P102 artin_dim, P103 modular_degree. Next reservation P104. |

---

## Why the gap at P004–P009, P013–P019

Legacy. Some early scorer IDs were allocated for ideas that were killed
before catalog entry. The gaps are fine — `reserve_p_id()` skips past
used IDs via max-scan; it doesn't care about unused gaps.

If you want to add a scorer and feel the aesthetic pull to use P004,
don't. Let `reserve_p_id()` allocate. Stable IDs > compact IDs.

---

## Why P100+ not P040+ for new stratifications

`reserve_p_id()` would happily hand you P044 today (no collision), but
convention is: **new Section 4 stratifications go P100+**, leaving
P040–P099 reserved for null-models (P040–P049), preprocessing (P050–P059),
and data-layer (P060–P099) growth.

This is documentation, not enforcement. If you end up at P109 and want
P044, you can — but the sectionalized layout helps humans scan the
catalog. The tool doesn't care.

---

## Failure history (why this doc exists)

Session of 2026-04-17, ticks 29–32:
1. **First collision (tick 29):** sessionC/D drafted P040 + P041 for new
   stratifications. Both collided with Section 5 null-model slots.
   Conductor (sessionA) bumped counter 32 → 60.
2. **Second collision (tick 31):** P060–P063 are Section 7 data-layer.
   sessionD caught it. Counter bumped 64 → 100.
3. **Infra fix (tick 32):** sessionB implemented `_scan_catalog_for_p_ids()`
   + Lua-atomic `max(counter, scan_floor)+1`. No more collisions possible
   via that path.

Lesson: when patching a flat counter, audit the full target space,
not just the local collision point. The self-healing fix removed the
need for conductor decisions entirely.

---

## One-line summary

**Use `reserve_p_id()`. Don't touch the counter. The ranges above are
documentation; the catalog is authority.**
