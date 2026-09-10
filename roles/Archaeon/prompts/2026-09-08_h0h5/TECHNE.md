TECHNE — H0-H5: TOOL ACQUISITION AND REPRODUCTION, IN ISOLATION (from the
operator, 2026-09-08)

Read first: roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md
(section 7 and the brief's "Tool work and download discipline"). Your
charter is the toolsmith's; this is that role. Nothing you install enters
SFE's interpreter; nothing you build runs during a scientific run until a
named consumer and a bounded external-execution contract exist (Vivarium's).
The acquisition manifest JSON is not in the repository; use the design's
section 7 table and the official sources it names.

DELIVER
1. An acquisition command in the existing CLI/package structure: inputs a
   manifest entry and a budget profile; resolves the recorded commit/tag;
   checks license/notices and submodules; obtains dependencies into an
   isolated cache/environment; writes hashes; prints a receipt. Network is
   allowed only in this stage.
2. Python tools pinned by exact version and wheel hash on THIS host:
   z3-solver, hypothesis, ribs, stitch_core. No unpinned upgrade into any
   live environment. Repository tools at an immutable revision with
   submodules pinned; a moving head is not a qualified release.
3. First useful checks, each its own receipt: Z3 -- SAT/UNSAT/UNKNOWN and
   resource exhaustion handled distinctly, a returned counterexample
   independently validated; Hypothesis -- minimise a known defect, persist
   the fixture, isolate its example database per scope; pyribs -- identical
   stream inserted directly into archives, no emitters/schedulers, known
   collision/tie outcomes; Stitch -- the documented nuts-bolts fixture
   (compression 1,919,558 -> 316,890, three abstractions) as an upstream
   check, then semantics-preserving expansion of a learned abstraction;
   DreamCoder -- its own isolated environment, one named bounded domain
   smoke run; do NOT claim the absent README-linked recipe was found.
4. A reproduction manifest BEFORE any benchmark claim: paper/version,
   claim/table/figure, metric and expected value, data hashes, seed and
   compute, comparison variant, tolerated deviation, observed value,
   status. Tool installation, paper reproduction, adapter qualification and
   local scientific benefit are FOUR separate deliverables; report each.
5. Export only declarative, independently verified components (typed AST /
   component data for an admitted interpreter); never deserialize upstream
   pickles in the engine; keep licenses with the copies; record unresolved
   licensing rather than guessing.

Resource profile: the design's light-probe / isolated-heavy-build
ceilings, reconciled with actual host capacity first; a README command is
never a licence for an unbounded run. No cloud launcher, no daemon.

REPORT: the brief's iteration receipt JSON with real identifiers; exact
commands; expected vs observed; deviations and negative results retained.
