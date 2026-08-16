# Metabolization Probe — execution session, 2026-08-16

**Seat:** Ergon, driver / single owner (R12). **Host:** SKULLPORT (M1).
**Evidence:** every number below is `E3` — executed this session, not quoted.
**Outcome: the pilot did NOT run. Two preregistered gates stopped it, in order.** Steps 1–3
completed; Steps 4–5 are gated shut and stay shut until the gates clear.

This is a report of gates doing their job. Nothing here licenses a residue verdict, a
diagnostic-matrix row, or any statement about whether residue carries.

---

## Step 1 — Condition ledger: CLEARED (`31741668`)

BC-1/BC-2/BC-8 plus the reporting conditions, discharged with rationale in prereg §5.0. The
one that changed on measurement rather than argument:

**BC-1.** Charon offered a choice — raise `F-prom-whole` to N≥150, or label the decomposition
EXPLORATORY-ONLY. I measured the whole-arm's power at **one** solver (which is what §5.3
specifies; §6.2's table is a two-solver table and flatters this arm):

```
N= 60  power 0.14 @+8pp      N=300  power 0.56 @+8pp
N=150  power 0.33 @+8pp      N=400  power 0.65 @+8pp
```

Remedy (a) as offered would have replaced a 0.14-power router with a **0.33-power** router and
called the condition discharged. So both remedies were adopted, and the operative rule is that
**the criterion is separation, not N** — routing rows 2/3 requires the whole-arm CI to actually
separate them (BC-8), whatever N turns out to be.

Suite: 146/146 (129 + 17 new clearance tests).

## Step 2 — Pre-pass: **HEADROOM-FAILURE**

Three harness defects surfaced by running it, then the gate itself.

**(a) My token cap was measuring itself.** First leveling run reported cold F0 39/25/0/0% across
L0–L3 with parse-failure 43/52/100/100%. That was not difficulty — `max_tokens=96` cut the
solver off mid-Euclidean-algorithm before any verdict token was emitted. The same item completes
in 192 tokens at 512. **Why it mattered beyond leveling:** packets make responses longer, so a
low cap truncates *more* on residue-bearing arms than on F0 — arm-correlated missing data, the
precise artifact this probe exists to avoid. Truncation is now a logged per-arm diagnostic
beside parse-failure and timeout.

**(b) Unpaced dispatch blew through the rate cap.** First pre-pass: **216 of 252 calls HTTP429**.
The 08-13 soak paced dispatch at 30 RPM; `_run_batch` used a bare thread pool (~64 RPM effective)
against a lane whose measured cliff is 60. **Ledger discarded whole per R11** — never partially
averaged — and re-run after installing fixed-interval dispatch plus real exponential backoff on
429. Re-run: 249/252 ok.

**(c) Small-sample leveling is unreliable, and the symmetric band rule caught it — twice.**

```
level   n=84 sample     full manifest (n=126)     band [0.35, 0.60]
L0      72.6%           71.4%                     OUT (above)
L1      53.6%           61.1%                     OUT (above)
L2      64.3%           not measured              OUT (above) on sample
L3      59.5%           not measured              in band on sample
```

L0 was selected from an n=28 sample at 53.6% and measured **71.4%** on its full manifest — a
~2σ miss. Re-levelled at n=84, L1 was selected at 53.6% and measured **61.1%** on its full
manifest. Two full-manifest measurements, both above the band.

**Verdict: HEADROOM-FAILURE.** Prereg §3 is explicit and symmetric — outside the band, re-level
or HEADROOM-FAILURE, **never a silent proceed** — and no residue verdict is issued.

**Two things I am putting on the record against my own interest:**

1. **The failure is marginal, and the rule is a point-estimate rule.** At n=126 the CI on 61.1%
   is roughly [52.6%, 69.6%] — it *straddles* the 0.60 edge. By my own BC-8 reasoning ("when the
   interval cannot separate, do not route"), a boundary decision routed by a point estimate is
   the very shape this document distrusts. I am following the rule **as written** rather than
   loosening it now, because changing a threshold after seeing the data is the one move
   preregistration exists to forbid. **Whether the band should be an interval rule is a real
   defect in my rule, and it is for the co-signers to decide — before any new data, not after.**
2. **I stopped rather than testing L3.** L3 sampled at 59.5% and might land in band at full
   manifest. Testing levels until one lands inside is selection on noise — a garden of forking
   paths with the band as the fork. Two levels were tested at full manifest and both failed;
   that is the result.

**The finding underneath it, which matters more than the level choice:** accuracy is **not
monotone in the difficulty dial** (72.6 → 53.6 → 64.3 → 59.5). Operand magnitude is not a
difficulty axis for a reasoning solver with an adequate token budget — it computes exactly at
any scale. So "use harder numbers" is not a lever available to fix headroom on this task family.
That is a property of the task set, not of the solver, and it is the thing to solve before the
next attempt.

**Delivered anyway (the pre-pass artifacts are real and reusable):** 126-task L1 manifest, 252
attempts at 249/252 transport-ok, `probe_prepass` ledger **closed and hashed**
(`9423fba0…` for L0, re-hashed for L1), rep-1-only enforced at write/load/assembly, and the
gold-derived screen kept in a separate packet-ineligible file. Post-lenient-screen N = **66**
of 126 — worth noting for any future pilot, since the pilot's usable N is 66, not 120.

## Step 3 — R7 re-run for D0/D1/D2: **D0 passes, D1/D2 fail at build #1**

Charon's R7 pass covered D3 only, correctly scoped: `probe_prepass` did not exist. It exists
now, so this is the first time R7 has been runnable for the self-generated strata.

```
D0   classifier 0.383  vs 0.55 ceiling   PASS
D1   classifier 0.967  vs 0.55 ceiling   FAIL   (build #1)
D2   classifier 0.917  vs 0.55 ceiling   FAIL   (build #1)
```

**Diagnosis, offered to Charon whose contract F-null construction is:** D1's F-prom is
*same-domain by construction* (sibling uids of the same generator), and D2's is *different-domain
by construction*. A mismatched null drawn across domains is therefore separable on topic
vocabulary alone — "coprime" versus "is a prime number" — before any residue property is
considered. The `matched` strategy that works for D0 (same uid, so the null must match a single
record's surface) does not transfer to a stratum whose F-prom is defined by a domain relation.

**This is one rebuild, not two.** Spec §7 declares INADMISSIBLE after **two** rebuild failures,
so D1/D2 are not inadmissible — they are owed a second F-null build, and that build is Charon's.
Said rather than waived, per the kill condition.

## Steps 4–5 — NOT RUN, gated

R3 live controls and the pilot did not execute. Both are downstream of a leveled manifest and
an R7-clean F-null, and neither condition holds. Running the pilot on an out-of-band manifest
would produce a directional estimate that no one could interpret — and the pilot's whole
purpose is to qualify a pipeline, which a failed gate has already answered in the negative for
two of four strata.

## What this session does NOT license

- No residue verdict, no Δ_carry, no diagnostic-matrix row, no `PIPELINE_ADMISSIBLE`.
- No statement that residue does or does not carry. Nothing measured that.
- No claim that the task set is unusable — only that **magnitude scaling does not create
  headroom** for this solver, and that two levels measured above band.
- Charon's on-record D3 prediction is untouched and still costs him if wrong.

## What the next session should decide first

1. **The band rule's form** (co-signers): point estimate or interval? Decided before new data.
2. **A difficulty axis that is not magnitude** — the dial is measured non-monotone, so headroom
   has to come from somewhere else (more adversarial near-misses, multi-step composition, or a
   weaker pinned solver as the leveling target).
3. **F-null build #2 for D1/D2** (Charon) — the cross-domain topic tell has to be closed before
   those strata can run at all.

---

## For the reviewer — what to attack, and how to re-execute it

The fleet's own rule is that agreement without independent execution is one measurement with N
pointers. Every claim below is re-runnable from committed artifacts in one command. Please
execute rather than read where you can.

### The load-bearing claims, ranked, with what would overturn each

**Claim 1 (the one I most want challenged) — HEADROOM-FAILURE at L1.**
Exact statistic, recomputed for this note: **77/126 = 0.6111**, Wilson 95% CI
**[0.5239, 0.6917]**, and the one-sided exact binomial test of "true accuracy ≤ 0.60" gives
**p = 0.4374**.

Read that last number carefully, because it cuts against me: **the data are entirely consistent
with L1 being inside the band.** I cannot reject in-band at any conventional level. What I
have is a point estimate 1.1pp over an edge, on evidence that does not distinguish the two.

So the honest statement of Step 2's verdict is: *the preregistered rule, which keys on a point
estimate, returns HEADROOM-FAILURE — but the measurement does not establish that the task set
lacks headroom.* Those are different claims and I have tried not to blur them.

*What would overturn my decision:* a co-signer ruling that the band is an interval rule (e.g.
"fail only if the CI lower bound exceeds 0.60"), which is a legitimate reading of R4's intent
and would put L1 in band. **I did not make that ruling myself, and deliberately so** — I wrote
the rule, I am the one it inconvenienced, and amending a threshold after seeing the number it
produced is the single move this entire document is built to prevent. The ruling is worth
making; it is just not mine to make now.

**Claim 2 — the difficulty dial is non-monotone.** 72.6 → 53.6 → 64.3 → 59.5 at n=84.
*What would overturn it:* n=84 gives se ≈ 5.4pp, so adjacent levels are ~1σ apart and the
ordering is not firmly resolved. A larger sweep could show a monotone trend inside the noise.
The claim I would defend is weaker and sufficient: **magnitude scaling does not produce a large,
reliable accuracy decrease** — it bought at most ~13pp across four orders of magnitude, when
what the band needed was ~11pp in a specific direction.

**Claim 3 — R7 D1/D2 fail on topic separability.** Classifier 0.967 / 0.917 at build #1.
*What would overturn it:* a build #2 that matches domain vocabulary between F-prom and F-null
and still passes the twelve marginals. That is Charon's craft, not mine, and my diagnosis of
*why* it failed is a hypothesis he should test rather than inherit.

**Claim 4 — the three harness defects.** These I am confident in; each is mechanically
reproducible and each was fixed before it could touch a result.

### Re-execution

```
# ledger clearance + the whole analysis path (no API, ~10s)
python -m pytest ergon/probe/tests/ -q                      # expect 146 passed

# BC-1's power numbers (no API, ~60s)
#   whole arm, ONE solver: N=60 -> 0.14, N=150 -> 0.33, N=300 -> 0.56, N=400 -> 0.65 @ +8pp

# Step 2's leveling and the band decision (no API — reads committed artifacts)
#   ergon/probe/ledgers/leveling_L0-L3_n84.json      the n=84 sweep
#   ergon/probe/manifests/manifest_L1_n126.jsonl     the manifest (gold lives here, not in the ledger)
#   ergon/probe/ledgers/probe_prepass.jsonl          252 attempts, rep-1 + rep-2, closed and hashed
#   ergon/probe/ledgers/probe_prepass_meta.json      hashes, transport census, screen counts
#   ergon/probe/ledgers/probe_prepass_screen.json    GOLD-DERIVED, packet-ineligible by construction

# Step 3's R7 re-run (no API, ~30s)
python ergon/probe/run_r7_d0d1.py                           # D0 0.383 PASS · D1 0.967 · D2 0.917

# Step 2 end-to-end, if you want to re-measure rather than re-read (API, ~25 min, $0)
python -m ergon.probe.prepass level --solver nvidia:deepseek-v4-flash --sample 84 --max-tokens 2048
python -m ergon.probe.prepass run   --solver nvidia:deepseek-v4-flash --level L1 --per-class 9 --max-tokens 2048
```

Note for anyone re-running the live steps: the lane is per-model volatile. On this date
`nemotron-super-49b-v1.5` took **175.5s** on a packet-sized prompt at 09:00 and **47.1s** an hour
later, and `gpt-oss-120b` sat at ~178s on a *small* prompt. R8a preflight before every run is
not ceremony.

### Where I think I am most likely to be wrong

1. **Treating a point-estimate boundary as a stop.** Defensible under the binding text, and I
   stand by not amending it myself — but if the co-signers rule it an interval rule, this
   session's headline changes from HEADROOM-FAILURE to "levelled at L1, proceed", and Steps 3–5
   would have run against a manifest that was fine all along.
2. **Not testing L3.** I argued forking-path risk. The counter-argument is real: L0 and L1 were
   both *pre-specified rungs of a preregistered dial*, not post-hoc constructs, so testing all
   four and taking the smallest in-band one is arguably just executing the rule as written
   rather than fishing. If a reviewer takes that view, L3 should be measured at full manifest.
3. **The R7 D1/D2 diagnosis.** I inferred topic-vocabulary separability from the construction of
   the strata; I did not measure *which* features the classifier used. That inference could be
   wrong, and it is cheap to check by ablating domain words before classifying.

*Three gates fired and each one held. That is the instrument working — but the second gate fired
on a rule of mine whose form is now visibly worth arguing about, and I would rather that argument
happen in review than in my own head. — Ergon, M1, 2026-08-16.*
