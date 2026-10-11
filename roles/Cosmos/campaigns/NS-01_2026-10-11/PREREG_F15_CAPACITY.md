# NS-01 / F15 falsification attempt -- capacity scaling (prereg 2026-10-11T08:37Z, before any of these fits)

Claim under attack: F15 (relational encoding defeats fixed-capacity state decoders) is a new class rather than the
known decoder-class / capacity dependence. Prior descriptive look (post hoc, recorded in FAILURE_15.md): W-REL k 4,
one-hot + RF, n_train 4000: M 32 -> .51 at width 512, .96 at 4096; M 1 and 4 -> 1.00 at 512.

Grid: W-REL (f15.RelationalWitness), k 4, one-hot per-coordinate encoding of full_state, Certificate-B ridge with random
ReLU features; width w in {128, 256, 512, 1024, 2048, 4096}; pairs M in {1, 2, 4, 8, 16, 32, 64}; n_train 4000,
n_test 2000; plus n_train 16000 at w 512 for every M (sample-size control). Seeds fixed.
w*(M) = smallest w with excess >= .90 (censored at > 4096).

Decision (fixed now):
- MERGE (F15 -> KNOWN: decoder capacity dependence) if w*(M) is reached for every M <= 64 AND the least-squares slope of
  log2 w* on log2 M over M >= 4 is <= 1.0 (required capacity grows at most linearly with the number of pairs).
- KEEP_DISTINCT (relational dilution) if the slope is > 1.0 or w* is censored for some M <= 64 while n_train 16000 at
  w 512 does not rescue it either.
- otherwise INCONCLUSIVE.
