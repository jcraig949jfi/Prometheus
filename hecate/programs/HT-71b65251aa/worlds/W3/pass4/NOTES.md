# HT-71b65251aa / W3 -- Pass 4 (first falsification), round 1: NOTES

Written BEFORE any Pass 4 run. Prompt: hecate/programs/_prompts/pass4_impl_v1.md
(sha256 77ff9e2d04f990b18d049dcf86bf70e10246b171cb4445cc8b34bebbcecece6e).
Bound by roles/Hecate/prereg/2026-09-30_pass4_round1/PREREG.md (section
"HT-71b65251aa W3") and roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Read: both PREREGs, worlds/W3/ (IMPLEMENTATION_NOTES.md, world.py, evaluate.py,
OUTCOME.json, rows.jsonl head), program.json experiment W3, mechanism M2,
lenses L5, L2. Nothing else.

## World reused

The round-1 world is reused verbatim (lexicon SOME_A, ALL_A, SOME_B, ALL_B;
8 object types; contexts of 3-4 DISTINCT types; target uniform; exact
normalized RSA tables L0..L3; utterance sampled from S2(.|target); answer =
argmax with uniform tie-break, scored as exact expected accuracy; adaptive
listener stops at the first k with max_o L_k(o|u) >= theta, cap 3;
2000 contexts per seed; thetas {0.6, 0.7, 0.8, 0.9}; alpha 1, cost 0,
uniform priors). attack.py re-implements it in the same code shape
(same rng call order per item) so a seed in 0..9 would reproduce round 1.

## R (replication)

- Seeds 100..109 (disjoint from round-1 seeds 0..9); twin rng
  default_rng(10_000 + seed) as in round 1.
- Round-1 success rule applied to the seed-mean statistics at theta 0.6:
  acc(0.6) >= acc(L2) - 0.01 AND mean_depth(0.6) <= 1.4 AND
  Spearman(depth, ambiguity)(0.6) >= 0.4 (NaN fails) AND the theta-0.6
  random-depth twin FAILS the accuracy clause AND no theta's twin meets all
  three clauses (round-1 CONFOUNDED rule, which would pre-empt SIGNAL).
- R.reproduced = that conjunction, plus R's positive and cheat controls
  detected (as in round 1: unique-literal-referent items at depth 0 and
  correct for every theta and seed, >= 1 per seed; cheat = correctness 1,
  depth 0 if ambiguity 1 else 1, detected iff the round-1 success rule
  fires on it).

## ORIG (original-world attack)

- On the R rows (seeds 100..109, original world), seed means:
  fires iff acc(fixed L1) >= acc(adaptive) - 0.005 AND
  mean_depth(fixed L1) (= 1.0) <= mean_depth(adaptive).
- Ambiguity: PREREG does not name theta for "adaptive". Reading chosen:
  theta 0.6, the theta at which round 1 found SIGNAL and at which R is
  stated. All other thetas are reported as diagnostics only.
- ORIG uses the R world's controls (same world variant).

## ALT (alternative implementation: a speaker variant under which depth matters)

"Speaker variant" reading: the RSA speaker definition S_k is changed; since
listener L_k is by definition the normalized inverse of S_k, the listener
hierarchy inherits the change (so fixed-L2 remains the Bayes inverse of the
actual speaker S2). Everything else (lexicon, contexts, target draw,
thetas, adaptive rule, scoring) is unchanged. Both candidates are fixed
here, before any listener runs:

- V1 (tried first): speaker rationality alpha = 4 (S_k(u|o) proportional
  to L_{k-1}(o|u)^4), utterance cost 0, actual speaker = S2 sampled.
  Why: in RSA, alpha = 1 keeps level-k posteriors close to each other
  (round 1: L1 argmax differs from L2 on 0.4% of items); a sharper speaker
  makes higher levels diverge from lower ones, and L2 is the exact Bayes
  inverse of S2, so any L1/L2 divergence should favour L2.
- V2 (only if V1 is NOT_ELIGIBLE; the PREREG's "one other speaker
  variant, once"): alpha = 4 AND utterance cost 1.0 on ALL_A and ALL_B
  (S_k(u|o) proportional to exp(alpha*(log L_{k-1}(o|u) - cost(u))) over
  utterances true of o), actual speaker = S2 sampled. Why: a costly
  strong term makes "some" ambiguous at L1 in a way only deeper
  reasoning about the speaker's cost-weighted choices resolves.
- Seeds for ALT: 100..109 (10 seeds, disjoint from round 1), 2000 contexts.
- Eligibility (checked first, in code, per variant): seed-mean
  acc(fixed L2) - acc(fixed L1) >= 0.02. The switch V1 -> V2 is automatic
  in attack.py by that rule alone; if V2 is also not eligible,
  ALT.status = NOT_ELIGIBLE (twice) -> PARK.
- Pass (on the eligible variant), seed means at theta 0.6 (same reading as
  ORIG; other thetas diagnostics only):
  acc(adaptive) >= acc(fixed L2) - 0.01 AND
  mean_depth(adaptive) <= 0.8 x mean_depth(fixed L2) = 1.6 AND
  Spearman(depth, listener uncertainty) >= 0.5 (NaN fails).
- Ambiguity: "listener uncertainty". Reading chosen: Shannon entropy
  (nats) of the listener's literal posterior L0(.|u) -- the uncertainty the
  listener faces before any recursion, which does not depend on the
  stopping rule (a level-dependent uncertainty would be partly circular
  with the depth it chose). Note this is monotone in ambiguity (log of the
  number of literal candidates), so it equals Spearman(depth, ambiguity);
  diagnostic: Spearman(depth, 1 - max_o L1(o|u)).
- ALT controls (per variant run): positive = unique-literal-referent items
  at depth 0 and correct for every theta and seed (>= 1 per seed);
  cheat = correctness 1, depth 0 if ambiguity 1 else 1, detected iff the
  ALT pass rule (acc, depth <= 1.6, rho >= 0.5 against entropy) fires on it.
- Also recorded per ALT variant: random-depth twin (permuted adaptive
  depths, rng 10_000 + seed) accuracy, as a diagnostic.

## Predicate (code, evaluate.py)

- Controls first: for each arm set (R world; each ALT variant run),
  positive_detected and cheat_detected. If any fails, no treatment
  statistic is computed; predicate PARK (controls fail), one repair
  allowed before any treatment statistic is printed.
- SURVIVES iff R.reproduced AND ALT.status == PASS AND all controls
  detected (ORIG recorded; per PREREG consequences, if ORIG fired the
  original-world claim is FOSSIL regardless).
- Prompt's vocabulary is {SURVIVES, ORIG_FOSSIL_ALT_PASS, PARK}. Mapping:
  ORIG fired AND ALT PASS AND controls -> ORIG_FOSSIL_ALT_PASS (even if R
  also reproduced -- the original-world claim is FOSSIL); R reproduced AND
  ALT PASS AND ORIG not fired -> SURVIVES; anything else (ALT FAIL,
  ALT NOT_ELIGIBLE twice, controls fail, or ALT PASS with R not reproduced
  and ORIG not fired) -> PARK. Reading on the last case: PREREG
  requires R for SURVIVES; with ORIG not fired there is no FOSSIL branch,
  so PARK.

## Compute

Round 1 took 2.7 s CPU for 10 seeds. Pass 4: R (10 seeds) + up to two ALT
variants (10 seeds each) ~ 10 s CPU. Measured with time.process_time and
written to PASS4_OUTCOME.json. Attempts counted in evaluate.py.

## Run record

- Fidelity pre-check (before attack.py, not a Pass 4 attempt): seed 0 of the
  original world via attack.run_seed matched round-1 rows exactly (L1 0.7395,
  L2 0.73975, theta-0.6 mean depth 1.287, depth hist [432, 956, 218, 394]);
  it wrote no file.
- attack.py attempt 1: 8.9 s CPU; V1 was not eligible by the pre-declared
  rule, so V2 ran automatically. evaluate.py run next, controls printed first.
- A __pycache__/ directory was created in pass4/ by the pre-check import.
