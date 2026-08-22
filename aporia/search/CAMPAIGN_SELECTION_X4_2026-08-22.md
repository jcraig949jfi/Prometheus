# Campaign selection — X-4 opens, with branches that partition and a rebuild tax paid once

Zero campaigns were live. Selection under all three doctrine rules: CAMPAIGN DISCIPLINE, GATE
DESIGN, and the new BRANCH CONDITIONS MUST PARTITION. **No primary experiment was run.**

## 0. A refinement of my own X-3 claim, before anything is built on it

X-3 reported D = −0.0025 with paired CI **[−0.0354, 0.0304]** and I said it excludes the 0.05 effect
the campaign was powered to detect. That is accurate. But the same interval **does not exclude
0.03** — 0.0304 > 0.03. So the honest standing claim is narrower than "the signature adds nothing":
it is *"the signature adds less than 0.05, and the data cannot rule out an effect as large as 0.03."*
Any successor must be powered below that or it will restate X-3 in new numbers.

## 1. Power arithmetic first

X-3's observed discordance rate was (22+23)/400 = 0.1125, so paired SE ≈ √(π/n):

    n =  400 real-op pairs   SE 0.01677   MDE(2 SE) 0.0335
    n =  640                 SE 0.01326   MDE        0.0265
    n =  800                 SE 0.01186   MDE        0.0237
    n = 1125                 SE 0.01000   MDE        0.0200

**640 real-operator pairs gives MDE ≈ 0.0265**, comfortably below the 0.03 that X-3 could not
exclude. That is the target, and it is what the build below delivers.

## 2. The restart tax, fixed structurally rather than paid a fourth time

Measured last selection pass: **2 rebuilds in 3 campaigns**, each costing roughly one of the three
passes a campaign gets — because every campaign burns its frozen split by reading it. X-4's build is
therefore **multi-split**: one scan produces a development set, a decision split, and a **reserved
frozen-B that X-4 must not open**. The successor campaign inherits a fresh, never-read split and pays
no rebuild.

This is infrastructure, and the doctrine admits infrastructure only with a named waiting consumer.
The consumer is X-4, opening now; the second consumer is whatever follows it, and if nothing does,
frozen-B was wasted — stated so it can be checked later.

**Built** (`build_x4_benchmark.py`, every original constant unchanged; seed 20260825 and target 400
per operator changed and disclosed): **2,000 positives, 400 per operator, 1,983 matched negatives,
disjoint from Campaigns X, X-2 AND X-3** (375 pairs excluded by A-number). All five operators hit
the 800 scan cap, so the corpus is not exhausted.

    development   400 pairs   320 four-real-operator
    frozen-A      800 pairs   640 four-real-operator   <- X-4's decision split
    frozen-B      800 pairs   640 four-real-operator   <- RESERVED, not opened by X-4

## 3. What X-4 measures, and why it beats the alternatives on resolvability

**The question.** Three campaigns established that raw 25-term log-magnitude vectors retrieve at
0.1250 (156× adjusted chance) and that a *hand-designed* 125-dim signature does not beat them. The
live question is whether a representation **learned from data** does — not whether a cleverer hand
design exists, which is the question three campaigns already answered.

**The method, fixed now.** Feature space = raw-25 concatenated with V2's 125 features (150 dims). A
linear metric is learned by closed-form **relevant-component / generalised-eigen metric learning**:
the covariance of `z_src − z_tgt` over development *positives* against the covariance of
`z_src − z_decoy` over development *negatives*, taking the top-k discriminative directions. Closed
form, no gradient training, no hyperparameter search to overfit with. **Fitted on the 400
development pairs only; frozen-A is read once in pass 3; frozen-B is never opened.**

**Rejected alternatives, on resolvability not interest:**

- *Cutoff sweep.* D was measured only at top-10 and no sweep was preregistered, so sweeping the
  burned X-3 split would be data dredging. Folded into X-4 instead as **descriptive only**: top-10
  is the single decision-bearing cutoff, and other cutoffs are reported without branch weight.
- *The moebius asymmetry* (raw 38/100 beat V2 29/100). At 160 pairs per operator in frozen-A the
  paired SE is 0.0265 and MDE is **0.053** — per-operator differences of the observed size cannot be
  resolved even at this scale. Reported descriptively; **no branch depends on it.**

## 4. X-4 PREREGISTRATION — branches verified to PARTITION

Let `[lo, hi]` be the paired McNemar 95% CI on `D = L2(learned) − L2(raw terms)`, top-10, any-valid
scoring, on the 640 four-real-operator frozen-A pairs. `shift` is reported separately and never
folded into D.

- **K0 gate, first.** Wilson 95% CI lower bound on frozen-A L1 top-1 > 0.90. Fails → **M0 PARK**,
  and no L2 is computed.
- **M1 ADVANCE** — `lo > 0.03`. A learned representation materially beats raw terms.
- **M2 REDESIGN** — `0 < lo ≤ 0.03`. Real but smaller than useful.
- **M3 KILL** — `lo ≤ 0 ≤ hi` **and** `hi < 0.03`. A useful effect is excluded; the
  learned-representation line dies, and with it the case for any representation over raw terms.
- **M4 PARK** — `lo ≤ 0 ≤ hi` **and** `hi ≥ 0.03`. Underpowered: cannot rule the effect in or out.
- **M5 REDESIGN** — `hi < 0`. The learned representation is *worse* than raw terms.

**Partition proof.** For any interval with `lo ≤ hi`: if `hi < 0` → M5. Otherwise `hi ≥ 0`, and
either `lo > 0.03` → M1, or `0 < lo ≤ 0.03` → M2, or `lo ≤ 0`, in which case the CI contains 0 and
`hi < 0.03` → M3 while `hi ≥ 0.03` → M4. **Exhaustive and mutually exclusive.**

**The region three campaigns missed is now covered.** X-3's own CI [−0.0354, 0.0304] maps to **M4
PARK** under this partition — inconclusive at the 0.03 level, which is exactly what it was, and
which no branch in X-3 could express.

**Minimum detectable effect stated explicitly: 0.0265** at 2 SE on 640 pairs. M3 KILL is reachable —
with D ≈ 0 the interval half-width is ≈ 0.026, so `hi ≈ 0.026 < 0.03` fires it. That is the first
campaign in this line where a kill can actually be earned by a null result.

## Campaign selection pass; CAMPAIGN X-4 opens at pass 1/3
