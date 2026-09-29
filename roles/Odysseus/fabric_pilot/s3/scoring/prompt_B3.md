You are a blind quality scorer for research reports about the Prometheus research repository. You receive several
reports, each labelled X###. They come from different sources, and you do not know which. Score each report
independently against the rubric below. Do not try to find out where a report came from: do NOT search the
repository for a report's own sentences, title or label. Only verify the evidence its claims cite.

Tools: Read, Grep and Glob inside the repository, and `rogit` for git history (a single command, used exactly like
git).

Rubric (frozen, S3_PROTOCOL s5). Score each item 0, 1 or 2:
1. EVIDENCE: are the load-bearing claims tied to checkable primary evidence (path:line, commit:path, data)?
   0 = mostly unsupported, 1 = partly, 2 = consistently.
2. CORRECTNESS: pick the 3 highest-stakes claims and verify them in the repository yourself.
   0 = a load-bearing claim is false, 1 = unverifiable or partly true, 2 = all 3 verified true.
   Name the 3 claims and what you found.
3. ANSWERS THE QUESTION: does it answer what it set out to answer, or state precisely why it could not?
   0 = no, 1 = partly, 2 = yes.
4. LIMITS STATED: does it say what was not checked and what would change the conclusion?
   0 = no, 1 = partly, 2 = yes.
5. USABLE: could a research principal act on it without redoing the work?
   0 = no, 1 = with significant rework, 2 = yes.

Write `scores.json` in your output directory:
{"<label>": {"evidence": n, "correctness": n, "answers": n, "limits": n, "usable": n, "total": n,
             "checked_claims": ["claim -> verified/false/unverifiable, with path:line"], "notes": "one or two sentences"},
 ...}
Finish with one line per report: `<label>: <total>/10`.


---------------- THE REPORTS ----------------


======== REPORT X005 ========

# [redacted] -- [redacted] expressivity ceiling; arbitration hash as hidden economics

[redacted]
`5266ccebea3ad5522b7cfa7a07a8718cac113a70` (below: `@5266cce`). No code was
run. All line numbers are at `@5266cce` unless marked otherwise.

## 1. Questions

**H-D3-17.** Is AETH-00's SplitMix64 arbitration law neutral enough that
its stated non-neutrality caveat does not become a hidden "economic law"
(an unmodelled selective force) now that AETH-01 attaches energy stakes
to contests? The source packet calls this a "required pre-campaign
check" (`[redacted]/AETH-01/ASTRA_REVIEW_PACKET.md:94-98`).

**H-D3-18.** AETH-01 has no movement primitive, one active opcode and no
conditional. Which added affordance (movement, conditional, sensing), if
any, is the minimal one? Does leaving out literal movement (D-AETH01-07)
lead to an R6 dead end? Astra's counter-warning is that energy
thresholds already provide conditionals, so a familiar ISA should not be
added (`[redacted]/AETH-01/ASTRA_REVIEW_01.md:217`; the harvest cites :215 at
`5e41c1d67`).

## 2. Method

1. I read the frozen arbitration law, its caveat, and the test plan
   (AETHER_SPEC, AETHER_TEST_PLAN, AETH-00A receipt,
   test_statistical_diagnostics.py).
2. I traced the AETH-01 decisions that reuse the law (D-AETH01-08), the
   adversarial items (#6, #16), the Astra M07 critique, and the repair
   ledger. I checked whether the required "AETH-01-scale stratified
   rerun" was ever run by searching evidence, observatory, tests and
   ops/campaigns.
3. I collected the measured contest statistics from the AETH-01/02 runs
   (contest rate, fan-in, winner persistence, energy-contest share).
4. I derived one exact property of the law from its text. Section 4.2
   gives the proof.
5. For H-D3-18, I read the three AETH-03 physics ladders, the fwd content
   control, amendments A1/A2 (E-008), the research-block synthesis, and
   TH-009.
6. The empirical check that is still missing is written as
   `out/analysis.py`. It was not run.

## 3. Evidence

### 3.1 The law and its caveat

- The winner is the greatest unsigned `priority = M(h3 XOR C(source))`.
  `h0=M(seed^K)`, `h1=M(h0^tick)`, `h2=M(h1^C(target))`,
  `h3=M(h2^field)`, and M is the SplitMix64 finalizer, a bijection.
  Payload never enters. `[redacted]/AETHER_SPEC.md:246-270`.
- The spec makes an explicit non-neutrality caveat: the law is
  "deterministic and order-independent", NOT "statistically neutral",
  and neutrality is to be measured. `[redacted]/AETHER_SPEC.md:296-302`.
- The spec itself lists "coordinate-keyed deterministic arbitration" as
  a time/space-dependent forcing field and a designed asymmetry.
  `[redacted]/AETHER_SPEC.md:358-361`.
- AETH-01 reuses the law unchanged, with the field domain widened to
  0..4 (D-AETH01-08). Its hidden prior is that the caveat now carries
  economic stakes. Its falsifier is an AETH-01-scale stratified rerun
  that finds a bias that "consistently determines who wins scarce
  energy". `[redacted]/AETH-01/DECISIONS.md:161-177`.
- Economic stake: a source always pays WRITE_COST and the attempted
  transfer. Only the winner is credited, and the losers' amounts are
  destroyed. `[redacted]/AETH-01/PHYSICS_SPEC_DRAFT.md:118-130`;
  `[redacted]/AETH-01/FIRST_LIGHT_01_2026-09-22.md:302-313`.

### 3.2 What was tested for neutrality

- AETH-00A diagnostic (tests 20/25): 11 direction-combo strata, N=300
  contests per stratum, a fresh random seed and tick per contest, a
  single target (2,2) on a 5x5 torus, and a Bonferroni family alpha of
  0.01. Result: **0 of 28 cells flagged**, stated as "not a neutrality
  proof". `[redacted]/test/test_statistical_diagnostics.py:1-36`;
  `[redacted]/AETH-00A_RECEIPT.md:135-147`.
  - Limits: the power is low. At N=300 with p=1/2 the per-cell detection
    threshold is roughly |bias| of 0.1. Seeds are drawn fresh per
    contest, so the test does not probe the fixed-seed trajectory
    process. It also has no energy field and no wrap-edge targets.
- The AETH-01-scale rerun (ADVERSARIAL #16, D-AETH01-08, M07) is named
  repeatedly as required and "not executed":
  - `[redacted]/AETH-01/ADVERSARIAL_ANALYSIS.md:175-183`
  - `[redacted]/AETH-01/REPAIR_LEDGER_01.md:494-505`
  - `[redacted]/AETH-01/AETH01_REPAIRED_FREEZE_CANDIDATE.md:72-75`
  - `[redacted]/AETH-01/PHYSICS_SPEC_DRAFT.md:214-218`

  A search of `[redacted]/AETH-01/evidence`, `[redacted]/AETH-03/evidence`,
  `[redacted]/observatory`, `[redacted]/test` and `ops/campaigns` for
  arbitration-bias / win-rate / neutrality found only the AETH-00A file.
  **The required pre-campaign check was never performed.** This confirms
  the harvest's "later evidence: none found".

### 3.3 Measured contest facts in AETH-01 (B-balanced v1)

- Contests are rare: 1.65-1.80% of targeted template fields and **0.56%
  of energy targets** have 2 or more contenders.
  `[redacted]/AETH-01/AETH02_CALIBRATION_2026-09-23.md:108-114, 130-139`.
- Contests are almost all two-way. Fan-in is 0 or 1 at 98.4% of (site,
  field) slots, 2 at 1.6%, 3 at about 20 per million, and 4 once in the
  whole run. `[redacted]/AETH-01/NATIVE_CIRCUITRY_01_2026-09-24.md:212-214`.
- Winner persistence equals chance. "Same contested winner (S4) vs 1/k"
  is 0.50 vs 0.50 for v1; the `hys` control reaches 0.97 by
  construction. `[redacted]/AETH-03/PHYSICS_DESIGN_01_2026-09-26.md:415`.
  A fixed-seed fixture shows both winners across 30 ticks.
  `[redacted]/AETH-01/KILL_GATES_01.md:292-296`.
- Slot usage is near uniform (spread 0.22-1.91% of the mean). This
  counts all edges, mostly uncontested, so it is not a contested-win
  statistic. `NATIVE_CIRCUITRY_01_2026-09-24.md:210-212`.
- Persistent edges are never contested (0 of 1,754).
  `NATIVE_CIRCUITRY_01_2026-09-24.md:267-271`.
- Hash keys are state-free and identical in both twins. Which
  contenders are valid is a radius-1 state fact, so arbitration opens no
  hidden causal path. `[redacted]/AETH-03/PROPAGATION_ASSAY_AUDIT.md:38,
  44-51`.
- "Quenched arbitration" (tick removed from the hash) was rejected
  precisely because it would impose a fixed hash landscape.
  `PHYSICS_DESIGN_01_2026-09-26.md:459-463`.
- Operating guidance: do not redesign the hash merely because it is not
  perfectly neutral; first separate a measured defect from a general
  caveat. `[redacted]/AETH-01/ASTRA_REVIEW_01.md:292`.

### 3.4 Expressivity ladders (AETH-03)

Status of each affordance class:

- **Explicit conditional (`cnd`)**: opcode 0x02 writes only if the
  target's low 2 bits match a key.
  - Evidence: the opcode persisted (share about 0.50), but the lattice
    froze further (0.961 vs v1 0.927 frozen). **KILLED K-b.**
    `PHYSICS_DESIGN_01:324-338, 405-433`.
  - In combination, `rcv_cnd` P_sust 0.016 is **ADDITIVE_OR_LESS**.
    `PHYSICS_DESIGN_03:173`.
- **Energy-threshold conditional / internal sensing (`str`)**: direction
  = (arg0 + energy>>6) mod 4.
  - Evidence: alone it is KILLED K-b (0.940 frozen).
  - `rcv_str` passes N1 (0.109) by one origin. Amendment A1 sets
    **UNRESOLVED** (`PHYSICS_DESIGN_03:252-284`). A2/E-008: the horizon
    matters (new generation after tick 2,000 in 6 of 32 origins)
    (`:286-...`).
  - The synthesis calls it "activity re-routes activity", performing the
    conversion that noise performed.
    `RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md:30-37`.
- **Receipt sensing (`rcv`)**: a written site fires once.
  - Evidence: the only single-change propagator (P_sust 0.047, radius
    11). **UNRESOLVED**, and later "retain as calibration" because it
    encodes its own relay. `PHYSICS_DESIGN_02:231-240, 356-368`;
    `SYNTHESIS:19-25`.
- **Accumulation (`add`) with receipt**: `rcv_add` shows NEW_BEHAVIOUR
  via N1 (0.172, every seed). It stores traces of activity; it is not
  content transport. `PHYSICS_DESIGN_03:164-175, 205-213`.
- **Conservative movement (`mov`)**: the winning source's payload is
  cleared, so the byte moves.
  - Evidence: **KILLED** (K1 local, K2 mechanical). 41% of differences
    die. `PHYSICS_DESIGN_02:47-58, 219-221, 341-343`.
- **Non-conservative content forwarding (`fwd`)**: a receipt-activated
  site re-emits the received byte.
  - Evidence: run as a positive control. **E-P1 FAILED** (3.1% preserved
    content at generation 5 or more). 92% of deep differences were
    altered, and a fixture passes 21/21, so the soup plus the XOR
    signature are confounded. `PHYSICS_DESIGN_03:118-135, 183-188,
    218-222`.
- **Literal relocation of the whole (opcode,arg0,arg1,payload) tuple**:
  **never built.** D-AETH01-07 excludes it, and its reversal trigger is
  "the traveling-structure case is UNRESOLVABLE even with full provenance
  and intervention". That was never evaluated, because no heredity
  detector exists. `DECISIONS.md:141-158`; `REQUIREMENTS.md:14, 22`.

Program state: the single-change search is retired. The next gate is the
frozen medium (TH-009: template turnover without noise), described as
"plausibly upstream" of content transport (TH-008).
`RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md:114-135` (row :121); `ops/threads/TH-009.md:7-15`.

## 4. Result

### 4.1 H-D3-17: answer

**Not empirically settled. The required check was never run.** However,
the committed law plus the measured contest statistics bound the concern
tightly for the AETH-01 v1 / B-balanced regime.

### 4.2 An exact property (derived here from AETHER_SPEC.md:246-270; not stated in the repo)

(a) For a fixed (seed, target, field), the map tick -> h3 is a
bijection of uint64. It is a composition of XOR-by-constant and M, each
invertible.

(b) For any bijection M and any two distinct source codes a and b, with
h uniform on {0,1}^64:

    P[M(h^a) > M(h^b)] = 1/2 exactly.

Proof: substitute h' = h^a^b, which is also uniform. That swaps the two
events. They are disjoint (M is injective and a != b) and exhaustive, so
each has probability 1/2.

(a) and (b) together: over the full tick domain, **every fixed two-way
contest pairing is won exactly 50/50, for every seed, target, field and
direction pair.**

Because 99.998% of contests are two-way (sec. 3.3), there is **no
systematic, trait-linked advantage in AETH-01's actual contest ensemble
to first order**. This includes direction, which is heritable through
arg0. The hash cannot act as a consistent selective force in two-way
contests. What remains is:

- **(i) Finite-window quenched fluctuation.** Within a campaign of about
  1e4-1e5 ticks at one seed, a given pair's win share differs from 1/2
  by a deterministic amount. For a good mixer it is binomial-sized
  (about 0.5/sqrt(n)), which acts like drift, not selection. This is
  ADVERSARIAL #6's "hidden forcing field", and its size is unmeasured.
- **(ii) Three- and four-way contests.** These are not covered by the
  symmetry argument, but they are about 20 per million slots.
- **(iii) Correlations.** These include tick-lag, cross-field,
  cross-target and cross-domain with Mu/Rho (M07). Only lag-1 winner
  persistence has a measurement (S4 = 0.50).

The economic effect is further diluted: only 0.56% of energy targets
are contested.

The genuine "economic law" in this area is **not the hash**. It is the
designed, identity-blind loser-pays-and-energy-destroyed rule. That rule
penalises contest participation and is openly specified (the FIRST_LIGHT
I4 energy leak). It is not hidden.

**Verdict:** "hidden economic law" is **unlikely to be material at
AETH-01 v1 stakes, by argument (high confidence for two-way contests over
the full period; moderate for finite windows)**. It is **formally
unverified**. The D-AETH01-08 falsifier remains open, and the "required
pre-campaign check" is outstanding. `out/analysis.py` specifies it.

### 4.3 H-D3-18: answer

The evidence does **not** support adding an explicit conditional/branch
opcode as the minimal affordance.

- `cnd` froze the lattice and was additive-or-less with `rcv`.
- Consistent with Astra's warning, the only conditional-like mechanism
  that contributed anything is an **energy-threshold** one (`str`), and
  only in interaction with `rcv`. Its status is UNRESOLVED, and the
  horizon matters.
- The affordance that produced reach is **receipt sensitivity** (`rcv`:
  being written changes what you do). It propagates timing, not content,
  and partly by definition.
- Its super-additive partners (`add`, `str`) give "history matters"
  effects, not transport.

On movement:

- **Conservative** movement (`mov`) is actively anti-propagating.
- The harvest's "no non-conservative movement primitive has been tried"
  is **partly inaccurate**. `fwd` is non-conservative content forwarding.
  It was run only as a positive control and failed its bar in a rich soup
  (an instrument confound is recorded).
- **Literal whole-tuple relocation has never been built.**
- Whether excluding movement forces an R6 dead end is **undetermined**.
  D-AETH01-07's reversal condition presupposes a heredity/provenance
  detector that does not exist.
- The program's own reading places the binding constraint upstream, in
  the frozen medium (TH-009), not in movement.

Ranking of minimal additions supported by committed evidence:

1. Receipt/activation sensitivity combined with an existing integrator or
   energy steering. These are interactions, not new ISA.
2. Movement: open; the conservative form is counter-indicated.
3. An explicit conditional opcode: counter-indicated.

## 5. Limits

- All ladder results come from one energy regime (B-balanced), 128^2,
  about 4 seeds, horizons of 400-10,000 ticks, and a one-bit-twin
  propagation assay. None of it is a heredity or R6 test. The
  synthesis's "energy / parameter regime: open" row applies.
- The sec. 4.2 result is a proof I derived from the spec text. It is not
  a repository claim. It assumes the implementation matches the spec,
  which is supported by the golden vectors and oracle parity (AETH-00A/B
  receipts). It does not address finite windows.
- The contest-rate and fan-in figures come from single AETH-01/02 runs.
  The arity mix could change in denser regimes or under new laws (e.g.
  `rcv` raises activity). Under such a law, three- and four-way contests
  would matter more.
- The AETH-03 variants `hys` (and any future law) change arbitration.
  The conclusion applies to the unmodified law only.
- Harvest line cites were made at `5e41c1d67`. The counter-warning now
  sits at `ASTRA_REVIEW_01.md:217` (the harvest has :215).

## 6. What would change the conclusion

- **H-D3-17 toward "material hidden law":** `analysis.py`, run at
  `@5266cce`, would have to find any of the following:
  - (A) a Bonferroni-significant directional deviation in fixed-seed
    trajectories, in a stratum that actually occurs (two-way), exceeding
    δ=0.005;
  - (B) a per-pair dispersion index clearly above 1 (a quenched positional
    advantage beyond binomial);
  - (C) significant lag or cross-field winner association;
  - or a campaign regime whose three/four-way share is above about 1%
    together with a detected k-way bias.

  Any one of these would trigger D-AETH01-08's reversal.
- **H-D3-17 toward "closed":** the same script reports no flags, CI
  half-widths below δ, and dispersion consistent with 1.
- **H-D3-18:** Several results would change this answer:
  - a built tuple-relocation law passing the preregistered
    propagation/content gates;
  - a value-provenance detector (the synthesis's named instrument gap)
    re-scoring `fwd`/`mov`;
  - a demonstration that the traveling-structure case is unresolvable
    (which would trigger D-AETH01-07's reversal);
  - a TH-009 result showing turnover without noise.

  If `cnd` were re-tested on a non-frozen medium and became super-additive,
  that would reopen the conditional question.



======== REPORT X017 ========

REPORT -- surprise-driven eviction vs random eviction: noise, recency or capacity?

1. WHAT I SET OUT TO TEST
A bounded low-rank learner (BufferALS: warm-started ALS over a buffer of B exact records) must choose which records to
evict. Two "surprise" rules (keep_worst = keep the highest current |residual|; residual_reservoir = residual-weighted
A-Res reservoir) were reported to lose to random reservoir eviction on a positive-control world where half the cells
carry extra noise. I asked: (a) is that loss a noise-retention effect (does it appear only as the extra noise grows),
(b) is surprise in the regime-switch family really a recency proxy, (c) is capacity or eviction order the bigger lever
in the committed dev rows, and (d) is the "random" control actually relevance-blind.

2. WHAT I DID
Code: [redacted]/ (lm01 arms, families, fixture) exported from origin/main@6ff2b2f8a into work/[redacted]/src and run only there.
- Reproduction: work/[redacted]/dose.py re-implements the fixture's positive control (F2_latent L2, generator lowrank,
  rank 3, B = cells/4 = 432, dev seeds 9330000-9330003, corrupted half = mode-0 index < d0/2, test = never-seen cells of
  the clean half). A subclass of BufferALS ("Tracked") is identical for the declared rules (same RNG consumption) and
  also records each retained record's admission index. It reproduces the committed fixture JSON on main to all digits
  (random -0.126, oracle +0.506, keep_worst -0.182, residual_reservoir +0.023).
- Dose-response: extra-noise SD in {0, 0.3, 1, 3} (same normal draws, scaled), arms random, oracle, keep_worst,
  residual_reservoir, fifo, plus two labelled EXPLORATORY arms: lp (learning progress: key = drop in the record's own
  residual over up to its last 3 refits; new records protected until one refit; arrivals enter with key ~0) and
  keep_best (evict the worst-fitting record). 4 seeds x 4 SD x 7 arms. Then 8 more dev seeds (9330004-9330011) for
  random / keep_worst / residual_reservoir at SD 0 and 3 (12 seeds there). Logged per run: AC, fraction of the buffer
  in the corrupted half, mean retained-record age (fraction of stream).
- Recency probe: F3_switch L2 lowrank, B = c/4, seeds 9330000-003, arms random/fifo/keep_worst/residual_reservoir/lp,
  logging retained ages and the fraction of the buffer from the final (scored) episode.
- Re-analysis (step1.py): all OK rows of [redacted]/lm01/dev/margins and dev/margins_f5real on main; self-signal minus
  random AC at equal B per family x B and per rule, bootstrap 95% CI of the median over worlds; dual B'/B ratio;
  |order| vs |doubling B| at c/4.
Commands: python3 dose.py f2|f3 <seeds> [<sds>] <arms> <out.jsonl> (2 workers, 1 BLAS thread); python3 reduce.py;
python3 step1.py. Outputs: work/[redacted]/out/{repro,dose,extra,f3}.jsonl, dose_table.txt, dose_summary.json, step1.json.
Seeds used: 9330000-9330011 (dev range, fixture block) and the committed margins rows; no campaign/sealed seeds.

3. RESULT
(a) The stated anomaly is stale. At the commit it was harvested from (6a48ff937) residual_reservoir scored -0.457 vs
random -0.335. The later ALS convergence-rule change re-ran the fixture; on current main the committed fixture says
residual_reservoir +0.023 BEATS random -0.126, and only keep_worst (-0.182) is below. The freeze-review text still says
"both rules lose to random" and quotes the old +0.91 oracle gap (current: +0.63). Also, the fixture compares medians of
arms over 4 seeds; paired per seed at SD 3 both rules beat random in 3/4 seeds.
Dose-response, paired (arm minus random) AC, median [bootstrap 95% CI], seeds won; buffer fraction in corrupted half:
  residual_reservoir  SD 0: +0.35 [+0.13,+0.58] 10/12, corrupt 0.51 | SD 0.3: +0.38 4/4, 0.60 | SD 1: +0.25 3/4, 0.69
                      SD 3: -0.16 [-0.43,+0.08] 5/12, corrupt 0.79
  keep_worst          SD 0: -0.22 [-0.27,+0.10] 4/12, corrupt 0.51 | SD 0.3: -0.23 0/4, 0.95 | SD 1: -0.02 2/4, 0.97
                      SD 3: +0.07 [-0.33,+0.18] 8/12, corrupt 0.99
  oracle              SD 0: -0.06 1/4 | 0.3: +0.12 4/4 | 1: +0.41 4/4 | 3: +0.66 4/4
  random median AC    SD 0 +0.59 (12 seeds), 0.3 +0.35, 1 -0.03, 3 -0.19 (12 seeds)
  fifo +0.01/+0.13/+0.24/+0.03; lp -0.16/+0.18/-0.16/+0.14; keep_best -0.53/-0.38/+0.07/+0.15 (4 seeds each).
Reading: residual_reservoir shows the predicted noise-retention pattern: a clear win at SD 0 that shrinks and crosses
below random at SD 3 while its corrupted-half share climbs 0.51 -> 0.79 (CI at SD 3 still spans 0). keep_worst is NOT a
noise-dose story: it is already at or below random with no corruption (SD 0, a younger buffer: age 0.41 vs 0.50),
fills its buffer 95-99% with corrupted records from SD 0.3 on, yet is not worse than random at SD 1-3, because at
SD >= 1 random itself is below AC 0 (worse than predicting zero): a floor effect, not a ranking signal. Only the oracle
is well above floor at SD 3. The lp arm as implemented degenerated into a near-FIFO (retained age 0.045 vs FIFO 0.034;
corrupt share 0.60 at SD 3), so it is not evidence for a learning-progress repair.
(b) F3 switch (B = c/4, 4 seeds): AC random -0.36, fifo +0.84, lp +0.76, keep_worst +0.16, residual_reservoir -0.47.
Final-episode share of the buffer: random 0.33 (= its share of the stream), keep_worst 0.50, fifo/lp 1.00; mean age
random 0.50, keep_worst 0.38. keep_worst's F3 win over random is consistent with a partial recency proxy, and a plain
FIFO beats it by ~0.7 AC; residual_reservoir (not the frozen F3 choice) loses to random there.
(c) Committed dev rows (1,056 OK; reproduces the [redacted]'s numbers): self-signal minus random at c/4 +0.074
[+0.055,+0.098], 63% > 0; F2 +0.37 [+0.32,+0.44] (all residual_reservoir); F3 +0.30 [+0.28,+0.32] 97% (all keep_worst);
F4 -0.054 [-0.068,-0.040]; F5 (old scale) keep_worst -0.32 [-0.37,-0.21] 17% > 0 while residual_reservoir +0.04; F5
real-cells rows: residual_reservoir +0.30 at c/4, keep_worst -0.04 (and -0.32 at c). Where the self-signal loses it
is mostly keep_worst. At c/4 median |order effect| 0.167 vs |doubling B| 0.160, order larger in 49% of rows (real-cell
F5: 0.26 vs 0.44, 35%). Dual B'/B at c/4 median 1.19 (F2 1.80, F3 1.57, F4 0.86).
(d) "random" here is Algorithm-R reservoir sampling: content-blind and age-neutral (mean retained age exactly 0.50,
per-segment shares equal stream shares), i.e. distribution matching. It is relevance-blind only when the test
distribution equals the stream distribution; in F3 (test = last episode) it is systematically mis-weighted, and FIFO is
the relevant relevance-free recency control.

4. DID IT RESOLVE THE QUESTION
Partly. Resolved: the harvested anomaly as quoted is stale on current code; the two surprise rules must be separated
(residual_reservoir: noise-retention crossing, consistent with the literature; keep_worst: loses without any
corruption and acts as a partial recency buffer); the SD >= 1 fixture regime is at the performance floor for all
non-oracle arms, so it cannot rank eviction rules; capacity and order are comparable levers at c/4 in the dev rows;
random is distribution matching. Not resolved: 4-12 seeds on one generator give wide CIs (residual_reservoir at SD 3
spans 0); the learning-progress key tested here collapsed to recency, so whether a proper learning-progress or
noise-floor key repairs residual_reservoir at high noise remains open; F4/F5 losses were not probed with new runs.

5. CONSEQUENCES
- Documentation/harness defect ([redacted] / LM01 prereg owners): the freeze-review note ("both self-signal rules lose to
  random", oracle gap +.91) describes the pre-convergence-fix fixture; the current committed fixture says otherwise.
  The fixture also compares per-arm medians over 4 seeds instead of paired differences; and at SD 3 (B = c/4) every
  non-oracle arm is below AC 0, so the fixture validates the oracle but says little about the self-signal rules. A
  lower-noise level (SD 0.3) separates the rules cleanly.
- False premise, partial: "surprise retains noise" is true for residual_reservoir (a clean, modest dose-response), but
  keep_worst's weakness is not noise retention; it is present with homoscedastic noise.
- F3: keep_worst's win over random is partly recency; FIFO dominates. Any F3 claim of "relevance selection" by
  surprise should be read against FIFO, which v0.3.2 already added as a reference arm -- this confirms that choice.
- Controls: calling reservoir-random "relevance-blind" is fine for content, but it is distribution matching; in
  non-stationary worlds it is not a neutral baseline. Programs using it as the blind control (SI, Ergon) should say so.
- "Order is second-order to capacity" does not hold at c/4 in these rows; an Ergon-style null on another consumer should
  not be generalised.
- Designers of learning-progress keys: a naive "residual drop" key with neutral admission becomes a recency buffer;
  it needs an admission test or a noise-floor term to be a genuine alternative.
Who should know: [redacted] (LM01 fixture/review text), whoever owns the engine-wide forgetting-rule primitive, SI and
Ergon control-labelling owners.

6. COST
About 1.5 hours of my time. CPU about 2,430 s (~41 CPU-minutes) of BufferALS fits (216 fits, 2 workers, 1 BLAS thread
each) plus a few seconds of re-analysis; RAM well under 1 GB. Not done: more generators/seeds for the dose curve, a
proper learning-progress/noise-floor key, F4/F5 new runs, retained-age logging across the full F3 dev set, and
committing step 1 (read-only clone).



======== REPORT X020 ========

# REPORT -- Is the engine ecology still a selection monoculture?

## 1. WHAT I SET OUT TO TEST

A June 2026 audit of the program found two problems with one shared root. Its
mechanisms looked diverse (NSGA-III, binary gates, tier ladders, bandits,
kernel claims), but all of them served one principle: "promote what passes the
gate". The gate at the center also trusted callers. The kernel's PROMOTE step
checked only that a non-BLOCK verdict object existed. An adapter built a CLEAR
verdict from a caller-supplied survival_evidence dict and never re-ran the
tests. Since the September reset, the program has about ten engines and
engine-like seats. A later landscape survey called their shared discipline
(preregistration, freeze, gate, cheat control) "healthy convergence", but
nobody re-audited their selection principles.

I asked three things of the current engines:
- (a) Does the trust-boundary defect recur? That is, does any gate turn a
  caller-asserted outcome into a verdict without recomputing it?
- (b) Is the inner selection rule the same everywhere (an exogenous "pass a
  test to reproduce")?
- (c) Is the program-level objective still "promote what passes the gate", or
  are the shared prereg/gate/control steps now a verification layer that sits
  under different objectives?

## 2. WHAT I DID

This was a read-only code and document audit. I ran no experiments and wrote
no code beyond git/grep one-liners.

Sources:
- Repository: [redacted] at origin/main 6ff2b2f8a, plus
  these branches:
  - origin/[redacted]/multiday-campaign-2026-09-26 @ ee7a7d954
  - origin/[redacted]/arc3-2026-09-28 @ 7587a93e1
  - origin/[redacted]/attribution-arc-2026-09-28 @ 05ab73917
  - the [redacted] branches, which are ancestors of main
- Baselines:
  - roles/[redacted]/AUDIT_20260622_program_stall_map_of_disagreement.md @ 3e13f736c
  - roles/[redacted]/ENGINE_LANDSCAPE_2026-09-25.md @ 95fff9111

Engines surveyed (10): SFE, NPE (primordial/ and roles/[redacted]/campaigns), BEE
(prometheus/toolbox, prometheus/z80atlas, the multiday campaign), AGE ([redacted]/),
CWE (prometheus/[redacted]), WTP ([redacted]/), PTE (prometheus/[redacted]), [redacted]
(roles/[redacted]/engine plus arc3), [redacted] ([redacted]/*), and the [redacted]
expedition code (roles/[redacted]). [redacted] has docs only, so I only noted it.

The same four-question rubric was applied to every engine:
1. The inner selection rule.
2. Where verdicts are computed, and whether they are recomputed from rows,
   replayed, or trusted as labels.
3. The form of the outputs.
4. The program-level objective.

Three read-only sub-surveys did the first pass. I re-checked every load-bearing
defect claim myself against source:
- primordial/core/contract.py board_eligible
- primordial/bus/bus.py receipt()
- primordial/score/progress.py
- SerendipityFoundry/SerendipityFoundryEngine/sfe/runtime.py record_observation (~2361-2450)
- the multiday-campaign md_analysis.py "holds" vs "instrument_ok"
- [redacted]/wtp/campaign.py replay_ok
- roles/[redacted]/engine/a16.py:490
- prometheus/[redacted]/campaign.py:560-572
- atlas/policy.py

Legacy check:
- git log on sigma_kernel/sigma_kernel.py and
  prometheus_math/discovery_promotion.py.
- git grep for importers of either file inside the post-reset engine
  directories.

Vocabulary proxy: I counted commit subjects on all branches, by period, that
contain "promot" or null/kill/falsif/sham/cheat/control.

## 3. RESULT

### (a) Trust boundary

Legacy gate:
- The June defect was never fixed. SigmaKernel.PROMOTE (sigma_kernel.py:822)
  still checks only that a verdict exists and is not BLOCK.
  discovery_promotion.py still turns caller-asserted survival_evidence into a
  CLEAR verdict. Both were last touched 2026-05-08.
- It is dormant. None of the 10 post-reset engines imports either module. The
  only hits in engine directories are two markdown mentions.

Post-reset engines: 8 of 10 compute their scientific verdicts from per-run rows
or re-runs:
- CWE: the broker re-runs sealed holdout worlds in a subprocess before
  scoring.
- [redacted]: an independent worker re-ran the whole battery and matched the
  fixture value by value.
- BEE: a 3% exact-equality replay.
- [redacted]: the forensic replay has to reproduce the recorded run exactly
  before the run is admitted.
- [redacted] z80atlas: REPLAY_MATCH is required.
- AGE: digest and spot-check replay tools.
- WTP and PTE: fresh-seed re-runs and held-out re-tests.
- [redacted]: the tribunal re-scores on fresh tasks.

Two engines keep a caller-trust path:
- SFE record_observation. The caller supplies FALSIFIED/SURVIVED and only the
  spelling is checked. A work_id proves that a completed work item exists, not
  that it supports the outcome. Without a work_id the outcome is stored as
  CLIENT_ASSERTED and still moves the hypothesis state. This is a stated
  design choice ("the engine stores the conclusion the experimenter reached").
  The evidence class is always recorded, and fail-closed enforcement is
  opt-in (require_attestation). So the audit's defect is present by design,
  labelled, and closable with one flag.
- NPE board_eligible (contract.py). It accepts a self-written PASS/KILL
  status, any non-empty controls.cheat string (the string is not checked to
  say the control passed), and any non-empty rows path (the path is not
  checked to exist). Board credit from it has been off since round 2
  (PM_BOARD_SCORING). Refutation credit in score/progress.py still uses it,
  but its instruments axis does read the row files.

Softer stage-to-stage label trust (a later stage trusts an earlier stage's
stored label or boolean; the verdict is never minted from a caller):
- [redacted]: run_s3s4.py reads stored PASS gate files, and a16.py:490
  hardcodes donor_adjudication_valid = True.
- [redacted]: a PREREG attribution_tests.passed boolean and a preflight
  verdict == "PASS".
- [redacted]: gate_v01.json PASS.
- AGE: GPU parity rests on the pod's self-reported PASS, though independent
  replay tools exist.
- BEE:
  - md_analysis.py sets "holds" without conditioning on instrument_ok; the two
    are printed side by side.
  - The scheduler re-uses a stored score on resume.
- WTP: replay_ok is computed and recorded but never enters the REPLICATED
  state.

### (b) Inner selection rule (10 engines)

Exogenous test-passing ("pass a test to reproduce"):
- PTE: truncation GA.
- [redacted]: gold-match search and a lower95 > 0 gate.
- [redacted] sandbox: hidden-target reward and colony truncation.

Mixed:
- NPE: QD elites alongside endogenous Z80 ALLOC/BIRTH.
- BEE: endogenous copying, but the copy resource is paid for correct task
  answers in the coupling physics.
- WTP: elite GA with about 20% novelty; WTP-03 parents are the worlds that
  passed admission gates.
- [redacted]: endogenous copying, an optional competence-gated pressure, and an
  outer "world promotion score" in rie.

Endogenous only:
- AGE: no score; a GA loop is explicitly rejected.

No selection:
- SFE: an instrument (its reference driver is a onemax (mu+lambda)).
- CWE: parameter worlds; the selection is over laws, by attack/survive/freeze.

So 3 of 10 are pure exogenous gates, and 7 of 10 contain a
test-passing-selection component. Mechanism diversity is real, but it leans
toward test-passing selection. Only AGE (and [redacted]'s census and envgate
lines) keep selection fully endogenous.

### (c) Program-level objective

- The central scorer has changed. atlas/policy.py (policy/2) states: "The
  learning target is NOT 'which experiments succeed'." Its weights have no
  term that rewards success, and it lets a confound-removing clean null
  outrank a novel demo.
- Promotion language has dropped out of commit subjects:
  - Apr-Jun: 133 of 2848 subjects contain "promot" (4.7%).
  - Jul-Aug: 3 of 1175.
  - Sep 10-30: 17 of 4796 (0.35%). Most of these are allocation or schema
    promotions, not claim promotions.
- Null/kill/control language roughly doubled in rate: 9.2% (Apr-Jun) against
  11.0% (Sep).
- Several engines have descriptive first-class products: the AGE observatory
  deliberately applies no labels; there are the [redacted] copier census, the
  [redacted] census and label-vs-capability audit, the WTP phase and niche maps,
  and the BEE "descriptive, not tested" block.
- One structural residue remains, which I call a "gate-then-describe" funnel.
  - PTE maps phase boundaries only around specimens that first pass SIGNAL
    (campaign.py:562-572).
  - CWE's product is a law that survived attack.
  - WTP-03 breeds from worlds that passed admission gates.

  In these engines, description is conditioned on a gate pass, so what gets
  described is still filtered by what passed.

### Plain conclusion

The June monoculture does not recur in its load-bearing form.
- Every post-reset scientific verdict path I checked is either recomputed from
  rows or replayed, or is explicitly labelled as client-asserted (SFE).
- The program-level objective is no longer "promote what passes".

What converged is the verification discipline, not the selection principle.
Treating those two as the same thing is the weak part of the question.

Three genuine residues remain:
1. The legacy gate defect is unfixed, though dormant.
2. There are two caller-trust paths (SFE by design and opt-in; NPE's
   board_eligible) and about six label-trust seams between stages.
3. Inner selection and descriptive scope still lean toward exogenous
   test-passing. Seven of ten engines have such a component, and three engines
   describe only what first passed a gate.

## 4. DID IT RESOLVE THE QUESTION

Partly.
- It resolves the trust-boundary half: the defect is identified per engine
  and verified in source.
- It gives a defensible classification of inner selection and of the
  program-level objective.

It does not resolve whether the shared discipline itself narrows what the
ecology can discover. That is an empirical question and a code read cannot
answer it. It would need, for example, the share of Atlas proposals or results
that exist only because a gate passed, against ungated exploratory output, or
a comparison of discovery yield between the gated and ungated lines. The
engine-level classification also rests on a medium-depth read of about ten
codebases, not a line-by-line audit. Unread parts include the SFE client,
NPE's soup/ worlds, [redacted]/lm01/launch_gate.py and
prometheus/[redacted]/launch.py.

## 5. CONSEQUENCES

Harness and instrument defects (small, concrete):
1. The legacy kernel PROMOTE and the discovery_promotion adapter still trust
   caller-asserted survival. The June recommendation (a re-execute-battery
   gate) was never applied. Either retire them or fix them before anything
   post-reset imports them. Owner: whoever owns sigma_kernel /
   prometheus_math ([redacted] raised it).
2. In NPE board_eligible, the cheat check is "any non-empty string" and the
   rows check is "any non-empty path". It should require that the cheat
   control passed and that the rows file exists and backs the status. It
   still feeds refutation credit. Owner: [redacted].
3. SFE should default to require_attestation=true for science worlds, or
   state in each world's charter why CLIENT_ASSERTED is acceptable. Owner:
   Daedalus.
4. BEE md_analysis should set holds = holds AND instrument_ok. WTP should let
   replay_ok gate REPLICATED. [redacted] a16.py:490 should compute
   donor_adjudication_valid instead of hardcoding True. All three are
   one-line fixes. Owners: [redacted], [redacted], [redacted].

False premise, or at least a conflation: "monoculture at the level of
discipline" mixes epistemic verification (which should be uniform) with
selection principle and objective (where diversity matters). The earlier
landscape verdict of "healthy convergence in discipline" is consistent with
what I found. But no re-audit had been done, and one was warranted: the
residues above are real.

Something seats could change: the remaining monoculture risk is at the
"gate-then-describe" funnel (PTE, CWE, WTP-03) and in the inner selection rules
(7 of 10 engines have a test-passing component). Atlas could track, per engine,
the share of described territory that was reached without passing a gate, which
would make this measurable. The operator (convergence concern of 2026-09-25)
and Atlas should know.

No new positive result and no reproduction of a known number. This is a
re-audit that mostly clears the post-reset ecology of the June finding and
leaves a short list of residues.

## 6. COST

About 1 hour of wall time, including three parallel read-only code surveys
and my own verification of each cited defect line. CPU: negligible (git and
grep only; well under 1 CPU-minute). Nothing was executed from the repository
and no database was queried.

Not done:
- the empirical measurement of gated vs ungated discovery share
- a deep read of the SFE client, NPE soup/ worlds and the launch gates
- [redacted] adjudication, which exists only as prose



======== REPORT X001 ========

REPORT -- one memory certificate applied to another engine's specimen

1. WHAT I SET OUT TO TEST

The program has three instruments that each claim to certify "history is kept and causally used". They are [redacted]'s public P1/P2 certificate, [redacted]'s LM01 and [redacted]'s SI01. I asked two things. First, do they return compatible verdicts on the same specimen? Second, which committed specimens could all three be run on? Only one of the three can actually be run today, so I did the cheapest discriminating part. I applied the [redacted] P1/P2 v3 certificate, unchanged, to [redacted]'s evolved M2 specimen. M2 is a HOLD memory which [redacted]'s own tests place "in packets in flight, not in site state". I ran it under two declared system boundaries: B1 declares site state + inbox + in-flight packets, and B2 declares site state only. The question was whether the certificate agrees with [redacted]'s own tests, and whether the verdict is set by the boundary the adapter author declares.

2. WHAT I DID

Code and data were exported with git archive into [redacted] Nothing was run against the clone.
- [redacted] certificate: prometheus/[redacted]/c3/{certify,system,task,probe,calib}.py @940b486f2, unchanged. Rule v3: 49 permutations, p <= 0.02, P2 = 3 bootstrap SE, 2000 training and 3000 test episodes.
- [redacted] engine: prometheus/[redacted]/*.py @cc98596dd. This is identical to main except for lens.py.
- The M2 specimen is cell 4ab2ba014aac967e. Its champion genome, physics and environment come from roles/[redacted]/pte/c1_rows/cells.jsonl.gz @b91f522ae.
- The physics is a ring of 144 sites with synchronous wake every 2 ticks, and the in-flight mailbox ring has length 8. The environment is HOLD with cue_len 2 and gap 8.
- New code, all in [redacted]
  - adapter.py: a [redacted] System around the [redacted] engine.
  - run_cert.py: the certification driver.
  - ka_check.py and ka_adapter.py: known-answer checks.

How the adapter maps a [redacted] episode (V=2, k=8) onto one HOLD trial run from a fresh world:
- The cue takes 2 engine ticks at +/-256 on the actuator site.
- Each distractor takes 1 tick at +/-64.
- The query takes 1 silent tick, which is the HOLD readout tick.
- The readout features are a one-hot of sign(S0) at the actuator, which is [redacted]'s own readout.
- The engine's counter-based RNG gets a fresh world seed per step from the harness's noise(), so the two rows of a P2 pair share every random draw.
- The C3 harness swaps every array in the state dict at t=k. Carriers outside the declared boundary are therefore kept outside the dict: they are neither swapped nor probed.
- full_state is the declared arrays, with sites re-indexed relative to the actuator (the ring is translation-symmetric). Columns that are constant within a batch are dropped, which loses nothing for a linear probe.
- "phase" is the engine tick parity at which the episode starts. Phase 0 reproduces trial 0 of [redacted]'s episodes.

Runs:
- ka_check.py: [redacted]'s own evaluate() on the 64 held worlds for the normal, flush_inflight, flush_inflight_late, reset_S, reset_all_nonpacket and zero_comm arms.
- ka_adapter.py: the same arms re-created through the adapter (flush after step 5 = mid-delay, flush after step 8 = the tick before readout, zero_comm), at phases 0 and 1, 2000 episodes each.
- run_cert.py PV|NZ seeds 6-10: the [redacted] planted sanity systems on the same V=2, k=8 task.
- run_cert.py B1 seeds 6,7,8 (phase 0) and B2 seeds 6-10 (phase 0).
- run_cert.py B2 seeds 6,7 at phase 1.
- Outputs are in out/*.json and out/log_*.txt.

3. RESULT

Known answers:
- [redacted]'s own run reproduces the committed held accuracy exactly: 0.8828. flush_inflight gives 0.497, zero_comm 0.500, reset_S 0.883 (unchanged), reset_all_nonpacket 0.863, and flush_inflight_late 0.845.
- Accuracy per trial alternates with the tick parity at which the trial starts: about 0.72-0.84 on even starts and 0.92-1.0 on odd starts. The trial period is 13 ticks and sites wake every 2 ticks.
- Through the adapter:
  - Phase 0: normal J = 0.736 (matches trial 0 = 0.72), flush mid-delay 0.50, flush just before readout 0.68, zero_comm 0.50.
  - Phase 1: normal 0.959, flush mid-delay 0.51, flush just before readout 0.959 (no effect), zero_comm 0.50.
- The adapter therefore reproduces [redacted]'s known answers.

Certificate, unchanged v3 rule:

| System | Seeds | Class | P1 D (bits) | P1 p | P2 effect (+/- SE) | Notes |
|---|---|---|---|---|---|---|
| M2, B1, phase 0 | 6, 7, 8 | FUNCTIONAL 3/3 | 0.80-0.81 | 0.02 | 0.45-0.47 +/- 0.009 | J 0.73 -> 0.27 |
| M2, B2, phase 0 | 6-10 | PASSIVE 5/5 | 0.83-0.85 | 0.02 | exactly 0.0000 | J_ablated = J_intact |
| M2, B2, phase 1 | 6, 7 | FUNCTIONAL 2/2 | 0.98 | 0.02 | 0.92 +/- 0.005 | |
| PV | 6-10 | PASSIVE 5/5 | | | | sanity as expected |
| NZ | 6-10 | 3 FUNCTIONAL, 1 INDETERMINATE (p=0.04), 1 INCOHERENT (p=0.30) | | | about 0.04 in all 5 | P1 gets weak at k=8 |

Plain conclusion:
- On this specimen the [redacted] certificate agrees with [redacted]'s tests once the boundary is declared. B1 is FUNCTIONAL and B2 is PASSIVE at phase 0, which is the pre-stated "agree" outcome. No INCOHERENT result occurred on M2: the linear P1 probe decodes the cue from the declared state.
- Two qualifications change how that should be read.
  - (a) The verdict is set not only by the declared boundary but also by the moment of the swap relative to the engine's wake cycle. With B2 fixed, starting the episode one tick later flips the verdict from PASSIVE to FUNCTIONAL. At phase 1 the cue has been written back into site state by the tick before readout, which is consistent with [redacted]'s own flush_inflight_late being harmless there. So "the memory is in packets, not site state" is true at mid-delay but not at every tick. The certificate's fixed swap time t=k samples only one tick.
  - (b) P1 held under both boundaries, including B2 where the cue's carrier is excluded. P1 probes at t=k+1, after the readout tick, so the state that holds the system's answer already contains the cue. On this task P1 does not locate where the memory is carried; only P2 discriminates.
- The second part of the question (which committed specimens all three instruments could be applied to) has the answer "none today". LM01 is frozen but not launched, and its world is tensor completion with no cue-delay-query episode. SI01 has a directive but no prereg and no code. Only the [redacted] certificate exists as runnable code, so no three-way comparison is possible.

4. DID IT RESOLVE THE QUESTION

Partly.
- The cheapest discriminator is resolved for the [redacted]-on-[redacted] pair. The dependence on the boundary was confirmed, and a second hidden degree of freedom was found (the wake phase at the swap time).
- The three-way compatibility question cannot be resolved with committed inputs: two of the three instruments have no runnable implementation.
- B1 was run on 3 of the 5 planned seeds because of the CPU budget. All 3 agree, with P2 z around 50, so the missing seeds are very unlikely to change the class.

5. CONSEQUENCES

- Positive result / reproduction: the adapter reproduces [redacted]'s known answers, and the certificate agrees with them under a declared boundary. The adapter ([redacted]) is a reusable tool for putting [redacted] specimens under the [redacted] certificate.
- Instrument caveat (for [redacted], and for anyone proposing this as the common ruler):
  - A verdict must name the boundary AND the swap tick, since the carrier can move between packets and site state within a trial.
  - A single fixed swap at t=k is not enough for engines with periodic update. Sweeping the swap over the delay would be the natural amendment.
  - P1 at t=k+1 cannot localize memory, because any system that answers correctly meets it trivially.
- Calibration note (for [redacted]): the v3 gate was passed at V=4, k=6. At the V=2, k=8 shape needed here, the weak planted system NZ is not 5/5 FUNCTIONAL (3/5; one INCOHERENT from a P1 miss). The gate's guarantees do not carry over to other task shapes without being re-run there.
- For [redacted]: the statement "memory in packets in flight, not site state" should be qualified. It holds at mid-delay, but at the tick before readout on odd-phase trials the cue is already in site state.
- For the thread steward: LM01 and SI01 need runnable code and a cue-query episode before any cross-instrument comparison. Adding an E class to [redacted] was not attempted.
- Governance: I ran this as a neutral worker using only the public certificate code and the committed specimen row. I did not contact [redacted] or [redacted] (the channel is frozen), so they should be told.

6. COST

- About 2 hours of my own time.
- About 47 CPU-minutes (roughly 2,800 CPU-seconds), single-threaded, at most one heavy process at a time, peak about 1.6 GB RSS.
- Not done:
  - B1 seeds 9 and 10.
  - B1 at phase 1.
  - A packets-only boundary (B3; implemented in the adapter but not run).
  - A sweep of the swap tick.
  - Any LM01 or SI01 application, since there is nothing runnable.



======== REPORT X016 ========

# [redacted] [redacted] — Assay blind spots, and an observer that may smuggle in a heredity ontology

[redacted]
repository at `5266ccebea3ad5522b7cfa7a07a8718cac113a70`. All citations
are `path:line` at that commit unless a commit is named. No code was run.

## 1. Question

The [redacted] bundles three harvest entries:

- **H-D3-14.** [redacted]'s AETH-02 negatives say its assays "cannot see" five
  classes of structure: spatially distributed, informational, uncontested,
  stateful-but-not-self-repairing, and dynamically reconfigurable. What
  assay could see them? And is [redacted]'s "no circuitry" reading an
  instrument limit?
- **H-D3-15.** Does the observer bring in a template-copy / Mu / parent-preserving heredity
  ontology (Astra, `[redacted]/AETH-01/ASTRA_REVIEW_01.md:209`)? How much of
  what the observatory reports comes from its vocabulary rather than from the physics?
- **H-D3-16.** How can recursive construction, mutual constructors and
  partial copying completed by the environment be turned into testable
  predicates?

Answered question: **In the committed record, how far are [redacted]'s reported
results and negatives set by the observer's ontology and assay coverage,
and how far are they findings about the physics? What has been done to
separate the two?**

## 2. Method

1. I read the source passages and everything that responds to them: the
   Astra review, the repair ledger, the terminology-refactor receipt, the
   repaired claim ladder, the observatory specification, the AETH-02
   native-circuitry and closing reports, the AETH-03 propagation-assay
   audit, Physics Design 03, the research-block synthesis and the engine card.
2. I read the code that implements the observer: `aeth01_graph.py`,
   `aeth01_observatory.py`, `aeth03_assay_audit.py` and the claim-ladder
   fixtures in `scientific_aeth01.py`.
3. I separated three layers:
   - (a) vocabulary: names only;
   - (b) inference contract: which evidence the claim ladder accepts;
   - (c) instrument logic: what the running assays can register.
4. For each layer I asked whether the heredity/template-copy assumption
   comes from the observer or from the `aeth01.v1` transition law.
5. I searched the repo for anything that designs or runs assays for the
   five blind-spot classes or for mutual constructors.
6. A decisive computation that I could not run is specified in `analysis.py`.

## 3. Evidence

### 3.1 The blind spots are stated as instrument limits by the program itself

- The AETH-02 conclusion is narrowed on purpose: "No evidence was found that the
  measured persistent-edge and cycle structures perform a demonstrated
  nontrivial function under the assays run… must not be quoted as, '[redacted]
  contains no possible circuitry.' The assays here can see localisation,
  contest, persistence and resource routing. They cannot see…"
  (`[redacted]/AETH-01/AETH-02_CLOSE_2026-09-24.md:276-286`).
- The same operator amendment appears twice in
  `[redacted]/AETH-01/NATIVE_CIRCUITRY_01_2026-09-24.md`:
  - `:451-459` gives the verdict scope.
  - `:602-611` says the four measured dimensions "are **not jointly
    necessary**, and freezing them as the definition of circuitry would make
    this round's instruments into the criterion". It asks that a future positive
    claim be "stated against whatever dimensions its own mechanism implies,
    declared in advance, each carrying a matched null".
- The engine card at HEAD still lists "anything spatially distributed and
  informational rather than resource-routing" as "Ambiguous or open"
  (`[redacted]/AETHER_ENGINE_CARD.md:113-121`). It also says "nothing in [redacted]'s
  observatory can say a structure does something useful, only that it causes
  differences" (`:117-118`).
- **A later, independent instrument limit.** The AETH-03 content signature
  "detects transport in a clean relay but not in a rich soup, even for a law
  that forwards bytes by construction (E-P1 failed). A value-provenance
  detector would be needed" (`[redacted]/AETH-03/RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md:39-42`;
  `[redacted]/AETH-03/PHYSICS_DESIGN_03_2026-09-27.md:216-224`, "Recorded as an
  instrument limit, not repaired here"). This is a blind spot for
  *informational* structure that was measured directly: a known positive
  control went undetected.
- **Part of the negatives is not an instrument limit.** The AETH-02 falsifiers show:
  - the bulk is about 92% static;
  - about 94% of template change disappears without injected perturbation;
  - a one-bit difference stays within about one site for 10,000 ticks.

  (`[redacted]/AETHER_ENGINE_CARD.md:123-140`;
  `[redacted]/AETH-01/AETH-02_CLOSE_2026-09-24.md:288-302`.) The one-bit-twin
  locality result is *not* heredity-shaped. It counts any differing carried
  state, including hidden flags (`[redacted]/AETH-03/PROPAGATION_ASSAY_AUDIT.md:14-16,35-40,130-132`).
  Informational, distributed or reconfigurable circuitry would still need
  *some* difference to move. Very limited causal reach therefore bounds those
  classes in `aeth01.v1` under B-balanced parameters. It does not rule out
  uncontested, stationary or stateful structures that hold information
  without moving it.

### 3.2 Is the heredity ontology in the vocabulary, the inference contract, or the instruments?

**(a) Vocabulary: addressed, and only vocabulary.** The terminology refactor
renamed heredity→configuration transmission, lineage→causal provenance,
offspring→successor, mutation→perturbation, reproduction→recursive
construction, and so on (`[redacted]/AETH-01/TERMINOLOGY_REFACTOR_RECEIPT_2026-09-21.md:81-106`).
Its receipt says: "No transition equations, byte layout, arbitration logic,
energy accounting, Mu-trigger behavior, or scientific thresholds were
changed. This is nomenclature only" (`:150-152`). Several items were kept as
frozen aliases: `HEREDITY_VARIATION`, `mutation_applied`, `MUT_NUMER`
(`:110-125`; `[redacted]/test/reference/scientific_aeth01.py:11-24`). A linter
enforces the vocabulary going forward (`:156-161,194-198`). The rename does not
answer Astra's point. Astra flagged the concern as "not solved by keeping
metadata out of physics" (`ASTRA_REVIEW_01.md:181`).

**(b) Inference contract: partly repaired; template-copy is still the backbone.**

- The repair ledger accepts S04, M05 and M08
  (`[redacted]/AETH-01/REPAIR_LEDGER_01.md:175-211,416-442,509-534`). The repaired
  ladder:
  - separates ten evidence axes;
  - drops "resemblance first" and "parent-intact vs parent-consumed" as
    universal requirements (`[redacted]/AETH-01/HEREDITY_REQUIREMENTS.md:141-149`);
  - allows standing, spatial and energy-pattern variation as well as
    Mu-origin variation (`:130-139`);
  - treats a distributed consortium as "a normal, not degenerate, case" (`:51-55,161`).

  These are real de-biasing steps against the template-copy/Mu/parent ontology.
- The heredity shape remains in the higher tiers:
  - "Capacity" is defined as a *write* into the target's opcode/arg0/arg1
    fields (`HEREDITY_REQUIREMENTS.md:35-38,76-86`).
  - Recursion is capacity-construction repeated along a chain (`:119-129`).
  - Tier 5 requires that a variant be "copied onward by a further
    value-transport event" (`:42-45`) and propagated "by a further
    CAUSAL_VALUE_CONSTRUCTION step" (`:130-136`).

  So tiers 2-5 still count transmission only when a winning write copies a
  byte or capacity. They do not count:
  - transmission through energy landscapes;
  - transmission through hidden carried state;
  - contest outcomes ("who wins" changing without any byte being copied);
  - reconfiguration of aim.

  The provenance graph the ladder uses is built from "this target field's
  stored value … was contributed by winning source site X" chains
  (`[redacted]/AETH-01/OBSERVATORY.md:158-173`).
- The ledger's M08 repair covers only component tracking and the novelty
  assay (`REPAIR_LEDGER_01.md:509-534`). It does not address the sentence at
  `ASTRA_REVIEW_01.md:209` as a whole. The ledger dispositions only numbered
  S/M/N/B/K items; it has no entry for the "Ontology audit" table (`:197-209`).
- **Astra's own closure review names this residue.** S04 and M08 are both
  PARTIALLY_CLOSED (`[redacted]/AETH-01/ASTRA_CLOSURE_REVIEW_02.md:78,88`):
  - S04: "tiers 3+ still require opcode/arg0/arg1 causation while the
    resource row admits resource-mediated evidence to tiers 2-5 … A funded,
    prewired writer exposes that exclusion" (`:78`).
  - In a probe, an energy donor made a preconfigured writer emit, which
    blocking the funding prevented. The helper still classed the donor edge
    "only CAUSAL_VALUE_CONSTRUCTION" (`:104-110`). This is a demonstrated
    false negative of the copy-shaped ladder.
  - The K3 helper "still encodes a restricted field ontology and does not
    qualify a general detector" (`:460-462`).
- **The linter does not watch the terms Astra named.** The terminology
  linter's deprecated list covers heredity, lineage, offspring, mutation and
  others, but not "parent", "template", "copy", "inherit" or "Mu"
  (`[redacted]/test/test_aeth01_terminology_audit.py:34-61`). The AETH-03 observer
  vocabulary ("sufficient parent", "template") therefore passes
  (`aeth03_assay_audit.py:28-44`).
- **Some of the fusion is a declared hidden prior of the physics.** "Hidden
  prior: 'movement' and 'replication' are physically fused by this choice"
  (`[redacted]/AETH-01/DECISIONS.md:141-152`, D-AETH01-07). Mu acts on fields 0-3
  only (`DECISIONS.md:73-75`).

**(c) Instrument logic: mostly from the physics, not the observer.**

- `aeth01_graph.py:9-26` says outright that a site's single out-edge per tick
  is a consequence of the transition law. Its cycle/in-tree structure is
  "consequences of the transition law, not findings", measured by a test
  rather than assumed.
- The template-copy primitive is part of the physics. Astra: "Writing a
  neighbor's byte is a supplied primitive" (`ASTRA_REVIEW_01.md:202`).
  Mu is applied only where a site wins a write
  (`[redacted]/AETH-03/PROPAGATION_ASSAY_AUDIT.md:52-53`).
- So for `aeth01.v1`, the edge/"template change" observables
  (`AETH-02_CLOSE_2026-09-24.md:243-251`) describe the law's own write
  channel. The observer does not impose them.
- The tier-1 observatory computes only histograms, entropy, Gini,
  autocorrelation, compression and change rate. It deliberately contains no
  construction or transmission detector (`[redacted]/observatory/aeth01_observatory.py:1-29`).
- The AETH-03 twin and counterfactual-parent assay is heredity-neutral:
  - it asks only whether a difference at x is caused by a neighbour's full
    state (`[redacted]/observatory/aeth03_assay_audit.py:28-44,168-183`);
  - its predicate covers every carried state (`PROPAGATION_ASSAY_AUDIT.md:130-132`).
- One structural bias remains. Causation is scored by *single-parent
  sufficiency*, and "joint" events are assigned a lower bound
  (`PROPAGATION_ASSAY_AUDIT.md:146-150`). Only 2 of 2,793 audited events were
  joint (`:118-119`). The audit's conclusion that "differences are caused one
  parent at a time" is partly fixed by that definition. That is the only measurement in the repo that touches
  "spatially distributed" causation, and it is made at radius 1 with pairs of
  neighbours inside one step. It is not a test of distributed circuitry.

### 3.3 Operationalising recursive construction and mutual constructors (H-D3-16)

- There are requirements text and fixtures, but no built detector:
  - Formal tiers 3-4 with ablation batteries are in `HEREDITY_REQUIREMENTS.md:76-129`.
  - The adversarial-case table has "Mutual constructors A<->B … Both
    directions of the intervention test … must be run and both must show
    positive causal effect before 'mutual' is claimed" (`HEREDITY_REQUIREMENTS.md:159`).
  - The same table covers partial copying completed by the environment:
    "Causal provenance graph must show ALL contributing source sites/events"
    (`:160`).
  - It also covers the distributed consortium (`:161`).
  - The seeded fixtures exist: relay, activation, distributed, and recursive
    activation (`[redacted]/test/reference/scientific_aeth01.py:42-117`). By the
    repo's own account, fixture 4 shows only
    RECURSIVE_ACTIVATION_OF_PRECONFIGURED_MACHINERY, "NOT … recursive
    configuration construction" (`HEREDITY_REQUIREMENTS.md:124-129`).
- The document status is "DRAFT REQUIREMENTS ONLY. No detector is built in
  AETH-01" (`HEREDITY_REQUIREMENTS.md:4-5`). The open question is still worded
  "not yet designed" (`[redacted]/AETHER_OPEN_QUESTIONS.md:134-137`). The K3
  tests call themselves "fixture-local calibration, not a general detector"
  (`[redacted]/test/test_aeth01_kill_gates.py:291`). The
  engine card lists "recursive construction" among things "Not built in"
  (`[redacted]/AETHER_ENGINE_CARD.md:52-56`).
- None of the tests handles a mutual constructor whose two directions are each
  *necessary but not sufficient*. The both-directions test (`:159`) uses
  single-source perturbations, so it would hit the same single-cause bias as
  the parent audit.
- A repo-wide search for "mutual constructor" / "A builds B" /
  "value-provenance" outside [redacted] found only harvest or frontier citations
  of the open question (e.g. `roles/[redacted]/frontier/poi/raw/I2_substrate_physics.md:245`).
  It found no [redacted] design.
- **Closest cross-substrate evidence (not [redacted]).** [redacted] P-11 built
  specimens for this: a two-tape mutual-construction pair ("A0 copies
  A1 … A1 copies A0 … neither member alone copies itself"), host-mediated
  heredity, and complement-encoded offspring
  (`roles/[redacted]/challenge/p11/PREREG_P11.md:168-170`). A copy-fidelity
  predicate rejected all three as false negatives
  (`roles/[redacted]/challenge/p11/RESULT.md:48-50`). This is independent
  support, in a Z80/toy-VM substrate, that copy-shaped heredity predicates miss
  mutual constructors and host-mediated heredity. It is a
  known-answer battery that any [redacted] mutual-constructor predicate could
  reuse.

## 4. Result

1. **H-D3-14: the "no circuitry" reading is partly an instrument limit, and
   the program itself declares it one.**
   - The AETH-02 negative is scoped to four assay dimensions. The operator
     amendment explicitly refuses to freeze those as the definition of circuitry.
   - One informational blind spot has since been *measured*: content transport
     goes undetected in a rich soup, and a value-provenance detector is needed.
   - The rest of the negative is not an instrument artefact. A heredity-neutral
     twin assay shows that a one-bit difference barely travels (about one
     site) and that the medium is about 92% frozen. So any
     distributed/informational circuitry in `aeth01.v1` (B-balanced) would
     have to work with almost no causal reach.
   - No assay for the five classes has been designed or run. Section 5 lists
     what would detect them.
2. **H-D3-15: the heredity ontology lives in the inference contract, not in the
   running instruments. Only the vocabulary layer was fixed; no
   ontology-neutral re-analysis exists.**
   - The measured edge graph and template-change figures come from the physics
     (a byte-write primitive), not from the observer.
   - The claim ladder (tiers 2-5) still recognises transmission only as a
     winning-write copy of a value or of opcode/arg0/arg1 "capacity". Because
     of that, a heredity route through energy, hidden state, contest outcome or
     re-aiming could not reach tiers 2-5 however well evidenced.
   - This matters for TH-001 and for "organism-free" claims. Any positive
     heredity claim made through this ladder would be ontology-shaped.
     [redacted]'s current *negatives* rest mainly on the heredity-neutral twin
     assay, so they are less exposed.
3. **H-D3-16: partly operationalised on paper; not operationalised as a
   running detector.** Requirements exist for:
   - capacity recursion;
   - both-direction mutual-constructor tests;
   - all-contributors provenance for environment-completed copying.

   Only seeded fixtures are built. The strong case, recursive *configuration*
   construction, has no fixture. No predicate handles jointly-necessary
   mutual causes.

Confidence: high on 1 and 3, because they rest on explicit program
statements; medium-high on 2. The "how much" in H-D3-15 is not quantified by
anything in the repo. `analysis.py` specifies the computation that would
quantify it.

## 5. What an assay for the five blind-spot classes would look like (design, not evidence)

These are derived from the program's own repaired requirements and
instruments. None has been run.

| Class | Candidate assay | Built from |
|:--|:--|:--|
| spatially distributed | joint-source ablation and rescue over *sets* of sites (k ≥ 2, non-adjacent), with a matched random-set null; report the super-additive share | parent audit's JOINT category (`aeth03_assay_audit.py:38-44`); "redundancy-aware joint ablation/rescue" (`OBSERVATORY.md:180-182`) |
| informational (vs resource-routing) | value-provenance tracking: which source byte a value was copied from, followed across rewrites; control = `fwd` relay in a rich soup (E-P1 must pass) | `PHYSICS_DESIGN_03:216-224` |
| uncontested in normal operation | counterfactual contest injection: add a competing writer and measure the downstream difference, instead of observing contests | edge classes `aeth01_graph.py:52-60` ("only intervention can tell") |
| stateful, not self-repairing | set a state bit, wait a delay, then read it out via a later twin divergence; compare against the delayed-causation share (which "does not discriminate" as currently defined, `PHYSICS_DESIGN_03:225-227`) | twin assay |
| dynamically reconfigurable | per-channel causal decomposition (content vs enabling vs energy vs hidden vs contest) of each causal event; `rcv_str`'s "activity re-routes later activity" is the known-answer case | `RESEARCH_BLOCK_SYNTHESIS:31-38`; `analysis.py` |

## 6. Limits

- I read committed documents and code only. No experiment was run, and the
  numbers above are quoted from committed reports.
- The layering in 3.2 (vocabulary / contract / instrument) is my analysis,
  not a program decision.
- "Mostly from the physics" applies to `aeth01.v1` and the AETH-03 variant
  laws. A different substrate would need the same check again.
- I did not check whether `World.extra` includes `rcv`'s received flag in
  every variant; `analysis.py` assumes it (per `PROPAGATION_ASSAY_AUDIT.md:130-132`).
- The search for later evidence was grep-based across the whole repo. Material
  under a different vocabulary could have been missed.

## 7. What would change the conclusion

- **H-D3-15 / result 2.** Run `analysis.py`. If literal-copy events are ≥ 0.8
  of causal events for every law and arm, the template-copy ontology is mostly
  the physics' own, and Astra's concern reduces to naming and inference hygiene. If non-copy
  channels are ≥ 0.5 for any law or arm, the tier ladder is blind to most
  causal transmission there, and it needs a channel-neutral tier.
- **Result 1.** A value-provenance detector that passes E-P1 in a rich soup
  and still finds no content transport would turn the informational blind spot
  into a real negative. A positive on any row of section 5 would overturn
  "no circuitry".
- **Result 3.** A committed detector, or a fixture showing recursive
  *configuration* construction (routing and field ablations at each
  generation), or a jointly-necessary A↔B fixture, would move H-D3-16 from
  "paper" to "operational".
- A commit after `5266cceb` that re-analyses AETH-02/03 data under a
  channel-neutral ontology would supersede the "no ontology-neutral
  re-analysis" finding.

