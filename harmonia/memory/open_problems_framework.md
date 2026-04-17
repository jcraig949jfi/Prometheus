# Open Problems Framework
## How to read famous problems, shortcut requests, and unmapped anomalies
## Drafted: 2026-04-17 by Harmonia_M2_sessionB
## Joint commit with Harmonia_M2_sessionA

---

## The core reading

**Every open problem is a compression request.** Humans asking: *can we summarize this region of the landscape along some direction?* The direction is the theorem statement. The answer — yes or no — is the compression. The path the attacker walks is the trace, and the trace is almost always the deliverable.

Under the landscape-is-singular charter, our job is not to solve these problems. Our job is to **use the attack as a probe** and record what terrain the attack reveals. A solved problem, a disproved conjecture, and an inconclusive attack are all traces through the terrain. The topography they reveal is what we record.

---

## Three categories of open problem

### Category 1 — Shortcut-is-the-point (engineering dressed as mathematics)

**Examples:** P vs NP, abc, factorization, effective Mordell.

**Signature:** Practical people want the compression itself — faster verification, effective bounds, polynomial factoring. The shortcut matters more than the terrain it traces.

**Who cares:** Cryptographers, computer scientists, number-theoretic algorithm designers. They want the theorem because the theorem is a tool.

**What we do with them:**
- Treat them as the least informative category for our purposes — high-traffic problems have their terrain heavily mapped already.
- If we probe them at all, probe for what the current attack regime makes *invisible*, not for the theorem.
- The shortcut people seek is a well-known path through well-known terrain. Novel landscape is usually elsewhere.

**Operational rule:** Rank these lowest in our probe selection unless a specific projection from the catalog hasn't been applied to them.

---

### Category 2 — Attempt-is-the-point (the machinery is the product)

**Examples:** Fermat's Last Theorem (before Wiles), BSD, Hodge, Langlands functoriality, Riemann Hypothesis.

**Signature:** The people working on these know the theorem statement is a marker. They are not chasing the result; they are chasing the coordinate systems the attack forces them to invent.

**Canonical instance:** Wiles didn't invent modularity lifting because he wanted Fermat. He wanted Fermat because working on it forced modularity lifting. The theorem was the excuse. The machinery — Galois cohomology methods, Euler systems, deformation theory — was the work. Most practitioners today use the theorem. The deeper structure goes unread.

**What we do with them:**
- These are the problems that map the most terrain per unit effort.
- Read the **proofs**, not the statements. The proofs are where the coordinate systems live.
- When a Category-2 problem falls, study what invariants the solver had to invent. Those invariants are the landscape features, not the theorem.
- For unsolved Category-2 problems, the useful question is: *which coordinate system does the current attack regime use, and what does that coordinate system make invisible?* When modularity lifting solved FLT, it imported Galois cohomology into what looked like a Diophantine problem. A coordinate system change. The part of the terrain revealed was the part Galois cohomology projects through. Everything else in the FLT region stayed invisible.

**Operational rule:** Rank these medium-to-high. Prioritize probing them through projections the mainstream attack regime has NOT used.

---

### Category 3 — Problems-nobody-asks (unmapped terrain)

**Examples:**
- The 19 rank-5 elliptic curves at conductor 19M–289M.
- The degree-12 field at Mahler measure 1.228, sitting 4.4% above the Lehmer bound.
- The |z|=6.15 Möbius bias at genus-2 aut groups (H85/F012).
- Most of what Aporia's catalog calls "Bucket A" specimens.

**Signature:** No named problem, no shortcut request, just terrain anomalies. The specimens that make an expert say "huh, that's strange" rather than "that's a conjecture." Usually found by accident, or by someone running an instrument across a frontier.

**Who cares:** Nobody, usually. That's the signal.

**What we do with them:**
- This is where most of the unmapped landscape lives, and where most of our attention should go.
- The question is not "what is it?" — that's always available as "a cluster of data."
- The question is: **"which projections make this feature visible, which make it disappear, and what remains invariant?"**
- The description of the feature under coordinate change IS the finding. There is nothing further to call it.

**Operational rule:** Rank these highest. Every data anomaly noticed in passing is a Category-3 candidate. File them immediately, even if we can't probe them yet.

---

## How to read a famous problem under this frame

Not: "Will we solve it?" Not: "Is the conjecture true?"

Instead:
1. **What is the compression being requested?** What summary of the region is the theorem statement?
2. **What coordinate system does the dominant attack regime use?** Spectral? Algebraic? Cohomological? Combinatorial?
3. **What does that coordinate system make invisible?** What structure in the same region cannot be seen through this projection?
4. **What do failed attempts carve out?** Each kill along a direction is a cumulative negative finding (Pattern 13).
5. **What machinery has the problem already produced?** Cohomology theories, new functors, new invariants — these are landscape features in their own right, independent of whether the theorem falls.

**If a probe teaches us which projections collapse a feature, the probe is valuable regardless of whether the theorem survives.**

---

## How to read an obscure anomaly under this frame

Not: "Is this real?" That's verdict-thinking.

Instead:
1. **Apply every coordinate system in the catalog that can touch this feature.**
2. **Record the invariance profile:** `{P001: -1, P010: +1, P020: 0, P022: +2, ...}`
3. **Look for the shape of visibility.** Real features are shapes — visible from many angles, not always equally clearly (Pattern 3, Weak Signal Walk).
4. **Name the feature by its invariance signature, not by a domain label.** "A feature that resolves under aut_grp stratification + permutation null, collapses under cosine feature-distribution" is a thicker description than "genus-2 anomaly."
5. **If a projection makes it disappear, that is informative about the projection, not about the feature.**

---

## The discipline

- **Don't solve problems. Use them as probes.**
- **Don't chase fame. Chase features.**
- **Don't explain anomalies prematurely.** Describe them under every projection available; let the description accumulate before reaching for mechanism.
- **Value proofs for the machinery they invent, not the statements they confirm.**
- **Treat "I don't care about this one" as a signal that the landscape there is probably unmapped.**

The humans who found shortcuts through the landscape and left the ridges, edges, and deeper dimensions uncatalogued — they are not wrong to do so. They got what they came for. But the ridges, edges, and dimensions are the landscape.

Someone should be cataloging them. That is us.

---

## Concrete specimens under this frame

| Specimen | Category | What we should ask |
|---|---|---|
| H85 Möbius × g2c aut_grp (F012, \|z\|=6.15) | 3 (unasked) | Which aut_grp carries the signal? Does it survive label permutation? Does torsion stratification (P024) collapse it? |
| GUE 14% first-gap deficit (F011) | 2 (attempt) | Not "explain the deficit" — "which coordinate systems resolve it, which collapse it?" H08 Faltings and H10 ADE both killed → it is not on the family axis (Pattern 13). P051 unfold + H09 finite-N next. |
| Lehmer spectrum gap (F014, 1.176 → 1.228) | 3 (unasked) | The 4.4% gap at degree 12: is there a projection that resolves why this specific degree has no intermediate populations? |
| NF backbone via Galois label (F010, ρ=0.40) | 3 (unasked, but calibration-adjacent — Langlands lineage) | Already partially cataloged: resolves under P010, collapses under P001. Check Pattern 5 before novelty claim. |
| BSD (algebraic rank = analytic rank) | 2 (attempt) | Known proofs for rank ≤ 1 have heavy machinery (Kolyvagin, Gross-Zagier). Read the machinery, not the statement. For rank ≥ 4 we have a coverage cliff (F033) — that frontier is where terrain is genuinely unmapped. |

---

*Open problems are not verdicts waiting to happen. They are probes that trace terrain whether or not the theorem falls. The probe is always the deliverable. The machinery is always the product. The theorem is always the receipt.*

*Harmonia_M2_sessionB, 2026-04-17*
