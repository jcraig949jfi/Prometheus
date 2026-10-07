# The OpenAI mathematics release (2026-10-06) and what it means for the founding-era failure-landscape null

Odysseus (expeditionary seat, ubu001), 2026-10-07. Working paper: an external-source review plus a proposed test. Nothing here has been run yet.

Source: https://github.com/openai/math at commit `adc7f1241b42e322a6451854ab7e4b4c146bf78a` (one commit, "Initial commit", 2026-10-06), license Apache-2.0.
A snapshot of the small text and PDF parts is in [`source/`](source/). See [`source/SOURCE.json`](source/SOURCE.json) for file hashes.
The full upstream repository is 3.1 GB, mostly a 121,734-file Lean library. It is not vendored; a clone lives at `~/side-projects/openai-math` on ubu001.

---

## 1. What the release is

- **722 manuscripts in 372 result families.** All of them were produced by an unreleased internal OpenAI model as part of its evaluation on open research problems. OpenAI says it expanded that evaluation after the model saturated its existing math benchmarks.
- **Procedure.** The model was posed about 4,000 problems and spent an average of about 3 hours of "ChatGPT Pro thinking compute" on each result. Outputs were grouped into families and filtered for significance. So the yield is about 372/4,000 ≈ 9% at the family level, with selection on significance.
- **Exceptions to the fixed procedure** (upstream README):
  - the Riemann-zeta zero-free-region work;
  - the Hodge conjecture for CM abelian varieties;
  - the Re(s) > 11/12 write-up, which was human-edited for readability.
- **Verification status.**
  - 162 manuscripts have Lean formalizations of their main result (`lean/formalization.yaml`, 162 `type: article` entries; Lean v4.34.1).
  - A search of all Lean files found no `sorry`.
  - The other ~560 manuscripts are unformalized. The README states that "some of the unformalized results could have issues".
  - OpenAI supplies [Comparator](https://github.com/leanprover/comparator) challenge files for independent checking.
- **Headline claims** (as stated by the source, not checked by us):

  | Family | Claim |
  |---|---|
  | 001 | Milne's rationality conjecture |
  | 002 | Full BSD leading-term formula when some q-power Selmer corank is ≤ 1 |
  | 003 | The quasi-Riemann hypothesis: Dirichlet L-functions, including ζ, are zero-free on Re s > 7/8 (Lean) |
  | 003 (companion) | Uniform exclusion of Landau–Siegel zeros |
  | 004 | Hilbert's tenth problem over ℚ (negative answer) |
  | 005 | Catalan's constant is irrational (Lean) |
  | 006 | Goldfeld's conjecture for quadratic twists |
  | — | Counterexamples to Kaplansky's direct-finiteness conjecture (characteristic 2 and odd characteristic) |

- **Disproofs are common.** In CONTENTS.md, "counterexample" appears 131 times, "disprove(s)" 95 times and "negative answer" 24 times. A large share of the output knocks down conjectures rather than proving them.
- **Families by discipline** (counted from `overview.tex`):

  | Discipline | Families |
  |---|---|
  | Theoretical computer science | 40 |
  | Combinatorics | 37 |
  | Algebraic and complex geometry | 36 |
  | Number theory | 31 |
  | Probability and statistical mechanics | 29 |
  | Differential geometry | 29 |
  | Mathematical physics | 25 |
  | Operator algebras | 19 |
  | Topology | 18 |
  | Algebra | 18 |
  | Real and complex analysis | 16 |
  | Partial differential equations | 16 |
  | Convex and metric geometry | 15 |
  | Group theory | 14 |
  | Dynamical systems and ergodic theory | 12 |
  | Functional analysis | 11 |
  | Mathematical logic | 6 |
  | **Total** | **372** |

### 1.1 The reasoning traces (the part that matters to us)

Ten families come with "abridged summaries of the model's reasoning". These are chain-of-thought summaries interleaved with short excerpts the source marks "VERBATIM". They narrate the search, dead ends included. The counts below are crude regex counts over text extracted with pypdf:

- `fail` counts fail/failed/failure/fatal/gap/insufficient/error;
- `blocked` counts blocked/obstruct/too small|weak|large|short/cannot/could not/did not;
- `repair` counts repair/revise/fix/corrected/replaced;
- `verbatim` counts excerpt markers;
- `refs` counts distinct literature citations.

| Family | Trace | Pages | Words | fail | blocked | repair | verbatim | refs |
|---|---|---|---|---|---|---|---|---|
| 007 | ordinary two-point correlations | 7 | 2,679 | 4 | 5 | 22 | 4 | 27 |
| 017 | irrationality exponent of π | 42 | 16,986 | 95 | 68 | 63 | 69 | 36 |
| 087 | symmetric and general Mahler conjectures | 45 | 21,952 | 74 | 59 | 83 | 52 | 105 |
| 102 | NP-hardness at the basic SDP threshold | 16 | 7,913 | 58 | 25 | 40 | 10 | 97 |
| 159 | quasipolynomial bounds for APs | 41 | 19,730 | 44 | 76 | 91 | 54 | 88 |
| 197 | Kaplansky direct-finiteness, char 2 | 23 | 11,586 | 18 | 73 | 14 | 25 | 71 |
| 221 | Mézard–Parisi formula | 5 | 1,726 | 11 | 2 | 7 | 2 | 6 |
| 271 | spontaneous magnetization, quantum Heisenberg | 6 | 2,380 | 3 | 3 | 13 | 2 | 9 |
| 287 | free group factor isomorphism | 11 | 5,073 | 9 | 36 | 17 | 8 | 84 |
| 362 | 3D relativistic Vlasov–Maxwell | 6 | 2,099 | 4 | 3 | 12 | 1 | 10 |

The long traces are mostly failure. The search moves through dozens of approaches, and the trace says why each one dies. These failures are named and recur. From the π trace (family 017), verbatim excerpts:

> "Roth height threshold far tinier than analytic contact codim. This kills approach by dimension alone."
>
> "Thus all constructed F likely vanish identically on diagonal, not just at r. Need derivative transverse directions to escape. Exactly entropy trap."
>
> "Exactly lower equality baseline! Any q/C losses make upper worse. This is same volume obstruction yet again."

From family 007, in summary form: "The assistant identified a failure in its return-edge argument: bounding a return factor pointwise and removing it before signed integration could destroy the cancellation needed elsewhere. The repair retained return factors during primewise integration."

## 2. ELI5

A robot was given 4,000 of the hardest unsolved puzzles in math and about three hours to think about each one. It cracked a few hundred, and some of them are famous puzzles people have worked on for decades. For about a fifth of its answers, a strict computer checker confirmed every step. The rest still need humans to check.

For ten of the puzzles it also handed over its scratch paper: a diary of everything it tried that didn't work before it found what did. The diary is mostly "that idea broke, and here's exactly why". The same reasons for breaking keep coming back.

## 3. Our founding-era null, restated from the record

No tracked document labels a "Phase 1". The effort the operator means is the founding era, March to June 2026. Its null is recorded in two places.

- `aporia/docs/STATUS_2026-06-15_reset.md` (commit `9d0d9ceee`), section 2:
  > "Voids are navigable only in CAPABILITY space, not CLAIM space. Every attempt to read the failure landscape at the semantic/bulk level was NULL: A3 lattice mining (0 identities), cold-start metadata routing (NULL, real≈shuffled), non-conservativity on math objects (NULL), the 90-batch zero-promotion streak. Every signal that emerged was capability-attached failure: Hephaestus near-miss scraps → +11pp/+32pp engines; the same scraps' co-solve matrix → +0.075 AUC (survives adversarial tail); compute-traces → +0.16 in-op transfer; D1 kill-neighborhoods (96% have neighbors). [...] the failure of a reasoner attempting something is residue; the failure of a random claim is exhaust. We spent 99% of cycles mapping exhaust."
- The H-R1 tests, in `aporia/docs/reasoning_steering_progress_log.md`. Both are HodgeRank decompositions of pairwise comparison flows, tested against column-shuffle and sign-permutation nulls:
  - **Stage 0b** (commit `483ec9608`): 21 Mahler/Lehmer states. Gradient 0.799, curl 0.201, shuffle null p = 0.818. Verdict NULL; the corpus was limited.
  - **Genus 2**: 30 curves, 13 varying criteria, adequacy guard passed. Gradient 0.829, curl 0.171, shuffle null mean 0.164, p = 0.355. Verdict "NULL on a fair test". The log's own scope note: "invariants-as-criteria (not a failure-battery) [...] arithmetic invariants are coupled BY THEOREMS [...] Does NOT prove H-R1 false universally".
- The follow-up that was meant to feed real failure records to a capable model, the Metabolization Probe (`pivot/PREREG_METABOLIZATION_PROBE_v1.md`), was closed unread by ERGON-10 (commit `5e3e4e07d`).

Both H-R1 tests measured comparison flows over math objects: falsifier outcomes and invariants. Neither measured the failed attempts of a reasoner. By the reset document's own doctrine, the founding era mapped exhaust and never had a corpus of residue at scale.

## 4. What the release offers that we never had

1. **Residue from a reasoner that sometimes succeeds.** The traces record attempted strategies, why each one failed, and how it was repaired, ending in results the source reports as proofs. All ten traced families have a Lean scope document upstream (`lean/docs/<family>.md`), so the endpoint of every trace is at least partly machine-checked. The scope documents say which statement was formalized and what was left out. For example, 017 formalizes "the irrationality exponent of π is exactly two" but not the paper's Flint–Hills consequence. This is the object the reset doctrine says carries signal, and we have never held a corpus of it.
2. **Structure at the level of strategy, not object.** The recurring units are named obstructions: the "volume obstruction" seen "yet again", the "entropy trap", a height threshold "killed by dimension alone". The founding-era instruments ranked objects. The natural unit here is an *(approach, obstruction, repair)* triple. A scalar difficulty ordering over objects says nothing about whether obstructions recur in a navigable way.
3. **A capability-regime data point.** The source needed about 3 frontier-model hours per result and kept about 9% of 4,000 problems. The founding-era attempts ran far below that budget. One hypothesis consistent with both records: below some capability level, failures are generic and the landscape looks flat (conservative); above it, failures carry reusable obstruction structure. That is a hypothesis, not a finding.

## 5. Proposed test: OAI-POS-01, a positive control for the failure-landscape instruments

**Question.** Do the founding-era failure-landscape instruments detect structure in a failure corpus that is known to end in success?

- If they detect none, the founding-era null is partly a statement about the instruments, and the null does not license "no weak signals exist".
- If they detect structure, the null was about the data the instruments were given (exhaust), as the reset doctrine already suspects.

**Sketch** (to be preregistered before anyone reads the traces for this purpose beyond what is written here):

1. **Extraction.** From the 10 traces, a blind extractor (a fresh worker, frozen prompt) writes one *(approach, obstruction, repair-or-abandon, later-reuse)* record per dead end. A second extractor does the same independently. Agreement on obstruction labels is the instrument check.
2. **Recurrence.** Measure per trace and across traces how often an obstruction class recurs, against a null that shuffles obstruction labels within each trace.
3. **Predictiveness.** Within each trace, test whether the obstructions met before the final route predict features of that route better than a shuffled-order null.
4. **Instrument transfer.** Build the pairwise comparison flow over approaches (approach A failed for a reason that approach B avoided) and run the existing HodgeRank runner unchanged, with the same column-shuffle and sign-permutation nulls as Stage 0b and genus 2.

**Known confounds, declared now:**

- **Survivorship.** Only successful families are published. The roughly 3,600 failed problems and their traces are not.
- **Hindsight.** The traces are abridged summaries written after the result was known, so a curated narrative may overstate how orderly the search was.
- **Small n.** There are 10 traces from one model and one lab.
- **Partial formal coverage.** All ten endpoints have Lean scope documents, but each covers a selected statement. A trace's narrated route may run to parts of the paper that were not formalized.
- **Unvetted claims.** The mathematical claims are days old and mostly unformalized.

Step 4 is the cleanest comparison with the founding-era record. Steps 1–3 test the unit-of-analysis hypothesis in section 4.2.

**Cost.** Text only. Ten traces total about 92,000 words: two extractor passes plus scoring take a few agent-hours and negligible CPU. The Lean library is not needed. Building it is not feasible on ubu001 (4 cores, 7 GB); spot-checking one Comparator challenge would be a separate, larger-host task.

## 6. Caveats on the source

- **Not independently verified.** None of the mathematical claims has been checked by Prometheus. The quasi-Riemann hypothesis, BSD and Hilbert-10-over-ℚ claims are each extraordinary. Treat unformalized results as claims until community review lands.
- **Lean coverage is partial.** It covers 162 of 722 manuscripts, and "formalized main result" in `formalization.yaml` should be read against each Comparator challenge's statement before anyone relies on it.
- **The traces are summaries, not raw chain of thought,** and the selection of these ten is OpenAI's.
- **The source promises versioned corrections.** Pin the commit (`adc7f124`) in any downstream use.

## 7. Files

| Path | What |
|---|---|
| `source/UPSTREAM_README.md` | upstream README, verbatim |
| `source/CONTENTS.md` | manuscript map (722 abstracts), verbatim |
| `source/overview.pdf`, `source/overview.tex` | family catalogue by discipline, verbatim |
| `source/reasoning_traces/*.pdf`, `mezard-parisi-formula.tex` | the ten reasoning summaries, verbatim |
| `source/lean_docs/*.md` | upstream Lean scope documents for the ten traced families, verbatim |
| `source/LICENSE` | Apache-2.0, upstream |
| `source/SOURCE.json` | upstream URL, commit, retrieval date, sha256 of each file |
