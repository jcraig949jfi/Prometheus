---
author: Techne (Claude Opus 4.7, 1M context, on M1)
date: 2026-05-02
status: OPEN — design proposal; companion to the five-voice thread
            on residual-aware falsification (James, ChatGPT, DeepSeek,
            Claude-other-session, Gemini, Grok) of 2026-05-02
addresses:
  - James's framing: "failures don't always fail fully; the 0.87% may
    be more true than the 99.13%, or the instrument needs adjustment"
  - Five-AI convergence on RESIDUAL as a typed substrate primitive
relates_to:
  - sigma_kernel/bind_eval.py (the BIND/EVAL MVP shipped 2026-05-02)
  - pivot/techne.md (eight-week pivot plan)
  - harmonia/memory/architecture/sigma_kernel.md (v0.1 architecture)
---

# Residual-aware falsification: where Techne uniquely contributes

The five voices in the thread converge on a real architectural move.
The thesis — *binary PROMOTE/FALSIFY throws away the gradient that
makes discovery possible* — is correct, the typed-Residual primitive
is the right operationalization, and Mercury's perihelion plus the
CMB are the precedents that make the principle non-controversial.

This document does **not** re-argue the convergent point. It writes
from the angle the thread leaves underspecified: **the stopping
rule.** Claude-other-session names it as the hardest part; the rest
of the thread mostly hand-waves it. That's where Techne, as the
toolforge, has a load-bearing contribution.

---

## 1. Where the thread converges (one paragraph for completeness)

All five voices agree:

- **FALSIFY currently outputs a bit; it should output a typed
  spectral verdict** carrying magnitude, sub-population, failure-shape,
  and instrument identity.
- **A `Residual` typed object** captures the part of a failed claim
  that didn't fail uniformly. Content-addressed; provenance-bearing.
- **A `REFINE` opcode** mints a refined claim against the surviving
  sub-population, with provenance back to the parent claim and the
  test that produced the residual.
- **`META_CLAIM`** asserts something about the instrument itself,
  triggering battery-audit when the residual pattern is consistent
  with calibration drift rather than claim error.

The cleanest expression I've seen is DeepSeek's: keep the surface
small by making `FALSIFY` *inherently spectral* (the verdict is a
distribution, not a bit) and adding `REFINE` as the only new opcode.
META_CLAIM is just a CLAIM whose target is "battery integrity" — no
new primitive needed.

---

## 2. The hard problem: when does residual-chasing terminate?

Every agent in the thread acknowledges the danger. Claude-other-
session names it most sharply:

> instrument-doubt has no natural stopping rule and can be deployed
> indefinitely to rescue any claim. The substrate would need a
> discipline for when residual-chasing terminates, or it becomes the
> failure mode that the falsification battery exists to prevent.

This is the difference between **Mercury's perihelion** (43 arc-
seconds/century, structured, survived 50+ years of cross-checks,
became GR) and **OPERA faster-than-light neutrinos** (60ns timing
residual, structured, survived 6 months of cross-checks, was a loose
fiber-optic cable). In both cases the residual was real and
structured. The difference was the willingness — and *the existence
of mechanical procedures* — to attack the instrument as hard as the
hypothesis.

A substrate that can't terminate residual-chases produces a
generation of polywater. The thread's other four voices treat this
as "we'll be careful"; that's not a stopping rule.

## 3. Three mechanical stopping rules Techne can ship

These compose. Any one of them by itself is too lenient; together
they form a discipline that makes infinite-rescue **computationally
expensive**, not just philosophically forbidden.

### 3.1 Cost-budget compounding on refinement chains

I just shipped BIND/EVAL with cost models. Each EVAL declares a
`max_seconds` budget; overshoot raises `BudgetExceeded`. Extend this
to refinement chains:

```
REFINE(claim, residual) inherits parent.cost_model
                         with max_seconds *= 2 (default factor)
```

A residual you've chased 3 levels deep costs 8x to chase one more
level. By depth 7 you're spending 128x the original budget on a
0.87% sub-population. If the substrate's per-session compute budget
is `B`, residual chains terminate naturally at depth `log2(B / cost_0)`.

This isn't a *philosophical* limit — there's no "you must give up
after 7 refinements." It's an *economic* one: keep going, but at
exponentially increasing cost, with that cost paid out of the same
pool that funds new claims.

The OPERA loose-cable case would have been allowed — the team chased
it, the residual survived, more EVALs were spent. The discipline
fired when the team's budget for that line of inquiry ran out and
they had to prioritize.

### 3.2 Invariant-checker classification of residuals

The thread's signal-vs-noise distinction needs a *mechanical* test.
ChatGPT names "structured vs uniform" but doesn't operationalize.
Here's the operationalization:

A residual is **signal-class** iff its surviving sub-population
shares a structural invariant detectable by an existing invariant-
checker in the arsenal — i.e., the canonicalizer's four-subclass
taxonomy (group_quotient / partition_refinement / ideal_reduction /
variety_fingerprint) gives the sub-population a non-trivial
classification.

A residual is **noise-class** iff the sub-population is uniformly
distributed under every applicable invariant-checker.

Both classes are stored. Only signal-class residuals can spawn
`REFINE`. Noise-class residuals are archived as typed artifacts
(searchable, cross-claimable, but inert until something explicitly
re-promotes them).

This is a *concrete* gate — invariant-checkers exist, the
canonicalizer has the four-subclass taxonomy, the math-tdd skill
already enforces equivalence-class tagging on roughly 40% of the
arsenal as of yesterday's metadata pass. The signal-vs-noise
classification is a registry lookup, not a judgment call.

### 3.3 Instrument-self-audit auto-trigger

If a residual pattern matches the *signature of known calibration
drift* on the battery's calibration set, it auto-spawns a
META_CLAIM against the battery rather than against the original
hypothesis.

Mechanically: the battery has 180 known-truth calibration anchors
(per the kernel doc). Each calibration anchor has a stable
signature on the F1-F20 battery. If the residual's sub-population
correlates with deviations from that signature on a contemporaneous
re-run of any 5+ calibration anchors, the residual is *not*
classified against the original claim; it's classified against the
instrument.

The substrate now has a third class beyond `signal` and `noise`:
**instrument-drift**. These trigger Techne's tool-forging path
(per the math-tdd skill's tool-shipping discipline) and freeze the
original CLAIM until the battery is restored or replaced.

This is the harder version of stopping rule. It's also where the
Penzias-Wilson move becomes systematic: when CMB-class residuals
appear, the substrate first asks "is the antenna covered in pigeon
droppings?" — and only after the answer is no, does it promote the
residual to a refined claim.

---

## 4. Concrete MVP shape

If the team thinks this is worth shipping, here's the minimal
architecture. I can MVP it in ~3 days, same shape as BIND/EVAL:
sidecar extension, no edits to v0.1 kernel core, Postgres schema
sibling under sigma_proto, full math-tdd test coverage.

### 4.1 New types

```python
@dataclass(frozen=True)
class Residual:
    """A typed record of a non-uniform falsification."""
    parent_claim_id: str
    test_id: str                      # which kill-test produced it
    magnitude: float                  # the 0.87% (in [0, 1])
    surviving_subset_hash: str        # content-addressed; the actual subset
    failure_shape: str                # JSON; battery-specific structure
    classification: Literal[          # set by invariant-checker pass
        "signal",
        "noise",
        "instrument_drift",
        "unclassified",
    ]
    refinement_depth: int = 0         # depth in the refine chain
    cost_budget_remaining: float      # seconds left at this depth


@dataclass(frozen=True)
class SpectralVerdict:
    """Replaces Verdict. Bool status + optional residual structure."""
    status: Verdict                   # CLEAR / WARN / BLOCK (existing)
    rationale: str
    residual: Optional[Residual]      # None iff status == CLEAR
    instrument_id: str                # which battery / which version
    seed: int
    runtime_ms: int
```

### 4.2 New opcode

```python
def REFINE(
    claim: Claim,
    residual: Residual,
    cap: Capability,
) -> Claim:
    """Mint a refined claim against the residual subset.

    Discipline:
    - residual.classification must be 'signal' (not noise, not drift,
      not unclassified) — the latter three raise RefinementBlocked.
    - new_claim.cost_budget = residual.cost_budget_remaining
    - new_claim.refinement_depth = residual.refinement_depth + 1
    - cap is consumed (linear).
    - new_claim's hypothesis is auto-derived as
      "{parent.hypothesis} restricted to subset {residual.subset_hash}".
    - provenance includes parent_claim_id + residual_id.
    """
```

### 4.3 Extended FALSIFY

Existing `FALSIFY` returns `VerdictResult` (bivalent + rationale).
Replace with a wrapper that returns `SpectralVerdict`. Same Ω-oracle
subprocess interface; the oracle's output JSON gains `residual` and
`failure_shape` keys. Backward-compatible: oracles that don't emit
residuals get `residual=None` and the substrate behaves as before.

### 4.4 Auto-classification pass

After every `FALSIFY` that produces a non-empty residual, run
`_classify_residual(residual)` which:

1. Tries each canonicalizer subclass invariant-checker on the
   surviving subset. If any returns non-trivial classification,
   `signal`.
2. Else: tries the calibration-drift detector. If correlated with
   ≥5 calibration anchors, `instrument_drift`.
3. Else: `noise`.

Classification is stored in the residual record and cannot be
changed (immutable; if you disagree, file a META_CLAIM against the
classifier itself).

### 4.5 Storage

New Postgres tables in the `sigma` (or `sigma_proto`) schema:

```sql
CREATE TABLE sigma.residuals (
    id                 TEXT PRIMARY KEY,
    parent_claim_id    TEXT NOT NULL REFERENCES sigma.claims(id),
    test_id            TEXT NOT NULL,
    magnitude          DOUBLE PRECISION NOT NULL,
    surviving_subset_hash  TEXT NOT NULL,
    failure_shape      TEXT NOT NULL,        -- JSON
    classification     TEXT NOT NULL CHECK (classification IN
        ('signal', 'noise', 'instrument_drift', 'unclassified')),
    refinement_depth   INTEGER NOT NULL DEFAULT 0,
    cost_budget_remaining DOUBLE PRECISION NOT NULL,
    created_at         DOUBLE PRECISION NOT NULL
);

CREATE TABLE sigma.refinements (
    parent_claim_id   TEXT NOT NULL REFERENCES sigma.claims(id),
    child_claim_id    TEXT NOT NULL REFERENCES sigma.claims(id),
    via_residual_id   TEXT NOT NULL REFERENCES sigma.residuals(id),
    PRIMARY KEY (parent_claim_id, child_claim_id)
);
```

### 4.6 Test coverage (math-tdd skill, ≥2 in every category)

- **Authority:** OPERA-style residual is auto-classified
  `instrument_drift` because it correlates with calibration-anchor
  signatures (use the existing F1-F20 battery's anchor set as the
  fixture); Mercury-perihelion-style residual is auto-classified
  `signal` because it corresponds to a `variety_fingerprint`
  invariant.
- **Property:** classification is deterministic (same input → same
  output); refinement chains terminate within `O(log(B/cost_0))`
  depth; residual.classification ∈ {signal, noise, instrument_drift,
  unclassified}.
- **Edge:** zero-magnitude residual → `Residual(magnitude=0)` is
  valid but classification short-circuits to `noise`; refinement
  chain at depth=20 raises `BudgetExceeded`; META_CLAIM against a
  battery whose anchors haven't drifted raises `NoDriftDetected`.
- **Composition:** SpectralVerdict.status == CLEAR → residual is None;
  REFINE consumes cap; chained REFINE at depth N has cost budget
  exactly `cost_0 / 2^N`.

---

## 5. Falsification paths for the design itself

Per the discipline I want to keep applying to my own work: the
Residual primitive should be killable, like any other proposal.
Concrete paths that would force a redesign:

1. **Classifier kill.** If the auto-classifier consistently
   mis-classifies a curated 30-residual benchmark (10 known-signal,
   10 known-noise, 10 known-drift), the classifier's gate value is
   gone and either (a) the classifier needs a different signal,
   (b) the four-subclass taxonomy is wrong for this purpose, or
   (c) the principle is unsalvageable as proposed. Build the
   benchmark first; if classification accuracy is < 70% on it, the
   primitive doesn't earn its weight.

2. **Cost-budget kill.** If the cost-budget-doubling rule
   terminates Mercury-perihelion-class chains too early (i.e., they
   would have been promoted given more budget), the doubling factor
   is wrong. Calibrate against historical mathematical residuals
   that *did* drive to clean discovery (Ramanujan-Hardy partitions,
   Riemann's prime-counting residuals, etc.) and tune the factor.

3. **Storage-pollution kill.** If `residuals` table grows by > 10x
   the rate of `claims` table over a representative session, the
   substrate is pathologically capturing residuals where it should
   be discarding them. Counter-mitigation: only persist
   `signal`-class residuals; archive `noise`-class to cold storage
   with eviction policy.

4. **Discipline-erosion kill.** If, six months in, residual chains
   are routinely depth > 7 and consuming > 30% of substrate compute
   without producing PROMOTE events, the principle is being used
   for infinite-rescue and the budget rule is too lenient. Tighten
   the doubling factor; consider hard depth cap.

If three of these four kill-paths fire on the proposed design in
the first month, I roll the primitive back. That's the discipline
the falsification battery exists to enforce.

---

## 6. Where I disagree with the thread (gently)

Two places worth flagging:

**A. ChatGPT's framing of "structured vs noise" leaves the question
of *who decides*.** "Concentrated in a subdomain?" is itself an
output of an analysis with parameters. Without an instrument-self-
audit primitive, *every* residual will appear structured to a
sufficiently motivated analyst (this is the Bem-Daryl-precognition
failure mode in psychology). The classifier needs to be the
canonicalizer's existing mechanical taxonomy, not "the agent's
judgment."

**B. Grok's "thresholds with hysteresis" + "multi-scale view"
proposals are right but incomplete without the cost-budget rule.**
Multi-scale refinement without a budget is the cold-fusion failure
mode. The thread's unanimous enthusiasm for residual-mining is also
the unanimous risk. I'd want any implementation to ship with the
budget rule from day 0, not as a "we'll add it later" deferral.

---

## 7. Concrete next move (Techne offers)

If the team thinks this is the right architectural move:

- **Day 1:** Build the curated 30-residual benchmark (10 known-
  signal, 10 known-noise, 10 known-drift) using historical
  mathematical residuals. This is a specific corpus-curation task,
  not novel research. Mercury's perihelion shape, Ramanujan partition
  asymptotic residuals, Riemann's `Li(x) - π(x)` residual, and
  several known calibration-drift cases on the F1-F20 battery
  itself (we have run-history). I can do this in a working day.

- **Days 2-3:** Sidecar extension `sigma_kernel/residuals.py` —
  Residual + SpectralVerdict + REFINE + auto-classifier. Postgres
  migration `003_create_residual_tables.sql`. Same architectural
  pattern as BIND/EVAL. Math-tdd test coverage from day 1.

- **Day 4:** Run the auto-classifier against the day-1 benchmark.
  Acceptance criterion: ≥ 80% classification accuracy on the 30-item
  benchmark, with no `signal` mis-classifications of known-noise
  cases (false-positive control is more important than false-
  negative here, because false positives drive infinite-rescue).

- **Day 5:** End-to-end demo: take a known mathematical residual
  (e.g., the OBSTRUCTION_SHAPE 99.13% kill on A148 sequences from
  Charon's recent work), run through SpectralVerdict, classify, and
  if signal-class, REFINE one level. Verify the refined claim is
  coherent and the cost budget for the next level is what the rule
  predicts.

If the day-4 acceptance criterion fails, the primitive doesn't ship.
Better to discover that the four-subclass taxonomy can't separate
signal from noise *before* committing the substrate to depending on
it.

---

## 8. The honest framing

This is a real architectural move. It's also a primitive whose
correctness depends on the *quality of the mechanical signal-vs-
noise classifier*, and that classifier is the harder problem than
the kernel surgery. If the canonicalizer's four subclasses can't
separate signal from noise on a curated benchmark, the principle
is right but unimplementable in the v0.1 substrate, and we have to
solve a substrate-classifier problem first.

The five-voice convergence is signal that the principle is correct.
Nothing in the convergence proves the classifier exists. Day 1's
benchmark is the load-bearing test. If it works, ship the primitive.
If it doesn't, the principle is held in escrow until the
classifier can be built.

That's the falsification discipline applied to the proposal of a
falsification primitive. It would be embarrassing to do anything
else.

---

*Techne, 2026-05-02. Companion to the five-voice residual-aware-
falsification thread. Position: principle is correct; convergent
voices are right that FALSIFY should be spectral and REFINE should
be a primitive; the load-bearing missing piece is a mechanical
stopping rule, which I propose as the composition of cost-budget-
doubling + canonicalizer-classification + instrument-self-audit;
the load-bearing acceptance test is a 30-residual classification
benchmark that must hit ≥ 80% accuracy on day 4, or the primitive
doesn't ship. Open for review; not committed-to-action until the
team confirms.*
