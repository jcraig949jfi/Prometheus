# 07 — Implementation roadmap

Constraint honoured: nothing below was implemented in this round. Paths are proposals in a new top-level package `rll/` (engine) plus `rso/rll/` (independent evaluator). Neither path exists at `5633cc02a`. No existing file is modified, except one new target registration in `rso/adversary/targets.py`, owned by RSO and done by RSO.

Language: Python 3.12 (the fleet standard). Dependencies:

| Dependency | Required? | Use |
|---|---|---|
| Standard library | required | everything in M0 |
| `numpy` | required | output-vector hashing, statistics |
| `pytest` | required | tests |
| `stitch_core` (MIT, PyPI bindings of `mlb2251/stitch`) | optional | cross-check of the MDL gate |

No GPU. No network at runtime. No LLM anywhere in the loop.

## M0 — Proof of mechanism (target: 3–4 engineer-weeks + ≤ 800 core-h)

### M0 code

| Module | Contents | Size est. | Reuses |
|---|---|---|---|
| `rll/kernel/lang.py` | Types, AST, total metered interpreter, structural hash | 600 lines | Escrow pattern (`roles/Aphrodite/engine/engine.py:82`) |
| `rll/kernel/promote.py` | Content-addressed abstractions, exact-expansion contract, independent CBV evaluator | 300 | `roles/Aphrodite/engine/w5p/promote.py` semantics |
| `rll/kernel/entropy.py` | Disjoint domains `RLL/DEV`, `RLL/SEARCH`, `RLL/PANEL`, `RLL/HELDOUT`; keyed CRN order | 80 | `engine.py:52-66`, `fair.py:key/keyed` |
| `rll/kernel/accept.py` | Filters, probe battery, screen/confirm panels, continuation test, rollback stack, ACCEPT record | 400 | `fair.py` paired-cell design; SSA rule |
| `rll/kernel/mdl.py` | Fixed MDL gain gate | 200 | cross-checked against Stitch on a shared corpus |
| `rll/kernel/ledger.py` | Hash-chained JSONL; ACTION/EVENT types; replay | 150 | — |
| `rll/kernel/edits.py` | Fixed type-preserving edit grammar over φ ASTs | 250 | — |
| `rll/engine/phi0.py` | φ₀ slot programs written in the DSL | 100 (DSL text) | DreamCoder-like baseline behaviour |
| `rll/engine/loop.py` | `solve`, `sleep`, `meta`, `generation` | 500 | — |
| `rll/tasks/devgen.py` | Dev generator: hidden motif grammar, recurrence, graded size | 300 | W8 lineage-generator lesson (`roles/Aphrodite/science/arc3/w8_lin_generator/`) |
| `rso/rll/heldout_gen.py` | **Written by an RSO seat**; sealed; hash committed before T runs | 300 | — |
| `rso/rll/eval.py` | `heldout_eval`, replay check, outcome-class reducer (06 §6) | 300 | `rso/` registry conventions |
| `rso/adversary` target `rll_accept` | DROP / DUPLICATE / REWRITE_DERIVED / CONSTANT / SCRUB_ANSWER on ledger, panels, acceptance; meter-bypass mutant | 150 | `rso/adversary/targets.py` pattern |

### M0 steps (each a small, reversible, separately committed increment)

1. `lang.py` + tests:
   - determinism (same AST + inputs gives the same value and charges);
   - totality (fuel);
   - meter monotonicity;
   - hash stability across processes;
   - CRLF-safe source (`.gitattributes eol=lf` for `rll/`; test from `git archive | tar -x`, per the fleet's CRLF lesson).
2. `promote.py` + tests:
   - expansion equality on 10k random programs (independent evaluator);
   - content id independent of arm/name.
3. `ledger.py`, `entropy.py` + tests: replay reproduces the head hash; domains disjoint (no lineage id in the PANEL/HELDOUT domains).
4. `edits.py`, `mdl.py` + tests: edits type-preserving; MDL gate agrees in sign with Stitch's compression on 3 shared corpora (agreement reported, not required to be exact).
5. `phi0.py`, `loop.py`, `devgen.py`. **Supply screen** (06 §6): φ₀ from θ₀ solves 20–60% of dev families. Iterate the generator until it does. Every revision is logged and frozen before step 7.
6. **Withheld-mechanism certification** (RSO): hand-build φ₀+W1 … φ₀+W6; each must beat φ₀ on H₁-same by ≥ δ. Record each one's P₀-depth. Uncertified Wk are dropped from the battery *before* freeze.
7. `accept.py` + the kit target. The planted negative is rejected ≥ 95%; the meter-bypass mutant is caught; the kit has 0 SURVIVED. **ENGINEERING_SUCCESS gate.**
8. Freeze the prereg (06, with generator hashes) → commit → run the M0 arms.

### M0 commands (planned)

```
python -m pytest -q rll/kernel/tests rll/engine/tests          # unit + contract
python -m rll.supply_screen --gen devgen@<sha> --seeds 0-2       # step 5
python -m rso.rll.certify_withheld --battery W1-W6               # step 6 (RSO)
python -m rso.adversary run rll_accept                           # step 7
python -m rll.run --arm T  --seed 0 --gens 10 --prereg <sha>     # arms T F0 N0 CM HP XM SH SA ID IK
python -m rso.rll.eval --arms all --heldout H1 --reveal-after    # RSO only
python -m rso.rll.replay --ledger <head-sha>                     # determinism
```

### M0 compute

| Item | Estimate |
|---|---|
| 10 arms × 3 seeds × 10 generations, ≈ 2–6 core-h per T generation | 300–800 core-h |
| Held-out evaluation | ~50 core-h |
| Fleet slice | One host with ≥ 16 cores suffices (≈ 2–3 days); Fabric optional |

The first measurement is interpreter throughput. All estimates are rescaled to it before freeze.

### M0 expected failure modes

- The generator is too easy or too hard (supply).
- The interpreter is too slow, so panels shrink and lose power.
- No edit passes ACCEPT: the S-META kill.
- Accepted edits are all W1/W2-like tuning: HP matches, S-L2.
- The MDL gate disagrees with Stitch badly: a compression-measure defect.

### M0 go/no-go

| Decision | Condition |
|---|---|
| **GO to M1** | ENGINEERING_SUCCESS **and** SELF_MODIFICATION_DEMONSTRATED (T beats F0, CM, HP and SH on H₁) in ≥ 2/3 seeds **and** ≥ 2 accepted edits in some lineage (otherwise there is no g+1 to test) |
| **GO to M1, flagged** | The above, but T ≯ XM. M1 then mainly tests whether recursion appears later, with the L3 prior lowered |
| **NO-GO** | Any S-condition in 06 §8. S-META → fall back to Candidate E (plasticity rules) as a separate programme |

## M1 — Recursive generation (target: 2–3 engineer-weeks + 1.5–4k core-h)

### M1 code

- `rll/meta_ko.py` — arms M-KO-C1, M-KO-C2, PM: role-split slot binding, edit-grammar restriction.
- `rso/rll/msr.py` — the MSR reducer and Fisher tests.
- Fabric task templates (`fabric/` worker executor `script`, pinned SHA worktree) for 30 replicates × 4 meta arms × each tested g+1.

### M1 steps

1. From each M0 T lineage with ≥ 2 accepted edits, take the state just before each accepted edit at g ≥ 2.
2. Run 30 independent meta-search replicates per arm (T-meta, M-KO-C1, M-KO-C2, PM) at matched C_meta. Fresh panels per replicate.
3. Extend T lineages to 20 generations on 5 seeds, collecting more g+1 test points. Report the edit-depth census and the abstraction-use census.
4. Held-out H₁ evaluation of φ₂, φ₃, … vs φ₁, and T vs XM at matched total compute.
5. RSO replays a random 10% of replicates byte-for-byte, plus every replicate that enters a deciding cell.

Command shape: `python -m fabric submit --template rll_msr --arm M-KO-C1 --state <sha> --replicates 30`.

### M1 compute

| Item | Estimate |
|---|---|
| 4 arms × 30 replicates × (2–6 core-h) × ~3 test points | 720–2,200 core-h |
| Extended lineages | ~800 core-h |
| Fleet fan-out over Linux and Windows workers | ≈ 1 week |

### M1 failure modes

- Too few lineages with a second accepted edit, so too few test points.
- MSR near 0 in every arm: UNTESTABLE.
- Channel 1 exists but only through W1-type pruning. That is a real but *designer-anticipated* effect; it is reported with that scope.
- Effects disappear at Holm-adjusted α.

### M1 go/no-go

| Decision | Condition |
|---|---|
| **GO to M2** | BOUNDED_RECURSIVE_IMPROVEMENT_SUPPORTED per 06 §6 |
| **M2-as-L2-transfer only** | RECURSION_NOT_DEMONSTRATED with L2 intact |
| **STOP** | INVALID |

## M2 — Transfer and expansion (target: 4–6 engineer-weeks + 2–5k core-h)

1. **Second domain H₂.** Tree/AST families: rewriting, tree queries, small program-transformation tasks. Written by RSO from the spec. This also tests the cross-level hypothesis that tree-task abstractions shorten φ-edits, since φ operates on ASTs.
2. **Budget shift.** Re-evaluate φ_final at 0.5B and 2B to check the gain is not budget-relative (the A23 walk-cliff lesson).
3. **External baseline check.** Run `ellisk42/ec` DreamCoder on one shared list domain at matched CPU-hours. This is a sanity check that φ₀ is not a strawman. If DreamCoder's fixed improver beats T, report it plainly.
4. **Composition Ladder link.** Port Hestia's R1–R4 rungs (hold two values, bit-conditioned mapping, parity-3, reuse) as RLL task families. Ask whether φ_final reaches rungs that φ₀ cannot at matched compute. This connects RSI to the program's central wall.
5. **Expansion:** only after L4 holds. Larger P₀, a second interpreter author for K (independence of the substrate), POET-style generator co-evolution — and only if Hestia's precondition holds, i.e. a seed passes R2.

### M2 go/no-go

| Decision | Condition |
|---|---|
| L4 class met | Write the external replication package (06 1e of the Phase-3 challenges: an outside reviewer's target) |
| Not met | The claim stays bounded to G_dev/H₁ |

## The initial executable experiment (the first thing to run after the build)

**RLL-M0-E1 "Can the meta channel find anything?"**

| Item | Setting |
|---|---|
| Arms | T, XM, HP, CM, F0, SH |
| Seeds | 3 |
| Generations | 10 |
| Readouts | (1) withheld-mechanism rediscovery count, T vs XM; (2) H₁ at g = 10 |
| Cost | ≈ 200–500 core-h |
| Decisive outcomes | 0/6 rediscovered and no acceptance → S-META, stop the route. Rediscovery in T ≫ XM → the reflexive search already beats a fixed searcher at L2. Rediscovery equal → the meta channel works, but the reflexive part is untested until M1 |

E1 is chosen because it is the experiment most likely to falsify the architecture quickly and cheaply (08, attack 10).
