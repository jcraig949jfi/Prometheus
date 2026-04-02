# Charon North Star
## What Does the Spectral Tail Encode?

---

## The Question

We proved the rank signal in L-function zeros lives in positions 5-19 (the spectral
tail), not in the central vanishing point. Three theoretical frameworks explain WHY
this works (ILS support theorem, Katz-Sarnak global rigidity, Deuring-Heilbronn
uniform mean shift). None of them explain WHAT specific mathematical structure the
spectral tail is measuring that makes rank-similar objects cluster.

The search tool finds things that are spectrally similar. We don't fully understand
what "spectrally similar" means yet. The north star is closing that gap.

## The Strategy: Decompose the Spectral Tail Layer by Layer

Each experiment strips a known mechanism. Either the spectral tail reduces entirely
to known components — in which case we've built the first empirical decomposition
of what L-function zero geometry measures. Or there's a residual after all known
mechanisms are stripped — in which case we've found something the theory doesn't
yet explain.

Either outcome is the paper.

---

## The Four Experiments

### Experiment 1: Higher Resolution (100+ Zeros)
**What it strips:** Truncation artifacts. Resolution limitations.

Pull 100+ zeros per object from LMFDB (most objects have them). Rebuild the
spectral tail as zeros 10-100 instead of 5-19. Re-run the ablation at finer
granularity: which specific zero range carries the most rank information?

**What survival means:** The signal isn't an artifact of our 20-zero truncation.
The structure persists or sharpens at higher resolution. The optimal feature
range becomes precise.

**What collapse means:** The signal was noise amplified by sparse data. The 20-zero
window happened to hit a sweet spot. Reset expectations.

### Experiment 2: Dirichlet Character Zeros as Repulsion Source
**What it strips:** The Deuring-Heilbronn character repulsion mechanism.

Ingest Dirichlet characters and their L-function zeros. For each dim-2 MF with
non-trivial character χ, test whether the MF's position in zero-space is PREDICTED
by the zeros of L(s,χ). If the character's standalone zero distribution explains
the MF's spectral position, the geometry reduces to character convolution.

**What survival means:** The spectral tail geometry is NOT just character repulsion.
Something else is structuring the zero positions beyond what the character dictates.

**What collapse means:** The spectral tail is measuring character repulsion effects.
The "rank geometry" is actually "which character twisted this form and where are
that character's zeros." Interesting but fully explained.

### Experiment 3: Conductor Scaling Gradient
**What it strips:** Pre-asymptotic uniformity.

The character anomaly research showed N_eff ≈ 1.3 at conductor 5000. ALL symmetry
types look orthogonal at this scale. Test: does the spectral tail ARI vary with
conductor? Bin existing data (or pull conductor 10K-50K) and check.

If ARI is flat across conductor: the signal is intrinsic to the zero geometry.
If ARI decreases with conductor: pre-asymptotic uniformity was carrying us, and
the signal weakens as symmetry types separate.
If ARI increases with conductor: more data sharpens the signal. Scale up.

**What survival means (flat or increasing):** The spectral tail structure is not
an artifact of pre-asymptotic symmetry-type blending.

**What collapse means (decreasing):** The geometry works because everything looks
the same at low conductor. Not a real coordinate system — a pre-asymptotic accident.

### Experiment 4: Inner Twist Decomposition
**What it strips:** Algebraic pseudo-self-duality.

The character research says dim-2 forms overwhelmingly admit inner twists that tie
them to trivial-character base forms. Query LMFDB for inner twist data on the 163
EC-proximate forms. Test: do forms with inner twists cluster differently from those
without? Does the inner twist character predict the spectral position?

**What survival means:** The spectral tail carries information beyond inner twist
structure. Something in the zero geometry isn't reducible to "which base form does
this twist back to."

**What collapse means:** The spectral tail is measuring inner twist chains. The
"geometry" is a graph of twist relationships visualized through zeros. Still useful
as infrastructure but fully algebraically explained.

---

## The Residual

After stripping all four layers — truncation, character repulsion, pre-asymptotic
uniformity, inner twist structure — either the ARI is fully explained or it isn't.

**If fully explained:** We've built the first empirical decomposition of L-function
zero geometry into its theoretical components. The paper: "We decomposed zero-space
geometry into its theoretical components and showed the ILS prediction holds
empirically. The spectral tail encodes [symmetry type + character repulsion +
inner twist structure], each contributing [X, Y, Z] to the total ARI."

**If there's a residual:** After removing all known mechanisms, some spectral-tail
structure remains that correlates with rank but isn't explained by symmetry type,
character, conductor, or inner twists. That residual is the finding.

## The Prometheus Connection

If a residual exists, it represents a structural transformation of mathematical
objects that preserves spectral-tail similarity but isn't captured by any known
invariant. That's a candidate for a Noesis primitive — an unnamed operation that
both the zero geometry and the Noesis tensor can see from their respective sides.

The honeycomb boundary between Charon and Noesis isn't the graph edge types
mapping to damage operators. It's the spectral tail residual — if it exists —
being the shadow of a structural transformation that both systems can detect.

That's far down the road. The north star for now: strip layers until you either
explain the signal completely or find what can't be explained.

---

## Execution Order

1. **Conductor scaling gradient** (existing data — one afternoon)
   Bin current objects by conductor. Check ARI gradient. Immediate.

2. **Inner twist query** (LMFDB query — one hour)
   Pull inner_twist_count for the 163. Check correlation with EC-proximity.

3. **100+ zeros ingestion** (LMFDB crossing — half day)
   Upgrade zero vectors. Re-run ablation at higher resolution.

4. **Dirichlet character ingestion** (LMFDB crossing — one day)
   New object type. Test character repulsion mechanism directly.

Each result either strips a layer or reveals the residual. The order is
cheapest-first, highest-information-per-token.
