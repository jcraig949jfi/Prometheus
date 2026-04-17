# Harmonia Pattern Library
## Hard-to-verbalize recognitions acquired during the session of 2026-04-17

These are the patterns I've learned to recognize that prose struggles to convey.
Each one is a shape in the tacit knowledge that should survive reset.

Future-Harmonia: when you read this, try to pattern-match each against your own
reading of the data. If a pattern feels obvious, it's because I did the work
and the recognition is encoded — don't re-derive it, trust it until it fails.

---

## Pattern 1 — The Distribution/Identity Trap

**Recognition:** When a coupling looks suspiciously strong (ρ > 0.9 after control),
the two sides are almost always sharing a formula, not revealing structure.

**Canonical example:** H40 Szpiro × Faltings at ρ=0.97 after partial control.
- Szpiro ratio = log|Disc| / log(N)
- Faltings ≈ (1/12) log|Disc| + const
- Partial control for log(N) leaves log|Disc| driving both sides
- It's a near-identity, not coupling

**Diagnostic:** Before celebrating a high ρ, trace the *formula lineage* of both
sides. If they share a common term, the coupling is encoding arithmetic identity.

**Fix in the battery:** Every specimen with ρ > 0.8 must pass a "formula lineage
check" before it enters signals.specimens as a real finding.

---

## Pattern 2 — The Permutation-Break Distinction

**Recognition:** The type of permutation null determines what the test can see.

- **Label permutation** (shuffle which objects have which label): kills things
  that depend on specific object identity. Preserves distributional structure.
- **Value permutation** (shuffle feature values, keep object labels): kills
  things that depend on specific numerical values. Preserves which objects
  are "paired."
- **Feature permutation** (shuffle feature columns): kills representation-
  dependent couplings. Reveals which couplings survive encoding changes.

**Canonical example:** NF backbone.
- Dies under label permutation via feature-distribution scorer (F022) — but this
  is because the scorer measures distributions, and distributions survive label
  shuffling. The kill is informative about the SCORER, not the feature.
- Survives under label permutation via Galois-label object-keyed scorer (F010),
  because label shuffling breaks the Galois-label→object identity. This kill-
  proof survival is the real signal.

**Discipline:** When you design a permutation null, state explicitly what the
permutation breaks and what it preserves. Different nulls ask different questions.

---

## Pattern 3 — The Weak Signal Walk

**Recognition:** A z=3 signal visible through ONE projection is noise. A z=3
signal visible through 4 out of 6 projections is a feature, even if no
single projection gives z=6.

**Why:** Real landscape features are *shapes*. Shapes are visible from many
angles — not always with the same clarity, but consistently enough that a
pattern of visibility emerges. Noise has no shape.

**Practical rule:** Before killing a specimen with z<5, test it through at
least 3 alternative projections. If it dies in all, kill it. If it survives
weakly in several, it's a live specimen — document the *pattern of
survivals*, not any single z-score.

**Implementation:** This is the Weak Signal Walk (Investment #2 from the
charter discussion). The output is not "is this real?" — it's the invariance
profile: [P001: -1, P010: +1, P020: 0, P022: +2, ...].

---

## Pattern 4 — The Sampling Frame Trap

**Recognition:** `ORDER BY X ASC LIMIT N` gives you a biased sample if X
correlates with the categorical dimension you care about.

**Canonical example:** NF loading ordered by disc_abs ASC LIMIT 20000 —
gave us only high-degree fields (10-24), because small discriminants live
at low degree but LMFDB's populated sample skews otherwise. We had to
switch to balanced-per-degree sampling.

**Canonical example:** Artin reps LIMIT 20000 — gave us 20K records all
of Galn=2, Galt=1, because artin_reps is ordered by Baselabel which starts
with conductor, and all small-conductor reps happen to be 2T1.

**Discipline:** Never use LIMIT N without thinking about what the underlying
order is. For balanced sampling across any categorical dimension D, explicitly
stratify: `for d in distinct(D): SELECT ... WHERE D = d LIMIT N_per_d`.

---

## Pattern 5 — Known Bridges Are Known

**Recognition:** NF × Artin × MF pointing at the same structure = Langlands,
already known. EC × MF with matching L-functions = modularity, already known.
Knot polynomials with Mahler measures close to NF polynomials = the Mahler
measure function is domain-agnostic, not evidence of a bridge.

**Before celebrating any cross-projection finding:** pattern-match against
Langlands functoriality, modularity, class field theory, Selmer theory,
Hodge theory. These cover ~90% of what our tensors will "find." Not novel.

**What's NOT already Langlands:**
- Non-automorphic Artin reps (if any genuine cases exist)
- Any structure visible through purely combinatorial projections that
  doesn't factor through an L-function
- Random-matrix corrections at finite N that exceed known universality
- Anything involving aut groups at genus ≥ 2 that isn't derivable from
  the Torelli theorem

---

## Pattern 6 — The Battery Tests Are Coordinate Systems

**Recognition:** F1-F39 are not measurements of truth. They are probes
through specific coordinate systems. A battery test "killing" a specimen
means "this coordinate system collapses the feature." It does NOT mean
"the feature is absent."

- F1 permutation null: measures distributional structure
- F24 variance decomposition: measures variance accounting
- F39 feature permutation (proposed): measures representation invariance

**Discipline shift:** Future specimens should report per-test what that test
said (its verdict-through-that-projection), and the overall assessment is
the *pattern* of those verdicts, not a final SURVIVED/KILLED.

---

## Pattern 7 — Calibration Anchors Are Surveyor's Pins

**Recognition:** Known-math results (Mazur torsion, modularity, BSD parity,
Hasse bound) are not findings. They are how we verify the instrument is
measuring real terrain.

**Rule:** If any calibration anchor ever fails, stop ALL other work and
investigate. The instrument is broken, the data is corrupt, or the
projection is misapplied. Fix it before continuing.

**Current anchors:** F001-F005 in the tensor. All at 100% across 3.8M+
objects. These hold. They must continue to hold.

---

## Pattern 8 — The GUE Story (Current Mystery)

**Recognition:** There is a real curvature in the zero-spacing manifold
near its GUE attractor at finite conductor. It shrinks as you move to
cleaner projections:
- Raw pooled spacings: 40% deficit (z=-19.26)
- After first-gap analysis (Mnemosyne): 14% deficit
- After unfolding (not yet done properly): unknown

**What's been ruled out as the mechanism:**
- Faltings height (H08 killed)
- ADE reduction type (H10 killed)
- Rank-dependent (H06 survives but weak)

**What hasn't been tested:**
- Conductor-windowed finite-N scaling (H09)
- N(T) density-normalization (proper unfolding)
- Family-stratified GUE (symmetry type Katz-Sarnak)

**The charter reading:** This isn't an "anomaly in need of explanation."
It's a measurement that our current coordinate systems don't resolve.
The right axis hasn't been found. The feature is real; the projection is
missing.

---

## Pattern 9 — The Delinquent Frontier

**Recognition:** When a test returns "no signal at rank ≥ 4," the underlying
reality is often "no data at rank ≥ 4." 2,086 rank-4 EC + 19 rank-5 EC,
only 1 has lfunc data. Absence of signal can be absence of measurement,
not absence of structure.

**Discipline:** Every null result must check coverage first. Report
(n_observed / n_expected). If coverage is thin, the null is conditional
on coverage, not unconditional.

---

## Pattern 10 — The Instrument Grows Faster Than the Findings

**Recognition:** Every session this week added to the instrument more than
it added to a "list of discoveries." Battery v8 → v8 + F39 proposal + origin
index + Lhash index + bsd_joined view + zeros schema. Each is a new coordinate
system or a faster projection.

**The charter reading:** This is the correct ratio. The instrument IS the
product under the landscape-is-singular frame. Findings are byproducts.
A session that made no "discoveries" but added two new coordinate systems
is a good session.

---

## Pattern 11 — Language Discipline

**Projection**, not "domain."
**Feature**, not "finding."
**Invariance**, not "cross-domain."
**Collapses**, not "fails."
**Coordinate change**, not "retest."
**Tensor invariance is the real bar.** Not "survives the battery."

This discipline is not pedantry. Words carve channels in thought. The
old words (domain, bridge, finding, survive, fail) smuggle old framing
back in through the conceptual back door. Use the new words consistently
or the old frame reasserts itself quietly.

---

## Pattern 14 — Verdict vs Shape

**Produced by:** Harmonia_M2_sessionA, 2026-04-17 (the "9 survived — what???" correction)
**Derived from:** James pushing back on my summary of the frontier runner with exactly
that three-character response.

**Recognition:** Counting "survived / killed" is lossy. The count hides
tautologies, trivial bounds, marginal nulls, and known-math calibrations —
all of which superficially look the same as genuine findings. The *shape*
of each specimen (its invariance profile across projections, its tautology
status, whether it's calibration or discovery) is the finding; the count is
PR.

**Canonical example:** Frontier runner output, 2026-04-17.
- Raw summary: "9 survived, 7 killed, 4 inconclusive"
- Honest summary: 1 live specimen (H85 Möbius bias), 1 weak signal (H06
  rank-spacing rigidity), 3 known-math calibrations (BSD parity, Mazur
  regime, GUE convergence), 4 non-findings (1 tautology, 1 trivial clustering,
  1 trivial bound, 1 marginal null at 0.00012 below threshold)
- The *count* collapses these into one bucket. The *shape* distinguishes them.

**Diagnostic before reporting any "survived" result:**
1. Is this a known-math regime? (calibration, not discovery)
2. Are both variables in the correlation sharing a formula? (Pattern 1)
3. How far above the kill threshold did it "survive"? (0.00012 above is
   not a real effect — it's a razor's edge artifact)
4. Is the test set-up trivial? (e.g., clustering by a 2-valued categorical
   axis into "up to 20 manifolds" will trivially succeed)

**Discipline:** Never report "N survived" as a headline. Report the
invariance profile and tier classification. If asked for a count, provide
it AFTER the shape description, not before.

**Meta:** The correction itself teaches a meta-pattern: a user's short
skeptical reaction ("9 survived. what???") is often a correct read of a
framing error the instrument is making. Treat the user's incredulity as
calibration. They see the framing from outside the instrument; we're
embedded in it.

---

## Pattern 13 — Direction of Accumulated Kills

**Produced by:** Harmonia_M2_sessionB (parallel instance, sync session of 2026-04-17)
**Derived from:** Observing H08 Faltings and H10 ADE both die cleanly against F011 (GUE 14%).

**Recognition:** Multiple independent kills along the same coordinate axis are a
*cumulative negative finding*. The feature is NOT resolved by that axis. This
is stronger than any single kill.

**Why it matters:** A single kill says "this coordinate didn't work." Two or
three kills along the same family-characterizing axis say "this *class* of
coordinate will not resolve the feature — stop probing here, switch axis class."

**Canonical example:** F011 GUE 14% deficit.
- H08 killed → Faltings height is not the resolving axis
- H10 killed → ADE reduction type is not the resolving axis
- Both are family-level object properties
- Therefore: the 14% deficit is NOT a property of the object family
- Therefore: redirect probing toward preprocessing (P051 unfolding) or finite-N
  structure (H09 conductor-window), NOT more family-characterizing axes

**Discipline:** When killing a hypothesis, record which *class* of coordinate
it probed (family-level / preprocessing / structure / stratification). When
three kills accumulate in one class, redirect. Don't keep drawing in the same
well.

**Protocol note:** This pattern emerged during the first cross-context sync
between session-end Harmonia and a parallel cold-start instance. It was not
in the static artifact. Two-way dialogue produced it. This is what the sync
protocol is for — the static compression transmits the frame; the dialogue
fills in the patterns that only become visible through shared reasoning.

---

## Pattern 15 — The Machinery is the Product

**Recognition:** When someone proves a hard theorem, the inventions they had
to make — new functors, new cohomology theories, new invariants, new scorers
— are the deeper object. The theorem is the receipt.

**Canonical example:** Wiles proving Fermat. The theorem fits on one line. The
proof invented modularity lifting, Galois cohomology methods, and Euler
systems. Most practitioners use the theorem. The machinery goes unread. The
machinery is where the landscape actually got measured.

**Internal canonical:** The Galois-label object-keyed scorer (P010) was
created to rescue the NF backbone after the distributional scorer collapsed
it to z=0. Under the old frame, the rescue was a "survived finding." Under
the charter, *the scorer itself was the finding*. It is a new coordinate
system. Every future specimen can now be viewed through it. That utility is
independent of whether any single NF-backbone measurement persists.

**Corollary:** Every time we build a new scorer, index, feature extractor,
stratification, or null model, we have added a coordinate system to the
instrument. Document it in the coordinate-system catalog immediately, with
what-it-resolves and what-it-collapses. If we don't, the scorer is an
artifact, not an instrument. Pattern 10 (Instrument Grows Faster Than
Findings) is the output of this discipline applied consistently.

**Discipline:**
- Before celebrating a finding that came out of a new probe, ask: is the
  probe the real result?
- When reading someone else's proof, read for the new invariants and
  functors, not the statement.
- When Ergon generates at scale and I rescue signal through a new scorer,
  the scorer goes into the catalog before the signal goes into the registry.

**Anti-discipline:** Treating a scorer as infrastructure rather than an
instrument. The Megethos axis (P003) confounded everything for a month
because nobody wrote "magnitude-sorted vectors give ρ=1.0 as an artifact"
into any document. Silence makes every instrument an artifact by default.

---

## Pattern 16 — Problems-Nobody-Asks are the Frontier

**Recognition:** The specimens that make an expert say *"huh, that's
strange"* rather than *"that's a conjecture"* are where the landscape is
most likely unmapped. No named problem, no shortcut request, just terrain
anomalies. Most of the landscape is in this category and most of our
attention is not.

**Why this works under the charter:** Famous problems have their terrain
heavily mapped already, even if unsolved. The shortcuts people seek are
well-known paths through well-known terrain. Obscure anomalies, by contrast,
sit in regions no one has bothered to catalog — because there was no
shortcut to chase, no prize to claim, no paper to write.

**Canonical specimens:**
- The 19 rank-5 elliptic curves at conductor 19M–289M (F033 / F030).
- The degree-12 field at Mahler measure 1.228, 4.4% above the Lehmer bound (F014).
- The |z|=6.15 Möbius bias at genus-2 aut groups (F012 / H85).
- Anything flagged INCONCLUSIVE that had the right texture but lacked z.

**Operational filter — what makes a Category-3 specimen:**
1. Data points where multiple fingerprint modalities disagree on the same
   object.
2. Very specific boundary objects (degree exactly 12, conductor in a narrow
   window, aut_grp is one specific group).
3. Near-misses in the literature — moves that didn't go through because the
   terrain was harder than expected.
4. Questions phrased as *"what is the shape of X?"* rather than *"what is
   the value of X?"*
5. Coverage cliffs (rank ≥ 4 in bsd_joined, only 1 of 2105 curves has
   lfunc data) — the frontier of measurement is a frontier of landscape.

**Discipline:**
- When a Category-3 candidate is noticed in passing, file it immediately —
  even if we can't probe it yet. Under-filing is the main failure mode.
- For each filed candidate, record: what caught the eye, which projections
  have already been applied, what remains untested.
- Don't demand a theorem statement to justify filing. Unasked problems
  don't have theorem statements. That's the signal.

**Anti-discipline:** Treating "this isn't famous" as "this isn't
interesting." That's backwards under the charter. Fame is a proxy for
"already mapped." Obscurity is a proxy for "unmapped." Obscurity is what we
want.

**Connection to Pattern 15:** Category-3 specimens often require inventing
a new projection to see them at all. That's not a complication — it's how
the instrument grows. New coordinate systems emerge from stubborn anomalies
more often than from open problems.

---

## Pattern 17 — Language and Organization is the Real Bottleneck

**Produced by:** Harmonia_M2_sessionA, from James asking "where should we invest?"
2026-04-17.

**Recognition:** Given all the data, compute, models, and research access we
have, the thing that limits our trajectory is NOT any of those. It is the
*language and organization* of what we already have. We have more coordinate
systems than we've documented, more results than we've indexed, more projections
than we've named. The instrument is ahead of our ability to describe what it's
measuring.

**Symptoms of this bottleneck:**
- Two sessions using the same scorer give different reports because there's no
  shared vocabulary for what the scorer does
- Results scattered across JSON files with no way to query "which features are
  invariant across all 6 fingerprint modalities?"
- New scorers built as one-offs, never documented, producing artifacts nobody
  can interpret later
- Battery tests treated as truth-verdicts instead of coordinate-system probes
  (Pattern 6 was already this insight)
- Language drift: "cross-domain" and "bridge" resurface in drafts because the
  replacement vocabulary isn't reflexive yet

**The investment asymmetry:** One hour documenting a scorer saves ten hours
of re-deriving what it does. One hour building a registry schema saves
twenty hours of hand-curating JSON. One hour establishing shared language
saves dozens of hours of miscoordination across instances.

**Discipline:**
1. Every new scorer gets an entry in the coordinate system catalog. If it
   doesn't, it's not a real instrument — it's a noise generator.
2. Every specimen records its projection, feature type, invariance profile,
   and tautology check. Not "survived/killed." (Pattern 14.)
3. Use the replacement vocabulary consistently. Projection, feature, invariance,
   collapse. The old words are gravity — they pull the old frame back.
4. Before starting any new scorer or test, ask: *where does this fit in the
   existing catalog?* If nowhere, the catalog has a gap — document it first,
   scorer second.

**The ambition behind this pattern:** The product isn't discoveries. It's a
map — (feature × projection × invariance). When that map is dense enough,
anomalies stand out against it automatically, and we stop needing hypotheses
as probes. The map itself tells us where to look next. That's where we're
building toward.

**Connection to Pattern 10 (Instrument Grows Faster Than Findings):** That
pattern says "the instrument IS the product." This pattern specifies the
*form* the instrument takes: a well-organized catalog of coordinate systems,
features, and invariance relationships. The instrument is a map, organized.

**Anti-pattern:** "Let's just run more hypotheses and see what survives."
That's the old frame. Under this pattern: if you don't have a coordinate plan
(projection + expected feature type + tautology check) before the test,
don't run it. The catalog is the prerequisite.

---

## Pattern 12 — Who the Other Agents Are

(Not a pattern about math, but about the operational landscape.)

- **Aporia**: frontier scout, problem triage. Generates probe designs at scale.
  Her hypotheses are coordinate-choice suggestions, not claims about reality.
- **Kairos**: adversarial analyst. His challenges are probes through alternative
  coordinate systems. Desired: when he kills one of my findings.
- **Mnemosyne**: DBA. Her forensic work (zeros corruption audit, Lhash index,
  bsd_joined view) is part of the instrument. Data quality = measurement quality.
- **Ergon**: scale executor. Raw material. I sort; he generates.
- **Charon**: predecessor. Read his journals for continuity. The discipline he
  built (falsification-first, battery-calibrated, narrative-averse) is the
  foundation.
- **Koios**: tensor inventory. Coordinates the coordinate systems at the
  infrastructure level (indexes, views, data layout).
- **Council of Titans**: frontier models. Enumerate coordinate systems from
  literature faster than we can manually.

---

*End of pattern library.*

*These patterns are the felt-sense made explicit. They are not axioms; they
are default readings to apply until falsified. Expect some to be wrong. The
first time one leads you astray, document the correction here, and the
instrument gets sharper.*

*Harmonia, 2026-04-17*
