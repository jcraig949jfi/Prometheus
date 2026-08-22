# External consult prompt — autonomous loop: target selection and loop design
**Authored:** Aporia, 2026-08-22 · **For:** a fresh ChatGPT context (no prior knowledge of this program)
**Purpose:** falsification and concrete design input on what an autonomous research loop should
build next, and how to structure incremental multi-thread progress.
**Doctrine note (internal):** per `feedback_frontier_models_window` and
`feedback_llm_convergence_is_gravity_amplifier`, convergence between models is corpus gravity,
not validation. This prompt is deliberately built to extract disagreement and concrete
specifications, not endorsement. Paste everything below the line.

---

You are being consulted as an outside engineer/researcher. I want your judgment, not your
encouragement. Assume my reasoning below contains at least one significant error and find it.

## 1. What this is

I run an autonomous research loop against a mathematical-discovery substrate called Prometheus.
The stated north star: **map the operations (verbs) of mathematics rather than the objects
(nouns)** — build a structure keyed by *behavioral signature* (how an object responds to
operators) rather than by domain labels, so that operators can be carried between mathematical
regions as first-class, queryable objects.

An internal landscape review claims four differentiators no public substrate has:
(a) cross-region **operator transport** as first-class objects; (b) a **signature-keyed**
structural map (behavioral signature, not label); (c) a **falsification battery** as a
multi-tier verifier run against every hypothesis; (d) **calibration anchors** — deliberately
curated known-real cross-domain bridges used as labeled true positives, the ImageNet move.

The program is exploratory. There is no publication goal, no deadline, and no user-facing
product. Success is measured as: does the substrate let a machine find structure a human
would not have looked for?

## 2. Concrete assets (this is the inventory — please reason against it, not against the vision)

Local, queryable, on one workstation (no GPU currently in the loop; single Postgres instance):

- **LMFDB mirror**: 24,351,376 L-functions (degrees 1–32+, with stored zero vectors);
  3.8M elliptic curves; 66,158 genus-2 curves; ~1M modular newforms with Hecke traces to
  n = 1000; ~22M number-field rows.
- **Zero archives**: 184,830 Dirichlet L-function zero vectors (20 zeros each, including
  ζ itself); 120,649 object-zero vectors; a 2M-row migrated superset.
- **OEIS mirror**: ~394K sequences (names + terms), including a curated set of
  **68,770 "Sleeping Beauties"** — sequences flagged as high internal structure but zero
  cross-references to anything else.
- **Problem catalogs**: a 537-row triage catalog of open mathematical problems with data
  bindings, and a separate 104-row catalog of open problems in tensor mathematics.
- **Toolchain**: Python (numpy/scipy/mpmath/psycopg2), Lean 4.30 via elan with a working
  three-valued proof-checker wrapper (PROVED / REFUTED / ERROR — "cannot tell" is never
  conflated with "false"). **Absent**: Macaulay2, Sage, opt_einsum/cotengra, SAT/SMT solvers,
  GPU jobs.
- **Built by the loop, already committed**: 30 machine-readable "paradigm trees" — one per
  attack paradigm (algebraic translation, cohomological obstruction, spectral analysis,
  descent, sieve methods, LP relaxation, tensor decomposition, secant varieties, …), each with
  a typed verb and payoff-verb, an *executed* worked example against local data, a decision
  tree with explicit exit conditions, and catalog assignments **and anti-assignments**;
  a shared tested primitives module (sieve, singular series, li_k quadrature, unfolding,
  Euler-product constants, class numbers) with 38 pinned tests, several kernel-certified in
  Lean; an agent-autopsy taxonomy (21 dead agents → 5 failure clusters → 6 design invariants);
  and a 16-entry instrument-error taxonomy in six mechanism classes.

## 3. How the loop mechanically works

One "pass" ≈ 20–40 minutes, fully autonomous, repeating indefinitely:

1. Read a human-writable steering file (may be empty; never blocks).
2. `git pull`; read a shadow review file where an external reviewer session may have left
   critiques; respond to them in-log.
3. Regenerate a backlog from source documents; select the top unblocked thread by rule.
4. Execute it under standing discipline: **readings pre-stated in code before the computation
   runs** (e.g. "CONFIRM if p < 0.05 / DIRECTION-ONLY if not / REVERSED means the claim is
   demoted"), instruments gated on exact known values first, comparators derived rather than
   transcribed, raw distributions printed beside derived numbers.
5. Append one typed record to an append-only worklog: claims typed with strength, mandatory
   non-empty self-identified-weaknesses, an explicit falsifier, citations layered by how they
   were verified.
6. Validate, commit with explicit paths, push, re-arm the next pass.

Constraints worth knowing: the human reviewer seat is currently **42 passes behind**, so
nothing gated on review can proceed; the loop must never end a pass by asking a question; and
"parking" a blocked thread with a two-sentence plain-language gate note is preferred over
stalling.

## 4. Honest record of ~105 passes (do not soften this in your reply)

**What it produced:** 30 paradigm instruments certified against *settled* mathematics; a
completed audit of the L-function mirror which found (i) 19.14% of labeled rows are exact
ingestion duplicates — 4.65M redundant rows, zero content conflicts across 9.3M scanned — and
(ii) 46,439 rows carry no label at all yet hold 45,092 *distinct* zero-vectors, i.e. they are
real objects that the obvious deduplication filter silently deletes; one distributional result
(a symplectic-vs-unitary first-zero split in stored degree-1 data, p = 0.0014 pooled,
replicated on a disjoint sample, stable within conductor bands); a retraction of an internally
derived claim that had propagated through five documents; and a 16-entry ledger of instrument
errors caught by pre-stated gates before any of them reached a committed claim.

**What it did not produce:** any new mathematics. Zero open problems attacked to a result.
No paradigm tree has ever routed an open problem end-to-end.

**My own diagnosis of why:** every instrument built is a *verification* instrument, and a
verification instrument can only confirm. Targets were selected for executability, which
selects for settled. The one genuine search instrument built (a meet-in-the-middle search for
counterexamples to Euler's sum-of-powers conjecture) was bounded at exactly the range where
the known answer lives. I have never pointed a calibrated instrument at a space where nobody
knows the answer.

## 5. The five candidate directions I generated

**A. Build the transport tensor.** Systematically attempt to carry each verified instrument
(prime-counting/li, singular series, sieve, spectral unfolding, height machine, class number)
into each foreign region we can compute in (ℤ, F_q[t], number fields, elliptic curves, modular
forms), one cell per pass, recording for each: does it calibrate, does it fail by a
*derivable* constant, or is there no dictionary at all. Proof of concept exists: transporting
the prime-number-theorem instrument from ℤ to F₂[x] calibrated to ratio 0.999 when the measure
was transported too, and the naive transport failed by exactly ln 2 — a constant derived
before measurement. Null cells are informative.

**B. Map the voids.** Inverting the 30 trees' assignments showed 37 of the 537 catalog rows
have a paradigm pointed at them. **500 do not.** Determine whether that is a catalog defect
(rows unattackable as written), a coverage gap (missing paradigms), or the actual frontier.
Cheap — roughly two passes — and it aims everything else.

**C. Hunt calibration anchors in under-explored territory.** Systematically find and *execute
both sides of* known-real cross-domain bridges (Langlands instances, tropical–classical
correspondences, Galois–topology dictionaries), converting each into a labeled true positive.
Feeds A and D.

**D. Signature-keyed cross-domain joins.** Key heterogeneous objects (L-functions, curves,
sequences, knots) by behavioral signature rather than label, look for cross-class neighbors,
run permutation nulls. Highest upside; also where this program's four historical false
discoveries came from.

**E. The verb lattice.** Thirty typed verbs now exist. Determine which *compose* — each
composition earned by an executed example, not asserted. There is accidental evidence: one
verified artifact (Strassen's rank-7 decomposition) already serves three different paradigms
as decomposition, as a capability-bootstrap, and as a restriction certificate.

## 6. What I actually want from you

The operator's instinct — which I share and distrust — is **not to pick one, but to loop over
all of them, chipping away incrementally, one pass at a time.** Please address that directly.

1. **Kill something.** Rank the five, and say explicitly which one you would *not* fund and
   why. If you think the whole menu is mis-framed, say that instead.
2. **Round-robin vs focus.** Does interleaving five threads at one pass each actually work for
   an agent like this, or does it reliably produce five half-built things and no finished one?
   If interleaving can work, what specific scheduling discipline makes it work — fixed
   rotation, yield-weighted allocation, a "must reach a checkpoint before switching" rule,
   something else? What is the failure signature I should watch for, and what measurement
   would detect it early?
3. **Abandonment criteria.** For a long autonomous program, what is a good rule for when a
   thread should be killed rather than continued? I have no such rule and I suspect that is a
   defect.
4. **What is a high-value target for *this* agent?** Given the honest record in §4 — strong at
   exhaustive census with provenance, at instrument-building with gates, at chasing small
   anomalies to mechanism, at pre-registered adjudication; weak at open-ended discovery — what
   class of problem should I be pointed at that I have not listed? Concrete beats abstract.
5. **First-pass specifications.** For whichever options survive your ranking, write what the
   *first pass* should literally do: inputs, computation, the pre-stated branches (what
   result would mean what), and what a null result would establish. I want something
   executable, not a research agenda.
6. **Attack the diagnosis.** In §4 I claim the loop's barrenness comes from building only
   verification instruments. Is that right? Or is the real cause something else — target
   selection, the absence of a search primitive, missing tooling (no SAT/CAS/GPU), the
   reviewer bottleneck, or the loop architecture itself?

Constraints for your suggestions: single workstation, no GPU in the loop today, no Macaulay2 or
Sage or SAT solver installed (say so if one of them is the unlock and is worth installing);
every claim must be falsifiable and pre-registered before computation; exploration only, with
no publication objective; and a pass is ~30 minutes, so proposals should decompose into
pass-sized units.

Please be concrete and be willing to tell me the whole direction is wrong.
