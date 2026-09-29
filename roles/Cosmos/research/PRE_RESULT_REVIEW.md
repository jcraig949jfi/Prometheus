# Adversarial pre-result review (directive 2026-09-28 s7)

Currency: 2026-09-28. Applies before ANY expensive or terminal test: every Z3 holdout, and every Z2
transfer that spends a world family. It applies to the C3 freeze first.

## 1. Who reviews
- A seat that is NOT Cosmos and NOT the author of the holdout being spent. Harmonia is excluded when
  it will adjudicate the same test: a reviewer should not grade what it helped shape.
- Two reviewers when the test is terminal: independent, with neither seeing the other's report before
  filing its own. Mixed model families where available (single-seed LLM review is prompt-steerable).
- The reviewer EXECUTES: it runs the fixtures and controls itself. A reviewer that only reads is
  reported as a reading lens, not a review.

## 2. The packet (hashed; its sha256 goes into FREEZES.md as the `review` input)
1 preregistration; 2 implementation (exact commit); 3 fixtures; 4 controls, planted truths and
cheat systems; 5 scoring rules, with the attainable resolution and the chance floor of every gate;
6 frozen visible evidence (Z1 rows and results).
NEVER in the packet: hidden-world outcomes, hidden-world identities, the decryption key.

## 3. Defect classes the reviewer must search, and a concrete probe for each
| # | defect class | probe the reviewer runs | calibration example from Cosmos's own record (C0, public) |
|---|---|---|---|
| 1 | unreachable gate | compute each gate's pass probability under the null and under a perfect predictor; a gate a perfect predictor fails, or a null passes, is defective | G6/G6b lacked a chance floor |
| 2 | threshold leakage | trace every constant back to the rows it was fit on; any constant touched by evaluation rows is leakage | pool-row leak caught before the prereg run |
| 3 | generator fingerprints | train a trivial classifier to identify the generator from the inputs the law sees; high accuracy means the law may be keyed on the generator | (new) |
| 4 | location dependence | offsets per family, not pooled; opposite-signed offsets that cancel in the pool | pooled G7 hid opposite-signed family offsets |
| 5 | coordinate dependence | apply T-C1 physics-preserving re-encodings to the fixtures; count verdict flips | ring's "dead memory is free" coordinate defect (offset tracks N, corr .99) |
| 6 | family imbalance | per-family row counts and per-family metric; a pooled pass carried by one family fails | per-family biases that cancel when pooled |
| 7 | pseudo-replication | count support in independent generators and author lineages (T-G1), not seeds or worlds | C0's D/E/F share one author |
| 8 | hidden tuning freedom | list every choice made after the data was seen (grammar size, folds, seeds, cmap version, tolerance); each must be preregistered or disclosed as an amendment | C1 -> C2 "improvement" was mostly seed |
| 9 | degenerate predictor | score a constant, a majority rule, a 5-NN twin and a size-matched classifier on every gate | G6b's magnitude window passed a constant prescription 10/12 |
| 10 | implementation/prose disagreement | run the code on a hand-built case whose answer follows from the prose; compare | adversary evaluated a v2 law with v1 coordinates |
| 11 | passing without the mechanism | build a cheat system with the law's inputs but not its claimed mechanism; it must fail the test | (C3 planted cheat systems are the model) |

## 4. Verdict format (filed as roles/Cosmos/research/reviews/<freeze id>_<reviewer>.md)
One line per finding: `class | severity (BLOCKING / REPAIR / NOTE) | evidence (command + output) |
proposed repair`. Overall verdict: GO / REPAIR / STOP. "Not worth continuing" (STOP) is a
first-class verdict.

## 5. After the review
- GO: the freeze stands. The freeze's `review` field changes once, from PENDING to the review file's id.
- REPAIR: repair only on visible (Z1) material. Append a NEW freeze with `supersedes` = old id, mark the
  old one SUPERSEDED, then review again. The old freeze stays and still verifies.
- STOP: the holdout is NOT spent. The thread records why, and it goes to the operator.
- A finding that Cosmos disputes is not dismissed by Cosmos. It goes to the operator with both sides.

## 6. Calibrating the reviewer (open, T-I1 adjacent)
A reviewer is an instrument too. Before its first terminal use: give it a reconstructed C0 packet
with the known C0 defects left in (table column 4), and count how many it finds. A reviewer that
misses the planted defects cannot be counted on to find real ones.
