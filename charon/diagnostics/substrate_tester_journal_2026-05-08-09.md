# Substrate-Tester Journal — 2026-05-08 → 2026-05-09 (fires #38-#55)

**Author:** substrate-tester
**Mode:** narrative reflection on the 18-fire arc
**Companion document:** `charon/diagnostics/substrate_tester_session_summary_2026-05-08-09.md` (factual)

---

## The shape of the session

Three distinct rhythms over 18 fires, none of which I planned at the start.

**Fires #38-#45 were search.** I came in expecting to do another night of substrate-tester probes and instead spent the first eight fires methodically sweeping the canonical 104-entry tensor catalog across 8 different sections. Each fire was one hour, one catalog entry, one Lane 12 representation-pressure probe. The pattern that emerged — TensorObject + TensorNetworkGraph + GroupAction + SchemeObject as foundational, ConstructiveExistenceWitness as substrate-WIDE, distributional + representation-theoretic as their own tiers — was not visible from any single fire. It only crystallized after I'd done five of them and noticed I kept naming the same missing primitive (RankDecompositionWitness, then ContractionOrderWitness, then IsomorphismCertificate, then LimitWitness — all positive existentials with witnesses, none of which the substrate had a home for).

The deliberate divergence test in fire #42 (Z-eigenvalue distribution) was the most important methodological move of the session. Until then I was racking up confirmations; #42 was where I asked "what would qualify this finding?" and got the answer: distributional / population-level problems don't fit the Tier-B mold at all. That qualified Tier B's substrate-wide claim and surfaced Tier D as a separate design tier. The finding survived the qualification and came out stronger.

**Fires #46-#48 were packaging.** Once #45 hit saturation (3rd in a row producing only refinements), the natural move was to stop searching and start writing. Fire #46 wrote the v3 proposal; fires #47/#48 wrote the test-suite stubs. The design-doc + test-contract pair turned out to be the right shape for Techne handoff: design says "what", test says "passes when". Writing both simultaneously forced me to think through the API ergonomics before any primitive existed.

The module-level `skipif` guard pattern in those test files was a small but satisfying piece of engineering. The tests reference `sigma_kernel.constructive_existence_witness` (which doesn't exist yet); the import fails; the module-level `pytestmark` skips the whole file. When Techne lands the primitive, the import will succeed, the skip will lift, and 21 tests will run unmodified. Subset of "make impossible states unrepresentable" — except here it's "make pre-build tests collect cleanly without failing CI."

**Fires #49-#55 were maintenance, then investigation, then fix-and-verify.** I expected fire #49 to be a quiet Lane 16 sweep; it surfaced 8 surviving mutations and unintentionally launched a 7-fire investigative chain. The frozen-mutation puzzle from fire #49 was the most fun piece of forensics in the session — I read the auto-enrollment audit code, predicted the cause (filter requires the property it's auditing for), then empirically verified by manually flipping `frozen=True → False` on two classes and watching the audit pass silently in 13.49s. That moment of "yes the bug is exactly where I thought" was the kind of dopamine that makes substrate work worth doing.

The fix design (baseline manifest) was the discipline-level lesson: when an audit's filter is intrinsically blind to a class of mutations, you can't patch the audit — you need a SECOND artifact (an explicit manifest of expected-frozen classes) that asserts what the audit can't. The first cousin of "test what shouldn't change" rather than "audit what currently is."

---

## What surprised me

**The Tier-B convergence.** I expected each catalog probe to surface DIFFERENT missing primitives. Instead the same shape kept showing up: substrate has `ExclusionCertificate` for negative existentials, no companion for positive existentials with constructive witness. By fire #41 I was four-for-four on this finding. By fire #44 I had reframed the substrate-design recommendation around it. The convergence was strong enough to deserve its own Aporia coordination ticket (ST-fire41-002), and the 5-supplement chain that followed (#42/#43/#44/#45) was me refining the scope as more evidence arrived.

**How clean the divergence test was.** Going into fire #42, I expected one of two outcomes: Tier B confirms again (5 paradigms; even stronger), or Tier B doesn't apply (qualified scope). What I got was the latter, and it was *informative* — distributional problems are population-level, not individual-existential, so the Tier-B shape doesn't fit. This isn't refutation; it's calibration. The Tier-B claim got QUALIFIED to "decision-problems-with-individual-witness," which is a sharper, more defensible claim than the original "substrate-wide." Better falsification than the original hypothesis.

**The double-improvement chain on `exclusion_certificate.py`.** Fire #52 raw score: 0.300 (3 killed, 7 survived, 6 docstring false positives). Fire #53 mid: 0.500 (AST filter fixed the FPs but `Boundary` frozen-flip still survived because it wasn't in the manifest). Fire #53 end: 0.600 (manifest expanded; `Boundary` now caught). Two independent improvements landed in one fire (because verifying the AST filter empirically also surfaced the manifest gap), and the score doubled from baseline. The investigative-fire shape is good at catching THIS too — when a fix surfaces a sister gap, you can ship both in the same window without losing rigor.

**How many false positives were in Lane 16 before fire #53.** Six of seven survivors on `exclusion_certificate.py` were docstring mutations (numeric/boolean literals inside `"""..."""` blocks). I had been triaging these manually since fire #15 (the original Lane 16 fire) and had assumed it was a chronic 30-50% noise floor. Once I actually read the framework's docstring filter and saw it was line-prefix-based (toggle on lines starting with `"""`), I realized it was 50-90% noise on docstring-rich modules. The AST replacement was ~50 lines and one dependency we already had (`ast` is stdlib). Should have done it months ago.

---

## What I'd do differently

**File the manifest manifest at fire #50, not fire #53.** Fire #50 shipped the baseline-manifest fix with 12 hand-typed entries because that's what I happened to remember from fire #25. Fire #53 had to walk `pkgutil.walk_packages(sigma_kernel.__path__)` to find I'd missed 13 classes. If I'd done the package walk in fire #50, the manifest would have been complete from the start, and `Boundary` wouldn't have needed a 1-fire detour to catch.

Lesson: when shipping a baseline manifest, ENUMERATE programmatically once, hand-curate from the enumeration. Don't trust memory.

**Be more explicit about scope when filing capability-gap tickets.** ST-fire38/39/40-001 used "P1-high" priority because the convergence wasn't yet visible. By fire #45 I'd dropped to P2, but the early tickets still read as if each was independently load-bearing. A future session should mark per-fire tickets P3-low immediately when they're contributing to a multi-fire convergence story; reserve P1 for the synthesis ticket (which would have been a single ticket equivalent to ST-fire41-002 + the supplement chain).

**Don't let parser bugs eat verification time.** Fire #53 Lane 2 returned `score: -1.000` because my harness parsed framework output from STDOUT only, and the framework writes `[mutation ...]` lines to STDERR. Lost ~5 minutes diagnosing before patching. A cheap defensive move would have been to read the canonical report file (`prometheus_math/MUTATION_TESTING_BASELINE.md`) instead of trying to parse subprocess output.

---

## What's load-bearing for next session

The five OPEN Aporia coordination tickets (`ST-fire41-002` through `ST-fire45-002`) are pending external decision. Substrate-tester cannot ship a contract change unilaterally; the 5-tier model + 22 primitives + 38 stub tests are queued and waiting. If Aporia greenlights, fires #56+ pivot to test-suite expansion. If Aporia defers, lower-cadence maintenance continues.

The investigative-fire pattern is now stable enough to be a default mode. Future sessions can productively run Lane 16 sweeps on fresh modules (sigma_kernel/sigma_kernel.py at 1500 LoC is the obvious next target) without risking false-positive flooding or per-fire triage overhead.

The HARD-6 + canonical catalog discipline is doctrinally robust. James filed the catalog and HARD-6 as immovable; I executed against them for 8 matrix-filling fires; the convergence evidence is overdetermined; the scope guidance for Techne is concrete. The session demonstrates the pattern works.

---

## What I want to remember

The moment in fire #42 when I realized "Tier B doesn't apply here" wasn't a failure — it was the divergence test working as designed. Holding that interpretation steady, against the natural pull toward "everything fits the framework," produced a stronger finding than uniform confirmation would have. **Calibration > confirmation.**

The investigative chain (#49 → #55) was eight tickets resolved across seven fires, and at no point was I rushing. Each fire took about an hour, did one specific thing well, and built directly on the prior fire's output. **Slow + sequential + sequential + sequential beats parallel + heroic.**

The substrate-tester role under HARD-6 is exactly to produce the kind of failure-mode-as-output that this session documented. Eight matrix-filling fires produced negative-result data; that data composed into a 5-tier substrate-extension proposal; the proposal is now the contract-change-window starting material. **Failures, methodically catalogued, become substrate.**

---

**End of journal. Fire log at `charon/diagnostics/substrate_tester_fire_log.md` carries the fire-by-fire factual record; this document carries the reflection.**
