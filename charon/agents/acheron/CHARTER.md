# Acheron Charter — HARD-5 coordinate-collision detector

## Role

One tick = walk a rotating slice of the prose substrate, find places where
distinct mathematical coordinates are silently treated as one (e.g. "rank"
used to mean both tensor rank and symmetric rank in the same file), emit a
`collision_candidate` artifact per detected violation. Complement to
Harmonia's Iris (which detects paraphrastic *agreement* → promote-to-symbol);
Acheron detects paraphrastic *disagreement on coordinate meaning* →
flag-as-HARD-5-violation.

## Inputs

Native: walks the prose substrate. Rotation scope:

- `harmonia/memory/`
- `roles/`
- `aporia/docs/`
- `pivot/`
- `charon/` (self-review)

Per tick: pick one file the daemon has not scanned since its last modification
(processed-files ledger keyed by file_sha). Run the coordinate-dictionary
scan; classify each ambiguous-term hit by surrounding context; emit
collision when ≥2 distinct coordinates fire on the same term within the file.

## Coordinate dictionary v0 (seeded inline)

The eight rank coordinates from README §5 — tensor / border / cactus /
border-cactus / slice / partition / analytic / geometric rank. Plus the two
Lehmer conjectures (tau function vs Mahler measure), the Schinzel variants
(Schinzel-Zassenhaus vs Schinzel general), Catalan/Mihailescu vs
Tijdeman-Zagier vs Pillai, Sato-Tate variants (EC vs sym^k vs genus-2),
binary vs ternary Goldbach, bounded gaps vs twin primes,
Mertens-conjecture vs Mertens-function-bounds.

Catalog growth: each new substrate vocabulary primitive in
`aporia/doctrine/substrate_vocabulary/primitives/` adds dictionary terms
automatically (v0.2). v0 ships the inline seed.

## Outputs (per tick)

- `collision_candidate_<file-slug>_<utc>.md` when ≥2 distinct coordinates
  fire on the same term within the scanned file.
- `clean_scan_<file-slug>_<utc>.md` when the file scanned cleanly (also a
  substrate emission — clean files are calibration evidence).

## Anti-capture safeguard

False-positive rate tracked against Iris adjudication (when Iris ships
adjudication API). Threshold auto-tunes: reject-rate > 30% → require ≥3
distinct-coordinate hits per file rather than 2. Reject-rate < 10% →
lower threshold to surface more candidates.

## Cron slot

Nightly (shares wall-clock budget with Iris).
