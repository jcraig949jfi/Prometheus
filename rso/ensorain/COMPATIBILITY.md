# Ensorain compatibility check and native phenomenon selection (C-016-T020)

Author: Cadmus[harry1-abbe9ede], claude-sonnet-5-5 (Q2), headless on harry1. Written 2026-10-11. Read-only against
`ensorain/` and `roles/Ensorain/`. Nothing here was run on ubu006 and no WTP-05 registered seed was used.

## 1. Decision

**Carrier: WTP-05 family C (law switch), world `C-R2-desert`, organism = TAPE genome with lifetime plasticity.
Lineage (A). Lineage (B) (E1 / D1) is not carried forward.** Two conditions come with the decision.

1. **The question must be re-worded.** The directive's candidate question is "retain and use information across a
   drift boundary". Family C does not reward retention across its boundary. It rewards REVISION: the information
   gathered before the switch (the sign of the law) becomes wrong at the switch and must be overwritten. The one thing
   that should be retained across the boundary, the never-switching type-2 law, is solved by every memoryless null
   (role-5 accuracy 1.00 for N1-N4, section 4). So the honest question for family C is: *"can a bounded persistent
   learner revise a lifetime-learned parameter at an unannounced law switch, while keeping the unrelated competence,
   and does the revision depend on its own reward history?"* Retention proper is not demanded here. If the
   Observatory wants retention across a drift boundary, no Ensorain world tested so far demands it (section 3).
2. **The demand margin is small.** On the demand-bearing role, a lawful plastic reference beats the best simple
   competitor by about 0.1 in accuracy, and the committed "GOLDILOCKS, H_null 0.54" admission label is inflated by
   the free half of the episodes (section 4). The first experiment must be sized for a 0.1 effect, not read off the
   admission label.

A combination of (A) and (B) is not proposed. Running E1's fitted-TT memory inside WTP-05's TAPE worlds would
change the physics on both sides (E1's address-event worlds and TAPE's obs/action episodes share no interface).

## 2. Pin and entry points

- Code pin: `origin/main` = `974a2edbe5f7b6b1f1940b0d6bad2c9b39bb1aed` at 2026-10-11 (worktree base
  `f7a2497c843206d0a374572187e460a175b584fc`). `ensorain/` and `roles/Ensorain/` were last changed at
  `7b1d549c8cc40cafa1b334acaa6d0aeba8ad88bb` in both. WTP-05 DEEP is still running on ubu006; its outputs and any
  later Ensorain commit move the tree. Re-pin and diff `ensorain/wtp5/` before any experiment.
- Prereg: `ensorain/PREREG_WTP05.md` (engine committed at efef48bcb per `roles/Ensorain/journal/2026-10-10.md`).

| What | Entry point |
|---|---|
| World family C | `ensorain/wtp5/worlds.py:239` `FamilyC`; `new_life` draws switch block `sw` in [4, 8] at `:245-246`; `law(b)` at `:248-252`; `block()` at `:254` |
| World factory | `ensorain/wtp5/worlds.py:275` `make("C-R2-desert")` (C has no rung ladder; `R2` is nominal) |
| Lawful reference (planted) | `ensorain/wtp5/planted.py:113` `switch_C(eta=1.0, sigma=0.5)`; dispatch `:120` `planted(world)` |
| Lifetime loop (plasticity, `history_shuffle`, `ws_reset`) | `ensorain/wtp5/tape.py:298` `lifetime(g, world, rng, plasticity, L, K, history_shuffle, ws_reset)` |
| Block interpreter | `ensorain/wtp5/tape.py:166` `run_block`; working state zeroed per block at `:171` |
| Plastic parameter set and bound | `ensorain/wtp5/tape.py:83` `plastic_keys`, `:49` `PLASTIC_BOUND = 1.0` |
| Family C certifier (SWITCH_TRACKED) | `ensorain/wtp5/certify.py:61` `certify`, family-C branch `:66-77` |
| Null ladder | `ensorain/wtp5/nulls.py:120` `ladder(world, seed)` |
| Admission | `ensorain/wtp5/admit.py:22` `admit(spec, seed)`; committed rows `ensorain/runs/wtp05/admission.json` |
| Existing control battery | `ensorain/wtp5/ablate.py:62` `controls(g, spec, plasticity, seed, n_lives)` |

## 3. Why not lineage (B), and what a "no world passes" reading looks like

- E1: `ensorain/E1_VERDICT.md` s1: INDETERMINATE (controls); positive control TT_LATENT@192 failed (median L2
  success 0.284 vs gate 0.5). In WORLD R no arm's L2 success exceeds NOMEM's (largest difference +0.0001). G failed
  against LOWRANK. E1.5 (`ensorain/E1P5_VERDICT.md`) later showed the TT advantage on a TT-generated world: that is
  the evaluator supplying the correct model class, which the directive warns about.
- D1: `ensorain/d1/core.py:17` `PHASE2 = 600`, `:44` `WorldD` drifts the generative parameters at event 600. The D-series
  (`ensorain/DIALS_SYNTHESIS.md`) found one replicated organism-intrinsic coupling (scratch x start) on a
  correctly-ordered memory. I did not find a committed demand gate in D1 that a simpler alternative fails; I did not
  re-run D1. The coordinator brief says no world passed one, and the committed text I read does not contradict it.
- What B has that C lacks: the native memory-cap audit (`ensorain/e0/memories.py:30` `audit(mem, cap)`) and the
  Smuggler arm (`ensorain/e0/memories.py:325`, `ensorain/e1/mem.py:320`). These are reusable as design patterns for
  a forbidden-channel control, not as code (they audit E0/E1 memory objects).
- If WTP-05 DEEP or a later Ensorain world passes a demand gate on retention, this decision should be reopened.

## 4. World-demand evidence for family C

Terms: role 1 = the switching law (the demand-bearing gates), role 5 = the never-switching law (unrelated competence),
per `ensorain/wtp5/worlds.py` header. The committed admission (seed 6_100_000, a registered seed, committed rows only,
not re-run) is `ensorain/runs/wtp05/admission.json`:

| spec | N0 const | N1-N3 | N4 menu | N1 role 1 | N1 role 5 | planted role 1 | planted role 5 |
|---|---|---|---|---|---|---|---|
| C-R2-desert | .479 | .737 | .770 | .468 | 1.00 | .601 | 1.00 |
| C-R2-stepping | .477 | .786 | .734 | .567 | 1.00 | .569 | 1.00 |
| C-R2-yoked | .477 | .786 | .770 | .519 | 1.00 | .577 | 1.00 |

`admit.py:31-33` computes H_null from the scored accuracy over all gates, so the free role-5 half sets the null floor at
about .75. H_null .54 is therefore a statement about the mixture. On role 1 alone, planted vs best null is .601 vs .534
in desert, and no separation in stepping. These rows are lifetime averages and include the blocks before the switch.

**Re-run with NEW seeds (this packet).** `rso/ensorain/rerun_c_demand.py`, result `rso/ensorain/rerun_c_demand_result.json`
(sha256 prefix 82fbab3778f8b138). Command from the repo root, one process, about 4 s:

    python -m rso.ensorain.rerun_c_demand rso/ensorain/rerun_c_demand_result.json

Seeds 16_020_001..16_020_040 (lives) and 16_030_001 (ladder); none is on the WTP-05 registered list. 40 lifetimes per
arm, K = 64, `C-R2-desert`, planted genome. The two runs I made were byte-identical (`cmp`).

| arm | role 1 before switch | role 1, 3 blocks after switch | role 1, switch+3 to end | role 5 | SWITCH_TRACKED (cert. rule) |
|---|---|---|---|---|---|
| plastic (lawful reference) | .922 | .076 | .639 | 1.00 | 14/40 = .35 |
| frozen (plasticity off; the simpler competitor) | 1.000 | .000 | .000 | 1.00 | 0/40 |
| history-shuffled plasticity | .606 | .437 | .412 | 1.00 | 11/40 = .275 |
| null ladder N1-N4 (new ladder seed) | role 1 .542 | | | 1.00 | |

Reading, kept apart as the directive requires:

- **Capacity.** PASS in the mean: the planted plastic solver reaches .639 on role 1 in the tracking window and recovers
  from .076 just after the switch. It is a lawful reference, not a high-accuracy one: only 35% of lifetimes meet the
  certifier's .75 rule on a new seed.
- **World demand.** PASS, with a small margin. The frozen competitor scores exactly 0 after the switch (it keeps the
  wrong sign), and the best memoryless/short-window/menu null scores .542 on role 1, versus .639 for the plastic
  reference. Static nulls here are trained in hindsight on blocks mixing both laws, so .54 is their best case.
- **Retention.** NOT demanded. Role 5 is 1.00 for every arm and every null. Nothing the world asks for after the switch
  needs a carried observation, only a revised scalar.
- **Causal dependence.** PARTLY visible: shuffling reward history inside a block drops late role 1 from .639 to .412
  and also damages the pre-switch accuracy (.922 to .606): noise-driven plasticity corrupts a correct initial
  parameter. But the shuffle arm still meets the SWITCH_TRACKED rule in 27.5% of lifetimes against 35%, because the
  rule thresholds a window mean and a clipped random walk lands on the negative side often enough. **The
  SWITCH_TRACKED fraction does not separate the reference from the shuffle control at n = 40; accuracy in the window
  does.** The Observatory endpoint must not be the certifier's tracked fraction.
- **Search accessibility.** Not tested here. Committed SCREEN rows (`roles/Ensorain/journal/2026-10-10.md`): searched
  plasticity arm L tracked the switch 4/8 in desert vs base 0/8; 8/8 both in stepping; 7/8 both in yoked. DEEP result
  pending (ubu006, ETA 13:00Z).
- **Qualification.** Open. Nothing here shows the evidence path detects a smuggled or forbidden alternative in
  family C (section 5).

## 5. Directive-s4 distinctions mapped to concrete controls

| Directive control | Concrete control in family C | Native machinery | Note |
|---|---|---|---|
| known-answer lawful reference | planted `switch_C` with plasticity | `planted.py:113`, `tape.py:298` | tracked 14/40 by the certifier rule; judge by window accuracy |
| memoryless / short-window competitor | N1 reactive, N2 short history (k 2-4), N3 bounded register | `nulls.py:120` | role 1 ~ .54, role 5 1.00 |
| stateful reference | the plastic genome IS the stateful reference (state lives in plastic CONST `theta`, 1 effective float of 8); N6 batch is not computed for C (`nulls.py:147` skips family C) | `planted.py:113` | no unbounded-memory reference exists for C |
| shuffled-history control | `history_shuffle=True` | `tape.py:344`, `ablate.py:70` | exists and works (above) |
| restart / reset control | see section 6 | | `ws_reset` is VACUOUS for family C |
| forbidden-memory / Smuggler | none native to TAPE. A candidate: a genome whose non-plastic CONST is set to the post-switch sign (reads the law from the genome, no learning); expected to fail before the switch and pass after | built from `tape.py` `genome`/`node` | an external construction, to be added in the adapter packet; `audit` (`e0/memories.py:30`) does not apply |

`ws_reset` is vacuous because `switch_C` has `S=1` and never uses `READ`/`WRITE` (`planted.py:113-118`) and the working
state is zeroed per block anyway (`tape.py:171`). `ablate.py:RG_state` for family C therefore measures nothing. The
state control for C is `plast_frozen` and `shuffled_hist` (`ablate.py:69-71`), not `ws_reset`.

Declared memory restriction. TAPE has structural bounds, not a cap audit: working state <= 8 x 8 floats and zeroed per
block (`tape.py` header), plastic parameters clipped to [-1, 1] (`tape.py:49`), 32 main-graph nodes. The only state
that crosses a block boundary is `out["learned"]` (the deep-copied genome, `tape.py:304,351`). An adapter can check
the declaration externally by counting the floats in `plastic_keys(g)` and asserting that the genome after the
lifetime differs from the input only at those keys. That check is new work and is not in Ensorain.

## 6. Reset and restart semantics (Ensorain's, not Ares's NULL)

- Episode: the working state `z` is zero at every block start (`tape.py:171`), and `ws_reset=True` zeroes it at every
  step (`tape.py:271`). Observations never depend on actions in these worlds.
- Block: parameters never change within a block; with plasticity on, every plastic parameter is used as
  `theta + sigma*eps_k` per episode (antithetic pairs) and updated once per block, between blocks (`tape.py` header).
- Life: `lifetime()` deep-copies the genome (`tape.py:304`), so every life restarts from the genome's initial
  `theta`; `FamilyC.new_life` draws a fresh switch block. A "restart" in Ensorain therefore means a new life from the
  genome, not an interrupt of a running life.
- Interrupt/resume of a running life is NOT offered. `lifetime()` has no start-block argument, and the law depends on
  the block index (`worlds.py:248`) while the perturbations depend on the `rng` stream. A resumed life needs: the
  learned genome, the block index, and the `rng` bit-generator state. An adapter has to re-implement the loop
  outside `ensorain/` to support this. Until then a mid-life restart control can only be built as "a new life
  starting at the learned parameters" (`out["learned"]`), which is a different experiment and must be named so.
- Consequence for the Ares comparison: Ares's interrupt carried recurrent activation and plastic weights across a
  checkpoint. Here activation never crosses a block, plastic parameters cross every block, and the boundary is a
  world event rather than an interrupt.

## 7. Environment check on harry1

- Ensorain pins (`ensorain/requirements.txt`): Python 3.14.4, numpy 2.3.5, scipy 1.16.3, psutil 7.1.0, pytest 9.0.2,
  psycopg2-binary 2.9.13. harry1 has Python 3.12.10, numpy 2.4.3, scipy 1.17.1, psutil 7.2.2, no pytest.
- `import ensorain.wtp5.admit, ensorain.wtp5.nulls` succeeds and the whole re-run executes on harry1 (about 4 s). I
  installed nothing and used no private venv.
- The file header says results are bitwise platform-bound ("a new host or version set needs a fresh dev baseline, not
  a comparison to M2 rows"). For us this means: (a) harry1 numbers are internally reproducible (two identical runs)
  but cannot be compared to ubu006 committed numbers digit for digit, so my new-seed numbers above are not checked
  against a ubu006 run; (b) any Observatory comparison must run all arms on one host/version set (a within-host
  paired design), never compare a harry1 arm to a committed ubu006 row; (c) the pinned versions are not reproduced
  here, so a reviewer who needs the exact pinned stack needs a venv with Python 3.14.4, numpy 2.3.5, scipy 1.16.3 under
  `C:/Prometheus-worktrees/`.
- Not done: `ensorain/wtp5/tests` (needs pytest, not installed); the committed admission was not reproduced because
  it uses a registered seed.

## 8. Registry fit (`python -m rso.registry.registry for-adapter`)

| Entry | Applies? | Where its scope stops |
|---|---|---|
| exec-binding | yes | flat inventories only (P-FLAT). One lifetime = one node, no nesting. |
| custody-keeper | yes | bytes, not truth. Registers the pinned genome and the output rows. |
| mutation-runner | yes, for the adapter/evaluator code | CHALLENGED; cannot tell a behavioural kill from a freeze-hash kill |
| receipt-canonical | yes, with encoding work | refuses floats. Family C endpoints are floats; encode as integer counts (correct, n) per window. |
| budget-ledger | yes | declared estimates, not billing. Cost is minutes of CPU; trivial. |
| witness-driver-ares | pattern only | imports Ares; its scope excludes multi-boundary and cross-episode drift designs, which family C is |
| ruler-binary-retention | partly | the per-episode endpoint is binary with chance 1/2, so the form fits; but "dependent episodes" are NOT qualified, and episodes within a life share the plastic parameter. The unit must be the lifetime (e.g. one binary or count per life), not the episode. It also names "retention"; family C does not test retention. |
| stratified-holm-analysis | partly | binary counts per stratum fit if the unit is the lifetime; CHALLENGED; `analyze.py` trusts the runner's `discovery` field. A continuous late-window accuracy endpoint is outside its scope. |

Scope limits hit by this check, to add to the registry when the adapter lands: the Ares ruler assumes independent
episodes; a plastic learner makes them dependent. The SWITCH_TRACKED rule is a poor discriminator at n = 40 (section 4).

## 9. Recommended next step (for T-adapter, not done here)

1. Endpoint: late-window role-1 accuracy per lifetime, or the count of correct role-1 gates in blocks >= sw+3 as an integer
   with its n, compared plastic vs frozen vs history-shuffled, paired by lifetime seed. Do not use the tracked fraction.
2. Size for a ~.1 effect with lifetime-level variance (plastic role-1 late window: see the result JSON).
3. Add the Smuggler analogue and an external declared-memory check (section 5).
4. Decide, before observing, whether the reworded question (section 1) is acceptable to the operator, or whether to seek
   a retention-demanding Ensorain world instead.

## 10. Limits of this packet

- One re-run: planted genome only, 40 lifetimes per arm, one ladder seed. Not powered for a claim about the searched
  arms. The SCREEN numbers (4/8 vs 0/8) are Ensorain's, quoted from its journal, not re-derived.
- Lineage (B) was assessed from committed verdict text and source, not re-run.
- Ensorain's WTP-05 DEEP outcome is unknown at this writing and could change the choice.
