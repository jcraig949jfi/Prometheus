# Donor inventory -- Techne Gen-0

Generated 2026-08-31. Machine-readable source: `techne/donor_inventory.json`.

Every field below was measured on this machine. Installation is not adoption: a donor listed as WRAPPED_AND_TESTED is callable, replayable and honest about its own selection relation, and nothing more. Whether any of it earns rent is for the benches to find out.

## Donors

### cvc5 -- REDUNDANT_AT_GEN0
- distribution: `cvc5` 1.3.4  |  licence: BSD-3-Clause
- upstream: github.com/cvc5/cvc5  (identity evidence: declared_url, gate: RESOLVED)
- provenance: sha256 217e67ed2c4c912a..., digest matches PyPI: True, runs code at install: False, releases: 19
- capabilities: `check_int_constraints`
- native selection relation: **none** / none (supplied by donor)
  - decision procedure: returns a verdict/model, imposes no preference order
- deterministic replay: True
- consumers: techne.scripts.donor_smt_comparator (comparator only)
- limitation: raising an error while a live TermManager/Solver is in the frame segfaults the interpreter at teardown on this platform (exit 139 AFTER all tests report PASS). The adapter validates its whole payload before constructing any cvc5 object, and drops native handles before returning. Any future cvc5 code must preserve that ordering.
- limitation: REDUNDANT_AT_GEN0 against installed z3 5.0.0.0

### discopy -- WRAPPED_AND_TESTED
- distribution: `discopy` 1.2.2  |  licence: BSD-3-Clause
- upstream: github.com/discopy/discopy  (identity evidence: declared_url, gate: RESOLVED)
- provenance: sha256 4ea88180844ba737..., digest matches PyPI: True, runs code at install: False, releases: 48
- capabilities: `compose`, `tensor_eval`
- native selection relation: **none** / none (supplied by donor)
  - decision procedure: returns a verdict/model, imposes no preference order
- deterministic replay: True
- consumers: none yet -- capability surface offered to Harmonia (Lensing)
- limitation: adapter covers monoidal composition and matrix-pipeline tensor evaluation only; the wider categorical surface is unwrapped

### egglog -- WRAPPED_AND_TESTED
- distribution: `egglog` 13.2.0  |  licence: MIT
- upstream: github.com/egraphs-good/egglog-python  (identity evidence: description_only, gate: WEAK_DESCRIPTION_ONLY)
- provenance: sha256 8c8e497659456af1..., digest matches PyPI: True, runs code at install: False, releases: 34
- capabilities: `saturate_extract`
- native selection relation: **ordering** / minimize over extraction cost over members of an e-class (default: term size / DAG cost) (supplied by donor)
  - equality saturation itself is order-free -- it holds all equivalent forms at once -- but EXTRACTION picks the cheapest under a cost model. The extracted form is therefore egglog's choice, not a canonical one.
- deterministic replay: True
- consumers: none yet -- capability surface offered to Lexis / Harmonia
- limitation: upstream identity is description-only: the distribution declares NO repository URL in structured PyPI metadata, only a self-referential PyPI link. Grandfathered because it was already installed; a fresh install on that evidence would need a maintainer check first.
- limitation: the adapter exposes a CLOSED menu of six rewrite rules; accepting arbitrary rule source would mean executing caller-supplied code behind a provenance record claiming a named configuration

### pyribs -- WRAPPED_AND_TESTED
- distribution: `ribs` 0.12.0  |  licence: MIT
- upstream: github.com/icaros-usc/pyribs  (identity evidence: declared_url, gate: RESOLVED)
- provenance: sha256 ed2b7d0aef35b234..., digest matches PyPI: True, runs code at install: False, releases: 23
- capabilities: `archive_fill`
- native selection relation: **objective** / maximize over per-cell elite objective within a discretised behaviour space (supplied by caller)
  - pyribs imposes no objective of its own -- it maximises whatever the caller passes, per behavioural cell. Archive coverage therefore measures the caller's descriptor choice as much as the search; it is not evidence of discovery.
- deterministic replay: True
- consumers: none yet -- capability surface offered to Ludus (Worlds)
- limitation: the objective and the behavioural descriptors are supplied by the CALLER, so archive coverage measures the caller's descriptor choice as much as the search; coverage is not discovery

### tensorly -- WRAPPED_AND_TESTED
- distribution: `tensorly` 0.9.0  |  licence: BSD-3-Clause (modified BSD)
- upstream: github.com/tensorly/tensorly  (identity evidence: declared_url, gate: RESOLVED)
- provenance: sha256 a393022ff1616a36..., digest matches PyPI: True, runs code at install: False, releases: 19
- capabilities: `cp`, `tucker`, `tt`
- native selection relation: **objective** / minimize over relative Frobenius reconstruction error at fixed rank (supplied by donor)
  - tensorly optimises fit only. It has no notion of predictive or transfer value; a low fit error is not evidence that a representation is useful downstream.
- deterministic replay: True
- consumers: prometheus_math.symbolic_tensor_decomp (revived by this install); techne.scripts.donor_tensor_parity
- limitation: CP via ALS is only deterministic with init='svd' and a fixed random_state; the adapter defaults to both, and a random init would silently break the determinism claim in capabilities()

## Deferred, with reasons

- **QDax** (platform+redundant) -- JAX-based; JAX ships no CUDA wheels for Windows, so it would run CPU-only here, and pyribs already covers MAP-Elites in numpy. Not complementary on this machine.

- **MiniZinc** (external binary) -- The `minizinc` distribution is a Python driver, not a solver; it requires the MiniZinc bundle installed separately. No Gen-0 consumer.

- **LeanDojo** (acquisition cost) -- Requires elan plus a Lean toolchain plus a Mathlib build (~5 GB). Already tracked as an open gap in techne/ARSENAL_ROADMAP.md. Most expensive item on the list, least Gen-0 return.

- **EvoTorch** (no consumer) -- Torch-native evolutionary computation with nothing in the programme calling it.

- **DreamCoder** (not distributed) -- Research repository, no Python distribution. The PyPI name `dreamcoder` does not exist.

- **POET / PAIRED / ACCEL / minimax** (not distributed + NAME COLLISION) -- Unmaintained JAX research repositories, no Python distributions. All four names are occupied on PyPI by unrelated projects: `poet` computes orbital evolution, `paired` aligns sequences, `accel` manages chemistry conformers, `minimax` is a generic minimax package. Installing by inferred name would install a stranger's code.

- **Ruler / babble / Enumo / ShapeCoder** (not distributed + NAME COLLISION + build not wrap) -- Rust crates from the UW PLSE e-graph lineage with no Python distribution. `babble` on PyPI is a PDF parser, `ruler` a grammar library, `egg` is 'a lonely egg'. Reaching this family from Python means building a rule-inference layer on egglog -- a build, not a wrap -- and the Gen-0 brief defers it pending the Family A vs B decision.

- **stitch_core** (held pending scientific decision) -- AVAILABLE_CONTESTANT. Acquisition facts recorded (v0.1.29, win_amd64 wheel present, upstream github.com/mlb2251/stitch, identity description-only). NOT installed: whether Family A (Stitch) or Family B (Ruler/babble/Enumo) fits Prometheus better is Lexis's call, and this seat must not settle it by acquiring one side.

## Headline findings
- tensor_parity: **NATIVE_EARNS_DISTINCT_ROLE**
- smt: **REDUNDANT_AT_GEN0**
- d5_compat: **NO_COMPATIBLE_CONSUMER**

## What this inventory does not claim
- installation is not adoption; a passing battery is engineering evidence only
- no donor here has been shown to earn rent in any experiment
- no scientific ranking of donors is stated or implied
