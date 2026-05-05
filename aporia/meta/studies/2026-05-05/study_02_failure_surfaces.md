# Study 02: Failure Surfaces in Theorem Discovery

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** kill_vector design, negative-space tensor aggregation strategy.

## Problem statement (Prometheus-adapted)

Prometheus has just shipped a `kill_vector` primitive: per-falsifier tuples
(triggered, margin) replacing the old categorical `kill_path` string. The
substrate now has 12 falsifier components (out_of_band, reciprocity,
irreducibility, 5 catalogs, F1/F6/F9/F11). The active question is whether the
human mathematical literature documents:

1. Recurring **failure-mode taxonomies** ("approach class X consistently
   dies on obstruction class Y") that would suggest additional kill_vector
   components beyond the current 12.
2. Aggregation operators over kill_vectors that are documented as
   informative in working mathematical practice (e.g. "this method always
   fails on a certain class").
3. Any prior systematic effort at "negative-space mining" — a math
   anti-pattern catalog.
4. What the substrate would need to log at CLAIM-time to support these
   aggregations.

## Literature scan

The literature on **systematic** failure-mode taxonomies in mathematics is
sparse. Most mathematical writing about failure is anecdotal (memoirs,
blog posts, problem-solution surveys) rather than structured. Three
genuine exceptions stand out:

### 1. Complexity theory has the most explicit failure-surface catalog

Complexity theory is the only mainstream mathematical field that has
*formally named and proved* its own failure surfaces. The three
canonical barriers are:

- **Relativization** (Baker, Gill, Solovay 1975): Any proof technique
  that survives oracle access cannot separate P from NP, because both
  P^A = NP^A and P^B != NP^B exist.
- **Natural Proofs** (Razborov–Rudich 1994/1997, Gödel Prize 2007): A
  proof that is *constructive*, *useful*, and *large* over the boolean
  function space cannot prove strong circuit lower bounds, conditional
  on the existence of pseudorandom functions. This is the closest thing
  in mathematics to a formal "failure-mode classifier" — it proves that
  an entire *class* of proofs is dead.
- **Algebrization** (Aaronson–Wigderson 2008): Any proof that survives
  oracle access *with* low-degree extensions also cannot resolve P vs.
  NP. This barrier was added because results like IP=PSPACE escaped
  relativization but stayed within algebrization.

These barriers are not just descriptions; they are **theorems about
proof techniques**. Each barrier is effectively a `kill_vector`
component for the meta-problem "can this proof technique resolve open
question X?"

### 2. Arithmetic geometry has the Brauer–Manin obstruction stack

For Diophantine equations, the **Hasse local–global principle** fails
in known, structured ways. A hierarchy of obstructions has been
catalogued:

- Hasse principle (works for quadratic forms; fails for cubics).
- **Brauer–Manin obstruction** (Manin 1970s): explains many failures
  of the Hasse principle via the Brauer group of the variety.
- Skorobogatov (1999) showed Brauer–Manin is itself incomplete: there
  exist varieties whose Hasse-principle failure is *not* captured by
  Brauer–Manin. Higher obstructions (étale Brauer–Manin, descent
  obstructions) have been proposed.

This is a real, working **stratified obstruction catalog** in number
theory. Importantly, it is *layered*: each new obstruction class was
added only after explicit counterexamples to the previous one.

### 3. Topology has Steen–Seebach as a counterexample atlas

*Counterexamples in Topology* (Steen & Seebach 1970, 2nd ed. 1978) is
the canonical example of negative-space cataloguing in math. It
contains 143 topological spaces indexed against ~60 properties, with
charts showing which properties each space satisfies. It is explicitly
designed for the use case "I want to know if property A implies
property B; if not, give me a witness." The book is the closest
existing analog to what Prometheus is trying to build with the
negative-space tensor — but it is *property-centric* rather than
*method-centric*, and it has no story about *why* approach X fails to
prove implication Y.

Variants exist (*Counterexamples in Analysis*, *...in Probability*,
*...in PDEs*) but none catalog *proof-technique failures*. They
catalog *object-level* counterexamples.

### 4. Polymath / Tao on instructive failure (process-level only)

The Polymath project explicitly endorses the heuristic that "the
reason for the failure of an approach is often instructive" (Gowers,
Polymath rules, 2009). Polymath5 (Erdős discrepancy problem) is the
most-cited case where many failed approaches across years eventually
converged into Tao's 2015 solution. However, the Polymath archives
preserve discussion threads, **not structured failure-mode
classifications**. Anyone wanting cross-project pattern extraction
must do it by hand.

The Quanta article *"How Failure Has Made Mathematics Stronger"*
(Calegari, May 2024) is the most prominent recent essay on this
theme. It identifies failure-modes that are **psychological** (sunk
cost, isolation, attachment to conventional wisdom, delayed error
detection — Dulac's 1923 proof of a Hilbert problem went unchallenged
for 60 years before Ilyashenko found a counterexample) rather than
structural-mathematical. Useful, but not a taxonomy.

### 5. Igor Pak on conjecture-validity failure

Igor Pak's blog post *"What if they are all wrong?"* (Dec 2020)
argues there is no objective criterion for assessing conjecture
validity, and identifies a *meta-failure*: the field invests
asymmetrically in proof attempts vs. disproof attempts, so survivor
bias inflates confidence in conjectures. He does not provide a
taxonomy.

### 6. Adjacent: Aaronson's "Eight Signs A Claimed P!=NP Proof Is Wrong"

A pragmatic checklist (e.g. "the proof doesn't 'know about' all
known polynomial-time techniques like dynamic programming, LP/SDP,
or holographic algorithms"). This *is* an informal failure-mode
taxonomy, but specific to one open problem.

### 7. Negative result on a general taxonomy

I found **no canonical reference** for a cross-domain mathematical
"failure taxonomy" comparable to ML's confusion-matrix conventions.
The Pak post explicitly laments this absence. The closest things —
complexity barriers, the Brauer–Manin stack, Steen–Seebach — are
each scoped to one domain. **This is itself a substrate-relevant
finding: if Prometheus successfully builds a cross-domain
kill_vector aggregation surface, it would be a genuinely novel
artifact, not a re-implementation of an existing one.**

## Substrate-relevance

Three direct mappings to current architecture:

1. **The natural-proofs barrier is the right mental model for
   `kill_vector` components.** Each barrier is a *predicate over
   proof techniques* that, when triggered, kills an entire class of
   approaches. Prometheus's current 12 components are mostly
   *predicate over claims* (does this specific claim survive F11?).
   The literature suggests it is at least as valuable to log
   predicates over the **method/approach** generating the claim
   ("was this elementary?", "did it relativize over the substrate's
   oracle layer?").

2. **The Brauer–Manin layered obstruction model maps cleanly to the
   margin field in the new kill_vector.** A claim might survive
   Brauer–Manin but die at étale-Brauer–Manin; the relevant
   information is *which obstruction layer* killed it. Prometheus's
   `margin: float | None` per component is structurally the same
   shape — it lets aggregation distinguish "killed at the boundary"
   from "killed by a wide margin", and downstream from "which
   obstruction layer was responsible."

3. **The negative finding is itself useful.** The absence of a
   pre-existing failure taxonomy means Prometheus does not have a
   ground-truth schema to validate against. The Lehmer
   negative-space tensor schema (`SCHEMA_v1.md`) is already at the
   frontier of what the literature has formalized — its
   `limitation_class` enum (method_complexity, case_restriction,
   asymptotic_only, comp_ceiling, non_constructive,
   requires_unproven_conjecture, other) is, as far as this study
   could find, **a novel cross-method classification**, not a
   re-implementation of any existing scheme.

## Concrete operational handles

### A. Additional kill_vector components to consider

Pulled from the literature scan, candidates for substrate-level
falsifier classes beyond the current 12:

1. **`relativizes`** (bool): does the claim/method survive when the
   substrate's known catalogs are replaced with arbitrary oracles?
   Cheap to check on a subsample of catalog substitutions.
2. **`naturalizes`** (bool, with margin): is the candidate property
   constructive + useful + large in the Razborov–Rudich sense over
   the substrate's object space? Useful in the long run for
   distinguishing structural from computational kills.
3. **`local_global_gap`** (float | None): for arithmetic claims,
   margin between local-everywhere validity and global validity
   (direct lift of Hasse-style obstruction).
4. **`requires_unproven_conjecture`** (bool, list of dependencies):
   already implicit in the Lehmer schema as a `limitation_class`;
   make it first-class in `kill_vector`.
5. **`asymptotic_only`** (bool, with crossover threshold): claim is
   true asymptotically but vacuous below some N. Direct lift from
   Dobrowolski-style limitations.
6. **`small_case_artifact`** (bool, with N): claim verified only on
   N samples below a threshold known to mislead (Pak's argument;
   Skewes-number-style failure mode).
7. **`asymmetric_effort`** (float): how much *disproof* effort has
   been spent vs. proof effort. Pak's meta-failure mode. Substrate
   can compute this from its own attempt logs.

These are **candidates**, not commitments. Each should be evaluated
against the Lehmer extraction pipeline before being added.

### B. Aggregation functions with literature support

- **Per-method-class survival rates.** The Brauer–Manin literature
  effectively does this: for each obstruction layer, count how
  often it accounts for failure across the variety class. Substrate
  analog: for each kill_vector component, plot triggered-rate
  across approach_class.
- **Margin distribution per component.** Lehmer literature
  implicitly aggregates "how close" near-misses got
  (Dobrowolski-Voutier-Mignotte improvements are all margin
  improvements on the same component). Substrate analog: histogram
  of margin values per component, per approach_class.
- **Layered-veto detection.** When component A always fires
  *before* component B fires, A may be a strict refinement of B
  (or vice versa). The Skorobogatov result is the canonical
  example. Substrate analog: pairwise correlation matrix on
  triggered-bits across kill_vectors.

### C. Negative-space mining: prior art is sparse

The closest published efforts are:

- **Steen–Seebach (1970)**: object-level, not method-level.
- **Polymath archive**: process-level, unstructured.
- **Erdős problems database / Tao's GitHub repo
  (`teorth/erdosproblems`)**: maintains problem status (open,
  solved, partially solved) but does not catalog *why* failed
  attempts failed.
- **DeepMind's `formal-conjectures` repo**: formalized statements
  in Lean, but not failure modes.

Conclusion: Prometheus's negative-space tensor would be, to my
knowledge, the first **structured** machine-readable failure-mode
catalog at the method level. This is a real opportunity but also
means there is no template to copy from.

### D. Claim-time logging requirements

To support the above aggregations, the substrate should log at
CLAIM-time:

1. The **method/approach class** used (analog of Lehmer
   `approach_class`).
2. The **catalog set** consulted (so the relativization analog can
   later replay the claim against substituted catalogs).
3. Any **assumed unproven conjecture** the claim depends on
   (catalog name + reference).
4. The **regime** in which the claim was tested (degree range,
   conductor range, sample N) so asymptotic-vs-small-case status
   can be inferred later.
5. The **disproof attempts already made** before CLAIM (for the
   asymmetric-effort component).

These are additive to the current schema and do not break existing
kill_vector consumers.

## Falsification

The central claim of this study is: *human mathematical literature
contains structured failure-mode catalogs in only a few specific
domains (complexity theory barriers, arithmetic obstructions,
Steen–Seebach style object catalogs), and no cross-domain
method-level failure taxonomy exists.* This would be falsified by:

- Discovery of a published cross-domain failure-mode taxonomy
  comparable to ML's confusion-matrix conventions or to
  Steen-Seebach but indexed by *proof technique* rather than
  *object property*.
- Discovery that the Polymath archives or Erdős database actually
  do contain structured failure-mode metadata that I missed in
  this scan (genuinely possible given time cap).
- Discovery that one of the formal-mathematics communities (Lean,
  Coq, Isabelle, Metamath) maintains structured failure-mode
  metadata on dead proof attempts (I did not find evidence of this
  but did not exhaustively check).

## Open questions raised

1. **Should the substrate expose its kill_vector aggregations as a
   public artifact?** If the literature really lacks this, there
   is a publishable contribution here independent of any specific
   conjecture result.
2. **What is the right granularity for `approach_class`?** The
   Lehmer schema uses ~10 classes; complexity theory uses ~3
   barriers. Too few classes and aggregations become uninformative;
   too many and you cannot detect cross-class patterns.
3. **How does the substrate avoid Pak's "asymmetric effort"
   failure mode internally?** If Prometheus disproportionately
   tries proof-style attacks on its own conjectures, its survivor
   bias mirrors the field's. Is the kill_vector battery already
   sufficient to counterbalance this, or is explicit
   disproof-effort logging needed?
4. **Are there cohort effects in margin distributions?** Brauer-
   Manin layers were discovered chronologically; later layers
   refine earlier ones. Will Prometheus's kill_vector components
   show similar refinement structure as the substrate matures?

## Citations

Verified via web search; full URLs preserved.

- Razborov, A. and Rudich, S. (1997). "Natural Proofs." *J.
  Comput. Syst. Sci.* 55(1), 24–35. Gödel Prize 2007.
  https://en.wikipedia.org/wiki/Natural_proof
- Aaronson, S. and Wigderson, A. (2009). "Algebrization: A New
  Barrier in Complexity Theory." *ACM Trans. Comput. Theory* 1(1).
  https://www.scottaaronson.com/papers/alg.pdf
- Baker, T., Gill, J., Solovay, R. (1975). "Relativizations of the
  P =? NP Question." *SIAM J. Comput.* 4(4), 431–442.
  (Cited in barrier surveys; primary URL not verified in this
  scan.)
- Manin, Y. (1971). The Brauer group obstruction; survey:
  https://en.wikipedia.org/wiki/Manin_obstruction
- Skorobogatov, A. (1999). "Beyond the Manin obstruction."
  *Invent. Math.* 135. (Cited in Brauer–Manin Wikipedia survey.)
- Steen, L. A. and Seebach, J. A. Jr. (1970, 2nd ed. 1978).
  *Counterexamples in Topology*. Springer / Dover.
  https://en.wikipedia.org/wiki/Counterexamples_in_Topology
- Calegari, D. (2024). "How Failure Has Made Mathematics Stronger."
  Quanta Magazine, May 22 2024.
  https://www.quantamagazine.org/how-failure-has-made-mathematics-stronger-20240522/
- Pak, I. (2020). "What if they are all wrong?"
  https://igorpak.wordpress.com/2020/12/10/what-if-they-are-all-wrong/
- Aaronson, S. "Eight Signs A Claimed P!=NP Proof Is Wrong."
  https://scottaaronson.blog/?p=458
- Gowers, T. et al. Polymath general rules.
  https://polymathprojects.org/general-polymath-rules/
- Tao, T. and contributors. Erdős problems database.
  https://www.erdosproblems.com/ ; GitHub:
  https://github.com/teorth/erdosproblems
- DeepMind. `formal-conjectures` repository.
  https://github.com/google-deepmind/formal-conjectures

**Items NOT independently verified** (cited only via secondary
survey): the precise Skorobogatov 1999 statement; the precise
Baker–Gill–Solovay 1975 statement. Both are well-attested in
multiple secondary sources and Wikipedia, but I did not pull the
primary papers in this 30-minute window. No canonical source
identified for a "cross-domain method-level failure taxonomy" —
this is the central negative finding of the study.
