# HT-321a8fd8e0 / W1 -- Pass 4 (first falsification) notes, written BEFORE any run

Prompt: hecate/programs/_prompts/pass4_impl_v1.md
(sha256 77ff9e2d04f990b18d049dcf86bf70e10246b171cb4445cc8b34bebbcecece6e).
Bound by roles/Hecate/prereg/2026-09-30_pass4_round1/PREREG.md (section
HT-321a8fd8e0 W1) and roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Read: round-1 W1 directory (IMPLEMENTATION_NOTES.md, world.py, evaluate.py,
OUTCOME.json, rows.jsonl), program.json experiment W1, mechanism M3, lens L4.

## Reuse of round-1 code

The GF(32)/BCH, linear-map, coset-leader decoder, parity, direct-rule and
coalition-search code of ../world.py is COPIED into attack.py (not imported:
importing would write __pycache__ into the round-1 directory, outside
pass4/). The only generalisation: the BCH generator is the lcm of the minimal
polynomials of alpha^1..alpha^(2t) for t = 1, 2, 3, giving BCH(31,26),
BCH(31,21), BCH(31,16); the message length is 31 - deg g. Coalition search is
unchanged: 200 uniform random k-subsets per (seed, k), fresh uniform true
message per coalition, exhaustive 2^k joint reports on the members' own
positions, success iff any report vector decodes to a message != truth.
k = 1..8. Everything else (primitive poly x^5+x^2+1, coset-leader enumeration
order, CONTROL matrix seed 1001, NULL_TWIN matrix seed 2000+seed) is reused.

## Seeds

All three attacks use seeds 100-119 (20 seeds, disjoint from round-1 0-19).
Coalition RNG per row = numpy default_rng([attack_code, arm_code, seed]),
attack_code R=1, ORIG=2, ALT=3; arm codes listed in attack.py. NULL_TWIN
matrix seed = 2000 + seed (so 2100..2119, new matrices). One row per
attack x arm x seed, parameters in every row, flushed per row.

## R (replication)

Arms exactly as round 1: TREATMENT (BCH(31,16), d verified = 7), CONTROL
(fixed random parity, matrix seed 1001), NULL_TWIN (per-seed random parity),
POSITIVE_CONTROL (direct 16-agent rule), CHEAT (injected 0 for k<=3, 200 for
k>=4). "Step at k = 4 reproduces for BCH(31,16)" is read as: the round-1
outcome class, computed by the round-1 rule verbatim on the new seeds, is
SIGNAL. I.e. pooled TREATMENT rate <= 0.02 for every k in 1..3 AND >= 0.5
for every k in 4..8 AND CONTROL k=1 rate >= 0.5 AND NULL_TWIN does not meet
the code clause AND positive (direct k=1 >= 0.99) and cheat (code clause
holds on CHEAT) detected.

## ORIG (is the rule minimum-distance decoding and nothing more?)

Codes: BCH(31,26) (d = 3, t = 1) and BCH(31,21) (d = 5, t = 2), both
nearest-codeword decoded with the same coset-leader method. The actual
minimum distance is verified in code (smallest weight w with a weight-w
pattern of syndrome 0 must equal the designed d; abort otherwise). The BCH
(31,16) d = 7 TREATMENT rows of R are NOT counted as a "further code".
Predicate per code: pooled manipulation fraction (20 seeds x 200 coalitions)
is exactly 0 for every k <= t = floor((d-1)/2) AND > 0 at k = t + 1.
ORIG fires iff this holds for at least two codes with different d (here:
both). If it fires, prior-art label KNOWN_ANALOGUE_FOUND is recorded.
Only these two further codes are run (the PREREG's own example); no other
code is added, so the firing rule is not given extra chances.
Controls in this variant: POSITIVE_CONTROL = direct 16-agent rule run with
this attack's RNG stream (detected iff k=1 rate >= 0.99); CHEAT_d3 / CHEAT_d5
= injected counts 0 for k <= t, 200 for k > t (detected iff the ORIG step
predicate returns true on the injected counts, for each).

## ALT (matched-redundancy majority vote)

AMBIGUITY 1 -- "repetition of each outcome bit over the same number of
agents ... at equal agent count": the code rule has 31 agents and 16 outcome
bits. Reading chosen: the majority rule has exactly 31 agents and 16 outcome
bits; agent i holds a copy of outcome bit (i mod 16), so bits 0..14 have 2
copies (agents i, i+16) and bit 15 has 1 copy. This is the most even
allocation possible at 31 agents; "the same number of agents per bit" cannot
hold exactly because 31 is not a multiple of 16. Honest reports = each
agent reports its bit. Outcome bit b = majority of its copies.
AMBIGUITY 2 -- ties (1-1 on a 2-copy bit): resolved to 0 (fixed default,
declared here). Declared in advance: at 31 agents no allocation gives every
bit >= 3 copies (that needs 48), so a single agent is pivotal for some bit
under ANY allocation / tie rule; the expected majority resistance is 0. This
is counting, not a result, and is recorded as such.
Statistic: largest fully-resistant coalition size K(rule) = largest K in
0..8 such that the pooled manipulation fraction is exactly 0 for every
k <= K (K = 0 if k = 1 already manipulates). Same sampled protocol (seeds
100-119, 200 coalitions per k, exhaustive 2^k reports). Code rule arm =
BCH(31,16) re-run in this attack's RNG stream. PASS iff K(code) > K(majority).
There is no eligibility gate for this ALT in the PREREG, so NOT_ELIGIBLE is
not used.
Auxiliary (recorded, not in the predicate): MAJ_R3_48 = majority with 3
copies per bit on 48 agents, to show the majority implementation CAN resist
(expected K = 1); and an exhaustive sweep of all C(31,k) coalitions for
k = 1..3 on both 31-agent rules (one fresh true message per coalition) as a
check that "fully resistant" is not a sampling artefact.
Controls in this variant: POSITIVE_CONTROL = direct rule (k=1 >= 0.99);
CHEAT_ALT = injected majority-arm counts 0 for k <= 3, 200 for k >= 4;
detected iff the evaluator's K function returns exactly 3 on it (i.e. the
evaluator could have seen a majority rule matching the code, a FAIL).

## Predicate (in code, evaluate.py), in this order

1. Any control in any variant (R, ORIG, ALT) undetected -> PARK
   (reason recorded). One repair allowed before any treatment stat prints.
2. ALT FAIL -> PARK.  (ALT NOT_ELIGIBLE cannot occur here.)
3. R not reproduced -> PARK (AMBIGUITY 3: the PREREG consequence
   "ORIG fires, ALT passes" does not mention R; reading chosen: without a
   replicated round-1 signal nothing survives in any world).
4. ORIG fired -> ORIG_FOSSIL_ALT_PASS (original-world claim FOSSIL,
   label KNOWN_ANALOGUE_FOUND).
5. Else -> SURVIVES.

## Compute

Expected < 0.5 core-minutes (round 1 took 0.018). Measured with
time.process_time into run_meta.json; attempts in attempts.json.
